# 奎因：腿（第 2 轮，按骨架画；给 Codex 的提示词）

> **用画图模型（image_gen）画。**上一轮的腿用户说「各种变形」：伸直的腿比原来长了三成、跪姿把腿压成一团、每张都重画了披风下摆、膝盖和靴子每张形状都不一样。这一轮**每条腿都按骨架线画**，骨架的长度就是定稿腿的长度。
> - `1_poses_body.png`（6 格）和 `2_run_body.png`（8 格）：奎因定稿的身体，**腿已经去掉**（披风下摆还在，**不要改**），每格 7 px 一个像素方块，绿色背景。
> - `1_poses_guide.png`、`2_run_guide.png`：同一张加了**骨架线**：**红线 = 近侧的腿（画面左边那条，颜色亮）**，**蓝线 = 远侧的腿（暗一档）**；圆点依次是**髋、膝、踝**，最后一段短线是脚（靴尖的方向）。深绿横线是地面。
> - `3_legs_sample.png`：定稿里她自己的两条腿（8 倍）——**就照这个样子画**：深紫色护腿（边上一圈偏亮的紫）、膝盖和小腿前面的**金色护板**、**尖头深棕靴子**；**大腿约 4 格宽、小腿约 3 格宽、靴子约 4 格长 3 格高**。
> - `4_poses_lol.png`、`5_run_lol.png`：英雄联盟原版的这些动作，只看腿的感觉。

## 要画什么

在 `*_body.png` 上**只加两条腿**，交出两张和原图一样大小、一样排列的图：

1. `quinn-legs2-poses.png`（1386 × 812，3 × 2 格）：下蹲、单膝跪地（近侧膝盖和小腿贴地）、向前弓步（后腿伸直）、宽站、空中收腿、两脚并拢。
2. `quinn-legs2-run.png`（1848 × 812，4 × 2 格）：跑步 8 帧，**两腿一前一后交叉迈步（剪刀步）**，着地的腿**笔直**，抬起的腿屈膝；红、蓝两条腿每半圈换一次前后。

## 规则

- **每条腿沿着它的骨架线画**：大腿从髋点到膝点，小腿从膝点到踝点，靴子从踝点朝短线的方向；**长度和粗细就是骨架和样图的**，不要画长、画短、画粗、画细，弯曲只在膝盖和脚踝处。
- 两条腿画得一模一样（同样的护腿、护板、靴子），只是远侧（蓝线）那条暗一档；近侧（红线）那条画在远侧的前面。
- **身体和披风下摆一格都不要改**（可以直接照抄 body 图），腿接在腰下面，和身体的描边连成一圈。
- 像素画：**每个方块 7 px，和 body 图的方块对齐**；1 格近黑描边；每种材质 2–3 档平涂；不要抗锯齿、渐变、模糊。
- **背景保持纯绿色 #00FF00**；格子之间的深绿分隔线可以保留；**交出的图上不要有红线、蓝线、圆点**。

## 提示词（两张各一次；附上表里的全部图）

```text
Attached: 1_poses_body / 2_run_body show an approved pixel-art character (a young woman ranger: gold winged visor, deep-blue hood, gold feather pauldron, blue-violet cape, brown leather corset, a gold and steel crossbow held out to the right) in a grid of cells, every square 7 px, on pure green - her LEGS ARE REMOVED (the cape's hem is still there: keep it). 1_poses_guide / 2_run_guide are the same with a SKELETON for each leg: RED = the near leg (in front, full tone), BLUE = the far leg (behind, a step darker); the dots are hip, knee and ankle, the short last line is the foot (the boot tip's direction); the dark green line is the ground. 3_legs_sample is her own two legs enlarged: dark violet greaves with a lighter violet edge, GOLD KNEE AND SHIN PLATES on the front, POINTED DARK BROWN BOOTS; the thigh about 4 squares wide, the shin about 3, the boot about 4 long and 3 tall. 4_poses_lol / 5_run_lol are the original 3D character in these moves (the feel of the legs only).
Draw with the image generator the body image again with ONLY her TWO LEGS added, each drawn ALONG ITS SKELETON: the thigh from the hip dot to the knee dot, the shin from the knee dot to the ankle dot, the boot from the ankle along the short line - EXACTLY the skeleton's lengths and the sample's widths, never longer, shorter, thicker or thinner, bending only at the knee and the ankle; both legs drawn the same way as the sample (greaves, gold plates, pointed boots), the far (blue) one a step darker and behind the near (red) one. The body and the cape's hem stay EXACTLY as in the body image (copy them square for square); the legs join the waist with the outline continuous. Every square 7 px aligned with the body image's squares; a 1-square near-black outline; 2-3 flat shades a material; no anti-aliasing, no gradients, no blur. Keep the background pure green #00FF00 (the dark green cell lines may stay); NO red or blue lines and NO dots in the result. Same size and layout as the body image.
For the run sheet: a running scissor stride - the leg on the ground STRAIGHT, the lifted leg bent at the knee, the two legs swapping front and back every half cycle, exactly as the skeletons show.
```

## 交付（`outputs/quinn-legs2/`）

- `quinn-legs2-poses.png`、`quinn-legs2-run.png`；原始生成图放 `raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/quinn_legs2_done.zip`。

## Claude 收到后（给 Claude 看）

- 按 7 px 读回，去绿、颜色归到定稿的调色板；**只取腿**（腰线以下、披风下摆以外的方块），身体和披风用定稿原样；每条腿量一下大腿、小腿的长度和宽度，和骨架、样图差一格以上的退回；8 倍逐帧看接缝、缺口（gap-check）。跑步取代 rig 里只挪腿的走路。之前的跑步换皮包（`quinn_run_pack.zip`）不用再给 Codex。
