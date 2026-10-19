# 妖姬：跑步的腿和裙摆（第 2 轮，腿照待机的画；给 Codex 的提示词）

> **用画图模型（image_gen）画。**上一轮画的腿是**棕色丝袜配棕色高跟鞋**，又细又长，和她站着时的腿完全不一样（用户：「腿有点变形啊 待机的腿和走路的腿不一样？」）。这一轮**腿一定要照她站着时的腿画**（`2_lower_sample.png`），骨架和上一轮一样。
> - `1_run_body.png`（8 格）：妖姬定稿的身体，**腰带以下的裙子和腿已经去掉**（身后垂着的红色披风还在，**不要改**），法杖拿掉了，每格 6 px 一个像素方块，绿色背景。
> - `1_run_guide.png`：同一张加了**骨架线**：**红线 = 近侧的腿（画面左边那条，颜色亮）**，**蓝线 = 远侧的腿（暗一档）**；圆点依次是**髋、膝、踝**，最后一段短线是脚。深绿横线是地面。
> - `2_lower_sample.png`：**她站着时腰带以下的样子（8 倍）——腿就照这个画**：
>   - **大腿是光着的浅肤色**（不是丝袜），约 **4 格宽**，大腿中间斜着**一道深色细绑带**；
>   - **从膝盖往下是深蓝色的长靴**，靴子两边是**金色的饰边**，膝盖处一圈金色，靴底有跟；小腿约 **4 格宽**；
>   - 裙子是深蓝色长裙，金边，酒红色内衬和裙片；**裙子只在正前方开衩**，从开衩里露出近侧的大腿，远侧的腿大部分被裙子挡住。
> - `3_run_lol.png`：英雄联盟原版她跑步的 8 帧，只看腿和裙摆的感觉。

## 要画什么

在 `1_run_body.png` 上**只加腰带以下**（两条腿 + 长裙的下半截），交出一张和原图一样大小、一样排列的图：

- `leblanc-legs2-run.png`（1680 × 1152，4 × 2 格）：跑步 8 帧，两腿一前一后交叉迈步（剪刀步），着地的腿笔直，抬起的腿屈膝；红、蓝两条腿每半圈换一次前后。**裙子还是和站着时一样的长裙**，迈步时前面的开衩被腿撑开一些、裙摆向后摆，**不要整片敞开、不要变成短裙**。

## 规则

- **腿的样子、颜色、粗细和 `2_lower_sample.png` 里站着的腿一模一样**：浅肤色光腿 + 斜绑带、膝盖以下深蓝金边长靴；**不要画丝袜、不要画棕色的腿或棕色的鞋**。
- **每条腿沿着它的骨架线画**：大腿从髋点到膝点，小腿从膝点到踝点，靴子从踝点朝短线的方向；**长度就是骨架的长度**；大腿约 4 格宽、小腿约 4 格宽，不要画长、画短、画粗、画细，弯曲只在膝盖和脚踝处。
- 远侧（蓝线）那条腿暗一档、在近侧（红线）后面，大部分被裙子挡住；近侧那条从开衩里露出来。
- **腰带以上的身体、手臂和身后的红披风一格都不要改**（直接照抄 body 图），裙子接在腰带下面，和身体的描边连成一圈。
- **8 帧的裙子用同样的颜色、同样的金边样式**，只是摆动不同。
- 像素画：**每个方块 6 px，和 body 图的方块对齐**；1 格近黑描边；每种材质 2–3 档平涂；不要抗锯齿、渐变、模糊。
- **背景保持纯绿色 #00FF00**；**交出的图上不要有红线、蓝线、圆点**；图的大小一定要是 **1680 × 1152**。

## 提示词（附上表里的全部图）

```text
Attached: 1_run_body shows an approved pixel-art character (a sly sorceress: a dark blue bob with a gold spiked crown, golden eyes, a gold collar, a deep navy gown with gold trims and wine-red panels, long dark gloves; her staff left out) in eight cells, every square 6 px, on pure green - EVERYTHING BELOW HER GOLD BELT IS REMOVED (the red cape hanging at her back, on the image left, stays: keep it). 1_run_guide is the same with a SKELETON for each leg: RED = the near leg (in front, full tone), BLUE = the far leg (behind, a step darker); the dots are hip, knee and ankle, the short last line is the foot; the dark green line is the ground. 2_lower_sample is HER OWN LOWER HALF STANDING, enlarged - DRAW HER LEGS EXACTLY LIKE THESE: a BARE PALE-SKINNED THIGH (no stockings) about 4 squares wide with one thin dark strap across it, and from the knee down a DEEP NAVY BOOT with GOLD trims down both sides, a gold band at the knee and a heel; the shin about 4 squares wide; the long deep navy gown with gold trims and wine-red lining, slit ONLY at the front, showing the near thigh, the far leg mostly hidden by the gown. 3_run_lol is the original 3D character running (the feel only).
Draw with the image generator the body image again with ONLY HER LOWER HALF added below the belt: her TWO LEGS drawn EXACTLY AS IN THE SAMPLE (bare pale thighs with the strap, navy gold-trimmed knee boots - NO stockings, NO brown legs, NO brown shoes), each ALONG ITS SKELETON - the thigh from the hip dot to the knee dot, the shin from the knee dot to the ankle dot, the boot from the ankle along the short line, EXACTLY the skeleton's lengths, the thigh and the shin about 4 squares wide, never longer, shorter, thicker or thinner, bending only at the knee and the ankle - and the SAME LONG GOWN as in the sample over them: the front slit opened a little by the striding legs, the hem swinging back, the gown still long (to about the ankles), NOT opened wide, NOT a short skirt. The far (blue) leg a step darker, behind the near (red) one and mostly hidden by the gown. Everything above the belt, the arm and the red cape stay EXACTLY as in the body image (copy them square for square); the gown joins the belt with the outline continuous; the gown has the same colours and gold trim pattern in all eight cells, only its swing differs. Every square 6 px aligned with the body image's squares; a 1-square near-black outline; 2-3 flat shades a material; no anti-aliasing, no gradients, no blur. Keep the background pure green #00FF00; NO red or blue lines and NO dots in the result. Output EXACTLY 1680 x 1152 pixels, 4 x 2 cells, the same layout as the body image.
A running scissor stride - the leg on the ground STRAIGHT, the lifted leg bent at the knee, the two legs swapping front and back every half cycle, exactly as the skeletons show.
```

## 交付（`outputs/leblanc-legs2/`）

- `leblanc-legs2-run.png`；原始生成图放 `raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/leblanc_legs2_done.zip`。

## Claude 收到后（给 Claude 看）

- `import_leblanc_legs.py --sheet` 读回：上半身逐格对齐，只取腰带以下，颜色归到定稿调色板（这次腿的颜色定稿里都有，不再加新色）；8 倍逐帧和待机的腿比宽度、颜色、靴子样子，和骨架比长度，差一格以上的退回。
