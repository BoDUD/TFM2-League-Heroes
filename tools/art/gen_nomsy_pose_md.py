#!/usr/bin/env python3
"""Write assets/source/nomsy/POSE_PROMPTS.md from pack_nomsy_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_nomsy_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_nomsy_poses as A  # noqa: E402

N = len(A.POSES)
HOVER = [name for name, (clip, *_r) in A.POSES.items() if clip in A.WING_LINES]

HEAD = f"""# 诺姆希：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 诺姆希的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按它自己的格子读回，1:1 定稿：3/4 朝右，**四肢着地蹲坐**；粉色大圆肚子、粉色的脸、额头深紫花纹带、绿眼睛、微张的地包天大嘴和白獠牙、头顶三根紫刺；深紫蓝的背鳞和紫色背刺、四条短粗腿；**近处的翅膀从背上往画面左边伸出去，末端是月牙形的紫红翼膜；远处的翅膀在头后面往右上方翘起；短粗的尾巴带四根小刺，在后腿后面**——这是你第 0 步纠正过的结构，每个姿势都照它）。
> - 请你画 **{N} 个姿势**（10 个动作 + 8 帧移动 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个诺姆希**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。**在空中的姿势（q_roar、r_up、r_fly1、r_fly2）也画在地面线上**，游戏里我再抬高。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、四条腿、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。参考图里**舌头已经收回嘴里**（金铲铲的普攻会把舌头甩出去一个身子长，我们不要）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**橙线 / 紫线 = 两条前腿**（大圆点是前爪；**紫线是近处的那条**），红线 / 蓝线 = 两条后腿（**蓝线是近处的**），**棕线 = 短尾巴**，**青线 = 近处的翅膀，粉线 = 远处的翅膀**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（三根紫刺、额头花纹带、绿眼睛、白獠牙、地包天的嘴）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**只有嘴可以变**：`a_spit`、`q_rise`、`q_roar`、`e_breath` 张大嘴（里面橙红色，舌头在嘴里），`e_back` 闭嘴鼓气；眼睛和獠牙不动。
> - **翅膀**：一直是定稿那两只翅膀（深紫的翼骨、紫红的翼膜、月牙形的末端），**长度和定稿一样，不要变长**。收着的姿势照定稿收在背上；`q_roar` 照参考图张开一点；**`r_up`、`r_fly1`、`r_fly2` 三个盘旋姿势参考图里没有翅膀**（模型的翅膀在这个角度会缩到身后）：**按骨架的青线 / 粉线把定稿的两只翅膀展开**——`r_up` 两只都高高往上扬，`r_fly1` 向两边平平展开，`r_fly2` 往下扇到最低；三张的身体一样，只有翅膀不同（连起来就是扇翅膀）。
> - **移动 8 帧（run1–run8）是一整个循环**：身体每帧都是同一个，只有四条腿和身体高低按参考图变；**近处的腿（紫、蓝）颜色正常，远处的腿（橙、红）暗一档**，前后两对腿要看得出交替。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (her feet on y {A.SOLE_Y}) - a CHUBBY BABY DRAGON sitting on all fours: a HUGE ROUND PINK BELLY, a pink face with a dark purple forehead band, green eyes, a wide underbite mouth slightly open with white tusks, three purple spikes on her head; dark violet-blue scaly back with purple spikes, four short stubby legs; her NEAR WING reaches from her back out to the image left, ending in a crescent magenta membrane; her FAR WING rises behind her head to the upper right; a SHORT THICK TAIL with four small spikes behind the hind legs; B her HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the body's and the head's angle from it - never its 3D shading; its tongue is pulled back into the mouth; in the three hover poses it shows no wings); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), ORANGE and PURPLE = her front legs (the big dot = the front paw; purple is the NEAR one), red / blue = her hind legs (blue is the NEAR one), BROWN = the short tail, CYAN = the NEAR WING, PINK = the FAR WING, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her lowest point on y {A.SOLE_Y} (a pose in the air is drawn standing on that line too).
THE SAME BULK AS IMAGE A: the belly as big and round as in A, the legs as short and thick, the body where C shows it. Each leg along its line, bending at the knee, never stretched, never thinner than in A. The WINGS are always image A's two wings at image A's length (dark violet bones, magenta membranes, crescent ends) - folded on her back where C shows them folded, spread along the CYAN and PINK lines where D draws them (never longer than in A). The short spiky tail along the brown line. The near side in full tone, the far side (the far legs, the far wing) a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the three head spikes, the forehead band, the green eyes, the white tusks) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; only the MOUTH may open wider where the pose says so (orange-red inside, the tongue inside the mouth).
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no fire, no fireball, no smoke, no sparks, no wind, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/nomsy-poses/nomsy-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/nomsy-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，最后写 `outputs/nomsy-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/nomsy_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/nomsy/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、翅膀长度不变、肚子大小不变、腿没有被压扁或拉长、移动 8 帧是同一个身体、远处的腿暗一档）。
- 骨架包：`tools/art/pack_nomsy_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影；舌头收回，盘旋三帧的身体用待机的朝向、翅膀是按定稿长度画的方向线 WING_LINES）；这份提示词由 `tools/art/gen_nomsy_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `nomsy-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "nomsy", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text), "hover", HOVER)


if __name__ == "__main__":
    main()
