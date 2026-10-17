# 嘉文四世（德玛西亚皇子）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 嘉文四世是**德玛西亚的年轻皇子、身穿金甲的骑士**：年轻的脸、坚毅的下巴；头戴**金色的王冠式头盔**（几根向上的金色尖角，额前一颗**蓝色宝石**），头盔后面拖着一束**深蓝色的羽冠（马鬃一样的头发）**。身上是**金色板甲**：两个**巨大的金色肩甲**，边上长着几根**银灰色的弯尖刺**；胸甲、护臂、护膝、长靴都是金色的，镶**亮蓝色宝石**；金甲下面是**深藏青偏紫的布衣和裤子**，腰间垂着深色的布片。他拿着一根**很长的骑枪（长矛）**：**银白色的长枪头**（又长又尖，两侧有倒刺和装饰），枪头下面一个**带蓝宝石的银色护手**，**深色的长杆**，杆尾一个小球。请 Codex 画**两张全身像**（同一个嘉文，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、8a）。他站直，**骑枪竖着立在身前偏右（画面右边）**，一只手握着枪杆中段，枪头朝上、比他的头高出很多，杆尾落在脚边地上。另一只手放松垂下。
> - **B：备战姿势**（附图 8b 只看枪的形状和方向）。两脚分开、膝盖微弯、身体稍微前倾，**双手握枪，枪斜着放低：银色枪头在前面（画面右边）靠近地面，杆尾斜向身后上方（画面左边）**——像本包的潘森（附图 12）那样拿枪。这样整个人矮一些、横向宽一些。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（PPU 1.5）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的盖伦（同是德玛西亚的金甲骑士）、潘森（长矛）和斯维因，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：健壮的骑士，**头（连头盔）约占身高的四分之一**（约 18 格），不要大头娃娃，也不要写实的细长比例。肩膀很宽（大肩甲），腰比肩窄，腿结实。
> - **头**（附图 3 特写）：金色王冠头盔（几档金：亮金、金、暗金、棕金，不要一片黄），尖角清楚，额前蓝宝石；头盔下露出年轻的脸，**两只眼睛一样大、一样高**；头盔后面深蓝色的羽冠。
> - **铠甲**：金色大肩甲（带银灰色的弯尖刺），金色胸甲、护臂、护膝、长靴，都镶亮蓝宝石；**深藏青偏紫的布衣和裤子**在金甲之间露出来。
> - **骑枪**：**比他高**（A 里枪尖到杆尾约是他身高的 1.5 倍；B 里约 1.3 倍）；银白色的长枪头（形状照附图 7），蓝宝石护手，深色长杆。枪头和枪杆**必须完整地画出来**、形状清楚，不要只剩一根细线。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只鞋底落在同一条地面线上。
> - **画布用正方形 1536×1536**。**从头盔顶（尖角）到鞋底约 792 px，也就是约 72 格**（骑枪不算），鞋底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。A 的枪尖会比头盔高很多（附图 8a，枪尖约在 y = 180），B 的枪尖在前下方；骑枪、尖角全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金甲、蓝宝石、深藏青布、银灰尖刺、银白枪头、深蓝羽冠、脸要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**深藏青的布很暗，一定要有偏亮的边**，不然在深色背景上会糊成一团。
> - 不画任何特效（军旗、金色护盾、击飞的光、大招的岩石圈都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/jarvaniv-picture/jarvaniv-A.png`、`jarvaniv-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/jarvaniv-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/jarvaniv_picture_done.zip`。

## 附图（在压缩包 `jarvaniv_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_jarvan_idle.png` | 英雄联盟原版嘉文的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势和拿枪的方法 |
| `refs/2_jarvan_frontal.png` | 同一帧，正面 | 肩甲、胸甲、腰间布片、护膝怎么排 |
| `refs/3_jarvan_head.png` | 头部特写（没画骑枪） | 金色王冠头盔、尖角、蓝宝石、深蓝羽冠、脸 |
| `refs/4_jarvan_back.png` | 同一帧的背后 | 肩甲背面、羽冠、背后的布 |
| `refs/5_jarvan_splash.png` | 官方加载画面 | 气质、金甲的颜色 |
| `refs/6_jarvan_ready.png` | 普攻的一帧：双手持枪刺出 | B 双手握枪的样子、身体前倾 |
| `refs/7_jarvan_lance.png` | 骑枪单独的侧面 | 枪头、护手、枪杆、杆尾的形状和比例 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰），骑枪竖起来的高度 |
| `refs/8b_layout_B.png` | B 的布局示意（英雄联盟的出枪姿势，只看枪的形状） | 他的位置和大小、地面线（灰）；**枪按文字拿：斜着放低，不要平伸出画** |
| `style/11_style_garen.png` | 本包的盖伦，8 倍放大，一格 = 一个像素 | **只看风格**：德玛西亚金甲、蓝色和金色怎么分档 |
| `style/12_style_pantheon.png` | 本包的潘森（8 倍，PPU 1.5，和嘉文一样） | **只看风格**：长矛在格子上怎么画、B 的拿法 |
| `style/13_style_swain.png` | 本包的斯维因（8 倍，PPU 1.5） | **只看风格**：脸、眼睛、暗色衣服的亮边 |

## 提示词：`jarvaniv-A.png` / `jarvaniv-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a YOUNG PRINCE IN GOLD ARMOUR - a young face with a strong jaw; a GOLD CROWN-LIKE HELMET with several upright gold spikes and a BLUE GEM on the brow, a DARK-BLUE PLUME (like a horse-hair crest) flowing from the back of the helmet; GOLD PLATE ARMOUR - two HUGE GOLD PAULDRONS edged with curved SILVER-GREY SPIKES, a gold breastplate, gold bracers, knee guards and tall gold boots, all set with BRIGHT BLUE GEMS; under the gold, DARK NAVY-VIOLET cloth and trousers, dark cloth flaps at the waist; he holds a VERY LONG LANCE: a long SILVER-WHITE SPEARHEAD with barbs and ornaments, a silver guard with a blue gem under it, a long dark shaft, a small ball at the butt end (1 his idle, 3/4 view facing right - the look, the ANGLE, pose A and how he holds the lance; 2 the same from the front: the pauldrons, the breastplate, the waist flaps, the knee guards; 3 the head close-up without the lance: the crown helmet, its spikes, the blue gem, the blue plume, the face; 4 the same from behind: the pauldrons' back, the plume; 5 the official illustration: his mood and the gold's colour; 6 one of his attacks: both hands on the lance, leaning forward; 7 the lance alone from the side: the spearhead, the guard, the shaft, the butt, their proportions). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, gold armour and blue cloth split into clear shades (11, a knight of the same kingdom), a long spear on the grid (12), a face with two clear eyes and dark clothes with light edges (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the helmet spikes, the plume, the lance and its spearhead whole); both soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 792 px (about 72 squares) from the helmet's spike tips to his soles - the lance not counted.
PROPORTIONS: a strong knight - the head with the helmet about a quarter of his height (about 18 squares), NOT a big-headed doll and NOT realistic slim proportions; very broad shoulders (the gold pauldrons), the waist narrower, strong legs.
THE HEAD: the gold crown helmet in bright gold / gold / dark gold / brown-gold (never one flat yellow), its spikes clear, the blue brow gem; a young face under it with TWO EYES of the SAME size at the SAME height; the dark-blue plume behind.
THE ARMOUR: huge gold pauldrons with curved silver-grey spikes; a gold breastplate, gold bracers, knee guards and tall gold boots with bright blue gems; the dark navy-violet cloth and trousers showing between the gold.
THE LANCE: longer than he is tall; a long silver-white spearhead with barbs (shaped like image 7), a silver guard with a blue gem, a long dark shaft, a small ball at the butt; the spearhead and the shaft drawn whole with a clear shape (never just a thin line).
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark navy-violet cloth with LIGHTER EDGES so it never turns into one dark mass, the gold armour, the blue gems, the silver-grey spikes, the silver-white spearhead, the blue plume and the face clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no banner, no golden shield, no glow, no rocks), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (jarvaniv-A.png): his idle (images 1 and 8a) - standing upright, the LANCE STANDING UPRIGHT in front of him on the image right, one hand gripping the shaft at mid height, the spearhead pointing up far above his helmet (its tip near y = 180), the butt end on the ground by his feet; the other arm relaxed at his side; the face to the front-right. The whole lance about 1.5 times his height.
POSE B (jarvaniv-B.png): a READY STANCE - the SAME prince with the SAME 11-px squares: feet apart, knees slightly bent, leaning a little forward, BOTH HANDS on the lance held LOW and DIAGONAL: the SILVER SPEARHEAD IN FRONT (image right) near the ground, the butt end slanting up behind him (image left), like the spear of image 12; the lance about 1.3 times his height, whole inside the picture (image 8b shows only the lance's shape and his lean - do NOT hold it out flat as there).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头盔尖角、羽冠、骑枪完整，不出画。
- 比例：健壮的骑士，头（连头盔）约占身高四分之一（约 18 格），不是大头娃娃；两只眼睛一样大、一样高。
- 头：金色王冠头盔分几档金色、尖角清楚、额前蓝宝石；年轻的脸；后面深蓝羽冠。
- 铠甲：金色大肩甲带银灰弯尖刺；金色胸甲、护臂、护膝、长靴镶亮蓝宝石；深藏青偏紫的布衣和裤子。
- 骑枪：比他高（A 约 1.5 倍、B 约 1.3 倍），银白长枪头（带倒刺）、蓝宝石护手、深色长杆、杆尾小球，完整清楚。
- A：站直，骑枪竖在身前偏右、枪头朝上高过头盔很多、杆尾落在脚边；B：双手持枪斜着放低、枪头在前下方。从头盔尖到鞋底约 792 px（约 72 格），鞋底都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/jarvaniv-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/jarvaniv_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/jarvaniv/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_nasus_hd.py` 的做法），和已合并的打野、盖伦、潘森按游戏里的大小并排，给用户挑 A / B 和定大小；PPU 1.5（用户选的），身体（不算骑枪）显示高度约 40 个游戏像素。
- 定下后第 1 步按游戏格子重画，再自己做动作帧（塔姆 / 内瑟斯的方式，无损：只平移、整块直角转、整行移；**骑枪是刚体，只能整根平移或直角转，每帧都用设计里的同一根枪**——内瑟斯的教训）；走路：两腿各自整块移动（内瑟斯的宽站姿走法），不用 Codex 换皮。英雄联盟的动作：普攻 jarvanIV_attack1 / attack2 / attack3（双手出枪刺）；Q 巨龙撞击 jarvanIV_spell1 + spell1_dash；W 黄金圣盾 jarvanIV_spell2；E 德邦军旗 jarvanIV_spell3（扔旗）；R 天崩地裂 jarvanIV_spell4（跳起砸下）；死亡 jarvanIV_death。
