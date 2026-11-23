#!/usr/bin/env python3
"""阿波罗（ragnarok_apollo）Codex 交的图：光弓和女神像一律按满的大小重贴，再和特效一起收色。

    python tools/art/apollo_fix.py            # 读 assets/source/apollo 的 bare/、runtime/，写 assets/source/apollo/snapped
    python tools/art/apollo_fix.py --check    # 和现在的 snapped/ 不一样就退出 1
    然后 tools/art/import_apollo.py、ppu_hd.py --hero apollo、hero_reels.py --hero apollo

Codex 2026-11-23 交的（apollo_packs/outputs/apollo_assets_done.zip，以提交 ab889d460 为准）：一格 256，脚底 (128, 232)，
8 个动作各 8 帧，特效八组各 8 帧（日轮拳的拳光和命中、阿尔忒弥斯之丝的投出和收束、光箭、离弦的光、女神像显现的光、银箭突进）。

弓和像。Codex 的每一帧是空手的身体（bare/，tools/art/apollo_bare.py 从它的工作目录取出来的），光之矢第 3-6 帧贴上光弓
（runtime/props/artemis_bow.png，两条光弦从弓梢拉到弦上的那一点），大招第 3-5 帧在身后贴阿尔忒弥斯的女神像
（artemis_statue.png），bow-registration.json 记着每帧的位置和大小。可它的大小是一帧一帧写死的，一会儿大一会儿小
（「模型不要变大变小」）：
- 弓第 4、5 帧（拉弦、放箭）84×27，第 3 帧（光弓成形）只有 65×21、第 6 帧（放完）76×24：弓先小一圈、再胀到满、再缩回去。
  一律 84×27，握点不动（弓梢、弦跟着弓重算，和它的 bow.point_plan 一样算）；成形的那一下有它画进去的 summon 光。
- 女神像第 4、5 帧 103×163，第 3 帧（显现）95×141 还往右挪了 7 格：显现那一帧也是满的大小、同一个地方。
别的帧不动。贴法照它的 bow.py：最近邻拉伸；弓盖在身体上面、握弓的手（握点 4.4 格以内）再从身体那层盖回来；拉弦的那一帧
（第 4 帧）两条弦拉到手上、再从手上到离弦点；女神像在身体后面。
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

AP = os.path.join(ROOT, "assets", "source", "apollo")
SRC = os.path.join(AP, "runtime", "sprites")
OUT = os.path.join(AP, "snapped")
BARE = os.path.join(AP, "bare", "ragnarok_apollo_bare_native")
DELIVERED = os.path.join(SRC, "ragnarok_apollo_native")
PROPS = os.path.join(AP, "runtime", "props")
REG = os.path.join(AP, "bow-registration.json")
MAIN = "ragnarok_apollo_native"
FX = "ragnarok_apollo_fx_native"
NEAR = Image.Resampling.NEAREST
CELL = 256
BOW, STRING, STATUE = "artemis_bow", "light_string", "artemis_statue"
BOW_HW = (84, 27)           # 光弓满的大小（高、宽）：拉弦、放箭那两帧的
GRIP_R = 4.4                # 握弓的手盖回来的半径（Codex 的）


def props():
    return {k: Image.open(os.path.join(PROPS, k + ".png")).convert("RGBA") for k in (BOW, STRING, STATUE)}


def affine(image, center, size, theta=0.0):
    """拉成 size、转 theta 弧度、中心放在 center（Codex 的 bow.affine）。"""
    x, y = center
    w, h = size
    zx, zy = w / image.width, h / image.height
    c, s = np.cos(theta), np.sin(theta)
    a, b = c / zx, s / zx
    cc, d = -s / zy, c / zy
    return image.transform((CELL, CELL), Image.Transform.AFFINE,
                           (a, b, image.width / 2 - a * x - b * y, cc, d, image.height / 2 - cc * x - d * y), NEAR)


def line(pr, a, b, width):
    x, y = a
    u, v = b
    dx, dy = u - x, v - y
    return affine(pr[STRING], ((x + u) / 2, (y + v) / 2), (max(2, math.hypot(dx, dy) + 2), width), math.atan2(dy, dx))


def bow_connections(pr):
    """弓的上梢、握把、下梢在弓图里的相对位置（Codex 的 bow.bow_connections）。"""
    mask = np.asarray(pr[BOW].getchannel("A")) > 0
    w, h = mask.shape[1], mask.shape[0]
    rows = [round(.021 * h), round(.506 * h), round(.979 * h)]
    xs = [float(np.median(np.flatnonzero(mask[y]))) for y in rows]
    return tuple((x / w, y / h) for x, y in zip(xs, rows))


def resized_bow(plan, pr):
    """同一个握点，弓按 BOW_HW 重算（Codex 的 bow.point_plan 的算法）；拉弦的那一帧弦上的点不变。"""
    h, w = BOW_HW
    x, y = plan["grip"]
    top, grip_local, bottom = bow_connections(pr)
    off = [x - grip_local[0] * w, y - grip_local[1] * h]

    def coord(p):
        return [round(off[0] + p[0] * w, 2), round(off[1] + p[1] * h, 2)]

    tip_top, tip_bottom = coord(top), coord(bottom)
    bend = plan["nock"] if plan["drawn"] else [round((tip_top[0] + tip_bottom[0]) / 2, 2), y - 1]
    return {**plan, "bounds": [round(off[0], 2), round(off[1], 2), w, h], "tips": [tip_top, tip_bottom], "nock": bend,
            "fire_origin": [round(x + 4, 2), round(bend[1], 2)]}


def art_for(plan, pr):
    x, y, w, h = plan["bounds"]
    art = affine(pr[plan["form"]], (x + w / 2, y + h / 2), (w, h))
    if plan["form"] == BOW or plan["drawn"]:
        for tip in plan["tips"]:
            art.alpha_composite(line(pr, tip, plan["nock"], 2.5))
    if plan["form"] == BOW and plan["drawn"]:
        art.alpha_composite(line(pr, plan["nock"], plan["fire_origin"], 2.7))
    return art


def hold(actor, plan, pr):
    """一帧贴弓 / 像（Codex 的 bow.hold）。"""
    if plan is None:
        return actor
    item = art_for(plan, pr)
    box = item.getbbox()
    if not box or any(v in (0, CELL) for v in box):
        sys.exit(f"the {plan['form']} leaves the cell: {plan}: {box}")
    if plan["form"] == STATUE:
        return Image.alpha_composite(item, actor)
    out = Image.alpha_composite(actor, item)
    hand = np.asarray(actor).copy()
    yy, xx = np.ogrid[:CELL, :CELL]
    gx, gy = plan["grip"]
    hand[(xx - gx) ** 2 + (yy - gy) ** 2 > GRIP_R ** 2] = 0
    out.alpha_composite(Image.fromarray(hand))
    return out


def fixed_plans(reg, pr):
    """改过的表：弓都是满的大小，女神像显现那一帧照第 4 帧的大小和位置。"""
    out = {k: [None if p is None else dict(p) for p in v] for k, v in reg.items()}
    for i, p in enumerate(out["skill2"]):
        if p is not None and [p["bounds"][3], p["bounds"][2]] != list(BOW_HW):
            out["skill2"][i] = resized_bow(p, pr)
    full = reg["ult"][3]
    out["ult"][2] = {**out["ult"][2], "bounds": list(full["bounds"]), "tips": [list(t) for t in full["tips"]]}
    return out


def compose(fixed):
    """身体图集：fixed 用改过的表，否则照 Codex 的原表。-> (sheet, fanim)"""
    bare = Image.open(BARE + "#sheet.png").convert("RGBA")
    fanim = json.load(open(BARE + "#anim.fanim", encoding="utf-8-sig"))
    reg = json.load(open(REG, encoding="utf-8"))["layers"]
    pr = props()
    plans = fixed_plans(reg, pr) if fixed else reg
    sheet = Image.new("RGBA", bare.size)
    for tag, a in fanim["anims"].items():
        for i, f in enumerate(a["frames"]):
            d = f["data"]
            body = bare.crop((d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"]))
            sheet.paste(hold(body, plans.get(tag, [None] * 8)[i], pr), (d["x"], d["y"]))
    return np.asarray(sheet), fanim


def same_as_codex():
    """按 Codex 的原表贴回去，和它交的图集比。"""
    sheet, _ = compose(False)
    codex = np.asarray(Image.open(DELIVERED + "#sheet.png").convert("RGBA"))
    if not np.array_equal(sheet, codex):
        bad = int((sheet != codex).any(axis=2).sum())
        sys.exit(f"pasted from Codex's own table the bow / statue differ from its delivery in {bad} px: this port does not "
                 "match its bow.py")


def make(_up=None):
    same_as_codex()
    sheet, fanim = compose(True)
    return R.snap_delivery(SRC, OUT, ((MAIN, sheet, fanim),), FX)


if __name__ == "__main__":
    R.run(__doc__, make, 2)
