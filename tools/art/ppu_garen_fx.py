#!/usr/bin/env python3
"""Garen's effects at PPU 2.5: `hd_<tag>` beside every tag of his effect sheets, read from the original pictures.

    python tools/art/ppu_garen_fx.py                 # write the hd tags into league/effects/league_garen_*
    python tools/art/ppu_garen_fx.py --review DIR    # garen_fx_<sprite>_<tag>.gif + garen_fx_frames.png (1x | hd)

The user, 2026-10-12 (branch ppu-rebuild, after Garen's idle): 「导入特效吧」 = the effects redone dense from the
original pictures (assets/source/garen/garen_fx_*.png). tools/art/import_garen.py made the 1x effects from them (its
FX table: strip, frames, scale, anchor rule, pivot-relative spot, timing - the 1x sheets are still exactly its
output); here the same pictures, anchors and spots at 2.5 x the scale, so an hd frame is the 1x frame 2.5 times as
fine about the same pivot: round(2.5 x its 1x size), grown alike at both ends where the finer drawing reaches a
little further. One palette per sheet (48 colours, effects have no outline). league_garen_sym (the E whirl, left-right
symmetric for the red side: tools/fix/mirror_union_fx.py) gets hd_spin = each hd loop frame over its mirror image.
league.dll draws a registered effect sheet's hd tags (addons/league_main/src/hd.rs EFFECTS).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "fix"))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import import_garen as I  # noqa: E402
import mirror_union_fx as M  # noqa: E402
import ppu_hd  # noqa: E402
import strips as G  # noqa: E402

PPU = 2.5
PREFIX = "hd_"
COLOURS = 48
MOD = os.path.join(ROOT, "league", "effects")
SYM = {"league_garen_sym": {"spin": ("league_garen_spin", "loop")}}   # sym tag: (source sheet, tag)


def frame_size(w, h, art):
    """round(PPU x the 1x size), grown by 2 at a time (alike at both ends) until `art` (rows, cols) fits."""
    W, H = ppu_hd.hd_size(w, h, PPU)
    need_w, need_h = art
    while W < need_w:
        W += 2
    while H < need_h:
        H += 2
    return W, H


def place(arr, u0, r0, W, H):
    """A render() array (pixel u's middle at u from the pivot) in a W x H frame whose pivot is its middle."""
    out = np.zeros((H, W, 4), np.uint8)
    ys, xs = np.nonzero(arr[..., 3])
    X = xs + u0 + W // 2
    Y = ys + r0 + H // 2
    if X.min() < 0 or Y.min() < 0 or X.max() >= W or Y.max() >= H:
        return None
    out[Y, X] = arr[ys, xs]
    return out


def build(sprite, one):
    """{tag: [(hd frame, ms)]} of an import_garen.FX sprite, frame for frame with its 1x sheet `one`."""
    raw = {}
    for tag, (strip, n, (sx, sy), rule, (X0, Y0), ms, cut) in I.FX[sprite].items():
        frames = G.split_strip(G.load_rgba(I.src(strip)), n, blob_thresh=0.05)
        out = []
        for i, (f, (ax, ay)) in enumerate(zip(frames, rule(frames))):
            w, h = one[tag][i][0].shape[1], one[tag][i][0].shape[0]
            W, H = ppu_hd.hd_size(w, h, PPU)
            # the pivot sits at the frame's middle: on a pixel's middle for an odd size, between two for an even one
            ox, oy = (W % 2) * 0.5 - 0.5, (H % 2) * 0.5 - 0.5
            arr, u0, r0 = G.render(f, sx * PPU, sy * PPU, ax, ay, X0 * PPU + ox, Y0 * PPU + oy, cut=cut, keep=0.9)
            out.append((arr, u0, r0, (w, h), one[tag][i][1]))
        raw[tag] = out
    pal = G.Palette([r[0] for rs in raw.values() for r in rs], colors=COLOURS, extra=())
    tags = {}
    for tag, rs in raw.items():
        fr = []
        for arr, u0, r0, (w, h), ms in rs:
            arr = pal.apply(arr)
            ys, xs = np.nonzero(arr[..., 3])
            # the art's reach from the pivot, both ways: the frame must hold it symmetric about the middle
            reach_x = 2 * max(-(xs.min() + u0), xs.max() + u0) + 2
            reach_y = 2 * max(-(ys.min() + r0), ys.max() + r0) + 2
            W, H = frame_size(w, h, (reach_x, reach_y))
            f = place(arr, u0, r0, W, H)
            while f is None:
                W, H = W + 2, H + 2
                f = place(arr, u0, r0, W, H)
            fr.append((f, ms))
        tags[tag] = fr
    return tags


def sym(dense):
    """hd tags of the left-right symmetric sheets: every source hd frame over its mirror image, all one size."""
    out = {}
    for sheet, tags in SYM.items():
        out[sheet] = {}
        for tag, (src, src_tag) in tags.items():
            frames = dense[src][src_tag]
            W = max(f.shape[1] for f, _ in frames)
            H = max(f.shape[0] for f, _ in frames)
            fr = []
            for f, ms in frames:
                c = np.zeros((H, W, 4), np.uint8)
                y, x = (H - f.shape[0]) // 2, (W - f.shape[1]) // 2
                c[y:y + f.shape[0], x:x + f.shape[1]] = f
                fr.append((M.union(c), ms))
            out[sheet][tag] = fr
    return out


def dense_all():
    one = {s: ppu_hd.read_sheet(os.path.join(MOD, s)) for s in list(I.FX) + list(SYM)}
    dense = {s: build(s, one[s]) for s in I.FX}
    dense.update(sym(dense))
    return one, dense


def write(one, dense):
    for sheet, tags in dense.items():
        plain = {t: fr for t, fr in one[sheet].items() if not t.startswith(PREFIX)}
        for t in tags:
            if t not in plain:
                sys.exit(f"{sheet}: hd_{t} has no 1x {t}")
        allt = dict(plain)
        allt.update({PREFIX + t: fr for t, fr in tags.items()})
        w, h = G.write_sheet(os.path.join(MOD, sheet), allt)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(f"{PREFIX}{t} {len(v)}f" for t, v in tags.items()))


def review(one, dense, out_dir):
    """Per tag a GIF, the 1x frame (x5) beside the hd one (x2): the same size on screen."""
    os.makedirs(out_dir, exist_ok=True)
    bg = (60, 66, 58, 255)
    rows = []
    for sheet, tags in dense.items():
        for tag, fr in tags.items():
            ones = one[sheet][tag]
            W = max(max(a.shape[1] * 5 for a, _ in ones), max(f.shape[1] * 2 for f, _ in fr))
            H = max(max(a.shape[0] * 5 for a, _ in ones), max(f.shape[0] * 2 for f, _ in fr))
            pics = []
            for (a, ms), (f, _) in zip(ones, fr):
                c = Image.new("RGBA", (2 * W + 30, H + 20), bg)
                for k, (img, z, x0) in enumerate(((a, 5, 10), (f, 2, W + 20))):
                    big = Image.fromarray(img).resize((img.shape[1] * z, img.shape[0] * z), Image.NEAREST)
                    c.alpha_composite(big, (x0 + (W - big.width) // 2, 10 + (H - big.height) // 2))
                pics.append(c.convert("RGB"))
            pics[0].save(os.path.join(out_dir, f"garen_fx_{sheet[len('league_garen_'):]}_{tag}.gif"), save_all=True,
                         append_images=pics[1:], duration=[int(round(ms)) for _, ms in ones], loop=0)
            rows.append(pics)
    print("review:", out_dir)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write review GIFs here (nothing written to the sheets)")
    args = ap.parse_args()
    one, dense = dense_all()
    for sheet, tags in dense.items():
        for t, fr in tags.items():
            print(sheet, t, [f.shape[1::-1] for f, _ in fr], "1x", [a.shape[1::-1] for a, _ in one[sheet][t]])
    if args.review:
        review(one, dense, args.review)
    else:
        write(one, dense)


if __name__ == "__main__":
    main()
