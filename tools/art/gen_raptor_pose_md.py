#!/usr/bin/env python3
"""Write assets/source/raptor/POSE_PROMPTS.md from pack_raptor_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_raptor_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_raptor_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 深红锋喙鸟：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 锋喙鸟的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（加了红冠的那版），按它自己 11 px 的格子读回，1:1 定稿，这里放大成每格 {A.PX} px：3/4 朝右，**压低身子蹲着的圆胖鸟**；**红色背羽和尾羽**往后上方翘；**紫色尖刺鬃毛**围着脖子；**棕色骨质鸟头、厚厚的弯钩喙、两只发光的橙色眼睛**，嘴里透橙光；头顶一个红色尖冠；**两条短棕腿、深藏青弯钩大爪**）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（8 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只鸟**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：翅膀和羽冠张开、腾空、仰头、侧翻倒地的时候，画面会变高、变宽或变矮，**但身子、头、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**头每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，头已经放大了一些——**姿势、两条腿、翅膀、尾巴、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。**羽毛的颜色分区（红色背羽尾羽、紫色鬃毛）、头和喙的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头，最后一段是下喙），**棕线 = 尾巴**，**粉线 / 青线 = 两只小翅膀**，**红线 / 蓝线 = 两条腿**；**灰框 = 头的位置**。**近处（画面右边、离我们近）的始终是蓝线腿和青线翅膀**（跑步时两条腿前后交错，也还是蓝线那条在近处）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（棕色骨质鸟头、弯钩喙、两只橙色眼睛）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**张嘴的姿势**（a_jab、q_spread、e_land、r_call、d_fall）只把下喙按绿线最后一段往下打开，嘴里画橙光，上半个头不变。只有 `d_down` 眼睛熄灭（暗褐色，不发光）。
> - **腿**：一直是定稿那两条短棕腿和深藏青弯钩大爪，**照骨架的红线 / 蓝线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的腿颜色正常、画在上面，远处的暗一档**。翅膀平时收在身侧看不见，**只有 q_rear、q_spread 张开**（照粉线 / 青线，红紫尖羽）。
> - **跑步 8 帧（run1–run8）是一整圈**：近处的腿迈一步、远处的腿迈一步；**每帧的身子、头、羽毛都是同一个**，只有两条腿按骨架换位置、身子跟着上下一点点。**一定要看得出两条腿在交替迈步**。
> - **死亡（d_fall、d_down）**：d_down 翻倒侧躺在地上；身子、头、羽毛的大小不变，只是躺倒。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest point on y {A.SOLE_Y}) - a ROUND, PLUMP, LOW-CROUCHED BIRD-RAPTOR: CRIMSON / ORANGE-RED BACK AND TAIL FEATHERS sweeping back and up into a fan of spiky tail feathers, a RUFF OF DEEP PURPLE SPIKE FEATHERS round the neck, a BIG BROWN BONY BIRD HEAD with a THICK HOOKED BEAK and TWO GLOWING ORANGE EYES, an orange glow in the mouth, ONE RED POINT of crest on top of the head, TWO SHORT BROWN LEGS with BIG HOOKED DARK NAVY TALONS, two tiny wings folded and hidden at its sides; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the wings, the tail, the body's and the head's angle from it - never its 3D shading; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head, its last stretch the lower beak), BROWN = the tail, PINK and CYAN = its two little wings, RED and BLUE = its two legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head and the legs exactly as big as in A in EVERY pose, also when the wings and crest spread, it hops into the air, rears up or lies on its side (the picture simply grows taller, wider or shorter - never shrink the body or the head to fit). Each leg along its line (short brown bird leg, the big hooked dark navy talons at the end), bending at the knee, never stretched, never squashed, never thinner than in A; the NEAR leg in full tone and in front, the FAR one a step darker. The wings stay folded and hidden unless the pose says they open; open, each wing follows its line as a fan of red and purple pointed feathers. The red back and tail feathers and the purple ruff stay where they are on the body, as big pointed triangles.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the brown bony head, the hooked beak, the two orange eyes) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; where the pose opens the beak, only the lower beak swings down along the green line's last stretch with the orange glow inside; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no flying feathers, no little birds, no marks, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/raptor-poses/raptor-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/raptor-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/raptor-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/raptor_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/raptor/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（翅膀张开、腾空时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、两只橙眼还在、腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的腿暗一档）。
- 骨架包：`tools/art/pack_raptor_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；头放大 {A.HEAD_SCALE} 倍；跑步按 1.2 s 一整圈均匀取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_raptor_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `raptor-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "raptor", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
