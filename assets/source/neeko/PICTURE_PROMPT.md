# 万花通灵 妮蔻：第 0 步，先画像素风原图（给 Codex 的提示词）

> 妮蔻是英雄联盟里一个**像变色龙一样的蜥蜴族女孩**：**青绿色带鳞片的皮肤**（手臂、肩膀、小腿是青绿色，额头和脸颊两边有一点青绿色的小鳞片），**一头蓬松的紫蓝色短发**（夹着几缕品红色），太阳穴边别着**一朵珊瑚粉色的百合花**（另一边耳下还有一朵小的）；头顶竖起**一圈细长的品红紫色羽刺**（根部青绿，中间一段亮粉色）；**一双大大的黄色眼睛**（竖瞳），浅桃色的小脸，**粉色的嘴唇**；脖子上一条细项链，挂着**一颗青蓝色的宝石**；上身是**珊瑚橙色的编织抹胸**，上面有金色的叶脉花纹，左肩上一条皮带、挂着几根小羽毛；腰上一条**棕色的皮带串着白色的贝壳珠**，下身是**深棕色的短裤**，前面垂着**一片橙色的叶子形腰布**；**大腿是浅桃色的**，上面有**紫色的螺旋纹**，小腿往下变成青绿色的鳞片；脚踝缠着**深棕色的绑带和金色的环**，**光着脚**，脚趾是紫色的；手指也是紫色的。身后拖着一条**长长的尾巴**（青绿色，背上一排紫色的鳞，尾巴末端紫色）。
>
> 请 Codex 画**两张全身像**（同一个妮蔻，长相、颜色、**格子大小**都一样），用户从里面挑大小：
> - **A：英雄联盟里的待机，3/4 正面朝右**（附图 1、2、8a）。她站着，两只手在胸前轻轻合着（附图 1），脸朝右前方、微微仰头，一脸好奇；**尾巴在身后（画面左边）往上弯成一个钩，尾巴尖离开地面**（原版的尾巴拖在地上——我们的游戏里尾巴不能躺在地上）。
> - **SA：A 的侧面，朝右**（附图 6、8b）。同一个妮蔻**正侧面朝右**站着（脸朝画面右边，看得见一只眼睛），尾巴同样在身后往上弯起。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的佐伊（小女孩）、婕拉（植物系女法师）和薇古丝（大头小女孩），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–6）。
> - **比例**：Q 版，**头大**（头发连脸约占身高的三分之一多，羽刺另算），身子短、腿短一点；不要细长的写实比例。羽刺是她最醒目的轮廓，要画得清楚，但**不能挡住脸**。
> - **脸**（附图 3 特写）：浅桃色的小脸，额头和脸颊两侧几格青绿色的小鳞片；**两只黄色的大眼睛一样大、一样高、都看得见**（每只至少 3×3 格，深色的竖瞳，一格白色高光）；粉色的小嘴；紫蓝色的刘海盖住额头、两边头发往外翘。
> - **颜色**：皮肤（手臂、肩、小腿、尾巴）青绿色 3–4 档（亮边偏薄荷绿，**不要糊成一团绿**）；脸和大腿浅桃色 2–3 档；头发紫蓝色 3–4 档加品红色的发缕；羽刺品红紫 3 档、中段亮粉、根部青绿；百合花珊瑚粉 2–3 档；抹胸和腰布珊瑚橙 3 档加金色花纹；短裤和绑带深棕 2–3 档；贝壳珠白色；宝石青蓝；大腿上的螺旋纹、手指、脚趾、尾巴背上的鳞是紫色。
> - **画布用正方形 1536×1536**。**妮蔻从最高的羽刺尖到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）；她站在画布中间（附图 8a、8b 的位置），尾巴在她身后（画面左边）。羽刺、头发、尾巴全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（种子、花、倒刺、分身、大招的花瓣和冲击波都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/neeko-picture/neeko-A.png`、`neeko-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/neeko-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/neeko_picture_done.zip`。

## 附图（在压缩包 `neeko_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_neeko_idle.png` | 英雄联盟原版妮蔻的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_neeko_frontal.png` | 同一帧，正面 | 抹胸、项链、贝壳腰带、短裤、腰布、腿上的花纹 |
| `refs/3_neeko_head.png` | 头部特写（3/4） | 羽刺、头发、百合花、脸、眼睛、鳞片 |
| `refs/4_neeko_back.png` | 同一帧的背后 | 头发背后、尾巴背上的紫色鳞片 |
| `refs/5_neeko_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/6_neeko_side.png` | 同一帧，侧面朝右 | SA 的角度：头发的长度、身子的厚度、尾巴 |
| `refs/8a_layout_front.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/11_style_zoe.png` | 本包的佐伊，8 倍放大，一格 = 一个像素 | **只看风格**：小女孩的大头、脸、眼睛在格子上怎么画 |
| `style/12_style_zyra.png` | 本包的婕拉（8 倍） | **只看风格**：植物系的颜色、花和叶子怎么分档 |
| `style/13_style_vex.png` | 本包的薇古丝（8 倍） | **只看风格**：Q 版大头、短身子的比例 |

## 提示词：`neeko-A.png` / `neeko-SA.png`（同一段提示词，只换最后一句）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-6 are 3D renders and art of a character from a game: a CURIOUS CHAMELEON-LIKE LIZARD GIRL with GREEN-TEAL SCALED SKIN (arms, shoulders, shins and tail; a few small teal scales on her forehead and cheeks), a fluffy mop of VIOLET-BLUE HAIR with MAGENTA STREAKS, a CORAL-PINK LILY at her temple (and a small one below the other ear), a crest of long thin MAGENTA-VIOLET QUILLS rising from her head (teal at the root, a bright pink band in the middle), BIG YELLOW EYES with slit pupils, a small pale-peach face, PINK LIPS, a thin necklace with a TEAL-BLUE GEM, a CORAL-ORANGE WOVEN TOP with gold leaf-vein patterns, a leather strap with small feathers on one shoulder, a BROWN BELT of WHITE SHELL BEADS, DARK BROWN SHORTS with an ORANGE LEAF-SHAPED LOINCLOTH hanging in front, PALE PEACH THIGHS with VIOLET SWIRL MARKINGS turning into teal scales down the shins, DARK BROWN ANKLE WRAPS with GOLD RINGS, BARE FEET with violet toes, violet fingers, and a LONG TAIL (teal, a row of violet scales along its top, a violet tip). (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the top, the necklace, the shell belt, the shorts, the loincloth, the leg markings; 3 the head close-up: the quills, the hair, the lilies, the face, the eyes, the scales; 4 the same from behind: the back of the hair, the tail's violet scales; 5 the official illustration: her mood, her colours, her face; 6 the idle from the side, facing right - the angle of SA.) Images 8a and 8b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a small girl's big head, face and eyes on the grid (11), plant colours, petals and leaves in flat shades (12), chibi proportions with a big head and a short body (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the quills, the hair, the tail); her soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). She is about 660 px (about 60 squares) from her highest quill tip to her soles and stands where images 8a / 8b show her (the centre), her tail behind her on the image left.
PROPORTIONS: chibi - the head with its hair BIG (more than a third of her height, the quills on top of that), a short body, shortish legs; NOT realistic slim proportions. The quill crest is her strongest shape, clear and readable, but it NEVER covers her face.
THE FACE: small, pale peach, a few teal scale squares on the forehead and both cheeks; TWO BIG YELLOW EYES of the SAME size at the SAME height, both visible (each at least 3x3 squares, a dark slit pupil and one white highlight square); a small pink mouth; violet-blue bangs over the forehead, the hair flaring out at both sides.
THE COLOURS: the skin of the arms, shoulders, shins and tail green-teal in 3-4 shades with MINT-GREEN LIT EDGES so it never turns into one green mass; the face and thighs pale peach in 2-3 shades; the hair violet-blue in 3-4 shades with magenta strands; the quills magenta-violet in 3 shades with a bright pink middle and a teal root; the lilies coral pink in 2-3 shades; the top and loincloth coral orange in 3 shades with gold patterns; the shorts and wraps dark brown in 2-3 shades; the shell beads white; the gem teal-blue; the thigh swirls, the fingers, the toes and the tail's top scales violet.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the teal skin, the peach face and thighs, the violet-blue hair, the magenta quills, the coral lilies, the orange top and loincloth, the brown shorts and wraps, the white shells and the violet markings clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no seeds, no flowers flying, no thorns, no clone, no petals, no shock waves, no sparkles), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (neeko-A.png): her idle in 3/4 view facing right (images 1, 2 and 8a) - standing, both hands held together lightly in front of her chest, the face to the front-right and tilted up a little, curious; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker; HER TAIL behind her (image left) CURLING UP into a hook, its tip OFF THE GROUND (never lying flat on the ground).
PICTURE SA (neeko-SA.png): the SAME girl seen exactly from the SIDE, FACING RIGHT (images 6 and 8b) - the face to the image right with one eye visible, the hands together in front of her chest, both soles on the ground line, her tail behind her (image left) curling up, its tip off the ground.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，羽刺、头发、尾巴完整，不出画。
- Q 版大头；**两只黄色大眼睛一样大、一样高**、竖瞳带白色高光；粉色小嘴；脸上几格青绿色鳞片；紫蓝色头发加品红发缕；**品红紫的羽刺不挡脸**；珊瑚粉百合花。
- 青绿色皮肤（有薄荷绿亮边，不糊成一团）、青蓝宝石项链、珊瑚橙抹胸和叶子腰布、白贝壳腰带、深棕短裤、浅桃色大腿上的紫色螺旋纹、深棕绑带和金环、光脚紫脚趾。
- **尾巴在身后往上弯，尾尖离地**，不躺在地上。
- A 是 3/4 正面朝右，SA 是正侧面朝右；两张都是从羽刺尖到脚底约 660 px（约 60 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- 两张都画完后，最后写 `outputs/neeko-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/neeko_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/neeko/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_heimerdinger_hd.py` / `design_zoe_hd.py` 的做法），和已合并的中单女孩（佐伊、薇古丝、婕拉、辛德拉）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_<hero>_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Neeko`）：普攻 Attack1 / Attack2，W 被动强化的第三下 Passive_attack（crit）；Q Spell1；E spell3（Spell3_0）；R Spell4（跳起来，落地 Spell4_toidle）；跑 Run（run_base = Neeko_Run.anm）；死亡 Death。被动的假扮由附加包换成队友的外观，不另画。
