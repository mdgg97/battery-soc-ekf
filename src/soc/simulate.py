"""Generate a synthetic discharge test with noisy, biased sensors."""
import numpy as np

from .model import Battery1RC, CellParams


def pulse_profile(duration_s, dt=1.0, seed=0):
    """Dynamic discharge profile: random current pulses (0.3..3 A) with rest periods."""
    rng = np.random.default_rng(seed)
    n = int(duration_s / dt)
    current = np.zeros(n)
    k = 0
    while k < n:
        pulse_len = int(rng.integers(30, 300) / dt)
        rest_len = int(rng.integers(10, 120) / dt)
        current[k:k + pulse_len] = rng.uniform(0.3, 3.0)
        k += pulse_len + rest_len
    return current


def simulate(params: CellParams, current, dt=1.0, soc0=1.0,
             i_bias=0.05, i_noise=0.02, v_noise=0.005, seed=1, soc_min=0.05):
    """Run the true model and return a dict of time series.

    i_bias / i_noise / v_noise model a cheap sensor such as the INA219.
    Simulation stops when the true SoC drops below soc_min.
    """
    rng = np.random.default_rng(seed)
    cell = Battery1RC(params, soc0)
    t, soc_true, i_true, i_meas, v_meas = [], [], [], [], []
    for k, i in enumerate(current):
        if cell.soc < soc_min:
            break
        t.append(k * dt)
        soc_true.append(cell.soc)
        i_true.append(i)
        v = cell.step(i, dt)
        i_meas.append(i + i_bias + rng.normal(0, i_noise))
        v_meas.append(v + rng.normal(0, v_noise))
    return {k: np.array(v) for k, v in dict(
        t=t, soc_true=soc_true, i_true=i_true, i_meas=i_meas, v_meas=v_meas).items()}
