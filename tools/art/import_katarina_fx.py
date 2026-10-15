#!/usr/bin/env python3
"""Katarina's effects from Codex's step-3 delivery (assets/source/katarina/codex_fx, from katarina_fx_pack_done.zip) as
the game sheets league_katarina_fx / league_katarina_big, and the pictures drawn into her frames
(assets/source/katarina/fx_bake, laid onto her restyled dense frames by tools/art/rig_katarina.py --pinholes).

    python tools/art/import_katarina_fx.py --prepare <delivery dir>   (once: copies what the import reads)
    python tools/art/import_katarina_fx.py [--review DIR]

import_jayce_fx.py's way: Codex's read-backs (pixel_1x/katarina_fx_<name>.png, the cells listed in manifest.json) used as
they are; each frame trimmed to its drawn box and placed by an anchor on a spot (FX):
  "mid"    the box's middle on the spot (hits on a unit, the spinning blade);
  "front"  the projectile's point BALL game px back from the drawn front, vertically the middle (the flying dagger);
  "feet"   the box's middle across, the tag's lowest drawn row on the spot (pictures standing on the ground or rising
           from a hand).
A ViewEffect on a point (the daggers' landing) is drawn round the point like a unit round its position, whose soles are
FEET game px lower: the ground there is (0, FEET) too.
The pictures for her frames are Codex's read-backs on the pack's guides (pixel_1x/katarina_bake_*.png), motes under MOTE
squares dropped.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "katarina")
CODEX = os.path.join(SRC, "codex_fx")
BAKE_DIR = os.path.join(SRC, "fx_bake")
CELLS = os.path.join(SRC, "fx_bake_cells.json")
MOD = os.path.join(ROOT, "league")
FEET = 11                       # game px from the pivot down to the soles' row
MOTE = 4
HEAD = -33                      # over a head (her crown is 27 game px over the pivot)

# name -> (mirror, frames, big, anchor, spot (x, y from the pivot), frame times, extra: BALL for "front")
FX = {
    # in flight: Animated, looping, turned to their flight
    "q_blade": ("pt", 4, False, "mid", (0, 0), [50] * 4, 0),
    "r_dagger": ("ud", 2, False, "front", (0, 0), [60, 60], 1),
    # on a unit, following
    "a_hit": ("lr", 4, False, "mid", (0, -6), [40, 50, 60, 70], 0),
    "q_hit": ("lr", 4, False, "mid", (0, -6), [40, 50, 60, 70], 0),
    "p_hit": ("lr", 3, False, "mid", (0, -6), [50, 60, 70], 0),
    "e_hit": ("lr", 4, False, "mid", (0, -6), [40, 50, 60, 70], 0),
    "r_hit": ("lr", 3, False, "mid", (0, -6), [40, 50, 60], 0),
    "q_arc": ("lr", 5, False, "feet", (0, -6), [60] * 5, 0),
    "p_reset": ("lr", 5, False, "feet", (0, FEET), [60, 70, 80, 90, 100], 0),
    # on her spot (not following) and on the ground
    "e_out": ("lr", 5, False, "feet", (0, FEET), [60, 70, 80, 90, 100], 0),
    "e_in": ("lr", 4, False, "feet", (0, FEET), [50, 60, 70, 80], 0),
    "w_toss": ("lr", 6, False, "feet", (0, -16), [60] * 6, 0),
    "d_fall": ("lr", 4, False, "feet", (0, FEET), [60, 60, 80, 100], 0),
    "d_stuck": ("lr", 4, False, "feet", (0, FEET), [167, 167, 167, 166], 0),
    # big: round her
    "spin": ("lr", 5, True, "feet", (0, FEET + 3), [40, 40, 50, 60, 70], 0),
    "r_lotus": ("lr", 6, True, "feet", (0, FEET + 3), [83, 83, 83, 83, 84, 84], 0),
    # buffs (Animated, looping on the unit)
    "w_ms": ("lr", 4, False, "feet", (0, FEET), [100] * 4, 0),
    "r_gw": ("shape", 4, False, "mid", (0, HEAD), [150] * 4, 0),
}
BAKES = ["a_slash_3", "q_throw_3", "e_slash_2"]


def load(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def manifest():
    with open(os.path.join(CODEX, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)
    return {it["file"]: it for it in m["assets"]}


def frames_of(name):
    """The tag's frames as Codex's read-back cells (manifest frames' pixel_1x_rect)."""
    item = manifest()[f"katarina_fx_{name}.png"]
    a = load(os.path.join(CODEX, "pixel_1x", f"katarina_fx_{name}.png"))
    a[a[..., 3] < 128] = 0
    a[..., 3][a[..., 3] > 0] = 255
    out = []
    for fr in item["frames"]:
        x, y, w, h = fr["pixel_1x_rect"]
        out.append(a[y:y + h, x:x + w].copy())
    return out


def box(f):
    ys, xs = np.nonzero(f[..., 3] > 0)
    return (xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else None


def placed(name):
    mirror, n, _, anchor, spot, times, extra = FX[name]
    cells = frames_of(name)
    if len(cells) != n or len(times) != n:
        sys.exit(f"{name}: {len(cells)} frames, {len(times)} times, not {n}")
    low = max(b[3] for b in (box(c) for c in cells) if b)
    seq = []
    for c, ms in zip(cells, times):
        b = box(c)
        if b is None:
            continue
        x0, x1, y0, y1 = b
        H, W = c.shape[:2]
        if anchor == "front":
            ax, ay = x1 + 0.5 - extra, (y0 + y1 + 1) / 2.0
        elif anchor == "mid":
            ax, ay = (x0 + x1 + 1) / 2.0, (y0 + y1 + 1) / 2.0
        elif anchor == "feet":
            ax, ay = W / 2.0, low + 1.0
        elif anchor == "ground":
            ax, ay = W / 2.0, H - extra
        else:
            ax, ay = W / 2.0, H / 2.0
        # the cell on a canvas round the anchor (whole pixels), then centred on the pivot with the anchor on the spot
        ix, iy = int(round(ax)), int(round(ay))
        seq.append((G.centre_frame(c, spot[0] - ix, spot[1] - iy), float(ms)))
    return seq


def check(e):
    bad = []
    for name, seq in e.items():
        mirror = FX[name][0]
        for k, (f, _) in enumerate(seq):
            al = f[..., 3]
            if not al.any():
                bad.append(f"{name} {k + 1} empty")
            if set(np.unique(al)) - {0, 255}:
                bad.append(f"{name} {k + 1} soft alpha")
            b = box(f)
            t = f[b[2]:b[3] + 1, b[0]:b[1] + 1] if b else f    # the drawn box (an even width sits half a pixel off)
            if mirror in ("lr", "both") and not (t == t[:, ::-1]).all():
                bad.append(f"{name} {k + 1} not symmetric left to right")
            if mirror == "pt" and not (t == t[::-1, ::-1]).all():
                bad.append(f"{name} {k + 1} not the same turned half round")
            if mirror == "ud" and not (t == t[::-1]).all():
                bad.append(f"{name} {k + 1} not symmetric top to bottom")
            if mirror == "shape" and not ((t[..., 3] > 0) == (t[..., 3] > 0)[:, ::-1]).all():
                bad.append(f"{name} {k + 1} shape not symmetric left to right")
    return bad


def bakes():
    with open(CELLS, encoding="utf-8") as f:
        cells = json.load(f)
    out = {}
    for key in BAKES:
        a = load(os.path.join(CODEX, "pixel_1x", f"katarina_bake_{key}.png"))
        c = cells[key]
        if list(a.shape[1::-1]) != c["canvas"]:
            sys.exit(f"pixel_1x/katarina_bake_{key}.png is {a.shape[1]}x{a.shape[0]}, the guide {c['canvas']}")
        a[a[..., 3] < 128] = 0
        a[..., 3][a[..., 3] > 0] = 255
        op = a[..., 3] > 0
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n:
            sizes = ndimage.sum(op, lbl, range(1, n + 1))
            small = np.zeros(n + 1, bool)
            small[1:] = sizes < MOTE
            a[small[lbl]] = 0
        out[key] = a
    return out


def review(out_dir, e):
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for name, seq in e.items():
        z = 3 if FX[name][2] else 6
        tiles = []
        for f, ms in seq:
            bg = Image.new("RGBA", (f.shape[1], f.shape[0]), (52, 60, 46, 255))
            bg.alpha_composite(Image.fromarray(f))
            d = ImageDraw.Draw(bg)
            cx, cy = f.shape[1] // 2, f.shape[0] // 2
            d.point((cx, cy), fill=(255, 0, 0, 255))
            if cy + FEET < f.shape[0]:
                d.point((cx, cy + FEET), fill=(0, 160, 255, 255))
            tiles.append(bg.resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST))
        W = sum(t.width + 4 for t in tiles)
        H = max(t.height for t in tiles) + 14
        r = Image.new("RGB", (W, H), (16, 16, 16))
        ImageDraw.Draw(r).text((2, 1), f"{name} (red: the pivot, blue: the soles)", fill=(255, 255, 0))
        x = 0
        for t in tiles:
            r.paste(t.convert("RGB"), (x, 14))
            x += t.width + 4
        rows.append(r)
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height + 4 for r in rows)), (0, 0, 0))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height + 4
    sheet.save(os.path.join(out_dir, "katarina_fx_frames.png"))
    print(os.path.join(out_dir, "katarina_fx_frames.png"), sheet.size)


def prepare(delivery):
    """The parts of Codex's delivery the import reads, into assets/source/katarina/codex_fx (the raw pictures stay in the
    delivery: the read-backs are good)."""
    os.makedirs(os.path.join(CODEX, "pixel_1x"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(delivery, "pixel_1x"))):
        shutil.copy2(os.path.join(delivery, "pixel_1x", f), os.path.join(CODEX, "pixel_1x", f))
    for f in ("HANDOFF.md", "manifest.json", "generation-prompts.txt"):
        shutil.copy2(os.path.join(delivery, f), os.path.join(CODEX, f))
    print("prepared", CODEX)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", help="Codex's delivery folder (unzipped)")
    ap.add_argument("--review", help="write every effect's frames here")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    e = {name: placed(name) for name in FX}
    bad = check(e)
    if bad:
        sys.exit("\n".join(bad))
    tables = {"league_katarina_fx": {}, "league_katarina_big": {}}
    for name, seq in e.items():
        tables["league_katarina_big" if FX[name][2] else "league_katarina_fx"][name] = seq
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    baked = bakes()
    os.makedirs(BAKE_DIR, exist_ok=True)
    for old in os.listdir(BAKE_DIR):
        if old.endswith(".png"):
            os.remove(os.path.join(BAKE_DIR, old))
    for key, arr in baked.items():
        Image.fromarray(arr).save(os.path.join(BAKE_DIR, f"{key}.png"))
    print("baked", len(baked), "pictures ->", BAKE_DIR)
    if a.review:
        review(a.review, e)


if __name__ == "__main__":
    main()
