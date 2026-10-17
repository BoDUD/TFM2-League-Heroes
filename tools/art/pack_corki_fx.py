#!/usr/bin/env python3
"""Build corki_fx_pack.zip: step 3 of Corki's sprite - Codex draws his effects (after tools/art/pack_gragas_fx.py).

    python tools/art/pack_corki_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name corki_fx_redo_pack]

The pack (dist/corki_packs/corki_fx_pack, zipped next to it) holds PROMPTS.md (also written to
assets/source/corki/PROMPTS_FX.md), design/corki_idle.png (his dense idle as league.dll shows it, 2x),
design/corki_size.png (beside the base fighter at game size, the ground line, a 10-px ruler), design/corki_shots.png
(the frames the pictures start from, the cyan cross his standing point) and refs/lol_fx_ref.png (League's own particle
textures for Corki, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/cr_work/fxref, extracted from Corki.wad.client's base-skin particles by %TEMP%/cr_work/fx/fx_ref_cr.py).
The effects are the views the kit binds (tools/kit/build_corki.py: view_projectiles a_bolt, q_bomb, r_missile,
r_big_missile; view_effects a_hit, q_hit, q_boom, e_hit, w_fire, w_fire_big, w_burn, pk_blast, pk_hit, r_hit, r_boom,
r_big_boom; view_buffs e_shred). League's colours: hextech gold bullets, phosphorus white-yellow flashes, orange fire
and grey smoke, red-orange missile flames. Light, fire and smoke get no outline; the flying bomb and missiles are
objects and have one. Red side: the flying things symmetric top to bottom, every picture on a unit or on the ground and
every buff symmetric left to right. Codex also delivers pixel_1x/ game-size sheets.
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
import ppu_hd as P  # noqa: E402

REF = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "cr_work", "fxref")
DOC = os.path.join(ROOT, "assets", "source", "corki", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_corki")
OUT = os.path.join(ROOT, "dist", "corki_packs")
K = 5                                                            # his PPU

GOLD = "#FFFFFF, #FFF6C8, #FFE070, #F2B830, #C47A12"              # hextech bullets and sparks
PHOS = "#FFFFFF, #FFFDE0, #FFF08A, #FFD03A, #F29A1E, #B8561A"     # the phosphorus bomb's flash
FIRE = "#FFFFFF, #FFF2B0, #FFC84A, #FF8A1E, #E04A16, #9A2410"     # fire (Valkyrie's trail, the missiles' blasts)
SMOKE = "#E8E4E0, #B8B0A8, #8A8078, #5C544E"                      # grey smoke
METAL = "#E8ECF4, #A8B0C4, #6E7690, #3C4058, #20222E"             # missile and bomb bodies (#20222E outlines)
CHECK = "#FFE24A, #E8B020, #E04030, #A02420"                      # the bombs' yellow-and-red checks (his design)
SHRED = "#FFD8C0, #FF8A5A, #E0402A, #8A1E16"                      # the armour shred
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, fire, smoke or rings, BRIGHT colours (each burst lit with its lightest shades and a "
        "white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GD = f"a hextech gold ramp ({GOLD})"
PH = f"a phosphorus flash ramp ({PHOS})"
FI = f"a fire ramp ({FIRE})"
SM = f"a smoke ramp ({SMOKE})"
MT = f"a metal ramp ({METAL}; #20222E is its 1-square outline)"
CK = f"the checks of his bombs ({CHECK})"
SH = f"a red-orange ramp ({SHRED})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack (Hextech Munitions)
    ("a_bolt", "普攻子弹（飞行，循环），2 帧", "view_projectiles `league_corki_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "12 × 4",
     "格林机枪射出的一发海克斯子弹：一颗金白色的子弹头，后面拖一道短的金色曳光和一缕灰烟（参考 BA_Bullet、BA_Mis_SmokeTrail）。**上下对称**。",
     f"{GD} and {SM}",
     f"a GLOWING BULLET flying to the RIGHT, 2 frames, a seamless loop, {TB}: a white-gold bullet head 2 squares tall at "
     "the front, a gold tracer streak 7 squares long behind it fading to the left, a thin wisp of grey smoke at its tail "
     "(mirrored top to bottom); frame 2 the streak a little longer and the smoke shifted.",
     row(2, 14, 6) + "; the bullet's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_corki_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "子弹打中：中间一点白光，四周溅开几颗金色火花（参考 Z_hiteffect、Sparks）。**左右对称**。约 10 格，居中画。",
     GD,
     f"a BULLET HIT, 4 frames, {LR}: 1 a white impact flash 4 squares across; 2 a gold starburst 8 squares across with "
     "4-6 sharp rays; 3 gold sparks flying out at mirrored places; 4 a few fading sparks.",
     row(4, 12, 12) + "; centered in every cell."),
    # ---- Q Phosphorus Bomb
    ("q_bomb", "Q 磷光炸弹（抛物线飞行，循环），4 帧", "view_projectiles `league_corki_q_bomb`（朝飞行方向转，画成朝右飞；上下对称）",
     "10 × 6",
     "Q 扔出去的小炸弹：黄红格子的圆头小炸弹（和他机身下挂的炸弹一样的花纹），尾巴一圈小尾翼，后面拖一串白黄色的磷光火星（参考 Flare、Spark）。**上下对称**。炸弹是实物，有 1 格深色描边。",
     f"{CK}, {MT} and {PH}",
     f"a SMALL BOMB flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round-nosed bomb 6 squares long and 4 tall "
     "with yellow-and-red checks, a brown-grey metal nose, small fins at its tail, a 1-square dark outline; a trail of "
     "white-yellow phosphorus sparks behind it to the left (mirrored), twinkling each frame.",
     row(4, 12, 8) + "; the bomb's nose 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_boom", "Q 磷光炸弹爆炸（落点），6 帧", "view_effects `league_corki_q_boom`（不跟随，画在人物上面；左右对称）", "36 × 24",
     "磷光炸弹炸开：先一团刺眼的白黄色闪光，再一圈橙色火焰往外炸，地上一圈扁椭圆的冲击波（约 34 格宽），最后散成灰烟（参考 Z_bigglow、Z_fire_ball、Z_disintegrate02）。**左右对称**。",
     f"{PH} and {SM}",
     f"a PHOSPHORUS BLAST on the ground, 6 frames, {LR}: 1 a blinding white flash 10 squares across; 2 a white-yellow "
     "fireball 18 squares wide; 3 the fireball 24 wide with an orange rim, a ground ring ellipse 28 squares wide and 10 "
     "tall; 4 the ring at 34 x 12, sparks flying out at mirrored places; 5 orange flames sinking into grey smoke puffs; "
     "6 fading smoke.",
     row(6, 38, 26) + "; centered across, the ring's middle 7 squares above the cell's bottom."),
    ("q_hit", "Q 炸中（被炸中的人身上），4 帧", "view_effects `league_corki_q_hit`（跟随，画在人物上面；左右对称）", "12",
     "被磷光炸中：一团白黄色的闪光和橙色火花溅在身上。**左右对称**。约 12 格，居中画。",
     PH,
     f"a PHOSPHORUS SPLASH on a unit, 4 frames, {LR}: 1 a white burst 5 squares; 2 white-yellow and orange sparks 11 "
     "squares across; 3 sparks at mirrored places; 4 fading sparks.",
     row(4, 14, 14) + "; centered in every cell."),
    # ---- E Gatling Gun
    ("e_hit", "E 格林机枪扫中（被扫的人身上，每 0.25 秒一次），3 帧", "view_effects `league_corki_e_hit`（跟随，画在人物上面；左右对称）",
     "10",
     "机枪一串子弹打在身上：两三点小金色火花，一闪就没（参考 BA_Muzzle_Flash、Sparks）。**左右对称**。约 10 格，居中画，要小、要快。",
     GD,
     f"a QUICK BULLET SPRAY HIT, 3 frames, {LR}: 1 three small gold-white sparks 2-3 squares each at mirrored places "
     "within 8 squares; 2 the sparks as tiny gold crosses, two more; 3 two fading specks.",
     row(3, 12, 12) + "; centered in every cell."),
    ("e_shred", "E 破甲（被扫过的人头顶，循环），4 帧", "view_buffs `league_corki_e_shred`（跟随，画在人物上面；左右对称）", "10 × 6",
     "护甲和魔抗被削：头顶一个小小的红橙色裂开的盾牌图标，轻轻闪（参考 Flare）。**左右对称**。4 帧无缝循环，画在格子上部。",
     SH,
     f"a SMALL CRACKED SHIELD above a head, 4 frames, a seamless loop, {LR}: a shield shape 6 squares wide and 5 tall in "
     "red-orange with a light rim, split down the middle by a crack (the two halves 1 square apart, mirrored), pulsing "
     "brighter on frames 2-3.",
     row(4, 12, 8) + "; centered across, the shield in the top half of the cell."),
    # ---- W Valkyrie and the Package
    ("w_fire", "W 瓦尔基里俯冲留下的火（地上，2.5 秒），10 帧", "view_effects `league_corki_w_fire`（不跟随，画在人物下面一层；左右对称）",
     "18 × 14",
     "俯冲沿途留下的一团火：地上一片扁椭圆的焦痕，上面竖着几簇橙黄色的火苗往上蹿，前几帧旺，最后几帧变小、冒灰烟熄掉（参考 Z_flames02、common_flames03、R_ground_decal）。**左右对称**。10 帧依次播放（每帧 0.25 秒），火苗竖直向上（这张画面游戏不会转）。",
     f"{FI} and {SM}",
     f"a PATCH OF GROUND FIRE, 10 frames played once over 2.5 s, {LR}: a dark scorched ellipse 16 squares wide and 4 tall "
     "on the ground, 3-5 upright tongues of fire (white-yellow cores, orange and red edges, 6-10 squares tall) rising "
     "from it at mirrored places, flickering to new mirrored shapes every frame; frames 1-7 burning strong, 8-9 the "
     "flames lower with grey smoke, 10 a few embers and smoke.",
     row(10, 20, 16) + "; centered across, the scorch's middle 2 squares above the cell's bottom."),
    ("w_fire_big", "W 弹药包的大火（地上，4 秒），12 帧", "view_effects `league_corki_w_fire_big`（不跟随，画在人物下面一层；左右对称）",
     "26 × 18",
     "弹药包（特别快递）沿途留下的大火：和上一张一样但更宽更高（焦痕约 24 格宽，火苗 8–14 格高），燃得更久。**左右对称**，火苗竖直向上。12 帧依次播放（每帧约 0.33 秒）。",
     f"{FI} and {SM}",
     f"a BIG PATCH OF GROUND FIRE, 12 frames played once over 4 s, {LR}: a dark scorched ellipse 24 squares wide and 6 "
     "tall, 5-7 upright tongues of fire 8-14 squares tall rising from it at mirrored places, flickering every frame; "
     "frames 1-9 roaring, 10-11 lower with grey smoke, 12 embers and smoke.",
     row(12, 28, 20) + "; centered across, the scorch's middle 3 squares above the cell's bottom."),
    ("w_burn", "W 火焰烧到的人（身上），4 帧", "view_effects `league_corki_w_burn`（跟随，画在人物上面；左右对称）", "10",
     "站在火里被烧：身上几簇小火苗往上蹿。**左右对称**。约 10 格。",
     FI,
     f"a SMALL BURN on a unit, 4 frames, {LR}: 2-3 small upright flames (3-6 squares tall) at mirrored places rising and "
     "fading, a few sparks above.",
     row(4, 12, 12) + "; centered in every cell."),
    ("pk_blast", "弹药包起飞的冲击（他脚下，留在原地），6 帧", "view_effects `league_corki_pk_blast`（不跟随，画在人物上面；左右对称）",
     "40 × 22",
     "弹药包起飞那一下：他身下炸开一圈橙色火焰冲击波（扁椭圆，约 38 格宽），中间一团白黄色的推进器火光往下喷，四周扬起灰烟（参考 R_Flame、Dust_Puffs、Z_bigglow）。**左右对称**，中间上半部分留空（不要挡住他）。",
     f"{FI} and {SM}",
     f"a ROCKET TAKE-OFF BLAST on the ground, 6 frames, {LR}, the upper middle 16 squares wide EMPTY: 1 a white-yellow "
     "flash 12 squares across at the bottom middle; 2 a ring of orange fire bursting out, an ellipse 24 squares wide and "
     "8 tall; 3 the ring at 38 x 12, grey dust puffs rising at mirrored places; 4 the fire thinning into smoke; 5-6 "
     "fading smoke puffs.",
     row(6, 42, 24) + "; centered across, the ring's middle 5 squares above the cell's bottom."),
    ("pk_hit", "弹药包击退（被撞开的人身上），4 帧", "view_effects `league_corki_pk_hit`（跟随，画在人物上面；左右对称）", "14",
     "被弹药包的冲击撞开：一团橙色火光和灰烟炸在身上。**左右对称**。约 14 格，居中画。",
     f"{FI} and {SM}",
     f"a BLAST HIT on a unit, 4 frames, {LR}: 1 an orange-white flash 6 squares; 2 fire and grey smoke puffs 13 squares "
     "across; 3 smoke at mirrored places; 4 fading smoke.",
     row(4, 16, 16) + "; centered in every cell."),
    # ---- R Missile Barrage
    ("r_missile", "R 火箭（飞行，循环），3 帧", "view_projectiles `league_corki_r_missile`（朝飞行方向转，画成朝右飞；上下对称）",
     "14 × 6",
     "R 打出去的火箭：一枚银灰色的小火箭（尖头、红色弹头环、尾部两片小尾翼），尾巴喷着橙黄色的火焰和一串灰烟（参考 Corki_R_Flame、Z_color-firemissile、BA_Mis_SmokeTrail）。**上下对称**。火箭是实物，有 1 格深色描边。",
     f"{MT}, {FI} and {SM}",
     f"a SMALL ROCKET flying to the RIGHT, 3 frames, a seamless loop, {TB}: a silver-grey rocket 7 squares long and 3 "
     "tall with a pointed nose, a red band behind the nose, two small tail fins, a 1-square dark outline; an orange-"
     "yellow exhaust flame 3-4 squares behind it flickering each frame, a puff of grey smoke behind the flame "
     "(mirrored).",
     row(3, 16, 8) + "; the rocket's nose 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_big_missile", "R 大火箭（每第 3 发，飞行，循环），3 帧",
     "view_projectiles `league_corki_r_big_missile`（朝飞行方向转，画成朝右飞；上下对称）", "20 × 8",
     "大火箭（The Big One）：比上一张大一圈，弹身上黄红格子花纹（和他的炸弹一样），尾焰更长更亮。**上下对称**。",
     f"{MT}, {CK}, {FI} and {SM}",
     f"a BIG ROCKET flying to the RIGHT, 3 frames, a seamless loop, {TB}: a rocket 11 squares long and 5 tall with a "
     "pointed silver nose, a body of yellow-and-red checks, tail fins, a 1-square dark outline; a long white-yellow and "
     "orange exhaust flame 5-6 squares behind it flickering each frame, grey smoke puffs behind (mirrored).",
     row(3, 22, 10) + "; the rocket's nose 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("r_boom", "R 火箭爆炸（落点），5 帧", "view_effects `league_corki_r_boom`（不跟随，画在人物上面；左右对称）", "26 × 18",
     "火箭炸开：一团橙黄色火球，外面一圈灰烟，地上一圈扁椭圆冲击（约 24 格宽），几块碎片飞起（参考 Z_fire_ball、R_GroundBits、Smoke_4x4）。**左右对称**。",
     f"{FI} and {SM}",
     f"a ROCKET BLAST on the ground, 5 frames, {LR}: 1 a white flash 8 squares across; 2 an orange-yellow fireball 14 "
     "squares wide; 3 the fireball inside a ring of grey smoke, a ground ellipse 22 squares wide and 8 tall, 4 dark "
     "debris bits flying at mirrored places; 4 smoke puffs, the ring at 24 x 9; 5 fading smoke.",
     row(5, 28, 20) + "; centered across, the ring's middle 5 squares above the cell's bottom."),
    ("r_big_boom", "R 大火箭爆炸（落点），7 帧", "view_effects `league_corki_r_big_boom`（不跟随，画在人物上面；左右对称）", "40 × 28",
     "大火箭炸开：比上一张大很多，火球更高、冲击圈约 38 格宽，火星和碎片更多。**左右对称**。",
     f"{FI} and {SM}",
     f"a BIG ROCKET BLAST on the ground, 7 frames, {LR}: 1 a white flash 12 squares across; 2 a white-yellow fireball "
     "20 squares wide rising; 3 the fireball 28 wide with an orange rim, a ground ring ellipse 30 squares wide and 10 "
     "tall; 4 the ring at 38 x 13, 6 debris bits and sparks flying out at mirrored places; 5 the fire rising into grey "
     "smoke puffs; 6 smoke drifting up, embers falling; 7 fading smoke.",
     row(7, 42, 30) + "; centered across, the ring's middle 7 squares above the cell's bottom."),
    ("r_hit", "R 炸中（被炸的人身上），4 帧", "view_effects `league_corki_r_hit`（跟随，画在人物上面；左右对称）", "12",
     "被火箭炸到：一团橙色火花和一点灰烟。**左右对称**。约 12 格，居中画。",
     f"{FI} and {SM}",
     f"a FIRE HIT on a unit, 4 frames, {LR}: 1 an orange-white flash 5 squares; 2 fire sparks 11 squares across; 3 "
     "sparks and smoke at mirrored places; 4 fading embers.",
     row(4, 14, 14) + "; centered in every cell."),
]

GROUPS = [
    ("a_* e_*", ["Corki_Base_BA_Bullet", "Corki_BA_Mis_SmokeTrail", "Corki_Base_BA_Muzzle_Flash", "Corki_Base_Z_hiteffect",
                 "Sparks", "Corki_Base_Flare"]),
    ("q_*", ["Corki_Base_Spark", "Corki_Base_Z_bigglow", "Corki_Base_Z_fire_ball", "Corki_Base_Z_disintegrate02",
             "Corki_Base_Smoke_4x4", "Corki_Base_Z_color-firemissile"]),
    ("w_* pk_*", ["Corki_Base_Z_flames02", "common_flames03", "Corki_Base_R_ground_decal", "Corki_R_Flame",
                  "Corki_Base_Dust_Puffs_4x4", "Corki_Base_Z_smokepuffs_02"]),
    ("r_*", ["Corki_Base_Z_color-firemissile", "Corki_Base_R_GroundBits", "Corki_Base_R_Smoke_Noise",
             "Corki_Base_Z_fire_ball", "common_SRU_Chaos_Turret1_Flare", "Corki_Base_Z_color-addflame"]),
]
# the frames the pictures start from: (tag, frame index, what)
SHOTS = [("attack", 2, "a_bolt：子弹从机头的格林机枪口飞出（青十字 = 站位点）"),
         ("skill", 2, "q_bomb：炸弹从机身下扔出"),
         ("ult", 2, "r_missile / r_big_missile：火箭从机头飞出"),
         ("skill2_w", 0, "pk_blast：起飞冲击在他脚下；w_fire 沿途落在地上"),
         ("idle", 0, "e_shred / w_burn / 各种 hit：站位点")]


def dense(tag, i):
    sh = P.read_sheet(SHEET)
    return sh["hd_" + tag][i][0]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Corki_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)




def size_sheet(path):
    """His dense idle at game size x 4 (league.dll draws it PPU times finer), the base fighter beside him, the ground."""
    import tfm2_ase as T
    Z = 4
    f = dense("idle", 0)
    fig = Image.fromarray(f).resize((round(f.shape[1] * Z / K), round(f.shape[0] * Z / K)), Image.NEAREST)
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    kf = Image.fromarray(k).resize((k.shape[1] * Z, k.shape[0] * Z), Image.NEAREST)
    W = fig.width + kf.width + 60
    H = max(fig.height, kf.height) + 80
    img = Image.new("RGBA", (W, H), (104, 112, 72, 255))
    cy = 70 + max(fig.height, kf.height) // 2           # both frames centred on their pivots on one row
    img.alpha_composite(fig, (20, cy - fig.height // 2))
    img.alpha_composite(kf, (40 + fig.width, cy - kf.height // 2))
    d = ImageDraw.Draw(img)
    g = cy + 11 * Z + Z // 2
    d.line([(0, g), (W, g)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, fig.width // Z + 1, 10):
        x = 20 + i * Z
        d.line([(x, 8), (x, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((x + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    ys, xs = np.nonzero(f[..., 3] > 0)
    fw, fh = round((xs.max() - xs.min() + 1) / K), round((ys.max() - ys.min() + 1) / K)
    d.text((8, 36), f"库奇约 {fw}×{fh} 格（游戏像素，悬停），原版斗士（4 倍，红线是地面）", fill=(255, 255, 255, 255),
           font=font)
    img.convert("RGB").save(path)
    return fh, fw


def shots_sheet(path):
    """The finished frames at game size x 4 (dense / PPU), his standing point as a cyan cross."""
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, i, what in SHOTS:
        f = dense(tag, i)
        im0 = Image.fromarray(f).resize((round(f.shape[1] * Z / K), round(f.shape[0] * Z / K)), Image.NEAREST)
        im = Image.new("RGBA", (max(im0.width, 330), im0.height + 24), (104, 112, 72, 255))
        im.alpha_composite(im0, (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = im0.width // 2, 24 + im0.height // 2
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {i + 1}: {what}", fill=(255, 255, 255, 255), font=font)
        tiles.append(im)
    sheet = Image.new("RGB", (sum(t.width + 10 for t in tiles), max(t.height for t in tiles)), (60, 64, 50))
    x = 0
    for t in tiles:
        sheet.paste(t.convert("RGB"), (x, 0))
        x += t.width + 10
    sheet.save(path)


def document(shape):
    h, w = shape
    L = []
    a = L.append
    a("# 库奇 英勇投弹手：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定：他坐在飞机里悬停（`design/corki_idle.png`，游戏里约 {w} 格宽、{h} 格高，"
      "图是高清帧，游戏里按 5 倍密度显示）。特效照常按游戏像素画（1 格 = 1 个游戏像素），和其他英雄一样。")
    a("> - 大小对照 `design/corki_size.png`：他和原版斗士按游戏大小放大 4 倍，红线是地面，上面是 10 格一段的刻度。每条写的大小都是游戏像素（格）。")
    a("> - `design/corki_shots.png`：定稿动作（游戏大小 x4），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里库奇自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。"
      "颜色照英雄联盟原版：**普攻和机枪是海克斯金色的子弹和火花**；**Q 是刺眼的白黄色磷光**；W 和弹药包是橙色的火和灰烟；R 是银灰色小火箭拖橙色尾焰，大火箭身上是他炸弹的黄红格子。")
    a("> - **特效要亮**：每团火光、闪光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **方向（重要，红色方会镜像）**：飞出去的子弹、炸弹、火箭（`a_bolt`、`q_bomb`、`r_missile`、`r_big_missile`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。"
      "其余所有画面（打中、爆炸、地上的火、身上、头顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；地上的火苗竖直向上（这些画面游戏不会转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `corki_fx_<名字>.png` 和原尺寸的 `pixel_1x/`，附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `corki_fx_pack_done.zip`。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「海克斯科技军备」 | 格林机枪打一发海克斯子弹，部分伤害是真实伤害 | `a_bolt` · `a_hit` |")
    a("| 技能 1 = Q「磷光炸弹」 | 往目标位置扔一颗炸弹，炸开一片磷光 | `q_bomb` · `q_boom` · `q_hit` |")
    a("| 技能 2 = E「格林机枪」+ W「瓦尔基里俯冲」 + 被动「特别快递」 | 4 秒向前扫射、叠加破甲；被贴脸时向后俯冲留下一路火；带弹药包时起飞炸开、火更大 | `e_hit` · `e_shred` · `w_fire` · `w_fire_big` · `w_burn` · `pk_blast` · `pk_hit` |")
    a("| 大招 = R「火箭轰击」 | 存 4 发火箭，每第 3 发是大火箭 | `r_missile` · `r_big_missile` · `r_boom` · `r_big_boom` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟、冲击圈都没有黑描边，也不要用最深的颜色给形状描一圈边**；只有飞出去的炸弹和火箭（实物）有 1 格深色描边。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("海克斯金色（子弹、火花）", GOLD), ("磷光（Q）", PHOS), ("火（W、R）", FIRE), ("灰烟", SMOKE),
                        ("金属（炸弹头、火箭，#20222E 是描边）", METAL), ("炸弹的黄红格子", CHECK), ("破甲（E）", SHRED)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在人身上、脚下的画面按每条写的站位画，**格子里留出空的位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，"
      "Q 爆炸半径 17000，W 火焰半径 9000（弹药包 13000），弹药包击退半径 20000，R 爆炸半径 13000（大火箭 20000））。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `corki_fx_{name}.png`：{title}\n")
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
        a(f"| `corki_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_corki_fx`（小的）和 `league_corki_big`（q_boom、w_fire_big、pk_blast、r_big_missile、r_big_boom），tag = 名字（build_corki.py 的 views）。")
    a("- `a_bolt` 是 TargetProjectile、`q_bomb` 是抛物线、`r_missile` / `r_big_missile` 是直线，画面都朝飞行方向转；`q_boom`、`r_boom`、`r_big_boom`、`pk_blast`、`w_fire`、`w_fire_big` 不跟随（落点 / 起步点）；`w_fire*` 画在人物下面（z -1）；`e_shred` 头顶 buff（z 3）。")
    a("- 用 `pixel_1x/` 切格（import_gragas 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="corki_fx_pack", help="the pack's name (folder and zip)")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(OUT, a.name)
    zpath = os.path.join(OUT, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/cr_work/fx/fx_ref_cr.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    f = dense("idle", 0)
    Image.fromarray(np.repeat(np.repeat(f, 2, 0), 2, 1)).save(os.path.join(out, "design", "corki_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "corki_size.png"))
    shots_sheet(os.path.join(out, "design", "corki_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as fh:
        json.dump([{"file": f"corki_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], fh,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
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
