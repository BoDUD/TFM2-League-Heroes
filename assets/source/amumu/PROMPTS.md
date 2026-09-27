# 阿木木：给 GPT 的生图提示词（直接按游戏原尺寸画）

一共 18 张图：
- 1 张原尺寸造型图；
- 9 张原尺寸动作图；
- 8 张特效图。

生成的 PNG 和 Codex 的交接说明放进一个文件夹，然后告诉 Claude。Claude 按 8×8 方块逐格读色，放回每帧的锚点，接到技能上（`tools/art/import_native.py`）。

走李青、索拉卡、德莱厄斯验证过的路线：直接按原尺寸画，不先画高清动作条。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 跳起来往下砸；被动「诅咒之触」+「绝望光环」：普攻或放技能后哭 4 秒，每秒伤害周围敌人并给他们上诅咒 | `amumu_attack` · `amumu_fx_hit` · `amumu_fx_despair` · `amumu_fx_curse` |
| 技能 1 | Q「绷带牵引」：扔出绷带，粘住第一个敌方英雄并眩晕，然后顺着绷带飞过去 | `amumu_skill` · `amumu_q_pull` · `amumu_fx_q_bandage` · `amumu_fx_q_wrap` |
| 技能 2 | E「阿木木的愤怒」：跺脚发脾气，周围敌人受伤 | `amumu_skill2` · `amumu_fx_e_tantrum` |
| 大招 | R「木乃伊之咒」：蜷起来再跳起，绷带向四周炸开，缠住周围所有敌人（眩晕 1.5 秒） | `amumu_ult` · `amumu_fx_r_burst` · `amumu_fx_r_wrap` |
| 其他 | 待机、跑步、受击、死亡 | `amumu_idle` · `amumu_run` · `amumu_hit` · `amumu_dead` |

## 这一轮的做法

1. **原尺寸姿势参考**：`tools/lol/native_pose.py` 把英雄联盟客户端里阿木木的真实动作直接渲染成游戏尺寸。
   - **比例**：阿木木在英雄联盟里本来就是大头小身子，原版比例（头 1.0、腿 1.0）时头已经占身高的六成多。以前的英雄用头 2.0、腿 0.8，放在阿木木身上头会占九成，所以这里用原版比例（选项对比见下面"头的大小"）。
   - 待机时头顶到脚底 34 px，每个游戏像素取 8×8 方块的平均色，放大 8 倍显示（`amumu_native_*.png`）。
   - 姿势、大小、每帧在格子里的位置都已经算好：动作的前冲保留原版的 70%，死亡保留 65%；普攻原版跳得很高，只保留 30% 的离地高度，E 保留 50%，大招保留 25%。
2. **高清对照**：同一批帧的高清渲染（`amumu_pose_*.png`），格子和位置完全一样。缩小图看不清姿势时看它。
3. **每帧锚点**：记在 `amumu_cells.json` 里。新图画在同样的格子里，按同一个锚点切出来，就站在参考图那一帧的位置上。

**格子**：64×64 方块，脚底线离格子底部 10 格。阿木木身后拖着一条长绷带，躺在地上往左伸出十几格。

## 头的大小（等用户选）

| 方案 | 设置 | 头占身高 | 说明 |
|---|---|---|---|
| A（推荐） | 头 1.0、腿 1.0 | 约 63% | 英雄联盟原版比例，大头是阿木木的标志；头宽 19 格，眼睛有地方画清楚 |
| B | 头 0.8、腿 1.0 | 约 53% | 头小一圈，身体和手脚多几格，更接近团战经理原版英雄 |
| C | 头 2.0、腿 0.8 | 约 91% | 前几个英雄的默认设置；阿木木只剩一颗头，不用 |

本文件夹的参考图按 A 渲染。用户选 B 时把 `poses.json` 的 `chibi` 改成 `{"head": 0.8, "legs": 1.0}` 重新渲染，提示词不用改（B 的头仍然超过身高一半）。

## 生成顺序（重要）

1. **先只生成造型图 `amumu_native.png`**（第 1 条），附五张图（见提示词）。
2. **Claude 和用户审造型图**，逐格对照原版英雄（`tfm2_style_ref_undead.png`、`tfm2_face_ref_undead.png`）：
   - 从头顶到脚底正好 34 个方块（272 px）；身后的长绷带贴在地上；
   - 所有方块都是 8×8、对齐同一个网格，没有半个方块、没有模糊边；颜色不超过 16 种，没有杂色点；
   - **头**：超过身高一半的大圆头，缠着一圈圈横向的绷带，绷带的缝用少量深色短线表示，不要满头碎点；
   - **眼睛**（最重要，满身绷带时最容易看不清）：朝右时近处的眼睛在左边、宽 2 格，远处的眼睛宽 1 格、贴着右边的脸边；每只眼睛 3 行高（最上一行近黑的眼窝，中间一行白色高光挨着亮琥珀色，下面一行琥珀色挨着橙色；远眼是近黑、琥珀、橙）；眼睛四周一圈深紫黑的眼窝，和青绿色的绷带分得开；眼睛下面约 2 行深绿色的脸，然后是下巴；
   - **嘴**：默认不画（原版模型没有嘴）。也可以作为选项加"一格暗红小嘴"，由用户决定；
   - 放到接近黑色的英雄卡片背景上，青绿色的轮廓和两只琥珀色的眼睛仍然看得出；头的右边不是一条直的竖边；
   - 小身子驼着背，细细的绷带手臂垂在身前，手是小爪子；短腿，一双缠着绷带的大圆脚；
   - 3/4 正面朝右，看得到两只眼睛。

   **不对就重画这一张，不要带着错的造型图往下做。**
3. 造型图通过后，9 张动作图**同一批**生成，每张附三张图：
   - 第一张：定稿造型图 `amumu_native.png`；
   - 第二张：对应的 `amumu_native_<动作>.png`（原尺寸姿势参考）；
   - 第三张：对应的 `amumu_pose_<动作>.png`（同一批帧的高清渲染）。
4. 输出排版和第二张附图完全一样：几列几行、每格多大（64×64 个方块）、每帧在第几格。
5. 8 张特效图不附图，可以和动作图同时生成。
6. **交给 Claude 之前请 Codex 整理**（和前几个英雄一样）：
   - 每个像素都是严格对齐的 8×8 纯色块，透明度只有全透明和不透明；
   - 全部角色图共用造型图的调色板，不超过 16 色，去掉孤立的杂色点；
   - **每一帧的头和造型图一样大**（按方块数一样），脸朝观众的帧直接把造型图的头逐格贴进去；头缩起来、倒下的帧按参考图转动同一个头，不要画大画小；
   - **身体要画出来，不要用方块拼**：德莱厄斯那批的身体是在格子上按参考手工拼的，动起来忽大忽小。如果生图做不到，请在交接说明里写明哪些帧是拼的，Claude 会改用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）；
   - 待机 6 帧头的大小不变，只随抽泣上下动；跑步 8 帧头保持在参考图的那一列，不要左右跳 1–2 格；
   - 每帧留在它的格子里、画在哪就是哪，**不要按包围框重新居中**（锚点记在 `amumu_cells.json`）；
   - 附交接说明 `HANDOFF.md`、逐帧记录 `MANIFEST.json`（文件哈希、每帧的包围框、每帧头的大小）和实际用的提示词。
7. 以后要改造型，全部动作图用新造型图整批重画，不和旧批次混用。

## 附图（压缩包里有）

Riot 模型渲染和原版游戏截图只在本地用，不提交到仓库。

| 文件 | 内容 | 用在 |
|---|---|---|
| `amumu_native_design.png` | 原版待机第 0 帧，直接渲染成游戏尺寸（34 px），8 倍显示，128×128 方块画布 | 造型图 |
| `amumu_pose_design.png` | 同一帧的高清渲染，位置相同 | 造型图（看不清时对照） |
| `tfm2_style_ref_undead.png` | 团战经理 2 原版的僵尸、幽灵、死灵法师、食人魔、鬼怪、囚徒，上排待机、下排攻击，8 倍 | 造型图 |
| `amumu_model_chibi.png` | 英雄联盟游戏内模型的正面、侧面、背面 | 造型图 |
| `tfm2_face_ref_undead.png` | 原版僵尸、幽灵、死灵法师、杀手的头，12 倍：眼睛怎么排，深色眼窝里的发光眼睛怎么画 | 造型图 |
| `pack_native_ref.png` | 本包按原尺寸画的拉克丝、艾希、李青、索拉卡、德莱厄斯，8 倍 | 造型图 |
| `amumu_native.png` | 定稿造型图（审完后放进来） | 全部动作图（第一张附图） |
| `amumu_native_<动作>.png` | 原版动作渲染成游戏尺寸，8 倍，按格子排好 | 各自的动作图 |
| `amumu_pose_<动作>.png` | 同一批帧的高清渲染，格子和位置完全相同 | 各自的动作图 |
| `amumu_cells.json` | 每帧锚点在格子里的位置和帧时长（给 Codex 核对位置用） | 整理 |

## 所有角色图的规则

- **像素尺寸（最重要）**：
  - 角色是游戏里的小精灵，站着时从头顶到脚底 34 像素高；
  - 按真正的低分辨率像素画来画，再整体放大 8 倍输出；
  - 每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格；
  - 没有比一个方块更小的东西，没有抗锯齿、模糊、柔光。
- **干净，不要细节**：
  - 整个精灵最多 16 种颜色：绷带 4 个青绿色阶（薄荷白高光、浅青、青绿、深绿），眼睛 4 色（白、亮琥珀、橙、深紫黑眼窝），再加近黑描边；
  - 不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；
  - 1 个方块宽的近黑色描边；
  - 绷带的缠绕用少量深色短横线表示（头上 3–4 道），不要把每条绷带都画出来。
- **脸**：
  - 头超过身高一半，每一帧都和造型图一样大；
  - 眼睛按造型图逐格照抄（近眼在左 2 格宽，远眼 1 格贴脸边，各 3 行），眼睛四周是深紫黑的眼窝；嘴按造型图（默认没有嘴）；
  - 眼睛下面约 2 行深绿色的脸；嘴鼻附近不要画深色点和竖线。
- **身体**：小身子驼背，细手臂、小爪子手，短腿、大圆脚，身上一圈圈绷带；身后拖着一条长绷带贴在地上，1–2 格粗。
- **朝向**：3/4 正面朝右，看得到两只眼睛。空翻、缩成一团时头会转开，按参考图画；其他帧都把脸转向观众，不画背影。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号。
- 角色图只画角色本身。绷带飞行物、冲击波、眼泪都是单独的特效图，不要画进角色图。
- 如果模型不肯画带名字的角色，把 "Amumu" / "League of Legends" 删掉，只保留外观描述。

## 所有特效图的规则

- 没有黑描边。
- 颜色：
  - 绷带：`#F1F8EE`、`#BFE6CF`、`#7FC9AE`、`#3F9A7D`、`#1F5A4A`；
  - 诅咒和绝望（暗紫加一点病态的绿）：`#E6C8FF`、`#B07BE8`、`#6B3FA8`、`#34205A`、`#16102A`，绿 `#9BE8B0`、`#3C8C6A`；
  - 琥珀光：`#FFF6C8`、`#FFD35A`、`#F08A2C`；
  - 眼泪：`#D8FBFF`、`#7FD8F0`、`#3A96C0`。
- 飞行类特效一律**朝右**画，游戏会按方向旋转；命中类特效居中画。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。

---

## 角色（10 张）

### 1. `amumu_native.png`：造型图

附五张图：`amumu_native_design.png`、`tfm2_style_ref_undead.png`、`amumu_model_chibi.png`、`tfm2_face_ref_undead.png`、`pack_native_ref.png`（看不清姿势时可再附 `amumu_pose_design.png`）。

**直接按原尺寸逐格画，不要先画大图再缩小**（德莱厄斯第一轮的碎点和糊掉的眼睛就是缩小造成的）。如果生图接口不可用，请先告诉用户，不要用缩小大图的办法凑。交接说明里请写明两只眼睛每一格的颜色。

```text
Five attached images. FIRST: League of Legends' Amumu rendered at our game's exact sprite size and shown enlarged 8x - every game pixel is an 8x8 block. Its size, pose and place are right, but it is a blurry downscaled 3D render: too many colors, no outline, details that do not read. SECOND: official heroes of the game Teamfight Manager 2 - small undead and monsters (a hopping jiangshi, a ghost, a necromancer, an ogre, a goblin, a prisoner), top row idle, bottom row attacking, also at 8x - this is the pixel size and the cleanliness to match: big flat areas, few colors, a 1-pixel dark outline, bold readable heads with clear eyes. THIRD: Amumu's in-game model, front, side and back - use it for his bandages, colors and eyes, not for the level of detail. FOURTH: heads of official heroes enlarged 12x - copy how their eyes are built, especially the ghost's glowing eyes inside black sockets. FIFTH: five heroes of this pack drawn at this exact size - match their pixel size, outline and cleanliness.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size: a sprite 34 pixels tall from the top of his head to the soles of his feet, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow. Work directly at this size, placing every square deliberately - do NOT draw a bigger picture and shrink it.
Amumu from League of Legends (default skin): a small, sad mummy child wrapped from head to toe in old teal-green bandages. A huge round head, more than half of his height, wrapped in horizontal bands of bandage. Two BIG round glowing eyes peek out of the bandages, each in a dark purple-black socket, glowing bright amber with a white glint. Below the eyes a darker green band of face; no mouth. A tiny hunched body, thin bandaged arms hanging in front of him with small clawed hands, short legs ending in big round bandage-wrapped feet. A long loose bandage end trails from behind his leg along the ground behind him. A sad, droopy pose: head hanging forward, shoulders slumped.
Pixel rules (most important): at most 16 colors in total: the bandages 4 teal-green shades (a pale mint highlight, a light teal, a mid teal-green, a dark green), the eyes white, bright amber, orange and a dark purple-black socket, plus a near-black outline; big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. The bandage wraps on the head are only 3-4 short darker horizontal lines, never a pattern of dots. Drop every other detail.
Face (most important): he faces right, so his NEAR eye is on the LEFT and is 2 squares wide, and his FAR eye is 1 square wide against the right edge of his face. Each eye is 3 rows tall: the top row near-black (the dark socket, a sad brow); the middle row a white glint square beside a bright amber square; the bottom row an amber square beside an orange square. The far eye: near-black, amber, orange. A dark purple-black socket may frame each eye by one square so the glowing eyes stand out from the teal bandages. Under the eyes about 2 rows of dark green face, then his chin with one darker row under it. NO mouth, no nose line, no dark dots around the lower face. The outline of his head is round - never one long straight vertical edge. At game size the head must read at once as "round bandaged head with two glowing amber eyes".
Pose, size and place: exactly as in the FIRST image - the same hunched, sad stance, the same height, the soles of his feet on the line 28 squares (224 px) above the bottom of the image, the trailing bandage on the ground behind him, the character where he stands in the FIRST image. 3/4 FRONT view facing right: we see both eyes.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check square by square: he is 34 squares tall from the top of his head to his soles, all squares 8x8 on one grid, at most 16 colors, the near eye on the left is 2 squares wide and the far eye 1 square, each eye 3 rows tall (socket, glint + amber, amber + orange), no mouth, an outline all around the head, and the eyes still read on a near-black background.
```

9 张动作图的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

**共同开头**（下面每条 `<共同开头>` 处原样贴这一段）：

```text
Three attached images. FIRST: the approved clean pixel-art design of Amumu at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Amumu rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the top of his head to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 16 colors (those of the FIRST image); big flat areas, 4 teal-green shades for the bandages; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame where he faces us - the same size (more than half of his standing height), the same bandage lines, the same two glowing amber eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same face. When the SECOND image tucks, tilts or turns his head (a flip, a fall), turn or tilt that same head - never draw it bigger or smaller. Draw the body in every frame as a real drawing of the pose in the SECOND image, not assembled from blocks. Keep the long loose bandage end trailing from his leg as in the SECOND image, 1-2 squares thick. 3/4 FRONT view facing right; keep his glowing eyes toward the viewer wherever the SECOND image shows them.
```

### 2. `amumu_idle.png`：待机，6 帧，3 列 × 2 行

附 `amumu_native.png` + `amumu_native_idle.png` + `amumu_pose_idle.png`。

```text
<共同开头>
Animation: IDLE, 6 frames, a seamless gentle loop, as in the SECOND image: he stands hunched and sad, head hanging forward, arms dangling in front of him, and sobs - his big head bobs down and up with each sob exactly as far as in the SECOND image; the feet stay planted and the trailing bandage lies still on the ground. The head is the same drawing in all 6 frames, it only moves with the body.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 64x64 squares (512x512 px), image 1536x1024; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 3. `amumu_run.png`：跑步，8 帧，4 列 × 2 行

附 `amumu_native.png` + `amumu_native_run.png` + `amumu_pose_run.png`。

```text
<共同开头>
Animation: RUN loop, 8 frames, as in the SECOND image: a quick, clumsy, hunched shuffle, leaning forward, his little arms swinging; his big round feet slap the ground in turn; his big head bobs a little; the loose bandage trails and flails behind him along the ground. Keep his head in the same column in every frame, as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 64x64 squares (512x512 px), image 2048x1024; frame N in the same cell as in the SECOND image, at the same place and height, the soles (or the ground line under them) 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 4. `amumu_attack.png`：普攻，7 帧，4 列 × 2 行（最后一格空）

附 `amumu_native.png` + `amumu_native_attack.png` + `amumu_pose_attack.png`。

```text
<共同开头>
Animation: BASIC ATTACK, 7 frames, as in the SECOND image: a clumsy hop and slam - 1 he crouches; 2 he springs up curling into a ball, head tucked; 3 he opens up at the top of the hop, arms out; 4-5 he slams down head-first onto the enemy in front of him (to the right) - the hit lands in frame 5; 6-7 he pushes himself back up to his sad stance. In frames 2, 4 and 5 his head is tucked or tilted as in the SECOND image: turn the same head, keep its size.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 64x64 squares (512x512 px), image 2048x1024; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 5. `amumu_skill.png`：Q 扔绷带，7 帧，4 列 × 2 行（最后一格空）

附 `amumu_native.png` + `amumu_native_skill.png` + `amumu_pose_skill.png`。

```text
<共同开头>
Animation: BANDAGE TOSS, 7 frames, as in the SECOND image: 1 he draws back; 2-4 he leans back further and further, winding up, head tilted back; 5 he flings his arms forward and throws (the throw is in frame 5 - draw only his arms and hands, the flying bandage is a separate effect); 6 follow-through, leaning forward; 7 back to his stance.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 64x64 squares (512x512 px), image 2048x1024; frame N in the same cell as in the SECOND image, at the same place and height, the soles 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 6. `amumu_q_pull.png`：Q 顺着绷带飞过去，4 帧，4 列 × 1 行

附 `amumu_native.png` + `amumu_native_q_pull.png` + `amumu_pose_q_pull.png`。

```text
<共同开头>
Animation: PULLED ALONG THE BANDAGE, 4 frames, a seamless loop, as in the SECOND image: he flies forward to the right, his body stretched out horizontally just above the ground, head first, both arms reaching forward along the (invisible) bandage, legs trailing behind, the loose bandage fluttering behind him; his glowing eyes look ahead. The game moves him; the frames only flutter.
Layout: exactly like the SECOND image - one row of 4 cells, each cell 64x64 squares (512x512 px), image 2048x512; frame N in the same cell as in the SECOND image, at the same place and height. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 7. `amumu_skill2.png`：E 发脾气，8 帧，4 列 × 2 行

附 `amumu_native.png` + `amumu_native_skill2.png` + `amumu_pose_skill2.png`。

```text
<共同开头>
Animation: TANTRUM, 8 frames, as in the SECOND image: 1-2 he crouches, fists clenched; 3-5 he jumps up throwing both arms in the air in a rage, face turned up to the viewer; 6 he lands; 7 he stomps down hard, bent over, head bowed, fists pounding - the stomp is in frame 7; 8 back to his stance.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 64x64 squares (512x512 px), image 2048x1024; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 8. `amumu_ult.png`：大招，8 帧，4 列 × 2 行

附 `amumu_native.png` + `amumu_native_ult.png` + `amumu_pose_ult.png`。

```text
<共同开头>
Animation: CURSE OF THE SAD MUMMY, 8 frames, as in the SECOND image: 1-2 he curls up small, head bowed; 3-4 he springs up; 5-6 at the top of the jump he turns to the viewer and flings his arms and legs wide open (the bandages burst out as a separate effect) - the burst is in frames 5-6; 7 he lands, bent over; 8 back to his stance.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 64x64 squares (512x512 px), image 2048x1024; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 9. `amumu_hit.png`：受击，2 帧，2 列 × 1 行

附 `amumu_native.png` + `amumu_native_hit.png` + `amumu_pose_hit.png`。

```text
<共同开头>
Animation: HIT, 2 frames, as in the SECOND image: he flinches backward, head thrown back a little (frame 1 the strongest), then starts to recover (frame 2).
Layout: exactly like the SECOND image - one row of 2 cells, each cell 64x64 squares (512x512 px), image 1024x512; frame N in the same cell as in the SECOND image, at the same place, the soles 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 10. `amumu_dead.png`：死亡，7 帧，4 列 × 2 行（最后一格空）

附 `amumu_native.png` + `amumu_native_dead.png` + `amumu_pose_dead.png`。

```text
<共同开头>
Animation: DEATH, 7 frames, as in the SECOND image: 1 he stands, sobbing; 2-4 he topples over backward; 5-7 he lies on his back, head on the left, his big round feet up in the air - the last frame holds. His lying head is the same head turned on its side, eyes still glowing faintly.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 64x64 squares (512x512 px), image 2048x1024; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 10 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

---

## 技能特效（8 张）

8 张特效的提示词都以同一段画风开头。

### 11. `amumu_fx_hit.png`：普攻命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a bandage color ramp (#F1F8EE, #BFE6CF, #7FC9AE, #3F9A7D, #1F5A4A).
Effect: a clumsy SLAM hit, 5 frames: 1 a pale mint flash where he lands; 2 a burst of teal dust puffs, two or three torn bandage scraps flying out; 3 the puffs spread out; 4 they shrink; 5 the last specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the burst at most 55% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `amumu_fx_q_bandage.png`：Q 飞出去的绷带，4 帧循环

游戏按阿木木到目标的方向旋转这张图。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a bandage color ramp (#F1F8EE, #BFE6CF, #7FC9AE, #3F9A7D, #1F5A4A) with an amber spark (#FFF6C8, #FFD35A).
Effect: BANDAGE TOSS, a sticky bandage flying to the RIGHT, 4 frames, a seamless loop: at the right part of every cell the head of the bandage, a tight knot of pale bandage about a third of the cell height with a small amber spark at its tip; behind it a long wavy bandage ribbon trailing to the LEFT edge of the cell, 2-3 teal shades, its waves shifting a little from frame to frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 2048x256; the ribbon along the middle height of the cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `amumu_fx_q_wrap.png`：Q 粘住的敌人（眩晕 1 秒），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a bandage color ramp (#F1F8EE, #BFE6CF, #7FC9AE, #3F9A7D, #1F5A4A) with amber sparks (#FFF6C8, #FFD35A).
Effect: an enemy CAUGHT by a sticky bandage, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a bandage strip whips in from the left at chest height; 2-3 it wraps twice around the chest and arms of the space (the parts in front of the body drawn, the parts behind it hidden); 4 the wraps pull tight with a pale flash and three small amber stars circling above the head; 5 the wraps and stars hold; 6 they loosen and fade.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 70% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `amumu_fx_curse.png`：诅咒标记（敌人头上），6 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a curse color ramp (#E6C8FF, #B07BE8, #6B3FA8, #34205A) with sickly green (#9BE8B0, #3C8C6A).
Effect: CURSED, a small sad mark floating over an enemy, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. Just above the head of the space a small dark purple wisp shaped like a crying little mummy face, with two tiny sickly green eye dots and a thin purple smoke tail below it; it bobs up and down by one square and its smoke curls; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the mark at most 25% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `amumu_fx_despair.png`：绝望光环（阿木木脚下，每秒放一次），6 帧

画在阿木木身后（地面上），每秒放一次，连起来要像一圈不断的光环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a despair color ramp (#E6C8FF, #B07BE8, #6B3FA8, #34205A, #16102A) with sickly green (#9BE8B0, #3C8C6A) and tears (#D8FBFF, #7FD8F0, #3A96C0).
Effect: DESPAIR, a sorrowful aura around a small crying mummy, seen from the same slightly top-down game camera, 6 frames, one pulse that repeats every second. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 70% of the cell height) - never draw the person. A flattened ring of dark purple-green mist on the ground around the feet of the space, about 1.3 times wider than tall and 90% of the cell width; 1 the ring faint; 2-3 it pulses brighter and wisps of greenish-purple mist rise from it; 4 the brightest, light blue tear drops splash on the ground inside the ring; 5-6 it fades back to faint, so that repeated pulses read as one continuous aura.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `amumu_fx_e_tantrum.png`：E 发脾气的冲击波（阿木木周围），6 帧

原版的圆形范围特效是正圆或略扁的圆（宽高比约 1–1.35），这张也照这个比例画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a bandage color ramp (#F1F8EE, #BFE6CF, #7FC9AE, #3F9A7D, #1F5A4A) with dust greys (#E8E4D8, #A8A290).
Effect: TANTRUM, a shockwave of dust and flying bandage scraps around a small stomping mummy, seen from the same slightly top-down game camera, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 70% of the cell height) - never draw the person. 1 a pale mint flash at the feet; 2 a flattened ring of teal dust bursts outward, torn bandage strips flying out; 3 THE FULL RING: a thick ring of dust and bandage scraps, about 1.3 times wider than tall, filling 92% of the cell width, centered on the feet; 4 the scraps fly beyond it and fall; 5-6 the dust settles and fades.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 17. `amumu_fx_r_burst.png`：R 绷带炸开（阿木木周围），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a bandage color ramp (#F1F8EE, #BFE6CF, #7FC9AE, #3F9A7D, #1F5A4A) with an amber glow (#FFF6C8, #FFD35A, #F08A2C).
Effect: CURSE OF THE SAD MUMMY, dozens of bandages exploding outward from a small mummy in every direction, seen from the same slightly top-down game camera, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 70% of the cell height) - never draw the person. 1 a bright amber-mint flash around the space; 2 long bandage strips shoot out radially along the ground in a flattened star; 3 THE FULL BURST: the bandages reach a flattened ring about 2 times wider than tall and 66% of the cell width, their ends curling and glowing amber; 4 the bandages snap tight like ropes; 5 they fade from the tips inward; 6 the last scraps and small green sparkles.
Layout: one horizontal row of 6 equal cells, each twice as wide as tall (2:1), image size 3072x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 18. `amumu_fx_r_wrap.png`：R 缠住的敌人（眩晕 1.5 秒），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a bandage color ramp (#F1F8EE, #BFE6CF, #7FC9AE, #3F9A7D, #1F5A4A) with an amber glow (#FFF6C8, #FFD35A).
Effect: an enemy ENTANGLED in bandages, 6 frames over 1.5 seconds. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 bandage ends shoot in from both sides at knee and chest height; 2 they wind around the space from the feet up; 3 the space is wrapped in several thick teal bands from the knees to the shoulders (gaps between the bands, the head left free); 4-5 the wraps hold, a faint amber glow pulsing along them; 6 the bandages unravel and fall away.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 70% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

帧时长已写进 `native/amumu_cells.json`；出手时刻导入时按画面对齐技能数据。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `amumu_idle.png` | 6 | `idle` | 6 × 211（原版 `Idle1` 1.27 秒一次抽泣） |
| `amumu_run.png` | 8 | `run` | 8 × 69（原版 `Run` 0.55 秒两步） |
| `amumu_attack.png` | 7 | `attack` | 70/70/80/70/90/80/80，第 5 帧砸中 |
| `amumu_skill.png` | 7 | `skill`（Q 扔绷带） | 70/70/60/70/80/80/90，第 5 帧出手 |
| `amumu_q_pull.png` | 4 | `q_pull`（Q 命中后 `CasterAnimation`，飞过去） | 4 × 75 循环 |
| `amumu_skill2.png` | 8 | `skill2`（E） | 70/70/70/70/70/90/90/90，第 7 帧跺地 |
| `amumu_ult.png` | 8 | `ult`（R） | 70/80/70/70/90/90/90/100，第 5–6 帧炸开 |
| `amumu_hit.png` | 2 | `hit` | 120/120 |
| `amumu_dead.png` | 7 | `dead` | 100/100/100/120/120/200/400 |
| `amumu_fx_hit.png` | 5 | 特效 `league_amumu_hit` | 5 × 60 |
| `amumu_fx_q_bandage.png` | 4 | 投射物 `league_amumu_q_bandage`（朝目标方向） | 4 × 60 循环 |
| `amumu_fx_q_wrap.png` | 6 | 特效 `league_amumu_q_wrap`（跟随目标，1 秒） | 6 × 167 |
| `amumu_fx_curse.png` | 6 | 状态 `league_amumu_curse` / `league_amumu_r_curse`（敌人头上循环） | 6 × 167 循环 |
| `amumu_fx_despair.png` | 6 | 特效 `league_amumu_despair`（跟随阿木木，脚下，每秒一次） | 6 × 167 |
| `amumu_fx_e_tantrum.png` | 6 | 特效 `league_amumu_e_tantrum`（跟随阿木木，半径 28000） | 6 × 60 |
| `amumu_fx_r_burst.png` | 6 | 特效 `league_amumu_r_burst`（跟随阿木木，半径 42000） | 6 × 80 |
| `amumu_fx_r_wrap.png` | 6 | 特效 `league_amumu_r_wrap`（跟随目标，1.5 秒） | 6 × 250 |

`amumu_native.png` 只用来保持造型一致，不进游戏。特效表：`league_amumu_fx`（hit、q_bandage、q_wrap、curse、despair、r_wrap），`league_amumu_big`（e_tantrum、r_burst）。

## 姿势参考：英雄联盟原版动作

**客户端动画图**（`animations/skin0.bin`）：阿木木是老英雄，全是单文件片段。待机 `Idle1`（1.27 秒；`Idle2` 是闲置小动作，不用）；移动只有 `Run`；普攻 `Attack1`（跳起下砸）、`Attack2`（向前扑倒）、`Crit`（空翻）；Q 是 `Spell1`（扔绷带）；`Spell2` 是 0.34 秒的平飞姿势（被绷带拉过去），用作 `q_pull`；E 是 `Spell3`；R 是 `Spell4`；死亡 `Death`（先站着哭，1.1 秒后向后倒下）。

**渲染设置**：
- **镜头**：yaw 40、pitch 25，**镜像**（`"mirror": true`）。镜像时身后的长绷带露在画面左边。yaw 55（前几个英雄的角度）下阿木木的待机头太侧，只看得到一只眼睛。
- **比例**：原版比例 `head 1.0 legs 1.0`（见上面"头的大小"）。
- **格子**：64×64 方块，脚底线离底部 10 格（`"cell": [64, 64]`）。
- **普攻**选 `Attack1`：跳起、缩成一团、头朝下砸下去，保留 30% 的离地高度（`"rise": 0.3`）。第 2、4、5 帧头缩着，转多少度都看不到脸，这是动作本身。
- **大招**：原版跳得很高，保留 25%（`"rise": 0.25`）；733、917 ms 两帧张开手脚时背对镜头，朝镜头转 120 度（`turn`）。
- **死亡**：保留 65% 的位移（向后倒），每帧的最低点按离地高度贴在地面线上。
- **受击**：原版没有受击动作，用待机和死亡 1150 ms（开始向后倒）按 0.3、0.12 混合。

帧的清单在 [`poses.json`](poses.json)，锚点表在 [`../native/amumu_cells.json`](../native/amumu_cells.json)。重新生成：

```bash
python tools/lol/native_pose.py assets/source/amumu/poses.json --out <文件夹>
python tools/art/native_refs.py --out <文件夹> --style --faces --pack lux --pack ashe --pack leesin --pack soraka --pack darius
```

第二条写出 `tfm2_style_ref_undead.png`、`tfm2_face_ref_undead.png` 和 `pack_native_ref.png`（还有其他几张风格图，用不到可以删）。原版英雄对照图从游戏的 `bundle.game_data` 读取，只在本地用。

三视图 `amumu_model_chibi.png`：待机第 0 帧 `Amumu_Idle1@0`，`--yaw 0`、`90`、`180` 各渲染一张，横向拼接：

```bash
python tools/lol/pose_ref.py --champ Amumu --frame Amumu_Idle1@0 --name model_y0 --yaw 0 --pitch 10 --head 1.0 --hq --size 520 --fit 0.8 --bg 225,225,225 --no-labels --out <文件夹>
```
