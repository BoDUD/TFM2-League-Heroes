#!/usr/bin/env python3
"""Norra's delivered effects made right where they came out wrong, before import_norra_fx.py reads them
(the fix-delivered-art-myself rule: clean it in code, no redo round trip).

    python tools/art/process_norra_fx.py [--check]     # writes assets/source/norra/fx_1x/norra_fx_<name>.png

The delivery (assets/source/norra/codex_fx/norra_fx, Codex 2026-10-26/new-chat-5) holds each effect as a one-row strip
at game size (pixel_1x/), read by Codex from its drafts (raw/) frame by frame: the draft cell's visible box (alpha 192
and over) fitted into a box in the game cell (manifest.json frame_details: source_cell, source_visible_bbox,
normalization_rect_1x), every game square the commonest palette colour of the draft pixels under it where 15% or more
are drawn, then mirrored. Two came out wrong:
  r_book   the visible boxes held the drafts' soft yellow glow and stray sparks, so the gate and the page inside them
           came out small (the gate 21 squares across, the page 9: under the 54-wide warning ring on the ground). Read
           again the same way from raw/ with every box SCALE times bigger about the cell's bottom middle (the landing
           point stays on the ground line), the cell grown to hold them.
  e_anvil_hit  frame 7 (the gate closing over the landed anvil) was fitted into a box twice as tall as the anvil's
           other frames, so the anvil grew to 14 x 22 squares there and shrank back in frame 8: rebuilt from frame 8 (the
           anvil and the dust on the ground) under frame 4's gate (the gate as it was before the anvil fell).
  e_guard  came as a rounded rectangle round the unit (a card frame rather than a shield): its border mapped onto an
           elliptic ring the same size (oval(): Codex's colours, the gold clasps and the sparkles kept).
Everything else is copied as delivered. Each output is checked symmetric the way manifest.json says.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_norra_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "norra", "codex_fx", "norra_fx")
OUT = os.path.join(ROOT, "assets", "source", "norra", "fx_1x")
SCALE = {"r_book": 1.4}
ALPHA, COVER = 192, 0.15


def manifest():
    m = json.load(open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8"))
    return {it["id"]: it for it in m["items"]}


def palette(it):
    return np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in it["palette"]], np.int32)


def strip(it):
    a = np.asarray(Image.open(lp(os.path.join(SRC, it["pixel_1x"]))).convert("RGBA")).copy()
    w, h = it["cell_1x"]
    return [a[:h, k * w:(k + 1) * w].copy() for k in range(it["frames"])]


def mirror(c, sym):
    """Codex's per-frame mirror: the fuller half copied over the other (left-right, or top-bottom for a projectile)."""
    c = c.copy()
    if sym in ("left-right", "both"):
        w = c.shape[1]
        L, R = c[:, :w // 2], c[:, (w + 1) // 2:]
        if (L[..., 3] > 0).sum() >= (R[..., 3] > 0).sum():
            c[:, (w + 1) // 2:] = L[:, ::-1]
        else:
            c[:, :w // 2] = R[:, ::-1]
    if sym in ("top-bottom", "both"):
        h = c.shape[0]
        T, B = c[:h // 2], c[(h + 1) // 2:]
        if (T[..., 3] > 0).sum() >= (B[..., 3] > 0).sum():
            c[(h + 1) // 2:] = T[::-1]
        else:
            c[:h // 2] = B[::-1]
    return c


def symmetric(c, sym):
    lr = (c == c[:, ::-1]).all()
    tb = (c == c[::-1]).all()
    return {"left-right": lr, "top-bottom": tb, "both": lr and tb}[sym]


def reread(it, k):
    """Every frame read again from raw/ the way the delivery was, its box k times bigger about the cell's bottom middle
    -> (frames, the new cell size)."""
    raw = np.asarray(Image.open(lp(os.path.join(SRC, it["raw"]))).convert("RGBA")).astype(np.int32)
    pal = palette(it)
    cw, ch = it["cell_1x"]
    boxes = []
    for f in it["frame_details"]:
        rx, ry, rw, rh = f["normalization_rect_1x"]
        nx = cw / 2 + (rx - cw / 2) * k
        ny = ch + (ry - ch) * k
        boxes.append((nx, ny, rw * k, rh * k))
    x0 = min(b[0] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes)
    y0 = min(b[1] for b in boxes)
    half = max(cw / 2 - x0, x1 - cw / 2)
    W = int(np.ceil(2 * half)) + 2
    H = int(np.ceil(ch - y0)) + 2
    W += (W - cw) % 2                                   # the same parity as the delivered cell: the middle stays put
    out = []
    for f, (nx, ny, nw, nh) in zip(it["frame_details"], boxes):
        sx, sy, sw, sh = f["source_cell"]
        vb = f["source_visible_bbox"]
        src = raw[sy + vb["y0"]:sy + vb["y1"], sx + vb["x0"]:sx + vb["x1"]]
        op = src[..., 3] >= ALPHA
        rgb = src[..., :3]
        idx = np.argmin(((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1), -1)
        ox, oy = nx + (W - cw) / 2, ny + (H - ch)
        cell = np.zeros((H, W, 4), np.uint8)
        gx0, gx1 = int(np.floor(ox)), int(np.ceil(ox + nw))
        gy0, gy1 = int(np.floor(oy)), int(np.ceil(oy + nh))
        for gy in range(max(0, gy0), min(H, gy1)):
            ya = int(round((gy - oy) / nh * src.shape[0]))
            yb = int(round((gy + 1 - oy) / nh * src.shape[0]))
            ya, yb = max(0, ya), min(src.shape[0], yb)
            if yb <= ya:
                continue
            for gx in range(max(0, gx0), min(W, gx1)):
                xa = int(round((gx - ox) / nw * src.shape[1]))
                xb = int(round((gx + 1 - ox) / nw * src.shape[1]))
                xa, xb = max(0, xa), min(src.shape[1], xb)
                if xb <= xa:
                    continue
                m = op[ya:yb, xa:xb]
                if m.mean() < COVER:
                    continue
                ids, n = np.unique(idx[ya:yb, xa:xb][m], return_counts=True)
                cell[gy, gx, :3] = pal[ids[n.argmax()]]
                cell[gy, gx, 3] = 255
        out.append(mirror(cell, it["symmetry"]))
    return out, (W, H)


def anvil_frame7(frames):
    """Frame 7 rebuilt: frame 8 (the anvil and the dust on the ground) under frame 4's gate (rows above the anvil)."""
    f4, f8 = frames[3], frames[7]
    rows4 = np.nonzero(f4[..., 3].any(1))[0]
    # frame 4's gate: its rows down to the first fully clear row under the top blob
    gap = [y for y in range(rows4[0], f4.shape[0]) if not f4[y, :, 3].any()]
    gate_end = gap[0] if gap else rows4[0] + 8
    out = f8.copy()
    gate = f4[:gate_end]
    m = gate[..., 3] > 0
    out[:gate_end][m] = gate[m]
    return out


def oval(c, ring=2.6):
    """e_guard's frame from a rounded rectangle to a bubble: an elliptic ring as wide and tall as the frame, each of
    its squares coloured from the rectangle's border where a ray from the middle at the same angle meets it, as deep
    into the border as the square lies in the ring (Codex's colours, gold clasps and sparkles kept; only the shape
    changes). Left-right symmetric because the source is."""
    H, W = c.shape[:2]
    op = c[..., 3] > 0
    cx, cy = (W - 1) / 2, (H - 1) / 2
    a, b = W / 2, H / 2
    cols = np.nonzero(op.any(0))[0]
    rows = np.nonzero(op.any(1))[0]
    # the source border's depth: how many squares in from the left edge the first row through the middle is drawn
    mid = op[int(round(cy))]
    depth = int(np.argmin(mid[cols[0]:])) or 3
    out = np.zeros_like(c)
    for y in range(H):
        for x in range(W):
            u, v = (x - cx) / a, (y - cy) / b
            r = np.hypot(u, v)
            if r > 1.0 or r < 1.0 - ring / min(a, b) * 1.15:
                continue
            k = (1.0 - r) / (ring / min(a, b) * 1.15)            # 0 outer edge .. 1 inner edge of the ring
            m = max(abs(u), abs(v)) or 1e-9
            # where the ray hits the rectangle's outer edge, then `k` of the border depth inward along the ray
            ex = cx + (u / m) * (cols[-1] - cx)
            ey = cy + (v / m) * (rows[-1] - cy)
            dx, dy = ex - cx, ey - cy
            n = np.hypot(dx, dy) or 1e-9
            sx = int(round(ex - dx / n * k * (depth - 1)))
            sy = int(round(ey - dy / n * k * (depth - 1)))
            sx, sy = min(max(sx, 0), W - 1), min(max(sy, 0), H - 1)
            if op[sy, sx]:
                out[y, x] = c[sy, sx]
            else:                                                 # a gap in the border: its nearest drawn square
                ys, xs = np.nonzero(op)
                j = np.argmin((ys - sy) ** 2 + (xs - sx) ** 2)
                out[y, x] = c[ys[j], xs[j]]
    return mirror(out, "left-right")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="read r_book again at 1x and compare with the delivery")
    a = ap.parse_args()
    man = manifest()
    if a.check:
        it = man["r_book"]
        mine, size = reread(it, 1.0)
        theirs = strip(it)
        for k, (m, t) in enumerate(zip(mine, theirs)):
            h, w = min(m.shape[0], t.shape[0]), min(m.shape[1], t.shape[1])
            same = ((m[:h, :w, 3] > 0) == (t[:h, :w, 3] > 0)).mean()
            print(f"frame {k + 1}: shapes {m.shape[:2]} / {t.shape[:2]}, opaque agree {same:.3f}, "
                  f"opaque {int((m[..., 3] > 0).sum())} / {int((t[..., 3] > 0).sum())}")
        return
    os.makedirs(lp(OUT), exist_ok=True)
    report = {}
    for name, it in man.items():
        frames = strip(it)
        size = tuple(it["cell_1x"])
        if name in SCALE:
            frames, size = reread(it, SCALE[name])
        if name == "e_anvil_hit":
            frames[6] = anvil_frame7(frames)
        if name == "e_guard":
            frames = [oval(c) for c in frames]
        for k, c in enumerate(frames):
            if not symmetric(c, it["symmetry"]):
                sys.exit(f"{name} frame {k + 1} is not {it['symmetry']} symmetric")
            if not c[..., 3].any():
                sys.exit(f"{name} frame {k + 1} is empty")
        sheet = np.concatenate(frames, axis=1)
        Image.fromarray(sheet).save(lp(os.path.join(OUT, f"norra_fx_{name}.png")))
        report[name] = dict(it, cell_1x=list(size), pixel_1x=f"norra_fx_{name}.png")
        print(f"{name:12s} {len(frames)} x {size[0]}x{size[1]}" + ("  (read again x%.2f)" % SCALE[name]
                                                              if name in SCALE else ""))
    with open(lp(os.path.join(OUT, "manifest.json")), "w", encoding="utf-8") as f:
        json.dump({"items": list(report.values())}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
