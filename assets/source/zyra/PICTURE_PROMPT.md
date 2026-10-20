# 荆棘之兴 婕拉：第 0 步，先画像素风原图（给 Codex 的提示词）

> 婕拉是一个**高挑纤细的植物女人**：头上是**一大蓬往后甩的深红-品红色头发**，一缕缕像厚厚的花瓣，尖端翘起；头顶两侧竖着**两只黄绿色的叶片角**（里面是紫色）；**浅奶油偏绿的皮肤**，**一双发光的琥珀色眼睛**、深色眼影、深色嘴唇，脸颊上一个小小的漩涡花纹；脖子上一圈**深紫色的项圈，中间一颗粉红色的宝石**；胸前是**绿色叶片做的抹胸**，腰下是**绿色叶片短裤**；**两条长腿是深紫色带刺的藤**，腿外侧一排**尖尖的深紫色刺叶**，脚是**深紫色带爪的光脚**；肩膀上各有**一丛品红色的尖刺**；小臂裹着**深紫色的藤蔓护手**，上面长着**粉红色的刺**，**爪子一样的手**；**每只手腕上垂出一根细细的品红色鞭藤**，弯弯的，尖端是一个**矛尖**。她的标志是植物，不过**种子、食人花、藤蔓这些都放到第 3 步特效里画**，这一步只画她本人。请 Codex 画**四张全身像**（同一个婕拉，长相、颜色、**格子大小**都一样），用户从里面挑：
> - **A：英雄联盟里的待机，3/4 正面朝右**（附图 1、2、7a）。她站着，两腿分开，两只手张在身体两边、爪子微微弯着，两根鞭藤从手腕垂下来弯向外面；头发是英雄联盟里那一大蓬。
> - **B：同样的待机，头发收紧一点，鞭藤短一点**。和 A 一模一样，只是那一蓬头发**往后收、不那么宽**（还是很显眼的一大蓬红发），两根鞭藤**短短地绕在手腕上**，不往外甩。
> - **SA：A 的侧面，朝右**（附图 6、7b）。同一个婕拉**正侧面朝右**站着（脸朝画面右边，看得见一只眼睛），头发甩在背后（画面左边）。
> - **SB：B 的侧面，朝右**。同一个婕拉正侧面朝右，头发收紧、鞭藤短。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的莫甘娜、伊莉丝（细长带刺的女人）和奈德丽（一大蓬头发的女人），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–6）。
> - **比例**：Q 版，**头大**（头连头发约占身高的三分之一，脸本身清楚），身子短、腿还是细长一点（她是高挑的植物女人），不要写实的八头身。
> - **脸**（附图 3 特写）：浅奶油偏绿的小脸，**两只琥珀色的眼睛一样大、一样高、都看得见**（每只至少 2×2 格，亮黄色，带一格更亮的高光），深色眼影、深色嘴唇；红发从额头两边垂下来。
> - **颜色**：头发深红-品红 3–4 档（亮边偏粉，**不要糊成一团红**）；叶片角黄绿色 2–3 档、里面紫色；皮肤浅奶油偏绿 3 档；抹胸和短裤叶绿色 3 档、叶脉深绿；腿和护手深紫色 3 档（偏紫的亮边，**不要糊成一团黑**）；肩刺、护手上的刺、鞭藤品红-粉红 3 档；项圈深紫、宝石粉红。
> - **画布用正方形 1536×1536**。**婕拉从头发顶到脚底约 726 px，也就是约 66 格**，脚底在离画布底边约 146 px 的地方（附图 7a、7b 的灰线）；她站在画布中间（附图 7a、7b 的位置）。头发、手、鞭藤全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（种子、植物、藤蔓、花粉都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/zyra-picture/zyra-A.png`、`zyra-B.png`、`zyra-SA.png`、`zyra-SB.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/zyra-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/zyra_picture_done.zip`。

## 附图（在压缩包 `zyra_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zyra_idle.png` | 英雄联盟原版婕拉的待机，3/4 朝右 | 颜色、形状、**角度**、A / B 的姿势 |
| `refs/2_zyra_frontal.png` | 同一帧，正面 | 抹胸、短裤、腿上的刺叶、护手 |
| `refs/3_zyra_head.png` | 头部特写（3/4） | 头发、叶片角、脸、眼睛、项圈 |
| `refs/4_zyra_back.png` | 同一帧的背后 | 头发背后、肩刺、腿的背面 |
| `refs/5_zyra_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_zyra_side.png` | 同一帧，侧面朝右 | SA / SB 的角度：头发往后甩多长、身子的厚度 |
| `refs/7a_layout_front.png` | A / B 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰） |
| `refs/7b_layout_side.png` | SA / SB 的布局示意 | 同上，侧面 |
| `style/11_style_morgana.png` | 本包的莫甘娜，8 倍放大，一格 = 一个像素 | **只看风格**：女法师的脸、眼睛在格子上怎么画 |
| `style/12_style_elise.png` | 本包的伊莉丝（8 倍） | **只看风格**：细长、带刺的女人怎么画，深色怎么分档 |
| `style/13_style_nidalee.png` | 本包的奈德丽（8 倍） | **只看风格**：一大蓬头发的格子密度、描边 |

## 提示词：`zyra-A.png` / `zyra-B.png` / `zyra-SA.png` / `zyra-SB.png`（同一段提示词，只换最后一句）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-6 are 3D renders and art of a character from the game: a TALL SLENDER PLANT WOMAN with a HUGE MANE OF CRIMSON-MAGENTA HAIR made of thick petal-like strands swept back, their tips curling up; TWO YELLOW-GREEN LEAF HORNS on her head (violet inside); PALE CREAM-GREEN SKIN; GLOWING AMBER EYES with dark lids, dark lips, a small swirl mark on her cheek; a DARK PURPLE CHOKER with a PINK GEM; a GREEN LEAF BODICE and LEAFY GREEN SHORTS; LONG DARK PURPLE THORNY LEGS with a row of SPIKY DARK PURPLE LEAVES down their outer side and CLAWED DARK PURPLE BARE FEET; a cluster of MAGENTA THORN SPIKES on each shoulder; DARK PURPLE VINE GAUNTLETS on her forearms studded with PINK THORNS; CLAWED HANDS; from each wrist a THIN MAGENTA WHIP-VINE curling outward and ending in a SPEAR TIP (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A and B; 2 the same from the front: the bodice, the shorts, the leaves on the legs, the gauntlets; 3 the head close-up: the mane, the leaf horns, the face, the eyes, the choker; 4 the same from behind; 5 the official illustration: her mood and colours; 6 the idle from the side, facing right - the angle of SA and SB). Images 7a and 7b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a woman mage's face and eyes on the grid (11), a slim spiky woman and her dark shades (12), a big mane of hair on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the whole mane, both hands, both whip-vines); her soles level on one ground line about 146 px above the bottom edge (the grey line of images 7a and 7b). She is about 726 px (about 66 squares) from the top of her hair to her soles and stands where images 7a / 7b show her (the centre).
PROPORTIONS: chibi - the head with its hair about a THIRD of her height, a clear face; a short body; the legs still a little long and slim (she is a tall plant woman); NOT realistic slim proportions.
THE FACE: small, pale cream-green; TWO AMBER EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, bright yellow-amber with one lighter highlight square), dark lids, dark lips; red hair falling on both sides of the forehead.
THE COLOURS: the hair crimson-magenta in 3-4 shades with PINKER LIT EDGES so it never turns into one red mass; the leaf horns yellow-green in 2-3 shades, violet inside; the skin pale cream-green in 3 shades; the bodice and the shorts leaf green in 3 shades with dark green veins; the legs and the gauntlets dark purple in 3 shades with VIOLET LIT EDGES so they never turn into one dark mass; the shoulder spikes, the gauntlet thorns and the whip-vines magenta-pink in 3 shades; the choker dark purple, its gem pink.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the red hair, the yellow-green leaf horns, the pale skin, the amber eyes, the green leaves, the dark purple legs and gauntlets, the magenta thorns and whips clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no seeds, no plants, no vines from the ground, no pollen, no sparkles), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (zyra-A.png): her idle in 3/4 view facing right (images 1, 2 and 7a) - standing with her legs apart, both clawed hands held out at her sides, the face to the front-right; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker; League's full mane; the two whip-vines hanging from her wrists and curling outward.
PICTURE B (zyra-B.png): the SAME Zyra in the SAME idle, 3/4 view facing right; her mane drawn TIGHTER, swept back and less wide (still a big striking red mane); the whip-vines SHORT, curled round her wrists, not swinging out.
PICTURE SA (zyra-SA.png): the SAME Zyra as A seen exactly from the SIDE, FACING RIGHT (images 6 and 7b) - the face to the image right with one eye visible, the mane swept back behind her (image left), both soles on the ground line, the hands and whip-vines as in A.
PICTURE SB (zyra-SB.png): the SAME Zyra as B exactly from the SIDE, FACING RIGHT (images 6 and 7b); the tighter mane and the short curled whip-vines of B.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、手、鞭藤完整，不出画。
- Q 版：头连头发约占身高三分之一；**两只琥珀色眼睛一样大、一样高**、带高光；深色嘴唇；红发、两只黄绿叶片角。
- 深红-品红的头发（有偏粉的亮边，不糊成一团）、浅奶油偏绿的皮肤、深紫项圈和粉宝石、绿叶抹胸和短裤、深紫带刺叶的长腿和爪脚、品红肩刺、深紫护手和粉刺、手腕上的品红鞭藤。
- A / B 是 3/4 正面朝右，SA / SB 是正侧面朝右；B / SB 的头发收紧、鞭藤短；四张都是从头发顶到脚底约 726 px（约 66 格），脚底在地面线上。
- 没有任何技能特效、没有植物。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- 四张都画完后，最后写 `outputs/zyra-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zyra_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/zyra/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_vex_hd.py` 的做法），和已合并的女法师（莫甘娜、伊莉丝、奈德丽、索拉卡）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑 A / B、定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画 3/4 正面和**侧面朝右**（动作都用侧面），一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Zyra`）：普攻 attack1 / attack2（Zyra_attack1 / _attack2.anm）；Q `spell1` = Zyra_spell2.anm；W `spell2` = Zyra_attack2.anm；E `spell3` = Zyra_spell3.anm；R `spell4` = Zyra_spell4.anm；跑 `run` = 移速 350 以上 Zyra_run.anm（以下 Zyra_Walk）；死亡 Zyra_death.anm。植物（ZyraThornPlant 荆棘喷射者、ZyraGraspingPlant 藤蔓鞭击者、ZyraSeed 种子）在 Zyra.wad.client 里是单独的角色（`pose_ref.py --champ ZyraThornPlant --wad Zyra`）：第 3 步特效的参考。
