#!/usr/bin/env python3
"""边境巡团（border）Codex 交的图收成游戏自带那种像素画风：身体只改颜色，形状、透明度一格不动。

    python -I tools/art/border_fix.py --from <交付解压的文件夹>   # 第一次：交付里的运行时文件原样拷进 assets/source/border/runtime
    python tools/art/border_fix.py                               # 读 runtime/，写 assets/source/border/snapped
    python tools/art/border_fix.py --check                       # 重算一遍和 snapped/ 比，不一样退出 1
    python tools/art/border_fix.py --review <文件夹>              # 另出每人一张前后对比图（1 倍、2 倍）
    （顺带把技能图标拷进 border/icons；选人立绘：python -I tools/art/bp_illustrations.py assets/source/border/runtime/banpick_illustrations --write）
    然后 tools/art/import_<英雄>.py、ppu_hd.py --hero <英雄>、hero_reels.py --hero <英雄>

Codex 2026-11-22 交的（v0.4.0 六个人，v0.5.0 又加六个、前六个的图一个字节没变：Border_Patrol_Mirror_Sea_Anime_Assets_v0.5.0.zip，
交接说明 assets/source/border/CLAUDE_HANDOFF.md）：十二个人，一格 256，脚底 (128, 184)，
站高 100-110 格，8 个动作（跑步 8 帧，其余 4 帧），朝右；特效一格 128，中心 (64, 68)。原画是缩小的厚涂，一帧三四千种颜色，
满是杂色点，没有成形的描边。用户要的是「利用PPU能把模型变成游戏那种自带的像素风格但是还能保持高清」：密度不变（PPU 3.3），
看着要像原版的像素画——平涂、三四档硬明暗、一格的描边、没有杂点。

身体（每人 8 个动作共用一套调色板，不超过 64 色）：
- 颜色在 OKLab 里算，色度乘 CW（色相差算得比明暗差重：皮肤和米色布分得开，同一种材质的几档明暗合得狠）；
- 先在人物里面做一遍保边的平均（邻近颜色差不到 TAU 的才平均，线条、眼睛、高光不糊）；
- 调色板：k-means 取主色，再把饱和、离主色远的小色块单独聚类、固定下来（点缀色：岑垒盾上的青色宝石、盐汐的紫眼睛，
  只用中位切分会变灰），然后把太近的两档合成一档（D_MIN），明暗就成了一档一档的；
- 清杂点：同一档颜色连成的块不到 SPECK 格、或者八邻里没有同色的，并进周围最多的那档（只并相近的颜色，眼睛、
  深色线条这类反差大的细节不动，点缀色不动）；只连着一两个同色、周围五个以上是另一档相近颜色的锯齿也并过去；
- 描边：最外一圈换成「同色系最暗那档再压暗」的颜色（色系按往里 1-3 格不是原画深线条的像素挑；描边最亮只到 L 0.42，
  不是一圈近黑的线）；紧贴描边里面那圈原画自带的深线（一两格粗）换成往里不深的颜色，描边只有一格。
特效：每个标签不超过 32 色（同样的取色，点缀色固定），透明度照交的原样。

Codex 的原样在 runtime/，只读；音频、design/ 没拷进来。
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.hierarchy import fcluster, linkage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(ROOT, "assets", "source", "border")
RUNTIME = os.path.join(BASE, "runtime")
OUT = os.path.join(BASE, "snapped")
HEROES = ("cenlei", "xiaolun", "dengmi", "zhumo", "fusuo", "yanxi", "yindu", "lanti", "luxin", "jiyan", "zhongli", "wuling")
# 交付里拷进来的：运行时的图（不要音频）和 docs/border_patrol 的交接说明、json
COPY_DIRS = ("champions", "effects", "icons", "banpick_illustrations", "portraits")
# 技能图标：Codex 的 96x96 RGB 原样拷进 border/icons（游戏和 lint 只认 asset/border/icons/<id>_<槽> 这张 PNG，不挑尺寸；
# 终末包也是原样用 Codex 的 256x256 RGB）；被动的图标留在 runtime/icons
ICONS = os.path.join(ROOT, "border", "icons")
ICON_SLOTS = ("skill", "skill2", "ult")

# 身体的参数（2026-11-22 照岑垒、盐汐、伏梭对比着试出来的：杂点比例 0.13-0.19，和用户认可的泽丽、阿狸、亚索的高清帧
# 0.08-0.18 一样干净；眼睛、宝石、腰带扣都在）
STYLE = dict(cw=3.0, tau=0.10, radius=2, passes=2, n_main=48, d_min=0.085, acc_C=0.07, acc_d=0.08, acc_min=24,
             diam=0.06, out_k=0.62, out_top=0.42, out_floor=0.12, merge_dE=0.13, clean_passes=6, speck=4,
             jag_own=2, jag_maj=5, line_L=0.22, colours=64)
FX_COLOURS = 32
SEED = 0

CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
SQ = np.ones((3, 3), bool)
NB8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


# ---------------------------------------------------------------- OKLab
M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
               [0.2119034982, 0.6806995451, 0.1073969566],
               [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
               [1.9779984951, -2.4285922050, 0.4505937099],
               [0.0259040371, 0.7827717662, -0.8086757660]])
M1I, M2I = np.linalg.inv(M1), np.linalg.inv(M2)


def to_lab(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return np.cbrt(lin @ M1.T) @ M2.T


def to_rgb(lab):
    lin = np.clip(((np.asarray(lab, np.float64) @ M2I.T) ** 3) @ M1I.T, 0, 1)
    c = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    return np.clip(np.round(c * 255), 0, 255).astype(np.uint8)


def shift(a, dy, dx, fill):
    """out[y, x] = a[y + dy, x + dx]，出界的填 fill。"""
    H, W = a.shape[:2]
    out = np.full_like(a, fill)
    ys0, ys1 = max(0, -dy), min(H, H - dy)
    xs0, xs1 = max(0, -dx), min(W, W - dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
    return out


def sigma_smooth(x, op, tau, passes, radius):
    """保边平均：每格和周围 radius 以内颜色差不到 tau 的一起平均，只在人物里面（x 是工作空间的颜色）。"""
    offs = [(dy, dx) for dy in range(-radius, radius + 1) for dx in range(-radius, radius + 1) if dy or dx]
    x = x.copy()
    for _ in range(passes):
        acc = x * op[..., None]
        n = op.astype(np.float64)
        for dy, dx in offs:
            nx_, no = shift(x, dy, dx, 0.0), shift(op, dy, dx, False)
            close = no & op & (np.sqrt(((nx_ - x) ** 2).sum(-1)) < tau)
            acc += nx_ * close[..., None]
            n = n + close
        x = np.where(op[..., None], acc / np.maximum(n, 1)[..., None], x)
    return x


def kmeans(x, k, w=None, iters=30, seed=SEED, init=None, fixed=0):
    """加权 k-means（k-means++ 起步；前 fixed 个中心不动）。-> (中心, 每点归哪个)。"""
    rng = np.random.default_rng(seed)
    w = np.ones(len(x)) if w is None else np.asarray(w, np.float64)
    k = min(k, len(x))
    if init is None:
        c = [x[rng.choice(len(x), p=w / w.sum())]]
        d = ((x - c[0]) ** 2).sum(-1)
        for _ in range(1, k):
            p = d * w
            if p.sum() <= 0:
                break
            c.append(x[rng.choice(len(x), p=p / p.sum())])
            d = np.minimum(d, ((x - c[-1]) ** 2).sum(-1))
        c = np.array(c)
    else:
        c = np.array(init, np.float64)
    for _ in range(iters):
        idx = ((x[:, None] - c[None]) ** 2).sum(-1).argmin(1)
        new = c.copy()
        for j in range(fixed, len(c)):
            m = idx == j
            if m.any():
                new[j] = (x[m] * w[m, None]).sum(0) / w[m].sum()
        if np.allclose(new, c):
            break
        c = new
    return c, ((x[:, None] - c[None]) ** 2).sum(-1).argmin(1)


def merge_close(cent, w, d_min, fixed):
    """距离小于 d_min 的两档合成一档（按像素数加权），点缀色只和点缀色合。"""
    cent, w, fixed = [np.array(c) for c in cent], list(w), list(fixed)
    while len(cent) > 1:
        X, F = np.array(cent), np.array(fixed)
        D = np.sqrt(((X[:, None] - X[None]) ** 2).sum(-1))
        D[np.arange(len(X)), np.arange(len(X))] = np.inf
        D[F[:, None] != F[None]] = np.inf
        i, j = np.unravel_index(np.argmin(D), D.shape)
        if D[i, j] >= d_min:
            break
        cent[i] = (cent[i] * w[i] + cent[j] * w[j]) / (w[i] + w[j])
        w[i] += w[j]
        del cent[j], w[j], fixed[j]
    return np.array(cent), np.array(w), np.array(fixed, bool)


def palette(P, wts, n_main, d_min, acc_C, acc_d, acc_min, cw):
    """工作空间里的像素 P -> (调色板, 是不是点缀色)：k-means 主色 + 固定的点缀色，太近的合并。"""
    rng = np.random.default_rng(SEED)
    pick = rng.choice(len(P), min(len(P), 50000), replace=False, p=wts / wts.sum())
    S = P[pick]
    cent, _ = kmeans(S, n_main)
    d = np.sqrt(((P[:, None] - cent[None]) ** 2).sum(-1)).min(1)
    chroma = np.hypot(P[:, 1], P[:, 2]) / cw
    A = P[(chroma >= acc_C) & (d >= acc_d)]
    accents = []
    if len(A) >= acc_min:
        for k in range(1, 9):
            ac, ai = kmeans(A, k)
            spread = max((np.sqrt(((A[ai == j] - ac[j]) ** 2).sum(-1)).mean() if (ai == j).any() else 0.0)
                         for j in range(len(ac)))
            if spread < 0.05 or k == 8 or k >= len(A) // acc_min:
                break
        accents = [ac[j] for j in range(len(ac)) if (ai == j).sum() >= acc_min]
    init = np.array(accents + list(cent)) if accents else cent
    cent, idx = kmeans(S, len(init), init=init, fixed=len(accents))
    w = np.bincount(idx, minlength=len(cent)).astype(float) + 1
    return merge_close(cent, w, d_min, [True] * len(accents) + [False] * (len(cent) - len(accents)))


def families(lab, diam, wl=0.25):
    """调色板分色系：(a, b, wl*L) 里全连接聚类，直径不超过 diam（一种材质的几档明暗在一组）。"""
    if len(lab) == 1:
        return np.zeros(1, int)
    x = np.stack([lab[:, 1], lab[:, 2], wl * lab[:, 0]], 1)
    return fcluster(linkage(x, method="complete"), t=diam, criterion="distance") - 1


def nb_counts(idx, op, K, r=1):
    """每格周围 (2r+1)^2-1 格里各个颜色的个数 (H, W, K)。"""
    H, W = idx.shape
    oh = np.zeros((H + 2 * r, W + 2 * r, K), np.int16)
    ys, xs = np.nonzero(op)
    oh[ys + r, xs + r, idx[ys, xs]] = 1
    cnt = np.zeros((H, W, K), np.int16)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy or dx:
                cnt += oh[r + dy:r + dy + H, r + dx:r + dx + W]
    return cnt


def comp_sizes(idx, op):
    """每格所在的同色块（八连通）有几格。"""
    out = np.zeros(idx.shape, np.int32)
    for k in np.unique(idx[op]):
        m = op & (idx == k)
        lab, n = ndimage.label(m, structure=SQ)
        out[m] = np.asarray(ndimage.sum(m, lab, range(1, n + 1)))[lab[m] - 1]
    return out


def clean(idx, op, pal_w, protect, st):
    """清杂点和锯齿：只并进相近的颜色（工作空间里差不到 merge_dE），点缀色不动。"""
    K = len(pal_w)
    dE = np.sqrt(((pal_w[:, None] - pal_w[None]) ** 2).sum(-1))
    idx = idx.copy()
    for _ in range(st["clean_passes"]):
        cnt = nb_counts(idx, op, K)
        own = np.take_along_axis(cnt, idx[..., None], 2)[..., 0]
        other = cnt.copy()
        np.put_along_axis(other, idx[..., None], -1, 2)
        maj, majn = other.argmax(2), other.max(2)
        near = (dE[maj, idx] < st["merge_dE"]) & ~protect[idx]
        speck = op & ((own == 0) | (comp_sizes(idx, op) <= st["speck"])) & (majn >= 3) & near
        jag = op & (own <= st["jag_own"]) & (majn >= st["jag_maj"]) & near
        ch = speck | jag
        if not ch.any():
            break
        idx[ch] = maj[ch]
    return idx


def edge_of(op):
    return op & ~ndimage.binary_erosion(op, structure=CROSS, border_value=0)


def outline(idx, op, lab, fam, otone, line_L):
    """最外一圈换成色系的描边色，紧贴里面那圈原画自带的深线换成往里不深的颜色。"""
    edge = edge_of(op)
    inner = op & ~edge
    famimg = fam[idx]
    L = lab[idx][..., 0]
    chroma = np.hypot(lab[idx][..., 1], lab[idx][..., 2])
    # 原画的深色线条：很暗又几乎没颜色（深色的头发、裤子有颜色，不算）
    plain = inner & ~((L < line_L) & (chroma < 0.04))
    choice = np.full(idx.shape, -1)
    for src, radii in ((plain, (1, 2, 3)), (inner, (1, 2))):
        for r in radii:
            size = 2 * r + 1
            best, bestn = np.full(idx.shape, -1), np.zeros(idx.shape)
            for f in np.unique(fam):
                c = ndimage.uniform_filter((src & (famimg == f)).astype(float), size=size, mode="constant") * size * size
                better = c > bestn + 1e-9
                best[better], bestn[better] = f, c[better]
            todo = edge & (choice < 0) & (bestn > 0.5)
            choice[todo] = best[todo]
    todo = edge & (choice < 0)
    choice[todo] = famimg[todo]
    out = idx.copy()
    ys, xs = np.nonzero(edge)
    out[ys, xs] = [otone[int(f)] for f in choice[ys, xs]]
    ring = inner & ndimage.binary_dilation(edge, structure=CROSS)
    near_out = ndimage.maximum_filter(np.where(edge, lab[out][..., 0], 0), size=3)
    deep = inner & ~ring
    cnt = nb_counts(np.where(deep, idx, 0), deep, len(lab), r=2)
    Lp = lab[:, 0]
    for y, x in zip(*np.nonzero(ring)):
        Lr = Lp[out[y, x]]
        if Lr > near_out[y, x] + 0.10 or Lr > 0.36:
            continue
        c = cnt[y, x].astype(int)
        c[Lp < Lr + 0.12] = 0
        if c.max() >= 3:
            out[y, x] = int(c.argmax())
    return out


def restyle(frames, st=STYLE):
    """一个英雄全部身体帧（RGBA）-> (新帧, 调色板 RGB)。只改颜色：透明度和原来一模一样（断言）。"""
    wv = np.array([1.0, st["cw"], st["cw"]])
    ops = [f[..., 3] > 0 for f in frames]
    # 只算人物所在的那一块（全部帧的并集外扩 4 格），快很多
    union = np.logical_or.reduce(ops)
    ys, xs = np.nonzero(union)
    y0, y1, x0, x1 = max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5
    crops = [f[y0:y1, x0:x1] for f in frames]
    cops = [o[y0:y1, x0:x1] for o in ops]
    sm = [sigma_smooth(to_lab(c[..., :3]) * wv, o, st["tau"], st["passes"], st["radius"]) for c, o in zip(crops, cops)]
    P = np.concatenate([s[o] for s, o in zip(sm, cops)])
    d_min = st["d_min"]
    while True:
        pal_w, _, fixed = palette(P, np.ones(len(P)), st["n_main"], d_min, st["acc_C"], st["acc_d"], st["acc_min"], st["cw"])
        lab = pal_w / wv
        fam = families(lab, st["diam"])
        lab, fam, fixed = list(lab), list(fam), list(fixed)
        otone = {}
        for f in sorted(set(fam)):
            m = [i for i in range(len(fam)) if fam[i] == f]
            dk = min(m, key=lambda i: lab[i][0])
            t = np.array([max(st["out_floor"], min(st["out_top"], st["out_k"] * lab[dk][0])), lab[dk][1], lab[dk][2]])
            d = [np.sqrt((((p - t) * wv) ** 2).sum()) for p in lab]
            if min(d) < 0.03:
                otone[f] = int(np.argmin(d))
            else:
                lab.append(t)
                fam.append(f)
                fixed.append(False)
                otone[f] = len(lab) - 1
        if len(lab) <= st["colours"]:
            break
        d_min += 0.005
    lab, fam, fixed = np.array(lab), np.array(fam), np.array(fixed, bool)
    pal_w, rgb = lab * wv, to_rgb(lab)
    out = []
    for f, c, s, o in zip(frames, crops, sm, cops):
        idx = np.zeros(o.shape, np.int64)
        idx[o] = ((s[o][:, None] - pal_w[None]) ** 2).sum(-1).argmin(1)
        idx = outline(clean(idx, o, pal_w, fixed, st), o, lab, fam, otone, st["line_L"])
        g = f.copy()
        sub = g[y0:y1, x0:x1]
        sub[o, :3] = rgb[idx[o]]
        if not np.array_equal(g[..., 3], f[..., 3]):
            sys.exit("restyle changed a frame's alpha")
        out.append(g)
    return out, rgb


def fx_colours(frames, n=FX_COLOURS, cw=3.0):
    """一组特效帧（RGBA）收到不超过 n 色：按透明度加权取色，饱和的小色块固定；透明度不动。"""
    wv = np.array([1.0, cw, cw])
    ops = [f[..., 3] > 0 for f in frames]
    P = np.concatenate([to_lab(f[o][:, :3]) * wv for f, o in zip(frames, ops)])
    W = np.concatenate([f[o][:, 3].astype(np.float64) / 255 for f, o in zip(frames, ops)])
    uniq = np.unique(np.concatenate([f[o][:, :3] for f, o in zip(frames, ops)]), axis=0)
    if len(uniq) <= n:
        return [f.copy() for f in frames]
    k = n
    while True:
        pal_w, _, _ = palette(P, W + 1e-3, k - 4, 0.02, 0.07, 0.08, 6, cw)
        if len(pal_w) <= n:
            break
        k -= 2
    rgb = to_rgb(pal_w / wv)
    out = []
    for f, o in zip(frames, ops):
        g = f.copy()
        if o.any():
            x = to_lab(f[o][:, :3]) * wv
            g[o, :3] = rgb[((x[:, None] - pal_w[None]) ** 2).sum(-1).argmin(1)]
        out.append(g)
    return out


# ---------------------------------------------------------------- 图和动画表
def read(stem):
    sheet = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        fanim = json.load(f)
    return sheet, fanim


def rects(fanim):
    """[(标签, 第几帧, (x, y, w, h))]，照 .fanim 的顺序。"""
    return [(t, i, tuple(int(fr["data"][k]) for k in "xywh")) for t, a in fanim["anims"].items()
            for i, fr in enumerate(a["frames"])]


def fix_body(stem):
    sheet, fanim = read(stem)
    rs = rects(fanim)
    frames = [sheet[y:y + h, x:x + w] for _, _, (x, y, w, h) in rs]
    new, rgb = restyle(frames)
    out = sheet.copy()
    for (_, _, (x, y, w, h)), g in zip(rs, new):
        out[y:y + h, x:x + w] = g
    if not np.array_equal(out[..., 3], sheet[..., 3]):
        sys.exit(f"{stem}: alpha changed")
    used = np.unique(out[out[..., 3] > 0][:, :3], axis=0)
    if len(used) > STYLE["colours"]:
        sys.exit(f"{stem}: {len(used)} colours")
    return out, fanim, len(used)


def fix_fx(stem):
    sheet, fanim = read(stem)
    out = sheet.copy()
    counts = {}
    for tag, a in fanim["anims"].items():
        rs = [tuple(int(fr["data"][k]) for k in "xywh") for fr in a["frames"]]
        new = fx_colours([sheet[y:y + h, x:x + w] for x, y, w, h in rs])
        for (x, y, w, h), g in zip(rs, new):
            out[y:y + h, x:x + w] = g
        px = np.concatenate([g[g[..., 3] > 0][:, :3] for g in new])
        counts[tag] = len(np.unique(px, axis=0)) if len(px) else 0
        if counts[tag] > FX_COLOURS:
            sys.exit(f"{stem} {tag}: {counts[tag]} colours")
    if not np.array_equal(out[..., 3], sheet[..., 3]):
        sys.exit(f"{stem}: alpha changed")
    return out, fanim, counts


def icon_files(hero):
    """[(Codex 的图标, border/icons 里的)]：技能、技能二、大招三个槽。"""
    return [(os.path.join(RUNTIME, "icons", f"border_{hero}_{s}.png"), os.path.join(ICONS, f"border_{hero}_{s}.png"))
            for s in ICON_SLOTS]


def make_hero(hero):
    """一个英雄：[(snapped 里的路径前缀, sheet, fanim)] 和要打印的话。"""
    hid = f"border_{hero}"
    body, bfan, n = fix_body(os.path.join(RUNTIME, "champions", hid))
    fx, ffan, counts = fix_fx(os.path.join(RUNTIME, "effects", f"{hid}_fx"))
    msg = f"{hid}: body {n} colours; fx " + ", ".join(f"{t} {c}" for t, c in counts.items())
    return [(os.path.join(OUT, hid), body, bfan), (os.path.join(OUT, f"{hid}_fx"), fx, ffan)], msg


def import_delivery(src):
    """交付（解压的文件夹）-> assets/source/border：runtime/ 下的图原样拷，docs/border_patrol 的 json 和交接说明放在上一层。"""
    mods = os.path.join(src, "mods", "border_patrol")
    docs = os.path.join(src, "docs", "border_patrol")
    if not os.path.isdir(mods) or not os.path.isdir(docs):
        sys.exit(f"{src}: no mods/border_patrol or docs/border_patrol")
    n = 0
    for d in COPY_DIRS:
        os.makedirs(os.path.join(RUNTIME, d), exist_ok=True)
        for f in sorted(os.listdir(os.path.join(mods, d))):
            shutil.copyfile(os.path.join(mods, d, f), os.path.join(RUNTIME, d, f))
            n += 1
    for f in sorted(os.listdir(docs)):
        if f.endswith(".json") or f == "CLAUDE_HANDOFF.md":
            shutil.copyfile(os.path.join(docs, f), os.path.join(BASE, f))
            n += 1
    print(f"copied {n} files into {os.path.relpath(BASE, ROOT)}")


def review(hero, out_dir):
    """前后对比：上一行 Codex 的、下一行收过的；左边 1 倍（一格 = 屏幕一个像素），右边 2 倍。"""
    hid = f"border_{hero}"
    a, fan = read(os.path.join(RUNTIME, "champions", hid))
    b, _ = read(os.path.join(OUT, hid))
    pick = [("idle", 0), ("run", 0), ("run", 4), ("attack", 2), ("skill", 2), ("skill2", 2), ("ult", 2), ("hit", 2),
            ("dead", 3)]
    rs = {(t, i): r for t, i, r in rects(fan)}
    bg = np.array([112, 128, 104], np.float64)

    def cells(sheet, which):
        out = []
        for key in which:
            x, y, w, h = rs[key]
            out.append(sheet[y:y + h, x:x + w])
        return out

    def strip(frames, z):
        m = np.logical_or.reduce([f[..., 3] > 0 for f in frames])
        ys, xs = np.nonzero(m)
        y0, y1 = ys.min() - 3, ys.max() + 4
        row = []
        for f in frames:
            mm = f[..., 3] > 0
            fx_ = np.nonzero(mm.any(0))[0]
            c = f[y0:y1, max(0, fx_.min() - 3):fx_.max() + 4]
            al = c[..., 3:4] / 255.0
            c = (c[..., :3] * al + bg * (1 - al)).round().astype(np.uint8)
            row.append(np.repeat(np.repeat(c, z, 0), z, 1))
            row.append(np.tile(bg.astype(np.uint8), (row[-1].shape[0], 6 * z, 1)))
        return np.concatenate(row[:-1], 1)

    def rows(z, which):
        top, bot = strip(cells(a, which), z), strip(cells(b, which), z)
        W = max(top.shape[1], bot.shape[1])
        pad = lambda r: np.concatenate([r, np.tile(bg.astype(np.uint8), (r.shape[0], W - r.shape[1], 1))], 1)
        return np.concatenate([pad(top), np.tile(bg.astype(np.uint8), (8, W, 1)), pad(bot)], 0)

    one, two = rows(1, pick), rows(2, pick[:4])
    H = max(one.shape[0], two.shape[0])
    pad_h = lambda r: np.concatenate([r, np.tile(bg.astype(np.uint8), (H - r.shape[0], r.shape[1], 1))], 0)
    img = np.concatenate([pad_h(one), np.tile(bg.astype(np.uint8), (H, 24, 1)), pad_h(two)], 1)
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, f"restyle_{hero}.png")
    Image.fromarray(img).save(p)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="src", help="交付解压的文件夹：先把运行时文件拷进 assets/source/border")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--hero", action="append", help="只做这几个（默认六个）")
    ap.add_argument("--review", help="另出前后对比图到这个文件夹")
    a = ap.parse_args()
    if a.src:
        import_delivery(a.src)
    heroes = a.hero or list(HEROES)
    bad = 0
    for hero in heroes:
        outs, msg = make_hero(hero)
        print(msg)
        for stem, sheet, fanim in outs:
            if a.check:
                p = stem + "#sheet.png"
                old = np.asarray(Image.open(p).convert("RGBA")) if os.path.isfile(p) else None
                if old is None or old.shape != sheet.shape or not np.array_equal(old, sheet):
                    print(f"{os.path.relpath(p, ROOT)} DIFFERS - run tools/art/border_fix.py")
                    bad += 1
                continue
            os.makedirs(os.path.dirname(stem), exist_ok=True)
            Image.fromarray(sheet).save(stem + "#sheet.png")
            with open(stem + "#anim.fanim", "w", encoding="utf-8") as f:
                json.dump(fanim, f, ensure_ascii=False)
        for src, dst in icon_files(hero):
            with open(src, "rb") as f:
                raw = f.read()
            if a.check:
                if not os.path.isfile(dst) or open(dst, "rb").read() != raw:
                    print(f"{os.path.relpath(dst, ROOT)} DIFFERS - run tools/art/border_fix.py")
                    bad += 1
                continue
            os.makedirs(ICONS, exist_ok=True)
            with open(dst, "wb") as f:
                f.write(raw)
        if a.review and not a.check:
            print("  review", review(hero, a.review))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
