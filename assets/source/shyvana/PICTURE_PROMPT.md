# 龙血武姬 希瓦娜：第 0 步，先画像素风原图（给 Codex 的提示词）

> 希瓦娜（英雄联盟 16.20 重做后的版本）有**两种形态**，这一步两种都画，用户从里面挑：
> - **人形**：一位**高挑的半龙女战士**：**淡紫色的皮肤**；一头**金橙色的长发**；头上一圈**深红色的龙角冠**（几根弯弯的红角往后扫，角尖是黑色）；身上是**青银色的龙鳞胸甲**，镶着**金边**；前臂缠着**深红色的布条**；**深紫红色的紧身护腿**，膝盖上有**银金色的鳞片护膝**；脚是**带爪的龙足**；身后一条**长长的深红色鳞片尾巴，尾尖是金色**；肩上有几根小小的金色尖刺。
> - **龙形**：同一个希瓦娜变成的**一头深红色巨龙**，四只带爪的脚着地：**深红色的鳞片**；**两只抬起的大蝙蝠翅膀**（深红色翼膜，里面颜色更深，翼骨关节上有金色的角爪）；头和脖子上是**一圈燃烧的橙黄色火焰鬃毛**；**深色的弯角**；背脊和肘上有**一排象牙色的尖刺**；胸前一块**青色的护甲片**；**黑色的爪子**；**尾尖是金色**的长尾巴。
>
> 请 Codex 画**四张全身像**（同一个希瓦娜，**两种形态的格子大小一样**），用户从里面挑：
> - **A：人形的待机，3/4 正面朝右**（附图 1、2、10a）。她站着，两手垂在身侧，尾巴从身后垂下来、尾尖翘起。
> - **SA：A 的侧面，朝右**（附图 4、10b）。同一个人形希瓦娜**正侧面朝右**（脸朝画面右边，看得见一只眼睛），尾巴在背后（画面左边）。
> - **D：龙形的待机，3/4 正面朝右**（附图 5、6、10c）。四脚着地、身子压低，头在前面（画面右边），两只翅膀抬起，尾巴拖在身后。
> - **SD：D 的侧面，朝右**（附图 8、10d）。同一头龙正侧面朝右。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的斯莫德（一条小龙）、沃利贝尔（大野兽的鳞片和毛）、婕拉和奈德丽（女英雄的脸和头发），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–9）。
> - **比例**：人形 Q 版，**头连角冠约占身高的三分之一**（脸本身清楚），身材修长；龙形是一头又长又壮的巨龙，头大、翅膀大、爪子大。
> - **人形的脸**（附图 3 特写）：淡紫色的脸，**两只眼睛一样大、一样高、都看得见**（每只至少 2×2 格，金黄色的瞳孔，一格白色高光），金橙色的刘海，红色龙角从额头两边往后长。
> - **龙形的脸**（附图 7 特写）：深红色的长吻，**一只发光的黄色眼睛**清楚可见（至少 2×2 格），嘴里一排象牙色尖牙，下巴微张露出紫红色的嘴里，头顶和脖子上的火焰鬃毛。
> - **颜色**：人形：皮肤淡紫 3 档，头发金橙 3–4 档（亮边偏黄），角冠深红 3 档加黑色角尖，胸甲青银 3 档加金边 2 档，布条和尾巴深红 3–4 档（**不要糊成一团红**），护腿深紫红 3 档，护膝银金 2–3 档。龙形：鳞片深红 3–4 档（**不要糊成一团红**，亮边偏橙），翼膜深红加更暗的里侧，火焰鬃毛橙黄 3 档（亮边偏白黄），角和爪黑灰 2–3 档，尖刺象牙色 3 档，胸甲青色 2–3 档，尾尖金色。
> - **画布用正方形 1536×1536**。**人形从角尖到脚底约 484 px，也就是约 44 格；龙形从最高的翼尖到爪底约 572 px，约 52 格**（两种形态格子一样大，所以龙大很多、也长很多）。脚底在离画布底边约 146 px 的地方（附图 10a–10d 的灰线）；站在画布中间（附图 10a–10d 的位置）。角、尾巴、翅膀、爪子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（火球、喷火、火焰护盾、爆炸都放到第 3 步单独画）；不画地面，不画投影。龙的火焰鬃毛是**身体的一部分**，要画。
> - 交付：`outputs/shyvana-picture/shyvana-A.png`、`shyvana-SA.png`、`shyvana-D.png`、`shyvana-SD.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/shyvana-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/shyvana_picture_done.zip`。

## 附图（在压缩包 `shyvana_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_human_idle.png` | 英雄联盟原版人形希瓦娜的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_human_frontal.png` | 同一帧，正面 | 胸甲、布条、护腿、尾巴 |
| `refs/3_human_head.png` | 头部特写（3/4） | 角冠、头发、眼睛 |
| `refs/4_human_side.png` | 同一帧，侧面朝右 | SA 的角度：尾巴、身子的厚度 |
| `refs/5_dragon_idle.png` | 龙形的待机，3/4 朝右 | D 的颜色、形状、角度、姿势 |
| `refs/6_dragon_frontal.png` | 同一帧，正面 | 翅膀、火焰鬃毛、胸甲 |
| `refs/7_dragon_head.png` | 龙头特写 | 眼睛、角、尖牙、鬃毛 |
| `refs/8_dragon_side.png` | 同一帧，侧面朝右 | SD 的角度 |
| `refs/9_shyvana_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/10a_layout_human.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰） |
| `refs/10b_layout_human_side.png` | SA 的布局示意 | 同上，侧面 |
| `refs/10c_layout_dragon.png` | D 的布局示意 | 同上，龙形 |
| `refs/10d_layout_dragon_side.png` | SD 的布局示意 | 同上，龙形侧面 |
| `style/11_style_smolder.png` | 本包的斯莫德，8 倍放大，一格 = 一个像素 | **只看风格**：龙的鳞片、翅膀、火焰在格子上怎么画 |
| `style/12_style_volibear.png` | 本包的沃利贝尔（8 倍） | **只看风格**：大野兽的身体、深色分档、爪子 |
| `style/13_style_zyra.png` | 本包的婕拉（8 倍） | **只看风格**：女英雄的脸、长发 |
| `style/14_style_nidalee.png` | 本包的奈德丽（8 倍） | **只看风格**：女战士的身材、皮肤分档 |

## 提示词：`shyvana-A.png` / `shyvana-SA.png` / `shyvana-D.png` / `shyvana-SD.png`（同一段提示词，只换最后一句）

十七张图都附上，顺序同上表。

```text
Seventeen attached images. Images 1-9 are 3D renders and art of one character from a game, in two forms. HUMAN FORM (images 1-4): a TALL HALF-DRAGON WARRIOR WOMAN with PALE LAVENDER SKIN, a mane of GOLDEN-ORANGE HAIR, a CROWN OF CRIMSON DRAGON HORNS with black tips sweeping back from her brow, a TEAL-SILVER SCALE BREASTPLATE trimmed with GOLD, CRIMSON CLOTH WRAPS on her forearms, DARK PLUM LEGGINGS with SILVER-GOLD SCALE KNEE GUARDS, CLAWED DRAGON FEET, small gold spikes on her shoulders and a LONG CRIMSON SCALY TAIL with a GOLDEN TIP. DRAGON FORM (images 5-8): the same character turned into a BIG CRIMSON DRAGON on four clawed legs: CRIMSON SCALES, TWO LARGE RAISED BAT WINGS (crimson membrane, darker inside, gold horn claws on the wing joints), a BLAZING ORANGE-YELLOW FLAME MANE on the head and neck, DARK CURVED HORNS, a row of IVORY SPIKES along the spine and on the elbows, a TEAL ARMOUR PLATE on the chest, BLACK CLAWS, a long tail with a GOLDEN TIP. (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the breastplate, the wraps, the leggings, the tail; 3 her head close-up: the horn crown, the hair, the eyes; 4 her from the side, facing right - the angle of SA; 5 the dragon's idle, 3/4 view facing right - the look, angle and pose of D; 6 the same from the front: the wings, the mane, the chest plate; 7 the dragon's head close-up: the eye, the horns, the fangs, the mane; 8 the dragon from the side, facing right - the angle of SD; 9 the official illustration: mood and colours.) Images 10a-10d are layout guides: where the character goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a dragon's scales, wings and flames on the grid (11), a big beast's body, dark shades and claws (12), a heroine's face and long hair (13, 14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both forms. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the horns, the tail, the wings, the claws); the soles level on one ground line about 146 px above the bottom edge (the grey line of images 10a-10d), standing where the guide shows the character (the centre). HUMAN is about 484 px (about 44 squares) from the horn tips to her soles; the DRAGON is about 572 px (about 52 squares) from its highest wing tip to its claws, and much longer than she is.
PROPORTIONS: the human is chibi - the head with its horn crown about ONE THIRD of her height, a clear face, a slim body; the dragon is a long heavy beast with a big head, big wings and big claws.
HER FACE: pale lavender; TWO EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, golden-yellow with one white highlight square), golden-orange bangs, the red horns growing back from both sides of her brow.
THE DRAGON'S FACE: a long crimson snout, ONE GLOWING YELLOW EYE clearly visible (at least 2x2 squares), a row of ivory fangs, the jaw slightly open showing a dark magenta mouth, the flame mane on top of the head and along the neck.
THE COLOURS: human - the skin pale lavender in 3 shades, the hair golden-orange in 3-4 shades with YELLOWER LIT EDGES, the horn crown crimson in 3 shades with black tips, the breastplate teal-silver in 3 shades with gold trim in 2, the wraps and the tail crimson in 3-4 shades so they never turn into one red mass, the leggings dark plum in 3 shades, the knee guards silver-gold in 2-3. Dragon - the scales crimson in 3-4 shades with ORANGER LIT EDGES so the body never turns into one red mass, the wing membrane crimson with a darker inside, the flame mane orange-yellow in 3 shades with PALE YELLOW LIT EDGES, the horns and claws black-grey in 2-3 shades, the spikes ivory in 3 shades, the chest plate teal in 2-3 shades, the tail tip gold.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no fireball, no fire breath, no flame shield, no explosions, no sparkles; the dragon's flame mane IS part of its body and is drawn), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (shyvana-A.png): HER idle in 3/4 view facing right (images 1, 2 and 10a) - standing on both clawed feet, the face to the front-right, both arms down at her sides, the tail hanging behind her with its golden tip curling up.
PICTURE SA (shyvana-SA.png): the SAME human as A seen exactly from the SIDE, FACING RIGHT (images 4 and 10b) - the face to the image right with one eye visible, the tail behind her (image left), both soles on the ground line.
PICTURE D (shyvana-D.png): the DRAGON's idle in 3/4 view facing right (images 5, 6 and 10c) - low on its four clawed legs, the head at the front (image right), the face to the front-right, both wings raised, the tail trailing behind.
PICTURE SD (shyvana-SD.png): the SAME dragon as D seen exactly from the SIDE, FACING RIGHT (images 8 and 10d) - the head to the image right with one eye visible, the near wing raised over the back, the tail behind (image left), all claws on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，角、尾巴、翅膀、爪子完整，不出画。
- 人形：Q 版，头连角冠约占身高三分之一；**两只眼睛一样大、一样高**、带白色高光；红色龙角冠、金橙色头发、青银色胸甲金边、深红布条、深紫红护腿、银金护膝、龙爪脚、金色尾尖的长尾巴。
- 龙形：深红鳞片、两只抬起的大翅膀、橙黄色火焰鬃毛、深色弯角、象牙色尖刺、青色胸甲、黑爪、金色尾尖；一只黄色眼睛看得清。
- A / D 是 3/4 正面朝右，SA / SD 是正侧面朝右；人形从角尖到脚底约 484 px（约 44 格），龙形约 572 px（约 52 格），脚底都在地面线上。
- 没有任何技能特效。**每块 11 像素、两种形态大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- 四张都画完后，最后写 `outputs/shyvana-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/shyvana_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

两种形态后面都要做成动作帧（由 Claude 按英雄联盟的动作逐帧拼，必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：人形的手臂、尾巴、角冠；龙形的翅膀（会扇动）、尾巴（会横扫）、头和下巴（会张嘴撕咬）、四条腿。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 人形 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle1 / Run / Attack1、Attack2 / — / Death | 普攻是一记带爪的挥击 |
| **人形 Q 一段：斩击** | Spell1_Attack1 | 连招第 1 段：向前横斩，火焰顺着手臂划出 |
| **人形 Q 二段：横扫** | Spell1_Attack2 | 连招第 2 段（下一次普攻）：转身扫一圈周围 |
| 人形 E：掷火球 | Spell3 | 往前甩出火球 |
| 人形 W：烈火圣盾 | Spell2（只取起手的一下） | 火焰护身，身子略缩再挺起（护盾特效第 3 步另画） |
| **人形 R：变身起跳** | Spell4_Cast | 往前上方跃起、在空中化成龙（变身的光放第 3 步） |
| 龙形 待机 / 跑 / 普攻 / 死亡 | idle1 / Run1 / Attack1 / Death | 普攻是前爪一抓 |
| **龙形 Q 一段：翼击** | Spell1_Wing | 连招第 1 段：用翅膀往前拍 |
| **龙形 Q 二段：尾扫** | Spell1_Tail | 连招第 2 段：转身用尾巴扫一圈 |
| **龙形 Q 三段：撕咬** | Spell1_Bite | 连招第 3 段：伸长脖子张大嘴咬下去 |
| 龙形 E：喷火球 | Spell3 | 仰头再往前喷出大火球 |
| **龙形 R：俯冲落地** | Spell4_Intro → Spell4 | 张开翅膀俯冲、一路喷火，落地后接 W（护盾）和 Q 一段（翼击） |
| 龙变回人 | DragonR_untransform 对应的收翅 | 龙收拢翅膀缩回人形 |

连招一共两条：**Q 三段**（人形：斩击 → 横扫；龙形：翼击 → 尾扫 → 撕咬，每段接在下一次普攻上）和 **R → W → Q**（魔龙降世落地后立刻开烈火圣盾，再接龙形翼击）。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/shyvana/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_zyra_hd.py` 的做法），和已合并的女英雄 / 龙（斯莫德、奈德丽、婕拉、沃利贝尔）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定两种形态的大小（PPU 不要超过 1.5，除非用户要；问用户要不要侧面——沃里克 / 梅尔 / 维克兹用户只要 3/4）。
- 定下后第 1 步按游戏格子重画两种形态的造型，一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Shyvana`（人形）和 `tools/lol/anim_graph.py ShyvanaDragon --wad Shyvana`（龙形，skin 缩放 0.45），渲染时 `pose_ref.py --champ ShyvanaDragon --wad Shyvana`。数据里用到的动作名（`tools/kit/build_shyvana.py`）：人形 `attack` `skill`（Q1）`skill_b`（Q2）`skill2`（E）`ult`（R 变身起跳）`revert`（龙变回人）；龙形 `d_attack` `d_skill`（翼击）`d_skill_b`（尾扫）`d_bite`（撕咬）`d_skill2`（E）；`idle` `run` `hit` `dead` 是人形的（龙形的待机和跑要附加包的显示代码，纳尔的做法）。
