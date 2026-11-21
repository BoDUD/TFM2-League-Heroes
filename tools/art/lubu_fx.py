#!/usr/bin/env python3
"""吕布的特效图按两倍密度重出：assets/source/lubu/rebuild/ragnarok_lubu_fx_native（#sheet.png + #anim.fanim）。

    python tools/art/lubu_fx.py [--check]

身体是 Codex 照动画第一季重画的两倍帧（一格 256，脚底点 (128, 232)），特效没重画，要和身体一样密：照 Codex 自己的
build_pixel_v02.py 那一段（effects_from_grid、common_palette）从原画重出，格子、缩放、脚底线都乘 2。原画一格对
两倍格子的一格，像素和身体一样细。天喰斩波（codex_req1/ragnarok_lubu_wave_native）游戏里是 1 倍的弹道图，不在这里。

原画在游戏目录下 Codex 的检出里（00d78f3，只读，不在仓库里）。格子排法、每格时长照 codex_v02 那张特效图，坐标乘 2。
--check 只重算一遍，和仓库里的两张比，不写文件。tools/art/import_lubu.py 读它。
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LUBU = os.path.join(ROOT, "assets", "source", "lubu")
CODEX_FX = os.path.join(LUBU, "codex_v02", "ragnarok_lubu_fx_native")       # 排法照这张
OUT = os.path.join(LUBU, "rebuild", "ragnarok_lubu_fx_native")
SOURCE = os.path.join("D:/steam/steamapps/common/Teamfight Manager2", "TeamFightMange2-mod-ragnarok-lubu", "design",
                      "ragnarok_lubu", "art", "pixel_v02", "source")
UP = 2
# Codex 的格子和脚底线；原画一张四个特效，两个一组（每张 4 x 4 格，前 8 格一个、后 8 格一个）
CELL, FOOT = 128, 116
FX_GROUPS = [("pixel_fx_melee", ("attack_swipe", "hit_spark")), ("pixel_fx_skills", ("sweep", "thrust")),
             ("pixel_fx_ultimate", ("ult_charge", "ult_release")), ("pixel_fx_impacts", ("ult_impact", "shield_break"))]


def effects_from_grid(im, up, cols=4, rows=4, ground=False):
    """Codex 的 effects_from_grid 按 up 倍：每格抠出来（不透明度 96 以上算有），最近邻缩到 80*up 宽的比例，摆在格子
    正中；地上的（ult_impact）底边摆在脚底线上。"""
    cell, foot = round(CELL * up), FOOT * up
    frames = []
    for idx in range(cols * rows):
        c, r = idx % cols, idx // cols
        x0, x1 = round(c * im.width / cols), round((c + 1) * im.width / cols)
        y0, y1 = round(r * im.height / rows), round((r + 1) * im.height / rows)
        a = np.asarray(im.crop((x0, y0, x1, y1))).copy()
        a[:, :, 3] = (a[:, :, 3] >= 96).astype(np.uint8) * 255
        a[a[:, :, 3] == 0, :3] = 0
        tile = Image.fromarray(a)
        k = 80 * up / (im.width / cols)
        tile = tile.resize((max(1, round(tile.width * k)), max(1, round(tile.height * k))), Image.Resampling.NEAREST)
        f = Image.new("RGBA", (cell, cell))
        px = round((cell - tile.width) / 2)
        py = round(foot - tile.height * .90) if ground else round((cell - tile.height) / 2)
        f.paste(tile, (px, py))
        frames.append(f)
    return frames


def common_palette(frames, colors):
    """Codex 的 common_palette：全部特效帧一起中位切分成 colors 色，不抖动。"""
    samples = np.concatenate([np.asarray(f)[:, :, :3][np.asarray(f)[:, :, 3] > 0] for f in frames])
    pal = Image.fromarray(samples.reshape(1, -1, 3)).quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    out = []
    for f in frames:
        q = f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE).convert("RGBA")
        q.putalpha(f.getchannel("A"))
        out.append(q)
    return out


def effects(up):
    """{特效: [8 帧 RGBA]}：天喰斩击用 pixel_fx_release_fix 那张（4 x 2 格），放大 1.65 倍摆在格子正中；最后全部特效
    一起取 48 色。都照 Codex 的做法。"""
    fx = {}
    for stem, names in FX_GROUPS:
        im = Image.open(os.path.join(SOURCE, stem + ".png")).convert("RGBA")
        for i, name in enumerate(names):
            fx[name] = effects_from_grid(im, up, ground=name == "ult_impact")[i * 8:i * 8 + 8]
    cell = round(CELL * up)
    fx["ult_release"] = []
    for f in effects_from_grid(Image.open(os.path.join(SOURCE, "pixel_fx_release_fix.png")).convert("RGBA"), up, 4, 2):
        big = f.resize((round(cell * 1.65), round(cell * 1.65)), Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", (cell, cell))
        canvas.paste(big, ((cell - big.width) // 2, (cell - big.height) // 2))
        fx["ult_release"].append(canvas)
    order = [n for _, names in FX_GROUPS for n in names]
    flat = common_palette([f for n in order for f in fx[n]], 48)
    return {n: [np.asarray(f) for f in flat[k * 8:(k + 1) * 8]] for k, n in enumerate(order)}


def sheet_of(frames, codex, up):
    """照 Codex 那张图的排法放大 up 倍：每格换成重出的帧，#anim.fanim 的坐标跟着乘 up，时长不动。"""
    old = Image.open(codex + "#sheet.png")
    sheet = np.zeros((round(old.height * up), round(old.width * up), 4), np.uint8)
    with open(codex + "#anim.fanim", encoding="utf-8-sig") as f:
        fanim = json.load(f)
    for tag, a in fanim["anims"].items():
        for i, fr in enumerate(a["frames"]):
            d = fr["data"]
            for k in ("x", "y", "w", "h"):
                d[k] = round(d[k] * up)
            x, y, w, h = (int(d[k]) for k in ("x", "y", "w", "h"))
            sheet[y:y + h, x:x + w] = frames[tag][i][:h, :w]
    return sheet, fanim


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="只比，不写")
    a = ap.parse_args()
    if not os.path.isdir(SOURCE):
        sys.exit(f"找不到 Codex 的原画：{SOURCE}")
    sheet, fanim = sheet_of(effects(UP), CODEX_FX, UP)
    text = json.dumps(fanim, ensure_ascii=False)
    if a.check:
        bad = []
        p = OUT + "#sheet.png"
        if not os.path.isfile(p) or not np.array_equal(np.asarray(Image.open(p).convert("RGBA")), sheet):
            bad.append(p)
        p = OUT + "#anim.fanim"
        if not os.path.isfile(p) or open(p, encoding="utf-8").read() != text:
            bad.append(p)
        for p in bad:
            print(p, "不一样：跑一遍 python tools/art/lubu_fx.py")
        sys.exit(1 if bad else 0)
    Image.fromarray(sheet).save(OUT + "#sheet.png")
    with open(OUT + "#anim.fanim", "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(OUT + "#sheet.png", sheet.shape[1], "x", sheet.shape[0])


if __name__ == "__main__":
    main()
