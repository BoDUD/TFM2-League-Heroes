# 芮尔（镕铁少女）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 芮尔是一个**骑着铁甲战马的少女骑士**：金色蓬松的短发（像炸开的金色火焰）、深棕色皮肤、坚毅的脸；平时穿深蓝紫色的紧身战衣，骑在一匹**全身由橄榄绿 / 暗铜绿铁甲拼成的战马**上，手里一支**很长的金色骑枪**（枪身一道道发光的金色裂纹）。她会把马「化」成铁甲穿在自己身上下马作战。请 Codex 画**两张**全身像素风原图，是同一个芮尔、同一个比例、同一种格子大小：
> - **A：骑马**（英雄联盟里的待机，附图 1）。她骑在铁甲战马上，骑枪平端朝前（画面右边）。
> - **B：下马披甲**（附图 6）。她站在地上，身上穿着马变成的厚重铁甲（同样的橄榄绿铁甲），骑枪握在手里斜指地面。**和 A 同一个比例**：她本人的头、身体大小和 A 里一样（附图 8b 是按同一比例摆好的位置）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（PPU 1.5）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的潘森、卡特琳娜、卡莉丝塔、赫卡里姆（半人马，看铁甲马身在游戏尺寸下怎么画），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：她是年轻的少女骑士，**头稍大一点**（约占她本人身高的四分之一），不要大头娃娃，也不要写实的细长比例。马要**粗壮、厚重**，一块块铁甲板的形状看得清。
> - **头**（附图 4 特写）：**金色蓬松的短发**，一绺绺向后、向上翘起，像金色的火焰；金色分出亮金、金、暗金、棕金几档，不要糊成一片黄。**深棕色皮肤**，坚毅的表情；**两只眼睛一样大、一样高**，眼白清楚，深色瞳孔。
> - **A 骑马的她**：深蓝紫色的紧身战衣，胸口和肩上少量深色护甲，红棕色的皮带 / 护腕；坐在马鞍上，近侧的腿垂在马身侧。
> - **B 披甲的她**：肩、胸、前臂、腿上都是**马变成的橄榄绿厚铁甲**，下身是一圈长长的铁甲裙板，深色的铁靴；甲片边缘有亮一点的高光，甲板之间露出深色的缝。
> - **铁甲战马**（只在 A）：橄榄绿 / 暗铜绿的一块块厚重铁甲拼成，马头是尖尖的铁盔，马腿是粗粗的铁柱、马蹄是方方的铁块，马尾是几片向后翘的铁片；铁甲上有浅浅的金色裂纹。马是**侧身朝右**、四条腿都着地。
> - **骑枪**：很长的锥形骑枪，枪身**金色、带一道道发亮的黄色裂纹**，握手处有一个铁护手。A 里平端朝右前方；B 里握在她手里、枪尖斜指地面。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。A 的四只马蹄、B 的两只脚底都落在同一条地面线上。
> - **画布用正方形 1536×1536**：A **从她的头发顶到马蹄底约 792 px，也就是约 72 格**，蹄底在离画布底边约 146 px 的地方（附图 8a 的灰线）；B 按附图 8b 的大小和位置。她、马、整支骑枪都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金色（头发、骑枪）、橄榄绿铁甲、深蓝紫战衣、深棕皮肤要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。铁甲要有**亮边和高光**（不然在游戏里会糊成一团深绿）。
> - 不画任何特效（磁力光、冲击波、护盾、尘土都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/rell-picture/rell-A.png`、`rell-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/rell-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/rell_picture_done.zip`。

## 附图（在压缩包 `rell_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_rell_mounted.png` | 英雄联盟原版芮尔骑马待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_rell_mounted_front.png` | 同一帧，正面 | 马头铁盔、马胸的铁甲、她坐的样子 |
| `refs/3_rell_mounted_back.png` | 同一帧，背后 | 马尾铁片、马背和马鞍 |
| `refs/4_rell_head.png` | 头部特写 | 金色蓬发、深棕皮肤、脸 |
| `refs/5_rell_splash.png` | 官方加载画面 | 气质（坚毅、厚重的铁骑） |
| `refs/6_rell_dismounted.png` | 下马披甲的待机，3/4 朝右 | B 的姿势、铁甲怎么穿在她身上 |
| `refs/7_rell_dismounted_front.png` | 下马披甲，正面 | 铁甲的肩、胸、裙板、铁靴 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（和 A 同一比例） | 画布上的位置、大小、地面线（灰） |
| `style/10_style_pantheon.png` | 本包的潘森，8 倍放大，一格 = 一个像素（PPU 1.5，和芮尔一样） | **只看风格**：重甲在这个密度下怎么分档、怎么留亮边 |
| `style/11_style_katarina.png` | 本包的卡特琳娜（8 倍，PPU 1.5） | **只看风格**：女英雄的脸和头发 |
| `style/12_style_kalista.png` | 本包的卡莉丝塔（8 倍） | **只看风格** |
| `style/13_style_hecarim.png` | 本包的赫卡里姆（8 倍，半人马） | **只看风格**：铁甲马身、马腿在游戏尺寸下的画法 |

## 提示词：`rell-A.png` / `rell-B.png`（同一段提示词，只换最后一句姿势）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-7 are 3D renders and art of a character from the game: a YOUNG IRON KNIGHT WOMAN with wild spiky GOLDEN hair like golden flames and dark brown skin, who rides a heavy WAR HORSE MADE OF OLIVE-GREEN IRON ARMOUR PLATES and carries a VERY LONG GOLDEN LANCE with glowing yellow cracks; she can melt the horse into heavy armour that she wears on foot (1 mounted, her idle in 3/4 view facing right - the look, the ANGLE, pose A; 2 the same from the front: the horse's iron helm, its chest plates, how she sits; 3 the same from behind: the iron tail plates, the saddle; 4 the head close-up: the golden flame-like hair, the dark brown skin, the face; 5 the official illustration: her mood, a heavy iron rider; 6 dismounted, her idle on foot wearing the horse as olive-green armour - pose B; 7 the same from the front: the armoured shoulders, chest, long plated skirt and iron boots). Images 8a and 8b are the layout guides of A and B: where she goes on the canvas and how big, the grey line is the ground; B is at the SAME SCALE as A. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, lit edges on heavy armour (10), how a face and hair read at this size (11), how an armoured horse body and legs read at game size (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). In A she and the horse are about 792 px (about 72 squares) from the top of her hair to the bottom of the hooves, the hooves about 146 px above the bottom edge (the grey line of image 8a); in B she stands at the size and place of image 8b (her own head and body the same size as in A). Everything whole inside the picture - her, the horse, the whole lance - with comfortable transparent margins, nothing cut off; all hooves / both soles level on one ground line.
PROPORTIONS: a young woman knight with a slightly big head - the head about a quarter of her own height - not a big-headed baby doll, not slender realistic proportions. The horse STOCKY and HEAVY, its separate thick armour plates clearly readable.
THE HEAD: WILD SPIKY GOLDEN HAIR swept back and up in flame-like locks; the gold in clear shades: bright gold highlights, gold, dark gold, brown-gold in the deepest shadow - never one flat yellow. DARK BROWN SKIN, a determined face, TWO EYES the same size on the same row with clear whites and dark pupils.
SHE, MOUNTED (A): a dark blue-violet bodysuit, a little dark armour on the chest and shoulders, red-brown straps and bracers; seated in the saddle, the near leg hanging down the horse's side.
SHE, DISMOUNTED (B): the horse's OLIVE-GREEN IRON ARMOUR worn on her shoulders, chest, forearms and legs, a long skirt of iron plates round her hips, dark iron boots; lit edges and highlights on the plate rims, dark seams between the plates.
THE IRON HORSE (A only): built of heavy OLIVE-GREEN / DARK BRONZE-GREEN iron plates; a pointed iron helm for the head, thick iron pillars for legs with blocky iron hooves, a few iron plates sweeping back as the tail; faint golden cracks in the iron. The horse side-on facing right, all four hooves on the ground.
THE LANCE: a very long tapering cone, GOLDEN with bright yellow glowing cracks along it, an iron hand guard at the grip. In A held level pointing forward (image right); in B held in her hand, the tip slanting down toward the ground.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image LEFT in full tone, the FAR ones on the image RIGHT a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the gold (hair, lance) in bright gold / gold / dark gold / brown-gold, the olive-green iron with LIT EDGES and highlights so it never turns into one dark green mass, the blue-violet bodysuit, the dark brown skin; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no magnetic glow, no shockwave, no shield, no dust), no background, no ground, no shadow, no text, no frame, no other characters.
POSE A (rell-A.png): mounted (image 1) - she sits on the iron horse standing still, the lance held level pointing forward to the image right, the horse's head and the lance tip toward the right.
POSE B (rell-B.png): dismounted (image 6) - she stands on the ground in the horse's heavy iron armour, feet a little apart, the lance in her near hand with its tip slanting down to the ground in front of her (image right); at the same scale as A (image 8b).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，她、马、整支骑枪都完整，不出画。
- 比例：年轻的少女骑士，头稍大（约占她本人身高的四分之一），不是大头娃娃；马粗壮厚重。
- 头：金色蓬松、像火焰一样翘起的短发；深棕皮肤；**两只一样大、一样高的眼睛**。
- A：深蓝紫战衣坐在橄榄绿铁甲战马上，骑枪平端朝右；马四蹄着地。B：同一个她穿着橄榄绿厚铁甲站着，骑枪斜指地面，**和 A 同一比例**。
- A 从头发顶到马蹄底约 792 px（约 72 格）；近侧在画面左边、颜色亮，远侧在右边、稍暗；蹄底 / 脚底在同一条水平线上；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；铁甲有亮边、不糊成一团；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- A、B 两张都画完后，最后写 `outputs/rell-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/rell_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/rell/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_pantheon_hd.py` 的做法），和辅助（布隆、阿利斯塔、蕾欧娜）、赫卡里姆、德莱厄斯按游戏里的大小并排，**宽度和高度都比**（骑马的她很宽），给用户定大小；PPU 1.5。
- 第 1 步造型包：A（骑马）和 B（下马披甲）都按游戏格子重画；骑枪单独看清楚。
- 第 2 步动作：主包 = 骑马的待机 / 跑（Run_Slow、gallop）/ 普攻（Auto_Attack1）/ Q（Spell1）/ W 轰落（Rell_Spell2_Dismount：马化成铁甲、她砸下来）/ W 上马冲锋（Spell2_Flip）/ E（Spell3_activation）/ R（Rell_Mounted_Spell4_Running 或 Spell4）/ 受击 / 死亡；附加包 = 下马形态的待机 / 走（Biped_Walk）/ 普攻（Attack1_Biped）/ Q（Biped_Spell1）/ 受击 / 死亡。
