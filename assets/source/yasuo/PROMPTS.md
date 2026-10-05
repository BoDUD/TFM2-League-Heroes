# 亚索：给 GPT 的生图提示词（直接按游戏原尺寸画）

> **2026-09-27 更新：这一轮只画 12 张特效图（第 12–23 条）。**
> - 造型图已定稿：Codex 的两版生图没对上 8×8 网格，眼睛也不符合要求。Claude 在英雄联盟的剪影上逐格画了一版，脸是用户选的英雄联盟里的冷脸：粗眉、细长的眼睛、一格暗褐色小嘴。定稿就是附带的 `yasuo_native.png`，只用来参考配色，不要改它。
> - 10 张动作图不用画：改用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`），和德莱厄斯、阿木木一样。
> - 特效照下面第 12–23 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `--raw` 转成原尺寸条，再按技能范围定大小。但每张请保持一行等宽的正方形格子，不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

一共 23 张图：
- 1 张原尺寸造型图；
- 10 张原尺寸动作图；
- 12 张特效图。

生成的 PNG 和 Codex 的交接说明放进一个文件夹，然后告诉 Claude。Claude 按 8×8 方块逐格读色，放回每帧的锚点，接到技能上（`tools/art/import_native.py`）。

走李青、索拉卡、德莱厄斯、阿木木验证过的路线：直接按原尺寸画，不先画高清动作条。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 挥刀劈砍；被动「浪客之道」：暴击几率 20%；剑意每 12 秒充满，充满后下一次出手获得护盾，并立起「风之障壁」（4 秒内身边友方英雄受到的普攻伤害降低 40%；后来风墙从技能里删了） | `yasuo_attack` · `yasuo_fx_hit` · `yasuo_fx_shield` · `yasuo_fx_wall`（未使用） |
| 技能 1 | Q「斩钢闪」：向前突刺；命中两次后第三次放出旋风，击飞直线上的敌人；刚用过 E 时改为环形斩（EQ），满两层时是环形击飞（EQ3） | `yasuo_skill` · `yasuo_q3` · `yasuo_eq` · `yasuo_fx_q_thrust` · `yasuo_fx_q_hit` · `yasuo_fx_q_ready` · `yasuo_fx_tornado` · `yasuo_fx_knockup` · `yasuo_fx_eq` · `yasuo_fx_eq3` |
| 技能 2 | E「踏前斩」：冲刺穿过一名敌方英雄，停在它身后 | `yasuo_skill2` · `yasuo_fx_e_hit` |
| 大招 | R「狂风绝息斩」：闪到被控制的敌方英雄身边，跃在空中连斩，落地 | `yasuo_ult` · `yasuo_fx_r_slash` |
| 其他 | 待机、跑步、受击、死亡 | `yasuo_idle` · `yasuo_run` · `yasuo_hit` · `yasuo_dead` |

## 这一轮的做法

1. **原尺寸姿势参考**：`tools/lol/native_pose.py` 把英雄联盟客户端里亚索的真实动作直接渲染成游戏尺寸。
   - **比例**：用户选了 C（头 2.0、腿 0.8）。原版比例下亚索的头只占身高 19%（约 6 px），Q 版后占 36%（约 12 px），和原版英雄、李青、德莱厄斯一致。马尾保持英雄联盟原来的长度（`"hair": 0.5`）。
   - 待机时头顶到脚底 34 px（不算马尾，马尾再往上翘约 9 格），每个游戏像素取 8×8 方块的平均色，放大 8 倍显示（`yasuo_native_*.png`）。亚索的待机是深蹲，身体只有站直时的 80% 左右，所以轮廓比李青宽。
   - 姿势、大小、每帧在格子里的位置都已经算好：普攻、Q、Q3 的前冲保留原版的 70%，死亡保留 65%；E 冲刺和 EQ 原地不动（游戏自己移动亚索），R 保留 30%，空中高度只保留 15%。
2. **高清对照**：同一批帧的高清渲染（`yasuo_pose_*.png`），格子和位置完全一样。缩小图看不清姿势时看它。
3. **每帧锚点**：记在 `yasuo_cells.json` 里。新图画在同样的格子里，按同一个锚点切出来，就站在参考图那一帧的位置上。

**格子**：96×88 方块，脚底线离格子底部 10 格。亚索的刀很长：待机时拖在身后左边 20 多格，Q3 往上举刀时刀尖接近格子顶。

## 生成顺序（重要）

1. **先只生成造型图 `yasuo_native.png`**（第 1 条），附五张图（见提示词），然后停下，等 Claude 和用户审过再画别的。
2. **Claude 和用户审造型图**，逐格对照原版英雄（`tfm2_style_ref_swordsman.png`、`tfm2_face_ref_male.png`）：
   - 从头顶到脚底正好 34 个方块（272 px），马尾在头顶上方另外翘起；
   - 所有方块都是 8×8、对齐同一个网格，没有半个方块、没有模糊边；颜色不超过 20 种，没有杂色点；
   - **眼睛**（最重要）：朝右时近处的眼睛在左边、宽 2 格；远处的眼睛宽 1 格、贴着右边的脸边；每只眼睛 3 行高（最上一行近黑的粗眉，中间一行浅色高光挨着近黑瞳孔，下面一行眼白挨着深棕色虹膜；远眼是近黑、近黑、深棕）；眼睛下面约 2 行脸，然后是下巴；
   - **嘴**：提示词要求不画。审图时 Claude 给用户两个选项：不画，或一格暗红小嘴（索拉卡、德莱厄斯选了小嘴，阿木木选了不画）；
   - 放到接近黑色的英雄卡片背景上，脸和腰都看得清；头的右边不是一条直的竖边；
   - **马尾**：头顶后方用金色小发箍扎住，一大束刺状的深红棕马尾往左上方翘，是头顶以上最大的形状；
   - **刀**：细长微弯的刀拖在身后左边，2 格粗，一眼能看出是刀；
   - 3/4 正面朝右，看得到两只眼睛；近处（画面左边）的肩膀是银色的层叠肩甲，浅蓝色的布从远处的肩膀斜搭过胸前；金黄色的粗绳腰带；深藏青色的宽裤子。

   **不对就重画这一张，不要带着错的造型图往下做。** 如果造型图是生图原稿（不在 8×8 网格上，或尺寸不对），Claude 会给用户两个选项：让 Codex 重做，或者由 Claude 在英雄联盟的剪影上逐格画（阿木木就是这样定稿的）。
3. 造型图通过后，10 张动作图**同一批**生成，每张附三张图：
   - 第一张：定稿造型图 `yasuo_native.png`；
   - 第二张：对应的 `yasuo_native_<动作>.png`（原尺寸姿势参考）；
   - 第三张：对应的 `yasuo_pose_<动作>.png`（同一批帧的高清渲染）。
4. 输出排版和第二张附图完全一样：几列几行、每格多大（96×88 个方块）、每帧在第几格。
5. 12 张特效图不附图，可以和动作图同时生成。
6. **交给 Claude 之前请 Codex 整理**（和前几个英雄一样）：
   - 每个像素都是严格对齐的 8×8 纯色块，透明度只有全透明和不透明；
   - 全部角色图只用定稿造型图的颜色，去掉孤立的杂色点；
   - **每一帧的头和造型图一样大**（按方块数一样），脸朝观众的帧直接把造型图的头逐格贴进去；头转开、低下、倒下的帧按参考图转动同一个头，不要画大画小；
   - **身体要画出来，不要用方块拼**：德莱厄斯那批的身体是在格子上按参考手工拼的，动起来忽大忽小。如果生图做不到，请在交接说明里写明哪些帧是拼的，Claude 会改用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）；
   - 待机 6 帧头的大小不变，只随呼吸上下动；上下动时从头到大腿一起沉，只有小腿和脚不动（接缝不能在腰上）；跑步 8 帧头保持在参考图的那一列，不要左右跳 1–2 格；
   - 每帧留在它的格子里、画在哪就是哪，**不要按包围框重新居中**（锚点记在 `yasuo_cells.json`）；
   - 附交接说明 `HANDOFF.md`、逐帧记录 `MANIFEST.json`（文件哈希、每帧的包围框、每帧头的大小）和实际用的提示词。
7. 以后要改造型，全部动作图用新造型图整批重画，不和旧批次混用。

## 附图（压缩包里有）

Riot 模型渲染和原版游戏截图只在本地用，不提交到仓库。

| 文件 | 内容 | 用在 |
|---|---|---|
| `yasuo_native_design.png` | 原版待机第 0 帧，按 Q 版比例直接渲染成游戏尺寸（34 px），8 倍显示，128×128 方块画布 | 造型图 |
| `yasuo_pose_design.png` | 同一帧的高清渲染，位置相同 | 造型图（看不清时对照） |
| `tfm2_style_ref_swordsman.png` | 团战经理 2 原版的剑客、双刀客、忍者、戏刃师、追猎者、狂战士，上排待机、下排攻击，8 倍 | 造型图 |
| `yasuo_model_chibi.png` | 英雄联盟游戏内模型（Q 版比例）的正面、侧面、背面，右边是 3/4 侧的头部特写 | 造型图 |
| `tfm2_face_ref_male.png` | 原版角斗士、骑兵、魔剑士、杀手的头，12 倍：眼睛怎么排，胡茬怎么画 | 造型图 |
| `pack_native_ref.png` | 本包按原尺寸画的拉克丝、艾希、李青、索拉卡、德莱厄斯、阿木木，8 倍 | 造型图 |
| `yasuo_native.png` | 定稿造型图，8 倍，128×128 方块画布（造型通过后才有） | 全部动作图（第一张附图） |
| `yasuo_native_<动作>.png` | 原版动作渲染成游戏尺寸，8 倍，按格子排好 | 各自的动作图 |
| `yasuo_pose_<动作>.png` | 同一批帧的高清渲染，格子和位置完全相同 | 各自的动作图 |
| `yasuo_cells.json` | 每帧锚点在格子里的位置和帧时长（给 Codex 核对位置用） | 整理 |

## 所有角色图的规则

- **像素尺寸（最重要）**：
  - 角色是游戏里的小精灵，从头顶到脚底 34 像素高（马尾另外往上翘）；
  - 按真正的低分辨率像素画来画，再整体放大 8 倍输出；
  - 每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格；
  - 没有比一个方块更小的东西，没有抗锯齿、模糊、柔光。
- **干净，不要细节**：
  - 颜色不超过 20 种：头发 3 个深红棕，皮肤 3 个棕褐，蓝布 3 个蓝，银甲和刀 3 个钢灰加一个近白，裤子 2 个深藏青，金色 2–3 个（发箍、绳腰带），眼白、深棕虹膜，近黑描边；
  - 不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；
  - 1 个方块宽的近黑色描边，绕着整个轮廓和每个部件（头、马尾、肩甲、手臂、腰带、每条腿、刀）；
  - 肩甲的层叠只用 3–4 道弧形分出来，裤子的纹路、护臂的花纹都不要画。
- **脸**：
  - 头约占身高的三分之一，每一帧都和造型图一样大；
  - 眼睛按造型图逐格照抄：近眼在左，2 格宽 3 行高（近黑粗眉；浅色高光挨着近黑瞳孔；眼白挨着深棕虹膜），远眼 1 格宽贴着脸边（近黑、近黑、深棕）；
  - 眼睛下面约 2 行棕褐色的脸，然后是下巴，下巴下面一行深一点的阴影；嘴鼻附近不要画深色点和竖线。
- **身体**：深蹲的武士架势，两腿分得很开；近处（画面左边）的肩膀是银色的层叠羽片肩甲，两条前臂戴银色护臂；浅蓝色的布从远处的肩膀斜搭过裸露的胸口；一根细皮带斜过胸前；金黄色的粗绳腰带，近处垂下两段短穗；深藏青色的宽大裤子在膝盖处鼓起；深灰护胫，棕褐色的赤脚。
- **刀**：细长微弯的刀，2 格粗（一行银白的刃口加一行蓝灰的刀身），一个小小的银色刀镡，深色的刀柄握在手里；和身体之间用描边隔开。不要画刀鞘、酒葫芦和笛子。
- **朝向**：3/4 正面朝右，看得到两只眼睛。EQ 转圈、Q 刺出时身体会侧过去，按参考图画；其他帧都把脸转向观众，不画背影。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号。
- 角色图只画角色本身。旋风、风墙、刀光、护盾都是单独的特效图，不要画进角色图。
- 如果模型不肯画带名字的角色，把 "Yasuo" / "League of Legends" 删掉，只保留外观描述。

## 所有特效图的规则

- 没有黑描边。
- 颜色（风系，白色的核心）：
  - 风：`#FFFFFF`、`#D8F6FF`、`#9ED9F2`、`#5AAEDC`、`#2E73B0`、`#173C6E`；
  - 刀光：`#FFFFFF`、`#E6EEF2`、`#A9C4D6`；
  - 尘土：`#E8E4D8`、`#A8A290`。
- 飞行类特效一律**朝右**画，游戏会按方向旋转；命中类特效居中画。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。

---

## 角色（11 张）

### 1. `yasuo_native.png`：造型图

附五张图：`yasuo_native_design.png`、`tfm2_style_ref_swordsman.png`、`yasuo_model_chibi.png`、`tfm2_face_ref_male.png`、`pack_native_ref.png`（看不清姿势时可再附 `yasuo_pose_design.png`）。

**直接按原尺寸逐格画，不要先画大图再缩小**（德莱厄斯第一轮的碎点和糊掉的眼睛就是缩小造成的）。如果生图接口不可用，请先告诉用户，不要用缩小大图的办法凑。交接说明里请写明两只眼睛每一格的颜色。画完这一张就停下，等审过再画动作图。

```text
Five attached images. FIRST: League of Legends' Yasuo rendered at our game's exact sprite size with chibi proportions and shown enlarged 8x - every game pixel is an 8x8 block. Its size, pose and place are right, but it is a blurry downscaled 3D render: too many colors, no outline, details that do not read. SECOND: official heroes of the game Teamfight Manager 2 - swordsmen and quick fighters (a swordsman, a dual-blade dancer, a ninja, a knife juggler, a hunter, a berserker), top row idle, bottom row attacking, also at 8x - this is the pixel size and the cleanliness to match: big flat areas, few colors, a 1-pixel dark outline, bold readable heads with clear eyes, blades drawn as crisp thin lines. THIRD: Yasuo's in-game model with the same chibi proportions - front, side and back, and on the right a close-up of his head in 3/4 view - use it for his hair, clothes, armor, colors and face, not for the level of detail. FOURTH: heads of official heroes enlarged 12x - copy how their eyes are built, and how the gladiator's short beard is drawn. FIFTH: six heroes of this pack drawn at this exact size - match their pixel size, outline and cleanliness.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size: a sprite 34 pixels tall from the top of his head to the soles of his feet (his ponytail rises higher), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow. Work directly at this size, placing every square deliberately - do NOT draw a bigger picture and shrink it.
Yasuo from League of Legends (default skin): a wandering samurai swordsman in a deep, wide, low stance, knees bent far apart, leaning slightly forward, holding his long katana low in front of his belt with the blade trailing far behind him to the left.
Head: dark reddish-brown hair swept back from his forehead, a lock of hair in front of his near ear; at the back of his crown a small gold ring ties a HUGE spiky ponytail that flares up and back to the upper left - the biggest shape above him, about 12 squares long and 8 tall, in 3 dark reddish-brown shades with spiky tips. Tanned skin, thick dark eyebrows angled down toward his nose (a stern, calm look), a short stubble.
Body: bare tanned chest and belly (1-2 darker squares hint the muscles), a thin brown leather strap across the chest; a light-blue cloth hangs over his FAR shoulder and drapes diagonally across his chest to his belt (3 blue shades); his NEAR shoulder (on the left of the image) wears a big silver-grey pauldron of 3-4 overlapping curved plates like feathers, pointing up and back - his second signature shape; silver bracers on both forearms; a thick golden-yellow rope belt with a knot and two short tassels hanging on the near side; very wide dark navy trousers puffing out at the knees; dark grey shin guards; bare tanned feet.
Katana (must read at game size): a long, thin, slightly curved blade, 2 squares thick - one row of silver-white cutting edge over one row of steel blue-grey - with a near-black outline around the blade, a small silver guard and a dark wrapped handle in his hand; the blade trails behind him to the left, about 20 squares long, separated from his body by the outline. No scabbard, no gourd, no flute.
Pixel rules (most important): at most 20 colors in total: hair 3 dark reddish-browns, skin 3 tans, the blue cloth 3 blues, the armor and blade 3 steel greys plus one near-white, the trousers 2 dark navies, gold 2-3 shades (hair ring, rope belt), an eye white, a dark brown iris, a near-black outline; big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and around each part (head, ponytail, pauldron, arms, belt, each leg, the katana). The pauldron plates are only 3-4 curved lines, no engravings; no pattern on the trousers.
Face (most important), built like the heads in the FOURTH image. He faces right, so his NEAR eye is on the LEFT and is 2 squares wide and 3 rows tall: the top row two near-black squares (his thick brow); the middle row a pale highlight square on the left and a near-black pupil on the right; the bottom row an eye-white square on the left and a dark brown iris on the right. Then 1-2 columns of skin. Then his FAR eye, 1 square wide and 3 rows tall, against the right edge of his face: a near-black brow, a near-black pupil, a dark brown iris. Under the eyes about 2 rows of tanned face, then his jaw and chin; his stubble is only the jaw's lowest row in one slightly darker warm tan, never near-black and never dots; one darker row under the chin separates it from the neck. NO mouth, no nose line, no other dark squares on the lower face. A 1-square near-black outline all around his head and face, down the far cheek to the chin too - the face never touches the background directly; the right side of his head is rounded, never one long straight vertical edge. At game size, even on a near-black background, the head must read at once as "tanned face with two dark eyes under a swept-back brown ponytail".
Pose, size and place: exactly as in the FIRST image - the same low stance, the same height, the soles of his feet on the line 28 squares (224 px) above the bottom of the image, the ponytail and the trailing katana where they are in the FIRST image, the character where he stands in the FIRST image. 3/4 FRONT view facing right: we see his face, chest and both eyes, never his back.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check square by square: he is 34 squares tall from the top of his head to his soles, all squares 8x8 on one grid, at most 20 colors; the near eye on the left is 2 squares wide and 3 rows tall (brow, highlight + pupil, white + iris), the far eye 1 square wide and 3 rows tall; no mouth; an outline all around the face; the ponytail, the silver pauldron, the blue cloth, the gold rope belt and the katana each read at once; everything still reads on a near-black background.
```

10 张动作图的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。造型定稿后 Claude 会在开头里补上头的方块数和定稿的颜色。

**共同开头**（下面每条 `<共同开头>` 处原样贴这一段）：

```text
Three attached images. FIRST: the approved clean pixel-art design of Yasuo at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Yasuo rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: in his stance he is 34 pixels tall from the top of his head to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): only the colors of the FIRST image; big flat areas; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette and around each part (head, ponytail, pauldron, arms, belt, each leg, the katana). His head is EXACTLY the head of the FIRST image, copied square for square, in every frame where he faces us - the same size, the same swept-back hair and gold ring, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square against the right edge of his face, each 3 rows tall) and no mouth. When the SECOND image turns, bows or tilts his head (a spin, a thrust, a fall), turn or tilt that same head - never draw it bigger or smaller. The ponytail flies where the SECOND image puts it, always the same size. Draw the body in every frame as a real drawing of the pose in the SECOND image, not assembled from blocks. The katana is always the same 2-square-thick blade with its outline, as long as in the SECOND image. 3/4 FRONT view facing right; keep his face toward the viewer wherever the SECOND image shows it.
```

### 2. `yasuo_idle.png`：待机，6 帧，3 列 × 2 行

附 `yasuo_native.png` + `yasuo_native_idle.png` + `yasuo_pose_idle.png`。

```text
<共同开头>
Animation: IDLE, 6 frames, a seamless calm loop, as in the SECOND image: he holds his low stance, katana trailing behind him, and breathes slowly - everything from his head down to his thighs sinks by 1 square and rises back exactly as in the SECOND image, while only his shins and feet stay planted (the seam is in his shins, never at his waist or belt); his ponytail sways a little. The head is the same drawing in all 6 frames, it only moves with the body.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 96x88 squares (768x704 px), image 2304x1408; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 3. `yasuo_run.png`：跑步，8 帧，4 列 × 2 行

附 `yasuo_native.png` + `yasuo_native_run.png` + `yasuo_pose_run.png`。

```text
<共同开头>
Animation: RUN loop, 8 frames, as in the SECOND image: a fast, low, forward-leaning samurai run, the katana held back behind him pointing up to the upper left, the ponytail streaming back, the rope-belt tassels flapping; his legs stride in turn. Keep his head in the same column in every frame, as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the soles (or the ground line under them) 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 4. `yasuo_attack.png`：普攻，7 帧，4 列 × 2 行（最后一格空）

附 `yasuo_native.png` + `yasuo_native_attack.png` + `yasuo_pose_attack.png`。

```text
<共同开头>
Animation: BASIC ATTACK, 7 frames, as in the SECOND image: 1 he rises from his stance; 2-3 he raises the katana high above his head, blade pointing up; 4 he slashes it down and across in front of him to the right - the hit lands in frames 4-5; 5 the blade ends low to the right; 6 he recovers with the blade raised forward; 7 back toward his stance. Draw only his body and blade - the slash trail is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 5. `yasuo_skill.png`：Q 斩钢闪（突刺），7 帧，4 列 × 2 行（最后一格空）

附 `yasuo_native.png` + `yasuo_native_skill.png` + `yasuo_pose_skill.png`。

```text
<共同开头>
Animation: STEEL TEMPEST, a lightning-fast thrust, 7 frames, as in the SECOND image: 1 he coils in his stance; 2-3 he draws the katana back at shoulder height, his body turning side-on, the point aimed to the right; 4 he lunges and thrusts the blade straight out to the right at full reach - the thrust is in frame 4; 5-6 he pulls back into a wide stance, arms spread, blade to the right; 7 back toward his stance. Draw only his body and blade - the wind of the thrust is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 6. `yasuo_q3.png`：Q3 放出旋风，8 帧，4 列 × 2 行

附 `yasuo_native.png` + `yasuo_native_q3.png` + `yasuo_pose_q3.png`。

```text
<共同开头>
Animation: GATHERING STORM, the whirlwind release, 8 frames, as in the SECOND image: 1-2 he lifts the katana and swings it back; 3-4 he sweeps it low and wide around in front of him; 5 he whips it up and throws his arm high, the blade pointing straight up - the whirlwind is released in frame 5; 6-7 he holds the blade high, ponytail flying; 8 back toward his stance. Draw only his body and blade - the whirlwind is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 7. `yasuo_eq.png`：EQ 环形斩（转身一圈），8 帧，4 列 × 2 行

附 `yasuo_native.png` + `yasuo_native_eq.png` + `yasuo_pose_eq.png`。

```text
<共同开头>
Animation: SPINNING SLASH (Steel Tempest cast during a dash), 8 frames, as in the SECOND image: he spins once in place with his arms and katana stretched out wide: 1 turning, face to the left; 2 facing us, arms flung wide, blade out to the right - the slash is in frame 2; 3-4 turning again, face to the left; 5-6 facing us, arms wide, blade low to the right; 7 recovering; 8 back toward his stance. In frames 1, 3 and 4 his head is turned as in the SECOND image: turn the same head, keep its size.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 8. `yasuo_skill2.png`：E 踏前斩（冲刺），7 帧，4 列 × 2 行（最后一格空）

附 `yasuo_native.png` + `yasuo_native_skill2.png` + `yasuo_pose_skill2.png`。

```text
<共同开头>
Animation: SWEEPING BLADE, a low dash, 7 frames, as in the SECOND image: 1 he crouches; 2-5 he dashes forward to the right almost horizontally, body stretched low over the ground, the katana held forward low along his body, the ponytail streaming far back behind him; 6 he lands in a low crouch; 7 back toward his stance. The game moves him; the frames stay in place as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 9. `yasuo_ult.png`：R 狂风绝息斩，8 帧，4 列 × 2 行

附 `yasuo_native.png` + `yasuo_native_ult.png` + `yasuo_pose_ult.png`。

```text
<共同开头>
Animation: LAST BREATH, 8 frames, as in the SECOND image: 1-2 he crouches low, katana back, ready to leap; 3 he is in the air, curled, blade raised over his head; 4-6 still in the air he slashes again and again - blade out to the left, then pointing down - the slashes are in frames 4-6; 7 he lands on one knee with a huge sweeping slash, the blade tracing a wide arc; 8 back toward his stance. Airborne frames keep the height of the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 10. `yasuo_hit.png`：受击，2 帧，2 列 × 1 行

附 `yasuo_native.png` + `yasuo_native_hit.png` + `yasuo_pose_hit.png`。

```text
<共同开头>
Animation: HIT, 2 frames, as in the SECOND image: he flinches, head and shoulders pushed back a little, katana still low behind him (frame 1 the strongest), then starts to recover (frame 2).
Layout: exactly like the SECOND image - one row of 2 cells, each cell 96x88 squares (768x704 px), image 1536x704; frame N in the same cell as in the SECOND image, at the same place, the soles 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 11. `yasuo_dead.png`：死亡，7 帧，4 列 × 2 行（最后一格空）

附 `yasuo_native.png` + `yasuo_native_dead.png` + `yasuo_pose_dead.png`。

```text
<共同开头>
Animation: DEATH, 7 frames, as in the SECOND image: 1-4 he sinks to one knee, leaning on his katana, its point stuck in the ground in front of him to the right; 5-7 he lets go and falls onto his side, the katana left standing in the ground beside him - the last frame holds. His lying head is the same head turned on its side, eyes closed as one near-black row.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 96x88 squares (768x704 px), image 3072x1408; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

---

## 技能特效（12 张）

12 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 12. `yasuo_fx_hit.png`：普攻命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0) with a steel slash (#FFFFFF, #E6EEF2, #A9C4D6).
Effect: a KATANA SLASH hit, 5 frames: 1 a thin white slash line cuts diagonally from upper left to lower right across the center; 2 it widens into a bright crescent with a pale cyan edge and two short wind streaks; 3 the crescent at full size, small white sparks flying out; 4 it thins and breaks up; 5 the last cyan specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the slash at most 60% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `yasuo_fx_q_thrust.png`：Q 突刺的风（直线），4 帧

游戏按亚索到目标的方向旋转这张图。命中范围是 45 × 12 格的长条，从亚索身前一直伸到最远处。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0).
Effect: STEEL TEMPEST, a sword thrust of wind shooting to the RIGHT, 4 frames: 1 a thin white line appears at the left of the cell and shoots to the right; 2 it becomes a long narrow spear of wind across the whole cell - a bright white core line, pale cyan edges, a sharp point at the right end, short swirling streaks along it; 3 the full spear flashes brightest; 4 it thins into fading streaks from the left.
Layout: one horizontal row of 4 equal cells, each four times as wide as tall (4:1), image size 2048x128; the spear along the middle height of the cell, as wide as the whole cell and about a quarter of the cell tall, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `yasuo_fx_q_hit.png`：Q 刺中的敌人，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0).
Effect: a PIERCING HIT, 5 frames: 1 a small white star flash at the center; 2 a sharp burst pointing to the right - a white spike with pale cyan wind curls on both sides; 3 the burst at full size; 4 it breaks into small streaks flying to the right; 5 the last specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the burst at most 45% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `yasuo_fx_q_ready.png`：旋风烈斩已就绪（亚索身上），6 帧循环

聚风满两层时一直套在亚索身上，直到放出旋风。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC).
Effect: GATHERING STORM READY, a small whirlwind swirling around a swordsman's waist and sword hand, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. Two or three thin curved wind ribbons circle around the waist of the space, slightly flattened (about 1.6 times wider than tall, 50% of the cell wide), white on the front, pale blue where they pass behind; a few tiny leaves of wind rise from them; the ribbons move around by one step every frame; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `yasuo_fx_tornado.png`：Q3 旋风（飞行物），6 帧循环

（2026-10-05：飞行物的画面跟着飞行方向转，这个竖漏斗往左飞会倒过来。用户要保留漏斗，所以旋风本体不挂画面，改成沿路每 2 tick 在旋风所在位置播一帧漏斗（`ViewEffect` 不旋转），见 `tools/fix/fix_yasuo_q3_stamps.py`。）

游戏按方向移动这张图（朝右飞）。旋风的碰撞范围约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0, #173C6E) with dust (#E8E4D8, #A8A290).
Effect: a WHIRLWIND travelling to the RIGHT, 6 frames, a seamless loop: a tall spinning tornado funnel, narrow at the bottom where it touches the ground and wide at the top, made of 4-5 stacked curved bands of white and pale cyan wind with deeper blue shadows on the back side; a little dust whirls at its foot; the bands shift sideways by one step every frame so it spins; it leans a little forward to the right; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal cells, each 2 times as tall as wide (1:2), image size 768x256; the tornado fills 80% of the cell height, its foot at 92% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 17. `yasuo_fx_knockup.png`：被旋风击飞的敌人，6 帧（1 秒）

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0).
Effect: an enemy KNOCKED UP by a whirlwind, 6 frames over 1 second. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a small whirl of wind spins up under the feet; 2-3 it wraps around the legs and lower body of the space as 2-3 curved rising bands; 4-5 the bands spin higher, around the waist, thinner; 6 they fade into a few rising specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 18. `yasuo_fx_eq.png`：EQ 环形斩（亚索周围），5 帧

范围半径约 25 格（地面上约 50 格宽的扁环）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0) with a steel slash (#FFFFFF, #E6EEF2).
Effect: a SPINNING SLASH around a swordsman, seen from the same slightly top-down game camera, 5 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 70% of the cell height) - never draw the person. 1 a white slash arc starts in front of the space at waist height; 2 it sweeps around into a flattened ring of wind; 3 THE FULL RING: a crisp white-and-cyan slash ring about 2 times wider than tall, 90% of the cell width, centered on the waist of the space, the part in front bright, the part behind it thinner and blue; 4 the ring breaks into curved streaks flying outward; 5 fading specks.
Layout: one horizontal row of 5 equal cells, each twice as wide as tall (2:1), image size 2560x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 19. `yasuo_fx_eq3.png`：EQ3 环形击飞（亚索周围），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0, #173C6E) with dust (#E8E4D8, #A8A290).
Effect: a SPINNING WHIRLWIND SLASH around a swordsman that throws enemies into the air, seen from the same slightly top-down game camera, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 70% of the cell height) - never draw the person. 1 a white slash arc and dust at the feet; 2 a flattened ring of wind spreads out on the ground around the space; 3 THE FULL BURST: the ring (about 2 times wider than tall, 90% of the cell width) throws up a wall of spiraling wind bands all around it, rising to above the head of the space; 4 the spiral bands rise higher and thin out; 5-6 they fade into rising specks and settling dust.
Layout: one horizontal row of 6 equal cells, each twice as wide as tall (2:1), image size 3072x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 20. `yasuo_fx_e_hit.png`：E 穿过的敌人，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0) with a steel slash (#FFFFFF, #E6EEF2).
Effect: a DASHING SLASH THROUGH an enemy, 5 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a long thin horizontal white streak cuts through the space at waist height from left to right; 2 it flashes into a sharp slash with pale cyan wind trails behind it on the left; 3 the slash splits into two thin lines with small sparks; 4-5 they fade from the left.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the slash at most 80% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 21. `yasuo_fx_shield.png`：剑意护盾（亚索身上，2 秒），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0).
Effect: a WIND SHIELD around a swordsman, 6 frames over 2 seconds. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 wind ribbons gather from both sides; 2 they close into an oval bubble outline around the whole space (about 70% of the cell high and 55% wide), drawn only as 3-4 thin curved white-and-cyan wind strokes with gaps, never a filled shape; 3-5 the strokes slide around the bubble, a white glint running along them; 6 the bubble breaks into streaks and fades.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 22. `yasuo_fx_wall.png`：风之障壁（立在亚索面前，4 秒），6 帧循环（未使用：风墙后来从技能里删了）

游戏把这张图转到亚索面对的方向：墙面垂直于前进方向，所以画成竖着的一道窄墙。约 40 格高、8 格厚。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0, #173C6E).
Effect: WIND WALL, a standing wall of wind seen edge-on, 6 frames, a seamless loop: a tall narrow vertical band of streaming wind filling the cell from top to bottom and about a quarter of its width, made of wavy vertical strokes of white, pale cyan and blue flowing upward, brighter in the middle, with small swirls breaking off its left and right edges; the strokes move up by one step every frame; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal cells, each 2 times as tall as wide (1:2), image size 768x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 23. `yasuo_fx_r_slash.png`：R 连斩（每个浮空的敌人身上），8 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind color ramp (#FFFFFF, #D8F6FF, #9ED9F2, #5AAEDC, #2E73B0) with a steel slash (#FFFFFF, #E6EEF2, #A9C4D6).
Effect: LAST BREATH, a flurry of sword slashes on an enemy held in the air, 8 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 50% of the cell height, floating with feet at 70% of the cell height) - never draw the person. 1 a swirl of wind holds the space; 2 a white slash crosses it diagonally; 3 a second slash crosses the other way; 4 a third, horizontal; 5 several thin slash lines at once in a star, sparks flying; 6 one huge bright slash from top right down to bottom left; 7 the slashes break into streaks falling downward; 8 fading specks.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the slashes at most 80% of the cell wide, centered on the space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

帧时长已写进 `native/yasuo_cells.json`；出手时刻导入时按画面对齐技能数据（`league/champion/league_yasuo.data_champion`）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `yasuo_idle.png` | 6 | `idle` | 6 × 278（原版 `Idle1` 1.67 秒一次呼吸） |
| `yasuo_run.png` | 8 | `run` | 8 × 112（原版 `Run1` 0.9 秒两步） |
| `yasuo_attack.png` | 7 | `attack` | 50/50/50/60/70/80/80，第 4–5 帧砍中 |
| `yasuo_skill.png` | 7 | `skill`（Q1、Q2 突刺） | 50/50/50/70/70/80/80，第 4 帧刺出 |
| `yasuo_q3.png` | 8 | `q3`（Q3 放旋风，`CasterAnimation`） | 50/50/50/60/80/80/90/90，第 5 帧放出 |
| `yasuo_eq.png` | 8 | `eq`（EQ、EQ3，`CasterAnimation`） | 50/50/50/50/60/60/70/80，第 2 帧斩出 |
| `yasuo_skill2.png` | 7 | `skill2`（E） | 40/40/50/50/60/70/80 |
| `yasuo_ult.png` | 8 | `ult`（R） | 60/60/80/90/90/90/100/100，第 4–6 帧连斩 |
| `yasuo_hit.png` | 2 | `hit` | 120/120 |
| `yasuo_dead.png` | 7 | `dead` | 100/100/150/150/100/120/400 |
| `yasuo_fx_hit.png` | 5 | 特效 `league_yasuo_hit` | 5 × 60 |
| `yasuo_fx_q_thrust.png` | 4 | 投射物 `league_yasuo_q_thrust`（朝目标方向，45000 × 12000） | 4 × 55 |
| `yasuo_fx_q_hit.png` | 5 | 特效 `league_yasuo_q_hit` | 5 × 60 |
| `yasuo_fx_q_ready.png` | 6 | 状态 `league_yasuo_q_ready`（亚索身上循环） | 6 × 100 循环 |
| `yasuo_fx_tornado.png` | 6 | Q3 旋风（半径 12000）：`tornado` 6 帧循环；2026-10-05 起逐帧拆成 `tornado_0`～`tornado_5`，沿路盖章播放（`league_yasuo_q3_tornado_<i>`，见 `tools/fix/fix_yasuo_q3_stamps.py`） | 6 × 60 循环；盖章每帧 34 |
| `yasuo_fx_knockup.png` | 6 | 特效 `league_yasuo_knockup`（跟随目标，1 秒） | 6 × 167 |
| `yasuo_fx_eq.png` | 5 | 特效 `league_yasuo_eq`（跟随亚索，半径 25000） | 5 × 60 |
| `yasuo_fx_eq3.png` | 6 | 特效 `league_yasuo_eq3`（跟随亚索，半径 25000） | 6 × 70 |
| `yasuo_fx_e_hit.png` | 5 | 特效 `league_yasuo_e_hit`（跟随目标） | 5 × 60 |
| `yasuo_fx_shield.png` | 6 | 特效 `league_yasuo_shield`（跟随亚索，2 秒） | 6 × 333 |
| `yasuo_fx_wall.png` | 6 | 未使用（风墙从技能里删了） | - |
| `yasuo_fx_r_slash.png` | 8 | 特效 `league_yasuo_r_slash`（跟随目标） | 8 × 70 |

`yasuo_native.png` 只用来保持造型一致，不进游戏。特效表：`league_yasuo_fx`（hit、q_hit、knockup、e_hit、shield、q_ready），`league_yasuo_big`（q_thrust、tornado、eq、eq3、r_slash）。

## 姿势参考：英雄联盟原版动作

**客户端动画图**（`animations/skin0.bin`）和技能数据（`yasuo.bin`）：
- 待机 `Idle1` 是一段 13.3 秒的片段，身体一直保持深蹲、刀慢慢换角度；头每 1.67 秒起伏一次（0 ms 最高、800 ms 最低），所以待机取 0–1389 ms 的 6 帧。
- 移动是 `Run1`（0.9 秒两步，压低身子、刀举在身后）。
- 普攻用 `Attack1`（举刀过头再劈下，139–278 ms 劈中）。
- Q1、Q2 的技能数据分别用 `Spell1A`、`Spell1B`（两种突刺），这里用 `Spell1A`；`YasuoQ3` 用 `Spell1C`（从下往上的大挥砍），这里当作 Q3 放旋风。`Spell1_Wind` 只给头发和衣摆做了动画（Q3 就绪时"风吹起来"的叠加层），不是身体动作，不用。
- EQ 用 `Spell1_Dash`（原地转两圈的旋斩），只取能看到脸的几帧。
- E 是 `Spell3`（贴地冲刺），R 是 `Spell4`（跳到空中连斩再落地，原版跳出画面，只保留 15% 的离地高度），死亡 `Death`（单膝跪地拄刀约 2 秒，然后侧倒，刀插在地上）。

**渲染设置**：
- **镜头**：yaw 55、pitch 25，**不镜像**。这一侧看得到 3/4 的脸、胸口和近处的银色肩甲，刀和马尾拖在身后左边。
- **比例**：`head 2.0 legs 0.8 hair 0.5`（马尾保持原版长度）。
- **格子**：96×88 方块，脚底线离底部 10 格（`"cell": [96, 88]`）。
- **Q 刺出**的 110–242 ms 和 **R 在空中**的 300、600、800 ms：原版身体侧过去露后背，朝镜头转 −30 度（`turn`）。
- **笛子**：`Flute` 骨骼在待机里缩成 0，但普攻和死亡片段没有它的轨道，会以原大小飘在身边，所以渲染时去掉（`"hide": ["^flute$"]`）。刀的骨骼叫 `Sword`（`"weapon": "^sword$"`，重新上色时刀按武器上色）。
- **受击**：原版没有受击动作，用待机和死亡 150 ms 按 0.3、0.12 混合。

帧的清单在 [`poses.json`](poses.json)，锚点表在 [`../native/yasuo_cells.json`](../native/yasuo_cells.json)。重新生成：

```bash
python tools/lol/native_pose.py assets/source/yasuo/poses.json --out <文件夹>
python tools/art/native_refs.py --out <文件夹> --style --faces --pack lux --pack ashe --pack leesin --pack soraka --pack darius --pack amumu
```

第二条写出 `tfm2_style_ref_swordsman.png`、`tfm2_face_ref_male.png` 和 `pack_native_ref.png`（还有其他几张风格图，用不到可以删）。原版英雄对照图从游戏的 `bundle.game_data` 读取，只在本地用。

三视图 `yasuo_model_chibi.png`：待机第 0 帧 `Yasuo_Idle1@0`，`--yaw 0`、`90`、`180` 各渲染一张，右边加一张 3/4 侧的头部特写，横向拼接：

```bash
python tools/lol/pose_ref.py --champ Yasuo --frame Yasuo_Idle1@0 --name model_y0 --yaw 0 --pitch 10 --head 2.0 --legs 0.8 --hair 0.5 --hq --size 520 --fit 0.8 --bg 225,225,225 --no-labels --out <文件夹>
python tools/lol/pose_ref.py --champ Yasuo --frame Yasuo_Idle1@0 --name model_face --yaw 55 --pitch 10 --head 2.0 --legs 0.8 --hair 0.5 --hq --size 900 --fit 1.6 --ground 1.35 --bg 225,225,225 --no-labels --out <文件夹>
```
