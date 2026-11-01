#!/usr/bin/env python3
"""Write assets/source/scuttlecrab/POSE_PROMPTS.md from pack_scuttlecrab_poses.POSES (the pose table and the per-pose
lines).

    python tools/art/gen_scuttlecrab_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_scuttlecrab_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 迅捷蟹：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 迅捷蟹的造型用户已经定稿：`0_design.png` 是你第 0 步画的 **A 原稿**（`raw/scuttle-A-original.png`），按它自己 8 px 的格子读回，1:1 定稿（120 × 80 格），这里放大成每格 {A.PX} px。3/4 朝右，**背着一大块青绿色叠片甲壳的河蟹**：甲片一片片往后叠，边缘柠檬黄绿，后沿一排黄绿尖刺；正前方一块**灰色石头面甲**；面甲两边**两只发光的柠檬黄绿眼睛**（短眼柄）；**两根一节一节的深青长触角**往后弯，末端黄绿弯钩；甲壳下面一圈**深青色尖叶形的短腿和小钳子**。每个姿势都照它画。
> - **你上一轮自己缩的 46 × 32 小图这次不用**（太糊）。这一轮全部照 `0_design.png` 的格子和大小画。
> - 请你画 **{N} 个姿势**：3 帧普攻、2 帧技能1、3 帧技能2、3 帧大招、8 帧跑步、1 帧死亡，**每个姿势一张图**。待机和挨打我直接用定稿做，不用画。
> - **每张都是同一只迅捷蟹**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**。画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：站高、跳起、缩壳的时候，画面会变高、变宽或变矮，**但甲壳、面甲、眼睛、腿都不能因此画小**。按参考图的大小画，超出去就让它超出去，画布够大。**甲壳每张都和定稿一样大。**
> - **参考图（每个姿势一张 `*_ref.png`）是它自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上，高度和位置都对好了，脸已经放大了一些。**姿势照参考图**：腿、钳子、触角、甲壳的角度。**长相和画法照定稿**：像素格、描边、平涂，不要 3D 光影。模型的脸比定稿小，**脸、甲片和腿的大小照定稿**。
> - **跳在空中的姿势（a_hop）也把最低点画在红线上**，离地的高度我自己加。**例外：`r_up1`、`r_up2` 是从土里钻出来，红线以下在地下，红线以下的部分不画**（从红线处整齐切掉）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：
>   - 绿线 = 身体（甲壳中心）；**黄线 / 橙线 = 两根触角**
>   - **粉线 / 青线 = 两只钳子**；**红线 = 一边三条腿，蓝线 = 另一边三条腿**
>   - **灰框 = 脸在哪里**（石头面甲和两只眼睛）
>   - **蓝线的腿和青线的钳子是靠我们这一侧的**：颜色正常。红线的腿和粉线的钳子在另一侧，暗一档。哪个在上面挡住哪个，照参考图。
>   - `0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，用来看清哪条线是哪个部位。
> - **脸一格一格照 `1_head.png` 画，大小和定稿一样（每格 {A.PX} px，不缩放），脸的中心对准灰框的中心**（灰色石头面甲和裂纹、两只发光眼睛和眼柄）。每个姿势都是这一张脸，只跟着身体移动和倾斜，**不要转方向、不要重新设计**。例外：
>   - `e_shell` 缩进壳里，脸、腿、钳子都看不见，只剩甲壳（触角也收进去）
>   - `d_down` 缩在壳里，只有两根触角软软地瘫在地上，眼睛暗下去（看不见或变成暗绿）
> - **腿和钳子**：一直是定稿那些深青色尖叶形的短腿和小钳子，**照骨架的线弯折**。不要拉长、不要变细。**触角**：一直是定稿那两根一节一节的深青长条，末端黄绿弯钩，照黄线 / 橙线的形状弯。
> - **跑步 8 帧（run1–run8）是一整圈**：甲壳、脸、触角每帧都是同一个，只有腿按骨架换位置，甲壳跟着一颠一颠。**一定要看得出腿在飞快地倒腾。**
> - **不画任何特效**：舞蹈的冲击、神龛的水纹、护盾的光、钻地的土，之后单独画。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（脸）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest leg tips on y {A.SOLE_Y}) - a round RIVER CRAB under a BIG TEAL-GREEN SHELL of overlapping plates (lime-yellow plate edges, a row of lime spikes along the rear rim), a GREY STONE FACE PLATE at the front, TWO GLOWING LIME EYES on short dark stalks at its sides, TWO LONG SEGMENTED DARK TEAL ANTENNAE curving back over the shell with lime hooked tips, and a ring of SHORT DARK TEAL LEAF-SHAPED LEGS and two small claws under the shell; B its FACE (the stone face plate and the two eyes) shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE - the legs, the claws, the antennae and the shell's angle - from it, never its 3D shading; the model's face is smaller than A's: keep A's face and bulk); D the SKELETON of that pose, exactly over C: green = the body (the shell's centre), YELLOW and ORANGE = its two antennae, PINK and CYAN = its two claws, RED = the three legs of one side, BLUE = the three legs of the other side, GREY BOX = where the face is, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y} (also when it is in the air), unless the pose says it is climbing out of the earth.
THE SAME BULK AS IMAGE A: the shell, the face, the legs and the claws exactly as big as in A in EVERY pose, also when it stands up tall, hops or pulls into its shell (the picture simply grows taller, wider or shorter - never shrink the shell to fit). Each leg and claw along its line (dark teal pointed leaf-shaped plates), never stretched, never thinner than in A; each antenna along its line (a segmented dark teal strip with a lime hooked tip). The BLUE legs and the CYAN claw are on the side nearer to us: full tone; the RED legs and the PINK claw are on the far side: a step darker; which one overlaps which as in image C.
THE FACE: copy image B SQUARE FOR SQUARE at image A's size (never scaled), centred on the grey box (the grey stone face plate with its cracks, the two glowing lime eyes on their stalks) - the same face in every pose, only moved and tilted with the body, never turned, never redrawn; the face changes only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no shockwave, no water ring, no shield glow, no dirt or dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/scuttle-poses/scuttle-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）。
- 原始生成图原样放进 `outputs/scuttle-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**，原图我自己按格子读。
- **{N} 张都画完再交**。最后写 `outputs/scuttle-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/scuttle_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/scuttlecrab/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw。
- **每张按定稿的身体大小读**：站高、跳起时 Codex 容易把身体画小（codex-fit-shrinks-bodies）。脸对齐定稿的脸（hd/idle.png）。
- 每帧 8 倍检查：脸不动、两只眼睛还在、甲壳和定稿一样大、腿没有被压扁或拉长、跑步 8 帧腿真的在换、远处的腿暗一档、r_up1 / r_up2 在红线处切齐。
- 骨架包由 `tools/art/pack_scuttlecrab_poses.py` 生成：骨架是英雄联盟河蟹的骨骼（金铲铲的模型用同一套），按动作片段的那一帧投影；脸放大 {A.HEAD_SCALE} 倍；跑步取一整圈 8 帧 {A.RUN_MS} ms。这份提示词由 `tools/art/gen_scuttlecrab_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en, *_how)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `scuttle-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "scuttlecrab", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
