# 魔蛇之拥 卡西奥佩娅：第 0 步，先画像素风原图（给 Codex 的提示词）

> 卡西奥佩娅是**蛇身女人**：上半身是人（**小麦色的皮肤**），下半身是一条**长长的深绿色蛇尾**（背上是深翠绿的鳞片、带一点亮绿的菱形花纹，**肚子一侧是一条浅黄绿色的腹鳞**，一节一节的）。头上戴着**金边翠绿的蛇头兜帽头盔**（像眼镜蛇张开的颈兜，金色的边框，额头正中一颗**蓝色的宝石**，头顶一根**向上的金色尖冠**），兜帽里是她的脸：**眼影是紫色的，眼睛发白发亮**（两只一样大），嘴角露出**两颗白色的小毒牙**；脑后垂下一点**墨绿色的头发**。身上是**金色和翠绿色的胸衣**，两条胳膊上有**金色的臂环**（上臂一个、手腕一个），两只手戴着**金色的尖爪手套**（手指像爪子一样弯着）。腰部和蛇尾接起来的地方有一圈**金色的腰带**，腰带两侧各伸出一根**弯钩一样的金色鳍刺**（像两把向下弯的金色镰刀，附图 1、2 里看得清楚）。请 Codex 画**两张全身像**（同一个卡西奥佩娅，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、8a）。上身挺直、微微前倾，**两只爪子手抬在胸前**（近侧的手在前、手指张开像要抓东西，远侧的手在胸口），脸朝右前方；蛇尾从腰下先往下弯，再**平平地铺在地面上往身后（画面左边）伸出去**，尾巴尖收细。
> - **B：盘起来的蛇尾**（附图 8b 只看高度和地面线）。上身和手一样，**蛇尾在她身下盘成一圈**（像一个扁扁的圆盘，腹鳞的浅色露在盘圈的边上，尾巴尖从盘圈后面翘出一小截），这样整个人横向窄很多。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的娜美（鱼尾）、莫甘娜和伊莉丝，**只看风格**——娜美就是这种没有腿、靠尾巴立着的英雄在格子上怎么画。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：Q 版，**头（连兜帽和尖冠）约占上半身（从冠尖到腰带）的一半**；身子小一点，手和爪子稍大；蛇尾粗壮。不要细长的写实比例。
> - **头**（附图 3 特写）：翠绿兜帽有金色的边，额头一颗蓝宝石，头顶金色尖冠；脸在兜帽里要看得清：**两只眼睛一样大、一样高、都看得见**（每只至少 2 格，发白的亮眼睛，周围一圈紫色眼影），两颗白色小毒牙；墨绿头发垂在脑后。
> - **衣服**：金色和翠绿的胸衣、金臂环、金色尖爪手套、腰间金腰带和两根向下弯的金鳍刺。
> - **蛇尾**：深翠绿的背鳞（3–4 档，带亮绿的菱形花纹）、浅黄绿的腹鳞（一节一节的横纹）**两种颜色要分得开**；尾巴粗细从腰到尾尖慢慢变细，**轮廓圆滑、粗细连续**，不要锯齿。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂在画面左边、颜色亮；远侧的在画面右边、稍暗**。蛇尾最低的地方落在地面线上。
> - **画布用正方形 1536×1536**。**从尖冠顶到蛇尾贴地的最低处约 770 px，也就是约 70 格**，地面线在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。蛇尾、爪子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。小麦色皮肤、翠绿兜帽、金色、蓝宝石、紫眼影、白眼睛、墨绿头发、深翠绿背鳞、浅黄绿腹鳞要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**深绿的蛇尾很暗，一定要有偏亮的边和亮绿的花纹**，不然在深色背景上会糊成一团。
> - 不画任何特效（毒雾、毒牙光、石化光都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/cassiopeia-picture/cassiopeia-A.png`、`cassiopeia-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/cassiopeia-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/cassiopeia_picture_done.zip`。

## 附图（在压缩包 `cassiopeia_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_cass_idle.png` | 英雄联盟原版卡西奥佩娅的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势和蛇尾怎么铺 |
| `refs/2_cass_frontal.png` | 同一帧，正面 | 胸衣、腰带、金鳍刺、腹鳞怎么排 |
| `refs/3_cass_head.png` | 头部特写 | 兜帽、尖冠、蓝宝石、脸、眼影、毒牙 |
| `refs/4_cass_back.png` | 同一帧的背后 | 兜帽背后、头发、蛇尾背鳞 |
| `refs/5_cass_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_cass_gaze.png` | 大招石化凝视的一帧 | 身体前探、手往前伸的样子 |
| `refs/7_cass_side.png` | 同一帧，接近侧面 | 蛇尾和身体从侧面看的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看高度和地面线） | 她的高度、地面线（灰）；**姿势按文字：蛇尾在身下盘成一圈** |
| `style/11_style_nami.png` | 本包的娜美（鱼尾），8 倍放大，一格 = 一个像素 | **只看风格**：没有腿、靠尾巴立着的身体在格子上怎么画 |
| `style/12_style_morgana.png` | 本包的莫甘娜（8 倍） | **只看风格**：格子密度、描边、每种材质分几档 |
| `style/13_style_elise.png` | 本包的伊莉丝（8 倍） | **只看风格**：女法师的脸、眼睛在格子上怎么画 |

## 提示词：`cassiopeia-A.png` / `cassiopeia-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a SERPENT WOMAN - a human upper body with TAN SKIN on a LONG, THICK DARK-GREEN SNAKE TAIL instead of legs (the back of the tail dark emerald scales with a brighter green diamond pattern, the BELLY side a band of PALE YELLOW-GREEN SEGMENTED belly scales); a COBRA-HOOD HELMET, emerald with GOLD rims, a BLUE GEM on the forehead and a tall GOLD CREST rising from the top; inside the hood her face: PURPLE eye shadow, PALE GLOWING WHITE EYES, two small white FANGS at the corners of the mouth; a little dark teal hair falling behind; a GOLD-AND-EMERALD bra top, GOLD ARM BANDS (one on each upper arm, one on each wrist), GOLD CLAWED GAUNTLETS with curled claw fingers; a GOLD BELT where her body meets the tail, with TWO CURVED GOLD HOOK-FINS sweeping down like sickles from its sides (1 her idle, 3/4 view facing right - the look, the ANGLE, pose A and how the tail lies; 2 the same from the front: the bra, the belt, the gold hook-fins, the belly scales; 3 the head close-up: the hood, the crest, the gem, the face, the eye shadow, the fangs; 4 the same from behind: the back of the hood, the hair, the tail's back scales; 5 the official illustration: her mood and colours; 6 a frame of her petrifying gaze: leaning forward, a hand thrust out; 7 the idle nearly from the side: the thickness of the tail and the body). Images 8a and 8b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - a legless figure standing on a tail on the grid (11), the square density, the outline and the number of shades a material gets (12), a female mage's face with readable eyes on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the whole tail and both clawed hands); the lowest part of the tail resting on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). She is about 770 px (about 70 squares) from the tip of her crest to the ground.
PROPORTIONS: chibi - the head with the hood and crest about HALF of her upper body (crest tip to belt); a smaller body, slightly big hands and claws, a THICK tail; NOT realistic slim proportions.
THE HEAD: the emerald hood with gold rims, the blue gem on the forehead, the gold crest on top; the face inside the hood clearly readable: TWO EYES of the SAME size at the SAME height, both visible (each at least 2 squares, pale glowing white, ringed with purple eye shadow), two small white fangs; dark teal hair behind.
THE CLOTHES: the gold-and-emerald bra, the gold arm bands, the gold clawed gauntlets, the gold belt and its two down-curved gold hook-fins.
THE TAIL: dark emerald back scales in 3-4 shades with a brighter green diamond pattern, PALE YELLOW-GREEN segmented belly scales with cross lines - the two clearly separated; the tail tapering smoothly from the waist to a thin tip, a SMOOTH, CONTINUOUS outline and thickness, no jagged steps.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm on the image left in full tone, the FAR one on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark green tail with LIGHTER EDGES and the bright green pattern so it never turns into one dark mass; the tan skin, the emerald hood, the gold, the blue gem, the purple eye shadow, the white eyes, the dark teal hair, the dark emerald back scales and the pale yellow-green belly scales clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no poison cloud, no green glow, no gaze beam), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (cassiopeia-A.png): her idle (images 1 and 8a) - the upper body upright and leaning a little forward, BOTH CLAWED HANDS raised in front of her chest (the NEAR hand forward with the claws spread as if to grab, the FAR hand at her chest); the tail bends down from her waist and then LIES FLAT ON THE GROUND stretching out BEHIND her (to the image left), tapering to a thin tip; the face to the front-right.
POSE B (cassiopeia-B.png): a COILED TAIL - the SAME serpent woman with the SAME 11-px squares and the same upper body and hands as A, but her tail COILED UNDER HER in one flat round loop (the pale belly scales showing along the coil's edge, the thin tip peeking out from behind the coil), so she is much narrower than in A; the face to the front-right (image 8b shows only her height and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，蛇尾、两只爪子完整，不出画。
- 比例：Q 版，头（连兜帽和尖冠）约占上半身的一半；蛇尾粗壮。
- 头：翠绿兜帽金边、额头蓝宝石、金色尖冠；**两只眼睛一样大、一样高、都看得见**、发白发亮、紫色眼影；两颗白色小毒牙；墨绿头发。
- 衣服：金翠胸衣、金臂环、金爪手套、金腰带和两根向下弯的金鳍刺。
- 蛇尾：深翠绿背鳞带亮绿菱形花纹、浅黄绿腹鳞一节一节，两种颜色分得开；从腰到尾尖慢慢变细，轮廓圆滑。
- A：上身挺直、两只爪子抬在胸前、蛇尾平铺在身后地上；B：上身一样、蛇尾在身下盘成一圈，比 A 窄。从冠尖到蛇尾贴地处约 770 px（约 70 格），最低处都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- A、B 两张都画完后，最后写 `outputs/cassiopeia-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/cassiopeia_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/cassiopeia/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_wukong_hd.py` / `design_ziggs_hd.py` 的做法，绝不按更少的行采样），和已合并的中单法师、娜美（鱼尾）按游戏里的大小并排，**早点给用户看 PPU 对比**（1.2 / 1.3 / 1.5 并排），给用户挑 A / B 和定大小。蛇尾很宽：A 的宽度要和其它英雄比一比（团战里挡视线）。
- 定下后第 1 步按游戏格子重画，再自己做动作帧（塔姆 / 普朗克 / 悟空的方式，无损：只平移、整块直角转、整行移）。**没有腿**：跑 = 蛇尾整段左右摆（英雄联盟 cassiopeia_run 是身体前探、尾巴 S 形摆），不要拆腿。英雄联盟的动作：普攻 cassiopeia_attack1 / attack2；Q 瘟毒爆炸 cassiopeia_spell1；W 剧毒迷雾 cassiopeia_spell2；E 双生毒牙 cassiopeia_spell3；R 石化凝视 cassiopeia_spell4；跑 cassiopeia_run；死亡 cassiopeia_death。
