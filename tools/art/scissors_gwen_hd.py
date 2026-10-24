#!/usr/bin/env python3
"""Gwen's scissors at full size in Codex's action frames (the user, 2026-10-25: 「有的部分剪刀有点小 … 帮我把剪刀调大点吧」
「你可以参考之前那个格温 做的时候剪刀就挺长的 但是codex做出来剪刀就挺短的 所以要调整」).

Codex drew the pair over her shoulder at the design's size, but wherever the whole pair shows (thrust forward, snipping,
raised, dropped) it drew it 45-75 % as long: 48-85 squares from the handle's end to the tip, against the old 1x Gwen's
36-43 game px (102-122 squares at PPU 2.84). So in those frames (SPECS) the old pair is found and replaced by one
template - attack frame 4's pair (hd/scissors.png: its rings, pivot and blade, cut out once), its blade lengthened K
times (57 -> 85 squares: 108 squares, 38 game px, from the rings' end to the tip, as the old Gwen's thrust):
- the old pair: the scissors' colours (GOLD, BLADE, INK) within a capsule round its axis (ahead along the blade, back
  along the handle - or along handle_deg where Codex bent the handle off the blade's line), joined to the squares by its
  pivot, then the squares mostly ringed by them (its navy streaks share the dress's colours) (old_mask);
- its angle refined from the blade side's squares (refine), its handle's far end measured;
- the template drawn rotated by RotSprite (Scale2x three times, each square the 8x picture's square under its middle;
  the blade part stretched K times along the axis, the rings not), its handle's far end on the old one's so the pair
  grows away from her hand; opened about the pivot for Snip Snip!'s open frames; behind her where it lies by her
  (z "under"); its outline completed where the turn thinned it (outline);
- a pair that would reach under the ground (her soles' row) is turned up about its handle's end until it does not
  (fit_ground); a pair lying on the ground rests on that row ("rest"), lying still in the same place (at);
- her hand drawn back over the handle (her glove's and skin's squares round its end), specks dropped.

    python tools/art/scissors_gwen_hd.py --review DIR     # every swapped frame before | after, 3x
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
H = lambda s: [int(h, 16) for h in s.split()]  # noqa: E731
GOLD = H("5C4232 7C5739 976A3A BB8740 DFAA4F F7CA6A A98C67 8E746B")
BLADE = H("F1F1F3 C7CCE0 B4B4D9 9598C4 6D7199 71F1FA 17DAFC 14CBF7 3CBDEB 19A8EF 258EE3 0B6FC8 035BBB 217EC3 5A5F65 307999")
INK = H("060213 070723 2C395D 321820 483B45")
SC = GOLD + BLADE + INK
GLOVE = H("183282 0D1E5B 091441 1A3CB0 174C9D 304A85")
SKIN = H("FDD0B4 F8A79B F58B7F CAA6A1")
OUTLINE = (0x06, 0x02, 0x13)

TEMPLATE = os.path.join(ROOT, "assets", "source", "gwen", "hd", "scissors.png")   # attack frame 4's pair, cut out
PIV_T = (24.5, 17.5)            # the template's pivot (its gem), template squares
END_T = (1.5, 17.5)             # its handle's far end on the axis
K = 1.5                         # the blade (pivot -> tip) lengthened: 57 -> 85 squares
S = 8                           # the RotSprite scale
SPECK = 15
GROUND = 163                    # her soles' row on Codex's frames (every frame's lowest row)

# name: (the old pair's pivot (x, y) on the frame's squares, the blade's angle (degrees, counter-clockwise from +x;
# refined unless fix_angle), the blades' opening, options)
SPECS = {
    "attack_2": ((125.5, 130.5), -142, 0, {}),
    "attack_3": ((192, 126.5), -47, 0, {}),
    "attack_4": ((183, 109.5), 0, 0, {}),
    "attack_6": ((182, 129), -42, 0, {}),
    "skill_1": ((193.8, 115.6), -50, 0, {}),
    "skill_2": ((191.9, 103.8), 2, 37, {}),
    "skill_3": ((187, 107.5), 0, 0, {}),
    "skill_9": ((192.9, 101.4), 6, 37, {}),
    "skill_12": ((182.5, 102.5), 0, 0, {}),
    "skill_13": ((168.9, 118.9), -46, 0, dict(handle_deg=175)),
    "skill2_6": ((160, 56), 49, 0, {}),
    "skill2_7": ((181, 50), 63, 0, {}),
    "dead_1": ((183.3, 110), -28, 0, {}),
    "dead_2": ((186.7, 125), -35, 0, {}),
    "dead_3": ((195.8, 145), -18, 0, dict(z="under")),
    # lying still on the ground beside her: flat, resting on the ground's row, frames 6-7 where frame 5 has it
    "dead_4": ((188.3, 151.7), 0, 0, dict(z="under", fix_angle=True, ground="rest")),
    "dead_5": ((156, 153), 0, 0, dict(z="under", fix_angle=True, ground="rest")),
    "dead_6": ((157, 151), 0, 0, dict(z="under", fix_angle=True, ground="rest", at_from="dead_5")),
    "dead_7": ((158, 152), 0, 0, dict(z="under", fix_angle=True, ground="rest", at_from="dead_5")),
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def rgb24(a):
    return (a[..., 0].astype(np.int32) << 16) | (a[..., 1].astype(np.int32) << 8) | a[..., 2]


def scale2x(a):
    h, w = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    E, B, D, F, Hh = p[1:-1, 1:-1], p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 2:], p[2:, 1:-1]
    eq = lambda u, v: (u == v).all(-1)  # noqa: E731
    out = np.zeros((h * 2, w * 2, a.shape[2]), a.dtype)
    out[0::2, 0::2] = np.where((eq(D, B) & ~eq(D, Hh) & ~eq(B, F))[..., None], D, E)
    out[0::2, 1::2] = np.where((eq(B, F) & ~eq(B, D) & ~eq(F, Hh))[..., None], F, E)
    out[1::2, 0::2] = np.where((eq(D, Hh) & ~eq(D, B) & ~eq(Hh, F))[..., None], D, E)
    out[1::2, 1::2] = np.where((eq(Hh, F) & ~eq(D, Hh) & ~eq(B, F))[..., None], F, E)
    return out


_BIG = None


def big():
    global _BIG
    if _BIG is None:
        b = np.asarray(Image.open(lp(TEMPLATE)).convert("RGBA"))
        for _ in range(3):
            b = scale2x(b)
        _BIG = b
    return _BIG


def outline(a):
    """One dark square outside every light edge square (the turn thins the template's own outline)."""
    op = a[..., 3] > 0
    dark = op & np.isin(rgb24(a), INK)
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    ring = ndimage.binary_dilation(op & ~dark, structure=cross) & ~op
    out = a.copy()
    out[ring] = (*OUTLINE, 255)
    return out


def render(anchor, deg, open_deg=0.0, shape=None):
    """The template with its handle's far end on `anchor` (x, y), its axis at `deg`; the blades (lengthened K times)
    opened by open_deg about the pivot. -> RGBA array of `shape`."""
    h, w = shape
    B = big()
    yy, xx = np.mgrid[0:h, 0:w]
    piv = PIV_T[0] - END_T[0]
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    pvx, pvy = anchor[0] + piv * c, anchor[1] - piv * s
    out = np.zeros((h, w, 4), np.uint8)

    def sample(a_deg, part):
        ca, sa = math.cos(math.radians(a_deg)), math.sin(math.radians(a_deg))
        px, py = xx + 0.5 - pvx, yy + 0.5 - pvy
        u = px * ca - py * sa + piv                      # along the axis from the far end (screen y down: +deg is up)
        v = px * sa + py * ca
        if part == "blade":
            sel = u > piv
            u = np.where(sel, piv + (u - piv) / K, u)
        else:
            sel = u <= piv + 0.5
        tx, ty = END_T[0] + u, END_T[1] + v
        bx, by = np.floor(tx * S).astype(int), np.floor(ty * S).astype(int)
        ok = sel & (bx >= 0) & (bx < B.shape[1]) & (by >= 0) & (by < B.shape[0])
        got = np.zeros((h, w, 4), np.uint8)
        got[ok] = B[by[ok], bx[ok]]
        return got

    parts = [("handle", deg)] + ([("blade", deg)] if not open_deg else
                                 [("blade", deg + open_deg / 2), ("blade", deg - open_deg / 2)])
    for part, a in parts:
        g = sample(a, part)
        m = g[..., 3] > 0
        out[m] = g[m]
    return outline(out)


def old_mask(d, piv, deg, back=28, ahead=75, r_blade=10, r_handle=16, open_deg=0.0, handle_deg=None):
    """The old pair (see the module's notes) -> (its squares, the capsule)."""
    h, w = d.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    rx, ry = xx + 0.5 - piv[0], yy + 0.5 - piv[1]
    cap = np.zeros((h, w), bool)
    for a in ([deg] if not open_deg else [deg + open_deg / 2, deg - open_deg / 2]):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        u, v = rx * c - ry * s, rx * s + ry * c
        cap |= (u >= 0) & (u <= ahead) & (np.abs(v) <= r_blade)
    hd = deg + 180 if handle_deg is None else handle_deg
    c, s = math.cos(math.radians(hd)), math.sin(math.radians(hd))
    u, v = rx * c - ry * s, rx * s + ry * c
    cap |= (u > 0) & (u <= back) & (np.abs(v) <= r_handle)
    cap |= (rx ** 2 + ry ** 2) <= 8 ** 2
    op = d[..., 3] > 0
    sc = cap & op & np.isin(rgb24(d), SC)
    lbl, n = ndimage.label(sc, structure=np.ones((3, 3)))
    near = (rx ** 2 + ry ** 2) <= 6 ** 2
    m = np.isin(lbl, list(set(np.unique(lbl[near & sc])) - {0}))
    for _ in range(4):
        cnt = ndimage.convolve(m.astype(int), np.ones((3, 3), int), mode="constant") - m
        add = cap & op & ~m & (cnt >= 5)
        if not add.any():
            break
        m |= add
    return m, cap


def refine(m, piv, deg):
    """The old pair's blade angle (the blade side's principal direction), its tip and its handle's far end."""
    ys, xs = np.nonzero(m)
    rx, ry = xs + 0.5 - piv[0], ys + 0.5 - piv[1]
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    u = rx * c - ry * s
    blade = u > 4
    a = math.degrees(math.atan2(-(ry[blade] * u[blade]).sum(), (rx[blade] * u[blade]).sum())) if blade.sum() > 10 else deg
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    u = rx * c - ry * s
    return a, (piv[0] + u.max() * c, piv[1] - u.max() * s), (piv[0] + u.min() * c, piv[1] - u.min() * s), u.max() - u.min()


def fit_ground(end, a, open_deg, shape, ground):
    """The angle nearest `a` at which the pair, its far end on `end`, keeps above the ground's row: turned toward the
    level (0 or 180 degrees) a degree at a time."""
    level = 0.0 if math.cos(math.radians(a)) >= 0 else 180.0
    step = 1.0 if (level - a) % 360 < 180 else -1.0
    for k in range(60):
        b = a + step * k
        new = render(end, b, open_deg, shape)
        if np.nonzero((new[..., 3] > 0).any(1))[0].max() <= ground:
            return b
        if abs(((b - level + 180) % 360) - 180) < 0.5:
            break
    return level


def replace(d, piv, deg, open_deg=0.0, hand_r=6, z="top", fix_angle=False, ground=None, at=None, pad=110, **kw):
    """d with its pair replaced: -> (frame grown by `pad` on every side, the new pair's squares there, info)."""
    m, cap = old_mask(d, piv, deg, open_deg=open_deg, **kw)
    a, tip, end, old_len = refine(m, piv, deg)
    if open_deg or fix_angle:
        a = deg
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        ys, xs = np.nonzero(m)
        u = (xs + 0.5 - piv[0]) * c - (ys + 0.5 - piv[1]) * s_
        end = (piv[0] + u.min() * c, piv[1] - u.min() * s_)
    if at is not None:
        end = at
    big_ = np.zeros((d.shape[0] + 2 * pad, d.shape[1] + 2 * pad, 4), np.uint8)
    big_[pad:-pad, pad:-pad] = d
    mm = np.zeros(big_.shape[:2], bool)
    mm[pad:-pad, pad:-pad] = m
    out = big_.copy()
    out[mm] = 0
    e = (end[0] + pad, end[1] + pad)
    g = GROUND + pad
    if ground != "rest":
        a = fit_ground(e, a, open_deg, big_.shape[:2], g)
    new = render(e, a, open_deg, big_.shape[:2])
    nm = new[..., 3] > 0
    if ground == "rest":
        dy = g - np.nonzero(nm.any(1))[0].max()
        new = np.roll(new, dy, axis=0)
        if dy > 0:
            new[:dy] = 0
        elif dy < 0:
            new[dy:] = 0
        nm = new[..., 3] > 0
    yy, xx = np.mgrid[0:big_.shape[0], 0:big_.shape[1]]
    handz = ((xx + 0.5 - e[0]) ** 2 + (yy + 0.5 - e[1]) ** 2) <= hand_r ** 2
    hand = handz & (big_[..., 3] > 0) & ~mm & np.isin(rgb24(big_), GLOVE + SKIN)
    put = nm & (out[..., 3] == 0) if z == "under" else nm
    out[put] = new[put]
    if z != "under":
        out[hand] = big_[hand]
    out = drop_specks(out, SPECK)
    return out, put & (out[..., 3] > 0), dict(angle=round(a, 1), end=end, old_len=round(old_len, 1), old=m)


def drop_specks(a, most):
    """Pieces of up to `most` squares apart from the figure (what is left of the old pair's outline): gone."""
    op = a[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n < 2:
        return a
    sz = ndimage.sum(op, lbl, range(1, n + 1))
    out = a.copy()
    for k in range(1, n + 1):
        if sz[k - 1] <= most:
            out[lbl == k] = 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True)
    a = ap.parse_args()
    import casts_gwen_hd as CG
    os.makedirs(a.review, exist_ok=True)
    raw = CG.read_all()
    for n in SPECS:
        d = raw[n]
        opts = dict(SPECS[n][3])
        opts.pop("at_from", None)
        out, nm, info = replace(d, *SPECS[n][:3], **opts)
        before = np.zeros_like(out)
        before[110:-110, 110:-110] = d
        ys, xs = np.nonzero((out[..., 3] > 0) | (before[..., 3] > 0))
        box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
        row = []
        for img in (before, out):
            im = Image.fromarray(img).crop(box)
            bg = Image.new("RGBA", im.size, (190, 200, 190, 255))
            bg.alpha_composite(im)
            row.append(bg.resize((im.width * 3, im.height * 3), Image.NEAREST))
        t = Image.new("RGB", (sum(r.width + 6 for r in row), row[0].height), (40, 40, 40))
        x = 0
        for r in row:
            t.paste(r.convert("RGB"), (x, 0))
            x += r.width + 6
        t.save(os.path.join(a.review, f"scissors_{n}.png"))
        print(n, "angle", info["angle"], "old length", info["old_len"])


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()
