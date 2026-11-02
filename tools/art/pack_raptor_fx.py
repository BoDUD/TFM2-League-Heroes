#!/usr/bin/env python3
"""Build raptor_fx_pack.zip: step 3 of the Crimson Raptor's sprite - Codex draws its effects and its three skill
icons (the tft heroes' way).

    python tools/lol/fx_ref_raptor.py            # the particle references -> C:/t/rp_work/fxref
    python tools/art/pack_raptor_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name raptor_fx_redo_pack]

The pack (C:/t/rp_work/fx/raptor_fx_pack, zipped into --out, default D:/TFM2-Workshop/raptor_packs) holds PROMPTS.md
(also written to assets/source/raptor/PROMPTS_FX.md), design/raptor_design.png (the approved idle at 4x on its own
squares), design/raptor_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and the
base fighter) and refs/tft_fx_ref.png (Xayah's feathers and hits, Quinn's Valor and wind, Jarvan IV's - grey shapes the
game tints, grouped by the effect they inform). The effects are the views the kit binds (tools/kit/build_raptor.py, the
user's picks 2026-10-31: bottom lane, plan A 「鸟群之家」): view_projectiles a_bolt, q_feather (tft.dll's fan),
r_peck; view_effects a_hit, q_hit, r_peck_hit, e_jump; view_buffs p_shred, e_rush, r_flock. Plus the three skill icons.
Its colours: the crimson to orange-red of its back and tail feathers, the orange of its eyes and lit mouth, the purple
of its ruff, brown dust.
Red side: every picture on a unit or the ground is symmetric left to right (the client never mirrors an effect
picture); the flying feathers and pecks are symmetric top to bottom, pointing right.
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

TMP = "C:/t/rp_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "raptor", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "raptor", "hd")
NAME = "raptor_fx_pack"
PPU = 1.56

FEATHER = "#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26"       # its back and tail feathers, crimson to orange-red
GLOW = "#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A"          # its orange eyes and lit mouth; Orange Buff
RUFF = "#CDBDFF, #8E6CF0, #5B3FC0, #35227A, #1C1240"          # the purple spike ruff round its neck
DUST = "#E8D9BF, #BFA27A, #8A6A48, #523C2A"                   # the dust it kicks up
FE = f"a crimson feather ramp ({FEATHER})"
GL = f"an orange glow ramp ({GLOW})"
RU = f"a purple ruff ramp ({RUFF})"
DU = f"a dust ramp ({DUST})"
LEAD = RF.LEAD
LR = RF.LR
TB = ("SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; "
      "turned half round to the left it must read the same)")
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, "
         "hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; "
         "no magic runes, no lightning, no smooth neon beams")
HIM = ("the raptor stands in the middle, not drawn: about 49 squares wide and 36 tall, a round crouched bird, its head at "
       "the right, its tail feathers at the upper left, its feet on the bottom line of the cell")
CHAMP = "an upright champion 16 squares wide and 30 tall stands in the middle, not drawn"
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little orange "
        "corner studs, a deep wine-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a "
        "square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_bolt", "普攻「锋羽射击」：飞出去的羽毛，4 帧循环", "view_projectiles `tft_raptor_a_bolt`（随飞行方向旋转；上下对称、朝右）",
     "14 × 6",
     "它甩出去的一根羽毛：**一根尖尖的红色羽毛**横着往右飞，羽尖朝右、亮橙色的边，羽根后面拖一小段橙红色的拖尾。**上下对称、朝右**，4 帧循环。",
     FE + ", " + GL,
     "A FLYING FEATHER DART, 4 looping frames, " + TB + ": one sharp CRIMSON FEATHER lying along the flight, its "
     "pointed tip at the RIGHT, 9 squares long and 3 tall, a bright orange edge on both vanes (mirrored top and bottom), a "
     "darker red quill line along its middle, a short orange-red streak trailing off to the left (4 squares); frames 1-4 "
     "the trail flickering and one orange glint running along the edge. " + MAGIC + ".",
     row(4, 14, 6) + CENTER),
    ("a_hit", "普攻「锋羽射击」：羽毛命中，4 帧", "view_effects `tft_raptor_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "羽毛扎中：一下橙白色的小闪光，几片红色的碎羽往两边崩开。**左右对称**，4 帧。",
     GL + ", " + FE,
     "A FEATHER IMPACT, 4 frames, " + LR + ": 1 a small orange-white flash 4 squares across; 2 a sharp four-point "
     "orange star 10 squares across, four tiny red feather shards flying out to both sides (mirrored); 3 the shards "
     "spinning outward and down, two orange sparks; 4 one shard falling on each side. " + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("q_feather", "技能 1「羽刃扇射」：飞出去的羽刃，4 帧循环", "view_projectiles `tft_raptor_q_feather`（tft.dll 扇形放出的五根，"
     "随飞行方向旋转；上下对称、朝右）", "20 × 8",
     "羽刃：比普攻的羽毛**更大、更锋利的一片刀刃似的红羽**，边缘亮橙色像在发烫，后面拖一段带红羽碎片的拖尾。**上下对称、朝右**，4 帧循环。",
     FE + ", " + GL,
     "A FLYING BLADE FEATHER, 4 looping frames, " + TB + ": a big blade-like CRIMSON FEATHER along the flight, its "
     "point at the RIGHT, 13 squares long and 5 tall, both edges glowing hot orange to pale yellow (mirrored top and "
     "bottom), a dark red quill along its middle, behind it a 6-square streak of orange-red with two tiny feather flecks "
     "(one above, one below); frames 1-4 the edge glow pulsing and the flecks trailing. " + MAGIC + ".",
     row(4, 20, 8) + CENTER),
    ("q_hit", "技能 1「羽刃扇射」：羽刃划中，4 帧", "view_effects `tft_raptor_q_hit`（跟随目标，z 2；左右对称）", "18 × 16",
     "羽刃划中：**一个橙色的 X 形划痕**一闪，红色碎羽往两边飞。**左右对称**，4 帧。",
     GL + ", " + FE,
     "A BLADE SLASH IMPACT, 4 frames, " + LR + ": 1 a pale yellow flash 5 squares across; 2 a bright orange X of "
     "two crossed slash marks 14 squares across, near-white along their middles, red feather shards bursting to both "
     "sides (mirrored); 3 the X fading to red, the shards flying out and down; 4 the last red sparks and one falling "
     "shard on each side. " + MAGIC + ".",
     row(4, 18, 16) + CENTER),
    ("r_peck", "大招「鸟群之家」：小锋喙鸟扑啄，4 帧循环", "view_projectiles `tft_raptor_r_peck`（随飞行方向旋转；上下对称、朝右）",
     "12 × 6",
     "一只小锋喙鸟扑向敌人的残影：**一个小小的红色泪滴形身影**往右冲，最前面一个棕色的小尖喙，上下各一根紫色小尖羽，后面拖橙红色的速度线。"
     "**上下对称、朝右**，4 帧循环。",
     FE + ", " + RU + ", " + GL,
     "A DIVING CHICK STREAK, 4 looping frames, " + TB + ": a tiny crimson teardrop body 6 squares long and 4 tall "
     "rushing to the RIGHT, a small brown pointed beak at its right tip, one little purple spike feather above and one "
     "below (mirrored), a tiny orange eye glint on each side of its middle line, two thin orange-red speed lines "
     "trailing to the left; frames 1-4 the speed lines flickering. " + MAGIC + ".",
     row(4, 12, 6) + CENTER),
    ("r_peck_hit", "大招「鸟群之家」：小锋喙鸟啄中，4 帧", "view_effects `tft_raptor_r_peck_hit`（跟随目标，z 2；左右对称）",
     "12 × 12",
     "被小鸟啄中：一下小小的橙色啄击闪光，**几根红色、紫色的小绒毛**往两边飘。**左右对称**，4 帧。",
     GL + ", " + FE + ", " + RU,
     "A PECK, 4 frames, " + LR + ": 1 a tiny orange-white point; 2 a small orange three-ray peck flash 7 squares "
     "across; 3 four tiny fluff feathers (two red, two purple, mirrored) popping out to both sides; 4 the fluff drifting "
     "down. " + MAGIC + ".",
     row(4, 12, 12) + CENTER),
    ("e_jump", "技能 2「惊飞跃退」：起跳的尘土，5 帧", "view_effects `tft_raptor_e_jump`（放在它起跳的地面上，不跟随，z -1；左右对称）",
     "40 × 14",
     "它受惊往后一跳：起跳的地面上**一团尘土往两边扬起**，几片红羽飘下来。**只在地面和低处**。**左右对称**，5 帧。",
     DU + ", " + FE,
     "A TAKE-OFF PUFF, 5 frames, " + LR + ": on the GROUND and low above it: 1 a flat dust puff 12 squares wide at "
     "the bottom middle; 2 two dust clouds rolling out to both sides (mirrored), 30 squares wide, 8 tall, three red "
     "feathers popping up from the middle; 3 the clouds 38 squares wide and thinner, the feathers fluttering higher; "
     "4 the dust settling, the feathers drifting down on both sides; 5 the last wisps and one feather on each side. "
     + MAGIC + ".",
     row(5, 40, 14) + CENTER),
    ("e_rush", "技能 2「惊飞跃退」：攻速大涨，6 帧循环", "view_buffs `tft_raptor_e_rush`（跟随它，z 3；左右对称）", "56 × 40",
     "攻速大涨：它身子两侧**几道橙红色的速度线往后掠**，身子周围一闪一闪几点橙色火星，羽毛尖上一圈亮橙色。**它的身体位置留空**。"
     "**左右对称**，6 帧循环。",
     GL + ", " + FE,
     "A FRENZY RUSH, 6 looping frames, " + LR + ": round " + HIM + ": on EACH side of its body (mirrored) three "
     "short orange-red speed streaks sweeping up and outward along its edge, small orange sparks (1x1 and 2x2 squares) "
     "blinking round its outline, a thin bright orange flicker along the top edge; frames 1-6 the streaks sliding and "
     "the sparks blinking in turn (every frame left-right symmetric). The middle of the cell (its body) stays EMPTY. "
     + MAGIC + ".",
     row(6, 56, 40) + CENTER),
    ("p_shred", "被动「橙霸符」：破甲标记，6 帧循环", "view_buffs `tft_raptor_p_shred`（跟随被减甲的人，头顶上方，z 3；左右对称）",
     "12 × 12",
     "被减护甲的人头顶：**一块裂开的橙色小盾牌**（中间一道锯齿裂缝，裂缝里透着亮橙光），轻轻上下浮动、一闪一闪。**左右对称**，6 帧循环。",
     GL + ", " + FE,
     "A CRACKED ARMOUR MARK, 6 looping frames, " + LR + ": above a unit's head: a small orange heater SHIELD 8 "
     "squares wide and 10 tall, a jagged CRACK down its middle glowing pale yellow, a darker red rim, one tiny shard "
     "chipping off each side (mirrored); frames 1-6 it bobbing one square up and down, the crack's glow pulsing. "
     + MAGIC + ".",
     row(6, 12, 12) + CENTER),
    ("r_flock", "大招「鸟群之家」：围着它的四只小锋喙鸟，6 帧循环", "view_buffs `tft_raptor_r_flock`（大表，跟随它，z 3；左右对称）",
     "84 × 44",
     "鸟群之家：**四只小锋喙鸟**围在它身边——左右两边各有一只站在地上、一只在肩膀高度扑腾着飞。小鸟是它的缩小版、**正面朝着我们**："
     "红色圆滚滚的绒毛身子、头顶一撮紫色尖毛、棕色小尖喙、两只橙色小眼睛、小短腿；每只约 10×10 格。轮流上下蹦跳、扑腾小翅膀。"
     "**中间它的身体位置留空**。**左右对称**，6 帧循环。",
     FE + ", " + RU + ", " + GL + ", " + DU,
     "THE FLOCK, 6 looping frames, " + LR + ": round " + HIM + ": FOUR TINY BEAKS (baby raptors, each about 10 "
     "squares wide and 10 tall, seen FROM THE FRONT facing us so they read the same both ways: a round fluffy CRIMSON "
     "body, a little tuft of PURPLE spike feathers on top, a small brown pointed beak in the middle of the face, two tiny "
     "glowing ORANGE eyes, two stubby brown legs, two tiny red wings) placed mirrored: on EACH side one chick standing on "
     "the bottom line just outside its feet and one chick flapping in the air at its shoulder height just outside its "
     "outline; frames 1-6 the standing chicks hopping one square up and down in turn and the flying chicks flapping "
     "their wings (up, level, down), every frame left-right symmetric. The middle of the cell (its body) stays EMPTY. "
     + MAGIC + ".",
     row(6, 84, 44) + CENTER),
]
ICONS = [
    ("skill", "技能 1「羽刃扇射」图标", "skill_icons[0] `asset/tft/icons/tft_raptor_skill`",
     ICON + ": a fan of five sharp blade-like crimson feathers bursting out from the lower left to the upper right, "
               "their edges glowing hot orange, small orange sparks round them."),
    ("skill2", "技能 2「惊飞跃退」图标", "skill_icons[1] `asset/tft/icons/tft_raptor_skill2`",
     ICON + ": a round crimson raptor with a purple ruff hopping up and backward, its feathers bristling, orange-red "
               "speed streaks behind it and a puff of brown dust below."),
    ("ult", "大招「鸟群之家」图标", "skill_icons[2] `asset/tft/icons/tft_raptor_ult`",
     ICON + ": a big brown hooked-beak raptor head with a purple ruff and glowing orange eyes, beak open calling, and "
               "four tiny round red baby raptors gathered in front of it."),
]
BIG_FX = ["r_flock"]
FLYING = ("a_bolt", "q_feather", "r_peck")

GROUPS = [
    ("a_bolt q_feather r_peck (the flying feathers)",
     ["xayah_base_p_feather_full", "xayah_base_q_feather", "xayah_base_r_feather", "xayah_base_w_feathers",
      "xayah_base_q_feather_glow"]),
    ("a_hit q_hit r_peck_hit (the hits)",
     ["xayah_base_ba_hit_flash", "xayah_base_ba_hit_centerflare", "quinn_base_ba_hit_hitflash", "xayah_base_z_flecks",
      "xayah_base_w_tar_bits"]),
    ("e_jump e_rush (the hop and the rush)",
     ["quinn_base_e_smoke_mult", "quinn_base_q_wind", "xayah_base_w_buf_swirls", "xayah_base_w_buf_feather",
      "quinnvalor_base_q_tar_wind_alpha"]),
    ("p_shred r_flock (the shred and the flock)",
     ["xayah_base_r_tar_impact", "xayah_base_e_tar_ring", "xayah_base_passive_sparks", "xayah_base_r_feathers",
      "quinn_base_q_slash_dark"]),
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
    """The raptor at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"锋喙鸟 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 深红锋喙鸟：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定（`design/raptor_design.png`："
      "3/4 朝右、压低身子蹲着的圆胖鸟：红色背羽和尾羽往后上方翘；紫色尖刺鬃毛围着脖子；棕色骨质鸟头、厚弯钩喙、两只发光的橙色眼睛，"
      "嘴里透橙光；头顶一个红色尖冠；两条短棕腿、深藏青弯钩大爪）。"
      f"锋喙鸟在游戏里是**高清**的（每个游戏格子里约 1.56×1.56 个细像素），{h} 格高、{w} 格宽（高×宽）；"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/raptor_size.png`：锋喙鸟缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是霞（羽毛、羽刃、命中）和奎因（华洛、风、烟）的特效贴图"
      "（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。")
    a("> - **锋喙鸟是峡谷里的野鸟，特效都是它的味道**：尖尖的红色、橙红色羽毛（边缘亮橙色）、像它眼睛一样的橙色火星、"
      "少量紫色尖羽、棕色尘土；不要符文魔法、不要闪电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、拖尾、尘土没有黑描边**；羽毛和小鸟可以有深色描边。")
    a("> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。")
    a("> - **对称**：飞出去的三种（`a_bolt`、`q_feather`、`r_peck`）**上下对称、朝右**（游戏按飞行方向旋转它们）；"
      "其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。`r_flock` 的四只小鸟**正面朝着我们**，所以左右对称也自然。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `raptor_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入）" + ("；图标交付 `raptor_icon_<名字>.png`（64×64）" if n_ic else "") +
      "，附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，"
      f"都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「锋羽射击」 | 甩出一根追踪的红色羽毛 | `a_bolt` · `a_hit` |")
    a("| 被动「橙霸符」 | 它的物理伤害减敌人护甲，最多叠 5 层 | `p_shred` |")
    a("| 技能 1 =「羽刃扇射」 | 张开翅膀和羽冠，扇形甩出五根羽刃，每根打中第一个敌人 | `q_feather` · `q_hit` |")
    a("| 技能 2 =「惊飞跃退」 | 尖叫一声往后一跳，之后几秒攻速大涨 | `e_jump` · `e_rush` |")
    a("| 大招 =「鸟群之家」 | 召唤四只小锋喙鸟围在身边，它每次普攻小鸟们一起扑上去啄同一个敌人 | "
      "`r_flock` · `r_peck` · `r_peck_hit` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、拖尾、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（羽毛、小鸟可以有深色描边）。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("羽毛红（背羽尾羽，深红到橙红）", FEATHER), ("橙光（眼睛、嘴里的光、橙霸符）", GLOW),
                        ("紫色鬃毛", RUFF), ("尘土", DUST)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中居中画，不旋转；地面上的尘土是从斜上方看的扁平一团。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `raptor_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `raptor_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `raptor_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `raptor_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_raptor_fx`（小的）和 `tft_raptor_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a(f"- {'、'.join(FLYING)} 断言上下对称（朝右），其余断言左右对称。")
    a("- a_bolt、r_peck 是普攻的追踪弹道，q_feather 是 tft.dll 扇形放出的羽刃；a_hit、q_hit、r_peck_hit 在被打中的人身上；"
      "e_jump 放在它起跳的地面上（不跟随，z -1）；e_rush、r_flock 是它身上的 buff；p_shred 是 tft.dll 给敌人叠的减甲 buff。")
    a("- 用 `pixel_1x/` 切格（import_sentinel_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="raptor_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/raptor_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_raptor.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "raptor_design.png"))
    shape = size_sheet(os.path.join(out, "design", "raptor_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"raptor_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"raptor_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
