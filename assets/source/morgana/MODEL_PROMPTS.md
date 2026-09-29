# 堕落天使 莫甘娜：角色模型（给 Codex 的提示词）

> **第一版的记录，已被重做取代。** 用户后来给了一张新立绘，造型按 [`MODEL_REDESIGN.md`](MODEL_REDESIGN.md) 重做（选了方案 A），8 张动作图按 [`MODEL_REDESIGN_STRIPS.md`](MODEL_REDESIGN_STRIPS.md) 重画。这一份和 `codex_model/designs_*`、`codex_model/animations_*`（不带 `_A`）是造型 B 那一版的提示词和交付记录。

> **这一轮 Codex 画莫甘娜的全部角色图（造型图 + 8 张动作图），特效在同一个压缩包的 `PROMPTS.md` 里，可以同一轮一起画。**
> - 目标：一眼认出是英雄联盟的莫甘娜（附 `lol_ref_model.png`：原版模型，和我们同一个镜头），画成团战经理2 原版英雄那样干净的像素画（附 `tfm2_style_ref_mage.png`、`tfm2_style_ref_healer.png`）。
> - **先只做造型图**（A / B / C 三个方案，只有比例不同），交回给用户挑；选定后再同一批做 8 张动作图。
> - 生图原稿通常不在严格网格上（方块 7.4–8.6 px、脸会变窄）。交回前请整理成：每个像素一个严格对齐的 8×8 纯色块，透明度只有全透明和不透明，每帧的脚底踩在参考线上，每帧的头和选定造型图的头一模一样。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、有没有没做到的地方）、`manifest.json`（文件名、尺寸、每帧所在的格子、站位点、不透明范围）和 `generation_prompts.json`（实际用的提示词）。

## 附图（都在压缩包里；英雄联盟渲染图、原版英雄对照图只在本地用，不要提交）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/lol_ref_model.png` | 英雄联盟原版模型（原比例），和我们同一个镜头（3/4 朝右、俯视 25°）：左边全身待机，右边头部特写 | 造型图（长相以它为准） |
| `design/morgana_now_design.png` | 原版待机姿势按游戏尺寸取色（Q 版比例：头放大 2 倍），放大 8 倍，1024×1024，脚底在 y=792–799 | 造型图（大小和站位；它是 3D 模型取色，很糊，长相不要照它） |
| `design/morgana_league_chibi.png` | 同一个姿势的高清渲染（同一张画布、同一个位置） | 造型图（Q 版比例和姿势） |
| `refs/tfm2_style_ref_mage.png`、`refs/tfm2_style_ref_healer.png` | 团战经理2 原版法师和辅助（上排待机、下排攻击），放大 8 倍：像素大小、干净程度、眼睛画法照它们 | 造型图、动作图 |
| `now/morgana_now_<动作>.png` | 原版每个动作按游戏尺寸取色，放大 8 倍，按格子排好（每格 96×96 个方块 = 768×768 px） | 各自的动作图（帧数、每帧的时机、大小和站位） |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 各自的动作图（动作照它） |
| `guide/morgana_guide_<动作>.png` | 每帧的站位点（蓝十字）和脚底线（红线），红线以下的淡红区不能有任何像素，右上角是帧号和帧时长 | 各自的动作图（对位用，不要画进图里） |
| `morgana_cells.json` | 每帧的站位点（格子里第几列、第几行，单位是方块）和帧时长 | 整理对位 |

## 所有图的规则

- **像素尺寸（最重要）**：她在游戏里从头顶（不算头后的羽冠）到脚底约 34 像素高，按真正的低分辨率像素画来画，再整体放大 8 倍输出：每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净，不要细节**：整个精灵最多 24 种颜色；每种材质 2–3 个平涂色阶（亮、中、暗）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；轮廓 1 个方块宽的近黑色描边 `#140A1C`，内部深色线条越少越好。
- **脚底线以下什么都不能有**：游戏在脚下画血条，红线以下的东西会被盖住。脚底（和拖地的裙摆、羽毛拖尾）正好踩在每帧的脚底线上，红线以下不能有任何像素——裙摆、拖尾、翅膀、影子都不行。只有死亡倒地的帧可以低于红线，最多 2 格。
- **脸（每帧都一样）**：两只眼睛都看得见，照原版英雄的画法：近处的眼睛（画面左边）2 格宽、远处的眼睛 1 格宽，每只眼睛上面一格深色睫毛、下面是紫色瞳孔和亮点；两眼之间隔一格皮肤；眼睛下面两行皮肤，再一格深紫红色的嘴。头发的刘海可以斜盖额头，但**不能盖住眼睛**。
- **眼睛的颜色只用在眼睛上**（身上、特效、翅膀都不要用这个紫色），导入时按这个颜色找眼睛来对齐帧。
- 3/4 正面朝右（脸朝右边的敌人），看得到脸和胸口，不画背影（死亡最后趴下的帧除外）。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号，也不要把参考图的十字和红线画进去。
- 如果模型不肯画有名字的角色，把 "Morgana" / "League of Legends" 删掉，只保留外观描述。

## 她的样子（照 `refs/lol_ref_model.png`）

- **头**：长而直的黑紫色头发垂到肩后，侧分，一缕刘海斜在脸的一边；尖尖的精灵耳朵；淡粉紫色的皮肤；发光的紫色眼睛、深色眼影；深梅红色的嘴唇。头后面竖着一丛深紫色、带金边的尖羽（像羽冠），旁边一根弯弯的淡粉色羽角——这是她最好认的头部剪影，要画出来，但不挡脸。
- **身体**：一件拖地的深紫色长裙，裙摆一圈深墨绿近黑的羽毛边；黑色紧身胸衣带金色花纹，胸前一枚紫色宝石；肩上一圈白色的羽毛披肩；脖子上一个金色的吊坠；裙子上几枚金色的水滴形饰片。
- **手臂**：光着的淡粉紫色手臂，手腕上细金镯，手指细长、指甲深紫；待机时一只手在胸前、一只手向前摊开，像在凝聚暗影魔法。
- **翅膀**：收拢在背后，从肩后向上、向后伸出：深墨青近黑的羽毛，边缘和羽尖是亮洋红色；翅膀的尖从头两侧露出一点，**不挡脸和胸口**。
- **拖尾**：一条长长的淡粉色羽毛拖尾从裙子后面拖在地上，伸向画面左边（她身后），平贴着脚底线，**不能低于红线**。
- **颜色**（从原版贴图取的，可按渲染图微调；合计不超过 24 色）：描边 `#140A1C`；皮肤 `#F2CCE0` `#D6A0C0` `#A06C92`；头发 `#3E2654` `#26163A` `#140C22`；眼睛 `#C890FF`（只用在眼睛上）+ 睫毛和瞳孔用头发最深的 `#140C22`；嘴 `#7A2050`；长裙 `#7C4AC4` `#5A30A0` `#3A1C70`；羽毛裙边 `#3A4438` `#1E241E`；金饰 `#F0C860` `#B08838`；白披肩 `#F6F0FA` `#C8B8DA`；翅膀 `#2E4450` `#1A2830`、羽尖 `#D23CB4` `#F48AD8`；拖尾 `#E8B0CC`（阴影用 `#D6A0C0`）。

---

## 1. 造型图（先只做这一步）：`morgana_design_A.png`、`morgana_design_B.png`、`morgana_design_C.png`

三个方案的长相、颜色、姿势都一样，只有比例不同，交回给用户挑：

| 方案 | 比例 |
|---|---|
| A | 团战经理2 的 Q 版：头约占身高 1/3（和原版牧师、附魔师一样），就是 `morgana_league_chibi.png` 的比例 |
| B | 更 Q：头约占身高 2/5，身体短一些 |
| C | 更接近原版身材：头约占身高 3/10，身体和长裙更修长 |

每个方案附五张图：`design/morgana_now_design.png`、`design/morgana_league_chibi.png`、`refs/lol_ref_model.png`、`refs/tfm2_style_ref_mage.png`、`refs/tfm2_style_ref_healer.png`。

```text
Five attached images. FIRST: our game-size color sample of the character's idle pose at 8x (every game pixel an 8x8 block) - use it ONLY for the size and the place in the canvas; it is a blurry downsample of a 3D model, not a look to copy. SECOND: the same pose as a high-resolution 3D render on the same canvas, in our chibi proportions (the head enlarged 2x). THIRD: the original 3D model of the character seen from the same camera, full body and a head close-up - copy its look: the shapes, materials and colors. FOURTH and FIFTH: official heroes of the game Teamfight Manager 2 at 8x - match this pixel size and cleanliness: big flat areas, few colors, bold readable shapes, and their way of drawing eyes.
Task: draw the character as clean hand-made pixel art: a sprite about 34 pixels tall from the top of her head (not counting the feather crest behind it) to her feet, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency.
Morgana from League of Legends (current default look), a fallen angel sorceress, chibi, 3/4 FRONT view facing right, standing calmly and conjuring dark magic: one hand held before her chest, the other open palm reaching forward to the right. Long straight black-violet hair falling behind her shoulders, parted to the side with one lock across the side of her forehead - never over her eyes; long pointed elf ears; pale pinkish-lavender skin; glowing violet eyes; dark plum lips. Behind her head a tall crest of dark violet, gold-edged spiky feathers and one curved pale-pink feather horn - her most recognizable head shape, kept behind the head, not over the face. A floor-length deep violet gown with a hem of dark moss-black feathers; a black corset with gold trim and a violet gem on the chest; a white feather stole over her shoulders; a gold pendant at the throat; a few gold teardrop ornaments on the skirt. Bare arms with thin gold bracelets and long dark-purple nails. Her wings are FOLDED on her back: dark teal-black feathers with bright magenta feather tips, rising behind her shoulders, their tips just showing beside her head, never covering her face or chest. A long pale-pink feather train lies on the ground behind her, trailing to the LEFT of the image along the ground line.
Face (most important): both eyes clearly visible like the game's heroes - the near eye (left of the face's middle) 2 squares wide, the far eye 1 square wide against the right cheek; each eye a dark lash square on top and a glowing violet square below; one square of skin between the eyes; two rows of skin under the eyes, then one dark plum mouth square on the face's middle line. The violet eye color #C890FF is used ONLY in the eyes, nowhere else.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades; palette: outline #140A1C, skin #F2CCE0 #D6A0C0 #A06C92, hair #3E2654 #26163A #140C22, eyes #C890FF, mouth #7A2050, gown #7C4AC4 #5A30A0 #3A1C70, feather hem #3A4438 #1E241E, gold #F0C860 #B08838, white stole #F6F0FA #C8B8DA, wings #2E4450 #1A2830 with tips #D23CB4 #F48AD8, train #E8B0CC. Big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Drop details that do not read at this size.
Proportions: [A: chibi like the game's heroes - the head about one third of her height, as in the SECOND image.] [B: cuter - the head about two fifths of her height, a shorter body.] [C: closer to the original model - the head about three tenths of her height, a slimmer, longer body and gown.]
Pose, size and place: the idle stance of the FIRST image; her soles and the gown's lowest edge on the line 28 squares (224 px) above the bottom of the image (the lowest drawn row is y 792-799); nothing below y 800 - not the gown, not the train, not the wings (the game draws the health bar right under the feet); the character's standing point in the middle column. 3/4 FRONT view facing right.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 34 squares from the top of the head to the soles, all squares 8x8 on one grid, at most 24 colors, both eyes visible and built as described, the violet eye color only in the eyes, the crest and the folded wings behind her, nothing below y 800.
```

中括号里是三个方案各自的一段，每张只保留自己那一段。

## 选定：方案 B（Claude 整理到游戏网格）

Codex 交回 A / A 简化 / B / C 四张（`morgana_design_candidates.zip`）。四张都是生图原稿：画布 1254×1254，其实是 128×128 格的像素画拉伸过去的（一格 9.797 px），人物 67（B）到 118（A、C）格高，比游戏尺寸大两三倍，还有抗锯齿和几万种颜色。用户让 Claude 整理、代选，看了游戏尺寸的对比后说 B（大头短身）"这个做的挺好的"。整理的做法（`design/morgana_native.png` 就是结果）：

1. 按草稿自己的网格把每格取成一种颜色（格子中间那片像素的多数色），得到 52×67 格的干净像素画；
2. 映射到 20 色色板（下表）；
3. 缩到游戏尺寸时不做平均：每 3 行（列）里删掉和邻行（列）最像的那一行（列），比例不变，眼睛、嘴、金边、描边这些只有一格粗的细节留下来；
4. 手修：脸按原版英雄的画法（近眼 2 格、远眼 1 格，上面一格深色睫毛、下面紫色眼珠，两眼之间一格皮肤，嘴 1 格在中线上）；羽冠里被当成嘴色的红改回羽冠红；粉色羽角补上左边描边；拖尾尖上的发色杂点；最后把没有描边的外轮廓补上一圈。

结果 34×45 格（含羽冠；头顶到脚底约 37 格），20 色，放在 128×128 的画布上，脚底在第 99 行（y 792–799）。**动作图照它画**，下面的动作图提示词已按它改好：

| 部位 | 颜色 |
|---|---|
| 描边 | `#16041E` |
| 头发（暗、中、亮） | `#220B2E` `#361951` `#531D70` |
| 皮肤（亮、中、暗；拖尾也用） | `#F6DCEA` `#E4ADCB` `#C572A4` |
| 眼睛（**只用在眼睛上**）、嘴 | `#C890FF`、`#7A1E48` |
| 长裙（亮、中、暗） | `#6A34A0` `#4E237A` `#2E1446` |
| 羽毛裙边、翅膀（亮、暗） | `#343B3A` `#222527` |
| 洋红羽尖（亮、暗） | `#CF3CA4` `#8A2878` |
| 金饰（亮、暗） | `#E4B44C` `#9B7034` |
| 羽冠红 | `#8E2A4E` |
| 白羽披肩 | `#FBF3FB` |

动作参考（`now/`、`pose/`、`guide/`、`morgana_cells.json`）也按 B 的比例重新渲染了（头放大 2.4 倍，头顶到脚底 37 格）。

---

## 2–9. 动作图（用户选定造型后，同一批做）

每张附三张图：第一张是**选定的造型图** `design/morgana_native.png`（上一节整理好的 B），第二张是对应的 `now/morgana_now_<动作>.png`，第三张是对应的 `pose/lol_pose_<动作>.png`；对位用 `guide/morgana_guide_<动作>.png` 和 `morgana_cells.json`。输出文件名 `morgana_<动作>.png`，排版和第二张附图完全一样。

8 张的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

**第一轮的教训**：造型原稿画得比游戏尺寸大两三倍（67–118 格高）。动作图每帧要按造型图的大小画（头顶到脚底约 37 格），不要画成大图再缩小。生图工具做不到严格网格时，照同样的排版（每格 768×768 px，帧的位置和第二张附图一样）直接交原稿也可以，Claude 会像处理造型图那样整理：按格取色、换回造型图的头、脚底对齐到站位线。

```text
Three attached images. FIRST: the approved clean pixel-art design of this character at 8x (every pixel an 8x8 block, 34x45 squares with the crest) - copy her colors, shapes, head, face, hair, crest, wings, gown and pixel style exactly. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), her size and where she stands in her cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
Task: draw every frame as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size as the FIRST image (about 37 squares from the top of the head to the feet when standing, 45 with the crest), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 20 colors of the FIRST image - outline #16041E; hair #220B2E #361951 #531D70; skin #F6DCEA #E4ADCB #C572A4 (the feather train uses them too); eyes #C890FF (only the eyes); mouth #7A1E48; gown #6A34A0 #4E237A #2E1446; feather hem and wings #343B3A #222527; magenta tips #CF3CA4 #8A2878; gold #E4B44C #9B7034; crest red #8E2A4E; white stole #FBF3FB. Big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. 3/4 FRONT view facing right, never her back.
The head is COPIED from the FIRST image in every frame - the same outline, hair, crest and face, square for square - and only moved (or tilted as a whole where the body bends); never redraw it, or it flickers when the frames play. The eyes stay exactly as in the FIRST image in every frame (the near eye 2 squares wide, the far eye 1 square, one skin square between them, the same distance from the mouth) - never merged into a bar or a line; the violet eye color appears ONLY in the eyes. Her arms come out of her shoulders and never cross in front of her face. The folded wings stay behind her body.
Feet line: in every cell the lowest row of her feet and gown is square row 78 from the top of the cell (pixels 624-631), the same line in every frame; NOTHING from pixel 632 down - not the gown, not the feather train, not the wings - because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in morgana_cells.json).
[animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size]; frame N in the same cell as in the SECOND image. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
```

| # | 文件 | 帧 × 毫秒 | 排版 | `[animation]` |
|---:|---|---|---|---|
| 2 | `morgana_idle.png` | 6 × 200 | 3 列 × 2 行，2304×1536 | `Animation: IDLE, 6 frames: all 6 frames are exactly the FIRST image, unchanged (the game adds the breathing).` |
| 3 | `morgana_run.png` | 8 × 143 | 4 列 × 2 行，3072×1536 | `Animation: MOVE loop, 8 frames, her walk from the THIRD image: an upright gliding walk, the gown swaying and one foot stepping out under the hem in turn (frames 1-4 one step, 5-8 the other), the arms held slightly out, the feather train trailing behind her to the left on the ground line. Her HEAD stays in the same place across the cell relative to her standing point in all 8 frames (at most 1 square up or down) - only the gown, the feet, the arms and the train move.` |
| 4 | `morgana_attack.png` | 6 帧：60 70 80 90 100 100 | 3 列 × 2 行，2304×1536 | `Animation: BASIC ATTACK, 6 frames: she flings a bolt of dark magic with her hand (the bolt is a separate effect - do not draw it): 1 the hand drawn back to her shoulder, 2 both hands swinging forward, 3 the throwing arm stretched fully forward to the right, palm open (the release), 4 held, 5-6 back toward idle.` |
| 5 | `morgana_skill.png` | 6 帧：70 70 80 90 110 150 | 3 列 × 2 行，2304×1536 | `Animation: DARK BINDING, 6 frames: she whirls and hurls the binding orb (a separate effect): 1 gathering, arms drawn in, the gown starting to swirl; 2 turning, the gown flaring wide around her; 3 the throw - one arm flung far forward to the right (the release); 4-5 the gown settling, the arm still reaching; 6 back toward idle. Keep her face toward the viewer in every frame.` |
| 6 | `morgana_skill2.png` | 6 帧：60 60 80 100 100 100 | 3 列 × 2 行，2304×1536 | `Animation: BLACK SHIELD, 6 frames: she casts a shield on an ally: 1-2 she raises one hand high above her head, the other hand forward; 3-5 the raised hand held high, fingers spread (the shield is a separate effect); 6 back toward idle.` |
| 7 | `morgana_ult.png` | 8 帧：80 80 80 90 100 100 110 120 | 4 列 × 2 行，3072×1536 | `Animation: SOUL SHACKLES, 8 frames: 1 she crouches a little, gathering; 2 she rises, lifting off the ground as in the THIRD image; 3-4 arms thrown wide open to both sides, her wings spreading wide behind her and the gown flaring (the chains are a separate effect); 5-6 she leans forward with her arms pulling, as if dragging chains; 7-8 back toward idle, the wings folding again. Only here may her wings open; they must still stay above the feet line.` |
| 8 | `morgana_hit.png` | 2 × 120 | 2 列 × 1 行，1536×768 | `Animation: HIT, 2 frames: 1 jolted back by a blow, eyes squeezed shut (two short dark lines), 2 recovering toward idle.` |
| 9 | `morgana_dead.png` | 8 帧：100 100 120 120 120 150 150 500 | 4 列 × 2 行，3072×1536 | `Animation: DEATH, 8 frames: 1 struck; 2-3 she staggers with her arms spread; 4 she collapses forward; 5-6 on her knees and hands, head bowed; 7 sinking down; 8 lying face down on the ground line, the wings flat on her back, the gown spread around her. Here the body may reach 2 squares below the feet line.` |

---

## Claude 导入时的对应关系（给 Claude 看）

- 交回的选定造型图改名 `morgana_native.png`，8 张动作图 `morgana_<动作>.png`，一起放进 `assets/source/native/`；`morgana_cells.json`（`tools/lol/native_pose.py assets/source/morgana/poses.json` 写的每帧站位点和帧时长）也放进去，不改。脚底是站位点下方 11 行（格子第 78 行），红线在第 79 行。
- `python tools/art/import_native.py --hero morgana`：每个 8×8 方块读成一个游戏像素，按站位点切帧；待机只用第 1 帧，加呼吸（`ORDER` / `BOB`）；按眼睛的颜色 `#C890FF` 对齐待机和移动（`EYES`）。交回后先逐帧放大看眼睛、头的轮廓、手臂和脚底线，需要时照 `tools/art/tidy_fiddlesticks.py` 写一个整理脚本。
- 出手时刻按这些帧定（普攻第 3 帧、Q 第 3 帧、E 第 4 帧、R 第 3 帧），数据里的 `start_timing` 已经对上；导入后做 `preview_morgana.py` 的演示 GIF，重新量头像截取点（`tfm2_ase.py face`）。
