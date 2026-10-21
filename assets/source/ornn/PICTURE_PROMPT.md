# 山脊之下的火焰 奥恩：第 0 步，先画像素风原图（给 Codex 的提示词）

> 奥恩是一个**巨大、驼背的半神铁匠**（羊角的神）：**皮肤是灰蓝 / 淡紫灰色**，**肩膀和手臂粗壮得夸张**；头上一对**非常大的盘曲羊角**——羊角是**深铁灰色**，表面刻着**暗红色的回纹符文槽**，**角尖是发光的红橙色**，从额头往上、往两边盘一大圈；**一大蓬深红色（偏玫红）的蓬乱鬃毛和大胡子**把脸围住、一直披到肩上，胡子两边垂着**几束编起来的小辫，扎着钢环、钢环上嵌着红色的小宝石**，**一双发光的红橙色眼睛**，深色的羊鼻；胸前是**一块青铜色的胸甲，上面铸着一对盘起来的羊角花纹**，**深棕色的皮背带**从肩上交叉下来，肩上是**青铜色的大方扣**；腰上一条**宽皮带**，挂着**一把铁钳**等锻造工具，前面垂着**深紫红色的皮围裙**；腿**短而粗**，穿**深紫红色的靴子 / 护腿**。**近侧的手臂**戴着**很大的青铜护肩和皮护腕**，手里低低握着**大锻造锤**（**钢青色 / 灰蓝色的方形大锤头**，像个小铁砧，深色锤柄）；**远侧的手臂从肘部往下是熔岩**：灰蓝的皮肤上爬满**发光的红橙色裂纹**，**拳头整个烧得通红**，手里握着**一把小一些的钢锤**。他的待机：**身子前倾、驼着背、两腿分开站稳**，两把锤子都垂在身体两侧低处。请 Codex 画**两张全身像**（同一个奥恩，长相、颜色、**格子大小**都一样），都是 **3/4 正面朝右**（**不画正侧面**），用户从里面挑：
> - **A：英雄联盟里的待机和比例**（附图 1、2、8a）：羊角照原版那么大、往两边盘开，两把锤子照原版大小。
> - **B：同样的待机，更紧凑**：**羊角盘得更紧、贴着头**（不往两边伸那么远），**两把锤子都小一号**（锤头大约是 A 的三分之二），整个人更窄。长相、颜色和 A 一模一样。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的沃利贝尔（巨大的毛茸茸的半神）、古拉加斯（大块头）和科加斯（大怪物），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：Q 版，**头（连鬃毛、胡子，不算羊角）约占身高的三分之一**，脸要大到看得清眼睛；身子**宽而厚、驼背**，手臂粗壮，腿**短**；不要细长的写实比例。
> - **脸**（附图 3 特写）：**两只发光的眼睛一样大、一样高、都看得见**（每只至少 2 格，红橙色，带一格亮黄的高光），浓眉压低，深色的鼻子；深红鬃毛和胡子**分 3 档**（亮边偏橙红，不要糊成一块红），两边的小辫和钢环看得出来。
> - **颜色**：灰蓝 / 淡紫灰皮肤 3 档（**不要发绿、不要变成纯灰**）；羊角深铁灰 3 档 + 暗红符文槽 + 红橙角尖 2 档；深红鬃毛 / 胡子 3 档；青铜胸甲、护肩、方扣 3 档；深棕皮背带、皮带 2 档；深紫红围裙和靴子 2–3 档（**有偏亮的边，不要一团黑**）；远侧熔岩手臂的红橙裂纹和通红的拳头 3 档（最亮一档偏黄）；锤头钢青色 3 档、锤柄深色 2 档。
> - **画布用正方形 1536×1536**。**奥恩从羊角最高处到脚底约 726 px，也就是约 66 格**，脚底在离画布底边约 146 px 的地方（附图 8a 的灰线），站在附图 8a 的位置。羊角、锤子、整个身子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（锤子、羊角也有）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（锤子上的火花、喷火、熔岩柱、公羊都放到第 3 步单独画）；熔岩手臂是他身体本身的颜色，照画，但**不要往外发光、不要光晕**；不画地面，不画投影。
> - 交付：`outputs/ornn-picture/ornn-A.png`、`ornn-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/ornn-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/ornn_picture_done.zip`。

## 附图（在压缩包 `ornn_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ornn_idle.png` | 英雄联盟原版奥恩的待机，3/4 朝右 | 颜色、形状、**角度**、待机姿势 |
| `refs/2_ornn_frontal.png` | 同一帧，正面 | 羊角、鬃毛、青铜胸甲、背带、腰带和铁钳、围裙、腿、两把锤 |
| `refs/3_ornn_head.png` | 头部特写（3/4） | 羊角、符文、鬃毛、脸、眼睛、胡子、小辫和钢环 |
| `refs/4_ornn_back.png` | 同一帧的背后 | 背带、腰带、熔岩手臂、羊角的背面 |
| `refs/5_ornn_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_ornn_slam.png` | 举锤砸地的一帧，3/4 朝右 | 大锤的样子、近侧的手怎么握锤、熔岩拳头举过头顶 |
| `refs/7_ornn_side.png` | 待机，侧面朝右 | 身子的厚度、驼背、羊角怎么往后盘（**只作参考，不画侧面**） |
| `refs/8a_layout_front.png` | 布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰线）、羊角最高处（浅灰线） |
| `style/11_style_volibear.png` | 本包的沃利贝尔，8 倍放大，一格 = 一个像素 | **只看风格**：巨大的半神、毛发、发光的眼睛在格子上怎么画 |
| `style/12_style_gragas.png` | 本包的古拉加斯（8 倍） | **只看风格**：宽厚的大块头、胡子、皮带 |
| `style/13_style_chogath.png` | 本包的科加斯（8 倍） | **只看风格**：驼背的大怪物、深色身体的亮边 |

## 提示词：`ornn-A.png` / `ornn-B.png`（同一段提示词，只换最后一句）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-7 are 3D renders and art of a character from the game: a HUGE HUNCHED RAM-HORNED DEMIGOD BLACKSMITH with SLATE BLUE-GREY (lavender-grey) SKIN and enormously thick shoulders and arms - two ENORMOUS CURLED RAM HORNS of DARK IRON GREY with DARK RED RUNE GROOVES and GLOWING RED-ORANGE TIPS, curling up and out from his brow; a big SHAGGY CRIMSON (rose-red) MANE AND BEARD round the face and over the shoulders, small BRAIDS at the sides of the beard tied with STEEL RINGS set with little red gems, TWO GLOWING RED-ORANGE EYES and a dark ram nose; a BRONZE CHEST PLATE cast with a pair of curled ram horns; DARK BROWN LEATHER HARNESS STRAPS over the shoulders with BIG BRONZE SQUARE BUCKLES; a wide leather belt with a pair of iron TONGS hanging from it and a DARK PLUM LEATHER APRON in front; SHORT THICK legs in dark plum boots; the NEAR arm with a BIG BRONZE PAULDRON and a leather bracer, its hand holding his BIG FORGE HAMMER low: a square STEEL-BLUE (grey-blue) hammer head like a small anvil on a dark handle; the FAR arm MOLTEN from the elbow down - glowing red-orange cracks over the blue-grey skin and a RED-HOT FIST - holding a SMALLER STEEL HAMMER (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose; 2 the same from the front: the horns, the mane, the bronze chest plate, the straps, the belt and tongs, the apron, the legs, both hammers; 3 the head close-up: the horns and their runes, the mane, the face, the eyes, the beard and its braids; 4 the same from behind: the straps, the belt, the molten arm and the backs of the horns; 5 the official illustration: his mood and colours; 6 a frame of his hammer slam, 3/4 view: the big hammer, how the near hand holds it, the molten fist raised; 7 the idle from the side: the depth of the body, the hunch, how the horns curl back - reference only, do NOT draw a side view). Image 8a is a layout guide: where he goes on the canvas and how big, the grey line is the ground, the light grey line the top of his horns. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a huge furry demigod with glowing eyes on the grid (11), a broad heavy body, a beard and straps (12), a hunched monster with lit edges on a dark body (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (both horns, the hammer, the whole body, both feet); his soles level on one ground line about 146 px above the bottom edge (the grey line of image 8a). He is about 726 px (about 66 squares) from the top of his horns to his soles and stands where image 8a shows him.
THE VIEW: 3/4 front, FACING RIGHT (image 1) - NOT a side view, NOT a front view; the NEAR side of the body on the image left in full tone, the FAR side a step darker.
THE POSE: his idle (image 1): leaning forward, the back hunched, the legs apart and planted, a hammer hanging low at each side (the big one in the near hand, the smaller one in the molten far hand).
PROPORTIONS: chibi - the head with the mane and beard (not counting the horns) about a THIRD of his height, the face big enough that both eyes read clearly; a WIDE, DEEP, HUNCHED body with thick arms; SHORT legs; NOT realistic proportions.
THE FACE: TWO GLOWING EYES of the SAME size at the SAME height, both visible (each at least 2 squares, red-orange with one bright yellow highlight square); heavy low brows; a dark nose; the crimson mane and beard in 3 shades with orange-red lit edges (never one red blob), the side braids and steel rings readable.
THE COLOURS: the slate blue-grey skin in 3 shades (never greenish, never plain grey); the horns dark iron grey in 3 shades with dark red rune grooves and red-orange tips in 2 shades; the crimson mane and beard in 3 shades; bronze (chest plate, pauldron, buckles) in 3 shades; the dark brown leather straps and belt in 2 shades; the dark plum apron and boots in 2-3 shades with LIGHTER EDGES (never one black mass); the molten far arm's red-orange cracks and red-hot fist in 3 shades (the brightest yellowish); the hammer heads steel-blue in 3 shades, the handles dark in 2 shades.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him, round the horns and round the hammers; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the blue-grey skin, the iron horns, the crimson mane, the bronze, the leather, the plum apron and boots, the molten arm and the steel hammers clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no sparks, no fire breath, no lava pillar, no glow or halo round the molten arm), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (ornn-A.png): his idle as in League (images 1, 2 and 8a) - the horns as big as League's, curling wide to both sides; both hammers at League's size.
PICTURE B (ornn-B.png): the SAME Ornn in the SAME idle, 3/4 view facing right, more COMPACT: the horns curled TIGHTER round the head (they do not reach out so far to the sides), both hammers one size smaller (their heads about two thirds of A's), so the whole figure is narrower; everything else (look, colours, square size, the pose) exactly as in A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，羊角、锤子、身子、脚完整，不出画。
- 两张都是 **3/4 正面朝右**（不是侧面、不是正面）；驼背前倾、两腿分开站稳、两把锤子垂在身体两侧低处（大锤在近侧手里，小锤在远侧熔岩手里）。
- Q 版：头连鬃毛胡子约占身高三分之一（不算羊角）；**两只发光的眼睛一样大、一样高**；深红鬃毛分档。
- 灰蓝皮肤、深铁灰羊角（暗红符文、红橙角尖）、深红鬃毛胡子（小辫和钢环）、青铜羊角胸甲和护肩、皮背带青铜方扣、腰带和铁钳、深紫红围裙和靴子（有亮边）、远侧熔岩手臂和通红的拳头、两把钢青锤头；两张都是从羊角最高处到脚底约 726 px（约 66 格），脚底在地面线上。
- A 的羊角照原版往两边盘开；B 的羊角贴着头、两把锤子都小一号。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 两张都画完后，最后写 `outputs/ornn-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ornn_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/ornn/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_mel_hd.py` 的做法），和已合并的大块头上单（纳尔巨型、沃利贝尔、科加斯、古拉加斯）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑 A 还是 B、定大小（PPU 不要超过 1.5），再问动作是我自己照英雄联盟摆，还是 Codex 照骨架画关键姿势。
- 只做 3/4 正面（照最近几个英雄）：第 1 步只在游戏格子上画 3/4 正面，动作都在 3/4 的造型上摆；一张脸用在所有帧。渲染时加 `--hide-submeshes`（皮肤里挂着被动锻造用的道具：木桶、剑、熔炉，不藏会盖住他）。英雄联盟的动作（`tools/lol/anim_graph.py Ornn`）：普攻 Attack1 / attack2 / attack3 / Crit、Q spell1（火山裂隙，抡锤砸地）、W Spell2 + spell2_attack（风箱烈息，喷火）、E spell3 → spell3_dash → spell3_hit（灼热冲撞）、R spell4_windup → spell4（召唤）、spell4_charge → spell4_hit（第二段头槌）、跑 Run、死亡 death。连招动作（Q→E 撞柱、R 两段头槌）的分帧另列在第 2 步的提示词里。
