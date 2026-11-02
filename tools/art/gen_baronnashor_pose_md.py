#!/usr/bin/env python3
"""Write assets/source/baronnashor/POSE_PROMPTS.md from pack_baronnashor_poses.POSES (the pose table and the per-pose
lines).

    python tools/art/gen_baronnashor_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_baronnashor_poses as A  # noqa: E402

N = len(A.POSES)
# the parts nearer the camera, as measured from both models' joints (2026-11-03): in every pose the R_ small head
# (cyan), the R_ claw (orange) and the R_ leg (blue)
NEAR = "青线小头、橙线爪子、蓝线腿"

HEAD = f"""# 纳什男爵：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 纳什男爵的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（带腿的那张 `baronnashor-A.png`），按它自己 11 px 的格子读回，1:1 定稿，这里放大成每格 {A.PX} px：3/4 朝右，**虚空巨蛇**：S 形的紫色鳞甲身躯，正面一整条**青绿色分节腹甲**；**蓝紫硬甲头**、正中黄色菱形大眼和两边的小黄眼、**红色大嘴白牙**、**象牙白獠牙**；头后一圈**紫色鳍刺头冠、洋红鳍尖**；头两侧细臂上的**两只小蛇头**；身子下部两只**象牙白大弯爪**；**两条紫色短粗后腿、象牙色三趾脚**）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（10 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只纳什男爵**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：立起来、往下砸、侧身倒地的时候，画面会变高、变宽或变矮，**但头、身子、爪子、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置（头的位置看骨架图的灰框）——**身躯怎么弯、头往哪探、两只小头和两只爪子、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。**金铲铲的模型没有腿**（它是从地里钻出来的），所以参考图上**腿只有骨架线（红线 / 蓝线）**，模型身躯在腿那里的部分不用管：**腿照骨架线、照定稿的腿画**。模型的头比定稿小，**头和身子的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 身躯（屁股到头），紫线 = 下颌，**粉线 / 青线 = 两只小蛇头（连在细臂上）**，**黄线 / 橙线 = 两只大弯爪**，**红线 / 蓝线 = 两条腿**；**灰框 = 头的位置**。每个姿势都是**{NEAR}在近处**，画在上面、颜色正常；另一边的暗一档。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（蓝紫硬甲头、黄眼睛、红嘴白牙、白獠牙）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；`a_rear`、`a_bite`、`q_breath`、`r_rear`、`r_spit` 嘴张得更大（照紫线），牙齿还是那些牙齿。只有 `d_down` 眼睛熄灭（暗黄，不发光）。头冠的鳍刺跟着头走。
> - **爪子和腿**：一直是定稿那两只象牙白大弯爪和那两条紫色短腿、三趾脚，**照骨架线摆**，不要拉长、不要压扁、不要比定稿细；腿的膝盖照线弯。
> - **`e_dig`（在地下穿行）只画头冠的几根鳍刺尖露在地面线上面**，地面线以下什么都不画（土堆、地洞是特效，我后面画）。
> - **跑步 8 帧（run1–run8）是一整圈**：红线的腿迈一步、蓝线的腿迈一步；**每帧的头、身躯、爪子、小头都是同一个**，只有两条腿按骨架换位置、身子跟着微微起伏。**一定要看得出两条腿在交替迈步**。
> - **不画特效**：没有酸液、尖刺、土块、尘土、光。

## {N} 个姿势

| 图 | 文件 | 身体的片段 | 腿的片段 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its soles on y {A.SOLE_Y}) - a VOID SERPENT MONSTER: an S-curved body of PURPLE SCALE ARMOUR with ONE TEAL-GREEN SEGMENTED BELLY down its front, a hard BLUE-VIOLET ARMOURED HEAD with a YELLOW DIAMOND EYE in the middle and small yellow eyes beside it, a RED MOUTH with white teeth, IVORY TUSKS, a crown of PURPLE CREST FINS with MAGENTA TIPS behind the head, TWO SMALL SERPENT HEADS on thin arms beside the head, TWO BIG CURVED IVORY CLAWS low on the body, and TWO SHORT THICK PURPLE LEGS with ivory three-toed feet; B its HEAD shown 8x; C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE from it: how the body curves, where the head goes, the two small heads, the two claws, the body's and the head's angle - never its 3D shading; the model's head is smaller than A's: keep A's proportions). THE MODEL HAS NO LEGS (in its game it rises out of the ground): its legs are only the RED and BLUE lines drawn on C - draw A's own legs along them and ignore the model's body where the legs are; D the SKELETON of that pose, exactly over C: green = the body (hips to head), purple = the jaw, PINK and CYAN = the two small heads on their thin arms, YELLOW and ORANGE = the two big claws, RED and BLUE = its two legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the head, the crest, the body, the claws and the legs exactly as big as in A in EVERY pose, also when it rears up, slams down or lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body to fit). The claws along the yellow and orange lines and the small heads along the pink and cyan lines, never stretched, never squashed, never thinner than in A; each leg along its line, the knee bending as the line bends, the three-toed foot at its end; the NEAR parts (the CYAN small head, the ORANGE claw, the BLUE leg) in full tone and in front, the far ones a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the blue-violet armoured head, the yellow eyes, the red mouth and teeth, the ivory tusks) with the crest fins behind it - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the mouth opens wider only where the purple line says so; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no acid, no spikes, no rocks, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/baronnashor-poses/baronnashor-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/baronnashor-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/baronnashor-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/baronnashor_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/baronnashor/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（立起来、往下砸时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、黄眼睛和红嘴还在、爪子和定稿一样大、腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的爪子和腿暗一档）。
- 骨架包：`tools/art/pack_baronnashor_poses.py`（身体的骨架是纳什男爵客户端模型自己的骨骼，腿是海克斯霸龙的腿，两者在定稿的屁股（第 {A.HIP_ROW} 行）接上；灰框 = 定稿的头跟着 Head 关节走；跑步按海克斯霸龙量出来的一整圈取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_baronnashor_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, legs, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `baronnashor-pose-{name}.png` | {clip} | {legs or '（在地下）'} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "baronnashor", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
