#!/usr/bin/env python3
"""Build pyke_fx_pack.zip: step 3 of Pyke's sprite - Codex draws his effects (after tools/art/pack_samira_fx.py).

    python tools/art/pack_pyke_fx.py [--no-zip] [--out DIR] [--only q_hook,q_hit --name pyke_fx_redo_pack]

The pack (%TEMP%/pk_work/fx/pyke_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/pyke/PROMPTS_FX.md), design/pyke_design.png (8x), design/pyke_size.png (the design at 4x on the arena
colour with the feet line, a 10-px ruler and the base fighter beside him), design/pyke_shots.png (the finished action
frames at 4x - tools/art/rig_pyke.py - with the point each picture starts from) and refs/lol_fx_ref.png (League's own
particle textures for Pyke, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/pk_work/fxref, extracted from Pyke.wad.client by the session's fx_ref_pk.py).
The effects are the views the kit binds (tools/kit/build_pyke.py: view_projectiles q_hook / q_hook_c (one picture),
q_return (q_hook mirrored at import), e_phantom; view_effects a_hit, q_charge, q_stab_hit, q_hit, w_cast, e_left, e_hit,
r_mark, r_strike, r_hit, r_reset, p_heal; view_buffs q_slow, e_stun). League's colours: the drowned ghost-water teal
(W, E's phantom, the grey health), the harpoon's bone white, blood red for R's execute, gold for the bounty. Light,
water and blood get no outline (the bright-effects lesson). Red side: projectiles symmetric top to bottom, pictures on
him after the first tick (r_reset, p_heal) symmetric left to right, the ground pictures (e_left, r_mark, r_strike)
symmetric both ways.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "pk_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "pyke", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "pyke_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


WATER = "#FFFFFF, #D8FFF8, #8CF4E6, #3CCFC8, #16929E, #0B5466"   # drowned ghost water: W, E, the grey health
BONE = "#FFFFFF, #FFF8E0, #E8D8AA, #C8B484, #8E7A54"             # the harpoon's blade and its flash
STEEL = "#F6D48C, #E09A40, #B86A28, #9A1020, #D81A26"            # the harpoon's gold guard and red-wrapped shaft
BLOOD = "#FFFFFF, #FFC8C0, #FF5A4A, #D01E2A, #8A0A1C, #4A0612"   # R's execute
GOLD = "#FFFFFF, #FFF0A0, #FFD040, #E89A10, #A85A08"             # the bounty
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around water, light, slashes, blood or sparks, BRIGHT colours (each shape lit with its lightest shades "
        "and a white core - it must read on a dark battlefield), colours only from {ramps}.")
LEAD_OBJ = ("Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
            "a 1-square dark outline #0A0608 around the object, colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FIG = "do NOT draw the figure; leave its place empty"
WT = f"a ghost-water ramp ({WATER})"
BN = f"a bone ramp ({BONE})"
ST = f"the harpoon's gold and red ({STEEL})"
BL = f"a blood ramp ({BLOOD})"
GL = f"a gold ramp ({GOLD})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout, outlined object
FX = [
    # ---- the attack and Q
    ("a_hit", "普攻鱼叉砍中（目标身上），4 帧", "view_effects `league_pyke_a_hit`（跟随，画在人物上面）", "14",
     "鱼叉砍中：一道斜着的骨白色刀痕闪过，白色的芯，几滴幽绿色的水花溅出去（参考 BA_hit_flash、BA_hit_blend、BA_hit_glow）。约 14 格，居中画。",
     f"{BN} and {WT}",
     "a HARPOON SLASH HIT, 4 frames: 1 a diagonal bone-white slash streak 12 squares long through the center (from the top "
     "right down to the bottom left), a white core; 2 the streak thinner, a white flash 5 squares across at its middle, "
     "teal water droplets flying out; 3 droplets scattering; 4 a few fading drops.",
     row(4, 16, 16) + "; centered in every cell.", False),
    ("q_charge", "Q 蓄力：举起的鱼叉上聚起的光（画在他身上，循环），4 帧",
     "view_effects `league_pyke_q_charge`（动作第一 tick 播放、跟随；`design/pyke_shots.png` skill 2 的十字）", "12",
     "派克蓄力扔鱼叉时，举在身后的叉刃上聚起一团幽绿的水光，几点光屑往里收（参考 Q_chargeup_glow、Q_channel_flares）。**左右对称**的一团光，"
     "4 帧循环（一明一暗、光屑往里收）。约 12 格。",
     WT,
     "a CHARGING GLOW, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: a teal-white glowing orb 5 squares across at the "
     "center, 6 small teal motes drawn inward toward it from 5 squares out; the orb pulses brighter and dimmer.",
     row(4, 12, 12) + "; centered in every cell.", False),
    ("q_hook", "Q 扔出去的鱼叉（飞行中，循环），4 帧",
     "view_projectiles `league_pyke_q_hook` / `q_hook_c`（朝飞行方向转，画成朝右飞；上下对称）；`q_return` 是它的镜像（收回）", "26 × 8",
     "派克扔出去的鱼叉：骨白色的宽叉刃在前（**两边都有倒钩，上下对称**），古铜金的护手和一颗青宝石，红布缠的杆子，尾巴拖一小段幽绿的水迹和一截暗色的绳子"
     "（参考 Q_ranged_mis_glow、Q_rope_trail、Q_Mis_Filler）。朝右飞。4 帧无缝循环（水迹抖动、宝石一闪）。约 26 格长、8 格高。",
     f"{BN}, {ST} and {WT}",
     "a THROWN HARPOON flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: at the front a wide "
     "bone-white blade 9 squares long with jagged barbs on BOTH edges (mirror-symmetric), a gold guard 2 squares wide with "
     "a cyan gem in its middle, a red-wrapped shaft 2 squares thick and 10 squares long, a short teal water trail and a "
     "dark rope 5 squares long behind it; the trail shimmers and the gem glints each frame.",
     row(4, 28, 10) + "; the blade's point 1 square from the RIGHT edge, vertically centered, in every cell.", True),
    ("q_hit", "Q 鱼叉钩中（目标身上），5 帧", "view_effects `league_pyke_q_hit`（跟随，画在人物上面）", "16",
     "鱼叉钩中：一颗白色的尖星形闪光，一圈幽绿色的水花炸开，几滴水往外飞（参考 Q_hit_tar_flash、Q_hit_blend、Q_splash_circular）。约 16 格，居中画。",
     WT,
     "a HARPOON HOOK HIT, 5 frames: 1 a white sharp eight-pointed star flash 8 squares across at the center; 2 the star "
     "smaller, a ring of teal water splash 12 squares across bursting out; 3 the splash wider and broken into droplets; "
     "4 droplets falling; 5 a few fading drops.",
     row(5, 18, 18) + "; centered in every cell.", False),
    ("q_stab_hit", "Q 近身戳刺打中（目标身上），4 帧", "view_effects `league_pyke_q_stab_hit`（跟随，画在人物上面）", "16 × 10",
     "近身戳刺打中：一道横着的白色骨刺穿透闪光（朝右的尖），后面一小团幽绿水花（参考 Q_melee_shape、P_Hit_tar_sharp）。**上下对称**。约 16 格宽、10 格高，居中画。",
     f"{BN} and {WT}",
     "a STAB HIT, 4 frames, SYMMETRIC TOP TO BOTTOM: 1 a horizontal white-hot spike streak 14 squares long through the "
     "center, pointed at its RIGHT end, a white flash 4 squares across at the center; 2 the streak thinner, a puff of teal "
     "water droplets behind it; 3 droplets scattering; 4 fading drops.",
     row(4, 18, 12) + "; centered in every cell.", False),
    # ---- W -> E
    ("w_cast", "W 潜入：脚下炸开的幽水（画在他身上），5 帧",
     "view_effects `league_pyke_w_cast`（技能第一 tick 播放、跟随；中心在站位点）", "28 × 16",
     "派克潜入幽水：脚下一圈幽绿色的水花往上炸开，一片鲨鱼鳍形的水影从中间划过（参考 W_start_burstwater、W_waterpattern、W_shark_fin、W_wisps）。"
     "**左右对称**。中间是人，不要画人。5 帧：1 地面一圈水纹，2 水花往上炸到腰高，3 最高、水滴，4 落下，5 地面水迹淡去。约 28 格宽、16 格高，站位点在格子底部往上 3 格的中间。",
     WT,
     f"a WATER BURST around a figure's feet ({FIG}), 5 frames, SYMMETRIC LEFT TO RIGHT: 1 a flat ellipse ripple 24 squares "
     "wide and 6 tall on the ground at the standing point; 2 teal water splashing UP from its rim to 10 squares high; 3 "
     "the splash at its highest, droplets, white crests; 4 the water falling back; 5 a fading ripple on the ground.",
     row(5, 30, 18) + "; the standing point 3 squares above the bottom, horizontally centered, in every cell.", False),
    ("e_left", "E 冲刺起点留下的幽水水洼（地上，魅影从这里飞回），6 帧",
     "view_effects `league_pyke_e_left`（放在冲刺起点的地上，不跟随，不旋转）", "26 × 10",
     "派克冲出去时，起点留下一滩幽绿色的水洼，水面上一个人形的影子往上浮（参考 E_puddle、E_ground_puddle、E_Start_water_spout）。**左右对称**。"
     "6 帧：1 水洼出现，2–4 水洼泛着水纹、中间一道水柱往上冒（魅影要出来了），5 水柱散开，6 水洼淡去。约 26 格宽、10 格高（水柱可以高到 14 格），格子底部往上 4 格的中间是水洼中心。",
     WT,
     "a GHOST-WATER PUDDLE on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT: 1 a flat teal ellipse puddle 20 squares wide "
     "and 5 tall appears; 2-4 the puddle ripples, a narrow teal water spout rising from its middle up to 12 squares high, "
     "white crests; 5 the spout bursting into droplets; 6 the puddle fading.",
     row(6, 28, 18) + "; the puddle's center 4 squares above the bottom, horizontally centered, in every cell.", False),
    ("e_phantom", "E 飞回来的溺毙魅影（飞行中，循环），4 帧",
     "view_projectiles `league_pyke_e_phantom`（朝飞行方向转，画成朝右飞；上下对称）", "24 × 12",
     "从水洼飞回派克身边的溺毙魅影：一股向前冲的幽绿色水流，前端是一个模糊的魅影（发光的两点眼睛、骨白色的獠牙轮廓），后面拖长长的水尾"
     "（参考 E_clone_trail、E_clone_wave、E_beam_mult、E_WaterTrail）。朝右飞。**上下对称**。4 帧无缝循环。约 24 格长、12 格高。",
     WT,
     "a DROWNED PHANTOM rushing to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: at the front a "
     "translucent-looking teal ghost head 8 squares tall with two glowing white eyes side by side and pale bone-white "
     "fang shapes along its front edge, behind it a long tapering wave of teal water 16 squares long; the wave ripples "
     "and the eyes flicker each frame.",
     row(4, 26, 14) + "; the head's front 2 squares from the RIGHT edge, vertically centered, in every cell.", False),
    ("e_hit", "E 魅影穿过、晕眩（目标身上），5 帧", "view_effects `league_pyke_e_hit`（跟随，画在人物上面）", "18",
     "魅影穿过英雄：一道横着冲过的幽绿水流，一颗白色闪光，水花往两边溅（参考 E_hit_dark、E_watersplashes、E_land_splash）。约 18 格，居中画。",
     WT,
     "a GHOST-WATER HIT, 5 frames: 1 a horizontal teal water streak 16 squares long rushing through the center, a white "
     "flash 6 squares across; 2 the water bursting into splashes above and below; 3 splashes wider; 4 droplets "
     "falling; 5 fading drops.",
     row(5, 20, 20) + "; centered in every cell.", False),
    ("e_stun", "E 晕眩（目标头顶，循环），4 帧", "view_buffs `league_pyke_e_stun`（画在头顶，左右对称）", "14 × 7",
     "被魅影晕住：头顶一圈转着的幽绿小水珠和两三个白色小星（参考 Z_waterbits、Z_BightSpark）。**左右对称**。4 帧无缝循环。约 14 格宽、7 格高。",
     WT,
     "a STUN RING over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: a flat ellipse ring 12 squares wide and "
     "4 tall of 6 small teal water beads and 2 tiny white stars circling round, each frame the beads moved a step along "
     "the ring.",
     row(4, 16, 8) + "; centered in every cell.", False),
    ("q_slow", "Q 减速（目标脚下，循环），4 帧", "view_buffs `league_pyke_q_slow`（画在脚下，左右对称）", "16 × 6",
     "被鱼叉戳中或钩中后的减速：脚下一圈幽绿色的水洼，几道水纹往外扩（参考 Z_splash_circular、P_hand_puddle）。**左右对称**。4 帧无缝循环。约 16 格宽、6 格高。",
     WT,
     "a SLOWING PUDDLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: a flat teal ellipse "
     "puddle 14 squares wide and 4 tall, 2 thin pale ripple rings spreading out from it each frame.",
     row(4, 18, 8) + "; centered in every cell.", False),
    # ---- R
    ("r_mark", "R 涌泉之恨：地上的 X 形预警（0.5 秒），6 帧",
     "view_effects `league_pyke_r_mark`（放在 X 的中心，地上，不跟随，不旋转）", "56 × 28",
     "大招的预警：地上一个大大的 X（两把交叉的鱼叉形状），暗红色的轮廓、中间幽绿的光慢慢亮起来（参考 R_indicator、R_indicator_glow、R_ground_mult）。"
     "从斜上方看，**X 是压扁的（宽是高的 2 倍）**，**上下左右都对称**。6 帧：1 X 淡淡出现，2–5 越来越亮、边缘发红光，6 最亮（马上要斩下来）。约 56 格宽、28 格高。",
     f"{BL} and {WT}",
     "a GROUND X-MARK seen from above at an angle (flattened: twice as wide as tall), 6 frames, SYMMETRIC LEFT TO RIGHT "
     "AND TOP TO BOTTOM: two crossing bars like two crossed harpoons, each bar 4 squares thick, from corner to corner of a "
     "54 x 26 square area, dark blood-red edges and a teal glow along their middle; 1 faint; 2-5 brighter and brighter, "
     "the red edges glowing; 6 at its brightest, a white line along the middle of each bar.",
     row(6, 58, 30) + "; centered in every cell.", False),
    ("r_strike", "R 斩下来：X 形的血色斩击，5 帧",
     "view_effects `league_pyke_r_strike`（放在 X 的中心，地上，不跟随，不旋转；落下前 0.1 秒开始）", "58 × 34",
     "派克从天而降、沿着 X 斩下：两道交叉的白热血红色斩痕，中间爆开一团暗红和幽绿的水花，往上溅起几根水刺（参考 R_slash、R_cas_strike、R_spike2、"
     "R_TarBig_splash、R_waterspike）。**左右对称**。5 帧：1 两道斩痕最亮（白芯红边），2 斩痕变细、中间水花炸开、水刺往上，3 水刺最高，4 落下、血红水滴，5 淡去。"
     "约 58 格宽、34 格高，X 的中心在格子底部往上 12 格的中间。",
     f"{BL} and {WT}",
     "an X-SHAPED STRIKE on the ground, 5 frames, SYMMETRIC LEFT TO RIGHT: 1 two crossing slash streaks along the "
     "diagonals of a 54 x 24 square flattened area, each 3 squares thick, white-hot cores with blood-red edges; 2 the "
     "streaks thinner, a burst of dark blood-red and teal water at the center, 4 water spikes shooting UP to 20 squares "
     "high; 3 the spikes at their highest; 4 the spikes falling into blood-red droplets; 5 fading drops and a faint X.",
     row(5, 60, 36) + "; the X's center 12 squares above the bottom, horizontally centered, in every cell.", False),
    ("r_hit", "R 斩中英雄（目标身上），5 帧", "view_effects `league_pyke_r_hit`（跟随，画在人物上面）", "20",
     "大招斩中：一道竖着劈下的白热血红斩痕，暗红色的血水往两边炸开（参考 R_execute_beam、R_burstSmoke、R_color-bloodfade）。约 20 格，居中画。",
     BL,
     "an EXECUTE HIT, 5 frames: 1 a vertical white-hot slash streak 18 squares tall through the center with blood-red "
     "edges; 2 the streak thinner, a burst of dark blood-red splash 14 squares across; 3 splash wider, droplets; 4 "
     "droplets falling; 5 fading drops.",
     row(5, 22, 22) + "; centered in every cell.", False),
    ("r_reset", "R 处决成功：赏金（他身上），6 帧",
     "view_effects `league_pyke_r_reset`（不跟随，左右对称；中心在站位点上面约 20 格）", "24",
     "大招处决了英雄：派克身边炸开一圈金币和金光，一道血红的光环往外扩（英雄联盟里处决会分赏金；参考 R_bodyglow、Kayn_Sparks）。**左右对称**。"
     "6 帧：1 金光，2–4 金币往外往上飞、血红光环扩大，5–6 金币落下淡去。约 24 格，居中画。",
     f"{GL} and {BL}",
     "a BOUNTY BURST, 6 frames, SYMMETRIC LEFT TO RIGHT: 1 a white-gold flash 8 squares across at the center; 2-4 8 small "
     "gold coins (2-3 squares each, a white glint) flying out and up, a thin blood-red ring expanding to 22 squares "
     "across; 5-6 the coins falling and fading, the ring fading.",
     row(6, 26, 26) + "; centered in every cell.", False),
    # ---- the passive
    ("p_heal", "被动 溺水之幸：灰血回复（他身上），6 帧",
     "view_effects `league_pyke_p_heal`（不跟随，左右对称；中心在站位点上面约 18 格）", "22 × 32",
     "灰血回复：身边几缕幽绿色的水雾往上飘，绕着身体收进去（参考 Passive_Wisps、Passive_flash_halo、W_wisps）。**左右对称**，**中间留空**（人在中间）。"
     "6 帧：1–2 水雾从脚边升起，3–4 绕着身体往上飘，5–6 在头顶散开淡去。约 22 格宽、32 格高。",
     WT,
     f"HEALING WISPS around a figure ({FIG}), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 10 squares left empty: 4 thin "
     "teal wisps (2 squares wide, white highlights) rising from the ground on both sides, curling up around the figure's "
     "place, fading above its head; each frame the wisps a step higher.",
     row(6, 24, 34) + "; the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell.", False),
]

GROUPS = [
    ("Q", ["Pyke_Base_Q_ranged_mis_glow", "Pyke_Base_Q_rope_trail", "Pyke_Base_Q_hit_tar_flash", "Pyke_Base_Q_hit_blend",
           "Pyke_Base_Q_splash_circular", "Pyke_Base_Q_chargeup_glow_blend"]),
    ("attack", ["Pyke_Base_BA_hit_flash", "Pyke_Base_BA_hit_blend", "Pyke_Base_BA_hit_glow_blend", "Pyke_Base_P_Hit_tar_sharp",
                "Pyke_Base_Q_melee_shape", "Pyke_Base_Z_waterbits"]),
    ("W", ["Pyke_Base_W_start_burstwater", "Pyke_Base_W_waterpattern_base", "Pyke_Base_W_shark_fin", "Pyke_Base_W_wisps",
           "Pyke_Base_W_flash", "Pyke_Base_Passive_Wisps"]),
    ("E", ["Pyke_Base_E_puddle", "Pyke_Base_E_clone_trail", "Pyke_Base_E_clone_wave", "Pyke_Base_E_beam_mult",
           "Pyke_Base_E_hit_dark", "Pyke_Base_E_watersplashes"]),
    ("R", ["Pyke_Base_R_indicator", "Pyke_Base_R_indicator_glow_init", "Pyke_Base_R_slash", "Pyke_Base_R_cas_strike",
           "Pyke_Base_R_spike2", "Pyke_Base_R_execute_beam"]),
]
# where the pictures drawn on him start: (tag, frame, what, marks: "feet" or [(dx, dy) from the standing point])
SHOTS = [("skill", 2, "q_charge: 叉刃", [(-14, -40)]), ("skill", 5, "q_hook: 出手（鱼叉从这里飞出）", [(-5, -31)]),
         ("skill2", 1, "w_cast: 站位点", "feet"), ("ult", 4, "r_strike / r_mark: 落在目标处（这里只标站位点）", "feet"),
         ("idle", 1, "p_heal / r_reset: 站位点", "feet")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Pyke_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"派克 {fig.shape[1]}×{fig.shape[0]} 格（连举起的鱼叉），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (rig_pyke.py), each picture's starting point as a cyan cross."""
    import rig_pyke as RP
    built = RP.Rig().build()
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    px, soles = RP.PIVOT[0], RP.SOLES
    for tag, k, what, marks in SHOTS:
        f = built[tag][k - 1]
        pts = [(px, soles + 1)] if marks == "feet" else [(px + dx, soles + 1 + dy) for dx, dy in marks]
        ys, xs = np.nonzero(f[..., 3] > 0)
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
    a("# 血港鬼影 派克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/pyke_design.png`，8 倍，连举起的鱼叉 {h} 行，光头顶到脚底 40 行）。")
    a(f"> - 大小对照 `design/pyke_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。派克 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/pyke_shots.png`：定稿动作（4 倍），青色十字是特效的起点（叉刃、出手点、脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里派克自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版皮肤：**溺毙的幽水是青绿色（W、E 的魅影、被动的灰血）；鱼叉是骨白色、金护手、青宝石、红缠杆；大招的处决是暗血红；处决赏金是金色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人、脚下的水花和水雾只画外圈，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要）**：飞行的东西（扔出去的鱼叉、飞回来的魅影）一律画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻，所以鱼叉两边都画倒钩）。"
      "画在他身上、晚于技能开始播放的（`r_reset`、`p_heal`）和挂在头顶、脚下的（`e_stun`、`q_slow`）要**左右对称**；地上的 X（`r_mark`、`r_strike`）和水洼 `e_left` 上下左右都对称。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `pyke_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`pyke_fx_done.zip`）放在 outputs 里，或放在 `outputs/pyke-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「溺水之幸」 | 鱼叉挥砍；挨打积攒灰血，潜行或几秒没挨打时回复 | `a_hit` · `p_heal` |")
    a("| 技能 1 = Q「透骨尖钉」 | 英雄贴身时戳刺（伤害+减速），否则蓄力把鱼叉扔出去，钩中第一个敌人拉回来 | `q_charge` · `q_hook`（收回时镜像）· `q_hit` · `q_stab_hit` · `q_slow` |")
    a("| 技能 2 = W「幽潭潜行」→ E「魅影浪洄」 | 潜行加速贴近，冲过敌方英雄；起点留下一滩水，魅影随后飞回他身边，途经的英雄被晕眩 | `w_cast` · `e_left` · `e_phantom` · `e_hit` · `e_stun` |")
    a("| 大招 = R「涌泉之恨」 | 目标处出现 X 形预警，0.5 秒后斩下：血量低的英雄被处决，其余受一半伤害；处决后可以再放 | `r_mark` · `r_strike` · `r_hit` · `r_reset` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水、光、刀光、血、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。只有扔出去的鱼叉（一件实物）有 1 格深色描边（`#0A0608`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("幽水（W、E、被动、减速、晕眩）", WATER), ("骨白（鱼叉刃、刀痕）", BONE), ("鱼叉的金和红", STEEL),
                        ("血红（大招）", BLOOD), ("金色（赏金）", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 24000，"
      "鱼叉射程 95000、宽 6000，魅影宽 12000，R 的 X 半径 28000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout, obj) in enumerate(FX, 1):
        a(f"### {k}. `pyke_fx_{name}.png`：{title}\n")
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
        a(f"| `pyke_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `q_return` = `q_hook` 左右镜像（收回的鱼叉尾巴朝前）；`q_hook` 从出手点出（扔出那帧手在站位点上面约 31 格、后面 5 格）：`y_offset` 不超过 8000，"
      "画面开头补几帧空的，让鱼叉飞过手再出现。")
    a("- `q_charge`、`w_cast` 在动作第一 tick 播放、跟随；`r_reset`、`p_heal` 晚于第一 tick，`is_follow` 为 false，左右对称；`e_left`、`r_mark`、`r_strike` 在地上，不跟随。")
    a("- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim`，鱼叉保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，"
      "和包里别的英雄比；飞行的画面上下对称；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="pyke_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Pyke's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "pyke_design.png"))
    shape = size_sheet(os.path.join(out, "design", "pyke_size.png"))
    shots_sheet(os.path.join(out, "design", "pyke_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"pyke_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
