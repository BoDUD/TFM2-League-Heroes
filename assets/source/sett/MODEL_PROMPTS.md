# 瑟提：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作。照用户选的原画 A（英雄联盟的待机：挺胸抬下巴、两臂垂在身侧），画 A、B 两版（只差头的大小），给用户挑头身比。**
>
> - **大小**：耳尖到脚底 **42 格**（和德莱厄斯一样，亚托克斯、蔚是 40 格）。脚底在第 99 行（y=792–799，红线），两脚中间在 x=512（蓝线）；绿线 = 耳尖，橙线 = A 版下巴，紫线 = B 版下巴。大小、姿势和位置照 `2_target_size.png`（原画按游戏尺寸缩出来的灰剪影）。
> - **两版只差头的大小**：耳尖到下巴 A **13 格** / B **11 格**。原画的头只占身高 16%，照原画缩到 42 格，脸只剩 6–7 格、眼睛会糊掉，所以两版的头都比原画大（灰剪影的头是原画的大小，以橙线、紫线为准）。
> - **转成朝右的 3/4 正面**：原画 A 几乎正对着镜头。姿势和长相照 A，身子稍微往画面右边转：近侧（画面左边）的肩膀大一点，脸、胸口和脚尖朝右。转多少看 `7_league_idle.png`（英雄联盟的模型待机就是这个角度）。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，只有一圈近黑描边。紫色毛领、梅子色外套和手套要看得出颜色，不要糊成黑的；白裤子要用灰蓝的阴影画出两条腿。**以前好几个英雄第一稿都画成了两倍大，这次请画大方块。**
> - **脸**：近处（画面左边）的眼睛 2×2：上行白色高光 + 深色瞳孔，下行琥珀色，上面一行睫毛；远处的眼睛 1–2 格宽，和近眼同一行；两眼之间 2 格皮肤；眉毛用头发最深的绯红（不要用描边黑），往鼻子方向压低（傲气）；嘴是脸中线上一格深红，眼睛下面两行；下巴两角不要连到下巴线的深色格；头发不能挡眼睛。琥珀色只用在眼睛上。
> - **要看得出的东西**：头顶两只竖起的兽耳（各约 2 格宽、3 格高，外面绯红、里面深紫）；脑后一条 1 格宽的细辫、末端红珠子和金尖坠；金色 V 字项圈；两肩前面的金色兽头扣饰（各约 4×3 格）；毛领一簇簇往两边、往后炸开，但不挡脸；两只拳头各约 5×5 格（梅子色手套、3–4 格金色指节、手腕一圈金环、上面 2 行浅色绷带）；白裤子外侧一条 1 格的金色细条纹；金边的尖头翘鞋，鞋尖朝右。
> - **脚底以下什么都不能有**（游戏在脚下画血条）：外套下摆、细辫、毛领都要在脚底线以上（外套下摆至少比脚底高 1 格）。背景透明（做不到用纯绿 `#00FF00`，**不要洋红**：他的头发是绯红色）。
> - **直接按游戏尺寸画**，不要先画大再缩小。`6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，不要照它。
> - **画不到正好 42 格时，把最接近的那一张也交来（不要超过 48 格）**，我按格子读回再整行整列删到 42 格（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 **`outputs/sett-model/`**：`sett_design_A.png`、`sett_design_B.png`（1024×1024）和各自的原尺寸图 `*_1x.png`（128×128），**生图原稿也一起交（不要缩放或重采样过的）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来耳尖到脚底是多少格、头是多少格），打成 `sett_design_pack.zip`。

## 附图（都在 `sett/` 里，按编号顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A（白底） | **长相、颜色和姿势** |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画按游戏尺寸缩出的灰剪影；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 耳尖（42 格），橙线 = A 版下巴，紫线 = B 版下巴 | **大小、姿势和位置照它**（头以橙线、紫线为准） |
| `3_quality_bar.png` | main 里的德莱厄斯（36×42）、亚托克斯（40×40）、蔚（30×40）、凯隐（40×40）、贾克斯（44×36），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**；他和德莱厄斯差不多高 |
| `4_head.png` | 原画的头，放大 | 头发、兽耳、脸、眼睛 |
| `5_fists.png` | 原画的两只拳头，放大 | 手套、金色指节、手腕的金环、绷带 |
| `6_size_guide.png` | 原画直接缩到游戏尺寸，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟的模型待机（用户从本机客户端导出，Riot 素材，只在这个包里） | **只看身子往右转多少**（3/4 的角度） |

图像工具一次最多收 5 张参考时，先附 1、2、3、4、7，5、6 不附。
（以前的包还附了一张团战经理2 原版英雄的 8 倍图；这个会话在云端读不到游戏本体，这次用 3 号图代替。）

## 提示词：`sett_design_A.png` 和 `sett_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`sett/` 里的 1–7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character - copy his look, colours and pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image's silhouette shrunk to game size - use it for his SIZE, his POSE and his PLACE in the canvas (the head will be bigger than in that shape, see the HEAD line). THIRD: heroes of this game as they look in the game now, shown at 8x, approved by the user (big fighters) - match their crisp, clean pixel look and their size; he is about as tall as the first of them. FOURTH: the FIRST image's head, big - the hair, the ears, the face and the eyes to copy. FIFTH: the FIRST image's two fists, big - the gloves, the gold knuckles, the gold wrist rings and the bandages. SIXTH: the FIRST image shrunk straight to game size - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the same character's 3D model standing in the same idle pose - use it ONLY for how far his body turns toward image right (a 3/4 view); copy nothing else from it.
The character: a towering, very muscular pit fighter - broad shoulders, a huge bare chest and abs, thick arms, a narrow waist, long legs, warm tan skin. HEAD: vivid CRIMSON spiky hair with a few locks over the forehead; two pointed furry EARS standing up on top of his head (crimson outside, dark violet inside); a thin crimson BRAID hanging behind his near shoulder to his waist, ending in a red bead and a small gold spike; AMBER eyes, heavy brows, a strong jaw, a proud expression. A GOLD V-shaped torc round his neck; two GOLD BEAST-HEAD clasps on the front of his shoulders pinning a HUGE shaggy VIOLET FUR MANTLE that bursts out to both sides and behind his shoulders in big pointed tufts. A long SLEEVELESS dark PLUM coat hanging from his shoulders, open in front, gold trim along its edges, its tails down to his ankles. Bare upper arms, forearms wrapped in pale bandages, dark plum fingerless gloves with GOLD knuckles and a GOLD ring round each wrist - the FISTS are big, his weapons. A gold V-shaped belt buckle; fitted WHITE trousers shaded in pale blue-greys with a thin gold stripe down each outer side; curled pointed shoes in gold and dark red, the tips pointing right. Pose (the FIRST image, his idle): standing upright, leaning back a little, chest out, chin slightly raised; both arms hang at his sides slightly bent, the fists clenched; feet apart, the front foot a step ahead - turned a little toward image right into a 3/4 FRONT view as in the SEVENTH image (the near shoulder on image left a little bigger, the face, the chest and the toes toward image right).
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 42 squares from the tips of his ears to his soles. Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 42 squares tall, no more.
Game proportions: the HEAD line at the end says how many squares from the tips of his ears to the chin; the rest shares the remaining squares. Things that must still read: each ear about 2 squares wide and 3 tall; each fist about 5x5 squares (a plum glove, 3-4 gold knuckle squares, a gold wrist ring, 2 rows of pale bandage above it); each beast-head clasp about 4x3 squares of gold; the torc 1-2 rows of gold; the braid 1 square wide with its red bead and gold tip; the mantle's tufts reaching 3-4 squares out past the shoulders on both sides but never in front of the face; a 1-square gold stripe down each trouser leg.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines - never a second black ring inside the outline; keep the dark parts coloured (the mantle reads violet, the coat and the gloves plum, never black); the white trousers show both legs with pale blue-grey shading.
Palette (from the FIRST image, adjust if needed): near-black outline #0B0508 (the only near-black); hair crimson #5A0B2C #AC133A #DA2850 #F2607A; skin #8A4A33 #C07942 #E39C55 #FCC377; eyes amber #F2A01E (the eyes only); mantle and the ears' inside violet #2F134E #3E1A67 #53278B #6A36AE; coat and gloves plum #371321 #511D2F #6E2A44; gold #8A5A12 #D28F33 #F6B830 #FCDC5A; trousers and bandages #8E97B0 #B8BFCE #DDE3ED #F6F8FC; shoes gold with the hair's dark crimsons.
Face (most important detail), as the FOURTH image: a 3/4 face turned to image right; the NEAR eye (image left) 2 squares wide and 2 tall - top row a white highlight square and a dark pupil square, bottom row AMBER - with a dark lash row over it; the FAR eye 1-2 squares wide on the SAME rows; 2 squares of skin between the eyes; heavy short brows in the hair's darkest crimson (not the outline black) just above the eyes, sloping down toward the nose (proud, stern); one dark-red mouth square on the face's middle line two rows under the eyes; no dark squares joining the jaw's corners to the chin line; the hair's locks frame the face but never cover an eye. The amber is used ONLY in the eyes.
Size and place: exactly where the SECOND image's grey shape stands: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the tips of his ears on the green line (42 squares), the chin on the orange line (version A) or the purple line (version B). Nothing below the soles (the game draws the health bar right under them): the coat's tails, the braid and the mantle stay above the soles' line, the coat's tails at least 1 square above it.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green, NEVER magenta or pink - the hair is crimson). No grid lines, no text, no border, no shadow.
Before finishing, check: 42 squares from the tips of his ears to the soles; the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 26 colours; one outline colour; both ears, both eyes (level) and both fists visible; the mantle, the coat and the gloves coloured, not black; a 3/4 view facing right; nothing below the soles.
VERSION A (sett_design_A.png): HEAD 13 squares from the tips of his ears to the chin; 42 squares in all.
VERSION B (sett_design_B.png): HEAD 11 squares from the tips of his ears to the chin; 42 squares in all.
```

## 交回前自查

- [ ] 耳尖到脚底 42 格（实在不行最接近的那张，不超过 48 格）；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] A 版头 13 格、B 版 11 格（耳尖到下巴）；两只兽耳、两只眼睛（同一行）、两只拳头都看得见；
- [ ] 往右转的 3/4 正面；毛领不挡脸；外套下摆、细辫在脚底线以上；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；毛领紫、外套和手套梅子色，不是黑的；白裤子有灰蓝阴影；
- [ ] 生图原稿一起交；最后写 `HANDOFF.md`（每张多少格、头多少格），打成 `sett_design_pack.zip`。

## 包怎么做的

`python tools/art/pack_sett_model.py --out <文件夹>/sett --league <用户 refs 里的 4_sett_ingame_front.png>` 从原画 A 和包里英雄的精灵图生成 1–6 号图（7 号是用户的参考图，Riot 素材，只放进包里，不进仓库）。
