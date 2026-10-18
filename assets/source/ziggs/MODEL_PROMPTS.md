# 吉格斯：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（两手张开托炸弹）**（`1_picked_A.png`），定的大小（每个游戏像素 1.5 格）：**从头盔顶到鞋底 48 格**（游戏里 32 行）。头的比例保持原画那样（头盔顶到胡子下沿约占身高一半，约德尔人）。
> - 我把 A 按这个大小直接缩好了（`2_target_A.png`，每格 14 px），**大小、位置、比例、姿势都对，但糊了**：近侧的绿色镜片几乎没了、两个镜片大小不一样，牙齿成了零散的白点，胡子和脸混成一片肉色，头盔的蓝红条纹断断续续，炸弹上的白骷髅变成杂点，牛仔蓝背带裤和蓝钢护腿糊在一起，靴子的灰钢色分不出档。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 14 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**画两稿。**

## 大小和位置（照 `2_target_A.png` / `3_layout_A.png`）

- 画布 **1024 × 1024**，**每格 14 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **头盔顶在 y = 288**（绿线），**胡子下沿在 y = 652 左右**（蓝线），**两只鞋底在 y = 960**（红线）。
- 人连两颗炸弹大约 62 格宽、48 格高，位置照 `2_target_A.png`：左边（近侧手）的炸弹约在 x = 100–240，右边（远侧手）的炸弹约在 x = 770–930，引线和火星在炸弹上方，全都在画布里。

## 要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍放大）：
  - **圆头盔**：蓝色和红色的条纹，每种颜色 2–3 档、上面一条亮边；头盔前面一块灰蓝色的护板。
  - **两个绿色护目镜片一样大、一样高**（各约 4×4 格的圆块，绿 2–3 档，每片一个 1–2 格的白高光），**红色镜框**一圈。这两个镜片就是他的眼睛，在游戏里必须一眼能看到。
  - **长尖耳朵**向两边伸出（米黄色，里面一格粉色）。
  - **咧嘴大笑**：一排**白牙**（白和浅灰两档，牙缝用浅灰，不要一片白），上下嘴唇深色。
  - **米黄色的毛胡子和鬓毛**围着脸，2–3 档（亮、中、暗），外缘是毛茸茸的锯齿，和肉色的脸分得开（胡子偏黄、脸偏粉）。
- **身体**：红外套和红袖子（红 3 档）；**牛仔蓝背带裤**（前面一块护胸，两颗小纽扣）；**橙色手套**；**蓝钢护膝护腿**（带一格亮边）；**灰钢色的大圆靴子**（2–3 档灰，有高光）；背后露出一点红炸药包。
- **炸弹**：两颗**红色圆炸弹**（红 3 档，有一个亮的高光），**白色骷髅头**清楚（约 4×4 格，白和浅灰），顶上一小截**深色引线**和 **2–3 格黄橙色火星**。炸弹是正圆的，左右两颗一样大。
- **姿势**：两脚分开、膝盖微弯、身子稍微弓着，两手向两边伸开各托一颗炸弹，脸朝右前方咧嘴笑。3/4 正面朝右：近侧的手臂和腿在画面左边、颜色亮，远侧的在画面右边、稍暗（照 `1_picked_A.png`）。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。**牛仔蓝和蓝钢一定要有偏亮的边**，不然在游戏里会糊成一团。

## 干净

- 和附图 5–8（本包的嘉文四世、斯维因、烈娜塔，每游戏像素 1.5 格，和吉格斯一样；库奇（约德尔人）2.2 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（蓝红条纹头盔、绿镜片红框、米黄胡子、白牙、红外套、牛仔蓝背带裤、橙手套、蓝钢护腿、灰钢靴子、红炸弹白骷髅）。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（爆炸、发光都不画）。

## 附图（压缩包 `ziggs_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` | 按新大小缩到每格 14 px 放在画布上（糊的） | **大小、位置、比例、姿势**照它，糊的地方重画 |
| `3_layout_A.png` | 同一张加网格线：绿线 = 头盔顶，蓝线 = 胡子下沿，红线 = 地面 | 对齐网格、头的大小、地面线的位置 |
| `4_head.png` | A 的头（第 0 步读回后 8 倍放大） | 头盔、护目镜、耳朵、牙齿、胡子 |
| `style/5_style_jarvaniv.png` … `8_style_corki.png` | 本包的嘉文四世、斯维因、烈娜塔（每游戏像素 1.5 格）、库奇（2.2 格），8 倍放大 | **只看风格**：这个密度下一格有多大、脸和眼睛怎么画、深色衣服的亮边 |

## 提示词：`ziggs-model-A-1.png`、`ziggs-model-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art picture of this character - a yordle bomb expert: a round helmet with blue and red stripes and a grey-blue plate in front, two big round GREEN GOGGLE LENSES in red rims (his eyes), long pointed ears out to the sides, a huge grin with a row of white teeth, a bushy blond-tan beard and mutton chops; a red jacket with red sleeves, denim-blue overalls with a bib and two small buttons, orange gloves, blue-steel knee and shin guards, big round grey-steel boots, a little of a red satchel behind him; feet wide apart, knees bent, a little hunched, BOTH ARMS HELD OUT TO THE SIDES, a round red bomb with a white skull, a short dark fuse and a yellow-orange spark resting in each hand (the LOOK, the COLOURS and the DETAILS to keep); 2 the same picture shrunk to its final game size on a 1024x1024 canvas, 14 px squares - the SIZE, the PLACE, the PROPORTIONS and the POSE are right, but it is muddy (the near green lens almost gone and the two lenses of different sizes, the teeth scattered white dots, the beard and the face one skin-coloured mass, the helmet's stripes broken, the skulls on the bombs turned to noise, the denim overalls and the steel guards smeared together, the boots' greys mixed); 3 the same with grid lines every 5 squares: the green line = the top of his helmet, the blue line = the bottom of his beard, the red line = the ground; 4 his head enlarged; 5-8 STYLE ONLY: other characters from the same game, shown 8x so every square is one pixel (5, 6 and 7 at this same square density, 8 another yordle) - copy their pixel-art look, how a face, goggles, teeth and dark clothes with light edges are drawn at this size.
Draw with the image generator ONE clean pixel-art picture of the character: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place, proportions and pose of image 2: every square 14 px, aligned on one straight grid starting at the canvas corner, the top of his helmet at y 288, the bottom of his beard at about y 652 (the head about half his height, a yordle), both soles on the ground line y 960, 48 squares from the helmet's top to the soles, about 62 squares wide with the two bombs - feet wide apart, knees bent, both arms out to the sides each holding a bomb, the face to the front-right, 3/4 view facing right - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the helmet's blue and red stripes in 2-3 shades each with a light top edge, the grey-blue front plate; TWO GREEN GOGGLE LENSES of the SAME size at the SAME height (round, about 4x4 squares each, 2-3 greens, a 1-2 square white highlight in each) in red rims - they are his eyes and must read at a glance; the long ears out to the sides (blond-tan, one pink square inside); the big grin with a row of WHITE TEETH (white and light grey, light grey gaps, never one white blob) and dark lips; the blond-tan beard and mutton chops in 2-3 shades with a furry jagged outer edge, clearly apart from the pinker face; the red jacket in 3 reds; the denim-blue overalls with a bib and two buttons; orange gloves; blue-steel knee and shin guards with a light edge; big round grey-steel boots in 2-3 greys with a highlight; the two round red bombs the same size, 3 reds and a highlight, a clear WHITE SKULL (about 4x4 squares, white and light grey), a short dark fuse and a 2-3 square yellow-orange spark on each.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); the denim and the steel with LIGHTER EDGES so they never turn into one dark mass; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no explosion, no glow), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` 一样：每格 14 px、对齐网格；头盔顶 y 288、胡子下沿约 y 652、鞋底 y 960；连炸弹约 62 格宽。
- 两个绿镜片一样大一样高、有白高光；牙齿清楚；胡子和脸分得开；头盔条纹清楚；炸弹上的白骷髅清楚、两颗一样大；牛仔蓝和蓝钢有亮边；外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/ziggs-model/`）

- `ziggs-model-A-1.png`、`ziggs-model-A-2.png`；**image_gen 的原始生成图原样放 `outputs/ziggs-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/ziggs_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 48 行（不经过脸和镜片），和 `2_target_A.png` 并排、按游戏大小和库奇、小鱼人、崔丝塔娜、提莫放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，嘉文 / 内瑟斯的方式；**炸弹是刚体，每帧都用设计里的同一颗**；腿用设计自己的整条腿，不用 Codex 画的腿）：待机（呼吸）、走路、普攻 Ziggs_Attack1（扔小炸弹）、Q skill（Ziggs_Spell1 抛投）、E skill2（Ziggs_Spell3 撒雷）、W skill_w（Ziggs_Spell2 脚下炸开）、R ult（Ziggs_Spell4 抛出大炸弹）、受击、死亡 Ziggs_Death。
