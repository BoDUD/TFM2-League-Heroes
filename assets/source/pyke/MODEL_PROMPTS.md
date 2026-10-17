# 派克：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`pyke/1_picture.png`，原画 A：身子前倾半蹲、两脚分开，后手把鱼叉高高举在身侧、叉刃斜朝右上、金钩在左下，前手空着垂在前膝外面、手指张开像爪子）在**游戏尺寸**重新画。
> - **大小**：从**光头顶到脚底 40 格**。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 头顶，橙线 = 下巴（A 版），紫线 = 下巴（B 版）。大小、姿势和位置照 `pyke/2_target_size.png`（原画直接缩到这个大小的灰剪影，浅灰的是鱼叉）。
> - **鱼叉画短一点**：原画的鱼叉缩到这个大小有约 46 格长，每一帧都会很宽。**从金钩到叉尖约 34 格**（原画的四分之三左右），握的位置和方向不变（手还在头的左边、比头顶略低，叉刃往右上指过头顶、叉尖比头顶高 4–6 格，金钩在手的左下方）。整个造型连鱼叉**最宽不超过 56 格**（本包的赵信 65 格、蛮王 53 格）。
> - **头**：**版本 A** 头顶到下巴 **13 格**（游戏 Q 版大头，脸约 8 格宽）；**版本 B** **11 格**（更接近原画，脸约 7 格宽，身体和腿更长）。两版都是 40 格高，身材**高瘦、手臂长、手是细长的爪子**（参考 `3_quality_bar.png` 里的烬、凯隐、蛮王），半蹲、腿稍短。
> - **干净、不要细节（最重要）**：最多 28 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。深紫棕皮肤、深灰绿裤子、深蓝下摆容易糊成一片：**皮肤用暖紫棕加亮边，外套青蓝加一格金边，獠牙和叉刃是最亮的骨白，红面巾和发光的眼睛是亮点**。去掉这个尺寸看不清的细节：头顶的疤 = 1–2 格深红或去掉、前臂的纹身环 = 1 格暗一点的肤色、外套上的金色花纹 = 只留一格金边、腰带徽章 = 2–3 个 2×2 的金圆、护膝的金扣 = 1–2 格金。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，头顶到脚底只有 40 格**。
> - **脸**：光头（圆顶，暖紫棕，一格亮边）；**两只眼睛发淡青白光**（各 1–2 格亮青白，周围一圈暗色眼窝），眼睛上面一道深色眉骨；**下半张脸是红面巾**，从鼻子下面一直盖到下巴、尖尖地垂到胸口，上面 3–4 道 1 格宽的**骨白锯齿竖条纹**（像一排鲨鱼牙）。眼睛不能被挡住，**青白色只用在眼睛和鱼叉的宝石上**。
> - **直接按游戏尺寸画**，不要先画大再缩小。`pyke/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色，描边只用一种近黑色。交付到 `outputs/pyke-model/`：`pyke_design_A.png`、`pyke_design_B.png`（1024×1024）和各自的原尺寸图 `pyke_design_A_1x.png`、`pyke_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来头顶到脚底是多少格、头是多少格、连鱼叉多宽），最好再打成一个 zip（`pyke_design_pack.zip`）。

## 附图（都在压缩包的 `pyke/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：光头和疤、发光的眼睛、红面巾和骨白锯齿条纹、两肩一圈骨白獠牙、青蓝金边外套、背后深蓝长下摆、腰带金徽章和红腰布、深灰绿宽裤、前膝棕色大护膝、棕靴、高举的鱼叉、垂着的爪子手 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 40 行的灰剪影（浅灰 = 鱼叉，要画短一点）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 头顶（40 格），橙线 = 下巴（A 版），紫线 = 下巴（B 版） | **大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的烬（29×41）、凯隐（40×40）、赵信（65×42）、蛮王（53×37）、莎弥拉（32×40），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**；男性身材照烬、凯隐、蛮王 |
| `4_head.png` | 原画的头，放大 | 光头和疤、发光的眼睛、眉骨、红面巾的形状和锯齿条纹、獠牙从脸旁边绕过 |
| `5_parts.png` | 原画的叉刃和护手（青宝石）、红缠杆和金钩、腰带和金徽章、前腿的护膝和靴子、爪子手，放大 | 鱼叉、腰带、护膝、靴子、手的形状 |
| `6_size_guide.png` | 原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟原版的待机（模型渲染） | 只看装备的结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：头顶到脚底 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材高瘦；3/4 正面朝右；前倾半蹲、两脚分开；后手（画面左边）把鱼叉高举在头的左边，手臂从后肩伸出去，**手和鱼叉都在身体外面、不被身体挡住**；前手（画面右边）空着垂在前膝外面、三四根细长的爪子指头张开；两肩一圈骨白獠牙，有一根大獠牙斜着从后肩上方伸出来；背后的深蓝下摆垂到小腿。
- **干净**：最多 28 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：皮肤是更深的紫棕、外套是更深的青蓝），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0A0608 outline (the only near-black); skin #4A2628 #6E3A3C #8E5452 #B07870; teal coat #142A34 #1F4E60 #3A7E92; gold trim, medallions, guard and hook #6A3A10 #B86A28 #E09A40 #F6D48C; bone spikes, mask stripes and harpoon blade #8E7A54 #C8B484 #E8D8AA #FFF8E0; red mask, waist cloth and shaft wrap #5A0A14 #9A1020 #D81A26; trousers #2A2822 #4A4536 #6A6450; navy coat tail #0E1322 #1C2844 #32466C; leather knee guard, belt and boots #3A1A10 #6A3018 #9E5A34; eyes #A8F4F0 #FFFFFF; gem #30C8C0 (eyes and gem only)。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，下摆和金钩也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`pyke_design_A.png` 和 `pyke_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`pyke/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Pyke, a drowned harpooner, tall and lean with dark purple-brown skin: a BALD round head with a scar, two eyes GLOWING PALE CYAN-WHITE under a dark brow, the lower face covered by a RED CLOTH MASK with jagged BONE-WHITE vertical stripes like shark teeth, its point hanging to the chest; a ring of huge BONE-WHITE SPIKES / shark teeth over both shoulders and round the neck, one big spike sticking up diagonally behind his back shoulder; a short TEAL-BLUE coat with GOLD trim, open at the chest; a LONG DARK NAVY coat tail hanging behind to the calves; a brown belt with round GOLD MEDALLIONS and a red waist cloth; baggy dark grey-green trousers; a big brown leather KNEE GUARD with a gold buckle on the front knee; brown boots; long thin CLAW-LIKE fingers; and a HARPOON: a wide BONE-WHITE barbed blade, a bronze-gold guard with a CYAN GEM, a RED-wrapped shaft and a curved GOLD HOOK at the butt. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the harpoon in lighter grey - use it for his SIZE, his POSE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the first, second and fourth for a man's build). FOURTH: the FIRST image's head, big - the bald head and scar, the glowing eyes, the brow, the red mask and its white stripes. FIFTH: the FIRST image's harpoon blade and guard with the gem, the red shaft and gold hook, the belt and medallions, the front knee guard and boot, and the claw hand, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in the same idle - ONLY for how the costume is built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of his head to his soles and at most 56 squares across (the harpoon included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: crouched forward in 3/4 FRONT view facing image right, knees bent, feet apart; the BACK hand (image left) holds the harpoon RAISED beside his head on image left, the arm reaching out from the back shoulder, the hand a little lower than the top of his head; the barbed blade points up and to image right over his head, its point 4-6 squares higher than the top of his head; the gold hook down-left of the hand; the FRONT hand (image right) empty, hanging low outside the front knee, the claw fingers spread; the coat tail hanging behind; the head turned toward the viewer. The hand and the harpoon are never hidden behind the body.
The harpoon SHORTER than in the FIRST image: about 34 squares from the gold hook to the point (the grey shape's lighter harpoon is longer - shorten both ends, keep the hand and the direction): the blade about 14 squares long and 4 wide with 3-4 barbs, the guard 3 squares with a 1-square cyan gem, the red shaft 2 squares thick, the hook a 4-5 square gold curl.
Game proportions: the HEAD line at the end says how many squares from the top of the head to the chin; the rest shares the remaining squares. A lean, wiry man with long arms (like the first, second and fourth heroes of the THIRD image), the legs a little short; the glowing eyes, the red mask and its stripes, the bone spikes, the gold medallions, the knee guard and the harpoon's white blade drawn big enough to read.
Clean, not detailed (most important): at most 28 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the purple-brown skin with lit edges, the teal coat with a 1-square gold edge, the bright bone-white spikes and blade, the red mask, the grey-green trousers, the navy coat tail, the brown leather. Drop what does not read at this size: the scalp scar 1-2 dark red squares or nothing, the forearm tattoo bands 1 darker skin square, the coat's gold pattern only a 1-square gold edge, the belt medallions 2-3 gold 2x2 rounds, the knee guard buckle 1-2 gold squares.
Palette (from the FIRST image, adjust if needed): #0A0608 outline (the only near-black); skin #4A2628 #6E3A3C #8E5452 #B07870; teal coat #142A34 #1F4E60 #3A7E92; gold trim, medallions, guard and hook #6A3A10 #B86A28 #E09A40 #F6D48C; bone spikes, mask stripes and harpoon blade #8E7A54 #C8B484 #E8D8AA #FFF8E0; red mask, waist cloth and shaft wrap #5A0A14 #9A1020 #D81A26; trousers #2A2822 #4A4536 #6A6450; navy coat tail #0E1322 #1C2844 #32466C; leather knee guard, belt and boots #3A1A10 #6A3018 #9E5A34; eyes #A8F4F0 #FFFFFF; gem #30C8C0 (eyes and gem only).
Face (most important detail), as the FOURTH image: a round bald head with a 1-square lit edge; two GLOWING eyes, each 1-2 squares of pale cyan-white in a small dark socket, a dark brow ridge above them; the RED MASK from under the nose down over the chin to a point on the chest, with 3-4 one-square BONE-WHITE vertical jagged stripes. Nothing covers the eyes. The cyan-white is used only by the eyes and the harpoon's gem.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the top of the head on the green line, the chin on the orange line (version A) or the purple line (version B). Nothing below the soles (the game draws the health bar right under them): the coat tail and the hook stay above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the top of the head to the soles (compare with the SECOND image); the head as tall as the HEAD line says; the harpoon about 34 squares and the whole sprite at most 56 squares wide; all squares 8x8 on one grid; at most 28 colours; one outline colour; both glowing eyes and the red mask with its white stripes; the bone spikes, the teal coat, the gold medallions, the knee guard, the claw hand and the harpoon with its gem and hook all readable; nothing below the soles.
VERSION A (pyke_design_A.png): HEAD 13 squares from the top of the head to the chin (a game-size chibi head, the face about 8 squares wide); 40 squares in all.
VERSION B (pyke_design_B.png): HEAD 11 squares from the top of the head to the chin (closer to the picture, the face about 7 squares wide), a longer body and legs; 40 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 头顶到脚底 40 格（最多 48），A 头 13 格、B 头 11 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 28 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；紫棕皮肤、青蓝外套、骨白獠牙、红面巾、灰绿裤子、深蓝下摆、棕皮护膝分得开；
- [ ] 两只发光的眼睛 + 红面巾上的白锯齿条纹；两肩獠牙；腰带金徽章；前膝大护膝；
- [ ] 鱼叉约 34 格、高举在头的左边，叉尖比头顶高 4–6 格，手和鱼叉没被身体挡住；整个造型不超过 56 格宽；前手爪子垂在前膝外；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
