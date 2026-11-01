#!/usr/bin/env python3
"""Import the Sentry's effects (assets/source/sentry/PROMPTS_FX.md: 13 pictures and 3 skill icons) as the tft pack's
sheets tft_sentry_fx and tft_sentry_big and its icons.

    python tools/art/import_sentry_fx.py [--review out.png]

The source is Codex's step-3 delivery (assets/source/sentry/codex_fx/sentry_fx: pixel_1x/sentry_fx_<name>.png, one row
of equal frames at game size; manifest.json lists each one's frames, cell_1x and source_crop_per_cell - each frame's box
in its raw draft, raw/; 64 px icons). Every frame is cut from pixel_1x as delivered (alpha 0 / 255) and placed as the kit
plays it: spots are game px from the pivot (x forward, y down); a unit's soles are 11 under it. Every picture is checked
symmetric left to right, the flying ones (a_bolt, q_zap, q_beam) top to bottom, pointing right; r_sweep is swept.
RECUT (cut again from the raw draft: each frame's raw box (manifest source_crop_per_cell, in its source_grid cell's
own frame, row by row) brought to the cell by an area average - colour weighted by
alpha, a square opaque where its cover reaches RECUT_COVER - snapped to the delivered strip's palette and the prompt's
ramps, the left half mirrored onto the right): Codex's own 1x read voted these into noise -
  e_ring  the raw's crystal shards are 3-5 game px: the majority vote of a misaligned grid left a grainy field;
  q_shred / r_shred / e_slow  the flecks and the cracked hexagon came back as scattered single squares.
The laser q_beam (league_velkoz R's beam_tag): each wave's homing projectile leaves the core (q_by) and creeps toward the
target 1 px a tick (q_bspeed), so its picture is one frame a tick: an empty first tick (its first move points it up),
then q_p frames - the beam strip's frame (t % 4) with its flare held on the core, each drawn 1 px further back than the
last - then empty for the rest of its creep. The sweep r_sweep the same way on the view-only line of the ult (r_speed
1000): an empty tick, then SWEEP_TICKS ticks a frame of Codex's six swept beams, the flare held on the core.
Anchors: the hits on the struck body (HIT); the bolt and the zap on their own point (FLY); the ring on the ground where
it leapt from, the split flash and the charge round its body (their cells' bottom on its soles: the core 19 game px up,
as the prompt laid them), the shreds and the slow on the unit that carries them (SOLES).
Icons: brought to 64 x 64 from the raw tiles with LANCZOS (Codex's 64 px cuts voted the 1254 px tiles into mud: skill2
a smear).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import import_jhin as J  # noqa: E402
import pack_sentry_fx as PK  # noqa: E402
from build_sentry import P  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sentry", "codex_fx", "sentry_fx")
MOD = os.path.join(ROOT, "tft")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BIG = set(PK.BIG_FX)
FLYING = set(PK.FLYING)
HIT = (0, -13)                  # a hit on the upper body of a 32-46 px unit
FLY = (0, 0)                    # a projectile's own point
SOLES = (0, 11)                 # on the ground under a unit (or under its own pivot)
MS = 1000 / 60                  # one tick
BEAM_FLARE = 4                  # q_beam's flare middle, px from the cell's left edge (the prompt)
SWEEP_FLARE = (5, 35)           # r_sweep's flare middle in its 100 x 70 cell (the prompt)
SWEEP_TICKS = 3                 # ticks each swept beam shows (6 x 3 = 18 ticks = r_rel's frame showing r_blast)
seq = J.seq
RECUT = {"e_ring", "q_shred", "r_shred", "e_slow"}
RECUT_COVER = 0.45


def loop(n, ms):
    return seq(range(n), [ms] * n)


# effect -> (anchor: "core", "foot", "beam" or "sweep", frames with ms, spots)
FX = {
    # Shard Bolt: the bolt in flight, the burst on the struck
    "a_bolt": ("core", loop(4, 60), [FLY]),
    "a_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    # Azure Laser: the zap carrying each wave's damage, the laser from the core, the burn, the cracked shield
    "q_zap": ("core", loop(4, 50), [FLY]),
    "q_beam": ("beam", None, None),
    "q_hit": ("core", seq(range(4), [40, 50, 60, 70]), [HIT]),
    "q_shred": ("foot", loop(6, 100), [SOLES]),
    # Rift Leap: the split flash round it, the shard ring left where it was, the slowed
    "e_split": ("foot", seq(range(5), [40, 50, 60, 70, 80]), [SOLES]),
    "e_ring": ("foot", seq(range(6), [60, 120, 400, 250, 200, 150]), [SOLES]),
    "e_slow": ("foot", loop(6, 100), [SOLES]),
    # Prism Sweep: the charge round its core, the swept beam, the blast on the struck, the shattered shield
    "r_open": ("foot", seq(range(6), [50, 50, 50, 50, 50, 70]), [SOLES]),
    "r_sweep": ("sweep", None, None),
    "r_hit": ("core", seq(range(5), [40, 50, 60, 70, 80]), [HIT]),
    "r_shred": ("foot", loop(6, 100), [SOLES]),
}
ICONS = {"skill": "tft_sentry_skill", "skill2": "tft_sentry_skill2", "ult": "tft_sentry_ult"}


def ramps():
    cols = []
    for ramp in (PK.AZURE, PK.SAGE, PK.NAVY):
        cols += [[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in ramp.split(", ")]
    return np.array(cols, float)


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8-sig") as f:
        m = json.load(f)
    return {e["file"][len("sentry_fx_"):-4]: e for e in m if e.get("kind") == "fx"}


def recut(name, strip, e):
    """Each frame's raw box averaged down to the cell (alpha-weighted colour, cover >= RECUT_COVER), snapped to the
    strip's palette and the ramps, the left half mirrored onto the right."""
    w, h = e["cell_1x"]
    raw = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"sentry_fx_{name}.png"))).convert("RGBA")).astype(float)
    pal = np.unique(np.concatenate([strip[strip[..., 3] >= 128][:, :3].astype(float), ramps()]), axis=0)
    out = np.zeros((h, w * e["frames"], 4), np.uint8)
    cols, rows = e["source_grid"]
    gw, gh = raw.shape[1] / cols, raw.shape[0] / rows
    for k, box in enumerate(e["source_crop_per_cell"][:e["frames"]]):
        ox, oy = (k % cols) * gw, (k // cols) * gh        # the crops are in each grid cell's own frame, row by row
        x0, y0, x1, y1 = box[0] + ox, box[1] + oy, box[2] + ox, box[3] + oy
        own = np.zeros_like(raw)      # the boxes reach past their cell (e_ring's 31-62 px up): the neighbour's frame out
        gy0, gx0 = int(round(oy)), int(round(ox))
        own[gy0:int(round(oy + gh)), gx0:int(round(ox + gw))] = raw[gy0:int(round(oy + gh)), gx0:int(round(ox + gw))]
        bw, bh = x1 - x0, y1 - y0
        cov = np.zeros((h, w))
        col = np.zeros((h, w, 3))
        for j in range(h):
            for i in range(w):
                ya, yb = int(round(y0 + j * bh / h)), int(round(y0 + (j + 1) * bh / h))
                xa, xb = int(round(x0 + i * bw / w)), int(round(x0 + (i + 1) * bw / w))
                win = own[max(0, ya):max(0, yb), max(0, xa):max(0, xb)].reshape(-1, 4)
                n = max(1, (yb - ya) * (xb - xa))
                a = win[:, 3] / 255.0
                cov[j, i] = a.sum() / n
                if a.sum() > 0:
                    col[j, i] = (win[:, :3] * a[:, None]).sum(0) / a.sum()
        on = cov >= RECUT_COVER
        idx = np.argmin(((col[:, :, None, :] - pal[None, None]) ** 2).sum(-1), axis=2)
        c = np.zeros((h, w, 4), np.uint8)
        c[on, :3] = pal[idx[on]]
        c[on, 3] = 255
        c[:, w - w // 2:] = c[:, :w // 2][:, ::-1]
        out[:, k * w:(k + 1) * w] = c
    print(f"{name}: recut from the raw by area")
    return out


def cells(name, m):
    """The frames of an effect, symmetry checked."""
    e = m[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"sentry_fx_{name}.png"))).convert("RGBA")).copy()
    w, h = e["cell_1x"]
    if name in RECUT:
        a = recut(name, a, e)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    if a.shape[0] != h or a.shape[1] != w * e["frames"]:
        sys.exit(f"{name}: sheet {a.shape[1]}x{a.shape[0]} is not {e['frames']} cells of {w}x{h}")
    out = [a[:, k * w:(k + 1) * w].copy() for k in range(e["frames"])]
    for k, c in enumerate(out):
        if name != "r_sweep":
            flip = c[::-1] if name in FLYING else c[:, ::-1]
            if not (c == flip).all():
                sys.exit(f"{name} frame {k + 1} is not symmetric "
                         + ("top to bottom" if name in FLYING else "left to right"))
        if not c[..., 3].any():
            sys.exit(f"{name} frame {k + 1} is empty")
    return out


def creep(cs, flare, ticks_of, n_ticks):
    """A creeping projectile's picture held on the core (league_velkoz's beam_tag): an empty first tick, then for tick
    t = 1..n_ticks the frame ticks_of(t) with its flare `t` px behind the projectile's point, then empty."""
    h, w = cs[0].shape[:2]
    fx, fy = flare
    reach = max(fx, w - fx) + n_ticks + 2
    W, H = 2 * reach + 1, 2 * max(fy, h - fy) + 1
    cx, cy = W // 2, H // 2
    out = [(np.zeros((3, 3, 4), np.uint8), MS)]
    for t in range(1, n_ticks + 1):
        canvas = np.zeros((H, W, 4), np.uint8)
        c = cs[ticks_of(t)]
        left, top = cx - t - fx, cy - fy
        m = c[..., 3] > 0
        canvas[top:top + h, left:left + w][m] = c[m]
        out.append((canvas, MS))
    out.append((np.zeros((3, 3, 4), np.uint8), 4000))
    return out


def anchor(cs, kind):
    h, w = cs[0].shape[:2]
    if kind == "core":
        return [(w - 1) / 2, (h - 1) / 2]
    return [(w - 1) / 2, h - 1]


def icon(name):
    """Codex's raw 1254 px icon tile -> 64 x 64 (LANCZOS)."""
    im = Image.open(lp(os.path.join(SRC, "raw", f"sentry_icon_{name}.png"))).convert("RGB")
    return im.resize((64, 64), Image.LANCZOS).convert("RGBA")


def review(allc, path):
    Z = 6
    rows = []
    for cs in allc.values():
        W = sum(c.shape[1] + 2 for c in cs)
        H = max(c.shape[0] for c in cs)
        img = Image.new("RGBA", (W * Z, H * Z), (104, 112, 72, 255))
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
    sheet.convert("RGB").save(path)
    icons = Image.new("RGB", (3 * 202, 192), (24, 24, 30))
    for i, src in enumerate(ICONS):
        icons.paste(icon(src).convert("RGB").resize((192, 192), Image.NEAREST), (i * 202, 0))
    icons.save(path.replace(".png", "_icons.png"))
    print(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect's game-size cells at 6x here (nothing else written)")
    a = ap.parse_args()
    m = manifest()
    if set(m) != set(FX):
        sys.exit(f"delivered {sorted(set(m) ^ set(FX))} differ from the list")
    allc = {n: cells(n, m) for n in FX}
    if a.review:
        review(allc, a.review)
        return
    tables = {"tft_sentry_fx": {}, "tft_sentry_big": {}}
    for tag, (kind, frames, spots) in FX.items():
        cs = allc[tag]
        if kind == "beam":
            out = creep(cs, (BEAM_FLARE, (cs[0].shape[0] - 1) // 2), lambda t: t % len(cs), P["q_p"])
        elif kind == "sweep":
            out = creep(cs, SWEEP_FLARE, lambda t: min(len(cs) - 1, (t - 1) // SWEEP_TICKS), len(cs) * SWEEP_TICKS)
        else:
            anc = anchor(cs, kind)
            out = [(np.zeros((3, 3, 4), np.uint8) if k == J.EMPTY else J.place(cs[k], anc, spots), ms)
                   for k, ms in frames]
        tables["tft_sentry_big" if tag in BIG else "tft_sentry_fx"][tag] = out
        print(f"{tag:8s} {cs[0].shape[1]}x{cs[0].shape[0]}, {kind}, {len(out)} frames")
    os.makedirs(lp(os.path.join(MOD, "effects")), exist_ok=True)
    for sheet, tags in tables.items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tags, share=True)
        print(f"tft/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(ms for _, ms in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(lp(os.path.join(MOD, "icons")), exist_ok=True)
    for src, dst in ICONS.items():
        icon(src).save(lp(os.path.join(MOD, "icons", dst + ".png")))
        print(f"tft/icons/{dst}.png")


if __name__ == "__main__":
    main()
