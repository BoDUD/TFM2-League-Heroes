#!/usr/bin/env python3
"""Build malzahar_fx_pack.zip: step 3 of Malzahar's sprite - Codex draws his effects (tools/art/pack_bard_fx.py's way).

    python tools/art/pack_malzahar_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name malzahar_fx_redo_pack]

The pack (%TEMP%/mz_work/fx/malzahar_fx_pack, zipped into --out, default dist/malzahar_packs) holds PROMPTS.md (also
written to assets/source/malzahar/PROMPTS_FX.md), design/malzahar_idle.png (his dense design at 6x),
design/malzahar_size.png (his idle as the game shows it - PPU 1.38 at hd.rs SIZES 1.15 - at 4x a game pixel on the
arena colour with the feet line, a 10-px ruler and the base fighter beside him), design/malzahar_shots.png (the action
frames the pictures start from, 4x), refs/lol_fx_ref.png (League's own particle textures for Malzahar, grouped by the
effect of ours they inform; Riot's art, local only: %TEMP%/mz_work/fxref from Malzahar.wad.client's base-skin particles,
%TEMP%/mz_work/fx/fx_ref_mz.py) and refs/voidling.png (League's voidling model, local render: tools/lol/pose_ref.py
--champ MalzaharVoidling --wad Malzahar).
The effects are the views the kit binds (tools/kit/build_malzahar.py): view_projectiles a_bolt, e_bolt; view_effects
a_hit, e_hit, e_mark (also the add-on's buff e_markb), w_spawn, w_swarm, w_bite, q_rift, q_hit, r_grasp, r_pool;
view_buffs p_shift. League's colours: the void's violet and black-purple, white-violet light, his magenta, the
voidlings' lilac-grey shells with magenta eyes. Light gets no outline. Red side: the flying pictures symmetric top to
bottom (they turn with the flight), every other picture symmetric left to right (nothing of his is mirrored for the red
side: the voidlings come as a mirrored pair).
He is about 33 x 40 game px in game (PPU 1.38, 115 %).
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "mz_work")
REF = os.path.join(TMP, "fxref")
VOIDLING = os.path.join(TMP, "fx", "voidling_attack.png")
DOC = os.path.join(ROOT, "assets", "source", "malzahar", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_malzahar")
HD_FRONT = os.path.join(ROOT, "assets", "source", "malzahar", "hd", "front.png")   # the approved dense design
SHOWN = 1.38 / 1.15             # his dense squares a shown game pixel
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VOID = "#FFFFFF, #F3E3FF, #D9A6FF, #B163F5, #8130D9, #5A169E, #36095F"     # void violet light
DARK = "#4A1C7A, #2E0F52, #1C0838, #100422"                               # the void's black-purple (dark matter)
MAG = "#FFE3F4, #FF86D2, #EE3AA6, #B4187A, #6E0B4B"                       # his magenta
SHELL = "#EFE6F2, #C6B4D2, #9682A8, #67527A, #3D2C4E"                     # the voidlings' lilac-grey shells
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, sparks or rings (dark void matter may have its own darkest shade at its edge), BRIGHT "
        "light (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), "
        "colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
VD = f"a void-violet ramp ({VOID})"
DK = f"a dark void ramp ({DARK})"
MG = f"a magenta ramp ({MAG})"
SH = f"a lilac-grey shell ramp ({SHELL})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack
    ("a_bolt", "普攻：飞出去的虚空弹（朝目标飞，循环），4 帧",
     "view_projectiles `league_malzahar_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "10 × 6",
     "从手心甩出去的一颗小虚空弹：紫白色的小光球，外面一圈紫色，后面拖一小段暗紫色的虚空烟和几个小光点（参考 BA_mis_dots、BA_Mis_mult、common_voidtrailhot）。**上下对称**，朝右飞。",
     f"{VD} and {DK}",
     f"a SMALL VOID BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white-violet glowing ball 4 squares "
     "across at the front inside a violet halo, a short tapering trail of dark purple void smoke behind it with 2-3 "
     "violet motes flickering in turn.",
     row(4, 12, 8) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_malzahar_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "虚空弹打中：目标身上紫白色的光一闪，炸成一圈小小的紫色火花（参考 BA_muzzle_flash、common_voidslash）。**左右对称**。约 10 格，居中画。",
     VD,
     f"a VOID HIT on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 a violet four-pointed burst 8 squares across "
     "with a white core; 3 the burst breaking into 6 small violet sparks at mirrored places, 10 squares across; 4 two "
     "fading specks.",
     row(4, 12, 12) + "; centered in every cell."),
    # ---- E Malefic Visions (+ W)
    ("e_bolt", "E 煞星幻象：飞出去的幻象（朝目标飞，循环），4 帧",
     "view_projectiles `league_malzahar_e_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "14 × 8",
     "飞向目标的幻象：前头一团暗紫色的虚空球，中间一点紫白的光，球面上闪着细细的紫色电弧，后面拖一条扭动的暗紫色烟尾（参考 E_Mis_AlphaCircles、E_Lightning03、E_SmokeErode、Demon_Trail4）。**上下对称**，朝右飞。",
     f"{VD} and {DK}",
     f"a DARK VISION ORB flying to the RIGHT, 4 frames, a seamless loop, {TB}: a dark purple void ball 6 squares across "
     "with a white-violet core and thin violet lightning crackling over it (the crackle pattern mirrored top to bottom), "
     "a wavy dark purple smoke tail 8 squares long behind it, its two edges mirrored.",
     row(4, 16, 10) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("e_hit", "E 打中：幻象缠上目标（目标身上），5 帧", "view_effects `league_malzahar_e_hit`（跟随，画在人物上面；左右对称）", "18",
     "幻象缠上目标的一下：一圈暗紫色、带锯齿边的虚空环在目标身上一合（参考 E_Edges、E_ImpactT），环里闪出紫白的光，几道紫色电弧往外蹦。**左右对称**，中间人形位置留空。",
     f"{VD} and {DK}",
     f"a VISION LATCHING on a unit, 5 frames, {LR}, its middle EMPTY (a clear upright area 8 squares wide): 1 a white "
     "violet flash 4 squares; 2 a jagged dark purple ring 18 squares across closing in, violet light along its inner "
     "edge; 3 the ring 12 squares across, 4 violet lightning sparks jumping out at mirrored places; 4 the ring breaking "
     "into dark wisps; 5 fading wisps.",
     row(5, 20, 20) + "; centered in every cell."),
    ("e_mark", "E 幻象持续：缠在目标身上的虚空电弧（目标身上，1 秒循环），4 帧",
     "view_effects `league_malzahar_e_mark`（跟随，画在人物上面；左右对称；4 帧 1 秒，幻象持续时每秒放一次）；附加包跳过去的幻象也用这张（buff `league_malzahar_e_markb`）",
     "22 × 26",
     "被煞星幻象缠住：目标上半身两边有暗紫色的虚空烟一缕缕往上飘，烟里噼啪闪着细细的紫白电弧（参考 E_Static_01、E_Lightning03、P_Morgana_Base_E_Wisps）。**中间人形位置留空**，**左右对称**。",
     f"{VD} and {DK}",
     f"VOID WISPS AND CRACKLES round a unit's upper body, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear "
     "upright area 10 squares wide and 22 tall): at each side 2 thin dark purple wisps rising and curling, small "
     "white-violet lightning zigzags (2-4 squares) flickering in them at mirrored places, a different pair lit in each "
     "frame.",
     row(4, 24, 28) + "; centered across, the wisps' bottom 2 squares above the cell's bottom."),
    ("w_spawn", "W 虚空虫群：虫子出现的小虚空门（目标脚下），4 帧",
     "view_effects `league_malzahar_w_spawn`（跟随，画在人物下面；左右对称）", "22 × 8",
     "虚空虫从地下钻出来的门：目标脚下一个扁扁的紫色虚空门（从斜上方看的椭圆，亮紫色的边，中间深紫黑，参考 W_VoidGate_Core_ring、W_VoidGate_DarkGround、W_Portal_Swirl），打开、闪光、合上。**左右对称**。",
     f"{VD} and {DK}",
     f"a SMALL VOID GATE on the ground, 4 frames, {LR}: a flat ellipse 22 squares wide and 8 tall, its rim bright violet "
     "1 square thick, its inside dark purple-black with a violet swirl; 1 a thin violet line opening; 2 the gate open, "
     "a few violet motes spurting up at mirrored places; 3 the gate's rim brightest; 4 the gate shrinking to a thin "
     "fading line.",
     row(4, 24, 10) + "; centered in every cell."),
    ("w_swarm", "W 虚空虫：两只虚空虫在目标脚边咬他（目标身上，1 秒循环），4 帧",
     "view_effects `league_malzahar_w_swarm`（跟随，画在人物下面；左右对称；4 帧 1 秒，每秒放一次，持续 4 秒）", "34 × 12",
     "两只虚空虫（参考 `refs/voidling.png`：灰紫色的甲壳头、两三只发光的洋红色眼睛、紫色的身体、镰刀一样的前爪），**一左一右在目标脚边，互相对着（左边那只朝右、右边那只朝左，像镜子一样对称）**，扑上去咬目标、退回来，轮流。中间人形位置留空。",
     f"{SH}, {DK} and {MG}",
     f"TWO VOIDLINGS biting at a unit's feet, 4 frames, a seamless loop, {LR} (the left one facing right, the right one "
     "its mirror image facing left), the middle EMPTY (a clear area 14 squares wide): each voidling 9 squares wide and 8 "
     "tall - a lilac-grey armored head with 2-3 glowing magenta eyes and small fangs, a dark purple body, two sickle "
     "claws, short legs; 1 both crouched; 2 both lunging inward 2 squares, claws raised; 3 both biting (closest); 4 both "
     "springing back.",
     row(4, 36, 14) + "; centered across, their feet on the cell's bottom row."),
    ("w_bite", "W 虫子咬一口（目标身上），3 帧", "view_effects `league_malzahar_w_bite`（跟随，画在人物上面；左右对称）", "10",
     "虚空虫咬中：目标身上两道洋红色的爪痕交叉一闪（左右对称的 X），几个小紫点溅开。**左右对称**。",
     f"{MG} and {VD}",
     f"a VOIDLING BITE on a unit, 3 frames, {LR}: 1 two magenta claw marks crossing as an X, 8 squares, white at the "
     "crossing; 2 the X brighter, 4 violet specks flying out at mirrored places; 3 fading marks.",
     row(3, 12, 12) + "; centered in every cell."),
    # ---- Q Call of the Void
    ("q_rift", "Q 虚空召唤：目标两侧的两道裂隙，合拢时两道光束在中间相撞（地上，不跟随，约 0.5 秒），6 帧",
     "view_effects `league_malzahar_q_rift`（不跟随，画在人物上面；左右对称；前 4 帧 0.4 秒，第 5 帧光束相撞=伤害生效）", "40 × 24",
     "虚空召唤：目标**左右两边**各撕开一道竖着的虚空裂隙（细长的紫黑色裂口，边缘亮紫色、闪着电弧，参考 W_Portal_Swirl、Q_Lightning03、Q_OrbEdge），慢慢张开发亮；然后**两道裂隙同时朝中间射出紫白色的光束，在正中间撞在一起**一炸，裂隙合上。**左右对称**（两道裂隙是一对镜像）。两道裂隙相距约 36 格。",
     f"{VD} and {DK}",
     f"TWO VOID RIFTS facing each other, 6 frames, {LR}: two upright rifts 36 squares apart (their middles at columns "
     "2 and 37 of the 40), each a narrow dark purple-black tear 4 squares wide and 20 tall with a bright violet jagged "
     "rim and small lightning crackles; 1 two thin violet cracks; 2 the rifts half open; 3 fully open, dark inside; 4 "
     "the rims brightest, violet light gathering inside; 5 two white-violet beams 3 squares thick shooting from both "
     "rifts to the middle and meeting there in a white flash 8 squares across (one straight horizontal line across the "
     "whole width at the rifts' middle height); 6 the beams gone, the rifts closing to fading cracks.",
     row(6, 42, 26) + "; centered across, the rifts' bottom 2 squares above the cell's bottom."),
    ("q_hit", "Q 打中：被沉默（目标身上），4 帧", "view_effects `league_malzahar_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "被虚空光束打中、沉默：目标身上紫白的光一炸，散成一圈紫色电火花（参考 Q_Lightning03、common_voidslash）。**左右对称**。",
     VD,
     f"a VOID BLAST on a unit, 4 frames, {LR}: 1 a white-violet flash 5 squares; 2 a violet burst 12 squares across "
     "with a white core; 3 a ring of 8 small violet lightning sparks 14 squares across at mirrored places; 4 fading "
     "sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    # ---- R Nether Grasp
    ("r_grasp", "R 冥府之握：从地下伸出来抓住目标的虚空触手（目标身上，循环），4 帧",
     "view_effects `league_malzahar_r_grasp`（跟随，画在人物上面；左右对称；4 帧共 0.25 秒，引导时每 0.25 秒放一次）", "26 × 30",
     "被冥府之握压制：两条暗紫色的虚空触手从目标脚下两边伸出来，弯上去缠住目标的腰和胸口（触手边缘亮紫色，上面有一节节的纹路，参考 W_VoidTentacles_01、Z_VoidTentacles_01、R_beam_Palette），触手间闪着紫白的电弧，微微扭动。**左右对称**（两条触手是一对镜像），中间人形位置留空。",
     f"{DK}, {VD} and {MG}",
     f"VOID TENTACLES GRIPPING a unit, 4 frames, a seamless loop, {LR}, the middle EMPTY (a clear upright area 10 "
     "squares wide and 24 tall): two thick dark purple tentacles rising from the ground at both sides, 4 squares thick "
     "at the root tapering to 2, curling up and inward round the unit's waist and chest, their edges bright violet, "
     "magenta segment marks on them; small white-violet lightning crackling between them; the tentacles writhing a "
     "little from frame to frame (every frame mirrored).",
     row(4, 28, 32) + "; centered across, the tentacles' roots on the cell's bottom row."),
    ("r_pool", "R 冥府领域：目标脚下的虚空领域（地上，不跟随，5 秒），8 帧",
     "view_effects `league_malzahar_r_pool`（不跟随，画在人物下面；左右对称；1-2 打开，3-6 循环，7-8 消失，导入时拼成 5 秒）", "40 × 14",
     "冥府之握留下的虚空领域：地上一个大圆（从斜上方看的扁椭圆），边缘一圈亮紫色，里面是暗紫黑色的虚空，里面有紫色的星点和慢慢转的漩涡（参考 Void_03、Void_05、Crater_01、W_VoidGate_DarkGround），边上一圈小火苗一样的紫色光往上冒。**左右对称**。范围约 40 格宽（半径 20000）。",
     f"{DK}, {VD} and {MG}",
     f"a NULL ZONE on the ground, 8 frames, {LR}: a flat ellipse 40 squares wide and 14 tall, its rim violet 1-2 "
     "squares thick, its inside dark purple-black with violet star motes and a slow violet swirl, small violet flames "
     "licking up from the rim at mirrored places; 1 a thin violet ring appearing; 2 the zone filling; 3-6 a seamless "
     "loop: the swirl and the flames shifting step by step (every frame mirrored); 7 the zone fading to its rim; 8 a "
     "faint thin ring.",
     row(8, 42, 16) + "; centered in every cell."),
    # ---- the passive
    ("p_shift", "被动 虚空穿越：玛尔扎哈身上的虚空护盾（他身上，循环），4 帧",
     "view_buffs `league_malzahar_p_shift`（跟随，画在人物上面；左右对称）", "34 × 44",
     "虚空穿越的护盾：玛尔扎哈全身外面一层很薄的紫白色光壳（竖着的椭圆，只画边缘一两格宽的弧光，上面几处亮的高光，参考 P_Shield_Edges、Q_Shield_Edges），光在边上慢慢流动。**中间人形位置留空**（他自己在里面），**左右对称**。",
     VD,
     f"a THIN VOID SHELL round a figure, 4 frames, a seamless loop, {LR}, its inside EMPTY (a clear upright area 28 "
     "squares wide and 38 tall): an upright ellipse 34 squares wide and 44 tall drawn only as a thin violet rim 1 square "
     "thick, brighter white-violet arcs 6-8 squares long on it at mirrored places moving one step round in each frame, "
     "a few violet motes beside the rim.",
     row(4, 36, 46) + "; centered across, the shell's bottom 1 square above the cell's bottom."),
]

GROUPS = [
    ("a_* q_*", ["Malzahar_Base_BA_mis_dots", "Malzahar_Base_BA_Mis_mult", "Malzahar_Base_BA_muzzle_flash", "common_voidtrailhot",
                 "common_voidslash", "Malzahar_Base_Q_Lightning03", "Malzahar_Base_Q_OrbEdge", "Malzahar_Base_W_Portal_Swirl"]),
    ("e_*", ["Malzahar_Base_E_Mis_AlphaCircles", "Malzahar_Base_E_Lightning03", "Malzahar_Base_E_SmokeErode",
             "Malzahar_Base_Demon_Trail4", "Malzahar_Base_E_Edges", "Malzahar_Base_E_ImpactT", "Malzahar_Base_E_Static_01",
             "Malzahar_Base_P_Morgana_Base_E_Wisps"]),
    ("w_*", ["Malzahar_Base_W_VoidGate_Core_ring", "Malzahar_Base_W_VoidGate_DarkGround", "Malzahar_Base_W_Portal_Bolts_8x1",
             "Malzahar_Base_W_EdgeRing"]),
    ("r_* p_*", ["Malzahar_Base_W_VoidTentacles_01", "Malzahar_Base_Z_VoidTentacles_01", "Malzahar_Base_R_beam_Palette",
                 "Malzahar_Base_Void_03", "Malzahar_Base_Void_05", "Malzahar_Base_Crater_01", "Malzahar_Base_P_Shield_Edges",
                 "Malzahar_Base_Q_Shield_Edges"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_bolt：从远侧手心飞出去"),
         ("skill", 3, "e_bolt：爪手推出，幻象飞出"),
         ("skill2", 3, "q_rift：两手合拢，裂隙在目标两侧张开"),
         ("ult", 4, "R：两手抓住，目标被触手缠住")]


def ref_sheet(path):
    S, LW = 170, 90
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 14, 24, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Malzahar_Base_", "")[:24], fill=(170, 190, 210, 255))
    sheet.save(path)


def hd_idle():
    import ppu_hd as P
    s = P.read_sheet(SHEET)
    f = s["hd_idle"][0][0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His idle as the game shows it (dense squares at 1 / SHOWN a game pixel) at 4x a game pixel on the arena colour,
    the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = hd_idle()
    Z, pad = 4, 6
    fw, fh = int(round(fig.shape[1] / SHOWN)), int(round(fig.shape[0] / SHOWN))
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    kn = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    W = pad + fw + pad + kn.shape[1] + pad
    float_px = 3                                     # he floats about 3 game px over the ground
    img = Image.new("RGBA", (max(W * Z, 760), (pad + max(fh + float_px, kn.shape[0]) + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + max(fh + float_px, kn.shape[0])
    img.alpha_composite(Image.fromarray(fig).resize((fw * Z, fh * Z), Image.NEAREST),
                        (pad * Z, (base - float_px - fh) * Z + 64))
    img.alpha_composite(Image.fromarray(kn).resize((kn.shape[1] * Z, kn.shape[0] * Z), Image.NEAREST),
                        ((2 * pad + fw) * Z, (base - kn.shape[0]) * Z + 64))
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fw + 1, 10):
        x = (pad + i) * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"玛尔扎哈 约 {fw}×{fh} 格（游戏里的大小，悬浮离地约 3 格），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（都是 4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return (fh, fw)


def shots_sheet(path):
    """The finished action frames as the game shows them, 4x a game pixel, his standing point as a cyan cross."""
    import ppu_hd as P
    s = P.read_sheet(SHEET)
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = s["hd_" + tag][k - 1][0]
        H, W = f.shape[:2]
        gw, gh = int(round(W / SHOWN * Z)), int(round(H / SHOWN * Z))
        im = Image.new("RGBA", (max(gw, 330), gh + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(f).resize((gw, gh), Image.NEAREST), ((max(gw, 330) - gw) // 2, 24))
        d = ImageDraw.Draw(im)
        cx = (max(gw, 330) - gw) // 2 + gw // 2
        cy = 24 + gh // 2 + int(round(11.5 * Z))     # the pivot is the frame's centre, the ground 11.5 game px under it
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 虚空先知 玛尔扎哈：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/malzahar_idle.png`：游戏里的 3/4 正面待机，悬浮，脚尖朝下）。他在游戏里约 {w} 格宽、{h} 格高（悬浮离地约 3 格）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素）。")
    a("> - 大小对照 `design/malzahar_size.png`：他在游戏里的样子放大 4 倍，红线是地面，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/malzahar_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里玛尔扎哈自己的特效贴图（虚空弹、幻象的电弧和烟、W 的虚空门、Q 的电弧、R 的触手和虚空），按用在我们哪张特效分好了行；"
      "`refs/voidling.png` 是英雄联盟里虚空虫的模型（灰紫色甲壳头、洋红色眼睛、镰刀前爪）。都只在本地用，不要提交。"
      "颜色照英雄联盟原版：**虚空的紫色和紫黑色、紫白色的光、他的洋红色、虚空虫灰紫色的壳和洋红色的眼睛**。")
    a("> - **特效要亮**：每道光、每个电弧都要有白色或最亮一档的芯，暗底上一眼能看见；暗紫黑的虚空物质（触手、领域、烟）旁边要有亮紫色的边，不然在暗底上看不见。")
    a("> - **围着人的光壳、电弧、触手、虫子只画外圈，中间人形位置留空**。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bolt`、`e_bolt` 画成朝右，**上下对称**（往左飞时会上下翻）。"
      "其余所有画面（打中、身上、脚下、地上的圈、裂隙、虫子、触手、护盾）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）：两只虚空虫画成一左一右互相对着的镜像，两道裂隙、两条触手也是镜像。")
    a(f"> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `malzahar_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `malzahar_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「虚空穿越」 | 甩出虚空弹；身上一层虚空护盾（被打破后过一会儿回来） | `a_bolt` · `a_hit` · `p_shift` |")
    a("| 技能 1 = E「煞星幻象」+ W「虚空虫群」 | 幻象飞向目标、缠住他持续掉血（目标死了会跳到附近的敌人）；虚空虫从目标脚下钻出来咬他 | `e_bolt` · `e_hit` · `e_mark` · `w_spawn` · `w_swarm` · `w_bite` |")
    a("| 技能 2 = Q「虚空召唤」 | 目标两侧撕开两道裂隙，光束在中间相撞：伤害 + 沉默 | `q_rift` · `q_hit` |")
    a("| 大招 = R「冥府之握」 | 压制一个敌方英雄 2.5 秒（虚空触手缠住他），脚下留下 5 秒的虚空领域 | `r_grasp` · `r_pool` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电弧、光环都没有黑描边，也不要用最深的颜色给光描一圈边**（暗紫黑的触手、领域可以用自己最深一档收边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空紫光", VOID), ("虚空暗紫", DARK), ("洋红", MAG), ("虚空虫的甲壳", SHELL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的门、领域是从斜上方看的椭圆（宽是高的 2.5–3 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 52000，"
      "Q 打中半径 18000，R 领域半径 20000，E 跳转距离 40000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `malzahar_fx_{name}.png`：{title}\n")
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
        a(f"| `malzahar_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_malzahar_fx`（小的）和 `league_malzahar_big`（q_rift、r_grasp、r_pool），tag = 名字（build_malzahar.py 的 views；"
      "`e_markb` 绑到 `e_mark` 这张）。")
    a("- 飞行的 `a_bolt`、`e_bolt` 朝飞行方向转；`q_rift`、`r_pool` 不跟随；`e_mark`、`w_swarm` 4 帧 1 秒；`r_grasp` 4 帧 0.25 秒；`q_rift` 前 4 帧共 24 tick、第 5 帧光束相撞；`r_pool` 拼成 5 秒（1-2 打开、3-6 循环、7-8 消失）。")
    a("- 用 `pixel_1x/` 切格（import_bard_fx 的做法），断言对称；必要时从 raw 重读（Codex 的读回可能清掉中间）；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="malzahar_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "malzahar_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/mz_work/fx/fx_ref_mz.py first")
    if not os.path.exists(SHEET + "#sheet.png"):
        sys.exit(f"no imported sprite {SHEET}#sheet.png: build this pack after step 2")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hd = np.asarray(Image.open(HD_FRONT).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(hd, 6, 0), 6, 1)).save(os.path.join(out, "design", "malzahar_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "malzahar_size.png"))
    shots_sheet(os.path.join(out, "design", "malzahar_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    shutil.copyfile(VOIDLING, os.path.join(out, "refs", "voidling.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"malzahar_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
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
