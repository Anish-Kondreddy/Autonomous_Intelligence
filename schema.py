from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Observation:
    """One perception reading for one object at one timestamp."""
    timestamp: float
    camera_id: str
    track_id: int
    object_class: str
    x: float                                       # bounding box centre x
    y: float                                       # bounding box centre y
    width: float = 0.0
    height: float = 0.0
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)   # e.g. {"hardhat": False}


@dataclass
class Event:
    """A structured event produced by an EventDetector.

    Mirrors the event definition table in the spec: event_type, camera_id,
    track_ids, start_time, end_time, duration (derived), confidence,
    evidence, and a lifecycle state (candidate / active / completed).
    """
    event_type: str
    camera_id: str
    track_ids: List[int]
    start_time: float
    end_time: Optional[float] = None
    confidence: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    state: str = "active"          # candidate | active | completed

    @property
    def duration(self) -> Optional[float]:
        if self.end_time is None:
            return None
        return round(self.end_time - self.start_time, 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "camera_id": self.camera_id,
            "track_ids": self.track_ids,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "confidence": round(self.confidence, 3),
            "evidence": self.evidence,
            "state": self.state,
        }
