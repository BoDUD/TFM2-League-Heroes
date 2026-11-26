#!/usr/bin/env python3
"""Zeus's sheets (the ragnarok pack, ragnarok_zeus) from Codex's delivery in assets/source/zeus/codex_v01.

    python tools/art/zeus_repixel.py                # 先按两倍密度重出五张图（assets/source/zeus/repixel）
    python tools/art/import_zeus.py [--check]
    python tools/art/ppu_hd.py --hero zeus          # then the hd_ and lo_ tags
    python tools/art/hero_reels.py --hero zeus      # then the idle and ban/pick reels (always in this order)

Codex drew him (2026-11-21, branch codex/ragnarok-zeus-assets, commit de2b95f) in Lu Bu's and Thor's cells, the soles'
point at (64, 116), three bodies of one hero: the old man (elder, 51 rows to the top of his head), the swollen muscle
body (muscle, 67) and Adamas (59), each with idle / run / attack / skill / hit / dead of 8 frames and skill2 of 4, plus
the three changes between them (transform: expand, compress, revert; each change's first and last frame are the two
forms' first idle frames). At Thor's PPU 1.65 the old man stands 31 game px, the muscle body 41, Adamas 36 (Thor 33,
Lu Bu 34). The engine is tools/art/ragnarok_art.py (Lu Bu's import_lubu.py tells why each step is so); BANKS put the
five sheets of Codex into one: the old man's tags as they are, mu_* the muscle body's, ad_* Adamas's, `expand` and
`revert` the changes the kit plays (tools/kit/build_zeus.py, CasterAnimation), the compression the ult's own `ult`.
ragnarok.dll's display hook (addons/ragnarok/src/zeus.rs) swaps idle .. skill2 for the mu_ / ad_ ones by his buffs.

- Baked into his frames (pictures with a front and a back), each body at its own fist (measured on the release frames):
  the jab's wind (attack frame 4, 0.245 s), the barrage's two streaks (skill frames 3 and 5, 0.18 / 0.315 s, 30 ms a
  frame), the time punch's charge round the drawn-back fist (skill2 from 0, 50 ms a frame) and its release at the fist
  (skill2 frame 3, 0.4 s, 34 ms a frame), the changes' rising light (expand and the compression, its bright foot on
  his soles, stretched over the change).
- On units: the jab's and the barrage's hits (on the target, the time punch's too), the change's burst round his feet
  (its ground line under the pivot like the soles: played when a change completes).

2026-11-26 照原作改（用户：「我需要的是完美的还原度」）：老人形态的 skill 换成 Codex 补画的黄昏流星群（メテオジャブ，
assets/source/zeus/fidelity，逻辑像素图集，按他 Q 版的像素格 2x2；原作第二回合：刺拳连打，越打越快）：8 帧 7 拳，0.12 秒和
0.304 秒各放一遍刺拳光迹（照 Codex 的位置会擦到胡子，往前挪 9 个逻辑像素）。动作 0.562 秒，最后一帧拉长到 Q 的 38 拍
（膨胀、阿陀磨须形态的 Q 还是原来的长度）。原来老人形态两拳的 barrage_wind 去掉。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

# 2026-11-21 和亚当一样按两倍密度重出（tools/art/zeus_repixel.py，用户：「然后调整另外三个 全都在一个pr里处理就行」）：
# 一格 256、脚底点 (128, 232)，PPU 3.3，个子不变。下面的数还是 Codex 128 格里量的，用 up() 乘两倍
SRC = os.path.join(ROOT, "assets", "source", "zeus", "repixel")
ID = "ragnarok_zeus"
HERO = "zeus"
UP = 2.0                    # 和 tools/art/zeus_repixel.py 一样
# 2026-11-22 整包放大到联盟英雄的个子（用户：「我发现女武神在格子里普遍偏小 不像英雄联盟那样」「放大到联盟大小」）：
# 英雄 PPU 除以 1.2，同样的像素画成 1.2 倍大；打在别人身上的特效图（FX_PPU）还是原来的大小，命中和范围按游戏里的距离走
PPU = round(1.65 * UP / 1.2, 3)   # 2.75（放大前 3.3）
FX_PPU = round(1.65 * UP, 3)     # 3.3：特效图不放大


def up(p):
    """Codex 128 格里的坐标 -> 重出图里的。"""
    return (round(p[0] * UP), round(p[1] * UP))


SOLE = up((64, 116))
FX_ORIGIN = up((64, 64))    # 特效格的中心
CANVAS = (760, 520, (300, 420))   # 2026-11-26 黄昏流星群的刺拳光往前挪（原来 (576, 448, (288, 352))）
FORM = ("idle", "run", "attack", "skill", "skill2", "hit", "dead")
# the three bodies (the old man's tags as they are, mu_ the muscle body's, ad_ Adamas's) and the changes
BANKS = [
    ("ragnarok_zeus_elder_native", {t: t for t in FORM}),
    ("ragnarok_zeus_muscle_native", {t: "mu_" + t for t in FORM}),
    ("ragnarok_zeus_adamas_native", {t: "ad_" + t for t in FORM}),
    ("ragnarok_zeus_transform_native", {"expand": "expand", "compress": "ult", "revert": "revert"}),
]
TAGS = list(FORM) + ["mu_" + t for t in FORM] + ["ad_" + t for t in FORM] + ["expand", "ult", "revert"]
# each body's fist on the release frames, from the soles (Codex's frames: elder attack 4 at +30 / -31 ...); the winds
# start 12 px ahead of it, the release's rings sit on it
FID = os.path.join(ROOT, "assets", "source", "zeus", "fidelity")
REDRAW = [(FID, "zeus", {"skill": "skill"}, None)]
REDRAW_FX = [(FID, "zeus", {"jab": "jab"}, None)]
FISTS = {"": {"attack": (30, -31), "skill1": (27, -32), "skill2": (28, -30), "charge": (17, -35), "punch": (34, -32)},
         "mu_": {"attack": (35, -42), "skill1": (38, -44), "skill2": (38, -43), "charge": (25, -35), "punch": (42, -46)},
         "ad_": {"attack": (30, -34), "skill1": (30, -35), "skill2": (26, -34), "charge": (22, -41), "punch": (37, -38)}}


def ahead(p, dx):
    return up((p[0] + dx, p[1]))


# (action, effect, from seconds, anchor from the soles, seconds a frame or None, the effect's origin in its cell)
BAKE = []
for pre, f in FISTS.items():
    BAKE += [
        (pre + "attack", "jab_wind", 0.245, ahead(f["attack"], 12), None, FX_ORIGIN),
        *([] if pre == "" else [(pre + "skill", "barrage_wind", 0.18, ahead(f["skill1"], 10), 0.03, FX_ORIGIN),
                                (pre + "skill", "barrage_wind", 0.315, ahead(f["skill2"], 10), 0.03, FX_ORIGIN)]),
        (pre + "skill2", "time_charge", 0.0, up(f["charge"]), 0.05, FX_ORIGIN),
        (pre + "skill2", "time_release", 0.40, ahead(f["punch"], 25), 0.034, FX_ORIGIN),
    ]
# the changes: the rising light's bright foot (its cell's row 64 + 26) on his soles, over the whole change
BAKE += [("expand", "form_charge", 0.0, up((0, -26)), 1.02 / 8, FX_ORIGIN),
         ("ult", "form_charge", 0.0, up((0, -26)), 1.04 / 8, FX_ORIGIN)]
# 黄昏流星群：两遍刺拳光迹（往前挪 9 个逻辑像素，不碰胡子）
BAKE += [("skill", "jab", t, RA.redraw_offset(FID, "jab", nudge=(18, 0)), None, RA.redraw_point(FID, "fx", "jab"))
         for t in (0.12, 0.304)]
# 0.562 秒的补画塞进 Q 的 38 拍：最后一帧拉长
RETIME = {"skill": [0.12, 0.098, 0.086, 0.072, 0.059, 0.049, 0.042, 0.107]}
TARGET_FX = {
    "jab_hit": FX_ORIGIN,
    "barrage_hit": FX_ORIGIN,
    # the burst's ground line (its cell's row 64 + 22) under the pivot like the soles
    "form_burst": (FX_ORIGIN[0], round(86 * UP - A.FEET * FX_PPU)),
}

ZEUS = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": RETIME,
        "TARGET_FX": TARGET_FX, "BANKS": BANKS, "TAGS": TAGS, "CANVAS": CANVAS,
        "REDRAW": REDRAW, "REDRAW_FX": REDRAW_FX}

if __name__ == "__main__":
    A.main(ZEUS, __doc__)
