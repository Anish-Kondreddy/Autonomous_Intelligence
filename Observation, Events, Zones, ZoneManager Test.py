from schema import Observation
from zones import Zone, ZoneManager

### Test

manager = ZoneManager()
manager.add_zone(Zone("restricted_zone_a", [(0,0),(100,0),(100,100),(0,100)]))
manager.add_zone(Zone("loading_bay", [(150,0),(250,0),(250,100),(150,100)]))

# Observation compatability check
obs = Observation(timestamp=1.0, camera_id="cam_01", track_id=104,
                   object_class="person", x=25, y=25)

# Zone Manager Test
zones_now = manager.zones_containing(obs.x, obs.y)
print(zones_now)

# Iteration Test
for zone in manager:
    print(f"Configured zone: {zone.name}")