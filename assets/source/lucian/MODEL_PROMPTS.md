# 圣枪游侠 卢锡安：模型（给 Codex 的提示词）

> **卢锡安的模型、动作帧和技能特效都由 Codex 画**，Claude 只做参考图、写提示词、导入。这个压缩包里是全部参考：
> - **第一轮**：造型图 A / B / C（第 1 节，三个方案只有比例不同）交回给用户挑；**同一轮顺便画 14 张特效**（`PROMPTS.md`，特效不依赖造型）。
> - **第二轮**：用户选定造型后，同一批画 10 张动作图（第 2–11 节）。
> - 参考全部取自英雄联盟原版：同一个镜头（3/4 朝右、俯视 25°）渲染的原版模型和原版动作，每个动作的帧数、每帧时长和出手时刻都已经和技能数据对好（普攻第 3 帧开枪、圣光银弹第 3、5 帧各开一枪、Q 第 4 帧放光束、E+W 第 6 帧射出烈弹、R 每两帧开一枪）。
> - 生图原稿通常不在严格网格上（方块 7.4–8.6 px、脸会变窄）。交回前请整理成：每个像素一个严格对齐的 8×8 纯色块，透明度只有全透明和不透明，每帧的脚底踩在参考线上，每帧的头和选定造型图的头一样大。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、有没有没做到的地方）、`manifest.json`（文件名、尺寸、每帧的格子矩形、站位点 pivot、不透明区域 bbox、眼睛颜色的中心）和 `generation_prompts.json`。

## 附图（都在压缩包里；英雄联盟渲染图、原版英雄对照图只在本地用，不要提交）

| 文件 | 内容 | 用在 |
|---|---|---|
| `lol_ref_model.png` | 英雄联盟原版模型（原比例），和我们同一个镜头：左边全身战斗待机（双枪举在头两边），右边头部特写 | 造型图（长相以它为准） |
| `lol_pose_design.png` | 同一个待机姿势按游戏的 Q 版比例（头放大、腿缩短）渲染，放大 8 倍，1024×1024 | 造型图（比例和姿势） |
| `lucian_now_design.png` | 同一个姿势的游戏尺寸（每个游戏像素是一个 8×8 方块，1024×1024）：只是参考大小和站位，是渲染的平均色，不是要的画法 | 造型图（大小和站位） |
| `tfm2_style_ref_gunner.png` | 团战经理2 原版英雄（用枪的、用弩的；上排待机、下排攻击），放大 8 倍：像素大小和干净程度照它们 | 造型图、动作图 |
| `lucian_now_<动作>.png` | 每个动作的游戏尺寸参考条，放大 8 倍，按格子排好（每格 96×96 个方块 = 768×768 px） | 各自的动作图（帧数、每帧的时机和站位） |
| `lol_pose_<动作>.png` | 英雄联盟原版同一帧的动作高清渲染，和上一张同样的格子、同样的位置 | 各自的动作图（动作照它） |
| `lucian_guide_<动作>.png` | 每帧的站位点（蓝十字）和脚底线（红线），红线以下的淡红区不能有任何像素 | 各自的动作图（对位用，不要画进图里） |
| `lucian_cells.json` | 每帧的站位点（格子里第几列、第几行，单位是方块）和帧时长 | 整理对位 |
| `lol_fx_ref.png`、`PROMPTS.md` | 英雄联盟卢锡安自己的特效贴图；14 张特效的提示词 | 特效 |

## 所有图的规则

- **像素尺寸（最重要）**：他在游戏里从头顶到脚底约 34 个像素（战斗待机时举在头两边的枪管再高出约 5 格），按真正的低分辨率像素画来画，再整体放大 8 倍输出：每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净，不要细节**：整个精灵最多 24 种颜色；每种材质 2–3 个平涂色阶（亮、中、暗）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；轮廓 1 个方块宽的近黑色描边，内部深色线条越少越好。
- **脚底线以下什么都不能有**：鞋底最低一行正好是每帧站位点下方第 11 行（`lucian_cells.json` 里每帧的 pivot 行 + 11；参考图的红线在它下面一行），红线以下不能有任何像素——枪、外套下摆、影子都不行，游戏在脚下画血条，下面的东西会被盖住。只有死亡倒地的帧可以低于红线，最多 2 格。
- **脸**：三格高的原版英雄眼睛（和 `tfm2_style_ref_gunner.png` 里的一样：近处的眼睛 2 格宽、远处的 1 格宽，中间隔一格皮肤，一行睫毛/眉，下面是眼白、虹膜和瞳孔），眼睛下面两行脸，一格深红色的嘴（可以不画嘴）。**每一帧的眼睛都和造型图完全一样**（大小、位置、相对关系不变），不能连成一条横杠、竖线或糊成一团；**眼睛用的颜色只用在眼睛上**（枪、衣服、特效都不用这个颜色）。
- **头部每帧照造型图复制**：轮廓、头发、脸都和造型图一样，只跟着动作整体移动或倾斜，不重新画；移动的每一帧，头相对站位点的横向位置固定，只让腿和手臂动。
- **手臂和枪从肩膀、胸口伸出**，不挡脸，不从脸上伸出来；两把枪各是一个清楚的形状（至少 5×3 格），和手臂分得开。
- 3/4 正面朝右（脸朝右边的敌人），不画背影；侧身开枪的帧也要看得到脸。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号，也不要把参考图的十字和红线画进去。
- 如果模型不肯画有名字的角色，把 "Lucian" / "League of Legends" 删掉，只保留外观描述。

## 他的样子（照 `lol_ref_model.png`）

- **头**：深棕色皮肤；深褐近黑的头发编成几股往后梳的短脏辫，在脑后扎成一小撮；两侧剃短，耳朵上方剃出一道线；浓黑的眉毛，绿色的眼睛，脸型硬朗，下巴上一小撮短胡子（游戏尺寸下如果像嘴，就省掉）。
- **外套**：白色（浅灰白）高领长外套，下摆到膝盖、在身后分开飘起；领口和前襟金色镶边，胸口一块深灰色的护胸，上面几道 V 形纹；一边肩膀一块金色肩甲；外套内侧和下摆的阴影带一点淡紫。
- **腰和腿**：深色腰带配金色扣，腰前垂一片暗红色的布；深炭灰色长裤，膝盖和小腿有浅灰色的护甲片，深色靴子；黑色手套。
- **双枪**：两把圣物手枪，枪身是深灰色金属，枪管长，上面有金色的花纹，**枪口是一块发光的青色晶体**（最亮的颜色），是他最好认的地方。
- **颜色**（照原版取的，可按渲染图微调）：皮肤 `#7A4A36` `#5A3428` `#3A221C`；头发 `#3A2A26` `#1E1618`；外套 `#F0F2F2` `#C8CED4` `#9098A4`，外套阴影的淡紫 `#8C7C9C`；金 `#F0C860` `#B88C3A` `#6E5424`；护胸和枪身 `#5A5E68` `#3A3C46`；裤子和靴子 `#3C3644` `#26222C`；暗红布 `#7A2A36` `#46161E`；枪口晶体 `#B8FAFF` `#48D0EC`；眼睛 `#1A1418` `#4E9A5C` `#F4F2EA`；描边 `#140E12`。

---

## 1. 造型图（第一轮）：`lucian_design_A.png`、`lucian_design_B.png`、`lucian_design_C.png`

三个方案的长相、颜色、姿势都一样，只有比例不同，交回给用户挑：

| 方案 | 比例 |
|---|---|
| A | 接近原版：头约占身高 1/4 多一点（约 27%），腿长 |
| B | 介于中间：头约占身高 1/3 弱（约 32%，和本包伊泽瑞尔一样），附图 `lol_pose_design.png` 就是这个比例 |
| C | 团战经理2 的 Q 版：头约占身高 1/3 强（约 36%，像原版英雄），腿短一些 |

每个方案附三张图：`lucian_now_design.png`、`tfm2_style_ref_gunner.png`、`lol_ref_model.png`（B 另附 `lol_pose_design.png`）。

```text
Three attached images. FIRST: a game-size reference of this character's pose at 8x (every game pixel an 8x8 block) - use it ONLY for the size and the place in the canvas; it is a blurry average of a 3D render, not the style to copy. SECOND: official heroes of the game Teamfight Manager 2 at 8x - match this pixel size and cleanliness: big flat areas, few colors, bold readable shapes, three-row eyes. THIRD: the original 3D model of the character seen from the same camera - copy its look: the shapes, materials and colors.
Task: draw the character as clean hand-made pixel art: a sprite about 34 pixels tall from the top of the head to the soles (the raised pistols stand about 5 more above the head), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency.
Lucian from League of Legends (default look): a gunslinger priest with dark brown skin. Dark hair in short dreadlocks swept back and tied at the back of the head, the sides shaved short with one carved line above the ear, heavy black eyebrows, green eyes, a strong face with a short dark goatee on the chin (leave it out if at this size it reads as a mouth). A white high-collared long coat reaching his knees and parting behind him, gold trim on the collar and the front edges, a dark grey chest plate with a few V-shaped ridges, one gold shoulder plate, faint violet in the coat's shadows. A dark belt with a gold buckle and a dark red cloth hanging at the front, charcoal trousers with light grey armor plates on the knees and shins, dark boots, black gloves. In each hand a relic pistol: a long dark grey metal gun with gold filigree and a glowing CYAN CRYSTAL at the muzzle - his most recognizable feature.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades; palette: skin #7A4A36 #5A3428 #3A221C, hair #3A2A26 #1E1618, coat #F0F2F2 #C8CED4 #9098A4, coat shadow violet #8C7C9C, gold #F0C860 #B88C3A #6E5424, chest plate and gun metal #5A5E68 #3A3C46, trousers and boots #3C3644 #26222C, dark red cloth #7A2A36 #46161E, crystal #B8FAFF #48D0EC, eyes #1A1418 #4E9A5C #F4F2EA, outline #140E12. Big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Drop details that do not read at this size. Use the eye colors ONLY in the eyes.
Proportions: [A: close to the original model - the head about 27% of his height, long legs.] [B: between - the head about 32% of his height (like the FOURTH image, if attached).] [C: chibi like the game's heroes - the head about 36% of his height, shorter legs.]
Face: readable at game size - three-row eyes like the SECOND image (the near eye 2 squares wide, the far eye 1 square wide, one square of skin between them; a row of brow/lashes, then the eye whites with the green iris and a dark pupil), two rows of face under the eyes, optionally one dark red mouth square; the hair never covers the eyes.
Pose, size and place: his combat stance - standing with his feet apart, both pistols raised beside his head, muzzles pointing up, the crystals glowing; the soles on the line 28 squares (224 px) above the bottom of the image; the character horizontally centered. 3/4 FRONT view facing right.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 34 squares from the top of the head to the soles, all squares 8x8 on one grid, at most 24 colors, both eyes visible, both pistols with their cyan crystals easy to read, nothing below the soles.
```

中括号里是三个方案各自的一段，每张只保留自己那一段。

## 选定：方案 B + 重画的头 U3

Codex 第一轮交回 A / B / C 三张（`lucian_round1.zip`，严格 8×8 方块、22–23 色）。选 **B**：头约占身高 1/3，比例和动作参考条一致（参考条就是按这个比例渲染的）；A 头小腿长，C 脸上有金色杂块、身体杂色多。三张的脸都有同一个问题：眼睛连成一条白绿横杠，脸像戴了面具。Claude 照英雄联盟原版的头在同一比例下逐格描出形状，再画五官，给用户看了三个脸，用户选了 **U3**：
- 头顶往后梳的深色头发（带发缝），左侧剃短的一块和耳朵，远眼贴着脸的右缘，鼻尖凸出一格；
- 浓眉（外端高、内端低，皱着眉）；
- 原版英雄的三行眼睛：近眼 2 格（上一行眉毛、中间一行"眼白 + 黑瞳孔"、下一行"眼白 + 绿虹膜"），远眼 1 格（黑、绿）；没有嘴。

改好的造型图就是附件 `lucian_native.png`（1024×1024，8×8 方块，脚底在第 99 行、y=792–799，26 色：Codex 的 22 色加上脸的提亮肤色和发缝的高光）。第二轮的动作图一起注意：

1. **头部每帧照 `lucian_native.png` 复制**：头发的形状和发缝、剃短的侧边、耳朵、浓眉、三行眼睛、鼻尖都和造型图一样，只随动作整体移动或倾斜，不重新画；眼睛的绿色 `#4E9A5C` 只用在眼睛上。
2. **身体照 B**：白色高领长外套（金边、深灰护胸、一边金色肩甲）、深色裤子和护腿、腰前暗红布、双枪（深灰枪身、枪口青色晶体）；身上不要零散的杂色点。
3. **透体圣光第 4、5 帧**：两把枪平举在腰带的高度往前推（游戏里的光束从他腰部的高度射出，枪口太高会和光束对不上）。
4. 其余照下面第 2–11 节的说明。

---

## 2–11. 动作图（第二轮，用户选定造型后同一批画）

每张附三张图：第一张是**选定的造型图**（交回时改名为 `lucian_native.png`），第二张是对应的 `lucian_now_<动作>.png`，第三张是对应的 `lol_pose_<动作>.png`；对位用 `lucian_guide_<动作>.png` 和 `lucian_cells.json`。输出文件名 `lucian_<动作>.png`，排版和第二张附图完全一样。

10 张的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

```text
Three attached images. FIRST: the approved clean pixel-art design of this character at 8x (every pixel an 8x8 block) - copy his colors, shapes, head, coat, pistols and pixel style exactly, the head the same size in every frame. SECOND: a game-size reference of the animation at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the shot, the recoil, the recovery) and where he stands in his cell, but NOT its look (it is a blurry average of a 3D render). THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
Task: draw every frame as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size (about 34 pixels from the top of the head to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): only the 26 colors of the FIRST image, no new ones; big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette.
Head and face: copy the head of the FIRST image into every frame - the same outline, hair and face, only moved or tilted with the body, never redrawn; the eyes exactly as in the FIRST image in every frame where the face shows (never merged into a bar or a line), and the eye colors used nowhere else. Arms and pistols come from the shoulders and the chest and never cover the face. Both pistols stay clear shapes with their cyan crystals. 3/4 FRONT view facing right, never his back.
Feet line: in every cell the lowest row of his soles is the row 11 squares below that frame's standing point (lucian_cells.json), the same ground in every frame; NOTHING below it - not a pistol, not the coat - because the game draws the health bar there. His place across the cell follows the SECOND image.
[animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size]; frame N in the same cell as in the SECOND image. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
```

| # | 文件 | 帧 × 毫秒 | 排版 | `[animation]` |
|---:|---|---|---|---|
| 2 | `lucian_idle.png` | 6 × 200 | 3 列 × 2 行，2304×1536 | `Animation: IDLE, 6 frames: his combat stance exactly as in the FIRST image - feet apart, both pistols raised beside his head, muzzles up, crystals glowing. Draw all 6 frames the same (the game adds the breathing).` |
| 3 | `lucian_run.png` | 8 × 117 | 4 列 × 2 行，3072×1536 | `Animation: MOVE loop, 8 frames, one second like the original: his combat run from the THIRD image - a running stride with both pistols held forward at chest height, the coat tails flying behind; frames 1-4 one stride, 5-8 the other; the head stays in the same place across the cell in every frame (at most 1 square up or down), facing right like in the FIRST image; the feet touch the ground line in the stride frames.` |
| 4 | `lucian_attack.png` | 6 帧：60 60 70 70 80 90 | 3 列 × 2 行，2304×1536 | `Animation: BASIC ATTACK, 6 frames, one shot with the front pistol (the bullet is a separate effect - do not draw it): 1 the front arm swinging down from the raised pose toward the target, 2 the arm straight, aiming right, 3 THE SHOT: the pistol kicks up with a small cyan-white muzzle flash (2-3 squares), 4 the recoil held, 5 the arm lowering, 6 back toward the idle pose. The other pistol stays raised beside his head.` |
| 5 | `lucian_passive.png` | 7 帧：50 50 60 60 60 70 90 | 4 列 × 2 行，最后一格空，3072×1536 | `Animation: DOUBLE SHOT, 7 frames: he turns a little side-on with BOTH pistols forward at shoulder height, one above the other; 3 the upper pistol fires (kicks up, small muzzle flash), 4 it comes back level, 5 the lower pistol fires (kicks up, small muzzle flash), 6 both level, 7 back toward the idle pose. Keep his face visible.` |
| 6 | `lucian_skill.png` | 7 帧：60 60 70 70 80 80 90 | 4 列 × 2 行，最后一格空，3072×1536 | `Animation: PIERCING LIGHT, 7 frames: 1-3 he turns side-on and braces, both pistols pushed forward together, a faint glow gathering at the crystals, 4 THE BEAM: both pistols held level at the height of his belt, a bright white-cyan flash at both muzzles (the beam itself is a separate effect and comes out at his waist), 5 a strong recoil - both pistols kicked up, he leans back, 6 recovering, 7 back toward the idle pose. Keep his face visible.` |
| 7 | `lucian_skill2.png` | 8 帧：50 50 50 60 60 70 80 90 | 4 列 × 2 行，3072×1536 | `Animation: DASH FORWARD then ARDENT BLAZE, 8 frames: 1 he crouches into the dash, 2-3 a low flat dive forward to the RIGHT, the body nearly horizontal, both pistols pointing forward, the coat streaming behind (off the ground, never below the feet line), 4 landing in a crouch on the ground line, 5 rising, the front arm reaching toward the target, 6 THE SHOT: the front pistol fires with a golden muzzle flash, 7 the recoil, the other pistol raised, 8 back toward the idle pose.` |
| 8 | `lucian_skill2_back.png` | 8 帧：50 50 50 60 60 70 80 90 | 4 列 × 2 行，3072×1536 | `Animation: DASH BACKWARD then ARDENT BLAZE, 8 frames: 1 he pushes off, 2-3 he leaps BACKWARD to the LEFT while still facing right, the body leaning back, both pistols pointing forward at the enemy, the coat flying forward (above the feet line), 4 landing on the ground line, 5-8 exactly like frames 5-8 of the forward dash: the front arm reaching out, the shot with a golden muzzle flash, the recoil, back toward idle.` |
| 9 | `lucian_ult.png` | 4 × 75（循环） | 4 列 × 1 行，3072×768 | `Animation: THE CULLING, 4 frames, a seamless fast loop: a planted wide stance, both pistols held forward at chest height, firing one after the other (the bullets are a separate effect): 1 the upper pistol kicks up with a small muzzle flash, 2 both level, 3 the lower pistol kicks up with a small muzzle flash, 4 both level. The legs, the body and the head do not move; only the pistols and the coat tails.` |
| 10 | `lucian_hit.png` | 2 × 100 | 2 列 × 1 行，1536×768 | `Animation: HIT, 2 frames: 1 jolted back by a blow, the pistols thrown up a little, 2 recovering toward the idle pose.` |
| 11 | `lucian_dead.png` | 8 帧：100 100 100 100 120 150 150 400 | 4 列 × 2 行，3072×1536 | `Animation: DEATH, 8 frames: struck, he staggers backward, falls to his knees and then onto his back on the ground line; the pistols drop from his hands and lie beside him from frame 5; the last frame lies still. Only here the body may reach 2 squares below the feet line.` |

---

## Claude 导入时的对应关系（给 Claude 看）

- 交回的 `lucian_native.png`（选定的造型图）和 10 张 `lucian_<动作>.png` 放进 `assets/source/native/`；`lucian_cells.json`（每帧站位点和帧时长，`tools/lol/native_pose.py assets/source/lucian/poses.json` 写出）不变，脚底线是站位点下方 11 行。先照 `tools/art/tidy_fiddlesticks.py` 的做法逐帧查：眼睛有没有连成横杠、有没有杂色、手臂和枪有没有挡脸，放大 5–6 倍看。
- `python tools/art/import_native.py --hero lucian`：每个 8×8 方块读成一个游戏像素，按站位点切帧；待机只用第 1 帧，第 3–5 帧下沉一格呼吸（`ORDER` / `BOB`）；举过头顶的枪是每帧最上面几行，不是头，所以按眼睛的颜色对齐待机和移动（`EYES`）。
- 出手时刻：普攻第 7 tick（第 3 帧）、圣光银弹第 6 和第 13 tick（第 3、5 帧）、Q 第 12 tick（第 4 帧）、E+W 的烈弹第 16 tick（第 6 帧）、R 每 9 tick 一枪（4 帧 × 75 ms 的循环里第 1、3 帧）。导入后重跑 `preview_lucian.py`，重新量头像截取点。
