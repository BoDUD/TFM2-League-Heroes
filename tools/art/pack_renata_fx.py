#!/usr/bin/env python3
"""Build renata_fx_pack.zip: step 3 of Renata's sprite - Codex draws her effects (pack_swain_fx.py's way; the user,
2026-10-17: 「动作帧通过，可以做特效包了」).

    python work/rn/fx_ref_rn.py              # League's particle textures -> %TEMP%/rn_work/fxref (Riot's art, local only)
    python tools/art/pack_renata_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name renata_fx_redo_pack]

The pack (%TEMP%/rn_work/fx/renata_fx_pack, zipped into --out, default dist/renata_packs) holds PROMPTS.md (also written
to assets/source/renata/PROMPTS_FX.md), design/renata_idle.png (her idle and the ult's machine at 4x, as the game shows
them: PPU 1.5), design/renata_size.png (the 1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the
base fighter), design/renata_shots.png (the finished 1x action frames the pictures start from, 4x: her standing point
and where a picture leaves her) and refs/lol_fx_ref.png (League's own particle textures for Renata grouped by the effect
of ours they inform).
The effects are the views the kit binds (tools/kit/build_renata.py: view_projectiles a_shot, e_missile, q_hand, r_wave;
view_effects a_hit, p_pop, w_cast, w_save, e_hit, e_boom, e_shield, q_hit, q_fling, q_land, q_crash_hit, r_cast, r_hit,
r_lash, r_lash_hit; view_buffs p_mark, w_buff, e_slow, r_berserk) and a_flash, the muzzle flash rig_renata.py draws
into her attack's shot frames (drawn on her own fine squares). The R machine is not here: it is in her ult frames.
League's colours (Renata_Base_Gradients, Q_Inner_Arm_Tubes_Gradient, R_Puddles, W_Smoke_Shape): her chemicals are rose
pink from deep wine to a white core, the hottest tips a pale cyan (BA_Beam_01, E_Shimmer_Trail), W's smoke magenta-
violet, gold only as a sparkle; light gets no outline.
Red side: the flying pictures (a_shot, e_missile, q_hand, r_wave) symmetric top to bottom (they turn with the flight),
every picture on a unit, on her, over a head and on the ground symmetric left to right; a_flash rides in her frames.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rn_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "renata", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_renata")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


CHEM = "#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634"      # her chemicals: white core to deep wine
SHIM = "#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB"                        # the hottest tips' pale cyan shimmer
VIOL = "#F7B4EA, #D53DB4, #A51791, #6E0C70, #3E0846"               # Bailout's magenta-violet smoke
GOLD = "#FFFFFF, #FFF0A8, #FFCB4A, #F29A12, #A65A0A"               # Glasc gold (sparkles only)
WINE = "#D07AA0, #A23E6E, #6E1C4A, #42102E"                        # dust and the gas's shadows
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
CH = f"a rose-pink chemical ramp ({CHEM})"
SM = f"a pale cyan shimmer ramp ({SHIM})"
VI = f"a magenta-violet smoke ramp ({VIOL})"
GO = f"a gold ramp ({GOLD})"
WI = f"a wine-pink dust ramp ({WINE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
HERO = "an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn"
MECH = "she and her machine stand in the middle (30 squares wide, 56 tall), not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive Leverage
    ("a_shot", "普攻：手枪射出的化学子弹（飞行，循环），4 帧", "view_projectiles `league_renata_a_shot`（朝目标飞，画面随方向转；上下对称）",
     "10 × 4",
     "从手枪枪口射出的一颗**玫红化学子弹**：白热的弹头（约 3 格长、2 格高，白芯），外面一圈玫红的光，身后拖一道约 7 格长、越往后越细的玫红光迹，"
     "光迹中间一条淡青白的细线，上下各一缕酒红的小烟（上下对称）（参考 BA_Bullet_Glow、BA_Beam_01、BA_Smoke_Trail）。**朝右飞，上下对称**。约 10 格长。",
     f"{CH} and {SM} and {WI}",
     f"a CHEMTECH PISTOL BULLET flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white-hot bullet 3 squares long and "
     "2 tall with a rose-pink glow round it, a tapered rose-pink tracer 7 squares long behind it with a thin pale cyan "
     "line in its middle, two small wine-pink smoke wisps curling off the tracer at mirrored places above and below, "
     "flickering.",
     row(4, 12, 6) + "; the bullet's tip 1 square from the RIGHT edge, vertically centered."),
    ("a_flash", "普攻：枪口火光（画进她的普攻帧，**按她的细格子画**），3 帧",
     "不进特效表：Claude 画进她自己的 attack 第 3、4 帧（枪口；跟着她翻面）", "10 × 9（她的细格子）",
     "开枪一瞬间枪口喷出的火光：白芯，三片玫红的火舌（往前一片最长，斜上、斜下各一片，上下对称），第 2 帧变小、带一点淡青白的光，"
     "第 3 帧只剩一小团玫红的烟（参考 BA_Flash_sharp、BA_Embers、BA_Screen_Flames_Soft）。**朝右，上下对称**。"
     "**这一张按她身上的细格子画**（她是高清的：她的 1 格 = 游戏的 2/3 格，见 `design/renata_idle.png`），10 × 9 格。",
     f"{CH} and {SM}",
     f"a PISTOL MUZZLE FLASH pointing to the RIGHT, 3 frames, played once, {TB}: 1 a white core 2 squares wide and 3 tall "
     "at the left edge with three rose-pink flame tongues (one forward 6 squares long, one up-forward and one "
     "down-forward 3 squares long, mirrored); 2 the flame smaller (the forward tongue 3 squares), a pale cyan glint at "
     "the core; 3 a small puff of rose-pink smoke 4 squares, no white.",
     row(3, 10, 9) + "; the flash's root (where the barrel ends) on the LEFT edge, vertically centered."),
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_renata_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "子弹打中：一颗四角星形的玫红闪光（白芯），中间横穿一道细长的镜头光（中间白、两头淡青），几粒玫红火星往外溅"
     "（参考 BA_Tar_Flare、BA_Hit_Lens_Flare、BA_Flash_sharp）。**左右对称**。约 12 格。",
     f"{CH} and {SM}",
     f"a CHEMTECH BULLET HIT on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 a four-pointed star flash 9 squares "
     "(white core, rose-pink rays up, down, left and right) with a thin horizontal lens-flare streak 13 squares long "
     "through its middle (white centre, pale cyan ends); 3 the star 11 squares, the streak fading, 4 rose-pink embers "
     "flying out at mirrored places; 4 fading pink embers.",
     row(4, 14, 14) + CENTER),
    ("p_mark", "被动 物尽其用：头顶的化学印记（敌方英雄身上，循环），4 帧", "view_buffs `league_renata_p_mark`（跟随，头顶上方；左右对称）",
     "12 × 13",
     "被她打中的敌方英雄挂上印记：头顶浮着一滴发光的**玫红化学药剂**（水滴形，尖头朝上，白色高光，约 4 格宽 6 格高），外面一圈细细的"
     "彩虹光环（玫红、淡青、金三色交替，像英雄联盟的 P_Rainbow_Flash），一闪一闪，水滴底下偶尔滴下一小滴（参考 P_Rainbow_Flash、"
     "Renata_P_Puddle_Goop、P_SmokeTrail）。**左右对称**，4 帧无缝循环。导入时 Claude 把它放到头顶上方。",
     f"{CH} and {SM} and {GO}",
     f"a HOVERING CHEMTECH DROP MARK, 4 frames, a seamless loop, {LR}: a glowing rose-pink teardrop of chemical (4 squares "
     "wide and 6 tall, pointed at the top, a white highlight 2 squares in its upper middle), inside a thin ring of "
     "iridescent light (a circle 12 squares across, 1 square thick, its squares alternating rose-pink, pale cyan and "
     "gold, mirrored left to right); frame 1 as described, 2 the ring brighter, 3 the drop swollen by a square, 4 a "
     "small droplet (2 squares) falling from the drop's round bottom.",
     row(4, 12, 14) + "; centered across, the ring in the upper 12 rows, the falling droplet below it."),
    ("p_pop", "被动引爆：印记炸开（敌方英雄身上），5 帧", "view_effects `league_renata_p_pop`（跟随，画在人物上面；左右对称）", "16",
     "队友打中带印记的敌人时印记引爆：一圈彩虹光环猛地扩开（玫红、淡青、金），中间一团玫红的化学爆炸（白芯），几滴玫红药剂和金色的小光点"
     "往外飞溅（参考 P_Rainbow_Flash、Q_Burst_Hit、Z_Flecks_02）。**左右对称**。约 16 格。",
     f"{CH} and {SM} and {GO}",
     f"a CHEMTECH MARK BURSTING on a unit, 5 frames, {LR}: 1 a white flash 4 squares; 2 a rose-pink chemical burst 10 "
     "squares with a white core inside a thin iridescent ring 12 squares across (its squares rose-pink, pale cyan and "
     "gold); 3 the burst 14 squares with spiky splash tips, the ring 16 squares, 6 pink goo drops (2 squares each) "
     "flying out at mirrored places; 4 the ring breaking into gold and pink motes, the drops further out; 5 fading pink "
     "motes.",
     row(5, 18, 18) + CENTER),
    # ---- E Loyalty Program
    ("e_missile", "E 忠诚激励：两枚并排的化学飞弹（飞行，循环），4 帧",
     "view_projectiles `league_renata_e_missile`（朝目标飞，画面随方向转；上下对称）", "14 × 10",
     "从金色机械手射出的**两枚并排的化学飞弹**：上下各一颗玫红的彗星头（约 3 格，白芯），各拖一道约 8 格长、闪着彩光的尾迹"
     "（玫红里夹着淡青和白的亮点，每帧往后流），两道尾迹微微往外弯，上下完全对称（参考 E_Comet、E_Missile_Head_2、E_Shimmer_Trail、"
     "E_Ribbon_01）。**朝右飞，上下对称**。约 14 格长、10 格宽。",
     f"{CH} and {SM}",
     f"TWO CHEMTECH MISSILES flying side by side to the RIGHT, 4 frames, a seamless loop, {TB}: two comet heads, one above "
     "and one below the middle line (their centres 6 squares apart), each 3 squares with a white core and a rose-pink "
     "glow, each trailing a shimmering ribbon 8 squares long (rose-pink with pale cyan and white glints that move back "
     "along it each frame) curving slightly outward away from the middle; the two missiles exact mirror images.",
     row(4, 16, 12) + "; the comet heads 1 square from the RIGHT edge, the pair vertically centered."),
    ("e_boom", "E 爆炸（飞弹的落点，地上，不跟随），6 帧", "view_effects `league_renata_e_boom`（不跟随，画在人物上面；左右对称）",
     "26 × 16",
     "飞弹在落点炸开：一团玫红的化学爆炸，地上一圈尖刺状的冲击环往外扩（从斜上方看的扁椭圆，约 24 格宽），炸完落成一摊冒泡的玫红药剂"
     "（参考 E_Burst_Hit、E_Mis_AoE_Wind、E_LeadingEdge_Ring、E_shockwave、E_Puddle_Mask、E_Bubble_01）。**左右对称**。",
     f"{CH} and {SM} and {WI}",
     f"a CHEMTECH BLAST on the ground, 6 frames, {LR}: 1 a white-pink flash 6 squares; 2 a rose-pink burst 12 squares wide "
     "and 10 tall with spiky splash tips and a white core, a ring on the ground (an ellipse 16 wide, 5 tall); 3 the "
     "spiky ring 24 squares wide and 8 tall (rose-pink with pale cyan glints on its rim), the burst at its tallest; 4 the "
     "burst falling into a glossy rose-pink puddle (an ellipse 14 wide, 4 tall) with 3 bubbles at mirrored places, the "
     "ring fading; 5 the bubbles popping (white rings 2 squares); 6 the puddle shrinking, a few drops.",
     row(6, 26, 18) + "; centered across, the ground ring's middle 5 squares above the cell's bottom row."),
    ("e_hit", "E 命中（目标身上），4 帧", "view_effects `league_renata_e_hit`（跟随，画在人物上面；左右对称）", "12",
     "被飞弹炸到：一团玫红的药剂溅开（白芯），几滴药剂往两边甩（参考 E_Burst_Hit、Froth）。**左右对称**。约 12 格。",
     f"{CH} and {SM}",
     f"a CHEMICAL SPLASH on a unit, 4 frames, {LR}: 1 a white-pink flash 4 squares; 2 a rose-pink splash 10 squares with a "
     "white core and spiky goo tips; 3 the splash 12 squares, 4 goo drops (2 squares) flung out at mirrored places, "
     "small bubbles; 4 fading drops.",
     row(4, 14, 14) + CENTER),
    ("e_slow", "E 减速：脚下一摊化学药剂（目标身上，循环），4 帧", "view_buffs `league_renata_e_slow`（跟随，画在人物下面；左右对称）",
     "16 × 6",
     "被减速的敌人脚下一摊发亮的**玫红药剂**（从斜上方看的扁椭圆，约 16 格宽 5 格高，边缘波浪形），表面两道白色高光，几个小泡冒出来又破掉"
     "（参考 E_Puddle_Mask、Renata_E_Puddle_Erode、E_Bubble_01）。**左右对称**，4 帧无缝循环。画在人物下面，中间会被人挡住。",
     f"{CH} and {WI}",
     f"a GLOSSY CHEMICAL PUDDLE on the ground under a unit, 4 frames, a seamless loop, {LR}: a rose-pink puddle (an ellipse "
     "16 squares wide and 5 tall with a wavy edge, darker wine-pink squares along its rim, two white highlight streaks at "
     "mirrored places), small bubbles (1-2 squares, white-pink rims) at mirrored places: frame 1 two small bubbles, 2 the "
     "bubbles bigger, 3 popped (white rings), 4 calm.",
     row(4, 18, 8) + "; centered across, the puddle's middle 3 squares above the cell's bottom row."),
    ("e_shield", "E：队友身上的化学泡泡护盾（队友身上，跟随），6 帧", "view_effects `league_renata_e_shield`（跟随，画在人物上面；左右对称）",
     "26 × 36",
     f"飞弹经过的队友得到护盾：一个**玫红色的泡泡**把队友罩住——先在胸口一闪，泡泡从中间长大成一个竖着的椭圆，边缘 1–2 格玫红，"
     f"左上和右上各一道白色高光（左右对称），顶上一层淡青白的彩光，最后泡泡边缘闪一闪碎成小点（参考 E_Shield_Bubble、E_Shield_Edges、"
     f"E_Shield_Front_1、E_Bubble_01）。**左右对称**，**泡泡里面（身体位置）留空**（{HERO}）。",
     f"{CH} and {SM}",
     f"a CHEMICAL BUBBLE SHIELD forming round a figure, 6 frames, {LR} ({HERO}): 1 a white-pink flash 4 squares at the "
     "figure's chest; 2 a rose-pink bubble rim (a circle 14 squares across, 1 square thick) round the chest; 3 the bubble "
     "an upright ellipse 24 squares wide and 34 tall round the whole figure, its rim 1-2 squares rose-pink, a curved "
     "white highlight (3 squares) at its upper left and the same at its upper right, a pale cyan shimmer band along its "
     "top; 4 the same bubble, the shimmer lower; 5 the same, the rim flickering lighter; 6 the rim breaking into "
     "scattered pink squares. Inside the rim the bubble is EMPTY (the figure shows through).",
     row(6, 26, 38) + "; centered across, the bubble's bottom (the figure's feet) 2 squares above the cell's bottom row."),
    # ---- Q Handshake
    ("q_hand", "Q 铁腕竞合：飞出去的化学之手（飞行，循环），4 帧",
     "view_projectiles `league_renata_q_hand`（朝目标飞，画面随方向转；上下对称）", "14 × 11",
     "从金色机械手射出的一只**发光的玫红化学之手**往前抓：手掌约 5 格（淡青白的芯），五根手指往前张开、上下对称（中间一根朝前最长，"
     "上下各两根往外张），手腕后面拖一段约 6 格的发光玫红管子（一节一节的暗酒红环），几粒玫红火星（参考 Q_Avatar_Mask、"
     "Q_Inner_Arm_Tubes、Q_Inner_Arm_Tubes_Gradient、Q_Constraint）。**朝右飞，上下对称**。",
     f"{CH} and {SM} and {WI}",
     f"an OPEN CHEMTECH HAND reaching to the RIGHT, 4 frames, a seamless loop, {TB}: a glowing rose-pink palm (5 squares, a "
     "pale cyan-white core) with five fingers spread forward, symmetric up and down (the middle finger 4 squares long "
     "pointing right, two fingers above and two below fanning outward, each 3 squares, bright pink tips), behind the "
     "wrist a glowing arm of rose-pink tubes 6 squares long with dark wine segment rings, a few pink sparks trailing; "
     "the fingers flexing a little between frames (open, wider, open, narrower).",
     row(4, 16, 13) + "; the middle fingertip 1 square from the RIGHT edge, vertically centered."),
    ("q_hit", "Q 抓住：化学之手攥住目标（目标身上，跟随），6 帧", "view_effects `league_renata_q_hit`（跟随，画在人物上面；左右对称）",
     "24 × 30",
     f"被化学之手抓住（定身）：一闪白光，左右两边各两根发光的玫红大手指从两边伸过来把目标攥住（左右对称），手指尖停在身体边上，"
     f"后三帧保持攥住、手指上的淡青高光一闪一闪（参考 Q_Burst_Hit、Q_Constraint、Q_Inner_Arm_Tubes）。**左右对称**，"
     f"中间身体位置留空（{HERO}）。",
     f"{CH} and {SM} and {WI}",
     f"a GIANT CHEMTECH HAND GRIPPING a figure, 6 frames, {LR} ({HERO}): 1 a white-pink flash 6 squares at its middle; 2 "
     "two glowing rose-pink fingers on each side of the figure (each 3 squares thick, 10 long) reaching in, mirrored; 3 "
     "the fingers curled round its waist and chest from both sides, their tips stopping at the figure's outline (the "
     "middle 12 squares stay empty), pink sparks; 4-6 the grip held (nearly the same frames), pale cyan-white highlights "
     "moving along the fingers.",
     row(6, 26, 32) + "; centered across, the figure's feet 2 squares above the cell's bottom row."),
    ("q_fling", "Q 甩人：被拽着甩出去的一瞬间（目标身上，跟随），4 帧",
     "view_effects `league_renata_q_fling`（跟随，画在人物上面；左右对称）", "22 × 28",
     "被拽着甩过来的一瞬间：目标两边各一道玫红的弧形气流（像被猛地一拽带起的风），脚下扬起一团酒红的烟尘（参考 W_speed_blur、"
     "Q_GroundSmoke02、Q_Smoke_Erode）。**左右对称**，中间身体位置留空。",
     f"{CH} and {SM} and {WI}",
     f"a VIOLENT YANK round a figure, 4 frames, {LR} ({HERO}): 1 a white-pink flash 4 squares at its middle; 2 a curved "
     "rose-pink swoosh arc on each side of the figure (each 3 squares thick, 16 tall, bowing outward, mirrored), "
     "wine-pink dust puffs at its feet; 3 the arcs further out and thinner with pale cyan glints, the dust spreading; 4 "
     "the arcs breaking into pink streaks, the dust fading.",
     row(4, 24, 30) + "; centered across, the figure's feet (the dust) 2 squares above the cell's bottom row."),
    ("q_land", "Q 落地：被甩的人砸到地上（地上，不跟随），6 帧", "view_effects `league_renata_q_land`（不跟随，画在人物下面；左右对称）",
     "30 × 14",
     "被甩出去的人砸到地上：地面一闪，一圈玫红的冲击环往外扩（从斜上方看的扁椭圆，约 28 格宽），两边扬起酒红到玫红的烟尘，地上留下几道"
     "发光的裂纹，慢慢散去（参考 Q_GroundSmoke02、Q_Ground_Light、Q_Radial_Erosion、Q_Smoke_Scroll）。**左右对称**。",
     f"{CH} and {WI}",
     f"a CRASH LANDING on the ground, 6 frames, {LR}: 1 a white-pink flash on the ground (an ellipse 10 wide, 3 tall); 2 a "
     "rose-pink shock ring (an ellipse 18 wide, 5 tall) and wine-pink dust puffs thrown up on both sides (6 squares "
     "tall); 3 the ring 28 wide and 8 tall, the dust at its highest, short glowing pink cracks on the ground at "
     "mirrored places; 4 the ring thinner and fading, the dust spreading low; 5 the dust settling, the cracks glowing "
     "faintly; 6 the last dust wisps.",
     row(6, 30, 16) + "; centered across, the ring's middle 5 squares above the cell's bottom row."),
    ("q_crash_hit", "Q 落地命中（目标身上），4 帧", "view_effects `league_renata_q_crash_hit`（跟随，画在人物上面；左右对称）", "12",
     "被砸中：一团玫红的冲击炸开（白芯），四道短短的碎片光斜着往外射（参考 Q_Burst_Hit、R_land_splash2）。**左右对称**。约 12 格。",
     f"{CH} and {WI}",
     f"an IMPACT on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a rose-pink impact burst 10 squares (white core) "
     "with 4 short white-pink shards shooting out diagonally at mirrored places; 3 the burst 12 squares, the shards "
     "further, wine-pink dust; 4 fading dust and sparks.",
     row(4, 14, 14) + CENTER),
    # ---- W Bailout (fired by the passive controller)
    ("w_cast", "W 及时救难：给队友打一针（队友身上，跟随），6 帧", "view_effects `league_renata_w_cast`（跟随，画在人物上面；左右对称）",
     "28 × 34",
     f"她给陷入危险的队友打一针：队友脚下冒出一圈**品红紫色的化学烟**，烟顺着身体两侧往上卷，几道玫红的小闪电噼啪闪，两边各两道淡青色的"
     f"风线往上冲（加速）（参考 W_Smoke_Shape、W_Smoke_Shape_03、W_Lightning、W_Wind、W_Hand_Glow）。**左右对称**，"
     f"中间身体位置留空（{HERO}）。",
     f"{VI} and {CH} and {SM}",
     f"a CHEMTECH STIMULANT BURST round a figure, 6 frames, {LR} ({HERO}): 1 a magenta-violet smoke ring bursting on the "
     "ground round the feet (an ellipse 18 wide, 4 tall) with a white-pink flash at its front middle; 2 magenta-violet "
     "smoke puffs (each 6-8 squares, lighter rims) rising on both sides of the figure to its waist, 2 short rose-pink "
     "lightning zigzags at mirrored places; 3 the smoke up to its shoulders, curling outward, 2 pale cyan wind streaks "
     "(1 square wide, 6 long, slanting up and out) on each side; 4 the smoke at its widest (26 squares across), the "
     "lightning crackling at head height on both sides; 5 the smoke thinning into rose-pink flakes rising; 6 a few pink "
     "flakes and cyan glints.",
     row(6, 28, 36) + "; centered across, the figure's feet 3 squares above the cell's bottom row."),
    ("w_buff", "W 期间：队友脚下的增益光环（队友身上，循环），4 帧", "view_buffs `league_renata_w_buff`（跟随，画在人物下面；左右对称）",
     "22 × 10",
     "救难期间队友脚下：一圈品红紫色的化学光环（从斜上方看的扁椭圆，约 20 格宽 5 格高，内圈玫红、一抖一抖），光环两头冒着小烟，几片玫红的"
     "小薄片往上飘，两边各一道淡青的风线（参考 W_WobbleLine、W_Flakes、W_Glow_Noise、W_Wind）。**左右对称**，4 帧无缝循环。"
     "画在人物下面，中间会被人挡住。",
     f"{VI} and {CH} and {SM}",
     f"a CHEMTECH AURA ON THE GROUND under a figure, 4 frames, a seamless loop, {LR}: a ring of magenta-violet chemical "
     "light on the ground (an ellipse 20 squares wide and 5 tall, 1-2 squares thick, a wobbling rose-pink inner edge), "
     "small smoke curls rising from its left and right ends, 2-3 rose-pink flakes (1-2 squares) drifting up above the "
     "ring at mirrored places (each frame a little higher), a pale cyan wind streak (1 square wide, 4 tall) at each "
     "side; the ring's brightest squares moving round it from frame to frame (mirrored).",
     row(4, 22, 12) + "; centered across, the ring's middle 3 squares above the cell's bottom row."),
    ("w_save", "W 结束：队友回一口血（队友身上，跟随），6 帧", "view_effects `league_renata_w_save`（跟随，画在人物上面；左右对称）",
     "24 × 38",
     f"救难结束时队友回血：脚下一圈玫红白光亮起，玫红的小薄片和淡青白的光点沿身体两侧往上升，最后在头顶散成一圈金色的小光点"
     f"（参考 W_Flakes、W_Glow_Noise、Z_Mote、Z_Flecks_02）。**左右对称**，中间身体位置留空（{HERO}）。",
     f"{CH} and {SM} and {GO}",
     f"a RESTORING SURGE round a figure, 6 frames, {LR} ({HERO}): 1 a white-pink ring lighting on the ground round the feet "
     "(an ellipse 16 wide, 4 tall); 2 rose-pink flakes and pale cyan sparkles (1-2 squares) rising on both sides of the "
     "figure to its knees; 3 the sparkles at its waist, the ring brighter; 4 the sparkles at its shoulders, a soft "
     "white-pink glow line up each side; 5 the sparkles above its head turning into gold motes; 6 a few gold and pink "
     "motes fading above the head.",
     row(6, 24, 40) + "; centered across, the figure's feet 3 squares above the cell's bottom row."),
    # ---- R Hostile Takeover
    ("r_cast", "R 恶意收购：召出机甲、喷出化学毒气（她身上，画在她下面），6 帧",
     "view_effects `league_renata_r_cast`（她身上播一次，跟随，画在她和机甲下面；左右对称；大图表）", "64 × 30",
     f"她召出机甲开大的一瞬间：脚下一圈玫红光环亮起，机甲往两边喷出大团**玫红化学毒气**，贴着地面往外滚，地上一圈冲击环往外扩，最后剩一层"
     f"薄薄的毒雾（参考 R_FlareOmni、R_Groundsmoke、R_Reset_Ground、R_Smoke_Strong、R_OilySmoke_erode）。**左右对称**，"
     f"中间她和机甲的位置只有地上的光环（{MECH}；整张画在她下面，被她挡住的地方看不见）。",
     f"{CH} and {WI} and {SM}",
     f"CHEMTECH GAS VENTING round a big figure, 6 frames, {LR} ({MECH}): 1 a white-pink flare 8 squares on the ground under "
     "the figure and a rose-pink ring on the ground round the feet (an ellipse 24 wide, 6 tall); 2 rose-pink gas clouds "
     "(8-10 squares each, lighter rims) bursting out low on both sides of the figure; 3 the gas rolling outward along "
     "the ground to 50 squares across, up to 14 squares tall at the sides, a thin shock ring on the ground 44 wide and "
     "10 tall; 4 the gas clouds at their widest (62 squares across), lower; 5 the gas thinning into wine-pink mist on "
     "the ground; 6 a few fading wisps.",
     row(6, 64, 32) + "; centered across, the figure's feet (the ground ring's middle) 6 squares above the cell's bottom row."),
    ("r_wave", "R：涌出去的化学毒气浪（飞行，循环），4 帧",
     "view_projectiles `league_renata_r_wave`（朝目标飞，画面随方向转；上下对称；大图表）", "18 × 32",
     "从机甲前面涌出的一大波**玫红化学毒气浪**往前推（从上往下看）：一道往前鼓的弧形浪头（约 32 格高，上下对称），浪头边缘最亮"
     "（白到淡青白，再到亮玫红），后面是翻滚的玫红到酒红的毒气云，往后拖约 10 格，几滴药剂往后甩（参考 R_Wave、R_Wave_Edge、"
     "R_Wave_Texture、R_Smoke_Strong、R_Groundsmoke、R_Puddles）。**朝右飞，上下对称**。",
     f"{CH} and {SM} and {WI}",
     f"a WAVE OF CHEMTECH GAS rolling to the RIGHT seen from above, 4 frames, a seamless loop, {TB}: a crescent wave front "
     "bulging forward (32 squares from top to bottom, 6 squares deep at its middle, its convex edge facing right), the "
     "front edge brightest (white and pale cyan rim squares, then bright rose-pink), behind it billowing rose-pink and "
     "wine-pink gas clouds 10 squares deep with lighter rims, drops of pink goo trailing behind at mirrored places; the "
     "clouds churning from frame to frame.",
     row(4, 20, 34) + "; the wave front's middle 1 square from the RIGHT edge, vertically centered."),
    ("r_hit", "R 命中：被毒气浪扫中、陷入狂暴（目标身上，跟随），6 帧",
     "view_effects `league_renata_r_hit`（跟随，画在人物上面；左右对称）", "18 × 20",
     "被毒气浪扫中、陷入狂暴：一团玫红的毒气裹住目标的头和肩，几道玫红的小闪电往外噼啪，最后毒气往上散开（参考 R_Lightning02、R_Whisp、"
     "R_Mark_distort_RGBA、R_Smoke_Strong）。**左右对称**，中间脸的位置淡一些。导入时 Claude 把格子中间放到头部。",
     f"{CH} and {WI} and {SM}",
     f"CHEMTECH GAS ENGULFING a unit's head, 6 frames, {LR}: 1 a white-pink flash 5 squares; 2 rose-pink gas swirling round "
     "the head and shoulders (a ring of puffs 16 squares wide, lighter rims), the middle 8 squares left faint; 3 the gas "
     "thicker, 4 short rose-pink lightning zigzags crackling out at mirrored places; 4 the lightning brighter (white "
     "cores); 5 the gas thinning into wisps rising; 6 fading wisps.",
     row(6, 20, 22) + "; centered in every cell (the cell's middle is the head)."),
    ("r_berserk", "R 狂暴中：头顶的小毒气云（目标身上，循环），4 帧",
     "view_buffs `league_renata_r_berserk`（跟随，头顶上方；左右对称）", "14 × 10",
     "狂暴期间目标头顶：一小团翻滚的玫红毒气云（约 12 格宽 6 格高），云下两边各一道小闪电噼啪闪（左右对称），表示被控制"
     "（参考 R_Lightning02、R_Whisp、Z_Sparks）。**左右对称**，4 帧无缝循环。导入时 Claude 把它放到头顶上方。",
     f"{CH} and {WI}",
     f"a SMALL CHEMTECH STORM CLOUD hovering over a head, 4 frames, a seamless loop, {LR}: a churning rose-pink gas cloud "
     "12 squares wide and 6 tall (lighter rims, a few wine-pink shadow squares at its bottom), a short rose-pink "
     "lightning zigzag (1 square wide, 4 tall, white core) under its left and right ends (mirrored); each frame the "
     "cloud's puffs shifting, the lightning on in frames 1 and 3 and off in 2 and 4.",
     row(4, 16, 12) + CENTER),
    ("r_lash", "R 狂暴发作：被控制的人朝身边自己人乱打（地上，不跟随），6 帧",
     "view_effects `league_renata_r_lash`（不跟随，画在人物下面；左右对称）", "50 × 14",
     "狂暴的敌人朝身边自己人乱打一下：脚下炸开一圈玫红的冲击环（从斜上方看的扁椭圆，约 50 格宽），环上跳着几道玫红的小闪电（左右对称），"
     "很快散去（参考 Shockwave01b、R_Grid_Edges、R_Lightning02、R_Puddles）。**左右对称**。",
     f"{CH} and {SM}",
     f"a BERSERK SHOCKWAVE on the ground, 6 frames, {LR}: 1 a white-pink flash on the ground (an ellipse 10 wide, 3 tall); "
     "2 a rose-pink ring (an ellipse 24 wide, 6 tall, 1-2 squares thick); 3 the ring 40 wide and 10 tall, 4 short pink "
     "lightning zigzags standing on it at mirrored places; 4 the ring 50 wide and 13 tall, thinner, the lightning "
     "fading; 5 the ring breaking into pink dashes; 6 fading pink specks.",
     row(6, 52, 16) + "; centered across, the ring's middle 7 squares above the cell's bottom row."),
    ("r_lash_hit", "R 狂暴发作命中（目标身上），4 帧", "view_effects `league_renata_r_lash_hit`（跟随，画在人物上面；左右对称）", "12",
     "被狂暴的同伴打中：两道交叉的玫红爪痕（X 形，白芯），一圈酒红的小火星（参考 R_ErosionShapes01、Z_Sparks）。**左右对称**。约 12 格。",
     f"{CH} and {WI}",
     f"a BERSERK STRIKE on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 two crossing rose-pink slash marks forming "
     "an X 10 squares wide (white cores, mirrored); 3 the X 12 squares, wine-pink sparks flying out at mirrored places; "
     "4 the X fading into sparks.",
     row(4, 14, 14) + CENTER),
]
BIG_FX = ("r_cast", "r_wave")
BAKED = ("a_flash",)                     # drawn into her own frames by rig_renata.py, not a sheet tag
NAME = "renata_fx_pack"
# why an effect is drawn again (a redraw pack, --only): what the delivery measured at game size
REDO = {}
GROUPS = [
    ("a_shot a_flash a_hit", ["Renata_Base_BA_Bullet_Glow", "Renata_Base_BA_Beam_01", "Renata_Base_BA_Smoke_Trail",
                              "Renata_Base_BA_Flash_sharp", "Renata_BA_Tar_Flare", "Renata_BA_Hit_Lens_Flare"]),
    ("p_mark p_pop", ["Renata_Base_P_Rainbow_Flash", "Renata_P_Puddle_Goop", "Renata_Base_P_SmokeTrail",
                      "Renata_Base_Q_Burst_Hit", "Renata_Base_Z_Flecks_02"]),
    ("e_missile", ["Renata_Base_E_Comet", "Renata_Base_E_Missile_Head_2", "Renata_Base_E_Shimmer_Trail",
                   "Renata_Base_E_Ribbon_01", "Renata_Base_E_Cas_Mis_Trail"]),
    ("e_boom e_hit e_slow", ["Renata_Base_E_Burst_Hit", "Renata_Base_E_Mis_AoE_Wind", "Renata_Base_E_LeadingEdge_Ring",
                             "Renata_Base_E_shockwave", "Renata_Base_E_Puddle_Mask", "Renata_Base_E_Bubble_01"]),
    ("e_shield", ["Renata_Base_E_Shield_Bubble", "Renata_Base_E_Shield_Edges", "Renata_Base_E_Shield_Front_1",
                  "Renata_Base_E_Bubble_01"]),
    ("q_hand q_hit", ["Renata_Base_Q_Avatar_Mask", "Renata_Base_Q_Inner_Arm_Tubes",
                      "Renata_Base_Q_Inner_Arm_Tubes_Gradient", "Renata_Base_Q_Constraint", "Renata_Base_Q_Burst_Hit"]),
    ("q_fling q_land q_crash_hit", ["Renata_Base_W_speed_blur", "Renata_Base_Q_GroundSmoke02",
                                    "Renata_Base_Q_Ground_Light", "Renata_Base_Q_Radial_Erosion",
                                    "Renata_Base_Q_Smoke_Scroll", "Renata_Base_R_land_splash2"]),
    ("w_cast w_buff w_save", ["Renata_Base_W_Smoke_Shape", "Renata_Base_W_Smoke_Shape_03", "Renata_Base_W_Lightning",
                              "Renata_Base_W_Wind", "Renata_Base_W_Flakes", "Renata_Base_W_WobbleLine"]),
    ("r_cast", ["Renata_Base_R_FlareOmni", "Renata_Base_R_Groundsmoke", "Renata_Base_R_Reset_Ground",
                "Renata_Base_R_Smoke_Strong", "Renata_Base_R_OilySmoke_erode"]),
    ("r_wave", ["Renata_Base_R_Wave", "Renata_Base_R_Wave_Edge", "Renata_Base_R_Wave_Texture",
                "Renata_Base_R_Smoke_Strong", "Renata_Base_R_Groundsmoke", "Renata_Base_R_Puddles"]),
    ("r_hit r_berserk", ["Renata_Base_R_Lightning02", "Renata_Base_R_Whisp", "Renata_Base_R_Mark_distort_RGBA",
                         "Renata_Base_Z_Sparks", "Renata_Base_R_Smoke_Strong"]),
    ("r_lash r_lash_hit", ["Renata_Base_Shockwave01b", "Renata_Base_R_Grid_Edges", "Renata_Base_R_Lightning02",
                           "Renata_Base_R_ErosionShapes01", "Renata_Base_Z_Sparks"]),
    ("colours", ["Renata_Base_Gradients", "Renata_Base_Q_Inner_Arm_Tubes_Gradient", "Renata_Base_R_Puddles",
                 "Renata_Base_W_Smoke_Shape", "Renata_Base_Z_HoneyStrands_2x2"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what, where a picture leaves her: 1x px from the pivot or
# None) - the cyan cross is her standing point, the yellow one that place (tools/kit/build_renata.py's release ticks)
SHOTS = [("attack", 3, "a_shot：子弹从枪口射出\na_flash 画在枪口", (24.5, -4.5)),
         ("skill", 3, "e_missile：两枚飞弹\n从机械手射出", (13.5, -13.0)),
         ("skill2", 3, "q_hand：化学之手\n从机械手射出", (16.5, -10.5)),
         ("skill2_fling", 3, "把抓住的人往身后甩\nq_fling 在那人身上", None),
         ("skill_w", 2, "W：抬手给队友打针\nw_cast 在队友身上", None),
         ("ult", 2, "r_cast：召出机甲\n画在她和机甲下面", None),
         ("ult", 4, "r_wave：毒气浪\n从她身前往前涌", None),
         ("hit", 2, "（参考）受击", None)]


def ref_sheet(path):
    S, LW = 180, 190
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                sys.exit(f"missing reference {p}")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            if im.width > 6 * im.height:                     # a colour bar: stretched so its shades read
                im = im.resize((im.width, S // 4), Image.NEAREST)
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Renata_Base_", "").replace("Renata_", "")[:26],
                   fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    anims = json.load(open(lp(SHEET + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(SHEET + "#sheet.png")).convert("RGBA")
    out = []
    for fr in anims[tag]["frames"]:
        r = fr["data"]
        out.append(np.asarray(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))))
    return out


def trim(f):
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    import tfm2_ase as T
    figs = [trim(sheet_frames("idle")[0])]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    figs.append(trim(k))
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
    d.text((8, 36), f"烈娜塔 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, out in SHOTS:
        raw = sheet_frames(tag)[k - 1]
        f = np.pad(raw, ((PAD, PAD), (PAD, PAD), (0, 0)))
        cx, cy = PAD + raw.shape[1] / 2, PAD + raw.shape[0] / 2      # the pivot (the frame's centre), pixel edges
        ys, xs = np.nonzero(f[..., 3] > 0)
        pts = [(cx, cy + FEET, (0, 255, 255, 255))]                  # her standing point, on the ground
        if out:
            pts.append((cx + out[0] + 0.5, cy + out[1] + 0.5, (255, 230, 0, 255)))
        x0 = int(min(xs.min(), *(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), *(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), *(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), *(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 240), sub.shape[0] * Z + 42), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 42))
        d = ImageDraw.Draw(im)
        for px, py, col in pts:
            X, Y = int((px - x0) * Z), int((py - y0) * Z) + 42
            d.line([(X - 10, Y), (X + 10, Y)], fill=col, width=2)
            d.line([(X, Y - 10), (X, Y + 10)], fill=col, width=2)
        d.multiline_text((4, 2), f"{tag} {k}  {what}", fill=(255, 255, 255, 255), font=font, spacing=2)
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
    """Her idle and the ult's machine as the game shows them (the hd frames: 1.5 fine squares a game px), at 4x."""
    tiles = [trim(sheet_frames("hd_idle")[0]), trim(sheet_frames("hd_ult")[3])]
    H = max(t.shape[0] for t in tiles)
    W = sum(t.shape[1] for t in tiles) + 12
    can = np.zeros((H, W, 4), np.uint8)
    x = 0
    for t in tiles:
        can[H - t.shape[0]:, x:x + t.shape[1]] = t
        x += t.shape[1] + 12
    img = Image.new("RGBA", (W * 4, H * 4), (104, 112, 72, 255))
    img.alpha_composite(Image.fromarray(np.repeat(np.repeat(can, 4, 0), 4, 1)))
    img.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 炼金男爵 烈娜塔·戈拉斯克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/renata_idle.png` 左边：3/4 正面朝右的女士，黑紫长发、银色面罩、白色短披肩、"
      f"深藏青马甲、白色喇叭裤，画面左边那只手是金色机械臂，手枪插在另一边胯上；右边是她开大招召出的金红大机甲——**机甲已经画进她的大招动作里，不用画**）。"
      f"她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），"
      f"不用画成高清（只有 `a_flash` 枪口火光例外，见那一条）。")
    a("> - 请把这个压缩包解压到**一个新的文件夹**，只用这个包里的文件（不要用以前烈娜塔模型包、走路包里的图）。")
    a("> - 大小对照 `design/renata_size.png`：她的待机（游戏格子）放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/renata_shots.png`：定稿动作（游戏格子，4 倍），**青色十字是她的站位点，黄色十字是特效出来的地方**（枪口、机械手）；每张写了特效从哪里出来。"
      "**E 和 Q 都从她的金色机械手往前射出**（待机时垂在画面左边，出招时甩到身前），普攻从另一只手的手枪射出。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里烈娜塔自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版（最后一行是原版的颜色条）：**她的化学药剂是玫红色**（从深酒红到白芯，**最亮的地方带一点淡青白**），"
      "**W 的烟偏品红紫**，**金色只做点缀**（彩虹光环、回血的光点）。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_shot`、`e_missile`、`q_hand`、`r_wave` 都画成朝右，**上下对称**（往左时会上下翻）。"
      "`a_flash` 画进她自己的动作帧（跟着她翻面），也画成朝右、上下对称。其余所有画面（打中、身上、脚下、地上、头顶）都要**严格左右对称**"
      "（逐格对称，游戏不会给它们镜像）。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 15]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。上一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `renata_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张一条：`name`、`file`、`frames`、"
      "`cell_1x` = [宽, 高]、`symmetry` = `top_bottom` 或 `left_right`）和生图原稿 `raw/`，"
      f"打包成 `{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「物尽其用」 | 手枪射出化学子弹；打中敌方英雄挂上印记，队友在旁边打它时印记炸开 | `a_shot` · `a_flash` · `a_hit` · `p_mark` · `p_pop` |")
    a("| 技能 1 = E「忠诚激励」 | 机械手射出两枚并排的化学飞弹，碰到敌人在落点炸开、减速；飞弹经过的队友得到护盾 | `e_missile` · `e_boom` · `e_hit` · `e_slow` · `e_shield` |")
    a("| 技能 2 = Q「铁腕竞合」 | 机械手射出化学之手，抓住第一个敌人定身，再把它甩过她身边砸到地上 | `q_hand` · `q_hit` · `q_fling` · `q_land` · `q_crash_hit` |")
    a("| 被动自动放的 W「及时救难」 | 给陷入危险的队友打一针：加攻速移速、不会阵亡，结束时回血 | `w_cast` · `w_buff` · `w_save` |")
    a("| 大招「恶意收购」 | 召出机甲，放出一大波化学毒气浪，扫中的敌方英雄陷入狂暴：不能攻击她这边、不能放技能，还会朝身边自己人乱打 | "
      "`r_cast` · `r_wave` · `r_hit` · `r_berserk` · `r_lash` · `r_lash_hit`（机甲已在她的动作里） |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、毒气、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("玫红化学药剂（主色）", CHEM), ("淡青白（最亮处的彩光）", SHIM), ("品红紫（W 的烟）", VIOL),
                        ("金色（只做点缀）", GOLD), ("酒红（烟尘、毒气的暗部）", WINE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 55000，"
      "E 爆炸半径 12000，Q 落地半径 14000，R 毒气浪宽 28000、长 100000，狂暴发作半径 25000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `renata_fx_{name}.png`：{title}\n")
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
        a(f"| `renata_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_renata_fx`（小的）和 `league_renata_big`（{'、'.join(BIG_FX)}），"
      "tag = 名字（build_renata.py 的 views）。")
    a("- `a_flash` 不进表：rig_renata.py 按她的细格子把它画进 attack 第 3、4 帧的枪口（1 倍时枪口在站位点前 24.5、上 4.5）。")
    a("- 投射物 `a_shot`、`e_missile`、`q_hand`、`r_wave` 画面朝方向转；`e_boom`、`q_land`、`r_lash` 不跟随（落点 / 地上的晚播画面，红色方规则）；"
      "`q_land`、`r_lash`、`r_cast`、`w_buff`、`e_slow` 画在人物下面（z -1；`r_lash` 在 build_renata.py 里还是 2，导入时改）。"
      "`p_mark`、`r_berserk` 放到头顶上方，`r_hit` 的格子中间放到头部。")
    a("- 用 `pixel_1x/` 切格（import_swain_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；"
      "量每张的亮度（平均 / 90% 分位）和包里其他英雄比。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="renata_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "renata_packs"), help="folder for the zip")
    a = ap.parse_args()
    global NAME
    NAME = a.name
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/rn/fx_ref_rn.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "renata_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "renata_size.png"))
    shots_sheet(os.path.join(out, "design", "renata_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"renata_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
