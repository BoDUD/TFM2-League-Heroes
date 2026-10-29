#!/usr/bin/env python3
"""Build smeech_fx_pack.zip: step 3 of Smeech's sprite - Codex draws his effects and his three skill icons
(pack_scar_fx.py's way).

    python tools/lol/fx_ref_smeech.py           # his TFT particle textures -> C:/t/sm_work/fxref
    python tools/art/pack_smeech_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name smeech_fx_redo_pack]

The pack (C:/t/sm_work/fx/smeech_fx_pack, zipped into --out, default D:/TFM2-Workshop/smeech_packs) holds PROMPTS.md
(also written to assets/source/smeech/PROMPTS_FX.md), design/smeech_design.png (the approved idle at 4x on its own
squares), design/smeech_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/tft_fx_ref.png (his own TFT particle textures - grey shapes the game tints - grouped by the
effect they inform). The effects are the views the kit binds (tools/kit/build_smeech.py, the user's picks 2026-10-29:
jungle, plan A 「废铁伏击手」): view_effects a_hit, p_hit, q_land, q_hit, e_hit, r_hit; view_buffs e_shred, r_frenzy.
Plus the three skill icons. The leap and the slashes' moves are in his own frames.
His colours: his brass claws' white-gold slash light, his arms' NEON-GREEN chem lights, a crit's hot red-orange, scrap
metal (grey steel chips, torn armour plates), Zaun grime and dust.
Red side: every picture is symmetric left to right (the client never mirrors an effect picture).
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

TMP = "C:/t/sm_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "smeech", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "smeech", "hd")
NAME = "smeech_fx_pack"
PPU = 2.4

CLAW = "#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C"               # his brass claws' slash light, white to brass
CHEM = "#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A"               # the neon-green chem lights in his arms
CRIT = "#FFFFFF, #FFE8B0, #FF9A3C, #E8402A, #8E1426"               # a crit's hot flash, red-orange
SCRAP = "#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30"              # scrap steel, torn armour plates
GRIME = "#E6DCC4, #B8A684, #847250, #54482E"                       # Zaun grime and dust
CL = f"a white-to-brass claw light ramp ({CLAW})"
CH = f"a neon chem green ramp ({CHEM})"
CR = f"a hot crit red-orange ramp ({CRIT})"
SC = f"a scrap steel ramp ({SCRAP})"
GR = f"a grime dust ramp ({GRIME})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at "
         "both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips "
         "of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning")
HIM = "the crouching gremlin stands in the middle, not drawn: 53 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-green frame with little "
        "riveted brass corners, a deep grimy purple-navy inside, the symbol big and centred, lit from the upper left; "
        "pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px")
CLAWS = "a big brass MECHANICAL CLAW (an olive-green metal bracer with a glowing neon-green diamond light, five long thin hooked brass fingers)"

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：爪子抓中，4 帧", "view_effects `tft_smeech_a_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "爪子抓在人身上：**两组爪痕交叉成 X**（每组三道细长的白金色爪痕，两头尖），中心一个小白闪，几颗灰色金属碎屑往两边崩开。**左右对称**，4 帧。",
     CL + ", " + SC,
     "A CLAW SCRATCH, 4 frames, " + LR + ": 1 a small white flash 6 squares across in the middle; 2 two sets of THREE "
     "thin curved white-gold claw lines crossing in an X, each line 14 squares long and pointed at both ends (the X "
     "mirrored); 3 the lines thinner and fading to brass, grey steel chips flying out to both sides; 4 the last glints "
     "and chips. " + MAGIC + ".",
     row(4, 18, 18) + CENTER),
    ("p_hit", "伏击：技能暴击，5 帧", "view_effects `tft_smeech_p_hit`（跟随目标，z 3；左右对称）", "26 × 26",
     "技能暴击时在目标身上亮一下：一个**红橙色的锯齿爆星**（八个尖角），白色的芯，外面一圈碎裂的冲击环，几块金属碎片往四周飞。"
     "比普攻显眼得多。**左右对称**，5 帧。",
     CR + ", " + CL + ", " + SC,
     "A CRITICAL HIT, 5 frames, " + LR + ": 1 a white core 8 squares across; 2 a jagged EIGHT-POINTED STARBURST 22 "
     "squares across, hot red-orange with a white-yellow core; 3 the star bigger and its points thinner, a broken "
     "shock ring around it, grey steel shards flying out to both sides (mirrored); 4 the star breaking into red sparks; "
     "5 the last sparks. " + MAGIC + ".",
     row(5, 26, 26) + CENTER),
    ("q_land", "废铁黑客：落地的尘土，5 帧", "view_effects `tft_smeech_q_land`（留在他落地的地上，z -1；左右对称）", "44 × 16",
     "他跳到目标身前落地：脚下「噗」地炸开一圈**灰土和碎屑**，几颗绿色的小火花往两边弹，最后尘土落下。画在**地上**（扁椭圆），"
     "中心在格子底部中间。**左右对称**，5 帧。",
     GR + ", " + SC + ", " + CH,
     "A LANDING PUFF, 5 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell: 1 a "
     "flat dust ring 14 squares wide and 4 tall; 2 the ring 30 wide and 8 tall, puffs of grime dust rising at both ends, "
     "steel chips and a few neon-green sparks kicked out to both sides (mirrored); 3 the ring 40 wide, the dust higher "
     "and thinner; 4 the dust settling; 5 faint specks. " + MAGIC + ".",
     row(5, 44, 16) + CENTER),
    ("q_hit", "废铁黑客：连斩，4 帧", "view_effects `tft_smeech_q_hit`（跟随目标，z 2；左右对称）", "22 × 24",
     "三连斩每一下：**三道竖着往下的爪痕**（中间那道直，两边的往外弯，像扇子一样张开），白金色的爪痕边上带一点**荧光绿**的光，"
     "火花往两边溅。**左右对称**，4 帧。",
     CL + ", " + CH + ", " + SC,
     "A TRIPLE CLAW SLASH, 4 frames, " + LR + ": 1 three thin white-gold slash lines 18 squares long raking DOWN, the "
     "middle one straight, the outer two curving outwards like a fan (mirrored), each pointed at both ends; 2 the "
     "lines fully drawn with a neon-green glow along their edges, sparks spraying to both sides; 3 the lines thinner, "
     "fading to brass and green; 4 the last glints. " + MAGIC + ".",
     row(4, 22, 24) + CENTER),
    ("e_hit", "拆解：撕开护甲，5 帧", "view_effects `tft_smeech_e_hit`（跟随目标，z 2；左右对称）", "30 × 26",
     "双爪往两边一撕：**两道大爪痕从中间往左右两边撕开**（像把东西扯成两半），中间迸出几块**灰色的碎甲片**往两边飞，绿色火花。"
     "**左右对称**，5 帧。",
     CL + ", " + SC + ", " + CH,
     "A TEARING RIP, 5 frames, " + LR + ": 1 a white flash 8 squares across in the middle; 2 two big curved claw "
     "sweeps (each three white-gold lines) tearing from the middle out to the left and to the right, 26 squares across "
     "in all (mirrored); 3 grey steel ARMOUR PLATE fragments (3-5 squares, angular, a lit edge) bursting out of the "
     "middle to both sides with neon-green sparks; 4 the plates farther and tumbling, the claw lines fading; 5 the "
     "last chips. " + MAGIC + ".",
     row(5, 30, 26) + CENTER),
    ("e_shred", "拆解：被撕掉护甲（减护甲），6 帧循环", "view_buffs `tft_smeech_e_shred`（跟随被撕的人，头顶，z 3；左右对称）",
     "16 × 14",
     "被撕掉护甲的人头顶：一块**裂成两半的灰色小盾牌**（中间一道锯齿裂缝），两半慢慢往外掉，裂缝里闪一点绿光。**左右对称**，6 帧循环。",
     SC + ", " + CH,
     "A BROKEN ARMOUR MARK OVER THE HEAD, 6 looping frames, " + LR + ": in the cell (it rides over the unit's head) a "
     "small grey steel SHIELD shape 10 squares wide and 11 tall split down the middle by a jagged crack, the two halves "
     "a square apart; frames 1-6 the halves rocking a square outwards and back, a neon-green glint flickering in the "
     "crack. " + MAGIC + ".",
     row(6, 16, 14) + CENTER),
    ("r_hit", "废铁狂潮：跳斩打中，5 帧", "view_effects `tft_smeech_r_hit`（跟随目标，z 2；左右对称）", "30 × 30",
     "大招每跳一下打中：**两组三道的大爪痕交叉成 X**，比普攻大得多，爪痕周围裹着**荧光绿**的光，中心白闪，火花和碎屑往四周飞。"
     "**左右对称**，5 帧。",
     CL + ", " + CH + ", " + SC,
     "A FRENZY SLASH, 5 frames, " + LR + ": 1 a white flash 10 squares across; 2 two sets of THREE thick claw lines "
     "crossing in a big X 26 squares across, white-gold cores with neon-green glowing edges (the X mirrored); 3 the "
     "lines at full length, sparks and steel chips flying out in all directions (mirrored); 4 the lines thinning to "
     "green; 5 the last green glints. " + MAGIC + ".",
     row(5, 30, 30) + CENTER),
    ("r_frenzy", "废铁狂潮：狂潮状态，6 帧循环", "view_buffs `tft_smeech_r_frenzy`（跟随他，z 3；左右对称）", "60 × 44",
     "大招期间他身上：身体两侧往上窜**荧光绿的速度线**（细长的竖条，一闪一闪），脚下一圈淡绿光圈，几点绿色光点往上飘。"
     "身体位置留空。**左右对称**，6 帧循环。",
     CH + ", " + CL,
     "A FRENZY AURA, 6 looping frames, " + LR + ", " + HIM + ": at both sides of him (mirrored) a few thin vertical "
     "neon-green SPEED STREAKS (1 square wide, 6-14 tall) flickering upward, a faint green ring " + GROUND_E + " 50 "
     "squares wide and 8 tall at the bottom, a few bright green motes drifting up; frames 1-6 the streaks shooting up "
     "and fading in turn. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 60, 44) + CENTER),
]
ICONS = [
    ("skill", "技能 1「废铁黑客」图标", "skill_icons[0] `asset/tft/icons/tft_smeech_skill`",
     "一只黄铜机械爪从右上往左下扑下来，后面拖着三道白金色的爪痕，爪子上的绿灯发亮。",
     ICON + ": " + CLAWS + " diving down from the upper right to the lower left, three white-gold claw slash lines "
     "trailing behind it, its green light glowing. Colours: " + CL + ", " + CH + ", " + SC + "."),
    ("skill2", "技能 2「拆解」图标", "skill_icons[1] `asset/tft/icons/tft_smeech_skill2`",
     "两只爪子把一块灰色的盾牌从中间撕成两半，碎甲片往两边飞，裂缝里冒绿光。",
     ICON + ": two brass claws tearing a grey steel SHIELD apart down the middle, the halves pulled to the left and to "
     "the right, armour chips flying, neon-green light bursting from the crack. Colours: " + SC + ", " + CL + ", " + CH +
     "."),
    ("ult", "大招「废铁狂潮」图标", "skill_icons[2] `asset/tft/icons/tft_smeech_ult`",
     "一串折线形的绿色跳跃轨迹在画面里来回折，每个折点上一个白金色的 X 爪痕，正中一个红橙色的暴击爆星。",
     ICON + ": a ZIGZAG trail of neon-green leaps bouncing across the tile, a small white-gold X of claw marks at each "
     "corner of the zigzag, a red-orange critical starburst in the middle. Colours: " + CH + ", " + CL + ", " + CR + "."),
]

GROUPS = [
    ("a_hit q_hit r_hit e_hit (his claw slashes)", ["tft13_gremlin_base_z_slash02", "tft13_gremlin_base_z_slash05",
                                                   "tft13_gremlin_base_z_slash06", "tft13_gremlin_base_q_hit01"]),
    ("p_hit (crit flash)", ["tft13_gremlin_base_z_glow", "tft13_gremlin_base_ringlight", "shaco_skin43_q_glow01",
                            "base_slash"]),
    ("q_land e_hit (dust, scrap)", ["impactcloud", "tft_illaoi_dust", "thresh_ashe_base_ground_cracknoise_mult",
                                    "shield_ringburnoff"]),
    ("r_frenzy (chem glow)", ["tft10_gnar_base_z_zed_shadowwisps", "tft5_dmg_skin36_misttrailsoft",
                              "tft7_soraka_base_trail_mult", "energymote_64_1"]),
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
    """Smeech at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"史密奇 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 史密奇：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/smeech_design.png`："
      "祖安的炼金男爵小怪物，青绿高礼帽、横着的红尖耳、灰褐绒毛脸，两条橄榄绿机械手臂末端是细长的黄铜爪，蹲得很低、双爪张开）。"
      f"史密奇在游戏里是**高清**的（每个游戏格子里约 2.4×2.4 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/smeech_size.png`：史密奇缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里史密奇自己的特效贴图（**灰色的形状，游戏里再染色**：爪痕、光晕、尘土、绿色拖尾），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **史密奇是祖安的废铁小怪物，特效都是他的机械爪**：**白金色的细长爪痕**（三道一组、两头尖），机械臂里的**荧光绿**光，"
      "暴击时**红橙色的锯齿爆星**，灰色的废铁碎屑和撕下来的护甲片，祖安的灰土；不要魔法符文，不要光滑的霓虹光束，不要闪电。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、爪痕、冲击波、尘土没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。跳跃和挥爪的动作画在他自己的动作帧里，这里不画。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `smeech_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `smeech_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「伏击」 | 自带暴击率；技能也能暴击，技能暴击伤害更高 | `p_hit` |")
    a("| 普攻「双爪连撕」 | 左右爪轮流挥抓 | `a_hit` |")
    a("| 技能 1 =「废铁黑客」 | 跳到射程内血最少的敌人身前，连斩 3 下；目标死了再跳一次 | `q_land` · `q_hit` |")
    a("| 技能 2 =「拆解」 | 双爪一撕，造成伤害并撕掉对方护甲几秒 | `e_hit` · `e_shred` |")
    a("| 大招 =「废铁狂潮」 | 不受控制，接连跳斩最多 5 个敌人，每跳一下叠暴击率 | `r_hit` · `r_frenzy` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、爪痕、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("爪痕白金（爪子的光）", CLAW), ("荧光绿（机械臂的化学光）", CHEM), ("暴击红橙", CRIT),
                        ("废铁灰（碎屑、护甲片）", SCRAP), ("祖安灰土", GRIME)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `smeech_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `smeech_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `smeech_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `smeech_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a("- 一张表：`asset/tft/effects/tft_smeech_fx`，tag = 名字。")
    a("- 全部断言左右对称。")
    a("- q_land / q_hit / r_hit / p_hit 由 tft.dll 播（--plain 的数据自己播 q_land / q_hit / r_hit）。")
    a("- 用 `pixel_1x/` 切格（import_scar_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="smeech_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/smeech_packs", help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_smeech.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "smeech_design.png"))
    shape = size_sheet(os.path.join(out, "design", "smeech_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"smeech_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"smeech_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
