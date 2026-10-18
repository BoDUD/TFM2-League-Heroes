# 齐天大圣 孙悟空：第 0 步，先画像素风原图（给 Codex 的提示词）

> 悟空是**猴王**：一身**棕色的猴毛**，头顶一撮**向上翘的尖刺头发**（深棕），**猴脸**——脸心是**浅粉肉色**，眼眶一圈红色，**一双发亮的绿眼睛**，圆圆的猴耳朵；脖子上围一条**红色的大围巾**（领子竖起来包着下巴）。两条胳膊套着**巨大的金红护臂**（金色的边框、红色的筒身，筒上一个**银灰色的花纹圆章**），远侧肩膀上有一个**金色的猴头肩饰**（外圈红白）。胸前是**金色的护胸**，中间一个**金色兽面圆扣**；前面垂下一条**长长的金色前襟**（金底、鳞片花纹、红边，尖角朝下垂到膝盖下），外面是**暗红褐色的长袍下摆**，两边膝盖各有一块**圆形的暗钢护膝**；脚上是**紫色的鞋**（金色鞋带）。**一条长长的棕色尾巴从背后翘起来**，尾巴尖颜色稍浅。手里拿着**金箍棒**：**两头是红色的棒身，各套着金色的箍和一个橙红色的端头**，**中段是灰钢色**。请 Codex 画**两张全身像**（同一个悟空，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、8a）。弓着身子、两腿分开半蹲，**近侧的手握着金箍棒斜着朝下**（棒头点在近侧脚前面的地上方向），**远侧的手臂向外张开、手指弯着**，尾巴在背后高高翘起，脸朝右前方，龇牙。
> - **B：收拢一点的备战姿势**（附图 8b 只看大小和地面线）。还是半蹲，**近侧的手把金箍棒竖着立在身边**（下端落在近侧脚旁边的地面上，上端比头高一点），**远侧的手握拳收在腰边**，尾巴翘起；这样整个人横向窄一些。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的嘉文四世（拿长枪、金甲）、潘森和内瑟斯（兽头、毛脸），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：Q 版，**头（连尖刺头发）约占身高的三分之一**（约 23 格）；身子和腿短一些，护臂和手大；不要细长的写实比例。
> - **头**（附图 3 特写）：深棕色的尖刺头发向上翘、分几档颜色；猴脸的浅粉肉色脸心要清楚，**两只绿眼睛一样大、一样高、都看得见**（每只至少 2 格，带一个亮点），眼眶周围一点红；圆猴耳朵；嘴龇着露出一点白牙；红围巾竖领包住下巴。
> - **衣服**：金红护臂（金框、红筒、银灰圆章要能看出来）、远侧肩上的金猴头肩饰、金护胸和中间的金兽面扣、金色长前襟（红边）、暗红褐长袍下摆、圆形暗钢护膝、紫鞋。
> - **金箍棒**：红—金箍—灰钢—金箍—红，两头橙红端头；棒身要**直**、粗细一致、完整（约 2–3 格粗）。
> - **尾巴**：棕色长尾巴从腰后翘起来，弯成一道弧，尾巴尖稍浅，**和头发、身体分得开**。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只鞋底落在同一条地面线上。
> - **画布用正方形 1536×1536**。**从头发尖到鞋底约 770 px，也就是约 70 格**（尾巴和金箍棒可以高出头顶，不算在内），鞋底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。尾巴、金箍棒、张开的手全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。棕色猴毛、深棕头发、浅粉脸、绿眼睛、红围巾、金色、红护臂筒、银灰圆章、暗红褐长袍、紫鞋、灰钢棒身要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**暗红褐长袍和棕色猴毛很暗，一定要有偏亮的边**，不然在深色背景上会糊成一团。
> - 不画任何特效（分身、筋斗云、旋风、冲击都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/wukong-picture/wukong-A.png`、`wukong-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/wukong-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/wukong_picture_done.zip`。

## 附图（在压缩包 `wukong_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_wukong_idle.png` | 英雄联盟原版悟空的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势和拿棒的方法 |
| `refs/2_wukong_frontal.png` | 同一帧，正面 | 护胸、前襟、护膝怎么排，左右对称的样子 |
| `refs/3_wukong_head.png` | 头部特写 | 尖刺头发、猴脸、绿眼睛、红围巾、金猴头肩饰 |
| `refs/4_wukong_back.png` | 同一帧的背后 | 尾巴从哪里长出来、长袍背后 |
| `refs/5_wukong_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_wukong_spin.png` | 大招转棒的一帧 | 金箍棒伸长横着的样子，身体怎么拧 |
| `refs/7_wukong_side.png` | 同一帧，接近侧面 | 护臂、尾巴、前襟从侧面看的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 他的大小、地面线（灰）；**姿势按文字：金箍棒竖着立在身边** |
| `style/11_style_jarvaniv.png` | 本包的嘉文四世，8 倍放大，一格 = 一个像素 | **只看风格**：金甲、长兵器在格子上怎么画 |
| `style/12_style_pantheon.png` | 本包的潘森（8 倍） | **只看风格**：格子密度、描边、每种材质分几档 |
| `style/13_style_nasus.png` | 本包的内瑟斯（8 倍） | **只看风格**：兽头、毛脸、眼睛在格子上怎么画 |

## 提示词：`wukong-A.png` / `wukong-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a MONKEY KING warrior - BROWN MONKEY FUR, a tuft of SPIKY DARK-BROWN HAIR sweeping up from the top of the head, a MONKEY FACE (a pale pinkish face centre, a little red round the eyes, TWO GLOWING GREEN EYES, round monkey ears, a snarl showing a few white teeth), a big RED SCARF with a high collar wrapped round the chin; HUGE GOLD-AND-RED ARM GUARDS on both arms (gold rims, red cylinders, each with a SILVER-GREY ROSETTE badge), a GOLD MONKEY-HEAD ornament on the far shoulder (ringed red and white); a GOLD CHEST PLATE with a round gold beast-face clasp in the middle; a LONG GOLD TABARD hanging down the front (gold with a scale pattern, red border, pointed tip below the knees) over a DARK MAROON-BROWN ROBE skirt; a round dark-steel guard on each knee; PURPLE SHOES with gold laces; a LONG BROWN TAIL rising from behind his waist in a curve, its tip a little lighter; his STAFF: RED at both ends with GOLD BANDS and ORANGE-RED end caps, a GREY STEEL middle (1 his idle, 3/4 view facing right - the look, the ANGLE, pose A and how he holds the staff; 2 the same from the front: the chest plate, the tabard, the knee guards; 3 the head close-up: the hair, the monkey face, the green eyes, the scarf, the shoulder ornament; 4 the same from behind: where the tail grows, the robe's back; 5 the official illustration: his mood and colours; 6 a frame of his staff spin: the staff extended level, how he twists; 7 the idle nearly from the side: the depth of the arm guards, the tail and the tabard). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, gold armour and a long polearm on the grid (11), the square density, the outline and the number of shades a material gets (12), a furry beast face with readable eyes on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the tail, the whole staff and the open hand whole); both soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 770 px (about 70 squares) from the tip of his hair to his soles - the tail and the staff may rise above his head and are not counted.
PROPORTIONS: chibi - the head with the spiky hair about ONE THIRD of his height (about 23 squares); a shorter body and legs, big arm guards and hands; NOT realistic slim proportions.
THE HEAD: the spiky dark-brown hair sweeping up in a few shades; the pale pinkish face centre clearly readable; TWO GREEN EYES of the SAME size at the SAME height, both visible (each at least 2 squares, with one bright highlight square), a little red round them; round monkey ears; a snarl with a few white teeth; the red scarf's high collar round the chin.
THE CLOTHES: the gold-and-red arm guards (gold rims, red cylinders, the silver-grey rosettes readable), the gold monkey-head ornament on the far shoulder, the gold chest plate and its beast-face clasp, the long gold tabard with a red border, the dark maroon-brown robe skirt, the round dark-steel knee guards, the purple shoes.
THE STAFF: red - gold band - grey steel - gold band - red, orange-red caps at both ends; STRAIGHT, the same thickness all along (2-3 squares), whole.
THE TAIL: a long brown tail rising from behind his waist in a curve, its tip lighter, clearly separated from the hair and the body.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark maroon-brown robe and the brown fur with LIGHTER EDGES so they never turn into one dark mass, the brown fur, the dark-brown hair, the pale face, the green eyes, the red scarf, the gold, the red arm-guard cylinders, the silver rosettes, the purple shoes and the grey steel staff clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no clone, no cloud, no whirlwind, no impact, no glow), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (wukong-A.png): his idle (images 1 and 8a) - hunched, feet wide apart in a half crouch, the NEAR hand holding the staff SLANTED DOWN toward the ground in front of his near foot, the FAR arm held OUT to the side with the fingers curled, the tail curving up high behind him; the face to the front-right, snarling.
POSE B (wukong-B.png): a NARROWER READY STANCE - the SAME monkey king with the SAME 11-px squares: still a half crouch, the NEAR hand holding the staff UPRIGHT beside him (its lower end on the ground by his near foot, its top a little above his head), the FAR fist at his waist, the tail curving up behind him, so he is narrower than in A; the face to the front-right (image 8b shows only his size and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尾巴、金箍棒、张开的手完整，不出画。
- 比例：Q 版，头（连尖刺头发）约占身高三分之一（约 23 格）；护臂和手大。
- 头：深棕尖刺头发分几档；浅粉猴脸清楚；**两只绿眼睛一样大、一样高、都看得见**、带亮点；圆猴耳；红围巾竖领。
- 衣服：金红护臂和银灰圆章、远侧金猴头肩饰、金护胸和兽面扣、金色长前襟（红边）、暗红褐长袍、圆形暗钢护膝、紫鞋。
- 金箍棒：红—金箍—灰钢—金箍—红，两头橙红端头，直、粗细一致、完整。尾巴棕色、尾尖稍浅、和头发身体分得开。
- A：半蹲、近侧手握棒斜向下、远侧手臂张开；B：半蹲、金箍棒竖立在身边、远侧拳头收在腰边，比 A 窄。从头发尖到鞋底约 770 px（约 70 格），鞋底都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/wukong-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/wukong_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/wukong/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_jarvaniv_hd.py` / `design_ziggs_hd.py` 的做法，绝不按更少的行采样），和已合并的近战（嘉文四世、潘森、赵信、易、李青、亚索）按游戏里的大小并排，**早点给用户看 PPU 对比**（茂凯的教训：1.2 / 1.3 / 1.5 并排），给用户挑 A / B 和定大小。
- 定下后第 1 步按游戏格子重画，再自己做动作帧（塔姆 / 茂凯的方式，无损：只平移、整块直角转、整行移；**金箍棒是刚体，每帧都用设计里的同一根**，伸长 = 整格接长同一根的中段）；走路：两腿用设计里自己的整条腿。删行删列后检查前臂、手腕、尾巴这些细的连接处（茂凯的教训）。英雄联盟的动作：普攻 MonkeyKing_attack1 / attack2 / crit；Q 粉碎打击 monkeyking_spell1；W 真假猴王 monkeyking_spell2；E 腾云突击 monkeyking_spell3；R 大闹天宫 monkeyking_spell4（转棒循环）；跑 MonkeyKing_run；死亡 MonkeyKing_death。
