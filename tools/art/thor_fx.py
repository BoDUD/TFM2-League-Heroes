#!/usr/bin/env python3
"""索尔的特效图按他身体的密度重出（assets/source/thor/rebuild/ragnarok_thor_fx_native#sheet.png / #anim.fanim）。

    python tools/art/thor_fx.py [--check]

为什么：Codex 照动画第一季重画的身体（assets/source/thor/rebuild）在格子里站高约 89 格，游戏里 PPU 2.67（33 个游戏像素），
特效图要和身体一样细，游戏里的大小才不变：原来 Codex 的 128 格是 1.65、我们的两倍重出是 3.3，这里是 2.67，倍数
UP = 2.67 / 1.65。做法照 Codex 6f4833f 的 build_pixel_v01.py（effects_from_grid、common_palette，我们 2026-11-21 的
两倍重出 thor_repixel.py 也是这样），格子和缩放乘 UP：每段特效从他的原画里按 4 x 4 切格，最近邻缩到 80 x UP 宽，摆在
一格正中（落在地上的两段：雷电、大招落地，九成高度那行对到脚底那行），七段一起量出 48 色。

飞出去的雷槌（hammer_flight）换成新画的锤子：rebuild/weapon_master.png（锤头 122 x 40）加上 Codex 在 weapons.py 里画的
短锤柄（深色柄、金色柄头，和他手里的、砸在地上的同一把），和身体同样密度，游戏里和手里的一样大；照原来那 8 帧转：每帧
逆时针 45 度、55 毫秒，绕锤头中心，最近邻（和 Codex 把锤子装到手上一样），颜色归到身体那张图的 64 色上（所以要在
tools/art/thor_rebuild_fix.py 之后跑）。

一格 CELL = round(128 x UP) 见方，一行一段，顺序、帧时长照 codex_v01 的特效表。tools/art/import_thor.py 的 FX_ORIGIN、
GROUND、PROJ_FX 是这一格里的点（格子中心、脚底那行）。原画在 Codex 第二轮补画的检出里（只读，环境变量 THOR_FX_CODEX
可以改）。--check 只重算一遍，和仓库里的比，不写文件。
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
THOR = os.path.join(ROOT, "assets", "source", "thor")
OUT = os.path.join(THOR, "rebuild", "ragnarok_thor_fx_native")
WEAPON = os.path.join(THOR, "rebuild", "weapon_master.png")
BODY = os.path.join(THOR, "rebuild", "ragnarok_thor_native")    # 先跑 tools/art/thor_rebuild_fix.py
TABLE = os.path.join(THOR, "codex_v01", "ragnarok_thor_fx_native#anim.fanim")
CODEX = os.environ.get("THOR_FX_CODEX",
                       r"D:\steam\steamapps\common\Teamfight Manager2\TeamFightMange2-mod-ragnarok-thor-req2")
SOURCE = os.path.join(CODEX, "design", "ragnarok_thor", "art", "pixel_v01", "source")

PPU = 2.67                  # 身体的密度（tools/art/import_thor.py 的 PPU）
UP = PPU / 1.65             # Codex 128 格的特效是 1.65
N, FOOT = 128, 116          # Codex 的格子、脚底那行
CELL = round(N * UP)
GROUND_ROW = round(FOOT * UP)
# 原画：每张 4 x 4 格，两段特效各 8 格
GROUPS = [("pixel_fx_melee", ("hammer_swing", "thunder_hit")),
          ("pixel_fx_skill_throw", ("ground_lightning", "hammer_flight")),
          ("pixel_fx_awakening_charge", ("hammer_awakening", "ult_charge")),
          ("pixel_fx_ult_impact", ("ult_slam", "ult_impact"))]
ON_GROUND = ("ground_lightning", "ult_impact")
SPIN = 8                    # 飞锤每圈 8 帧，每帧逆时针 45 度


def from_grid(im, ground, cols=4, rows=4):
    """build_pixel_v01.py 的 effects_from_grid：切格、去掉格边 10 像素、透明度只留 0 / 255，最近邻缩到 80 x UP 宽，
    摆在 CELL 见方的格子正中（落地的九成高度那行对到 GROUND_ROW）。"""
    frames = []
    for idx in range(cols * rows):
        c, r = idx % cols, idx // cols
        x0, x1 = round(c * im.width / cols), round((c + 1) * im.width / cols)
        y0, y1 = round(r * im.height / rows), round((r + 1) * im.height / rows)
        a = np.asarray(im.crop((x0, y0, x1, y1))).copy()
        guard = 10
        a[:guard, :, 3] = 0
        a[-guard:, :, 3] = 0
        a[:, :guard, 3] = 0
        a[:, -guard:, 3] = 0
        a[:, :, 3] = (a[:, :, 3] >= 96).astype(np.uint8) * 255
        a[a[:, :, 3] == 0, :3] = 0
        tile = Image.fromarray(a)
        s = 80 * UP / (im.width / cols)
        tile = tile.resize((max(1, round(tile.width * s)), max(1, round(tile.height * s))), Image.Resampling.NEAREST)
        f = Image.new("RGBA", (CELL, CELL))
        px = round((CELL - tile.width) / 2)
        py = round(GROUND_ROW - tile.height * .90) if ground else round((CELL - tile.height) / 2)
        f.paste(tile, (px, py))
        frames.append(f)
    return frames


def common_palette(frames, colors):
    samples = np.concatenate([np.asarray(f)[:, :, :3][np.asarray(f)[:, :, 3] > 0] for f in frames])
    palette = Image.fromarray(samples.reshape(1, -1, 3)).quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    out = []
    for f in frames:
        q = f.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE).convert("RGBA")
        q.putalpha(f.getchannel("A"))
        out.append(np.asarray(q))
    return out


def hammer():
    """锤头（weapon_master.png）加 Codex 画的短锤柄，122 x 54，锤头中心 (61, 20)：照 weapons.py 的 weapon('hammer')。"""
    full = Image.new("RGBA", (122, 54))
    d = ImageDraw.Draw(full)
    d.rectangle((57, 35, 64, 51), fill="#1a1922")
    d.rectangle((58, 40, 63, 48), fill="#5f5261")
    d.line((59, 41, 59, 48), fill="#978394")
    d.rectangle((57, 49, 64, 51), fill="#9d743d")
    d.line((58, 49, 63, 49), fill="#d9b173")
    full.alpha_composite(Image.open(WEAPON).convert("RGBA"))
    return full, (61, 20)


def flight():
    """飞锤 8 帧：整把锤子绕锤头中心逆时针转，每帧 45 度，锤头中心在格子正中（weapons.py 的 stamp，最近邻）。颜色归到
    身体那张图的色板上（tools/art/thor_rebuild_fix.py 收成的 64 色），和他手里的锤子同色。"""
    prop, (px, py) = hammer()
    body = np.asarray(Image.open(BODY + "#sheet.png").convert("RGBA"))
    pal = np.unique(body[body[..., 3] > 0][:, :3], axis=0).astype(np.float64)
    x = y = CELL / 2
    out = []
    for k in range(SPIN):
        t = -k * math.pi / 4
        c, s = math.cos(t), math.sin(t)
        f = prop.transform((CELL, CELL), Image.Transform.AFFINE, (c, s, px - c * x - s * y, -s, c, py + s * x - c * y),
                           Image.Resampling.NEAREST)
        a = np.array(f)
        a[a[..., 3] == 0] = 0
        op = a[..., 3] > 0
        rgb = a[op][:, :3].astype(np.float64)
        a[op, :3] = pal[((rgb[:, None, :] - pal[None]) ** 2).sum(-1).argmin(1)].astype(np.uint8)
        out.append(a)
    return out


def effects():
    fx = {}
    for stem, names in GROUPS:
        im = Image.open(os.path.join(SOURCE, stem + ".png")).convert("RGBA")
        for i, name in enumerate(names):
            if name == "hammer_flight":
                continue
            fx[name] = from_grid(im, name in ON_GROUND)[i * 8:(i + 1) * 8]
    order = list(fx)
    flat = common_palette([f for name in order for f in fx[name]], 48)
    out = {name: flat[j * 8:(j + 1) * 8] for j, name in enumerate(order)}
    out["hammer_flight"] = flight()
    return out


def sheet():
    """一行一段（照 codex_v01 特效表的顺序和帧时长），每格 CELL 见方。"""
    with open(TABLE, encoding="utf-8-sig") as f:
        table = json.load(f)["anims"]
    fx = effects()
    big = np.zeros((len(table) * CELL, 8 * CELL, 4), np.uint8)
    anims = {}
    for row, (tag, a) in enumerate(table.items()):
        frames = []
        for i, fr in enumerate(a["frames"]):
            x, y = i * CELL, row * CELL
            big[y:y + CELL, x:x + CELL] = fx[tag][i]
            frames.append({"duration": fr["duration"], "data": {"x": x, "y": y, "w": CELL, "h": CELL}})
        anims[tag] = {"frames": frames}
    return big, {"anims": anims}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="只重算，和仓库里的比")
    a = ap.parse_args()
    if not os.path.isdir(SOURCE):
        sys.exit(f"{SOURCE}: Codex 的特效原画不在（环境变量 THOR_FX_CODEX 指到他第二轮补画的检出）")
    img, fanim = sheet()
    text = json.dumps(fanim, ensure_ascii=False)
    if a.check:
        bad = 0
        if not os.path.isfile(OUT + "#sheet.png") or not np.array_equal(
                np.asarray(Image.open(OUT + "#sheet.png").convert("RGBA")), img):
            print(OUT + "#sheet.png differs")
            bad += 1
        if not os.path.isfile(OUT + "#anim.fanim") or open(OUT + "#anim.fanim", encoding="utf-8").read() != text:
            print(OUT + "#anim.fanim differs")
            bad += 1
        sys.exit(1 if bad else 0)
    Image.fromarray(img).save(OUT + "#sheet.png")
    with open(OUT + "#anim.fanim", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{OUT}#sheet.png {img.shape[1]}x{img.shape[0]}, cell {CELL}, ground row {GROUND_ROW}")


if __name__ == "__main__":
    main()
