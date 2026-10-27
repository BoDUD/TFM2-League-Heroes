#!/usr/bin/env python3
"""Write assets/source/vander/POSE_PROMPTS.md from pack_vander_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_vander_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_vander_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 范德尔：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 范德尔的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，缩到游戏大小定稿：3/4 朝右，**屈膝压低的格斗架势**，**画面左边那只手戴着红铜色大铁拳套、压在身前腰带前面往前伸，画面右边缠绷带的拳头举在下巴前**；往后梳的深色头发、粗黑浓眉、短络腮胡；焦橙色皮夹克、米白竖条纹马甲、青绿领口、暗红腰带黄铜扣、深藏青牛仔裤、黑工装靴；戴拳套那条前臂套着紫色护臂）。
> - 请你画 **{N} 个姿势**（9 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个范德尔**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**脚底 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、两只手、拳套在哪照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **铁拳套**：一直戴在**同一只手**上（骨架里的**橙色手臂**，手上套着**金圈**），样子、颜色、大小照定稿（黄铜八角框、两块红面板、金色六角螺栓，比拳头大一圈，手腕接紫色护臂）。另一只手（**青色手臂**）永远是缠灰白绷带的拳头。参考图里拳套在画面哪边，就画在哪边。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 戴拳套的手臂**，**青线 = 缠绷带的手臂**（哪只在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 两条腿；**金圈 = 拳套**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **头一格一格照 `1_head.png` 画在灰框里**（往后梳的头发、粗黑浓眉、两只眼睛、短络腮胡、脸朝右前方）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`r_air` 怒吼时嘴张开一点，`d_down` 趴在地上时头跟着身体放倒，但还是这个头）。拳套和拳头**不要盖住脸**（两只眼睛和胡子里的嘴）：`q_guard` 的拳套举在头的**右边**护着，眼睛露出来。
> - **长短要数格子**：和定稿一样，手臂从肩膀到拳头约 16 格，头（含头发）约 26 × 22 格，拳套约 12 × 12 格。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。他是壮汉：肩宽、胸厚、手臂粗，不要画瘦。

## {N} 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (his soles on y {A.SOLE_Y}) - a big, burly middle-aged BRAWLER in a low fighting stance: swept-back dark hair, thick black brows, a short grey-brown beard; a burnt-orange leather jacket, a cream striped waistcoat, a teal collar, a dark red belt with brass buckles, dark navy jeans, black work boots; on one hand (image left, held low in front of his belt) a big IRON GAUNTLET (an octagonal brass frame, two red panels, gold hexagonal bolts) joined to a purple bracer, the other hand (image right, at his chin) a fist wrapped in grey-white bandages; B its HEAD shown 8x (about 26 squares wide, 22 tall: the hair, the brows, two eyes, the beard); C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, both hands and where the gauntlet is from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = his GAUNTLET arm, CYAN = his BANDAGED arm (each line from the shoulder, the big dot = the hand), red / blue = his legs, GOLD ring = the gauntlet, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y {A.SOLE_Y}.
COUNT THE SQUARES: the same proportions as image A - each arm about 16 squares from the shoulder to the fist, the head with the hair about 26 x 22, the gauntlet about 12 x 12 (the 3D render may squash it: keep its real size), a broad, strong body. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. The gauntlet always on the ORANGE arm's hand, the same gauntlet as image A, only moved and turned; the CYAN arm's hand always the bandaged fist. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the swept-back hair, the thick brows, both eyes, the short beard, the face to the front-right) - the same head in every pose, only moved (tilted with the body when he falls or lies down), never turned, never redrawn as a profile. No fist or gauntlet covers the face (the eyes and the mouth in the beard).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no punch wind, no shockwave, no dust, no sparkles, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/vander-poses/vander-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/vander-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，最后写 `outputs/vander-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/vander_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/vander/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛和嘴还在、拳套和拳头不挡脸、拳套一直在同一只手上、大小不变、没有被压扁的身体）。
- 骨架包：`tools/art/pack_vander_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的；拳套在模型的 R_ 手上）；这份提示词由 `tools/art/gen_vander_pose_md.py` 生成。
"""

# the arm nearer the camera, as pack_vander_poses prints it for each pose (2026-10-27)
NEAR = {name: "橙（拳套）" for name in A.POSES}
NEAR.update({n: "青（绷带拳）" for n in ("a_wind", "e_upper", "run1", "run2")})


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        n = k + 2
        rows.append(f"| {n} | `vander-pose-{name}.png` | {clip} | {NEAR[name]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "vander", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
