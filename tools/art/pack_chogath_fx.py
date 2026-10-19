#!/usr/bin/env python3
"""Build chogath_fx_pack.zip: step 3 of Cho'Gath's sprite - Codex draws his effects (pack_rammus_fx.py's way).

    python <scratchpad>/fx_ref_cg.py          # League's particle textures -> C:/t/cg_work/fxref (Riot's art, local only)
    python tools/art/pack_chogath_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name chogath_fx_redo_pack]

The pack (C:/t/cg_work/fx/chogath_fx_pack, zipped into --out, default dist/chogath_packs) holds PROMPTS.md (also written
to assets/source/chogath/PROMPTS_FX.md), design/chogath_idle.png (his idle at 4x, the design's squares at PPU 1.2),
design/chogath_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/chogath_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Cho'Gath grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_chogath.py): view_projectiles e_pic (Vorpal Spikes' line) and
w_wave (Feral Scream's cone); view_effects a_hit, p_heal, e_arm, e_hit, q_crack, q_spikes, q_hit, w_hit, r_hit, r_grow;
view_buffs e_slow, q_slow, w_sil. League's colours: the void's violet and magenta (Rupture's spikes and its glow, Vorpal
Spikes, Feast's swirl), Rupture throws up tan rock shards, Feral Scream is blue-violet sound, Feast bites with a red ring
of teeth, Carnivore's heal is the usual green. Red side: the client never mirrors an effect picture, so every picture is
symmetric left to right - except the two projectile pictures, which the game turns to their direction: they are drawn
pointing right and symmetric top to bottom instead.
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
TMP = "C:/t/cg_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "chogath", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_chogath")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "chogath_fx_pack"
SIZE_LABEL = "科加斯"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VOID = "#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A"       # the void's violet-magenta light
SPIKE = "#F4E0FF, #C890F0, #9A58D0, #6A3098, #3E1A60, #22102E"      # solid void spikes (outlined)
ROCK = "#E6D2AA, #C2A470, #927448, #60482C, #34261A"                # Rupture's rock shards (solid: outlined)
SOUND = "#FFFFFF, #DCE6FF, #A0B6FF, #6E78F2, #4C3ECA, #2C1E84"      # Feral Scream's blue-violet sound
BLOOD = "#FFFFFF, #FFD0D0, #FF6E6E, #E42A3A, #A41426, #5C0A16"      # Feast's red teeth ring
HEAL = "#FFFFFF, #DAFFD2, #90F088, #42C858, #1E8A3A"                # Carnivore's heal
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with "
        "its lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
VO = f"a void violet-magenta light ramp ({VOID})"
SP = f"a solid void spike ramp ({SPIKE}; spikes are solid: a dark edge allowed)"
RO = f"a rock ramp ({ROCK}; rocks are solid: a dark edge allowed)"
SO = f"a blue-violet sound ramp ({SOUND})"
BL = f"a red teeth-ring ramp ({BLOOD})"
HE = f"a green heal ramp ({HEAL})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = ("POINTING RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to the way it "
      "flies, so cast to the left it is turned upside down)")
CENTER = "; centered in every cell."
HIM = ("the void beast stands in the middle, not drawn: 38 squares from his raised scythe tips to the ground, about 58 "
       "squares wide, his body a low mass 24 squares tall")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack + passive
    ("a_hit", "普攻：直立后扑下来砸中目标，3 帧", "view_effects `league_chogath_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "他直立起来、整个扑下来砸中目标的一下：一团紫白色的冲击闪光，四道短短的紫色爪痕往外劈开，溅出几点品红（参考 flash、"
     "r_spike_slash、z_sparks）。**左右对称**，约 16 × 16 格。",
     VO,
     "A HEAVY VOID IMPACT, 3 frames, " + LR + ": 1 a white-violet burst 8 squares across with 4 short magenta claw "
     "streaks slashing outward diagonally (mirrored pairs); 2 the burst 12 squares across, the streaks longer, 6 magenta "
     "sparks (1-2 squares) flying out; 3 only a fading violet ring 14 squares across and the sparks further out.",
     row(3, 16, 16) + CENTER),
    ("p_heal", "被动肉食者：吃掉小兵回血（他身上，跟随），4 帧",
     "view_effects `league_chogath_p_heal`（跟随，画在人物上面 z 2；左右对称）", "40 × 36",
     "他的攻击打死一个单位、回血的一下：他身上冒起一圈绿色的十字小光点，往上飘，中间一团淡淡的紫色虚空雾一闪（参考 z_star、z_glow、"
     "mist）。**只画他身上、往上飘的光点，身体轮廓不要画**（" + HIM + "）。**左右对称**，4 帧。",
     f"{HE} and {VO}",
     "A HEAL over a big beast, 4 frames, " + LR + " (" + HIM + "): 1 a faint violet puff 14 squares across in the middle "
     "and 6 small green plus-shaped sparkles (3x3) round it at mirrored places 6-14 squares up; 2 the sparkles 4 squares "
     "higher, white cores, the puff fading; 3 the sparkles 8 squares higher and smaller; 4 only 4 tiny green dots near "
     "the top.",
     row(4, 40, 36) + "; centered across, the cell's bottom row is the ground under him (the sparkles' lowest row 6 "
     "squares above it)."),
    # ---- E Vorpal Spikes
    ("e_arm", "E 恐惧之刺：背上的刺充能（他身上，跟随），4 帧",
     "view_effects `league_chogath_e_arm`（跟随，画在人物上面 z 2；左右对称）", "48 × 30",
     "恐惧之刺准备好的一下（接下来 3 次攻击会射刺）：他背上一排尖刺亮起紫红色的光，一圈紫色的光从背上往外一闪（参考 e_cas_glowmask、"
     "e_cas_spikes_mult、e_swirltrail）。**只画背上那一排亮起的刺和外圈的光，身体留空**（" + HIM + "，背在 18–24 格高）。"
     "**左右对称**，4 帧。",
     f"{VO} and {SP}",
     "SPIKES LIGHTING UP along a beast's back, 4 frames, " + LR + " (" + HIM + ", his back 18-24 squares up): 1 a row of "
     "7 small glowing violet spike tips (2 squares wide, 4 tall, pointing up) along an arc 40 squares wide, 20-26 squares "
     "up; 2 the tips magenta with white cores, a thin violet arc of light under them; 3 the arc flaring 4 squares "
     "outward, the tips brightest; 4 only the tips, dimmer.",
     row(4, 48, 30) + "; centered across, the cell's bottom row is the ground under him (the arc's middle 20 squares "
     "above it)."),
    ("e_pic", "E：一排尖刺飞出去（弹道，转向飞行方向），4 帧",
     "view_projectiles `league_chogath_e_pic`（只画图的直线，长 50 宽 17，画在直线中点，跟着方向转；上下对称）", "52 × 18",
     "攻击时射出的一排尖刺：从左边（他嘴前）往右飞出去的 5–6 根紫色尖刺，每根后面拖一道品红的光尾，刺尖朝右（参考 e_cas_spikes_mult、"
     "e_trail、directionalshapes）。**朝右画、上下对称**（游戏会把它转到飞行方向，往左射时上下颠倒）。4 帧：刺从左往右飞过整条线。",
     f"{SP} and {VO}",
     "A VOLLEY OF FLYING SPIKES, 4 frames, " + TB + ": 5 solid violet spikes (each 6 squares long, 2 tall, the point to "
     "the right) in a fan 14 squares tall, each with a magenta light trail behind it; 1 the spikes at the cell's left "
     "quarter, trails short; 2 at the middle, trails 10 squares; 3 at the right quarter, trails 14; 4 at the right edge, "
     "the trails fading behind them.",
     row(4, 52, 18) + "; the fan's middle on the cell's middle row."),
    ("e_hit", "E：被尖刺打中的敌人身上，3 帧", "view_effects `league_chogath_e_hit`（跟随敌人，画在人物上面 z 2；左右对称）", "14 × 14",
     "被尖刺打中：几根紫色的小刺扎上去碎开，一点品红的闪光（参考 flash、z_sparks）。**左右对称**，约 14 × 14 格。",
     f"{SP} and {VO}",
     "A SPIKE HIT, 3 frames, " + LR + ": 1 a magenta-white flash 6 squares across; 2 the flash 9 across, 4 small violet "
     "spike shards (2 squares) breaking off outward at mirrored places; 3 the shards further out, the flash fading.",
     row(3, 14, 14) + CENTER),
    ("e_slow", "E：被减速的敌人脚下扎着的刺（循环），2 帧",
     "view_buffs `league_chogath_e_slow`（跟随，画在人物下面 z 3；左右对称；循环，1.5 秒）", "18 × 8",
     "被恐惧之刺减速的敌人脚下：地上扎着几根紫色的小刺，刺尖一明一暗（参考 e_cas_spikes_mult）。**左右对称**，2 帧循环。",
     f"{SP} and {VO}",
     "SPIKES STUCK IN THE GROUND round a unit's feet, 2 frames, a seamless loop, " + LR + ": 6 small solid violet spikes "
     "(1-2 squares wide, 3-4 tall, slanting outward) on a flat ellipse 16 squares wide and 5 tall; 1 their tips dim; "
     "2 their tips glowing magenta.",
     row(2, 18, 8) + "; centered across, the spikes' feet on the cell's bottom rows."),
    # ---- Q Rupture
    ("q_crack", "Q 破裂：目标点地面裂开（地上，不跟随，0.6 秒后地刺冲出），6 帧",
     "view_effects `league_chogath_q_crack`（不跟随，画在人物下面 z -1；左右对称；大图表）", "54 × 20",
     "破裂的预警：目标点的地面上，一圈裂缝从中间往外裂开（半径约 25 格，地上的椭圆），裂缝里透出紫色和品红的光，越来越亮，几粒碎石在"
     "裂缝边跳起来（参考 q_cas_spikegradient、w_grounddecalfinal、q_rockshards）。**左右对称**，6 帧（约 0.6 秒）。",
     f"{VO} and {RO}",
     "THE GROUND CRACKING OPEN, 6 frames, " + LR + ": 1 a small glowing violet crack star in the middle (6 short cracks, "
     "10 squares across); 2 the cracks 24 squares across, magenta glow in them; 3 the cracks reaching an ellipse 40 wide "
     "and 14 tall, a faint violet glow filling it; 4 the cracks 50 wide and 18 tall, brighter, 4 small rock grains "
     "(2x2, solid) hopping at their edges; 5 the whole ellipse glowing, the cracks white-magenta; 6 the brightest, about "
     "to burst. Flat on the ground, nothing tall.",
     row(6, 54, 20) + "; centered across, the ellipse's middle 9 squares above the cell's bottom row."),
    ("q_spikes", "Q：地刺冲出（地上，不跟随），6 帧",
     "view_effects `league_chogath_q_spikes`（不跟随，画在人物上面 z 3；左右对称；大图表）", "56 × 46",
     "裂开的地面里冲出一丛紫色的巨大地刺（中间最高约 30 格，两边矮），刺上流着品红的光，碎石和土块往外飞，之后地刺缩回地里（参考 "
     "q_cas_spikegradient、r_indicator_spikes、q_rockshards）。**左右对称**，6 帧。",
     f"{SP}, {VO} and {RO}",
     "GIANT VOID SPIKES BURSTING FROM THE GROUND, 6 frames, " + LR + ": 1 a flash of magenta light on the ground (an "
     "ellipse 40 wide and 12 tall); 2 a cluster of 7 solid violet spikes shooting up from it (the middle one 22 squares "
     "tall, the side ones 10-16, slanting outward), magenta light running up their edges; 3 the spikes at full height "
     "(the middle one 32 squares), 8 rock chunks (2-3 squares, solid) flying up and out at mirrored places; 4 the spikes "
     "still, the rocks higher; 5 the spikes sinking back (half height), the rocks falling; 6 only spike stubs and dust "
     "puffs on the ground.",
     row(6, 56, 46) + "; centered across, the spikes' feet 8 squares above the cell's bottom row."),
    ("q_hit", "Q：被地刺顶飞的敌人身上，3 帧", "view_effects `league_chogath_q_hit`（跟随敌人，画在人物上面 z 2；左右对称）", "16 × 16",
     "被地刺顶飞的敌人：一团紫色的冲击闪光，几块碎石往外飞（参考 flash、q_rockshards）。**左右对称**，约 16 × 16 格。",
     f"{VO} and {RO}",
     "AN UPWARD IMPACT, 3 frames, " + LR + ": 1 a violet-white flash 7 squares across; 2 the flash 11 across, 4 rock "
     "chips (2x2, solid) flying up and out at mirrored places; 3 the flash fading, the chips further out.",
     row(3, 16, 16) + CENTER),
    ("q_slow", "Q：被减速的敌人脚下裂开的地面（循环），2 帧",
     "view_buffs `league_chogath_q_slow`（跟随，画在人物下面 z 3；左右对称；循环，1.5 秒）", "20 × 8",
     "被破裂减速的敌人脚下：一小片裂开的地面，裂缝里透着紫光，一明一暗（参考 w_grounddecalfinal）。**左右对称**，2 帧循环。",
     f"{RO} and {VO}",
     "CRACKED GROUND GLOWING VIOLET at a unit's feet, 2 frames, a seamless loop, " + LR + ": a flat patch of dark cracked "
     "earth (an ellipse 18 wide and 6 tall) with 5 thin glowing cracks; 1 the cracks dim violet; 2 the cracks bright "
     "magenta.",
     row(2, 20, 8) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- W Feral Scream
    ("w_wave", "W 野性尖叫：往前一扇形的声波（弹道，转向前方），5 帧",
     "view_projectiles `league_chogath_w_wave`（只画图的直线，长 55，画在直线中点，跟着方向转；上下对称；大图表）", "56 × 32",
     "他直立起来朝前尖叫：从左边（他的嘴）往右扩散的一扇蓝紫色声波（60° 的扇形，最远约 55 格），几道弧形的声浪一层层往外推，夹着"
     "几道短短的冲击条纹（参考 w_cas_coneaoe、w_cas_soundring、w_chogath_distortion_waves、w_sound_waves_styled_impact）。"
     "**朝右画、上下对称**（游戏会把它转到他面对的方向）。5 帧：声浪从左往右推出去。",
     SO,
     "A CONE OF SOUND WAVES, 5 frames, " + TB + ": a 60-degree cone opening from the middle of the cell's left edge to "
     "the right, filled by curved wave arcs (each 2 squares thick, white cores, curving like ')' ); 1 two small arcs "
     "near the left edge; 2 three arcs reaching 20 squares out; 3 four arcs reaching 38 squares out, 6 short straight "
     "streaks between them; 4 the arcs reaching the right edge, the nearest ones fading; 5 only the 2 farthest arcs, "
     "faint.",
     row(5, 56, 32) + "; the cone's tip on the middle of the cell's left edge."),
    ("w_hit", "W：被尖叫打中的敌人身上，3 帧", "view_effects `league_chogath_w_hit`（跟随敌人，画在人物上面 z 2；左右对称）", "16 × 16",
     "被尖叫打中：一圈蓝紫色的声波环在他身上炸开（参考 w_soundwave_blue_hit、w_cas_soundringwhite）。**左右对称**，约 16 × 16 格。",
     SO,
     "A SOUND RING BURST, 3 frames, " + LR + ": 1 a white-blue ring 6 squares across; 2 two rings, 9 and 13 across, the "
     "inner brighter; 3 one faint ring 15 across.",
     row(3, 16, 16) + CENTER),
    ("w_sil", "W：被沉默的敌人头上（循环），4 帧",
     "view_buffs `league_chogath_w_sil`（跟随，画在人物上面 z 3；左右对称；循环，1.8 秒）", "12 × 10",
     "被沉默期间敌人头上：一个蓝紫色的小声波圈，中间一道斜杠（禁止说话的标记），一明一暗（参考 w_cas_soundringwhite）。"
     "**画在头上**（" + CHAMP + "，标记在 36–44 格高）。**左右对称**（斜杠用竖杠或 X 保持对称）。",
     SO,
     "A SILENCE MARK over a unit's head, 4 frames, a seamless loop, " + LR + ": a small blue-violet ring 8 squares "
     "across (2 squares thick, white core) with an X of 1-square lines inside it; frames 2 and 3 the ring a shade "
     "brighter and 1 square bigger, frame 4 back to frame 1.",
     row(4, 12, 10) + CENTER),
    # ---- R Feast
    ("r_hit", "R 盛宴：一口咬下去（被咬的敌人身上，跟随），5 帧",
     "view_effects `league_chogath_r_hit`（跟随敌人，画在人物上面 z 2；左右对称；大图表）", "32 × 34",
     "盛宴咬下的一口：一圈红色的牙从上下两边合拢咬住敌人（上排、下排两排尖牙），中间一团紫色的虚空漩涡（参考 r_tooth_target_ring、"
     "r_tar_voidswirl、r_tar_voidplasmas）。**左右对称**（" + CHAMP + "），5 帧。",
     f"{BL} and {VO}",
     "A GIANT BITE, 5 frames, " + LR + " (" + CHAMP + "): 1 a red ring of teeth wide open round it (an upper row of 7 "
     "white fangs 3 squares long pointing down along an arc 28 squares wide, 30 squares up, and a lower row pointing up "
     "along an arc 2 squares up); 2 the two rows closing to 22 and 8 squares up, a violet swirl filling the middle; 3 "
     "the rows meeting at 15 squares up, the swirl bright magenta; 4 the teeth gone, the swirl collapsing inward; 5 only "
     "a fading violet spark in the middle.",
     row(5, 32, 34) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_grow", "R：吃掉英雄、身体变大（他身上，跟随），5 帧",
     "view_effects `league_chogath_r_grow`（跟随，画在人物上面 z 2；左右对称；大图表）", "64 × 48",
     "盛宴吃死一个英雄、叠一层变大的一下：他身体外面一圈紫色的虚空能量往上冒，一圈品红的光环从他身上往外一胀，几缕虚空的火苗往上飘"
     "（参考 r_tar_voidwisps、r_tar_voidplasmas、z_glow）。**只画外圈，身体留空**（" + HIM + "）。**左右对称**，5 帧。",
     VO,
     "A VOID SURGE round a big beast, 5 frames, " + LR + " (" + HIM + "): 1 a thin magenta outline of light round an "
     "empty oval 56 squares wide and 30 tall (his body); 2 the outline 2 squares thick and 4 squares outside it, 8 violet "
     "flame wisps (3 squares wide, 6 tall) rising from it at mirrored places; 3 the ring swelling to 62 wide and 36 tall, "
     "the wisps higher with white tips; 4 the ring fading, the wisps at the top; 5 only 4 small wisps near the top.",
     row(5, 64, 48) + "; centered across, the cell's bottom row is the ground under him (the oval's bottom on it)."),
]
BIG_FX = ["q_crack", "q_spikes", "w_wave", "r_hit", "r_grow"]
REDO = {}
GROUPS = [
    ("a_hit e_hit q_hit", ["chogath_base_flash", "chogath_base_r_spike_slash", "chogath_base_z_sparks", "chogath_base_flare",
                           "chogath_base_q_rockshards"]),
    ("p_heal", ["chogath_base_z_star", "chogath_base_z_glow", "chogath_base_mist"]),
    ("e_arm e_pic e_slow", ["chogath_base_e_cas_glowmask", "chogath_base_e_cas_spikes_mult", "chogath_base_e_swirltrail",
                            "chogath_base_e_trail", "chogath_base_directionalshapes_2x4"]),
    ("q_crack q_spikes q_slow", ["chogath_base_q_cas_spikegradient", "chogath_base_r_indicator_spikes",
                                 "chogath_base_q_rockshards", "chogath_base_w_grounddecalfinal", "chogath_base_gradients"]),
    ("w_wave w_hit w_sil", ["chogath_base_w_cas_coneaoe", "chogath_base_w_cas_soundring_2x2",
                            "chogath_base_w_chogath_distortion_waves", "chogath_base_w_sound_waves_styled_impact_01",
                            "chogath_base_w_cas_soundringwhite", "chogath_base_w_indicator"]),
    ("r_hit r_grow", ["chogath_base_r_tooth_target_ring", "chogath_base_r_tar_voidswirl", "chogath_base_r_tar_voidplasmas",
                      "chogath_base_r_tar_voidwisps", "chogath_base_r_tar_spikemeshblur_panner"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 4, "a_hit：直立后扑下来砸在前面的目标上（打中的目标身上）"),
         ("attack_e", 4, "e_pic：扑下来时一排尖刺从嘴前往前飞；e_arm 在他背上"),
         ("skill", 2, "q_crack / q_spikes：低头跺地，远处目标点的地面裂开、冲出地刺"),
         ("skill2", 3, "w_wave：直立仰头尖叫，声波从嘴往前扩散"),
         ("ult", 2, "r_hit：扑上去咬住前面的敌人"), ("ult", 3, "r_grow：一口吃死时，围着他"),
         ("idle", 1, "待机（大小参考；p_heal 在他身上）")]


def ref_sheet(path):
    S, LW = 170, 220
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        for k, word in enumerate(label.split()):
            d.text((10, y + S // 2 - 30 + k * 24), word, fill=(230, 240, 250, 255), font=font)
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                cand = [f for f in os.listdir(REF) if f.startswith(nm)]
                if not cand:
                    sys.exit(f"missing reference {p}")
                p = os.path.join(REF, sorted(cand)[0])
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("chogath_base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    anims = json.load(open(lp(SHEET + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(SHEET + "#sheet.png")).convert("RGBA")
    out = []
    for fr in anims[tag]["frames"]:
        r = fr["data"]
        out.append(np.asarray(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))))
    return out


def first_1x(tag):
    f = sheet_frames(tag)[0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    import tfm2_ase as T
    figs = [first_1x("idle")]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    figs.append(k[ky.min():ky.max() + 1, kx.min():kx.max() + 1])
    Z, pad = 4, 6
    W = pad + sum(f.shape[1] + pad for f in figs)
    top = max(f.shape[0] for f in figs)
    img = Image.new("RGBA", (max(W * Z, 560), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
    x = pad
    for f in figs:
        img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST),
                            (x * Z, (base - f.shape[0]) * Z + 64))
        x += f.shape[1] + pad
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, W, 10):
        xx = (pad + i) * Z
        d.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"{SIZE_LABEL} {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is his pivot, FEET rows over the ground
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), pt[1])) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 440), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    cols = 4
    rows_ = (len(tiles) + cols - 1) // cols
    cw = max(t.width for t in tiles) + 10
    ch = max(t.height for t in tiles) + 10
    sheet = Image.new("RGB", (cols * cw, rows_ * ch), (60, 64, 50))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % cols) * cw, (i // cols) * ch))
    sheet.save(path)


def design_sheet(path):
    """His idle at 4x, the design's own squares (PPU 1.2: 1.2 squares a game pixel)."""
    import rig_chogath as M
    F = M.form()
    c = F.rig.finish(M.frames(F)["idle"][0][0])
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 虚空恐惧 科加斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/chogath_idle.png`：3/4 正面朝右、四肢着地的虚空巨兽，深紫甲壳、"
      f"酒红甲片，大嘴里两排白牙、紫舌头、青色眼睛，背上两条镰刀臂）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），"
      f"{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/chogath_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/chogath_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里科加斯自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**虚空的紫色和品红**（破裂的地刺和光、恐惧之刺、盛宴的漩涡），**破裂掀起土黄色的碎石**，"
      "**野性尖叫是蓝紫色的声波**，**盛宴是一圈红色的牙咬下去**，**被动回血是常见的绿色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：13 张严格**左右对称**（逐格对称：这些画面在红色方不会镜像）；两张弹道图（`e_pic` 尖刺、`w_wave` 声波）"
      "**朝右画、上下对称**（游戏把它们转到飞行方向，往左时上下颠倒）。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 12]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `chogath_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/chogath_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「肉食者」和 E「恐惧之刺」在里面） | 直立起来再扑下来砸；打死单位回血；每 6 秒接下来 3 次攻击射出一排尖刺 | `a_hit` · "
      "`p_heal` · `e_arm` · `e_pic` · `e_hit` · `e_slow` |")
    a("| 技能 1 = Q「破裂」 | 目标点地面裂开，0.6 秒后冲出地刺，击飞、减速 | `q_crack` · `q_spikes` · `q_hit` · `q_slow` |")
    a("| 技能 2 = W「野性尖叫」 | 朝前方扇形尖叫，魔法伤害、沉默 | `w_wave` · `w_hit` · `w_sil` |")
    a("| 大招「盛宴」 | 咬一口受伤的敌方英雄，吃死就叠一层、身体变大 | `r_hit` · `r_grow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、声波、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：地刺、尖刺、碎石可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空的紫色 / 品红光", VOID), ("实心的虚空尖刺", SPIKE), ("碎石（实心）", ROCK), ("蓝紫色声波", SOUND),
                        ("盛宴的红牙", BLOOD), ("回血的绿色", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：破裂的半径 25000，尖叫的扇形 55000 长，"
      "尖刺的直线 50000 长、17000 宽）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `chogath_fx_{name}.png`：{title}\n")
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
        a(f"| `chogath_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_chogath_fx`（小的）和 `league_chogath_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_chogath.py 的 views）。")
    a("- `e_pic` / `w_wave` 是只画图的直线（Ally，没有效果）上的画面，直线的持续时间（build_chogath P e_pic_t / w_pic_t）要等于画面"
      "的时长；画在直线中点、跟着方向转，所以上下对称、朝右。`q_crack` / `q_spikes` 不跟随（地上的点）。其余跟随、左右对称。")
    a("- 用 `pixel_1x/` 切格（import_rammus_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（尖刺、碎石保留描边）；核对交回的张数和"
      "这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="chogath_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "chogath_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run fx_ref_cg.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "chogath_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "chogath_size.png"))
    shots_sheet(os.path.join(out, "design", "chogath_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"chogath_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(lp(zpath)):
            os.remove(lp(zpath))
        with zipfile.ZipFile(lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
