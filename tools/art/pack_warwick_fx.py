#!/usr/bin/env python3
"""Build warwick_fx_pack.zip: step 3 of Warwick's sprite - Codex draws his effects (pack_vex_fx.py's way,
pack_rammus_fx's sheets).

    python tools/lol/fx_ref_warwick.py          # League's particle textures -> C:/t/ww_work/fxref (Riot's art, local only)
    python tools/art/pack_warwick_fx.py [--no-zip] [--out DIR] [--only a_hit,q_hit --name warwick_fx_redo_pack]

The pack (C:/t/ww_work/fx/warwick_fx_pack, zipped into --out, default dist/warwick_packs) holds PROMPTS.md (also written
to assets/source/warwick/PROMPTS_FX.md), design/warwick_idle.png (his idle at 4x, the design's squares at PPU 1.5),
design/warwick_size.png (the 1x idle at 4x on the arena colour with the ground line, a 10-px ruler and the base fighter),
design/warwick_shots.png (action frames the pictures start from, 4x) and refs/lol_fx_ref.png (League's own particle
textures for Warwick grouped by the effect they inform).
The effects are the views the kit binds (tools/kit/build_warwick.py): view_effects a_hit, q_hit, q_heal, e_howl, e_roar,
e_fear, r_bind, r_hit; view_buffs e_guard (Primal Howl's guard, on `e_on`) and w_hunt (Blood Hunt). League's colours:
his claws and his hunger are BLOOD RED (the claw streaks, the bite, the heal, the suppression, the Blood Hunt trail), the
Primal Howl's guard is a pale STEEL-BLUE shell, its howl a pale VIOLET-GREY shockwave, the fear a PURPLE snarling wolf
head (League's fear mark). Red side: the client never mirrors an effect picture, so every hit, buff and ground picture is
symmetric left to right (no projectile pictures: his strikes are hidden homing strikes).
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402

TMP = "C:/t/ww_work"
REF = os.path.join(TMP, "fxref")
DOC = os.path.join(ROOT, "assets", "source", "warwick", "PROMPTS_FX.md")
SHEET = os.path.join(ROOT, "league", "champions", "league_warwick")
NAME = "warwick_fx_pack"

BLOOD = "#FFFFFF, #FFD6CC, #FF7466, #E8242E, #A8101E, #5C0812"       # claws, the bite, the hunger, the hunt
STEEL = "#FFFFFF, #E6EEFF, #BACAEA, #8494C4, #525E94, #2C3262"       # Primal Howl's guard shell
HOWL = "#FFFFFF, #ECE6FF, #C0B2E6, #8A7ABA, #544488, #2C2054"        # the howl's shockwave and sound waves
FEAR = "#FFFFFF, #FFC0F2, #DA56E8, #9424B2, #520E6E"                 # the fear's wolf head
BL = f"a blood-red ramp ({BLOOD})"
ST = f"a pale steel-blue ramp ({STEEL})"
HO = f"a pale violet-grey ramp ({HOWL})"
FE = f"a purple ramp ({FEAR})"
LEAD = RF.LEAD
LR = RF.LR
CENTER = RF.CENTER
HIM = ("the hunched werewolf stands in the middle, not drawn: 46 squares from the spike on his back to the ground, about "
       "40 squares wide without his tail")
CHAMP = "an upright champion 16 squares wide and 36 tall stands in the middle, not drawn"
row = RF.row

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- auto attack
    ("a_hit", "普攻：爪子撕中目标，3 帧", "view_effects `league_warwick_a_hit`（跟随目标，画在人物上面 z 2；左右对称）", "16 × 16",
     "他挥爪打中目标：三道并排、竖着往下的血红色爪痕一闪（中间白、边上血红），然后散成几点血珠（参考 q_wolfmanclaw、q_slash、q_shred）。"
     "**左右对称**（三道爪痕都是竖的，中间那道最长）。",
     BL,
     "A CLAW RAKE ON A TARGET, 3 frames, " + LR + ": 1 three parallel VERTICAL claw streaks 12 squares tall, 3 squares apart, "
     "the middle one the longest, each white in the middle and blood red at its edges, tapering to points at both ends; "
     "2 the streaks thinner and darker red, a few blood droplets flying out to both sides at mirrored places; 3 only the "
     "droplets and the faint streak tails, fading.",
     row(3, 16, 16) + CENTER),
    # ---- Q Jaws of the Beast
    ("q_hit", "Q 野兽之口：獠牙咬合，5 帧", "view_effects `league_warwick_q_hit`（跟随目标，画在人物上面 z 2；左右对称）", "22 × 22",
     "Q 咬中目标：一副大狼嘴的上下两排白色獠牙从上下两边合拢、在目标身上咬住，咬合处爆出一团血红色的血花（参考 q_biteswipe、"
     "q_swipetrail、q_shred）。**左右对称**，5 帧。",
     BL,
     "A BEAST'S BITE ON A TARGET, 5 frames, " + LR + ": 1 an upper row of 5 big white fangs (each 2 wide, 4 tall, pointing "
     "down) on a dark red gum at the top of the cell and a lower row of 4 fangs (pointing up) at the bottom, far apart; "
     "2 the two rows half-way closed; 3 the rows SNAPPED SHUT in the middle, a bright white-red flash where they meet; "
     "4 the fangs gone, a blood-red burst 18 squares across with droplets flying out; 5 only droplets and wisps, fading.",
     row(5, 22, 22) + CENTER),
    ("q_heal", "Q / 血之饥渴：吸血回复（他身上，跟随），5 帧",
     "view_effects `league_warwick_q_heal`（跟随他，画在人物上面 z 2；左右对称）", "44 × 50",
     "他咬中或者残血时回血：一圈血红色的光从他脚下亮起，一颗颗血珠从两边往上飘、往他胸口的高度聚过去（参考 z_bightspark、"
     "idle_plasma）。**他站在中间不画人，只画外圈和脚下**，**左右对称**，5 帧。",
     BL,
     "A BLOOD HEAL ROUND A BIG BEAST, 5 frames, " + LR + " (" + HIM + ", his body area left EMPTY): 1 a thin blood-red "
     "ellipse lighting up on the ground under him (40 wide, 9 tall); 2 eight round blood droplets (2-3 squares each) rising "
     "from the ellipse at his left and right; 3 the droplets higher, curving in toward the middle at his chest height (two "
     "thirds up), a soft red glint on each; 4 the droplets reaching the middle and flashing white; 5 only the fading "
     "ellipse and two sparks.",
     row(5, 44, 50) + "; centered across, the ellipse's middle 4 squares above the cell's bottom row."),
    # ---- E Primal Howl
    ("e_guard", "E 远祖嗥叫：护体（buff，循环），4 帧", "view_buffs `league_warwick_e_on`（跟随他，画在人物上面 z 2；左右对称；循环）",
     "64 × 54",
     "E 开着时他受到的伤害减少：一层淡钢蓝色的护罩罩住他，罩子是一个扁圆的半透明壳（只画边：2 格宽的亮边，几道弧形的高光），上面有一圈圈"
     "波纹慢慢流动（参考 w_deflectionbubble、w_deflectionripples）。**他站在中间不画人，只画罩子的边和高光**，**左右对称**，4 帧循环。",
     ST,
     "A STEEL-BLUE GUARD SHELL ROUND A BIG BEAST, 4 frames, a seamless loop, " + LR + " (" + HIM + ", his body area left "
     "EMPTY): a wide dome-shaped shell outline round him, 60 squares wide and 50 tall, its bottom open at the ground, its "
     "rim 2 squares of pale steel-blue with a white inner edge; two curved white highlight arcs on its upper left and "
     "upper right; each frame a ripple ring of lighter blue travels a few squares up the rim and the highlights shimmer.",
     row(4, 64, 54) + "; centered across, the dome's open bottom on the cell's bottom row."),
    ("e_howl", "E：嚎叫冲击波（地上，跟随），6 帧", "view_effects `league_warwick_e_howl`（跟随他，画在人物下面 z -1；左右对称；大图表）",
     "88 × 32",
     "嚎叫的一下：贴着地面一圈淡紫灰色的冲击波往外扩，带一圈灰白色的尘土，范围约 80 格宽（参考 z_shockwave、e_fearlines、z_smokepoofs）。"
     "**只画在地面上（他站在中间，不画人）**，**左右对称**，6 帧。",
     HO,
     "A HOWL'S SHOCKWAVE along the ground round him, 6 frames, " + LR + " (" + HIM + "): 1 a small bright ring on the ground "
     "(an ellipse 24 wide and 8 tall), white-violet; 2 the ring 46 wide and 15 tall, 2 squares thick, with a second fainter "
     "ring inside; 3 the outer ring 66 wide and 22 tall, small grey dust puffs kicked up along it at mirrored places; "
     "4 the ring 80 wide and 27 tall, thinning, the dust rising; 5 only broken arcs of the ring and the dust; 6 faint dust, "
     "fading.",
     row(6, 88, 32) + "; centered across, the ellipse's middle 3 squares above the cell's middle row."),
    ("e_roar", "E：嚎叫的声浪（他头顶上方，跟随），5 帧", "view_effects `league_warwick_e_roar`（跟随他，画在人物上面 z 3；左右对称）",
     "44 × 26",
     "他仰天嚎叫时从头顶往外扩的声浪：三道弧形的淡紫灰色声波一道接一道往上、往两边扩开（像括号形的弧），中间夹着几道白色的短线"
     "（参考 e_fearlines、z_eyeripples）。**画在他头顶上方，下面留空**，**左右对称**，5 帧。",
     HO,
     "A ROAR'S SOUND WAVES over a head, 5 frames, " + LR + ": three wide upward-opening ARCS (like the top of a ring, each "
     "2 squares thick) rising one after another from the bottom middle of the cell: 1 a small bright arc 10 wide just above "
     "the bottom; 2 that arc 20 wide and higher, a second small one under it; 3 the first 32 wide, the second 20, a third "
     "small one; 4 the arcs 42, 30 and 18 wide, the outer one fading, short white lines between them radiating out; 5 only "
     "faint outer arcs, fading.",
     row(5, 44, 26) + "; centered across; the arcs start from the cell's bottom middle."),
    ("e_fear", "E：恐惧（敌人头上），6 帧", "view_effects `league_warwick_e_fear`（跟随目标，画在人物上面 z 3；左右对称）", "16 × 14",
     "被嚎叫吓到的敌人头上冒出一个紫色的狼头（龇牙咧嘴、两只尖耳朵，正面），一闪一闪地抖动（参考 w_warn_solid、e_fearlines）。"
     "**左右对称**（狼头是正面的），6 帧。",
     FE,
     "A FEAR MARK over a head, 6 frames, " + LR + ": a small snarling WOLF HEAD seen from the front (two pointed ears, two "
     "slanted white eyes, an open jaw with white fangs), 12 squares wide, purple with a pale pink rim; 1 it pops in small; "
     "2 full size; 3 shaken one square up; 4 back, two short purple jitter lines at its sides; 5 like 2; 6 fading.",
     row(6, 16, 14) + CENTER),
    # ---- R Infinite Duress
    ("r_bind", "R 无尽束缚：压制（目标身上），8 帧", "view_effects `league_warwick_r_bind`（跟随目标，画在人物上面 z 2；左右对称）",
     "28 × 36",
     "R 扑中的英雄被压住 1.5 秒：两道血红色的能量环一上一下箍住他（扁圆环，一前一后），环上缠着暗红色的爪痕和锁链样的纹路，一闪一闪地"
     "收紧（参考 r_missscratches、warwick_temp_r_wolfmanclaw、r_rangeringmult）。**被压住的人站在中间不画，只画环和爪痕**，"
     "**左右对称**，8 帧（一共约 1.5 秒）。",
     BL,
     "A BLOOD SHACKLE ROUND A CHAMPION, 8 frames, " + LR + " (" + CHAMP + ", the body area left EMPTY): two flat blood-red "
     "rings (ellipses 26 wide and 7 tall, 2 squares thick, white-hot inner edge) around the body, one at its waist and "
     "one at its chest; dark red claw scratches (short diagonal triple streaks, mirrored) on both sides between them; the "
     "rings pulse tighter and brighter on frames 1, 4 and 7 and fade a little between; frame 8 the rings breaking into "
     "red sparks.",
     row(8, 28, 36) + "; centered across, the waist ring 12 squares above the cell's bottom row."),
    ("r_hit", "R：撕扯（目标身上），4 帧", "view_effects `league_warwick_r_hit`（跟随目标，画在人物上面 z 2；左右对称）", "24 × 24",
     "R 压住时每一下抓：一个大大的血红色 X 形爪痕（两组三道爪痕交叉）在目标身上炸开，中间白光，血珠四溅（参考 q_wolfmanclaw、"
     "q_shred、z_blaststreaks）。**左右对称**，比普攻的打中大。",
     BL,
     "A BIG CROSSED CLAW TEAR, 4 frames, " + LR + ": 1 a white flash 6 squares across; 2 two sets of three claw streaks "
     "crossing in an X, 20 squares across, white in the middle and blood red at their edges; 3 the X darker, blood droplets "
     "bursting out at mirrored places; 4 only droplets and faint streak ends.",
     row(4, 24, 24) + CENTER),
    # ---- W Blood Hunt
    ("w_hunt", "W 鲜血追猎：追猎中（buff，他脚下，循环），4 帧",
     "view_buffs `league_warwick_w_hunt`（跟随他，画在人物下面 z -1；左右对称；循环）", "52 × 22",
     "他嗅到残血的猎物、加速追过去：脚下一圈血红色的光晕，两边有血红色的细烟往上飘，像血的气味在他周围翻腾（参考 w_scenttrail_blend、"
     "w_deathwisps、w_arrow_directional_red）。**只画在他脚下和两边下方，不画人**，**左右对称**，4 帧循环。",
     BL,
     "A BLOOD-SCENT AURA under a big beast, 4 frames, a seamless loop, " + LR + " (" + HIM + "): a glowing blood-red "
     "ellipse on the ground under him (46 wide, 11 tall, its rim brightest), thin red wisps of scent curling up 8-10 "
     "squares at its left and right ends; each frame the wisps curl a little higher and fade while new ones start low, "
     "the rim flickering.",
     row(4, 52, 22) + "; centered across, the ellipse's middle 6 squares above the cell's bottom row."),
]
BIG_FX = ["e_howl", "e_guard"]
GROUPS = [
    ("a_hit r_hit", ["warwick_base_q_wolfmanclaw", "warwick_base_q_slash", "warwick_base_q_shred",
                     "warwick_base_z_blaststreaks", "warwick_temp_r_wolfmanclaw"]),
    ("q_hit q_heal", ["warwick_base_q_biteswipe", "warwick_base_q_swipetrail", "warwick_base_z_bightspark",
                      "warwick_base_idle_plasma"]),
    ("e_guard e_howl e_roar", ["warwick_base_w_deflectionbubble", "warwick_base_w_deflectionripples",
                               "warwick_base_z_shockwave", "warwick_base_e_fearlines", "warwick_base_z_smokepoofs",
                               "warwick_base_z_eyeripples"]),
    ("e_fear", ["warwick_base_w_warn_solid", "warwick_base_w_warn_top", "warwick_base_e_fearlines"]),
    ("r_bind", ["warwick_base_r_missscratches", "warwick_base_r_rangeringmult", "warwick_temp_r_wolfmanclaw"]),
    ("w_hunt", ["warwick_base_w_scenttrail_blend", "warwick_base_w_deathwisps", "warwick_base_w_arrow_directional_red"]),
]
SHOTS = [("attack", 3, "a_hit：爪子挥到前面打中目标（在目标身上）"), ("skill_bite", 1, "q_hit：落地咬住目标（在目标身上）；q_heal 在他身上"),
         ("skill2", 2, "e_guard：护罩罩住他"), ("skill2_howl", 3, "e_howl：脚下的冲击波；e_roar：头顶上方的声浪"),
         ("ult_hold", 1, "r_bind / r_hit：压住的英雄身上（他扑在那个英雄身上）"), ("idle", 1, "待机（大小参考）；w_hunt 在他脚下")]


def configure():
    """pack_rammus_fx's sheets drawn from Warwick's sheet, references and shots."""
    RF.SHEET, RF.REF, RF.GROUPS, RF.SHOTS, RF.SIZE_LABEL = SHEET, REF, GROUPS, SHOTS, "沃里克"


def design_sheet(path):
    """His idle at 4x, the design's own squares (PPU 1.5: 1.5 squares a game pixel)."""
    d = np.asarray(Image.open(RF.lp(os.path.join(ROOT, "assets", "source", "warwick", "hd", "idle.png"))).convert("RGBA"))
    bg = Image.new("RGBA", (d.shape[1] * 4 + 32, d.shape[0] * 4 + 32), (225, 225, 225, 255))
    bg.alpha_composite(Image.fromarray(np.repeat(np.repeat(d, 4, 0), 4, 1)), (16, 16))
    bg.convert("RGB").save(path)


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 祖安怒兽 沃里克：给 Codex 的特效提示词（第 3 步）\n")
    a(f"> **这一份是 {len(FX)} 张特效图。** 造型已定（`design/warwick_idle.png`：3/4 正面朝右、弓着背的狼人，蓝紫色的毛、白色鬃毛、"
      f"黄眼睛、张着嘴，背上竖着绿药瓶和铜尖刺，两只铜护臂，橄榄色短裤，一条翘起来的大尾巴）。他在游戏里是**高清**的（每个游戏格子里 "
      f"1.5×1.5 个细像素），{h} 格高、{w} 格宽（连尾巴）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。")
    a("> - 大小对照 `design/warwick_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是"
      "游戏像素（格）。")
    a("> - `design/warwick_shots.png`：动作帧（4 倍），青色十字是他的站位点；每张写了特效出现在哪里（动作还在改，只看位置和大小）。")
    a("> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里沃里克自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，"
      "只在本地用，不要提交。颜色照英雄联盟原版：**他的爪子、撕咬、吸血、压制和鲜血追猎都是血红色的**，**远祖嗥叫的护体是淡钢蓝色的护罩**，"
      "**嚎叫的冲击波和声浪是淡紫灰色的**，**恐惧是紫色的狼头**。")
    a("> - **特效要亮**：每团光都要有白色或最亮一档的芯；血红色要有亮红 / 白的芯，暗底上一眼能看见。")
    a("> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。")
    a("> - **对称**：所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。没有弹道图。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `warwick_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 "
      "0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和"
      f"生图原稿 `raw/`，都放在 `outputs/warwick_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 普攻（被动「血之饥渴」和 W「鲜血追猎」在里面） | 挥爪；附带魔法伤害并吸血；追猎残血的英雄时加速 | `a_hit` · `q_heal` · `w_hunt` |")
    a("| 技能 1 = Q「野兽之口」 | 扑到目标身上咬一口，回血 | `q_hit` · `q_heal` |")
    a("| 技能 2 = E「远祖嗥叫」 | 减伤护体，结束时仰天嚎叫让周围的敌人恐惧 | `e_guard` · `e_howl` · `e_roar` · `e_fear` |")
    a("| 大招「无尽束缚」 | 朝前飞扑，压住第一个英雄 1.5 秒连抓三下 | `r_bind` · `r_hit` · `q_heal` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、烟、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**"
      "（恐惧的狼头可以有一圈暗紫色的边）。")
    a("- **要亮**：每个光的形状都有白色或最亮一档的芯。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("血红色（爪痕、撕咬、吸血、压制、追猎）", BLOOD), ("淡钢蓝色（护体的罩子）", STEEL),
                        ("淡紫灰色（嚎叫的冲击波、声浪）", HOWL), ("紫色（恐惧的狼头）", FEAR)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 打中、爆发居中画，不旋转；地面上的圆（冲击波、光晕）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 画在别人身上、他身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    a(f"{len(FX)} 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 25000，嚎叫的半径 "
      "40000）。\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `warwick_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `warwick_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 两张表：`asset/league/effects/league_warwick_fx`（小的）和 `league_warwick_big`（{'、'.join(BIG_FX)}），tag = 名字"
      "（build_warwick.py 的 views；e_guard 绑在 buff `league_warwick_e_on` 上，w_hunt 绑在 `league_warwick_w_hunt` 上）。")
    a("- 全部断言左右对称；`e_howl`、`w_hunt` 画在他下面（z -1），`e_roar`、`e_fear` 在上面（z 3）。")
    a("- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（恐惧狼头的暗紫边保留）；核对交回的张数和这份清单；"
      "和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。")
    return "\n".join(L) + "\n"


def main():
    global FX, NAME
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--only", help="a redraw pack of these effects (comma separated)")
    ap.add_argument("--name", default="warwick_fx_pack", help="the pack's name (folder and zip)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "warwick_packs"), help="folder for the zip")
    a = ap.parse_args()
    NAME = a.name
    configure()
    if a.only:
        keep = a.only.split(",")
        FX = [x for x in FX if x[0] in keep]
        if len(FX) != len(keep):
            sys.exit("unknown effect in --only: %s" % a.only)
    out = os.path.join(TMP, "fx", a.name)
    zpath = os.path.join(a.out, a.name + ".zip")
    if not os.path.isdir(REF):
        sys.exit(f"no League references in {REF}: run tools/lol/fx_ref_warwick.py first")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    design_sheet(os.path.join(out, "design", "warwick_idle.png"))
    shape = RF.size_sheet(os.path.join(out, "design", "warwick_size.png"))
    RF.shots_sheet(os.path.join(out, "design", "warwick_shots.png"))
    RF.ref_sheet(os.path.join(out, "refs", "lol_fx_ref.png"))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"),) + (() if a.only else (DOC,)):
        with open(RF.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as f:
        json.dump([{"file": f"warwick_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"}
                   for x in FX], f, ensure_ascii=False, indent=1)
    print(len(FX), "effects;", DOC, shape)
    if not a.no_zip:
        os.makedirs(RF.lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(RF.lp(zpath)):
            os.remove(RF.lp(zpath))
        with zipfile.ZipFile(RF.lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(a.name, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(RF.lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
