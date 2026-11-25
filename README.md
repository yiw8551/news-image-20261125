# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/yiw8551/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/yiw8551/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A single-file, standard-library-only Python program that sums up Wednesday
25 November 2026's world news in one 1024x1024 image. It renders a
newspaper-style front page — a masthead naming the day, three featured
stories in large tiles (the Houthi strikes on Saudi Arabia, Washington's
new tariff plans, and the Asia stock sell-off), and 37 further dated
stories as a compact numbered grid — 40 stories in total, each tagged by
region across 10 regions: North America, Latin America, Europe,
Russia-Ukraine, the Middle East, Africa, Asia, Oceania, global bodies and
markets. The PNG encoder and the 5x7 bitmap font are implemented from
scratch in the file, and the output is byte-for-byte deterministic.

## Run it

```sh
python3 main.py
```

This writes `entry.png` to `/output` if that directory exists, otherwise
to `./output`.

<sub>Entered on [make.fun](https://make.fun/?ref=azfjxkfk&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
