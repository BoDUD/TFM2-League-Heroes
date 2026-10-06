#!/usr/bin/env python3
"""Samira's step 1b pack for Codex: the approved design (the skin) re-posed in oppi's idle stance (the skeleton).

    python tools/art/pack_samira_pose.py --out <folder>

The user, 2026-10-06, with oppi's Samira idle attached: 「站立的姿势换一换 模型已经可以了」 - the design
(assets/source/native/samira_native.png, tools/art/design_samira.py) stays square for square in the head and the costume;
only the stance changes: feet wider apart, both pistols drawn and held low at her sides pointing out, the greatsword
across her back as now. Writes into <out>:
  1_design.png / _1x.png   the approved design at 8x (1024x1024) and at 1x (128x128)
  2_pose.png               oppi's Samira idle, first frame, at 8x on a 1024x1024 canvas, its soles on row 99 and the middle
                           of its feet on column 64 (League of Legends Reborn, Steam Workshop 3774304166: a pose
                           reference in the pack only, never committed)
  3_guide.png              the canvas: the feet line (red, row 99), the middle column (blue, 64), the hair's top (green,
                           row 60) and the head box to paste (orange)
  4_head.png / _1x.png     the head to paste into the new pose, as it is in the design
  5_palette.png            the design's colours
  MODEL_POSE.md            the prompts (also assets/source/samira/MODEL_POSE.md)
then <out>.zip.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import tfm2_ase  # noqa: E402

DESIGN = os.path.join(ROOT, "assets", "source", "native", "samira_native.png")
DOC = os.path.join(ROOT, "assets", "source", "samira", "MODEL_POSE.md")
OPPI = r"D:\steam\steamapps\workshop\content\3009300\3774304166\champions\cf_samira"
Z, SOLE, MID = 8, 99, 64
HEAD_BOXES = [(60, 64, 57, 77), (65, 73, 57, 75), (74, 74, 59, 71)]   # rows r0..r1, columns c0..c1 (inclusive)


def up(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    des = np.array(Image.open(DESIGN).convert("RGBA"))
    up(des).save(os.path.join(a.out, "1_design.png"))
    Image.fromarray(des).save(os.path.join(a.out, "1_design_1x.png"))

    sp = tfm2_ase.load_sprite(OPPI)
    fr = np.array(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    fr[fr[..., 3] < 128] = 0
    ys, xs = np.nonzero(fr[..., 3])
    fig = fr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    feet = np.nonzero(fig[-3:, :, 3].any(0))[0]
    can = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE + 1 - fig.shape[0], int(round(MID - (feet.min() + feet.max()) / 2))
    can[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    pose = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    pose.alpha_composite(up(can))
    pose.convert("RGB").save(os.path.join(a.out, "2_pose.png"))

    op = des[..., 3] > 0
    head = np.zeros(op.shape, bool)
    for r0, r1, c0, c1 in HEAD_BOXES:
        head[r0:r1 + 1, c0:c1 + 1] = op[r0:r1 + 1, c0:c1 + 1]
    hpart = np.where(head[..., None], des, 0).astype(np.uint8)
    up(hpart).save(os.path.join(a.out, "4_head.png"))
    Image.fromarray(hpart).save(os.path.join(a.out, "4_head_1x.png"))

    g = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    g.alpha_composite(up(np.where(op[..., None], np.array([170, 170, 170, 255], np.uint8), 0).astype(np.uint8)))
    d = ImageDraw.Draw(g)
    d.line([(0, (SOLE + 1) * Z), (1023, (SOLE + 1) * Z)], fill=(230, 30, 30, 255), width=3)
    d.line([(MID * Z, 0), (MID * Z, 1023)], fill=(40, 90, 230, 255), width=3)
    top = int(np.nonzero(op.any(1))[0].min())
    d.line([(0, top * Z), (1023, top * Z)], fill=(30, 170, 60, 255), width=3)
    hy, hx = np.nonzero(head)
    d.rectangle([hx.min() * Z, hy.min() * Z, (hx.max() + 1) * Z, (hy.max() + 1) * Z], outline=(245, 140, 20, 255), width=3)
    g.convert("RGB").save(os.path.join(a.out, "3_guide.png"))

    cols = sorted({tuple(int(v) for v in c[:3]) for c in des[op]}, key=lambda c: (sum(c), c))
    font = ImageFont.load_default(size=22)
    im = Image.new("RGB", (6 * 170, ((len(cols) + 5) // 6) * 70), (255, 255, 255))
    dd = ImageDraw.Draw(im)
    for i, c in enumerate(cols):
        x, y = (i % 6) * 170, (i // 6) * 70
        dd.rectangle([x + 6, y + 6, x + 60, y + 60], fill=c, outline=(0, 0, 0))
        dd.text((x + 68, y + 22), "#%02X%02X%02X" % c, fill=(0, 0, 0), font=font)
    im.save(os.path.join(a.out, "5_palette.png"))
    shutil.copyfile(DOC, os.path.join(a.out, "MODEL_POSE.md"))
    print(shutil.make_archive(a.out, "zip", a.out), len(cols), "colours, head", hx.min(), hy.min(), hx.max(), hy.max(),
          "oppi", fig.shape)


if __name__ == "__main__":
    main()
