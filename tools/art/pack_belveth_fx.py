#!/usr/bin/env python3
"""Build belveth_fx_pack.zip: step 3 of Bel'Veth's sprite - Codex draws her effects (pack_singed_fx.py's way).

    python tools/lol/fx_ref_belveth.py             # League's particle textures -> C:/t/bv_work/fxref (Riot's art, local only)
    python tools/art/pack_belveth_fx.py [--no-zip] [--out DIR] [--only a_hit,e_hit --name belveth_fx_redo_pack]

The pack (C:/t/bv_work/fx/belveth_fx_pack, zipped into --out, default dist/belveth_packs) holds PROMPTS.md (also written to
assets/source/belveth/PROMPTS_FX.md), design/belveth_design.png (the idle at 4x, its own squares), design/belveth_size.png
(at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base fighter) and refs/lol_fx_ref.png
(League's own particle textures for Bel'Veth, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_belveth.py, the user's picks 2026-10-24: jungle, layout A - Q / W
/ R, E's maelstrom in the true form): view_projectiles w_tail; view_effects a_hit, q_dash, q_hit, w_slam (big), w_hit,
r_burst (big), r_hit, e_hit, c_eat; view_buffs p_as (p_as), slow (w_slow, r_slow), r_aura (r_on), e_storm (big, e_on).
League's colours: the Void's LAVENDER and VIOLET energy (pale lilac highlights, deep purple depths), hot MAGENTA edges,
pink-lilac VOID CORAL crystals, the sea-foam of her maelstrom (pale teal water flecks). Red side: the client never mirrors
an effect picture, so every hit, buff, ground and body picture is symmetric left to right; a projectile is turned with its
flight, so it is drawn flying right and symmetric top to bottom.
Lasting pictures (the maelstrom, the true form's aura) are a few looping frames the import stretches to the buff's life.
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
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/bv_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "belveth", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "belveth", "hd")
NAME = "belveth_fx_pack"
PPU = 1.75

VOID = "#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258"     # the Void's lavender to deep purple
MAGENTA = "#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58"           # hot magenta edges and glows
CORAL = "#FFE8F4, #F6B4DA, #DA7CBE, #A44C96, #622C60"             # the void coral: pink-lilac crystal
FOAM = "#E8FFFC, #A8E8E8, #5CB4C4, #2E7088"                       # the maelstrom's sea foam and water flecks
FLASH = "#FFFFFF, #FCF2FF, #EED2FF"                               # white-lilac flashes
DUST = "#E2DCEA, #B2A8C4, #807496, #4E4462"                       # the ground's lilac-grey dust and rock bits
VO = f"a void lavender-violet ramp ({VOID})"
MA = f"a hot magenta ramp ({MAGENTA})"
CO = f"a void coral pink-lilac ramp ({CORAL})"
FO = f"a sea-foam teal ramp ({FOAM})"
FL = f"a white-lilac flash ramp ({FLASH})"
DU = f"a lilac-grey dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
CENTER = RF.CENTER
row = RF.row
VOIDS = ("everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale "
         "lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth "
         "neon beams")
WATER = ("her maelstrom is a whirling storm of blade-sharp lavender crescents with flecks of pale teal sea foam and "
         "droplets; flat shades, crisp shapes")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HER = "Bel'Veth stands in the middle, not drawn: 46 squares wide and 47 tall (to the shoulder spikes)"
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack
    ("a_hit", "普攻：翼刃劈中，3 帧", "view_effects `league_belveth_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "膜翼像刀一样劈中敌人（参考 ba_attacklead、hitflash_core、tar_spark）：中间一下白紫色的闪光，一个 **X 形的两道淡紫色刀痕**交叉划过，"
     "边上溅开几颗品红的火星。**左右对称**，3 帧。",
     FL + ", " + VO + ", " + MA,
     "A BLADE STRIKE, 3 frames, " + LR + ": 1 a white-lilac flash 6 squares across; 2 two sharp lavender crescent cuts "
     "crossing in an X 13 across, magenta edges, a few magenta sparks flying out at mirrored places; 3 the cuts thinner and "
     "dimmer, the sparks further out, fading. " + VOIDS + ".",
     row(3, 14, 14) + CENTER),
    # ---- passive: Death in Lavender
    ("p_as", "溶烛化紫：放技能后攻速变快，脚下的紫色气流，4 帧循环",
     "view_buffs `league_belveth_p_as`（tag `p_as`，跟随她，脚下，z -1；左右对称；约 4 秒）", "30 × 10",
     "放完技能攻速变快的那几秒：她脚下**两缕淡紫色的气流**往两边打旋，几片小小的薰衣草色光点往上飘。**左右对称**，4 帧循环。",
     VO + ", " + MA,
     "A LAVENDER FRENZY, 4 looping frames, " + LR + ": two thin lavender swirls curling out from under her to both sides "
     + FEET + " 28 wide, three small lilac motes rising at mirrored places; the swirls turn and the motes rise frame to "
     "frame so the loop flows. " + VOIDS + ".",
     row(4, 30, 10) + CENTER),
    # ---- Q Void Surge
    ("q_dash", "虚空激流：起步的地方，4 帧", "view_effects `league_belveth_q_dash`（在她起步的地上，不跟随，z -1；左右对称）",
     "34 × 14",
     "虚空激流（参考 q_dashnoise、q_trail_soft、q_lightning_flipbook）：她猛地冲出去的地方，**地上一圈紫色的虚空能量炸开**，"
     "几道尖尖的紫色碎片和品红的电弧往两边甩出去。**左右对称**，4 帧。",
     VO + ", " + MA + ", " + FL,
     "A VOID LAUNCH ON THE GROUND, 4 frames, " + LR + ": 1 a white-lilac flash 10 squares wide " + FEET + "; 2 a violet "
     "ring bursting out 26 wide with sharp lavender shards thrown out to both sides; 3 the ring 32 wide, thin magenta arcs "
     "at its ends at mirrored places; 4 the ring breaking into fading shards. " + VOIDS + ".",
     row(4, 34, 14) + CENTER),
    ("q_hit", "虚空激流：穿过时打中，3 帧", "view_effects `league_belveth_q_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "冲过去时打中的敌人：一道**横着的白紫色刀光**从中间划过（左右对称：两头一样尖），上下各崩出几片紫色碎片。**左右对称**，3 帧。",
     FL + ", " + VO + ", " + MA,
     "A PASSING CUT, 3 frames, " + LR + ": 1 a white-lilac horizontal slash 16 squares long, pointed at both ends, through "
     "the middle; 2 the slash wider with magenta edges, violet shards bursting up and down at mirrored places; 3 the "
     "shards drifting out, fading. " + VOIDS + ". " + TARGET + ".",
     row(3, 18, 16) + CENTER),
    # ---- W Above and Below
    ("w_tail", "上觐沉渊：沿直线往前冲的地裂，4 帧循环", "view_projectiles `league_belveth_w_tail`（直线弹道，z 2；上下对称）",
     "22 × 10",
     "尾巴砸地后沿着一条直线往前冲的冲击（参考 w_rift、w_impactspike、w_ring_shockwave）：一道**紫色的地裂波**往前推，"
     "前头翻起几根尖尖的紫色岩刺，后面拖一条品红的光。**朝右飞、上下对称**，4 帧循环。",
     VO + ", " + MA + ", " + DU,
     "A RIFT WAVE, 4 looping frames, " + TB + ": a surging violet rift 20 squares long, its front a cluster of sharp "
     "lavender spikes bursting up and down equally from the middle line, a magenta glow and lilac-grey rock bits trailing "
     "behind on the left; the spikes rise and fall in turn so the loop surges. " + VOIDS + ".",
     row(4, 22, 10) + CENTER),
    ("w_slam", "上觐沉渊：尾巴砸地，5 帧", "view_effects `league_belveth_w_slam`（大表，在她身边的地上，不跟随，z -1；左右对称）",
     "48 × 20",
     "上觐沉渊（参考 w_splash、w_basetexture、w_ring_shockwave、medrock）：尾巴砸在地上，**地面裂开一圈紫色的冲击波**，"
     "几块岩石和紫色的水花往两边溅起来。**左右对称**，5 帧。",
     VO + ", " + MA + ", " + DU + ", " + FL,
     "A TAIL SLAM ON THE GROUND, 5 frames, " + LR + ": 1 a white-lilac impact flash 16 squares wide " + FEET + "; 2 the "
     "ground cracking in violet lines and a shock ring 36 wide, lavender splashes bursting up at both sides; 3 the ring 46 "
     "wide, lilac-grey rock chunks flying up at mirrored places; 4 the rocks falling, the cracks glowing magenta; 5 the "
     "cracks and the ring fading. " + VOIDS + ".",
     row(5, 48, 20) + CENTER),
    ("w_hit", "上觐沉渊：被击飞，4 帧", "view_effects `league_belveth_w_hit`（跟随目标，z 2；左右对称）", "18 × 26",
     "被尾巴砸中击飞的敌人（参考 w_impactspike、w_comet）：脚下**一股紫色的能量往上喷**，把人顶起来，几根尖尖的紫色碎片往上飞。"
     "**左右对称**，4 帧。",
     VO + ", " + MA + ", " + FL,
     "A LAUNCH FROM BELOW, 4 frames, " + LR + ": 1 a violet burst " + FEET + " 12 wide; 2 a column of lavender energy "
     "shooting up through the target 24 squares tall with sharp shards rising at mirrored places; 3 the column thinning, "
     "the shards high; 4 a few shards and sparkles falling, fading. " + VOIDS + ". " + TARGET + ".",
     row(4, 18, 26) + CENTER),
    ("slow", "减速：脚下缠着的紫色虚空，4 帧循环",
     "view_buffs `league_belveth_w_slow` / `league_belveth_r_slow`（tag `slow`，跟随，脚下，z -1；左右对称）", "18 × 7",
     "被减速的敌人脚下：一小圈**紫色的虚空能量**缠着脚，几缕细细的紫色触须一伸一缩。**左右对称**，4 帧循环。",
     VO + ", " + MA,
     "A VOID SNARE, 4 looping frames, " + LR + ": a flat violet ring " + FEET + " 16 wide and 5 tall, two thin lavender "
     "tendrils at mirrored places curling up and down in turn, a magenta glint going round. " + VOIDS + ".",
     row(4, 18, 7) + CENTER),
    # ---- R Endless Banquet
    ("r_burst", "万载豪筵：吞下珊瑚、化为真身的爆发，6 帧",
     "view_effects `league_belveth_r_burst`（大表，在她身边的地上和身上，不跟随，z -1；左右对称）", "64 × 48",
     "万载豪筵（参考 r_coral_base、r_flash、r_flashes_rays、r_shards、r_wave_mult、r_voidtentacles）：她脚下的**虚空珊瑚一下子炸开**——"
     "先是一下白紫色的闪光，一圈品红的冲击波贴着地往外推，粉紫色的珊瑚碎片和尖尖的紫色碎片往四周和往上飞，几根细细的虚空触须从地上扬起来。"
     "她在中间不画，**身体的位置留空**。**左右对称**，6 帧。",
     FL + ", " + VO + ", " + MA + ", " + CO,
     "A VOID CORAL BURST, 6 frames, " + LR + "; " + HER + " - leave her body's place EMPTY: 1 a white-lilac flash round her "
     "feet 20 wide " + FEET + " and light rays rising; 2 a magenta shock ring 44 wide on the ground, pink-lilac coral shards "
     "bursting out and up at mirrored places; 3 the ring 60 wide, the shards high, four thin violet tentacles rising from "
     "the ground at mirrored places; 4 the shards falling, the tentacles curling; 5 the ring thin, a few shards; 6 "
     "sparkles fading. " + VOIDS + ".",
     row(6, 64, 48) + CENTER),
    ("r_hit", "万载豪筵：被珊瑚爆发打中，3 帧", "view_effects `league_belveth_r_hit`（跟随目标，z 2；左右对称）", "16 × 18",
     "被珊瑚爆发打中的敌人：身上一下白紫色闪光，几片粉紫色的珊瑚碎片扎上来、往两边弹开。**左右对称**，3 帧。",
     FL + ", " + CO + ", " + VO,
     "A CORAL HIT, 3 frames, " + LR + ": 1 a white-lilac flash 6 squares across on the target's chest; 2 pink-lilac coral "
     "shards bursting out 15 across at mirrored places; 3 the shards falling, fading. " + VOIDS + ". " + TARGET + ".",
     row(3, 16, 18) + CENTER),
    ("r_aura", "真身：化身期间身边一直冒的虚空光，4 帧循环",
     "view_buffs `league_belveth_r_on`（tag `r_aura`，跟随她，z -1，在她身后；左右对称；约 15 秒）", "50 × 56",
     "真身期间：她身边一直**往上飘着淡紫色的虚空光点和几缕品红的光丝**，脚下一圈淡紫色的光，背后隐约张开一圈尖尖的紫色光芒（像女皇的冠）。"
     "她在中间不画，**身体的位置留空**；画在她身后，要淡一点。**左右对称**，4 帧循环。",
     VO + ", " + MA,
     "A VOID EMPRESS AURA, 4 looping frames, " + LR + "; " + HER + " - leave her body's place EMPTY: a faint fan of sharp "
     "violet light spikes behind her shoulders like a crown, small lavender motes and two thin magenta wisps rising at "
     "mirrored places, a faint violet glow ring " + FEET + " 40 wide; the motes and wisps rising frame to frame so the "
     "loop flows upward. Sparse and light - it plays behind her for 15 seconds. " + VOIDS + ".",
     row(4, 50, 56) + CENTER),
    ("c_eat", "吃珊瑚：击杀后珊瑚碎片飞进她身体，4 帧", "view_effects `league_belveth_c_eat`（跟随她，z 2；左右对称）", "30 × 36",
     "击杀以后吃掉虚空珊瑚（参考 p_coral_tx、r_onkillray、r_minion_ringflare）：**几块粉紫色的珊瑚碎片从四周飞向她**，"
     "到身上化成一圈淡紫色的光。她在中间不画，**身体的位置留空**。**左右对称**，4 帧。",
     CO + ", " + VO + ", " + FL,
     "CORAL DRAWN IN, 4 frames, " + LR + "; she stands in the middle, not drawn - leave the middle 18 squares wide EMPTY: 1 "
     "four pink-lilac coral shards at the cell's corners at mirrored places; 2 the shards halfway in with lavender trails; "
     "3 the shards reaching her outline, a white-lilac glint; 4 a lavender ring round her fading. " + VOIDS + ".",
     row(4, 30, 36) + CENTER),
    # ---- E Royal Maelstrom (in the true form)
    ("e_storm", "搠面皇锋：身边旋转的刀光风暴，6 帧循环",
     "view_buffs `league_belveth_e_on`（tag `e_storm`，大表，跟随她，z 3；左右对称；约 1.5 秒）", "60 × 44",
     "搠面皇锋（参考 e_wingflurry、eswirl、e_splashes、e_tether_crescent、swipes）：她原地不动，**身边一圈淡紫色的月牙刀光飞快地旋转**，"
     "刀光之间溅起青白色的水花（她是从海里来的），脚下一圈旋转的水纹。她在中间不画，**身体的位置留空**。**左右对称**，6 帧循环。",
     VO + ", " + MA + ", " + FO,
     "A STORM OF SLASHES, 6 looping frames, " + LR + "; " + HER + " - leave her body's place EMPTY: a whirling ring 56 wide "
     "and 40 tall of sharp lavender crescent slashes with magenta edges round her, pale teal sea-foam flecks and droplets "
     "between them, a swirling water ring " + FEET + " 50 wide; the crescents at mirrored places move round frame to frame "
     "(in frame k the left and right halves mirror each other) so the loop spins. " + WATER + ".",
     row(6, 60, 44) + CENTER),
    ("e_hit", "搠面皇锋：被风暴斩中，3 帧", "view_effects `league_belveth_e_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被风暴的刀光斩中：一道**竖着的淡紫色月牙刀痕**（左右对称）加几滴青白色的水花。**左右对称**，3 帧。",
     FL + ", " + VO + ", " + FO,
     "A STORM CUT, 3 frames, " + LR + ": 1 a white-lilac vertical crescent slash 12 squares tall in the middle; 2 the slash "
     "with magenta edges, pale teal droplets splashing out at mirrored places; 3 fading. " + WATER + ".",
     row(3, 14, 14) + CENTER),
]
BIG_FX = ["w_slam", "r_burst", "e_storm"]
FLYING = ["w_tail"]
FORWARD = []

GROUPS = [
    ("a_hit q_hit (the wing blades)", ["belveth_ba_attacklead", "belveth_base_2021_ba_hitflash_core",
                                       "belveth_base_basicattack_tar_spark", "belveth_base_swipes"]),
    ("q_dash p_as (Void Surge, the frenzy)", ["belveth_q_dashnoise", "belveth_base_q_trail_soft",
                                              "belveth_base_q_lightning_flipbook", "belveth_base_q_animeshapesmesh01"]),
    ("w_tail w_slam w_hit slow (Above and Below)", ["belveth_w_rift", "belveth_base_w_impactspike",
                                                    "belveth_base_w_ring_shockwave", "belveth_w_splash"]),
    ("w_slam rocks", ["belveth_base_medrock", "belveth_base_rockbits", "belveth_w_basetexture", "belveth_base_w_comet"]),
    ("r_burst r_hit r_aura (Endless Banquet)", ["belveth_r_coral_base", "belveth_base_r_shards", "belveth_r_flashes_rays",
                                                "belveth_base_r_voidtentacles_01"]),
    ("c_eat (the coral)", ["belveth_base_p_coral_tx", "belveth_base_r_onkillray", "belveth_base_r_minion_ringflare01",
                           "belveth_base_r_flash"]),
    ("e_storm e_hit (Royal Maelstrom)", ["belveth_e_wingflurry", "belveth_base_eswirl", "belveth_base_e_splashes",
                                         "belveth_base_e_tether_crescent"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", ppu=PPU):
    """A design at game size (1 / PPU of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, 1 / ppu, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Bel'Veth at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x()]
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
    d.text((8, 36), f"卑尔维斯 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 虚空女皇 卑尔维斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/belveth_design.png`：深紫色的脸、两只发光的品红眼睛、头顶品红的冠，"
      "两肩高高的深紫长刺，两只收拢像斗篷一样的深灰青膜翼，下面粉紫色的爪子，左边拖在地上的长尾巴）。"
      f"她在游戏里是**高清**的（每个游戏格子里约 1.75×1.75 个细像素），{h} 格高、{w} 格宽（高×宽，连肩刺和尾巴）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/belveth_size.png`：卑尔维斯放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卑尔维斯自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。"
      "**卑尔维斯是虚空女皇**：她的力量是**锋利的淡紫 / 紫色虚空能量**（月牙刀光、尖尖的碎片，边缘品红，中心近白），"
      "吞下的是**粉紫色的虚空珊瑚**，旋风里夹着**青白色的海水泡沫**（她从海底来）；不要火、不要电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。")
    a("> - **能量、刀光、冲击波、水花、尘土都没有黑描边**（用它自己最深的一档）。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`" +
      "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。")
    a("> - **持续的画面**（真身光 15 秒、刀光风暴 1.5 秒、减速、攻速）只画几帧循环，Claude 导入时按时长拉开循环。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `belveth_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/belveth_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 用膜翼像刀一样劈砍，打得很快 | `a_hit` |")
    a("| 被动「溶烛化紫」 | 每放一个技能攻速变快几秒；击杀英雄叠永久攻速、吃掉虚空珊瑚 | `p_as` · `c_eat` |")
    a("| 技能 1 =「虚空激流」 | 朝目标冲过去，穿过的敌人都受伤 | `q_dash` · `q_hit` |")
    a("| 技能 2 =「上觐沉渊」 | 尾巴砸地，一道地裂沿直线往前冲，打中的敌人被击飞、减速 | `w_slam` · `w_tail` · `w_hit` · `slow` |")
    a("| 大招 =「万载豪筵」 | 吞下虚空珊瑚爆开（伤害、减速），化为真身 15 秒（生命、攻击距离、攻速、移速变高） | `r_burst` · `r_hit` · `r_aura` · `slow` |")
    a("| 真身里的「搠面皇锋」 | 被围住时原地化成刀光风暴：减伤、吸血，斩最近被打的敌人 | `e_storm` · `e_hit` |\n")
    a("连招：**尾巴击飞英雄 → 立刻再冲一次**，**冲过英雄 → 马上甩尾**，**敌方英雄阵亡 → 吃珊瑚**（真身续上或大招冷却缩短），**真身期间冲得更远更快**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**能量、刀光、冲击波、水花、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的亮点。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空·淡紫到深紫", VOID), ("品红", MAGENTA), ("虚空珊瑚·粉紫", CORAL), ("海水泡沫·青白", FOAM),
                        ("闪光·白紫", FLASH), ("尘土·紫灰", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的东西（冲击波、地裂、脚下的光圈和水纹）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `belveth_fx_{name}.png`：{title}\n")
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
        a(f"| `belveth_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_belveth_fx`（小的）和 `league_belveth_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_belveth.py 的 views；w_slow 和 r_slow 用 `slow`，r_on 用 `r_aura`，e_on 用 `e_storm`，p_as 用 `p_as`）。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；其余断言左右对称。e_storm 循环 e_t（90 tick），r_aura 循环 r_t，p_as 循环 p_t，slow 循环。")
    a("- 用 `pixel_1x/` 切格（import_zac_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="belveth_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "belveth_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    RF.REF, RF.GROUPS = REF, GROUPS
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_belveth.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "belveth_design.png"))
    shape = size_sheet(os.path.join(out, "design", "belveth_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"belveth_fx_{x[0]}.png", "binding": x[2], "size": x[3],
                    "symmetry": "top-bottom" if x[0] in FLYING else ("none (forward)" if x[0] in FORWARD else "left-right")}
                   for x in FX], f, ensure_ascii=False, indent=1)
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
