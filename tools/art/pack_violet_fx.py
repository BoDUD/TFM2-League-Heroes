#!/usr/bin/env python3
"""Build violet_fx_pack.zip: step 3 of Violet's sprite - Codex draws her effects and her three skill icons
(pack_vander_fx.py's way).

    python tools/lol/fx_ref_violet.py           # her TFT particle textures -> C:/t/vo_work/fxref
    python tools/art/pack_violet_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name violet_fx_redo_pack]

The pack (C:/t/vo_work/fx/violet_fx_pack, zipped into --out, default dist/violet_packs) holds PROMPTS.md (also written
to assets/source/violet/PROMPTS_FX.md), design/violet_design.png (the approved idle at 4x on its own squares),
design/violet_size.png (her at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the base
fighter) and refs/tft_fx_ref.png (her own TFT particle textures - grey shapes the game tints - grouped by the effect
they inform). The effects are the views the kit binds (tools/kit/build_violet.py, the user's picks 2026-10-28:
jungle, plan A 「搏击手·1-2-3连招」): view_effects a_hit, q_jab, q_up, e_dash, e_hit, r_slam, r_hit, p_burst; view_buffs
r_fury, p_wind. Plus the three skill icons. She throws nothing: no projectile pictures.
Her colours: the GOLD of her gauntlets' fists, their blue-grey STEEL, a hot IMPACT white-orange, the ELECTRIC cyan of
her TFT combo's crackle, her hair's PINK for the fury, Zaun dust, a warm green for the second wind.
Red side: every picture is symmetric left to right (the client never mirrors an effect picture; nothing here points).
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

TMP = "C:/t/vo_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "violet", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "violet", "hd")
NAME = "violet_fx_pack"
PPU = 2.0

GOLD = "#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010"              # her gauntlets' gold fist frames
STEEL = "#F0F6FA, #C4D2DC, #8A9CAC, #566676, #2C3640"             # their blue-grey steel plates
IMPACT = "#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C"            # a hot punch impact
SPARK = "#FFFFFF, #D8FAFF, #7EE6FF, #2EA8E8, #145A9A"             # the electric crackle of her combo (TFT13_Red's Q)
PINK = "#FFE0F0, #FF8ACB, #F53F8D, #B22059, #5C0E30"              # her hair: the fury
DUST = "#F0E2C8, #C8AE88, #9A7E5C, #64503A"                       # Zaun dust and grit
HEAL = "#F2FFE8, #BFF0A0, #7ED460, #3E9A3A, #1E5A22"              # the second wind
GD = f"a gold ramp ({GOLD})"
SL = f"a steel blue-grey ramp ({STEEL})"
IM = f"a hot impact ramp ({IMPACT})"
SP = f"an electric cyan ramp ({SPARK})"
PK = f"a hot pink ramp ({PINK})"
DS = f"a dust brown ramp ({DUST})"
HL = f"a fresh green ramp ({HEAL})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch "
         "flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock "
         "rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no "
         "fire columns")
HER = "the slim girl with the two huge gauntlets stands in the middle, not drawn: 34 squares wide and 38 tall"
TARGET = "the unit stands in the middle, not drawn: 16 squares wide and 36 tall"
GROUND_E = "on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall)"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted "
        "corners, a deep plum-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")
GAUNTLET = ("her huge IRON GAUNTLET (blue-grey steel plates on the forearm, copper piston rods, a square gold-yellow "
            "fist frame with rows of dark rivets, a thick gold knuckle plate)")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：铁拳直拳打中，4 帧", "view_effects `tft_violet_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "拳套打在人身上：一个白热的**星形闪光**，几颗金色和钢灰色的火星往两边崩开，一小圈冲击环。**左右对称**，4 帧。",
     IM + ", " + GD,
     "A PUNCH IMPACT, 4 frames, " + LR + ": 1 a white-hot four-pointed STAR flash 8 squares across; 2 a short orange "
     "shock ring 12 squares wide and 6 tall, gold and steel sparks flying out to both sides (mirrored); 3 the ring "
     "thinner and wider, the sparks farther, a puff of dust in the middle; 4 the last dust fading. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_jab", "1-2-3连招：刺拳打中（前两拳），4 帧", "view_effects `tft_violet_q_jab`（跟随目标，z 2；左右对称）", "18 × 18",
     "连招的前两拳，又快又脆：一个比普攻更亮的白热**星形闪光**，带几道**短短的电光**（青色的小闪电）往两边跳，几颗金色火星。"
     "**左右对称**，4 帧。",
     IM + ", " + SP + ", " + GD,
     "A QUICK JAB HIT, 4 frames, " + LR + ": 1 a bright white-hot STAR flash 10 squares across with two short "
     "electric-cyan zigzag crackles jumping out to both sides (mirrored, 4 squares long); 2 a small orange shock ring 14 "
     "squares wide and 6 tall, gold sparks; 3 the ring thin, the crackles gone, a few sparks; 4 fading glints. "
     + MAGIC + ".",
     row(4, 18, 18) + CENTER),
    ("q_up", "1-2-3连招：第 3 拳上勾拳打中（击飞），6 帧", "view_effects `tft_violet_q_up`（跟随目标，z 2；左右对称）", "24 × 36",
     "第三拳从下往上的上勾拳：一道**竖直往上冲的旋风光柱**（白热的芯、外面一圈青色的电光），金色和橙色的火星呈 V 字往两边上方喷出，"
     "脚下一小圈冲击环，最后电光散掉。比刺拳狠得多。**左右对称**，6 帧。",
     IM + ", " + SP + ", " + GD + ", " + DS,
     "AN UPPERCUT THAT THROWS THE TARGET UP, 6 frames, " + LR + ": 1 a big white-hot flash at the bottom middle 10 "
     "squares across; 2 a tall narrow WHIRLWIND column shooting UP 28 squares from the middle - a white-hot core 4 "
     "squares wide wrapped in curling electric-cyan streaks - gold and orange sparks spraying up and out in a V to both "
     "sides (mirrored), a shock ring at the bottom 18 squares wide and 6 tall; 3 the column at its full height (34 "
     "squares), cyan crackles jumping off it; 4 the column thinner, the sparks higher; 5 the sparks falling, dust at "
     "the bottom; 6 the last sparks and crackles fading. " + MAGIC + ".",
     row(6, 24, 36) + CENTER),
    ("e_dash", "冲拳：起步踢起的尘土，5 帧", "view_effects `tft_violet_e_dash`（留在起跑的地上，z 1；左右对称）", "30 × 12",
     "冲出去那一脚：地上「轰」地踢起一团尘土和碎石，往两边扩散开再落下。留在她起跑的地上（不跟着她），画成圆的，往哪边冲都能用。"
     "**左右对称**，5 帧。",
     DS + ", " + GD,
     "A DASH'S KICK-OFF DUST, 5 frames, " + LR + ": everything " + GROUND_E + ": 1 a burst of dust 10 squares wide "
     "at the bottom middle, two small grit stones flung up to both sides (mirrored); 2 the dust spreading 18 squares "
     "wide and 7 tall, rolling puffs; 3 28 squares wide, the stones falling; 4 thinning; 5 the last thin puffs. "
     + MAGIC + ".",
     row(5, 30, 12) + CENTER),
    ("e_hit", "冲拳：一拳打中（打退），5 帧", "view_effects `tft_violet_e_hit`（跟随目标，z 2；左右对称）", "26 × 26",
     "冲到身上的那一拳：一下很大的白热**星形闪光**，一个**方方的金色冲击波**（拳套正面的形状，带几排深色的小方孔）往外炸开，"
     "橙色火星和碎石往两边四溅，留一团尘土。**左右对称**，5 帧。",
     IM + ", " + GD + ", " + DS,
     "A RUSHING GAUNTLET BLOW, 5 frames, " + LR + ": 1 a big white-hot STAR flash 12 squares across; 2 a SQUARE gold "
     "shock wave (the gauntlet's fist face, with a row of dark rivet holes) 14 squares across bursting out, orange "
     "sparks flying out to both sides (mirrored); 3 a wide orange shock ring 24 squares wide and 10 tall, the sparks "
     "farther, grit stones; 4 the ring thin, dust puffs in the middle; 5 the dust fading. " + MAGIC + ".",
     row(5, 26, 26) + CENTER),
    ("r_slam", "底城怒拳：双拳砸地的冲击波，8 帧", "view_effects `tft_violet_r_slam`（大表，留在她脚下的地上，z -1；左右对称）",
     "84 × 30",
     "大招：从半空落下，两只拳套狠狠砸进地面，**地面炸开一圈很大的冲击波**（从中间往外推的橙色和金色的环，环上跳着青色的电光），"
     "地上裂开几道裂缝，碎石和尘土往四周飞，裂缝里透出一点橙色的热光，最后慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），"
     "中心在格子底部中间（她的脚下）。**左右对称**，8 帧。",
     IM + ", " + GD + ", " + SP + ", " + DS,
     "A GROUND SHOCKWAVE, 8 frames, " + LR + ": everything " + GROUND_E + ", centred at the bottom middle of the cell "
     "(her feet): 1 a white-hot flash 16 squares wide; 2 a thick orange shock ring 34 squares wide and 12 tall with a "
     "gold outer edge, CRACKS (dark brown lines 1 square wide) starting out from the middle (mirrored); 3 the ring 54 "
     "wide and 18 tall, short electric-cyan crackles jumping along it, the cracks longer, chunks of stone and dust "
     "flung up to both sides; 4 the ring 76 wide and 26 tall, thinner; 5 the ring at the edge breaking into bright "
     "segments, dust billowing; 6 the dust settling, the cracks glowing orange; 7 the cracks dimming; 8 faint cracks "
     "and thin dust. " + MAGIC + ".",
     row(8, 84, 30) + CENTER),
    ("r_hit", "底城怒拳：被击飞，4 帧", "view_effects `tft_violet_r_hit`（跟随被击飞的人，z 2；左右对称）", "18 × 20",
     "被冲击波掀起来的人：脚下「砰」地一下橙色的闪光，尘土往上喷，两边几颗碎石。**左右对称**，4 帧。",
     IM + ", " + DS,
     "A UNIT THROWN UP, 4 frames, " + LR + ": 1 an orange-white flash at the bottom middle 10 squares wide; 2 a jet of "
     "dust shooting upward 14 squares high, grit stones to both sides (mirrored); 3 the dust spreading and thinning; 4 "
     "the last puffs. " + MAGIC + ".",
     row(4, 18, 20) + CENTER),
    ("r_fury", "底城怒拳：怒火（越打越快、吸血），6 帧循环", "view_buffs `tft_violet_r_fury`（跟随她，z 3；左右对称）", "40 × 44",
     "砸地之后她打红了眼：两只拳套的位置（身体两侧、胸口高度）各绕着**几道粉红色和青色的短电光**，一跳一跳地噼啪作响，"
     "脚下一圈淡淡的粉红色光圈，几点粉色火星往上飘。身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。",
     PK + ", " + SP + ", " + GD,
     "A FIGHTER IN A FURY, 6 looping frames, " + LR + ", " + HER + ": at both sides of her at chest height (where her "
     "gauntlets are, mirrored) a small knot of three or four short crackling ZIGZAG sparks in hot pink and electric "
     "cyan (each 3-5 squares long), a faint pink ring " + GROUND_E + " 30 squares wide and 7 tall at the bottom, and a "
     "few pink embers (1-2 squares) drifting up from it; frames 1-6 the crackles jumping to new places, the embers "
     "rising. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 40, 44) + CENTER),
    ("p_burst", "搏击手：回气的一下（半血时触发一次），5 帧", "view_effects `tft_violet_p_burst`（跟随她，z 3；左右对称）", "40 × 44",
     "她第一次被打到半血时缓过一口气：脚下「呼」地一圈**清新的绿色光环**往外一荡，身体两侧往上冒一串绿色和白色的光点，头顶一闪。"
     "身体位置留空。**左右对称**，5 帧。",
     HL + ", " + IM,
     "A SECOND WIND, 5 frames, " + LR + ", " + HER + ": 1 a fresh green flash ring " + GROUND_E + " 14 squares wide; 2 "
     "the ring 30 squares wide and 8 tall, two columns of green and white light motes rising at both sides of her "
     "(mirrored); 3 the motes up at her shoulders, a white glint over her head; 4 the ring fading, the motes higher; 5 "
     "the last motes. The middle (the body) left empty. " + MAGIC + ".",
     row(5, 40, 44) + CENTER),
    ("p_wind", "搏击手：回气中（持续回血），6 帧循环", "view_buffs `tft_violet_p_wind`（跟随她，z 3；左右对称）", "36 × 40",
     "回气的 2 秒里：身体两侧几点**绿色的小光点**慢慢往上飘，脚下一圈很淡的绿色光圈。要淡，不要盖住她。身体位置留空。"
     "**左右对称**，6 帧循环。",
     HL,
     "HEALING OVER TIME, 6 looping frames, " + LR + ", " + HER + ": a faint thin green ring " + GROUND_E + " 28 "
     "squares wide and 7 tall at the bottom, and at both sides of her (mirrored) a few small green and white motes "
     "(1-2 squares) drifting slowly upward from the ring to her shoulders; frames 1-6 the motes rising and new ones "
     "starting. Subtle. The middle (the body) left empty. " + MAGIC + ".",
     row(6, 36, 40) + CENTER),
]
ICONS = [
    ("skill", "技能 1「1-2-3连招」图标", "skill_icons[0] `asset/tft/icons/tft_violet_skill`",
     "两只大铁拳套一左一右往前打，中间一记往上的上勾拳带着青色电光和白热的闪光。",
     ICON + ": " + GAUNTLET + " driving UP in an uppercut at the centre, a white-hot star flash at its knuckles and "
     "short electric-cyan crackles round it, two small speed lines below it for the two jabs before. Colours: " + GD +
     ", " + SL + ", " + IM + ", " + SP + "."),
    ("skill2", "技能 2「冲拳」图标", "skill_icons[1] `asset/tft/icons/tft_violet_skill2`",
     "一只大铁拳套从左往右冲出来，后面拖着橙色的速度线和尘土，拳头前一个白热的星形闪光。",
     ICON + ": " + GAUNTLET + " rushing forward from the left to the right, bold orange speed lines and a puff of dust "
     "trailing behind it, a white-hot star flash at its knuckles. Colours: " + GD + ", " + SL + ", " + IM + ", " + DS +
     "."),
    ("ult", "大招「底城怒拳」图标", "skill_icons[2] `asset/tft/icons/tft_violet_ult`",
     "两只大铁拳套从上往下砸进地面，地面炸开一圈橙色和金色的冲击波，裂缝四散，粉红色的电光往上跳。",
     ICON + ": two huge iron gauntlets (gold fist frames, blue-grey steel) smashing DOWN together into the ground at "
     "the centre, an orange-and-gold SHOCKWAVE ring bursting out flat around them, cracks spreading through the ground, "
     "hot pink crackles jumping up. Colours: " + GD + ", " + SL + ", " + IM + ", " + PK + "."),
]
BIG_FX = ["r_slam"]

GROUPS = [
    ("a_hit q_jab e_hit r_hit (impacts)", ["tft13_red_base_flash", "tft_tar_flash", "tft_tar_erode",
                                          "jayce_skin05_animeshapes02"]),
    ("q_up (the uppercut's whirlwind)", ["tft12_galio_base_q_tar_tornado_beam", "tft12_galio_q_tar_tornado_burstwind_v04",
                                         "tft13_red_base_q_elec_01"]),
    ("r_fury (crackles)", ["tft13_red_base_lightningerosion", "tft_set6_skin05_lightning02"]),
    ("e_dash r_slam (dust)", ["petchibiaatrox_skin1_smoke01", "tft9_ksante_base_r_smokeerosion01", "tft12_galio_base_smoke"]),
    ("p_burst p_wind (glow)", ["common_ball32_gradient_128", "caitlyn_skin11_r_small_mote",
                               "tft8_starguardian_particles_green"]),
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
    """Violet at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"蔚奥莱 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 蔚奥莱：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/violet_design.png`："
      "祖安街头的少女拳手，洋红色头发，两只手各戴一只比头还大的铁拳套（蓝灰钢板、金黄方框拳头），双拳举起的格斗架势）。"
      f"蔚奥莱在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/violet_size.png`：蔚奥莱缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里蔚奥莱自己的特效贴图（**灰色的形状，游戏里再染色**：星形打击、电光、旋风、尘土、光点），"
      "按用在我们哪张特效分好了行。只在本地用。")
    a("> - **蔚奥莱是祖安的街头拳手，特效都是她的两只铁拳套**：白热的星形拳光、金色和钢灰色的金属火星、青色的短电光（金铲铲里她连招带电）、"
      "厚重的冲击环、祖安的尘土和碎石；大招之后的怒火是她头发的粉红色，回气是清新的绿色；不要魔法符文，不要光滑的霓虹光束，不要火柱。")
    a("> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、电光、冲击波、尘土没有黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。她没有飞行道具，没有要朝向的画面。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `violet_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格左右对称——Claude 直接用这一份切格导入）" + ("；图标交付 `violet_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「搏击手」 | 每一下都附带额外真实伤害、全能吸血；每条命第一次掉到半血时，2 秒里回一口气 | `p_burst` · `p_wind` |")
    a("| 普攻 | 拳套一记直拳 | `a_hit` |")
    a("| 技能 1 =「1-2-3连招」 | 两记刺拳，再一记上勾拳把目标打飞 | `q_jab` · `q_up` |")
    a("| 技能 2 =「冲拳」 | 冲到敌人身上一拳打退 | `e_dash` · `e_hit` |")
    a("| 大招 =「底城怒拳」 | 跳进敌群双拳砸地，冲击波击飞周围的敌人；之后几秒打红了眼：攻速、吸血提高（队里家人越多攻速越高） | `r_slam` · `r_hit` · `r_fury` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色（拳套的拳头框、图标边框）", GOLD), ("钢灰（拳套钢板）", STEEL), ("白热拳光", IMPACT),
                        ("青色电光", SPARK), ("粉红（怒火）", PINK), ("尘土", DUST), ("绿色（回气）", HEAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `violet_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `violet_icon_{name}.png`：{title}\n")
            a(zh + "\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `violet_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `violet_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_violet_fx`（小的）和 `tft_violet_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- p_burst / p_wind 由 tft.dll 在她第一次掉到半血时播 / 挂上；r_fury 由 tft.dll 在砸地时挂上。")
    a("- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="violet_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "violet_packs"), help="folder for the zip")
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
        sys.exit(f"no TFT references in {REF}: run tools/lol/fx_ref_violet.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "violet_design.png"))
    shape = size_sheet(os.path.join(out, "design", "violet_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"violet_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX] +
                  ([{"file": f"violet_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
