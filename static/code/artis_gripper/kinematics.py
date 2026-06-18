from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, sin, sqrt
from typing import Optional, Tuple


@dataclass(frozen=True)
class FourBarGeometry:
    l0: float
    l1: float
    l2: float
    l3: float
    theta0: float
    r_tip: float = 0.0
    theta_tip: float = 0.0


def solve_fourbar(theta1: float, geom: FourBarGeometry, elbow: int = 1) -> Optional[Tuple[float, float, Tuple[float, float]]]:
    """Solve planar four-bar closure for theta2, theta3, and fingertip position.

    Equation:
      l1*[cos(theta1), sin(theta1)] + l3*[cos(theta3), sin(theta3)] =
      l0*[cos(theta0), sin(theta0)] + l2*[cos(theta2), sin(theta2)]

    Angles are radians. Returns None if the linkage cannot close.
    """
    ax = geom.l1 * cos(theta1)
    ay = geom.l1 * sin(theta1)
    bx = geom.l0 * cos(geom.theta0)
    by = geom.l0 * sin(geom.theta0)

    dx = bx - ax
    dy = by - ay
    d = sqrt(dx * dx + dy * dy)
    if d <= 1e-12:
        return None
    if d > geom.l2 + geom.l3 or d < abs(geom.l2 - geom.l3):
        return None

    # Circle intersection between radius l3 centered at A and radius l2 centered at B.
    a = (geom.l3**2 - geom.l2**2 + d**2) / (2.0 * d)
    h2 = geom.l3**2 - a**2
    if h2 < -1e-9:
        return None
    h = sqrt(max(0.0, h2))

    ux, uy = dx / d, dy / d
    px, py = ax + a * ux, ay + a * uy
    ix = px + elbow * (-uy) * h
    iy = py + elbow * ux * h

    theta3 = atan2(iy - ay, ix - ax)
    theta2 = atan2(iy - by, ix - bx)
    tip = (
        ix + geom.r_tip * cos(theta3 + geom.theta_tip),
        iy + geom.r_tip * sin(theta3 + geom.theta_tip),
    )
    return theta2, theta3, tip
