# 龙血武姬 希瓦娜：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的四张（`1_picture_A.png` 人形 3/4、`1_picture_D.png` 龙形 3/4、`1_picture_SA.png` 人形侧面、`1_picture_SD.png` 龙形侧面）**样子、颜色用户认可了，全照它们**。
> - 这一步要把她画成**游戏里的格子数**：**人形从角尖到脚底 63 格**，**龙形从最高的翼尖到爪底 72 格**。我把四张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、角、牙齿、金边碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，四张的格子大小不一样（为了都撑满画布）：**A 和 SA 每格 17 px**，**D 每格 10 px**，**SD 每格 8 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**六张**（同一个希瓦娜、同样的颜色）：**A 两稿**（A-1 / A-2）、**D 两稿**（D-1 / D-2）、**SA 一稿**、**SD 一稿**。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（人形 3/4）**：每格 **17 px**；照 `2_target_A.png` / `3_layout_A.png`：角尖 **y = 119**（橙线），眼睛约 **y = 357**（蓝线），脚底 **y = 1190**（红线）：**63 格高、约 42 格宽**。
- **D（龙形 3/4）**：每格 **10 px**；照 `2_target_D.png` / `3_layout_D.png`：最高的翼尖 **y = 460**，眼睛约 **y = 930**，爪底 **y = 1180**：**72 格高、约 118 格宽**。
- **SA（人形侧面朝右）**：每格 **17 px**；照 `2_target_SA.png` / `3_layout_SA.png`：角尖 **y = 119**，眼睛约 **y = 391**，脚底 **y = 1190**：**63 格高、约 34 格宽**。
- **SD（龙形侧面朝右）**：每格 **8 px**；照 `2_target_SD.png` / `3_layout_SD.png`：最高的翼尖 **y = 608**，眼睛约 **y = 968**，爪底 **y = 1184**：**72 格高、约 137 格宽**。
- 全在画布里，角、尾巴、翅膀、爪子不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **人形的脸**（`4_head_human.png` 是第 0 步读回的头部，8 倍）：淡紫色的脸；**两只金黄色的眼睛：每只约 2 × 2 格，一样高、一样大**，各带 **1 格白色高光**；金橙色刘海；**深红色龙角冠**从额头两边往后扫（红色 3 档、角尖黑色），中间一道金色；**金橙色的长发**一绺一绺垂到背后。
- **人形的身体**：**青银色鳞片胸甲**（3 档）配**金边**（2 档）；肚子露出淡紫皮肤；前臂**深红布条**；**深紫红护腿**，膝盖和小腿上**银金色鳞片护甲**；**龙爪脚**踩在地面线上，**两条腿之间要有空隙和描边分开**；身后**深红鳞片长尾巴**（3–4 档）弯到地面附近、**尾尖金色**；肩上小金刺。
- **龙的头**（`4_head_dragon.png`）：深红色长吻，**一只发光的黄色眼睛**（约 2 × 2 格）清楚可见；嘴微张，**一排象牙色尖牙**（一颗颗分开）、紫色的嘴里；头顶和脖子上**橙黄色火焰鬃毛**（3 档、亮边偏白黄、一簇簇尖尖的）；深色的弯角。
- **龙的身体**：深红鳞片 3–4 档（**不要糊成一团红**，鳞片和肌肉用亮边分清）；**两只抬起的大翅膀**：翼骨金色 / 象牙色、翼膜深红、远处那只的翼膜里侧是深紫黑；背脊和肘上**象牙色尖刺**；胸前**青色护甲片**配金边；四条腿、**黑色爪子**，近处的腿全亮、远处的腿暗一档；**尾巴拖在身后**，尾尖金色。**D 和 SD 是同一头龙**：头、角、鬃毛、颜色一样。**A 和 SA 是同一个人**：脸、角冠、头发、颜色一样。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的梅尔、斯莫德、巨型纳尔，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `shyvana_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_D.png` / `1_picture_SA.png` / `1_picture_SD.png` | 你第 0 步画的四张（用户认可） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `2_target_D.png` / `2_target_SA.png` / `2_target_SD.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_D.png` / `3_layout_SA.png` / `3_layout_SD.png` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_human.png` / `4_head_dragon.png` | 第 0 步读回的两个头（8 倍） | 脸、眼睛、角冠、头发；龙的眼睛、牙、鬃毛 |
| `style/5_style_mel.png`、`6_style_smolder.png`、`7_style_gnar_mega.png` | 本包的梅尔、斯莫德、巨型纳尔，8 倍放大 | **只看风格**：这么粗的格子里女英雄的脸和身材、龙的鳞片和翅膀、大野兽的身体怎么画 |

## 提示词（四种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A, 1D, 1SA and 1SD your own earlier pixel-art drawings of one character in two forms - HUMAN (1A 3/4 view facing right, 1SA side-on facing right): a tall half-dragon warrior woman with pale lavender skin, long golden-orange hair, a crown of crimson dragon horns with black tips sweeping back, a teal-silver scale breastplate with gold trim, crimson cloth wraps on her forearms, dark plum leggings with silver-gold scale knee guards, clawed dragon feet and a long crimson scaly tail with a golden tip; DRAGON (1D 3/4 view facing right, 1SD side-on facing right): the same character as a big crimson dragon low on four clawed legs with two big raised bat wings (gold and ivory wing bones, crimson membrane, darker inside), a blazing orange-yellow flame mane on the head and neck, dark horns, ivory spikes on the spine and elbows, a teal chest plate with gold trim, black claws and a gold-tipped tail - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A, 2D, 2SA and 2SD the same pictures cut down to the RIGHT square count - the human 63 squares from her horn tips to her soles, the dragon 72 squares from its highest wing tip to its claws - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A, 3D, 3SA and 3SD the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the two heads enlarged (human, dragon); 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a heroine's face and figure, a dragon's scales and wings and a big beast's body are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ. HUMAN: her pale lavender face; TWO GOLDEN-YELLOW EYES, each about 2x2 squares, at the SAME height and the SAME size, each with 1 WHITE highlight square; golden-orange bangs; the crimson horn crown in 3 shades with black tips and a gold stripe; the long golden-orange hair tress by tress; the teal-silver breastplate in 3 shades with 2-shade gold trim; crimson forearm wraps; dark plum leggings with silver-gold scale guards; clawed feet with a clear gap and outline between her two legs; the crimson tail in 3-4 shades with a gold tip. DRAGON: the crimson scales in 3-4 shades with lit edges, never one red mass; ONE GLOWING YELLOW EYE about 2x2 squares; a row of separate ivory fangs and a purple mouth; the flame mane in 3 orange-yellow shades with PALE YELLOW LIT EDGES and sharp tufts; dark horns; the raised wings with gold-ivory bones and crimson membranes, the far wing's inside dark violet-black; ivory spikes; the teal chest plate with gold trim; black claws, the near legs in full tone and the far legs a step darker; the gold-tipped tail.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`shyvana-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: HER idle exactly as images 1A, 2A and 3A - she stands in 3/4 view facing right, the face to the front-right, both arms down at her sides, the tail curving behind her to the image left with its gold tip near the ground; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both clawed feet on the ground line. Every square exactly 17 px; her horn tips at y 119, her eyes at about y 357, her soles on y 1190 - exactly 63 squares tall, about 42 squares wide.
  ```
- **D（`shyvana-model-D-1.png`、`-D-2.png`，两稿）**：
  ```text
  PICTURE D: the DRAGON's idle exactly as images 1D, 2D and 3D - low on its four clawed legs in 3/4 view facing right, the head at the front (image right) with the eye and the fangs visible, both wings raised, the tail trailing behind to the image left. Every square exactly 10 px; its highest wing tip at y 460, its eye at about y 930, its claws on y 1180 - exactly 72 squares tall, about 118 squares wide.
  ```
- **SA（`shyvana-model-SA.png`，一稿）**：
  ```text
  PICTURE SA: the SAME woman as picture A exactly SIDE-ON, FACING RIGHT, as images 1SA, 2SA and 3SA - the face to the image right with one eye visible, the horn crown and hair the same as in A, the near arm in front, the tail behind her (image left), the near leg in full tone and the far leg a step darker and a little behind, both feet on the ground line. Every square exactly 17 px; her horn tips at y 119, her eye at about y 391, her soles on y 1190 - exactly 63 squares tall, about 34 squares wide.
  ```
- **SD（`shyvana-model-SD.png`，一稿）**：
  ```text
  PICTURE SD: the SAME dragon as picture D exactly SIDE-ON, FACING RIGHT, as images 1SD, 2SD and 3SD - the head at the front (image right) with one eye and the fangs, the flame mane along the neck, the near wing raised over the back and the far wing behind it, the near legs in full tone and the far legs a step darker and a little behind, all four on the ground line, the long tail behind (image left). The SAME head, horns, mane and colours as picture D. Every square exactly 8 px; its highest wing tip at y 608, its eye at about y 968, its claws on y 1184 - exactly 72 squares tall, about 137 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A、SA 每格 17 px、63 格高；D 每格 10 px、72 格高；SD 每格 8 px、72 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 人形：两只眼睛一样大、一样高、带白色高光；角冠、头发、胸甲金边、护腿、尾巴清楚；两条腿分开。A 和 SA 是同一个人。
- 龙形：眼睛看得清；尖牙一颗颗分开；鬃毛、翅膀、尖刺、胸甲清楚；D 和 SD 是同一头龙。外描边连续；没有任何技能特效。

## 交付（`outputs/shyvana-model/`）

- `shyvana-model-A-1.png`、`shyvana-model-A-2.png`、`shyvana-model-D-1.png`、`shyvana-model-D-2.png`、`shyvana-model-SA.png`、`shyvana-model-SD.png`；原始生成图原样放 `outputs/shyvana-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/shyvana_model_done.zip`。中间不要停，六张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（A / SA 约 17 px / 63 行，D 约 10 px / 72 行，SD 约 8 px / 72 行），从 raw/ 按格读回（regrid），在游戏大小下和梅尔、奈德丽、斯莫德、沃里克并排自查（PPU 1.5：人形 42、龙形 48 游戏像素），把两稿给用户挑，并问用户侧面要不要（第 0 步没回答）。
- 动作帧由 Claude 自己照英雄联盟的动作拼（`tools/lol/anim_graph.py Shyvana` / `ShyvanaDragon --wad Shyvana`，`pose_ref.py --champ Shyvana` / `--champ ShyvanaDragon --wad Shyvana`）；腿和待机一致、不变形；一张脸用在所有帧。数据里的动作名见 `tools/kit/build_shyvana.py` 和 PICTURE_PROMPT.md 最后一节。
