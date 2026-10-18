"""league_riven's two swords at 8 angles each, read back from Codex's raw sheets (hd/swords_raw/, the answer to
pack_riven_swords.py): hd/swords/{normal,reforged}_<n>.png + hd/swords/swords.json.

    python tools/art/swords_riven_hd.py [--review C:/t/rv_sw_review]

Codex's exported sheets were rescaled to the template lines and came out speckled (the glow sampled into the rim), so
the raw sheets are read instead. They are drawn on black with a soft glow, on squares of ~5.5 px: a sword is
whatever the closed ring of its sharp colour edges (EDGE) holds - the glow is smooth and never makes one. Each cell
is read on the square that makes it LENGTH squares long (about 2 x 2 of Codex's squares -> one game square; 31 the
size the pack asked for), all 16 drawings on one shared palette.

Per drawing swords.json keeps (in the drawing's own squares): "angle" (degrees counter-clockwise from pointing right,
measured pommel -> tip along the drawing's long axis), "grip" (the centre of the leather grip, where her fist goes),
"pommel" and "tip" (the ends of the axis), "guard" (the crossguard's centre).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
HD = os.path.join(ROOT, "assets", "source", "riven", "hd")
SHEETS = {"normal": ["normal_1", "normal_2"], "reforged": ["reforged_1", "reforged_2"]}
ANGLES = [13.0, 35.5, 58.0, 80.5, 103.0, 125.5, 148.0, 170.5]   # pack_riven_swords.ANGLES, cell order
CELL = (768, 512)
EDGE, CLOSE, OPEN, MIN_AREA = 60, 4, 2, 3000   # raw px: colour step over 2 px, gap closing, crumb opening, sword size
NATIVE = (4.0, 8.0)                            # Codex's own squares lie in here
COLOURS = 28
LENGTH = {"normal": 31, "reforged": 44}       # squares pommel to tip (the reforged one's steel = the normal one's)
GRIP = lambda c: c[0] > c[1] + 25 and c[1] > c[2] + 8 and c[0] > 90      # the brown leather wrap
GUARD = lambda c: max(c) - min(c) < 22 and 70 < max(c) < 150              # the steel crossguard's greys


def lp(path):
    return FD.lp(path)


def cutout(a):
    s = a[..., :3].astype(float).sum(axis=2)
    g = np.zeros_like(s)
    g[:, 1:-1] = np.abs(s[:, 2:] - s[:, :-2])
    g[1:-1] = np.maximum(g[1:-1], np.abs(s[2:] - s[:-2]))
    fig = nd.binary_closing(g > EDGE, structure=np.ones((3, 3)), iterations=CLOSE)
    fig = nd.binary_opening(nd.binary_fill_holes(fig), iterations=OPEN)
    lab, n = nd.label(fig)
    if n:
        sz = nd.sum(fig, lab, range(1, n + 1))
        fig = np.isin(lab, [i + 1 for i, v in enumerate(sz) if v >= MIN_AREA])
    return np.dstack([a[..., :3], np.where(fig, 255, 0)]).astype(np.uint8)


def read_cell(c, length):
    """The cell on squares that make the sword LENGTH squares pommel to tip (Codex drew sheet 2 on bigger squares
    than sheet 1: about 2 of its own squares to one), starting where Codex's own lines are."""
    op = c[..., 3] > 0
    FD.PITCH = NATIVE
    (_, phx), (_, phy) = FD.fit(c, op, 1), FD.fit(c, op, 0)
    ys, xs = np.nonzero(op)
    pts = np.stack([xs, ys], 1).astype(float)
    u = np.linalg.svd(pts - pts.mean(0), full_matrices=False)[2][0]
    t = (pts - pts.mean(0)) @ u
    px = py = (t.max() - t.min() + 1) / length
    xs, ys = np.arange(phx, c.shape[1], px), np.arange(phy, c.shape[0], py)
    out = np.zeros((len(ys) - 1, len(xs) - 1, 4), np.uint8)
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            win = c[int(round(ys[j])):int(round(ys[j + 1])), int(round(xs[i])):int(round(xs[i + 1]))].reshape(-1, 4)
            on = win[win[:, 3] > 0]
            if len(on) * 2 > len(win):
                out[j, i, :3] = np.median(on[:, :3], axis=0)
                out[j, i, 3] = 255
    return FD.crop(out), (px, py)


def measure(d):
    """Pommel, tip, grip, guard and angle of one drawing (its own squares, y down)."""
    op = d[..., 3] > 0
    ys, xs = np.nonzero(op)
    pts = np.stack([xs, ys], 1).astype(float) + 0.5
    m = pts.mean(0)
    u = np.linalg.svd(pts - m, full_matrices=False)[2][0]
    t = (pts - m) @ u
    grip = np.array([[x + 0.5, y + 0.5] for y, x in zip(ys, xs) if GRIP(d[y, x, :3].astype(int))])
    g = grip.mean(0) if len(grip) else m
    if (g - m) @ u > 0:          # the grip is at the pommel's end
        u, t = -u, -t
    pommel, tip = m + u * t.min(), m + u * t.max()
    guard = np.array([[x + 0.5, y + 0.5] for y, x in zip(ys, xs) if GUARD(d[y, x, :3].astype(int))
                      and (np.array([x + 0.5, y + 0.5]) - m) @ u < (g - m) @ u + 8])
    gd = guard.mean(0) if len(guard) else g
    ang = math.degrees(math.atan2(-u[1], u[0]))
    r = lambda p: [round(float(p[0]), 2), round(float(p[1]), 2)]
    return dict(angle=round(ang, 1), pommel=r(pommel), tip=r(tip), grip=r(g), guard=r(gd),
                length=round(float(t.max() - t.min()), 1), size=[d.shape[1], d.shape[0]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    reads = {}
    for kind, sheets in SHEETS.items():
        for s, sheet in enumerate(sheets):
            im = np.asarray(Image.open(lp(os.path.join(HD, "swords_raw", sheet + ".png"))).convert("RGB"))
            for k in range(4):
                x0, y0 = (k % 2) * CELL[0], (k // 2) * CELL[1]
                c = cutout(im[y0:y0 + CELL[1], x0:x0 + CELL[0]])
                d, pitch = read_cell(c, LENGTH[kind])
                reads[f"{kind}_{s * 4 + k + 1}"] = (d, pitch)
    # one palette for all 16
    tall = max(d.shape[0] for d, _ in reads.values())
    strip = np.concatenate([np.pad(d, ((0, tall - d.shape[0]), (0, 1), (0, 0))) for d, _ in reads.values()], axis=1)
    op = strip[..., 3] > 0
    idx, pal = V.kmeans(strip, COLOURS)
    q = np.zeros_like(strip)
    q[op, :3] = pal[idx[op]]
    q[op, 3] = 255
    out_dir = os.path.join(HD, "swords")
    os.makedirs(lp(out_dir), exist_ok=True)
    info, x = {}, 0
    for name, (d, pitch) in reads.items():
        w = d.shape[1]
        dq = FD.crop(q[:d.shape[0], x:x + w])
        x += w + 1
        Image.fromarray(dq).save(lp(os.path.join(out_dir, name + ".png")))
        n = int(name.split("_")[1]) - 1
        info[name] = dict(asked=ANGLES[n], pitch=[round(float(pitch[0]), 2), round(float(pitch[1]), 2)],
                          **measure(dq))
        print(name, info[name])
    with open(lp(os.path.join(out_dir, "swords.json")), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        cells = []
        for name in info:
            im = Image.open(lp(os.path.join(out_dir, name + ".png"))).convert("RGBA")
            cells.append((f"{name} {info[name]['angle']:g} ({info[name]['asked']:g})", FD.shown(im, 1, 6)))
        FD.strip(cells[:8]).convert("RGB").save(os.path.join(a.review, "swords_normal.png"))
        FD.strip(cells[8:]).convert("RGB").save(os.path.join(a.review, "swords_reforged.png"))
        print("review written to", a.review)


if __name__ == "__main__":
    main()
