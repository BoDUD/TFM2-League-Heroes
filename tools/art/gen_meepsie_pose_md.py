#!/usr/bin/env python3
"""Write assets/source/meepsie/POSE_PROMPTS.md from pack_meepsie_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_meepsie_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_meepsie_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 小木灵：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 小木灵的造型用户已经定稿：`0_design.png` 是你第 0 步画的 **A 第一稿**（`raw/meepsie-A-original.png`），按它自己 7 px 的格子读回，1:1 定稿（137 × 115 格），这里放大成每格 {A.PX} px。3/4 朝右，**没有脑袋的浅蓝白月岩巨像**：身上是带陨石坑的大石块；**两只比身体还宽的巨拳**；靛蓝色的短粗腿和前臂；紫色腰带和紫色石缝；头顶和背上长着**绿叶和紫蘑菇**；胸口高处有个**白边陨石坑驾驶舱，里面坐着绿色小木灵**（天线、两只大黑眼睛、小手）。每个姿势都照它画。
> - **你上一轮自己做的 42 帧动作（meepsie-motion）这次不用**：那一套是按 50 × 40 的粗图画的，跑步和大招起跳那几帧的身形和待机不一样。这一轮全部照 `0_design.png` 的格子和大小画。
> - 请你画 **{N} 个姿势**：10 个技能动作、8 帧走路、2 帧死亡，**每个姿势一张图**。待机和挨打我直接用定稿做，不用画。
> - **每张都是同一个小木灵**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**。画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：拳头举过头顶、两臂张开、跳在空中、跪倒的时候，画面会变高、变宽或变矮，**但身子、驾驶舱、拳头、腿都不能因此画小**。按参考图的大小画，超出去就让它超出去，画布够大。**两只巨拳每张都和定稿一样大。**
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上，高度和位置都对好了，驾驶舱里的小木灵已经放大了一些。**姿势照参考图**：两只手臂和拳头、两条腿、身体的角度。**长相和画法照定稿**：像素格、描边、平涂，不要 3D 光影。模型比定稿瘦，**身子的宽窄、石块和拳头的大小照定稿**。
> - **跳在空中的姿势（r_jump、r_air）也把最低点画在红线上**，离地的高度我自己加。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：
>   - 绿线 = 脊柱（屁股到身体顶部）；**黄线 = 驾驶舱里的小木灵**
>   - **粉线 / 青线 = 两条手臂**（肩膀到拳头）；**红线 / 蓝线 = 两条腿**
>   - **灰框 = 小木灵在哪里**（只标位置，比驾驶舱小）
>   - **青线手臂和蓝线腿是靠我们这一侧的**（画面右边）：颜色正常。粉线手臂和红线腿在另一侧，暗一档。哪个在上面挡住哪个，照参考图。
>   - `0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，用来看清哪条线是哪个部位。
> - **驾驶舱和小木灵一格一格照 `1_head.png` 画，大小和定稿一样（每格 {A.PX} px，不缩放），小木灵的中心对准灰框的中心**（白边陨石坑、紫色内壁、绿色小木灵、两只大黑眼睛和白高光、天线）。每个姿势都是这一个，只跟着身体移动和倾斜，**不要转方向、不要重新设计**。例外两个：
>   - `e_call` 小木灵两只小手举高欢呼，其他不变
>   - `d_down` 小木灵缩进驾驶舱里，看不见
> - **手臂和拳头**：一直是定稿那两条粗石臂和两只带陨石坑的巨拳，**照骨架的粉线 / 青线弯折**。不要拉长、不要压扁、不要比定稿细。腿也一样：靛蓝短粗石墩，照红线 / 蓝线。
> - **叶子和紫蘑菇一直长在身体顶部和背上**，跟着身体倾斜，不要掉下来，也不要变多变少。
> - **走路 8 帧（run1–run8）是一整圈**：近处的脚迈一步，远处的脚迈一步，中间两次两腿交错（run4、run8）。**每帧的身子、驾驶舱、拳头都是同一个**，只有两条腿按骨架换位置，两只拳头跟着一前一后摆。**一定要看得出两条腿在交替迈步。**
> - **不画任何特效**：Q 的震波、E 飞出去的小木灵、大招的冲击波，之后单独画。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（驾驶舱和小木灵）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its soles on y {A.SOLE_Y}) - a HEADLESS MOON-ROCK GOLEM: pale blue-white CRATERED rock boulders for the body and shoulders, TWO HUGE CRATERED BOULDER FISTS wider than its body, dark INDIGO short thick legs and forearm rocks, a PURPLE belt and purple seams, a cap of GREEN LEAVES and PURPLE MUSHROOMS on its top and back, and high on its chest a round WHITE-RIMMED CRATER COCKPIT (purple inside) where a small LIME-GREEN MEEP PILOT sits (an antenna, two big black eyes with white highlights, tiny hands); B its COCKPIT WITH THE PILOT shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two arms and fists, the two legs and the body's angle from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to the top of the body), YELLOW = the meep pilot, PINK and CYAN = its two arms (shoulder to fist), RED and BLUE = its two legs, GREY BOX = where the pilot sits (it only marks the place; it is smaller than the cockpit), the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y} (also when it is in the air).
THE SAME BULK AS IMAGE A: the body, the cockpit, the two HUGE FISTS and the legs exactly as big as in A in EVERY pose, also when the fists go up over it, the arms spread, it leaps or it kneels (the picture simply grows taller, wider or shorter - never shrink the body or the fists to fit). Each arm along its line (the cratered upper arm, the indigo forearm rock, the huge cratered boulder fist at the end), bending at the elbow, never stretched, never squashed, never thinner than in A; each leg along its line (a short thick indigo rock pillar). The CYAN arm and the BLUE leg are on the side nearer to us: full tone; the PINK arm and the RED leg are on the far side: a step darker; which one overlaps which as in image C. The leaves and purple mushrooms stay on its top and back, tilting with the body.
THE COCKPIT AND THE PILOT: copy image B SQUARE FOR SQUARE at image A's size (never scaled), the pilot centred on the grey box (the white crater rim, the purple inside, the lime-green meep with its antenna and its two big black eyes) - the same cockpit and pilot in every pose, only moved and tilted with the body, never turned, never redrawn; the pilot changes only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no shockwave, no dust, no cracks in the ground, no flying meeps, no stars, no heal sparkles, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/meepsie-poses/meepsie-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）。
- 原始生成图原样放进 `outputs/meepsie-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**，原图我自己按格子读。
- **{N} 张都画完再交**。最后写 `outputs/meepsie-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/meepsie_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/meepsie/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw。
- **每张按定稿的身体大小读**：拳头举高、两臂张开时 Codex 容易把身体画小（codex-fit-shrinks-bodies）。驾驶舱对齐定稿的驾驶舱（hd/idle.png）。
- 每帧 8 倍检查：驾驶舱和小木灵不动、两只大黑眼睛还在、拳头和定稿一样大、手臂和腿没有被压扁或拉长、走路 8 帧两条腿真的交替、远处的手臂和腿暗一档。
- 骨架包由 `tools/art/pack_meepsie_poses.py` 生成：骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；小木灵放大 {A.HEAD_SCALE} 倍；走路按 C:/t/mp_work/gait.py 量的一整圈取 8 帧 {A.RUN_MS} ms，含两次两腿交错。这份提示词由 `tools/art/gen_meepsie_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `meepsie-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "meepsie", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
