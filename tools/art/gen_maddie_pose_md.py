#!/usr/bin/env python3
"""Write assets/source/maddie/POSE_PROMPTS.md from pack_maddie_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_maddie_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_maddie_poses as A  # noqa: E402

HEAD = """# 麦迪：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 麦迪的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，缩到游戏大小定稿：3/4 朝右，**把粗长的海克斯步枪扛在近处的肩上、枪口朝后**；橙红短发齐刘海、灰蓝眼睛；歪戴的深色贝雷帽 + 金帽徽；白立领、金边宝蓝制服、胸前金徽章蓝宝石、金腰带；黑手套、淡紫灰马裤、黑长靴金护膝；步枪深藏青金箍、握把前一颗蓝水晶）。
> - 请你画 **15 个姿势**（9 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个麦迪**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 18 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、手、步枪照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的步枪贴图是乱的，**步枪的样子和颜色照定稿**。
> - **步枪的方向**：3D 模型是斜着朝镜头的，枪身常常被透视压短；我们的画面是 3/4 朝右，**端平开枪时枪口一律朝画面右边、整杆枪画全长**，后坐力把枪顶起来时枪口朝上（在头的左上方）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 她的左臂**，**紫线 = 她的右臂**（哪只在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 左腿 / 右腿；**金线 = 步枪**（两头），**金圈 = 枪口那一头**；**灰框 = 头的位置**。`0_design_skeleton.png` 是待机的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **「通缉令」（`e_point`）没有自己的动画**：参考图是她庆祝动作里伸手指人的那一帧，步枪在那段动画里是飘着的，已经藏掉了——**这一张她把步枪照定稿扛在近处的肩上**，远处的手伸出去指着右边。
> - **头一格一格照 `1_head.png` 画在灰框里**（歪戴的贝雷帽和金帽徽、橙红短发齐刘海、灰蓝眼睛、脸朝右前方；左边那一点金色和蓝色是头后面的步枪，不是头）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、步枪**不要盖住脸**（两只眼睛和嘴）；枪托抵肩、脸贴枪的姿势里，步枪从脸的下面过去。
> - **长短要数格子**：和定稿一样，手臂从肩膀到指尖约 16 格，头（含贝雷帽）约 28 × 20 格，步枪约 26 格长。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。

## 15 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
"""

NEAR = {name: "橙（左臂）" for name in A.POSES}
NEAR.update({"a_back": "紫（右臂）", "e_point": "紫（右臂）", "d_fall": "紫（右臂）"})

PROMPT = """
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 18 px squares (her soles on y 1176) - a young POLICEWOMAN SHARPSHOOTER with a big LONG HEXTECH RIFLE resting on her near shoulder, muzzle back; short orange-ginger bob with a fringe, grey-blue eyes; a dark beret tilted right with a gold badge; a white high collar, a royal blue uniform jacket with gold trim, a gold crest with a blue gem on her chest, a gold belt; black gloves, lavender-grey riding trousers, black knee boots with gold knee guards; the rifle dark navy with gold bands and a glowing BLUE CRYSTAL in front of the grip; B its HEAD shown 8x (about 28 squares wide, 20 tall: the beret, the hair, the face; the bit of gold and blue at its left edge is the rifle behind her head, not the head); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE and the hands from it - never its 3D shading; its rifle texture is broken: the rifle looks like image A's); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = her LEFT arm, PURPLE = her RIGHT arm (each line from the shoulder, the big dot = the hand), red / blue = her left / right leg, GOLD line = the rifle, GOLD ring = its MUZZLE end, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the idle skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 18 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - each arm about 16 squares from the shoulder to the fingertips, the head with the beret about 28 x 20, the rifle about 26 squares long, ALWAYS drawn at its full length (the 3D render foreshortens it): held level it points to the IMAGE RIGHT, kicked up by the recoil it points UP above the left of her head. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. The same rifle as image A (dark navy, gold bands, the blue crystal), only moved and turned. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the tilted beret with its gold badge, the orange bob and fringe, the grey-blue eyes, the face to the front-right) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or rifle covers the face (the eyes and the mouth): aiming with the stock at her shoulder, the rifle passes BELOW the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no muzzle flash, no bullets, no smoke, no sparkles, no motion lines, no target marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = """
## 交回

- 每个姿势一张：`outputs/maddie-poses/maddie-pose-<名字>.png`（1254 × 1254、真透明背景、每格 18 px）；原始生成图原样放进 `outputs/maddie-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **15 张都画完再交**，最后写 `outputs/maddie-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/maddie_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/maddie/codex_poses/`，**先量 Codex 实际的格子**（不一定是 18 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛和嘴还在、手和枪不挡脸、步枪不断、全长、没有被压扁的身体）。
- 骨架包：`tools/art/pack_maddie_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_maddie_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, zh, en)) in enumerate(A.POSES.items()):
        n = k + 2
        rows.append(f"| {n} | `maddie-pose-{name}.png` | {clip} | {NEAR[name]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "maddie", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
