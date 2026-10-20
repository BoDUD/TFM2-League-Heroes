#!/usr/bin/env python3
"""Build vex_fx_pack.zip: step 3 of Vex's sprite - Codex draws her effects (pack_zoe_fx.py's way, pack_rammus_fx's sheets).

    python <scratchpad>/fx_ref_vx.py           # League's particle textures -> C:/t/vx_work/fxref (Riot's art, local only)
    python tools/art/pack_vex_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name vex_fx_redo_pack]

The pack (C:/t/vx_work/fx/vex_fx_pack, zipped into --out, default dist/vex_packs) holds PROMPTS.md (also written to
assets/source/vex/PROMPTS_FX.md), design/vex_idle.png (her idle at 4x, the design's squares at PPU 1.5),
design/vex_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/vex_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Vex grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_vex.py): view_projectiles a_bolt, q_bolt, r_missile;
view_effects a_hit, q_hit, w_hit, w_ring, w_shield, e_cast, e_land, r_hit, p_ready, g_pop; view_buffs e_slow, g_mark,
r_mark. League's colours: her magic is a MINT / TEAL glow (the Gloom's eye sigil, her bolts, Mistral Bolt's wave) and
her Shadow is INK INDIGO-VIOLET with pale spiral eyes. The user (2026-10-20: 「感觉背后的宠物不需要啊」) took the Shadow off
her body: it lives only here, in E (it flies off her and crashes on the spot), W (it wraps her), R (it is the missile)
and Doom's ready flash (its eyes). Red side: the client never mirrors an effect picture, so every hit, buff and ground
picture is symmetric left to right; a projectile's picture is turned with its flight (drawn flying right, the trail
behind it on the left), so it is symmetric top to bottom instead (it flies upside down to the left).
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/vx_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "vex", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_vex")
NAME = "vex_fx_pack"

MINT = "#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A"        # her magic: the mint / teal glow
SHADE = "#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830"       # the Shadow: ink indigo-violet, lilac edge
EYES = "#FFFFFF, #CFF7FC, #8EC8FF"                                    # the Shadow's pale spiral eyes
MI = f"a mint-teal glow ramp ({MINT})"
SH = f"an ink indigo-violet shadow ramp ({SHADE})"
EY = f"the pale eye colours ({EYES})"
LEAD = RF.LEAD.replace("NO outline around light, energy, dust, smoke, rings or shockwaves",
                       "NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature")
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
HER = "the small girl stands in the middle, not drawn: 28 squares from her ear tips to the ground, about 24 squares wide"
row = RF.row
SPIRAL = ("each eye a little pale blue-white open spiral (a clear @ shape about 4 squares across) - the Shadow's drawn "
          "eyes")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_bolt", "普攻：暗影弹（弹道，循环），4 帧", "view_projectiles `league_vex_a_bolt`（跟着弹道转向；上下对称）", "12 × 8",
     "她普攻甩出去的一小团暗影弹：薄荷青绿色的亮芯，外面裹一层靛紫色的雾，后面拖一小段青绿色的尾迹（参考 ba_streak、ba_glowtrail、ba_tar）。"
     "**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。",
     f"{MI} and {SH}",
     "A SMALL GLOOM BOLT, 4 frames, a seamless loop, " + TB + ": a round mint-white core 4 squares across inside a 6-square "
     "indigo-violet mist at the right, a short tapering mint trail 5 squares long behind it to the left; each frame the "
     "mist wavers and the trail flickers (symmetric top and bottom).",
     row(4, 12, 8) + "; the core's middle on the cell's middle row, 3 squares from its right edge."),
    ("a_hit", "普攻：打中目标，3 帧", "view_effects `league_vex_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "暗影弹打中目标：一团青绿色的小闪光，几缕靛紫色的雾散开（参考 hitflash、vex_hiteffect_magic_s_02_star）。**左右对称**。",
     f"{MI} and {SH}",
     "A SMALL GLOOM HIT, 3 frames, " + LR + ": 1 a mint-white four-pointed flash 6 squares across; 2 the flash 9 across with "
     "4 indigo-violet mist puffs at mirrored places; 3 only the puffs further out, fading.",
     row(3, 12, 12) + CENTER),
    # ---- Q Mistral Bolt
    ("q_bolt", "Q 寒心波云：一道暗风波（弹道，循环），4 帧", "view_projectiles `league_vex_q_bolt`（跟着弹道转向；上下对称）",
     "18 × 18",
     "她推出去的寒心波云：一道往右鼓起的弧形风波，像一弯竖着的月牙（弧顶朝右），弧的前缘是亮的薄荷青绿色，后面是翻滚的靛紫色暗雾，"
     "里面隐约一只青绿色的眼睛符印（参考 q_wave、q_missileeye、q_spawntrails）。**朝右飞，弧顶在右边，上下严格对称**，4 帧循环。"
     "它穿过一条线上的所有敌人，所以要宽（约 16 格高）。",
     f"{MI} and {SH}",
     "A CRESCENT GUST OF GLOOM, 4 frames, a seamless loop, " + TB + ": an upright crescent wave 16 squares tall bulging to the "
     "RIGHT, its leading edge 2 squares of bright mint-white, behind it 5 squares of churning indigo-violet mist that frays "
     "into wisps to the left; a small mint eye sigil (an almond eye with a dot) in its middle; each frame the mist churns "
     "and the edge shimmers (symmetric top and bottom).",
     row(4, 18, 18) + "; the crescent's middle on the cell's middle row, its edge 2 squares from the cell's right edge."),
    ("q_hit", "Q：风波打中目标，4 帧", "view_effects `league_vex_q_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "风波打中目标：一团青绿色的闪光，靛紫色的暗雾往两边卷开（参考 q_tar_erode、q_tar_trail_smoke）。**左右对称**。",
     f"{MI} and {SH}",
     "A GUST IMPACT, 4 frames, " + LR + ": 1 a mint-white flash 7 squares across; 2 the flash 11 across, indigo-violet mist "
     "curling out to both sides; 3 the mist 16 across, thinning, the flash gone; 4 only faint wisps at the edges.",
     row(4, 16, 16) + CENTER),
    # ---- W Personal Space (in the attack and on landing from R)
    ("w_ring", "W 生人勿近：她身边炸开的冲击环（地上，跟随），5 帧",
     "view_effects `league_vex_w_ring`（跟随她，画在人物下面 z -1；左右对称；大图表）", "84 × 30",
     "她身边炸开的冲击波：贴着地面的一圈椭圆冲击环往外扩，环是薄荷青绿色的亮线带着靛紫色的暗雾，环上有四个对称的小漩涡花纹"
     "（参考 w_ring_normal、w_shockwave、w_smokering_dissolve、w_praxis）。**只画在地面上（她站在中间，不画人）**，**左右对称**，5 帧。"
     "范围约 80 格宽。",
     f"{MI} and {SH}",
     "A SHOCK RING bursting out along the ground round her, 5 frames, " + LR + " (" + HER + "): 1 a small bright mint ring "
     "(an ellipse 20 wide and 7 tall); 2 the ring 44 wide and 15 tall, 2 squares thick, mint-white with an indigo-violet "
     "mist band just inside it; 3 the ring 66 wide and 22 tall, four small mint curl ornaments on it at mirrored places; "
     "4 the ring 80 wide and 27 tall, thinning, the mist fraying; 5 only a faint broken ring and wisps.",
     row(5, 84, 30) + "; centered across, the ellipse's middle 3 squares above the cell's middle row."),
    ("w_shield", "W：影子护住她（她身上，跟随），5 帧", "view_effects `league_vex_w_shield`（跟随她，画在人物上面 z 3；左右对称）", "34 × 42",
     "护盾的一下：她的影子从地面升起、张开两只大爪子把她围住，然后化成一圈靛紫色的暗影罩，罩的边是青绿色的亮线（参考 w_shield_shadow、"
     "shield_01、w_shieldmask）。**她站在中间不画人**，只画外圈：影子的两只手在她两侧、头（两只尖耳朵、两只螺旋眼）在她头顶上方；"
     "**左右对称**，5 帧。",
     f"{SH}, {EY} and {MI}",
     "THE SHADOW WRAPPING A GIRL IN A SHIELD, 5 frames, " + LR + " (" + HER + ", her body area left EMPTY): 1 dark "
     "indigo-violet mist rising from the ground at both sides of her; 2 two big shadow hands with long claws rising at her "
     "left and right, a shadow head with two pointed ears over her head, " + SPIRAL + "; 3 the hands curling round her, the "
     "head looking down; 4 the shadow melting into a dome-shaped shield outline round her, 32 wide and 40 tall, its rim 2 "
     "squares of mint-white light over indigo mist; 5 only the dome's rim, thinner, fading.",
     row(5, 34, 42) + "; centered across, the bottom of the mist on the cell's bottom row."),
    ("w_hit", "W：冲击波打中，3 帧", "view_effects `league_vex_w_hit`（跟随目标，画在人物上面 z 2；左右对称）", "12 × 12",
     "冲击波打到身边的敌人：一团青绿色的小闪光和一缕暗雾（参考 tar_flashglow）。**左右对称**。",
     f"{MI} and {SH}",
     "A SMALL SHOCK HIT, 3 frames, " + LR + ": 1 a mint-white flash 6 across; 2 a mint ring 10 across with indigo mist "
     "inside it; 3 only a faint ring and wisps.",
     row(3, 12, 12) + CENTER),
    # ---- E Looming Darkness
    ("e_cast", "E 溟濛渐染：影子从她身上飞出去（她身上，跟随），5 帧",
     "view_effects `league_vex_e_cast`（跟随她，画在人物上面 z 3；左右对称）", "26 × 44",
     "放 E 的一下：她的影子从她背后升起、往上一跃飞走（飞去落点的那段由落地的画面接上）：靛紫色的影子身形带两只尖耳朵和两只螺旋眼，"
     "往上拉长成一缕烟冲出画面顶上（参考 r_shadow、e_missile、vertical_wisp）。**她站在下半部不画人**，影子在她头顶，**左右对称**，5 帧。",
     f"{SH}, {EY} and {MI}",
     "A SHADOW LEAPING UP AND AWAY, 5 frames, " + LR + " (" + HER + ", her body in the lower part left EMPTY): 1 dark "
     "indigo-violet mist gathering over her head; 2 a shadow creature 18 squares wide rising over her head - a round head "
     "with two tall pointed ears, " + SPIRAL + ", a body narrowing to a wisp down to her; 3 the creature 4 squares higher, "
     "stretched taller, a mint glow round its eyes; 4 it shooting up to the cell's top, a long indigo wisp trailing; 5 only "
     "the wisp's end at the top, fading.",
     row(5, 26, 44) + "; centered across, the mist's bottom 20 squares above the cell's bottom row."),
    ("e_land", "E：影子落在目标点扩散（地上，不跟随），6 帧",
     "view_effects `league_vex_e_land`（不跟随，画在人物下面 z -1；左右对称；大图表）", "48 × 44",
     "影子从天上扑下来落在目标点：靛紫色的影子身形（尖耳朵、螺旋眼、张开的大爪子）往下扑，撞地后化成一大片靛紫色的暗影地面，"
     "外圈一道青绿色的符文环，然后散成雾（参考 e_decal、e_runedecal、e_ring_01、e_groundlight_01、e_eyesigil）。"
     "**左右对称**，6 帧。范围约 44 格宽。",
     f"{SH}, {EY} and {MI}",
     "A SHADOW CRASHING DOWN AND SPREADING, 6 frames, " + LR + ": 1 a shadow creature 20 squares wide diving down from the "
     "top - a round head with two pointed ears, " + SPIRAL + ", two clawed hands spread to the sides; 2 it hitting the "
     "ground at the bottom middle, splashing; 3 a flat dark indigo-violet pool on the ground (an ellipse 40 wide and 13 "
     "tall) with a 1-square mint rune ring round its edge and a small mint eye sigil in its middle; 4 the pool 44 wide, "
     "indigo mist rising from it in 6 wisps at mirrored places; 5 the pool fading, the wisps higher; 6 only thin wisps and "
     "a broken ring.",
     row(6, 48, 44) + "; centered across, the pool's middle 7 squares above the cell's bottom row."),
    ("e_slow", "E：被减速（敌人脚下，循环），4 帧", "view_buffs `league_vex_e_slow`（跟随，画在人物下面 z -1；左右对称；循环）", "22 × 6",
     "减速的 2 秒：敌人脚下一小滩靛紫色的暗雾，几缕暗烟往上冒（参考 noisemist、mist_noise）。**只画在脚下的地面上**，**左右对称**，4 帧循环。",
     SH,
     "GLOOMY MIST at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat indigo-violet mist ellipse 20 wide and 4 "
     "tall, 3 short dark wisps (2-3 squares) rising from it at mirrored places; each frame the wisps rise a square and new "
     "ones start.",
     row(4, 22, 6) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- the passive Doom 'n Gloom
    ("g_mark", "被动：暮气（敌人头上，循环），4 帧", "view_buffs `league_vex_g_mark`（跟随，画在人物上面 z 3；左右对称；循环）", "12 × 10",
     "暮气的标记：敌人头上飘着一个薄荷青绿色的眼睛符印（杏仁形的眼睛、中间一个点，上面三道火苗似的尖），一闪一闪（参考 p_gloomdebuff、"
     "e_eyesigil）。**画在头上**，**左右对称**，4 帧循环。",
     MI,
     "A GLOOM EYE SIGIL over a unit's head, 4 frames, a seamless loop, " + LR + ": a mint almond-shaped eye 10 squares wide "
     "and 5 tall with a white dot pupil, three short flame-like points above it and two below; each frame it pulses (its "
     "glow 1 square wider on frames 2 and 3) and bobs a square.",
     row(4, 12, 10) + CENTER),
    ("g_pop", "被动：暮气被引爆（他身上），4 帧", "view_effects `league_vex_g_pop`（跟随目标，画在人物上面 z 2；左右对称）", "20 × 20",
     "暮气被她引爆：青绿色的眼睛符印猛地睁大、炸成一团青绿色的十字星闪光，碎片四散（参考 vex_hiteffect_magic_s_02_star、tar_flashglow、"
     "p_castcrackswipe）。**左右对称**。",
     MI,
     "A GLOOM DETONATION, 4 frames, " + LR + ": 1 a mint eye sigil 10 wide opening wide; 2 it bursting into a mint-white "
     "four-pointed star flash 14 across; 3 the flash 18 across with 8 mint shards flying out; 4 only fading shards at the "
     "edge.",
     row(4, 20, 20) + CENTER),
    ("p_ready", "被动：终焉好了（她头上），4 帧", "view_effects `league_vex_p_ready`（跟随她，画在人物上面 z 3；左右对称）", "16 × 10",
     "终焉充好的一下：她头上方一对影子的螺旋眼睁开、亮一下，旁边两只小尖耳朵的影子轮廓，然后消散（参考 r_r1_eyes、r_target_ears）。"
     "**画在她头顶上方（不画人）**，**左右对称**，4 帧。",
     f"{SH}, {EY} and {MI}",
     "TWO SHADOW EYES OPENING over a head, 4 frames, " + LR + ": 1 a thin dark indigo mist band 12 wide; 2 two eyes opening "
     "in it, " + SPIRAL + ", with two small pointed shadow ears above them; 3 the eyes flashing mint-white; 4 only fading "
     "mist.",
     row(4, 16, 10) + CENTER),
    # ---- R Shadow Surge
    ("r_missile", "R 愁煞：影子飞弹（弹道，循环），4 帧", "view_projectiles `league_vex_r_missile`（跟着弹道转向；上下对称）", "24 × 14",
     "她扔出去的愁煞：影子的头化成一颗彗星——靛紫色的头上两只尖耳朵朝后、两只螺旋眼朝前，后面拖一条长长的靛紫色暗影尾巴，尾巴边上闪着"
     "青绿色的光（参考 r_missile_v2、r_head_01、r_comet_flipped、r_galaxysphere_streaks）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。",
     f"{SH}, {EY} and {MI}",
     "A SHADOW-HEAD COMET, 4 frames, a seamless loop, " + TB + ": at the right a round indigo-violet shadow head 9 squares "
     "across with two pointed ears swept back (one at the top, one mirrored at the bottom) and two eyes side by side "
     "facing forward, " + SPIRAL + "; behind it to the left a long tapering indigo-violet shadow tail 13 squares long with "
     "mint-white sparks along its edges; each frame the tail ripples (symmetric top and bottom) and the sparks move.",
     row(4, 24, 14) + "; the head's middle on the cell's middle row, 5 squares from its right edge."),
    ("r_mark", "R：被标记（敌人头上，循环），4 帧", "view_buffs `league_vex_r_mark`（跟随，画在人物上面 z 3；左右对称；循环）", "16 × 10",
     "被愁煞的飞弹打中、她马上冲过来：敌人头上一对影子的眼睛和两只尖耳朵的暗影轮廓盯着他（参考 r_target_ears、r_r1_eyes）。**画在头上**，"
     "**左右对称**，4 帧循环。",
     f"{SH} and {EY}",
     "A SHADOW WATCHING from over a unit's head, 4 frames, a seamless loop, " + LR + ": a small indigo-violet shadow face 14 "
     "wide and 8 tall - two pointed ears and two eyes, " + SPIRAL + "; each frame it bobs a square and the eyes' spirals "
     "turn.",
     row(4, 16, 10) + CENTER),
    ("r_hit", "R：冲过去的一击（他身上），4 帧", "view_effects `league_vex_r_hit`（跟随目标，画在人物上面 z 2；左右对称）", "26 × 26",
     "她冲到目标身边的一击：一团大大的靛紫色暗影炸开，中间青绿白色的闪光，外圈一道青绿色的冲击环，影子的爪痕往四周撕开（参考 r_tar_impact、"
     "r_flash、r_land_glow）。**左右对称**，比普通打中大。",
     f"{SH} and {MI}",
     "A BIG SHADOW STRIKE, 4 frames, " + LR + ": 1 a mint-white flash 10 squares across; 2 an indigo-violet shadow burst 18 "
     "across round it with 4 claw-mark streaks tearing out at mirrored diagonals; 3 a mint ring 24 across, the burst "
     "fading; 4 only the ring's broken arcs and wisps.",
     row(4, 26, 26) + CENTER),
]
BIG_FX = ["w_ring", "e_land"]
FLYING = ["a_bolt", "q_bolt", "r_missile"]
GROUPS = [
    ("a_bolt a_hit w_hit", ["vex_base_ba_streak", "vex_base_ba_glowtrail", "vex_base_ba_tar", "vex_base_hitflash",
                           "vex_hiteffect_magic_s_02_star", "vex_tar_flashglow"]),
    ("q_bolt q_hit", ["vex_base_q_wave", "vex_base_q_missileeye", "vex_base_q_spawntrails", "vex_base_q_tar_erode",
                      "vex_base_q_tar_trail_smoke", "vex_base_q_wavelead_fear"]),
    ("w_ring w_shield", ["vex_base_w_ring_normal", "vex_base_w_shockwave", "vex_base_w_smokering_dissolve",
                         "vex_base_w_shield_shadow", "vex_base_shield_01", "vex_base_w_praxis"]),
    ("e_cast e_land e_slow", ["vex_base_r_shadow", "vex_base_e_missile", "vex_base_e_decal", "vex_base_e_runedecal",
                              "vex_base_e_ring_01", "vex_base_noisemist"]),
    ("g_mark g_pop p_ready", ["vex_base_p_gloomdebuff_v2", "vex_base_e_eyesigil", "vex_base_p_castcrackswipe",
                              "vex_base_r_r1_eyes", "vex_base_r_target_ears"]),
    ("r_missile r_mark r_hit", ["vex_base_r_missile_v2", "vex_base_r_head_01", "vex_base_r_comet_flipped",
                                "vex_base_r_tar_impact", "vex_base_r_flash", "vex_base_r_land_glow"]),
]
SHOTS = [("attack", 2, "a_bolt：袖子甩到前面，暗影弹从袖口飞出去；a_hit 在目标身上"), ("skill", 3, "q_bolt：弓步往前推，风波飞出去"),
         ("skill_w", 3, "w_ring / w_shield：落地时冲击环从她脚下炸开，影子护住她"),
         ("skill2", 2, "e_cast：跳起甩袖，影子从她身上飞走"), ("ult", 3, "r_missile：甩袖扔出影子飞弹"),
         ("ult_hit", 2, "r_hit 在目标身上（她冲到他身边那一下）"), ("idle", 1, "待机（大小参考）")]


def configure():
    """pack_rammus_fx's sheets drawn from Vex's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "薇古丝"


def design_sheet(path):
    """Her idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    import rig_vex as Z
    F = Z.form()
    c = F.rig.finish(Z.frames(F)["idle"][0][0])
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 愁云使者 薇古丝：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/vex_idle.png`：3/4 正面朝右的 Q 版约德尔小女孩，深青黑色的连帽衫、"
      f"兜帽上两只尖耳朵，青绿色头发、灰白皮肤、品红色的眼睛，长到小腿的袖子、品红紫灯笼裤）。她在游戏里是**高清**的（每个游戏格子里 "
      f"1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/vex_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/vex_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里薇古丝自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**她的魔法是薄荷青绿色的光**（暮气的眼睛符印、暗影弹、寒心波云的前缘），"
      "**她的影子是墨一样的靛紫色**，带两只尖耳朵和两只浅蓝白的**螺旋眼**。")
    a("> - **影子只出现在特效里**（用户把她身后的影子从人物上拿掉了）：E 影子从她身上飞走、扑到目标点；W 影子护住她；R 影子的头就是飞弹；"
      "终焉好了时她头上睁开一对影子的眼睛。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯；深色的影子要有靛紫 / 淡紫的亮边，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、头上、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（暗影弹、风波、"
      "影子飞弹）**朝右飞、尾巴在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `vex_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/vex_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（W「生人勿近」和被动「终焉暮气」在里面） | 甩出暗影弹；敌方英雄靠近时改成护盾 + 身边炸开冲击波；每隔一段时间下一个技能附带恐惧；"
      "暮气标记被她引爆 | `a_bolt` · `a_hit` · `w_ring` · `w_shield` · `w_hit` · `g_mark` · `g_pop` · `p_ready` |")
    a("| 技能 1 = Q「寒心波云」 | 一道暗风波穿过一条线上的所有敌人 | `q_bolt` · `q_hit` |")
    a("| 技能 2 = E「溟濛渐染」 | 影子飞到目标点扩散：伤害、减速、施加暮气 | `e_cast` · `e_land` · `e_slow` · `g_mark` |")
    a("| 大招「愁煞」 | 扔出影子飞弹标记英雄，然后冲过去一击，落地放生人勿近 | `r_missile` · `r_mark` · `r_hit` · `w_ring` · `w_shield` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、暗雾、烟、光环、冲击波和影子都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("薄荷青绿色的光", MINT), ("墨一样的靛紫色影子", SHADE), ("影子的螺旋眼", EYES)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（冲击环、暗影地面、减速的雾）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，冲击波半径 40000，"
      "影子落地的范围半径 22000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `vex_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `vex_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_vex_fx`（小的）和 `league_vex_big`（{'、'.join(BIG_FX)}），tag = 名字（build_vex.py 的 views）。")
    a(f"- 弹道图（{'、'.join(FLYING)}）断言上下对称，其余断言左右对称；`e_land` 不跟随（落点）；`w_ring` 跟随她、画在下面。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（影子的靛紫暗部保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="vex_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "vex_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    configure()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run fx_ref_vx.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "vex_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "vex_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "vex_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"vex_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else "left-right"} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(RF.lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(RF.lp(zpath)):
            os.remove(RF.lp(zpath))
        with zipfile.ZipFile(RF.lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(RF.lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
