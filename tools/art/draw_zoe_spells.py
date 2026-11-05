#!/usr/bin/env python3
"""Zoe's stolen summoner spells, drawn square by square (the user, 2026-10-22: 「给我展现一个比如佐伊w现在召唤师技能的
gif图？」 -> only Exhaust showed anything; 「加啊」「地面上最好也要有图标显示」, picked「放的时候地上亮图标」).

    python tools/art/draw_zoe_spells.py [--sheets spells,spells_1x,icons] [--review out.png]

Writes three sheets (#sheet.png + #anim.fanim) under league/effects (the icons need assets/source/zoe/summoner_icons):
  * league_zoe_spells      Flash's pictures, a dense effect sheet at PPU 2 (league_main hd.rs EFFECTS + DRAWN_EFFECTS:
                           every tag has its hd_ twin, the 1x frames are the dense ones halved);
  * league_zoe_spells_1x   the pictures that ride a unit (the buffs' views and Cleanse), drawn at a square a game px - a
                           plain sheet the game draws itself (0.6.0, 2026-11-05, the user: 「捡起来的召唤师技能的技能特效
                           完全错位」): league.dll's effect draw (hd_engine src/view.rs effect_detour) shrinks only what the
                           view node draw draws - pictures played at a point (Flash, the icons). A dense sheet's buff view
                           or following effect never passes there (11-05 log: no "league_zoe_spells: effect picture drawn"
                           line through Heal, Ghost, Barrier, Ignite, Exhaust and Cleanse; nor for league_yuumi_ride), so it
                           stayed PPU times big, its top-left corner where a 1 / PPU frame's would be: 2x, hanging right and
                           down from the unit by half its size;
  * league_zoe_spell_icons the icons, dense at PPU 3 (DRAWN_EFFECTS, played at points).
The add-on league_zoe plays them (addons/league_zoe/src/lib.rs summon / shards; the views from tools/kit/build_zoe.py
--native):

  * sg_<spell>  the spell's icon lighting up on the ground in front of her feet as she casts it (a ring round her feet,
                the icon popping in white, held, dithered away; ~0.8 s, z -1, where she stood);
  * ss_<spell>  the same icon over a spell shard lying on the ground (one picture for one stamp, 15 ticks): the shard
                cycles through the seven - which one it gives is picked when she picks it up;
  * s_flash     a starburst where she blinks from and where she lands;   s_cleanse  a ring sweeping up her body;
  * s_flash_trail  one puff of the golden streak between the two (played at points along the way);
  * s_barrier   a golden bubble round her;                               s_heal     green crosses rising (a buff's view);
  * s_ignite    flames on the burning one (a buff's view);               s_exhaust  a dusty cloud over his head;
  * s_ghost     cyan wisps round her feet (a buff's view, under her).

Every picture is symmetric left to right (the client never mirrors an effect) except the icons' own symbols. Squares
are counted from the pivot (the unit's / the point's position): the soles are 11 game px = 22 squares under it (11 in
the 1x sheet's own drawings, `*_1x`: the dense drawings at their sizes, redrawn a square a game px - halving the dense
squares broke every thin ring and the mirror).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
from build_zoe import P  # noqa: E402

PRE = chr(92) * 2 + "?" + chr(92)
OUT = os.path.join(ROOT, "league", "effects", "league_zoe_spells")
OUT_1X = os.path.join(ROOT, "league", "effects", "league_zoe_spells_1x")
OUT_ICONS = os.path.join(ROOT, "league", "effects", "league_zoe_spell_icons")
ICONS = os.path.join(ROOT, "assets", "source", "zoe", "summoner_icons")
PPU = 2                                         # the spells' own pictures
SY = 11 * PPU                                   # the soles under the pivot
SY1 = 11                                        # the same in the 1x sheet
PPU_I = 3                                       # the icons: 32 squares of League's 64-px icon still read (22 did not)
SYI = 11 * PPU_I
ICON = 32
SHOW_MS = P["e_show"] * 1000 / 60               # a shard re-stamped every 15 ticks
SPELLS = ["flash", "ignite", "exhaust", "heal", "barrier", "ghost", "cleanse"]
OUTLINE = (16, 12, 20)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# the spell's colours, light to dark (its icon's: Flash's yellow, Ignite's flame, Exhaust's amber, Heal's green,
# Barrier's gold, Ghost's blue, Cleanse's teal)
PAL = {k: dict(zip(("core", "mid", "edge", "out"), map(rgb, v.split()))) for k, v in {
    "flash": "FFFFFF FFF2A8 FFC838 8A5A18",
    "ignite": "FFFBE0 FFD050 FF8A28 A83414",
    "exhaust": "FFF0C8 E8C080 C08A4A 6A4426",
    "heal": "FFFFFF CCFFC0 74E070 2A7A3C",
    "barrier": "FFFFF0 FFE48C F2B43A 8A5A14",
    "ghost": "FFFFFF CCE8FF 6EB8FF 1E5AB8",
    "cleanse": "FFFFFF C8FFF4 6EE6D2 1E7A78",
}.items()}


# ------------------------------------------------------------------ a frame: squares round the pivot

class F:
    W, H = 200, 220
    OX, OY = 100, 120                           # the pivot: the square boundary at (OX, OY)

    def __init__(self, ppu=PPU):
        self.a = np.zeros((self.H, self.W, 4), np.uint8)
        self.ppu = ppu

    def put(self, x, y, col):
        X, Y = self.OX + int(x), self.OY + int(y)
        if 0 <= X < self.W and 0 <= Y < self.H:
            self.a[Y, X] = (*col, 255)

    def sym(self, x, y, col):
        """x >= 0: the square and its mirror (x -> -1 - x)."""
        self.put(x, y, col)
        self.put(-1 - x, y, col)

    def paste(self, arr, x0, y0, keep=None):
        h, w = arr.shape[:2]
        for y in range(h):
            for x in range(w):
                if arr[y, x, 3] and (keep is None or keep(x, y)):
                    self.put(x0 + x, y0 + y, tuple(int(v) for v in arr[y, x, :3]))

    def ring(self, cy, rx, ry, col, t=1.0, keep=None):
        """An ellipse's outline about (0, cy), symmetric; `keep(x, y)` thins it."""
        for y in range(int(cy - ry - 2), int(cy + ry + 2)):
            for x in range(0, int(rx + 2)):
                v = math.hypot((x + 0.5) / rx, (y + 0.5 - cy) / ry)
                if abs(v - 1) * min(rx, ry) <= t / 2 + 0.3 and (keep is None or keep(x, y)):
                    self.sym(x, y, col)

    def spark(self, x, y, col_core, col_arm, n=1, mirror=True):
        """A four-pointed sparkle centred on square (x, y): arms n long."""
        pts = [(x, y, col_core)] + [(x + s * k, y, col_arm) for k in range(1, n + 1) for s in (-1, 1)] + \
              [(x, y + s * k, col_arm) for k in range(1, n + 1) for s in (-1, 1)]
        for px, py, c in pts:
            if mirror:
                self.put(px, py, c)
                self.put(-1 - px, py, c)
            else:
                self.put(px, py, c)

    def crop(self):
        """The frame centred on the pivot, its width and height whole multiples of 2 x PPU (the 1x frame is it / PPU,
        centred too)."""
        ys, xs = np.nonzero(self.a[..., 3])
        if not len(xs):
            return np.zeros((2 * self.ppu, 2 * self.ppu, 4), np.uint8)
        hx = max(self.OX - xs.min(), xs.max() + 1 - self.OX)
        hy = max(self.OY - ys.min(), ys.max() + 1 - self.OY)
        hx += -hx % self.ppu
        hy += -hy % self.ppu
        return self.a[self.OY - hy:self.OY + hy, self.OX - hx:self.OX + hx].copy()


def checker(n):
    """Fade masks: 0 all, 1 half (a checkerboard), 2 a quarter."""
    return [None, lambda x, y: (x + y) % 2 == 0, lambda x, y: x % 2 == 0 and y % 2 == 0][n]


# ------------------------------------------------------------------ the effects

def astroid(f, cy, r, c, keep=None):
    for y in range(int(cy - r - 1), int(cy + r + 1)):
        for x in range(0, int(r + 1)):
            dx, dy = x + 0.5, abs(y + 0.5 - cy)
            a = (dx ** (2 / 3) + dy ** (2 / 3)) / r ** (2 / 3)
            if a <= 1 and (keep is None or keep(x, y)):
                f.sym(x, y, c["core"] if a < 0.45 else c["mid"] if a < 0.75 else c["edge"])


def flash():
    """Where she blinks from and where she lands (the user, 2026-11-01: 「闪现现在怎么看不出效果？」 - the old one was
    10-22 squares and 0.22 s): a starburst as tall as she is with a ring bursting out to 17 px, a flat ring on the
    ground round her feet, glints drifting up as it fades; 0.5 s."""
    c = PAL["flash"]
    cy = SY - 26
    out = []
    for k, ms in enumerate([40, 50, 60, 60, 70, 70, 80, 90]):
        f = F()
        if 1 <= k <= 5:                             # the ground ring at her feet, widening and thinning
            f.ring(SY, 16 + 5 * k, 4 + 1.2 * k, c["mid"] if k < 3 else c["edge"] if k < 5 else c["out"],
                   1.5 if k < 3 else 1, keep=None if k < 3 else checker(1 if k < 5 else 2))
        if k == 0:
            astroid(f, cy, 16, c)
            f.ring(cy, 10, 10, c["core"], 1.5)
        elif k == 1:
            f.ring(cy, 18, 18, c["core"], 2)
            astroid(f, cy, 28, c)
        elif k == 2:
            f.ring(cy, 26, 26, c["mid"], 2)
            astroid(f, cy, 20, c)
            for d in (14, 20):
                f.spark(d, cy - d, c["core"], c["mid"], 2)
                f.spark(d, cy + d, c["mid"], c["edge"], 1)
        elif k == 3:
            f.ring(cy, 31, 31, c["edge"], 1.5, keep=checker(1))
            astroid(f, cy, 13, c)
            for d in (19, 25):
                f.spark(d, cy - d, c["core"], c["mid"], 2)
                f.spark(d, cy + d, c["mid"], c["edge"], 1)
        elif k == 4:
            f.ring(cy, 34, 34, c["out"], 1, keep=checker(2))
            astroid(f, cy, 8, c)
            f.spark(22, cy - 28, c["core"], c["mid"], 2)
            f.spark(28, cy + 16, c["mid"], c["edge"], 1)
            f.spark(8, cy - 34, c["mid"], c["edge"], 1)
        else:                                       # glints drifting up and going out
            up = 6 * (k - 4)
            f.spark(0, cy, c["core"] if k == 5 else c["mid"], c["mid"] if k == 5 else c["edge"], 7 - k)
            f.spark(20, cy - 30 - up, c["mid"], c["edge"], 1 if k < 7 else 0)
            f.spark(10, cy - 40 - up, c["edge"], c["out"], 1 if k < 6 else 0)
            if k < 7:
                f.spark(26, cy + 10 - up, c["edge"], c["out"], 0)
        out.append((f.crop(), ms))
    return out


def flash_trail():
    """s_flash_trail: one puff of the golden streak Flash leaves between where she was and where she lands (the add-on
    plays it at points along the way, so it lies the right way whichever way she blinks): a sparkle at her chest height
    that blooms, sheds glints and fades; 0.43 s."""
    c = PAL["flash"]
    cy = SY - 26
    out = []
    for k, ms in enumerate([50, 70, 90, 100, 120]):
        f = F()
        if k == 0:
            astroid(f, cy, 9, c)
        elif k == 1:
            astroid(f, cy, 7, c)
            f.ring(cy, 10, 10, c["mid"], 1, keep=checker(1))
        elif k == 2:
            astroid(f, cy, 5, c, keep=checker(1))
            f.spark(7, cy - 9, c["core"], c["mid"], 1)
            f.spark(9, cy + 5, c["mid"], c["edge"], 1)
        elif k == 3:
            f.spark(0, cy, c["mid"], c["edge"], 1)
            f.spark(8, cy - 13, c["mid"], c["edge"], 1)
        else:
            f.spark(8, cy - 17, c["edge"], c["out"], 0)
        out.append((f.crop(), ms))
    return out


def cleanse():
    c = PAL["cleanse"]
    out = []
    left = [(14, SY - 6), (6, SY - 16), (12, SY - 28), (4, SY - 38)]        # sparkles the ring leaves behind
    for k, ms in enumerate([50, 60, 60, 70, 80, 90]):
        f = F()
        if k < 4:
            cy = SY - 12 * k
            f.ring(cy, 16, 5, c["core"] if k else c["mid"], 2, keep=lambda x, y: (y < cy) or (x + y) % 2 == 0)
            for j in range(k):
                x, y = left[j]
                f.spark(x, y, c["mid"], c["edge"], 1)
        elif k == 4:
            for j in range(4):
                x, y = left[j]
                f.spark(x, y - 4, c["edge"], c["out"], 0)
            for x, y in ((10, SY - 50), (2, SY - 56)):
                f.spark(x, y, c["core"], c["mid"], 2)
        else:
            for x, y in ((10, SY - 54), (2, SY - 60)):
                f.spark(x, y, c["mid"], c["edge"], 1)
        out.append((f.crop(), ms))
    return out


def barrier():
    """A golden shell over her while the shield lasts (a buff's view, looped; the user: 「屏障罩住人啊」): an egg from
    under her soles to over her hair, a sparse gold shimmer inside it drifting up, its shine sliding down a side,
    sparkles twinkling."""
    c = PAL["barrier"]
    # 17 px up, 15 x 22 px half-axes: a shell hugging her (soles - 5 px .. 39 px over them, her mane in it), League's
    # thin shell. It was 22 x 26 px (44 x 52 across) - and the game drew it twice that, 88 x 104 px, three times her
    # height, until league_main's DRAWN_EFFECTS listed this sheet (the user, 2026-11-03: 「大橙圈是召唤师技能屏障特效
    # 你弄的太大了吧」)
    cy, rx, ry = SY - 34, 30, 44
    out = []
    for k in range(4):
        f = F()
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(0, rx + 1):
                v = math.hypot((x + 0.5) / rx, (y + 0.5 - cy) / ry)
                if v < 0.93 and x % 4 == 1 and (y + 2 * k + (x // 4) * 2) % 8 == 0:
                    f.sym(x, y, c["mid"] if v > 0.6 else c["core"])
        f.ring(cy, rx, ry, c["edge"], 1.5)
        f.ring(cy, rx - 1.6, ry - 1.6, c["out"], 1, keep=lambda x, y: (x + y) % 2 == 0)
        a0 = math.pi * (0.30 + 0.08 * k)
        for x in range(0, rx + 1):
            for y in range(int(cy - ry - 1), int(cy + ry + 1)):
                th = math.atan2(-(y + 0.5 - cy) * rx / ry, x + 0.5)
                v = math.hypot((x + 0.5) / rx, (y + 0.5 - cy) / ry)
                if abs(v - 0.92) <= 0.025 and abs(th - a0) <= 0.24:
                    f.sym(x, y, c["core"])
        f.spark(int(rx * 0.55), int(cy - ry * 0.66), c["core"], c["mid"], 1 if k % 2 else 2)
        f.spark(int(rx * 0.86), int(cy + ry * 0.2), c["mid"], c["edge"], 1 if k % 2 == 0 else 0)
        out.append((f.crop(), 120))
    return out

def flame(f, bx, by, h, w, phase, c):
    """One tongue of fire standing on (bx, by), mirrored; its tip sways with the phase."""
    for y in range(int(by - h), int(by) + 1):
        v = (by - y) / h
        hw = w * max(0.0, 1 - v) ** 0.9 * min(1.0, 0.45 + v * 2.2)
        sway = 1.6 * math.sin(phase + v * 3.0) * v
        for x in range(int(bx - w - 3), int(bx + w + 3)):
            u = abs(x + 0.5 - (bx + sway)) / max(hw, 0.35)
            if u <= 1:
                col = c["core"] if (u < 0.35 and v < 0.55) else c["mid"] if u < 0.7 and v < 0.8 else c["edge"]
                if v > 0.88:
                    col = c["out"]
                f.sym(x, y, col)


def blob(f, cx, cy, rx, ry, col):
    for y in range(int(cy - ry - 1), int(cy + ry + 1)):
        for x in range(int(cx - rx - 1), int(cx + rx + 1)):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                f.put(x, y, col)


def cross(f, x, y, arm, core, edge, out):
    """A plus two squares thick, `arm` squares each way from its 2 x 2 middle, outlined; mirrored."""
    sq = set()
    for i in range(-arm, arm + 2):
        for j in (0, 1):
            sq.add((x + i, y + j))
            sq.add((x + j, y + i))
    ring = {(a + dx, b + dy) for a, b in sq for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - sq
    for a, b in ring:
        f.sym(a, b, out)
    for a, b in sq:
        mid = (a in (x, x + 1)) and (b in (y, y + 1))
        f.sym(a, b, core if mid or abs(a - x - 0.5) + abs(b - y - 0.5) < arm * 0.6 else edge)


def heal():
    """Green crosses rising round the body (loops while the buff lasts), a dotted ring on the ground."""
    c = PAL["heal"]
    out = []
    crosses = [(12, 0), (5, 16)]                                    # (x, phase in squares) mirrored pairs
    for k in range(4):
        f = F()
        f.ring(SY, 18, 5, c["edge"], 1, keep=lambda x, y, k=k: (x + y + k) % 3 == 0)
        for x, ph in crosses:
            rise = (ph + 8 * k) % 32
            y = SY - 10 - rise
            if rise < 22:
                cross(f, x, y, 2, c["core"], c["mid"], c["out"])
            else:
                cross(f, x, y, 1, c["mid"], c["edge"], c["out"])
        out.append((f.crop(), 120))
    return out


def ignite():
    """Flames licking up his sides and shoulders, embers rising: loops while he burns."""
    c = PAL["ignite"]
    out = []
    for k in range(4):
        f = F()
        ph = k * math.pi / 2
        flame(f, 13, SY - 14, 24 + 3 * math.sin(ph), 5, ph, c)
        flame(f, 6, SY - 28, 14 + 2 * math.cos(ph), 3.4, ph + 1.3, c)
        flame(f, 2, SY - 6, 12 + 2 * math.sin(ph + 2), 3, ph + 2.6, c)
        for j, (x, base) in enumerate(((9, SY - 46), (17, SY - 52), (4, SY - 58))):
            y = base - 5 * ((k + j) % 4)
            f.put(x + (k + j) % 2, y, c["mid"] if (k + j) % 4 < 2 else c["edge"])
            f.put(-1 - x - (k + j + 1) % 2, y - 3, c["edge"])
        out.append((f.crop(), 100))
    return out


DUST = {"dark": rgb("3A302A"), "mid": rgb("6C5E52"), "light": rgb("9C8C78")}


def exhaust():
    """A grey dust cloud over his head with the drained amber spiral turning in it, dust drooping from its ends and
    amber chevrons sinking down his sides (weakened)."""
    c = PAL["exhaust"]
    cy = SY - 86                                    # over a 41-px champion's head
    lumps = ((0, -1, 8), (8, 0, 6), (-9, 0, 6), (15, 2, 4), (-16, 2, 4), (4, 3, 5), (-5, 3, 5))
    out = []
    for k in range(4):
        f = F()
        for cx, dy, r in lumps:
            blob(f, cx, cy + dy, r + 1, r * 0.7 + 1, DUST["dark"])
        for cx, dy, r in lumps:
            blob(f, cx, cy + dy, r, r * 0.7, DUST["mid"])
        for cx, dy, r in ((-2, -3, 5), (7, -2, 3), (-11, -1, 3)):
            blob(f, cx, cy + dy, r, r * 0.55, DUST["light"])
        for j in range(16):
            th = j * 0.6 + k * math.pi / 2
            rr = 0.8 + j * 0.3
            f.put(round(rr * math.cos(th) * 1.5) - 1, round(cy + rr * math.sin(th) * 0.75),
                  c["core"] if j < 5 else c["mid"] if j < 11 else c["edge"])
        for x0 in (17, 10):
            for j in range(3):
                y = cy + 6 + ((4 * k + 7 * j + x0) % 14)
                f.sym(x0 + (j % 2), y, DUST["mid"] if j == 0 else DUST["dark"])
        # the chevrons: a 'v' each side, sinking a step a frame
        for x0, ph in ((20, 0), (14, 10)):
            y0 = SY - 60 + ((ph + 5 * k) % 20)
            for i in range(3):
                f.sym(x0 - 2 + i, y0 + i, c["mid"])
                f.sym(x0 + 2 - i + 2, y0 + i, c["mid"])
            f.sym(x0 + 1, y0 + 3, c["edge"])
        out.append((f.crop(), 140))
    return out


MINI_GHOST = [".####.", "######", "#o##o#", "######", "######", "#.##.#"]


def ghost():
    """Cyan wisps circling her feet (three, a tail each) and two little ghosts rising behind her: under her (z -1)."""
    c = PAL["ghost"]
    out = []
    for k in range(4):
        f = F()
        f.ring(SY, 18, 6, c["out"], 1, keep=lambda x, y, k=k: (x + 2 * y + k) % 4 == 0)
        for j in range(3):
            th = 2 * math.pi * j / 3 + k * math.pi / 6
            for t, col, r in ((0, c["core"], 2), (0.32, c["mid"], 1.5), (0.62, c["edge"], 1)):
                x, y = 18 * math.cos(th - t), SY + 6 * math.sin(th - t)
                blob(f, x, y, r, r * 0.8, col)
        for x, ph in ((14, 0),):
            rise = (ph + 6 * k) % 24
            y0 = SY - 14 - rise
            for j, row in enumerate(MINI_GHOST):
                for i, ch in enumerate(row):
                    if ch != ".":
                        f.sym(x + i - 3, y0 + j, c["out"] if ch == "o" else c["core"] if j < 2 else c["mid"])
        out.append((f.crop(), 90))
    return out


# ------------------------------------------------------------------ the 1x sheet: the pictures that ride a unit

def plus1(f, x, y, core, arm, out=None):
    """A plus one square thick, arms one square long, on (x, y), mirrored; `out`: outlined."""
    if out is not None:
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            f.sym(x + dx, y + dy, out)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        f.sym(x + dx, y + dy, arm)
    f.sym(x, y, core)


def oval1(f, cy, rx, ry, col, keep=None):
    """A one-square ellipse outline about (0, cy), mirrored, for the small ground rings (F.ring's band grows thick when
    one half-axis is a few squares); `keep(x, y)` thins it."""
    for y in range(int(cy - ry - 2), int(cy + ry + 2)):
        for x in range(0, int(rx + 2)):
            px, py = x + 0.5, y + 0.5 - cy
            g = (px / rx) ** 2 + (py / ry) ** 2 - 1
            if abs(g) / (2 * math.hypot(px / rx ** 2, py / ry ** 2)) <= 0.55 and (keep is None or keep(x, y)):
                f.sym(x, y, col)


def rim_lit(f, cy, rx, ry, a0, span, col):
    """The pixels of an ellipse's one-square rim within `span` radians of the angle a0 (from the right, upward), mirrored."""
    for x in range(0, int(rx + 2)):
        for y in range(int(cy - ry - 2), int(cy + ry + 2)):
            v = math.hypot((x + 0.5) / rx, (y + 0.5 - cy) / ry)
            th = math.atan2(-(y + 0.5 - cy) * rx / ry, x + 0.5)
            if abs(v - 1) * min(rx, ry) <= 0.8 and abs(th - a0) <= span:
                f.sym(x, y, col)


def barrier_1x():
    """s_barrier: the dense shell at its size (half-axes 15 x 22 px, its middle 6 px over the pivot: from 5 px under her
    soles to over her hair), a one-pixel gold rim with a dark dotted lining, the shine sliding down a side, a sparse
    shimmer drifting up inside, a sparkle twinkling."""
    c = PAL["barrier"]
    cy, rx, ry = SY1 - 17, 15, 22
    out = []
    for k in range(4):
        f = F(1)
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(0, rx + 1):
                v = math.hypot((x + 0.5) / rx, (y + 0.5 - cy) / ry)
                if v < 0.84 and x % 3 == 1 and (y + k + 2 * (x // 3)) % 6 == 0:
                    f.sym(x, y, c["mid"] if v > 0.55 else c["core"])
        f.ring(cy, rx - 1.2, ry - 1.2, c["out"], 0.6, keep=lambda x, y: (x + y) % 2 == 0)
        f.ring(cy, rx, ry, c["edge"], 1)
        rim_lit(f, cy, rx, ry, math.pi * (0.30 + 0.08 * k), 0.26, c["core"])
        f.spark(int(rx * 0.55), int(cy - ry * 0.66), c["core"], c["mid"], 1 if k % 2 else 0)
        f.spark(int(rx * 0.86), int(cy + ry * 0.2), c["mid"], c["edge"], 0 if k % 2 else 1)
        out.append((f.crop(), 120))
    return out


def heal_1x():
    """s_heal: green crosses rising round the body in mirrored pairs (outlined while low, fading up), a dotted ring on
    the ground (loops while the buff lasts)."""
    c = PAL["heal"]
    out = []
    for k in range(4):
        f = F(1)
        oval1(f, SY1, 9, 2.5, c["edge"], keep=lambda x, y, k=k: (x + y + k) % 2 == 0)
        for x, ph in ((6, 0), (2, 8)):
            rise = (ph + 4 * k) % 16
            y = SY1 - 5 - rise
            if rise < 11:
                plus1(f, x, y, c["core"], c["mid"], c["out"])
            else:
                plus1(f, x, y, c["mid"], c["edge"])
        out.append((f.crop(), 120))
    return out


def ignite_1x():
    """s_ignite: three tongues of fire licking up his sides and shoulders (the dense ones' sizes), embers rising."""
    c = PAL["ignite"]
    out = []
    for k in range(4):
        f = F(1)
        ph = k * math.pi / 2
        flame(f, 6.5, SY1 - 7, 12 + 1.5 * math.sin(ph), 2.6, ph, c)
        flame(f, 3, SY1 - 14, 7 + math.cos(ph), 1.8, ph + 1.3, c)
        flame(f, 1, SY1 - 3, 6 + math.sin(ph + 2), 1.6, ph + 2.6, c)
        for j, (x, base) in enumerate(((4, SY1 - 23), (8, SY1 - 26), (2, SY1 - 29))):
            y = base - 2 * ((k + j) % 4)
            f.put(x + (k + j) % 2, y, c["mid"] if (k + j) % 4 < 2 else c["edge"])
            f.put(-1 - x - (k + j + 1) % 2, y - 2, c["edge"])
        out.append((f.crop(), 100))
    return out


def exhaust_1x():
    """s_exhaust: the grey dust cloud over his head (its middle 32 px over the pivot, over a 41-px champion's crown) with
    the drained amber spiral turning in it, dust drooping from its ends, amber chevrons sinking down his sides."""
    c = PAL["exhaust"]
    cy = SY1 - 43
    lumps = ((0, -0.5, 4), (4, 0, 3), (-4.5, 0, 3), (7.5, 1, 2), (-8, 1, 2), (2, 1.5, 2.5), (-2.5, 1.5, 2.5))
    out = []
    for k in range(4):
        f = F(1)
        for cx, dy, r in lumps:
            blob(f, cx, cy + dy, r + 0.8, r * 0.7 + 0.8, DUST["dark"])
        for cx, dy, r in lumps:
            blob(f, cx, cy + dy, r, r * 0.7, DUST["mid"])
        for cx, dy, r in ((-1, -1.5, 2.5), (3.5, -1, 1.5), (-5.5, -0.5, 1.5)):
            blob(f, cx, cy + dy, r, r * 0.55, DUST["light"])
        for j in range(8):
            th = j * 0.9 + k * math.pi / 2
            rr = 0.5 + j * 0.3
            f.put(round(rr * math.cos(th) * 1.5) - 1, round(cy + rr * math.sin(th) * 0.75),
                  c["core"] if j < 3 else c["mid"] if j < 6 else c["edge"])
        for x0 in (8, 5):
            y = cy + 3 + ((2 * k + 3 + x0) % 7)
            f.sym(x0, y, DUST["mid"])
            f.sym(x0, y + 2, DUST["dark"])
        for x0, ph in ((10, 0), (7, 5)):              # a 'v' each side, sinking a step a frame
            y0 = SY1 - 30 + ((ph + 3 * k) % 10)
            f.sym(x0 - 1, y0, c["mid"])
            f.sym(x0 + 1, y0, c["mid"])
            f.sym(x0, y0 + 1, c["edge"])
        out.append((f.crop(), 140))
    return out


MINI_GHOST_1X = ["###", "o#o", "###", "#.#"]


def ghost_1x():
    """s_ghost: cyan wisps circling her feet (three, a tail each), a dotted ring, a little ghost rising behind her on
    each side: under her (z -1)."""
    c = PAL["ghost"]
    out = []
    for k in range(4):
        f = F(1)
        oval1(f, SY1, 9, 3, c["out"], keep=lambda x, y, k=k: (x + y + k) % 2 == 0)
        for j in range(3):
            th = 2 * math.pi * j / 3 + k * math.pi / 6
            for t, col in ((0.62, c["edge"]), (0.32, c["mid"]), (0, c["core"])):
                f.put(round(9 * math.cos(th - t) - 0.5), round(SY1 + 3 * math.sin(th - t) - 0.5), col)
        rise = (6 * k) % 24 // 2
        y0 = SY1 - 7 - rise
        for j, row in enumerate(MINI_GHOST_1X):
            for i, ch in enumerate(row):
                if ch != ".":
                    f.sym(6 + i, y0 + j, c["out"] if ch == "o" else c["core"] if j < 2 else c["mid"])
        out.append((f.crop(), 90))
    return out


def cleanse_1x():
    """s_cleanse: a teal ring sweeping up her body (feet to crown), leaving sparkles that drift up and go out."""
    c = PAL["cleanse"]
    out = []
    left = [(7, SY1 - 3), (3, SY1 - 8), (6, SY1 - 14), (2, SY1 - 19)]
    for k, ms in enumerate([50, 60, 60, 70, 80, 90]):
        f = F(1)
        if k < 4:
            cy = SY1 - 6 * k
            oval1(f, cy, 8, 2.5, c["core"] if k else c["mid"], keep=lambda x, y, cy=cy: (y < cy) or (x + y) % 2 == 0)
            for j in range(k):
                x, y = left[j]
                f.spark(x, y, c["mid"], c["edge"], 1 if j == k - 1 else 0)
        elif k == 4:
            for j in range(4):
                x, y = left[j]
                f.put(x, y - 2, c["edge"])
                f.put(-1 - x, y - 2, c["edge"])
            for x, y in ((5, SY1 - 25), (1, SY1 - 28)):
                f.spark(x, y, c["core"], c["mid"], 1)
        else:
            for x, y in ((5, SY1 - 27), (1, SY1 - 30)):
                f.spark(x, y, c["mid"], c["edge"], 0)
        out.append((f.crop(), ms))
    return out


def icon(spell):
    """League's own icon (assets/source/zoe/summoner_icons, tools/lol/extract_summoner_icons.py) shrunk to 32 x 32
    squares, in a one-square frame: dark (`edge` given: that colour, lit)."""
    src = Image.open(lp(os.path.join(ICONS, spell + ".png"))).convert("RGB").resize((ICON, ICON), Image.LANCZOS)
    a = np.zeros((ICON + 2, ICON + 2, 4), np.uint8)
    a[..., :3] = OUTLINE
    a[..., 3] = 255
    a[1:-1, 1:-1, :3] = np.asarray(src)
    for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1)):
        a[y, x] = 0                                     # rounded corners
    return a


def decal(spell):
    """The icon lying on the ground: seen from the battlefield's slant it is twice as wide as tall, so every square
    becomes two side by side (68 x 34 squares, 23 x 11 game px); its frame glows in the spell's colour."""
    a = icon(spell)
    dark = (a[..., :3] == OUTLINE).all(-1) & (a[..., 3] > 0)
    a[dark] = (*PAL[spell]["edge"], 255)
    return np.repeat(a, 2, axis=1)


def ground(spell):
    """sg_<spell>: the icon lights up lying on the ground at her feet (its middle 4 px in front of her soles), a ring
    round it: its frame drawn first, then the whole icon with a glow, held while sparkles run round the ring, dithered
    away."""
    c = PAL[spell]
    dc = decal(spell)
    h, w = dc.shape[:2]
    cy = SYI + 4 * PPU_I
    top, left = cy - h // 2, -w // 2
    edge = np.zeros_like(dc)
    edge[[0, 1, 2, -3, -2, -1], :] = dc[[0, 1, 2, -3, -2, -1], :]
    edge[:, list(range(6)) + list(range(-6, 0))] = dc[:, list(range(6)) + list(range(-6, 0))]
    lit = np.where(edge[..., 3:] > 0, np.array([*c["core"], 255], np.uint8), 0).astype(np.uint8)
    rx, ry = w / 2 + 6, h / 2 + 4
    out = []
    for k, ms in enumerate([50, 70, 120, 120, 120, 120, 90, 90]):
        f = F(PPU_I)
        if k == 0:
            f.ring(cy, rx - 6, ry - 3, c["core"], 1)
            f.paste(lit, left, top)
        elif k == 1:
            f.ring(cy, rx, ry, c["mid"], 2)
            for x in range(left - 2, -left + 2):
                for y in (top - 2, top - 1, top + h, top + h + 1):
                    f.put(x, y, c["mid"])
            for y in range(top, top + h):
                for x in (left - 2, left - 1, -left, -left + 1):
                    f.put(x, y, c["mid"])
            f.paste(dc, left, top)
        elif k < 6:
            f.ring(cy, rx + 3, ry + 1.5, c["edge"], 1.5, keep=lambda x, y: (x + y) % 3 != 0)
            # four sparkles running round the ring (mirrored pairs)
            for j in range(2):
                th = math.pi * (0.15 + 0.35 * j) + (k - 2) * math.pi / 8
                sx, sy = (rx + 3) * math.cos(th), cy + (ry + 1.5) * math.sin(th)
                f.spark(int(sx), int(sy), c["core"], c["mid"], 2)
                f.spark(int(sx), int(2 * cy - sy), c["mid"], c["edge"], 1)
            f.paste(dc, left, top)
        else:
            f.ring(cy, rx + 5, ry + 2.5, c["out"], 1.5, keep=checker(2))
            f.paste(dc, left, top, keep=checker(k - 5))
        out.append((f.crop(), ms))
    return out


def badge(spell):
    """The icon as a small round badge (the user, 2026-11-03: 「缩成小块外面用圆圈包裹着不是更美观吗」): League's icon cut
    to a disc, in a ring of the spell's colour (lit on its upper half) and a dark rim - 38 squares, 12.7 game px."""
    ic = icon(spell)[1:-1, 1:-1]                    # the 32 x 32 picture without its square frame
    n, r = ICON + 6, ICON / 2
    a = np.zeros((n, n, 4), np.uint8)
    c = PAL[spell]
    for y in range(n):
        for x in range(n):
            d = math.hypot(x + 0.5 - n / 2, y + 0.5 - n / 2)
            if d <= r - 0.5:
                a[y, x, :3] = ic[y - 3, x - 3, :3]
                a[y, x, 3] = 255
            elif d <= r + 1.5:
                a[y, x] = (*(c["core"] if y < n / 2 - 2 else c["edge"]), 255)
            elif d <= r + 2.6:
                a[y, x] = (*OUTLINE, 255)
    return a


def shard(spell):
    """ss_<spell>: the spell's round badge over a shard lying on the ground (its crystal is ~12 px tall). Until 0.5.2 it
    was the square icon, and the game drew it three times its size (34 px, Zoe's height: 「还有地上的召唤师技能图标也太大
    了吧」) until league_main's DRAWN_EFFECTS listed this sheet."""
    f = F(PPU_I)
    b = badge(spell)
    f.paste(b, -b.shape[1] // 2, SYI - 13 * PPU_I - b.shape[0])
    return [(f.crop(), SHOW_MS + 20)]          # a little over the stamp's 15 ticks: no gap between two stamps


def sheet(t, ppu):
    """The tags with their 1x frames (the dense ones / PPU) and the dense ones as hd_<tag>."""
    out = {name: [(a[::ppu, ::ppu].copy(), ms) for a, ms in fr] for name, fr in t.items()}
    out.update({"hd_" + name: fr for name, fr in t.items()})
    return out


def fx_tags():
    """Flash's dense pictures {tag: [(dense frame, ms)]}, idle first (league_main's lookup reads its width to tell a dense
    sheet)."""
    fx = dict(s_flash=flash(), s_flash_trail=flash_trail())
    return {"idle": fx["s_flash"], **fx}


def fx1_tags():
    """The pictures that ride a unit, at a square a game px (a plain sheet: no idle, no hd_ twins). The dense designs
    (cleanse(), barrier(), heal(), ignite(), exhaust(), ghost()) are kept as the reference they were redrawn from."""
    return dict(s_cleanse=cleanse_1x(), s_barrier=barrier_1x(), s_heal=heal_1x(), s_ignite=ignite_1x(),
                s_exhaust=exhaust_1x(), s_ghost=ghost_1x())


def icon_tags():
    """The icons' dense pictures, idle first (they read assets/source/zoe/summoner_icons)."""
    icons = {"sg_" + s: ground(s) for s in SPELLS}
    icons.update({"ss_" + s: shard(s) for s in SPELLS})
    return {"idle": icons["ss_flash"], **icons}


# --sheets name -> (stem, tags, PPU: 1 = a plain sheet written as drawn)
SHEETS = {"spells": (OUT, fx_tags, PPU), "spells_1x": (OUT_1X, fx1_tags, 1), "icons": (OUT_ICONS, icon_tags, PPU_I)}


def review(t, path, z=4):
    """Every tag's frames at z screen px a game px; `t`: {tag: ([(frame, ms)], squares a game px)}."""
    from PIL import ImageDraw
    rows = []
    for name, (fr, ppu) in t.items():
        if name == "idle":
            continue
        h = max(a.shape[0] for a, _ in fr) * z // ppu
        w = sum(a.shape[1] * z // ppu + 6 for a, _ in fr)
        row = Image.new("RGB", (w + 120, h + 8), (92, 98, 86))
        d = ImageDraw.Draw(row)
        d.text((4, 4), name, fill=(255, 255, 255))
        d.text((4, 18), f"{len(fr)}f {sum(m for _, m in fr):.0f}ms PPU {ppu}", fill=(30, 30, 30))
        x = 120
        for a, _ in fr:
            im = Image.fromarray(a, "RGBA")
            im = im.resize((a.shape[1] * z // ppu, a.shape[0] * z // ppu), Image.NEAREST)
            row.paste(im, (x, 4 + (h - im.height) // 2), im)
            x += im.width + 6
        rows.append(row)
    W = max(r.width for r in rows)
    out = Image.new("RGB", (W, sum(r.height + 4 for r in rows)), (40, 40, 40))
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height + 4
    out.save(path)
    print(path, out.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", default=",".join(SHEETS), help="which sheets to write (the icons need assets/)")
    ap.add_argument("--review")
    a = ap.parse_args()
    made = {}
    for name in a.sheets.split(","):
        stem, make, ppu = SHEETS[name]
        t = make()
        w, h = G.write_sheet(lp(stem), sheet(t, ppu) if ppu > 1 else t, share=True)
        print(f"{os.path.relpath(stem, ROOT)}#sheet.png {w}x{h}: {len(t)} tags at PPU {ppu}")
        made.update({tag: (fr, ppu) for tag, fr in t.items()})
    if a.review:
        review(made, a.review)


if __name__ == "__main__":
    main()
