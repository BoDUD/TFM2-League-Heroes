#!/usr/bin/env python3
"""Build shiohyu_fx_pack.zip: step 3 of Shi Oh Yu's sprite - Codex draws his effects and his three skill icons
(the tft dragons' way).

    python tools/lol/fx_ref_shiohyu.py            # the particle references -> C:/t/sy_work/fxref
    python tools/art/pack_shiohyu_fx.py [--no-zip] [--out DIR] [--only a_hit,r3_hit --name shiohyu_fx_redo_pack]

The pack (C:/t/sy_work/fx/shiohyu_fx_pack, zipped into --out, default D:/TFM2-Workshop/shiohyu_packs) holds PROMPTS.md
(also written to assets/source/shiohyu/PROMPTS_FX.md), design/shiohyu_design.png (the approved idle at 4x on its own
squares), design/shiohyu_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (his own set-7 particle textures - grey shapes the game tints, grouped by the
effect they inform). The effects are the views the kit binds (tools/kit/build_shiohyu.py, the user's picks 2026-10-30:
top lane, plan A 「玉龙三连」): view_projectiles r3_wave; view_effects a_hit, q_hit, e_slam, e_hit, r, r1_hit, r2_hit,
r3_hit, p; view_buffs e_slow, r_jade, p_skin. Plus the three skill icons.
His colours: jade green with a white core, the gold of his horns and chest edges, grey-brown rock for the dust.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the line picture (FLYING) points right and is symmetric top to bottom (the game turns it with the cast).
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

TMP = "C:/t/sy_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "shiohyu", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "shiohyu", "hd")
NAME = "shiohyu_fx_pack"
PPU = 2.46

JADE = "#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F"          # his jade: white, mint, jade, deep jade
GOLD = "#FFF7D6, #FFDD7A, #F0B23A, #B97A1C"                       # the gold of his horns and chest edges
ROCK = "#E3DCCB, #B0A690, #7A705C, #4A4336"                       # rock and dust
JA = f"a jade ramp ({JADE})"
GO = f"a gold ramp ({GOLD})"
RO = f"a rock-dust ramp ({ROCK})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its direction; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, "
         "a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, "
         "no purple, no smooth neon beams")
HIM = "the dragon-man stands in the middle, not drawn: 30 squares wide and 42 tall, his head near the top right"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark gold frame with little jade "
        "corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：爪痕，4 帧", "view_effects `tft_shiohyu_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "龙爪打中：两道交叉成 X 的玉色爪痕（每道三条平行的细爪痕），中间一下白光，几颗玉屑飞出。**左右对称**，4 帧。",
     JA,
     "A CLAW HIT, 4 frames, " + LR + ": 1 a white flash 4 squares across; 2 two sets of three thin parallel jade claw "
     "marks crossing in an X, 14 squares across, white along their middles; 3 the marks fading from their ends, small "
     "jade chips flying out symmetrically; 4 a few fading chips. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_hit", "玉拳连打：拳头打中，3 帧", "view_effects `tft_shiohyu_q_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "一拳打中：一个白芯的玉色冲击星（四个尖角），一圈小冲击环，两三点金色火星。**左右对称**，3 帧（快，每拳一下）。",
     JA + ", " + GO,
     "A PUNCH IMPACT, 3 frames, " + LR + ": 1 a four-pointed jade impact star 8 squares across with a white core; 2 a "
     "thin jade ring round it 11 squares wide, two or three gold sparks flying out mirrored; 3 the ring broken into "
     "fading bits. " + MAGIC + ".",
     row(3, 12, 12) + CENTER),
    ("e_slam", "震地：地面裂开的冲击，6 帧", "view_effects `tft_shiohyu_e_slam`（大表，砸地时在他脚下的地面上，不跟随，z 1；左右对称）", "52 × 22",
     "他一拳砸进地面：脚下的地面**裂开一圈发着玉光的裂缝**（从中心往外放射，从斜上方看的椭圆，宽是高的 3 倍左右），"
     "一圈冲击波往外推，碎石块和尘土往两边飞起来。**左右对称**，6 帧（砸下、裂开、冲击波推出去、尘土落下）。",
     JA + ", " + RO,
     "A GROUND SLAM, 6 frames, " + LR + ": on the GROUND, an ellipse seen from above, about 50 squares wide and 16 tall, "
     "its middle where his fist hits: 1 a white-jade flash at the middle; 2 jagged cracks glowing jade running out from "
     "the middle in a symmetric star, a jade ring pushing out; 3 the ring at full width, chunky grey-brown rock chunks "
     "and dust puffs thrown up to both sides (mirrored, up to 6 squares above the ellipse); 4-5 the rocks falling, the "
     "dust spreading, the cracks still glowing; 6 the cracks dim, a little dust. " + MAGIC + ".",
     row(6, 52, 22) + CENTER),
    ("e_hit", "震地：被震飞，4 帧", "view_effects `tft_shiohyu_e_hit`（跟随被打中的人，z 2；左右对称）", "18 × 14",
     "被震到的人脚下：地面迸起一圈碎石和尘土，几颗玉屑。**只在脚下**。**左右对称**，4 帧。",
     RO + ", " + JA,
     "A ROCK BURST, 4 frames, " + LR + ": at the unit's FEET only (the bottom of the cell): 1 a small jade flash on the "
     "ground; 2 small rock chunks and dust puffs bursting up to both sides (mirrored), 10 squares high at most; 3 the "
     "rocks at the top of their arc; 4 the dust settling. " + MAGIC + ".",
     row(4, 18, 14) + CENTER),
    ("e_slow", "震地：减速，6 帧循环", "view_buffs `tft_shiohyu_e_slow`（跟随被减速的人，脚下地面，z 3；左右对称）", "20 × 8",
     "被减速：脚下一圈裂开的地面和慢慢冒起的尘土（从斜上方看的椭圆，宽是高的 3 倍），几颗小碎石在抖。**左右对称**，6 帧循环。",
     RO + ", " + JA,
     "A CRACKED GROUND SNARE, 6 looping frames, " + LR + ": on the GROUND round the unit's feet, an ellipse seen from "
     "above, about 18 squares wide and 6 tall: short cracks with a faint jade glow, small dust puffs rising and "
     "falling, a few pebbles trembling; frames 1-6 the dust breathing (keep every frame left-right symmetric). Nothing "
     "above the feet. " + MAGIC + ".",
     row(6, 20, 8) + CENTER),
    ("r", "玉龙形态（开启）：玉光迸发，6 帧", "view_effects `tft_shiohyu_r`（大表，跟随他，z 4；左右对称）", "44 × 52",
     "他进入玉龙形态的一下：脚下一圈玉光猛地亮起，一圈玉石碎晶和几片小叶子从脚下沿着身体**两侧**往上卷起来，头顶上方一下金色和玉色的光芒。"
     "**身体位置留空**（只画脚下、两侧边缘、头顶）。**左右对称**，6 帧。",
     JA + ", " + GO,
     "A JADE AWAKENING, 6 frames, " + LR + ": round " + HIM + ": 1 a bright jade ring flashing on the ground under his "
     "feet (an ellipse 36 squares wide, 10 tall); 2-3 a whirl of faceted jade shards and a few small jade leaves "
     "spiralling up along BOTH SIDES of him from the ring to above his head, a starburst of jade and gold rays above "
     "his head; 4-5 the shards scattering outward and fading, the ring dimming; 6 a few last glints. The middle of the "
     "cell (his body) stays EMPTY. " + MAGIC + ".",
     row(6, 44, 52) + CENTER),
    ("r_jade", "玉龙形态：持续的玉光，6 帧循环", "view_buffs `tft_shiohyu_r_jade`（大表，跟随他，z 3；左右对称）", "40 × 50",
     "玉龙形态持续时：脚下一圈慢慢转的玉光圈，身体两侧几颗玉色光点往上飘，头顶上方一个小小的玉色光芒在闪。"
     "**身体位置留空**。**左右对称**，6 帧循环。",
     JA + ", " + GO,
     "A JADE STANCE AURA, 6 looping frames, " + LR + ": round " + HIM + ": under his feet a glowing jade ring (an "
     "ellipse 34 squares wide, 9 tall) with small runes of light turning round it; small jade motes drifting up along "
     "both sides of him; a small jade-and-gold glint above his head; frames 1-6 the motes rising and the glint "
     "twinkling (every frame left-right symmetric). The middle of the cell (his body) stays EMPTY. " + MAGIC + ".",
     row(6, 40, 50) + CENTER),
    ("r1_hit", "玉龙形态第 1 击：晕眩的重击，5 帧", "view_effects `tft_shiohyu_r1_hit`（跟随目标，z 3；左右对称）", "22 × 22",
     "第 1 击打中：一下很亮的玉色重击闪光，一圈粗的冲击环，玉石碎片往四周炸开。**左右对称**，5 帧。",
     JA + ", " + GO,
     "A HEAVY JADE BLOW, 5 frames, " + LR + ": 1 a big white-jade flash 8 squares across; 2 a thick jade shock ring "
     "bursting out to 20 squares, faceted jade shards flying out in a symmetric star; 3-4 the ring thinning, the "
     "shards spinning out; 5 fading shards. " + MAGIC + ".",
     row(5, 22, 22) + CENTER),
    ("r2_hit", "玉龙形态第 2 击：真实伤害，5 帧", "view_effects `tft_shiohyu_r2_hit`（跟随目标，z 3；左右对称）", "20 × 24",
     "第 2 击打中（真实伤害）：一道竖直的白金色刺穿光，从中心往上下劈开，金色火星和玉屑飞出。**左右对称**，5 帧。",
     GO + ", " + JA,
     "A PIERCING TRUE STRIKE, 5 frames, " + LR + ": 1 a white point of light; 2 a tall thin VERTICAL slash of white and "
     "gold light 22 squares tall splitting up and down from the middle, a small jade diamond flash at its centre; "
     "3 gold sparks and jade chips flying out to both sides (mirrored); 4-5 the slash thinning and fading. "
     + MAGIC + ".",
     row(5, 20, 24) + CENTER),
    ("r3_wave", "玉龙形态第 3 击：直线玉石冲击波，6 帧", "view_projectiles `tft_shiohyu_r3_wave`（大表，从他身前指向目标的一条线，随方向旋转；上下对称、朝右）", "92 × 24",
     "第 3 击打出的**直线冲击波**：从左端（他身前）往右，地面上一道发着玉光的裂缝一路冲出去，裂缝两边一排排玉石尖晶从地里刺出来"
     "（从左往右一个接一个冒出），最前端一团玉光。**朝右、上下对称**，6 帧（从左往右冲出去、尖晶立起、碎开）。",
     JA + ", " + RO,
     "A JADE SPIKE WAVE, 6 frames, " + TB + ": a long band from the LEFT edge (in front of him) to the RIGHT end: along "
     "its middle a glowing jade crack racing to the right; along both sides of the crack (mirrored) rows of sharp "
     "faceted jade crystal spikes bursting out, pointing outward, up to 9 squares long; a ball of jade light with a "
     "white core at the leading edge; 1-2 the crack and the first spikes at the left, the light rushing right; 3-4 the "
     "spikes along the whole length, the light at the right end; 5-6 the spikes cracking into jade shards and dust and "
     "fading from the left. " + MAGIC + ".",
     row(6, 92, 24) + CENTER),
    ("r3_hit", "冲击波打中，4 帧", "view_effects `tft_shiohyu_r3_hit`（跟随被打中的人，z 3；左右对称）", "18 × 18",
     "冲击波打中：被打中的人脚下一下玉光，几根玉石尖晶从脚下刺起来又碎掉。**左右对称**，4 帧。",
     JA + ", " + RO,
     "A JADE SPIKE HIT, 4 frames, " + LR + ": 1 a jade flash 6 squares across; 2 three faceted jade spikes stabbing "
     "up from the ground at the unit's feet (one in the middle, two leaning out mirrored), 14 squares tall; 3 the "
     "spikes shattering into shards; 4 fading shards and dust. " + MAGIC + ".",
     row(4, 18, 18) + CENTER),
    ("p", "被动「玉石之肤」：化作玉石，5 帧", "view_effects `tft_shiohyu_p`（大表，跟随他，z 4；左右对称）", "40 × 50",
     "他的皮肤一下化成玉石：身体**两侧**一圈玉石晶片从外往里合拢闪一下，脚下一圈石质的光环，头顶一下白光。**身体位置留空**。**左右对称**，5 帧。",
     JA + ", " + RO,
     "A STONE SKIN FLASH, 5 frames, " + LR + ": round " + HIM + ": 1 a ring of faceted jade plates appearing on both "
     "sides of him (mirrored) a little away from his outline; 2-3 the plates closing in to his sides with a white glint "
     "on each, a stone-grey and jade ring on the ground under him (an ellipse 34 squares wide, 9 tall), a white flash "
     "above his head; 4-5 the plates and the ring fading. The middle of the cell (his body) stays EMPTY. " + MAGIC + ".",
     row(5, 40, 50) + CENTER),
    ("p_skin", "被动「玉石之肤」：持续，6 帧循环", "view_buffs `tft_shiohyu_p_skin`（大表，跟随他，z 3；左右对称）", "38 × 48",
     "玉石之肤持续时：身体两侧各有两三片玉石晶片慢慢上下浮动，边上一闪一闪的白色高光；脚下一圈淡淡的石质光环。**身体位置留空**。**左右对称**，6 帧循环。",
     JA + ", " + RO,
     "A STONE SKIN AURA, 6 looping frames, " + LR + ": round " + HIM + ": two or three faceted jade plates floating on "
     "EACH side of him (mirrored), bobbing gently up and down, white glints winking on their edges; a faint stone-grey "
     "and jade ring on the ground under him (an ellipse 32 squares wide, 8 tall). The middle of the cell (his body) "
     "stays EMPTY. " + MAGIC + ".",
     row(6, 38, 48) + CENTER),
]
ICONS = [
    ("skill", "技能 1「玉拳连打」图标", "skill_icons[0] `asset/tft/icons/tft_shiohyu_skill`",
     ICON + ": a coral-orange dragon fist punching to the right with two fading jade afterimages of it behind, a "
               "four-pointed jade impact star where it lands."),
    ("skill2", "技能 2「震地」图标", "skill_icons[1] `asset/tft/icons/tft_shiohyu_skill2`",
     ICON + ": a coral-orange dragon fist smashing down into the ground, jade-glowing cracks radiating from it, "
               "rock chunks flying up to both sides."),
    ("ult", "大招「玉龙形态」图标", "skill_icons[2] `asset/tft/icons/tft_shiohyu_ult`",
     ICON + ": the head of a jade dragon (a teal brow, two curved gold horns, a small purple horn on the forehead, "
               "glowing orange eyes) roaring, jade light rays bursting behind it."),
]
BIG_FX = ["e_slam", "r", "r_jade", "r3_wave", "p", "p_skin"]
FLYING = ("r3_wave",)

GROUPS = [
    ("a_hit q_hit r1_hit r2_hit (claws, fists, blows)",
     ["tft7_dragongreen_base_e_hands_v2", "tft7_dragongreen_base_p_impact_flash01", "tft7_dragongreen_base_p_impacttero",
      "tft7_dragongreen_base_e_hand_flare"]),
    ("e_slam e_hit e_slow (the slam)",
     ["tft7_dragongreen_base_e_cracks_add_v02", "tft7_dragongreen_base_e_ring_shockwave",
      "tft7_dragongreen_base_e_pebbles_4x4", "tft7_dragongreen_base_e_impactpuffs_2x2"]),
    ("r r_jade p p_skin (jade form, stone skin)",
     ["tft7_dragongreen_base_r_third_attack_cast_glowring", "tft7_dragongreen_base_p_swirltext01",
      "tft7_dragongreen_base_leaf", "tft7_dragongreen_base_p_fireup"]),
    ("r3_wave r3_hit (the third blow's wave)",
     ["tft7_dragongreen_base_r_third_attack_cast_lightspikes", "tft7_dragongreen_base_r_third_attack_mis_lightline",
      "tft7_dragongreen_base_r_mis_groundcracks", "tft7_dragongreen_base_r_third_attack_mis_wake_tex"]),
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
    """Shi Oh Yu at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"石傲玉 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 石傲玉：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/shiohyu_design.png`："
      "侧身朝右、直立站着的玉石龙人武者：翡翠青绿的皮肤、浅玉色的大胡子、金边的深青胸甲、深紫水晶肩甲；青绿眉盔、两根金角、紫色额角、"
      "橙黄发光的眼睛；珊瑚橙的爪子；背后两片高高竖起的翅膀（深紫翼骨、金到玫瑰色的翼膜）；尾巴尖一片带刺的叶形尾鳍）。"
      f"石傲玉在游戏里是**高清**的（每个游戏格子里约 2.46×2.46 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/shiohyu_size.png`：石傲玉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里石傲玉自己的特效贴图（爪痕、砸地的裂缝和碎石、玉龙形态的光环、第三击的光刺和地裂）"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **石傲玉是玉龙，特效都是玉石的力量**：白芯的翡翠玉光、有棱角的玉石碎晶和尖晶、几点金色火星（他角和胸甲边的金色），"
      "砸地时灰褐色的碎石和尘土；不要火、不要紫色光、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或白色的芯，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**（玉石碎晶用自己最深的一档做暗面）。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：画在人身上和地上的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；"
      f"**沿直线打出去的画面（{'、'.join(FLYING)}）朝右、严格上下对称**（游戏会按方向转）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `shiohyu_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `shiohyu_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「龙爪三连」 | 左右爪交替挥，第三下更重 | `a_hit` |")
    a("| 被动「玉石之肤」 | 血量掉到一半以下时全身化作玉石，几秒内大幅减伤 | `p` · `p_skin` |")
    a("| 技能 1 =「玉拳连打」 | 冲到目标面前连打 4 拳 | `q_hit` |")
    a("| 技能 2 =「震地」 | 一拳砸地，周围敌人被震飞并减速 | `e_slam` · `e_hit` · `e_slow` |")
    a("| 大招 =「玉龙形态」 | 减伤、免控，接下来 3 次普攻：晕眩 / 真实伤害 / 直线玉石冲击波 + 晕眩 | `r` · `r_jade` · `r1_hit` · `r2_hit` · `r3_wave` · `r3_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("玉（白、薄荷、翡翠、深玉）", JADE), ("金（他角和胸甲边的颜色）", GOLD), ("碎石和尘土", ROCK)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `shiohyu_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `shiohyu_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `shiohyu_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `shiohyu_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_shiohyu_fx`（小的）和 `tft_shiohyu_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- r3_wave 是从他身前出发、指向目标的一条线（LineRangeProjectile，左端对着他身前）；e_slam 放在砸地点的地面上（不跟随）；"
      "r_jade、p_skin 是他身上的 caster buff（z 3）；r、p 是他身上的一下（z 4）。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="shiohyu_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/shiohyu_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_shiohyu.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "shiohyu_design.png"))
    shape = size_sheet(os.path.join(out, "design", "shiohyu_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"shiohyu_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"shiohyu_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
