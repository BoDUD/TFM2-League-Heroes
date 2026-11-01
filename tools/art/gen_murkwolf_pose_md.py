#!/usr/bin/env python3
"""Write assets/source/murkwolf/POSE_PROMPTS.md from pack_murkwolf_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_murkwolf_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_murkwolf_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 暗影狼：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 暗影狼的造型用户已经定稿。`0_design.png` 是你第 0 步交的 A（murkwolf-A.png），按它自己 9 px 的格子读回、1:1 定稿，这里放大成每格 {A.PX} px。它的样子：
>   - 3/4 朝右、**四条腿压低身子的双头狼**，灰蓝色的毛；
>   - 背上一大片**紫色鬃毛**，鬃毛里一排**墨绿尖刺**；
>   - **蓬松的大尾巴**往左上方翘，尾尖发黑；
>   - **两个一样大的狼头**并排：粉色内耳的尖耳朵、**发光的青色眼睛**、张开的**粉色大嘴和黄色尖牙**、**白色腮毛**；
>   - 四只爪子是**黑色弯钩爪**。
>   每个姿势都照它。
> - 请你画 **{N} 个姿势**（9 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只狼**：样子、颜色、大小全照 `0_design.png`。**格子和它一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，网格从画布左上角对齐。红线是地面，**最低点 y = {A.SOLE_Y}**。
> - **身体大小每张都和定稿一样**：起跳竖起、仰头嚎叫、被掀翻、侧躺的时候，画面会变高、变宽或变矮，**但身子、头、腿不能因此画小**。按参考图的大小画，超出去就让它超出去，画布够大。**两个头每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上，高度和位置都一样，头已经放大了一些。
>   - 姿势、四条腿、尾巴、身体和两个头的角度**照参考图**。
>   - 长相和画法**照定稿**：像素格、描边、平涂，不要 3D 光影。
>   - 毛色分区（灰蓝身子、紫色鬃毛和墨绿尖刺、白色腮毛）、头的大小**照定稿**。
>   - 嚎叫（e_gather、e_howl）和号令（r_growl、r_bark）这几张，两个脖子是我按骨架抬起或压低的，**以骨架的橙线 / 黄线为准**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：
>   - 绿线 = 脊柱（屁股到肩膀），**棕线 = 尾巴**。
>   - **橙线 / 黄线 = 两条脖子和两个头**（最后一段是下巴）。
>   - **红线 / 蓝线 = 两条前腿**，**粉线 / 青线 = 两条后腿**。
>   - **灰框 = 两个头的位置**。
>   - **近处（离我们近）的始终是黄线头、蓝线前腿、青线后腿**。跑步时腿前后交错，也还是这几条在近处。
>   - `0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，用来看清哪条线是哪个部位。
> - **头照 `1_head.png` 一格一格地画**（定稿的两个头，放大 8 倍）。近处的头在前、在下，远处的头在后、略高。每个姿势都是这两个头，只跟着脖子移动和倾斜，**不要重新设计**。
>   - **张嘴的姿势**（a_bite、q_leap、e_howl、r_bark、d_fall）只把下巴按橙线 / 黄线的最后一段往下打开，嘴里粉色、黄色尖牙，上半个头不变。
>   - 只有 `d_down` 的眼睛熄灭（暗灰色，不发光）。
> - **腿**：一直是定稿那四条灰蓝色的腿和黑色弯钩爪，**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细。**近处的腿颜色正常、画在上面，远处的暗一档**。
> - **跑步 8 帧（run1–run8）是一整圈**：每帧的身子、头、鬃毛都是同一个，只有四条腿按骨架换位置，身子跟着上下一点点。**一定要看得出腿在交替迈步**。
> - **死亡（d_fall、d_down）**：d_down 侧躺在地上；身子、头、鬃毛的大小不变，只是躺倒。

## {N} 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (its lowest point on y {A.SOLE_Y}) - a LOW-CROUCHED FOUR-LEGGED TWO-HEADED WOLF: SLATE-BLUE FUR with a lighter belly, a big DARK PURPLE MANE down its back with a ROW OF DARK GREEN-BLACK THORN SPIKES in it, a THICK BUSHY TAIL raised up and back to the left with a near-black tip, and TWO EQUAL WOLF HEADS side by side at the front (the near one lower and in front, the far one behind and a little higher), each with upright pointed ears with pink insides, GLOWING CYAN EYES, an open PINK SNARLING MOUTH with YELLOW FANGS and a fluffy WHITE CHEEK RUFF; four strong legs with HOOKED BLACK CLAWS; B its TWO HEADS shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same {A.CANVAS} canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the tail, the body's and the heads' angles from it - never its 3D shading; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to shoulders), BROWN = the tail, ORANGE and YELLOW = the two necks and heads (the last stretch of each is the lower jaw), RED and BLUE = the two front legs, PINK and CYAN = the two hind legs, GREY BOX = where the heads go, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y {A.SOLE_Y}.
THE SAME BULK AS IMAGE A: the body, the two heads and the legs exactly as big as in A in EVERY pose, also when it rears up, leaps, throws its heads back or lies on its side (the picture simply grows taller, wider or shorter - never shrink the body or the heads to fit). Each leg along its line (a strong slate-blue wolf leg, the hooked black claws at the end), bending at its joints, never stretched, never squashed, never thinner than in A; the NEAR legs (blue and cyan lines) in full tone and in front, the FAR ones a step darker. The purple mane and its green-black thorns stay along the back, the bushy tail follows the brown line.
THE HEADS: copy image B SQUARE FOR SQUARE onto the two neck lines inside the grey box (the near head on the YELLOW line, the far head on the ORANGE line) - the same two heads in every pose, only moved and tilted with their necks, never redrawn, never merged into one, never a third head; where the pose opens the mouths, only the lower jaw swings down along its line's last stretch (pink inside, yellow fangs); the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no claw slashes, no wolf pups, no sound rings, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/murkwolf-poses/murkwolf-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）。
- 原始生成图原样放进 `outputs/murkwolf-poses/raw/`。
- `generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**。最后写 `outputs/murkwolf-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/murkwolf_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/murkwolf/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw。
- **每张按定稿的身体大小读**：竖起、腾空时 Codex 容易把身体画小（codex-fit-shrinks-bodies）。两个头对齐定稿的头（hd/idle.png）。
- 每帧放大 8 倍检查：
  - 还是两个头，没有合成一个；
  - 青色眼睛还在；
  - 腿没有被压扁或拉长；
  - 跑步 8 帧的腿真的在交替；
  - 远处的腿暗一档。
- 骨架包：`tools/art/pack_murkwolf_poses.py`。骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；两个头放大 {A.HEAD_SCALE} 倍；嚎叫和号令的脖子按 lift 转；跑步按 0.8 s 一整圈均匀取 8 帧 {A.RUN_MS} ms。这份提示词由 `tools/art/gen_murkwolf_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (clip, _yaw, lift, zh, en)) in enumerate(A.POSES.items()):
        src = clip + (f"（脖子 {lift:+d}°）" if lift else "")
        rows.append(f"| {k + 2} | `murkwolf-pose-{name}.png` | {src} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "murkwolf", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
