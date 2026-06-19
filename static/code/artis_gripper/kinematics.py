from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, sin, sqrt
from typing import Dict, Tuple


@dataclass(frozen=True)
class FourBarGeometry:
    l0: float
    l1: float
    l2: float
    l3: float
    theta0: float = 0.0
    r_tip: float = 0.0
    theta_tip: float = 0.0


def solve_fourbar(theta1: float, geom: FourBarGeometry, elbow: int = 1) -> Dict[str, Tuple[float, float] | float]:
    """Solve the planar four-bar closure equation for one driven angle.

    Equation:
        l1*[cos(theta1), sin(theta1)] + l3*[cos(theta3), sin(theta3)]
        = l0*[cos(theta0), sin(theta0)] + l2*[cos(theta2), sin(theta2)]
    """
    ax = geom.l1 * cos(theta1)
    ay = geom.l1 * sin(theta1)
    bx = geom.l0 * cos(geom.theta0)
    by = geom.l0 * sin(geom.theta0)
    dx = bx - ax
    dy = by - ay
    d = sqrt(dx * dx + dy * dy)
    if d <= 1e-9:
        raise ValueError("Degenerate four-bar configuration")
    if d > geom.l2 + geom.l3 or d < abs(geom.l2 - geom.l3):
        raise ValueError("No real four-bar solution for this theta1")

    a = (geom.l3**2 - geom.l2**2 + d**2) / (2 * d)
    h_sq = geom.l3**2 - a**2
    h = sqrt(max(0.0, h_sq))
    ux, uy = dx / d, dy / d
    px, py = ax + a * ux, ay + a * uy
    sign = 1 if elbow >= 0 else -1
    cx = px + sign * (-uy) * h
    cy = py + sign * ux * h

    theta3 = atan2(cy - ay, cx - ax)
    theta2 = atan2(cy - by, cx - bx)
    tip = (
        cx + geom.r_tip * cos(theta3 + geom.theta_tip),
        cy + geom.r_tip * sin(theta3 + geom.theta_tip),
    )
    return {"theta2": theta2, "theta3": theta3, "joint_c": (cx, cy), "tip": tip}
