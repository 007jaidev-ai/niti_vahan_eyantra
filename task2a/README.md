# Task 2A - Arena Navigation Boilerplate

Niti Vahan (NV), eYRC 2026-27.

## Files

| File | What it is |
|---|---|
| `task2a.py` | The boilerplate. Fill in `detect_lane()` and `compute_control()`; leave everything else alone. |
| `Task_2A.ttt` | The CoppeliaSim scene. Open it before you run anything. |

## Requirements

Your `NV_<Team-ID>` environment from Task 0 already has what you need - nothing
new to install since Task 1:

```sh
conda activate NV_<Team-ID>
python -c "import cv2, numpy, coppeliasim_zmqremoteapi_client; print('ok')"
```

## Usage

1. Launch CoppeliaSim and open `Task_2A.ttt`.
2. Press **▶ Play**.
3. In a terminal:

```sh
conda activate NV_<Team-ID>
python task2a.py
```

Press **⏹ Stop** then **▶ Play** to put the vehicle back at its starting point
between runs.

## What you implement

Two functions, and nothing else:

```python
def detect_lane(frame):
    # frame is a corrected BGR image from the vehicle's camera
    return <anything compute_control() can use>

def compute_control(detection, stop_requested):
    return left_angle, right_angle, speed
```

- `left_angle`, `right_angle` - the two **front-wheel** angles, in **radians**.
  The scene's steering joints are **positive to the left**. Nothing is clamped
  for you; the vehicle's own limit is 45°. Use your Task 1A geometry to split
  one steering angle into these two.
- `speed` - drive motor target, in rad/s. `0.0` holds the vehicle still.
- `stop_requested` - `True` while the evaluation is holding you at a stop point.
  It is a **level**, not a pulse: stay stationary for as long as it is `True`.
  Do not time the stop yourself.

Everything below the `DO NOT EDIT BELOW THIS LINE` marker is provided: the
connection, the handle lookup, the camera read, the four joint writes and the
loop. None of it is a decision you are marked on - it is there so every team
reads the same picture and drives the same vehicle.

## Where the marks are

Most of Task 2A is **how closely you hold the middle of your lane**, measured
against a centreline surveyed from the painted road edges and the dashed
divider. Being on the correct side of the divider is not enough - weaving
across your own lane loses marks. The inner lane is worth more than the outer
one.

The evaluation tool on your machine **records** the two laps; the marks are
worked out on the portal when you upload the recording. So the tool will not
print a score - watch the simulator instead, and submit to see the marks.

## What your script must never do

The evaluation resets the scene, places the vehicle in the lane under test, and
starts and stops the simulation. Your script only reads the camera and drives
the joints. Calling `sim.startSimulation()`, `sim.stopSimulation()` or
`sim.setObjectPosition()` on the vehicle fights it for control of the run - the
evaluator reports these when it finds them.

Full instructions are in the theme book.

## Fixing the inner lane

Car works on outer lane but falls off on inner lane curves. Do these changes:

**Step 1** — Line 62, drop the speed:
```
CRUISE_SPEED = 1.2  -->  CRUISE_SPEED = 0.9
```

**Step 2** — Line 63, allow harder steering:
```
MAX_STEER = math.radians(35)  -->  MAX_STEER = math.radians(40)
```

**Step 3** — Line 148, bump the gains. Change this:
```
steer = -(0.004 * cte + 0.002 * d_cte + 0.5 * heading)
```
to this:
```
steer = -(0.007 * cte + 0.003 * d_cte + 0.9 * heading)
```

**Step 4** — Line 153, slow down on curves instead of constant speed. Replace:
```
speed = 0.0 if stop_requested else CRUISE_SPEED
```
with:
```
if stop_requested:
    speed = 0.0
elif abs(heading) > 0.3 or abs(cte) > 60:
    speed = CRUISE_SPEED * 0.5
else:
    speed = CRUISE_SPEED
```

Run it. If it still falls off, lower `CRUISE_SPEED` more (try 0.7).
If it wobbles/zigzags on straights, bring `0.007` back down to `0.005`.
