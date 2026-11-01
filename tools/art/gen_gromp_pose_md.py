#!/usr/bin/env python3
"""Write assets/source/gromp/POSE_PROMPTS.md from pack_gromp_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_gromp_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_gromp_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 魔沼蛙：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 魔沼蛙的造型用户已经定稿。`0_design.png` 是你第 0 步交的**第一版 A**（raw/gromp-A-initial.png），按它自己 12 px 的格子读回、1:1 定稿，这里放大成每格 {A.PX} px。它的样子：
>   - 3/4 朝右、**蹲着的大胖蛤蟆**；
>   - 前面（右下）一个**又圆又鼓的橄榄褐大肚子**，上面有一块块甲片褶皱和深色圆斑；
>   - **橙色的扁头**压在肚子上方：隆起的眉骨、**发黄绿色光的眼睛**、嘴角两根**淡黄绿色獠牙**往上翘；
>   - 背和四肢是**深紫色的疙瘩皮**，四条短粗的蛙腿，前脚是张开的蛙爪；
>   - 背上一丛**紫色和蓝色的大蘑菇**（伞盖上有浅色圆点），头后面一个**蓝蘑菇**。
>   每个姿势都照它。
> - 请你画 **{N} 个姿势**（8 个动作 + 8 帧蛙跳 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只蛤蟆**：样子、颜色、大小全照 `0_design.png`。**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，网格从画布左上角对齐。红线是地面，**最低点 y = {A.SOLE_Y}**。
> - **身体大小每张都和定稿一样**：仰起身子、蛙跳伸长、翻倒、仰躺的时候，画面会变高、变宽或变矮，**但身子、头、腿不能因此画小**。按参考图的大小画，超出去就让它超出去，画布够大。**头每张都和定稿一样大**。
> - **只有两张肚子比定稿大**：`q_puff`（鼓起来）和 `r_belch`（鼓到最大，比 q_puff 还大）；`r_rear` 开始鼓一点。其他姿势的肚子和定稿一样大。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲 / 英雄联盟里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上，高度和位置都一样。死亡的两张是我把待机姿势往后翻倒做的（模型自己的死亡动作是直接沉进地里）。
>   - 姿势、四条腿、身体和头的角度**照参考图**。
>   - 长相和画法**照定稿**：像素格、描边、平涂，不要 3D 光影。
>   - 颜色分区（橄榄褐肚子、橙色扁头、深紫疙瘩皮、紫蓝蘑菇、淡黄獠牙）、头的大小**照定稿**。模型的头比定稿小，**以定稿为准**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：
>   - 绿线 = 脊柱（屁股到肩膀），**棕线 = 大肚子**（喉囊的骨头）。
>   - **橙线 = 头**（到上嘴唇），**黄线 = 下巴**。
>   - **红线 / 蓝线 = 两条前腿**，**粉线 / 青线 = 两条后腿**。
>   - **灰框 = 脸（眼睛、嘴、獠牙）的位置**。
>   - **近处（离我们近）的始终是蓝线前腿、青线后腿**。蛙跳时也是这两条在近处。
>   - `0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，用来看清哪条线是哪个部位。
> - **头照 `1_head.png` 一格一格地画**（定稿的头，放大 8 倍）。每个姿势都是这个头，只跟着骨架移动和倾斜，**不要重新设计**。
>   - **张嘴的姿势**（a_spit、q_belch、e_spit、r_belch、d_fall）只把下巴按黄线往下打开，嘴里画成**深粉紫色**，獠牙还在嘴角；上半个头（眉骨、眼睛）不变。**舌头都不伸出来**（参考图里伸出来的舌头不要画）。
>   - 只有 `d_down` 的眼睛熄灭（暗灰色，不发光）。
> - **腿**：一直是定稿那四条深紫色的短粗蛙腿和张开的蛙爪，**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细。**近处的腿颜色正常、画在上面，远处的暗一档**。
> - **背上的蘑菇**跟着身子走，大小、颜色、位置（相对身子）和定稿一样；仰躺时压在地上那一侧。
> - **蛙跳 8 帧（run1–run8）是一整跳**：蹲 → 蹬地 → 腾空伸长 → 落地 → 蹲回去。身子、头、蘑菇都是同一个，**后腿按骨架蹬直再收回**，**一定要看得出是在跳**。
> - **死亡（d_fall、d_down）**：d_fall 往后翻倒、肚子朝上前方；d_down 肚皮朝天仰躺、四条腿朝上；身子、头、蘑菇的大小不变。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest point on y {A.SOLE_Y}) - a HUGE SQUAT FAT TOAD crouching: a GIANT ROUND OLIVE-BROWN BELLY at the front (lower right) with plate-like folds and dark spots, a FLAT ORANGE HEAD resting on top of it with a ridged brow, GLOWING YELLOW-GREEN EYES and two PALE YELLOW-GREEN TUSKS curving up at the corners of the mouth, DARK PURPLE WARTY SKIN on the back and the four short thick frog legs with splayed frog hands, a cluster of BIG PURPLE AND BLUE MUSHROOMS with light spots on its back and one blue mushroom behind the head; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the body's and the head's angles from it - never its 3D shading, never its small head, never its tongue; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to shoulders), BROWN = the belly, ORANGE = the head (to the upper lip), YELLOW = the lower jaw, RED and BLUE = the two front legs, PINK and CYAN = the two hind legs, GREY BOX = where the face goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head and the legs exactly as big as in A in EVERY pose, also when it rears up, hops, tips over or lies on its back (the picture simply grows taller, wider or shorter - never shrink the body or the head to fit); the belly the same size as in A unless the pose line says it swells. Each leg along its line (a short thick dark purple frog leg, the splayed frog hand or foot at the end), bending at its joints, never stretched, never squashed, never thinner than in A; the NEAR legs (blue and cyan lines) in full tone and in front, the FAR ones a step darker. The mushrooms stay on its back, the same size and colours as in A.
THE HEAD: copy image B SQUARE FOR SQUARE onto the head line inside the grey box - the same head in every pose, only moved and tilted with it, never redrawn; where the pose opens the mouth, only the lower jaw swings down along the yellow line (dark pinkish purple inside, the tusks still at the corners); the TONGUE NEVER sticks out; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no spit, no bubbles, no slime, no poison cloud, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/gromp-poses/gromp-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）。
- 原始生成图原样放进 `outputs/gromp-poses/raw/`。
- `generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**。最后写 `outputs/gromp-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/gromp_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/gromp/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw。
- **每张按定稿的身体大小读**：仰起、腾空时 Codex 容易把身体画小（codex-fit-shrinks-bodies）。头对齐定稿的头（hd/idle.png）。
- 每帧放大 8 倍检查：
  - 头是定稿的头（眉骨、黄绿眼睛、獠牙），没有伸舌头；
  - 肚子只在 q_puff / r_rear / r_belch 变大；
  - 腿没有被压扁或拉长；
  - 蛙跳 8 帧真的是一跳；
  - 远处的腿暗一档。
- 骨架包：`tools/art/pack_gromp_poses.py`。骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影（金铲铲的 7 段 + 峡谷魔沼蛙的 spit / roar）；死亡两张是待机往后翻 45° / 160°；蛙跳按 0.53 s 一整跳均匀取 8 帧 {A.RUN_MS} ms。这份提示词由 `tools/art/gen_gromp_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, tilt, zh, en)) in enumerate(A.POSES.items()):
        src = clip + (f"（往后翻 {tilt}°）" if tilt else "")
        rows.append(f"| {k + 2} | `gromp-pose-{name}.png` | {src} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "gromp", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
