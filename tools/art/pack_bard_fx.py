#!/usr/bin/env python3
"""Build bard_fx_pack.zip: step 3 of Bard's sprite - Codex draws his effects (after tools/art/pack_galio_fx.py).

    python tools/art/pack_bard_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name bard_fx_redo_pack]

The pack (%TEMP%/ba_work/fx/bard_fx_pack, zipped into --out, default dist/bard_packs) holds PROMPTS.md (also written to
assets/source/bard/PROMPTS_FX.md), design/bard_idle.png (his dense 3/4 front design at 3x), design/bard_size.png (the
1x idle at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter beside him),
design/bard_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Bard, grouped by the effect of ours they inform; Riot's art, local only: it reads
%TEMP%/ba_work/fxref, extracted from Bard.wad.client's base-skin particles by %TEMP%/ba_work/fx/fx_ref_ba.py).
The effects are the views the kit binds (tools/kit/build_bard.py): view_projectiles a_bolt, p_meep, q_bolt, w_shrine,
r_orb; view_effects a_hit, p_hit, q_hit, q_bind, w_land, e_door (also e_door_out), e_ride, r_mark, r_dome, r_lock (the
Banish's lock picture, on every frozen unit for the 2.5 s), r_free (its end picture); view_buffs slow (p_slow, q_slow)
and haste (w_haste, e_haste). League's colours: Bard's cosmic gold and white light, the purple-blue of the stars, the
teal of his chime orb, the shrine's leaf green. Light gets no outline. Red side: the flying pictures symmetric top to
bottom (they turn with the flight), every other picture symmetric left to right.
He is about 39 x 36 game px in game (PPU 1.5, 100 %).
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "ba_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "bard", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_bard")
HD_FRONT = os.path.join(ROOT, "assets", "source", "bard", "hd", "front.png")   # the approved dense design
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF6C8, #FFE27A, #F5C343, #D9962B, #A86A1E"      # cosmic gold light
STAR = "#FFFFFF, #F2E8FF, #C7B3FF, #8E7BEA, #5A4CC4, #2E2A7A"      # purple-blue starlight
TEAL = "#FFFFFF, #E8FFF8, #8CF2D8, #3FCFAE, #1E8F80"               # his chime orb's teal
LEAF = "#F4FFE0, #C6F27A, #7FCF4A, #3E8F3A, #8A5A2E"               # the shrine: leaves, a little wood
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, stars, rings or sparkles, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GD = f"a gold ramp ({GOLD})"
ST = f"a starlight ramp ({STAR})"
TL = f"a teal ramp ({TEAL})"
LF = f"a leaf ramp ({LEAF})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack and the passive (the Meeps)
    ("a_bolt", "普攻：飞出去的星光弹（朝目标飞，循环），4 帧",
     "view_projectiles `league_bard_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "10 × 6",
     "从喇叭口甩出去的一颗小星光：金白色的小星（4 个尖），后面拖一小段闪光（参考 BA_Flare_Cas、BA1_Distort）。**上下对称**，朝右飞。",
     GD,
     f"a SMALL STAR BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white-gold four-pointed star 4 squares "
     "across at the front, a short trail of 2-3 gold sparkles behind it, flickering in turn.",
     row(4, 12, 8) + "; the star's points 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_bard_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "星光打中：目标身上金白色的星一闪，散成几颗小星（参考 P_speed_flash）。**左右对称**。约 10 格，居中画。",
     GD,
     f"a STAR HIT on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 a white-gold four-pointed star 8 squares "
     "across; 3 the star breaking into 4 small gold sparkles at mirrored places, 10 squares across; 4 two fading specks.",
     row(4, 12, 12) + "; centered in every cell."),
    ("p_meep", "被动 旅者的召唤：飞出去的米普（朝目标飞，循环），4 帧",
     "view_projectiles `league_bard_p_meep`（朝飞行方向转，画成朝右飞；上下对称）", "10 × 8",
     "米普小精灵：一团圆圆的金黄色小精灵（参考 M_Meep_override 的颜色和旋涡），两只小眼睛**在正中横线上**（这样上下对称），身后拖着几颗小星。**上下对称**，朝右飞。",
     f"{GD} and {ST}",
     f"a TINY ROUND SPIRIT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a round golden-yellow puff 6 squares "
     "across with a pale swirl on it, two small dark eyes side by side on the horizontal middle line (so it stays "
     "symmetric), a tail of 3 purple-white sparkles behind it bobbing in turn.",
     row(4, 12, 10) + "; the puff's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("p_hit", "被动：米普打中（目标身上，扇形溅开），5 帧", "view_effects `league_bard_p_hit`（跟随，画在人物上面；左右对称）", "18 × 12",
     "米普打中：目标身上金色的光一炸，往两边溅开一圈紫蓝色的星光弧（参考 P_Meep_cone_main、P_Meep_cone30）。**左右对称**。",
     f"{GD} and {ST}",
     f"a SPIRIT BURST on a unit, 5 frames, {LR}: 1 a white-gold flash 4 squares; 2 a golden burst 10 squares across with "
     "a white core; 3 a purple-blue arc of starlight 18 squares wide and 8 tall spreading out from it, small stars at "
     "mirrored places; 4 the arc thinning, the stars drifting out; 5 fading stars.",
     row(5, 20, 14) + "; centered across, the burst's middle 7 squares above the cell's bottom."),
    # ---- Q Cosmic Binding
    ("q_bolt", "Q 星界束缚：飞出去的星界能量（直线飞，循环），4 帧",
     "view_projectiles `league_bard_q_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "16 × 10",
     "星界能量弹：前头一团金白色的光球，后面拖着一条紫蓝色的星尾，尾巴里闪着小星（参考 Q_mis_spark、R_distort 的紫蓝色）。**上下对称**，朝右飞。",
     f"{GD} and {ST}",
     f"a COSMIC BOLT flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white-gold glowing ball 6 squares across at "
     "the front, a tapering purple-blue tail 10 squares long behind it with small white stars in it twinkling in turn.",
     row(4, 18, 12) + "; the ball's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("q_hit", "Q 打中（目标身上），5 帧", "view_effects `league_bard_q_hit`（跟随，画在人物上面；左右对称）", "16",
     "星界能量打中：金色和紫蓝色的星光炸开，一圈小星往外飞。**左右对称**。约 16 格。",
     f"{GD} and {ST}",
     f"a COSMIC HIT on a unit, 5 frames, {LR}: 1 a white flash 5 squares; 2 a gold burst 10 squares across, white core; "
     "3 a purple-blue starry ring 16 squares across round it, 6 small stars flying out at mirrored places; 4 the ring "
     "breaking up; 5 fading stars.",
     row(5, 18, 18) + "; centered in every cell."),
    ("q_bind", "Q 眩晕：星界锁链缠住（目标身上，约 1.5 秒），6 帧",
     "view_effects `league_bard_q_bind`（跟随，画在人物上面；左右对称；6 帧铺满 1.5 秒）", "22 × 14",
     "被星界束缚晕住：目标腰间一圈金色的光环（从斜上方看的扁椭圆），环上缠着几颗星，星慢慢绕着转（亮暗交替）。**中间人形位置留空**，**左右对称**。",
     f"{GD} and {ST}",
     f"a GOLDEN BINDING RING round a unit's waist, 6 frames, {LR}, its middle EMPTY (a clear upright area 10 squares "
     "wide): a flat gold ellipse 22 squares wide and 8 tall, 1-2 squares thick, white highlights at its front; 4 small "
     "purple-white stars on it at mirrored places taking turns to brighten (the spin shown by light, every frame "
     "mirrored); 1 the ring snapping shut (brightest); 2-5 the ring holding; 6 the ring fading.",
     row(6, 24, 16) + "; centered in every cell."),
    # ---- W Caretaker's Shrine
    ("w_shrine", "W 游神圣坛：丢出去的圣坛（朝队友飞，循环），4 帧",
     "view_projectiles `league_bard_w_shrine`（朝飞行方向转，画成朝右飞；上下对称）", "10",
     "飞向队友的圣坛：一颗绿色和金色的光球（中间一颗金白色的光芯，外面绕着几片绿叶，参考 P_Shrine_spark、P_shrine_grass），后面一点金光。**上下对称**。",
     f"{LF} and {GD}",
     f"a GLOWING LEAF ORB flying to the RIGHT, 4 frames, a seamless loop, {TB}: a white-gold core 4 squares across inside "
     "a ring of small green leaves 8 squares across, the leaves turning step by step (mirrored top to bottom), a short "
     "gold sparkle trail behind.",
     row(4, 12, 12) + "; the orb's front 1 square from the RIGHT edge, vertically centered, in every cell."),
    ("w_land", "W 圣坛落到队友身上：治疗（队友身上），6 帧", "view_effects `league_bard_w_land`（跟随，画在人物上面；左右对称）",
     "20 × 26",
     "圣坛落地给队友治疗：队友脚下冒出一个小小的圣坛（一个金色的小台子，上面一颗发光的金绿光球，旁边几片草），然后绿色和金色的光点往上升（治疗），最后散开。**左右对称**，中间人形位置留空。",
     f"{LF} and {GD}",
     f"a HEALING SHRINE at a unit's feet, 6 frames, {LR}, the middle above the shrine EMPTY (a clear upright area 12 "
     "squares wide and 14 tall): 1 a gold flash on the ground 8 squares wide; 2 a small gold pedestal 6 squares wide "
     "with a glowing green-gold orb on it and grass tufts at both sides; 3 the orb bursting, green and gold motes rising "
     "at mirrored places up to 20 squares high; 4 more motes higher; 5 the motes highest, the pedestal fading; 6 a few "
     "fading motes.",
     row(6, 22, 28) + "; centered across, the pedestal's bottom 2 squares above the cell's bottom."),
    # ---- E Magical Journey
    ("e_door", "E 神奇旅程：传送门（门口 / 出口，不跟随 / 跟随），6 帧",
     "view_effects `league_bard_e_door`（入口：不跟随，画在人物下面；出口 `e_door_out` 用同一张，跟随；左右对称）", "18 × 30",
     "传送门：一个竖着的金色椭圆门框（金色光环，环上几个小星），门里是紫蓝色的星空隧道，打开、亮着、关上（参考 R_Ring_flare 的金环、R_distort 的紫蓝色）。**左右对称**。",
     f"{GD} and {ST}",
     f"an UPRIGHT STAR PORTAL, 6 frames, {LR}: an upright gold oval ring 18 squares wide and 30 tall, 2 squares thick, "
     "white highlights at its top, small white stars on it at mirrored places; inside it a deep purple-blue starry "
     "tunnel with white stars; 1 a thin gold line opening; 2 the ring half open; 3-4 fully open, the tunnel's stars "
     "twinkling; 5 the ring narrowing; 6 a thin fading line.",
     row(6, 20, 32) + "; centered across, the oval's bottom 1 square above the cell's bottom."),
    ("e_ride", "E 被传送门带走的队友（队友身上），4 帧", "view_effects `league_bard_e_ride`（跟随，画在人物上面；左右对称）", "16 × 22",
     "被门带走的队友：身上一圈金色的星光和几道往上的光痕（像被吸进门里），**中间人形位置留空**。**左右对称**。",
     f"{GD} and {ST}",
     f"a GOLD TRAVEL SPARKLE round a unit, 4 frames, {LR}, its middle EMPTY (a clear upright area 10 squares wide and 18 "
     "tall): gold and purple-white sparkles and short vertical light streaks at both sides at mirrored places; 1 the "
     "sparkles appearing; 2-3 the streaks rising; 4 fading sparkles.",
     row(4, 18, 24) + "; centered across, the streaks' bottom on the cell's bottom row."),
    # ---- R Tempered Fate
    ("r_orb", "R 调和命运：飞出去的金色法球（抛物线，循环），4 帧",
     "view_projectiles `league_bard_r_orb`（朝飞行方向转；上下、左右都对称）", "14",
     "金色的时之法球：一颗大金球，球面上一圈钟表一样的金色符文环，中间白色的光芯（参考 R_Ring_flare、R_explo_symbol）。**上下、左右都对称**（逐格）。",
     GD,
     f"a GOLDEN FATE ORB, 4 frames, a seamless loop, {LR} and {TB}: a white-gold glowing ball 10 squares across with a "
     "thin gold ring round it 14 squares across marked with 8 small clock ticks; the ticks taking turns to brighten.",
     row(4, 16, 16) + "; centered in every cell."),
    ("r_mark", "R 落点提示（地上，不跟随，法球飞的时候），6 帧",
     "view_effects `league_bard_r_mark`（不跟随，画在人物下面；左右对称；6 帧铺满法球飞行 0.4 秒）", "52 × 18",
     "法球落点地上的提示：一个金色的大圆环（从斜上方看的扁椭圆），环上钟表刻度，中间几道金光慢慢变亮。**左右对称**。范围约 52 格宽（落点半径 26000）。",
     GD,
     f"a GOLDEN CLOCK CIRCLE on the ground, 6 frames, {LR}: a flat gold ellipse 52 squares wide and 18 tall, 1 square "
     "thick, 12 small clock ticks on it at mirrored places; 1 the ring faint; 2-5 the ring brighter each frame, gold "
     "motes gathering inward at mirrored places; 6 the ring brightest.",
     row(6, 54, 20) + "; centered in every cell."),
    ("r_dome", "R 落地：金色时停穹顶（落点，不跟随），5 帧",
     "view_effects `league_bard_r_dome`（不跟随，画在人物上面；左右对称）", "52 × 40",
     "法球落地的一下：一个金色的大穹顶罩下来（半个大气泡，外圈金色、几道钟表一样的符文，表面一点白色反光），一闪就静止。**左右对称**，中间留空（里面的人会被时停）。范围约 52 格宽。",
     f"{GD} and {ST}",
     f"a GOLDEN STASIS DOME landing, 5 frames, {LR}, its inside EMPTY apart from faint lines (a clear area 40 squares "
     "wide and 30 tall): 1 a white-gold flash at the ground's middle 12 squares wide; 2 a gold dome outline 36 squares "
     "wide and 28 tall growing from the ground; 3 the dome 52 wide and 40 tall, 2 squares thick at its rim, a gold "
     "clock ring round its base with 12 ticks, white highlights at its top; 4 the dome's rim glowing, 4 purple-white "
     "stars at mirrored places; 5 the dome dimming to a thin gold rim.",
     row(5, 54, 42) + "; centered across, the dome's base 3 squares above the cell's bottom."),
    ("r_lock", "R 被时停的单位（每个被冻住的人，2.5 秒），6 帧",
     "view_effects `league_bard_r_lock`（时停的锁定画面：不跟随，画在人物上面；左右对称；6 帧铺满 2.5 秒）", "24 × 30",
     "每个被时停的人：被罩在一个金色的时停气泡里（竖着的椭圆，外圈金色，表面几道金色的光纹和一个钟表的指针图案，像琥珀），**里面的人会隐身，所以气泡里面用浅金色填一层（硬边像素块，不要半透明）**，看起来像人被封在金色琥珀里。**左右对称**。",
     f"{GD} and {ST}",
     f"a GOLDEN STASIS BUBBLE where a unit is frozen, 6 frames, {LR}: an upright gold ellipse 24 squares wide and 30 "
     "tall, its rim 2 squares thick gold, filled with pale gold (hard flat pixels, no transparency) like amber, a faint "
     "darker gold upright figure shape inside it, a clock face with two hands drawn faintly in the middle; 1 the bubble "
     "forming (rim only); 2-5 the full bubble, white highlights on its top moving one step each frame; 6 the same as 5.",
     row(6, 26, 32) + "; centered across, the bubble's bottom 1 square above the cell's bottom."),
    ("r_free", "R 时停结束：气泡碎开（每个被冻住的人），4 帧",
     "view_effects `league_bard_r_free`（不跟随，画在人物上面；左右对称）", "28 × 32",
     "时停结束：金色气泡碎成几片金色的碎片往外飞，一圈白光一闪。**左右对称**。",
     GD,
     f"a GOLDEN BUBBLE SHATTERING, 4 frames, {LR}: 1 the bubble rim (24 wide, 30 tall) cracking with white lines; 2 a "
     "white flash and 8 gold shards flying out at mirrored places, 28 squares across; 3 the shards farther, smaller; "
     "4 fading gold specks.",
     row(4, 30, 34) + "; centered across, the shards' middle 15 squares above the cell's bottom."),
    # ---- buffs
    ("slow", "减速（被米普、Q 减速的人脚下，循环），4 帧",
     "view_buffs `league_bard_p_slow` 和 `league_bard_q_slow`（跟随，画在人物下面；左右对称）", "18 × 6",
     "被减速：脚下一圈紫蓝色的星光慢慢转（扁椭圆上几颗小星，亮暗交替）。**左右对称**。",
     ST,
     f"a SLOW RING at a unit's feet, 4 frames, a seamless loop, {LR}: a flat purple-blue ellipse 18 squares wide and 6 "
     "tall, 1 square thick, with 4 small white stars on it at mirrored places taking turns to brighten.",
     row(4, 20, 8) + "; centered in every cell."),
    ("haste", "加速（圣坛、传送门给的移速，脚下，循环），4 帧",
     "view_buffs `league_bard_w_haste` 和 `league_bard_e_haste`（跟随，画在人物下面；左右对称）", "18 × 8",
     "加速：脚下两边几道金绿色的速度光痕往后飘（左右对称，两边各一组），夹着小光点。**左右对称**。",
     f"{GD} and {LF}",
     f"SPEED STREAKS at a unit's feet, 4 frames, a seamless loop, {LR}: at each side of the feet three short horizontal "
     "gold-green light streaks (2-5 squares long) and two small motes, the streaks taking turns to brighten, 18 squares "
     "wide in all.",
     row(4, 20, 10) + "; centered across, the streaks' middle 3 squares above the cell's bottom."),
]

GROUPS = [
    ("a_* p_*", ["Bard_Base_BA_Flare_Cas", "Bard_Base_BA1_Distort_RGBA", "Bard_Base_P_speed_flash", "Bard_Base_M_Meep_override",
                 "Bard_Base_P_Meep_cone_main", "Bard_Base_P_Meep_cone30_distortion"]),
    ("q_*", ["Bard_Base_Q_mis_spark", "Bard_Base_R_distort", "Bard_Base_P_speed_flash"]),
    ("w_*", ["Bard_Base_P_Shrine_spark", "Bard_Base_P_shrine_grass", "Bard_Base_W_glow", "Bard_Base_W_Ground_Clump",
             "Bard_Base_W_smoke_seq"]),
    ("e_* r_*", ["Bard_Base_R_Ring_flare", "Bard_Base_R_distort", "Bard_Base_R_explo_symbol"]),
]
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_bolt / p_meep：从喇叭口飞出去"),
         ("skill", 4, "q_bolt：从喇叭口往右推出去"),
         ("skill2", 3, "w_shrine：举起的手召出圣坛，飞向队友"),
         ("skill2_e", 2, "e_door：身前开门"),
         ("ult", 4, "r_orb：挥下乐器，法球飞出")]


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
            d.text((LW + c * S + 4, y + 2), nm.replace("Bard_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def idle_1x():
    import tfm2_ase as T
    sp = T.load_sprite(SHEET)
    f = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """His 1x idle at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
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
    d.text((8, 36), f"巴德 {fig.shape[1]}×{fig.shape[0]} 格（游戏里 1 倍图），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (the imported sheet's 1x frames), his standing point as a cyan cross."""
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
    a("# 星界游神 巴德：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/bard_idle.png`：游戏里的 3/4 正面待机，乐器扛在近侧肩上）。他在游戏里是**高清**的（PPU 1.5：每个游戏格子里 1.5 个细像素，这张图是高清造型放大 3 倍），1 倍图 {h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/bard_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/bard_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里巴德自己的特效贴图（米普、圣坛的光和草、R 的金环和紫蓝色时停、Q 的火花），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**金色和白色的星界之光、紫蓝色的星光、他乐器上青绿色的光球、圣坛的叶绿色**。")
    a("> - **特效要亮**：每道光、每颗星都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光环、气泡、门只画外圈，中间人形位置留空**（`r_lock` 例外：被时停的人在游戏里会隐身，气泡里面用浅金色填满，像封在琥珀里）。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bolt`、`p_meep`、`q_bolt`、`w_shrine` 画成朝右，**上下对称**（往左飞时会上下翻）；`r_orb` 上下左右都对称。"
      "其余所有画面（打中、身上、脚下、地上的圈、门、穹顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `bard_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `bard_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「旅者的召唤」 | 甩出星光弹；每 3 秒一只米普跟着飞出去，打中后溅开、减速 | `a_bolt` · `a_hit` · `p_meep` · `p_hit` · `slow` |")
    a("| 技能 1 = Q「星界束缚」 | 星界能量弹打中第一个敌人，身后还有敌人就两个都晕住 | `q_bolt` · `q_hit` · `q_bind` · `slow` |")
    a("| 技能 2 = W「游神圣坛」+ E「神奇旅程」 | 给交战的队友丢圣坛治疗加速；被近身时开门带身边的队友传走 | `w_shrine` · `w_land` · `haste` · `e_door` · `e_ride` |")
    a("| 大招 = R「调和命运」 | 金色法球飞向扎堆的敌人，落地后范围里所有单位时停 2.5 秒 | `r_orb` · `r_mark` · `r_dome` · `r_lock` · `r_free` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、星、光环、门都没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色光", GOLD), ("紫蓝色星光", STAR), ("青绿色光球", TEAL), ("圣坛叶绿", LEAF)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 52000，"
      "米普溅射半径 14000，Q 宽 6000，圣坛找队友 50000，传送门带人半径 25000，R 落点半径 26000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `bard_fx_{name}.png`：{title}\n")
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
        a(f"| `bard_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_bard_fx`（小的）和 `league_bard_big`（e_door、r_orb、r_mark、r_dome、r_lock、r_free），tag = 名字（build_bard.py 的 views；"
      "`e_door_out` 绑到 `e_door` 这张，`p_slow` / `q_slow` 绑到 `slow`，`w_haste` / `e_haste` 绑到 `haste`）。")
    a("- 飞行的 `a_bolt`、`p_meep`、`q_bolt`、`w_shrine`、`r_orb` 朝飞行方向转；`e_door`、`r_mark`、`r_dome`、`r_lock`、`r_free` 不跟随；`q_bind` 6 帧铺满 1.5 秒，`r_mark` 6 帧铺满 0.4 秒，`r_lock` 6 帧铺满 2.5 秒。")
    a("- 用 `pixel_1x/` 切格（import_kassadin / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="bard_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "bard_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run %TEMP%/ba_work/fx/fx_ref_ba.py first")
    if not os.path.exists(SHEET + "#sheet.png"):
        sys.exit(f"no imported sprite {SHEET}#sheet.png: build this pack after step 2")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    hd = np.asarray(Image.open(HD_FRONT).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(hd, 3, 0), 3, 1)).save(os.path.join(out, "design", "bard_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "bard_size.png"))
    shots_sheet(os.path.join(out, "design", "bard_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"bard_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
