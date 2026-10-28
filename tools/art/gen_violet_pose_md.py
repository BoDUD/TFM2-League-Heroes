#!/usr/bin/env python3
"""Write assets/source/violet/POSE_PROMPTS.md from pack_violet_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_violet_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_violet_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 蔚奥莱：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 蔚奥莱的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，缩到游戏大小定稿：3/4 朝右，**格斗架势，两只大铁拳套举在胸前**（画面右边那只往前顶、在上，画面左边那只收在身前）；洋红色斜垂的头发、深棕上挑的眉毛、浅蓝眼睛；酒红短马甲、红兜帽、浅灰绿衬衫和胸前绷带、深棕腰带、深紫褐宽裤（近处大腿藏青补丁）、橄榄绿绑腿、深棕短靴；**两只拳套一样：蓝灰钢板的前臂、金黄方框的大拳头**）。
> - 请你画 **{N} 个姿势**（13 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个蔚奥莱**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**脚底 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、两只拳套在哪照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **铁拳套**：**两只手都戴**，样子、颜色、大小照定稿（每只拳头比她的头还大一点）；参考图里的拳套在 3D 里常被透视压扁、看着小，**画的时候保持定稿的大小**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 一只手臂、青线 = 另一只手臂**（哪只在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 两条腿；**两个金圈 = 两只拳套**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **头一格一格照 `1_head.png` 画在灰框里**（洋红色头发斜垂在远处的脸边、上挑的眉毛、两只浅蓝眼睛、脸朝右前方）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`d_down` 仰面倒地时头跟着身体放倒，但还是这个头）。拳套**不要盖住脸**（两只眼睛和嘴）：`q_upper` 往上勾的拳套在头的**前面（画面右上）**，`a_wind` / `q_coil` 举起的拳套在头的**后面（画面左上）**，脸都露出来。
> - **长短要数格子**：和定稿一样，头（含头发）约 28 × 27 格，每只拳套（连前臂）约 20 × 18 格，手臂从肩膀到拳头约 18 格。**手臂沿着骨架画，长短和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。她身材瘦，但拳套很大。
> - **跳起来的姿势**（`q_upper`、`r_air`）：参考图里最低的点已经放在地面线上，**照着画就行**，离地多高我在动画里再抬。

## {N} 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (her soles on y {A.SOLE_Y}) - a lean TEENAGE GIRL street fighter in a fighting stance: magenta-pink hair swooping over the far side of her face, dark brown brows tilted up, pale blue eyes; a short wine-red vest with a red hood behind the neck, a pale grey-green shirt with chest wraps, a dark brown belt, baggy dark purple-brown trousers with a navy patch, olive leg wraps, dark brown boots; on EACH hand a HUGE IRON GAUNTLET (blue-grey steel plates on the forearm, a square gold-yellow fist frame with dark rivets), both held up at her chest; B its HEAD shown 8x (about 28 squares wide, 27 tall: the hair, the brows, two eyes, the mouth); C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE and where both gauntlets are from it - never its 3D shading, and never its squashed small gauntlets); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = one arm, CYAN = the other arm (each line from the shoulder, the big dot = the hand), red / blue = her legs, the two GOLD rings = the two gauntlets, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her soles (or the lowest point) on y {A.SOLE_Y}.
COUNT THE SQUARES: the same proportions as image A - the head with the hair about 28 x 27, each gauntlet with its forearm about 20 x 18 (as BIG as in image A, whatever the 3D render shows), each arm about 18 squares from the shoulder to the fist, a slim body. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. Both gauntlets the same gauntlet as image A, only moved and turned. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the magenta hair over the far side of the face, the brows, both pale blue eyes, the mouth, the face to the front-right) - the same head in every pose, only moved (tilted with the body when she falls or lies down), never turned, never redrawn as a profile. No gauntlet covers the face (the eyes and the mouth).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no punch wind, no shockwave, no dust, no sparks, no lightning, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/violet-poses/violet-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/violet-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，中间不要停，最后写 `outputs/violet-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/violet_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/violet/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛和嘴还在、拳套不挡脸、两只拳套大小不变、没有被压扁的身体、腿不变形）。
- 骨架包：`tools/art/pack_violet_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_violet_pose_md.py` 生成。
"""

# the arm nearer the camera, as pack_violet_poses prints it for each pose (2026-10-28)
NEAR = {name: "青" for name in A.POSES}
NEAR.update({n: "橙" for n in ("a_punch", "a_back", "q_land", "run1", "run2", "run3", "run4", "d_fall")})


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        n = k + 2
        rows.append(f"| {n} | `violet-pose-{name}.png` | {clip} | {NEAR[name]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "violet", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
