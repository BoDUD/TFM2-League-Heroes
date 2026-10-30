#!/usr/bin/env python3
"""Write assets/source/daeja/POSE_PROMPTS.md from pack_daeja_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_daeja_pose_md.py [--lol "D:/Riot Games/League of Legends"]

The table says, per pose, which arm is nearer the camera (pack_daeja_poses.near_arm on that pose's skeleton).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_daeja_poses as A  # noqa: E402

N = len(A.POSES)
RUNS = sum(1 for k in A.POSES if k.startswith("run"))

HEAD = f"""# 迭嘉：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 迭嘉的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按它自己的格子读回，1:1 定稿：**3/4 朝右、直立站着**；冰蓝水晶皮肤、深蓝紫的人字形胸甲、肩膀和前臂上古铜 / 银灰的尖刺；**古铜面甲、品红发光的眼睛、浅青蓝的大团鬃毛、头后两撮青蓝鬃冠**；**两只发光的青色水晶拳**；**背后两片收起来高高竖起的翅膀**（深紫翼骨、青到紫的扇形翼膜、锯齿边）；深紫黑的腿和黑爪；尾巴往左下方拖，尾尖一片古铜叶形尾鳍）。
> - 请你画 **{N} 个姿势**（普攻 2 个 + 技能 9 个 + 死亡 2 帧 + **跑步 {RUNS} 帧**），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个迭嘉**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、两条腿、两只手臂、两片翅膀、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，参考图里已经放大了。他的金铲铲动作里**没有普攻**，`a_wind`、`a_punch` 两张是待机把近处那只手臂转过去做出来的（只有那只手臂和待机不一样）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**橙线 = 他的左臂，紫线 = 他的右臂**（大圆点是拳头），**红线 = 左腿，蓝线 = 右腿**，**粉线 = 左边的翅膀，青线 = 右边的翅膀**（从背上的翼根连到每一根翼骨的根部、一直到翼尖那根：翅膀就沿着这条线张开或收起），**棕线 = 尾巴**，**灰框 = 头的位置**。近处是哪只手臂，下表写了（近处的手臂、腿、翅膀用全亮的颜色，远处的暗一档）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（古铜面甲、额头小尖角、品红发光的眼睛、浅青鬃毛、头后两撮鬃冠）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；眼睛一直在。
> - **翅膀**：一直是定稿那两片（深紫翼骨、青到紫的扇形翼膜、锯齿边），**大小和定稿一样，不要变长变大**。收着的姿势照定稿竖在背后；`q_raise`、`e_beat`、`e_hop`、`r_up`、`r_fly1`、`r_fly2` 照参考图张开（扇子打开，翼膜一条条摊开）；`q_sweep`、`r_blast` 照参考图往前扫到身前。
> - **拳头**：一直是定稿那两只发光的青色水晶拳，大小不变。
> - **跑步 {RUNS} 帧（`run1`–`run{RUNS}`）是一整个循环**：金铲铲里他弓着身子跑，**两条腿各往前迈一次**——左腿（红线）和右腿（蓝线）在不同的帧轮流在前面，**每一帧的两条腿都照骨架摆，换腿要看得出来**；身子、头、翅膀每帧都是同一个，只跟着骨架起伏。

## {N} 个姿势

| 图 | 文件 | 片段 | 近处的手臂 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (his feet on y {A.SOLE_Y}) - a BLUE CRYSTAL DRAGON-MAN standing upright on two legs: ice-blue / cyan crystal skin, layered dark blue-violet chevron plates on the chest and belly, bronze / silver-grey spikes on the shoulders and forearms; a BRONZE SKULL MASK over his face with GLOWING MAGENTA EYES, a big PALE CYAN MANE hanging from the chin, two cyan crests behind the head; two GLOWING CYAN CRYSTAL FISTS; two big FOLDED WINGS rising high behind his back (dark violet spiked wing bones, cyan-to-violet fan membranes, saw-toothed edges); dark violet-black legs with black claws; a blue tail to the lower left ending in a bronze leaf-shaped FLUKE; B his HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the two arms, the two wings, the body's and the head's angle from it - never its 3D shading; its head is already enlarged to image A's); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), ORANGE = his LEFT arm, PURPLE = his RIGHT arm (the big dot = the fist), RED = his LEFT leg, BLUE = his RIGHT leg, PINK = the LEFT wing and CYAN = the RIGHT wing (from the wing's root on his back through the roots of its ribs out to the tip: the wing opens or folds along that line), BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the arms and the legs as thick as in A, where C shows them. Each leg along its line, bending at its knee, never stretched, never thinner than in A. The WINGS are always image A's two at image A's size, never bigger - standing folded behind his back where C shows them folded, opened like a fan (the membrane strips spread between the ribs) where C and D open them, swept in front of him where C sweeps them. The FISTS are always image A's two glowing crystal fists. The tail along the brown line with its fluke at the end. The near side (the near arm, leg and wing) in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the bronze mask with its forehead spike, the glowing magenta eyes, the pale cyan mane, the two crests) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eyes always visible.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no wind, no air streaks, no shock wave, no bolts, no glow beyond the fists' own colour, no sparks, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/daeja-poses/daeja-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/daeja-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，最后写 `outputs/daeja-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/daeja_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/daeja/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、翅膀大小不变、腿没有被压扁或拉长、跑步 {RUNS} 帧是同一个身体且换腿看得出来、远处的腿暗一档）。
- 骨架包：`tools/art/pack_daeja_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影，yaw {A.YAW}；头放大 HEAD_SCALE {A.HEAD_SCALE}；普攻两帧是待机把左臂按 ARM 转过去）；这份提示词由 `tools/art/gen_daeja_pose_md.py` 生成。
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", default=r"D:\Riot Games\League of Legends")
    a = ap.parse_args()
    poser = A.Poser(a.lol)
    rows, lines = [], []
    for k, (name, (clip, yaw, zh, en)) in enumerate(A.POSES.items()):
        _, joints = poser.pose(clip, A.ARM.get(name))
        _, jz = A.Poser.project(joints, yaw, 1.0, 0.0, 0.0)
        near = "左（橙线）" if A.near_arm(jz, poser) == "L" else "右（紫线）"
        rows.append(f"| {k + 2} | `daeja-pose-{name}.png` | {clip} | {near} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "daeja", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
