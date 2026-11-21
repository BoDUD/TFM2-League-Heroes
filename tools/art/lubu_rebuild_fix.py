#!/usr/bin/env python3
"""吕布重画帧的修整：整套 64 帧只用一个头。

    python tools/art/lubu_rebuild_fix.py [--check] [--fit]

Codex 2026-11-21 照动画第一季重画了吕布（assets/source/lubu/rebuild，一格 256，脚底点 (128, 232)）。每帧的头是单独画的：
眼睛、鼻子、嘴、下巴、胡子帧帧不一样，大小也不一样（按跑步第 1 帧量：待机 0.90-0.96 倍，横扫、破阵、天喰 1.05-1.14 倍，
受击 0.84-0.90 倍），跑起来脸在变形（用户：「高清帧后吕布和索尔跑步时都出现脸部模型变形」）。这里照基础游戏画跑步的办法
整套只用一个头：

- 标准头：跑步第 1 帧的头（脸、胡子、耳朵、包着头的那片头发；不含发髻、金箍、翎子、披下来的长发，这些本来就该动）。
  范围是 HEAD（这一帧里描的多边形），金箍那几格不要。
- 摆放（PLACE）：每帧一个整数平移和一个角度。平移是按脸对出来的（--fit 重算：标准头在这帧附近逐格平移，脸那块颜色差
  最小的位置），头是正的帧角度为 0，标准头原样平移过去，和跑步第 1 帧的头逐像素相同；倒地第 3-6 帧头低下去了，用
  同一个头按 RotSprite 的办法转过去（放大八倍转再缩回，像素不糊），相邻几帧低头差不多的用同一个角度，不闪。
  倒地最后两帧脸埋在地上，用它们自己的。
- 旧头比标准头大的帧（横扫、破阵、天喰）：标准头盖不住的旧头要处理掉，不然脸周围多一圈旧脸：
  · 外侧（跑步第 1 帧里头外面是背景的那一圈，6 格宽）：圈里不连到圈外的块（旧发顶、旧脸前面）清掉；眉毛往下、头中心
    往前那一片，旧头范围里的不管连没连着都清掉（旧下巴连着脖子、胸口）；
  · 里侧（跑步第 1 帧那里是头发、脖子）：旧头范围里没被盖住的（旧耳朵、旧下巴），按离头中心往外的方向取第一格旧头外面
    的颜色补上（后脑勺接上长发、下巴底下接上脖子）；嘴往下、耳朵往前取到深色（旧胡子）时再往外找脖子的皮肤；
  · 旧胡子特别长的两帧（天喰第 6、7 帧）旧头范围往下多算几格（BEARD）；
  · 横扫第 1、2、7、8 帧和天喰第 1、8 帧旧胡子尾巴垂到脖子右边，剩下那截像块黑疙瘩：从外往里取周围的颜色补掉（TAIL）。
  旧头范围是标准头的多边形按旧头自己的大小（PLACE 第四个数，按跑步第 1 帧量的倍数）放大。
- 挡在头前面的东西留着：天喰第 3 帧戟杆斜着压在脸前（WEAPON_FRONT：weapon_master 按 checks.csv 的位置画出来，帧里
  确实是戟的像素留在前面）；戟在头后面的帧（横扫第 3、4 帧戟扛在脖子后面），旧头清掉以后露出来的那段戟按 weapon_master
  补上。

最后整张收到 64 色（ragnarok_repixel.snap，中位切分不抖动）：Codex 这版 22 万种颜色，ppu_hd.py 出 lo_（选人、百科）
和 ragnarok_art.py 出 1 倍帧拿每帧最常见的 64 / 96 种颜色当调色板，挑歪了皮肤一块深一块平、普攻那几帧整个人发黄。

读 rebuild/codex/ragnarok_lubu_native（Codex 交来的原样，不改），写 rebuild/ragnarok_lubu_native（import_lubu.py 读它），
#anim.fanim 原样复制。--check 只重算一遍，和仓库里的比，不写文件。
"""
import argparse
import csv
import json
import os
import shutil
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ragnarok_repixel as R  # noqa: E402
from scipy.signal import fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REBUILD = os.path.join(ROOT, "assets", "source", "lubu", "rebuild")
CODEX = os.path.join(REBUILD, "codex", "ragnarok_lubu_native")
OUT = os.path.join(REBUILD, "ragnarok_lubu_native")
WEAPON = os.path.join(REBUILD, "weapon_master.png")
CHECKS = os.path.join(REBUILD, "checks.csv")

HEAD_FROM = ("run", 0)
# 标准头的范围（跑步第 1 帧里的格子坐标）：发顶、额前、脸前、下巴、胡子底、耳朵后面
HEAD = [(141, 115), (147, 112), (153, 112), (157, 115), (160, 118), (161, 123), (161, 130), (160, 135), (158, 139),
        (155, 143), (150, 144), (147, 142), (145, 138), (143, 134), (141, 129), (140, 122)]
C0 = (150.5, 128.5)          # 头的中心（转、按大小放大都绕这一点）
RING = (116, 148)            # 这一行以上、这一列以左是金箍，金色的不算头
# 对脸用的范围（--fit）：额头到胡子，不含头发
FACE = [(147, 118), (157, 116), (161, 121), (161, 131), (158, 138), (154, 143), (148, 142), (145, 136), (144, 126)]
# 每帧 (dx, dy, 角度, 旧头大小)：标准头平移 (dx, dy)、逆时针转的角度（度）；旧头按跑步第 1 帧量的大小（1 以下记 1）。
# None：用这帧自己的头
PLACE = {
    "idle": [(-1, -2, 0, 1.00), (-2, -3, 0, 1.00), (-3, -5, 0, 1.00), (-1, -4, 0, 1.00), (-3, -3, 0, 1.00),
             (-2, -2, 0, 1.00), (-1, -2, 0, 1.00), (1, -1, 0, 1.00)],
    "run": [(0, 0, 0, 1.00), (-1, 1, 0, 1.00), (-3, 0, 0, 1.02), (0, 10, 0, 1.00), (3, 1, 0, 1.02), (3, 3, 0, 1.02),
            (-7, 4, 0, 1.00), (9, 16, 0, 1.02)],
    "attack": [(-4, -2, 0, 1.00), (-5, 5, 0, 1.00), (-3, 6, 0, 1.00), (1, 13, 0, 1.00), (2, 19, 0, 1.02),
               (2, 11, 0, 1.02), (-11, 6, 0, 1.00), (-6, -2, 0, 1.00)],
    "skill": [(-5, 7, 0, 1.14), (-10, 6, 0, 1.05), (-6, 1, 0, 1.08), (2, 4, 0, 1.11), (-12, 16, 0, 1.14),
              (0, 18, 0, 1.14), (-12, 9, 0, 1.08), (-1, 4, 0, 1.14)],
    "skill2": [(-15, 0, 0, 1.08), (-3, 6, 0, 1.08), (1, 13, 0, 1.11), (7, 19, 0, 1.14), (13, 26, 0, 1.08),
               (9, 26, 0, 1.14), (9, 14, 0, 1.11), (-10, 3, 0, 1.14)],
    "ult": [(-18, 3, 0, 1.08), (-10, 5, 0, 1.05), (-11, 2, 0, 1.00), (-15, -6, 0, 1.08), (-13, 8, 0, 1.11),
            (-3, 20, 0, 1.08), (2, 30, 0, 1.11), (-15, 2, 0, 1.11)],
    "hit": [(-8, -4, 0, 1.00), (-12, -3, 0, 1.00), (-17, -1, 0, 1.00), (-19, 4, 0, 1.00), (-12, 5, 0, 1.00),
            (-8, 1, 0, 1.00), (-9, 1, 0, 1.00), (-13, -2, 0, 1.00)],
    "dead": [(-13, -7, 0, 1.00), (-9, 2, 0, 1.00), (-11, 7, -15, 1.00), (-6, 22, -32.5, 1.00), (-9, 47, -32.5, 1.00),
             (-8, 56, -32.5, 1.00), None, None],
}
WEAPON_FRONT = {("ult", 2)}
BEARD = {("ult", 5): 4, ("ult", 6): 9}
# 旧胡子尾巴垂在脖子右边、肩膀上方的帧（标准头的胡子短，剩下那截像一块黑疙瘩）：tail_off() 补掉
TAIL = {("skill", 0), ("skill", 1), ("skill", 6), ("skill", 7), ("ult", 0), ("ult", 7)}
BAND = 6


def read(stem):
    sheet = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA")).copy()
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    rects = {t: [tuple(int(fr["data"][k]) for k in ("x", "y", "w", "h")) for fr in a["frames"]] for t, a in anims.items()}
    return sheet, rects


def poly(shape, pts):
    m = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(pts, fill=1, outline=1)
    return np.asarray(m).astype(bool)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    y0, y1, x0, x1 = max(0, dy), min(H, H + dy), max(0, dx), min(W, W + dx)
    out[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    return out


def gold(a):
    r, g, b = (a[..., k].astype(np.float32) for k in range(3))
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1)
    hue = np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) % 360
    lum = (r * 30 + g * 59 + b * 11) / 100
    return (a[..., 3] > 0) & (hue >= 28) & (hue <= 60) & (sat >= 0.35) & (lum >= 70)


def lum(a):
    return (a[..., 0].astype(int) * 30 + a[..., 1].astype(int) * 59 + a[..., 2].astype(int) * 11) / 100


# ---------------------------------------------------------------- 像素图旋转（RotSprite：Scale2x 放大 8 倍，转，取中心）
def scale2x(a):
    p = np.pad(a, 1, mode="edge")
    B, D, F, H_, E = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 2:], p[2:, 1:-1], a
    out = np.empty((a.shape[0] * 2, a.shape[1] * 2), a.dtype)
    out[0::2, 0::2] = np.where((D == B) & (B != F) & (D != H_), D, E)
    out[0::2, 1::2] = np.where((B == F) & (B != D) & (F != H_), F, E)
    out[1::2, 0::2] = np.where((D == H_) & (D != B) & (H_ != F), D, E)
    out[1::2, 1::2] = np.where((H_ == F) & (D != H_) & (B != F), F, E)
    return out


def rotsprite(rgba, ang, center, masks=()):
    """rgba 绕 center 逆时针转 ang 度（屏幕上看），大小不变；masks 跟着一起转。"""
    H, W = rgba.shape[:2]
    k = rgba.reshape(-1, 4).astype(np.int64)
    key = (k[:, 0] << 24) | (k[:, 1] << 16) | (k[:, 2] << 8) | k[:, 3]
    key[k[:, 3] == 0] = 0
    for j, m in enumerate(masks):
        key = key | (m.reshape(-1).astype(np.int64) << (32 + j))
    uniq, idx = np.unique(key, return_inverse=True)
    a = idx.reshape(H, W)
    for _ in range(3):
        a = scale2x(a)
    c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    yy, xx = np.mgrid[:H, :W].astype(np.float64)
    dx, dy = xx + 0.5 - center[0], yy + 0.5 - center[1]
    ix = np.floor((c * dx - s * dy + center[0]) * 8).astype(int)
    iy = np.floor((s * dx + c * dy + center[1]) * 8).astype(int)
    ok = (ix >= 0) & (iy >= 0) & (ix < W * 8) & (iy < H * 8)
    got = np.zeros((H, W), np.int64)
    got[ok] = uniq[a[iy[ok], ix[ok]]]
    out = np.stack([(got >> 24) & 255, (got >> 16) & 255, (got >> 8) & 255, got & 255], -1).astype(np.uint8)
    return out, [((got >> (32 + j)) & 1).astype(bool) for j in range(len(masks))]


# ---------------------------------------------------------------- 戟：weapon_master 按 checks.csv 画回每帧
W_IMG = None
W_POSE = None
W_REF = (-8.5, 4.3)          # checks.csv 的 (x, y) 是戟上离 weapon_master 中心 (-8.5, +4.3) 的那一点（按戟自己的方向）


def weapon_layer(action, i, shape=(256, 256)):
    global W_IMG, W_POSE
    if W_IMG is None:
        W_IMG = np.asarray(Image.open(WEAPON).convert("RGBA"))
        with open(CHECKS, encoding="utf-8") as f:
            W_POSE = {(r["action"], int(r["frame"]) - 1): [float(v) for v in r["weapon_x_y_degrees"].split("/")]
                      for r in csv.DictReader(f)}
    x, y, deg = W_POSE[(action, i)]
    ang = -deg
    c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    cx = x - (c * W_REF[0] + s * W_REF[1])
    cy = y - (-s * W_REF[0] + c * W_REF[1])
    H, W = shape
    yy, xx = np.mgrid[:H, :W].astype(np.float64)
    dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
    ix = np.floor(c * dx - s * dy + W_IMG.shape[1] / 2).astype(int)
    iy = np.floor(s * dx + c * dy + W_IMG.shape[0] / 2).astype(int)
    ok = (ix >= 0) & (iy >= 0) & (ix < W_IMG.shape[1]) & (iy < W_IMG.shape[0])
    out = np.zeros((H, W, 4), np.uint8)
    out[ok] = W_IMG[iy[ok], ix[ok]]
    return out


def weapon_shown(F, layer, tol=90):
    """帧里确实画着戟的像素：戟在这里，颜色和 3x3 以内画出来的戟对得上。"""
    m = ndimage.binary_dilation(layer[..., 3] > 0, iterations=1)
    best = np.full(F.shape[:2], 1 << 30)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            sh = np.roll(np.roll(layer, dy, 0), dx, 1)
            d = np.abs(F[..., :3].astype(int) - sh[..., :3].astype(int)).sum(-1)
            d[sh[..., 3] == 0] = 1 << 30
            best = np.minimum(best, d)
    return m & (F[..., 3] > 0) & (best < tol)


# ---------------------------------------------------------------- 合成
def own_zone(shape, ang, s, cx, cy, grow):
    """旧头的范围：HEAD 按 s 放大、转 ang 度，中心放在 (cx, cy)。"""
    c, sn = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    pts = []
    for x, y in HEAD:
        dx, dy = (x - C0[0]) * s, (y - C0[1]) * s
        pts.append((cx + c * dx + sn * dy, cy - sn * dx + c * dy))
    m = poly(shape, pts)
    return ndimage.binary_dilation(m, iterations=grow) if grow else m


def radial_fill(F, R, Z, c, skip_dark, reach=10):
    """R 里的每格：从头中心 c 往外，取第一格出了 Z 的颜色；skip_dark 里的格子取到深色时再往外 reach 格以内找亮的。"""
    out = F.copy()
    L = lum(F)
    H, W = F.shape[:2]
    for y, x in zip(*np.nonzero(R)):
        vx, vy = x + 0.5 - c[0], y + 0.5 - c[1]
        n = np.hypot(vx, vy)
        if n < 1e-6:
            continue
        ux, uy = vx / n, vy / n
        got = first = None
        for k in range(1, 80):
            qx, qy = int(np.floor(x + 0.5 + ux * k * 0.5)), int(np.floor(y + 0.5 + uy * k * 0.5))
            if not (0 <= qx < W and 0 <= qy < H):
                break
            if Z[qy, qx]:
                continue
            if first is None:
                first = (qx, qy, k)
            if not skip_dark[y, x] or (F[qy, qx, 3] > 0 and L[qy, qx] >= 90):
                got = F[qy, qx]
                break
            if k - first[2] > reach * 2:
                break
        if got is None:
            got = F[first[1], first[0]] if first is not None else np.zeros(4, np.uint8)
        out[y, x] = got
    return out


class Head:
    def __init__(self, frames):
        a = frames[HEAD_FROM[0]][HEAD_FROM[1]]
        ring = np.zeros(a.shape[:2], bool)
        ring[:RING[0], :RING[1]] = True
        self.full = a
        self.mask = poly(a.shape[:2], HEAD) & (a[..., 3] > 0) & ~(gold(a) & ring)
        self.head = a.copy()
        self.head[~self.mask] = 0

    def placed(self, dx, dy, ang):
        head, mask, full = self.head, self.mask, self.full
        if ang:
            head, (mask,) = rotsprite(self.head, ang, C0, [self.mask])
            mask &= head[..., 3] > 0
            full, _ = rotsprite(self.full, ang, C0)
        return shift(head, dx, dy), shift(mask, dx, dy), shift(full, dx, dy)


def fix_frame(F, action, i, head, place):
    dx, dy, ang, own = place
    P, Pm, full = head.placed(dx, dy, ang)
    cx, cy = C0[0] + dx, C0[1] + dy
    H, W = F.shape[:2]
    yy, xx = np.mgrid[:H, :W]
    Z = own_zone(F.shape[:2], ang, max(1.0, own), cx, cy, 1 if own > 1.0 else 0)
    beard = BEARD.get((action, i), 0)
    if beard:
        down = np.zeros_like(Z)
        for k in range(1, beard + 1):
            down |= shift(Z, 0, k)
        Z |= down & (xx >= cx - 6) & (yy >= cy + 6)
    layer = weapon_layer(action, i)
    front = (action, i) in WEAPON_FRONT
    K = weapon_shown(F, layer) if front else np.zeros(F.shape[:2], bool)
    out = F.copy()
    opq = F[..., 3] > 0
    # 外侧：标准头周围 BAND 格以内、跑步第 1 帧那里是背景的一圈
    near = ndimage.binary_dilation(Pm, iterations=BAND)
    outside = full[..., 3] == 0
    ring = near & ~Pm & outside
    lab, n = ndimage.label(opq & ring, structure=np.ones((3, 3)))
    edge = ndimage.binary_dilation(~near, iterations=1) & near
    reach = set(np.unique(lab[edge & (lab > 0)]).tolist())
    clear = np.isin(lab, [k for k in range(1, n + 1) if k not in reach])
    clear |= opq & ring & ndimage.binary_dilation(Z, iterations=2) & (xx >= cx - 2) & (yy >= cy - 6)
    clear &= ~K
    out[clear] = 0
    # 里侧：旧头范围里没被盖住、跑步第 1 帧那里是头发脖子的；发髻那块（头顶后面）不动
    inner = Z & ~Pm & ~outside & ~K & ~((yy < cy - 10) & (xx < cx + 2))
    if inner.any():
        filled = radial_fill(F, inner, Z & ~Pm, (cx, cy), (yy >= cy + 4) & (xx >= cx - 7))
        out[inner] = filled[inner]
    # 戟在头后面：旧头外侧清掉以后露出来的那段（里侧补的是脖子、头发，本来就在戟前面）
    if not front:
        behind = clear & (layer[..., 3] > 0)
        out[behind] = layer[behind]
    put = Pm & ~K
    out[put] = P[put]
    if (action, i) in TAIL:
        out = tail_off(F, out, Pm, cx, cy)
    return out


def tail_off(F, out, Pm, cx, cy):
    """旧胡子垂到脖子前面的那截（TAIL 的帧）：Codex 原图里和下巴底下那块深色连着的深色，在嘴往下、下巴前面的一块里，
    标准头没盖到、现在还是深色的；轮廓最外一圈不动。从外往里一圈一圈补：每格取周围八格里已经定下来、不深的颜色
    （透明也算）里最多的那个，两个以上邻居才补。"""
    H, W = F.shape[:2]
    yy, xx = np.mgrid[:H, :W]
    dark = (F[..., 3] > 0) & (lum(F) < 75)
    win = (yy >= cy + 8) & (yy <= cy + 26) & (xx >= cx - 3) & (xx <= cx + 11)
    chin = (yy >= cy + 8) & (yy <= cy + 16) & (xx >= cx - 3) & (xx <= cx + 8)
    lab, _ = ndimage.label(dark & win, structure=np.ones((3, 3)))
    ids = [k for k in np.unique(lab[chin & (lab > 0)]).tolist() if k]
    op = out[..., 3] > 0
    edge = op & ~ndimage.binary_erosion(op, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    todo = np.isin(lab, ids) & ~Pm & ~edge & op & (lum(out) < 75)
    res = out.copy()
    for _ in range(40):
        got = {}
        for y, x in zip(*np.nonzero(todo)):
            near = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    y2, x2 = y + dy, x + dx
                    if (dy or dx) and 0 <= y2 < H and 0 <= x2 < W and not todo[y2, x2]:
                        c = res[y2, x2]
                        if c[3] == 0:
                            near.append((0, 0, 0, 0))
                        elif lum(c[None, None])[0, 0] >= 75:
                            near.append(tuple(int(v) for v in c))
            if len(near) >= 2:
                got[(y, x)] = Counter(near).most_common(1)[0][0]
        if not got:
            break
        for (y, x), c in got.items():
            res[y, x] = c
            todo[y, x] = False
    return res


def frames_of(sheet, rects):
    return {t: [sheet[y:y + h, x:x + w].copy() for x, y, w, h in r] for t, r in rects.items()}


def build():
    sheet, rects = read(CODEX)
    frames = frames_of(sheet, rects)
    head = Head(frames)
    out = sheet.copy()
    for action, places in PLACE.items():
        for i, place in enumerate(places):
            if place is None:
                continue
            x, y, w, h = rects[action][i]
            out[y:y + h, x:x + w] = fix_frame(frames[action][i], action, i, head, place)
    # 最后整张收到 64 色（ragnarok_repixel.snap：Codex 这版 22 万种颜色，lo_ 和 1 倍帧挑调色板会挑歪）
    return R.snap(out)


def fit():
    """每帧按脸对出来的平移（PLACE 的角度不变）：标准头的脸那块在 PLACE 位置附近 +-8 格里逐格比，颜色差最小的。"""
    sheet, rects = read(CODEX)
    frames = frames_of(sheet, rects)
    head = Head(frames)
    face = poly(head.mask.shape, FACE) & head.mask

    def feat(a):
        f = a.astype(np.float64).copy()
        f[a[..., 3] == 0, :3] = 0
        f[..., 3] = (a[..., 3] > 0) * 255.0
        return np.stack([ndimage.gaussian_filter(f[..., c], 0.7) for c in range(4)], -1)

    for action, places in PLACE.items():
        got = []
        for i, place in enumerate(places):
            if place is None:
                got.append(None)
                continue
            dx0, dy0, ang, own = place
            src, m = head.head, face
            if ang:
                src, (m,) = rotsprite(head.head, ang, C0, [face])
            ys, xs = np.nonzero(m)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            T, M = feat(src[y0:y1, x0:x1]), ndimage.gaussian_filter(m[y0:y1, x0:x1].astype(np.float64), 0.7)
            Fe = feat(frames[action][i])
            acc = sum(fftconvolve(Fe[..., c] ** 2, M[::-1, ::-1], mode="valid")
                      - 2 * fftconvolve(Fe[..., c], (M * T[..., c])[::-1, ::-1], mode="valid") for c in range(4))
            best = min((acc[y0 + dy, x0 + dx], dx, dy) for dy in range(dy0 - 8, dy0 + 9) for dx in range(dx0 - 8, dx0 + 9)
                       if 0 <= y0 + dy < acc.shape[0] and 0 <= x0 + dx < acc.shape[1])
            got.append((best[1], best[2]))
        print(action, got)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="只比，不写")
    ap.add_argument("--fit", action="store_true", help="打印按脸对出来的平移")
    a = ap.parse_args()
    if a.fit:
        fit()
        return
    out = build()
    if a.check:
        bad = []
        p = OUT + "#sheet.png"
        if not os.path.isfile(p) or not np.array_equal(np.asarray(Image.open(p).convert("RGBA")), out):
            bad.append(p)
        p = OUT + "#anim.fanim"
        if not os.path.isfile(p) or open(p, "rb").read() != open(CODEX + "#anim.fanim", "rb").read():
            bad.append(p)
        for p in bad:
            print(p, "不一样：跑一遍 python tools/art/lubu_rebuild_fix.py")
        sys.exit(1 if bad else 0)
    Image.fromarray(out).save(OUT + "#sheet.png")
    shutil.copyfile(CODEX + "#anim.fanim", OUT + "#anim.fanim")
    print(OUT + "#sheet.png", out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()
