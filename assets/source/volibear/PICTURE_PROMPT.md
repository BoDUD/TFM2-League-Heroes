# 不灭狂雷 沃利贝尔：第 0 步，先画像素风原图（给 Codex 的提示词）

> 沃利贝尔是弗雷尔卓德的**雷霆半神**：一头**用后腿站立的巨熊**，弓着背、肩膀非常宽厚。**头、肩膀、胸口和手臂是白色、带一点冰蓝的长毛**，往下渐渐变成**深灰紫色的毛**（肚子下半、两条腿、手掌和脚掌都是深色）。**头相对身体小**，埋在巨大的肩膀之间：熊的长嘴、**黑鼻头**、龇着牙的嘴、**两只发浅蓝光的眼睛**、额头上一道**蓝色的闪电符文**，一只耳朵上挂着一颗**蓝色宝石**，两只小圆耳朵。从两肩各垂下**一条长长的编起来的毛辫**，挂在胸前，辫子上套着**深色铁环**（铁环上有**发青光的符文**），末端是一撮**白毛穗子**。上臂有**发蓝光的符文纹身**，胸口和肚子上有几道**蓝色的闪电纹**。手和脚上是**发光的冰蓝色水晶爪子**。请 Codex 画**两张全身像**（同一只沃利贝尔，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、2、8a）。两脚分开、膝盖弯着半蹲，**两只手臂向两边张开、手肘弯着，爪子张开朝下**，整个身子很宽；头微微低着往前探，脸朝右前方，龇牙。
> - **B：手臂垂直放下的备战姿势**（附图 8b 只看大小和地面线）。两脚稍微分开、膝盖微弯，**两只手臂笔直地垂在身体两侧，爪子朝下、爪尖在膝盖上下**；脸朝右前方，龇牙。**手臂一定要竖直**（横平竖直，不要斜伸出去），这样整个身子横向窄一些。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的内瑟斯、布隆、塔姆和孙悟空（同是大体型、毛发多的英雄），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、7）。**不要画大招形态的冰刺、长鬃毛**，也不要画他脚边的小魄罗。
> - **比例**：他是**大体型的野兽，不要画成大头娃娃**。头（从耳朵顶到下巴）约占身高的五分之一（约 14 格），和英雄联盟一样小；最大的形状是**宽厚的肩膀和胸口**、**粗壮的手臂**；腿粗短。
> - **头**（附图 3 特写）：白色的毛分几档（纯白、浅冰蓝、偏灰蓝的暗部）；长长的熊嘴、黑鼻头、**龇着的牙**（白色）；**两只眼睛一样大、一样高、都看得见、发浅蓝光**（平涂的亮蓝，不要柔光），眉头压着、很凶；额头一道蓝色闪电符文；两只小圆耳朵，一只上挂着蓝宝石。
> - **毛色**：头、肩、胸、手臂是白色带冰蓝的毛（3–4 档），往下渐变成**深灰紫色**（肚子下半、腿、手掌、脚掌，3–4 档），两种颜色之间可以有一两档过渡，但**不要渐变**，用平涂的色块。深色的腿一定要有**偏亮的边**，不然在深色背景上会糊成一团。
> - **毛辫**：两条毛辫从肩膀垂到肚子，白毛编成，套着两三个**深色铁环**（铁环上有发青光的符文），末端一撮白毛穗；两条辫子都要清楚。
> - **发光的部分**：眼睛、额头符文、上臂的符文纹身、胸腹的闪电纹、铁环上的符文、**冰蓝水晶爪子**（手上各 3–4 根、脚上各 3 根）用平涂的亮青蓝色，不要柔光。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只脚掌落在同一条地面线上。
> - **画布用正方形 1536×1536**。**从耳朵顶到脚底约 792 px，也就是约 72 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。两只手臂、爪子、毛辫全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。白毛、深灰紫毛、黑鼻头、牙、铁环、发光的符文和爪子要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（闪电、雷云、落雷、电光、冲击波都放到第 3 步单独画；身上的符文和爪子是身体的一部分，用平涂的亮色画）；不画地面，不画影子。
> - 交付：`outputs/volibear-picture/volibear-A.png`、`volibear-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/volibear-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/volibear_picture_done.zip`。

## 附图（在压缩包 `volibear_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_volibear_idle.png` | 英雄联盟原版沃利贝尔的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_volibear_frontal.png` | 同一帧，正面 | 白毛和深色毛的分界、毛辫、铁环、胸腹的闪电纹、爪子怎么排 |
| `refs/3_volibear_head.png` | 头部特写 | 熊嘴、黑鼻头、龇牙、发蓝光的眼睛、额头符文、耳朵上的宝石 |
| `refs/4_volibear_back.png` | 同一帧的背后 | 背上的毛、肩膀的宽度 |
| `refs/5_volibear_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/7_volibear_side.png` | 同一帧，接近侧面 | 熊嘴的长度、毛辫、肩膀和肚子的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 他的大小、地面线（灰）；**姿势按文字：两只手臂竖直垂在身体两侧** |
| `style/11_style_nasus.png` | 本包的内瑟斯，8 倍放大，一格 = 一个像素 | **只看风格**：大体型、毛发的野兽在格子上怎么分档、留亮边 |
| `style/12_style_braum.png` | 本包的布隆（8 倍） | **只看风格**：弗雷尔卓德的大块头、白色和冰蓝色怎么分档 |
| `style/13_style_tahmkench.png` | 本包的塔姆（8 倍） | **只看风格**：大个子的描边和暗色的亮边 |
| `style/14_style_wukong.png` | 本包的孙悟空（8 倍） | **只看风格**：毛茸茸的边缘、脸在格子上怎么画 |

## 提示词：`volibear-A.png` / `volibear-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a HUGE BEAR STANDING ON HIS HIND LEGS, hunched, with massive shoulders - WHITE fur with a pale ICE-BLUE tint on the head, shoulders, chest and arms, turning to DARK SLATE-VIOLET fur on the lower belly, the legs, the hands and the feet; a SMALL BEAR HEAD sunk between the huge shoulders: a long muzzle, a BLACK NOSE, a SNARLING mouth with white teeth, TWO EYES GLOWING PALE BLUE, a BLUE LIGHTNING RUNE on the forehead, two small round ears, a BLUE JEWEL hanging from one ear; TWO LONG BRAIDED FUR TRESSES hanging from the shoulders down his chest, each in two or three DARK IRON BANDS with GLOWING CYAN RUNES and ending in a WHITE FUR TASSEL; GLOWING BLUE RUNE TATTOOS on the upper arms and BLUE LIGHTNING STRIPES across the chest and belly; CRYSTALLINE GLOWING ICE-BLUE CLAWS on the hands and feet (1 his idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: where the white fur turns dark, the tresses, the bands, the lightning stripes, the claws; 3 the head close-up: the muzzle, the nose, the teeth, the glowing eyes, the forehead rune, the ear jewel; 4 the same from behind: the fur of the back, the width of the shoulders; 5 the official illustration: his mood and colours; 7 the idle nearly from the side: the length of the muzzle, the tresses, the depth of the shoulders and belly). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Do NOT draw his ultimate form's ice spikes or long mane, and NO small creature at his feet. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a big furred beast split into clear shades with lit edges (11), a big northern brawler in white and ice-blue (12), a big body's outline and the lit edges of its dark parts (13), furry edges and a face on the grid (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (both arms, the claws and the tresses whole); both feet level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 792 px (about 72 squares) from the top of his ears to his soles.
PROPORTIONS: a BIG BEAST, NOT a big-headed doll: the head (ears to chin) about a fifth of his height (about 14 squares), as small as in images 1-3, never enlarged; the biggest shapes are the BROAD SHOULDERS AND CHEST and the THICK ARMS; the legs short and thick.
THE HEAD: the white fur in a few shades (pure white, pale ice-blue, a greyish-blue shade); the long muzzle, the black nose, the bared white teeth; TWO EYES of the SAME size at the SAME height, both visible, glowing pale blue (flat bright squares, no glow halo), a heavy angry brow; the blue lightning rune on the forehead; two small round ears, one with the blue jewel.
THE FUR: white with an ice-blue tint on the head, shoulders, chest and arms (3-4 shades), turning to dark slate-violet on the lower belly, the legs, the hands and the feet (3-4 shades), with one or two in-between shades but NO gradient - flat colour areas; the dark legs with LIGHTER EDGES so they never turn into one dark mass.
THE TRESSES: two braided white fur tresses from the shoulders down to the belly, each with two or three dark iron bands (glowing cyan runes on them) and a white fur tassel at the end; both clearly readable.
THE GLOWING PARTS: the eyes, the forehead rune, the rune tattoos on the upper arms, the lightning stripes on the chest and belly, the runes on the bands and the CRYSTALLINE ICE-BLUE CLAWS (3-4 on each hand, 3 on each foot) in flat bright cyan-blue, no soft glow.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the white fur, the dark slate-violet fur, the black nose, the teeth, the iron bands and the glowing runes and claws clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no lightning, no storm cloud, no bolt, no sparks, no shockwave), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (volibear-A.png): his idle (images 1, 2 and 8a) - feet apart in a half crouch, BOTH ARMS HELD OUT TO THE SIDES with the elbows bent and the claws spread pointing down, the body wide; the head a little low and thrust forward, the face to the front-right, snarling.
POSE B (volibear-B.png): an ARMS-DOWN READY STANCE - the SAME bear with the SAME 11-px squares: feet a little apart, knees slightly bent, BOTH ARMS HANGING STRAIGHT DOWN beside the body, the claws pointing down with their tips about knee height; the face to the front-right, snarling (image 8b shows only his size and the ground line). The arms must hang vertically, not spread out.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，两只手臂、爪子、毛辫完整，不出画。
- 比例：大体型的野兽，头（耳朵顶到下巴）约占身高五分之一（约 14 格），肩膀胸口宽厚、手臂粗壮、腿粗短；没有大招的冰刺和长鬃毛，脚边没有小魄罗。
- 头：长熊嘴、黑鼻头、龇着的白牙；**两只发浅蓝光的眼睛一样大、一样高**；额头蓝色闪电符文；小圆耳朵和蓝宝石。
- 毛：上半身白色带冰蓝，下面深灰紫色，平涂的色块、没有渐变；深色的腿有亮边。
- 两条毛辫、深色铁环和发光的符文、白毛穗；上臂的符文纹身、胸腹的闪电纹；冰蓝水晶爪子。
- A：两脚分开半蹲、两臂向两边张开、爪子朝下；B：两臂**竖直**垂在身体两侧、爪尖在膝盖上下。从耳朵顶到脚底约 792 px（约 72 格），脚底都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/volibear-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/volibear_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/volibear/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_ziggs_hd.py` 的做法，绝不按更少的行采样），和已合并的大体型上单 / 坦克（内瑟斯、布隆、塔姆、孙悟空、赛恩、茂凯）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑 A / B 和定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画（3/4 正面 + **侧面朝右**两种角度），再自己做动作帧（2026-10-19 补帧的方式，无损：只整格平移、绕半格枢轴的四分之一转、镜像；一张脸用在所有帧）。英雄联盟的动作：普攻 Volibear_Attack_1 / _2；W 暴怒撕咬 Volibear_Spell2_Slash；Q 擂首一击 Volibear_spell1_run（四脚着地冲）和 volibear_spell1_attack（扑上去砸）；E 霹天雳地 volibear_spell3（举爪召雷）；R 天声震落 Volibear_Spell4_Ground_Pound（跳起砸地）；跑 volibear_run；死亡 volibear_death。
