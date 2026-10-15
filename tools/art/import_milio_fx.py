#!/usr/bin/env python3
"""Milio's effects from Codex's step-3 delivery (assets/source/milio/codex_fx, from milio_fx_pack_done.zip of 2026-10-15)
as the game sheets league_milio_fx / league_milio_fx_big, and the pictures drawn into his frames
(assets/source/milio/fx_bake, laid onto his restyled dense frames by tools/art/rig_milio.py --pinholes).

    python tools/art/import_milio_fx.py --prepare <delivery dir>   (once: copies what the import reads)
    python tools/art/import_milio_fx.py [--review DIR]

league_kindred's way (tools/art/import_kindred_fx.py). Codex drew every effect as its own sheet (raw/milio_fx_<name>.png:
the frames side by side in equal cells, squares of 10-16 px) and read them back itself at the pack's cell sizes
(pixel_1x/) - too small: the hug's ribbons became dots, the kick's impact ring broke apart. So every sheet is read here
from the raw picture: its frames are the equal cells (each boundary moved to the emptiest column near it, split()),
one scale for the sheet (the widest frame to WIDTH game pixels), each game pixel drawn where half its block is, its
colour the block's commonest once every raw pixel is snapped to the effect's ramp (the manifest's palette; white
counted WHITE_W times so the cores stay white), then mirrored - left to right, or top to bottom for the fireballs (they
are turned to their flight). Each frame is read round an anchor and the anchor goes on a spot (ANCHOR / SPOT in FX):
  "mid"   its drawn box's middle on the spot (hits on a unit);
  "front" the ball: BALL game px back from its drawn front, vertically its middle (in flight: the projectile's point);
  "feet"  its box's middle across, the sheet's lowest drawn row on the soles row (lights round an ally, his buffs);
  "row:<k>"  across its box's middle, down the raw row the sheet's frame k marks: q_fall's rune ring, q_land's first
          frame's flash (the ground point), w_fire's ring - all on the soles row (the lob's landing point is a unit's
          spot: its pivot, FEET over the ground).
The pictures for his frames are Codex's read-backs on the pack's guides (pixel_1x/milio_bake_*.png: 192 x 128 or
128 x 192 dense squares, re-registered by Codex on the guide's crosses), motes under MOTE squares dropped.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "milio")
CODEX = os.path.join(SRC, "codex_fx")
BAKE_DIR = os.path.join(SRC, "fx_bake")
CELLS = os.path.join(SRC, "fx_bake_cells.json")
MOD = os.path.join(ROOT, "league")
FEET = 11                       # game px from the pivot down to the soles' row
ALPHA = 128
NEED = 0.5
WHITE_W = 1.6
SPECK = 30                      # raw pieces smaller than this (px) are the generator's noise

# name -> (width in game px of the widest frame, mirror, frames, big, anchor, spot (x, y from the pivot), frame times,
#          extra: BALL for "front")
FX = {
    # in flight: Animated, looping (build_milio P_), turned to their flight
    "a_ball": (14, "ud", 4, False, "front", (0, 0), [70] * 4, 3),
    "q_ball": (20, "ud", 4, False, "front", (0, 0), [70] * 4, 4),
    "e_ball": (16, "ud", 4, False, "front", (0, 0), [80] * 4, 3),
    # on a unit, following (build_milio E(..., FX, 2))
    "a_hit": (14, "lr", 4, False, "mid", (0, -6), [40, 50, 60, 70], 0),
    "q_hit": (22, "lr", 5, False, "mid", (0, -6), [40, 50, 60, 70, 80], 0),
    "q_burn": (18, "lr", 4, False, "feet", (0, FEET - 1), [80, 90, 100, 110], 0),
    "e_hug": (26, "lr", 5, False, "feet", (0, FEET - 1), [60, 70, 90, 100, 120], 0),
    "w_heal": (20, "lr", 5, False, "feet", (0, FEET - 1), [70, 80, 90, 100, 110], 0),
    "r_hit": (28, "lr", 6, False, "feet", (0, FEET - 1), [70, 80, 100, 110, 120, 130], 0),
    # the fall (the lob's telegraph for its whole q_fall 36-tick flight: 600 ms) and the burst where it lands
    "q_fall": (50, "lr", 6, True, "row:0", (0, FEET), [100] * 6, 0),
    "q_land": (56, "lr", 6, True, "row:0", (0, FEET), [60, 70, 80, 90, 100, 120], 0),
    # buffs (Animated, looping on the unit)
    "fired": (20, "lr", 4, False, "feet", (0, FEET - 1), [120] * 4, 0),
    "e_on": (24, "lr", 4, False, "feet", (0, FEET - 1), [120] * 4, 0),
    "w_fire": (70, "lr", 4, True, "row:0", (0, FEET), [120] * 4, 0),
    "q_slow": (16, "lr", 4, False, "feet", (0, FEET - 1), [120] * 4, 0),
}
UD_TOO = {"w_fire"}             # also symmetric top to bottom (the campfire ring)
# read this much flatter (game px tall per game px wide): Codex drew q_land's fire column 1.3 times the ring's width
# (73 game px at the ring's 56, twice his height; the pack asked for 30) - at 0.6 the column is 44, the ring 13 tall
SQUASH = {"q_land": 0.6}
MOTE = 4
BAKES = ["a_fling_3", "q_ready_3", "q_kick_4", "e_gather_2", "e_send_3", "r_rise_3", "r_burst_4", "r_fade_5"]


def load(path):
    return np.asarray(Image.open(path).convert("RGBA"))


def manifest():
    with open(os.path.join(CODEX, "manifest.json"), encoding="utf-8") as f:
        items = json.load(f)
    return {it["file"]: it for it in items}


def hexes(pal):
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in pal], float)


def despeckle(drawn):
    lbl, n = ndimage.label(drawn, structure=np.ones((3, 3)))
    if not n:
        return drawn
    sizes = ndimage.sum(drawn, lbl, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes >= SPECK
    return keep[lbl]


def split(drawn, n):
    """n frames in equal cells, each boundary moved to the emptiest column within a fifth of a cell of it."""
    W = drawn.shape[1]
    col = drawn.sum(0)
    cw = W / float(n)
    cuts = [0]
    for k in range(1, n):
        b = int(round(k * cw))
        lo, hi = max(1, int(b - 0.2 * cw)), min(W - 1, int(b + 0.2 * cw))
        cuts.append(lo + int(np.argmin(col[lo:hi])))
    cuts.append(W)
    return [(cuts[k], cuts[k + 1]) for k in range(n)]


def vote(sub, cx, cy, s, hw, hh, pal, white, need=NEED, sy=None):
    """The game-px frame (2 hw + 1 by 2 hh + 1) round raw point (cx, cy) at s raw px a game px (sy down)."""
    sy = sy or s
    f = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    for j in range(2 * hh + 1):
        ya, yb = cy + (j - hh - 0.5) * sy, cy + (j - hh + 0.5) * sy
        r0, r1 = max(0, int(round(ya))), min(sub.shape[0], int(round(yb)))
        if r1 <= r0:
            continue
        for i in range(2 * hw + 1):
            xa, xb = cx + (i - hw - 0.5) * s, cx + (i - hw + 0.5) * s
            c0, c1 = max(0, int(round(xa))), min(sub.shape[1], int(round(xb)))
            if c1 <= c0:
                continue
            blk = sub[r0:r1, c0:c1].reshape(-1)
            on = blk[blk >= 0]
            if len(on) < need * len(blk):
                continue
            cnt = np.bincount(on, minlength=len(pal)).astype(float)
            cnt[white] *= WHITE_W
            f[j, i, :3] = pal[int(np.argmax(cnt))]
            f[j, i, 3] = 255
    return f


def mirrored(f, how):
    f = f.copy()
    if how in ("lr", "both"):
        w = f.shape[1]
        f[:, w - w // 2:] = f[:, :w // 2][:, ::-1]
    if how in ("ud", "both"):
        h = f.shape[0]
        f[h - h // 2:] = f[:h // 2][::-1]
    return f


def read(name):
    """[(frame, (anchor column, anchor row))] in game px for effect `name`, and the scale."""
    width, mirror, n, _, anchor, _, _, ball = FX[name]
    item = manifest()[f"milio_fx_{name}.png"]
    a = load(os.path.join(CODEX, "raw", f"milio_fx_{name}.png"))
    pal = hexes(item["palette"])
    lab = srgb2lab(pal)
    drawn = despeckle(a[..., 3] >= ALPHA)
    flat = a[..., :3].reshape(-1, 3).astype(float)
    idx = np.full(flat.shape[0], -1)
    m = drawn.reshape(-1)
    d = ((srgb2lab(flat[m])[:, None, :] - lab[None, :, :]) ** 2).sum(-1)
    idx[m] = d.argmin(1)
    idx = idx.reshape(a.shape[:2])
    cols = split(drawn, n)
    boxes = []
    for x0, x1 in cols:
        ys, xs = np.nonzero(idx[:, x0:x1] >= 0)
        boxes.append((xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else None)
    widest = max(b[1] - b[0] + 1 for b in boxes if b)
    s = widest / float(width)
    white = int(np.argmax(pal.sum(1)))
    low = max(b[3] for b in boxes if b)
    if anchor.startswith("row:"):
        k = int(anchor.split(":")[1])
        b = boxes[k]
        if name == "q_fall":          # the rune ring: the rows of frame k's lowest piece
            sub = idx[:, cols[k][0]:cols[k][1]] >= 0
            lbl, nl = ndimage.label(sub, structure=np.ones((3, 3)))
            lows = [(np.nonzero(lbl == j)[0].max(), j) for j in range(1, nl + 1)]
            ring = lbl == max(lows)[1]
            ry = np.nonzero(ring.any(1))[0]
            row = (ry.min() + ry.max()) / 2.0
        else:                         # q_land's first flash, w_fire's ring: the frame's own middle row
            row = (b[2] + b[3]) / 2.0
    out = []
    for (x0, x1), b in zip(cols, boxes):
        sub = idx[:, x0:x1]
        if b is None:
            out.append((np.zeros((1, 1, 4), np.uint8), (0, 0)))
            continue
        bx0, bx1, by0, by1 = b
        if anchor == "front":
            cx, cy = bx1 + 0.5 - ball * s, (by0 + by1 + 1) / 2.0
        elif anchor == "mid":
            cx, cy = (bx0 + bx1 + 1) / 2.0, (by0 + by1 + 1) / 2.0
        elif anchor == "feet":
            cx, cy = (bx0 + bx1 + 1) / 2.0, low + 0.5 - 0.5 * s
        else:
            cx, cy = (bx0 + bx1 + 1) / 2.0, row
        sy = s / SQUASH.get(name, 1.0)
        if anchor == "feet":
            cy = low + 0.5 - 0.5 * sy
        hw = int(np.ceil(max(cx - bx0, bx1 + 1 - cx) / s)) + 1
        hh = int(np.ceil(max(cy - by0, by1 + 1 - cy) / sy)) + 1
        f = vote(sub, cx, cy, s, hw, hh, pal, white, sy=sy)
        if not f[..., 3].any():       # a last frame of fading sparks smaller than a game pixel each: a fifth will do
            f = vote(sub, cx, cy, s, hw, hh, pal, white, need=0.2, sy=sy)
        how = "both" if name in UD_TOO else mirror
        out.append((mirrored(f, how), (hw, hh)))
    return out, s


def place(f, anc, spot):
    """The frame on a canvas centred on the unit's pivot, its anchor pixel on `spot`."""
    hw, hh = anc
    return G.centre_frame(f, spot[0] - hw, spot[1] - hh)


def effects():
    out, notes = {}, []
    for name, (width, mirror, n, big, anchor, spot, times, _) in FX.items():
        frames, s = read(name)
        if len(frames) != n or len(times) != n:
            sys.exit(f"{name}: {len(frames)} frames, {len(times)} times, not {n}")
        seq = [(place(f, anc, spot), float(ms)) for (f, anc), ms in zip(frames, times)]
        while len(seq) > 1 and not seq[-1][0][..., 3].any():     # a last frame of sparks under a game pixel each
            notes.append(f"{name}: last frame empty at this size, dropped")
            seq.pop()
        out[name] = seq
        size = max(f.shape[1] for f, _ in frames), max(f.shape[0] for f, _ in frames)
        notes.append(f"{name}: {n} frames at {s:.1f} raw px a game px, up to {size[0]}x{size[1]}, "
                     f"{sum(times)} ms")
    return out, notes


def check(e):
    bad = []
    for name, seq in e.items():
        mirror = FX[name][1]
        for k, (f, _) in enumerate(seq):
            al = f[..., 3]
            if not al.any():
                bad.append(f"{name} {k + 1} empty")
            if set(np.unique(al)) - {0, 255}:
                bad.append(f"{name} {k + 1} soft alpha")
            if mirror == "lr" and not (f == f[:, ::-1]).all():
                bad.append(f"{name} {k + 1} not symmetric left to right")
    return bad


def bakes():
    with open(CELLS, encoding="utf-8") as f:
        cells = json.load(f)
    out = {}
    for key in BAKES:
        a = load(os.path.join(CODEX, "pixel_1x", f"milio_bake_{key}.png")).copy()
        c = cells[key]
        if list(a.shape[1::-1]) != c["canvas"]:
            sys.exit(f"pixel_1x/milio_bake_{key}.png is {a.shape[1]}x{a.shape[0]}, the guide {c['canvas']}")
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
        z = 3 if FX[name][3] else 6
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
    sheet.save(os.path.join(out_dir, "milio_fx_frames.png"))
    print(os.path.join(out_dir, "milio_fx_frames.png"), sheet.size)


def prepare(delivery):
    """The parts of Codex's delivery the import reads, into assets/source/milio/codex_fx (the bakes' raw pictures stay
    in the delivery: their read-backs are on the guides' grid already)."""
    os.makedirs(os.path.join(CODEX, "raw"), exist_ok=True)
    os.makedirs(os.path.join(CODEX, "pixel_1x"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(delivery, "raw"))):
        if f.startswith("milio_fx_"):
            shutil.copy2(os.path.join(delivery, "raw", f), os.path.join(CODEX, "raw", f))
    for f in sorted(os.listdir(os.path.join(delivery, "pixel_1x"))):
        if f.startswith("milio_bake_"):
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
    e, notes = effects()
    for line in notes:
        print(line)
    bad = check(e)
    if bad:
        sys.exit("\n".join(bad))
    tables = {"league_milio_fx": {}, "league_milio_fx_big": {}}
    for name, seq in e.items():
        tables["league_milio_fx_big" if FX[name][3] else "league_milio_fx"][name] = seq
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
