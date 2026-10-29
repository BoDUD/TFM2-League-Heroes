#!/usr/bin/env python3
"""Build renni_fx_pack.zip: step 3 of Renni's sprite - Codex draws her effects and her three skill icons
(pack_scar_fx.py's way).

    python tools/lol/fx_ref_renni.py           # her TFT particle textures -> C:/t/rn_work/fxref
    python tools/art/pack_renni_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name renni_fx_redo_pack]

The pack (C:/t/rn_work/fx/renni_fx_pack, zipped into --out, default dist/renni_packs) holds PROMPTS.md (also written to
assets/source/renni/PROMPTS_FX.md), design/renni_design.png (the approved idle at 4x on its own squares),
design/renni_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (her own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_renni.py, the user's picks 2026-10-29: top,
plan A 「泥奔者」): view_effects a_hit, q_hit, p, e, r_hit, r_slam; view_buffs q_slow, p_rush, e_guard, r_up. Plus the
three skill icons. The charge, the guard and the lift are in her own frames.
Her colours: the saw's hot SPARKS (orange-yellow, white cores), its BRASS and STEEL, the chem-barons' NEON-GREEN
chemtech (her tubes and vials), SHIMMER's violet-pink glow, Zaun's MUD (the Mudrunner).
Red side: every picture is symmetric left to right (the client never mirrors an effect picture); she has no
projectile.
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
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/rn_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "renni", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "renni", "hd")
NAME = "renni_fx_pack"
PPU = 2.0

SPARK = "#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C"             # the saw's hot sparks
BRASS = "#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A"             # the saw's guide bars
STEEL = "#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36"             # the saw's teeth and the engine's metal
CHEM = "#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10"              # chemtech green: her tubes, her vials, the rotor
SHIMMER = "#FFE6FF, #F4A8FF, #C858F0, #7C24B8, #3C0E66"           # Shimmer's violet-pink glow
MUD = "#D8D0A8, #A89868, #74684A, #4A422E, #262014"               # Zaun's mud and grit
SP = f"a hot spark ramp ({SPARK})"
BR = f"a brass ramp ({BRASS})"
SL = f"a steel ramp ({STEEL})"
CG = f"a chemtech green ramp ({CHEM})"
SH = f"a Shimmer violet-pink ramp ({SHIMMER})"
MD = f"a mud brown ramp ({MUD})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, "
         "NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; "
         "no magic runes, no smooth neon beams, no lightning, no blood")
HER = "the sturdy woman stands in the middle, not drawn: 34 squares wide and 38 tall"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little "
        "riveted brass corners, a deep murky green-black inside, the symbol big and centred, lit from the upper left; "
        "pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px")
SAW = ("her CHAINSAW (a round magenta engine with a glowing neon-green rotor disc, a grey-blue handle, two parallel "
       "brass guide bars with a dark slot and grey round holes)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：链锯咬一下，4 帧", "view_effects `tft_renni_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "链锯咬在人身上（一次普攻锯三下，每下播一次）：一个白热的**小闪光**，一把**橙黄色的火花**往两边喷开，几颗钢屑。**左右对称**，4 帧。",
     SP + ", " + SL,
     "A CHAINSAW BITE, 4 frames, " + LR + ": 1 a white-hot flash 6 squares across; 2 a fan of short orange-yellow "
     "SPARK streaks (1 square thick, 3-5 long) spraying out to both sides (mirrored), a few grey steel chips; 3 the "
     "sparks farther and fewer; 4 the last sparks fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_hit", "链锯冲撞：前方锯切（减速），5 帧", "view_effects `tft_renni_q_hit`（跟随目标，z 2；左右对称）", "24 × 24",
     "冲撞后链锯在前方扇形里连锯三下，每下打中一个人播一次：比普攻大，白热闪光外面一圈**火花喷泉**，夹着几滴**荧光绿的化学液**，"
     "钢屑往两边飞。**左右对称**，5 帧。",
     SP + ", " + CG + ", " + SL,
     "A HEAVY GRIND, 5 frames, " + LR + ": 1 a white-hot flash 10 squares across; 2 a fountain of orange-yellow "
     "SPARKS spraying up and out to both sides (mirrored) 20 squares wide, a few neon-green chemical drops (1-2 "
     "squares) among them; 3 the sparks wider and falling, steel chips flying; 4 the sparks thinning, the green drops "
     "falling; 5 the last glints. " + MAGIC + ".",
     row(5, 24, 24) + CENTER),
    ("q_slow", "链锯冲撞：被减速，6 帧循环", "view_buffs `tft_renni_q_slow`（跟随被减速的人，脚下，z 3；左右对称）", "24 × 10",
     "被锯中后减速：脚下一摊**泥浆**，泥里冒着几个**荧光绿的化学泡泡**，泡泡鼓起来又破掉。**左右对称**，6 帧循环。",
     MD + ", " + CG,
     "A SLOWING MUD PUDDLE, 6 looping frames, " + LR + ": " + GROUND_E + " a puddle of dark Zaun MUD 20 squares wide "
     "and 6 tall with a lighter rim, two or three neon-green chemical BUBBLES (2-3 squares) swelling in it and popping "
     "into a tiny green splash, in turn; frames 1-6 the bubbles rising and bursting. " + MAGIC + ".",
     row(6, 24, 10) + CENTER),
    ("p", "微光狂热：给自己打一针微光，6 帧", "view_effects `tft_renni_p`（跟随她，z 3；左右对称）", "36 × 44",
     "血量低于 40% 时给自己注射微光：胸口「嘭」地炸开一团**紫粉色的微光**，往两边冲出一圈光环，一串紫粉色的光点往上窜到头顶，"
     "最后几缕紫色的烟。身体位置留空（光从胸口位置的两侧和外圈冒出来）。**左右对称**，6 帧。",
     SH + ", " + CG,
     "A SHIMMER SHOT, 6 frames, " + LR + ", " + HER + ": 1 a violet-pink flash at her chest height, two bright spots "
     "4 squares across at both sides of the body; 2 a violet-pink shock ring 30 squares wide and 10 tall around her "
     "waist, a few neon-green drops flicked out (mirrored); 3 the ring wider and fading, two columns of violet-pink "
     "motes (1-2 squares) rushing up both sides of her; 4 the motes over her head, a pink glint at the top; 5 thin "
     "violet smoke curls rising; 6 the last motes. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 36, 44) + CENTER),
    ("p_rush", "微光狂热：药劲上头（加攻速），6 帧循环", "view_buffs `tft_renni_p_rush`（跟随她，z 3；左右对称）", "36 × 44",
     "打完微光那几秒：身体两侧一闪一闪的**紫粉色光焰**（只画外圈几格亮边），几点紫粉色的光点往上飘，脚下一圈淡淡的紫光。"
     "身体位置留空。**左右对称**，6 帧循环。",
     SH,
     "A SHIMMER RUSH, 6 looping frames, " + LR + ", " + HER + ": at both sides of her (mirrored) tall flickering "
     "violet-pink FLAME tongues 3 squares wide and 20 tall hugging her outline (only a bright edge and a few lit "
     "squares), a faint violet ring " + GROUND_E + " 28 squares wide and 7 tall at the bottom, a few pink motes "
     "drifting up; frames 1-6 the flames flickering and the motes rising. The middle (the body) left empty. "
     + MAGIC + ".",
     row(6, 36, 44) + CENTER),
    ("e", "锯刃格挡：竖锯挡住，5 帧", "view_effects `tft_renni_e`（跟随她，z 3；左右对称）", "40 × 44",
     "她把链锯竖起来挡在身前的一瞬间：身体两侧各「锵」地亮起一道**钢蓝色和黄铜色的护盾弧**，弧上几颗铆钉一闪，"
     "几颗火花往外崩。身体位置留空。**左右对称**，5 帧。",
     SL + ", " + BR + ", " + SP,
     "A SAW GUARD RAISED, 5 frames, " + LR + ", " + HER + ": 1 two bright glints at both sides of her chest; 2 at both "
     "sides of her (mirrored) a tall curved steel-blue SHIELD ARC 4 squares wide and 32 tall with a brass rim and "
     "three rivet glints, a white flash where it rings; 3 a few orange sparks knocked off the arcs; 4 the arcs dimmer; "
     "5 only the rims glinting. The middle (the body) left empty. " + MAGIC + ".",
     row(5, 40, 44) + CENTER),
    ("e_guard", "锯刃格挡：护盾和减伤，6 帧循环", "view_buffs `tft_renni_e_guard`（跟随她，z 3；左右对称）", "40 × 44",
     "格挡的那几秒：身体两侧淡淡的**钢蓝色护盾弧**（只画轮廓的亮边），一道亮光沿着弧往上跑，黄铜铆钉一闪一闪。身体位置留空。"
     "**左右对称**，6 帧循环。",
     SL + ", " + BR,
     "A GUARD, 6 looping frames, " + LR + ", " + HER + ": at both sides of her (mirrored) a tall curved steel-blue "
     "shield ARC 3 squares wide and 32 tall (only a bright rim and a few lit squares, the inside empty), three brass "
     "rivet glints on each arc; frames 1-6 a white glint running up the arcs, the rivets blinking in turn. The middle "
     "(the body) left empty. " + MAGIC + ".",
     row(6, 40, 44) + CENTER),
    ("r_up", "泥奔者重击：被举在半空（晕眩），6 帧循环", "view_buffs `tft_renni_r_up`（跟随被举起的人，头顶，z 3；左右对称）", "20 × 10",
     "被链锯挑起来、挂在半空晕着的人头顶：几颗**黄铜色和荧光绿的小星星**转圈，中间几颗火花。**左右对称**，6 帧循环。",
     BR + ", " + CG + ", " + SP,
     "A STUN OVER THE HEAD, 6 looping frames, " + LR + ": in the cell (it rides over the unit's head) three small "
     "stars (3 squares) in brass and neon green circling on a flat ring 16 squares wide and 4 tall, two tiny orange "
     "sparks in the middle; frames 1-6 the stars going round. " + MAGIC + ".",
     row(6, 20, 10) + CENTER),
    ("r_hit", "泥奔者重击：挑起 / 砸中，5 帧", "view_effects `tft_renni_r_hit`（跟随目标，z 2；左右对称）", "22 × 24",
     "把人挑起来的那一下、和砸地时被砸到的人：一个大的白热闪光，**火花和泥点**往两边四溅，一圈冲击环。**左右对称**，5 帧。",
     SP + ", " + MD + ", " + SL,
     "A CRUSHING HIT, 5 frames, " + LR + ": 1 a big white-hot flash 12 squares across; 2 an orange shock ring 20 "
     "squares wide and 8 tall, orange-yellow sparks and brown MUD clots (2-3 squares) flying out to both sides "
     "(mirrored); 3 the ring wider and thinner, the mud falling; 4 a puff of dust; 5 the last specks. " + MAGIC + ".",
     row(5, 22, 24) + CENTER),
    ("r_slam", "泥奔者重击：砸地，8 帧", "view_effects `tft_renni_r_slam`（大表，留在她面前的地上，z -1；左右对称）", "84 × 34",
     "链锯把人狠狠砸在面前的地上：地面炸开**一圈很大的泥浆和碎石冲击波**，中间裂开几道地缝，泥浆和石块往四周飞，环上溅着火花和"
     "几滩荧光绿的化学液，最后尘土慢慢落下、地缝暗下去。画在**地上**（从斜上方看的扁椭圆），中心在格子底部中间。**左右对称**，8 帧。",
     MD + ", " + SP + ", " + CG,
     "A BIG GROUND SLAM, 8 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell: "
     "1 a white-hot flash 16 squares wide; 2 a thick shock ring of brown MUD 34 squares wide and 12 tall with an "
     "orange spark edge, CRACKS splitting out from the middle; 3 the ring 54 wide and 18 tall, mud clots, rock chunks "
     "and orange sparks thrown up to both sides (mirrored), neon-green chemical splashes on the ring; 4 the ring 76 "
     "wide and 26 tall, thinner; 5 the ring breaking into clumps at the edge, the cracks glowing dull orange; 6 the "
     "dust settling; 7 the cracks dimming; 8 faint mud specks and thin dust. " + MAGIC + ".",
     row(8, 84, 34) + CENTER),
]
ICONS = [
    ("skill", "技能 1「链锯冲撞」图标", "skill_icons[0] `asset/tft/icons/tft_renni_skill`",
     "一把链锯从左下往右上猛冲，后面拖着几道速度线，导板前端喷出一大把橙色火花。",
     ICON + ": " + SAW + " thrust from the lower left to the upper right, bars first, three speed streaks behind it, a "
     "big fan of orange-yellow sparks spraying from the bar tips. Colours: " + BR + ", " + SL + ", " + SP + ", " + CG
     + "."),
    ("skill2", "技能 2「锯刃格挡」图标", "skill_icons[1] `asset/tft/icons/tft_renni_skill2`",
     "一把链锯竖着立在画面中间，前面一道钢蓝色的护盾弧，弧上一闪白光。",
     ICON + ": " + SAW + " standing UPRIGHT in the middle, bars up, a curved steel-blue SHIELD ARC in front of it "
     "with a white glint and brass rivets. Colours: " + SL + ", " + BR + ", " + CG + "."),
    ("ult", "大招「泥奔者重击」图标", "skill_icons[2] `asset/tft/icons/tft_renni_ult`",
     "一把链锯从上往下狠狠砸在地上，地面裂开，泥浆和碎石往两边喷，导板上溅着火花。",
     ICON + ": " + SAW + " slamming DOWN from the top, bars first, into cracked ground at the bottom, a burst of brown "
     "mud and rock chunks to both sides, orange sparks off the bars, a neon-green splash. Colours: " + MD + ", " + BR
     + ", " + SP + ", " + CG + "."),
]
BIG_FX = ["r_slam"]

GROUPS = [
    ("a_hit q_hit r_hit (saw sparks, hits)", ["tft13_chainsaw_base_chainsaw_spin", "hit_spark_blue",
                                              "draven_skin39_e_hitflash1", "trait_adept_throw_sparks",
                                              "alistar_base_e_flash"]),
    ("r_slam (the slam on the ground)", ["alistar_base_e_impactring", "tft5_volibear_base_shockwave",
                                         "tft6_jinx_base_rocks_2x2", "base_dash_dirttrail", "tft_base_dust"]),
    ("p p_rush (shimmer)", ["tft7_dragonpurple_base_firelight", "tft_firefly_mote", "xayah_skin01_recall_glow_64",
                            "aura_self_128_1"]),
    ("q_slow (mud, smoke)", ["tft_vi_smoke_2x2", "malphite_skin25_primary_z_tar_exit_smoke", "impactcloud"]),
    ("e e_guard r_up (guard, stun)", ["tft13_chainsaw_base_q_chainsaw_mult", "ekko_skin36_flame_ring",
                                      "ashe_skin17_head_star"]),
]


def lp(p):
    return RF.lp(p)


def design_1x(name="idle", k=1 / PPU):
    """A design at game size (k of its squares), cropped."""
    import pixel_down as PD
    d = np.asarray(Image.open(lp(os.path.join(HD, f"{name}.png"))).convert("RGBA"))
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    ys, xs = np.nonzero(g[..., 3] > 0)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def size_sheet(path):
    """Renni at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x()]
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
    d.text((8, 36), f"伦妮 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
           fill=(255, 255, 255, 255), font=font)
    img.convert("RGB").save(path)
    return figs[0].shape


def design_sheet(path):
    """The idle at 4x, its own squares."""
    a = np.asarray(Image.open(lp(os.path.join(HD, "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (a.shape[1] * 4 + 32, a.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(a, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape, icons=True):
    h, w = shape[:2]
    L = []
    a = L.append
    n_ic = len(ICONS) if icons else 0
    a("# 伦妮：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/renni_design.png`："
      "祖安的炼金男爵，结实的女人，橘红背头、苍白脸、灰色鼻夹和荧光绿导管，背后一大团墨绿羽毛，双手端着一把洋红引擎、黄铜双导板的大链锯）。"
      f"伦妮在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/renni_size.png`：伦妮缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里伦妮自己的特效贴图（**灰色的形状，游戏里再染色**：链锯旋转、火花、砸地冲击环、碎石、尘土、光点），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **伦妮是祖安的炼金男爵，特效都是她的大链锯和化学药剂**：链锯的**橙黄色火花**和钢屑、黄铜的闪光、炼金男爵的**荧光绿化学液**"
      "（她导管和药剂罐的颜色）、**微光（Shimmer）的紫粉色光**、祖安的**泥浆**和碎石（她是「泥奔者」）；不要魔法符文，不要光滑的霓虹光束，"
      "不要闪电，不要血。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、火花、冲击波、尘土、泥浆溅射没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。她没有飞行道具。冲撞、竖锯格挡、把人举起来的动作"
      "都画在她自己的动作帧里，这里不画。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `renni_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `renni_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「微光狂热」 | 血量低于 40% 时给自己打一针微光：几秒内加攻速，并持续回复最大生命的一部分（30 秒一次） | `p` · `p_rush` |")
    a("| 普攻「链锯研磨」 | 链锯往前一顶，一次锯三下 | `a_hit` |")
    a("| 技能 1 =「链锯冲撞」 | 端着链锯冲向目标，在前方扇形里连锯三下：物理伤害 + 减速 | `q_hit` · `q_slow` |")
    a("| 技能 2 =「锯刃格挡」 | 把链锯竖起来挡在身前：护盾 + 减伤 | `e` · `e_guard` |")
    a("| 大招 =「泥奔者重击」 | 链锯把目标挑起来举过头顶（晕眩，她自己回血），再狠狠砸在面前的地上：砸地范围伤害 | `r_hit` · `r_up` · `r_slam` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火花、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("火花（链锯）", SPARK), ("黄铜（导板、铆钉）", BRASS), ("钢（锯齿、护盾弧）", STEEL),
                        ("荧光绿化学液（导管、药剂）", CHEM), ("微光紫粉", SHIMMER), ("泥浆", MUD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `renni_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, zh, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `renni_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `renni_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `renni_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_renni_fx`（小的）和 `tft_renni_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- p 和 p_rush 由 tft.dll 在血量低于线时播 / 挂上（--plain 的数据在格挡时自己播）。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="renni_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "renni_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    RF.REF, RF.GROUPS = REF, GROUPS
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_renni.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "renni_design.png"))
    shape = size_sheet(os.path.join(out, "design", "renni_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"renni_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"renni_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
                   if not a.only else []), f, ensure_ascii=False, indent=1)
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
