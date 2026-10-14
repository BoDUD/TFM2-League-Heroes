# 赛恩（亡灵战神）：先画一张游戏尺寸的像素原图（第 0 步，给 Codex 的提示词）

> 赛恩还没有原图。这一步请 Codex 画一张全身像素图，**直接画成游戏里的大小**：一格 = 游戏里一个像素（1 倍帧，不走高清），
> 画布横版 1536×1024，**每格 18 像素**，**头顶（光头顶，不算红飘带）到脚底 44 格**（包里达瑞斯 42 格、诺提勒斯 51 格）。
> A、B 两版只差**那把巨斧怎么拿**，人、脸、铠甲、颜色完全一样：**A = 英雄联盟里的待机，斧头提在近侧手里、斧刃朝下垂在近侧腿边**（附图 1、2）；
> **B = 同一个人，斧头扛在近侧肩上、斧刃在他背后上方**（斧头样子看附图 8）。你挑一版，第 1 步再按它画干净的正面 + 侧面造型。
> - **长相照英雄联盟原版**（附图 1–9）：赛恩，一个被死灵术唤醒的诺克萨斯巨人，**巨大、驼背、肌肉夸张**，上身特别大、头特别小。
> - **头**（附图 3 特写）：**小小的光头**，皮肤苍白灰紫，**两只发红光的眼睛**（同一行，各 1–2 格，这个红色别处不用），
>   下半张脸被一个**黑铁的下颌笼**罩住，笼边一圈**向外的尖刺**（2–4 个灰色尖格），露出几颗黄牙；头顶插着**一截断剑**（剑柄朝上，深色），剑柄上系着一条**红色飘带**往左后方飘。头约占身高的 **1/5**（原版就是小头，别画大）。
> - **身体**：**灰紫色的大块肌肉**（亮部浅灰蓝，暗部紫灰），胸口有几道**暗红的缝合伤口**和几块**钉进肉里的黑铁菱形片**；
>   **远侧肩膀（画面右边）一大块带尖刺的黑铁肩甲**（三四根尖角往上翘，几颗铆钉），远侧前臂一个**黑铁护手**、棕色皮绑带；近侧手臂裸着，前臂缠着**棕色皮带**；
>   肚子正中一个**发光的红色熔炉核心**（椭圆，亮红 + 粉红高光，全身最亮的地方），压在一条**宽大的黑铁腰带**上（两个圆形铁扣）；
>   腰下**棕色 + 深紫褐色的裤子**，前面垂一片**短短的橄榄绿破布**（下摆参差）；两条短粗腿岔开半蹲，**黑铁大靴**，远侧靴子上一个尖刺。
> - **巨斧（很重要，附图 8）**：长长的**木柄缠着深棕色皮条**，一头是一片**宽大的弧形钢斧刃**（冷灰蓝，刃口亮），斧刃和柄连接处是**黑铁箍 + 一块浅灰绿的方铁块**，柄尾一个小铁尖。
>   斧刃至少 8 格宽、斧柄至少 2 格粗，和身体之间要有描边分开。**A**：近侧手（画面左边）握着柄的上端，斧刃朝下、刃口朝外，垂在近侧腿边，刃尖离地面一两格；
>   **B**：近侧手抬到肩前握着柄，斧柄斜扛在近侧肩膀上，斧刃在他背后、头的左上方，**不能挡住脸**。
> - **姿势**：3/4 正面朝右（脸、胸口朝向看画的人），驼背前倾、两腿岔开半蹲：**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗、稍高**，两只靴子踩在同一条地面线上；远侧手（画面右边，戴铁护手）自然垂着、手指张开。
> - **大小和位置**（附图 15 是量尺）：画布 1536×1024，**每格 18 像素**，网格从左上角 (0,0) 开始；**脚底在第 52 行**（像素 y 936–953，绿线就是地面），**光头顶在第 9 行**（y 162–179，红线）；红飘带、肩甲尖角可以高过红线。人放在画面中间。
>   附图 15 右边那个人是包里的达瑞斯，按同样的格子画的（42 格高）——**只用来看大小**，你的画里不要画他。
> - **像素块**：每块 18×18 像素，大小一致、对齐网格，一块一个颜色（会被按格子读回成游戏像素）；**外轮廓一圈 1 格宽的近黑描边**（像附图 10–14）；
>   内部每种材质 3–4 档平涂，光从左上来；整张图**最多约 24 种颜色**；不要零散的单个杂色格，不要描边里面再套一圈黑。
> - **风格照附图 10–14**：附图 10–13 是包里已经在游戏里的 1 倍英雄（诺提勒斯、阿利斯塔、达瑞斯、雷克顿）放大 8 倍，**只看风格**（像素大小、描边、平涂、厚重的比例）；
>   附图 14 是另一位作者画的赛恩（8 倍），**只看这么小的尺寸下斧头、肩甲、小头怎么读得清**，不要照抄。
> - 不画任何特效（护盾、冲撞火焰、亡灵灵魂都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/sion-picture/sion-model-A.png`、`outputs/sion-picture/sion-model-B.png`（1536×1024 横版、真透明背景，按上面的格子）；
>   再交两张**一格一像素**的读回：`sion-model-A_1x.png`、`sion-model-B_1x.png`（85×56）；附一个 `generation-prompts.txt` 写明实际用的提示词，
>   原始生成稿放 `outputs/sion-picture/raw/`，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `sion_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sion_league_front.png` | 英雄联盟原版赛恩待机，3/4 朝右 | 颜色、形状、**角度**、A 的斧头拿法 |
| `refs/2_sion_league_frontal.png` | 同一帧，更正面的角度 | 熔炉核心、腰带、破布、靴子 |
| `refs/3_sion_league_head.png` | 头的特写 | 光头、红眼、**下颌笼 + 尖刺**、头顶断剑 + 红飘带 |
| `refs/4_sion_league_back.png` | 同一帧的背后 | 肩甲背面、背部 |
| `refs/5_sion_splash.png` | 官方加载画面 | 气质（狰狞、压迫感） |
| `refs/6_sion_league_run.png` | 他跑动的几个瞬间 | 第 2 步用（这一步不用） |
| `refs/7_sion_league_actions.png` | 普攻、Q 蓄力、Q 砸地、E 怒吼、R 冲撞的瞬间 | 第 2 步用（这一步不用） |
| `refs/8_sion_league_axe.png` | 斧头举起来的样子 | **斧头的样子**（宽弧形斧刃、缠皮条的柄、铁箍 + 方铁块）、B 的扛法 |
| `refs/9_sion_league_side.png` | 待机的侧面（朝右） | 第 1 步还会用 |
| `style/10_style_nautilus.png` | 诺提勒斯 1 倍待机（8 倍放大，一格 = 一个游戏像素） | **只看风格** |
| `style/11_style_alistar.png` | 阿利斯塔 1 倍待机（8 倍） | **只看风格**（同样魁梧） |
| `style/12_style_darius.png` | 达瑞斯 1 倍待机（8 倍） | **只看风格**（同是诺克萨斯、拿斧头） |
| `style/13_style_renekton.png` | 雷克顿 1 倍待机（8 倍） | **只看风格**（上单） |
| `style/14_other_artist_sion.png` | 另一位作者的赛恩（8 倍） | 只看小尺寸下怎么读清，**不照抄** |
| `guide/15_size_guide.png` | 1536×1024 画布的 18 像素格子，绿线 = 脚底，红线 = 头顶；右边是达瑞斯 | **只看大小和地面**，不要画进去 |

## 提示词 A：`sion-model-A.png`（斧头提在近侧手里、斧刃朝下）

十五张图都附上，顺序同上表。

```text
Fifteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look, the ANGLE and the AXE HOLD of this picture; 2 the same from a more frontal angle: the glowing furnace in the belly, the iron belt, the loin cloth, the boots; 3 the head close-up: the small BALD head, the RED GLOWING EYES, the black IRON JAW CAGE with spikes, the broken blade stuck in the top of the head with a RED RIBBON on its hilt; 4 the same from behind; 5 the official illustration: his mood; 6 moments of his running - not used here; 7 moments of his attack and spells - not used here; 8 the great axe raised: the shape of the AXE; 9 the idle from the side - not used here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one game pixel: copy EXACTLY their pixel-art look - square size, the one-square near-black outline, flat 3-4 step shading, heavy chunky proportions (image 14 is another artist's version of this same character at game size: see how the axe, the pauldron and the small head stay readable that small - do NOT copy it). Image 15 is the SIZE GUIDE: the 1536x1024 canvas on its 18-px grid, the green line is the ground (soles), the red line is the top of the head; the figure at its right edge is another character drawn on the same grid, ONLY to show the size - never draw it.
Create ONE full-body pixel-art picture of this character at GAME SIZE: a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), drawn on the grid of image 15 - squares of 18x18 px starting at the top-left corner (0,0), every square ONE flat colour. The soles stand on square row 52 (pixels y 936-953, the green line), the top of the bald head on square row 9 (y 162-179, the red line): 44 squares from the crown to the soles; the red ribbon and the pauldron spikes may rise above the red line. Centred, nothing cut off.
The character: Sion, the Undead Juggernaut, a huge reanimated warrior - HUNCHED forward, an enormous muscular upper body, a SMALL head, short thick legs. THE HEAD (image 3): a small BALD head with pale grey-lilac skin, TWO RED GLOWING EYES on the same row (each 1-2 squares, that red used nowhere else), the lower face locked in a BLACK IRON JAW CAGE with a few short grey SPIKES pointing outward and a couple of yellow teeth showing; a short broken BLADE stuck in the top of the head, its dark hilt pointing up with a RED RIBBON tied to it fluttering back to the upper left. The head is about ONE FIFTH of his height (League's small head - do not enlarge it). THE BODY: huge PALE GREY-LILAC muscles (light grey-blue highlights, purple-grey shadows) with a few DARK RED STITCHED SCARS and a few BLACK IRON DIAMOND PLATES nailed into the chest; on the FAR shoulder (image right) a HUGE BLACK-IRON SPIKED PAULDRON with three or four horns pointing up and a few rivets; a black iron GAUNTLET with brown leather straps on the far forearm; the near arm bare, a brown leather wrap on its forearm; in the middle of the belly a GLOWING RED FURNACE CORE (an oval, bright red with a pink highlight - the brightest spot of the figure) sitting on a WIDE BLACK IRON BELT with two round iron buckles; below it BROWN and DARK PLUM-BROWN trousers with a short ragged OLIVE-GREEN LOIN CLOTH hanging in front; two short thick legs apart, knees bent, in BIG BLACK IRON BOOTS, one spike on the far boot. THE GREAT AXE (image 8): a long wooden HAFT wrapped in dark brown leather strips, at one end a BROAD CURVED STEEL BLADE (cold grey-blue, a bright edge), where blade and haft meet a black iron collar and a small pale grey-green square iron block, a small iron spike at the butt; the blade at least 8 squares wide, the haft at least 2 squares thick, the outline always between the axe and the body.
Pose: League's own idle (images 1, 2): hunched forward, legs apart in a heavy half crouch, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher, both boots on the ground line; the NEAR HAND (image left) grips the top of the haft and the axe HANGS DOWN beside his near leg, the blade pointing down with its edge turned outward, its tip one or two squares above the ground; the far arm in its iron gauntlet hangs relaxed, fingers spread. The axe and the hands never cover the face or the furnace. 3/4 FRONT view facing image right, face and chest toward the viewer.
Style: crisp game-size pixel art like images 10-13 - every pixel one 18x18 square of one flat colour on the grid, a ONE-SQUARE near-black outline around the silhouette and no black ring inside it, every material in its own 3-4 flat shades lit from the upper left, at most about 24 colours in the whole picture, no stray single odd squares: the skin pale grey-lilac, the iron black-grey with lighter edges, the furnace bright red, the eyes red, the trousers brown and plum, the cloth olive, the axe blade cold steel grey-blue, the haft and straps brown; light and dark parts clearly separated, never one blob; no dithering, no gradients, no soft glow, no blur, no anti-aliasing, no half-transparent edges.
No effects (no shield, no flames, no souls, no dust), no background, no ground, no shadow, no text, no frame, no other characters.
Also deliver the same picture read back ONE PIXEL PER SQUARE (85x56 PNG, transparent), exactly square for square.
```

## 提示词 B：`sion-model-B.png`（斧头扛在近侧肩上）

十五张图都附上，顺序同上表。

```text
Fifteen attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from a more frontal angle: the glowing furnace in the belly, the iron belt, the loin cloth, the boots; 3 the head close-up: the small BALD head, the RED GLOWING EYES, the black IRON JAW CAGE with spikes, the broken blade stuck in the top of the head with a RED RIBBON on its hilt; 4 the same from behind; 5 the official illustration: his mood; 6 moments of his running - not used here; 7 moments of his attack and spells - not used here; 8 the great axe raised over his near shoulder: the shape of the AXE and the SHOULDER HOLD of this picture; 9 the idle from the side - not used here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one game pixel: copy EXACTLY their pixel-art look - square size, the one-square near-black outline, flat 3-4 step shading, heavy chunky proportions (image 14 is another artist's version of this same character at game size: see how the axe, the pauldron and the small head stay readable that small - do NOT copy it). Image 15 is the SIZE GUIDE: the 1536x1024 canvas on its 18-px grid, the green line is the ground (soles), the red line is the top of the head; the figure at its right edge is another character drawn on the same grid, ONLY to show the size - never draw it.
Create ONE full-body pixel-art picture of this character at GAME SIZE: a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), drawn on the grid of image 15 - squares of 18x18 px starting at the top-left corner (0,0), every square ONE flat colour. The soles stand on square row 52 (pixels y 936-953, the green line), the top of the bald head on square row 9 (y 162-179, the red line): 44 squares from the crown to the soles; the red ribbon, the pauldron spikes and the axe blade may rise above the red line. Centred, nothing cut off.
The character: Sion, the Undead Juggernaut, a huge reanimated warrior - HUNCHED forward, an enormous muscular upper body, a SMALL head, short thick legs. THE HEAD (image 3): a small BALD head with pale grey-lilac skin, TWO RED GLOWING EYES on the same row (each 1-2 squares, that red used nowhere else), the lower face locked in a BLACK IRON JAW CAGE with a few short grey SPIKES pointing outward and a couple of yellow teeth showing; a short broken BLADE stuck in the top of the head, its dark hilt pointing up with a RED RIBBON tied to it fluttering back to the upper left. The head is about ONE FIFTH of his height (League's small head - do not enlarge it). THE BODY: huge PALE GREY-LILAC muscles (light grey-blue highlights, purple-grey shadows) with a few DARK RED STITCHED SCARS and a few BLACK IRON DIAMOND PLATES nailed into the chest; on the FAR shoulder (image right) a HUGE BLACK-IRON SPIKED PAULDRON with three or four horns pointing up and a few rivets; a black iron GAUNTLET with brown leather straps on the far forearm; the near arm bare, a brown leather wrap on its forearm; in the middle of the belly a GLOWING RED FURNACE CORE (an oval, bright red with a pink highlight - the brightest spot of the figure) sitting on a WIDE BLACK IRON BELT with two round iron buckles; below it BROWN and DARK PLUM-BROWN trousers with a short ragged OLIVE-GREEN LOIN CLOTH hanging in front; two short thick legs apart, knees bent, in BIG BLACK IRON BOOTS, one spike on the far boot. THE GREAT AXE (image 8): a long wooden HAFT wrapped in dark brown leather strips, at one end a BROAD CURVED STEEL BLADE (cold grey-blue, a bright edge), where blade and haft meet a black iron collar and a small pale grey-green square iron block, a small iron spike at the butt; the blade at least 8 squares wide, the haft at least 2 squares thick, the outline always between the axe and the body.
Pose: hunched forward, legs apart in a heavy half crouch, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher, both boots on the ground line; the NEAR HAND (image left) is raised in front of his near shoulder gripping the haft, the haft RESTS ON HIS NEAR SHOULDER slanting back, the broad blade BEHIND HIM above and to the left of his head, its edge facing up and back; the butt of the haft ends in front of his near hip; the far arm in its iron gauntlet hangs relaxed, fingers spread. The axe and the hands never cover the face or the furnace. 3/4 FRONT view facing image right, face and chest toward the viewer. A compact silhouette.
Style: crisp game-size pixel art like images 10-13 - every pixel one 18x18 square of one flat colour on the grid, a ONE-SQUARE near-black outline around the silhouette and no black ring inside it, every material in its own 3-4 flat shades lit from the upper left, at most about 24 colours in the whole picture, no stray single odd squares: the skin pale grey-lilac, the iron black-grey with lighter edges, the furnace bright red, the eyes red, the trousers brown and plum, the cloth olive, the axe blade cold steel grey-blue, the haft and straps brown; light and dark parts clearly separated, never one blob; no dithering, no gradients, no soft glow, no blur, no anti-aliasing, no half-transparent edges.
No effects (no shield, no flames, no souls, no dust), no background, no ground, no shadow, no text, no frame, no other characters.
Also deliver the same picture read back ONE PIXEL PER SQUARE (85x56 PNG, transparent), exactly square for square.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，人物和整把斧头都完整，不出画。
- **每块 18×18 像素、一块一个颜色、对齐从 (0,0) 开始的网格**；脚底在第 52 行（y 936–953），光头顶在第 9 行（y 162–179），44 格高；1 倍读回 85×56 和大图逐格一致。
- 小光头、两只红眼（同一行）、黑铁下颌笼 + 尖刺、头顶断剑 + 红飘带；头约占身高 1/5。
- 灰紫肌肉、暗红缝合伤、黑铁菱形钉片；远侧（画面右边）带尖角的大黑铁肩甲 + 铁护手；肚子上发光的红色熔炉 + 黑铁宽腰带；棕/深紫褐裤子 + 橄榄绿破布；黑铁大靴。
- 巨斧：宽弧形钢斧刃（至少 8 格宽）+ 缠皮条的长柄（至少 2 格粗）+ 铁箍和方铁块；A 垂在近侧腿边、B 扛在近侧肩上斧刃在背后左上；都不挡脸和熔炉。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；两只靴子落在同一条地面线上；没有任何特效。
- 外轮廓 1 格近黑描边，里面不再套黑圈；每种材质 3–4 档平涂，最多约 24 种颜色；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/sion-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画、1 倍读回和 raw/ 放进 `assets/source/sion/codex_picture/`；自己用 `scripts/regrid.py` 读回大图（核对 Codex 的 1 倍读回），和达瑞斯、诺提勒斯、阿利斯塔并排、在游戏实际大小（1x、2x、4x）下给用户挑 A / B 和大小。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：**正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子）**，同一套 18 像素格子、同样的高度和细节（side-view-design）；1 倍，读回 1:1，绝不先画大再缩。
- 跑步用诺提勒斯/布隆的走法（待机身体 + 造型自己的两条腿轮流抬起、小步前移、身体微浮，rig_galio.walk_frame），不做向前冲刺的交叉腿；同一张脸贯穿所有帧；斧头是刚体（只平移或 90 度转）。
