# 泽丽：只重画跑步的腿——8 帧换腿，腿要是设计稿那双腿（给 Codex 的提示词）

> **为什么重画**：现在的跑步腿是程序按英雄联盟斜侧视角的关节角度「画骨头」画出来的细腿，**跟设计稿的腿完全不是一个形状**，
> 投影到侧面后两条腿交叉打结、一只靴子踩在另一只上或整个被挡住，身体还跟着英雄联盟的跳步上下跳 3 行。
> 用户：「泽丽走路时候模型怪」「应该是腿部完全变形的原因」。
> **上半身（头、头发、外套、两只手、端平的枪）已经定稿，一个像素都不要动。只画腰带以下的腿：紧身裤、膝盖上的浅色补丁、靴子。**

## 交给你的文件

- `inputs/body_run_1x.png`：跑步 8 帧（4 列 x 2 行，每格 96x80，1 像素 = 游戏里 1 格），**每格已经放好这一帧的上半身**
  （外套下摆的两片和垂着的手也在），腰带以下是空的——你在下面画腿。上半身在第 3、4、7、8 帧抬高 1 行，已经放好。
- `inputs/design_legs.png`（放大 16 倍）、`inputs/idle_1x.png`：**设计稿的腿就是这双腿**——深酒红色紧身裤（亮/暗两层），近侧膝盖一块浅棕色补丁，
  棕色靴子（橙黄色鞋扣和鞋底高光），粗细、长短、靴子的形状照这个画，每一帧都一样。
- `inputs/guide_run.png`：每一帧两条腿该在哪里——**橙色线是近侧腿，蓝色线是远侧腿**（胯 → 膝盖 → 脚踝），**红线是地面**
  （靴底的黑色描边落在这一行）。
- `inputs/now_run_1x.png`：现在的样子（错误示范：细腿、打结、靴子叠在一起）。
- `inputs/palette.png`：只用这 26 种颜色。

## 要求

1. **只画腰带以下**，上半身的像素原样保留；外套下摆在腿的前面，腿从下摆下面伸出来；胯和腰带严丝合缝。
2. **腿就是设计稿那双腿**：紧身裤的粗细和设计稿一样（不细成一根线、不像橡皮筋一样弯），靴子是设计稿的整只靴子、形状不变；
   弯膝盖就画成弯的腿，但大腿、小腿的粗细不变。
3. **跑步是真正的换腿**（身体朝右的侧身跑）：第 1-4 帧近侧腿领先——1 着地（近侧脚在前落地，远侧腿在后蹬地）、
   2 下沉（近侧脚踩在身下，远侧脚在后面抬起）、3 交错（近侧腿直立在身下，远侧腿弯着从身下向前摆，脚离地）、
   4 腾起（近侧腿在后蹬，远侧腿膝盖抬起向前伸）；**第 5-8 帧同样的动作换成远侧腿领先**。按 `guide_run.png` 画，
   每帧只移动一点，连起来是顺的。
4. **近侧腿用设计稿的颜色（膝盖补丁在近侧腿上），远侧腿整条暗一档**，两腿重叠的地方远侧腿在后面被挡住；**两只靴子不能叠在一起**。
5. **落地的脚靴底描边在红线那一行**，抬起的脚离地 2-3 行；步子轻快，不要大劈叉。
6. 像素风规则：1 像素 = 1 格，1 像素黑色描边（#0A0411），不要抗锯齿、不要半透明、不要新颜色。

## 交付

- `run_1x.png`：384x160（4 列 x 2 行，每格 96x80），8 帧完整画面（你的腿 + 原样的上半身），透明背景；
- 再给一张放大 8 倍的预览图。

## Prompt (English)

Redraw ONLY the legs of this pixel-art girl (Zeri, side view facing right, rifle held level), 1 px = 1 game pixel, the
26 colours of palette.png only, 1-px outline #0A0411, no anti-aliasing. Every cell of body_run_1x.png already holds the
finished upper body (the coat's two hanging panels and the hanging hand included): keep every one of those pixels and
draw the legs under the belt, coming out from under the coat. The legs must be the DESIGN's legs (design_legs.png,
idle_1x.png): dark wine-red leggings in their two shades and the design's thickness (never thin lines or rubber bends),
the tan patch on the near knee, the design's whole brown boots with their orange-yellow buckle and sole. The run must
CHANGE LEGS: frames 1-4 the near leg leads (1 contact: near foot forward on the ground, far leg pushing off behind;
2 down: near foot planted under her, far foot lifting behind; 3 passing: near leg straight under her, far leg swinging
forward under the body with the knee bent, foot off the ground; 4 up: near leg pushing off behind, far knee raised
reaching forward), frames 5-8 the same with the far leg leading - follow guide_run.png (orange = near leg, blue = far
leg, red = the ground row). The far leg one shade darker and behind the near one where they overlap; the two boots never
stack on each other. Planted soles on the red row, lifted feet 2-3 rows up, light quick steps. Deliver run_1x.png
(384x160, 4x2 cells of 96x80), transparent, plus an 8x preview.
