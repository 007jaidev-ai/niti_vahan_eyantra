'''
# NV_Task1A.py
# Team ID:          NV_XXXX          # ← fill in your team ID
# Author List:                        # ← fill in
# Filename:         NV_Task1A.py
# Theme:            Niti Vahan
# Functions:        ackermann_wheel_angles, (no additional helpers)
# Global variables: None
'''

import numpy as np
import math

# ─── vehicle constants (DO NOT CHANGE) ───────────────────────────
WHEELBASE       = 0.3302    # L  – distance between front and rear axles (m)
TRACK_WIDTH     = 0.2286    # T  – distance between left and right wheels (m)
WHEEL_OFFSET    = 0.0300    # W  – kingpin offset per side (m)
# ─────────────────────────────────────────────────────────────────

# ==================== ADD YOUR IMPLEMENTATION HERE ====================

def ackermann_wheel_angles(delta):
    """
    Given a single bicycle-model steering angle *delta* (radians),
    return the (left_wheel_angle, right_wheel_angle) pair using
    Ackermann geometry.

    Positive delta  → turning LEFT
    Negative delta  → turning RIGHT
    """

    if delta == 0.0:
        return 0.0, 0.0

    L = WHEELBASE
    d = TRACK_WIDTH - 2 * WHEEL_OFFSET

    R = L / math.tan(delta)

    left_angle  = math.atan(L / (R - d / 2))
    right_angle = math.atan(L / (R + d / 2))

    return left_angle, right_angle

# ==================== END OF YOUR IMPLEMENTATION ======================

if __name__ == "__main__":

    test_angles = np.arange(-0.35, 0.35, 0.05)

    for d in test_angles:
        left, right = ackermann_wheel_angles(d)
        print(f"delta={d:.4f}  ->  left={left:.6f}, right={right:.6f}")
