#!/usr/bin/env python3
"""Write assets/source/idas/POSE_PROMPTS.md from pack_idas_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_idas_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_idas_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 艾达丝：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 艾达丝的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，按它自己的格子读回，1:1 定稿：**正侧面朝右、两条反关节腿直立**；有棱角的金色鳞甲、深棕色的胸腹和关节、青蓝宝石；龙头往前伸，**青蓝鬃冠、往后的细角、脸颊往下绕的月牙角、鼻梁上的小角、发光的青蓝眼睛**；**两只翅膀手臂**：前臂上一片金色的羽刃翼，手腕上是深灰三指爪；长尾巴往左后方伸，尾尖一片深灰紫刀刃）。
> - 请你画 **{N} 个姿势**（9 个动作 + 8 帧移动 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个艾达丝**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、两条腿、两只翅膀手臂、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，参考图里已经放大了；滑翔和倒地几帧的尾巴已经缩短到定稿的长度。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**紫线 = 近处的翅膀手臂，橙线 = 远处的**（大圆点是爪子；前臂上的金翼跟着这条手臂走，青线 / 粉线是翼根到翼尖的方向），**蓝线 = 近处的腿，红线 = 远处的**，**棕线 = 尾巴**，**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位（定稿比模型更往前弓着身子，骨架只看部位）。
> - **头一格一格照 `1_head.png` 画在灰框里**（鬃冠、细角、月牙角、鼻角、发光的眼睛、长吻）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**只有嘴可以变**：`q_breath`、`e_roar`、`r_burst` 张大嘴（里面深红色），其余闭嘴；眼睛和角不动。
> - **翅膀手臂**：一直是定稿那两只（金色前臂、金色羽刃翼、深灰三指爪），**长度和金翼的大小都和定稿一样，不要变长变大**。收着的姿势照定稿收在身前；`e_open`、`e_roar`、`r_burst` 照参考图向两边张开，金翼完全展开；`r_wrap`、`r_hold` 把两只翅膀收到身前、像盾一样挡住身体和半张脸。
> - **移动 8 帧（run1–run8）是一整个循环**：金铲铲里她是张开翅膀贴着地面往前滑翔的；身体每帧都是同一个，只有翅膀、两条腿和身体高低按参考图变；**近处的腿和翅膀（蓝、紫）颜色正常，远处的（红、橙）暗一档**。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, side view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (her feet on y {A.SOLE_Y}) - a GOLDEN DRAGON standing upright on two backward-bending legs: angular faceted gold scale plates, a dark brown chest, belly and joints, cyan gems; the head thrust forward with a CYAN FAN CREST, thin cyan horns swept back, a CRESCENT pale-cyan cheek horn bending under the jaw, a small snout horn and a GLOWING CYAN EYE; her arms are her WINGS: each gold forearm carries a GOLDEN FEATHER-BLADE WING and ends in a DARK GREY THREE-TALONED CLAW; a long gold tail reaching back to the left with a dark grey-violet BLADE at its tip; B her HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the two wing-arms, the body's and the head's angle from it - never its 3D shading; its head is already enlarged and its tail already shortened to image A's); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PURPLE = the NEAR wing-arm, ORANGE = the FAR wing-arm (the big dot = the claw; the golden wing rides on that forearm, the CYAN / PINK short line points from its root to its tip), BLUE = the NEAR leg, RED = the FAR leg, BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the arms and the legs as thick as in A, where C shows them. Each leg along its line, bending at its backward knee, never stretched, never thinner than in A. The WING-ARMS are always image A's two (gold forearms, golden feather-blade wings, dark grey claws) at image A's length, their wings never bigger than in A - held in front of her where C shows them folded, spread to the sides where C and D spread them. The tail along the brown line with its blade at the end. The near side in full tone, the far side (the far leg, the far wing-arm) a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the cyan crest, the swept-back horns, the crescent cheek horn, the snout horn, the glowing eye, the long snout) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; only the MOUTH may open wide where the pose says so (dark red inside).
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no golden breath, no shield, no glow, no coins, no sparks, no wind, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/idas-poses/idas-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/idas-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，最后写 `outputs/idas-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/idas_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/idas/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、金翼大小不变、腿没有被压扁或拉长、移动 8 帧是同一个身体、远处的腿暗一档）。
- 骨架包：`tools/art/pack_idas_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影，yaw {A.YAW}；头放大 HEAD_SCALE {A.HEAD_SCALE}，滑翔、倒地和 a_claw 的尾巴缩到 TAIL_SCALE {A.TAIL_SCALE}）；这份提示词由 `tools/art/gen_idas_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `idas-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "idas", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
