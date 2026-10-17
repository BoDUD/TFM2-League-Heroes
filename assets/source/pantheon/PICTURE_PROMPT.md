# 潘森（不屈之枪）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 潘森是一个**金盔金盾的斯巴达式战士**：头戴遮住整张脸的金色头盔，头盔顶上竖着一道高高的弯月形冠饰；光着肌肉结实的古铜色上身，肩上披着一条深蓝色的披风；近侧手里拿一支金色长矛，远侧手臂挎着一面大圆盾。请 Codex 用同一段提示词画**两版**全身像素风原图，我从中挑一张：两版是同一个潘森，长相、衣服、颜色、格子大小都一样，只有姿势不同。
> - **A**：英雄联盟里的待机（附图 1）。长矛低低地握在近侧手里，矛头朝前下方；远侧手臂挎着圆盾；披风向后飘。
> - **B**：Q 投掷前的蓄力（附图 6）。近侧手臂把长矛高高举过肩头，矛头朝前，准备掷出；圆盾举在身前；两腿分开站稳。
>
> 选定一张后，第 1 步再按它做游戏尺寸的造型。这一版每个游戏像素约 **1.8 格**，读回后再降到 PPU 1.5。附图 9–12 是本包里的加里奥、布隆、盖伦、伊莉丝，其中伊莉丝也是 1.8 格。你画的原图会按格子直接读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：人形战士，**头稍大一点**（连头盔约占身高的四分之一，不算冠饰），肩宽、胸厚、胳膊粗，腿结实；不要画成大头小身子的娃娃，也不要写实的细长比例。
> - **头盔**（附图 3 特写）：
>   - **金色的全脸头盔**，前面一道**深色的 T 形眼缝**，看不到脸（眼缝里是阴影，照原版不画发光的眼睛），护颊一直包到下巴。
>   - 头盔顶上竖着一道**高高的金色弯月形冠饰**（像一片向上、向后弯的鳍），两侧还有两根短的尖角。
>   - 金色要分出亮金、金、暗金、古铜几档，不要糊成一片黄。
> - **身体**：
>   - **古铜色的皮肤**，胸肌、腹肌、三角肌、二头肌分得清楚，胸口有几道浅浅的疤。
>   - 肩上披一条**深宝蓝色的披风 / 围巾**，绕过脖子，在身后飘起来，末端颜色更深（近海军蓝）。
>   - 一条**棕色皮带斜挎过胸口**。
>   - 近侧（拿矛的）手臂套着**金色的护肩和护臂**，远侧前臂也有**金色护腕**。
> - **下身**（附图 1、2、4）：
>   - 腰上一条**深红色的麻绳腰带**，压在棕色皮腰带上，正中一个**金色的圆环徽章**。
>   - 腰前垂一块**深蓝色的布帘**，上面有**金色的弯月 + 圆环纹章**；两侧是棕色的皮甲片。
>   - 两条小腿套着**金色的护胫**（膝盖到脚踝），脚上穿**露脚趾的皮凉鞋**。
> - **长矛**（附图 1、6）：**金色的矛杆**，靠近矛头的握把缠着**深红色的布条**；**矛头又大又华丽**：宽阔的金色叶形刃，根部一个金环，环里嵌着一颗**淡蓝色发光的宝石**；矛尾一个小小的金色尖刺。
> - **圆盾**（附图 1、2、6）：**很大的金色圆盾**，一层层的金边，盾面中间有弯月 / 太阳纹章。附图 1 里盾几乎是侧对镜头的，请**稍微转过来一点**，让圆形的盾面露出一块。
> - **姿势**：3/4 正面朝右（头盔朝右前方）。**近侧的手臂（拿矛的那只）和腿在画面左边、颜色亮；远侧的（挎盾的）在画面右边、稍暗**，两只脚底落在同一条地面线上。
> - **画布用正方形 1536×1536**：**从头盔顶（不算冠饰）到脚底约 836 px，也就是约 76 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。长矛、盾、披风、冠饰全在画面里，B 版举起的长矛也不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金色（头盔、护甲、长矛、盾）、古铜皮肤、深蓝披风、深红绳子要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。宝石的淡蓝只用在矛头的宝石上。
> - 不画任何特效（飞出去的长矛、彗星、盾上的光、星光都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/pantheon-picture/pantheon-A.png`、`pantheon-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/pantheon-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/pantheon_picture_done.zip`。

## 附图（在压缩包 `pantheon_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_pantheon_idle.png` | 英雄联盟原版潘森的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_pantheon_frontal.png` | 同一帧，正面 | 头盔、披风、斜挎皮带、绳腰带、蓝布帘、护胫、凉鞋、矛头 |
| `refs/3_pantheon_head.png` | 头盔特写 | 弯月冠饰、两侧尖角、T 形眼缝、护颊 |
| `refs/4_pantheon_back.png` | 同一帧的背后 | 披风、背后的皮甲片、盾的背面 |
| `refs/5_pantheon_splash.png` | 官方加载画面 | 气质（坚毅、伤痕累累的老兵） |
| `refs/6_pantheon_throw.png` | Q 投掷前的蓄力，长矛举过肩头 | B 的姿势、盾举在身前的样子 |
| `refs/7_pantheon_throw_side.png` | 同一帧，接近侧面 | B 里长矛怎么握 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上他的位置、大小、脚底线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（同一比例） | 画布上他的位置、大小、脚底线（灰） |
| `style/9_style_galio.png` | 本包的加里奥（金石色的大块头），8 倍放大，一格 = 一个像素 | **只看风格**：像素粗细、描边、金色怎么分档 |
| `style/10_style_braum.png` | 本包的布隆（8 倍） | **只看风格**（壮汉、大盾） |
| `style/11_style_garen.png` | 本包的盖伦（8 倍） | **只看风格**（金甲战士、头身比） |
| `style/12_style_elise.png` | 本包的伊莉丝（8 倍，和这张一样每游戏像素 1.8 格） | **只看风格**：这个密度下格子有多细 |

## 提示词：`pantheon-A.png` / `pantheon-B.png`（同一段提示词，只换最后一句姿势）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-7 are 3D renders and art of a character from the game: a SPARTAN-STYLE WARRIOR in a full-face GOLDEN HELMET with a tall crescent crest, a bare muscular bronze-skinned torso, a deep blue cape, a golden spear in his near hand and a big round golden shield on his far arm (1 his idle in 3/4 view facing right - the look, the ANGLE and pose A of this picture; 2 the same from the front: the helmet, the cape, the chest strap, the rope belt, the blue loincloth with its emblem, the greaves, the sandals, the spearhead; 3 the helmet close-up: the crescent crest, the side horns, the T-shaped eye slit, the cheek guards; 4 the same from behind: the cape, the leather tassets, the back of the shield; 5 the official illustration: his mood, a stern scarred veteran; 6 his spear-throw wind-up, the spear raised over his shoulder - pose B; 7 the same from nearer the side: how he grips the raised spear). Images 8a and 8b are the layout guides of A and B: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 9-12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how gold is split into clear shades (9, 11). Image 12 has the same square density this picture needs.
Create ONE pixel-art picture of him, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). He is about 836 px (about 76 squares) from the top of his helmet (not counting the crest) to the soles of his feet, the soles about 146 px above the bottom edge (the grey line of images 8a / 8b); the spear, the shield, the cape and the crest whole inside the picture (the raised spear of pose B too), comfortable transparent margins, nothing cut off; both soles level on one ground line.
PROPORTIONS: a human warrior with a slightly big head - the helmet about a quarter of his height (the crest not counted) - broad shoulders, a deep chest, thick arms, sturdy legs; not a big-headed doll, not slender realistic proportions.
THE HELMET: a FULL-FACE GOLDEN HELMET; a dark T-SHAPED EYE SLIT in front, the face unseen (only shadow in the slit, no glowing eyes, as in the game), cheek guards reaching down to the chin; on top a TALL GOLDEN CRESCENT CREST curving up and back like a fin, and two short horn points at the sides. The gold in clear shades: bright gold highlights, gold, dark gold, bronze-brown in the deepest shadow - never one flat yellow.
THE BODY: BRONZE-TAN skin with clearly separated muscle masses (chest, abs, deltoids, biceps), a few faint scars on the chest; a DEEP ROYAL-BLUE CAPE / scarf wrapped round the neck and shoulders, flying out behind him, its ends darker navy; a BROWN LEATHER STRAP across the chest; on the near (spear) arm a GOLDEN PAULDRON and a golden arm guard, a GOLDEN BRACER on the far forearm.
THE LOWER BODY: a DARK RED TWISTED ROPE BELT over a brown leather belt with a round GOLDEN RING BUCKLE in the middle; a DEEP BLUE CLOTH PANEL hanging in front with a golden crescent-and-ring emblem; brown leather tassets at the sides; GOLDEN GREAVES from the knees to the ankles; open-toed leather SANDALS, the toes showing.
THE SPEAR in his near hand: a GOLDEN shaft, a DARK RED cloth-wrapped grip near the head; a BIG ORNATE SPEARHEAD: a broad golden leaf-shaped blade with a golden ring at its base holding a PALE BLUE GLOWING GEM (colour only, no glow effect); a small golden spike at the butt end.
THE SHIELD on his far arm: a BIG ROUND GOLDEN SHIELD with layered golden rims and a crescent / sun emblem in the middle. In image 1 it is seen nearly edge-on: turn it a little toward us so a slice of its round face shows.
THE VIEW: 3/4 view facing right (the helmet to the front-right): the NEAR arm (holding the spear) and leg on the image LEFT in full tone, the FAR ones (with the shield) on the image RIGHT a step darker; both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure, the spear and the shield; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the gold (helmet, armour, spear, shield) in bright gold / gold / dark gold / bronze, the skin in warm bronze-tan shades, the cape deep royal blue to navy, the rope belt and the spear grip dark red, the straps and tassets brown; the pale blue used ONLY for the spearhead's gem; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no flying spear, no comet, no starlight, no shield glow), no background, no ground, no shadow, no text, no frame, no other characters.
POSE A (pantheon-A.png): his idle (image 1) - standing with the feet apart, the spear held LOW in the near hand with the spearhead pointing forward and down (image lower right), the round shield on the far arm, the cape flying back to the image left.
POSE B (pantheon-B.png): his spear-throw wind-up (image 6) - the near arm raising the spear HIGH over his shoulder, the spearhead pointing forward (image right) and the butt reaching back (image left), the shield held out before him on the far arm, the legs apart and planted.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，长矛、盾、披风、冠饰完整，不出画。
- 比例：头稍大（连头盔约占身高四分之一），肩宽胸厚，不是大头娃娃，也不是写实的细长身材。
- 头盔：全脸金盔 + **深色 T 形眼缝**（不画发光眼睛）+ **高高的弯月冠饰** + 两侧短尖角；金色分出几档。
- 身体：古铜皮肤、肌肉块清楚、胸口浅疤；深宝蓝披风绕肩、向后飘；斜挎皮带；近侧手臂金护肩和护臂，远侧金护腕。
- 下身：深红麻绳腰带 + 金色圆环扣；深蓝布帘 + 金色纹章；棕色皮甲片；金护胫；露脚趾的凉鞋。
- 长矛：金杆、深红握把、华丽的金色矛头 + **淡蓝宝石**（这个颜色只用在这里）、矛尾小尖刺。
- 圆盾：大金圆盾，稍微转过来露出盾面和纹章。
- 从头盔顶（不算冠饰）到脚底约 836 px（约 76 格）；近侧手脚在画面左边、颜色亮，远侧在右边、稍暗；脚底在同一条水平线上；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- A、B 两版都画完后，最后写 `outputs/pantheon-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/pantheon_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两版都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/pantheon/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_<hero>_hd.py` 的做法），和同位置英雄（盖伦、诺手、加里奥、布隆、蒙多）按游戏里的大小并排，给用户挑 A / B；PPU 已定 1.5，再出 2–3 个大小（约 40 / 42 / 44 行）的对比让用户定。
- 选定后写第 2 步动作包：长矛和圆盾是刚体部件，动作里只平移和整块转直角，不变形；跑步照英雄联盟（Pantheon_Run_base）；普攻 = 长矛突刺（Pantheon_attack1-3）；Q = 近戳（spell1_hit）和举矛投掷（spell1_longhit）；W = 举盾跃起砸下（spell2 / spell2_hit）；E = 举盾向前、矛从盾边连刺（spell3_loop_nomove_0）+ 盾击（spell3_hit）；R = 跪地蓄力（spell4）+ 跃起（spell4_leap）+ 落地（spell4_hit）；死亡（Pantheon_Death）。
