# 雷克塞（虚空遁地兽）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 雷克塞是一只**瞎眼的虚空掘地巨兽**：四肢着地蹲伏，全身是**靛蓝 / 宝蓝色的硬甲壳**，甲片边缘泛**青绿色高光**、甲壳上有细细的**青色纹路**；背上竖着一片巨大的、向后弯的**洋红到蓝的鳍冠**；头像一块**带尖棱的蓝色头盔**，**没有眼睛**；嘴是**洋红色**的，长着一排**骨白色的獠牙**，下颚两边各伸出一根**弯弯的大獠牙**；两只前肢外侧各挂着一大块**刀片一样的蓝色护甲**，手腕和脚踝是**暗酒红色**，爪子是**又黑又尖的三根大爪**；身后拖着一条**很长的、分节带尖刺的尾巴**。请 Codex 画**两张全身像**（同一个雷克塞，长相、颜色、格子大小都一样；两张**都要用**，不是二选一）：
> - **A**：地面上的待机（附图 1）。四肢撑地蹲伏，前爪按在地上，头压低朝前（画面右边），鳍冠高高竖在背上，尾巴拖在身后、末端往上翘。
> - **B**：钻在地下（附图 6）。地面以下的部分都看不见，**只露出鳍冠、上背和头顶**，周围是一圈**被拱起的碎土和碎石**（土堆本身也画进图里，贴在地面线上）。B 用来做她在地底下赶路的身体和钻地技能。
>
> 这一版每个游戏像素约 **1.8 格**，读回后再降到 PPU 1.5。附图 11–13 是本包里的斯莫德、芮尔、伊莉丝（蜘蛛形态），都是 1.5–1.8 的密度；附图 14 是本包的卡兹克（同为虚空生物，1 倍），**只看虚空的配色**。你画的原图会按格子直接读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相和结构照英雄联盟原版**（附图 1–4、9）。
> - **比例**：大型生物，不画成大头娃娃（附图 12 芮尔的马就是这种比例）。头可以比原版**稍大一点**（约占从鳍冠顶到爪尖总高的五分之一，约 13 格），让嘴和獠牙在游戏尺寸下看得清。
> - **头和脸**（附图 3 特写）：
>   - **没有眼睛**（她是瞎的，靠震动感知）；头顶是**宝蓝色的头盔甲片**，几道尖棱向后，带青色高光。
>   - 嘴部是**亮洋红色**，上面一排**骨白 / 米黄色的獠牙**，下颚两侧各一根**向前弯的大獠牙**；嘴里深处是暗酒红。**洋红色主要用在嘴和鳍冠上**。
> - **鳍冠**（附图 1、4）：背上一片巨大的、像镰刀一样**向后弯的鳍**，根部洋红、往外过渡成**宝蓝**，上面有几道深色的分节槽；鳍后面还有一片小一点的洋红色尖鳍。
> - **身体和四肢**（附图 1、2、9）：**靛蓝 / 宝蓝的甲壳**，甲片之间是暗紫色；甲片边缘有**亮青色的高光**和细细的**青色纹路**；肚子和关节下面是**暗紫褐色**。前肢外侧挂着大块的**刀片状蓝色护甲**，手腕、脚踝是**暗酒红色**的硬皮；每只脚三根**黑紫色的大尖爪**。
> - **尾巴**：很长，一节一节的蓝紫色甲片，每节上有尖刺，末端往上翘（附图 1、8a）。
> - **视角**：3/4 正面朝右（头朝右前方）。近侧（画面前面）的肢体颜色亮，远侧的暗一档；**爪尖落在同一条地面线上**（远侧的可以略高，但不能低于地面线）。
> - **画布用正方形 1536×1536**：**A 从鳍冠最高点到爪尖约 726 px，也就是约 66 格**，爪尖在离画布底边约 136 px 的地方（附图 8a 的灰线）。她横着比竖着宽很多，左右要留够边，尾巴尖、獠牙、爪子全在画面里。**B 和 A 用同一个比例**（附图 8b：同样的格子大小，鳍冠一样大），露出地面的部分贴在同一条地面线上，土堆也压在这条线上。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。蓝色甲壳、暗紫关节、洋红的嘴和鳍、骨白獠牙、暗酒红腕甲、黑爪要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。甲片的上沿要有**亮青色的高光**，免得深蓝色的身体在深色背景上糊成一团。
> - 不画任何特效（虚空能量、紫光、飞溅的尘土都放到第 3 步单独画；B 的土堆是静止的碎土碎石，照画）；不画地面，不画影子，不画别的角色。
> - 交付：`outputs/reksai-picture/reksai-A.png`、`reksai-B.png`（都是 1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/reksai-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/reksai_picture_done.zip`。

## 附图（在压缩包 `reksai_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_reksai_idle.png` | 英雄联盟原版雷克塞的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_reksai_frontal.png` | 同一帧，正面 | 头盔、嘴和獠牙、四肢和刀片护甲怎么排 |
| `refs/3_reksai_head.png` | 头部特写 | 头盔甲片（没有眼睛）、洋红的嘴、骨白獠牙、下颚大獠牙 |
| `refs/4_reksai_back.png` | 同一帧的背后 | 鳍冠、背甲、尾巴怎么接 |
| `refs/5_reksai_splash.png` | 官方加载画面 | 气质（凶狠、虚空的紫蓝、亮青色的甲片） |
| `refs/6_reksai_burrowed.png` | 钻地待机，3/4 朝右（地面以下已经去掉） | B 的姿势：露出的鳍冠、上背和头顶 |
| `refs/7_reksai_burrowed_side.png` | 同一帧，接近侧面 | B 里露出地面的部分有多高 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上她的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（同一比例） | 画布上露出部分的位置、大小、地面线（灰） |
| `refs/9_reksai_claws.png` | 四肢和爪子的特写 | 刀片护甲、暗酒红腕甲、三根黑爪 |
| `style/11_style_smolder.png` | 本包的斯莫德（小龙），8 倍放大，一格 = 一个像素 | **只看风格**：生物的甲片、鳍怎么分档 |
| `style/12_style_rell.png` | 本包的芮尔（骑马，8 倍） | **只看风格**：大型四足的比例、描边；这个密度下格子有多细 |
| `style/13_style_elise_spider.png` | 本包伊莉丝的蜘蛛形态（8 倍） | **只看风格**：多条腿和尖爪、紫色甲壳怎么分档 |
| `style/14_style_khazix.png` | 本包的卡兹克（虚空生物，1 倍放大 8 倍） | **只看配色**：虚空的紫蓝和青色高光 |

## 提示词：`reksai-A.png` / `reksai-B.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-7 and 9 are 3D renders and art of a creature from the game: a BLIND VOID BURROWING BEAST crouched on four clawed limbs - an armoured body of INDIGO / ROYAL-BLUE CARAPACE PLATES with bright CYAN-TEAL edge highlights and thin teal vein lines, a huge sickle-shaped DORSAL FIN CREST on her back curving backwards (MAGENTA at its root turning ROYAL BLUE outwards), a head like a spiked BLUE HELMET plate with NO EYES, a MAGENTA mouth with a row of BONE-WHITE FANGS and two big curved TUSKS on the lower jaw, big blue BLADE-LIKE ARMOUR PLATES on the outside of her front limbs, DARK WINE-RED wrists and ankles, three huge BLACK-PURPLE CLAWS on every foot, and a LONG SEGMENTED SPIKED TAIL (1 her idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the helmet, the mouth and fangs, how the limbs and blade plates spread; 3 the head close-up: the eyeless helmet, the magenta mouth, the fangs and tusks; 4 the same from behind: the fin crest, the back plates, where the tail joins; 5 the official illustration: her mood, savage, Void purple-blue with glowing cyan plates; 6 her burrowed idle with everything under the ground removed - pose B: the crest, the upper back and the top of the head out of the ground; 7 the same from nearer the side: how high the part above ground is; 9 a close-up of the limbs: the blade plates, the wine-red wrists, the black claws). Images 8a and 8b are layout guides of A and B: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how creature plates and fins are split into clear shades (11), how a big four-legged body is proportioned and how fine the squares are at this density (12), how many legs, pointed claws and a purple carapace are shaded (13). Image 14 is COLOUR ONLY: another Void creature of the same game (1x shown 8x) - its purple-blue and cyan highlights.
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Pose A: she is about 726 px (about 66 squares) from the top of the fin crest to the claw tips, the claw tips about 136 px above the bottom edge (the grey line of image 8a); she is much wider than tall - the tail tip, the tusks and every claw whole inside the picture, comfortable transparent margins, nothing cut off; the claw tips on or just above one ground line, none below it. Pose B uses EXACTLY the same scale and square size as A (the crest the same size), on the same ground line (image 8b).
PROPORTIONS: a big creature, NOT a big-headed doll (like the horse of image 12); the head may be a little larger than in the renders - about one fifth of the total height, about 13 squares - so the mouth and fangs read at game size.
THE HEAD: NO EYES at all (she is blind); a ROYAL-BLUE HELMET of carapace plates with a few sharp ridges sweeping back and cyan highlights; a bright MAGENTA mouth with a row of BONE-WHITE / CREAM FANGS, two big CURVED TUSKS from the lower jaw pointing forward, dark wine-red deep inside the mouth. Magenta is used mainly for the mouth and the crest.
THE CREST: a huge SICKLE-SHAPED FIN on her back curving backwards, MAGENTA at the root turning ROYAL BLUE towards the edge, a few dark segment grooves; a smaller magenta spike fin behind it.
THE BODY AND LIMBS: INDIGO / ROYAL-BLUE carapace plates with dark purple between them, bright CYAN highlights on the plate edges and thin teal vein lines; the belly and the undersides of the joints dark purple-brown; big blue BLADE-LIKE plates on the outside of the front limbs; DARK WINE-RED hard skin on the wrists and ankles; three big pointed BLACK-PURPLE CLAWS on every foot.
THE TAIL: long, made of blue-purple plated segments with a spike on each, its end curling up (images 1, 8a).
THE VIEW: 3/4 view facing right (the head to the front-right): the NEAR limbs in full tone, the FAR ones a step darker; the claw tips level on one ground line (the far ones may sit a little higher, never lower).
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the blue carapace, the dark purple joints, the magenta mouth and crest, the bone-white fangs, the wine-red wrists and the black claws clearly separated; bright cyan highlights on the top edges of the plates so the dark blue body reads on a dark background; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no Void energy, no purple glow, no flying dust), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (reksai-A.png): her idle on the surface (image 1) - crouched on all four limbs, the front claws planted, the head low and forward (image right), the fin crest high on her back, the tail lying behind her with its end curling up.
POSE B (reksai-B.png): burrowed (images 6, 7) - everything under the ground line is hidden: only the fin crest, the upper back and the top of the helmet head show above the ground, ringed by a low heap of BROKEN DARK EARTH AND STONE CHUNKS she is pushing up (a few chunks with faint purple cracks), the heap sitting on the ground line and part of the picture.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尾巴尖、獠牙和爪子完整，不出画。
- 比例：大型生物，不是大头娃娃；头约占总高五分之一（约 13 格），嘴和獠牙看得清。
- 头：**没有眼睛**；宝蓝头盔甲片带尖棱；**洋红的嘴**、骨白獠牙、下颚两根大獠牙。
- 鳍冠：镰刀形、向后弯、根部洋红到外缘宝蓝；后面一片小洋红尖鳍。
- 身体：靛蓝 / 宝蓝甲壳、青色高光和纹路；前肢刀片护甲、暗酒红腕甲、每只脚三根黑爪；长尾巴分节带刺、末端上翘。近侧亮、远侧暗一档。
- A：四肢着地蹲伏，头压低朝前；从鳍冠顶到爪尖约 726 px（约 66 格），爪尖在同一条地面线附近，不低于它。
- B：和 A **同一个比例、同样的格子**；只露出鳍冠、上背和头顶，周围一圈碎土碎石，土堆压在地面线上；地面以下什么都不画。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- A、B 两张都画完后，最后写 `outputs/reksai-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/reksai_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/reksai/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_<hero>_hd.py` 的做法），和已合并的打野大块头（赫卡里姆、伊莉丝蜘蛛、雷恩加尔、卡兹克、蔚）按游戏里的大小并排给用户看；PPU 已定 1.5，再出 2–3 个大小的对比让用户定（**每个动作的显示高度**都要和德莱厄斯比，潘森的教训；她很宽，也量宽度）。头的大小按 oppi 大块头的比例检查（赫卡里姆的教训）。
- 定下后第 1 步按游戏格子重画 A 和 B（潘森 / 厄斐琉斯的做法），再做动作帧：鳍冠、刀片护甲、爪子是刚体部件，只平移和整块转直角，不变形；跑步照 RekSai_run；普攻 RekSai_attack1–3；Q 女王之怒 RekSai_spell1，猎物搜寻 RekSai_spell1_burrowed；W 钻地 RekSai_Spell3_burrowed / 破土 RekSai_Spell2_unburrow；R RekSai_Spell4_cast → Spell4_hit；死亡 RekSai_death；地底的跑步 RekSai_run_burrowed（附加包整身换图用 B）。
