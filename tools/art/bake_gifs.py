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
PANEL = (180, 120)
PIVOT = (90, 66)
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
    """Composite a frame centred on (x, y), clipped to the panel."""
    h, w = a.shape[:2]
    x0, y0 = int(x - w // 2), int(y - h // 2)
    cx0, cy0 = max(0, x0), max(0, y0)
    cx1, cy1 = min(can.shape[1], x0 + w), min(can.shape[0], y0 + h)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    part = Image.fromarray(np.ascontiguousarray(a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]))
    img = Image.fromarray(can)
    img.alpha_composite(part, (cx0, cy0))
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
    ap.add_argument("--repeat", type=int, default=1, help="plays of each action")
    args = ap.parse_args()
    with open(os.path.join(SRC, f"{args.hero}_bake.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    items = cfg["items"]
    hero_now = sheet_at(f"champions/league_{args.hero}", None)
    hero_was = sheet_at(f"champions/league_{args.hero}", args.base)
    fx_was = {}

    def fx_frames(it):
        name = it.get("fx", cfg["fx"])
        if name not in fx_was:
            fx_was[name] = sheet_at("effects/" + name, args.base)
        return timeline(fx_was[name], it["tag"])

    copies = {it["into"]: it for it in items if "from" in it}

    def origin(tag):
        """(the tag at --base it comes from, ms into it, [(ms into that tag, picture frames)])."""
        own = [it for it in items if it["into"] == tag]
        if tag in copies:
            c = copies[tag]
            base, start, pics = origin(c["from"])
            start += c["slice_ms"]
        else:
            base, start, pics = tag, 0, []
        return base, start, pics + [(start + it["at_ms"], fx_frames(it)) for it in own]

    def body_from(sp, tag, start, length):
        fr = timeline(sp, tag)
        total = sum(d for _, d in fr)
        out, t, end = [], 0, start + length
        while t < end and total:
            for a, d in fr:
                lo, hi = max(t, start), min(t + d, end)
                if hi > lo:
                    out.append((a, hi - lo))
                t += d
        return out

    frames = []
    for tag in dict.fromkeys(it["into"] for it in items):
        now = timeline(hero_now, tag)
        total = sum(d for _, d in now)
        base, start, pics = origin(tag)
        was = body_from(hero_was, base, start, total)
        pics = [(t0 - start, fr) for t0, fr in pics]
        for _ in range(args.repeat):
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
