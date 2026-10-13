#!/usr/bin/env python3
"""Gragas's dense (PPU 2) frames: assets/source/ppu/gragas_<tag>.png, the strips tools/art/ppu_hd.py reads as drawn.

    python tools/art/ppu_gragas.py [--review DIR]

The user, 2026-10-12: 「用PPU的方法完成酒桶」, the route picked 「整套都用 PPU 原稿放大」 - the design's high-density
picture is Codex's raw draft (codex_model/raw/gragas-front-A-raw.png, read back as 71 x 86 squares), which the 1x design
was traced from 2:1 (tools/art/trace_gragas.py: table square (r, c) = raw squares (2r-1 .. 2r, 2c-1 .. 2c)); the actions
are the 1x frames doubled, with the raw's squares wherever a frame shows the design.
- idle (the design): every 1x square becomes the raw's 2 x 2 squares under it - unless the square was finished by hand
  (design/front.txt differs from front_auto.txt there: the face, the keg lid, the scar), then the square doubled; the
  silhouette stays the 1x one doubled (a raw square outside it is dropped, a clear raw square inside takes the 1x
  colour), so nothing sticks out and no hole opens.
- every other frame: its head is found (the design's head rows, the shift where most of its squares are the same);
  where the frame's squares equal the design's at that shift, in pieces of 4 squares or more, they become the idle's
  dense squares; everything else is the 1x square doubled. Frames whose head matches less than MIN_HEAD keep the 1x
  frame doubled (a turned or lying head: never a front face pasted on it).
Every dense frame is drawn SHIFT dense px lower (he is shown at SIZE on the battlefield, scaled about his position:
the soles stay on the ground). Writes one strip per tag (the frames left to right, 1 px apart, each exactly 2x its 1x frame), then
tools/art/import_native.py --hero gragas (or ppu_hd.py --hero gragas) puts them into the sheet's hd_ tags.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_hd as P  # noqa: E402
import trace_gragas as T  # noqa: E402

K = 2
MIN_HEAD = 0.6                   # share of the design head's squares a frame must hold to take the dense squares
PIECE = 4                        # smallest piece of equal squares that turns dense
# On the battlefield he is drawn at SIZE of the 1x size (addons/league_main/src/hd.rs SIZES: the user, 「酒桶模型缩小一点
# 太大了」, 85%, then 80%: 「怎么看起来还是比诺手高这么多」), scaled about his position, so every dense frame is drawn SHIFT dense px lower: the soles, 2 x 11.5 dense
# px under the pivot, land (23 + SHIFT) / 2 x SIZE = 11.5 under it again (SHIFT = 23 (1 / SIZE - 1) = 5.75).
SIZE = 0.80                       # the size these frames are drawn for; hd.rs SIZES is 1.00 since 2026-10-13 (ppu_restyle lifts them)
SHIFT = round(23 * (1 / SIZE - 1))
assert P.SHIFT.get("gragas") == SHIFT, "ppu_hd.SHIFT must match"
HEAD_ROWS, HEAD_COLS = (1, 11), (14, 30)   # the design's head in its table: the dome, brows, eyes, nose, moustache
OUT = os.path.join(ROOT, "assets", "source", "ppu", "orig")  # the dense frames as drawn; tools/art/ppu_restyle.py makes the strips ppu_hd.py reads from them (2026-10-13)


def dense_design():
    """The design table's dense picture, (2H, 2W): the raw's squares, the 1x silhouette, the hand-finished squares."""
    design = T.from_text(open(os.path.join(T.DESIGN, "front.txt")).read())
    auto = T.from_text(open(os.path.join(T.DESIGN, "front_auto.txt")).read())
    pal = T.np.array([[int(v[i:i + 2], 16) for i in (1, 3, 5)]
                      for v in __import__("json").load(open(os.path.join(T.DESIGN, "palette.json"))).values()], np.uint8)
    raw = T.read_back()
    H, W = design.shape
    one = T.rgba(design, pal)
    out = P.up(one, K)
    for r in range(H):
        for c in range(W):
            if design[r, c] < 0 or design[r, c] != auto[r, c]:
                continue
            for a in range(K):
                for b in range(K):
                    y, x = K * r + a - 1, K * c + b - 1
                    if 0 <= y < raw.shape[0] and 0 <= x < raw.shape[1] and raw[y, x, 3] > 0:
                        out[K * r + a, K * c + b] = raw[y, x]
    return one, out


def head_shift(frame, tpl, tm, base):
    """(share, dx, dy): where the frame holds the most of the design head's squares."""
    best = (0.0, 0, 0)
    H, W = frame.shape[:2]
    hy0, hx0 = base
    th, tw = tpl.shape[:2]
    for dy in range(-hy0, H - hy0 - th + 1):
        for dx in range(-hx0, W - hx0 - tw + 1):
            reg = frame[hy0 + dy:hy0 + dy + th, hx0 + dx:hx0 + dx + tw]
            s = ((np.abs(reg.astype(int) - tpl.astype(int)).max(2) == 0) & tm).sum() / tm.sum()
            if s > best[0]:
                best = (s, dx, dy)
    return best


def dense_frame(frame, one, dense, at, shift):
    """frame doubled, with the design's dense squares where its squares equal the design's at `shift`."""
    out = P.up(frame, K)
    dx, dy = shift
    oy, ox = at                                     # the design's top-left in the idle frame
    H, W = frame.shape[:2]
    same = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            r, c = y - dy - oy, x - dx - ox
            if 0 <= r < one.shape[0] and 0 <= c < one.shape[1] and frame[y, x, 3] > 0 and one[r, c, 3] > 0:
                same[y, x] = (frame[y, x] == one[r, c]).all()
    lab, n = ndimage.label(same)
    keep = np.isin(lab, [v for v, z in enumerate(ndimage.sum(same, lab, range(1, n + 1)), 1) if z >= PIECE])
    for y, x in zip(*np.nonzero(keep)):
        r, c = y - dy - oy, x - dx - ox
        out[K * y:K * y + K, K * x:K * x + K] = dense[K * r:K * r + K, K * c:K * c + K]
    return out, int(keep.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    sheet = P.read_sheet(os.path.join(P.MOD, "champions", "league_gragas"))
    one, dense = dense_design()
    idle = sheet["idle"][0][0]
    ys, xs = np.nonzero(idle[..., 3] > 0)
    at = (ys.min(), xs.min())
    assert (idle[at[0]:at[0] + one.shape[0], at[1]:at[1] + one.shape[1]] == one).all(), "the idle is not the design"
    tpl = one[HEAD_ROWS[0]:HEAD_ROWS[1], HEAD_COLS[0]:HEAD_COLS[1]]
    tm = tpl[..., 3] > 0
    base = (at[0] + HEAD_ROWS[0], at[1] + HEAD_COLS[0])
    for tag in [t for t in sheet if P.plain(t)]:
        frames = []
        notes = []
        for i, (f, _) in enumerate(sheet[tag]):
            share, dx, dy = head_shift(f, tpl, tm, base)
            if share < MIN_HEAD:
                frames.append(P.up(f, K))
                notes.append(f"{i + 1}:-")
                continue
            d, n = dense_frame(f, one, dense, at, (dx, dy))
            frames.append(d)
            notes.append(f"{i + 1}:{n}")
        moved = []
        for fr in frames:
            assert not fr[-SHIFT:, :, 3].any(), (tag, "no room under the soles to move the frame down")
            m = np.zeros_like(fr)
            m[SHIFT:] = fr[:-SHIFT]
            moved.append(m)
        frames = moved
        h = max(fr.shape[0] for fr in frames)
        w = sum(fr.shape[1] for fr in frames) + len(frames) - 1
        strip = np.zeros((h, w, 4), np.uint8)
        x = 0
        for fr in frames:
            strip[:fr.shape[0], x:x + fr.shape[1]] = fr
            x += fr.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(OUT, f"gragas_{tag}.png"))
        print(f"{tag:7s} dense squares per frame (- = the head not found, doubled): {' '.join(notes)}")


if __name__ == "__main__":
    main()
