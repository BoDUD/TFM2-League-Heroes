# 远古恐惧 费德提克：模型重画（给 Codex 的提示词）

> **这一轮只重画角色（造型图 + 10 张动作图），特效不变。**
> - 用户看了游戏里的费德提克，觉得模型太丑，要 Codex 重画。现在的问题（附 `ingame_hpbar.png`，游戏截图）：
>   1. 镰刀的刀刃挂在脚底下面，游戏在脚下画血条，刀刃被血条盖住，看不到；高跷的爪尖也比脚底线低 3–4 格。
>   2. 麻袋头是一颗很亮的白色"蛋"，满脸大牙，像卡通吉祥物；身体是一团暗紫色；细长的手臂和镰刀在动作里像一团乱枝。
> - 目标：一眼认出是英雄联盟的费德提克（附 `lol_ref_model.png`：原版模型，和我们同一个镜头），画成团战经理2 原版英雄那样干净的像素画（附 `tfm2_style_ref_undead.png`、`tfm2_style_ref_mage.png`）。
> - **先只做造型图**（A / B / C 三个方案），交回给用户挑；选定后再同一批做 10 张动作图。
> - 生图原稿通常不在严格网格上（方块 7.4–8.6 px、脸会变窄）。交回前请整理成：每个像素一个严格对齐的 8×8 纯色块，透明度只有全透明和不透明，每帧的脚底踩在参考线上，每帧的头和选定造型图的头一样大。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、有没有没做到的地方）和 `MANIFEST.json`（文件名、尺寸、每帧所在的格子）。

## 附图（都在压缩包里；英雄联盟渲染图、原版英雄对照图、游戏截图只在本地用，不要提交）

| 文件 | 内容 | 用在 |
|---|---|---|
| `lol_ref_model.png` | 英雄联盟原版模型（原比例），和我们同一个镜头（3/4 朝右、俯视 25°）：左边全身待机，右边麻袋头和锯盘的特写 | 造型图（长相以它为准） |
| `fiddlesticks_now_design.png` | 现在游戏里的待机第 1 帧，放大 8 倍（1024×1024，每个像素 8×8） | 造型图（大小和站位；长相不要照它） |
| `tfm2_style_ref_undead.png`、`tfm2_style_ref_mage.png` | 团战经理2 原版英雄（上排待机、下排攻击），放大 8 倍：像素大小和干净程度照它们；死灵法师竖着拿法杖的样子就是镰刀要的拿法 | 造型图、动作图 |
| `ingame_hpbar.png` | 游戏截图：刀刃被血条盖住 | 说明 |
| `fiddlesticks_now_<动作>.png` | 现在游戏里的每个动作，放大 8 倍，按格子排好（每格 96×96 个方块 = 768×768 px） | 各自的动作图（帧数、每帧的时机和站位） |
| `lol_pose_<动作>.png` | 英雄联盟原版同一帧的动作渲染，和上一张同样的格子、同样的位置 | 各自的动作图（动作照它） |
| `fiddlesticks_guide_<动作>.png` | 每帧的站位点（十字）和脚底线（红线），红线以下的淡红区不能有任何像素 | 各自的动作图（对位用，不要画进图里） |
| `fiddlesticks_cells.json` | 每帧的站位点（格子里第几列、第几行，单位是方块）和帧时长 | 整理对位 |

## 所有图的规则

- **像素尺寸（最重要）**：他在游戏里约 36 像素高（头后锯盘的尖和头顶枝角到爪尖），按真正的低分辨率像素画来画，再整体放大 8 倍输出：每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净，不要细节**：整个精灵最多 24 种颜色；每种材质 2–3 个平涂色阶（亮、中、暗）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；轮廓 1 个方块宽的近黑色描边，内部深色线条越少越好。
- **脚底线以下什么都不能有（新规则）**：爪尖正好踩在每帧的脚底线上（格子里第 72 行方块是最低一行，即 576–583 px；参考图的红线在 584 px），红线以下不能有任何像素——镰刀、刀刃、斗篷、影子都不行，游戏在脚下画血条，下面的东西会被盖住。只有技能2 挥镰的帧和死亡倒地的帧可以低于红线，最多 2 格。
- **镰刀**是他最重要的剪影：长木柄 + 一把生锈、带锯齿的大弯刃，刀刃至少 7×4 个方块，要看得清。平时竖着或斜着拿在身后，刀刃在肩膀到头顶的高度（像原版死灵法师竖着拿法杖），不拖在地上。
- 3/4 正面朝右（脸朝右边的敌人），不画背影。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号，也不要把参考图的十字和红线画进去。
- 如果模型不肯画有名字的角色，把 "Fiddlesticks" / "League of Legends" 删掉，只保留外观描述。

## 他的样子（照 `lol_ref_model.png`）

- **麻袋头**：土黄色粗麻布袋，像兜帽一样往前、往下垂（不是圆蛋），布面上几道深色缝线；正面一道竖着的缝口，两边一排小三角牙（一条深色的缝，不是满脸大嘴）；缝口上方两只发光的黄绿色眼睛（每只 2×2 个方块，待机时两只都看得见）；头顶两根黑色细枝角。
- **锯盘**：头后面一个大圆锯盘（灰紫色金属，一圈尖齿，中间一个深色圆孔），是原版最显眼的剪影，从头的后上方露出来。
- **身体**：瘦长、驼背。黑褐色的木头骨架，胸口几条横木肋条，两三道暗红色发光的裂纹；肩上披着一片片破麻布（和头一样的土黄色），垂到腰；腰上一圈草绳。
- **手臂**：拿镰刀的一条缠着麻布（土黄色），另一条是黑色细长的木手臂，手是几根长爪。
- **腿**：像金属高跷一样的细长腿，胯部和膝盖有圆形齿轮关节，脚是鸟爪一样的钩爪。
- **颜色**（从原版取的，可按渲染图微调）：麻布 `#EACB94` `#C8985E` `#946438`；黑木 `#4A2E36` `#2C1A22`；描边 `#140A0E`；金属 `#B8A2A6` `#8A7478` `#5A4448`；锈刃 `#C8644A` `#943A2E` `#5E2220`；刃口 `#D8CCC4`；发光裂纹 `#E0443A`；眼睛 `#F4F8B0` `#C8E060`；草绳 `#A08A40` `#6E5A28`。

---

## 1. 造型图（先只做这一步）：`fiddlesticks_design_A.png`、`fiddlesticks_design_B.png`、`fiddlesticks_design_C.png`

三个方案的长相、颜色都一样，只有比例和拿镰刀的方式不同，交回给用户挑：

| 方案 | 比例 | 镰刀 |
|---|---|---|
| A | 照原版：头约占身高 1/4，高跷腿长，驼背很明显 | 竖着拿在身后，刀刃在头后上方 |
| B | 团战经理2 的 Q 版：头约占身高 1/3（像原版英雄），腿短一些 | 竖着拿在身后，刀刃在头后上方 |
| C | 介于 A 和 B 之间 | 扛在肩上，刀刃从背后越过肩头朝前弯 |

每个方案附三张图：`fiddlesticks_now_design.png`、`tfm2_style_ref_undead.png`、`lol_ref_model.png`。

```text
Three attached images. FIRST: our game's current in-game sprite of this character at 8x (every game pixel an 8x8 block) - use it ONLY for the size and the place in the canvas; its look is rejected (too big and bright a head, a muddy purple body, the scythe hanging below the feet). SECOND: official heroes of the game Teamfight Manager 2 at 8x - match this pixel size and cleanliness: big flat areas, few colors, bold readable shapes. THIRD: the original 3D model of the character seen from the same camera - copy its look: the shapes, materials and colors.
Task: draw the character as clean hand-made pixel art: a sprite about 36 pixels tall (from the tips of the saw collar and the twig horns to the claw feet), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency.
Fiddlesticks from League of Legends (2020 default look): a tall, gaunt, hunched living scarecrow. His head is a tan burlap sack that hangs forward and down like a drooping hood, with a few dark stitch lines; on its front a vertical stitched slit with a row of small triangular teeth (a thin dark seam, not a huge mouth), two small glowing yellow-green eyes above it, two thin black twig horns on top. Behind his head and shoulders a big round saw-blade collar in dull mauve-grey metal with a ring of sharp teeth and a dark hole in the middle - his most recognizable shape. A skeletal body of dark maroon-black wood, a few horizontal wooden ribs on the chest, two or three glowing red cracks; tattered strips of tan burlap hang from his shoulders to his waist; a coil of straw rope round the waist. One arm wrapped in tan burlap holds the scythe; the other is a long thin black wooden arm ending in long claws. Legs like thin metal stilts with round gear joints at the hips and knees, ending in bird-like hooked claws. The scythe: a long dark wooden pole and a big rusty jagged curved blade (at least 7x4 squares) with a pale edge.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades; palette: burlap #EACB94 #C8985E #946438, dark wood #4A2E36 #2C1A22, outline #140A0E, metal #B8A2A6 #8A7478 #5A4448, rusty blade #C8644A #943A2E #5E2220, blade edge #D8CCC4, glowing cracks #E0443A, eyes #F4F8B0 #C8E060, straw rope #A08A40 #6E5A28. Big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Drop details that do not read at this size.
Proportions and scythe: [A: as the original model - the head about one quarter of his height, long stilt legs, a strong hunch; he holds the scythe upright behind him, its blade above and behind his head.] [B: chibi like the game's heroes - the head about one third of his height, shorter legs; he holds the scythe upright behind him, its blade above and behind his head.] [C: between A and B; the scythe rests on his shoulder, its blade curving forward over his shoulder from behind.] Keep the whole scythe ABOVE his feet - no part of anything below the soles (the game draws the health bar right under the feet).
Face: both eyes clearly visible (2x2 squares each, glowing yellow-green), the sack's slit and teeth readable, the saw collar showing behind the head.
Pose, size and place: the idle stance, standing on his claw feet; the soles on the line 28 squares (224 px) above the bottom of the image; the character horizontally centered. 3/4 FRONT view facing right.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 36 squares tall, all squares 8x8 on one grid, at most 24 colors, both eyes visible, the saw collar and the scythe blade easy to read, nothing below the soles.
```

中括号里是三个方案各自的一段，每张只保留自己那一段。

## 选定：方案 B

Codex 交回 A / B / C 三张（`fiddlesticks_model_designs.zip`，都是严格 8×8 方块、15–16 色）。用户让 Claude 代选，选了 **B**（麻袋头约占身高 1/3，竖持大弯镰，刀刃弧在头顶上方）：和包里其他英雄一样是 Q 版大头，游戏尺寸下两只眼睛最清楚；头顶的弯刃是三张里最好认的镰刀剪影，也完全在血条上方。A 头太小、刀刃像宽锯片；C 横扛的镰刀让剪影宽到 42 px，刀刃挡在脸前。`fiddlesticks_design_B.png` 改名为 `fiddlesticks_native.png`，动作图里一起改进四点：

1. 身体和腿更干净：黑木只用 2 个色阶大块平涂，去掉躯干和腿上零散的红点、灰点（发光裂纹只留 2–3 道短线）；
2. 锯盘画出一圈 5–6 个三角尖齿和中间的深色圆孔，看得出是圆锯；
3. 麻袋头保持 B 的大小和形状，脸朝右时两只黄绿眼睛都在，正面加一条竖着的深色缝口；
4. 镰刀保持 B 的大弯刃（刃口一条浅色边），刀刃始终在脚底线以上。

---

## 2–11. 动作图（用户选定造型后，同一批做）

每张附三张图：第一张是**选定的造型图**（交回时改名为 `fiddlesticks_native.png`），第二张是对应的 `fiddlesticks_now_<动作>.png`，第三张是对应的 `lol_pose_<动作>.png`；对位用 `fiddlesticks_guide_<动作>.png` 和 `fiddlesticks_cells.json`。输出文件名 `fiddlesticks_<动作>.png`，排版和第二张附图完全一样。

10 张的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

```text
Three attached images. FIRST: the approved clean pixel-art design of this character at 8x (every pixel an 8x8 block) - copy his colors, shapes, head, saw collar, scythe and pixel style exactly, the head the same size in every frame. SECOND: our current in-game animation at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery) and where he stands in his cell, but NOT its look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
Task: draw every frame as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size (about 36 pixels tall when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): at most 24 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. Keep the face readable (both glowing eyes whenever the head faces right). Keep the scythe a clear shape - the pole a clean 1-square line, the blade at least 7x4 squares. 3/4 FRONT view facing right, never his back.
Feet line: in every cell the lowest row of his claws is square row 72 from the top of the cell (pixels 576-583), the same line in every frame; NOTHING from pixel 584 down - not the scythe, not the blade, not cloth - because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in fiddlesticks_cells.json).
[animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size]; frame N in the same cell as in the SECOND image. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
```

| # | 文件 | 帧 × 毫秒 | 排版 | `[animation]` |
|---:|---|---|---|---|
| 2 | `fiddlesticks_idle.png` | 6 × 200 | 3 列 × 2 行，2304×1536 | `Animation: IDLE, 6 frames: he stands hunched on his stilt legs, the sack head drooping forward, the claw arm hanging, the scythe held upright behind him exactly as in the FIRST image. Draw all 6 frames the same (the game adds the breathing).` |
| 3 | `fiddlesticks_run.png` | 8 × 108 | 4 列 × 2 行，3072×1536 | `Animation: MOVE loop, 8 frames: his stalking walk from the THIRD image - a long stride on the stilt legs, leaning forward, the claw arm swinging; frames 1-4 one stride, 5-8 the other; the scythe carried upright or sloped back, its blade high, never dragging on the ground; the head bobs at most 1 square.` |
| 4 | `fiddlesticks_attack.png` | 6 帧：60 60 70 70 80 90 | 3 列 × 2 行，2304×1536 | `Animation: BASIC ATTACK, 6 frames: he flings a dark bolt with his claw hand (the bolt is a separate effect - do not draw it): 1 wind-up, 2 lunging forward, 3 the claw arm stretched fully forward (the release), 4-5 held, 6 back toward idle; the scythe stays behind him, off the ground.` |
| 5 | `fiddlesticks_skill.png` | 8 帧：50 50 60 60 70 70 80 90 | 4 列 × 2 行，3072×1536 | `Animation: TERRIFY, 8 frames: 1 idle-like, 2-4 he hunches and curls up, head down, gathering (frame 4 is the moment the crow flies out - a separate effect), 5-8 he unfolds back up to idle.` |
| 6 | `fiddlesticks_skill2.png` | 7 帧：50 60 60 50 80 80 90 | 4 列 × 2 行，最后一格空，3072×1536 | `Animation: REAP, 7 frames: a huge sweeping swing of the scythe at full stretch - 1-2 wind-up, the scythe reaching far out, 3-4 the sweep at full length (the hit lands at frame 4), 5 the scythe whipped up overhead, 6-7 back toward idle. The blade may dip at most 2 squares below the feet line here.` |
| 7 | `fiddlesticks_w_loop.png` | 8 × 250 | 4 列 × 2 行，3072×1536 | `Animation: BOUNTIFUL HARVEST, 8 frames, a seamless 2-second loop: he leans back with his arms spread wide, the scythe held out to one side above the feet line, swaying slowly as he drains souls (the souls are a separate effect).` |
| 8 | `fiddlesticks_ult.png` | 8 × 125 | 4 列 × 2 行，3072×1536 | `Animation: CROWSTORM CHANNEL, 8 frames over 1 second: 1-4 he crouches low and gathers, 5-8 he rises tall with his arms and the scythe raised high, about to burst into crows.` |
| 9 | `fiddlesticks_ult_land.png` | 4 × 125 | 4 列 × 1 行，3072×768 | `Animation: CROWSTORM LANDING, 4 frames: he lands in a low crouch, knees bent, arms spread, rising a little each frame.` |
| 10 | `fiddlesticks_hit.png` | 2 × 100 | 2 列 × 1 行，1536×768 | `Animation: HIT, 2 frames: 1 jolted back by a blow, 2 recovering toward idle.` |
| 11 | `fiddlesticks_dead.png` | 8 帧：100 100 100 100 120 150 150 400 | 4 列 × 2 行，3072×1536 | `Animation: DEATH, 8 frames: struck, he stumbles and falls apart into a heap of sticks and burlap on the ground line; the scythe drops from his hand and lies flat on the ground beside him (frames 3-8); the last frame lies still. Here the heap may reach 2 squares below the feet line.` |

---

## Claude 导入时的对应关系（给 Claude 看）

- 交回的 `fiddlesticks_native.png`（选定的造型图）和 10 张 `fiddlesticks_<动作>.png` 先过 `python tools/art/tidy_fiddlesticks.py <交付文件夹>`：连成横杠的眼睛改回待机那样一高一低的两只，夜割最后一帧镰刀柄上的眼睛绿换成柄的颜色，普攻第 2–5 帧从麻袋正面伸出的手臂下移 5 行、从麻袋下面伸出；写进 `assets/source/native/`。`fiddlesticks_cells.json`（每帧站位点和帧时长）不变，脚底线是站位点下方 11 行（第 72 行）。Codex 的两次交接说明在 `codex_model/`。
- `python tools/art/import_native.py --hero fiddlesticks`：每个 8×8 方块读成一个游戏像素，按站位点切帧；待机只用第 1 帧，第 3–5 帧导入时下沉一格呼吸（`ORDER` / `BOB`）。重画的头不再是贴上去的，`fiddlesticks` 从 `PASTED` 里去掉；镰刀举在头顶，最上面几行不是头，所以按眼睛的颜色对齐待机和移动（`EYES`，移动原来左右晃 12 像素）。
- 出手时刻不变（普攻第 8 tick、Q 第 13 tick、夜割第 13 tick 出现第 18 tick 命中、第 25 tick 起引导），所以每帧的时机要和现在的动作图一致；导入后重跑 `preview_fiddlesticks.py`，重新量头像截取点。
