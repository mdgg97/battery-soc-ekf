import numpy as np

from soc import Battery1RC, CellParams, docv_dsoc, ocv


def test_ocv_is_monotonic():
    s = np.linspace(0, 1, 101)
    assert np.all(np.diff(ocv(s)) > 0)


def test_ocv_slope_positive():
    assert all(docv_dsoc(s) > 0 for s in np.linspace(0.01, 0.99, 50))


def test_one_hour_at_1a_removes_one_over_capacity():
    p = CellParams(capacity_ah=3.0)
    cell = Battery1RC(p, soc0=1.0)
    for _ in range(3600):
        cell.step(1.0, 1.0)
    assert np.isclose(cell.soc, 1 - 1 / 3.0, atol=1e-9)


def test_rest_voltage_equals_ocv():
    cell = Battery1RC(CellParams(), soc0=0.5)
    assert np.isclose(cell.terminal_voltage(0.0), ocv(0.5))


def test_polarisation_settles_to_i_times_r1():
    p = CellParams()
    cell = Battery1RC(p, soc0=0.8)
    for _ in range(int(10 * p.tau)):
        cell.step(2.0, 1.0)
    assert np.isclose(cell.v1, 2.0 * p.r1, rtol=1e-3)
