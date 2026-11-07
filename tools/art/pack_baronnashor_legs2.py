#!/usr/bin/env python3
"""Baron Nashor's spider legs, step 2: Codex puts the chosen L6 legs on every pose and run frame.

2026-11-07: the user picked L6 (three legs a side) from step 1 (tools/art/pack_baronnashor_legs.py, delivered in
assets/source/baronnashor/codex_legs). Step 2 hands Codex its own earlier drawings - the poses (codex_poses) and the
run (codex_run), 1254 x 1254 at 9 px a square - and asks for the same pictures with the two hind legs and the ivory
feet replaced by L6's legs, everything else kept; then design_baronnashor_poses.py reads them back as before.

    python tools/art/pack_baronnashor_legs2.py [--out <folder>]

Writes <out>/baronnashor_legs2_pack.zip with assets/source/baronnashor/LEGS2_PROMPT.md and:
  design/L6_9px.png       the chosen idle (L6) read on its 11 px grid and drawn at 9 px a square on the 1254 canvas,
                          its leg tips on y = SOLE: the legs to copy, at the poses' square size
  design/L6_11px.png      the L6 picture as Codex delivered it
  refs/reference_baron.png the user's TFT screenshot cut-out (from step 1's pack)
  style/skarner_run.png   league_skarner's run, 8x: thin legs in a walk cycle (style only)
  poses/NN_<pose>.png     Codex's pose drawings to edit (e_dig has no legs and is left out)
  guides/NN_<pose>.png    the same with its ground line in grey (the lowest row its feet reach now)
  run/runK.png, guides/runK.png  the eight run frames (codex_run) and their ground lines
"""
import argparse
import io
import json
import os
import zipfile

from PIL import Image, ImageDraw

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(REPO, "assets", "source", "baronnashor")
CANVAS = 1254
PX = 9
SOLE = 1176              # pack_baronnashor_poses.py's SOLE_Y: where the poses' feet stand
GREY = (60, 60, 70, 255)
L6 = os.path.join(SRC, "codex_legs", "baronnashor-legs", "baronnashor-legs-L6.png")
POSES = ["a_rear", "a_bite", "q_breath", "e_dive", "e_rise", "r_rear", "r_slam", "r_spit", "d_fall", "d_down"]


def png(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


def read_grid(path, px):
    """A picture drawn on a `px` grid from its top-left corner, one pixel a square (the square's centre)."""
    im = Image.open(path).convert("RGBA")
    w, h = im.size[0] // px, im.size[1] // px
    out = Image.new("RGBA", (w, h))
    src, dst = im.load(), out.load()
    for y in range(h):
        for x in range(w):
            p = src[x * px + px // 2, y * px + px // 2]
            dst[x, y] = p if p[3] >= 128 else (0, 0, 0, 0)
    return out.crop(out.getchannel("A").getbbox())


def ground_of(img):
    """The lowest opaque row (the feet now)."""
    a = img.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    return a.getbbox()[3]


def guide(img, y):
    g = img.copy()
    ImageDraw.Draw(g).rectangle((0, y, CANVAS, y + 2), fill=(150, 150, 150, 255))
    return g


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="D:/TFM2-Workshop/baronnashor_packs")
    a = ap.parse_args()

    l6 = read_grid(L6, 11)
    l6_9 = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    big = l6.resize((l6.width * PX, l6.height * PX), Image.NEAREST)
    left = (CANVAS - big.width) // 2 // PX * PX
    l6_9.alpha_composite(big, (left, SOLE - big.height))

    files = {"design/L6_9px.png": png(l6_9), "design/L6_11px.png": open(L6, "rb").read()}
    step1 = os.path.join(a.out, "baronnashor_legs_pack.zip")
    with zipfile.ZipFile(step1) as z:
        files["refs/reference_baron.png"] = z.read("refs/2_reference_baron.png")
        files["style/skarner_run.png"] = z.read("style/5_style_skarner_run.png")
    grounds = {}
    for k, name in enumerate(POSES, 1):
        img = Image.open(os.path.join(SRC, "codex_poses", "baronnashor-poses", f"baronnashor-pose-{name}.png"))
        img = img.convert("RGBA")
        y = ground_of(img)
        grounds[name] = y
        files[f"poses/{k:02d}_{name}.png"] = png(img)
        files[f"guides/{k:02d}_{name}.png"] = png(guide(img, y))
    for k in range(1, 9):
        img = Image.open(os.path.join(SRC, "codex_run", "baronnashor-run", f"baronnashor-run-run{k}.png")).convert("RGBA")
        y = ground_of(img)
        grounds[f"run{k}"] = y
        files[f"run/run{k}.png"] = png(img)
        files[f"guides/run{k}.png"] = png(guide(img, y))
    files["grounds.json"] = json.dumps(grounds, indent=1).encode()
    files["LEGS2_PROMPT.md"] = open(os.path.join(SRC, "LEGS2_PROMPT.md"), "rb").read()
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "baronnashor_legs2_pack.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    print(path, f"{len(files)} files; L6 {l6.size} squares, at x {left} on the 9 px canvas; grounds {grounds}")


if __name__ == "__main__":
    main()
