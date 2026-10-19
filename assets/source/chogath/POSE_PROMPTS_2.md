# 虚空恐惧 科加斯：动作姿势第 2 轮（只重画 3 张，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 1 轮 7 张里，**蓄力、扑咬、瘫倒、侧躺**按游戏比例读回后和定稿一致，**保留不动**。
> - **半起身、直立、下砸**三张按游戏比例读回后（`*_readback_8x.png`，左边是定稿侧面、右边是你的图，同样 8 倍）：**后腿太细太长**（只有约 3 格粗，定稿约 5 格），**直立的身子太瘦**（像一根细杆顶着头），**头画小了**（只有定稿的六成）。
> - 请**保留第 1 轮的姿势**（`*_round1.png`），**只把身体画成定稿的体型**：
>   - **头**：照 `B_idle_head.png` 逐格画，**和定稿一样大：24 × 21 格**（每格 16 px 时是 384 × 336 px）。
>   - **躯干**：和定稿侧面（`A_side_design_8x.png`）一样厚——从肚子到背（不算骨刺）约 **18–20 格**；直立时这个厚度变成身子的宽度，不要画成细杆。
>   - **后腿**：和定稿一样**粗短**——大腿和小腿约 **5 格粗**，从胯到脚底约 **11–12 格**（直立时也一样长，不要拉长）；红钩爪和定稿一样大。
>   - **前爪、镰刀臂、尾巴**：和定稿一样粗、一样长。
> - 画布 **1254 × 1254**，**每格 16 px**（每个方块 16 × 16 px，不要更小的格子），着地的脚在 **y = 1120**。真透明背景，alpha 只有 0 / 255。

## 提示词（每张一次，换最后一行）

每次上传：`A_side_design_8x.png`、`B_idle_head.png`、这张的 `*_round1.png`、这张的 `*_readback_8x.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED side view of this character, shown 8x (every 8x8 block is one square): a huge void beast with a THICK carapaced body, SHORT THICK legs and a BIG head; B its HEAD, 8x (24 squares wide, 21 tall); C YOUR earlier drawing of this pose - the POSE is right, keep it; D your drawing brought to the game's size beside the approved design at the same scale: its hind legs are too THIN and LONG and its body too SLIM, its head too small.
Redraw image C with the image generator as ONE clean pixel-art picture, the SAME POSE, but with the BODY OF IMAGE A: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px on one straight grid from the canvas corner (never smaller squares), the feet on the ground at y 1120.
THE HEAD: image B copied square for square at its full size, 24 x 21 squares (384 x 336 px), the face to the front-right, both cyan eyes, the open maw, the fangs, the tongue, the tusks.
THE TORSO as thick as image A's body: about 18-20 squares from the belly to the back (not counting the spikes) - when he stands upright that thickness is the body's WIDTH; never a thin stalk.
THE HIND LEGS as SHORT and THICK as image A's: thigh and shin about 5 squares thick, about 11-12 squares from the hip to the sole, the red hooked talons as big as in image A; the front claws, the scythe arms and the tail as thick and long as in image A.
The same colours as image A: the carapace in its 3 violet-purples, the plate edges in its 3 wine-reds, the dark legs with lighter edges; one continuous 1-square near-black outline; the near parts in full tone, the far parts a step darker; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text.
THE POSE: <one line below>
```

- rise: `RISE (as image C) - pushing up on the hind legs, the upper body lifted about 45 degrees, the front claws off the ground, the scythe arms raised high.`
- rear: `REAR (as image C) - standing upright on the two short thick hind legs, the thick body vertical, the front claws held up in front of the chest, both scythe arms raised high and spread apart, the tail on the ground behind.`
- slam: `SLAM (as image C) - the whole body thrown forward and down to the image right, the head and the front claws striking the ground, the short thick hind legs pushing back, the tail raised high, the scythe arms slashing forward and down.`

## 交回前请检查

- 3 张都是 image_gen 画的；1254 × 1254；真透明背景；**每格 16 px**。
- 头 24 × 21 格（和定稿一样大）；躯干和定稿一样厚；后腿约 5 格粗、胯到脚底约 11–12 格；姿势和第 1 轮一样。

## 交付（`outputs/chogath-poses2/`）

- `chogath-pose-rise.png`、`chogath-pose-rear.png`、`chogath-pose-slam.png`；原始生成图放 `outputs/chogath-poses2/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/chogath_poses2_done.zip`。

## Claude 收到后（给 Claude 看）

- design_chogath_poses.py 读回（同样按面积定比例）；8 倍下量后腿粗细长短、躯干厚度、头的大小，和定稿比；合格再接进 rig_chogath.py。
