"""SoC estimators: plain coulomb counting and an Extended Kalman Filter."""
import numpy as np

from .model import CellParams, ocv, docv_dsoc


class CoulombCounter:
    """Integrates measured current. Simple, but cannot fix a wrong start value or a sensor bias."""

    def __init__(self, params: CellParams, soc0: float):
        self.p = params
        self.soc = soc0

    def update(self, current, voltage, dt):  # voltage unused, same interface as the EKF
        self.soc -= self.p.eta * current * dt / (3600.0 * self.p.capacity_ah)
        return self.soc


class SocEKF:
    """Extended Kalman Filter with state x = [soc, v1].

    Predict uses the 1RC model with the measured current.
    Correct compares the predicted terminal voltage with the measured one.
    Because OCV(soc) is non-linear, the measurement is linearised around the
    current estimate: H = [dOCV/dsoc, -1].
    """

    def __init__(self, params: CellParams, soc0: float,
                 p0=(0.1, 1e-4), q=(1e-10, 1e-8), r=1e-4):
        self.p = params
        self.x = np.array([soc0, 0.0])
        self.P = np.diag(p0)        # initial uncertainty
        self.Q = np.diag(q)         # process noise (model error)
        self.R = r                  # voltage measurement noise variance [V^2]

    def predict(self, current, dt):
        a = np.exp(-dt / self.p.tau)
        F = np.array([[1.0, 0.0], [0.0, a]])
        soc, v1 = self.x
        self.x = np.array([
            soc - self.p.eta * current * dt / (3600.0 * self.p.capacity_ah),
            a * v1 + self.p.r1 * (1.0 - a) * current,
        ])
        self.P = F @ self.P @ F.T + self.Q

    def correct(self, current, voltage):
        soc, v1 = self.x
        v_pred = ocv(soc) - v1 - self.p.r0 * current
        H = np.array([docv_dsoc(soc), -1.0])
        S = H @ self.P @ H + self.R
        K = self.P @ H / S
        self.x = self.x + K * (voltage - v_pred)
        self.x[0] = np.clip(self.x[0], 0.0, 1.0)
        self.P = (np.eye(2) - np.outer(K, H)) @ self.P
        return v_pred

    def update(self, current, voltage, dt):
        """One full EKF cycle: correct with the sample at k, then predict k+1."""
        self.correct(current, voltage)
        soc_k = self.x[0]
        self.predict(current, dt)
        return soc_k

    @property
    def soc_std(self):
        return float(np.sqrt(self.P[0, 0]))
