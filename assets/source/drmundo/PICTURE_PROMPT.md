# 蒙多医生（祖安狂人）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 蒙多是一个**紫色皮肤的巨大肌肉怪人**，自称医生：一颗小小的方脑袋缩在两座小山一样的肩膀中间，手里拎着一把生锈的大骨锯（带锯齿的切肉刀）。请 Codex 用同一段提示词画**两版**全身像素风原图，我从中挑一张。两版是同一个蒙多，长相、衣服、颜色、格子大小都一样，只有姿势不同：
> - **A**：英雄联盟里的待机（附图 1）。微微驼背站着，骨锯垂在近侧手里，另一只手空着，自然垂在身侧。
> - **B**：英雄联盟里普攻的抬手（附图 6）。近侧手臂把骨锯高高举过头顶，身子往前压，嘴张开吼。
>
> 选定一张后，第 1 步再按它做正面和侧面的造型。这一版每个游戏像素约 **1.8 格**。附图 9–12 是本包里的加里奥、布隆、酒桶、伊莉丝，其中伊莉丝也是 1.8 格。你画的原图会按格子直接读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **不要 Q 版大头**：蒙多是大块头，头**很小**，往前探着缩在两个巨大的肩膀和斜方肌中间，脖子几乎看不到。肩膀、胸口和两条粗胳膊才是最大的形状，手大，腿短而粗。比例照原版，不要画成大头小身子的卡通娃娃。
> - **头和脸**（附图 3 特写）：
>   - **黑色的短刺头**，头顶一撮往上、往后翘。
>   - 方下巴，脸是紫色。**近侧一只发光的粉红 / 洋红色眼睛**，周围一圈暗色眼窝，要看得清；远侧那只眼睛被挡住一部分。
>   - 嘴微张，露出几颗**歪歪扭扭的米白色牙齿**（下牙往上翘），嘴唇偏灰紫。
> - **身体**：
>   - 皮肤是**紫色 / 淡紫色**：亮面偏粉的淡紫，暗面是深紫，肌肉块（胸肌、三角肌、二头肌、前臂）分得清楚。
>   - 两边肩头各嵌着**一块金铜色的星形金属片，中间一颗发红光的粉红宝石**（电击器的插座）；手臂上散着几颗**小铜钉**。
> - **衣服**（附图 1、2、4、7）：
>   - 上身是一件**米白 / 灰白色的无袖病号服**，领口撕成一圈，胸前交叉着几条**带铜扣的皮带**，衣服上有一道**紫色闪电形的破口**，胸口别一个小名牌。
>   - 两只手腕缠着**米白色的绷带**。
>   - 腰上一条**棕色皮带**，近侧挂一个小皮包。
>   - 下身是**灰蓝色的肥大工装裤**，有补丁、膝盖处一条绑带，沾着几块**黄绿色的污渍**。
>   - **光着两只大紫脚**，近侧那只脚穿一只**灰色的人字拖 / 凉鞋**。
> - **骨锯**（附图 1、6）：一把**很大的切肉刀式骨锯**。刀身是**偏青的灰白钢色**，下缘一排**粗大的锯齿**；刀背是**锈橙 / 棕色**，带铜边；刀柄缠着深色布条，接口处有一圈**青蓝色的箍和铆钉**。附图 1 里骨锯是侧着对镜头的（只看得到刀背），请照附图 2 把**刀面转过来**，让锯齿看得清。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂（拿骨锯的那只）和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**，两只脚底落在同一条地面线上。
> - **画布用横版 1536×1024**：**从头发顶到脚底约 858 px，也就是约 78 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线）。骨锯、手、头发全在画面里，B 版举起的骨锯也不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。紫色皮肤分出清楚的几档（亮粉紫、淡紫、紫、深紫）；病号服的米白、裤子的灰蓝、皮带的棕色、骨锯的钢青和锈橙要分得开，不要糊成一团；眼睛和肩上宝石的粉红只用在这两处。
> - 不画任何特效（飞出去的骨锯、电击的闪电、喝药的光圈都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/drmundo-picture/drmundo-A.png`、`drmundo-B.png`（1536×1024 横版，**真透明背景**）；原始生成图原样放进 `outputs/drmundo-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/drmundo_picture_done.zip`。

## 附图（在压缩包 `drmundo_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_mundo_idle.png` | 英雄联盟原版蒙多的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_mundo_frontal.png` | 同一帧，几乎正面 | 病号服、交叉皮带、铜扣、名牌、裤子、两只脚 |
| `refs/3_mundo_head.png` | 头部特写 | 黑色刺头、粉红眼睛、歪牙、方下巴 |
| `refs/4_mundo_back.png` | 同一帧的背后 | 背上的肌肉、病号服的背带、腰包 |
| `refs/5_mundo_splash.png` | 官方加载画面 | 气质（疯狂、得意、力大无穷） |
| `refs/6_mundo_swing.png` | 普攻抬手，骨锯举过头顶 | B 的姿势、骨锯正面的样子 |
| `refs/7_mundo_side.png` | 待机的侧面（朝右） | 第 1 步用（这一步不用） |
| `refs/8_layout.png` | 布局示意（从模型上剪的，只看位置和大小） | 横版画布上他的位置、脚底线（深灰） |
| `style/9_style_galio.png` | 本包的加里奥（大体型），8 倍放大，一格 = 一个像素 | **只看风格**：像素粗细、描边、明暗 |
| `style/10_style_braum.png` | 本包的布隆（8 倍） | **只看风格**（壮汉） |
| `style/11_style_gragas.png` | 本包的酒桶（8 倍） | **只看风格**（大块头） |
| `style/12_style_elise.png` | 本包的伊莉丝（8 倍，和蒙多一样每游戏像素 1.8 格） | **只看风格**：这个密度下格子有多细 |

## 提示词：`drmundo-A.png` / `drmundo-B.png`（同一段提示词，只换最后一句姿势）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a huge, mad, purple-skinned brute who calls himself a doctor, a tiny head between enormous shoulders, a rusty bone saw in his hand (1 his idle in 3/4 view facing right - the look, the ANGLE and pose A of this picture; 2 the same nearly from the front: the patient's top, the crossed straps with brass buckles, the name tag, the trousers, both feet; 3 his head close-up: the black spiky hair, the glowing pink eye, the crooked teeth, the square jaw; 4 the same from behind: the back muscles, the straps, the hip pouch; 5 the official illustration: his mood; 6 his attack wind-up, the saw raised over his head - pose B; 7 his idle from the side - not used here). Image 8 is THIS picture's layout guide: where he goes on the canvas, the dark grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 9-12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading. Image 12 has the same square density this picture needs.
Create ONE pixel-art picture of him, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha). He is about 858 px (about 78 squares) from the top of his hair to the soles of his feet, the soles about 64 px above the bottom edge (the dark grey line of image 8); the saw, the hands and the hair whole inside the picture (the raised saw of pose B too), comfortable transparent margins, nothing cut off; both soles level on one ground line.
NOT CHIBI: keep the game model's own proportions (image 1): a SMALL head pushed forward and sunk between HUGE shoulders and trapezius muscles, almost no neck; the shoulders, the chest and the two thick arms are the biggest shapes, big hands, short thick legs. Do not draw a big cartoon head on a small body.
THE HEAD: short spiky BLACK hair with a tuft standing up and back; a square jaw; purple face; ONE glowing PINK / MAGENTA eye on the near side inside a dark socket, clearly readable (the far eye partly hidden); the mouth a little open showing a few crooked cream-white teeth (an underbite), greyish-purple lips.
THE BODY: PURPLE / LILAC skin - pinkish light lilac on the lit planes, deep violet in the shadows - with clearly separated muscle masses (chest, deltoids, biceps, forearms); on each shoulder a BRONZE-GOLD STAR-SHAPED PLATE with a glowing PINK-RED GEM in the middle; a few small bronze rivets in the arms.
THE CLOTHES: a sleeveless OFF-WHITE / pale grey PATIENT'S TOP with a ragged torn neckline, leather STRAPS WITH BRASS BUCKLES crossing the chest, a purple LIGHTNING-SHAPED RIP in the cloth and a small name tag; CREAM BANDAGES wrapped round both wrists; a BROWN LEATHER BELT with a small pouch at the near hip; baggy BLUE-GREY work TROUSERS with patches, a strap at the knee and a few yellow-green stains; two big BARE PURPLE FEET, the near foot in one grey flip-flop sandal.
THE BONE SAW: a BIG cleaver-like bone saw in his NEAR hand: a pale teal-steel blade with a row of big jagged SAW TEETH on its lower edge, a RUSTY ORANGE-BROWN back with bronze trim, a dark cloth-wrapped grip with a TEAL-BLUE band and rivets where it meets the blade. In image 1 the saw is seen edge-on: draw its FLAT SIDE turned to us as in image 2, the teeth readable.
THE VIEW: 3/4 view facing right (face to the front-right): the NEAR arm (holding the saw) and leg on the image LEFT in full tone, the FAR ones on the image RIGHT a step darker; both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, no stray single odd squares: the skin in clear purples (light pinkish lilac, lilac, purple, deep violet), the patient's top off-white, the trousers blue-grey, the belt and straps brown, the buckles and plates bronze-gold, the blade teal-steel with a rusty orange back; the pink used only for the eye and the shoulder gems; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no flying saw, no lightning, no chemical glow), no background, no ground, no shadow, no text, no frame, no other characters.
POSE A (drmundo-A.png): his idle (image 1) - standing a little hunched, the bone saw hanging down in the near hand, the far hand empty and hanging at his side.
POSE B (drmundo-B.png): his attack wind-up (image 6) - the near arm raising the bone saw high over his head, the body leaning forward, the mouth open in a roar.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1024 横版；四周留边，骨锯、手、头发完整，不出画。
- **不是 Q 版**：小脑袋缩在两个巨大的肩膀中间，粗胳膊、大手、短粗腿。
- 头：黑色刺头；**近侧一只发光粉红眼睛看得清**；方下巴、歪牙、嘴微张。
- 身体：紫色皮肤分出几档、肌肉块清楚；两肩的铜色星形片 + 粉红宝石；手臂上的小铜钉。
- 衣服：米白无袖病号服 + 交叉皮带铜扣 + 紫色闪电破口 + 小名牌；手腕绷带；棕皮带和腰包；灰蓝肥裤（补丁、绑带、黄绿污渍）；两只光脚，近侧那只穿灰色人字拖。
- 骨锯：钢青刀身 + 下缘大锯齿 + 锈橙刀背 + 青蓝色箍的刀柄，拿在近侧手里。
- 从头发顶到脚底约 858 px（约 78 格）；近侧手脚在画面左边、颜色亮，远侧在右边、稍暗；脚底在同一条水平线上；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- A、B 两版都画完后，最后写 `outputs/drmundo-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/drmundo_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两版都画完再交。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/drmundo/codex_picture/`。**先在 8 倍下数描边台阶，量出 Codex 实际的格子大小**（它从来不是要求的 11 px），再按它自己的格子读回（`design_tahmkench_hd.py` / `design_kalista_hd.py` 的办法，先量化到约 40 色再读）。然后在 PPU 1.8 / 1.5 / 1.2 下和加里奥、布隆、酒桶、塞恩、塔姆的游戏帧并排，让用户挑 A / B 和大小。
- 头的占比照原版和 oppi 的蒙多（46 行里头约 10 行，[[head-share-like-oppi]]）。用户说脸不对时，先查头的大小，再动五官。
- 选定后写第 2 步动作包（塔姆、卡莉丝塔的 `pack_*_strips.py`）；Codex 额度不够时，用定稿自己的像素摆动作（`rig_*.py`，只做无损变换）。
