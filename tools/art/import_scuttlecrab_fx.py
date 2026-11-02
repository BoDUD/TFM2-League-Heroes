#!/usr/bin/env python3
"""Import the Scuttle Crab's effects (assets/source/scuttlecrab/PROMPTS_FX.md: 10 pictures and 3 skill icons) as the tft
pack's sheets tft_scuttlecrab_fx and tft_scuttlecrab_big and its icons.

    python tools/art/import_scuttlecrab_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/scuttlecrab/codex_fx/scuttle_fx: pixel_1x/scuttle_fx_<name>.png,
one row of equal frames at game size; manifest.json "assets": frames, cell_1x and source_layout, the rows and columns
of its raw draft's frames; raw/<name>-original.png its drafts; 64 px icons). Codex's pixel_1x read each draft by the
majority of every square at a scale fitted to the asked cell: the splash's droplets and its star, the heal's leaves and
cross, the knock-up's clods and the thin haste and wet-ground streaks fell under the majority (a_hit kept 14 specks). So the effects in RECUT are read again
from the raw drafts here, at one scale for x and y (RECUT[name] raw px a square, a little bigger than asked so they
read): the draft's grid of frames cut at its row_cuts and at the widest empty column round each column's share, each
frame about its own middle column, standing on the lowest row any frame reaches, a square drawn where at least COVER of
its raw pixels are, in the commonest colour of Codex's palette (every pixel_1x colour) among them, the left half
mirrored (meepsie's way). The rest are cut from pixel_1x as delivered.
Every frame is placed as the kit plays it (import_raptor_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it. Every picture is checked symmetric (left to right; the shrine also top to bottom:
a zone's picture turns with the cast).
Anchors: the splash on the struck body (HIT); the heal, the haste, the wet ground and the knock-up's clods stand on a
unit's soles (SOLES); the shrine's ring is centred on the ground under it (SOLES, "core": a CasterViewEffect where
it was cast, never turned); the shell
dome, its burst and the burst out of the earth stand on its soles under the middle of its body (BODY: the design's middle
is a game px ahead of its standing point); the earth mound lies on the ground round it, a little under its soles (DIG).
Icons: from the raw tiles with LANCZOS (meepsie's way).
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
import pack_scuttlecrab_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "scuttlecrab", "codex_fx", "scuttle_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
BODY = (1, 11)                  # under the middle of its body (a game px ahead of its standing point), on its soles
DIG = (1, 13)                   # the earth mound: its lowest row 2 game px under its soles
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it
EDGE_KEEP = {"q_shrine", "e_shell", "e_burst", "r_dig", "r_burst", "q_haste", "e_slow"}   # rings, shards and earth run
                                # out to the cell's sides on purpose
COVER = 0.3                     # the share of a square's raw pixels that draws it
RECUT = {"a_hit": 30, "p_heal": 18, "r_up": 18, "q_haste": 29, "e_slow": 33}   # name -> raw px a square (x and y)


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot" or a row, frames with ms, spots)
FX = {
    # Crab Dance: the splash on each one stomped
    "a_hit": ("core", seq(range(4), [50, 60, 70, 60]), [HIT]),
    # Green Buff (tft.dll plays it on the ally healed)
    "p_heal": ("foot", seq(range(5), [70, 90, 110, 120, 130]), [SOLES]),
    # Speed Shrine: the ring for the zone's life (a CasterViewEffect plays its tag once: six loops of 110 ms = 3.96 s of
    # q_t's 4 s), the haste on the allies in it
    "q_shrine": ("core", seq(list(range(6)) * 6, [110] * 36), [SOLES]),
    "q_haste": ("foot", loop(6, 90), [SOLES]),
    # Shell Shield: the dome while the shield holds, the burst (tft.dll), the wet ground on the slowed
    "e_shell": ("foot", loop(6, 110), [BODY]),
    "e_burst": ("foot", seq(range(5), [60, 80, 100, 110, 130]), [BODY]),
    "e_slow": ("foot", loop(6, 100), [SOLES]),
    # Can You Dig It?: digging in (2 frames) and the mound for the rest of the burrow (r_t 150 ticks = 2.5 s: 3-8 looped
    # three times over), the burst out, the clods under the knocked up
    "r_dig": ("foot", seq([0, 1] + [2, 3, 4, 5, 6, 7] * 3, [120, 140] + [124] * 18), [DIG]),
    "r_burst": ("foot", seq(range(6), [60, 80, 100, 110, 120, 130]), [BODY]),
    "r_up": ("foot", seq(range(5), [70, 90, 110, 120, 130]), [SOLES]),
}
ICONS = {"skill": "tft_scuttlecrab_skill", "skill2": "tft_scuttlecrab_skill2", "ult": "tft_scuttlecrab_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        effects = json.load(f)["assets"]
    return {e["file"][len("scuttle_fx_"):-4]: e for e in effects if e["file"].startswith("scuttle_fx_")}


def palette():
    """Every colour of Codex's pixel_1x strips (its readback of the four ramps)."""
    cols = []
    for name in FX:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"scuttle_fx_{name}.png"))).convert("RGBA"))
        cols.append(a[a[..., 3] >= 128][:, :3])
    return np.unique(np.concatenate(cols), axis=0).astype(float)


def grid_tiles(raw, layout, n):
    """The draft's frames, row-major: its row bands at row_cuts, each band split into `columns` at the widest empty run
    of columns round each share."""
    tiles = []
    cuts = layout["row_cuts"]
    for r in range(layout["rows"]):
        band = raw[cuts[r]:cuts[r + 1]]
        empty = ~(band[..., 3] >= 128).any(0)
        W, cols = band.shape[1], layout["columns"]
        xs = [0]
        for c in range(1, cols):
            want = W * c // cols
            best, x = None, max(0, want - W // 6)
            while x < min(W, want + W // 6):
                if empty[x]:
                    x1 = x
                    while x1 < W and empty[x1]:
                        x1 += 1
                    if best is None or x1 - x > best[1] - best[0]:
                        best = (x, x1)
                    x = x1
                else:
                    x += 1
            xs.append((best[0] + best[1]) // 2 if best else want)
        xs.append(W)
        tiles += [band[:, xs[c]:xs[c + 1]] for c in range(cols)]
    return [t for t in tiles if (t[..., 3] >= 128).any()][:n]


def recut(name, e, pal):
    """The frames read again from the raw draft at RECUT[name] raw px a square -> a strip of equal cells."""
    k = RECUT[name]
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"{name}-original.png"))).convert("RGBA"))
    fly = False
    tiles = grid_tiles(raw, e["source_layout"], e["frames"])
    if len(tiles) != e["frames"]:
        sys.exit(f"{name}: {len(tiles)} frames in the draft for {e['frames']}")
    boxes = [np.nonzero(t[..., 3] >= 128) for t in tiles]
    if fly:   # each frame round its own middle, pointing right
        w = int(np.ceil(max(np.ptp(b[1]) + 1 for b in boxes) / k)) + 2
        h = int(np.ceil(max(np.ptp(b[0]) + 1 for b in boxes) / k)) + 2
        org = [((b[1].min() + b[1].max() + 1) / 2 - w / 2 * k, (b[0].min() + b[0].max() + 1) / 2 - h / 2 * k)
               for b in boxes]
    else:     # each frame about its own middle column, all standing on the lowest drawn row
        y1 = max(b[0].max() for b in boxes) + 1
        y0 = min(b[0].min() for b in boxes)
        w = int(np.ceil(max(np.ptp(b[1]) + 1 for b in boxes) / k)) + 2
        w += w % 2
        h = int(np.ceil((y1 - y0) / k)) + 1
        org = [((b[1].min() + b[1].max() + 1) / 2 - w / 2 * k, y1 - h * k) for b in boxes]
    out = np.zeros((h, w * len(tiles), 4), np.uint8)
    for f, t in enumerate(tiles):
        ox, oy = org[f]
        for j in range(h):
            for i in range(w):
                ya, yb = int(round(oy + j * k)), int(round(oy + (j + 1) * k))
                xa, xb = int(round(ox + i * k)), int(round(ox + (i + 1) * k))
                win = t[max(0, ya):max(0, yb), max(0, xa):max(0, xb)].reshape(-1, 4)
                if len(win) == 0:
                    continue
                on = win[win[:, 3] >= 128]
                if len(on) < COVER * (yb - ya) * (xb - xa):
                    continue
                idx = np.argmin(((on[:, None, :3].astype(float) - pal[None]) ** 2).sum(-1), axis=1)
                out[j, f * w + i, :3] = pal[np.bincount(idx).argmax()]
                out[j, f * w + i, 3] = 255
        c = out[:, f * w:(f + 1) * w]
        if fly:
            c[h - h // 2:] = c[:h // 2][::-1]          # top half onto the bottom
        else:
            c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]  # left half onto the right
    return out, (w, h)


def cells(name, m, pal):
    """The frames of an effect, symmetry checked."""
    if name in RECUT:
        a, (w, h) = recut(name, m[name], pal)
    else:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"scuttle_fx_{name}.png"))).convert("RGBA")).copy()
        w, h = m[name]["cell_1x"]
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
        if not (c == c[:, ::-1]).all() or (name in PK.BOTH and not (c == c[::-1]).all()):
            sys.exit(f"{name} frame {k + 1} is not symmetric")
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    if kind == "foot":
        return [(w - 1) / 2, h - 1]
    return [(w - 1) / 2, kind]


def icon(name):
    """Codex's raw icon tile -> 64 x 64 (LANCZOS): its own 64 px cut voted 2 x 2 blocks into mud. The raw tiles sit on
    a white, grey or black page with corner gems sticking out of the frame: cut to the frame first (the rows and columns
    more than half coloured), or the page shows at the corners."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"{name}-original.png"))).convert("RGB")
    a = np.asarray(im).astype(int)
    on = (a.max(-1) - a.min(-1)) > 40
    xs, ys = np.nonzero(on.mean(0) > 0.5)[0], np.nonzero(on.mean(1) > 0.5)[0]
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    pal = palette()
    allc = {n: cells(n, m, pal) for n in FX}
    tables = {"tft_scuttlecrab_fx": {}, "tft_scuttlecrab_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_scuttlecrab_big" if tag in BIG else "tft_scuttlecrab_fx"][tag] = out
        print(f"{tag:8s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}" + ("  (raw recut)" if tag in RECUT else ""))
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
