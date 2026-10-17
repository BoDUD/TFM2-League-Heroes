# 米利欧（明烛）：在格子上画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画 B（男孩 + 他肩后圆滚滚的小火精灵），游戏里的大小定为**发顶到鞋底 70 格**。游戏里是高清 PPU：**你画的每一格就是一个高清像素**，交回后我 1:1 读回，不缩放。
> - `1_front_grid.png` 是我把原画 B 缩到 70 格放在格子上的样子——**大小、位置、颜色对，但脸和细节糊了**（眼睛、嘴、肩垫都看不清）。所以**第一件事：在同样的格子上把正面重新画干净**（样子照 `2_picture_B.png`，就是你上一轮画的 B）。
> - **第二件事：侧身版（最重要，所有动作都从它来）**：本包所有英雄除了待机，每个动作都是**侧身朝右**。之前一个英雄的造型只画了正面，动作帧全成了正面站着，被用户全部退回。所以同一个男孩再画**身体转向画面右边**的版本，两稿（A 完全侧面、B 稍带 3/4）。侧身版**只画男孩，不画火精灵**。
>
> **侧身版和正面版必须是同一个角色**：同样的格子、同样的高度和头身比、同样的颜色和细节，只是身体转了个角度。

## 大小和位置

- 画布 **1024 × 1536 竖版，固定 12 × 12 px 的格子**（85 列 × 128 行，最右边 4 px 留透明），**每个格子一个颜色，格子对齐画布左上角**。直接在格子上画，**不要先画大图再缩小**（会糊）。
- **男孩**：**发顶在第 30 行**（绿线），**鞋底最低的一行是第 99 行**（红线上面那一行，红线以下什么都不能有：游戏在脚下画血条）——发顶到鞋底 70 行；**站立点（两只凉鞋中间）在第 48 列**（蓝线）。正面宽度约 36 格（肩垫流苏都算），和 `1_front_grid.png` 一样。
- **火精灵（只在正面版）**：和 `1_front_grid.png` 里一样大、一样的位置（约 14 × 18 格（算上顶上的火苗），在男孩背后肩膀高度、画面左边，第 44–61 行、第 16–29 列附近），不碰男孩的脸和手。

## 正面怎么画（`milio-front.png` + 分层）

- **照 `2_picture_B.png` 的样子**、**照 `1_front_grid.png` 的大小和位置**，在 12 px 格子上逐格重画：3/4 正面朝右、双拳握在胸前、两脚稍分开站稳（近侧腿在画面左边亮色，远侧腿在右边稍暗）。
- **脸一定要清楚**（全身最重要的地方）：深靛蓝黑卷发（亮部蓝紫光泽）、暖棕皮肤、**两只琥珀色大眼睛**（每只至少 2 格宽 3 格高：深色瞳孔 + 一格白色高光）、**咧嘴笑**（深色嘴 + 一点白牙），眉毛清楚；脸朝右前方平视。
- 衣服：红上衣 + 青绿立领 + 胸前**青绿圆坠饰**；**金色蓬起的大肩垫 + 米白流苏**；青绿斜腰带 + 金扣；品红/紫红褶裙下摆；棕色小腿；红 + 青绿绑腿；棕色凉鞋。
- 火精灵：圆滚滚的发光火球，**黄白芯、橙圈、橙红边、顶上两三簇小火苗**，**小脸清楚**（两只小黑眼 + 小嘴）。
- 从同一张成品图分出两层（同样的画布和位置，不重画）：`milio-front-boy.png`（只有男孩）、`milio-front-spirit.png`（只有火精灵，被挡的地方补完整）。

## 侧身怎么画（`milio-side-A.png` / `milio-side-B.png`，只有男孩）

- **身体转向画面右边**（像 `3_league_side.png`）：胸口朝右，**近侧（画面右边）的肩垫在前面**、远侧的肩垫在身后被挡住一部分；**双拳握在胸前**（拳头在身体右边、胸口前）；腰带、裙摆跟着转过来。
- **腿**：从侧面看**一前一后**（近侧腿在前、颜色亮；远侧腿在后、暗一档），**凉鞋朝右**，两只鞋底都踩在第 99 行；腿不要画细、画长。
- **头保持和正面版一样的 3/4 头**（卷发、两只琥珀大眼都看得见、咧嘴笑），**逐格照你画的正面版**——本包的规矩是所有动作帧都用待机那一张脸，**不另画侧脸**；只是把这颗头放在侧过来的身体上，脖子接得自然。
- 比例和正面版一样敦实；不要把侧身画瘦、画高。发顶第 30 行、鞋底第 99 行、站立点第 48 列。
- **A**：完全侧面（干净的侧身轮廓）；**B**：转得少一点（约 3/4 朝侧面，多露一点胸口和坠饰）。

## 干净（照 `4_style.png` 的统一画风）

- 每个 12 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光）；外轮廓一圈 **2 格粗的近黑描边**，里面少用黑（内部分界用材质自己的暗色）；不要抖动、渐变、碎点、零散杂色格；**三张图用同一套颜色**（照 `2_picture_B.png`）。
- 背景真透明，**alpha 只能是 0 或 255**（不要半透明光晕——上一轮的图四周有一圈半透明，alpha 从来没到 255）。不要网格线、文字、编号、边框、影子、特效。

## 附图（压缩包 `milio_model_pack.zip` 里；一次只能附五张时全部附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_front_grid.png` | 原画 B 缩到游戏大小放在 12 px 格子上（每 2 格一条浅线、每 10 格一条深线并编号）；绿线 = 发顶第 30 行，红线 = 第 99 行下沿，蓝线 = 站立点第 48 列 | **大小、位置、颜色、比例**（细节糊了，要重画） |
| `2_picture_B.png` | 你上一轮画的原画 B（大图） | **样子**：脸、衣服、火精灵都照它 |
| `3_league_side.png` | 英雄联盟的米利欧转到侧面朝右（两个角度的待机 + 一帧跑步） | **侧身怎么转**：肩垫一前一后、拳头在胸前、腿一前一后、鞋朝右 |
| `4_style.png` | 本包重做后的高清英雄（泽丽、千珏、尼菈） | 统一画风：像素粗细、粗描边、敦实 |
| `5_empty_grid.png` | 空格子，同样的行列标线 | 画布 |

## 提示词 1：正面重画 `milio-front.png`（+ 两个分层）

附 1、2、4、5。

```text
Attached images: 1 this character's front design cut down to its game size on a fixed grid of 12x12-pixel squares (a thin line every 2 squares, a numbered line every 10; green line = row 30, red line = the bottom of row 99, blue line = column 48) - the SIZE, POSITION, COLOURS and PROPORTIONS to keep, but its face and details came out MUDDY; 2 the same character as a bigger picture (the previous take) - the LOOK to keep, crisp: the face, the clothes, the fire spirit; 4 other heroes of this game in the same look (style only); 5 an empty grid with the same lines - the canvas.
REDRAW the front design of image 1 cleanly, square by square, ON THE SAME FIXED GRID: one 1024x1536 PORTRAIT PNG with a real transparent background (85 x 128 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same size and place as image 1: the top of his hair on row 30, the sandals' lowest row 99 (nothing below it), the standing point (between the sandals) on column 48, about 36 squares wide with the shoulder tassels; the fire spirit the same size and place as in image 1 (about 14 x 18 squares with its flame tips, behind him at shoulder height on the image left, about rows 44-61, columns 16-29), never covering his face or hands.
The boy, exactly as image 2: 3/4 FRONT view facing image right, both FISTS held together in front of his chest, standing firm with the feet a little apart (the near leg on the image left in full tone, the far leg on the image right a shade darker). THE FACE MUST READ CLEARLY, the most important part: fluffy curly DARK INDIGO-BLACK hair with blue-violet lights; WARM BROWN skin; TWO BIG AMBER EYES, each at least 2 squares wide and 3 tall (a dark pupil and one white highlight square); clear dark eyebrows; a happy open GRIN (a dark mouth with a little white of the teeth); looking straight ahead to the front-right. A short RED tunic, a TEAL stand-up collar and a round TEAL pendant on the chest; BIG PUFFED GOLDEN-BRONZE SHOULDER PADS with CREAM tassels; a diagonal TEAL sash with a gold buckle; a MAGENTA / PURPLE-RED pleated kilt; bare brown shins; RED-AND-TEAL ankle wraps; BROWN SANDALS. The fire spirit, exactly as image 2: a ROUND glowing fireball buddy - a bright YELLOW-WHITE core, an ORANGE ring, a DEEP ORANGE-RED rim, two or three little FLAME TIPS curling up from its top, a clear CUTE FACE (two small dark eyes, a small happy mouth).
Clean like image 4: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round each silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares except the eye highlights, no specks, no dithering, no gradients, the colours of image 2. No other effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Then, from the SAME finished picture (do not redraw), save two layers on the same canvas at the same positions: milio-front-boy.png (the boy only) and milio-front-spirit.png (the fire spirit only, any hidden part completed).
```

## 提示词 2：侧身 `milio-side-A.png`、`milio-side-B.png`（两稿，只有男孩）

附你刚画好的 `milio-front.png`、3、5、2、4。

```text
Attached images: first this character's approved front design on a fixed grid of 12x12-pixel squares (the picture you just drew: milio-front.png) - the LOOK, colours, square size and proportions of the boy, and his HEAD square for square; 3 his 3D model turned to the side, facing right (the idle at two angles, then a run frame) - how he looks SIDE-ON; 5 an empty grid with numbered lines (green line = row 30, red line = the bottom of row 99, blue line = column 48) - the canvas; 2 the same character as a bigger picture; 4 other heroes of this game in the same look (style only).
Draw ONLY THE BOY (no fire spirit) SIDE-ON, his body turned to face the IMAGE RIGHT, on the same fixed grid: one 1024x1536 PORTRAIT PNG with a real transparent background (85 x 128 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same height as the front design: the top of his hair on row 30, the sandals' lowest row 99 (nothing below it), the standing point (between the sandals) on column 48.
The boy: exactly the colours, square size, outline and details of the front design. SIDE-ON (like image 3): his chest turned to the right; the NEAR golden shoulder pad (image right) in front, the far one behind him partly hidden; both FISTS together in front of his chest (on the right side of his body); the teal sash and the magenta kilt turned with him; the legs ONE IN FRONT OF THE OTHER (the near leg in front in full tone, the far leg behind a shade darker), the BROWN SANDALS pointing RIGHT, both on row 99; do not make the legs thinner or longer. THE HEAD STAYS THE SAME 3/4 HEAD AS IN THE FRONT DESIGN, square for square (the curly dark hair, BOTH big amber eyes visible, the grin) - every frame of this game keeps the idle's face, no separate profile face - only placed on the side-on body with a natural neck. Keep the front's STOCKY proportions; do not make him thinner or taller.
Clean like the front design and image 4: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares except the eye highlights, no specks, no dithering, no gradients, ONLY the colours of the front design. No fire spirit, no effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Make TWO takes, A and B: A turned fully side-on (a clean profile body), B turned a little less (about three quarters toward the side, a bit more of the chest and the pendant showing).
```

## 交回前请检查

- 所有图都是 1024×1536、12 px 格子对齐左上角、每格一个颜色、**alpha 只有 0 / 255**。
- 正面：大小位置和 `1_front_grid.png` 一样（发顶第 30 行、鞋底第 99 行、站立点第 48 列）；**脸清楚**（两只琥珀大眼 + 高光、眉毛、咧嘴笑）；火精灵圆圆的、小脸清楚、在左边肩膀高度、不挡脸和手；分层和成品同一张画。
- 侧身：身体真的转向右边（近侧肩垫在前、拳头在胸前、腿一前一后、鞋朝右）；**头和正面版是同一颗 3/4 头**（两只眼都看得见）；颜色只用正面版的；图里没有火精灵；不比正面瘦、不比正面高。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/milio-model/`）

- `milio-front.png`、`milio-front-boy.png`、`milio-front-spirit.png`、`milio-side-A.png`、`milio-side-B.png`；未经处理的生成原稿放 `outputs/milio-model/raw/`；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 原稿逐格读回（先在 8 倍下数描边台阶量实际格子大小，再 regrid；Codex 从来不在要求的格子上），检查高度（70 行）、站立点、脸（眼睛 / 嘴清楚）、颜色映射到一套调色板；侧身贴正面的 3/4 头（one-face-all-frames）。
- 用户选侧身 A / B 后：第 2 步动作条包 MODEL_STRIPS.md 从侧身版出（动作侧面朝右；火精灵每帧整块放在他身后，不剪切；跑步按 Caitlyn 的直腿交叉步）。最后全部帧走 ppu_restyle crisp（2.2，描边约 1 游戏像素）。
