#!/usr/bin/env python3
"""Corki's step-1 pack for Codex (assets/source/corki/MODEL_PROMPTS.md): the design drawn ON THE GAME GRID.

    python tools/art/pack_corki_model.py --out dist/corki_packs/corki_model_pack [--lol D:/WeGameApps/lol]

The user picked picture 2 (assets/source/corki/user_picture/corki-picture-2.png, 2026-10-12: the 3/4 front hover, the
saw-toothed lower wing). The design is drawn at game size on a fixed 26-px grid (Gwen's geometry turned to a LANDSCAPE
1536 x 1024 canvas = 59 x 39 squares, since the craft is wider than tall: art-spec "A design drawn at game size" and
"A muddy design"), in TWO views from the start - the 3/4 front for the idle and the ban/pick card, and SIDE-ON facing
right for every action (memory side-view-design), the pilot's head the same 3/4 face in both (one-face-all-frames).
Layout: the propellers' top on row TOP, the bombs' bottom on row BOT (30 rows), rows below BOT empty down to the ground
row GROUND (he hovers; the shadow is added at import), the hull's middle on column MID, at most WIDE squares wide.
  1_guide_grid.png       picture 2 brought straight down to the layout (blurry, at 26 px a square with a yellow
                         measuring grid and the rows marked): the size, the pose and the place only
  2_picture.png          picture 2 on light grey: the look
  3_league_head.png      League's in-game model, the pilot's head (local render, Riot's model: never committed)
  4_example_picture.png  Gwen's on-grid delivery (Codex, approved) at 26 px a square: the way of working
  5_example_sprite.png   the same at 1x enlarged 8x
  6_quality_bar.png      heroes the user approved, 8x on one feet line
  7_parts.png            picture 2's pilot and the nose with the gatling gun, enlarged
  8_league_side.png      League's model turned to the side, facing right (idle and two run frames; local render)
  9_empty_grid.png       the same grid empty, with the rows and the middle column marked: the canvas for the side view
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
SRC = os.path.join(ROOT, "assets", "source", "corki")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
PICTURE = os.path.join(SRC, "user_picture", "corki-picture-2.png")
SQ = 26                          # Codex's square
COLS, ROWS = 59, 39              # 1534 x 1014 inside the 1536 x 1024 canvas
TOP, BOT, GROUND = 5, 34, 37     # propellers' top row 5, bombs' bottom row 34 (30 rows), the ground under row 37
MID = 29                         # the hull's middle column
WIDE = 40                        # at most this many squares wide
# picture 2: the propellers' top y 46, the bombs' bottom y 978, the middle of the figure x 760
P_TOP, P_BOT, P_MID = 46, 978, 760
PILOT_BOX = (640, 190, 1150, 520)
NOSE_BOX = (640, 470, 1360, 940)


def hard(im):
    a = np.array(im.convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] > 200, 255, 0)
    a[a[..., 3] == 0] = 0
    return Image.fromarray(a)


def guide(pic):
    """The picture straight down to the layout: every square the picture's average where it covers half of it."""
    k = (BOT + 1 - TOP) / (P_BOT - P_TOP)
    x0, y0 = P_MID - (MID + 0.5) / k, P_TOP - TOP / k
    box = (round(x0), round(y0), round(x0 + COLS / k), round(y0 + ROWS / k))
    a = np.asarray(pic.crop(box)).astype(float) / 255
    pre = a[..., :3] * a[..., 3:4]
    ch = [np.asarray(Image.fromarray((pre[..., i] * 255).astype(np.uint8)).resize((COLS, ROWS), Image.BOX)) / 255
          for i in range(3)]
    cov = np.asarray(Image.fromarray((a[..., 3] * 255).astype(np.uint8)).resize((COLS, ROWS), Image.BOX)) / 255
    rgb = np.dstack(ch) / np.maximum(cov[..., None], 1e-6)
    out = np.zeros((ROWS, COLS, 4), np.uint8)
    out[..., :3] = (rgb.clip(0, 1) * 255).astype(np.uint8)
    out[..., 3] = np.where(cov > 0.5, 255, 0)
    return out


def big(can):
    img = Image.new("RGBA", (1536, 1024), (255, 255, 255, 255))
    img.alpha_composite(Image.fromarray(can).resize((COLS * SQ, ROWS * SQ), Image.NEAREST))
    d = ImageDraw.Draw(img)
    for c in range(COLS + 1):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(ROWS + 1):
        d.line([(0, r * SQ), (COLS * SQ, r * SQ)], fill=(240, 200, 0, 255), width=1)
    for r in range(0, ROWS, 5):
        d.text((2, r * SQ + 6), str(r), fill=(200, 0, 0, 255))
    for c in range(0, COLS, 5):
        d.text((c * SQ + 6, 2), str(c), fill=(0, 0, 200, 255))
    d.line([(0, TOP * SQ), (COLS * SQ, TOP * SQ)], fill=(30, 170, 60, 255), width=3)
    d.line([(0, (BOT + 1) * SQ), (COLS * SQ, (BOT + 1) * SQ)], fill=(230, 30, 30, 255), width=3)
    d.line([(0, (GROUND + 1) * SQ), (COLS * SQ, (GROUND + 1) * SQ)], fill=(120, 80, 40, 255), width=3)
    d.line([((MID + 0.5) * SQ, 0), ((MID + 0.5) * SQ, ROWS * SQ)], fill=(40, 90, 230, 255), width=3)
    for c in (MID - WIDE // 2, MID + WIDE // 2 + 1):
        d.line([(c * SQ, 0), (c * SQ, ROWS * SQ)], fill=(170, 60, 200, 255), width=2)
    return img


def on_grey(im, k=1):
    bg = Image.new("RGBA", im.size, (225, 225, 225, 255))
    bg.alpha_composite(im)
    return bg.resize((im.width * k, im.height * k), Image.NEAREST)


def hero(n):
    im = Image.open(os.path.join(NATIVE, f"{n}_native.png")).convert("RGBA")
    if im.width == 1024:
        im = im.resize((128, 128), Image.NEAREST)
    return im.crop(im.getbbox())


def quality_bar():
    shots = [hero(n) for n in ("gwen", "zeri", "xerath", "viktor", "kennen", "twitch")]
    z, pad = 8, 24
    tall = max(s.height for s in shots) * z
    img = Image.new("RGBA", (sum(s.width * z + pad for s in shots) + pad, tall + 2 * pad), (255, 255, 255, 255))
    x = pad
    for s in shots:
        img.alpha_composite(s.resize((s.width * z, s.height * z), Image.NEAREST), (x, pad + tall - s.height * z))
        x += s.width * z + pad
    return img


def parts(pic):
    tiles = [on_grey(pic.crop(PILOT_BOX), 2), on_grey(pic.crop(NOSE_BOX), 1)]
    img = Image.new("RGBA", (sum(t.width for t in tiles) + 40, max(t.height for t in tiles)), (255, 255, 255, 255))
    x = 0
    for t in tiles:
        img.alpha_composite(t, (x, 0))
        x += t.width + 40
    return img


def league(lol, out, name, frames, yaw, size, crop=None):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Corki", "--hq",
           "--bg", "225,225,225", "--no-labels", "--size", str(size), "--fit", "0.62", "--ground", "0.92", "--width",
           "1.4" if len(frames) > 1 else "1.3", "--yaw", str(yaw), "--mirror", "--name", name, "--out", out]
    for f in frames:
        cmd += ["--frame", f]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    if crop:
        im = Image.open(path)
        w, h = im.size
        im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out = os.path.join(a.out, "corki")
    os.makedirs(out, exist_ok=True)
    pic = hard(Image.open(PICTURE))
    g = guide(pic)
    big(g).convert("RGB").save(os.path.join(out, "1_guide_grid.png"))
    box = pic.getbbox()
    on_grey(pic.crop((box[0] - 30, box[1] - 30, box[2] + 30, box[3] + 30))).convert("RGB").save(
        os.path.join(out, "2_picture.png"))
    league(a.lol, out, "3_league_head", ["corki_idle1@0"], 15, 2400, (0.36, 0.2, 0.68, 0.52))
    shutil.copyfile(os.path.join(ROOT, "assets", "source", "gwen", "codex_grid", "gwen-grid-A.png"),
                    os.path.join(out, "4_example_picture.png"))
    gw = Image.open(os.path.join(ROOT, "assets", "source", "gwen", "codex_grid", "gwen-grid-A_1x.png")).convert("RGBA")
    gw = gw.crop(gw.getbbox())
    gw.resize((gw.width * 8, gw.height * 8), Image.NEAREST).save(os.path.join(out, "5_example_sprite.png"))
    quality_bar().convert("RGB").save(os.path.join(out, "6_quality_bar.png"))
    parts(pic).convert("RGB").save(os.path.join(out, "7_parts.png"))
    league(a.lol, out, "8_league_side", ["corki_idle1@0", "corki_run@0", "corki_run@500"], 80, 800)
    big(np.zeros_like(g)).convert("RGB").save(os.path.join(out, "9_empty_grid.png"))
    Image.fromarray(g).save(os.path.join(out, "guide_1x.png"))
    shutil.copyfile(os.path.join(SRC, "MODEL_PROMPTS.md"), os.path.join(a.out, "MODEL_PROMPTS.md"))
    ys, xs = np.nonzero(g[..., 3])
    print(f"guide: rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()} ({xs.max() - xs.min() + 1} wide)")
    print("written", shutil.make_archive(a.out, "zip", a.out))


if __name__ == "__main__":
    main()
