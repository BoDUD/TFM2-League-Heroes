#!/usr/bin/env python3
"""Write assets/source/thex/POSE_PROMPTS.md from pack_thex_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_thex_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_thex_poses as A  # noqa: E402

N = len(A.POSES)
# the arm and leg nearer the camera in each pose, as pack_thex_poses prints them ("near R_leg R_arm"): every pose has
# the gatling (R, cyan) and the blue leg in front
NEAR = {name: "RR" for name in A.POSES}
LEG, ARM = {"L": "红", "R": "蓝"}, {"L": "粉（机械爪）", "R": "青（加特林）"}

HEAD = f"""# 海克斯霸龙：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 海克斯霸龙的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（第一版 `thex-A-initial`），按它自己 10 px 的格子读回，1:1 定稿，这里放大成每格 {A.PX} px：3/4 朝右，**机械霸王龙**：深藏青的机械身体盖着**铜色装甲板**、嵌着蓝色发光面板，背上一排**蓝色水晶尖刺**；**铜色恐龙头盔**（两根尖耳）、**蓝色面罩**、**白眼红眶**、钢灰紫的大下颌和白色三角牙；**近处的前爪是六管加特林**，远处是机械爪；两条鸟腿、铜色三趾爪脚；**长长的机械尾巴**）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（7 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只海克斯霸龙**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：背甲翻开、低头冲撞、侧身倒地的时候，画面会变高、变宽或变矮，**但身子、头、加特林、腿、尾巴不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**加特林每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置（头的位置看骨架图的灰框）——**姿势、加特林和爪子、两条腿、尾巴、背甲、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，**头、身子和加特林的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），紫线 = 下颌，**青线 = 加特林那只前爪**，**粉线 = 机械爪那只前爪**，**红线 / 蓝线 = 两条腿**，**棕线 = 尾巴**，**黄线 / 橙线 = 背上两块铜甲（导弹舱）**；**灰框 = 头的位置**。每个姿势都是**青线（加特林）和蓝线的腿在近处**，画在上面。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（铜色头盔、蓝色面罩、白眼红眶、下颌和牙齿）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；`e_bite` 和 `r_fire` 下颌张得更大（照紫线），牙齿还是那些牙齿。只有 `d_down` 面罩和蓝色面板熄灭（暗蓝灰，不发光）。
> - **背甲（导弹舱）**：平时两块铜甲合在背上（像定稿那样，背上是蓝色尖刺）；`q_fire`、`r_open`、`r_fire` 照黄线 / 橙线**往上翻开竖起**，像一对铜框翅膀，里面是蓝色面板（你第 0 步 B 图画的那样）。
> - **前爪和腿**：一直是定稿那只六管加特林和那只机械爪，**照青线 / 粉线摆**，不要拉长、不要压扁、不要比定稿细；**近处的颜色正常、画在上面，远处的暗一档**。鸟腿同理（照红线 / 蓝线，膝盖往后折）。
> - **跑步 8 帧（run1–run8）是一整圈**：红线的腿迈一步、蓝线的腿迈一步；**每帧的身子、头、加特林、尾巴都是同一个**，只有两条腿按骨架换位置、尾巴跟着微微摆。**一定要看得出两条腿在交替迈步**。
> - **不画特效**：没有子弹、枪口火光、导弹、激光、烟。

## {N} 个姿势

| 图 | 文件 | 片段 | 近处（画在上面） | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its soles on y {A.SOLE_Y}) - a MECHANICAL T-REX: a dark navy robot body under COPPER ARMOUR PLATES with glowing BLUE PANELS, a row of BLUE CRYSTAL SPIKES down its back, a COPPER DINOSAUR HELMET with two ear spikes, a BLUE VISOR, a white eye with a red rim, a big steel-lavender jaw with white triangle teeth, the NEAR forelimb a SIX-BARREL GATLING GUN, the far one a mechanical claw, two bird-like legs with copper three-toed clawed feet, a LONG ARMOURED TAIL; B its HEAD shown 8x; C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the gatling and the claw, the two legs, the tail, the back plates, the body's and the head's angle from it - never its 3D shading; the model's head is smaller than A's: keep A's proportions); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), purple = the jaw, CYAN = the gatling forelimb, PINK = the claw forelimb, RED and BLUE = its two legs, BROWN = the tail, YELLOW and ORANGE = its two back plates (the missile pods), GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head, the GATLING, the legs and the tail exactly as big as in A in EVERY pose, also when the back plates rise, it lunges low or it lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body to fit). The gatling and the claw along the cyan and pink lines, never stretched, never squashed, never thinner than in A; each leg along its line (a bird leg, the knee bending back); the tail along the brown line; the NEAR (cyan, blue) parts in full tone and in front, the FAR ones a step darker. The back plates lie closed on its back (as in A) unless the yellow and orange lines lift them: then they stand up open like a pair of copper-framed wings with blue panels inside.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the copper helmet, the blue visor, the eye, the jaw and teeth) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the jaw opens wider only where the purple line says so; the visor and the panels go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no bullets, no muzzle flash, no missiles, no laser, no smoke, no dust, no motion lines, no glow halo), no pilot, no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/thex-poses/thex-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/thex-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/thex-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/thex_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/thex/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（背甲翻开、低头冲撞时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、眼睛和面罩还在、加特林和定稿一样大、腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的爪子和腿暗一档）。
- 骨架包：`tools/art/pack_thex_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；灰框 = 定稿的头跟着 Head 关节走；跑步按量出来的一整圈取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_thex_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        near = f"{ARM[NEAR[name][1]]}、{LEG[NEAR[name][0]]}线腿"
        rows.append(f"| {k + 2} | `thex-pose-{name}.png` | {clip} | {near} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "thex", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
