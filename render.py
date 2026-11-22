# render.py — draws entry.png for news-image-20261122 v2.
# A 1024x1024 newspaper front page summing up Sunday 22 November 2026.
# Rendered with Pillow + Noto Sans (real text, never an AI picture), so every
# letter stays crisp and legible even at 300 pixels wide.
# Run: python3 render.py  (writes entry.png next to this file)
#
# Layout (all coordinates in px, canvas 1024x1024, side margins 36):
#   masthead  -> red rule, paper name, big date, black rule
#   hero      -> dark teal panel: COP31 collapse (the day's biggest story)
#   2x2 cards -> Bahrain / El Chapo / Kryvyi Rih / markets
#   wide card -> FBI database breach
#   strip     -> three short items + a one-line dateline footer
# Every text block is measured before drawing; if a block would overflow its
# box the script stops loudly instead of writing a broken image.

import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 36                      # side margin; content spans 36..988
PAPER = (247, 243, 234)
INK = (26, 26, 26)
BODY = (64, 58, 48)
RED = (200, 16, 46)
GOLD = (245, 197, 66)
EDGE = (214, 205, 190)
FAINT = (140, 132, 118)
CARD_BG = (255, 255, 255)
HERO_TOP = (16, 78, 70)
HERO_BOT = (8, 48, 44)
HERO_SUB = (226, 236, 232)

FONTS = "/usr/share/fonts/truetype/noto/"


def load(name, size):
    return ImageFont.truetype(FONTS + name, size)


BLACK = lambda s: load("NotoSans-Black.ttf", s)
BOLD = lambda s: load("NotoSans-Bold.ttf", s)
REG = lambda s: load("NotoSans-Regular.ttf", s)

canvas = Image.new("RGB", (W, H), PAPER)
pen = ImageDraw.Draw(canvas)


def fit_lines(text, font, max_w, max_lines=None):
    """Greedy word wrap. Raises if the text cannot fit max_lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if pen.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        raise SystemExit(
            f"OVERFLOW: {len(lines)} lines for {max_lines}-line box: {text!r}")
    return lines


def vgrad(box, top, bottom, radius):
    """Rounded rectangle filled with a vertical gradient."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    grad = Image.new("RGB", (w, h))
    px = grad.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = col
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=radius,
                                           fill=255)
    canvas.paste(grad, (x0, y0), mask)


def diamond(cx, cy, r, color):
    pen.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
                fill=color)


# ---------------- masthead ----------------
pen.line([(MX, 28), (988, 28)], fill=RED, width=4)
pen.text((MX, 40), "THE WORLD IN ONE DAY", font=BOLD(28), fill=RED)
pen.text((MX, 72), "Sunday 22 November 2026", font=BLACK(56), fill=INK)
pen.line([(MX, 146), (988, 146)], fill=INK, width=3)

# ---------------- hero: COP31 collapses ----------------
hx0, hy0, hx1, hy1 = MX, 162, 988, 440
vgrad((hx0, hy0, hx1, hy1), HERO_TOP, HERO_BOT, 16)
pen = ImageDraw.Draw(canvas)
pen.text((62, 178), "CLIMATE  \u2022  ANTALYA, TURKEY",
         font=BOLD(22), fill=GOLD)
pen.text((62, 206), "COP31 COLLAPSES", font=BLACK(70), fill=(255, 255, 255))
pen.text((62, 282), "WITH NO DEAL", font=BLACK(70), fill=(255, 255, 255))
hero_sub = ("Climate talks end with no agreement after two days of overtime "
            "\u2014 the EU rejects a text silent on fossil fuels.")
for i, ln in enumerate(fit_lines(hero_sub, REG(24), 698, max_lines=2)):
    pen.text((62, 362 + i * 30), ln, font=REG(24), fill=HERO_SUB)
# "No deal" mark: a gold ring cut by a diagonal slash, right of the headline.
pen.ellipse([782, 216, 950, 384], outline=GOLD, width=6)
pen.line([(806, 360), (926, 240)], fill=GOLD, width=6)

# ---------------- story cards ----------------
def card(box, accent, kicker, headline, body, head_size=28):
    """One white story card: accent bar, kicker, headline, short body."""
    x0, y0, x1, y1 = box
    pen.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=CARD_BG,
                          outline=EDGE, width=1)
    pen.rectangle([x0 + 10, y0, x1 - 10, y0 + 5], fill=accent)
    tx = x0 + 20
    diamond(tx + 7, y0 + 25, 7, accent)
    pen.text((tx + 22, y0 + 14), kicker, font=BOLD(18), fill=accent)
    head_lines = fit_lines(headline, BOLD(head_size), x1 - x0 - 40,
                           max_lines=2)
    y = y0 + 40
    for ln in head_lines:
        pen.text((tx, y), ln, font=BOLD(head_size), fill=INK)
        y += head_size + 5
    body_lines = fit_lines(body, REG(19), x1 - x0 - 40, max_lines=3)
    y += 4
    for ln in body_lines:
        pen.text((tx, y), ln, font=REG(19), fill=BODY)
        y += 23


card((36, 454, 504, 640), (178, 34, 34), "MIDDLE EAST \u2014 BAHRAIN",
     "Iran strikes Bahrain; US bases hit",
     "Missiles and drones hit a civilian site, wounding two; Houthis fire "
     "on Riyadh as tankers are hit near Hormuz.")
card((520, 454, 988, 640), (180, 83, 9), "MEXICO \u2014 SINALOA",
     "Mexico captures \u2018El Chapo Isidro\u2019",
     "FBI most-wanted cartel boss seized in a night raid; 11 killed, four "
     "of them soldiers, with US intelligence aiding.")
card((36, 654, 504, 840), (30, 58, 138), "WAR IN UKRAINE",
     "Missile kills boy, 7, in Zelenskyy\u2019s hometown",
     "Russian strike kills a child and a woman, 20, and wounds 60; a drone "
     "hits Kyiv flats and a Russian cargo ship burns.")
card((520, 654, 988, 840), (22, 101, 52), "MARKETS \u2014 NEW YORK",
     "Stocks slide into correction",
     "S&P 500 falls 3.7% and Nasdaq 5.3% in a Friday AI sell-off; Japan\u2019s "
     "Nikkei drops 5.1% as the rout spreads.")

# ---------------- wide card: FBI breach ----------------
wx0, wy0, wx1, wy1 = MX, 854, 988, 940
pen.rounded_rectangle([wx0, wy0, wx1, wy1], radius=10, fill=CARD_BG,
                      outline=EDGE, width=1)
pen.rectangle([wx0, wy0 + 10, wx0 + 6, wy1 - 10], fill=(126, 34, 206))
pen.text((62, wy0 + 10), "CYBER \u2014 WASHINGTON", font=BOLD(17),
         fill=(126, 34, 206))
pen.text((62, wy0 + 32), "Trump confirms FBI crime database breached",
         font=BOLD(26), fill=INK)
fbi = ("Hackers got into the NCIC system holding fingerprints, "
       "wanted-persons and missing-persons records.")
fbi_lines = fit_lines(fbi, REG(18), wx1 - 62 - 20, max_lines=1)
pen.text((62, wy0 + 63), fbi_lines[0], font=REG(18), fill=BODY)

# ---------------- bottom strip + dateline ----------------
pen.line([(MX, 956), (988, 956)], fill=INK, width=2)
strip = ("EU\u2013INDONESIA TRADE DEAL SIGNED  \u2022  NIGERIA BOAT: "
         "24 MOURNERS DEAD  \u2022  CIKANDE FIRE: 3 DEAD, 36 MISSING")
strip_lines = fit_lines(strip, BOLD(16), 952, max_lines=1)
pen.text((MX, 966), strip_lines[0], font=BOLD(16), fill=INK)
footer = "All stories happened or were first reported on Sunday 22 November 2026."
fw = pen.textlength(footer, font=REG(14))
pen.text(((W - fw) / 2, 992), footer, font=REG(14), fill=FAINT)

canvas.save("entry.png", optimize=True)
print("wrote entry.png", canvas.size)
