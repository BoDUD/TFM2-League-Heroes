# 凯南：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`kennen/1_kennen_source.png`，你上一轮画的：英雄联盟的待机，两只爪手举在胸前，大金色手里剑背在背上）在**游戏尺寸**重新画。两版只差背上手里剑的大小：
> - **版本 A**：手里剑照原画，和兜帽差不多宽，上面的尖角比兜帽顶高约 **6 格**（从尖角到脚底 38 格），左边的尖角伸出兜帽约 5 格；
> - **版本 B**：手里剑小一些（原画的约三分之二），上尖角只比兜帽顶高约 **3 格**（总高 35 格），左尖角伸出约 3 格；其余和 A 一样。
>
> 其余两版都一样：
> - **大小（约德尔人，很小）**：从**兜帽顶（不算耳朵）到脚底 32 格**，耳朵尖再高约 2 格；兜帽头（帽顶到面罩下沿）约 14–15 格高、16 格宽，脸的开口约 9 格宽，每只眼睛 2×2；整体宽约 **24 格**。和游戏里的约德尔人一样大：菲兹 32 格、小炮 34、安妮 34、提莫连帽子 38（`kennen/3_quality_bar.png`）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线），绿线 = 兜帽顶（32 格）、紫线 = 耳朵尖（34）、橙线 = 手里剑顶（A 版 38）；大小和位置看 `kennen/2_target_size.png`（他自己原画的灰色剪影，正好这么大）。
> - **干净、不要细节（最重要）**：最多 24 色，每种材质 2–3 档平涂加一点高光，大块纯色，去掉这个尺寸看不清的细节。以前乐芙兰、卡莎的第一稿都画成了两倍大（86 格、79 格），因为细节越多，生图模型画的方块越小、整个人越大——**这次请画大方块，兜帽顶到脚底只有 32 格**。
> - **直接按游戏尺寸画**，不要先画大再缩小（缩小会把细节弄碎）。`kennen/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - **画不到正好 32 格时，把最接近的那一张也交来（兜帽顶到脚底不要超过 40 格）**，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 24 色，描边只用一种近黑色。交付 `kennen_design_A.png`、`kennen_design_B.png`（1024×1024）和各自的原尺寸图 `kennen_design_A_1x.png`、`kennen_design_B_1x.png`，生图原稿，`HANDOFF.md`（**最后写**，写明每张读回来兜帽顶到脚底是多少格、总高多少格）和色板，最好打成一个 zip（`kennen_design_pack.zip`）。

## 附图（都在压缩包的 `kennen/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_kennen_source.png` / `1_kennen_source_white.png` | 用户选的原画 A（透明底 / 白底） | **长相**：兜帽和耳朵、金色闪电镶边、蓝眼睛和眉毛、面罩、长袍、肩甲的闪电标志、胸前背带、爪子手套、短腿和忍者鞋、背上的大手里剑、颜色和姿势 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），他自己原画的灰色剪影 = 大小和位置（版本 A）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 兜帽顶（32 格），紫线 = 耳朵尖（34），橙线 = 手里剑顶（38） | **大小和位置照它** |
| `3_quality_bar.png` | main 里的菲兹（32 格）、小炮（34）、安妮（34）、提莫（38，连帽子）和乐芙兰（43，大人），游戏里现在的样子 ×8，同一条脚底线 | **像素大小、干净程度和身高照它们**（凯南和提莫差不多高） |
| `4_tfm2_style.png` | 团战经理2 原版的忍者、雷电法师、刺客、双刀、影法师 ×8 | 原版的像素画法：大块平涂、少色、形状清楚 |
| `5_face_ref.png` | 原画 A 的兜帽、脸和手里剑中心，放大（750×730） | 兜帽、耳朵、眼睛、眉毛、面罩 |
| `6_size_guide.png` | 原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：兜帽顶到脚底 32 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照原画**：约德尔人，兜帽头很大（约占身高的 45%），小身体、很短的腿；两只爪手举在胸前；手里剑背在背上，两个尖角从兜帽后面左上方和远侧肩膀后面露出来。
- **干净**：最多 24 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：袍子是深紫，手套和鞋是深梅紫，金是暖棕），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **颜色**：紫色兜帽和长袍 4 档（最亮的淡紫在帽顶和肩膀）；深梅紫 3 档（手套、绑腿、鞋、肩甲、背带）；金 4 档（闪电镶边、肩甲标志、手里剑）；皮肤 3 档；眉毛深棕；眼睛蓝色虹膜、深色瞳孔、白色高光；钢蓝 2 档（手背护片、背带扣）。**蓝色只用在眼睛上**。
- **脸（最重要的细节）**：照 `5_face_ref.png`：两只眼睛都在兜帽开口里、**在同一行**，各 **2 格宽、2 格高**：上一行白色高光 + 深色瞳孔，下一行两格蓝色；近侧眼（画面左）在脸的近侧，远侧眼靠着远侧脸颊；每只眼睛和帽檐之间隔一格皮肤；每只眼睛上面一对深棕色眉毛格，往鼻梁方向压低；眼睛正下方是面罩的金色上沿，下面是紫色面罩（不画嘴，面罩盖着）；手里剑在兜帽后面，绝不挡脸。
- **手**：两只前臂在宽袖子里、2–3 格粗、举在胸前，末端是小的深梅紫爪子手套，三根 1 格的爪，手背一格钢蓝，连着手臂（不要 1 像素的黑细棍、不要飘着的手）。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`kennen_design_A.png` 和 `kennen_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`kennen/` 里的 1–6 号图，按顺序。

```text
Six attached images. FIRST: the approved illustration of this character - copy his look: a tiny yordle ninja; a big round VIOLET-PURPLE hood covering his whole head, with two short pointed EARS standing up on top (a small dark cross-stitched strap at each ear's base); zigzag GOLD lightning trims over the hood and a thick gold rim round the face opening; inside it a band of warm peach skin with two BIG BRIGHT BLUE EYES under thick dark-brown brows slanting down toward the nose (a determined look); a violet cloth MASK over his nose, mouth and chin with a gold zigzag along its top edge; a loose violet ROBE with wide sleeves and zigzag gold trims down the front and along the hem; a dark plum shoulder plate with a GOLD LIGHTNING-BOLT emblem on his near shoulder; a dark strap across his chest; dark plum CLAWED GLOVES (three curved claws each) with a small steel-blue plate on the back of each hand, both hands held forward at chest height; very short legs in dark plum wrappings, small dark plum ninja shoes; and the huge four-pointed GOLD SHURIKEN strapped on his back, two of its points sticking out up-left behind his hood and behind his far shoulder (a round hole in its centre, engraved lightning lines) - his signature prop. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - his own silhouette at game size - use it for his SIZE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user (four small yordles and one adult) - match their pixel size and their crisp, clean look; he is about as big as the fourth one (38 squares including the hat). FOURTH: official heroes of this game at 8x (ninjas and a lightning mage) - the pixel size and cleanliness to match: big flat areas, few colours, bold readable shapes. FIFTH: the FIRST image's head, big - the hood, the ears, the eyes, the brows, the mask to copy. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look.
Task: draw him as a SMALL game sprite - a tiny low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 32 squares from the top of the hood (not counting the ears) to his soles, the ears' tips about 2 squares higher, and the shuriken's top point as the VERSION lines at the end say. Each square is BIG compared with his body: his whole hooded head (hood top to the mask's chin) is only about 14-15 squares tall and 16 wide, the face opening about 9 squares wide, each eye 2x2 squares. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD and FOURTH images. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 32 squares from the hood's top to the soles, no more.
Clean, not detailed (most important): at most 24 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Drop what does not read at this size: the gold zigzags are 1-square lines with 2-3 sharp turns, the shoulder emblem a 3x4 gold zigzag on a plum plate, each claw one square, the robe's folds two or three lines, the shuriken four clean points round a 2x2 hole with one gold engraving line.
Palette (from the FIRST image, adjust if needed): #0B060E outline; violet hood and robe #3A1452 #5E2386 #8A36B8 #B657DE (highlight on the hood's top and the shoulders); dark plum gloves, legs, shoes, plate, strap #251324 #452348 #6E3E75; gold trims, emblem and shuriken #7A3E1C #CB7420 #F8A23B #FEDC80; skin #8E3E30 #C9714E #EDA27A; brows #4C1819; eyes #3FAEF8 (blue iris, the eyes only) #02112D (pupil) #F5F5F5 (eye shine); steel plates and the strap's buckle #4A4E70 #8A8FB0.
Face (most important detail), as the FIFTH image: both eyes visible on the SAME rows inside the hood's opening, each 2 squares wide and 2 tall - the top row the white shine beside the dark pupil, the bottom row two blue squares; the near eye (image left) on the face's near side, the far eye against the far cheek; one square of peach skin between each eye and the hood rim; one dark-brown brow square-pair above each eye slanting down toward the nose; the mask's gold top edge right under the eyes, the violet mask below it (no mouth: the mask covers it); the hood rim frames the face; the shuriken stays behind the hood, never in front of the face. The blue is used for nothing but the eyes.
Hands: both forearms 2-3 squares thick in wide violet sleeves held forward at chest height, each ending in a small dark plum glove with three 1-square claws and a steel square on its back, joined to the arm (no 1-pixel black sticks, no floating hands).
Pose, size and place: the pose of the FIRST image, 3/4 FRONT view facing right, exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the point between his feet on the middle column (x=512, the blue line); the green line of the SECOND image is the hood's top (32 squares over the soles), the purple line the ears' tips (34), the orange line the shuriken's top (38). Nothing below the soles (the game draws the health bar right under them).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: 32 squares from the hood's top to the soles (compare with the SECOND image); all squares 8x8 on one grid; at most 24 colours; one outline colour; both eyes visible and clear, 2x2, level; blue only in the eyes; both hands joined to the arms; the shuriken behind him with two points showing; nothing below the soles.
VERSION A (kennen_design_A.png): the FIRST image's shuriken - as wide as the hood, its top point about 6 squares above the hood's top (38 squares from the shuriken's top to the soles), its left point sticking out about 5 squares left of the hood.
VERSION B (kennen_design_B.png): a more compact shuriken - about two thirds of the FIRST image's size, its top point about 3 squares above the hood's top (35 squares from its top to the soles), its left point about 3 squares left of the hood; everything else the same as version A.
```

## 交回前自查

- [ ] 兜帽顶到脚底 32 格（最多 40），A 总高约 38、B 约 35；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 24 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png`、`4_tfm2_style.png` 一个像素大小；
- [ ] 两只眼睛 2×2、同一行、看得清；蓝色只在眼睛上；面罩盖住嘴；手里剑在兜帽后面、不挡脸；
- [ ] 两只爪手都连着手臂；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和提莫、小炮、菲兹放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
