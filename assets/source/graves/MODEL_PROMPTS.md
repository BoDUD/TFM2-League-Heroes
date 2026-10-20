# 法外狂徒 格雷福斯：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（长枪的待机）**（`1_picture_A.png`）和它的侧面 SA（`1b_picture_SA.png`）**用户选定了，样子、颜色、姿势全照它们**。
> - 这一步要把他画成**游戏里的格子数**：**从头顶头发到脚底 57 格**，连霰弹枪约 66 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（脸、眼睛、胡子、枪上的金边碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **要画两个角度**（同一个格雷福斯、同样的格子、同样的颜色）：
>   - **3/4 正面朝右**（和 A 一样）：游戏里的待机。
>   - **侧面朝右**（附图 1b、5、6）：身体转成侧面，**脸朝画面右边**，近侧的手臂、护肩在前面、颜色亮，远侧的大部分被身体挡住、稍暗；霰弹枪平端在腰间、**枪口朝右、枪管水平笔直**，和 3/4 正面一样长；深红围巾在身后（画面左边）飘起一点。**头保持和 3/4 正面一样**（脸朝右前方、两只眼睛都看得见，同样的格子），只把身体转成侧面。他的跑步、开枪和技能动作都从这张侧面图来做。
> - **每格画大：16 px 一格**。画布用你平时的 **1254 × 1254**：**头顶 y = 256，眼睛约 y = 416，脚底 y = 1168**。每一格都是 16 × 16 px 的方块，不要用更小的格子画细节。**每个角度画两稿，一共四张。**

## 大小和位置（照 `2_target.png` / `3_layout.png` / `6_side_layout.png`）

- 画布 **1254 × 1254**，**每格 16 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **头顶 y = 256**（绿线），**眼睛约 y = 416**（蓝线），**脚底 y = 1168**（红线）：头顶到脚底 **57 格**。
- 3/4 正面：宽约 66 格（枪托到枪口），放在 `2_target.png` 的位置。侧面：照 `6_side_layout.png` 的大小、位置和地面线（约 76 格宽，围巾在左边）。

## 在 57 格里要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍）：往后梳、翘起几撮的**黑头发**（深棕黑 3 档，亮边）；**脸要亮、要大到看得清**（肤色 3 档，至少 7 格宽）；**两只眼睛：每只 2 格（眼白 + 深色瞳孔），一样高**；浓黑眉压在眼睛上；**黑络腮胡分 2–3 档**（不要糊成一块黑），包住下巴和两颊；耳朵看得见。
- **衣服**：深红围巾 3 档（亮边），围住脖子、搭在肩上；近侧肩膀上**很大的棕色皮护肩**（3–4 档，铜色包边、2–3 颗铆钉）；棕色皮马甲、深藏青衬衫；宽皮带和弹药袋；**深灰裤子**（偏亮的边、膝盖的皮护垫）；棕色靴子。
- **霰弹枪（最重要）**：后面**金色的两叉枪托** + 木头握把，中间**金色的圆弹仓**（看得出圆形和金边），前面**两根平行的黑色枪管，横平竖直、笔直水平**（黑钢 3 档，上面一条偏亮的高光线），枪口和中段有**金色的箍**，枪管下面**金色的前握把**。两只手都握在枪上：近侧的手握后面的握把，远侧的手握前握把。
- **一圈 1 格的近黑外描边**，连续不断（枪也有）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的普朗克、杰斯、嘉文四世、斯维因——**和格雷福斯同一个密度 PPU 1.5**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画枪口火光、子弹、烟）。

## 附图（压缩包 `graves_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1b_picture_SA.png` | 你第 0 步画的 A 的侧面 | 侧面图的样子 |
| `2_target.png` | A 缩到游戏格子数、每格 16 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 头顶，蓝 = 眼睛，红 = 地面 | 对齐网格、57 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 头发、脸、眼睛、眉毛、胡子 |
| `5_side_ref.png` | 英雄联盟原版的待机，侧面、朝右 | **侧面图的身体**：身子的厚度、护肩、围巾、枪的位置和两只手 |
| `6_side_layout.png` | 第 0 步的侧面缩到同样的格子数 | 侧面图的大小、位置、地面线 |
| `style/7_style_gangplank.png` … `10_style_swain.png` | 本包的普朗克、杰斯、嘉文四世、斯维因，8 倍放大（同密度） | **只看风格**：这么粗的格子里胡子、金属、深色衣服的亮边、脸和眼睛怎么画 |

## 提示词 1：`graves-model-A-1.png`、`graves-model-A-2.png`（3/4 正面，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a burly gunslinger: slicked-back black hair, a full black beard, thick brows; a ragged deep crimson scarf round his neck and shoulders; a big brown leather pauldron with brass trim on the near shoulder, a brown leather vest, a dark navy shirt, a wide belt with shell pouches; loose dark grey trousers, brown boots; a HUGE DOUBLE-BARRELLED SHOTGUN of black steel and polished gold held level at his hip with both hands - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 1b the same character from the side; 2 the same character cut down to the RIGHT square count - 57 squares from the top of his hair to his soles, about 66 squares wide with the gun - shown with 16 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the face, the eyes, the beard and the gun's gold trim are specks); 3 the same with grid lines every 5 squares: green = the top of the hair, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 5 and 6 are for the side view (not this picture); 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel, at this same square density - how a beard, metal, the lit edges of dark clothes, a face and eyes are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 16 px, aligned on one straight grid from the canvas corner; the top of the hair at y 256, the eyes at about y 416, both soles on y 1168 - exactly 57 squares from the top of the hair to the soles, about 66 squares wide, placed as in image 2. Every detail drawn with whole 16 px squares, never with smaller pixels.
With only 57 squares make every part READ: the slicked-back black hair with a few spikes, in 3 dark shades with lit edges; the FACE BRIGHT and BIG ENOUGH TO READ (skin in 3 shades, at least 7 squares wide); TWO EYES, each 2 squares (white with a dark pupil), at the SAME height, thick black brows over them; the full black BEARD in 2-3 shades round the jaw and cheeks (never one black blob); the ear visible; the crimson scarf in 3 shades with lit edges round his neck and over his shoulders; the BIG BROWN LEATHER PAULDRON on the near shoulder in 3-4 shades with brass trim and 2-3 rivets; the brown leather vest, the dark navy shirt, the wide belt with shell pouches; the dark grey trousers with lighter edges and leather knee pads; the brown boots.
THE SHOTGUN, the most important part: the TWO-PRONGED GOLD STOCK and a wooden grip at the back, the ROUND GOLD DRUM CHAMBER in the middle (its round shape and gold rim readable), TWO PARALLEL BLACK BARRELS in front - perfectly STRAIGHT and HORIZONTAL rows of squares, black steel in 3 shades with one lighter highlight line along the top -, GOLD RINGS at the muzzles and halfway along, a GOLD FORE-GRIP under the barrels. Both hands on the gun: the near hand on the back grip, the far hand on the fore-grip.
THE POSE as image 1: feet apart, knees a little bent, the gun level at his hip pointing right; 3/4 view facing right (the face to the front-right), the NEAR side in front in full tone, the FAR side a step darker.
One continuous 1-square near-black outline round the figure and the gun; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no bullets, no smoke), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`graves-model-side-1.png`、`graves-model-side-2.png`（侧面朝右，两稿）

附全部图。**用 image_gen 画。**

```text
Same attached images and the SAME character, colours, square size (16 px) and square count as prompt 1 - now SIDE-ON, FACING RIGHT. Image 1b is your own earlier side drawing of him and image 5 the original character from the side, facing right: copy from them the BODY seen side-on - the depth of the body, the pauldron, the scarf trailing behind, the shotgun held level at the hip with both hands; image 6 is your earlier side drawing brought to the same count on the grid (its size, place and ground line).
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px on one straight grid from the canvas corner; the top of the hair at y 256, the eyes at about y 416, the soles on y 1168 - exactly 57 squares from the top of the hair to the soles - placed as in image 6 (about 76 squares wide with the scarf and the gun).
THE BODY SIDE-ON: facing the image right; the NEAR arm and the big pauldron in front in full tone, the FAR arm mostly hidden behind the body, a step darker; the SHOTGUN held LEVEL at his hip pointing RIGHT, as long as in prompt 1, its two black barrels perfectly STRAIGHT and HORIZONTAL, the gold stock behind his hip, the round gold drum, the gold rings and the gold fore-grip; both hands on the gun; the crimson scarf trailing a little behind him (on the image left); one leg a little in front of the other, both boots on the ground line.
THE HEAD stays the SAME as the 3/4 view of prompt 1 (the slicked-back black hair, the face to the front-right, BOTH eyes visible, the same squares, the bright face, the black beard in 2-3 shades) - only the body is turned side-on.
The same colours and details as prompt 1; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px**：头顶 y 256、脚底 y 1168，**头顶到脚底正好 57 格**（数一下台阶数：**如果是 90 格以上就是格子画小了，请重画**）。
- 脸亮、看得清；两只眼睛一样高；黑胡子分档；深红围巾、棕色大护肩；霰弹枪的金色枪托、圆弹仓、**两根黑枪管笔直水平**、金箍、金色前握把；外描边连续；没有任何特效。
- 3/4 正面：两只手都握着枪；侧面：脸朝右、枪平端在腰间朝右、围巾在身后、**头和 3/4 正面一样**、枪和 3/4 正面一样长。

## 交付（`outputs/graves-model/`）

- `graves-model-A-1.png`、`graves-model-A-2.png`、`graves-model-side-1.png`、`graves-model-side-2.png`；原始生成图原样放 `outputs/graves-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/graves_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、头顶到脚底 57 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在 12 倍下查脸（眼睛有没有画在半格上，`codex-face-half-squares`），**查枪管是不是一整行一整行的水平线**，在游戏大小下和普朗克、杰斯、嘉文四世并排自查（PPU 1.5，38 游戏像素），给用户挑 3/4 和侧面各一张。
- 动作：英雄联盟的 attack1（开枪 + 上膛）/ attack2（装弹，第二发之后）/ crit；Q spell1；E spell3（翻滚冲刺）；R spell4 + spell4_BACK（后坐力往后推）；跑 run；死亡 death。W 烟幕弹随普攻扔出（不单独做动作，或用普攻的帧）。枪口火光烤进他自己的帧。造型摆不出的姿势让 Codex 照带骨架的包画（`codex-draws-poses`），腿和待机一致、不变形，拿枪的手臂从肩膀画出来。
