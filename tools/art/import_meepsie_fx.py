#!/usr/bin/env python3
"""Import Meepsie's effects (assets/source/meepsie/PROMPTS_FX.md: 9 pictures and 3 skill icons) as the tft pack's
sheets tft_meepsie_fx and tft_meepsie_big and its icons.

    python tools/art/import_meepsie_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/meepsie/codex_fx/meepsie_fx: pixel_1x/meepsie_fx_<name>.png, one
row of equal frames at game size; manifest.json "effects": frames, cell_1x and source_splits_x, the columns where its
raw draft's frames part; raw/ its drafts; 64 px icons). Codex's pixel_1x read each draft by the majority of every
square at a scale fitted to the asked cell, x and y apart: the meeps, the stars, the leaves and the ribbons of the thin
effects fell under the majority and were lost (e_cast kept a dotted outline, r_up two brackets), and q_wave came out
squashed to a third of its height. So the effects in RECUT are read again from the raw drafts here, at one scale for
x and y (RECUT[name] raw px a square): each frame centred on its own drawing (the left-right ones about their middle
column, standing on the lowest row any frame reaches; the flying ones about their middle row), a square drawn where at
least COVER of its raw pixels are, in the commonest colour of Codex's palette (every pixel_1x colour) among them, the
author half mirrored. The rest (q_slow, r_slam) are cut from pixel_1x as delivered (import_elderdragon_fx's way).
Every frame is placed as the kit plays it (import_raptor_fx.py's way): spots are game px from the pivot (x forward, y
down); a unit's soles are 11 under it. Every picture is checked symmetric (left to right; the flying wave and meep
top to bottom, pointing right: they turn with their flight).
Anchors: the punch's moon dust on the struck body (HIT); the quake's jolt, the drag, the mending glow and the knock-up's
stars stand on a unit's soles (SOLES); the meeps popping out stand on its soles under the middle of its body (BODY: the
design's middle is 2 game px ahead of its standing point); the Big Bang lies on the ground where it landed, its lower
edge a little under its soles (SLAM); the meep flies on its own point (FLY); the dust wave is drawn on its picture-only
line's middle (WAVE: the kit's q_len is twice the distance from the pivot to the wave's middle, its left end at the
fist that hits the ground in q_smash, 24 game px ahead).
Icons: Codex's 64 px icons are its raw tiles voted down 2 x 2; brought to 64 x 64 again from the raw tiles with LANCZOS
(the Sohm, Terra, Sentinel, Raptor and Elder Dragon way).
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
import pack_meepsie_fx as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "meepsie", "codex_fx", "meepsie_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
SOLES = (0, 11)                 # on the ground under a unit
BODY = (2, 11)                  # under the middle of its body (2 game px ahead of its standing point), on its soles
SLAM = (2, 14)                  # the Big Bang's ring: its lower edge 3 game px under its soles
FLY = (0, 0)                    # a projectile's own point
WAVE = (0, 0)                   # the dust wave on its line's middle, on the ground line
FIST = 24                       # q_smash's fist on the ground, game px ahead of the pivot: the wave's left end
seq = J.seq
EDGE_SPECK = 6                  # parts touching a cell's side smaller than this are dropped
EDGE_STRIP = 3                  # and parts within this many columns of a side and narrower than it
EDGE_KEEP = {"e_cast", "r_slam", "e_hot", "r_up", "q_wave", "e_meep"}   # meeps, rings, ribbons and trails run out to
                                # the cell's sides on purpose
COVER = 0.3                     # the share of a square's raw pixels that draws it
# name -> raw px a square (one scale for x and y), the draft (raw/meepsie_fx_<file>.png)
RECUT = {"a_hit": (26, "a_hit"), "q_wave": (8.6, "q_wave"), "q_hit": (18, "q_hit"), "e_cast": (7, "e_cast-revision"),
         "e_meep": (24, "e_meep"), "e_hot": (12, "e_hot"), "r_up": (14, "r_up")}


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot" or a row, frames with ms, spots)
FX = {
    # Moon-Rock Punch + the pilot's zap: the moon dust and the violet star on the struck
    "a_hit": ("core", seq(range(4), [50, 60, 70, 60]), [HIT]),
    # Moon-Dust Quake: the wave along its picture-only line, the jolt on each one struck, the drag (q_slow_t 120 ticks)
    "q_wave": ("core", loop(6, 60), [WAVE]),
    "q_hit": ("foot", seq(range(4), [60, 80, 100, 100]), [SOLES]),
    "q_slow": ("foot", loop(6, 100), [SOLES]),
    # Healing Meeps: the meeps popping out of it, a meep flying to an ally (tft.dll's homing projectile), the mending glow
    # (e_t 180 ticks)
    "e_cast": ("foot", seq(range(5), [70, 80, 90, 100, 110]), [BODY]),
    "e_meep": ("core", loop(4, 80), [FLY]),
    "e_hot": ("foot", loop(6, 100), [SOLES]),
    # The Big Bang: the blast where it lands, the stars round the knocked up (tft.dll's view)
    "r_slam": ("foot", seq(range(6), [60, 80, 100, 120, 120, 140]), [SLAM]),
    "r_up": ("foot", seq(range(5), [70, 90, 110, 120, 130]), [SOLES]),
}
ICONS = {"icon_skill": "tft_meepsie_skill", "icon_skill2": "tft_meepsie_skill2", "icon_ult": "tft_meepsie_ult"}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        effects = json.load(f)["effects"]
    return {e["file"][len("meepsie_fx_"):-4]: e for e in effects if e["file"].startswith("meepsie_fx_")}


def palette():
    """Every colour of Codex's pixel_1x strips (its readback of the four ramps, the meeps' dark eyes)."""
    cols = []
    for name in FX:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"meepsie_fx_{name}.png"))).convert("RGBA"))
        cols.append(a[a[..., 3] >= 128][:, :3])
    return np.unique(np.concatenate(cols), axis=0).astype(float)


def recut(name, e, pal):
    """The frames read again from the raw draft at RECUT[name] raw px a square -> a strip of equal cells."""
    k, file = RECUT[name]
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"meepsie_fx_{file}.png"))).convert("RGBA"))
    xs = e["source_splits_x"]
    fly = name in FLYING
    tiles = [raw[:, xs[f]:xs[f + 1]] for f in range(e["frames"])]
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
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"meepsie_fx_{name}.png"))).convert("RGBA")).copy()
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
    if kind == "foot":
        return [(w - 1) / 2, h - 1]
    return [(w - 1) / 2, kind]


def icon(name):
    """Codex's raw icon tile -> 64 x 64 (LANCZOS): its own 64 px cut voted 2 x 2 blocks into mud. The raw tiles sit on
    a white, grey or black page with corner gems sticking out of the frame: cut to the frame first (the rows and columns
    more than half coloured), or the page shows at the corners."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"meepsie_{name}.png"))).convert("RGB")
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
    print(f"q_wave {allc['q_wave'][0].shape[1]} game px long: the kit's q_len = 2 x ({FIST} + its half) = "
          f"{2 * (FIST + allc['q_wave'][0].shape[1] // 2) * 1000}")
    tables = {"tft_meepsie_fx": {}, "tft_meepsie_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        anc = anchor(cs, kind)
        out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms) for k, ms in frames]
        tables["tft_meepsie_big" if tag in BIG else "tft_meepsie_fx"][tag] = out
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
