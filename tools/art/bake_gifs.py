#!/usr/bin/env python3
"""Before / after GIFs of the caster pictures baked into a hero's frames (assets/source/native/<hero>_bake.json).

    python tools/art/bake_gifs.py --hero jhin [--base origin/main]      # docs/preview/red_side/<hero>_bake.gif

The client never mirrors a data effect picture (ViewEffect, CasterViewEffect) but mirrors the hero's own frames with
his facing (champion-data.md section 6). Each action that carries a baked picture plays in three panels: the blue side
now (facing right), the red side before (the hero at --base mirrored, the effect picture drawn as it is: pointing
right, behind him) and the red side now (the baked frames mirrored). Put together from the sheets, not recorded in game.
"""
import argparse
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase  # noqa: E402

OUT = os.path.join(ROOT, "docs", "preview", "red_side")
SRC = os.path.join(ROOT, "assets", "source", "native")
STEP = 1000 / 30                                  # ms a GIF frame
PANEL = (150, 110)
PIVOT = (75, 60)
Z = 3
ARENA = (92, 104, 88)
FONT = "C:/Windows/Fonts/msyh.ttc"


def sheet_at(stem, ref):
    """Sprite of league/<stem> in the working tree (ref None) or at a git ref."""
    if ref is None:
        return tfm2_ase.load_sprite(os.path.join(ROOT, "league", stem + "#sheet.png"))
    png = subprocess.run(["git", "show", f"{ref}:league/{stem}#sheet.png"], cwd=ROOT, capture_output=True,
                         check=True).stdout
    fan = subprocess.run(["git", "show", f"{ref}:league/{stem}#anim.fanim"], cwd=ROOT, capture_output=True,
                         check=True).stdout
    return tfm2_ase.read_sheet(png, json.loads(fan.decode("utf-8-sig")))


def timeline(sp, tag):
    return [(np.asarray(sp.frames[i]), sp.durations[i]) for i in sp.tag_frames(tag)]


def at(frames, ms):
    t = 0
    for a, d in frames:
        if t <= ms < t + d:
            return a
        t += d
    return None


def paste(can, a, x, y):
    h, w = a.shape[:2]
    x0, y0 = int(x - w // 2), int(y - h // 2)
    img = Image.fromarray(can)
    img.alpha_composite(Image.fromarray(a), (x0, y0)) if x0 >= 0 and y0 >= 0 else None
    can[...] = np.asarray(img)


def panel(body, pics, ms, mirror):
    can = np.zeros((PANEL[1], PANEL[0], 4), np.uint8)
    can[...] = ARENA + (255,)
    b = at(body, ms)
    if b is not None:
        paste(can, b[:, ::-1] if mirror else b, *PIVOT)
    for t0, fr in pics:
        a = at(fr, ms - t0)
        if a is not None:
            paste(can, a, *PIVOT)                 # a data picture: never mirrored
    return can


def label(img, text, x):
    try:
        font = ImageFont.truetype(FONT, 22)
    except OSError:
        font = ImageFont.load_default()
    ImageDraw.Draw(img).text((x, 4), text, fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--base", default="origin/main")
    args = ap.parse_args()
    with open(os.path.join(SRC, f"{args.hero}_bake.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    hero_now = sheet_at(f"champions/league_{args.hero}", None)
    hero_was = sheet_at(f"champions/league_{args.hero}", args.base)
    fx_was = sheet_at("effects/" + cfg["fx"], args.base)
    frames = []
    for into in dict.fromkeys(e["into"] for e in cfg["items"]):
        now = timeline(hero_now, into)
        was = timeline(hero_was, into)
        pics = [(e["at_ms"], timeline(fx_was, e["tag"])) for e in cfg["items"] if e["into"] == into]
        total = sum(d for _, d in now)
        for _ in range(2):                        # each action twice, then a short pause
            ms = 0.0
            while ms < total + 150:
                row = [panel(now, [], ms, False), panel(was, pics, ms, True), panel(now, [], ms, True)]
                frames.append(np.concatenate([np.pad(p, ((0, 0), (0, 2), (0, 0))) for p in row], 1))
                ms += STEP
    os.makedirs(OUT, exist_ok=True)
    imgs = []
    for f in frames:
        img = Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST).convert("RGB")
        for k, text in enumerate(["蓝色方", "红色方 修复前", "红色方 修复后"]):
            label(img, text, k * (PANEL[0] + 2) * Z + 8)
        imgs.append(img)
    out = os.path.join(OUT, f"{args.hero}_bake.gif")
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=int(STEP), loop=0, optimize=True)
    print(f"{os.path.relpath(out, ROOT)}: {len(imgs)} frames, {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
