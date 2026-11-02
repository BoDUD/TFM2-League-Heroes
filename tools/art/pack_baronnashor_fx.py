#!/usr/bin/env python3
"""Build baronnashor_fx_pack.zip: step 3 of Baron Nashor's sprite - Codex draws its effects and its three skill icons
(the tft heroes' way).

    python tools/lol/fx_ref_baronnashor.py            # the particle references -> C:/t/bn_work/fxref
    python tools/art/pack_baronnashor_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name baronnashor_fx_redo_pack]

The pack (C:/t/bn_work/fx/baronnashor_fx_pack, zipped into --out, default D:/TFM2-Workshop/baronnashor_packs) holds
PROMPTS.md (also written to assets/source/baronnashor/PROMPTS_FX.md), design/baronnashor_design.png (the approved idle
at 4x on its own squares), design/baronnashor_size.png (it at game size, 4x, on the arena colour with the ground line, a
10-px ruler and the base fighter) and refs/tft_fx_ref.png (its own set-16 particle textures and the Rift Baron's - grey
shapes the game tints, grouped by the effect they inform). The effects are the views the kit binds (the user's pick
2026-11-03: jungle, plan A): view_effects a_hit, q_hit, e_burst, e_hit, r_spikes, r_hit, r_fall, p_tent;
view_projectiles q_spray; view_buffs q_acid. Plus the three skill icons.
Its colours: void violet-magenta (its rift, the tentacle, the spikes' glow), corrosive violet acid (TFT's own colour), earth and rock (the
burrow), ivory (its fangs).
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying spray is symmetric top to bottom, pointing right.
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

TMP = "C:/t/bn_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "baronnashor", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "baronnashor", "hd")
NAME = "baronnashor_fx_pack"
PPU = 2.04

VOID = "#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E"           # void light: the rift, the tentacle, the spikes' glow
ACID = "#FFEAFF, #EBA8FF, #B464F2, #7834C2, #3C1A72"           # corrosive acid: glossy violet, as TFT's own
ROCK = "#D8C8B4, #A08870, #6E5A4A, #47392F, #2A211C"           # earth and rock: the burrow, the debris
IVORY = "#FFF6DC, #F2D8A0, #C9A46E, #8A6A44"                   # its fangs and claws
VO = f"a void-violet ramp ({VOID})"
AC = f"a corrosive acid ramp ({ACID})"
RO = f"an earth and rock ramp ({ROCK})"
IV = f"an ivory ramp ({IVORY})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing "
         "VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH "
         "and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no "
         "leaves")
HIM = ("the serpent stands in the middle, not drawn: about 28 squares wide and 46 tall, a tall S-curved body on two "
       "short legs, its big crested head at the top")
CHAMP = "an upright champion 16 squares wide and 24 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little "
        "magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at "
        "2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「腐蚀撕咬」：咬中，4 帧", "view_effects `tft_baronnashor_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "一口咬中：**上下两排象牙白的尖牙形状一下合拢**，中间一下紫色冲击闪光，几滴紫色酸液往两边溅。**左右对称**，4 帧。",
     IV + ", " + VO + ", " + AC,
     "A VOID BITE, 4 frames, " + LR + ": 1 two rows of ivory FANG shapes, one at the top of the cell pointing down and "
     "one at the bottom pointing up, wide apart (each row 12 squares wide, four fangs); 2 the rows snapped together in "
     "the middle, a bright pale-pink and violet flash between them; 3 the fangs fading, a violet burst 14 squares "
     "across, a few glossy violet acid drops flying out to both sides (mirrored); 4 the last drops falling. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_spray", "技能 1「腐蚀吐息」：从嘴里喷出的一股酸液，4 帧循环",
     "view_projectiles `tft_baronnashor_q_spray`（大表，直线弹道，从嘴里喷出飞得很快，随飞行方向旋转；上下对称、朝右）",
     "48 × 22",
     "一股往前喷的酸液：**左边窄、右边张开的一团扇形酸雾**（往右喷），里面是亮紫色的酸液团和泡泡，边缘一圈紫色的虚空雾气，最前端几滴大酸滴。"
     "**上下对称、朝右**，4 帧循环（酸液团和泡泡往前滚）。",
     AC + ", " + VO,
     "A SPRAY OF CORROSIVE ACID, 4 looping frames, " + TB + ": a fan-shaped gush flying RIGHT - narrow at the left edge "
     "(6 squares tall), opening to 20 squares tall at the right; inside it blobs and bubbles of bright glossy violet acid "
     "with pale pink highlights, a thin haze of void violet along its top and bottom edges (mirrored), a few big acid "
     "drops leading at the right; frames 1-4 the blobs and bubbles rolling to the right. " + MAGIC + ".",
     row(4, 48, 22) + CENTER),
    ("q_hit", "技能 1「腐蚀吐息」：被酸液泼中，4 帧", "view_effects `tft_baronnashor_q_hit`（跟随目标，z 2；左右对称）", "18 × 18",
     "被酸液泼中：一团**亮紫色的酸液啪地溅开**，几滴往两边飞，冒起一缕淡紫色的腐蚀烟。**左右对称**，4 帧。",
     AC + ", " + VO,
     "AN ACID SPLASH, 4 frames, " + LR + ": 1 a glossy violet blob 6 squares across with a pale pink core; 2 the blob "
     "bursting into a splash 16 squares across, drops flying out to both sides (mirrored); 3 the drops falling, small "
     "bubbles, a thin violet hiss of smoke rising from the middle; 4 the last bubbles and smoke. " + MAGIC + ".",
     row(4, 18, 18) + CENTER),
    ("q_acid", "技能 1：被腐蚀（护甲魔抗降低），6 帧循环", "view_buffs `tft_baronnashor_q_acid`（跟随被腐蚀的人，z 3；左右对称）",
     "22 × 26",
     "被腐蚀的人：**身体两侧边缘几滴亮紫色酸液往下滴**，脚下一小滩冒泡的酸液，偶尔冒一缕淡紫色的烟。**身体位置留空**、很淡。**左右对称**，6 帧循环。",
     AC + ", " + VO,
     "CORROSION ON A UNIT, 6 looping frames, " + LR + ": round " + CHAMP + ": on EACH side (mirrored) along the body's "
     "edges two or three glossy violet acid DRIPS sliding down, a small bubbling acid puddle at the feet (an ellipse 18 "
     "squares wide, 3 tall) with bubbles popping, now and then a thin violet smoke wisp rising from the shoulders; "
     "frames 1-6 the drips falling and the bubbles popping in turn (every frame left-right symmetric). Subtle. The "
     "middle stays EMPTY (the unit). " + MAGIC + ".",
     row(6, 22, 26) + CENTER),
    ("e_burst", "技能 2「钻地突袭」：破土而出，6 帧",
     "view_effects `tft_baronnashor_e_burst`（大表，放在它冒出来的地面上，不跟随，z -1；画面最下面是地面；左右对称）",
     "60 × 40",
     "它从地里冲出来：**地面一圈裂开**（椭圆的裂缝，缝里透出紫色的虚空光），**土块和石头往上、往两边飞**，最后一圈尘土。"
     "**中间它的位置留空**。**左右对称**，6 帧。",
     RO + ", " + VO,
     "THE GROUND BURSTING OPEN, 6 frames, " + LR + ": the bottom of the cell is the ground, the serpent bursts up "
     "through the middle (not drawn): 1 a ring of CRACKS in the ground round the middle (an ellipse 30 squares wide, 8 "
     "tall), void-violet light glowing in the cracks; 2 the ground broken open, brown earth chunks and grey-brown rocks "
     "thrown up and out to both sides (mirrored), violet light bursting up from the cracks; 3 the rocks at their "
     "highest, a dust ring 50 squares wide on the ground; 4 the rocks falling, the dust rolling outward; 5 rubble on "
     "the ground round the middle, the cracks dimming; 6 the last dust. The middle above the ground stays EMPTY. "
     + MAGIC + ".",
     row(6, 60, 40) + CENTER),
    ("e_hit", "技能 2「钻地突袭」：被击飞，4 帧", "view_effects `tft_baronnashor_e_hit`（跟随目标，z 2；左右对称）", "18 × 20",
     "身边被击飞的人：脚下**一下紫色的冲击**，几块小石头往上蹦，一圈短短的往上的速度线。**左右对称**，4 帧。",
     VO + ", " + RO,
     "A KNOCK-UP HIT, 4 frames, " + LR + ": 1 a violet flash 8 squares across at the bottom middle; 2 a violet burst 14 "
     "squares across with a pale pink core, three short upward streaks on each side (mirrored), small rocks popping "
     "up; 3 the burst fading, the rocks at their highest; 4 the rocks falling, the last violet sparks. " + MAGIC + ".",
     row(4, 18, 20) + CENTER),
    ("r_spikes", "大招「虚空之怒」：一圈尖刺从地里刺出来，7 帧",
     "view_effects `tft_baronnashor_r_spikes`（大表，放在它脚下的地面上，不跟随，z -1；画面最下面是地面；左右对称）",
     "96 × 48",
     "它猛砸地面：**以它为中心的一大圈地面裂开**，**一圈尖锐的紫色虚空尖刺从地里刺出来**（里圈矮、外圈高，尖端洋红色发光），"
     "然后尖刺碎掉缩回地里，剩一圈裂缝和尘土。**中间它的位置留空**。**左右对称**，7 帧。",
     VO + ", " + RO,
     "A RING OF VOID SPIKES, 7 frames, " + LR + ": the bottom of the cell is the ground, round " + HIM + ": 1 a ring of "
     "glowing violet CRACKS spreading on the ground (an ellipse 80 squares wide, 22 tall); 2 sharp dark-violet SPIKES "
     "punching up out of the cracks all round the ring (each 3-4 squares wide at its base, 8-16 tall, pointing up, their "
     "tips bright magenta), the far ones smaller and higher in the cell, the near ones bigger and lower (mirrored); 3 "
     "the spikes at full height, magenta glow at their tips, earth chunks flying; 4 the spikes cracking; 5 the spikes "
     "shattering into violet shards and falling back; 6 a ring of rubble and glowing cracks; 7 the last dust and glow. "
     "The middle stays EMPTY (its body). " + MAGIC + ".",
     row(7, 96, 48) + CENTER),
    ("r_hit", "大招「虚空之怒」：被尖刺刺中，4 帧", "view_effects `tft_baronnashor_r_hit`（跟随目标，z 2；左右对称）", "18 × 22",
     "被尖刺刺中的人：**脚下一根紫色尖刺往上一刺**，一下洋红色闪光，几块碎片往两边飞。**左右对称**，4 帧。",
     VO + ", " + RO,
     "A SPIKE PIERCE, 4 frames, " + LR + ": 1 a small magenta flash at the bottom middle; 2 one sharp dark-violet SPIKE "
     "3 squares wide shooting straight up from the bottom, 16 squares tall, its tip bright magenta, a violet burst at its "
     "base; 3 the spike cracking, violet shards flying out to both sides (mirrored); 4 the last shards. " + MAGIC + ".",
     row(4, 18, 22) + CENTER),
    ("r_fall", "大招「虚空之怒」：一团酸液从天上落下溅开，7 帧",
     "view_effects `tft_baronnashor_r_fall`（大表，放在落点的地面上，不跟随，z 2；画面最下面是地面；左右对称）",
     "24 × 52",
     "一团酸液从天上落下来：**一团冒泡的亮紫色酸液球（外面一圈紫色雾气）从格子最上面直直落下来**，后面拖着几滴酸液，砸在格子最下面的地上，"
     "**啪地溅开一大滩冒泡的酸液**，一圈紫色的腐蚀烟。**左右对称**，7 帧。",
     AC + ", " + VO,
     "A FALLING ACID BALL, 7 frames, " + LR + ": the bottom of the cell is the ground: 1 a round bubbling ACID BALL 8 "
     "squares across (glossy violet, a pale pink highlight, a thin violet haze round it) at the very top of the cell, a "
     "few drops trailing above it; 2 the ball a third of the way down; 3 the ball two thirds down; 4 the ball hitting "
     "the ground at the bottom, a bright pale-pink splash flash; 5 a wide SPLASH of acid 20 squares across at the "
     "bottom, drops flying out low to both sides (mirrored); 6 a bubbling acid puddle on the ground (an ellipse 18 "
     "squares wide), violet smoke hissing up; 7 the puddle fading, the last smoke. " + MAGIC + ".",
     row(7, 24, 52) + CENTER),
    ("p_tent", "被动「虚空裂隙」：敌人脚下冒出一条虚空触手，7 帧",
     "view_effects `tft_baronnashor_p_tent`（大表，放在被选中的人脚下的地面上，不跟随，z 2；画面最下面是地面；左右对称）",
     "28 × 60",
     "一条虚空触手从地里冒出来把人顶飞：地面先**裂开一个透着紫光的小洞**，然后**一条粗壮的紫色触手（尖端洋红、表面一圈圈的环纹）笔直往上窜出来**，"
     "到最高后缩回洞里，洞口留一点紫光和碎土。触手**笔直朝上、左右对称**，7 帧。",
     VO + ", " + RO,
     "A VOID TENTACLE BURSTING UP, 7 frames, " + LR + ": the bottom of the cell is the ground: 1 a small hole cracking "
     "open at the bottom middle (an ellipse 12 squares wide, 4 tall), violet light inside it; 2 the tip of a thick "
     "TENTACLE pushing out of the hole, earth chunks flying to both sides (mirrored); 3 the tentacle shooting STRAIGHT "
     "UP, 6 squares thick at its base narrowing to a bright magenta tip, dark violet with lighter ring bands, 30 squares "
     "tall; 4 the tentacle at its full height 50 squares tall, its tip pointing straight up, a violet glow at the hole; "
     "5 the tentacle sinking back, 30 squares; 6 only its tip at the hole; 7 the hole closing, the last violet light and "
     "rubble. The tentacle stays upright and left-right symmetric in every frame. " + MAGIC + ".",
     row(7, 28, 60) + CENTER),
]
ICONS = [
    ("skill", "技能 1「腐蚀吐息」图标", "skill_icons[0] `asset/tft/icons/tft_baronnashor_skill`",
     ICON + ": a blue-violet serpent head with a yellow eye seen from the side, its jaws wide open with ivory fangs, a "
               "fan of bubbling glossy violet acid gushing out of its mouth to the right."),
    ("skill2", "技能 2「钻地突袭」图标", "skill_icons[1] `asset/tft/icons/tft_baronnashor_skill2`",
     ICON + ": purple crest fins with magenta tips cutting through broken brown earth, rocks flying up, a glowing "
               "violet crack beneath."),
    ("ult", "大招「虚空之怒」图标", "skill_icons[2] `asset/tft/icons/tft_baronnashor_ult`",
     ICON + ": a ring of sharp violet spikes with magenta tips bursting out of cracked ground, a big blue-violet "
               "serpent head roaring above them, glossy violet acid drops falling round it."),
]
BIG_FX = ["q_spray", "e_burst", "r_spikes", "r_fall", "p_tent"]
FLYING = ("q_spray",)

GROUPS = [
    ("a_hit e_hit r_hit (the bite, the knock-up, the spike)",
     ["tft16_baronnashor_base_baron_splash", "tft16_impactspike_01", "tft16_volibear_base_hit07", "flareburst",
      "tft15_leesin_base_shockwave_sharp"]),
    ("q_spray q_hit q_acid r_fall (the acid)",
     ["tft16_baronnashor_base_baron_splash_02", "tft16_baronnashor_base_baron_splash_03",
      "tft16_baronnashor_base_baron_splash_04", "tft16_baronnashor_base_r_honeywater", "malzahar_base_tar"]),
    ("e_burst (the burrow)",
     ["tft16_baronnashor_base_baron_cracks", "tft16_baronnashor_base_baron_burrow_hotedge",
      "tft16_baronnashor_base_baronnashor_rocks", "tft16_baronnashor_base_rock_debris",
      "tft16_baronnashor_base_p_ground_hole"]),
    ("r_spikes (the spike ring)",
     ["sru_baron_spikes", "tft16_baronnashor_base_baron_spikecracks", "tft16_baronnashor_base_ground_crack_fill",
      "naafiri_base_foundation_impactspike_2x2", "tft15_leesin_base_groundcracks"]),
    ("p_tent (the tentacle)",
     ["tft16_baronnashor_base_p_crack_dissolve", "tft16_baronnashor_base_p_dian", "tft16_baronnashor_base_p_rock_debris",
      "sru_baron_base_lightning_flipbook", "baron_base_tail_tx_cm"]),
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
    """Baron Nashor at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"纳什男爵 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 纳什男爵：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/baronnashor_design.png`："
      "3/4 朝右、虚空巨蛇：S 形紫色鳞甲身躯、正面青绿色分节腹甲；蓝紫硬甲头、黄色菱形大眼、红嘴白牙、象牙白獠牙；紫色鳍刺头冠、洋红鳍尖；"
      "两只小蛇头、两只象牙白大弯爪、两条紫色短腿）。"
      f"纳什男爵在游戏里是**高清**的（每个游戏格子里约 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/baronnashor_size.png`：纳什男爵缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是纳什男爵自己（金铲铲的钻地裂缝、石块、尖刺、酸液、触手）和召唤师峡谷纳什男爵的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **纳什男爵是虚空最大的巨兽，特效都是它的味道**：淡粉芯的**虚空紫 / 洋红**光、冒泡的**亮紫色腐蚀酸液**（金铲铲里它的酸液就是紫色的）、裂开的棕色**土地和飞石**、"
      "象牙白的尖牙形状；不要火、不要蓝色电光、不要树叶。")
    a("> - **特效要亮**：每个光都有最亮一档或淡粉色的芯，暗底上一眼能看见。**光、冲击环、尘土、酸液没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：除了飞行的酸液 `q_spray`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `baronnashor_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `baronnashor_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「虚空裂隙」 | 战斗中每隔几秒，在附近随机一名敌方英雄脚下喷出虚空触手，伤害并击飞 | `p_tent` |")
    a("| 普攻「腐蚀撕咬」 | 往前猛咬，咬到目标和它身后一条直线上的敌人 | `a_hit` |")
    a("| 技能 1 =「腐蚀吐息」 | 往前喷一扇形酸液：伤害，护甲和魔抗降低 | `q_spray` · `q_hit` · `q_acid` |")
    a("| 技能 2 =「钻地突袭」 | 钻进地里冲到目标脚下破土而出，伤害并击飞身边的敌人 | `e_burst` · `e_hit` |")
    a("| 大招 =「虚空之怒」 | 猛砸地面，一圈尖刺从地里刺出；然后连续吐出 10 团酸液落在附近的敌人身上 | "
      "`r_spikes` · `r_hit` · `r_fall` · `q_acid` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土、酸液没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（石块和尖刺可以有自己最暗一档的边）。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("虚空紫（裂隙、触手、尖刺的光）", VOID), ("腐蚀酸液", ACID), ("土地和石块", ROCK), ("象牙白（尖牙）", IVORY)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `baronnashor_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `baronnashor_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `baronnashor_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `baronnashor_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_baronnashor_fx`（小的）和 `tft_baronnashor_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- q_spray 断言上下对称（朝右），其余断言左右对称。")
    a("- e_burst、r_spikes 放在地面上（不跟随，z -1）；r_fall、p_tent 放在落点（不跟随，p_tent 由 tft.dll 播）；q_acid 是敌人身上的 buff；"
      "q_spray 是直线弹道（从嘴里喷出）。钻地时的 `dig` 帧（只露鳍刺）是精灵帧，不是特效。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="baronnashor_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/baronnashor_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_baronnashor.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "baronnashor_design.png"))
    shape = size_sheet(os.path.join(out, "design", "baronnashor_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"baronnashor_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"baronnashor_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
