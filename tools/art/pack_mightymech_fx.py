#!/usr/bin/env python3
"""Build mightymech_fx_pack.zip: step 3 of the Mighty Mech's sprite - Codex draws its effects and its three skill icons
(the tft heroes' way).

    python tools/lol/fx_ref_mightymech.py            # the particle references -> C:/t/mm_work/fxref
    python tools/art/pack_mightymech_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name mightymech_fx_redo_pack]

The pack (C:/t/mm_work/fx/mightymech_fx_pack, zipped into --out, default D:/TFM2-Workshop/mightymech_packs) holds
PROMPTS.md (also written to assets/source/mightymech/PROMPTS_FX.md), design/mightymech_design.png (the approved idle at
4x on its own squares), design/mightymech_size.png (it at game size, 4x, on the arena colour with the ground line, a
10-px ruler and the base fighter) and refs/tft_fx_ref.png (its own set-17 and set-15 particle textures - grey shapes the
game tints, grouped by the effect they inform). The effects are the views the kit binds (the user's pick 2026-11-03:
support, plan A; the look B, the giant sword always in hand): view_effects a_hit, a_crush, q_taunt, q_wave, q_hit,
e_slam, e_up, r_transform, r_sword, r_hit; view_projectiles r_slash; view_buffs a_slow, q_stance, r_form, p_shield.
Plus the three skill icons.
Its colours: its blade-wing red, the sword core's orange-gold, its silver steel, Gravity Matrix's violet (TFT set 17's
space gods: a gravity field), dust.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the slash wave r_slash is symmetric top to bottom, pointing right (it lies along the cast line).
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

TMP = "C:/t/mm_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "mightymech", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "mightymech", "hd")
NAME = "mightymech_fx_pack"
PPU = 2.0

RED = "#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A"            # its blade-wings, the slashes
CORE = "#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A"           # the sword's core, the Ultimate form, the shields
STEEL = "#F4F7FA, #C9D2DC, #8D99A8, #56606E"                   # its silver steel, shards
GRAV = "#F0E9FF, #B9A4FF, #7B62F0, #4A36B8, #261B6E"           # Gravity Matrix (a set-17 space-gods gravity field)
DUST = "#ECE6DA, #B8AE9E, #7E7466, #4A433B"                    # dust and rubble
RD = f"a mecha red ramp ({RED})"
CO = f"an orange-gold core ramp ({CORE})"
ST = f"a silver steel ramp ({STEEL})"
GR = f"a gravity violet ramp ({GRAV})"
DU = f"a dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with the cast; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword "
         "with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, "
         "clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity "
         "rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke")
HIM = ("the mech stands in the middle, not drawn: about 47 squares wide and 40 tall, crouched, its blade-wings fanned "
       "behind it, its giant sword held forward")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark steel frame with small red "
        "chevron corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「活塞重斩」：剑砍中，3 帧", "view_effects `tft_mightymech_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "巨剑砍中：**一道竖着的白芯红色刀光**从上往下一闪，两边溅几粒银色火花。**左右对称**，3 帧（要快）。",
     RD + ", " + ST,
     "A SWORD CUT, 3 frames, " + LR + ": 1 a thin vertical white-red slash line 12 squares tall in the middle; 2 the "
     "slash 3 squares wide, white core with red edges, a few silver chevron sparks flying out to both sides (mirrored); "
     "3 the slash fading to dark red, the last sparks. Small and quick. " + MAGIC + ".",
     row(3, 14, 14) + CENTER),
    ("a_crush", "普攻：每第三下「活塞重斩」砸中，4 帧", "view_effects `tft_mightymech_a_crush`（跟随目标，z 2；左右对称）", "24 × 22",
     "每第三下活塞推着剑重重砸下：**一道更粗的竖刀光 + 橙金色的冲击闪光**炸开，两边各一小股白色**活塞蒸汽**喷出，银色碎片往两边飞。"
     "**左右对称**，4 帧。",
     RD + ", " + CO + ", " + ST,
     "A HEAVY PISTON CHOP, 4 frames, " + LR + ": 1 a thick vertical white-red slash 18 squares tall; 2 an orange-gold "
     "IMPACT FLASH 14 squares across where it lands (bottom middle), a white core, two short white STEAM jets bursting "
     "out sideways (mirrored); 3 a red-orange burst ring 20 squares across, silver shards flying out to both sides, the "
     "steam spreading; 4 the last embers and steam. " + MAGIC + ".",
     row(4, 24, 22) + CENTER),
    ("a_slow", "普攻第三下：减速，6 帧循环", "view_buffs `tft_mightymech_a_slow`（跟随被减速的人，脚下，z 3；左右对称）", "24 × 8",
     "被重斩减速的人：脚边**几道红色的小裂痕电光**一闪一闪，一点银色碎屑。很淡、只在脚下。**左右对称**，6 帧循环。",
     RD + ", " + ST,
     "A CRACKLE AT THE FEET, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): on EACH side "
     "(mirrored) two tiny red energy cracks (2-3 square zigzags on the ground line) and one silver speck; frames 1-6 the "
     "cracks flickering on and off in new spots (every frame left-right symmetric). Subtle. " + MAGIC + ".",
     row(6, 24, 8) + CENTER),
    ("q_stance", "技能「引力矩阵」：引力罩，6 帧循环", "view_buffs `tft_mightymech_q_stance`（大表，跟随超级机甲，z 3；左右对称）",
     "64 × 52",
     "它张开刃翼进入防御姿态：身子外面**一圈紫色的引力罩**（横着的椭圆，只画外圈：一圈由**小六边形**拼成的紫色格子，边缘奶白），"
     "罩子外面几道**往里吸的紫色弧线**（像把东西吸过来）。**里面它的身体位置留空**。**左右对称**，6 帧循环。",
     GR,
     "A GRAVITY FIELD, 6 looping frames, " + LR + ": round " + HIM + ": a ring of small HEXAGON cells (an ellipse 60 "
     "squares wide and 48 tall, only its 3-square rim drawn, hexagons 4 squares across with thin bright edges), gravity "
     "violet with pale white edges; outside the ring on each side (mirrored) two short curved violet arcs pointing INWARD "
     "(things being pulled in); frames 1-6 the arcs sliding inward toward the ring and a few hexagons lighting up white in "
     "turn (mirrored pairs; every frame left-right symmetric). INSIDE the ring stays EMPTY (its body). " + MAGIC + ".",
     row(6, 64, 52) + CENTER),
    ("q_taunt", "技能「引力矩阵」：被吸住（嘲讽），4 帧", "view_effects `tft_mightymech_q_taunt`（跟随被嘲讽的人，头上，z 3；左右对称）",
     "16 × 12",
     "被引力吸住、只能打它的人：头顶**一个紫色的小引力漩涡**（两三圈椭圆弧），一个小小的红色感叹号形状在中间亮一下。"
     "**左右对称**，4 帧。",
     GR + ", " + RD,
     "A GRAVITY MARK ABOVE A HEAD, 4 frames, " + LR + ": above a unit's head (the unit not drawn, the bottom of the cell is "
     "the top of its head): 1 a small violet ellipse ring 8 squares wide; 2 two nested violet ellipse rings 14 squares wide, "
     "a small red exclamation mark (2 squares wide, 5 tall) flashing in the middle; 3 the rings tightening inward, the mark "
     "bright; 4 the rings fading. " + MAGIC + ".",
     row(4, 16, 12) + CENTER),
    ("q_wave", "技能「引力矩阵」结束：冲击波，6 帧", "view_effects `tft_mightymech_q_wave`（大表，放在它脚下的地面上，不跟随，z -1；左右对称）",
     "90 × 30",
     "防御结束时释放的冲击波：**一圈紫色加奶白的冲击环贴着地面往外推开**（半径两格），环上带着小六边形碎片和银色碎屑。"
     "**只在地面和低处**。**左右对称**，6 帧。",
     GR + ", " + ST,
     "A GROUND SHOCKWAVE, 6 frames, " + LR + ": on the GROUND seen from above at an angle (ellipses 3 times as wide as "
     "tall): 1 a bright white-violet flash ellipse 20 squares wide in the middle; 2 a thick violet SHOCKWAVE RING 44 "
     "squares wide with a white leading edge; 3 the ring 66 squares wide, small hexagon fragments and silver specks flying "
     "off it low to both sides (mirrored); 4 the ring 82 squares wide, thinning; 5 the ring at the cell's edge, broken into "
     "arcs; 6 the last faint arcs. " + MAGIC + ".",
     row(6, 90, 30) + CENTER),
    ("q_hit", "技能「引力矩阵」：被冲击波打中，3 帧", "view_effects `tft_mightymech_q_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "被冲击波打中的人：**一下紫白色的冲击闪光**，几道紫色短线往外炸开。**左右对称**，3 帧。",
     GR,
     "A GRAVITY IMPACT, 3 frames, " + LR + ": 1 a white-violet flash 6 squares across; 2 a violet burst 14 squares across "
     "with a white core and six short straight rays (mirrored); 3 the rays fading, small violet sparks. " + MAGIC + ".",
     row(3, 16, 16) + CENTER),
    ("e_slam", "技能 2「机甲飞跃」：落地砸出的坑，6 帧", "view_effects `tft_mightymech_e_slam`（大表，放在落点的地面上，不跟随，z -1；左右对称）",
     "60 × 24",
     "它从天上砸下来：落点**一下橙金色的冲击闪光**，地上**裂开一圈放射状的红色裂纹**，**灰土和碎石往两边低低溅起**，最后剩一点尘土。"
     "**只在地面和低处**。**左右对称**，6 帧。",
     CO + ", " + RD + ", " + DU,
     "A LANDING SLAM, 6 frames, " + LR + ": on the GROUND seen from above at an angle: 1 a bright white-gold flash ellipse "
     "18 squares wide in the middle; 2 an orange-gold impact ring 34 squares wide, red glowing CRACKS radiating out on the "
     "ground (mirrored); 3 dust and small rocks bursting out low to both sides (mirrored), the ring 50 squares wide; 4 the "
     "dust rolling outward, the cracks dimming to dark red; 5 the dust thinning; 6 the last dust and faint cracks. "
     + MAGIC + ".",
     row(6, 60, 24) + CENTER),
    ("e_up", "技能 2「机甲飞跃」：被击飞，4 帧", "view_effects `tft_mightymech_e_up`（跟随被击飞的人，z 3；左右对称）", "16 × 20",
     "被击飞的人：身子两边**几道往上的白色速度线**和几块小碎石往上飞。**身体位置留空**。**左右对称**，4 帧。",
     ST + ", " + DU,
     "A KNOCK-UP, 4 frames, " + LR + ": round a small unit (not drawn) in the middle: on EACH side (mirrored) two straight "
     "white-silver SPEED LINES pointing up (1 square wide, 6-10 long) and two small rocks flying up; frames 1-4 the lines "
     "rising and fading, the rocks higher; the middle stays EMPTY. " + MAGIC + ".",
     row(4, 16, 20) + CENTER),
    ("r_transform", "大招「究极变形」：变形闪光，6 帧", "view_effects `tft_mightymech_r_transform`（大表，跟随超级机甲，z 3；左右对称）",
     "70 × 56",
     "它变形成究极形态：身后**一圈放射状的红色光芒**一下炸开（像刃翼的形状一片片射出去），中间一圈**橙金色的光环**，"
     "几颗**菱形的金色亮星**闪一下。**光都在它身后和四周，身体位置留空**。**左右对称**，6 帧。",
     RD + ", " + CO,
     "A MECHA TRANSFORMATION FLARE, 6 frames, " + LR + ": round " + HIM + ": 1 a white-gold flash ring 30 squares across "
     "behind it; 2 long straight RED LIGHT BLADES bursting out radially behind it like a fan (12 blades, mirrored), an "
     "orange-gold halo ring 44 squares across; 3 the blades at full length to the cell's edges, four gold DIAMOND STARS "
     "flashing at the corners (mirrored); 4 the blades thinning, the halo widening; 5 the blades fading to dark red, small "
     "gold sparks; 6 the last sparks. The middle stays EMPTY (its body). " + MAGIC + ".",
     row(6, 70, 56) + CENTER),
    ("r_sword", "大招「超级战刃」：剑核爆燃，6 帧", "view_effects `tft_mightymech_r_sword`（大表，跟随超级机甲，z 3；左右对称）",
     "56 × 56",
     "剑的橙色核心爆燃、剑刃变长之前的蓄力：**橙金色的能量粒子从四周往它身上（中间偏下）汇聚**，身后**一道橙金色的光柱**往上冲。"
     "**身体位置留空**。**左右对称**，6 帧。",
     CO + ", " + RD,
     "A SUPER BLADE CHARGE, 6 frames, " + LR + ": round " + HIM + ": 1 small orange-gold sparks appearing at the cell's "
     "edges on both sides (mirrored); 2 the sparks streaming INWARD toward the middle along straight lines; 3 a tall "
     "orange-gold LIGHT PILLAR rising behind it (10 squares wide, the full height of the cell, white core), the sparks "
     "nearer; 4 the pillar at its brightest, the sparks gathered in a ring 30 squares across at mid height; 5 a flash of "
     "white-gold at the middle, the pillar thinning; 6 the last gold sparks. The middle stays EMPTY (its body). "
     + MAGIC + ".",
     row(6, 56, 56) + CENTER),
    ("r_slash", "大招「超级战刃」：一剑劈出的剑气，4 帧", "view_projectiles `tft_mightymech_r_slash`（大表，直线范围，贴着地面沿出手方向；上下对称、朝右）",
     "80 × 18",
     "巨剑往前劈出的剑气：**一道长长的红色月牙形剑气贴着地面往右扫出去**，白芯、橙金色的边，后面拖着红色的速度线。"
     "**上下对称、朝右**，4 帧。",
     RD + ", " + CO,
     "A SWORD WAVE, 4 frames, " + TB + ": a long energy blade wave across the cell: 1 a short bright white-red crescent "
     "(its curve bulging to the right) at the left third of the cell; 2 the crescent 14 squares tall at the middle, white "
     "core, orange-gold edge, straight red speed lines trailing behind it to the left (mirrored top and bottom); 3 the "
     "crescent at the right part of the cell, the trail the whole length; 4 the crescent leaving the right edge, the trail "
     "fading. " + MAGIC + ".",
     row(4, 80, 18) + CENTER),
    ("r_hit", "大招「超级战刃」：被剑气砍中，4 帧", "view_effects `tft_mightymech_r_hit`（跟随目标，z 2；左右对称）", "22 × 22",
     "被剑气砍中的人：**一个红色的大 X 形十字刀光**一闪，中间橙金色的闪光，银色碎片往外飞。**左右对称**，4 帧。",
     RD + ", " + CO + ", " + ST,
     "A BIG CROSS SLASH, 4 frames, " + LR + ": 1 two thin white-red slash lines crossing in an X, 18 squares across; 2 the "
     "X 3 squares thick, white core, red edges, an orange-gold flash at the crossing; 3 silver shards flying out from the "
     "middle to both sides (mirrored), the X fading to dark red; 4 the last shards. " + MAGIC + ".",
     row(4, 22, 22) + CENTER),
    ("r_form", "大招：究极形态的余光，6 帧循环", "view_buffs `tft_mightymech_r_form`（跟随超级机甲，z 1；左右对称）", "52 × 44",
     "究极形态持续的那几秒：身子两边**几粒橙金色的小火光往上飘**，偶尔一道很细的红色光线一闪。很淡。**身体位置留空**。**左右对称**，6 帧循环。",
     CO + ", " + RD,
     "AN ULTIMATE-FORM GLOW, 6 looping frames, " + LR + ": round " + HIM + ": on EACH side (mirrored) three small "
     "orange-gold embers (1-2 squares) drifting upward along its flanks, and one thin red light line flickering; frames "
     "1-6 the embers rising and reappearing at the bottom (every frame left-right symmetric). Subtle. The middle stays "
     "EMPTY (its body). " + MAGIC + ".",
     row(6, 52, 44) + CENTER),
    ("p_shield", "被动「旅人护航」：护盾，6 帧循环", "view_buffs `tft_mightymech_p_shield`（跟随被护盾的人，z 3；左右对称）", "24 × 36",
     "被动给自己和队友的护盾：人外面**一圈很薄的橙金色护盾外框**（竖着的椭圆，只画外圈，边上几个小菱形），一道亮光沿着外框往上扫。"
     "**身体位置留空**。**左右对称**，6 帧循环。",
     CO,
     "A VOYAGER SHIELD, 6 looping frames, " + LR + ": round " + CHAMP + ": a thin orange-gold shield outline (an upright "
     "ellipse 22 squares wide and 34 tall, only its 2-square rim drawn, pale gold with a white outer edge), four small gold "
     "DIAMOND studs on it (mirrored pairs); frames 1-6 a bright white-gold glint sweeping up both sides of the rim "
     "(mirrored; every frame left-right symmetric). INSIDE stays EMPTY. " + MAGIC + ".",
     row(6, 24, 36) + CENTER),
]
ICONS = [
    ("skill", "技能「引力矩阵」图标", "skill_icons[0] `asset/tft/icons/tft_mightymech_skill`",
     ICON + ": a ring of small violet hexagons forming a dome, red blade-wing shapes spread round it, violet arcs "
               "curving inward toward its centre, a bright white-violet core."),
    ("skill2", "技能 2「机甲飞跃」图标", "skill_icons[1] `asset/tft/icons/tft_mightymech_skill2`",
     ICON + ": a red mecha silhouette with spread blade-wings diving down at the lower right, its sword pointing down, "
               "an orange-gold impact burst and red ground cracks under it, white speed lines above."),
    ("ult", "大招「究极变形·超级战刃」图标", "skill_icons[2] `asset/tft/icons/tft_mightymech_ult`",
     ICON + ": a giant red-and-silver sword drawn diagonally from the lower left to the upper right, its round orange "
               "core blazing white-gold in the middle, a red crescent energy wave sweeping off its blade, gold diamond "
               "sparks."),
]
BIG_FX = ["q_stance", "q_wave", "e_slam", "r_transform", "r_sword", "r_slash"]
FLYING = ("r_slash",)

GROUPS = [
    ("a_hit a_crush (the sword)",
     ["tft15_galio_base_ba_swipe_white_tip_01", "tft15_galio_base_ba_trail", "tft15_galio_base_hit07",
      "tft15_galio_base_z_slash_1", "tft17_galio_base_impactflasha_2"]),
    ("q_stance q_taunt (Gravity Matrix)",
     ["tft17_galio_base_shield_mult", "tft17_galio_base_shield_mult_01", "tft15_galio_base_w_hexagon_1",
      "tft17_galio_base_electric", "tft17_galio_base_ring_02"]),
    ("q_wave q_hit e_slam (the shockwaves)",
     ["tft17_galio_base_ring_03", "tft17_galio_base_slicering", "galio_skin19_ring_shockwave_2", "tft17_galio_base_rock23",
      "tft15_galio_base_w_groundswipe_02"]),
    ("r_transform r_sword r_form (the Ultimate form)",
     ["tft15_galio_base_r_glow", "tft15_galio_base_r_sparks_gold", "tft15_galio_base_r_diamond",
      "tft15_galio_base_r_animeshapes02", "tft15_galio_base_rainbowhalo"]),
    ("r_slash r_hit e_up p_shield",
     ["tft15_galio_base_slashult", "tft15_galio_base_w_slash_core_color", "tft15_galio_base_wind_horizontal",
      "tft15_galio_base_w_shield", "tft17_galio_base_flamehead02"]),
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
    """T-Hex at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"超级机甲 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape, icons=True):
    h, w = shape[:2]
    L = []
    a = L.append
    n_ic = len(ICONS) if icons else 0
    a("# 超级机甲：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/mightymech_design.png`："
      "3/4 朝右、红银黑三色的超级机器人：小红头盔、银色 V 形角、黄色眼罩；宽厚的红色胸甲、银色星形大护肩；背后扇形红色刃翼；"
      "双手握着一把比身体还长的红银巨剑，剑格中间一颗橙色发光圆核）。"
      f"超级机甲在游戏里是**高清**的（每个游戏格子里约 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/mightymech_size.png`：超级机甲缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是超级机甲自己的特效贴图（金铲铲第 17 季的引力矩阵、冲击环、变形，第 15 季机甲的剑光、剑击、护盾、金色火花）"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **超级机甲是巨型机器人，特效都是机甲动画的味道**：干脆的直线速度线、硬朗的菱形和箭头状火花、白芯的**红色**刀光、剑核的**橙金色**光、"
      "银色金属碎片；只有引力矩阵（`q_*`）用**紫色**引力；不要绿色、不要树叶、不要烟火。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了贴着地面扫出去的剑气 `r_slash`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `mightymech_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `mightymech_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「旅人护航」 | 每条命开打时给自己和血最少的队友上护盾（自己双倍） | `p_shield` |")
    a("| 普攻「活塞重斩」 | 巨剑砍下；每第三下活塞推着剑重砸，多打一下并减速 | `a_hit` · `a_crush` · `a_slow` |")
    a("| 技能 =「引力矩阵」 | 刃翼张开防御：减伤、把附近敌人吸过来打自己（嘲讽）、回血；结束时一圈冲击波 | "
      "`q_stance` · `q_taunt` · `q_wave` · `q_hit` |")
    a("| 技能 2 =「机甲飞跃」 | 跳到正在冲我方后排的敌人身上砸下：伤害、击飞 | `e_slam` · `e_up` |")
    a("| 大招 =「究极变形·超级战刃」 | 变形（护盾、加双抗），剑核爆燃、剑刃变长，往前劈出一道剑气：伤害、击飞 | "
      "`r_transform` · `r_sword` · `r_slash` · `r_hit` · `r_form` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("机甲红（刃翼、刀光、剑气）", RED), ("橙金（剑核、究极形态、护盾）", CORE), ("银（金属碎片）", STEEL),
                        ("引力紫（只给引力矩阵）", GRAV), ("尘土和碎石", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `mightymech_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `mightymech_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `mightymech_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `mightymech_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_mightymech_fx`（小的）和 `tft_mightymech_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- r_slash 断言上下对称（朝右），其余断言左右对称。")
    a("- q_wave、e_slam 放在地面上（不跟随，z -1）；r_transform、r_sword 跟随它；q_stance、r_form 是它身上的 buff，p_shield 是被护盾的人"
      "身上的 buff（mightymech.rs 挂）；a_slow 是敌人身上的 buff；r_slash 是直线范围（LineRangeProjectile）的画面，贴着地面沿出手方向。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="mightymech_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/mightymech_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_mightymech.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "mightymech_design.png"))
    shape = size_sheet(os.path.join(out, "design", "mightymech_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"mightymech_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"mightymech_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
                   if not a.only else []), f, ensure_ascii=False, indent=1)
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
