# 生化魔人 扎克：第 0 步，先画像素风原图（给 Codex 的提示词）

> 扎克是英雄联盟里**一个用活体绿色黏液做成的大块头**（祖安的秘密武器），身体能拉长、弹射、分裂。这一步把他画出来，用户从里面挑：
> - **扎克**：**宽大、驼背的身体**，整个人是**半透明的亮绿色黏液**（像果冻），身体里面能看到**深一点的绿色纹路和内脏的影子**；**两条又粗又长的手臂**，垂到膝盖附近，**三根粗手指的大手**；**短粗的腿**，两脚分开稳稳站着；**小小的头埋在两肩之间**，**发黄光的眼睛**，**咧开的大嘴**，露出一排**深色的尖牙**；头顶长出**一根深色的弯弯触须**（像一根茎，末端一个小圆疙瘩，颜色偏深蓝绿），往后上方卷起来。
>
> 请 Codex 画**两张全身像**（**格子大小一样**），用户从里面挑大小：
> - **A：扎克，英雄联盟里的待机，3/4 正面朝右**（附图 1、2、9a）。
> - **SA：A 的侧面，朝右**（附图 6、9b）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的科加斯、蒙多医生、古拉加斯、沃利贝尔（都是大块头），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–8；附图 5 官方原画看气质和颜色——**原画里的半透明黏液感最重要**）。
> - **比例**：Q 版。扎克的**头比原版大一些**（连嘴约占头顶到脚底的四分之一），但还是**埋在两个大肩膀中间**；**肩膀和手臂很大很壮**，手垂到膝盖附近；**腿短粗**，两脚分开；**触须要清楚**，从头顶往后上方卷，不出画。
> - **扎克的脸**（附图 3 特写）：**两只发黄光的眼睛一样大、一样高、都看得见**（每只至少 2×2 格，最亮一格接近白黄）；眼睛上面一点深色的眉骨；**咧开的大嘴**，一排**深色的尖牙**，嘴里深绿近黑；看起来顽皮、坏笑。
> - **颜色**：黏液身体 **亮绿 4 档**（最亮处是带一点黄的荧光绿高光，像果冻反光；暗处是深一点的翠绿）；身体里面的纹路和内脏影子 **深绿 2 档**（一块一块，不要乱点）；手指尖和脚 稍深的绿；眼睛 黄 2 档（中心近白）；牙齿 深灰绿 2 档；触须 深蓝绿 2–3 档，末端小圆疙瘩最深。
> - **画布用正方形 1536×1536**。**扎克从头顶（不算触须）到脚底约 550 px，也就是约 50 格；触须再往上约 8 格，触须顶到脚底约 58 格（约 638 px）**。脚底在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站在画布中间（附图 9a、9b 的位置）。触须、两只大手全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（深墨绿近黑也可以）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。**半透明感用平涂的高光块和里面的深色纹路表现，不要真的半透明像素。**
> - 不画任何技能特效（黏液块、拉长的手臂、弹弓、弹跳冲击、爆炸的黏液都放到后面单独画）；不画地面，不画投影，不画脚下的黏液水洼。
> - 交付：`outputs/zac-picture/zac-A.png`、`zac-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/zac-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/zac_picture_done.zip`。

## 附图（在压缩包 `zac_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zac_idle.png` | 英雄联盟原版扎克的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_zac_frontal.png` | 同一帧，正面 | 肩膀、手臂、手、腿 |
| `refs/3_zac_head.png` | 头部特写（3/4） | 黄眼睛、大嘴尖牙、触须怎么从头顶长出来 |
| `refs/4_zac_back.png` | 同一帧的背后 | 背、肩膀、触须往后卷 |
| `refs/5_zac_splash.png` | 官方加载画面 | 气质、**半透明黏液的颜色和高光**、脸 |
| `refs/6_zac_side.png` | 同一帧，侧面朝右 | SA 的角度 |
| `refs/7_zac_run.png` | 跑步的一帧（3/4） | 腿和手臂怎么动（这一步不画，后面用） |
| `refs/8_zac_stretch.png` | Q 拉长手臂的一帧 | 手臂能拉多长（这一步不画，后面用） |
| `refs/9a_layout_zac.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 在画布上的位置、大小、地面线（灰）；浅灰线 = 触须顶 |
| `refs/9b_layout_zac_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/10_style_chogath.png` | 本包的科加斯，8 倍放大，一格 = 一个像素 | **只看风格**：大块头怪物、尖牙大嘴 |
| `style/11_style_drmundo.png` | 本包的蒙多医生（8 倍） | **只看风格**：祖安的紫绿配色、壮汉的手臂 |
| `style/12_style_gragas.png` | 本包的古拉加斯（8 倍） | **只看风格**：圆滚滚的大身子怎么分档 |
| `style/13_style_volibear.png` | 本包的沃利贝尔（8 倍） | **只看风格**：大肩膀、大爪子在格子上怎么画 |

## 提示词：`zac-A.png` / `zac-SA.png`（同一段提示词，只换最后一句）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-8 are 3D renders and art of a character from a game. THE GOO BRUTE (images 1-8): a HULKING, HUNCHED man made entirely of LIVING GREEN SLIME - his body TRANSLUCENT BRIGHT GREEN like jelly, with DARKER GREEN VEINS and the shadows of organs showing inside; HUGE THICK LONG ARMS hanging down to about his knees, BIG HANDS with three thick fingers; SHORT THICK LEGS; a SMALL HEAD SUNK BETWEEN THE BIG SHOULDERS with GLOWING YELLOW EYES and a WIDE GRIN full of DARK JAGGED TEETH; a DARK CURLING TENDRIL (a stalk ending in a small round knob, dark blue-green) growing from the top of his head and curling up and back. (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the shoulders, the arms, the hands, the legs; 3 his head close-up: the yellow eyes, the grin and teeth, where the tendril grows; 4 the same from behind: the back, the shoulders, the tendril curling back; 5 the official illustration: his mood, the COLOURS and the GLOSSY TRANSLUCENT SLIME LOOK, the face; 6 the idle from the side, facing right - the angle of SA; 7 a running frame and 8 an arm stretched far - both for later.) Images 9a-9b are layout guides: where the character goes on the canvas and how big, the grey line is the ground, the light line the tendril top. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a big monster with a toothy grin (10), a hulking brute's arms in flat shades (11), a big round body shaded on the grid (12), huge shoulders and big hands on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the tendril, the big hands); the feet on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows the character (the centre). THE GOO BRUTE is about 550 px (about 50 squares) from the top of his HEAD to his soles; the TENDRIL rises about 8 squares above the head top (about 58 squares from the tendril top to the soles).
PROPORTIONS: chibi. The HEAD BIGGER than in the renders (head with the grin about a quarter of head-top-to-soles) but still SUNK BETWEEN the big shoulders; the SHOULDERS and ARMS HUGE and strong, the hands hanging near the knees; the LEGS SHORT and THICK, the two feet apart, planted on the ground; the tendril clear, curling up and back from the top of the head.
THE FACE: TWO GLOWING YELLOW EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, the brightest square almost white-yellow); a little dark brow ridge over them; a WIDE MISCHIEVOUS GRIN with a row of DARK JAGGED TEETH, the inside of the mouth very dark green.
THE COLOURS: the slime body BRIGHT GREEN in 4 shades (the lightest a glossy yellow-green highlight like jelly catching light, the darkest a deep emerald); the veins and organ shadows inside DARK GREEN in 2, as a few clear blobs and lines (never noise); the fingertips and feet a little darker green; the eyes yellow in 2 (near-white centre); the teeth dark grey-green in 2; the tendril dark blue-green in 2-3, its knob the darkest. Show the TRANSLUCENT JELLY LOOK only with flat highlight blocks and the dark shapes inside - every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black (very dark green-black) outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the bright slime, the dark inner veins, the yellow eyes, the dark teeth and the dark tendril clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no slime blobs flying, no stretched arms, no splashes, no puddle, no glow); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (zac-A.png): THE GOO BRUTE's idle in 3/4 view facing right (images 1, 2 and 9a) - standing hunched and ready, the face to the front-right; the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker and a little higher; both big hands hanging loose near the knees, never covering the face; the tendril curling up and back.
PICTURE SA (zac-SA.png): the SAME brute as A seen exactly from the SIDE, FACING RIGHT (images 6 and 9b) - the face to the image right with one yellow eye visible and the grin in profile, the near arm hanging in front of the body, the tendril curling up and back over his back, both feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，触须、两只大手完整，不出画。
- 扎克：Q 版但头埋在两个大肩膀中间；**两只发黄光的眼睛一样大、一样高**、带高光；**咧嘴坏笑，一排深色尖牙**；头顶**深色弯触须**（末端小圆疙瘩）；亮绿半透明黏液感（平涂高光块 + 里面的深绿纹路）；粗长手臂、三指大手垂到膝盖附近；短粗腿，两脚分开站在地上。
- A 是 3/4 正面朝右，SA 是正侧面朝右；头顶到脚底约 550 px（约 50 格），触须顶到脚底约 638 px（约 58 格），脚底在地面线上。
- 没有任何技能特效，没有水洼。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边，也不要半透明的身体像素）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/zac-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zac_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：扎克的头（一张脸用在所有帧，触须跟着头走）、两条大手臂和手（拉长、抓、砸）、两条短腿（跑、蹲下蓄力、跳）、身体（弹跳时会压扁、拉高）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | Zac_idle1 / Zac_run_Slow / Zac_attack1–4 / — / Zac_death2 | 普攻是大手砸、抡 |
| **延伸打击**（Q，skill） | Spell1_max / Spell1_min / Spell1_Slam | 一只手臂拉得很长抓住敌人，再把人甩过来砸在一起 |
| **橡筋弹弓**（E，skill2） | spell3_windup / spell3_flying | 双手按在地上，身体往后拉成弹弓，蓄力后把自己弹出去，落地击飞 |
| **动感弹球**（R，大招） | Spell4_3 / Revert_spell4 | 身体压扁成一个大球，连弹 4 次，每次落地击飞敌人 |
| 不稳定物质（W，并入被动） | Spell2_scale | 身体一鼓，黏液向四周爆开 |
| 细胞分裂（被动复活，扩展包） | Death_unite | 死时分裂成 4 块小黏液，再合回来 |

连招：**E 落地 → W**（弹弓落地立刻爆一圈黏液）；**E 击飞 → Q**（落地击飞的敌人马上被拉住甩回来）；**Q 甩人 → R**（甩完立刻开大追着弹）；**R 最后一弹 → W**（落地爆一圈并刷新 W）。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/zac/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的打野 / 坦克（科加斯、蒙多、古拉加斯、沃利贝尔、努努）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_nunu_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Zac`（片段名是 .anm 文件名：zac_idle1、zac_run_slow、zac_attack1…4、zac_spell1_max、zac_spell1_slam、zac_spell2_scale、zac_spell3_windup、zac_spell3_flying、zac_spell4_3、zac_death2、zac_death_unite…）；渲染要加 `--hide-submeshes`（皮肤藏着一个水洼和一块小黏液）。加载画面在 WAD 里：`assets/characters/zac/skins/base/zacloadscreen.tex`。
