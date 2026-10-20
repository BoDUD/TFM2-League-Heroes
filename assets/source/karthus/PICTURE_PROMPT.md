# 死亡颂唱者 卡尔萨斯：第 0 步，先画像素风原图（给 Codex 的提示词）

> 卡尔萨斯是一个**又高又瘦的巫妖**：灰绿色的死人皮紧紧包着骷髅脸，**两只发光的青色眼睛**，下巴张着、像在唱歌；头上一顶**又高又尖的深钢色主教冠**，中间嵌着**深红色**的条纹，冠下垂出深红色的头发；肩上一对**又大又弯的深钢色肩甲**，镶着**发光的青色宝石**；身上是**深红色的长袍**，外面罩着好几层**撕成一条条的深紫色破布**，一直拖到地上，胸前垂下两条紫色的长带，腰带上有一个小骷髅；**两只灰白发绿的骨爪手**；袍子底下露出**光着的骷髅脚**；一只手握着一根**比他还高的深钢色法杖**，杖头是**青色水晶的矛尖**，下面一圈**深红色的尖刺护环**。请 Codex 画**四张全身像**（同一个卡尔萨斯，长相、颜色、**格子大小**都一样），用户从里面挑：
> - **A：英雄联盟里的待机，3/4 正面朝右，法杖照原版那么长**（附图 1、2、8a）。他微微驼背站着，远侧（画面右边）的手握着法杖、法杖竖直立在身边，杖尖比冠尖高出约 14 格；近侧（画面左边）的骨爪手垂在身侧、手指弯着。
> - **B：同样的待机，法杖短一些**。他和 A 一模一样，只是法杖缩短：**杖尖只比冠尖高 3–4 格**，杖底还在地面上（这样精灵图更紧凑）。
> - **SA：A 的正侧面，朝右**（附图 7、8b）。同一个卡尔萨斯**正侧面朝右**站着（脸朝画面右边，看得见一只眼睛），法杖照 A 的长度。
> - **SB：B 的正侧面，朝右**。法杖照 B 的长度。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的玛尔扎哈（穿袍子的法师）、斯维因（长大衣、深色调）和泽拉斯（发光的法师），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–5、7）。
> - **比例**：Q 版，**头连主教冠约占身高的三分之一**，脸要大到看得清眼睛；身子瘦长、肩甲宽；不要细长的写实比例。
> - **脸**（附图 3 特写）：灰绿色的骷髅脸，**两只青色的发光眼睛一样大、一样高、都看得见**（每只至少 2×2 格，中间一格最亮的浅青白色），深陷的眼窝；张开的下巴露出几颗白牙。
> - **颜色**：主教冠和肩甲深钢灰色（3–4 档，偏青的亮边，**不要糊成一团黑**），冠上的条纹深红色；青色宝石和眼睛用平涂的亮青色（带一格浅青白高光）；长袍深红色 3 档；外面的破布和胸前长带深紫色 3 档（和深红分得开）；皮肤和骨爪灰绿色 3 档；法杖深钢色，杖头青色水晶、护环深红色。
> - **画布用正方形 1536×1536**。**卡尔萨斯从冠尖到脚底约 704 px，也就是约 64 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线），站在画布中间（附图 8a、8b 的位置）。法杖、破布、肩甲全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（法杖也有）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（爆炸、墙、灵魂、光芒都放到第 3 步单独画；眼睛和宝石的光是他身上的颜色，用平涂的亮色画，不要外发光）；不画地面，不画投影。
> - 交付：`outputs/karthus-picture/karthus-A.png`、`karthus-B.png`、`karthus-SA.png`、`karthus-SB.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/karthus-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/karthus_picture_done.zip`。

## 附图（在压缩包 `karthus_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_karthus_idle.png` | 英雄联盟原版卡尔萨斯的待机，3/4 朝右 | 颜色、形状、**角度**、A / B 的姿势 |
| `refs/2_karthus_frontal.png` | 同一帧，正面 | 主教冠、肩甲、长袍、破布、长带、腰带 |
| `refs/3_karthus_head.png` | 头部特写（3/4） | 主教冠、脸、眼睛、下巴 |
| `refs/4_karthus_back.png` | 同一帧的背后 | 冠和肩甲的背后、破布 |
| `refs/5_karthus_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/7_karthus_side.png` | 同一帧，侧面朝右 | SA / SB 的角度：冠的形状、肩甲、身子的厚度、法杖的位置 |
| `refs/8a_layout_front.png` | A / B 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰线）、冠尖的高度（浅灰线） |
| `refs/8b_layout_side.png` | SA / SB 的布局示意 | 同上，侧面 |
| `style/11_style_malzahar.png` | 本包的玛尔扎哈，8 倍放大，一格 = 一个像素 | **只看风格**：长袍、深色布料怎么分档 |
| `style/12_style_swain.png` | 本包的斯维因（8 倍） | **只看风格**：瘦高的人形、深色衣服的亮边、脸 |
| `style/13_style_xerath.png` | 本包的泽拉斯（8 倍） | **只看风格**：发光的青色怎么用平涂画 |

## 提示词：`karthus-A.png` / `karthus-B.png` / `karthus-SA.png` / `karthus-SB.png`（同一段提示词，只换最后一句）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-5 and 7 are 3D renders and art of a character from the game: a TALL GAUNT LICH with grey-green dead skin drawn tight over a SKULL FACE, TWO GLOWING CYAN EYES in deep sockets and an OPEN SINGING JAW with a few white teeth, under a TALL POINTED DARK-STEEL MITRE CROWN with CRIMSON inlays and crimson hair hanging below it; HUGE CURVED DARK-STEEL PAULDRONS studded with GLOWING CYAN GEMS; a long DEEP CRIMSON ROBE under layers of TORN DARK VIOLET CLOTH that hang to the ground in ragged strips, two violet stoles down the front, a belt with a small skull; BONY PALE GREY-GREEN CLAWED HANDS; bare skeletal feet under the robe; in his far hand a TALL DARK-STEEL STAFF, taller than he is, with a CYAN CRYSTAL SPEAR-HEAD and a spiked CRIMSON COLLAR below it (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A and B; 2 the same from the front: the crown, the pauldrons, the robe, the torn cloth, the stoles, the belt; 3 the head close-up: the crown, the face, the eyes, the jaw; 4 the same from behind; 5 the official illustration: his mood and colours; 7 the idle from the side, facing right - the angle of SA and SB). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground, the light grey line the height of his crown tip. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a robed mage's dark cloth in shades (11), a tall figure in a dark coat with lit edges and a readable face (12), glowing cyan drawn as flat bright squares (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the whole staff, both pauldrons, the torn cloth); his soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 704 px (about 64 squares) from the tip of his crown to his soles and stands where images 8a / 8b show him (in the middle).
PROPORTIONS: chibi - the head with the crown about a THIRD of his height, the face big enough that both eyes read clearly; a slim body under wide pauldrons, a little hunched; NOT realistic slim proportions.
THE FACE: a grey-green skull face; TWO GLOWING CYAN EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares with a pale cyan-white centre square), deep dark sockets; the open jaw with a few white teeth.
THE COLOURS: the crown and the pauldrons dark steel grey in 3-4 shades with LIGHTER TEAL-GREY EDGES so they never turn into one dark mass; the crown's inlays crimson; the gems and the eyes flat bright cyan with one pale cyan-white square; the robe deep crimson in 3 shades; the torn cloth and the stoles dark violet in 3 shades, clearly apart from the crimson; the skin and the bony hands grey-green in 3 shades; the staff dark steel with a cyan crystal head and a crimson collar.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him and around the staff; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the steel crown and pauldrons, the crimson robe, the violet cloth, the grey-green skin, the cyan eyes and gems and the staff clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no blasts, no walls, no souls, no glow around him), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (karthus-A.png): his idle in 3/4 view facing right (images 1, 2 and 8a) - standing a little hunched, the FAR hand (image right) holding the staff upright beside him, its foot on the ground and its tip about 14 squares above his crown tip as in League; the NEAR hand (image left) hanging at his side with bent claw fingers; the NEAR side of the body on the image left in full tone, the FAR side a step darker.
PICTURE B (karthus-B.png): the SAME Karthus in the SAME idle, 3/4 view facing right; the staff SHORTER: its foot still on the ground, its crystal tip only 3-4 squares above his crown tip; everything else exactly as in A.
PICTURE SA (karthus-SA.png): the SAME Karthus seen exactly from the SIDE, FACING RIGHT (images 7 and 8b) - the face to the image right with one eye visible, the staff held upright in front of him at League's length (its tip about 14 squares above his crown), the torn cloth hanging behind; his soles on the ground line.
PICTURE SB (karthus-SB.png): the SAME Karthus exactly from the SIDE, FACING RIGHT (images 7 and 8b); the staff shortened as in B (its tip only 3-4 squares above his crown).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，法杖、肩甲、破布完整，不出画。
- Q 版：头连主教冠约占身高三分之一；**两只青色眼睛一样大、一样高**、中间有浅青白的亮格；张开的下巴有白牙。
- 深钢色主教冠（深红条纹）和大肩甲（青色宝石、偏青的亮边，不糊成一团）；深红长袍、深紫破布和长带（两种颜色分得开）；灰绿骨爪手；法杖：青色水晶矛尖、深红护环。
- A / SA 的杖尖比冠尖高约 14 格，B / SB 只高 3–4 格；A / B 是 3/4 正面朝右，SA / SB 是正侧面朝右；四张都是从冠尖到脚底约 704 px（约 64 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 四张都画完后，最后写 `outputs/karthus-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/karthus_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/karthus/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_zoe_hd.py` 的做法，绝不按更少的行采样），和已合并的法师（玛尔扎哈、斯维因、泽拉斯、维克托）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑长杖还是短杖、定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画 3/4 正面和**侧面朝右**（动作都用侧面），一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Karthus`）：普攻 attack1 / attack2；Q Spell1a / Spell1_b / Spell1_c；W Spell2；E spell3；R spell4（Spell4_In）+ spell4_loop（引导 3 秒）；跑 run_base = karthus_run.anm；死亡 death；死后的灵体 Karthus_Passive_Idle / Passive_Spell1 / Passive_Spell2 / Passive_Spell4。
