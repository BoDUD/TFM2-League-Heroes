#!/usr/bin/env python3
"""边境巡团（border 包）六个人的 tools/art/import_<英雄>.py 共用的设定和特效小工具；引擎是 tools/art/ragnarok_art.py。

    python tools/art/border_fix.py                   # 先收色（snapped/，Codex 的原样在 runtime/）
    python tools/art/import_<英雄>.py [--check]       # cenlei xiaolun dengmi zhumo fusuo yanxi
    python tools/art/ppu_hd.py --hero <英雄>          # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero <英雄>      # 最后出待机和选人动图（顺序不能换）

Codex 的格子：身体一格 256，脚底 (128, 184)，人站高 100-110 格；PPU 3.3（33 个游戏像素上下，和终末包、原版一样高）。
特效一格 128，Codex 把每张画的中心放在 (64, 68)，和身体一样密（FX_PPU 也是 3.3）。

放在单位身上的特效（TARGET_FX），画面帧的中心落在单位的位置上，也就是脚底往上 11.5 个游戏像素（= 38 格）。所以：
- 打中的火花（CONTACT）：Codex 的中心 (64, 68) 就是帧的中心；
- 身上的（BODY）：画的中心要在身子中间（脚底往上 16.5 个游戏像素），帧的中心比画的中心低 5 个游戏像素 = 16 格：(64, 84)；
- 地上的（ground(y)）：画里贴地的那一点（圈的中心、脚印的中间）在第 y 行，帧的中心比它高 38 格：(64, y - 38)。
弹道的图（PROJ_FX）1 倍、朝右，引擎按飞的方向转；画进身体帧的（BAKE）跟着他左右翻。

Codex 的特效边上是半透明的：画进身体帧时按透明度叠（BLEND），缩成 1 倍时每格的透明度按格子里的平均算（scale_fx_alpha），
不像 pixel_down.scale_fx 那样一律变成不透明的方块。
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "border", "snapped")
MOD = os.path.join(ROOT, "border")
PPU = 3.3                   # 和 tools/art/ppu_hd.py 的 PPU、addons/border/src/hd.rs 的 HEROES 一致
SOLE = (128, 184)
FX_CENTRE = (64, 68)        # Codex 特效格的中心
LIFT = round(A.FEET * PPU)  # 38：单位的位置在脚底往上 11.5 个游戏像素
CONTACT = FX_CENTRE
BODY = (64, 68 + 16)
# 合成用的画布（宽、高、脚底点）：最宽的出招（盾往前推、晶浪）往前伸 150 格以内
CANVAS = (448, 288, (224, 232))
ACTS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")


def ground(y, x=64):
    """地上的特效：画里贴地的那点在 (x, y)，帧的中心在它上面 38 格。"""
    return (x, y - LIFT)


def at(x, y):
    """Codex 身体格里的坐标 -> 离脚底点的偏移。"""
    return (x - SOLE[0], y - SOLE[1])


def config(hero, **kw):
    """一个英雄给 ragnarok_art 的设定：border/ 包、Codex 的图名、半透明的特效。"""
    hid = f"border_{hero}"
    cfg = {"SRC": SRC, "ID": hid, "HERO": hero, "PPU": PPU, "SOLE": SOLE, "MOD": MOD, "BODY_STEM": hid,
           "FX_STEM": f"{hid}_fx", "BLEND": True, "SCALE_FX": scale_fx_alpha, "PROJ_IDLE": True, "RETIME": {},
           "CANVAS": CANVAS, "BAKE": [], "TARGET_FX": {}}
    cfg.update(kw)
    return cfg


def scale_fx_alpha(a, k, pivot, least=20):
    """半透明的特效缩到 k 倍（k < 1），格子网过 pivot（和 pixel_down.scale_fx 一样的格子）：每格的透明度 = 格子里各像素
    透明度的平均（空的算 0），颜色 = 按透明度加权的平均，再归到这帧自己用的颜色里最近的那个（不添新颜色）；平均透明度
    不到 least 的格子空着。-> (图, 新的 pivot)。"""
    H, W = a.shape[:2]
    c = 1.0 / k
    px, py = pivot
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))
    nx1, ny1 = int(np.ceil((W - px) / c)), int(np.ceil((H - py) / c))
    Wn, Hn = nx0 + nx1, ny0 + ny1
    n = Hn * Wn
    cx = np.floor((np.arange(W) + 0.5 - px) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - py) / c).astype(int) + ny0
    cell = (cy[:, None] * Wn + cx[None, :]).ravel()
    tot = np.bincount(cell, minlength=n).astype(np.float64)
    al = a[..., 3].ravel().astype(np.float64)
    asum = np.bincount(cell, weights=al, minlength=n)
    alpha = asum / np.maximum(tot, 1)
    rgb = np.stack([np.bincount(cell, weights=a[..., i].ravel() * al, minlength=n) for i in range(3)], 1)
    rgb /= np.maximum(asum, 1e-9)[:, None]
    out = np.zeros((n, 4), np.uint8)
    keep = alpha >= least
    own = np.unique(a[a[..., 3] > 0][:, :3], axis=0).astype(np.float64)
    if keep.any() and len(own):
        d = ((rgb[keep][:, None] - own[None]) ** 2).sum(-1)
        out[keep, :3] = own[d.argmin(1)].astype(np.uint8)
        out[keep, 3] = np.clip(np.round(alpha[keep]), 1, 255).astype(np.uint8)
    return out.reshape(Hn, Wn, 4), (nx0, ny0)


# ---------------------------------------------------------------- 从交来的特效另做几组（FX_MAKE 用）
def frames(fx, tag, idx=None, secs=None):
    """fx 里 tag 的第 idx 几帧（不给就全部），secs 给了就换成这些时长（一个数 = 每帧一样）。"""
    fr = fx[tag] if idx is None else [fx[tag][i] for i in idx]
    if secs is None:
        return list(fr)
    secs = [secs] * len(fr) if np.isscalar(secs) else secs
    return [(a, float(s)) for (a, _), s in zip(fr, secs)]


def settle(fr, rows, to, pad=32):
    """每帧上下挪，让贴地的那一行（rows，每帧量出来的一个数）都落在第 to 行：Codex 有几张地上的特效是绕着格子中间放大的，
    贴地的线（圈心、底边）一帧一帧往下走，一个中心放下去会在地上跳；对齐以后才贴得住地。上下各补 pad 行（帧变高了，
    中心要用返回的那一行算）。-> (帧, 对齐以后贴地的那一行)。"""
    out = []
    for (a, s), r in zip(fr, rows):
        dy = to - r
        if abs(dy) > pad:
            sys.exit(f"settle: 挪 {dy} 行，超过了补的 {pad} 行")
        H, W = a.shape[:2]
        b = np.zeros((H + 2 * pad, W, 4), np.uint8)
        b[pad + dy:pad + dy + H] = a
        out.append((b, s))
    return out, to + pad


def flip_lr(fr):
    return [(np.ascontiguousarray(a[:, ::-1]), s) for a, s in fr]


def flip_tb(fr):
    return [(np.ascontiguousarray(a[::-1]), s) for a, s in fr]


def axis_of(a):
    """一张图里画的东西的主方向（按透明度加权的主成分）：(中心 x, 中心 y, 方向单位向量，x 朝右)。"""
    ys, xs = np.nonzero(a[..., 3] > 0)
    w = a[ys, xs, 3].astype(np.float64)
    mx, my = (xs * w).sum() / w.sum(), (ys * w).sum() / w.sum()
    cov = np.cov(np.stack([xs - mx, ys - my]), aweights=w)
    val, vec = np.linalg.eigh(cov)
    d = vec[:, np.argmax(val)]
    if d[0] < 0:
        d = -d
    return mx, my, d


def turn_flat(fr, centre, d, size):
    """每帧转到 d 方向躺平、朝右（最近邻取样，不加新颜色、不糊）：输出 size x size，centre 落在输出的正中。
    -> (帧, 新的中心)。"""
    cx, cy = centre
    dx, dy = d
    C = (size - 1) / 2.0
    v, u = np.mgrid[0:size, 0:size].astype(np.float64)
    u -= C
    v -= C
    # 输出的 x 轴是 d，往下是 d 顺时针转 90 度
    sx = np.round(cx + u * dx - v * dy).astype(int)
    sy = np.round(cy + u * dy + v * dx).astype(int)
    out = []
    for a, s in fr:
        H, W = a.shape[:2]
        ok = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H)
        b = np.zeros((size, size, 4), np.uint8)
        b[ok] = a[sy[ok], sx[ok]]
        out.append((b, s))
    return out, (C, C)


def extend_ends(fr, centre, want, h=1):
    """一条横躺的细线（风线）从两头往外接到 want 格：只往外添，画里原有的一个像素都不挪（纸鸢、叶子、光雾都不切开）；接的是
    这帧线中间那半段的「典型横截面」（中线上下 h 行，每行取有线的那些列的中位数），粗细、颜色和线一样。几帧加一样长
    （按几帧的并集算），每帧从自己的线头往外接。-> (帧, 新的中心)。"""
    cx, cy = centre
    yc = int(round(cy))
    rows = slice(max(0, yc - h), yc + h + 1)
    union = np.logical_or.reduce([a[..., 3] > 0 for a, _ in fr])
    xs = np.nonzero(union[rows].any(0))[0]
    G = max(0, int(round((want - (xs.max() - xs.min() + 1)) / 2)))
    out = []
    for a, s in fr:
        H, W = a.shape[:2]
        b = np.zeros((H, W + 2 * G, 4), np.uint8)
        b[:, G:G + W] = a
        on = a[rows, :, 3] > 0
        cols = np.nonzero(on.any(0))[0]
        if len(cols) and G:
            x0, x1 = cols.min(), cols.max()
            mid = cols[(cols >= x0 + (x1 - x0) // 4) & (cols <= x1 - (x1 - x0) // 4)]
            band = a[rows][:, mid]
            prof = np.zeros((band.shape[0], 4), np.uint8)
            for r in range(band.shape[0]):
                got = band[r][band[r, :, 3] > 0]
                if len(got):
                    prof[r] = np.median(got, 0).round().astype(np.uint8)
            # 从线还实的地方接起（线头那几列淡下去了，从那里接才连得上）
            solid = np.nonzero(a[rows, :, 3].max(0) >= 0.5 * prof[:, 3].max())[0]
            s0, s1 = (solid.min(), solid.max()) if len(solid) else (x0, x1)
            seg = b[rows]
            for x in list(range(G + x0 - G, G + s0)) + list(range(G + s1 + 1, G + x1 + 1 + G)):
                weak = seg[:, x, 3] < prof[:, 3]
                seg[weak, x] = prof[weak]
            b[rows] = seg
        out.append((b, s))
    return out, (cx + G, cy)


def stretch_mid(fr, centre, want, xl, xr):
    """星束这种两头有东西（星盘、星光）、中间是一条干净的束的：两头原样，中间 [xl, xr) 那段按最近邻拉长（束本身横着是
    匀的，拉长看不出来；不糊、不添颜色），整条到 want 格。几帧用同样的切口，叠起来对得上。-> (帧, 新的中心)。"""
    cx, cy = centre
    union = np.logical_or.reduce([a[..., 3] > 0 for a, _ in fr])
    xs = np.nonzero(union.any(0))[0]
    extra = max(0, int(round(want - (xs.max() - xs.min() + 1))))
    n = xr - xl
    src = xl + (np.arange(n + extra) * n // (n + extra))
    out = []
    for a, s in fr:
        H, W = a.shape[:2]
        b = np.zeros((H, W + extra, 4), np.uint8)
        b[:, :xl] = a[:, :xl]
        b[:, xl:xr + extra] = a[:, src]
        b[:, xr + extra:] = a[:, xr:]
        out.append((b, s))
    return out, (cx + extra / 2, cy)


def lengthen(fr, centre, want, q=0.22, period=1, each=False):
    """横躺的一条（斩线、盐带）加长到 want 格：在两头 q 处切开，左右两段各往外挪，空出来的地方用切口里面 period 列的
    「贴着中线的那一段」反复填（period 1 = 就用切口那一列，接出来粗细一样、不起条纹；盐带用几列一轮，晶体接着排）；
    每列只取连着中线的那段，旁边飞的碎片、火星不复制，中间的亮芯和碎片原样。
    each=False：几帧用同样的切口、加一样长（Codex 画的由短到长保留）；each=True：每帧各自加到 want（斩线的预警细线
    也要整条那么长），左边补空让几帧的中心对齐。-> (帧, 新的中心)。"""
    cx, cy = centre
    yc = int(round(cy))

    def extent(m):
        xs = np.nonzero(m[max(0, yc - 2):yc + 3].any(0))[0]
        return xs.min(), xs.max()

    union = np.logical_or.reduce([a[..., 3] > 0 for a, _ in fr])
    plan = []
    for a, _ in fr:
        x0, x1 = extent(a[..., 3] > 0 if each else union)
        have = x1 - x0 + 1
        plan.append((max(0, int(round((want - have) / 2))), int(round(x0 + q * have)), int(round(x1 - q * have))))
    G = max(g for g, _, _ in plan)
    out = []
    for (a, s), (grow, xl, xr) in zip(fr, plan):
        H, W = a.shape[:2]
        off = G - grow
        b = np.zeros((H, W + 2 * G, 4), np.uint8)
        b[:, off:off + xl] = a[:, :xl]
        b[:, off + xl + grow:off + xr + 1 + grow] = a[:, xl:xr + 1]
        b[:, off + xr + 1 + 2 * grow:off + W + 2 * grow] = a[:, xr + 1:]

        def core(col):
            """一列里连着中线（或离中线最近）的那段的行。"""
            on = a[:, col, 3] > 0
            if not on.any():
                return []
            ys = np.nonzero(on)[0]
            y = ys[np.argmin(np.abs(ys - yc))]
            if abs(y - yc) > 6:
                return []
            lo = hi = y
            while lo - 1 >= 0 and on[lo - 1]:
                lo -= 1
            while hi + 1 < H and on[hi + 1]:
                hi += 1
            return list(range(lo, hi + 1))

        for j in range(grow):
            src = xl + (j % period)
            rows = core(src)
            b[rows, off + xl + j] = a[rows, src]
            src = xr - period + 1 + (j % period)
            rows = core(src)
            b[rows, off + xr + 1 + grow + j] = a[rows, src]
        out.append((b, s))
    return out, (cx + G, cy)
