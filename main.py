#!/usr/bin/env python3
"""The World in One Day -- newspaper front page for Monday 23 November 2026.

Draws a 1024x1024 PNG summing up the day's world news and writes it to
/output/entry.png. Python 3 stdlib only, no network, fully deterministic:
the same input always produces byte-identical output.

Stories (all real, reported on Mon 23 Nov 2026):
  1. COP31 climate summit collapses in Antalya without a deal.
  2. Iran-US war widens: missiles hit a US base in Bahrain, Houthis
     strike western Saudi Arabia, tankers attacked in the Strait of Hormuz.
  3. Ukraine war spills over: Russian missiles land in Poland, a drone
     sets a Russian cargo ship ablaze off Finland, 14 missing in Kyiv.
  4. Mexico captures FBI most-wanted cartel boss "El Chapo Isidro".
  5. Indonesian candy-factory fire: 7 dead, 50 workers missing.
  6. Liverpool 4-0 Man Utd: Pochettino's debut ends in a rout.
  7. India post a record 720/9 declared in the Wellington Test.

Run:  python3 main.py
"""

import hashlib
import os
import struct
import sys
import zlib

W, H = 1024, 1024
OUT = os.environ.get("OUT", "/output/entry.png")

# ---------------------------------------------------------------- palette
PAPER = (253, 253, 247)
INK = (12, 12, 12)
RED = (176, 0, 32)
BLUE = (18, 78, 150)
SKY = (120, 180, 225)
GREEN = (34, 120, 60)
GREY = (110, 110, 104)
LIGHT = (238, 238, 230)
GOLD = (184, 134, 11)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, '#' = ink, '.' = blank.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "a": ("     ", "     ", " ####", "    #", " ####", "#   #", " ####"),
    "b": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "),
    "c": ("     ", "     ", " ####", "#    ", "#    ", "#    ", " ####"),
    "d": ("    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"),
    "e": ("     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "),
    "f": ("  ## ", " #   ", "#####", " #   ", " #   ", " #   ", " #   "),
    "g": ("     ", " ####", "#   #", "#   #", " ####", "    #", " ### "),
    "h": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "i": ("  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", " ### "),
    "j": ("   # ", "     ", "  ## ", "   # ", "   # ", "   # ", " ##  "),
    "k": ("#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "),
    "l": (" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "m": ("     ", "     ", "## # ", "# # #", "# # #", "# # #", "# # #"),
    "n": ("     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "o": ("     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "),
    "p": ("     ", "     ", "#### ", "#   #", "#### ", "#    ", "#    "),
    "q": ("     ", "     ", " ####", "#   #", " ####", "    #", "    #"),
    "r": ("     ", "     ", "# ## ", "##  #", "#    ", "#    ", "#    "),
    "s": ("     ", "     ", " ####", "#    ", " ### ", "    #", "#### "),
    "t": (" #   ", " #   ", "#####", " #   ", " #   ", " #   ", "  ## "),
    "u": ("     ", "     ", "#   #", "#   #", "#   #", "#   #", " ####"),
    "v": ("     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "w": ("     ", "     ", "#   #", "# # #", "# # #", "# # #", " # # "),
    "x": ("     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"),
    "y": ("     ", "     ", "#   #", "#   #", " ####", "    #", " ### "),
    "z": ("     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#### ", "#   #", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    '"': (" # # ", " # # ", "     ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "   # ", "  #  ", " #   ", "#    "),
    "&": (" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"),
    "%": ("#   #", "#  # ", "   # ", "  #  ", " #   ", "#  # ", "#   #"),
    "$": ("  #  ", " ####", "# # #", " ### ", "  # #", "#### ", "  #  "),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    ":": ("     ", " ##  ", "     ", " ##  ", "     ", " ##  ", " ##  "),
    ";": ("     ", " ##  ", "     ", " ##  ", " ##  ", " ##  ", " #   "),
    "#": (" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "),
    "*": ("     ", " # # ", "  #  ", "#####", "  #  ", " # # ", "     "),
    "@": (" ### ", "#   #", "# ###", "# # #", "# ###", "#    ", " ### "),
    "|": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(xx, yy, c)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)


# ---------------------------------------------------------------- text
def char_w(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * char_w(scale) - scale


def draw_text(cv, x, y, s, scale, color):
    for ch in s:
        g = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "#":
                    cv.fill_rect(x + col * scale, y + row * scale,
                                 scale, scale, color)
        x += char_w(scale)
    return x


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_w, scale):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, max_w, scale, color, leading=None):
    if leading is None:
        leading = 9 * scale
    for ln in wrap(s, max_w, scale):
        draw_text(cv, x, y, ln, scale, color)
        y += leading
    return y


# ---------------------------------------------------------------- icons
def icon_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, BLUE)
    cv.circle(cx, cy, r, SKY, fill=False)
    # continents: rough blobs made of small filled circles
    for dx, dy, rr in ((-28, -22, 20), (-8, -30, 14), (22, -18, 16),
                       (-30, 18, 16), (5, 8, 18), (28, 22, 12),
                       (-2, 32, 12)):
        cv.circle(cx + dx, cy + dy, rr, GREEN)
    # red crack across the globe
    cv.line(cx - r + 6, cy - 8, cx - 18, cy + 12, RED)
    cv.line(cx - 18, cy + 12, cx + 4, cy - 4, RED)
    cv.line(cx + 4, cy - 4, cx + 26, cy + 22, RED)
    cv.line(cx + 26, cy + 22, cx + r - 8, cy + 6, RED)
    cv.circle(cx, cy, r, INK, fill=False)


def icon_flame(cv, x, y, s, c):
    cv.triangle([(x + s // 2, y), (x, y + s), (x + s, y + s)], c)
    cv.triangle([(x + s // 2, y + s // 3), (x + s // 4, y + s),
                 (x + 3 * s // 4, y + s)], GOLD)


def icon_ship(cv, x, y, s, c):
    cv.fill_rect(x, y + s // 2, s, s // 4, c)
    cv.fill_rect(x + s // 4, y + s // 4, s // 6, s // 4, c)
    cv.line(x + s // 4, y + s // 4, x + s // 2, y, c)
    cv.triangle([(x, y + 3 * s // 4), (x + s, y + 3 * s // 4),
                 (x + s // 2, y + s)], RED)


def icon_cuffs(cv, x, y, s, c):
    cv.circle(x + s // 4, y + s // 2, s // 4, c, fill=False)
    cv.circle(x + 3 * s // 4, y + s // 2, s // 4, c, fill=False)
    cv.line(x + s // 4, y + s // 2, x + 3 * s // 4, y + s // 2, c)


def icon_ball(cv, x, y, s, c):
    cv.circle(x + s // 2, y + s // 2, s // 2, c, fill=False)
    cv.circle(x + s // 2, y + s // 2, s // 6, c)


def icon_bat(cv, x, y, s, c):
    cv.fill_rect(x + s // 3, y, s // 3, 2 * s // 3, c)
    cv.fill_rect(x + s // 3, y + 2 * s // 3, s // 5, s // 3, c)
    cv.circle(x + 3 * s // 4, y + s // 4, s // 6, RED)


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    mx = 32                      # margin
    cw = W - 2 * mx              # content width

    # ---- masthead ----
    cv.hline(mx, 24, cw, INK, 3)
    draw_text_centered(cv, W // 2, 38, "THE WORLD IN ONE DAY", 6, INK)
    draw_text_centered(cv, W // 2, 92,
                       "MONDAY, 23 NOVEMBER 2026  |  ONE PAGE, THE WHOLE WORLD",
                       2, INK)
    cv.hline(mx, 122, cw, INK, 4)
    cv.hline(mx, 130, cw, INK, 1)

    # ---- lead story ----
    y = 146
    draw_text(cv, mx, y, "CLIMATE  -  ANTALYA, TURKIYE", 2, RED)
    y += 30
    draw_text(cv, mx, y, "COP31 COLLAPSES:", 5, INK)
    y += 45
    draw_text(cv, mx, y, "NO CLIMATE DEAL", 5, INK)
    y += 52
    y = draw_para(cv, mx, y,
                  "After two weeks of talks and two days of overtime, nearly "
                  "200 nations walk away from Antalya with no pact at all. "
                  "The final draft never even named fossil fuels, and UN chief "
                  "Antonio Guterres called the outcome deeply disappointing. "
                  "It is the longest climate summit in history - and the "
                  "first to end with no deal since Copenhagen in 2009.",
                  600, 2, INK)
    y += 8
    draw_text(cv, mx, y, "Focus now shifts to COP32 in Addis Ababa.", 2, RED)

    # lead illustration: globe, right column
    icon_globe(cv, 826, 300, 96)
    draw_text_centered(cv, 826, 408, "THE LONGEST COP EVER", 2, INK)
    draw_text_centered(cv, 826, 426, "ENDS EMPTY-HANDED", 2, RED)

    # ---- divider + section header ----
    cv.hline(mx, 452, cw, INK, 3)
    draw_text(cv, mx, 466, "THE DAY IN BRIEF", 2, RED)
    draw_text(cv, mx + text_w("THE DAY IN BRIEF", 2) + 16, 466,
              "- SIX MORE STORIES FROM AROUND THE WORLD", 2, GREY)

    stories = [
        ("GULF WAR WIDENS", RED,
         "The Iran-US war reaches Bahrain and Saudi Arabia. Missiles hit "
         "a US base in Bahrain, Houthis strike western Saudi Arabia, and "
         "tankers come under attack in the Strait of Hormuz.",
         icon_ship),
        ("UKRAINE WAR SPILLS OVER", RED,
         "Two Russian missiles land in Poland. A drone sets a Russian "
         "cargo ship ablaze off Finland, and 14 people are missing after "
         "a drone strike on a building in the Kyiv region.",
         icon_ship),
        ("CARTEL KINGPIN CAUGHT", RED,
         "Mexico captures \"El Chapo Isidro\", one of the FBI's most "
         "wanted cartel bosses, after firefights in Sinaloa leave "
         "11 people dead.",
         icon_cuffs),
        ("FACTORY FIRE HORROR", RED,
         "Seven bodies are recovered and 50 workers are missing after "
         "a blaze tears through a candy factory in Indonesia. The "
         "search for survivors goes on through the night.",
         icon_flame),
        ("LIVERPOOL 4, MAN UTD 0", BLUE,
         "Pochettino's United debut is a nightmare. Yoro is sent off "
         "after 8 minutes and Liverpool run riot at Anfield. United "
         "stay 19th in the Premier League.",
         icon_ball),
        ("CRICKET: INDIA 720/9", BLUE,
         "India post a record 720 for 9 declared in the Wellington "
         "Test against New Zealand - a mountain of runs built on a "
         "slowing Basin Reserve pitch.",
         icon_bat),
    ]

    # 2 columns x 3 rows
    col_w = (cw - 24) // 2
    row_h = 148
    x0, y0 = mx, 500
    for i, (head, accent, body, icon) in enumerate(stories):
        col, row = i % 2, i // 2
        bx = x0 + col * (col_w + 24)
        by = y0 + row * row_h
        if col == 1:
            cv.vline(bx - 12, by, row_h - 16, GREY, 1)
        icon(cv, bx, by + 2, 30, accent)
        draw_text(cv, bx + 40, by + 6, head, 3, INK)
        draw_para(cv, bx, by + 44, body, col_w, 2, INK, leading=16)
        if row < 2:
            cv.hline(bx, by + row_h - 18, col_w, LIGHT, 1)

    # ---- footer ----
    fy = 500 + 3 * row_h + 6
    cv.hline(mx, fy, cw, INK, 3)
    draw_text_centered(cv, W // 2, fy + 12,
                       "THE WORLD IN ONE DAY  -  PAGE 1  -  ALL STORIES REPORTED "
                       "MONDAY 23 NOVEMBER 2026", 2, INK)
    draw_text_centered(cv, W // 2, fy + 34,
                       "Sources: UN News, CNN, Reuters, The Squiz, Observer Voice, "
                       "Jagran Josh", 1, GREY)
    return cv


# ---------------------------------------------------------------- PNG out
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    cv = build()
    n = write_png(cv, OUT)
    with open(OUT, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print("wrote %s (%d bytes, %dx%d, sha256 %s)" % (OUT, n, W, H, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
