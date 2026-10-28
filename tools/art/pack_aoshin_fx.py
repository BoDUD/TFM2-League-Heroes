#!/usr/bin/env python3
"""Build aoshin_fx_pack.zip: step 3 of Ao Shin's sprite - Codex draws his effects and his three skill icons
(pack_krug_fx.py's way).

    python tools/lol/fx_ref_aoshin.py            # the particle references -> C:/t/ao_work/fxref
    python tools/art/pack_aoshin_fx.py [--no-zip] [--out DIR] [--only a_hit,r_bolt --name aoshin_fx_redo_pack]

The pack (C:/t/ao_work/fx/aoshin_fx_pack, zipped into --out, default dist/aoshin_packs) holds PROMPTS.md (also written to
assets/source/aoshin/PROMPTS_FX.md), design/aoshin_design.png (the approved idle at 4x on its own squares),
design/aoshin_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (his own set-7 particle textures and Volibear's - grey shapes the game tints, grouped
by the effect they inform). The effects are the views the kit binds (tools/kit/build_aoshin.py, the user's picks
2026-10-28: mid, plan A 「风暴龙神」): view_projectiles a_ball, q_beam; view_effects a_hit, q_hit, e_cast, r_bolt;
view_buffs q_sil (r_sil shows it too), e_shield, r_cloud and tft.dll's p_bolt, p_storm. Plus the three skill icons.
His colours: ELECTRIC white / pale cyan / cyan / blue lightning, dark STORM-cloud slate, a touch of his mask's GOLD.
Red side: a picture with a front and a back is symmetric left to right (the client never mirrors an effect picture);
the flying ones are turned with their flight (a_ball round, q_beam top-bottom symmetric); the bolts from the sky have
no front and stay as drawn.
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

TMP = "C:/t/ao_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "aoshin", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "aoshin", "hd")
NAME = "aoshin_fx_pack"
PPU = 2.0

ELEC = "#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0"            # his lightning, the ball, the sparks
STORM = "#9AA6C0, #6A7690, #444E68, #262C40"                    # the storm cloud
SCALE = "#BFF6FF, #6FE0F2, #2AB4D2, #18809E"                    # his cyan scales and mane (the wind, the wisps)
GOLD = "#FFF1A8, #FFD24A, #E0A020, #9A6410"                     # his mask and shoulder guards
EL = f"an electric white-cyan-blue ramp ({ELEC})"
SM = f"a dark storm-cloud slate ramp ({STORM})"
SC = f"a cyan scale-and-wind ramp ({SCALE})"
GD = f"a gold ramp ({GOLD})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
TB = ("flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the "
      "game turns the picture with its flight, so flying left it is upside down)")
ROUND = ("ROUND: SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square (the game turns it with its "
         "flight)")
MAGIC = ("everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, "
         "dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no "
         "runes, no soft round bubbles")
HIM = "the hovering dragon is in the middle, not drawn: 37 squares wide and 38 tall"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with small gold "
        "corners, a deep storm-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_ball", "普攻：球状闪电（飞行中），4 帧循环", "view_projectiles `tft_aoshin_a_ball`（追踪弹道，z 2；圆的、四面对称）", "12 × 12",
     "从他嘴里吐出的**一团球状闪电**：白色的芯、青蓝色的球，外面几道细小的电弧一跳一跳。**四面对称**（飞行时会跟着方向转），4 帧循环。",
     EL,
     "A BALL OF LIGHTNING IN FLIGHT, 4 looping frames, " + ROUND + ": a round ball 8 squares across - a white core 3 "
     "squares, pale cyan around it, a cyan-blue rim - with three or four tiny jagged arcs (2-3 squares) flicking out of "
     "it at different places in each frame (keep each frame symmetric). " + MAGIC + ".",
     row(4, 12, 12) + CENTER),
    ("a_hit", "普攻：球状闪电打中，4 帧", "view_effects `tft_aoshin_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "球状闪电打中：一下白色的闪光，一圈青蓝色的小电弧往外炸开，几颗电火花。**左右对称**，4 帧。",
     EL,
     "A SMALL LIGHTNING POP, 4 frames, " + LR + ": 1 a white star flash 8 squares across; 2 a ring of short jagged "
     "cyan-blue arcs bursting out 14 squares across, a white core; 3 the arcs broken into sparks flying out; 4 the last "
     "sparks fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_beam", "雷息：一道闪电（飞行中），3 帧循环", "view_projectiles `tft_aoshin_q_beam`（直线、很快，z 2；上下对称）", "40 × 10",
     "从他嘴里喷出去的**一段锯齿形闪电**：中间一条白色的亮芯，外面青蓝色，前头尖、后头散成几道细电弧。**朝右飞、上下对称**，3 帧循环（每帧锯齿位置变一下）。",
     EL,
     "A SEGMENT OF A LIGHTNING BREATH, 3 looping frames, " + TB + ": a jagged horizontal BOLT 38 squares long - a white "
     "core 1-2 squares thick zigzagging along it, pale cyan and cyan-blue around (6-8 squares thick in all), the head on "
     "the right pointed and brightest, the tail on the left splitting into three thin forks; the zigzag shifting in each "
     "frame. " + MAGIC + ".",
     row(3, 40, 10) + CENTER),
    ("q_hit", "雷息：被闪电打中，4 帧", "view_effects `tft_aoshin_q_hit`（跟随被打中的人，z 2；左右对称）", "20 × 24",
     "被雷息打中：身上「啪」地一下炸开一团电光，几道电弧在身上乱窜，一圈电火花。比普攻大一点。**左右对称**，4 帧。",
     EL,
     "A UNIT STRUCK BY LIGHTNING, 4 frames, " + LR + ", centred on the unit's body: 1 a white flash 12 squares across; 2 "
     "jagged cyan-blue arcs crawling over a body-sized area 18 wide and 22 tall (mirrored), a white core; 3 the arcs "
     "thinning, sparks flying out; 4 the last sparks. " + MAGIC + ".",
     row(4, 20, 24) + CENTER),
    ("q_sil", "被电麻（沉默）：头上冒电火花，6 帧循环", "view_buffs `tft_aoshin_q_sil`（跟随被沉默的人，z 4；左右对称；大招的沉默也用它）", "18 × 44",
     "被雷息或闪电暴雨电麻了（放不了技能）：头顶上一圈**噼啪作响的小电弧**，像短路一样一闪一闪。"
     "身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。",
     EL,
     "A UNIT STUNG BY STATIC (silenced), 6 looping frames, " + LR + ", " + TARGET + ": over the head (the top 10 squares "
     "of the cell) a little crown of crackling jagged arcs 12 squares wide, white and cyan-blue, two tiny sparks hopping "
     "beside it (mirrored); frames 1-6 the arcs flickering on and off in turn. The rest of the cell empty. " + MAGIC + ".",
     row(6, 18, 44) + CENTER),
    ("e_cast", "腾云：飞起时的一团风云，5 帧", "view_effects `tft_aoshin_e_cast`（留在起飞的地方，z 1；左右对称）", "40 × 26",
     "他向后飞开的那一下：原地「呼」地卷起一团青色的风和一小片灰白的云，往两边散开。中心在格子底部中间。**左右对称**，5 帧。",
     SC + ", " + SM,
     "A GUST OF CLOUD AT TAKE-OFF, 5 frames, " + LR + ": 1 a small puff of pale slate cloud 12 squares wide at the bottom "
     "middle; 2 two curls of cyan wind sweeping out to both sides (mirrored) from it, the cloud 24 wide; 3 the wind curls "
     "at their widest (38 squares), the cloud rising 20 squares; 4 the cloud thinning into wisps; 5 the last wisps. "
     + MAGIC + ".",
     row(5, 40, 26) + CENTER),
    ("e_shield", "腾云：风暴护盾，6 帧循环", "view_buffs `tft_aoshin_e_shield`（跟随他，z 3；左右对称）", "46 × 44",
     "护盾在的时候：他身体外面一圈**旋转的青色风环和几缕灰白的云**，风环上时不时闪过一道小电弧。"
     "身体位置留空（只画外圈）。**左右对称**，6 帧循环。",
     SC + ", " + SM + ", " + EL,
     "A WIND-AND-CLOUD SHIELD HELD, 6 looping frames, " + LR + ", " + HIM + ": an outline of streaming cyan wind 44 "
     "squares wide and 42 tall around him (2 squares thick, broken into curls), a few pale slate cloud wisps on it, one "
     "tiny white arc flicking along it in each frame (mirrored); the curls flowing round in turn. The middle (the body) "
     "left empty. " + MAGIC + ".",
     row(6, 46, 44) + CENTER),
    ("p_bolt", "风暴龙威：天雷劈中（被动），5 帧", "view_buffs `tft_aoshin_p_bolt`（大表，跟随被劈的人，z 3；不用左右对称）", "26 × 90",
     "被动「风暴龙威」：一道**又粗又亮的天雷从格子顶上直劈下来**，砸在人身上，脚下炸开一圈电光。人站在格子底部中间（不画人）。5 帧（半秒）。",
     EL + ", " + SM,
     "A BOLT FROM THE SKY ON A UNIT, 5 frames, the unit stands at the bottom middle, not drawn (16 squares wide, 36 "
     "tall): 1 a thin white jagged bolt from the very top of the cell down to the unit's feet, a little dark cloud wisp "
     "at the top; 2 the bolt at its thickest (5-6 squares: a white core, cyan-blue edges) with two forks, a white flash "
     "ring 20 squares wide at the feet " + GROUND_E + "; 3 the bolt flickering thinner, cyan-blue sparks bursting from the "
     "feet; 4 the bolt gone, arcs crawling up the unit's outline; 5 the last sparks at the feet. " + MAGIC + ".",
     row(5, 26, 90) + CENTER),
    ("p_storm", "风暴龙威：落雷后他身上的电光（增伤），6 帧循环", "view_buffs `tft_aoshin_p_storm`（跟随他，z 3；左右对称）", "46 × 44",
     "落雷之后他变强的几秒：身上**噼啪地缠着几道电弧**，脚下一圈淡淡的青色电光。不要太显眼，身体位置留空。**左右对称**，6 帧循环。",
     EL,
     "A CHARGED STORM AURA, 6 looping frames, " + LR + ", " + HIM + ": four or five short jagged white-cyan arcs flicking "
     "along his outline (44 squares wide, 42 tall), a different few in each frame (mirrored), and a faint thin ring of "
     "cyan light 30 squares wide " + GROUND_E + " at the bottom. The middle (the body) left empty. Subtle. " + MAGIC + ".",
     row(6, 46, 44) + CENTER),
    ("r_cloud", "闪电暴雨：头顶的雷云（召雷时），6 帧循环", "view_buffs `tft_aoshin_r_cloud`（大表，跟随他，z 4；左右对称）", "70 × 64",
     "他召来闪电暴雨的这一秒多：**头顶上空一大团翻滚的乌云**，云里不停地闪着电光。云画在格子最上面 22 格，下面留出他的位置（不画他）。**左右对称**，6 帧循环。",
     SM + ", " + EL,
     "A STORM CLOUD OVERHEAD, 6 looping frames, " + LR + ", " + HIM + " at the bottom middle: in the top 22 squares of "
     "the cell a big rolling dark slate STORM CLOUD 66 squares wide (lumpy, lit pale on its upper edges), lightning "
     "flashing inside it - in each frame one or two jagged white-cyan flashes at mirrored places, the cloud's lumps rolling "
     "slowly. The rest of the cell empty. " + MAGIC + ".",
     row(6, 70, 64) + CENTER),
    ("r_bolt", "闪电暴雨：一道落雷劈中，6 帧", "view_effects `tft_aoshin_r_bolt`（大表，劈在被打中的人身上，z 3；不用左右对称）", "24 × 90",
     "闪电暴雨的每一道雷：**一道锯齿形的闪电从格子顶上劈到人脚下**（比被动的天雷细一点、快一点），脚下炸开一小圈电光。人站在格子底部中间（不画人）。6 帧。",
     EL,
     "ONE STRIKE OF A LIGHTNING STORM, 6 frames, the unit stands at the bottom middle, not drawn (16 squares wide, 36 "
     "tall): 1 a thin white flicker at the top of the cell; 2 a jagged bolt (3-4 squares thick: a white core, cyan-blue "
     "edges) from the top down to the feet; 3 the bolt bright with one fork, a white flash 14 squares wide " + GROUND_E +
     " at the feet; 4 the bolt thinner, sparks bursting from the feet; 5 a faint afterglow line, sparks falling; 6 the "
     "last sparks. " + MAGIC + ".",
     row(6, 24, 90) + CENTER),
]
ICONS = [
    ("skill", "技能 1「雷息」图标", "skill_icons[0] `asset/tft/icons/tft_aoshin_skill`",
     "雷息：一个金色的龙头侧面朝右，张开的嘴里喷出一道粗粗的白色锯齿闪电，穿过整个图标。",
     ICON + ": a GOLD DRAGON HEAD in profile facing right at the left, its jaw open, breathing a thick jagged white-cyan "
     "LIGHTNING BOLT straight across to the right edge, small sparks along it."),
    ("skill2", "技能 2「腾云」图标", "skill_icons[1] `asset/tft/icons/tft_aoshin_skill2`",
     "腾云：一团卷着青色风的白云，上面一条青色的龙尾往左上方飞走。",
     ICON + ": a swirling white-and-pale-slate CLOUD with curls of cyan wind in the lower half, a cyan dragon's spiky "
     "TAIL sweeping away up to the upper left out of it."),
    ("ult", "大招「闪电暴雨」图标", "skill_icons[2] `asset/tft/icons/tft_aoshin_ult`",
     "闪电暴雨：上面一大团乌云，好几道白色的闪电同时劈下来。",
     ICON + ": a big dark slate STORM CLOUD across the top, four jagged white-cyan LIGHTNING BOLTS striking down from it "
     "to the bottom edge, little flashes where they land."),
]
BIG_FX = ["p_bolt", "r_cloud", "r_bolt"]
SYM = {"a_ball": "round (both ways)", "q_beam": "top-bottom", "p_bolt": "none (a bolt from the sky)",
       "r_bolt": "none (a bolt from the sky)"}

GROUPS = [
    ("a_ball a_hit (ball lightning)", ["tft7_aoshin_base_ba_ball_lightning", "tft7_aoshin_base_sonicwaves_ba",
                                       "tft7_aoshin_base_sparkmote", "tft_electric_sparks"]),
    ("q_beam q_hit q_sil (the breath)", ["tft_kennen_skin11_i_lightning03_128", "tft_set6_skin05_lightning03_128_1",
                                         "tft_dragoncharge_lightning_trail", "tft7_kennen_base_r_electric_arcs"]),
    ("p_bolt r_bolt (bolts from the sky)", ["tft7_aoshin_base_r_lighitngshapes_4", "volibear_runewars_lightning_graphic",
                                            "volibear_base_jacobsladder", "xinzhao_skin27_e_lightningerosion03"]),
    ("r_cloud e_shield e_cast (storm clouds)", ["volibear_base_ult_clouds_a", "volibear_base_dissolve_cloudy_01",
                                                "leesin_skin31_e_cloudtxt03", "tft7_aoshin_base_r_smoketip"]),
    ("p_storm (his storm sigils, aura)", ["tft7_aoshin_base_r_sigil_2", "tft7_aoshin_base_r_sigil_3",
                                          "tft7_aoshin_base_star_128", "tft7_aoshin_base_r_tar_flipbook"]),
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
    """Ao Shin at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"敖兴 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 敖兴：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/aoshin_design.png`："
      "竖直悬浮的风暴之龙，青绿鳞片的蛇形身体和浅青尖刺鬃毛，金面具和两只弯角，金护肩蓝宝石，蓝紫龙爪，尾巴尖化成青色的风）。"
      f"敖兴在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/aoshin_size.png`：他缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲第 7 赛季敖兴自己的特效贴图（球状闪电、落雷的闪电形状、风暴符印）和英雄联盟沃利贝尔的雷云、闪电贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **敖兴是风暴之龙，特效都是雷电和风暴**：锯齿形、带白色亮芯的**闪电**，噼啪的**青蓝色电弧和电火花**，深灰蓝的**雷云**，一点青色的**风**；"
      "不要火，不要紫色魔法，不要符文，不要软软的圆泡泡。")
    a("> - **特效要亮**：每道闪电都有白色的芯，暗底上一眼能看见。**光、电弧、风、云没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：围着人、在人身上炸开的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；飞行的 `a_ball` 四面对称、`q_beam` 上下对称"
      "（游戏会跟着飞行方向转它们）；从天上劈下来的 `p_bolt`、`r_bolt` 没有朝向，不用对称。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `aoshin_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `aoshin_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「风暴龙威」 | 开战几秒后，天雷劈向周围所有敌方英雄（最大生命值百分比真实伤害 + 晕眩），之后他身上缠着电光、伤害提高 | `p_bolt` · `p_storm` |")
    a("| 普攻 | 往前一扑，从嘴里吐出一团球状闪电 | `a_ball` · `a_hit` |")
    a("| 技能 1 =「雷息」 | 张嘴喷出一道直线闪电，打中的敌人被电麻（短暂放不了技能） | `q_beam` · `q_hit` · `q_sil` |")
    a("| 技能 2 =「腾云」 | 敌人贴近时卷起一团风云向后飞开，身上一层风暴护盾 | `e_cast` · `e_shield` |")
    a("| 大招 =「闪电暴雨」 | 立起身子召来头顶的雷云，一连串闪电随机劈向附近的敌方英雄，每道都电麻一下 | `r_cloud` · `r_bolt` · `q_sil` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电弧、风、云没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("闪电（亮芯、电弧、电火花、球状闪电）", ELEC), ("雷云", STORM), ("青色的风（风环、风雾）", SCALE),
                        ("金色（只在图标的龙头和边角用）", GOLD)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `aoshin_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `aoshin_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `aoshin_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `aoshin_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_aoshin_fx`（小的）和 `tft_aoshin_big`（{'、'.join(BIG_FX)}），tag = 名字；r_sil 用 q_sil 的 tag。")
    a("- 对称按 `SYM`（其余左右对称）断言。")
    a("- p_bolt、p_storm 是 tft.dll 在风暴龙威落雷时挂的 buff（30 tick / p_t tick）；r_cloud 在大招整个施法期间挂在他身上；r_bolt 是每道落雷打在被劈的人身上的 ViewEffect；q_beam 是从他嘴里（y_offset q_y）飞出去的纯画面弹道。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="aoshin_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "aoshin_packs"), help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_aoshin.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "aoshin_design.png"))
    shape = size_sheet(os.path.join(out, "design", "aoshin_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"aoshin_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": SYM.get(x[0], "left-right")}
                   for x in FX] +
                  ([{"file": f"aoshin_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
