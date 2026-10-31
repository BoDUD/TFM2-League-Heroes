#!/usr/bin/env python3
"""Build brambleback_fx_pack.zip: step 3 of the Crimson Brambleback's sprite - Codex draws its effects and its three
skill icons (the tft heroes' way).

    python tools/lol/fx_ref_brambleback.py            # the particle references -> C:/t/bb_work/fxref
    python tools/art/pack_brambleback_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name brambleback_fx_redo_pack]

The pack (C:/t/bb_work/fx/brambleback_fx_pack, zipped into --out, default D:/TFM2-Workshop/brambleback_packs) holds
PROMPTS.md (also written to assets/source/brambleback/PROMPTS_FX.md), design/brambleback_design.png (the approved idle
at 4x on its own squares), design/brambleback_size.png (it at game size, 4x, on the arena colour with the ground line,
a 10-px ruler and the base fighter) and refs/tft_fx_ref.png (the Rift's Red Brambleback's particle textures and
Warwick's, Brand's and Nasus's - grey shapes the game tints, grouped by the effect they inform). The effects are the
views the kit binds (tools/kit/build_brambleback.py, the user's picks 2026-10-31: jungle, plan A 「猩红之怒」):
view_effects a_hit, q_hit (also tft.dll's leap on to the next), e_cast, r_cast; view_buffs q_slow, e_slow, e_guard,
r_fury, p_burn (tft.dll's). Plus the three skill icons.
Its colours: the crimson-orange of its glowing veins, core and claws, its dark red-brown bark, its green leaves.
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

TMP = "C:/t/bb_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "brambleback", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "brambleback", "hd")
NAME = "brambleback_fx_pack"
PPU = 1.7

FIRE = "#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C"   # its glowing veins, red core and claws: the red buff
BARK = "#C9925C, #9B6741, #6E4430, #42271D, #24140F"            # its bark plates and branches
LEAF = "#B8DC6A, #72AE45, #3F7A36, #24492A"                     # its leaf collar
FI = f"a crimson fire ramp ({FIRE})"
BA = f"a bark ramp ({BARK})"
LE = f"a leaf ramp ({LEAF})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark "
         "reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; "
         "no lightning, no blue, no smooth neon beams")
HIM = ("the beast crouches in the middle, not drawn: about 61 squares wide and 40 tall, on all fours, its long arms and "
       "claws in front, its wedge head low at the right")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bark-brown frame with little "
        "red ember corners, a deep red-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 "
        "px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「荆爪横扫」：爪击，4 帧", "view_effects `tft_brambleback_a_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "大爪抓中：**三道红橙色的爪痕**（中间一道竖的，两边两道往外斜，像爪子从上往下抓过），一下火星和几片碎树皮往两边崩开。"
     "**左右对称**，4 帧。",
     FI + ", " + BA,
     "A CLAW RAKE, 4 frames, " + LR + ": 1 a small hot yellow-white flash 5 squares across; 2 THREE glowing red-orange CLAW "
     "MARKS raked from top to bottom, 12 squares tall - the middle one straight down, the two outer ones leaning outward "
     "(mirrored) - each 2 squares thick with a near-white core, a few embers flying out to both sides; 3 the marks "
     "fading to dark red from the top, small bark chips and embers falling outward; 4 the last faint marks and one "
     "falling ember on each side. " + MAGIC + ".",
     row(4, 18, 16) + CENTER),
    ("q_hit", "技能 1「荆棘飞扑」：扑落冲击，6 帧", "view_effects `tft_brambleback_q_hit`（跟随被扑中的人，z 3；左右对称；"
     "tft.dll 的「扑向下一个」落地时也用）", "40 × 24",
     "扑落砸中：被扑中的人脚下**一圈红橙色的冲击**（从斜上方看的扁椭圆），两边各三道爪痕往外划开，碎树皮、火星和几片绿叶往两边飞。"
     "**人站的地方留空**。**左右对称**，6 帧。",
     FI + ", " + BA + ", " + LE,
     "A POUNCE IMPACT, 6 frames, " + LR + ": round " + CHAMP + ", low on the ground at its feet: 1 a bright yellow-white "
     "flash at the feet, 10 squares wide; 2 a flat ring of red-orange impact (an ellipse 26 squares wide, 8 tall) and "
     "on EACH side three short glowing CLAW MARKS raking outward along the ground (mirrored); 3 the ring 36 squares wide, "
     "bark chips, embers and two or three GREEN LEAVES flying out to both sides; 4 the ring thinning, chips falling; "
     "5 the claw marks fading to dark red, a little dust; 6 the last embers. The middle (its body) stays EMPTY. "
     + MAGIC + ".",
     row(6, 40, 24) + CENTER),
    ("q_slow", "技能 1「荆棘飞扑」：减速，6 帧循环", "view_buffs `tft_brambleback_q_slow`（跟随被减速的人，脚下，z 3；左右对称）",
     "24 × 8",
     "被减速的人：脚边**几根带红刺的荆棘藤缠着脚踝**，藤上冒一点红光，像脚被荆棘绊住。很淡、只在脚下。**左右对称**，6 帧循环。",
     BA + ", " + LE + ", " + FI,
     "BRAMBLE SNARE, 6 looping frames, " + LR + ": low round a unit's feet only (the unit not drawn): on EACH side "
     "(mirrored) two thorny dark bark-brown BRAMBLE VINES curling round the ankle line, small red thorns on them, one tiny "
     "green leaf, a faint red glint; frames 1-6 the vines tightening and loosening a square and the glints moving "
     "(every frame left-right symmetric). Subtle. " + MAGIC + ".",
     row(6, 24, 8) + CENTER),
    ("e_cast", "技能 2「绯红咆哮」：怒吼声波，5 帧", "view_effects `tft_brambleback_e_cast`（大表，跟随它，z 3；左右对称）",
     "72 × 48",
     "它人立起来怒吼：身体两侧**一层层红色的声波弧线**往外推开（像括号一样的弧，左右各三层），被吹起的绿叶和火星往外飞。"
     "**它的身体位置留空**。**左右对称**，5 帧。",
     FI + ", " + LE,
     "A ROAR SHOCKWAVE, 5 frames, " + LR + ": round " + HIM + ": 1 a short red flash at the upper right and upper left "
     "edges (mirrored); 2 on EACH side two curved crimson SOUND-WAVE ARCS like big brackets, 3 squares thick, bright "
     "orange cores, pushed out from the body's edges; 3 three arcs on each side, the outer ones near the cell's edges, "
     "green leaves and embers blown outward; 4 the arcs fading to dark red and breaking into short dashes, leaves still "
     "flying; 5 the last dashes and two leaves at the edges. The middle of the cell (its body) stays EMPTY. "
     + MAGIC + ".",
     row(5, 72, 48) + CENTER),
    ("e_slow", "技能 2「绯红咆哮」：被吼得减速减攻，6 帧循环", "view_buffs `tft_brambleback_e_slow`（跟随被吼的人，头顶上方，z 3；"
     "左右对称）", "12 × 12",
     "被吼过的人头顶：**一个暗红色的三道爪痕印记**（圆形，里面三道往下的爪痕，表示被吓得变弱），一跳一跳地发光。**左右对称**，6 帧循环。",
     FI + ", " + BA,
     "A FEAR MARK, 6 looping frames, " + LR + ": above a unit's head: a round dark bark-brown disc 10 squares across with "
     "THREE glowing red CLAW SCRATCHES cut down through it (the middle straight, the outer two leaning out), a thin red "
     "ring round the disc; frames 1-6 the scratches pulsing brighter and dimmer and the disc bobbing one square up and "
     "down. " + MAGIC + ".",
     row(6, 12, 12) + CENTER),
    ("e_guard", "技能 2「绯红咆哮」：树皮护体（减伤），6 帧循环", "view_buffs `tft_brambleback_e_guard`（大表，跟随它，z 3；左右对称）",
     "74 × 50",
     "它减伤的时候：身子外面**一圈厚树皮甲片和带刺的荆棘藤**围成的护壳（横着的椭圆，只画外圈），甲片缝里透红光，几片绿叶挂在上面。"
     "**里面它的身体位置留空**。**左右对称**，6 帧循环。",
     BA + ", " + LE + ", " + FI,
     "A BARK AND BRAMBLE GUARD, 6 looping frames, " + LR + ": round " + HIM + ": a ring of THICK BARK PLATES and THORNY "
     "BRAMBLE VINES (a wide ellipse 70 squares wide and 46 tall, only its 3-square rim drawn), dark reddish-brown plates "
     "with glowing red seams, red thorns on the vines, a few green leaves on it; frames 1-6 the red seams lighting up in "
     "turn round the ring (mirrored pairs) and the thorns twitching (every frame left-right symmetric). INSIDE the ring "
     "stays EMPTY (its body). " + MAGIC + ".",
     row(6, 74, 50) + CENTER),
    ("r_cast", "大招「猩红之怒」：狂暴爆发，6 帧", "view_effects `tft_brambleback_r_cast`（大表，跟随它，z 3；左右对称）",
     "76 × 56",
     "它开大的一下：从它背上的红核和全身**猛地爆出一圈猩红的火焰**往上往外冲，火星四溅，地面上一圈火光。**它的身体位置留空**。"
     "**左右对称**，6 帧。",
     FI,
     "A CRIMSON FURY BURST, 6 frames, " + LR + ": round " + HIM + ": 1 a hot yellow-white flash at the top of its back "
     "(where its red core is); 2 a ring of crimson-orange FLAMES bursting up all round the body's edges, tallest at the "
     "top, a flat ring of fire light on the ground under it (an ellipse 60 squares wide, 10 tall); 3 the flames at their "
     "tallest (the top flames 14 squares tall), embers flying out to both sides (mirrored); 4 the flames sinking to the "
     "edges, embers rising; 5 small flames and the ground glow fading; 6 the last rising embers. The middle (its body) "
     "stays EMPTY. " + MAGIC + ".",
     row(6, 76, 56) + CENTER),
    ("r_fury", "大招「猩红之怒」：狂暴火焰，6 帧循环", "view_buffs `tft_brambleback_r_fury`（大表，跟随它，z 3；左右对称）",
     "70 × 54",
     "它狂暴期间：**猩红的火苗沿着身子两侧和背上往上舔**，一颗颗火星往上飘，像全身的红纹烧起来了。不要太满，只在身体边缘。"
     "**它的身体位置留空**。**左右对称**，6 帧循环。",
     FI,
     "A FURY BLAZE, 6 looping frames, " + LR + ": round " + HIM + ": small crimson-orange FLAME TONGUES licking up along "
     "the edges of its body - both sides and above its back (mirrored), each 4-8 squares tall with a yellow core - and "
     "single embers rising above it; frames 1-6 the flames flickering up and down in turn and the embers rising a few "
     "squares a frame (every frame left-right symmetric). Only at the body's edges, never over it. INSIDE stays EMPTY "
     "(its body). " + MAGIC + ".",
     row(6, 70, 54) + CENTER),
    ("p_burn", "被动「红霸符」：灼烧，6 帧循环", "view_buffs `tft_brambleback_p_burn`（跟随被烧的人，z 4；左右对称；tft.dll 给）",
     "20 × 26",
     "被红霸符烧着的人：身体两侧下半身**几簇小小的红橙火苗**往上窜，几颗火星往上飘（像英雄联盟里红 buff 的灼烧）。很小，不要盖住人。"
     "**人站的地方留空**。**左右对称**，6 帧循环。",
     FI,
     "A RED BUFF BURN, 6 looping frames, " + LR + ": round " + CHAMP + ": on EACH side of its lower body (mirrored) two "
     "small crimson-orange FLAME TONGUES 3-6 squares tall with yellow cores, and two or three single embers rising "
     "beside its body; frames 1-6 the flames flickering up and down in turn and the embers rising (every frame "
     "left-right symmetric). Small; the middle (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 20, 26) + CENTER),
]
ICONS = [
    ("skill", "技能 1「荆棘飞扑」图标", "skill_icons[0] `asset/tft/icons/tft_brambleback_skill`",
     ICON + ": a huge dark bark-brown arm with three big red-orange claws lunging down from the upper left toward the "
               "lower right, three glowing red claw streaks behind it, a few green leaves."),
    ("skill2", "技能 2「绯红咆哮」图标", "skill_icons[1] `asset/tft/icons/tft_brambleback_skill2`",
     ICON + ": the beast's wedge-shaped bark head roaring, seen from the side facing right, two red eyes, under a green "
               "leaf collar, three curved crimson sound-wave arcs coming out in front of it."),
    ("ult", "大招「猩红之怒」图标", "skill_icons[2] `asset/tft/icons/tft_brambleback_ult`",
     ICON + ": a big red-orange claw raised and wreathed in crimson flames, a glowing red-orange ember core behind it, "
               "embers flying up."),
]
BIG_FX = ["e_cast", "e_guard", "r_cast", "r_fury"]
FLYING = ()

GROUPS = [
    ("a_hit q_hit (the claw rakes)",
     ["sru_red_base_ba_swipe_mult_01", "sru_redbuff_ba1_swipe_pink", "warwick_base_q_slash", "warwick_base_q_biteswipe",
      "warwick_base_q_wolfmanclaw"]),
    ("e_cast e_slow q_slow (the roar, the bramble)",
     ["warwick_base_e_fearlines", "warwick_base_z_shockwave", "warwick_base_e_aura_self", "sru_redbuff_ba_leaves_2x2_pink",
      "nasus_base_w_wither_swirl"]),
    ("r_cast r_fury p_burn (the red buff's fire)",
     ["redbuff_glow", "sru_redbuff_centerglow", "brand_base_p_fire_mult", "brand_base_w_fireup", "sru_redbuff_sparks"]),
    ("e_guard r_cast (the guard, the burst)",
     ["nasus_base_r_transform_wave_swirl", "brand_base_flame_ring", "brand_base_w_ring_shockwave_2",
      "sru_redbuff_redtrail", "warwick_base_r_dustcloud"]),
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
    """The beast at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"树怪 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 绯红印记树怪：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/brambleback_design.png`："
      "3/4 朝右、四肢着地弓背蹲着的深红褐树皮巨兽：两条长前臂、三根红橙大爪；脖子上一圈绿叶领子；背上弯曲的深色树枝和发光的红橙核心；"
      "楔子形树皮脑袋低在领子下，两只红眼、额头橙色螺旋；树皮上发光的红色裂纹）。"
      f"树怪在游戏里是**高清**的（每个游戏格子里约 1.7×1.7 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/brambleback_size.png`：树怪缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是峡谷红 buff 自己（爪痕、红霸符的火光）、狼人（爪击、恐惧波纹）、布兰德（火焰）和内瑟斯（光环）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **树怪是峡谷的红 buff 野兽，特效都是它的味道**：猩红到橙色的火焰和火星、发光的红色爪痕、深红褐的碎树皮和带刺的荆棘藤、"
      "被扯下来的绿叶；不要闪电、不要蓝色、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个火光和爪痕都有最亮一档的黄白色芯，暗底上一眼能看见。**火焰、爪痕、冲击环没有黑描边**。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `brambleback_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `brambleback_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「荆爪横扫」 | 一只大爪举起往前往下横扫 | `a_hit` |")
    a("| 被动「红霸符」 | 普攻让目标灼烧（按最大生命的真实伤害），自己回血；杀了人自动扑向下一个敌人 | `p_burn` · `q_hit` |")
    a("| 技能 1 =「荆棘飞扑」 | 跃起扑到目标身上，物理伤害并减速 | `q_hit` · `q_slow` |")
    a("| 技能 2 =「绯红咆哮」 | 人立怒吼，周围敌人减速、攻击力降低，自己受到的伤害降低 | `e_cast` · `e_slow` · `e_guard` |")
    a("| 大招 =「猩红之怒」 | 全身红纹烧起来狂暴：攻击力、攻速大涨，无视一部分护甲 | `r_cast` · `r_fury` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("猩红火焰（它发光的红纹、红核和爪子）", FIRE), ("树皮（深红褐）", BARK), ("树叶", LEAF)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `brambleback_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `brambleback_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `brambleback_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `brambleback_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_brambleback_fx`（小的）和 `tft_brambleback_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- a_hit 跟随目标；q_hit 跟随被扑中的人（tft.dll 的「扑向下一个」落地时也用 play_view_effect 放它）；e_cast、r_cast 是它身上的 caster 画面；"
      "e_guard、r_fury 是它身上的 buff；q_slow、e_slow 是敌人身上的 buff；p_burn 是 tft.dll 给被烧的人挂的 buff。")
    a("- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="brambleback_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/brambleback_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_brambleback.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "brambleback_design.png"))
    shape = size_sheet(os.path.join(out, "design", "brambleback_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"brambleback_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"brambleback_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
