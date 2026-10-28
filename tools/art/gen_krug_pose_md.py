#!/usr/bin/env python3
"""Write assets/source/krug/POSE_PROMPTS.md from pack_krug_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_krug_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_krug_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 远古石甲虫：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 远古石甲虫的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，缩到游戏大小定稿：3/4 朝右，**四肢着地、驼着背**；浅土黄 / 灰绿的砂岩巨石背和发光的橙金裂缝；深灰褐带紫的石头身体、粗石臂和大石拳、短粗的后腿和石趾；右下方小小的深紫褐硬壳脸、两只琥珀橙眼睛、两只弯钳子）。
> - 请你画 **{N} 个姿势**（8 个动作 + 4 帧奔跑 + 3 帧死亡），**每个一张图**。待机、挨打、重生后的小石甲虫我从定稿本身来做，不用画。
> - **每张都是同一个石甲虫**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**脚底 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、石臂、后腿、巨石的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。定稿比模型画得宽一点（巨石和石臂更厚），**每个姿势都保持定稿的厚度**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到头），**橙线 / 紫线 = 两条前臂**（每条线第一个点是肩膀，**大圆点是石拳**；哪条在前面每个姿势写明了），红线 / 蓝线 = 两条后腿；**灰框 = 头（硬壳脸和两只钳子）的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上：**紫线是近处（画面右前方）的那条石臂**。
> - **头一格一格照 `1_head.png` 画在灰框里**（深紫褐的硬壳脸和中间的竖棱高光、两只琥珀橙眼睛、两只弯钳子）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；石拳**不要盖住眼睛**。`q_ball`（缩成石球）时头和四肢收进去，只露出一点钳子和一只眼睛；`d_crack`、`d_down` 碎掉时头埋在碎石里，但还是这个头。
> - **巨石背**：棱面、裂缝的走向照定稿（缩成石球时裂缝还在原来的地方，跟着巨石转）；`d_sink`、`d_crack`、`d_down` 照参考图裂开成几块，**每块都还是定稿里的砂岩颜色和橙金裂缝**，碎块之间露出发光的橙金色。

## {N} 个姿势

| 图 | 文件 | 片段 | 前面的石臂 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (his soles on y {A.SOLE_Y}) - a big hunched STONE BEAST on all fours: a HUGE ANGULAR SANDSTONE BOULDER for a back (pale khaki / sand / grey-green facets) split by GLOWING ORANGE-GOLD CRACKS; a dark grey-brown, slightly violet stone body; two THICK STONE FOREARMS ending in BIG STONE FISTS with blunt stone toes; two short thick hind legs; a SMALL dark violet-brown HARD SHELL FACE low at his front right with a pale ridge highlight, two glowing AMBER EYES and two CURVED DARK BROWN PINCERS; B his HEAD shown 8x (the shell face, the eyes, the pincers); C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the forearms, the hind legs and the boulder's angle from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the head), ORANGE and PURPLE = his two forearms (each line from the shoulder, the big dot = the stone fist), red / blue = his hind legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the boulder as big and as thick as in A, the forearms and the fists as thick as in A, the hind legs as short and thick; the body where C shows it, only as thick as A (A is a little wider than the 3D model). Each forearm along its line, bending at the elbow, never stretched, never thinner than in A; the hind legs along the red / blue lines. The boulder's facets and its glowing cracks as in A, turned with the body; where the pose breaks the boulder (images C of the death poses), each piece keeps A's sandstone colours and cracks, glowing orange-gold between the pieces. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the shell face with its pale ridge, both amber eyes, both curved pincers) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; no fist covers the eyes. Curled up into a ball, only a pincer and one eye show; broken in the rubble, the head lies in the pieces.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo (glow only as a brighter flat shade), no blur, no anti-aliasing.
No effects (no dust, no flying rocks apart from the boulder's own pieces, no shockwave, no sparkles, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/krug-poses/krug-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/krug-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，最后写 `outputs/krug-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/krug_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/krug/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、石拳不挡脸、石臂粗细不变、巨石大小不变、没有被压扁的身体）。
- 骨架包：`tools/art/pack_krug_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_krug_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        n = k + 2
        rows.append(f"| {n} | `krug-pose-{name}.png` | {clip} | {NEAR[name]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "krug", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


# which forearm is nearer the camera in each pose (pack_krug_poses' run prints it: L = orange, R = purple)
P_ = "紫（定稿里近处的那条）"
NEAR = {name: P_ for name in A.POSES}
NEAR.update({"d_sink": "橙", "d_crack": "橙", "d_down": "橙"})

if __name__ == "__main__":
    main()
