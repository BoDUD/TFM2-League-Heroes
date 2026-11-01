#!/usr/bin/env python3
"""Build murkwolf_fx_pack.zip: step 3 of Murk Wolf's sprite - Codex draws its effects and its three skill icons
(the tft heroes' way).

    python tools/lol/fx_ref_murkwolf.py            # the particle references -> C:/t/mw_work/fxref
    python tools/art/pack_murkwolf_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name murkwolf_fx_redo_pack]

The pack (C:/t/mw_work/fx/murkwolf_fx_pack, zipped into --out, default D:/TFM2-Workshop/murkwolf_packs) holds PROMPTS.md
(also written to assets/source/murkwolf/PROMPTS_FX.md), design/murkwolf_design.png (the approved idle at 4x on its own
squares), design/murkwolf_size.png (it at game size, 4x, on the arena colour with the ground line, a 10-px ruler and
the base fighter) and refs/tft_fx_ref.png (Naafiri's fangs and packmates, Samira's and Volibear's slashes and cracks,
Warwick's sparks and smoke - grey shapes the game tints, grouped by the effect they inform). The effects are the views
the kit binds (tools/kit/build_murkwolf.py, the user's picks 2026-11-01: jungle, plan A 「撕裂之爪」): view_effects
a_hit, q_land, q_hit, r_hit, r_bite, p_hit; view_buffs q_emp, e_howl, r_pack (the big sheet). No projectiles. Plus the
three skill icons. Its colours: the dark purple murk of its mane, the cyan of its eyes, the cream of its fangs, the
pink-crimson of its mouths and the wounds it tears, the slate blue of its fur.
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

TMP = "C:/t/mw_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "murkwolf", "PROMPTS_FX.md")
HD = os.path.join(ROOT, "assets", "source", "murkwolf", "hd")
NAME = "murkwolf_fx_pack"
PPU = 1.67

MURK = "#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030"         # the dark purple murk of its mane, its smoke
CYAN = "#F0FFFF, #9CF5FF, #36D6F2, #1690B8, #0C4E70"         # its glowing cyan eyes; the claws' edge
FANG = "#FFFCEB, #F7E9AE, #DCC062, #9E812F"                  # its cream-yellow fangs
GASH = "#FFD6E6, #F57FB4, #D63F78, #8C1F46, #4A0E26"         # its pink mouths, the wounds it tears
FUR = "#DCE4F5, #9AA9D1, #6A78A8, #444E78, #262B47"           # its slate-blue fur (the pups)
MU = f"a murk purple ramp ({MURK})"
CY = f"a cyan glow ramp ({CYAN})"
FA = f"a fang cream ramp ({FANG})"
GA = f"a gash pink-crimson ramp ({GASH})"
FU = f"a slate-blue fur ramp ({FUR})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
row = RF.row
MAGIC = ("everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson "
         "gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic "
         "runes, no lightning, no smooth neon beams")
HIM = ("the wolf stands in the middle, not drawn: about 50 squares wide and 36 tall, a crouched four-legged TWO-HEADED "
       "wolf, its two heads at the right, its bushy tail up at the upper left, its feet on the bottom line of the cell")
ICON = ("A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan "
        "corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px "
        "a square (32 x 32 squares), chunky and readable at 64 px")

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    ("a_hit", "普攻「双头撕咬」：咬中，4 帧", "view_effects `tft_murkwolf_a_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "两个头一口咬下：**上下两排奶白色尖牙**一下合拢，中间一闪粉红色，两边崩出两点粉色血星。**左右对称**，4 帧。",
     FA + ", " + GA,
     "A SNAPPING BITE, 4 frames, " + LR + ": 1 two curved rows of cream FANGS (an upper row pointing down and a "
     "lower row pointing up, each 10 squares wide with 4 sharp teeth) wide apart, top and bottom of the cell; 2 the rows "
     "snapping shut in the middle, a pink-white flash 6 squares across where they meet; 3 the fangs gone, a pink-crimson "
     "burst 10 squares across with two pink droplets flying out to both sides (mirrored); 4 the droplets falling, one on "
     "each side. " + MAGIC + ".",
     row(4, 14, 14) + CENTER),
    ("q_land", "技能 1「撕裂之爪」：落地的尘土，5 帧", "view_effects `tft_murkwolf_q_land`（放在它落地的地面上，不跟随，z -1；左右对称）",
     "44 × 12",
     "它扑落的地面：**一圈紫黑色的暗影尘土往两边炸开**，地上裂开几道短裂缝，透出青色微光。**只在地面和低处**。**左右对称**，5 帧。",
     MU + ", " + CY,
     "A POUNCE LANDING, 5 frames, " + LR + ": on the GROUND and low above it, seen from above at a slant: 1 a flat "
     "dark purple murk puff 14 squares wide at the bottom middle; 2 two murk clouds bursting out to both sides "
     "(mirrored), 34 squares wide and 8 tall, three short jagged ground CRACKS under them glowing cyan; 3 the clouds 42 "
     "squares wide and thinner, the cracks' glow fading; 4 the murk settling low; 5 the last wisps on each side. "
     + MAGIC + ".",
     row(5, 44, 12) + CENTER),
    ("q_hit", "技能 1「撕裂之爪」：撕裂，5 帧", "view_effects `tft_murkwolf_q_hit`（跟随目标，z 2；左右对称）", "20 × 18",
     "撕裂之爪抓中：**两组三道爪痕交叉成 X**（左上往右下三道、右上往左下三道），爪痕边缘青白色、里面是粉红色的伤口，周围一圈紫色暗影。**左右对称**，5 帧。",
     CY + ", " + GA + ", " + MU,
     "A RENDING CLAW X, 5 frames, " + LR + ": 1 a cyan-white flash 6 squares across; 2 TWO SETS OF THREE parallel CLAW "
     "GASHES crossing in a big X 16 squares across (three from the upper left down to the lower right and the mirror "
     "three from the upper right), each gash near-white and cyan along its edges with a hot pink-crimson core; 3 the "
     "gashes at full length, dark purple murk wisps puffing out at the four tips; 4 the gashes fading to pink-crimson, "
     "a few pink droplets; 5 the last murk wisps. " + MAGIC + ".",
     row(5, 20, 18) + CENTER),
    ("p_hit", "被动「灰霸符」：技能暴击，4 帧", "view_effects `tft_murkwolf_p_hit`（跟随目标，z 3；左右对称）", "16 × 16",
     "技能暴击：**一个锋利的银白色四角星**一闪，星芯青色，外面一圈锯齿状的灰紫色尖刺往外扎。**左右对称**，4 帧。",
     CY + ", " + MU,
     "A CRITICAL STRIKE, 4 frames, " + LR + ": 1 a tiny near-white point; 2 a sharp silver-white FOUR-POINT STAR 14 "
     "squares across with a cyan core, a ring of eight short jagged grey-purple spikes round it; 3 the star shrinking, "
     "the spikes flying outward; 4 four small cyan sparks at the corners. " + MAGIC + ".",
     row(4, 16, 16) + CENTER),
    ("r_hit", "大招「狼群攻击」：小狼扑中，5 帧", "view_effects `tft_murkwolf_r_hit`（跟随目标，z 2；左右对称）", "22 × 16",
     "两只小狼从两边扑上来：**左右各一道弯弯的爪痕**向中间划过，中间一团紫色暗影炸开，两点青色眼光一闪。**左右对称**，5 帧。",
     CY + ", " + GA + ", " + MU,
     "A PACK POUNCE, 5 frames, " + LR + ": 1 two cyan eye glints (2x1 squares) at the left and right edges; 2 from "
     "each side a curved claw swipe of two parallel gashes sweeping in toward the middle (mirrored), cyan-white edges, "
     "pink-crimson cores, 9 squares long; 3 the swipes meeting, a dark purple murk burst 12 squares across in the "
     "middle; 4 the murk spreading and thinning, pink droplets; 5 the last wisps. " + MAGIC + ".",
     row(5, 22, 16) + CENTER),
    ("r_bite", "大招「狼群攻击」：小狼咬一口，4 帧", "view_effects `tft_murkwolf_r_bite`（跟随目标，z 2；左右对称）", "10 × 10",
     "小狼咬一口：**一对小小的奶白色尖牙**一下合拢，一点粉红色。比普攻的小。**左右对称**，4 帧。",
     FA + ", " + GA,
     "A SMALL NIP, 4 frames, " + LR + ": 1 two tiny rows of cream fangs (6 squares wide, 3 teeth each) apart; 2 "
     "snapping shut; 3 a small pink burst 6 squares across; 4 one pink droplet on each side. " + MAGIC + ".",
     row(4, 10, 10) + CENTER),
    ("q_emp", "技能 1「撕裂之爪」：强化攻击，6 帧循环", "view_buffs `tft_murkwolf_q_emp`（跟随它，z 3；左右对称）", "60 × 40",
     "撕裂之爪后面三次攻击被强化（攻速加快）：它**脚下两边各一道青白色的爪光**一闪一闪，身子轮廓外面几点青色小火星和短短的速度线往后掠。**它的身体位置留空**。**左右对称**，6 帧循环。",
     CY + ", " + MU,
     "SHARPENED CLAWS, 6 looping frames, " + LR + ": round " + HIM + ": at the bottom on EACH side (mirrored), "
     "where its front and hind paws touch the ground, three short bright cyan-white CLAW GLINTS (thin slanted lines 4 "
     "squares long); a few small cyan sparks (1x1 and 2x2 squares) blinking just outside its outline, two short cyan "
     "speed streaks on each side sweeping up and outward; frames 1-6 the glints flashing in turn and the sparks "
     "blinking (every frame left-right symmetric). The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 60, 40) + CENTER),
    ("e_howl", "技能 2「狂战士之嚎」：嚎叫之后，6 帧循环", "view_buffs `tft_murkwolf_e_howl`（跟随它，z 3；左右对称）", "64 × 48",
     "狂战士之嚎（吸血、伤害提高）：它身子两侧**紫黑色的暗影烟往上蹿**，烟里飘着粉红色的小火星，头顶一圈淡淡的粉红色光边。**它的身体位置留空**。**左右对称**，6 帧循环。",
     MU + ", " + GA,
     "A BERSERK AURA, 6 looping frames, " + LR + ": round " + HIM + ": on EACH side of its body (mirrored) tongues "
     "of DARK PURPLE MURK SMOKE licking up along its outline from the ground to above its back, small hot pink-crimson "
     "embers rising through the smoke, a thin pink-red rim glow along the top edge above it; frames 1-6 the smoke "
     "tongues rising and curling, the embers drifting up (every frame left-right symmetric). The middle of the cell "
     "(its body) stays EMPTY. " + MAGIC + ".",
     row(6, 64, 48) + CENTER),
    ("r_pack", "大招「狼群攻击」：身边的两只小暗影狼，6 帧循环", "view_buffs `tft_murkwolf_r_pack`（大表，跟随它，z -1；左右对称）",
     "100 × 40",
     "狼群攻击：**两只小暗影狼**站在它身体左右两边的地上。小狼是峡谷里的小狼、**只有一个头**、**正面朝着我们**：灰蓝色的毛、"
     "背上一小撮紫色鬃毛、尖耳朵、两只发光的青色眼睛、龇着牙伸着粉色舌头，约 14 格宽、13 格高。轮流低吼、喘气、往前一顿。"
     "**中间它的身体位置留空**（小狼画在它后面一层）。**左右对称**，6 帧循环。",
     FU + ", " + MU + ", " + CY + ", " + GA,
     "THE PACK, 6 looping frames, " + LR + ": round " + HIM + ": TWO WOLF PUPS (little one-headed murk wolves, "
     "each about 14 squares wide and 13 tall, seen FROM THE FRONT facing us so they read the same both ways: slate-blue "
     "fur with a lighter chest, a small tuft of DARK PURPLE MANE on the back of the neck, two upright pointed ears with "
     "pink insides, two glowing CYAN eyes, a snarling mouth with tiny cream fangs and a pink tongue, four short legs with "
     "black claws) placed mirrored: one pup standing on the bottom line on EACH side just outside its outline; frames "
     "1-6 the pups growling, panting and lunging one square forward in turn, a small murk wisp at their paws, every frame "
     "left-right symmetric. The middle of the cell (its body) stays EMPTY. " + MAGIC + ".",
     row(6, 100, 40) + CENTER),
]
ICONS = [
    ("skill", "技能 1「撕裂之爪」图标", "skill_icons[0] `asset/tft/icons/tft_murkwolf_skill`",
     ICON + ": a slate-blue two-headed wolf leaping toward the upper right, both mouths open, its front claws spread, "
               "three cyan-white claw gashes slashing across the corner in front of it."),
    ("skill2", "技能 2「狂战士之嚎」图标", "skill_icons[1] `asset/tft/icons/tft_murkwolf_skill2`",
     ICON + ": two slate-blue wolf heads side by side with white cheek ruffs, muzzles thrown up to the sky howling, "
               "glowing cyan eyes, dark purple murk smoke and pink embers rising round them."),
    ("ult", "大招「狼群攻击」图标", "skill_icons[2] `asset/tft/icons/tft_murkwolf_ult`",
     ICON + ": a big two-headed slate-blue wolf with a purple mane snarling at the back, two small one-headed wolf "
               "pups with glowing cyan eyes lunging forward in front of it."),
]
BIG_FX = ["r_pack"]
FLYING = ()

GROUPS = [
    ("a_hit r_bite p_hit (the bites and the crit)",
     ["naafiri_base_ba_fangs01", "naafiri_base_foundation_impactspike_2x2", "warwick_base_z_bightspark",
      "samira_skin10_flarestar_dissove", "naafiri_base_2x2_sparkle"]),
    ("q_hit r_hit (the claws)",
     ["volibear_base_q_swipe_a", "samira_base_ba_sharp_ray", "naafiri_base_r_flash_sharp",
      "warwick_base_w_rengar_base_p_shafts", "naafiri_base_foundation_missile01"]),
    ("q_land e_howl q_emp (the landing, the howl, the claws' glint)",
     ["samira_base_e_ground_cracks", "vladimir_base_e_smokeerode", "warwick_base_idle_smoke",
      "warwick_base_idle_plasma_sharp", "naafiripackmate_speedboostline"]),
    ("r_pack (the pups)",
     ["naafiri_base_r_packmatehead", "naafiri_base_r_eyes01", "naafiri_base_glowavatar01", "naafiri_base_r_cas_outline",
      "warwick_base_idle_steamjets"]),
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
    """The wolf at game size next to the base fighter (4x), the ground line, a 10-px ruler."""
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
    d.text((8, 36), f"暗影狼 {figs[0].shape[1]}×{figs[0].shape[0]} 格，原版斗士 {figs[1].shape[1]}×{figs[1].shape[0]} 格（4 倍）",
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
    a("# 暗影狼：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图" + (f" + {n_ic} 个技能图标" if n_ic else "") + "。** 造型已定，见 `design/murkwolf_design.png`：")
    a(">   - 3/4 朝右、四条腿压低身子的**双头狼**，灰蓝色的毛；")
    a(">   - 背上紫色鬃毛和一排墨绿尖刺，蓬松的大尾巴往左上方翘；")
    a(">   - 两个狼头并排，青色发光的眼睛、粉色大嘴、奶黄色尖牙、白色腮毛；")
    a(">   - 黑色弯钩爪。")
    a(f">\n> 暗影狼在游戏里是**高清**的（每个游戏格子里约 {PPU}×{PPU} 个细像素），{h} 格高、{w} 格宽（高×宽）。"
      "**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/murkwolf_size.png`：暗影狼缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。"
      "每条写的大小都是游戏像素（格）。")
    a("> - 参考图 `refs/tft_fx_ref.png` 是纳亚菲利（尖牙、猎犬）、莎弥拉和沃利贝尔（爪痕、地裂）、沃里克（火星、烟）的特效贴图。"
      "这些是**灰色的形状，游戏里再染色**，已经按用在我们哪张特效分好了行。只在本地用。")
    a("> - **暗影狼是峡谷里的野狼，特效都是它的味道**：爪痕、咬痕、奶白色尖牙、粉红色的伤口、像它眼睛一样的青色闪光、紫黑色的暗影烟。"
      "不要符文魔法、不要闪电、不要光滑的霓虹光束。")
    a("> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、烟、尘土没有黑描边**；尖牙和小狼可以有深色描边。")
    a("> - **围着它的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住它。")
    a("> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。`r_pack` 的两只小狼**正面朝着我们**，所以左右对称也自然。")
    a("> - 交付方式：")
    a(">   - 每张生成后按格子取回（每格取多数颜色）。")
    a(">   - 交付 8 倍的 `murkwolf_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。")
    if n_ic:
        a(">   - 图标交付 `murkwolf_icon_<名字>.png`（64×64）。")
    a(">   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。")
    a(f">   - 都放在 `outputs/{NAME.replace('_pack', '')}/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。")
    a(">   - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻「双头撕咬」 | 两个头一起咬 | `a_hit` |")
    a("| 被动「灰霸符」 | 血越少暴击越高，技能也能暴击 | `p_hit`（技能暴击时） |")
    a("| 技能 1 =「撕裂之爪」 | 跳到附近血最少的敌人身边撕一口，之后 3 次攻击加攻速、多打伤害 | `q_land` · `q_hit` · `q_emp` |")
    a("| 技能 2 =「狂战士之嚎」 | 仰头长嚎，5 秒吸血、伤害提高，对残血更高 | `e_howl` |")
    a("| 大招 =「狼群攻击」 | 叫来两只小暗影狼，先扑向目标，之后它每次攻击小狼跟着咬两口 | "
      "`r_pack` · `r_hit` · `r_bite` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（尖牙、小狼可以有深色描边）。")
    a("- 每个形状 2–3 档平涂。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("暗影紫（鬃毛、暗影烟）", MURK), ("青光（眼睛、爪光）", CYAN), ("尖牙奶黄", FANG),
                        ("伤口粉红（嘴、撕开的伤口）", GASH), ("灰蓝毛（小狼）", FUR)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中的画面居中画，不旋转；地面上的尘土是从斜上方看的扁平一团。")
    a("- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `murkwolf_fx_{name}.png`：{title}\n")
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
            a(f"### 图标 {k}. `murkwolf_icon_{name}.png`：{title}\n")
            a("```text")
            a(prompt + " No text, no letters.")
            a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `murkwolf_fx_{name}` | {bind} | {size} |")
    for name, _, bind, *_ in (ICONS if n_ic else []):
        a(f"| `murkwolf_icon_{name}` | {bind} | 64 × 64 |")
    a("")
    a(f"- 两张表：`asset/tft/effects/tft_murkwolf_fx`（小的）和 `tft_murkwolf_big`（{'、'.join(BIG_FX)}），tag = 名字。")
    a("- 全部断言左右对称。")
    a("- a_hit、q_hit、r_hit、r_bite、p_hit 在被打中的人身上（tft.dll 放 q_land、q_hit、r_hit、r_bite、p_hit）；"
      "q_land 放在它落地的地面上（不跟随，z -1）；q_emp、e_howl 是它身上的 buff；r_pack 是大表上的 buff（z -1，小狼在它后面一层）。")
    a("- 用 `pixel_1x/` 切格（import_raptor_fx 的做法，改成 import_murkwolf_fx）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="murkwolf_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default="D:/TFM2-Workshop/murkwolf_packs", help="folder for the zip")
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
        sys.exit(f"no references in {REF}: run tools/lol/fx_ref_murkwolf.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "murkwolf_design.png"))
    shape = size_sheet(os.path.join(out, "design", "murkwolf_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    doc = document(shape, icons=not a.only)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    sym = lambda name: "top-bottom (pointing right)" if name in FLYING else "left-right"
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"murkwolf_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": sym(x[0])}
                   for x in FX] +
                  ([{"file": f"murkwolf_icon_{x[0]}.png", "binding": x[2], "size": "64 x 64"} for x in ICONS]
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
