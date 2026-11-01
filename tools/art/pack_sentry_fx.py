#!/usr/bin/env python3
"""Build sentry_fx_pack.zip: step 3 of the Sentry's sprite - Codex draws its effects and its three skill icons (the tft
heroes' way).

    python tools/lol/fx_ref_sentry.py            # the particle references -> C:/t/pb_work/fxref
    python tools/art/pack_sentry_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name sentry_fx_redo_pack]

The pack (C:/t/pb_work/fx/sentry_fx_pack, zipped into --out, default D:/TFM2-Workshop/sentry_packs) holds PROMPTS.md
(also written to assets/source/sentry/PROMPTS_FX.md), design/sentry_design.png (the approved idle at 4x on its own
squares), design/sentry_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/tft_fx_ref.png (Viktor's beam and flare, the Rift's pebbles, Taliyah's stones, cracks and rings -
grey shapes the game tints, grouped by the effect they inform). The effects are the views the kit binds
(tools/kit/build_sentry.py, the user's picks 2026-11-02: bottom lane, plan A 「蔚蓝激光」): view_projectiles a_bolt,
q_zap, q_beam, r_sweep; view_effects a_hit, q_hit, e_split, e_ring, r_open, r_hit; view_buffs q_shred, e_slow,
r_shred (q_beam r_sweep e_ring r_open on the big sheet). Plus the three skill icons. Its colours: the azure of its core
and its laser, the pale sage of its upper rock, the navy of its lower rock.
Red side: every picture but the flying ones is symmetric left to right (the client never mirrors an effect picture);
a_bolt, q_zap and q_beam top to bottom, pointing right (turned with their flight); r_sweep is the one swept picture
(turned half round to the left it sweeps the other way up - fine).
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

TMP = "C:/t/pb_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "sentry", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "sentry", "hd")
NAME = "sentry_fx_pack"
PPU = 1.29

AZURE = "#F2FCFF, #9EEBFF, #3CC3FF, #1C7FE0, #10418C"        # its core, the laser, the bolts
SAGE = "#E4E9C8, #B4C2A6, #7E9488, #4E6670, #26343F"         # its pale upper rock, the shards
NAVY = "#6A80B8, #3A4A80, #252F58, #161B36"                  # its dark lower rock, the cracks
AZ = f"an azure light ramp ({AZURE})"
SG = f"a pale sage stone ramp ({SAGE})"
NV = f"a deep navy stone ramp ({NAVY})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a FLOATING CRYSTAL SENTRY's from the jungle's blue camp: crisp AZURE LIGHT with a near-white "
         "core (its glowing core and its laser), sharp little CRYSTAL SHARDS and stone chips in pale sage and deep "
         "navy; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smoke clouds, no runes or letters")
HIM = ("the sentry floats in the middle, not drawn: two crystal shards about 22 squares wide and 34 tall, their bottom "
       "points 2 squares above the bottom line of the cell, its glowing core 19 squares above the bottom line in the "
       "middle column")
UNIT = "a champion 16 squares wide and 36 tall stands in the middle, not drawn, its feet on the bottom line of the cell"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square deep navy frame with little pale "
        "sage stone corner studs, a dark blue-black inside, the symbol big and centred, lit from the upper left; pixel "
        "art at 2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_bolt", "普攻「碎光弹」：飞出去的蓝光弹，4 帧循环",
     "view_projectiles `tft_sentry_a_bolt`（追踪弹道，随飞行方向转；上下对称、朝右）", "10 × 6",
     "一颗**蔚蓝色的光弹**往右飞：前头一个菱形的亮芯（近白），后面拖一条变细的蓝光尾巴和两点小碎光。**上下对称、朝右**，4 帧循环（光芯一闪一闪）。",
     AZ,
     "A FLYING SHARD OF LIGHT, 4 looping frames, " + TB + ": a small diamond-shaped azure bolt 4 squares long at the "
     "right with a near-white core square, a tapering azure tail 5 squares long behind it to the left, two tiny sparks "
     "trailing; frames 1-4 the core pulsing and the sparks flickering. " + MAGIC + ".",
     row(4, 10, 6) + CENTER),
    ("q_zap", "技能 1「蔚蓝激光」：每一下打到人的小光点，4 帧循环",
     "view_projectiles `tft_sentry_q_zap`（很快的追踪弹道，几乎一出来就到；上下对称、朝右）", "6 × 6",
     "激光每一下伤害的小光点：**一颗很小的近白光点**外面一圈蔚蓝，四个方向各一格小光芒。**上下对称、朝右**，4 帧循环。",
     AZ,
     "A TINY ZAP, 4 looping frames, " + TB + ": a near-white dot 2 squares across in an azure ring, one-square glints "
     "up, down, left and right; frames 1-4 it pulsing. " + MAGIC + ".",
     row(4, 6, 6) + CENTER),
    ("q_beam", "技能 1「蔚蓝激光」：激光（一整条，Claude 切成每一帧），4 帧",
     "view_projectiles `tft_sentry_q_beam`（Claude 把每帧切成从蓝核射出的固定激光：league_velkoz R 的做法；上下对称；大图表）",
     "92 × 9",
     "技能 1 的激光：从它的蓝核射向前方的一整条细光束，**长 90 格**：近白的芯（1 格），外面亮蔚蓝，再外面一层深一点的蓝光边；"
     "光束里有一节一节往右流动的亮点；**左端是一个圆形的亮光（蓝核处的发射点，7 格）**，右端变细、散成几点碎光（参考 viktor_base_e_flare、"
     "viktor_base_q_lightning_thick、taliyah_base_e_beam_sandflow）。**横着画、上下对称**，4 帧循环（亮点往右流动、发射点一闪一闪）。",
     AZ,
     "A LONG AZURE LASER, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the "
     "game turns the picture with its direction): a straight horizontal beam 90 squares long from a round near-white "
     "and azure flare 7 squares across at the LEFT end (where it leaves the core); the beam 5 squares thick near the "
     "flare and 3 along its length - a near-white core 1 square, bright azure round it, a thin deeper blue edge; small "
     "bright beads of light running along it; the RIGHT end thinning to 1 square and breaking into azure sparks over its "
     "last 6 squares; each frame the beads move to the right and the flare pulses.",
     row(4, 92, 9) + "; the beam on the cell's middle row, the flare's middle 4 squares from the left edge."),
    ("r_sweep", "大招「棱镜扫射」：扫过去的粗光柱，6 帧",
     "view_projectiles `tft_sentry_r_sweep`（Claude 把每帧钉在蓝核上；朝右画，向左时游戏把它转半圈；大图表）", "100 × 70",
     "大招：从蓝核射出的**一道粗光柱，从右上方扫到右下方**。每帧一根光柱（长 90 格、粗 7 格：近白的芯 3 格、外面蔚蓝、最外一层深蓝光边），"
     "角度依次是 **上 30°、上 18°、上 6°、下 6°、下 18°、下 30°**，后面几帧留着前一根淡淡的残影；"
     "**所有光柱都从格子左边正中间的同一个点（蓝核，9 格的亮光）射出**。这一张**不用对称**。6 帧。",
     AZ,
     "A THICK PRISM BEAM SWEEPING DOWN, 6 frames (NOT symmetric: drawn pointing right, the game turns it): every beam "
     "leaves ONE point - a round near-white and azure flare 9 squares across centred on the cell's LEFT edge middle "
     "(5 squares in from the left edge, the middle row); each frame one straight thick beam 90 squares long and 7 thick "
     "(a near-white core 3 squares, bright azure round it, a deeper blue edge), its far end breaking into azure sparks, "
     "aimed in turn 30 degrees UP, 18 up, 6 up, 6 DOWN, 18 down, 30 down (frames 1-6) from that point; from frame 2 on a "
     "faint thin afterimage of the previous frame's beam. " + MAGIC + ".",
     row(6, 100, 70) + "; the flare in the same place in every cell."),
    ("a_hit", "普攻：光弹打中，4 帧", "view_effects `tft_sentry_a_hit`（跟随目标，z 2；左右对称）", "12 × 12",
     "光弹打中：**一圈蔚蓝色的小光爆**，中间近白，四周飞出几点碎光。**左右对称**，4 帧。",
     AZ,
     "A SMALL LIGHT BURST, 4 frames, " + LR + ": 1 a near-white dot 3 squares across; 2 an azure star burst 8 squares "
     "across with a white core; 3 a thin azure ring 11 squares across, four sparks flying out (mirrored); 4 the last "
     "sparks. " + MAGIC + ".",
     row(4, 12, 12) + CENTER),
    ("q_hit", "技能 1：激光烧在身上，4 帧", "view_effects `tft_sentry_q_hit`（跟随目标，z 2；左右对称；每 0.25 秒打一下）", "14 × 14",
     "激光照着的地方：**一团蔚蓝色的光斑**，中间近白，边上冒出几点往上飘的小光点，像被烧灼。**左右对称**，4 帧。",
     AZ,
     "A LASER BURN, 4 frames, " + LR + ": 1 a near-white spot 4 squares across in an azure glow 9 squares across; 2 the "
     "glow flaring to 12 squares, small azure flecks spitting out to both sides (mirrored); 3 the flecks rising, the "
     "glow shrinking; 4 a fading azure spot. " + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("e_split", "技能 2「裂石跃迁」：石头裂开的一闪，5 帧", "view_effects `tft_sentry_e_split`（跟随它，z 3；左右对称）",
     "40 × 40",
     "两块石头猛地分开的一下：**从它中间（蓝核处）往左右两边炸开一道蔚蓝色的裂光**，几片浅绿和深蓝的小石片往两边飞。**它的身体位置留空**。**左右对称**，5 帧。",
     AZ + ", " + SG,
     "A SPLITTING FLASH, 5 frames, " + LR + ": round " + HIM + ": 1 a near-white flash 6 squares across at the core's "
     "spot; 2 two azure crack-lines of light shooting out level from it to the left and right, 30 squares across in all; "
     "3 small pale sage and navy STONE CHIPS (1x1 to 2x2 squares) flying out to both sides (mirrored) along the lines; "
     "4 the lines fading, the chips falling; 5 the last chips. Keep the shards' place (the middle 22 squares wide, "
     "except the core's spot) EMPTY. " + MAGIC + ".",
     row(5, 40, 40) + CENTER),
    ("e_ring", "技能 2：原地留下的一圈碎石，6 帧",
     "view_effects `tft_sentry_e_ring`（大表，放在它原来的位置，不跟随，z -1；左右对称）", "50 × 18",
     "它跳走后原地留下的**一圈碎水晶**（站在里面的敌人被减速）：地上一圈插着的浅绿和深蓝小尖石，缝里透出蔚蓝的光，慢慢暗下去、碎石沉进地里。从斜上方看，扁一点。**左右对称**，6 帧。",
     SG + ", " + AZ,
     "A RING OF CRYSTAL SHARDS, 6 frames, " + LR + ": on the GROUND seen from above at a slant, centred on the bottom "
     "middle: 1 an azure flash ring 20 squares wide and 6 tall; 2 small pointed CRYSTAL SHARDS (pale sage tops, navy "
     "bases, 2-4 squares tall) bursting up in an oval ring 46 squares wide and 14 tall, azure light in the cracks between "
     "them; 3 the ring settled, the light glowing; 4 the light dimming; 5 the shards sinking into the ground; 6 a few "
     "last chips and a faint azure glint. " + MAGIC + ".",
     row(6, 50, 18) + CENTER),
    ("r_open", "大招「棱镜扫射」：蓝核蓄力，6 帧", "view_effects `tft_sentry_r_open`（大表，跟随它，z 3；左右对称）", "60 × 60",
     "两块石头张开、蓝核蓄力的一下：**四周的蔚蓝光线一道道往它的蓝核收拢**，蓝核外面一圈光环越来越亮，最后一帧亮到发白。**蓝核在格子正中那一列、离底边 19 格**。**它的身体位置留空**（蓝核那一点除外）。**左右对称**，6 帧。",
     AZ,
     "A CHARGING CORE, 6 frames, " + LR + ": round " + HIM + ": 1 eight thin azure light streaks far out round the core's "
     "spot, pointing at it (mirrored pairs); 2 the streaks closer; 3 the streaks reaching it, a thin azure ring 14 "
     "squares across round the core's spot; 4 the ring brighter, 10 squares; 5 the ring tight, 7 squares, near-white; "
     "6 a white-hot flash 9 squares across at the core's spot with four short glints. The shards' place round the core "
     "stays EMPTY. " + MAGIC + ".",
     row(6, 60, 60) + CENTER),
    ("r_hit", "大招：光柱扫中，5 帧", "view_effects `tft_sentry_r_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "粗光柱扫中：**一团亮到发白的蔚蓝光爆**，溅出几片小水晶碎光。**左右对称**，5 帧。",
     AZ + ", " + SG,
     "A BEAM BLAST HIT, 5 frames, " + LR + ": 1 a white flash 6 squares across; 2 an azure blast 14 squares across with a "
     "near-white core, small crystal glints thrown to both sides (mirrored); 3 the blast ringing out, thinner; 4 azure "
     "flecks drifting; 5 the last flecks. " + MAGIC + ".",
     row(5, 18, 16) + CENTER),
    ("q_shred", "技能 1：魔抗被削的裂纹印记，6 帧循环", "view_buffs `tft_sentry_q_shred`（跟随被照的人，z 3；左右对称）",
     "20 × 40",
     "被激光削了魔抗：**头顶上方一个蔚蓝色的小护盾符号裂开了**（一块六边形的蓝色小盾牌，中间一道裂缝，一明一暗地闪），身子两边飘下几点蓝色碎光。**身体位置留空**。**左右对称**，6 帧循环。",
     AZ + ", " + NV,
     "MAGIC RESIST BROKEN, 6 looping frames, " + LR + ": round " + UNIT + ": above its head, in the top middle of the "
     "cell, a small azure HEXAGON SHIELD 8 squares across with a jagged dark navy CRACK down its middle, near-white "
     "edges; a few azure flecks falling along both sides of its outline (mirrored); frames 1-6 the shield flickering "
     "bright and dim and the crack glinting, the flecks falling. The middle of the cell (its body) stays EMPTY. "
     + MAGIC + ".",
     row(6, 20, 40) + CENTER),
    ("e_slow", "技能 2：被碎石绊住减速，6 帧循环", "view_buffs `tft_sentry_e_slow`（跟随被减速的人，z 3；左右对称）", "24 × 10",
     "脚下被碎水晶绊住：**脚边一圈浅绿深蓝的小碎石**，缝里透着蓝光，偶尔一闪。**只在脚下**。**左右对称**，6 帧循环。",
     SG + ", " + AZ,
     "SLOWED BY SHARDS, 6 looping frames, " + LR + ": at the bottom of the cell round a unit's feet (the feet 8 squares "
     "apart in the middle, not drawn): a flat oval of small crystal shards and stone chips 22 squares wide and 4 tall "
     "(pale sage and navy), two little shards 3 squares tall poking up on each side (mirrored), azure light glinting "
     "between them; frames 1-6 the glints moving round. " + MAGIC + ".",
     row(6, 24, 10) + CENTER),
    ("r_shred", "大招：被光柱削魔抗，6 帧循环", "view_buffs `tft_sentry_r_shred`（跟随被扫中的人，z 3；左右对称）", "24 × 40",
     "被大招光柱扫中、魔抗大降：**身子两边各一道蔚蓝色的裂纹光**从下往上爬，头顶一个裂成两半的蓝色六边形护盾。**身体位置留空**。**左右对称**，6 帧循环。",
     AZ + ", " + NV,
     "MAGIC RESIST SHATTERED, 6 looping frames, " + LR + ": round " + UNIT + ": a jagged azure CRACK OF LIGHT climbing "
     "up each side of its outline (mirrored), near-white at its tip; above its head a navy and azure HEXAGON SHIELD 10 "
     "squares across split into two halves with a gap between them; frames 1-6 the cracks climbing and flickering, the "
     "halves trembling. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 24, 40) + CENTER),
]
ICONS = [
    ("skill", "技能 1「蔚蓝激光」图标", "skill_icons[0] `asset/tft/icons/tft_sentry_skill`",
     ICON + ": two tall crystal shards (pale sage tops, navy bottoms) at the lower left with a glowing azure core between "
               "them, a straight bright azure LASER with a white core shooting from the core to the upper right."),
    ("skill2", "技能 2「裂石跃迁」图标", "skill_icons[1] `asset/tft/icons/tft_sentry_skill2`",
     ICON + ": two crystal shards flung apart to the left and right with a glowing azure core between them, a ring of "
               "small crystal shards on the ground below, a short azure arrow curving back to the left."),
    ("ult", "大招「棱镜扫射」图标", "skill_icons[2] `asset/tft/icons/tft_sentry_ult`",
     ICON + ": two crystal shards opened wide into a V at the left, a white-hot azure core between them, a thick azure "
               "BEAM fanning out to the right with two faint afterimages above and below it (a sweep)."),
]
BIG_FX = ["q_beam", "r_sweep", "e_ring", "r_open"]
FLYING = ("a_bolt", "q_zap", "q_beam")

GROUPS = [
    ("a_bolt q_zap q_beam r_sweep (the bolt, the laser, the beam)",
     ["viktor_base_e_flare", "viktor_base_q_lightning_thick", "viktor_base_ba_glowalpha", "taliyah_base_e_beam_sandflow",
      "taliyah_lulu_base_z_glowflare"]),
    ("a_hit q_hit r_hit r_open (the bursts, the charge)",
     ["common_hiteffect", "taliyah_base_q_hit_ring", "taliyah_base_q_flash_cas", "viktor_base_w_setshine01",
      "taliyah_base_q_mis_glow"]),
    ("e_split e_ring e_slow (the shards)",
     ["common_sru_pebbles_4x4", "taliyah_base_e_rocks_2x2", "taliyah_base_e_stone_spike", "taliyah_base_r_rock_debris",
      "taliyah_base_e_shockwaveground"]),
    ("q_shred r_shred (the cracks)",
     ["taliyah_base_r_ground_crack", "taliyah_base_p_down_move_crack", "taliyah_base_w_indicator_cracks",
      "ice_shard_2"]),
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
    """The sentry at game size (2 px above the ground: it floats) next to the base fighter (4x), the ground line, a
    10-px ruler."""
    sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
    import tfm2_ase as T
    figs = [design_1x()]
    s = T.load_sprite("asset/base/aseprite_resources/champions/fighter")
    k = np.asarray(s.frames[s.tag("idle")["frm"]].convert("RGBA"))
    ky, kx = np.nonzero(k[..., 3] > 0)
    figs.append(k[ky.min():ky.max() + 1, kx.min():kx.max() + 1])
    lifts = [2, 0]
    Z, pad = 4, 6
    W = pad + sum(f.shape[1] + pad for f in figs)
    top = max(f.shape[0] + l for f, l in zip(figs, lifts))
    img = Image.new("RGBA", (max(W * Z, 560), (pad + top + 4) * Z + 64), (104, 112, 72, 255))
    base = pad + top
    x = pad
    for f, l in zip(figs, lifts):
        img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * Z, f.shape[0] * Z), Image.NEAREST),
                            (x * Z, (base - l - f.shape[0]) * Z + 64))
        x += f.shape[1] + pad
    d = ImageDraw.Draw(img)
    d.line([(0, base * Z + 64), (img.width, base * Z + 64)], fill=(220, 40, 40, 255), width=2)
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    for i in range(0, W, 10):
        xx = (pad + i) * Z
        d.line([(xx, 8), (xx, 30)], fill=(255, 255, 255, 255), width=2)
        d.text((xx + 3, 8), f"{i}", fill=(255, 255, 255, 255), font=font)
    d.text((8, 36), f"苍蓝哨戒 {figs[0].shape[1]}×{figs[0].shape[0]} 格（离地 2 格飘着），原版斗士 "
                    f"{figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）", fill=(255, 255, 255, 255), font=font)
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
    a("# 苍蓝哨戒：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定，见 `design/sentry_design.png`：")
    a(">   - 稍微 3/4 朝右、**两块漂浮的高瘦水晶石**，没有手脚、没有脸；")
    a(">   - 上半截浅灰绿岩面、下半截深海军蓝，底下收成尖；")
    a(">   - 中间一个圆孔，孔里一颗**发光的蔚蓝能量核**（激光和光弹都从这里射出）。")
    a(f">\n> 苍蓝哨戒在游戏里是**高清**的（每个游戏格子里约 {PPU}×{PPU} 个细像素），{h} 格高、{w} 格宽（高×宽），**离地约 2 格飘着**。"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/sentry_size.png`：苍蓝哨戒缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。**它的蓝核在离地约 19 格的地方**。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是维克托（光束、发射点的亮光）、峡谷的小石子、塔莉垭（石头、碎石、裂纹、光环）的特效贴图。"
      "这些是**灰色的形状，游戏里再染色**，已经按用在我们哪张特效分好了行。只在本地用。")
    a("> - **苍蓝哨戒是蓝 buff 营地里漂浮的水晶石，特效都是它的味道**：**蔚蓝色的光**（中间近白）、细细的**激光**和**光柱**、"
      "浅灰绿和深蓝的**小水晶碎片**。不要火、不要闪电、不要大团烟雾、不要文字和符文。")
    a("> - **特效要亮**：每个光都有最亮一档或近白的芯，暗底上一眼能看见。**光、光柱、光环没有黑描边**（碎石片可以有深色的边）。")
    a("> - **围着它的画面只画蓝核和身体周围，身体位置留空**，不要盖住它。")
    a(f"> - **对称**：飞行的三张（{'、'.join(FLYING)}）**上下对称、朝右**（游戏按飞行方向转）；`r_sweep`（扫射）**不用对称**；"
      "其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 交付方式：")
    a(">   - 每张生成后按格子取回（每格取多数颜色）。")
    a(">   - 交付 8 倍的 `sentry_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。")
    if n_ic:
        a(">   - 图标交付 `sentry_icon_<名字>.png`（64×64）。")
    a(">   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。")
    a(f">   - 都放在 `outputs/{NAME.replace('_pack', '')}/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。")
    a(">   - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「碎光弹」 | 蓝核里射出一颗小蓝光弹 | `a_bolt` · `a_hit` |")
    a("| 被动「青霸符」 | 引导激光每满 1 秒，大招冷却 -1 秒 | （没有图，只有声音） |")
    a("| 技能 1 =「蔚蓝激光」 | 对目标引导 2.5 秒激光，每 0.25 秒一下魔法伤害，削魔抗（可叠） | `q_beam` · `q_zap` · `q_hit` · `q_shred` |")
    a("| 技能 2 =「裂石跃迁」 | 两块石头一分一合往后闪开，原地留一圈碎石，周围敌人受伤减速 | `e_split` · `e_ring` · `e_slow` |")
    a("| 大招 =「棱镜扫射」 | 两块石头张成 V 字，蓝核蓄力射出粗光柱扫过前方扇形，伤害、大幅削魔抗 | "
      "`r_open` · `r_sweep` · `r_hit` · `r_shred` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、光柱、光环没有黑描边，也不要用最深的颜色给光描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("蔚蓝（蓝核、激光、光弹）", AZURE), ("浅灰绿（上半截岩面、水晶碎片）", SAGE),
                        ("深海军蓝（下半截岩面、裂纹）", NAVY)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中的画面居中画，不旋转；地上的一圈碎石是从斜上方看的扁平一圈。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `sentry_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `sentry_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `sentry_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `sentry_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_sentry_fx`（小的）和 `tft_sentry_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），r_sweep 不断言，其余断言左右对称。")
    a("- a_bolt 是普攻的追踪弹道，q_zap 是激光每一下的快速追踪弹（伤害在它身上），q_beam 是慢慢爬的追踪弹（league_velkoz R 的做法：切成每 tick 一帧、"
      "钉在蓝核上），r_sweep 是只有画面的直线弹（同样钉在蓝核上，kit 的 r_speed 改成 1000）；a_hit、q_hit、r_hit 在被打中的人身上；"
      "e_ring 放在地上（不跟随）；e_split、r_open 跟随它；q_shred、e_slow、r_shred 在敌人身上。")
    a("- 用 `pixel_1x/` 切格（import_velkoz_fx 的 beam_tag + import_gromp_fx 的做法，改成 import_sentry_fx）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="sentry_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/sentry_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_sentry.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "sentry_design.png"))
    shape = size_sheet(os.path.join(out, "design", "sentry_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: ("top-bottom (pointing right)" if name in FLYING else "none (swept, pointing right)"
                        if name == "r_sweep" else "left-right")
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"sentry_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"sentry_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
