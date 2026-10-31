#!/usr/bin/env python3
"""Write assets/source/zippy/POSE_PROMPTS.md from pack_zippy_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_zippy_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_zippy_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 呲呲：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 呲呲的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按它自己 17 px 的格子读回，1:1 定稿，这里放大成每格 {A.PX} px：3/4 朝右，**两条腿站得笔直的小迅猛龙**；圆圆的橙褐色脑袋，头顶玫红尖刺，脸周围一圈黑色尖片，**半闭的大紫眼**；**喉咙到肚子一整块紫色围兜**；**脖子两侧垂着玫红长羽毛**；背上洋红马鞍（金边、金环、钢蓝小钩，没有骑手）；橙褐色的身子和腿，脚踝紫色绑带，黑色大弯爪；尾巴在左后方，上面一排粉色尖鳍）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（12 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个呲呲**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。**在空中的姿势（q_flip、q_kick、r_spring、r_open）也画在地面线上**，游戏里我再抬高。
> - **身体大小每张都和定稿一样**：腿踢起来、羽毛张开、身子蜷成球的时候，画面会变宽变矮，**但身子、头、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置，头已经放大了一些——**姿势、两条腿、尾巴、羽毛、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**红线 / 蓝线 = 两条腿（蓝线是近处的那条）**，**棕线 = 尾巴**，**粉线 / 青线 = 脖子两侧的玫红长羽毛（青线是近处的）**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（玫红尖刺、黑色尖片、半闭的紫眼、嘴线）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**只有嘴可以变**：`q_kick`、`r_open` 张大（嘴里深蓝色，露几颗白牙）；`d_down` 眼睛闭上；别的眼睛不动。
> - **腿**：一直是定稿那两条腿（橙褐色大腿、紫色脚踝绑带、黑色三趾大爪），**照骨架的红线 / 蓝线弯折**，不要拉长、不要压扁、不要比定稿细；**近处（蓝线）的腿颜色正常、画在上面，远处（红线）的腿暗一档**。
> - **羽毛球（e_ball、d_down）**：整个身子缩成一个圆球，外面是玫红长羽毛一缕一缕包着，露出一点马鞍金边和爪子；球的大小照参考图，**不要比定稿的身子小**。
> - **跑步 8 帧（run1–run8）是一整圈**：两条腿各在前面一次，run3 和 run7 是两腿交错的那一帧；**每帧的身子、头、尾巴都是同一个**（身子前倾、尾巴往后伸直），只有两条腿按骨架换位置。**一定要看得出两条腿在前后交换**：近处（蓝）的腿正常颜色、远处（红）的腿暗一档。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its soles on y {A.SOLE_Y}) - a small BIPEDAL RAPTOR standing upright on two legs: a ROUND ORANGE-BROWN HEAD with HOT-PINK SPIKES on top, a frill of BLACK SHARDS round the face, BIG HALF-CLOSED PURPLE EYES; one DEEP PURPLE BIB from under the eyes to the belly; LONG HOT-PINK FEATHER LOCKS hanging at both sides of the neck; a MAGENTA SADDLE with gold trim, a gold ring and steel-blue hooks on its back (no rider); orange-brown body and thighs, PURPLE ANKLE BANDS, big three-toed BLACK CLAWS; an orange-brown tail to the back left with a row of PINK SPINES; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the tail, the feathers, the body's and the head's angle from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), RED and BLUE = its two legs (BLUE is the NEAR one), BROWN = the tail, PINK and CYAN = the long feather locks at the two sides of the neck (CYAN is the NEAR one), GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y} (a pose in the air is drawn standing on that line too).
THE SAME BULK AS IMAGE A: the body, the head and the legs exactly as big as in A in EVERY pose, also when a leg kicks high, the feathers spread or the body curls into a ball (the picture simply grows wider or shorter - never shrink the body to fit). Each leg along its line (orange-brown thigh, purple ankle band, black three-toed claws), bending at the joints, never stretched, never squashed, never thinner than in A; the NEAR leg (blue line) in full tone and in front, the FAR leg (red line) a step darker. The tail along the brown line with its pink spines. The long pink feathers along the pink and cyan lines (hanging, swept back, spread like wings or wrapped round the body as C shows). The saddle stays on its back.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the pink spikes, the black shards, the half-closed purple eye, the mouth line) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; only the MOUTH may open where the pose says so (deep blue inside, a few small white fangs), and the eyes shut only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no wind, no spin trails, no motion lines, no dust, no shield, no impact, no stars, no glow), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/zippy-poses/zippy-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/zippy-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/zippy-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zippy_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/zippy/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（腿踢高、羽毛张开时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、眼睛还在、腿没有被压扁或拉长、身体大小不变、跑步 8 帧两条腿真的前后交换、远处的腿暗一档）。
- 骨架包：`tools/art/pack_zippy_poses.py`（骨架是它客户端模型自己的骨骼 Mount_*，按动作片段的那一帧投影；头放大 {A.HEAD_SCALE} 倍；跑步按 C:/t/zz_work/gait.py 量的一整圈取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_zippy_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `zippy-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "zippy", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
