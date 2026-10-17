# 布兰德：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`brand/1_picture.png`，原画 A：微微弓身、膝盖弯着、两脚分开，两只火焰手张开放在身体两侧腰部高度，头顶燃着一簇火焰）在**游戏尺寸**重新画。
> - **大小**：从**光头顶到脚底 37 格**，头顶的火焰再往上窜 **5–6 格**（连火焰最高 43 格）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 光头顶，橙线 = 下巴（A 版），紫线 = 下巴（B 版）。大小、姿势和位置照 `brand/2_target_size.png`（原画直接缩到这个大小的灰剪影，浅灰的是头顶火焰）。
> - **宽度**：两只火焰手张开，整个造型**最宽不超过 34 格**（本包的泽拉斯 31 格、派克 48 格）。手可以比原画收近身体一点。
> - **头**：**版本 A** 光头顶到下巴 **12 格**（游戏 Q 版大头，脸约 7 格宽）；**版本 B** **10 格**（更接近原画，身体和腿更长）。两版身材都**瘦而结实、肌肉块分明**（参考 `3_quality_bar.png` 里的蛮王、派克），微微弓身、腿稍短。
> - **干净、不要细节（最重要）**：最多 28 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。**焦黑身体最容易糊成一团黑**：皮肤用几档**带紫的深灰**，肩、胸、手臂的肌肉块要有一格亮一点的灰紫亮面；**熔岩裂纹只画主要几道，每道 1 格宽的亮橙**，胸口正中那道最亮（亮黄）；不要满身细碎的裂纹（这个尺寸会变成噪点）。头顶火焰、两只火焰手是全身最亮的地方：外圈红橙、里面橙黄、芯是近白的亮黄，**火焰形状用 3–4 个大火舌**，不要碎。裤子：棕褐 2–3 档，裤脚 3–4 个大的锯齿布条；腿外侧的铜扣 = 2–3 个 2×2 的铜色方扣。
> - **脸**：光头圆顶（深灰紫，头顶一道亮橙裂纹接着火焰）；**两只发光的黄橙眼睛**（各 1–2 格亮黄，旁边一格深色眼窝），眼睛上面一道深色眉骨，表情凶；嘴可以是一格暗红或不画。眼睛不能被火焰或手挡住，**亮黄只用在眼睛、火焰芯和胸口裂纹上**。
> - **直接按游戏尺寸画**，不要先画大再缩小。`brand/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 37 格时，把最接近的那一张也交来（光头顶到脚底不要超过 44 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色，描边只用一种近黑色。交付到 `outputs/brand-model/`：`brand_design_A.png`、`brand_design_B.png`（1024×1024）和各自的原尺寸图 `brand_design_A_1x.png`、`brand_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来光头顶到脚底是多少格、火焰多高、头是多少格、多宽），最好再打成一个 zip（`brand_design_pack.zip`）。

## 附图（都在压缩包的 `brand/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：焦黑身体和熔岩裂纹、光头和头顶火焰、发光的眼睛、两只火焰手、棕褐破裤和腰带、腿外侧铜扣、光脚 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画缩到这个大小的灰剪影（浅灰 = 头顶火焰）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 光头顶（37 格），橙线 = 下巴（A 版），紫线 = 下巴（B 版） | **大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的泽拉斯（31×44）、派克（48×41）、蛮王（53×37）、赵信（65×42）、烬（29×41），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**；发光照泽拉斯，男性身材和赤裸上身照蛮王、派克 |
| `4_head.png` | 原画的头和火焰，放大 | 光头、头顶裂纹、发光的眼睛、凶的表情、火焰的形状 |
| `5_parts.png` | 原画的两只火焰手、腰带和铜扣、两条腿的破裤脚和光脚，放大 | 手、腰带、铜扣、裤脚、脚的形状 |
| `6_size_guide.png` | 原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟原版的待机（模型渲染） | 只看身体和裤子的结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：光头顶到脚底 37 格（火焰再高 5–6 格），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数；3/4 正面朝右；微微弓身、两脚分开；两只火焰手张开在身体两侧腰部高度（靠后的手在画面左边、靠前的手在画面右边），**两只手都在身体外面、不被身体挡住**，手臂从肩膀外角出来；前臂往手腕越来越红。
- **干净**：最多 28 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：皮肤是更深的灰紫、裤子是更深的棕），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。火焰和火焰手的外缘也要有描边（用深红 #6A1004 或近黑都可以，但要一致）。
- **色板**（从原画取，可以微调）：#0A0608 outline (the only near-black); charcoal skin #1E1A26 #2E2838 #423A50 #5C526C; lava cracks #A01808 #E04010 #FF8A1A; brightest crack, eye and flame core #FFD040 #FFF4B0; fire hands and head flames #8A1206 #D02A0A #FF6A14 #FFA428 #FFD040 #FFF4B0; forearm glow #6A1A20 #A0281C; trousers #3E3020 #6A5434 #92784C #B89C6C; belt and straps #2A1E16 #4A3424; copper buckles #7A4A1A #C08030 #F0C060; eyes #FFD040 #FFFFFF (eyes, flame cores and the chest crack only)。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`brand_design_A.png` 和 `brand_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`brand/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Brand, a man burned into living charcoal: a lean, sinewy, muscular body with CHARRED dark purple-grey skin crossed by GLOWING ORANGE LAVA CRACKS, the brightest one straight down the middle of the chest; a BALD head with a glowing crack over the crown and a crown of FLAMES rising from the top and back of the head like hair; two GLOWING YELLOW EYES under a dark brow, an angry face; the forearms turning red toward the wrists and two open HANDS made of FIRE (red-orange outside, yellow inside, near-white cores); bare chest; ragged TAN-BROWN trousers to the calves with big torn jagged hems, a thick dark belt, a few dark straps with COPPER buckles down the outside of his front leg; BARE charred feet with a crack or two. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the head flames in lighter grey - use it for his SIZE, his POSE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the first for glowing parts, the second and third for a bare-chested man's build). FOURTH: the FIRST image's head and flames, big - the bald head, the crown crack, the glowing eyes, the brow, the flame tongues. FIFTH: the FIRST image's two fire hands, the belt and copper buckles, the torn trouser hems and the bare feet, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in the same idle - ONLY for how the body and trousers are built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 37 squares from the top of his bald head to his soles, the flames rising 5-6 squares higher, and at most 34 squares across (the fire hands included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 37 squares to the crown, no more.
Pose: the FIRST image's pose and the SECOND image's shape: a slight menacing crouch in 3/4 FRONT view facing image right, knees a little bent, feet apart; both fire hands OPEN beside his body at waist height, fingers spread like claws - the BACK hand on image left, the FRONT hand on image right, the arms coming out of the outer corners of the shoulders; the head turned toward the viewer. Both hands are always outside the body, never hidden behind it.
Game proportions: the HEAD line at the end says how many squares from the top of the bald head to the chin; the rest shares the remaining squares. A lean, muscular man (like the second and third heroes of the THIRD image), the legs a little short; the glowing eyes, the head flames, the fire hands, the chest crack and the copper buckles drawn big enough to read.
Clean, not detailed (most important): at most 28 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The dark body must NOT become one black blob: the charcoal skin in purple-greys with a 1-square lighter plane on each big muscle (shoulders, chest, arms, calves); only the MAIN lava cracks, each a clean 1-square bright orange line, the chest crack the brightest (yellow); no small scattered cracks. The flames and fire hands are the brightest things: 3-4 big flame tongues each, red-orange edge, orange-yellow inside, a near-white yellow core. The trousers tan-brown with 3-4 big jagged rags at each hem; the copper buckles 2-3 squares of 2x2 copper on the front leg.
Palette (from the FIRST image, adjust if needed): #0A0608 outline (the only near-black); charcoal skin #1E1A26 #2E2838 #423A50 #5C526C; lava cracks #A01808 #E04010 #FF8A1A; brightest crack, eye and flame core #FFD040 #FFF4B0; fire hands and head flames #8A1206 #D02A0A #FF6A14 #FFA428 #FFD040 #FFF4B0; forearm glow #6A1A20 #A0281C; trousers #3E3020 #6A5434 #92784C #B89C6C; belt and straps #2A1E16 #4A3424; copper buckles #7A4A1A #C08030 #F0C060; eyes #FFD040 #FFFFFF (eyes, flame cores and the chest crack only).
Face (most important detail), as the FOURTH image: a round bald head in dark purple-grey with a 1-square lit edge and a bright crack running up into the flames; two GLOWING eyes, each 1-2 squares of bright yellow beside a dark socket square, a dark brow ridge above them, an angry look; the mouth one dark red square or none. Nothing covers the eyes.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the top of the bald head on the green line with the flames above it, the chin on the orange line (version A) or the purple line (version B). Nothing below the soles (the game draws the health bar right under them).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 37 squares from the top of the bald head to the soles, the flames 5-6 squares above (compare with the SECOND image); the head as tall as the HEAD line says; at most 34 squares wide; all squares 8x8 on one grid; at most 28 colours; one outline colour; both glowing eyes; the body readable (lit muscle planes, a few clean bright cracks, the bright chest crack); both fire hands outside the body; the head flames, the belt, the copper buckles, the torn hems and bare feet readable; nothing below the soles.
VERSION A (brand_design_A.png): HEAD 12 squares from the top of the bald head to the chin (a game-size chibi head, the face about 7 squares wide); 37 squares to the crown in all.
VERSION B (brand_design_B.png): HEAD 10 squares from the top of the bald head to the chin (closer to the picture), a longer body and legs; 37 squares to the crown in all; everything else as version A.
```

## 交回前自查

- [ ] 光头顶到脚底 37 格（最多 44），火焰再高 5–6 格；A 头 12 格、B 头 10 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 28 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；焦黑身体有灰紫亮面、不是一团黑；裂纹只有主要几道、胸口最亮；
- [ ] 两只发光的眼睛；头顶 3–4 个大火舌；两只火焰手张开在身体外面；腰带、铜扣、破裤脚、光脚；
- [ ] 最宽不超过 34 格；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
