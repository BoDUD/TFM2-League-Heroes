# 虚空女皇 卑尔维斯：第 0 步，先画像素风原图（给 Codex 的提示词）

> 卑尔维斯是英雄联盟里的**虚空女皇**：上半身是一个瘦削的紫皮肤女人，两条手臂长成**巨大的蝙蝠翼一样的膜翼**（她就用翼刃砍人），下半身是一条长斗篷似的暗色躯体，底下几根**粉紫色的长爪**着地，后面拖一条**长尾巴**。这一步把她画出来，用户从里面挑：
> - **卑尔维斯**：**小小的深紫色脸**，**一双发光的品红色眼睛**；头顶一道**品红色的冠**（像一缕往后扫的头发 / 角，冠上一个小黄点）；**两肩各竖一根又高又尖的深紫色长刺**，刺尖比头顶还高；胸口是**深紫黑色的甲壳**，领口一圈**灰青 / 象牙色的尖刺花饰**（像扇子张开），两肩各一颗**发光的品红色圆珠**；**两条手臂是巨大的膜翼**：翼膜**深灰青到黑**，翼尖和翼边是**品红色**，翼骨像蝙蝠翼；腰下是**深紫黑色的长斗篷形躯体**，下摆裂成几片尖角；**三四根粉紫色的弯爪**像腿一样撑在地上（最亮的一档接近粉白）；**一条长尾巴**拖在地上，尾巴下面一面是品红色。
>
> 请 Codex 画**两张全身像**（**格子大小一样**，都是 **3/4 正面朝右**），用户从里面挑：
> - **A：收翼待机**——英雄联盟里放松的待机：两只膜翼**收拢垂下，像斗篷一样裹住身体**（附图 6、9a）。
> - **B：张翼待机**——英雄联盟里战斗的待机：两只膜翼**抬起、半张开**，像蝙蝠翼（附图 1、2、9b）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的卡莎、卡萨丁、雷克塞、维克兹（都是虚空英雄），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–8；附图 5 官方原画看气质和颜色——**紫色的脸和发光的眼睛、肩上的长刺、巨大的膜翼、粉紫的爪子最重要**）。
> - **比例**：Q 版。**头比原版大很多**（原版的头很小，Q 版要让脸清楚：头约占肩刺尖到爪尖的六分之一），脸朝右前方；身子瘦；肩刺高高竖起；**膜翼又大又显眼**；爪子分开稳稳着地；尾巴绕在靠近我们这一侧（画面左边）的地上。**膜翼和肩刺都不能挡住脸。**
> - **卑尔维斯的脸**（附图 3 特写）：深紫色皮肤（3 档），**两只眼睛一样高、都看得见**（每只至少 2×2 格），**发光的品红 / 粉白色**，没有瞳孔；脸尖、下巴尖，表情冷傲；头顶的品红色冠往后扫。
> - **颜色**：皮肤 深紫 3 档；冠 品红 3 档（加一个小黄点）；眼睛 品红 + 粉白高光；甲壳和斗篷躯体 深紫黑 3–4 档；领口尖刺花饰 灰青 / 象牙 3 档；肩上圆珠 品红 2 档 + 一格高光；膜翼 深灰青 3 档 + 翼边品红 2 档；肩刺 深紫 3 档；爪子 粉紫 3 档（最亮接近粉白）；尾巴 深紫黑 + 下面品红。**发光只用平涂的亮色块表现，不要柔光、不要半透明像素。**
> - **画布用正方形 1536×1536**。**A：从肩刺尖到最低的爪尖约 638 px，也就是约 58 格**；宽约 45 格。**B：同样的格子大小**，肩刺 / 翼尖到爪尖约 60 格，两翼张开宽约 85 格（可以收窄一点，但不能超过 90 格）。爪尖在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站在画布中间（附图 9a、9b 的位置）。翼尖、肩刺、尾巴、爪子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（突进的紫色残影、尾巴砸地、真身变身、珊瑚、虚空鱼都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/belveth-picture/belveth-A.png`、`belveth-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/belveth-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/belveth_picture_done.zip`。

## 附图（在压缩包 `belveth_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_belveth_idle.png` | 英雄联盟原版卑尔维斯的战斗待机，3/4 朝右 | 颜色、形状、**角度**、B 的姿势（张翼） |
| `refs/2_belveth_frontal.png` | 同一帧，正面 | 膜翼的形状、胸甲、领口花饰、爪子 |
| `refs/3_belveth_head.png` | 头部特写（3/4） | 紫色的脸、品红的冠、肩刺、肩上的圆珠 |
| `refs/4_belveth_back.png` | 同一帧的背后 | 膜翼背面、尾巴 |
| `refs/5_belveth_splash.png` | 官方加载画面 | 气质、**脸和发光的眼睛**、甲壳的尖刺、颜色 |
| `refs/6_belveth_relaxed.png` | 放松的待机，3/4 朝右 | **A 的姿势**：膜翼收拢像斗篷，尾巴绕在地上 |
| `refs/7_belveth_run.png` | 移动的一帧（3/4） | 她怎么滑行（这一步不画，后面用） |
| `refs/8_belveth_tail.png` | W 甩尾砸地的一帧 | 尾巴甩起来的样子（这一步不画，后面用） |
| `refs/9a_layout_belveth.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 在画布上的位置、大小、地面线（灰）；浅灰线 = 肩刺尖 |
| `refs/9b_layout_belveth_combat.png` | B 的布局示意 | 同上，张翼；和 A 同一个比例 |
| `style/10_style_kaisa.png` | 本包的卡莎，8 倍放大，一格 = 一个像素 | **只看风格**：虚空紫、品红发光、Q 版女性的脸 |
| `style/11_style_kassadin.png` | 本包的卡萨丁（8 倍） | **只看风格**：深紫的长斗篷、尖刺肩甲 |
| `style/12_style_reksai.png` | 本包的雷克塞（8 倍） | **只看风格**：虚空生物的甲壳、品红 |
| `style/13_style_velkoz.png` | 本包的维克兹（8 倍） | **只看风格**：深青的触手、品红的发光 |

## 提示词：`belveth-A.png` / `belveth-B.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-8 are 3D renders and art of a character from a game. THE VOID EMPRESS (images 1-8): a slim woman's upper body with DARK VIOLET SKIN, a small sharp face with GLOWING MAGENTA EYES (no pupils), a MAGENTA CREST sweeping back over her head like a swept-back horn of hair with a tiny yellow spot on it; TWO TALL SHARP DARK-PURPLE SPIKES rising from her shoulders, their tips higher than her head; a DARK PLUM-BLACK carapace chest with a fan of PALE TEAL-IVORY SPIKES at the collar and a GLOWING MAGENTA ORB on each shoulder; her two ARMS are HUGE BAT-LIKE WING MEMBRANES (dark slate-teal to black, MAGENTA tips and edges, bat-wing bones) that she slashes with; below the waist a long DARK CAPE-LIKE BODY whose hem splits into a few sharp points; three or four long curved PINK-MAGENTA CLAWS standing on the ground like legs (the lightest shade almost pink-white); a LONG TAIL lying on the ground, magenta on its underside. (1 her combat idle, 3/4 view facing right - the look, the ANGLE and the pose of B with the wings raised; 2 the same from the front: the wing shapes, the chest, the collar fan, the claws; 3 her head close-up: the violet face, the magenta crest, the shoulder spikes, the shoulder orbs; 4 the same from behind: the backs of the wings, the tail; 5 the official illustration: her mood, the FACE AND GLOWING EYES, the spiky carapace, the colours; 6 her relaxed idle, 3/4 view facing right - the pose of A with the wings folded down like a cloak and the tail curled on the ground; 7 a moving frame and 8 the tail swung in a slam - both for later.) Images 9a-9b are layout guides: where the character goes on the canvas and how big, the grey line is the ground, the light line the top of the figure. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a chibi woman's face with void purple and glowing magenta (10), a long dark purple cloak with spiked pauldrons (11), a void creature's carapace (12), dark teal tentacles with magenta glow (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the wing tips, the shoulder spikes, the tail, the claws); the claw tips on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows the character (the centre). In picture A THE VOID EMPRESS is about 638 px (about 58 squares) from her shoulder-spike tips to her lowest claw tip and about 45 squares wide; in picture B, at the same square size, about 60 squares from the highest wing or spike tip to the claw tips and about 85 squares wide with the wings half spread (narrower is fine, never more than 90).
PROPORTIONS: chibi. The HEAD MUCH BIGGER than in the renders (her head is tiny there; here about a sixth of spike-tips-to-claws) so the face reads clearly, turned to the front-right; a slim body; the shoulder spikes standing tall; the WING-ARMS big and clear; the claws apart and planted; the tail curled on the ground on her near side (the image left). The wings and spikes NEVER cover the face.
THE FACE: dark violet skin in 3 shades, both eyes at the SAME height and both visible (each at least 2x2 squares), GLOWING MAGENTA with a pink-white highlight, no pupils; a sharp face and pointed chin, a cold proud look; the magenta crest sweeping back over the head.
THE COLOURS: the skin dark violet in 3 shades; the crest magenta in 3 with one small yellow spot; the eyes magenta with a pink-white highlight; the carapace and the cape-like body dark plum-black in 3-4; the collar fan pale teal-ivory in 3; the shoulder orbs magenta in 2 with one highlight square; the wing membranes dark slate-teal in 3 with magenta edges and tips in 2; the shoulder spikes dark purple in 3; the claws pink-magenta in 3 (the lightest almost pink-white); the tail dark plum-black with a magenta underside. Show every glow only with flat bright blocks - every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the violet face, the magenta crest, the dark carapace, the teal wings, the ivory collar and the pink claws clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no dash trail, no slam, no void coral, no transformation, no little void fish); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (belveth-A.png): THE VOID EMPRESS's relaxed idle in 3/4 view facing right (images 6 and 9a) - standing tall and calm, the face to the front-right; both WING-ARMS FOLDED DOWN around her body like a long cloak, the near wing on the image left in full tone, the far wing on the image right a step darker; the shoulder spikes up; the tail curled on the ground on the image left; the claws planted; nothing covering the face.
PICTURE B (belveth-B.png): the SAME empress as A in her combat idle, 3/4 view facing right (images 1, 2 and 9b) - both WING-ARMS RAISED AND HALF SPREAD like bat wings, the near wing to the image left, the far wing raised high to the image right a step darker; the body leaning forward a little, ready to strike; the claws on the ground line; nothing covering the face.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，翼尖、肩刺、尾巴、爪子完整，不出画。
- 卑尔维斯：Q 版，**头比原版大很多**、脸清楚；**深紫色的脸**，**两只眼睛一样高、发光的品红色**；头顶品红的冠；肩上两根高高的长刺**不挡脸**；深紫黑甲壳 + 灰青象牙色领口花饰 + 肩上品红圆珠；**两只巨大的膜翼**（深灰青 + 品红翼边）；斗篷形的下身；粉紫爪子着地；长尾巴。
- A 是收翼（像斗篷），B 是张翼；都是 3/4 正面朝右；A 从肩刺尖到爪尖约 638 px（约 58 格），B 同样的格子大小；爪尖在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/belveth-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/belveth_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：卑尔维斯的头（一张脸用在所有帧）、两只膜翼（普攻是左右交替用翼刃砍）、尾巴（W 甩尾砸地）、爪子（她是贴地滑行的，不是迈步跑）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 移动 / 普攻 / 死亡 | Idle1_Combat 或 Idle1_Relaxed_base / RunClosed / Attack_Slow1a、Attack_Slow2a / — | 普攻是两只翼刃交替劈砍；移动是贴地滑行 |
| **虚空激流**（Q） | Q_spell1 | 朝目标方向突进，身后留一道紫色残影 |
| **上觐沉渊**（W） | Spell2_0 | 尾巴甩起来砸地，把敌人击飞 |
| **万载豪筵**（R） | Spell4 → Idle_Ult | 吃掉珊瑚，变成真身（更大、更多爪子），后面另外画 |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/belveth/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的打野英雄（卡兹克、雷克塞、希瓦娜、扎克、奈德丽）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小、收翼还是张翼。
- 定下后第 1 步按游戏格子重画（`pack_singed_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Belveth`（idle1_combat、idle1_relaxed_base、runclosed、attack_slow1a/2a、q_spell1、spell2_0、spell4、idle_ult）；不需要 `--hide-submeshes`。加载画面：`assets/characters/belveth/skins/base/belvethloadscreen_0.tex`（不带 `_0` 的那个不在包里）。
