"""Download the NWS 7-day forecast for every Georgia county and save nightly lows.

Run:  python3 freeze.py
Writes: data/ga_counties.geojson  (county shapes, for the map)
        data/freeze.json          (each county's forecast lows)
        data/grid_cache.json      (saves NWS lookups so later runs are faster)
"""
import json, os, time, urllib.request
from datetime import datetime, timezone

STATE_FIPS = "13"  # Georgia
COUNTIES_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
HEADERS = {"User-Agent": "ga-freeze-map (github.com/ga-freeze-map)", "Accept": "application/geo+json"}
os.makedirs("data", exist_ok=True)


def get_json(url, tries=3):
    """Download a URL and parse it as JSON, retrying a couple of times if NWS hiccups."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if attempt == tries - 1:
                raise
            print(f"  retrying ({e})")
            time.sleep(2)


def center(geometry):
    """Rough center of a county: the average of its outline's points."""
    rings = geometry["coordinates"] if geometry["type"] == "Polygon" else [p[0] for p in geometry["coordinates"]]
    pts = [pt for ring in rings[:1] for pt in ring]
    lon = sum(p[0] for p in pts) / len(pts)
    lat = sum(p[1] for p in pts) / len(pts)
    return round(lat, 4), round(lon, 4)


# 1. Georgia county shapes (downloaded once, then reused)
shapes_path = "data/ga_counties.geojson"
if not os.path.exists(shapes_path):
    print("Downloading county shapes...")
    us = get_json(COUNTIES_URL)
    ga = [f for f in us["features"] if f["properties"]["STATE"] == STATE_FIPS]
    with open(shapes_path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": ga}, f)
counties = json.load(open(shapes_path))["features"]

# 2. Cache of county -> NWS forecast URL (this mapping never changes)
cache_path = "data/grid_cache.json"
cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}

# 3. Forecast for each county
results, failed = [], []
for i, c in enumerate(counties, 1):
    fips, name = c["id"], c["properties"]["NAME"]
    lat, lon = center(c["geometry"])
    print(f"[{i}/{len(counties)}] {name}")
    try:
        if fips not in cache:
            cache[fips] = get_json(f"https://api.weather.gov/points/{lat},{lon}")["properties"]["forecast"]
        periods = get_json(cache[fips])["properties"]["periods"]
        nights = [{"name": p["name"], "date": p["startTime"][:10], "low": p["temperature"]}
                  for p in periods if not p["isDaytime"]]
        results.append({"fips": fips, "name": name, "lat": lat, "lon": lon, "nights": nights})
    except Exception as e:
        print(f"  skipped: {e}")
        failed.append(name)
    time.sleep(0.25)  # be polite to NWS

json.dump(cache, open(cache_path, "w"))
json.dump({"updated": datetime.now(timezone.utc).isoformat(timespec="minutes"),
           "counties": results}, open("data/freeze.json", "w"))
print(f"Done: {len(results)} counties saved, {len(failed)} skipped {failed if failed else ''}")