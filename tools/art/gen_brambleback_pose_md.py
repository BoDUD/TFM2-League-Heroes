#!/usr/bin/env python3
"""Write assets/source/brambleback/POSE_PROMPTS.md from pack_brambleback_poses.POSES (the pose table and the per-pose
lines).

    python tools/art/gen_brambleback_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_brambleback_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 绯红印记树怪：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 树怪的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A 的原稿，按它自己 6 px 的格子读回，缩到游戏大小定稿（40 像素高，PPU 1.7），这里放大成每格 {A.PX} px：3/4 朝右，**四肢着地弓背蹲着的深红褐树皮巨兽**；**两条又长又粗的前臂，前爪是三根红橙大爪**；脖子上一圈**绿叶领子**；背上**弯曲的深色树枝（内侧红）和发光的红橙核心**；**楔子形树皮脑袋低在领子下，两只红眼（黄色亮芯）和额头的橙色螺旋**；树皮上发光的红色裂纹）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（9 个动作 + 8 帧奔跑 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个树怪**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：人立起来、爪子举过头顶、跳到空中、趴倒在地的时候，画面会变高、变宽或变矮，**但身子、头、手臂、爪子、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**三根红爪每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，头已经放大了一些——**姿势、两条手臂和爪子、两条腿、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型比定稿瘦，**身子的宽窄、树皮甲片、树叶领子和背上树枝的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两条前臂（肩膀到爪子）**，**红线 / 蓝线 = 两条后腿**；**灰框 = 头的位置**。**大多数姿势近处（画面右边、离我们近）的是青线前臂和蓝线后腿**（奔跑里有几帧近处的是红线后腿或粉线前臂，照骨架）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（楔子形树皮脑袋、两只红眼和黄色亮芯、额头的橙色螺旋、压在上面的绿叶）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 眼睛熄灭（暗红褐色，不发光）。
> - **手臂和爪子**：一直是定稿那两条粗长的树皮前臂和三根红橙大爪（前臂上的红色裂纹），**照骨架的粉线 / 青线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的手臂颜色正常、画在上面，远处的暗一档**。后腿同理（短粗，脚上小红爪，照红线 / 蓝线）。
> - **背上的树枝、红核和绿叶领子**每张都在，跟着身子倾斜；人立起来时在背上最高处，趴下时压低往前倾。
> - **奔跑 8 帧（run1–run8）是一整圈**：像大猩猩一样用前爪撑地往前跑，**粉线前爪抡一步、青线前爪抡一步**，两条后腿跟着交替；**每帧的身子、头、爪子都是同一个**，只有四肢按骨架换位置。**一定要看得出两只前爪在交替往前撑**。
> - **死亡（d_rear、d_down）**：d_down 整个趴平在地上；身子、爪子的大小不变，只是躺平。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest point on y {A.SOLE_Y}) - a HUNCHED FOUR-LIMBED BARK BEAST built like a gorilla, of DARK REDDISH-BROWN BARK PLATES with GLOWING RED VEINS: TWO LONG THICK FRONT ARMS each ending in THREE BIG RED-ORANGE CLAWS, short thick back legs with small red claws, a COLLAR OF GREEN LEAVES round its neck and shoulders, CURLING DARK BRANCHES with red insides and a GLOWING RED-ORANGE CORE on its back, a WEDGE-SHAPED BARK HEAD set low under the leaf collar with TWO RED EYES with yellow-hot centres and an ORANGE SPIRAL on its forehead; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two arms and claws, the two back legs, the body's and the head's angle from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two front arms (shoulder to claws), RED and BLUE = its two back legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y} (in the air only where the pose says so).
THE SAME BULK AS IMAGE A: the body, the head, the two LONG ARMS with their BIG CLAWS and the back legs exactly as big as in A in EVERY pose, also when it rears up, lifts its claws over its head, leaps or lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body or the claws to fit). Each front arm along its line (thick bark upper arm and forearm with red veins, the three big red-orange claws at the end), bending at the elbow, never stretched, never squashed, never thinner than in A; each back leg along its line (short and thick); the NEAR arm and leg in full tone and in front, the FAR ones a step darker. The leaf collar, the curling branches and the red core stay on its neck and back, tilting with the body.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the wedge of bark, the two red eyes with yellow centres, the orange forehead spiral, the leaves over it) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no fire, no burn, no red aura, no claw trails, no leap trail, no roar waves, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/brambleback-poses/brambleback-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/brambleback-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/brambleback-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/brambleback_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/brambleback/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（人立、举爪、跳起时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、两只红眼和螺旋还在、爪子和定稿一样大、手臂和腿没有被压扁或拉长、奔跑 8 帧两只前爪真的交替、远处的手臂和腿暗一档）。
- 骨架包：`tools/art/pack_brambleback_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；头放大 {A.HEAD_SCALE} 倍；奔跑按爪子和脚尖的高度量的一整圈取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_brambleback_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `brambleback-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "brambleback", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
