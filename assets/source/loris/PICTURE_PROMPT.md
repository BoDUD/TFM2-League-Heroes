# 洛里斯（金铲铲之战 · 第 16 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 洛里斯是金铲铲之战第 16 赛季的三费卡（皮尔特沃夫 / 神盾使），双城之战里皮尔特沃夫的大胡子执法官，**拿一面比他人还宽的铜金色巨型塔盾**。金铲铲里他**把巨盾立在身前的地上，双臂交叉搭在盾的上沿，只露出头和肩膀**。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **长相**：中年壮汉，**深棕色的乱发**（往后往上翘，有几缕垂在额前），额头上绑一条**蓝色的头巾**，**浓密的络腮胡**（深棕带一点灰，下巴上的胡子最厚），**浓眉**，眼睛不大、眼神沉稳，鼻子宽、嘴角往下，一脸严肃；脸是晒过的暖肤色。
> - **身上**：**深蓝 / 宝蓝色的执法官盔甲**，到处镶**铜金色的边**；肩上有**厚重的铜金色肩甲**（近处的肩甲上有一个圆形齿轮纹章）；胸甲是深藏青色，上面有铜金色的线条；里面的衣服是**蓝色**；**黑色的手套**；腰下是**蓝灰色的裤子**，膝盖和小腿有**深蓝镶铜边的护甲**；**黑色的厚靴子**。人很壮：肩宽、胸厚、手臂粗。
> - **巨盾**：一面**高大的长方形塔盾**（立在地上时从地面到他的胸口，宽度比他的身体还宽）：**铜金色的盾框**，盾面分成几条**深藏青色的竖条**（上面有淡淡的蓝色光泽），中间一条**铜金色的竖脊**，**盾底收成一个 V 字（倒人字形）**，盾的上半部中间是一枚**铜金色的十字星形徽章，中心镶一颗发光的青蓝色宝石**（看附图 7）。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：立盾**（金铲铲原样，附图 1、4、6、7、10a）：**3/4 朝右**，**巨盾立在他身前的地上**、盾面朝右前方，他站在盾后面，**两条手臂交叉搭在盾的上沿**，盾上面露出**头、络腮胡和两边的肩甲**，盾底下露出两只靴子；抬着下巴、沉着地看向右前方。
> - **B：持盾**（附图 2、8、10b）：**3/4 朝右**，站得很稳，**远处的手（画面左）握着巨盾立在身体后侧**（盾竖着，底边快碰到地面，盾面朝画面左前方），**整个身体都露出来**；**近处的手（画面右）握拳放在胸前**，随时要挥拳；看向右前方。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的布隆（同样拿大盾的辅助）、杰斯、凯特琳（皮城的执法官、他的上司）和希尔科（本系列的金铲铲英雄），**只看风格**。
> - **长相照金铲铲的模型**（附图 1、2、4、5、8 是模型的渲染，附图 3 是脸部特写；附图 6 是官方原画（上一个版本的他），**头发、头巾、胡子、脸以原画和附图 3 为准**；附图 7 是巨盾单独的正面（盾上方那一小块碎片不用画）；附图 9 是他举盾冲锋的样子，只看盾有多大）。
> - **比例**：Q 版人类，**头约占身高的三分之一**（脸要大、要清楚，头发算在头里），身材**比一般英雄更壮**：肩宽、胸厚。
> - **脸要清楚**（附图 3 特写、附图 6 原画）：皮肤 3 档；**两只眼睛一样高**，每只至少 1×2 格，深色，各有一格白色反光；**浓眉**压在眼睛上；**络腮胡**从耳朵下面一直包到下巴，下巴最厚，胡子 2–3 档深棕；嘴在胡子里露出一格暗色；**蓝头巾**横在额头上，头发从头巾上面翘出来，额前垂一两缕，**头发不能盖住眼睛**。
> - **画布用正方形 1536×1536**。**A 和 B：从头发顶到脚底都约 638 px，也就是约 58 格**；A 宽约 29 格（主要是巨盾的宽度，最多 36 格），B 宽约 31 格（含身后的巨盾，最多 38 格）。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。巨盾全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。发光的地方（盾上徽章的青蓝宝石）用**更亮的一档平涂**表示，不要柔光。
> - 不画任何技能特效（护盾光罩、冲击波、嘲讽标记都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/loris-picture/loris-A.png`、`loris-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/loris-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/loris_picture_done.zip`。

## 附图（在压缩包 `loris_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_loris_34.png` | 金铲铲洛里斯的模型，待机（盾立身前），3/4 朝右 | **A** 的姿势、颜色、**角度**、手臂怎么搭在盾上 |
| `refs/2_loris_front.png` | 模型，盾在身体一侧，整个身体露出来 | 盔甲、肩甲、铜边、裤子、靴子 |
| `refs/3_loris_head.png` | 头部特写 | **头发、蓝头巾、络腮胡、脸**、肩甲 |
| `refs/4_loris_body.png` | 待机，去掉巨盾 | 盾后面的身体、交叉的手臂 |
| `refs/5_loris_back.png` | 背后 | 头发后面、盔甲背面、盾背面 |
| `refs/6_loris_art.png` | 官方原画（上一个版本的棋子卡面） | **头发、头巾、胡子、脸、神情** |
| `refs/7_loris_shield.png` | 巨盾单独，正面 | **盾的形状、竖条、V 字盾底、十字星徽章和青蓝宝石**（上面那一小块碎片不画） |
| `refs/8_loris_side.png` | 模型持盾在身侧 | **B**：盾竖在身体后侧 |
| `refs/9_loris_charge.png` | 模型举盾冲锋 | 只看盾有多大 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 头顶 |
| `refs/10b_layout_B.png` | B 的大小示意 | 只看大小和地面线 |
| `style/11_style_braum.png` | 本包的布隆（同样拿大盾），8 倍放大，一格 = 一个像素 | **只看风格**：大盾、壮汉怎么画 |
| `style/12_style_jayce.png` | 本包的杰斯（8 倍） | **只看风格**：皮尔特沃夫的蓝金配色 |
| `style/13_style_caitlyn.png` | 本包的凯特琳（8 倍，皮城执法官） | **只看风格**：皮城执法官的制服 |
| `style/14_style_silco.png` | 本系列的希尔科（8 倍） | **只看风格**：金铲铲英雄在格子上的样子 |

## 提示词：`loris-A.png` / `loris-B.png`（同一段提示词，先画 A 再画 B）

十五张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fifteen attached images. Images 1-9 show ONE character from a game: a big, burly middle-aged POLICEMAN with a GIANT TOWER SHIELD - messy DARK BROWN HAIR swept back and up with a few strands over the forehead, a BLUE HEADBAND tied round his forehead, a THICK FULL BEARD (dark brown with a little grey, thickest on the chin), heavy brows, small steady eyes, a broad nose, the mouth turned down, a stern look; warm tanned skin. DARK BLUE / ROYAL BLUE enforcer ARMOUR with BRONZE-GOLD TRIM everywhere; HEAVY BRONZE SHOULDER PAULDRONS (a round GEAR emblem on the near one); a dark navy breastplate with bronze lines; a BLUE shirt under it; BLACK GLOVES; BLUE-GREY trousers with dark blue, bronze-edged KNEE AND SHIN ARMOUR; heavy BLACK BOOTS. He is broad and strong: wide shoulders, deep chest, thick arms. THE SHIELD: a TALL RECTANGULAR TOWER SHIELD (standing on the ground it reaches his chest and is wider than his body): a BRONZE-GOLD FRAME, the face split into DARK NAVY vertical panels with a faint blue sheen, a BRONZE central ridge, the BOTTOM ending in a V (an inverted chevron), and on its upper middle a BRONZE FOUR-POINTED STAR EMBLEM holding a GLOWING CYAN GEM. (1 his idle, 3/4 view facing right: the shield planted on the ground in front of him, his arms crossed on its top edge - for picture A, the look and the ANGLE; 2 the same model with the shield off at his side, the whole body seen: the armour, the pauldrons, the trim, the trousers, the boots; 3 his head close-up: the HAIR, the BLUE HEADBAND, the BEARD and the face; 4 the idle without the shield: the body and the crossed arms behind it; 5 from behind; 6 the official art of him: follow it for the hair, the headband, the beard and the face; 7 the shield alone from the front: its SHAPE, the panels, the V bottom, the star emblem with the cyan gem - ignore the small loose fragment above it; 8 his model holding the shield upright at his side, for picture B; 9 his model charging behind the raised shield: how big the shield is.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the top of his hair. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a strong man with a big shield, 12 a man in the same blue and gold city, 13 a policewoman of the same city, 14 a hero of this same series).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hair, the shield); his soles level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; GLOW drawn only as a brighter flat shade (the cyan gem on the shield), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO effects (no shield bubble, no shockwave, no sparkles, no marks); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi - his head (with the hair) about ONE THIRD of his body height, the face big and clear, turned to the front-right; a BROAD, STRONG body, wider than an ordinary hero. FACE CLEAR: skin in 3 shades; TWO EYES at the SAME height, each at least 1x2 squares, dark with one white glint square each; heavy brows just over them; the FULL BEARD from below the ears round the jaw, thickest on the chin, in 2-3 dark brown shades; a one-square dark mouth inside the beard; the BLUE HEADBAND straight across the forehead with the hair sticking up above it and one or two strands over the forehead, the hair never over the eyes. THE COLOURS: hair dark brown in 3; skin warm tan in 3; beard dark brown-grey in 2-3; headband blue in 2; armour dark blue / royal blue in 3-4 with bronze-gold trim in 2-3; pauldrons bronze in 3; shirt blue in 2; gloves black in 2; trousers blue-grey in 3; boots black in 2; shield frame and ridge bronze-gold in 3, panels dark navy in 2-3 with a lighter blue streak, the gem cyan in 2.
PICTURE A (loris-A.png): THE SHIELD PLANTED IN FRONT, 3/4 view facing right (images 1, 4, 6, 7 and 10a): the giant shield stands on the ground in front of him, its face turned to the front-right; he stands behind it with BOTH FOREARMS CROSSED ON ITS TOP EDGE; over the shield show his head, beard and both pauldrons; under the shield his two boots; chin up, looking calmly to the front-right. About 638 px (about 58 squares) from the top of his hair to his soles, about 29 squares wide (never more than 36).
PICTURE B (loris-B.png): THE SHIELD AT HIS SIDE, 3/4 view facing right (images 2, 8 and 10b): standing firm, feet apart; his FAR hand (image left) holds the giant shield upright at the back of his body, its bottom just above the ground, its face turned to the front-left, so his WHOLE BODY is seen; his NEAR hand (image right) is a clenched fist held in front of his chest, ready to punch; eyes to the front-right. About 638 px (about 58 squares) from the top of his hair to his soles, about 31 squares wide with the shield (never more than 38); his soles on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、巨盾完整，不出画。
- **A**：约 638 px（约 58 格），3/4 朝右，**巨盾立在身前的地上、双臂交叉搭在盾沿上**，盾上露出头、胡子、肩甲，盾下露出靴子；脚底在地面线上。
- **B**：约 638 px（约 58 格），**远处的手握着巨盾竖在身体后侧、整个身体露出来，近处的手握拳在胸前**；脚底在地面线上。
- 两张都要：**深棕乱发 + 蓝头巾 + 浓密络腮胡 + 浓眉**；**宝蓝镶铜边的盔甲 + 厚重铜金肩甲（齿轮纹章）+ 黑手套 + 蓝灰裤子 + 黑靴子**；**铜金框、深藏青竖条、V 字盾底、十字星徽章 + 青蓝宝石的巨盾**；身材壮实。
- 没有特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/loris-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/loris_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有洛里斯自己的动作（我已经按动作片段渲染出来了，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、两只手（挥拳、握盾、交叉搭在盾上）、整面巨盾（会被举起来冲锋、甩出去砸人、砸进地里）、两条腿（跑步、冲锋、半蹲）。

| 动作 | 金铲铲里怎么做 / 我们的技能 |
|---|---|
| 待机 | 选 A：巨盾立在身前、双臂搭在盾上；选 B：盾竖在身侧、拳在胸前 |
| 移动 | 盾提在身侧沉重地小跑（金铲铲原样） |
| 普攻「盾击」 | 把巨盾从身侧抡过来砸人，再补一拳（金铲铲原样） |
| 技能1「皮城争斗」 | 身上亮起护盾，举起巨盾挡在身前往前冲锋，撞飞路上的敌人（金铲铲的冲锋动作） |
| 技能2「盾卫」 | 冲到受伤的队友身边，把巨盾往身前一立，给两人都套上护盾 |
| 大招「钢铁防线」 | 双手把巨盾高高举起，狠狠砸进地里，冲击波击飞周围的敌人并嘲讽他们（金铲铲的施法动作） |
| 死亡 | 巨盾脱手倒下，人跪倒在地（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/loris/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和布隆、希尔科、麦迪、爆爆按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_loris_picture.py`（模型在 Riot 客户端的 `TFTSet16.wad.client`；两个子网格名字是空的，按序号：0 = 人，1 = 巨盾；九段动作只有路径哈希，`CLIPS` 里按内容命名）。
