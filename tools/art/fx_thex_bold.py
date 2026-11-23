#!/usr/bin/env python3
"""海克斯霸龙（tft_thex）的特效重画得更醒目（用户 2026-11-23：「海克斯霸龙的激光特效看不到 什么问题？」「事没做吗」
「其他特效效果也感觉挺淡的 起码做明显一点酷炫一点啊」）。

原来的特效是 import_thex_fx.py 从用户的 Gemini 图导进来的，素材都在，可是太小、太细：普攻命中 7-11 个游戏像素宽，
大招激光命中 11-21，导弹落地的爆炸 17 x 23，子弹 11 x 3，护盾是一圈细线；大招的激光是一颗 37 x 9 的小光弹，以每拍
9000 飞 10 拍（0.17 秒）就没了，屏幕上一闪而过。

这里重画这些动作（其余动作逐像素不动），都画在高清（PPU 2）上，1x 由高清每 2 x 2 投票缩出来；颜色沿用原图的三套：
火焰的橙黄、海克斯的青蓝、烟的灰。硬边，没有半透明（和原图一样）。

- r_beam：激光。不再是飞的小光弹，是一整条从嘴里打出去的光束：图的中心就是投射物的位置（霸龙身上、离地 9000），
  光束画在右半边、和伤害线一样长（r_len 90000 = 90 个游戏像素），亮起 -> 打满 -> 闪一下 -> 变细 -> 散掉，约 0.3 秒；
  build_thex.py 让这颗投射物几乎不动（每拍 60）、寿命和动画一样长、不循环。
- q_fall：导弹落地。前三帧（掉下来的导弹）不动，后面换成：白光一闪 -> 火球 + 地上一圈海克斯冲击波 -> 火球炸开、碎屑 ->
  烟和余烬（大招的导弹 r_fall 用的也是它）。
- r_shield：护盾。粗亮的青边、里面一圈六边形能量纹，四帧轮着亮，像在呼吸。
- a_bullet / a_hit / a_crit：加特林的子弹更长更亮；命中是一团白芯的火花；第四发的暴击是青白的星爆加一圈冲击环。
- e_dash / e_hit：冲撞起步的尘土放大、带火星；咬中时咬合的牙后面一团白橙的冲击和一圈冲击环。
- r_hit：激光打中的人身上一团青白的光爆。

    python tools/art/fx_thex_bold.py              # 写 tft/effects/tft_thex_fx 和 tft_thex_big
    python tools/art/fx_thex_bold.py --preview D  # 只出每个动作的预览图（新旧对照），不写图
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_hd as PH  # noqa: E402
import strips as G  # noqa: E402

FX = os.path.join(ROOT, "tft", "effects", "tft_thex_fx")
BIG = os.path.join(ROOT, "tft", "effects", "tft_thex_big")
PPU = 2

# 原图里的三套颜色（亮 -> 暗）
E = [(255, 255, 255), (232, 252, 253), (176, 236, 250), (96, 214, 250), (51, 182, 240), (40, 128, 201),
     (28, 78, 128), (24, 46, 74)]
F = [(255, 253, 232), (254, 240, 160), (252, 206, 64), (247, 160, 40), (236, 104, 38), (186, 62, 36),
     (116, 40, 30), (64, 28, 24)]
S = [(196, 194, 198), (160, 160, 168), (122, 124, 134), (88, 92, 102), (58, 62, 72)]
BEAM_LEN = 90          # 激光伤害线长 r_len 90000 = 90 个游戏像素（build_thex.py）
# 帧的中心是单位的位置（脚底往上一截）：原图打在身上的特效画在中心往上 25-28（高清），脚下的（尘土、减速、冲击波）
# 在中心往下 16 左右。新画的照抄这两个高度。
BODY = -27
FEET = 16


# ===================== 画布和画笔（高清像素） =====================

class Can:
    """一帧高清画布：1x 宽高 (w1, h1) 都是单数，高清是它的两倍；中心（特效放的那个点）在 (w1, h1)。"""

    def __init__(self, w1, h1):
        self.w1, self.h1 = w1, h1
        self.a = np.zeros((h1 * PPU, w1 * PPU, 4), np.uint8)
        self.cx, self.cy = float(w1), float(h1)
        yy, xx = np.mgrid[0:h1 * PPU, 0:w1 * PPU]
        self.x, self.y = xx + 0.5, yy + 0.5

    def put(self, mask, c):
        self.a[mask, :3] = c
        self.a[mask, 3] = 255

    def ell(self, cx, cy, rx, ry=None):
        ry = rx if ry is None else ry
        return ((self.x - cx) / max(rx, 0.01)) ** 2 + ((self.y - cy) / max(ry, 0.01)) ** 2

    def disc(self, cx, cy, rx, c, ry=None):
        self.put(self.ell(cx, cy, rx, ry) <= 1.0, c)

    def ring(self, cx, cy, rx, ry, th, c):
        d = self.ell(cx, cy, rx, ry)
        inner = self.ell(cx, cy, max(rx - th, 0.01), max(ry - th * ry / rx, 0.01))
        self.put((d <= 1.0) & (inner > 1.0), c)

    def ball(self, cx, cy, r, ramp, ry=None, steps=(1.0, 0.8, 0.62, 0.44, 0.26)):
        """一团光 / 火：外暗里亮的几圈。ramp 从亮到暗，取后面 len(steps) 个当外圈。"""
        cols = list(reversed(ramp[:len(steps)]))
        for f, c in zip(steps, cols):
            self.disc(cx, cy, r * f, c, None if ry is None else ry * f)

    def spike(self, cx, cy, ang, r0, r1, w, ramp):
        """从 (cx, cy) 往 ang 方向的一根尖刺：r0 处宽 w，到 r1 收成尖；越靠里越亮。"""
        dx, dy = math.cos(ang), math.sin(ang)
        px, py = self.x - cx, self.y - cy
        t = px * dx + py * dy
        s = np.abs(-px * dy + py * dx)
        k = np.clip((t - r0) / max(r1 - r0, 0.01), 0, 1)
        m = (t >= r0) & (t <= r1) & (s <= w * (1 - k) + 0.5)
        for i, c in enumerate(reversed(ramp)):
            lo = i / len(ramp)
            self.put(m & (k >= 1 - (i + 1) / len(ramp)) & (k <= 1 - lo), c)

    def rays(self, cx, cy, n, r0, r1, w, ramp, rot=0.0, jitter=None):
        for i in range(n):
            a = rot + 2 * math.pi * i / n
            rr = r1 if jitter is None else r1 * (1 - jitter[i % len(jitter)])
            self.spike(cx, cy, a, r0, rr, w, ramp)

    def dot(self, x, y, size, c):
        self.put((np.abs(self.x - x) + np.abs(self.y - y)) <= size, c)

    def band(self, x0, x1, cy, half, c, wob=None):
        """横的一道：x0..x1、上下各 half 宽；wob(x) 给每一列的上下起伏。"""
        h = half if wob is None else half + wob(self.x)
        self.put((self.x >= x0) & (self.x <= x1) & (np.abs(self.y - cy) <= h), c)

    def puff(self, cx, cy, r, ramp=S):
        """一团烟：暗边、中间亮一点、左上一点高光。"""
        self.disc(cx, cy, r, ramp[-1])
        self.disc(cx, cy - r * 0.12, r * 0.86, ramp[-2])
        self.disc(cx - r * 0.18, cy - r * 0.25, r * 0.5, ramp[-3])

    def blob_mask(self, cx, cy, r, ry=None, seed=0, amp=0.12):
        """边上带起伏的一团（半径随角度起伏几个正弦）。"""
        ry = r if ry is None else ry
        g = rng(seed)
        ks = [3, 4, 5, 7]
        ph = g.uniform(0, 2 * math.pi, len(ks))
        am = g.uniform(0.4, 1.0, len(ks)) * amp
        ang = np.arctan2(self.y - cy, self.x - cx)
        mod = 1 + sum(a * np.sin(k * ang + p) for k, a, p in zip(ks, am, ph))
        return np.sqrt(((self.x - cx) / max(r, 0.01)) ** 2 + ((self.y - cy) / max(ry, 0.01)) ** 2) <= mod

    def fire(self, cx, cy, r, seed, ry=None, dark=0, tongues=7):
        """一团火：外暗里亮几层不规则的圈，外面一圈火舌（往上的长一些）。dark：整体往暗挪几档（烧到后面）。"""
        ry = r if ry is None else ry
        ramp = F[dark:] + [F[-1]] * dark
        g = rng(seed)
        for i in range(tongues):
            a = -math.pi / 2 + g.uniform(-1.0, 1.0) * math.pi * (0.55 if i % 2 else 1.0)
            ln = r * g.uniform(1.15, 1.55) * (1.15 if math.sin(a) < 0 else 0.9)
            self.spike(cx, cy, a, r * 0.6, ln, r * 0.22, [ramp[2], ramp[3], ramp[4], ramp[5]])
        for f, col, amp in [(1.0, ramp[5], .14), (.84, ramp[4], .12), (.66, ramp[3], .1), (.48, ramp[2], .08),
                            (.3, ramp[1], .06), (.15, ramp[0], .04)]:
            self.put(self.blob_mask(cx, cy - r * (1 - f) * 0.25, r * f, ry * f, seed, amp), col)

    def cloud(self, cx, cy, r, seed, n=5, ramp=S, flat=0.75):
        """一朵烟：几团不规则的叠在一起，暗描边、下面暗上面亮、左上高光。"""
        g = rng(seed)
        parts = [(cx + g.uniform(-r, r) * 0.7, cy + g.uniform(-r, r) * 0.35 * flat, r * g.uniform(0.45, 0.7))
                 for _ in range(n)]
        for x, y, rr in parts:
            self.put(self.blob_mask(x, y, rr * 1.12, rr * 1.12 * flat, seed + 1, .1), ramp[-1])
        for x, y, rr in parts:
            self.put(self.blob_mask(x, y, rr, rr * flat, seed + 2, .1), ramp[-2])
        for x, y, rr in parts:
            self.put(self.blob_mask(x - rr * 0.1, y - rr * 0.22 * flat, rr * 0.72, rr * 0.72 * flat, seed + 3, .1),
                     ramp[-3])
        for x, y, rr in parts[:max(1, n // 2)]:
            self.put(self.blob_mask(x - rr * 0.28, y - rr * 0.38 * flat, rr * 0.32, rr * 0.32 * flat, seed + 4, .1),
                     ramp[0])

    def done(self):
        return self.a


def down(frames):
    """高清帧缩成 1x：每 2 x 2 投票，过半透明就透明，取最多的颜色（一样多取亮的）。"""
    res = []
    for f, ms in frames:
        H, W = f.shape[:2]
        h, w = H // PPU, W // PPU
        o = np.zeros((h, w, 4), np.uint8)
        blk = f[:h * PPU, :w * PPU].reshape(h, PPU, w, PPU, 4).transpose(0, 2, 1, 3, 4).reshape(h, w, PPU * PPU, 4)
        for y in range(h):
            for x in range(w):
                b = blk[y, x]
                opq = b[b[:, 3] > 0]
                if len(opq) * 2 < len(b):
                    continue
                cols, cnt = np.unique(opq[:, :3], axis=0, return_counts=True)
                best = max(range(len(cols)), key=lambda i: (cnt[i], int(cols[i].sum())))
                o[y, x] = (*cols[best], 255)
        res.append((o, ms))
    return res


def rng(seed):
    return np.random.default_rng(seed)


# ===================== 激光 r_beam =====================

# 1x 画布：中心是投射物（霸龙身体中心、离地 9），光束在右半边：先空 BEAM_GAP（嘴在身体前面，图跟着方向转，
# 光束就总是从嘴前打出去、不压在它自己身上），再打 BEAM_LEN 长
BEAM_GAP = 16
BEAM_W1, BEAM_H1 = 2 * (BEAM_GAP + BEAM_LEN) + 1, 15


def beam_frame(layers, muzzle, phase, sparks=0, seed=0, broken=False):
    """layers: [(半宽, 颜色)] 从外到里；muzzle: 枪口那团光的半径（0 = 没有）。"""
    c = Can(BEAM_W1, BEAM_H1)
    x0 = c.cx + 2 * BEAM_GAP
    x1 = x0 + 2 * BEAM_LEN
    taper = np.clip((x1 - c.x) / 18.0, 0, 1) * np.clip((c.x - x0) / 6.0 + 0.35, 0, 1)
    for i, (half, col) in enumerate(layers):
        wob = 0.9 * np.sin(c.x / 6.5 + phase + i) if i == 0 else 0.0
        h = half * taper + wob
        m = (c.x >= x0) & (c.x <= x1) & (np.abs(c.y - c.cy) <= h)
        if broken:
            m &= (np.floor((c.x - x0) / 9) + phase) % 3 != 0
        c.put(m, col)
    r = rng(seed)
    for _ in range(sparks):
        x = x0 + r.uniform(14, 2 * BEAM_LEN - 10)
        y = c.cy + r.choice([-1, 1]) * r.uniform(4, 9)
        c.dot(x, y, r.choice([1, 1.5]), E[r.integers(0, 3)])
    if muzzle:
        c.ball(x0 + 3, c.cy, muzzle, E)
    return c.done()


def beam():
    """亮起 -> 打满 -> 闪一下 -> 变细 -> 散掉，约 0.27 秒（build_thex.py 的投射物寿命跟它一样长）。"""
    return [
        (beam_frame([(2.0, E[3]), (1.0, E[0])], 6, 0.0), 40),
        (beam_frame([(7.0, E[6]), (5.5, E[4]), (3.6, E[2]), (1.6, E[0])], 10, 0.0, sparks=10, seed=1), 60),
        (beam_frame([(8.0, E[5]), (6.0, E[3]), (4.0, E[1]), (2.0, E[0])], 12, 1.7, sparks=14, seed=2), 60),
        (beam_frame([(4.5, E[5]), (3.0, E[3]), (1.4, E[0])], 7, 3.1, sparks=8, seed=3), 60),
        (beam_frame([(1.6, E[4])], 0, 4.4, sparks=10, seed=4, broken=True), 50),
    ]


# ===================== 预览 =====================

def show(frames, path, z=3, bg=(58, 72, 48)):
    """一排高清帧，z 倍，帧和帧之间空一格。"""
    W = sum(f.shape[1] + 6 for f, _ in frames)
    H = max(f.shape[0] for f, _ in frames)
    im = Image.new("RGBA", (W, H), (*bg, 255))
    x = 0
    for f, _ in frames:
        im.alpha_composite(Image.fromarray(f), (x, (H - f.shape[0]) // 2))
        x += f.shape[1] + 6
    im.resize((W * z, H * z), Image.NEAREST).save(path)


# ===================== 导弹落地 q_fall（大招的 r_fall 也用它） =====================

def blast_frames():
    """白光一闪 -> 火球 + 地上一圈海克斯冲击波 -> 炸开、碎屑 -> 烟和余烬 -> 散。中心是落点（目标脚下）。"""
    out = []
    W1, H1 = 61, 41
    gy = FEET           # 冲击波在中心往下（脚下）
    fy = FEET - 12      # 火球在中心往下多少（高清）
    # 1 白光一闪
    c = Can(W1, H1)
    c.rays(c.cx, c.cy + fy, 8, 4, 22, 2.2, [F[0], F[1], F[2]], rot=0.3)
    c.ball(c.cx, c.cy + fy, 11, [F[0], F[0], F[1], F[2], F[3]])
    out.append((c.done(), 40))
    # 2 火球 + 冲击波
    c = Can(W1, H1)
    c.ring(c.cx, c.cy + gy, 32, 10, 3.5, E[4])
    c.ring(c.cx, c.cy + gy, 30, 9, 1.5, E[1])
    c.fire(c.cx, c.cy + fy, 19, seed=5, ry=17, tongues=9)
    out.append((c.done(), 60))
    # 3 炸开：火球最大、火舌往上窜，碎屑往外飞，冲击波扩开
    c = Can(W1, H1)
    c.ring(c.cx, c.cy + gy, 46, 14, 3.5, E[5])
    c.ring(c.cx, c.cy + gy, 44, 13, 1.5, E[2])
    r = rng(11)
    for k in range(12):
        a = 2 * math.pi * k / 12 + r.uniform(-.2, .2)
        d = r.uniform(28, 38)
        c.dot(c.cx + d * math.cos(a), c.cy + fy + d * math.sin(a) * 0.8, r.choice([1.5, 2]),
              [F[2], F[5], S[3]][k % 3])
    c.fire(c.cx, c.cy + fy - 2, 25, seed=6, ry=21, tongues=10)
    out.append((c.done(), 70))
    # 4 火往下暗、烟冒上来，余烬
    c = Can(W1, H1)
    c.ring(c.cx, c.cy + gy, 56, 17, 2, E[5])
    c.cloud(c.cx, c.cy + fy - 12, 26, seed=7, n=6)
    c.fire(c.cx, c.cy + fy + 2, 13, seed=8, ry=10, dark=2, tongues=5)
    r = rng(12)
    for _ in range(14):
        c.dot(c.cx + r.uniform(-32, 32), c.cy + fy + r.uniform(-30, 8), 1.2, [F[1], F[2], F[3]][r.integers(0, 3)])
    out.append((c.done(), 90))
    # 5 烟散开往上飘
    c = Can(W1, H1)
    c.ring(c.cx, c.cy + gy, 60, 19, 1, E[6])
    c.cloud(c.cx, c.cy + fy - 18, 24, seed=9, n=5, ramp=S[:4])
    r = rng(13)
    for _ in range(8):
        c.dot(c.cx + r.uniform(-32, 32), c.cy + fy + r.uniform(-36, 2), 1, [F[3], F[4], F[5]][r.integers(0, 3)])
    out.append((c.done(), 110))
    return out


def q_fall(old):
    """原来的前三帧（掉下来的导弹）不动，后面换成新的爆炸。"""
    return list(old[:3]) + blast_frames()


# ===================== 护盾 r_shield =====================

def hexagon(c, cx, cy, r, col, th=1.0):
    pts = [(cx + r * math.cos(math.pi / 3 * k), cy + r * math.sin(math.pi / 3 * k)) for k in range(6)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for t in np.linspace(0, 1, n):
            c.dot(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, th * 0.5, col)


def shield_frames():
    """粗亮的青边、里面一圈六边形能量纹；四帧轮着亮、边一呼一吸。中心是霸龙。"""
    out = []
    W1, H1 = 63, 71
    oy = -19            # 原图护盾中心在单位中心往上 19（高清）
    for k in range(4):
        c = Can(W1, H1)
        rx, ry = 60, 50
        pulse = [0, 1, 2, 1][k]
        # 六边形纹：贴着边里面一圈，每帧亮的那几个转一点
        for i in range(14):
            a = 2 * math.pi * i / 14 + k * 0.11
            hx, hy = c.cx + (rx - 13) * math.cos(a), c.cy + oy + (ry - 13) * math.sin(a)
            lit = (i + k) % 4 == 0
            hexagon(c, hx, hy, 6.5, E[2] if lit else E[5], 1.6 if lit else 1.2)
        c.ring(c.cx, c.cy + oy, rx + pulse, ry + pulse, 6 + pulse, E[6])
        c.ring(c.cx, c.cy + oy, rx - 1 + pulse, ry - 1 + pulse, 4.2 + pulse * 0.5, E[4])
        c.ring(c.cx, c.cy + oy, rx - 2 + pulse, ry - 2 + pulse, 2.0, E[2])
        # 左上一段高光，跟着帧转
        d = c.ell(c.cx, c.cy + oy, rx - 2 + pulse, ry - 2 + pulse)
        ang = np.arctan2(c.y - (c.cy + oy), c.x - c.cx)
        a0 = -2.4 + k * 0.5
        c.put((d <= 1.0) & (d >= 0.9) & (np.abs(np.angle(np.exp(1j * (ang - a0)))) < 0.5), E[0])
        for j in range(3):
            a = a0 + 2.1 * j + 0.8
            c.dot(c.cx + (rx + pulse - 1) * math.cos(a), c.cy + oy + (ry + pulse - 1) * math.sin(a), 2, E[0])
        out.append((c.done(), 120))
    return out


# ===================== 普攻：子弹、命中、暴击 =====================

def bullet_frames():
    """往右飞的一颗曳光弹（投射物跟着方向转）：白芯、橙尾，尾巴一长一短闪。"""
    out = []
    for tail in (13, 10):
        c = Can(17, 5)
        head = c.cx + 14
        m = (c.x >= head - 2 * tail) & (c.x <= head)
        t = np.clip((c.x - (head - 2 * tail)) / (2 * tail), 0, 1)
        c.put(m & (np.abs(c.y - c.cy) <= 0.5 + 3.5 * t), F[4])
        c.put(m & (np.abs(c.y - c.cy) <= 0.5 + 2.2 * t), F[2])
        c.put(m & (np.abs(c.y - c.cy) <= 0.6 + 1.0 * t) & (t > 0.25), F[0])
        c.ball(head - 2, c.cy, 3.2, F)
        out.append((c.done(), 60))
    return out


def hit_frames():
    """普攻打中：白芯火花一炸、火星四散、余烬。"""
    out = []
    W1, H1 = 23, 51
    c = Can(W1, H1)
    c.rays(c.cx, (c.cy + BODY), 4, 2, 12, 1.8, [F[0], F[1], F[2]], rot=math.pi / 4)
    c.ball(c.cx, (c.cy + BODY), 5, [F[0], F[0], F[1], F[2], F[3]])
    out.append((c.done(), 30))
    c = Can(W1, H1)
    c.rays(c.cx, (c.cy + BODY), 8, 4, 19, 2.0, [F[1], F[2], F[3], F[4]], rot=0.25, jitter=[0, .25, .1, .3])
    c.ball(c.cx, (c.cy + BODY), 8, F)
    out.append((c.done(), 40))
    c = Can(W1, H1)
    r = rng(21)
    for k in range(10):
        a = 2 * math.pi * k / 10 + r.uniform(-.2, .2)
        d = r.uniform(12, 19)
        c.dot(c.cx + d * math.cos(a), (c.cy + BODY) + d * math.sin(a), 1.6, [F[1], F[2], F[3]][k % 3])
    c.ball(c.cx, (c.cy + BODY), 5, [F[2], F[3], F[4], F[5], F[6]])
    out.append((c.done(), 50))
    c = Can(W1, H1)
    for k in range(8):
        a = 2 * math.pi * k / 8 + r.uniform(-.3, .3)
        d = r.uniform(17, 21)
        c.dot(c.cx + d * math.cos(a), (c.cy + BODY) + d * math.sin(a), 1.1, [F[4], F[5]][k % 2])
    out.append((c.done(), 60))
    return out


def burst_frames(W1, r1, seed, sparks_fire):
    """青白的星爆 + 一圈冲击环（暴击、激光命中），打在身上。r1：最大的那圈多大（高清）。"""
    out = []
    H1 = (29 + int(r1)) | 1
    c = Can(W1, H1)
    c.rays(c.cx, (c.cy + BODY), 4, 3, r1 * 0.75, 2.6, [E[0], E[1], E[2], E[3]], rot=0.0)
    c.rays(c.cx, (c.cy + BODY), 4, 3, r1 * 0.45, 2.0, [E[0], E[1], E[3]], rot=math.pi / 4)
    c.ball(c.cx, (c.cy + BODY), r1 * 0.22, [E[0], E[0], E[1], E[2], E[3]])
    out.append((c.done(), 30))
    c = Can(W1, H1)
    c.rays(c.cx, (c.cy + BODY), 8, r1 * 0.2, r1 * 0.95, 2.6, [E[1], E[2], E[3], E[4], E[5]], rot=0.2,
           jitter=[0, .2, .05, .25])
    c.ball(c.cx, (c.cy + BODY), r1 * 0.4, E)
    out.append((c.done(), 40))
    c = Can(W1, H1)
    c.ring(c.cx, (c.cy + BODY), r1 * 0.72, r1 * 0.72, 3.5, E[5])
    c.ring(c.cx, (c.cy + BODY), r1 * 0.7, r1 * 0.7, 1.6, E[1])
    c.ball(c.cx, (c.cy + BODY), r1 * 0.22, [E[1], E[2], E[3], E[4], E[5]])
    r = rng(seed)
    for k in range(10):
        a = 2 * math.pi * k / 10 + r.uniform(-.2, .2)
        d = r1 * r.uniform(0.75, 0.98)
        c.dot(c.cx + d * math.cos(a), (c.cy + BODY) + d * math.sin(a), 1.6, F[2] if (sparks_fire and k % 2) else E[0])
    out.append((c.done(), 50))
    c = Can(W1, H1)
    c.ring(c.cx, (c.cy + BODY), r1 * 0.92, r1 * 0.92, 2.2, E[5])
    for k in range(8):
        a = 2 * math.pi * k / 8 + r.uniform(-.3, .3)
        d = r1 * r.uniform(0.9, 1.0)
        c.dot(c.cx + d * math.cos(a), (c.cy + BODY) + d * math.sin(a), 1.1, F[3] if (sparks_fire and k % 2) else E[2])
    out.append((c.done(), 60))
    c = Can(W1, H1)
    c.ring(c.cx, (c.cy + BODY), r1, r1, 1.0, E[6])
    out.append((c.done(), 60))
    return out


# ===================== 冲撞：起步的尘土、咬中 =====================

def dash_frames():
    """冲撞起步：脚下一圈尘土往外翻（画在人下面，不跟着转方向，所以是一圈），中间几道海克斯青的速度线，带火星。"""
    out = []
    W1, H1 = 55, 43
    for k, (spread, rr, sparks) in enumerate([(9, 8, 4), (16, 10, 8), (22, 11, 8), (26, 9, 4)]):
        c = Can(W1, H1)
        r = rng(30 + k)
        # 尘土要浅：不用最暗的两档
        ramp = [S[0], S[0], S[1], S[2]] if k < 3 else [S[0], S[1], S[1], S[2]]
        for i in range(6):
            a = 2 * math.pi * i / 6 + k * 0.25 + 0.3
            x = c.cx + spread * 1.6 * math.cos(a)
            y = c.cy + FEET + spread * 0.5 * math.sin(a)
            c.cloud(x, y - rr * 0.3, rr, seed=60 + 7 * k + i, n=3, ramp=ramp, flat=0.7)
        if k < 3:
            for i in range(3):
                yy = c.cy + FEET - 6 - 5 * i
                ln = (10 + 6 * k) * (1.0 - 0.2 * i)
                c.put((np.abs(c.y - yy) <= 0.9) & (np.abs(c.x - c.cx - (i - 1) * 4) <= ln), E[2] if i == 1 else E[4])
        for _ in range(sparks):
            c.dot(c.cx + r.uniform(-spread * 1.7, spread * 1.7), c.cy + FEET + r.uniform(-spread * 1.0, spread * 0.3),
                  1.2, [F[1], F[2], E[1]][r.integers(0, 3)])
        out.append((c.done(), [50, 60, 80, 110][k]))
    return out


def bite_frames(old):
    """咬中：原来的咬合的牙（old 的三帧）放在上面，后面一团白橙冲击、一圈冲击环、火星；最后一帧只剩环和余烬。"""
    out = []
    W1, H1 = 45, 61
    for i, (ball, ms) in enumerate([(9, 40), (15, 50), (0, 70)]):
        c = Can(W1, H1)
        if i == 2:
            c.ring(c.cx, (c.cy + BODY), 26, 26, 3.5, F[4])
            c.ring(c.cx, (c.cy + BODY), 24, 24, 1.5, F[1])
            r = rng(41)
            for k in range(10):
                a = 2 * math.pi * k / 10 + r.uniform(-.2, .2)
                d = r.uniform(22, 30)
                c.dot(c.cx + d * math.cos(a), (c.cy + BODY) + d * math.sin(a), 1.6, [F[0], F[2], F[3]][k % 3])
        else:
            c.rays(c.cx, (c.cy + BODY), 8, 4, 18 + 10 * i, 2.4, [F[0], F[1], F[2], F[3]], rot=0.4 * i)
            c.ball(c.cx, (c.cy + BODY), ball, [F[0], F[0], F[1], F[2], F[3]] if i == 0 else F)
        f = c.done()
        j = old[i][0]
        jh, jw = j.shape[:2]
        y0, x0 = (f.shape[0] - jh) // 2, (f.shape[1] - jw) // 2
        m = j[..., 3] > 0
        f[y0:y0 + jh, x0:x0 + jw][m] = j[m]
        out.append((f, ms))
    c = Can(W1, H1)
    c.ring(c.cx, (c.cy + BODY), 32, 32, 1.5, F[5])
    r = rng(42)
    for k in range(8):
        a = 2 * math.pi * k / 8 + r.uniform(-.3, .3)
        c.dot(c.cx + 30 * math.cos(a), (c.cy + BODY) + 30 * math.sin(a), 1.1, [F[3], F[4]][k % 2])
    out.append((c.done(), 90))
    return out


# ===================== 写进两张特效图 =====================

def build():
    """-> ({fx 的新动作}, {big 的新动作})，每个动作 1x 和 hd_ 各一份。别的动作不在这里，写图时原样留着。"""
    fx = PH.read_sheet(FX)
    big = PH.read_sheet(BIG)
    new_fx = {
        "a_bullet": bullet_frames(),
        "a_hit": hit_frames(),
        "a_crit": burst_frames(37, 36, 51, True),
        "r_hit": burst_frames(29, 28, 52, False),
        "e_dash": dash_frames(),
        "e_hit": bite_frames(fx["hd_e_hit"]),
    }
    new_big = {
        "q_fall": q_fall(big["hd_q_fall"]),
        "r_beam": beam(),
        "r_shield": shield_frames(),
    }
    out = []
    for sheet, new in ((fx, new_fx), (big, new_big)):
        for tag, hd in new.items():
            sheet["hd_" + tag] = hd
            # 掉下来的导弹那三帧原来就有 1x，照旧用原来的（缩出来的和原来的一样大，但颜色是原图挑的）
            if tag == "q_fall":
                sheet[tag] = list(sheet[tag][:3]) + down(hd[3:])
            else:
                sheet[tag] = down(hd)
        out.append(sheet)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    fx, big = build()
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        for name, sheet in (("fx", fx), ("big", big)):
            for tag, frames in sheet.items():
                if tag.startswith("hd_"):
                    show(frames, os.path.join(a.preview, f"{name}_{tag}.png"))
        return
    G.write_sheet(FX, fx, share=True)
    G.write_sheet(BIG, big, share=True)
    print("wrote", {os.path.basename(FX): len(fx), os.path.basename(BIG): len(big)})


if __name__ == "__main__":
    main()
