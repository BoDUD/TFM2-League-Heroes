#!/usr/bin/env python3
"""Build norra_fx2_pack.zip: the effects Norra's Wild Rift kit needs that the first pack did not have (the user,
2026-10-26: 「你要参照手游的技能啊」 - the kit moved from TFT's to Wild Rift's after the first pack was drawn).

    python tools/art/pack_norra_fx2.py [--no-zip] [--out DIR]

The pack (C:/t/nr_work/fx/norra_fx2_pack, zipped into --out, default dist/norra_packs) holds PROMPTS.md (also written to
assets/source/norra/PROMPTS_FX2.md), design/norra_design.png and design/norra_size.png (pack_norra_fx.py's),
refs/first_delivery.png (the first pack as Codex delivered it: the same style, the same colours), refs/tft_fx_ref.png
(her TFT particle textures) and refs/wr_*.jpg (frames of the Wild Rift abilities from Riot's champion overview,
YouTube K2W95xf2wfc: the trinkets, Journey to Nowhere, Threads of Homecoming, Portalpalooza!; local only).
The effects are the views tools/kit/build_norra.py binds that the first delivery has no picture for: view_effects
p_trinkets, p_burst, w_in, w_lock, w_out, e_threads, t_hit, r_rift, r_yarn, r_hit; view_buffs t_mark, r_slow; and the
three skill icons. a_bolt, a_hit, q_bolt (the first pack's q_ball), q_blast and q_hit stay as delivered.
Red side: every picture here is upright and symmetric left to right (the client never mirrors an effect picture).
"""
import argparse
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_fx as RF  # noqa: E402
import pack_norra_fx as F  # noqa: E402

TMP = F.TMP
VIDEO = F.VIDEO
DOC = os.path.join(ROOT, "assets", "source", "norra", "PROMPTS_FX2.md")
FIRST = os.path.join(ROOT, "assets", "source", "norra", "codex_fx", "norra_fx", "fx-overview.png")
NAME = "norra_fx2_pack"

YARN = "#FFFFFF, #FFE8F4, #FF9CCB, #F05A9E, #8FF0F0, #44C8D2, #FFD95A"   # her yarn: pink, teal and gold strands
CRYSTAL = "#FFFFFF, #F4E6FF, #C9A2FF, #9A62F0, #6A34D0"                  # a trinket's violet memory glow
YA = f"a yarn ramp ({YARN})"
CR = f"a violet memory-crystal ramp ({CRYSTAL})"
GO, PO, PI = F.GO, F.PO, F.PI
LEAD, LR, CENTER, row = F.LEAD, F.LR, F.CENTER, F.row
MAGIC = ("everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, "
         "little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon "
         "beams, no realistic fire or smoke")
TARGET = F.TARGET
GROUND_E = F.GROUND_E

# name, title (zh), binding, size (game px), description (zh), ramps, effect, layout
FX = [
    # ---- passive: Beloved Trinkets
    ("p_trinkets", "寄情琐物：地上的琐物，4 帧循环", "view_effects `tft_norra_p_trinkets`（大表，落点，地面，z -1，不跟随；左右对称）",
     "44 × 20",
     "诺拉的技能落地时撒在地上的**琐物**（她带着的回忆小物件）：地上三个发着紫光的小东西——中间一个**小茶杯**，两边各一个**小水晶**（菱形、紫色发光），"
     "每个脚下一小圈淡紫色的光，几颗小星星一闪一闪（手游里是地上发紫光的小晶体，参考 `refs/wr_trinkets.jpg`）。**左右对称**，4 帧循环。",
     CR + ", " + GO + ", " + PI,
     "MEMORY TRINKETS ON THE GROUND, 4 looping frames, " + LR + ": three small keepsakes standing on the ground line 4 "
     "squares above the bottom: in the middle a tiny teacup (6 squares wide, white-and-violet porcelain with a gold rim "
     "and a 1-square near-black outline), at each side 14 squares out a small violet memory crystal (a diamond 4 wide and "
     "7 tall, glowing, a white core); under each a faint violet glow ellipse; frames 1-4 the crystals pulsing and little "
     "gold stars twinkling in turn above them. " + MAGIC + ".",
     row(4, 44, 20) + CENTER),
    ("p_burst", "寄情琐物：琐物飞到敌人身上爆开，5 帧", "view_effects `tft_norra_p_burst`（跟随目标，z 2；左右对称）", "18 × 24",
     "敌方英雄踩到琐物：一颗紫色的回忆水晶**从上面飞落到他身上**，啪地炸成一团**粉紫色的光泡**和几颗小星星（手游里琐物炸开是粉色的光球，参考 `refs/wr_trinkets.jpg` 第一格）。"
     "**左右对称**，5 帧。",
     CR + ", " + PI + ", " + GO,
     "A TRINKET STRIKES, 5 frames, " + LR + ", the unit hit stands in the lower middle, not drawn: 1 a small violet memory "
     "crystal (4 wide, 6 tall) high in the cell; 2 the crystal dropping, a short violet streak above it; 3 a pink-violet "
     "bubble burst 12 squares across at the middle; 4 the bubble 16 across, thin, little gold stars flying out at "
     "mirrored places; 5 fading sparkles. " + MAGIC + ".",
     row(5, 18, 24) + CENTER),
    # ---- passive: Journey to Nowhere (folded)
    ("w_in", "奇异旅程：开门吸走，5 帧", "view_effects `tft_norra_w_in`（目标脚下，z 2，不跟随；左右对称）", "30 × 46",
     "诺拉把贴近的敌人**放逐到异空间**：他脚下一圈**粉橙色的门环**亮起（地面上的椭圆，手游参考 `refs/wr_w_banish.jpg` 82 秒那格），门里紫色的漩涡往上卷，"
     "把人整个吸进去（人被放逐后看不见了，所以这几帧可以盖住人的位置）。**左右对称**，5 帧。",
     PO + ", " + PI + ", " + GO,
     "A PORTAL SWALLOWS THE UNIT, 5 frames, " + LR + ", the unit stands in the middle (36 squares tall) with its feet on "
     "the ground line 6 squares above the bottom; it vanishes into this picture: 1 a thin pink-orange ring 18 wide and 6 "
     "tall on the ground under it; 2 the ring 26 wide, a violet swirl filling it; 3 a violet whirl rising from the ring to "
     "36 squares tall, spiralling, covering the unit's place; 4 the whirl drawn down into the ring; 5 the ring flashing "
     "and shrinking. " + MAGIC + ".",
     row(5, 30, 46) + CENTER),
    ("w_lock", "奇异旅程：放逐中，门在原地转，4 帧循环", "view_effects `tft_norra_w_lock`（放逐的位置，z 2，不跟随；左右对称）", "24 × 12",
     "敌人被放逐的这段时间（1.5 秒），他原来站的地上留着一个**小小的紫色漩涡门**慢慢转，边上一圈粉橙色。**左右对称**，4 帧循环。",
     PO + ", " + PI,
     "A HUMMING PORTAL ON THE GROUND, 4 looping frames, " + LR + ", " + GROUND_E + ": a violet swirl ellipse 20 wide and 7 "
     "tall with a thin pink-orange rim; frames 1-4 the swirl turning and two tiny sparks orbiting. " + MAGIC + ".",
     row(4, 24, 12) + CENTER),
    ("w_out", "奇异旅程：被吐回来，4 帧", "view_effects `tft_norra_w_out`（放逐的位置，z 2，不跟随；左右对称）", "30 × 46",
     "放逐结束，门把人**吐回原地**：一道紫色的光柱从地上的门里冲起来、一闪，人重新出现（人会出现在中间，所以中间留空），然后门合上。"
     "**左右对称**，4 帧。",
     PO + ", " + PI + ", " + GO,
     "SPAT BACK OUT, 4 frames, " + LR + ", the unit reappears in the middle (36 squares tall, feet on the ground line 6 "
     "squares above the bottom; its place left mostly empty): 1 the violet ground ring 24 wide flashing white; 2 a ring "
     "of violet light rising round the unit's place to its waist, sparks; 3 the light fading upward, small gold stars; "
     "4 the ring on the ground shrinking to nothing. " + MAGIC + ".",
     row(4, 30, 46) + CENTER),
    # ---- skill2: Threads of Homecoming
    ("e_threads", "思乡线缕：两侧开门、射出线缕，6 帧", "view_effects `tft_norra_e_threads`（大表，目标位置，z 2，不跟随；左右对称）",
     "76 × 30",
     "E：目标的**左右两侧各开一个紫色的圆形门**（地上的椭圆，手游参考 `refs/wr_e_threads.jpg` 104 秒那格），短短一下后，"
     "**粉、青、金三色的毛线一样的线缕**从两个门里一起射出来，在中间交织穿过目标的位置，再慢慢散开。门之间 50 格左右。**左右对称**，6 帧。",
     PO + ", " + YA + ", " + GO,
     "THREADS BETWEEN TWO PORTALS, 6 frames, " + LR + ": the target stands in the middle (not drawn); 1 two violet portal "
     "ellipses (10 wide and 4 tall, a gold rim) opening on the ground 25 squares to the left and right of the middle; 2 the "
     "portals glowing, rising into upright swirls 10 tall; 3 bright yarn threads (pink, teal and gold strands, 1 square "
     "thick, slightly wavy) shooting from both portals toward the middle at waist height; 4 the threads meeting and "
     "crossing over the middle, a white spark where they cross; 5 the threads loosening into curls; 6 the portals closing, "
     "the threads fading. " + MAGIC + ".",
     row(6, 76, 30) + CENTER),
    ("t_hit", "思乡线缕：被线缕打中，3 帧", "view_effects `tft_norra_t_hit`（跟随目标，z 2；左右对称）", "14 × 14",
     "被线缕打中：一圈粉、青色的线头一甩、一下白光。**左右对称**，3 帧。",
     YA,
     "A THREAD LASH, 3 frames, " + LR + ": 1 a white spark 4 squares across; 2 pink and teal thread ends whipping out 10 "
     "across at mirrored places; 3 the threads curling and fading. " + MAGIC + ".",
     row(3, 14, 14) + CENTER),
    ("t_mark", "线缕印记：身上缠着线缕，6 帧循环", "view_buffs `tft_norra_t_mark`（跟随目标，z 3；左右对称）", "26 × 42",
     "被挂上**线缕**的敌人（减速、变大、更好被打中）：身上松松地缠着几圈**粉、青、金色的线**（腰和膝盖），头顶一个小小的**紫色线团**慢慢转"
     "（手游里被缠住的人身上裹着紫色的漩涡线，参考 `refs/wr_e_threads.jpg` 100 秒那格）。**身体位置留空**。**左右对称**，6 帧循环。",
     YA + ", " + PO,
     "WRAPPED IN THREADS, 6 looping frames, " + LR + ", " + TARGET + ": two loose loops of yarn thread round the unit "
     "(pink, teal and gold strands, 1 square thick) - one at its waist 24 wide and 6 tall, one at its knees 20 wide - "
     "seen slightly from above (their back halves behind the unit's place), and a small violet yarn ball 5 squares across "
     "with a loose end floating over its head; frames 1-6 the loops slowly turning round and the ball bobbing. The middle "
     "(the body) left empty. " + MAGIC + ".",
     row(6, 26, 42) + CENTER),
    # ---- ult: Portalpalooza!
    ("r_rift", "传送门欢腾！：地上的大裂隙，6 帧循环", "view_effects `tft_norra_r_rift`（大表，落点，地面，z -2，不跟随；左右对称）",
     "76 × 28",
     "大招：目标脚下展开一个**巨大的粉紫色圆形裂隙**（地上的椭圆，横 70 格、纵 24 格）：一圈粉紫色发光的边，边上有金色的小花纹，里面淡淡的紫色漩涡，"
     "几颗小星星往上飘（手游参考 `refs/wr_r_rift.jpg`：整个圈子很大、粉紫色）。**左右对称**，6 帧循环。",
     PO + ", " + PI + ", " + GO,
     "A GREAT RIFT ON THE GROUND, 6 looping frames, " + LR + ", " + GROUND_E + ": a big ring 70 squares wide and 24 tall: "
     "its rim 2 squares thick, glowing pink-violet with small gold filigree curls along it, inside a faint violet swirl "
     "(a few thin curved streaks, mostly see-through - units stand on it); frames 1-6 the swirl slowly turning, the rim's "
     "glow running round it, little stars rising at mirrored places. Frames MUST fill 70 squares across. " + MAGIC + ".",
     row(6, 76, 28) + CENTER),
    ("r_yarn", "传送门欢腾！：一波毛线球，6 帧", "view_effects `tft_norra_r_yarn`（大表，落点，z 2，不跟随；左右对称）", "76 × 40",
     "每一波：**两个毛线球**（一个粉色、一个金黄色，都拖着一根线）从裂隙的**左右两头**滚着飞进来，在中间撞到一起，炸开成一团毛茸茸的线和小星星"
     "（手游参考 `refs/wr_r_rift.jpg` 118、122、128 秒那几格：粉色和金色的球横穿裂隙）。为了左右对称，两个球大小、位置对称（颜色可以一粉一金对称摆）。"
     "**左右对称**，6 帧。",
     YA + ", " + PI + ", " + GO,
     "TWO YARN BALLS CROSS THE RIFT, 6 frames, " + LR + ": the balls fly at waist height (the middle of the cell's lower "
     "half): 1 two yarn balls 6 squares across (wound pink and gold strands, a few loose loops) at the far left and right "
     "edges, each trailing a thin thread; 2 the balls a third of the way in, spinning, the threads trailing behind them; 3 "
     "the balls two thirds in; 4 the balls meeting in the middle with a white-pink flash 12 across; 5 a fluffy burst of "
     "yarn curls and little gold stars 24 across; 6 the curls drifting down and fading. " + MAGIC + ".",
     row(6, 76, 40) + CENTER),
    ("r_hit", "传送门欢腾！：被毛线球砸中，4 帧", "view_effects `tft_norra_r_hit`（跟随目标，z 2；左右对称）", "16 × 16",
     "被毛线球砸中：一团粉金色的毛线炸开、几个线头乱飞。**左右对称**，4 帧。",
     YA + ", " + PI,
     "A YARN BALL HIT, 4 frames, " + LR + ": 1 a pink-gold yarn ball 6 squares across in the middle; 2 the ball bursting "
     "into loose curls 12 across with a white flash; 3 the curls flying out at mirrored places; 4 fading curls. " + MAGIC
     + ".",
     row(4, 16, 16) + CENTER),
    ("r_slow", "传送门欢腾！：被缠住减速，4 帧循环", "view_buffs `tft_norra_r_slow`（跟随，脚下，z 3；左右对称）", "22 × 10",
     "被第一个毛线球打中、减速 80% 的那一下：脚下缠着一团乱糟糟的**粉、青色毛线**。**左右对称**，4 帧循环。",
     YA,
     "TANGLED FEET, 4 looping frames, " + LR + ", " + GROUND_E + ": a messy tangle of pink and teal yarn round the unit's "
     "feet 20 wide and 6 tall, a few loose ends; frames 1-4 the loose ends wiggling. " + MAGIC + ".",
     row(4, 22, 10) + CENTER),
]
ICONS = [
    ("icon_skill", "技能 1 图标「回忆涌现」", "a glowing violet memory orb wrapped in a gold filigree ring, little pink stars streaming from it "
     "to the right, on a deep violet background"),
    ("icon_skill2", "技能 2 图标「思乡线缕」", "two small violet portals at the left and right with bright pink, teal and gold threads crossing "
     "between them, on a deep violet background"),
    ("icon_ult", "大招图标「传送门欢腾！」", "a big pink-violet ring rift seen from above with two yarn balls (one pink, one gold) rolling "
     "across it, on a deep violet background"),
]
BIG_FX = ["p_trinkets", "e_threads", "r_rift", "r_yarn"]


def document(shape):
    h, w = shape[:2]
    L = []
    a = L.append
    a("# 诺拉：补充特效（给 Codex 的提示词，第 3 步补充）\n")
    a(f"> **这一份是 {len(FX)} 张特效图 + {len(ICONS)} 个技能图标。** 诺拉的技能改成了**英雄联盟手游**里她的技能（被动「寄情琐物」、Q「回忆涌现」、"
      "W「奇异旅程」、E「思乡线缕」、R「传送门欢腾！」），上一份特效里普攻的魔法弹、Q 的球和爆炸**继续用**，这一份只画新技能需要的画面。")
    a("> - **画风和颜色照你上一次的交付**（`refs/first_delivery.png`：金色花纹、紫色漩涡、粉金小星星，硬边像素、没有柔光），"
      "样子照手游（`refs/wr_*.jpg` 是手游官方技能介绍视频的截图：琐物、奇异旅程、思乡线缕、传送门欢腾！）。")
    a(f"> - 诺拉在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），{h} 格高、{w} 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素）。"
      "大小对照 `design/norra_size.png`（诺拉缩到游戏大小、放大 4 倍，红线是地面，右边是原版斗士）。")
    a("> - **特效要亮**；**光、门、线、星星没有黑描边**；**只有茶杯（`p_trinkets`）有 1 格近黑描边**。")
    a("> - **围着人的画面只画外圈、脚下、头上，身体位置留空**（`w_in` 例外：人被放逐时看不见，可以盖住）。")
    a("> - **所有画面严格左右对称**（逐格对称：这些画面在红色方不会镜像），都是**正着**的画面（游戏不会转它们）。")
    a("> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `norra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、"
      "逐格左右对称——Claude 直接用这一份切格导入）。**量画面大小时只量实心的形状，不要把柔光、光晕、零散噪点算进去**（上一次大招的门就因为光晕被缩小了），"
      "形状要填到每条写的大小。附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`；技能图标交付 `icons/norra_icon_*.png`"
      f"（64 × 64）。都放在 `outputs/{NAME.replace('_pack', '')}/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/{NAME}_done.zip`。"
      "**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。\n")
    a("## 技能方案（每张图用在哪里）\n")
    a("| 技能位 | 内容 | 用到的图 |")
    a("|---|---|---|")
    a("| 被动「寄情琐物」 | 技能落地时在地上留下琐物，敌方英雄踩到，琐物飞到他身上爆开（伤害 + 线缕） | `p_trinkets` · `p_burst` |")
    a("| 被动里的 W「奇异旅程」 | 敌方英雄贴近时，诺拉在他脚下开门把他放逐 1.5 秒，然后吐回原地 | `w_in` · `w_lock` · `w_out` |")
    a("| 技能 1 =「回忆涌现」 | 蓄力后发射魔法弹，落点爆炸（上一份的球和爆炸）；挂线缕 | （已有） |")
    a("| 技能 2 =「思乡线缕」 | 目标两侧开门，线缕从两边射出、交织，伤害并挂线缕（减速、变大） | `e_threads` · `t_hit` · `t_mark` |")
    a("| 大招 =「传送门欢腾！」 | 目标脚下展开大裂隙，四波毛线球横穿，砸中的英雄减速 | `r_rift` · `r_yarn` · `r_hit` · `r_slow` |\n")
    a("## 所有特效图的规则\n")
    a("- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、门、线没有黑描边**（茶杯除外）。")
    a("- 颜色（按每条写的用）：")
    for label, ramp in (("金色花纹", F.GOLD), ("紫色漩涡", F.PORTAL), ("粉金星星", F.PINK), ("毛线", YARN), ("回忆水晶", CRYSTAL)):
        a(f"  - {label}：{'、'.join('`' + c + '`' for c in ramp.split(', '))}；")
    a("- 地面上的圈（琐物脚下的光、门、裂隙）是从斜上方看的椭圆（宽是高的 3 倍左右）。")
    a("- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。\n")
    a("---\n")
    a(f"## 特效（{len(FX)} 张）\n")
    for k, (name, title, _, _, zh, ramps, effect, layout) in enumerate(FX, 1):
        a(f"### {k}. `norra_fx_{name}.png`：{title}\n")
        a(zh + "\n")
        a("```text")
        a(LEAD.format(ramps=ramps))
        a(f"Effect: {effect}")
        a(f"Layout: {layout} {RF.TAIL}")
        a("```\n")
    a(f"## 技能图标（{len(ICONS)} 个，64 × 64）\n")
    for name, title, desc in ICONS:
        a(f"### `norra_{name}.png`：{title}\n")
        a("```text")
        a("A 64x64 pixel-art skill icon for a small tactics game, chunky square pixels, hard edges, no anti-aliasing, a "
          "1-pixel dark frame, bright and readable at small size: " + desc + ". Colours from the same violet, gold, pink "
          "and teal shades as the effects. No text.")
        a("```\n")
    a("---\n")
    a("## Claude 导入时的对应关系（给 Claude 看）\n")
    a("| 特效图 | 绑定 | 大小（游戏像素） |")
    a("|---|---|---|")
    for name, _, bind, size, *_ in FX:
        a(f"| `norra_fx_{name}` | {bind} | {size} |")
    a("")
    a(f"- 大表 `tft_norra_big`（{'、'.join(BIG_FX)}），其余在 `tft_norra_fx`；全部断言左右对称。图标 -> `tft/icons/tft_norra_skill` / `_skill2` / `_ult`。")
    a("- 用 `pixel_1x/` 切格（import_norra_fx 的做法）；和 `raw/` 原稿对照读回，形状小了就从 raw/ 按 process_norra_fx.reread 的办法放大读回。")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "norra_packs"), help="folder for the zip")
    a = ap.parse_args()
    RF.REF, RF.GROUPS = F.REF, F.GROUPS
    out = os.path.join(TMP, "fx", NAME)
    zpath = os.path.join(a.out, NAME + ".zip")
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("design", "refs"):
        os.makedirs(os.path.join(out, sub))
    F.design_sheet(os.path.join(out, "design", "norra_design.png"))
    shape = F.size_sheet(os.path.join(out, "design", "norra_size.png"))
    RF.ref_sheet(os.path.join(out, "refs", "tft_fx_ref.png"))
    shutil.copyfile(FIRST, os.path.join(out, "refs", "first_delivery.png"))
    for f in ("wr_trinkets.jpg", "wr_w_banish.jpg", "wr_e_threads.jpg", "wr_r_rift.jpg"):
        shutil.copyfile(os.path.join(VIDEO, f), os.path.join(out, "refs", f))
    doc = document(shape)
    for path in (os.path.join(out, "PROMPTS.md"), DOC):
        with open(F.lp(path), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc)
    with open(os.path.join(out, "fx_list.json"), "w", encoding="utf-8") as fh:
        json.dump([{"file": f"norra_fx_{x[0]}.png", "binding": x[2], "size": x[3], "symmetry": "left-right"} for x in FX]
                  + [{"file": f"icons/norra_{n}.png", "size": "64 x 64"} for n, _, _ in ICONS], fh, ensure_ascii=False,
                  indent=1)
    print(len(FX), "effects,", len(ICONS), "icons;", DOC, shape)
    if not a.no_zip:
        os.makedirs(F.lp(os.path.dirname(zpath)), exist_ok=True)
        if os.path.exists(F.lp(zpath)):
            os.remove(F.lp(zpath))
        with zipfile.ZipFile(F.lp(zpath), "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out):
                for fn in sorted(files):
                    p = os.path.join(root, fn)
                    z.write(p, os.path.join(NAME, os.path.relpath(p, out)).replace(os.sep, "/"))
        print(zpath, os.path.getsize(F.lp(zpath)) // 1024, "KB")


if __name__ == "__main__":
    main()
