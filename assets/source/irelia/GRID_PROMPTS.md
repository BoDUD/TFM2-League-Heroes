# 艾瑞莉娅：在游戏格子上整张精修（给 Codex 的提示词）

> 现在的艾瑞莉娅（`irelia/1_current_grid.png`）是我把你画的 `irelia-front-B.png`（`irelia/2_picture.png`）按格子一格一格还原到游戏尺寸的（42 格高）。用户说**「修的挺好的」**，整体的大小、比例、姿势、位置都认可；但**细节要更好**：
> - **眼睛还是太怪**，要**像英雄联盟里的刀妹**（`irelia/3_league_face.png`）；**嘴巴不画**；
> - **背后的刀刃太模糊**，要一把一把看得清；
> - **两个手臂是歪的**、**手指没画**；
> - **腿要直**（右腿之前是歪的，我已经扶正，请保持）。
>
> 以前格温、莉莉娅、劫碰到细节糊的问题，都是你**直接在游戏格子上整张重画**以后变干净的（`irelia/4_example_picture.png` / `5_example_sprite.png` 是格温那次你交的图）。这一轮请照那次的做法，把艾瑞莉娅在格子上**整张精修一遍**：布局不动，细节画好。我收到后按格子逐格取回。

## 大小和位置（照 `1_current_grid.png`，不要变）

- 画布 **1024 × 1536，固定 26 × 26 px 的格子**（39 列 × 59 行，右边 10 px、下面 2 px 留透明）。
- **42 格高**：飞刃尖在**第 9 行**，鞋底在**第 50 行**；人从第 6 列到第 26 列（约 21 格宽），两脚中间在**第 19 列**。
- 各部位的位置（行/列都是这个 39 × 59 的格子）：
  - 飞刃束在背后画面左边：第 9–32 行，第 6–13 列；头顶深红尖角发饰：第 9–13 行，第 14–16 列；
  - 头发圆顶第 13–17 行；**脸第 17–23 行、第 14–22 列**（眼睛在第 19–21 行）；
  - 胸甲、红心、领口宝石第 25–29 行；红色前摆第 29–37 行；
  - **近侧手（画面左）第 36–39 行、第 12–14 列；远侧手（画面右）第 36–39 行、第 23–25 列**；
  - 膝盖银色星形护膝第 40–43 行；红靴第 43–50 行；鞋底第 50 行。

## 细节要求

- **眼睛（最重要，照 `3_league_face.png`）**：杏仁形、眼尾上挑的凤眼；**上眼线又黑又粗**，眼尾拉出一点上翘的尖；下眼线细；**青蓝色大虹膜**（外圈深、里面亮，一格白高光）；眼白只在眼角露一点；**深蓝色的粗眉毛，眉峰明显、往鼻梁方向压低**，和眼睛之间留一点皮肤；冷静、坚定；3/4 侧脸朝画面右，近眼完整、远眼稍窄。**不画嘴**，鼻子最多一格阴影。额头上银色头冠的 V 形尖保留。
- **飞刃要清楚**：每一把都是一片**弯月形的长刃**——深红刃身（亮红 + 暗红两档）、**刃口一条白边**、刃尖尖、**每把之间有黑色描边隔开**；刃根有**青蓝宝石**（带一格亮点）；照原稿的排列（一把最高的在中间、左上一把、中间一把银白的、左下一把带宝石），**不要糊成一堆红白碎块**。
- **手臂要直**：近侧手臂（画面左）从银色卷钩肩甲下来：上臂皮肤 → 白色臂环 → 红色护臂 → 手，**一条顺的斜线**；远侧手臂（画面右）：银色肩甲 → 红袖 → 白色肘甲 → 红色护臂 → 白腕环 → 手，也是一条顺的斜线。两只手**画出手指**（手掌 + 3–4 根分开的手指，指尖有深色分隔），自然张开垂在身侧。
- **腿要直**：两条深藏青的腿，膝盖上一个**银色四角星形护膝**（尖朝上），下面红靴、白色脚踝环、红鞋带白色鞋尖和灰色鞋跟；两只鞋平放在第 50 行。
- **头发**：深靛蓝 + 亮蓝光泽，长发从背后垂到膝盖附近，发丝有几道亮蓝高光。
- **干净**：每个 26 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光），一圈 1 格近黑描边，**里面少用黑**；不要小于一格的细节、不要碎点；最多约 24 色（尽量用现在设计里的颜色）。

## 附图（压缩包 `irelia_grid_pack.zip` 的 `irelia/` 里，按顺序附上；一次只能附五张时先附 1、2、3、4、5）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_current_grid.png` | 现在的设计，每格 26 px，黄线是量格子用的 | **大小、比例、姿势、位置**（不要画黄线） |
| `2_picture.png` | 你画的原稿 front-B | **长相和细节**：飞刃、肩甲、胸甲、手、靴子 |
| `3_league_face.png` | 英雄联盟里刀妹模型的脸 | **眼睛照它画** |
| `4_example_picture.png` | 格温：你上次在 26 px 格子上重画的图（用户认可） | 怎么画：每格一个颜色 |
| `5_example_sprite.png` | 同一张 1 倍图放大 8 倍 | 干净程度 |
| `6_quality_bar.png` | 用户认可过的英雄（格温、泽丽、辛德拉、萨勒芬妮、霞）8 倍 | 质量标准 |
| `current_1x.png` | 现在的 1 倍图（39 × 59） | 对位置 |

## 提示词

```text
Six attached images. Image 1 is this character's CURRENT game sprite, each square drawn 26x26 px with a yellow measuring grid: the SIZE, PROPORTIONS, POSE and PLACE to keep (the user approved them) - but its details need work. Image 2 is the bigger picture it was made from: the LOOK and the DETAILS to restore (the blades, the armour, the hands, the boots). Image 3 is her face on her in-game 3D model: copy her EYES from it. Image 4 is another character redrawn correctly on such a grid, and image 5 that sprite at 1x enlarged - copy that way of working: every square one flat colour, big clean areas, no half squares, no soft edges. Image 6: heroes of this game at game size the user approved - the quality to match.
Create ONE pixel-art picture of Irelia, the Blade Dancer (a calm, resolute Ionian warrior woman), a 1024x1536 PORTRAIT PNG with a real transparent background, drawn on a FIXED GRID of 26x26-pixel squares aligned to the canvas edges (39 columns x 59 rows; the right 10 px and the bottom 2 px transparent). Keep image 1's layout exactly: the figure is 42 squares tall - the blade tips on row 9, the soles on row 50 - columns 6 to 26, the middle between her feet on column 19; the blade bundle behind her on the image-left (rows 9-32, columns 6-13); the crimson crest on her head (rows 9-13, columns 14-16); the face on rows 17-23, columns 14-22 (the eyes on rows 19-21); the near hand (image-left) on rows 36-39, columns 12-14; the far hand (image-right) on rows 36-39, columns 23-25; the star knee guards on rows 40-43; the soles on row 50.
Her look (image 2): very long dark indigo hair with bright blue sheen falling behind her to her knees, a silver tiara with a V point on her forehead, a crimson crest spike edged in silver on her head; silver-white shoulder guards curling into hooks (the near one big); a crimson bodysuit with a silver breastplate, a red heart in its middle and a cyan gem at the collar; a long crimson tabard hanging in front with white borders; crimson arm guards with white bands; dark navy leggings; silver four-pointed star knee guards (pointing up); crimson boots with white ankle bands, white toe caps and grey heels.
Fix these details, the user's notes:
EYES (most important) - like image 3: almond eyes with lifted outer corners, a thick black upper lash line ending in a small upward wing, a thin lower lash line, big CYAN-TEAL irises (a darker rim, brighter inside, a one-square white glint), only a little eye white at the corners; thick dark-indigo eyebrows with a clear angle, pressed down toward the nose, a little skin between brow and eye; calm and determined; 3/4 view turned to image-right (the near eye whole, the far eye a little narrower). NO MOUTH. At most one square of nose shadow.
BLADES - crisp, each one a separate long CRESCENT blade: a crimson body (bright and dark red), a white edge along one side, a sharp pointed tip, a black outline between neighbouring blades, a cyan gem with a light square at the root; as in image 2 (the tallest in the middle, one up-left, a silver-white one in the middle, a lower-left one with the gem) - never a blur of red and white specks.
ARMS - straight, each a smooth diagonal: the near arm from the big silver hook shoulder guard: bare upper arm, a white arm band, a crimson arm guard, the hand; the far arm: silver shoulder guard, crimson sleeve, white elbow plate, crimson arm guard, white wrist band, the hand. Both HANDS with FINGERS: a palm and 3-4 separate fingers pointing down, dark lines between the fingertips, open and relaxed at her sides.
LEGS - straight; the knee guards four-pointed silver stars; both boots flat on row 50.
Clean like image 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black 1-square outline round the silhouette and little black inside (inner edges in each material's own dark shade), every detail at least one whole square, no specks, no dithering, no gradients, at most about 24 colours (use image 1's colours where you can). No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Make THREE takes (A, B, C) that differ mainly in the eyes and the blades. Deliver for each: irelia-grid-<X>.png (the 1024x1536 picture) and irelia-grid-<X>_1x.png, the same picture reduced so that each 26x26 square becomes one pixel (39x59, nearest-neighbour, transparency kept) - the game reads the 1x file, so it must match the big one square for square.
Before finishing, check each take: 42 rows from the blade tips (row 9) to the soles (row 50); every 26x26 square one colour; alpha only 0/255; at most ~24 colours; the eyes read as Irelia's cyan eyes at 1x and 2x and there is no mouth; every blade separate and crisp; both arms straight; fingers on both hands; both legs straight.
```

## 交付（`outputs/irelia-grid/`）

- `irelia-grid-A.png` / `-B.png` / `-C.png`（1024 × 1536）和 `irelia-grid-A_1x.png` …（39 × 59）；
- `irelia-grid-compare.png`：三个方案 1 倍放大 8 倍并排，旁边放 `1_current_grid.png` 的 1 倍图和英雄联盟的脸；
- 生图原稿（`raw/`）、`generation-prompts.txt`、色板、`HANDOFF.md`（**最后写**：高度、宽度、色数、每格是否单色、哪里没做到）；最好再打一个 `irelia_grid_pack.zip`。

## 交回前自查

- [ ] 42 行（飞刃尖第 9 行到鞋底第 50 行），两脚中间第 19 列，布局和 `1_current_grid.png` 一样；
- [ ] 每格一个颜色、透明度只有 0/255、不超过约 24 色、只有一种近黑描边；
- [ ] 眼睛像英雄联盟的刀妹（青蓝凤眼、黑粗上眼线带眼尾、深蓝斜眉），不画嘴；
- [ ] 飞刃一把一把清楚；两条手臂是顺的斜线；两只手有手指；两条腿是直的；
- [ ] 三个方案 A–C；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读 1 倍图（核对和大图逐格一致），放回 128 画布（鞋底第 99 行，两脚中间第 64 列），一圈描边整理（tidy_codex18 的规则），和现在的设计、原稿并排给用户挑；选定后写进 `design42/`，只修用户指出的地方，再做侧身版和动作帧。
