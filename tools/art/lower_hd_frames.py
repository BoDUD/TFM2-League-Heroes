#!/usr/bin/env python3
"""A dense hero's battlefield frames drawn lower, for a SIZES row (hd.rs) when its frames are not made by ppu_restyle.py.

    python tools/art/lower_hd_frames.py tft/champions/tft_gromp --rows 7 [--check]

The game draws a frame about its centre, so a hero shown smaller (SIZES) shrinks toward the middle of its frame and its
soles leave the ground; ppu_restyle.py's lift_sq moves the frames down when it writes them. A hero whose sheet comes from
its own rig (tft_gromp: rig_gromp.py, then hero_reels.py) gets the same here: every battlefield hd_ frame (not hd_bp /
hd_idle_base, the BP card's) loses `rows` empty rows at its bottom - its centre goes rows / 2 up, the picture rows / 2
lower about it; no pixel changes. Rows for size s and soles c dense rows under the centre: 2 x c x (1 / s - 1).
Refuses a frame with fewer empty rows at its bottom. Run once: a second run lowers them again.
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image

# the BP card's frames (tools/art/hero_reels.py): drawn by the UI at its own size, so they stay
UI_TAGS = ("hd_bp", "hd_idle_base")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", help="the sheet's path without #anim.fanim / #sheet.png")
    ap.add_argument("--rows", type=int, required=True)
    ap.add_argument("--check", action="store_true", help="only say what would change")
    a = ap.parse_args()
    anim_path = f"{a.base}#anim.fanim"
    with open(anim_path, encoding="utf-8") as f:
        text = f.read()
    doc = json.loads(text)
    sheet = np.asarray(Image.open(f"{a.base}#sheet.png").convert("RGBA"))
    n = 0
    for tag, anim in doc["anims"].items():
        if not tag.startswith("hd_") or tag in UI_TAGS:
            continue
        for i, fr in enumerate(anim["frames"]):
            r = fr["data"]
            x, y, w, h = (int(r[k]) for k in ("x", "y", "w", "h"))
            used = np.nonzero(sheet[y:y + h, x:x + w, 3].any(1))[0]
            empty = h - 1 - used.max() if len(used) else h
            if empty < a.rows:
                sys.exit(f"{tag}[{i}]: {empty} empty rows at its bottom, fewer than {a.rows}")
            r["h"] = float(h - a.rows)
            n += 1
    print(f"{anim_path}: {n} battlefield frames {a.rows} rows shorter at the bottom (drawn {a.rows / 2} rows lower)")
    if not a.check:
        with open(anim_path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
