import streamlit as st
import numpy as np
import pandas as pd
from Data import Data
from Autocalibrate import Autocalibrate
import plotly.graph_objects as go

st.set_page_config(
    page_title="MSOE Wachi Sewer Dashboard",
    page_icon="graphics/msoe_icon.png",
    layout="wide"
)

if "_init_" not in st.session_state:
    st.session_state._init_ = False
    st.session_state.page = "dashboard"
# Header
title_cols = st.columns([1,10])
with title_cols[0]:
    st.image("graphics/msoe_logo.png", width=100)
with title_cols[1]:
    st.header("Breaking Apart Wet Weather Flow Signals Allows Streamlined Auto-calibration of Sewer Hydrology Models")
    st.write("Dr. William Gonwa P.E., Cocoro Wachi Undergraduate")
methods_c, poster_c, authors_c = st.columns([2,2,2])
with methods_c:
    if st.button("Methods & Case Study", type="primary" if st.session_state.page == "dashboard" else "secondary", disabled=not st.session_state._init_, width="stretch"):
        st.session_state.page = "dashboard"
        st.rerun()
# with topbutton_cols[1]:
#     if st.button("Case Study & Result", type="primary" if st.session_state.page == "casestudy" else "secondary", disabled=not st.session_state._init_, width="stretch"):
#         st.session_state.page = "casestudy"
#         st.rerun()
with poster_c:
    if st.button("Poster", type="primary" if st.session_state.page == "poster" else "secondary", disabled=not st.session_state._init_, width="stretch"):
        st.session_state.page = "poster"
        st.rerun()
with authors_c:
    if st.button("Authors/About the Project", type="primary" if st.session_state.page == "authors" else "secondary", disabled=not st.session_state._init_, width="stretch"):
        st.session_state.page = "authors"
        st.rerun()
st.write("---")
if not st.session_state._init_:
    with st.spinner("Initializing Model"):
        path = "Data/"
        temp = "Temperature.csv"
        sewer = "MMSD Sewer Flow Data.csv"
        precip = "MMSD Precipitation Raw Data.csv"

        temperature_df = Data(path + temp)
        sewer_df = Data(path + sewer)
        precip_df = Data(path + precip)
        st.session_state.weights_df = pd.read_csv("Data/parameter.csv")
        st.session_state.acali = Autocalibrate(np.datetime64("2015-06-01T00:00"), np.datetime64("2020-01-31T23:00"), 64, sewer_df.read('MS0208 FlowMGD'), temperature_df.read("Temperature (F)"), precip_df.read("WS1201 Precip HourlyInches"), True)
        st.session_state.acali.optimize(st.session_state.weights_df)
        st.session_state._init_ = True
    st.rerun()

events = [(np.datetime64("2016-10-15T14:00"),np.datetime64("2016-10-18T14:00")),
          (np.datetime64("2016-10-25T14:00"),np.datetime64("2016-10-29T22:00")),
          (np.datetime64("2016-11-01T22:00"),np.datetime64("2016-11-04T07:00")),
          (np.datetime64("2016-11-27T12:00"),np.datetime64("2016-11-30T16:00")),
          (np.datetime64("2017-01-19T10:00"),np.datetime64("2017-01-19T22:00")),
          (np.datetime64("2017-02-23T09:00"),np.datetime64("2017-02-27T19:00")),
          (np.datetime64("2017-04-15T10:00"),np.datetime64("2017-04-19T08:00")),
          (np.datetime64("2017-04-29T17:00"),np.datetime64("2017-05-05T01:00")),
          (np.datetime64("2017-06-03T02:00"),np.datetime64("2017-06-06T14:00")),
          (np.datetime64("2017-06-16T19:00"),np.datetime64("2017-06-19T01:00")),
          (np.datetime64("2017-06-22T13:00"),np.datetime64("2017-06-27T13:00")),
          (np.datetime64("2017-06-28T04:00"),np.datetime64("2017-07-02T17:00")),
          (np.datetime64("2017-07-09T23:00"),np.datetime64("2017-07-16T08:00")),
          (np.datetime64("2017-10-10T04:00"),np.datetime64("2017-10-13T12:00")),
          (np.datetime64("2017-10-13T17:00"),np.datetime64("2017-10-17T10:00")),
          (np.datetime64("2018-01-21T20:00"),np.datetime64("2018-01-26T15:00")),
          (np.datetime64("2018-02-19T04:00"),np.datetime64("2018-02-24T07:00")),
          (np.datetime64("2018-04-13T04:00"),np.datetime64("2018-04-18T06:00")),
          (np.datetime64("2018-05-02T08:00"),np.datetime64("2018-05-06T18:00")),
          (np.datetime64("2018-05-08T15:00"),np.datetime64("2018-05-10T20:00")),
          (np.datetime64("2018-05-10T21:00"),np.datetime64("2018-05-19T02:00")),
          (np.datetime64("2018-05-20T06:00"),np.datetime64("2018-05-25T02:00")),
          (np.datetime64("2017-01-19T10:00"),np.datetime64("2017-01-19T22:00"))]
acali=st.session_state.acali
datetime, diurnal, sim_fast, sim_slow, sim_seasonal = acali.get_sim_flow()
s, e = 11200, 26700
# datetime = datetime[s:e]

plot_config = {
    'displayModeBar': True,
    'scrollZoom': True
}
if st.session_state.page == "dashboard":
    with st.container(border=True):
        st.header("Problem")
        problem_sec_cols = st.columns([1,38,1])
        with problem_sec_cols[1]:
            st.write("Modeling the impacts of precipitation on sanitary sewer flow is challenging due to limited-duration flow metering records, complex interactions among static and time-varying factors, and short-term, long-term, and seasonal hydrologic processes. The traditional calibration approach adjusts and optimizes parameters for all processes simultaneously to attempt to match the measured flow rate.")
            st.write("In this study, we present an alternative calibration approach that first disaggregates the measured sewer flow signal into four sub-signals, each of which represents a different hydrologic process. Then each hydrologic process is independently modeled and calibrated  to its own distinct sub-signal. This approach significantly reduces the parameter solution domain, resulting in faster, and more reliable and confident calibration.")
    
    # with st.container(border=True):
        st.header("Data Assumptions & Methods")
        data_sec_cols = st.columns([1,38,1])
        with data_sec_cols[1]:
            st.write("This study uses measured sanitary sewer flow and precipitation data provided by Milwaukee Metropolitan Sewerage District. Flow and rainfall data were available at hourly resolution, which is sufficient to capture both short-duration inflow responses and longer-term groundwater-driven infiltration effects.")
            st.write("The modeling framework relies on:")
            st.write(" - Sewer flow monitoring data at individual meters,")
            st.write(" - Rainfall time series from nearby precipitation gauges, and")
            st.write(" - Air temperature time series used as a proxy for seasonal groundwater conditions.")
            st.write("Furthurmore, the following assumptions were made:")
            st.write(" - The diurnal sanitary flow pattern is stationary over the calibration and validation periods,")
            st.write(" - Rainfall–runoff relationships are time-invariant within the study period, ")
            st.write(" - No major structural changes occurred in the sewer system during the analysis window, and")
            st.write(" - Monitoring data are of sufficient quality to support signal separation and calibration.")
            st.write("---")
            st.write("Traditional sanitary sewer flow models simulate multiple hydrologic processes simultaneously and calibrate all parameters at once to match observed flow. This creates large parameter spaces and introduces uncertainty due to correlated parameters. In this study, we adopt an alternative approach that first separates the measured flow signal into physically meaningful components, then calibrates each process independently.")
            
            st.write("Step 1: Separation of Sanitary and Wet-Weather Flow")
            st.write("The total measured flow was first separated into:")
            st.write(" - Diurnal sanitary flow, representing regular residential, commercial, and industrial discharge")
            st.write(" - Rainfall-derived infiltration and inflow (RDI/I), representing wet-weather response")
            st.write("The diurnal component was identified using dry-weather periods and removed to isolate wet-weather behavior.")
            
            st.write("Step 2: Disaggregation of Wet-Weather Flow")
            st.write("The wet-weather flow signal was further decomposed into three components:")
            st.write(" - Fast response (direct rainfall-driven inflow and rapid infiltration)")
            st.write(" - Slow response (delayed groundwater infiltration following rainfall)")
            st.write(" - Long-term seasonal variation (groundwater-driven base infiltration)")
            st.write("This disaggregation was performed using recursive baseflow separation filters applied at different time scales. Each resulting sub-signal represents a distinct hydrologic process with a characteristic response speed.")
            st.write("Below is an excel file recreating the baseflow separation filter.")
            with open("graphics/lyne_hollick.xlsx", "rb") as f:
                st.download_button(
                    label="📥Download Excel (xlsx)",
                    data=f.read(),
                    file_name="Lyne-Hollick Baseflow Isolation.xlsx",
                )

            st.write("Step 3: Independent Model Calibration ")
            st.write("Each sub-signal was modeled separately using a hydrologic transfer function framework. By calibrating each process independently, only a small subset of parameters influenced each modeled response. This preserves parameter interpretability and reduces interaction between unrelated processes.")


    # with st.container(border=True):
    #     st.write("some coding detail for reproducability for some audience")
    # with st.container(border=True):
    #     st.write("validation, results, metrics")
    #     st.write("talk about limitations of the mmodel/methodology")

# if st.session_state.page == "casestudy":
    with st.container(border=True):
        with st.container():
            st.header("Case Study: MS0208 Sewer Basin (Milwaukee, WI) Sept. 2016 - June 2018")
            ######################################
            # obs disagg 
            fig = go.Figure()
            # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,                                                       name="precip", mode="lines", yaxis='y2'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e],                line_color="blue", name="Seasonal+Slow+Fast Flow", mode="lines", yaxis='y1'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.obs_slow_flow+acali.obs_seasonal)[s:e],                                    line_color="red", name="Seasonal+Slow Flow", mode="lines", yaxis='y1'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_seasonal[s:e],                                                          line_color="green", name="Seasonal Flow", mode="lines", yaxis='y1'))
            # fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.diurnal+acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e],  name="diurnal", mode="lines", yaxis='y1'))
            fig.update_layout(
                title="Disaggregated Signal (Diurnal Excluded)",
                xaxis=dict(title="Date Time",
                        showgrid=True,
                        fixedrange=False),
                yaxis=dict(title='Flow [MGD]',
                            side='left',
                            showgrid=True,
                            fixedrange=True),
                template="plotly_dark",
                hovermode='x unified', 
                dragmode='pan'
            )
            fig.update_yaxes(range=[-0.5, 4])
            st.plotly_chart(fig, config={'scrollZoom': True}, width='stretch')
        with st.container():
                
            ########################################
            # model fast
            fig = go.Figure()
            # fig.add_trace(go.Scattergl(x=datetime[2:], y=acali.precip_signal[2:],   line_color="green", name="precip", mode="lines", yaxis='y2'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_fast_flow[s:e],   line_color="blue", name="Observed Fast Flow", mode="lines", yaxis='y1'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_fast[s:e],              line_color="red", name="Simulated Fast Flow", mode="lines", yaxis='y1'))
            fig.update_layout(
                title="Fast Response Observed and Simulated Signal",
                xaxis=dict(title="Date Time",
                        showgrid=True,
                        fixedrange=False),
                yaxis=dict(title='Flow [MGD]',
                            side='left',
                            fixedrange=True),
                template="plotly_dark",
                hovermode='x unified', 
                dragmode='pan'
            )
            fig.update_yaxes(range=[-0.5, 4])
            st.plotly_chart(fig, config={'scrollZoom': True}, width='stretch')

        with st.container():
            ###############################
            # Model slow
            fig = go.Figure()
            # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,   line_color="green", name="precip", mode="lines", yaxis='y2'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_slow_flow[s:e],   line_color="blue", name="Observed Slow Flow", mode="lines", yaxis='y1'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_slow[s:e],              line_color="red", name="Simulated Slow Flow", mode="lines", yaxis='y1'))
            fig.update_layout(
                title="Slow Response Observed and Simulated Signal",
                xaxis=dict(title="Date Time",
                        showgrid=True,
                        fixedrange=False),
                yaxis=dict(title='Flow [MGD]',
                            side='left',
                            fixedrange=True),
                template="plotly_dark",
                hovermode='x unified', 
                dragmode='pan'
            )
            fig.update_yaxes(range=[-0.5, 4])
            st.plotly_chart(fig, config={'scrollZoom': True}, width='stretch')

        with st.container():
            ##############################
            # model seasonal
            fig = go.Figure()
            # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,   line_color="green", name="precip", mode="lines", yaxis='y2'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_seasonal[s:e],    line_color="blue", name="Observed Seasonal Flow", mode="lines", yaxis='y1'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_seasonal[s:e],          line_color="red", name="Simulated Seasonal Flow", mode="lines", yaxis='y1'))
            fig.update_layout(
                title="Seasonal Response Observed and Simulated Signal",
                xaxis=dict(title="Date Time",
                        showgrid=True,
                        fixedrange=False),
                yaxis=dict(title='Flow [MGD]',
                            side='left',
                            fixedrange=True),
                template="plotly_dark",
                hovermode='x unified', 
                dragmode='pan'
            )
            fig.update_yaxes(range=[-0.5, 4])
            st.plotly_chart(fig, config={'scrollZoom': True}, width='stretch')

        with st.container():
            #############################
            # combine
            fig = go.Figure()
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e],    line_color="blue", name="Observed Flow", mode="lines", yaxis='y1'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.sim_rdii[s:e],                                                  line_color="green", name="Trad. Simulated Flow", mode="lines", yaxis='y1'))
            fig.add_trace(go.Scattergl(x=datetime[s:e], y=(sim_fast+sim_slow+sim_seasonal)[s:e],                                line_color="red", name="New Simulated Flow", mode="lines", yaxis='y1'))

            fig.update_layout(
                title="Observed and Re-aggregated Simulated Signal",
                xaxis_title="Date Time",
                xaxis_showgrid=True,
                yaxis=dict(title='Flow [MGD]',
                            side='left',
                            fixedrange=True),
                hovermode='x unified', 
                dragmode='pan'
            )

            fig.update_yaxes(range=[-0.5, 4])
            st.plotly_chart(fig, config={'scrollZoom': True}, width='stretch')

        ####################
        # Event OTO
        obs_rdii = (acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)
        sim_rdii = (sim_fast+sim_slow+sim_seasonal)
        simT_rdii = acali.sim_rdii

        obs_events = []
        sim_events = []
        simT_events = []

        for start, end in events:
            mask = (datetime >= start) & (datetime <= end)
            obs_events.append(obs_rdii[mask].sum())
            sim_events.append(sim_rdii[mask].sum())
            simT_events.append(simT_rdii[mask].sum())

        obs_events = np.array(obs_events)
        sim_events = np.array(sim_events)
        simT_events = np.array(simT_events)


        fig = go.Figure()
        fig.add_trace(go.Scattergl(x=obs_events, y=sim_events, line_color="blue", mode="markers", marker_size=8, showlegend=False, yaxis='y1'))
        fig.add_trace(go.Scattergl(x=obs_events, y=simT_events, line_color="red", mode="markers", marker_size=8, showlegend=False, yaxis='y1'))


        fig.add_trace(go.Scattergl(x=[0,max(obs_events)], y=[0, max(obs_events)], line_color="black", line_dash="dash", name="True 1:1", mode="lines", yaxis='y1'))
        m2, b2 = np.polyfit(obs_events, simT_events, 1)   # slope, intercept
        fig.add_trace(go.Scattergl(x=[0,max(obs_events)], y=[b2, m2*max(obs_events)+b2], line_color="red", name="Trad. Simulated Points", mode="lines", yaxis='y1'))
        # st.write("m2:",m2,", b2:",b2)
        m1, b1 = np.polyfit(obs_events, sim_events, 1)   # slope, intercept
        fig.add_trace(go.Scattergl(x=[0,max(obs_events)], y=[b1, m1*max(obs_events)+b1], line_color="blue", name="New Simulated Points", mode="lines", yaxis='y1'))
        # st.write("m1:",m1,", b1:",b1)


        fig.add_annotation(
            x=0.05,
            y=0.9,
            xref="paper",
            yref="paper",
            text="Trad. Approach LOBF: 1.5026x+2.628 <br>New Approach LOBF: 1.0099x+28.89",
            showarrow=False,
            align="left",
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            borderpad=6,
            font=dict(size=12)
        )

        fig.update_layout(
            width=400, height=500,
            title="Event Volume One-to-One",
            xaxis_title="Obs. Event Volume [MG]",
            xaxis_showgrid=True,
            yaxis=dict(title='Sim. Event Volume [MG]',
                        side='left'),
            template="plotly_dark",
            dragmode='pan'
        )
        st.plotly_chart(fig, config={'scrollZoom': True})


        ####################
        # peak flow oto
        obs_rdii = (acali.obs_rdii)
        sim_rdii = (sim_fast+sim_slow+sim_seasonal)
        simT_rdii = acali.sim_rdii

        obs_top20 = []
        sim_top20 = []
        simT_top20 = []

        for start, end in events:
            mask = (datetime >= start) & (datetime <= end)
            obs_top20.append(max(obs_rdii[mask]))
            sim_top20.append(max(sim_rdii[mask]))
            simT_top20.append(max(simT_rdii[mask]))

        obs_top20 = np.array(obs_top20)
        sim_top20 = np.array(sim_top20)
        simT_top20 = np.array(simT_top20)

        fig = go.Figure()
        # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal, line_color="green", name="precip", mode="lines", yaxis='y2'))
        fig.add_trace(go.Scattergl(x=obs_top20, y=sim_top20, line_color="blue", mode="markers", marker_size=8, showlegend=False, yaxis='y1'))
        fig.add_trace(go.Scattergl(x=obs_top20, y=simT_top20, line_color="red", mode="markers", marker_size=8, showlegend=False, yaxis='y1'))


        fig.add_trace(go.Scattergl(x=[0,max(obs_top20)], y=[0, max(obs_top20)], line_dash="dash",line_color="black", name="True 1:1", mode="lines", yaxis='y1'))
        m2, b2 = np.polyfit(obs_top20, simT_top20, 1)   # slope, intercept
        fig.add_trace(go.Scattergl(x=[0,max(obs_top20)], y=[b2, m2*max(obs_top20)+b2], line_color="red", name="Trad. Simulated Points", mode="lines", yaxis='y1'))
        # st.write("m2:",m2,", b2:",b2)
        m1, b1 = np.polyfit(obs_top20, sim_top20, 1)   # slope, intercept
        fig.add_trace(go.Scattergl(x=[0,max(obs_top20)], y=[b1, m1*max(obs_top20)+b1], line_color="blue", name="New Simulated Points", mode="lines", yaxis='y1'))
        # st.write("m1:",m1,", b1:",b1)

        fig.add_annotation(
            x=0.05,
            y=0.9,
            xref="paper",
            yref="paper",
            text="Trad. Approach LOBF: 0.6823x+0.3036 <br>New Approach LOBF: 0.9573x+0.8457",
            showarrow=False,
            align="left",
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            borderpad=6,
            font=dict(size=12)
        )

        fig.update_layout(
            width=400, height=500,
            title="Peak Flow One-to-One",
            xaxis_title="Obs. Peak Flow [MGD]",
            xaxis_showgrid=True,
            yaxis=dict(title='Sim. Peak Flow [MGD]',
                        side='left'),
            template="plotly_dark",
            dragmode='pan'
        )
        st.plotly_chart(fig, config={'scrollZoom': True}, width='stretch')


if st.session_state.page == "poster":
    poster_cols = st.columns([6,1])
    with poster_cols[0]:
        with st.container(border=True, width="stretch"):
            st.image("graphics/ICWMM_poster.png", width="stretch")
    with poster_cols[1]:
        with open("graphics/ICWMM_poster.pdf", "rb") as f:
            file_bytes = f.read()
        st.download_button("📥Download as PDF", data=file_bytes, file_name="Wachi_ICWMM2026_Poster.pdf")



if st.session_state.page == "authors":
    with st.container():
        gonwa_cols = st.columns([1,6])
        with gonwa_cols[0]:
            st.image("graphics/gonwa.jpg")
        with gonwa_cols[1]:
            st.header("Dr. William Gonwa P.E., Milwaukee School of Engineering.")
            st.write("Professor and Program Director for Civil Engineering. ")
            st.write("Civil and Architectural Engineering and Construction Management.")
            col, _ = st.columns([2,3])
            with col:
                with st.container(width="stretch"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("+1(414)277-7320")
                        st.write("gonwa@msoe.edu")
                    with col2:
                        st.write("Campus Center: CC-27")
                        st.markdown(
                            '<a href="https://www.msoe.edu/directory/profile/william.gonwa/" target="_blank">Faculty Resume↗</a>',
                            unsafe_allow_html=True
                        )
    with st.container():
        wachi_cols = st.columns([1,6])
        with wachi_cols[0]:
            st.image("graphics/wachi.JPG")
        with wachi_cols[1]:
            st.header("Cocoro Wachi Undergraduate, Milwaukee School of Engineering.")
            st.write("B.S. Computer Science Major, Mathematics Minor, UX Design Minor.")
            st.write("Dwight & Dian Diercks School of Advanced Computing.")
            col, _ = st.columns([2,3])
            with col:
                with st.container(width="stretch"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("+1(224)345-1255")
                        st.write("wachic@msoe.edu")
                    with col2:
                        st.markdown(
                            '<a href="https://www.linkedin.com/in/cocorowachi/" target="_blank">LinkedIn↗</a>',
                            unsafe_allow_html=True
                        )
                        with open("graphics/wachi_resume.pdf", "rb") as f:
                            pdf_bytes = f.read()
                        st.download_button("Download Resume", data=pdf_bytes, file_name="Cocoro Wachi Resume.pdf")
                        
    st.write("---")
    with st.container():
        st.header("Acknowledgement")
        st.write("This undergraduate research and presentation at ICWMM2026 was made possible by the support of:")
        st.write("- Dwight & Dian Diercks School of Advanced Computing")
        st.write("- Civil and Architectural Engineering & Construction Management Department")
        # st.write("of Milwaukee School of Engineering.")
        st.markdown(
            'of <a href="https://www.msoe.edu/" target="_blank">Milwaukee School of Engineering↗</a>',
            unsafe_allow_html=True
        )
    # used for export data for dr gonwa for excel useage
    # import pandas as pd
    # df = pd.DataFrame({
    #     "datetime": acali.datetime,
    #     "MS0208 Total Flow MGD": acali.target_flow
    # })
    # df.to_csv("hourly_MS0208_total.csv", index=False)

    # df = pd.DataFrame({
    #     "datetime": acali.datetime,
    #     "MS0208 RDII Flow MGD": acali.target_flow - acali.diurnal
    # })
    # df.to_csv("hourly_MS0208_rdii.csv", index=False)

    # x = acali.datetime
    # y = acali.target_flow
    # n_days = x.shape[0] // 24
    # x_daily = x[:n_days * 24].reshape(n_days, 24)[:, 0]
    # y_daily = y[:n_days * 24].reshape(n_days, 24)[:, 0]
    # df = pd.DataFrame({
    #     "datetime": x_daily,
    #     "MS0208 Total Flow MGD": y_daily
    # })
    # df.to_csv("daily_MS0208_total.csv", index=False)

    # x = acali.datetime
    # y = acali.target_flow - acali.diurnal
    # n_days = x.shape[0] // 24
    # x_daily = x[:n_days * 24].reshape(n_days, 24)[:, 0]
    # y_daily = y[:n_days * 24].reshape(n_days, 24)[:, 0]
    # df = pd.DataFrame({
    #     "datetime": x_daily,
    #     "MS0208 Total Flow MGD": y_daily
    # })
    # df.to_csv("daily_MS0208_rdii.csv", index=False)
