#!/usr/bin/env python3
"""Write assets/source/brock/POSE_PROMPTS.md from pack_brock_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_brock_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_brock_poses as A  # noqa: E402

N = len(A.POSES)
# the arm and leg nearer the camera in each pose, as pack_brock_poses prints them ("near R_leg R_arm")
NEAR = {"a_raise": "RR", "a_slam": "RR", "q_wind": "LL", "q_throw": "LR", "e_plant": "LR", "e_reach": "LL",
        "r_crouch": "LL", "r_leap": "LR", "r_air": "RR", "r_land": "RR", "run1": "RR", "run2": "RR", "run3": "LR",
        "run4": "RR", "run5": "RR", "run6": "RR", "run7": "RR", "run8": "RR", "d_fall": "RR", "d_down": "RR"}
LEG, ARM = {"L": "红", "R": "蓝"}, {"L": "粉", "R": "青"}

HEAD = f"""# 岩宝：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 岩宝的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（最终版），按它自己 14 px 的格子读回，1:1 定稿，两只眼睛我重画成了清楚的圆环，这里放大成每格 {A.PX} px：3/4 朝右，**深青灰板岩色的大块头岩石魔像**；**两只巨大的石拳**垂在身体两侧；棕色树根缠满肩膀、手臂和腰；肩上的亮绿叶丛和**小盆景树**、一根弯木刺；**小头缩在两肩之间：灰蓝色尖顶石兜帽、发光的橙色脸板、两只黄色圆环眼睛**；胸口紫色三角水晶纹章）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（10 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个岩宝**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：拳头举过头顶、两臂张开、蹲下、趴倒在地的时候，画面会变高、变宽或变矮，**但身子、头、拳头、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**两只巨拳每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置（模型的头很小，头的位置看骨架图的灰框）——**姿势、两只手臂和拳头、两条腿、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型比定稿瘦，**身子的宽窄、石块和拳头的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两条手臂（肩膀到拳头）**，**红线 / 蓝线 = 两条腿**；**灰框 = 头的位置**。**每张骨架图旁边的表里写了这个姿势哪条手臂、哪条腿离我们近**（近处的画在上面）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（灰蓝石兜帽、橙色脸板、两只黄色圆环眼睛）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 脸板和眼睛熄灭（暗橙褐色，不发光）。
> - **手臂和拳头**：一直是定稿那两条缠着树根的粗石臂和两只巨拳，**照骨架的粉线 / 青线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的手臂颜色正常、画在上面，远处的暗一档**。腿同理（短粗石墩，照红线 / 蓝线）。
> - **跑步 8 帧（run1–run8）是一整圈**：红线的腿迈一步、蓝线的腿迈一步；**每帧的身子、头、拳头都是同一个**，只有两条腿按骨架换位置、两只拳头跟着前后摆。**一定要看得出两条腿在交替迈步**。
> - **大招跳起的两帧（r_leap、r_air）也画在地面线上**（最低点 y = {A.SOLE_Y}），离地的高度我在游戏里加。
> - **扔石头（q_wind、q_throw）不要画石头**，石头是后面单独画的特效；拳头空着就好。
> - **死亡（d_fall、d_down）**：d_down 脸朝下趴倒在地；石块、拳头、盆景树的大小不变，只是躺平。

## {N} 个姿势

| 图 | 文件 | 片段 | 近处（画在上面） | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (his soles on y {A.SOLE_Y}) - a big chunky STONE GOLEM of dark slate-teal rock blocks: TWO HUGE BOULDER FISTS on thick stone arms, BROWN ROOTS wound round his shoulders, arms and waist, BRIGHT GREEN LEAF TUFTS and a SMALL BONSAI TREE on his shoulders, a curved bark thorn, a VIOLET TRIANGULAR CRYSTAL EMBLEM on the chest, short thick stone legs, a SMALL HEAD sunk between the shoulders: a pointed GREY-BLUE STONE HOOD round a glowing ORANGE FACE PLATE with TWO YELLOW RING EYES; B his HEAD shown 8x; C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two arms and fists, the two legs, the body's and the head's angle from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two arms (shoulder to fist), RED and BLUE = its two legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head, the two HUGE FISTS and the legs exactly as big as in A in EVERY pose, also when the fists go up over his head, the arms spread, he squats or he lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body or the fists to fit). Each arm along its line (thick root-wound stone upper arm and forearm, the huge boulder fist at the end), bending at the elbow, never stretched, never squashed, never thinner than in A; each leg along its line (short thick stone pillar); the NEAR arm and leg in full tone and in front, the FAR ones a step darker. The leaf tufts, the bonsai tree and the thorn stay on his shoulders; the roots and the violet chest emblem stay where they are on the body.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the grey-blue hood, the orange face plate, the two yellow ring eyes) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the face plate and the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no boulder in the hand, no roots from the ground, no shockwave, no cracks in the ground, no shield, no falling rocks, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/brock-poses/brock-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/brock-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/brock-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/brock_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/brock/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（拳头举高、两臂张开时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、两只圆环眼还在、拳头和定稿一样大、手臂和腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的手臂和腿暗一档）。
- 骨架包：`tools/art/pack_brock_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影；灰框 = 定稿的头跟着 Head 关节走；跑步按 C:/t/br_work/s/gait.py 量的一整圈取 8 帧 {A.RUN_MS} ms）；这份提示词由 `tools/art/gen_brock_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        near = f"{ARM[NEAR[name][1]]}线手臂、{LEG[NEAR[name][0]]}线腿"
        rows.append(f"| {k + 2} | `brock-pose-{name}.png` | {clip} | {near} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "brock", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
