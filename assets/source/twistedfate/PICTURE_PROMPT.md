# 崔斯特：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 崔斯特还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站直、重心在后腿，近侧手在腰边捏着一把扇开的三张牌，远侧手臂自然下垂）；**B = 亮牌的站姿**（近侧手把扇开的三张牌举在胸前给人看，远侧手叉腰、把外套撑开露出红色里衬）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行，连帽子）。
> - **长相照英雄联盟原版**（附图 1–5）：**黑色宽檐帽**（平顶圆帽身、宽帽檐两边微微上翘，帽檐一圈细金边、帽檐底面暗红色、帽身前面一枚小金贝壳饰物）；古铜色皮肤、下巴一圈黑色短胡子连着山羊胡和小胡子、黑色长直发披到肩后，**眼睛在帽檐下发淡青色的光**（附图 3）；外套的**高立领**像小披肩一样立在脖子和肩后（赭金色花纹布、金边）。
> - **衣服**：**黑色长风衣**拖到脚踝、前面敞开，每条边都镶**金边**，里衬是**深红色**（外套在腿后飘起时露出来）；袖口是华丽的**金色袖箍**和白色衬衫袖口；里面是**橙红色马甲**配金纽扣和圆形金扣、白色领巾，棕色皮带挂小皮包，**黑裤子**，**棕色皮质长靴**带金边、靴尖微尖。
> - **牌是他的标志道具，必须画清楚**：近侧手的手指间夹着**一把扇开的三张牌**，牌面朝外：**蓝牌、红牌、金牌**（附图 6 是英雄联盟自己的牌面：蓝牌上一个人影、红牌上一把剑、金牌上一个锁链纹，牌背是淡紫色带星），每张都有细金边；牌要画大一点，一张牌差不多和他的手一样长，小尺寸下才看得出来（以后每个动作都要看得到牌、牌和手连着）。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的烬、凯特琳、乐芙兰）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（连帽子约占身高三分之一），身材修长；**帽檐在眼睛上面，两只眼睛都要看得见**、一样高一样大，下面是山羊胡；脸不能被帽子或牌挡住。外套、帽子、裤子在游戏里是黑色的，要用**深炭蓝灰的几档颜色加亮边和高光**画出褶子，不要糊成一整块黑；金边亮、红里衬和马甲暖而亮、三张牌是饱和的蓝、红、金。
> - 不画任何特效（发光的牌、飞牌、光环第 3 步再单独画）；脚底是最低点，外套下摆不能低于脚底线（游戏在脚下画血条）。
> - 交付：`outputs/twistedfate-picture/twistedfate-model-A.png`、`outputs/twistedfate-picture/twistedfate-model-B.png`（都是 1024×1536 竖版、真透明背景，人物从帽顶到脚底约 1250 px）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_twistedfate_league_front.png` | 英雄联盟原版崔斯特，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_twistedfate_league_frontal.png` | 同一帧，更正面一点 | 马甲、金扣、高立领 |
| `refs/3_twistedfate_league_head.png` | 头部特写 | 帽子（宽檐、金边、红帽带）、脸、山羊胡、长发 |
| `refs/4_twistedfate_league_side.png` | 同一帧的侧面 | 帽檐的侧面、外套的长度 |
| `refs/5_twistedfate_splash.png` | 官方加载画面 | **看气氛和手里的牌** |
| `refs/6_twistedfate_cards.png` | 英雄联盟自己的牌面贴图：蓝牌、红牌、金牌、牌背、小图标 | 三张牌的颜色和图案 |
| `style/7_style_jhin.png` | 你之前的烬像素图 | **只看风格**（深色衣服配金边的男性角色） |
| `style/8_style_caitlyn.png` | 你之前的凯特琳像素图 | **只看风格**（帽子下面的脸怎么画得清楚） |
| `style/9_style_leblanc.png` | 你之前的乐芙兰像素图 | **只看风格**（金边红里衬的深色长外套、游戏比例的头） |

## 提示词 A：`twistedfate-model-A.png`（英雄联盟待机：站直，近侧手在腰边捏着扇开的三张牌）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-5 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the waistcoat, the buckle, the collar; 3 the head close-up: the hat, the face, the goatee, the hair; 4 the same pose in profile: the hat brim and the coat's length; 5 the official illustration, for the mood and the cards in his hand). Image 6 shows the game's own card designs (blue, red, gold, the back, and the small card icons). Copy from them the costume, the colours, the hat and the cards - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 8 shows how a wide hat sits over a readable face, image 9 a dark coat with gold trim and a red lining).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hat to the soles, centred, comfortable transparent margins, nothing cut off.
The character: Twisted Fate, the Card Master: a roguish card sharp and gambler - a tall, lean, confident man. HAT: a wide-brimmed BLACK hat (a flat round crown, the broad brim curling up a little at both sides) with a thin GOLD edge round the brim, a dark RED underside of the brim and a small GOLD shell-shaped ornament on the front of the crown. HEAD: tanned skin, a short black beard along the jaw with a goatee and moustache, long straight BLACK hair falling behind to his shoulders, a sly confident look; his eyes glow a pale CYAN under the brim (image 3). COLLAR: the tall flared collar of his coat stands up behind his neck and shoulders like a small mantle - an ochre-gold brocade with GOLD edges. COAT: a long BLACK duster coat down to the ankles, open at the front, GOLD trim along every edge and a deep CRIMSON-RED lining that shows where the coat flares behind his legs; ornate GOLD cuffs on the sleeves with white shirt cuffs. Under the coat: a RED-ORANGE waistcoat with gold buttons and a round gold buckle, a white cravat, a brown leather belt with small pouches, BLACK trousers, brown leather KNEE BOOTS with gold trims and slightly pointed toes. THE CARDS (his signature prop, they must be clearly seen): a FAN of THREE playing cards held between the fingers of his near hand, faces out - a BLUE card, a RED card and a GOLD card (image 6 shows League's card designs: the blue card with a figure, the red card with a sword, the gold card with a chain mark, the back lavender with a star), each with a thin gold border; draw the cards big enough to read at small size, each card about as long as his hand.
Proportions: game-sprite proportions like images 7-9 - a bigger head than in the 3D model (the head with the hat about a third of his height), a slim upright body, long legs in the boots; the hat and the cards drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the hat brim sits ABOVE the eyes - BOTH eyes visible under the brim, level and the same size, the goatee below; nothing covers the face (the cards stay beside or below it).
Pose: League's own idle (image 1): standing upright and relaxed in 3/4 view facing image right, the weight on the back leg, the near foot a short step forward; the long coat hanging straight down behind him, its red lining showing at the back hem; his NEAR hand held a little out from the hip at waist height, the fan of three cards spread between its fingers (beside the body, not in front of it); the FAR arm hanging relaxed at his side; the head turned toward the viewer under the hat. The soles are the lowest thing in the picture: the coat's hem ends AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The coat, the hat and the trousers are BLACK in the game: draw them in dark charcoal-navy shades with lit edges and highlights (never one flat black mass - black is only the outline), so their folds read; the gold trims bright, the red lining and the waistcoat warm and bright, the three cards saturated blue, red and gold; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no glowing aura round the cards, no floating cards, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`twistedfate-model-B.png`（亮牌站姿：三张牌举在胸前，远侧手叉腰撑开外套）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-5 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the waistcoat, the buckle, the collar; 3 the head close-up: the hat, the face, the goatee, the hair; 4 the same pose in profile: the hat brim and the coat's length; 5 the official illustration, for the mood and the cards in his hand). Image 6 shows the game's own card designs (blue, red, gold, the back, and the small card icons). Copy from them the costume, the colours, the hat and the cards - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 8 shows how a wide hat sits over a readable face, image 9 a dark coat with gold trim and a red lining).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hat to the soles, centred, comfortable transparent margins, nothing cut off.
The character: Twisted Fate, the Card Master: a roguish card sharp and gambler - a tall, lean, confident man. HAT: a wide-brimmed BLACK hat (a flat round crown, the broad brim curling up a little at both sides) with a thin GOLD edge round the brim, a dark RED underside of the brim and a small GOLD shell-shaped ornament on the front of the crown. HEAD: tanned skin, a short black beard along the jaw with a goatee and moustache, long straight BLACK hair falling behind to his shoulders, a sly confident look; his eyes glow a pale CYAN under the brim (image 3). COLLAR: the tall flared collar of his coat stands up behind his neck and shoulders like a small mantle - an ochre-gold brocade with GOLD edges. COAT: a long BLACK duster coat down to the ankles, open at the front, GOLD trim along every edge and a deep CRIMSON-RED lining that shows where the coat flares behind his legs; ornate GOLD cuffs on the sleeves with white shirt cuffs. Under the coat: a RED-ORANGE waistcoat with gold buttons and a round gold buckle, a white cravat, a brown leather belt with small pouches, BLACK trousers, brown leather KNEE BOOTS with gold trims and slightly pointed toes. THE CARDS (his signature prop, they must be clearly seen): a FAN of THREE playing cards held between the fingers of his near hand, faces out - a BLUE card, a RED card and a GOLD card (image 6 shows League's card designs: the blue card with a figure, the red card with a sword, the gold card with a chain mark, the back lavender with a star), each with a thin gold border; draw the cards big enough to read at small size, each card about as long as his hand.
Proportions: game-sprite proportions like images 7-9 - a bigger head than in the 3D model (the head with the hat about a third of his height), a slim upright body, long legs in the boots; the hat and the cards drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the hat brim sits ABOVE the eyes - BOTH eyes visible under the brim, level and the same size, the goatee below; nothing covers the face (the cards stay beside or below it).
Pose: a confident card-master stance: standing upright in 3/4 view facing image right, the feet a little apart; his NEAR hand raised in front of his chest showing the fan of three cards (blue, red, gold) to the viewer - the cards beside his chest, never in front of his face; his FAR hand resting on his hip, pushing the coat back so its red lining shows; the coat flaring a little behind his legs; the head turned toward the viewer, a slight smirk under the hat. The soles are the lowest thing in the picture: the coat's hem ends AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The coat, the hat and the trousers are BLACK in the game: draw them in dark charcoal-navy shades with lit edges and highlights (never one flat black mass - black is only the outline), so their folds read; the gold trims bright, the red lining and the waistcoat warm and bright, the three cards saturated blue, red and gold; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no glowing aura round the cards, no floating cards, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，帽檐两边没被切掉。
- 黑色宽檐帽：金边、帽檐底面暗红、帽前小金饰；帽檐在眼睛上面，两只淡青色的眼睛都看得见、同一高度、一样大；胡子和长发都在。
- 三张牌清楚：蓝、红、金三种颜色分得开，每张有细金边，夹在近侧手的手指间，牌和手连在一起，没挡住脸。
- 黑外套有金边和红里衬，橙红马甲、金扣、白领巾、金袖箍、棕色长靴都在；黑色部分有亮边和褶子，没有糊成一块黑。
- 脚底是最低点，外套下摆不低于它；没有发光、飞牌、光晕。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/twistedfate-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
