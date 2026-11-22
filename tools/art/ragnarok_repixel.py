#!/usr/bin/env python3
"""终末包英雄照 Codex 的原画重出更细的像素图：共用的取样和清理。亚当先这么做的（tools/art/adam_repixel.py），
吕布、索尔、宙斯照着来。

每个英雄一个小脚本：照 Codex 自己的工具算出每帧原画里对应一格的位置和缩放（重出时乘上密度倍数 UP），
把（原画格, 缩放, 左上角 x, 左上角 y）交给 repixel()；部位怎么分、每个部位留几档、描边用什么颜色由英雄自己给（Style）。

做法（亚当试出来、用户看过的）：
- 部位：原画每个像素先分到部位（皮肤、头发……，各英雄自己分），每个部位从全部动作的原画里取几档颜色（中位切分）；
- 取样：每格按占多数的部位定是什么（深色线条占到四成就算线条，不会被肤色吃掉），取这个部位在格子里的平均色，
  归到这个部位最近的那一档；人物盖住一半以上的格子才算人物；手臂、手指这类细处加厚（用户嫌亚当「手臂有点细」），
  身体里被包住的很小的透明洞填上；
- 清杂点：同部位里孤立的一两个像素并进周围那档（头顶往下几行里的眼睛、眉毛留着）；头部以外的深色线换成所在部位
  最暗的那档（线条画在皮肤上像脏点：「身体上还是不干净啊」）；
- 修轮廓、补描边：去掉只连着一格的小刺、填上三面被包住的缺口、去掉碎块；最外一圈换成同色系的深一档（描边色按往里
  一格那个颜色的部位挑，不用一圈近黑的线：「身体周围那个描边还是太厚了太浓了」），紧贴描边里面那圈太深的换成
  旁边不深的颜色（不然描边看着有两格粗）。
"""
import argparse
import importlib.util
import json
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image

NEAR8 = ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1))
NEAR4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
LUM = np.array([30, 59, 11])


class Style:
    """一个英雄的部位和颜色设定。

    parts_of(rgb)：每个像素属于哪个部位，编号从 1 起（0 留给透明）；tile_parts(rgba)：一整格原画的部位图，不给就是
    parts_of 再把透明的记成 0（亚当另给了一个：头发只认连成一大片的那块）。
    tones：{部位: 留几档颜色}，所有部位都要在里面；ink：深色线条那个部位。
    head_keep：头顶往下 head_rows 行（按重出前的格数算，会乘 up）里，单个像素不当杂点清掉的部位（眼睛、眉毛）。
    outline：{部位: 描边色}，按往里一格那个颜色用 parts_of 分出来的部位挑。
    thin_cover：细的地方旁边，原画盖住这么多的格子也算人物；ink_share：格子里深色线条占到这么多就算线条；
    ring_lum：紧贴描边里面那圈亮度低于这个的换掉。
    """

    def __init__(self, parts_of, tones, ink, outline, up=2.0, tile_parts=None, head_keep=(), head_rows=16,
                 thin_cover=0.2, ink_share=0.4, ring_lum=75):
        self.parts_of = parts_of
        self.tile_parts = tile_parts or self._tile_parts
        self.tones = dict(tones)
        self.ink = ink
        self.outline = dict(outline)
        self.up = up
        self.head_keep = tuple(head_keep)
        self.head_rows = head_rows
        self.thin_cover = thin_cover
        self.ink_share = ink_share
        self.ring_lum = ring_lum
        self.count = max(self.tones) + 1
        self.colours = [k for k in sorted(self.tones) if k != ink]

    def _tile_parts(self, a):
        lab = self.parts_of(a[..., :3])
        lab[a[..., 3] == 0] = 0
        return lab

    def outline_of(self, c):
        return self.outline[int(self.parts_of(np.array([[c]], np.uint8))[0, 0])]


def load(path, name):
    """把 Codex 的工具当模块载进来（拿它的切格、抠图、位置算法）。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ramps(st, tiles):
    """每个部位的几档颜色：全部动作的原画一起算（中位切分），从暗到亮排好。"""
    pools = {k: [] for k in st.tones}
    for t in tiles:
        a = np.asarray(t)
        lab = st.tile_parts(a)
        rgb = a[..., :3]
        for k in st.tones:
            pools[k].append(rgb[lab == k][::5])
    out = {}
    for k, n in st.tones.items():
        px = np.concatenate(pools[k]).astype(np.uint8)
        q = Image.fromarray(px.reshape(1, -1, 3)).quantize(colors=n, dither=Image.Dither.NONE)
        pal = np.array(q.getpalette()[:3 * n]).reshape(-1, 3)
        out[k] = pal[np.argsort(pal @ LUM)]
    return out


def sample(st, tile, scale, x0, y0, cell, ramp):
    """缩到 cell 格：每格先按占多数的部位定是什么，再取这个部位在格子里的平均颜色，归到这个部位最近的那一档。
    人物盖住一半以上的格子才算人物；离背景最远也只有 2*up 格的细处，旁边被原画盖住一点的格子也算进来，身体的大小
    不变。返回（部位、档、是不是人物）三张图。"""
    from scipy import ndimage
    up = st.up
    a = np.asarray(tile)
    lab = st.tile_parts(a)
    rgb = a[..., :3].astype(np.float32)
    cover = np.zeros((cell, cell), np.float32)
    part = np.zeros((cell, cell), np.uint8)
    tone = np.zeros((cell, cell), np.uint8)
    step = 1 / scale
    edges_y = np.floor(y0 + np.arange(cell + 1) * step).astype(int)
    edges_x = np.floor(x0 + np.arange(cell + 1) * step).astype(int)
    H, W = lab.shape
    ids = np.arange(st.count)
    for v in range(cell):
        sy0, sy1 = max(0, edges_y[v]), min(H, edges_y[v + 1])
        if sy1 <= sy0:
            continue
        for u in range(cell):
            sx0, sx1 = max(0, edges_x[u]), min(W, edges_x[u + 1])
            if sx1 <= sx0:
                continue
            lb = lab[sy0:sy1, sx0:sx1]
            on = lb > 0
            if not on.any():
                continue
            full = (edges_y[v + 1] - edges_y[v]) * (edges_x[u + 1] - edges_x[u])
            cover[v, u] = on.sum() / full
            counts = np.bincount(lb[on], minlength=st.count)
            if counts[st.ink] >= st.ink_share * on.sum() or counts[st.colours].sum() == 0:
                k = st.ink
            else:
                k = int(np.argmax(np.where(ids == st.ink, -1, counts)))
            mean = rgb[sy0:sy1, sx0:sx1][lb == k].mean(0)
            part[v, u] = k
            tone[v, u] = int(np.argmin(((ramp[k] - mean) ** 2).sum(1)))
    body = cover >= 0.5
    # 细的地方分两步加厚：先加原画盖住 thin_cover 以上的格子，再加原画边上沾到一点的格子；躯干这种粗的地方不动
    for least in (st.thin_cover, 0.02):
        for _ in range(round(up)):
            depth = ndimage.distance_transform_edt(body)
            thin = body & (ndimage.maximum_filter(depth, size=3) <= 2 * up)
            near_thin = ndimage.binary_dilation(thin, structure=np.ones((3, 3), bool))
            body |= near_thin & (cover >= least)
    # 身体里被包住的很小的透明洞（手臂和身子之间缩小后剩下的一点缝）填上，用周围部位偏暗的那档：留着会补出一个
    # 深色小圈，看着像脏点
    holes = ndimage.binary_fill_holes(body) & ~body
    hl, hn = ndimage.label(holes)
    for i in range(1, hn + 1):
        m = hl == i
        if m.sum() > 4 * up * up:
            continue
        ring = ndimage.binary_dilation(m) & body
        k = Counter(part[ring].tolist()).most_common(1)[0][0]
        body |= m
        part[m] = k
        tone[m] = min(1, len(ramp[k]) - 1)
    part[~body] = 0
    return part, tone, body


def settle(st, part, tone, body):
    """同一部位里把孤立的一两个像素并进周围那一档：八个邻居里没有一个和它同部位同档、而有四个以上是同一个（部位、档），
    就改成那个；整个被别的部位围着的单个像素也一样。头顶往下 head_rows 行里 head_keep 部位的单个像素留着。做两遍。
    然后头部以外的深色线换成它所在部位最暗的那档。"""
    H, W = part.shape
    ys = np.nonzero(body.any(1))[0]
    head_end = (ys.min() + round(st.head_rows * st.up)) if len(ys) else 0
    for _ in range(2):
        np_, nt = part.copy(), tone.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if not body[y, x]:
                    continue
                own = (part[y, x], tone[y, x])
                keys = [(part[y + dy, x + dx], tone[y + dy, x + dx]) for dy, dx in NEAR8 if body[y + dy, x + dx]]
                if not keys or own in keys:
                    continue
                if part[y, x] in st.head_keep and y < head_end:
                    continue
                key, n = Counter(keys).most_common(1)[0]
                if n >= 4:
                    np_[y, x], nt[y, x] = key
        part, tone = np_, nt
    for y, x in zip(*np.nonzero((part == st.ink) & body)):
        if y < head_end:
            continue
        around = [part[y + dy, x + dx] for dy, dx in NEAR8
                  if 0 <= y + dy < H and 0 <= x + dx < W and body[y + dy, x + dx] and part[y + dy, x + dx] != st.ink]
        if around:
            part[y, x] = Counter(around).most_common(1)[0][0]
            tone[y, x] = 0
    return part, tone


def paint(part, tone, ramp):
    out = np.zeros(part.shape + (4,), np.uint8)
    for k, pal in ramp.items():
        m = part == k
        out[m, :3] = pal[tone[m]]
        out[m, 3] = 255
    return out


def dilate4(mask):
    """上下左右挨着 mask 的格子（含 mask 自己）。"""
    out = mask.copy()
    out[1:] |= mask[:-1]
    out[:-1] |= mask[1:]
    out[:, 1:] |= mask[:, :-1]
    out[:, :-1] |= mask[:, 1:]
    return out


def smooth(f, op):
    """把轮廓修顺：只连着一格的小刺去掉，三面被包住的小缺口填上（颜色取四周最多的），各做两遍；再去掉不到 4 格的碎块。"""
    from scipy import ndimage
    f = f.copy()
    H, W = op.shape
    for _ in range(2):
        pad = np.pad(op, 1)
        n4 = pad[:-2, 1:-1].astype(int) + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]
        spur = op & (n4 <= 1)
        notch = ~op & (n4 >= 3)
        for y, x in zip(*np.nonzero(notch)):
            nb = [tuple(f[y + dy, x + dx, :3]) for dy, dx in NEAR4
                  if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx]]
            f[y, x, :3] = Counter(nb).most_common(1)[0][0]
            f[y, x, 3] = 255
        op = (op & ~spur) | notch
        f[~op] = 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    if n:
        sizes = ndimage.sum(op, lab, range(1, n + 1))
        small = np.zeros(n + 1, bool)
        small[1:] = sizes < 4
        op &= ~small[lab]
        f[~op] = 0
    return f, op


def tidy(st, f):
    """清杂点（两遍），修轮廓，再补一圈同色系的描边。"""
    f = f.copy()
    op = f[..., 3] > 0
    q = f[..., :3].astype(int)
    H, W = op.shape
    for _ in range(2):
        new = q.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if not op[y, x]:
                    continue
                nb = [tuple(q[y + dy, x + dx]) for dy, dx in NEAR4 if op[y + dy, x + dx]]
                if len(nb) < 4 or tuple(q[y, x]) in nb:
                    continue
                c, n = Counter(nb).most_common(1)[0]
                if n >= 3:
                    new[y, x] = c
        q = new
    f[..., :3] = q.astype(np.uint8)
    f, op = smooth(f, op)
    pad = np.pad(op, 1)
    inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    edge = op & ~inner
    # 最外一圈全部换成描边色（原来已经够深的也换，免得描边一块深一块浅），颜色按往里一格的部位挑
    ys, xs = np.nonzero(edge)
    cols = []
    for y, x in zip(ys, xs):
        col = None
        for dy, dx in NEAR8:
            y2, x2 = y + dy, x + dx
            if 0 <= y2 < H and 0 <= x2 < W and inner[y2, x2]:
                col = st.outline_of(f[y2, x2, :3])
                break
        cols.append(col if col is not None else st.outline_of(f[y, x, :3]))
    for y, x, col in zip(ys, xs, cols):
        f[y, x, :3] = col
    # 紧贴描边里面那一圈：原画自带的深色描边被缩进这里，看起来描边成了两格粗、一坨一坨的；改成旁边不深的颜色
    lum = f[..., :3].astype(int) @ LUM / 100
    ring = inner & dilate4(edge)
    for y, x in zip(*np.nonzero(ring & (lum < st.ring_lum))):
        nb = [tuple(f[y + dy, x + dx, :3]) for dy, dx in NEAR8
              if 0 <= y + dy < H and 0 <= x + dx < W and inner[y + dy, x + dx] and lum[y + dy, x + dx] >= st.ring_lum]
        if nb:
            f[y, x, :3] = Counter(nb).most_common(1)[0][0]
    return f


def repixel(st, jobs, cell, ramp=None):
    """jobs：[(原画格 RGBA, 缩放, 左上角 x, 左上角 y)]，按顺序出 cell x cell 的帧。颜色档不给就用这批原画一起算。"""
    ramp = ramp if ramp is not None else ramps(st, [t for t, *_ in jobs])
    out = []
    for t, scale, x0, y0 in jobs:
        part, tone, body = sample(st, t, scale, x0, y0, cell, ramp)
        part, tone = settle(st, part, tone, body)
        out.append(tidy(st, paint(part, tone, ramp)))
    return out


def median_cut(cols, n):
    """一堆颜色（N x 3）的中位切分调色板（不抖动），只留真用上的。"""
    q = Image.fromarray(cols.reshape(1, -1, 3).astype(np.uint8)).quantize(
        colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:3 * n]).reshape(-1, 3)
    return pal[np.unique(np.asarray(q).ravel())]


def snap(sheet, n=64):
    """整张图收到 n 色：中位切分出调色板，每个不透明像素换成最近的颜色（透明的不动）。Codex 重画的图是缩小的手绘，
    十几二十万种颜色；ppu_hd.py 出 lo_（选人、百科）和 ragnarok_art.py 出 1 倍帧都拿「这一帧最常见的 64 / 96 种颜色」当
    调色板，颜色一散就挑歪（皮肤一块深一块浅、整个人发黄发粉）。收到 64 色 3 倍放大看和原来几乎一样。"""
    out = sheet.copy()
    op = sheet[..., 3] > 0
    cols = sheet[op][:, :3].astype(int)
    pal = median_cut(cols, n)
    snapped = np.empty_like(cols)
    for i in range(0, len(cols), 20000):            # 分块算最近的颜色，省内存
        d = ((cols[i:i + 20000, None, :] - pal[None]) ** 2).sum(-1)
        snapped[i:i + 20000] = pal[np.argmin(d, 1)]
    out[op, :3] = snapped
    return out


def snap_to(sheet, pal, mask=None):
    """不透明像素（mask 给了就只管 mask 里的）换成 pal 里最近的颜色。"""
    out = sheet.copy()
    op = sheet[..., 3] > 0
    if mask is not None:
        op &= mask
    cols = sheet[op][:, :3].astype(int)
    snapped = np.empty_like(cols)
    for i in range(0, len(cols), 20000):
        d = ((cols[i:i + 20000, None, :] - pal[None]) ** 2).sum(-1)
        snapped[i:i + 20000] = pal[np.argmin(d, 1)]
    out[op, :3] = snapped
    return out


def snap_delivery(src, out, bodies, fx, body_colours=64, fx_colours=32):
    """Codex 直接按两倍密度交的一个英雄（小次郎以后都这样：一格 256、脚底 (128, 232)）收色，tools/art/kojiro_fix.py 的做法：
    几张身体图合起来一套 body_colours 色的调色板（换形态时颜色不跳），特效图每组 fx_colours 色。
    src 是 Codex 的 runtime/sprites（只读），返回 [(out 里的路径前缀, sheet, fanim)] 给 run()。
    bodies 里也可以直接给 (名字, sheet, fanim)：先改过再收色的图（零福重贴过斧子的常态，tools/art/zerofuku_fix.py）。"""
    def read(stem):
        if isinstance(stem, tuple):
            return stem[1], stem[2]
        sheet = np.asarray(Image.open(os.path.join(src, stem + "#sheet.png")).convert("RGBA"))
        return sheet, json.load(open(os.path.join(src, stem + "#anim.fanim"), encoding="utf-8-sig"))

    outs = []
    sheets = [read(s) for s in bodies]
    pool = np.concatenate([s[s[..., 3] > 0][:, :3] for s, _ in sheets])
    pal = median_cut(pool, body_colours)
    for stem, (sheet, fanim) in zip(bodies, sheets):
        name = stem[0] if isinstance(stem, tuple) else stem
        outs.append((os.path.join(out, name), snap_to(sheet, pal), fanim))
    sheet, fanim = read(fx)
    done = sheet.copy()
    for a in fanim["anims"].values():
        mask = np.zeros(sheet.shape[:2], bool)
        for f in a["frames"]:
            x, y, w, h = (int(f["data"][k]) for k in "xywh")
            mask[y:y + h, x:x + w] = True
        cols = sheet[mask & (sheet[..., 3] > 0)][:, :3]
        done = snap_to(done, median_cut(cols, fx_colours), mask)
    outs.append((os.path.join(out, fx), done, fanim))
    return outs


def sheet_of(frames, codex, up):
    """照 Codex 那张图的排法放大 up 倍：每格换成重出的帧（frames[动作][第几帧]），#anim.fanim 的坐标跟着乘 up。"""
    old = Image.open(codex + "#sheet.png")
    sheet = np.zeros((round(old.height * up), round(old.width * up), 4), np.uint8)
    fanim = json.load(open(codex + "#anim.fanim", encoding="utf-8-sig"))
    for tag, a in fanim["anims"].items():
        for i, fr in enumerate(a["frames"]):
            d = fr["data"]
            for k in ("x", "y", "w", "h"):
                d[k] = round(d[k] * up)
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            sheet[y:y + h, x:x + w] = frames[tag][i][:h, :w]
    return sheet, fanim


def run(doc, make, up):
    """命令行：make(up) 返回 [(输出路径前缀, sheet, fanim)]。--check 只重算一遍和仓库里的比，不写文件。"""
    ap = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--up", type=float, help=f"密度倍数（默认 {up}）")
    ap.add_argument("--out-dir", help="写到别的文件夹（比较用）")
    a = ap.parse_args()
    outs = make(a.up or up)
    if a.out_dir:
        outs = [(os.path.join(a.out_dir, os.path.basename(stem)), sheet, fanim) for stem, sheet, fanim in outs]
    if a.check:
        bad = 0
        for stem, sheet, _ in outs:
            old = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA")) if os.path.exists(stem + "#sheet.png") else None
            if old is None or not (old.shape == sheet.shape and np.array_equal(old, sheet)):
                print(stem, "DIFFERS - run", os.path.relpath(sys.argv[0]))
                bad += 1
        sys.exit(1 if bad else 0)
    for stem, sheet, fanim in outs:
        os.makedirs(os.path.dirname(stem), exist_ok=True)
        Image.fromarray(sheet).save(stem + "#sheet.png")
        with open(stem + "#anim.fanim", "w", encoding="utf-8") as f:
            json.dump(fanim, f, ensure_ascii=False)
        print(stem + "#sheet.png", sheet.shape[1], "x", sheet.shape[0])
