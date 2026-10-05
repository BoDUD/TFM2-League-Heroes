#!/usr/bin/env python3
"""Build tryndamere_fx_pack.zip: step 3 of Tryndamere's sprite - Codex draws his effects (after league_varus's pack).

    python tools/art/pack_tryndamere_fx.py [--no-zip] [--out DIR] [--only a_hit,e_spin --name tryndamere_fx_redo_pack]

The pack (%TEMP%/tr_work/fx/tryndamere_fx_pack, zipped next to it or into --out) holds PROMPTS.md (also written to
assets/source/tryndamere/PROMPTS_FX.md), design/tryndamere_design.png (8x), design/tryndamere_size.png (the design at 4x
on the arena colour with the feet line, a 10-px ruler and the base fighter beside him), design/tryndamere_shots.png (the
finished action frames at 4x - tools/art/rig_tryndamere.py - with the point each caster picture starts from) and
refs/lol_fx_ref.png (League's own particle textures for Tryndamere, grouped by the effect of ours they inform; Riot's
art, local only: run the reference extraction first, it reads Tryndamere.wad.client into %TEMP%/tr_work/fxref).
The effects are the views the kit binds (tools/kit/build_tryndamere.py: view_effects a_hit, e_spin, e_hit, w_shout,
w_hit, r_cast, q_heal; view_buffs f_5, r_rage, w_weak, w_slow). League's colours: the blood red and ember orange of his
fury with white-hot cores (the slash arcs, the roar, the rage flames), the darker crimson of the debuffs. Blades of
light, flames and glow get no outline; the bright-effects lesson (Nocturne) holds.
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
TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "tr_work")
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "tryndamere", "PROMPTS_FX.md")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "tryndamere_native.png")
PRE = chr(92) * 2 + "?" + chr(92)


def lp(p):
    p = os.path.abspath(p)
    return p if os.name != "nt" or p.startswith(PRE) else PRE + p


RED = "#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A"      # the fury: slash arcs, hits, the roar
EMBER = "#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10"    # the rage flames, white-hot cores
DARK = "#C02040, #8A1030, #5A0A24, #3A0618, #1E040C"              # the debuffs, smoke, ash
LEAD = ("Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, "
        "NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get "
        "a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it "
        "must read on a dark battlefield), colours only from {ramps}.")
TAIL = "Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels."
ROW = "one horizontal row of {n} equal {shape} cells, image size {w}x{h}"
FIG = "do NOT draw the figure; leave its place empty"
RC = f"a blood-red ramp ({RED})"
EC = f"an ember ramp ({EMBER})"
DC = f"a dark crimson ramp ({DARK})"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- the attack
    ("a_hit", "普攻打中（目标身上），4 帧", "view_effects `league_tryndamere_a_hit`（跟随，画在人物上面）", "16",
     "大剑砍中：一道从右上往左下的红白色斩击弧光，砍中的地方一下白色闪光，几点红色火星飞出去（参考 E_SlashUlt、common_SlashWave、"
     "E_Sparks）。约 16 格，居中画。",
     f"{RC} and {EC}",
     "a GREATSWORD HIT, 4 frames: 1 a crescent slash arc of white-red light 14 squares long cutting from the upper right "
     "to the lower left through the center; 2 a white flash at the center 8 squares across, the arc thinning, 5 red-"
     "orange sparks flying out; 3 the arc gone, sparks further out; 4 a few fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    # ---- passive: Battle Fury at full
    ("f_full", "被动 怒气满了：脚下和身上的红光（循环），4 帧",
     "view_buffs `league_tryndamere_f_5`（满 5 层怒气时，循环，画在人物下面）", "26 × 40",
     "怒气叠满（暴击率最高）时：蛮王身后和脚下烧着一层红色的怒气光，几缕红光往上飘（参考 Q_bigglow02、common_color-aura-red、"
     "Aura_Self）。画在人物下面，所以只有从人身边露出来的部分看得见：脚下一圈扁的红光，身体两边往上飘的红色光丝，到头顶为止。"
     "中间是人，不要画人。左右对称，4 帧无缝循环。约 26 格宽、40 格高，脚在格子底部往上 4 格的中间。",
     f"{RC} and {EC}",
     f"a FURY AURA round a standing figure ({FIG}; symmetric left and right), 4 frames, a seamless loop: a flattened "
     "ellipse of red light on the ground round the feet (twice as wide as tall, 22 squares wide), 6 thin red-orange light "
     "wisps rising along both sides of the figure's place up to head height (36 squares), small ember sparks; the wisps "
     "climb a few squares each frame and flicker.",
     ROW.format(n=4, shape="13:20", w=832, h=320) + " (each cell 208x320); the figure's feet 4 squares (32 px) above the "
     "bottom, horizontally centered, in every cell."),
    # ---- E: Spinning Slash
    ("e_spin", "E 旋风斩：绕着身体转的刀光（施法者身上，跟着冲过去），6 帧",
     "view_effects `league_tryndamere_e_spin`（BIG，施法者身上，跟随；格子中心放到他的腰）", "40 × 30",
     "E「旋风斩」：蛮王一边旋转一边往前冲，大剑在身边转出一圈红白色的刀光（从斜上方看是扁的椭圆，宽是高的 2 倍左右），刀光带一点火焰的"
     "橙色尾巴（参考 E_SlashUlt、E_FlameHead、E_Outerring、E_Erode_01、E_Mis_Tail_V2）。中间是人，不要画人：刀光绕着人的位置转，"
     "前面一段从人身前经过，后面一段在人身后。6 帧转一圈多：1 刀光出现，2–5 转（亮的刀头每帧往前转 90°，后面拖着变暗的弧），6 散开。"
     "约 40 格宽、30 格高，腰在格子正中。",
     f"{RC} and {EC}",
     f"a SPINNING SWORD SLASH round a figure ({FIG}), seen from above at an angle, 6 frames: 1 a short bright white-red "
     "blade arc appears at the right of the figure's place; 2-5 the arc sweeps round the figure's place along a "
     "flattened ellipse 38 squares wide and 18 tall (its bright head moving a quarter turn each frame, a fading red and "
     "orange trail behind it covering half the ellipse; small flame licks on the trail); 6 the trail breaks into red "
     "sparks.",
     ROW.format(n=6, shape="4:3", w=1920, h=480) + " (each cell 320x240 - keep the 4:3 shape); the figure's waist "
     "(the ellipse's center) at the center of every cell."),
    ("e_hit", "E 砍中（目标身上），4 帧", "view_effects `league_tryndamere_e_hit`（跟随，画在人物上面）", "16",
     "旋风斩从身边扫过：一道横着的红白色刀光划过，一下闪光和红色火星（参考 E_SlashUlt、E_Sparks、common_SlashWave）。约 16 格，居中画。",
     f"{RC} and {EC}",
     "a SWEEPING SLASH HIT, 4 frames: 1 a horizontal white-red slash streak 16 squares long through the center; 2 a white "
     "flash at the center 8 squares across, the streak thinning, 4 orange sparks; 3 sparks flying out; 4 fading sparks.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; centered in every cell."),
    # ---- W: Mocking Shout
    ("w_shout", "W 蔑视怒吼：从他嘴里吼出去的冲击波（施法者身上），6 帧",
     "view_effects `league_tryndamere_w_shout`（BIG，施法者身上，跟随；格子里的脚放到他脚下）", "84 × 48",
     "W「蔑视」：蛮王仰头怒吼，嘴前喷出一下红色的吼声，地面上一圈红色的冲击波往外推到很远（从斜上方看的扁椭圆，宽是高的 2 倍，"
     "半径约 40 格，所以外圈约 80 格宽），几道红色的声波弧从头的位置往两边散开（参考 W_Dissolve_Cloudy_01、Orianna distort-wave、"
     "R_speed_blur、common_SRU_Tower_Explosion_Glow）。中间是人，不要画人。6 帧：1 嘴前红光，2–4 冲击波从脚下往外扩、声波弧往外，"
     "5 冲击波到边变细，6 散去。约 84 格宽、48 格高，脚在格子底部往上 14 格的中间，嘴在脚上方 28 格、往右 15 格。",
     f"{RC} and {DC}",
     f"a BATTLE ROAR from a figure ({FIG}), seen from above at an angle, 6 frames: 1 a burst of red light at the mouth's "
     "point (28 squares above the feet, 15 squares right of them); 2 three curved red sound-wave arcs spreading left and "
     "right from the head, a red shockwave ring starting on the ground round the feet; 3-4 the ring expanding over a "
     "flattened ellipse twice as wide as tall up to 80 squares wide, dark crimson dust kicked up along it, the arcs "
     "further out; 5 the ring thin at its edge; 6 fading dust.",
     ROW.format(n=6, shape="7:4", w=3360, h=480) + " (each cell 560x320 - keep the 7:4 shape; 48 squares tall); the figure's feet 14 "
     "squares (about 93 px) above the bottom, horizontally centered, in every cell."),
    ("w_hit", "W 吼中（敌人身上），4 帧", "view_effects `league_tryndamere_w_hit`（跟随，画在人物上面）", "16 × 20",
     "被吼中的敌人：头那里一下暗红色的冲击，几道红色的声波弧打在他身上（参考 W_Dissolve_Cloudy_01、R_speed_blur）。中间是人，不要画人。"
     "约 16 格宽、20 格高，居中画（中心在人的胸口）。",
     f"{RC} and {DC}",
     f"a ROAR STRIKING a figure ({FIG}), 4 frames: 1 three curved red sound-wave arcs coming in from the left; 2 the arcs "
     "hit the center with a dark crimson burst 12 squares across; 3 red dust puffs, the burst fading; 4 fading wisps.",
     ROW.format(n=4, shape="4:5", w=1024, h=320) + " (each cell 256x320); centered in every cell."),
    ("w_weak", "W 攻击力降低：头上的标记（敌人身上，循环 4 秒），4 帧",
     "view_buffs `league_tryndamere_w_weak`（循环，画在人物上面，头顶）", "12 × 12",
     "被吼了的敌人攻击力降低：头顶一个暗红色的「断剑」标记（一把小剑断成两截，有描边），下面一个往下的红色箭头，暗红光一明一暗"
     "（参考 common_color-aura-red）。4 帧无缝循环。约 12 格见方，标记的底边在格子底部（导入时放到头顶）。",
     f"{DC} and {RC}",
     "an ATTACK-DOWN MARK over a head, 4 frames, a seamless loop: a small broken sword icon 8 squares tall (a blade "
     "snapped in two, the halves a square apart, a 1-square dark outline, dark crimson with a red glint) above a small "
     "red arrow pointing DOWN; a dim crimson glow round it pulsing brighter and dimmer; the icon bobs a square.",
     ROW.format(n=4, shape="square", w=1024, h=256) + "; the icon centered, its bottom near the bottom of every cell."),
    ("w_slow", "W 减速：脚下的标记（敌人身上，循环 2 秒），4 帧", "view_buffs `league_tryndamere_w_slow`（循环，画在脚下）",
     "18 × 8",
     "背对着他跑的敌人被减速：脚下一圈暗红色的光，几道往下的红色光痕（像被吓得腿软）（参考 common_color-aura-red、Aura_Self）。"
     "中间是人，不要画人。左右对称，4 帧无缝循环。约 18 格宽、8 格高，贴着地面。",
     f"{DC} and {RC}",
     f"a SLOW MARK at a figure's feet ({FIG}; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse "
     "of dark crimson light on the ground round the feet (twice as wide as tall, 16 squares wide), 4 short red streaks "
     "sliding DOWN into it a square each frame, 2 small dust puffs.",
     ROW.format(n=4, shape="9:4", w=2304, h=256) + " (each cell 576x256); the ellipse at the bottom middle of every cell."),
    # ---- Q: Bloodlust
    ("q_heal", "Q 嗜血：吸血回血的红光（施法者身上），5 帧",
     "view_effects `league_tryndamere_q_heal`（施法者身上，不跟随；格子中心放到他的胸口）", "30 × 44",
     "Q「嗜血」（R 结束时和危险时喝）：四周的红色光点和血色光丝往他身上吸过去，胸口一下红白色的光爆开，几点红色的「+」形火花往上升"
     "（参考 Temp_Q_Heal_01_Spark_RGBA、Q_bigglow02、Q_WeaponTrail、Flicker_04）。中间是人，不要画人。5 帧：1–2 光点往里吸，"
     "3 胸口爆光，4 火花上升，5 淡去。约 30 格宽、44 格高，胸口在格子正中。",
     f"{RC} and {EC}",
     f"a BLOOD HEAL on a figure ({FIG}), 5 frames: 1 ten red light motes and thin blood-red streaks 14 squares out "
     "from the center, drawn inward; 2 the motes closer, a red glow at the center; 3 a red-white flash at the center 14 "
     "squares across; 4 six small red plus-shaped sparks rising from it 8-16 squares above the center; 5 the sparks fading "
     "near the top of the cell.",
     ROW.format(n=5, shape="15:22", w=1200, h=352) + " (each cell 240x352); the figure's chest at the center of every "
     "cell."),
    # ---- R: Undying Rage
    ("r_cast", "R 不死怒火爆发（施法者身上），6 帧",
     "view_effects `league_tryndamere_r_cast`（BIG，施法者身上，不跟随；格子里的脚放到他脚下）", "48 × 56",
     "R「不灭狂暴」触发：蛮王身上猛地炸开一团橙红色的怒火，地上一圈耀斑一样的火环往外冲，火焰从脚下往上窜过头顶，几片灰烬飞起来"
     "（参考 R_Flare、R_dome_flames、R_FireStrands_4x1_Darker、R_FlameErosion、R_Ash01、common_flames03）。中间是人，不要画人。"
     "6 帧：1 身上白橙色的闪光，2 火环往外冲、火焰往上窜，3 火焰最高（过头顶），4–5 火焰往下落、灰烬飘，6 剩几点火星。约 48 格宽、56 格高。",
     f"{EC}, {RC} and {DC}",
     f"an UNDYING RAGE ERUPTION round a figure ({FIG}), 6 frames: 1 a white-orange flash at the figure's chest (16 "
     "squares above the feet); 2 a jagged flare ring of orange fire bursting outward along the ground (a flattened ellipse "
     "twice as wide as tall), tongues of red and orange flame shooting up round the figure's place; 3 the flames at their "
     "tallest, 50 squares above the feet, the ring 44 squares wide; 4 the flames sinking, dark ash flakes (outlined) "
     "drifting up; 5 low flames and ash; 6 a few embers.",
     ROW.format(n=6, shape="6:7", w=2304, h=448) + " (each cell 384x448); the figure's feet 4 squares (32 px) above the "
     "bottom, horizontally centered, in every cell."),
    ("r_rage", "R 不死期间：身上烧着的怒火（循环 5 秒），4 帧",
     "view_buffs `league_tryndamere_r_rage`（BIG，循环，画在人物下面）", "34 × 50",
     "不死的 5 秒里：蛮王全身被橙红色的火焰包着往上烧，脚下一圈火（参考 R_dome_flames、R_FireStrands_4x1_Darker、R_buf_01_GroundFlame、"
     "R_Small_Mote、common_flames03）。画在人物下面，所以火从人身边和头顶露出来：两边和头顶往上蹿的火舌，脚下一圈扁的火环。"
     "中间是人，不要画人。左右对称，4 帧无缝循环（火舌每帧往上跳几格、换形状）。约 34 格宽、50 格高，脚在格子底部往上 4 格的中间。",
     f"{EC} and {RC}",
     f"RAGE FLAMES burning round a standing figure ({FIG}; symmetric left and right), 4 frames, a seamless loop: a "
     "flattened ring of orange fire on the ground round the feet (twice as wide as tall, 30 squares wide), tall tongues of "
     "red and orange flame with white-yellow cores rising along both sides of the figure's place and above its head (up "
     "to 46 squares above the feet), embers; the flames leap and change shape each frame.",
     ROW.format(n=4, shape="17:25", w=1088, h=400) + " (each cell 272x400); the figure's feet 4 squares (32 px) above "
     "the bottom, horizontally centered, in every cell."),
]

GROUPS = [
    ("slash", ["Tryndamere_Base_E_SlashUlt", "common_SlashWave", "Tryndamere_Base_E_FlameHead",
               "Tryndamere_Base_E_Outerring", "Tryndamere_Base_E_Erode_01", "Tryndamere_E_Mis_Tail_V2"]),
    ("sparks", ["Tryndamere_Base_E_Sparks", "common_BW_Sparks", "Tryndamere_Base_Flicker_04", "common_Glows",
                "Helix", "glow-soft"]),
    ("roar", ["Tryndamere_Base_W_Dissolve_Cloudy_01", "Orianna_Base_E_distort-wave", "Tryndamere_Base_R_speed_blur",
              "common_SRU_Tower_Explosion_Glow", "common_SmokePuffs", "common_color-aura-red"]),
    ("blood", ["Tryndamere_Base_Temp_Q_Heal_01_Spark_RGBA", "Tryndamere_Base_Q_bigglow02",
               "Tryndamere_Base_Q_WeaponTrail", "Aura_Self", "common_color-incinerate", "Flame_trail_gradient"]),
    ("rage", ["Tryndamere_Base_R_Flare", "Tryndamere_Base_R_dome_flames", "Tryndamere_Base_R_FireStrands_4x1_Darker",
              "Tryndamere_Base_R_FlameErosion", "Tryndamere_Base_R_Ash01", "common_flames03"]),
]
# where the caster pictures go: (tag, frame, what, mark) - "feet" = the standing point, "mouth", "waist", "chest"
MOUTH, WAIST, CHEST = (79, 72), (71, 86), (70, 80)
SHOTS = [("skill", 3, "e_spin: 腰（刀光的中心）", "waist"), ("skill2", 4, "w_shout: 脚下（冲击波）/ 嘴", "feet"),
         ("skill2", 4, "w_shout: 嘴", "mouth"), ("skill_q", 3, "q_heal: 胸口", "chest"),
         ("ult", 2, "r_cast / r_rage: 脚下", "feet"), ("idle", 1, "f_full: 脚下", "feet")]


def ref_sheet(path):
    S, LW = 180, 90
    sheet = Image.new("RGBA", (LW + 6 * S, len(GROUPS) * (S + 16)), (16, 22, 34, 255))
    d = ImageDraw.Draw(sheet)
    on_disk = {os.path.splitext(f)[0] for f in os.listdir(REF)}
    for r, (label, names) in enumerate(GROUPS):
        y = r * (S + 16)
        d.text((6, y + S // 2), label, fill=(230, 240, 250, 255))
        for c, nm in enumerate(names):
            nm = next((x for x in sorted(on_disk) if x.lower() == nm.lower()), nm)
            im = Image.open(os.path.join(REF, nm + ".png")).convert("RGBA")
            im.thumbnail((S - 12, S - 22))
            sheet.alpha_composite(im, (LW + c * S + (S - im.width) // 2, y + 16 + (S - 16 - im.height) // 2))
            d.text((LW + c * S + 4, y + 2), nm.replace("Tryndamere_Base_", "")[:26], fill=(170, 190, 210, 255))
    sheet.save(path)


def design_1x():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """The design at 4x on the arena colour, the feet line, a 10-px ruler and the base fighter beside him."""
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
    d.text((8, 36), f"蛮王 {fig.shape[1]}×{fig.shape[0]} 格（含大剑），原版斗士 {kn.shape[1]}×{kn.shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return fig.shape


def shots_sheet(path):
    """The finished action frames at 4x (rig_tryndamere), the point each caster picture starts from as a cyan cross."""
    import rig_tryndamere as R
    P = R.Parts()
    Z = 4
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
    tiles = []
    for tag, k, what, mark in SHOTS:
        f = P.D.a if tag == "idle" else R.frames(P, tag)[k - 1]
        mx, my = {"feet": (R.PIVOT[0], P.D.soles), "mouth": MOUTH, "waist": WAIST, "chest": CHEST}[mark]
        ys, xs = np.nonzero(f[..., 3] > 0)
        x0, x1 = min(xs.min(), mx) - 3, max(xs.max(), mx) + 4
        y0, y1 = min(ys.min(), my) - 3, max(ys.max(), my) + 4
        sub = f[y0:y1, x0:x1]
        im = Image.new("RGBA", (max(sub.shape[1] * Z, 220), sub.shape[0] * Z + 24), (104, 112, 72, 255))
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sub)).resize((sub.shape[1] * Z, sub.shape[0] * Z),
                                                                             Image.NEAREST), (0, 24))
        d = ImageDraw.Draw(im)
        cx, cy = (mx - x0) * Z + Z // 2, (my - y0) * Z + Z // 2 + 24
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
    a("# 蛮族之王 泰达米尔：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型和动作已定（`design/tryndamere_design.png`，8 倍，{h} 行）。")
    a(f"> - 大小对照 `design/tryndamere_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。蛮王 {w}×{h} 格（含拖在身后的大剑，人约 40 格宽）。每条写的大小都是游戏像素（格）。")
    a("> - `design/tryndamere_shots.png`：E、W、Q、R 和待机的定稿动作（4 倍），青色十字是特效的起点（脚下、腰、胸口或嘴），导入时 Claude 把特效放到这里。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里蛮王自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**刀光、怒吼、嗜血是血红色带白芯；大招的不死怒火是橙红色的火焰（白黄色的芯）和黑色的灰烬；减益标记是暗红色**。")
    a("> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。")
    a("> - **绕着人的刀光、围着人的火和光只画边，中间留空**，不然会把人整个挡住。")
    a(f"> - 特效照下面第 1–{len(FX)} 条和「所有特效图的规则」画，每张一个 PNG，文件名 `tryndamere_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。")
    a("> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。")
    a("> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`tryndamere_fx_done.zip`）放在 outputs 里。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻 + 被动「战斗狂怒」 | 大剑砍，会暴击；普攻、E 和击杀叠怒气（5 层，每层加暴击率），叠满时身上烧着红光 | `tryndamere_fx_a_hit` · `tryndamere_fx_f_full` |")
    a("| 技能 1 = E「旋风斩」 | 旋转着冲向目标并穿过去，砍到路上所有敌人，每砍一个叠一层怒气 | `tryndamere_fx_e_spin` · `tryndamere_fx_e_hit` |")
    a("| 技能 2 = W「蔑视」 | 怒吼，附近敌方英雄攻击力降低 4 秒，背对他（远一点）的还被减速 2 秒 | `tryndamere_fx_w_shout` · `tryndamere_fx_w_hit` · `tryndamere_fx_w_weak` · `tryndamere_fx_w_slow` |")
    a("| 大招 = R「不灭狂暴」 + Q「嗜血」 | 危险时触发：5 秒内血量不会低于 1，怒气直接叠满；结束时喝 Q 按怒气回血 | `tryndamere_fx_r_cast` · `tryndamere_fx_r_rage` · `tryndamere_fx_q_heal` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、光、火焰、烟、火花没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的东西（灰烬片、断剑标记）有 1 格深色描边（`#12040A`）。")
    a("- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("血红（刀光、命中、怒吼、嗜血、怒气）", RED), ("余烬橙（大招的火焰、白热的芯）", EMBER),
                        ("暗红（减益标记、烟尘、灰烬）", DARK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。")
    a("- 画在他身上或脚下的画面（`e_spin`、`w_shout`、`q_heal`、`r_cast`、`r_rage`、`f_full`）按每条写的站位画，**格子里留出空的人形位置，不要画人**。挂在人身上或脚下的循环画面（`f_full`、`r_rage`、`w_weak`、`w_slow`）左右对称或不分左右，因为人朝左朝右都用同一张。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：E 的刀光半径 15000、W 的怒吼半径 40000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `tryndamere_fx_{name}.png`：{title}\n")
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
        a(f"| `tryndamere_fx_{name}` | {bind} | {size} |")
    a("")
    a("- `f_full` 导成 view_buffs `f_5`（只有满怒气的那一层有画面）；`r_rage`、`f_full` 的 z 是 -1（人物下面），`w_weak` 画在头顶。")
    a("- 施法者身上的画面按 `design/tryndamere_shots.png` 的十字把起点挪过去；晚于第一 tick 播放的（`r_cast`、`q_heal`）`is_follow` 为 false（红方方向）。`e_spin` 跟着他冲过去（跟随）。")
    a("- 清掉 Codex 给光和火描的最深色边（`import_riven.py` 的 `unrim`，灰烬和断剑保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。")
    return "\n".join(L) + "\n"


def main():
    global FX
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="tryndamere_fx_pack", help="the pack's name (folder and zip)")
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
        sys.exit(f"no League references in {REF}: extract Tryndamere's particle textures first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(os.path.join(out, "design", "tryndamere_design.png"))
    shape = size_sheet(os.path.join(out, "design", "tryndamere_size.png"))
    shots_sheet(os.path.join(out, "design", "tryndamere_shots.png"))
    ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"tryndamere_fx_{x[0]}.png", "binding": x[2], "size": x[3]} for x in FX], f,
                  ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC)
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
