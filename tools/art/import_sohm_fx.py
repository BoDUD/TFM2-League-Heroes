#!/usr/bin/env python3
"""Import Sohm's effects (assets/source/sohm/PROMPTS_FX.md: 11 pictures and 3 skill icons) as the tft pack's sheets
tft_sohm_fx and tft_sohm_big and its icons.

    python tools/art/import_sohm_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/sohm/codex_fx/sohm_fx: pixel_1x/sohm_fx_<name>.png, one row of
equal frames at game size, cell_1x and frames in manifest.json; raw/ the drawings they came from, 3 to 14 px a square;
64 px icons). Every frame is cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit plays it
(import_daeja_fx.py's way): spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it.
Every picture is checked left-right symmetric, the three that fly (FLYING: the water bolt, the wave, the flower bud
jumping on) top-bottom: they point right and the game turns them with their flight.
Two taken again from the raw drawings (2026-10-30):
  r_bloom   Codex's 40 x 40 cells, but the bloom bursts r_r 32000 round each flower (a 64-px circle): read again from
            raw/sohm_fx_r_bloom.png (4 x 2 cells of 444 px, drawn at ~5 px squares) at BLOOM px - each cell's square
            blocks' median colour where most of the block is drawn, snapped to the colours of Codex's own 1x bloom, made
            left-right symmetric (the fuller half), lone squares dropped;
  icons     Codex's 64 px icons were brought down from 1254 px tiles drawn at ~10 px squares into a blur of single
            squares: the tiles brought to 64 x 64 again with LANCZOS (tft_violet's / Shi Oh Yu's way).
SPECKS: the bloom's last frame carried two loose dashes at its top (the cut of the frame drawn over it) - parts of a
frame touching its top or a side smaller than EDGE_PART squares go, and so do parts smaller than SPECK squares lying away
from the rest (more than SPECK_GAP squares from it).
Anchors: the hits on the body (the cell's middle, HIT); the flower floats over the flowered one's head (FLOWER); the
ripple at her chest, the shield bubble round the shielded one's body (BODY); the bloom and her tide stand on the
soles (the cell's bottom); the flying ones on the projectile's own point.
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
import pack_sohm_fx as PK  # noqa: E402
import pixel_down as PD  # noqa: E402
from clean_skarner_fx import despeckle, symmetric  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sohm", "codex_fx", "sohm_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
BODY = (0, -8)                  # the middle of a unit's body (the shield's bubble, the ripple at her chest)
FLOWER = (0, -36)               # over a unit's head
SOLES = (0, 11)                 # on the ground under a unit
FLY = (0, 0)                    # a projectile's own point
BLOOM = 64                      # the bloom's cell (game px): r_r 32000 round the flower
KEEP = 0.5                      # a bloom square is drawn when this share of its block is
SPECK, SPECK_GAP = 4, 3
EDGE_PART = 12                  # parts touching the cell's top or a side smaller than this: a neighbour's cut
seq = J.seq


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core" or "foot", frames with ms, spots)
FX = {
    # Water Bolt: the bolt in flight, its splash on the target
    "a_bolt": ("core", loop(4, 60), [FLY]),
    "a_hit": ("core", seq(range(4), [40, 50, 50, 60]), [HIT]),
    # Tideblossom: the wave flying through, the splash on each one it passes, the water flower over the marked one's
    # head (a buff: while the mark lasts), the bud jumping on when the marked one falls
    "q_wave": ("core", loop(6, 70), [FLY]),
    "q_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_flower": ("core", loop(6, 110), [FLOWER]),
    "q_jump": ("core", loop(4, 60), [FLY]),
    # Tidecaller's Guard: the ripple at her claws as she pushes, the bubble round the shielded ally (e_sh_t)
    "e": ("core", seq(range(5), [40, 50, 60, 70, 80]), [BODY]),
    "e_shield": ("core", loop(6, 100), [BODY]),
    # Tidal Bloom: the lotus bursting on each flower, the petals' splash on each one caught
    "r_bloom": ("foot", seq(range(7), [50, 60, 70, 90, 80, 80, 90]), [SOLES]),
    "r_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Lagoon: her tide behind her (a buff: while she has stacks)
    "p_glow": ("foot", loop(6, 100), [SOLES]),
}
ICONS = {"icon_skill": "tft_sohm_skill", "icon_skill2": "tft_sohm_skill2", "icon_ult": "tft_sohm_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {e["file"][len("sohm_fx_"):-4]: e for e in json.load(f) if e["file"].startswith("sohm_fx_")}


def unspeck(c):
    """Parts smaller than SPECK squares lying more than SPECK_GAP squares from the rest of the frame go."""
    op = c[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    if n < 2:
        return c
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        part = lb == j
        edge = part[0].any() or part[:, 0].any() or part[:, -1].any()
        if edge and sizes[j - 1] < EDGE_PART:
            c[part] = 0
            continue
        if sizes[j - 1] >= SPECK:
            continue
        rest = op & (lb != j)
        near = ndimage.binary_dilation(lb == j, iterations=SPECK_GAP)
        if not (near & rest).any():
            c[lb == j] = 0
    return c


def bloom(m):
    """The bloom read again from Codex's raw drawing at BLOOM x BLOOM (see the module's note)."""
    e = m["r_bloom"]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", "sohm_fx_r_bloom.png"))).convert("RGBA")).astype(float)
    cols, rows = e["source_layout"]
    cw, ch = a.shape[1] / cols, a.shape[0] / rows
    x0, y0, x1, y1 = e["source_common_crop"]
    ref = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", "sohm_fx_r_bloom.png"))).convert("RGBA"))
    pal = np.unique(ref[ref[..., 3] > 0][:, :3], axis=0).astype(float)
    lab_p = PD._lab(pal)
    out = []
    for k in range(e["frames"]):
        cx, cy = (k % cols) * cw, (k // cols) * ch
        sub = a[int(cy + y0):int(cy + y1), int(cx + x0):int(cx + x1)]
        bh, bw = sub.shape[0] / BLOOM, sub.shape[1] / BLOOM
        c = np.zeros((BLOOM, BLOOM, 4), np.uint8)
        for j in range(BLOOM):
            for i in range(BLOOM):
                blk = sub[int(j * bh):int((j + 1) * bh), int(i * bw):int((i + 1) * bw)].reshape(-1, 4)
                on = blk[:, 3] >= 160
                if on.mean() < KEEP:
                    continue
                rgb = np.median(blk[on][:, :3], axis=0)
                c[j, i, :3] = pal[np.argmin(((PD._lab(rgb[None]) - lab_p) ** 2).sum(-1))]
                c[j, i, 3] = 255
        out.append(despeckle(symmetric(c, {})))
    return out


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    if name == "r_bloom":
        out = bloom(m)
    else:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"sohm_fx_{name}.png"))).convert("RGBA")).copy()
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
        a[a[..., 3] == 0] = 0
        w, h = m[name]["cell_1x"]
        if a.shape[0] != h or a.shape[1] != w * m[name]["frames"]:
            sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {m[name]['frames']} cells of {w}x{h}")
        out = [a[:, k * w:(k + 1) * w].copy() for k in range(m[name]["frames"])]
    out = [unspeck(c) for c in out]
    for k, c in enumerate(out):
        flip = c[::-1] if name in FLYING else c[:, ::-1]
        if not (c == flip).all():
            sys.exit(f"{name} frame {k + 1} is not symmetric " + ("top to bottom" if name in FLYING else "left to right"))
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1]


def icon(name):
    """Codex's raw 1254 px icon tile -> 64 x 64 (LANCZOS)."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"sohm_{name}.png"))).convert("RGB")
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    tables = {"tft_sohm_fx": {}, "tft_sohm_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_sohm_big" if tag in BIG else "tft_sohm_fx"][tag] = out
        print(f"{tag:10s} {cs[0].shape[1]}x{cs[0].shape[0]}, anchor {anc}")
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
        icons = Image.new("RGBA", (3 * 64 * 4 + 16, 64 * 4), (40, 40, 52, 255))
        for k, src in enumerate(ICONS):
            icons.alpha_composite(icon(src).resize((256, 256), Image.NEAREST), (k * (256 + 8), 0))
        rows.append(icons)
        sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 8 for r in rows)), (24, 24, 30, 255))
        y = 0
        for r in rows:
            sheet.alpha_composite(r, (0, y))
            y += r.height + 8
        sheet.convert("RGB").save(a.review)
        print(a.review)


if __name__ == "__main__":
    main()
