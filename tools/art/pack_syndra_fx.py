#!/usr/bin/env python3
"""Build syndra_fx_pack.zip: step 3 of Syndra's sprite - Codex draws her effects (after tools/art/pack_viktor_fx.py).

    python tools/art/pack_syndra_fx.py [--no-zip] [--out DIR] [--only a_bolt,a_hit --name syndra_fx_redo_pack]

The pack (%TEMP%/sy_work/fx/syndra_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/syndra/PROMPTS_FX.md), design/syndra_design.png (8x), design/syndra_size.png (the design at 4x on the
arena colour with the feet line, a 10-px ruler and the base fighter beside her), design/syndra_shots.png (the finished
release frames at 4x from league/champions/league_syndra, with the point each picture starts from) and
refs/lol_fx_ref.png (League's own particle textures for Syndra, grouped by the effect of ours they inform; Riot's art,
local only: it reads %TEMP%/sy_work/fxref, extracted from Syndra.wad.client).
The effects are the views the kit binds (tools/kit/build_syndra.py: view_projectiles a_bolt, w_throw, r_orb, e_wave;
view_effects a_hit, q_form, q_blast, q_hit, orb, w_land, w_hit, e_hit, e_stun, r_cast, r_hit, evo; view_buffs w_slow).
League's colours: the Dark Spheres are near-black violet orbs with a violet glow and a magenta rim, her force and the
wave a bright violet, the hits magenta-white. Light gets no outline. Red side: the flying spheres and the bolt
symmetric top to bottom, the wave drawn in the right half of the cell from its centre (the line's view sits on her,
turned toward the target) and symmetric top to bottom, every picture on a unit, the cast ring and the buff symmetric
left to right, the ground pictures (the forming and resting sphere, the blasts) both ways. Codex also delivers
pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "sy_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "syndra", "PROMPTS_FX.md")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "syndra_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VIOLET = "#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8"            # her force: the wave, the throw's glow, the halo
VOID = "#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430"              # a Dark Sphere's body (dark core, violet glow)
MAGENTA = "#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480"           # the spheres' rims, the hits, the gems
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a "
        "white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are "
        "bright), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
VI = f"a force violet ramp ({VIOLET})"
VO = f"a dark sphere ramp ({VOID})"
MG = f"a magenta ramp ({MAGENTA})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
BOTH = "SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame"
SPHERE = ("a DARK SPHERE: a round orb, its body near-black violet with a darker core, a bright violet glow ring 1 square "
          "thick round it, a thin magenta rim light on its top-left and bottom-right, a tiny white glint")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack
    ("a_bolt", "普攻：飞出去的暗黑小光弹（飞行中，循环），4 帧",
     "view_projectiles `league_syndra_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "8 × 5",
     "辛德拉的普攻：一颗深紫色的小暗黑弹，外面一圈亮紫光，前面一点洋红白芯，后面拖一小段紫色光尾（参考 basatk_core、P_Mis_AnimeShapes、P_trail）。朝右飞。**上下对称**。4 帧无缝循环。约 8 格长、5 格高。",
     f"{VO}, {VI} and {MG}",
     f"a small DARK BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round near-black violet core 3 squares "
     "across at the right with a bright violet glow round it and a 1-square magenta-white glint at its front, a short "
     "tapering violet trail 4 squares long behind it to the left; the trail flickers frame to frame.",
     row(4, 10, 6) + "; the bolt's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_syndra_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "普攻打中：一朵紫色带洋红芯的小星光炸开（参考 HitEffect、darksov_Sparkle）。**左右对称**。约 10 格，居中画。",
     f"{VI} and {MG}",
     f"a DARK SPARK HIT, 4 frames, {LR}: 1 a white-magenta 4-point star 5 squares across; 2 a violet burst 7 squares "
     "across; 3 four violet sparks flying out diagonally; 4 a few fading sparks.",
     row(4, 12, 12) + "; centered in every cell."),
    # ---- Q Dark Sphere
    ("q_form", "Q 暗黑法球成形：落点上法球凝聚（地上，0.5 秒），6 帧",
     "view_effects `league_syndra_q_form`（Q 发出时在落点播放，不旋转，画在人物下面；上下左右都对称）", "40 × 16",
     "Q 的法球在落点凝聚（0.5 秒后砸下）：地上一个从斜上方看的扁椭圆，紫色的暗影从四周往中心旋进来，中心慢慢亮起一个洋红色的光点（参考 Q_Orb_Core、darksov_force、Q_Lightning02）。"
     "这是技能的范围（半径 20 格），约 40 格宽、16 格高。**上下左右都对称**。",
     f"{VI}, {VO} and {MG}",
     f"a DARK SPHERE FORMING on the ground seen from above at an angle, 6 frames, {BOTH}: a thin violet ellipse 38 "
     "squares wide and 14 tall (the area), 1 faint; 2-5 dark violet wisps at mirrored places drawing in from the ellipse "
     "toward the center, the ellipse brighter each frame, a magenta point growing at the center (1, 2, 3, 4 squares); 6 "
     "the ellipse brightest, the center a white-magenta spark.",
     row(6, 42, 18) + "; centered in every cell."),
    ("q_blast", "Q 法球砸下的爆发（地上），5 帧",
     "view_effects `league_syndra_q_blast`（落点上，不旋转，画在人物下面；上下左右都对称）", "40 × 16",
     "法球砸下爆发：中间一下紫白色的闪光，一圈紫色冲击波从中心往外扩到椭圆边缘，地上几道洋红色的裂纹光（参考 2021_Q_Flash_01、2021_Q_Cracks、darksov_blasthole）。**上下左右都对称**。约 40 格宽、16 格高。",
     f"{VI} and {MG}",
     f"a DARK SPHERE IMPACT on the ground seen from above at an angle, 5 frames, {BOTH}: 1 a white-violet flash 12 squares "
     "wide at the center; 2 a violet shockwave ring 24 squares wide with short magenta crack lines at mirrored places; 3 "
     "the ring 34 wide; 4 the ring 40 wide and 16 tall, thinner; 5 fading sparks on the ellipse.",
     row(5, 42, 18) + "; centered in every cell."),
    ("q_hit", "Q 打中（目标身上），4 帧", "view_effects `league_syndra_q_hit`（跟随；左右对称）", "14",
     "Q 打中：一团紫白色的爆光，四周几块深紫色的碎片往外飞（参考 2021_Q_flashPiece_1、Q_ErosionShapes01）。**左右对称**。约 14 格，居中画。",
     f"{VI}, {VO} and {MG}",
     f"a DARK BLAST HIT, 4 frames, {LR}: 1 a white-violet flash 6 squares across; 2 a violet burst 10 squares across with "
     "a magenta core; 3 four dark violet shards flying out diagonally at mirrored places; 4 fading shards and sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("orb", "地上停留的暗黑法球（落点上空，持续 6 秒），12 帧",
     "view_effects `league_syndra_orb`（落点上，不旋转，画在人物上面；左右对称；12 帧共 6 秒）", "16 × 22",
     "法球留在原地 6 秒：一颗悬浮的暗黑法球（球体深紫、外圈亮紫光、洋红色的边光、一点白色高光），离地约 8 格浮着，地上一个扁椭圆的紫色影子（参考 common_darksov_orb_outlines、Q_Orb_Core、justicar_SphereGlow）。"
     "帧 1–2 球出现（从小变大），帧 3–10 球上下浮动 1 格、光圈一明一暗（循环感），帧 11–12 球淡出（变暗、缩小）。**左右对称**。球直径约 10 格，整张约 16 格宽、22 格高。",
     f"{VO}, {VI} and {MG}",
     f"{SPHERE}, 10 squares across, FLOATING above its shadow, 12 frames, {LR}: the shadow a flat violet ellipse 12 "
     "squares wide and 3 tall on the cell's bottom, the orb's bottom 6 squares above it; 1 the orb 4 squares across, "
     "faint; 2 the orb 8 across; 3-10 the full orb rising and sinking 1 square (3-4 up, 5-6 middle, 7-8 down, 9-10 "
     "middle), its glow ring brighter on odd frames; 11 the orb darker and 8 across; 12 a faint 4-square orb and shadow.",
     row(12, 18, 24) + "; centered across, the shadow on the cell's bottom."),
    # ---- W Force of Will
    ("w_throw", "W 掷出的法球（飞行中，循环），4 帧",
     "view_projectiles `league_syndra_w_throw`（抛物线飞行、朝方向转；上下对称）", "12 × 10",
     "W 抓起的法球被掷出去：一颗暗黑法球，外面裹着一层亮紫色的念力光，后面拖一道短的紫色光尾（参考 darksov_forcetrail、darksov_forcebubble）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、10 格高。",
     f"{VO}, {VI} and {MG}",
     f"a THROWN DARK SPHERE flying to the RIGHT, 4 frames, a seamless loop, {TB}: {SPHERE}, 8 squares across at the "
     "right, wrapped in a bright violet force glow, a violet trail 4 squares long behind it; the glow pulses.",
     row(4, 14, 12) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("w_land", "W 法球砸地的冲击（地上），5 帧",
     "view_effects `league_syndra_w_land`（落点上，不旋转，画在人物下面；上下左右都对称）", "44 × 18",
     "W 的法球砸到地上：一圈紫色的念力冲击波往外扩，中心一下洋红白光，地上几道紫色的压痕（参考 darksov_crushwave、W_Circle_normal、W_Void_Background）。"
     "这是技能的范围（半径 21 格），约 44 格宽、18 格高。**上下左右都对称**。",
     f"{VI} and {MG}",
     f"a FORCE SLAM on the ground seen from above at an angle, 5 frames, {BOTH}: 1 a white-magenta flash 10 squares wide; "
     "2 a bright violet ring 24 squares wide with a darker violet dent inside; 3 the ring 36 wide; 4 the ring 44 wide and "
     "18 tall, thinner, violet sparks; 5 fading sparks.",
     row(5, 46, 20) + "; centered in every cell."),
    ("w_hit", "W 打中（目标身上），4 帧", "view_effects `league_syndra_w_hit`（跟随；左右对称）", "14",
     "W 打中：紫色念力的爆光，几道往下压的紫色光线（参考 darksov_force2、darksov_blastflash）。**左右对称**。约 14 格，居中画。",
     f"{VI} and {MG}",
     f"a FORCE HIT, 4 frames, {LR}: 1 a white-violet flash 6 squares across; 2 a violet burst 10 squares across with "
     "short downward streaks at mirrored places; 3 the burst breaking into sparks; 4 fading sparks.",
     row(4, 16, 16) + "; centered in every cell."),
    ("w_slow", "W 减速（被减速的人脚下，循环），4 帧", "view_buffs `league_syndra_w_slow`（画在脚下；左右对称）", "16 × 6",
     "被 W 减速：脚下一圈紫色的细光环，环里有往中间收的短线（左右对称）。**左右对称**。4 帧无缝循环。",
     VI,
     f"a SLOWING RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin violet ellipse 14 squares wide and 4 "
     "tall, 4 short inward ticks at mirrored places that slide toward the center each frame.",
     row(4, 18, 8) + "; centered in every cell."),
    # ---- E Scatter the Weak
    ("e_wave", "E 弱者退散：往前推出去的锥形冲击波（线的画面，朝方向转），5 帧",
     "view_projectiles `league_syndra_e_wave`（线的画面：以辛德拉为中心、朝目标的方向转；**画在格子右半边**；上下对称）",
     "140 × 64",
     "E：从辛德拉身前（格子正中）往右推出一道扇形的紫色冲击波：一道弯弯的弧形波前从中心往右推到 70 格远，越远越宽（扇形张角约 56°，到末端约 64 格高），波前亮紫白色，后面拖着几道紫色的气流和一点洋红碎光（参考 2021_E_Core、2021_E_Lead、2021_E_Edge_2、E_Wisps、DarkSov_W5_Waves）。"
     "**整张图左半边是空的**（游戏把这张图的中心放在辛德拉身上，朝目标转）。**上下对称**。",
     f"{VI} and {MG}",
     f"a CONE SHOCKWAVE pushing to the RIGHT from the cell's CENTER, 5 frames, {TB}: the LEFT HALF of every cell stays "
     "EMPTY; a bright curved wavefront (an arc bulging to the right, white-violet, 2 squares thick) inside a cone opening "
     "from the center to the right (56 degrees wide), violet wisps streaming behind it and a few magenta sparks: 1 the "
     "arc 12 squares right of the center, 14 tall; 2 the arc at 30, 32 tall; 3 the arc at 48, 48 tall, brightest; 4 the "
     "arc at 64, 60 tall, thinner; 5 the arc at 70 fading into sparks.",
     row(5, 144, 66) + "; the cone's tip on the cell's exact center, the cone vertically centered."),
    ("e_hit", "E 打中（被推开的人身上），4 帧", "view_effects `league_syndra_e_hit`（跟随；左右对称）", "12",
     "被 E 推开：人身上一团紫色的冲击光，两边各几道往外的气流线（左右对称）。**左右对称**。约 12 格，居中画。",
     VI,
     f"a PUSH HIT, 4 frames, {LR}: 1 a white-violet flash 6 squares across; 2 a violet burst 10 squares across with short "
     "streaks out to both sides at mirrored places; 3 the streaks longer, fading; 4 a few sparks.",
     row(4, 14, 14) + "; centered in every cell."),
    ("e_stun", "E 法球撞人晕眩（被晕的人身上），8 帧",
     "view_effects `league_syndra_e_stun`（跟随；左右对称；8 帧共约 1.25 秒）", "18 × 30",
     "被推开的法球撞到人：先在人身上炸开一团暗紫色带洋红边的爆光（法球碎掉），然后头顶出现一圈紫色的晕眩小星（左右对称的位置），晃一会儿（参考 2021_R_HitFlash_Core、2021_R_HitFlash_Ring、darksov_Sparkle）。"
     "**左右对称**。下半部分是撞击（人身体的位置），上面是头顶的晕眩星。约 18 格宽、30 格高。",
     f"{VO}, {VI} and {MG}",
     f"a SPHERE CRASH AND STUN on a figure, 8 frames, {LR}: frames 1-3 a burst at the cell's lower middle (the body): 1 "
     "a dark sphere 8 squares across with a magenta rim cracking; 2 a white-magenta flash 12 squares across with dark "
     "violet shards; 3 the shards flying out at mirrored places, fading; frames 4-8 a stun halo at the top of the cell: "
     "a flat violet ellipse 12 squares wide and 4 tall with 4 small white-violet stars on it at mirrored places that "
     "step round the ring each frame (keep each frame mirrored); in 8 the halo fading.",
     row(8, 20, 32) + "; centered across, the burst in the lower half, the halo in the top quarter."),
    # ---- R Unleashed Power
    ("r_cast", "R 能量倾泻：法球聚到她身边（她身上，施法时），6 帧",
     "view_effects `league_syndra_r_cast`（施法时、跟随她，画在人物上面；左右对称）", "56 × 48",
     "R：她身边浮起一圈暗黑法球（7 颗，左右对称地排成一个椭圆，环绕在她周围，中间人站的位置留空），法球一颗颗亮起、往她身边收，最后一下发出去前最亮（参考 darksov_orb_outlines、justicar_SphereGlow、common_Darksov_Blackhole）。"
     "**中间留空**，**左右对称**（逐格对称）。约 56 格宽、48 格高。",
     f"{VO}, {VI} and {MG}",
     f"SEVEN DARK SPHERES round a figure, 6 frames, {LR}, the figure's place in the middle (16 x 36 squares, its bottom on "
     "the cell's bottom) EMPTY: the spheres (each a near-black violet orb 6 squares across with a bright violet glow and "
     "a magenta rim) placed on an ellipse 50 squares wide and 40 tall round the figure at mirrored places (one at the "
     "top center, three on each side); 1 the spheres faint and small (4 across); 2 full size; 3 a violet glow line "
     "linking them; 4 the spheres brighter and 3 squares closer to the figure; 5 brightest, white glints; 6 fading.",
     row(6, 58, 50) + "; centered across, the figure area's bottom on the cell's bottom."),
    ("r_orb", "R 飞向敌人的法球（飞行中，循环），4 帧",
     "view_projectiles `league_syndra_r_orb`（追踪弹、朝方向转；上下对称）", "14 × 10",
     "R 发出的法球：一颗暗黑法球拖着一道紫色彗星尾，尾巴里有洋红色的光点（参考 2021_R_Mis_Core、2021_R_Mis_Lead）。朝右飞。**上下对称**。4 帧无缝循环。约 14 格长、10 格高。",
     f"{VO}, {VI} and {MG}",
     f"a DARK SPHERE MISSILE flying to the RIGHT, 4 frames, a seamless loop, {TB}: {SPHERE}, 8 squares across at the "
     "right, a violet comet tail 6 squares long behind it with magenta sparks in it; the tail flickers.",
     row(4, 16, 12) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_hit", "R 每颗法球打中（目标身上），5 帧", "view_effects `league_syndra_r_hit`（跟随；左右对称）", "18",
     "R 的法球打中：一团暗紫色的爆炸，外圈一道洋红色的光环，中心白光（参考 2021_R_HitFlash_Core、2021_R_HitFlash_Ring、darksov_blastflash）。**左右对称**。约 18 格，居中画。",
     f"{VO}, {VI} and {MG}",
     f"a DARK SPHERE EXPLOSION, 5 frames, {LR}: 1 a white-magenta flash 8 squares across; 2 a dark violet blast 14 "
     "squares across with a bright magenta ring round it; 3 the ring 18 across, dark shards at mirrored places; 4 the ring "
     "thinner, sparks; 5 fading sparks.",
     row(5, 20, 20) + "; centered in every cell."),
    # ---- the passive
    ("evo", "卓尔不凡：技能升级时她身上的暗紫光（她身上），6 帧",
     "view_effects `league_syndra_evo`（施法后，不跟随，画在人物上面；左右对称）", "30 × 44",
     "卓尔不凡升级一个技能：她脚下亮起一圈紫色的光环往上升，几片紫色的水晶碎片往上飘，身边飘起洋红色的小光点（只画外圈和碎片，中间留空）（参考 2021_P_GlassCrystals、P_Flash_sharp、P_GroundLight_01）。**左右对称**。约 30 格宽、44 格高。",
     f"{VI} and {MG}",
     f"a DARK ASCENSION round a figure, 6 frames, {LR}, the figure's place EMPTY: 1 a violet ellipse ring 24 squares wide "
     "and 6 tall at the feet; 2 the ring rising to the waist, small violet crystal shards (2x3 squares) at mirrored places "
     "beside the figure; 3 the ring at the chest, the shards higher, magenta sparks rising; 4 the ring at the head, bright; "
     "5 the ring above the head, fading, shards and sparks; 6 fading sparks.",
     row(6, 32, 46) + "; centered across, the feet ring on the cell's bottom."),
]

GROUPS = [
    ("attack", ["common_darksov_basatk_core", "Syndra_Base_P_Mis_AnimeShapes", "Syndra_Base_P_trail", "common_HitEffect",
                "common_darksov_Sparkle", "common_FlashPurple"]),
    ("Q", ["Syndra_Base_Q_Orb_Core", "Syndra_Base_2021_Q_Cracks", "Syndra_Base_2021_Q_Flash_01", "Syndra_Base_Q_Lightning02",
           "common_darksov_orb_outlines", "common_darksov_blasthole"]),
    ("W", ["common_darksov_force", "common_darksov_forcetrail", "common_darksov_forcebubble", "Syndra_Base_W_Circle_normal",
           "Syndra_Base_W_Void_Background", "common_darksov_crushwave"]),
    ("E", ["Syndra_Base_2021_E_Core", "Syndra_Base_2021_E_Lead", "Syndra_Base_2021_E_Edge_2", "Syndra_Base_E_Beam_Core_Color",
           "Syndra_Base_E_Wisps", "common_DarkSov_W5_Waves"]),
    ("R", ["Syndra_Base_2021_R_Mis_Core", "Syndra_Base_2021_R_Mis_Lead", "Syndra_Base_2021_R_HitFlash_Core",
           "Syndra_Base_2021_R_HitFlash_Ring", "common_darksov_blastflash", "common_Darksov_Blackhole"]),
    ("passive", ["Syndra_Base_2021_P_GlassCrystals", "Syndra_Base_P_Flash_sharp", "Syndra_Base_P_GroundLight_01",
                 "Syndra_Base_Packed_Glows", "common_darksov_dust", "Syndra_Base_P_SoulTrail_01"]),
]
# where the pictures start: (tag, frame, what, marks: "feet" or [(dx, dy) from the standing point, dy from the soles]);
# measured on rig_syndra's release frames (the glove's centre)
SHOTS = [("attack", 3, "a_bolt: 伸出的右手（光弹从这里飞出）", [(6, -24)]),
         ("skill", 3, "Q: 指向落点的手（法球画在落点，不从手上画）", [(6, -24)]),
         ("skill2", 3, "w_throw: 掷出的手（法球从这里飞出）", [(7, -24)]),
         ("skill2_e", 3, "e_wave: 推出的手（冲击波以她为中心往前推）", [(7, -24)]),
         ("ult", 3, "r_orb: 前推的手（法球从这里飞出）", [(6, -26)]),
         ("idle", 1, "r_cast / evo: 站位点", "feet")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Syndra_Base_", "").replace("common_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The design at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside her."""
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
    d.text((8, 36), f"辛德拉 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (league/champions/league_syndra, the imported sheet), each picture's starting
    point as a cyan cross (the standing point is the frame's pivot: the sheet's frames are centred on it)."""
    import tfm2_ase as T
    sp = T.load_sprite(os.path.join(ROOT, "league", "champions", "league_syndra"))
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    PAD = 12                                       # her horns reach the frame's top
    px = sp.w // 2 + PAD
    for tag, k, what, marks in SHOTS:
        f = np.pad(np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA")), ((PAD, PAD), (PAD, PAD), (0, 0)))
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
    a("# 暗黑元首 辛德拉：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/syndra_design.png`，8 倍，{h} 行、{w} 格宽）。")
    a(f"> - 大小对照 `design/syndra_size.png`：定稿造型放大 4 倍，最低的脚尖在红线上，上面是 10 格一段的刻度，右边是原版斗士。辛德拉 {w}×{h} 格。每条写的大小都是游戏像素（格）。")
    a("> - `design/syndra_shots.png`：定稿动作的出手帧（4 倍），青色十字是特效的起点（伸出的右手、脚下），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里辛德拉自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**暗黑法球是近黑的深紫色球体、外面一圈亮紫色光、洋红色的边光；她的念力、推波是亮紫色；打中是洋红白色**。")
    a("> - **特效要亮**：法球的球体可以暗，但外圈的光、边光和高光要亮，暗底上一眼能看见；其他光、波、火花都用最亮的几档和白色的芯。")
    a("> - **围着人的法球圈、晕眩、升级光只画外圈和两边，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的光弹和法球（`a_bolt`、`w_throw`、`r_orb`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "推波 `e_wave` 是**线的画面**：游戏把整张图的**中心**放在辛德拉身上、朝目标的方向转，所以**冲击波只画在格子右半边、从正中间往右推**，同样**上下对称**。"
      "画在人身上、脚下的（打中、晕眩、减速、法球圈、升级光）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；"
      "地上的 `q_form`、`q_blast`、`w_land` 上下左右都对称；地上停留的法球 `orb` 左右对称。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `syndra_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。")
    a("> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。")
    a("> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`syndra_fx_done.zip`）放在 outputs 里，或放在 `outputs/syndra-fx/`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「卓尔不凡」 | 暗黑小光弹普攻；按等级依次强化 Q、W、E、R（升级时身上亮暗紫光） | `a_bolt` · `a_hit` · `evo` |")
    a("| 技能 1 = Q「暗黑法球」 | 在目标处凝聚一颗法球，0.5 秒后砸下造成伤害；法球留在原地 6 秒 | `q_form` · `q_blast` · `q_hit` · `orb` |")
    a("| 技能 2 = W「驱使念力」→ E「弱者退散」 | 抓起法球掷向敌方英雄（伤害 + 减速，法球留在落点）；接着往前推出锥形冲击波，被推开的法球撞到的人被晕眩 | `w_throw` · `w_land` · `w_hit` · `w_slow` · `e_wave` · `e_hit` · `e_stun` · `orb` |")
    a("| 大招 = R「能量倾泻」 | 身边聚起法球，向一名敌方英雄发射 3 颗 + 场上法球数（最多 7 颗） | `r_cast` · `r_orb` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、火花、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**（法球的球体本身可以深色，但外面不要再加黑圈）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给法球的球体和很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("念力亮紫（推波、掷出的光、晕眩、减速）", VIOLET), ("暗黑法球（球体、碎片）", VOID),
                        ("洋红（法球边光、打中、宝石光）", MAGENTA)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，"
      "Q 半径 20000，W 半径 21000，E 推波长 70000，法球的晕眩范围半径 24000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `syndra_fx_{name}.png`：{title}\n")
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
        a(f"| `syndra_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 光弹、掷出的法球、R 的法球从伸出的右手出（出手帧手在站位点前 6–7 格、脚底上 24–26 格）；`bolt_y` / `r_y` 按这个量（太高的弹道会斜），画面开头补一帧空的（追踪弹第一 tick 朝上）。")
    a("- `e_wave`：线的画面在辛德拉身上、朝目标转（champion-data section 6）；按 144 格宽切格，确认左半边是空的、上下对称；QE 时它也从辛德拉出发（模拟日志核对线的出生点）。")
    a("- `orb`：12 帧共 6 秒（orb_t 360 tick），落点画在人物上面；`q_form` 6 帧共 0.5 秒（q_fall 30 tick，`range_effect_name`）；`e_stun` 8 帧共约 1.25 秒（e_stun 75 tick）。")
    a("- 没有烘进动作帧的特效：`evo` 晚于第一 tick，`is_follow` 为 false，逐格左右对称；`r_cast` 在 R 第一 tick 跟随播放、逐格左右对称；`q_form`、`q_blast`、`w_land` 画在人物下面（z -2 / -1）。")
    a("- 用 `pixel_1x/` 切格（import_viktor / import_senna 的做法），断言对称；清掉 Codex 给光描的最深色边（法球球体的深色保留）；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="syndra_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Syndra's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "syndra_design.png"))
    shape = size_sheet(os.path.join(out, "design", "syndra_size.png"))
    shots_sheet(os.path.join(out, "design", "syndra_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"syndra_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
