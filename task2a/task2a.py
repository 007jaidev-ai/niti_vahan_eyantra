'''
*****************************************************************************************
*
*  ===============================================
*     Niti Vahan (NV) Theme of eYRC 2026-27
*  ===============================================
*
*  This script is intended for implementation of Task 2A of Niti Vahan (NV) Theme.
*
*  Filename:         task2a.py
*  Created:          2026
*  Last Modified:
*  Author:           e-Yantra Team
*
*  You are ONLY allowed to write your code inside the block marked
*  "ADD YOUR IMPLEMENTATION HERE". Do not change anything outside it - the
*  evaluation script relies on the rest of this file staying as it is.
*
*****************************************************************************************
'''

# Team ID:          < Team-ID >
# Author List:      < Names of the team members who worked on this file, comma separated >
# Filename:         task2a.py
# Functions:        detect_lane, compute_control
# Global variables: < List any global variables you add, "None" if you add none >


####################### IMPORT MODULES #######################
import sys
import time

import cv2
import numpy as np

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
##############################################################


##################### SCENE CONSTANTS ########################
# Paths into the CoppeliaSim scene hierarchy, read off Task_2A.ttt.
VISION_SENSOR = '/Niti_Vahan/Camera_joint/Cuboid/visionSensor'
STEER_LEFT    = '/steeringLeft'
STEER_RIGHT   = '/steeringRight'
MOTOR_LEFT    = '/motorLeft'
MOTOR_RIGHT   = '/motorRight'

# The integer signal the evaluation raises when the vehicle must stop.
STOP_SIGNAL = 'NV_stop'
##############################################################


##############################################################
############### ADD YOUR IMPLEMENTATION HERE #################
##############################################################

import math

WHEELBASE = 0.120
TRACK_WIDTH = 0.110
WHEEL_OFFSET = 0.0275
CRUISE_SPEED = 1.2
MAX_STEER = math.radians(35)

_prev_cte = 0
_last_steer = 0.0


def _ackermann(delta):
    if abs(delta) < 1e-9:
        return 0.0, 0.0
    L = WHEELBASE
    d = TRACK_WIDTH - 2 * WHEEL_OFFSET
    R = L / math.tan(delta)
    return math.atan(L / (R - d / 2)), math.atan(L / (R + d / 2))


def _find_lane_center(y_hist, w_hist, mid, thresh=100):
    k = np.ones(11) / 11
    hy = np.convolve(y_hist.astype(float), k, 'same')
    hw = np.convolve(w_hist.astype(float), k, 'same')
    yl = int(np.argmax(hy[:mid])) if np.max(hy[:mid]) > thresh else None
    yr = mid + int(np.argmax(hy[mid:])) if np.max(hy[mid:]) > thresh else None
    wx = int(np.argmax(hw)) if np.max(hw) > thresh else None
    if yl is not None and wx is not None and wx > yl + 15:
        return (yl + wx) // 2
    if yr is not None and wx is not None and wx < yr - 15:
        return (wx + yr) // 2
    if yl is not None and yr is not None and yr > yl + 30:
        rc = (yl + yr) // 2
        return (yl + rc) // 2 if mid < rc else (rc + yr) // 2
    if yl is not None and wx is not None:
        return (yl + wx) // 2
    if yr is not None and wx is not None:
        return (wx + yr) // 2
    if wx is not None:
        return (wx - 80) if wx > mid else (wx + 80)
    if yl is not None:
        return yl + 80
    if yr is not None:
        return yr - 80
    return None


def detect_lane(frame):
    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    yellow = cv2.inRange(hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
    white = cv2.inRange(hsv, np.array([0, 0, 155]), np.array([180, 60, 255]))

    mid = w // 2

    near_t, near_b = int(h * 0.75), int(h * 0.90)
    far_t, far_b = int(h * 0.50), int(h * 0.65)

    c_near = _find_lane_center(
        np.sum(yellow[near_t:near_b], axis=0),
        np.sum(white[near_t:near_b], axis=0), mid)

    c_far = _find_lane_center(
        np.sum(yellow[far_t:far_b], axis=0),
        np.sum(white[far_t:far_b], axis=0), mid, thresh=60)

    if c_near is not None:
        cte = c_near - mid
        heading = float(c_far - c_near) / max(near_t - far_t, 1) if c_far is not None else 0.0
        return {'cte': cte, 'heading': heading, 'valid': True}
    if c_far is not None:
        return {'cte': c_far - mid, 'heading': 0.0, 'valid': True}
    return {'cte': 0, 'heading': 0.0, 'valid': False}


def compute_control(detection, stop_requested):
    global _prev_cte, _last_steer

    if detection is None or not detection.get('valid'):
        l, r = _ackermann(_last_steer * 0.9)
        speed = 0.0 if stop_requested else CRUISE_SPEED * 0.3
        return l, r, speed

    cte = detection['cte']
    heading = detection['heading']

    d_cte = cte - _prev_cte
    _prev_cte = cte

    steer = -(0.004 * cte + 0.002 * d_cte + 0.5 * heading)
    steer = max(-MAX_STEER, min(MAX_STEER, steer))
    _last_steer = steer

    l, r = _ackermann(steer)
    speed = 0.0 if stop_requested else CRUISE_SPEED
    return l, r, speed


##############################################################
############## END OF YOUR IMPLEMENTATION ####################
##############################################################


#################### DO NOT EDIT BELOW THIS LINE ####################
#
# Connecting to the simulator, reading the camera and writing to the joints.
# None of it involves a decision you are being marked on - it is here so that
# every team reads the same picture and drives the same vehicle.
#
#####################################################################

def connect_and_locate():
    '''Open the remote API connection and look up every scene handle once.

    Each getObject() is a network round trip, which is why they all happen
    here rather than inside the loop.
    '''
    try:
        sim = RemoteAPIClient().getObject('sim')
        sim.getSimulationTime()
    except Exception as err:
        raise ConnectionError(
            f'Could not reach CoppeliaSim on the ZMQ Remote API port.\n'
            f'  Is CoppeliaSim running with Task_2A.ttt open?\n'
            f'  Simulator said: {err}')

    handles = {}
    for name, path in (('vision_sensor', VISION_SENSOR),
                       ('steer_left', STEER_LEFT),
                       ('steer_right', STEER_RIGHT),
                       ('motor_left', MOTOR_LEFT),
                       ('motor_right', MOTOR_RIGHT)):
        try:
            handles[name] = sim.getObject(path)
        except Exception as err:
            raise RuntimeError(
                f'No object at "{path}" in the open scene.\n'
                f'  Open Task_2A.ttt from the repository.\n'
                f'  Simulator said: {err}')
    return sim, handles


def read_frame(sim, handles):
    '''Grab one frame from the vehicle's camera as a BGR image.

    The vision sensor hands back a raw byte buffer and a resolution, not an
    image, and three corrections are needed to turn one into the other. None
    of these problems announces itself - each produces a detector that looks
    like it is working on a frame that is wrong:

      * handleVisionSensor() - this scene's sensor renders only when asked.
        Without it every read returns the SAME frame for the whole lap.
      * cv2.flip(frame, 0) - the buffer's first row is the BOTTOM of the
        image, so the road comes out vertically mirrored.
      * RGB2BGR - the buffer is RGB and OpenCV assumes BGR. Without the swap
        every HSV threshold you tuned in Task 1C selects the wrong colour.

    Note `res[1], res[0]` in the reshape too: the resolution comes back as
    (width, height) while NumPy wants rows first.

    Returns None if no frame is ready yet, which happens on the first few
    iterations after the simulation starts.
    '''
    sim.handleVisionSensor(handles['vision_sensor'])
    img, res = sim.getVisionSensorImg(handles['vision_sensor'], 0)
    if len(img) == 0:
        return None
    frame = np.frombuffer(img, dtype=np.uint8).reshape((res[1], res[0], 3))
    frame = cv2.flip(frame, 0)
    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


def drive(sim, handles, left_angle, right_angle, speed):
    '''Write the two steering angles and the drive speed to the joints.'''
    sim.setJointTargetPosition(handles['steer_left'], float(left_angle))
    sim.setJointTargetPosition(handles['steer_right'], float(right_angle))
    sim.setJointTargetVelocity(handles['motor_left'], float(speed))
    sim.setJointTargetVelocity(handles['motor_right'], float(speed))


def main():
    sim, handles = connect_and_locate()

    # While you are developing you press Play yourself. Under evaluation the
    # harness resets the scene, places the vehicle in the lane being tested
    # and starts the simulation - so wait for that rather than starting your
    # own, which would race the harness into position.
    #
    # Your script must never call startSimulation(), stopSimulation() or move
    # the vehicle. Reading the camera and driving the joints is all it does.
    deadline = time.monotonic() + 120.0
    while sim.getSimulationState() != sim.simulation_advancing_running:
        if time.monotonic() > deadline:
            print('The simulation never started. Press Play in CoppeliaSim, '
                  'then run this script again.')
            return 1
        time.sleep(0.05)
    print('Simulation running - driving.')

    frames = 0
    try:
        # The harness stops the simulation when the lap is over, which is the
        # cue to exit - hence testing the state rather than looping forever.
        while sim.getSimulationState() == sim.simulation_advancing_running:
            frame = read_frame(sim, handles)
            if frame is None:
                continue
            frames += 1

            # getInt32Signal() returns None until the signal is first set, so
            # "not set" reads as "not stopping" and the first frames behave.
            stop_requested = bool(sim.getInt32Signal(STOP_SIGNAL))

            detection = detect_lane(frame)
            left_angle, right_angle, speed = compute_control(detection,
                                                             stop_requested)
            drive(sim, handles, left_angle, right_angle, speed)
    except KeyboardInterrupt:
        print('\nInterrupted.')
    except Exception as err:
        # A call raising because the simulation stopped mid-frame is normal at
        # the end of a run; anything else is a bug worth seeing.
        print(f'Loop ended: {type(err).__name__}: {err}')
    finally:
        # Without this, whatever speed was last commanded is still being
        # applied and the vehicle drives on unsteered.
        try:
            sim.setJointTargetVelocity(handles['motor_left'], 0.0)
            sim.setJointTargetVelocity(handles['motor_right'], 0.0)
        except Exception:
            pass

    print(f'{frames} frames processed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
