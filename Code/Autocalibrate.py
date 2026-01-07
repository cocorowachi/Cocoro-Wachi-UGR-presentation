import numpy as np
import streamlit as st
import pandas as pd
from numba import njit
from model import amm_3, poly_model
from scipy.stats import pearsonr, linregress
from scipy.optimize import differential_evolution, minimize

class Autocalibrate:
    def __init__(self, start: np.datetime64, end: np.datetime64, area: float, target: pd.Series, temperature: pd.Series, precip: pd.Series):

        self.datetime = np.arange(start, end, np.timedelta64(1, 'h'))

        self.target_flow = target[target.index.minute == 0].reindex(self.datetime, fill_value=0).to_numpy()
        self.temperature_signal = temperature[temperature.index.minute == 0].reindex(self.datetime, fill_value=0).to_numpy()
        self.precip_signal = precip[precip.index.minute == 0].reindex(self.datetime, fill_value=0).to_numpy()

        self.area = area

        self.simulated_flow = None

        self._isolate()

    def _isolate(self):
        self.diurnal = self._get_diurnal()
        l15 = self._lyne_hollick(self.target_flow - self.diurnal, 15)
        l3 = self._lyne_hollick(self.target_flow - self.diurnal, 3)

        self.obs_seasonal = l15
        self.obs_slow_flow = l3 - self.obs_seasonal
        self.obs_fast_flow = self.target_flow - self.diurnal - self.obs_slow_flow - self.obs_seasonal
    
    def _get_diurnal(self):
        flow = pd.Series(self.target_flow, index=self.datetime)
        # make a list of daily volume
        daily_vol = flow.resample("D").sum()
        low = daily_vol.quantile(0.10)
        high = daily_vol.quantile(0.60)
        # select index where it's between the percentile, then the flow movement
        selected_days = daily_vol[(daily_vol >= low) & (daily_vol <= high)].index
        selected_flows = flow[flow.index.normalize().isin(selected_days)]
        selected_flows = selected_flows - min(selected_flows)
        #calculate the daily avg
        is_weekend = selected_flows.index.dayofweek >= 5
        weekday_profile = selected_flows[~is_weekend].groupby(selected_flows[~is_weekend].index.hour).mean()
        weekend_profile = selected_flows[is_weekend].groupby(selected_flows[is_weekend].index.hour).mean()
        #broadcasting to flow index
        hours = flow.index.hour
        dow = flow.index.dayofweek
        out_arr = np.where(dow >= 5, weekend_profile.reindex(hours).to_numpy(), weekday_profile.reindex(hours).to_numpy())
        mean_dwf = np.mean(out_arr)
        min_dwf = min(out_arr)
        steven_schutzbach = (0.4*min_dwf)/(1 - 0.6*((min_dwf/mean_dwf)**(mean_dwf**0.7)))
        return out_arr - steven_schutzbach
    
    def _lyne_hollick(self, flow, n):

        @njit
        def lyne_hollick_numba_1d(data, alpha):
            """
            Numba-optimized Lyne-Hollick filter for a single 1D NumPy array.
            """
            n = data.shape[0]
            out = np.empty_like(data)
            oneplusalphahalf = (1 + alpha) / 2

            out[0] = data[0]
            prev_out = data[0]
            prev_data = data[0]

            for i in range(1, n):
                cur_data = data[i]

                if np.isnan(cur_data):
                    out[i] = prev_out
                    continue

                term1 = alpha * (prev_data - prev_out)
                term2 = oneplusalphahalf * (cur_data - prev_data)
                cur_out = cur_data - max(term1 + term2, 0)

                if np.isnan(cur_out) or cur_out <= 0:
                    cur_out = prev_out

                out[i] = cur_out
                prev_out = cur_out
                prev_data = cur_data

            return out


        def lyne_hollick_array(arr: np.ndarray, passes: int = 5, alpha: float = 0.925) -> np.ndarray:
            """
            Apply Lyne-Hollick filter to a 1D NumPy array.
            """
            if arr.ndim != 1:
                raise ValueError("Input array must be 1D")

            def _recursive(data, passes):
                if passes < 1:
                    return data

                reverse_pass = (passes % 2 == 0)
                data_proc = data[::-1] if reverse_pass else data

                filtered = lyne_hollick_numba_1d(data_proc, alpha)
                if reverse_pass:
                    filtered = filtered[::-1]

                return _recursive(filtered, passes - 1) if passes > 1 else filtered

            return _recursive(arr.astype(np.float64), passes)


        def insert_mirrored_rows_array(arr: np.ndarray, num_rows: int = 30) -> np.ndarray:
            """
            Mirror head and tail of a 1D array to reduce edge effects.
            """
            if arr.ndim != 1:
                raise ValueError("Input array must be 1D")
            head = arr[:num_rows][::-1]
            tail = arr[-num_rows:][::-1]
            return np.concatenate([head, arr, tail])


        def lyne_hollick_init_array(arr: np.ndarray, passes: int = 3, alpha: float = 0.925, num_rows: int = 60) -> np.ndarray:
            """
            Apply Lyne-Hollick filter with mirrored padding for edge-effect reduction.
            """
            padded = insert_mirrored_rows_array(arr, num_rows=num_rows)
            filtered = lyne_hollick_array(padded, passes=passes, alpha=alpha)
            return filtered[num_rows:-num_rows]

        return lyne_hollick_init_array(flow, passes = n)

    def _lin_score(self, target, sim_flow):
        r, p = pearsonr(target, sim_flow) # 4

        stdev_sim = sim_flow.std()
        stdev_obs = target.std()

        C_b = (2*stdev_obs*stdev_sim)/((stdev_obs**2)+(stdev_sim**2)+(stdev_obs-stdev_sim)**2) # 5
        return -r*C_b
        
    def _fast_obj_amm(self, params):
        target = self.obs_fast_flow
        temp = self.temperature_signal
        precip = self.precip_signal

        area = self.area
        p1, p2, p3, p4, p5 = params

        sim_flow = amm_3(temp, precip, area, p1, p2, p3, p4, p5)

        mask = ~np.isnan(target) & ~np.isnan(sim_flow)
        target = target[mask]
        sim_flow = sim_flow[mask]
        
        if len(target) < 2 or len(sim_flow) < 2:
            return 1e9   # or any large positive penalty

        # If shapes mismatch, truncate or return penalty
        if len(target) != len(sim_flow):
            return 1e9
        
        # fast flow cali only looks at tops of peak
        median = np.percentile(target, 60)
        mask = (target>median) & (sim_flow>median)
        target = target[mask]
        sim_flow = sim_flow[mask]

        out = self._lin_score(target, sim_flow)
        return out

    def _slow_obj_amm(self, params):
        target = self.obs_slow_flow
        temp = self.temperature_signal
        precip = self.precip_signal

        area = self.area
        p1, p2, p3, p4, p5 = params

        sim_flow = amm_3(temp, precip, area, p1, p2, p3, p4, p5)

        mask = ~np.isnan(target) & ~np.isnan(sim_flow)
        target = target[mask]
        sim_flow = sim_flow[mask]
        
        if len(target) < 2 or len(sim_flow) < 2:
            return 1e9   # or any large positive penalty

        # If shapes mismatch, truncate or return penalty
        if len(target) != len(sim_flow):
            return 1e9

        # slow flow cali looks at all data
        # median = np.percentile(target, 0)
        # mask = (target>median) & (sim_flow>median)
        # target = target[mask]
        # sim_flow = sim_flow[mask]

        out = self._lin_score(target, sim_flow)
        return out

    def _seasonal_obj(self, params):
        target = self.obs_seasonal
        temp = self.temperature_signal
        indicator = self._lyne_hollick(temp, 25)

        p1, p2 = params

        sim_flow = poly_model(indicator, p1, p2)

        mask = ~np.isnan(target) & ~np.isnan(sim_flow)
        target = target[mask]
        sim_flow = sim_flow[mask]
        
        if len(target) < 2 or len(sim_flow) < 2:
            return 1e9   # or any large positive penalty

        # If shapes mismatch, truncate or return penalty
        if len(target) != len(sim_flow):
            return 1e9
        
        # seasonal flow cali looks at all data
        # median = np.percentile(target, 50)
        # mask = (target>median) & (sim_flow>median)
        # target = target[mask]
        # sim_flow = sim_flow[mask]

        out = self._lin_score(target, sim_flow)
        return out
    
    def optimize(self):
        
        ### Fast Cali
        indicator = self.temperature_signal
        precip = self.precip_signal
                # RD,      HHL,      AMHL,     hot_shcf,delta_shcf
        bounds = [(0, 50), (1e-6, 100), (1e-6, 100), (0, 10), (0, 10)]
            
        global_res = differential_evolution(self._fast_obj_amm, 
                                            bounds=bounds, 
                                            maxiter=50,
                                            polish=False,
                                            popsize=3,
                                            recombination=0.8,
                                            mutation=(0.25, 0.5),
                                            strategy='best1bin'
                                            )
        result = minimize(self._fast_obj_amm, 
                        bounds=bounds, 
                        x0=global_res.x,
                        method='Nelder-Mead',
                        options={#'ftol':1.0e-05, #scipy default is 2.2e-09
                                'maxiter':100},
                        )
        p1, p2, p3, p4, p5 = result.x
        self.sim_fast_flow = amm_3(indicator, precip, self.area, p1, p2, p3, p4, p5)
        self.fast_param = result.x
        st.write("fast done")

        ### Slow Cali
        indicator = self.temperature_signal
        precip = self.precip_signal
                # RD,      HHL,      AMHL,     hot_shcf,delta_shcf
        bounds = [(0, 50), (1e-6, 100), (1e-6, 100), (0, 10), (0, 10)]
            
        global_res = differential_evolution(self._slow_obj_amm, 
                                            bounds=bounds, 
                                            maxiter=50,
                                            polish=False,
                                            popsize=3,
                                            recombination=0.8,
                                            mutation=(0.25, 0.5),
                                            strategy='best1bin'
                                            )
        result = minimize(self._slow_obj_amm, 
                        bounds=bounds, 
                        x0=global_res.x,
                        method='Nelder-Mead',
                        options={#'ftol':1.0e-05, #scipy default is 2.2e-09
                                'maxiter':100},
                        )
        p1, p2, p3, p4, p5 = result.x
        self.sim_slow_flow = amm_3(indicator, precip, self.area, p1, p2, p3, p4, p5)
        self.slow_param = result.x
        st.write("slow done")
        ### Seasonal Cali
        # temp = self.temperature_signal
        # indicator = self._lyne_hollick(temp, 25)
        # precip = self.precip_signal
        #         # exp,    scalar
        # bounds = [(0, 3), (0, 500)]
            
        # global_res = differential_evolution(self._seasonal_obj, 
        #                                     bounds=bounds, 
        #                                     maxiter=50,
        #                                     polish=False,
        #                                     popsize=3,
        #                                     recombination=0.8,
        #                                     mutation=(0.25, 0.5),
        #                                     strategy='best1bin'
        #                                     )
        # result = minimize(self._seasonal_obj, 
        #                 bounds=bounds, 
        #                 x0=global_res.x,
        #                 method='Nelder-Mead',
        #                 options={#'ftol':1.0e-05, #scipy default is 2.2e-09
        #                         'maxiter':100},
        #                 )
        # p1, p2 = result.x
        # self.sim_seasonal = poly_model(indicator, p1, p2)

        # obs_med = np.percentile(self.obs_seasonal, 50)
        # sim_med = np.percentile(self.sim_seasonal, 50)

        # self.sim_seasonal = self.sim_seasonal + (obs_med - sim_med)
        # self.seasonal_param = (p1, p2, (obs_med - sim_med))
        
    def get_sim_flow(self):
        return self.datetime, self.diurnal, self.sim_fast_flow, self.sim_slow_flow
        # return self.datetime, self.diurnal, self.sim_fast_flow, self.sim_slow_flow, self.sim_seasonal