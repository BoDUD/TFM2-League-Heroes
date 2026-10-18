# 影哨 阿克尚：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（阿克尚待机：站直、近侧手把枪举在头边枪口朝上、远侧手叉腰、披风垂在身后）**（`1_picked_A.png`），定的大小（每个游戏像素 1.5 格）：
>   - **从头顶头发到鞋底 57 格**（游戏里 38 行）；举起的枪高出头顶，**连枪整个人约 70 格高、约 44 格宽**。
> - 比例照原画（Q 版，头连头发约占身高三分之一），不用改。
> - 我把 A 按这个大小直接缩好了（`2_target_A.png`，每格 15 px，放在 1254 × 1254 的画布上），**大小、位置、姿势都对，但糊了**：**眼睛几乎没了**（只剩一两个深色格），脸和胡子、头发混成一片，小发髻看不出来；浅蓝白围巾成了几个散格；橙红饰带和金箍、暗红披风混在一起；青绿布片和金环断断续续；黑裤子和黑靴糊成一块；**回旋镖枪的两道弯钩成了一团暗红和杂色**。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 15 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**画两稿。**

## 大小和位置（照 `2_target_A.png` / `3_layout_A.png`）

- 画布 **1254 × 1254**（就是你平时出图的大小），**每格 15 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **头顶头发在 y = 345**（绿线），**两只鞋底在 y = 1200**（红线），中间正好 57 格；**枪的最上端在 y ≈ 150**；人从 **x ≈ 285**（举枪的近侧手和枪）到 **x ≈ 945**（披风右下角），位置照 `2_target_A.png`。**照这个大小画，不要缩小。**

## 要画清楚的地方

- **脸**（`4_face.png` 是 A 的头，第 0 步读回后 8 倍放大）：
  - 深棕色的**长卷发**，3 档颜色，能看出一绺一绺；头顶的**小发髻**看得出（一个圆圆的小团）；
  - 棕色的脸清楚，和头发、胡子分得开；
  - **两只眼睛一样大、一样高、都看得见**：**每只至少 2×2 格**（一格眼白 + 深色瞳孔），这是这一轮最重要的一点；浓眉（深色一横）；
  - **短络腮胡**比头发稍浅一点，沿下巴一圈；嘴角带点笑。脸不要放大，就照原画的大小。
- **上身**：脖子和肩上的**浅蓝白围巾**（2–3 档，亮）；两肩的**灰色护肩**（金边、一个金色尖角）；赤膊的**棕色胸口和手臂**（有亮边，看得出胸肌）；**橙红饰带**从近侧肩斜挎到远侧腰，中间的**金色宽箍**清楚。
- **手**：两只前臂的**金色护腕**；**浅蓝色无指手套**；举枪的近侧手握着握把；远侧手叉在腰上（手肘向外）。
- **下身**：**青绿腰带**和前面垂下的**青绿长布片**（中间一个**金环**、下端金色花纹）；**深灰黑裤子**（3 档，**一定要有偏亮的边**）；**黑色高筒靴**（有亮边和金色饰纹）。
- **披风**：**暗红色长披风**垂在身后两边（3 档，**有偏亮的边**），下摆金色卷边，内侧一点浅蓝。
- **枪**：**暗红色带青铜色**的大枪，前端**两道回旋镖一样的弯钩**朝上张开，**形状完整、轮廓清楚**（每道弯钩至少 3 格粗，有亮边和橙色高光），握把青白；枪身直、不歪。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–7（本包的普朗克、赵信、悟空，**每游戏像素 1.5 格，和阿克尚一样**，8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（棕色皮肤、深棕头发、浅蓝白围巾、灰护肩、金色、橙红饰带、暗红披风、青绿布片、深灰黑裤子、黑靴、暗红青铜的枪）。披风、裤子和靴子很暗，**一定要有亮边**，不然在游戏里会糊成一团。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（枪口火光、子弹、回旋镖飞行、钩索、伪装都不画）。

## 附图（压缩包 `akshan_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` | 按新大小缩到每格 15 px 放在画布上（糊的） | **大小、位置、姿势**照它，糊的地方重画 |
| `3_layout_A.png` | 同一张加网格线：绿线 = 头顶头发，红线 = 地面 | 对齐网格、头顶和地面线的位置 |
| `4_face.png` | A 的头（第 0 步读回后 8 倍放大） | 卷发和发髻、脸、眼睛、胡子、围巾 |
| `style/5_style_gangplank.png` … `7_style_wukong.png` | 本包的普朗克、赵信、悟空（每游戏像素 1.5 格），8 倍放大 | **只看风格**：这个密度下一格有多大、手枪和胡子怎么画、暗色衣服怎么留亮边 |

## 提示词：`akshan-model-A-1.png`、`akshan-model-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art picture of a ROGUE GUNSLINGER - brown skin, long wavy dark-brown hair with a small topknot, a short beard, a confident half smile; a pale blue-white scarf round the neck and shoulders, grey gold-trimmed shoulder pads; a bare muscular chest; a wide orange-red sash slung from the near shoulder to the far hip with a wide gold band; a long dark-red cape behind him with gold curled hems and a little pale blue inside; a teal belt with a long teal front cloth (a gold ring, a gold pattern at its end); dark grey-black trousers, tall black boots with gold trim; gold bracers and pale blue fingerless gloves; a big dark-crimson-and-bronze relic pistol whose front is two curved boomerang-like hooks, a pale teal-white grip; standing upright, the near hand raising the gun beside his head pointing UP, the far hand on his hip (the LOOK, the COLOURS and the DETAILS to keep); 2 the same picture shrunk to its final game size on a 1254x1254 canvas, 15 px squares - the SIZE, the PLACE and the POSE are right, but it is muddy (the eyes almost gone, the face, beard and hair mixed, the topknot lost, the scarf a few scattered squares, the sash, its gold band and the cape mixed, the teal cloth and its ring broken, the black trousers and boots one block, the gun's two hooks a dark-red smudge); 3 the same with grid lines every 5 squares: the green line = the top of his hair, the red line = the ground; 4 his head enlarged; 5-7 STYLE ONLY: other characters from the same game at this SAME square density, shown 8x so every square is one pixel - copy their pixel-art look, a pistol and a beard on the grid, lit edges on dark cloth.
Draw with the image generator ONE clean pixel-art picture of the gunslinger: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 15 px, aligned on one straight grid starting at the canvas corner, the top of his hair at y 345, both soles on the ground line y 1200 (57 squares from the hair to the soles), the top of the raised gun at about y 150, the figure from about x 285 (the raised near hand and the gun) to about x 945 (the cape's lower right corner) - keep it that big - standing upright, the near hand raising the gun beside his head pointing up (image left), the far hand on his hip (image right), the cape hanging behind him, the face to the front-right - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the long wavy dark-brown hair in 3 shades with clear locks and the small round topknot readable; the brown face clear and apart from the hair and the beard; TWO EYES of the SAME size at the SAME height, both visible, EACH AT LEAST 2x2 SQUARES (one white square and a dark pupil) - the most important point; thick dark brows; the short beard a shade lighter than the hair along the jaw; a half smile; the face exactly as big as in image 1 (never enlarged); the pale blue-white scarf in 2-3 bright shades; the grey shoulder pads with gold trim and a gold point; the brown chest and arms with LIGHTER EDGES; the orange-red sash with its CLEAR GOLD BAND; gold bracers and pale blue fingerless gloves; the teal belt and the long teal front cloth with its gold ring and gold end pattern; the dark grey-black trousers in 3 shades with LIGHTER EDGES; tall black boots with lit edges and gold trim; the dark-red cape in 3 shades with LIGHTER EDGES, gold curled hems, a little pale blue inside; the gun WHOLE and CLEAR: dark crimson with bronze, its two boomerang-like hooks spread at the top, each hook at least 3 squares thick with a lit edge and orange highlights, the pale teal-white grip in his near hand.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` 一样：每格 15 px、对齐网格；头顶 y 345、鞋底 y 1200（57 格），枪上端约 y 150。
- **两只眼睛一样大、一样高、每只至少 2×2 格**；脸、头发、胡子分得开；小发髻看得出。
- 围巾亮、护肩金边、饰带的金箍清楚；青绿布片和金环；裤子、靴子、披风都有亮边。
- 枪完整：两道弯钩每道至少 3 格粗、有亮边，握把青白。
- 外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/akshan-model/`）

- `akshan-model-A-1.png`、`akshan-model-A-2.png`；**image_gen 的原始生成图原样放 `outputs/akshan-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/akshan_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 57 行（头顶到鞋底，不经过脸和眼睛；删完检查手腕、枪管、弯钩这些细的连接处——茂凯的教训），和 `2_target_A.png` 并排、按游戏大小和卢锡安、普朗克、赵信、悟空放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，茂凯 / 悟空的方式：只平移、整块直角转、整行移，不变形、不缺像素；**枪是刚体**，每帧用设计里同一把，只做直角转；腿先做材质图再切）：待机（呼吸）、走路（造型自己的整条腿）、普攻双发 Attack1 / Attack2（枪平端朝右）、Q 去而复还 Spell1（扔回旋镖）、E 骄行荡寇 Akshan_Spell3 / Swing_shooting / Roll（甩钩、荡、翻滚）、R 恩怨相抵 Channel / Spell4（蓄力瞄准、连射）、受击、死亡。回旋镖、钩索、子弹、伪装放第 3 步特效。
