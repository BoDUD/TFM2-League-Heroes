#!/usr/bin/env python3
"""Write assets/source/syfen/POSE_PROMPTS.md from pack_syfen_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_syfen_pose_md.py [--lol "D:/Riot Games/League of Legends"]

The table says, per pose, which wing-arm is nearer the camera (pack_syfen_poses.near_arm on that pose's skeleton).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_syfen_poses as A  # noqa: E402

N = len(A.POSES)
RUNS = sum(1 for k in A.POSES if k.startswith("run"))

HEAD = f"""# 赛芬：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 赛芬的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，按它自己的格子读回、缩到游戏大小：**侧身朝右、弓着身子直立**；灰白皮肤，胸口和肚子上**深青黑色的横肋甲**，四肢缠着深青黑甲带；脖子和背上**宝蓝到紫色的背甲**；**品红头甲、蓝紫长嘴、一排白牙、两根带横纹的暗红弯角、粉紫色发光的眼睛**；**两条浅灰色的长前臂就是翅膀**（外侧粉色水晶刺，下面是紫到品红的翼膜，手上三根钢蓝利爪）；反关节腿和深紫黑爪；**长尾巴**往左下方拖，尾尖是一把浅钢灰的弯刀刃）。
> - 请你画 **{N} 个姿势**（普攻 4 个 + 技能 7 个 + 死亡 2 帧 + **跑步 {RUNS} 帧**），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个赛芬**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都一样**：翅膀张开、身子压低、整个趴下的姿势，身体、头、手臂和腿也**和定稿一样粗、一样大**，不要为了把翅膀装进画面就把整个人缩小（参考图已经按同一个比例摆好了，照它的大小画就行）。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、两条腿、两条翅膀手臂、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，参考图里已经放大了。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**橙线 = 他的左翅膀手臂，紫线 = 他的右翅膀手臂**（大圆点是利爪），**粉线 / 青线 = 左 / 右的翼骨**（从手腕伸到翼膜的尖：翼膜就挂在前臂和这根翼骨之间），**红线 = 左腿，蓝线 = 右腿**，**棕线 = 尾巴**，**灰框 = 头的位置**。近处是哪条翅膀手臂，下表写了（近处的手臂、腿、翼膜用全亮的颜色，远处的暗一档）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（品红头甲、蓝紫长嘴、白牙、两根暗红弯角、粉紫色发光的眼睛）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；眼睛一直在。`q_rear`、`q_bite`、`r_bite` 这三个咬人的姿势，**嘴可以张大**（上颚照 `1_head.png`，下颚往下张开，露出上下两排白牙），其余的嘴照定稿。
> - **翅膀手臂**：一直是定稿那两条（浅灰长前臂 + 粉色水晶刺 + 紫到品红的翼膜 + 钢蓝利爪），**长度和定稿一样，不要变长**。翼膜一直挂在前臂下面；张开的姿势（`e_spread`、`a2_wind`、`r_roar`）照参考图把翼膜展开，收着的姿势照参考图垂下或贴着身体。
> - **尾巴**：一直是定稿那条（深青黑甲片 + 尖刺 + 刀刃尾尖），粗细不变。**跑步 {RUNS} 帧和 `d_down` 的尾巴比模型短**（参考图里已经缩短了，照参考图画）。
> - **跑步 {RUNS} 帧（`run1`–`run{RUNS}`）是一整个循环**：金铲铲里他**四肢着地奔跑**，两条翅膀手臂当前腿撑地（翼膜收着），**两条后腿各往前迈一次**——左腿（红线）和右腿（蓝线）在不同的帧轮流在前面（`run2` 和 `run6` 是两条后腿交错经过的那一帧），**每一帧的四条腿都照骨架摆，换腿要看得出来**；身子、头、尾巴每帧都是同一个，只跟着骨架起伏。

## {N} 个姿势

| 图 | 文件 | 片段 | 近处的翅膀手臂 | 姿势 |
|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, side-on facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (his feet on y {A.SOLE_Y}) - a WYVERN standing hunched and upright on two digitigrade legs, WHOSE ARMS ARE HIS WINGS: pale grey / off-white skin, DARK BLACK-TEAL HORIZONTAL RIB PLATES on his chest and belly and dark bands round his limbs, ROYAL BLUE TO VIOLET plates down his neck and back; a MAGENTA HEAD PLATE, a long BLUE-VIOLET SNOUT with a row of WHITE TEETH, TWO RIDGED DARK CRIMSON CURVED HORNS, a GLOWING PINK-VIOLET EYE; two LONG PALE GREY FOREARMS with bright pink crystal spikes, the PURPLE-TO-MAGENTA WING MEMBRANE hanging under each forearm, THREE STEEL-BLUE TALONS at each hand; dark purple-black clawed feet; a LONG TAIL of dark black-teal plates and spikes ending in a curved pale steel BLADE; B his HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the two wing-arms, the tail, the body's and the head's angle from it - never its 3D shading; its head is already enlarged to image A's); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), ORANGE = his LEFT wing-arm, PURPLE = his RIGHT wing-arm (the big dot = the talons), PINK / CYAN = the LEFT / RIGHT wing bone (from the wrist out to the membrane's tip: the membrane hangs between the forearm and this bone), RED = his LEFT leg, BLUE = his RIGHT leg, BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the head, the wing-arms and the legs as big and as thick as in A, where C shows them - never shrink the whole creature to fit spread wings or a long pose in. Each leg along its line, bending at its knee, never stretched, never thinner than in A. The WING-ARMS are always image A's two at image A's length, never longer: the membrane always hangs under the forearm, spread open where C and D open it, hanging or folded along the body where C folds it. The TALONS are always image A's steel-blue talons. The tail along the brown line with its blade at the end. The near side (the near wing-arm, leg and membrane) in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the magenta head plate, the blue-violet snout, the white teeth, the two crimson horns, the glowing pink-violet eye) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eye always visible. Only in the bite poses the lower jaw may drop open, both rows of white teeth showing.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no claw trails, no bite marks, no sweep arcs, no charge trails, no purple smoke, no sparks, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/syfen-poses/syfen-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/syfen-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，最后写 `outputs/syfen-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/syfen_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/syfen/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw 原稿、按同一个身体大小读（不要用 Codex 按框缩放的成品：张翅膀的姿势身体会变小），按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、翅膀手臂和弯角大小不变、腿没有被压扁或拉长、跑步 {RUNS} 帧是同一个身体且换腿看得出来、远处的腿暗一档）。
- 骨架包：`tools/art/pack_syfen_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影，yaw {A.YAW}；头放大 HEAD_SCALE {A.HEAD_SCALE}；跑步是一整个 0.667 秒的四肢着地循环，两条后腿交错在 run2 / run6，跑步和 d_down 的尾巴缩到 {A.TAIL_SCALE}）；这份提示词由 `tools/art/gen_syfen_pose_md.py` 生成。
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
        rows.append(f"| {k + 2} | `syfen-pose-{name}.png` | {clip} | {near} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "syfen", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
