#!/usr/bin/env python3
"""Build scuttle_fx_pack.zip: step 3 of the Scuttle Crab's sprite - Codex draws its effects and its three skill icons
(the tft heroes' way, pack_meepsie_fx.py's).

    python tools/lol/fx_ref_scuttlecrab.py            # the particle references -> C:/t/sc_work/fxref
    python tools/art/pack_scuttlecrab_fx.py [--no-zip] [--out DIR] [--only a_hit,r_burst --name scuttle_fx_redo_pack]

The pack (C:/t/sc_work/fx/scuttle_fx_pack, zipped into --out, default D:/TFM2-Workshop/scuttle_packs) holds PROMPTS.md
(also written to assets/source/scuttlecrab/PROMPTS_FX.md), design/scuttle_design.png (the approved idle at 4x on its own
squares), design/scuttle_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (Rek'Sai's burrow and unburrow, Sona's and Soraka's - grey shapes the game
tints, grouped by the effect they inform; TFT has no set-18 bin for the crab and League's river crab names none). The
effects are the views the kit binds (tools/kit/build_scuttlecrab.py, the user's picks 2026-11-01: support, plan A
「河道守护」): view_projectiles q_shrine (the shrine zone); view_effects a_hit, p_heal (tft.dll's Green Buff), e_burst
(tft.dll's shell burst), r_dig, r_burst, r_up; view_buffs q_haste, e_slow, e_shell. Plus the three skill icons.
Its colours: the teal-green of its shell with lime-yellow edges, river water, river-bank earth, the green of the heals.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the shrine, a zone's picture the game may turn half round, is symmetric top to bottom too.
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

TMP = "C:/t/sc_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "scuttlecrab", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "scuttlecrab", "hd")
NAME = "scuttle_fx_pack"
PPU = 80 / 30

SHELL = "#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548"   # its plated teal shell, lime-yellow edges
WATER = "#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80"   # river water
EARTH = "#F0DCB4, #C8A276, #9A7450, #6E4E34, #44301E"            # river-bank earth
LEAF = "#F6FFE4, #D4F794, #96DC5A, #58B034, #2E7A22, #184A16"    # the Green Buff's heal
SH = f"a teal shell ramp ({SHELL})"
WA = f"a river-water ramp ({WATER})"
EA = f"an earth ramp ({EARTH})"
LE = f"a leaf-green heal ramp ({LEAF})"
LEAD = RF.LEAD
LR = RF.LR
LRTB = ("SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square, about its centre (the game may "
        "turn it half round: it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell "
         "plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp "
         "blocky shapes; no fire, no lightning bolts, no smooth neon beams")
HIM = ("the crab sits in the middle, not drawn: about 45 squares wide and 30 tall, low on its legs, its teal shell "
       "domed over it, its stone face at the right, its two long antennae curving back over the shell")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark teal frame with little lime "
        "corners, a deep river-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「螃蟹舞」：踩中，4 帧", "view_effects `tft_scuttlecrab_a_hit`（跟随被打中的人，z 2；左右对称）", "18 × 14",
     "跳舞踩中身边的敌人：一下**河水溅开**，水花往两边飞，中间一颗**柠檬黄绿的小星闪光**。**左右对称**，4 帧。",
     WA + ", " + SH,
     "A SPLASHING STOMP, 4 frames, " + LR + ": 1 a white-cyan flash 5 squares across with a small lime-yellow "
     "four-point star in its middle; 2 a splash of river water bursting out to both sides, 14 squares across, droplets "
     "flying up and out (mirrored), the lime star at its brightest; 3 the droplets arcing outward and falling, a low "
     "ripple spreading; 4 the last droplets on each side. " + MAGIC + ".",
     row(4, 18, 14) + CENTER),
    ("p_heal", "被动「绿霸符」：给低血队友回血，5 帧", "view_effects `tft_scuttlecrab_p_heal`（tft.dll 在被治疗的人身上播，z 3；左右对称）",
     "26 × 34",
     "队友血量掉到 40% 以下时：脚下一圈**绿色的符文光环**亮起，绿色的叶子和光点**绕着身体两侧旋转往上飘**，头顶一下亮起一个"
     "**绿色小十字**。**人站的地方留空**。**左右对称**，5 帧。",
     LE + ", " + SH,
     "A GREEN BUFF HEAL, 5 frames, " + LR + ": round " + CHAMP + ": 1 a bright leaf-green rune ring flashing on the "
     "ground at its feet (an ellipse 22 squares wide, 6 tall); 2 small green leaves and lime motes swirling up both "
     "sides of the body (mirrored), the ring glowing; 3 the leaves at chest height, a small green PLUS sign (a heal "
     "cross, 5 squares) lighting above its head; 4 the leaves above its head, the cross bright, the ring fading; 5 the "
     "last motes drifting up. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(5, 26, 34) + CENTER),
    ("q_shrine", "技能 1「疾行神龛」：地上的加速神龛，6 帧循环", "view_projectiles `tft_scuttlecrab_q_shrine`（大表，神龛范围的画面，"
     "放在它脚下的地面上，游戏可能把它转半圈；左右上下都对称，z -1）", "96 × 30",
     "它脚下的地面上，**一圈河水做的神龛**：从斜上方看的椭圆，外圈一道打转的水流波纹，里面几圈一圈圈往外扩的涟漪，"
     "水面上一点点柠檬黄绿的亮光闪烁，像一个会发光的小水潭。**只画平平的地面，不要往上冒的东西**（游戏可能把它转半圈，往上的东西会倒过来）。"
     "**左右对称、上下也对称（以中心为准）**，6 帧循环。",
     WA + ", " + SH,
     "A RIVER SPEED SHRINE, 6 looping frames, " + LRTB + ": FLAT ON THE GROUND, seen from above at a slant: a big "
     "ellipse 90 squares wide and 26 tall centred in the cell - its rim a ring of swirling river water (a band 3 squares "
     "wide of white-cyan foam and blue water), inside it 2-3 thin concentric RIPPLE rings spreading outward from the "
     "centre, a few small lime-yellow glints twinkling on the water (placed mirror-symmetric); frames 1-6 the ripples "
     "moving outward one step and a new one starting at the centre, the rim's foam swirling, the glints twinkling in "
     "turn. NOTHING sticking up from the ground (no spouts, no rising motes). " + MAGIC + ".",
     row(6, 96, 30) + CENTER),
    ("q_haste", "技能 1「疾行神龛」：加速，6 帧循环", "view_buffs `tft_scuttlecrab_q_haste`（跟随被加速的队友，脚下，z 3；左右对称）",
     "26 × 10",
     "站在神龛里被加速的队友：脚边两侧**几道蓝白的水流速度线**往后飘，脚下一圈小涟漪，偶尔一点柠檬黄绿的亮光。很淡、只在脚下。"
     "**左右对称**，6 帧循环。",
     WA + ", " + SH,
     "RIVER HASTE, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): a small ripple ring "
     "under the feet (an ellipse 18 squares wide, 4 tall), on EACH side (mirrored) two short white-cyan water streaks "
     "flowing outward like speed lines, one tiny lime glint; frames 1-6 the streaks flowing out and fading, new ones "
     "starting at the feet, the ripple breathing (every frame left-right symmetric). Subtle. " + MAGIC + ".",
     row(6, 26, 10) + CENTER),
    ("e_shell", "技能 2「蟹壳护盾」：护盾，6 帧循环", "view_buffs `tft_scuttlecrab_e_shell`（跟随它，z 3；左右对称）", "54 × 40",
     "它缩壳得到护盾的时候：身上罩着**一层半透明的青绿色甲片护盾**（一片片六边形的甲片拼成的圆罩），罩子边缘柠檬黄绿亮边，"
     "上面偶尔一道亮光扫过。**只画罩子的边和几片甲片，它的身体位置留空**。**左右对称**，6 帧循环。",
     SH + ", " + WA,
     "A SHELL SHIELD, 6 looping frames, " + LR + ": round " + HIM + ": a dome-shaped shield over it, 52 squares wide "
     "and 38 tall, drawn as an OUTLINE of hexagonal teal shell plates (each plate's edge 1-2 squares, lime-yellow on "
     "its upper rim, the plates themselves left EMPTY so the crab shows through), a few small white glints on the dome; "
     "frames 1-6 a band of light sweeping across the plates from both sides to the top (mirrored), the rim breathing "
     "a square. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 54, 40) + CENTER),
    ("e_burst", "技能 2「蟹壳护盾」：蟹壳碎裂，5 帧", "view_effects `tft_scuttlecrab_e_burst`（大表，tft.dll 在它身上播，z 3；左右对称）",
     "70 × 44",
     "护盾被打光（或者时间到）时：罩子**一下炸开**，一片片青绿色带黄绿边的**甲片碎块往四周飞**，中间一圈河水溅开，"
     "落到地上成一圈水渍（让周围的敌人减速）。**它的身体位置留空**。**左右对称**，5 帧。",
     SH + ", " + WA,
     "THE SHELL BURSTS, 5 frames, " + LR + ": round " + HIM + ": 1 a white-cyan flash over its shell, cracks of light "
     "across a dome 52 squares wide; 2 the dome breaking into teal shell SHARDS (pointed plates 4-6 squares with lime "
     "edges) flying out to both sides and up (mirrored), a ring of river water splashing out low on the ground; 3 the "
     "shards further out, tumbling, the water ring 66 squares wide; 4 the shards falling at the cell's edges, droplets "
     "raining; 5 a few shards and a thin wet ring on the ground. The middle of the cell (its body) stays EMPTY. "
     + MAGIC + ".",
     row(5, 70, 44) + CENTER),
    ("e_slow", "技能 2「蟹壳护盾」：减速，6 帧循环", "view_buffs `tft_scuttlecrab_e_slow`（跟随被减速的人，脚下，z 3；左右对称）",
     "24 × 8",
     "被碎壳水花减速的人：脚下**一摊黏糊糊的河水**，几块小甲壳碎片粘在脚边，水滴一滴滴往下掉，像踩在泥水里走不动。很淡、只在脚下。"
     "**左右对称**，6 帧循环。",
     WA + ", " + SH,
     "WATERLOGGED, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): a dark wet puddle "
     "of river water round the ankle line (an ellipse 20 squares wide, 4 tall), on EACH side (mirrored) a small teal "
     "shell chip stuck in it and a drop falling; frames 1-6 the puddle rippling a square, the drops falling in turn "
     "(every frame left-right symmetric). Subtle. " + MAGIC + ".",
     row(6, 24, 8) + CENTER),
    ("r_dig", "大招「你挖得动吗？」：钻进地下，8 帧", "view_effects `tft_scuttlecrab_r_dig`（大表，跟随它，地面上，z -1；左右对称）",
     "60 × 26",
     "它钻进地下的这 2.5 秒：先是**泥土往两边翻飞**（它在往下挖），然后地上鼓起**一个土包**，土包顶上露出**两根柠檬黄绿的触角尖**"
     "一抖一抖，土包边上小土块轻轻滚落。**只在地面和低处**。**左右对称**，8 帧（1–2 挖土，3–8 土包，最后一帧和第 3 帧接得上）。",
     EA + ", " + SH,
     "DIGGING IN, 8 frames, " + LR + ": on the GROUND and low above it, seen from above at a slant: 1 clods of earth "
     "and pebbles flung up to both sides (mirrored) from a hole 30 squares wide; 2 more earth flying, the hole filling; "
     "3 a round EARTH MOUND 34 squares wide and 12 tall, two short LIME-YELLOW ANTENNA TIPS (hooked, 1 square wide, 4 "
     "tall) poking out of its top side by side; 4-8 the mound breathing a square up and down, the antenna tips "
     "twitching (mirrored), small clods rolling down both sides in turn (frame 8 runs on into frame 3). " + MAGIC + ".",
     row(8, 60, 26) + CENTER),
    ("r_burst", "大招「你挖得动吗？」：钻出地面，6 帧", "view_effects `tft_scuttlecrab_r_burst`（大表，跟随它，z 3；左右对称）",
     "84 × 48",
     "它从地下钻出来的一下：土包**一下炸开**，泥土、石块和草皮往上往四周飞，地上一圈尘土冲击环扩开（把身边的敌人击飞），"
     "空中夹着几点河水和柠檬黄绿的亮光。**它的身体位置留空**。**左右对称**，6 帧。",
     EA + ", " + WA + ", " + SH,
     "BURSTING OUT, 6 frames, " + LR + ": round " + HIM + ": 1 a bright flash at the middle bottom and a ring of cracks "
     "in the ground 30 squares wide; 2 EARTH ERUPTING - clods, pebbles and dirt shooting UP and out on both sides "
     "(mirrored) to the cell's top, a ring of dust bursting open on the ground (an ellipse 50 squares wide, 14 tall), a "
     "few water droplets and lime glints among the earth; 3 the clods at their highest, the dust ring 76 squares wide; "
     "4 the clods falling, the ring thinning at the cell's edge; 5 the settling dust and a few pebbles; 6 the last "
     "specks. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 84, 48) + CENTER),
    ("r_up", "大招「你挖得动吗？」：被击飞，5 帧", "view_effects `tft_scuttlecrab_r_up`（跟随被击飞的人，z 3；左右对称）", "22 × 28",
     "被钻出来的螃蟹顶飞的人：脚下**一下土块和尘土冲上来**，两边几块小石头往上飞。**人站的地方留空**。**左右对称**，5 帧。",
     EA + ", " + WA,
     "AN EARTHEN KNOCK-UP, 5 frames, " + LR + ": round " + CHAMP + ": 1 a puff of earth shooting up under its feet; 2 "
     "dirt clods and small pebbles flying up both sides of its legs (mirrored), a dust streak up each side; 3 the clods "
     "at its chest, the dust high; 4 the clods above its shoulders, falling back; 5 the last pebbles and settling "
     "dust. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(5, 22, 28) + CENTER),
]
ICONS = [
    ("skill", "技能 1「疾行神龛」图标", "skill_icons[0] `asset/tft/icons/tft_scuttlecrab_skill`",
     ICON + ": a glowing ring of swirling river water seen from above at a slant, rippling, with two lime-yellow "
               "chevron arrows pointing right above it (speed)."),
    ("skill2", "技能 2「蟹壳护盾」图标", "skill_icons[1] `asset/tft/icons/tft_scuttlecrab_skill2`",
     ICON + ": a round teal crab shell of overlapping plates with lime-yellow edges, wrapped in a bright hexagonal shield "
               "outline, a few shell shards breaking off at its side."),
    ("ult", "大招「你挖得动吗？」图标", "skill_icons[2] `asset/tft/icons/tft_scuttlecrab_ult`",
     ICON + ": a brown earth mound bursting open, clods and pebbles flying up, two lime-yellow hooked crab antenna tips "
               "and the top of a teal shell popping out of it."),
]
BIG_FX = ["q_shrine", "e_burst", "r_dig", "r_burst"]
FLYING = ()
BOTH = ("q_shrine",)

GROUPS = [
    ("a_hit e_slow (the splash, the wet ground)",
     ["reksai_base_burrowed_q_hit_tar", "reksai_base_burrowed_q_splash_tar", "akali_base_z_flash_01",
      "reksai_base_burrowed_q_tar_dust"]),
    ("q_shrine q_haste (the speed shrine)",
     ["sona_base_q_area_circle", "sona_base_q_impactwave", "seraphine_base_e_wave_alphablend", "sona_base_r_motes",
      "sona_base_z_lightgradient"]),
    ("p_heal e_shell e_burst (the heal, the shell)",
     ["soraka_heal_sparkle", "bigglow02", "3026_items_ball32_02", "reksai_base_burrowed_w_fin_debris"]),
    ("r_dig r_burst r_up (the burrow)",
     ["reksai_base_w_ground_hole", "reksai_base_burrowed_q_ground_hole_02", "reksai_base_burrowed_q_tar_crown_dirt",
      "reksai_base_burrowed_q_ground_clump", "reksai_base_burrowed_w_knock_up_ring", "reksai_base_burrowed_w_tremor_ring",
      "reksai_base_r_end_dust", "reksai_base_t_rock"]),
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
    """The crab at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"迅捷蟹 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 迅捷蟹：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/scuttle_design.png`："
      "3/4 朝右、背着青绿色叠片甲壳的河蟹：甲片边缘柠檬黄绿、后沿一排尖刺；正前方灰色石头面甲、两只发光的柠檬黄绿眼睛；"
      "两根一节一节的长触角往后弯；甲壳下面一圈深青色尖叶形的短腿和小钳子）。"
      f"迅捷蟹在游戏里是**高清**的（每个游戏格子里约 2.7×2.7 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/scuttle_size.png`：迅捷蟹缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是雷克塞（钻地、钻出击飞）、娑娜（加速）、索拉卡（治疗）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **迅捷蟹是河道里的螃蟹，特效都是它的味道**：溅开的河水和涟漪、青绿色带黄绿边的甲片、"
      "河岸的泥土和小石子（大招是钻地）、治疗用叶子的嫩绿色光；不要火焰、不要闪电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；地上的神龛 `q_shrine` **左右、上下都对称**"
      "（游戏可能把它转半圈）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `scuttle_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `scuttle_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「螃蟹舞」 | 跳一段舞，踩中身边一圈的敌人 | `a_hit` |")
    a("| 被动「绿霸符」 | 身边的队友掉到 40% 血以下时回一大口血（每人 10 秒一次） | `p_heal` |")
    a("| 技能 1 =「疾行神龛」 | 脚下放一个河水神龛，水花溅伤身边的敌人；队友站在里面移动和攻击变快 | `q_shrine` · `q_haste` |")
    a("| 技能 2 =「蟹壳护盾」 | 缩进壳里得到护盾；护盾打光时蟹壳炸开，伤害、减速、短暂眩晕身边的敌人 | `e_shell` · `e_burst` · `e_slow` |")
    a("| 大招 =「你挖得动吗？」 | 钻进地下大幅减伤、持续回血，然后钻出来把身边的敌人击飞 | `r_dig` · `r_burst` · `r_up` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("甲壳青绿（黄绿边）", SHELL), ("河水", WATER), ("泥土", EARTH), ("叶绿（治疗）", LEAF)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `scuttle_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `scuttle_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `scuttle_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `scuttle_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_scuttlecrab_fx`（小的）和 `tft_scuttlecrab_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- q_shrine 断言左右上下都对称（神龛范围的画面，会随方向转），其余断言左右对称。")
    a("- q_shrine 是神龛范围（RangePeriodProjectile）的画面，在它脚下的地面上（z -1）；r_dig 是它身上的 caster 画面（跟随、地面 z -1，"
      "整段钻地 2.5 秒，第 3–8 帧循环）；r_burst 是钻出那一拍的 caster 画面；e_burst、p_heal 是 tft.dll 播的（蟹壳碎、绿霸符）；"
      "a_hit、r_up 是打中的画面；q_haste 是队友身上的 buff，e_slow 是敌人身上的 buff，e_shell 是它自己身上的 buff。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="scuttle_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/scuttle_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_scuttlecrab.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "scuttle_design.png"))
    shape = size_sheet(os.path.join(out, "design", "scuttle_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "left-right and top-bottom" if name in BOTH else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"scuttle_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"scuttle_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
