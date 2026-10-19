# 暮光星灵 佐伊：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（待机）**（`1_picture_A.png`）**用户选定了，样子、颜色全照它**；`1_picture_B.png`（站直）只用来看手臂垂下时手和手镯的样子。
> - 这一步要把她画成**游戏里的格子数**：**从发髻顶到脚底 53 格**。我把 A 直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、彩带、手镯碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大：19 px 一格，人物撑满画布**。画布用你平时的 **1254 × 1254**：**发髻顶 y = 190，两只脚底 y = 1197**。每一格都是 19 × 19 px 的大方块，不要用更小的格子画细节。
> - 一共画**两种**（同一个佐伊、同样的格子、同样的颜色）：**A 待机（3/4 正面）**、**S 侧面朝右**，各画**两稿**。

## 大小和位置

- 画布 **1254 × 1254**，**每格 19 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A**：照 `2_target_A.png` / `3_layout_A.png`：发髻顶 **y = 190**（橙线），眼睛约 **y = 513**（蓝线），脚底 **y = 1197**（红线）：**53 格高、约 62 格宽**（头发向画面左边飘出去占了一半宽）。
- **S**：同样 **53 格高**（发髻顶 y = 190、脚底 y = 1197），**侧面朝右**：`3_side_ref.png` 是英雄联盟模型的侧面按这个格子数摆好的（淡色，只看**轮廓、位置和大小**，约 46 格宽；模型这一帧仰得很厉害，**你画的 S 身子要直一些**，见下面）。
- 全在画布里，头发、手、脚不出画，四周留至少 1 格空。

## 在 53 格里要画清楚的地方

- **脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：圆脸，暖肉色，两颊各一点粉；**两只大眼睛：每只约 3 × 4 格，一样高，画面左边那只紫罗兰色、右边那只浅蓝色，各带 1 格白色高光，上面一道深色眼线**；咧嘴笑，嘴里 1–2 格白牙；一只小耳朵。**S 里也是同一张脸**：**脸朝右前方、两只眼睛都看得见**（和 A 一样的脸，不要另画一个只有一只眼的侧脸）。
- **头发**：深藏青 3 档，头顶两个**圆鼓鼓的发髻**；头发里的**彩带**：青绿、金黄、珊瑚橙、粉红，每种 2 档、边清楚；几缕头发上套着**金色的发环**（2–3 档 + 1 格高光）。
- **身体**：**青绿色围巾**（2–3 档，一圈圈的条纹）；**深蓝短上衣**，露出肚子；**蓝色多层裹裙**，前面一块尖角垂下；深色短裤；腰上**金色圆扣**带一颗紫色小宝石；两只手腕**金手镯**；**深藏青护腿**（上面一圈金色小扣），光脚，脚趾肉色。
- **A 的姿势**和第 0 步的 A 一样：3/4 正面朝右，胯往前、上身微微后仰，两只手臂向身体两侧稍稍张开、手掌朝外，脸朝右前方笑，头发向身后（画面左边）飘出去；**近侧的腿（画面左边）颜色亮，远侧的腿（画面右边）稍暗**，两只脚都踩在地面线上。
- **S 的姿势**：**完全侧面、朝右**，**身子直立**（只比直立往后仰一点点），头上是和 A 一样朝右前方的脸；**头发从脑后向画面左边飘出去**（和 A 一样长、一样的彩带）；**近侧的手臂自然垂在身体前侧（画面右边一点）**，手和手镯清楚，**手臂外面一圈描边、和身体分开**；远侧手臂只露一点、稍暗；**两条腿一前一后**站在地面线上，脚尖朝右。所有动作都从这张画出来，所以手臂、腿、头发都要清楚地分开。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的迦娜、娜美、卡特琳娜，**和佐伊同一个密度 PPU 1.5**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效、道具。

## 附图（压缩包 `zoe_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1_picture_B.png` | 你第 0 步画的 B（站直） | 只看手臂垂下时手、手镯的样子（S 的近侧手臂） |
| `2_target_A.png` | A 缩到游戏格子数、每格 19 px 放在画布上（细节是坏的） | A 的**大小、位置、比例、姿势** |
| `3_layout_A.png` | A 加网格线：橙 = 发髻顶，蓝 = 眼睛，红 = 地面 | 对齐网格、53 格的高度、地面线 |
| `3_side_ref.png` | 英雄联盟模型的侧面，按格子数摆好（淡色） | **S** 的轮廓、位置、大小（身子画直一些） |
| `4_head.png` | 第 0 步读回的头部（8 倍） | 发髻、脸、一紫一蓝的眼睛、围巾 |
| `style/5_style_janna.png` … `7_style_katarina.png` | 本包的迦娜、娜美、卡特琳娜（同密度），8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、头发、金饰怎么画 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A your own earlier pixel-art drawing of this character - a small cheerful chibi girl with a huge mane of long dark-navy hair woven with ribbons of teal, gold, coral-orange and pink, two round buns on top, gold rings round some strands, the hair streaming far behind her; a round face with big eyes of two colours (the image-left eye violet, the image-right eye light blue) and a wide grin; a teal striped scarf, a dark-blue crop top, a blue layered wrap skirt with a pointed front flap over dark shorts, a round gold buckle with a small purple gem, gold bangles on both wrists, dark-navy leg warmers with little gold studs over bare feet (her idle, 3/4 view facing right, the arms a little out with open palms) - its LOOK and COLOURS are approved, but it is drawn with far too many small squares; 1B the same girl standing with her arms hanging (only to see the hanging arm, hand and bangle); 2A image 1A cut down to the RIGHT square count - 53 squares from the top of her buns to her soles - shown with 19 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details; 3A the same with grid lines every 5 squares: orange = the top of the buns, blue = the eyes, red = the ground; 3-side: the game's 3D model at the same count (faded) seen from the side - only its OUTLINE, PLACE and SIZE; 4 the head of image 1A enlarged; 5-7 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - how a face, eyes, long hair and gold jewellery are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 19 px, aligned on one straight grid from the canvas corner; the top of the buns at y 190 and the soles on y 1197 - exactly 53 squares tall, the figure filling the canvas with at least one empty square on every side. Every detail drawn with whole 19 px squares, never with smaller pixels.
With only 53 squares make every part READ: the round face in warm skin with a little pink on each cheek; TWO BIG EYES, each about 3x4 squares, at the SAME height, the image-left one VIOLET and the image-right one LIGHT BLUE, each with ONE white highlight square and a dark lash line above; a wide grin with one or two white tooth squares; the dark-navy hair in 3 shades with two round buns; the teal, gold, coral-orange and pink ribbons in the hair, each in 2 shades with clear edges; the gold hair rings with a highlight; the teal striped scarf; the dark-blue crop top; the blue layered skirt with its pointed front flap; the gold buckle with a purple gem; the gold bangles; the dark-navy leg warmers with gold studs; bare feet.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no props, no background, no ground, no shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`zoe-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  POSE A: her idle exactly as images 1A, 2A and 3A - 3/4 view facing right, the hips forward and the upper body leaning back a little, both arms held a little out from her sides with the open palms turned outward, grinning to the front-right, the hair streaming far back to the image left; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both feet on the ground line; about 62 squares wide.
  ```
- **S（`zoe-model-S-1.png`、`-S-2.png`，两稿）**：
  ```text
  POSE S: the SAME character SIDE-ON, FACING RIGHT (size and place of image 3-side, about 46 squares wide), standing UPRIGHT - leaning back only slightly, much less than the faded model; the head is the SAME head as in image 1A - turned to the front-right with BOTH eyes visible (violet on the image left, light blue on the image right; not a one-eyed profile); the hair streaming back from the back of her head to the image left, as long and with the same ribbons as in 1A; the NEAR arm hanging naturally a little in front of her body, hand and bangle clear, separated from the body by its own outline; the far arm only a little visible and a step darker; the two legs one in front of the other on the ground line, the feet pointing right.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 19 px 的大方块**：发髻顶 y 190、脚底 y 1197，**正好 53 格高**（数一下台阶数：**如果是 80–130 格就是格子画小了，请重画**）。
- 两只眼睛一样大、一样高、带高光，左紫右蓝（A、S 都是）；S 里是同一个朝右前方的头、两只眼睛都看得见；S 身子直立、头发往后飘、近侧手臂和身体分开；外描边连续；没有任何特效和道具。

## 交付（`outputs/zoe-model/`）

- `zoe-model-A-1.png`、`zoe-model-A-2.png`、`zoe-model-S-1.png`、`zoe-model-S-2.png`；原始生成图原样放 `outputs/zoe-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/zoe_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 19 px、53 行），从 raw/ 按格读回（regrid），在游戏大小下和迦娜、娜美、卡特琳娜、辛德拉、拉克丝并排自查（PPU 1.5，35 游戏像素），把 A / S 的两稿给用户挑。
- 动作帧自己摆（`rig_zoe.py`，照 rig_rammus.py / rig_volibear.py：只整格平移、绕半格点的四分之一转、镜像），脸用 A 的同一张 3/4 脸。每个动作对照英雄联盟（`tools/lol/anim_graph.py Zoe`、`pose_ref.py`，渲染要 `--hide-submesh` 掉跳绳、球拍、溜溜球、冰淇淋）：普攻 Zoe_attack1 / Attack2 / Attack3，强化普攻 Zoe_Empowered_Attack（`attack_p`）；Q Spell1；E Zoe_Spell3（踢出气泡）；R Zoe_Spell2（跳进传送门）、`ult_back`（从传送门回来）；跑 Zoe_Run1；死亡 Zoe_Death（8 帧带回弹）；挨打第 1 帧闪白后退。自查到完美（8 倍逐帧：不挡脸、不错切、不留透光缝）再给用户审。
