#!/usr/bin/env python3
"""Aphelios's effects from Codex's step-3 delivery (assets/source/aphelios/codex_fx, from aphelios_fx_pack_done.zip) as
the game sheets league_aphelios_fx / league_aphelios_big (the tags build_aphelios.py's views bind).

    python tools/art/import_aphelios_fx.py --prepare <delivery dir>   (once: copies what the import reads)
    python tools/art/import_aphelios_fx.py [--review DIR]

import_katarina_fx.py's way: Codex's read-backs (pixel_1x/aphelios_fx_<name>.png, the frames side by side in the pack's
equal cells - manifest.json's pixel_1x_rect when it lists them) used as they are, checked for hard alpha and the
symmetry the pack asked. Each tag is placed by one anchor for all its frames (the frames' union box, so a loop does not
jitter) on a spot, game px from the pivot (x forward, y down):
  "front"  the drawn front BALL px back, vertically the middle (in flight: the projectile's point);
  "mid"    the box's middle (hits on a unit, the sentry);
  "root"   the box's left edge, vertically the middle (the muzzle flash and Infernum's wave start there);
  "feet"   the box's middle across, the row under its lowest drawn row (lights standing round a unit);
  ("row", k) the box's middle across, the cell's k-th row from the bottom (the pack's "k squares above the cell's
           bottom row": the root's ring, the blast's ground ring, the chakrams' orbit).
The weapon aura `mw` is drawn once (Calibrum's green) and recoloured square for square along the ramps to each weapon
(mw_cal .. mw_cre). The muzzle flash is not a tag here: the client never mirrors an effect picture (SKILL.md "Both
sides"), so tools/art/rig_aphelios.py draws it into his shot frames. `q_c_pop` is two strips: (A) the bolt (tag
q_c_pop) and (B) the burst (tag q_c_pop_b).
The muzzles (for the bullets' lead ticks) are measured on his sheet (league/champions/league_aphelios: the plain 1x
tags, the aim frame 1 of a_<w> - the shot frames carry the baked flash - its drawn front's column and the middle of its
rows) and moved to where the game shows him: 90 % about the soles (league.dll hd.rs SIZES - the unit's soles stay at
FEET, the rest comes in by a tenth).
The bullets stay unseen until they pass the muzzle (flight's lead ticks at the attack's projectile speed); their views
are repeat false (build_aphelios.py), the last frame held a second. Severum's Onslaught bolts and Infernum's splash
show the attacks' pictures under tags of their own (q_s_bolt, a_inf_s): they fly faster or start at the target.
Every cell goes through clean() first (the user, 2026-10-20: 「厄斐琉斯的特效 调的清晰点」, picked "fewer specks, more
contrast" over redrawing them dense): loose dim specks of 1-3 squares off, the dim rim round a light (its soft halo)
off except on the rings drawn in the ramp's dark steps, pinholes filled, every colour's saturation x1.25 and value
pushed apart ((v - .45) x 1.3 + .5, the brightest a touch whiter), then the pack's symmetry put back exactly.
"""
import argparse
import json
import math
import os
import re
import shutil
import sys

import colorsys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import pack_aphelios_fx as PK  # noqa: E402
from build_aphelios import P, WEAPONS  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aphelios")
CODEX = os.path.join(SRC, "codex_fx")
MOD = os.path.join(ROOT, "league")
SHEET = os.path.join(MOD, "champions", "league_aphelios")
FEET = 11                       # game px from the pivot down to the soles' row
RING = (0, 9)                   # a ring on the ground round a unit's feet (the ellipse's middle 2 over the soles)
SOLE_RING = (0, FEET)           # the low buff rings (5-7 rows): their middle on the soles, the front half below the feet
                                # (2 over the soles his coat and legs hid all but the tips)
HIT = (0, -10)                  # a hit on the upper body (his and the ADCs' 36-47 px)
SIZE = 0.90                     # hd.rs SIZES: league_aphelios
MS = 1000 / 60
EMPTY = "empty"

RAMP = {w: [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in r.split(", ")]
        for w, r in (("cal", PK.GREEN), ("sev", PK.RED), ("grav", PK.VIOLET), ("inf", PK.BLUE), ("cre", PK.SILVER))}


def seq(frames, ms):
    return list(zip(frames, ms))


def flight(n, ms, total, lead):
    """`lead` empty ticks (the bullet leaves his pivot: unseen until it passes the muzzle), then n frames of ms looped
    over `total` ms (twice a straight flight: homing shots chase), the last held a second (repeat false)."""
    k = max(1, math.ceil(total / ms))
    return [(EMPTY, lead * MS)] * (lead > 0) + seq([i % n for i in range(k)], [ms] * (k - 1) + [1000])


def lead(px, speed):
    return max(1, math.ceil(px * 1000 / speed))


def loop(n, total, ms):
    """n frames round and round for `total` ms (an Animation plays its tag once)."""
    k = max(n, int(round(total / ms)))
    return seq([i % n for i in range(k)], [total / k] * k)


def muzzles():
    """weapon -> its muzzle as the game shows him (game px from the pivot): a_<w>'s shot frame 2 on his sheet."""
    anims = json.load(open(SHEET + "#anim.fanim", encoding="utf-8-sig"))["anims"]
    sh = np.asarray(Image.open(SHEET + "#sheet.png").convert("RGBA"))
    out = {}
    for w in WEAPONS:
        r = anims[f"a_{w}"]["frames"][0]["data"]          # the aim (the shot frames carry the baked flash)
        x, y, ww, hh = (int(r[c]) for c in "xywh")
        f = sh[y:y + hh, x:x + ww]
        op = f[..., 3] > 0
        x1 = int(np.nonzero(op.any(0))[0].max())
        ys = np.nonzero(op[:, x1 - 1:x1 + 1].any(1))[0]
        mx, my = x1 - ww // 2, (ys.min() + ys.max()) / 2 - hh // 2
        out[w] = (SIZE * mx, FEET + SIZE * (my - FEET))
    return out


MUZ = muzzles()
A_SPEED = P["a_speed"]           # game units a tick (1000 a game px)
A_TOTAL = 2 * (P["atk_range"] + P["c_range"]) / A_SPEED * MS
Q_SPEED = 20000                  # build_aphelios: the pop, Severum's bolts and the off-hand shots

# tag -> (picture, strip, mirror, big, anchor, spot, frames, recolour)
#   strip: which of the picture's strips (q_c_pop has two); mirror: lr / ud / pt; recolour: a weapon's ramp or None
FX = {
    # the five shots (and Severum's Onslaught bolts, Infernum's splash: the same tags)
    **{f"a_{w}": (f"a_{w}", 0, "ud", False, "front", (0, 0), flight(n, 50, A_TOTAL, lead(MUZ[w][0], A_SPEED)), None)
       for w, n in (("cal", 3), ("sev", 3), ("grav", 4), ("inf", 3), ("cre", 4))},
    # the faster shots (20000 a tick: the pop, Severum's Onslaught, the off-hand shots) one empty tick; Infernum's splash
    # leaves the target, none
    "q_c_pop": ("q_c_pop", 0, "ud", False, "front", (0, 0), flight(3, 40, 2 * P["s_range"] / Q_SPEED * MS, 1), None),
    "q_s_bolt": ("a_sev", 0, "ud", False, "front", (0, 0), flight(3, 50, 2 * P["q_s_r"] / Q_SPEED * MS, 1), None),
    "off_bolt": ("off_bolt", 0, "ud", False, "front", (0, 0), flight(3, 50, 2 * P["s_range"] / Q_SPEED * MS, 1), None),
    "a_inf_s": ("a_inf", 0, "ud", False, "front", (0, 0), flight(3, 50, 2 * P["inf_r"] / A_SPEED * MS, 0), None),
    # on a unit, following
    "a_hit": ("a_hit", 0, "lr", False, "mid", HIT, seq(range(4), [40, 50, 60, 70]), None),
    "q_c_hit": ("q_c_hit", 0, "lr", False, "mid", HIT, seq(range(5), [40, 50, 70, 90, 110]), None),
    "q_c_pop_b": ("q_c_pop", 1, "lr", False, "mid", HIT, seq(range(4), [40, 50, 60, 70]), None),
    "q_s_hit": ("q_s_hit", 0, "lr", False, "mid", HIT, seq(range(3), [30, 40, 50]), None),
    # the root: q_g_root ticks, the ring 2 rows over the cell's bottom on the ring's spot; frames 4-5 pulse
    "q_g_hit": ("q_g_hit", 0, "lr", False, ("row", 2), RING,
                seq([0, 1, 2] + [3, 4] * 3 + [5], [50, 60, 70] + [(P["q_g_root"] * MS - 280) / 6] * 6 + [100]), None),
    "q_i_hit": ("q_i_hit", 0, "lr", False, "mid", HIT, seq(range(4), [40, 50, 60, 70]), None),
    "q_r_hit": ("q_r_hit", 0, "lr", False, "mid", HIT, seq(range(3), [30, 40, 50]), None),
    "r_hit": ("r_hit", 0, "lr", False, "mid", HIT, seq(range(4), [40, 50, 70, 90]), None),
    # on him, following
    "swap": ("swap", 0, "lr", False, "feet", (0, FEET), seq(range(5), [50, 60, 70, 80, 90]), None),
    "q_s_on": ("q_s_on", 0, "lr", False, "mid", RING, loop(4, P["q_s_t"] * MS, 90), None),
    # buffs (Animated, looping on the unit)
    **{f"mw_{w}": ("mw", 0, "lr", False, "mid", SOLE_RING, seq(range(4), [130] * 4), w) for w in WEAPONS},
    "g_slow": ("g_slow", 0, "lr", False, "mid", SOLE_RING, seq(range(4), [100] * 4), None),
    "q_s_haste": ("q_s_haste", 0, "lr", False, "mid", SOLE_RING, seq(range(4), [80] * 4), None),
    # the chakrams round his chest (their drawn middle: Codex drew them lower in the cell than the pack's row 20)
    "cre": ("cre", 0, "lr", False, "mid", (0, -15), seq(range(4), [110] * 4), None),
    # ---- big
    "q_c_shot": ("q_c_shot", 0, "ud", True, "front", (0, 0),
                 flight(4, 50, P["q_c_len"] / P["q_c_speed"] * MS, lead(MUZ["cal"][0], P["q_c_speed"])), None),
    "r_moon": ("r_moon", 0, "ud", True, "front", (0, 0),
               flight(4, 50, 2 * P["r_range"] / P["r_speed"] * MS, lead(MUZ["cal"][0], P["r_speed"])), None),
    "q_g_cast": ("q_g_cast", 0, "lr", True, "mid", RING, seq(range(5), [50, 60, 70, 80, 90]), None),
    # on its view-only projectile (build_aphelios q_inf: from his pivot, lifted to the gun, crawling q_i_wv a tick): the
    # fan's point 12 px ahead of it, on its line; its q_i_wt ticks
    "q_i_wave": ("q_i_wave", 0, "ud", True, "root", (12, 0), seq(range(5), [50, 60, 60, 60, 70]), None),
    # on the landing point (a ViewEffect, never turned), round and round for the sentry's q_r_t ticks
    "q_r_turret": ("q_r_turret", 0, "pt", True, "mid", (0, 0), loop(6, P["q_r_t"] * MS, 90), None),
    "r_cast": ("r_cast", 0, "lr", True, "feet", (0, FEET), seq(range(5), [60, 70, 80, 90, 100]), None),
    "r_boom": ("r_boom", 0, "lr", True, ("row", 5), RING, seq(range(6), [50, 60, 70, 80, 90, 110]), None),
}
BALL = 1


N8 = np.ones((3, 3), bool)


def lum(c):
    return c[..., 0] * 0.299 + c[..., 1] * 0.587 + c[..., 2] * 0.114


def mirror_fix(c, mirror):
    """The drawn box made exactly symmetric again (the fuller half onto the other)."""
    al = c[..., 3] > 0
    if not al.any():
        return c
    ys, xs = np.nonzero(al)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    t = c[y0:y1, x0:x1].copy()
    if mirror in ("lr", "ud"):
        ax = 1 if mirror == "lr" else 0
        n = t.shape[ax]
        h = n // 2
        a = t[:, :h] if ax == 1 else t[:h]
        b = t[:, n - h:] if ax == 1 else t[n - h:]
        if (a[..., 3] > 0).sum() >= (b[..., 3] > 0).sum():
            if ax == 1:
                t[:, n - h:] = a[:, ::-1]
            else:
                t[n - h:] = a[::-1]
        else:
            if ax == 1:
                t[:, :h] = b[:, ::-1]
            else:
                t[:h] = b[::-1]
    elif mirror == "pt":
        flat = t.reshape(-1, 4)
        n = len(flat)
        flat[n - n // 2:] = flat[:n // 2][::-1]
        t = flat.reshape(t.shape)
    out = c.copy()
    out[y0:y1, x0:x1] = t
    return out


def clean(c, mirror, halo=True):
    """Specks off, pinholes filled, colours a step crisper; symmetric as before."""
    c = c.copy()
    op = c[..., 3] > 0
    if not op.any():
        return c
    L = lum(c[..., :3].astype(float))
    bright = np.percentile(L[op], 80)
    # 1. loose specks: pieces of 1-2 squares, unless they are among the brightest (a sparkle meant to be there)
    lbl, n = ndimage.label(op, structure=N8)
    sizes = ndimage.sum(op, lbl, range(1, n + 1))
    peak = ndimage.maximum(L, lbl, range(1, n + 1))
    for i in range(n):
        if sizes[i] <= 3 and peak[i] < bright:
            c[lbl == i + 1] = 0
    op = c[..., 3] > 0
    # 1b. dim fringe: the darkest squares on the drawing's rim (a soft halo that blurs a light on a dark field), and
    # dim squares with at most one drawn neighbour (dust between the shapes)
    V = c[..., :3].max(-1).astype(float) / 255
    vmax = V[op].max()
    rim = op & ~ndimage.binary_erosion(op, structure=np.ones((3, 3), bool), border_value=0)
    nbrs = ndimage.convolve(op.astype(int), np.ones((3, 3), int), mode="constant") - op
    lit = ndimage.binary_dilation(op & (V > 0.7 * vmax), structure=np.ones((3, 3), bool))
    gone = rim & (V < 0.42 * vmax) & lit if halo else np.zeros_like(op)
    gone |= op & (nbrs == 0) & (L < bright)
    c[gone] = 0
    op = c[..., 3] > 0
    # 2. pinholes: an empty square with drawn squares on all four sides takes their commonest colour
    up, dn = np.roll(op, 1, 0), np.roll(op, -1, 0)
    lf, rt = np.roll(op, 1, 1), np.roll(op, -1, 1)
    hole = ~op & up & dn & lf & rt
    hole[0] = hole[-1] = False
    hole[:, 0] = hole[:, -1] = False
    for y, x in zip(*np.nonzero(hole)):
        nb = [tuple(c[y + dy, x + dx]) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))]
        best = max(set(nb), key=lambda v: (nb.count(v), lum(np.array(v[:3], float))))
        c[y, x] = best
    op = c[..., 3] > 0
    # 3. crisper colours: saturation and value pushed apart (each colour on its own, so the palette stays small)
    cols = {tuple(v) for v in c[op][:, :3]}
    m = {}
    for col in cols:
        h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in col))
        s2 = min(1.0, s * 1.25)
        v2 = min(1.0, max(0.0, (v - 0.45) * 1.3 + 0.5))
        if v > 0.88:                              # the cores a touch whiter
            s2 *= 0.8
        m[col] = tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(h, s2, v2))
    px = c[op][:, :3]
    c[op, :3] = np.array([m[tuple(v)] for v in px], np.uint8)
    return mirror_fix(c, mirror)


def halo(tag):
    """The dim rim is a halo on a light, except on the rings drawn in the ramp's dark steps (the weapon auras, the
    buff rings, the chakrams)."""
    return not (tag.startswith("mw_") or tag in ("q_s_on", "g_slow", "q_s_haste", "cre"))


def load(path):
    a = np.asarray(Image.open(path).convert("RGBA")).copy()
    a[a[..., 3] < 128] = 0
    a[..., 3][a[..., 3] > 0] = 255
    return a


def layouts():
    """picture -> [(frames, cell w, cell h)] per strip, from the pack's layout lines (16 px a game px)."""
    out = {}
    pat = re.compile(r"row of (\d+) equal .*? cells, image size \d+x\d+ \(each cell (\d+)x(\d+)")
    for name, *_, layout in PK.FX:
        out[name] = [(int(n), int(w) // 16, int(h) // 16) for n, w, h in pat.findall(layout)]
    return out


LAYOUT = layouts()


# a picture's strips in files of their own (Codex's delivery: the Moonshot pop's bolt apart from its burst)
FILES = {"q_c_pop": ["q_c_pop_bolt", "q_c_pop"]}


def manifest():
    path = os.path.join(CODEX, "manifest.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8-sig") as f:
        m = json.load(f)
    items = m.get("assets", m.get("strips", [])) if isinstance(m, dict) else m
    return {os.path.basename(it.get("file", "")): it for it in items if isinstance(it, dict)}


def cut(a, fn, n, cw, ch, y=0):
    if a.shape[1] < n * cw or a.shape[0] < y + ch:
        sys.exit(f"{fn} is {a.shape[1]}x{a.shape[0]}: no room for {n} cells of {cw}x{ch} at row {y}")
    return [a[y:y + ch, k * cw:(k + 1) * cw].copy() for k in range(n)]


def strips_of(pic):
    """The picture's strips as lists of cells. A file a strip (FILES) or one file with the strips one under another;
    each file's cells from manifest.json (pixel_1x_rect, or n cells of fw x fh side by side), else the pack's layout."""
    man = manifest()
    files = FILES.get(pic, [pic])
    if not all(os.path.isfile(os.path.join(CODEX, "pixel_1x", f"aphelios_fx_{f}.png")) for f in files):
        files = [pic]
    out = []
    for j, f in enumerate(files):
        fn = f"aphelios_fx_{f}.png"
        a = load(os.path.join(CODEX, "pixel_1x", fn))
        item = man.get(fn, {})
        frames = item.get("frames")
        if isinstance(frames, list) and frames and isinstance(frames[0], dict) and "pixel_1x_rect" in frames[0]:
            groups = {}
            for fr in frames:
                x, y, w, h = fr["pixel_1x_rect"]
                groups.setdefault(fr.get("strip", 0), []).append(a[y:y + h, x:x + w].copy())
            out += [groups[k] for k in sorted(groups)]
        elif {"frames", "frame_width", "frame_height"} <= set(item):
            out.append(cut(a, fn, int(item["frames"]), int(item["frame_width"]), int(item["frame_height"])))
        elif len(files) > 1:
            out.append(cut(a, fn, *LAYOUT[pic][j]))
        else:
            y = 0
            for n, cw, ch in LAYOUT[pic]:
                out.append(cut(a, fn, n, cw, ch, y))
                y += ch
    return out


def recolour(cell, w):
    """Calibrum's green moved square for square to weapon w's ramp (each colour the same step of its ramp)."""
    src = np.array(RAMP["cal"], float)
    dst = np.array(RAMP[w], np.uint8)
    out = cell.copy()
    op = cell[..., 3] > 0
    px = cell[op][:, :3].astype(float)
    out[op, :3] = dst[((px[:, None] - src[None]) ** 2).sum(2).argmin(1)]
    return out


def box(cells):
    """The union box of the frames' drawn squares: x0, x1, y0, y1 (inclusive)."""
    op = np.zeros(cells[0].shape[:2], bool)
    for c in cells:
        op |= c[..., 3] > 0
    ys, xs = np.nonzero(op)
    return xs.min(), xs.max(), ys.min(), ys.max()


def placed(tag):
    pic, k, mirror, _, anchor, spot, frames, w = FX[tag]
    cells = strips_of(pic)[k]
    if w:
        cells = [recolour(c, w) for c in cells]
    cells = [clean(c, mirror, halo(tag)) for c in cells]
    x0, x1, y0, y1 = box(cells)
    H = cells[0].shape[0]
    if anchor == "front":
        ax, ay = x1 + 0.5 - BALL, (y0 + y1 + 1) / 2
    elif anchor == "mid":
        ax, ay = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2
    elif anchor == "root":
        ax, ay = x0, (y0 + y1 + 1) / 2
    elif anchor == "feet":
        ax, ay = (x0 + x1 + 1) / 2, y1 + 1
    else:                                   # ("row", k): the cell's k-th row from the bottom
        ax, ay = (x0 + x1 + 1) / 2, H - anchor[1]
    ix, iy = int(math.floor(ax)), int(math.floor(ay))
    out = []
    for i, ms in frames:
        if i == EMPTY:
            out.append((np.zeros((3, 3, 4), np.uint8), float(ms)))
            continue
        if i >= len(cells):
            sys.exit(f"{tag}: frame {i + 1} of {len(cells)}")
        out.append((G.centre_frame(cells[i], int(round(spot[0])) - ix, int(round(spot[1])) - iy), float(ms)))
    return out, cells


def check(tag, cells):
    """Hard alpha, every frame drawn, the symmetry the pack asked (on each frame's drawn box)."""
    mirror = FX[tag][2]
    bad = []
    for k, c in enumerate(cells):
        al = c[..., 3]
        if not al.any():
            bad.append(f"{tag} {k + 1} empty")
            continue
        if set(np.unique(al)) - {0, 255}:
            bad.append(f"{tag} {k + 1} soft alpha")
        ys, xs = np.nonzero(al)
        t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        if mirror == "lr" and not (t == t[:, ::-1]).all():
            bad.append(f"{tag} {k + 1} not symmetric left to right ({int((t != t[:, ::-1]).any(-1).sum())} squares)")
        if mirror == "ud" and not (t == t[::-1]).all():
            bad.append(f"{tag} {k + 1} not symmetric top to bottom ({int((t != t[::-1]).any(-1).sum())} squares)")
        if mirror == "pt" and not (t == t[::-1, ::-1]).all():
            bad.append(f"{tag} {k + 1} not the same turned half round ({int((t != t[::-1, ::-1]).any(-1).sum())})")
    return bad


def review(out_dir, e):
    from PIL import ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for tag, seq_ in e.items():
        z = 3 if FX[tag][3] else 6
        tiles = []
        for f, ms in seq_:
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
        ImageDraw.Draw(r).text((2, 1), f"{tag} (red: the pivot, blue: the soles)", fill=(255, 255, 0))
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
    path = os.path.join(out_dir, "aphelios_fx_frames.png")
    sheet.save(path)
    print(path, sheet.size)


def prepare(delivery):
    """The parts of Codex's delivery the import reads, into assets/source/aphelios/codex_fx (the raw pictures stay in
    the delivery)."""
    os.makedirs(os.path.join(CODEX, "pixel_1x"), exist_ok=True)
    for f in sorted(os.listdir(os.path.join(delivery, "pixel_1x"))):
        if f.startswith("aphelios_fx_") and f.endswith(".png"):
            shutil.copy2(os.path.join(delivery, "pixel_1x", f), os.path.join(CODEX, "pixel_1x", f))
    for f in ("HANDOFF.md", "manifest.json", "generation-prompts.txt"):
        if os.path.isfile(os.path.join(delivery, f)):
            shutil.copy2(os.path.join(delivery, f), os.path.join(CODEX, f))
    have = {f[len("aphelios_fx_"):-4] for f in os.listdir(os.path.join(CODEX, "pixel_1x"))}
    missing = sorted({x[0] for x in PK.FX} - have)
    print("prepared", CODEX, "missing:", missing or "none")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", help="Codex's delivery folder (unzipped)")
    ap.add_argument("--review", help="write every effect's frames here")
    ap.add_argument("--partial", action="store_true", help="leave out the tags whose picture is not delivered yet")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    print("muzzles", {w: (round(x, 1), round(y, 1)) for w, (x, y) in MUZ.items()})
    e, bad, missing = {}, [], []
    have = lambda pic: os.path.isfile(os.path.join(CODEX, "pixel_1x", f"aphelios_fx_{pic}.png"))
    for tag in FX:
        if a.partial and not have(FX[tag][0]):
            missing.append(tag)
            continue
        e[tag], cells = placed(tag)
        bad += check(tag, cells)
    if bad:
        sys.exit("\n".join(bad))
    tables = {"league_aphelios_fx": {}, "league_aphelios_big": {}}
    for tag, seq_ in e.items():
        tables["league_aphelios_big" if FX[tag][3] else "league_aphelios_fx"][tag] = seq_
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        review(a.review, e)


if __name__ == "__main__":
    main()
