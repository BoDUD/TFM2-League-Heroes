# 魔法猫咪 悠米：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的三张（`1_picture_A.png` 坐在书里、`1_picture_B.png` 趴在摊平的书上、`1_picture_C.png` 合上的书）**用户选定了，样子、颜色全照它们**。
> - 这一步要把她画成**游戏里的格子数**：**A 从触须小球顶到书底 48 格**。我把 A 直接缩到这个格子数（`2_target_A.png` / `3_layout_A.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、金饰碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 一共画**六种**（同一只猫、同一本书、同样的颜色）：**A 待机（3/4 正面）**、**S 侧面朝右**、**L 扑出去**、**R 扒着竖起的书**、**B 趴在摊平的书上**、**C 合上的书**。A、S、L、R 各画**两稿**，B 两稿，C 一稿，共 **11 张**。

## 大小和位置

- 画布都用你平时的 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐，**真透明背景**。
- **A、S、L、R：每格 22 px，地面线 y = 1188**（四张同一个格子大小，猫和书一样大）。
  - **A**：照 `2_target_A.png` / `3_layout_A.png`：触须小球顶 **y = 132**（橙线），眼睛约 **y = 528**（蓝线），书底 **y = 1188**（红线）：**48 格高、约 48 格宽**。
  - **S**：同样 **48 格高**（小球顶 y = 132、书底 y = 1188），侧面朝右：`3_side_ref.png` 是英雄联盟模型的侧面按这个大小摆好的（淡色，只看**轮廓、位置和大小**，约 57 格宽；它的头比我们的小，**头照 A 的大小画**）。
  - **L**：照 `3_leap_ref.png`（英雄联盟的普攻那一下：从书里扑出去、身子伸长；淡色，只看**姿势**）。**总宽不超过 56 格**（比淡色模型短：**尾巴往上卷在背上，不要在后面拖很长**），最低点在地面线上。
  - **R**：照 `3_ult_ref.png`（英雄联盟的大招：书竖起来，她扒在书边；淡色，只看**姿势**，图右边被画布切掉了一点）。**约 48 格高、不超过 54 格宽**，书底在地面线上。
- **B：每格 44 px**（它在游戏里只有 21 格高，所以格子画大）：照 `2_target_B.png`：顶 **y = 264**、最低点（尾巴尖）**y = 1188**：**21 格高、约 24 格宽**。
- **C：每格 30 px**：照 `2_target_C.png`：书顶 **y = 420**、书底 **y = 1170**：**约 38 格宽、25 格高**。
- 每张都整个在画布里，触须、尾巴、书角不出画，四周留至少 1 格空。

## 要画清楚的地方

- **脸**（`4_head.png` 是第 0 步 A 读回的头部，8 倍）：淡紫蓝的头、**白色的脸和嘴边**；**两只大蓝眼睛：每只约 3 × 3 格（B 里约 2 × 2），一样高，各带 1 格白色高光，上面一道深色眼线**；粉色小鼻子；耳朵外面淡紫蓝、里面粉红；额头上的**金色叶子头饰**；头饰上伸出的**弯弯的金色触须和末端的蓝色小球**（2 档 + 1 格高光）。**每一张里都是同一个头**：脸朝右前方、**两只眼睛都看得见**（S、L、R 也一样，不要另画一个只有一只眼的侧脸）。
- **身体**：淡紫蓝的毛 3 档；胸前**深蓝色的蓬毛**；**金项圈和正中的蓝宝石**；**白色的前爪**；长尾巴，**几圈金环**，尾巴尖一簇**金色的毛**。
- **书**：**深红色的皮封面**（2–3 档）、**金色的边框和书角**（3 档 + 高光）、封面正中**金色的漩涡纹章**、**米黄色书页**（2 档，看得见几道页边线）。
- **A 的姿势**和第 0 步的 A 一样：3/4 正面朝右，书打开竖在她身前和身下，她坐在书里，两只前爪搭在书的上沿，尾巴从书后面在画面左边卷起，尾巴尖的金毛朝上。
- **S 的姿势**：**完全侧面、朝右**，她**坐在打开的书里**：书从侧面看是一个 V 字形（两边封面张开、书页在中间），她的身子从书里探出来，前爪搭在书的前沿（画面右边），头是和 A 一样朝右前方的脸；尾巴从书后面（画面左边）伸出来往上卷。所有动作都从这张画出来，所以**猫、书、尾巴都要清楚地分开**，每样外面都有自己的描边。
- **L 的姿势**：**侧面朝右，她从书里扑出去**：身子**往右伸得长长的**，两只前爪向右伸出，后腿往后蹬；书还**打开着挂在她的肚子和后腿下面**；尾巴往上卷在背上；头还是那个朝右前方的脸（两只眼睛都看得见）。
- **R 的姿势**：**书立起来**（书脊朝下站在地面线上，打开一点，封面朝右前方，看得见金框和漩涡纹章），**她扒在书的左边**：两只前爪搭在书的上沿，头从书沿上面探出来朝右前方看，身子和尾巴垂在书的左边，尾巴尖的金毛在下面。
- **B 的姿势**和第 0 步的 B 一样：书完全摊平、书页朝上，她趴在书页上，两只前爪伸出书的前沿，头抬起朝右前方（两只眼睛都看得见），尾巴从书的后沿垂下去。
- **C**：和第 0 步的 C 一样，只有合上的书，平放在地上，3/4 朝右，看得见封面的金框、漩涡纹章和一侧的书页边。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的佐伊、斯莫德、卡特琳娜，**和悠米同一个密度 PPU 1.5**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `yuumi_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节**全照它；A 的姿势 |
| `1_picture_B.png` | 你第 0 步画的 B（用户选定） | B 的样子和姿势 |
| `1_picture_C.png` | 你第 0 步画的 C（用户选定） | C 的样子 |
| `2_target_A.png` | A 缩到游戏格子数、每格 22 px 放在画布上（细节是坏的） | A 的**大小、位置、比例、姿势** |
| `3_layout_A.png` | A 加网格线：橙 = 小球顶，蓝 = 眼睛，红 = 地面 | 对齐网格、48 格的高度、地面线 |
| `2_target_B.png` | B 缩到 21 格、每格 44 px（细节是坏的） | B 的**大小、位置** |
| `2_target_C.png` | C 缩到 38 格宽、每格 30 px（细节是坏的） | C 的**大小、位置** |
| `3_side_ref.png` | 英雄联盟模型的侧面（淡色） | **S** 的轮廓、位置（头照 A 的大小） |
| `3_leap_ref.png` | 英雄联盟的普攻：从书里扑出去（淡色） | **L** 的姿势（尾巴卷起、总宽不超过 56 格） |
| `3_ult_ref.png` | 英雄联盟的大招：书立起来、她扒在书边（淡色） | **R** 的姿势 |
| `4_head.png` | 第 0 步 A 读回的头部（8 倍） | 耳朵、眼睛、头饰、触须和小球 |
| `style/5_style_zoe.png` … `7_style_katarina.png` | 本包的佐伊、斯莫德、卡特琳娜（同密度），8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、金饰怎么画 |

## 提示词（六种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A, 1B, 1C your own earlier pixel-art drawings of this character - a small magical chibi cat with lilac-blue fur, a white face, muzzle and front paws, two huge blue eyes, pink inner ears and a pink nose, a deep-blue fur ruff on the chest, a gold collar with a blue gem, a gold leaf circlet from which a curling gold antenna rises ending in a glowing blue orb, a long tail with gold rings ending in a gold tuft, and her flying book with dark-red leather covers, gold frame and corners, a gold spiral emblem and cream pages (1A sitting in the open book, 3/4 view facing right; 1B lying on the book laid flat; 1C the closed book) - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A image 1A cut down to the RIGHT square count - 48 squares from the top of the orb to the bottom of the book - shown with 22 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details; 3A the same with grid lines every 5 squares: orange = the top of the orb, blue = the eyes, red = the ground; 2B image 1B cut to 21 squares tall with 44 px squares; 2C image 1C cut to 38 squares wide with 30 px squares; 3-side, 3-leap, 3-ult: the game's 3D model at the scale of 2A (faded) - only their POSE, OUTLINE and PLACE (its head is smaller than ours: keep our head size); 4 the head of image 1A enlarged; 5-7 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - how a face, eyes and gold trim are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square the size given below, aligned on one straight grid from the canvas corner, the figure whole inside the canvas with at least one empty square on every side. Every detail drawn with whole squares of that size, never with smaller pixels.
With so few squares make every part READ: the lilac-blue fur in 3 shades with the white face, muzzle and paws; TWO BIG BLUE EYES at the SAME height, each with ONE white highlight square and a dark lash line above; a small pink nose; pink inner ears; the gold leaf circlet; the curling gold antenna with its blue orb; the deep-blue chest ruff; the gold collar with its blue gem; the tail's gold rings and gold tuft; the book's dark-red covers in 2-3 shades, the gold frame and corners in 3 shades with a highlight, the gold spiral emblem, the cream pages with a few page lines. The SAME head in every picture: the face turned to the front-right with BOTH eyes visible (never a one-eyed profile).
One continuous 1-square near-black outline round the figure; the cat, the book and the tail each with their own outline where they cross; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`yuumi-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A, squares of exactly 22 px: her idle exactly as images 1A, 2A and 3A - 3/4 view facing right, the book open and standing in front of and under her, she sits inside it with both front paws on its top edge, the tail coming out behind the book and curling up on the image left with its gold tuft upward; the top of the orb at y 132 and the bottom of the book on y 1188 - exactly 48 squares tall, about 48 squares wide.
  ```
- **S（`yuumi-model-S-1.png`、`-S-2.png`，两稿）**：
  ```text
  PICTURE S, squares of exactly 22 px: the SAME cat and book SIDE-ON, FACING RIGHT (pose and place of image 3-side): she sits inside the open book, the book seen from the side as a V (both covers spread, the pages in the middle), her body rising out of it with the front paws on its front edge (image right), the head the SAME head as in image 1A turned to the front-right with BOTH eyes visible, the tail coming out behind the book (image left) and curling up; the cat, the book and the tail clearly separated, each with its own outline; the top of the orb at y 132 and the bottom of the book on y 1188 - exactly 48 squares tall, at most 57 squares wide.
  ```
- **L（`yuumi-model-L-1.png`、`-L-2.png`，两稿）**：
  ```text
  PICTURE L, squares of exactly 22 px, the SAME size of cat and book as picture A: THE LEAP (pose of image 3-leap), side-on facing right - she springs out of the book, her body STRETCHED LONG to the right, both front paws reaching forward to the right, the hind legs pushing back, the open book still hanging under her belly and hind legs, the tail curled UP over her back (not trailing behind); the head the SAME head as in image 1A turned to the front-right with BOTH eyes visible; at most 56 squares wide, the lowest point on y 1188.
  ```
- **R（`yuumi-model-R-1.png`、`-R-2.png`，两稿）**：
  ```text
  PICTURE R, squares of exactly 22 px, the SAME size of cat and book as picture A: FINAL CHAPTER (pose of image 3-ult) - the book STANDING UPRIGHT on its spine on the ground line, opened a little, its cover turned to the front-right showing the gold frame and the gold spiral emblem; the cat CLINGS to the book's LEFT side: both front paws over its top edge, the head peeking over the edge looking to the front-right with BOTH eyes visible, the body and the tail hanging down the left side of the book, the gold tuft at the bottom; about 48 squares tall, at most 54 squares wide, the bottom of the book on y 1188.
  ```
- **B（`yuumi-model-B-1.png`、`-B-2.png`，两稿）**：
  ```text
  PICTURE B, squares of exactly 44 px (it is small in the game): ATTACHED, exactly as images 1B and 2B - the book opened fully and laid flat like a small cushion, the cream pages on top, she lies on the pages on her belly, both front paws stretched forward over the front edge, the head raised looking to the front-right with BOTH eyes visible (each about 2x2 squares with one white highlight), the tail hanging down over the back edge with its gold tuft at the bottom; the top at y 264 and the tail tuft on y 1188 - exactly 21 squares tall, about 24 squares wide.
  ```
- **C（`yuumi-model-C-1.png`，一稿）**：
  ```text
  PICTURE C, squares of exactly 30 px: THE CLOSED BOOK alone, exactly as images 1C and 2C - closed, lying flat on the ground, 3/4 view facing right: the dark-red cover with its gold frame, gold corners and gold spiral emblem on top, the cream page edges on one side; the top of the book at y 420 and its bottom on y 1170 - about 38 squares wide and 25 squares tall.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **格子大小对**：A、S、L、R 每格 22 px（A、S 正好 48 格高）；B 每格 44 px（21 格高）；C 每格 30 px（约 38 × 25 格）。**数一下台阶：如果比这多一倍以上，就是格子画小了，请重画。**
- 每张里都是同一个头：两只大蓝眼睛一样大、一样高、带高光，脸朝右前方、两只眼睛都看得见；金头饰、金触须和蓝色小球、金项圈和蓝宝石、尾巴的金环和金尾尖；书的深红封面、金框、漩涡纹章、米黄书页。
- S 侧面朝右、坐在 V 字形的书里；L 身子伸长往右扑、书挂在肚子下面、尾巴卷在背上、不超过 56 格宽；R 书立着、她扒在书的左边、头从书沿探出来；B 趴在摊平的书上；C 合上的书。外描边连续；没有任何特效。

## 交付（`outputs/yuumi-model/`）

- `yuumi-model-A-1.png`、`-A-2.png`、`-S-1.png`、`-S-2.png`、`-L-1.png`、`-L-2.png`、`-R-1.png`、`-R-2.png`、`-B-1.png`、`-B-2.png`、`-C-1.png`；原始生成图原样放 `outputs/yuumi-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/yuumi_model_done.zip`。中间不要停，11 张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（A、S、L、R 约 22 px、48 行；B 约 44 px、21 行；C 约 30 px），从 raw/ 按格读回（regrid），在游戏大小下和佐伊、米利欧、璐璐、提莫并排自查（PPU 1.5，32 游戏像素），把每种的两稿给用户挑。
- 动作帧自己摆（`rig_yuumi.py`，照 rig_rammus.py / rig_zoe.py：只整格平移、绕半格点的四分之一转、镜像），脸用 A 的同一张 3/4 脸。英雄联盟的动作（`tools/lol/anim_graph.py Yuumi`、`pose_ref.py` 要带 pack_yuumi_picture.LOOK 的参数）：待机 Idle01；跑 Run01（坐在书里飞，书一起一伏）；普攻 Attack01 / Crit01（扑出去 = L）；Q Spell1_detached；W Spell2_Attach_in（扑向队友 = L）、Spell2_Detach_out（跳下来）；E Spell3_detached；R Spell4_in / Spell4_loop01（= R）；死亡 Death01（钻进书里、书合上落地 = C，8 帧带回弹）；挨打第 1 帧闪白后退；附身 a_*（= B，画在队友头顶的高度）。自查到完美（8 倍逐帧：不挡脸、不错切、不留透光缝）再给用户审。
