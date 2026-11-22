#!/usr/bin/env python3
"""边境巡团：每人整套只用一个头（待机第 1 帧的），按整数格贴进每一帧。

    python tools/art/border_heads.py [--hero <英雄> ...] [--check] [--review <文件夹>]

读 assets/source/border/snapped/（border_fix.py 收过色的），写 assets/source/border/headed/（import_<英雄>.py 读身体图就读
这里；特效图还在 snapped/）。之后照常 import_<英雄>.py、ppu_hd.py --hero、hero_reels.py --hero。
--check 只重算一遍和 headed/ 比，不写文件；--review 另出每人每个动作一张前后对比图（上：原样，中：贴头后，下：贴好的头对齐排开）。

为什么（用户 2026-11-22）：「这个待机跑步还是看起来不一样 还有上下摆动的时候模型明显看的出变形 你看看女武神怎么做的吧」
「几乎这12个英雄待机时候都会产生模型变形 刚才两个是待机和跑步模型都不一样」。量出来：
- 跑步（v0.6.0 重画）的头十二个人都是另画的：侧脸、头发小一圈、发色也不一样，和待机不像一个人；
- 别的动作是把同一个头按 0.91-1.04 倍、半格的位置重新采样贴的（Codex 的 head_core_measurements.json 里的 head_pose），
  每帧眼睛、眉毛、发丝差一两格，放到高清帧就是脸在变形；
- 待机的呼吸是头整格上下、躯干逐行拉伸，拉伸就是变形：待机改回只停第 1 帧再插动作片段（tools/art/hero_reels.json）。
终末包的办法（tools/art/lubu_rebuild_fix.py 等）：整套只用一个头，按整数格平移贴过去，头歪的帧用 RotSprite 转。

做法：
- 标准头：待机第 1 帧里 CUT 多边形以内的不透明像素（头发、脸、耳朵、发饰，下巴连一点脖子；领口、披风、肩甲不算，
  多边形只有下巴、脖子、领口那条边要准）。
- 摆放：每帧在整个格子里逐格平移找标准头和这帧颜色差最小的位置（跑步以外的动作再试几个角度，转了要明显更像才用，
  上一帧的位置附近也找一遍）；找出来的存在 assets/source/border/head_place.json（--fit 重找），找错的帧在 PLACE 里按帧写死。
- 合成：标准头盖上去；标准头外面一圈（BAND 格）里不连着身体的旧头碎块清掉；FRONT 里的帧，挡在头前面的东西
  （手、盾、武器：颜色不是头上那些颜色、又从头外面伸进来的那一块）留在前面。
- 头底下的脖子：标准头的下巴比原来高、和领口中间漏了空，按标准头最下面那格往下补到碰着身体（NECK 格以内）。
- KEEP 里的帧（躺平的、脸埋在地上的）用它自己的头。
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(ROOT, "assets", "source", "border")
SNAP = os.path.join(BASE, "snapped")
OUT = os.path.join(BASE, "headed")
# 找出来的位置 {英雄: {"动作:帧": [dx, dy, 角度]}}：默认照表贴（快，也看得见每帧贴在哪），--fit 重新找并写回
FITS = os.path.join(BASE, "head_place.json")
HEROES = ("cenlei", "xiaolun", "dengmi", "zhumo", "fusuo", "yanxi", "yindu", "lanti", "luxin", "jiyan", "zhongli", "wuling")
ACTIONS = ("run", "attack", "skill", "skill2", "ult", "hit", "dead")   # 待机只放第 1 帧（hero_reels），不动
CELL = 256
BAND = 6          # 标准头外面这么宽一圈里，不连着身体的旧头碎块清掉
REACH = 24        # 整块在下巴以上、只连着标准头的旧头（旧马尾、旧发髻）：离标准头这么远以内的清掉
NECK = 4          # 下巴底下最多补这么多格脖子
PAD = 96          # 找位置时格子四周垫的透明边
ANGLES = (-45, -37.5, -30, -22.5, -15, -7.5, 7.5, 15, 22.5, 30, 37.5, 45)
DEAD_ANGLES = (-90, -75, -60, 60, 75, 90)
TURN_GAIN = 0.9   # 转过的比不转的颜色差小到这个比例以下才转

# 头和身体的分界：多边形以内、不透明的算头（格子坐标，待机第 1 帧）
CUT = {
    "cenlei": [(90, 60), (165, 60), (165, 101), (146, 101), (141, 103), (138, 104), (130, 104), (128, 103), (126, 101),
               (90, 101)],
    "xiaolun": [(90, 70), (170, 70), (170, 121), (90, 121)],
    "dengmi": [(80, 70), (160, 70), (160, 126), (80, 126)],
    "zhumo": [(90, 60), (165, 60), (165, 108), (144, 108), (141, 111), (128, 111), (126, 106), (120, 104), (90, 104)],
    "fusuo": [(100, 66), (165, 66), (165, 110), (142, 110), (138, 113), (128, 113), (124, 111), (100, 111)],
    "yanxi": [(86, 70), (170, 70), (170, 114), (147, 114), (147, 121), (139, 121), (137, 122), (128, 122), (126, 120),
              (86, 120)],                                    # 右下手里那颗宝珠的顶（x 147 往右）不算
    "yindu": [(96, 60), (176, 60), (176, 112), (150, 112), (147, 118), (129, 118), (127, 114), (124, 111), (118, 110),
              (96, 110)],
    "lanti": [(88, 70), (165, 70), (165, 122), (88, 122)],
    "luxin": [(100, 76), (170, 76), (170, 110), (142, 110), (139, 111), (133, 111), (129, 109), (123, 108), (121, 111),
              (119, 116), (100, 116)],                       # 左下那束黄绿的是发带，兜帽（x 121-131、y 110 往下）不算
    "jiyan": [(100, 66), (148, 66), (148, 104), (142, 104), (139, 108), (131, 108), (128, 106), (100, 106)],
    "zhongli": [(90, 66), (155, 66), (155, 106), (140, 106), (136, 110), (127, 111), (122, 106), (118, 104), (90, 104)],
    "wuling": [(90, 70), (160, 70), (160, 113), (140, 113), (137, 114), (128, 114), (124, 113), (90, 113)],
}
# 按帧写死的位置 {英雄: {(动作, 帧): (dx, dy, 角度)}}，帧从 0 数
PLACE = {}
# 挡在头前面的东西要留在前面的帧 {英雄: {(动作, 帧)}}
FRONT = {
    "cenlei": {("hit", 3)},                                           # 受击缩在盾后
    "yindu": {("ult", i) for i in range(2, 9)} | {("hit", 3)},       # 大招举盾、拳头在下巴前；受击缩在盾后
}
# 旧头比标准头大出一截、又连着身体（清碎块那一圈清不掉）的地方：{英雄: {(动作, 帧 或 None=整个动作): [多边形, ...]}}，
# 多边形按待机第 1 帧的坐标画，跟着这帧的位置平移；多边形里标准头没盖住的格子清掉
ERASE = {}
# 用自己的头的帧 {英雄: {(动作, 帧)}}：倒下去以后头歪了、闭着眼
KEEP = {
    # 最后两帧躺平（脸朝下或侧着贴地、闭眼）
    **{h: {("dead", 6), ("dead", 7)} for h in ("cenlei", "dengmi", "fusuo", "lanti", "jiyan", "wuling")},
    # 第 5 帧起头就垂下去（只看得见头顶）或扑倒在地
    **{h: {("dead", i) for i in range(4, 8)} for h in ("zhumo", "yanxi", "yindu", "luxin", "zhongli")},
}
# 绡轮倒下是趴着抬头看前面，标准头正合适，不留


# ---------------------------------------------------------------- 读写
def read(stem):
    sheet = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA")).copy()
    with open(stem + "#anim.fanim", encoding="utf-8-sig") as f:
        doc = json.load(f)
    anims = doc.get("anims", doc)
    rects = {t: [tuple(int(fr["data"][k]) for k in ("x", "y", "w", "h")) for fr in a["frames"]] for t, a in anims.items()}
    return sheet, rects


def cell(sheet, r):
    x, y, w, h = r
    return sheet[y:y + h, x:x + w].copy()


def poly(pts, shape=(CELL, CELL)):
    m = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(pts, fill=1, outline=1)
    return np.asarray(m).astype(bool)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    y0, y1, x0, x1 = max(0, dy), min(H, H + dy), max(0, dx), min(W, W + dx)
    if y0 < y1 and x0 < x1:
        out[y0:y1, x0:x1] = a[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    return out


def keys(a):
    k = a.reshape(-1, 4).astype(np.int64)
    return ((k[:, 0] << 16) | (k[:, 1] << 8) | k[:, 2]).reshape(a.shape[:2])


# ---------------------------------------------------------------- 像素图旋转（RotSprite：Scale2x 放大 8 倍，转，取回原大小）
def scale2x(a):
    p = np.pad(a, 1, mode="edge")
    B, D, F, H_, E = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 2:], p[2:, 1:-1], a
    out = np.empty((a.shape[0] * 2, a.shape[1] * 2), a.dtype)
    out[0::2, 0::2] = np.where((D == B) & (B != F) & (D != H_), D, E)
    out[0::2, 1::2] = np.where((B == F) & (B != D) & (F != H_), F, E)
    out[1::2, 0::2] = np.where((D == H_) & (D != B) & (H_ != F), D, E)
    out[1::2, 1::2] = np.where((H_ == F) & (D != H_) & (B != F), F, E)
    return out


def rotsprite(rgba, ang, center):
    """rgba 绕 center 逆时针转 ang 度（屏幕上看），大小不变，不出新颜色。"""
    H, W = rgba.shape[:2]
    k = rgba.reshape(-1, 4).astype(np.int64)
    key = (k[:, 0] << 24) | (k[:, 1] << 16) | (k[:, 2] << 8) | k[:, 3]
    key[k[:, 3] == 0] = 0
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
    return np.stack([(got >> 24) & 255, (got >> 16) & 255, (got >> 8) & 255, got & 255], -1).astype(np.uint8)


# ---------------------------------------------------------------- 标准头
class Head:
    def __init__(self, hero, idle0):
        self.mask = poly(CUT[hero]) & (idle0[..., 3] > 0)
        self.rgba = idle0.copy()
        self.rgba[~self.mask] = 0
        ys, xs = np.nonzero(self.mask)
        self.c = ((xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2)
        self.palette = set(np.unique(keys(self.rgba)[self.mask]).tolist())
        self._turned = {0: (self.rgba, self.mask)}

    def turned(self, ang):
        if ang not in self._turned:
            r = rotsprite(self.rgba, ang, self.c)
            self._turned[ang] = (r, r[..., 3] > 0)
        return self._turned[ang]

    def placed(self, dx, dy, ang):
        r, m = self.turned(ang)
        return shift(r, dx, dy), shift(m, dx, dy)


def scores(F, rgba, mask, dxs, dys, sub=False):
    """标准头（rgba, mask）平移 (dx, dy) 以后和 F 的平均颜色差（F 透明的格子按 300 算），dys x dxs 一张表。
    sub：只算棋盘格一半的像素（先粗找，再全算）。"""
    Fp = np.pad(F, ((PAD, PAD), (PAD, PAD), (0, 0)))
    ys, xs = np.nonzero(mask)
    if sub:
        k = (xs + ys) % 2 == 0
        ys, xs = ys[k], xs[k]
    ref = rgba[ys, xs, :3].astype(np.int16)
    out = np.empty((len(dys), len(dxs)))
    dxa = np.asarray(dxs)
    for j, dy in enumerate(dys):
        yy = ys[None, :] + dy + PAD
        xx = xs[None, :] + dxa[:, None] + PAD
        c = Fp[yy, xx]
        d = np.abs(c[..., :3].astype(np.int16) - ref[None]).sum(-1).astype(np.float64)
        d[c[..., 3] == 0] = 300
        out[j] = d.mean(1)
    return out


def best_in(F, rgba, mask, cx, cy, r, sub=True):
    """(cx, cy) 周围 r 格以内最像的位置：先半数像素粗找，再在最好的那格周围全算。"""
    dxs, dys = range(cx - r, cx + r + 1), range(cy - r, cy + r + 1)
    s = scores(F, rgba, mask, dxs, dys, sub)
    j, i = np.unravel_index(np.argmin(s), s.shape)
    if not sub:
        return dxs[i], dys[j], s[j, i]
    dxs, dys = range(dxs[i] - 1, dxs[i] + 2), range(dys[j] - 1, dys[j] + 2)
    s = scores(F, rgba, mask, dxs, dys)
    j, i = np.unravel_index(np.argmin(s), s.shape)
    return dxs[i], dys[j], s[j, i]


def fit(F, head, action, prev=None):
    """(dx, dy, 角度, 颜色差)：先不转，整格子找；再在那附近、上一帧的位置附近试几个角度（转了要明显更像才用）。"""
    x, y, e = best_in(F, head.rgba, head.mask, 0, 20, 60)
    best = (x, y, 0, e)
    if action == "run":
        return best
    seeds = [(x, y, 14)] + ([(prev[0], prev[1], 30)] if prev else [])
    for ang in ANGLES + (DEAD_ANGLES if action in ("dead", "hit") else ()):
        r, m = head.turned(ang)
        for sx, sy, rad in seeds:
            tx, ty, te = best_in(F, r, m, sx, sy, rad)
            if te < best[3] * (TURN_GAIN if best[2] == 0 else 1.0):
                best = (tx, ty, ang, te)
    return best


# ---------------------------------------------------------------- 合成
def compose(F, head, dx, dy, ang, front, erase=()):
    P, Pm = head.placed(dx, dy, ang)
    out = F.copy()
    for pts in erase:
        z = poly([(x + dx, y + dy) for x, y in pts]) & ~Pm
        out[z] = 0
    F = out.copy()
    opq = F[..., 3] > 0
    # 挡在前面的：颜色不是头上的颜色、从标准头外面连进来的那几块
    lock = in_front(F, head, Pm) if front else np.zeros_like(Pm)
    # 旧头剩下的：标准头外面、不经过标准头就连不到身体的块（整块都在下巴以上、离标准头 REACH 格以内）清掉；
    # 标准头外面一圈（BAND 格）里不连着外面的碎块也清掉
    lab, n = ndimage.label(opq & ~Pm & ~lock, structure=np.ones((3, 3)))
    chin = np.nonzero(Pm.any(1))[0].max()
    near = ndimage.binary_dilation(Pm, iterations=REACH)
    ids = np.arange(1, n + 1)
    low = ndimage.maximum(np.arange(Pm.shape[0])[:, None] * np.ones_like(Pm, int), lab, ids) if n else []
    inside = ndimage.minimum(near.astype(int), lab, ids) if n else []
    loose = [k for k, y, z in zip(ids, low, inside) if y < chin - 1 and z == 1]
    out[np.isin(lab, loose)] = 0
    near = ndimage.binary_dilation(Pm, iterations=BAND)
    ring = near & ~Pm & opq
    lab, n = ndimage.label(ring, structure=np.ones((3, 3)))
    edge = ndimage.binary_dilation(~near, iterations=1) & near
    reach = np.unique(lab[edge & (lab > 0)])
    stray = (lab > 0) & ~np.isin(lab, reach)
    out[stray] = 0
    put = Pm & ~lock
    out[put] = P[put]
    # 下巴底下漏空：标准头最下面那格往下补，碰到身体为止
    fill = neck_gaps(out, Pm)
    out[fill[..., 3] > 0] = fill[fill[..., 3] > 0]
    return out, Pm


def in_front(F, head, Pm):
    """标准头范围里、颜色不是头上那些颜色、又和标准头外面连着的格子（手、盾、武器伸到脸前）。"""
    opq = F[..., 3] > 0
    foreign = opq & ~np.isin(keys(F), list(head.palette))
    lab, n = ndimage.label(foreign, structure=np.ones((3, 3)))
    out_ids = np.unique(lab[foreign & ~Pm])
    return np.isin(lab, out_ids[out_ids > 0]) & Pm


def neck_gaps(G, Pm):
    """标准头每一列最下面那格，往下 NECK 格以内碰到身体的，中间透明的格子用这格的颜色补上。"""
    out = np.zeros_like(G)
    H = G.shape[0]
    cols = np.nonzero(Pm.any(0))[0]
    for x in cols:
        y = np.nonzero(Pm[:, x])[0].max()
        k = 1
        while k <= NECK and y + k < H and G[y + k, x, 3] == 0:
            k += 1
        if 1 < k <= NECK and y + k < H and G[y + k, x, 3] > 0:
            out[y + 1:y + k, x] = G[y, x]
    return out


# ---------------------------------------------------------------- 一个英雄
def run_hero(hero, review=None, fits=None, refit=False):
    stem = os.path.join(SNAP, f"border_{hero}")
    sheet, rects = read(stem)
    head = Head(hero, cell(sheet, rects["idle"][0]))
    new = sheet.copy()
    log = {}
    place, front, keep = PLACE.get(hero, {}), FRONT.get(hero, set()), KEEP.get(hero, set())
    erase = ERASE.get(hero, {})
    for action in ACTIONS:
        rows = []
        prev = None
        for i, r in enumerate(rects[action]):
            F = cell(sheet, r)
            if (action, i) in keep:
                rows.append((F, F, None, None))
                log[f"{action}:{i}"] = "keep"
                continue
            key = f"{action}:{i}"
            if (action, i) in place:
                dx, dy, ang = place[(action, i)]
                err = None
            elif not refit and fits is not None and key in fits:
                dx, dy, ang = fits[key]
                err = None
            else:
                dx, dy, ang, err = fit(F, head, action, prev)
                if fits is not None:
                    fits[key] = [int(dx), int(dy), ang]
            prev = (dx, dy)
            er = erase.get((action, i), []) + erase.get((action, None), [])
            G, Pm = compose(F, head, dx, dy, ang, (action, i) in front, er)
            x, y, w, h = r
            new[y:y + h, x:x + w] = G
            rows.append((F, G, (dx, dy, ang), Pm))
            # 最后一个数：标准头范围里有多少格像是挡在前面的东西（挑 FRONT 用）
            log[f"{action}:{i}"] = [int(dx), int(dy), ang, None if err is None else round(float(err), 1),
                                    int(in_front(F, head, Pm).sum())]
        if review:
            review_strip(hero, action, head, rows, review)
    return sheet, new, log


def review_strip(hero, action, head, rows, folder, S=3):
    """上：原样，中：贴头后（新头外缘一圈红点），下：贴好的头按位置对齐排开（应该一模一样，转过的除外）。"""
    ys, xs = np.nonzero(head.mask)
    hx0, hy0, hx1, hy1 = xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7
    bx = (70, 50, 200, 200)
    cw, ch = (bx[2] - bx[0]) * S, (bx[3] - bx[1]) * S
    hw, hh = (hx1 - hx0) * S, (hy1 - hy0) * S
    img = Image.new("RGBA", (cw * len(rows), ch * 2 + hh + 30), (40, 40, 40, 255))
    d = ImageDraw.Draw(img)
    for k, (F, G, pl, Pm) in enumerate(rows):
        for row, A in ((0, F), (1, G)):
            bg = Image.new("RGBA", (CELL, CELL), (96, 110, 92, 255))
            bg.alpha_composite(Image.fromarray(A))
            img.paste(bg.crop(bx).resize((cw, ch), Image.NEAREST), (k * cw, 14 + row * ch))
        if pl is not None:
            e = Pm & ~ndimage.binary_erosion(Pm)
            for yy, xx in zip(*np.nonzero(e)):
                if bx[0] <= xx < bx[2] and bx[1] <= yy < bx[3]:
                    X, Y = k * cw + (xx - bx[0]) * S + S // 2, 14 + ch + (yy - bx[1]) * S + S // 2
                    d.point((X, Y), fill=(255, 40, 40, 255))
            dx, dy = pl[0], pl[1]
            bg = Image.new("RGBA", (CELL, CELL), (96, 110, 92, 255))
            bg.alpha_composite(Image.fromarray(G))
            hc = bg.crop((hx0 + dx, hy0 + dy, hx1 + dx, hy1 + dy)).resize((hw, hh), Image.NEAREST)
            img.paste(hc, (k * cw, 16 + 2 * ch))
        d.text((k * cw + 3, 1), f"{action}{k + 1} {pl if pl else 'keep'}", fill=(255, 255, 255, 255))
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, f"{hero}_{action}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hero", nargs="*", default=list(HEROES))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--fit", action="store_true", help="重新找每帧的位置（写回 head_place.json）")
    a = ap.parse_args()
    table = {}
    if os.path.exists(FITS):
        with open(FITS, encoding="utf-8") as f:
            table = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    logs = {}
    for hero in a.hero:
        fits = table.setdefault(hero, {})
        old, new, log = run_hero(hero, a.review, fits, a.fit)
        logs[hero] = log
        dst = os.path.join(OUT, f"border_{hero}")
        if a.check:
            have = np.asarray(Image.open(dst + "#sheet.png").convert("RGBA")) if os.path.exists(dst + "#sheet.png") else None
            same = have is not None and have.shape == new.shape and np.array_equal(have, new)
            print(hero, "same" if same else "DIFFERENT")
            bad += not same
            continue
        Image.fromarray(new).save(dst + "#sheet.png", optimize=True)
        shutil.copyfile(os.path.join(SNAP, f"border_{hero}#anim.fanim"), dst + "#anim.fanim")
        changed = int((np.abs(new.astype(int) - old.astype(int)).sum(-1) > 0).sum())
        print(hero, "frames", len(log), "pixels changed", changed)
    if not a.check:
        with open(FITS, "w", encoding="utf-8") as f:
            rows = [f'  "{h}": ' + json.dumps(table[h], ensure_ascii=False) for h in sorted(table)]
            f.write("{\n" + ",\n".join(rows) + "\n}\n")
    if a.review:
        with open(os.path.join(a.review, "placements.json"), "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=1)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
