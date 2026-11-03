#!/usr/bin/env python3
"""Write assets/source/mightymech/POSE_PROMPTS.md from pack_mightymech_poses.POSES (the pose table and the per-pose
lines).

    python tools/art/gen_mightymech_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_mightymech_poses as A  # noqa: E402

N = len(A.POSES)
# the leg and arm nearer the camera in each pose (leg, arm), as pack_mightymech_poses prints them ("near R_leg L_arm")
NEAR = {"a_up": "RR", "a_down": "LL", "q_brace": "RR", "e_crouch": "RR", "e_air": "RL", "e_land": "LL",
        "r_flare": "RR", "r_slash": "LL", "run1": "RL", "run2": "LL", "run3": "LL", "run4": "LL", "run5": "LL",
        "run6": "LL", "run7": "RL", "run8": "RL", "d_fall": "RR", "d_down": "RR"}
LEG, ARM = {"L": "红", "R": "蓝"}, {"L": "粉", "R": "青"}

HEAD = f"""# 超级机甲：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 超级机甲的造型用户已经定稿：`0_design.png` 是你第 0 步画的 **B（究极形态握剑）**，按它自己 7 px 的格子读回，再缩到游戏大小（80 格高）定稿，这里放大成每格 {A.PX} px。3/4 朝右，**红银黑三色的超级机器人**：小红头盔、**银色 V 形角**、银色面甲、**黄色眼罩**；宽厚的红色胸甲、黑色腰；两边**银色星形大护肩**（红色六边形宝石、圆形黄灯）；**银黑大方拳**；红色护腿；黑色鞭尾；背后**扇形红色刃翼**和两根尖刺；**双手握着一把比身体还长的红银巨剑**（红色剑格、**橙色发光圆核**、银色锯齿剑刃）。**它一直握着这把剑**。每个姿势都照它。
> - 请你画 **{N} 个姿势**（8 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一台超级机甲**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**身体最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：举剑、跳起、刃翼张开的时候，画面会变高、变宽或变矮，**但身子、头、拳头、腿、刃翼不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**巨剑每张都和定稿一样长、一样宽**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置（头的位置看骨架图的灰框）——**姿势、双手和剑、两条腿、尾巴、刃翼、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，**头、身子和剑的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两只手臂**，**红线 / 蓝线 = 两条腿**，棕线 = 尾巴，**黑线 = 巨剑（从剑柄到剑尖）**，**深红 / 橙色的放射细线 = 两边的刃翼**（每根线一片刃）；**灰框 = 头的位置**。每个姿势哪只手、哪条腿在近处见下表，**近处的画在上面、颜色正常，远处的暗一档**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（红头盔、银色 V 形角、银色面甲、黄眼罩）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 黄眼罩和黄灯熄灭（暗灰，不发光）。
> - **巨剑**：一直是定稿那把剑，**照黑线摆**（剑柄在两手之间，剑尖在黑线另一头），不要变短、变细；两只手都握在剑柄上，除非姿势另外说。**`q_brace`、`d_fall`、`d_down` 三张参考图里模型把剑丢在地上了，所以参考图里没画剑、骨架里也没有黑线**——按那一行的说明自己摆剑（`q_brace` 剑尖朝下立在身前、双手按着剑柄；`d_fall` 剑脱手往下掉；`d_down` 剑倒在身边地上）。
> - **刃翼**：平时像定稿那样扇形收在背后；`q_brace`、`r_flare` 照放射细线**往两边大大张开**，`e_air` 张开，`e_crouch` 往上竖。
> - **跑步 8 帧（run1–run8）是一整圈**：双手握剑竖在身前，红线的腿迈一步、蓝线的腿迈一步；**每帧的身子、头、剑、刃翼都是同一个**，只有两条腿按骨架换位置、尾巴跟着微微摆。**一定要看得出两条腿在交替迈步**。
> - **不画特效**：没有剑光、刀气、冲击波、护盾光圈、尘土、火花。

## {N} 个姿势

| 图 | 文件 | 片段 | 近处（画在上面） | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its soles on y {A.SOLE_Y}) - a RED, SILVER and BLACK SUPER ROBOT: a small red helmet with a SILVER V HORN, a silver face plate and a YELLOW VISOR; a broad red chest and a black waist; BIG SILVER STAR-SHAPED PAULDRONS with red hexagonal gems and round yellow lamps; big blocky silver-and-black fists; red armoured shins; a thin black whip tail; a fan of RED BLADE-WINGS and two tall spikes on its back; and in BOTH HANDS a GIANT RED-AND-SILVER SWORD longer than its body (a red cross-guard with a GLOWING ORANGE ROUND CORE, a silver serrated blade) - it ALWAYS holds this sword; B its HEAD shown 8x; C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the hands and the sword, the two legs, the tail, the blade-wings, the body's and the head's angle from it - never its 3D shading; the model's head is smaller than A's: keep A's proportions); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two arms, RED and BLUE = its two legs, BROWN = the tail, BLACK = the SWORD from the hilt to the tip, thin DARK RED and ORANGE spokes = the blade-wings of each side (one spoke a blade), GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; the lowest point of its body on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head, the fists, the legs, the blade-wings and the SWORD exactly as big as in A in EVERY pose, also when it raises the sword, leaps or spreads its wings (the picture simply grows taller, wider or shorter - never shrink the body or the sword to fit). The sword along the black line, its hilt between the hands and its tip at the line's other end, never shorter or thinner than in A; each arm along its line; each leg along its line; the tail along the brown line; the blade-wings fanned along their spokes; the NEAR arm and leg in full tone and in front, the FAR ones a step darker. Where the render shows no sword and the skeleton has no black line, place the sword as THE POSE line says.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the red helmet, the silver V horn, the silver face plate, the yellow visor) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the visor and the lamps go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no sword trail, no slash wave, no shockwave, no shield glow, no dust, no sparks, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/mightymech-poses/mightymech-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/mightymech-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读，上一轮你自己缩的 1x 图糊了）。
- **{N} 张都画完再交**，最后写 `outputs/mightymech-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/mightymech_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/mightymech/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（举剑、张开刃翼时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png 的 FACE_BOX）；每帧 8 倍检查（头不动、黄眼罩还在、剑和定稿一样长、腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的手和腿暗一档）。
- 骨架包：`tools/art/pack_mightymech_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影，整张左右翻转成定稿的朝向；灰框 = 定稿的头跟着 Head 关节走；跑步按量出来的一整圈取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_mightymech_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        near = f"{ARM[NEAR[name][1]]}线手臂、{LEG[NEAR[name][0]]}线腿"
        rows.append(f"| {k + 2} | `mightymech-pose-{name}.png` | {clip} | {near} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "mightymech", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
