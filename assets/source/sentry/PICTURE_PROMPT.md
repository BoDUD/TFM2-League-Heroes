# 苍蓝哨戒（金铲铲之战 · 第 18 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 苍蓝哨戒是金铲铲之战第 18 赛季的一费卡（峡谷野怪 / 神谕），技能「蔚蓝激光」：**一对漂浮在空中的高瘦水晶石**（英雄联盟峡谷蓝 buff 营地里的小石像）。它**没有手脚、没有脸**，整只就是两块石头。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **两块石头**：**左右两块高高的尖石**并排竖着，中间留一条窄缝。**左边那块更高**，顶上是一个**尖尖的多面晶顶**；**右边那块矮一点**，顶是**圆钝的**。两块的**上半截是浅灰绿 / 鼠尾草绿的岩面**（3–4 档，带几道浅色的棱），**下半截是深海军蓝 / 蓝紫色**（3 档），越往下越窄，**底下收成一个尖**。两块石头内侧的缝边各有**一道暗红紫色的细边**。
> - **中间的圆孔**（附图 3 特写）：两块石头在**中间偏上**的地方各挖掉半圆，合起来是**一个圆孔**（像一只大眼睛），孔的内壁是**亮蓝色**。
> - **孔里的蓝核**：请在孔里画**一颗发光的蔚蓝色能量核**（亮蔚蓝 → 青白，**中间一格近白**），把孔填满大半，这就是它的「脸」，也是激光射出来的地方。**蔚蓝核 + 两块浅绿顶深蓝底的尖石**是它最好认的地方。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：待机，稍微 3/4 朝右**（附图 1、2、10a）：两块石头并排竖着，**圆孔正对着看得清清楚楚**（略微偏右），蓝核在孔里；左边的高尖石在画面左边，右边的矮圆石在画面右边、稍稍靠前。**比宽高很多**。
> - **B：同样的待机，更侧一点朝右**（附图 4、10b）：石头转过去一些，**左边高尖石挡住大半**，右边那块缩到右侧，**圆孔变成画面右边的一个竖椭圆**，蓝核从椭圆里露出来。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的苍蓝雕纹魔像（**同一个营地的大石像**，颜色最接近）、远古石甲虫（同一个系列的峡谷野怪）、斯卡纳（水晶）和泽拉斯（漂浮、发光的能量），**只看风格**。
> - **长相照金铲铲的模型**（附图 1、2、4、5、6、9 是模型的渲染；附图 3 是圆孔的特写，**孔的位置和边缘以附图 3 为准**；附图 7 是开火时，**只看它怎么往上一抬、往前一倾**；附图 8 是死亡，**只看两块石头怎么分开倒下**）。模型里孔是空的，**蓝核是要你加上的**。
> - **比例**：Q 版，**比模型矮胖一点**（模型很细长：高约是宽的 2.1 倍，你画成约 1.5–1.7 倍），**圆孔和蓝核放大**（孔约占两块石头总宽的一半，**蓝核至少 6×6 格**），两块石头的**分缝清楚**、尖顶和尖底都保留。
> - **画布用正方形 1536×1536**。**A：从最高点（左边尖顶）到最低点（底下的尖）约 374 px，也就是约 34 格**，宽约 20–24 格（最多 26 格）；**B：同样的格子大小**，约 32–34 格高，宽约 16–22 格（最多 24 格）。最低点在离画布底边约 146 px 的地方（附图 10a、10b 的灰线）。**附图 10a、10b 是按模型原比例渲染的，比你要画的瘦，只看位置、高度和最低点线，宽度以上面的格数为准。** 它在游戏里是**飘着的**，离地的高度后面我来调，这一步**底尖放在灰线上**就行。尖顶、尖底全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（两块石头中间的窄缝也用近黑分开）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。岩面画成**几块清楚的平面**（每块一亮一暗，像切面），不要碎点；浅绿顶和深蓝底的分界要清楚。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（激光、光弹、碎石都放到后面单独画）；**蓝核的光是它本来就有的，要画**，但核外面最多一圈 1 格的亮蓝内壁，**不要光晕散到石头外面**；不画地面，不画投影。
> - 交付：`outputs/sentry-picture/sentry-A.png`、`sentry-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/sentry-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/sentry_picture_done.zip`。

## 附图（在压缩包 `sentry_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sentry_34.png` | 金铲铲苍蓝哨戒的模型，待机，稍微 3/4 朝右 | **A** 的形状、颜色、**角度** |
| `refs/2_sentry_front.png` | 模型，正面 | 两块石头、中间的窄缝、**整个圆孔** |
| `refs/3_sentry_hole.png` | 圆孔的特写 | **孔的位置、边缘、亮蓝内壁**（孔里的蓝核要你加） |
| `refs/4_sentry_side.png` | 同样的待机，更侧一点 | **B** 的角度：孔变成右边的竖椭圆 |
| `refs/5_sentry_back.png` | 斜后方 | 背面的岩面和颜色 |
| `refs/6_sentry_top.png` | 从上往下看 | 两块石头的横截面、中间的缝 |
| `refs/7_sentry_attack.png` | 开火的一下 | **只看**它往上一抬、往前一倾 |
| `refs/8_sentry_death.png` | 死亡 | **只看**两块石头分开倒下 |
| `refs/9_sentry_profile.png` | 正侧面 | 石头有多薄（不要画成这个角度） |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上渲染的，只看位置和高度） | 画布上的位置、高度、最低点线（灰）；浅灰线 = 最高点；**宽度以格数为准** |
| `refs/10b_layout_B.png` | B 的大小示意（和 A 同一个比例） | 只看位置、高度和最低点线 |
| `style/11_style_sentinel.png` | 本系列的苍蓝雕纹魔像（8 倍放大，一格 = 一个像素） | **只看风格**：同一个营地的石像，**颜色最接近**（深蓝灰石头 + 浅绿石块 + 青蓝光） |
| `style/12_style_krug.png` | 本系列的远古石甲虫（8 倍） | **只看风格**：同一个系列的石头怪 |
| `style/13_style_skarner.png` | 斯卡纳（8 倍） | **只看风格**：水晶的切面怎么画 |
| `style/14_style_xerath.png` | 泽拉斯（8 倍） | **只看风格**：漂浮的身体、发光的能量核 |

## 提示词：`sentry-A.png` / `sentry-B.png`（同一段提示词，先画 A 再画 B）

十五张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fifteen attached images. Images 1-9 show ONE creature from a game: a PAIR OF TALL CRYSTAL SHARDS FLOATING side by side, with NO limbs and NO face - the whole creature is two rocks. The LEFT shard is TALLER with a POINTED FACETED TIP; the RIGHT shard is a little shorter with a BLUNT ROUNDED TOP; a narrow gap runs between them. The UPPER part of each shard is PALE SAGE / GREY-GREEN ROCK (3-4 shades with a few light ridges); the LOWER part is DARK NAVY BLUE / BLUE-VIOLET (3 shades), tapering down to a POINT at the bottom. A thin DARK RED-VIOLET edge runs along the inner side of each shard by the gap. A little above the middle the two shards each have a half-circle cut out, together making ONE ROUND HOLE like a big eye, its inner wall BRIGHT BLUE. INSIDE THE HOLE draw A GLOWING AZURE ENERGY CORE (bright azure to cyan-white, a near-white centre square) filling most of the hole - this core is its "face" and where its laser comes from; it is NOT in the model renders, ADD it. The azure core and the two pale-topped, dark-bottomed shards make it recognisable. (1 its idle at a slight 3/4 facing right - for picture A, the look and the ANGLE; 2 the same from the front: the two halves, the gap, the whole round hole; 3 the hole close-up: its position, its rims, the bright blue inner wall; 4 the same idle turned more side-on - for picture B, the hole becomes an upright oval at the right; 5 from behind; 6 from above: the two halves and the gap; 7 firing: ONLY how it lifts up and tips forward; 8 dying: ONLY how the two halves split and fall; 9 true side: how thin the shards are - do NOT draw this angle.) Images 10a-10b are layout guides rendered at the MODEL's proportions: where the figure goes on the canvas, how tall, the grey line is its lowest point, the light line the highest point - the model is thinner than you should draw, so take the WIDTH from the square counts below, not from the guide. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 (the last four) are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a big stone golem from the SAME camp, the closest colours: dark blue-grey stone, pale sage boulders, cyan glow; 12 a stone beast of this same series; 13 a crystal creature: how crystal facets are drawn; 14 a floating figure with a glowing energy core).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the pointed tip, the bottom points); its lowest point on one line about 146 px above the bottom edge (the grey line of images 10a-10b), centred where the guide shows the figure. No ground under it.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure, and the narrow gap between the two shards near-black too; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; the rock as a few CLEAR FLAT FACETS, each with one light face and one dark face, never noisy dots; a clear border between the pale sage top and the dark navy bottom; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. The azure glow of its core is part of its body - draw it - but at most one square of bright blue inner wall around the core, NO glow halo outside the rocks, NO effects (no laser, no bolt, no flying shards), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi - a little SHORTER AND STOUTER than the model (the model is about 2.1 times as tall as wide; draw it about 1.5-1.7 times); the ROUND HOLE and the CORE ENLARGED: the hole about half the width of the pair, THE CORE AT LEAST 6x6 SQUARES with a near-white centre; the gap between the shards clear; keep the pointed tip of the left shard, the blunt top of the right one and the pointed bottoms. THE COLOURS: upper rock pale sage / grey-green in 3-4 with light ridges; lower rock dark navy / blue-violet in 3; a thin dark red-violet edge by the gap; the hole's inner wall bright blue; the core azure to cyan-white with a near-white centre; outline near-black.
PICTURE A (sentry-A.png): IDLE, a slight 3/4 view facing right (images 1, 2, 3 and 10a): the two shards standing side by side, the ROUND HOLE facing the viewer, fully readable (slightly to the right), the core inside it; the tall pointed shard at image left, the shorter rounded shard at image right and slightly in front. MUCH TALLER THAN WIDE. About 374 px (about 34 squares) from the highest point (the left tip) to the lowest point (the bottom points), about 20-24 squares wide (never more than 26).
PICTURE B (sentry-B.png): THE SAME IDLE MORE SIDE-ON, facing right (images 4 and 10b): turned further, the tall pointed shard covering most of the view, the shorter shard pushed to the right edge, the hole now an UPRIGHT OVAL at the image right with the core showing through it. The SAME square size as A: about 32-34 squares from the highest point to the lowest, about 16-22 squares wide (never more than 24); its lowest point on the grey line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尖顶、尖底完整，不出画。
- **A**：约 374 px（约 34 格）高、约 20–24 格宽，稍微 3/4 朝右，**两块尖石并排、左高尖右矮圆、圆孔正对着看得清、蓝核在孔里**；最低点在灰线上。
- **B**：同样的格子，约 32–34 格高、约 16–22 格宽，**更侧一点，左边高尖石挡住大半、孔变成右边的竖椭圆、蓝核露出来**；最低点在灰线上。
- 两张都要：**浅灰绿的上半截 + 深海军蓝的下半截**（分界清楚、切面清楚）；**中间的窄缝 + 暗红紫细边**；**圆孔 + 亮蓝内壁**；**蔚蓝能量核（至少 6×6 格、中间一格近白）**；尖顶和尖底。
- 没有特效，核外面没有散到石头外的光晕。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/sentry-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sentry_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有苍蓝哨戒自己的动作（待机飘动、开火时往上一抬、死亡时两块分开倒下，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：**左边的高尖石**、**右边的矮圆石**（技能里**两块会分开再合上、张到最大**）、**中间的蓝核**（**激光和光弹都从这里射出去**，要能单独变亮变大）。

| 动作 | 用在 |
|---|---|
| 待机 | 选 A：稍微 3/4；选 B：更侧一点。整只飘在空中，上下轻轻浮动 |
| 移动 | 整只往前飘，稍稍前倾，不走路 |
| 普攻 | 往上一抬、往前一倾，蓝核里射出一颗小蓝光弹 |
| 技能 | 蓝核对准敌人引导一道持续的蓝色激光（蔚蓝激光）；两块石头一分一合、往后闪开（裂石跃迁）；两块石头张到最大、蓝核射出一道粗光柱从左扫到右（棱镜扫射） |
| 死亡 | 两块石头分开倒下，蓝核熄灭 |
