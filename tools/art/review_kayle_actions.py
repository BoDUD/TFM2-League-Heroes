#!/usr/bin/env python3
"""Kayle's redo for the user's review (memory one-gif-review): every tag of his old 1x sheet
(assets/source/kayle/hd/old) beside the same tag of the sheet now (its hd_ frames, PPU 2.29), one game pixel the
same size on both sides, the two frames' pivots (the frame's middle) on one point, each frame shown for its own
duration - tools/art/review_taric_actions.py's.

    python tools/art/review_kayle_actions.py --out DIR [--z 4] [--tags run,attack]

Writes <out>/kayle_all_old_new.gif (every action tag in turn, each played twice) and <out>/kayle_<tag>_old_new.png
(the old frames over the new ones).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import casts_kayle_hd as CS  # noqa: E402
import casts_rengar_hd as CR  # noqa: E402

TAGS = ["idle_base", "run", "attack", "attack_melee", "skill", "skill2", "ult", "hit", "dead"]
NAMES = {"idle_base": "idle", "run": "flight", "attack": "ranged attack", "attack_melee": "melee attack",
         "skill": "Q Radiant Blast", "skill2": "E Starfire Spellblade", "ult": "R Divine Judgment", "hit": "hit",
         "dead": "death"}
STEM = os.path.join(ROOT, "league", "champions", "league_kayle")
BG = (96, 112, 96)


def sheet(png, fanim):
    px = np.asarray(Image.open(CR.lp(png)).convert("RGBA"))
    with open(CR.lp(fanim), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag, a in anims.items():
        out[tag] = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            out[tag].append((px[y:y + h, x:x + w].copy(), round(f_["duration"] * 1000)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=float, default=4, help="screen px a game pixel")
    ap.add_argument("--tags")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    old = sheet(os.path.join(CS.HD, "old", "sheet.png"), os.path.join(CS.HD, "old", "anim.fanim"))
    new = sheet(STEM + "#sheet.png", STEM + "#anim.fanim")
    ppu = CS.PPU
    tags = a.tags.split(",") if a.tags else TAGS
    W, H = 120 * a.z, 76 * a.z                                   # each side, in screen px
    W, H = int(W), int(H)
    cx, cy = W // 2, int(H * 0.56)                                # the pivot on screen
    gif, ms = [], []
    for tag in tags:
        pairs = list(zip(old[tag], new["hd_" + tag]))
        rows = []
        for (o, d), (n, _) in pairs:
            can = Image.new("RGB", (2 * W + 8, H), (40, 40, 40))
            for side, (img, k) in enumerate(((o, a.z), (n, a.z / ppu))):
                im = Image.fromarray(img).resize((max(1, round(img.shape[1] * k)), max(1, round(img.shape[0] * k))),
                                                 Image.NEAREST)
                tile = Image.new("RGBA", (W, H), BG + (255,))
                tile.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
                can.paste(tile.convert("RGB"), (side * (W + 8), 0))
            dr = ImageDraw.Draw(can)
            dr.text((6, 4), f"old 1x - {NAMES[tag]}", fill=(255, 255, 255))
            dr.text((W + 14, 4), f"new PPU {ppu:.3f} - {NAMES[tag]}", fill=(255, 255, 255))
            rows.append((can, d))
        for _ in range(2):
            for can, d in rows:
                gif.append(can)
                ms.append(max(d, 40))
        strip = Image.new("RGB", (2 * W + 8, len(rows) * (H + 4)), (40, 40, 40))
        for i, (can, _) in enumerate(rows):
            strip.paste(can, (0, i * (H + 4)))
        strip.save(os.path.join(a.out, f"kayle_{tag}_old_new.png"))
    gif[0].save(os.path.join(a.out, "kayle_all_old_new.gif"), save_all=True, append_images=gif[1:], duration=ms, loop=0)
    print("written", a.out, len(gif), "frames")


if __name__ == "__main__":
    main()
