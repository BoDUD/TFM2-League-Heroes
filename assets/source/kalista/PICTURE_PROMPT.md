# 卡莉斯塔（复仇之矛）：先画像素风原图（第 0 步，给 Codex 的提示词）

> 卡莉斯塔是一个**复仇的幽灵女战士**：青绿色发光的幽魂身体，穿着破旧的黑色铠甲，手里一支长长的黑色长矛。这一步请 Codex 画**两张**全身像素风原图：**A、B**（同一个人、同样的长相衣服，只差姿势）。用户挑一张，之后第 1 步再按选中的画造型。这一版每个游戏像素约 **1.8 格**（附图 10、11 是本包同样密度的伊莉丝、弗拉基米尔；12–14 是密度稍低的奈德丽、加里奥、泽丽）：像素块清楚、整齐、大小一致，描边约 **2 格**，身材**偏 Q 版**。你画的原图会直接按格子读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **头**（附图 3 特写）：头约占身高的**四分之一到三分之一**（偏 Q 版，像附图 10 的伊莉丝、12 的奈德丽）；**青绿色的幽魂皮肤**；**深古铜色的头盔**，顶上和两侧有**向上弯的尖角**，头盔顶上竖起一束**很长的紫罗兰色羽冠 / 马尾**，向后飘；头盔下面两侧垂着**黑色的长发**；**眼睛是发亮的淡青白色**，**两只眼睛看得清**；**深蓝色的嘴唇**，冷着脸；**脸朝右前方平视**。
> - **身体和衣服**：**青绿色发光的幽魂皮肤**（手和脚最亮，接近亮青色；手臂、大腿稍暗的青绿）；**深灰黑色的铠甲**：胸甲、肩甲、腰带、腰间几块甲片；腰下是**深紫红色、下摆破成一条条的布裙**；**小腿套着黑色的护胫**，**脚是光着的青色脚**；手腕有黑色护腕；**手指细长、像爪子**。**背上斜插着两支备用的矛**（一支黑色、一支发光的青色幽灵矛），从肩后露出来。
> - **长矛**（附图 1、6）：**很长**，约和她的身高一样长；**黑色的矛杆**，杆上有**青色的发光条纹**；矛头是**又长又尖的黑色叶形刃**。只是颜色，不画光晕特效。
> - **A = 英雄联盟的待机**（附图 1、5a）：**低低地弓步蹲着**，两腿大大地分开；**近侧的手（画面左边）低低地握着长矛，矛头朝画面左下方、伸到她身后**；远侧的手垂在身前，五指张开像爪子；羽冠向后飘。**B = 站直的战斗站姿**（附图 6、7、5b）：身体立起来，两脚分开站稳，**近侧的手握着长矛斜向下、矛头指向画面左下方**，远侧的手张开伸在身前。
> - **姿势**：3/4 正面朝右（脸朝右前方，胸口朝向看画的人），**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗**，两只脚落在同一条地面线上。
> - **比例**：**偏 Q 版**——头大一点，身材苗条但不要细长的写实比例；风格完全照附图 10–14。
> - **大小**：**两张都用正方形画布 1536×1536**，同样大小的格子。B 站直时**从头盔顶（不算羽冠和尖角）到脚底约 864 px，也就是约 72 格**；A 蹲着，用同一个比例（附图 5a 就是这个大小）。**脚底在离画布底边约 196 px 的地方**（附图 5a、5b 的灰线）；**她的身体靠画面右边**，长矛向左伸，羽冠可以高出头顶，全部在画面里。
> - **像素块**：大小一致的方块，**每块 12 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个像素）；**外轮廓一圈 2 块宽的近黑描边**；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（飞出去的矛、矛插在敌人身上、灵魂锁链、光晕都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/kalista-picture/kalista-A.png`、`kalista-B.png`（1536×1536），都是**真透明背景**；原始生成图原样放进 `outputs/kalista-picture/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `kalista_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_kalista_idle.png` | 英雄联盟原版卡莉斯塔待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_kalista_frontal.png` | 同一帧，正面 | 铠甲、腰带、布裙怎么叠 |
| `refs/3_kalista_head.png` | 头部特写 | 头盔的尖角、紫色羽冠、黑发、眼睛、嘴唇、皮肤颜色 |
| `refs/4_kalista_back.png` | 同一帧的背后 | 背上的两支备用矛、羽冠 |
| `refs/5_kalista_splash.png` | 官方加载画面 | 气质（复仇、幽灵、冷） |
| `refs/5a_layout_A.png` | A 的布局示意（模型剪贴，只看位置和大小） | 画布上她的位置、大小、脚底线 |
| `refs/5b_layout_B.png` | B 的布局示意（同一比例） | 画布上她的位置、大小、脚底线 |
| `refs/6_kalista_stand.png` | 英雄联盟里她站直的一帧，3/4 朝右 | B 的姿势和**角度** |
| `refs/7_kalista_stand_side.png` | 同一帧，接近侧面 | B 的矛怎么握 |
| `style/10_style_elise.png` | 本包同样密度（每游戏像素 1.8 格）的伊莉丝待机（8 倍放大，一格 = 一个像素） | **只看风格**：像素粗细、描边、比例、女英雄的头身比 |
| `style/11_style_vladimir.png` | 同样密度的弗拉基米尔（8 倍） | **只看风格** |
| `style/12_style_nidalee.png` | 奈德丽（8 倍，密度稍低） | **只看风格**：女英雄的头身比例 |
| `style/13_style_galio.png` | 加里奥（8 倍） | **只看风格** |
| `style/14_style_zeri.png` | 泽丽（8 倍） | **只看风格** |

## 提示词 1：`kalista-A.png`（英雄联盟的待机）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-7 are 3D renders and art of a character from the game: a vengeful GHOST WARRIOR WOMAN with a long spear (1 her idle in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 2 the same from the front: the armour, the belt and the layered skirt; 3 her head close-up: the horned helm, the long violet crest, the black hair, the eyes, the lips, the skin; 4 the same from behind: the two spare spears on her back; 5 the official illustration: her vengeful, cold, ghostly mood; 5a THIS picture's layout guide: where she goes on the canvas and how big, the grey line is the ground; 5b the other picture's guide: ignore it; 6-7 an upright pose - not this picture). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chunky chibi-ish proportions and head size (10 and 12 are the closest: women of this series; 10 and 11 have exactly this picture's density).
Create ONE pixel-art picture of the woman, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Draw her at the size of image 5a: standing upright she would be about 864 px (about 72 squares) from the top of her helm (not counting the crest and the horns) to her soles; here she crouches, so she is lower. Her soles about 196 px above the bottom edge (the grey line of image 5a); her body on the RIGHT half of the canvas, the spear reaching back to the LEFT; the crest may rise above her head; everything whole, comfortable transparent margins, nothing cut off; both feet on one ground line.
THE WOMAN: a spectral warrior. THE HEAD, a little big (chibi-ish, about a quarter to a third of her height): GLOWING CYAN-TEAL ghost skin; a DARK BRONZE HELM with upward-curving HORN points on top and at the sides, and from the helm's top a very long VIOLET-PURPLE CREST / plume sweeping back; long BLACK HAIR hanging at both sides of the face under the helm; PALE WHITE-CYAN GLOWING EYES, TWO EYES clearly readable; dark blue lips, a cold stern face; the face turned to the front-right, looking straight ahead. THE BODY: slim; the skin GLOWING CYAN-TEAL everywhere it shows (the hands and the bare feet the brightest, almost bright cyan; the arms and thighs a deeper teal); DARK GREY-BLACK ARMOUR: a breastplate, pauldrons, a belt and plates at the waist; below the waist a DARK MAROON-PURPLE cloth skirt torn into ragged strips; BLACK armoured SHIN GUARDS, BARE cyan feet; dark bracers on the wrists; long thin clawed fingers. Two SPARE SPEARS stuck diagonally across her back (one black, one glowing cyan), their ends showing behind her shoulders. THE SPEAR in her hand: VERY LONG, about as long as she is tall; a BLACK shaft with GLOWING CYAN streaks; a long, sharp BLACK LEAF-SHAPED BLADE (colours only, no glow effect).
THE POSE: League's idle (image 1): 3/4 view facing right (face to the front-right, chest toward the viewer), CROUCHED LOW in a wide lunge, legs far apart; the NEAR hand (image left) holds the spear LOW, its blade pointing to the image LOWER LEFT, reaching out behind her; the FAR hand hangs before her with the fingers spread like claws; the crest flowing back. The NEAR leg on the image LEFT in full tone, the FAR leg on the image RIGHT a step darker; both feet on one ground line.
PROPORTIONS: chibi-ish like images 10-14 - a slightly big head, slim but NOT slender realistic proportions, legs not too long.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and the spear; inside it every material in its own 3-4 flat shades, no stray single odd squares: the skin cyan-teal (bright cyan on the hands and feet), the eyes pale white-cyan and that colour used ONLY by the eyes, the helm dark bronze with a lighter bronze edge, the crest violet-purple with a lighter lilac highlight, the hair black with a dark blue-grey highlight, the armour dark grey-black with LIGHTER grey edge highlights so it never reads as one black blob, the skirt dark maroon-purple with a lighter edge, the spear black with a grey edge light and cyan streaks; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no flying spears, no soul chains, no glow aura, no mist), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 2：`kalista-B.png`（站直的战斗站姿）

十四张图都附上，顺序同上表；**最好把 A 画好的那张也附上**，让人和衣服一模一样。

```text
Fourteen attached images (plus, if you have it, your finished picture A of the same woman: keep her IDENTICAL, only the pose changes). Images 1-7 are 3D renders and art of a character from the game: a vengeful GHOST WARRIOR WOMAN with a long spear (6 her upright stance in 3/4 view facing right - the ANGLE and the POSE of this picture; 7 the same from nearer the side: how she holds the spear; 1 her idle in 3/4 view: the look; 2 the front: the armour, the belt and the layered skirt; 3 her head close-up: the horned helm, the long violet crest, the black hair, the eyes, the lips, the skin; 4 the back: the two spare spears on her back; 5 the official illustration: her vengeful, cold, ghostly mood; 5b THIS picture's layout guide: where she goes on the canvas and how big, the grey line is the ground; 5a the other picture's guide: ignore it). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chunky chibi-ish proportions and head size (10 and 12 are the closest: women of this series; 10 and 11 have exactly this picture's density).
Create ONE pixel-art picture of the woman, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). She is about 864 px (about 72 squares) from the top of her helm (not counting the crest and the horns) to her soles, her soles about 196 px above the bottom edge (the grey line of image 5b); her body on the RIGHT half of the canvas, the spear reaching back to the LEFT; the crest may rise above her head; everything whole, comfortable transparent margins, nothing cut off; both feet on one ground line.
THE WOMAN: exactly as in picture A - GLOWING CYAN-TEAL ghost skin (the hands and bare feet the brightest), a DARK BRONZE HELM with upward-curving HORN points and a very long VIOLET-PURPLE CREST sweeping back, long BLACK HAIR at both sides of the face, PALE WHITE-CYAN GLOWING EYES (two eyes clearly readable), dark blue lips, a cold stern face looking to the front-right, the head a little big (a quarter to a third of her height); DARK GREY-BLACK ARMOUR (breastplate, pauldrons, belt, waist plates), a DARK MAROON-PURPLE skirt torn into ragged strips, BLACK SHIN GUARDS, BARE cyan feet, dark bracers, long thin clawed fingers; two SPARE SPEARS across her back (one black, one glowing cyan); THE SPEAR in her hand VERY LONG (about her height), a BLACK shaft with GLOWING CYAN streaks, a long sharp BLACK LEAF-SHAPED BLADE (colours only, no glow).
THE POSE: an upright fighting stance (image 6): 3/4 view facing right (face to the front-right, chest toward the viewer), the body UPRIGHT, feet apart and planted; the NEAR hand (image left) holds the spear slanting DOWN, its blade pointing to the image LOWER LEFT behind her; the FAR hand open and held out before her. The NEAR leg on the image LEFT in full tone, the FAR leg on the image RIGHT a step darker; both feet on one ground line.
PROPORTIONS: chibi-ish like images 10-14 - a slightly big head, slim but NOT slender realistic proportions, legs not too long.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and the spear; inside it every material in its own 3-4 flat shades, no stray single odd squares (colours as in picture A: the eye colour used ONLY by the eyes, the armour dark grey-black with LIGHTER grey edge highlights, the skin bright cyan on the hands and feet); light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no flying spears, no soul chains, no glow aura, no mist), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底）；两张都是 1536×1536；四周留边，人物、长矛、羽冠都完整，不出画。
- 头：青绿色皮肤、深古铜色带尖角的头盔、**很长的紫色羽冠**、两侧黑色长发、**淡青白色发亮的眼睛、两只眼睛看得清**（这个颜色只给眼睛用）、深蓝嘴唇、**平视前方**；头约占身高四分之一到三分之一。
- 衣服：深灰黑铠甲（有亮一点的边，不糊成一团黑）、深紫红破布裙、黑护胫、**光着的青色脚**、手和脚最亮；**背上两支备用矛**。
- 长矛：约和身高一样长、黑杆青纹、黑色叶形长刃，矛头朝画面左下方。
- A：低低地弓步蹲着、近侧手低握长矛；B：站直、两脚分开、近侧手握矛斜向下、远侧手张开在身前。A 和 B 是同一个人、同样的格子大小、同样大的头和身体。
- B 从头盔顶到脚底约 864 px（约 72 格）；A 用同一个比例；身体在画面右半边。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗；脚都在同一条水平线上；没有任何特效。
- **每块 12 像素、大小一致、对齐网格**；2 块宽的近黑外描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述（提示词里本来就没写名字）。
- 全部画完后最后写 `outputs/kalista-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/kalista/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 12 px；伊莉丝回来时画大了一半），按它自己的格子读回，和同位置英雄（瓦鲁斯、图奇、德莱文、伊莉丝）并排、按游戏里的大小给用户挑 A / B（PPU 先按 1.8，再出 1.5 / 1.8 / 2.0 / 2.2 的对比给用户定）。
- 选定后写第 2 步动作包：长矛是刚体部件，动作里只平移和整块转直角，不变形；跑步照英雄联盟（她是飘着滑行的，脚离地，矛斜拖在身后，附图 Kalista_Run1）；普攻 = 抬手投矛（新矛从手里出现）+ 攻击后的小跳（Kalista_Attack1_Dash_0 / _180：往前、往后各一套）；Q = 举矛过肩全力投掷（Kalista_Spell1）；E = 握拳往回一扯（Kalista_Spell3）；R = 伸手召唤再甩出（Kalista_Spell4_Call / _Throw）。
