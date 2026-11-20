#!/usr/bin/env python3
"""Lu Bu's sheets (the ragnarok pack, ragnarok_lubu) from Codex's delivery in assets/source/lubu/codex_v02.

    python tools/art/import_lubu.py [--check]
    python tools/art/ppu_hd.py --hero lubu          # then: the hd_ and lo_ tags from the dense strips written here

Codex drew him (2026-11-20, branch codex/ragnarok-lubu-assets-v02, commit 00d78f3) in 128 x 128 cells, the soles' point
at (64, 116): 66 rows from his hair to his soles, 73 to the plume's tip - dense frames already. At PPU 1.65 (PPU
below) he stands 40 game px to his hair, 44 to the plume, a little over the base heroes' 35 (Lu Bu is a giant).

- The swing pictures go into his own frames (BAKE): the client never mirrors an effect picture and does mirror his
  frames, so a crescent drawn pointing right would point right on the red side too (SKILL.md "Both sides"). Each
  effect frame is laid on the body frame showing at that moment, its cell's centre at the soles plus Codex's anchor
  (asset_manifest_v02.json effect_anchors_logical, the way his preview.html lays them); the body frames are cut where
  an effect frame starts or ends (import_native's way), the effect over the body. The ult's charge plays stretched over
  the whole 1.18 s gathering, as in the preview.
- The 1x frames: each dense frame brought to 1 / PPU squares by pixel_down.pixelate (the pack's way: the mean of each
  square snapped to the frame's own colours, near-black squares outline), on a grid one of whose squares has the pivot
  at its centre; the pivot 11.5 game px over the soles (every base and pack sheet), at the centre of an odd frame.
- The dense frames: assets/source/ppu/lubu_<tag>.png, each round(PPU x its 1x frame), the pivot at its centre, 1 px
  gaps - ppu_hd.py reads them as drawn strips (drawn_strip) and writes hd_<tag> and lo_<tag>.
- The effects the kit plays on a unit (hit_spark on every hit, ult_impact where the cut lands, shield_break when a
  shield really breaks): ragnarok/effects/ragnarok_lubu_fx, brought to 1x by pixel_down.scale_fx (no outline, light
  has none), centred on the unit's pivot - ult_impact by its ground line (Codex's cell row 116) 11.5 game px under it,
  shield_break lifted to the chest - each with its hd_ twin (Codex's frames as drawn), an empty idle / hd_idle pair
  for the PPU: addons/ragnarok/src/hd.rs lists the sheet in EFFECTS and DRAWN_EFFECTS (view effects only).
--check rebuilds everything in memory and compares it with the files.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as D  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "lubu", "codex_v02")
PPU_DIR = os.path.join(ROOT, "assets", "source", "ppu")
MOD = os.path.join(ROOT, "ragnarok")
ID = "ragnarok_lubu"
HERO = "lubu"
SHEET = os.path.join(MOD, "champions", ID)
FX_SHEET = os.path.join(MOD, "effects", f"{ID}_fx")
PPU = 1.65                  # tools/art/ppu_hd.py PPU and addons/ragnarok/src/hd.rs HEROES say the same
SOLE = (64, 116)            # Codex's cells: the soles' point (the bottom edge of the feet's last row)
FEET = 11.5                 # game px from a frame's pivot (its centre) down to the soles
ACTIONS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")
# (action, effect, from seconds, anchor from the soles in Codex's px, seconds a frame or None for the effect's own)
BAKE = [
    ("attack", "attack_swipe", 0.26, (32, -30), None),
    ("skill", "sweep", 0.42, (28, -24), None),
    ("skill2", "thrust", 0.34, (40, -28), None),
    ("ult", "ult_charge", 0.0, (12, -76), 1.18 / 8),
    ("ult", "ult_release", 1.18, (35, -43), None),
]
# the attack is a 30-tick action (build_lubu atk_dur): the recovery frames shortened so the swing still ends inside it,
# the blow on frame 4 at 0.32 s as drawn
RETIME = {"attack": [0.08, 0.08, 0.10, 0.06, 0.06, 0.04, 0.04, 0.04]}
# effects played on a unit: Codex's tag, the cell's point that goes on the unit's pivot (x, y in Codex's px)
TARGET_FX = {
    "hit_spark": (64, 64),
    "shield_break": (64, 64 + 14),          # lifted ~8 game px: on his chest, not his belt
    "ult_impact": (64, 116 - FEET * PPU),   # the burst's ground line under the pivot like the soles
}


def read(stem):
    px = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    out = {}
    for tag, a in anims.items():
        fr = []
        for f_ in a["frames"]:
            d = f_["data"]
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            fr.append((px[y:y + h, x:x + w].copy(), float(f_["duration"])))
        out[tag] = fr
    return out


def over(dst, src, x, y):
    """src alpha-composited onto dst with its top-left at (x, y) (hard alpha: src's opaque pixels win)."""
    h, w = src.shape[:2]
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x]
    m = s[..., 3] > 0
    d = dst[y0:y1, x0:x1]
    d[m] = s[m]


def no_specks(a, under=4):
    """Pieces of fewer than `under` pixels apart from everything else go (the user's rule for every frame: 「别留多余的
    像素」; ppu_hd.drawn_strays flags them): the charge's first one-pixel glints, a grain of dust by his knee."""
    from scipy import ndimage
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if not n:
        return a
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    small = np.zeros(n + 1, bool)
    small[1:] = sizes < under
    out = a.copy()
    out[small[lab]] = 0
    return out


# the composing canvas: room for the widest swing round the soles
CW, CH, CS = 288, 224, (144, 176)


def baked(body, fx):
    """{action: [(dense frame on the canvas, seconds)]}: the body frames with the BAKE pictures, cut where an effect
    frame starts or ends."""
    out = {}
    for tag in ACTIONS:
        frames = body[tag]
        durs = RETIME.get(tag, [d for _, d in frames])
        starts = np.cumsum([0.0] + durs[:-1])
        end = float(sum(durs))
        bakes = [b for b in BAKE if b[0] == tag]
        cuts = {0.0, end} | {float(s) for s in starts}
        plays = []
        for _, name, t0, anchor, step in bakes:
            fr = fx[name]
            dt = step if step is not None else fr[0][1]
            for j in range(len(fr) + 1):
                t = t0 + j * dt
                if t < end:
                    cuts.add(round(t, 6))
            plays.append((name, t0, anchor, dt, fr))
        cuts = sorted(c for c in cuts if c <= end)
        segs = []
        for a, b in zip(cuts, cuts[1:]):
            if b - a < 1e-6:
                continue
            i = int(np.searchsorted(starts, a + 1e-9, side="right") - 1)
            canvas = np.zeros((CH, CW, 4), np.uint8)
            over(canvas, frames[i][0], CS[0] - SOLE[0], CS[1] - SOLE[1])
            for name, t0, (ax, ay), dt, fr in plays:
                j = int(np.floor((a - t0) / dt + 1e-9))
                if 0 <= j < len(fr):
                    over(canvas, fr[j][0], CS[0] + ax - 64, CS[1] + ay - 64)
            canvas = no_specks(canvas)
            if segs and np.array_equal(segs[-1][0], canvas):
                segs[-1] = (canvas, segs[-1][1] + (b - a))
            else:
                segs.append((canvas, b - a))
        out[tag] = segs
    return out


def outline_of(frames):
    return D.edge_colour(np.concatenate([f for f, _ in frames], axis=1))


def one_x(dense, pivot, outline, pal):
    """A dense canvas -> (the 1x frame, odd, its pivot at the centre; the pivot's pixel)."""
    c = PPU
    px, py = pivot
    small, (nx, ny) = D.pixelate(dense, 1.0 / c, (px - c / 2, py - c / 2), outline, pal)
    op = small[..., 3] > 0
    if not op.any():
        return np.zeros((1, 1, 4), np.uint8)
    ys, xs = np.nonzero(op)
    rx = max(nx - xs.min(), xs.max() - nx)
    ry = max(ny - ys.min(), ys.max() - ny)
    W, H = 2 * rx + 1, 2 * ry + 1
    f = np.zeros((H, W, 4), np.uint8)
    f[ys - ny + ry, xs - nx + rx] = small[ys, xs]
    return f


def dense_of(dense, pivot, size):
    """The dense frame of `size` (W, H) cut round the pivot at its centre."""
    W, H = size
    px, py = pivot
    x0, y0 = int(round(px - W / 2)), int(round(py - H / 2))
    out = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(dense.shape[1], x0 + W), min(dense.shape[0], y0 + H)
    out[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = dense[sy0:sy1, sx0:sx1]
    lost = dense[..., 3].sum() - out[..., 3].sum()
    if lost:
        sys.exit(f"a dense frame lost {lost / 255:.0f} pixels outside round(PPU x its 1x frame) - widen the 1x frame")
    return out


def hero_sheets(body, fx):
    """-> ({tag: [(1x frame, ms)]}, {tag: [dense frame of round(PPU x 1x)]})."""
    segs = baked(body, fx)
    every = [f for tag in ACTIONS for f, _ in segs[tag]]
    outline = D.edge_colour(np.concatenate(every, axis=1))
    pal = D.palette_of(np.concatenate([body[t][0][0] for t in ACTIONS], axis=1), 96)
    pivot = (CS[0], CS[1] - FEET * PPU)
    ones, denses = {}, {}
    for tag in ACTIONS:
        ones[tag], denses[tag] = [], []
        for canvas, secs in segs[tag]:
            f1 = one_x(canvas, pivot, outline, pal)
            h1, w1 = f1.shape[:2]
            # the dense frame must hold the whole picture: grow the 1x frame alike at both ends until it does
            while True:
                size = (round(w1 * PPU), round(h1 * PPU))
                try:
                    d = dense_of(canvas, pivot, size)
                    break
                except SystemExit:
                    w1, h1 = w1 + 2, h1 + 2
            if (h1, w1) != f1.shape[:2]:
                g = np.zeros((h1, w1, 4), np.uint8)
                oy, ox = (h1 - f1.shape[0]) // 2, (w1 - f1.shape[1]) // 2
                g[oy:oy + f1.shape[0], ox:ox + f1.shape[1]] = f1
                f1 = g
            ones[tag].append((f1, round(secs * 1000, 3)))
            denses[tag].append(d)
    return ones, denses


def fx_sheet(fx):
    """{tag: [(frame, ms)]} of TARGET_FX: each tag's 1x frames (pixel_down.scale_fx, centred on its point) and their
    hd_ twins (Codex's own frames cut round the same point, round(PPU x the 1x frame)), plus the empty `idle` /
    `hd_idle` pair hd_engine reads the sheet's PPU from (20 x 20 and 33 x 33: 1.65 x 20 is whole)."""
    out = {"idle": [(np.zeros((20, 20, 4), np.uint8), 100.0)]}
    dense = {"hd_idle": [(np.zeros((33, 33, 4), np.uint8), 100.0)]}
    for name, (px, py) in TARGET_FX.items():
        frames, twins = [], []
        for a, secs in fx[name]:
            small, (nx, ny) = D.scale_fx(a, 1.0 / PPU, (px, py), mote=0)
            op = small[..., 3] > 0
            rx = ry = 1
            if op.any():
                ys, xs = np.nonzero(op)
                rx = int(np.ceil(max(nx - xs.min(), xs.max() + 1 - nx)))
                ry = int(np.ceil(max(ny - ys.min(), ys.max() + 1 - ny)))
            # the dense twin must hold Codex's whole picture round the same centre
            ys2, xs2 = np.nonzero(a[..., 3] > 0)
            if len(xs2):
                rx = max(rx, int(np.ceil(max(px - xs2.min(), xs2.max() + 1 - px) / PPU)))
                ry = max(ry, int(np.ceil(max(py - ys2.min(), ys2.max() + 1 - py) / PPU)))
            W, H = 2 * rx, 2 * ry
            f = np.zeros((H, W, 4), np.uint8)
            if op.any():
                f[ys - int(ny) + ry, xs - int(nx) + rx] = small[ys, xs]
            frames.append((f, round(secs * 1000, 3)))
            twins.append((dense_of(a, (px, py), (round(W * PPU), round(H * PPU))), round(secs * 1000, 3)))
        out[name] = frames
        dense["hd_" + name] = twins
    return {**out, **dense}


def strip(frames):
    """Dense frames left to right, 1 px gaps (ppu_hd.drawn_strip's layout)."""
    W = sum(f.shape[1] for f in frames) + len(frames) - 1
    H = max(f.shape[0] for f in frames)
    s = np.zeros((H, W, 4), np.uint8)
    x = 0
    for f in frames:
        s[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1] + 1
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    body = read(os.path.join(SRC, f"{ID}_native"))
    fx = read(os.path.join(SRC, f"{ID}_fx_native"))
    ones, denses = hero_sheets(body, fx)
    fxs = fx_sheet(fx)
    if a.check:
        bad = 0
        for tag, frames in denses.items():
            p = os.path.join(PPU_DIR, f"{HERO}_{tag}.png")
            if not os.path.isfile(p) or not np.array_equal(np.asarray(Image.open(p).convert("RGBA")), strip(frames)):
                print(f"{p}: differs")
                bad += 1
        sys.exit(1 if bad else 0)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    os.makedirs(os.path.dirname(FX_SHEET), exist_ok=True)
    os.makedirs(PPU_DIR, exist_ok=True)
    w, h = G.write_sheet(SHEET, ones)
    for tag, frames in denses.items():
        Image.fromarray(strip(frames)).save(os.path.join(PPU_DIR, f"{HERO}_{tag}.png"))
    fw, fh = G.write_sheet(FX_SHEET, fxs)
    print(f"{ID}#sheet.png {w}x{h} (1x), {ID}_fx#sheet.png {fw}x{fh}; dense strips in {PPU_DIR}")
    for tag in ACTIONS:
        f = ones[tag][0][0]
        print(f"  {tag:7s} {len(ones[tag]):2d} frames, 1x {f.shape[1]}x{f.shape[0]}, "
              f"{sum(ms for _, ms in ones[tag]) / 1000:.2f} s")


if __name__ == "__main__":
    main()
