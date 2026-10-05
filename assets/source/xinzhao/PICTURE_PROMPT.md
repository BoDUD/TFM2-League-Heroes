# 赵信：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 赵信还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（两脚分开、膝盖微弯，后手握着长枪斜架在身后，枪尖从前肩上方伸出去，前手空着张开在身前）；**B = 英雄联盟 Q（三重爪击）第三下之后的架枪**（两脚站稳，双手把长枪横举过头顶）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行）。
> - **长相照英雄联盟原版**（附图 1–7）：一位**德玛西亚的武将**，身材匀称结实。**黑色头发往后梳，鬓角和额前有银白色的挑染**；头顶高高**束起一个发髻**，发髻上一个**金色发冠 / 发箍**，后面垂下**两条深紫色的长发带**。脸：剑眉、眼神凌厉、神情严肃，耳朵上一个小小的金耳饰。注意：模型渲染（附图 1–4、6、7）头顶上方那一大团深色带金角的东西是发髻和发带渲染坏了，**发髻照附图 5（官方加载画面）画**：黑色发髻 + 金色发冠 + 飘在后面的深紫发带。
> - **装备**：深色高领；胸前**银白色的鳞片 / 板甲**；外面一件**皇家紫（蓝紫色）的长战袍**，衣边一圈**金色滚边**，前襟一块紫色长布片垂在两腿之间；**后肩（画面左边）一块张开的金色大护肩**，**前肩（画面右边）一块很大的银白色护肩，上面嵌着亮蓝色的装饰**；两只前臂是**棕色皮革护臂**，手上深色露指手套；腰间**棕色皮腰带**，金色扣环；胯两侧**银白色的甲片**；下身**浅紫灰色（薰衣草色）的宽松裤子**；**深灰钢色的护胫和靴子**，带金边。
> - **武器**：一杆**很长的长枪**（约是他身高的 1.4 倍）：**深棕色木枪杆**，隔一段一道**金色箍**；枪头是**紫色的长刃**，刃旁边有一个**银白色的月牙形倒钩**和一条紫色飘带；枪尾是一小截**深铁色的尖锥**。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的凯隐、崔斯特、韦鲁斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头（连发髻）比英雄联盟模型大一些（约占身高三分之一），身材匀称，腿稍短；发髻、金发冠、前肩的蓝饰银护肩、金色后护肩、枪头和月牙倒钩画大一点，小尺寸下才看得出来。紫色战袍、金边、银甲要分得开：**紫色用几档蓝紫加亮边，银甲用几档冷灰加白色高光**，不要糊成一片。
> - **画布用横版 1536×1024**（长枪太长，竖版放不下）：人物从发髻顶到鞋底约 850 px，整杆长枪都要在画面里，枪头、枪尾都不能出画。
> - **3/4 正面朝右**，脸朝向观众：两只眼睛、眉毛都要看得见，不能画成背影。
> - 不画任何特效（突刺的风、横扫的月牙、冲锋的光第 3 步再单独画）；鞋底是最低点，平平地落在一条地面线上（游戏在脚下画血条），枪也不能低于这条线。
> - 交付：`outputs/xinzhao-picture/xinzhao-model-A.png`、`outputs/xinzhao-picture/xinzhao-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `xinzhao_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_xinzhao_league_front.png` | 英雄联盟原版赵信，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_xinzhao_league_frontal.png` | 同一帧，更正面一点 | 胸甲、战袍、腰带、裤子、两只手 |
| `refs/3_xinzhao_league_head.png` | 头和肩的特写 | 脸、银白挑染、金耳饰、高领、两块护肩（头顶那团是渲染坏了的发髻，不要照） |
| `refs/4_xinzhao_league_side.png` | 同一帧的侧面（背后） | 紫色长发带、战袍后摆、长枪的长度和两头 |
| `refs/5_xinzhao_splash.png` | 官方加载画面 | **发髻和发冠照它**；看气氛（严肃的脸、银甲、紫战袍） |
| `refs/6_xinzhao_league_q3.png` | 英雄联盟 Q 第三下之后，长枪横举过头顶 | B 的姿势 |
| `refs/7_xinzhao_league_e.png` | 英雄联盟 E 无畏冲锋，持枪飞身突刺 | 长枪端平时的样子 |
| `style/8_style_kayn.png` | 你之前的凯隐像素图 | **只看风格**（长柄大兵器） |
| `style/9_style_twistedfate.png` | 你之前的崔斯特像素图 | **只看风格**（穿长外衣的人类英雄） |
| `style/10_style_varus.png` | 你之前的韦鲁斯像素图 | **只看风格**（最近通过的一张） |

## 提示词 A：`xinzhao-model-A.png`（英雄联盟待机：长枪斜架在身后）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the chest armour, the coat, the belt, the trousers, both hands; 3 the head and shoulders close-up: the face, the hair, the collar, both shoulder pieces; 4 the same pose from behind: the long purple hair ribbons, the coat's back and the whole spear; 5 the official illustration: copy the TOPKNOT from it, and the mood; 6 League's Three Talon Strike finish with the spear held level over his head, the pose of version B; 7 League's Audacious Charge, the spear held level). In the 3D renders the dark lump with gold horns above his head is the topknot rendered wrongly: ignore it and draw the topknot as image 5 shows. Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a fighter with a long polearm, image 9 a man in a long coat, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 850 px tall from the top of his topknot to the soles, centred, comfortable transparent margins, nothing cut off (the whole spear inside the picture, both ends).
The character: Xin Zhao, the Seneschal of Demacia: a fit, athletic male spear warrior, noble and stern. HEAD: black hair combed back with SILVER-WHITE streaks at the temples and the front, tied up in a high TOPKNOT held by a GOLD crown clasp, two long DARK PURPLE RIBBONS trailing back from it; a stern face with sharp dark brows and fierce eyes, a small gold earring. BODY: a dark high collar; a SILVER-WHITE scale-and-plate breastplate; over it a long ROYAL PURPLE (blue-violet) war coat with GOLD trim on every edge, its front panel hanging down between his legs; a big flaring GOLD shoulder guard on his back shoulder (image left) and a large SILVER-WHITE PAULDRON with BRIGHT BLUE insets on his front shoulder (image right); brown leather forearm guards and dark fingerless gloves; a brown leather belt with a gold buckle; silver-white tasset plates at the hips. LEGS: loose pale LAVENDER-GREY trousers, dark steel greaves and boots with gold trim. SPEAR: a very LONG spear, about 1.4 times his height: a dark brown wooden shaft with GOLD rings along it; its HEAD a long PURPLE blade with a SILVER CRESCENT HOOK beside it and a purple streamer (in image 7 it points forward), its BUTT end a short dark iron spike.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height with the topknot), a fit, balanced body, legs a little shorter; the topknot with its gold clasp, the blue-inlaid silver pauldron, the gold shoulder guard, the spear's point, purple blade and crescent hook drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes and brows visible, nothing covers the face.
Pose: League's own idle (image 1), turned a little more toward the viewer: a wide stance facing image right, feet apart, knees slightly bent; the arm on the image-LEFT side holds the spear at shoulder height, the spear slanting across behind his shoulders: its purple-bladed head low behind him at image left, its iron butt spike high in front of him past his front shoulder at image right; the other arm in front of his belly, the open hand clawed, ready; the purple ribbons hanging behind the topknot. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the spear stays above that line.
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat royal purple with blue-violet lit edges, the trim and the shoulder guard gold, the breastplate and pauldron cool silver-grey with white highlights and bright blue insets, the leather brown, the trousers pale lavender-grey, the boots dark steel, the skin warm light tan, the hair black with silver-white streaks; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`xinzhao-model-B.png`（英雄联盟 Q 第三下之后：长枪横举过头顶）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the chest armour, the coat, the belt, the trousers, both hands; 3 the head and shoulders close-up: the face, the hair, the collar, both shoulder pieces; 4 the same pose from behind: the long purple hair ribbons, the coat's back and the whole spear; 5 the official illustration: copy the TOPKNOT from it, and the mood; 6 League's Three Talon Strike finish with the spear held level over his head, the pose of version B; 7 League's Audacious Charge, the spear held level). In the 3D renders the dark lump with gold horns above his head is the topknot rendered wrongly: ignore it and draw the topknot as image 5 shows. Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a fighter with a long polearm, image 9 a man in a long coat, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 850 px tall from the top of his topknot to the soles, centred, comfortable transparent margins, nothing cut off (the whole spear inside the picture, both ends).
The character: Xin Zhao, the Seneschal of Demacia: a fit, athletic male spear warrior, noble and stern. HEAD: black hair combed back with SILVER-WHITE streaks at the temples and the front, tied up in a high TOPKNOT held by a GOLD crown clasp, two long DARK PURPLE RIBBONS trailing back from it; a stern face with sharp dark brows and fierce eyes, a small gold earring. BODY: a dark high collar; a SILVER-WHITE scale-and-plate breastplate; over it a long ROYAL PURPLE (blue-violet) war coat with GOLD trim on every edge, its front panel hanging down between his legs; a big flaring GOLD shoulder guard on his back shoulder (image left) and a large SILVER-WHITE PAULDRON with BRIGHT BLUE insets on his front shoulder (image right); brown leather forearm guards and dark fingerless gloves; a brown leather belt with a gold buckle; silver-white tasset plates at the hips. LEGS: loose pale LAVENDER-GREY trousers, dark steel greaves and boots with gold trim. SPEAR: a very LONG spear, about 1.4 times his height: a dark brown wooden shaft with GOLD rings along it; its HEAD a long PURPLE blade with a SILVER CRESCENT HOOK beside it and a purple streamer (in image 7 it points forward), its BUTT end a short dark iron spike.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height with the topknot), a fit, balanced body, legs a little shorter; the topknot with its gold clasp, the blue-inlaid silver pauldron, the gold shoulder guard, the spear's point, purple blade and crescent hook drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes and brows visible, nothing covers the face.
Pose: League's Three Talon Strike finish (image 6): standing firm with the feet apart and the knees a little bent, facing image right, the chest open toward the viewer; BOTH arms raised, both hands gripping the shaft above his head, the spear held LEVEL over his head, its iron butt spike to image right and its purple-bladed head with the crescent hook to image left; the head under the spear, turned toward the viewer, stern; the purple ribbons hanging behind the topknot. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat royal purple with blue-violet lit edges, the trim and the shoulder guard gold, the breastplate and pauldron cool silver-grey with white highlights and bright blue insets, the leather brown, the trousers pale lavender-grey, the boots dark steel, the skin warm light tan, the hair black with silver-white streaks; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物和整杆长枪（两头）都完整。
- 发髻照加载画面：黑发髻 + 金色发冠 + 两条深紫发带；黑发带银白挑染；脸露出来，两只眼睛和剑眉看得见。
- 银白胸甲、皇家紫长战袍和金边、后肩金护肩、前肩带亮蓝饰的银白大护肩、棕色护臂、棕色腰带。
- 浅紫灰宽裤、胯边银甲片、深钢色护胫和靴子。
- 长枪：深棕枪杆 + 金箍、紫色长刃枪头 + 银色月牙倒钩 + 紫飘带、深铁色枪尾尖锥。
- 鞋底是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/xinzhao-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/xinzhao/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40 行连发髻；长枪在游戏里要比原画短一些，否则每帧太宽——先给用户看两种枪长的取舍）。
