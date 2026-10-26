#!/usr/bin/env python3
"""Write assets/source/alune/POSE_PROMPTS.md from pack_alune_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_alune_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_alune_poses as A  # noqa: E402

HEAD = """# 拉露恩：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 拉露恩的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，缩到游戏大小定稿：3/4 朝右，**侧坐在青铜月牙法杖上漂浮、双手抱胸**；银白短发、深蓝紫月牙角饰、额头发光月珠；紫色长袍、青色卷云纹、墨绿腰带、金边高领；青铜月牙 + 亮蓝刀刃 + 螺旋圆环 + 淡蓝月球）。
> - 请你画 **14 个姿势**（8 个动作 + 4 帧移动 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个拉露恩**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，已经按 Q 版大头放大、摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、手、月环、法杖照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。她的长裙比脚长，下摆飘在脚下面，最低点就是下摆。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 她的左臂**，**紫线 = 她的右臂**（哪只在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 左腿 / 右腿（大部分在长袍里，只决定长袍怎么走）；**金线 = 月牙法杖的杆**，**金圈 = 螺旋圆环中心的月球**；**灰框 = 头的位置**。`0_design_skeleton.png` 是待机的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **头一格一格照 `1_head.png` 画在灰框里**（角饰、银白短发、额头月珠、脸朝右前方）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、月环、法杖**不要盖住脸**（眼睛、月珠和嘴）；举起来的手从脸的旁边过去，可以挡住头发或角饰。
> - **月环和法杖**：螺旋圆环（里面有淡蓝月球）和青铜月牙都照定稿的样子和大小画，只照参考图换位置、换角度（平端着就画成扁的椭圆，竖着就是圆的）；站起来的姿势里月牙法杖照参考图在她身边或身后，死亡最后一张法杖碎成几个环落在地上。
> - **长短要数格子**：和定稿一样，手臂从肩膀到指尖约 12 格，头（含角饰）约 42 × 30 格，螺旋圆环直径约 22 格。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长**。手臂从宽袖里长出来，袖子跟着手。

## 14 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
"""

NEAR = {"a_wind": "紫（右臂）", "a_throw": "紫（右臂）", "a_catch": "紫（右臂）", "q_raise": "紫（右臂）",
        "q_call": "紫（右臂）", "e_bless": "橙（左臂）", "r_raise": "紫（右臂）", "r_call": "橙（左臂）",
        "run1": "抱胸", "run2": "抱胸", "run3": "抱胸", "run4": "抱胸", "d_fall": "橙（左臂）", "d_down": "橙（左臂）"}

PROMPT = """
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (the lowest point on y 1176) - a chibi MOON PRIESTESS SITTING SIDEWAYS on a big BRONZE CRESCENT-MOON GLAIVE with glowing blue blades, her arms crossed; silver-white bob hair, dark blue-violet CRESCENT HORN ornaments, a glowing white-blue MOON GEM on her forehead; a purple wide-sleeved robe with cyan swirls, a dark green sash, a gold-trimmed navy collar; inside the crescent a SPIRAL BLUE RING holding a pale blue MOON ORB; B its HEAD shown 8x (about 42 squares wide, 30 tall: the horns, the hair, the forehead gem, the face); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the hands, the ring and the glaive from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = her LEFT arm, PURPLE = her RIGHT arm (each line from the shoulder, the big dot = the hand), red / blue = her left / right leg (mostly hidden in the robe), GOLD line = the glaive's shaft, GOLD circle = the moon orb in the spiral ring, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the idle skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; the lowest point (the robe's hem, or the glaive) on y 1176.
COUNT THE SQUARES: the same proportions as image A - each arm about 12 squares from the shoulder to the fingertips, the head with the horns about 42 x 30, the spiral ring about 22 squares across; the body exactly where C shows it. Each arm from its wide sleeve along its line, bending at the elbow, never stretched; the robe flowing as in C. THE RING AND THE GLAIVE: the same spiral ring with its moon orb and the same bronze crescent with blue blades as in image A, only moved and turned as in C (held flat it is a flat ellipse, upright it is round). The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the horns, the silver-white hair, the glowing forehead gem, the face to the front-right) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand, ring or glaive covers the face (the eyes, the forehead gem and the mouth).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no moonshards, no moon, no moonlight, no sparkles, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = """
## 交回

- 每个姿势一张：`outputs/alune-poses/alune-pose-<名字>.png`（1254 × 1254、真透明背景、每格 12 px）；原始生成图原样放进 `outputs/alune-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **14 张都画完再交**，最后写 `outputs/alune-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/alune_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/alune/codex_poses/`，**先量 Codex 实际的格子**（不一定是 12 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、手不挡脸、袖子连着手、没有被压扁的身体）。
- 骨架包：`tools/art/pack_alune_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_alune_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        n = k + 2
        rows.append(f"| {n} | `alune-pose-{name}.png` | {clip} | {NEAR[name]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "alune", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
