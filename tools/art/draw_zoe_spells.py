#!/usr/bin/env python3
"""Zoe's stolen summoner spells, drawn square by square (the user, 2026-10-22: 「给我展现一个比如佐伊w现在召唤师技能的
gif图？」 -> only Exhaust showed anything; 「加啊」「地面上最好也要有图标显示」, picked「放的时候地上亮图标」).

    python tools/art/draw_zoe_spells.py [--review out.png]

Writes league/effects/league_zoe_spells (#sheet.png + #anim.fanim), a dense effect sheet at PPU 2 (league_main hd.rs
EFFECTS: every tag has its hd_ twin, the 1x frames are the dense ones halved). The add-on league_zoe plays them
(addons/league_zoe/src/lib.rs summon / shards; the views from tools/kit/build_zoe.py --native):

  * sg_<spell>  the spell's icon lighting up on the ground in front of her feet as she casts it (a ring round her feet,
                the icon popping in white, held, dithered away; ~0.8 s, z -1, where she stood);
  * ss_<spell>  the same icon over a spell shard lying on the ground (one picture for one stamp, 15 ticks): the shard
                cycles through the seven - which one it gives is picked when she picks it up;
  * s_flash     a starburst on her and on the one Flash knocks away;     s_cleanse  a ring sweeping up her body;
  * s_barrier   a golden bubble round her;                               s_heal     green crosses rising (a buff's view);
  * s_ignite    flames on the burning one (a buff's view);               s_exhaust  a dusty cloud over his head;
  * s_ghost     cyan wisps round her feet (a buff's view, under her).

Every picture is symmetric left to right (the client never mirrors an effect) except the icons' own symbols. Squares
are counted from the pivot (the unit's / the point's position): the soles are 11 game px = 22 squares under it.
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
OUT_ICONS = os.path.join(ROOT, "league", "effects", "league_zoe_spell_icons")
ICONS = os.path.join(ROOT, "assets", "source", "zoe", "summoner_icons")
PPU = 2                                         # the spells' own pictures
SY = 11 * PPU                                   # the soles under the pivot
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
    c = PAL["flash"]
    cy = SY - 24
    out = []
    for k, ms in enumerate([40, 50, 60, 70]):
        f = F()
        if k == 0:
            astroid(f, cy, 10, c)
        elif k == 1:
            f.ring(cy, 12, 12, c["mid"], 1)
            astroid(f, cy, 17, c)
        elif k == 2:
            f.ring(cy, 18, 18, c["edge"], 1, keep=lambda x, y: (x + y) % 2 == 0)
            astroid(f, cy, 9, c)
            for d in (10, 14):
                f.spark(d, cy - d, c["core"], c["mid"], 1)
                f.spark(d, cy + d, c["mid"], c["edge"], 1)
        else:
            f.ring(cy, 22, 22, c["out"], 1, keep=checker(2))
            f.spark(15, cy - 15, c["mid"], c["edge"], 1)
            f.spark(15, cy + 15, c["edge"], c["out"], 0)
            f.spark(0, cy, c["core"], c["mid"], 2)
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
    cy, rx, ry = SY - 26, 44, 52                    # 13 px up; 22 x 26 px: soles - 7 px .. 39 px over them, her mane in it
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


def shard(spell):
    """ss_<spell>: the icon over a shard lying on the ground (its crystal is ~12 px tall)."""
    f = F(PPU_I)
    ic = icon(spell)
    f.paste(ic, -ic.shape[1] // 2, SYI - 13 * PPU_I - ic.shape[0])
    return [(f.crop(), SHOW_MS + 20)]          # a little over the stamp's 15 ticks: no gap between two stamps


def sheet(t, ppu):
    """The tags with their 1x frames (the dense ones / PPU) and the dense ones as hd_<tag>."""
    out = {name: [(a[::ppu, ::ppu].copy(), ms) for a, ms in fr] for name, fr in t.items()}
    out.update({"hd_" + name: fr for name, fr in t.items()})
    return out


def tags():
    """(the spells' own pictures, the icons): {tag: [(dense frame, ms)]} each, idle first (league_main's lookup reads
    its width to tell a dense sheet)."""
    fx = dict(s_flash=flash(), s_cleanse=cleanse(), s_barrier=barrier(), s_heal=heal(), s_ignite=ignite(),
              s_exhaust=exhaust(), s_ghost=ghost())
    icons = {"sg_" + s: ground(s) for s in SPELLS}
    icons.update({"ss_" + s: shard(s) for s in SPELLS})
    return {"idle": fx["s_flash"], **fx}, {"idle": icons["ss_flash"], **icons}


def review(t, path, z=4):
    from PIL import ImageDraw
    rows = []
    for name, fr in t.items():
        if name == "idle":
            continue
        h = max(a.shape[0] for a, _ in fr)
        w = sum(a.shape[1] + 6 for a, _ in fr) + 110
        row = Image.new("RGB", (w * z // 2 + 120, h * z // 2 + 8), (92, 98, 86))
        d = ImageDraw.Draw(row)
        d.text((4, 4), name, fill=(255, 255, 255))
        d.text((4, 18), f"{len(fr)}f {sum(m for _, m in fr):.0f}ms", fill=(30, 30, 30))
        x = 120
        for a, _ in fr:
            im = Image.fromarray(a, "RGBA")
            im = im.resize((a.shape[1] * z // 2, a.shape[0] * z // 2), Image.NEAREST)
            row.paste(im, (x, 4 + (h - a.shape[0]) * z // 4), im)
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
    ap.add_argument("--review")
    a = ap.parse_args()
    fx, icons = tags()
    for stem, t, ppu in ((OUT, fx, PPU), (OUT_ICONS, icons, PPU_I)):
        w, h = G.write_sheet(lp(stem), sheet(t, ppu), share=True)
        print(f"{os.path.relpath(stem, ROOT)}#sheet.png {w}x{h}: {len(t)} tags at PPU {ppu}")
    if a.review:
        review({**fx, **icons}, a.review)


if __name__ == "__main__":
    main()
