#!/usr/bin/env python3
"""Build khazix_fx_pack.zip: step 3 of Kha'Zix's sprite - Codex draws his effects (after tools/art/pack_pyke_fx.py).

    python tools/art/pack_khazix_fx.py [--no-zip] [--out DIR] [--only w_spike,w_hit --name khazix_fx_redo_pack]

The pack (%TEMP%/kz_work/fx/khazix_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/khazix/PROMPTS_FX.md), design/khazix_design.png (8x), design/khazix_size.png (the design at 4x on the arena
colour with the feet line, a 10-px ruler and the base fighter beside him), design/khazix_shots.png (the finished action
frames at 4x from league/champions/league_khazix, with the point each picture starts from) and refs/lol_fx_ref.png
(League's own particle textures for Kha'Zix, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/kz_work/fxref, extracted from Khazix.wad.client by the session's fx_ref_kz.py).
The effects are the views the kit binds (tools/kit/build_khazix.py: view_projectiles w_spike; view_effects a_hit, p_hit,
q_hit, q_iso_hit, e_land, e_hit, w_hit, w_heal, r_cast, p_ready, e_reset, evo; view_buffs ut, slow (p_slow and w_slow
share it), r_on). League's colours: the Void's magenta and violet (his passive, Q, the spike, R), violet lightning,
the claws' bone white, a pale green for W's heal. Light, smoke and slashes get no outline (the bright-effects lesson);
the spike, an object, has one. Red side: the projectile symmetric top to bottom, the buffs and the pictures on him after
the first tick (w_heal, p_ready, e_reset, evo) symmetric left to right, the ground picture (e_land) symmetric both ways.
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "kz_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "khazix", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "khazix_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VOID = "#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A"   # the Void's magenta: his passive, Q, R, the evolution
BOLT = "#FFFFFF, #E8E0FF, #B8A8FF, #7C6CF0, #4A3CB0"             # violet lightning: the spike, the leap's shock
BONE = "#FFFFFF, #FFF6F0, #F2DCD4, #C8A8A8"                      # the claws' bone-white edges: the slashes
HEAL = "#FFFFFF, #ECFFD8, #BCF08C, #72C84C, #2E7A28"              # W's heal
SPIKE = "#0B0814, #2A1A5C, #46309A, #6A4ED0, #9478F0, #F08CFF, #FFFFFF"   # the spike itself (an object)
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades "
        "and a white core - it must read on a dark battlefield), colours only from {ramps}.")
LEAD_OBJ = ("Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
            "a 1-square dark outline #0B0814 around the object, colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FIG = "do NOT draw the figure; leave its place empty"
VD = f"a void magenta ramp ({VOID})"
BT = f"a violet lightning ramp ({BOLT})"
BN = f"a bone ramp ({BONE})"
HL = f"a pale green ramp ({HEAL})"
SP = f"the spike's violet chitin ({SPIKE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout, outlined object
FX = [
    # ---- the attack and the passive
    ("a_hit", "普攻镰爪砍中（目标身上），4 帧", "view_effects `league_khazix_a_hit`（跟随，画在人物上面）", "14",
     "镰爪砍中：一道斜着的骨白色爪痕，白色的芯，边上一点紫色的虚空碎光（参考 Q_Slash、Hit_Spark、bolts_HitEffect）。约 14 格，居中画。",
     f"{BN} and {VD}",
     "a CLAW SLASH HIT, 4 frames: 1 a curved bone-white claw streak 12 squares long through the center (from the top right "
     "down to the bottom left), a white core; 2 the streak thinner, a magenta flash 4 squares across at its middle, small "
     "violet sparks flying out; 3 sparks scattering; 4 a few fading sparks.",
     row(4, 16, 16) + "; centered in every cell.", False),
    ("p_hit", "被动 无形威胁打中（目标身上），5 帧", "view_effects `league_khazix_p_hit`（跟随，画在人物上面）", "18",
     "无形威胁打出：一颗洋红色的尖星爆开，几缕紫色虚空火焰往上窜（参考 Q_impact、P_OuterRing、Flames2）。约 18 格，居中画。",
     VD,
     "a VOID BURST HIT, 5 frames: 1 a magenta-white sharp six-pointed star 10 squares across at the center; 2 the star "
     "bigger, a ring of magenta sparks 14 squares across; 3 three violet flame tongues licking up 8 squares from the "
     "center, the ring breaking into motes; 4 the flames thinner, motes drifting up; 5 fading motes.",
     row(5, 20, 20) + "; centered in every cell.", False),
    ("ut", "被动 无形威胁就绪（他身上，循环），4 帧", "view_buffs `league_khazix_ut`（跟随，画在他身上，左右对称）", "26 × 12",
     "无形威胁就绪：他胸前两侧各一团小小的洋红色虚空火光在跳（英雄联盟里是他爪子上的紫光；参考 P_Glow、P_InnerCore）。**左右对称**，"
     "**中间留空**（人在中间）。4 帧无缝循环。约 26 格宽、12 格高，两团火光各约 5 格，相距约 16 格。",
     VD,
     f"two small VOID FLAMES around a figure's chest ({FIG}), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: one "
     "magenta-white flame 5 squares across on each side, 16 squares apart, the middle 12 squares empty; each frame the "
     "flames flicker (taller, shorter) and 2 tiny motes rise from them.",
     row(4, 28, 14) + "; centered in every cell.", False),
    ("p_ready", "被动就绪的提示（他头顶，一闪），5 帧",
     "view_effects `league_khazix_p_ready`（不跟随，左右对称；中心在站位点上面约 36 格）", "16",
     "无形威胁刚就绪时，他头顶亮一下：一个洋红色的眼睛形状的闪光一闪而过（参考 NegaSparkle、Q_SingleEnemy_Indicator）。**左右对称**。约 16 格，居中画。",
     VD,
     "an EYE-SHAPED GLINT, 5 frames, SYMMETRIC LEFT TO RIGHT: 1 a thin magenta horizontal line 6 squares long; 2 it opens "
     "into an almond-shaped eye 12 squares wide and 5 tall with a white slit pupil; 3 the eye glowing brightest, 4 short "
     "rays around it; 4 the eye closing; 5 a fading magenta dot.",
     row(5, 16, 16) + "; centered in every cell.", False),
    # ---- Q
    ("q_hit", "Q 品尝恐惧打中（目标身上），4 帧", "view_effects `league_khazix_q_hit`（跟随，画在人物上面）", "16",
     "Q 打中：三道并排的斜爪痕（骨白芯、紫边）一齐划过（参考 Q_Slash、Q_Lightning02）。约 16 格，居中画。",
     f"{BN} and {VD}",
     "a TRIPLE CLAW HIT, 4 frames: 1 three parallel diagonal claw streaks 12 squares long, 2 squares apart, white cores with "
     "violet edges; 2 the streaks thinner, a small magenta flash at the center; 3 the streaks breaking into violet sparks; "
     "4 fading sparks.",
     row(4, 18, 18) + "; centered in every cell.", False),
    ("q_iso_hit", "Q 打中孤立无援的目标（目标身上），6 帧", "view_effects `league_khazix_q_iso_hit`（跟随，画在人物上面）", "26",
     "打孤立目标时更重的一击：三道大爪痕，后面炸开一颗大大的洋红尖星，一圈紫色的三叶形标记一闪（英雄联盟孤立目标头上的标记；参考 Q_impact、"
     "Q_SingleEnemy_Indicator02_Reticle、Q_Impact_04）。约 26 格，居中画。",
     f"{BN} and {VD}",
     "an ISOLATED-TARGET CRUSHING HIT, 6 frames: 1 three big parallel diagonal claw streaks 18 squares long, white cores with "
     "magenta edges; 2 a magenta-white eight-pointed star 16 squares across bursting behind them; 3 a thin violet ring 22 "
     "squares across with three curved notches (a three-lobed reticle) flashing round the star; 4 the star shrinking, the "
     "ring brightest; 5 the ring fading into sparks; 6 fading sparks.",
     row(6, 28, 28) + "; centered in every cell.", False),
    # ---- E -> W
    ("e_land", "E 跃击落地：地上的冲击（地上），6 帧",
     "view_effects `league_khazix_e_land`（落地点的地上，不跟随，不旋转）", "40 × 16",
     "卡兹克从天而降落地：地上一圈紫色的冲击波往外扩，一圈碎土和紫色闪电往外溅（参考 E_Shockwave_1、E_SmokeErode、Z_VoidLightning）。"
     "从斜上方看，**冲击波是压扁的椭圆**，**上下左右都对称**。中间是人，不要画人。6 帧。约 40 格宽、16 格高。",
     f"{BT} and {VD}",
     "a LANDING SHOCKWAVE on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM: "
     "1 a bright violet-white flattened ellipse ring 14 squares wide and 5 tall; 2-4 the ring widening to 38 squares wide "
     "and 14 tall, thinner each frame, short violet lightning cracks and dust bits thrown out along it; 5 the ring faint, "
     "sparks settling; 6 a few fading sparks.",
     row(6, 42, 18) + "; centered in every cell.", False),
    ("e_hit", "E 落地砍中（目标身上），4 帧", "view_effects `league_khazix_e_hit`（跟随，画在人物上面）", "16",
     "落地砍中：一道竖着劈下的骨白爪痕，紫色闪电在边上一跳（参考 E_glow、Q_Electric_Arcs）。约 16 格，居中画。",
     f"{BN} and {BT}",
     "a DOWNWARD CLAW HIT, 4 frames: 1 a vertical bone-white claw streak 14 squares tall through the center, a white core; "
     "2 the streak thinner, 2 short violet lightning zigzags jumping off its sides; 3 the zigzags breaking into sparks; 4 "
     "fading sparks.",
     row(4, 18, 18) + "; centered in every cell.", False),
    ("w_spike", "W 虚空突刺：飞出去的尖刺（飞行中，循环），4 帧",
     "view_projectiles `league_khazix_w_spike`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 6",
     "卡兹克甩出去的虚空尖刺：一根紫色甲壳质的尖刺，尖头朝右、发洋红色的光，后面拖一小段紫色的虚空光迹（参考 W_Spike、W_Mis_Front、W_Swirl_Core）。"
     "朝右飞。**上下对称**。4 帧无缝循环。约 16 格长、6 格高。",
     f"{SP}",
     "a VOID SPIKE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a sharp violet chitin spike 10 "
     "squares long and 3 tall, pointed at its RIGHT end with a magenta-white glowing tip, a short tapering violet glow "
     "trail 5 squares long behind it; the trail flickers and the tip glints each frame.",
     row(4, 18, 8) + "; the spike's point 1 square from the RIGHT edge, vertically centered, in every cell.", True),
    ("w_hit", "W 尖刺炸开（目标身上），5 帧", "view_effects `league_khazix_w_hit`（跟随，画在人物上面）", "20",
     "尖刺炸开：一团紫色的虚空爆炸，几根小尖刺碎片往外飞，一圈洋红色的光（参考 W_Tar、W_VoidTentacles、shards）。约 20 格，居中画。",
     f"{VD} and {BT}",
     "a VOID SPIKE BURST, 5 frames: 1 a violet-white flash 8 squares across at the center; 2 a magenta burst 16 squares "
     "across, 6 small violet spike shards flying outward; 3 the burst ring breaking up, the shards farther; 4 shards and "
     "motes fading; 5 a few motes.",
     row(5, 22, 22) + "; centered in every cell.", False),
    ("w_heal", "W 在爆炸里回血（他身上），5 帧",
     "view_effects `league_khazix_w_heal`（不跟随，左右对称；中心在站位点上面约 16 格）", "22 × 30",
     "卡兹克在尖刺的爆炸范围里回血：身边几缕淡绿色的光往上飘，几个小十字（参考 Default_Glow）。**左右对称**，**中间留空**（人在中间）。"
     "5 帧：1–2 从脚边升起，3–4 绕身体往上，5 头顶散开。约 22 格宽、30 格高。",
     HL,
     f"HEALING WISPS around a figure ({FIG}), 5 frames, SYMMETRIC LEFT TO RIGHT, the middle 10 squares left empty: 4 thin "
     "pale green wisps (2 squares wide, white highlights) and 4 small plus-shaped sparkles rising from the ground on both "
     "sides, fading above its head; each frame a step higher.",
     row(5, 24, 32) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
    ("slow", "减速（目标脚下，循环），4 帧", "view_buffs `league_khazix_p_slow` 和 `league_khazix_w_slow`（同一张，画在脚下，左右对称）", "16 × 6",
     "被无形威胁或虚空突刺减速：脚下一圈紫色的虚空水洼，几缕紫雾往外散（参考 W_Tar、Z_Void）。**左右对称**。4 帧无缝循环。约 16 格宽、6 格高。",
     VD,
     "a SLOWING VOID PUDDLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: a flat violet "
     "ellipse puddle 14 squares wide and 4 tall, 2 thin magenta ripple rings spreading out from it and tiny motes rising "
     "each frame.",
     row(4, 18, 8) + "; centered in every cell.", False),
    # ---- R
    ("r_cast", "R 虚空来袭：隐身时炸开的虚空雾（他身上），6 帧",
     "view_effects `league_khazix_r_cast`（技能第一 tick 播放、跟随；中心在站位点上面约 16 格）", "34 × 36",
     "卡兹克隐身：身边炸开一团紫黑色的虚空烟雾，一圈洋红的光环往外扩，几片甲壳状的碎影散开（参考 R_Ring、R_End_Mult、R_Shed、smoke）。"
     "**左右对称**，**中间留空**（人在中间）。6 帧：1 光环亮起，2–4 烟雾炸开、光环扩大，5–6 烟雾散开淡去。约 34 格宽、36 格高。",
     VD,
     f"a VOID SMOKE BURST around a figure ({FIG}), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly "
     "empty: 1 a thin magenta ring 16 squares across at the center; 2-4 the ring growing to 32 squares, puffs of dark "
     "violet and magenta smoke bursting out round it, small chitin-shaped flakes flying off; 5-6 the smoke thinning and "
     "fading upward.",
     row(6, 36, 38) + "; the figure's place horizontally centered, its feet 3 squares above the bottom, in every cell.", False),
    ("r_on", "R 隐身中（他身上，循环），4 帧", "view_buffs `league_khazix_r_on`（跟随，画在他身上，左右对称）", "30 × 40",
     "隐身中：他身体外面一圈淡淡的紫色波纹在闪，像空气被扭曲（参考 R_Evo2_Ring、R_Ring、Z_Void）。**左右对称**，**中间留空**（人在中间，"
     "游戏会把隐身的他画淡）。4 帧无缝循环。约 30 格宽、40 格高。",
     VD,
     f"a STEALTH SHIMMER outline around a figure ({FIG}), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT, the middle 20 "
     "squares wide left empty: thin broken violet and magenta wavy lines (1 square thick) tracing a tall oval 28 squares "
     "wide and 38 tall, a few motes drifting up; each frame the lines shift and break in different places.",
     row(4, 32, 42) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
    # ---- evolutions and the E reset
    ("e_reset", "击杀刷新 E（他身上，一闪），5 帧",
     "view_effects `league_khazix_e_reset`（不跟随，左右对称；中心在站位点上面约 20 格）", "24",
     "进化虫翼后击杀英雄刷新跃击：他身边一圈紫色光环收紧、一对翅膀形状的光闪一下（参考 Ring_Pickup、Lantern_Ring）。**左右对称**。约 24 格，居中画。",
     f"{BT} and {VD}",
     "a RESET FLASH, 5 frames, SYMMETRIC LEFT TO RIGHT: 1 a violet ring 22 squares across; 2 the ring shrinking to 14, a pair "
     "of thin wing-shaped light streaks flaring out left and right; 3 the ring 8 across and brightest, a white core; 4 a "
     "white flash; 5 fading sparks.",
     row(5, 26, 26) + "; centered in every cell.", False),
    ("evo", "进化（他身上），8 帧",
     "view_effects `league_khazix_evo`（不跟随，左右对称；中心在站位点上面约 18 格）", "34 × 40",
     "进化：他身边卷起一团紫色和洋红的虚空漩涡往上收，几道紫色闪电，最后一下白光（参考 R_End_Mult 的漩涡、Z_VoidLightning、Magma_Flash）。"
     "**左右对称**，**中间留空**（人在中间）。8 帧：1–3 漩涡从脚下卷起，4–5 闪电，6 最亮的白光，7–8 散开。约 34 格宽、40 格高。",
     f"{VD} and {BT}",
     f"an EVOLUTION SURGE around a figure ({FIG}), 8 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly empty: "
     "1-3 a magenta-violet spiral of void energy rising from the ground round the figure's place, up to 36 squares high; "
     "4-5 4 violet lightning bolts crackling along the spiral; 6 a white flash 20 squares across at the middle; 7-8 the "
     "energy bursting outward into motes and fading.",
     row(8, 36, 42) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
]

GROUPS = [
    ("attack / Q", ["Khazix_Base_Q_Slash", "Khazix_Base_Q_impact", "Khazix_Base_Q_Impact_04", "Khazix_Base_Q_Lightning02",
                    "Khazix_Base_Q_SingleEnemy_Indicator02_Reticle", "Hit_Spark_blue"]),
    ("passive", ["Khazix_Base_P_OuterRing", "Khazix_Base_P_Glow_01", "Khazix_Base_P_InnerCore", "Khazix_Base_Flames2",
                 "Khazix_Base_NegaSparkle", "Khazix_Base_P_Passive_Target_Ring"]),
    ("E", ["Khazix_Base_E_Shockwave_1", "Khazix_Base_E_SmokeErode", "Khazix_Base_E_WeaponTrails_smoke_Trail",
           "Khazix_Base_E_glow", "Khazix_Base_Q_Electric_Arcs", "Khazix_Base_Z_VoidLightning"]),
    ("W", ["Khazix_Base_W_Spike", "Khazix_Base_W_Mis_Front", "Khazix_Base_W_Swirl_Core", "Khazix_Base_W_Tar",
           "Khazix_Base_W_VoidTentacles_01", "shards"]),
    ("R / evolve", ["Khazix_Base_R_Ring", "Khazix_Base_R_End_Mult", "Khazix_Base_R_Evo2_Ring", "Khazix_Base_Z_Void",
                    "Khazix_Base_Ring_Pickup", "Khazix_Base_Magma_Flash"]),
]
# where the pictures start: (tag, frame, what, marks: "feet" or [(dx, dy) from the standing point]); the W release's claw
# tip from Codex's manifest (skill2 frame 6: claw_tip (103, 79), pivot (77, 70) -> +26, +9)
SHOTS = [("skill2", 6, "w_spike: 出手（尖刺从这里飞出）", [(26, -2)]), ("skill2", 4, "e_land: 落地站位点", "feet"),
         ("ult", 1, "r_cast / r_on: 站位点", "feet"), ("idle", 1, "ut / p_ready / e_reset / evo / w_heal: 站位点", "feet")]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Khazix_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The design at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = design_1x()
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    img = Image.new("RGBA", (max(W * Z, 420), (pad + max(fig.shape[0], kn.shape[0]) + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + max(fig.shape[0], kn.shape[0])
    img.alpha_composite(Image.fromarray(fig).resize((fig.shape[1] * Z, fig.shape[0] * Z), Image.NEAREST),
                        (pad * Z, (base - fig.shape[0]) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fig.shape[1]) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.shape[1] + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"卡兹克 {fig.shape[1]}×{fig.shape[0]} 格（连触角和翅膀），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (league/champions/league_khazix, the imported sheet), each picture's starting
    point as a cyan cross (the standing point is the frame's pivot: the sheet's frames are centred on it)."""
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_khazix"))
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    px = sp.w // 2
    for tag, k, what, marks in SHOTS:
        f = np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA"))
        ys, xs = np.nonzero(f[..., 3] > 0)
        soles = int(ys.max())
        pts = [(px, soles + 1)] if marks == "feet" else [(px + dx, soles + 1 + dy) for dx, dy in marks]
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 260), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        for mx, my in pts:
            cx, cy = int((mx - x0) * Z), int((my - y0) * Z) + 24
            d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
            d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    W = sum(t.width + 10 for t in tiles)
    H = max(t.height for t in tiles)
    sheet = Image.new("RGB", (W, H), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 虚空掠夺者 卡兹克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/khazix_design.png`，8 倍，连触角和翅膀 {h} 行、{w} 格宽）。")
    a(f"> - 大小对照 `design/khazix_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。卡兹克 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/khazix_shots.png`：定稿动作（4 倍），青色十字是特效的起点（尖刺的出手点、脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡兹克自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版皮肤：**虚空是洋红和紫色（被动、Q、R、进化）；尖刺和跃击的冲击是紫色闪电；爪痕是骨白色；W 回血是淡绿色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人的烟雾、光环、火光只画外圈，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要）**：飞出去的尖刺画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "画在他身上、晚于技能开始播放的（`w_heal`、`p_ready`、`e_reset`、`evo`）和挂在他身上、脚下循环的（`ut`、`r_on`、`slow`）要**左右对称**；地上的落地冲击 `e_land` 上下左右都对称。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `khazix_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`khazix_fx_done.zip`）放在 outputs 里，或放在 `outputs/khazix-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「无形威胁」 | 镰爪攻击；隐身后或几秒没出手，下一次攻击英雄附加魔法伤害并减速 | `a_hit` · `ut` · `p_ready` · `p_hit` · `slow` |")
    a("| 技能 1 = Q「品尝恐惧」 | 爪击；目标身边没有友军（孤立无援）时伤害更高 | `q_hit` · `q_iso_hit` |")
    a("| 技能 2 = E「跃击」→ W「虚空突刺」 | 跃向敌方英雄，落地造成伤害，再甩出尖刺（伤害、减速，自己在爆炸里回血） | `e_land` · `e_hit` · `w_spike` · `w_hit` · `w_heal` · `slow` |")
    a("| 大招 = R「虚空来袭」 | 隐身并加速，可以再用 1–2 次 | `r_cast` · `r_on` |")
    a("| 进化 | 5/8/11 级依次进化 Q、E、R；进化后的 E 击杀英雄刷新 | `evo` · `e_reset` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、爪痕、火星、闪电没有黑描边，也不要用最深的颜色给形状描一圈边**。只有飞出去的尖刺（一件实物）有 1 格深色描边（`#0B0814`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空洋红（被动、Q、R、进化、减速）", VOID), ("紫色闪电（落地冲击、尖刺爆炸、刷新）", BOLT),
                        ("骨白（爪痕）", BONE), ("淡绿（W 回血）", HEAL), ("尖刺本体（紫色甲壳）", SPIKE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 23000，"
      "孤立判定半径 30000，跃击落地半径 22000，尖刺宽 6000、爆炸回血范围 30000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout, obj) in enumerate(FX, 1):
        a(f"### {k}. `khazix_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a((LEAD_OBJ if obj else LEAD).format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `khazix_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `w_spike` 从出手点出（甩刺那帧爪尖在站位点前面约 26 格、贴近地面；`y_offset` 定在 2000–6000，画面开头补几帧空的，让尖刺离开爪子再出现）。")
    a("- `r_cast` 在动作第一 tick 播放、跟随；`w_heal`、`p_ready`、`e_reset`、`evo` 晚于第一 tick，`is_follow` 为 false，左右对称；`e_land` 在地上，不跟随。"
      "`slow` 一张图给 `p_slow` 和 `w_slow` 两个 buff 用（tools/kit/build_khazix.py 的绑定改成同一个 tag）。")
    a("- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim`，尖刺保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，"
      "和包里别的英雄比；飞行的画面上下对称；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="khazix_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", help="folder for the zip (default: next to the pack folder)")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out or os.path.join(TMP, "fx"), a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: extract Kha'Zix's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "khazix_design.png"))
    shape = size_sheet(os.path.join(out, "design", "khazix_size.png"))
    shots_sheet(os.path.join(out, "design", "khazix_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"khazix_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC)
    if not a.no_zip:
        os.makedirs(os.path.dirname(zpath), exist_ok=True)
        if os.path.exists(zpath):
            os.remove(zpath)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(zpath) // 1024, "KB")


if __name__ == "__main__":
    main()
