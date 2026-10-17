#!/usr/bin/env python3
"""Build gragas_fx_pack.zip: step 3 of Gragas's sprite - Codex draws his effects (after tools/art/pack_nautilus_fx.py).

    python tools/art/pack_gragas_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name gragas_fx_redo_pack]

The pack (%TEMP%/gr_work/fx/gragas_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/gragas/PROMPTS_FX.md), design/gragas_idle.png (his 3/4 front idle at 8x, as imported),
design/gragas_size.png (the idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter
beside him), design/gragas_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png
(League's own particle textures for Gragas, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/gr_work/fxref, extracted from Gragas.wad.client's base-skin particles).
The effects are the views the kit binds (tools/kit/build_gragas.py: view_projectiles q_barrel, r_cask; view_effects
a_hit, w_hit, q_hit, q_land, q_boom, e_hit, e_dust, w_drink, p_heal, r_hit, r_boom; view_buffs q_slow, e_stun, w_on).
League's colours: golden ale and white foam, the keg's wood and iron, the cask's fire; dust for the slam, gold stars
for the stun, hot red-orange steam for Drunken Rage, a green-gold swig for Happy Hour. Light, liquid and smoke get no
outline; the flying kegs are objects and have one. Red side: the flying kegs symmetric top to bottom, every picture on
a unit or on the ground and every buff symmetric left to right. Codex also delivers pixel_1x/ game-size sheets.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gr_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "gragas", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_gragas")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


ALE = "#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12"     # ale and foam: white foam, gold and amber beer
WOOD = "#F2B868, #C47A34, #8A4E22, #5A2F16, #2E1A10"            # the keg's wood (the design's browns; #2E1A10 outlines)
IRON = "#D8DCE6, #9EA6B8, #6A7088, #3E4256"                     # the keg's iron hoops
FIRE = "#FFFFFF, #FFF2B0, #FFD24A, #FF9A1E, #E8501A, #A8280E"    # the cask's blast: fire over the ale
DUST = "#F4E8D0, #D8C4A0, #B09A78, #806E58"                      # dust and grit (the body slam)
RAGE = "#FFE2C0, #FF9A5A, #F05A28, #B8301A"                      # Drunken Rage: hot red-orange steam
STAR = "#FFFFFF, #FFF6A0, #FFD84A, #E8A21A"                      # stun stars
HEAL = "#FFFFFF, #E8FFD0, #B8F070, #6CC83A"                      # Happy Hour: a fresh green-gold swig
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a "
        "white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
AL = f"an ale-and-foam ramp ({ALE})"
WD = f"the keg's wood ({WOOD}; #2E1A10 is its 1-square outline)"
IR = f"iron hoops ({IRON})"
FI = f"a fire ramp ({FIRE})"
DU = f"a dust ramp ({DUST})"
RG = f"a hot steam ramp ({RAGE})"
ST = f"a star-gold ramp ({STAR})"
HL = f"a fresh green-gold ramp ({HEAL})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
BOTH = "SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and Drunken Rage's empowered punch
    ("a_hit", "普攻拳头打中（目标身上），4 帧", "view_effects `league_gragas_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "一记重拳打中：中间一道白色闪光，四周溅开几颗金黄色的酒滴和白沫（参考 ImpactGlow、Foam_Splash）。**左右对称**。约 12 格，居中画。",
     AL,
     f"a FIST HIT, 4 frames, {LR}: 1 a white impact flash 5 squares across; 2 a burst of white foam and golden ale "
     "drops 10 squares across; 3 the burst thinner, drops flying out at mirrored places; 4 a few fading drops.",
     row(4, 14, 14) + "; centered in every cell."),
    ("w_hit", "W 醉酒狂暴：强化普攻的酒浪爆发（目标身上），5 帧", "view_effects `league_gragas_w_hit`（跟随，画在人物上面；左右对称）",
     "36 × 20",
     "喝过酒后的下一拳：以目标为中心炸开一圈金黄色的酒浪和白沫（从斜上方看的扁椭圆，约 34 格宽），中间一团白光，酒滴往外飞（参考 Z_WineSplash、Splash_2x2、Z_Splashes_Anim_4x4）。**左右对称**，中间留出人的位置不要盖满。",
     AL,
     f"an ALE SHOCKWAVE round a unit, 5 frames, {LR}: 1 a white flash 8 squares across at the middle; 2 a ring of white "
     "foam and golden ale bursting out, an ellipse 24 squares wide and 9 tall; 3 the ring at 34 x 13, splashes rising "
     "at mirrored places on its rim; 4 the ring breaking into drops; 5 fading drops. The middle stays mostly clear.",
     row(5, 38, 22) + "; centered in every cell."),
    # ---- Q Barrel Roll
    ("q_barrel", "Q 滚动酒桶：飞出去的酒桶（抛物线飞行，循环），4 帧",
     "view_projectiles `league_gragas_q_barrel`（朝飞行方向转，画成朝右飞；上下对称）", "12 × 10",
     "Q 扔出去的小酒桶：从侧面看的木酒桶在翻滚（桶身横着，两头是圆桶盖，两道铁箍），后面拖一小串白沫（参考 Q_Mis、Q_Wood）。**上下对称**（滚动用铁箍和木纹的位置变化表现，不画朝一边转的斜线）。桶是实物，有 1 格深棕描边。",
     f"{WD}, {IR} and {AL}",
     f"a SMALL TUMBLING KEG flying to the RIGHT, 4 frames, a seamless loop, {TB}: a wooden keg seen from the side, 10 "
     "squares long and 8 tall, warm brown staves, two grey iron hoops, a round lid at each end, a 1-square dark brown "
     "outline; its rolling shown by the staves' lines and the hoops shifting each frame (mirrored top to bottom); a short "
     "trail of white foam bubbles behind it to the left (mirrored).",
     row(4, 14, 12) + "; the keg's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_land", "Q 酒桶落地后在地上冒泡（落点，0.75 秒），6 帧", "view_effects `league_gragas_q_land`（不跟随，画在人物下面一层；左右对称）",
     "14 × 14",
     "酒桶落在地上：一只立着的小酒桶（正面看，上面的桶盖和方木塞朝上），桶缝里往外冒白沫和金色酒泡，越来越多、桶在抖（参考 Q_Bubbles、Q_Floor_Puddle、Goo_Q）。**左右对称**。6 帧依次播放，最后一帧泡沫最满（下一刻就爆）。桶底在格子底部。",
     f"{WD}, {IR} and {AL}",
     f"a SMALL KEG ON THE GROUND ABOUT TO BURST, 6 frames, {LR}: an upright wooden keg 8 squares wide and 9 tall seen "
     "from the front (two grey iron hoops, a dark brown outline), standing on a small golden puddle; frame by frame more "
     "white foam and golden bubbles squirt out of its seams and lid at mirrored places, the keg trembling one square "
     "(1, 3, 5 up, 2, 4, 6 down), frame 6 brimming with foam.",
     row(6, 16, 16) + "; centered across, the keg's foot on the cell's bottom row."),
    ("q_boom", "Q 酒桶爆炸（落点），6 帧", "view_effects `league_gragas_q_boom`（不跟随，画在人物上面；左右对称）", "40 × 24",
     "酒桶炸开：一大团金黄色的酒浪和白沫往四周炸，地上一圈扁椭圆的酒浪（约 38 格宽），几块木片飞起来（参考 Z_WineSplash、Z_BarrelPiece、Q_hit_aoering）。**左右对称**。",
     f"{AL} and {WD}",
     f"a KEG BLAST on the ground, 6 frames, {LR}: 1 a white flash 10 squares across; 2 a dome of white foam and golden "
     "ale 20 squares wide bursting up; 3 a ring of ale on the ground, an ellipse 32 squares wide and 12 tall, splashes "
     "and 4 wooden stave pieces flying up at mirrored places; 4 the ring at 38 x 14, the pieces higher; 5 drops falling, "
     "the ring thinning; 6 a fading puddle ring.",
     row(6, 42, 26) + "; centered across, the ring's middle 7 squares above the cell's bottom."),
    ("q_hit", "Q 炸中（被炸中的人身上），4 帧", "view_effects `league_gragas_q_hit`（跟随，画在人物上面；左右对称）", "12",
     "被酒浪泼中：一团金色酒花和白沫溅在身上（参考 Foam_Splash）。**左右对称**。约 12 格，居中画。",
     AL,
     f"an ALE SPLASH on a unit, 4 frames, {LR}: 1 a white burst 4 squares; 2 golden ale and white foam splashing 10 "
     "squares across; 3 drops at mirrored places; 4 fading drops.",
     row(4, 14, 14) + "; centered in every cell."),
    ("q_slow", "Q 减速（被减速的人脚下，循环），4 帧", "view_buffs `league_gragas_q_slow`（跟随，画在人物下面；左右对称）", "16 × 6",
     "脚下一滩黏糊糊的金色酒水（从斜上方看的扁椭圆），表面几个泡泡冒起又破（参考 Puddle_Ripples、Q_Floor_Puddle）。**左右对称**。4 帧无缝循环。",
     AL,
     f"a STICKY ALE PUDDLE under a figure's feet, 4 frames, a seamless loop, {LR}: an ellipse 16 squares wide and 5 "
     "tall of golden amber ale with a lighter rim, 2-4 bubbles at mirrored places that swell and pop in turn.",
     row(4, 18, 8) + "; centered in every cell."),
    # ---- E Body Slam
    ("e_dust", "E 肉弹冲击：起步的尘土（他脚下，留在原地），5 帧", "view_effects `league_gragas_e_dust`（不跟随，画在人物下面；左右对称）",
     "24 × 10",
     "冲出去的那一下：脚下扬起一圈尘土（从斜上方看的扁椭圆，往外散开）和几颗碎石（参考 E_Dirt_Takeoff、E_EdgeDust、Dust）。**左右对称**。",
     DU,
     f"a DUST KICK-OFF on the ground, 5 frames, {LR}: 1 a low dust puff 8 squares wide; 2 a ring of dust clouds, an "
     "ellipse 18 squares wide and 6 tall, grit specks flying at mirrored places; 3 the ring at 24 x 8; 4 thinning; 5 "
     "fading wisps.",
     row(5, 26, 12) + "; centered across, the ring's middle 4 squares above the cell's bottom."),
    ("e_hit", "E 撞中（被撞的人身上），5 帧", "view_effects `league_gragas_e_hit`（跟随，画在人物上面；左右对称）", "20",
     "肚子撞上去：一个大的白色冲击星（四到八个尖角）炸开，一圈尘土往外，几颗星星溅出来（参考 E_Cas_01、E_CloudRing、ImpactGlow）。**左右对称**。约 20 格，居中画。",
     f"{DU} and {ST}",
     f"a BODY SLAM IMPACT, 5 frames, {LR}: 1 a white starburst 8 squares across with sharp points; 2 the starburst 16 "
     "squares, a ring of dust puffs round it; 3 the ring 20 squares across, 4 little gold stars flying out at mirrored "
     "places; 4 dust and stars fading; 5 a few wisps.",
     row(5, 22, 22) + "; centered in every cell."),
    ("e_stun", "E 眩晕（被晕的人头顶，循环），4 帧", "view_buffs `league_gragas_e_stun`（跟随，画在人物上面；左右对称）", "14 × 6",
     "头顶一圈打转的金色小星星（从斜上方看的扁圆，3 颗星）。**每帧左右对称**（星星换到对称的位置，不画成朝一个方向转）。4 帧无缝循环。画在格子的上部（头顶上方）。",
     ST,
     f"DIZZY STARS above a head, 4 frames, a seamless loop, {LR}: three small 5-point gold stars (3 squares each) on a "
     "flat ellipse 14 squares wide and 4 tall, their places mirrored left-right in every frame and moving to new "
     "mirrored places each frame; a faint gold trail between them.",
     row(4, 16, 8) + "; centered in every cell."),
    # ---- W Drunken Rage + the passive
    ("w_drink", "W 醉酒狂暴：喝酒时头边冒的酒泡（他身上），6 帧", "view_effects `league_gragas_w_drink`（跟随，画在人物上面；左右对称）",
     "20 × 16",
     "扛起酒桶灌酒：头部周围冒出一串金色酒泡和白沫，往上飘、一个个破掉（参考 W_Bubble、W_Flare）。**左右对称、中间留空**（不要挡住他的脸）。画在格子上部。",
     AL,
     f"ALE BUBBLES round a drinking head, 6 frames, {LR}, the MIDDLE 8 squares wide EMPTY: golden and white bubbles (1-3 "
     "squares) rising on both sides from the bottom of the cell to the top, mirrored, popping into tiny white sparks "
     "near the top; frame by frame more bubbles, frame 6 fewer.",
     row(6, 22, 18) + "; centered in every cell."),
    ("w_on", "W 醉酒狂暴：下一拳蓄满（他身上，循环），4 帧", "view_buffs `league_gragas_w_on`（跟随，画在人物上面；左右对称）", "36 × 44",
     "喝完酒的狂暴：他身体两侧往上冒红橙色的热气（一股一股往上飘），头顶几缕蒸汽（参考 W_Buff_Avatar、flame_Ring）。**中间留空、左右对称**，只画身体外沿和头顶。4 帧无缝循环。约 36 格宽、44 格高。",
     RG,
     f"HOT RAGE STEAM round a big figure, 4 frames, a seamless loop, {LR}, its inside EMPTY (a clear upright area 26 "
     "squares wide and 40 tall in the middle): puffs of red-orange steam rising along both sides from the waist up and "
     "3 wisps above the head, mirrored, each puff moving up 2-3 squares a frame and fading at the top.",
     row(4, 38, 46) + "; centered across, the figure's feet on the cell's bottom row."),
    ("p_heal", "被动欢乐时光：喝一口回血（他身上），5 帧", "view_effects `league_gragas_p_heal`（跟随，画在人物上面；左右对称）", "24 × 30",
     "每放一个技能先喝一口：身上冒出一圈绿金色的小光点和小酒泡往上飘（参考 W_Global_Heal、Rengar_Base_W_Heal_Spark）。**左右对称、中间留空**。",
     HL,
     f"a FRESH SWIG HEAL round a figure, 5 frames, {LR}, the middle 12 squares EMPTY: small green-gold plus-shaped "
     "sparks (3 squares) and bubbles rising on both sides from the feet to above the head, mirrored, frame 3 the most, "
     "frame 5 a few fading.",
     row(5, 26, 32) + "; centered across, the figure's feet on the cell's bottom row."),
    # ---- R Explosive Cask
    ("r_cask", "R 爆破酒桶：飞出去的大酒桶（抛物线飞行，循环），4 帧",
     "view_projectiles `league_gragas_r_cask`（朝飞行方向转，画成朝右飞；上下对称）", "18 × 14",
     "R 扔出去的大酒桶：比 Q 的大，桶身横着翻滚，桶盖上一圈火光，拖着火星和酒沫（参考 Z_Cask、Z_Grog、Goo_R）。**上下对称**。桶是实物，有 1 格深棕描边。",
     f"{WD}, {IR}, {FI}",
     f"a BIG TUMBLING CASK flying to the RIGHT, 4 frames, a seamless loop, {TB}: a wooden cask seen from the side, 14 "
     "squares long and 11 tall, warm brown staves, three grey iron hoops, a dark brown outline; a small burning fuse of "
     "fire at its front lid; a trail of sparks and foam to the left (mirrored); the staves and hoops shifting each frame "
     "to show it rolling.",
     row(4, 20, 16) + "; the cask's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_boom", "R 爆炸（落点），7 帧", "view_effects `league_gragas_r_boom`（不跟随，画在人物上面；左右对称）", "56 × 36",
     "大酒桶爆炸：一团橙黄色的火球往上冲，外面裹着金色酒浪和白沫，地上一圈扁椭圆的冲击波（约 52 格宽）往外扩，几块木桶碎片飞出（参考 Z_Color_WineSplash、Z_Splashes_Anim、Z_BarrelPiece、Flare_1）。**左右对称**。",
     f"{FI}, {AL} and {WD}",
     f"a BIG CASK EXPLOSION on the ground, 7 frames, {LR}: 1 a white flash 12 squares across; 2 a fireball 20 squares "
     "wide rising, white-yellow core, orange edge; 3 the fireball 28 wide inside a ring of golden ale and foam, a ground "
     "shockwave ellipse 36 squares wide and 12 tall; 4 the shockwave at 52 x 16, 6 wooden stave pieces flying out at "
     "mirrored places, the fire rising into smoke-free orange puffs; 5 ale drops raining, the ring thinning; 6 fading "
     "puffs and drops; 7 a few embers.",
     row(7, 58, 38) + "; centered across, the ground ring's middle 8 squares above the cell's bottom."),
    ("r_hit", "R 炸中（被炸飞的人身上），4 帧", "view_effects `league_gragas_r_hit`（跟随，画在人物上面；左右对称）", "14",
     "被炸到：一团橙黄色的小火花和酒沫溅在身上（参考 R_cone_hit、R_Drops）。**左右对称**。约 14 格，居中画。",
     f"{FI} and {AL}",
     f"a BLAST HIT on a unit, 4 frames, {LR}: 1 an orange-white flash 6 squares; 2 fire sparks and golden ale "
     "splashing 12 squares across; 3 sparks and drops at mirrored places; 4 fading embers.",
     row(4, 16, 16) + "; centered in every cell."),
]

GROUPS = [
    ("a_hit w_*", ["Gragas_Base_ImpactGlow", "Gragas_Base_Foam_Splash_2x2", "Gragas_Base_W_Bubble", "Gragas_Base_W_Flare",
                   "Gragas_Base_W_Buff_Avatar_rgba", "Gragas_Base_Z_WineSplash"]),
    ("q_*", ["Gragas_Base_Q_Mis", "Gragas_Base_Q_Wood", "Gragas_Base_Q_Bubbles", "Gragas_Base_Q_Floor_Puddle",
             "Gragas_Base_Q_hit_aoering", "Gragas_Base_Puddle_Ripples"]),
    ("e_*", ["Gragas_Base_E_Cas_01", "Gragas_Base_E_CloudRing", "Gragas_Base_E_Dirt_Takeoff_Specs",
             "Gragas_Base_E_EdgeDust_01", "Gragas_Dust_01", "Gragas_Base_E_Glow"]),
    ("r_* p_heal", ["Gragas_Base_Z_Cask", "Gragas_Base_Z_Grog_RGBA", "Gragas_Base_Z_Color_WineSplash_RGBA",
                    "Gragas_Base_Z_Splashes_Anim_4x4", "Gragas_Base_Z_BarrelPiece", "Gragas_Base_W_Global_Heal_01_Mult_v3"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit / w_hit：拳头打到的地方（画在目标身上）"),
         ("skill", 3, "q_barrel：酒桶从手里飞出去"),
         ("skill2", 3, "e_hit：肚子撞上去；e_dust 在起步的脚下"),
         ("skill2", 6, "w_drink：喝酒，酒泡在头边"),
         ("ult", 3, "r_cask：大酒桶从手里飞出去"),
         ("idle", 1, "w_on / p_heal / q_slow / e_stun：站位点")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Gragas_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def idle_1x():
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
    import tfm2_ase as T
    fig = idle_1x()
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
    d.text((8, 36), f"古拉加斯 {fig.shape[1]}×{fig.shape[0]} 格，原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (the imported sheet), his standing point as a cyan cross."""
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    px = sp.w // 2 + PAD
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(np.asarray(sp.frames[sp.tag_frames(tag)[k - 1]].convert("RGBA")), ((PAD, PAD), (PAD, PAD), (0, 0)))
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(ys.max()) + 1)
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(ys.max()) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 330), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 酒桶 古拉加斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/gragas_idle.png`：游戏里的 3/4 正面待机，8 倍，连背上的酒桶 {h} 行、{w} 格宽）。")
    a("> - 大小对照 `design/gragas_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/gragas_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里酒桶自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**金黄色的酒和白色泡沫**；扔出去的酒桶是木头加铁箍；R 的爆炸是火光裹着酒浪；E 是尘土和金星；W 的狂暴是红橙色热气；被动回血是清新的绿金色。")
    a("> - **特效要亮**：每团酒花、火光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的热气、酒泡、回血光点只画两边，中间留空**，不然会把人整个挡住。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的两只酒桶（`q_barrel`、`r_cask`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "其余所有画面（打中、落地、爆炸、脚下、头顶、身上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `gragas_fx_<名字>.png` 和原尺寸的 `pixel_1x/`，附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `gragas_fx_pack_done.zip`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「欢乐时光」 | 重拳；每放一个技能先喝一口回血 | `a_hit` · `p_heal` |")
    a("| 技能 1 = Q「滚动酒桶」 | 扔出酒桶，落地冒泡 0.75 秒后爆炸，炸到的人减速 | `q_barrel` · `q_land` · `q_boom` · `q_hit` · `q_slow` |")
    a("| 技能 2 = E「肉弹冲击」+ W「醉酒狂暴」 | 冲过去用肚子撞，撞到的人眩晕；随后扛桶喝酒，下一拳炸开一圈酒浪 | `e_dust` · `e_hit` · `e_stun` · `w_drink` · `w_on` · `w_hit` |")
    a("| 大招 = R「爆破酒桶」 | 扔出大酒桶，落地爆炸，把人炸飞到他这边 | `r_cask` · `r_boom` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**酒、泡沫、火光、尘土、热气、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**；只有飞出去的两只酒桶（实物）有 1 格深棕描边。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("酒和泡沫", ALE), ("酒桶的木头（#2E1A10 是描边）", WOOD), ("铁箍", IRON), ("火光（R）", FIRE),
                        ("尘土（E）", DUST), ("狂暴热气（W）", RAGE), ("眩晕星星", STAR), ("回血（被动）", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，"
      "Q 爆炸半径 19000，W 酒浪半径 17000，E 撞击半径 20000，R 爆炸半径 26000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `gragas_fx_{name}.png`：{title}\n")
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
        a(f"| `gragas_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_gragas_fx`（小的）和 `league_gragas_big`（w_hit、q_boom、r_cask、r_boom），tag = 名字（build_gragas.py 的 views）。")
    a("- `q_barrel`、`r_cask` 是抛物线（ParabolicProjectile），画面朝飞行方向转；`q_land`、`q_boom`、`r_boom`、`e_dust` 不跟随（落点 / 起步点）；`q_slow` 脚下 buff（z -1）；`w_on`、`e_stun` 画在人物上面（z 3），所以 `w_on` 中间必须是空的。")
    a("- 用 `pixel_1x/` 切格（import_viktor / import_seraphine 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="gragas_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Gragas's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    fig = idle_1x()
    Image.fromarray(np.repeat(np.repeat(fig, 8, 0), 8, 1)).save(os.path.join(out, "design", "gragas_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "gragas_size.png"))
    shots_sheet(os.path.join(out, "design", "gragas_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"gragas_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
