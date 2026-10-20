# 祖安怒兽 沃里克：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（弓背的待机）**（`1_picture_A.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把他画成**游戏里的格子数**：**从背上尖刺的顶端到脚底 69 格**，连尾巴约 94 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、牙、嘴、鬃毛、护臂上的药剂碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **只画 3/4 正面朝右**（和 A 一样；**不画侧面**）：游戏里的待机，所有动作也都从这张图来做。
> - **每格画大：12 px 一格**。画布用你平时的 **1254 × 1254**：**尖刺顶端 y = 348，眼睛约 y = 696，脚底 y = 1176**。每一格都是 12 × 12 px 的方块，不要用更小的格子画细节。**画三稿。**

## 大小和位置（照 `2_target.png` / `3_layout.png`）

- 画布 **1254 × 1254**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **尖刺顶端 y = 348**（绿线），**眼睛约 y = 696**（蓝线），**脚底 y = 1176**（红线）：尖刺顶端到脚底 **69 格**。
- 宽约 94 格（尾巴尖到前面那只爪子），放在 `2_target.png` 的位置。

## 在 69 格里要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍）：**两只很大的尖耳朵**（蓝紫色的毛，里面粉色 2 档）；脸上白色的鬃毛（白、淡蓝灰 2–3 档）；**两只黄眼睛：每只至少 2 格，一样高，都看得见**（黄色 + 一格深色的眼角）；深色的鼻子；**张开的嘴**：红色的口腔、粉色的舌头、**上下白色的尖牙（每颗至少 1 格）**；额头上两三道暗红色的疤。
- **身体**：蓝紫色的毛 3–4 档（亮边偏浅蓝，暗处深靛蓝，**不要糊成一团黑**），胸口和下巴是大片白色鬃毛；背上脖子后面竖着**绿色的药瓶（2–3 档亮绿）和铜色的尖刺**（铜 3 档）；肩膀上一块铜色的圆片。
- **胳膊**：两条长胳膊垂在身前，**铜色的护臂**（3 档，近侧那只嵌着两管绿色药剂），手是蓝紫色的，**深色的长爪子**（亮边）张开。
- **下身**：**橄榄色短工装裤**（3 档）和皮带（铜扣、两颗白色的牙挂饰）；蓝紫色的反关节狼腿，脚上深色的爪子，两只脚踩在地面线上。
- **尾巴**：又长又蓬的深蓝色尾巴，从屁股后面**往后上方翘起、尾巴尖不碰地**（和 A 一样）。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的格雷福斯、薇古丝——**和沃里克同一个密度 PPU 1.5**——以及沃利贝尔、内瑟斯；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画血雾、爪痕、发光）。

## 附图（压缩包 `warwick_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | A 缩到游戏格子数、每格 12 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 尖刺顶端，蓝 = 眼睛，红 = 地面 | 对齐网格、69 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 耳朵、眼睛、牙、嘴、鬃毛 |
| `style/7_style_graves.png` … `10_style_nasus.png` | 本包的格雷福斯、薇古丝（同密度）、沃利贝尔、内瑟斯，8 倍放大 | **只看风格**：这么粗的格子里毛、脸、眼睛、金属、深色的亮边怎么画 |

## 提示词：`warwick-model-A-1.png`、`warwick-model-A-2.png`、`warwick-model-A-3.png`（3/4 正面，三稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a hunched werewolf: blue-violet fur, a shaggy white mane on his chest and cheeks, huge pointed ears (pink inside), a snarling open jaw with white fangs and a red mouth, yellow eyes; a green glowing vial with a copper spike standing up behind his neck; copper gauntlets on both forearms (green vials in the near one), long dark claws; olive cargo shorts with a belt; digitigrade wolf legs; a long bushy dark blue tail lifted off the ground - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 69 squares from the tip of the spike to his soles, about 94 squares wide with the tail - shown with 12 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the eyes, the fangs, the mouth, the mane and the vials are specks); 3 the same with grid lines every 5 squares: green = the tip of the spike, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel (7 and 8 at this same square density) - how fur, a face, eyes, metal and the lit edges of dark colours are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 12 px, aligned on one straight grid from the canvas corner; the tip of the spike at y 348, the eyes at about y 696, both soles on y 1176 - exactly 69 squares from the tip of the spike to the soles, about 94 squares wide, placed as in image 2. Every detail drawn with whole 12 px squares, never with smaller pixels.
With only 69 squares make every part READ: the two HUGE POINTED EARS (blue-violet fur, pink inside in 2 shades); the white mane on the face in 2-3 shades (white, pale blue-grey); TWO YELLOW EYES, each at least 2 squares, at the SAME height, both visible; the dark nose; the OPEN JAW - the red mouth, the pink tongue, upper and lower WHITE FANGS (each at least 1 square); two or three dark red scars on the brow; the blue-violet fur in 3-4 shades (light blue edges, deep indigo shadows - never one black mass), the big white mane on the chest and throat; the GREEN VIAL (2-3 bright greens) and the COPPER SPIKE (3 shades) standing up behind the neck, a round copper plate on the shoulder; the two long arms hanging in front with COPPER GAUNTLETS (3 shades, two green vials in the near one), blue-violet hands and LONG DARK CLAWS with lighter edges, open; the OLIVE CARGO SHORTS in 3 shades with the belt (a copper buckle, two white fang charms); the blue-violet digitigrade wolf legs and dark clawed feet, both on the ground line; the long bushy dark blue TAIL rising behind his hips back and up, its tip well above the ground (never on the ground).
THE POSE as image 1: hunched forward, the head pushed out in front of the shoulders, the arms hanging in front with the claws open, feet apart and knees bent; 3/4 view facing right (the face to the front-right), the NEAR side in front in full tone, the FAR side a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no blood mist, no claw trails, no glow), no background, no ground, no shadow, no text, no grid lines. Make three takes.
```

## 交回前请检查

- **三张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 12 px**：尖刺顶端 y 348、脚底 y 1176，**尖刺顶端到脚底正好 69 格**（数一下台阶数：**如果是 100 格以上就是格子画小了，请重画**）。
- 3/4 正面朝右；两只黄眼睛一样高、看得见；张开的嘴里有白牙；白鬃毛分档；铜护臂、绿药剂、铜尖刺；橄榄色短裤；尾巴不碰地；外描边连续；没有任何特效。

## 交付（`outputs/warwick-model/`）

- `warwick-model-A-1.png`、`warwick-model-A-2.png`、`warwick-model-A-3.png`；原始生成图原样放 `outputs/warwick-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/warwick_model_done.zip`。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px、尖刺顶端到脚底 69 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在 12 倍下查脸（**优先用 Codex 原本画的脸，不要自己把脸重画成方块**——薇古丝的教训），在游戏大小下和格雷福斯、薇古丝并排自查（PPU 1.5，46 游戏像素），给用户挑一张。
- 动作（用户：「不做侧面 只做四分之三的侧面」）都在这张 3/4 造型上摆：英雄联盟的 Attack1–4（挥爪）、Q Spell1（扑咬）、E Spell3 / Spell3_Howl（缩身护体 / 仰头嚎叫）、R Spell4Dash / Spell4Hit（扑过去压住、连抓）、跑 run_base、死亡 Death。尾巴在待机和走路时不碰地；所有帧同一张脸；腿和待机一致、不变形。
