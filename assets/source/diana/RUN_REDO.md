# 戴安娜：重画跑步的腿（给 Codex 的提示词）

> 上次交回的 9 张动作条里，**只有跑步要重画**（其他 8 张 Claude 已经在导入）。跑步 8 帧的腿一模一样：前面那条腿（近腿，金色护膝朝着看的人）一直踩地，后面那条腿（远腿）一直往后踢，两条腿从来没有交换，也没有从身体下面交叉经过，看起来像一直单脚往前蹦。你没采用的那版修正也一样。英雄联盟的跑步第 1–4 帧近腿踩地，第 5 帧换脚，第 6–8 帧远腿踩地，两条腿在身体下面交叉。
> - **腿以上都不用改**：头、头发、马尾、脸、盔甲、披风、弯刀、大小、8 帧 × 125 毫秒、排版（4 列 × 2 行，3072×1536），全部照 `diana_run_current.png`（你上次交回的跑步）。**从胯往下的两条腿按下面的表和 `guide/lol_run_legs.png` 重画**；手臂可以跟着腿反向小幅摆动（最多 2 格），马尾和披风照常往后飘。
> - **注意颜色和上次的腿图相反**：这次 **橙色 = 近腿**（画在前面、亮一点、金色护膝朝着看的人），**蓝色 = 远腿**（在后面、暗一点，一部分被近腿和垂甲挡住）。
> - **每帧都有一只脚踩在脚底线上**：上次整条跑步比脚底线高了 2–4 格（浮在空中），这次鞋底要踩到红线上方那一行。
> - 这次也**不要贴头、不要擦头周围的像素**，整个人一起画；造型图的脸由 Claude 导入时贴。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/diana_design.png` | 定稿造型，放大 8 倍 | 第一张附图：腿的材质（深蓝紧身裤、金色护膝、银色护胫、深蓝高跟靴）和像素风格 |
| `diana_run_current.png` | 你上次交回的跑步（8 帧，放大 8 倍） | 第二张附图：**胯以上照它**，只换腿 |
| `guide/lol_run_legs.png` | 英雄联盟的跑步，同样的 8 帧、同样的格子：**近腿橙色**（前面），**远腿蓝色**（后面），其余灰色，红线是脚底线 | 第三张附图：**每帧两条腿的位置照它** |
| `guide/lol_run_legs_game.png` | 同一张按游戏尺寸取的方块（一格就是游戏里一个像素） | 看腿在游戏尺寸下有多粗、多长 |
| `guide/run_legs_now_vs_lol.png` | 逐帧对比：上排你上次的腿（错），下排英雄联盟的腿（对） | 看错在哪 |
| `pose/lol_pose_run.png`、`now/diana_now_run.png`、`guide/diana_guide_run.png`、`diana_cells.json` | 和上次一样的参考、参考线和站位点 | 身体动作、时机、对位 |

## 每帧的腿（最重要）

近腿 = 橙色，画在前面（金色护膝朝着看的人、颜色亮）；远腿 = 蓝色，在后面（暗一点）。

| 帧 | 近腿（橙） | 远腿（蓝） |
|---|---|---|
| 1 | 踩地：直的，在身体下面，鞋底在脚底线上 | 在后面：膝盖弯着，脚稍微离地 |
| 2 | 还踩着地 | 往后踢：膝盖弯成直角，脚跟抬起 |
| 3 | 还踩着地，稍微移到身体后面 | 往前摆：从身体下面经过——**两个膝盖在这里交叉** |
| 4 | 往后伸直蹬地，脚尖在脚底线上 | 在前面伸出去，准备落地 |
| 5 | 离地往后收 | 落地：鞋底踩到脚底线（换脚） |
| 6 | 往后踢：膝盖弯成直角，脚跟抬起（第 2 帧换了一条腿） | 踩地：直的，在身体下面 |
| 7 | 往前摆：从身体下面经过，**画在远腿前面**——两个膝盖交叉 | 还踩着地，稍微移到身体后面 |
| 8 | 在前面伸出去，准备落地；接回第 1 帧落地 | 往后伸直蹬地，脚尖在脚底线上 |

所以：第 1–4 帧近腿（橙）踩地，第 5 帧换脚，第 6–8 帧远腿（蓝）踩地；第 3 帧和第 7 帧两条腿在身体下面交叉。

## 提示词（附三张图：`design/diana_design.png`、`diana_run_current.png`、`guide/lol_run_legs.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - her colors, materials and pixel style. SECOND: her current 8-frame run at 8x in a 4x2 grid of 96x96-square cells - keep EVERYTHING above the hips exactly as drawn there (head, hair, ponytail, face, armour, mantle, arms, the crescent blade, size and place in each cell). THIRD: the same 8 frames of the original run in the same cells, her legs painted apart: the NEAR leg ORANGE (in front, toward the viewer), the FAR leg BLUE (behind), the rest grey, the red line under the feet - copy the position of both legs in every frame from it.
The problem to fix: in the SECOND image all 8 frames have the same legs (the near leg planted, the far leg kicked up behind), so she never changes step, and the feet float 2-4 squares above the ground. A run swaps the legs: frames 1-4 the near leg is planted, frame 5 changes feet, frames 6-8 the far leg is planted; in frames 3 and 7 the knees pass each other under her body.
Frame by frame: 1 near leg planted straight under her, far leg behind with the knee bent, its foot just off the ground; 2 near leg planted, far leg kicked up behind with the knee bent 90 degrees; 3 near leg still planted a little behind her, far leg swinging forward under her body, knees passing each other; 4 near leg stretched back pushing off with its toe on the ground, far leg reaching forward; 5 far leg landing on the ground, near leg lifting behind; 6 far leg planted straight under her, near leg kicked up behind with the knee bent 90 degrees; 7 far leg still planted a little behind, near leg swinging forward under her body IN FRONT of the far leg, knees passing each other; 8 far leg stretched back pushing off, near leg reaching forward - it lands in frame 1.
Draw her legs in the FIRST image's materials: dark navy leggings, gold knee guards, silver greaves, dark navy heeled boots; the near leg in front of the far one, lighter, its gold knee guard toward the viewer; the far leg darker and partly behind the near leg and the hip tassets. One foot's sole touches the feet line in every frame (the row just above the red line): no floating. The arms may swing a little against the legs (at most 2 squares); the ponytail and the mantle keep streaming behind her; the blade stays in her right hand, its tip above the feet line.
Pixel rules: exactly the FIRST image's pixel size (40 squares from the top of the hair to the soles), every pixel one crisp 8x8 square on one 8-px grid, no anti-aliasing, no blur, no semi-transparency, ONLY the FIRST image's 26 colors, a 1-square near-black outline round the silhouette and each material's own dark shade inside it, big flat areas, no dithering or noise. Draw the whole character in one piece; do not cut out or paste a head.
Feet line: the lowest row of her feet is square row 79 of each cell; nothing from row 80 down. Layout: exactly like the SECOND image - 4 columns x 2 rows of 96x96-square cells, 3072x1536 pixels, frame N in the same cell; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.
```

## 交回（`diana_run_redo.zip`）

- `raw/run.png`：生图模型的原始输出；
- `diana_run.png`：整理后的跑步（放大 8 倍，3072×1536，不清头、不贴头）和 `native/diana_run_1x.png`；
- `manifest.json`：每帧格子矩形、站位点、bbox、eye_mark（和上次一样的写法）；
- `HANDOFF.md`：用了哪条提示词、哪里没做到。

## 交回前自查

- [ ] 第 1–4 帧近腿（橙，前面、金色护膝）踩地，第 5 帧换脚，第 6–8 帧远腿（蓝）踩地，第 3、7 帧两条腿交叉换位——和 `guide/lol_run_legs.png` 逐帧对过；
- [ ] 每帧都有一只鞋底踩在脚底线上（红线上面那一行），脚底线以下没有任何像素，不浮空；
- [ ] 胯以上和 `diana_run_current.png` 一样（头、马尾、披风、弯刀、位置），头每帧在同一处（上下最多 1 格），首尾接得上；
- [ ] 整个人连在一起，没有切头、没有贴头；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，只用造型图的 26 色。
