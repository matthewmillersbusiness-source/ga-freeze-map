# Georgia Freeze Map

Live: https://matthewmillersbusiness-source.github.io/ga-freeze-map/

Every Georgia county shaded by its coldest forecast low over the next 7 nights, plus a ranked
"knock list" of where pipes are most likely to freeze. Built for plumbers (and HVAC/insulation
companies) to aim door hangers, texts, and ads before the calls come in. Defaults to a
50-mile service area around Athens; switch to all of Georgia anytime.

## How it works
- `freeze.py` asks the National Weather Service (api.weather.gov, free, no key) for each
  county's 7-day forecast and saves the nightly lows to `data/freeze.json`.
- `index.html` draws the map (Leaflet) and ranks counties by freeze score: how far below the
  threshold each night drops, plus a bonus for hard-freeze nights (28°F or colder).
- A GitHub Action reruns the script every morning at 6am Eastern and republishes the site.

## Run it yourself
    python3 freeze.py              # takes 2-4 minutes, 159 counties
    python3 -m http.server 8000    # then open http://localhost:8000

## What broke today (Day 1 of 22)
- Planned a roofer hail map, but late October has almost no hail. Pivoted to freezes.
- My Mac didn't have room for git's developer tools, so I used GitHub Codespaces instead.
- The Census county file wouldn't load; switched to a county map file hosted on GitHub.
- Typed commands into Copilot's terminal instead of a regular one.
- A stray keystroke (`felse`) broke the script. Python pointed right at the line.
- OpenStreetMap's tile servers blocked my preview, and CARTO's need a key, so I dropped
  the background map. County outlines are enough at this zoom.

## Next ideas
- Street-level knock list: pick a county, highlight streets with the oldest homes (Day 2 data).
- Freeze alert texts when a plumber's counties drop below 32°F.