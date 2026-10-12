#!/usr/bin/env python3
"""Braum's run fix pack for Codex (assets/source/braum/RUN_FIX.md): the legs of his 8 run frames redrawn as a
crossing step.

    python tools/art/pack_braum_run.py [--out dist/braum_packs/braum_run_fix]

The user, 2026-10-12: 「布隆走路没交叉步？」 - in Codex's run (codex_strips) the same leg stays behind in all 8 frames and
the other in front: a hop, the legs never pass each other. Everything above the hip plates (the head, the body, the
arms) and the shield stay as they are (the user had passed the frames); only the legs are redrawn, phase by phase the
way of league_caitlyn's approved run (memory run-legs-caitlyn-way): the near and the far leg take turns in front and
pass each other under the body.
Writes <out>/ (and <out>.zip): RUN_FIX.md, now/braum_run_<k>.png (the frame as it is in game now, on the step-2 pack's
1536 x 1024 canvas, 6 px a square), guide/ (the same with the cut line, the ground line and the standing point),
design/ (the design, its palette), refs/caitlyn_run.png (the approved crossing run, 8x), refs/league_run.png (League's
run, a local render).
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import import_braum_strips as I  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "braum")
DOC = os.path.join(SRC, "RUN_FIX.md")
PX = 6
CUT = 112                       # the pack canvas row under the hip plates: the legs start below it
LEAGUE_RUN = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "br_work", "clips", "Braum_Run_02.png")


def up(a, k):
    return np.repeat(np.repeat(a, k, 0), k, 1)


def lines(img):
    dr = ImageDraw.Draw(img)
    for c in range(0, 257, 10):
        dr.line([(c * PX, 0), (c * PX, 1024)], fill=(200, 200, 200, 90))
    for r in range(0, 171, 10):
        dr.line([(0, r * PX), (1536, r * PX)], fill=(200, 200, 200, 90))
    dr.line([(0, CUT * PX), (1536, CUT * PX)], fill=(255, 160, 0, 255), width=2)
    dr.line([(0, (I.SOLE - I.PAD + 1) * PX), (1536, (I.SOLE - I.PAD + 1) * PX)], fill=(255, 40, 40, 255), width=2)
    cx, cy = (I.PIV_X + 0.5) * PX, (I.SOLE - I.PAD + 1) * PX
    dr.line([(cx - 18, cy), (cx + 18, cy)], fill=(40, 90, 255, 255), width=3)
    dr.line([(cx, cy - 18), (cx, cy + 18)], fill=(40, 90, 255, 255), width=3)
    return img


def caitlyn(path):
    import tfm2_ase as T
    from preview_garen import frames_of
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_caitlyn"))
    tiles = [f.crop(f.getchannel("A").getbbox()) for f, _ in frames_of(sp, "run")]
    Z = 8
    w = max(t.width for t in tiles)
    h = max(t.height for t in tiles)
    can = Image.new("RGBA", (w * Z * len(tiles), h * Z + 20), (96, 112, 96, 255))
    d = ImageDraw.Draw(can)
    for i, t in enumerate(tiles):
        can.alpha_composite(t.resize((t.width * Z, t.height * Z), Image.NEAREST), (i * w * Z, 20 + (h - t.height) * Z))
        d.text((i * w * Z + 4, 4), f"frame {i + 1}", fill=(255, 255, 255, 255))
    can.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "braum_packs", "braum_run_fix"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        for e in os.listdir(out):
            p = os.path.join(out, e)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for sub in ("now", "guide", "design", "refs"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for k in range(1, 9):
        f = np.asarray(Image.open(os.path.join(I.OUT, f"braum_run_{k}.png")).convert("RGBA"))[I.PAD:]
        can = np.zeros((1024 // PX + 1, 256, 4), np.uint8)
        can[:f.shape[0]] = f
        big = Image.fromarray(up(can, PX)).crop((0, 0, 1536, 1024))
        big.save(os.path.join(out, "now", f"braum_run_{k}.png"))
        g = Image.new("RGBA", big.size, (0, 0, 0, 0))
        g.alpha_composite(big)
        lines(g).save(os.path.join(out, "guide", f"braum_run_{k}.png"))
    d = np.asarray(Image.open(I.DESIGN).convert("RGBA"))
    Image.fromarray(up(d, PX)).save(os.path.join(out, "design", "braum_design.png"))
    cols = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    pal = np.zeros((1, len(cols), 4), np.uint8)
    pal[0, :, :3], pal[0, :, 3] = cols[np.argsort(cols.sum(1))], 255
    Image.fromarray(up(pal, 24)).save(os.path.join(out, "design", "braum_palette.png"))
    caitlyn(os.path.join(out, "refs", "caitlyn_run.png"))
    if os.path.isfile(LEAGUE_RUN):
        shutil.copyfile(LEAGUE_RUN, os.path.join(out, "refs", "league_run.png"))
    shutil.copyfile(DOC, os.path.join(out, "RUN_FIX.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
