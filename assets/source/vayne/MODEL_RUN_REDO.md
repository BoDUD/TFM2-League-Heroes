# 薇恩：重画跑步的腿（给 Codex 的提示词）

> 上次交回的 9 张动作条已经导入游戏，**只有跑步要重画**：8 帧的腿一模一样——前面那条腿（近腿）踩地、后面那条腿（远腿）往后踢——两条腿从来没有交换，也没有从身体下面交叉经过，看起来像一直单脚往前蹦（用户：「走路没有交叉步」）。英雄联盟的跑步每 4 帧换一次腿，第 2–3 帧和第 6–7 帧两条腿在身体下面交叉。
> - **腿以上都不用改**：头、头发、马尾、脸和墨镜、披风、身体、两把弩、大小（站着 48 格）、每帧在格子里的位置、头每帧在同一处（上下最多 1 格）、8 帧 × 125 毫秒、排版（4 列 × 2 行，3072×1536），全部照 `vayne_run_current.png`（你上次交回的跑步）。**从胯往下的两条腿按下面的表和 `guide/lol_run_legs.png` 重画**；手臂可以跟着腿反向小幅摆动（最多 2 格），披风照常往后飘。
> - **这次不要清头、不要贴头**：上次的导出先把原稿里画的头发、脸连同下巴下面的脖子和立领一起清掉，再贴造型图的整颗头，结果头像贴纸一样和身体分开了（用户：「头和身体有点分离」）。这次整个人一起画、一起导出，头和脖子、立领连在一起；造型图的脸由 Claude 导入时贴（它会在你画的脸上找位置）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/vayne_design.png` | 定稿造型，放大 8 倍 | 第一张附图：腿的材质（深色紧身衣、银色护膝、黑色高跟靴、银色靴尖）和像素风格 |
| `vayne_run_current.png` | 你上次交回的跑步（8 帧，放大 8 倍） | 第二张附图：**胯以上照它**，只换腿 |
| `guide/lol_run_legs.png` | 英雄联盟的跑步，同样的 8 帧、同样的格子：**近腿橙色**（画在前面），**远腿蓝色**（在后面），其余灰色 | 第三张附图：**每帧两条腿的位置照它** |
| `guide/lol_run_legs_game.png` | 同一张按游戏尺寸取的方块（一格就是游戏里一个像素） | 看腿在游戏尺寸下有多粗、多长 |
| `guide/run_legs_now_vs_lol.png` | 逐帧对比：上排你上次的腿（错），下排英雄联盟的腿（对） | 看错在哪 |
| `pose/lol_pose_run.png` | 同一帧的高清渲染（上次也给过） | 身体动作 |
| `now/vayne_now_run.png` | 英雄联盟原版按游戏尺寸取色（上次也给过） | 帧数、时机、站位 |
| `guide/vayne_guide_run.png` | 格子、站位点（蓝十字）、脚底线（红线）和禁区 | 对位用，不要画进图里 |
| `vayne_cells.json` | 每帧站位点和时长 | 对位 |

## 每帧的腿（最重要）

近腿 = 参考图里的橙色腿，画在前面（护膝朝着看的人、颜色亮一点）；远腿 = 蓝色腿，在后面（暗一点，被近腿和披风挡住一部分）。**每帧都有一只脚踩在脚底线上。**

| 帧 | 近腿（橙） | 远腿（蓝） |
|---|---|---|
| 1 | 踩地：直的，在身体下面，鞋底在脚底线上 | 往后踢：大腿朝后，膝盖弯成直角，脚跟抬起朝向披风 |
| 2 | 还踩着地，稍微移到身体后面 | 往前摆：从身体下面经过，膝盖弯着——**两个膝盖在这里交叉** |
| 3 | 往后伸直蹬地，脚尖在脚底线上 | 在前面：膝盖抬到身前，小腿往下 |
| 4 | 离地往后收，膝盖开始弯 | 落地：在前面伸直，鞋底踩到脚底线 |
| 5 | 往后踢：膝盖弯成直角，脚跟抬起（第 1 帧换了一条腿） | 踩地：直的，在身体下面 |
| 6 | 往前摆：从身体下面经过，**画在远腿前面**——两个膝盖交叉 | 还踩着地，稍微移到身体后面 |
| 7 | 在前面：膝盖抬到身前，小腿往下 | 往后伸直蹬地，脚尖在脚底线上 |
| 8 | 落地：在前面伸直，鞋底踩到脚底线 | 离地往后收，膝盖开始弯；接回第 1 帧 |

所以：第 8、1、2 帧近腿踩地，第 4、5、6 帧远腿踩地，第 3、7 帧两条腿前后交叉换位。

## 提示词（附三张图：`design/vayne_design.png`、`vayne_run_current.png`、`guide/lol_run_legs.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - her colors, materials and pixel style. SECOND: her current 8-frame run at 8x in a 4x2 grid of 96x96-square cells - keep EVERYTHING above the hips exactly as drawn there (head, hair, ponytail, face, glasses, collar, cape, torso, arms, both crossbows, size and place in each cell). THIRD: the same 8 frames of the original run in the same cells, her legs painted apart: the NEAR leg ORANGE (in front, toward the viewer), the FAR leg BLUE (behind), the rest grey - copy the position of both legs in every frame from it.
The problem to fix: in the SECOND image all 8 frames have the same legs (the near leg planted, the far leg kicked up behind), so she never changes step. A run swaps the legs: frames 8, 1, 2 the near leg is planted; frames 4, 5, 6 the far leg is planted; in frames 2-3 and 6-7 the legs cross under her body.
Frame by frame: 1 near leg planted straight under her, far leg kicked up behind with the knee bent 90 degrees; 2 near leg still planted, a little behind her, far leg swinging forward under her body, knees passing each other; 3 far leg in front with the knee lifted, near leg stretched back pushing off with its toe on the ground; 4 far leg landing straight in front, near leg lifting behind; 5 far leg planted straight under her, near leg kicked up behind with the knee bent 90 degrees (frame 1 with the other leg); 6 far leg still planted, near leg swinging forward under her body in front of the far leg, knees passing each other; 7 near leg in front with the knee lifted, far leg stretched back pushing off; 8 near leg landing straight in front, far leg lifting behind - it flows into frame 1.
Draw her legs in the FIRST image's materials: the black-navy bodysuit, silver knee guards, black heeled boots with silver toes; the near leg in front of the far one, lighter; the far leg darker, partly behind the near leg and the cape. One foot touches the feet line in every frame; the arms may swing a little against the legs (at most 2 squares); the cape keeps streaming behind her.
Pixel rules: exactly the FIRST image's pixel size (48 squares tall standing), every pixel one crisp 8x8 square on one 8-px grid, no anti-aliasing, no blur, no semi-transparency, ONLY the FIRST image's 26 colors, a 1-square near-black outline round the silhouette and each material's own dark shade inside it, big flat areas, no dithering or noise. Draw the whole character in one piece: the head stays joined to the neck and the collar (do not cut it out or paste another head on).
Feet line: the lowest row of her feet is square row 81 of each cell; nothing from row 82 down. Layout: exactly like the SECOND image - 4 columns x 2 rows of 96x96-square cells, 3072x1536 pixels, frame N in the same cell; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.
```

## 导出（和上次一样，只改贴头那步）

1. 对齐网格、换成造型图色板、按站位点放回格子、脚底线以下清空、放大 8 倍输出 `vayne_run.png`——和上次一样。
2. **不要做上次的第 4 步**（清掉头周围的头发、脸、紧身衣颜色再贴整颗头）：原稿里画的头和脖子、立领原样保留。
3. 墨镜颜色：色板里去掉 `#F8303C`、`#B0102A` 这一步照旧（原稿的镜片会变成别的红，没关系，Claude 会贴回造型图的脸）。

## 交回（`vayne_run_redo.zip`）

- `raw/run.png`：生图模型的原始输出（和上次 `strips_raw/run.png` 同样的格式：品红底，4 列 × 2 行）；
- `strip_eyes_run.json`：8 帧里墨镜中心在 `raw/run.png` 上的坐标，`[[x, y], ...]`（和上次 `strip_eyes.json` 的跑步那一行一样）；
- `vayne_run.png`：你导出的跑步（放大 8 倍，3072×1536，不清头、不贴头）；
- `HANDOFF.md`：用了哪条提示词、哪里没做到。

## 交回前自查

- [ ] 第 8、1、2 帧近腿（前面那条）踩地，第 4、5、6 帧远腿踩地，第 3、7 帧两条腿交叉换位——和 `guide/lol_run_legs.png` 逐帧对过；
- [ ] 每帧都有一只脚在脚底线上，脚底线以下没有任何像素；
- [ ] 胯以上和 `vayne_run_current.png` 一样（头、披风、弩、位置），头每帧在同一处（上下最多 1 格），首尾接得上；
- [ ] 头和脖子、立领连在一起，没有被切开、没有贴另一颗头；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，只用造型图的颜色。
