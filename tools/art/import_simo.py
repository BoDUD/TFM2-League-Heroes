#!/usr/bin/env python3
"""西蒙·海耶（终末包 ragnarok_simo）的图：Codex 交的逻辑像素图集（assets/source/simo/atlases）。

    python tools/art/import_simo.py [--check]
    python tools/art/ppu_hd.py --hero simo           # 然后出 hd_ / lo_
    python tools/art/hero_reels.py --hero simo       # 最后出待机和选人动图（顺序不能换）

Codex 2026-11-26 画的（simo_packs/outputs/simo_final_assets.zip，交接说明 assets/source/simo/HANDOFF.md）：第十一回合漫画的
样子（雪衣、白兜帽、条纹遮面、一支长枪），Q 版像素画。一格 128×96 逻辑像素，脚底 (59, 87)，人站直 56 格；特效格同样大，
中心 (64, 48)。和冲田一样（tools/art/import_okita.py）：两倍最近邻读进来，PPU 8/3，站直 42 个游戏像素，特效和人一个比例。

画进他自己帧里的（会跟着他左右翻），位置照 frames.json 的 fx_events（离脚底的偏移，逻辑像素，这里乘 2），时间照 cues：
- 普攻第 4 帧（0.269 秒）的枪口焰 muzzle 和短弹道光迹 trace；
- 精确一击（skill）第 5 帧（0.44 秒）的光迹 precision；
- 雪幕步（skill2）第 2 帧（0.1 秒）展开的雪幕 snow_veil（脚下一圈雪，画在身后）、第 4 帧（0.25 秒）的踏雪 snow_step（脚底，
  画在身后）；
- 白色死神（ult）第 5 帧（0.5 秒）的光迹 white_death。
放在别处的：命中雪晶 impact、终结命中 finisher_impact 放在目标身上；雪幕 snow_veil 也挂在他身上（雪幕的状态里循环）。

2026-11-26 照原作补的子弹特效（Codex，assets/source/simo/fidelity，逻辑像素，和他的图一样两倍读）：Q 按原作的顺序轮流打出
三发，画面分得出来——Q 的身体帧再出两份（ALIAS），数据按轮到哪一发用 CasterAnimation 放：
- skill_lily 万花缭乱：0.44 秒枪口炸开铃兰扇形（扇子的尖对着枪口：一发子弹在半空炸成碎片，扇形的长短正好是 Q 的扇形范围），
  碎片打中的光 lily_hit 打在目标身上；
- skill_swan 天穿白鸟：0.44 秒从枪口拉出一条长螺旋光（钉在原地：后坐力把他往后推的 0.1 秒里光往前挪同样多），脚后的后坐光
  画在身后；
- skill 精灵的气息：原来的精确一击光迹。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ragnarok_art as A  # noqa: E402
import ragnarok_atlas as RA  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "simo")
ID = "ragnarok_simo"
HERO = "simo"
PPU = 2.667                 # 8/3，和 tools/art/ppu_hd.py 的 PPU、addons/ragnarok/src/hd.rs 的 HEROES 一致
FX_PPU = 2.667
SOLE = RA.scaled((59, 87))
FX_ORIGIN = RA.scaled((64, 48))
CANVAS = (640, 320, (200, 260))     # 天穿白鸟的螺旋光从枪口往前拉 132 个逻辑像素
# 别的动作照原来的画布裁（放宽以后原来切掉的特效露出来，帧变大，选人卡片的界面图放不进 2048）
CANVAS_OLD = (480, 320, (200, 260))


def at(dx, dy):
    """Codex 的偏移（离脚底，逻辑像素）-> 放大后的偏移。"""
    return RA.scaled((dx, dy))


def on_unit(dx, dy):
    """挂在单位身上的特效：中心在脚底 + (dx, dy)，游戏把特效中心放在枢轴上（脚底往上 FEET 个游戏像素）。"""
    ox, oy = at(dx, dy)
    return (FX_ORIGIN[0] - ox, round(FX_ORIGIN[1] - oy - A.FEET * FX_PPU))


FID = os.path.join(ROOT, "assets", "source", "simo", "fidelity")
REDRAW_FX = [(FID, "simo", {"lily_burst": "lily_burst", "lily_hit": "lily_hit", "swan_spiral": "swan_spiral",
                            "swan_recoil": "swan_recoil"}, 2)]
ALIAS = {"skill_lily": "skill", "skill_swan": "skill"}
TAGS = A.ACTIONS + ("skill_lily", "skill_swan")

# (动作, 特效, 开始秒, 离脚底的锚点, 每帧秒数（None 用特效自己的）, 特效格的中心[, "behind"])
BAKE = [
    ("attack", "muzzle", 0.269, at(44, -35), None, FX_ORIGIN),
    ("attack", "trace", 0.269, at(44, -35), None, FX_ORIGIN),
    ("skill", "precision", 0.44, at(46, -29), None, FX_ORIGIN),
    ("skill2", "snow_veil", 0.1, at(0, -9), None, FX_ORIGIN, "behind"),
    ("skill2", "snow_step", 0.25, at(-8, -1), None, FX_ORIGIN, "behind"),
    ("ult", "white_death", 0.5, at(45, -33), None, FX_ORIGIN),
    # 万花缭乱：扇子的尖（Codex 的挂点）对着精确一击光迹的枪口
    ("skill_lily", "lily_burst", 0.44, at(46, -29), None, RA.redraw_point(FID, "fx", "lily_burst", 2)),
    # 天穿白鸟：螺旋光的尾巴对着枪口；后坐力（build_simo q2_back 3000 x 6 拍 = 18 个游戏像素，0.45-0.55 秒）把他往后推，
    # 光每秒往前挪 3000 x 60 / 1000 x PPU = 480 格，钉在原地
    ("skill_swan", "swan_spiral", 0.44, at(46, -29), None, RA.redraw_point(FID, "fx", "swan_spiral", 2),
     {"world": (0.45, 480, 0.55)}),
    ("skill_swan", "swan_recoil", 0.44, RA.redraw_offset(FID, "swan_recoil", 2), None,
     RA.redraw_point(FID, "fx", "swan_recoil", 2), "behind"),
]
TARGET_FX = {"impact": FX_ORIGIN, "finisher_impact": FX_ORIGIN, "snow_veil": on_unit(0, -9), "snow_step": on_unit(-8, -1),
             "lily_hit": RA.redraw_point(FID, "fx", "lily_hit", 2)}

SIMO = {"SRC": SRC, "ID": ID, "HERO": HERO, "PPU": PPU, "FX_PPU": FX_PPU, "SOLE": SOLE, "BAKE": BAKE, "RETIME": {},
        "TARGET_FX": TARGET_FX, "CANVAS": CANVAS, "READ": RA.reader(SRC, "simo", ID), "REDRAW_FX": REDRAW_FX,
        "ALIAS": ALIAS, "TAGS": TAGS, "CANVAS_OLD": CANVAS_OLD, "WIDE": ("skill_lily", "skill_swan")}

if __name__ == "__main__":
    A.main(SIMO, __doc__)
