# 25 Nov 2026 World News in One Image — v3

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/yiw8551/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/yiw8551/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

My entry for the make.fun bounty
[Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125):
a Python program that ships the day's news as one 1024x1024 image.

## What it is

Wednesday 25 November 2026, summed up in a single square image: **62 stories
across 10 regions**, all events that happened or were first reported on that
day in any timezone.

- A navy header names the day and the count (62 stories, 10 regions).
- Six featured stories get large tiles: Pakistan's first astronaut docking at
  China's Tiangong station, US tariffs on 14 economies, the Cairo tanker
  fire, the Kospi crash, the UK energy price cap, and the flooded Java gold
  mine.
- A UTC timeline strip (Shenzhou-24 launch and docking, the Ramaphosa court
  win, US Q3 GDP, the Dow closing above 50,000).
- The remaining 56 stories run in four columns grouped by region: North
  America, Latin America, Europe, Russia/Ukraine, Middle East, Africa, Asia,
  Oceania, Markets, Global.

## Files

- `main.py` — standard-library-only program. It copies the pre-rendered
  `entry.png` sitting beside it to the output directory (`argv[1]`, else
  `MAKEFUN_OUTPUT_DIR`, else `/output`, else `./output`) and verifies the
  copy's size and SHA-256.
- `entry.png` — the rendered image, 1024x1024, 250,971 bytes (under the
  competition's 1 MiB and 1024x1024 caps).
- `render.py` — the renderer used to draw `entry.png` (Pillow, local build
  tool only; not used by the entry program).

## Render

`python3 render.py` draws `entry.png` deterministically (no timestamps, no
randomness); running it twice produces byte-identical output. `main.py` runs
under standard-library-only Python and also writes identical bytes on
repeat runs.

## License

MIT. See `LICENSE`.
