#!/usr/bin/env python3
"""渊契（abysspact）英雄图集调色：只改颜色，不动形状和透明度。

    python tools/abysspact_recolor.py [--hero oathbreaker ...] [--out DIR]

为什么要调：原图是生成图缩成像素画，配色普遍发灰发糊——浅色英雄（骸弦、呓语、千蛾、烛灵）没有轮廓，
深色英雄（鸦医、血月、入殓、丧钟）糊成一团，设计书里每人一种的「深渊发光色」大半没画出来。
这里按设计书的配色给每个英雄做三件事：

1. 拉开明暗、调饱和度（近白近灰的像素不染色，骨头、白发、白衣保持干净）；
2. 按色相段把颜色换到设计书的色板上，尤其把发光色找回来（规则见 PARAMS）；
3. 最暗的一档统一成偏紫黑的轮廓色，并把剪影最外一圈压暗，按游戏里约 1 像素的宽度描边。

颜色映射对整张图集一视同仁，所以各个动作、形态、BP 小图的颜色是一致的。描边按帧来做：高清帧（hd_）
2 像素，其余 1 像素。

原图一律从 git 里 BASE 那一版读（调色前的最后一版），写到 abysspact/champions；所以改了参数直接重跑就行，
不会在调过的图上再调一遍。以后图集重画了，把 BASE 换成新图那一版再跑。
"""
import argparse
import colorsys
import io
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = Path(__file__).resolve().parents[1]
CHAMPIONS = REPO / "abysspact" / "champions"
# 调色前的最后一版（2026-11-24 22:22 的配色，main 5bc1a2c9f 时还是这一版）
BASE = "5bc1a2c9f"


def R(h, s_min=0.15, v_min=0.0, v_max=1.0, to=None, sat=None, s_mul=1.0, v=(1.0, 0.0)):
    """一条换色规则：色相落在 h=(起, 止) 段里（可跨 0），饱和度 ≥ s_min、明度在 [v_min, v_max] 的像素，
    色相换成 to（None = 不换），饱和度设成 sat 或乘 s_mul，明度按 v=(倍数, 加量) 变。"""
    return dict(h=h, s_min=s_min, v_min=v_min, v_max=v_max, to=to, sat=sat, s_mul=s_mul, v=v)


# 每个英雄：
#   tone=(反差, 亮度)：以中灰为轴拉开反差，再整体提或压；sat：整体饱和度倍数；
#   rules：按顺序套的换色规则（同一像素只吃第一条命中的）；
#   outline：轮廓色；edge：最外一圈压暗的力度（0~1）。
# 色相用 0~1：红 0、橙 0.08、黄 0.15、绿 0.33、青 0.5、蓝 0.62、紫 0.75、品红 0.85。
PARAMS = {
    # —— 第一批 ——
    # 断誓：盔甲回到冷钢灰，品红披风换成设计书的黑紫火，亮处是亮紫
    "oathbreaker": dict(tone=(1.15, -0.02), sat=1.0, outline="140A1A", edge=0.85, rules=[
        R((0.60, 0.80), s_min=0.10, to=0.64, s_mul=0.35, v=(0.78, -0.03)),
        R((0.84, 1.00), s_min=0.20, v_min=0.62, to=0.76, sat=0.42, v=(1.1, 0.05)),
        R((0.84, 1.00), s_min=0.20, to=0.76, sat=0.75, v=(1.0, 0.0)),
    ]),
    # 无面：黑风衣、深红衬里、瓷白脸；最亮的白偏冷，像惨白的光
    "faceless": dict(tone=(1.12, 0.0), sat=1.0, outline="0E0A10", edge=0.8, rules=[
        R((0.90, 1.02), s_min=0.25, to=0.975, sat=0.72, v=(0.95, 0.0)),
        R((0.0, 1.0), s_min=0.0, v_min=0.86, to=0.64, sat=0.05, v=(1.0, 0.04)),
    ]),
    # 呓语：灰袍里的粉紫换成疯狂紫，整体压暗一点让袍子成灰
    "whisperer": dict(tone=(1.28, -0.10), sat=1.1, outline="1C0A22", edge=0.95, rules=[
        R((0.80, 0.95), s_min=0.30, v_min=0.30, to=0.755, sat=0.70, v=(1.1, 0.06)),
        R((0.80, 0.95), s_min=0.12, to=0.72, s_mul=0.6),
    ]),
    # 骸弦：骨白不动，阴影里的灰紫换成魂火蓝和深蓝，弓和眼睛带青光
    "bonebow": dict(tone=(1.25, -0.10), sat=1.0, outline="141825", edge=1.0, rules=[
        R((0.66, 0.92), s_min=0.10, v_max=0.55, to=0.60, sat=0.55, v=(0.9, 0.0)),
        R((0.66, 0.92), s_min=0.10, to=0.54, sat=0.42, v=(1.05, 0.04)),
        R((0.45, 0.66), s_min=0.15, to=0.54, sat=0.65, v=(1.1, 0.08)),
    ]),
    # 鸦医：棕色大衣压成近黑，留一点皮革棕；黄绿、绿换成病绿发光
    "corvus": dict(tone=(1.12, -0.02), sat=0.9, outline="120A10", edge=0.8, rules=[
        R((0.14, 0.45), s_min=0.18, v_min=0.25, to=0.29, sat=0.85, v=(1.3, 0.14)),
        R((0.97, 0.14), s_min=0.15, v_max=0.62, to=0.03, s_mul=0.35, v=(0.62, -0.02)),
        R((0.97, 0.14), s_min=0.15, to=0.06, s_mul=0.6, v=(0.8, 0.0)),
    ]),
    # —— 第二批 ——
    # 血月：发灰的粉红换成血月红，暗的是深红；棕色外套稍微收一点饱和
    "bloodmoon": dict(tone=(1.15, 0.0), sat=1.0, outline="150A12", edge=0.85, rules=[
        R((0.90, 0.04), s_min=0.38, v_min=0.45, to=0.975, sat=0.82, v=(1.1, 0.05)),
        R((0.90, 0.04), s_min=0.38, to=0.97, sat=0.85, v=(0.85, 0.0)),
        R((0.04, 0.14), s_min=0.20, s_mul=0.8),
    ]),
    # 入殓：黑外套、铁箍、银钉；偏紫的冷灰换成引魂灯的灰蓝光
    "undertaker": dict(tone=(1.18, -0.04), sat=1.0, outline="100A12", edge=0.85, rules=[
        R((0.66, 0.98), s_min=0.22, v_min=0.74, to=0.58, sat=0.40, v=(1.1, 0.08)),
        R((0.66, 0.98), s_min=0.0, to=0.68, s_mul=0.3, v=(0.88, -0.02)),
    ]),
    # 替身：红线回到正红，补丁、纽扣的紫压暗一点
    "effigy": dict(tone=(1.12, 0.0), sat=1.05, outline="12060E", edge=0.8, rules=[
        R((0.91, 0.99), s_min=0.30, to=0.965, sat=0.85, v=(1.1, 0.04)),
        R((0.83, 0.91), s_min=0.20, s_mul=0.7, v=(0.9, 0.0)),
    ]),
    # 七弹：发黄的猎装换成墨绿，红色是魔弹的深渊红
    "sevenfold": dict(tone=(1.15, 0.0), sat=1.0, outline="100A0C", edge=0.85, rules=[
        R((0.96, 0.03), s_min=0.40, v_min=0.40, to=0.985, sat=0.82, v=(1.15, 0.08)),
        R((0.06, 0.18), s_min=0.35, s_mul=0.75),
    ]),
    # 烛灵：粉白长袍换成淡紫，红橙的烛火换成暖金和橙
    "vesper": dict(tone=(1.18, -0.06), sat=1.05, outline="1E0C22", edge=0.95, rules=[
        R((0.84, 0.95), s_min=0.12, to=0.74, s_mul=0.85),
        R((0.95, 0.12), s_min=0.30, v_min=0.55, to=0.10, sat=0.70, v=(1.15, 0.10)),
        R((0.95, 0.12), s_min=0.30, to=0.06, sat=0.75),
    ]),
    # —— 第三批 ——
    # 蜕甲：青色亮处是深渊青光，红点收成铁锈
    "carapace": dict(tone=(1.15, 0.0), sat=1.0, outline="06100F", edge=0.8, rules=[
        R((0.40, 0.56), s_min=0.30, v_min=0.72, to=0.465, sat=0.80, v=(1.12, 0.06)),
        R((0.40, 0.56), s_min=0.0, to=0.47, s_mul=0.6, v=(0.72, -0.03)),
        R((0.94, 0.04), s_min=0.25, to=0.04, s_mul=0.55),
    ]),
    # 附骨：亮的品红是发光的血管，斗篷的紫压成暗灰紫
    "leech": dict(tone=(1.15, -0.02), sat=1.0, outline="120A14", edge=0.85, rules=[
        R((0.78, 0.95), s_min=0.40, v_min=0.74, to=0.87, sat=0.75, v=(1.15, 0.08)),
        R((0.78, 0.95), s_min=0.0, to=0.78, s_mul=0.35, v=(0.85, -0.02)),
    ]),
    # 千蛾：偏橙的眼斑换成余烬橙，裙子压暗成灰褐，让人有个形
    "noctua": dict(tone=(1.30, -0.12), sat=1.0, outline="1E1410", edge=1.0, rules=[
        R((0.97, 0.10), s_min=0.45, v_min=0.55, to=0.06, sat=0.88, v=(1.15, 0.08)),
        R((0.97, 0.14), s_min=0.08, v_max=0.62, to=0.08, s_mul=0.6, v=(0.8, -0.04)),
    ]),
    # 沉锚：蓝紫换成藏青外套，最亮的蓝是深海电蓝
    "anchor": dict(tone=(1.15, 0.0), sat=1.0, outline="080A14", edge=0.85, rules=[
        R((0.58, 0.78), s_min=0.35, v_min=0.78, to=0.615, sat=0.80, v=(1.12, 0.08)),
        R((0.58, 0.78), s_min=0.0, to=0.63, s_mul=0.62, v=(0.78, -0.03)),
    ]),
    # 返照：品红紫外套换成墨紫，粉红亮处是暮光玫瑰，橙是黄铜（头发三档的黑灰白不动）
    "hourglass": dict(tone=(1.12, 0.0), sat=1.0, outline="140C1C", edge=0.85, rules=[
        R((0.90, 1.0), s_min=0.30, v_min=0.55, to=0.955, sat=0.62, v=(1.12, 0.06)),
        R((0.80, 0.92), s_min=0.15, to=0.73, s_mul=0.6, v=(0.9, 0.0)),
        R((0.03, 0.12), s_min=0.30, to=0.11, s_mul=0.85),
    ]),
    # —— 第四批 ——
    # 缓刑：皮肤的橙收成正常肤色，囚衣、铁更冷更灰
    "reprieve": dict(tone=(1.15, 0.0), sat=1.0, outline="161010", edge=0.8, rules=[
        R((0.02, 0.12), s_min=0.30, to=0.07, s_mul=0.6, v=(1.0, 0.02)),
    ]),
    # 赊命：偏紫的点换成深靛命火，整体提一点亮度免得看不清
    "debtor": dict(tone=(1.12, 0.04), sat=1.0, outline="0E0C14", edge=0.85, rules=[
        R((0.66, 0.80), s_min=0.30, v_min=0.50, to=0.68, sat=0.78, v=(1.25, 0.10)),
    ]),
    # 无痕：白外套保持干净，只拉开明暗、加描边
    "traceless": dict(tone=(1.18, -0.02), sat=1.0, outline="121016", edge=1.0, rules=[]),
    # 陨夜：蓝斗篷更深，最亮的白偏冷，像星光
    "starfall": dict(tone=(1.12, 0.0), sat=1.0, outline="0A0A18", edge=0.85, rules=[
        R((0.58, 0.76), s_min=0.20, to=0.64, s_mul=1.05, v=(0.92, 0.0)),
        R((0.0, 1.0), s_min=0.0, v_min=0.84, to=0.62, sat=0.07, v=(1.0, 0.04)),
    ]),
    # 丧钟：钟上偏青的纹路是铜绿光，棕色收成青铜
    "knell": dict(tone=(1.15, 0.0), sat=1.0, outline="0E0C10", edge=0.85, rules=[
        R((0.30, 0.58), s_min=0.08, v_min=0.35, to=0.42, sat=0.62, v=(1.2, 0.10)),
        R((0.02, 0.12), s_min=0.25, to=0.09, s_mul=0.75),
    ]),
    # 骸弦的骷髅兵跟着骸弦走
    "skeleton": dict(tone=(1.2, -0.06), sat=1.0, outline="141825", edge=1.0, rules=[
        R((0.45, 0.66), s_min=0.15, to=0.54, sat=0.65, v=(1.1, 0.08)),
    ]),
}


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def in_band(h, band):
    lo, hi = band
    return (h >= lo) & (h <= hi) if lo <= hi else (h >= lo) | (h <= hi)


def map_colors(cols, p):
    """一批颜色（N×3，0~1）按英雄参数换色，返回新颜色。"""
    hsv = np.array([colorsys.rgb_to_hsv(*c) for c in cols])
    h, s, v = hsv[:, 0].copy(), hsv[:, 1].copy(), hsv[:, 2].copy()
    h0, s0, v0 = h.copy(), s.copy(), v.copy()
    k, b = p["tone"]
    v = np.clip((v - 0.5) * k + 0.5 + b, 0, 1)
    s = np.where(s > 0.08, np.clip(s * p["sat"], 0, 0.95), s)
    done = np.zeros(len(cols), bool)
    for r in p["rules"]:
        m = ~done & in_band(h0, r["h"]) & (s0 >= r["s_min"]) & (v0 >= r["v_min"]) & (v0 <= r["v_max"])
        if r["to"] is not None:
            h = np.where(m, r["to"], h)
        if r["sat"] is not None:
            s = np.where(m, r["sat"], s)
        s = np.where(m, np.clip(s * r["s_mul"], 0, 0.95), s)
        vm, vb = r["v"]
        v = np.where(m, np.clip(v * vm + vb, 0, 1), v)
        done |= m
    out = np.array([colorsys.hsv_to_rgb(*c) for c in np.stack([h, s, v], 1)])
    lum = out @ np.array([0.299, 0.587, 0.114])
    out[lum < 0.11] = hexrgb(p["outline"])
    return out


def git_bytes(rev, rel):
    return subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=REPO, check=True, capture_output=True).stdout


def frame_rects(fanim_bytes):
    """图集里每一帧的矩形和描边宽度（高清帧 2 像素，其余 1 像素；同一矩形取大的）。"""
    d = json.loads(fanim_bytes.decode("utf-8"))
    rects = {}
    for tag, anim in d["anims"].items():
        width = 2 if tag.startswith("hd_") else 1
        for fr in anim["frames"]:
            f = fr["data"]
            key = (int(f["x"]), int(f["y"]), int(f["w"]), int(f["h"]))
            rects[key] = max(rects.get(key, 0), width)
    return rects


def recolor_sheet(sheet_bytes, fanim_bytes, p):
    img = Image.open(io.BytesIO(sheet_bytes)).convert("RGBA")
    a = np.array(img)
    rgb = a[:, :, :3].astype(np.float32) / 255
    solid = a[:, :, 3] > 0
    # 换色：按颜色查表，整张图集一致
    cols, inv = np.unique(rgb[solid], axis=0, return_inverse=True)
    newc = map_colors(cols, p)
    out = rgb.copy()
    out[solid] = newc[inv.reshape(-1)]
    # 描边：每帧剪影最外一圈压向轮廓色
    oc = hexrgb(p["outline"])
    e = p["edge"]
    for (x, y, w, h), width in frame_rects(fanim_bytes).items():
        m = solid[y:y + h, x:x + w]
        if not m.any():
            continue
        pad = np.pad(m, width)
        inner = ndimage.binary_erosion(pad, iterations=width)[width:-width, width:-width]
        ring = m & ~inner
        sub = out[y:y + h, x:x + w]
        sub[ring] = sub[ring] * (1 - e) + oc * e
    res = a.copy()
    res[:, :, :3] = np.where(solid[:, :, None], (out * 255).round().astype(np.uint8), a[:, :, :3])
    return Image.fromarray(res, "RGBA")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hero", action="append", help="只调这几个（默认全部）")
    ap.add_argument("--base", default=BASE, help="从 git 的哪一版读原图（默认 BASE）")
    ap.add_argument("--out", default=str(CHAMPIONS), help="写到哪里（默认 abysspact/champions）")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for hero in args.hero or list(PARAMS):
        sheet = f"abysspact_{hero}#sheet.png"
        fanim = f"abysspact_{hero}#anim.fanim"
        fanim_bytes = git_bytes(args.base, f"abysspact/champions/{fanim}")
        img = recolor_sheet(git_bytes(args.base, f"abysspact/champions/{sheet}"), fanim_bytes, PARAMS[hero])
        img.save(out / sheet, optimize=True)
        if out != CHAMPIONS:
            (out / fanim).write_bytes(fanim_bytes)
        print(f"{hero:12s} -> {out / sheet}")


if __name__ == "__main__":
    main()
