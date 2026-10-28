#!/usr/bin/env python3
"""Write assets/source/aoshin/POSE_PROMPTS.md from pack_aoshin_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_aoshin_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_aoshin_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 敖兴：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 敖兴的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，缩到游戏大小定稿：3/4 朝右，**竖直悬浮在空中**；青绿鳞片的蛇形长身体、背上和尾巴上的浅青尖刺鬃毛、尾巴尖的青色风雾；金面具、竖起的金棱、两只弯角、发亮的眼睛、浅青胡子；深青胸甲金边、金护肩蓝宝石、棕铜护腕、蓝紫龙爪；两条短小的后腿）。
> - 请你画 **{N} 个姿势**（8 个动作 + 4 帧飞行 + 3 帧阵亡），**每个一张图**。待机和挨打我从定稿本身来做，不用画。
> - **每张都是同一条龙**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是最低点（**身体最低处 y = {A.SOLE_Y}**），网格从画布左上角对齐。他一直浮在空中，没有脚踩地。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、身体和尾巴的弯法、两只爪子、头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脖子（身体根部到头），**青线 = 身体和尾巴**（从身体根部一直到尾巴尖），**橙线 / 紫线 = 两条手臂**（每条线第一个点是肩膀，**大圆点是爪子**；哪条在前面每个姿势写明了），红线 / 蓝线 = 两条短后腿；**灰框 = 头（金面具、两只角、胡子）的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上：**紫线是近处（画面左前方、胸前）的那只爪子**。
> - **头一格一格照 `1_head.png` 画在灰框里**（金面具和中间竖起的金棱、发亮的眼睛、两只弯角、下面的浅青胡子）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；爪子**不要盖住眼睛**。`a_lunge`、`q_breath` 张嘴时只把面具下面的胡子和下巴往下张开一点，面具不变；`d_back` 仰面、`d_away` 转过身去时，头跟着身体转，但还是这个头的颜色和形状。
> - **身体和尾巴**：粗细照定稿（脖子和胸口最粗，往尾巴尖慢慢变细），背上的浅青尖刺鬃毛一路跟着身体弯；**尾巴尖的青色风雾**每帧都在，跟着尾巴飘。身体拉长的姿势（飞行、前扑）也**不要把身体画细**。

## {N} 个姿势

| 图 | 文件 | 片段 | 前面的爪子 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (his lowest point on y {A.SOLE_Y}) - a STORM DRAGON that HOVERS: a long SERPENT BODY in CYAN / TURQUOISE SCALES with a row of PALE CYAN SPIKES streaming back along it, a long tail ending in CYAN WISPS; a GOLD DRAGON MASK with a tall gold crest, two CURVED DARK HORNS, glowing pale eyes and a PALE CYAN BEARD below; a dark teal breastplate with gold trim, GOLD SHOULDER GUARDS with blue gems, bronze-brown bracers, two BLUE-VIOLET CLAWED HANDS; two short blue-violet hind legs; B his HEAD shown 8x (the mask, the eyes, the horns, the beard); C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, how the body and tail curve, the claws and the head's angle from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the neck (the root of the body to the head), CYAN = the body and tail (to the tail tip), ORANGE and PURPLE = his two arms (each line from the shoulder, the big dot = the claw), red / blue = his short hind legs, GREY BOX = where the head goes, the red horizontal line = his lowest point; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the neck and chest as thick as in A, the body tapering to the tail as in A (never thinner when the pose stretches it), the spikes along the back as big as in A, the tail wisps always there; the shoulder guards, breastplate and bracers as in A; each arm along its line, bending at the elbow, never stretched, never thinner than in A, the claws as big as in A; the hind legs along the red / blue lines. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the gold mask with its crest, the eyes, both horns, the beard) - the same head in every pose, only moved and tilted with the body, never redrawn; no claw covers the eyes. With the jaw open only the beard and the lower jaw drop a little, the mask stays.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo (glow only as a brighter flat shade), no blur, no anti-aliasing.
No effects (no lightning, no storm cloud, no breath, no wind lines, no sparkles, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/aoshin-poses/aoshin-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/aoshin-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，最后写 `outputs/aoshin-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/aoshin_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/aoshin/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、爪子不挡脸、身体粗细不变、尾巴风雾还在、没有被压扁的身体）。
- 骨架包：`tools/art/pack_aoshin_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_aoshin_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        n = k + 2
        rows.append(f"| {n} | `aoshin-pose-{name}.png` | {clip} | {NEAR[name]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "aoshin", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


# which arm is nearer the camera in each pose (pack_aoshin_poses' run prints it: L = orange, R = purple; checked on
# the renders - the design's near claw is the purple one)
P_ = "紫（定稿里近处的那只）"
NEAR = {name: P_ for name in A.POSES}
NEAR.update({"d_back": "橙", "d_away": "橙"})

if __name__ == "__main__":
    main()
