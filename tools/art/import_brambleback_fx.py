#!/usr/bin/env python3
"""Import the Crimson Brambleback's effects (assets/source/brambleback/PROMPTS_FX.md: 9 pictures and 3 skill icons)
as the tft pack's sheets tft_brambleback_fx and tft_brambleback_big and its icons.

    python tools/art/import_brambleback_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/brambleback/codex_fx/brambleback_fx: pixel_1x/brambleback_fx_
<name>.png, one row of equal frames at game size, cell_1x and frames in manifest.json's assets; raw/ its drafts; 64 px
icons). Every frame is cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it (import_terra_fx.py's
way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked
symmetric left to right.
RECUT: Codex brought the claw's hit (a_hit) to its 18 x 16 cell with all the empty draft round it, so its flash came
out 2 squares and the claw marks 8 rows (the prompt's 12); it is cut again from its raw 4 x 1 draft: the box the four
frames' drawing shares, brought to the cell (each square the commonest colour of the delivered strip's palette among
its raw pixels, alpha by majority), its left half mirrored onto the right.
Anchors: the claw's hit on the body (the cell's middle, HIT); the pounce's ring is centred on the soles of the one it
lands on (also tft.dll's leap on to the next); the snare lies on the ground round the feet; the fear mark floats over
the head (OVER); the pictures round it - the roar's waves, the bark guard, the fury's burst and its blaze - stand on its
soles under the middle of its body (BODY); the burn stands on the burned unit's soles.
Icons: Codex's 64 px icons were its 1254 px tiles voted down into mud; brought to 64 x 64 again from the raw tiles with
LANCZOS (the Sohm, Terra and Sentinel way).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_brambleback_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "brambleback", "codex_fx", "brambleback_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
OVER = (0, -30)                 # over a unit's head
BODY = (0, 11)                  # under the middle of its body (its standing point: the design's middle), on its soles
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it
SIDE_CUT = {}
RECUT = {"a_hit": (4, 1)}       # name -> its raw draft's grid (columns, rows): cut again from the raw draft


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot" or a row, frames with ms, spots)
FX = {
    # Bramble Claw's rake
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Bramble Pounce: the ring under the one it lands on (tft.dll's leap on to the next too), the snare (q_slow_t 60)
    "q_hit": ("core", seq(range(6), [40, 50, 60, 70, 80, 90]), [SOLES]),
    "q_slow": ("core", loop(6, 100), [SOLES]),
    # Crimson Roar: the waves round it, the mark over the roared at, its bark guard (e_t 180 ticks)
    "e_cast": ("foot", seq(range(5), [60, 70, 80, 90, 100]), [BODY]),
    "e_slow": ("core", loop(6, 100), [OVER]),
    "e_guard": ("foot", loop(6, 120), [BODY]),
    # Crimson Fury: the burst, then the blaze for r_t
    "r_cast": ("foot", seq(range(6), [50, 60, 70, 80, 90, 110]), [BODY]),
    "r_fury": ("foot", loop(6, 100), [BODY]),
    # Red Buff's burn on the one it clawed (tft.dll)
    "p_burn": ("foot", loop(6, 100), [SOLES]),
}
ICONS = {"icon_skill": "tft_brambleback_skill", "icon_skill2": "tft_brambleback_skill2", "icon_ult": "tft_brambleback_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("brambleback_fx_"):-4]: e for e in json.load(f)["assets"] if e["file"].startswith("brambleback_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"brambleback_fx_{name}.png"))).convert("RGBA")).copy()
    if name in RECUT:
        a = recut(name, a, m[name]["cell_1x"], m[name]["frames"])
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    w, h = m[name]["cell_1x"]
    if a.shape[0] != h or a.shape[1] != w * m[name]["frames"]:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {m[name]['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(m[name]["frames"])]
    for c in out:   # bits of a neighbour at the cell's sides
        op = c[..., 3] > 0
        lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            part = lb == j
            side = part[:, :EDGE_STRIP].any() or part[:, -EDGE_STRIP:].any()
            thin = np.ptp(np.nonzero(part.any(0))[0]) < EDGE_STRIP   # a sliver of the next cell standing at the side
            if side and (part.sum() < EDGE_SPECK or thin):
                c[part] = 0
    for (fx, k), cols in SIDE_CUT.items():
        if fx != name:
            continue
        c = out[k]
        lb, n = ndimage.label(c[..., 3] > 0, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            xs = np.nonzero((lb == j).any(0))[0]
            if xs.max() < cols or xs.min() >= c.shape[1] - cols:
                c[lb == j] = 0
    for k, c in enumerate(out):
        flip = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == flip).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric " + ("top to bottom" if name in FLYING else "left to right"))
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def recut(name, strip, cell, frames):
    """An effect cut again from its raw draft (RECUT[name] columns x rows of frames, read row by row): the box every
    frame's drawing shares, brought to `cell`, each square the commonest colour of the delivered strip's palette among
    its raw pixels (alpha by majority), the left half mirrored onto the right. -> a new strip like `strip`."""
    cols, rows = RECUT[name]
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"brambleback_fx_{name}.png"))).convert("RGBA"))
    ch, cw = raw.shape[0] // rows, raw.shape[1] // cols
    tiles = [raw[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw] for k in range(frames)]
    boxes = [np.nonzero(t[..., 3] >= 128) for t in tiles]
    y0 = min(b[0].min() for b in boxes)
    y1 = max(b[0].max() for b in boxes) + 1
    xc = cw / 2                                          # the drafts are drawn round each tile's middle
    half = max(max(abs(b[1].min() - xc), abs(b[1].max() + 1 - xc)) for b in boxes)
    w, h = cell
    k_ = max(2 * half / w, (y1 - y0) / h)                # raw px a square, the same both ways
    n = max(1, int(k_))
    pal = np.unique(strip[strip[..., 3] >= 128][:, :3], axis=0).astype(float)
    out = np.zeros((h, w * frames, 4), np.uint8)
    for f, t in enumerate(tiles):
        for j in range(h):
            for i in range(w):
                ya, xa = int(y1 - (h - j) * k_), int(xc - w / 2 * k_ + i * k_)
                win = t[max(0, ya):max(0, ya) + n, max(0, xa):max(0, xa) + n].reshape(-1, 4)
                if len(win) == 0:
                    continue
                on = win[win[:, 3] >= 128]
                if len(on) * 2 < len(win):
                    continue
                idx = np.argmin(((on[:, None, :3].astype(float) - pal[None]) ** 2).sum(-1), axis=1)
                out[j, f * w + i, :3] = pal[np.bincount(idx).argmax()]
                out[j, f * w + i, 3] = 255
        c = out[:, f * w:(f + 1) * w]
        c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]     # left half onto the right
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "foot":
        return [(w - 1) / 2, h - 1]
    return [(w - 1) / 2, kind]


def icon(name):
    """Codex's raw 1254 px icon tile -> 64 x 64 (LANCZOS): its own 64 px cut voted 2 x 2 blocks into mud."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"brambleback_{name}.png"))).convert("RGB")
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    tables = {"tft_brambleback_fx": {}, "tft_brambleback_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_brambleback_big" if tag in BIG else "tft_brambleback_fx"][tag] = out
        print(f"{tag:13s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        icon(src).save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")
    if a.review:
        Z = 6
        rows = []
        for name, cs in allc.items():
            W = sum(c.shape[1] + 2 for c in cs)
            H = max(c.shape[0] for c in cs)
            img = Image.new("RGBA", (W * Z, H * Z), (40, 40, 52, 255))
            x = 0
            for c in cs:
                img.alpha_composite(Image.fromarray(c).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST),
                                    (x * Z, (H - c.shape[0]) * Z))
                x += c.shape[1] + 2
            rows.append(img)
        sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
        y = 0
        for r in rows:
            sheet.alpha_composite(r, (0, y))
            y += r.height + 8
        sheet.convert("RGB").save(a.review)
        print(a.review)


if __name__ == "__main__":
    main()
