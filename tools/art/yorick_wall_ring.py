#!/usr/bin/env python3
"""约里克 2026-11-22 新加的几段特效，全用他自己特效表里已有的图拼（不找 Codex）：暗灵缠身的整圈墙、跟着他的室女、
室女的魂弹和标记。写回 league/effects/league_yorick_big 和 league_yorick_fx（1 倍帧和 hd_ 帧各一套，别的 tag 逐像素不变）。

    python tools/art/yorick_wall_ring.py [--check] [--review DIR]

在 import_yorick_fx.py（和 densify_fx.py 的 hd_ 帧）之后跑；它只读那两张表里现有的 tag，自己的 tag 每次重拼（跑几遍一样）。

暗灵缠身（用户：「没有那个地形框出来的技能」）：英雄联盟的墙是一圈 18 段鬼魂。这里的墙线半径 R = 30 格（数据的 w_r 30000，
1 格 = 1000），18 段，每段是抓脚鬼手 `w_hit` 里的一个小鬼（左半边那个；圈的右半边用它的镜像，整圈左右对称），脚踩在
地面的圆上——地面在挂点下面 11 格（hd.rs FEET，单位的脚也在这儿），地面没有透视压扁（引擎里位置 1:1 画），所以是正圆。
小鬼按脚的上下排前后（后面的先画）。
  w_ring_up   落地时放（1 秒）：地上一圈青色亮点（鬼手闪光帧里的青，250 ms）→ 亮点 + 土里冒出的小鬼头（`w_hit` 第 0 帧，250 ms）→ 小鬼头（250 ms）
              → 小鬼站起来（第 1 帧，250 ms；数据在落地后 w_delay = 45 tick 立墙，正好在这一帧开始）
  w_ring      站着（0.5 秒一段，数据每 30 tick 放一段）：单数段第 1 帧、双数段第 2 帧，250 ms 后互换，整圈在扭动
  w_ring_fall 塌掉（340 ms）：第 3 帧（发白的闪光）→ 第 0 帧（缩回土里）→ 一圈亮点
画在单位下面（z -1）。前后遮挡：小鬼只有 12 格高，人在圈里时中心离圆心最多 20 格（墙线 30 - 半厚 10），圈外的至少 40 格，
所以圈里的人脚离前墙最高处、圈外的人脚离后墙最高处都还差不多 1–2 格——整圈画在人下面，前后都对得上（不用拆前后两层）。
hd_ 帧照同样的位置用 hd_w_hit 的小鬼拼（2 倍）。

室女跟着他（数据的 r_rise / r_follow 在约里克身上播）：`r_spawn` / `r_maiden` 原样往上挪 FOLLOW_UP 格（她浮在他身后上方，
画在他下面）。魂弹（r_bolt，飞的时候按方向转）：`r_mark` 第 0 帧那个紫色小椭圆，裁到有画的部分、居中（上下对称）。
她的标记（r_mkv，挂在被打中的英雄头上）：`r_mark` 第 1 帧那个紫圈，放在哀伤之雾的标记（e_mark，头顶 28 格）再往上
MARK_UP 格，两个标记同时在也不叠。
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

FX_DIR = os.path.join(ROOT, "league", "effects")
BIG, FX = "league_yorick_big", "league_yorick_fx"
R = 30              # 墙线半径（格），数据的 w_r / 1000
SEGS = 18           # 英雄联盟的段数
FEET = 11           # 地面在挂点下面几格
FOLLOW_UP = 8       # 室女跟着他时往上挪几格
MARK_UP = 14        # 她的标记比哀伤之雾的标记高几格（e_mark 的底在头顶 28 格）
OVER = 28
NEW_BIG = ("w_ring_up", "w_ring", "w_ring_fall", "r_rise", "r_follow")
NEW_FX = ("r_bolt", "r_mkv")


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def load(sheet):
    """{tag: [(rgba array, ms), ...]} in the file's tag order."""
    with open(lp(os.path.join(FX_DIR, sheet + "#anim.fanim")), encoding="utf-8-sig") as f:
        anims = json.load(f)["anims"]
    img = np.asarray(Image.open(lp(os.path.join(FX_DIR, sheet + "#sheet.png"))).convert("RGBA"))
    out = {}
    for tag, a in anims.items():
        fr = []
        for f in a["frames"]:
            q = f["data"]
            x, y, w, h = int(q["x"]), int(q["y"]), int(q["w"]), int(q["h"])
            fr.append((img[y:y + h, x:x + w].copy(), round(f["duration"] * 1000)))
        out[tag] = fr
    return out


def bbox(a):
    ys, xs = np.nonzero(a[..., 3])
    return xs.min(), xs.max(), ys.min(), ys.max()


def crop(a):
    x0, x1, y0, y1 = bbox(a)
    return a[y0:y1 + 1, x0:x1 + 1].copy()


def ghost(frame):
    """`w_hit` 一帧里左边那个小鬼（两个小鬼左右镜像，中间一列空着）：裁到有画的部分。"""
    w = frame.shape[1]
    left = frame[:, :w // 2]
    return crop(left)


def stamp(canvas, sprite, foot):
    """把 sprite 的脚（最底一行的中间）放在 canvas 的 foot（x, y）上，透明的地方不盖。"""
    h, w = sprite.shape[:2]
    x0, y0 = foot[0] - w // 2, foot[1] - h + 1
    for yy in range(h):
        for xx in range(w):
            if sprite[yy, xx, 3]:
                Y, X = y0 + yy, x0 + xx
                if 0 <= Y < canvas.shape[0] and 0 <= X < canvas.shape[1]:
                    canvas[Y, X] = sprite[yy, xx]


def feet(s):
    """18 段的脚，s 倍：(段号, x, y)，按 y 从后往前排。挂点在画布中间。角度从正下方偏 10 度起（左右对称、正中没有一段）。"""
    out = []
    for k in range(SEGS):
        t = math.radians(100 + 360 * k / SEGS)
        out.append((k, round(s * R * math.cos(t)), round(s * (FEET + R * math.sin(t)))))
    return sorted(out, key=lambda v: (v[2], v[1]))


def ring_frame(s, seg_for, dots=None, line=None):
    """一帧墙环（s 倍）：seg_for(k, x) -> 这一段画什么小鬼（或 None）；dots: 亮点的颜色；line: 地上那一圈裂缝的颜色
    （None 不画）。"""
    half_w, half_h = s * (R + 7), s * (FEET + R + 3)
    canvas = np.zeros((2 * half_h + 1, 2 * half_w + 1, 4), np.uint8)
    cx, cy = half_w, half_h
    if line is not None:
        # 一圈 s 格粗的地缝：圆上每一格（按角度细分，不漏格）
        for i in range(int(2 * math.pi * R * s * 4)):
            t = 2 * math.pi * i / int(2 * math.pi * R * s * 4)
            x, y = cx + round(s * R * math.cos(t)), cy + round(s * (FEET + R * math.sin(t)))
            canvas[y:y + s, x - s // 2:x - s // 2 + s] = line
    for k, x, y in feet(s):
        if dots is not None:
            for dx in range(-s, s):
                for dy in range(0, s):
                    canvas[cy + y - dy, cx + x + dx] = dots
        g = seg_for(k, x)
        if g is not None:
            stamp(canvas, g, (cx + x, cy + y))
    return canvas


def cyan(frames):
    """这些帧里最青的不透明颜色（蓝绿减红最多：鬼手闪光的那种青），地上亮点用它。"""
    best, key = None, -1
    for a in frames:
        px = a[a[..., 3] > 0]
        for c in {tuple(v) for v in px.tolist()}:
            k = min(c[1], c[2]) - c[0]
            if k > key:
                best, key = c, k
    return np.array(best, np.uint8)


def darkest(frames):
    """这些帧里最暗的不透明颜色（小鬼的底色），地缝用它。"""
    px = np.concatenate([a[a[..., 3] > 0][:, :3] for a in frames])
    return np.append(px[np.argmin(px.astype(int).sum(axis=1))], 255).astype(np.uint8)


def shift(a, up):
    """整帧往上挪 up 格：底下补 2*up 行透明（帧是居中画的，补一行内容就上去半格）。"""
    pad = np.zeros((2 * up, a.shape[1], 4), np.uint8)
    return np.concatenate([a, pad], axis=0)


def centred(a, up=0):
    """裁到有画的部分，宽高都是单数（以中间那格为中心），再往上挪 up 格。"""
    c = crop(a)
    h, w = c.shape[:2]
    if w % 2 == 0:
        c = np.concatenate([c, np.zeros((h, 1, 4), np.uint8)], axis=1)
    if c.shape[0] % 2 == 0:
        c = np.concatenate([c, np.zeros((1, c.shape[1], 4), np.uint8)], axis=0)
    return shift(c, up) if up else c


def build(big, fx):
    """新 tag：{sheet: {tag: [(array, ms)], 'hd_'+tag: [...]}}。"""
    out = {BIG: {}, FX: {}}
    for s, pre in ((1, ""), (2, "hd_")):
        hit = [a for a, _ in fx[pre + "w_hit"]]
        g = [ghost(a) for a in hit]
        gm = [x[:, ::-1] for x in g]
        dot = cyan(hit[3:4])
        crack = darkest(hit[1:2])

        def side(f):
            return lambda k, x: (g[f] if x < 0 else gm[f])

        def alt(a, b):
            return lambda k, x: (g if x < 0 else gm)[a if k % 2 else b]
        up = [(ring_frame(s, lambda k, x: None, dot), 250), (ring_frame(s, side(0), dot, crack), 250),
              (ring_frame(s, side(0), None, crack), 250), (ring_frame(s, side(1), None, crack), 250)]
        stand = [(ring_frame(s, alt(1, 2), None, crack), 250), (ring_frame(s, alt(2, 1), None, crack), 250)]
        fall = [(ring_frame(s, side(3), None, crack), 100), (ring_frame(s, side(0), None, crack), 120),
                (ring_frame(s, lambda k, x: None, dot), 120)]
        out[BIG][pre + "w_ring_up"] = up
        out[BIG][pre + "w_ring"] = stand
        out[BIG][pre + "w_ring_fall"] = fall
        out[BIG][pre + "r_rise"] = [(shift(a, s * FOLLOW_UP), ms) for a, ms in big[pre + "r_spawn"]]
        out[BIG][pre + "r_follow"] = [(shift(a, s * FOLLOW_UP), ms) for a, ms in big[pre + "r_maiden"]]
        mark = [a for a, _ in fx[pre + "r_mark"]]
        out[FX][pre + "r_bolt"] = [(centred(mark[0]), 80)]
        ring = centred(mark[1])
        # 头顶：底边在 OVER + MARK_UP 格高处（帧居中画：内容往上挪 半高 + 那么高）
        out[FX][pre + "r_mkv"] = [(shift(ring, ring.shape[0] // 2 + s * (OVER + MARK_UP)), 150)]
    return out


def merged(old, new):
    """旧表的 tag 原样（顺序不变，去掉上一次拼的），新 tag 接在后面：1 倍的在前，hd_ 的在后。"""
    keep = {t: v for t, v in old.items() if t not in new}
    plain = {t: v for t, v in new.items() if not t.startswith("hd_")}
    dense = {t: v for t, v in new.items() if t.startswith("hd_")}
    return {**keep, **plain, **dense}


def same(a, b):
    return set(a) == set(b) and all(len(a[t]) == len(b[t]) and all(x.shape == y.shape and (x == y).all() and m == n
                                                                    for (x, m), (y, n) in zip(a[t], b[t])) for t in a)


def review(new, folder):
    os.makedirs(lp(folder), exist_ok=True)
    for sheet, tags in new.items():
        for tag, frames in tags.items():
            for z in ((3, 6) if not tag.startswith("hd_") else (3,)):
                W = sum(a.shape[1] + 3 for a, _ in frames)
                H = max(a.shape[0] for a, _ in frames)
                img = Image.new("RGBA", (W, H), (58, 66, 58, 255))
                x = 0
                for a, _ in frames:
                    img.alpha_composite(Image.fromarray(a), (x, H - a.shape[0]))
                    x += a.shape[1] + 3
                img.resize((W * z, H * z), Image.NEAREST).save(lp(os.path.join(folder, f"{tag}_x{z}.png")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when the sheets are not what this writes")
    ap.add_argument("--review", help="each new tag's frames at 3x / 6x into this folder")
    a = ap.parse_args()
    big, fx = load(BIG), load(FX)
    new = build(big, fx)
    sheets = {BIG: merged(big, new[BIG]), FX: merged(fx, new[FX])}
    if a.check:
        bad = [s for s, tags in sheets.items() if not same(tags, load(s))]
        if bad:
            sys.exit(f"not as tools/art/yorick_wall_ring.py writes them: {bad}")
        print("ok")
        return
    for sheet, tags in sheets.items():
        w, h = G.write_sheet(lp(os.path.join(FX_DIR, sheet)), tags, share=True)
        back = load(sheet)
        if not same(tags, back):
            sys.exit(f"{sheet}: read back differs from what was written")
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v)}ms" for t, v in new[sheet].items()))
    if a.review:
        review(new, a.review)
        print("review", a.review)


if __name__ == "__main__":
    main()
