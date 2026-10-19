# 爆爆（金铲铲之战 · 双城之战）：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图缩小、最近邻取样来凑格子。**
> - 第 0 步你画的 **A（待机）**（`1_picture_A.png`）**用户选定了，样子、颜色全照它**；`1_picture_B.png`（站直）只用来看手臂垂下时手和护臂的样子。
> - 这一步要把她画成**游戏里的格子数**：**从头顶到脚底 53 格**。我把 A 直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、发夹、炸弹袋碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大：22 px 一格，人物撑满画布高度**。画布用你平时的 **1254 × 1254**：**头顶 y = 44，两只脚底 y = 1210**。每一格都是 22 × 22 px 的大方块，不要用更小的格子画细节。
> - 一共画**两种**（同一个爆爆、同样的格子、同样的颜色）：**A 待机（3/4 正面）**、**S 侧面朝右**，各画**两稿**。

## 大小和位置

- 画布 **1254 × 1254**，**每格 22 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A**：照 `2_target_A.png` / `3_layout_A.png`：头顶 **y = 44**（橙线），眼睛约 **y = 374**（蓝线），脚底 **y = 1210**（红线）：**53 格高、约 34 格宽**（伸出去的手占了右边几格）。
- **S**：同样 **53 格高**（头顶 y = 44、脚底 y = 1210），**侧面朝右**：`3_side_ref.png` 是金铲铲模型的侧面按这个格子数摆好的（淡色，只看**轮廓、位置和大小**，约 14–18 格宽；模型这一帧一只手抬到脸前，**你画的 S 两只手臂要垂下来**，见下面）。
- 全在画布里，头发、手、脚不出画，四周留至少 1 格空。

## 在 53 格里要画清楚的地方

- **脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：圆脸，浅肉色，两颊各一点粉；**两只大眼睛：每只约 3 × 4 格，一样高，蓝色眼珠，各带 1 格白色高光，上面一道深色眼线**，两道深棕色细眉毛；小嘴 1–2 格。**S 里也是同一张脸**：**脸朝右前方、两只眼睛都看得见**（和 A 一样的脸，不要另画一个只有一只眼的侧脸）。
- **头发**：亮蓝色 3–4 档，乱蓬蓬的短发，发梢一缕缕翘着；两条小辫子从耳后垂到肩下，辫梢扎一格金色小绳；**两个金色 X 形发夹**（亮金、金、暗金 3 档）在头顶两侧，形状清楚。
- **身体**：**青绿色上衣**（3 档，下摆盖到大腿），**粉色条纹短袖**露在袖口；两条小臂缠着**深棕色护臂**，手指露出来；腰上**棕色皮带**、**银色带扣**；胯边**棕色皮袋，袋口露出 3–4 颗蓝色小炸弹**（2–3 档 + 1 格高光，不要光晕）；**棕色短裤**；**紫色裤袜**（可以有一两道深一档的条纹）；**棕色系带短靴**（3 档，鞋底深一档）。
- **A 的姿势**和第 0 步的 A 一样：3/4 正面朝右，一只手抬到下巴前，另一只手向画面右边伸出去、掌心朝上；**近侧的腿（画面左边）颜色亮，远侧的腿（画面右边）稍暗**，两只脚都踩在地面线上。
- **S 的姿势**：**完全侧面、朝右**，**身子直立**，头上是和 A 一样朝右前方的脸；两条小辫子垂在脑后（画面左边）；**近侧的手臂自然垂在身体前侧（画面右边一点）**，手和护臂清楚，**手臂外面一圈描边、和身体分开**；远侧手臂只露一点、稍暗；皮袋在身后一侧（画面左边）露出来；**两条腿一前一后**站在地面线上，脚尖朝右。所有动作都从这张画出来，所以手臂、腿、辫子都要清楚地分开。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本系列借用画风的佐伊、迦娜、卡特琳娜，**和爆爆同一个密度 PPU 1.5**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明；**不要黑底、不要光晕**（第 0 步的 B 画在黑底上带了一圈蓝光，这次不要）。不要网格线、文字、边框、影子、地面、特效、道具（手里什么都不拿）。

## 附图（压缩包 `powder_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1_picture_B.png` | 你第 0 步画的 B（站直） | 只看手臂垂下时手、护臂的样子（S 的近侧手臂） |
| `2_target_A.png` | A 缩到游戏格子数、每格 22 px 放在画布上（细节是坏的） | A 的**大小、位置、比例、姿势** |
| `3_layout_A.png` | A 加网格线：橙 = 头顶，蓝 = 眼睛，红 = 地面 | 对齐网格、53 格的高度、地面线 |
| `3_side_ref.png` | 金铲铲模型的侧面，按格子数摆好（淡色） | **S** 的轮廓、位置、大小（手臂按文字垂下） |
| `4_head.png` | 第 0 步读回的头部（8 倍） | 头发、两个 X 形发夹、脸、眼睛、小辫子 |
| `style/5_style_zoe.png` … `7_style_katarina.png` | 佐伊、迦娜、卡特琳娜（同密度），8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、头发、金属件怎么画 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A your own earlier pixel-art drawing of this character - a small chibi girl with bright blue messy short hair, two thin braids hanging behind, two big gold X-shaped hair clips, a round face with big blue eyes, a teal tunic with short pink striped sleeves, dark brown fingerless arm wraps, a brown belt with a silver buckle, a brown pouch on her hip full of small blue bombs, brown shorts, purple tights and brown laced boots (her idle, 3/4 view facing right, one hand at her chin, the other held out palm up) - its LOOK and COLOURS are approved, but it is drawn with far too many small squares; 1B the same girl standing with her arms hanging (only to see the hanging arm, hand and arm wrap); 2A image 1A cut down to the RIGHT square count - 53 squares from the top of her head to her soles - shown with 22 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details; 3A the same with grid lines every 5 squares: orange = the top of the head, blue = the eyes, red = the ground; 3-side: the game's 3D model at the same count (faded) seen from the side - only its OUTLINE, PLACE and SIZE; 4 the head of image 1A enlarged; 5-7 STYLE ONLY: other characters drawn in the same style at this same square density, shown 8x so every square is one pixel - how a face, eyes, hair and metal parts are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255, no dark backdrop, no glow). BIG SQUARES: every square exactly 22 px, aligned on one straight grid from the canvas corner; the top of the head at y 44 and the soles on y 1210 - exactly 53 squares tall, at least one empty square on every side. Every detail drawn with whole 22 px squares, never with smaller pixels; do not draw big and shrink.
With only 53 squares make every part READ: the round face in light warm skin with a little pink on each cheek; TWO BIG EYES, each about 3x4 squares, at the SAME height, blue, each with ONE white highlight square and a dark lash line above, thin dark brown eyebrows; a small mouth; the bright blue hair in 3-4 shades with tufts sticking out; the two thin braids with a gold tie at each end; the two gold X clips in 3 shades with clear shapes; the teal tunic in 3 shades; the pink striped short sleeves; the dark brown arm wraps with the fingers showing; the brown belt with a silver buckle; the brown pouch with 3-4 small blue bombs showing (2-3 shades and one highlight, no glow); the brown shorts; the purple tights; the brown laced boots with darker soles.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, nothing in her hands, no background, no ground, no shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`powder-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  POSE A: her idle exactly as images 1A, 2A and 3A - 3/4 view facing right, one hand raised to her chin as if thinking, the other arm held out to the image right with the open palm turned up, the legs a little apart; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both feet on the ground line; about 34 squares wide.
  ```
- **S（`powder-model-S-1.png`、`-S-2.png`，两稿）**：
  ```text
  POSE S: the SAME character SIDE-ON, FACING RIGHT (size and place of image 3-side, about 16-20 squares wide), standing UPRIGHT; the head is the SAME head as in image 1A - turned to the front-right with BOTH eyes visible (not a one-eyed profile); the two braids hanging behind her head to the image left; BOTH ARMS DOWN: the NEAR arm hanging naturally a little in front of her body, hand and arm wrap clear, separated from the body by its own outline; the far arm only a little visible and a step darker; the pouch with the blue bombs at her hip on the image left; the two legs one in front of the other on the ground line, the boots pointing right.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**，没有黑底和光晕。
- **每格 22 px 的大方块**：头顶 y 44、脚底 y 1210，**正好 53 格高**（数一下台阶数：**如果是 80–130 格就是格子画小了，请重画**）。
- 两只眼睛一样大、一样高、带高光（A、S 都是）；S 里是同一个朝右前方的头、两只眼睛都看得见；S 身子直立、两只手臂垂下、近侧手臂和身体分开、两腿一前一后；两个金色 X 发夹、两条小辫子、蓝色小炸弹袋都在；外描边连续；没有任何特效和道具。

## 交付（`outputs/powder-model/`）

- `powder-model-A-1.png`、`powder-model-A-2.png`、`powder-model-S-1.png`、`powder-model-S-2.png`；原始生成图原样放 `outputs/powder-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/powder_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 22 px、53 行），从 raw/ 按格读回（regrid），在游戏大小下和佐伊、安妮、波比、金克丝并排自查（PPU 1.5，35 游戏像素），把 A / S 的两稿给用户挑。
- 动作帧自己摆（`rig_powder.py`，照 rig_zoe.py / rig_rammus.py：只整格平移、绕半格点的四分之一转、镜像），脸用 A 的同一张 3/4 脸；缺的姿势（尤其腿）出部件包，腿给骨架（codex-legs-need-skeletons）。每个动作对照金铲铲（`pose_ref.py --champ TFT13_Blue --wad-file TFTSet13.wad.client`，渲染要 `--hide-submesh Bomb --hide-submesh Monkey`）：普攻 attack_1 / attack_2（扔小鞭炮）；技能 Spell（蹲下点燃、扔出猴子炸弹，给 Q 和 R）；E 的摔烟雾弹 + 后跳自己设计；跑 Run；死亡 Death（8 帧）；挨打第 1 帧闪白后退。自查到完美（8 倍逐帧：不挡脸、不错切、不留透光缝、腿不变形）再给用户审，审查只发一张合成 GIF。
