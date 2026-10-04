#!/usr/bin/env python3
"""Sett's step 2 pack for Codex: the pictures that go with assets/source/sett/MODEL_STRIPS.md.

    python tools/lol/native_pose.py assets/source/sett/poses.json --out <renders>      # where League is installed
    python tools/art/pack_sett_strips.py --renders <renders> --out <folder> [--zip]

<renders> is native_pose.py's output for poses.json (sett_native_<tag>.png, sett_pose_<tag>.png, sett_cells.json).
Into <folder>:
  design/sett_design.png, _1x.png   the approved design (assets/source/native/sett_native.png) at 8x and 1x: 26 x 42,
                                    the soles on row 99, the middle of the feet on column 64, the pivot (64, 88)
  design/sett_head.png, _1x.png     the head every frame gets pasted: the ear tips to the chin (rows 58-69), the hair,
                                    both ears and the face, nothing of the mantle or the torc
  design/sett_palette.png           the design's 26 colours, dark to light, with their hex
  sett_idle.png                     the idle strip, already done: every frame is the design on the cell's pivot
  now/sett_now_<tag>.png            League's frames sampled at game size, at 8x (native_pose's sett_native_<tag>.png)
  pose/lol_pose_<tag>.png           the same frames rendered big, same grid and places (sett_pose_<tag>.png)
  guide/sett_guide_<tag>.png        per cell: its border, the pivot (blue cross), the feet line (red: the soles' row
                                    is the one above it), the band under it where nothing may be (pink), the frame
                                    number and its ms
  sett_cells.json                   native_pose's table: each frame's pivot in its cell and its ms
  refs/sett_picture.png             Codex's picture A, where the design comes from
  style/3_quality_bar.png           pack fighters as they are in the game now, at 8x (pack_sett_model.quality_bar)
  MODEL_STRIPS.md                   the prompts
The renders show Riot's model: they go into the pack only, never into git.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_sett as D  # noqa: E402
import pack_sett_model as P  # noqa: E402
from native_refs import layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sett")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "sett_native.png")
POSES = os.path.join(SRC, "poses.json")
Z = 8
PIVOT = (64, 88)                 # the design's pivot on its 128 x 128 canvas: 11.5 px above the soles (row 99)
HEAD_ROWS = (58, 69)             # the ear tips to the chin on the canvas


def design_1x():
    return np.asarray(Image.open(DESIGN).convert("RGBA"))[::Z, ::Z].copy()


def head_mask(a):
    """The head on the design canvas: its hair, skin and eye squares from the ear tips to the chin, the ears' violet
    insides above the mantle, and the outline squares touching them."""
    mat = {h: m for m, hs in D.PALETTE.items() for h in hs}
    mat.update({D.EYE: "face", D.WHITE: "face"})
    name = lambda p: "%02X%02X%02X" % tuple(int(v) for v in p[:3])
    top, chin = HEAD_ROWS
    head = np.zeros(a.shape[:2], bool)
    for y in range(top, chin + 1):
        for x in range(a.shape[1]):
            m = mat.get(name(a[y, x])) if a[y, x, 3] else None
            head[y, x] = m in ("hair", "skin", "face") or (m == "mantle" and y < top + 5 and 58 <= x <= 68)
    edge = [(y, x) for y in range(top, chin + 1) for x in range(1, a.shape[1] - 1)
            if a[y, x, 3] and name(a[y, x]) in D.DARK and not head[y, x]
            and any(head[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)) if 0 <= y + dy < a.shape[0])]
    for p in edge:
        head[p] = True
    return head


def big(a):
    return Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1), "RGBA")


def palette_sheet(a):
    cols = np.unique(a[a[..., 3] > 0][:, :3], axis=0)
    cols = sorted(cols.tolist(), key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])
    sw, per = 64, 9
    img = Image.new("RGB", (per * (sw + 80), -(-len(cols) // per) * (sw + 24)), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for i, c in enumerate(cols):
        x, y = (i % per) * (sw + 80), (i // per) * (sw + 24)
        d.rectangle((x + 4, y + 4, x + 4 + sw, y + 4 + sw), fill=tuple(c), outline=(0, 0, 0))
        d.text((x + sw + 10, y + sw // 2), "#%02X%02X%02X" % tuple(c), fill=(0, 0, 0))
    return img, ["#%02X%02X%02X" % tuple(c) for c in cols]


def idle_strip(a, frames, cell):
    cols, rows = layout(len(frames))
    out = np.zeros((rows * cell[1], cols * cell[0], 4), np.uint8)
    for k, f in enumerate(frames):
        ox = k % cols * cell[0] + f["pivot"][0] - PIVOT[0]
        oy = k // cols * cell[1] + f["pivot"][1] - PIVOT[1]
        ys, xs = np.nonzero(a[..., 3])
        out[ys + oy, xs + ox] = a[ys, xs]
    return big(out)


def guide(frames, cell, feet):
    cols, rows = layout(len(frames))
    w, h = cell[0] * Z, cell[1] * Z
    img = Image.new("RGBA", (cols * w, rows * h), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    line = (cell[1] - feet) * Z
    for k, f in enumerate(frames):
        x0, y0 = k % cols * w, k // cols * h
        d.rectangle((x0, y0 + line, x0 + w - 1, y0 + h - 1), fill=(255, 215, 225, 255))
        d.line((x0, y0 + line, x0 + w - 1, y0 + line), fill=(230, 30, 30, 255), width=3)
        d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), outline=(150, 150, 150, 255), width=2)
        px, py = x0 + f["pivot"][0] * Z + Z // 2, y0 + f["pivot"][1] * Z + Z // 2
        d.line((px - 24, py, px + 24, py), fill=(40, 90, 230, 255), width=3)
        d.line((px, py - 24, px, py + 24), fill=(40, 90, 230, 255), width=3)
        d.text((x0 + 10, y0 + 8), f"frame {k + 1}  {f['ms']} ms", fill=(0, 0, 0, 255))
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--renders", required=True, help="native_pose.py's --out for assets/source/sett/poses.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--zip", action="store_true", help="also write <out>.zip")
    args = ap.parse_args()
    with open(POSES, encoding="utf-8") as f:
        spec = json.load(f)
    with open(os.path.join(args.renders, "sett_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cell, feet = cells["cell"], spec["cell"][2]
    for sub in ("design", "now", "pose", "guide", "refs", "style"):
        os.makedirs(os.path.join(args.out, sub), exist_ok=True)

    a = design_1x()
    big(a).save(os.path.join(args.out, "design", "sett_design.png"))
    Image.fromarray(a, "RGBA").save(os.path.join(args.out, "design", "sett_design_1x.png"))
    hm = head_mask(a)
    head = np.where(hm[..., None], a, 0).astype(np.uint8)
    big(head).save(os.path.join(args.out, "design", "sett_head.png"))
    Image.fromarray(head, "RGBA").save(os.path.join(args.out, "design", "sett_head_1x.png"))
    ys, xs = np.nonzero(hm)
    sheet, hexes = palette_sheet(a)
    sheet.save(os.path.join(args.out, "design", "sett_palette.png"))

    tags = cells["tags"]
    idle_strip(a, tags["idle"], cell).save(os.path.join(args.out, "sett_idle.png"))
    out = lambda *p: os.path.join(args.out, *p)
    for tag, frames in tags.items():
        if tag != "idle":
            shutil.copy(os.path.join(args.renders, f"sett_native_{tag}.png"), out("now", f"sett_now_{tag}.png"))
            shutil.copy(os.path.join(args.renders, f"sett_pose_{tag}.png"), out("pose", f"lol_pose_{tag}.png"))
        guide(frames, cell, feet).convert("RGB").save(out("guide", f"sett_guide_{tag}.png"))
    shutil.copy(os.path.join(args.renders, "sett_cells.json"), out("sett_cells.json"))
    shutil.copy(os.path.join(SRC, "codex_picture", "sett-model-A.png"), out("refs", "sett_picture.png"))
    P.quality_bar().convert("RGB").save(os.path.join(args.out, "style", "3_quality_bar.png"))
    shutil.copy(os.path.join(SRC, "MODEL_STRIPS.md"), os.path.join(args.out, "MODEL_STRIPS.md"))

    print(f"design 26 x 42, {len(hexes)} colours: {' '.join(hexes)}")
    print(f"head: x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()} on the canvas, {int(hm.sum())} squares")
    for tag, frames in tags.items():
        cols, rows = layout(len(frames))
        print(f"{tag}: {len(frames)} frames, {cols} x {rows} cells, {cols * cell[0] * Z} x {rows * cell[1] * Z} px, "
              f"ms {' '.join(str(f['ms']) for f in frames)}, feet row {cell[1] - feet - 1}")
    if args.zip:
        path = shutil.make_archive(os.path.abspath(args.out), "zip", args.out)
        print("wrote", path)


if __name__ == "__main__":
    main()
