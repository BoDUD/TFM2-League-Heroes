#!/usr/bin/env python3
"""Write assets/source/scar/POSE_PROMPTS.md from pack_scar_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_scar_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_scar_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 刀疤：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 刀疤的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，缩到游戏大小定稿：3/4 朝右，**持矛架势，双手横握长矛、矛尖朝右前方**；白骷髅面具（两个黑眼窝、白瞳孔、牙齿栅格）、蓝紫莫西干尖发、两只红色尖耳；紫色皮肤、黑色高围脖、芥末黄马甲（深色皮带、金扣）、棕色铆钉护肩、**画面左边那只胳膊缠满米白绷带**、另一只光着（紫色、戴护腕）、深蓝腰包、洋红 / 深紫裤子、灰绿护膝、深藏青高筒靴；**长矛：深紫矛杆、铜箍、紫底金色涂鸦的箭头形矛头、金色矛尾**）。
> - 请你画 **{N} 个姿势**（12 个动作 + 8 帧走路 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个刀疤**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**脚底 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**身体的姿势照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **长矛按骨架图画，不按参考图**：金铲铲的动画里他常把矛尖朝后拿，我们的造型矛尖朝前。骨架图里**紫线 = 矛杆，金色三角 = 矛尖**，矛尖画在金三角那一头。长矛的样子、粗细、长短照定稿（**约 80 格长**，比他人还长一点），**不要画短**；参考图里的长矛方向对不上时以骨架图为准。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 缠绷带的那只胳膊**、**青线 = 光着的那只胳膊**（戴护腕），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 两条腿；**紫线 + 金三角 = 长矛（金三角 = 矛尖）**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **握矛的手照定稿**：双手握矛时，**光着的那只手（青线）在前、靠近矛头，缠绷带的那只手（橙线）在后、靠近矛尾**。单手拿矛时（扔炸弹、走路）用骨架图里离矛最近的那只手。
> - **头一格一格照 `1_head.png` 画在灰框里**（骷髅面具朝右前方、两个黑眼窝白瞳孔、牙齿栅格、两只红尖耳、蓝紫尖发）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`d_fall` / `d_down` 倒下时头跟着身体放倒，但还是这个头）。长矛和手**不要挡住面具**（两个眼窝和牙齿）。
> - **长短要数格子**：和定稿一样，头（含耳朵和尖发）约 27 × 29 格，手臂从肩膀到拳头约 18 格。**手臂沿着骨架画，长短和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。他身材瘦长。
> - **走路 8 帧要有交叉步**：两条腿照红线 / 蓝线**前后交换**，中间几帧两条腿**交叉经过**（一条腿从另一条腿旁边走过去），不要每帧都是两腿大大叉开；**远处的那条腿暗一档**，近处的腿完整亮色，这样看得出哪条腿在前。
> - **悬浮滑板**（只画在 `surf`、`surf_hit` 两帧）：脚底下画一块野火帮的悬浮滑板——**约 30 × 5 格**，深灰 / 深棕的板面，前端微翘，**底下一排发光的青绿色（野火帮的绿火）推进口**，板子离地面约 3 格（板底在地面线上方）；他两脚踩在板上。滑板不画火焰拖尾（特效另画）。
> - **跳起来的姿势**（`r_jump`）：参考图里最低的点已经放在地面线上，**照着画就行**，离地多高我在动画里再抬。
> - **`d_down`**：参考图是他翻倒的半途，乱一点——**照它的大小和位置，把他画成仰面平躺在地上**（头在画面左、脚在右，身体贴着地面线），长矛掉在身边地上。

## {N} 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 矛尖 | 姿势 |
|---|---|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (his soles on y {A.SOLE_Y}) - a LANKY purple-skinned man behind a WHITE SKULL MASK (two black eye sockets with white pupils, a teeth grille), a blue-violet mohawk, two big pointed RED ears; a tall black collar, a mustard-yellow vest with dark straps and gold buckles, a brown riveted shoulder guard, ONE ARM WRAPPED IN OFF-WHITE BANDAGES and the other bare purple with a bracer, a dark blue hip pouch, magenta / dark purple trousers, grey-green knee guards, dark navy boots; holding a LONG SPEAR across him in both hands, the POINT forward to the right (dark purple shaft, copper bands, a purple arrowhead blade with gold graffiti, a gold butt cap); B its HEAD shown 8x (about 27 squares wide, 29 tall: the mask, the ears, the mohawk); C a 3D RENDER of this same character's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the BODY POSE from it - never its 3D shading, and NOT its spear direction); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = the BANDAGED arm, CYAN = the BARE arm (each line from the shoulder, the big dot = the hand), red / blue = his legs, the PURPLE line = the spear's shaft and the GOLD TRIANGLE = the spear's POINT, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y {A.SOLE_Y}.
COUNT THE SQUARES: the same proportions as image A - the head with the ears and the mohawk about 27 x 29, each arm about 18 squares from the shoulder to the fist, a lanky slim body, THE SPEAR about 80 squares long as in image A (never shorter). The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. THE SPEAR along the purple line of D with its POINT at the GOLD TRIANGLE; held in both hands, the BARE hand is forward near the blade and the BANDAGED hand behind near the butt, as in image A. The near side in full tone, the far side a step darker (the far leg a step darker than the near leg).
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the skull mask to the front-right, both eye sockets with their pupils, the teeth grille, the red ears, the mohawk) - the same head in every pose, only moved (tilted with the body when he falls or lies down), never turned, never redrawn as a profile. Neither the spear nor a hand covers the mask.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no bombs, no fire, no smoke, no dash wind, no sparks, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes. Only in the two HOVERBOARD poses: a small Firelight hoverboard under his feet, about 30 x 5 squares, a dark grey-brown deck with a slightly raised nose and a row of glowing TEAL-GREEN thruster vents on its underside, floating about 3 squares above the ground line, both his feet on it (no flame trail).
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/scar-poses/scar-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/scar-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **{N} 张都画完再交**，中间不要停，最后写 `outputs/scar-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/scar_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/scar/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、面具眼窝和牙齿还在、长矛不挡脸、长矛长短和矛尖方向对、没有被压扁的身体、腿不变形、走路有交叉步、远近腿深浅分得开）。
- 骨架包：`tools/art/pack_scar_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的；长矛的矛尖按 POSES 的 tip 放）；这份提示词由 `tools/art/gen_scar_pose_md.py` 生成。
"""

# the arm nearer the camera, as pack_scar_poses prints it for each pose (2026-10-28): 橙 = the bandaged R_ arm
NEAR = {name: "青" for name in A.POSES}
NEAR.update({n: "橙" for n in ("a_wind", "a_thrust", "a_back", "q_wind", "e_wind", "run1", "run2", "run3", "run7",
                               "run8", "d_fall")})
TIP = {"model": "照骨架", "flip": "照骨架（和模型相反）"}


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, tip, zh, en)) in enumerate(A.POSES.items()):
        n = k + 2
        rows.append(f"| {n} | `scar-pose-{name}.png` | {clip} | {NEAR[name]} | {TIP[tip]} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "scar", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
