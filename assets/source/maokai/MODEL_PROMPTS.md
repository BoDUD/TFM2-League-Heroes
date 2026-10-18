# 茂凯：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（茂凯待机）** 和 **C（树苗）**（`1_picked_A.png`、`1_picked_C.png`），定的大小（每个游戏像素 1.2 格）：
>   - **A：从树冠顶（嫩叶不算）到脚底 48 格**（游戏里 40 行），约 42 格宽。
>   - **C：树苗是他身高的 0.3 倍**：从叶尖到根尖 **14 格**（游戏里 12 行），约 10 格宽。格子大小和 A 一样。
> - 比例照原画（大体型的树精，脸在树干中间，不是大头），不用改。
> - 我把 A、C 按这个大小直接缩好了（`2_target_A.png`、`2_target_C.png`，每格 11 px），**大小、位置、姿势都对，但糊了**：脸上的蓝眼睛只剩一两个散格，木头眉骨和额头的尖糊在苔藓里，巨大手臂上的鬼脸成了一团蓝色杂点，树皮的纹路和苔藓的几档绿色混成一片，灯笼只剩一个蓝点，紫布看不出来，树苗的小脸没了。
> - **这一轮就是在同样的格子上把它们重画清楚**：同样大小、同样位置、同样姿势，**每块 11 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**A、C 各画两稿。**

## 大小和位置（照 `2_target_*.png` / `3_layout_*.png`）

- 画布 **1024 × 1024**，**每格 11 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A**：**树冠顶在 y = 462**（绿线），**两只树根脚的底在 y = 990**（红线）；人从 x ≈ 275 到 x ≈ 737，位置照 `2_target_A.png`。
- **C**：**叶尖在 y = 836**（绿线），**根尖在 y = 990**（红线）；树苗从 x ≈ 451 到 x ≈ 561，放在画布中间，位置照 `2_target_C.png`。

## 要画清楚的地方

- **脸**（`4_face.png` 是 A 的脸，第 0 步读回后 8 倍放大）：
  - 脸在树干中间：浅褐色的**木头额头和竖着的木头尖**，两侧的木头眉骨；**两只眼睛一样大、一样高、发亮蓝色**（每只至少 2 格：一格亮蓝、一格更亮的高光），眼睛下面是深色木头；下巴是一圈**苔藓绿的"胡子"**。脸不要放大，就照原画的大小（约占身高五分之一）。
- **巨大的近侧手臂**（`4_armface.png` 是拳头上的鬼脸，8 倍放大）：浅褐色木头，比身体亮，有 2–3 档和木纹；拳头上刻着鬼脸，**鬼脸的两只眼睛和咧开的嘴发亮蓝色**（整齐的亮蓝块，嘴是一条弯弯的亮蓝带），整条手臂从肩膀垂到差不多地面，形状完整清楚。
- **身体**：深褐偏紫的树皮（3–4 档，有树皮纹路），**一定要有偏暖的亮边**；背上的**苔藓树冠**青绿色 3 档；背后弯曲的树枝和挂着的**蓝色水晶灯笼**（至少 2×3 格的亮蓝，连着一根细绳）；顶上的嫩叶。
- **远侧的绿爪子**拿着小树苗（树苗要能认出来：浅褐色的小身体、一格蓝眼睛、顶上一片叶子）。
- **下身**：腰间一块**紫色的布**（2 档紫，能看清）；两条粗短的树根腿，树根脚落在同一条地面线上。
- **C 树苗**：浅褐、黄绿色的木头小身体，刻着小脸，**一只发亮蓝的眼睛**（2 格），顶上一片嫩叶，两侧两片叶子当手臂，底下尖尖的根。格子少，**宁可形状简单清楚，也不要细碎的杂格**。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包的塔姆、内瑟斯、厄加特，每游戏像素 1.2 格，和茂凯一样；斯维因 1.5 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（深褐偏紫的树皮、青绿苔藓、浅褐木头的巨臂、亮蓝的眼睛和鬼脸、蓝色灯笼、紫布、绿爪子）。树皮很暗，**一定要有亮边**，不然在游戏里会糊成一团。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（荆棘、冲击波、树根突刺、发光拖尾都不画）。

## 附图（压缩包 `maokai_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` / `1_picked_C.png` | 你第 0 步画的 A、C（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` / `2_target_C.png` | 按新大小缩到每格 11 px 放在画布上（糊的） | **大小、位置、姿势**照它，糊的地方重画 |
| `3_layout_A.png` / `3_layout_C.png` | 同一张加网格线：绿线 = 顶，红线 = 地面 | 对齐网格、顶和地面线的位置 |
| `4_face.png` | A 的脸（第 0 步读回后 8 倍放大） | 木头额头、眉骨、蓝眼睛、苔藓胡子 |
| `4_armface.png` | A 巨臂拳头上的鬼脸（8 倍放大） | 鬼脸的蓝眼睛和咧开的蓝嘴、木纹 |
| `style/5_style_tahmkench.png` … `8_style_swain.png` | 本包的塔姆、内瑟斯、厄加特（每游戏像素 1.2 格）、斯维因（1.5 格），8 倍放大 | **只看风格**：这个密度下一格有多大、暗色身体怎么留亮边、发光的部分怎么平涂 |

## 提示词 1：`maokai-model-A-1.png`、`maokai-model-A-2.png`（茂凯，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1C approved pixel-art pictures - 1A a huge hunched living tree: a body of dark brown, violet-tinged bark under a big teal-green moss crown on his back with young leaves on top; his face in the middle of the trunk (a pale wooden forehead with an upright wooden spike, wooden brows, two eyes glowing bright blue, a mossy green beard at the chin); a curved branch on his back with a blue crystal lantern hanging from it; a HUGE near arm (image left) of pale brown wood whose fist is carved into a grinning face with glowing blue eyes and a glowing blue grin, hanging almost to the ground; a smaller green wooden far claw holding a small sapling; a violet cloth at the waist; two short thick root legs - and 1C his sapling alone: a small standing wooden seedling with a carved face, one glowing blue eye, a leaf on top, two leaves as arms, a pointed root (the LOOK, the COLOURS and the DETAILS to keep); 2A and 2C the same two pictures shrunk to their final game size on a 1024x1024 canvas, 11 px squares - the SIZE, the PLACE and the POSE are right, but they are muddy (the blue eyes scattered into one or two loose squares, the wooden brow and forehead spike lost in the moss, the fist's carved face turned to blue noise, the bark grain and the moss greens mixed into one mass, the lantern a single blue dot, the violet cloth gone, the sapling's face gone); 3A and 3C the same with grid lines every 5 squares: the green line = the top, the red line = the ground; 4 his face enlarged and his fist's carved face enlarged; 5-8 STYLE ONLY: other characters from the same game, shown 8x so every square is one pixel (5, 6 and 7 at this same square density) - copy their pixel-art look, the lit edges on a dark body, how glowing parts are drawn as flat bright squares.
Draw with the image generator ONE clean pixel-art picture of the tree creature (picture A): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2A: every square 11 px, aligned on one straight grid starting at the canvas corner, the top of the moss crown at y 462, both root feet on the ground line y 990, about 48 squares from the crown to the feet, the figure from about x 275 to about x 737 - hunched, the huge near arm hanging in front (image left), the far claw raised before his chest holding the small sapling, the face to the front-right - as if a pixel artist redrew image 1A square by square on image 2A's grid.
Make it CRISP and READABLE at this size: the face in the trunk exactly as big as in 1A (never enlarged): the pale wooden forehead and its upright spike, the wooden brows, TWO EYES of the SAME size at the SAME height glowing bright blue (each at least 2 squares: a bright blue square and a brighter highlight), dark wood under them, the mossy green beard; the HUGE near arm in pale brown wood (lighter than the body, 2-3 shades with wood grain), its fist's carved face with two glowing blue eyes and a curved glowing blue grin as neat bright blocks, the arm whole from the shoulder almost to the ground; the dark brown violet-tinged bark in 3-4 shades with bark grain and WARM LIT EDGES; the teal-green moss crown in 3 shades; the curved branch with the blue crystal lantern (at least 2x3 bright blue squares on a thin cord) and the young leaves; the green far claw with a recognisable small sapling (pale brown body, one blue eye square, a leaf on top); the violet cloth at the waist in 2 shades; two short thick root legs, the root feet on one ground line.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`maokai-model-C-1.png`、`maokai-model-C-2.png`（树苗，两稿）

附同样的图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of the SAPLING alone (picture C): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size and place of image 2C: every square 11 px (the SAME square size as picture A), aligned on one straight grid starting at the canvas corner, the leaf tip at y 836, the root tip on the ground line y 990, about 14 squares from the leaf tip to the root tip and about 10 squares wide, from about x 451 to about x 561, standing upright facing right - as if a pixel artist redrew image 1C square by square on image 2C's grid.
With so few squares keep the shapes SIMPLE and CLEAR: a small pale brown and yellow-green wooden body with a carved face, ONE eye glowing bright blue (2 squares), a young leaf on top, two leaves as arms at the sides, a pointed root at the bottom; one continuous near-black outline; 2-3 flat shades per material; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` / `2_target_C.png` 一样：每格 11 px、对齐网格；A 顶 y 462、C 叶尖 y 836，底都在 y 990。
- A：脸在树干中间、没有放大，两只蓝眼睛一样大、一样高；巨臂拳头上的鬼脸眼睛和嘴是整齐的亮蓝块；树皮有亮边；苔藓几档绿分得开；灯笼看得见；紫布看得见；绿爪子里的小树苗认得出；外描边连续；没有任何特效。
- C：和 A 同样的格子大小，14 格高；一只蓝眼睛、顶上一片叶子、两片叶子手臂、尖根，形状简单清楚。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/maokai-model/`）

- `maokai-model-A-1.png`、`maokai-model-A-2.png`、`maokai-model-C-1.png`、`maokai-model-C-2.png`；**image_gen 的原始生成图原样放 `outputs/maokai-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/maokai_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 48 / 14 行（不经过脸和鬼脸），和 `2_target_*.png` 并排、按游戏大小和塔姆、布隆、内瑟斯、墨菲特放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，塔姆 / 内瑟斯的方式；巨臂只整块平移或直角转）：待机（呼吸）、走路（造型自己的整条树根腿，不用 Codex 画的腿）、普攻 maokai_attack1 / attack2（巨臂横扫）、Q Maokai_spell1（拳头砸地）、W maokai_spell2_up / spell2_down（钻进地里、在目标处冒出）、E maokai_spell3（扔树苗）、R maokai_spell4（两臂高举再砸下）、受击、死亡。树苗的落地、等待、扑人、爆炸放第 3 步特效。
