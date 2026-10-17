#!/usr/bin/env python3
"""Build orianna_fx_pack.zip: step 3 of Orianna's sprite - Codex draws her effects and her Ball (pack_pantheon_fx.py's
way).

    python work/or/fx_ref_or.py              # League's particle textures -> %TEMP%/or_work/fxref (Riot's art, local only)
    python tools/art/pack_orianna_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name orianna_fx_redo_pack]

The pack (%TEMP%/or_work/fx/orianna_fx_pack, zipped into --out, default dist/orianna_packs) holds PROMPTS.md (also
written to assets/source/orianna/PROMPTS_FX.md), design/orianna_idle.png (her design at 4x), design/orianna_ball.png (the
user's Ball, step 1 take 2, at 8x), design/orianna_size.png (the 1x idle at 4x on the arena colour with the feet line, a
10-px ruler, the base fighter and where the Ball floats), design/orianna_shots.png (the finished action frames the
pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle textures for Orianna grouped by the effect of ours
they inform).
The effects are the views the kit binds (tools/kit/build_orianna.py): the Ball itself three ways - beside a champion
(view_buffs home, on her, and e_def, on the ally it rides), lying on the ground (view_effects b_ground, re-stamped every
b_step ticks) and flying (view_projectiles q_ball, e_ball, b_back) - and a_bolt, a_hit, q_land, q_hit, b_home_in, w_ring,
w_hit, e_shield, e_hit, r_wave, r_hit, the buffs w_slow, w_haste. League's colours: her Ball's electric blue-white light
(its cyan core, the azure arcs), the clockwork gold of the gears and rune circles; light gets no outline, the Ball does.
Red side: the flying pictures symmetric top to bottom (they turn with the flight); the Ball beside a champion sits on one
side (the game never mirrors it: on the red side it floats behind her, as League's Ball trails her); everything else
symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "or_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "orianna", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_orianna")
HD = os.path.join(ROOT, "assets", "source", "orianna", "hd")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


ELEC = "#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E"     # her Ball's light: white core, pale cyan to deep blue
GEAR = "#FFF4C4, #FFD75E, #E7A41C, #A36608"                       # the clockwork gold of gears and rune circles
BALL = "#EDECEC, #ADADAF, #706F73, #323231, #FDE949, #F39D00, #C26700, #3C2003, #C59DF7, #040208"   # the Ball itself
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest "
        "shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
EL = f"an electric blue ramp ({ELEC})"
GO = f"a clockwork gold ramp ({GEAR})"
BA = f"the Ball's own colours ({BALL})"
THE_BALL = ("THE BALL (image 2 shows it at 8x): a round SILVER METAL SPHERE 10 squares across with a 1-square near-black "
            "outline (the Ball is a solid object: it keeps its outline), steel-silver shades lit from the upper left, dark "
            "engraved swirls, two small pale violet window panels, TWO COPPER-GOLD BANDS round its middle and a golden curved "
            "ridge over its top")


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


TB = "SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down)"
LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
FIG = "an upright girl 21 squares wide and 38 tall stands in the middle, not drawn"
SIDE = (12, -20)                  # the Ball beside a champion: its centre this far from the feet's middle (game px)

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the Ball
    ("ball_side", "球漂在英雄身边（跟随，循环），6 帧",
     "view_buffs `league_orianna_home`（在她身上）和 `league_orianna_e_def`（挂在队友身上），tag `ball_side`", "48 × 44",
     "球在她（或队友）身边漂着：照附图 2 的球画成 10 格大，**中心在人物脚下中点右边 12 格、离地 20 格**的地方（附图 4 里的位置），"
     "上下慢慢浮动 1 格，球面上的高光轻轻转，周围一圈很淡的蓝色电光、偶尔一两道小电弧。人物不画（格子中间留空）。"
     "**这张不左右对称**（球在右边），游戏不会镜像它。",
     f"{BA} and {EL}",
     f"THE BALL FLOATING BESIDE A FIGURE, 6 frames, a seamless loop ({FIG}). {THE_BALL}; its centre 12 squares RIGHT of the "
     "figure's middle and 20 squares above the ground, bobbing up and down by 1 square (frames 1-6: 0, -1, -1, 0, +1, +1), "
     "its highlight sliding round a little; round it a faint electric blue glow 1-2 squares wide, a tiny blue arc crackling on "
     "frames 2 and 5. Nothing else in the cell.",
     row(6, 48, 44) + "; the figure's feet (not drawn) on the cell's bottom row, its middle at column 24."),
    ("ball_ground", "球停在地上（不跟随，每 0.25 秒盖一次），2 帧",
     "view_effects `league_orianna_b_ground`（不跟随，地上；左右对称）", "14 × 18",
     "Q 扔出去后球停在落点：同一个球，浮在离地 5 格的地方，脚下一小块深蓝色的影子，带很淡的蓝色电光。两帧：球高一格、低一格（游戏里每 0.25 秒盖一次，两帧要能连着循环）。**左右对称**（球本身的花纹可以照原样，不用强行对称）。",
     f"{BA} and {EL}",
     f"THE BALL HOVERING OVER THE GROUND, 2 frames, a seamless loop. {THE_BALL}; its bottom 5 squares above the cell's bottom "
     "row (frame 2: 1 square lower); a flat dark navy shadow ellipse 8 squares wide and 2 tall on the bottom row under it; a "
     "faint electric blue glow 1 square round the Ball.",
     row(2, 14, 18) + "; the Ball centered across."),
    ("ball_fly", "球飞出去（投射物，朝飞行方向转，循环），4 帧",
     "view_projectiles `league_orianna_q_ball`、`e_ball`、`b_back`（朝飞行方向转，画成朝右飞；上下对称），tag `ball_fly`", "26 × 12",
     "Q 扔球、E 送球、球飞回来都用这张：球（10 格）在右边，身后拖一条蓝白色的电光尾迹，往左变细变淡，几颗电火星。**上下对称**（球的花纹可以照原样）。",
     f"{BA} and {EL}",
     f"THE BALL FLYING to the RIGHT, 4 frames, a seamless loop, {TB} (the Ball's own markings may stay as they are). "
     f"{THE_BALL}; the Ball at the RIGHT end of the cell, behind it a tapering electric blue-white trail 14 squares long, "
     "brightest next to the Ball, 2-3 small blue sparks along it at mirrored places, flickering between frames.",
     row(4, 26, 12) + "; the Ball 1 square from the RIGHT edge, vertically centered."),
    # ---- the attack
    ("a_bolt", "普攻：发条电弹（投射物，朝目标飞），3 帧",
     "view_projectiles `league_orianna_a_bolt`（朝飞行方向转，画成朝右飞；上下对称）", "10 × 6",
     "她手一挥射出的小电弹：一颗蓝白色的电光小球，后面一小段电光尾巴（参考 BA_Lightning、BA_Sparks）。**上下对称**。",
     EL,
     f"a SMALL ELECTRIC BOLT flying to the RIGHT, 3 frames, a seamless loop, {TB}: a white-cyan orb 3 squares at the right end, a "
     "thin blue crackling tail 6 squares long behind it.",
     row(3, 10, 6) + "; the orb 1 square from the RIGHT edge."),
    ("a_hit", "普攻命中（目标身上），4 帧", "view_effects `league_orianna_a_hit`（跟随，画在人物上面；左右对称）", "10",
     "电弹打中：一小团蓝白色电光炸开，几道短电弧。**左右对称**。约 10 格。", EL,
     f"a SMALL ELECTRIC HIT on a unit, 4 frames, {LR}: 1 a white dot 2 squares; 2 a cyan flash 7 squares with a white core; 3 the "
     "flash 10 squares, 4 short blue arcs at mirrored places; 4 a few fading blue motes.",
     row(4, 12, 12) + CENTER),
    # ---- Q Command: Attack
    ("q_land", "Q 指令：攻击：球落地的电击（地上，不跟随），5 帧",
     "view_effects `league_orianna_q_land`（不跟随，地上、人物下面；左右对称）", "34 × 16",
     "球砸到落点：地上炸开一圈蓝白色的电光环（扁椭圆，直径 32 格），中间一下白色闪光，几道电弧往外跳（参考 BA_Shockwave、Z_shockWave、BA_Sparks）。**左右对称**。",
     EL,
     f"an ELECTRIC BURST on the ground, 5 frames, {LR}: 1 a white flash 8 squares on the ground; 2 a flat cyan ring 18 wide and 6 "
     "tall with a bright white rim, a short burst of light rising 6 squares in the middle; 3 the ring 30 wide and 10 tall, 6 short "
     "blue arcs jumping out at mirrored places; 4 the ring 34 wide and fading; 5 the last motes.",
     row(5, 36, 18) + "; centered across, the ring's middle 5 squares above the cell's bottom row."),
    ("q_hit", "Q 命中（目标身上），5 帧", "view_effects `league_orianna_q_hit`（跟随，画在人物上面；左右对称）", "14",
     "球打中：一团蓝白色电光，一颗四角星光闪一下，几道电弧。**左右对称**。约 14 格。", EL,
     f"an ELECTRIC IMPACT on a unit, 5 frames, {LR}: 1 a white flash 4 squares; 2 a cyan burst 9 squares with a white core; 3 a "
     "four-pointed white-cyan star 14 squares across over the burst, 6 short blue arcs at mirrored places; 4 the star fading, "
     "sparks flying out; 5 fading motes.",
     row(5, 16, 16) + CENTER),
    ("b_home_in", "球回到她身边的一闪（她身边，不跟随），4 帧",
     "view_effects `league_orianna_b_home_in`（在她身上，不跟随），位置和 ball_side 的球一样", "48 × 44",
     "球飞回来、落回她身边的那一下：在 ball_side 的球的位置（人物脚下中点右边 12 格、离地 20 格）一下蓝白色闪光和一圈小光环。人物和球都不画。**不左右对称**（在球的位置）。",
     EL,
     f"a SMALL ELECTRIC SPARKLE where the floating Ball sits, 4 frames ({FIG}): centred 12 squares RIGHT of the figure's middle "
     "and 20 squares above the ground: 1 a white flash 4 squares; 2 a cyan ring 12 squares across with a white core; 3 the ring "
     "14 squares and fading, 4 tiny sparks; 4 the last motes. No Ball, no figure.",
     row(4, 48, 44) + "; the figure's feet (not drawn) on the cell's bottom row, its middle at column 24."),
    # ---- W Command: Dissonance
    ("w_ring", "W 指令：杂音：球的电磁脉冲（地上，不跟随），6 帧",
     "view_effects `league_orianna_w_ring`（不跟随，地上、人物下面；左右对称；大图表）", "50 × 22",
     "W：以球为中心炸开一个电磁场：地上一圈蓝色的电光环（扁椭圆，直径 48 格），环上是金色的发条符文圈（四个菱形尖角，参考 Orb_Rune、W_timerwheels），"
     "圈里噼啪跳着蓝白色的电弧，中间往上冲起一下蓝白色的脉冲光（参考 W_Flare、W_Shockwave、W_Gears、BA_Lightning）。**左右对称**。",
     f"{EL} and {GO}",
     f"an ELECTROMAGNETIC PULSE on the ground, 6 frames, {LR}: 1 a white flash 10 squares on the ground and a short white-cyan "
     "column of light 12 squares tall rising from it; 2 a flat cyan ring 28 wide and 9 tall with a white rim, the light column "
     "brightest; 3 the ring 48 wide and 16 tall, a thin golden clockwork rune circle just inside it with four small diamond "
     "points at front, back, left and right, white-blue lightning arcs crackling between the middle and the ring at mirrored "
     "places; 4 the same, the arcs moved, the column fading; 5 the ring and the runes fading, a few arcs left; 6 the last "
     "motes on the ring.",
     row(6, 50, 24) + "; centered across, the ring's middle 8 squares above the cell's bottom row."),
    ("w_hit", "W 命中（目标身上），4 帧", "view_effects `league_orianna_w_hit`（跟随，画在人物上面；左右对称）", "14",
     "被杂音电到：目标身上一团蓝白色电光和几道往外的电弧。**左右对称**。约 14 格。", EL,
     f"an ELECTRIC ZAP on a unit, 4 frames, {LR}: 1 a white flash 4 squares; 2 a cyan burst 10 squares with a white core; 3 the "
     "burst 14 squares with 6 zigzag blue arcs at mirrored places; 4 fading motes.",
     row(4, 16, 16) + CENTER),
    ("w_slow", "W 减速（敌人脚下，循环），4 帧", "view_buffs `league_orianna_w_slow`（跟随，画在人物下面；左右对称）", "16 × 5",
     "被杂音减速：敌人脚下一圈淡淡的蓝色电光环，几道小电弧轮流闪。**左右对称**。", EL,
     f"a FAINT ELECTRIC RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 14 squares wide and 4 "
     "tall in dim blue, 2 tiny white-blue arcs on it at mirrored places taking turns to flash.",
     row(4, 16, 6) + CENTER),
    ("w_haste", "W 加速（队友脚下，循环），4 帧", "view_buffs `league_orianna_w_haste`（跟随，画在人物下面；左右对称）", "18 × 8",
     "被杂音加速：队友脚下一圈淡淡的亮青色光环，两边几道往后飘的青色速度线。**左右对称**。", EL,
     f"a FAINT CYAN SPEED RING under a figure's feet, 4 frames, a seamless loop, {LR}: a thin flat ellipse 16 squares wide and 5 "
     "tall in pale cyan, at both ends 2 short cyan streaks rising and fading in turns.",
     row(4, 18, 8) + CENTER),
    # ---- E Command: Protect
    ("e_shield", "E 指令：防卫：护盾（人物身上，跟随），6 帧",
     "view_effects `league_orianna_e_shield`（跟随，画在人物上面；左右对称）", "28 × 42",
     "球送到身上的护盾：一层淡淡的蓝白色光罩包住人物（椭圆，宽 26、高 40），顶上一道亮的月牙形高光慢慢转，几颗小电光点在罩子上闪（参考 Shield、Ring_Smooth）。"
     f"**左右对称**，中间身体位置留空（{FIG}），罩子要淡，不要盖住人。最后一帧淡出。",
     EL,
     f"a FAINT ELECTRIC SHIELD BUBBLE round a figure, 6 frames, {LR} ({FIG}): an ellipse outline 26 wide and 40 tall in pale cyan "
     "1 square thick, a bright white crescent highlight on its top third; frames 1-5 the crescent sliding a little left and right "
     "symmetrically while 4 tiny white sparks twinkle on the bubble at mirrored places; frame 6 the bubble fading.",
     row(6, 28, 42) + "; centered across, the figure's feet (not drawn) 1 square above the cell's bottom row."),
    ("e_hit", "E 球路过打中的敌人（目标身上），4 帧", "view_effects `league_orianna_e_hit`（跟随，画在人物上面；左右对称）", "12",
     "E 的球路过时打中：一小团蓝色电光和两道短电弧。**左右对称**。约 12 格。", EL,
     f"a SMALL ELECTRIC HIT on a unit, 4 frames, {LR}: 1 a white dot 3 squares; 2 a cyan flash 8 squares; 3 the flash 12 squares "
     "with 4 short blue arcs at mirrored places; 4 fading motes.",
     row(4, 14, 14) + CENTER),
    # ---- R Command: Shockwave
    ("r_wave", "R 指令：冲击波：球的蓄力和冲击波（地上，不跟随），9 帧",
     "view_effects `league_orianna_r_wave`（不跟随，地上、人物下面；左右对称；大图表）", "76 × 44",
     "R：先蓄力 0.5 秒：以球的位置为中心，四周的蓝色电光和金色发条碎光旋转着往中间收（参考 R_Swirl_OuterRing、R_ballswirl、R_Streaks、R_Swipe），中间越来越亮；"
     "然后爆开：一道往上冲的蓝白色强光柱，地上一个巨大的蓝色冲击波环往外推开（扁椭圆，直径 72 格），环里是旋转的电光条纹，最后淡掉（参考 R_Shockwave_Pan、R_InvertedGlow、Z_shockWave）。**左右对称**。",
     f"{EL} and {GO}",
     f"a GATHERING VORTEX then a SHOCKWAVE, 9 frames, {LR}; the centre is a point 8 squares above the cell's bottom row "
     "(where the Ball hovers): 1 a faint blue swirl 40 squares wide and 14 tall round the centre on the ground, small gold "
     "clockwork sparks on it; 2 the swirl 32 wide, brighter, blue streaks curving inward at mirrored places; 3 the swirl 24 "
     "wide, a white-cyan glow 6 squares at the centre; 4 the swirl 14 wide, the glow 10 squares, brightest; 5 everything sucked "
     "into a white point 4 squares; 6 THE BLAST: a white-cyan column of light 8 squares wide rising 36 squares from the centre, a "
     "flat cyan shockwave ring 36 wide and 12 tall with a white rim on the ground; 7 the ring 60 wide and 20 tall, blue electric "
     "streaks swirling inside it, the column fading; 8 the ring 72 wide and 24 tall, fading, sparks at its rim at mirrored "
     "places; 9 the last faint arcs of the ring.",
     row(9, 76, 44) + "; centered across, the centre 8 squares above the cell's bottom row."),
    ("r_hit", "R 命中（目标身上），4 帧", "view_effects `league_orianna_r_hit`（跟随，画在人物上面；左右对称）", "18",
     "被冲击波打中：目标身上一团大的蓝白色电光爆开，几道往外的电弧。**左右对称**。约 18 格。", EL,
     f"a BIG ELECTRIC IMPACT on a unit, 4 frames, {LR}: 1 a white flash 6 squares; 2 a cyan burst 12 squares with a white core; 3 "
     "the burst 18 squares with 8 zigzag blue arcs at mirrored places; 4 fading motes.",
     row(4, 20, 20) + CENTER),
]

GROUPS = [
    ("a_bolt a_hit q_*", ["Orianna_Base_BA_Lightning_flipbook", "Orianna_Base_BA_Shockwave02", "Orianna_Base_BA_Sparks01",
                          "Orianna_Base_Q_Trail", "Orianna_Base_Z_hiteffect", "Orianna_Base_Z_shockWave"]),
    ("ball_* e_shield", ["Orianna_Base_Orb_Rune", "Orianna_Base_Glow02", "Orianna_Base_Shield", "Orianna_Ring_Smooth",
                         "Orianna_Base_Trail01", "Orianna_Base_Z_flash32"]),
    ("w_ring w_hit w_*", ["Orianna_Base_W_Flare", "Orianna_Base_W_Shockwave", "Orianna_Base_W_Gears",
                          "Orianna_Base_W_timerwheels", "Orianna_Base_Gear_1_TX", "Orianna_Base_W_Aura_Self"]),
    ("r_wave r_hit", ["Orianna_Base_R_Swirl_OuterRing", "Orianna_Base_R_ballswirl", "Orianna_Base_R_Streaks",
                      "Orianna_Base_R_Swipe", "Orianna_Base_R_Shockwave_Pan", "Orianna_Base_R_InvertedGlow"]),
]
# the action frames the pictures start from: (tag, frame, what)
SHOTS = [("attack", 3, "a_bolt：普攻出手"), ("skill", 2, "q_ball：Q 指挥球"), ("skill_w", 2, "w_ring：W"),
         ("skill_e", 2, "e_ball：E 送球"), ("ult", 5, "r_wave：R 冲击波")]


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
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Orianna_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def sheet_frames(tag):
    anims = json.load(open(lp(SHEET + "#anim.fanim"), encoding="utf-8-sig"))["anims"]
    sh = Image.open(lp(SHEET + "#sheet.png")).convert("RGBA")
    out = []
    for fr in anims[tag]["frames"]:
        r = fr["data"]
        out.append(np.asarray(sh.crop((int(r["x"]), int(r["y"]), int(r["x"] + r["w"]), int(r["y"] + r["h"])))))
    return out


def size_sheet(path):
    """Her 1x idle (the frame centred on the pivot: its middle column is the pivot, the soles 11 under it) at 4x with the
    Ball's place marked, the base fighter beside her, a 10-px ruler."""
    import tfm2_ase as T
    f = sheet_frames("idle")[0]
    H, W = f.shape[:2]
    piv_x, piv_y = W // 2, H // 2
    soles = piv_y + 11
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    k = k[ky.min():ky.max() + 1, kx.min():kx.max() + 1]
    Z, pad = 4, 8
    cols = pad + W + 20 + pad + k.shape[1] + pad
    top = max(soles, k.shape[0]) + pad
    img = Image.new("RGBA", (cols * Z, (top + 4) * Z + 64), (104, 112, 72, 255))
    base = top
    img.alpha_composite(Image.fromarray(f[:soles]).resize((W * Z, soles * Z), Image.NEAREST), (pad * Z, (base - soles) * Z + 64))
    d = ImageDraw.Draw(img)
    # the Ball's place: SIDE from the feet's middle (the pivot column)
    bx, by = pad + piv_x + SIDE[0], base + SIDE[1]
    d.ellipse([((bx - 5) * Z, (by - 5) * Z + 64), ((bx + 5) * Z, (by + 5) * Z + 64)], outline=(0, 255, 255, 255), width=2)
    x2 = pad + W + 20
    img.alpha_composite(Image.fromarray(k).resize((k.shape[1] * Z, k.shape[0] * Z), Image.NEAREST),
                        (x2 * Z, (base - k.shape[0]) * Z + 64))
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    px = (pad + piv_x) * Z + Z // 2
    d.line([(px, base * Z + 64 - 12), (px, base * Z + 64 + 12)], fill=(255, 255, 0, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, cols, 10):
        xx = (pad + i) * Z
        d.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    ys, xs = np.nonzero(f[..., 3] > 0)
    d.text((8, 36), f"奥莉安娜 {xs.max() - xs.min() + 1}×{soles - ys.min()} 格（4 倍；黄线 = 脚下中点，青圈 = 球的位置），原版斗士 "
                    f"{k.shape[1]}×{k.shape[0]} 格", fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return (soles - ys.min(), xs.max() - xs.min() + 1)


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
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 220), sub.shape[0] * Z + 24), (104, 112, 72, 255))
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
    h, w = shape
    L = []
    a = L.append
    a("# 发条魔灵 奥莉安娜：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张图：她的球（3 张）和技能特效。** 造型和动作已定（`design/orianna_idle.png`：3/4 正面朝右，金色短发和发髻、"
      f"瓷白的脸、青绿眼睛、银色胸甲、金色齿轮裙、分节金属四肢）。她在游戏里是**高清**的（每个游戏格子里 2.2×2.2 个细像素），{h} 格高、{w} 格宽；"
      "**特效和球照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - **球**是她的武器，游戏里是单独的一张图，会出现在三个地方：漂在她（或被 E 送到的队友）身边、Q 扔出去后停在地上、飞来飞去。"
      "三张球的图都照 `design/orianna_ball.png`（你第 1 步画的第 2 稿球，8 倍放大）画，**直径 10 格**，银色金属球、两道铜金色环、顶上金脊、淡紫色小窗格，"
      "**球是实物，保留一圈近黑描边**。")
    a("> - 大小对照 `design/orianna_size.png`：她的待机放大 4 倍，脚底在红线上，黄线是脚下中点（她的站位点），**青色圈是球漂在她身边的位置**（脚下中点右边 12 格、离地 20 格），"
      "上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/orianna_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奥莉安娜自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。"
      "颜色照英雄联盟原版：**球的能量是蓝白色的电光（白芯、青色到深蓝）**，**符文圈和齿轮是发条金色**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈，中间身体位置留空**，要淡一点，不要盖住人。")
    a("> - **方向（重要，红色方不会镜像）**：飞出去的 `ball_fly`、`a_bolt` 画成朝右，**上下对称**（往左时会上下翻；球自己的花纹可以照原样）。"
      "`ball_side`、`b_home_in` 的球在人物右边（这两张不对称，游戏里红色方时球会漂在她身后，没关系）。"
      "其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `orianna_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `orianna_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「发条协奏」 | 手一挥射出发条电弹，连续普攻叠加魔法伤害 | `a_bolt` · `a_hit` |")
    a("| 球 | 漂在她身边；Q 扔出去停在地上；E 送到队友身上；离太远或停太久会飞回来 | `ball_side` · `ball_ground` · `ball_fly` · `b_home_in` |")
    a("| 技能 1 = Q「指令：攻击」+ W「指令：杂音」 | Q 把球扔到敌人脚下；球附近有敌人时 W 自动放电，敌人减速、队友加速 | `q_land` · `q_hit` · `w_ring` · `w_hit` · `w_slow` · `w_haste` |")
    a("| 技能 2 = E「指令：防卫」 | 把球送给队友（或自己），加护盾，路过的敌人受伤 | `e_shield` · `e_hit` |")
    a("| 大招「指令：冲击波」 | 球蓄力 0.5 秒后放出冲击波，把周围敌人甩向球 | `r_wave` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电弧、火星、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**（球例外：球是实物，有一圈近黑描边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("电光蓝（球的能量、电弧、冲击波）", ELEC), ("发条金（符文圈、齿轮碎光）", GEAR), ("球本身", BALL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。")
    a("- 画在人物身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张图的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 落点半径 16000，"
      "W 半径 24000，R 半径 36000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `orianna_fx_{name}.png`：{title}\n")
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
        a(f"| `orianna_fx_{name}` | {bind} | {size} |")
    a("")
    a("- 两张表：`asset/league/effects/league_orianna_fx`（小的）和 `league_orianna_big`（w_ring、r_wave），tag = 名字；"
      "build_orianna.py 的 views 里 home 和 e_def 绑 tag `ball_side`，q_ball / e_ball / b_back 绑 tag `ball_fly`（b_ally 不再用：球挂在队友身上改为 e_def 的 view_buffs）。")
    a("- `ball_ground` 每 b_step（15 tick = 250 ms）盖一次：两帧各 125 ms；`r_wave` 的第 6 帧（冲击）要在 r_delay（30 tick = 500 ms）时出现；`e_shield` 盖满护盾 e_t（150 tick）。")
    a("- 用 `pixel_1x/` 切格（import_pantheon_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（球除外）；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="orianna_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "orianna_packs"), help="folder for the zip")
    a = ap.parse_args()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run work/or/fx_ref_or.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    des = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(des, 4, 0), 4, 1)).save(os.path.join(out, "design", "orianna_idle.png"))
    ball = np.asarray(Image.open(lp(os.path.join(HD, "ball.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (ball.shape[1] * 8 + 32, ball.shape[0] * 8 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(ball, 8, 0), 8, 1)), (16, 16))
    bg.convert("RGB").save(os.path.join(out, "design", "orianna_ball.png"))
    shape = size_sheet(os.path.join(out, "design", "orianna_size.png"))
    shots_sheet(os.path.join(out, "design", "orianna_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"orianna_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
