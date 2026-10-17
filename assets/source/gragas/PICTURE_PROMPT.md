# 古拉加斯（酒桶）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 酒桶还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**那只大酒桶的位置**，人、胡子、衣服、酒桶完全一样：**A = 英雄联盟里的待机：大酒桶用粗绳背在背上，桶底（带木塞）朝向画面左边露出来**（附图 1、2、4）；**B = 英雄联盟里 W 喝酒的姿势：大酒桶扛在远侧肩膀上，近侧手托着，桶口凑在胡子边上**（附图 8）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 36–38 行，侧面和 3/4 正面两张）。
> - **长相照英雄联盟原版**（附图 1–9）：酒桶古拉加斯，一个**又高又胖的大块头酒鬼**，豪爽、快活、醉醺醺。**光头**（头顶淡肤色、有几道皱纹）、**粗浓的橙红色眉毛**、**眯着的小眼睛**、**大鼻子**；**一大把橙红色长胡子**从下巴一直垂到肚子上，**编成几股辫子**，辫梢用**银灰色的铁环**扎着，两边鬓角的胡子像火焰一样往外翘。
> - **身体**：**超大的圆肚子**（肚子是全身最宽的地方），**淡米黄色皮肤**，皮肤上有几道**浅色的疤和暗红的划痕**（肚子上一个 X 形疤）；**很宽的肩膀、很粗的手臂**，前臂和手腕缠着**棕色粗麻绳**；**拳头又大又粗**。**上身不穿衣服**，一根**粗麻绳**从远侧肩膀斜着绕过胸口，拴着背上的酒桶。腰下是**短短的深蓝色破边短裤（下摆撕成锯齿）**，**光着两只大脚**（脚趾分明），腿短粗、膝盖有绳子绑着。
> - **酒桶**：**一只很大的木酒桶**（差不多和他的上半身一样大），**暖棕色木板**、**几道铁灰色的铁箍**，桶底是**八角形的木盖**，中间塞着**一个方形的浅色木塞**。
> - **姿势**（附图 1、2、4 = A；附图 8 = B）：3/4 正面朝右，挺着大肚子、两腿岔开稳稳地站着，**两只脚都踩在地面线上**。A：酒桶背在背上偏画面左边，桶底和木塞朝着画面左前方，两只手垂在身体两边握拳（**不要举手**）。B：酒桶扛在他远侧（画面左边）的肩膀上、斜着往上，近侧手从下面托着桶，桶口凑到胡子边上；远侧手垂在身旁。**脸（眼睛、眉毛、鼻子）和两只手都不能被挡住**。
> - **风格和比例照附图 10–12**（之前让你画的诺提勒斯、阿利斯塔、蛮王）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；**头按原版比例，不要画成大头娃娃**（他的头相对身体很小，肚子很大，这是他的特色）；**整体收紧凑，不要画成巨大的块**（游戏里他和其他英雄差不多大）。颜色：**皮肤淡米黄（亮部偏奶白、暗部偏棕灰）、胡子和眉毛橙红（亮部橙、暗部深红棕）、短裤深蓝、绳子棕色、酒桶暖棕木色 + 铁灰箍、辫子环银灰**；深色和浅色之间要有清楚的分界，不要糊成一团。
> - **画布用竖版 1024×1536**：从头顶到脚底约 560 px（B 的酒桶会比头高，留足边距）；酒桶、绳子都在画面里，不能出画。
> - 不画任何特效（酒水、泡沫、爆炸、醉酒气泡第 3 步再单独画）；脚底是最低点，平平地落在一条地面线上（游戏在脚下画血条）。
> - 交付：`outputs/gragas-picture/gragas-model-A.png`、`outputs/gragas-picture/gragas-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `gragas_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_gragas_league_front.png` | 英雄联盟原版酒桶待机，3/4 朝右 | 颜色、形状、A 的姿势（酒桶背在背上） |
| `refs/2_gragas_league_frontal.png` | 同一帧，正面 | 脸、胡子辫子、胸前的绳子、肚子上的疤、短裤 |
| `refs/3_gragas_league_head.png` | 头和胡子的特写 | 光头、眉毛、眯眼、大鼻子、编辫的胡子和铁环 |
| `refs/4_gragas_league_back.png` | 同一帧的背后 | 酒桶怎么用绳子背在背上 |
| `refs/5_gragas_splash.png` | 官方加载画面 | 气质（豪爽、醉醺醺） |
| `refs/6_gragas_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 背着酒桶怎么跑 |
| `refs/7_gragas_league_actions.png` | 普攻、Q 扔酒桶、E 肉弹冲击、大招的瞬间 | 手和酒桶怎么动 |
| `refs/8_gragas_league_drink.png` | W 喝酒：酒桶扛在肩上 | **B 的酒桶的位置** |
| `refs/9_gragas_league_side.png` | 待机的侧面（朝右） | 侧面看肚子和胡子（侧面时酒桶挂在近侧腰后，挡住一半肚子） |
| `style/10_style_nautilus.png` | 你之前的诺提勒斯像素图 | **只看风格**（最近通过的一张） |
| `style/11_style_alistar.png` | 你之前的阿利斯塔像素图 | **只看风格**（同是坦克大块头） |
| `style/12_style_tryndamere.png` | 你之前的蛮王像素图 | **只看风格**（同是赤膊的壮汉） |

## 提示词 A：`gragas-model-A.png`（酒桶背在背上）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture, the keg slung on his back; 2 the same from the front: the face, the braided beard, the rope across the chest, the scars on the belly, the shorts; 3 the head close-up: bald head, bushy brows, squinting eyes, big nose, the braided beard with its iron rings; 4 the same pose from behind: how the keg is tied on his back; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells: how the hands and the keg move; 8 his drink with the keg on his shoulder - not used in this version; 9 the same idle from the side: the keg then hangs at his near hip, half over the belly). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 another big tank, image 12 another bare-chested brawler).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 560 px from the top of his head to the soles of his feet, centred, comfortable transparent margins, nothing cut off (the whole keg and the rope inside the picture).
The character: Gragas, the Rabble Rouser, a huge, jolly, drunken brawler. A BALD HEAD (pale skin, a few wrinkles), BUSHY ORANGE-RED BROWS, small SQUINTING EYES, a BIG NOSE, and a LONG ORANGE-RED BEARD falling from his chin over his belly, BRAIDED into several plaits tied with SILVER-GREY IRON RINGS, the sideburns flaring out like flames. BODY: an ENORMOUS ROUND BELLY (the widest part of him), PALE BEIGE SKIN with a few light scars and dark-red scratches (an X-shaped scar on the belly), very broad shoulders, very thick arms, the forearms and wrists wrapped in BROWN ROPE, HUGE FISTS. NO SHIRT: a THICK ROPE runs from his far shoulder across his chest and holds the keg on his back. SHORT DARK-BLUE RAGGED SHORTS (the hem torn into zigzags), BARE BIG FEET with clear toes, short thick legs with rope tied below the knees. THE KEG: a VERY BIG WOODEN KEG (about as big as his upper body), WARM BROWN WOODEN STAVES, a few IRON-GREY HOOPS, an OCTAGONAL WOODEN LID with a SQUARE PALE WOODEN CORK in its middle. Here the keg is SLUNG ON HIS BACK (images 1, 2 and 4), toward the image left, its lid and cork turned toward the viewer on the image left; both hands hang at his sides as fists (NOT raised).
Proportions: game-sprite proportions like images 10-12, but keep HIS OWN proportions: a SMALL HEAD on a HUGE BODY - do NOT make a big-headed chibi; the belly is his signature. Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: League's own idle (images 1 and 2): belly out, legs apart, both feet planted firmly. The soles of his feet are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 10-12 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the skin pale beige (creamy highlights, brown-grey shadows), the beard and brows orange-red (orange highlights, dark red-brown shadows), the shorts dark blue, the rope brown, the keg warm brown wood with iron-grey hoops, the beard rings silver-grey; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no beer, no foam, no explosions, no bubbles, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`gragas-model-B.png`（酒桶扛在肩上）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look of this picture; 2 the same from the front: the face, the braided beard, the rope across the chest, the scars on the belly, the shorts; 3 the head close-up: bald head, bushy brows, squinting eyes, big nose, the braided beard with its iron rings; 4 the same from behind; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells: how the hands and the keg move; 8 HIS DRINK WITH THE KEG HOISTED ON HIS SHOULDER - the keg position of this picture; 9 the idle from the side). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 another big tank, image 12 another bare-chested brawler).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 560 px from the top of his head to the soles of his feet, centred, comfortable transparent margins, nothing cut off (the whole keg and the rope inside the picture).
The character: Gragas, the Rabble Rouser, a huge, jolly, drunken brawler. A BALD HEAD (pale skin, a few wrinkles), BUSHY ORANGE-RED BROWS, small SQUINTING EYES, a BIG NOSE, and a LONG ORANGE-RED BEARD falling from his chin over his belly, BRAIDED into several plaits tied with SILVER-GREY IRON RINGS, the sideburns flaring out like flames. BODY: an ENORMOUS ROUND BELLY (the widest part of him), PALE BEIGE SKIN with a few light scars and dark-red scratches (an X-shaped scar on the belly), very broad shoulders, very thick arms, the forearms and wrists wrapped in BROWN ROPE, HUGE FISTS. NO SHIRT: a THICK ROPE runs from his far shoulder across his chest. SHORT DARK-BLUE RAGGED SHORTS (the hem torn into zigzags), BARE BIG FEET with clear toes, short thick legs with rope tied below the knees. THE KEG: a VERY BIG WOODEN KEG (about as big as his upper body), WARM BROWN WOODEN STAVES, a few IRON-GREY HOOPS, an OCTAGONAL WOODEN LID with a SQUARE PALE WOODEN CORK in its middle. Here the keg is HOISTED ONTO HIS FAR SHOULDER (image 8), on the image left, slanting up, his near hand under it holding it, its open end tipped toward his beard as if he is about to drink; his far hand hangs at his side as a fist.
Proportions: game-sprite proportions like images 10-12, but keep HIS OWN proportions: a SMALL HEAD on a HUGE BODY - do NOT make a big-headed chibi; the belly is his signature. Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: belly out, legs apart, both feet planted firmly. The soles of his feet are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 10-12 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the skin pale beige (creamy highlights, brown-grey shadows), the beard and brows orange-red (orange highlights, dark red-brown shadows), the shorts dark blue, the rope brown, the keg warm brown wood with iron-grey hoops, the beard rings silver-grey; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no beer, no foam, no explosions, no bubbles, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，人物、整只酒桶和绳子都完整。
- 光头、橙红浓眉、眯眼、大鼻子；橙红长胡子编成辫子、辫梢有银灰铁环，鬓角往外翘。
- 超大圆肚子、淡米黄皮肤、肚子上的 X 形疤；粗手臂缠棕绳、大拳头；胸前斜挂粗麻绳；深蓝锯齿边短裤；光脚、脚趾分明。
- 大木酒桶：暖棕木板、铁灰箍、八角形桶盖、方形浅色木塞。A 背在背上、桶盖朝画面左边；B 扛在远侧肩上、近侧手托着、桶口凑到胡子边。
- 头小肚子大（原版比例），不要大头娃娃；脸和两只手没被挡住；整体紧凑。
- 脚底是最低点，落在一条水平线上；没有任何特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/gragas-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/gragas/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 36–38 行，**侧面朝右 + 3/4 正面两张**，记忆 side-view-design；酒桶另算，不能让模型过大）。
- 技能动作里酒桶和托桶的手是一整块部件，只做平移和 90° 整转，不按任意角度转；动作全用侧面造型，只有待机和 BP 卡用 3/4 正面。
