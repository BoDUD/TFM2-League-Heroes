#!/usr/bin/env python3
"""The pack for Codex that goes with assets/source/red_side/PROMPTS.md: Ekko from the front.

    python tools/art/pack_red_side_figures.py --out <folder> [--zip]

The client never mirrors an effect picture (champion-data.md section 6), so a figure of the hero left on the ground
while he moves on - league_ekko's Chronobreak hologram (r_ghost, made from his idle drawing by import_ekko.py) - faces
right whichever way he went. Drawn from the front, it faces no way. (league_yone's E body is a front view already: it
only stood 4 squares right of its spot, fixed in yone_cells.json; league_shaco's R clone always stands left of the
champion it strikes, facing him, so either side is right.) Into <folder>:
  PROMPTS.md                         the prompts
  design/ekko_design.png             the approved design at 8x (assets/source/native/ekko_native.png)
  now/ekko_r_ghost.png               the hologram as it is in game, at 8x on a dark ground, and mirrored beside it:
                                     the blue side and what the red side should show
  size/ekko_canvas.png               the canvas to draw on, at 8x: the soles line (red), the middle column (cyan), the
                                     top of his hair in the side view (yellow), 8 x 8 grid
  refs/ekko_front_league_<yaw>.png   League's own model near the front (tools/lol/pose_ref.py --yaw -45 / -70,
                                     Idle01) - Riot's, in the pack only, never committed
"""
import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase  # noqa: E402

Z = 8
GROUND = (40, 42, 52, 255)
CANVAS = (56, 56)          # blocks
SOLES = 46                 # the soles' row on the canvas
CLIP = "PunkGenius_Idle01@0"
YAWS = ("-45", "-70")


def frames(stem, tag):
    sp = tfm2_ase.load_sprite(os.path.join(ROOT, "league", stem + "#sheet.png"))
    return [np.asarray(sp.frames[i]) for i in sp.tag_frames(tag)]


def big(a, z=Z):
    img = Image.fromarray(a)
    return img.resize((img.width * z, img.height * z), Image.NEAREST)


def now_picture(out):
    """The hologram's first frame, cropped round its pixels on the pivot column, and its mirror."""
    f = frames("effects/league_ekko_big", "r_ghost")[0]
    al = f[..., 3]
    ys, xs = np.nonzero(al)
    cx = al.shape[1] // 2
    hw = max(cx - xs.min(), xs.max() - cx) + 3
    crop = f[max(0, ys.min() - 3):ys.max() + 4, cx - hw:cx + hw + 1]
    a, b = big(crop), big(crop[:, ::-1].copy())
    can = Image.new("RGBA", (a.width * 2 + 4 * Z, a.height), GROUND)
    can.alpha_composite(a, (0, 0))
    can.alpha_composite(b, (a.width + 4 * Z, 0))
    can.save(out)


def canvas(out):
    """The 8x canvas with the soles line, the middle column and the hair line of his side view; returns the rows."""
    side = frames("champions/league_ekko", "idle")[0]
    ys, _ = np.nonzero(side[..., 3])
    rows = ys.max() - ys.min() + 1
    w, h = CANVAS
    img = Image.new("RGBA", (w * Z, h * Z), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(0, w * Z + 1, Z):
        d.line([(x, 0), (x, h * Z)], fill=(255, 255, 255, 28))
    for y in range(0, h * Z + 1, Z):
        d.line([(0, y), (w * Z, y)], fill=(255, 255, 255, 28))
    mid = (w // 2) * Z + Z // 2
    d.line([(mid, 0), (mid, h * Z)], fill=(60, 220, 255, 200), width=2)
    d.line([(0, (SOLES + 1) * Z), (w * Z, (SOLES + 1) * Z)], fill=(255, 60, 60, 255), width=3)
    top = SOLES - rows + 1
    d.line([(0, top * Z), (w * Z, top * Z)], fill=(255, 220, 60, 220), width=2)
    img.save(out)
    return rows, top


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    args = ap.parse_args()
    out = args.out
    for sub in ("design", "now", "size", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets", "source", "red_side", "PROMPTS.md"), os.path.join(out, "PROMPTS.md"))
    shutil.copy(os.path.join(ROOT, "assets", "source", "native", "ekko_native.png"),
                os.path.join(out, "design", "ekko_design.png"))
    now_picture(os.path.join(out, "now", "ekko_r_ghost.png"))
    rows, top = canvas(os.path.join(out, "size", "ekko_canvas.png"))
    print(f"ekko: {rows} rows tall in the side view; canvas {CANVAS[0]} x {CANVAS[1]}, hair line row {top}, "
          f"soles row {SOLES}, middle column {CANVAS[0] // 2}")
    for yaw in YAWS:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", args.lol,
                            "--champ", "Ekko", "--hq", "--size", "480", "--no-labels", "--yaw", yaw,
                            "--name", f"ekko_front_league_{yaw.lstrip('-')}", "--out", os.path.join(out, "refs"),
                            "--frame", CLIP], capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.returncode == 0 else "League render failed: " + r.stderr)
    if args.zip:
        print("zip:", shutil.make_archive(out.rstrip("/\\"), "zip", out))


if __name__ == "__main__":
    main()
