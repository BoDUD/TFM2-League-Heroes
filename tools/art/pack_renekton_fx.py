#!/usr/bin/env python3
"""Build renekton_fx_pack.zip: step 3 of Renekton's sprite - Codex draws his effects (after tools/art/pack_twitch_fx.py).

    python tools/art/pack_renekton_fx.py [--no-zip] [--out DIR] [--only a_hit,q_spin --name renekton_fx_redo_pack]

The pack (%TEMP%/rk_work/fx/renekton_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/renekton/PROMPTS_FX.md), design/renekton_design.png (8x), design/renekton_size.png (the design at 4x on the
arena colour with the feet line, a 10-px ruler and the base fighter beside him), design/renekton_shots.png (the finished
action frames at 4x from league/champions/league_renekton, with the point each picture starts from) and
refs/lol_fx_ref.png (League's own particle textures for Renekton, grouped by the effect of ours they inform; Riot's art,
local only: it reads %TEMP%/rk_work/fxref, extracted from Renekton.wad.client).
The effects are the views the kit binds (tools/kit/build_renekton.py: view_effects a_hit, q_hit, q_spin, q_spin_e,
e_hit, w_hit, w_glow, r_cast, r_burn; view_buffs f5, w_stun, e_shred, r_on) and two pictures with a front and a back
baked into his frames (renekton_bake.json): the attack's slash a_slash and E's dash streak e_dash. League's colours:
the blade's ivory light (the slashes, Q), Fury's red (empowered skills, full Fury, R), the desert's sand (E, R), gold
stun stars. Light, sand and splashes get no outline. Red side: the hits, the buffs and the pictures on him after the
first tick symmetric left to right. Codex also delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rk_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "renekton", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "renekton_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


BLADE = "#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C"                # the blade's ivory light: slashes, Q
RAGE = "#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E"         # Fury red: empowered skills, full Fury, R
SAND = "#FFF6D8, #F4DC98, #DCB460, #B88838, #84602A"                 # desert sand: E's dash, R's storm
STAR = "#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C"                 # gold: stun stars, R's scarab sign
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades "
        "and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
FIG = "do NOT draw the figure; leave its place empty"
BL = f"an ivory blade-light ramp ({BLADE})"
RG = f"a fury red ramp ({RAGE})"
SD = f"a desert sand ramp ({SAND})"
ST = f"a gold ramp ({STAR})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack
    ("a_slash", "普攻刀光（烘进普攻第 3 帧），3 帧",
     "烘进普攻出手帧（`renekton_bake.json`：刀刃中点，随人物朝向翻转）", "30 × 18",
     "月牙刀砍出去的那一道刀光：一道象牙白的弧形刀光从左上扫到右前方，弧的外缘最亮（参考 BA_trail、Q_cas_swipetrail、Z_Glow_Trail）。"
     "朝右砍。3 帧：亮出、拖长、消散。约 30 格宽、18 格高。",
     BL,
     "a CRESCENT SLASH ARC swung to the RIGHT, 3 frames: 1 a thick bright white-ivory arc 24 squares wide curving from the "
     "upper left down to the right, its outer edge white, thinning to a point at both ends; 2 the arc longer (28 squares) "
     "and thinner, pale ivory, a few sparks at its front end; 3 the arc breaking into fading ivory streaks.",
     row(3, 32, 20) + "; the arc's middle at the center of every cell.", False),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_renekton_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "刀砍中：一个象牙白的 X 形十字刀痕，几粒白色火星往外溅（参考 common_HitEffect、common_color-hit-physical）。"
     "**左右对称**（X 形）。约 12 格，居中画。",
     BL,
     "a CROSS SLASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a white X of two crossing slash marks 8 "
     "squares across at the center; 2 the X 12 squares across, ivory, 6 sparks flying out evenly on both sides; 3 the X "
     "fading, sparks farther; 4 a few fading sparks.",
     row(4, 14, 14) + "; centered in every cell.", False),
    # ---- Q
    ("q_spin", "Q 巨鳄狂袭：绕身一圈的刀光（脚下到腰，地上的椭圆），6 帧",
     "view_effects `league_renekton_q_spin`（画在他身上，`is_follow` false；左右对称）", "64 × 22",
     "Q 横扫一圈：一圈象牙白的弧形刀光绕着他转一圈，是斜上方看下去的扁椭圆（宽是高的约 3 倍），刀光前面亮、后面淡，地上扬起一点沙尘"
     "（参考 Q_cas_swipetrail、Q_cas_color-swipetrail、Q_cas_Shadow、Oriental_Dust_2x2）。**只画外圈，中间留空**（人站在中间）。"
     "**每一帧都左右对称**（不要画成转动的方向：用一整圈同时变亮再散开表现横扫）。约 64 格宽、22 格高。",
     f"{BL} and {SD}",
     "a SPIN SLASH RING round a figure, seen from above at an angle (a flat ellipse three times as wide as tall), 6 frames, "
     "SYMMETRIC LEFT TO RIGHT in every frame, " + FIG + ": 1 a thin pale ivory ellipse 40 squares wide appears at "
     "waist height; 2 the ring of blade light widens to 56 squares, a thick bright white-ivory band, brightest at its "
     "front (bottom) edge; 3 the full ring 62 squares wide, white sparks flung out on both sides, a little sand dust "
     "rising from the ground on both sides; 4 the ring thinning, the dust spreading; 5 fading streaks of ivory and sand; "
     "6 last motes. The middle of the ellipse stays EMPTY.",
     row(6, 66, 24) + "; the ellipse centered in every cell.", False),
    ("q_spin_e", "Q 强化（满怒气）：更大的红色刀光圈，6 帧",
     "view_effects `league_renekton_q_spin_e`（画在他身上，`is_follow` false；左右对称）", "72 × 26",
     "满怒气的 Q：同一圈刀光，但更大、是怒气的红橙色，带一圈热浪和火星（参考 Q_cas_rage_swipetrail、Q_cas_rage_renekton_runewars_swipe、"
     "Q_cas_rage_Aura_self、Q_cas_rage_color-bellcurve32）。**只画外圈，中间留空**；**每一帧左右对称**。约 72 格宽、26 格高。",
     f"{RG} and {BL}",
     "an EMPOWERED SPIN SLASH RING round a figure, a flat ellipse three times as wide as tall, 6 frames, SYMMETRIC LEFT TO "
     "RIGHT in every frame, " + FIG + ": 1 a red-orange ellipse 46 squares wide flares at waist height; 2 a thick ring of "
     "red fury light with a white-hot inner edge, 64 squares wide; 3 the full ring 70 squares wide, red and orange sparks "
     "and heat flames licking up on both sides; 4 the ring breaking into red streaks; 5 fading embers; 6 last sparks. "
     "The middle of the ellipse stays EMPTY.",
     row(6, 74, 28) + "; the ellipse centered in every cell.", False),
    ("q_hit", "Q 打中（每个被扫到的敌人身上），4 帧", "view_effects `league_renekton_q_hit`（跟随，画在人物上面；左右对称）", "12",
     "Q 扫中：一道横着的象牙白刀痕穿过身体，两边溅出几粒火星和一点红色（参考 common_HitEffect、Q_cas_White_Tip）。"
     "**左右对称**。约 12 格，居中画。",
     f"{BL} and {RG}",
     "a HORIZONTAL CUT HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a white horizontal slash 10 squares long "
     "through the center; 2 the slash 12 squares, ivory, with 2 red drops and 4 sparks flying out evenly to both sides; "
     "3 fading, sparks farther; 4 a few fading sparks.",
     row(4, 14, 14) + "; centered in every cell.", False),
    # ---- E -> W
    ("e_dash", "E 横冲直撞：冲刺的残影和沙尘（烘进冲刺的动作帧），4 帧",
     "烘进 E 的动作帧（`renekton_bake.json`：站位点后面，随人物朝向翻转）", "34 × 16",
     "冲刺：他身后拖一道长长的沙色风痕和几道象牙白的速度线，脚下扬起沙尘（参考 E_cas_spiralwind、E_cas_alpha_12、Oriental_Dust_2x2）。"
     "人朝右冲，所以风痕在**左边**（身后），从站位点往左拖。4 帧：拉出、最长、散开、消失。约 34 格宽、16 格高。",
     f"{SD} and {BL}",
     "a DASH STREAK behind a figure dashing to the RIGHT, 4 frames, " + FIG + ": 1 four horizontal ivory speed lines and a "
     "band of sand-coloured wind 20 squares long trailing to the LEFT from the right edge, a puff of sand dust at the "
     "bottom; 2 the streak 32 squares long, the wind swirling, the dust cloud bigger; 3 the lines breaking up, the sand "
     "drifting; 4 fading sand motes.",
     row(4, 36, 18) + "; the streak starts at the RIGHT edge's middle of every cell and trails left.", False),
    ("e_hit", "E 冲刺砍中（每个被穿过的人身上），4 帧", "view_effects `league_renekton_e_hit`（跟随，画在人物上面；左右对称）", "12",
     "冲刺砍中：一道斜的象牙白刀痕加一团沙尘，**左右对称**（两道交叉的斜刀痕），约 12 格，居中画（参考 common_HitEffect、Oriental_Dust_2x2）。",
     f"{BL} and {SD}",
     "a DASH CUT HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 two crossing white diagonal slashes 10 squares "
     "across; 2 the slashes ivory with a burst of sand dust 12 squares across; 3 the dust drifting out to both sides; 4 "
     "fading dust.",
     row(4, 14, 14) + "; centered in every cell.", False),
    ("w_hit", "W 冷酷捕猎：每一刀劈中（目标身上），4 帧", "view_effects `league_renekton_w_hit`（跟随，画在人物上面；左右对称）", "16",
     "W 劈中：一道从上往下的重劈刀痕（竖的象牙白粗线），落点炸开一圈红色的冲击和火星（参考 Z_Glow_Trail、skin05_W_sub_flash、"
     "common_angstlines）。**左右对称**。约 16 格，居中画。",
     f"{BL} and {RG}",
     "a HEAVY CHOP HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a thick vertical white slash 14 squares tall "
     "down the center; 2 the slash ivory, a burst of red impact 14 squares across at its lower end with 6 sparks flying "
     "out evenly to both sides; 3 the red burst breaking up; 4 fading sparks.",
     row(4, 18, 18) + "; centered in every cell.", False),
    ("w_glow", "W 强化（满怒气）：身上一团红色的怒气爆发，5 帧",
     "view_effects `league_renekton_w_glow`（画在他身上，`is_follow` false；左右对称）", "44 × 44",
     "满怒气的 W：举刀时全身冒出一团红色怒气，向上窜的红焰和热浪（参考 Q_cas_rage_Aura_self、R_buf_renekton_runewars_flare_reddish、"
     "Renekton_runewars_hot）。**只画外圈，中间留空**；**每一帧左右对称**。约 44 格。",
     RG,
     "a FURY FLARE round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, " + FIG + ": 1 a red-orange glow "
     "outline round the figure's place 30 squares tall; 2 red flames licking UP on both sides, 40 squares tall, a white-hot "
     "flash at the top; 3 the flames tallest, sparks rising; 4 the flames thinning; 5 fading embers. The figure's place in "
     "the middle stays EMPTY.",
     row(5, 46, 46) + "; the figure's place (20 squares wide, 38 tall, its soles 4 squares above the bottom) centered.",
     False),
    ("w_stun", "W 眩晕（被晕的人头顶，循环），4 帧", "view_buffs `league_renekton_w_stun`（挂在目标头顶；左右对称）", "14 × 6",
     "眩晕：头顶一圈转的金色小星星（3 颗），**每一帧左右对称**（用星星一闪一闪表现，不要画旋转）。约 14 格宽、6 格高。",
     ST,
     "STUN STARS above a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame: three small gold stars "
     "3 squares across on a flat ellipse 14 squares wide (one at the center, one at each side); each frame the stars "
     "twinkle in turn (bigger and white, then smaller and gold).",
     row(4, 16, 8) + "; centered in every cell.", False),
    ("e_shred", "E 强化：被削甲的标记（目标头顶，循环），4 帧", "view_buffs `league_renekton_e_shred`（挂在目标头顶；左右对称）", "8 × 8",
     "削甲：头顶一个裂开的小盾牌（灰银色，中间一道红色裂痕），**左右对称**，红光一闪一闪。约 8 格。",
     f"{RG} and {BL}",
     "a CRACKED SHIELD MARK, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame: a small pale silver-ivory "
     "shield 7 squares across with a red crack down its middle; each frame the crack glows brighter and dimmer.",
     row(4, 10, 10) + "; centered in every cell.", False),
    # ---- the passive and R
    ("f5", "满怒气（他身上，循环），6 帧", "view_buffs `league_renekton_f5`（挂在他身上、画在身后；左右对称）", "48 × 44",
     "满怒气：脚下一圈红光，身上往上冒红色的怒气火焰和热浪，在身后（参考 Passive_ring_red_03、Passive_Renekton_VG_Q_Fire_Cas、"
     "Passive_xerath_Magma_Strands）。**只画外圈，中间留空**；**每一帧左右对称**。约 48 格宽、44 格高。",
     RG,
     "a FULL FURY AURA behind a figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, " + FIG + ": a "
     "flat red ellipse 40 squares wide on the ground at the bottom, red-orange flames and heat wisps rising on both sides "
     "of the figure's place up to 40 squares high, flickering each frame; a few embers floating up.",
     row(6, 50, 46) + "; the ground ellipse 2 squares above the bottom, centered.", False),
    ("r_cast", "R 终极统治：变身爆发（他身上），8 帧",
     "view_effects `league_renekton_r_cast`（画在他身上，`is_follow` false；左右对称）", "72 × 60",
     "大招变身：脚下炸开一圈沙暴，一个金色的鳄鱼神（索贝克）符号在他头顶亮一下，红色怒气冲天，沙子旋转着往外扫"
     "（参考 R_cas_sobeksymbol、R_Sand_01、R_Sand_02、R_buf_renekton_runewars_transform_swirl、R_end_Geo_ConeBurst、R_Scarab）。"
     "**只画外圈，中间留空**；**每一帧左右对称**。约 72 格宽、60 格高。",
     f"{SD}, {RG} and {ST}",
     "a TRANSFORMATION BURST round a figure, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, " + FIG + ": 1 a red-gold "
     "flash at the figure's feet; 2 a ring of sand blasting outward along the ground, 40 squares wide; 3 the sand storm "
     "rising in a wide funnel on both sides, red fury flames inside it, a gold crocodile-god sigil appearing above the "
     "head; 4 the funnel tallest (56 squares), the sigil brightest; 5-6 the sand swirling outward and thinning, the sigil "
     "fading; 7-8 drifting sand and embers. The figure's place in the middle stays EMPTY.",
     row(8, 74, 62) + "; the funnel's base 3 squares above the bottom, centered.", False),
    ("r_on", "R 变身期间：脚下的沙暴光环（循环），6 帧",
     "view_buffs `league_renekton_r_on`（挂在他身上、画在身后；左右对称）", "64 × 28",
     "变身期间：脚下一圈旋转的沙暴（扁椭圆），里面红色的热浪往上冒（参考 R_AuraTwirl、R_buf_Aura_Self、R_Buff_Decal_BG、R_Sand_02）。"
     "也是伤害光环的范围。**只画外圈，中间留空**；**每一帧左右对称**（用沙粒一闪一闪表现旋转）。约 64 格宽、28 格高。",
     f"{SD} and {RG}",
     "a SAND STORM AURA at a figure's feet, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, " + FIG +
     ": a flat ellipse 60 squares wide of swirling sand on the ground, thick at its front (bottom) edge, red heat wisps "
     "rising from it up to 20 squares on both sides; each frame the sand grains shift and twinkle.",
     row(6, 66, 30) + "; the ellipse's center 6 squares above the bottom, centered.", False),
    ("r_burn", "R 光环烧到的敌人（目标身上），4 帧", "view_effects `league_renekton_r_burn`（跟随，画在人物上面；左右对称）", "10",
     "大招光环每半秒烫一下：一小团沙尘加红色火星，**左右对称**，约 10 格，居中画（参考 R_Sand_01、Z_Speck）。",
     f"{SD} and {RG}",
     "a SMALL SAND BURN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a red-gold spark 4 squares at the center; 2 a "
     "puff of sand 9 squares across with 4 red embers; 3 the sand drifting out; 4 fading grains.",
     row(4, 12, 12) + "; centered in every cell.", False),
]

GROUPS = [
    ("attack / Q", ["Renekton_Base_BA_trail", "Renekton_Base_Q_cas_swipetrail", "Renekton_Base_Q_cas_color-swipetrail",
                    "Renekton_Base_Q_cas_Shadow", "Renekton_Base_Q_cas_White_Tip", "common_HitEffect"]),
    ("Q rage / Fury", ["Renekton_Base_Q_cas_rage_swipetrail", "Renekton_Base_Q_cas_rage_renekton_runewars_swipe",
                       "Renekton_Base_Q_cas_rage_Aura_self", "Renekton_Base_Passive_ring_red_03",
                       "Renekton_Base_Passive_Renekton_VG_Q_Fire_Cas", "Renekton_Base_Passive_xerath_Magma_Strands"]),
    ("E / W", ["Renekton_Base_E_cas_spiralwind", "Renekton_Base_E_cas_spiralwind_rage", "Renekton_Base_Oriental_Dust_2x2",
               "Renekton_Base_Z_Glow_Trail", "Renekton_skin05_W_sub_flash", "common_angstlines"]),
    ("R", ["Renekton_Base_R_cas_sobeksymbol", "Renekton_Base_R_Sand_01", "Renekton_Base_R_Sand_02",
           "Renekton_Base_R_AuraTwirl", "Renekton_Base_R_buf_renekton_runewars_transform_swirl",
           "Renekton_Base_R_end_Geo_ConeBurst"]),
]
# where the pictures start: (tag, frame, what, marks: "feet" or [(dx, dy) from the standing point, dy from the soles]);
# the blade's middle from Codex's manifest (attack frame 3: (92.8, 48.7), pivot (60, 70), soles 81 -> +33, 32 up; W's
# chop frame 2: (87.3, 63.8), pivot (53, 70) -> +34, 17 up)
SHOTS = [("attack", 3, "a_slash: 刀刃中点", [(33, -32)]), ("skill2", 2, "e_dash: 站位点（风痕往左拖）", "feet"),
         ("skill2_w", 2, "w_hit 打在目标身上（刀刃中点）", [(34, -17)]), ("ult", 3, "r_cast / r_on / f5 / q_spin: 站位点", "feet")]


def ref_sheet(path):
    S, LW = 180, 110
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Renekton_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    d.text((8, 36), f"雷克顿 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (league/champions/league_renekton, the imported sheet), each picture's starting
    point as a cyan cross (the standing point is the frame's pivot: the sheet's frames are centred on it)."""
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_renekton"))
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
    a("# 荒漠屠夫 雷克顿：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/renekton_design.png`，8 倍，{h} 行、{w} 格宽）。")
    a(f"> - 大小对照 `design/renekton_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。雷克顿 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/renekton_shots.png`：定稿动作（4 倍），青色十字是特效的起点（刀刃中点、站位点），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里雷克顿自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版皮肤：**刀光是象牙白；怒气（满怒气、强化技能、大招）是红橙色；冲刺和大招的沙暴是沙黄色；眩晕的星星是金色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **围着人的刀光圈、怒气、沙暴只画外圈，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：游戏不会翻转特效图片，只翻转人物的动作帧。所以："
      "打中目标的（`a_hit`、`q_hit`、`e_hit`、`w_hit`、`r_burn`）、画在他身上的（`q_spin`、`q_spin_e`、`w_glow`、`r_cast`）"
      "和挂着循环的（`f5`、`w_stun`、`e_shred`、`r_on`）都要**每一帧严格左右对称**（逐格对称）。"
      "只有 `a_slash`（普攻刀光）和 `e_dash`（冲刺风痕）是朝右的：它们会烘进动作帧里，跟着人物一起翻转。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `renekton_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。")
    a("> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`renekton_fx_done.zip`）放在 outputs 里，或放在 `outputs/renekton-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「怒之领域」 | 挥刀攻击，积攒怒气；满怒气时下一个技能被强化 | `a_slash` · `a_hit` · `f5` |")
    a("| 技能 1 = Q「巨鳄狂袭」 | 横扫一圈、回血；强化时更大更红 | `q_spin` · `q_spin_e` · `q_hit` |")
    a("| 技能 2 = E「横冲直撞」→ W「冷酷捕猎」 | 冲过去砍，接连劈两刀眩晕（强化三刀、晕更久），再冲一次（强化削甲） | `e_dash` · `e_hit` · `w_hit` · `w_glow` · `w_stun` · `e_shred` |")
    a("| 大招 = R「终极统治」 | 变身：加生命、脚下沙暴光环每半秒烫周围的敌人 | `r_cast` · `r_on` · `r_burn` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("刀光象牙白（普攻、Q、E、W）", BLADE), ("怒气红（强化、满怒气、大招）", RAGE),
                        ("沙暴沙黄（E、R）", SAND), ("金色（眩晕星星、大招的神像符号）", STAR)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中的画面居中画，不旋转；地面上、绕身体的圈是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，"
      "Q 半径 32000，R 光环半径 30000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout, obj) in enumerate(FX, 1):
        a(f"### {k}. `renekton_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `renekton_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `a_slash` 烘进普攻第 3 帧（刀刃中点：站位点前 33 格、脚底上 32 格），`e_dash` 烘进 E 的第 1–3 帧（站位点往后拖），"
      "都写在 `renekton_bake.json`，不做成特效（红色方翻转）。`q_spin`、`q_spin_e`、`w_glow`、`r_cast` 的 `is_follow` 为 false，逐格左右对称；"
      "`f5`、`r_on` 在他身后（z −1）。")
    a("- 用 `pixel_1x/` 切格（import_twitch 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；"
      "量每张的平均亮度和最亮的一成，和包里别的英雄比。Q 圈按半径 32000 对宽度，R 光环按 30000。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="renekton_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Renekton's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "renekton_design.png"))
    shape = size_sheet(os.path.join(out, "design", "renekton_size.png"))
    shots_sheet(os.path.join(out, "design", "renekton_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"renekton_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
