#!/usr/bin/env python3
"""Rek'Sai's step-0 pictures at game size: A (the surface idle) at several heights, PPU 1.5 (the user's, 2026-10-17),
B (burrowed) at A's scale, next to the pack's junglers as the game shows them, for the user's pick of the height.

    python tools/art/review_reksai_size.py --out DIR [--heights 36,40,44] [--ppu 1.5] [--scale 4]

Step 0 (assets/source/reksai/codex_picture, 2026-10-17, Codex 2026-10-17/new-chat): A and B on 1254 squares; asked for
66 squares of 11 px, Codex drew squares of ~8 px (A) and ~7.5 px (B), A 137 x 160 squares, B 89 x 152, B's crest drawn
~1.16x A's (its HANDOFF: no exact grid or scale, soft edges). Both are needed (A the body, B the burrowed body), so B
is brought to A's scale by the crest: the opaque width of the top CREST_BAND of each picture's rows. Each picture
(alpha >= 128) is brought to PPU x height squares from the crest top to the claw tips by an alpha-weighted box shrink and
a 40-colour palette, then shown 1 / PPU game pixels a square. The neighbours: their battlefield idles (hd_idle / PPU, or
the 1x idle), the same scale, feet on one line. Writes <out>/reksai_size_ppu.png and reksai_AB_<h>px_6x.png.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_varus as V  # noqa: E402
import ppu_hd  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "reksai", "codex_picture")
CHAMPS = os.path.join(ROOT, "league", "champions")
NEIGHBOURS = ["darius", "xinzhao", "vi", "khazix", "rengar", "nidalee", "hecarim", "rell"]
CREST_BAND = 0.22   # top share of A's rows that hold only the crest
BG = (196, 200, 190, 255)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def picture(name):
    """Read back one pixel per drawn square (regrid's own measure), alpha 0 / 255."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"reksai-{name}.png"))).convert("RGBA")).copy()
    a, _, _ = RG.regrid(a)
    op = a[..., 3] >= 128
    a[..., 3] = np.where(op, 255, 0)
    ys, xs = np.nonzero(op)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


COLOURS = 40


def shrink(d, k, pal):
    """Area mean (colour weighted by alpha), clear under half cover, every square snapped to the pictures' palette.
    pixel_down.pixelate's near-black rule turned the whole figure black here: Codex's lines are ~1 square in ~4."""
    w, h = max(1, round(d.shape[1] * k)), max(1, round(d.shape[0] * k))
    f = d.astype(np.float64)
    al = f[..., 3:] / 255.0
    pre = np.concatenate([f[..., :3] * al, al * 255], axis=2).astype(np.float32)
    small = np.stack([np.asarray(Image.fromarray(pre[..., c]).resize((w, h), Image.BOX)) for c in range(4)], axis=2)
    a = small[..., 3] / 255.0
    rgb = small[..., :3] / np.maximum(a[..., None], 1e-6)
    op = a >= 0.5
    dist = ((rgb[:, :, None, :] - pal[None, None, :, :].astype(np.float64)) ** 2).sum(-1)
    out = np.zeros((h, w, 4), np.uint8)
    out[op, :3] = pal[dist.argmin(-1)][op]
    out[op, 3] = 255
    return Image.fromarray(out)


def frame0(hero):
    stem = os.path.join(CHAMPS, f"league_{hero}")
    anims = json.load(open(lp(stem + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    ppu = ppu_hd.PPU.get(hero)
    tag = "hd_idle" if ppu and "hd_idle" in anims else "idle"
    f = anims[tag]["frames"][0]["data"]
    sheet = Image.open(lp(stem + "#sheet.png")).convert("RGBA")
    im = sheet.crop((int(f["x"]), int(f["y"]), int(f["x"] + f["w"]), int(f["y"] + f["h"])))
    return im.crop(im.getbbox()), (ppu if tag == "hd_idle" else 1.0)


def shown(im, ppu, scale):
    """`im` drawn at `ppu` squares a game pixel -> screen pixels at `scale` a game pixel (nearest)."""
    k = scale / ppu
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.NEAREST)


def crest(d):
    """Opaque width of the crest band (the top CREST_BAND of A's height, in squares from each picture's top)."""
    band = round(CREST_BAND * 137)
    cols = np.nonzero((d[:band, :, 3] > 0).any(axis=0))[0]
    return cols.max() - cols.min() + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--heights", default="36,40,44")
    ap.add_argument("--ppu", type=float, default=1.5)
    ap.add_argument("--scale", type=int, default=4)
    a = ap.parse_args()
    A, B = picture("A"), picture("B")
    both = np.concatenate([A[:min(A.shape[0], B.shape[0])], B[:min(A.shape[0], B.shape[0])]], axis=1)
    _, pal = V.kmeans(both, COLOURS)
    cells = []
    for h in [int(x) for x in a.heights.split(",")]:
        k = a.ppu * h / A.shape[0]
        for name, d in (("A", A), ("B", B)):
            kk = k * crest(A) / crest(d)       # B at A's scale: the same crest
            im = shrink(d, kk, pal)
            im = im.crop(im.getbbox())
            cells.append((f"{name} {h} px", shown(im, a.ppu, a.scale), im))
    for hero in NEIGHBOURS:
        im, p = frame0(hero)
        cells.append((f"{hero} {round(im.height / p)} px", shown(im, p, a.scale), None))
    gap, top = 16, 22
    W = sum(c[1].width for c in cells) + gap * (len(cells) + 1)
    H = max(c[1].height for c in cells) + top + gap
    can = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(can)
    x = gap
    for label, im, _ in cells:
        can.alpha_composite(im, (x, H - gap - im.height))
        dr.text((x, 4), label, fill=(30, 30, 30, 255))
        x += im.width + gap
    dr.line([(0, H - gap), (W, H - gap)], fill=(120, 120, 120, 255))
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "reksai_size_ppu.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)
    # the two designs side by side at 8x one height (46 px), to judge the details the game size keeps
    mid = [int(x) for x in a.heights.split(",")][len(a.heights.split(",")) // 2]
    pair = [c[2] for c in cells if c[2] is not None and c[0].endswith(f" {mid} px")]
    if pair:
        w = sum(p.width for p in pair) + 8 * (len(pair) + 1)
        h = max(p.height for p in pair) + 16
        sheet = Image.new("RGBA", (w, h), BG)
        x = 8
        for p in pair:
            sheet.alpha_composite(p, (x, h - 8 - p.height))
            x += p.width + 8
        sheet = sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST)
        path = os.path.join(a.out, f"reksai_AB_{mid}px_6x.png")
        sheet.convert("RGB").save(lp(path))
        print(path, sheet.size)


if __name__ == "__main__":
    main()
