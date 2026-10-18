#!/usr/bin/env python3
"""Akshan's slim design and Wukong's new design (tools/art/pack_redo_1018.py, delivered 2026-10-18) read back from Codex's
raw generations on their own grid, and shown at game size for the user to pick.

    python tools/art/design_redo_1018.py [--review OUT]

Codex's own exports (akshan-slim-<n>.png, wukong-redo-<n>.png) were its raw pictures nearest-sampled onto the asked 46 / 39
rows - squeezed sideways and full of stray squares - so they are not used. The raw pictures are clean pixel art on
10 px squares (regrid.py's guess, checked by eye at 4x), drawn bigger than asked: read back as they are (alpha at 128,
near-white background keyed out, colours brought to 40 by median cut, crumbs of at most 3 squares dropped)
-> assets/source/<hero>/hd/<name>.png. Their density in game: hair top to soles in rows / the game height (Akshan 38,
Wukong 32 = 38 x 85 %) = ORIG_PPU; ppu_restyle brings them to PPU 1.2 the way it brings every hero (pixel_down).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402
import pixel_down as PD  # noqa: E402
from review_urgot_ppu import frame0, shown  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source")
# name -> (hero, raw picture, square size, game px hair to soles)
TAKES = {
    "slim1": ("akshan", "codex_slim/akshan-slim-1-refined.png", 10, 38),
    "slim2": ("akshan", "codex_slim/akshan-slim-2-clean.png", 10, 38),
    "redo1": ("wukong", "codex_redo/wukong-redo-1-raw.png", 10, 32),
    "redo2": ("wukong", "codex_redo/wukong-redo-2-raw.png", 10, 32),
}
# hair top row in each read-back (the topknot / the hair tuft; not the gun, the staff or the tail) - read off the 8x view
HAIR = {"slim1": 16, "slim2": 14, "redo1": 2, "redo2": 4}
PEERS = {"akshan": ["kaisa", "jhin", "lucian", "akshan"], "wukong": ["leesin", "xinzhao", "jarvaniv", "wukong"]}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def read(path, size):
    a = np.asarray(Image.open(lp(path)).convert("RGBA")).astype(np.int64)
    op = (a[..., 3] >= 128) & ~(a[..., :3].min(-1) > 235)
    a[..., 3] = np.where(op, 255, 0)
    d, s, _ = RG.regrid(a.astype(np.uint8), size)
    d = d.astype(np.int64)
    op = d[..., 3] > 0
    # 40 colours by median cut over the figure (its commonest colours alone are all near-black outline shades)
    rgb = Image.fromarray(d[..., :3].astype(np.uint8))
    q = np.asarray(rgb.quantize(colors=40, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB"))
    d[op, :3] = q[op]
    lbl, k = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lbl, range(1, k + 1))
    for j, z in enumerate(sizes):
        if z <= 3:
            op[lbl == j + 1] = False
    d[~op] = 0
    d[..., 3] = np.where(op, 255, 0)
    ys, xs = np.nonzero(op)
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8), s


def hair_top(name):
    return HAIR.get(name, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", default="C:/t/ak_work/redo_review")
    a = ap.parse_args()
    os.makedirs(a.review, exist_ok=True)
    got = {}
    for name, (hero, raw, size, game) in TAKES.items():
        d, s = read(os.path.join(SRC, hero, raw), size)
        Image.fromarray(d).save(lp(os.path.join(SRC, hero, "hd", f"{name}.png")))
        top = hair_top(name)
        rows = d.shape[0] - top
        ppu = rows / game
        got[name] = (hero, d, ppu)
        print(f"{name}: {d.shape[1]} x {d.shape[0]} squares at {s} px; hair top row {top}, {rows} rows to the soles "
              f"-> {game} game px at PPU {ppu:.2f}")
        big = Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1))
        bg = Image.new("RGBA", big.size, (200, 200, 200, 255))
        bg.alpha_composite(big)
        dr = ImageDraw.Draw(bg)
        dr.line([(0, top * 8), (bg.width, top * 8)], fill=(40, 170, 60, 255), width=2)
        bg.convert("RGB").save(os.path.join(a.review, f"{name}_8x.png"))
    for hero in ("akshan", "wukong"):
        cells = []
        for name, (h, d, ppu) in got.items():
            if h != hero:
                continue
            for p in (round(ppu, 2), 1.2):
                if p == round(ppu, 2):
                    im = d
                else:
                    pv = (d.shape[1] / 2, d.shape[0] - 0.5)
                    im = PD.pixelate(d, p / ppu, pv, (12, 4, 8))[0]
                cells.append((f"{name} PPU {p}", shown(Image.fromarray(im), p, 4)))
        for peer in PEERS[hero]:
            im, p = frame0(peer)
            cells.append((f"{peer} now (PPU {p})", shown(im.crop(im.getbbox()), p, 4)))
        gap, top = 18, 22
        W = sum(c[1].width for c in cells) + gap * (len(cells) + 1)
        H = max(c[1].height for c in cells) + top + gap
        can = Image.new("RGB", (W, H), (96, 112, 96))
        dr = ImageDraw.Draw(can)
        x = gap
        for lab, im in cells:
            can.paste(im, (x, H - gap - im.height), im)
            dr.text((x, 4), lab, fill=(240, 240, 240))
            x += im.width + gap
        can.save(os.path.join(a.review, f"{hero}_choices.png"))
        print("written", hero)


if __name__ == "__main__":
    main()
