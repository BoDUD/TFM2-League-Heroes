#!/usr/bin/env python3
"""Build syfen_fx_pack.zip: step 3 of Sy'fen's sprite - Codex draws his effects and his three skill icons
(the tft dragons' way).

    python tools/lol/fx_ref_syfen.py            # the particle references -> C:/t/sf_work/fxref
    python tools/art/pack_syfen_fx.py [--no-zip] [--out DIR] [--only a_hit,r_hit --name syfen_fx_redo_pack]

The pack (C:/t/sf_work/fx/syfen_fx_pack, zipped into --out, default D:/TFM2-Workshop/syfen_packs) holds PROMPTS.md
(also written to assets/source/syfen/PROMPTS_FX.md), design/syfen_design.png (the approved idle at 4x on its own
squares), design/syfen_size.png (him at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (his own set-7 particle textures - grey shapes the game tints, grouped by the
effect they inform). The effects are the views the kit binds (tools/kit/build_syfen.py, the user's picks 2026-10-30:
jungle, plan A 「暴走猎杀」): view_effects a_hit, q_bite, e_sweep, e_hit, r, r_dash, r_hit, r_bite, p; view_buffs
e_slow, p_shrink, p_rage. Plus the three skill icons.
His colours: violet and magenta with a white-pink core (his wing membranes, his head plate), the blue-violet of his
snout and back plates, the steel of his talons, grey-brown dust where he charges.
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

TMP = "C:/t/sf_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "syfen", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "syfen", "hd")
NAME = "syfen_fx_pack"
PPU = 2.52

VIOLET = "#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A"        # his wings and head plate: white-pink, pink, magenta, purple, deep violet
BLUE = "#E6EEFF, #8FA8FF, #4F5BEA, #2A2A9A"                       # the blue-violet of his snout and back plates
STEEL = "#F2F4FA, #B8C2D8, #7E8AA8, #4A5270"                      # his talons and his tail blade
DUST = "#E3DCCB, #B0A690, #7A705C, #4A4336"                       # dust where he charges
VI = f"a violet-magenta ramp ({VIOLET})"
BL = f"a blue-violet ramp ({BLUE})"
ST = f"a steel ramp ({STEEL})"
DU = f"a dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp "
         "crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no "
         "fire, no green, no smooth neon beams")
HIM = "the wyvern stands in the middle, not drawn: 52 squares wide and 40 tall, hunched, his head at the top right"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little "
        "magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 "
        "px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻：爪痕，4 帧", "view_effects `tft_syfen_a_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "翼爪 / 甩尾打中：两组交叉成 X 的品红爪痕（每组三条平行的细爪痕），中间一下粉白光，几缕紫色烟丝散开。**左右对称**，4 帧。",
     VI + ", " + ST,
     "A CLAW HIT, 4 frames, " + LR + ": 1 a white-pink flash 4 squares across; 2 two sets of three thin parallel "
     "magenta claw marks crossing in an X, 14 squares across, white-pink along their middles, a steel-blue glint at "
     "each end; 3 the marks fading from their ends, small violet wisps curling out symmetrically; 4 a few fading "
     "wisps. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("q_bite", "噬咬：一口咬下，5 帧", "view_effects `tft_syfen_q_bite`（跟随目标，z 3；左右对称）", "20 × 20",
     "咬中：上下两排**粉白色的獠牙虚影**从上下合拢咬在一起（像一张发光的龙嘴咬下去），合拢的一下品红光爆开，"
     "几滴紫色的光点往两边溅出。**左右对称**，5 帧。",
     VI + ", " + ST,
     "A BITE, 5 frames, " + LR + ": 1 two glowing jaw outlines open wide, an upper row of 5 white-pink fangs pointing "
     "down at the top and a lower row of 5 pointing up at the bottom, 18 squares wide; 2 the jaws snapping half shut; "
     "3 the fangs meeting in the middle with a bright magenta burst 12 squares across; 4 violet droplets of light "
     "splashing out to both sides (mirrored), the fangs fading; 5 a few fading sparks. " + MAGIC + ".",
     row(5, 20, 20) + CENTER),
    ("e_sweep", "翼刃横扫：两侧的翼刃弧光，6 帧", "view_effects `tft_syfen_e_sweep`（大表，跟随他，z 4；左右对称）", "64 × 36",
     "他张开翅膀往前合拢扫过：身体**两侧**各一道很大的品红月牙弧光（翼膜扫过的轨迹），从后上方往前下方扫过去，"
     "弧光边缘一排钢蓝色的爪尖闪光，弧光后面拖着紫色的烟。**身体位置留空**。**左右对称**，6 帧。",
     VI + ", " + ST,
     "A DOUBLE WING SWEEP, 6 frames, " + LR + ": round " + HIM + ": 1 two thin violet arcs appearing high on BOTH "
     "sides of him (mirrored); 2-3 each arc swelling into a big magenta crescent blade sweeping down and inward, 20 "
     "squares long, white-pink along its leading edge, a row of steel-blue talon glints on its rim; 4 the two crescents "
     "meeting low in front of and behind his feet; 5 the crescents breaking into trailing violet smoke; 6 a few wisps. "
     "The middle of the cell (his body) stays EMPTY. " + MAGIC + ".",
     row(6, 64, 36) + CENTER),
    ("e_hit", "翼刃横扫：被扫中，4 帧", "view_effects `tft_syfen_e_hit`（跟随被打中的人，z 2；左右对称）", "14 × 14",
     "被翼刃扫中：一道横着的品红斩痕，中间一下白光，两边几缕紫烟。**左右对称**，4 帧。",
     VI,
     "A WING SLASH HIT, 4 frames, " + LR + ": 1 a white-pink flash 4 squares across; 2 one HORIZONTAL magenta slash "
     "12 squares long through the middle, white-pink along its centre; 3 the slash splitting into small violet wisps "
     "curling out to both sides; 4 fading wisps. " + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("e_slow", "翼刃横扫：减速，6 帧循环", "view_buffs `tft_syfen_e_slow`（跟随被减速的人，脚下地面，z 3；左右对称）", "20 × 8",
     "被减速：脚下一圈紫色的烟雾缠着脚（从斜上方看的椭圆，宽是高的 3 倍），几缕烟丝像手一样往上抓。**左右对称**，6 帧循环。",
     VI,
     "A CLINGING SHADOW SNARE, 6 looping frames, " + LR + ": on the GROUND round the unit's feet, an ellipse seen "
     "from above, about 18 squares wide and 6 tall, of violet-purple smoke; a few thin wisps reaching up like small "
     "claws and sinking back; frames 1-6 the wisps rising and falling (keep every frame left-right symmetric). Nothing "
     "above the feet. " + MAGIC + ".",
     row(6, 20, 8) + CENTER),
    ("r", "暴走（开启）：龙吼音波，6 帧", "view_effects `tft_syfen_r`（大表，跟随他，z 4；左右对称）", "56 × 48",
     "他挺身咆哮的一下：从他身上往外**一圈圈扩散的品红音波环**（从斜上方看的椭圆，一圈比一圈大），脚下一圈紫色的警示光圈亮起，"
     "两侧几缕紫烟被吹开。**身体位置留空**（只画外面的环、脚下和两侧）。**左右对称**，6 帧。",
     VI + ", " + BL,
     "A ROAR OF SOUND WAVES, 6 frames, " + LR + ": round " + HIM + ": 1 a violet warning ring flashing on the ground "
     "under his feet (an ellipse 40 squares wide, 11 tall); 2-4 three concentric magenta SOUND-WAVE RINGS (ellipses, "
     "each 2 squares thick, white-pink on their front edge, blue-violet behind) bursting outward from him one after "
     "another, the outer one reaching the cell edge; violet smoke blown out to both sides; 5 the rings thinning; 6 the "
     "last ring fading. The middle of the cell (his body) stays EMPTY. " + MAGIC + ".",
     row(6, 56, 48) + CENTER),
    ("r_dash", "暴走冲锋：起步的尘土，4 帧", "view_effects `tft_syfen_r_dash`（冲锋开始时在他脚下的地面上，不跟随，z 1；左右对称）", "32 × 12",
     "他蹬地冲出去的一下：脚下的地面爆起一圈灰褐色的尘土和紫色的烟，往两边散开。**只在地面上**。**左右对称**，4 帧。",
     DU + ", " + VI,
     "A CHARGE KICK-OFF, 4 frames, " + LR + ": on the GROUND only (the bottom of the cell), an ellipse about 30 "
     "squares wide and 8 tall: 1 a small violet flash at the middle; 2 chunky grey-brown dust puffs and violet smoke "
     "bursting out to both sides (mirrored), up to 8 squares high; 3 the puffs spreading wider; 4 the dust settling. "
     + MAGIC + ".",
     row(4, 32, 12) + CENTER),
    ("r_hit", "暴走冲锋：被撞晕，5 帧", "view_effects `tft_syfen_r_hit`（跟随被撞到的人，z 3；左右对称）", "20 × 20",
     "被冲锋撞到：一下很亮的品红撞击闪光，一圈冲击环，几颗紫色的星星在头上绕（晕眩）。**左右对称**，5 帧。",
     VI + ", " + BL,
     "A RAMMED-AND-STUNNED IMPACT, 5 frames, " + LR + ": 1 a big white-pink flash 8 squares across in the middle; "
     "2 a thick magenta shock ring bursting out to 18 squares, violet shards flying out in a symmetric star; 3 the ring "
     "thinning; 4-5 three small violet stars circling in the top of the cell (a stun), the ring gone. " + MAGIC + ".",
     row(5, 20, 20) + CENTER),
    ("r_bite", "暴走猛咬：大咬，6 帧", "view_effects `tft_syfen_r_bite`（大表，跟随目标，z 4；左右对称）", "32 × 32",
     "暴走最后的一口：一张很大的**紫色幽影龙嘴虚影**（上下两排粉白獠牙）从上下猛地合拢咬住目标，咬合的一下品红光大爆炸，"
     "紫色的烟和光点往四周炸开。**左右对称**，6 帧。",
     VI + ", " + BL + ", " + ST,
     "A GREAT SHADOW BITE, 6 frames, " + LR + ": 1 a huge ghostly violet dragon's jaw outline opening wide around the "
     "middle, 30 squares wide, an upper row of 6 big white-pink fangs at the top and a lower row of 6 at the bottom; "
     "2 the jaws slamming half shut; 3 the fangs meeting with a big magenta explosion 20 squares across, a white-pink "
     "core; 4 violet smoke and sparks bursting out in a symmetric star; 5-6 the smoke fading. " + MAGIC + ".",
     row(6, 32, 32) + CENTER),
    ("p", "被动「幽影低语」：缩小，5 帧", "view_effects `tft_syfen_p`（跟随被缩小的人，z 3；左右对称）", "20 × 24",
     "敌人被缩小的一下：一圈紫色的低语烟丝从外往里**螺旋着收紧**到目标身上，几个往下的小箭头形光点，最后一下轻轻的粉光。"
     "**身体位置留空**。**左右对称**，5 帧。",
     VI,
     "A SHRINKING WHISPER, 5 frames, " + LR + ": round a unit 14 squares wide and 20 tall in the middle (not drawn): "
     "1 a ring of thin violet whisper wisps appearing at the cell edge; 2-3 the wisps spiralling INWARD and down toward "
     "the unit (mirrored), small downward-pointing chevrons of pink light on both sides; 4 the wisps tight round the "
     "unit's middle, a soft pink flash; 5 fading wisps. The middle of the cell stays EMPTY. " + MAGIC + ".",
     row(5, 20, 24) + CENTER),
    ("p_shrink", "被动「幽影低语」：缩小中，6 帧循环", "view_buffs `tft_syfen_p_shrink`（跟随被缩小的人，脚下地面，z 3；左右对称）", "18 × 8",
     "被缩小的人脚下：一个淡紫色的旋涡印记（从斜上方看的椭圆）慢慢转，几缕细烟往上飘一点。**左右对称**，6 帧循环（和减速的烟不一样：这是一个转动的符印）。",
     VI,
     "A WHISPER SIGIL, 6 looping frames, " + LR + ": on the GROUND round the unit's feet, an ellipse seen from above, "
     "about 16 squares wide and 6 tall: a thin violet ring with a small swirl sigil inside, its marks seeming to turn "
     "(keep every frame left-right symmetric), two or three thin wisps rising 2-3 squares and fading. Nothing above "
     "the feet. " + MAGIC + ".",
     row(6, 18, 8) + CENTER),
    ("p_rage", "被动「幽影低语」：越打越强，6 帧循环", "view_buffs `tft_syfen_p_rage`（大表，跟随他，z 3；左右对称）", "56 × 44",
     "他叠起力量时：身体**两侧**和两只利爪附近飘着紫色的火焰状烟丝，往上卷，脚下一圈淡淡的品红光。**身体位置留空**。**左右对称**，6 帧循环。",
     VI + ", " + BL,
     "A SHADOW FURY AURA, 6 looping frames, " + LR + ": round " + HIM + ": flame-like violet-magenta wisps curling "
     "upward along BOTH sides of him (mirrored) and at the outer edges low down where his talons are, white-pink tips "
     "on the brightest wisps; a faint magenta ring on the ground under him (an ellipse 40 squares wide, 10 tall); frames "
     "1-6 the wisps flickering upward (every frame left-right symmetric). The middle of the cell (his body) stays EMPTY. "
     + MAGIC + ".",
     row(6, 56, 44) + CENTER),
]
ICONS = [
    ("skill", "技能 1「噬咬」图标", "skill_icons[0] `asset/tft/icons/tft_syfen_skill`",
     ICON + ": a wyvern's long blue-violet snout with a magenta head plate seen from the side, its jaws snapping shut "
               "on a glowing magenta bite flash, rows of white fangs."),
    ("skill2", "技能 2「翼刃横扫」图标", "skill_icons[1] `asset/tft/icons/tft_syfen_skill2`",
     ICON + ": a purple-to-magenta bat-like wing with steel-blue talons sweeping across, a big magenta crescent arc "
               "trailing behind it."),
    ("ult", "大招「暴走」图标", "skill_icons[2] `asset/tft/icons/tft_syfen_ult`",
     ICON + ": the head of a shadow wyvern (a magenta head plate, two curved dark crimson horns, a glowing pink eye, "
               "open jaws with white fangs) charging to the right, violet speed streaks and smoke behind it."),
]
BIG_FX = ["e_sweep", "r", "r_bite", "p_rage"]
FLYING = ()

GROUPS = [
    ("a_hit e_hit (claws, slashes)",
     ["tft7_dragonpurple_base_r_hit_ray", "tft7_aphelios_base_emote_sion_base_emote_hit_circle_swipe", "hit_flash",
      "spark"]),
    ("q_bite r_bite (the bites)",
     ["tft7_dragonpurple_base_r_hit_explosion", "tft7_dragonpurple_base_r_hit_radial",
      "tft7_dragonpurple_base_r_hit_bits_tar", "chogath_base_q_spikeflakes"]),
    ("r r_hit (the roar's sound waves, the ram)",
     ["tft7_dragonpurple_base_r_cas_meshtex_sonicwaves", "tft7_dragonpurple_base_r_cas_ring",
      "tft7_dragonpurple_base_r_warning_zone_pow", "tft7_dragonpurple_base_shockwave"]),
    ("r_dash e_sweep (the charge, the sweep)",
     ["impactcloud", "tft7_dragonpurple_base_r_mis_trail", "tft7_dragonpurple_base_r_windswirl01",
      "morde_base_dust"]),
    ("p p_shrink p_rage e_slow (the whispers)",
     ["tft7_dragonpurple_base_ba_clouds", "tft7_dragonpurple_base_r_linger_rgba", "smoke_erode",
      "tft7_dragonpurple_base_firelight"]),
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
    """Sy'fen at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"赛芬 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 赛芬：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/syfen_design.png`："
      "侧身朝右、弓着身子直立的幽影飞龙：灰白皮肤、深青黑的横肋甲、宝蓝到紫色的背甲；品红头甲、蓝紫长嘴、白牙、两根暗红弯角、"
      "粉紫色发光的眼睛；两条浅灰长前臂就是翅膀（紫到品红的翼膜、钢蓝利爪）；长尾巴，尾尖一把钢灰弯刀刃）。"
      f"赛芬在游戏里是**高清**的（每个游戏格子里约 2.52×2.52 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/syfen_size.png`：赛芬缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里赛芬自己的特效贴图（打中的光、暴走的音波和警示圈、冲锋的拖尾、大爆炸、幽影龙的烟）"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **赛芬是幽影龙，特效都是幽影的力量**：粉白芯的紫色 / 品红烟丝和光、锐利的月牙斩痕、钢蓝色的爪尖闪光、"
      "冲锋时灰褐色的尘土；不要火、不要绿色、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或粉白色的芯，暗底上一眼能看见。**光、烟、冲击波、尘土没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `syfen_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `syfen_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「翼爪连击」 | 翼爪抓一下、甩尾抽一下，交替 | `a_hit` |")
    a("| 被动「幽影低语」 | 他的伤害让敌人缩小几秒（护甲、魔抗降低）；打缩小的敌人越打越强 | `p` · `p_shrink` · `p_rage` |")
    a("| 技能 1 =「噬咬」 | 扑上去狠咬一口，无视一部分护甲，回一点血 | `q_bite` |")
    a("| 技能 2 =「翼刃横扫」 | 张开翅膀往前合拢扫一大片，扫中的减速 | `e_sweep` · `e_hit` · `e_slow` |")
    a("| 大招 =「暴走」 | 龙吼，冲向最远的敌人，路上撞到的全部晕眩，冲到后再狠咬一口 | `r` · `r_dash` · `r_hit` · `r_bite` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("紫 / 品红（他的翼膜和头甲）", VIOLET), ("蓝紫（他的口鼻和背甲）", BLUE), ("钢蓝（利爪、尾刃）", STEEL),
                        ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `syfen_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `syfen_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `syfen_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `syfen_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_syfen_fx`（小的）和 `tft_syfen_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- e_sweep、r 是他身上的一下（跟随他，z 4）；p_rage 是他身上的 caster buff（z 3）；r_dash 放在冲锋起点的地面上（不跟随）；"
      "p_shrink、e_slow 是敌人身上的 buff（脚下，z 3）；q_bite、r_bite、r_hit、p 打在目标身上。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="syfen_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/syfen_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_syfen.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "syfen_design.png"))
    shape = size_sheet(os.path.join(out, "design", "syfen_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"syfen_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"syfen_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
