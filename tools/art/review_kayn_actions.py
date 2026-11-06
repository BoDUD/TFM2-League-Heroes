#!/usr/bin/env python3
"""Kayn's redo for the user's review (memory one-gif-review): every action tag of his old 1x sheet
(assets/source/kayn/hd/old) in his three forms beside the same tag of the sheet now (its hd_ frames, PPU 1.80), one game
pixel the same size on both sides, the two frames' pivots (the frame's middle) on one point, each frame shown for its
own duration - tools/art/review_khazix_actions.py's, for the base Kayn, the Darkin (rh_) and the Shadow Assassin (sh_);
the in-wall shadows (w_ / rw_ / hw_) too.

    python tools/art/review_kayn_actions.py --out DIR [--z 4] [--tags run,rh_run]

Writes <out>/kayn_all_old_new.gif (every tag in turn, each played twice), <out>/kayn_<form>_old_new.gif (one form's)
and <out>/kayn_<tag>_old_new.png (the old frames over the new ones).
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
import casts_rengar_hd as CR  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "kayn", "hd")
PPU = 72 / 40
ACTS = ["idle_base", "run", "attack", "skill", "skill2", "skill2_fx1", "ult", "ult_fx1", "ult_exit", "transform", "hit",
        "dead"]
FORMS = {"": "base", "rh_": "darkin", "sh_": "shadow"}
TAGS = [p + t for p in FORMS for t in ACTS] + [w + t for w in ("w_", "rw_", "hw_") for t in ("run", "skill")]
NAMES = {"idle_base": "idle", "run": "run", "attack": "attack", "skill": "Q Reaping Slash", "skill2": "W Blade's Reach",
         "skill2_fx1": "W (wind)", "ult": "R dive", "ult_fx1": "R dive (fx)", "ult_exit": "R exit",
         "transform": "transform", "hit": "hit", "dead": "death"}
FORM_NAME = {"": "Kayn", "rh_": "Darkin", "sh_": "Shadow", "w_": "in wall", "rw_": "Darkin in wall",
             "hw_": "Shadow in wall"}
STEM = os.path.join(ROOT, "league", "champions", "league_kayn")
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


def label(tag):
    for p in ("rw_", "hw_", "rh_", "sh_", "w_"):
        if tag.startswith(p):
            return f"{FORM_NAME[p]} - {NAMES.get(tag[len(p):], tag[len(p):])}"
    return f"Kayn - {NAMES.get(tag, tag)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--z", type=float, default=4, help="screen px a game pixel")
    ap.add_argument("--tags")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    old = sheet(os.path.join(HD, "old", "sheet.png"), os.path.join(HD, "old", "anim.fanim"))
    new = sheet(STEM + "#sheet.png", STEM + "#anim.fanim")
    tags = a.tags.split(",") if a.tags else TAGS
    W, H = int(130 * a.z), int(100 * a.z)                         # each side, in screen px
    cx, cy = W // 2, int(H * 0.6)                                 # the pivot on screen
    gif, per_form = [], {p: [] for p in FORMS}
    for tag in tags:
        pairs = list(zip(old[tag], new["hd_" + tag]))
        if len(old[tag]) != len(new["hd_" + tag]):
            sys.exit(f"{tag}: {len(old[tag])} old frames, {len(new['hd_' + tag])} new")
        rows = []
        for (o, d), (n, _) in pairs:
            can = Image.new("RGB", (2 * W + 8, H), (40, 40, 40))
            for side, (img, k) in enumerate(((o, a.z), (n, a.z / PPU))):
                im = Image.fromarray(img).resize((max(1, round(img.shape[1] * k)), max(1, round(img.shape[0] * k))),
                                                 Image.NEAREST)
                tile = Image.new("RGBA", (W, H), BG + (255,))
                tile.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
                can.paste(tile.convert("RGB"), (side * (W + 8), 0))
            dr = ImageDraw.Draw(can)
            dr.text((6, 4), f"old 1x - {label(tag)}", fill=(255, 255, 255))
            dr.text((W + 14, 4), f"new PPU {PPU:.2f} - {label(tag)}", fill=(255, 255, 255))
            rows.append((can, d))
        frm = "rh_" if tag.startswith(("rh_", "rw_")) else "sh_" if tag.startswith(("sh_", "hw_")) else ""
        for _ in range(2):
            for can, d in rows:
                gif.append((can, max(d, 40)))
                per_form[frm].append((can, max(d, 40)))
        strip = Image.new("RGB", (2 * W + 8, len(rows) * (H + 4)), (40, 40, 40))
        for i, (can, _) in enumerate(rows):
            strip.paste(can, (0, i * (H + 4)))
        strip.save(os.path.join(a.out, f"kayn_{tag}_old_new.png"))
    for name, fr in [("all", gif)] + [(FORMS[p], v) for p, v in per_form.items()]:
        if fr:
            fr[0][0].save(os.path.join(a.out, f"kayn_{name}_old_new.gif"), save_all=True,
                          append_images=[c for c, _ in fr[1:]], duration=[d for _, d in fr], loop=0)
    print("written", a.out, len(gif), "frames")


if __name__ == "__main__":
    main()
