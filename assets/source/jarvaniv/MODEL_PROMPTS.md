# 嘉文四世：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（竖枪待机）**（`1_picked_A.png`），定的大小（每个游戏像素 1.5 格）：**从头盔顶到鞋底 60 格**（游戏里 40 行，骑枪不算），骑枪的枪尖再高出头盔约 12 格。
> - 用户还要求**头放大到约四分之一**：**从头盔顶到下巴 15 格**（原画里头只占身高约五分之一）。头盔、尖角、额前蓝宝石、羽冠都跟着放大，**脸要清楚**：两只眼睛一样大、一样高（各 2 格左右，能看出眼白和瞳孔），鼻子、嘴、下巴分得出来。
> - 我把 A 按这个大小直接缩好了（`2_target_A.png`，每格 12 px，头已经放大），**大小、位置、比例、姿势都对，但糊了**：脸只剩几个肉色格子，头盔的尖角和羽冠混在一起，几档金色分不开，蓝宝石变成零散的亮格，深藏青的布糊成一片，肩甲的银刺断断续续，骑枪的枪头和护手成了杂点。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**画两稿。**

## 大小和位置（照 `2_target_A.png` / `3_layout_A.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **头盔顶在 y = 240**（绿线），**下巴在 y = 420**（蓝线），**两只鞋底在 y = 960**（红线）。
- 人连骑枪大约 32 格宽、73 格高，位置照 `2_target_A.png`：人在左边，骑枪竖在身前偏右，**枪尖约在 y = 96**，杆尾落在右脚边的地面上。

## 要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍放大）：
  - **金色王冠头盔**分 3–4 档（亮金、金、暗金、棕金），几根向上的**尖角清楚、彼此分开**，额前和两侧各一颗**亮蓝宝石**（2×2 左右的整齐小块，带一格亮点）。
  - 头盔后面**深蓝色的羽冠**，向身后飘，几档蓝色分得开，和头盔的金色有清楚的边界。
  - **年轻的脸**：肉色 2–3 档；**两只眼睛一样大、一样高**，看得出眼白和深色瞳孔；鼻子和下巴的轮廓清楚。
- **铠甲**：两个大金色肩甲，边上的**银灰色弯尖刺**一根一根分开（2 格粗）；金色胸甲、护臂、护膝、长靴，镶**亮蓝宝石**（整齐小块，不要散成单格）；金色分 3–4 档。
- **布料**：金甲之间露出的**深藏青偏紫**的布衣和裤子，**一定要有亮一点的边**，不然在游戏里会糊成一团。
- **骑枪**：**枪杆连续不断**（2 格粗，深色、亮暗两档）；**银白色长枪头**形状清楚（尖、两侧倒刺，银白 2–3 档）；枪头下面**带蓝宝石的银色护手**；杆尾一个小银球，落在地上。
- **姿势**：站直，骑枪竖在身前偏右，近侧（画面右边）的手握住枪杆中段；另一只手放松垂在身侧。3/4 正面朝右（脸朝右前方）。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包的潘森、斯维因、贾克斯，每游戏像素 1.5 格，和嘉文一样；盖伦 1.9 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（金甲、亮蓝宝石、深藏青偏紫的布、银灰尖刺、深蓝羽冠、银白枪头、深色枪杆）。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（军旗、护盾、发光都不画）。

## 附图（压缩包 `jarvaniv_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` | 按新大小缩到每格 12 px 放在画布上，头已放大（糊的） | **大小、位置、比例、姿势**照它，糊的地方重画 |
| `3_layout_A.png` | 同一张加网格线：绿线 = 头盔顶，蓝线 = 下巴，红线 = 地面 | 对齐网格、头的大小、地面线的位置 |
| `4_head.png` | A 的头（第 0 步读回后 8 倍放大） | 头盔、尖角、宝石、羽冠、脸 |
| `style/5_style_pantheon.png` … `8_style_garen.png` | 本包的潘森、斯维因、贾克斯（每游戏像素 1.5 格）、盖伦（1.9 格），8 倍放大 | **只看风格**：这个密度下一格有多大、脸和眼睛怎么画、金甲和长矛怎么画 |

## 提示词：`jarvaniv-model-A-1.png`、`jarvaniv-model-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art picture of this character - a young prince in gold plate armour: a gold crown-like helmet with several upright spikes and bright blue gems, a dark-blue plume flowing back from it, a young face; two huge gold pauldrons edged with curved silver-grey spikes, a gold breastplate, bracers, knee guards and tall boots set with bright blue gems, dark navy-violet cloth and trousers between the gold; a very long lance standing upright in front of him on the image right (a long silver-white barbed spearhead far above his helmet, a silver guard with a blue gem, a long dark shaft, a small silver ball at the butt on the ground), his near hand gripping the shaft at mid height, the other arm relaxed (the LOOK, the COLOURS and the DETAILS to keep); 2 the same picture shrunk to its final game size on a 1024x1024 canvas, 12 px squares, the head already enlarged to a quarter of his height - the SIZE, the PLACE, the PROPORTIONS and the POSE are right, but it is muddy (the face reduced to a few skin squares, the helmet's spikes merged with the plume, the gold shades mixed, the blue gems scattered into loose bright squares, the dark cloth smeared into one mass, the pauldrons' silver spikes broken, the spearhead and the guard turned to noise); 3 the same with grid lines every 5 squares: the green line = the top of his helmet, the blue line = his chin, the red line = the ground; 4 his head enlarged; 5-8 STYLE ONLY: other characters from the same game, shown 8x so every square is one pixel (5, 6 and 7 at this same square density) - copy their pixel-art look, how a face with two clear eyes, gold armour and a long spear are drawn at this size.
Draw with the image generator ONE clean pixel-art picture of the character: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place, proportions and pose of image 2: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of his helmet at y 240, his chin at y 420 (the head about a quarter of his height: 15 squares of 60), both soles on the ground line y 960, about 60 squares from the helmet's top to the soles, the lance's tip at about y 96 - standing upright, the lance standing upright in front of him on the image right, the near hand on the shaft at mid height, the butt on the ground by his feet, the other arm relaxed at his side, 3/4 view facing right - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the GOLD CROWN HELMET in 3-4 gold shades (bright gold, gold, dark gold, brown-gold), its upright spikes clear and apart, its bright blue gems neat small blocks (about 2x2 with a 1-square light); the dark-blue plume flowing back, its blues clearly apart from the gold; the YOUNG FACE in 2-3 skin shades with TWO EYES of the SAME size at the SAME height (about 2 squares each, white and a dark pupil), the nose and chin readable; the huge gold pauldrons with their curved silver-grey spikes drawn one by one (2 squares thick); the gold breastplate, bracers, knee guards and boots with neat bright blue gems; the dark navy-violet cloth with LIGHTER EDGES so it never turns into one dark mass; the lance's dark shaft CONTINUOUS (2 squares thick, a light and a dark shade), the silver-white barbed spearhead with a clean shape (2-3 silver shades), the silver guard with its blue gem, the small silver ball at the butt.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no banner, no shield, no glow), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` 一样：每格 12 px、对齐网格；头盔顶 y 240、下巴 y 420、鞋底 y 960；枪尖约 y 96。
- 头约占身高四分之一；脸清楚、两只眼睛一样大一样高；头盔尖角分开、宝石是整齐的小块；羽冠和金色分得开；深藏青的布有亮边；肩甲银刺一根根分开；枪杆连续、枪头和护手完整；外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/jarvaniv-model/`）

- `jarvaniv-model-A-1.png`、`jarvaniv-model-A-2.png`；**image_gen 的原始生成图原样放 `outputs/jarvaniv-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/jarvaniv_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 60 行身体（不经过脸），和 `2_target_A.png` 并排、按游戏大小和潘森、赵信、盖伦、蔚、李青放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，塔姆 / 内瑟斯的方式；**骑枪是刚体，每帧都用设计里的同一根枪，只整根平移或直角转**）：待机、走路（宽站姿：两腿各自整块移动，内瑟斯的走法）、普攻 jarvanIV_attack1（双手出枪刺）、E→Q：skill（扔旗）+ skill_dash（拖枪冲刺）+ skill_land、Q 单放 skill2（jarvanIV_spell1 出枪）、W skill_w（jarvanIV_spell2 举盾）、R ult（jarvanIV_spell4 跳起砸下）、受击、死亡 jarvanIV_death。
