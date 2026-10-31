#!/usr/bin/env python3
"""Import the Crimson Raptor's effects (assets/source/raptor/PROMPTS_FX.md: 10 pictures and 3 skill icons) as the tft
pack's sheets tft_raptor_fx and tft_raptor_big and its icons.

    python tools/art/import_raptor_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/raptor/codex_fx/raptor_fx: pixel_1x/raptor_fx_<name>.png, one
row of equal frames at game size, cell_1x, frames and its raw drafts' layout (columns, rows) in manifest.json; raw/ its
drafts; 64 px icons). Every frame is cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it
(import_sentinel_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it.
Every picture is checked symmetric (left to right; the flying ones top to bottom, pointing right: they turn with their
flight).
RECUT: the flying feathers were asked too small (a_bolt 14 x 6, q_feather 20 x 8, r_peck 12 x 6): Codex's fine feathers
voted down into blobs. They are cut again from their raw 2 x 2 drafts into the bigger cells RECUT gives (each frame round its own drawing, each square the
commonest colour of the delivered strip's palette among its raw pixels, alpha by majority, the top half mirrored onto
the bottom); the feather's hit (a_hit) likewise into a 16 x 16 cell (its last frame's shards
stood alone at the sides of Codex's cut). The flock (r_flock): Codex's chicks are 18-20 of its own ~5 px squares in the
raw, but its 84 x 44 cut kept
them 4-6 squares; read again from the raw 3 x 2 draft at RECUT's 9.5 raw px a square (each chick about 11 squares), the
left half mirrored onto the right.
Anchors: the hits on the struck body (the cell's middle, HIT); the cracked-armour mark floats over the head (OVER);
the frenzy rush and the flock stand on its soles under the middle of its body (BODY: the design's middle is 3 game px
behind its standing point); the take-off puff lies on the ground where it stood (SOLES); the feathers and pecks fly on
their own point (FLY).
Icons: Codex's 64 px icons were its 1254 px tiles voted down 2 x 2 into mud; brought to 64 x 64 again from the raw
tiles with LANCZOS (the Sohm, Terra and Sentinel way).
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
import pack_raptor_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "raptor", "codex_fx", "raptor_fx")
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
BODY = (-3, 11)                 # under the middle of its body (3 game px behind its standing point), on its soles
FLY = (0, 0)                    # a projectile's own point
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it
EDGE_KEEP = {"r_peck_hit"}      # its fluff drifts out to the cell's sides on purpose
# name -> the cell (game px) to cut again from the raw draft, and raw px a square (None: the frames' shared box fitted)
RECUT = {"a_bolt": ((18, 7), None), "q_feather": ((26, 10), None), "r_peck": ((16, 8), None),
         "r_flock": ((76, 40), 9.5), "a_hit": ((16, 16), None)}
SPREAD = {"r_flock": 4}         # each half moved this many game px outward after the recut (the right pair stood on its
                                # face): the cell grows by twice that


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot" or a row, frames with ms, spots)
FX = {
    # Feather Shot: the feather in flight, its hit
    "a_bolt": ("core", loop(4, 60), [FLY]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Feather Fan: the blade feathers in flight (tft.dll's fan), their slash
    "q_feather": ("core", loop(4, 60), [FLY]),
    "q_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Flock Family: the four Tiny Beaks round it (r_t 420 ticks), a chick's dive, its peck
    "r_flock": ("foot", loop(6, 110), [BODY]),
    "r_peck": ("core", loop(4, 60), [FLY]),
    "r_peck_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Startled Hop: the puff it hops from, the frenzy round it (e_t 180 ticks)
    "e_jump": ("foot", seq(range(5), [50, 60, 70, 80, 90]), [SOLES]),
    "e_rush": ("foot", loop(6, 90), [BODY]),
    # Orange Buff: the cracked armour over a shredded enemy
    "p_shred": ("core", loop(6, 100), [OVER]),
}
ICONS = {"icon_skill": "tft_raptor_skill", "icon_skill2": "tft_raptor_skill2", "icon_ult": "tft_raptor_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("raptor_fx_"):-4]: e for e in json.load(f) if e["file"].startswith("raptor_fx_")}


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"raptor_fx_{name}.png"))).convert("RGBA")).copy()
    w, h = m[name]["cell_1x"]
    if name in RECUT:
        a = recut(name, a, m[name])
        w, h = RECUT[name][0]
    if name in SPREAD:
        a, w = spread(a, w, m[name]["frames"], SPREAD[name]), w + 2 * SPREAD[name]
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    if a.shape[0] != h or a.shape[1] != w * m[name]["frames"]:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {m[name]['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(m[name]["frames"])]
    for c in ([] if name in EDGE_KEEP else out):   # bits of a neighbour at the cell's sides
        op = c[..., 3] > 0
        lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
        for j in range(1, n + 1):
            part = lb == j
            side = part[:, :EDGE_STRIP].any() or part[:, -EDGE_STRIP:].any()
            thin = np.ptp(np.nonzero(part.any(0))[0]) < EDGE_STRIP
            if side and (part.sum() < EDGE_SPECK or thin):
                c[part] = 0
    for k, c in enumerate(out):
        flip = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == flip).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric " + ("top to bottom" if name in FLYING else "left to right"))
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def recut(name, strip, e):
    """An effect cut again from its raw draft (manifest source_layout columns x rows of frames, read row by row) into
    RECUT[name]'s cell: the flying ones each centred on its own drawing (Codex drew them at different places in their
    tiles) at the scale that fits the largest; the rest mirrored about the tile's middle column, standing on the
    drawings' lowest row, fitted to the box they share (or at RECUT's fixed raw px a square: the flock); each square
    the commonest colour of the delivered strip's palette among its raw pixels (alpha by majority), the symmetric half
    mirrored. -> a new strip."""
    (w, h), k_fixed = RECUT[name]
    cols, rows = e["source_layout"]
    frames = e["frames"]
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"raptor_fx_{name}.png"))).convert("RGBA"))
    ch, cw = raw.shape[0] // rows, raw.shape[1] // cols
    tiles = [raw[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw] for k in range(frames)]
    boxes = [np.nonzero(t[..., 3] >= 128) for t in tiles]
    fly = name in FLYING
    if fly:   # pointing right, each frame round its own middle
        k_ = k_fixed or max(max((np.ptp(b[1]) + 1) / w, (np.ptp(b[0]) + 1) / h) for b in boxes)
        org = [((b[1].min() + b[1].max() + 1) / 2 - w / 2 * k_, (b[0].min() + b[0].max() + 1) / 2 - h / 2 * k_)
               for b in boxes]
    else:     # mirrored about the tile's middle column, standing on the lowest drawn row
        xc = cw / 2
        y1 = max(b[0].max() for b in boxes) + 1
        half = max(max(abs(b[1].min() - xc), abs(b[1].max() + 1 - xc)) for b in boxes)
        y0 = min(b[0].min() for b in boxes)
        k_ = k_fixed or max(2 * half / w, (y1 - y0) / h)
        org = [(xc - w / 2 * k_, y1 - h * k_)] * frames
    n = max(1, int(k_))
    pal = np.unique(strip[strip[..., 3] >= 128][:, :3], axis=0).astype(float)
    out = np.zeros((h, w * frames, 4), np.uint8)
    for f, t in enumerate(tiles):
        ox, oy = org[f]
        for j in range(h):
            for i in range(w):
                ya, xa = int(oy + j * k_), int(ox + i * k_)
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
        if fly:
            c[h - h // 2:] = c[:h // 2][::-1]          # top half onto the bottom
        else:
            c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]  # left half onto the right
    return out


def spread(strip, w, frames, k):
    """Each frame's left half moved k columns left and its right half k right (a strip of cells w + 2k wide)."""
    h = strip.shape[0]
    out = np.zeros((h, (w + 2 * k) * frames, 4), np.uint8)
    for f in range(frames):
        c = strip[:, f * w:(f + 1) * w]
        o = out[:, f * (w + 2 * k):(f + 1) * (w + 2 * k)]
        o[:, :w // 2] = c[:, :w // 2]
        o[:, w // 2 + 2 * k:] = c[:, w // 2:]
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
    im = Image.open(lp(os.path.join(SRC, "raw", f"raptor_{name}.png"))).convert("RGB")
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    tables = {"tft_raptor_fx": {}, "tft_raptor_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_raptor_big" if tag in BIG else "tft_raptor_fx"][tag] = out
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
