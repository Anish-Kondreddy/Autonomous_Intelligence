# Event Intelligence Engine

A prototype that turns a stream of per-object perception observations
(detections + tracking + attributes) into structured, temporal **events**
(zone entry/exit, prolonged presence, directional movement, proximity,
attribute-based) — without needing a live video/DeepStream pipeline.

This repo implements the MVP intern project spec: a deterministic baseline
first, with a small ML comparison layered on top once the baseline exists.

## Quick start

```bash
pip install -r requirements.txt        # just pytest, the engine itself has no deps
python experiments/run_baseline.py     # run the demo scenario, print detected events
python experiments/run_robustness.py   # same scenario under noise/dropout/rate changes
python -m pytest tests/ -q             # unit tests

# optional, Week 5 ML investigation:
pip install -r requirements-ml.txt
python ml/prolonged_presence_ml.py
```

## Repository structure

```
event_intelligence/       <- the engine itself (the primary deliverable)
    schema.py              Observation + Event data structures
    zones.py                Zone polygons, point-in-polygon membership
    object_state.py          Per-track_id rolling history + derived features
    detectors.py               One state machine per event type
    confidence.py                Simple explainable event confidence score
    engine.py                      Wires everything together
    simulator.py                     Perception metadata generator + noise/dropout/etc

evaluation/
    metrics.py             Precision / recall / F1 between detected and ground-truth events

experiments/
    run_baseline.py         Demo scenario, clean data, all six event types
    run_robustness.py         Same scenario under imperfect perception

ml/
    prolonged_presence_ml.py  Week 5: learned classifier vs. rule-based baseline

tests/
    test_engine.py          Unit tests for detectors + engine
```

## How it maps to the spec

**Perception → Event Intelligence → Enterprise Intelligence.** This repo is
only the middle layer. `simulator.py` stands in for the perception layer
(DeepStream in the real system); nothing here does object detection or
tracking. `event_intelligence/` is the actual deliverable.

**Core technical problem** ("maintain a representation of objects over time
rather than processing every observation independently") is solved by
`ObjectState` in `object_state.py`: it keeps a rolling history per
`track_id` and derives velocity, distance travelled, current zone(s) and
dwell time from it. Detectors never see raw observations directly — they
only see this derived state.

**Event lifecycle** (candidate → active → completed) is implemented as an
explicit per-`track_id` state machine inside each detector in
`detectors.py`. For example `ProlongedPresenceDetector`:
- **Trigger**: object is first seen inside the zone → candidate opens, start
  time recorded.
- **Confirmation**: candidate stays open until dwell time passes the
  threshold → marked confirmed (this is the "event is developing" case the
  spec calls out — we know about it before we can report it).
- **Termination**: object leaves the zone → if confirmed, a completed
  `Event` (with both `start_time` and `end_time`) is emitted. If never
  confirmed, nothing is emitted — no false positive for a brief pass-through.

**Event confidence** (`confidence.py`) is a simple, explainable weighted sum
of mean detection confidence, number of supporting observations, and
duration relative to what's expected — deliberately not a black box, so it
stays auditable per the spec's "Explainability" success criterion.

**Imperfect perception** (`simulator.py`): `apply_position_noise`,
`drop_observations`, `vary_confidence`, `simulate_tracking_loss`,
`simulate_track_id_change`, `vary_observation_rate` implement every row of
the spec's Imperfect Perception table. `run_robustness.py` sweeps these and
reports how precision/recall/F1 degrade — this is the Week 4 deliverable.

**ML investigation** (`ml/prolonged_presence_ml.py`) directly answers the
spec's question — *"where does ML provide measurable value over a
well-designed deterministic baseline?"* — by training a plain logistic
regression on the same task the rule-based `ProlongedPresenceDetector`
solves, and comparing precision/recall/F1 head to head. On the current
synthetic task the rule wins (as expected — it's a linear threshold on the
exact feature the rule checks). The script's docstring explains how to
change the feature set to make the comparison less trivial; genuinely
extending this to an LSTM/GRU or a graph-based multi-object model (for
proximity/interaction events) is the natural next step **only if** this
simple baseline shows deterministic rules aren't enough.

## Example event output

```json
{
  "event_type": "prolonged_presence",
  "camera_id": "camera_01",
  "track_ids": [1],
  "start_time": 1.0,
  "end_time": 7.0,
  "duration": 6.0,
  "confidence": 0.975,
  "evidence": {"zone": "zone_a", "threshold": 3.0},
  "state": "completed"
}
```

## Extending this

- **New event type**: add a class in `detectors.py` following the
  trigger/confirm/terminate pattern of the existing ones, then register it
  in the `build_detectors()` list in an experiment file.
- **New scenario**: compose `generate_linear_walk` / `generate_stationary`
  calls in `simulator.py`, or add a new generator function there.
- **Smoothing noisy trajectories**: `ObjectState.velocity()` currently uses
  a simple two-point finite difference. A Kalman filter (e.g. via
  `filterpy`) is a natural drop-in replacement if `run_robustness.py` shows
  position noise is a real problem.
- **Multi-object interaction beyond pairwise proximity**: a graph-based
  model (`torch-geometric`) is the spec's suggested extension point for
  scenario 5 (multiple objects interacting) if pairwise `ProximityDetector`
  proves insufficient.

## Out of scope (per spec Section 3.3)

VMS/Milestone integration, RTSP, camera config, GPU/DeepStream pipeline
work, object detection/tracking model development, cloud deployment,
CI/CD, production API/auth/UI. This repo is the prototype Event
Intelligence layer only.
