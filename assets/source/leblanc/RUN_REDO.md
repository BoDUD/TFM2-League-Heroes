# 乐芙兰：重画移动（给 Codex 的提示词）

> **为什么重画**：上一轮交回的移动（`current/leblanc_run_current.png`）有三个问题，用户在动图里看出来了：
> 1. **没有交叉步，像平移**（「走路没有交叉步 平行走路？」）：8 帧里一直是左腿在后、右腿在前的同一个大跨步，两条腿从不交替、也从不经过对方，人像是滑着走。
> 2. **耳朵两边冒东西**（「走路的时候左右耳会冒出来什么东西？」）：贴头以后，生成图自己画的耳饰和头的描边还留在贴上去的头旁边（第 2、4–8 帧近耳旁的一小块金色和黑色），播放时一闪一闪。
> 3. **前 4 帧脚离地**：第 1–4 帧最低的脚在脚底线上面 1–3 格，人在飘。
> 看 `current/run_problems.png`（每帧标了离地格数）和 `current/run_current_vs_league.gif`（左边现在、右边英雄联盟原版：原版两条腿一前一后交替、膝盖交错）。
> **这一轮只重画移动 8 帧**，其他动作不动。造型就是定稿的 B 版 43 格（`design/leblanc_design.png`），**照它的大小和样子画，不要改造型**。
> 交回 `leblanc_run.png`（放大 8 倍，3072×1280）和原尺寸 `leblanc_run_1x.png`，附 `HANDOFF.md`（**最后写**）、`manifest.json`（每帧格子矩形、站位点、不透明范围、头贴在哪里）、`generation_prompts.json`，打成一个 zip（`leblanc_run_redo_done.zip`，放在 outputs 里）。

## 这一轮的关键要求

1. **交叉步**：前 4 帧一步、后 4 帧另一步。第 1 帧近侧腿在前、远侧腿在后（两脚着地）；第 2 帧后脚抬起；**第 3 帧两腿交叉经过**（近侧腿踩在身体正下方，远侧腿弯膝从它旁边往前带，两条腿重叠交错）；第 4 帧远侧腿向前摆；第 5–8 帧换过来（远侧腿在前……第 7 帧再交叉经过）。首尾无缝循环。
2. **步子窄**：两只鞋最远相距 **12 格以内**（现在是 18 格，太宽）；腿从长裙的开衩和下摆下面出来，大腿被裙子盖住，看得到的是小腿和高跟鞋。
3. **脚踩地**：每一帧至少有一只脚踩在脚底线上（第 67 行），不能整个人飘起来；身体随步子上下最多 1 格（着地帧低 1 格、经过帧高 1 格），头跟着身体一起动，不在身体上滑。
4. **两条腿一样的颜色**：都是造型图的腿（深色长袜和高跟鞋，同样的颜色），不要一条亮一条暗；近侧腿画在远侧腿前面（它的描边压住后面那条）。
5. **头的周围干净**：头照搬 `design/leblanc_head_1x.png`（逐格一样，只平移）。**先把自己画的头、耳饰、头发的描边全部擦掉**——头的范围和它外面 3 格以内、下巴以上的像素都清空——**再贴造型图的头**。贴完后头外面不能多出任何金色、黑色的碎块。
6. **法杖照原版跑步的拿法**：远侧手握着法杖向前、在腰的高度斜指前下方，杖头是造型图的**红水晶加两只深蓝蝙蝠翼**（不是一个红球），杖身是笔直的金线。
7. 长裙和身后的披风跟着步子向后飘、摆动。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/leblanc_design.png` | **定稿造型（43 格高）**，放大 8 倍 | 第一张附图 |
| `design/leblanc_design_1x.png`、`leblanc_head_1x.png`、`leblanc_palette.png` | 原尺寸造型、要贴的头、18 色色板 | 色板、贴头 |
| `leblanc_idle.png` | 已做好的待机条 | 看大小和站位 |
| `now/leblanc_now_run.png` | 英雄联盟原版跑步按游戏尺寸取色，放大 8 倍 | 第二张附图：帧数、站位 |
| `pose/lol_pose_run.png` | 同一帧的高清渲染 | 第三张附图：步伐（两腿交替、交叉）、法杖拿法 |
| `refs/caitlyn_run_example.png` | **用户认可的另一个英雄的跑步**（长裙下两腿交替、交叉，步子窄、脚踩地），放大 8 倍 | 第四张附图：**只学腿的动作**，长相照乐芙兰的造型图 |
| `current/leblanc_run_current.png`、`run_problems.png`、`run_current_vs_league.gif` | 现在的移动（错的）、问题标注、和原版并排的动图 | 看清楚要改什么 |
| `guide/leblanc_guide_run.png` | 格子、站位点（蓝十字）、脚底线（红线）和红线下的禁区 | 对位，不要画进图里 |
| `leblanc_cells.json` | 每帧的站位点和时长（跑步 8 × 142 毫秒） | 整理对位 |

## 规则

- 像素：每个像素一个 8×8 方块，对齐同一网格，没有抗锯齿、模糊、半透明；和造型图一样大（站着时头冠尖到脚底 43 格）。
- 只用造型图的 18 色：#060212 #2B010E #130F31 #390C20 #1C1948 #7A0012 #7F0015 #690B36 #AA011B #C90D33 #2C40A3 #B8662B #DE8D36 #F4AA45 #F9B954 #FCC967 #FDE59B #FEDECD；暗红 `#7A0012` 只用在近侧眼的瞳孔上。
- 1 格近黑外描边，**不要第二圈黑边、不要零散黑格**；明暗照定稿；没有碎点；手臂 2–3 格粗、连在身上；身体、手臂、法杖、披风连成一个整体。
- 脚底线以下什么都不能有：每格最低一行是第 67 行（像素 536–543），从像素 544 往下全空。
- 3/4 正面朝右，不画背影；只画角色，不画尘土、速度线、残影。
- 排版和 `now/leblanc_now_run.png` 完全一样：4 列 × 2 行，每格 96×80 方块（768×640 像素），图片 3072×1280，帧 N 在同一格；背景透明（做不到用纯品红 `#FF00FF`）；不要网格、边框、文字。

## 提示词（附四张图：`design/leblanc_design.png`、`now/leblanc_now_run.png`、`pose/lol_pose_run.png`、`refs/caitlyn_run_example.png`）

```text
Four attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block), 43 squares tall from the tip of the diadem to the soles - copy its colors, shapes, head, face, gown, cape, staff and pixel style exactly; do not redesign anything. SECOND: the original run sampled at game size at 8x, 8 frames in a 4x2 grid read left to right, top to bottom - copy the number of frames and where she stands in each cell, NOT its blurry look. THIRD: the original 3D run at the same frames - copy the stride: the legs ALTERNATE and CROSS, one leg ahead in frames 1-4 and the other in frames 5-8, and how the far hand carries the staff forward. FOURTH: another character's approved pixel-art run - learn ONLY its leg motion from it (narrow steps, the legs crossing under a skirt, a foot on the ground in every frame), never its look.
The character: LeBlanc (dark indigo-blue hair, a gold diadem with a tall spike, gold ear-cuffs, pale face, amber eyes, a gold collar, a long midnight-blue and crimson gown with a slit, a cape behind her, long plum-black gloves, a staff with a straight gold shaft, a red crystal on top and two navy bat wings).
Task: a MOVE loop, 8 frames, one seamless cycle of her run (8 x 142 ms), running to the right.
THE MOST IMPORTANT RULE - A CROSSING STRIDE: frame 1 the near leg forward and the far leg back, both feet on the ground; frame 2 the back foot lifting; frame 3 PASSING - the near leg straight under her body, the far leg bent at the knee swinging forward past it, the two legs overlapping and crossing; frame 4 the far leg reaching forward; frames 5-8 the same with the legs swapped (frame 7 passing again). The two shoes are never more than 12 squares apart. In EVERY frame at least one foot stands on the feet line - she never floats. Her legs show under the long gown's hem and through its slit (the thighs hidden by the gown, the lower legs and heeled shoes showing); BOTH legs in the same colors as the FIRST image's legs - never one light and one dark; the near leg is drawn over the far one. The body rises and drops at most 1 square with the steps (lower on frames 1 and 5, higher on 3 and 7) and the head moves with the body.
The head (the diadem with its spike, the hair, the face with both eyes, the two gold ear-cuffs, down to the chin's outline) is COPIED from the FIRST image in every frame, square for square, and only MOVED. Before pasting it, ERASE everything you drew yourself where the head goes and within 3 squares around it above the collar (your own hair, ear-cuffs, outline); after pasting, nothing of yours may be left beside the head - no gold or black bits by the ears. The dark red #7A0012 appears ONLY in the near eye's pupil.
The staff is in her far hand as in the THIRD image - held forward at waist height, pointing ahead and a little down - its shaft a STRAIGHT 1-square gold line, its head the FIRST image's red crystal with the two navy bat wings (never a round ball). The gown's hem and the cape stream back and sway with the steps.
Pixel rules: every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller, no anti-aliasing, no blur, no semi-transparency. ONLY the 18 colors of the FIRST image: #060212 #2B010E #130F31 #390C20 #1C1948 #7A0012 #7F0015 #690B36 #AA011B #C90D33 #2C40A3 #B8662B #DE8D36 #F4AA45 #F9B954 #FCC967 #FDE59B #FEDECD. ONE 1-square near-black outline around the silhouette and each material's own dark shade inside - never a second black ring, never stray black squares; copy the FIRST image's shading; no dithering, no noise. Arms 2-3 squares wide joined to the body; no loose pieces.
Feet line: in every cell her lowest square is on square row 67 from the top of the cell (pixels 536 to 543); NOTHING from pixel 544 down. Her place across each cell follows the SECOND image (the standing points are in leblanc_cells.json). 3/4 front view facing right, never her back. Only the character - no dust, no speed lines, no afterimages.
Layout: exactly like the SECOND image - 4 columns x 2 rows, each cell 96x80 squares (768x640 px), 3072x1280 pixels, frame N in the same cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, borders, labels or guide marks.
Before finishing, check: every square 8x8 on one grid; only the FIRST image's colors; the head identical to the FIRST image in every frame with NOTHING else within 3 squares of it above the collar; the legs alternating and crossing (frames 3 and 7 passing), the shoes at most 12 squares apart, a foot on the feet line in every frame; both legs the same colors; the staff straight with the crystal and bat wings; nothing below the feet line; frames in the same cells as the SECOND image.
```

## 交回前自查

- [ ] 图片 3072×1280，4×2 格，帧 N 和 now 条在同一格；严格 8×8 方块，透明度只有 0 和 255；只用造型图色板；
- [ ] **两条腿交替、第 3/7 帧交叉经过**，两只鞋相距不超过 12 格，**每帧至少一只脚踩在脚底线上**；两条腿颜色一样；
- [ ] 头是造型图的头逐格照搬，**头外 3 格以内（下巴以上）没有任何多余像素**；暗红只在近侧眼瞳孔；
- [ ] 法杖笔直，杖头是红水晶加两只蝙蝠翼；长裙、披风每帧都在；
- [ ] 脚底线以下没有像素；没有第二圈黑边、零散黑格、碎块；没有背影、特效、网格文字；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `leblanc_run.png` 存进 `assets/source/leblanc/codex_run_redo/`，`tools/art/fix_leblanc_strips.py` 的跑步改用它（去掉 `leblanc_run_legs.py` 的重画和 1–4 帧复用），照常清理碎块和多余黑边；检查两腿交替、鞋距、每帧踩地、头外 3 格干净。
- `import_native.py --hero leblanc` 后做「我们 vs 英雄联盟」的移动对比 GIF 给用户看。
