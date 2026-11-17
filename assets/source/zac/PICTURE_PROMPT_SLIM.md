# 生化魔人 扎克：第 0 步重画，瘦长的扎克（给 Codex 的提示词）

> 上一版扎克画成了大块头（宽肩、粗胳膊、短粗腿，附图 14），用户说**「扎克身体应该是瘦的」**。英雄联盟里的扎克是**细腰、长腿**的（肩膀和手臂比较壮，但腰很细、腿很长，不是圆滚滚的一团）。这一步照联盟原版的长短比例重画，**整个人画得比联盟原版还要瘦一些**：
> - **扎克**：**瘦长、微微驼背**的人形，整个人是**半透明的亮绿色黏液**（像果冻），身体里面能看到**深一点的绿色纹路和内脏的影子**；**胸窄、腰细**，看得出一点精瘦的肌肉线条；**两条长手臂**（精瘦，不要鼓成一大团）垂到大腿中间，**三根手指的手**（手不要大）；**细长的腿**，膝盖微弯，两脚分开站着；**头不大**，在短脖子上往前探，**发黄光的眼睛**，**咧开的大嘴**露出一排**深色的尖牙**；头顶长出**一根深色的弯弯触须**（末端一个小圆疙瘩，偏深蓝绿），往后上方卷起来。
>
> 请 Codex 画**两张全身像**（**格子大小一样**）：
> - **A：扎克，英雄联盟里的待机，3/4 正面朝右**（附图 1、2、9a）。
> - **SA：A 的侧面，朝右**（附图 6、9b）。
>
> 你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的费德提克、凯隐、沃里克、艾克（都是瘦的），**只看风格**。附图 14 是上一版扎克：**颜色、脸、触须可以照着它，身材千万不要照它**。
> - **长相和手脚的长短照英雄联盟原版**（附图 1–8；附图 9a、9b 是原版的剪影，看位置和大小；**身子、手臂、腿都要画得比这些图更瘦**；附图 5 官方原画看气质和颜色，**半透明黏液感最重要**）。
> - **比例**：头可以比原版稍大一点（连嘴约占头顶到脚底的五分之一），但**整个人要瘦**：
>   - 肩宽最多两个头宽，腰只有一个头宽左右；
>   - 手臂长而精瘦，粗细大约半个头宽，手垂到大腿中间；
>   - 腿长而瘦，粗细大约半个头宽，大腿和小腿差不多长，膝盖微弯；
  - 胸窄，没有圆肚子，肩膀上不要鼓起两大块；
>   - 身体往前弓一点，头往前探。
> - **扎克的脸**（附图 3 特写）：**两只发黄光的眼睛一样大、一样高、都看得见**（每只至少 2×2 格，最亮一格接近白黄）；眼睛上面一点深色的眉骨；**咧开的大嘴**，一排**深色的尖牙**，嘴里深绿近黑；看起来顽皮、坏笑。
> - **颜色**（和上一版一样，可以照附图 14）：黏液身体 **亮绿 4 档**（最亮处是带一点黄的荧光绿高光，像果冻反光；暗处是深一点的翠绿）；身体里面的纹路和内脏影子 **深绿 2 档**（一块一块，不要乱点）；手指尖和脚稍深的绿；眼睛黄 2 档（中心近白）；牙齿深灰绿 2 档；触须深蓝绿 2–3 档，末端小圆疙瘩最深。
> - **画布用正方形 1536×1536**。**扎克从头顶（不算触须）到脚底约 550 px，也就是约 50 格；触须再往上约 8 格，触须顶到脚底约 58 格（约 638 px）**——和上一版一样高，只是变瘦。脚底在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站在画布中间。触须、两只手全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（深墨绿近黑也可以）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。**半透明感用平涂的高光块和里面的深色纹路表现，不要真的半透明像素。**
> - 不画任何技能特效；不画地面、投影、脚下的黏液水洼。
> - 交付：`outputs/zac-slim-picture/zac-A.png`、`zac-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/zac-slim-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/zac_slim_picture_done.zip`。

## 附图（在压缩包 `zac_slim_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zac_idle.png` | 英雄联盟原版扎克的待机，3/4 朝右 | 颜色、形状、**身材**、**角度**、A 的姿势 |
| `refs/2_zac_frontal.png` | 同一帧，正面 | 细腰、长腿、长手臂（照长短，画得更瘦） |
| `refs/3_zac_head.png` | 头部特写（3/4） | 黄眼睛、大嘴尖牙、触须怎么从头顶长出来 |
| `refs/4_zac_back.png` | 同一帧的背后 | 背、触须往后卷 |
| `refs/5_zac_splash.png` | 官方加载画面 | 气质、**半透明黏液的颜色和高光**、脸 |
| `refs/6_zac_side.png` | 同一帧，侧面朝右 | SA 的角度、身体往前弓 |
| `refs/7_zac_run.png` | 跑步的一帧（3/4） | 腿和手臂怎么动（这一步不画，后面用） |
| `refs/8_zac_stretch.png` | Q 拉长手臂的一帧 | 手臂能拉多长（这一步不画，后面用） |
| `refs/9a_layout_zac.png` | A 的布局示意（原版模型的剪影，按目标大小放好） | 在画布上的位置、大小、站姿、地面线（灰）；浅灰线 = 触须顶（**身子和手脚要比剪影瘦**） |
| `refs/9b_layout_zac_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/10_style_fiddlesticks.png` | 本包的费德提克，8 倍放大，一格 = 一个像素 | **只看风格**：细长四肢的怪物在格子上怎么画 |
| `style/11_style_kayn.png` | 本包的凯隐（8 倍） | **只看风格**：精瘦的上身、细腰、肌肉线条怎么分档 |
| `style/12_style_warwick.png` | 本包的沃里克（8 倍） | **只看风格**：弓着身子的祖安怪物 |
| `style/13_style_ekko.png` | 本包的艾克（8 倍） | **只看风格**：祖安的配色、细手细脚 |
| `style/14_old_zac.png` | 上一版扎克（8 倍） | **只看颜色、脸、触须；身材太胖，不要照它** |

## 提示词：`zac-A.png` / `zac-SA.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-8 are 3D renders and art of a character from a game. THE GOO MAN (images 1-8): a LEAN, LANKY, slightly HUNCHED humanoid made entirely of LIVING GREEN SLIME (the user found the previous picture far too fat: draw him SLIMMER than the renders) - his body TRANSLUCENT BRIGHT GREEN like jelly, with DARKER GREEN VEINS and the shadows of organs showing inside; a NARROW chest and a THIN WAIST with a hint of wiry muscle; LONG LEAN ARMS (wiry, not bloated) hanging to about mid-thigh, smallish hands with three fingers; LONG THIN LEGS, the knees a little bent; a SMALL HEAD on a short neck pushed a little forward (NOT sunk between big shoulders) with GLOWING YELLOW EYES and a WIDE GRIN full of DARK JAGGED TEETH; a DARK CURLING TENDRIL (a stalk ending in a small round knob, dark blue-green) growing from the top of his head and curling up and back. (1 his idle, 3/4 view facing right - the look, the BUILD, the ANGLE and the pose of A; 2 the same from the front: the narrow waist, the long legs and long arms - draw them SLIMMER than here; 3 his head close-up: the yellow eyes, the grin and teeth, where the tendril grows; 4 the same from behind: the back, the tendril curling back; 5 the official illustration: his mood, the COLOURS and the GLOSSY TRANSLUCENT SLIME LOOK, the face; 6 the idle from the side, facing right - the angle of SA and the forward hunch; 7 a running frame and 8 an arm stretched far - both for later.) Images 9a-9b are layout guides: the real model's silhouette placed at the target size - follow where it stands, its stance and how big it is, but make the body, arms and legs SLIMMER than this silhouette; the grey line is the ground, the light line the tendril top. Copy from the images the shapes, the proportions, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading: a lanky creature with long thin limbs (10), a lean bare torso and narrow waist shaded on the grid (11), a hunched creature (12), thin arms and legs in Zaun colours (13). Image 14 is the PREVIOUS picture of this same character: copy ONLY its colours, its face and its tendril - its build is WRONG (far too wide and bulky), do NOT copy its shoulders, arms or legs.
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the tendril, the hands); the feet on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows the character (the centre). THE GOO MAN is about 550 px (about 50 squares) from the top of his HEAD to his soles; the TENDRIL rises about 8 squares above the head top (about 58 squares from the tendril top to the soles).
PROPORTIONS: LEAN and LANKY like the real model (images 1, 2 and 9a). The head may be a little bigger than in the renders (head with the grin about a fifth of head-top-to-soles) but the BODY STAYS SLIM: the shoulders at most two head-widths across, the waist about one head-width; the arms LONG and LEAN (each about half a head wide), the hands hanging to mid-thigh; the legs LONG and LEAN (each about half a head wide), thigh and shin about equally long, the knees slightly bent, the feet a little apart; a narrow chest with NO round belly and NO big lumps on the shoulders; the body leaning slightly forward, the head pushed forward on a short neck; the tendril clear, curling up and back from the top of the head.
THE FACE: TWO GLOWING YELLOW EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, the brightest square almost white-yellow); a little dark brow ridge over them; a WIDE MISCHIEVOUS GRIN with a row of DARK JAGGED TEETH, the inside of the mouth very dark green.
THE COLOURS: the slime body BRIGHT GREEN in 4 shades (the lightest a glossy yellow-green highlight like jelly catching light, the darkest a deep emerald); the veins and organ shadows inside DARK GREEN in 2, as a few clear blobs and lines (never noise); the fingertips and feet a little darker green; the eyes yellow in 2 (near-white centre); the teeth dark grey-green in 2; the tendril dark blue-green in 2-3, its knob the darkest. Show the TRANSLUCENT JELLY LOOK only with flat highlight blocks and the dark shapes inside - every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black (very dark green-black) outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no slime blobs flying, no stretched arms, no splashes, no puddle, no glow); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (zac-A.png): THE GOO MAN's idle in 3/4 view facing right (images 1, 2 and 9a) - standing slightly hunched and ready, the face to the front-right; the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker; both thin arms hanging loose, the hands near mid-thigh, never covering the face; the tendril curling up and back.
PICTURE SA (zac-SA.png): the SAME slim goo man as A seen exactly from the SIDE, FACING RIGHT (images 6 and 9b) - the face to the image right with one yellow eye visible and the grin in profile, the body leaning a little forward, the near thin arm hanging in front of the body, the tendril curling up and back over his back, both feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，触须、两只手完整，不出画。
- **扎克是瘦的**：窄肩细腰、细长手臂（手垂到大腿中间）、细长腿；身体微微往前弓；头不大，在短脖子上，不埋在肩膀里。和附图 9a 的剪影比，宽窄差不多。
- **两只发黄光的眼睛一样大、一样高**，带高光；**咧嘴坏笑，一排深色尖牙**；头顶**深色弯触须**（末端小圆疙瘩）；亮绿半透明黏液感（平涂高光块 + 里面的深绿纹路）。
- A 是 3/4 正面朝右，SA 是正侧面朝右；头顶到脚底约 550 px（约 50 格），触须顶到脚底约 638 px（约 58 格），脚底在地面线上。
- 没有任何技能特效，没有水洼。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/zac-slim-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zac_slim_picture_done.zip`。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**）

选定造型后，Claude 会按这张新造型把扎克所有的动作（待机、跑、普攻、Q 延伸打击、E 橡筋弹弓、R 动感弹球、受击、死亡）照英雄联盟的动作重做一遍，必要时再请你照骨架画关键姿势。所以造型里这些部件要**画得清楚、彼此分得开**：头（一张脸用在所有帧，触须跟着头走）、两条细长手臂和手、两条细长腿、身体。
