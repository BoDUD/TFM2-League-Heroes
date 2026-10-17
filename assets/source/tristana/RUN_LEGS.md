# 崔丝塔娜：重画跑步的腿（交叉步，给 Codex 的提示词）

> 上次交回的跑步（`tristana_run_current.png`）已经导入游戏：头和身体一起前倾、起落，用户认可这部分；但用户说「走路有点怪 没明显的交叉步 再调一下」。原因：第 1 帧和第 5 帧的腿几乎一样（两次着地都是同一条腿在前），第 4、8 帧也一样，看起来像一直用同一条腿往前蹦。英雄联盟的跑步每半圈换一次腿：第 8 帧近腿在前落地、第 1 帧近腿着地、第 2–3 帧近腿往后蹬；第 4 帧远腿在前落地、第 5 帧远腿着地、第 6–7 帧远腿往后蹬；第 2–3、6–7 帧两个膝盖在身体下面交叉经过。
> - **胯以上一点都不要改**：头、护目镜、耳朵、脸、躯干、手臂、大炮、每帧在格子里的位置和高低（4 格起伏）、8 帧时长、排版（4 列 × 2 行，3072×1536），全部照 `tristana_run_current.png`（你上次交回的跑步）——这个上半身是一整块，只是每帧平移，继续保持。**只重画从胯（短裤下沿）往下的两条腿**。
> - 两条腿的位置每帧照 `guide/lol_run_legs.png`（英雄联盟的跑步，同样的 8 帧、同样的格子：**近腿橙色**，**远腿蓝色**，其余灰色）。英雄联盟里她的炮端得很低，挡住了大半条腿；被炮挡住的部分，按下表补全一条完整的腿，画在炮的后面（炮在最前面）。
> - 交回 `tristana_run_legs.zip`：`tristana_run.png`（放大 8 倍，3072×1536）、`native/tristana_run_1x.png`、`manifest.json`（每帧的格子矩形、站位点、bbox、近腿和远腿的脚的位置）、`HANDOFF.md`、`generation_prompts.json`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/tristana_design.png` | 定稿造型（34 行），放大 8 倍 | 第一张附图：腿的材质（橄榄绿短裤下沿、棕色皮革绑腿、淡紫色赤脚）和像素风格 |
| `tristana_run_current.png` | 你上次交回的跑步（8 帧，放大 8 倍） | 第二张附图：**胯以上照它**，只换腿 |
| `guide/lol_run_legs.png` | 英雄联盟的跑步，近腿橙、远腿蓝，其余灰 | 第三张附图：**每帧两条腿的位置照它** |
| `guide/lol_run_legs_game.png` | 同一张按游戏尺寸取的方块（一格就是游戏里一个像素） | 看腿在游戏尺寸下的长短粗细 |
| `guide/run_legs_now_vs_lol.png` | 逐帧对比：上排你上次的腿（错），下排英雄联盟的腿（对） | 看错在哪 |
| `now/tristana_now_run.png`、`pose/lol_pose_run.png` | 英雄联盟原版（34 行取色、高清渲染） | 身体动作、站位 |
| `guide/tristana_guide_run.png` | 格子、站位点（蓝十字）、脚底线（红线）和禁区 | 对位用，不要画进图里 |
| `design/tristana_palette.png` | 造型图的 26 色 | 色板 |
| `tristana_cells.json` | 每帧站位点和时长 | 对位 |

## 每帧的腿（最重要）

近腿 = 参考图里的橙色腿：画在前面（离看的人近，颜色亮一点）；远腿 = 蓝色腿：在后面（暗一档，被近腿挡住一部分）。大炮永远在两条腿前面。第 2、3、6、7 帧是腾空帧（上半身最高的几帧），两只脚都离地；第 1、4、5、8 帧有脚踩在脚底线上。

| 帧 | 近腿（橙） | 远腿（蓝） |
|---|---|---|
| 1 | 着地：在身体下面，直的，脚掌踩在脚底线上 | 在后面抬起：膝盖弯，脚在身后、离地 |
| 2 | 往后蹬：在身后伸直，脚尖刚离地 | 往前摆：从身体下面经过，膝盖抬起——**两个膝盖在这里交叉** |
| 3 | 收在后面，膝盖弯，离地 | 在前面：膝盖抬到身前，小腿往下 |
| 4 | 在后面抬着 | 落地：在前面伸直，脚掌踩到脚底线 |
| 5 | 在后面抬起：膝盖弯，脚在身后、离地（第 1 帧换了一条腿） | 着地：在身体下面，直的 |
| 6 | 往前摆：从身体下面经过，**画在远腿前面**——两个膝盖交叉 | 往后蹬：在身后伸直，脚尖刚离地 |
| 7 | 在前面：膝盖抬到身前，小腿往下 | 收在后面，膝盖弯，离地 |
| 8 | 落地：在前面伸直，脚掌踩到脚底线 | 在后面抬着；接回第 1 帧 |

所以：第 8、1 帧近腿着地，第 4、5 帧远腿着地；第 1 帧和第 5 帧是同一个姿势、换了一条腿；第 2–3、6–7 帧两条腿前后交叉换位。**第 1 帧和第 5 帧的腿不能一样，第 4 帧和第 8 帧也不能一样。**

## 提示词（附三张图：`design/tristana_design.png`、`tristana_run_current.png`、`guide/lol_run_legs.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - her colors, materials and pixel style, 34 squares tall standing. SECOND: her current 8-frame run at 8x in a 4x2 grid of 96x96-square cells - keep EVERYTHING above the hips exactly as drawn there, square for square (the head with the goggles and ears, the torso, both arms, the short thick cannon, the size, the place and the height of the body in each cell). THIRD: the same 8 frames of the original run in the same cells, her legs painted apart: the NEAR leg ORANGE (in front, toward the viewer), the FAR leg BLUE (behind), the rest grey - copy the position of both legs in every frame from it; where the grey cannon covers a leg there, complete the leg behind the cannon.
The problem to fix: in the SECOND image frames 1 and 5 have the same legs, and so do frames 4 and 8: she always lands on the same leg, so she never changes step. A run swaps the legs every half cycle: the near leg lands in front in frame 8, is planted in frame 1 and pushes off behind in frames 2-3; the far leg lands in front in frame 4, is planted in frame 5 and pushes off behind in frames 6-7; the knees pass each other under her body in frames 2-3 and 6-7.
Frame by frame: 1 near leg planted straight under her, its sole on the feet line, far leg lifted behind with the knee bent; 2 (in the air) near leg stretched behind, toe just off the ground, far leg swinging forward under her body, the knees passing each other; 3 (in the air) far leg in front with the knee lifted, near leg tucked behind with the knee bent; 4 far leg landing straight in front, its sole on the feet line, near leg lifted behind; 5 far leg planted straight under her, near leg lifted behind with the knee bent (frame 1 with the other leg); 6 (in the air) far leg stretched behind, near leg swinging forward under her body in front of the far leg, the knees passing each other; 7 (in the air) near leg in front with the knee lifted, far leg tucked behind; 8 near leg landing straight in front, far leg lifted behind - it flows into frame 1. Frames 1 and 5 must NOT have the same legs; frames 4 and 8 must NOT have the same legs.
Draw her legs in the FIRST image's materials: the olive shorts' hem at the hips, the quilted brown leather leg wraps, bare lavender feet; short, sturdy yordle legs; the near leg in front of the far one and one shade lighter, the far leg a shade darker and partly behind the near leg; the cannon always in front of both legs. In frames 1, 4, 5 and 8 one foot touches the feet line; in frames 2, 3, 6 and 7 both feet are off the ground.
Pixel rules: exactly the FIRST image's pixel size, every pixel one crisp 8x8 square on one 8-px grid, no anti-aliasing, no blur, no semi-transparency, ONLY the FIRST image's 26 colors: #191421 #442A23 #283447 #41492D #821D3F #734832 #87602E #445E80 #727745 #D13845 #A36A43 #835B9E #C35C80 #7E879E #C8994E #A3A26B #CE9560 #7397C3 #F6BA30 #B889D1 #E6BF86 #F699B4 #BFCCD8 #DFB4EB #B9DDED #FFF4E4. A 1-square near-black outline round the silhouette and each material's own dark shade inside it; no dithering, no noise, no specks; the legs joined to the hips, no loose pieces.
Feet line: the lowest row of her feet is square row 81 of each cell; nothing from row 82 down. Layout: exactly like the SECOND image - 4 columns x 2 rows of 96x96-square cells, 3072x1536 pixels, frame N in the same cell, the body in the same place and at the same height as in the SECOND image; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.
Before finishing, check: everything above the hips identical to the SECOND image in every frame; frames 1 and 5 with different legs (the other leg planted), frames 4 and 8 with different legs; the knees crossing in frames 2-3 and 6-7; one foot on the feet line in frames 1, 4, 5, 8; only the FIRST image's colors; nothing below the feet line.
```

## 交回前自查

- [ ] 胯以上和 `tristana_run_current.png` 逐格一样（头、身体、炮、每帧位置和高低）；
- [ ] 第 1 帧近腿着地、第 5 帧远腿着地，两帧的腿不一样；第 4、8 帧也不一样；第 2–3、6–7 帧两个膝盖交叉；
- [ ] 第 1、4、5、8 帧有一只脚踩在第 81 行，第 2、3、6、7 帧两脚离地；脚底线以下没有像素；
- [ ] 近腿在前、亮一档，远腿在后、暗一档，大炮在两条腿前面；腿连在胯上，没有碎块；
- [ ] 只用造型图色板，严格 8×8 方块，透明度只有 0 和 255；排版 3072×1536、帧 N 在同一格。

## Claude 导入时

- 检查胯以上是否和上次逐格一样、第 1/5 帧和第 4/8 帧的腿是否不同、脚底线、色板、连通块；放进 `assets/source/native/tristana_run.png`，`import_native.py --hero tristana`，做「我们 vs 英雄联盟」的对比 GIF 给用户看，重做演示 GIF 并重新固定 PR 链接。
