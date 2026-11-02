#!/usr/bin/env python3
"""Write assets/source/elderdragon/POSE_PROMPTS.md from pack_elderdragon_poses.POSES (the pose table and the per-pose
lines).

    python tools/art/gen_elderdragon_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_elderdragon_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 远古巨龙：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 远古巨龙的造型用户已经定稿（`0_design.png` 是你第 0 步画的**第一版 A**（细格子、脸最清楚的那版），按它自己约 7.5 px 的格子读回，1:1 定稿，这里放大成每格 {A.PX} px：3/4 朝右，**四条腿压低站着的翼龙**；**两只深紫色大蝙蝠翼**半张开往上举，翼骨和翼指尖是**青色发光的爪尖**；背上、尾巴上一排排**青色水晶尖刺**；**白色晶体鬃毛**盖住脖子和胸口；**深色尖嘴、两只往后弯的蓝色大角、发青光的嘴、青色眼睛**；尾巴往上卷，末端一把尖刺扇）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（8 个动作 + 8 帧飞行 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **远古巨龙移动时是低空飞行**（英雄联盟里的远古巨龙没有跑步动作），所以 8 帧「飞」是**原地振翅飞**的一整圈：翅膀从最高扇到最低再提回来。大招飞上天也用这 8 帧。
> - **每张都是同一条龙**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：翅膀张开举高、腾空、倒地的时候，画面会变高、变宽或变矮，**但身子、头、腿、翅膀不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**头每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是同一个 3D 模型做那个动作的那一帧**，摆在同一张画布、同一个格子上、同样的高度和位置，头已经放大了一些——**姿势、四条腿、两只翅膀、尾巴、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。**颜色分区（深紫翼膜、青色尖刺、白色鬃毛、蓝角）、头的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱和脖子（屁股到头，最后一段是下颚），**棕线 = 尾巴**，**粉线 / 青线 = 两只翅膀**（从肩膀到翼尖），**橙线 / 紫线 = 两条前腿**，**红线 / 蓝线 = 两条后腿**；**灰框 = 头的位置**。**近处（画面右边、离我们近）的始终是青线翅膀、紫线前腿、蓝线后腿**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（深色尖嘴、两只蓝色弯角、青色眼睛、发光的嘴、下巴的白晶刺）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**张嘴的姿势**（a_bite、q_rear、q_breath）只把下颚按绿线最后一段往下打开，嘴里画亮青光和白牙，上半个头不变。只有 `d_down` 眼睛和嘴的青光熄灭（暗灰蓝色，不发光）。
> - **腿**：一直是定稿那四条腿和黑色弯钩爪，**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的腿颜色正常、画在上面，远处的暗一档**。**翅膀**照粉线 / 青线张开或收拢，翼膜是大块深紫色平涂，翼骨深一档，每根翼指尖一个青色发光爪尖；近处的翅膀在前面、完整，远处的翅膀在身后、暗一档。
> - **飞行 8 帧（run1–run8）是一整圈振翅**：**每帧的身子、头、尾巴都是同一个**，只有两只翅膀按骨架上下扇、身子跟着上下一点点、四条腿收在身下。**一定要看得出翅膀在一下一下地扇**。
> - **死亡（d_fall、d_down）**：d_down 侧翻倒在地上；身子、头、翅膀的大小不变，只是躺倒。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest point on y {A.SOLE_Y}) - a FOUR-LEGGED WINGED DRAGON standing low: TWO HUGE DARK PURPLE BAT WINGS, every wing bone and finger ending in a GLOWING CYAN CLAW TIP, rows of GLOWING CYAN CRYSTAL SPIKES along its back and tail, a MANE OF WHITE CRYSTAL SHARDS over its neck and chest, a DARK POINTED BEAK-LIKE JAW, TWO BIG BLUE HORNS curving back, a GLOWING CYAN MOUTH, a CYAN EYE, four legs with BLACK HOOKED TALONS, the tail curled up ending in a fan of spikes; B its HEAD shown 8x; C a 3D RENDER of this same creature's game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the two wings, the tail, the body's and the head's angle from it - never its 3D shading; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine and neck (rump to head, its last stretch the lower jaw), BROWN = the tail, PINK and CYAN = its two wings (shoulder to wing tip), ORANGE and PURPLE = its two front legs, RED and BLUE = its two hind legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head, the legs and the wings exactly as big as in A in EVERY pose, also when the wings rise and spread, it leaps into the air, flies or lies on its side (the picture simply grows taller, wider or shorter - never shrink the body or the head to fit). Each leg along its line (lean dragon leg, the black hooked talons at the end), bending at its joints, never stretched, never squashed, never thinner than in A; the NEAR legs (purple and blue lines) in full tone and in front, the FAR ones a step darker. Each wing along its line: big flat dark purple membranes, darker lines for the bones, a glowing cyan claw tip on every finger; the NEAR wing (cyan line) whole and in front, the FAR wing behind the body a step darker. The cyan crystal spikes and the white crystal mane stay where they are on the body, as big pointed triangles.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the dark beak-like jaw, the two blue horns, the cyan eye, the glowing mouth, the white chin spikes) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; where the pose opens the jaws, only the lower jaw swings down along the green line's last stretch with the bright cyan glow and white fangs inside; the glow goes out only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no fire, no breath, no flames, no wind, no dust, no motion lines, no glow halo outside the body), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/elderdragon-poses/elderdragon-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/elderdragon-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/elderdragon-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/elderdragon_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/elderdragon/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（翅膀张开、腾空时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、眼睛和发光的嘴还在、腿没有被压扁或拉长、飞行 8 帧翅膀真的在扇、远处的腿和翅膀暗一档）。
- 骨架包：`tools/art/pack_elderdragon_poses.py`（骨架是英雄联盟远古巨龙的骨骼（金铲铲模型同一套），按动作片段的那一帧投影；头放大 {A.HEAD_SCALE} 倍；飞行按 2.33 s 一整圈振翅均匀取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_elderdragon_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `elderdragon-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "elderdragon", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
