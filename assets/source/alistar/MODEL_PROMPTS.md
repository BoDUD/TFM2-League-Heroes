# 阿利斯塔：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`alistar/1_alistar_picture.png`，原画 A：弓背前探、双手垂在身前）在**游戏尺寸**重新画。
> - **大小**：包里的壮汉在游戏里是 42–47 行（墨菲特 47、布里茨 44、原版食人魔 44），所以**版本 A 从鬃毛顶到牛蹄底 42 格**（约 30 格宽）、**版本 B 46 格**（约 33 格宽，和食人魔一样大）。牛蹄最低一行在第 99 行（y=792–799，红线），两只蹄子中间在中间那一列（x=512，蓝线）；绿线 = 鬃毛顶，黄线 = 眼睛，橙线 = 下巴（A 版；B 版是同一个形状放大到 46 行，蹄底和中线不变）。大小、姿势、位置照 `alistar/2_target_size.png`（原画直接缩到 42 行的灰剪影）。原画的头连角已经约占身高三分之一，不用再改比例。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。紫色皮肤分出几档紫色、肌肉亮面是淡紫，**肌肉画成几块大的平涂形状，不要很多小块**；去掉这个尺寸看不清的细节：伤疤 = 2–3 格粉色，镣铐花纹 = 一道铜色线，断链 = 3–4 格链环，手指 = 2–3 格粗短指头、一格灰指甲，鬃毛 = 4–6 根大的青色尖刺。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，行数不要超过版本写的数**。
> - **脸（最重要）**：3/4 朝右的牛头，深紫色眉骨，**两只红眼睛**（近处 2 格宽、远处 1–2 格，同一行），下面是颜色深一点的口鼻、两格深色鼻孔，**口鼻前端下面挂 2–3 格的银色鼻环**，下巴一行短胡子；牛角是象牙白加一档暗色，**角和眼睛之间留一行紫色**，青色鬃毛从两角之间竖起来。
> - **直接按游戏尺寸画**，不要先画大再缩小。`alistar/7_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好的行数时，把最接近的那一张也交来（不要超过 52 格）**，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 `outputs/alistar-model/`：`alistar_design_A.png`、`alistar_design_B.png`（1024×1024）和各自的原尺寸图 `alistar_design_A_1x.png`、`alistar_design_B_1x.png`，**生图原稿**（未经脚本拼装的那几张，放 `raw/`），色板，`HANDOFF.md`（**最后写**，写明每张读回来鬃毛顶到蹄底是多少格），最好再打成一个 zip（`alistar_design_pack.zip`）。

## 附图（都在压缩包的 `alistar/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_alistar_picture.png` | 用户选的原画 A | **长相和姿势**：蓝紫皮肤、青色尖鬃毛、象牙白大弯角（画面左边那只角有铁箍）、红眼睛、银鼻环、两只很宽的断铁镣铐和断链、大手、棕色皮围裙、短粗的腿和黑色牛蹄 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画直接缩到 42 行的灰剪影；红线 = 蹄底那一行的下沿，蓝线 = 两蹄中间，绿线 = 鬃毛顶（42 格），黄线 = 眼睛，橙线 = 下巴 | **大小、姿势、位置照它**（B 版放大到 46 行） |
| `3_quality_bar.png` | main 里的malphite（47×47）、blitzcrank（44×46）、sett（42×26）、darius（42×36）、leona（41×44），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们** |
| `4_tfm2_style.png` | 团战经理2 原版的ogre（44×45）、berserker（39×34）、knight（36×36）、executioner（41×30）、demon（32×25） ×8 | **大块头、粗手臂、野兽的头怎么画**：大块平涂、少色、形状清楚 |
| `5_head_ref.png` | 原画的头，放大（1172×1080） | 牛角、鬃毛、眉骨、红眼睛、口鼻、鼻环 |
| `6_arms_ref.png` | 原画的手臂和腰，放大（986×590） | 两只宽镣铐、断链、大手、皮围裙 |
| `7_size_guide.png` | 原画直接缩到 42 行，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：A 42 格、B 46 格（鬃毛顶到蹄底），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **姿势照原画**：3/4 正面朝右、弓背前探、头低在右边、两手垂在身前、两只蹄子平落在地面线上；不能画成背影。
- **干净**：最多 26 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：皮肤暗部是深靛紫），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#140A20 outline (the only near-black); the VIOLET skin #2E1862 #4A2AA0 #6A44D2 #8E6AEA, the lavender chest and belly #A584E0 #C6AAF2; the scars #C0608C; the CYAN mane #1C66C4 #34A2EE #6AD6FF #CAF4FF; the ivory horns #8C7868 #CDB89E #F2E6D4; the iron shackles and chains #2A2730 #4A4652 #77727E with bronze edges #A58467; the leather loincloth #5A2E16 #8C5228 #BC7C42 with gold studs #D2A23C; the silver nose ring #8E96A2 #E2E6EC; the red eyes #FF2E2E; the hooves #3C1A1C #6E3226; the nails #8C8494。
- **蹄底以下什么都不能有**（游戏在脚下画血条）：蹄底在第 99 行，下面一格都不能有，铁链挂在上面。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`alistar_design_A.png` 和 `alistar_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`alistar/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Alistar, the Minotaur, a huge hulking bull-headed minotaur: deep VIOLET-PURPLE skin (lavender chest and belly, dark indigo shadows, a few pink scars on the shoulder and arm), massive rounded shoulders and arms much bigger than his short legs, a big hump of a back; a crest of spiky bright CYAN hair running from between the horns over the head and down the back of the neck and the hump; a bull's head carried low and forward in front of the hump, a broad snout with a darker muzzle, a silver NOSE RING, small glowing RED eyes under heavy brows, a short beard; two big curved IVORY HORNS sweeping out to the sides and curling forward, the image-left horn with a dark iron band near its tip; on each wrist a very WIDE broken iron SHACKLE (dark iron with a bronze rim and an engraved zig-zag line) with a broken chain hanging from it; huge hands with thick fingers and grey nails; a brown leather loincloth with a gold stud and a gold ring at the belt; short thick bull legs with shaggy purple fur round the ankles and dark cloven HOOVES. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size - use it for his SIZE, his POSE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user (the big ones: a rock giant, a steam golem, two brawlers, an armoured warrior) - match their pixel size and their crisp, clean look. FOURTH: official heroes of this game at 8x - an ogre, a berserker, a knight, an executioner, a demon - copy how a big heavy body, big arms and a beast's head are drawn at this size: big flat areas, few colours, bold readable shapes. FIFTH: the FIRST image's head, big - the horns, the cyan mane, the brow, the red eyes, the snout and the nose ring. SIXTH: the FIRST image's arms and waist, big - both wide shackles, the chains, the hands, the loincloth. SEVENTH: the FIRST image shrunk straight to game size - use it ONLY to see what fits where; it is blurry, do not copy its look.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only the number of squares the VERSION line at the end says from the top of the mane to the soles of the hooves. Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD and FOURTH images. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares, no more rows than the VERSION line says.
Pose: the FIRST image's pose and the SECOND image's shape: hunched forward in 3/4 FRONT view facing image right, the shoulders and the hump high, the head low and forward on the right with the horns spread, the face turned toward the viewer; both huge arms hanging forward, the near hand (image-right) in front of the body above the knee, the far hand (image-left) beside the far leg, the chains hanging; the legs a little apart and bent, both hooves flat on the ground line.
Game proportions: as the SECOND image - the head with the horns about a third of his height, the body wide and heavy, the arms and the shackles big, the legs short. The horns, the cyan mane, the nose ring, the red eyes and the shackles must read.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The violet skin in clear purple shades with lavender lit muscle tops (never one dark mass - near-black is only the outline); the muscles as a few big flat shapes, not many small ones. Drop what does not read at this size: the scars are 2-3 pink squares, the shackle's engraving one bronze line, the chains 3-4 squares of links, the fingers 2-3 square stubs with one grey nail square each, the mane 4-6 big cyan spikes.
Palette (from the FIRST image, adjust if needed): #140A20 outline (the only near-black); the VIOLET skin #2E1862 #4A2AA0 #6A44D2 #8E6AEA, the lavender chest and belly #A584E0 #C6AAF2; the scars #C0608C; the CYAN mane #1C66C4 #34A2EE #6AD6FF #CAF4FF; the ivory horns #8C7868 #CDB89E #F2E6D4; the iron shackles and chains #2A2730 #4A4652 #77727E with bronze edges #A58467; the leather loincloth #5A2E16 #8C5228 #BC7C42 with gold studs #D2A23C; the silver nose ring #8E96A2 #E2E6EC; the red eyes #FF2E2E; the hooves #3C1A1C #6E3226; the nails #8C8494.
Face (most important detail), as the FIFTH image: the head in 3/4 view facing right; a dark violet brow ridge; TWO red eyes (the near one 2 squares wide, the far one 1-2 squares, both on one row, a darker square under each), the snout below with a darker muzzle and two dark nostril squares, the SILVER NOSE RING 2-3 squares hanging under the snout's front, a short beard row under the chin; the horns ivory with one darker shade, leaving the head clear (one row of violet between a horn and an eye); the cyan mane rising between the horns.
Size and place: exactly where the SECOND image's grey shape stands (version B: the same shape scaled up to 46 rows, the soles and the middle column kept): the hooves' lowest row at y=792-799 (square row 99, the red line), the middle between the hooves on the middle column (x=512, the blue line), the mane's top on the green line, the eyes on the yellow line, the chin on the orange line (version A). Nothing below the hooves (the game draws the health bar right under them); the chains hang above that line.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: the number of rows from the mane's top to the soles (compare with the SECOND image); all squares 8x8 on one grid; at most 26 colours; one outline colour; two red eyes and the nose ring readable; both shackles, both hands and both hooves visible; nothing below the soles.
VERSION A (alistar_design_A.png): 42 squares from the mane's top to the soles, about 30 squares across, the head with the horns about 14 rows - the SECOND image's size.
VERSION B (alistar_design_B.png): 46 squares from the mane's top to the soles, about 33 squares across, the head with the horns about 15 rows - the SECOND image's shape a tenth bigger (as big as the base ogre); everything else as version A.
```

## 交回前自查

- [ ] A 42 格、B 46 格（最多 52）；蹄底在第 99 行、两蹄中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png`、`4_tfm2_style.png` 一个像素大小；紫色皮肤分出几档，不是一块深色；
- [ ] 两只红眼睛、银鼻环、象牙白牛角、青色鬃毛都看得清；角和眼睛之间有一行紫色；
- [ ] 两只宽镣铐、断链、两只手、两只蹄子都看得见；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、蹄底线、脸，只补缺的描边。
- A、B 两版和包里的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
