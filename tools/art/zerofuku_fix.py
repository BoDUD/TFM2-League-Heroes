#!/usr/bin/env python3
"""零福／波旬（ragnarok_zerofuku）Codex 交的图：常态重贴斧爻，再和波旬、特效一起收色。

    python tools/art/zerofuku_fix.py            # 读 assets/source/zerofuku 的 bare/、runtime/，写 assets/source/zerofuku/snapped
    python tools/art/zerofuku_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_zerofuku.py、ppu_hd.py --hero zerofuku、hero_reels.py --hero zerofuku

Codex 2026-11-22 交的（zerofuku_packs/outputs/zerofuku_assets_done.zip，之后它又提交了一次 e8ff128fd「握柄那只空手露在斧柄上面」，
以提交为准）：一格 256，脚底 (128, 232)，常态 8 个动作、波旬 8 个动作（h_*）各 8 帧，特效八组各 8 帧。

斧爻（用户：「如果武器有歪的地方你可以帮忙修复一下」）。Codex 的常态每一帧是空手握拳的身体（bare/，tools/art/zerofuku_bare.py
从它的工作目录取出来的）贴上一把横着画的斧子（runtime/props/misery_cleaver.png；axe-registration.json 记着每帧的握点、角度、
长度、握在斧柄的哪里、斧刃放大几倍），握柄的手再从身体那层盖回斧柄上面。这里照它的做法（它的 rigid_axe.py）重贴，改两处：
- 长度：为了把斧子塞进 256 的格子，它有几帧把整把斧子缩短了（Q 落斧那两帧 90、91，变身前蹲下 95，跑步 103，Q 别的帧 101-109），
  斧柄跟着一会儿长一会儿短。这里一律 LENGTH（待机的 107），常态的格子放宽到 WIDE（只有 Q 落斧那两帧伸出 256，到 261）。
- 待机第 4 帧（LOCK）：画的两只手让斧子比前后两帧平了 3 度多，一循环斧头往下点一下。这一帧用前后两帧的角度，还是从握柄那只
  手出去；上面那只手离斧柄的中线 2 个像素，还握在手里。
Q 里斧刃放大（第 3-6 帧 1.18-1.35 倍，斧柄和斧头的接点不动）是 Codex 照原作画的：斧爻吸了不幸变大。不改。
重贴之前先验一遍：按 Codex 的原表、256 的格子贴回去，64 帧要和它交的一模一样（不一样说明这里的做法和它的对不上，不往下走）。

收色和别的英雄一样（tools/art/kojiro_fix.py 有来由）：两个形态合起来 64 色（同一套调色板，变身时颜色不跳），特效每组 32 色。
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

Z = os.path.join(ROOT, "assets", "source", "zerofuku")
SRC = os.path.join(Z, "runtime", "sprites")
OUT = os.path.join(Z, "snapped")
BARE = os.path.join(Z, "bare", "ragnarok_zerofuku_bare_native")
DELIVERED = os.path.join(SRC, "ragnarok_zerofuku_native")
PROP = os.path.join(Z, "runtime", "props", "misery_cleaver.png")
REG = os.path.join(Z, "axe-registration.json")
MAIN = "ragnarok_zerofuku_native"
HAJUN = "ragnarok_zerofuku_hajun_native"
FX = "ragnarok_zerofuku_fx_native"
NEAR = Image.Resampling.NEAREST
CELL, FOOT = 256, 232
WIDE = 272                  # 重贴以后常态一格的宽：右边多出来的给伸出去的斧头
LENGTH = 107                # 斧子全长，每帧一样（待机的长度）
LOCK = {("idle", 3): -32.5}  # 待机第 4 帧的角度（前后两帧是 -32.5）


def grown(prop, axis, blade):
    """斧刃放大 blade 倍：斧柄不动，从接点（全长 0.55 处）往后的斧头放大，中线对齐。"""
    if blade == 1:
        return prop, axis
    socket = round(.55 * prop.width)
    handle = prop.crop((0, 0, socket, prop.height))
    head = prop.crop((socket, 0, prop.width, prop.height))
    big = head.resize((round(head.width * blade), round(head.height * blade)), NEAR)
    extent = math.ceil(prop.height * max(1, blade))
    big_axis = round(axis * max(1, blade))
    out = Image.new("RGBA", (socket + big.width, extent + 3))
    out.paste(handle, (0, round(big_axis - axis)))
    out.paste(big, (socket, round(big_axis - axis * blade)))
    return out, big_axis


def place(prop, axis, size, x, y, angle, grip, length, blade):
    """斧子摆到 size 的画布上：握点 (x, y)，角度 angle（度，朝右为 0），握在全长的 grip 处，全长 length。"""
    image, ax = grown(prop, axis, blade)
    t = math.radians(angle)
    u, v = math.cos(t), math.sin(t)
    k = length / prop.width
    c = grip * prop.width
    tr = (u / k, v / k, c - (u * x + v * y) / k, -v / k, u / k, ax + (v * x - u * y) / k)
    return image.transform(size, Image.Transform.AFFINE, tr, NEAR)


def attach(body, plan, prop, axis, angle=None, length=None):
    """一帧贴斧子（Codex 的 rigid_axe.attach）：两只手的帧斧柄过两只手；握柄的手（和张开的空手）从身体那层盖回来。"""
    size = body.size
    hands = plan.get("hands", [])
    a = plan.get("angle", 0)
    if len(hands) == 2:
        (x0, y0, _), (x1, y1, _) = hands
        a = math.degrees(math.atan2(y1 - y0, x1 - x0))
    if angle is not None:
        a = angle
    x, y = plan["grip"]
    item = place(prop, axis, size, x, y, a, plan.get("grip_ratio", .21), length or plan.get("width", 101), plan.get("blade", 1))
    if plan.get("ground"):
        item = item.transform(size, Image.Transform.AFFINE, (1, 0, 0, 0, 1, -(FOOT - item.getbbox()[3])), NEAR)
    board = Image.alpha_composite(body, item)
    front = hands + plan.get("open_hand", [])
    if front:
        px = np.asarray(body)
        r, g, b, al = px.astype(np.int16).transpose(2, 0, 1)
        yy, xx = np.ogrid[:size[1], :size[0]]
        region = np.zeros((size[1], size[0]), bool)
        for hx, hy, rad in front:
            region |= (xx - hx) ** 2 + (yy - hy) ** 2 <= rad ** 2
        skin = (al > 0) & (r - g > 11) & (g - b > 5) & (r >= 91)
        cover = ndi.binary_dilation(skin & region, iterations=1) & region & (al > 0)
        top = px.copy()
        top[~cover] = 0
        board.alpha_composite(Image.fromarray(top))
    return board


def compose(width, fixed):
    """常态图集：每格 width 宽；fixed 用这里的长度和 LOCK，否则照 Codex 的原表。-> (sheet, fanim)"""
    bare = Image.open(BARE + "#sheet.png").convert("RGBA")
    fanim = json.load(open(BARE + "#anim.fanim", encoding="utf-8-sig"))
    reg = json.load(open(REG, encoding="utf-8"))
    prop = Image.open(PROP).convert("RGBA")
    axis = reg["horizontal_axis_y"]
    rows = list(fanim["anims"])
    sheet = Image.new("RGBA", (8 * width, len(rows) * CELL))
    for tag in rows:
        for i, f in enumerate(fanim["anims"][tag]["frames"]):
            d = f["data"]
            body = Image.new("RGBA", (width, CELL))
            body.paste(bare.crop((d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"])), (0, 0))
            p = reg["frames"].get(tag, [None] * 8)[i]
            if p:
                body = attach(body, p, prop, axis, LOCK.get((tag, i)) if fixed else None, LENGTH if fixed else None)
            box = body.getbbox()
            if not (0 < box[0] and box[2] < width):
                sys.exit(f"{tag} frame {i + 1} leaves its {width} px cell: {box}")
            d["x"], d["w"] = i * width, width
            sheet.paste(body, (d["x"], d["y"]))
    return np.asarray(sheet), fanim


def same_as_codex():
    """按 Codex 的原表、256 的格子贴回去，和它交的图集比。"""
    sheet, _ = compose(CELL, False)
    codex = np.asarray(Image.open(DELIVERED + "#sheet.png").convert("RGBA"))
    if not np.array_equal(sheet, codex):
        bad = int((sheet != codex).any(axis=2).sum())
        sys.exit(f"pasted from Codex's own plan the axe differs from its delivery in {bad} px: this port does not match "
                 "its rigid_axe.py")


def make(_up=None):
    same_as_codex()
    sheet, fanim = compose(WIDE, True)
    return R.snap_delivery(SRC, OUT, ((MAIN, sheet, fanim), HAJUN), FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
