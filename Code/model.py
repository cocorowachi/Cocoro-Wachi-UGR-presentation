import numpy as np
from numba import njit

@njit
def moving_avg_numba(arr: np.ndarray, length: int) -> np.ndarray:
    """
    Centered moving average similar to np.convolve(arr, np.ones(length)/length, mode='same'),
    but implemented in a numba-friendly fashion using prefix sums.
    At boundaries the window shrinks so the divisor equals actual window length.
    """
    n = arr.shape[0]
    out = np.empty(n, dtype=np.float64)

    # prefix sum: ps[0] = 0, ps[i] = sum(arr[:i])
    ps = np.zeros(n + 1, dtype=np.float64)
    for i in range(n):
        ps[i+1] = ps[i] + arr[i]

    half = length // 2

    for i in range(n):
        start = i - half
        if length % 2 == 0:
            # for even length emulate np.convolve 'same' by centering slightly left
            # this choice is arbitrary but consistent
            start = i - half + 1
        if start < 0:
            start = 0
        end = start + length
        if end > n:
            end = n
            start = max(0, end - length)  # adjust start so window length is length when possible
        window_sum = ps[end] - ps[start]
        window_len = end - start
        # avoid division by zero (shouldn't happen)
        if window_len == 0:
            out[i] = 0.0
        else:
            out[i] = window_sum / window_len

    return out

import numpy as np
from numba import njit

@njit
def moving_min_numba(arr: np.ndarray, length: int) -> np.ndarray:
    """
    Trailing moving minimum with boundary shrink.
    out[i] = min(arr[max(0, i-length+1) : i+1])
    Runs in O(n) using a monotonic deque of indices.
    """
    n = arr.shape[0]
    out = np.empty(n, dtype=np.float64)

    # Deque implemented with a fixed-size array of indices
    dq = np.empty(n, dtype=np.int64)
    head = 0
    tail = 0  # dq[head:tail] is the active deque

    for i in range(n):
        # 1) Evict indices that are out of the window (older than i-length+1)
        left = i - length + 1
        if left < 0:
            left = 0
        while head < tail and dq[head] < left:
            head += 1

        # 2) Maintain deque monotonic increasing by value:
        # Pop from back while current value <= last value (so front is min)
        ai = arr[i]
        while head < tail and arr[dq[tail - 1]] >= ai:
            tail -= 1

        # 3) Push current index
        dq[tail] = i
        tail += 1

        # 4) Front is min
        out[i] = arr[dq[head]]

    return out

@njit
def amm_3(temperature: np.ndarray,
                precip: np.ndarray,
                area: float,
                PAT: int,
                TAT: int,
                RD: float,
                HHL: float,
                AMHL: float,
                hot_shcf: float,
                delta_shcf: float) -> np.ndarray:
    """
    Numba-jitted version of amm_3.
    Inputs must be 1D numpy arrays of dtype float64 (no pandas).
    Returns a 1D numpy array of float64 (simulated flow).
    """

    # Level 3
    cold_shcf = hot_shcf + delta_shcf
    L = 1.2 * (cold_shcf - hot_shcf)
    k = 4.7964 / (30.0 - 70.0)
    x_0 = (70.0 + 30.0) / 2.0

    MAT_t_df = moving_avg_numba(temperature, TAT)
    # logistic-like seasonal curve
    n_mat = MAT_t_df.shape[0]
    SHCF_t = np.empty(n_mat, dtype=np.float64)
    for i in range(n_mat):
        SHCF_t[i] = (L / (1.0 + np.exp(-k * (MAT_t_df[i] - x_0)))) + cold_shcf - (11.0 / 12.0) * L

    # Level 2
    MAP_t = moving_avg_numba(precip, PAT)
    AMRF = 0.5 ** (1.0 / AMHL)
    RW_nd = np.copy(SHCF_t)

    # guard for AMRF==1 (shouldn't happen with given formula) but avoid division by zero
    if AMRF == 1.0:
        denom = 1e-12
    else:
        denom = np.log(AMRF)

    for row_i in range(1, RW_nd.shape[0]):
        RW_nd[row_i] = (AMRF - 1.0) / denom * SHCF_t[row_i] * MAP_t[row_i] + (AMRF * RW_nd[row_i - 1])

    # Level 1
    SF = 0.5 ** (1.0 / HHL)
    Q_t_nd = np.copy(RW_nd)

    for row_i in range(1, Q_t_nd.shape[0]):
        Q_t_nd[row_i] = area * (RD + ((RW_nd[row_i] + RW_nd[row_i - 1]) / 2.0)) * MAP_t[row_i] * (1.0 - SF) + (SF * Q_t_nd[row_i - 1])

    return Q_t_nd


@njit
def poly_model(indicator: np.ndarray, p: float, m: float) -> np.ndarray:
    n = indicator.shape[0]
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        out[i] = m * (indicator[i] ** p)
    return out
