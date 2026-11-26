#!/usr/bin/env python3
"""峡谷版的元素亚龙和远古巨龙（league_dragons 0.5.12）。

用户 2026-11-26：「我们的小龙在大地图的龙坑站位方向应该朝着外面吧 要和原版地图不一样吧 这个得改一下吧」。Rin 的召唤师峡谷上
小龙坑被石墙围了大半圈，只在右上方开口；正面朝着镜头的龙在那里等于脸对着坑后面的墙。Codex 第 3 步把六条元素亚龙和远古巨龙
转身朝画面右上方（背对镜头，看得到右侧身和背）重画了设计、攻击 1-5、死亡 1-6（dragons_rift_done.zip 里的 dragons-rift/<模型>/
rift_*.png：Codex 已经校正成 6 px 一格、透明度只有 0 / 255，攻击帧的身子直接用设计图的）。图不在仓库里，这个工具从解压的地方读：

    python tools/art/dragons_rift_hd.py --frames DIR/dragons-rift [--only infernal ...] [--review DIR]

写 addons/league_dragons/effects/league_drake_<元素>_rift、league_drake_elder_rift。动作名、帧数、每帧时长、PPU 1.8、锚点（脚底在
锚点下 37 游戏像素）都和正面那套（dragons_hd.py）一样；只在 Rin 的峡谷上换成这一套（src/skin.rs），游戏自带的地图照旧用正面的。

1. 读：每格取格子中间那个像素（Codex 交的每格已经是平的）。Codex 是一帧一帧校色的，死亡帧和攻击帧的头每张都有五十来种设计图里
   没有的颜色（色差多数在 3-8 之间），连着播会闪：和设计图的 48 色色差 15 以内的都换成设计图的那一色，更远的只有元素特效（火、
   水花、碎石之类），保留原色。
2. 死亡第 2 帧（扭着倒下、蜷成一团）七只都画小了：头 14 格宽，第 1 帧和设计图 23 格左右。以落地的底边中点为准放大 1.5 倍
   （一格变一格半，最近邻），不然播到这一帧龙突然变小（用户：模型不要变大变小）。
3. base = 设计图；idle = 远处那只往左伸的翅膀扇动：翅根在肩上钉住，翅尖抬 0 / 1 / 2 / 3 / 3 / 2 / 1 / 0 格，身子、头、尾巴、近处的
   翅膀都不动（用户不许变形，正面那套也是只动翅膀）；attack = Codex 的 5 帧，第 2 帧嘴里聚起元素，第 3-5 帧从那一帧的嘴朝右上方
   （坑口）喷出去、落点炸开，外加正面那套一样的冲击环（dragon_fx.drake_attack_aimed：嘴朝外，吐息画在龙后面）；dead 1-6 =
   Codex 的（主体的底边放在脚底那一行），7 = 第 6 帧碎开，8 = 空（和正面那套一样）。
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dragons_hd as H  # noqa: E402  裁帧、1x、碎开、写图都用正面那套的
import dragon_fx as fx  # noqa: E402

SQ = 6
MODELS = ["infernal", "mountain", "ocean", "cloud", "hextech", "chemtech", "elder"]
NAMES = {m: f"league_drake_{m}_rift" for m in MODELS}
DIR = None

# 嘴的位置：Codex 画布上的格子（x 往右、y 往下，256 x 170 格），拿尺子从帧上量的。第一个是第 2 帧嘴里聚元素的地方，后面三个
# 是第 3、4、5 帧吐息出来的地方（头每帧都在动）
JAWS = {
    "infernal": ((166.5, 58.0), ((176.5, 59.0), (177.5, 52.5), (172.0, 54.0))),
    "mountain": ((165.0, 54.0), ((176.5, 58.0), (177.5, 52.0), (172.0, 54.0))),
    "ocean": ((166.0, 55.0), ((176.0, 58.0), (175.0, 53.0), (172.0, 54.0))),
    "cloud": ((163.5, 55.0), ((176.5, 60.0), (170.0, 54.0), (172.0, 55.0))),
    "hextech": ((165.0, 60.0), ((173.5, 60.0), (176.5, 55.0), (173.0, 56.5))),
    "chemtech": ((166.0, 56.5), ((176.5, 56.5), (173.5, 53.5), (175.0, 55.0))),
    "elder": ((191.0, 45.0), ((204.0, 47.5), (196.0, 46.0), (199.0, 40.0))),
}
# 吐息落在哪：第 4 帧的嘴往右上方这么多格（约 38 度，和 Codex 画的元素同一个方向）
AIM = (55.0, -43.0)
DEAD2_SCALE = 1.5
NEAR = 15.0           # 和设计图颜色的色差在这以内就换成设计图那一色
WING_ROOT_ROW = 115   # 往右数第一列、最上面一段一直连到这一行以下的：翅根（肩膀），从这一列起不动


def lab(rgb):
    return color.rgb2lab(np.asarray(rgb, float).reshape(-1, 1, 3) / 255.0)[:, 0]


def load(model, frame):
    a = np.asarray(Image.open(os.path.join(DIR, model, frame + ".png")).convert("RGBA"))
    h = a.shape[0] // SQ * SQ
    out = a[SQ // 2:h:SQ, SQ // 2::SQ].copy()
    out[..., 3] = np.where(out[..., 3] >= 128, 255, 0)
    return out


def to_design(a, pal, pal_lab):
    """色差 NEAR 以内的颜色换成设计图的那一色，远的（元素特效）不动"""
    on = a[..., 3] > 0
    if not on.any():
        return a
    px = a[on][:, :3]
    u, inv = np.unique(px, axis=0, return_inverse=True)
    d = np.sqrt(((lab(u)[:, None] - pal_lab[None]) ** 2).sum(-1))
    j = d.argmin(1)
    new = np.where((d.min(1) < NEAR)[:, None], pal[j], u)
    out = a.copy()
    out[on, :3] = new[inv.ravel()]
    return out


def upscale(a, k, pivot):
    """`a` 放大 k 倍，`pivot`（格子坐标 (x, y)，格子的边上）不动：每一格取放大前那个位置上的格子（最近邻）"""
    h, w = a.shape[:2]
    px, py = pivot
    ys = np.floor(py + (np.arange(h) + 0.5 - py) / k).astype(int)
    xs = np.floor(px + (np.arange(w) + 0.5 - px) / k).astype(int)
    out = np.zeros_like(a)
    oy = np.nonzero((ys >= 0) & (ys < h))[0]
    ox = np.nonzero((xs >= 0) & (xs < w))[0]
    out[np.ix_(oy, ox)] = a[np.ix_(ys[oy], xs[ox])]
    return out


def runs_touching(col, seed):
    """`col` 里和 `seed` 有交集的那几段（整段）"""
    out = np.zeros_like(col)
    ys = np.nonzero(col)[0]
    if not len(ys):
        return out
    s = p = ys[0]
    for y in list(ys[1:]) + [None]:
        if y is not None and y == p + 1:
            p = y
            continue
        if seed[s:p + 1].any():
            out[s:p + 1] = True
        if y is not None:
            s = p = y
    return out


def far_wing(d):
    """远处那只翅膀：从最左边的翅尖那一列开始一列一列往右追，每一列取和上一列翅膀挨着的那几段；追到哪一列这几段一直连到
    WING_ROOT_ROW 以下（和肩膀、身子连上了）就是翅根，从那一列起不算翅膀。返回 (翅膀那一块, 翅尖那一列, 翅根那一列)。
    （先前按每一列最上面那一段找翅根，海克斯亚龙肩上多一根小刺，翅膀在下一段里已经和身子连上，整个身子都被当成了翅膀）"""
    on = d[..., 3] > 0
    tip = int(np.nonzero(on.any(0))[0].min())
    wing = np.zeros_like(on)
    cur = on[:, tip].copy()
    root = None
    for x in range(tip, d.shape[1]):
        if x > tip:
            cur = runs_touching(on[:, x], wing[:, x - 1])
        if not cur.any():
            root = x
            break
        if np.nonzero(cur)[0].max() >= WING_ROOT_ROW:
            root = x
            break
        wing[:, x] = cur
    return wing, tip, root


def flap(d, wing, tip, root, k):
    """翅膀那一块一列一列往上挪：离翅根越远挪得越多，翅尖 k 格，翅根不动；别的都不动"""
    out = d.copy()
    out[wing] = 0
    span = max(1, root - tip)
    for x in range(tip, root):
        ys = np.nonzero(wing[:, x])[0]
        if not len(ys):
            continue
        s = int(round(k * (root - x) / span))
        yy = ys - s
        ok = yy >= 0
        out[yy[ok], x] = d[ys[ok], x]
    return out


def frames_of(model):
    d = load(model, "rift_design")
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    pl = lab(pal)
    ys = np.nonzero(d[..., 3].any(1))[0]
    bot = int(ys.max())                                   # 脚底最后一行
    tags = {"base": [d]}
    wing, tip, root = far_wing(d)
    wy = np.nonzero(wing.any(1))[0]
    tags["idle"] = [flap(d, wing, tip, root, k) for k in H.WING_LIFTS]
    tags["attack"] = [to_design(load(model, f"rift_attack_{k}"), pal, pl) for k in range(1, 6)]
    dead = [to_design(load(model, f"rift_dead_{k}"), pal, pl) for k in range(1, 7)]
    m2 = dead[1][..., 3] > 0
    yy, xx = np.nonzero(m2)
    pivot = ((xx.min() + xx.max() + 1) / 2.0, float(yy.max() + 1))
    dead[1] = upscale(dead[1], DEAD2_SCALE, pivot)
    dys = {}
    for k in range(6):
        b = H.main_box(dead[k])
        dys[k + 1] = bot - (b[3] - 1)
    if abs(dys[6] - dys[5]) <= 3:
        dys[6] = dys[5]                                   # 同一个躺姿在消散：不跳
    dead = [H.shift(a, dys[k + 1]) for k, a in enumerate(dead)]
    dead += H.shards(dead[-1], [0.55], seed=11)
    dead.append(np.zeros_like(d))
    tags["dead"] = dead
    anchor = (128.0, bot + 1 - 66.5)
    M = H.RING_MARGIN
    tags = {t: [H.pad(a, M) for a in frs] for t, frs in tags.items()}
    big = (anchor[0] + M, anchor[1] + M)
    glow, mouths = JAWS[model]
    glow = (glow[0] + M, glow[1] + M)
    mouths = [(x + M, y + M) for x, y in mouths]
    land = (mouths[1][0] + AIM[0], mouths[1][1] + AIM[1])
    tags["attack"] = fx.drake_attack_aimed(tags["attack"], big, model, glow, mouths, land, H.RINGS)
    meta = {"ppu": 1.8, "anchor": list(big), "dead_dy": dys, "dead2": {"scale": DEAD2_SCALE, "pivot": list(pivot)},
            "wing": {"tip": tip, "root": root, "rows": [int(wy.min()), int(wy.max())]}, "glow": list(glow),
            "mouths": [list(p) for p in mouths], "land": list(land), "durations": H.DRAKE_MS}
    return tags, meta


def build(model, review=None):
    tags, meta = frames_of(model)
    ppu = meta["ppu"]
    one, hd = {}, {}
    for t in ["idle", "base", "attack", "dead"]:
        per = meta["durations"].get(t)
        ms = [per[k] if per else H.DURATIONS.get(t, 80) for k in range(len(tags[t]))]
        pairs = [H.crop_pair(a, meta["anchor"], ppu) for a in tags[t]]
        hd["hd_" + t] = [(dd, m) for (dd, _), m in zip(pairs, ms)]
        one[t] = [(o, m) for (_, o), m in zip(pairs, ms)]
    W, Hh = H.G.write_sheet(os.path.join(H.OUT_DIR, NAMES[model]), {**one, **hd}, share=True)
    if review:
        os.makedirs(review, exist_ok=True)
        for t, frs in tags.items():
            for k, a in enumerate(frs):
                Image.fromarray(a).save(os.path.join(review, f"{model}_{t}_{k + 1}.png"))
    print(f"{NAMES[model]}: sheet {W}x{Hh}, PPU {ppu}, " + ", ".join(f"{t} {len(v)}" for t, v in one.items())
          + f"; idle {one['idle'][0][0].shape[1]}x{one['idle'][0][0].shape[0]} / hd_idle {hd['hd_idle'][0][0].shape[1]}"
          + f"; wing tip {meta['wing']['tip']} root {meta['wing']['root']} rows {meta['wing']['rows']}; dead dy {meta['dead_dy']}",
          flush=True)
    return meta


def main():
    global DIR
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frames", required=True, help="Codex 第 3 步的 dragons-rift 文件夹")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--review", default=None, help="每一帧整张（加了边的）也写到这里")
    a = ap.parse_args()
    DIR = a.frames
    for model in a.only or MODELS:
        build(model, a.review)


if __name__ == "__main__":
    main()
