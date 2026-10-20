# 解脱者 塞拉斯：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（长锁链的待机）**（`1_picture_A.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把他画成**游戏里的格子数**：**从头顶到脚底 46 格**，连两边的锁链约 66 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、胡子、金色护颈片、镣铐的金边、锁链的链环碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **只画 3/4 正面朝右**（和 A 一样；**不画侧面**）：游戏里的待机，所有动作也都从这张图来做。
> - **每格画大：16 px 一格**。画布用你平时的 **1254 × 1254**：**头顶 y = 432，眼睛约 y = 560，脚底 y = 1168**。每一格都是 16 × 16 px 的方块，不要用更小的格子画细节。**画三稿。**

## 大小和位置（照 `2_target.png` / `3_layout.png`）

- 画布 **1254 × 1254**，**每格 16 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **头顶 y = 432**（绿线），**眼睛约 y = 560**（蓝线），**脚底 y = 1168**（红线）：头顶到脚底 **46 格**。
- 宽约 66 格（左边拖在地上的锁链到右边那只镣铐的锁链），放在 `2_target.png` 的位置。

## 在 46 格里要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍）：头约 10 格高。黑色的长发往后梳（2–3 档，亮边偏蓝紫），几缕垂在脸旁；**两只眼睛：每只至少 1 格白 + 1 格深色瞳孔，一样高，都看得见**；浓眉一格深色；**短黑胡子**（下巴和两颊，和皮肤分得清）；暖色皮肤 2–3 档。
- **身体**：赤裸的上身，暖肤色 3 档（暗处红棕，**不要灰**），胸肌、腹肌用一两格暗色点出来；近侧肩头一个**暗红色的菱形烙印**（2–3 格）；脖子上**深青灰色的高领围巾**（3 档），胸前一块**金色护颈片**（亮金、金、暗金 3 档）和一个**深灰的菱形坠子**。
- **镣铐**：两只前臂上**很大的白色石头镣铐**（白、浅灰、灰 3 档，**带金边**），比拳头还大，是他身上最显眼的东西；拳头露在镣铐下面。
- **锁链**：从两只镣铐垂下来的**金色大方链**（3 档金），**一个链环至少 2 × 2 格、中间有一格空洞**，看得出一环扣一环；近侧那条拖在地上往左后方伸出去，远侧那条垂到地上在脚边绕一下（和 A 一样）。
- **下身**：宽的**棕色皮带**（铜扣），扣子两边垂下**青色的布片**；**深青绿色的长裤**（3 档），小腿裹着灰布；**赤脚**，脚趾一格肤色，两只脚踩在地面线上。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的沃里克——**和塞拉斯同一个密度 PPU 1.2**——以及格雷福斯、德莱厄斯、杰斯；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画蓝色的魔法、闪电、锁链的光）。

## 附图（压缩包 `sylas_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | A 缩到游戏格子数、每格 16 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 头顶，蓝 = 眼睛，红 = 地面 | 对齐网格、46 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 头发、眼睛、胡子、围巾、护颈片 |
| `style/7_style_warwick.png` … `10_style_jayce.png` | 本包的沃里克（同密度）、格雷福斯、德莱厄斯、杰斯，8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、胡子、金属和石头的亮边怎么画 |

## 提示词：`sylas-model-A-1.png`、`sylas-model-A-2.png`、`sylas-model-A-3.png`（3/4 正面，三稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a lean, muscular, bare-chested man: long black hair swept back with a few strands by his face, a short black beard, warm skin, a dark red diamond-shaped brand on his near shoulder; a high dark teal-grey scarf round his neck with a gold neck plate and a dark diamond pendant on his chest; huge white stone manacles with gold trim on both forearms and heavy gold square-link chains hanging from them to the ground; a wide brown belt with teal cloth flaps, dark teal-green trousers, grey shin wraps, bare feet - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 46 squares from the top of his head to his soles, about 66 squares wide with the chains - shown with 16 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the eyes, the beard, the gold plate, the manacles' trim and the chain links are specks); 3 the same with grid lines every 5 squares: green = the top of the head, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel (7 at this same square density) - how a face, eyes, a beard, metal and stone are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 16 px, aligned on one straight grid from the canvas corner; the top of the head at y 432, the eyes at about y 560, both soles on y 1168 - exactly 46 squares from the top of the head to the soles, about 66 squares wide, placed as in image 2. Every detail drawn with whole 16 px squares, never with smaller pixels.
With only 46 squares make every part READ: the black hair swept back in 2-3 shades (blue-violet lit edges); TWO EYES, each at least 1 white square and 1 dark pupil square, at the SAME height, both visible; a dark brow; the SHORT BLACK BEARD on the chin and cheeks, clearly apart from the skin; warm skin in 3 shades (red-brown shadows, never grey) with the chest and stomach muscles marked by a few darker squares; the dark red diamond brand on the near shoulder; the dark teal-grey high scarf (3 shades), the GOLD NECK PLATE (bright gold, gold, dark gold) and the dark grey diamond pendant; the two HUGE WHITE STONE MANACLES (white, light grey, grey) with GOLD TRIM, bigger than his fists, the fists showing below them; the GOLD CHAINS (3 golds) with links at least 2x2 squares each with a 1-square hole, link hooked into link: the near chain lies on the ground trailing out to the left behind him, the far chain hangs to the ground by his feet; the wide brown belt with a copper buckle and the teal cloth flaps; the dark teal-green trousers (3 shades), grey shin wraps, bare feet with skin-coloured toes on the ground line.
THE POSE as image 1: feet apart and planted, knees a little bent, both manacled hands hanging at his sides with the fists closed; 3/4 view facing right (the face to the front-right), the NEAR side in front in full tone, the FAR side a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no blue magic, no lightning, no glow on the chains), no background, no ground, no shadow, no text, no grid lines. Make three takes.
```

## 交回前请检查

- **三张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px**：头顶 y 432、脚底 y 1168，**头顶到脚底正好 46 格**（数一下台阶数：**如果是 60 格以上就是格子画小了，请重画**）。
- 3/4 正面朝右；两只眼睛一样高、看得见；黑胡子；白石镣铐带金边；金链一环一环看得清；深青绿长裤、棕皮带；外描边连续；没有任何特效。

## 交付（`outputs/sylas-model/`）

- `sylas-model-A-1.png`、`sylas-model-A-2.png`、`sylas-model-A-3.png`；原始生成图原样放 `outputs/sylas-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/sylas_model_done.zip`。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、头顶到脚底 46 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在 12 倍下查脸（**优先用 Codex 原本画的脸**），在游戏大小下和沃里克（同 PPU 1.2）、格雷福斯并排自查（38 游戏像素），给用户挑一张。
- 动作：用户选「Codex 照骨架画关键姿势」（沃里克 pack_warwick_poses.py 的做法：骨架线 + 造型的头作样本，量好的四肢长度），都在这张 3/4 造型上；所有帧同一张脸；腿和待机一致、不变形（codex-legs-need-skeletons）。英雄联盟的动作（`tools/lol/anim_graph.py Sylas`）：普攻 Sylas_Attack_01 / 02（甩链）、被动 Sylas_Attack_Passive（转身挥链一圈）、W Sylas_Spell2（跃起突刺）、Q Sylas_Spell1_Cast（双手甩链交叉）、E Sylas_Spell3_Dash（冲刺）+ Sylas_Spell3_Bhit_Cast（甩链拉过去）、R Sylas_Spell4_Cast（甩链偷大招）、跑 Sylas_Run、死亡 Sylas_Death。
