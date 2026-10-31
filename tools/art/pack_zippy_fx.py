#!/usr/bin/env python3
"""Build zippy_fx_pack.zip: step 3 of Zippy's sprite - Codex draws its effects and its three skill icons
(the tft dragons' way).

    python tools/lol/fx_ref_zippy.py            # the particle references -> C:/t/zz_work/fxref
    python tools/art/pack_zippy_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name zippy_fx_redo_pack]

The pack (C:/t/zz_work/fx/zippy_fx_pack, zipped into --out, default D:/TFM2-Workshop/zippy_packs) holds PROMPTS.md
(also written to assets/source/zippy/PROMPTS_FX.md), design/zippy_design.png (the approved idle at 4x on its own
squares), design/zippy_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (its own set-7 particle textures and Kled's - grey shapes the game tints,
grouped by the effect they inform). The effects are the views the kit binds (tools/kit/build_zippy.py, the user's
picks 2026-10-31: jungle, plan A 「冒险家突击」): view_effects a_hit, q_hit, e, e_hit, r, r_hit; view_buffs p_guild,
e_speed, r_shield. Plus the three skill icons.
Its colours: the hot pink of its feather locks, the gold of its saddle, the sky blue of TFT's Somersault shield,
brown dust.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture).
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

TMP = "C:/t/zz_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "zippy", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "zippy", "hd")
NAME = "zippy_fx_pack"
PPU = 2.2

PINK = "#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36"           # its feather locks: pale pink to deep magenta
GOLD = "#FFF4C2, #FFD24A, #E39A1A, #9A5A0E"                     # its saddle's gold trim and ring
SKY = "#F2FCFF, #AEEBFF, #5CC6F0, #2A86C2"                      # TFT's Somersault shield (its aqua nova) and steel hooks
DUST = "#F0E2C8, #C9AE86, #94775A, #5E4A38"                     # the dust its claws kick up
PK = f"a feather-pink ramp ({PINK})"
GO = f"a gold ramp ({GOLD})"
SK = f"a sky-blue ramp ({SKY})"
DU = f"a dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and "
         "four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky "
         "shapes; no fire, no lightning, no smooth neon beams")
HER = "the raptor stands in the middle, not drawn: 24 squares wide and 38 tall, upright on two legs, its head at the upper right"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little gold "
        "corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「利爪踢」：爪子踢中，4 帧", "view_effects `tft_zippy_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "利爪踢中：一下金色的闪光，三道交叉的玫红爪痕，几根玫红小羽毛和金色小星星往两边崩开。**左右对称**，4 帧。",
     PK + ", " + GO,
     "A CLAW KICK HIT, 4 frames, " + LR + ": 1 a cream-gold flash 4 squares across; 2 three short thick hot-pink claw "
     "marks crossing in a fan, 12 squares across, pale pink along their middles; 3 the marks breaking into small pink "
     "feather tufts and gold sparkles flying out to both sides (mirrored); 4 a few drifting tufts and a puff of dust. "
     + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("q_hit", "技能 1「后空翻踢」：往上踢中，5 帧", "view_effects `tft_zippy_q_hit`（跟随目标，z 3；左右对称）", "20 × 24",
     "后空翻踢中：从下往上**一道玫红色的大弧线**（像脚踢过的轨迹，左右对称的两道弧向上合拢），弧顶一下金光爆开，"
     "被踢飞的人周围几颗金色四角星往上飞、羽毛往两边飘。**左右对称**，5 帧。",
     PK + ", " + GO,
     "AN UPWARD KICK BURST, 5 frames, " + LR + ": 1 a gold flash low in the cell; 2 two hot-pink crescent ARCS sweeping "
     "UP from the bottom on both sides (mirrored), meeting at the top, 18 squares wide and 20 tall, pale pink on their "
     "leading edges; 3 a bright cream-gold burst at the top where they meet, 10 squares across, little rays; 4 three or "
     "four gold four-point stars shooting UPWARD from it and pink feather tufts drifting out to both sides; 5 the stars "
     "fading at the top, a last feather. " + MAGIC + ".",
     row(5, 20, 24) + CENTER),
    ("e", "技能 2「翻滚冲锋」：起滚扬尘，4 帧", "view_effects `tft_zippy_e`（放在它起滚的地面上，不跟随，z 1；左右对称）", "30 × 10",
     "它缩成球滚出去的那一下：地上**一团褐色尘土往两边扬开**，几根玫红小羽毛被带起来。**只在地面上**。**左右对称**，4 帧。",
     DU + ", " + PK,
     "A DUST KICK-OFF, 4 frames, " + LR + ": on the GROUND only (the bottom of the cell): 1 a small dust puff in the "
     "middle, 8 squares wide; 2 brown dust billowing out low to both sides (mirrored), 26 squares wide, 6 tall, pale "
     "tops; 3 the puffs rolling outward and thinning, two small pink feather tufts tossed up; 4 the last dust fading. "
     + MAGIC + ".",
     row(4, 30, 10) + CENTER),
    ("e_hit", "技能 2「翻滚冲锋」：撞到，4 帧", "view_effects `tft_zippy_e_hit`（跟随被撞到的人，z 3；左右对称）", "16 × 16",
     "被羽毛球撞到：一圈玫红色的冲击小环一下撑开，几根羽毛和金色小星星往两边弹开。**左右对称**，4 帧。",
     PK + ", " + GO,
     "A BUMP HIT, 4 frames, " + LR + ": round a unit standing in the middle (not drawn): 1 a pale-pink flash 5 squares "
     "across; 2 a hot-pink impact ring (a circle 14 squares across, 2 squares thick) bursting open; 3 the ring breaking "
     "into pink feather tufts and gold sparkles bouncing out to both sides (mirrored); 4 a few fading sparkles. "
     + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("r", "大招「翻滚突袭」：起跳，4 帧", "view_effects `tft_zippy_r`（放在它起跳的地面上，不跟随，z 1；左右对称）", "34 × 12",
     "它蹬地高高跃起的一下：脚下地面**一圈尘土环**往外推开（从斜上方看的椭圆，宽是高的 3 倍），几道金色的小光线往上射。**只在地面上**。**左右对称**，4 帧。",
     DU + ", " + GO,
     "A SPRING-OFF RING, 4 frames, " + LR + ": on the GROUND only (the bottom of the cell): 1 a gold glint in the middle; "
     "2 a ring of brown dust pushed outward (an ellipse 30 squares wide, 9 tall), pale on its top edge, three short gold "
     "light streaks shooting straight UP from the middle; 3 the dust ring wider and thinner, the streaks gone; 4 the last "
     "dust fading. " + MAGIC + ".",
     row(4, 34, 12) + CENTER),
    ("r_hit", "大招「翻滚突袭」：砸中，6 帧", "view_effects `tft_zippy_r_hit`（大表，跟随被砸中的人，z 4；左右对称）", "56 × 40",
     "羽毛球从天上砸下来：一下奶黄的大闪光，地上**一圈玫红 + 金色的冲击环**猛地撑开（从斜上方看的椭圆），尘土和羽毛往两边炸开，"
     "最后被砸晕的人头顶上方转着**三颗金色的小星星**。**人站的地方留空**。**左右对称**，6 帧。",
     PK + ", " + GO + ", " + DU,
     "A CRASH LANDING, 6 frames, " + LR + ": round a unit standing in the middle (not drawn, 16 squares wide, 30 tall): "
     "1 a big cream-gold flash at its feet, 14 squares across, short rays; 2 a hot-pink and gold SHOCK RING bursting "
     "open on the ground (an ellipse 50 squares wide, 14 tall, 2 squares thick), brown dust thrown up low to both sides "
     "(mirrored); 3 the ring at the cell's edge, pink feather tufts flying out and up on both sides; 4 the dust rolling "
     "out, the ring thinning; 5 three small gold four-point STARS appearing in a row above where its head is (the top "
     "of the cell), the dust settling; 6 the stars, the last dust. The middle of the cell (the unit's body) stays "
     "EMPTY. " + MAGIC + ".",
     row(6, 56, 40) + CENTER),
    ("p_guild", "被动「冒险家之魂」：护甲光，6 帧循环", "view_buffs `tft_zippy_p_guild`（跟随它，脚下地面，z 3；左右对称）", "30 × 8",
     "身边有队友时它的被动：脚下一圈**淡淡的金色小光环**（从斜上方看的椭圆），上面几颗小金星一闪一闪。很淡，不抢眼。**只在地面上**。**左右对称**，6 帧循环。",
     GO,
     "A FAINT GUILD RING, 6 looping frames, " + LR + ": on the GROUND round its feet only: a thin gold ring (an ellipse "
     "26 squares wide, 6 tall, 1 square thick, its back half fainter), two or three tiny gold four-point stars twinkling "
     "on it in turn; frames 1-6 the twinkles moving round and the ring breathing a little brighter and dimmer (every "
     "frame left-right symmetric). Subtle: mostly mid and dark gold, only the twinkles bright. " + MAGIC + ".",
     row(6, 30, 8) + CENTER),
    ("e_speed", "技能 2「翻滚冲锋」：加速，6 帧循环", "view_buffs `tft_zippy_e_speed`（跟随加速的友军，脚下，z 3；左右对称）", "30 × 14",
     "被加速的友军：脚边**两侧几道玫红色的风线**往外飘（像跑起来带的风），一两根小羽毛跟着飘。**只在脚边两侧**。**左右对称**，6 帧循环。",
     PK,
     "SPEED WISPS, 6 looping frames, " + LR + ": low beside a unit's feet (the unit not drawn, the middle 10 squares of "
     "the cell empty): on EACH side (mirrored) two or three short horizontal hot-pink wind lines 5-8 squares long, "
     "pale pink at their inner ends, streaming outward, one small pink feather tuft drifting with them; frames 1-6 the "
     "lines sliding outward and new ones appearing near the feet (every frame left-right symmetric). " + MAGIC + ".",
     row(6, 30, 14) + CENTER),
    ("r_shield", "大招「翻滚突袭」：护盾，6 帧循环", "view_buffs `tft_zippy_r_shield`（大表，跟随它，z 3；左右对称）", "44 × 50",
     "它的护盾：一个**天蓝色的泡泡护盾**罩着它（竖着的椭圆，只画边，2 格厚，亮的一边奶白），边上几点玫红和金色的光点转着；"
     "**泡泡里面它的身体位置留空**。**左右对称**，6 帧循环。",
     SK + ", " + PK + ", " + GO,
     "A BUBBLE SHIELD, 6 looping frames, " + LR + ": round " + HER + ": a sky-blue BUBBLE (an upright ellipse 40 squares "
     "wide and 46 tall, only its 2-square rim drawn, pale sky-white on the upper left of the rim, deeper blue below), a "
     "faint sky shimmer band across its top; small pink and gold glints running round the rim; frames 1-6 the glints "
     "moving round and the rim breathing (every frame left-right symmetric). INSIDE the bubble stays EMPTY (its "
     "body). " + MAGIC + ".",
     row(6, 44, 50) + CENTER),
]
ICONS = [
    ("skill", "技能 1「后空翻踢」图标", "skill_icons[0] `asset/tft/icons/tft_zippy_skill`",
     ICON + ": a little pink-feathered orange raptor upside down in a backflip, both clawed feet kicking up, a "
               "hot-pink crescent arc following the kick, gold stars bursting at its tip."),
    ("skill2", "技能 2「翻滚冲锋」图标", "skill_icons[1] `asset/tft/icons/tft_zippy_skill2`",
     ICON + ": a round ball wrapped in hot-pink feathers rolling to the right, a gold saddle edge showing, brown dust "
               "and pink speed lines trailing behind it."),
    ("ult", "大招「翻滚突袭」图标", "skill_icons[2] `asset/tft/icons/tft_zippy_ult`",
     ICON + ": a pink feather ball diving down from the upper left onto the ground, a hot-pink and gold shock ring "
               "bursting under it, a sky-blue shield glint round the ball, three gold stars."),
]
BIG_FX = ["r_hit", "r_shield"]
FLYING = ()

GROUPS = [
    ("a_hit q_hit e_hit (the kicks and the bumps)",
     ["kled_base_ba_hit_flash", "kled_base_ba_hit_blast", "tft7_dragonguild_base_q_hit_flash",
      "tft7_dragonguild_base_spark", "poppy_skin07_star_02_gold"]),
    ("r_hit r e (the crash and the dust)",
     ["tft7_dragonguild_base_q_impactring", "tft7_dragonguild_base_outerring", "kled_base_r_smoke_dust",
      "kled_base_e_rock_debris"]),
    ("r_shield (its shield)",
     ["tft7_dragonguild_base_q_shieldmask", "tft7_dragonguild_base_q_aqua_nova_04", "kled_base_r_shield_base",
      "kled_base_r_shield_mult"]),
    ("e_speed p_guild (the roll's trail, the speed, the guild)",
     ["tft7_dragonguild_base_q_smoketrail03", "tft7_dragonguild_base_trail3", "kled_base_r_trail",
      "tft7_dragonguild_base_bokeh_dots_4x4"]),
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
    """Zippy at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"呲呲 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 呲呲：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/zippy_design.png`："
      "3/4 朝右、两条腿站得笔直的小迅猛龙：圆圆的橙褐色脑袋、头顶玫红尖刺、脸周围黑色尖片、半闭的大紫眼；喉咙到肚子一块紫色围兜；"
      "脖子两侧垂着玫红长羽毛；背上洋红马鞍（金边、金环）；橙褐色的腿、紫色脚踝绑带、黑色大爪；尾巴上一排粉色尖鳍）。"
      f"呲呲在游戏里是**高清**的（每个游戏格子里约 2.2×2.2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/zippy_size.png`：呲呲缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里呲呲自己的特效贴图（翻滚、冲击环、打中的闪光、护盾泡泡）和克烈的（斯嘎尔的冲锋尘土、护盾）"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **呲呲是机灵的冒险家小龙，特效都是它的味道**：玫红色的羽毛丝和小羽毛、金色的闪光和四角小星星、褐色的尘土团，"
      "只有护盾用天蓝色的泡泡光；不要火焰、不要闪电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zippy_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `zippy_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「利爪踢」 | 抬腿往前一蹬 | `a_hit` |")
    a("| 被动「冒险家之魂」 | 身边每有一个友方英雄，护甲和魔抗多一点 | `p_guild` |")
    a("| 技能 1 =「后空翻踢」 | 后空翻，两只脚往上踢中敌人，把它踢飞一下 | `q_hit` |")
    a("| 技能 2 =「翻滚冲锋」 | 缩成羽毛球滚向敌人，路上撞到的受伤，身边友军加速 | `e` · `e_hit` · `e_speed` |")
    a("| 大招 =「翻滚突袭」 | 套护盾，跃起缩成球砸向生命百分比最高的敌人：伤害、晕眩、小击退 | `r` · `r_hit` · `r_shield` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("玫红（它的羽毛）", PINK), ("金（马鞍的金边、星星）", GOLD), ("天蓝（护盾泡泡）", SKY),
                        ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `zippy_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    if n_ic:
        a("---\n")
        a(f"## 技能图标（{n_ic} 个，64×64）\n")
        for k, (name, title, _, prompt) in enumerate(ICONS, 1):
            a(f"### 图标 {k}. `zippy_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `zippy_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `zippy_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_zippy_fx`（小的）和 `tft_zippy_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- e、r 放在它起滚 / 起跳的地面上（不跟随，z 1）；p_guild 是它脚下的 caster buff，r_shield 是它身上的 caster buff（z 3）；"
      "e_speed 是被加速的友军脚边的 buff（z 3）；a_hit、q_hit、e_hit、r_hit 打在目标身上（r_hit 是 tft.dll 落地时放的）。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="zippy_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/zippy_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_zippy.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "zippy_design.png"))
    shape = size_sheet(os.path.join(out, "design", "zippy_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"zippy_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"zippy_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
