#!/usr/bin/env python3
"""Ao Shin's effects from Codex's step-3 delivery (assets/source/aoshin/codex_fx/aoshin_fx, PROMPTS_FX.md) made ready
for tools/art/import_aoshin_fx.py: assets/source/aoshin/codex_fx/clean/pixel_1x/aoshin_fx_<name>.png, one row of equal
frames each at game size (the pack's cell sizes), alpha 0 / 255.

    python tools/art/clean_aoshin_fx.py [--review out.png]

Codex's own game-size sheets are kept for eight (a_ball a_hit q_beam q_hit e_cast p_bolt r_cloud r_bolt: clean, the
asked sizes and symmetries). Three are cut again from its raws (2026-10-28), because its reduction lost them:
  e_shield  the storm shield's swirling wind and cloud round him came back as a square frame of broken strokes (its
            HANDOFF: the edge pressed into a narrow outer band) - the raw's two curved bands are brought down whole;
  p_storm   the lightning crackling up round him after the storm, also a square - the raw's two bolts and ground ring,
            only its brighter squares (LUM_MIN: the dull blue haze between the strokes dropped);
  q_sil     the silence's crackling crown came back as a few white arches - the raw's zigzag of sparks, over the head.
Each raw frame is cut at the emptiest column near its 1/k mark, every frame of an effect brought down by one factor
(its biggest frame to the cell's INNER box), alpha-weighted Lanczos (ppu_rig.lanczos_down), snapped to the pack's
ramps (pack_aoshin_fx ELEC / SCALE / STORM) and made symmetric left to right (a square and its mirror: the brighter).
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pack_aoshin_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aoshin", "codex_fx", "aoshin_fx")
OUT = os.path.join(ROOT, "assets", "source", "aoshin", "codex_fx", "clean")
KEEP = ("a_ball", "a_hit", "q_beam", "q_hit", "e_cast", "p_bolt", "r_cloud", "r_bolt")
# name -> (frames, cell (w, h), inner box (w, h) the biggest frame fills, top row of that box (None: centred),
#          LUM_MIN (a square's mean rgb at least this, 0: all), the raw's squares counted from this mean rgb)
REDO = {
    "e_shield": (6, (46, 44), (46, 44), None, 0, 0),
    "p_storm": (6, (46, 44), (46, 44), None, 120, 0),
    "q_sil": (6, (18, 44), (18, 16), 0, 0, 90),
}


def lp(p):
    return R.lp(p)


def ramp(s):
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in s.replace(" ", "").split(",")], float)


PAL = np.vstack([ramp(PK.ELEC), ramp(PK.SCALE), ramp(PK.STORM)])


def raw_frames(name, k, seen):
    """The raw cut into k frames at the emptiest column near each 1/k mark; `seen` = the squares counted (alpha over
    60 and mean rgb at least `seen`: q_sil's raw has faint grid boxes round its frames)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"aoshin_fx_{name}.png"))).convert("RGBA")).copy()
    vis = (a[..., 3] > 60) & (a[..., :3].mean(-1) >= seen)
    a[~vis] = 0
    col = vis.sum(0)
    W = a.shape[1]
    cuts = [0]
    for j in range(1, k):
        c = int(W * j / k)
        cuts.append(min(range(c - 60, c + 60), key=lambda x: (col[x], abs(x - c))))
    cuts.append(W)
    return [a[:, cuts[j]:cuts[j + 1]] for j in range(k)]


def redo(name):
    k, (W, H), inner, top, lum_min, seen = REDO[name]
    frs = raw_frames(name, k, seen)
    boxes = []
    for f in frs:
        ys, xs = np.nonzero(f[..., 3] > 0)
        boxes.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    s = min(inner[0] / max(b[2] - b[0] for b in boxes), inner[1] / max(b[3] - b[1] for b in boxes))
    y_lo, y_hi = min(b[1] for b in boxes), max(b[3] for b in boxes)
    out = []
    for f, (x0, _y0, x1, _y1) in zip(frs, boxes):
        w, h = int(round(W / s)), int(round(H / s))
        X0 = int((x0 + x1) / 2 - w / 2)
        Y0 = int(y_lo - top / s) if top is not None else int((y_lo + y_hi) / 2 - h / 2)
        crop = np.zeros((h, w, 4), np.uint8)
        sx0, sy0 = max(0, X0), max(0, Y0)
        sx1, sy1 = min(f.shape[1], X0 + w), min(f.shape[0], Y0 + h)
        crop[sy0 - Y0:sy1 - Y0, sx0 - X0:sx1 - X0] = f[sy0:sy1, sx0:sx1]
        d = R.lanczos_down(crop, 0, size=(W, H)).astype(float)
        op = (d[..., 3] > 0) & (d[..., :3].mean(-1) >= lum_min)
        idx = ((d[..., None, :3] - PAL[None, None]) ** 2).sum(-1).argmin(-1)
        o = np.zeros((H, W, 4), np.uint8)
        o[op, :3] = PAL[idx[op]].astype(np.uint8)
        o[op, 3] = 255
        m = o[:, ::-1]
        take = (m[..., 3] > 0) & ((o[..., 3] == 0) | (m[..., :3].astype(int).sum(-1) > o[..., :3].astype(int).sum(-1)))
        o[take] = m[take]
        if not o[..., 3].any():
            sys.exit(f"{name}: an empty frame")
        out.append(o)
    return np.concatenate(out, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the redone sheets at 8x here")
    a = ap.parse_args()
    os.makedirs(lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    for name in KEEP:
        shutil.copyfile(lp(os.path.join(SRC, "pixel_1x", f"aoshin_fx_{name}.png")),
                        lp(os.path.join(OUT, "pixel_1x", f"aoshin_fx_{name}.png")))
    sheets = {}
    for name in REDO:
        sheets[name] = redo(name)
        Image.fromarray(sheets[name]).save(lp(os.path.join(OUT, "pixel_1x", f"aoshin_fx_{name}.png")))
        print(f"{name}: {sheets[name].shape[1]} x {sheets[name].shape[0]}")
    for slot in ("skill", "skill2", "ult"):
        shutil.copyfile(lp(os.path.join(SRC, f"aoshin_icon_{slot}.png")), lp(os.path.join(OUT, f"aoshin_icon_{slot}.png")))
    if a.review:
        z = 8
        H = sum(s.shape[0] + 4 for s in sheets.values())
        W = max(s.shape[1] for s in sheets.values())
        im = Image.new("RGBA", (W * z, H * z), (40, 40, 52, 255))
        y = 0
        for s in sheets.values():
            im.alpha_composite(Image.fromarray(s).resize((s.shape[1] * z, s.shape[0] * z), Image.NEAREST), (0, y * z))
            y += s.shape[0] + 4
        im.convert("RGB").save(lp(a.review))
        print(a.review)


if __name__ == "__main__":
    main()
