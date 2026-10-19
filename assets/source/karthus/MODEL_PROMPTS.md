# 死亡颂唱者 卡尔萨斯：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（长杖的待机）**（`1_picture_A.png`）和它的侧面 SA（`1b_picture_SA.png`）**用户选定了，样子、颜色、姿势全照它们**。
> - 这一步要把他画成**游戏里的格子数**：**从冠尖到脚底 60 格**，法杖的水晶尖再高出冠尖 **8 格**（一共 68 格高），约 36 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（脸、眼睛、宝石、肩甲碎成杂点，脸太暗看不清）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **要画两个角度**（同一个卡尔萨斯、同样的格子、同样的颜色）：
>   - **3/4 正面朝右**（和 A 一样）：游戏里的待机。
>   - **侧面朝右**（附图 1b、5、6）：身体转成侧面，**脸朝画面右边**，近侧的手臂、肩甲在前面、颜色亮，远侧的大部分被身体挡住、只露一点、稍暗；法杖握在身前（画面右边）竖直立着，**和 3/4 正面一样长：水晶尖在 y = 80**；破布在身后（画面左边）垂下。**头保持和 3/4 正面一样**（主教冠、脸朝右前方、两只青色眼睛都看得见，同样的格子），只把身体转成侧面。他的跑步和施法动作都从这张侧面图来做。
> - **每格画大：16 px 一格**。画布用你平时的 **1254 × 1254**：**杖尖 y = 80，冠尖 y = 208，眼睛约 y = 416，脚底 y = 1168**。每一格都是 16 × 16 px 的方块，不要用更小的格子画细节。**每个角度画两稿，一共四张。**

## 大小和位置（照 `2_target.png` / `3_layout.png` / `6_side_layout.png`）

- 画布 **1254 × 1254**，**每格 16 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **杖尖 y = 80**（紫线），**冠尖 y = 208**（绿线），**眼睛约 y = 416**（蓝线），**脚底 y = 1168**（红线）：冠尖到脚底 **60 格**，杖尖到脚底 68 格。
- 3/4 正面：宽约 36 格，放在画布中间（`2_target.png` 的位置）。侧面：照 `6_side_layout.png` 的身体大小和地面线（那张是第 0 步短杖的侧面缩下来的，**只看身体**；法杖照 3/4 正面的长度画到紫线）。

## 在 60 格里要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍）：高高的尖顶主教冠（深钢灰 3 档、偏青的亮边），冠中间**深红色**的条纹，冠下沿正中一颗**青色宝石**（2 格）；冠下垂出深红色的头发；**灰绿色的骷髅脸要亮、要大到看得清**（至少 6 格宽、7 格高，不要被冠和头发的暗色吞掉）；**两只发光的青色眼睛：每只 2 格，一样高，中间 1 格浅青白色最亮**，眼睛周围是深色的眼窝；**张开的下巴，上下各一排白牙**（每颗 1 格）。
- **肩甲**：一对又大又弯的深钢色肩甲，尖角往两边翘，每边镶一颗**发光的青色宝石**（2×2 格，1 格浅青白高光）；胸前一颗青色宝石。
- **衣服**：深红长袍 3 档；外面撕成一条条的**深紫破布** 3 档（和深红分得开），从肩上垂到地上，下摆是参差的尖条；胸前两条紫色长带；腰带上一个小骷髅（2–3 格的白色）。
- **手**：灰绿的骨爪手。近侧（画面左边）的手垂在身侧、手指弯成爪；远侧（画面右边）的手握着法杖。
- **法杖**：深钢色，2 格粗、竖直，杖头是**青色水晶的矛尖**（3–4 格高，1 格浅青白高光），下面一圈**深红色的尖刺护环**（左右各伸出 1–2 格），杖底一个小叉。
- **脚**：袍子底下露出两只灰白的骷髅脚，都落在地面线上。
- **一圈 1 格的近黑外描边**，连续不断（法杖也有）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的斯维因、莫甘娜、烈娜塔、佐伊——**和卡尔萨斯同一个密度 PPU 1.5**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画爆炸、墙、灵魂、光芒）。

## 附图（压缩包 `karthus_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1b_picture_SA.png` | 你第 0 步画的 A 的侧面 | 侧面图的样子 |
| `2_target.png` | A 缩到游戏格子数、每格 16 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：紫 = 杖尖，绿 = 冠尖，蓝 = 眼睛，红 = 地面 | 对齐网格、60 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 主教冠、宝石、头发、骷髅脸、青色眼睛、白牙 |
| `5_side_ref.png` | 英雄联盟原版的待机，侧面、朝右 | **侧面图的身体**：身子的厚度、肩甲、长袍和破布、法杖握在身前 |
| `6_side_layout.png` | 第 0 步短杖侧面缩到同样的格子数（只看身体大小） | 侧面图的大小、位置、地面线；法杖画到紫线 |
| `style/7_style_swain.png` … `10_style_zoe.png` | 本包的斯维因、莫甘娜、烈娜塔、佐伊，8 倍放大（同密度） | **只看风格**：这么粗的格子里长袍、深色衣服的亮边、脸和眼睛怎么画 |

## 提示词 1：`karthus-model-A-1.png`、`karthus-model-A-2.png`（3/4 正面，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a tall gaunt lich: a tall pointed dark-steel mitre crown with crimson inlays and a cyan gem, crimson hair, a grey-green skull face with two glowing cyan eyes and an open jaw with white teeth; huge curved dark-steel pauldrons with glowing cyan gems; a deep crimson robe under torn dark violet cloth hanging to the ground in ragged strips, two violet stoles, a belt with a small skull; bony grey-green claw hands; bare skeletal feet; a tall dark-steel staff with a cyan crystal spear-head and a spiked crimson collar - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 1b the same character from the side; 2 the same character cut down to the RIGHT square count - 60 squares from the crown tip to his soles, the staff tip 8 squares higher, about 36 squares wide - shown with 16 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the face, the eyes, the gems and the pauldrons are specks, the face too dark); 3 the same with grid lines every 5 squares: purple = the staff tip, green = the crown tip, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 5 and 6 are for the side view (not this picture); 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel, at this same square density - how robes, the lit edges of dark clothes, a face and eyes are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 16 px, aligned on one straight grid from the canvas corner; the staff tip at y 80, the crown tip at y 208, the eyes at about y 416, both soles on y 1168 - exactly 60 squares from the crown tip to the soles, about 36 squares wide, placed as in image 2. Every detail drawn with whole 16 px squares, never with smaller pixels.
With only 60 squares make every part READ: the tall pointed mitre crown in 3 dark steel greys with lighter teal-grey edges, its crimson inlays and a 2-square cyan gem at its lower front edge; the crimson hair falling from under it; the grey-green SKULL FACE BRIGHT and BIG ENOUGH TO READ (at least 6 squares wide and 7 tall, never swallowed by the dark crown and hair); TWO GLOWING CYAN EYES, each 2 squares, at the SAME height, a 1-square pale cyan-white centre, dark sockets round them; the OPEN JAW with an upper and a lower row of WHITE TEETH (1 square each); the huge curved pauldrons with their tips flaring out, each with a 2x2 GLOWING CYAN GEM (one pale cyan-white square), a cyan gem on the chest; the deep crimson robe in 3 shades; the TORN DARK VIOLET CLOTH in 3 shades, clearly apart from the crimson, hanging from the shoulders to the ground in ragged pointed strips; two violet stoles down the front; a small white skull (2-3 squares) on the belt; the bony grey-green claw hands - the NEAR one (image left) hanging at his side with bent claw fingers, the FAR one (image right) gripping the staff; the STAFF 2 squares thick and upright, its cyan crystal spear-head 3-4 squares tall with a pale highlight, a spiked crimson collar under it (1-2 squares out each side), a small fork at its foot; two bare grey-white skeletal feet on the ground line.
THE POSE as image 1: standing a little hunched, 3/4 view facing right (the face to the front-right), the NEAR side in front in full tone, the FAR side a step darker.
One continuous 1-square near-black outline round the figure and the staff; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no blasts, no walls, no souls, no glow round him), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`karthus-model-side-1.png`、`karthus-model-side-2.png`（侧面朝右，两稿）

附全部图。**用 image_gen 画。**

```text
Same attached images and the SAME character, colours, square size (16 px) and square count as prompt 1 - now SIDE-ON, FACING RIGHT. Image 1b is your own earlier side drawing of him and image 5 the original character from the side, facing right: copy from them the BODY seen side-on - the depth of the body, the pauldrons, the robe and the torn cloth hanging behind, the staff held in front; image 6 is your earlier short-staff side brought to the same count on the grid (the body's size, place and ground line only).
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px on one straight grid from the canvas corner; the crown tip at y 208, the eyes at about y 416, the soles on y 1168 - exactly 60 squares from the crown tip to the soles - in the middle of the canvas; the staff AS LONG AS IN PROMPT 1, its crystal tip at y 80 (the purple line of image 6).
THE BODY SIDE-ON: facing the image right; the NEAR arm and pauldron in front in full tone, the FAR ones mostly hidden behind the body, a step darker; the staff held upright IN FRONT of him (on the image right) in his claw hand; the torn violet cloth and the robe's tail hanging behind him (on the image left) down to the ground; both skeletal feet on the ground line.
THE HEAD stays the SAME as the 3/4 view of prompt 1 (the tall mitre crown, the face to the front-right, BOTH glowing cyan eyes visible, the same squares, the bright skull face, the open jaw with white teeth, the crimson hair) - only the body is turned side-on.
The same colours and details as prompt 1: dark steel with lighter teal-grey edges, the cyan gems, the crimson robe, the violet cloth, the grey-green bones; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px**：冠尖 y 208、脚底 y 1168，**冠尖到脚底正好 60 格**；杖尖 y 80（数一下台阶数：**如果是 100 格以上就是格子画小了，请重画**）。
- 骷髅脸亮、看得清；两只发光的青色眼睛一样高；白牙；肩甲和冠上的青色宝石；深红长袍和深紫破布分得开；法杖的青色水晶尖和深红护环；外描边连续；没有任何特效。
- 3/4 正面：近侧的手垂着、远侧的手握杖；侧面：脸朝右、法杖在身前、破布在身后、**头和 3/4 正面一样**、杖和 3/4 正面一样长。

## 交付（`outputs/karthus-model/`）

- `karthus-model-A-1.png`、`karthus-model-A-2.png`、`karthus-model-side-1.png`、`karthus-model-side-2.png`；原始生成图原样放 `outputs/karthus-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/karthus_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、冠尖到脚底 60 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在 12 倍下查脸（眼睛、牙有没有画在半格上，`codex-face-half-squares`），在游戏大小下和斯维因、莫甘娜、烈娜塔、佐伊并排自查（PPU 1.5，40 游戏像素），给用户挑 3/4 和侧面各一张。
- 动作：英雄联盟的 attack1 / attack2（普攻，W 痛苦之墙用 Spell2 的姿势）；Q Spell1a / _b / _c；E spell3；R spell4 + spell4_loop（引导 3 秒）；跑 run_base；死亡 death。造型摆不出的姿势让 Codex 照带骨架的包画（`codex-draws-poses`），腿（袍子下摆）和待机一致、不变形。
