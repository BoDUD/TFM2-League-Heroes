#!/usr/bin/env python3
"""Write assets/source/sentry/POSE_PROMPTS.md from pack_sentry_poses.POSES (the pose table and the per-pose lines).

    python tools/art/gen_sentry_pose_md.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_sentry_poses as A  # noqa: E402

N = len(A.POSES)

HEAD = f"""# 苍蓝哨戒：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 苍蓝哨戒的造型用户已经定稿。`0_design.png` 是你第 0 步交的 A（raw/generation-02.png 左半边），按 12 px 的格子读回、1:1 定稿（28 × 44 格），这里放大成每格 {A.PX} px。它的样子：
>   - 稍微 3/4 朝右，**两块漂浮的高瘦水晶石**并排，没有手脚、没有脸；
>   - **左边那块高**，尖尖的多面晶顶；**右边那块矮**，顶是圆钝的；
>   - 上半截**浅灰绿岩面**，下半截**深海军蓝 / 蓝紫**，底下收成尖，缝边一道**暗红紫细边**；
>   - 中间偏上一个圆孔，孔里一颗**发光的蔚蓝能量核**（中间近白）。
>   每个姿势都照它。
> - 请你画 **{N} 个姿势**（普攻 2 + 技能 7 + 飘移 4 + 死亡 2），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **格子和定稿一样大：每格 {A.PX} px**，画布 **{A.CANVAS} × {A.CANVAS}**，网格从画布左上角对齐。红线是地面（y = {A.SOLE_Y}）。它是**飘着的**，大部分姿势离地几格，**位置和高度照布局图**。
> - **它只有三个部件**（`0_parts.png`：**红 = 左边高尖石，蓝 = 右边矮圆石，黄 = 蓝核**）。每个姿势的**布局图**（`*_layout.png`）就是我把定稿的这三块**原样挪动、转动**拼出来的，`*_parts.png` 是同一个布局的纯色版：
>   - **每块石头的形状、大小、颜色、切面都和定稿一样**，只是**换了位置和角度**；
>   - 布局图是最近邻转的，**斜边上的锯齿、断线、缺格是转出来的毛病**：请按定稿的画法**重新画干净**（整齐的近黑描边、平涂切面），**不要照抄锯齿**，但位置、角度、大小照布局图；
>   - 两块石头分开以后，**中间露出来的地方是透明的**（它们本来就是两块），石头内侧的断面画成这块石头自己最暗的一档 + 近黑描边；
>   - **蓝核**：亮几圈就画多大（布局图里外面那几圈亮蓝就是它变亮变大），最亮的时候中间发白；**死亡时变暗、最后熄灭**（暗灰蓝，不发光）。
> - 有 `*_ref.png` 的三个姿势（a_fire、d_split、d_down）是它在金铲铲里自己的动作那一帧（同一个 3D 模型、同一张画布、同样高），**只看动势**；模型很细长，**大小和长相以定稿为准**。
> - **不画任何特效**：激光、光弹、光柱、碎石、尘土、光晕都不画（后面另外画）。

## {N} 个姿势

| 图 | 文件 | 参考 | 姿势 |
|---|---|---|---|
"""

PROMPT = f"""
## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`0_parts.png`（三个部件）、`1_core.png`（蓝核放大 12 倍）、这个姿势的 `*_layout.png` 和 `*_parts.png`，有 `*_ref.png` 的也附上。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, a slight 3/4 view facing right, on a {A.CANVAS}x{A.CANVAS} canvas with {A.PX} px squares (the red line is the ground) - TWO TALL CRYSTAL SHARDS FLOATING side by side with NO limbs and NO face: the LEFT shard taller with a pointed faceted tip, the RIGHT shard shorter with a blunt top, PALE SAGE / GREY-GREEN rock above and DARK NAVY / BLUE-VIOLET below tapering to points, a thin dark red-violet edge by the gap, and A GLOWING AZURE CORE (near-white centre) in the round hole between them; B the same design in its THREE PARTS: RED = the left shard, BLUE = the right shard, YELLOW = the core; C the core shown 12x; D the LAYOUT of THIS POSE: the design's own three parts moved and turned (rotated nearest-neighbour, so its slanted edges are jagged and broken - that is NOT the look, only the placement); E the same layout in flat part colours; F (if attached) a 3D render of the creature's own game model in this pose - only its motion, never its thin proportions or 3D shading.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images D and E: a {A.CANVAS}x{A.CANVAS} PNG with a real transparent background (alpha only 0 or 255), every square exactly {A.PX} px - the SAME square size as image A - aligned on one straight grid from the canvas corner; each part exactly where and at the angle D and E put it, at the same height above the red ground line.
EACH SHARD IS IMAGE A'S SHARD: the same shape, size, colours and flat facets, only moved and turned - redraw its turned edges CLEAN (a tidy continuous near-black outline, flat facets), never copy the jagged rotation; never shrink or stretch a shard. Where the shards have moved apart the space between them is EMPTY (transparent): they are two separate stones; the inner face of a shard its own darkest shade inside the outline. The CORE as big as the layout shows it: its bright blue rings are the core glowing bigger, white in the middle at its brightest; where the pose line says it dims or goes out, make it dark.
The same colours as image A; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no laser, no bolt, no beam, no rubble, no dust, no motion lines, no glow halo outside the core), no background, no ground, no shadow, no text, no grid lines, no guide colours.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

"""

TAIL = f"""
## 交回

- 每个姿势一张：`outputs/sentry-poses/sentry-pose-<名字>.png`（{A.CANVAS} × {A.CANVAS}、真透明背景、每格 {A.PX} px）。
- 原始生成图原样放进 `outputs/sentry-poses/raw/`。
- `generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **{N} 张都画完再交**。最后写 `outputs/sentry-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sentry_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sentry/codex_poses/`，**先量 Codex 实际的格子**（不一定是 {A.PX} px），读 raw。
- **每张按定稿的石头大小读**（codex-fit-shrinks-bodies：分开、张开、倒地时 Codex 容易把石头画小）：以两块石头各自的高度对齐定稿。
- 每帧放大 8 倍检查：两块石头是定稿的形状和颜色；分开处是透明的；蓝核大小随姿势变；没有特效。
- 布局包：`tools/art/pack_sentry_poses.py`（定稿拆成左石、右石、蓝核三块，按 POSES 挪动、转动、加光圈）。这份提示词由 `tools/art/gen_sentry_pose_md.py` 生成。
"""


def main():
    rows, lines = [], []
    for k, (name, (_moves, clip, zh, en)) in enumerate(A.POSES.items()):
        rows.append(f"| {k + 2} | `sentry-pose-{name}.png` | {clip or '布局图'} | {zh} |")
        lines.append(f"- {name}: `{en}`")
    text = HEAD + "\n".join(rows) + "\n" + PROMPT + "\n".join(lines) + "\n" + TAIL
    path = os.path.join(ROOT, "assets", "source", "sentry", "POSE_PROMPTS.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(path, len(text))


if __name__ == "__main__":
    main()
