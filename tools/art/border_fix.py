#!/usr/bin/env python3
"""边境巡团（border）Codex 交的特效图收色、技能图标拷进包。身体帧不在这里：Codex v0.9.0 的高清帧由
tools/art/border_hd.py 重出（PPU 2.5）。

    python -I tools/art/border_fix.py --from <交付解压的文件夹>   # Codex 交运行时文件（特效、图标、立绘）时：原样拷进 runtime/
    python tools/art/border_fix.py                               # 读 runtime/effects，写 assets/source/border/snapped/<id>_fx
    python tools/art/border_fix.py --check                       # 重算一遍和 snapped/ 比，不一样退出 1
    （选人立绘：python -I tools/art/bp_illustrations.py assets/source/border/runtime/banpick_illustrations --write）
    然后 tools/art/import_<英雄>.py、ppu_hd.py --hero <英雄>、hero_reels.py --hero <英雄>

特效：每个标签不超过 32 色（颜色在 OKLab 里算，按透明度加权取主色，饱和、离主色远的小色块单独固定），透明度照交的原样。

以前（v0.1-v0.7.2）身体帧也在这里收：Codex 交的是一格 256 的小图（他自己从原画缩的），这里给每人拟合一套 64 色调色板、
清杂点、补同色系描边。2026-11-22 Codex 交了高清帧（v0.9.0），用户要在高清帧上用 PPU 重出（「稍微有点像素感」「比终末
更有像素感一点」），身体改由 border_hd.py 出，那套调色板、描边就拿掉了（在 git 历史里）。
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

FX_COLOURS = 32
SEED = 0



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


def make_hero(hero, write=True):
    """一个英雄的特效：[(snapped 里的路径前缀, sheet, fanim)] 和要打印的话。"""
    hid = f"border_{hero}"
    fx, ffan, counts = fix_fx(os.path.join(RUNTIME, "effects", f"{hid}_fx"))
    msg = f"{hid}: fx " + ", ".join(f"{t} {c}" for t, c in counts.items())
    return [(os.path.join(OUT, f"{hid}_fx"), fx, ffan)], msg


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="src", help="交付解压的文件夹：先把运行时文件拷进 assets/source/border")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--hero", action="append", help="只做这几个（默认六个）")
    a = ap.parse_args()
    if a.src:
        import_delivery(a.src)
    heroes = a.hero or list(HEROES)
    bad = 0
    for hero in heroes:
        outs, msg = make_hero(hero, write=not a.check)
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
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
