# 芮尔：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（骑马）** 和 **B（下马披甲）**（`1_picked_A.png`、`1_picked_B.png`），定的大小（每个游戏像素 1.5 格）：
>   - **A：从头发顶到马蹄底 66 格**（游戏里 44 行），约 80 格宽（连骑枪尖和马尾）。
>   - **B：从头发顶到脚底 60 格**（游戏里 40 行），约 48 格宽（连骑枪）。
> - 用户还要求**头画大一点**，让脸在游戏里看得清：从头发顶到下巴 **A 约 15 格、B 约 17 格**（两张里她的头差不多大，她是同一个人）；脸（皮肤部分）占头的一半左右，**不要被蓬发盖得只剩一条**。身体比例照原画，不要变成大头娃娃。
> - 我把 A、B 按这个比例直接缩好了（`2_target_A.png`、`2_target_B.png`，每格 12 px），**大小、位置、姿势都对，但糊了**：脸和眼睛糊成几格，金发分不出层次，马的铁甲板糊成一片，骑枪的金色裂纹没了，脖子那里还有一道接缝。
> - **这一轮就是在同样的格子上把它们重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**A、B 各画两稿。**

## 大小和位置（照 `2_target_*.png` / `3_layout_*.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A**：**头发顶在 y = 168**（绿线），**下巴在 y ≈ 348**（蓝线），**四只马蹄底在 y = 960**（红线）；骑枪尖朝右、马尾朝左，左右位置照 `2_target_A.png`。
- **B**：**头发顶在 y = 240**（绿线），**下巴在 y ≈ 444**（蓝线），**两只脚底在 y = 960**（红线）；骑枪斜指右下、枪尖碰到地面线，左右位置照 `2_target_B.png`。

## 要画清楚的地方

- **头**（`4_head.png`，两张一样）：
  - **金色蓬松的短发**，一绺绺向后、向上翘起，像金色的火焰；金色分 3–4 档（亮金、金、暗金、棕金），每一绺的方向用档次分出来，不要糊成一片黄。
  - **深棕色皮肤**的脸，坚毅的表情：**两只眼睛一样大、在同一行**（每只至少 2 格宽，有 1 格眼白或亮点），眉毛压低，嘴是 1 格深色线，下巴清楚。
- **A 骑马**：
  - 她：深蓝紫的紧身战衣（3 档），红棕色的皮带、护腕和膝甲；坐在马鞍上，近侧的腿垂在马身侧，铁靴踩在马镫上。
  - **铁甲战马**：橄榄绿 / 暗铜绿的一块块厚铁甲板，**每块板有亮边和深色缝**，板的形状数得出来；尖尖的马头铁盔，粗铁柱一样的四条腿，方方的铁蹄，向后翘的铁片马尾；铁甲上细细的金色裂纹（1 格）。
  - **骑枪**：平端朝右的长锥形骑枪，金色，**一道道发亮的黄色裂纹**清楚，握手处的铁护手看得出来。
- **B 下马披甲**：
  - 肩、胸、前臂、腿上的**橄榄绿厚铁甲**（亮边 + 深缝），一圈长长的**铁甲裙板**，每片板分得开；甲片之间露出深蓝紫战衣和红棕皮带；深色铁靴。
  - **骑枪**握在近侧手里，锥形枪身金色带黄色裂纹，护手处的金色尖片清楚，枪尖斜指右下碰到地面线。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包的潘森、卡特琳娜每游戏像素 1.5 格，和芮尔一样；赫卡里姆的铁甲马身；卡莉丝塔；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（金发、深棕皮肤、深蓝紫战衣、橄榄绿铁甲、金色骑枪）。铁甲**一定要有亮边和高光**，不然在游戏里会糊成一团深绿。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图里面是 192–254 的半透明，这次不要）。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `rell_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` / `1_picked_B.png` | 你第 0 步画的 A、B（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` / `2_target_B.png` | 按新大小（头放大）缩到每格 12 px 放在画布上（糊的） | **大小、位置、姿势、头身比**照它，糊的地方重画 |
| `3_layout_A.png` / `3_layout_B.png` | 同一张加网格线：绿线 = 头发顶，蓝线 = 下巴，红线 = 地面 | 对齐网格、头和地面线的位置 |
| `4_head.png` | B 的头（读回后 8 倍放大） | 金发、脸、眼睛 |
| `style/5_style_pantheon.png` … `8_style_kalista.png` | 本包的潘森、卡特琳娜（每游戏像素 1.5 格）、赫卡里姆、卡莉丝塔，8 倍放大 | **只看风格**：这个密度下一格有多大、重甲怎么分档和留亮边、马身怎么画、脸怎么画 |

## 提示词 1：`rell-model-A-1.png`、`rell-model-A-2.png`（骑马，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1B approved pixel-art pictures of this character - a young iron knight woman with wild spiky golden hair like flames and dark brown skin; in 1A she rides a heavy war horse built of olive-green iron armour plates and holds a very long golden lance with glowing yellow cracks level forward; in 1B she stands dismounted wearing the horse's iron as heavy armour, the lance slanting down (the LOOK, the COLOURS and the DETAILS to keep); 2A and 2B the same two pictures shrunk to their final game size on a 1024x1024 canvas, 12 px squares, with a bigger head - the SIZE, the PLACE, the POSE and the HEAD-TO-BODY PROPORTION are right, but they are muddy (the face and eyes blurred, the hair's gold shades lost, the horse's plates smeared, the lance's cracks gone, a seam at the neck); 3A and 3B the same with grid lines every 5 squares: the green line = the top of her hair, the blue line = her chin, the red line = the ground; 4 her head enlarged; 5-8 STYLE ONLY: other characters from the same game at this same square density (5, 6) and a horse body (7), shown 8x so every square is one pixel - copy their pixel-art look, the lit edges on heavy armour.
Draw with the image generator ONE clean pixel-art picture of the MOUNTED character (picture A): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2A: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of her hair at y 168, her chin at y 348 (the head from the hair's top to the chin about 15 squares - bigger than in image 1A, so her face reads at game size: the dark brown face about half of the head, not hidden by the hair), all four hooves on the ground line y 960, the lance level pointing right, the horse's tail sweeping left - as if a pixel artist redrew image 1A square by square on image 2A's grid.
Make it CRISP and READABLE at this size: the WILD SPIKY GOLDEN HAIR in flame-like locks, the gold in 3-4 shades (bright gold, gold, dark gold, brown-gold) showing each lock; the DARK BROWN face with TWO EYES the same size on the same row (at least 2 squares wide each with a 1-square light), low brows, a 1-square dark mouth line, a clear chin; her dark blue-violet bodysuit in 3 shades with red-brown straps, bracers and knee guard, seated in the saddle, the near leg down the horse's side; the IRON HORSE built of thick OLIVE-GREEN iron plates, EVERY PLATE WITH A LIT EDGE AND A DARK SEAM so the plates are countable, a pointed iron helm for the head, thick iron pillar legs with blocky iron hooves, iron plates sweeping back as the tail, thin golden cracks (1 square) in the iron; the long tapering GOLDEN LANCE with bright yellow glowing cracks and an iron hand guard at the grip.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`rell-model-B-1.png`、`rell-model-B-2.png`（下马披甲，两稿）

附同样的图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of the DISMOUNTED character (picture B): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2B: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of her hair at y 240, her chin at y 444 (the head from the hair's top to the chin about 17 squares - bigger than in image 1B, so her face reads at game size: the dark brown face about half of the head, not hidden by the hair), both soles on the ground line y 960, the lance in her near hand slanting down to the right with its tip touching the ground line - as if a pixel artist redrew image 1B square by square on image 2B's grid. Her head the same as in picture A (the same woman).
Make it CRISP and READABLE at this size: the WILD SPIKY GOLDEN HAIR in flame-like locks, the gold in 3-4 shades; the DARK BROWN face with TWO EYES the same size on the same row (at least 2 squares wide each with a 1-square light), low brows, a 1-square dark mouth line, a clear chin; HEAVY OLIVE-GREEN IRON ARMOUR on her shoulders, chest, forearms and legs, EVERY PLATE WITH A LIT EDGE AND A DARK SEAM, a long SKIRT OF SEPARATE IRON PLATES round her hips, the dark blue-violet bodysuit and red-brown straps showing between the plates, dark iron boots; the GOLDEN LANCE: a tapering cone with bright yellow glowing cracks and golden spiked guard plates at the grip.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` / `2_target_B.png` 一样：每格 12 px、对齐网格；A 头发顶 y 168、下巴约 y 348、马蹄底 y 960；B 头发顶 y 240、下巴约 y 444、脚底 y 960。
- **头比原画大**，脸看得清：**两只眼睛一样大、同一行**；A、B 里她的头差不多大；身体比例照原画。
- 铁甲板有亮边和深缝，数得出来；骑枪的黄色裂纹清楚；外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/rell-model/`）

- `rell-model-A-1.png`、`rell-model-A-2.png`、`rell-model-B-1.png`、`rell-model-B-2.png`；**image_gen 的原始生成图原样放 `outputs/rell-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/rell_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时按 design_orianna_cut 的 even_cut 删整行整列到 66 / 60 行（不经过脸），和 `2_target_*.png` 并排、按游戏大小和阿利斯塔、布隆、蕾欧娜、赫卡里姆、德莱厄斯放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作：主包骑马（待机、跑 gallop/Run_Slow、普攻 Auto_Attack1、Q Spell1、W 轰落 Rell_Spell2_Dismount、驾临 Spell2_Flip、E Spell3_activation、R Spell4、受击、死亡），附加包下马（待机、走 Biped_Walk、普攻 Attack1_Biped、Q Biped_Spell1、受击、死亡）；先试奥莉安娜 / 塔姆的做法（用造型部件无损自己摆），马腿的跑步太难再给 Codex 写动作包。
