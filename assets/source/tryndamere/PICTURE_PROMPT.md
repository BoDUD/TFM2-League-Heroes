# 泰达米尔（蛮王）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 蛮王还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（弓步站着、身体前倾，右手握着大刀拖在身后，左手空着张开在身前）；**B = 英雄联盟 R（无尽怒火）**（挺胸仰头怒吼，大刀垂在身后）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行，连盔角）。
> - **长相照英雄联盟原版**（附图 1–6）：一个**魁梧的蛮族战士**，晒成**古铜色的皮肤**，赤裸上身、胸肌和手臂很粗。头上一顶**深灰黑色的铁头盔**，盔顶两侧**一对向上弯的短黑角**，额头正中一颗**青绿色宝石**，盔沿护住两颊，露出脸：浓眉、凶狠的眼睛、**短黑胡子**，咧嘴怒吼。头盔后面垂下一大把**黑色长发**，披到背上。
> - **装备**：左肩一块**深灰色大肩甲**，上面有**青绿色宝石**和花纹；两只前臂**缠着灰白色布条**，护腕是深色皮革；胸前斜挎一条细皮带；腰间一圈**灰白色布腰带**，中间垂一块**深色兽首护裆**（嵌一颗青绿色宝石）；下身是**层叠的深灰铁甲裙**（一片片带花纹的甲片），下面露出**深青色的鳞甲裙摆**，锯齿边；**深灰黑色靴子**。
> - **武器**：一把**巨大的深灰黑色弯刀**，刀身宽厚、刀背一排**锯齿尖刺**，银白色刃口；刀柄末端和护手处各有一颗**发青光的圆宝珠**（护手那颗很大）；刀和他的身高差不多长。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的瑟提、凯隐、韦鲁斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头（连盔角）比英雄联盟模型大一些（约占身高三分之一），身体宽而壮（和瑟提差不多），腿稍短；盔角、青色宝石、刀上的青光宝珠、白布缠手画大一点，小尺寸下才看得出来。头盔、甲裙、刀都是深灰黑色，要用**深灰、蓝灰几档颜色加银白亮边**画出甲片和锯齿，不要糊成一整块黑。
> - **3/4 正面朝右**，脸朝向观众：两只眼睛、胡子和张开的嘴都要看得见，不能画成背影（英雄联盟原版待机的身体是侧过去的，这里转成正面一些）。
> - 不画任何特效（旋风斩的刀光、怒吼的冲击波、怒火的红光第 3 步再单独画）；鞋底是最低点，平平地落在一条地面线上（游戏在脚下画血条）。整把刀都要在画面里，刀尖不能出画。
> - 交付：`outputs/tryndamere-picture/tryndamere-model-A.png`、`outputs/tryndamere-picture/tryndamere-model-B.png`（都是 1024×1536 竖版、真透明背景，人物从盔角顶到鞋底约 1200 px）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_tryndamere_league_front.png` | 英雄联盟原版蛮王，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_tryndamere_league_frontal.png` | 同一帧，更正面一点 | 胸口、腰带、护裆、甲裙、两只手 |
| `refs/3_tryndamere_league_head.png` | 头和肩的特写 | 角盔、额头宝石、脸、胡子、黑发、肩甲 |
| `refs/4_tryndamere_league_side.png` | 同一帧的侧面（背后） | 黑色长发、刀的宽度和锯齿 |
| `refs/5_tryndamere_splash.png` | 官方加载画面 | **看气氛**（怒吼的脸、角盔、刀） |
| `refs/6_tryndamere_league_r.png` | 英雄联盟 R 怒吼那一帧 | B 的姿势（挺胸仰头） |
| `refs/7_tryndamere_league_e.png` | 英雄联盟 E 旋风斩中间一帧 | 刀横着时的样子 |
| `style/8_style_sett.png` | 你之前的瑟提像素图 | **只看风格**（赤膊壮汉） |
| `style/9_style_kayn.png` | 你之前的凯隐像素图 | **只看风格**（大型兵器） |
| `style/10_style_varus.png` | 你之前的韦鲁斯像素图 | **只看风格**（最新一张） |

## 提示词 A：`tryndamere-model-A.png`（英雄联盟待机：前倾弓步，大刀拖在身后）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the chest, the cloth belt, the beast-head belt plate, the armoured skirt, both hands; 3 the head and shoulders close-up: the horned helmet, the teal forehead gem, the face and beard, the long black hair, the shoulder plate; 4 the same pose from behind: the long black hair, the width and the serrated back of the sword; 5 the official illustration, for the mood; 6 League's Undying Rage roar, the pose of version B; 7 League's Spinning Slash, the sword held flat). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a bare-chested muscular brawler, image 9 a fighter with a huge weapon, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1200 px tall from the tips of the helmet horns to the soles, centred, comfortable transparent margins, nothing cut off (the whole sword inside the picture).
The character: Tryndamere, the Barbarian King: a huge, broad, heavily muscled male barbarian warrior. HEAD: a dark grey-black iron HELMET with a pair of short black HORNS curving up from its sides, a TEAL-GREEN gem in the middle of the forehead, cheek guards framing the face; the face visible: thick dark brows, fierce eyes, a short black BEARD, the mouth open in a battle snarl; a big mane of long BLACK HAIR falls from under the helmet down his back. BODY: bare bronze-tanned skin, a massive chest and thick arms; a big dark grey PAULDRON on his left shoulder with teal-green gems and engraved trim; both forearms WRAPPED IN GREY-WHITE CLOTH bandages with dark leather bracers; a thin leather strap across the chest; a grey-white CLOTH SASH round the waist with a dark BEAST-HEAD belt plate hanging in front, set with a teal gem. LEGS: a layered skirt of dark grey iron PLATES with engraved scroll patterns, under it a dark TEAL SCALE-MAIL skirt with a jagged hem; heavy dark grey-black boots. SWORD: a HUGE dark grey-black curved greatsword, as long as he is tall, with a broad heavy blade, a row of SERRATED SPIKES along its back and a silver-white cutting edge; a big GLOWING TEAL-CYAN ORB set at the guard and a smaller one at the pommel.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height with the helmet), a broad powerful body like image 8, legs a little shorter; the helmet horns, the teal gems, the glowing orbs on the sword and the white cloth wraps drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes, the beard and the snarling mouth visible, nothing covers the face.
Pose: League's own idle (image 1), turned more toward the viewer: a wide low stance leaning forward, facing image right, feet apart, knees bent; the arm on the image-LEFT side holds the greatsword by its grip low behind him, the blade trailing down and back on the ground side with its tip near the floor behind his back foot; the other arm forward and slightly raised in front of him, the open hand clawed, ready; the black hair hanging behind the helmet; the head turned toward the viewer. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the sword tip may touch that line but not go below it.
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The helmet, the armoured skirt, the boots and the sword are DARK GREY-BLACK in the game: draw them in dark grey and blue-grey shades with silver-white lit edges and highlights (never one flat black mass - black is only the outline), so their plates, engravings and serrations read; the skin warm bronze with reddish-brown shadows, the hair black with dark blue-grey highlights, the cloth wraps grey-white, the scale skirt dark teal, the gems and the sword orbs a bright teal-cyan; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects beyond the glow drawn on the sword orbs and the gems, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`tryndamere-model-B.png`（英雄联盟 R 无尽怒火：挺胸仰头怒吼，大刀垂在身后）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the chest, the cloth belt, the beast-head belt plate, the armoured skirt, both hands; 3 the head and shoulders close-up: the horned helmet, the teal forehead gem, the face and beard, the long black hair, the shoulder plate; 4 the same pose from behind: the long black hair, the width and the serrated back of the sword; 5 the official illustration, for the mood; 6 League's Undying Rage roar, the pose of version B; 7 League's Spinning Slash, the sword held flat). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a bare-chested muscular brawler, image 9 a fighter with a huge weapon, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1200 px tall from the tips of the helmet horns to the soles, centred, comfortable transparent margins, nothing cut off (the whole sword inside the picture).
The character: Tryndamere, the Barbarian King: a huge, broad, heavily muscled male barbarian warrior. HEAD: a dark grey-black iron HELMET with a pair of short black HORNS curving up from its sides, a TEAL-GREEN gem in the middle of the forehead, cheek guards framing the face; the face visible: thick dark brows, fierce eyes, a short black BEARD, the mouth open in a battle snarl; a big mane of long BLACK HAIR falls from under the helmet down his back. BODY: bare bronze-tanned skin, a massive chest and thick arms; a big dark grey PAULDRON on his left shoulder with teal-green gems and engraved trim; both forearms WRAPPED IN GREY-WHITE CLOTH bandages with dark leather bracers; a thin leather strap across the chest; a grey-white CLOTH SASH round the waist with a dark BEAST-HEAD belt plate hanging in front, set with a teal gem. LEGS: a layered skirt of dark grey iron PLATES with engraved scroll patterns, under it a dark TEAL SCALE-MAIL skirt with a jagged hem; heavy dark grey-black boots. SWORD: a HUGE dark grey-black curved greatsword, as long as he is tall, with a broad heavy blade, a row of SERRATED SPIKES along its back and a silver-white cutting edge; a big GLOWING TEAL-CYAN ORB set at the guard and a smaller one at the pommel.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height with the helmet), a broad powerful body like image 8, legs a little shorter; the helmet horns, the teal gems, the glowing orbs on the sword and the white cloth wraps drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes, the beard and the roaring mouth visible, nothing covers the face.
Pose: League's Undying Rage (image 6): standing firm with the feet apart and the knees a little bent, facing image right; the chest thrust out and the shoulders pulled back, the head tilted up and back, ROARING with the mouth wide open; the free arm bent with the fist clenched at his side; the arm on the image-LEFT side holds the greatsword low behind him, the blade hanging down and back with its tip near the floor behind his back foot; the black hair swinging behind the helmet. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the sword tip may touch that line but not go below it.
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The helmet, the armoured skirt, the boots and the sword are DARK GREY-BLACK in the game: draw them in dark grey and blue-grey shades with silver-white lit edges and highlights (never one flat black mass - black is only the outline), so their plates, engravings and serrations read; the skin warm bronze with reddish-brown shadows, the hair black with dark blue-grey highlights, the cloth wraps grey-white, the scale skirt dark teal, the gems and the sword orbs a bright teal-cyan; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects beyond the glow drawn on the sword orbs and the gems (no red rage aura - that comes later as a separate effect), no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物和整把刀都完整。
- 深色角盔（一对短黑角、额头青绿宝石），脸露出来：两只眼睛、短黑胡子、张开的嘴；盔后一大把黑色长发。
- 古铜色赤膊上身、左肩深灰大肩甲、两只前臂缠白布；灰白布腰带和兽首护裆。
- 层叠深灰甲裙下露出深青色鳞甲裙摆；深灰黑靴子。
- 巨大的深灰黑弯刀：刀背锯齿、银白刃口、护手和刀柄末端的青光圆珠；甲和刀有银白亮边，不是一整块黑。
- 鞋底是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/tryndamere-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
