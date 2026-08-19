from dataclasses import dataclass
from typing import Dict, List, Tuple

# Might need to consider it being exactly on a polygon line or a vertex, usually not an issue as float
@dataclass
class Zone:
    name: str
    polygon: List[Tuple[float, float]]   # ordered list of (x, y) vertices

    def contains(self, x: float, y: float) -> bool:
        """Ray casting point-in-polygon test."""
        inside = False
        n = len(self.polygon)
        j = n - 1
        for i in range(n):
            xi, yi = self.polygon[i]
            xj, yj = self.polygon[j]
            intersects = ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
            )
            if intersects:
                inside = not inside
            j = i
        return inside


class ZoneManager:
    """Holds all configured zones and answers 'which zone(s) is this point in'."""

    def __init__(self):
        self._zones: Dict[str, Zone] = {}

    def add_zone(self, zone: Zone) -> None:
        self._zones[zone.name] = zone

    def zones_containing(self, x: float, y: float) -> List[str]:
        return [z.name for z in self._zones.values() if z.contains(x, y)]

    def __iter__(self):
        return iter(self._zones.values())
