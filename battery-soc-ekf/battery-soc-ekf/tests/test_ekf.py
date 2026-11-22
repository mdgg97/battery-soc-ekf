import numpy as np
import pytest

from soc import CellParams, CoulombCounter, SocEKF, pulse_profile, simulate


@pytest.fixture(scope="module")
def run():
    p = CellParams()
    data = simulate(p, pulse_profile(4 * 3600), soc0=0.95)
    ekf, cc = SocEKF(p, soc0=0.60), CoulombCounter(p, soc0=0.60)
    soc_ekf = np.array([ekf.update(i, v, 1.0) for i, v in zip(data["i_meas"], data["v_meas"])])
    soc_cc = np.array([cc.update(i, v, 1.0) for i, v in zip(data["i_meas"], data["v_meas"])])
    return data, soc_ekf, soc_cc


def test_ekf_converges_from_wrong_start(run):
    data, soc_ekf, _ = run
    after_15_min = data["t"] > 900
    err = np.abs(soc_ekf - data["soc_true"])[after_15_min]
    assert err.max() < 0.05  # within 5 %SoC


def test_ekf_beats_coulomb_counting(run):
    data, soc_ekf, soc_cc = run
    rmse = lambda s: np.sqrt(np.mean((s - data["soc_true"]) ** 2))
    assert rmse(soc_ekf) < rmse(soc_cc)


def test_ekf_soc_stays_in_range(run):
    _, soc_ekf, _ = run
    assert soc_ekf.min() >= 0 and soc_ekf.max() <= 1
