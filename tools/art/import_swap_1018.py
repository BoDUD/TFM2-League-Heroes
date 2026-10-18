#!/usr/bin/env python3
"""Codex's skin-swap action sheets (tools/art/pack_swap_1018.py) read back frame by frame.

    python tools/art/import_swap_1018.py akshan [--review DIR]

Codex delivered each action on the skeleton's own layout (up to 4 cells a row, cell sizes as in the pack's sheets.txt),
5 px a square aligned to the sheet's corner, the colours already brought to the design's palette, the background #00FF00.
Each cell is cut, the key removed, read at 5 px -> assets/source/<hero>/hd/act/<tag>_<i>.png (trimmed, soles on the bottom
row). Enclosed key-green specks of at most 2 squares (eyes Codex drew in the key's green) are filled with the darkest colour next
to them. A review sheet (every frame at 6x, rows per tag) and per-frame stats (height, hair-top row, width) are written.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pack_swap_1018 import PACKS, PADC  # noqa: E402

DELIVERY = {"akshan": "C:/Users/OWNER/Documents/Codex/2026-10-18/new-chat-14/outputs/akshan-actions",
            "wukong": "C:/Users/OWNER/Documents/Codex/2026-10-18/new-chat-16/outputs/wukong-actions"}
SQ = 5
# enclosed key-green specks: Akshan's eyes (dark - filled from the darkest neighbour), Wukong's glowing green eyes
EYE = {"wukong": (70, 215, 90)}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def is_key(a):
    return (a[..., 1] > 200) & (a[..., 0] < 80) & (a[..., 2] < 80)


def cells(path, n, eye=None):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)
    H, W = a.shape[:2]
    cols = min(4, n)
    rows = (n + cols - 1) // cols
    cw, ch = W // cols, H // rows
    out = []
    for i in range(n):
        y0, x0 = (i // cols) * ch, (i % cols) * cw
        c = a[y0:y0 + ch, x0:x0 + cw]
        sm = c[SQ // 2::SQ, SQ // 2::SQ]           # one sample in the middle of each 5 px square
        key = is_key(sm)
        fig = ~key
        lbl, k = ndimage.label(fig, structure=np.ones((3, 3)))
        if k == 0:
            continue
        sizes = ndimage.sum(fig, lbl, range(1, k + 1))
        keep = np.isin(lbl, [j + 1 for j, s in enumerate(sizes) if s > 6])
        holes = ndimage.binary_fill_holes(keep) & key
        hl, hk = ndimage.label(holes)
        hs = ndimage.sum(holes, hl, range(1, hk + 1))
        holes = np.isin(hl, [j + 1 for j, z in enumerate(hs) if z <= 2])     # eyes; real gaps between limbs stay clear
        rgba = np.zeros(sm.shape[:2] + (4,), np.uint8)
        rgba[keep, :3] = sm[keep]
        rgba[keep, 3] = 255
        if holes.any() and eye is not None:
            rgba[holes, :3] = eye
            rgba[holes, 3] = 255
        elif holes.any():
            for y, x in zip(*np.nonzero(holes)):
                nb = rgba[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
                nb = nb[nb[:, 3] > 0]
                if len(nb):
                    rgba[y, x] = nb[np.argmin(nb[:, :3].astype(int).sum(1))]
        # the key's fringe: greenish squares that are not the eye colour - on the figure's edge cleared, inside it
        # given the darkest neighbour's colour
        c3 = rgba[..., :3].astype(int)
        fr_ = (rgba[..., 3] > 0) & (c3[..., 1] > c3[..., 0] + 60) & (c3[..., 1] > c3[..., 2] + 60)
        if eye is not None:
            fr_ &= np.abs(c3 - np.array(eye)).sum(-1) > 0
        for _ in range(3):
            if not fr_.any():
                break
            clear = rgba[..., 3] == 0
            edge = fr_ & ndimage.binary_dilation(clear, structure=np.ones((3, 3)))
            rgba[edge] = 0
            fr_ &= ~edge
        for y, x in zip(*np.nonzero(fr_)):
            nb = rgba[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
            nb = nb[(nb[:, 3] > 0) & ~((nb[:, 1].astype(int) > nb[:, 0].astype(int) + 60) & (nb[:, 1].astype(int) > nb[:, 2].astype(int) + 60))]
            if len(nb):
                rgba[y, x] = nb[np.argmin(nb[:, :3].astype(int).sum(1))]
        ys, xs = np.nonzero(rgba[..., 3])
        out.append((rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1], int(holes.sum())))
    return out


def frame_count(cfg, tag):
    for line in open(os.path.join("C:/t/ak_work/swap", cfg["pack"], "sheets.txt"), encoding="utf-8"):
        if line.startswith(tag + ":"):
            return int(line.split(":")[1].split()[0])
    raise SystemExit(f"{tag} not in sheets.txt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero", choices=list(DELIVERY))
    ap.add_argument("--review", default="C:/t/ak_work/swap_review")
    a = ap.parse_args()
    cfg = PACKS[a.hero]
    dst = os.path.join(ROOT, "assets", "source", a.hero, "hd", "act")
    os.makedirs(lp(dst), exist_ok=True)
    os.makedirs(a.review, exist_ok=True)
    rows, stats = [], {}
    for tag in cfg["tags"]:
        n = frame_count(cfg, tag)
        fr = cells(os.path.join(DELIVERY[a.hero], f"{a.hero}-{tag}.png"), n, EYE.get(a.hero))
        if tag == "hit":
            fr = fr[:1]                 # Lucian's second hit frame is a white silhouette (the game's flash)
        stats[tag] = []
        for i, (f, holes) in enumerate(fr):
            Image.fromarray(f).save(lp(os.path.join(dst, f"{tag}_{i}.png")))
            stats[tag].append(dict(h=f.shape[0], w=f.shape[1], holes=holes))
        H = max(f.shape[0] for f, _ in fr)
        W = sum(f.shape[1] + 4 for f, _ in fr) + 70
        row = Image.new("RGBA", (W, H + 4), (200, 210, 200, 255))
        ImageDraw.Draw(row).text((2, 2), tag, fill=(0, 0, 0, 255))
        x = 70
        for f, _ in fr:
            row.alpha_composite(Image.fromarray(f), (x, 2 + H - f.shape[0]))
            x += f.shape[1] + 4
        rows.append(row)
        print(tag, [(s["h"], s["w"], s["holes"]) for s in stats[tag]])
    W = max(r.width for r in rows)
    can = Image.new("RGB", (W, sum(r.height for r in rows)), (255, 255, 255))
    y = 0
    for r in rows:
        can.paste(r.convert("RGB"), (0, y))
        y += r.height
    can.resize((can.width * 4, can.height * 4), Image.NEAREST).save(os.path.join(a.review, f"{a.hero}_frames.png"))
    json.dump(stats, open(os.path.join(a.review, f"{a.hero}_stats.json"), "w"))


if __name__ == "__main__":
    main()
