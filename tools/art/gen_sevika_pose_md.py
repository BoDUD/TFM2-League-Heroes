#!/usr/bin/env python3
"""Write assets/source/sevika/POSE_PROMPTS.md from pack_sevika_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_sevika_pose_md.py [--near C:/t/sv_work/poses_near.txt]

--near: pack_sevika_poses.py's printout (one "<k>_<name> <clip> yaw 35 near arm CYAN|ORANGE ..." line a pose), for the
table's "front arm" column.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_sevika_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 塞薇卡：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 塞薇卡的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按你自己的格子读回、定稿：3/4 朝右，**站姿戒备，左臂是巨大的黄铜机械臂，垂在身前（画面右边），爪钳朝下到膝盖**；深棕色往后梳的头发（脸边两缕）、暖肤色方脸、压低的深色直眉、灰眼睛；藏青短袖 + 金色菱形肩章、棕色短皮背心（露腹）、棕腰带 + 灰色小包、深棕长裤带护膝、金包头短靴；右手（肉手，画面左边）戴金钉护腕、手指张开；**机械臂：黄铜肩甲上一台小老虎机（红棕盒子、三个奶白转轮窗、粉紫青小灯珠、两根黄铜管）+ 黄铜上臂 + 青绿装甲前臂 + 洋红尖刺 + 亮青爪钳**）。
> - 请你画 **{N} 个姿势**（13 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个塞薇卡**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**脚底 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**身体的姿势照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **机械臂的大小照定稿，不照参考图**：骨架图里**青线 = 机械臂**（第一个点是肩膀，**大圆点是手腕**），**紫线 + 金三角 = 爪钳**（从手腕到爪尖），**紫圈 = 肩上老虎机的位置**。机械臂沿青线、爪钳沿紫线的方向画，**粗细、长短和定稿一样（垂下时从老虎机到爪尖约 50 格，前臂约 12 格粗，爪钳约 12 × 11 格）**，线比这长时画到定稿的长度就停；**老虎机一直在机械臂的肩上**，三个转轮窗要看得见。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 右手（肉手）**，**青线 = 机械臂**；红线 / 蓝线 = 两条腿；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **头一格一格照 `1_head.png` 画在灰框里**（深棕头发、暖肤色脸朝右前方、压低的直眉、两只灰眼睛、紧闭的嘴）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`d_fall` / `d_down` 倒下时头跟着身体放倒，但还是这个头）。机械臂、爪钳和手**不要挡住脸**（眼睛、眉毛、嘴）；机械臂举过头顶时（`a2_raise`、`r_raise`）它在头的上面或后面，脸露在外面。
> - **长短要数格子**：和定稿一样，头（含头发）约 31 × 22 格，肉手从肩膀到手约 30 格。**手臂沿着骨架画，长短和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。她肩宽、身材结实。
> - **跑步 8 帧要有交叉步**：两条腿照红线 / 蓝线**前后交换**，中间几帧两条腿**交叉经过**，不要每帧都是两腿大大叉开；**远处的那条腿暗一档**，近处的腿完整亮色，这样看得出哪条腿在前。
> - **举高的姿势**（`a2_raise`、`r_raise`）：机械臂举过头顶，**画布上方要放得下**，爪尖别出画；目标不画。
> - **`d_down`**：参考图是她被打飞的那一帧放倒，**照它的大小和位置，把她画成仰面躺在地上**（身体贴着地面线），机械臂摊在身边地上。

## {N} 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (her soles on y {A.SOLE_Y}) - a BROAD-SHOULDERED, STURDY WOMAN with DARK BROWN HAIR combed back (a lock at each side of the face), a warm square face, thick dark straight brows, grey eyes; a dark navy short-sleeved top with gold diamond shoulder badges, a brown leather cropped vest (bare midriff), a brown belt with a small grey pouch, dark brown trousers with knee pads, dark boots with gold toe caps, a studded brown wristband on her flesh right hand; her LEFT ARM a HUGE BRASS MECHANICAL ARM - a brass pauldron carrying a SMALL SLOT MACHINE (a red-brown box, three cream reel windows, tiny pink / purple / cyan bulbs, two brass pipes on top), a segmented brass upper arm, a TEAL-armoured forearm with MAGENTA SPIKES and gold bolts, a huge pair of BRIGHT CYAN CLAWS with magenta tips; B its HEAD shown 8x (about 31 squares wide, 22 tall: the hair and the face); C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the BODY POSE from it - never its 3D shading, and NOT its arm size); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = her flesh right arm, CYAN = the MECHANICAL arm (each line from the shoulder, the big dot = the hand / wrist), the PURPLE line with a GOLD TRIANGLE = the CLAWS (from the wrist to the claw tips), the PURPLE RING = the slot machine on its shoulder, red / blue = her legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her soles (or the lowest point) on y {A.SOLE_Y}.
COUNT THE SQUARES: the same proportions as image A - the head with the hair about 31 x 22, the flesh arm about 30 squares from the shoulder to the hand, broad shoulders, a sturdy body. The body exactly where C shows it. The flesh arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. THE MECHANICAL ARM along the cyan line and the CLAWS along the purple line toward the gold triangle, EXACTLY AS THICK AND AS LONG AS IN IMAGE A (about 50 squares from the slot machine to the claw tips when it hangs, the forearm about 12 squares thick, the claws about 12 x 11) - stop at that length even if the lines run longer; the slot machine always on its shoulder at the purple ring, its three reel windows visible. The near side in full tone, the far side a step darker (the far leg a step darker than the near leg).
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the warm face to the front-right, the low straight brows, the two grey eyes, the closed mouth, the dark brown hair) - the same head in every pose, only moved (tilted with the body when she falls or lies down), never turned, never redrawn as a profile. Neither the mechanical arm, nor the claws, nor a hand covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no fire, no rockets, no coins, no spring or flying fist, no sparks, no motion lines, no marks), no target character, no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/sevika-poses/sevika-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/sevika-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，中间不要停，最后写 `outputs/sevika-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sevika_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sevika/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、脸上眼睛眉毛还在、机械臂不挡脸、机械臂和爪钳大小方向对、老虎机还在肩上、没有被压扁的身体、腿不变形、跑步有交叉步、远近腿深浅分得开）。
- 骨架包：`tools/art/pack_sevika_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的；爪钳按 L_ClampA / L_ClampB 的顶点画）；这份提示词由 `tools/art/gen_sevika_pose_md.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--near", required=True, help="pack_sevika_poses.py's printout")
    a = ap.parse_args()
    near = {}
    for line in open(a.near, encoding="utf-8"):
        m = re.match(r"\d+_(\w+) \S+ yaw \d+ near arm (CYAN|ORANGE)", line)
        if m:
            near[m.group(1)] = "青（机械臂）" if m.group(2) == "CYAN" else "橙（肉手）"
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `sevika-pose-{name}.png` | {clip} | {near[name]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "sevika", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
