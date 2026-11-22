"""Compare coulomb counting and EKF on a simulated discharge. Saves plots to results/."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from soc import CellParams, CoulombCounter, SocEKF, pulse_profile, simulate

OUT = Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)

DT = 1.0
SOC0_TRUE = 0.95
SOC0_GUESS = 0.60   # deliberately wrong start value


def main():
    params = CellParams()
    data = simulate(params, pulse_profile(4 * 3600, DT), DT, soc0=SOC0_TRUE)

    cc = CoulombCounter(params, SOC0_GUESS)
    ekf = SocEKF(params, SOC0_GUESS)
    soc_cc, soc_ekf, std_ekf = [], [], []
    for i, v in zip(data["i_meas"], data["v_meas"]):
        soc_ekf.append(ekf.update(i, v, DT))
        std_ekf.append(ekf.soc_std)
        soc_cc.append(cc.update(i, v, DT))
    soc_cc, soc_ekf, std_ekf = map(np.array, (soc_cc, soc_ekf, std_ekf))

    t_h = data["t"] / 3600
    err_cc = (soc_cc - data["soc_true"]) * 100
    err_ekf = (soc_ekf - data["soc_true"]) * 100
    settle = t_h > 0.25  # skip the first 15 min of convergence
    rmse = lambda e: float(np.sqrt(np.mean(e ** 2)))
    print(f"Samples: {len(t_h)}, duration: {t_h[-1]:.2f} h")
    print(f"RMSE after 15 min  coulomb counting: {rmse(err_cc[settle]):5.2f} %SoC")
    print(f"RMSE after 15 min  EKF:              {rmse(err_ekf[settle]):5.2f} %SoC")

    fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    ax[0].plot(t_h, data["i_meas"], lw=0.6)
    ax[0].set_ylabel("Current [A]")
    ax0b = ax[0].twinx()
    ax0b.plot(t_h, data["v_meas"], color="tab:orange", lw=0.6)
    ax0b.set_ylabel("Voltage [V]", color="tab:orange")
    ax[0].set_title("Simulated dynamic discharge (noisy, biased sensors)")

    ax[1].plot(t_h, data["soc_true"] * 100, "k", label="true")
    ax[1].plot(t_h, soc_cc * 100, label="coulomb counting")
    ax[1].plot(t_h, soc_ekf * 100, label="EKF")
    ax[1].fill_between(t_h, (soc_ekf - 2 * std_ekf) * 100, (soc_ekf + 2 * std_ekf) * 100,
                       color="tab:green", alpha=0.2, label="EKF ±2σ")
    ax[1].set_ylabel("SoC [%]")
    ax[1].legend()

    ax[2].plot(t_h, err_cc, label="coulomb counting")
    ax[2].plot(t_h, err_ekf, label="EKF")
    ax[2].axhline(0, color="k", lw=0.5)
    ax[2].set_ylabel("Error [%SoC]")
    ax[2].set_xlabel("Time [h]")
    ax[2].set_ylim(-40, 10)
    ax[2].legend()

    fig.tight_layout()
    fig.savefig(OUT / "soc_comparison.png", dpi=120)
    print(f"Plot saved to {OUT / 'soc_comparison.png'}")


if __name__ == "__main__":
    main()
