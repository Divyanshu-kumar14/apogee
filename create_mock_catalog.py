import json
import os
import random
from datetime import datetime

# ISS parameters for reference
iss_inclination = 51.6
iss_mean_motion = 15.5
iss_altitude = 420.0

catalog = []
for i in range(1, 51):
    # generate random debris near ISS
    incl = iss_inclination + random.uniform(-1, 1)
    mm = iss_mean_motion + random.uniform(-0.1, 0.1)
    
    catalog.append({
        "OBJECT_NAME": f"DEBRIS_{i}",
        "OBJECT_ID": f"2023-00{i}A",
        "NORAD_CAT_ID": 80000 + i,
        "EPOCH": datetime.utcnow().isoformat(),
        "INCLINATION": incl,
        "MEAN_MOTION": mm,
        "RA_OF_ASC_NODE": random.uniform(0, 360),
        "ARG_OF_PERICENTER": random.uniform(0, 360),
        "MEAN_ANOMALY": random.uniform(0, 360),
        "BSTAR": 0.0001,
        "ECCENTRICITY": 0.001
    })

os.makedirs('backend/data/tles', exist_ok=True)
with open('backend/data/tles/catalog_active.json', 'w') as f:
    json.dump(catalog, f, indent=2)

print("Mock catalog created.")
