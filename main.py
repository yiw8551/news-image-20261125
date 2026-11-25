#!/usr/bin/env python3
"""Sum up 25 November 2026's world news in one image.

Renders a 1024x1024 newspaper-style front page: a masthead naming the day,
three featured stories in large tiles, and 37 further dated stories as a
compact numbered grid tagged by region -- 40 stories, 10 region tags.
Pure Python 3 standard library; the PNG encoder and the 5x7 bitmap font
are implemented here from scratch. Output is deterministic.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- font ----

_FONT_ROWS = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".##..", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".###."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
}

GLYPH_W = 5
GLYPH_H = 7


def text_width(text, scale):
    """Pixel width of a string at the given integer scale."""
    if not text:
        return 0
    return len(text) * (GLYPH_W + 1) * scale - scale


# ------------------------------------------------------------- canvas -----

class Canvas:
    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.px = bytearray(colour) * (width * height)

    def set_px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                base = yy * self.w * 3
                for xx in range(x, x + w):
                    if 0 <= xx < self.w:
                        i = base + xx * 3
                        self.px[i:i + 3] = bytes(colour)

    def hline(self, x, y, w, colour, thick=1):
        self.rect(x, y, w, thick, colour)

    def draw_char(self, x, y, ch, scale, colour):
        rows = _FONT_ROWS.get(ch, _FONT_ROWS["?"])
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == "#":
                    self.rect(x + c * scale, y + r * scale, scale, scale, colour)

    def draw_text(self, x, y, text, scale, colour, bold=False):
        cx = x
        for ch in text.upper():
            self.draw_char(cx, y, ch, scale, colour)
            if bold:
                self.draw_char(cx + scale, y, ch, scale, colour)
            cx += (GLYPH_W + 1) * scale
        return cx

    def draw_text_centred(self, y, text, scale, colour, bold=False):
        w = text_width(text, scale) + (scale if bold else 0)
        return self.draw_text((self.w - w) // 2, y, text, scale, colour, bold)


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines of at most max_chars."""
    lines = []
    cur = ""
    for word in text.upper().split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ content -----

FEATURED = [
    ("MIDDLE EAST",
     "HOUTHIS HIT SAUDI REFINERY AND RIYADH",
     "YEMEN'S HOUTHIS SAY THEY STRUCK THE RAS TANURA OIL REFINERY AND "
     "RIYADH'S FINANCE DISTRICT. SAUDI AIR DEFENCES DOWNED FOUR DRONES; "
     "11 PEOPLE WERE HURT WHEN A TOWER WAS HIT."),
    ("NORTH AMERICA",
     "US READIES NEW TARIFFS ON CHINA, EU AND 14 MORE",
     "THE TRUMP ADMINISTRATION IS SET TO UNVEIL ITS 'EXCESS CAPACITY' "
     "PROBE FINDINGS ON 16 TRADING PARTNERS, WITH NEW IMPORT DUTIES "
     "EXPECTED TO STACK ON TOP OF EXISTING TARIFFS."),
    ("MARKETS",
     "ASIA STOCKS TUMBLE AS AI RALLY FIZZLES",
     "ASIA-PACIFIC SHARES FELL 2.3% AS AI DOUBTS RETURNED: SOUTH KOREA "
     "SANK 5.3% AND TAIWAN 5.1%. NVIDIA SHED ABOUT 6% AS THE RALLY OVER "
     "JENSEN HUANG'S RETURN AS CEO FADED."),
]

ITEMS = [
    ("N AMERICA", "ABREGO GARCIA LEAVES THE US VOLUNTARILY FOR SPAIN, ENDING HIS DEPORTATION SAGA"),
    ("N AMERICA", "DEMOCRATS CLINCH HOUSE MAJORITY OF AT LEAST 259 SEATS, BEST RESULT SINCE 1990"),
    ("N AMERICA", "CYBERATTACK BREACHES AN UNCLASSIFIED CIA SYSTEM, A SOURCE SAYS"),
    ("N AMERICA", "CDC DIRECTOR DRAWS DOUBTS FROM STAFF AND ANGER FROM LAWMAKERS"),
    ("N AMERICA", "FORT HOOD SHOOTER HASAN ASKS COURT TO DELAY HIS FIRING-SQUAD EXECUTION"),
    ("N AMERICA", "ARMY TO DETONATE ENTIRE 5-TON STOCKPILE OF LEAD AZIDE EXPLOSIVES IN IOWA"),
    ("N AMERICA", "SHEIN TO PAY $100M TO SETTLE FTC CLAIMS OF DECEPTIVE PRACTICES"),
    ("N AMERICA", "GROUPS SUE TRUMP ADMINISTRATION OVER CHANGES TO PHILADELPHIA SLAVERY EXHIBIT"),
    ("N AMERICA", "TRUMP PARDONS THE THANKSGIVING TURKEYS AT THE WHITE HOUSE"),
    ("LATAM", "GUNMEN HOLD ABOUT 25 PEOPLE HOSTAGE IN A CARTAGENA SUPERMARKET SIEGE"),
    ("LATAM", "VENEZUELA REVEALS PUBLIC DEBT OF $237.5 BILLION"),
    ("LATAM", "ARGENTINA SLIPS INTO TECHNICAL RECESSION"),
    ("EUROPE", "SPAIN: SANCHEZ AND FEIJOO CLASH OVER HOUSING BEFORE SUNDAY'S SNAP ELECTION"),
    ("EUROPE", "TWO ARRESTED OVER SUSPECTED BURGLARY AT THE ROYALS' SANDRINGHAM ESTATE"),
    ("EUROPE", "BRITAIN WARNS FIRMS AIDING UKRAINE TO BRACE FOR RUSSIAN SABOTAGE"),
    ("EUROPE", "TURKISH MILITARY HELICOPTER CRASHES ON TRAINING FLIGHT, KILLING 5 CREW"),
    ("RUSSIA-UKRAINE", "LEAKED RUSSIAN DATA POINTS TO ABOUT 490,000 RUSSIAN DEATHS IN THE UKRAINE WAR"),
    ("RUSSIA-UKRAINE", "UKRAINE AIRS VIDEO OF STRIKES ON RUSSIAN SHIPS OFF LIBYA; 2 LIBYAN OFFICERS DIE"),
    ("MIDEAST", "SAUDI-LED COALITION STRIKES THE HOUTHI-RUN PORT OF HODEIDAH IN YEMEN"),
    ("MIDEAST", "ISRAELI STRIKE ON A GAZA CITY APARTMENT KILLS A FAMILY OF FOUR"),
    ("MIDEAST", "IRAN'S GUARDS SAY TWO TANKERS HIT MINES IN THE STRAIT OF HORMUZ"),
    ("MIDEAST", "JORDAN COURT SENTENCES MAN TO DEATH OVER ATTACK THAT KILLED AN OFFICER"),
    ("MIDEAST", "GAZA DOCTORS ISSUE MENINGITIS ALERT AS CASES JUMP TO 272 IN OCTOBER"),
    ("MIDEAST", "IRAN FLOGS SINGER 74 TIMES OVER AN UNVEILED CONCERT PERFORMANCE"),
    ("AFRICA", "SOUTH AFRICA'S RAMAPHOSA WINS COURT BID TO OVERTURN 'FARMGATE' REPORT"),
    ("AFRICA", "SAHEL INSURGENTS TAKE DRONE WAR TO ARMIES AND THEIR RUSSIAN BACKERS"),
    ("AFRICA", "SENEGAL REGAIN THE AFRICA CUP OF NATIONS TITLE"),
    ("ASIA", "CHINA INVESTIGATES POLITBURO MEMBER AND SHANGHAI PARTY CHIEF CHEN JINING"),
    ("ASIA", "US JURY CONVICTS HUAWEI OF TRADE-SECRET CONSPIRACY AND BANK FRAUD"),
    ("ASIA", "RUSSIAN JETS ENTER SOUTH KOREA'S AIR DEFENCE ZONE, SEOUL SAYS"),
    ("ASIA", "PAKISTAN'S FIRST ASTRONAUT REACHES CHINA'S SPACE STATION"),
    ("ASIA", "HONG KONG MARKS ONE YEAR SINCE THE DEADLY TAI PO FIRE"),
    ("ASIA", "MALAYSIA TO REPATRIATE MORE MYANMAR MIGRANTS"),
    ("OCEANIA", "AUSTRALIA AND SOLOMON ISLANDS SIGN SECURITY TREATY BARRING FOREIGN BASES"),
    ("OCEANIA", "AUSTRALIA INFLATION SURGES PAST FORECASTS, HIGHEST SINCE THE IRAN WAR"),
    ("GLOBAL", "UN: FIVE WOMEN ARE KILLED BY RELATIVES EVERY HOUR AROUND THE WORLD"),
    ("GLOBAL", "LEAKED FILES REVEAL INFANTINO'S 96-YEAR PRIVATE-EQUITY PLAN FOR FIFA"),
]

# -------------------------------------------------------------- render ----

PAPER = (246, 242, 233)
INK = (24, 24, 28)
RED = (168, 18, 32)
TILE = (255, 253, 247)
GREY = (96, 94, 90)

W = H = 1024
MARGIN = 28


def render():
    img = Canvas(W, H, PAPER)

    # Masthead
    img.hline(MARGIN, 18, W - 2 * MARGIN, INK, 3)
    img.draw_text(MARGIN, 30, "MAKE.FUN DAILY - ONE DAY, ONE IMAGE", 1, GREY)
    right = "40 STORIES - 10 REGIONS"
    img.draw_text(W - MARGIN - text_width(right, 1), 30, right, 1, GREY)
    img.draw_text_centred(46, "THE WORLD IN ONE IMAGE", 6, INK)
    img.draw_text_centred(96, "WEDNESDAY 25 NOVEMBER 2026", 3, RED)
    img.hline(MARGIN, 128, W - 2 * MARGIN, INK, 2)

    # Featured tiles
    top = 144
    tile_h = 148
    gap = 12
    tile_w = (W - 2 * MARGIN - 2 * gap) // 3
    for i, (tag, head, body) in enumerate(FEATURED):
        x = MARGIN + i * (tile_w + gap)
        img.rect(x, top, tile_w, tile_h, TILE)
        img.rect(x, top, tile_w, 6, RED)
        img.hline(x, top + tile_h - 2, tile_w, INK, 2)
        img.draw_text(x + 12, top + 16, tag, 1, RED, bold=True)
        hy = top + 34
        for line in wrap(head, 25):
            img.draw_text(x + 12, hy, line, 2, INK)
            hy += 17
        by = hy + 8
        for line in wrap(body, 47):
            img.draw_text(x + 12, by, line, 1, INK)
            by += 10

    # Section header
    sy = top + tile_h + 22
    img.hline(MARGIN, sy + 6, 300, INK, 2)
    img.hline(W - MARGIN - 300, sy + 6, 300, INK, 2)
    img.draw_text_centred(sy, "AROUND THE WORLD IN BRIEF", 2, INK)

    # Compact grid: two columns
    gy = sy + 30
    col_w = (W - 2 * MARGIN - 24) // 2
    col_x = [MARGIN, MARGIN + col_w + 24]
    per_col = (len(ITEMS) + 1) // 2
    row_h = 32
    for idx, (tag, text) in enumerate(ITEMS):
        col = 0 if idx < per_col else 1
        row = idx if col == 0 else idx - per_col
        x = col_x[col]
        y = gy + row * row_h
        prefix = "%02d %s: " % (idx + 1, tag)
        lines = wrap(prefix + text, 76)
        for li, line in enumerate(lines[:2]):
            img.draw_text(x, y + li * 11, line, 1, INK)
        # re-draw the number + tag in red on the first line
        img.draw_text(x, y, prefix.rstrip(), 1, RED, bold=True)

    # Footer
    fy = gy + per_col * row_h + 14
    img.hline(MARGIN, fy, W - 2 * MARGIN, INK, 2)
    img.draw_text_centred(
        fy + 10,
        "SOURCES: REUTERS - AP - BBC - AL JAZEERA - UN - EVERY STORY DATED 25 NOV 2026",
        1, GREY)
    return img


# ---------------------------------------------------------- PNG output ----

def encode_png(img):
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)
        raw += img.px[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    png = encode_png(render())
    out_dir = "/output" if os.path.isdir("/output") else "output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))


if __name__ == "__main__":
    main()
