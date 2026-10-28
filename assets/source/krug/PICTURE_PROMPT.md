# 远古石甲虫（金铲铲之战 · 第 18 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 远古石甲虫是金铲铲之战第 18 赛季的三费卡（峡谷野怪 / 斗士），峡谷里的石甲虫营地的老大：**一只驼着背、四肢着地的岩石巨兽**。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **背上的大石头**：整个背部是**一块巨大的、棱角分明的砂岩巨石**，往上隆起、尖顶微微朝后（看附图 1、5、7），颜色是**浅土黄 / 卡其 / 灰绿的砂岩色**，上面有**几道发光的橙金色裂缝**（像岩浆在石缝里亮着，一道从顶上斜着裂到前面）。巨石占了身体的一大半。
> - **身体和四肢**：巨石下面是**深灰褐、带一点紫的石头身体**；**两条粗壮的前臂**像两块叠起来的大石头，末端是**大石拳 / 石爪**（几根短而钝的石趾）；**两条短粗的后腿**，脚掌宽、有石趾；关节处的石块之间露出一点**橙金色的光缝**。**肚子**上是一排**横着的深褐色甲板**，甲板之间是橙金色的缝（看附图 8）。
> - **头和脸**：头**很小，长在身体最前面、靠下**，几乎缩在巨石下面（看附图 1、3、6）：一个**深紫褐色的硬壳头盔一样的脸**，正中有一道竖的凸棱、带浅色高光；头两侧各一只**发光的琥珀橙色眼睛**（眼窝是一圈橙色的光）；脸上方长着**两只弯弯的深褐色大钳子（像甲虫的大颚）**，朝上、朝里弯。没有嘴巴、没有毛发。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：伏地待机**（金铲铲原样待机，附图 1、2、10a）：**3/4 朝右**，**四肢着地、驼着背**，巨石背高高隆起，头和钳子在右下方、朝右前方，两只前臂撑在地上。
> - **B：人立而起**（他攻击时抬起身子的那一下，附图 4、10b）：**3/4 朝右**，**后腿蹲着撑地、上身立起来**，两只大石臂抬在身前准备砸下去，头抬起来、两只钳子张开朝上，巨石背在身后。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的加里奥（石像）、斯卡纳（水晶蝎子，四脚野兽）、拉莫斯（背着甲壳）和可酷伯（本系列的金铲铲英雄），**只看风格**。
> - **长相照金铲铲的模型**（附图 1、2、4、5、7、8 是模型的渲染；附图 3、6 是头部特写，**眼睛、钳子、脸上的硬壳以附图 3、6 为准**；附图 7 是侧面，看清**巨石往后伸多远、四条腿在哪**；附图 8 是立起来的正面，看清**肚子上的甲板和橙色光缝**）。
> - **比例**：Q 版、圆墩墩的大块头，**头小、巨石大**——这只怪物本来就是头小，不要把头画大；但**脸（眼睛、钳子）一定要清楚**，是全图最好认的地方。
> - **脸要清楚**（附图 3、6 特写）：硬壳脸 3 档深紫褐，中间竖棱 1 列浅色高光；**两只眼睛**各至少 2×2 格，琥珀橙色、中间一格浅黄色的亮点（发光就用更亮的一档平涂，不要柔光）；**两只钳子**各至少 2 格粗，深褐 3 档，轮廓清楚、和巨石分得开。
> - **画布用正方形 1536×1536**。**A：从巨石顶到脚底约 550 px，也就是约 50 格**，宽约 37–46 格（最多 54 格）；**B：同样的身体大小，因为立起来了，从最高点到脚底约 594 px，也就是约 54 格**，宽约 52–58 格（最多 62 格）。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。巨石、钳子、石臂全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。**巨石的棱面**用 3–4 档成块的平面（亮面朝左上），**发光的裂缝**用 2–3 档（深橙 / 橙金 / 浅黄）**连成线的成块裂纹**，不要碎点、不要柔光。
> - 不画任何技能特效（滚动的尘土、护盾、碎石、冲击波都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/krug-picture/krug-A.png`、`krug-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/krug-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/krug_picture_done.zip`。

## 附图（在压缩包 `krug_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_krug_34.png` | 金铲铲远古石甲虫的模型，待机（伏地），3/4 朝右 | **A** 的姿势、颜色、**角度** |
| `refs/2_krug_front.png` | 模型，待机，正面 | 巨石的形状、前臂、后腿、头在哪 |
| `refs/3_krug_head.png` | 头部特写（立起来时，3/4） | **眼睛、钳子、硬壳脸** |
| `refs/4_krug_rear.png` | 模型，人立而起，3/4 朝右 | **B** 的姿势 |
| `refs/5_krug_back.png` | 背后 | 巨石的背面和棱面 |
| `refs/6_krug_head_front.png` | 头部特写（立起来，正面） | **脸**：竖棱、两只眼睛、两只钳子怎么排 |
| `refs/7_krug_side.png` | 侧面 | 巨石往后伸多远、四条腿的位置 |
| `refs/8_krug_belly.png` | 立起来的正面 | **肚子上的甲板和橙色光缝**、石臂 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 巨石顶 |
| `refs/10b_layout_B.png` | B 的大小示意 | 只看大小和地面线 |
| `style/11_style_galio.png` | 本包的加里奥（石像），8 倍放大，一格 = 一个像素 | **只看风格**：石头的大块头怎么画 |
| `style/12_style_skarner.png` | 本包的斯卡纳（四脚野兽，8 倍） | **只看风格**：四脚着地的怪物怎么画 |
| `style/13_style_rammus.png` | 本包的拉莫斯（8 倍） | **只看风格**：背上的大甲壳怎么画 |
| `style/14_style_kobuko.png` | 本系列的可酷伯（8 倍） | **只看风格**：金铲铲英雄在格子上的样子 |

## 提示词：`krug-A.png` / `krug-B.png`（同一段提示词，先画 A 再画 B）

十四张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fourteen attached images. Images 1-8 show ONE creature from a game: a big hunched STONE BEAST that walks on all fours. Its whole back is a HUGE ANGULAR SANDSTONE BOULDER rising high, the peak leaning a little backwards, pale khaki / sand / grey-green stone in flat facets, split by a few GLOWING ORANGE-GOLD CRACKS (like lava shining in the seams, one running diagonally from the top down to the front); the boulder is more than half of the body. Under it a DARK GREY-BROWN, slightly violet STONE BODY: two THICK FOREARMS like stacked boulders ending in BIG STONE FISTS with a few short blunt stone toes; two SHORT THICK HIND LEGS with wide stone feet; thin orange-gold light showing in the joints between the stones; a BELLY of horizontal dark brown armour plates with orange-gold seams between them. A SMALL HEAD low at the very front, almost tucked under the boulder: a DARK VIOLET-BROWN HARD SHELL face like a helmet with one vertical ridge down its middle (a pale highlight on it), a GLOWING AMBER-ORANGE EYE on each side of the head (an orange glowing ring round each), and above the face TWO CURVED DARK BROWN PINCERS (like a beetle's mandibles) curling up and inwards. No mouth, no hair. (1 his idle, hunched on all fours, 3/4 view facing right - for picture A, the look and the ANGLE; 2 the same from the front: the boulder, the forearms, the hind legs, where the head sits; 3 his head close-up, reared up, 3/4: the EYES, the PINCERS, the shell face; 4 reared up on his hind legs, the stone forearms raised in front of him - for picture B; 5 from behind: the boulder's back facets; 6 his head from the front, reared: how the ridge, the two eyes and the two pincers sit; 7 from the side: how far the boulder overhangs, where the four limbs are; 8 reared, from the front: the BELLY PLATES and the orange seams, the forearms.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the top of the boulder. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a stone statue, 12 a four-legged beast, 13 a hero with a big shell on his back, 14 a hero of this same series).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the boulder, the pincers, the forearms); his soles level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; the BOULDER as big flat facets in 3-4 shades (the light side to the upper left); the GLOWING CRACKS as connected solid crack lines in 2-3 shades (deep orange, orange-gold, pale yellow), never noisy dots; GLOW drawn only as a brighter flat shade (the cracks, the eyes, the seams), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO effects (no dust, no shield, no flying rocks, no shockwave); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi and chunky - a round, heavy, compact body; the head stays SMALL (this creature has a small head under a huge boulder: do not enlarge it) but the FACE IS THE CLEAREST PART of the picture. FACE CLEAR: the shell face in 3 dark violet-brown shades with a 1-square pale highlight down its ridge; TWO EYES, each at least 2x2 squares, amber-orange with one pale yellow square in the middle; TWO PINCERS, each at least 2 squares thick, dark brown in 3 shades, outlined and clearly apart from the boulder. THE COLOURS: boulder pale khaki / sand / grey-green in 4; cracks deep orange / orange-gold / pale yellow; body, forearms and legs dark grey-brown with a violet tint in 3-4; belly plates dark brown in 3 with orange-gold seams; head shell dark violet-brown in 3; eyes amber-orange with pale yellow; pincers dark brown in 3.
PICTURE A (krug-A.png): HUNCHED ON ALL FOURS, 3/4 view facing right (images 1, 2, 3 and 10a): the boulder back high, its peak leaning back; the small head and the pincers low at the front right, looking to the front-right; both stone forearms planted on the ground in front, the hind legs under the back. About 550 px (about 50 squares) from the top of the boulder to his soles, about 37-46 squares wide (never more than 54).
PICTURE B (krug-B.png): REARED UP, 3/4 view facing right (images 4, 6, 8 and 10b): crouched on his hind legs, the upper body raised upright; both big stone forearms lifted in front of his chest, ready to slam down; the head raised, the two pincers spread upwards; the boulder behind him; the belly plates showing. The SAME body size as A; about 594 px (about 54 squares) from the highest point to his soles, about 52-58 squares wide (never more than 62); his soles on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，巨石、钳子、石臂完整，不出画。
- **A**：约 550 px（约 50 格），3/4 朝右，**四肢着地、驼背**，巨石背高高隆起，小头和钳子在右前下方；脚底在地面线上。
- **B**：约 594 px（约 54 格），和 A 一样大的身体，**后腿蹲着、上身立起、两只石臂抬在身前、钳子张开朝上**；脚底在地面线上。
- 两张都要：**浅土黄 / 灰绿的砂岩巨石背 + 发光的橙金裂缝**；**深灰褐带紫的石头身体 + 粗石臂石拳 + 短粗后腿**；**肚子上的深褐甲板和橙金缝**；**小小的深紫褐硬壳脸 + 两只琥珀橙发光眼睛 + 两只弯钳子**。
- 没有特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/krug-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/krug_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有远古石甲虫自己的动作（我已经按动作片段渲染出来了，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸和两只钳子用在所有帧、两条石臂（砸地、撑地、抬起）、巨石背（滚动时缩成一个大石球）、两条后腿（奔跑、蹲下、跳起、落地）。

| 动作 | 金铲铲里怎么做 / 我们的技能 |
|---|---|
| 待机 | 选 A：伏地喘气；选 B：人立而起 |
| 移动 | 四肢着地、沉重地跑（金铲铲原样） |
| 普攻「岩拳砸地」 | 立起身子，两只石臂砸下去（金铲铲原样） |
| 被动「碎岩重生」 | 第一次阵亡时碎裂，片刻后以小石甲虫的样子重新站起来，嘲讽周围的敌人 |
| 技能1「岩之摇滚」 | 身上加一层石头（额外生命），缩成一个大石球滚向目标，撞上去造成伤害并击退（金铲铲的滚动登场动作） |
| 技能2「坚岩外壳」 | 缩进巨石里，护甲魔抗大增，嘲讽周围的敌人 |
| 大招「远古崩落」 | 跃起砸进敌群：周围的敌人被击飞，天上落下碎石 |
| 死亡 | 沉下去，背上的巨石裂开散落（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/krug/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和加里奥、斯卡纳、拉莫斯、可酷伯按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_krug_picture.py`（模型在 Riot 客户端的 `TFTSet18.wad.client`，`tft18_krug.skn/.skl`，46 个关节；七段动作在 `data/characters/da_krug18/animations/skin0.bin`，只有路径哈希，`CLIPS` 里按内容命名；客户端里没有他的原画，所以用头部特写代替）。
