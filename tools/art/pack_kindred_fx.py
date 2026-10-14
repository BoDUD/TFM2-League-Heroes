#!/usr/bin/env python3
"""Build kindred_fx_pack.zip: step 3 of Kindred's sprite - Codex draws her effects (tools/art/pack_nilah_fx.py's way:
effects at game pixels, plus pictures drawn into her own dense frames).

    python tools/art/pack_kindred_fx.py [--no-zip] [--out DIR] [--only a_hit,e_bite --name kindred_fx_redo_pack]

The pack (%LOCALAPPDATA%/Temp/kn_work/fx/kindred_fx_pack, zipped into --out, default dist/kindred_packs) holds
PROMPTS.md (also written to assets/source/kindred/PROMPTS_FX.md), design/kindred_designs.png (the front design, the side
design and the Wolf's profile at 3x), design/kindred_size.png (her 1x idle at 4x on the arena colour with the feet
line, a 10-px ruler and the base fighter), design/kindred_shots.png (finished action frames, 1x at 4x, the point each
picture on her starts from as a cyan cross), bake/kindred_bake_<name>_<n>.png (the frame a picture is drawn INTO: her
finished dense frame - the hd_ tag of league/champions/league_kindred, 2.86 squares a game pixel - faded on a guide
canvas at 6 px a square, the points it starts from as crosses) and refs/lol_fx_ref.png (League's own particle textures
for Kindred, grouped by the effect of ours they inform; Riot's art, local only: it reads %LOCALAPPDATA%/Temp/kn_work/
fxref, extracted from Kindred.wad.client's base skin by Temp/kn_work/fx/fx_ref_kn.py).
The effects are the views the kit binds (tools/kit/build_kindred.py: view_projectiles a_arrow, q_arrow, e_arrow;
view_effects a_hit, q_hit, q_dash, e_hit, e_mark, e_bite, w_zone, w_bite, r_zone, r_heal; view_buffs p_stack) and the
pictures drawn into her frames at import (BAKE): the client mirrors her frames with her facing and never an effect
picture, so whatever has a front and a back on her - the arrow on the string, the loosing flash at the bow, Q's leap
trail, the light off the raised bow in R, the Wolf's smoke called up in W - rides in the frames (art-spec, league_nilah).
League's colours: Lamb's spirit light (white cores, pale cyan to sky blue: her arrows, Q, R), the Wolf's dread (pale
lilac to deep indigo smoke: E, W, the bites) and the mark's cyan-and-violet swirl. Light and smoke get no outline.
Red side: projectiles symmetric top to bottom (they are turned to their flight); pictures on a unit, on the ground and
the buffs symmetric left to right - but for the mark's swirl (no front or back; the game draws it as it is).
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
import import_kindred_strips as I  # noqa: E402
import ppu_hd as P  # noqa: E402

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "kn_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "kindred", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_kindred")
HD = os.path.join(I.SRC, "hd")
PRE = chr(92) * 2 + "?" + chr(92)
FEET = 11
ORIG_PPU = 154 / 34                 # rig_kindred.PPU: the import canvas' squares a game pixel
HD_PPU = P.PPU["kindred"]           # her finished dense frames (Zeri's density)
K = HD_PPU / ORIG_PPU
PY = I.SOLE + 1 - FEET * ORIG_PPU   # the import canvas' pivot row (rig_kindred.down)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


LAMB = "#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2"      # Lamb's spirit light: white core, pale cyan to blue
WOLF = "#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43"      # the Wolf's dread: pale lilac to deep indigo smoke
MARK = "#FFFFFF, #6AE3EA, #39B4F7, #2E78F2, #8E82F7, #5C44DE"      # the mark's swirl: cyan and violet bands
HEAL = "#FFFFFF, #E1FBFD, #C0E6FC, #89F7DD, #A6AAF8"               # R's respite: white, pale cyan, mint, lilac
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a "
        "white or pale core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, {px} px a square)"
LR_ = f"a Lamb spirit-light ramp ({LAMB})"
WR_ = f"a Wolf dread ramp ({WOLF})"
MR_ = f"a mark ramp ({MARK})"
HR_ = f"a respite ramp ({HEAL})"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
TB = "SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight)"
CENTER = "; centered in every cell."


def row(n, cw, ch, px=16):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * px, h=ch * px, cw=cw * px, ch=ch * px, px=px)


# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the arrows in flight (turned to their flight)
    ("a_arrow", "普攻灵箭（飞行中，循环），4 帧",
     "view_projectiles `league_kindred_a_arrow`（朝飞行方向转，画成朝右飞；上下对称）", "14 × 4",
     "羊灵射出的灵箭：一根细细的白色光箭，箭头是青白色的叶片形（参考 BA_Arrow_Tip），后面拖一小段淡青色的光迹（参考 BA_Trail_Wisp、BA_glow_mis）。"
     "朝右飞。**上下对称**。4 帧无缝循环（光迹闪一闪）。约 14 格长、4 格高。", LR_,
     f"a SPIRIT ARROW flying to the RIGHT, 4 frames, a seamless loop, {TB}: a thin white light shaft 8 squares long and 1 "
     "square thick, a pale cyan glow 1 square above and below it, a leaf-shaped white-cyan arrowhead 3 squares long "
     "pointing RIGHT, a wispy pale cyan trail 4 squares long behind; the trail flickers each frame.",
     row(4, 16, 6) + "; the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_arrow", "Q 乱箭之舞的箭（飞行中，循环），4 帧",
     "view_projectiles `league_kindred_q_arrow`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 5",
     "乱箭之舞一次射向最多 3 个目标的箭：比普攻的箭更亮更长，拖一条带亮点的青色光尾（参考 BA_Trail_Wisp、BA_Spark_cas）。"
     "朝右飞。**上下对称**。4 帧无缝循环。约 16 格长、5 格高。", LR_,
     f"a BRIGHT SPIRIT ARROW flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white light shaft 9 squares long, a "
     "pale cyan glow round it 1 square thick, a leaf-shaped white arrowhead 3 squares long pointing RIGHT, a tapering "
     "cyan light trail 5 squares long with 2 white motes; the motes move back along the trail each frame.",
     row(4, 18, 7) + "; the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("e_arrow", "E 横生惧意的箭（飞行中，循环），4 帧",
     "view_projectiles `league_kindred_e_arrow`（朝飞行方向转，画成朝右飞；上下对称）", "18 × 6",
     "横生惧意：羊灵射出带着狼灵恶意的箭——深紫色的箭身、淡紫色的芯、青白色箭头，箭身上缠着几缕深靛色的狼烟往后飘（参考 E_Muzzle_cas、"
     "W_wolf_smoke）。朝右飞。**上下对称**。4 帧无缝循环（烟一缕一缕往后飘）。约 18 格长、6 格高。", f"{WR_} and {LR_}",
     f"a DREAD ARROW flying to the RIGHT, 4 frames, a seamless loop, {TB}: a violet shaft 10 squares long with a pale lilac "
     "core, a white-cyan arrowhead 3 squares long pointing RIGHT, curls of dark indigo smoke 2 squares thick trailing 6 "
     "squares behind it, above and below alike; the curls drift back a square each frame.",
     row(4, 20, 8) + "; the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell."),
    # ---- hits on the target
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_kindred_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "灵箭射中：一团青白色的光炸开，4 片羽毛状的淡蓝光丝往外散（参考 BA_Hit_Feather、BA_flash_tar、BA_Flash_sharp）。**左右对称**。约 12 格。",
     LR_,
     f"a SPIRIT ARROW HIT, 4 frames, {LR}: 1 a white flash 4 squares across; 2 a pale cyan burst 8 squares across with a "
     "white core and 4 feather-shaped wisps at mirrored places; 3 the wisps flying out to 12 squares across; 4 a few "
     "fading motes.",
     row(4, 14, 14) + CENTER),
    ("q_hit", "Q 的箭打中（每个目标身上），4 帧", "view_effects `league_kindred_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "乱箭之舞射中：一个白亮的十字星光，周围一圈青色的小火花（参考 Q_hit_Sparks、BA_Flare）。**左右对称**。约 14 格。", LR_,
     f"a STAR-SPARK HIT, 4 frames, {LR}: 1 a white dot 3 squares; 2 a four-pointed white-cyan star 10 squares across; "
     "3 the star 14 squares across, 6 cyan sparks round it at mirrored places; 4 fading sparks.",
     row(4, 16, 16) + CENTER),
    ("e_hit", "E 横生惧意：打中、种下印记（目标身上），5 帧", "view_effects `league_kindred_e_hit`（跟随，画在人物上面；左右对称）", "18",
     "横生惧意的箭射中：一圈深紫色的环猛地往里收（参考 E_Ring_Cas），中间一闪青白光，几缕狼烟往外甩（参考 E_hit_Flare、W_Dark_flash）。"
     "**左右对称**。约 18 格。", f"{WR_} and {LR_}",
     f"a DREAD MARK HIT, 5 frames, {LR}: 1 a dark violet ring 18 squares across; 2 the ring snapping inward to 10 squares, "
     "a white-cyan flash 4 squares at the center; 3 the flash at its brightest, 6 curls of indigo smoke thrown out at "
     "mirrored places; 4 the smoke drifting, a small violet ring 6 squares; 5 fading wisps.",
     row(5, 20, 20) + CENTER),
    ("e_mark", "E 的狼之印记（目标头顶，跟着目标，每 1/3 秒重播一次），4 帧",
     "view_effects `league_kindred_e_mark`（跟随，画在人物上面；中间的漩涡不用对称）", "11 × 11",
     "被横生惧意标记的目标头顶浮着千珏的印记：一个青色和紫色相间的漩涡圆印（参考 P_Mark、P_full_mark、E_Stack_1/2/3），一闪一闪。"
     "**漩涡本身不用左右对称**（它没有前后，游戏两边画法一样），其他光点左右对称。4 帧要能接起来循环（每 1/3 秒重播一次）。画在格子中间，"
     "导入时 Claude 把它放到头顶。约 11 格。", MR_,
     "a SWIRL MARK, 4 frames, a seamless loop: a round swirl sigil 11 squares across - three curling bands (pale cyan, "
     "sky blue, violet) spiralling into a white center, a dark indigo rim 1 square thick only where the bands meet the "
     "outside - pulsing brighter (frame 2) and dimmer (frame 4), 2 tiny white glints at mirrored places beside it.",
     row(4, 14, 14) + CENTER),
    ("p_stack", "被动 千珏之印：得到一层印记（她头顶，1.5 秒，循环），4 帧",
     "view_buffs `league_kindred_p_stack`（跟随，画在人物上面；中间的漩涡不用对称）", "10 × 12",
     "千珏收下一层印记（击杀、助攻）：她头顶亮起漩涡印记，下面一道细细的光往上收（参考 P_Mark_activate_ring、P_collect_godlay、P_spark）。"
     "**漩涡本身不用左右对称**，其他左右对称。4 帧无缝循环。画在格子中间，导入时 Claude 放到她头顶。约 10 格宽、12 格高。", MR_,
     "a MARK GAINED, 4 frames, a seamless loop: a round swirl sigil 9 squares across (pale cyan, sky blue and violet "
     "bands spiralling into a white center) over a thin vertical beam of pale light 1 square wide and 3 squares tall "
     "under it, 4 white motes at mirrored places rising round it and taking turns to brighten.",
     row(4, 12, 14) + CENTER),
    # ---- the Wolf
    ("e_bite", "E 狼灵扑咬（被标记的目标身上，大），6 帧", "view_effects `league_kindred_e_bite`（BIG，跟随，画在人物上面；左右对称）", "28 × 32",
     "横生惧意的第三下之后狼灵扑上去咬：狼灵的头从正面画——白色的面具脸、两只发青光的眼睛、深紫色烟一样的鬃毛（参考 E_wolf_head、"
     "`design/kindred_designs.png` 里狼的样子），从目标头顶扑下来、张嘴、一口咬合，四周炸开深靛色狼烟。**左右对称**（正面的狼头）。"
     "约 28 格宽、32 格高。", f"{WR_} and {LR_}",
     f"a SPIRIT WOLF'S BITE seen from the FRONT, 6 frames, {LR}: 1 the Wolf's head small at the top of the cell - a pale "
     "bone-white mask face with two glowing cyan eyes, a mane of dark indigo smoke; 2 the head lunging down and larger "
     "(20 squares wide), jaws opening, fangs white; 3 the jaws wide open over the middle of the cell, the mane flaring out "
     "26 squares; 4 the jaws snapped shut at the middle, a burst of indigo smoke 28 squares across, a white-cyan flash "
     "between the fangs; 5 the head dissolving into smoke curls at mirrored places; 6 fading wisps and two eye glints.",
     row(6, 30, 34) + "; centered across, the bite (frame 4's jaws) at the middle of the cell."),
    ("w_bite", "W 狼灵狂热：狼灵在领域里咬中（目标身上），5 帧", "view_effects `league_kindred_w_bite`（跟随，画在人物上面；左右对称）", "18 × 18",
     "狼灵在自己的领域里每秒咬一口：一对深紫色的狼牙从上下两边合拢（正面看，像一张嘴合上），中间一闪，几缕狼烟（参考 W_wolf_hit_circle、"
     "W_wolf_smoke、W_Dark_flash）。**左右对称**。约 18 格。", f"{WR_} and {LR_}",
     f"a SNAPPING BITE seen from the FRONT, 5 frames, {LR}: 1 two rows of white fangs in dark indigo smoke, one at the "
     "top and one at the bottom of an open mouth 16 squares tall; 2 the jaws closing to 8 squares; 3 the fangs meeting at "
     "the middle, a white-cyan flash 6 squares, smoke 18 squares across; 4 smoke curls at mirrored places; 5 fading wisps.",
     row(5, 20, 20) + CENTER),
    # ---- on the ground
    ("q_dash", "Q 起跳点的尘烟（地上，留在原地），5 帧",
     "view_effects `league_kindred_q_dash`（画在人物下面，不跟随；左右对称、上下对称）", "24 × 8",
     "乱箭之舞跳开时地上留下的一圈淡淡的灵光尘烟：从斜上方看的扁椭圆，几片羽毛状的光往两边飘（参考 R_light_dust、BA_Hit_Feather）。"
     "**左右对称**、**上下对称**。约 24 格宽、8 格高。", LR_,
     f"a SPIRIT DUST PUFF on the ground seen from above at an angle, 5 frames, {LR} and top to bottom: 1 a pale cyan "
     "ellipse 10 squares wide and 3 tall; 2 a ring of pale dust 20 squares wide and 7 tall, white specks; 3 the ring 24 "
     "squares wide, 4 feather-like wisps drifting out at mirrored places; 4 the ring thinning; 5 a few fading specks.",
     row(5, 26, 10) + CENTER),
    ("w_zone", "W 狼灵狂热：狼灵的领域（地上，8.5 秒，大），10 帧",
     "view_effects `league_kindred_w_zone`（BIG，画在人物下面，不跟随，留在她放 W 的地方；左右对称、上下对称）", "120 × 46",
     "狼灵的狩猎场：地上一个从斜上方看的扁椭圆领域（半径 60 个游戏像素）——边上一圈深靛色、发着暗紫光的狼烟环（参考 W_area、W_Ring_mult），"
     "环里贴地飘着几缕狼烟（参考 W_ground_smoke、W_wolf_smoke），零星几点青色的光（狼灵的眼睛一闪）。要暗、要淡，不能挡住站在里面的人。"
     "**左右对称**、**上下对称**。第 1-2 帧出现（环从中间扩开），第 3-8 帧循环（烟在环上流动，但每帧都对称），第 9-10 帧消散。"
     "这张很大：按**每格 8 像素**画。", WR_,
     f"a WOLF'S HUNTING GROUND on the ground seen from above at an angle, 10 frames, {LR} and top to bottom: a flat "
     "ellipse 120 squares wide and 46 tall whose rim is a ring of dark indigo smoke 3-4 squares thick glowing violet on "
     "its inner edge, faint wisps of smoke curling low inside it, 4 tiny cyan glints at mirrored places; the inside stays "
     "mostly empty and dark-transparent (no fill). 1-2 the ring spreading out from a small ellipse at the center to full "
     "size; 3-8 a seamless loop, the smoke on the rim flowing round (mirrored in every frame), the glints taking turns; "
     "9-10 the ring breaking into smoke and fading.",
     row(10, 124, 50, px=8) + CENTER),
    ("r_zone", "R 羊灵生息：羊灵的庇护法阵（地上，4 秒，大），9 帧",
     "view_effects `league_kindred_r_zone`（BIG，画在人物下面，不跟随，留在她放大招的地方；中间的漩涡不用对称）", "100 × 38",
     "羊灵生息：地上一个从斜上方看的发光法阵（半径 50 个游戏像素）——一圈白亮的光环，环上对称的几个符文刻痕（参考 R_symbol_Light_01/02/03），"
     "中间一个青白色的漩涡（漩涡不用对称），环的边缘升起一圈细细的光墙（一根根竖着的光条，参考 R_cylinder、R_light_wall），光点往上飘"
     "（参考 R_light_dust）。法阵里的人不会死，所以要亮、要神圣，但中间人站的地方别涂满。第 1-2 帧法阵画出来（光环从中间扩开、符文亮起），"
     "第 3-6 帧循环（光墙和光点往上飘），第 7 帧一闪白光，第 8-9 帧消散（结束时给法阵里的人治疗）。这张很大：按**每格 8 像素**画。", HR_,
     "a HOLY CIRCLE on the ground seen from above at an angle, 9 frames, the ring, the runes, the light wall and the motes "
     "SYMMETRIC LEFT TO RIGHT square for square (only the swirl in the middle may turn): a flat ellipse 100 squares wide "
     "and 38 tall - a bright white-cyan ring 2 squares thick, 6 rune marks on it at mirrored places, a pale cyan swirl "
     "18 squares across at the center, a low wall of thin upright light streaks (1 square wide, 4-10 squares tall) rising "
     "along the ring's front and back edges, white motes floating up; the inside mostly empty. 1-2 the ring drawn out "
     "from the center, the runes lighting one pair at a time; 3-6 a seamless loop, the streaks and motes rising; 7 a "
     "white flash over the whole ring; 8-9 the circle fading.",
     row(9, 104, 44, px=8) + CENTER),
    # ---- the heal
    ("r_heal", "R 羊灵生息结束时的治疗（每个队友身上），6 帧", "view_effects `league_kindred_r_heal`（跟随，画在人物上面；左右对称）", "18 × 32",
     "法阵结束时法阵里的英雄回血：脚下一圈白光升起，两边几道淡青、薄荷色的光往上飘，羊毛一样软的小光团（参考 R_Heal_Flash、R_Heal_spark、"
     "W_heal_sparks、R_outside_light_up）。**左右对称**，中间人形位置留空（8 格宽、26 格高）。格子底部就是脚底。", HR_,
     f"a HEALING RISE round a figure, 6 frames, {LR}, the middle EMPTY (a clear upright area 8 squares wide and 26 tall): "
     "1 a white ellipse glow on the ground 14 squares wide at the bottom; 2 pale cyan and mint light streaks rising at "
     "both sides to 16 squares; 3 the streaks at their top (30 squares), soft round light puffs and white motes at "
     "mirrored places; 4 the light thinning, motes still rising; 5 a few motes; 6 the last glints.",
     row(6, 20, 34) + "; centered across, the ground glow on the cell's bottom row."),
]
# pictures drawn INTO her own frames, on her finished dense grid (the hd_ tags, 2.86 squares a game pixel): name, tag,
# frames, over / under her, title (zh), description (zh), ramps, the effect (en) per frame
BAKE_PX = 6                          # guide px a square: 256 x 170 squares (or 170 x 256) on Codex's 1536 x 1024
LAND = (256, 170, (110, 85))         # canvas squares, the pivot's square (her frame centred on it)
PORT = (170, 256, (85, 128))
BAKE = [
    ("a_nock", "attack", (2, 3), "over", "普攻：搭在弦上的灵箭（画进普攻第 2、3 帧，她拉满弓的时候）",
     "羊灵拉满弓时弦上搭着一支灵箭：从青色十字（拉弦的手、弦的顶点）穿过黄色十字（握弓的手、箭搭在弓上的地方），箭头伸出弓外几格。"
     "箭身是一根白色的光线，两边一圈淡青光，叶片形的青白色箭头，尾端两小片羽毛光。画在她**上面**。", LR_,
     {2: "a SPIRIT ARROW nocked on a drawn bow: a straight white light shaft 2 squares thick with a pale cyan glow 1 "
         "square each side, from the cyan cross (the drawing hand) through the yellow cross (the bow hand) and 12 squares "
         "beyond it, ending in a leaf-shaped white-cyan arrowhead 9 squares long and 7 tall pointing RIGHT; two pale "
         "feather wisps 5 squares long at the cyan cross.",
      3: "the same SPIRIT ARROW at full draw, a little brighter: the shaft 2 squares thick from the cyan cross through "
         "the yellow cross and 12 squares beyond it, the leaf-shaped arrowhead 9 squares long pointing RIGHT, 3 white "
         "motes 2 squares big along the shaft."}),
    ("a_loose", "attack", (4,), "over", "普攻：松弦的一闪（画进普攻第 4 帧）",
     "箭射出去那一下：握弓的手（黄色十字）前面炸开一团青白色的光，一道细长的光往**右**射出去（箭离弦），几点火花。画在她**上面**。", LR_,
     {4: "the LOOSE: a burst of white-cyan light 20 squares across centered 8 squares RIGHT of the yellow cross (the bow "
         "hand), a straight streak of white light 2 squares thick and 40 squares long shooting to the RIGHT from it, 4 "
         "cyan sparks 2-3 squares big flying off; nothing over her face."}),
    ("e_nock", "skill2", (2, 3), "over", "E 横生惧意：搭在弦上的狼烟之箭（画进 E 第 2、3 帧）",
     "射横生惧意前弦上搭着一支带狼烟的箭：深紫色箭身、淡紫色芯、青白色箭头，箭身上缠着深靛色的狼烟往上飘。从青色十字（拉弦的手）"
     "穿过黄色十字（握弓的手），箭头伸出弓外。画在她**上面**。", f"{WR_} and {LR_}",
     {2: "a DREAD ARROW nocked on a drawn bow: a straight violet shaft 3 squares thick with a pale lilac core, from the "
         "cyan cross (the drawing hand) through the yellow cross (the bow hand) and 12 squares beyond it, a white-cyan "
         "arrowhead 9 squares long and 7 tall pointing RIGHT, 3 curls of dark indigo smoke 3 squares thick rising off the "
         "shaft.",
      3: "the same DREAD ARROW at full draw: the shaft 3 squares thick from the cyan cross through the yellow cross and 12 "
         "squares beyond, the white-cyan arrowhead pointing RIGHT, the indigo smoke curls thicker and higher (up to 14 "
         "squares), a violet glow round the arrowhead."}),
    ("e_loose", "skill2", (4,), "over", "E 横生惧意：松弦（画进 E 第 4 帧）",
     "带狼烟的箭射出去：握弓的手（黄色十字）前面炸开一团深靛色的狼烟，中间一点青白光，一道深紫色的光往**右**射出去。画在她**上面**。",
     f"{WR_} and {LR_}",
     {4: "the DREAD LOOSE: a puff of dark indigo smoke 22 squares across centered 8 squares RIGHT of the yellow cross (the "
         "bow hand) with a white-cyan spark 5 squares big at its middle, a violet streak 3 squares thick and 40 squares "
         "long shooting to the RIGHT from it, smoke curls drifting up; nothing over her face."}),
    ("q_nock", "skill", (5,), "over", "Q 乱箭之舞：弦上扇开的三支灵箭（画进 Q 第 5 帧）",
     "跳完落地拉弓：弦上同时搭着三支灵箭，从青色十字（拉弦的手）出发扇开：中间一支穿过黄色十字（握弓的手），上下两支各偏 12 度，"
     "箭头都伸出弓外。画在她**上面**。", LR_,
     {5: "THREE SPIRIT ARROWS nocked together and fanned: three white light shafts 2 squares thick with pale cyan glows, "
         "all starting at the cyan cross (the drawing hand); the middle one through the yellow cross (the bow hand) and 12 "
         "squares beyond it, the other two 12 degrees above and below it, each ending in a leaf-shaped white-cyan "
         "arrowhead 8 squares long pointing RIGHT."}),
    ("q_loose", "skill", (6,), "over", "Q 乱箭之舞：三箭齐发（画进 Q 第 6 帧）",
     "三支箭同时射出去：握弓的手（黄色十字）前面一团青白光，三道细光往**右**扇形射出（中间一道平的，上下各一道斜 12 度）。画在她**上面**。", LR_,
     {6: "the VOLLEY: a burst of white-cyan light 18 squares across centered 8 squares RIGHT of the yellow cross (the bow "
         "hand), three white light streaks 2 squares thick and 40 squares long fanning out to the RIGHT from it (one "
         "level, one 12 degrees up, one 12 degrees down), cyan sparks 2-3 squares big; nothing over her face."}),
    ("q_trail", "skill", (3, 4), "under", "Q 乱箭之舞：跳跃时身后的灵光拖影（画进 Q 第 3、4 帧，画在她身后）",
     "乱箭之舞是一个灵巧的跳跃：她身后（**左下**方，跳起的地方）拖着一道淡淡的青白色灵光，几片羽毛状的光丝往后飘。从青色十字（她的后蹄）"
     "往**左下**拖出去，第 3 帧长、第 4 帧开始散。画在她**后面**（被她挡住的地方不用画）。", LR_,
     {3: "a GHOSTLY LEAP TRAIL behind the figure: a soft band of pale cyan and white spirit light 10 squares thick "
         "streaming from the cyan cross (her hind hooves) down and to the LEFT for 60 squares, toward the ground she "
         "jumped from, thinning to its end, 4 feather-shaped wisps 8 squares long and white motes along it.",
      4: "the TRAIL breaking up: the band 50 squares long from the cyan cross (her hind hooves) down and to the LEFT, its "
         "far half turning into feather wisps and fading motes."}),
    ("r_raise", "ult", (5,), "over", "R 羊灵生息：举起的弓上一闪（画进大招第 5 帧）",
     "羊灵把弓举向天空：弓的顶端（黄色十字）炸开一颗白亮的星光，几道短光芒，光点往下飘落到她身边（大招的法阵就在这一帧出现）。"
     "画在她**上面**，别挡住她的脸。", HR_,
     {5: "a RADIANT STAR at the yellow cross (the raised bow's top): a white four-pointed star 26 squares across with a "
         "pale cyan glow, 6 light rays 8 squares long, 10 white and mint motes 2-3 squares big falling below it on both "
         "sides of the bow; nothing over her face."}),
    ("w_call", "w_cast", (2,), "over", "W 狼灵狂热：举起的手里召来狼烟（画进 W 第 2 帧）",
     "羊灵举手召唤狼灵去狩猎：举起的手（青色十字）上方卷起一团深靛色的狼烟，烟里两点青色的狼眼一闪。画在她**上面**，别挡住她的脸。",
     f"{WR_} and {LR_}",
     {2: "a SUMMONING SWIRL above the cyan cross (the raised hand): curls of dark indigo smoke 3-4 squares thick, 28 "
         "squares across, rising and swirling up to 32 squares above the hand, a violet glow inside, two glowing cyan "
         "eyes 2 squares big in it; nothing over her face."}),
]
GROUPS = [
    ("arrows", ["Kindred_Base_BA_Arrow_Tip", "Kindred_Base_BA_Trail_Wisp", "Kindred_Base_BA_glow_mis",
                "Kindred_Base_BA_Spark_cas", "Kindred_Base_BA_Flash_sharp", "Kindred_Base_BA_Flare"]),
    ("hits", ["Kindred_Base_BA_Hit_Feather", "Kindred_Base_BA_flash_tar", "Kindred_Base_Q_hit_Sparks",
              "Kindred_Base_E_hit_Flare", "Kindred_Base_P_spark", "Kindred_Base_R_activate_spark"]),
    ("mark / E", ["Kindred_Base_P_Mark", "Kindred_Base_P_full_mark", "Kindred_Base_E_Stack_1", "Kindred_Base_E_Stack_2",
                  "Kindred_Base_E_Stack_3", "Kindred_Base_E_Ring_Cas"]),
    ("Wolf / W", ["Kindred_Base_E_wolf_head", "Kindred_Base_W_wolf_smoke", "Kindred_Base_W_ground_smoke",
                  "Kindred_Base_W_area", "Kindred_Base_W_wolf_hit_circle", "Kindred_Base_W_Dark_flash"]),
    ("R circle", ["Kindred_Base_R_symbol_Light_01", "Kindred_Base_R_symbol_Light_02", "Kindred_Base_R_symbol_Light_03",
                  "Kindred_Base_R_cylinder", "Kindred_Base_R_Rising_wall", "Kindred_Base_R_light_dust"]),
    ("R heal", ["Kindred_Base_R_Heal_Flash", "Kindred_Base_R_Heal_spark", "Kindred_Base_W_heal_sparks",
                "Kindred_Base_R_outside_light_up", "Kindred_Base_R_Activate_Halo", "Kindred_Base_P_collect_godlay"]),
]
# where the pictures on her start (tag, frame, what, marks: "feet" = her standing point on the soles' line, or
# [(dx, dy)] in game px from the pivot, x forward, y down; the soles 11 under it)
SHOTS = [("idle", 1, "p_stack：她头顶（站位点上方 27 格）", [(0, -27)]),
         ("skill", 3, "q_dash：起跳点（地上）", "feet"),
         ("w_cast", 2, "w_zone：领域中心（她脚下）", "feet"),
         ("ult", 5, "r_zone：法阵中心（她脚下）", "feet")]
# the import's points on its canvas (import_kindred_strips fix_bow, printed as "draw" and "fist": rows, columns of the
# COLS x ROWS canvas at ORIG_PPU) - the drawing hand on the string, the bow hand
DRAW = {"attack_2": (133, 180), "attack_3": (123, 169), "skill_5": (161, 167), "skill2_2": (150, 203),
        "skill2_3": (136, 224)}
FIST = {"attack_2": (130.9, 246.1), "attack_3": (125.0, 262.5), "attack_4": (124.5, 257.9), "skill_5": (148.0, 259.3),
        "skill_6": (141.2, 208.2), "skill2_2": (148.0, 273.9), "skill2_3": (140.8, 314.6), "skill2_4": (142.6, 284.9)}


def to_hd(rc, W, H):
    """An import-canvas point (row, col) -> its (x, y) on the finished dense frame (W x H, centred on the pivot)."""
    r, c = rc
    return W / 2.0 + (c + 0.5 - (I.PIV + 0.5)) * K, H / 2.0 + (r + 0.5 - PY) * K


def ref_sheet(path):
    S, LW = 180, 120
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
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Kindred_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


SHEETS = {}


def frames_of(tag):
    if not SHEETS:
        SHEETS.update(P.read_sheet(SHEET))
    return [a for a, _ in SHEETS[tag]]


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def designs(path):
    pics = [crop(np.asarray(Image.open(os.path.join(HD, f)).convert("RGBA")))
            for f in ("front.png", "side.png", "side_wolf.png")]
    H = max(p.shape[0] for p in pics)
    W = sum(p.shape[1] for p in pics) + 12 * (len(pics) - 1)
    both = np.zeros((H, W, 4), np.uint8)
    x = 0
    for p in pics:
        both[H - p.shape[0]:, x:x + p.shape[1]] = p
        x += p.shape[1] + 12
    Image.fromarray(np.repeat(np.repeat(both, 3, 0), 3, 1)).save(path)


def size_sheet(path):
    """Her 1x idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter."""
    import tfm2_ase as T
    fig = crop(frames_of("idle")[0])
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    kn = crop(np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA")))
    Z, pad = 4, 6
    W = pad + fig.shape[1] + pad + kn.shape[1] + pad
    top = max(fig.shape[0], kn.shape[0])
    img = Image.new("RGBA", (max(W * Z, 760), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
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
    d.text((8, 36), f"千珏 {fig.shape[1]}×{fig.shape[0]} 格（连弓和狼灵），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """Finished action frames (1x) at 4x, each picture's starting point as a cyan cross."""
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, marks in SHOTS:
        f = np.pad(frames_of(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px, py = f.shape[1] / 2.0, f.shape[0] / 2.0
        pts = [(px, py + FEET)] if marks == "feet" else [(px + dx, py + dy) for dx, dy in marks]
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0 = int(min(xs.min(), min(p[0] for p in pts))) - 3
        x1 = int(max(xs.max(), max(p[0] for p in pts))) + 4
        y0 = int(min(ys.min(), min(p[1] for p in pts))) - 3
        y1 = int(max(ys.max(), max(p[1] for p in pts))) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 300), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        for mx, my in pts:
            cx, cy = int((mx - x0) * Z), int((my - y0) * Z) + 24
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


def bake_points(name, tag, k, a):
    """{"cyan": (x, y), "yellow": (x, y)} on the dense frame a (its pixels) for this picture."""
    H, W = a.shape[:2]
    key = f"{tag}_{k}"
    pts = {}
    if key in DRAW:
        pts["cyan"] = to_hd(DRAW[key], W, H)
    if key in FIST:
        pts["yellow"] = to_hd(FIST[key], W, H)
    op = a[..., 3] > 0
    if name == "q_trail":
        # her hind hooves (the leap's trail runs back from them to where she jumped from): the leftmost of the drawn
        # squares in the lowest 12 rows of the figure, the bow's cyan left out
        rgb = a[..., :3].astype(int)
        bow = (rgb[..., 1] > 150) & (rgb[..., 2] > 150) & (rgb[..., 0] < 120)
        ys, xs = np.nonzero(op & ~bow)
        low = ys >= ys.max() - 12
        lx, ly = xs[low], ys[low]
        near = lx <= lx.min() + 8
        pts["cyan"] = (float(lx[near].mean()), float(ly[near].mean()))
    elif name == "r_raise":
        ys, xs = np.nonzero(op)
        top = ys.min()
        pts["yellow"] = (float(xs[ys <= top + 2].mean()), float(top + 1))
    elif name == "w_call":
        # the raised hand: the topmost drawn squares left of the bow (the bow stands at the frame's right)
        rgb = a[..., :3].astype(int)
        bow = (rgb[..., 1] > 150) & (rgb[..., 2] > 150) & (rgb[..., 0] < 120)
        bow = np.zeros_like(op) | bow
        cols_bow = np.nonzero(bow.any(0))[0]
        left = op.copy()
        if len(cols_bow):
            left[:, cols_bow.min() - 4:] = False
        ys, xs = np.nonzero(left)
        top = ys.min()
        pts["cyan"] = (float(xs[ys <= top + 3].mean()), float(top + 2))
    return pts


def bake_guides(out):
    """bake/kindred_bake_<name>_<n>.png: the finished dense frame faded on the guide canvas (LAND or PORT squares at
    BAKE_PX, her pivot on the canvas' pivot square), a light grid every 10 squares, the ground line red, the frame's box
    grey, the points as crosses. -> {(name, n): {"canvas": [w, h], "frame": [x0, y0, w, h], "cyan" / "yellow": [x, y]}}."""
    cells = {}
    for name, tag, ks, _, *_ in BAKE:
        for k in ks:
            a = frames_of("hd_" + tag)[k - 1]
            H, W = a.shape[:2]
            CW, CH, (gx, gy) = LAND if H / 2 <= LAND[2][1] and W / 2 <= LAND[2][0] else PORT
            x0, y0 = gx - W // 2, gy - H // 2
            assert x0 >= 0 and y0 >= 0 and x0 + W <= CW and y0 + H <= CH, (name, k, W, H)
            can = np.zeros((CH, CW, 4), np.uint8)
            can[y0:y0 + H, x0:x0 + W] = a
            img = Image.new("RGB", (CW * BAKE_PX, CH * BAKE_PX), (36, 40, 52))
            g = np.asarray(Image.fromarray(can).resize((CW * BAKE_PX, CH * BAKE_PX), Image.NEAREST)).astype(float)
            m = g[..., 3:] / 255.0
            grey = g[..., :3].mean(-1, keepdims=True) * 0.35 + 70
            base = np.asarray(img).astype(float)
            img = Image.fromarray((base * (1 - m) + grey * m).astype(np.uint8))
            d = ImageDraw.Draw(img)
            for x in range(0, CW + 1, 10):
                d.line([(x * BAKE_PX, 0), (x * BAKE_PX, img.height)], fill=(52, 58, 72))
            for y in range(0, CH + 1, 10):
                d.line([(0, y * BAKE_PX), (img.width, y * BAKE_PX)], fill=(52, 58, 72))
            ground = y0 + H / 2.0 + FEET * HD_PPU
            d.line([(0, ground * BAKE_PX), (img.width, ground * BAKE_PX)], fill=(150, 60, 60), width=2)
            d.rectangle([x0 * BAKE_PX, y0 * BAKE_PX, (x0 + W) * BAKE_PX - 1, (y0 + H) * BAKE_PX - 1],
                        outline=(96, 100, 112))
            pts = bake_points(name, tag, k, a)
            cell = {"canvas": [CW, CH], "px": BAKE_PX, "frame": [x0, y0, W, H], "into": f"hd_{tag} {k}"}
            for colour, rgb in (("cyan", (0, 255, 255)), ("yellow", (255, 220, 40))):
                if colour not in pts:
                    continue
                px_, py_ = pts[colour]
                cx, cy = int(round(px_ + x0)), int(round(py_ + y0))
                cell[colour] = [cx, cy]
                X, Y = (cx + 0.5) * BAKE_PX, (cy + 0.5) * BAKE_PX
                d.line([(X - 18, Y), (X + 18, Y)], fill=rgb, width=3)
                d.line([(X, Y - 18), (X, Y + 18)], fill=rgb, width=3)
            img.save(os.path.join(out, f"kindred_bake_{name}_{k}.png"))
            cells[(name, k)] = cell
    return cells


def document(shape, cells):
    h, w = shape[:2]
    L = []
    a = L.append
    n_bake = sum(len(b[2]) for b in BAKE)
    a("# 永猎双子 千珏：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图 + {n_bake} 张画进她动作帧的图。** 造型和动作已定（`design/kindred_designs.png`：3/4 正面待机（羊灵 + 身后的狼灵）、"
      "羊灵侧面、狼灵侧面；动作都是侧面朝右，狼灵浮在她身后）。")
    a(f"> - 她在游戏里是**高清**的：每个游戏像素里 2.86×2.86 个细格子；1 倍时 {w}×{h} 格（连弓和狼灵）。")
    a("> - **两种画法**：")
    a(f"> 1. 第一部分 {len(FX)} 张普通特效（箭、打中、印记、狼咬、地上的领域和法阵、治疗）**照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。"
      "大小对照 `design/kindred_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；"
      "`design/kindred_shots.png` 是定稿动作（4 倍），青色十字是她身上、脚下特效的位置。")
    a("> 2. 第二部分是**画进她自己动作帧**的图（她的帧会随朝向镜像，特效图不会，所以弦上的箭、松弦的光、跳跃的拖影这些有方向的东西必须画进帧里）。"
      f"这些按**她的高清细格子**画：`bake/kindred_bake_<名字>_<帧>.png` 是那一帧的定位图（横图 {LAND[0]}×{LAND[1]} 格或竖图 {PORT[0]}×{PORT[1]} 格，"
      f"每格 {BAKE_PX} 像素；她本人画成淡灰色、只用来对位置；灰框是这一帧的范围，红线是地面，每 10 格一道浅线；青色、黄色十字是起点）。"
      "**在同样大小、同样格子的图上只画特效，背景透明，不要画她本人**；Claude 按格子取回，直接叠进她的帧。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里千珏自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，"
      "不要提交。颜色照英雄联盟原版：**羊灵的箭和光是灵光：白芯、淡青到天蓝**；**狼灵的 E、W 和咬是深紫靛色的烟，淡紫的芯**；"
      "**印记是青色和紫色相间的漩涡**；**大招是白亮、淡青和薄荷色的神圣光**。")
    a("> - **特效要亮**：每道光、每缕烟都要有白色或最亮一档的芯，暗底上一眼能看见（狼烟的芯用淡紫）。")
    a("> - **围着人的光只画两边，中间身体位置留空**；地上的领域和法阵里面基本是空的，不要涂满。")
    a("> - **方向（重要，红色方不会镜像）**：飞行的箭画成**朝右飞、上下对称**（游戏会把它转向飞行方向）；打中、目标身上、地上的画面和她身上的 buff "
      "都要**严格左右对称**（逐格对称），只有印记和法阵中间的**漩涡**不用对称（它没有前后，游戏两边画法一样）。第二部分画进帧里的图照定位图的方向画（箭朝右，"
      "拖影朝左下），不用对称。")
    a(f"> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kindred_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），"
      f"以及 `kindred_bake_<名字>_<帧>.png`（第二部分，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（{LAND[0]}×{LAND[1]} 或 {PORT[0]}×{PORT[1]}）。"
      "透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `kindred_fx_pack_done.zip`。"
      "**请用生图画，不要用代码拼方块**；**每张图单独交付，不要只给一张总览图**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「千珏之印」 | 羊灵拉弓射灵箭；击杀、助攻得到印记（射程、攻速、E 伤害随印记变大） | `a_nock`（帧里）· `a_loose`（帧里）· "
      "`a_arrow` · `a_hit` · `p_stack` |")
    a("| 技能 1 = Q「乱箭之舞」 | 灵巧地一跳，落地向最多 3 个目标各射一箭，之后攻速变快 | `q_trail`（帧里）· `q_dash` · `q_nock`（帧里）· "
      "`q_loose`（帧里）· `q_arrow` · `q_hit` |")
    a("| 技能 2 = E「横生惧意」+ W「狼灵狂热」 | E：一箭减速并打上狼的印记，再射中三下后狼灵扑上去咬；E 冷却时开 W：狼灵的领域，每秒咬领域里的敌人 | "
      "`e_nock`（帧里）· `e_loose`（帧里）· `e_arrow` · `e_hit` · `e_mark` · `e_bite` · `w_call`（帧里）· `w_zone` · `w_bite` |")
    a("| 大招「羊灵生息」 | 羊灵举弓，脚下展开法阵 4 秒，法阵里谁都不会死，结束时给里面的英雄回血 | `r_raise`（帧里）· `r_zone` · `r_heal` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火花、光丝都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("羊灵灵光（箭、普攻、Q、松弦）", LAMB), ("狼灵狼烟（E、W、狼咬）", WOLF), ("印记漩涡（E 印记、被动）", MARK),
                        ("羊灵生息（大招法阵、治疗）", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地上的圈是从斜上方看的扁椭圆（宽是高的 2.5 倍左右）。")
    a("- 画在别人身上的画面**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 第一部分：特效（{len(FX)} 张，游戏格子）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位："
      "普攻射程 55000，W 领域半径 60000，大招法阵半径 50000）。两张大领域按每格 8 像素画，其余每格 16 像素。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `kindred_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {TAIL}")
        a("```\n")
    a("---\n")
    a(f"## 第二部分：画进她动作帧的图（{n_bake} 张，她的高清格子）\n")
    a(f"每张都在对应的定位图 `bake/kindred_bake_<名字>_<帧>.png` 上画：同样大小（横图 {LAND[0] * BAKE_PX}×{LAND[1] * BAKE_PX}、竖图 "
      f"{PORT[0] * BAKE_PX}×{PORT[1] * BAKE_PX} 像素）、每格 {BAKE_PX} 像素，格子和定位图完全对齐；**只画特效，不画她**，背景透明。"
      "她本人在定位图里是淡灰色，只用来对位置。青色十字一般是拉弦的手（弦的顶点）或起点，黄色十字是握弓的手（箭搭在弓上的地方）或弓尖。"
      "画在她**上面**的会盖住她（所以都别盖住她的脸），画在她**后面**的被她挡住的部分不用画。尽量画在灰框里，箭头和松弦的光可以伸出灰框。"
      "注意这里 1 格只有游戏里的 0.35 个像素（她的弓弦是 2 格白），所以线条至少 2 格粗，太细的进游戏就看不见了。\n")
    k0 = len(FX)
    for name, tag, ks, layer, title, zh, ramps, effects in BAKE:
        k0 += 1
        a(f"### {k0}. {title}\n")
        a(zh + "\n")
        for k in ks:
            c = cells[(name, k)]
            where = "，".join(f"{'青色' if col == 'cyan' else '黄色'}十字在第 {c[col][0]} 列、第 {c[col][1]} 行"
                             for col in ("cyan", "yellow") if col in c)
            a(f"**`kindred_bake_{name}_{k}.png`**（定位图 `bake/kindred_bake_{name}_{k}.png`，{c['canvas'][0]}×{c['canvas'][1]} 格，{where}）：\n")
            crosses = "; ".join(f"the {col} cross of the guide is at square ({c[col][0]}, {c[col][1]})"
                                for col in ("cyan", "yellow") if col in c)
            a("```text")
            a(LEAD.format(ramps=ramps).replace("VFX sprite sheet", "VFX overlay on a character frame"))
            a(f"Effect: {effects[k]}")
            a(f"Layout: ONE image {c['canvas'][0] * BAKE_PX}x{c['canvas'][1] * BAKE_PX}, the same size and {BAKE_PX}-px "
              f"square grid as the guide picture (a {c['canvas'][0]} x {c['canvas'][1]} square grid); {crosses}, counted "
              "from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the "
              f"crosses or the lines. {TAIL}")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `kindred_fx_{name}` | {bind} | {size} |")
    for name, tag, ks, layer, *_ in BAKE:
        a(f"| `kindred_bake_{name}_<帧>` | 画进 `hd_{tag}` 第 {'、'.join(str(k) for k in ks)} 帧（{'人物上面' if layer == 'over' else '人物后面'}） | 高清格子 |")
    a("")
    a("- 两张表：`asset/league/effects/league_kindred_fx`（小的）和 `league_kindred_big`（e_bite、w_zone、r_zone），tag = 名字（build_kindred.py 的 views）。")
    a("- e_mark、p_stack 画在格子中间：导入时按目标 / 她的头顶高度垫高；地上的 q_dash、w_zone、r_zone 椭圆中心放在脚底线（站位点下方 11 格）；"
      "r_heal 的底放在脚底线。w_zone 的 3-8 帧、r_zone 的 3-6 帧按技能时长（510、240 tick）重复。")
    a("- 画进帧的图在 restyle 之后（rig_kindred.py 补洞那一步）按 `bake_cells.json` 从画布上切下这一帧的范围，叠到 `assets/source/ppu/kindred_<tag>.png` "
      "的高清帧上（over 盖在上面，under 只填空白），伸出帧外的地方两边一样加宽；1 倍表按格子投票一起更新。")
    a("- 用 `pixel_1x/` 切格（import_nidalee / import_nilah_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX, BAKE
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="kindred_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "kindred_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        BAKE = [x for x in BAKE if x[0] in keep]
        if len(FX) + len(BAKE) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run Temp/kn_work/fx/fx_ref_kn.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs", "bake"):
        os.makedirs(os.path.join(out, sub))
    designs(os.path.join(out, "design", "kindred_designs.png"))
    shape = size_sheet(os.path.join(out, "design", "kindred_size.png"))
    shots_sheet(os.path.join(out, "design", "kindred_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    cells = bake_guides(os.path.join(out, "bake"))
    doc = document(shape, cells)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"kindred_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX] +
                  [{"file": f"kindred_bake_{b[0]}_{k}.png", "into": f"hd_{b[1]} {k}", "layer": b[3]}
                   for b in BAKE for k in b[2]], f, ensure_ascii=False, indent=1)
    cells_json = {f"{n}_{k}": c for (n, k), c in cells.items()}
    for path in (os.path.join(out, "bake_cells.json"),) + (() if a.only else
                                                          (os.path.join(I.SRC, "fx_bake_cells.json"),)):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cells_json, f, indent=1)
    print(len(FX), "effects,", sum(len(b[2]) for b in BAKE), "frame overlays;", DOC, shape)
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
