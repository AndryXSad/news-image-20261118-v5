#!/usr/bin/env python3
"""The Daily Globe -- world edition front page, 18 November 2026.

Draws a 1024x1024 newspaper front page with Pillow only. Every story on
the page was checked against real reporting from 17-18 November 2026.
Deterministic: fixed layout, fixed colours, no randomness, no timestamps.

Output: writes entry.png ONLY to $MAKEFUN_OUTPUT_DIR when that variable
is set (the grader sandbox layout); otherwise to the script directory
for plain local runs.
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (26, 26, 26)
SOFT = (74, 74, 74)
FAINT = (120, 116, 104)
RED = (176, 32, 32)
RULE = (26, 26, 26)
OCEAN = (214, 231, 240)
LAND = (232, 219, 190)
LAND_EDGE = (168, 152, 120)
GRIDLINE = (196, 214, 224)
NIGHT_TOP = (13, 27, 58)
NIGHT_LOW = (32, 56, 96)
SEA = (18, 38, 66)
GREEN_BG = (12, 58, 44)
SUNSET_TOP = (248, 176, 92)
SUNSET_LOW = (214, 120, 110)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
NOTO_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size, directory=FONT_DIR):
    return ImageFont.truetype(os.path.join(directory, name), size)


F_MAST = font("DejaVuSerif-Bold.ttf", 62)
F_DATE = font("DejaVuSans-Bold.ttf", 15)
F_META = font("DejaVuSans.ttf", 12)
F_META_B = font("DejaVuSans-Bold.ttf", 12)
F_MAP_LBL = font("DejaVuSans-Bold.ttf", 10)
F_PIN = font("DejaVuSans-Bold.ttf", 11)
F_KEY = font("DejaVuSans.ttf", 12)
F_KICK = font("DejaVuSans-Bold.ttf", 13)
F_LEAD = font("DejaVuSerif-Bold.ttf", 33)
F_DECK = font("DejaVuSerif.ttf", 16)
F_BYLINE = font("NotoSerif-Italic.ttf", 12, NOTO_DIR)
F_PANEL_CAP = font("DejaVuSans-Bold.ttf", 10)
F_PANEL_HEAD = font("DejaVuSerif-Bold.ttf", 16)
F_PANEL_DECK = font("DejaVuSerif.ttf", 12)
F_GRID_HEAD = font("DejaVuSans-Bold.ttf", 15)
F_TAG = font("DejaVuSans-Bold.ttf", 9)
F_GRID = font("DejaVuSans-Bold.ttf", 12)
F_TICK = font("DejaVuSans.ttf", 10)
F_TICK_SM = font("DejaVuSans.ttf", 9)
F_FOOT = font("DejaVuSans.ttf", 10)
F_CHART = font("DejaVuSans-Bold.ttf", 11)
F_CHART_SM = font("DejaVuSans.ttf", 9)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_rule(draw, x0, y, x1, width=1):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def draw_double_rule(draw, x0, y, x1):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=2)
    draw.line([(x0, y + 4), (x1, y + 4)], fill=RULE, width=1)


# ---------------------------------------------------------------- content
# All 33 stories, checked against reporting dated 17-18 Nov 2026.
LEAD_HEAD = "Ukraine destroys a span of Putin's Crimea bridge"
LEAD_DECK = ("Kyiv calls the overnight strike \u2018unprecedented\u2019; rail "
             "traffic resumes as the road span lies in the strait.")
LEAD_BYLINE = "From our correspondents in Kyiv and Moscow"

PANEL_STORIES = [
    ("MANILA \u2014 3",
     "Trump lands in Manila for Quad talks ahead of China visit",
     "Quad leaders meet in Manila before APEC; Trump meets Marcos."),
    ("SHENZHEN \u2014 4",
     "APEC opens in Shenzhen; first Trump\u2013Xi\u2013Putin summit tomorrow",
     "Leaders gather on APEC\u2019s sidelines."),
    ("WALL STREET",
     "Nvidia revenue doubles to $115.8bn; board rules out Huang return",
     "Huang says he would return if asked; board says no."),
]

# (section tag, headline) -- 18 items, 6 per column, fixed-height cells.
GRID_STORIES = [
    ("EUROPE", "Russia hits Kyiv bridges in reply; UN counts 372 dead in October"),
    ("ASIA", "Trump vows deeper Philippines defence ties ahead of Shenzhen"),
    ("SPORT", "Dhoni retires from IPL after 19 years; to mentor CSK"),
    ("EUROPE", "Britain sanctions eight firms over West Bank settlements"),
    ("EUROPE", "Hundreds of thousands march in Prague for media freedom"),
    ("MIDDLE EAST", "Kahana elected Knesset speaker in blow to Netanyahu"),
    ("MIDDLE EAST", "Iran drones hit a US radar site in Bahrain; Kuwait reports attacks"),
    ("ASIA", "Modi presses free, open Indo-Pacific; offers free e-visas to ASEAN tourists"),
    ("MARKETS", "Dow sheds 849 points, dipping 1,000 intraday in chip sell-off"),
    ("EUROPE", "UK sends Kyiv \u00a3240m of air defences"),
    ("AFRICA", "DR Congo peace efforts fail to halt eastern violence"),
    ("AMERICAS", "Pakistani man jailed 27\u00bd years over plot to kill Trump"),
    ("ASIA", "US presses UN aviation body over Taiwan curbs; China hits back"),
    ("ASIA", "Cyclone Akvan bears down on Andhra Pradesh; landfall due 20 Nov"),
    ("BUSINESS", "Anthropic IPO prices today; book six times subscribed"),
    ("EUROPE", "Estonia to shut Russia border from 1 Dec after GRU arson plot"),
    ("MIDDLE EAST", "Gaza ceasefire \u2018faces imminent collapse\u2019, warns Trump\u2019s Board of Peace"),
    ("ASIA", "Xi meets Carney in Shenzhen; Canada\u2013China trade deals extended"),
]

TICKER_ITEMS = [
    "Latvia approves Kulbergs cabinet, 57\u201334",
    "Berlin hands spies hack-back powers as hybrid threats grow",
    "Spain strikes, France walks out in cost-of-living unrest",
    "Ecuador fishermen sue Trump over drone strike",
    "EU readies \u20ac45bn loan for Ukraine",
    "Cape Town baboon move draws protests",
    "Deutsche Bank ignored client warnings, leak shows",
    "Trump\u2019s $10bn BBC suit: judge gives him until 22 Jan",
    "NZ to cover Penrhyn port cost blowouts",
    "One Nation vows 90% refugee-intake cut",
    "Voyager 1 reaches one light-day from Earth",
]

# (number, label, lon, lat) for the map pins.
PINS = [
    (1, "Crimea bridge", 36.5, 45.3),
    (2, "Kyiv", 30.5, 50.45),
    (3, "Manila", 121.0, 14.6),
    (4, "Shenzhen", 114.06, 22.55),
    (5, "Bahrain", 50.55, 26.2),
    (6, "Taipei", 121.56, 25.03),
    (7, "New Delhi", 77.2, 28.6),
    (8, "New York", -74.0, 40.7),
]

MAP_LABELS = [
    ("NORTH AMERICA", -100, 56),
    ("SOUTH AMERICA", -60, -14),
    ("ATLANTIC", -32, 22),
    ("AFRICA", 18, 4),
    ("EUROPE", 12, 55),
    ("ASIA", 92, 56),
    ("INDIAN", 76, -30),
    ("PACIFIC", -152, 2),
    ("AUSTRALIA", 134, -26),
]


# ---------------------------------------------------------------- map
def load_land():
    with open(os.path.join(BASE, "data", "land.json"), "r") as fh:
        return json.load(fh)["land"]


def paint_map(draw, box, polygons):
    """Equirectangular world map with numbered pins and a printed key."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=OCEAN, outline=RULE, width=2)
    lat_top, lat_bot = 84.0, -60.0

    def proj(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * w
        py = y0 + (lat_top - lat) / (lat_top - lat_bot) * h
        return px, py

    # graticule every 30 degrees
    for lon in range(-150, 181, 30):
        px, _ = proj(lon, 0)
        draw.line([(px, y0 + 2), (px, y1 - 2)], fill=GRIDLINE, width=1)
    for lat in (-30, 0, 30, 60):
        _, py = proj(0, lat)
        draw.line([(x0 + 2, py), (x1 - 2, py)], fill=GRIDLINE, width=1)

    for poly in polygons:
        pts = [proj(lon, lat) for lon, lat in poly
               if lat_bot <= lat <= lat_top]
        if len(pts) >= 3:
            draw.polygon(pts, fill=LAND, outline=LAND_EDGE)

    for name, lon, lat in MAP_LABELS:
        px, py = proj(lon, lat)
        tw = draw.textlength(name, font=F_MAP_LBL)
        draw.text((px - tw / 2, py - 6), name, font=F_MAP_LBL,
                  fill=(96, 96, 88))

    for num, _label, lon, lat in PINS:
        px, py = proj(lon, lat)
        r = 9
        draw.ellipse([px - r, py - r, px + r, py + r],
                     fill=RED, outline=(255, 255, 255), width=1)
        s = str(num)
        tw = draw.textlength(s, font=F_PIN)
        draw.text((px - tw / 2, py - 7), s, font=F_PIN,
                  fill=(255, 255, 255))


# ---------------------------------------------------------------- Kerch art
def paint_kerch(draw, box):
    """Night scene: Crimea bridge with one span down, clean smoke puffs."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # sky gradient in horizontal bands
    bands = 24
    for i in range(bands):
        t = i / (bands - 1)
        col = tuple(int(NIGHT_TOP[c] + (NIGHT_LOW[c] - NIGHT_TOP[c]) * t)
                    for c in range(3))
        draw.rectangle([x0, y0 + i * h // bands,
                        x1, y0 + (i + 1) * h // bands + 1], fill=col)
    # stars (fixed positions)
    stars = [(0.06, 0.10), (0.16, 0.22), (0.24, 0.08), (0.33, 0.16),
             (0.44, 0.07), (0.52, 0.20), (0.60, 0.10), (0.68, 0.24),
             (0.78, 0.08), (0.86, 0.18), (0.12, 0.34), (0.30, 0.30),
             (0.48, 0.32), (0.66, 0.36), (0.90, 0.32)]
    for fx, fy in stars:
        draw.ellipse([x0 + fx * w - 1, y0 + fy * h - 1,
                      x0 + fx * w + 1, y0 + fy * h + 1],
                     fill=(235, 238, 245))
    # moon with halo, top right
    mx, my, mr = x0 + 0.90 * w, y0 + 0.13 * h, 13
    for rr, shade in ((22, (52, 76, 116)), (17, (72, 96, 136))):
        draw.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=shade)
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr],
                 fill=(238, 234, 214))
    draw.ellipse([mx - mr + 5, my - mr + 4, mx - mr + 10, my - mr + 9],
                 fill=(214, 208, 186))
    # sea
    sea_y = y0 + int(0.66 * h)
    draw.rectangle([x0, sea_y, x1, y1], fill=SEA)
    for fy, ln in ((0.72, 0.30), (0.80, 0.42), (0.88, 0.24), (0.95, 0.36)):
        draw.line([(x0 + 0.08 * w, y0 + fy * h),
                   (x0 + (0.08 + ln) * w, y0 + fy * h)],
                  fill=(70, 100, 140), width=1)
    # bridge deck: intact left + right, broken middle span
    deck_y = y0 + int(0.52 * h)
    draw.rectangle([x0 + 0.02 * w, deck_y, x0 + 0.40 * w, deck_y + 5],
                   fill=(226, 226, 222))
    draw.rectangle([x0 + 0.62 * w, deck_y, x1 - 0.02 * w, deck_y + 5],
                   fill=(226, 226, 222))
    # fallen span, tilted down into the water
    fx0, fy0 = x0 + 0.42 * w, deck_y + 2
    fx1, fy1 = x0 + 0.58 * w, sea_y + int(0.16 * h)
    draw.line([(fx0, fy0), (fx1, fy1)], fill=(200, 200, 196), width=4)
    draw.line([(fx0, fy0 + 6), (fx1, fy1 + 6)], fill=(160, 160, 156),
              width=2)
    # pylons
    for px in (0.14, 0.80):
        pxx = x0 + px * w
        draw.rectangle([pxx - 3, y0 + int(0.24 * h), pxx + 3, deck_y + 5],
                       fill=(210, 210, 206))
        draw.rectangle([pxx - 8, y0 + int(0.24 * h) - 4, pxx + 8,
                        y0 + int(0.24 * h)], fill=(210, 210, 206))
    # suspension cables from pylons to deck
    for px, span in ((0.14, (0.02, 0.40)), (0.80, (0.62, 0.98))):
        pxx = x0 + px * w
        top_y = y0 + int(0.24 * h)
        for ex in (span[0] + 0.04, span[0] + 0.12, span[1] - 0.12,
                   span[1] - 0.04):
            draw.line([(pxx, top_y), (x0 + ex * w, deck_y)],
                      fill=(190, 196, 204), width=1)
    # blast at the break: glow + starburst spikes
    bx, by = x0 + 0.47 * w, deck_y - 2
    for rr, shade in ((30, (120, 60, 20)), (20, (220, 120, 30)),
                      (12, (250, 200, 80))):
        draw.ellipse([bx - rr, by - rr, bx + rr, by + rr], fill=shade)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x2 = bx + 34 * math.cos(a)
        y2 = by + 34 * math.sin(a)
        draw.line([(bx, by), (x2, y2)], fill=(255, 190, 60), width=2)
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(255, 240, 180))
    # smoke: separate rising puffs, drifting right, fading
    puffs = [(0.47, 0.44, 10, (168, 168, 168)),
             (0.50, 0.37, 12, (182, 182, 182)),
             (0.54, 0.30, 14, (196, 196, 196)),
             (0.59, 0.24, 16, (208, 208, 208)),
             (0.64, 0.18, 18, (220, 220, 220))]
    for fx, fy, r, shade in puffs:
        cx, cy = x0 + fx * w, y0 + fy * h
        draw.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8],
                     fill=shade)
    # ripples where the span hit the water
    for rr in (10, 18, 26):
        draw.arc([fx1 - rr, fy1 - 4, fx1 + rr, fy1 + 8], 0, 180,
                 fill=(120, 150, 185), width=1)
    # caption strip
    draw.rectangle([x0, y1 - 20, x1, y1], fill=(10, 18, 38))
    draw.text((x0 + 8, y1 - 16), "A span down \u2014 the bridge to Crimea",
              font=F_PANEL_CAP, fill=(240, 240, 235))
    draw.rectangle(box, outline=RULE, width=2)


# ---------------------------------------------------------------- panels
def paint_flag_usa(draw, x0, y0, w, h):
    stripe_h = h / 13.0
    for i in range(13):
        col = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([x0, y0 + i * stripe_h,
                        x0 + w, y0 + (i + 1) * stripe_h + 1], fill=col)
    cw, ch = w * 0.42, stripe_h * 7
    draw.rectangle([x0, y0, x0 + cw, y0 + ch], fill=(28, 48, 110))
    for r in range(5):
        for c in range(6):
            cx = x0 + cw * (0.10 + 0.16 * c)
            cy = y0 + ch * (0.14 + 0.18 * r)
            draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1],
                         fill=(255, 255, 255))


def paint_flag_japan(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(255, 255, 255))
    cx, cy, r = x0 + w / 2, y0 + h / 2, h * 0.30
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 0, 45))


def paint_flag_india(draw, x0, y0, w, h):
    third = h / 3.0
    draw.rectangle([x0, y0, x0 + w, y0 + third], fill=(255, 153, 51))
    draw.rectangle([x0, y0 + third, x0 + w, y0 + 2 * third],
                   fill=(255, 255, 255))
    draw.rectangle([x0, y0 + 2 * third, x0 + w, y0 + h],
                   fill=(19, 136, 8))
    cx, cy, r = x0 + w / 2, y0 + h / 2, h * 0.22
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 outline=(6, 62, 138), width=1)
    for k in range(12):
        a = math.radians(k * 30)
        draw.line([(cx, cy),
                   (cx + r * math.cos(a), cy + r * math.sin(a))],
                  fill=(6, 62, 138), width=1)


def paint_flag_australia(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(0, 40, 104))
    # simplified Union Jack canton
    cw, ch = w * 0.5, h * 0.5
    draw.rectangle([x0, y0, x0 + cw, y0 + ch], fill=(0, 36, 125))
    draw.line([(x0, y0), (x0 + cw, y0 + ch)], fill=(255, 255, 255), width=2)
    draw.line([(x0 + cw, y0), (x0, y0 + ch)], fill=(255, 255, 255), width=2)
    draw.line([(x0 + cw / 2, y0), (x0 + cw / 2, y0 + ch)],
              fill=(255, 255, 255), width=3)
    draw.line([(x0, y0 + ch / 2), (x0 + cw, y0 + ch / 2)],
              fill=(255, 255, 255), width=3)
    draw.line([(x0 + cw / 2, y0), (x0 + cw / 2, y0 + ch)],
              fill=(204, 0, 0), width=1)
    draw.line([(x0, y0 + ch / 2), (x0 + cw, y0 + ch / 2)],
              fill=(204, 0, 0), width=1)
    # southern cross + federation star as white dots
    for fx, fy in ((0.72, 0.30), (0.86, 0.52), (0.70, 0.72), (0.92, 0.28),
                   (0.30, 0.78)):
        cx, cy = x0 + fx * w, y0 + fy * h
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2],
                     fill=(255, 255, 255))


def paint_quad(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(240, 235, 218), outline=RULE, width=2)
    flags = [("USA", paint_flag_usa), ("JAPAN", paint_flag_japan),
             ("INDIA", paint_flag_india), ("AUSTRALIA", paint_flag_australia)]
    n = len(flags)
    gap = 10
    fw = (x1 - x0 - gap * (n + 1)) / n
    fh = 48
    fy = y0 + 10
    for i, (name, painter) in enumerate(flags):
        fx = x0 + gap + i * (fw + gap)
        painter(draw, fx, fy, fw, fh)
        draw.rectangle([fx, fy, fx + fw, fy + fh], outline=RULE, width=1)
        tw = draw.textlength(name, font=F_PANEL_CAP)
        draw.text((fx + fw / 2 - tw / 2, fy + fh + 4), name,
                  font=F_PANEL_CAP, fill=INK)
    draw.text((x0 + 10, y1 - 16), "QUAD MEETS IN MANILA \u2014 FIRST IN TWO YEARS",
              font=F_PANEL_CAP, fill=SOFT)


def paint_skyline(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    bands = 20
    for i in range(bands):
        t = i / (bands - 1)
        col = tuple(int(SUNSET_TOP[c] + (SUNSET_LOW[c] - SUNSET_TOP[c]) * t)
                    for c in range(3))
        draw.rectangle([x0, y0 + i * h // bands,
                        x1, y0 + (i + 1) * h // bands + 1], fill=col)
    # sun
    sx, sy, sr = x0 + 0.80 * w, y0 + 0.30 * h, 15
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(224, 84, 48))
    # towers: (x fraction, width fraction, height fraction, spire?)
    towers = [(0.02, 0.10, 0.42, False), (0.14, 0.08, 0.55, False),
              (0.24, 0.12, 0.62, True), (0.38, 0.09, 0.48, False),
              (0.49, 0.07, 0.66, False), (0.58, 0.11, 0.52, False),
              (0.71, 0.09, 0.60, True), (0.82, 0.08, 0.44, False),
              (0.91, 0.07, 0.36, False)]
    base = y1
    for fx, fw, fh, spire in towers:
        tx = x0 + fx * w
        tw = fw * w
        th = fh * h
        draw.rectangle([tx, base - th, tx + tw, base],
                       fill=(44, 34, 52))
        if spire:
            draw.polygon([(tx + tw / 2 - 2, base - th - 14),
                          (tx + tw / 2 + 2, base - th - 14),
                          (tx + tw / 2, base - th - 26)],
                         fill=(44, 34, 52))
        # lit windows, fixed pattern
        rows = int(th // 12)
        cols = max(1, int(tw // 10))
        for r in range(rows):
            for c in range(cols):
                if (r * 3 + c * 7) % 4 == 0:
                    wx = tx + 3 + c * (tw - 6) / cols
                    wy = base - th + 5 + r * 12
                    draw.rectangle([wx, wy, wx + 3, wy + 4],
                                   fill=(252, 214, 110))
    draw.rectangle(box, outline=RULE, width=2)
    draw.text((x0 + 8, y0 + 6), "APEC", font=F_PANEL_CAP,
              fill=(255, 255, 255))


def paint_nvda(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=GREEN_BG, outline=RULE, width=2)
    draw.text((x0 + 8, y0 + 6), "NVDA", font=F_CHART,
              fill=(255, 255, 255))
    # two verified bars: Q3 a year ago $57.0bn, Q3 now $115.8bn (+103%)
    vals = [("Q3 2025", 57.0), ("Q3 2026", 115.8)]
    chart_top = y0 + 26
    chart_bot = y1 - 22
    max_v = 130.0
    bw = 52
    gap = 58
    total = 2 * bw + gap
    start_x = x0 + (w - total) / 2
    for i, (label, val) in enumerate(vals):
        bx = start_x + i * (bw + gap)
        bh = (val / max_v) * (chart_bot - chart_top)
        top = chart_bot - bh
        col = (120, 200, 160) if i == 0 else (60, 220, 140)
        draw.rectangle([bx, top, bx + bw, chart_bot], fill=col)
        draw.rectangle([bx, top, bx + bw, chart_bot], outline=(255, 255, 255),
                       width=1)
        vtxt = "$%.1fbn" % val
        tw = draw.textlength(vtxt, font=F_CHART_SM)
        draw.text((bx + bw / 2 - tw / 2, top - 13), vtxt,
                  font=F_CHART_SM, fill=(255, 255, 255))
        tw = draw.textlength(label, font=F_CHART_SM)
        draw.text((bx + bw / 2 - tw / 2, chart_bot + 4), label,
                  font=F_CHART_SM, fill=(220, 230, 225))
    draw.line([(x0 + 14, chart_bot), (x1 - 14, chart_bot)],
              fill=(200, 210, 205), width=1)
    draw.text((x1 - 8 - draw.textlength("+103% YoY", font=F_CHART),
               y0 + 6), "+103% YoY", font=F_CHART, fill=(110, 255, 170))


# ---------------------------------------------------------------- compose
def compose():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    land = load_land()
    mx = 30
    right = W - mx

    # ---- masthead
    title = "THE DAILY GLOBE"
    tw = draw.textlength(title, font=F_MAST)
    draw.text(((W - tw) / 2, 20), title, font=F_MAST, fill=INK)
    draw.text((mx, 96), "WEDNESDAY 18 NOVEMBER 2026", font=F_DATE, fill=RED)
    mid = "33 STORIES \u00b7 6 CONTINENTS \u00b7 ONE DAY"
    tw = draw.textlength(mid, font=F_META)
    draw.text(((W - tw) / 2, 98), mid, font=F_META, fill=SOFT)
    we = "WORLD EDITION"
    tw = draw.textlength(we, font=F_DATE)
    draw.text((right - tw, 96), we, font=F_DATE, fill=INK)
    draw_double_rule(draw, mx, 118, right)

    # ---- world map + key
    paint_map(draw, (mx, 126, right, 238), land)
    key = ("THE WORLD AT A GLANCE \u2014  1 Crimea bridge \u00b7 2 Kyiv \u00b7 "
           "3 Manila \u00b7 4 Shenzhen \u00b7 5 Bahrain \u00b7 6 Taipei \u00b7 "
           "7 New Delhi \u00b7 8 New York")
    draw.text((mx, 244), key, font=F_KEY, fill=SOFT)

    # ---- lead story + Kerch illustration
    lead_x, lead_w = mx, 530
    draw.text((lead_x, 268), "UKRAINE WAR \u2014 1", font=F_KICK, fill=RED)
    y = 288
    for line in wrap(draw, LEAD_HEAD, F_LEAD, lead_w):
        draw.text((lead_x, y), line, font=F_LEAD, fill=INK)
        y += 38
    y += 6
    for line in wrap(draw, LEAD_DECK, F_DECK, lead_w):
        draw.text((lead_x, y), line, font=F_DECK, fill=INK)
        y += 20
    draw.text((lead_x, y + 4), LEAD_BYLINE, font=F_BYLINE, fill=FAINT)
    paint_kerch(draw, (576, 268, right, 444))

    # ---- three panels
    panel_y0, panel_y1 = 458, 552
    panel_w = 301
    gap = 25
    boxes = []
    for i in range(3):
        px0 = mx + i * (panel_w + gap)
        boxes.append((px0, panel_y0, px0 + panel_w, panel_y1))
    paint_quad(draw, boxes[0])
    paint_skyline(draw, boxes[1])
    paint_nvda(draw, boxes[2])

    # ---- panel stories
    for (px0, _py0, px1, _py1), (kick, head, deck) in zip(boxes, PANEL_STORIES):
        draw.text((px0, 560), kick, font=F_KICK, fill=RED)
        y = 580
        for line in wrap(draw, head, F_PANEL_HEAD, panel_w)[:2]:
            draw.text((px0, y), line, font=F_PANEL_HEAD, fill=INK)
            y += 20
        for line in wrap(draw, deck, F_PANEL_DECK, panel_w)[:2]:
            draw.text((px0, y + 2), line, font=F_PANEL_DECK, fill=SOFT)
            y += 15

    # ---- around the world grid: 3 even columns, fixed-height cells
    draw_rule(draw, mx, 660, right, width=1)
    draw.text((mx, 664), "AROUND THE WORLD", font=F_GRID_HEAD, fill=INK)
    more = "18 MORE STORIES"
    tw = draw.textlength(more, font=F_META_B)
    draw.text((right - tw, 666), more, font=F_META_B, fill=SOFT)
    draw_rule(draw, mx, 684, right, width=1)

    col_w = 301
    col_xs = [mx, mx + col_w + gap, mx + 2 * (col_w + gap)]
    cell_h = 44
    grid_top = 690
    for col in range(3):
        items = GRID_STORIES[col * 6:(col + 1) * 6]
        for row, (tag, head) in enumerate(items):
            cy = grid_top + row * cell_h
            draw.text((col_xs[col], cy), tag, font=F_TAG, fill=RED)
            lines = wrap(draw, head, F_GRID, col_w)[:2]
            ly = cy + 12
            for line in lines:
                draw.text((col_xs[col], ly), line, font=F_GRID, fill=INK)
                ly += 14
            if row < 5:
                draw.line([(col_xs[col], cy + cell_h - 4),
                           (col_xs[col] + col_w, cy + cell_h - 4)],
                          fill=(206, 200, 184), width=1)
        if col < 2:
            vx = col_xs[col] + col_w + gap // 2
            draw.line([(vx, grid_top + 2), (vx, grid_top + 6 * cell_h - 8)],
                      fill=(206, 200, 184), width=1)

    # ---- ticker: black strip, three lines (shrink font until it fits)
    tick_y0 = 960
    draw.rectangle([mx, tick_y0, right, tick_y0 + 42], fill=(18, 18, 18))
    tick_font = F_TICK
    tick_lines = []
    for cand in (F_TICK, F_TICK_SM):
        lines = []
        cur = ""
        for item in TICKER_ITEMS:
            trial = item if not cur else cur + "  \u2022  " + item
            if draw.textlength(trial, font=cand) <= right - mx - 16:
                cur = trial
            else:
                lines.append(cur)
                cur = item
        if cur:
            lines.append(cur)
        tick_lines = lines
        tick_font = cand
        if len(lines) <= 3:
            break
    ty = tick_y0 + 4
    for line in tick_lines[:3]:
        draw.text((mx + 8, ty), line, font=tick_font, fill=(240, 240, 235))
        ty += 13

    # ---- footer
    foot = ("THE DAILY GLOBE \u2014 WORLD EDITION  \u00b7  WEDNESDAY "
            "18 NOVEMBER 2026  \u00b7  PAGE 1")
    tw = draw.textlength(foot, font=F_FOOT)
    draw.text(((W - tw) / 2, 1006), foot, font=F_FOOT, fill=FAINT)
    return img


def main():
    img = compose()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
    else:
        path = os.path.join(BASE, "entry.png")
    img.save(path, format="PNG")
    print("saved", path)


if __name__ == "__main__":
    main()
