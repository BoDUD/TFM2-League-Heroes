# 妖姬：跑步的腿和裙摆（按骨架画；给 Codex 的提示词）

> **用画图模型（image_gen）画。**妖姬的高清造型定好了，动作也摆好了，但跑步时她的腿一直不动（腿藏在长裙里）。这次请**只画腰带以下：两条腿和长裙的下半截**，跑步 8 帧，**每条腿都沿着骨架线画**，骨架的长度就是定稿里她腿的长度。
> - `1_run_body.png`（8 格）：妖姬定稿的身体，**腰带以下的裙子和腿已经去掉**（她身后垂着的红色披风还在，**不要改**），法杖也拿掉了（不用画），每格 6 px 一个像素方块，绿色背景。
> - `1_run_guide.png`：同一张加了**骨架线**：**红线 = 近侧的腿（画面左边那条，颜色亮）**，**蓝线 = 远侧的腿（暗一档）**；圆点依次是**髋、膝、踝**，最后一段短线是脚（鞋尖的方向）。深绿横线是地面。
> - `2_lower_sample.png`：定稿里她自己腰带以下的样子（8 倍）——**裙子和腿就照这个样子画**：深蓝色长裙、金色的饰边、酒红色的内衬和裙片，裙子前面高开衩，露出近侧的大腿（浅肤色）；腿上是深色丝袜，**深蓝色带金饰的高跟靴**。
> - `3_run_lol.png`：英雄联盟原版她跑步的 8 帧，只看腿和裙摆的感觉。

## 要画什么

在 `1_run_body.png` 上**只加腰带以下**（两条腿 + 长裙的下半截），交出一张和原图一样大小、一样排列的图：

- `leblanc-legs-run.png`（1680 × 1152，4 × 2 格）：跑步 8 帧，**两腿一前一后交叉迈步（剪刀步）**，着地的腿**笔直**，抬起的腿屈膝；红、蓝两条腿每半圈换一次前后。**长裙跟着腿动**：迈开时前面的开衩被撑开、露出腿，裙摆向后飘，裙子的长度到脚踝附近（和样图一样长），不要拖地太多，也不要变短。

## 规则

- **每条腿沿着它的骨架线画**：大腿从髋点到膝点，小腿从膝点到踝点，靴子从踝点朝短线的方向；**长度就是骨架的长度**，大腿约 4 格宽、小腿约 3 格宽，不要画长、画短、画粗、画细，弯曲只在膝盖和脚踝处。
- 两条腿画得一样（深色丝袜、金饰高跟靴），远侧（蓝线）那条暗一档、在近侧（红线）后面；裙子盖在腿的上半截外面，从开衩里露出腿。
- **腰带以上的身体、手臂和身后的红披风一格都不要改**（直接照抄 body 图），裙子接在腰带下面，和身体的描边连成一圈。
- **8 帧的裙子用同样的颜色、同样的金边样式**，只是摆动不同；不要每帧换花纹。
- 像素画：**每个方块 6 px，和 body 图的方块对齐**；1 格近黑描边；每种材质 2–3 档平涂；不要抗锯齿、渐变、模糊。
- **背景保持纯绿色 #00FF00**；格子之间的深绿分隔线可以保留；**交出的图上不要有红线、蓝线、圆点**。

## 提示词（附上表里的全部图）

```text
Attached: 1_run_body shows an approved pixel-art character (a sly sorceress: a dark blue bob with a gold spiked crown, golden eyes, a gold collar, a deep navy gown with gold trims and wine-red panels, long dark gloves; her staff left out) in eight cells, every square 6 px, on pure green - EVERYTHING BELOW HER GOLD BELT IS REMOVED (the red cape hanging at her back, on the image left, is still there: keep it). 1_run_guide is the same with a SKELETON for each leg: RED = the near leg (in front, full tone), BLUE = the far leg (behind, a step darker); the dots are hip, knee and ankle, the short last line is the foot (the shoe's direction); the dark green line is the ground. 2_lower_sample is her own lower half enlarged: the deep navy long gown with gold trims and wine-red lining and panels, slit high in front showing the near leg's pale thigh, dark sheer stockings and NAVY HIGH-HEELED BOOTS WITH GOLD ORNAMENTS. 3_run_lol is the original 3D character running (the feel of the legs and the gown only).
Draw with the image generator the body image again with ONLY HER LOWER HALF added below the belt: her TWO LEGS, each drawn ALONG ITS SKELETON - the thigh from the hip dot to the knee dot, the shin from the knee dot to the ankle dot, the boot from the ankle along the short line, EXACTLY the skeleton's lengths, the thigh about 4 squares wide and the shin about 3, never longer, shorter, thicker or thinner, bending only at the knee and the ankle - and the LONG GOWN over them as in the sample, moving with the stride: the front slit opened by the striding legs showing them, the hem swinging back, the gown reaching about the ankles as in the sample. Both legs drawn the same way (dark stockings, gold-trimmed heeled boots), the far (blue) one a step darker and behind the near (red) one. Everything above the belt, the arm and the red cape stay EXACTLY as in the body image (copy them square for square); the gown joins the belt with the outline continuous; the gown has the same colours and the same gold trim pattern in all eight cells, only its swing differs. Every square 6 px aligned with the body image's squares; a 1-square near-black outline; 2-3 flat shades a material; no anti-aliasing, no gradients, no blur. Keep the background pure green #00FF00 (the dark green cell lines may stay); NO red or blue lines and NO dots in the result. Same size and layout as the body image (1680 x 1152, 4 x 2 cells).
A running scissor stride - the leg on the ground STRAIGHT, the lifted leg bent at the knee, the two legs swapping front and back every half cycle, exactly as the skeletons show.
```

## 交付（`outputs/leblanc-legs/`）

- `leblanc-legs-run.png`；原始生成图放 `raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/leblanc_legs_done.zip`。

## Claude 收到后（给 Claude 看）

- 按 6 px 读回，去绿、颜色归到定稿的调色板；**只取腰带以下**（披风以外的方块），身体、手臂和披风用定稿原样；每条腿量大腿、小腿的长度和宽度，和骨架差一格以上的退回；8 倍逐帧看接缝、缺口（gap-check）、裙子的花纹前后是否一致。跑步取代 rig 里只挪整个人的走路，法杖照 rig 平端在身后。
