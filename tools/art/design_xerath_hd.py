#!/usr/bin/env python3
"""league_xerath at PPU (assets/source/xerath/hd/design.png): Codex's draft B read back on its own grid as a whole
(78 x 39 squares - tools/art/design_xerath.py had cut it to the 1x's 44 rows), then made slimmer with a smaller head
by whole rows and columns, every kept square the draft's own.

    python tools/art/design_xerath_hd.py [--check]

The user, 2026-10-21: 「主模型也要利用PPU重做吧 身材可以变细 头可以变小」「不是重做 是重新调整」, on the leg tips
「下面要做成一样长吧 黑边要去掉吧」, and of three takes (as drawn / slim / slimmer) 「你选一个吧 反正游戏里别太大就行」 ->
the slimmer one (32 x 73), shown at about 42 game px (the 1x was 44). In game that one read as stretched (「泽拉斯在游戏里
身体太长了吧？」「看着好奇怪 泽拉斯模型」: 19.5 x 43 game px beside heroes 25-37 wide), and of three shorter takes the user
picked C (「改成这个 优先改这个 优先级最高 改完合并」): three body columns back (BODY_COLS 4, not 7) and whole rows out of the
waist and the leg spikes (SHORTER) - 35 x 62, shown at 40 game px. Steps:
  1. the read-back of design_xerath (78 x 39) on its 24 colours (design_varus.kmeans, as the 1x);
  2. the hood (rows 0-14) loses HEAD_ROWS rows and HEAD_COLS columns (design_riven.keep_axis, never the eyes' rows
     FACE_R nor the hood's opening FACE_C), the body below it BODY_COLS columns (never the torso TORSO_C); the hood goes
     back on the body over the neck column;
  3. strips.complete_outline where a deleted line held the outline (the face kept);
  4. the leg spikes (fix_legs): below each spike's last filled row only the outline square under its fill, the black
     tails the draft drew below them gone; the shorter (far) spike grows by copies of its own rows spread down its
     taper, so both end on one row;
  5. shorter (SHORTER): in each band, the rows that differ least from the row above them go, never two side by side
     (rows 31, 33, 41 and 43 of the waist, every other row of the spikes from 54 to 66).
--check compares the result with the committed design.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
import design_varus as dv  # noqa: E402
import design_xerath as DX  # noqa: E402
import strips  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "xerath", "hd", "design.png")
SPLIT = 15                 # read-back rows 0..14: the hood; 15..: the shoulders and the body
FACE_R = range(9, 14)      # the hood's rim, the eyes, the energy face
FACE_C = range(17, 31)     # the hood's opening
TORSO_C = range(15, 29)    # the chest, the gem, the energy core
NECK = 23                  # the column the hood sits over
HEAD_ROWS, HEAD_COLS, BODY_COLS = 3, 4, 4
SHORTER = ((51, 68, 7), (31, 44, 4))   # (first row, end row, rows out): the leg spikes, the waist
DARK = 30.0                # luma under which a square is outline


def lp(path):
    return DX.lp(path)


def slimmer(idx, pal):
    H, W = idx.shape
    head, body = idx[:SPLIT], idx[SPLIT:]
    rows = R.keep_axis([head[y] for y in range(SPLIT)], SPLIT - HEAD_ROWS, FACE_R)
    head = head[rows]
    hcols = R.keep_axis([head[:, x] for x in range(W)], W - HEAD_COLS, FACE_C)
    bcols = R.keep_axis([body[:, x] for x in range(W)], W - BODY_COLS, TORSO_C)
    head, body = head[:, hcols], body[:, bcols]
    off = bcols.index(NECK) - hcols.index(NECK)
    x0 = min(0, off)
    w = max(body.shape[1], head.shape[1] + off) - x0
    out = np.full((head.shape[0] + body.shape[0], w), -1, int)
    out[head.shape[0]:, -x0:-x0 + body.shape[1]] = body
    hh = out[:head.shape[0], off - x0:off - x0 + head.shape[1]]
    hh[head >= 0] = head[head >= 0]
    fig = np.zeros(out.shape + (4,), np.uint8)
    m = out >= 0
    fig[m, :3] = pal[out[m]]
    fig[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [i for i, r in enumerate(rows) if r in FACE_R]
    fc = [i for i, c in enumerate(hcols) if c in FACE_C]
    keep[fr[0]:fr[-1] + 1, off - x0 + fc[0]:off - x0 + fc[-1] + 1] = True
    outline = tuple(int(v) for v in pal[int(np.argmin((pal * [0.299, 0.587, 0.114]).sum(1)))])
    can = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    can, _, _ = strips.complete_outline(can, color=outline, feet=fig.shape[0], keep=np.pad(keep, 1))
    ys, xs = np.nonzero(can[..., 3] > 0)
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1], outline


def fix_legs(fig, outline):
    fig = fig.copy()
    op = fig[..., 3] > 0
    lum = (fig[..., :3].astype(float) * [0.299, 0.587, 0.114]).sum(2)
    fill = op & (lum >= DARK)
    H, W = op.shape
    low = range(H - 20, H)
    lit = [x for x in range(W) if op[H - 20:, x].any()]
    gap = [x for x in range(min(lit), max(lit)) if not op[H - 20:, x].any()]
    mid = (min(gap) + max(gap)) // 2
    legs = [(c0, c1, max(y for y in low if fill[y, c0:c1].any())) for c0, c1 in ((0, mid), (mid, W))]
    cap = np.array([*outline, 255], np.uint8)
    for c0, c1, tip in legs:
        under = fill[tip, c0:c1]
        fig[tip + 1:, c0:c1] = 0
        if tip + 1 < H:
            fig[tip + 1, c0:c1][under] = cap
    end = max(t for _, _, t in legs)
    for c0, c1, tip in legs:
        n = end - tip
        if not n:
            continue
        top = tip - 14
        seg = fig[top:tip + 2, c0:c1].copy()
        reps = np.ones(len(seg), int)
        for k in np.linspace(2, len(seg) - 4, n).round().astype(int):
            reps[k] += 1
        grown = np.repeat(seg, reps, axis=0)
        fig[top:, c0:c1] = 0
        fig[top:top + len(grown), c0:c1] = grown[:H - top]
    ys = np.nonzero(fig[..., 3].any(1))[0]
    return fig[:ys.max() + 1]


def build():
    raw = DX.read_back()
    assert raw.shape[:2] == (78, 39), raw.shape
    idx, pal = dv.kmeans(raw, DX.K)
    fig, outline = slimmer(idx, pal)
    return shorter(fix_legs(fig, outline))


def shorter(fig):
    gone = set()
    for r0, r1, n in SHORTER:
        cost = sorted((int((np.abs(fig[y].astype(int) - fig[y - 1].astype(int)).sum(-1) > 0).sum()), y)
                      for y in range(r0, r1))
        picked = []
        for _, y in cost:
            if len(picked) == n:
                break
            if all(abs(y - q) >= 2 for q in picked):
                picked.append(y)
        gone |= set(picked)
    return fig[[y for y in range(fig.shape[0]) if y not in gone]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    d = build()
    info = f"{d.shape[1]} x {d.shape[0]}, {len({tuple(p[:3]) for p in d[d[..., 3] > 0]})} colours"
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, d) else "DIFFERENT", info)
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    Image.fromarray(d).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    main()
