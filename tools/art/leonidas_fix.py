#!/usr/bin/env python3
"""列奥尼达斯（ragnarok_leonidas）Codex 交的图：盾一律按原来的大小重贴，再和特效一起收色。

    python tools/art/leonidas_fix.py            # 读 assets/source/leonidas 的 bare/、runtime/，写 assets/source/leonidas/snapped
    python tools/art/leonidas_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_leonidas.py、ppu_hd.py --hero leonidas、hero_reels.py --hero leonidas

Codex 2026-11-23 交的（leonidas_packs/outputs/leonidas_assets_done.zip，以提交 35546c8f5 为准）：一格 256，脚底 (128, 232)，
8 个动作各 8 帧，特效八组各 8 帧（盾击的钢弧和命中、链盾的飞盘尾迹和回卷、举盾的盾沿和反弹光箭、方阵冲锋的尘土和冲击）。

盾。Codex 的每一帧是空手的身体（bare/，tools/art/leonidas_bare.py 从它的工作目录取出来的）贴上一面盾（runtime/props/
round_shield.png；大招第 3-7 帧换成大一号的真理之盾 truth_shield.png，那是另一面盾），shield-registration.json 记着每帧的
中心、角度、大小。圆盾平时是 37×51（竖着的直径 51，横向看斜了只剩 37），可它有几处故意改了大小，盾一会儿大一会儿小
（「模型不要变大变小」）：
- 举盾（skill2）第 3-6 帧放大成 42×55，收盾又变回来，看着是盾突然胀了一圈；改回 37×51，中心不动。
- 链盾飞出去那三帧（skill 第 4-6 帧）是平着转的飞盘，44×24、51×31、43×29。圆不管怎么转，投影的长轴都是直径，44、43 就是
  盾缩了一圈；长轴一律 51，短轴不动（51×24、51×31、51×29）。
- 倒地第 4 帧盾脱手往下倒，37×36，长轴缩了三成；改成手里那面一样的 37×51，只是转到 -42 度。第 5-8 帧平躺在地上 55×17，
  长轴比直径大，改成 51×17。
别的帧（待机、跑、普攻、受击、大招）本来就是同一面盾，不动。贴法照它的 shield.py：盾按大小拉伸、按角度转，最近邻；盾盖在
身体上面，倒地后躺在地上的在身体下面；飞出去的三帧从握点到盾中心再拉一条钢链，链在盾下面。
重贴之前先验一遍：按 Codex 的原表贴回去，64 帧要和它交的一模一样（不一样说明这里的做法和它的对不上，不往下走）。

收色和别的英雄一样（tools/art/kojiro_fix.py 有来由）：身体 64 色，特效每组 32 色。
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_repixel as R  # noqa: E402

L = os.path.join(ROOT, "assets", "source", "leonidas")
SRC = os.path.join(L, "runtime", "sprites")
OUT = os.path.join(L, "snapped")
BARE = os.path.join(L, "bare", "ragnarok_leonidas_bare_native")
DELIVERED = os.path.join(SRC, "ragnarok_leonidas_native")
PROPS = os.path.join(L, "runtime", "props")
REG = os.path.join(L, "shield-registration.json")
MAIN = "ragnarok_leonidas_native"
FX = "ragnarok_leonidas_fx_native"
NEAR = Image.Resampling.NEAREST
CELL = 256
# 改过的大小：(动作, 第几帧从 0 数) -> (宽, 高)。别的帧照原表。
SIZE = {("skill2", i): (37, 51) for i in range(2, 6)}
SIZE.update({("skill", 3): (51, 24), ("skill", 4): (51, 31), ("skill", 5): (51, 29), ("dead", 3): (37, 51)})
SIZE.update({("dead", i): (51, 17) for i in range(4, 8)})


def place(picture, center, size, angle):
    """一件东西摆到一格上（Codex 的 shield.transform_prop）：拉成 size，转 angle 度，中心放在 center。"""
    x, y = center
    width, height = size
    wx, hy = width / picture.width, height / picture.height
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    a, b = c / wx, s / wx
    cc, d = -s / hy, c / hy
    return picture.transform((CELL, CELL), Image.Transform.AFFINE,
                             (a, b, picture.width / 2 - a * x - b * y, cc, d, picture.height / 2 - cc * x - d * y), NEAR)


def hold(actor, plan, props, size):
    """一帧贴盾（Codex 的 shield.render_prop + hold）。"""
    disc = place(props[plan["form"]], plan["center"], size, plan["angle"])
    if plan["flight"]:
        x, y = plan["grip"]
        dx, dy = plan["center"][0] - x, plan["center"][1] - y
        chain = place(props["chain"], (x + dx / 2, y + dy / 2), (math.hypot(dx, dy) + 3, 7), math.degrees(math.atan2(dy, dx)))
        disc = Image.alpha_composite(chain, disc)
    box = disc.getbbox()
    if not box or any(v in (0, CELL) for v in box):
        sys.exit(f"the shield leaves the cell: {plan} size {size}: {box}")
    if plan["fixed"]:
        return Image.alpha_composite(disc, actor)
    return Image.alpha_composite(actor, disc)


def compose(fixed):
    """身体图集：fixed 用 SIZE 改过的大小，否则照 Codex 的原表。-> (sheet, fanim)"""
    bare = Image.open(BARE + "#sheet.png").convert("RGBA")
    fanim = json.load(open(BARE + "#anim.fanim", encoding="utf-8-sig"))
    reg = json.load(open(REG, encoding="utf-8"))["frames"]
    props = {k: Image.open(os.path.join(PROPS, k + ".png")).convert("RGBA") for k in ("round_shield", "truth_shield", "chain")}
    sheet = Image.new("RGBA", bare.size)
    for tag, a in fanim["anims"].items():
        for i, f in enumerate(a["frames"]):
            d = f["data"]
            body = bare.crop((d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"]))
            p = reg[tag][i]
            size = SIZE.get((tag, i), p["size"]) if fixed else p["size"]
            sheet.paste(hold(body, p, props, size), (d["x"], d["y"]))
    return np.asarray(sheet), fanim


def same_as_codex():
    """按 Codex 的原表贴回去，和它交的图集比。"""
    sheet, _ = compose(False)
    codex = np.asarray(Image.open(DELIVERED + "#sheet.png").convert("RGBA"))
    if not np.array_equal(sheet, codex):
        bad = int((sheet != codex).any(axis=2).sum())
        sys.exit(f"pasted from Codex's own table the shield differs from its delivery in {bad} px: this port does not match "
                 "its shield.py")


def make(_up=None):
    same_as_codex()
    sheet, fanim = compose(True)
    return R.snap_delivery(SRC, OUT, ((MAIN, sheet, fanim),), FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
