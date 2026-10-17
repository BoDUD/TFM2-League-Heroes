# 瑟提：照原稿重画成游戏尺寸（第 1 步第二轮，给 Codex 的提示词）

> 上一轮（`codex_model/`）的生图原稿没有画在游戏尺寸上：按它自己的格子读回来，原稿 B 是 **50×81 格**，原稿 A 是 78×118 格，都比要的 42 格大一倍以上。交付的两张 42 格造型是把原稿缩小、再把头和身体分开重采样拼出来的，脸、毛领、拳头都碎成了杂点（`4_rejected.png`）——这正是之前几个英雄被用户否掉的做法。
> **原稿 B 本身画得很好**（`1_draft.png`：按它自己的格子读回，一格一像素，没有缩放）。这一轮请**照它一模一样重画，只是小一号**：耳尖到脚底 **42 格**。
> - **直接按 42 格的格子一格一格画**，像像素画师画同一个角色的小一号版本；**不要先画大再缩小，不要删原稿的行列，不要重采样，不要把头和身体分开缩放**。画出来比 42 格大，就重画，别缩。
> - **生图原稿本身就要是 42 格的画**：之后的整理只能把方块对齐网格、把颜色归到色板，别的都不要动。每一次生图的原稿都原样交来（不缩放、不重采样）。
> - **长相、姿势、颜色、毛领、外套、拳头、鞋子都照原稿**：两边炸开的紫色毛领、金色兽头扣饰和项圈、梅子色外套、白裤子、金色尖头鞋、脑后的细辫和红珠子。色板还是上一轮的 25 色。
> - **两版只差头的大小**：耳尖到下巴 A **13 格** / B **11 格**（原稿的比例缩到 42 格大约就是 11 格）。脸照 `6_face_ref.png`：近处（画面左边）的眼睛 2×2（上行白色高光 + 深色瞳孔，下行琥珀色，上面一行睫毛），远处的眼睛 1–2 格宽、同一行，两眼之间 2 格皮肤，眉毛用头发最深的绯红往鼻子方向压低，脸中线上一格深红的嘴，琥珀色只用在眼睛上，头发不挡眼睛。
> - 画不到正好 42 格时，把最接近的那张也交来（**不要超过 48 格**），我按格子读回再整行删到 42 格（脸不删）。
> - 交付到 **`outputs/sett-model-v2/`**：`sett_design_v2_A.png`、`sett_design_v2_B.png`（1024×1024，8×8 严格网格、透明度 0/255、≤26 色、一种近黑描边）、各自的 `*_1x.png`（128×128）、**每一次生图的原稿**、色板，最后写 `HANDOFF.md`（写明每张耳尖到脚底多少格、头多少格，原稿和交付的图之间做了哪些整理），打成 `sett_design_v2_pack.zip`。

## 附图（都在 `sett/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_draft.png` | 你上一轮的原稿 B，按它自己的格子读回来（50×81 格，×8） | **照它画**：样子、姿势、颜色、毛领、拳头，全都一样 |
| `2_target_size.png` | 1024×1024 画布，原稿等比缩到 42 格的灰色剪影；红线 = 脚底下沿（第 99 行），蓝线 = 两脚中间，绿线 = 耳尖（42 格），橙线 = A 版下巴，紫线 = B 版下巴 | **大小和位置照它** |
| `3_quality_bar.png` | 包里的德莱厄斯（36×42）、亚托克斯、蔚、凯隐、贾克斯，游戏里的样子 ×8 | 像素大小和干净程度；他和德莱厄斯差不多高 |
| `4_rejected.png` | 上一轮交付的两张 42 格造型（原稿缩小再重采样拼出来的） | **反例：脸、毛领、拳头碎成杂点，不要画成这样** |
| `5_size_guide.png` | 原稿等比缩到 42 格（彩色，糊的） | 只看能放下什么，不要照它的样子 |
| `6_face_ref.png` | 原稿的头 ×16（耳尖到下巴下面） | 脸照它画 |

图像工具一次最多收 5 张参考时，先附 1、2、3、4、6，5 不附。

## 提示词：`sett_design_v2_A.png` 和 `sett_design_v2_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

```text
Six attached images. FIRST: YOUR OWN earlier draft of this character, read back square by square (50 x 81 squares, shown at 8x) - copy it EXACTLY: the same man, the same upright pose (chest out, arms hanging with clenched fists), the same colours, the same face, hair, ears, braid, violet fur mantle bursting out on both sides, gold beast-head clasps and torc, plum coat, white trousers and gold curled shoes. Only its SIZE changes. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image scaled evenly to its new size: use it for his SIZE and his PLACE in the canvas (the head may be bigger, see the HEAD line). THIRD: heroes of this game at game size as they are in the game now, at 8x, approved by the user - he should be about as tall as the first of them (42 squares) and match their crisp, clean pixel look. FOURTH: REJECTED versions - they were made by shrinking the FIRST image and resampling the head and the body separately: the face, the mantle and the fists broke into specks of colour. Do NOT draw him like them. FIFTH: the FIRST image scaled evenly to the new size in colour - use it ONLY to see what fits where; it is blurry, do not copy its look. SIXTH: the FIRST image's head, big - copy the face.
Task: REDRAW the FIRST image a size smaller as a crisp game sprite - a low-resolution pixel-art character shown enlarged 8x, every pixel one 8x8 square on a single 8-px grid: 42 squares from the tips of his ears to his soles (the FIRST image has 81). Draw it directly at that size, square by square, like a pixel artist making a smaller version of the same sprite - do NOT draw it bigger and shrink or resample it, do NOT delete rows or columns from the FIRST image, do NOT scale the head and the body separately: that is what broke the FOURTH image. If your drawing comes out bigger than 42 squares, draw it again smaller instead of shrinking it. The generated image itself must be the 42-square drawing; afterwards only snap its squares to the grid and its colours to the palette.
Shapes that must still read at this size: two pointed ears on top of the head (each about 2 squares wide, 3 tall, crimson outside, dark violet inside); the crimson spiky hair; a 1-square braid behind the near shoulder with a red bead and a gold tip; the violet mantle's tufts reaching 3-4 squares past both shoulders but never in front of the face; two gold beast-head clasps (about 4x3 squares each) and the gold torc; each fist about 5x5 squares (a plum glove, 3-4 gold knuckle squares, a gold wrist ring, 2 rows of pale bandage above); the plum coat with its gold edge, its tails at least 1 square above the soles; the white trousers showing both legs in pale blue-grey shades with a 1-square gold stripe; gold curled shoes, the tips pointing right.
Clean (as the FIRST image): at most 26 colours, every material 2-3 flat shades plus a small highlight, big solid areas, no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette and inside it the materials' own darker shades, never a second black ring; the mantle reads violet, the coat and the gloves plum, never black.
Palette (the FIRST image's colours): #0B0508 (the outline, the only near-black) #5A0B2C #AC133A #DA2850 #F2607A (hair) #8A4A33 #C07942 #E39C55 #FCC377 (skin) #F2A01E (the eyes only) #2F134E #3E1A67 #53278B #6A36AE (mantle, the ears' inside) #371321 #511D2F #6E2A44 (coat, gloves) #8A5A12 #D28F33 #F6B830 #FCDC5A (gold) #8E97B0 #B8BFCE #DDE3ED #F6F8FC (trousers, bandages).
Face, as the SIXTH image: a 3/4 face turned to image right; the NEAR eye (image left) 2 squares wide and 2 tall - top row a white highlight square and a dark pupil square, bottom row AMBER - with a dark lash row over it; the FAR eye 1-2 squares wide on the SAME rows; 2 squares of skin between the eyes; short heavy brows in the hair's darkest crimson (not the outline black) sloping down toward the nose; one dark-red mouth square on the face's middle line two rows under the eyes; no dark squares joining the jaw's corners to the chin; the hair never covers an eye. The amber only in the eyes.
Size and place: where the SECOND image's grey shape stands: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the tips of his ears on the green line (42 squares), the chin on the orange line (version A) or the purple line (version B). Nothing below the soles.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green, never magenta - the hair is crimson). No grid lines, no text, no border, no shadow.
Before finishing, check: 42 squares from the tips of his ears to the soles; the head as tall as the HEAD line says; the same look as the FIRST image, side by side; all squares 8x8 on one grid; at most 26 colours; one outline colour; both ears, both eyes (level) and both fists visible; nothing below the soles.
VERSION A (sett_design_v2_A.png): HEAD 13 squares from the tips of his ears to the chin; 42 squares in all.
VERSION B (sett_design_v2_B.png): HEAD 11 squares from the tips of his ears to the chin; 42 squares in all.
```

## 交回前自查

- [ ] 生图原稿本身就是 42 格的画（每一次的原稿都交了）；整理只对齐了网格、归了色板；
- [ ] 耳尖到脚底 42 格（实在不行最接近的那张，不超过 48 格）；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 和原稿放在一起比：样子一样；A 版头 13 格、B 版 11 格；两只兽耳、两只眼睛（同一行）、两只拳头、两边的毛领都看得见；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；最后写 `HANDOFF.md`，打成 `sett_design_v2_pack.zip`。

## 包怎么做的

`python tools/art/pack_sett_model_redo.py --out <文件夹>/sett`：原稿 B（`codex_model/sett_design_B_raw.png`）用 `scripts/regrid.py` 按它自己的格子读回成 1 号图，其余几张从它和包里英雄的精灵图生成。
