# 纳祖芒荣耀 奎桑提：跑步重画 3 张（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 你上一轮画的跑步，两条腿没有轮流迈步：普通跑步的 run1 和 run3 都是**同一条腿**在前面踩地、另一条腿在后面；全盛跑步的 ao-run1 和 ao-run3 也一样，ao-run2 和 ao-run4 都是**同一边的膝盖**抬起来。连起来播，他像一条腿在跳。
> - 所以请重画 **3 张**，每张都是**它的搭档帧原样再画一遍，只把两条腿对调**：身体、头、手臂、两把陀斧（长棍）的位置、大小、颜色、角度**全部和搭档帧一样**，只有腿换：
>   - `ksante-pose-run3.png`：照 `partner_for_run3.png`（你画的 run1）。run1 里**在前面踩地的那条腿改成在后面、脚抬起往后蹬**；**在后面的那条腿改成迈到前面踩地**。
>   - `ksante-pose-ao-run3.png`：照 `partner_for_ao_run3.png`（你画的 ao-run1），同样把前后两条腿对调。
>   - `ksante-pose-ao-run4.png`：照 `partner_for_ao_run4.png`（你画的 ao-run2）。ao-run2 里**抬起膝盖的是哪条腿，就改成另一条腿抬膝盖**，原来抬膝的那条腿改成踩在身体下面撑地。
> - 近侧的腿（画面左边那条）颜色全亮，远侧的腿（画面右边那条）暗一档；**迈到前面的近侧腿会从远侧腿前面交叉过去**，它在前面挡住远侧腿，不要把两条腿画成左右镜像。腿的粗细、长短、护膝、靴子和搭档帧一样，**不要拉长或压短**；着地的脚在 y 1180（红线）。
> - 每张附了这一帧原来的骨架（`*_skeleton.png`）和英雄联盟原版那一帧（`*_league.png`）作参考；定稿（`2_design_*.png`）和头（`1_head_*.png`）照旧。

## 提示词（每张一次）

每次上传：这张的 `partner_for_*.png`、这张的 `*_skeleton.png`、`*_league.png`、对应姿态的 `2_design_*.png` 和 `1_head_*.png`。**用 image_gen 画。**

```text
Attached images: A your own earlier pixel-art frame of this character running (the PARTNER frame), 1254x1254, 10 px squares, soles on y 1180; B the skeleton of the frame to draw now (red = the NEAR leg, image left; blue = the FAR leg, image right); C the original character in this run frame (only for the feel); D the approved design; E its head.
Draw with the image generator ONE clean pixel-art picture: image A AGAIN with ONLY THE TWO LEGS EXCHANGED. The head, the face, the body, both arms, both weapons (their place, size, angle and colours), the outline and the square size stay EXACTLY as in image A. Only the legs change: <THE LEG LINE BELOW>. The near leg (image left) in full tone, the far leg (image right) a step darker; a near leg stepping forward crosses IN FRONT of the far leg - never draw the two legs as a left-right mirror image. Each leg the SAME thickness and length as in image A, with the same knee guard and boot; never stretch or shorten a leg. The foot on the ground on y 1180.
A 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square 10 px on one grid from the canvas corner; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing; no effects, no ground, no shadow, no text, no grid lines, no skeleton lines.
```

每张最后换成这一句（英文）：

- run3（照 `partner_for_run3.png`）：`the leg that is planted forward in image A now trails BEHIND him, its foot lifted, pushing off; the leg that trails behind in image A now steps FORWARD and plants its foot on the ground ahead of him.`
- ao-run3（照 `partner_for_ao_run3.png`）：`the leg that is planted forward in image A now trails BEHIND him, its foot lifted, pushing off; the leg that trails behind in image A now steps FORWARD and plants its foot on the ground ahead of him.`
- ao-run4（照 `partner_for_ao_run4.png`）：`the leg whose knee is lifted forward in image A now stands UNDER him carrying his weight, its foot flat on the ground; the leg that stands under him in image A now swings forward with its KNEE LIFTED.`

## 交回前请检查

- 3 张都是 image_gen 画的；1254 × 1254；alpha 只有 0 / 255；每格 10 px。
- 和搭档帧比：**只有腿不一样**，头、身体、手臂、武器一模一样；前后腿确实对调了（不是同一条腿在前）；近侧腿亮、远侧腿暗；腿的粗细长短和搭档帧一样；着地的脚在 y 1180。

## 交付（`outputs/ksante-run-redo/`）

- `ksante-pose-run3.png`、`ksante-pose-ao-run3.png`、`ksante-pose-ao-run4.png`；原图放 `raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ksante_run_redo_done.zip`。

## 附图（压缩包 `ksante_run_redo_pack.zip` 里）

| 文件 | 内容 |
|---|---|
| `partner_for_run3.png` / `partner_for_ao_run3.png` / `partner_for_ao_run4.png` | 你画的 run1 / ao-run1 / ao-run2：照它原样画，只对调两条腿 |
| `run3_skeleton.png` / `ao_run3_skeleton.png` / `ao_run4_skeleton.png` | 这一帧原来的骨架 |
| `run3_league.png` / `ao_run3_league.png` / `ao_run4_league.png` | 英雄联盟原版那一帧 |
| `2_design_base.png` / `2_design_ao.png`、`1_head_base.png` / `1_head_ao.png`、`0_design_skeleton_*.png` | 两个定稿、两个头、定稿上的骨架 |

## Claude 收到后（给 Claude 看）

- 读回（design_ksante_poses.py，按身体面积定格子、贴定稿的头），在 8 倍下和搭档帧比：只有腿变了、前后腿对调了；再排成 run1 → run2 → run3 → run4 和 ao_run1 → ao_run2 → ao_run3 → ao_run4 看循环是左右腿轮流。
