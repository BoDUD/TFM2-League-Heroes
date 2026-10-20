# 荆棘之兴 婕拉：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（一大蓬红发、手腕上的长鞭藤）**（`1_picture_A.png`）**用户选定了，样子、颜色全照它**；`1_picture_SA.png` 是你画的侧面，侧面的身体照它（它还偏 3/4，这一步要画成**正侧面**）。
> - 这一步要把她画成**游戏里的格子数**：**从头发顶到脚底 66 格**。我把 A、SA 直接缩到这个格子数（`2_target_A.png`、`2_target_SA.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、项圈、刺碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大：16 px 一格，人物撑满画布**。画布用你平时的 **1254 × 1254**：**头发顶 y = 128，两只脚底 y = 1184**。每一格都是 16 × 16 px 的大方块，不要用更小的格子画细节。
> - 一共画**两种**（同一个婕拉、同样的格子、同样的颜色）：**A 待机（3/4 正面）**、**SA 正侧面朝右**，各画**两稿**。

## 大小和位置

- 画布 **1254 × 1254**，**每格 16 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` / `3_layout_SA.png` 的浅灰线每 5 格一条）。
- **A**：照 `2_target_A.png` / `3_layout_A.png`：头发顶 **y = 128**（橙线），眼睛约 **y = 384**（蓝线），脚底 **y = 1184**（红线）：**66 格高、约 74 格宽**（两根鞭藤往两边甩出去），人在画布中间。
- **SA**：照 `2_target_SA.png` / `3_layout_SA.png`：同样的高度和地面线，**侧面朝右**，约 58 格宽。
- 全在画布里，头发、手、鞭藤不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：浅奶油偏绿的小脸；**两只琥珀色的眼睛：每只约 2 × 2 格，一样高、一样大**，亮黄色、各带 1 格更亮的高光，**上面一道深色眼影**；深色嘴唇 1–2 格；红发从额头两边垂下来。
- **头发**：深红-品红 3–4 档，**偏粉的亮边**一缕一缕分清楚，一大蓬往后、往上甩（第 0 步 A 的样子），**不要糊成一团红**；头顶两只**黄绿色的叶片角**（2 档、里面紫色），清楚地竖在头发里。
- **身体**：脖子上**深紫色项圈和 1 格粉红宝石**；**绿色叶片抹胸**和**叶片短裤**（3 档、深绿叶脉）；肩膀上一丛**品红尖刺**；小臂是**深紫色藤蔓护手**、上面几根**粉红色的刺**，**爪子手**；**两根细细的品红鞭藤**从手腕垂出、弯向两边，尖端一个**矛尖**（鞭藤 1–2 格粗，连续不断）。
- **腿**：两条**深紫色带刺的长腿**（3 档、偏紫的亮边，**不要糊成一团黑**），腿外侧一排**尖尖的刺叶**；**带爪的深紫色光脚**，两只脚踩在地面线上。**两条腿之间要有空隙和描边分开**。
- **A 的姿势**和第 0 步的 A 一样：她 3/4 正面朝右站着，两腿分开，两只爪子手张在身体两边，鞭藤垂下弯向外面；**近侧的腿（画面左边）颜色亮，远侧的腿（画面右边）稍暗**。
- **SA 的姿势**：**她完全侧面、朝右站直**（身体照 `1_picture_SA.png`，但要转成正侧面：胸口、肩膀朝右，不再是 3/4），**但头是和 A 一样的那颗头**：**脸朝右前方、两只琥珀色的眼睛都看得见**（不要另画一个只有一只眼的侧脸：所有动作都用同一张脸）；头发甩在背后（画面左边）；**近侧的手臂垂在身体前侧，外面一圈描边、和身体分开**，爪子手在大腿旁边，鞭藤垂到身前地面上方、弯向右边；远侧的手臂只露一点、稍暗；**两条腿一前一后**站在地面线上，脚尖朝右。所有动作都从这张画出来，所以手臂、鞭藤、腿、头发都要清楚地分开。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的莫甘娜、卡蜜尔、迦娜，**和婕拉同一个密度 PPU 1.5**，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效、植物。

## 附图（压缩包 `zyra_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1_picture_SA.png` | 你第 0 步画的侧面 | SA 的身体、手臂、腿（转成正侧面；头用 A 的） |
| `2_target_A.png` / `2_target_SA.png` | 缩到游戏格子数、每格 16 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_SA.png` | 加网格线：橙 = 头发顶，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的头部（8 倍） | 头发、叶片角、脸、眼睛、项圈 |
| `style/5_style_morgana.png`、`6_style_camille.png`、`7_style_janna.png` | 本包的莫甘娜、卡蜜尔、迦娜（同密度），8 倍放大 | **只看风格**：这么粗的格子里女人的脸、眼睛、头发、细长的腿怎么画 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A your own earlier pixel-art drawing of this character - a tall slender chibi plant woman with a huge mane of crimson-magenta petal-strand hair swept back, two yellow-green leaf horns (violet inside), pale cream-green skin, glowing amber eyes under dark lids, dark lips, a dark purple choker with a pink gem, a green leaf bodice and leafy green shorts, magenta thorn spikes on her shoulders, dark purple vine gauntlets with pink thorns, clawed hands, a thin magenta whip-vine with a spear tip curling from each wrist, long dark purple thorny legs with spiky leaves down their outer side and clawed dark feet (3/4 view facing right) - its LOOK and COLOURS are approved, but it is drawn with far too many small squares; 1SA your earlier side view of the same (only for her side-on body; it still leans 3/4); 2A and 2SA images 1A and 1SA cut down to the RIGHT square count - 66 squares from her hair top to her soles - shown with 16 px squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A and 3SA the same with grid lines every 5 squares: orange = her hair top, blue = her eyes, red = the ground; 4 her head of image 1A enlarged; 5-7 STYLE ONLY: other women from the same game at this same square density, shown 8x so every square is one pixel - how a face, eyes, hair and slim legs are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 16 px, aligned on one straight grid from the canvas corner; her hair top at y 128 and her soles on y 1184 - exactly 66 squares tall; the figure filling the canvas with at least one empty square on every side. Every detail drawn with whole 16 px squares, never with smaller pixels.
With this few squares make every part READ: her small pale cream-green face; TWO AMBER EYES, each about 2x2 squares, at the SAME height and the SAME size, bright yellow-amber each with ONE lighter highlight square, a dark lid line above; dark lips; the crimson-magenta mane in 3-4 shades with PINKER LIT EDGES, strand by strand, swept back and up, never one red mass; the two yellow-green leaf horns standing clearly out of the hair; the dark purple choker with a 1-square pink gem; the green leaf bodice and leafy shorts in 3 shades with dark green veins; the magenta shoulder spikes; the dark purple vine gauntlets with a few pink thorns and clawed hands; the two thin magenta whip-vines (1-2 squares thick, unbroken) ending in a spear tip; the long dark purple thorny legs in 3 shades with VIOLET LIT EDGES and a row of spiky leaves down their outer side, a clear gap and outline between the two legs; clawed dark purple bare feet on the ground line.
One continuous 1-square near-black outline round her; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no plants, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`zyra-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  POSE A: her idle exactly as images 1A, 2A and 3A - she stands in 3/4 view facing right with her legs apart, both clawed hands held out at her sides, the whip-vines hanging from her wrists and curling outward, the face to the front-right; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both feet on the ground line; about 74 squares wide.
  ```
- **SA（`zyra-model-SA-1.png`、`-SA-2.png`，两稿）**：
  ```text
  POSE SA: the SAME character exactly SIDE-ON, FACING RIGHT (size and place of images 2SA and 3SA, her body as in image 1SA but turned fully side-on: chest and shoulders facing right, no longer 3/4), standing upright; her head is the SAME head as in image 1A - turned to the front-right with BOTH amber eyes visible (not a one-eyed profile); the mane swept back behind her (image left); the NEAR arm hanging a little in front of her body, separated from the body by its own outline, the clawed hand by her thigh, its whip-vine hanging in front of her and curling to the right above the ground; the far arm only a little visible and a step darker; the two legs one in front of the other on the ground line, the feet pointing right; about 58 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px 的大方块**：头发顶 y 128、脚底 y 1184，**正好 66 格高**（数一下台阶数：**如果是 90–130 格就是格子画小了，请重画**）。
- 两只琥珀色眼睛一样大、一样高、带高光（A、SA 都是）；SA 里是和 A 同一个朝右前方的头、两只眼睛都看得见；SA 身子是正侧面、直立、近侧手臂和身体分开、两条腿一前一后。
- 头发一缕缕分清、两只叶片角清楚；鞭藤连续不断；两条腿分开、深紫色有亮边。外描边连续；没有任何技能特效和植物。

## 交付（`outputs/zyra-model/`）

- `zyra-model-A-1.png`、`zyra-model-A-2.png`、`zyra-model-SA-1.png`、`zyra-model-SA-2.png`；原始生成图原样放 `outputs/zyra-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/zyra_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、66 行），从 raw/ 按格读回（regrid），在游戏大小下和莫甘娜、卡蜜尔、迦娜、乐芙兰并排自查（PPU 1.5，44 游戏像素），把 A / SA 的两稿给用户挑。
- 动作照英雄联盟的骨骼摆（`tools/lol/anim_graph.py Zyra`、`pose_ref.py --champ Zyra`）：普攻 Zyra_attack1 / _attack2，Q `spell1` = Zyra_spell2.anm，E Zyra_spell3，R Zyra_spell4，跑 Zyra_run，死亡 Zyra_death。造型摆不出的姿势让 Codex 照带骨架的包画；腿和待机一致、不变形；一张脸用在所有帧；鞭藤连在手腕上。
