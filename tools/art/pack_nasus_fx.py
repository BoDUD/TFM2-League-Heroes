#!/usr/bin/env python3
"""Build nasus_fx_pack.zip: step 3 of Nasus's sprite - Codex draws his effects (pack_swain_fx.py's way).

    python work/nas/fx_ref_nas.py            # League's particle textures -> %TEMP%/nas_work/fxref (Riot's art, local only)
    python tools/art/pack_nasus_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name nasus_fx_redo_pack]

The pack (%TEMP%/nas_work/fx/nasus_fx_pack, zipped into --out, default dist/nasus_packs) holds PROMPTS.md (also written to
assets/source/nasus/PROMPTS_FX.md), design/nasus_idle.png (his two forms at 4x: A and Fury of the Sands' big body),
design/nasus_size.png (both 1x idles at 4x on the arena colour with the feet line, a 10-px ruler and the base fighter),
design/nasus_shots.png (the finished action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own
particle textures for Nasus grouped by the effect of ours they inform).
The effects are the views the kit binds (tools/kit/build_nasus.py: no projectile picture - every blow flies unseen, the
swing is in his frames; view_effects a_hit, q_hit, q_soul, e_fire, e_hit, w_hit, r_cast, r_hit; view_buffs w_slow,
e_shred, r_on). League's colours: Siphoning Strike and Spirit Fire violet with a white core, Spirit Fire's ground rune
blue-violet, Fury of the Sands golden sand with violet energy, the armour shred League's gold cracked shield; light gets
no outline.
Red side: none of them flies, so every picture (on a unit, on him, on the ground) is symmetric left to right.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "nas_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "nasus", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_nasus")
PRE = chr(92) * 2 + "?" + chr(92)
NAME = "nasus_fx_pack"


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


VIOL = "#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580"      # spirit fire (Q, E's flames, W): white core to deep violet
BLUE = "#FFFFFF, #DCE4FF, #9AAEFF, #5A6CF2, #3238C0, #1A1A70"      # Spirit Fire's ground rune, the strike's star
SAND = "#FFF8DC, #F5DC96, #E0B65E, #B5863A, #7D5726, #4A3216"      # Fury of the Sands' sand, the dust
GOLD = "#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A"      # the crescent blade's gleam, the cracked shield
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its "
        "lightest shades and a white core - it must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h} (each cell {cw}x{ch}, 16 px a square)"
VI = f"a violet spirit-fire ramp ({VIOL})"
BL = f"a blue-violet rune ramp ({BLUE})"
SA = f"a golden sand ramp ({SAND})"
GO = f"a gold gleam ramp ({GOLD})"


def row(n, cw, ch):
    shape = "square" if cw == ch else f"{cw}:{ch}"
    return ROW.format(n=n, shape=shape, w=n * cw * 16, h=ch * 16, cw=cw * 16, ch=ch * 16)


LR = "SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)"
CENTER = "; centered in every cell."
HIM = "a jackal-headed warrior 30 squares wide and 44 tall stands in the middle, not drawn"
BIGHIM = "a giant jackal-headed warrior 40 squares wide and 59 tall stands in the middle, not drawn"
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack: the crescent blade chops down on the target
    ("a_hit", "普攻命中：月牙斧刃劈中（目标身上），4 帧", "view_effects `league_nasus_a_hit`（跟随，画在人物上面；左右对称）", "12",
     "法杖的月牙斧刃从上往下劈中：一道金白色的竖劈光，劈中处横着炸开一道短冲击线（十字形），金色火星往两边飞，带一点沙尘"
     "（参考 AA_Weapon_Trail、Flare-Omnimax）。**左右对称**。约 12 格。",
     f"{GO} and {SA}",
     f"a STAFF BLADE IMPACT on a unit, 4 frames, {LR}: 1 a white flash 3 squares; 2 a gold-white vertical slash streak 10 "
     "squares tall with a white core and a short horizontal impact line 8 squares wide across its middle (a cross of "
     "light); 3 the slash fading, 6 gold sparks flying out at mirrored places, small sand-coloured dust bits at the "
     "bottom; 4 fading sparks and dust.",
     row(4, 12, 12) + CENTER),
    # ---- Q Siphoning Strike
    ("q_hit", "Q 汲魂痛击命中（目标身上），5 帧", "view_effects `league_nasus_q_hit`（跟随，画在人物上面；左右对称）", "18",
     "灌满灵魂之力的一击：先是一颗白色的四芒星闪光，然后紫色的灵魂之力炸开，带白芯，一圈紫色的冲击波纹往外扩（参考 Q_Cas_Activate、"
     "Q_Hit_Glow、Q_Waves）。**左右对称**。约 18 格。",
     f"{VI} and {BL}",
     f"a SIPHONING STRIKE HIT on a unit, 5 frames, {LR}: 1 a white four-pointed star flash (thin rays 8 squares long up, "
     "down, left and right); 2 a violet spirit burst 12 squares with a white core, the star's rays 14 squares long tinted "
     "blue-violet; 3 the burst 16 squares, short violet streaks radiating out all round like a shockwave, a darker violet "
     "ring at its edge; 4 the ring 18 squares wide and thinner, violet motes; 5 fading violet motes.",
     row(5, 18, 18) + CENTER),
    ("q_soul", "Q 击杀吸魂：灵魂被吸进他身体（他身上，跟随），6 帧", "view_effects `league_nasus_q_soul`（跟随，画在他上面；左右对称）",
     "40 × 48",
     f"汲魂痛击打死目标、叠层的时候：两团紫色的小灵魂从左右两边飘进来，在他胸口合成一团紫白的光，被吸进身体，再往外荡一圈细光环"
     f"（参考 Q_Staff_Swirl、Q_Hand_Swirl）。**左右对称**，中间身体位置留空（{HIM}）。",
     f"{VI}",
     f"a SOUL ABSORBED by a figure, 6 frames, {LR} ({HIM}): 1 two small violet soul wisps (each a teardrop flame 3 "
     "squares wide and 5 tall with a white core and a thin curling tail) at the left and right edges at chest height (14 "
     "squares under the head's top); 2 the wisps halfway in, curving; 3 the wisps at the figure's sides; 4 the wisps "
     "merged into one violet-white glow 8 squares at the chest middle; 5 the glow smaller (4 squares), a thin violet "
     "ring 24 squares wide and 8 tall pulsing out round the chest; 6 a few violet motes rising.",
     row(6, 40, 48) + "; centered across, the figure's feet on the cell's bottom row."),
    # ---- E Spirit Fire
    ("e_fire", "E 灵魂烈焰：地上的灵魂火圈（地上，不跟随，5 秒），8 帧（1–2 燃起、3–6 循环、7–8 熄灭）",
     "view_effects `league_nasus_e_fire`（不跟随，画在人物下面；左右对称；大图表；3–6 帧循环铺满 5 秒）", "64 × 44",
     "目标脚下燃起一圈**灵魂烈焰**（从斜上方看是扁椭圆，直径 56 格）：第 1 帧一道蓝紫色的光柱从天上落下来；第 2 帧地上亮起蓝紫色的"
     "符文圈（圈里一个三叉轮形的紫色符文），紫火开始冒；第 3–6 帧是循环的燃烧（紫色的灵魂火沿着整个圈往上窜，6–10 格高，白芯，"
     "每帧火苗不一样，第 6 帧接得回第 3 帧）；第 7 帧火变矮、符文变暗；第 8 帧只剩淡淡的圈和几粒余烬（参考 E_Ground_Rune、"
     "E_Clynder_Scroll、E_Fire_Scroll、E_Energy_Beam、E_SpiritFire_ColorMap）。**左右对称**。",
     f"{VI} and {BL}",
     f"SPIRIT FIRE ON THE GROUND seen from above at an angle, 8 frames (1-2 it starts, 3-6 a seamless loop of the burning, "
     f"7-8 it dies), {LR}: 1 a thin blue-violet beam of light 4 squares wide falling from the top of the cell onto the "
     "ground's middle, a white-blue flash ellipse 20 squares wide and 6 tall where it lands; 2 a rune circle on the ground: "
     "an ellipse 56 squares wide and 18 tall, a bright blue-violet ring line with a darker blue rim, a three-spoked violet "
     "rune inside it (like a wheel), the first violet flames 4 squares tall rising along the ring; 3, 4, 5, 6 the burning "
     "loop: the same rune ellipse glowing, violet spirit flames 6 to 10 squares tall licking up along the whole ring and a "
     "few inside, white-violet cores, the flames different in each frame (frame 6 flows back into frame 3); 7 the flames "
     "low (3 squares), the rune dimmer; 8 only the faint blue-violet ring and a few violet embers.",
     row(8, 64, 44) + "; centered across, the ellipse's middle 14 squares above the cell's bottom row."),
    ("e_hit", "E 爆发命中（目标身上），4 帧", "view_effects `league_nasus_e_hit`（跟随，画在人物上面；左右对称）", "16",
     "灵魂烈焰燃起的一瞬间烧到目标：一团紫色的灵魂火炸开往上窜，蓝紫色的火星往外飞（参考 E_Fire_Scroll）。**左右对称**。约 16 格。",
     f"{VI} and {BL}",
     f"a SPIRIT FIRE BURST on a unit, 4 frames, {LR}: 1 a white-violet flash 5 squares; 2 a violet flame burst 12 squares "
     "wide with a white core, its flame tongues pointing up; 3 the flames 16 squares tall, blue-violet sparks flying out "
     "at mirrored places; 4 fading violet embers rising.",
     row(4, 16, 18) + CENTER),
    ("e_shred", "E 减护甲：头顶裂开的盾牌（站在火里的敌人身上，循环），4 帧",
     "view_buffs `league_nasus_e_shred`（跟随，画在人物上面；左右对称；循环）", "10 × 12",
     "站在灵魂烈焰里的敌人护甲被削弱：头顶一面**金色的小盾牌，中间一道裂缝**，裂缝发紫光，一闪一闪（英雄联盟用的就是这个金色裂盾，"
     "参考 Armor_Pen）。**左右对称**（裂缝画成竖直的折线，左右对称）。",
     f"{GO} and {VI}",
     f"a CRACKED SHIELD floating over a unit's head, 4 frames, a seamless loop, {LR}: a small heater shield 7 squares wide "
     "and 8 tall in amber gold with a darker gold rim (a 1-square dark brown edge is allowed: it is a solid thing), a "
     "jagged crack running straight down its middle (a symmetric zigzag 1 square wide) glowing violet-white; 1 the crack "
     "dim violet; 2 brighter; 3 brightest, 2 tiny violet chips beside the shield at mirrored places; 4 like 2.",
     row(4, 10, 12) + CENTER),
    # ---- W Wither (cast by the passive's watch)
    ("w_hit", "W 枯萎命中（目标身上），5 帧", "view_effects `league_nasus_w_hit`（跟随，画在人物上面；左右对称）", "22",
     "枯萎打中：一颗紫色的四芒星闪光，一圈带符文的紫色光环套住目标的腰，往里收紧、沉下去，冒出灰紫色的衰败气息（参考 W_Cas_Flare、"
     "W_Runes、W_Wither_Swirl）。**左右对称**。约 22 格。",
     f"{VI}",
     f"WITHER STRIKING a unit, 5 frames, {LR}: 1 a violet four-pointed star flash 8 squares (thin rays, white centre); 2 a "
     "ring of violet light round the unit's middle (an ellipse 20 squares wide and 7 tall) with 6 small bright rune marks "
     "on it at mirrored places, a white-violet glow at its centre; 3 the ring tightening (16 wide), the runes brighter, "
     "dark violet wisps; 4 the ring 12 wide sinking lower, grey-violet motes; 5 fading motes.",
     row(5, 22, 22) + CENTER),
    ("w_slow", "W 枯萎持续：头顶的枯萎符文（目标身上，5 秒，循环），4 帧",
     "view_buffs `league_nasus_w_slow`（跟随，画在人物上面；左右对称；循环）", "20 × 44",
     f"被枯萎的英雄身上：头顶浮着一个紫色的枯萎符文（倒三角里一只眼睛），一亮一暗；两肩往下飘灰紫色的衰败气息，小小的暗紫色微粒往下落"
     f"（参考 W_Tar_Rune_Anim、W_Wither_Swirl、W_Locus）。**左右对称**，中间身体位置留空（{CHAMP}）。",
     f"{VI}",
     f"a WITHERING CURSE on a champion, 4 frames, a seamless loop, {LR} ({CHAMP}): a violet withering glyph floating over its "
     "head (an eye inside a downward-pointing triangle, 7 squares wide and 6 tall, violet-white lines), pulsing: 1 dim, "
     "2 bright, 3 brightest, 4 bright; grey-violet wisps of age curling down from both shoulders (mirrored), small dark "
     "violet motes falling past the body's edges, each frame a little lower.",
     row(4, 20, 44) + "; centered across, the figure's feet on the cell's bottom row, the glyph's top 1 square under the "
                      "cell's top."),
    # ---- R Fury of the Sands
    ("r_cast", "R 死神降临：变身爆发（他身上，不跟随），7 帧",
     "view_effects `league_nasus_r_cast`（他身上播一次，不跟随；左右对称；大图表）", "80 × 76",
     f"他变成大号的一瞬间：胸口一道紫白闪光，两条紫色能量带从脚下盘旋着往上绕到头顶，地上炸开一圈沙尘，金色沙粒往外飞，头顶闪过一个"
     f"紫色符文；然后沙尘卷到肩高，慢慢落下（参考 R_Transform_Wave_Swirl、R_Transform_Smoke、R_Symbol_Anim、R_Sparks、"
     f"R_Swirl_Energy、Z_Taunt_Bits4x4）。**左右对称**，中间身体位置留空（{BIGHIM}）。",
     f"{VI} and {SA}",
     f"FURY OF THE SANDS: a TRANSFORMATION BURST round a figure, 7 frames, {LR} ({BIGHIM}): 1 a white-violet flash 14 "
     "squares at its chest; 2 two violet energy ribbons spiralling up round the figure from its feet to above its head "
     "(crossing at mirrored places), a ring of sand dust bursting out on the ground (an ellipse 40 squares wide, 10 tall); "
     "3 the ribbons 6 squares above the head, the dust ring 64 wide and 16 tall, golden sand grains flying out at mirrored "
     "places, a violet rune symbol 10 squares wide flashing above the head; 4 the widest: the dust 76 squares wide, sand "
     "swirling up to shoulder height on both sides; 5 the ribbons thinning, sand falling; 6 the dust settling low; 7 a "
     "few violet sparks and sand grains.",
     row(7, 80, 76) + "; centered across, the figure's feet (the dust ring's middle) 6 squares above the cell's bottom row."),
    ("r_hit", "R 沙暴伤害（敌人身上，每半秒一次），4 帧", "view_effects `league_nasus_r_hit`（跟随，画在人物上面；左右对称）", "12",
     "沙暴刮到身边的敌人：一小团金色沙粒打在身上，中间一点紫光，灰黄的沙尘散开（参考 Z_Taunt_Bits4x4、R_Sparks）。**左右对称**。约 12 格。",
     f"{SA} and {VI}",
     f"a SANDSTORM BITE on a unit, 4 frames, {LR}: 1 a small white-violet flash 3 squares; 2 a burst of golden sand grains "
     "10 squares with a violet core; 3 the grains flying out at mirrored places, pale dust puffs; 4 settling dust.",
     row(4, 12, 12) + CENTER),
    ("r_on", "R 沙暴光环（他脚下和身后，跟随，循环），6 帧",
     "view_buffs `league_nasus_r_on`（跟随，画在他下面：z -1；左右对称；循环；大图表）", "76 × 68",
     f"大招期间围着他的**沙暴**：地上一圈打旋的金色沙尘（扁椭圆，直径 64 格，近的一边亮），两边各有一股沙流夹着紫色能量从地面盘旋"
     f"往上卷到他肩膀那么高，沙粒绕着他飞，圈里有淡淡的紫光；每帧沙流往上走一点，第 6 帧接得回第 1 帧（参考 R_Aura_Swirl、"
     f"R_Ground_Rune_Scroll、R_Swirl、Z_Taunt_TrailCourse、Z_Taunt_Bits4x4）。这张**画在他身后**（他挡住的地方画了也看不见），"
     f"**左右对称**，中间身体位置留空（{BIGHIM}）。",
     f"{SA} and {VI}",
     f"a SANDSTORM AURA round a giant figure, 6 frames, a seamless loop, {LR} ({BIGHIM}; the picture is drawn behind him): "
     "a ring of swirling sand on the ground (an ellipse 64 squares wide and 20 tall, golden dust with darker sand streaks, "
     "brighter on its near side), streams of sand mixed with violet energy spiralling up on both sides of the figure from "
     "the ground to its shoulders (mirrored), golden sand grains orbiting, a faint violet glow inside the ring; each frame "
     "the streams a little higher (frame 6 flows back into frame 1).",
     row(6, 76, 68) + "; centered across, the figure's feet (the ring's middle) 10 squares above the cell's bottom row."),
]
BIG_FX = ["e_fire", "r_cast", "r_on"]
REDO = {}
GROUPS = [
    ("a_hit", ["Nasus_Base_AA_Weapon_Trail", "Flare-Omnimax", "EnergyMote", "Base_StarShape01"]),
    ("q_hit q_soul", ["Nasus_Base_Q_Cas_Activate", "Nasus_Base_Q_Hit_Glow", "Nasus_Base_Q_Waves",
                      "Nasus_Base_Q_Staff_Swirl", "Nasus_Base_Q_Hand_Swirl", "Nasus_Base_Q_Weapon_Trail"]),
    ("e_fire e_hit", ["Nasus_Base_E_Ground_Rune", "Nasus_Base_E_Clynder_Scroll", "Nasus_Base_E_Fire_Scroll",
                      "Nasus_Base_E_Energy_Beam", "Nasus_Base_E_SpiritFire_ColorMap", "Nasus_Base_E_Spotlight"]),
    ("e_shred", ["Armor_Pen"]),
    ("w_hit w_slow", ["Nasus_Base_W_Cas_Flare", "Nasus_Base_W_Runes", "Nasus_Base_W_Tar_Rune_Anim",
                      "Nasus_Base_W_Wither_Swirl", "Nasus_Base_W_Locus"]),
    ("r_cast", ["Nasus_Base_R_Transform_Wave_Swirl", "Nasus_Base_R_Transform_Smoke", "Nasus_Base_R_Symbol_Anim",
                "Nasus_Base_R_Sparks", "Nasus_Base_R_Swirl_Energy", "Nasus_Base_R_Transform_Fire_Mult"]),
    ("r_on r_hit", ["Nasus_Base_R_Aura_Swirl", "Nasus_Base_R_Ground_Rune_Scroll", "Nasus_Base_R_Swirl",
                    "Nasus_Base_Z_Taunt_TrailCourse", "Nasus_Base_Z_Taunt_Bits4x4", "Nasus_Base_R_Hand_Swirl"]),
]
FEET = 11                                             # 1x rows from a frame's centre (the pivot) down to the ground
# the action frames the pictures start from: (tag, frame, what) - the cyan cross is his standing point
SHOTS = [("attack", 3, "a_hit：月牙斧刃劈中前方的目标"), ("skill", 4, "q_hit：汲魂痛击砸中前方的目标"),
         ("skill2", 3, "e_fire：杖指远处，目标脚下起火"), ("skill_w", 2, "w_hit：远侧的手伸向英雄"),
         ("ult", 4, "r_cast：从这帧起变成大号"), ("b_idle", 1, "r_on：大号形态，沙暴在他脚下和身后"),
         ("b_skill", 4, "（参考）大号形态的 Q"), ("hit", 1, "（参考）受击")]


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
                sys.exit(f"missing reference {p}")
            im = Image.open(p).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Nasus_Base_", "")[:26], fill=(170, 190, 210, 255))
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
    figs = [first_1x("idle"), first_1x("b_idle")]
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
    d.text((8, 36), f"内瑟斯 {figs[0].shape[1]}×{figs[0].shape[0]} 格，大招形态 {figs[1].shape[1]}×{figs[1].shape[0]} 格，"
                    f"原版斗士 {figs[2].shape[1]}×{figs[2].shape[0]} 格（4 倍，宽度含法杖）", fill=(255, 255, 255, 255), font=font)
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
        pt = (px, int(f.shape[0] / 2 + FEET))           # the frame's centre is his pivot, FEET rows over the ground
        x0, x1 = int(min(xs.min(), pt[0])) - 3, int(max(xs.max(), pt[0])) + 4
        y0, y1 = int(ys.min()) - 3, int(max(ys.max(), pt[1])) + 4
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
    cols = 4
    rows_ = (len(tiles) + cols - 1) // cols
    cw = max(t.width for t in tiles) + 10
    ch = max(t.height for t in tiles) + 10
    sheet = Image.new("RGB", (cols * cw, rows_ * ch), (60, 64, 50))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), ((i % cols) * cw, (i // cols) * ch))
    sheet.save(path)


def design_sheet(path):
    """His two forms at 4x, the design's own squares (PPU 1.2: 1.2 squares a game pixel): A and the big body."""
    import rig_nasus as N
    fa = N.form_a()
    fb = N.form_b(fa)
    tiles = []
    for F in (fa, fb):
        c = F.rig.finish(F.pose())
        ys, xs = np.nonzero(c[..., 3] > 0)
        tiles.append(c[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    H = max(t.shape[0] for t in tiles)
    W = sum(t.shape[1] for t in tiles) + 8
    can = np.zeros((H, W, 4), np.uint8)
    x = 0
    for t in tiles:
        can[H - t.shape[0]:, x:x + t.shape[1]] = t
        x += t.shape[1] + 8
    Image.fromarray(np.repeat(np.repeat(can, 4, 0), 4, 1)).save(path)


def document(shapes):
    (h, w), (bh, bw) = shapes[0][:2], shapes[1][:2]
    L = []
    a = L.append
    a("# 沙漠死神 内瑟斯：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/nasus_idle.png`：3/4 正面朝右的豺狼头战士，金色头冠和大肩甲，"
      f"黑褐色的毛，青绿腰布，两手握着长法杖、月牙斧刃在前面；右边是大招「死神降临」时变大的样子，眼睛和宝石发青白光）。"
      f"他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），{h} 格高、连法杖 {w} 格宽，大招形态 {bh} 格高；"
      f"**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/nasus_size.png`：他两种形态的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。")
    a("> - `design/nasus_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。他的普攻、Q、E 都是法杖打出去的，"
      "**特效都画在目标身上或地上，没有飞行的弹道**。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里内瑟斯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**汲魂痛击、灵魂烈焰、枯萎是紫色的灵魂之火（白芯）**，**灵魂烈焰的地面符文是蓝紫色**，"
      "**死神降临是金黄的沙尘加紫色能量**，**减护甲是英雄联盟的金色裂盾**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。")
    a("> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。")
    a("> - **全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他和目标朝左时也是同一张图。")
    redo = [x[0] for x in FX if x[0] in REDO and len(FX) < 11]
    if redo:
        a("> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：")
        for nm in redo:
            a(f"> - `{nm}`：{REDO[nm]}")
        a(">")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nasus_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "逐格左右对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"打包成 `{NAME}_done.zip`。**请用生图画，不要用代码拼方块**。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「吞噬灵魂」 | 月牙斧刃从上往下劈，附带生命偷取 | `a_hit` |")
    a("| 技能 1 = Q「汲魂痛击」 | 灌满灵魂的一击；用它打死单位会叠层（叠层加 Q 的伤害） | `q_hit` · `q_soul` |")
    a("| 技能 2 = E「灵魂烈焰」 | 目标脚下燃起一圈灵魂火：燃起时爆发一次，之后 5 秒里站在圈里的敌人持续受伤、护甲降低 | `e_fire` · `e_hit` · `e_shred` |")
    a("| 被动自动放的 W「枯萎」 | 让一个敌方英雄衰老：5 秒里减速、减攻速，越来越强 | `w_hit` · `w_slow` |")
    a("| 大招「死神降临」 | 变成大号，身边刮起沙暴，每半秒按最大生命扣身边敌人的血 | `r_cast` · `r_on` · `r_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火、火星、烟、沙尘、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（裂盾例外：实心的东西可以有一圈深色边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("紫色灵魂之火（Q、E 的火、W）", VIOL), ("蓝紫符文（E 的地面符文、Q 的星芒）", BLUE),
                        ("金黄沙尘（死神降临）", SAND), ("金色光泽（斧刃的劈光、裂盾）", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。")
    a("- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：灵魂烈焰半径 28000，"
      "死神降临的沙暴半径 30000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `nasus_fx_{name}.png`：{title}\n")
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
        a(f"| `nasus_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_nasus_fx`（小的）和 `league_nasus_big`（{'、'.join(BIG_FX)}），tag = 名字（build_nasus.py 的 views）。")
    a("- 没有投射物画面（views_p 为空）。`e_fire`、`r_cast` 不跟随（地上 / 他身上的晚播画面，红色方规则）；`e_fire`、`r_on` 画在人物下面（z -1）；"
      "`e_fire` 第 3–6 帧循环铺满 5 秒（e_t 300 tick）。")
    a("- 用 `pixel_1x/` 切格（import_swain_fx / import_urgot_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="nasus_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "nasus_packs"), help="folder for the zip")
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
        sys.exit(f"no League references in {REF}: run work/nas/fx_ref_nas.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "nasus_idle.png"))
    shapes = size_sheet(os.path.join(out, "design", "nasus_size.png"))
    shots_sheet(os.path.join(out, "design", "nasus_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shapes)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"nasus_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
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
