# 诺提勒斯：只重画腿——跑步 8 帧换腿 + 待机直立（给 Codex 的提示词）

> **为什么重画**：上一轮的侧身跑步 8 帧里**始终是同一条腿在前**（像小跳步），没有换腿的画面；用这些帧拼出来的换腿，
> 要么一帧之内腿从后面跳到前面，要么跑到一半两腿并拢像停下来站了一下；待机也只能拿其中一条腿复制一份。
> 用户：「走路压根看不出换腿」「这交叉步看着好怪啊」「走路的时候看着还有点怪」「待机动作你看了不奇怪吗」
> 「待机时腿不要岔开啊 直立站那不就行了 你看oppi的泰坦啊」。
> **上半身（头盔、胸甲肩甲、两只手、背上的锚）已经定稿，一个像素都不要动。只画腰带以下：胯、大腿、护膝、小腿、靴子。**

## 交给你的文件

- `inputs/body_run_1x.png`：跑步 8 帧（4 列 x 2 行，每格 128x128，1 像素 = 游戏里 1 格），**每格里已经放好了这一帧的上半身**，
  画到腰带（青色灯带那一行）为止，下面是空的——你在下面画腿。上半身随步伐上下浮动 1 行，已经放在正确的高度。
- `inputs/body_idle_1x.png`：待机 1 格，上半身同上。
- `inputs/guide_run.png`、`inputs/guide_idle.png`：每一帧两条腿该在哪里——**橙色线是近侧腿，蓝色线是远侧腿**
  （胯 → 膝盖 → 脚踝，圆点是脚踝），**红线是地面**（靴底的黑色描边落在这一行，第 99 行）。
- `inputs/now_run_1x.png`、`inputs/now_idle_1x.png`：现在的样子（腿的颜色、粗细、靴子的画法照这个，**换腿的方式不要照这个**）。
- `inputs/palette.png`：只用这 23 种颜色。
- `refs/lol_walk_legs.png`：英雄联盟里诺提勒斯走路的腿（沉重、步子不大、抬膝跺脚）；
  `refs/oppi_nautilus_run.png`、`refs/oppi_nautilus_idle.png`：oppi 画的诺提勒斯（待机两腿并拢直立）。

## 要求

1. **只画腰带以下**；腰带那一行和以上（包括锚、手）的像素原样保留。胯部要和上半身的下边缘严丝合缝（没有缝、没有台阶、不歪）。
2. **腿就是现在这双腿**：深灰黑的潜水服、膝盖正面的青铜护膝、巨大的潜水靴（厚青铜鞋底，鞋尖朝画面右边）；
   粗细、长短和 `now_run_1x.png` 一样，每一帧都一样（不压扁、不拉长、不变形）；膝盖弯就画成弯的腿。
3. **跑步是真正的换腿**（侧身朝右）：第 1-4 帧近侧腿领先——1 着地（近侧脚在前落地，远侧腿在后蹬地）、2 下沉（近侧脚踩在身下，远侧脚在后面抬起）、
   3 交错（近侧腿直立在身下，远侧腿弯着从身下向前摆，脚离地）、4 腾起（近侧腿在后蹬，远侧腿膝盖抬起向前伸）；
   **第 5-8 帧同样的动作换成远侧腿领先**。按 `guide_run.png` 的骨架画，两条腿每帧都只移动一点，连起来是顺的，不能一帧之内跳过去。
4. **近侧腿用现在近侧腿的颜色，远侧腿整条暗一档**（同一套颜色里往暗一级），两腿重叠的地方远侧腿在后面被挡住。
5. **落地的脚靴底描边在第 99 行**，抬起的脚离地 2-4 行；步子不比现在第 1 帧更大，沉重、短促，像英雄联盟里那样。
6. **待机**：两腿并拢直立（近侧腿在前一点，远侧腿紧挨在后面，两只靴子都平踩在第 99 行），不岔开，像 oppi 的诺提勒斯；静止的一帧。
7. 像素风规则：1 像素 = 1 格，1 像素黑色描边（#070211），不要抗锯齿、不要半透明、不要新颜色。

## 交付

- `run_1x.png`：512x256（4 列 x 2 行，每格 128x128），8 帧完整画面（你的腿 + 原样的上半身），透明背景；
- `idle_1x.png`：128x128，同上；
- 再各给一张放大 8 倍的预览图，方便我对照。

## Prompt (English)

Redraw ONLY the legs of this pixel-art character (Nautilus in a heavy diving suit, side view facing right), 1 px = 1 game
pixel, the 23 colours of palette.png only, 1-px outline #070211, no anti-aliasing. Every cell of body_run_1x.png already
holds the finished upper body down to the belt (the teal light): keep every one of those pixels; draw the hips, thighs,
bronze knee guards, shins and big diving boots below it, joined to the body's lower edge without a gap or a step. The
legs are the legs of now_run_1x.png (same colours, thickness, length, boots pointing right), but the run must CHANGE LEGS:
frames 1-4 the near leg leads (1 contact: near foot forward on the ground, far leg pushing off behind; 2 down: near foot
planted under him, far foot lifting behind; 3 passing: near leg straight under him, far leg swinging forward under the
body with the knee bent, foot off the ground; 4 up: near leg pushing off behind, far knee raised reaching forward),
frames 5-8 the same with the far leg leading - follow guide_run.png (orange = near leg, blue = far leg, red = the ground,
row 99). Small steps every frame so the cycle plays smoothly, heavy and short like League's Nautilus (lol_walk_legs.png).
The near leg in the current near-leg colours, the far leg one shade darker and behind it where they overlap. Planted
soles on row 99, lifted feet 2-4 rows up. Idle (body_idle_1x.png, guide_idle.png): one frame standing upright, legs
straight and together, the near leg a little in front, both boots flat on row 99 - like oppi's Nautilus. Deliver
run_1x.png (512x256, 4x2 cells of 128x128) and idle_1x.png (128x128), transparent, plus 8x previews.
