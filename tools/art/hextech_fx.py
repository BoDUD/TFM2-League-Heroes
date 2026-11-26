"""海克斯大乱斗（league_hextech 0.3.0）的战场特效：一格一格画的像素图（1 格 = 1 个游戏像素），照 dragons_soul_fx.py 的做法
（每段动画一行、透明度只有 0 和 255、编进 DLL 的横条备份）。只用 numpy 和 Pillow。

每种效果先算一张「热度」图（几团高斯、圆环、线段加起来），再按热度切成 4 档颜色、外面描一圈深色的边：同一套笔法画 29 段动画。

写出：
  addons/league_hextech/effects/league_hextech_fx#sheet.png   贴图
  addons/league_hextech/src/fx_atlas.rs                         每段动画在图上的位置
  addons/league_hextech/src/fx_runs.bin                         同一份图拆成同色横条（画不了贴图时一条条画）

  python tools/art/hextech_fx.py [--preview out.png] [--check]
--check 只比对，不写（CI 里看图和表是不是这个脚本画出来的那份）。
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MOD = os.path.join(ROOT, "addons", "league_hextech")
SHEET = os.path.join(MOD, "effects", "league_hextech_fx#sheet.png")
ATLAS = os.path.join(MOD, "src", "fx_atlas.rs")
RUNS = os.path.join(MOD, "src", "fx_runs.bin")
SHEET_W = 1024


def rgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


# 描边、深、中、亮、高光
PAL = {
    "fire": ["3a0d0a", "a3241a", "e8561c", "ffa23a", "ffe9a0"],
    "frost": ["0e1f3d", "2a5fa8", "5fb4f0", "b8ecff", "ffffff"],
    "gold": ["4a2a00", "c07a10", "f5c542", "fff0a0", "ffffff"],
    "arcane": ["1e0b33", "5a1f9a", "9a4ae0", "d39bff", "fff0ff"],
    "hex": ["0b1a3a", "1f5fd0", "4fb0ff", "b0ecff", "ffffff"],
    "grow": ["0f2a12", "2e7a2a", "6cc040", "c8f06a", "fffbd0"],
    "stone": ["2a1a0a", "7a4a1a", "c08a3a", "ecc878", "fff2c8"],
    "blood": ["2a0508", "8a1018", "e02a2a", "ff8a7a", "fff0e8"],
    "holy": ["3a2a08", "b08a20", "f0d050", "fff4b0", "ffffff"],
    "orange": ["3a1a05", "b0501a", "f08a2a", "ffc860", "fff6d0"],
    "cyan": ["06283a", "147a9a", "2ad0e0", "9af6ff", "ffffff"],
    "snow": ["2a3a5a", "7a9ac8", "c8dcf0", "eef6ff", "ffffff"],
    "shade": ["140a24", "4a1a6a", "8a3ac0", "c890ff", "f4e0ff"],
    "wind": ["1a3a3a", "3a8a80", "7ad0c0", "c8fff0", "ffffff"],
    "comet": ["0b1033", "3a3ab0", "6a8af0", "c0d8ff", "ffffff"],
}
PAL = {k: [rgb(c) for c in v] for k, v in PAL.items()}


def field(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return xx + 0.5, yy + 0.5


def blob(X, Y, cx, cy, rx, ry, a=1.0):
    return a * np.exp(-(((X - cx) / max(rx, 0.3)) ** 2 + ((Y - cy) / max(ry, 0.3)) ** 2))


def ring(X, Y, cx, cy, r, width, squash=1.0, a=1.0, arc=None):
    """一圈（`squash` < 1 是躺在地上的椭圆）；`arc`=(从, 到) 弧度时只画那一段。"""
    dx, dy = X - cx, (Y - cy) / squash
    d = np.sqrt(dx * dx + dy * dy)
    out = a * np.exp(-((d - r) / max(width, 0.3)) ** 2)
    if arc is not None:
        ang = np.arctan2(dy, dx)
        lo, hi = arc
        span = (ang - lo) % (2 * math.pi)
        out = np.where(span <= (hi - lo) % (2 * math.pi) + 1e-6, out, 0.0)
    return out


def seg(X, Y, p0, p1, width, a=1.0, taper=False):
    """一条线段；`taper` 时两头细。"""
    (x0, y0), (x1, y1) = p0, p1
    vx, vy = x1 - x0, y1 - y0
    ll = vx * vx + vy * vy
    t = np.clip(((X - x0) * vx + (Y - y0) * vy) / max(ll, 1e-6), 0.0, 1.0)
    px, py = x0 + t * vx, y0 + t * vy
    d = np.sqrt((X - px) ** 2 + (Y - py) ** 2)
    wd = width * (np.sin(t * math.pi) * 0.85 + 0.15) if taper else width
    return a * np.exp(-(d / np.maximum(wd, 0.3)) ** 2)


def star(X, Y, cx, cy, n, r, width, rot=0.0, a=1.0, r0=0.0):
    out = np.zeros_like(X)
    for k in range(n):
        ang = rot + k * 2 * math.pi / n
        p0 = (cx + math.cos(ang) * r0, cy + math.sin(ang) * r0)
        p1 = (cx + math.cos(ang) * r, cy + math.sin(ang) * r)
        out = np.maximum(out, seg(X, Y, p0, p1, width, a, taper=True))
    return out


def noise(w, h, cell, seed):
    """块状的值噪声（0..1），格子 `cell` 像素。"""
    rng = np.random.default_rng(seed)
    gw, gh = w // cell + 2, h // cell + 2
    g = rng.random((gh, gw)).astype(np.float32)
    X, Y = field(w, h)
    fx, fy = X / cell, Y / cell
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - x0, fy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b = g[y0, x0], g[y0, x0 + 1]
    c, d = g[y0 + 1, x0], g[y0 + 1, x0 + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def paint(heat, pal, cuts=(0.22, 0.42, 0.64, 0.86), outline=True, keep=None):
    """热度 -> 一帧：低于 cuts[0] 透明，往上深、中、亮、高光，外面一圈描边（4 邻接）。`keep`：另外要涂成不透明的地方。"""
    h, w = heat.shape
    f = np.zeros((h, w, 4), np.uint8)
    m = heat > cuts[0]
    if keep is not None:
        m |= keep
    # 孤零零的一格去掉（像素画里是噪点）
    n = np.zeros_like(m, dtype=np.int32)
    n[1:, :] += m[:-1, :]
    n[:-1, :] += m[1:, :]
    n[:, 1:] += m[:, :-1]
    n[:, :-1] += m[:, 1:]
    m &= n > 0
    tone = np.digitize(heat, cuts[1:])  # 0..3
    for k in range(4):
        sel = m & (tone == k)
        f[sel, :3] = pal[k + 1]
        f[sel, 3] = 255
    if outline:
        e = np.zeros_like(m)
        e[1:, :] |= m[:-1, :]
        e[:-1, :] |= m[1:, :]
        e[:, 1:] |= m[:, :-1]
        e[:, :-1] |= m[:, 1:]
        e &= ~m
        f[e, :3] = pal[0]
        f[e, 3] = 255
    return f


def over(top, bottom):
    out = bottom.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def ease(t):
    return 1 - (1 - t) ** 2


def anim(w, h, ax, ay, ticks, n, draw):
    frames = [draw(k, k / max(n - 1, 1)) for k in range(n)]
    for k, f in enumerate(frames):
        assert f.shape == (h, w, 4), (k, f.shape)
        if not f[..., 3].any():  # 最后一帧淡没了：留一点余光
            frames[k] = frames[k - 1].copy() if k else f
    return w, h, (ax, ay), ticks, frames


# ===================== 每一种 =====================

def burn():
    w, h = 20, 26
    X, Y = field(w, h)

    def d(k, t):
        nz = noise(w, h, 3, 11 + k)
        heat = (blob(X, Y, 10, 21 - 2 * t, 5.5 * (1 - 0.35 * t), 5.5)
                + blob(X, Y, 10 + math.sin(k * 1.7) * 1.5, 13 - 5 * t, 3.0, 5.0, 0.85 * (1 - 0.5 * t))
                + blob(X, Y, 6.5 + (k % 2), 8 - 3 * t, 1.5, 2.3, 0.7 * (1 - t))
                + blob(X, Y, 13.5 - (k % 2), 6 - 3 * t, 1.3, 2.0, 0.6 * (1 - t)))
        heat *= (0.55 + 0.45 * Y / h) * (0.75 + 0.5 * nz) * (1 - 0.45 * t)
        return paint(heat, PAL["fire"], (0.28, 0.45, 0.66, 0.86))
    return anim(w, h, 10, 24, 4, 6, d)


def frost():
    w, h = 34, 34
    X, Y = field(w, h)
    c = (17, 18)

    def d(k, t):
        grow = ease(min(1.0, t * 2.2))
        heat = blob(X, Y, *c, 4.5 * (1 - 0.6 * t), 4.5 * (1 - 0.6 * t), 0.9)
        for i in range(6):
            ang = math.radians(30 + i * 60)
            if t < 0.55:
                ln = 5 + 9 * grow
                p1 = (c[0] + math.cos(ang) * ln, c[1] + math.sin(ang) * ln * 0.9)
                heat = np.maximum(heat, seg(X, Y, c, p1, 1.9, 1.0, taper=True))
            else:
                # 碎成冰碴往外飘、往下落
                s = (t - 0.55) / 0.45
                for j in (0.55, 0.9):
                    ln = (5 + 9) * j + 4 * s
                    px = c[0] + math.cos(ang) * ln
                    py = c[1] + math.sin(ang) * ln * 0.9 + 5 * s * s
                    heat = np.maximum(heat, blob(X, Y, px, py, 1.3, 1.3, 0.95 * (1 - 0.6 * s)))
        return paint(heat, PAL["frost"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 17, 30, 4, 6, d)


def light_pop():
    w, h = 32, 32
    X, Y = field(w, h)

    def d(k, t):
        r = 5 + 11 * ease(t)
        a = 1.0 - 0.75 * t
        heat = star(X, Y, 16, 14, 8, r, 1.4 * (1 - 0.4 * t), rot=0.2 + 0.25 * k, a=a, r0=2 + 3 * t)
        heat = np.maximum(heat, blob(X, Y, 16, 14, 4.5 * (1 - 0.7 * t), 4.5 * (1 - 0.7 * t), 1.0 - 0.5 * t))
        return paint(heat, PAL["gold"], (0.3, 0.48, 0.68, 0.88))
    return anim(w, h, 16, 26, 3, 5, d)


def escape():
    w, h = 40, 48
    X, Y = field(w, h)

    def d(k, t):
        r = 6 + 9 * ease(min(1.0, t * 3))
        thin = 1.6 if t < 0.8 else 1.6 * (1 - (t - 0.8) * 2.5)
        heat = ring(X, Y, 20, 26, r, max(thin, 0.6), squash=1.2, a=1.0)
        # 一道高光在泡泡上转
        ang = -2.2 + t * 3.0
        heat = np.maximum(heat, ring(X, Y, 20, 26, r - 2, 1.0, 1.2, 1.0, arc=(ang, ang + 0.9)))
        if t > 0.2:
            s = (t - 0.2) / 0.8
            for i, yy in enumerate((20, 28, 36)):
                x0 = 8 - 6 * s - i * 2
                heat = np.maximum(heat, seg(X, Y, (x0, yy), (x0 - 6, yy), 0.8, 0.9 * (1 - 0.5 * s)))
                x1 = 32 + 6 * s + i * 2
                heat = np.maximum(heat, seg(X, Y, (x1, yy + 2), (x1 + 6, yy + 2), 0.8, 0.9 * (1 - 0.5 * s)))
        return paint(heat, PAL["hex"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 20, 44, 4, 8, d)


def grow():
    w, h = 44, 52
    X, Y = field(w, h)

    def d(k, t):
        heat = ring(X, Y, 22, 46, 6 + 14 * ease(t), 1.6 * (1 - 0.5 * t), squash=0.38, a=1.0 - 0.5 * t)
        for i in range(3):
            s = (t * 1.3 - i * 0.18)
            if 0 <= s <= 1:
                y = 44 - 38 * s
                for side in (-1, 1):
                    heat = np.maximum(heat, seg(X, Y, (22, y), (22 + side * 6, y + 5), 1.1, 1.0 - 0.6 * s))
        if t > 0.3:
            for i in range(5):
                sx = 8 + i * 7 + (k % 2)
                sy = 44 - 30 * ((t - 0.3) / 0.7) - (i % 2) * 6
                heat = np.maximum(heat, blob(X, Y, sx, sy, 0.9, 0.9, 0.9))
        return paint(heat, PAL["grow"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 22, 48, 4, 8, d)


def punch():
    w, h = 24, 24
    X, Y = field(w, h)

    def d(k, t):
        heat = blob(X, Y, 12, 12, 3.8 * (1 - 0.6 * t), 3.8 * (1 - 0.6 * t), 1.0)
        heat = np.maximum(heat, star(X, Y, 12, 12, 4, 4 + 6 * ease(t), 1.0, rot=0.785, a=1 - 0.7 * t, r0=2))
        heat = np.maximum(heat, ring(X, Y, 12, 12, 3 + 6 * t, 0.9, a=0.9 * (1 - t)))
        return paint(heat, PAL["hex"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 12, 20, 3, 5, d)


def heavy():
    w, h = 34, 30
    X, Y = field(w, h)
    rng = np.random.default_rng(5)
    bits = [(rng.uniform(0, 2 * math.pi), rng.uniform(8, 13)) for _ in range(6)]

    def d(k, t):
        heat = blob(X, Y, 17, 16, 6 * (1 - 0.6 * t), 5 * (1 - 0.6 * t), 1.0)
        heat = np.maximum(heat, ring(X, Y, 17, 16, 4 + 10 * ease(t), 1.2, 0.8, 1 - 0.8 * t))
        for ang, sp in bits:
            px = 17 + math.cos(ang) * sp * ease(t)
            py = 16 + math.sin(ang) * sp * 0.8 * ease(t) + 4 * t * t
            heat = np.maximum(heat, blob(X, Y, px, py, 1.2, 1.2, 0.95 * (1 - 0.5 * t)))
        return paint(heat, PAL["orange"], (0.3, 0.5, 0.7, 0.88))
    return anim(w, h, 17, 25, 3, 5, d)


def missile():
    w, h = 16, 16
    X, Y = field(w, h)

    def d(k, t):
        heat = blob(X, Y, 8, 8, 3.6, 3.6, 1.0)
        ang = k * math.pi / 2
        for j in range(3):
            a2 = ang + j * 2 * math.pi / 3
            heat = np.maximum(heat, blob(X, Y, 8 + math.cos(a2) * 5, 8 + math.sin(a2) * 5, 1.0, 1.0, 0.8))
        return paint(heat, PAL["arcane"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 8, 8, 3, 4, d)


def missile_pop():
    w, h = 28, 28
    X, Y = field(w, h)

    def d(k, t):
        heat = ring(X, Y, 14, 14, 3 + 9 * ease(t), 1.3, a=1 - 0.6 * t)
        heat = np.maximum(heat, blob(X, Y, 14, 14, 4 * (1 - t), 4 * (1 - t), 1.0))
        heat = np.maximum(heat, star(X, Y, 14, 14, 5, 5 + 8 * t, 0.9, rot=0.5, a=0.9 * (1 - t), r0=3))
        return paint(heat, PAL["arcane"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 14, 22, 3, 5, d)


def zig(rng, p0, p1, segs, amp):
    pts = [p0]
    for i in range(1, segs):
        f = i / segs
        x = p0[0] + (p1[0] - p0[0]) * f + rng.uniform(-amp, amp)
        y = p0[1] + (p1[1] - p0[1]) * f + rng.uniform(-amp, amp)
        pts.append((x, y))
    pts.append(p1)
    return pts


def spark():
    w, h = 30, 30
    X, Y = field(w, h)

    def d(k, t):
        rng = np.random.default_rng(40 + k)
        heat = blob(X, Y, 15, 15, 3.5 * (1 - 0.6 * t), 3.5 * (1 - 0.6 * t), 1.0)
        for i in range(5):
            ang = i * 2 * math.pi / 5 + k * 0.6
            ln = 6 + 6 * (1 - t)
            p1 = (15 + math.cos(ang) * ln, 15 + math.sin(ang) * ln)
            pts = zig(rng, (15, 15), p1, 3, 1.5)
            for a, b in zip(pts, pts[1:]):
                heat = np.maximum(heat, seg(X, Y, a, b, 0.75, 1.0 - 0.6 * t))
        return paint(heat, PAL["hex"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 15, 23, 3, 5, d)


def crack():
    w, h = 24, 50
    X, Y = field(w, h)
    cy = 10

    def d(k, t):
        s = ease(min(1.0, t * 3))
        r = 3 + 5 * s
        heat = ring(X, Y, 12, cy, r, 1.1, a=1.0)
        heat = np.maximum(heat, blob(X, Y, 12, cy, r * 0.55, r * 0.55, 0.55))
        if t > 0.25:
            split = (t - 0.25) / 0.75
            pts = [(12, cy - r - 1), (10.5, cy - 2), (13, cy + 1), (11, cy + r + 1)]
            for a, b in zip(pts, pts[1:]):
                heat = np.maximum(heat, seg(X, Y, (a[0] - split * 1.5, a[1]), (b[0] - split * 1.5, b[1]), 0.7, 1.0))
                heat = np.maximum(heat, seg(X, Y, (a[0] + split * 1.5, a[1]), (b[0] + split * 1.5, b[1]), 0.7, 1.0))
            heat *= 1 - 0.55 * split
            for i in range(3):
                heat = np.maximum(heat, blob(X, Y, 8 + i * 4, cy + r + 2 + 10 * split * split, 0.9, 0.9, 0.9 * (1 - split)))
        return paint(heat, PAL["blood"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 12, 46, 4, 6, d)


def ether():
    w, h = 36, 32
    X, Y = field(w, h)

    def d(k, t):
        a0 = -2.6 + 2.4 * ease(t)
        heat = ring(X, Y, 18, 17, 10, 1.8 * (1 - 0.5 * t), squash=0.8, a=1.0 - 0.4 * t, arc=(a0, a0 + 2.2))
        heat = np.maximum(heat, ring(X, Y, 18, 17, 7.5, 1.0, 0.8, 0.8 * (1 - t), arc=(a0 + 0.4, a0 + 1.8)))
        if t > 0.4:
            for i in range(4):
                heat = np.maximum(heat, blob(X, Y, 10 + i * 5, 8 + (i % 2) * 4 - 6 * (t - 0.4), 0.9, 0.9, 0.9 * (1 - t)))
        return paint(heat, PAL["arcane"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 18, 27, 3, 5, d)


def stone():
    w, h = 40, 46
    X, Y = field(w, h)

    def d(k, t):
        heat = np.zeros_like(X)
        for i in range(7):
            ang = i * 2 * math.pi / 7 + 0.3
            ex, ey = 20 + math.cos(ang) * 13, 25 + math.sin(ang) * 15
            s = ease(min(1.0, t * 1.8 - i * 0.05))
            px = 20 + (ex - 20) * s
            py = 42 + (ey - 42) * s
            heat = np.maximum(heat, blob(X, Y, px, py, 3.2, 2.6, 1.0))
        if t > 0.55:
            heat = np.maximum(heat, ring(X, Y, 20, 25, 13.5, 1.0, 15 / 13, 0.7))
        return paint(heat, PAL["stone"], (0.32, 0.5, 0.7, 0.9))
    return anim(w, h, 20, 42, 4, 7, d)


def execute():
    w, h = 32, 32
    X, Y = field(w, h)

    def d(k, t):
        heat = np.zeros_like(X)
        s1 = min(1.0, 0.4 + t * 4)
        s2 = min(1.0, max(0.0, t * 4 - 0.6))
        fade = 1.0 if t < 0.5 else 1 - (t - 0.5) * 1.6
        if s1 > 0:
            heat = np.maximum(heat, seg(X, Y, (6, 5), (6 + 20 * s1, 5 + 20 * s1), 1.8, fade, taper=True))
        if s2 > 0:
            heat = np.maximum(heat, seg(X, Y, (26, 5), (26 - 20 * s2, 5 + 20 * s2), 1.8, fade, taper=True))
        if t >= 0.5:
            heat = np.maximum(heat, blob(X, Y, 16, 15, 3, 3, fade))
        return paint(heat, PAL["blood"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 16, 27, 3, 5, d)


def dawn():
    w, h = 36, 72
    X, Y = field(w, h)

    def d(k, t):
        down = ease(min(1.0, t * 3))
        wid = 5.5 if t < 0.6 else 5.5 * (1 - (t - 0.6) * 2.2)
        top = 66 - 66 * down
        col = np.where(Y >= top, blob(X, Y, 18, 66, max(wid, 0.8), 200, 1.0), 0.0)
        col *= 0.75 + 0.25 * (Y / h)
        heat = np.maximum(col, ring(X, Y, 18, 66, 6 + 8 * t, 1.3, 0.4, 1 - 0.5 * t))
        for i in range(4):
            sy = 60 - 50 * ((t * 1.2 + i * 0.22) % 1.0)
            heat = np.maximum(heat, blob(X, Y, 8 + i * 7, sy, 0.9, 1.4, 0.95 * (1 - 0.6 * t)))
        return paint(heat, PAL["holy"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 18, 67, 4, 8, d)


def excited():
    w, h = 40, 48
    X, Y = field(w, h)

    def d(k, t):
        heat = np.zeros_like(X)
        for i in range(6):
            ang = t * 5 + i * 2 * math.pi / 6
            r = 9 + 3 * math.sin(i + t * 4)
            px, py = 20 + math.cos(ang) * r, 40 - 34 * ((t + i * 0.12) % 1.0)
            sz = 2.6 * (1 - 0.4 * t)
            heat = np.maximum(heat, star(X, Y, px, py, 4, sz + 1.5, 0.6, rot=ang, a=1.0))
            heat = np.maximum(heat, blob(X, Y, px, py, 1.0, 1.0, 1.0))
        heat = np.maximum(heat, ring(X, Y, 20, 44, 5 + 10 * t, 1.2, 0.38, 1 - 0.7 * t))
        return paint(heat, PAL["orange"], (0.3, 0.5, 0.7, 0.88))
    return anim(w, h, 20, 44, 4, 7, d)


def kite_shape(X, Y, cx, cy, s):
    """一面盾的形状（上平、下尖）：盾里面 > 0。"""
    u, v = (X - cx) / s, (Y - cy) / s
    top = v > -1.0
    side = np.abs(u) < np.where(v < 0.2, 0.85, 0.85 * (1.4 - v) / 1.2)
    return top & side & (v < 1.4)


def guard():
    w, h = 30, 44
    X, Y = field(w, h)

    def d(k, t):
        s = 6 + 3 * ease(min(1.0, t * 3)) - (0 if t < 0.7 else 3 * (t - 0.7))
        inside = kite_shape(X, Y, 15, 20, max(s, 2))
        edge = inside & ~kite_shape(X, Y, 15, 20.6, max(s - 1.6, 1))
        heat = np.where(edge, 0.95, np.where(inside, 0.4 + 0.2 * np.sin(Y * 0.8 + k), 0.0)).astype(np.float32)
        heat = np.maximum(heat, blob(X, Y, 15, 18, 1.3, 1.3, 1.0) * inside)
        return paint(heat, PAL["hex"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 15, 40, 4, 7, d)


def wisp():
    w, h = 16, 32
    X, Y = field(w, h)

    def d(k, t):
        y = 28 - 16 * ease(t)
        a = 1.0 - 0.6 * t
        heat = blob(X, Y, 8 + math.sin(k) * 1.2, y, 2.6, 3.2, a)
        heat = np.maximum(heat, blob(X, Y, 8 - math.sin(k) * 1.0, y + 5, 1.5, 3.0, 0.8 * a))
        return paint(heat, PAL["shade"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 8, 29, 4, 6, d)


def laser_mark():
    w, h = 48, 26
    X, Y = field(w, h)

    def d(k, t):
        r = 20 - 8 * t
        heat = ring(X, Y, 24, 13, r, 1.0, squash=0.5, a=1.0)
        for i in range(4):
            ang = i * math.pi / 2 + t * 1.2
            p0 = (24 + math.cos(ang) * (r - 5), 13 + math.sin(ang) * (r - 5) * 0.5)
            p1 = (24 + math.cos(ang) * (r - 1), 13 + math.sin(ang) * (r - 1) * 0.5)
            heat = np.maximum(heat, seg(X, Y, p0, p1, 0.8, 1.0))
        if k % 2 == 0:
            heat = np.maximum(heat, blob(X, Y, 24, 13, 1.6, 1.0, 1.0))
        return paint(heat, PAL["blood"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 24, 13, 5, 9, d)


def laser():
    w, h = 44, 160
    X, Y = field(w, h)

    def d(k, t):
        widths = [1.2, 7, 9, 8, 6, 4, 2.4, 1.2]
        wd = widths[k]
        col = blob(X, Y, 22, 150, wd, 400, 1.0)
        col = np.where(Y <= 151, col, 0.0)
        heat = col
        heat = np.maximum(heat, ring(X, Y, 22, 150, 3 + 16 * ease(t), 1.4, 0.4, 1 - 0.6 * t))
        heat = np.maximum(heat, blob(X, Y, 22, 150, 6 * (1 - 0.6 * t), 3 * (1 - 0.6 * t), 1.0))
        if k >= 2:
            for i in range(5):
                ang = i * 2 * math.pi / 5 + k
                heat = np.maximum(heat, blob(X, Y, 22 + math.cos(ang) * 10 * t, 148 - 8 * t * (i % 3), 0.9, 0.9, 0.8))
        return paint(heat, PAL["blood"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 22, 151, 3, 8, d)


def comet():
    w, h = 64, 120
    X, Y = field(w, h)
    end = (32, 104)
    start = (58, 6)

    def d(k, t):
        heat = np.zeros_like(X)
        if k < 6:
            s = k / 5
            hx = start[0] + (end[0] - start[0]) * s
            hy = start[1] + (end[1] - start[1]) * s
            tail = (hx + 10, hy - 34)
            heat = np.maximum(heat, seg(X, Y, (hx, hy), tail, 3.2, 0.85, taper=True))
            heat = np.maximum(heat, blob(X, Y, hx, hy, 4.5, 4.5, 1.0))
        else:
            s = (k - 6) / 4
            heat = np.maximum(heat, blob(X, Y, *end, 9 * (1 - 0.5 * s), 6 * (1 - 0.5 * s), 1.0 - 0.4 * s))
            heat = np.maximum(heat, ring(X, Y, end[0], end[1], 6 + 20 * ease(s), 1.8, 0.45, 1 - 0.6 * s))
            for i in range(6):
                ang = -math.pi + i * math.pi / 5
                heat = np.maximum(heat, blob(X, Y, end[0] + math.cos(ang) * 16 * s, end[1] - 10 * s + 12 * s * s
                                             + math.sin(ang) * 4, 1.3, 1.3, 0.9 * (1 - s)))
        return paint(heat, PAL["comet"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 32, 106, 5, 11, d)


def final_form():
    w, h = 56, 64
    X, Y = field(w, h)

    def d(k, t):
        heat = star(X, Y, 28, 34, 10, 10 + 16 * ease(t), 1.4, rot=0.1 * k, a=1.0 - 0.7 * t, r0=5)
        aura = ring(X, Y, 28, 34, 11 + 2 * math.sin(k), 1.6, squash=1.7, a=0.9 * (1 - 0.5 * t))
        heat = np.maximum(heat, aura)
        heat = np.maximum(heat, ring(X, Y, 28, 58, 6 + 16 * ease(t), 1.6, 0.36, 1 - 0.6 * t))
        heat = np.maximum(heat, blob(X, Y, 28, 34, 5 * (1 - t), 7 * (1 - t), 1.0))
        return paint(heat, PAL["holy"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 28, 59, 4, 8, d)


def snowball():
    w, h = 22, 22
    X, Y = field(w, h)

    def d(k, t):
        dx, dy = X - 11, Y - 11
        inside = dx * dx + dy * dy <= 8.2 ** 2
        light = np.clip(0.75 - (dx + dy) * 0.045, 0, 1)
        heat = np.where(inside, 0.4 + 0.6 * light, 0.0).astype(np.float32)
        ang = k * math.pi / 2
        for j in range(3):
            a2 = ang + j * 2.1
            sx, sy = 11 + math.cos(a2) * 4.5, 11 + math.sin(a2) * 4.5
            heat = np.where((X - sx) ** 2 + (Y - sy) ** 2 <= 1.3, 0.3, heat)
        return paint(heat, PAL["snow"], (0.2, 0.42, 0.66, 0.86))
    return anim(w, h, 11, 11, 4, 4, d)


def snow_burst():
    w, h = 60, 48
    X, Y = field(w, h)
    rng = np.random.default_rng(9)
    bits = [(rng.uniform(-math.pi, 0), rng.uniform(10, 20)) for _ in range(8)]

    def d(k, t):
        heat = blob(X, Y, 30, 30, 9 * (1 - 0.6 * t), 7 * (1 - 0.6 * t), 1.0)
        heat = np.maximum(heat, ring(X, Y, 30, 38, 8 + 18 * ease(t), 2.0, 0.42, 1 - 0.5 * t))
        for ang, sp in bits:
            px = 30 + math.cos(ang) * sp * ease(t)
            py = 30 + math.sin(ang) * sp * 0.9 * ease(t) + 14 * t * t
            heat = np.maximum(heat, blob(X, Y, px, py, 1.8, 1.6, 0.95 * (1 - 0.4 * t)))
        return paint(heat, PAL["snow"], (0.3, 0.5, 0.7, 0.88))
    return anim(w, h, 30, 38, 4, 7, d)


def quantum():
    w, h = 68, 40
    X, Y = field(w, h)

    def d(k, t):
        head = -math.pi / 2 + 2 * math.pi * ease(t)
        heat = ring(X, Y, 34, 22, 26, 1.6, squash=0.5, a=1.0, arc=(head - 1.8, head))
        heat = np.maximum(heat, ring(X, Y, 34, 22, 23, 1.0, 0.5, 0.8, arc=(head - 1.0, head)))
        if t > 0.6:
            heat = np.maximum(heat, ring(X, Y, 34, 22, 26, 0.9, 0.5, (1 - t) * 2.2))
        return paint(heat, PAL["cyan"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 34, 24, 3, 6, d)


def undying():
    w, h = 56, 60
    X, Y = field(w, h)

    def d(k, t):
        s = ease(min(1.0, t * 2.5))
        fade = 1.0 if t < 0.75 else 1 - (t - 0.75) * 3
        heat = ring(X, Y, 28, 9, 7, 1.0, 0.38, fade)
        for side in (-1, 1):
            for j in range(4):
                ang = math.radians(200 - j * 22) if side < 0 else math.radians(-20 + j * 22)
                ln = (9 + j * 3) * s
                x0, y0 = 28 + side * 4, 28
                p1 = (x0 + math.cos(ang) * ln, y0 - abs(math.sin(ang)) * ln * 0.7 - j * 2 * s)
                heat = np.maximum(heat, seg(X, Y, (x0, y0), p1, 2.0 - j * 0.25, 0.85 * fade, taper=True))
        heat = np.maximum(heat, blob(X, Y, 28, 30, 3, 6, 0.6 * fade))
        return paint(heat, PAL["holy"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 28, 54, 5, 8, d)


def immolate():
    w, h = 56, 34
    X, Y = field(w, h)

    def d(k, t):
        heat = ring(X, Y, 28, 22, 23, 1.6, squash=0.42, a=0.85 * (1 - 0.4 * t))
        for i in range(10):
            ang = i * 2 * math.pi / 10 + k * 0.4
            px, py = 28 + math.cos(ang) * 23, 22 + math.sin(ang) * 23 * 0.42
            heat = np.maximum(heat, blob(X, Y, px, py - 3 - 3 * t, 1.6, 3.2 * (1 - 0.4 * t), 0.95 * (1 - 0.5 * t)))
        return paint(heat, PAL["fire"], (0.3, 0.48, 0.68, 0.88))
    return anim(w, h, 28, 22, 3, 5, d)


def gust():
    w, h = 26, 26
    X, Y = field(w, h)

    def d(k, t):
        heat = np.zeros_like(X)
        for j in range(2):
            r = 4 + 4 * j + 3 * t
            a0 = k * 1.3 + j * math.pi
            heat = np.maximum(heat, ring(X, Y, 13, 13, r, 0.9, a=1 - 0.6 * t, arc=(a0, a0 + 2.4)))
        heat = np.maximum(heat, blob(X, Y, 13, 13, 2 * (1 - t), 2 * (1 - t), 1.0))
        return paint(heat, PAL["wind"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 13, 20, 3, 4, d)


def ward():
    w, h = 44, 50
    X, Y = field(w, h)

    def d(k, t):
        s = ease(min(1.0, t * 3))
        fade = 1.0 if t < 0.7 else 1 - (t - 0.7) * 3
        dome = ring(X, Y, 22, 44, 17 * s, 1.4, squash=1.6, a=fade)
        dome = np.where(Y <= 45, dome, 0.0)
        heat = np.maximum(dome, ring(X, Y, 22, 44, 17 * s, 1.3, 0.38, 0.9 * fade))
        ang = -2.6 + t * 2.2
        heat = np.maximum(heat, ring(X, Y, 22, 44, 17 * s - 2, 0.9, 1.6, fade, arc=(ang, ang + 0.6)))
        for i in range(3):
            heat = np.maximum(heat, blob(X, Y, 12 + i * 10, 40 - 30 * ((t + i * 0.3) % 1.0), 0.9, 1.3, 0.9 * fade))
        return paint(heat, PAL["holy"], (0.3, 0.5, 0.72, 0.9))
    return anim(w, h, 22, 46, 4, 8, d)


EFFECTS = [
    ("burn", burn), ("frost", frost), ("light_pop", light_pop), ("escape", escape), ("grow", grow), ("punch", punch),
    ("heavy", heavy), ("missile", missile), ("missile_pop", missile_pop), ("spark", spark), ("crack", crack),
    ("ether", ether), ("stone", stone), ("execute", execute), ("dawn", dawn), ("excited", excited), ("guard", guard),
    ("wisp", wisp), ("laser_mark", laser_mark), ("laser", laser), ("comet", comet), ("final_form", final_form),
    ("snowball", snowball), ("snow_burst", snow_burst), ("quantum", quantum), ("undying", undying),
    ("immolate", immolate), ("gust", gust), ("ward", ward),
]


def animations():
    return [(name,) + make() for name, make in EFFECTS]


# ===================== 拼图、横条、表 =====================

def pack(anims):
    rows, y = [], 0
    for name, w, h, anchor, ticks, frames in anims:
        per_row = min(len(frames), SHEET_W // w)
        lines = -(-len(frames) // per_row)
        rows.append((name, 0, y, w, h, len(frames), per_row, anchor[0], anchor[1], ticks))
        y += lines * h
    width = -(-max(r[6] * r[3] for r in rows) // 4) * 4
    height = -(-y // 4) * 4
    sheet = np.zeros((height, width, 4), np.uint8)
    for (name, x0, y0, w, h, n, per_row, _, _, _), (_, _, _, _, _, frames) in zip(rows, anims):
        for k, f in enumerate(frames):
            assert f.shape == (h, w, 4), (name, k, f.shape)
            assert set(np.unique(f[..., 3])) <= {0, 255}, f"{name} {k}: half-transparent pixels"
            assert f[..., 3].any(), f"{name} {k}: an empty frame"
            x, yy = x0 + (k % per_row) * w, y0 + (k // per_row) * h
            sheet[yy:yy + h, x:x + w] = f
    return sheet, rows


def runs_of(anims):
    """DFXR、u16 颜色数、颜色（RGBA）、u16 动画数，每段动画 u8 帧数，每帧 u16 横条数和横条（x、y、宽、颜色各一个字节）。"""
    palette, body = {}, bytearray()
    for name, w, h, anchor, ticks, frames in anims:
        assert w <= 255 and h <= 255 and len(frames) <= 255, name
        body.append(len(frames))
        for f in frames:
            runs = bytearray()
            n = 0
            for y in range(h):
                x = 0
                while x < w:
                    if f[y, x, 3] == 0:
                        x += 1
                        continue
                    c = tuple(int(v) for v in f[y, x, :3])
                    x0 = x
                    while x < w and f[y, x, 3] and tuple(int(v) for v in f[y, x, :3]) == c:
                        x += 1
                    k = palette.setdefault(c, len(palette))
                    assert k <= 255, "more than 256 colours"
                    runs += bytes((x0, y, x - x0, k))
                    n += 1
            body += n.to_bytes(2, "little") + runs
    out = bytearray(b"DFXR") + len(palette).to_bytes(2, "little")
    for c in palette:
        out += bytes(c) + bytes([255])
    out += len(anims).to_bytes(2, "little") + body
    return bytes(out)


def table(rows, size):
    lines = [
        "//! 本包战场特效在 `effects/league_hextech_fx#sheet.png` 上的位置。",
        "//! tools/art/hextech_fx.py 生成，别手改。",
        "",
        "/// 一段动画：帧从 (`x`, `y`) 往右排，一行 `per_row` 帧，每帧 `w` x `h`；(`ax`, `ay`) 是放在发生地点（英雄脚下）的那一点；",
        "/// 一帧停 `ticks` 个模拟 tick。",
        "#[derive(Clone, Copy, Debug, PartialEq, Eq)]",
        "pub struct Anim {",
        "    pub name: &'static str,",
        "    pub x: u16,",
        "    pub y: u16,",
        "    pub w: u16,",
        "    pub h: u16,",
        "    pub frames: u8,",
        "    pub per_row: u8,",
        "    pub ax: u16,",
        "    pub ay: u16,",
        "    pub ticks: u8,",
        "}",
        "",
        "/// 图的大小（像素）。",
        f"pub const SHEET: (u16, u16) = ({size[0]}, {size[1]});",
        "",
        f"pub const ANIMS: [Anim; {len(rows)}] = [",
    ]
    for name, x, y, w, h, n, per_row, ax, ay, ticks in rows:
        lines.append(f'    Anim {{ name: "{name}", x: {x}, y: {y}, w: {w}, h: {h}, frames: {n}, per_row: {per_row}, ax: {ax}, '
                     f"ay: {ay}, ticks: {ticks} }},")
    lines.append("];")
    return "\n".join(lines) + "\n"


def preview(anims, path, scale=4):
    """每段动画一行，`scale` 倍，草地的底色。"""
    pad = 6
    width = max(len(fr) * (w + pad) for _, w, h, _, _, fr in anims) + pad
    height = sum(h + pad for _, w, h, _, _, fr in anims) + pad
    img = np.zeros((height, width, 4), np.uint8)
    img[..., :3] = (52, 92, 52)
    img[..., 3] = 255
    y = pad
    for name, w, h, anchor, ticks, frames in anims:
        x = pad
        for f in frames:
            m = f[..., 3] > 0
            region = img[y:y + h, x:x + w]
            region[m] = f[m]
            # 锚点（放在英雄脚下的那一点）标一个黑点
            ax, ay = anchor
            img[y + ay, x + ax, :3] = (0, 0, 0)
            x += w + pad
        y += h + pad
    Image.fromarray(img, "RGBA").resize((width * scale, height * scale), Image.NEAREST).save(path)


# 每段动画是什么（给画师看的：哪个海克斯、什么时候放、画什么）
WHAT = {
    "burn": "烈焰烙印 Firebrand：被点燃的英雄每烧一下，身上冒一小团火（3 秒里 6 下）",
    "frost": "彻骨冰寒 Ice Cold：命中时冰晶在英雄身上炸开、碎成冰碴",
    "light_pop": "点亮他们！ Light 'em Up!：第 4 下命中时一团金色的星爆",
    "escape": "逃跑计划 Escape Plan：残血时一层蓝色的泡泡盾罩住英雄，两边几道速度线",
    "grow": "坦克引擎 Tank Engine / 歌利亚巨人 Goliath：脚下一圈绿光、往上冒的箭头（变强、变大）",
    "punch": "秘术冲拳 Mystic Punch：普攻时一小团蓝色的拳光（一秒最多一次）",
    "heavy": "重击手 Heavy Hitter：橙色的冲击、碎块飞出去",
    "missile": "魔法飞弹 Magic Missile：飞行中的紫色飞弹（循环，从施法者飞向目标，锚点是弹的中心）",
    "missile_pop": "魔法飞弹打中时：紫色的小爆炸",
    "spark": "连锁闪电 Chain Lightning：闪电（游戏里画成线）落点的蓝白电光",
    "crack": "弱点暴露 Vulnerability：英雄头顶一个红色的圈裂开（受到的伤害 +10%）",
    "ether": "以太武器 Ethereal Weapon：紫色的月牙斩",
    "stone": "巨像的勇气 Courage of the Colossus：石块从地上升起、围着英雄成一圈石盾",
    "execute": "处刑人 Executioner：红色的十字斩",
    "dawn": "黎明使者的决心 Dawnbringer's Resolve：金色光柱从天上落到英雄身上，往上飘的光点",
    "excited": "兴奋起来！ Get Excited!：绕着身体往上飞的橙色星星",
    "guard": "守护者 Guardian：队友身前一面蓝白的盾（两人之间的光线游戏里画成线）",
    "wisp": "惊世邪恶 Phenomenal Evil：一缕紫色的魂飘进英雄身体",
    "laser_mark": "轨道激光 Orbital Laser 的瞄准：地上的红色瞄准圈慢慢收紧（正好 45 tick，之后激光打下来）",
    "laser": "轨道激光打下来：从天而降的红白光柱、地上一圈灼烧",
    "comet": "残忍 Cruelty：彗星从右上方落下（前 6 帧 = 30 tick 是下落），后 5 帧砸地炸开",
    "final_form": "最终形态 Final Form：放大招后金色的光爆、身边一圈光焰（身体变大由引擎做，不用画）",
    "snowball": "超级雪球 Giant Snowball：飞行中的大雪球（循环，转动；锚点是球心）",
    "snow_burst": "超级雪球落地：雪花炸开、地上一圈雪",
    "quantum": "量子计算 Quantum Computing：绕英雄一圈的青色斩击（地上的椭圆）",
    "undying": "不灭意志 Undying Will：头顶的光环和背后张开的金色翅膀",
    "immolate": "献祭光环 Immolate：脚下一圈火焰（每秒一次）",
    "gust": "台风 Typhoon：风刃（游戏里画成线）落点的小旋风",
    "ward": "圣光庇佑 Sacred Ward：金白色的光罩罩住友方英雄",
}


def dump_frames(anims, out):
    """每一帧存成一张 PNG（frames/<动画>/<动画>_<第几帧>.png），加一份 spec.json：画师照这个格子重画。"""
    import json
    spec = []
    for name, w, h, anchor, ticks, frames in anims:
        d = os.path.join(out, "frames", name)
        os.makedirs(d, exist_ok=True)
        for k, f in enumerate(frames):
            Image.fromarray(f, "RGBA").save(os.path.join(d, f"{name}_{k}.png"))
        spec.append({"name": name, "w": w, "h": h, "anchor": list(anchor), "frames": len(frames), "ticks": ticks,
                     "seconds": round(len(frames) * ticks / 60, 3), "what": WHAT.get(name, "")})
    with open(os.path.join(out, "spec.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)


def load_frames(src):
    """画师交回来的帧（dump_frames 的格子）：大小、帧数、锚点照 spec.json；透明度压成 0 / 255。"""
    import json
    with open(os.path.join(src, "spec.json"), encoding="utf-8") as f:
        spec = {s["name"]: s for s in json.load(f)}
    out = []
    for name, _ in EFFECTS:
        s = spec[name]
        frames = []
        for k in range(s["frames"]):
            img = np.array(Image.open(os.path.join(src, "frames", name, f"{name}_{k}.png")).convert("RGBA"))
            assert img.shape == (s["h"], s["w"], 4), f"{name} {k}: {img.shape[1]}x{img.shape[0]}, want {s['w']}x{s['h']}"
            img[..., 3] = np.where(img[..., 3] >= 128, 255, 0)
            img[img[..., 3] == 0] = 0
            frames.append(img)
        out.append((name, s["w"], s["h"], tuple(s["anchor"]), s["ticks"], frames))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="also write every animation's frames, 4x, to this file")
    ap.add_argument("--check", action="store_true", help="compare with the files instead of writing them")
    ap.add_argument("--dump", help="write every frame as a PNG and spec.json into this folder (for the artist)")
    ap.add_argument("--from-frames", help="build the sheet from an artist's frames (the --dump layout) instead")
    ap.add_argument("--procedural", action="store_true",
                    help="overwrite the sheet with this script's drawing (it is Codex's art since 0.3.1)")
    a = ap.parse_args()
    # 0.3.1（2026-11-26）起图集是 Codex 重画的，源头是图集本身（tools/art/fx_frames.py dump / build）；这个脚本画的是
    # 0.3.0 的占位图，只有明说 --procedural 才拿它覆盖
    if not (a.preview or a.dump or a.from_frames or a.procedural):
        sys.exit("the sheet is Codex's art since 0.3.1: edit it with tools/art/fx_frames.py (dump / build); "
                 "--procedural overwrites it with this script's placeholder drawing")
    anims = load_frames(a.from_frames) if a.from_frames else animations()
    if a.dump:
        dump_frames(anims, a.dump)
    sheet, rows = pack(anims)
    text = table(rows, (sheet.shape[1], sheet.shape[0]))
    runs = runs_of(anims)
    if a.preview:
        preview(anims, a.preview)
    # 只拆帧、只出预览：不碰图集
    if not (a.from_frames or a.procedural or a.check):
        return
    if a.check:
        bad = []
        try:
            old = np.array(Image.open(SHEET).convert("RGBA"))
            if old.shape != sheet.shape or (old != sheet).any():
                bad.append(SHEET)
        except FileNotFoundError:
            bad.append(SHEET)
        for path, want, is_text in ((ATLAS, text.encode("utf-8"), True), (RUNS, runs, False)):
            try:
                with open(path, "rb") as f:
                    got = f.read()
                # 表是文本（检出时可能换成 CRLF），横条是二进制：原样比
                if is_text:
                    got = got.replace(b"\r\n", b"\n")
                if got != want:
                    bad.append(path)
            except FileNotFoundError:
                bad.append(path)
        if bad:
            sys.exit("out of date (run tools/art/hextech_fx.py): " + ", ".join(bad))
        print("ok: the sheet, its table and its runs are this script's")
        return
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    Image.fromarray(sheet, "RGBA").save(SHEET, optimize=True)
    with open(ATLAS, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(RUNS, "wb") as f:
        f.write(runs)
    n = sum(len(fr) for *_, fr in anims)
    print(f"{len(anims)} animations, {n} frames, sheet {sheet.shape[1]}x{sheet.shape[0]}, runs {len(runs)} bytes")


if __name__ == "__main__":
    main()
