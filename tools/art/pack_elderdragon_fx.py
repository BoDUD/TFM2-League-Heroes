#!/usr/bin/env python3
"""Build elderdragon_fx_pack.zip: step 3 of the Elder Dragon's sprite - Codex draws its effects and its three skill
icons (the tft heroes' way).

    python tools/lol/fx_ref_elderdragon.py            # the particle references -> C:/t/ed_work/fxref
    python tools/art/pack_elderdragon_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name elderdragon_fx_redo_pack]

The pack (C:/t/ed_work/fx/elderdragon_fx_pack, zipped into --out, default D:/TFM2-Workshop/elderdragon_packs) holds
PROMPTS.md (also written to assets/source/elderdragon/PROMPTS_FX.md), design/elderdragon_design.png (the approved idle
at 4x on its own squares), design/elderdragon_size.png (it at game size, 4x, on the arena colour with the ground line, a
10-px ruler and the base fighter) and refs/tft_fx_ref.png (Smolder's dragon fire and Malphite's slam - grey shapes the
game tints, grouped by the effect they inform). The effects are the views the kit binds (tools/kit/build_elderdragon.py,
the user's picks 2026-11-01: top lane, plan A 「绝伦火热」): view_projectiles q_fire (tft.dll's breath); view_effects
a_hit, e_cast, r_slam; view_buffs a_splash, q_hit, ig, p_exec, e_slow, e_guard, r_stun, r_vamp. Plus the three skill
icons. Its colours: the cyan to near-white of its glowing mouth, eyes and crystal spikes (its dragonfire is cyan), the
dark purple of its wings, the white of its crystal mane.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying breath is symmetric top to bottom, pointing right.
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

TMP = "C:/t/ed_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "elderdragon", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "elderdragon", "hd")
NAME = "elderdragon_fx_pack"
PPU = 2.84

FIRE = "#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A"   # its dragonfire: its glowing mouth and crystals, cyan
WING = "#B9A6E8, #7A5CC2, #4E3590, #2E1F5C, #1A1236"           # its dark purple wings
MANE = "#FFFFFF, #E4E6EC, #B4B6C4, #7C7E92"                     # its white crystal mane
WIND = "#F2FBFF, #BFE8F5, #7FC4DE, #4A8DB0"                     # the wind of its wings
FI = f"a cyan dragonfire ramp ({FIRE})"
WI = f"a dark purple wing ramp ({WING})"
MA = f"a white crystal ramp ({MANE})"
WD = f"a pale wind ramp ({WIND})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy "
         "at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp "
         "blocky flame tongues; no lightning, no smooth neon beams, no runes")
HIM = ("the dragon stands in the middle, not drawn: about 59 squares wide and 44 tall, a four-legged winged dragon, its "
       "head low at the right, its wings raised over its back, its feet on the bottom line of the cell")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little cyan "
        "crystal corner studs, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art "
        "at 2 px a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「龙焰撕咬」：咬中，4 帧", "view_effects `tft_elderdragon_a_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "咬中：**上下两排青色的尖牙印**一合，中间一下青白色的火花，几点青色火星往两边崩开。**左右对称**，4 帧。",
     FI,
     "A BITE IMPACT, 4 frames, " + LR + ": 1 two rows of three pointed cyan FANG marks, one row above and one below, "
     "open, 12 squares wide; 2 the fang rows snapped shut in the middle, a near-white flash 6 squares across where they "
     "meet; 3 a cyan flame burst 14 squares across, small cyan sparks flying out to both sides (mirrored); 4 the last "
     "sparks and two thin teal wisps. " + MAGIC + ".",
     row(4, 18, 16) + CENTER),
    ("a_splash", "普攻「龙焰撕咬」：被溅到，4 帧", "view_buffs `tft_elderdragon_a_splash`（跟随被溅射的人，z 3；左右对称）",
     "12 × 12",
     "目标身边的人被溅到：一小团青色火星炸开。**左右对称**，4 帧。",
     FI,
     "A SPLASH OF SPARKS, 4 frames, " + LR + ": 1 a tiny near-white point; 2 a small cyan flame puff 7 squares across; "
     "3 four cyan sparks flying out (mirrored); 4 two sparks fading. " + MAGIC + ".",
     row(4, 12, 12) + CENTER),
    ("q_fire", "技能 1「烈焰吐息」：喷出去的龙焰，6 帧循环", "view_projectiles `tft_elderdragon_q_fire`（tft.dll 沿直线放出、"
     "穿透一路的敌人，随飞行方向旋转；上下对称、朝右）", "34 × 18",
     "它喷出去的龙焰：**一团往右冲的青色火焰**，前端是近白色的火头、往后变成亮青、再到深青色的火舌，火舌一条条往后甩开（像一团巨大的喷火头）。"
     "**上下对称、朝右**，6 帧循环（火舌翻滚）。",
     FI,
     "A ROARING BREATH OF DRAGONFIRE flying RIGHT, 6 looping frames, " + TB + ": a big rolling ball of cyan flame 16 "
     "squares long and 14 tall at the RIGHT end, its front a near-white hot core, behind it long cyan to teal FLAME "
     "TONGUES streaming back to the left (3 above the middle line and 3 below, mirrored), 34 squares in all, a few cyan "
     "crystal sparks inside; frames 1-6 the tongues rolling and flickering backward, the core pulsing. " + MAGIC + ".",
     row(6, 34, 18) + CENTER),
    ("q_hit", "技能 1「烈焰吐息」：被龙焰烧到，4 帧", "view_buffs `tft_elderdragon_q_hit`（跟随被烧到的人，z 3；左右对称）",
     "18 × 22",
     "被龙焰烧到：一下**青色火焰从脚下往上窜**、身体两侧各一条火舌，近白色的火芯，火星往上飘。**身体位置留空**。**左右对称**，4 帧。",
     FI,
     "A BURST OF DRAGONFIRE, 4 frames, " + LR + ": round " + CHAMP + " (only its feet line and its sides): 1 a flat "
     "near-white flash at its feet 10 squares wide; 2 cyan flames leaping up both its sides (mirrored), 18 squares tall, "
     "near-white cores; 3 the flames at their highest, sparks rising; 4 the flames sinking, two teal wisps. The middle of "
     "the cell (the body) stays EMPTY. " + MAGIC + ".",
     row(4, 18, 22) + CENTER),
    ("ig", "引燃：持续燃烧，6 帧循环", "view_buffs `tft_elderdragon_ig`（跟随被引燃的人，z 3；左右对称）", "22 × 30",
     "被【引燃】的人：**脚下和身体两侧一直有小小的青色火苗在烧**，火星往上飘。**身体位置留空**。**左右对称**，6 帧循环。",
     FI,
     "AN IGNITE, 6 looping frames, " + LR + ": round " + CHAMP + ": small cyan flames (3-6 squares tall) licking up "
     "along its feet line and up both its sides to its shoulders (mirrored), near-white tips, two or three cyan sparks "
     "drifting up; frames 1-6 the flames flickering and the sparks rising in turn. The middle of the cell (the body) "
     "stays EMPTY. " + MAGIC + ".",
     row(6, 22, 30) + CENTER),
    ("p_exec", "被动「远古巨龙霸符」：处决，6 帧", "view_buffs `tft_elderdragon_p_exec`（跟随被处决的人，z 4；左右对称）",
     "28 × 34",
     "被处决：**一只青色的巨龙之眼**在人身上猛地睁开，然后**一道青色龙焰柱从上往下砸穿**，火焰往两边炸开。**左右对称**，6 帧。",
     FI + ", " + WI,
     "AN EXECUTION, 6 frames, " + LR + ": round " + CHAMP + ": 1 a slit-pupil cyan DRAGON EYE 10 squares wide opening "
     "over its chest; 2 the eye wide, glowing; 3 a near-white pillar of cyan dragonfire crashing straight down through it "
     "from the top of the cell, 8 squares wide; 4 the pillar at its brightest, flames bursting out to both sides at the "
     "feet (mirrored); 5 the flames rolling out, the eye gone; 6 the last cyan wisps rising. " + MAGIC + ".",
     row(6, 28, 34) + CENTER),
    ("e_cast", "技能 2「龙翼风暴」：翅膀扇出的风暴，6 帧", "view_effects `tft_elderdragon_e_cast`（大表，跟随它，z 3；左右对称）",
     "96 × 40",
     "它两只翅膀猛地往下一拍：**一圈风浪从它身边贴着地面往两边扫开**，风里卷着青色的火星和紫色的碎羽。**它的身体位置留空**。**左右对称**，6 帧。",
     WD + ", " + FI + ", " + WI,
     "A WING STORM, 6 frames, " + LR + ": round " + HIM + ": 1 two pale wind arcs at its feet on both sides; 2 broad "
     "curling GUST WAVES (pale blue-white with cyan edges) rolling out low along the ground to both sides (mirrored), 70 "
     "squares wide, cyan sparks and dark purple wing scraps caught in them; 3 the waves 90 squares wide, thinner, curling "
     "over at their ends; 4 swirls of wind spinning at both ends; 5 the waves breaking into wisps; 6 the last wisps and "
     "sparks. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 96, 40) + CENTER),
    ("e_slow", "技能 2「龙翼风暴」：被风缠住减速，6 帧循环", "view_buffs `tft_elderdragon_e_slow`（跟随被减速的人，脚下，z 3；左右对称）",
     "20 × 8",
     "被减速的人脚下：**两圈淡蓝色的小旋风**绕着脚转。**左右对称**，6 帧循环。",
     WD,
     "A CLINGING GUST, 6 looping frames, " + LR + ": at a unit's feet: two flat pale blue-white wind loops 18 squares "
     "wide and 3 tall, one swirling each way (mirrored), a few tiny cyan specks; frames 1-6 the loops turning. " + MAGIC
     + ".",
     row(6, 20, 8) + CENTER),
    ("e_guard", "技能 2「龙翼风暴」：龙鳞护体（减伤），6 帧循环", "view_buffs `tft_elderdragon_e_guard`（大表，跟随它，z 3；左右对称）",
     "70 × 52",
     "它减伤的几秒：**身体轮廓外一圈青色的水晶鳞片光**一闪一闪，几片小水晶在身边绕。**它的身体位置留空**。**左右对称**，6 帧循环。",
     FI + ", " + MA,
     "A CRYSTAL SCALE GUARD, 6 looping frames, " + LR + ": round " + HIM + ": small pointed CYAN CRYSTAL SCALES (2-4 "
     "squares) set in a ring just outside its outline, glinting near-white one after another, two little white crystal "
     "shards orbiting on each side (mirrored); frames 1-6 the glints running round. The middle of the cell (its body) "
     "stays EMPTY. " + MAGIC + ".",
     row(6, 70, 52) + CENTER),
    ("r_slam", "大招「绝伦火热」：从天上砸落，8 帧", "view_effects `tft_elderdragon_r_slam`（大表，放在它落地的地方，不跟随，z -1；左右对称）",
     "130 × 44",
     "它从天上砸回地面：**地面一圈青色龙焰冲击波往四周扫开**（从斜上方看是扁扁的一个椭圆环），中间一下近白色的强光、地面裂开、碎石和青色火柱往上窜。"
     "**只在地面和低处**。**左右对称**，8 帧。",
     FI + ", " + WI,
     "A DRAGON'S SLAM, 8 frames, " + LR + ": on the GROUND seen from above at a slant: 1 a near-white flash 20 squares "
     "wide at the bottom middle; 2 a flat ELLIPSE RING of cyan dragonfire 60 squares wide and 14 tall rushing out, the "
     "ground cracked under it with glowing cyan seams; 3 the ring 100 squares wide, cyan flame pillars (6-14 squares "
     "tall) shooting up along it, rock chips flying (mirrored); 4 the ring 126 squares wide, the pillars at their highest; "
     "5-6 the ring thinning, the pillars falling into embers; 7 glowing cracks and drifting sparks; 8 the last cyan "
     "embers. " + MAGIC + ".",
     row(8, 130, 44) + CENTER),
    ("r_stun", "大招「绝伦火热」：被震晕，6 帧循环", "view_buffs `tft_elderdragon_r_stun`（跟随被晕的人，头顶上方，z 4；左右对称）",
     "16 × 8",
     "被晕眩的人头顶：**一圈青色的小火星**在转。**左右对称**，6 帧循环。",
     FI,
     "A DAZE, 6 looping frames, " + LR + ": above a unit's head: a flat ring 14 squares wide of four small cyan flame "
     "stars circling (mirrored); frames 1-6 the stars going round. " + MAGIC + ".",
     row(6, 16, 8) + CENTER),
    ("r_vamp", "大招「绝伦火热」：全能吸血，6 帧循环", "view_buffs `tft_elderdragon_r_vamp`（大表，跟随它，z 3；左右对称）",
     "76 × 56",
     "它全能吸血的几秒：**一缕缕青色的生命之火从四周往它身上流**，身体轮廓边上一圈青光一闪一闪。**它的身体位置留空**。**左右对称**，6 帧循环。",
     FI + ", " + WI,
     "A DRAGON'S HUNGER, 6 looping frames, " + LR + ": round " + HIM + ": thin streams of cyan life-fire curling in "
     "from the corners of the cell toward its outline (mirrored), small near-white motes riding them, a flickering cyan "
     "edge glow along its outline; frames 1-6 the streams flowing inward. The middle of the cell (its body) stays EMPTY. "
     + MAGIC + ".",
     row(6, 76, 56) + CENTER),
]
ICONS = [
    ("skill", "技能 1「烈焰吐息」图标", "skill_icons[0] `asset/tft/icons/tft_elderdragon_skill`",
     ICON + ": a dark dragon head with blue curved horns at the left, jaws wide open, a roaring stream of cyan dragonfire "
               "blasting out to the right, near-white at its core."),
    ("skill2", "技能 2「龙翼风暴」图标", "skill_icons[1] `asset/tft/icons/tft_elderdragon_skill2`",
     ICON + ": a huge dark purple bat wing with glowing cyan claw tips beating down, pale curling gust waves rushing out "
               "beneath it."),
    ("ult", "大招「绝伦火热」图标", "skill_icons[2] `asset/tft/icons/tft_elderdragon_ult`",
     ICON + ": a dark winged dragon diving down from the top with wings spread, a white crystal mane and a glowing cyan "
               "mouth, a ring of cyan dragonfire bursting on the ground below it."),
]
BIG_FX = ["e_cast", "e_guard", "r_slam", "r_vamp"]
FLYING = ("q_fire",)

GROUPS = [
    ("q_fire (the breath)",
     ["smolder_q_mis_lvl3_lead", "smolder_q_mis_firenoise_horiz", "smolder_r_generalfire_2x2", "smolder_base_4x4fire",
      "smolder_w_mis_firemask"]),
    ("a_hit a_splash q_hit ig p_exec (the bites and burns)",
     ["smolder_base_generichit", "smolder_base_ba_muzzle_flash", "smolder_base_sparks_2x2", "smolder_base_w_flamebits",
      "smolder_base_q_impactspike"]),
    ("e_cast e_slow e_guard (the wings' storm)",
     ["smolder_base_r_wave_edge", "smolder_q_aoe_waveout", "smolder_base_swirllead", "malphite_base_p_swoop",
      "smolder_base_thinring"]),
    ("r_slam r_stun r_vamp (the slam)",
     ["smolder_base_q_groundimpact", "smolder_r_ground_tell_v2", "malphite_base_z_furrow", "malphite_base_r_rock_debris",
      "smolder_base_healwisps"]),
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
    """The dragon at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"远古巨龙 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 远古巨龙：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/elderdragon_design.png`："
      "3/4 朝右、四条腿压低站着的翼龙：两只深紫色大蝙蝠翼半张开往上举，翼指尖是青色发光的爪尖；背上、尾巴上一排排青色水晶尖刺；"
      "白色晶体鬃毛盖住脖子和胸口；深色尖嘴、两只蓝色弯角、发青光的嘴、青色眼睛；尾巴往上卷）。"
      f"远古巨龙在游戏里是**高清**的（每个游戏格子里约 2.84×2.84 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/elderdragon_size.png`：远古巨龙缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是斯莫德（龙焰、吐息、火花、落地）和墨菲特（冲击、碎石）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **远古巨龙的龙焰是青色的**（和它发光的嘴、眼睛、水晶尖刺一样）：近白色的火芯、亮青色的火焰、边上深青到深蓝；"
      "**不要橙色的火**；少量深紫色（翅膀）、白色水晶；不要闪电、不要光滑的霓虹光束、不要符文。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**火焰、光、风没有黑描边**；水晶碎片可以有深色描边。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：喷出去的龙焰（`q_fire`）**上下对称、朝右**（游戏按飞行方向旋转它）；"
      "其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `elderdragon_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `elderdragon_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「龙焰撕咬」 | 咬目标，目标身边的敌人被溅射 | `a_hit` · `a_splash` |")
    a("| 被动「远古巨龙霸符」 | 对生命很低的敌方英雄造成伤害时直接处决 | `p_exec` |")
    a("| 技能 1 =「烈焰吐息」 | 朝穿过目标、敌人最多的直线喷青色龙焰，伤害逐个递减，并【引燃】 | `q_fire` · `q_hit` · `ig` |")
    a("| 技能 2 =「龙翼风暴」 | 立起身两翼猛拍，扇开身边的敌人并减速，自己减伤 | `e_cast` · `e_slow` · `e_guard` |")
    a("| 大招 =「绝伦火热」 | 无敌飞上天空再砸落：大范围晕眩并【引燃】，自己全能吸血，落地立刻再喷一口烈焰吐息 | "
      "`r_slam` · `r_stun` · `r_vamp` · `ig` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火焰、光、风没有黑描边，也不要用最深的颜色给形状描一圈边**（水晶碎片可以有深色描边）。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("青色龙焰（它的嘴、眼睛、水晶尖刺）", FIRE), ("深紫翅膀", WING),
                        ("白色水晶鬃毛", MANE), ("风", WIND)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的冲击波是从斜上方看的扁平椭圆。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `elderdragon_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `elderdragon_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `elderdragon_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `elderdragon_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_elderdragon_fx`（小的）和 `tft_elderdragon_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- q_fire 是 tft.dll 沿直线放出的穿透弹道；a_hit 在被咬的人身上；a_splash、q_hit、ig、p_exec 是 tft.dll 给敌人上的 buff；"
      "e_cast 跟随它；r_slam 放在它落地的地方（不跟随，z -1）；e_slow、r_stun 是数据给敌人的 buff；e_guard、r_vamp 是它身上的 buff。")
    a("- 用 `pixel_1x/` 切格（import_sentinel_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="elderdragon_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/elderdragon_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_elderdragon.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "elderdragon_design.png"))
    shape = size_sheet(os.path.join(out, "design", "elderdragon_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"elderdragon_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"elderdragon_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
