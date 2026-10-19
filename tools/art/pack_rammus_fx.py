#!/usr/bin/env python3
"""Build rammus_fx_pack.zip: step 3 of Rammus's sprite - Codex draws his effects (pack_poppy_fx.py's way).

    python <scratchpad>/fx_ref_ra.py           # League's particle textures -> C:/t/ra_work/fxref (Riot's art, local only)
    python tools/art/pack_rammus_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name rammus_fx_redo_pack]

The pack (C:/t/ra_work/fx/rammus_fx_pack, zipped into --out, default dist/rammus_packs) holds PROMPTS.md (also written to
assets/source/rammus/PROMPTS_FX.md), design/rammus_idle.png (his idle at 4x, the design's squares at PPU 1.2),
design/rammus_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/rammus_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Rammus grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_rammus.py): view_effects a_hit, q_dust, q_burst, q_hit, w_cast,
e_hit, r_land, r_shock, r_hit; view_buffs q_slow, w_on, e_taunt, r_slow. League's colours: his light is the gold of his
shell (the spike shield, the impacts), Powerball and Soaring Slam throw up desert sand and rock chips, the slam's crater
glows with orange cracks, the taunt is a red-orange flare. Red side: the client never mirrors an effect picture, so every
picture is symmetric left to right (no projectile pictures: Powerball is his own body).
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
TMP = "C:/t/ra_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "rammus", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_rammus")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "rammus_fx_pack"
SIZE_LABEL = "拉莫斯"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


GOLD = "#FFFFFF, #FFF2C0, #FFD266, #F2A630, #C06E18, #7A3E10"       # the shell's light: spike shield, impacts
SAND = "#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A"       # desert sand, dust
ROCK = "#D8C8A8, #A89070, #7A6448, #50402E, #2E241A"                # rock chips (solid: outlined)
LAVA = "#FFF4B0, #FFC040, #FF7A1A, #C83C10, #6E1C0A"                # the slam's glowing cracks
RAGE = "#FFFFFF, #FFD8B0, #FF9A4A, #F05A24, #B8301A, #6E1A12"       # the taunt's flare
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with "
        "its lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
GO = f"a gold light ramp ({GOLD})"
SA = f"a desert sand ramp ({SAND})"
RO = f"a rock ramp ({ROCK})"
LA = f"a glowing lava-crack ramp ({LAVA})"
RA = f"a red-orange flare ramp ({RAGE})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
HIM = ("the squat armadillo stands in the middle, not drawn: 36 squares from his tallest spike to the ground, about 35 "
       "squares wide")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_hit", "普攻：翻跟头撞中目标，3 帧", "view_effects `league_rammus_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "他整个翻过去用甲壳撞中目标的一下：一团金白色的撞击闪光，四周溅出几粒沙子（参考 common_hiteffect、spark）。**左右对称**，约 16 × 16 格。",
     f"{GO} and {SA}",
     "A HEAVY IMPACT FLASH, 3 frames, " + LR + ": 1 a white-gold burst 8 squares across with 8 short rays; 2 the burst "
     "12 squares across, its rays longer and gold, 6 sand grains (1-2 squares) flying out; 3 only a fading gold ring 14 "
     "squares across and the grains further out.",
     row(3, 16, 16) + CENTER),
    # ---- Q Powerball
    ("q_dust", "Q 动力冲刺：滚动时球下的沙尘（跟着他，循环），4 帧",
     "view_effects `league_rammus_q_dust`（跟随，画在人物下面 z -1；左右对称；滚动时一直在放）", "44 × 14",
     "缩成球滚动的时候，球底下翻起的一团沙尘：贴着地面的扁扁的沙团，左右两边各甩起一小股沙，几道金色的速度线（参考 rollingforce、"
     "sandstreaks、smokeerode）。**只画在地面线附近（球在上面，不画球）**。**左右对称**，4 帧循环。",
     f"{SA} and {GO}",
     "ROLLING DUST under a ball, 4 frames, a seamless loop, " + LR + ": a low flat cloud of sand on the ground (an ellipse "
     "40 squares wide and 8 tall, puffy edge, lighter on top), two small sand plumes kicked up at its left and right ends "
     "(mirrored), 4 short gold speed streaks just above it; each frame the puffs boil and the plumes rise and fall.",
     row(4, 44, 14) + "; centered across, the cloud's bottom on the cell's bottom row."),
    ("q_burst", "Q：撞上目标时炸开（他身边，跟随），5 帧",
     "view_effects `league_rammus_q_burst`（跟随，画在人物下面 z -1；左右对称；大图表）", "48 × 28",
     "球撞上敌人的一瞬间：脚下炸开一圈沙尘冲击波（半径约 18 格，地上的椭圆），中间一团金色的闪光，碎沙往外飞（参考 cloudring、"
     "air_swoosh、common_dustcloud）。**他的身体位置留空**（" + HIM + "）。**左右对称**，5 帧。",
     f"{SA} and {GO}",
     "A SAND SHOCKWAVE bursting out on the ground round a figure, 5 frames, " + LR + " (" + HIM + "): 1 a gold flash "
     "12 squares across at the ground; 2 a sand ring on the ground (an ellipse 24 squares wide and 9 tall, 2-3 squares "
     "thick, puffy) and the flash fading; 3 the ring 36 wide and 14 tall, sand grains flying out above it; 4 the ring 44 "
     "wide and 18 tall, thinner, breaking into puffs; 5 only scattered thin puffs. The middle above the ground empty.",
     row(5, 48, 28) + "; centered across, the ellipse's middle 9 squares above the cell's bottom row."),
    ("q_hit", "Q：撞中的敌人身上，3 帧", "view_effects `league_rammus_q_hit`（跟随敌人，画在人物上面 z 2；左右对称）", "16 × 16",
     "被球撞中的敌人：一团金色的撞击闪光和几粒飞溅的沙（参考 common_hiteffect、spark_round_bloom）。**左右对称**，约 16 × 16 格。",
     f"{GO} and {SA}",
     "AN IMPACT FLASH, 3 frames, " + LR + ": 1 a white-gold star 7 squares across; 2 the star 11 across with 4 sand grains "
     "flying out; 3 a fading gold ring 13 across and the grains further out.",
     row(3, 16, 16) + CENTER),
    ("q_slow", "Q：被减速的敌人脚下的沙（循环），4 帧",
     "view_buffs `league_rammus_q_slow`（跟随，画在人物下面 z 3；左右对称；循环，1 秒）", "20 × 8",
     "被撞减速的敌人脚下：一小圈卷着的沙尘贴着地面转（参考 sandstreaks、smokeerode）。**左右对称**，4 帧循环。",
     SA,
     "SWIRLING SAND at a unit's feet, 4 frames, a seamless loop, " + LR + ": a flat ring of sand puffs on the ground (an "
     "ellipse 18 squares wide and 6 tall, 2 squares thick), a few grains lifting off it; each frame the puffs move round.",
     row(4, 20, 8) + "; centered across, the ellipse's bottom on the cell's bottom row."),
    # ---- W Defensive Ball Curl
    ("w_cast", "W 尖刺防御：蜷起来的一下（他身上，跟随），4 帧",
     "view_effects `league_rammus_w_cast`（跟随，画在人物上面 z 2；左右对称；大图表）", "48 × 46",
     "他蜷起来进入防御的一下：一圈金色的尖刺光从他身上往外一亮（像甲壳上的刺都在发光），一圈金色的光环炸开（参考 w_spikeshield、"
     "w_spikes、w_deflectionripples）。**只画外圈，他的身体位置留空**（" + HIM + "）。**左右对称**，4 帧。",
     GO,
     "A GOLD SPIKE-SHIELD FLARE round a figure, 4 frames, " + LR + " (" + HIM + "): 1 a ring of 12 short gold light "
     "spikes pointing outward round an empty oval 34 squares wide and 34 tall; 2 the spikes longer (5 squares) with white "
     "tips and a thin gold ring behind them; 3 the ring 44 squares across expanding, the spikes fading; 4 only a faint "
     "thin ring 46 across. The middle (the figure) empty.",
     row(4, 48, 46) + "; centered across, the oval's middle 18 squares above the cell's bottom row."),
    ("w_on", "W：尖刺防御开着（他身上，循环），4 帧",
     "view_buffs `league_rammus_w_on`（跟随，画在人物上面 z 3；左右对称；循环，7 秒）", "44 × 42",
     "防御开着的 7 秒：他身边一圈淡淡的金色光壳，壳上几根金色小尖刺一闪一闪（参考 w_spikeshield_blur、soccershield）。**只画外圈的"
     "壳和刺，中间留空**（" + HIM + "）。**左右对称**，4 帧循环。",
     GO,
     "A FAINT GOLD SPIKED SHELL round a figure, 4 frames, a seamless loop, " + LR + " (" + HIM + "): a thin gold outline "
     "of light (1 square, no fill) round an empty oval 40 squares wide and 38 tall, 8 small gold spikes (3 squares) on "
     "it at mirrored places; each frame a different pair of spikes glints white.",
     row(4, 44, 42) + "; centered across, the oval's bottom 1 square above the cell's bottom row."),
    # ---- E Frenzying Taunt
    ("e_hit", "E 狂乱嘲讽：被嘲讽的敌人身上（跟随），4 帧",
     "view_effects `league_rammus_e_hit`（跟随敌人，画在人物上面 z 2；左右对称）", "24 × 28",
     "被嘲讽的一瞬间：敌人身上一团红橙色的火光往上冲，两道红橙色的光弧绕着他（参考 e_terrify_beam、e_energy_01、e_slash）。"
     "**左右对称**（" + CHAMP + "）。",
     RA,
     "A RED-ORANGE TAUNT FLARE on a figure, 4 frames, " + LR + " (" + CHAMP + "): 1 a red-orange flash 10 squares across "
     "at its chest (18 squares up); 2 two mirrored flame-like arcs rising round it from the ground to 30 squares up, white "
     "cores; 3 the arcs higher and thinner, a ring of sparks at its feet; 4 only fading sparks rising.",
     row(4, 24, 28) + "; centered across, the figure's feet on the cell's bottom row."),
    ("e_taunt", "E：被嘲讽的敌人头上（循环），4 帧",
     "view_buffs `league_rammus_e_taunt`（跟随，画在人物上面 z 3；左右对称；循环）", "12 × 10",
     "被嘲讽期间敌人头上：一个红橙色的怒气标记（两道交叉的小火焰 / 一个红色的「！」形光），一跳一跳（参考 e_buff、e_solar_tag）。"
     "**画在头上**（" + CHAMP + "，标记在 36–44 格高）。**左右对称**。",
     RA,
     "AN ANGER MARK over a unit's head, 4 frames, a seamless loop, " + LR + ": a small red-orange flame-like mark (a "
     "vertical bar 2 squares wide and 6 tall with a dot under it, white core, glowing edge) with 2 tiny sparks at its "
     "sides; each frame it pulses (1 row taller on frames 2 and 3) and the sparks flicker.",
     row(4, 12, 10) + CENTER),
    # ---- R Soaring Slam
    ("r_land", "R 冲天猛撞：砸在地上（地上，不跟随），6 帧",
     "view_effects `league_rammus_r_land`（不跟随，画在人物下面 z -1；左右对称；大图表）", "80 × 40",
     "他从空中砸下来的一下：地面上炸开一个大的沙尘冲击波环（半径约 36 格，地上的椭圆），中间砸出一个裂开的坑，裂缝里透出橙色的熔岩光，"
     "碎石往外飞（参考 r_ring_shockwave、r_craterobsi、r_craterlava、r_rocks、r_sand_smoke）。**左右对称**，6 帧。",
     f"{SA}, {RO} and {LA}",
     "A GROUND SLAM, 6 frames, " + LR + ": 1 a gold-white flash 14 squares across on the ground; 2 a cracked crater on "
     "the ground (an ellipse 26 wide and 9 tall, dark rock with 6 glowing orange cracks running out) and a sand ring "
     "round it (an ellipse 40 wide and 14 tall, puffy, 3 squares thick); 3 the sand ring 60 wide and 22 tall, 6 rock chips "
     "(3x3, solid, a dark edge) flying out above it at mirrored places; 4 the ring 76 wide and 28 tall, thinner, the chips "
     "falling; 5 the ring breaking into puffs, the crater's cracks dimmer; 6 only the crater with faint cracks and thin "
     "puffs.",
     row(6, 80, 40) + "; centered across, the ellipses' middle 14 squares above the cell's bottom row."),
    ("r_shock", "R：余震（地上，不跟随），4 帧",
     "view_effects `league_rammus_r_shock`（不跟随，画在人物下面 z -1；左右对称；大图表；落地后放 3 次）", "76 × 32",
     "砸地之后的余震：同一个地方地面又震一下，一圈沙尘波从中间往外推（比落地那圈细），裂缝里的橙光闪一下（参考 r_ring_shockwave、"
     "crack_dissolve）。**左右对称**，4 帧。",
     f"{SA} and {LA}",
     "AN AFTERSHOCK on the ground, 4 frames, " + LR + ": 1 six short glowing orange cracks round an empty middle (an "
     "ellipse 24 wide and 8 tall); 2 a thin sand ring (2 squares thick) an ellipse 44 wide and 16 tall, the cracks bright; "
     "3 the ring 64 wide and 24 tall, fainter, the cracks dimming; 4 the ring 74 wide and 28 tall breaking into puffs.",
     row(4, 76, 32) + "; centered across, the ellipses' middle 12 squares above the cell's bottom row."),
    ("r_hit", "R：被砸中的敌人身上，3 帧", "view_effects `league_rammus_r_hit`（跟随敌人，画在人物上面 z 2；左右对称）", "16 × 16",
     "被砸中的敌人：一团沙尘和几块飞起来的碎石（参考 r_rocks、r_burstsmoke）。**左右对称**，约 16 × 16 格。",
     f"{SA} and {RO}",
     "A SAND AND ROCK BURST, 3 frames, " + LR + ": 1 a sand puff 8 squares across with a gold-white core; 2 the puff 12 "
     "across, 4 rock chips (2x2, solid, a dark edge) flying out at mirrored places; 3 the puff fading, the chips further "
     "out and lower.",
     row(3, 16, 16) + CENTER),
    ("r_slow", "R：被减速的敌人脚下裂开的地面（循环），2 帧",
     "view_buffs `league_rammus_r_slow`（跟随，画在人物下面 z 3；左右对称；循环，1.5 秒）", "20 × 8",
     "被冲天猛撞减速的敌人脚下：一小片裂开的地面，裂缝透着橙光，一明一暗（参考 r_craterlava、crack_dissolve）。**左右对称**，2 帧循环。",
     f"{RO} and {LA}",
     "CRACKED GLOWING GROUND at a unit's feet, 2 frames, a seamless loop, " + LR + ": a flat patch of dark cracked rock (an "
     "ellipse 18 wide and 6 tall) with 5 thin glowing orange cracks; 1 the cracks dim orange; 2 the cracks bright yellow.",
     row(2, 20, 8) + "; centered across, the ellipse's bottom on the cell's bottom row."),
]
BIG_FX = ["q_burst", "w_cast", "r_land", "r_shock"]
REDO = {}
GROUPS = [
    ("a_hit q_hit r_hit", ["common_hiteffect", "rammus_base_spark", "rammus_base_spark_round_bloom", "rammus_base_ba_tar_slash",
                           "rammus_base_r_rocks", "rammus_base_r_burstsmoke"]),
    ("q_dust q_burst q_slow", ["rammus_base_rollingforce", "rammus_base_sandstreaks", "rammus_base_smokeerode",
                               "rammus_base_cloudring", "common_dustcloud", "rammus_base_air_swoosh"]),
    ("w_cast w_on", ["rammus_base_w_spikeshield", "rammus_base_w_spikeshield_blur", "rammus_base_w_spikes",
                     "rammus_base_w_deflectionripples", "rammus_base_soccershield"]),
    ("e_hit e_taunt", ["rammus_base_e_terrify_beam", "rammus_base_e_energy_01", "rammus_base_e_slash", "rammus_base_e_buff",
                       "rammus_base_e_solar_tag", "rammus_base_e_beam_pulse"]),
    ("r_land r_shock r_slow", ["rammus_base_r_ring_shockwave", "rammus_base_r_craterobsi", "rammus_base_r_craterlava",
                               "rammus_base_r_rocks", "rammus_base_r_sand_smoke", "rammus_base_crack_dissolve"]),
]
FEET = 11.5                                           # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：翻跟头倒过来撞在前面的目标上（打中的目标身上）"),
         ("skill_roll", 1, "q_dust：球滚动时，在球底下"), ("skill_hit", 1, "q_burst：撞上目标时，以他为中心；q_hit 在敌人身上"),
         ("skill_w", 3, "w_cast / w_on：蜷起来防御，围着他"), ("skill2", 2, "e_hit / e_taunt：在被嘲讽的敌人身上 / 头上"),
         ("ult_land", 1, "r_land / r_shock：砸在地上的点（他落下的地方）"), ("idle", 1, "待机（大小参考）")]


def ref_sheet(path):
    S, LW = 170, 200
    cols = max(len(n) for _, n in GROUPS)
    sheet = Image.new("RGBA", (LW + cols * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            p = os.path.join(REF, nm + ".png")
            if not os.path.isfile(p):
                cand = [f for f in os.listdir(REF) if f.startswith(nm)]
                if not cand:
                    sys.exit(f"missing reference {p}")
                p = os.path.join(REF, sorted(cand)[0])
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("rammus_base_", "")[:26],
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


def first_1x(tag):
    f = sheet_frames(tag)[0]
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    import tfm2_ase as T
    figs = [first_1x("idle")]
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
    d.text((8, 36), f"{SIZE_LABEL} {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def shots_sheet(path):
    Z, PAD = 4, 12
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what in SHOTS:
        f = np.pad(sheet_frames(tag)[k - 1], ((PAD, PAD), (PAD, PAD), (0, 0)))
        px = f.shape[1] // 2
        ys, xs = np.nonzero(f[..., 3] > 0)
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is her pivot, FEET rows over the ground
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), pt[1])) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 440), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = int((pt[0] - x0) * Z), int((pt[1] - y0) * Z) + 24
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(0, 255, 255, 255), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(0, 255, 255, 255), width=2)
        d.text((4, 2), f"{tag} {k}: {what}", fill=(255, 255, 255, 255), font=font)
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
    """His idle at 4x, the design's own squares (PPU 1.2: 1.2 squares a game pixel)."""
    import rig_rammus as M
    F = M.form()
    c = F.rig.finish(M.frames(F)["idle"][0][0])
    ys, xs = np.nonzero(c[..., 3] > 0)
    t = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    bg = Image.new("RGBA", (t.shape[1] * 4 + 32, t.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(t, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 披甲龙龟 拉莫斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/rammus_idle.png`：3/4 正面朝右的矮胖犰狳，橙金色带尖刺的大甲壳，"
      f"甲壳前缘下探出绿色的小乌龟头和红眼睛，青绿鳞皮、米白爪子、黄褐肚子、暗红挽具）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个"
      f"细像素），{h} 格高、{w} 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/rammus_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/rammus_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里拉莫斯自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**他的光是甲壳的金色**（尖刺护盾、撞击），**动力冲刺和冲天猛撞掀起沙漠的黄沙和碎石**，"
      "**砸出的坑里透着橙色的熔岩裂纹**，**嘲讽是红橙色的火光**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像（这个英雄没有弹道图：动力冲刺就是他自己滚过去）。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 12]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `rammus_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/rammus_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「锥刺甲壳」在里面） | 整个翻一个跟头用甲壳撞过去，多一段魔法伤害 | `a_hit` |")
    a("| 技能 1 = Q「动力冲刺」 | 缩成刺球滚向敌人，撞上炸开，击退、减速 | `q_dust` · `q_burst` · `q_hit` · `q_slow` |")
    a("| W「尖刺防御」（敌方英雄靠近时自动开） | 蜷起来，7 秒内护甲魔抗提升、反伤 | `w_cast` · `w_on` |")
    a("| 技能 2 = E「狂乱嘲讽」 | 嘲讽一个敌方英雄 | `e_hit` · `e_taunt` |")
    a("| 大招「冲天猛撞」 | 缩成球跳起来砸进一片区域，减速，之后余震 3 次（刚滚完时中间的人被击飞） | `r_land` · `r_shock` · `r_hit` · "
      "`r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙尘、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（实心的东西例外：碎石可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色的光（尖刺护盾、撞击）", GOLD), ("沙漠黄沙", SAND), ("碎石（实心）", ROCK), ("熔岩裂纹的橙光", LAVA),
                        ("嘲讽的红橙火光", RAGE)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 撞击的半径 18000，大招的半径 36000、"
      "中心 18000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `rammus_fx_{name}.png`：{title}\n")
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
        a(f"| `rammus_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_rammus_fx`（小的）和 `league_rammus_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_rammus.py 的 views）。")
    a("- `q_dust` 在滚动时循环（附加包的整身滚球也放它）；`r_shock` 落地后每 70 tick 放一次、共 3 次；`r_land`、`r_shock` 不跟随（地上的点）。"
      "全部左右对称。")
    a("- 用 `pixel_1x/` 切格（import_poppy_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（碎石保留描边）；核对交回的张数和"
      "这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"



def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="rammus_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "rammus_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run fx_ref_ra.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "rammus_idle.png"))
    shape = size_sheet(os.path.join(out, "design", "rammus_size.png"))
    shots_sheet(os.path.join(out, "design", "rammus_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"rammus_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
