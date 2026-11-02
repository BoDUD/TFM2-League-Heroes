#!/usr/bin/env python3
"""Write assets/source/riftherald/POSE_PROMPTS.md from pack_riftherald_poses.POSES (the pose table and the per-pose
lines).

    python tools/art/gen_riftherald_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_riftherald_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 峡谷先锋：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 峡谷先锋的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A 的第一稿 `riftherald-A-initial.png`，按它自己 8 px 的格子读回，缩到 44 像素高（PPU 2.0，88 格），这里每格 {A.PX} px：3/4 朝右，**弓着背缩在大圆顶甲壳下的虚空巨兽**；**蓝紫色晶体甲片拼成的大甲壳，每块甲片中间一个洋红小菱形，前沿一圈金色小尖刺**；**深紫色身体、两条短粗后腿、细长往上卷的尾巴**；**两只大蟹钳（深紫甲片、金色爪尖）**；脸藏在甲壳前沿下面：**两只发光的洋红眼睛、一排金色小尖牙、脸旁一根又大又弯的金色獠牙**）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（10 个动作 + 6 帧小跑 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只峡谷先锋**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**站在地上的姿势最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：站起来、翻身、转圈、躺下的时候，画面会变高、变宽或变矮，**但甲壳、身子、钳爪、腿、尾巴不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**脸每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，脸已经放大了一些——**姿势、两条腿、两只钳爪、尾巴、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的身子比定稿瘦长，**甲壳的大小和圆顶形状、钳爪的大小照定稿**。
> - **翻身的 e_flip 在空中**：参考图里离地多高就画多高，**不要落到红线上**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两只前臂（肩膀到钳爪）**，**红线 / 蓝线 = 两条后腿**，**黄线 = 尾巴**；**灰框 = 脸的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。前臂后面那两条小后臂藏在甲壳下面，骨架里没画，照定稿画就行。
> - **脸一格一格照 `1_head.png` 画在灰框里**（洋红眼睛、金色小尖牙、金獠牙）。每个姿势都是这一张脸，只跟着身体移动和倾斜，**不要转头、不要重新设计**。转圈（q_spin）和冲锋（e_flip、e_charge）时脸被身体挡住多少就挡住多少。只有 `d_down` 眼睛和甲壳上的洋红斑熄灭（暗紫色，不发光）。
> - **甲壳**：每张都是定稿那个大圆顶甲壳（甲片、洋红小菱形、金色尖刺），**跟着脊柱转**；转圈和冲锋时能看到它的背面——背面正中有一只**竖着的粉红裂眼**（第 0 步的附图 5）。
> - **腿和钳爪**：一直是定稿那两条短粗的后腿和两只大蟹钳，**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的腿和钳爪颜色正常、画在上面，远处的暗一档**。
> - **小跑 6 帧（run1–run6）是一整圈**：两条后腿各迈一步、各经过一次身体下面；**每帧的甲壳、脸、钳爪都是同一个**，只有身体高低、两条腿、钳爪和尾巴的摆动按参考图变。
> - **死亡（d_fall、d_down）**：d_down 翻倒在甲壳上；甲壳、身子的大小不变。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（脸）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest point on y {A.SOLE_Y}) - a hunched, heavy VOID BEAST under a HUGE DOMED SHELL of FACETED BLUE-VIOLET CRYSTAL PLATES, a small GLOWING MAGENTA DIAMOND in the middle of every plate, a row of small GOLDEN THORNS on the shell's front rim; a DARK PLUM body on TWO SHORT THICK HIND LEGS, a LONG THIN TAIL curling up behind; TWO BIG CRAB-LIKE PINCER CLAWS (dark violet plates, golden tips) in front; a small face under the shell's rim with TWO GLOWING MAGENTA EYES, a row of small golden fangs and a BIG CURVED GOLDEN TUSK beside it; B its FACE shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the two pincers, the tail, the body's and the head's angle from it - never its 3D shading; the model is leaner than A: keep A's big domed shell and big pincers); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two front arms (shoulder to pincer), RED and BLUE = its two hind legs, YELLOW = the tail, GREY BOX = where the face goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; standing poses with their lowest point on y {A.SOLE_Y}; a pose in the air exactly as high as in image C (NOT on the red line).
THE SAME BULK AS IMAGE A: the shell, the body, the pincers, the legs and the tail exactly as big as in A in EVERY pose, also when it rears up, spins, flips over or lies on its shell (the picture simply grows taller, wider or shorter - never shrink the body to fit). The shell turns with the spine; where its BACK shows, draw the VERTICAL PINK SLIT EYE in its middle. Each leg and arm along its line (short and thick, the pincers big), bending at the joints, never stretched, never squashed, never thinner than in A; the NEAR legs and pincer in full tone and in front, the FAR ones a step darker. The two small rear arms stay tucked under the shell as in A.
THE FACE: copy image B SQUARE FOR SQUARE into the grey box (the magenta eyes, the golden fangs, the golden tusk) - the same face in every pose, only moved and tilted with the body, never turned, never redrawn; hidden only where the body covers it; the eyes and the spots go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no shockwave, no void glow, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/riftherald-poses/riftherald-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/riftherald-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/riftherald-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/riftherald_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/riftherald/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（站起、翻身、转圈时 Codex 容易把身体画小：codex-fit-shrinks-bodies），脸对齐定稿的脸（hd/idle.png）；每帧 8 倍检查（脸不动、洋红眼睛和金獠牙还在、腿没有被压扁或拉长、远处的腿暗一档、翻身的姿势真的离地）；跑步量脚尖间距，一整圈两次经过都在（tft-run-full-cycle），腿要是变形就按定稿自己画（run-legs-caitlyn-way）。
- 骨架包：`tools/art/pack_riftherald_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；脸放大 {A.HEAD_SCALE} 倍）；这份提示词由 `tools/art/gen_riftherald_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `riftherald-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "riftherald", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
