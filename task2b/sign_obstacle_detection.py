'''
*****************************************************************************************
*
*  ===============================================
*     Niti Vahan (NV) Theme of eYRC 2026-27
*  ===============================================
*
*  This script is intended for implementation of Task 2B of Niti Vahan (NV) Theme.
*
*  Filename:         sign_obstacle_detection.py
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
# Filename:         sign_obstacle_detection.py
# Functions:        detect_signs, detect_obstacle
# Global variables: < List any global variables you add, "None" if you add none >


####################### IMPORT MODULES #######################
import cv2
import numpy as np
##############################################################

# The only sign labels detect_signs() is allowed to return.
SIGN_LABELS = ("School", "Speed40", "Parking", "Hospital")


##############################################################
############### ADD YOUR IMPLEMENTATION HERE #################
##############################################################

def detect_signs(image):
    '''
    Purpose:
    ---
    Detect every road sign visible in a single image, and report what each
    one is and how large it appears. An image can hold zero, one, or more
    than one sign at once.

    Input Arguments:
    ---
    `image` :   [ numpy.ndarray ]
        A single BGR image, of shape (height, width, 3).

    Returns:
    ---
    `detections` :  [ list of dict ]
        Zero, one, or many entries - one per sign found in the image:
        [
            {
                "label" : str,   one of SIGN_LABELS
                "area"  : int,   that sign's area in pixels
            },
            ...
        ]

    Example call:
    ---
    detections = detect_signs(image)

    NOTE:
    ---
    This function must ONLY compute and return the result. Do not call
    cv2.imshow(), cv2.waitKey(), cv2.imwrite() or print() from inside it -
    reading images and reporting results is the evaluator's job, not this
    function's.
    '''

    detections = []
    import math

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    kernel = np.ones((3, 3), np.uint8)

    # --- Red signs: School (triangle) and Speed40 (circle) ---
    red1 = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255]))
    red2 = cv2.inRange(hsv, np.array([160, 70, 50]), np.array([180, 255, 255]))
    red_mask = red1 | red2
    red_clean = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    red_clean = cv2.morphologyEx(red_clean, cv2.MORPH_OPEN, kernel)

    contours_r, hierarchy_r = cv2.findContours(
        red_clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i, cnt in enumerate(contours_r):
        area = cv2.contourArea(cnt)
        if area < 150:
            continue
        if hierarchy_r is not None and hierarchy_r[0][i][3] != -1:
            continue
        peri = cv2.arcLength(cnt, True)
        if peri < 10:
            continue
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        circularity = 4 * math.pi * area / (peri * peri)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / max(h, 1)

        if len(approx) <= 5 and circularity < 0.55 and 0.6 < aspect < 1.8 and area > 180:
            detections.append({"label": "School", "area": int(area)})
        elif circularity > 0.55 and 0.65 < aspect < 1.5 and area > 180:
            detections.append({"label": "Speed40", "area": int(area)})

    # --- Blue signs: Parking and Hospital ---
    blue_mask = cv2.inRange(hsv, np.array([95, 70, 40]), np.array([140, 255, 255]))
    blue_clean = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    blue_clean = cv2.morphologyEx(blue_clean, cv2.MORPH_OPEN, kernel)

    contours_b, _ = cv2.findContours(
        blue_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours_b:
        area = cv2.contourArea(cnt)
        if area < 150:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / max(h, 1)
        if not (0.5 < aspect < 2.0):
            continue

        roi = image[y:y+h, x:x+w]
        if roi.size == 0:
            continue
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, white_roi = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

        rh, rw = white_roi.shape
        if rh < 4 or rw < 4:
            continue
        total_white = np.sum(white_roi > 0)
        if total_white < 10:
            continue

        br = white_roi[rh // 2:, rw // 2:]
        br_white = np.sum(br > 0)
        br_ratio = br_white / total_white

        if br_ratio > 0.15:
            detections.append({"label": "Hospital", "area": int(area)})
        else:
            detections.append({"label": "Parking", "area": int(area)})

    return detections


def detect_obstacle(image):
    '''
    Purpose:
    ---
    Detect whether the obstacle is visible in a single image, and how large
    it appears.

    Input Arguments:
    ---
    `image` :   [ numpy.ndarray ]
        A single BGR image, of shape (height, width, 3).

    Returns:
    ---
    `result` :  [ dict ]
        {
            "present" : bool,   True if the obstacle is visible
            "area"    : int,    its area in pixels, 0 if not present
        }

    Example call:
    ---
    result = detect_obstacle(image)

    NOTE:
    ---
    This function must ONLY compute and return the result. Do not call
    cv2.imshow(), cv2.waitKey(), cv2.imwrite() or print() from inside it -
    reading images and reporting results is the evaluator's job, not this
    function's.
    '''

    import math

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h_img = image.shape[0]

    red1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([15, 255, 255]))
    red2 = cv2.inRange(hsv, np.array([155, 50, 50]), np.array([180, 255, 255]))
    red_mask = red1 | red2

    kernel = np.ones((5, 5), np.uint8)
    red_clean = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    red_clean = cv2.morphologyEx(red_clean, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(
        red_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacle_area = 0
    for cnt in contours:
        a = cv2.contourArea(cnt)
        if a < 300:
            continue
        peri = cv2.arcLength(cnt, True)
        if peri < 10:
            continue
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        circularity = 4 * math.pi * a / (peri * peri)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / max(h, 1)

        is_triangle = len(approx) <= 5 and circularity < 0.55 and 0.6 < aspect < 1.8
        is_circle = circularity > 0.6 and 0.65 < aspect < 1.5

        if is_triangle or is_circle:
            continue

        cy = y + h // 2
        if cy < h_img * 0.25:
            continue

        obstacle_area += int(a)

    present = obstacle_area > 0
    area = obstacle_area if present else 0
    return {"present": present, "area": area}


# ------------------------------------------------------------------
# Add any helper functions and global variables you need below this
# comment, and keep them ABOVE the "END OF YOUR IMPLEMENTATION" line.
# They must be called from detect_signs() or detect_obstacle() - the
# evaluation script only ever calls those two functions. List them in
# the file header too.
# ------------------------------------------------------------------


##############################################################
################ END OF YOUR IMPLEMENTATION ##################
##############################################################


#################### DO NOT EDIT BELOW THIS LINE ####################

def validate_signs(detections, image_name):
    '''
    Purpose:
    ---
    Check that detect_signs() returned the expected structure and normalise
    it, so a malformed return is reported here instead of silently scoring
    zero during evaluation.

    Input Arguments:
    ---
    `detections` :  [ object ]     whatever detect_signs() returned
    `image_name` :  [ str ]        name of the image, used in error messages

    Returns:
    ---
    `clean` :       [ list of dict ]   [{"label": str, "area": int}, ...]
    '''
    where = "detect_signs() on {}".format(image_name)

    if not isinstance(detections, list):
        raise TypeError("{} must return a list, got {}".format(where, type(detections).__name__))

    clean = []
    for index, entry in enumerate(detections):
        entry_where = "{}, entry {}".format(where, index)

        if not isinstance(entry, dict):
            raise TypeError("{} must be a dict, got {}".format(entry_where, type(entry).__name__))

        missing = {"label", "area"} - set(entry.keys())
        if missing:
            raise ValueError("{} is missing the key(s): {}".format(entry_where, ", ".join(sorted(missing))))

        label = entry["label"]
        if label not in SIGN_LABELS:
            raise ValueError("{} returned label = '{}', expected one of {}".format(
                entry_where, label, ", ".join(SIGN_LABELS)))

        area = _validate_area(entry["area"], entry_where)
        clean.append({"label": label, "area": area})

    return clean


def validate_obstacle(result, image_name):
    '''
    Purpose:
    ---
    Check that detect_obstacle() returned the expected structure and
    normalise it.

    Input Arguments:
    ---
    `result` :      [ object ]     whatever detect_obstacle() returned
    `image_name` :  [ str ]        name of the image, used in error messages

    Returns:
    ---
    `clean` :       [ dict ]       {"present": bool, "area": int}
    '''
    where = "detect_obstacle() on {}".format(image_name)

    if not isinstance(result, dict):
        raise TypeError("{} must return a dict, got {}".format(where, type(result).__name__))

    missing = {"present", "area"} - set(result.keys())
    if missing:
        raise ValueError("{} is missing the key(s): {}".format(where, ", ".join(sorted(missing))))

    present = result["present"]
    if not isinstance(present, (bool, np.bool_)):
        raise TypeError("{} returned present of type {}, expected a bool".format(
            where, type(present).__name__))
    present = bool(present)

    area = _validate_area(result["area"], where)
    if not present and area != 0:
        raise ValueError("{} returned present=False but area={}, expected 0".format(where, area))

    return {"present": present, "area": area}


def _validate_area(area, where):
    if isinstance(area, bool) or not isinstance(area, (int, float, np.integer, np.floating)):
        raise TypeError("{} returned area of type {}, expected a number".format(
            where, type(area).__name__))
    area = int(round(float(area)))
    if area < 0:
        raise ValueError("{} returned a negative area: {}".format(where, area))
    return area
