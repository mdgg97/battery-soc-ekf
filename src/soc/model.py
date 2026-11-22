"""1RC (Thevenin) equivalent circuit model of a Li-ion cell.

Sign convention: discharge current is positive.

    soc[k+1] = soc[k] - eta * I[k] * dt / (3600 * Q)
    v1[k+1]  = a * v1[k] + R1 * (1 - a) * I[k],      a = exp(-dt / (R1 * C1))
    V[k]     = OCV(soc[k]) - v1[k] - R0 * I[k]
"""
from dataclasses import dataclass

import numpy as np

# Typical NMC 18650 open-circuit-voltage curve (illustrative values).
# Replace with your own cell's OCV table once you measure it (step 2).
SOC_TABLE = np.array([0.00, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00])
OCV_TABLE = np.array([3.00, 3.30, 3.45, 3.55, 3.62, 3.67, 3.72, 3.80, 3.88, 3.97, 4.07, 4.20])


def ocv(soc):
    """Open-circuit voltage [V] for a given SoC (0..1), linear interpolation."""
    return np.interp(np.clip(soc, 0.0, 1.0), SOC_TABLE, OCV_TABLE)


def docv_dsoc(soc, h=1e-3):
    """Slope of the OCV curve [V per unit SoC], central difference."""
    lo = np.clip(soc - h, 0.0, 1.0)
    hi = np.clip(soc + h, 0.0, 1.0)
    return (ocv(hi) - ocv(lo)) / (hi - lo)


@dataclass
class CellParams:
    capacity_ah: float = 3.0   # Q, nominal capacity
    r0: float = 0.030          # ohmic resistance [ohm]
    r1: float = 0.015          # polarisation resistance [ohm]
    c1: float = 2000.0         # polarisation capacitance [F]
    eta: float = 1.0           # coulombic efficiency

    @property
    def tau(self):
        return self.r1 * self.c1


class Battery1RC:
    """Ground-truth cell used to generate simulated measurements."""

    def __init__(self, params: CellParams, soc0: float = 1.0):
        self.p = params
        self.soc = soc0
        self.v1 = 0.0

    def terminal_voltage(self, current):
        return ocv(self.soc) - self.v1 - self.p.r0 * current

    def step(self, current, dt):
        """Advance the model by dt seconds with a constant current. Returns terminal voltage before the step."""
        v = self.terminal_voltage(current)
        a = np.exp(-dt / self.p.tau)
        self.soc = self.soc - self.p.eta * current * dt / (3600.0 * self.p.capacity_ah)
        self.v1 = a * self.v1 + self.p.r1 * (1.0 - a) * current
        return v
