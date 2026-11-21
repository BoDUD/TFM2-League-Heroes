#!/usr/bin/env python3
"""索尔第一季造型的两倍帧（assets/source/thor/rebuild/ragnarok_thor_native#sheet.png）：照 Codex 的 build_rebuild.py
从他的原画一格一格重出，改了四处。

    python tools/art/thor_rebuild_fix.py [--check]

Codex 的工具和原画不在仓库里：CODEX（D:/TFM2-Workshop/ragnarok_hd_packs/codex_rebuild，环境变量 THOR_CODEX 可以改），
只读；他交的成品在旁边的 outputs/ragnarok_model_rebuild/thor。这里把他的 models.py、weapons.py、build_rebuild.py 当模块
载进来，照他的步骤（normalized 缩放、按旧帧的胯和脚底定位，place 照青色标记装上 122 x 40 的锤子）重出，拿到三层：锤子、
人物、手边盖在人物上的那截锤子。四处都不改的时候，64 格和他交的逐像素一样。

1. 大小（用户：「人物放技能的时候别一大一小啊」「模型不要变大变小」）。Codex 每个动作按几格剪影的中位高度缩到 112 格，
   剪影里有时带着青色锤子标记的黑边（锤子扛在肩上，剪影高出一截），有时不带（锤子拿在身前、放在地上），几个动作就缩得
   不一样大。量出来（和待机一样扛着锤子站着的帧：头发最高点到脚底，待机 88-91；人物的面积，不算锤子）：普攻、技能、受击
   和待机一样大，不动；投锤矮 9%、面积小 11%；大招没有站着的帧，和同样姿势的比（技能举锤、普攻和技能的砸地、普攻抬锤），
   头大了约 30%（头顶到下巴 23-24 格，别的动作 17-18），身子、靴子也大一圈；倒地后五格（跪下、趴下）和受击是同一张原画，
   缩放却大了 15%；倒地前三格（他单独补画的）第 1 格高了 8%、面积差不多（画得细长）。FIT 在他的缩放上再乘：投锤 1.09
   （高、面积都和普攻、受击一样），大招 0.78（头按 0.76、身子按 0.80-0.84，取中间），倒地后五格 0.87（和受击同一个缩放），
   倒地前三格 0.95（高 3%、面积小 2%，取中间）。锤子还是那把，不跟着缩；大招第 1 格锤子横抱在胸前，人缩小以后锤子上沿
   压到下巴，这一格的锤子单独往下挪 8 格（HAMMER_DY），头和肩膀露在锤子上面。
2. 头（「跑步时脸部模型变形」「索尔投锤和普通的时候也出现了一定程度的模型变形」）：每格的头都是生成图里单独画的，两倍
   密度下一帧一个样。站着的帧都换成待机第 1 格的头（HEAD：脸、额头和头顶的头发，不要后面垂下来的长发、脖子），只平移，
   一个像素不差：待机、跑步跟着胸口走（每帧胸口比第 1 格挪了多少，头就挪多少，头不会在脖子上晃）；别的帧对着原来那个头
   的眼睛（金色眼珠、泪痕最上面那格）放，再按头发、皮肤的位置微调 2 格以内。原来的头比新头大的，头顶、前面多出来的头发、
   皮肤去掉，旧头顶剩下的一两格宽的发丝也去掉，新头最外一圈补深色描边。扑在地上砸锤、举过头顶（头被手臂挡着）、趴下的
   帧头是歪的、被长发盖着，不换（换上去对不上长发，反而难看）。
3. 锤子盖住头顶：Codex 把青色标记外扩 2 格里的锤子画在人物上面（这样手握的地方锤柄在手前面），锤子扛在头后面的帧，
   头顶一两行也被盖掉了（待机每格 25-36 格）。换头的帧，头上的这截锤子不画，头在锤子前面。
4. 色板：Codex 的帧是生成图最近邻缩下来的，64 格里有 12 万多种颜色。选人、百科、记分板用的 lo_ 帧（tools/art/ppu_hd.py
   add_lo）和 1 倍帧（ragnarok_art.hero_sheets）缩的时候，每一块的平均色都要归到这帧（或几帧）最常见的 64 / 96 种颜色上，
   这么多颜色里最常见的全是锤子的灰，皮肤、头发归不过去，出来一个灰白的人、暗红的头发。整张收成 PALETTE 种颜色（中位切分
   起步，再做几轮 k 均值），放大 5 倍并排看和原来几乎一样，lo_、1 倍帧的颜色就对了。

写 rebuild/ragnarok_thor_native#sheet.png 和 checks.csv（每格的脚底、范围、锤子的中心和角度、SHA256，列照 Codex 的）；
#anim.fanim 是 Codex 的，不动。--check 只重算一遍，和仓库里的比，不写文件。
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REBUILD = os.path.join(ROOT, "assets", "source", "thor", "rebuild")
STEM = os.path.join(REBUILD, "ragnarok_thor_native")
CHECKS = os.path.join(REBUILD, "checks.csv")
CODEX = os.environ.get("THOR_CODEX", r"D:\TFM2-Workshop\ragnarok_hd_packs\codex_rebuild")

# 在 Codex 的缩放上再乘多少（倒地前三格是他另画的 thor_deathfix.png，单独一个）
FIT = {"ult": 0.78, "skill2": 1.09, "dead": 0.87}
# 锤子单独往下挪几格的帧：大招第 1 格锤子横抱在胸前，人缩到 0.78 以后锤子还是原来那么大，上沿压到下巴，把脸和肩膀
# 盖住了（用户：「雷神这里有点不对？」）。Codex 原样里下巴到锤子上沿有 7 格（缩完是 5 格），往下挪 8 格，头和肩膀露在
# 锤子上面；手握的那截锤柄一起挪，还在拳头前面
HAMMER_DY = {("ult", 0): 8}
DEATHFIX_FIT = 0.95
# 待机第 1 格里头的范围（格子坐标）：头顶、额头的头发和脸，到下巴；后面只到耳后，垂到肩上的长发不要
HEAD = [(150, 141), (157, 141), (161, 143.5), (162.5, 146), (163, 152), (162, 157.5), (159, 160), (151, 160),
        (147, 157.5), (144.5, 154), (145, 148), (147.5, 143)]
# 换头的帧（站着、头是正的）；待机、跑步按胸口走，别的对着原来的眼睛
UPRIGHT = {"idle": range(8), "run": range(8), "hit": range(8), "skill2": range(8), "attack": (0, 1, 2, 7),
           "skill": (0, 1, 2, 7), "dead": (0, 1, 2), "ult": (0, 1, 2, 7)}
FOLLOW_CHEST = ("idle", "run")
# 待机第 1 格的胸口（脖子下面到腰带上面），量每帧胸口挪了多少用
CHEST = (142, 161, 172, 182)
ACTIONS = ("idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead")

PALETTE = 64                # 整张收成多少种颜色（ppu_hd 的 lo_ 帧按每帧最常见的 64 种取色）
HAIR, SKIN, DARK, OTHER = 1, 2, 3, 4
# 新头最外一圈的描边色（按那格是什么）：头发深红褐、皮肤深褐
OUTLINE = {HAIR: (64, 14, 22), SKIN: (92, 50, 42), DARK: (30, 14, 16), OTHER: (40, 34, 44)}
LUM = np.array([30, 59, 11])


# ---------------------------------------------------------------- Codex 的管线


def codex():
    """载 Codex 的 models / weapons / build_rebuild（不在他的文件夹里留 __pycache__）。改两处：锤子标记缩小以后会短过
    他的检查线 58（只是检查，长度别处不用），记下最后一次装上的锤子（拿锤子那一层）。"""
    if not os.path.isdir(CODEX):
        sys.exit(f"{CODEX}: Codex 的工具和原画不在（环境变量 THOR_CODEX 指到 codex_rebuild 文件夹）")
    sys.dont_write_bytecode = True
    sys.path.insert(0, CODEX)
    import models as M
    import weapons as W
    import build_rebuild as B
    axis = W.marker_axis

    def any_length(mask):
        c, a, n, length = axis(mask)
        return c, a, n, max(length, 58.0)

    W.marker_axis = any_length
    stamp = W.stamp

    def remember(variant, center, angle):
        out = stamp(variant, center, angle)
        W.LAST_STAMP = out
        return out

    W.stamp = remember
    return M, W, B


def posed(M, tag):
    """一个动作 8 格：Codex 的原画格按 normalized 缩放、定位（乘上 FIT），还带着青色标记；和他用的旧帧（定位的参照）。"""
    _, _, previous = M.load_atlas("thor", old=True)
    key = next(k for k, tags in M.BANKS.items() if tag in tags)
    j = M.BANKS[key].index(tag)
    cells = M.cut_grid(M.ART / f"thor_{key}.png")[j * 8:(j + 1) * 8]
    out = M.normalized("thor", tag, cells, previous[tag], fit_override=FIT.get(tag, 1.0))
    if tag == "dead":
        fixes = M.cut_grid(M.ART / "thor_deathfix.png", rows=1)
        out[:3] = M.normalized("thor", "dead", fixes, previous["dead"][:4], fit_override=DEATHFIX_FIT)[:3]
    return out, previous[tag]


def layers(M, W, B, tag, i, image, original):
    """照 weapons.place 装锤子，拆成三层：hammer（整把锤子，在人物后面）、actor（人物）、front（青色标记外扩 2 格里的
    那截锤子，画在人物上面：握的地方锤柄在手前面）。prop 是锤子的中心和角度。"""
    point = M.bounds(M.alpha(original))[3]
    W.LAST_STAMP = None
    result, prop = W.place("thor", tag, i, image, point)
    marker, erase = W.mark_mask(image)
    actor = np.array(W.remove_marker(image, marker, erase, hammer=True))
    actor[actor[..., 3] == 0] = 0
    out = {"actor": actor, "hammer": None, "front": None, "prop": prop, "done": np.asarray(B.clean_pixels(result))}
    if prop is not None:
        out["hammer"] = np.array(W.LAST_STAMP)
        if not (tag == "dead" and i >= 3):
            front = out["hammer"].copy()
            front[~ndi.binary_dilation(marker, iterations=2)] = 0
            out["front"] = front
    return out


def compose(B, L, actor, front):
    if L["hammer"] is None:
        im = Image.fromarray(actor)
    else:
        im = Image.fromarray(L["hammer"])
        im.alpha_composite(Image.fromarray(actor))
        if front is not None:
            im.alpha_composite(Image.fromarray(front))
    return np.asarray(B.clean_pixels(im))


# ---------------------------------------------------------------- 头


def hsv(rgb):
    r, g, b = (rgb[..., i].astype(np.float32) for i in range(3))
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1)
    hue = np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) % 360
    return (r * 30 + g * 59 + b * 11) / 100, sat, hue


def classes(a):
    """每个像素是什么：头发（饱和的红）、皮肤（橙粉）、深色（线条、描边）、别的；透明是 0。"""
    lum, sat, hue = hsv(a[..., :3])
    out = np.full(a.shape[:2], OTHER, np.uint8)
    out[(sat >= 0.12) & (hue >= 8) & (hue < 45) & (lum >= 100)] = SKIN
    out[(sat >= 0.45) & ((hue >= 340) | (hue < 14)) & (lum >= 45)] = HAIR
    out[lum < 45] = DARK
    out[a[..., 3] == 0] = 0
    return out


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    out[max(0, dy):min(H, H + dy), max(0, dx):min(W, W + dx)] = \
        a[max(0, -dy):min(H, H - dy), max(0, -dx):min(W, W - dx)]
    return out


def hair_top(a):
    lum, sat, hue = hsv(a[..., :3])
    h = (a[..., 3] > 0) & (sat >= 0.45) & ((hue >= 340) | (hue < 12)) & (lum > 35)
    ys = np.nonzero(h.sum(1) >= 2)[0]
    top = int(ys.min())
    return int(np.median(np.nonzero(h[top:top + 8].any(0))[0])), top


def eye_of(a):
    """眼睛：头顶往下 22 行里最上面那团金黄（眼珠和下面那道金色泪痕），它最上面一行最靠前（右）的那格。"""
    cx, top = hair_top(a)
    lum, sat, hue = hsv(a[..., :3])
    yel = (a[..., 3] > 0) & (hue >= 22) & (hue < 58) & (sat >= 0.30) & (lum >= 105)
    win = np.zeros_like(yel)
    win[top + 3:top + 22, cx - 10:cx + 14] = True
    lab, n = ndi.label(yel & win, structure=np.ones((3, 3)))
    best = None
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) >= 2 and (best is None or ys.min() < best[1]):
            best = (int(xs[ys == ys.min()].max()), int(ys.min()))
    return best


class Head:
    """待机第 1 格人物层里 HEAD 范围内的像素。"""

    def __init__(self, actor):
        m = Image.new("L", (256, 256))
        ImageDraw.Draw(m).polygon(HEAD, fill=255)
        self.poly = np.asarray(m) > 0
        self.rgba = np.where((self.poly & (actor[..., 3] > 0))[..., None], actor, 0).astype(np.uint8)
        self.mask = self.rgba[..., 3] > 0
        self.cls = classes(self.rgba)
        ys, xs = np.nonzero(self.poly)
        self.box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        self.centre = (float(xs.mean()), float(ys.mean()))
        self.eye = eye_of(actor)

    def fit(self, tgt, guess, reach=2):
        """在 guess 附近 reach 格里找头发、皮肤、深色对得最齐的平移（皮肤算两倍：脸要对上），头伸到透明里扣分。"""
        tc = classes(tgt)
        x0, y0, x1, y1 = self.box
        c = self.cls[y0:y1, x0:x1]
        m = c > 0
        skin = (c == SKIN) & m
        best = None
        for dy in range(guess[1] - reach, guess[1] + reach + 1):
            for dx in range(guess[0] - reach, guess[0] + reach + 1):
                t = tc[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
                same = (c == t) & m
                good = same.sum() + 2.0 * (same & skin).sum() - 0.5 * (m & (t == 0)).sum()
                score = good / (m.sum() + 2.0 * skin.sum())
                if best is None or score > best[0]:
                    best = (score, dx, dy)
        return best[1], best[2]


def chest_shift(ref, tgt, box, reach=6):
    """ref 帧胸口那块（box）在 tgt 里平移多少最像（按部位比）。"""
    c0, c = classes(ref), classes(tgt)
    x0, y0, x1, y1 = box
    r = c0[y0:y1, x0:x1]
    m = r > 0
    best = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            t = c[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
            score = ((t == r) & m).sum() - 0.5 * (m & (t == 0)).sum() - 0.5 * ((t > 0) & ~m).sum()
            if best is None or score > best[0]:
                best = (score, dx, dy)
    return best[1], best[2]


def paste(actor, head, dx, dy):
    """head 平移 (dx, dy) 贴到人物层上，返回（新的人物层、新头的范围）。原来的头多出来的去掉：新头范围里、外面上方和前方
    4 格（皮肤 2 格）里的头发、皮肤、深色像素；再去掉外面 8 格里留不下来的细发丝（3 x 3 开运算去掉的）。新头最外一圈挨着
    透明的、不够深的，换成描边色。"""
    out = actor.copy()
    P, Hm, Hr = shift(head.poly, dx, dy), shift(head.mask, dx, dy), shift(head.rgba, dx, dy)
    yy, xx = np.mgrid[0:256, 0:256]
    ang = np.degrees(np.arctan2(yy + .5 - head.centre[1] - dy, xx + .5 - head.centre[0] - dx))
    cls = classes(actor)
    near = (ang > -160) & (ang < 25)
    old = ((ndi.binary_dilation(P, iterations=4) & near & np.isin(cls, (HAIR, DARK)))
           | (ndi.binary_dilation(P, iterations=2) & near & (cls == SKIN))
           | (P & np.isin(cls, (HAIR, SKIN, DARK)))) & ~Hm
    out[old] = 0
    out[Hm] = Hr[Hm]
    ring = ndi.binary_dilation(P, iterations=8) & ~P & (ang > -170) & (ang < 30)
    op = out[..., 3] > 0
    thin = ring & op & ~ndi.binary_opening(op, structure=np.ones((3, 3), bool)) & np.isin(classes(out), (HAIR, DARK))
    out[thin] = 0
    op = out[..., 3] > 0
    pad = np.pad(op, 1)
    inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    hc = classes(out)
    for y, x in zip(*np.nonzero(Hm & ~inner)):
        if out[y, x, :3].astype(int) @ LUM / 100 > 70:
            out[y, x, :3] = OUTLINE[int(hc[y, x])]
    return out, Hm


# ---------------------------------------------------------------- 色板


def nearest(px, pal, chunk=200000):
    """每个颜色在色板里最近的那个（RGB 平方距离）的序号。"""
    out = np.empty(len(px), np.int64)
    p = pal.astype(np.float64)
    for i in range(0, len(px), chunk):
        d = ((px[i:i + chunk, None, :].astype(np.float64) - p[None]) ** 2).sum(-1)
        out[i:i + chunk] = d.argmin(1)
    return out


def palette(px, n, rounds=12):
    """px（N x 3）的 n 色色板：中位切分起步，再做几轮 k 均值（每色取归到它的那些像素的平均）。"""
    q = Image.fromarray(px.reshape(1, -1, 3)).quantize(colors=n, method=Image.Quantize.MEDIANCUT,
                                                       dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:n * 3], np.float64).reshape(-1, 3)
    x = px.astype(np.float64)
    for _ in range(rounds):
        idx = nearest(x, pal)
        for k in range(len(pal)):
            m = idx == k
            if m.any():
                pal[k] = x[m].mean(0)
    return np.round(pal).astype(np.uint8)


def flatten(frames):
    """所有帧一起收成 PALETTE 种颜色（同一个颜色到哪儿都换成同一个）。"""
    every = np.concatenate([a[a[..., 3] > 0][:, :3] for tag in ACTIONS for a in frames[tag]])
    pal = palette(every, PALETTE)
    out = {}
    for tag in ACTIONS:
        out[tag] = []
        for a in frames[tag]:
            b = a.copy()
            op = b[..., 3] > 0
            b[op, :3] = pal[nearest(b[op][:, :3], pal)]
            out[tag].append(b)
    return out


# ---------------------------------------------------------------- 出图


def build():
    """-> ({动作: [8 格 RGBA]}, {动作: [(锤子中心 x, y, 角度) 或 None]}, {动作: [人物层]}, {(动作, 格): (dx, dy)})"""
    M, W, B = codex()
    L = {}
    for tag in ACTIONS:
        imgs, prev = posed(M, tag)
        L[tag] = [layers(M, W, B, tag, i, imgs[i], prev[i]) for i in range(8)]
    head = Head(L["idle"][0]["actor"])
    frames, props, actors, moved = {}, {}, {}, {}
    for tag in ACTIONS:
        frames[tag], props[tag], actors[tag] = [], [], []
        base = None
        for i, Li in enumerate(L[tag]):
            actor, front = Li["actor"], Li["front"]
            hdy = HAMMER_DY.get((tag, i), 0)
            if hdy:
                p = Li["prop"]
                Li = dict(Li, hammer=shift(Li["hammer"], 0, hdy),
                          prop=None if p is None else (p[0], p[1] + hdy, *p[2:]))
                front = None if front is None else shift(front, 0, hdy)
            if i in UPRIGHT.get(tag, ()):
                if tag in FOLLOW_CHEST and base is not None:
                    bx, by = base
                    box = (CHEST[0] + bx, CHEST[1] + by, CHEST[2] + bx, CHEST[3] + by)
                    cx, cy = chest_shift(L[tag][0]["actor"], actor, box)
                    dx, dy = bx + cx, by + cy
                else:
                    ex, ey = eye_of(actor)
                    dx, dy = head.fit(actor, (ex - head.eye[0], ey - head.eye[1]))
                    if i == 0:
                        base = (dx, dy)
                actor, on = paste(actor, head, dx, dy)
                if front is not None:
                    front = front.copy()
                    front[on] = 0
                moved[tag, i] = (dx, dy)
            frames[tag].append(compose(B, Li, actor, front))
            props[tag].append(Li["prop"])
            actors[tag].append(actor)
    return frames, props, actors, moved


def sheet_and_checks(frames, props, actors):
    with open(STEM + "#anim.fanim", encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    sheet = np.zeros((8 * 256, 8 * 256, 4), np.uint8)
    rows = []
    for tag in ACTIONS:
        for i, fr in enumerate(anims[tag]["frames"]):
            d = fr["data"]
            x, y = int(d["x"]), int(d["y"])
            a = frames[tag][i]
            sheet[y:y + 256, x:x + 256] = a
            ys, xs = np.nonzero(a[..., 3] > 0)
            body = np.nonzero((actors[tag][i][..., 3] > 0).any(1))[0]
            p = props[tag][i]
            rows.append([tag, i + 1, fr["duration"], int(body.max()) + 1, int(ys.max()) + 1,
                         int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1,
                         "" if p is None else "/".join(f"{v:.2f}" for v in p),
                         hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()])
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["action", "frame", "seconds", "actor_baseline", "visible_baseline", "x0", "y0", "x1", "y1",
                "weapon_x_y_degrees", "rgba_sha256"])
    w.writerows(rows)
    return sheet, buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="只重算，和仓库里的比")
    a = ap.parse_args()
    frames, props, actors, moved = build()
    sheet, checks = sheet_and_checks(flatten(frames), props, actors)
    if a.check:
        bad = 0
        old = np.asarray(Image.open(STEM + "#sheet.png").convert("RGBA"))
        if old.shape != sheet.shape or not np.array_equal(old, sheet):
            print(STEM + "#sheet.png differs")
            bad += 1
        with open(CHECKS, encoding="utf-8") as f:
            if f.read() != checks:
                print(CHECKS + " differs")
                bad += 1
        sys.exit(1 if bad else 0)
    Image.fromarray(sheet).save(STEM + "#sheet.png")
    with open(CHECKS, "w", encoding="utf-8", newline="") as f:
        f.write(checks)
    print(f"{STEM}#sheet.png, checks.csv; head pasted in {len(moved)} frames")


if __name__ == "__main__":
    main()
