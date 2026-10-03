# 烬：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`jhin/1_jhin_source.png`，你上一轮画的：英雄联盟的待机，金色机械手搭在腰间的手杖枪上，手炮「低语」垂在近侧手里）在**游戏尺寸**重新画。
> - **大小**：从**头套顶到脚底 41 格**（和凯特琳差不多高；包里的修长大人英雄 40–46 格，`jhin/3_quality_bar.png`）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线），绿线 = 头套顶（41 格），橙线 = 面具下巴；大小和位置看 `jhin/2_target_size_A.png` / `_B.png`（他自己原画按游戏比例拼的灰色剪影）。
> - **头要比原画大（游戏比例）**：原画的头只占身高约 1/7，游戏里的英雄头约占 1/3。两版只差头的大小：
>   - **版本 A**：头套顶到面具下巴 **13 格**（和包里的英雄一样的 Q 版比例），面具约 9 格宽；
>   - **版本 B**：头 **11 格**（更修长，接近原画），面具约 8 格宽；
>   - 身体其余部分（立领、披风、长腿）占剩下的格数，整体保持**又高又瘦**：披风下窄肩、细长腿。
> - **干净、不要细节（最重要）**：最多 24 色，每种材质 2–3 档平涂加一点高光，大块纯色，去掉这个尺寸看不清的细节（披风漩涡 2–3 条 1 格的棕线，金扣 = 金框里一格绿，枪上花饰几格金，膝关节 3×3 的金圆盘）。以前乐芙兰、卡莎的第一稿都画成了两倍大，因为细节越多，生图模型画的方块越小、整个人越大——**这次请画大方块，头套顶到脚底只有 41 格**。
> - **两把枪是标志道具，必须清楚、笔直、完整**：金拳头搭在手杖枪的金色顶上，手杖枪笔直竖在远侧腰间（2 格宽的深铁灰杆、一段青绿布缠、几行金环），下端在小腿中间、挂着品红流苏（不低于脚底）；近侧肤色手臂（紫护腕）握着「低语」的象牙白握把，枪口朝下贴着近侧大腿、到膝盖高。
> - **脸**：白瓷面具是全身最亮的地方；两只眼睛在同一行，各 2 格宽 = 1 格近黑眼缝 + 1 格亮粉紫虹膜（`#FF6EB4`，只用在眼睛上），每只眼睛上面一格浅蓝阴影当眉骨；一条浅蓝的鼻线，下面 2 格中蓝的刻出来的嘴（不要红色）；面具顶中间一格深紫的美人尖；深紫头套包住头顶和后脑；品红立领在下巴两边竖起来。
> - **直接按游戏尺寸画**，不要先画大再缩小（缩小会把细节弄碎）。`jhin/7_size_guide_A.png` 是原画按游戏比例直接缩到这个大小的样子，只用来看能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - **画不到正好 41 格时，把最接近的那一张也交来（头套顶到脚底不要超过 48 格）**，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 24 色，描边只用一种近黑色。交付 `jhin_design_A.png`、`jhin_design_B.png`（1024×1024）和各自的原尺寸图 `jhin_design_A_1x.png`、`jhin_design_B_1x.png`，生图原稿，`HANDOFF.md`（**最后写**，写明每张读回来头套顶到脚底是多少格、头是多少格）和色板，最好打成一个 zip（`jhin_design_pack.zip`）。

## 附图（都在压缩包的 `jhin/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_jhin_source.png` / `1_jhin_source_white.png` | 用户选的原画 A（透明底 / 白底） | **长相**：白瓷面具、深紫头套、品红立领、绿宝石金扣、米白披风、紫红衬里、金色机械臂、手杖枪、手炮「低语」、紫裤子、金色腿撑、颜色和姿势 |
| `2_target_size_A.png` / `2_target_size_B.png` | 1024×1024 画布（128×128 格 ×8），原画按游戏比例拼的灰色剪影（A 头 13 格 / B 头 11 格）= 大小和位置；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 头套顶（41 格），橙线 = 面具下巴 | **大小和位置照它** |
| `3_quality_bar.png` | main 里的vayne（40）、caitlyn（41）、kaisa（44）、lucian（46）、camille（46），游戏里现在的样子 ×8，同一条脚底线 | **像素大小、干净程度和身高照它们**（烬和凯特琳差不多高） |
| `4_tfm2_style.png` | 团战经理2 原版的枪手、赌徒、杀手、士兵、弓箭手 ×8 | 原版的像素画法：大块平涂、少色、形状清楚 |
| `5_face_ref.png` | 原画 A 的头、立领和金扣，放大（680×660） | 面具、眼睛、头套、立领 |
| `6_guns_ref.png` | 原画 A 的两把枪，放大（900×1030）：金拳头搭着的手杖枪、近侧手里的「低语」 | 两把枪的样子 |
| `7_size_guide_A.png` / `7_size_guide_B.png` | 原画按游戏比例直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：头套顶到脚底 41 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身体又高又瘦；3/4 正面朝右；金手搭着手杖枪、「低语」垂在近侧大腿边。
- **干净**：最多 24 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：头套和裤子是深紫，衬里是深红，金是暖棕），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0E0814 outline (the only near-black); porcelain mask #F4F8FA #BCCEDC #74859E; hood #22162F #3A2052 (the trousers share #3A2052, then #5E2E7A); crimson collar, cloak lining and tassel #5E0A2C #A01248 #D42A62; ivory cape, its swirls and Whisper's grip #F2EEDC #D2CAB0 #A89C7C; gold arm, leg braces, rings, brooch rim and gun ornaments #5A2E10 #A0581A #D8902C #FFD878; skin #A86450 #E0A07E; gunmetal (Whisper's body, the cane's shaft) #262A3A #4A5470; teal cane wrap #2E9696; brooch gem #22B28A; eyes #FF6EB4 (the eyes only)。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，流苏和枪口也不能低于脚底。背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`jhin_design_A.png` 和 `jhin_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画；第二张图 A 版用 `2_target_size_A.png`、B 版用 `2_target_size_B.png`，第七张同理）

附图：`jhin/` 里的 1–7 号图，按顺序。

```text
Seven attached images. FIRST: the approved illustration of this character - copy his look: a tall, slender theatrical gunman; his whole face hidden by a white PORCELAIN MASK with cool pale-blue shading (a widow's-peak notch at the top middle, a heavy brow, two narrow eyes with small glowing pink-magenta irises, a long nose, a carved frowning mouth, a pointed chin); a tight DARK PURPLE HOOD over the top and back of his head; a high CRIMSON COLLAR up to the jaw; a big IVORY CAPE with faint tan swirl patterns over his FAR shoulder and down his chest to the hips, a gold-rimmed GREEN brooch at the throat; a crimson cloak lining hanging behind him to the knees; a GOLD ARMOURED far arm bent at the elbow, the gold fist resting on the top of his CANE-RIFLE, which hangs straight down at his far hip (dark gunmetal shaft, a TEAL wrapped grip, GOLD rings, a small CRIMSON TASSEL hanging from its lower end); his near arm bare (tan skin) with a dark purple wrist guard, hanging down and holding WHISPER, an ornate hand cannon (a dark gunmetal body, gold scroll ornaments, a long curved IVORY grip), pointing at the ground beside his near thigh; purple trousers; from the knees down GOLD-BRONZE leg braces with round knee joints and clawed metal shoes. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - his silhouette at game size with a game-size (bigger) head - use it for his SIZE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user (five slim adults, 40-46 squares tall) - match their pixel size and their crisp, clean look; he is about as tall as the second one (41 squares). FOURTH: official heroes of this game at 8x (gunners and marksmen) - the pixel size and cleanliness to match: big flat areas, few colours, bold readable shapes. FIFTH: the FIRST image's head, big - the mask, the hood, the eyes, the collar and the brooch to copy. SIXTH: the FIRST image's two guns, big - the cane-rifle with the gold fist on it, and Whisper in the near hand. SEVENTH: the SECOND image's grey shape with the colours of the FIRST image, shrunk straight to game size - use it ONLY to see what fits where; it is blurry, do not copy its look.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 41 squares from the top of the hood to his soles. Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD and FOURTH images. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 41 squares from the hood's top to the soles, no more.
Game proportions, NOT the illustration's: the masked head is BIGGER than in the FIRST image - the HEAD line at the end says how many squares from the hood's top to the mask's chin; the rest (collar, cape, legs) shares the remaining squares. Keep him slim and tall in that body: narrow shoulders under the cape, long thin legs, the guns a little oversized so they read.
Clean, not detailed (most important): at most 24 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Drop what does not read at this size: the cape's swirls are two or three 1-square tan lines, the brooch one green square in a gold rim, Whisper's ornaments a few gold squares, the cane's rings single gold rows, the leg braces' knees round 3x3 gold discs.
Palette (from the FIRST image, adjust if needed): #0E0814 outline (the only near-black); porcelain mask #F4F8FA #BCCEDC #74859E; hood #22162F #3A2052 (the trousers share #3A2052, then #5E2E7A); crimson collar, cloak lining and tassel #5E0A2C #A01248 #D42A62; ivory cape, its swirls and Whisper's grip #F2EEDC #D2CAB0 #A89C7C; gold arm, leg braces, rings, brooch rim and gun ornaments #5A2E10 #A0581A #D8902C #FFD878; skin #A86450 #E0A07E; gunmetal (Whisper's body, the cane's shaft) #262A3A #4A5470; teal cane wrap #2E9696; brooch gem #22B28A; eyes #FF6EB4 (the eyes only).
Face (most important detail), as the FIFTH image: the mask is the lightest area of the sprite; both eyes on the SAME row inside the mask, each 2 squares wide: a near-black slit square beside one bright pink-magenta iris square (#FF6EB4), with a pale-blue shadow square over each eye for the heavy brow; the near eye (image left) on the mask's near side, the far eye toward the far edge; between and below them the mask's light shades, a long nose as one pale-blue shade line, a carved mouth of 2 mid-blue squares under it (no red); the widow's-peak notch is one dark-purple square at the mask's top middle; the dark purple hood frames the mask on the top and the back of the head; the crimson collar rises on both sides of the chin. The pink-magenta is used for nothing but the eyes.
Hands and guns: the gold far arm bent with its elbow out to the left, the forearm 2-3 squares thick, ending in a gold fist ON the cane's gold top; the cane straight and vertical (a 2-square gunmetal shaft with one teal section and single gold ring rows), its lower end at mid-shin with the crimson tassel hanging from it, above the soles; the near arm 2 squares thick in tan skin with a purple wrist guard, the hand holding Whisper's ivory grip, the gun pointing down along the near thigh with its muzzle at knee height; both guns straight, whole and clearly seen; no 1-pixel black sticks, no floating hands.
Pose, size and place: the pose of the FIRST image, 3/4 FRONT view facing right, exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the point between his feet on the middle column (x=512, the blue line); the green line of the SECOND image is the hood's top (41 squares over the soles), the orange line the mask's chin. Nothing below the soles (the game draws the health bar right under them).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: 41 squares from the hood's top to the soles (compare with the SECOND image); the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 24 colours; one outline colour; both eyes visible, level, the magenta only in the eyes; the gold fist on the cane and Whisper in the near hand, both guns straight and whole; nothing below the soles.
VERSION A (jhin_design_A.png): HEAD 13 squares from the hood's top to the mask's chin (like the game's heroes in the THIRD image); the mask about 9 squares wide; 41 squares in all.
VERSION B (jhin_design_B.png): HEAD 11 squares from the hood's top to the mask's chin (a little more slender, closer to the FIRST image); the mask about 8 squares wide; 41 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 头套顶到脚底 41 格（最多 48），A 头 13 格、B 头 11 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 24 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png`、`4_tfm2_style.png` 一个像素大小；
- [ ] 两只眼睛同一行、粉紫虹膜看得清、粉紫只在眼睛上；面具是最亮的地方；
- [ ] 金拳头搭在手杖枪顶上，手杖枪笔直、流苏在脚底以上；「低语」在近侧手里、笔直完整；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和凯特琳、薇恩、卢锡安放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
