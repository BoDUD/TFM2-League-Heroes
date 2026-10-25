#!/usr/bin/env python3
"""Build rumble_fx_pack.zip: step 3 of Rumble's sprite - Codex draws his effects (pack_yorick_fx.py's way).

    python tools/lol/fx_ref_rumble.py           # League's particle textures -> C:/t/ru_work/fxref (Riot's art, local only)
    python tools/art/pack_rumble_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name rumble_fx_redo_pack]

The pack (C:/t/ru_work/fx/rumble_fx_pack, zipped into --out, default outputs/ like his pose pack) holds PROMPTS.md (also
written to assets/source/rumble/PROMPTS_FX.md), design/rumble_design.png (the approved idle at 4x on its own squares),
design/rumble_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/lol_fx_ref.png (League's own particle textures for Rumble, grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_rumble.py, the user's picks 2026-10-25: top, Q / E / R, W in
the controller): view_effects a_hit, oh_hit, q_hit, e_hit, e2_hit, dz_on, oh_on, r_launch, r_fall; view_projectiles
e_harpoon; view_buffs w_shield, haste, dz_steam, oh_smoke, e_zap, burn; and q_flame, drawn into his own skill frames
(the flame rides on him and has a front and a back; the client mirrors his frames, never an effect picture).
League's colours: Flamespitter's FIRE (white-yellow core to deep red), soot and black SMOKE, the harpoon's ELECTRIC
cyan-blue, white STEAM from the overheating mech, the Scrap Shield's BRASS and steel junk. Red side: the client never
mirrors an effect picture, so every hit, buff, ground and body picture is symmetric left to right; a projectile is
turned with its flight, so it is drawn flying right and symmetric top to bottom.
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

TMP = "C:/t/ru_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "rumble", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "rumble", "hd")
NAME = "rumble_fx_pack"
PPU = 1.75

FIRE = "#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010"      # Flamespitter: white-yellow core to deep red
SMOKE = "#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C"              # soot, burnt oil, black smoke
ELEC = "#FFFFFF, #CCF6FF, #70DCFF, #2C98F4, #1A4CB8"               # the electro-harpoon's arcs
STEAM = "#FFFFFF, #E6EEF2, #BCCAD2, #8A9CA8"                        # white steam venting from the hot mech
BRASS = "#FFF2C4, #ECBE56, #B47E2C, #72501C, #3C2A12"              # the scrap shield's brass plates
STEEL = "#E2E6EA, #A0A8B0, #646C74, #3A4046"                       # bolts, nuts, sheet steel
FI = f"a fire ramp ({FIRE})"
SM = f"a soot and smoke ramp ({SMOKE})"
EL = f"an electric ramp ({ELEC})"
ST = f"a steam ramp ({STEAM})"
BR = f"a brass ramp ({BRASS})"
SL = f"a steel ramp ({STEEL})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game "
      "turns the picture with its flight, so flying left it is upside down)")
OWN = ("pointing RIGHT, NOT symmetric (drawn into his own skill frames at the cannon's muzzle; the game mirrors his frames "
       "with him)")
CENTER = RF.CENTER
row = RF.row
JUNK = ("everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling "
        "cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes")
TARGET = "the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall"
HIM = ("Rumble's mech stands in the middle, not drawn: 36 squares from the mohawk to the ground, its hull about 24 squares "
       "wide")
FEET = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- attack (+ Overheat's burning blows)
    ("a_hit", "普攻：铁球砸中，3 帧", "view_effects `league_rumble_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "带刺铁球砸在敌人身上：一个白色的闪光，几块铁片和橙色火星往外弹（参考 hiteffect、sharp_flash、metal_shards）。**左右对称**，3 帧。",
     SL + ", " + FI,
     "A SPIKED IRON BALL STRIKE LANDING, 3 frames, " + LR + ": 1 a white flash 5 squares across; 2 a ring of short orange "
     "sparks and little grey metal shards bursting out 11 across at mirrored places; 3 the sparks further out, dimming. "
     + JUNK + ".",
     row(3, 12, 12) + CENTER),
    ("oh_hit", "过热：烧着的一击，4 帧", "view_effects `league_rumble_oh_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "过热时的普攻：铁球砸中处炸开一团火，火舌往上窜、冒黑烟（参考 fireball_hit、overheat_plasma）。**左右对称**，4 帧。",
     FI + ", " + SM,
     "A BURNING STRIKE, 4 frames, " + LR + ": 1 a white-yellow flash 6 across; 2 an orange fire burst 12 across, flame "
     "tongues licking up at mirrored places; 3 the flames 8 squares tall, black smoke curls rising from them; 4 smoke and "
     "embers. " + JUNK + ".",
     row(4, 14, 14) + CENTER),
    # ---- skill: Q Flamespitter
    ("q_flame", "纵火盛宴：喷火炮喷出的火，4 帧循环（画进他自己的动作帧）", "画进 skill 动作帧（q_spray 的炮口；跟着他翻转，可以有方向）",
     "40 × 18",
     "喷火炮喷出的**一大股火**：从格子左边中间（炮口）喷出，往右越来越宽、越来越暗，最前面卷成翻滚的火团、冒黑烟（参考 flames_flamethrower、"
     "color-flamethrower、flames02/03）。**朝右，不用对称**（这张画进他自己的动作帧，会跟着他一起翻），4 帧循环。",
     FI + ", " + SM,
     "A FLAMETHROWER BLAST, 4 looping frames, " + OWN + ": the fire pours out of a nozzle at the MIDDLE of the cell's "
     "LEFT edge: a white-yellow core 3 squares tall at the nozzle, widening to the right into a roaring orange cone 14 "
     "squares tall at 30 squares, its far end breaking into rolling red-orange fireballs and curls of black smoke at the "
     "right edge; the tongues and fireballs shift a step forward each frame so it loops. " + JUNK + ".",
     row(4, 40, 18) + "; the nozzle at the middle of the left edge in every cell."),
    ("q_hit", "纵火盛宴：被火烧到，3 帧", "view_effects `league_rumble_q_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "被喷火烧到：身上冒起几簇小火苗和火星。**左右对称**，3 帧。",
     FI + ", " + SM,
     "A SCORCH ON A UNIT, 3 frames, " + LR + ": 1 two small orange flames 4 squares tall at mirrored places 6 apart; 2 the "
     "flames 7 tall, embers flying up; 3 the flames shrinking, a wisp of black smoke. " + JUNK + ".",
     row(3, 12, 12) + CENTER),
    # ---- skill2: E Electro-Harpoon
    ("e_harpoon", "电子鱼叉：飞出去的鱼叉，4 帧循环", "view_projectiles `league_rumble_e_harpoon`（弹道，z 2；上下对称）", "16 × 8",
     "射出去的**电子鱼叉**：一支钢鱼叉头朝右，叉身缠着蓝白色的电弧，后面拖着一条电光尾巴（参考 taze_mis_missile、taze_mis_electric、"
     "taze_mis_trail）。**朝右飞，上下对称**，4 帧循环。",
     SL + ", " + EL,
     "AN ELECTRO-HARPOON IN FLIGHT, 4 looping frames, " + TB + ": a steel harpoon 9 squares long, its barbed head at the "
     "right, crackling cyan-blue electric arcs wrapped round its shaft, a jagged cyan-white lightning trail 6 long behind "
     "it; the arcs jump to new places each frame (mirrored top and bottom). " + JUNK + ".",
     row(4, 16, 8) + CENTER),
    ("e_hit", "电子鱼叉：打中，3 帧", "view_effects `league_rumble_e_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "鱼叉打中：蓝白色的电光炸开，几道电弧往外窜（参考 taze_tar_plasma、taze_tar_sphere）。**左右对称**，3 帧。",
     EL,
     "AN ELECTRIC JOLT, 3 frames, " + LR + ": 1 a white-cyan flash 6 across; 2 a ball of crackling blue sparks 10 across "
     "with jagged arcs shooting out at mirrored places to 13 across; 3 a few arcs and sparks dimming. " + JUNK + ".",
     row(3, 14, 14) + CENTER),
    ("e2_hit", "电子鱼叉：第二发打中（更强），4 帧", "view_effects `league_rumble_e2_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "第二发鱼叉打中同一个人：比第一发更大的电光爆开，一圈蓝色电环往外扩（参考 blue_rings、flare-rainbow_blue）。**左右对称**，4 帧。",
     EL,
     "A BIGGER ELECTRIC BLAST, 4 frames, " + LR + ": 1 a white star flash 8 across; 2 a cyan-blue ring 14 across with "
     "jagged arcs sticking out at mirrored places; 3 the ring 17 across breaking into sparks; 4 sparks and two small arcs "
     "fading. " + JUNK + ".",
     row(4, 18, 18) + CENTER),
    ("e_zap", "电子鱼叉：被减速的人身上噼啪的电，4 帧循环", "view_buffs `league_rumble_e_zap`（跟随，身上，z 3；左右对称）", "20 × 30",
     "被鱼叉减速的敌人：身体两边一闪一闪地爬着几道小电弧（**身体位置留空**，只画在外圈）。**左右对称**，4 帧循环。",
     EL,
     "CRACKLING ELECTRICITY ON A UNIT, 4 looping frames, " + LR + ", the unit (16 wide, 28 tall) in the middle not drawn: "
     "small jagged cyan-blue arcs 3-5 squares long crawling up its left and right edges at mirrored places, a few white "
     "sparks; the arcs jump to new places each frame; the middle left empty. " + JUNK + ".",
     row(4, 20, 30) + CENTER),
    # ---- W Scrap Shield (in the controller: no animation of its own)
    ("w_shield", "破碎护盾：围着他的废铁护盾，4 帧循环", "view_buffs `league_rumble_w_shield`（跟随，罩着他，z 3；左右对称）", "56 × 42",
     "破碎护盾：**一圈半透明的护盾罩着整个机甲**，罩子的边上转着一圈废铁（黄铜板、螺母、螺丝、钢片），蓝白色的光边一闪一闪"
     "（参考 shield_01_flash、mord_energy_ball、nut、screw）。他走路时也挂着，**中间他的身体位置留空**（只画罩子的边和废铁）。**左右对称**，4 帧循环。",
     BR + ", " + SL + ", " + EL,
     "A SCRAP SHIELD AROUND THE MECH, 4 looping frames, " + LR + ", " + HIM + " (the cell's bottom on the ground): a dome "
     "outline 52 squares wide and 40 tall round him, a thin bright cyan-white rim 1-2 squares wide with a faint blue "
     "glint here and there, and a ring of junk riding on the rim at mirrored places - brass plates, hex nuts, screws, "
     "bent steel sheets, each 2-4 squares; the junk shifts a step round the rim each frame and the rim flickers; the "
     "inside left EMPTY (he shows through). " + JUNK + ".",
     row(4, 56, 42) + CENTER),
    ("haste", "破碎护盾：加速时脚下的尾气，4 帧循环", "view_buffs `league_rumble_haste`（跟随，脚下，z -1；左右对称）", "40 × 10",
     "护盾带的加速：机甲脚下两边喷出一股股灰白的尾气和几粒火星，像引擎全开。**左右对称**，4 帧循环。",
     ST + ", " + SM + ", " + FI,
     "EXHAUST PUFFS AT THE FEET, 4 looping frames, " + LR + ", " + FEET + ", the middle 20 squares left empty: puffs of "
     "white-grey exhaust 4-6 squares rolling out to both sides along the ground, a few orange sparks; the puffs roll "
     "outward a step each frame. " + JUNK + ".",
     row(4, 40, 10) + CENTER),
    # ---- passive: heat, the Danger Zone, Overheat
    ("dz_on", "危险地带：热量过半那一下，5 帧", "view_effects `league_rumble_dz_on`（跟随他，z 3；左右对称）", "40 × 40",
     "进入危险地带（热量 50 以上）：机甲两边猛地喷出两股白色蒸汽，一圈橙红色的热浪闪一下（参考 color-hex_steam、smoke_02、distort-heat）。"
     "**他的身体位置留空**。**左右对称**，5 帧。",
     ST + ", " + FI,
     "STEAM VENTING, 5 frames, " + LR + ", " + HIM + " (the cell's bottom on the ground): 1 an orange-red heat flash ring "
     "30 across round his middle (only the ring); 2 two jets of white steam bursting out sideways from his shoulders at "
     "mirrored places, 8 squares long; 3 the jets 14 long, rolling up; 4 the steam clouds rising and spreading; 5 wisps "
     "fading. The middle 24 squares left empty. " + JUNK + ".",
     row(5, 40, 40) + CENTER),
    ("dz_steam", "危险地带：热着的时候冒的蒸汽，4 帧循环", "view_buffs `league_rumble_dz_steam`（跟随，头上，z 3；左右对称）", "36 × 16",
     "在危险地带里：机甲肩膀两边一缕缕往上冒白色蒸汽和热气（格子底边贴着他的肩膀）。**左右对称**，4 帧循环。",
     ST,
     "STEAM RISING FROM A HOT MECH, 4 looping frames, " + LR + ": two thin columns of white steam puffs at mirrored places "
     "26 squares apart, rising from the cell's bottom (his shoulders) 12 squares up and curling outward; the puffs climb "
     "a step each frame. " + JUNK + ".",
     row(4, 36, 16) + CENTER),
    ("oh_on", "过热：炸出一团火和黑烟，6 帧", "view_effects `league_rumble_oh_on`（大表，跟随他，z 3；左右对称）", "56 × 50",
     "过热（热量满了）：机甲身上**轰地炸出一大团火和黑烟**，往上冲、往两边翻，火星四溅，几块废铁片弹飞（参考 overheat_plasma、poof_soot2、"
     "charred_billow、infernalguardian）。**他的身体位置大致留空**（火从他背后、两边冒）。**左右对称**，6 帧。",
     FI + ", " + SM,
     "AN OVERHEAT BLOWOUT, 6 frames, " + LR + ", " + HIM + " (the cell's bottom on the ground): 1 a white-yellow flash "
     "behind his top 14 across; 2 a fireball bursting up 24 across above and round him, flames licking out to both sides; "
     "3 the fire 40 across, thick black smoke rolling up from it, sparks and a few small steel shards flying out at "
     "mirrored places; 4 the smoke billowing 48 across, the fire inside it dying; 5 a black smoke cloud with embers; 6 "
     "smoke thinning. His body (the middle 24 squares wide, 30 tall) never covered by solid fire. " + JUNK + ".",
     row(6, 56, 50) + CENTER),
    ("oh_smoke", "过热中：冒黑烟着火，4 帧循环", "view_buffs `league_rumble_oh_smoke`（跟随，头上，z 3；左右对称）", "36 × 22",
     "过热的几秒里：机甲肩膀两边窜着小火苗、往上冒滚滚黑烟（格子底边贴着他的肩膀）。**左右对称**，4 帧循环。",
     FI + ", " + SM,
     "AN OVERHEATED MECH SMOKING, 4 looping frames, " + LR + ": at mirrored places 26 squares apart on the cell's bottom "
     "(his shoulders), small orange flames 4 squares tall and above them thick black smoke curling 16 squares up; the "
     "smoke rolls up a step each frame, embers drifting. " + JUNK + ".",
     row(4, 36, 22) + CENTER),
    # ---- ult: R The Equalizer
    ("r_launch", "恒温灼烧：背上的火箭一齐打出去，5 帧", "view_effects `league_rumble_r_launch`（大表，跟随他，z 3；左右对称）", "36 × 60",
     "发射火箭：机甲背后猛地一亮，**几枚火箭拖着火焰和白烟笔直往上飞出格子**，下面留一团硝烟（参考 r_burn_rocket、r_rockettrail、"
     "r_rocketsmoke）。**他的身体位置留空**。**左右对称**，5 帧。",
     FI + ", " + SM + ", " + ST + ", " + SL,
     "ROCKETS LAUNCHING STRAIGHT UP from behind him, 5 frames, " + LR + ", " + HIM + " at the bottom of the cell: 1 a "
     "white-orange flash 14 across just above his head; 2 three small rockets (steel bodies, red tips, 2 wide and 5 tall) "
     "leaving it straight up at mirrored places (one in the middle, two 8 squares to the sides), each with a white-yellow "
     "flame under it; 3 the rockets 20 squares higher, each trailing fire and a white smoke column; 4 the rockets at the "
     "top edge, the smoke columns to the cell's top; 5 the rockets gone, the smoke columns and a puff of smoke over him "
     "drifting. " + JUNK + ".",
     row(5, 36, 60) + CENTER),
    ("r_fall", "恒温灼烧：火箭落地烧一片，10 帧", "view_effects `league_rumble_r_fall`（大表，地上，z -1，不跟随；左右对称；"
     "长度 = 火区的时间）", "24 × 40",
     "一枚火箭从天上**笔直扎下来**、落地爆炸，然后地上**烧着一块火**（几块连成一条火线），烧一会儿后熄成火星（参考 r_impactcrater、"
     "r_impactflasha、r_burn_sparks、r_dirt_rock）。**左右对称**，10 帧（5–8 帧是火在地上烧，可以循环）。",
     FI + ", " + SM + ", " + SL,
     "A ROCKET STRIKE AND A BURNING PATCH, 10 frames, " + LR + ", the ground patch " + FEET + " at the bottom of the cell, "
     "about 20 squares wide and 7 tall: 1 a small steel rocket with a red tip pointing straight DOWN near the top middle, "
     "a fire trail above it; 2 the rocket just above the ground; 3 a white-yellow impact flash 12 across on the ground; 4 "
     "an orange blast 20 across, clods of dirt flying out to both sides; 5-8 a patch of burning ground 20 wide: orange "
     "flames 4-7 squares tall dancing on a dark scorched ellipse, the tongues changing a step each frame (5-8 loop); 9 "
     "the flames low, black smoke; 10 embers on the scorched ground. " + JUNK + ".",
     row(10, 24, 40) + CENTER),
    ("burn", "恒温灼烧：被烧的人脚下，4 帧循环", "view_buffs `league_rumble_burn`（跟随，脚下，z -1；左右对称）", "18 × 8",
     "被火区烧到、减速的敌人脚下：一圈小火苗烧着脚。**左右对称**，4 帧循环。",
     FI,
     "FLAMES LICKING AT THE FEET, 4 looping frames, " + LR + ", " + FEET + ": a band of small orange flames 16 squares "
     "wide and 3-5 squares tall, the middle a little lower; the tongues change a step each frame, mirrored. " + JUNK + ".",
     row(4, 18, 8) + CENTER),
]
BIG_FX = ["oh_on", "r_launch", "r_fall"]
FLYING = ["e_harpoon"]
FORWARD = ["q_flame"]
OWN_FX = {"q_flame": "skill"}     # drawn into his own frames by tools/art/rig_rumble.py at the cannon's muzzle

GROUPS = [
    ("a_hit oh_hit (the ball)", ["rumble_hiteffect", "rumble_sharp_flash_02", "rumble_metal_shards_03",
                                 "rumble_fireball_hit"]),
    ("q_flame q_hit (Flamespitter)", ["flames_flamethrower", "color-flamethrower", "rumble_flames02", "rumble_flames03"]),
    ("e_harpoon (the harpoon)", ["rumble_base_taze_mis_electric",
                                 "rumble_base_taze_mis_trail", "rumble_lightning05"]),
    ("e_hit e2_hit e_zap", ["rumble_base_taze_tar_plasma", "rumble_base_taze_tar_sphere", "rumble_blue_rings_01",
                            "rumble_flare-rainbow_blue_04"]),
    ("w_shield haste (Scrap Shield)", ["rumble_base_shield_01_flash", "rumble_mord_energy_ball_03", "nut_05",
                                       "screw_08", "rumble_smokepuffs"]),
    ("dz_on dz_steam (Danger Zone)", ["color-hex_steam", "rumble_smoke_02", "rumble_distort-heat", "rumble_orange-light"]),
    ("oh_on oh_smoke (Overheat)", ["rumble_base_overheat_plasma", "rumble_poof_soot2", "charred_billow_03",
                                   "rumble_infernalguardian02"]),
    ("r_launch (the rockets)", ["rumble_base_r_burn_rocket", "rumble_base_r_rockettrail", "rumble_base_r_rocketsmoke",
                                "rumble_base_r_rockettrailsmokey"]),
    ("r_fall burn (the fire line)", ["rumble_base_r_impactcrater", "rumble_base_r_impactflasha",
                                     "rumble_base_r_burn_sparks_01", "rumble_base_r_dirt_rock"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", k=1 / PPU):
    """A design at game size (k of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Rumble at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"兰博 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The approved idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 机械公敌 兰博：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/rumble_design.png`：Q 版蓝毛约德尔人坐在黄铜色的废铁机甲里——亮蓝莫西干、"
      "红镜片护目镜、坏笑；往前伸的长喷火炮管、后面那只机械手握着带刺铁球、背上两个红头火箭舱、短腿和红色圆盘脚）。"
      f"兰博在游戏里是**高清**的（每个游戏格子里 1.75×1.75 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/rumble_size.png`：兰博缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里兰博自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "**兰博是约德尔人的废铁机甲**，特效都是**机械和火**：喷火炮的**橙黄火焰**、**黑烟**、过热的**白色蒸汽**、鱼叉的**蓝白电弧**、"
      "护盾的**黄铜和钢铁废料**；不要魔法符文，也不要光滑的霓虹光束。")
    a("> - **特效要亮**：每道火、每道电都有最亮一档或白色的高光，暗底上一眼能看见。")
    a("> - **火、电、烟、蒸汽没有黑描边**（用它自己最深的一档）；**只有火箭、鱼叉、废铁片这些“东西”有 1 格近黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人（`w_shield`、`dz_on`、`oh_on`、`r_launch` 罩着兰博自己）。")
    a("> - **对称**：所有不飞的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。"
      "**弹道**（`" + "`、`".join(FLYING) + "`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。"
      "**`q_flame` 例外**：它画进兰博自己的动作帧里、跟着他一起翻，所以**朝右、不用对称**。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `rumble_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、"
      f"对称方式）和生图原稿 `raw/`，都放在 `outputs/rumble_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 | 抡带刺铁球砸；过热时每一击都着火 | `a_hit` · `oh_hit` |")
    a("| 被动「废品巨像」（热量） | 放技能攒热量；热量过半进危险地带（技能加强、冒蒸汽）；热量满了过热（几秒不能放技能，普攻着火、冒黑烟） | "
      "`dz_on` · `dz_steam` · `oh_on` · `oh_smoke` |")
    a("| 技能 1 =「纵火盛宴」 | 喷火炮往前喷一大股火，烧锥形范围里的人 | `q_flame` · `q_hit` |")
    a("| 破碎护盾（W，并入被动） | 附近有敌方英雄时自动套上废铁护盾，加一点移速 | `w_shield` · `haste` |")
    a("| 技能 2 =「电子鱼叉」 | 射鱼叉：伤害、减速；打中英雄后再射第二发（更痛、减速更多） | `e_harpoon` · `e_hit` · `e2_hit` · `e_zap` |")
    a("| 大招 =「恒温灼烧」 | 背上的火箭一齐打出去，沿一条线落下，地上烧出一条火线，烧到的人减速 | `r_launch` · `r_fall` · `burn` |\n")
    a("连招：**鱼叉打中英雄 → 第二发鱼叉**，**第二发打中 → 马上喷火**，**火箭落地 → 马上射鱼叉**，**进危险地带 → 马上套护盾**。\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、电、烟、蒸汽没有黑描边，也不要用最深的颜色给形状描一圈边**（火箭、鱼叉、废铁片除外）。")
    a("- **都是废铁机甲**：火、烟、蒸汽、电、黄铜和钢；每个形状 2–3 档平涂。")
    a("- **要亮**：每个形状都有最亮一档或白色的高光。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("火", FIRE), ("烟·煤灰", SMOKE), ("电", ELEC), ("蒸汽", STEAM), ("黄铜", BRASS), ("钢", STEEL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈（火区、尾气）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `rumble_fx_{name}.png`：{title}\n")
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
        a(f"| `rumble_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_rumble_fx`（小的）和 `league_rumble_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_rumble.py 的 views；w_shown → w_shield、w_ms → haste、dz → dz_steam、oh → oh_smoke、e_slow → e_zap、r_slow → burn）。"
      "r_fall 的 tag 和火区一样长（r_t），5–8 帧循环填满。")
    a("- 画进动作帧的 " + "、".join(f"`{k}`（{v}）" for k, v in OWN_FX.items()) +
      "：rig_rumble.py 把它贴在 q_spray 的炮口（炮管方向），帧按 q_t 循环。")
    a(f"- 弹道（{'、'.join(FLYING)}）断言上下对称；{'、'.join(FORWARD)} 不断言；其余断言左右对称。")
    a("- 用 `pixel_1x/` 切格（import_ivern_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="rumble_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_rumble.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "rumble_design.png"))
    shape = size_sheet(os.path.join(out, "design", "rumble_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"rumble_fx_{x[0]}.png", "binding": x[2], "size": x[3],
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
