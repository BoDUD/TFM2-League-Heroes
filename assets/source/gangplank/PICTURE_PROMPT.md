# 普朗克（海洋之灾）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 普朗克是**比尔吉沃特的海盗船长**：魁梧、敦实的中年壮汉，**肚子圆、胸膛宽**。头戴一顶**很大的黑色海盗帽**（帽檐两边高高翘起，正面看像一弯**月牙**）；**花白偏棕的长络腮胡**，胡子尖在下巴下面用一根**红布条扎成一束**，**两撇浓密的八字胡**，**皱眉、凶狠的脸**。上身**赤膊**，胸口和肚子露出肉色皮肤（有深色纹身），肩上一圈**青绿色的高领皮护肩**和交叉的深色皮带；小臂缠**红布**、戴**棕色皮护腕**；腰上一条**红色的宽腰带**，外面一条**棕色皮带和金扣**；背后拖着一件**深紫色的长外套下摆**（边上有金色的花纹，下摆破成几条），**深灰绿色的裤子**，**棕色翻口的长靴**（翻口有金边）。武器两件：近侧手一把**金色的燧发手炮**（又粗又短的金色炮管，雕花），远侧手一把**深色的锯齿弯刀**，**刀尖一段烧得橙红发亮**。请 Codex 画**两张全身像**（同一个普朗克，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、8a）。站得很稳、两脚分开，**近侧手把金色手炮扛在近侧肩上**（手在**脸的旁边，绝不能挡住脸**），**远侧手的弯刀垂向前下方**，刀尖朝前。
> - **B：备战姿势**（附图 8b 只看大小和地面线）。两脚分开、膝盖微弯，**近侧手把手炮端在腰间、炮口朝前**，**远侧手的弯刀斜举在身前**（刀尖朝前上方，不高过肩），整个人更有攻击性。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的厄运小姐（同是比尔吉沃特的海盗）、斯维因（长外套）和嘉文四世（格子密度），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：魁梧的壮汉，**头（连帽子和胡子）约占身高的四分之一多一点**（约 20 格，帽子约 7 格），肩宽、肚子圆、腿粗短有力；不要大头娃娃，也不要写实的细长比例。
> - **头**（附图 3 特写）：黑色月牙海盗帽（几档黑灰，有亮边，不要一团死黑）；**两只眼睛一样大、一样高**，眉头皱着；鼻子明显；八字胡和长胡子是**花白偏棕**，分几档颜色，下巴下面红布条扎一束。
> - **身体**：赤膊的胸口和圆肚子（肉色分几档，胸口有深色纹身），青绿色高领护肩，交叉皮带，红布缠小臂，红腰带 + 棕皮带金扣，背后深紫长外套的下摆（金边、破成几条），深灰绿裤子，棕色翻口长靴。
> - **武器**：金色燧发手炮（粗短、金色有雕花和亮点），深色锯齿弯刀（刀背有锯齿，刀尖橙红发亮）；两件都完整画在画面里。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只鞋底落在同一条地面线上。
> - **画布用正方形 1536×1536**。**从帽子顶到鞋底约 792 px，也就是约 72 格**，鞋底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。帽子、手炮、弯刀、外套下摆全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。黑帽子、花白胡子、肉色皮肤、青绿护肩、红布和红腰带、金手炮和金扣、深紫外套、深灰绿裤子、棕靴子、深色弯刀和橙红刀尖要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**黑帽子、深紫外套、深灰绿裤子都很暗，一定要有偏亮的边**，不然在深色背景上会糊成一团。
> - 不画任何特效（枪口火光、火药桶、爆炸、炮弹雨都放到第 3 步单独画）；不画火药桶，不画地面，不画影子。
> - 交付：`outputs/gangplank-picture/gangplank-A.png`、`gangplank-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/gangplank-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/gangplank_picture_done.zip`。

## 附图（在压缩包 `gangplank_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_gangplank_idle.png` | 英雄联盟原版普朗克的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势（手炮扛在肩上、弯刀朝前下） |
| `refs/2_gangplank_frontal.png` | 同一帧，正面 | 护肩、皮带、腰带、裤子和靴子怎么排 |
| `refs/3_gangplank_head.png` | 头部特写 | 月牙海盗帽、皱眉的脸、八字胡、红布扎的胡子 |
| `refs/4_gangplank_back.png` | 同一帧的背后 | 背后的深紫长外套下摆、帽子后面 |
| `refs/5_gangplank_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_gangplank_shot.png` | Q 枪火谈判开枪的一帧 | 手炮的样子、端枪的方法（B 的手炮拿法参考） |
| `refs/7_gangplank_side.png` | 同一帧，接近侧面 | 帽子、肚子、外套下摆从侧面看的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 他的大小、地面线（灰）；**姿势按文字：手炮端在腰间，弯刀斜举在身前** |
| `style/11_style_missfortune.png` | 本包的厄运小姐，8 倍放大，一格 = 一个像素 | **只看风格**：比尔吉沃特海盗的帽子、红色和金色在格子上怎么画 |
| `style/12_style_swain.png` | 本包的斯维因（8 倍） | **只看风格**：长外套下摆、深色衣服的亮边、脸 |
| `style/13_style_jarvaniv.png` | 本包的嘉文四世（8 倍） | **只看风格**：格子密度、描边、每种材质分几档 |

## 提示词：`gangplank-A.png` / `gangplank-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a BURLY MIDDLE-AGED PIRATE CAPTAIN - heavy-set, a broad chest and a round belly; a BIG BLACK PIRATE HAT whose brim turns up high on both sides (a CRESCENT shape seen from the front); a long GREYISH-BROWN BEARD tied into a tail under the chin with a RED CLOTH TIE, a thick MOUSTACHE, a FROWNING, STERN face; a BARE CHEST and belly (skin with dark tattoos) under a high TEAL-GREEN leather shoulder collar and crossed dark straps; RED CLOTH wrapped on the forearms and brown leather bracers; a wide RED SASH at the waist with a BROWN BELT and a GOLD BUCKLE; a long DARK-PURPLE COAT hanging behind him in torn tails with GOLD trim; DARK GREY-GREEN trousers; BROWN CUFFED BOOTS with gold-trimmed cuffs. Two weapons: in the NEAR hand a GOLDEN FLINTLOCK HAND CANNON (a short thick ornate gold barrel), in the FAR hand a DARK SERRATED CUTLASS whose TIP GLOWS ORANGE-HOT (1 his idle, 3/4 view facing right - the look, the ANGLE, pose A; 2 the same from the front: the collar, the straps, the sash, the trousers, the boots; 3 the head close-up: the crescent hat, the frowning face, the moustache, the tied beard; 4 the same from behind: the dark-purple coat tails, the hat's back; 5 the official illustration: his mood and colours; 6 his pistol shot: the hand cannon and how he holds it; 7 the idle nearly from the side: the depth of the hat, the belly and the coat). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a pirate's hat, red and gold on the grid (11), a long dark coat with lit edges and a face (12), the square density, the outline and the number of shades a material gets (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hat, the hand cannon, the cutlass and the coat tails whole); both soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 792 px (about 72 squares) from the top of his hat to his soles.
PROPORTIONS: a burly man - the head with the hat and the beard a little more than ONE QUARTER of his height (about 20 squares, the hat about 7 of them); broad shoulders, a round belly, thick strong legs; NOT a big-headed chibi and NOT realistic slim proportions.
THE HEAD: the black crescent hat in a few dark grey-black shades with a LIGHT EDGE (never one dead-black blob); TWO EYES of the SAME size at the SAME height under frowning brows; a clear nose; the moustache and the long beard GREYISH-BROWN in a few shades, the red tie under the chin.
THE BODY: the bare chest and round belly in a few skin shades with dark tattoo marks, the teal-green collar, the crossed straps, the red forearm wraps, the red sash with the brown belt and gold buckle, the dark-purple coat tails behind him with gold trim, torn into a few strips, the dark grey-green trousers, the brown cuffed boots.
THE WEAPONS: the golden hand cannon (short, thick, ornate, gold with bright highlights), the dark serrated cutlass (a saw-toothed back, the tip glowing orange-red); both whole.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the black hat, the dark-purple coat and the dark trousers with LIGHTER EDGES so they never turn into one dark mass; the hat, the beard, the skin, the teal collar, the red cloth, the gold, the purple coat, the trousers, the boots, the dark blade and its orange tip clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no smoke, no fire, no explosion), no barrel, no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (gangplank-A.png): his idle (images 1 and 8a) - a steady wide stance, the NEAR hand resting the golden hand cannon on his NEAR SHOULDER (the hand BESIDE his face, never covering it), the FAR hand holding the cutlass down and forward, its tip to the front; the face to the front-right, frowning.
POSE B (gangplank-B.png): a READY STANCE - the SAME pirate with the SAME 11-px squares: feet apart, knees slightly bent, the NEAR hand holding the hand cannon AT HIS HIP, its muzzle pointing forward, the FAR hand holding the cutlass slanted up in front of him (the tip forward and up, never above his shoulder); the face to the front-right, frowning (image 8b shows only his size and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，帽子、手炮、弯刀、外套下摆完整，不出画。
- 比例：魁梧的壮汉，头（连帽子、胡子）约占身高四分之一多一点（约 20 格）；肩宽、肚子圆、腿粗。
- 头：黑色月牙海盗帽分几档、有亮边；**两只眼睛一样大、一样高**，皱眉；八字胡、花白偏棕的长胡子，下巴下红布条扎一束。
- 身体：赤膊（有纹身）、青绿高领护肩、交叉皮带、红布缠小臂、红腰带 + 棕皮带金扣、背后深紫长外套下摆（金边、破成几条）、深灰绿裤子、棕翻口长靴。
- 武器：金色燧发手炮、深色锯齿弯刀（刀尖橙红）。
- A：手炮扛在近侧肩上（手在脸旁，不挡脸）、弯刀朝前下；B：手炮端在腰间朝前、弯刀斜举在身前。从帽子顶到鞋底约 792 px（约 72 格），鞋底都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/gangplank-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/gangplank_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/gangplank/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_ziggs_hd.py` / `design_jarvaniv_hd.py` 的做法，绝不按更少的行采样），和已合并的壮汉 / 海盗（厄运小姐、斯维因、嘉文四世、内瑟斯、奥拉夫、潘森）按游戏里的大小并排，给用户挑 A / B、定游戏里多高和 PPU（先出 PPU 1.5 / 1.3 / 1.2 的密度对比：用户嫌高清，吉格斯降到了 1.2）。
- 定下后第 1 步按游戏格子重画，再自己做动作帧（嘉文 / 吉格斯的方式，无损：只整块平移、整行移；**手和武器只能整块平移，不按肩转、不相对身体上下挪**；手炮和弯刀是刚体，每帧都用设计里的同一件）；走路：两腿用设计里自己的整条腿（不用 Codex 画的腿），落脚下沉 + 两腿交错时整个人弹起一格。英雄联盟的动作：普攻 Gangplank_Attack1 / Attack2 / Crit / Passive_Attack（弯刀砍）；Q 枪火谈判 Gangplank_spell1（手炮开枪）；W 坏血病疗法 Gangplank_Spell2（吃橘子）；E 火药桶 Gangplank_spell3（放桶）；R 加农炮幕 Gangplank_spell4（举手发信号）；跑 Gangplank_Run；死亡 Gangplank_Death。
