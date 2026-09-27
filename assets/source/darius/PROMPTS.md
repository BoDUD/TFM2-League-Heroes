# 德莱厄斯：给 GPT 的生图提示词（直接按游戏原尺寸画）

一共 20 张图：
- 1 张原尺寸造型图；
- 9 张原尺寸动作图；
- 10 张特效图。

生成的 PNG 和 Codex 的交接说明放进一个文件夹，然后告诉 Claude。Claude 按 8×8 方块逐格读色，放回每帧的锚点，接到技能上（`tools/art/import_native.py`）。

走李青、索拉卡验证过的路线：直接按原尺寸画，不先画高清动作条。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 双手举斧过头下劈；被动「出血」：普攻和 Q 命中让敌人流血，5 秒内命中 5 次进入「诺克萨斯之力」 | `darius_attack` · `darius_fx_hit` · `darius_fx_bleed` · `darius_fx_might` |
| 技能 1 | Q「大杀四方」：举斧蓄力，抡一整圈，周围敌人受伤流血，每命中一名敌方英雄回血 | `darius_skill` · `darius_fx_q_spin` · `darius_fx_q_heal` |
| 技能 2 | E「无情铁手」：斧钩扫过前方扇形，把敌人拉到身边；合并 W「致残打击」：之后的下一次普攻贴地横扫，重伤并减速 | `darius_skill2` · `darius_fx_e_sweep` · `darius_fx_e_hook` · `darius_w_attack` · `darius_fx_w_ready` · `darius_fx_w_hit` |
| 大招 | R「诺克萨斯断头台」：跳起来把斧头砸在目标身上，真实伤害 | `darius_ult` · `darius_fx_r_impact` |
| 其他 | 待机、跑步、受击、死亡 | `darius_idle` · `darius_run` · `darius_hit` · `darius_dead` |

## 这一轮的做法

1. **原尺寸姿势参考**：`tools/lol/native_pose.py` 把英雄联盟客户端里德莱厄斯的真实动作，直接渲染成游戏尺寸。
   - Q 版比例：头 2 倍、腿 0.8 倍。头从发尖到下巴约占身高 1/3。
   - 待机时发尖到脚底 34 px，每个游戏像素取 8×8 方块的平均色，放大 8 倍显示（`darius_native_*.png`）。
   - 姿势、大小、每帧在格子里的位置都已经算好：动作的前冲保留原版的 70%，死亡保留 65%；大招原版跳起 5 米多（Q 版身高的 3 倍），只保留 18% 的离地高度。
2. **高清对照**：同一批帧的高清渲染（`darius_pose_*.png`），格子和位置完全一样。缩小图看不清姿势时看它。
3. **每帧锚点**：记在 `darius_cells.json` 里。新图画在同样的格子里，按同一个锚点切出来，就站在参考图那一帧的位置上。

**格子比前几个英雄大**：88×96 方块，脚底线离格子底部 18 格（前几个英雄是 10 格）。巨斧伸直时比人还长，大招砸地时斧刃落在脚底线下面十几格（镜头俯视，斧刃在他身前的地上，画面上就比脚低）。

## 生成顺序（重要）

1. **先只生成造型图 `darius_native.png`**（第 1 条），附四张图（见提示词）。
2. **Claude 和用户审造型图**，逐格对照原版英雄（`tfm2_style_ref_warrior.png`）：
   - 从发尖到脚底正好 34 个方块（272 px），斧刃再往下 4 格；
   - 所有方块都是 8×8、对齐同一个网格，没有半个方块、没有模糊边；颜色不超过 20 种，没有杂色点；
   - **头发盖住头**：黑发盖住头顶、后脑和两侧，一直到耳朵，近侧有鬓角；发际线压得低，眉毛上面只露 1–2 行额头；头顶一撮往上往后竖的刺发；
   - **眼睛**：朝右时近处的眼睛在左边、宽 2 格，远处的眼睛宽 1 格、贴着右边的脸边；每只眼睛 3 行高（最上一行近黑的浓眉，中间一行白色高光挨着近黑瞳孔，下面一行白色挨着灰蓝虹膜）；眼睛下面只露约 2 行脸，然后是下巴和下巴下的阴影；
   - **嘴**：默认不画。也可以作为选项加"一格暗红小嘴"，由用户决定；
   - 头的轮廓是弧形加刺发，不是一条直的竖边；放到接近黑色的英雄卡片背景上，黑发和暗色盔甲仍然看得出轮廓（头发用比描边亮的深灰棕，刺发尖有灰色高光）；
   - 盔甲：暗钢灰三个色阶加亮银包边；巨大的圆形刺肩甲；胸甲银色 V 形领口；上臂露出古铜色肌肉；深红披风在身后，一条深红布垂在两腿前；
   - **巨斧**：画面左边的手（近侧手）提着斧头垂在身侧；黑铁长柄，顶端一个大铁环，底端一片巨大的银色双月牙斧刃（带钩尖、中间一格白色徽记），斧刃落在脚边；斧柄和身体之间有描边隔开；
   - 3/4 正面朝右，看得到脸和胸口。

   **不对就重画这一张，不要带着错的造型图往下做。**

   **第一轮结果（2026-09-27）**：Codex 本机的生图接口返回 404，改用桥接流程生成了一张 1254 px 的大图，再用最近邻缩成 34 格。高度、8×8 网格、20 色、站姿、发型、深红前摆都对，但有 4 处没过：
   - 近眼只有两行（白色加灰块，没有近黑瞳孔），远眼上下颠倒；
   - 右脸没有描边；
   - 肩甲和胸口满是单格的银白碎点；
   - 斧刃是一团碎块，看不出双月牙和徽记。

   用户选择让 Codex 按第 1b 条再画一版：保留姿势、大小、发型和配色，逐格重画，不再缩小大图。

   **第二轮结果（2026-09-27）**：Codex 修好了本机生图接口的 404，但生成的图仍做不到逐格精确，所以直接在第一轮候选的 128×128 格子上逐格改。眼睛、眼下两行脸、脸的描边、肩甲、银色 V 领和铁环都对了，18 种颜色。还差两处，Claude 逐格改好，用户选定后定稿为 [`../native/darius_native.png`](../native/darius_native.png)（比第二轮改了 181 格）：
   - 深红太少：前襟从 2 列加宽到 4 列，两条腿后面各露出一点披风；
   - 斧刃是对称的心形/V 字：照模型改成双月牙斧。左边一把高高的大月牙刃，右边一把小月牙刃压在画面左边那条腿的小腿前面，暗铁斧心上一条白色徽记，刃尖和斧柄之间有弧形凹口；整个斧头约 17 格宽、15 格高，最下面比靴底低 5 格；
   - 用户选了一格暗红小嘴：(68, 73)，`#77182B`。

   9 张动作图都以这张定稿为第一张附图。

   **动作图的结果（2026-09-27）**：Codex 交回 9 张动作图和 10 张特效（[`codex/HANDOFF.md`](codex/HANDOFF.md)）。它说生图结果的大小、头和斧刃都漂移，最后在 88×96 的格子上按参考手工拼了身体，头和斧刃从定稿逐格复制。动起来很怪：身体在出招时忽大忽小，披风是红色方块，跑步时斧柄是一根竖着的黑杆，躺倒后斧头飘在半空。另外参考图本身浮空 5 格（`native_pose.py` 把斧尖当成了地面，已改成按靴底算锚点）。
   - 用户选了用英雄联盟原版动画重做 9 张动作图：`native_pose.py --alpha --parts` 在游戏尺寸下渲染每一帧和它的部位图，[`tools/art/restyle_native.py`](../../../tools/art/restyle_native.py) 按本文件夹 `poses.json` 的 `restyle` 把每个 8×8 块投票成定稿的 18 色，描边画在轮廓外，头换成定稿的头。肩甲放大 1.4 倍（`chibi.scale`）。写出的 `native/darius_<动作>.png` 和交付的格式一样，由 `import_native.py` 导入。
   - 10 张特效用 Codex 画的（本文件夹的 `darius_fx_*.png`），由 `tools/art/import_darius.py` 导入：围着人画的放大 2 倍，Q 旋风放大后半径约 29 px，所以 Q 的范围改成 32000。
3. 9 张动作图**同一批**生成，每张附三张图：
   - 第一张：新造型图 `darius_native.png`；
   - 第二张：对应的 `darius_native_<动作>.png`（原尺寸姿势参考）；
   - 第三张：对应的 `darius_pose_<动作>.png`（同一批帧的高清渲染）。
4. 输出排版和第二张附图完全一样：几列几行、每格多大（88×96 个方块）、每帧在第几格。
5. 10 张特效图不附图，可以和动作图同时生成。
6. **交给 Claude 之前请 Codex 整理**（和李青、索拉卡那批一样）：
   - 每个像素都是严格对齐的 8×8 纯色块，透明度只有全透明和不透明；
   - 全部角色图共用造型图的调色板，不超过 20 色，去掉孤立的杂色点；
   - **每一帧的头和造型图一样大**（按方块数一样），最好直接把造型图的头逐格贴进每一帧；
   - **待机 6 帧用同一个头**（从造型图取），只随身体上下移动，这样循环不会抖；起伏是"低、低、高、高、高、低"，每次只差 1 格；
   - 跑步 8 帧的头也保持同一列，不要左右跳 1–2 格；
   - 每帧留在它的格子里、画在哪就是哪，**不要按包围框重新居中**（锚点记在 `darius_cells.json`）；
   - 附交接说明 `HANDOFF.md`、逐帧记录 `MANIFEST.json`（文件哈希、每帧的包围框、每帧头的大小）和实际用的提示词。
7. 以后要改造型，全部动作图用新造型图整批重画，不和旧批次混用。

## 附图（压缩包里有）

Riot 模型渲染和原版游戏截图只在本地用，不提交到仓库。

| 文件 | 内容 | 用在 |
|---|---|---|
| `darius_native_design.png` | 原版待机第 0 帧，直接渲染成游戏尺寸（34 px），8 倍显示，128×128 方块画布 | 造型图 |
| `darius_pose_design.png` | 同一帧的高清渲染，位置相同 | 造型图（看不清时对照） |
| `tfm2_style_ref_warrior.png` | 团战经理 2 原版的狂战士、处刑者、锤手、攻城者、骑士、大力士（重武器、盔甲），上排待机、下排攻击，8 倍 | 造型图 |
| `darius_model_chibi.png` | 英雄联盟游戏内模型的正面、侧面、背面，Q 版比例 | 造型图 |
| `pack_native_ref.png` | 本包按原尺寸画的拉克丝、艾希、李青、索拉卡，8 倍 | 造型图 |
| `darius_native_round1.png` | Codex 第一轮造型候选（没通过），8 倍 | 造型图第二版（1b） |
| `tfm2_face_ref_male.png` | 原版角斗士、骑兵、魔剑士、杀手的头，12 倍：眼睛怎么排 | 造型图第二版（1b） |
| `darius_native.png` | 定稿造型图（第二轮加上 Claude 改的深红、双月牙斧和小嘴），8 倍，128×128 方块画布 | 全部动作图（第一张附图） |
| `darius_native_<动作>.png` | 原版动作渲染成游戏尺寸，8 倍，按格子排好 | 各自的动作图 |
| `darius_pose_<动作>.png` | 同一批帧的高清渲染，格子和位置完全相同 | 各自的动作图 |
| `darius_cells.json` | 每帧锚点在格子里的位置和帧时长（给 Codex 核对位置用） | 整理 |

## 所有角色图的规则

- **像素尺寸（最重要）**：
  - 角色是游戏里的小精灵，站着时从发尖到脚底 34 像素高；
  - 按真正的低分辨率像素画来画，再整体放大 8 倍输出；
  - 每个像素是一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格；
  - 没有比一个方块更小的东西，没有抗锯齿、模糊、柔光。
- **干净，不要细节**：
  - 整个精灵最多 20 种颜色，每种材质 2–3 个平涂色阶；
  - 不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；
  - 1 个方块宽的近黑色描边。
- **脸**：
  - 头约占身高 1/3，每一帧都和造型图一样大；
  - 古铜色皮肤 2–3 个色阶；眼睛按造型图逐格照抄（近眼在左 2 格宽，远眼 1 格贴脸边，各 3 行）；嘴是一格暗红 `#77182B`，和造型图同一格（两眼之间那一列、眼睛下面第 2 行）；
  - 黑发盖住头顶、后脑和两侧，发际线压低，不遮眼；嘴鼻附近不要画深色点和竖线。
- **盔甲和披风**：暗钢灰 3 个色阶加亮银包边；圆形刺肩甲；深红披风和前摆 2 个色阶。
- **巨斧**：
  - 斧柄 1 格宽的黑铁色，顶端一个约 3×3 格的铁环；
  - 斧头照造型图逐格画，每帧一样大（约 17 格宽、15 格高）：暗铁斧心上一条白色徽记，一边一把高高的大月牙刃，另一边一把小月牙刃，刃口一条淡青色，刃尖和斧柄之间有弧形凹口；不要画成心形、V 字或一整块扇形；
  - 和手、腿、头之间有描边或颜色隔开，斧刃不和身体粘成一团；
  - 按参考图的位置和握法画，单手提斧时一直在同一只手（近侧手，画面左边）。
- **朝向**：3/4 正面朝右，看得到脸和胸口。转身、抡斧时也把脸和胸口转向观众，不画背影。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号。
- 角色图只画角色本身。刀光、血、火焰都是单独的特效图，不要画进角色图。
- 如果模型不肯画带名字的角色，把 "Darius" / "League of Legends" 删掉，只保留外观描述。

## 所有特效图的规则

- 没有黑描边。
- 颜色用诺克萨斯的血与钢：
  - 血红：白色核心 → 淡粉 → 猩红 → 深红 → 暗红黑（`#FFFFFF`、`#FFC2B8`、`#FF3B30`、`#B3121F`、`#5A0710`）；
  - 钢：`#F2F6F8`、`#BFC8CF`、`#7E8A94`、`#3C434A`；
  - 暗焰（诺克萨斯之力）：`#FFD9A0`、`#FF6A2B`、`#D11E1E`、`#6E0A12`、`#2A0508`。
- 飞行、扫击类特效一律**朝右**画，游戏会按方向旋转；命中类特效居中画。
- 套在人身上的特效：格子中间留出一个空的人形位置（人高约占格子 60%，脚在格子高度 88% 处），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。

---

## 角色（10 张）

### 1. `darius_native.png`：造型图

附四张图：`darius_native_design.png`、`tfm2_style_ref_warrior.png`、`darius_model_chibi.png`、`pack_native_ref.png`（看不清姿势时可再附 `darius_pose_design.png`）。

```text
Four attached images. FIRST: League of Legends' Darius rendered at our game's exact sprite size and shown enlarged 8x - every game pixel is an 8x8 block. Its size, pose and place are right, but it is a blurry downscaled 3D render: too many colors, no outline, details that do not read. SECOND: official heroes of the game Teamfight Manager 2 carrying heavy weapons and armor (a berserker with axes, an executioner with a big axe, a hammer knight, an armored siege breaker, a knight, a strongman), top row idle, bottom row attacking, also at 8x - this is the pixel size and the cleanliness to match: big flat areas, few colors, a 1-pixel dark outline, bold readable heads with clear eyes. THIRD: Darius's in-game model with chibi proportions, front, side and back - use it for his armor, colors, hair and axe, not for the level of detail. FOURTH: four heroes of this pack drawn at this exact size - match their pixel size, outline and cleanliness.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size: a sprite 34 pixels tall from the tips of his hair to the soles of his boots, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow.
Darius from League of Legends (default skin), chibi: a grim, broad-shouldered Noxian general. Black hair swept up into a short spiky crest on top of his head, cut short at the sides, with sideburns; thick black eyebrows in a fierce frown; grey-blue eyes; a tanned face with a strong square jaw. Dark steel plate armor (black-grey) with bright silver edges: huge round shoulder pauldrons with short spikes, a chest plate with a silver V-shaped collar, spiked knee guards, black gauntlets and armored boots; bare muscular upper arms (tanned skin) between the pauldrons and the forearm guards. A dark crimson cape hangs behind him and a crimson cloth hangs in front between his legs. He holds his giant battle-axe in his far hand (on the left side of the image), hanging down at his side: a long dark iron handle with a big iron ring at its top end (near his shoulder), and at its bottom end a huge double crescent blade of silver steel with a hooked point and a white emblem in its middle; the blade hangs by his feet.
Pixel rules (most important): at most 20 colors in total; every material 2-3 flat shades (light, base, shadow); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Keep only details that read at this size: the hair 3 dark shades that are LIGHTER than the outline (a dark grey-brown fill and a grey highlight on the spikes) so the head still reads on a near-black background; the armor 3 steel greys plus a silver trim line on the edges of the plates; each pauldron a big rounded plate with 1-2 one-square spikes; the skin 2-3 tans; the cape and the front cloth 2 crimson shades. The axe handle a 1-square dark iron line, the ring about 3x3 squares, the blade about 9-10 squares wide and 8-9 squares tall, silver with a row of pale cyan highlight along its edge and one white square in its middle. Keep a dark outline or a different color between the axe and his hand, legs and body, so the blade never merges with his boots. Drop every other trim, rivet and pattern.
Face: the head is one third of his height. The hair covers the top, the back and the sides of his head down to his ears, with a sideburn on the near side, and leaves only 1-2 rows of forehead above the brows. He faces right, so his NEAR eye is on the LEFT and is 2 squares wide, and his FAR eye is 1 square wide against the right edge of his face. Each eye is 3 rows tall: the top row near-black (his thick angry brow), the middle row a white highlight square beside a near-black pupil, the bottom row white beside a grey-blue iris. Under the eyes only about 2 rows of tanned face, then his jaw and one darker row under the chin. NO mouth - at this size a mouth only makes the face look odd; no dark squares or lines around the nose and mouth. The outline of his head is rounded with the spiky crest on top - never one long straight vertical edge. At game size the head must read at once as "tanned face, black spiky hair, angry eyes".
Pose, size and place: exactly as in the FIRST image - the same menacing stance, the axe hanging from his far hand, the same height, the soles of his boots on the line 32 squares (256 px) above the bottom of the image and the axe blade reaching 4 squares lower, the character where he stands in the FIRST image. 3/4 FRONT view facing right: we see his face and chest.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: he is 34 squares tall from the tips of his hair to his soles, all squares 8x8 on one grid, at most 20 colors, the near eye on the left is 2 squares wide and the far eye 1 square, each eye 3 rows tall, no mouth, the hair covers his head, and the axe is separated from his body by an outline.
```

### 1b. `darius_native.png`：造型图第二版（按第一轮候选修订）

附五张图：`darius_native_round1.png`（第一轮候选）、`darius_native_design.png`、`tfm2_face_ref_male.png`（原版角斗士、骑兵、魔剑士、杀手的头，12 倍）、`tfm2_style_ref_warrior.png`、`darius_model_chibi.png`。

**直接按原尺寸逐格画，不要先画大图再缩小**（第一轮的碎点和糊掉的眼睛就是缩小造成的）。如果生图接口仍然不可用，请先告诉用户，不要用缩小大图的办法凑。交接说明里请写明两只眼睛每一格的颜色。

```text
Five attached images. FIRST: a first pixel-art draft of Darius at our game's exact sprite size, shown enlarged 8x - every game pixel is an 8x8 block. Keep its pose, its size and its place on the canvas, its hair, its palette and its costume colors. But it was made by shrinking a bigger picture, so it is noisy and several parts do not read - redraw it cleanly, square by square, at this exact size. SECOND: League of Legends' Darius rendered at this size (a blurry 3D render) - his pose and where the axe hangs. THIRD: heads of official Teamfight Manager 2 heroes enlarged 12x - copy how their eyes are built. FOURTH: official heroes with heavy weapons and armor at 8x - the cleanliness to match: big flat plates, few colors, a 1-pixel dark outline. FIFTH: Darius's in-game model with chibi proportions - his armor and his axe.
Task: redraw the FIRST image as clean hand-made pixel art at EXACTLY the same pixel size and place: 34 pixels from the tips of his hair to his soles, the soles on the line 32 squares above the bottom of the 128x128-square canvas, the axe blade 4 squares lower. Work directly at this size, placing every square deliberately - do NOT draw a bigger picture and shrink it. Every pixel one crisp 8x8 square on one 8-px grid; at most 20 colors; no anti-aliasing, no blur.
Fix these five things and keep everything else of the FIRST image:
1. EYES (most important), built like the heads in the THIRD image. He faces right. His NEAR eye is on the LEFT, 2 squares wide and 3 rows tall: the top row two near-black squares (his thick angry brow); the middle row a pale highlight square on the left and a near-black pupil on the right; the bottom row a white square on the left and a grey-blue iris on the right. Then 1-2 columns of skin. Then his FAR eye, 1 square wide and 3 rows tall, near the right edge of his face: a near-black brow, a near-black pupil, a dark grey-blue iris. Under the eyes 2 rows of tanned skin, then his jaw with one darker row under the chin. NO mouth and no nose line.
2. OUTLINE: a 1-square near-black outline all around his head and face, down the far cheek to the chin too - the face never touches the background directly.
3. ARMOR, flat and clean: each round shoulder pauldron one big plate in 3 steel greys with a 1-square silver rim and 1-2 one-square spikes; the chest plate dark steel with one silver V-shaped collar; spiked knee guards; dark gauntlets and boots. No lone speckles: never a single white, silver or grey square scattered inside a plate.
4. AXE, bold and clear: a 1-square dark iron handle line from his far hand; a 3x3-square iron ring at its top end, above and behind his shoulder; at its bottom end a big double crescent blade about 9-10 squares wide and 8-9 tall - two curved silver blades back to back, a row of pale cyan along their cutting edges, one white square emblem in the middle, a dark outline all around - hanging by his feet and separated from his boots by an outline.
5. Keep his black spiky hair covering the top, back and sides of his head down to his ears (drawn in dark grey-brown shades lighter than the outline), his tanned skin, bare tanned upper arms, the crimson cape and the crimson cloth hanging in front of his legs.
3/4 FRONT view facing right. Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check square by square: 34 squares tall, all squares 8x8 on one grid, at most 20 colors; the near eye on the left is 2 wide and 3 tall (brow, highlight + pupil, white + iris), the far eye 1 wide and 3 tall; no mouth; an outline all around the face; no lone speckles on the armor; the axe reads at once as ring, handle and double crescent blade.
```

9 张动作图的提示词都以同一段开头，可以整段复制；每张只有最后的动作说明和排版不同。

### 2. `darius_idle.png`：待机，6 帧，3 列 × 2 行

附 `darius_native.png` + `darius_native_idle.png` + `darius_pose_idle.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: IDLE, 6 frames, a seamless gentle loop, as in the SECOND image: he stands firm and menacing, the huge axe hanging from the hand on the left of the image with its blade by his feet, his other hand at his side, and breathes slowly - his body (not the boots) is one square lower in frames 1, 2 and 6 than in frames 3, 4 and 5; the axe moves with his hand; the cape sways a little. The head is exactly the same drawing in all 6 frames, it only moves up and down with the body; the boots stay planted.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2112x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 3. `darius_run.png`：跑步，8 帧，4 列 × 2 行

附 `darius_native.png` + `darius_native_run.png` + `darius_pose_run.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: RUN loop, 8 frames, as in the SECOND image: a heavy, powerful bounding run, leaning forward; he carries the axe low in the hand on the left of the image, the ring end up behind his shoulder and the blade down by his legs; his other arm swings; one boot on the ground in frames 3 and 7, both boots off the ground in the other frames; his body rises in the air and dips at each landing; the cape streams out behind him. Keep his head in the same column in every frame, as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place and height, the soles (or the ground line under them) 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 4. `darius_attack.png`：普攻，6 帧，3 列 × 2 行

附 `darius_native.png` + `darius_native_attack.png` + `darius_pose_attack.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: BASIC ATTACK, a two-handed overhead axe chop, 6 frames, as in the SECOND image: 1 leaving his stance; 2 he heaves the axe high up behind his head, blade up; 3 he lunges forward, the axe swung back behind him; 4 the axe comes round and down, low; 5 THE HIT: he lunges forward and chops the blade into the ground in front of him (to the right), his cape flying out behind; 6 back toward his stance. Draw no slash and no blood - they are separate effects.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2112x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 5. `darius_skill.png`：Q「大杀四方」，8 帧，4 列 × 2 行

附 `darius_native.png` + `darius_native_skill.png` + `darius_pose_skill.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: DECIMATE, a wind-up and a full-circle axe swing, 8 frames, as in the SECOND image: 1 leaving his stance; 2-3 he heaves the axe up and back over his far shoulder with both hands, winding up; 4 he crouches and starts the swing, the axe low behind him; 5 THE SPIN: he whirls round, the axe held out at full reach to the right; 6 still whirling, the axe swept round behind him to the lower left, his cape flaring out; 7 the axe comes round in front again, reaching out to the right; 8 back toward his stance. The axe is very long at full reach - draw it inside the cell as in the SECOND image. Draw no motion trail - the spin is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 6. `darius_w_attack.png`：W「致残打击」强化普攻，6 帧，3 列 × 2 行

附 `darius_native.png` + `darius_native_w_attack.png` + `darius_pose_w_attack.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: CRIPPLING STRIKE, a low sweeping cut at the enemy's legs, 6 frames, as in the SECOND image: 1 he crouches low, the axe drawn back low behind him; 2 he whirls it low along the ground; 3 the axe low behind him again as he turns; 4 the axe sweeps low in front of his legs; 5 THE HIT: crouched, the blade sweeping at knee height in front of him (to the right); 6 back toward his stance. Draw no slash and no blood - they are separate effects.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2112x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 7. `darius_skill2.png`：E「无情铁手」，8 帧，4 列 × 2 行

附 `darius_native.png` + `darius_native_skill2.png` + `darius_pose_skill2.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: APPREHEND, a hooking pull, 8 frames, as in the SECOND image: 1 leaving his stance, crouching; 2 he leaps forward, swinging the axe low; 3 lunging, he throws the axe forward and down; 4 THE HOOK: the axe held out at full reach far to the right, its hooked blade catching the enemy, both arms stretched out, his body low at the left of the cell; 5-6 he yanks the axe back toward himself; 7 the axe pulled back behind him, crouched; 8 back toward his stance. The axe is very long at full reach - draw it inside the cell as in the SECOND image. Draw no streak and no glow - they are separate effects.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 8. `darius_ult.png`：R「诺克萨斯断头台」，8 帧，4 列 × 2 行

附 `darius_native.png` + `darius_native_ult.png` + `darius_pose_ult.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: NOXIAN GUILLOTINE, a leaping execution, 8 frames, as in the SECOND image: 1 he crouches, gripping the axe; 2 he leaps up, raising the axe over his head with both hands; 3-4 high in the air, the axe held up behind his head; 5 dropping, the axe raised straight up above him; 6 THE SLAM: he lands crouched and drives the blade down into the ground in front of him (to the right; the blade reaches below the line of his soles, exactly as in the SECOND image); 7 holding the slam; 8 standing up toward his stance. He is in the air in frames 2-5 exactly as high as in the SECOND image. Draw no giant axe, no glow and no blood - they are a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 9. `darius_hit.png`：受击，2 帧，2 列 × 1 行

附 `darius_native.png` + `darius_native_hit.png` + `darius_pose_hit.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in both frames - the same black spiky hair, the same eyes and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image, separated from his body by an outline. 3/4 FRONT view facing right, never his back.
Animation: HIT, 2 frames, as in the SECOND image: 1 he flinches from a blow - hunching a little, head dipped, the axe tilting; 2 recovering toward his stance.
Layout: exactly like the SECOND image - a grid of 2 columns x 1 row of cells, each cell 88x96 squares (704x768 px), image 1408x768; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

### 10. `darius_dead.png`：死亡，7 帧，4 列 × 2 行（最后一格空）

附 `darius_native.png` + `darius_native_dead.png` + `darius_pose_dead.png`。

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame. Keep the axe exactly as in the FIRST image. The same camera as the FIRST image.
Animation: DEATH, 7 frames, as in the SECOND image: 1 struck, he doubles over, head down; 2 he twists and staggers; 3 he sinks to his knees; 4 he topples backwards, the axe flung up out of his hands; 5 he falls on his back; 6-7 he lies on the ground, his cape spread under him, the axe lying on the ground beyond his head. Draw the axe exactly where the SECOND image has it, inside the cell. He lies on the ground line in frames 5-7, exactly as high as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

---

## 技能特效（10 张）

10 张特效的提示词都以同一段画风开头。

### 11. `darius_fx_hit.png`：普攻命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94).
Effect: a heavy AXE CHOP hit, 5 frames: 1 a white flash where the blade lands; 2 a thick crescent slash cutting diagonally down from upper left to lower right, white core with a crimson edge; 3 the slash splits and dark red sparks and a few blood drops burst out; 4 the sparks fly apart and shrink; 5 the last red specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the slash at most 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `darius_fx_bleed.png`：出血（敌人身上），5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood color ramp (#FFC2B8, #FF3B30, #B3121F, #5A0710).
Effect: HEMORRHAGE, a bleeding wound, 5 frames: 1 a small red slash glint; 2 three or four fat blood drops spurt up and out from it; 3 the drops arc outward and down; 4 they fall, smaller; 5 two last drops fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the wound at the center of every cell, the whole effect at most 45% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `darius_fx_q_spin.png`：Q 大杀四方（德莱厄斯周围），6 帧

原版的圆形范围特效是正圆或略扁的圆（宽高比约 1–1.35），这张也照这个比例画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94).
Effect: DECIMATE, a giant axe swung in a full circle around a warrior, seen from the same slightly top-down game camera, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 70% of the cell height) - never draw the person. The swing is a slightly flattened ring about 1.3 times wider than tall, filling 92% of the cell width, centered at the person's waist. 1 a short bright arc starts at the right side of the ring, a white-hot leading edge; 2 the arc sweeps round the front and the left: a thick crescent of crimson with a white edge and a steel-grey trail behind it; 3 the arc sweeps round the back, almost closing the ring; 4 THE FULL RING: a complete thick crimson ring with a white-hot outer edge, a few blood drops flung outward; 5 the ring breaks into curved crimson streaks spinning outward; 6 the last dark red wisps fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `darius_fx_q_heal.png`：Q 回血（德莱厄斯身上），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710).
Effect: a warrior drinking in the blood of his enemies, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a few crimson wisps appear at both sides of the cell; 2-3 they curl inward toward the chest of the space as thin red streams with bright tips; 4 a crimson flash at chest height with a pale pink core; 5 a soft red ring pulses out from the chest; 6 the last red specks fade upward.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 70% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `darius_fx_might.png`：诺克萨斯之力（德莱厄斯身后），6 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark fire color ramp (#FFD9A0, #FF6A2B, #D11E1E, #6E0A12, #2A0508).
Effect: NOXIAN MIGHT, a blood-red battle rage aura around a warrior, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person; the aura is drawn BEHIND him, so it may overlap the space. A flat dark red glowing ellipse on the ground at the feet; tongues of crimson and dark red flame rising all around the space up to a little above the head, their tips curling into black-red smoke; small orange-red embers rising; the flames flicker and climb from frame to frame and frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the aura at most 75% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `darius_fx_w_ready.png`：W 准备好（脚下），4 帧循环

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF).
Effect: CRIPPLING STRIKE READY, a menacing mark on the ground under a warrior's feet, seen from the same slightly top-down game camera, 4 frames, a seamless loop: a flattened ellipse ring (about 2.5 times wider than tall) of dark crimson on the ground, with three small blade-shaped steel glints spaced around it; the glints slide around the ring a little each frame and pulse from dark red to bright red, frame 4 leading back into frame 1.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the ring centered at 75% of the cell height, 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 17. `darius_fx_w_hit.png`：W 致残打击命中（敌人身上），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94).
Effect: CRIPPLING STRIKE on an enemy's legs, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a white flash at knee height; 2 a long low horizontal slash across the legs of the space, white core and crimson edge, sweeping from left to right; 3 blood sprays from the slash and a dark red X-shaped wound mark appears at the knees; 4 two short iron chain links snap shut around the ankles, dark red and steel; 5 the chains and the X mark flash once; 6 they fade into red specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 70% of the cell wide, around the lower half of the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 18. `darius_fx_e_hook.png`：E 被钩住的敌人，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94, #3C434A).
Effect: an enemy CAUGHT by an axe hook and yanked toward the LEFT, 5 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a curved steel hook glint snaps shut at chest height on the right side of the space; 2 a crimson jolt bursts from it; 3-4 dark red speed streaks stretch from the space toward the LEFT edge of the cell, showing the pull; 5 the streaks fade.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the effect at most 80% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 19. `darius_fx_e_sweep.png`：E 斧钩扫过前方扇形，5 帧

游戏按德莱厄斯到目标的方向旋转这张图，图的左边中点就是德莱厄斯的位置。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94, #3C434A).
Effect: APPREHEND, a giant axe hook sweeping out in a cone and yanking back, seen from the same slightly top-down game camera, pointing to the RIGHT, 5 frames. The warrior stands at the middle of the LEFT edge of every cell (never draw him): the cone opens from that point to the right, about 90 degrees wide, reaching the right edge. 1 a fan of three or four hooked steel-grey arcs shoots out from the left point toward the right, crimson streaks behind them; 2 THE FULL SWEEP: the hooked arcs reach the right part of the cell, a wide dark red fan glowing behind them; 3 the hooks snap back toward the left point, bright crimson pull streaks pointing left; 4 the streaks converge on the left point; 5 the last dark red wisps fading.
Layout: one horizontal row of 5 equal cells, each twice as wide as tall (2:1), image size 2560x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 20. `darius_fx_r_impact.png`：R 诺克萨斯断头台（砸在目标身上），8 帧

落点在每格底部往上 12% 处（游戏按这个点放在目标脚下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with a dark fire accent (#FF6A2B, #2A0508) and steel greys (#F2F6F8, #BFC8CF).
Effect: NOXIAN GUILLOTINE, a giant ghostly executioner's axe slamming down on a target, 8 frames. The impact point is at the horizontal center of every cell, 12% of the cell height above the bottom edge (the target's feet; never draw the target). 1 a red glint high up near the top of the cell; 2 a huge spectral axe blade (crimson and dark red, with a white-hot cutting edge and a steel-grey handle top) appears high above, raised; 3 it drops fast toward the impact point with a crimson motion trail; 4 THE IMPACT: the blade hits the impact point, a blinding white-red flash; 5 a flattened crimson shockwave ring bursts on the ground around the impact point (about 1.3 times wider than tall, 70% of the cell width), a column of red light rising from it; 6 the ring widens to 90% of the cell width and blood-red shards fly up; 7 the column fades, embers drifting up; 8 the last red embers fading.
Layout: one horizontal row of 8 equal cells, each twice as tall as wide (1:2), image size 2048x512; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

帧时长已写进 `native/darius_cells.json`，出手帧对齐数据里的出手时刻；导入时按画面再微调。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `darius_idle.png` | 6 | `idle` | 6 × 222（原版 `Idle1` 1.33 秒一次呼吸） |
| `darius_run.png` | 8 | `run` | 8 × 142（原版 `Run` 1.13 秒两步） |
| `darius_attack.png` | 6 | `attack` | 60/60/50/50/90/80，第 5 帧砍中（tick 15） |
| `darius_skill.png` | 8 | `skill`（Q） | 80/120/120/80/70/60/70/130，第 5 帧抡出（tick 28） |
| `darius_w_attack.png` | 6 | `w_attack`（W，普攻里的 `CasterAnimation`） | 60/60/60/60/100/140，第 5 帧砍中（动画开始后 tick 16） |
| `darius_skill2.png` | 8 | `skill2`（E） | 60/60/70/60/60/70/100/100，第 4–5 帧回拉（tick 14） |
| `darius_ult.png` | 8 | `ult`（R） | 60/60/80/80/60/100/120/120，第 6 帧砸地（tick 26） |
| `darius_hit.png` | 2 | `hit` | 120/120 |
| `darius_dead.png` | 7 | `dead` | 100/100/100/120/120/200/400 |
| `darius_fx_hit.png` | 5 | 特效 `league_darius_hit` | 5 × 60 |
| `darius_fx_bleed.png` | 5 | 特效 `league_darius_bleed`（跟随目标） | 5 × 80 |
| `darius_fx_q_spin.png` | 6 | 特效 `league_darius_q_spin`（跟随德莱厄斯，半径 36000） | 6 × 50 |
| `darius_fx_q_heal.png` | 6 | 特效 `league_darius_q_heal`（跟随德莱厄斯） | 6 × 80 |
| `darius_fx_might.png` | 6 | 特效 `league_darius_might`（跟随，身后，每 1 秒放一次，共 5 秒） | 6 × 167 |
| `darius_fx_w_ready.png` | 4 | 状态 `league_darius_w_ready`（脚下循环，最多 4 秒） | 4 × 100 循环 |
| `darius_fx_w_hit.png` | 6 | 特效 `league_darius_w_hit`（跟随目标） | 6 × 70 |
| `darius_fx_e_hook.png` | 5 | 特效 `league_darius_e_hook`（跟随被拉的敌人） | 5 × 60 |
| `darius_fx_e_sweep.png` | 5 | 投射物 `league_darius_e_sweep`（朝目标方向，16 tick） | 5 × 55 |
| `darius_fx_r_impact.png` | 8 | 特效 `league_darius_r_impact`（跟随目标） | 8 × 70 |

`darius_native.png` 只用来保持造型一致，不进游戏。特效表：`league_darius_fx`（hit、bleed、q_heal、might、w_ready、w_hit、e_hook），`league_darius_big`（q_spin、e_sweep、r_impact）。

## 姿势参考：英雄联盟原版动作

**客户端动画图**（`animations/skin0.bin`）：
- 德莱厄斯是老英雄，动画图里全是单文件片段，没有条件分支。
- 待机 `Idle1` 循环（`Idle2` 是闲置小动作，不用）；移动只有 `Run`。
- 普攻 `Attack1`、`Attack2`，暴击 `Crit`；Q 是 `Spell1_IN`（蓄力 0.8 秒）接 `Spell1`（抡一圈 0.52 秒）；W 的强化普攻是 `Spell2`（贴地抡两圈）；E 是 `Spell3`；R 是 `Spell4`；死亡 `Death`。

**测量结果**（斧尖 `BuffBone_Cstm_Weapon_9` 和脚的骨骼轨迹）：
- **跑步是跑，不是走**：`Run` 1.13 秒两步，每步落地一次，其余时间双脚离地，头上下起伏很大。
- **待机**：1.33 秒一次呼吸，头的起伏换算到游戏尺寸不到 1 px；动作图里要求画成 1 格的起伏。
- **出手时刻**：普攻斧尖约 330–400 ms 砍到地面；Q 蓄力 0.75 秒后约 0.2 秒抡完一圈；W 约 250–330 ms 贴地扫过身前；E 约 70 ms 甩出斧钩、230–370 ms 回拉；R 从空中开始，约 400 ms 砸地，原版跳起 5 米多。
- 普攻选 `Attack1`：双手举斧过头下劈，最像诺手的招牌动作。`Crit` 也是重劈，但出手后转成背影更多。

**渲染设置**：
- **镜头**：yaw 55、pitch 25，**镜像**（`"mirror": true`）。镜像时待机是 3/4 正面，胸口、脸和挂在近侧手（画面左边）的巨斧都看得清；不镜像时待机偏侧面，Q 蓄力变成背影。全部动作同一侧。
- **比例**：`--head 2.0 --legs 0.8`；德莱厄斯的头发是头部网格的一部分，没有辫子类骨骼，不用 hair。
- **格子**：88×96 方块，脚底线离底部 18 格（`"cell": [88, 96, 18]`）。巨斧伸直时整帧宽 80 格左右；R 砸地时斧刃在脚底线下 16 格。
- **转身**：普攻第 3–6 帧、W 第 4–6 帧朝镜头转 20–100 度（`turn`）。原版这几帧抡斧转到背对镜头。W 的原版动作是贴地抡两整圈，只取面朝右的几帧（0、33、200、267、333 ms）。
- **跳过背影帧**：Q 抡圈时 100 ms 左右正好背对镜头，转多少都是背影，改用 33、167、233 ms 三帧表现一圈；E 在 133–200 ms 头转开，改用 233 ms（斧钩甩到最远、正脸）当"钩住"。
- **大招**：原版跳起 5 米多，保留 18% 的离地高度（`"rise": 0.18`）；390 ms 那帧斧头竖直举过头顶，再早斧尖会出格子。
- **死亡**：保留 65% 的位移（向后倒），每帧的最低点按离地高度贴在地面线上。
- **受击**：原版没有受击动作，用待机和死亡 100 ms（身体前屈）按 0.3、0.12 混合。

帧的清单在 [`poses.json`](poses.json)，锚点表在 [`../native/darius_cells.json`](../native/darius_cells.json)。重新生成：

```bash
python tools/lol/native_pose.py assets/source/darius/poses.json --out <文件夹>
python tools/art/native_refs.py --out <文件夹> --style --faces --pack lux --pack ashe --pack leesin --pack soraka
```

第二条写出 `tfm2_style_ref_warrior.png`、`tfm2_face_ref_male.png` 和 `pack_native_ref.png`（还有其他几张风格图，用不到可以删）。原版英雄对照图从游戏的 `bundle.game_data` 读取，只在本地用。

三视图 `darius_model_chibi.png`：待机第 0 帧 `Darius_Idle1@0`，`--mirror`，`--yaw 40`、`100`、`200` 各渲染一张，横向拼接：

```bash
python tools/lol/pose_ref.py --champ Darius --hq --head 2.0 --legs 0.8 --mirror --yaw 40 --pitch 10 --size 800 --width 0.75 --fit 0.8 --ground 0.92 --bg 225,225,225 --no-labels --out <文件夹> --name view_40 --frame Darius_Idle1@0
```
