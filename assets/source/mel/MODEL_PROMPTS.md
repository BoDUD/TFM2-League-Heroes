# 流光镜影 梅尔：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（长袍拖尾的待机）**（`1_picture_A.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把她画成**游戏里的格子数**：**从发髻顶端到脚底 66 格**，连拖尾约 59 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、嘴、额饰、耳环、护甲片、袍子的金边碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **只画 3/4 正面朝右**（和 A 一样；**不画侧面**）：游戏里的待机，所有动作也都从这张图来做。
> - **每格画大：16 px 一格**。画布用你平时的 **1254 × 1254**：**发髻顶端 y = 128，眼睛约 y = 416，脚底 y = 1184**。每一格都是 16 × 16 px 的方块，不要用更小的格子画细节。**画三稿。**

## 大小和位置（照 `2_target.png` / `3_layout.png`）

- 画布 **1254 × 1254**，**每格 16 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **发髻顶端 y = 128**（绿线），**眼睛约 y = 416**（蓝线），**脚底 y = 1184**（红线）：发髻顶端到脚底 **66 格**。
- 宽约 59 格（拖尾的左端到伸出去的那只手），放在 `2_target.png` 的位置。

## 在 66 格里要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍）：**高高的黑色卷发髻**（深棕亮边 3 档，一团团的卷，不要糊成一块黑），发髻上**金色和银色的发饰**；额头上**金色的额饰**；深棕色的脸（3 档，暖色亮面）；**两只眼睛：每只至少 2 格，一样高，都看得见**（白眼珠 + 深棕瞳孔 + 一格高光），细眉毛；深红色的嘴唇；**很大的金色圆耳环**（两只都看得见）；**金色的项圈**。
- **身体**：**青绿色的紧身连体衣**（3–4 档），胸口和腰上**银白色的尖角护甲片**（2–3 档），肩上一对青绿色带银边的小肩甲。
- **胳膊**：近侧的手**叉在腰上**，远侧的手臂**向前伸出、手心朝上**（不画光）；**深红色的喇叭袖**（外红内金，3 档）垂下来。
- **长袍**：深红色（3–4 档），**金色的衬里和金边**，**深蓝黑色的滚边**（2 档）；袍子从腰后垂下，**在她身后（画面左边）铺成一条拖尾**，拖尾贴着地面线。
- **腿**：青绿色的紧身裤，**银青色的高跟鞋**，两只脚踩在地面线上（站得比较并拢）。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的莫甘娜、卡尔萨斯、迦娜——**和梅尔同一个密度 PPU 1.5**——以及乐芙兰；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（手上不画光、不画金色飞弹）。

## 附图（压缩包 `mel_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | A 缩到游戏格子数、每格 16 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 发髻顶端，蓝 = 眼睛，红 = 地面 | 对齐网格、66 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 发髻、发饰、额饰、眼睛、嘴、耳环 |
| `style/7_style_morgana.png` … `10_style_leblanc.png` | 本包的莫甘娜、卡尔萨斯、迦娜（同密度）、乐芙兰，8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、头发、长袍、金边、深色的亮边怎么画 |

## 提示词：`mel-model-A-1.png`、`mel-model-A-2.png`、`mel-model-A-3.png`（3/4 正面，三稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a tall noblewoman mage with deep brown skin; black curly hair in a high updo with gold and silver ornaments, a gold forehead piece, big gold hoop earrings and a gold collar; a fitted teal-green bodysuit with pointed silver-white plates on the chest and waist, small teal shoulder pieces; a long crimson robe with a gold lining, gold trim and a dark navy hem, wide crimson bell sleeves, the robe lying on the ground behind her as a train; teal leggings and silver-teal high heels; one hand on her hip, the other arm reaching forward palm up - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 66 squares from the top of the bun to her soles, about 59 squares wide with the train - shown with 16 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the eyes, the mouth, the forehead piece, the earrings, the plates and the robe's gold trim are specks); 3 the same with grid lines every 5 squares: green = the top of the bun, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel (7, 8 and 9 at this same square density) - how a face, eyes, hair, a robe, gold trim and the lit edges of dark colours are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 16 px, aligned on one straight grid from the canvas corner; the top of the bun at y 128, the eyes at about y 416, both soles on y 1184 - exactly 66 squares from the top of the bun to the soles, about 59 squares wide, placed as in image 2. Every detail drawn with whole 16 px squares, never with smaller pixels.
With only 66 squares make every part READ: the HIGH BLACK CURLY UPDO in 3 shades (dark brown lit edges, round curls - never one black mass) with gold and silver ornaments; the GOLD FOREHEAD PIECE; the deep brown face in 3 shades (warm light side); TWO EYES, each at least 2 squares (white, a dark brown iris, one highlight square), at the SAME height, both visible, thin brows; dark red lips; the BIG GOLD HOOP EARRINGS, both visible; the GOLD COLLAR; the TEAL-GREEN BODYSUIT in 3-4 shades with the pointed SILVER-WHITE PLATES (2-3 shades) on the chest and waist, small teal shoulder pieces with silver edges; the near hand ON HER HIP, the far arm REACHING FORWARD palm up (no light in it); the wide CRIMSON BELL SLEEVES (red outside, gold inside, 3 shades); the CRIMSON ROBE in 3-4 shades with its GOLD LINING and GOLD TRIM and the DARK NAVY HEM (2 shades), falling from her waist and lying on the ground behind her (to the image left) as a TRAIN along the ground line; the teal leggings and SILVER-TEAL HIGH HEELS, both feet on the ground line, close together.
THE POSE as image 1; 3/4 view facing right (the face to the front-right), the NEAR side in front in full tone, the FAR side a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no light in her hand, no golden bolts, no glow), no background, no ground, no shadow, no text, no grid lines. Make three takes.
```

## 交回前请检查

- **三张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px**：发髻顶端 y 128、脚底 y 1184，**发髻顶端到脚底正好 66 格**（数一下台阶数：**如果是 90 格以上就是格子画小了，请重画**）。
- 3/4 正面朝右；两只眼睛一样高、看得见；额饰、大耳环、项圈清楚；青绿连体衣和银白护甲；红袍金边、深蓝黑滚边、拖尾贴地；一只手叉腰、一只手前伸；外描边连续；没有任何特效。

## 交付（`outputs/mel-model/`）

- `mel-model-A-1.png`、`mel-model-A-2.png`、`mel-model-A-3.png`；原始生成图原样放 `outputs/mel-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/mel_model_done.zip`。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、发髻顶端到脚底 66 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在 12 倍下查脸（**优先用 Codex 原本画的脸，不要自己把脸重画成方块**——薇古丝的教训），在游戏大小下和莫甘娜、卡尔萨斯、乐芙兰并排自查（PPU 1.5，44 游戏像素），给用户挑一张。
- 动作（用户：只做 3/4、「我自己照英雄联盟摆」）都在这张 3/4 造型上摆：英雄联盟的 Attack1 / Attack2-new（施法普攻）、Q Spell1（耀光齐射）、E Spell3（阳炎涡旋）、R Spell4（鎏金蚀日）、W Spell2（灵魂折镜，给附加包或普攻里的屏障用）、跑 Run、死亡 Death。拖尾在跑步时跟着身后拖动；所有帧同一张脸；腿和待机一致、不变形。
