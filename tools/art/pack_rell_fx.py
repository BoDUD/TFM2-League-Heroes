#!/usr/bin/env python3
"""Build rell_fx_pack.zip: step 3 of Rell's sprite - Codex draws her effects (pack_pantheon_fx.py's way).

    python work/rl/fx_ref_rl.py              # League's particle textures -> %TEMP%/rl_work/fxref (Riot's art, local only)
    python tools/art/pack_rell_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name rell_fx_redo_pack]

The pack (%TEMP%/rl_work/fx/rell_fx_pack, zipped into --out, default dist/rell_packs) holds PROMPTS.md (also written to
assets/source/rell/PROMPTS_FX.md), design/rell_idle.png (her two designs at 4x), design/rell_size.png (the 1x idles at 4x
on the arena colour with the feet line, a 10-px ruler and the base fighter), design/rell_shots.png (the finished action
frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle textures for Rell grouped by the
effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_rell.py: view_projectiles q_line; view_effects a_hit, q_hit,
e_cast, e_boom, w_jump, w_crash, w_hit, w2_mount, w2_hit, r_cast, r_yank, r_hit; view_buffs p_shred, q_stun, e_ms,
e_ready, w_shield, foot, r_on). League's colours: her lance and Shattering Strike's amber gold with a white core, the
horse's olive iron flying as metal scraps, Crash Down's dust and crater, Magnet Storm's blue-violet magnetic warp with
gold sparks; light gets no outline.
Red side: the line picture (q_line) symmetric top to bottom (it turns with the strike), every picture on a unit, on her,
on the ground and every buff symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rl_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "rell", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_rell")
HD = os.path.join(ROOT, "assets", "source", "rell", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A"      # her lance's light: white core, pale to amber gold
MAGNET = "#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650"    # Magnet Storm's field: white, lavender to deep violet
IRON = "#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522"               # the horse's olive iron (flying scraps, shields)
EARTH = "#E6D9BE, #BFA882, #93805E, #685843, #43392E"               # dust, the crater, the cracks
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours "
        "(each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only "
        "from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GO = f"an amber gold ramp ({GOLD})"
MA = f"a magnetic violet ramp ({MAGNET})"
IR = f"an olive iron ramp ({IRON})"
ER = f"an earth ramp ({EARTH})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
RIDER = "a rider on a horse 52 squares wide and 44 tall stands in the middle, not drawn"
FIG = "an upright figure 20 squares wide and 40 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_rell_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "骑枪刺中：一小团琥珀金色的闪光和几颗火星（参考 BA_Tar_Flash、BA_Throw_Sparks）。**左右对称**。约 10 格。", GO,
     f"a SMALL GOLDEN HIT on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a gold flash 7 squares with a white core; 3 the "
     "flash 10 squares, 6 short gold sparks at mirrored places; 4 a few fading gold motes.",
     row(4, 12, 12) + CENTER),
    ("p_shred", "被动 溃敌沉力：破甲印记（敌人头顶，循环），4 帧", "view_buffs `league_rell_p_shred`（跟随，画在人物上面；左右对称）", "10 × 8",
     "被她的普攻和技能打中的敌人 5 秒内护甲和魔抗降低：敌人头顶一块小小的、裂开的橄榄铁甲片，裂缝里透出金光，一闪一闪（参考 P_Rocks、E_Metal_Scrap）。**左右对称**，要小。",
     f"{IR} and {GO}",
     f"a SMALL CRACKED ARMOUR PLATE floating over a unit, 4 frames, a seamless loop, {LR}: a little olive iron shield plate 8 squares "
     "wide and 7 tall cracked down the middle, gold light glowing in the crack, the crack's glow pulsing (dim, bright, brightest, "
     "bright), two tiny gold motes at mirrored places.",
     row(4, 10, 8) + CENTER),
    # ---- Shattering Strike
    ("q_line", "Q 裂阵：直线冲击（一条线，朝目标），6 帧", "view_projectiles `league_rell_q_line`（裂阵那条线：朝目标方向转，画成朝右；上下对称；大图表）", "42 × 12",
     "裂阵：骑枪往前猛刺，一道琥珀金色的冲击波沿直线冲出去，前头是一个尖尖的白金色枪尖光，两边炸开金色碎光和火星，后面一缕淡淡的烟（参考 Q_Streak、Rell_Q_Shockwaves2、Q_Impact_Flare、Q_Trail_Smoke、Skin08_Q_StabPoint）。"
     "**上下对称**。这条线出现 0.4 秒后才打中：前 3 帧是一条淡淡的金色预警线（越来越亮），第 4 帧冲击打出去，后 2 帧消散。",
     GO,
     f"a GOLDEN LANCE SHOCKWAVE along a line to the RIGHT, 6 frames, {TB}: 1-3 a thin faint gold guide line the whole 42 squares, "
     "a little brighter each frame (frame 3 with a dim glow 4 squares tall); 4 the strike: a white-gold spear point of light 8 squares "
     "tall at the RIGHT end, a gold shockwave filling the line 8 squares tall with a white core, gold shards and sparks flying out above "
     "and below at mirrored places; 5 the shockwave breaking into gold fragments along the line; 6 fading motes and a thin smoke wisp.",
     row(6, 44, 14) + "; the line through the middle row of every cell, from the LEFT edge to the RIGHT edge."),
    ("q_hit", "Q 裂阵命中：打破护盾（目标身上），5 帧", "view_effects `league_rell_q_hit`（跟随，画在人物上面；左右对称）", "18",
     "裂阵打中：一个金白色的十字闪光炸开，像玻璃一样的金色护盾碎片往四周飞（打破护盾），几颗火星（参考 Q_Impact_Cross、Q_Hit_Flash_Spikes_yellow、Q_Spark_tar）。**左右对称**。约 18 格。",
     GO,
     f"a SHIELD-SHATTERING IMPACT on a unit, 5 frames, {LR}: 1 a white flash 5 squares; 2 a white-gold four-pointed cross flash 14 squares "
     "across; 3 the cross 18 squares, a ring of pale gold glass-like shield shards breaking outward at mirrored places; 4 the shards flying "
     "out and falling, gold sparks; 5 fading shards and motes.",
     row(5, 20, 20) + CENTER),
    ("q_stun", "Q 晕眩（目标头顶，循环），4 帧", "view_buffs `league_rell_q_stun`（跟随，画在人物上面；左右对称；W 驾临的晕眩也用这张）", "14 × 6",
     "被晕住：头顶三颗金色小星星绕圈转。**左右对称**（每帧左右对称地摆放），要小。", GO,
     f"STUN STARS over a unit's head, 4 frames, a seamless loop, {LR}: three small white-gold four-pointed stars 3 squares each on a flat "
     "ellipse 12 squares wide and 4 tall, one in the middle front and two at mirrored places at the sides, brightening in turn.",
     row(4, 14, 6) + CENTER),
    # ---- Full Tilt
    ("e_cast", "E 全速冲锋：起手（她身上，跟随），5 帧", "view_effects `league_rell_e_cast`（跟随，画在她身上；左右对称）", "56 × 30",
     "全速冲锋：她和马脚下一圈金色的磁力冲击向外扩，几道金色的速度光线从地面往上冲，几片小铁甲片和金色火星绕着她转一圈（参考 E_LeadingEdge_Ring、E_Clone_Sparkle、E_Metal_Scrap、E_Trail_Persist）。"
     f"**左右对称**，中间身体位置留空（{RIDER}）。",
     f"{GO} and {IR}",
     f"a SPEED SURGE round a mounted figure, 5 frames, {LR} ({RIDER}): 1 a white-gold flash ring on the ground 20 wide and 5 tall under "
     "the middle; 2 the ring 40 wide with a bright rim, 4 thin gold speed streaks rising at mirrored places; 3 the ring 56 wide, the "
     "streaks 20 squares tall, 4 small olive iron scraps and gold sparks circling at mirrored places; 4 the ring fading, the scraps "
     "spinning out; 5 the last sparks.",
     row(5, 58, 32) + "; centered across, the ground ring's middle 3 squares above the cell's bottom row."),
    ("e_ms", "E 全速冲锋：加速（她和队友脚下，循环），4 帧", "view_buffs `league_rell_e_ms`（跟随，画在人物下面；左右对称）", "26 × 8",
     "加速中：脚下两侧扬起小股的金色尘风，几颗金色火星贴着地面往外甩（参考 E_Trail_Persist、R_Dash_DirtTrail）。**左右对称**（两边一样），淡一点，不要盖住人。",
     f"{GO} and {ER}",
     f"a SPEED WIND at a unit's feet, 4 frames, a seamless loop, {LR}: a flat ellipse of faint gold wind 24 squares wide and 4 tall on the "
     "ground, at both ends small dust puffs curling outward and gold sparks skimming out at mirrored places, the puffs taking turns to "
     "swell; the middle 8 squares nearly empty.",
     row(4, 26, 8) + CENTER),
    ("e_ready", "E 全速冲锋：下一击会爆炸（她头顶，循环），4 帧", "view_buffs `league_rell_e_ready`（跟随，画在她上面；左右对称）", "12 × 12",
     "下一次普攻或裂阵会爆炸：她头顶一个金色的磁力印记（一个小小的马蹄形磁铁符号，两端冒着蓝紫色的电火花），一闪一闪。**左右对称**，要小但亮。",
     f"{GO} and {MA}",
     f"a MAGNET SIGIL floating over a unit, 4 frames, a seamless loop, {LR}: a small gold horseshoe magnet sign 9 squares wide and 9 "
     "tall, its two prongs pointing DOWN, a white core line along it, tiny blue-violet sparks crackling at both prong tips at mirrored "
     "places; pulsing dim, bright, brightest, bright.",
     row(4, 12, 12) + CENTER),
    ("e_boom", "E 全速冲锋：爆炸（目标身上），5 帧", "view_effects `league_rell_e_boom`（跟随，画在人物上面；左右对称）", "22",
     "爆炸：目标身上一团金色的磁力爆炸，中间白芯，外面一圈蓝紫色的磁力冲击环，几片铁甲碎片和火星往外飞（参考 Q_Impact_Flare、Distort_Ring、E_Metal_Scrap）。**左右对称**。约 22 格。",
     f"{GO}, {MA} and {IR}",
     f"a MAGNETIC BLAST on a unit, 5 frames, {LR}: 1 a white flash 6 squares; 2 a gold burst 14 squares with a white core; 3 a blue-violet "
     "shock ring 22 squares across round the gold burst, olive iron scraps and gold sparks flying out at mirrored places; 4 the ring "
     "breaking up, the scraps falling; 5 fading motes.",
     row(5, 24, 24) + CENTER),
    # ---- Ferromancy: Crash Down / Mount Up
    ("w_jump", "W 轰落：起跳（她身上，跟随），4 帧", "view_effects `league_rell_w_jump`（跟随，画在她身上；左右对称）", "50 × 16",
     "轰落起跳：马蹄下炸开两团土黄色的尘土往两边扬，中间几道金色的光线往上冲，马身化成铁甲时冒出的金光碎片（参考 W_Dirt_Takeoff、W_Horse_Erode_Swipe、W_ArmorFlow）。**左右对称**，只画地上的尘土和往上的光。",
     f"{ER} and {GO}",
     f"a TAKE-OFF BURST on the ground, 4 frames, {LR}: 1 a white-gold flash 10 squares wide on the ground; 2 two dust clouds blasting out "
     "to both sides 18 squares each, 3 gold light streaks shooting up 12 squares from the middle; 3 the dust 50 squares wide and rising, "
     "gold flecks floating up; 4 the dust settling and thinning.",
     row(4, 52, 18) + "; centered across, the dust's base on the cell's bottom row."),
    ("w_crash", "W 轰落：砸地（落点地上，不跟随），6 帧", "view_effects `league_rell_w_crash`（不跟随，画在地上、人物下面；左右对称；大图表）", "50 × 22",
     "她披着铁甲砸到地上：地上砸出一个土坑，一圈金色的冲击波向外推开，地面裂开、裂缝里透出金光，尘土往两边炸，几块碎石飞起来（参考 Rell_W_Ground_Crater、W_Ground_Impact、W_GroundCracks_Glow、W_Burst、W_Smoke）。**左右对称**。",
     f"{ER} and {GO}",
     f"a GROUND CRASH, 6 frames, {LR}: 1 a white-gold flash 12 squares wide on the ground; 2 a dark crater ellipse 20 wide and 6 tall, a "
     "bright gold shock ring 30 wide and 9 tall round it; 3 the ring 46 wide, gold-glowing cracks spreading out from the crater at mirrored "
     "places, dust blasting out at both sides, small rocks flying up; 4 the ring 50 wide and fading, the dust spreading; 5 the dust "
     "thinning, the cracks still glowing; 6 faint cracks and the crater.",
     row(6, 52, 24) + "; centered across, the crater's middle 6 squares above the cell's bottom row."),
    ("w_hit", "W 轰落：击飞命中（目标身上），4 帧", "view_effects `league_rell_w_hit`（跟随，画在人物上面；左右对称）", "16",
     "被砸飞：目标身上一团金色冲击，脚下一小股尘土往上冲。**左右对称**。约 16 格。",
     f"{GO} and {ER}",
     f"a KNOCK-UP HIT on a unit, 4 frames, {LR}: 1 a white flash 5 squares; 2 a gold burst 12 squares with a white core, a puff of dust "
     "shooting up from the bottom; 3 the burst 16 squares, 6 gold rays at mirrored places, the dust column rising; 4 fading motes and dust.",
     row(4, 18, 18) + CENTER),
    ("w_shield", "W 轰落：护盾（她身上，循环），4 帧", "view_buffs `league_rell_w_shield`（跟随，画在她身上；左右对称）", "40 × 40",
     "轰落的护盾：她身体两侧各一片弯弯的金色铁盾光（像两片月牙形的盾），盾面有亮边，外面一层淡淡的金光（参考 W_Shield_Flair、W_template_Shield、W_Shield_Mult）。"
     f"**左右对称**，中间身体位置留空（{FIG}），淡一点，不要盖住她。",
     f"{GO} and {IR}",
     f"a PAIR OF CURVED GOLDEN SHIELD PLATES round a figure, 4 frames, a seamless loop, {LR} ({FIG}): one crescent shield of gold-lit "
     "iron 8 squares wide and 30 tall at each side of the figure, their hollow sides facing it, bright white-gold rims, a faint gold "
     "glow round them; the glow pulsing, a white glint sliding down both rims together.",
     row(4, 42, 42) + "; centered across, the figure's feet on the cell's bottom row."),
    ("foot", "W 下马作战：铁甲光环（她身上，循环），4 帧", "view_buffs `league_rell_foot`（跟随，画在她身上；左右对称）", "36 × 40",
     "下马作战的状态：几片小小的橄榄铁甲碎片在她身边慢慢绕着漂，每片边上一点金光，偶尔一道蓝紫色的磁力小电弧把两片连起来（参考 W_ArmorFlow、E_Metal_Scrap、R_Metal_Scrap）。"
     f"**左右对称**（碎片左右对称地摆放），中间身体位置留空（{FIG}），要淡，不要盖住她。",
     f"{IR}, {GO} and {MA}",
     f"FLOATING IRON SCRAPS round a figure, 4 frames, a seamless loop, {LR} ({FIG}): 6 small olive iron scraps 2-3 squares each at "
     "mirrored places round the figure (2 at the shoulders, 2 at the hips, 2 at the knees), each with a gold glint, bobbing up and down "
     "1 square in turn; in frames 2 and 4 a thin blue-violet magnetic arc joins the two shoulder scraps across the top.",
     row(4, 38, 42) + "; centered across, the figure's feet on the cell's bottom row."),
    ("w2_mount", "W 驾临：铁甲合成马（她身上，跟随），5 帧", "view_effects `league_rell_w2_mount`（跟随，画在她身上；左右对称）", "56 × 40",
     "驾临：四周的铁甲碎片和金光往她身上飞回来、合成马，最后一道金色的光闪一下（参考 W_Mount_Whoosh、W_ArmorFlow、R_Metal_Scrap）。"
     f"**左右对称**，中间位置留空（{RIDER}）。",
     f"{IR} and {GO}",
     f"IRON SCRAPS GATHERING into a mount, 5 frames, {LR} ({RIDER}): 1 8 olive iron scraps 3-4 squares each far out at mirrored places, "
     "gold trails behind them; 2 the scraps halfway in, gold whooshes curving in from both sides; 3 the scraps reaching the middle, a "
     "gold glow outline 50 wide and 40 tall; 4 a white-gold flash line across the middle, the outline brightest; 5 fading gold motes.",
     row(5, 58, 42) + "; centered across, the bottom of the shape on the cell's bottom row."),
    ("w2_hit", "W 驾临：冲锋撞飞（目标身上），5 帧", "view_effects `league_rell_w2_hit`（跟随，画在人物上面；左右对称）", "20",
     "上马冲锋撞中：目标身上一团金色冲击，一道金色的弧光从下往上翻（把人掀起来），几颗火星（参考 W_Flip_Swipe、Q_Impact_Flare）。**左右对称**。约 20 格。",
     GO,
     f"a FLIPPING CHARGE HIT on a unit, 5 frames, {LR}: 1 a white flash 6 squares; 2 a gold burst 12 squares with a white core; 3 two gold "
     "arcs sweeping UP from the bottom at both sides like a fountain, 20 squares tall; 4 the arcs at the top, gold sparks falling at "
     "mirrored places; 5 fading motes.",
     row(5, 22, 22) + CENTER),
    # ---- Magnet Storm
    ("r_cast", "R 极涌：爆发（她身上，跟随），6 帧", "view_effects `league_rell_r_cast`（跟随，画在她身上、人物后面；左右对称；大图表）", "72 × 44",
     "极涌：她身上爆出一大圈蓝紫色的磁力冲击波（地上扁椭圆 + 往上的半透明磁力穹顶），金色的电弧和铁甲碎片从四周往她身上吸（参考 R_glow_distort、R_RipplesEdge、R_TrampleAOE_Glow、R_Metal_Scrap、Distort_RGBA）。"
     f"**左右对称**，中间位置留空（{RIDER}）。",
     f"{MA}, {GO} and {IR}",
     f"a MAGNETIC BURST round a mounted figure, 6 frames, {LR} ({RIDER}): 1 a white-violet flash 16 squares round the middle; 2 a "
     "blue-violet ring on the ground 40 wide and 12 tall with a bright lavender rim, a faint violet dome 36 tall over it; 3 the ring 72 "
     "wide and 22 tall, the dome's rim crackling with gold arcs at mirrored places, olive iron scraps far out; 4 the scraps streaking IN "
     "toward the middle with gold trails; 5 the ring pulsing, violet ripples; 6 the ring fading to its rim.",
     row(6, 74, 46) + "; centered across, the ground ring's middle 6 squares above the cell's bottom row."),
    ("r_on", "R 极涌：磁场（她脚下，2 秒循环），6 帧", "view_buffs `league_rell_r_on`（跟随，画在她下面；左右对称；大图表）", "70 × 24",
     "极涌持续 2 秒，把周围的人往她身边拖：她脚下一大圈蓝紫色的磁力场在转，圈上几道金色电弧，圈里的地面有往中间收的蓝紫色波纹（参考 R_Wave_Texture、R_GroundDrag、R_Mark_distort）。**左右对称**，只画地上的圈和波纹。",
     f"{MA} and {GO}",
     f"a SPINNING MAGNETIC FIELD on the ground, 6 frames, a seamless loop, {LR}: a flat blue-violet ellipse ring 68 squares wide and 22 tall "
     "with a bright lavender rim, 3 ripple rings inside it shrinking toward the middle frame by frame (pulled in), 4 short gold "
     "electric arcs on the rim at mirrored places jumping between frames; the middle 20 squares empty.",
     row(6, 70, 24) + CENTER),
    ("r_yank", "R 极涌：被拉（敌人身上），4 帧", "view_effects `league_rell_r_yank`（跟随，画在人物上面；左右对称）", "18 × 26",
     "被猛地拉过去：敌人身上一圈蓝紫色的磁力光收紧，几道金色电弧缠在身上。**左右对称**，中间身体留空（一个 12 格宽、24 格高的人站在中间，不要画）。",
     f"{MA} and {GO}",
     f"a MAGNETIC GRIP round a unit, 4 frames, {LR} (a figure 12 squares wide and 24 tall stands in the middle, not drawn): 1 a "
     "blue-violet glow outline 18 wide and 26 tall; 2 the outline tightening to 14 wide with a bright lavender rim, 2 gold arcs crossing "
     "the figure at mirrored places; 3 the arcs crackling; 4 the glow fading.",
     row(4, 20, 28) + "; centered across, the figure's feet on the cell's bottom row."),
    ("r_hit", "R 极涌：持续伤害（敌人身上，每 0.25 秒），3 帧", "view_effects `league_rell_r_hit`（跟随，画在人物上面；左右对称）", "10",
     "每跳伤害：一小团蓝紫色的磁力火花加一点金光。**左右对称**，要小（会连续出现很多次）。", f"{MA} and {GO}",
     f"a TINY MAGNETIC SPARK on a unit, 3 frames, {LR}: 1 a white dot 2 squares; 2 a violet spark star 7 squares with a gold core; "
     "3 4 fading violet motes.",
     row(3, 10, 10) + CENTER),
]

GROUPS = [
    ("a_hit q_line q_hit q_stun", ["Rell_Base_BA_Tar_Flash", "Rell_Base_BA_Throw_Sparks", "Rell_Base_Q_Streak", "Rell_Q_Shockwaves2",
                                   "Rell_Base_Q_Impact_Cross", "Rell_Base_Q_Hit_Flash_Spikes_yellow"]),
    ("e_* p_shred", ["Rell_Base_E_LeadingEdge_Ring", "Rell_Base_E_Clone_Sparkle", "Rell_Base_E_Metal_Scrap", "Rell_Base_E_Trail_Persist",
                     "Rell_Base_Distort_Ring", "Rell_Base_P_Rocks_2X2"]),
    ("w_jump w_crash w_hit", ["Rell_Base_W_Dirt_Takeoff_Style_Erode_V02", "Rell_W_Ground_Crater", "Rell_W_Ground_Impact",
                              "Rell_Base_W_GroundCracks_Glow", "Rell_W_Burst", "Rell_Base_W_Smoke_01"]),
    ("w_shield foot w2_*", ["Rell_Base_W_Shield_Flair", "Rell_Base_W_template_Shield", "Rell_Base_W_ArmorFlow", "Rell_W_Mount_Whoosh_Mult",
                            "Rell_Base_W_Flip_Swipe", "Rell_Base_R_Metal_Scrap"]),
    ("r_*", ["Rell_Base_R_glow_distort", "Rell_Base_R_RipplesEdge", "Rell_Base_R_TrampleAOE_Glow", "Rell_Base_R_Wave_Texture",
             "Rell_Base_R_GroundDrag", "Rell_Base_Distort_RGBA"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is her standing point
SHOTS = [("attack", 3, "a_hit：枪刺出"), ("skill", 4, "q_line：裂阵打出"), ("skill2", 2, "w_jump：起跳"),
         ("skill2", 6, "w_crash：落地"), ("skill2_up", 4, "w2_hit：冲锋"), ("ult", 3, "r_cast：极涌"),
         ("f_idle", 1, "w_shield / foot：下马的她")]


def ref_sheet(path):
    S, LW = 180, 170
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                continue
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
            bg.alpha_composite(im)
            sheet.alpha_composite(bg, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Rell_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    figs = [first_1x("idle"), first_1x("f_idle")]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    figs.append(k[ky.min():ky.max() + 1, kx.min():kx.max() + 1])
    Z, pad = 4, 6
    W = pad + sum(f.shape[1] + pad for f in figs)
    top = max(f.shape[0] for f in figs)
    img = Image.new("RGBA", (W * Z, (pad + top + 4) * Z + 64), (104, 112, 72, 255))
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
    d.text((8, 36), f"芮尔骑马 {figs[0].shape[1]}×{figs[0].shape[0]} 格，下马 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape, figs[1].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 260), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
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


def document(shapes):
    (ha, wa), (hb, wb) = (s[:2] for s in shapes)
    L = []
    a = L.append
    a("# 镕铁少女 芮尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/rell_idle.png`：左边骑着橄榄铁甲战马、平端金色骑枪的她，右边是下马后穿着马化成的铁甲的她；"
      "3/4 正面朝右）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），"
      f"骑马时连骑枪 {wa} 格宽、{ha} 格高，下马时 {wb} 格宽、{hb} 格高；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/rell_size.png`：她两种形态的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/rell_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里芮尔自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**骑枪和裂阵是琥珀金色的光（白芯）**，**马的橄榄铁甲会变成飞来飞去的铁甲碎片**，**轰落是土黄色的尘土和土坑**，"
      "**极涌是蓝紫色的磁力场、带金色电弧**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住她。")
    a("> - **方向（重要，红色方不会镜像）**：裂阵那条线 `q_line` 画成朝右，**上下对称**（往左时会上下翻）。"
      "其余所有画面（打中、身上、脚下、地上、头顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `rell_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `rell_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「溃敌沉力」 | 骑枪突刺；打中英雄削减其护甲魔抗 | `a_hit` · `p_shred` |")
    a("| 技能 1 = Q「裂阵」+ E「全速冲锋」 | Q 沿直线刺出冲击波、晕眩、打破护盾；E 和队友加速，下一击爆炸 | `q_line` · `q_hit` · `q_stun` · `e_cast` · `e_ms` · `e_ready` · `e_boom` |")
    a("| 技能 2 = W「驭铁术」 | 轰落：跳起砸地、击飞、得护盾、下马作战；驾临：铁甲合回成马、冲锋撞飞 | `w_jump` · `w_crash` · `w_hit` · `w_shield` · `foot` · `w2_mount` · `w2_hit` |")
    a("| 大招「极涌」 | 把周围敌人猛拉到身边，2 秒内持续拖拽并造成伤害 | `r_cast` · `r_on` · `r_yank` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火星、尘土、冲击环、磁力光都没有黑描边，也不要用最深的颜色给形状描一圈边**（铁甲碎片例外：可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("琥珀金（骑枪、裂阵、冲击）", GOLD), ("磁力紫（极涌、E 的爆炸）", MAGNET), ("橄榄铁（铁甲碎片、盾）", IRON),
                        ("土黄（尘土、土坑、裂缝）", EARTH)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 25000，"
      "裂阵 42000 长，轰落砸地半径 24000，极涌半径 34000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `rell_fx_{name}.png`：{title}\n")
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
        a(f"| `rell_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_rell_fx`（小的）和 `league_rell_big`（q_line、w_jump、w_crash、r_cast、r_on），tag = 名字（build_rell.py 的 views）。")
    a("- `q_line` 是投射物（LineRangeProjectile），画面朝方向转，第 4 帧（打中）要落在出现后约 0.38 秒；`w_crash` 不跟随、画在人物下面（z -1）；`r_on` 循环盖满 2 秒；`r_cast` 画在她后面（z -1）。")
    a("- 用 `pixel_1x/` 切格（import_pantheon_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="rell_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "rell_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/rl/fx_ref_rl.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    da = np.asarray(Image.open(lp(os.path.join(HD, "design_A.png"))).convert("RGBA"))
    db = np.asarray(Image.open(lp(os.path.join(HD, "design_B.png"))).convert("RGBA"))
    both = np.zeros((max(da.shape[0], db.shape[0]), da.shape[1] + db.shape[1] + 8, 4), np.uint8)
    both[both.shape[0] - da.shape[0]:, :da.shape[1]] = da
    both[both.shape[0] - db.shape[0]:, da.shape[1] + 8:] = db
    Image.fromarray(np.repeat(np.repeat(both, 4, 0), 4, 1)).save(os.path.join(out, "design", "rell_idle.png"))
    shapes = size_sheet(os.path.join(out, "design", "rell_size.png"))
    shots_sheet(os.path.join(out, "design", "rell_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"rell_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shapes)
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
