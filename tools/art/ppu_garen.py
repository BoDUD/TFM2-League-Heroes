#!/usr/bin/env python3
"""Garen's dense frames (PPU 2.5) read straight from his original pictures, no image model in between.

    python tools/art/ppu_garen.py                  # write assets/source/ppu/garen_<tag>.png (+ .json sizes)
    python tools/art/ppu_garen.py --review DIR     # garen_hd_<tag>.png (8x) and garen_hd_<tag>.gif
    python tools/art/ppu_garen.py --actions        # the actions too (attack, q_attack, skill, spin, ult, hit, dead)

The user, 2026-10-12: 「这个分支用来重建老英雄的 用PPU重建 先是盖伦 但是所有模型图生成就不拜托codex了 我们自己处理 因为也有原稿
对比了」, then 「按原稿走 密度2.5」. The originals are the GPT strips in assets/source/garen (garen_<tag>.png, round 3/4,
garen_ref_v3.png's chibi): drawn about 3.5 picture pixels to a square, so 2.5 x the 1x sprite (92 rows head to sole) is
their own density - every square is the area average of the picture under it, mapped to one palette for the whole hero.
The 1x sheet (Codex's step-2 redraw) is a different drawing; only its frame sizes, timing and standing point are kept:
an hd frame is round(2.5 x its 1x frame) round the same centre, the soles on the 1x soles' row. --write puts the idle
in (its 1x frames into the sheet, replacing the Codex idle: import_native.py --hero garen would bring that back - run
this again after it); the actions not redrawn yet are the 1x frames scaled (ppu_hd.py).

actions (the user, 2026-10-12: 「盖伦游戏里还是老模型 ... 你参考亚索那些怎么弄的啊」, then the idle's face in every
frame, the slashes and bursts out, the glowing gold blade kept): each strip's pictures one to a frame, read at the
strip's own scale (the median of 2.5 x the 1x frame's height over the picture's: every strip was drawn at its own size),
the palette of the idle, its sparkles and glints (parts under 2% of the figure) dropped, the feet - the lowest rows of
what is not blade - where the 1x frame's feet are; then the idle's head (hair, face, eyes; not the scarf) pasted where
the picture's face is (import_ppu_strips.paste_head searched round its skin), except where no face shows (the spin
seen from behind, the death lying down). The slash's white arc across attack picture 4 and the burst over q_attack
picture 5's legs leave nothing to keep, so those frames take the next picture; ult pictures 4-6's ground burst round
the planted blade is cleared (the blade kept); the skill's raised blade, guard and fist go back over the pasted head
(held beside it). The run (the user picked the idle for it, then 「走路时腿变形 你好好解决」 on lower legs slid whole -
the knee left the hip) is drawn the approved way (league_caitlyn, league_zeri, league_irelia): the dense idle's frame 0
without its legs, the hips fixed under the skirt, each ankle placed by the eight run phases, the knee solved at one
thigh and shin length, thigh and shin straight greaves in the idle's own greys with an outline ring, the idle's knee
guard on the knee and its boot on the ankle (the far leg - the one under the blade, image right: the body is turned to
the front-right - a step darker, half a cycle on); the cape behind the legs, the skirt, body and blade in front, the
whole body a row or two down as a foot lands, and where it stands on the 1x run's ground.

idle: the first picture of garen_idle.png is the design; the loop is that design breathing (tools/art/idle_breathe.py,
the 1x recipe: the body above the shins down 0-2 rows and a column forward, the head a frame late), the sword lifted out
first and stamped back with the body so the cut rows never step through the blade.
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import idle_breathe as IB  # noqa: E402
import import_native as N  # noqa: E402
import ppu_hd  # noqa: E402
import strips as G  # noqa: E402

PPU = 2.5
HERO = "garen"
PICS = os.path.join(ROOT, "assets", "source", "garen")
OUT = os.path.join(ROOT, "assets", "source", "ppu")
STEM = os.path.join(ROOT, "league", "champions", "league_garen")
ROWS = 92                       # head to sole in the design: round(2.5 x the 1x idle's 37 rows) (92.5, the lower)
ROWS_1X = 37                    # the 1x design (the sheet without league.dll), the old 1x idle's height
COLOURS = 40                    # the hero's palette (median cut of the design), plus the outline
FRAMES = {"idle": 6}            # pictures in each original strip
# the idle's blade from the guard to the tip, lifted out before the breath and stamped back moved with the body:
# (start, end) of its middle line and its half width, in 1x px from the idle frame's centre (both densities)
BLADE = ((-5.2, 1.7), (13.4, 9.9), 2.5)
# the idle's blade redrawn straight (the user: 「剑感觉有点歪？」 - the picture's edges are not parallel, 0.445 and 0.478,
# its lower edge bends flat near the tip and the point sits under the middle line; averaged down, the two edges
# stepped unevenly and the fuller wobbled). Measured on the picture (strip px, garen_idle.png picture 1): the middle
# line through (220, 459.05) at slope 0.4615, half width 16.6 across it (outline outside), from the guard (x 200)
# straight to x 322, then both edges meet on the middle line at x 345. Its colours: the picture's own, for each square
# the median of the picture's blade pixels at the same distance from the middle line, within 12 px along it.
# the hilt behind the near fist (the user, again: 「还是歪的」 - the picture's grip and pommel run from the guard to the
# left at slope 0.2, the blade at 0.46: the sword bent ~14 degrees at the guard). The grip ends in the fist instead, as
# oppi's Garen holds his: the pommel and the grip left of the fist (picture box x 76-107, rows 416-444; the fist starts
# at x 107) are taken out and what lies round them (the cape, the dark under-suit) fills the hole, nearest pixel first.
HILT_SRC = (76, 416, 107, 444)
BLADE_SRC = {"seed": (270, 470), "through": (220, 459.05), "slope": 0.4615, "half": 16.6, "start": 200,
             "bend": 322, "tip": 345, "along": 12}


def load_strip(tag):
    a = np.asarray(Image.open(os.path.join(PICS, f"garen_{tag}.png")).convert("RGBA")).astype(np.float32) / 255
    return G.split_strip(a, FRAMES[tag])


def regrid(fr, scale):
    """A picture's frame at `scale` (hd px per picture px), the soles' bottom edge on y = 0 and the feet's middle on
    x = 0: (array, column of its left edge, row of its top edge) in those coordinates."""
    x0, y0, x1, y1 = fr.bbox(0.5)
    fx = G.feet_mid(fr, scale, px=3)
    out, u0, r0 = G.render(fr, scale, scale, fx, y1, X0=0.0, Y0=-0.5, cut=0.5)
    return out, u0, r0, (fx, y1, scale)


def drop_pommel(fr):
    """HILT_SRC's pommel and grip out of idle picture 1 (strip px), filled from the nearest pixels round them; the
    cape's blue inside the box stays."""
    x0, y0, x1, y1 = HILT_SRC
    a = fr.a.copy()
    X0, Y0, X1, Y1 = x0 - fr.ox, y0 - fr.oy, x1 - fr.ox, y1 - fr.oy
    rgb = a[..., :3] * 255
    box = np.zeros(a.shape[:2], bool)
    box[Y0:Y1, X0:X1] = True
    cape = (rgb[..., 2] > 110) & (rgb[..., 0] < 50) & (rgb[..., 2] > rgb[..., 1] + 60)
    hole = box & (a[..., 3] > 0.5) & ~cape
    _, (iy, ix) = ndimage.distance_transform_edt(hole, return_indices=True)
    a[hole] = a[iy[hole], ix[hole]]
    fr.a = a
    return fr


def blade_coords(x, y):
    """Picture points -> (along the blade's middle line from its start, across it, + down) in picture px."""
    b = BLADE_SRC
    ux, uy = 1 / np.hypot(1, b["slope"]), b["slope"] / np.hypot(1, b["slope"])
    sx, sy = b["start"], b["through"][1] + b["slope"] * (b["start"] - b["through"][0])
    return (x - sx) * ux + (y - sy) * uy, -(x - sx) * uy + (y - sy) * ux


def straight_blade(a, u0, r0, geo, pal):
    """The idle's blade in the regridded picture `a` redrawn from BLADE_SRC: straight parallel edges, a point on the
    middle line, a one-square outline; squares of the old blade left outside take the body behind them or go clear.
    Gold and blue squares (the guard over the blade's root) are never painted. -> (picture, blade squares)."""
    b = BLADE_SRC
    fx, ay, s = geo
    pic = np.asarray(Image.open(os.path.join(PICS, "garen_idle.png")).convert("RGBA")).astype(int)
    op = pic[..., 3] > 128
    lum = 0.299 * pic[..., 0] + 0.587 * pic[..., 1] + 0.114 * pic[..., 2]
    sat = pic[..., :3].max(-1) - pic[..., :3].min(-1)
    lab, _ = ndimage.label(op & (lum > 60) & (sat < 70))
    old = ndimage.binary_fill_holes(lab == lab[b["seed"][1], b["seed"][0]])
    py, px = np.nonzero(old)
    pt, pd = blade_coords(px + 0.5, py + 0.5)
    pcol = pic[py, px, :3]
    L = blade_coords(b["bend"], b["through"][1] + b["slope"] * (b["bend"] - b["through"][0]))[0]
    T = blade_coords(b["tip"], b["through"][1] + b["slope"] * (b["tip"] - b["through"][0]))[0]
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    sx = fx + (u0 + xx) / s                                     # each square's middle in the picture
    sy = ay + (r0 + yy + 0.5) / s
    t, d = blade_coords(sx, sy)
    half = np.where(t <= L, b["half"], b["half"] * (T - t) / (T - L))
    inside = (t >= 0) & (t <= T) & (np.abs(d) <= half)
    rgb = a[..., :3].astype(int)
    body_col = (a[..., 3] > 0) & (rgb.max(-1) - rgb.min(-1) >= 70)   # the guard's gold and blue
    paint = inside & ~body_col
    out = a.copy()
    step = 0.5 / s                                              # half a square across, in picture px
    for y, x in zip(*np.nonzero(paint)):
        for win in (b["along"], 3 * b["along"]):
            sel = (np.abs(pd - d[y, x]) <= step) & (np.abs(pt - min(t[y, x], L)) <= win)
            if sel.sum() >= 3:
                break
        c = np.median(pcol[sel], axis=0) if sel.any() else pcol.mean(0)
        out[y, x, :3] = pal.colors[((pal.colors - c) ** 2).sum(1).argmin()].astype(np.uint8)
        out[y, x, 3] = 255
    ring = ~inside & ~body_col & (t >= -1 / s) & ndimage.binary_dilation(inside, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    dark = pal.colors[G.lum(pal.colors).argmin()].astype(np.uint8)
    out[ring, :3] = dark
    out[ring, 3] = 255
    # what the old blade and its outline covered beyond the new one (each square by the picture under its middle)
    old_line = ndimage.binary_dilation(old, iterations=4) & ~old & op & (lum < 70)
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    ok = (ix >= 0) & (iy >= 0) & (ix < pic.shape[1]) & (iy < pic.shape[0])
    was = np.zeros((h, w), bool)
    was[ok] = (old | old_line)[iy[ok], ix[ok]]
    left = was & ~inside & ~ring & ~body_col & (out[..., 3] > 0)
    out[left] = 0
    out = N.fill_behind(out, left)
    return out, int(paint.sum())


def design():
    """The idle design at both densities from picture 1 of garen_idle.png: {"hd": (array, u0, r0), "1x": ...} on
    ROWS and ROWS_1X rows, one palette (made on the hd one), crumbs dropped."""
    fr = drop_pommel(load_strip("idle")[0])
    x0, y0, x1, y1 = fr.bbox(0.5)
    hd = regrid(fr, ROWS / (y1 - y0))
    pal = G.Palette([hd[0]], colors=COLOURS)
    out = {}
    for k, rows in (("hd", ROWS), ("1x", ROWS_1X)):
        a, u0, r0, geo = hd if k == "hd" else regrid(fr, rows / (y1 - y0))
        a = G.drop_lonely(pal.apply(a))
        a, _ = straight_blade(a, u0, r0, geo, pal)
        out[k] = (a, u0, r0)
    return out, pal


COUNTS = {"attack": 6, "q_attack": 7, "skill": 4, "spin": 8, "ult": 8, "hit": 2, "dead": 7}
# frame -> the picture it takes instead of its own (0-based): the slash's white arc across attack picture 4's legs and
# the burst over q_attack picture 5's legs leave nothing to keep - the next picture's pose
SAME = {"attack": {3: 4}, "q_attack": {4: 5}}
# the ground burst round the planted blade in ult pictures 4-6: a box (picture px from the frame's top-left) whose
# glow goes, the blade's columns spared
BURST = {"ult": {i: {"box": (100, 143, 216, 196), "blade": (133, 167)} for i in (3, 4, 5)}}
# frames without the idle's head (0-based): the spin seen from behind, the death lying down
NO_HEAD = {"spin": {1, 2, 3, 4, 5}, "dead": {5, 6}}
# frames whose raised blade is held beside the head (its fist and guard in front of it): back over the pasted head
FRONT = {"skill": {0, 1, 2}}


def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def steel(a):
    """The blade's light greys and whites (a glowing blade's pale gold too)."""
    r, g, b = (a[..., c].astype(int) for c in range(3))
    sat = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    return (a[..., 3] > 0) & (lum(a) > 120) & ((sat < 45) | ((r > 220) & (g > 200)))


def feet(a):
    """(feet's middle x, soles' bottom edge y) of a frame: the lowest three rows of what is not blade."""
    op = (a[..., 3] > 0) & ~steel(a)
    sole = int(np.nonzero(op.any(1))[0].max())
    xs = np.nonzero(op[max(0, sole - 2):sole + 1].any(0))[0]
    return (xs.min() + xs.max() + 1) / 2.0, sole + 1.0


def head_of(design):
    """The dense idle's head: hair, skin, the eyes and the outline above the scarf (rows 3-42, columns 33-79 of the
    142 x 138 idle frame), the largest 4-connected part -> (head mask, face mask: its skin and eyes)."""
    a = design.astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    op = a[..., 3] > 0
    h, w = op.shape
    box = np.zeros((h, w), bool)
    box[3:43, 33:80] = True
    rows = np.arange(h)[:, None] * np.ones((1, w), int)
    skin = (r > 190) & (g > 140) & (g < 220) & (b > 100) & (b < 195) & (r > b + 35)
    hair = (r > 45) & (r < 175) & (g > 25) & (g < 120) & (b < 90) & (r > g + 10) & (r > b + 20)
    eye = (((b > 140) & (r < 110)) | ((lum(a) > 200) & (np.abs(r - b) < 40))) & (rows <= 33)
    m = op & box & (skin | hair | (lum(a) < 60) | eye)
    lab, n = ndimage.label(m)
    head = lab == (int(np.argmax(ndimage.sum(m, lab, range(1, n + 1)))) + 1)
    head = ndimage.binary_fill_holes(head) & op & box
    return head, head & (skin | eye)


def glow(a):
    """A burst's colours in a picture (float RGBA): bright yellow to white."""
    r, g, b = a[..., 0] * 255, a[..., 1] * 255, a[..., 2] * 255
    return (a[..., 3] > 0.05) & (0.299 * r + 0.587 * g + 0.114 * b > 150) & (r > 200) & (g > 140)


def unburst(fr, spec):
    """The burst's glow in spec's box cleared from the picture frame (the blade's columns kept) -> pixels cleared."""
    x0, y0, x1, y1 = spec["box"]
    b0, b1 = spec["blade"]
    m = np.zeros(fr.a.shape[:2], bool)
    m[y0:y1, x0:x1] = True
    m[:, b0:b1] = False
    gone = m & glow(fr.a)
    fr.a = fr.a.copy()
    fr.a[gone] = 0
    return int(gone.sum())


def drop_bits(a, keep=0.02):
    """Parts apart from the figure under `keep` of its largest part (sparkles, glints): clear."""
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n <= 1:
        return a
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    out = a.copy()
    for k, z in enumerate(sizes, 1):
        if z < keep * sizes.max():
            out[lab == k] = 0
    return out


def skin_mid(f):
    """The middle of the largest skin-coloured part in the frame's upper 70% (the face) -> (x, y) or None."""
    a = f.astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    skin = (a[..., 3] > 0) & (r > 190) & (g > 140) & (g < 220) & (b > 100) & (b < 195) & (r > b + 35)
    ys = np.nonzero((a[..., 3] > 0).any(1))[0]
    skin[ys.min() + int(0.7 * (ys.max() - ys.min())):] = False
    lab, n = ndimage.label(skin)
    if not n:
        return None
    yy, xx = np.nonzero(lab == int(np.argmax(ndimage.sum(skin, lab, range(1, n + 1)))) + 1)
    return float(xx.mean()), float(yy.mean())


def prop(f):
    """A blade held up with its guard and fist: steel greys and whites and gold with their dark outline, the parts of
    them reaching above the figure's top fifth -> mask."""
    a = f.astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    op = a[..., 3] > 0
    sat = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    metal = op & (((sat < 45) & (lum(a) > 90)) | ((r > 190) & (g > 110) & (b < 100) & (lum(a) > 140)))
    m = metal | (op & (lum(a) < 60) & ndimage.binary_dilation(metal, structure=np.ones((3, 3))))
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    ys = np.nonzero(op.any(1))[0]
    top = ys.min() + 0.2 * (ys.max() - ys.min())
    out = np.zeros(op.shape, bool)
    for v in range(1, n + 1):
        z = lab == v
        if np.nonzero(z)[0].min() < top:
            out |= z
    return out


def on_feet(a, one, margin=3):
    """A read picture on a dense frame round(PPU x the 1x frame `one`), its feet where the 1x frame's are (PPU x round
    the centre); the frame grown alike at both ends until it fits with `margin` clear."""
    fx, fy = feet(a)
    ox, oy = feet(one)
    h1, w1 = one.shape[:2]
    W, H = ppu_hd.hd_size(w1, h1, PPU)
    ys, xs = np.nonzero(a[..., 3])
    while True:
        dx = int(round((ox - w1 / 2) * PPU + W / 2 - fx))
        dy = int(round((oy - h1 / 2) * PPU + H / 2 - fy))
        if (ys.min() + dy >= margin and xs.min() + dx >= margin and ys.max() + dy < H - margin
                and xs.max() + dx < W - margin):
            out = np.zeros((H, W, 4), np.uint8)
            out[ys + dy, xs + dx] = a[ys, xs]
            return out
        W, H = W + 2, H + 2


def actions(pal, design):
    """{tag: [dense frame]} for COUNTS' tags from the pictures (see the module's notes), with a line per tag."""
    import import_ppu_strips as IPS
    sheet = ppu_hd.read_sheet(STEM)
    head, face = head_of(design)
    fy, fx = np.nonzero(face)
    face_mid = (float(fx.mean()), float(fy.mean()))
    out = {}
    for tag, n in COUNTS.items():
        a = np.asarray(Image.open(os.path.join(PICS, f"garen_{tag}.png")).convert("RGBA")).astype(np.float32) / 255
        pics = G.split_strip(a, n)
        for i, spec in BURST.get(tag, {}).items():
            unburst(pics[i], spec)
        frames = [pics[SAME.get(tag, {}).get(i, i)] for i in range(n)]
        ones = [f for f, _ in sheet[tag]]
        if len(ones) != n:
            sys.exit(f"{tag}: {n} pictures, {len(ones)} 1x frames")
        ratios = []
        for fr, one in zip(frames, ones):
            x0, y0, x1, y1 = fr.bbox(0.5)
            ys = np.nonzero((one[..., 3] > 0).any(1))[0]
            ratios.append(PPU * (ys.max() - ys.min() + 1) / (y1 - y0))
        s = float(np.median(ratios))
        done, notes = [], []
        for i, (fr, one) in enumerate(zip(frames, ones)):
            pic, _, _, _ = regrid(fr, s)
            f = on_feet(drop_bits(G.drop_lonely(pal.apply(pic))), one)
            mid = skin_mid(f)
            if i in NO_HEAD.get(tag, ()) or mid is None:
                notes.append("-")
            else:
                before = f.copy()
                guess = (int(round(mid[0] - face_mid[0])), int(round(mid[1] - face_mid[1])))
                res = IPS.paste_head(f, design, head, guess, 10, match=face, ring=False, hair_above=False)
                if i in FRONT.get(tag, ()):
                    m = prop(before)
                    ox, oy = res["at"]
                    cy, cx = np.nonzero(face)
                    ok = (cy + oy >= 0) & (cy + oy < f.shape[0]) & (cx + ox >= 0) & (cx + ox < f.shape[1])
                    m[cy[ok] + oy, cx[ok] + ox] = False          # never over the pasted face itself
                    f[m] = before[m]
                notes.append(f"{res['match']}%")
            done.append(f)
        out[tag] = done
        print(f"{tag}: scale {s:.4f}, head match " + " ".join(notes))
    return out


# the run, in the dense idle frame 0's pixels (142 x 138): the near leg's knee guard and boot (rows, cols, ends
# excluded) pasted on every knee and ankle; both legs' pixels below the skirt (taken out of the body); the hips; thigh and
# shin lengths; the boot's top row on the ground; each foot lands RUN_LEAD ahead of its hip and pushes off as far behind
RUN_KNEE = (76, 87, 25, 39)
RUN_BOOT = (86, 99, 17, 37)
RUN_LEGS = ((76, 99, 16, 40), (80, 99, 58, 90))
RUN_HIP = {"near": (34.0, 73.0), "far": (60.0, 75.0)}
RUN_LEG = (8.5, 7.5)
RUN_ANKLE = 87.0
RUN_LEAD = 5.5
RUN_FAR_DARK = 0.18
# one leg's eight phases (league_zeri's, approved; strips_irelia.RUN_PHASES): the ankle from its place in 1x squares of
# a longer leg (x RUN_SCALE: Garen's legs are shorter) and how far the foot is lifted
RUN_PHASES = [(0.0, 0), (-2.0, 0), (-4.0, 0), (-6.5, 1), (-8.0, 3), (-7.5, 4), (-2.5, 3.5), (0.0, 1.5)]
RUN_SCALE = 1.4
RUN_BOB = [2, 1, 0, 1, 2, 1, 0, 1]


def run(idle0, ones):
    """The 8 dense run frames from the dense idle's frame 0, each on round(PPU x its 1x run frame), the body where the
    idle's stands on the 1x run's ground (see the module's notes)."""
    import rigkit as K
    a = idle0.astype(int)
    h, w = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    op = a[..., 3] > 0
    navy = op & (b > r + 15) & (b > 60)                   # the cape's and the skirt's blues down to their darkest
    yy, xx = np.mgrid[0:h, 0:w]
    core = blade_mask(idle0, PPU) & (lum(a) >= 70)
    # the blade's steel and only the outline right against it (blade_mask reaches 1.5 px out: the far boot's dark)
    blade = core | (blade_mask(idle0, PPU) & (lum(a) < 70)
                    & ndimage.binary_dilation(core, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])))

    blue = op & (b > r + 40) & (b > 90)

    def box(r0, r1, c0, c1, skip):
        m = np.zeros((h, w), bool)
        m[r0:r1, c0:c1] = True
        return m & op & ~skip & ~blade

    # the pasted pieces never carry a blue (the cape's dark outline touches the knee guard); the legs taken out leave
    # the darkest blues with the body
    knee = box(*RUN_KNEE, navy)
    boot = box(*RUN_BOOT, navy) & ~knee
    legs = np.zeros((h, w), bool)
    for bx in RUN_LEGS:
        legs |= box(*bx, blue)
    cape = ndimage.binary_fill_holes(blue & (yy > 46) & (xx < 34))
    cape |= op & ndimage.binary_dilation(cape, iterations=2) & (lum(a) < 60) & ~legs & (xx < 34)
    body = op & ~legs & ~cape
    ky, kx = np.nonzero(knee)
    knee_mid = (kx.mean(), ky.mean())
    by, bx_ = np.nonzero(boot)
    boot_top = ((bx_.min() + bx_.max() + 1) / 2, by.min())
    # the greave's greys (lit, mid, dark) from the near leg's shin and boot, the outline's colour
    px = a[box(84, 92, 20, 36, navy)][:, :3]
    l = 0.299 * px[:, 0] + 0.587 * px[:, 1] + 0.114 * px[:, 2]
    grey, gl = px[(np.abs(px[:, 0] - px[:, 2]) < 30) & (l > 60)], l[(np.abs(px[:, 0] - px[:, 2]) < 30) & (l > 60)]
    lit, mid, dark = (tuple(int(c) for c in grey[np.argmin(np.abs(gl - v))]) for v in np.quantile(gl, [0.85, 0.55, 0.2]))
    outline = tuple(int(c) for c in a[op & (lum(a) < 40)][:, :3][0])

    def stamp(dst, m, ox, oy, shade=0.0):
        ys, xs = np.nonzero(m)
        Y, X = ys + oy, xs + ox
        ok = (Y >= 0) & (Y < dst.shape[0]) & (X >= 0) & (X < dst.shape[1])
        px = idle0[ys[ok], xs[ok]].astype(int)
        px[:, :3] = (px[:, :3] * (1 - shade)).astype(int)
        dst[Y[ok], X[ok]] = px.astype(np.uint8)

    def segment(cells, p0, p1, w0, w1):
        n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])) * 3) + 1
        for i in range(n + 1):
            x, y = p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n
            wd = w0 + (w1 - w0) * i / n
            for j in range(int(round(wd))):
                t = j / max(1, wd - 1)
                cells[(int(np.floor(y)), int(np.floor(x - wd / 2 + j)))] = dark if t < 0.3 else (mid if t < 0.75 else lit)

    fx, fy = feet(idle0)
    stood = [feet(one) for one in ones]
    sx = float(np.mean([x - one.shape[1] / 2 for (x, _), one in zip(stood, ones)]))
    sy = float(np.mean([y - one.shape[0] / 2 for (_, y), one in zip(stood, ones)]))
    pad = 12
    out = []
    for k, one in enumerate(ones):
        f = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)
        step = RUN_BOB[k]
        stamp(f, cape, pad, pad + step)
        for phase, far in (((k + 4) % 8, True), (k, False)):
            hx, hy = RUN_HIP["far" if far else "near"]
            hy += step
            dx, lift = RUN_PHASES[phase]
            ax, ay = hx + RUN_LEAD + RUN_SCALE * dx, RUN_ANKLE - RUN_SCALE * lift
            k1, _ = K.elbow((hx, hy), (ax, ay), RUN_LEG[0], RUN_LEG[1], bend=-1)
            k2, _ = K.elbow((hx, hy), (ax, ay), RUN_LEG[0], RUN_LEG[1], bend=1)
            kx_, ky_ = k1 if k1[0] >= k2[0] else k2                    # the knee forward
            cells = {}
            segment(cells, (hx, hy), (kx_, ky_), 10, 8)
            segment(cells, (kx_, ky_), (ax, ay), 8, 7)
            layer = np.zeros(f.shape, np.uint8)
            for (y, x), col in cells.items():
                if 0 <= y + pad < f.shape[0] and 0 <= x + pad < f.shape[1]:
                    layer[y + pad, x + pad, :3] = col
                    layer[y + pad, x + pad, 3] = 255
            m = layer[..., 3] > 0
            ring = ndimage.binary_dilation(m, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])) & ~m
            layer[ring, :3] = outline
            layer[ring, 3] = 255
            shade = RUN_FAR_DARK if far else 0.0
            if shade:
                layer[..., :3] = (layer[..., :3].astype(int) * (1 - shade)).astype(np.uint8)
            stamp(layer, boot, int(round(ax - boot_top[0])) + pad, int(round(ay - boot_top[1])) + pad, shade)
            stamp(layer, knee, int(round(kx_ - knee_mid[0])) + pad, int(round(ky_ - knee_mid[1])) + pad, shade)
            lm = layer[..., 3] > 0
            f[lm] = layer[lm]
        stamp(f, body, pad, pad + step)
        opf = f[..., 3] > 0
        holes = ndimage.binary_fill_holes(opf) & ~opf
        if holes.any():
            f = N.fill_behind(f, holes)
        # specks round the legs (the cape's frayed edge, bits of the old legs): pixels with <= 2 neighbours, small parts
        zone = np.zeros(f.shape[:2], bool)
        zone[pad + 70:] = True
        for _ in range(2):
            opf = f[..., 3] > 0
            nb = ndimage.convolve(opf.astype(int), np.ones((3, 3), int), mode="constant") - opf
            f[opf & (nb <= 2) & zone] = 0
        opf = f[..., 3] > 0
        lab, n = ndimage.label(opf, structure=np.ones((3, 3)))
        for v, z in enumerate(ndimage.sum(opf, lab, range(1, n + 1)), 1):
            if z < 30:
                f[lab == v] = 0
        # where the 1x run stands (the mean of its frames: the old run's own legs move); the body never sways
        h1, w1 = one.shape[:2]
        W, H = ppu_hd.hd_size(w1, h1, PPU)
        ys, xs = np.nonzero(f[..., 3])
        while True:
            dx_ = int(round(sx * PPU + W / 2 - (fx + pad)))
            dy_ = int(round(sy * PPU + H / 2 - (fy + pad)))
            if ys.min() + dy_ >= 3 and xs.min() + dx_ >= 3 and ys.max() + dy_ < H - 3 and xs.max() + dx_ < W - 3:
                break
            W, H = W + 2, H + 2
        g_ = np.zeros((H, W, 4), np.uint8)
        g_[ys + dy_, xs + dx_] = f[ys, xs]
        out.append(g_)
    return out


def write_strip(tag, frames, ones):
    """A tag's dense frames as ppu_hd.py's drawn strip: assets/source/ppu/garen_<tag>.png (left to right, 1 px apart,
    top-aligned) and garen_<tag>.json with the sizes when a frame is grown beyond round(PPU x its 1x frame)."""
    want = [ppu_hd.hd_size(o.shape[1], o.shape[0], PPU) for o in ones]
    sizes = [(f.shape[1], f.shape[0]) for f in frames]
    H = max(h for _, h in sizes)
    strip = np.zeros((H, sum(w + 1 for w, _ in sizes) - 1, 4), np.uint8)
    x = 0
    for f in frames:
        strip[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1] + 1
    Image.fromarray(strip).save(os.path.join(OUT, f"garen_{tag}.png"))
    side = os.path.join(OUT, f"garen_{tag}.json")
    if sizes != want:
        with open(side, "w", encoding="utf-8") as fh:
            json.dump({"sizes": [list(v) for v in sizes]}, fh)
    elif os.path.isfile(side):
        os.remove(side)
    return sum(1 for a, b in zip(sizes, want) if a != b)


def frame_1x(tag, i=0):
    return ppu_hd.read_sheet(STEM)[tag][i][0]


# where the Codex 1x frames stood (soles' bottom edge, feet's middle from the frame's centre; the frame's size), kept
# once a tag is replaced in the sheet (the idle since --write)
STOOD = {"idle": (11.5, -4.0, (45, 55))}


def standing(tag):
    """Where the 1x frame 0 of `tag` stands: (soles' bottom edge, feet's middle) in 1x px from the frame's centre."""
    if tag in STOOD:
        return STOOD[tag]
    one = frame_1x(tag)
    op = one[..., 3] > 0
    sole = int(np.nonzero(op.any(1))[0].max())
    xs = np.nonzero(op[sole - 1:sole + 1].any(0))[0]
    h, w = one.shape[:2]
    return sole + 1 - h / 2, (xs.min() + xs.max() + 1) / 2 - w / 2, (w, h)


def place(a, u0, r0, size, sole_dy, feet_dx, k=1.0, margin=0):
    """`a` (feet-relative, see regrid) on an empty (w, h) frame whose centre stands sole_dy over the soles' bottom
    edge and feet_dx right of the feet's middle (1x px; k = the frame's px per 1x px). None when a pixel would come
    within `margin` of the frame's edge."""
    w, h = size
    out = np.zeros((h, w, 4), np.uint8)
    sole_row = int(round(h / 2 + sole_dy * k)) - 1
    feet_x = w / 2 + feet_dx * k
    ys, xs = np.nonzero(a[..., 3])
    Y = sole_row + 1 + r0 + ys
    X = np.floor(feet_x + u0 + xs).astype(int)
    if Y.min() < margin or X.min() < margin or Y.max() >= h - margin or X.max() >= w - margin:
        return None
    out[Y, X] = a[ys, xs]
    return out


def fit(pair, sole_dy, feet_dx, size, margin=(2, 3)):
    """Both densities placed: the 1x frame grown from `size` (odd, alike at both ends, so its centre stays) until
    both fit with `margin` (1x, hd) clear all round; the hd frame is round(PPU x the 1x frame)."""
    w, h = size
    while True:
        W, H = ppu_hd.hd_size(w, h, PPU)
        one = place(*pair["1x"], (w, h), sole_dy, feet_dx, 1.0, margin[0])
        hd = place(*pair["hd"], (W, H), sole_dy, feet_dx, PPU, margin[1])
        if one is not None and hd is not None:
            return one, hd
        a1 = place(*pair["1x"], (w + 200, h + 200), sole_dy, feet_dx, 1.0)
        ah = place(*pair["hd"], (W + 500, H + 500), sole_dy, feet_dx, PPU)
        grow_w = grow_h = False
        for arr, m, bw, bh in ((a1, margin[0], w, h), (ah, margin[1], W, H)):
            ys, xs = np.nonzero(arr[..., 3])
            pad_x = (arr.shape[1] - bw) // 2
            pad_y = (arr.shape[0] - bh) // 2
            grow_w |= xs.min() - pad_x < m or xs.max() - pad_x >= bw - m
            grow_h |= ys.min() - pad_y < m or ys.max() - pad_y >= bh - m
        w, h = w + 2 * grow_w, h + 2 * grow_h


def blade_mask(a, k):
    """BLADE's drawn pixels in the frame `a` of k px per 1x px (pixel centres within the half width of the line,
    from its start on; the dark outline squares up to 0.6 1x px further)."""
    (x0, y0), (x1, y1), r = BLADE
    h, w = a.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    px = ((xs + 0.5) - w / 2) / k
    py = ((ys + 0.5) - h / 2) / k
    dx, dy = x1 - x0, y1 - y0
    t = ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)
    d = np.hypot(px - (x0 + t * dx), py - (y0 + t * dy))
    dark = a[..., :3].astype(int).sum(-1) < 210                          # its outline, a square further out
    return (a[..., 3] > 0) & (t >= 0) & (((t <= 1.08) & (d <= r)) | (dark & (t <= 1.25) & (d <= r + 0.6)))


def eye(a):
    """The near eye's iris: the middle of the bright blue squares in the top third (the head point for the nod)."""
    top = int(np.nonzero(a[..., 3].any(1))[0].min())
    h = a.shape[0]
    rgb = a[..., :3].astype(int)
    blue = (a[..., 3] > 0) & (rgb[..., 2] > 150) & (rgb[..., 2] > rgb[..., 0] + 80)
    blue[top + (h - top) // 3:] = False
    ys, xs = np.nonzero(blue)
    return float(xs.mean()), float(ys.mean())


def breathe(a, k):
    """8 idle frames of the design `a` (k px per 1x px): the blade lifted out (the squares it covered filled with the
    body round them), idle_breathe.py's breath at k x its 1x rows (rounded: the same dip on screen), the blade stamped back with the body."""
    blade = blade_mask(a, k)
    body_rows = [int(round(v * k)) for v in IB.BODY]
    lift = a.copy()
    lift[blade] = 0
    lift = N.fill_behind(lift, blade)
    frames, rows = IB.breathe(lift, eye(a), body=body_rows)
    ys, xs = np.nonzero(blade)
    out = []
    for f, dip, lean in zip(frames, body_rows, IB.SWAY):
        f[ys + 2 + dip, xs + 2 + lean] = a[ys, xs]
        out.append(np.ascontiguousarray(f[2:-2, 2:-2]))
    return out, rows, int(blade.sum())


def gif(frames, path, zoom, ms):
    bg = (90, 120, 90, 255)
    ims = []
    for f in frames:
        im = Image.new("RGBA", (f.shape[1], f.shape[0]), bg)
        im.alpha_composite(Image.fromarray(f))
        ims.append(im.convert("RGB").resize((f.shape[1] * zoom, f.shape[0] * zoom), Image.NEAREST))
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=ms, loop=0)


def write_idle(idle_1x, idle_hd):
    """The 1x idle into league_garen's sheet (the other tags as they are) and the hd idle as ppu_hd.py's drawn strip
    (assets/source/ppu/garen_idle.png: the frames left to right, 1 px apart, each round(PPU x its 1x frame))."""
    sheet = ppu_hd.read_sheet(STEM)
    sheet = {t: fr for t, fr in sheet.items() if not t.startswith(ppu_hd.PREFIX)}
    sheet["idle"] = [(f, IB.MS) for f in idle_1x]
    for a, b in zip(idle_1x, idle_hd):
        if ppu_hd.hd_size(a.shape[1], a.shape[0], PPU) != (b.shape[1], b.shape[0]):
            sys.exit(f"hd idle frame {b.shape[1]}x{b.shape[0]} is not round({PPU} x {a.shape[1]}x{a.shape[0]})")
    G.write_sheet(STEM, sheet)
    H = max(b.shape[0] for b in idle_hd)
    strip = np.zeros((H, sum(b.shape[1] + 1 for b in idle_hd) - 1, 4), np.uint8)
    x = 0
    for b in idle_hd:
        strip[:b.shape[0], x:x + b.shape[1]] = b
        x += b.shape[1] + 1
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(strip).save(os.path.join(OUT, "garen_idle.png"))
    print(f"league_garen idle: {len(idle_1x)} x {idle_1x[0].shape[1]}x{idle_1x[0].shape[0]} (1x), "
          f"assets/source/ppu/garen_idle.png {strip.shape[1]}x{strip.shape[0]} (hd)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write review pictures here")
    ap.add_argument("--write", action="store_true",
                    help="the idle into league_garen's sheet (1x) and assets/source/ppu/garen_idle.png (hd); then run "
                         "tools/art/ppu_hd.py --hero garen")
    ap.add_argument("--actions", action="store_true",
                    help="the other actions' dense strips from their pictures (assets/source/ppu/garen_<tag>.png); then "
                         "run tools/art/ppu_hd.py --hero garen")
    args = ap.parse_args()
    pair, pal = design()
    sole_dy, feet_dx, size = standing("idle")
    one, hd = fit(pair, sole_dy, feet_dx, size)
    print("idle 1x", one.shape[1], "x", one.shape[0], "(was", size, ") hd", hd.shape[1], "x", hd.shape[0],
          "colours", len(pal.colors))
    idle_hd, rows, n = breathe(hd, PPU)
    idle_1x, rows1, n1 = breathe(one, 1)
    print("idle breath hd: cut cost", rows["dip_cost"], "lean", rows["lean_cost"], "nod", rows["neck"] is not None,
          "blade", n, "| 1x:", rows1["dip_cost"], rows1["lean_cost"], rows1["neck"] is not None, "blade", n1)
    if args.write:
        write_idle(idle_1x, idle_hd)
    if args.actions or args.review:
        made = actions(pal, idle_hd[0])
        sheet = ppu_hd.read_sheet(STEM)
        made["run"] = run(idle_hd[0], [f for f, _ in sheet["run"]])
        for tag, frames in made.items():
            if args.actions:
                grown = write_strip(tag, frames, [f for f, _ in sheet[tag]])
                print(f"assets/source/ppu/garen_{tag}.png: {len(frames)} frames, {grown} grown")
            if args.review:
                gif(frames, os.path.join(args.review, f"garen_hd_{tag}.gif"), 4, 100)
    if args.review:
        os.makedirs(args.review, exist_ok=True)
        Image.fromarray(hd).resize((hd.shape[1] * 6, hd.shape[0] * 6), Image.NEAREST).save(
            os.path.join(args.review, "garen_design_hd_6x.png"))
        Image.fromarray(one).resize((one.shape[1] * 15, one.shape[0] * 15), Image.NEAREST).save(
            os.path.join(args.review, "garen_design_1x_15x.png"))
        gif(idle_hd, os.path.join(args.review, "garen_hd_idle.gif"), 4, IB.MS)
        gif(idle_1x, os.path.join(args.review, "garen_1x_idle.gif"), 10, IB.MS)


if __name__ == "__main__":
    main()
