# 剑姬：重画走路的腿（给 Codex 的提示词）

> 上次交回的 9 张动作条里，**只有走路要重画**：8 帧的腿一直是同一条带金边的腿（近腿）在前面、另一条（远腿）在后面，两条腿从来没有交换，也没有从身体下面交叉经过（用户看了对照图，选了"给 Codex 返修走路"）。英雄联盟的走路每 4 帧换一次腿，第 3–4 帧和第 7–8 帧两条腿在身体下面交叉。
> - **腿以上都不用改**：头、脸、头发、披风、身体、平举的细剑和手臂、大小（站着 40 格）、每帧在格子里的位置、头每帧在同一处（上下最多 1 格）、8 帧 × 114 毫秒、排版（4 列 × 2 行，3840×1792），全部照 `fiora_run_current.png`（你上次交回的走路）。**从胯往下的两条腿按下面的表和 `guide/lol_run_legs.png` 重画**；披风照常往后飘。
> - 贴头和上次一样（定稿的头逐格贴回，上次做得很好），细剑照旧是 1 格、不描边的直线。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/fiora_design.png` | 定稿造型，放大 8 倍 | 第一张附图：腿的材质（青绿紧身裤和金色竖条、青绿高跟靴、金色靴尖和靴口）和像素风格 |
| `fiora_run_current.png` | 你上次交回的走路（8 帧，放大 8 倍） | 第二张附图：**胯以上照它**，只换腿 |
| `guide/lol_run_legs.png` | 英雄联盟的走路，同样的 8 帧、同样的格子：**近腿橙色**（画在前面），**远腿蓝色**（在后面），其余灰色 | 第三张附图：**每帧两条腿的位置照它** |
| `guide/lol_run_legs_game.png` | 同一张按游戏尺寸取的方块（一格就是游戏里一个像素） | 看腿在游戏尺寸下有多粗、多长 |
| `guide/run_legs_now_vs_lol.png` | 逐帧对比：左边你上次的腿（错），右边英雄联盟的腿（对，青=近腿，品红=远腿） | 看错在哪 |
| `pose/lol_pose_run.png`、`now/fiora_now_run.png`、`guide/fiora_guide_run.png`、`fiora_cells.json` | 上次也给过的参考、站位和格子 | 身体动作、对位 |

## 每帧的腿（最重要）

近腿 = 参考图里的橙色腿，画在前面（金色竖条朝着看的人、颜色亮一点）；远腿 = 蓝色腿，在后面（暗一点，被近腿和披风挡住一部分）。**每帧都有一只脚踩在脚底线上。**

| 帧 | 近腿（橙） | 远腿（蓝） |
|---|---|---|
| 1 | 踩地：在前面伸直，鞋底在脚底线上 | 在后面：往后伸，脚跟抬起 |
| 2 | 还踩着地，移到身体下面 | 往前收：膝盖弯着，脚离地 |
| 3 | 踩地：直的，在身体下面 | 往前摆：从身体下面经过——**两个膝盖在这里交叉** |
| 4 | 往后蹬：脚跟抬起 | 在前面落地，伸直 |
| 5 | 在后面：往后伸，脚跟抬起（第 1 帧换了一条腿） | 踩地：在前面伸直，鞋底在脚底线上 |
| 6 | 往前收：膝盖弯着，脚离地 | 还踩着地，移到身体下面 |
| 7 | 往前摆：从身体下面经过，**画在远腿前面**——两个膝盖交叉 | 踩地：直的，在身体下面 |
| 8 | 在前面落地，伸直 | 往后蹬：脚跟抬起；接回第 1 帧 |

所以：第 1–3 帧近腿踩地，第 5–7 帧远腿踩地，第 3–4 帧和第 7–8 帧两条腿前后交叉换位。和 `guide/lol_run_legs.png` 逐帧对照，以指引图为准。

## 提示词（附三张图：`design/fiora_design.png`、`fiora_run_current.png`、`guide/lol_run_legs.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - her colors, materials and pixel style. SECOND: her current 8-frame walk at 8x in a 4x2 grid of 120x112-square cells - keep EVERYTHING above the hips exactly as drawn there (head, face, hair, collar, cape, torso, both arms, the level rapier, size and place in each cell). THIRD: the same 8 frames of the original walk in the same cells, her legs painted apart: the NEAR leg ORANGE (in front, toward the viewer), the FAR leg BLUE (behind), the rest grey - copy the position of both legs in every frame from it.
The problem to fix: in the SECOND image all 8 frames have the same legs (the near leg always in front, the far leg always behind), so she never changes step. A walk swaps the legs: frames 1-3 the near leg is planted; frames 5-7 the far leg is planted; in frames 3-4 and 7-8 the legs cross under her body.
Frame by frame: 1 near leg planted straight in front, far leg stretched behind with the heel up; 2 near leg still planted, moving under her, far leg drawn forward with the knee bent, foot off the ground; 3 near leg planted straight under her, far leg swinging forward under her body, knees passing each other; 4 far leg landing straight in front, near leg pushing off behind, heel up; 5 far leg planted straight in front, near leg stretched behind with the heel up (frame 1 with the other leg); 6 far leg still planted, moving under her, near leg drawn forward with the knee bent; 7 far leg planted under her, near leg swinging forward under her body IN FRONT of the far leg, knees passing each other; 8 near leg landing straight in front, far leg pushing off behind - it flows into frame 1.
Draw her legs in the FIRST image's materials: dark teal fitted leggings with gold stripes, teal heeled boots with gold toe caps and trims; the near leg in front of the far one, lighter; the far leg darker, partly behind the near leg and the cape. One foot touches the feet line in every frame; the cape keeps streaming behind her.
Pixel rules: exactly the FIRST image's pixel size (40 squares tall standing), every pixel one crisp 8x8 square on one 8-px grid, no anti-aliasing, no blur, no semi-transparency, ONLY the FIRST image's 25 colors, a 1-square near-black outline round the silhouette and each material's own dark shade inside it, big flat areas, no dithering or noise. The head is the FIRST image's head pasted square for square as last time; the rapier stays a straight bare 1-square line.
Feet line: the lowest row of her feet is square row 97 of each cell; nothing from row 98 down. Layout: exactly like the SECOND image - 4 columns x 2 rows of 120x112-square cells, 3840x1792 pixels, frame N in the same cell; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.
```

## 交回（`fiora_run_redo.zip`）

- `fiora_run.png`：整理后的走路（放大 8 倍，3840×1792，定稿的头已贴回，细剑 1 格直线）；
- `logical/fiora_run_1x.png`：同一张 1 倍逻辑像素版；
- 生图原稿（`generated_sources/`）、`manifest.json`、`HANDOFF.md`：用了哪条提示词、哪里没做到。

## 交回前自查

- [ ] 第 1–3 帧近腿（前面那条、亮的）踩地，第 5–7 帧远腿踩地，第 3–4、7–8 帧两条腿交叉换位——和 `guide/lol_run_legs.png` 逐帧对过；
- [ ] 每帧都有一只脚在脚底线上，脚底线以下没有任何像素；
- [ ] 胯以上和 `fiora_run_current.png` 一样（头、披风、细剑、位置），头每帧在同一处（上下最多 1 格），首尾接得上；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，只用造型图的 25 色；每帧连成一块。
