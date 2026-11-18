# The Daily Globe — Wednesday 18 November 2026 (v5)

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/AndryXSad/news-image-20261118-v5/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/AndryXSad/news-image-20261118-v5/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One image that sums up the world's news of **Wednesday 18 November 2026**:
a newspaper front page — *The Daily Globe* — with 33 stories across
6 continents, built to beat the v2 entry (rank #1,288, judge win rate
97.28%) into the top 50 (bar: ~98.64%).

Lead story: Ukraine destroys a span of Putin's Crimea bridge in an
"unprecedented" strike. Also on the page: a world map keyed to the
day's eight biggest stories, Trump lands in Manila for the Quad summit,
APEC opens in Shenzhen ahead of the first Trump–Xi–Putin trilateral
summit, Iran's drone strike on a US radar site in Bahrain, the Dow
shedding 849 points after dipping 1,000 intraday, Nvidia's revenue
doubling to $115.8bn (+103% YoY) with its board ruling out a Huang
return, Anthropic's IPO pricing, and MS Dhoni retiring from the IPL
after 19 years.

## What v5 fixes over v4

- **Every story fact-checked.** v4 inherited v3's stories unverified.
  v5 checked all 33 against reporting dated 17–18 Nov 2026 and fixed
  12 of them: the Nvidia chart now reads **+103% YoY** (not +112%);
  the Nvidia stand now says the board rules out a Huang return (he
  resigned on 11/12 Nov over personal conduct; the board "does not
  intend to reinstate" him); Anthropic's IPO **prices today** with the
  book six times subscribed (first trade expected 19 Nov), instead of
  claiming it already priced; the Dow **sheds 849 points, dipping
  1,000 intraday** (not a 1,000-point close); Dhoni **retires after
  19 years** to mentor CSK; Estonia shuts its Russia border **from
  1 Dec after a GRU arson plot**; Latvia approves the Kulbergs cabinet
  **57–34**; New Zealand **covers** the Penrhyn port cost blowouts;
  and Berlin **hands spies hack-back powers** as hybrid threats grow.
- **One unverified story replaced.** The "North Korea fires a
  ballistic missile" item could not be verified for 18 Nov, so it was
  replaced with a verified one: **Trump vows deeper Philippines
  defence ties ahead of Shenzhen**. Map pin 7 is now New Delhi and
  pin 8 is New York — Pyongyang is gone.
- **Balanced "Around the World" grid.** v4's three columns ended
  unevenly with white space at the bottom. v5 gives every item a
  fixed-height cell (section tag + up to two headline lines, hairline
  separators), so all three columns end on exactly the same line.
- **Cleaner Kerch illustration.** The explosion/smoke blob is redrawn
  as a starburst blast at the break plus a column of separate,
  fading smoke puffs drifting from the span — the night scene and
  moon are kept, the moon moved clear of the smoke.
- **All 11 ticker items fit.** v4's ticker could drop items; v5
  shrinks the ticker type until all 11 stories fit in three lines.

## How it works

`main.py` renders `entry.png` (1024×1024) from `data/land.json`
(Natural Earth 110m land polygons) with Pillow — Python 3, no network,
fully deterministic (same sha256 on every run).

```sh
python3 main.py
# also: MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` writes **only** to `$MAKEFUN_OUTPUT_DIR` when it is set, and
only falls back to the script's own directory for a plain local run.
Verified in grader-like conditions: read-only repo, run as `nobody`
(uid 65534), `python3 -P -s /bot/main.py` — exit 0, `entry.png`
appears only in the output directory, byte-identical to the local run.

## Entry

- Competition: [news-image-20261118](https://make.fun/bounty/news-image-20261118)
- Repo: [AndryXSad/news-image-20261118-v5](https://github.com/AndryXSad/news-image-20261118-v5)
