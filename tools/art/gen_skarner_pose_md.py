#!/usr/bin/env python3
"""Write assets/source/skarner/POSE_PROMPTS.md from pack_skarner_poses.POSES (the poses' table and their last lines).

    python tools/art/gen_skarner_pose_md.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_skarner_poses as K  # noqa: E402

HEAD = """# 上古领主 斯卡纳：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 斯卡纳的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A，按原样定稿：3/4 正面朝右的 Q 版水晶蝎子——又宽又厚的青绿 / 深石板蓝甲壳身体，甲片上橙红镶白边的部族花纹；身体最前面、甲壳下沿是一张**骨白色的骷髅小脸**（两只亮青色的小眼睛、几道橙色纹），上面罩着**银白色的头甲**；身前两只**很大的青绿钳子**（钳口内侧骨白色，橙白花纹）；背上**三根长长的分节尾巴**，末端三枚**青绿水晶毒刺 + 橙红核心**；身下**六条节肢腿**，深紫黑的钩爪）。`2b_rock.png` 是同一个他把**灰绿色的大巨石**举在尾巴上（第 0 步的 B）。
> - 英雄联盟里他用尾巴扎人、从地里掘出巨石举着再扔出去、蹦起来砸地、冲锋夹人、三根尾巴一起往前贯穿压制，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **{n} 个姿势**（{n_act} 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个斯卡纳**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：**绿线 = 身体**（从尾巴根到脸）；**三根青色系的线 = 三根尾巴**（青色 = 最后面那根、浅青 = 中间那根、钢蓝 = 最前面那根），每根末端的**三角块 = 毒刺**（尖朝三角的尖）；**橙线 = 近侧的钳子**（定稿里脸左下方那只），**紫线 = 远侧的钳子**（定稿里脸右边那只），线末端的大圆点 = 钳子尖；**红线 = 近侧的三条腿**，**蓝线 = 远侧的三条腿**（每条：腿根 → 膝 → 脚尖）；**灰框 = 头的位置**（银白头甲 + 骷髅脸）；**灰绿椭圆 = 巨石**（只在举石的几个姿势里）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：骨架就是按定稿量的，每一节都和定稿一样长——**三根尾巴从根到毒刺底分别约 {tr} / {tc} / {tl} 格**（毒刺另加约 9 格），**近侧钳子约 {cr} 格、远侧约 {cl} 格**，**腿很短：从腿根到脚尖约 {leg} 格**；头（头甲连脸）{hw} × {hh} 格。**尾巴、钳子、腿沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常的长腿，只能重画——请画完数一数），**不要把直的一截整块转个方向贴上去**；尾巴一节一节的甲片照定稿的大小，转弯处甲片跟着弯。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、银白头甲、骷髅脸、两只亮青眼睛一样高）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。尾巴、钳子**不要盖住脸**；尾巴从头上方经过时画在头**后面**。
> - **巨石**照 `2b_rock.png` 的巨石画（灰绿色多面体、几道裂缝），画在灰绿椭圆的位置、一样大；毒刺扎在巨石上抓住它。没有椭圆的姿势不画巨石。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的斯卡纳尾巴和腿都长；我们的是 Q 版：腿短、脸大，**照骨架的长短和位置画，不照原版的长短**。

## {n} 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
"""

PROMPT = """
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`；举石的姿势（q_dig、q_lift、t_wind）再加 `2b_rock.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (soles on y 1188) - a chibi CRYSTAL SCORPION: a broad thick armoured body of teal-green / dark slate-blue carapace plates with orange-red tribal markings edged in white; at the very front, under the edge of the carapace, a small BONE-WHITE SKULL-LIKE FACE with two small bright cyan eyes under a SILVER-WHITE HEAD PLATE; two BIG teal PINCERS in front (bone-white inner jaws, orange and white markings); THREE LONG SEGMENTED TAILS rising from his back, each ending in a big TEAL CRYSTAL STINGER with an orange-red core; SIX short jointed legs underneath with dark purple-black hooked claws; B its HEAD shown 8x (the silver head plate and the face); C a SKELETON on the same 1254 canvas and 9 px grid: GREEN = the body (the tails' root to the face), the THREE CYAN-ISH LINES = the three tails (cyan = the back one, light cyan = the middle one, steel blue = the front one), the TRIANGLE at the end of each = its stinger (pointing where the triangle points), ORANGE = the NEAR claw (below left of the face in A), PURPLE = the FAR claw (right of the face in A), the bigger dot at the end = the claw's tip, RED = the three NEAR legs, BLUE = the three FAR legs (each: the leg's root -> knee -> claw tip), GREY BOX = where the head goes, the GREY-GREEN ELLIPSE (only in some poses) = the BOULDER, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long limbs); E (if attached) the same skeleton drawn over image A, showing which line is which part; F (if attached) the same character holding the boulder - the look of the boulder.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions exactly as in image A - the tails about {tr}, {tc} and {tl} squares from the root to the stinger's base (each stinger about 9 more), the near claw about {cr} squares and the far claw about {cl}, the legs SHORT, about {leg} squares from the root to the claw tip. Lay the body along the green line with the same carapace plates and markings; each tail along its line, plate after plate of the same size as in image A, bending with the line, its crystal stinger on the triangle; each claw along its line (the same big pincer at its tip); each leg along its line, bending at the knee dot. Never stretch or shorten a tail, a claw or a leg, never paste a straight piece turned as one block. Where a tail passes the grey box it goes BEHIND the head. The near side in full tone, the far side a step darker. THE BOULDER (only where the ellipse is): the grey-green faceted boulder of image F on the ellipse, the same size, the stingers gripping it.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the silver head plate, the skull face to the front-right, both cyan eyes at the same height) - the same head in every pose, only moved, never turned, never redrawn as a profile. No tail or claw covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing (the crystals' highlights are bright squares, not a halo).
No effects (no shockwave, no dust, no rock debris, no charge trail, no motion lines, no enemies), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = """
## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1254×1254；**每格 9 px、对齐网格**；脚底在 y = 1188（蹦起来的 w_rear 离地，照骨架）。
- **数格子**：三根尾巴、两只钳子、六条腿和定稿一样长（尾巴约 {tr} / {tc} / {tl} 格 + 毒刺，钳子约 {cr} / {cl} 格，腿约 {leg} 格），没有被拉长或压短；关节处弯折，不是整块转过去。
- 头和 `1_head.png` 一格一格一样，没转、没变侧脸；尾巴、钳子没盖住脸。
- 颜色、描边、甲片花纹和定稿一样；举石的三张巨石和 `2b_rock.png` 一样；没有特效、没有敌人、没有地面和影子。
- 文件名：`outputs/skarner-poses/skarner-pose-<名字>.png`（名字见上表），原始生成图原样放进 `outputs/skarner-poses/raw/`；附一个 `generation-prompts.txt`；**最后**写 `outputs/skarner-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/skarner_poses_done.zip`。中间不要停，全部画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/skarner/codex_poses/`，先在 8 倍下量 Codex 实际的格子（读 raw 原稿），按它自己的格子读回，再把每张和骨架、定稿逐一比：尾巴 / 钳子 / 腿的长短、头的位置、脸、巨石。
- 骨架：`tools/art/pack_skarner_poses.py`（POSES 手调，长短来自 hd/idle.png；`--check DIR` 把骨架和英雄联盟那一帧并排）。
"""


def main():
    rig = K.Rig(r"D:\WeGameApps\lol")
    L = lambda c: round(sum(math.dist(p, q) for p, q in zip(rig.rest[c], rig.rest[c][1:])))
    v = dict(tr=L("tail_r"), tc=L("tail_c"), tl=L("tail_l"), cr=L("claw_r"), cl=L("claw_l"),
             leg=round(sum(L(c) for c in K.LEGS) / len(K.LEGS)), hw=K.HEAD[2] - K.HEAD[0], hh=K.HEAD[3] - K.HEAD[1],
             n=len(K.POSES), n_act=len(K.POSES) - 6)
    md = HEAD.format(**v)
    for k, (name, (_, zh, _, _)) in enumerate(K.POSES.items(), start=3):
        md += f"| {k} | `skarner-pose-{name}.png` | {zh} |\n"
    md += PROMPT.format(**v)
    for name, (_, _, en, _) in K.POSES.items():
        md += f"- {name}: `{en}`\n"
    md += TAIL.format(**v)
    path = os.path.join(ROOT, "assets", "source", "skarner", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(path, v)


if __name__ == "__main__":
    main()
