# 愁云使者 薇古丝：第 0 步，先画像素风原图（给 Codex 的提示词）

> 薇古丝是一个**闷闷不乐的约德尔小女孩**：穿一件**又大又厚的深青黑色连帽衫**，兜帽上竖着**两只又高又尖的耳朵**（耳朵里面是紫色，耳根有一撮浅色的绒毛）；兜帽下面是一头**乱糟糟的青绿色短发**，**灰白的皮肤**，**一双品红色的眼睛**、眼皮厚重、半睁着，一脸不高兴（小小的嘴往下撇）；胸口挂着一个**金色的吊坠**；**袖子特别长**，垂下来一直到小腿，**袖口是品红色的交叉绑带**；下身是**蓬松的品红紫色灯笼裤**，绑着几条带子，脚上一双**深色的鞋**。她身后总跟着**她的影子**：一只活的影子，是她最显眼的标志——**墨一样的深蓝黑色**，形状像一个更大、更软的她：圆脑袋上两只**和兜帽一样的尖耳朵**，**两只画出来的发光眼睛**（浅蓝白色的线条眼、中间一个**螺旋形的瞳孔**，附图 6），一双**大大的爪子手**，身子往下收成一缕烟似的尾巴，连在她身后的地上。请 Codex 画**四张全身像**（同一个薇古丝和同一只影子，长相、颜色、**格子大小**都一样），用户从里面挑：
> - **A：英雄联盟里的待机，3/4 正面朝右，影子站起来**（附图 1、2、8a）。她站着，两只长袖垂在身体两边，脸朝右前方；**影子从她身后（画面左边、她背后）的地上立起来**，比她高一点，一只爪子搭在她肩膀上方，像在她背后探出头来。
> - **B：同样的待机，影子躺在地上**。她和 A 一模一样；**影子不站起来**，是她脚后（画面左边）地上一滩**扁扁的深色影子**，只有 2–4 格厚，上面露出那两只发光的线条眼睛（影子站起来的样子留到技能特效里画）。
> - **SA：A 的侧面，朝右**（附图 7、8b）。同一个薇古丝**正侧面朝右**站着（脸朝画面右边，看得见一只眼睛），影子同样从她身后（画面左边）立起来。
> - **SB：B 的侧面，朝右**。同一个薇古丝正侧面朝右，影子是她脚后地上扁扁的一滩。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的波比（约德尔女孩）、佐伊（小女孩）和魔腾（深色的暗影角色），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–5、7）。影子照附图 5（官方加载画面）和附图 6（影子的眼睛）。
> - **比例**：Q 版，**头大**（兜帽连耳朵约占身高的一半，脸本身约占三分之一），身子短、腿细短；不要细长的写实比例。
> - **脸**（附图 3 特写）：灰白的小脸，**两只品红色的眼睛一样大、一样高、都看得见**（每只至少 2×3 格，带一格白色高光），上眼皮厚、半睁着；小嘴往下撇；青绿色的头发盖住额头、从兜帽两边露出来。
> - **颜色**：连帽衫深青黑色（3–4 档，偏青的亮边，**不要糊成一团黑**）；兜帽耳朵内侧紫色；头发青绿色 3 档；灯笼裤和袖口绑带品红紫色 3 档；吊坠金色 2 档；鞋深色。**影子用和连帽衫分得开的颜色**：墨一样的深蓝黑（2–3 档深靛蓝），外边一圈**靛紫色的亮边**，眼睛是平涂的浅蓝白色线条加螺旋瞳孔——影子要一眼看出是"另一个东西"，不能和她的衣服混在一起。
> - **画布用正方形 1536×1536**。**薇古丝从兜帽耳尖到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）；她站在画布中间偏右（附图 8a、8b 的位置），**影子在她左后方**。站起来的影子耳尖约 750 px 高（约 68 格），不能挡住她的脸。耳朵、袖子、影子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（影子也有）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（飞弹、冲击波、暗影奔涌都放到第 3 步单独画；影子的眼睛是它身体的一部分，用平涂的亮色画）；不画地面，不画她自己的投影（**B / SB 里地上那一滩是她的影子这个角色**，不是投影）。
> - 交付：`outputs/vex-picture/vex-A.png`、`vex-B.png`、`vex-SA.png`、`vex-SB.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/vex-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/vex_picture_done.zip`。

## 附图（在压缩包 `vex_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_vex_idle.png` | 英雄联盟原版薇古丝的待机，3/4 朝右（模型里的影子只是地上的贴图，渲染时拿掉了） | 颜色、形状、**角度**、A / B 的姿势 |
| `refs/2_vex_frontal.png` | 同一帧，正面 | 连帽衫、吊坠、长袖、灯笼裤、鞋 |
| `refs/3_vex_head.png` | 头部特写（3/4） | 兜帽的耳朵、头发、脸、眼睛 |
| `refs/4_vex_back.png` | 同一帧的背后 | 兜帽背后、袖子、裤子的带子 |
| `refs/5_vex_splash.png` | 官方加载画面 | 气质、颜色、**影子**的样子 |
| `refs/6_shadow_eyes.png` | 影子眼睛的贴图（各种表情），**用左下角第二个：睁开的眼睛、螺旋瞳孔** | 影子的眼睛 |
| `refs/7_vex_side.png` | 同一帧，侧面朝右 | SA / SB 的角度：兜帽的长度、身子的厚度 |
| `refs/8a_layout_front.png` | A / B 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰）；影子在她左后方 |
| `refs/8b_layout_side.png` | SA / SB 的布局示意 | 同上，侧面 |
| `style/11_style_poppy.png` | 本包的波比，8 倍放大，一格 = 一个像素 | **只看风格**：约德尔女孩的大头、脸、眼睛在格子上怎么画 |
| `style/12_style_zoe.png` | 本包的佐伊（8 倍） | **只看风格**：小女孩的格子密度、描边、头发 |
| `style/13_style_nocturne.png` | 本包的魔腾（8 倍） | **只看风格**：深色的暗影角色怎么分档、怎么留亮边 |

## 提示词：`vex-A.png` / `vex-B.png` / `vex-SA.png` / `vex-SB.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-5 and 7 are 3D renders and art of a character from the game: a SMALL SULLEN YORDLE GIRL in a BIG THICK DARK TEAL-BLACK HOODIE whose hood has TWO TALL POINTED EARS (violet inside, a pale feathery tuft at the base), MESSY TEAL HAIR over GREY-PALE SKIN, MAGENTA EYES with heavy half-closed lids, a small down-turned mouth, a GOLD PENDANT on her chest, SLEEVES FAR TOO LONG hanging down to her shins with MAGENTA CROSS-LACES at the cuffs, PUFFY MAGENTA-PURPLE TROUSERS with straps, dark shoes (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A and B; 2 the same from the front: the hoodie, the pendant, the sleeves, the trousers, the shoes; 3 the head close-up: the hood with its ears, the hair, the face, the eyes; 4 the same from behind; 5 the official illustration: her mood, her colours and HER SHADOW; 7 the idle from the side, facing right - the angle of SA and SB). Her SHADOW follows her everywhere, a living shadow and her signature: an INK-DARK BLUE-BLACK creature shaped like a bigger, softer silhouette of her in the hood - a round head with TWO POINTED EARS like her hood's, TWO DRAWN GLOWING EYES (pale blue-white line-drawn eyes with a SPIRAL PUPIL: image 6, the open eye, second picture of its bottom row), TWO BIG CLAWED HANDS, its body narrowing into a wisp of smoke joined to the ground behind her. Images 8a and 8b are layout guides: where SHE goes on the canvas and how big, the grey line is the ground; her Shadow goes behind her, on the image LEFT. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a yordle girl's big head, face and eyes on the grid (11), a small girl's square density and outline (12), a dark shadowy character's shades and lit edges (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (both ears, both sleeves, the whole Shadow); her soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). She is about 660 px (about 60 squares) from her hood's ear tips to her soles and stands where images 8a / 8b show her (a little right of the centre).
PROPORTIONS: chibi - the hood with its ears about HALF her height, her face about a third; a short body, short slim legs; NOT realistic slim proportions.
THE FACE: small, grey-pale; TWO MAGENTA EYES of the SAME size at the SAME height, both visible (each at least 2x3 squares, with one white highlight square), heavy upper lids, half-closed, bored; a small down-turned mouth; the teal hair over her forehead and out of both sides of the hood.
THE COLOURS: the hoodie dark teal-black in 3-4 shades with LIGHTER TEAL EDGES so it never turns into one dark mass; the inside of the ears violet; the hair teal in 3 shades; the trousers and the cuff laces magenta-purple in 3 shades; the pendant gold in 2 shades; dark shoes. THE SHADOW in colours clearly apart from her hoodie: ink-dark blue-black (2-3 very dark indigo shades) with an INDIGO-VIOLET RIM along its edge, its eyes flat pale blue-white lines with a spiral pupil - at a glance it must read as a SECOND BEING, never mixed into her clothes.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her and around the Shadow; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the teal-black hoodie, the violet ear insides, the teal hair, the pale skin, the magenta eyes, the gold pendant, the magenta trousers and laces, the dark shoes and the blue-black Shadow clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no bolts, no shock waves, no dashes, no sparkles), no background, no ground plane, no cast shadow of her own (the dark pool of B and SB IS the Shadow character), no text, no frame, no other characters.
PICTURE A (vex-A.png): her idle in 3/4 view facing right (images 1, 2 and 8a) - standing, both long sleeves hanging at her sides, the face to the front-right; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker; HER SHADOW RISEN behind her (on the image left, at her back), a little taller than her (its ear tips about 750 px, about 68 squares, above the ground line), one big clawed hand raised over her near shoulder as if looming over her, its eyes glowing; it never covers her face.
PICTURE B (vex-B.png): the SAME Vex in the SAME idle, 3/4 view facing right; HER SHADOW NOT RISEN: it lies FLAT on the ground behind her feet (stretching to the image left), a thin dark pool only 2-4 squares thick, about as long as she is tall, its two glowing line-drawn eyes peeking out of it.
PICTURE SA (vex-SA.png): the SAME Vex seen exactly from the SIDE, FACING RIGHT (images 7 and 8b) - the face to the image right with one eye visible, both sleeves hanging, both soles on the ground line; HER SHADOW RISEN behind her (on the image left), the same as in A.
PICTURE SB (vex-SB.png): the SAME Vex exactly from the SIDE, FACING RIGHT (images 7 and 8b); HER SHADOW lying FLAT behind her feet as in B.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，耳朵、袖子、影子完整，不出画。
- Q 版：兜帽连耳朵约占身高一半；**两只品红色眼睛一样大、一样高**、带白色高光、半睁着；小嘴往下撇；青绿色头发。
- 深青黑连帽衫（有偏青的亮边，不糊成一团）、耳朵内侧紫色、金吊坠、长到小腿的袖子和品红色交叉绑带、品红紫灯笼裤、深色鞋。
- 影子：深蓝黑、靛紫亮边、两只浅蓝白线条眼带螺旋瞳孔、尖耳朵、大爪子手，一眼看得出是另一个东西；A / SA 站在她左后方、不挡脸；B / SB 是她脚后扁扁的一滩。
- A / B 是 3/4 正面朝右，SA / SB 是正侧面朝右；四张都是从兜帽耳尖到脚底约 660 px（约 60 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- 四张都画完后，最后写 `outputs/vex-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/vex_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/vex/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_zoe_hd.py` 的做法，绝不按更少的行采样），和已合并的中单、小个子女孩（波比、佐伊、卡西奥佩娅、吉格斯、璐璐）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑影子站着还是躺着、定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画 3/4 正面和**侧面朝右**（动作都用侧面），一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Vex`）：普攻 Attack_1 / Attack_2（接 _Hit），被动强化的普攻 Attack_Passive；Q Spell1；W Spell2；E Spell3；R Spell4_Cast（扔出去）、Spell4_Dash（冲过去）、Spell4_Attack；跑 run_base = Run.anm；死亡 Death。影子在模型里只是地上的贴图，技能里站起来的影子是粒子特效：第 3 步画。
