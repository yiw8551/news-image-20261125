#!/usr/bin/env python3
"""news-image-20261125 v2 — renders 'The World in One Image' for
Wednesday 25 November 2026. 62 verified stories, 10 regions.
Deterministic PIL render: run twice, outputs are byte-identical.
Usage: python3 main.py [output.png]
"""
import hashlib
import sys
from PIL import Image, ImageDraw, ImageFont

W = 3000
MARGIN = 96
COL_GAP = 48
CONTENT_W = W - 2 * MARGIN

# ---- palette -------------------------------------------------------------
INK      = (18, 22, 34)      # near-black navy
PAPER    = (250, 247, 240)   # warm off-white
NAVY     = (13, 32, 66)
NAVY2    = (24, 52, 96)
GOLD     = (201, 148, 32)
RED      = (178, 34, 34)
TEAL     = (13, 110, 110)
ORANGE   = (204, 92, 18)
PURPLE   = (88, 60, 140)
GREEN    = (34, 120, 64)
GREY     = (92, 96, 104)
LIGHT    = (233, 229, 220)
CARD     = (255, 255, 255)
RULE     = (200, 194, 182)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B  = FONT_DIR + "/dejavu/DejaVuSerif-Bold.ttf"
SANS     = FONT_DIR + "/dejavu/DejaVuSans.ttf"
SANS_B   = FONT_DIR + "/dejavu/DejaVuSans-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

# ---- content -------------------------------------------------------------
MASTHEAD_TITLE = "THE WORLD IN ONE IMAGE"
MASTHEAD_SUB   = "WEDNESDAY  ·  25 NOVEMBER 2026"
MASTHEAD_META  = "62 STORIES  ·  10 REGIONS  ·  EVERY STORY DATED 25 NOV 2026"

# (tag, colour, headline, detail, icon)
FEATURED = [
    ("SPACE", NAVY2,
     "PAKISTAN'S FIRST ASTRONAUT DOCKS AT TIANGONG",
     "Shenzhou-24 docks 11:56 Beijing time. Muhammad Zeeshan Ali, 40, is the "
     "first Pakistani in orbit — and the first foreigner aboard China's "
     "station. Crew: Tang Hongbo, Wu Yi. Stay: about a week.",
     "rocket"),
    ("TRADE", RED,
     "US UNVEILS TARIFFS ON 14 ECONOMIES",
     "USTR proposes duties of up to 20% on China, 15% on the EU, Japan, "
     "South Korea, Taiwan and Switzerland — up to 35% on Vietnam if talks "
     "fail. Hearing 25 Jan; nothing in force yet.",
     "bars"),
    ("DISASTER", ORANGE,
     "CAIRO TANKER FIRE KILLS AT LEAST 31",
     "A fuel tanker overturns and explodes on Cairo's Ring Road at Al-Warraq, "
     "Giza. At least 31 dead, 21 injured; dozens of cars and motorcycles "
     "charred. Toll still preliminary.",
     "flame"),
    ("MARKETS", PURPLE,
     "KOSPI CRASHES 6.2% AS CHIP ROUT SPREADS",
     "Seoul closes at 4,697.51, lowest since January. Samsung -9.9%, "
     "SK Hynix -11.1%. Taiwan -4.8%, Nikkei -2.8%, SoftBank -14.8%.",
     "crash"),
    ("ENERGY", TEAL,
     "UK ENERGY BILLS TO JUMP 26%",
     "Ofgem lifts the price cap to £2,166 a year for typical use from "
     "January, up £443 — highest since 2023. About 20m households hit; "
     "£100 support payment promised.",
     "plug"),
    ("DISASTER", GREEN,
     "JAVA GOLD MINE FLOOD: 9 DEAD, 17 TRAPPED",
     "Heavy rain floods an unauthorised mine shaft near Bogor, West Java. "
     "Nine bodies recovered; 17 miners believed trapped 100m down. "
     "325 rescuers on site.",
     "mine"),
]

# (region, colour, [(headline, detail), ...])
SECTIONS = [
    ("NORTH AMERICA", NAVY2, [
        ("US economy grows 4.3% in Q3",
         "Second estimate revises growth up from 3.4%; fastest in three years, BEA says."),
        ("Dow holds above 50,000",
         "Closes 50,182.95 (+0.33%) after recovering from a 1,100-point intraday slide."),
        ("Thanksgiving storms threaten 250m",
         "Severe weather disrupts holiday travel; Macy's parade postponed to Saturday."),
        ("Abrego Garcia leaves US for Spain",
         "Salvadoran man mistakenly deported in March departs voluntarily; hopes to return."),
        ("Democrats clinch House majority of 259",
         "Best general-election result since 1990, AP projects."),
        ("Cyberattack breaches CIA system",
         "Unclassified CIA and ODNI systems hit, sources tell AP."),
        ("CDC director faces staff doubts",
         "Employees question leadership; legislators press for answers."),
        ("Fort Hood shooter seeks delay",
         "Nidal Hasan asks a court to delay his execution by firing squad."),
        ("Army to detonate 5 tons of lead azide",
         "Degraded explosive stockpile destroyed at an Iowa plant."),
        ("Shein to pay $100m FTC settlement",
         "Settles allegations of deceptive practices."),
        ("Groups sue over slavery exhibit",
         "Philadelphia exhibit alterations challenged in court."),
        ("Trump pardons Thanksgiving turkeys",
         "White House ceremony ahead of the holiday."),
        ("FCC clears SpaceX for 1m satellites",
         "Approval for a million-satellite constellation for space data centres."),
        ("Birthright order blocked again",
         "Second judge blocks Trump's newest order curtailing birthright citizenship."),
        ("Plane crash kills family of 6",
         "Small plane crashes off the Mississippi coast on a fishing trip."),
    ]),
    ("LATIN AMERICA", GREEN, [
        ("Cartagena hostages freed",
         "Police storm a supermarket, free ~20 remaining hostages; one captor killed."),
        ("Venezuela reveals $237.5bn debt",
         "Government discloses its public debt total."),
        ("Argentina enters technical recession",
         "Economy contracts into recession."),
    ]),
    ("EUROPE", TEAL, [
        ("Spain heads for snap election",
         "29 Nov vote; Sanchez and Feijoo clash over the housing crisis."),
        ("Sandringham burglary arrests",
         "Two men held over a suspected burglary at the royal estate."),
        ("UK firms warned of Russian sabotage",
         "Security officials tell Ukraine-aiding firms to brace for attacks."),
        ("Turkish helicopter crashes",
         "Training flight crash kills 5 crew members."),
        ("Nuclear test veterans win inquiry",
         "UK veterans win a 40-year battle for an inquiry into Cold War tests."),
        ("Duran Duran's Andy Taylor dies at 65",
         "Guitarist and songwriter dies; tributes pour in."),
    ]),
    ("RUSSIA & UKRAINE", RED, [
        ("Leak: ~490,000 Russian war dead",
         "Leaked statistics-agency data analysed by BBC; true toll may top 700,000."),
        ("Ukraine hits Russian ships off Benghazi",
         "Two Libyan naval officers die of wounds; Libya vows retaliation."),
        ("Ukraine strikes Russian air base",
         "Five planes damaged in the strike, Kyiv says."),
        ("Russian missiles hit Kyiv",
         "Ballistic missiles strike a shopping centre and buildings late Wednesday."),
        ("34 nations demand Russia stop riot gas",
         "34 countries and the EU call for a halt to alleged battlefield use."),
    ]),
    ("MIDDLE EAST", ORANGE, [
        ("Houthis hit Saudi refinery and Riyadh",
         "Houthis claim Ras Tanura attack; 11 wounded in a Riyadh tower strike."),
        ("Coalition strikes Hodeidah port",
         "Saudi-led strikes hit the Houthi-run Red Sea port and sites in Saada."),
        ("Israeli strike kills family of four",
         "Apartment in Gaza City's Shati camp hit; official, wife and two daughters killed."),
        ("Two tankers hit mines in Hormuz",
         "Iran's Revolutionary Guards say vessels struck mines in the strait."),
        ("Jordan sentences man to death",
         "State Security Court ruling over an attack that killed an officer."),
        ("Gaza meningitis alert",
         "Cases hit 272 in October, over eight times the typical monthly rate."),
        ("Iran flogs singer 74 times",
         "Punishment over an unveiled concert performance."),
    ]),
    ("AFRICA", (150, 90, 20), [
        ("Ramaphosa wins court fight",
         "Court sets aside the Farmgate panel report against him."),
        ("Sahel insurgents weaponise drones",
         "JNIM has carried out 187 drone attacks since 2023, Reuters finds."),
        ("Senegal regain AFCON title",
         "Senegal win the Africa Cup of Nations again."),
        ("Kenyan cult leader convicted again",
         "Mackenzie, serving 200 years, convicted of new charges."),
        ("RSF drone strikes kill 19 in Sudan",
         "Strikes in two cities kill 19 civilians, wound 20, lawyers say."),
        ("Ebola workers flee Congo fighting",
         "Fighting in eastern Congo forces response teams to evacuate."),
    ]),
    ("ASIA", PURPLE, [
        ("China probes Politburo member Chen Jining",
         "Shanghai party chief investigated; fourth Politburo inquiry since 2025."),
        ("Huawei convicted in US trial",
         "Jury finds conspiracy to steal trade secrets and bank fraud."),
        ("Russian warplanes enter Korean ADIZ",
         "Seoul says Russian jets flew into its air defence zone."),
        ("Hong Kong marks Tai Po fire anniversary",
         "One year since the deadly estate fire; survivors demand accountability."),
        ("Malaysia to repatriate Myanmar migrants",
         "Another 6,803 to be sent home next month."),
        ("Bangladesh raises garment wage 36%",
         "Minimum pay rises to $139 a month after protests."),
        ("N. Korea expels Swiss envoy",
         "Pyongyang orders diplomat out in 48 hours and office shut in sanctions row."),
    ]),
    ("OCEANIA", (16, 120, 150), [
        ("Australia–Solomons security treaty",
         "Canberra pact excludes foreign military bases."),
        ("Australia passes online safety law",
         "Big Tech faces multibillion-dollar fines under new rules."),
    ]),
    ("MARKETS", (120, 40, 90), [
        ("Nasdaq slides 0.62% on Wednesday",
         "S&P 500 -0.25% as the AI rout deepens."),
        ("Nvidia falls 5.9%",
         "A day after soaring 31.5% on Huang's return as CEO."),
        ("Australian inflation runs hot",
         "Trimmed mean 3.8% in October, pressuring the Reserve Bank."),
    ]),
    ("GLOBAL", (90, 90, 90), [
        ("Five women killed every hour",
         "UN femicide figures for 2025, released for the 25 Nov international day."),
        ("FIFA leak: Infantino's 96-year plan",
         "Leaked documents show a private-equity plan for the World Cup."),
    ]),
]

TIMELINE = [
    ("00:18", "Shenzhou-24 launches, Jiuquan"),
    ("03:56", "Shenzhou-24 docks at Tiangong"),
    ("08:34", "Ramaphosa wins Farmgate court bid"),
    ("13:30", "US Q3 GDP +4.3% released"),
    ("21:00", "Dow closes 50,182.95, above 50,000"),
]

FOOTER = ("DATE CHECK — every story happened or was first reported on 25 Nov 2026 "
          "(any timezone).  Sources: Reuters · AP · BBC · Al Jazeera · Xinhua / CMSA · "
          "BEA · Ofgem · UN · USTR.  Rendered 26 Nov 2026 · v2")

# ---- text helpers ----------------------------------------------------------
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_h(draw, lines, fnt, leading):
    if not lines:
        return 0
    return len(lines) * fnt.size + (len(lines) - 1) * leading


# ---- drawn icons (simple geometric, deterministic) -------------------------
def draw_icon(d, kind, cx, cy, s, colour):
    """Small pictogram centred at (cx, cy), size s, in colour."""
    if kind == "rocket":
        d.polygon([(cx, cy - s), (cx + s * 0.32, cy + s * 0.1),
                   (cx + s * 0.18, cy + s * 0.55), (cx - s * 0.18, cy + s * 0.55),
                   (cx - s * 0.32, cy + s * 0.1)], fill=colour)
        d.ellipse([cx - s * 0.14, cy - s * 0.45, cx + s * 0.14, cy - s * 0.1],
                  fill=PAPER)
        d.polygon([(cx - s * 0.05, cy + s * 0.55), (cx + s * 0.05, cy + s * 0.55),
                   (cx, cy + s * 0.95)], fill=GOLD)
        d.ellipse([cx - s * 0.9, cy - s * 0.75, cx - s * 0.55, cy - s * 0.4],
                  outline=colour, width=3)
    elif kind == "bars":
        vals = [0.45, 0.7, 1.0, 0.6]
        bw = s * 0.32
        for i, v in enumerate(vals):
            x0 = cx - s + i * (bw + s * 0.12)
            d.rectangle([x0, cy + s * 0.6 - v * s * 1.1, x0 + bw,
                         cy + s * 0.6], fill=colour)
        d.line([cx - s * 1.1, cy + s * 0.6, cx + s * 1.1, cy + s * 0.6],
               fill=colour, width=4)
    elif kind == "flame":
        d.polygon([(cx, cy - s), (cx + s * 0.55, cy - s * 0.1),
                   (cx + s * 0.75, cy + s * 0.45), (cx + s * 0.3, cy + s * 0.7),
                   (cx, cy + s * 0.35), (cx - s * 0.3, cy + s * 0.7),
                   (cx - s * 0.75, cy + s * 0.45), (cx - s * 0.55, cy - s * 0.1)],
                  fill=colour)
        d.ellipse([cx - s * 0.28, cy - s * 0.05, cx + s * 0.28, cy + s * 0.55],
                  fill=GOLD)
    elif kind == "crash":
        pts = [(cx - s, cy - s * 0.5), (cx - s * 0.5, cy - s * 0.6),
               (cx, cy + s * 0.1), (cx + s * 0.5, cy - s * 0.2),
               (cx + s, cy + s * 0.55)]
        d.line(pts, fill=colour, width=6, joint="curve")
        d.polygon([(cx + s * 0.72, cy + s * 0.55), (cx + s, cy + s * 0.55),
                   (cx + s, cy + s * 0.28)], fill=colour)
        d.line([cx - s * 1.1, cy + s * 0.7, cx + s * 1.1, cy + s * 0.7],
               fill=GREY, width=3)
    elif kind == "plug":
        d.rounded_rectangle([cx - s * 0.28, cy - s * 0.75, cx + s * 0.28,
                             cy + s * 0.35], radius=8, fill=colour)
        d.line([cx - s * 0.18, cy - s * 1.05, cx - s * 0.18, cy - s * 0.7],
               fill=colour, width=7)
        d.line([cx + s * 0.18, cy - s * 1.05, cx + s * 0.18, cy - s * 0.7],
               fill=colour, width=7)
        d.line([cx, cy + s * 0.35, cx, cy + s * 0.85], fill=colour, width=7)
        d.arc([cx - s * 0.55, cy + s * 0.45, cx + s * 0.55, cy + s * 1.15],
              start=0, end=180, fill=GOLD, width=6)
    elif kind == "mine":
        d.rectangle([cx - s * 0.55, cy - s * 0.8, cx + s * 0.55, cy + s * 0.8],
                    outline=colour, width=6)
        d.line([cx - s * 0.55, cy, cx + s * 0.55, cy], fill=colour, width=4)
        d.line([cx, cy - s * 0.8, cx, cy + s * 0.8], fill=colour, width=4)
        d.ellipse([cx - s * 0.22, cy - s * 0.22, cx + s * 0.22, cy + s * 0.22],
                  fill=GOLD)

# ---- masthead --------------------------------------------------------------
def draw_masthead(d, y):
    d.rectangle([0, 0, W, y + 300], fill=NAVY)
    d.rectangle([0, y + 300, W, y + 308], fill=GOLD)
    f_title = font(SERIF_B, 118)
    f_sub = font(SANS_B, 46)
    f_meta = font(SANS, 34)
    d.text((MARGIN, y + 28), MASTHEAD_TITLE, font=f_title, fill=(255, 255, 255))
    d.text((MARGIN, y + 168), MASTHEAD_SUB, font=f_sub, fill=GOLD)
    d.text((MARGIN, y + 232), MASTHEAD_META, font=f_meta, fill=(205, 212, 226))
    # date badge, top right
    badge = "25 NOV\n2026"
    f_badge = font(SANS_B, 44)
    bx0 = W - MARGIN - 300
    d.rounded_rectangle([bx0, y + 40, bx0 + 300, y + 210], radius=18,
                        outline=GOLD, width=4)
    d.text((bx0 + 30, y + 62), "25 NOV", font=f_badge, fill=(255, 255, 255))
    d.text((bx0 + 30, y + 122), "2026", font=f_badge, fill=GOLD)
    return y + 308

# ---- featured cards --------------------------------------------------------
def featured_card_h(d, card, cw):
    f_head = font(SANS_B, 50)
    f_det = font(SANS, 33)
    _, _, head, det, _ = card
    hl = wrap(d, head, f_head, cw - 190)
    dl = wrap(d, det, f_det, cw - 56)
    return 78 + text_h(d, hl, f_head, 8) + 10 + text_h(d, dl, f_det, 6) + 40

def draw_featured(d, y, card, card_h, x, cw):
    tag, colour, head, det, icon = card
    d.rounded_rectangle([x, y, x + cw, y + card_h], radius=22,
                        fill=CARD, outline=RULE, width=2)
    d.rounded_rectangle([x, y, x + cw, y + 58], radius=22, fill=colour)
    d.rectangle([x, y + 30, x + cw, y + 58], fill=colour)
    f_tag = font(SANS_B, 32)
    d.text((x + 28, y + 12), tag, font=f_tag, fill=(255, 255, 255))
    # icon top-right of the card body
    draw_icon(d, icon, x + cw - 78, y + 150, 46, colour)
    f_head = font(SANS_B, 50)
    f_det = font(SANS, 33)
    hl = wrap(d, head, f_head, cw - 190)
    yy = y + 78
    for ln in hl:
        d.text((x + 28, yy), ln, font=f_head, fill=INK)
        yy += 58
    yy += 10
    dl = wrap(d, det, f_det, cw - 56)
    for ln in dl:
        d.text((x + 28, yy), ln, font=f_det, fill=(52, 56, 66))
        yy += 41
    return yy

# ---- timeline --------------------------------------------------------------
def draw_timeline(d, y):
    f_lab = font(SANS_B, 30)
    f_time = font(SANS_B, 40)
    f_ev = font(SANS, 30)
    d.text((MARGIN, y), "THE DAY IN UTC", font=f_lab, fill=GOLD)
    y += 48
    d.line([MARGIN, y + 26, W - MARGIN, y + 26], fill=RULE, width=4)
    n = len(TIMELINE)
    slot = CONTENT_W / n
    for i, (t, ev) in enumerate(TIMELINE):
        cx = MARGIN + slot * i + slot / 2
        d.ellipse([cx - 13, y + 13, cx + 13, y + 39], fill=GOLD,
                  outline=NAVY, width=3)
        tw = d.textlength(t, font=f_time)
        d.text((cx - tw / 2, y + 56), t, font=f_time, fill=NAVY)
        el = wrap(d, ev, f_ev, slot - 24)
        yy = y + 108
        for ln in el:
            lw = d.textlength(ln, font=f_ev)
            d.text((cx - lw / 2, yy), ln, font=f_ev, fill=(52, 56, 66))
            yy += 38
    return y + 108 + 76

# ---- region sections -------------------------------------------------------
ITEM_HEAD = 36
ITEM_DET = 29

def section_height(d, items, col_w):
    """Height of one region section in a column of width col_w.
    Mirrors draw_section's arithmetic exactly."""
    f_head = font(SANS_B, ITEM_HEAD)
    f_det = font(SANS, ITEM_DET)
    h = 62 + 14  # header + gap
    for head, det in items:
        hl = wrap(d, head, f_head, col_w - 8)
        dl = wrap(d, det, f_det, col_w - 8)
        h += len(hl) * (ITEM_HEAD + 4) + 4 + len(dl) * (ITEM_DET + 4) + 44
    return h

def draw_section(d, x, y, col_w, name, colour, items):
    f_reg = font(SANS_B, 40)
    d.rectangle([x, y, x + col_w, y + 62], fill=colour)
    d.text((x + 18, y + 10), name, font=f_reg, fill=(255, 255, 255))
    d.text((x + col_w - 18 - d.textlength(str(len(items)), font=f_reg),
            y + 10), str(len(items)), font=f_reg, fill=(255, 255, 255))
    y += 62 + 14
    f_head = font(SANS_B, ITEM_HEAD)
    f_det = font(SANS, ITEM_DET)
    for head, det in items:
        hl = wrap(d, head, f_head, col_w - 8)
        for ln in hl:
            d.text((x + 4, y), ln, font=f_head, fill=INK)
            y += ITEM_HEAD + 4
        y += 4
        dl = wrap(d, det, f_det, col_w - 8)
        for ln in dl:
            d.text((x + 4, y), ln, font=f_det, fill=(74, 78, 88))
            y += ITEM_DET + 4
        y += 22
        d.line([x, y, x + col_w, y], fill=(226, 222, 212), width=2)
        y += 22
    return y


# ---- render ----------------------------------------------------------------
def render():
    # column width for the region grid (3 columns)
    col_w = (CONTENT_W - 2 * COL_GAP) // 3

    # probe image for measurement (never saved)
    probe = Image.new("RGB", (W, 100), PAPER)
    pd = ImageDraw.Draw(probe)

    # featured: 2 rows x 3 cards
    fcw = (CONTENT_W - 2 * COL_GAP) // 3
    row1_h = max(featured_card_h(pd, c, fcw) for c in FEATURED[:3])
    row2_h = max(featured_card_h(pd, c, fcw) for c in FEATURED[3:])
    feat_h = row1_h + 36 + row2_h

    # balance the 10 region sections across 3 columns (greedy, deterministic)
    heights = [section_height(pd, items, col_w) for _, _, items in SECTIONS]
    cols = [[], [], []]
    col_h = [0, 0, 0]
    order = sorted(range(len(SECTIONS)), key=lambda i: -heights[i])
    for i in order:
        j = col_h.index(min(col_h))
        cols[j].append(i)
        col_h[j] += heights[i] + 40
    # keep each column in original section order
    cols = [sorted(c) for c in cols]
    grid_h = max(col_h) - 40

    mast_h = 308
    tl_h = 48 + 26 + 108 + 76 + 40  # label + line + times + events + gap
    foot_h = 120
    total_h = (mast_h + 44 + feat_h + 44 + tl_h + 20
               + grid_h + 48 + foot_h)

    img = Image.new("RGB", (W, total_h), PAPER)
    d = ImageDraw.Draw(img)

    y = draw_masthead(d, 0)
    y += 44
    # featured row 1
    for k, card in enumerate(FEATURED[:3]):
        x = MARGIN + k * (fcw + COL_GAP)
        draw_featured(d, y, card, row1_h, x, fcw)
    y += row1_h + 36
    # featured row 2
    for k, card in enumerate(FEATURED[3:]):
        x = MARGIN + k * (fcw + COL_GAP)
        draw_featured(d, y, card, row2_h, x, fcw)
    y += row2_h + 44
    # timeline
    y = draw_timeline(d, y)
    y += 20
    # region grid
    grid_top = y
    for ci, col in enumerate(cols):
        cx = MARGIN + ci * (col_w + COL_GAP)
        cy = grid_top
        for si in col:
            name, colour, items = SECTIONS[si]
            cy = draw_section(d, cx, cy, col_w, name, colour, items)
            cy += 40
    y = grid_top + grid_h + 48
    # footer
    d.rectangle([0, y, W, y + foot_h], fill=NAVY)
    f_foot = font(SANS, 28)
    fl = wrap(d, FOOTER, f_foot, CONTENT_W)
    yy = y + 22
    for ln in fl:
        d.text((MARGIN, yy), ln, font=f_foot, fill=(205, 212, 226))
        yy += 36
    return img

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "news-image-20261125-v2.png"
    img = render()
    img.save(out, format="PNG")
    with open(out, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    n_stories = len(FEATURED) + sum(len(it) for _, _, it in SECTIONS)
    print(f"saved {out}  {img.size[0]}x{img.size[1]}  "
          f"stories={n_stories} regions={len(SECTIONS)}  sha256={digest}")

if __name__ == "__main__":
    main()
