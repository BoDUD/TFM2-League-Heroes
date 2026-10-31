#!/usr/bin/env python3
"""Write assets/source/sentinel/POSE_PROMPTS.md from pack_sentinel_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_sentinel_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_sentinel_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 苍蓝雕纹魔像：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 魔像的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（修订版），按它自己 8 px 的格子读回，1:1 定稿，这里放大成每格 {A.PX} px：3/4 朝右，**弓着背的深青灰岩石巨人**；**两只比脑袋大得多的巨拳**垂在身前两侧；肩背上堆着浅灰绿大石块；**浅色八角石墩小脑袋半埋在两肩之间，深色缺口里一只青色独眼**；胸口 V 形青光、腰上青色带子、膝盖脚踝透青光；石块上刻着螺旋符文）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（8 个动作 + 8 帧走路 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个魔像**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：拳头举过头顶、两臂张开、趴倒在地的时候，画面会变高、变宽或变矮，**但身子、头、拳头、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**两只巨拳每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，头已经放大了一些——**姿势、两只手臂和拳头、两条腿、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型比定稿瘦，**身子的宽窄、石块和拳头的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两条手臂（肩膀到拳头）**，**红线 / 蓝线 = 两条腿**；**灰框 = 头的位置**。**大多数姿势近处（画面右边、离我们近）的是青线手臂和蓝线腿**，只有 `a_raise` 近处的是粉线手臂和红线腿。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（浅色石墩、深色缺口、青色独眼）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 独眼熄灭（暗青色，不发光）。
> - **手臂和拳头**：一直是定稿那两条粗石臂和两只巨拳（拳头上的螺旋符文），**照骨架的粉线 / 青线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的手臂颜色正常、画在上面，远处的暗一档**。腿同理（短粗石墩，照红线 / 蓝线）。
> - **走路 8 帧（run1–run8）是一整圈**：近处的脚迈一步、远处的脚迈一步；**每帧的身子、头、拳头都是同一个**，只有两条腿按骨架换位置、两只拳头跟着前后摆。**一定要看得出两条腿在交替迈步**。
> - **死亡（d_fall、d_down）**：d_down 趴倒在地、像一堆石头；石块、拳头的大小不变，只是躺平。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its soles on y {A.SOLE_Y}) - a HUNCHED STONE GOLEM of dark slate-teal rock blocks: TWO HUGE BOULDER FISTS much bigger than its head on thick stone arms, PALE SAGE BOULDERS piled on its shoulders and back, a SMALL PALE OCTAGONAL STONE HEAD half sunk between the shoulders with a DARK NOTCH holding ONE GLOWING CYAN EYE, a V of CYAN GLOW on the chest under the head, a GLOWING CYAN BAND round the waist, cyan in the seams of the knees and ankles, SPIRAL RUNES carved into the stones, short thick stone legs; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two arms and fists, the two legs, the body's and the head's angle from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two arms (shoulder to fist), RED and BLUE = its two legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head, the two HUGE FISTS and the legs exactly as big as in A in EVERY pose, also when the fists go up over its head, the arms spread or it lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body or the fists to fit). Each arm along its line (thick stone upper arm and forearm, the huge boulder fist with its spiral rune at the end), bending at the elbow, never stretched, never squashed, never thinner than in A; each leg along its line (short thick stone pillar); the NEAR arm and leg in full tone and in front, the FAR ones a step darker. The pale boulders stay on its shoulders and back; the cyan waist band and the V of cyan glow stay where they are on the body.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the pale stone stump, the dark notch, the one cyan eye) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eye goes dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no shockwave, no cracks in the ground, no shield, no rune circles, no flying rocks, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/sentinel-poses/sentinel-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/sentinel-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/sentinel-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sentinel_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sentinel/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（拳头举高、两臂张开时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、独眼还在、拳头和定稿一样大、手臂和腿没有被压扁或拉长、走路 8 帧两条腿真的交替、远处的手臂和腿暗一档）。
- 骨架包：`tools/art/pack_sentinel_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；头放大 {A.HEAD_SCALE} 倍；走路按 C:/t/bg_work/gait.py 量的一整圈取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_sentinel_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `sentinel-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "sentinel", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
