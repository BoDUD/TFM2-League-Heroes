# 普朗克：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（手炮扛在肩上、弯刀朝前下）**（`1_picked_A.png`），定的大小（每个游戏像素 1.2 格）：**从帽子顶到鞋底 50 格**（游戏里 42 行）。头的比例保持原画那样（帽子顶到胡子扎的红布约占身高的 30%）。
> - 我把 A 按这个大小直接缩好了（`2_target_A.png`，每格 14 px），**大小、位置、比例、姿势都对，但糊了**：脸和眼睛几乎看不出来、胡子和脸混成一片，帽子的月牙形状边缘不清，手炮的金色和手套、护腕糊在一起，青绿护肩只剩几个杂格，赤膊的胸口和肚子上的纹身成了乱点，深紫外套下摆和深灰绿裤子分不开，弯刀的刀身断断续续。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 14 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**画两稿。**

## 大小和位置（照 `2_target_A.png` / `3_layout_A.png`）

- 画布 **1024 × 1024**，**每格 14 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **帽子顶在 y = 260**（绿线），**胡子扎红布的地方在 y = 470 左右**（蓝线），**两只鞋底在 y = 960**（红线）。
- 人连弯刀和外套下摆大约 52 格宽、50 格高，位置照 `2_target_A.png`：左边是外套下摆（约 x = 140 起），扛在近侧肩上的金色手炮约在 x = 265–350、y = 370–480，右边的弯刀刀尖约到 x = 870、y = 750–840，全都在画布里。

## 要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍放大）：
  - **黑色月牙海盗帽**：帽檐两边高高翘起像一弯月牙，黑灰 2–3 档、**上沿一条偏亮的灰边**（不要一团死黑）。
  - **两只眼睛一样大、一样高**：各 1–2 格深色（近黑）的眼睛，上面一条浓眉往下压（皱眉），**不要红色的眼睛**；鼻子 1–2 格肉色高光。游戏里眼睛必须能看到。
  - **八字胡和长胡子**：花白偏棕，2–3 档（亮灰、中灰棕、暗棕），胡子尖下面一格**红布**扎一束；胡子和肉色的脸分得开。
- **身体**：赤膊的胸口和圆肚子（肉色 3 档，几格深色纹身线，不要乱点）；**青绿色高领护肩**（青绿 2–3 档，一格亮边）；交叉的深色皮带；**红布缠小臂**；**红腰带**（红 3 档）+ **棕皮带和金扣**（金扣约 3×3 格）；背后**深紫长外套的下摆**（紫 2–3 档、**金色描边**，下摆破成几条）；**深灰绿裤子**（有一格亮边）；**棕色翻口长靴**（翻口金边）。
- **武器**：
  - **金色燧发手炮**扛在近侧肩上（金 3 档 + 亮高光，炮口一圈深色），近侧手握着它，**手在脸的旁边，不挡脸**。
  - **深色锯齿弯刀**握在远侧手，朝前下方伸出：刀身深灰 2 档、刀背几格锯齿、**刀尖 4–6 格橙红发亮**（橙、黄、红 3 档）。刀身连续，不要断。
- **姿势**：站得很稳、两脚分开，照 `1_picked_A.png`。3/4 正面朝右：近侧的手臂和腿在画面左边、颜色亮，远侧的在画面右边、稍暗。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。**黑帽子、深紫外套、深灰绿裤子一定要有偏亮的边**，不然在游戏里会糊成一团。

## 干净

- 和附图 5–8（本包的内瑟斯、塔姆，每游戏像素 1.2 格，和普朗克一样；斯维因 1.5 格；厄运小姐原尺寸；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（黑月牙帽、花白棕胡子、肉色皮肤、青绿护肩、红布红腰带、金手炮金扣、深紫外套金边、深灰绿裤子、棕靴子、深色弯刀橙红刀尖）。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（枪口火光、火药桶、发光都不画）。

## 附图（压缩包 `gangplank_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` | 按新大小缩到每格 14 px 放在画布上（糊的） | **大小、位置、比例、姿势**照它，糊的地方重画 |
| `3_layout_A.png` | 同一张加网格线：绿线 = 帽子顶，蓝线 = 胡子扎红布处，红线 = 地面 | 对齐网格、头的大小、地面线的位置 |
| `4_head.png` | A 的头（第 0 步读回后 8 倍放大） | 帽子、脸、眼睛、胡子、扛在肩上的手炮 |
| `style/5_style_nasus.png` … `8_style_missfortune.png` | 本包的内瑟斯、塔姆（每游戏像素 1.2 格）、斯维因（1.5 格）、厄运小姐（原尺寸），8 倍放大 | **只看风格**：这个密度下一格有多大、脸和眼睛怎么画、深色衣服的亮边、海盗帽 |

## 提示词：`gangplank-model-A-1.png`、`gangplank-model-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art picture of this character - a burly middle-aged pirate captain: a big black pirate hat whose brim turns up on both sides like a CRESCENT, a frowning face with heavy brows, a thick moustache and a long greyish-brown beard tied under the chin with a red cloth; a bare chest and round belly with dark tattoo lines under a high teal-green shoulder collar and crossed dark straps; red cloth on the forearms; a red sash with a brown belt and a gold buckle; a long dark-purple coat hanging behind him in torn tails with gold trim; dark grey-green trousers; brown cuffed boots with gold-trimmed cuffs; a steady wide stance, the NEAR hand resting a GOLDEN FLINTLOCK HAND CANNON on his near shoulder (the hand beside the face, never over it), the FAR hand holding a DARK SERRATED CUTLASS down and forward, its tip glowing orange-red (the LOOK, the COLOURS and the DETAILS to keep); 2 the same picture shrunk to its final game size on a 1024x1024 canvas, 14 px squares - the SIZE, the PLACE, the PROPORTIONS and the POSE are right, but it is muddy (the face and the eyes almost gone, the beard and the face one mass, the crescent hat's edge unclear, the gold cannon smeared into the glove, the teal collar a few odd squares, the tattoos noise, the purple coat and the trousers smeared together, the blade broken); 3 the same with grid lines every 5 squares: the green line = the top of his hat, the blue line = the red tie of his beard, the red line = the ground; 4 his head enlarged; 5-8 STYLE ONLY: other characters from the same game, shown 8x so every square is one pixel (5 and 6 at this same square density, 7 a little denser, 8 another pirate) - copy their pixel-art look, how a face, eyes, a beard and dark clothes with light edges are drawn at this size.
Draw with the image generator ONE clean pixel-art picture of the character: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place, proportions and pose of image 2: every square 14 px, aligned on one straight grid starting at the canvas corner, the top of his hat at y 260, the beard's red tie at about y 470, both soles on the ground line y 960, 50 squares from the hat's top to the soles, about 52 squares wide with the coat tails and the cutlass - a steady wide stance, the hand cannon on the near shoulder, the cutlass down and forward, the face to the front-right, 3/4 view facing right - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the black crescent hat in 2-3 dark shades with a LIGHT GREY TOP EDGE (never one dead-black blob); TWO EYES of the SAME size at the SAME height (1-2 near-black squares each, NOT red) under heavy frowning brows, a 1-2 square nose highlight - they must read at a glance; the moustache and the long beard greyish-brown in 2-3 shades, one red square of cloth at the tie, clearly apart from the skin; the bare chest and belly in 3 skin shades with a few clean dark tattoo lines (no noise); the teal-green collar in 2-3 shades with a light edge; the crossed dark straps; red cloth on the forearms; the red sash in 3 reds, the brown belt and a 3x3 gold buckle; the dark-purple coat tails in 2-3 purples with GOLD TRIM, torn into a few strips; the dark grey-green trousers with a light edge; the brown cuffed boots with gold cuffs; the GOLDEN HAND CANNON on the near shoulder in 3 golds with a bright highlight and a dark muzzle ring, the near hand holding it BESIDE the face; the dark serrated cutlass in 2 greys, a few saw teeth on its back, ONE CONTINUOUS blade, its tip 4-6 squares glowing orange, yellow and red.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); the black hat, the purple coat and the dark trousers with LIGHTER EDGES so they never turn into one dark mass; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no barrel, no glow), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` 一样：每格 14 px、对齐网格；帽子顶 y 260、胡子红布约 y 470、鞋底 y 960；连弯刀和外套下摆约 52 格宽。
- 两只眼睛一样大一样高、深色（不是红色）、能看到；胡子和脸分得开；月牙帽有亮边；金手炮清楚、手不挡脸；弯刀连续、刀尖橙红；深紫外套金边、裤子有亮边；外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/gangplank-model/`）

- `gangplank-model-A-1.png`、`gangplank-model-A-2.png`；**image_gen 的原始生成图原样放 `outputs/gangplank-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/gangplank_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），Codex 常画得比要求大（吉格斯要 48 行画了 62）：用 design_ziggs_cut 的 even_cut 删整行整列到 50 行，**脸、眼睛的行列保护**，手炮和弯刀单独裁再贴回（否则删的行全挤到腿上）；和 `2_target_A.png` 并排、按游戏大小和内瑟斯、塔姆、斯维因、德莱厄斯、奥拉夫放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，吉格斯 / 嘉文的方式：手和武器只整块平移，不按肩转、不相对身体上下挪；**手炮、弯刀是刚体**；腿用设计自己的整条腿；走路落脚下沉 + 两腿交错时整个人弹起一格）：待机（呼吸）、走路、普攻 Gangplank_Attack1（弯刀砍）、Q skill（Gangplank_spell1 手炮开枪）、E skill2（Gangplank_spell3 放桶）、W skill_w（Gangplank_Spell2 吃橘子）、R ult（Gangplank_spell4 举手发信号）、受击、死亡 Gangplank_Death。
