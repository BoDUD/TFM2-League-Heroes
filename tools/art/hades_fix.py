#!/usr/bin/env python3
"""哈迪斯（ragnarok_hades）Codex 交的图：待机重贴双叉枪，再和特效一起收色。

    python tools/art/hades_fix.py            # 读 assets/source/hades 的 bare/、runtime/，写 assets/source/hades/snapped
    python tools/art/hades_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_hades.py、ppu_hd.py --hero hades、hero_reels.py --hero hades

Codex 2026-11-22 交的（hades_packs/outputs/hades_assets_done.zip，以提交 6adc388f9 为准）：一格 256，脚底 (128, 232)，8 个动作
各 8 帧，特效八组各 8 帧。

双叉枪（用户：「如果武器有歪的地方你可以帮忙修复一下」，零福那次说的，这次照样查）。Codex 的每一帧是空手握拳的身体（bare/，
tools/art/hades_bare.py 从它的工作目录取出来的）贴上一根直的枪（runtime/props/bident.png，大招换枪头以后是 desmos.png；
spear-registration.json 记着每帧的握点、角度、握在枪杆的哪里），握枪的手再从身体那层盖回枪杆上面。枪长每帧都是 154，不用改；
这里照它的做法（它的 spear.py）重贴，只改待机：
- 待机（LOCK）：它每帧给的角度 -83、-81、-85、-82、-85、-83、-82、-83，一会儿左一会儿右，枪尖跟着左右来回跳 2-3 个像素，
  看着是在抖。8 帧一律 -83（最多的那个），枪跟着握枪的手走，手怎么随呼吸动枪就怎么动。
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

H = os.path.join(ROOT, "assets", "source", "hades")
SRC = os.path.join(H, "runtime", "sprites")
OUT = os.path.join(H, "snapped")
BARE = os.path.join(H, "bare", "ragnarok_hades_bare_native")
DELIVERED = os.path.join(SRC, "ragnarok_hades_native")
PROPS = os.path.join(H, "runtime", "props")
REG = os.path.join(H, "spear-registration.json")
MAIN = "ragnarok_hades_native"
FX = "ragnarok_hades_fx_native"
NEAR = Image.Resampling.NEAREST
CELL, FOOT = 256, 232
WIDTH = 154                 # 枪全长（Codex 的 spear.WIDTH），每帧一样
THICK = 1.28                # 枪杆比按长度缩放再粗这么多（Codex 的）
LOCK = {("idle", i): -83 for i in range(8)}


def place(source, axis, plan, angle):
    """枪摆到一格上：握点 plan["grip"]，角度 angle（度，朝右为 0），握在全长的 shaft_fraction 处（Codex 的 spear.place）。"""
    x, y = plan["grip"]
    t = math.radians(angle)
    u, v = math.cos(t), math.sin(t)
    zoom = WIDTH / source.width
    grip = (source.width - 1) * plan["shaft_fraction"]
    thickness = zoom * THICK
    m = (u / zoom, v / zoom, grip - (u * x + v * y) / zoom,
         -v / thickness, u / thickness, axis + (v * x - u * y) / thickness)
    weapon = source.transform((CELL, CELL), Image.Transform.AFFINE, m, NEAR)
    box = weapon.getbbox()
    if not box or any(a in (0, CELL) for a in box):
        sys.exit(f"the spear leaves the cell: {plan} angle {angle}: {box}")
    if plan.get("ground"):
        weapon = weapon.transform((CELL, CELL), Image.Transform.AFFINE, (1, 0, 0, 0, 1, -(FOOT - box[3])), NEAR)
    return weapon


def hold(actor, plan, props, axes, angle=None):
    """一帧贴枪（Codex 的 spear.hold）：两只手的帧角度按两只手定；落地、背在身后的在身子后面，别的在前面，握枪的手盖回来。"""
    form = plan.get("form", "bident")
    if angle is None:
        angle = plan["angle"]
        if len(plan.get("hands", [])) == 2:
            (x, y, _), (u, v, _) = plan["hands"]
            angle = math.degrees(math.atan2(v - y, u - x))
    blade = place(props[form], axes[form], plan, angle)
    if plan.get("ground") or plan.get("behind"):
        return Image.alpha_composite(blade, actor)
    held = Image.alpha_composite(actor, blade)
    hands = plan.get("hands", [])
    if hands:
        yy, xx = np.ogrid[:CELL, :CELL]
        mask = np.zeros((CELL, CELL), bool)
        for hx, hy, r in hands:
            mask |= (xx - hx) ** 2 + (yy - hy) ** 2 <= r * r
        front = np.asarray(actor).copy()
        front[~mask] = 0
        held.alpha_composite(Image.fromarray(front))
    return held


def compose(fixed):
    """身体图集：fixed 用 LOCK 的角度，否则照 Codex 的原表。-> (sheet, fanim)"""
    bare = Image.open(BARE + "#sheet.png").convert("RGBA")
    fanim = json.load(open(BARE + "#anim.fanim", encoding="utf-8-sig"))
    reg = json.load(open(REG, encoding="utf-8"))
    props = {k: Image.open(os.path.join(PROPS, k + ".png")).convert("RGBA") for k in reg["axis_y"]}
    sheet = Image.new("RGBA", bare.size)
    for tag, a in fanim["anims"].items():
        for i, f in enumerate(a["frames"]):
            d = f["data"]
            body = bare.crop((d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"]))
            p = reg["frames"].get(tag, [None] * 8)[i]
            if p:
                body = hold(body, p, props, reg["axis_y"], LOCK.get((tag, i)) if fixed else None)
            sheet.paste(body, (d["x"], d["y"]))
    return np.asarray(sheet), fanim


def same_as_codex():
    """按 Codex 的原表贴回去，和它交的图集比。"""
    sheet, _ = compose(False)
    codex = np.asarray(Image.open(DELIVERED + "#sheet.png").convert("RGBA"))
    if not np.array_equal(sheet, codex):
        bad = int((sheet != codex).any(axis=2).sum())
        sys.exit(f"pasted from Codex's own plan the spear differs from its delivery in {bad} px: this port does not match "
                 "its spear.py")


def make(_up=None):
    same_as_codex()
    sheet, fanim = compose(True)
    return R.snap_delivery(SRC, OUT, ((MAIN, sheet, fanim),), FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
