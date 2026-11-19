#!/usr/bin/env python3
"""Compose the 18 November 2026 world-news front page (1024x1024).

Reads the six text-free panel illustrations from ../panels/ and lays them
out as a newspaper front page: a masthead naming the day, then a 2x3 grid
where every panel carries a bold PIL-rendered headline and one factual
sub-line. All type is drawn here with DejaVu, so no letter can garble.

Run from this directory:  python3 build/compose.py
Writes entry.png next to main.ts (the repository root).
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PANELS = os.path.join(os.path.dirname(ROOT), "panels")

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (248, 244, 232)
INK = (26, 26, 26)
RED = (176, 42, 32)
GREY = (90, 86, 78)

# (panel file, headline, sub-line) in reading order.
STORIES = [
    ("panel-kuwait", "IRAN HITS U.S. BASE IN KUWAIT",
     "Drones strike air defences at Ali Al Salem base"),
    ("panel-bridge", "UKRAINE HITS KERCH BRIDGE",
     "Road span collapses after a second day of strikes"),
    ("panel-summit", "TRUMP LANDS IN CHINA FOR 3-WAY SUMMIT",
     "First Trump\u2013Xi\u2013Putin meeting set for Thursday"),
    ("panel-cyclone", "CYCLONE AKVAN NEARS INDIA",
     "Severe storm strengthens; thousands move to shelters"),
    ("panel-cop31", "COP31 LAUNCHES CLIMATE STOCKTAKE",
     "Nations begin 5-year check on pledges in Antalya"),
    ("panel-crash", "19 KILLED IN SIBERIA PLANE CRASH",
     "Russian military transport plane crashes"),
]


def find_panel(stem):
    for name in sorted(os.listdir(PANELS)):
        if name.startswith("media-generation-" + stem) and name.endswith(".png"):
            return os.path.join(PANELS, name)
    raise FileNotFoundError(stem)


def wrap(draw, text, font, width):
    """Greedy word wrap; returns a list of lines that fit in width."""
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def crop_to(img, width, height, focus_y=0.5):
    """Centre-crop to the target aspect ratio, then resize.
    focus_y (0 top .. 1 bottom) picks which vertical band survives."""
    target = width / height
    w, h = img.size
    if w / h > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target)
        top = int((h - new_h) * focus_y)
        img = img.crop((0, top, w, top + new_h))
    return img.resize((width, height), Image.LANCZOS)


# Vertical focus per panel: keep the story's key band in the wide crop.
FOCUS = {"panel-kuwait": 0.72}


def main():
    page = Image.new("RGB", (1024, 1024), PAPER)
    draw = ImageDraw.Draw(page)

    # Thin outer frame.
    draw.rectangle([10, 10, 1013, 1013], outline=INK, width=3)

    # --- Masthead -------------------------------------------------------
    date_font = ImageFont.truetype(SERIF_BOLD, 62)
    draw.text((512, 44), "18 NOVEMBER 2026", font=date_font, fill=INK,
              anchor="ma")
    tag_font = ImageFont.truetype(SANS_BOLD, 27)
    draw.text((512, 118), "T H E   W O R L D   I N   O N E   D A Y",
              font=tag_font, fill=RED, anchor="ma")
    draw.line([(28, 158), (996, 158)], fill=INK, width=3)

    # --- Grid -----------------------------------------------------------
    head_font = ImageFont.truetype(SANS_BOLD, 25)
    sub_font = ImageFont.truetype(SANS, 17)
    num_font = ImageFont.truetype(SANS_BOLD, 22)
    col_w, gap_x, gap_y = 476, 16, 14
    img_h, top = 158, 174
    for i, (stem, headline, sub) in enumerate(STORIES):
        row, col = divmod(i, 2)
        x = 28 + col * (col_w + gap_x)
        y = top + row * (img_h + 88 + gap_y)
        img = crop_to(Image.open(find_panel(stem)).convert("RGB"),
                      col_w, img_h, FOCUS.get(stem, 0.5))
        page.paste(img, (x, y))
        draw.rectangle([x, y, x + col_w - 1, y + img_h - 1],
                       outline=INK, width=2)
        # Number badge over the image's top-left corner.
        cx, cy, r = x + 20, y + 20, 17
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        draw.text((cx, cy - 1), str(i + 1), font=num_font, fill=(255, 255, 255),
                  anchor="mm")
        # Headline (up to two lines) and one sub-line.
        ty = y + img_h + 8
        for line in wrap(draw, headline, head_font, col_w)[:2]:
            draw.text((x, ty), line, font=head_font, fill=INK)
            ty += 30
        draw.text((x, ty + 2), sub, font=sub_font, fill=GREY)

    # --- Footer ---------------------------------------------------------
    draw.line([(28, 966), (996, 966)], fill=INK, width=2)
    foot_font = ImageFont.truetype(SANS, 16)
    draw.text((512, 976),
              "All six stories happened or were first reported on 18 November 2026.",
              font=foot_font, fill=GREY, anchor="ma")

    out = os.path.join(ROOT, "entry.png")
    page.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
