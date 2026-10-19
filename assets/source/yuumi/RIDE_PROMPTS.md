# 魔法猫咪 悠米：附身小猫按格子重画（给 Codex 的提示词）

> 上一步你画的 B（趴在摊平的书上，`1_model_B1.png` / `1_model_B2.png`）**样子和姿势用户都满意**，但游戏里它只有 **21 格高**（画在附身队友的头顶上），我把它缩到 21 格（`2_target_B.png`）就糊了：书变成一团、眼睛碎了。请照**格温那次的做法**（`5_method/`：先用画图模型重画，再按固定格子逐格取色、固定调色板、硬透明，交付大图和 1 倍图）把它**在 21 格上重新画清楚**。
> - **固定格子：每格 50 px**，画布 **1254 × 1254**，网格从左上角 (0, 0) 对齐；**最高点 y = 100**（触须小球顶，橙线），**最低点 y = 1150**（尾巴尖，红线）：**正好 21 格高，约 22–24 格宽**（`3_layout_B.png`）。
> - 交付的大图里**每一格只有一个颜色**（格内所有像素 RGBA 相同），同时交一张逐格对应的 **1 倍图**（约 24 × 21 像素）。画两稿。

## 21 格里要画清楚的地方

- **头约占 10–11 格高**，是整张图的重点，**和待机的脸是同一张**（`4_head.png` 是用户定下的待机头部，8 倍；这里要按约一半的格子画）：淡紫蓝的头、**白色的脸和嘴边**；**两只蓝眼睛：每只 2 × 2 格（或 2 宽 3 高），一样高，各带 1 格白色高光**，眼睛上面 1 格深色眼线；**粉色鼻子 1 格**；耳朵外面淡紫蓝、里面粉红（各 2–3 格）；额头 1 行**金色头饰**；头顶伸出**金色触须**（1 格宽的弯线）和末端的**蓝色小球**（2 × 2 格，1 格高光）。脸朝右前方，**两只眼睛都看得见**。
- **身子**：趴着，淡紫蓝 2 档；胸前 1–2 格**深蓝蓬毛**和**金项圈**；两只**白色前爪**伸出书的前沿（画面右边）。
- **书**：完全摊平、**米黄书页朝上**（1–2 行，看得见一道中缝），下面一行**深红封面**、**金色的边和书角**（书的前后两角各 1–2 格金）。
- **尾巴**：从书的后沿（画面左边）垂下去，淡紫蓝，**尾巴尖一簇金毛**（2 × 2 格左右）。
- **一圈 1 格的近黑外描边**，连续不断；猫和书之间、尾巴和书之间也有描边分开；每种材质只用 2 档，没有孤立的单个杂色格。

## 附图（压缩包 `yuumi_ride_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_model_B1.png`、`1_model_B2.png` | 你上一步画的 B（用户满意的样子和姿势） | **样子、颜色、姿势** |
| `1_picture_B.png` | 你第 0 步画的 B | 细节参考 |
| `2_target_B.png` | B 缩到 21 格、每格 50 px（糊的，只看大小和位置） | **大小、位置** |
| `3_layout_B.png` | 同上加网格线：橙 = 最高点，红 = 最低点 | 对齐网格、21 格的高度 |
| `4_head.png` | 用户定下的待机头部（8 倍） | **脸**：同一张脸，按一半的格子画 |
| `5_method/gwen-grid-A.png`、`gwen-grid-A_1x.png`、`HANDOFF.md` | 格温那次的格子重画交付 | **做法和交付格式**（只看做法，不看样子） |
| `style/6_style_zoe.png` | 本包的佐伊（同密度，8 倍） | **只看风格** |

## 提示词（同一段，画两稿）

```text
Attached: 1_model_B1 and 1_model_B2 are your own earlier pixel-art drawings of this character lying on her flat open book - a small magical chibi cat with lilac-blue fur, a white face and paws, big blue eyes, pink ears and nose, a gold circlet with a curling gold antenna ending in a blue orb, a deep-blue chest ruff with a gold collar, a long tail ending in a gold tuft, lying on the cream pages of her book laid flat (dark-red covers, gold edges and corners), both front paws stretched forward over the front edge, the tail hanging down over the back edge - their LOOK and POSE are approved, but in the game this picture is only 21 squares tall; 2_target_B is that drawing cut to 21 squares with 50 px squares: its SIZE and PLACE are right but it is muddy; 3_layout_B the same with grid lines (orange = the top, red = the bottom); 4_head the approved head of this character enlarged 8x - the SAME face, drawn with about half as many squares; 5_method shows the way of working: an AI redraw, then every fixed grid cell given one colour, a fixed palette, hard alpha, a big picture plus its 1x picture; 6 STYLE ONLY: another character of the same game at this square density, 8x.
Redraw this cat lying on the flat book as a clean pixel-art picture on a FIXED GRID: a 1254x1254 PNG, real transparent background (alpha only 0 or 255), squares of exactly 50 px aligned from the canvas corner, EVERY CELL ONE COLOUR; the top of the antenna's orb at y 100 and the tail tuft's bottom on y 1150 - exactly 21 squares tall, about 22-24 squares wide; also its 1x picture, one pixel per cell.
With 21 squares make it READ: the head about 10-11 squares tall, the same face as image 4 - TWO BLUE EYES each 2x2 squares (or 2 wide, 3 tall) at the SAME height, each with ONE white highlight square and a dark lash square above, a one-square pink nose, white muzzle and cheeks, pink inner ears, one row of gold circlet, the curling one-square-wide gold antenna with a 2x2 blue orb with a highlight; the face turned to the front-right with BOTH eyes visible; the body lying flat, lilac-blue in 2 shades, a little deep-blue ruff and the gold collar, both white front paws over the book's front edge (image right); the book flat, one or two rows of cream pages with a centre line, a row of dark-red cover below, gold edges and corners; the tail hanging down over the back edge (image left) with a gold tuft at its end.
One continuous 1-square near-black outline round the figure, the cat and the book and the tail separated by outline where they meet; every material in 2 flat shades; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines.
```

## 交回前请检查

- 1254 × 1254，真透明，**alpha 只有 0 / 255**；**每格 50 px、格内一个颜色**；最高点 y 100、最低点 y 1150，**正好 21 格高**；1 倍图和大图逐格一致。
- 两只蓝眼睛一样大、一样高、各带 1 格白高光，两只都看得见；粉鼻子；金头饰、金触须和蓝色小球；白色前爪伸出书沿；书页米黄、封面深红、金边金角；尾巴垂下、金色尾尖。外描边连续。

## 交付（`outputs/yuumi-ride/`）

- `yuumi-ride-1.png`、`yuumi-ride-1_1x.png`、`yuumi-ride-2.png`、`yuumi-ride-2_1x.png`；选中的 AI 原稿放 `outputs/yuumi-ride/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/yuumi_ride_done.zip`。中间不要停，两稿都画完再交。

## Claude 收到后（给 Claude 看）

- 检查 1 倍图（21 行、格内单色、硬 alpha），在队友头上按游戏大小并排看（金克丝、艾希、盖伦、布隆），给用户挑；选定后写 `assets/source/yuumi/hd/ride.png`，做主包的 `w_ride` buff 画面（1.5 倍密度：league.dll 给这张特效图加高清帧，不生效时退回 1 倍）。
