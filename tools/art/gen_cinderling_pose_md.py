#!/usr/bin/env python3
"""Write assets/source/cinderling/POSE_PROMPTS.md from pack_cinderling_poses.POSES (the pose table and the per-pose
lines).

    python tools/art/gen_cinderling_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_cinderling_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 绯红树怪：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 绯红树怪的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A 的第一稿，按它自己 8 px 的格子读回，原样定稿（30 像素高，PPU 2.33），这里每格 {A.PX} px：3/4 朝右，**四脚着地蹲着的矮胖小树皮兽**；**深紫褐的树皮身子**，**前腿外面的暖褐木头甲片和青苔**，**深紫黑的尖爪**；背上**一排浅绿色的高尖叶**、脖子一圈深绿叶；脸是**圆圆的木头面具：左边一只发光的大眼睛（黄色亮芯），右边一个发光的 G 形螺旋纹，下面一排尖牙**）。每个姿势都照它。
> - 请你画 **{N} 个姿势**（7 个动作 + 4 帧蹦跳着跑 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只绯红树怪**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，红线是地面（**站在地上的姿势最低点 y = {A.SOLE_Y}**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：站起来、蹦到空中、翻倒、躺下的时候，画面会变高、变宽或变矮，**但身子、面具、腿、叶子不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**面具每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，面具已经放大了一些——**姿势、四条腿、身体和面具的角度、叶子鬃毛的方向照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型比定稿瘦，**身子的胖瘦、木头甲片、叶子的大小照定稿**。
> - **蹦在空中的姿势**（a_fling、run2、run3、e_pop）参考图里离地多高就画多高，**脚不要落到红线上**；**钻地的 e_dig 红线以下什么都不画**（下半身在地里）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两条前腿（肩膀到爪子）**，**红线 / 蓝线 = 两条后腿**，**黄线 = 背上最高那片叶子**；**灰框 = 面具的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **面具一格一格照 `1_head.png` 画在灰框里**（木板、左边的大眼睛和黄色亮芯、右边的螺旋纹、下面的尖牙）。每个姿势都是这一个面具，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 眼睛和螺旋纹熄灭（暗褐色，不发光）。
> - **腿**：一直是定稿那四条短粗的腿（前腿包着暖褐木甲和青苔，爪子深紫黑），**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的腿颜色正常、画在上面，远处的暗一档**。
> - **背上的叶子鬃毛**每张都在：竖起、甩动、往后飘都照参考图和黄线；**叶子的数量、颜色、大小照定稿**。
> - **蹦跳 4 帧（run1–run4）是一整圈**：小兽往前一蹦一蹦地跑——蹲紧、蹬起、空中、前爪落地；**每帧的身子、面具、叶子都是同一个**，只有身体高度、四条腿和叶子的方向按参考图变。
> - **死亡（d_flip、d_down）**：d_down 四脚朝天躺在地上；身子、面具的大小不变。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（面具）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest point on y {A.SOLE_Y}) - a SMALL SQUAT FOUR-LEGGED BARK CRITTER: a DARK PURPLE-BROWN BARK body, SHORT THICK LEGS, the front legs covered by WARM BROWN WOOD PLATES with MOSS-GREEN PATCHES, DARK PURPLE-BLACK CLAWS, a row of TALL POINTED PALE GREEN LEAVES standing on its back and a collar of darker green leaves, and for a face a ROUND WOODEN MASK of upright brown planks with ONE BIG GLOWING ORANGE EYE (yellow centre) on its left, a GLOWING ORANGE G-SHAPED SPIRAL on its right and a ROW OF DARK WOODEN FANGS below; B its MASK shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the body's and the mask's angle and the leaves' direction from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two front legs (shoulder to paw), RED and BLUE = its two back legs, YELLOW = the tallest leaf on its back, GREY BOX = where the mask goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; standing poses with their lowest point on y {A.SOLE_Y}; poses in the air exactly as high as in image C (feet NOT on the red line); a pose sunk into the ground shows NOTHING below the red line.
THE SAME BULK AS IMAGE A: the body, the mask, the four legs and the leaves exactly as big as in A in EVERY pose, also when it stands up, hops into the air, flips over or lies on its back (the picture simply grows taller, wider or shorter - never shrink the body or the mask to fit). Each leg along its line (short and thick, the front ones with their wood plates and moss, dark claws at the end), bending at the joints, never stretched, never squashed, never thinner than in A; the NEAR legs in full tone and in front, the FAR ones a step darker. The leaf mane stays on its back, raised, flung or streaming as image C shows, the same leaves as in A.
THE MASK: copy image B SQUARE FOR SQUARE into the grey box (the wooden planks, the big glowing eye with its yellow centre on the left, the orange spiral on the right, the fangs below) - the same mask in every pose, only moved and tilted with the body, never turned, never redrawn; the eye and the spiral go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no flying leaves, no fire, no burn, no dirt or dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/cinderling-poses/cinderling-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）；原始生成图原样放进 `outputs/cinderling-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**，最后写 `outputs/cinderling-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/cinderling_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/cinderling/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw，**每张按定稿的身体大小读**（站起、蹦起、翻倒时 Codex 容易把身体画小：codex-fit-shrinks-bodies），面具对齐定稿的面具（hd/idle.png）；每帧 8 倍检查（面具不动、大眼睛和螺旋纹还在、腿没有被压扁或拉长、远处的腿暗一档、空中的姿势真的离地）。
- 骨架包：`tools/art/pack_cinderling_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；面具放大 {A.HEAD_SCALE} 倍；它没有跑步动作，蹦跳 4 帧取自它普攻的往前一蹦）；这份提示词由 `tools/art/gen_cinderling_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `cinderling-pose-{name}.png` | {clip} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "cinderling", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
