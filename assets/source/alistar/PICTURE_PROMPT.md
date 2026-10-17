# 阿利斯塔：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 阿利斯塔还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（弓着背向前探，两只大手垂在身体前面）；**B = 英雄联盟 Q（大地粉碎）的起手**（站直、两只拳头一起高高举过头顶，准备砸地）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行，连鬃毛/角）。
> - **长相照英雄联盟原版**（附图 1–6）：一头**巨大的牛头人**，全身**蓝紫色皮肤**（胸口、肚子和肌肉亮面是淡紫色，阴影是深靛蓝），肩膀和手臂极粗、比腿大得多，背上高高拱起。**头顶到后背是一道亮青色的尖刺鬃毛**。牛头低低地向前伸：宽鼻子、深紫色口鼻、**鼻子上穿一个银色鼻环**、浓眉下一双**发红光的小眼睛**、下巴一撮短胡子；**两只又大又弯的象牙白牛角**向两边伸出再往前卷，画面左边那只角的尖头附近套着一圈黑铁箍。
> - **手和装备**：一双大手、粗手指、黑指甲；**两只手腕上各一个断开的粗铁镣铐**（黑灰色铁、浅钢色花纹），挂着几节断铁链；**镣铐很宽、几乎和小臂一样宽**；腰上一条**棕色皮带**（侧面挂一个铁环），前面垂一块**棕色皮围裙**；腿短而粗、膝盖弯着，脚踝一圈蓬松的紫毛，**黑色偶蹄**。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的瑟提、蔚、韦鲁斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头（连角）比英雄联盟模型大一些（约占身高三分之一），但身体仍然又宽又壮（比瑟提还要壮），手臂和手画大、腿短；牛角、青色鬃毛、鼻环、镣铐画大一点，小尺寸下才看得出来。紫色皮肤要分出几档紫色和淡紫高光，不要糊成一块深色。
> - **3/4 正面朝右**，脸朝向观众：两只红眼睛、鼻子和鼻环都要看得见，不能画成背影。
> - 不画任何特效（冲击波、尘土、光环第 3 步再单独画）；牛蹄是最低点，平平地落在一条地面线上（游戏在脚下画血条），铁链挂在上面。
> - 交付：`outputs/alistar-picture/alistar-model-A.png`、`outputs/alistar-picture/alistar-model-B.png`（都是 1024×1536 竖版、真透明背景，人物从鬃毛顶（B 版从举起的拳头顶）到牛蹄约 1150 px）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_alistar_league_front.png` | 英雄联盟原版阿利斯塔，待机第一帧，3/4 朝右 | 外形、颜色、A 的姿势 |
| `refs/2_alistar_league_frontal.png` | 同一帧，更正面一点 | 脸、牛角、胸口、皮围裙、两只镣铐 |
| `refs/3_alistar_league_head.png` | 头和肩的特写 | 牛角、青色鬃毛、口鼻、鼻环、眼睛 |
| `refs/4_alistar_league_side.png` | 同一帧的侧面 | 背上的鬃毛、驼峰、牛角 |
| `refs/5_alistar_splash.png` | 官方加载画面 | **看气氛** |
| `refs/6_alistar_league_cast.png` | 英雄联盟 Q 起手那一帧 | B 的姿势（双拳举过头顶） |
| `style/7_style_sett.png` | 你之前的瑟提像素图 | **只看风格**（壮汉） |
| `style/8_style_vi.png` | 你之前的蔚像素图 | **只看风格**（大手） |
| `style/9_style_varus.png` | 你之前的韦鲁斯像素图 | **只看风格**（最新一张） |

## 提示词 A：`alistar-model-A.png`（英雄联盟待机：弓背前探，双手垂在身前）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the face, the horns, the chest, the belt and loincloth, both shackles; 3 the head and shoulders close-up: the horns, the cyan mane, the snout, the nose ring, the eyes; 4 the same pose in profile: the mane down the back, the hump, the horns; 5 the official illustration, for the mood; 6 League's Pulverize wind-up with both fists raised, the pose of version B). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 7 a big muscular brawler, image 8 huge hands, image 9 the latest picture in this style).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the top of the mane (or of the raised fists) to the hooves, centred, comfortable transparent margins, nothing cut off (both horn tips inside the picture).
The character: Alistar, the Minotaur: a huge, hulking bull-headed MINOTAUR, a gentle giant support built like a wall of muscle. SKIN: deep VIOLET-PURPLE all over (a blue-violet, lighter lavender on the chest, the belly and the lit muscle tops, dark indigo in the shadows), massive rounded shoulders and arms much bigger than his legs. MANE: a crest of spiky bright CYAN / sky-blue hair running from between the horns over the top of the head and down the back of the neck and the hump of his back, like flames or icicles. HEAD: a bull's head carried low and forward in front of the hump, a broad snout with a darker purple muzzle and nostrils, a silver NOSE RING through the nose, small fierce red-glowing eyes under heavy brows, a short purple beard on the chin; two big curved IVORY-WHITE HORNS sweeping out to the sides and curling forward, the horn on the image-left with a dark iron band near its tip. ARMS: huge hands with thick fingers and dark nails; on each wrist a very WIDE, thick broken iron SHACKLE cuff (a big dark grey-black iron band with a lighter steel engraved zig-zag pattern, as wide as his forearm) with a few broken chain links hanging from it. WAIST: a brown leather belt with an iron ring at the side, a brown leather loincloth hanging in front. LEGS: short, thick bull legs, bent at the knee, shaggy purple fur round the ankles, dark cloven HOOVES.
Proportions: game-sprite proportions like images 7-9 - the head with its horns bigger than in the 3D model (about a third of his height), the body still massive and wide (he is the biggest, bulkiest of them: much broader than image 7), the arms and hands oversized, the legs short; the horns, the cyan mane, the nose ring and the shackles drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both red eyes, the snout and the nose ring clearly visible; never his back.
Pose: League's own idle (image 1): hunched forward in 3/4 view facing image right, the massive shoulders and the back's hump high, the head low and forward with the horns spread, the face turned toward the viewer; both huge arms hanging forward in front of the body, the hands relaxed and slightly open just above knee height, the shackles' chains hanging; the legs a little apart and bent, both hooves flat on one ground line. The hooves are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the chains hang above that line.
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The purple skin in clear violet shades with lavender highlights on the muscles (never one flat dark mass - black is only the outline), the mane bright cyan with white-blue tips, the horns ivory with warm grey shading, the iron dark grey with steel-grey engraved lines, the leather brown; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no shockwave, no dust, no aura, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`alistar-model-B.png`（英雄联盟 Q 的起手：双拳高举过头顶）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the face, the horns, the chest, the belt and loincloth, both shackles; 3 the head and shoulders close-up: the horns, the cyan mane, the snout, the nose ring, the eyes; 4 the same pose in profile: the mane down the back, the hump, the horns; 5 the official illustration, for the mood; 6 League's Pulverize wind-up with both fists raised, the pose of version B). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 7 a big muscular brawler, image 8 huge hands, image 9 the latest picture in this style).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the top of the mane (or of the raised fists) to the hooves, centred, comfortable transparent margins, nothing cut off (both horn tips inside the picture).
The character: Alistar, the Minotaur: a huge, hulking bull-headed MINOTAUR, a gentle giant support built like a wall of muscle. SKIN: deep VIOLET-PURPLE all over (a blue-violet, lighter lavender on the chest, the belly and the lit muscle tops, dark indigo in the shadows), massive rounded shoulders and arms much bigger than his legs. MANE: a crest of spiky bright CYAN / sky-blue hair running from between the horns over the top of the head and down the back of the neck and the hump of his back, like flames or icicles. HEAD: a bull's head carried low and forward in front of the hump, a broad snout with a darker purple muzzle and nostrils, a silver NOSE RING through the nose, small fierce red-glowing eyes under heavy brows, a short purple beard on the chin; two big curved IVORY-WHITE HORNS sweeping out to the sides and curling forward, the horn on the image-left with a dark iron band near its tip. ARMS: huge hands with thick fingers and dark nails; on each wrist a very WIDE, thick broken iron SHACKLE cuff (a big dark grey-black iron band with a lighter steel engraved zig-zag pattern, as wide as his forearm) with a few broken chain links hanging from it. WAIST: a brown leather belt with an iron ring at the side, a brown leather loincloth hanging in front. LEGS: short, thick bull legs, bent at the knee, shaggy purple fur round the ankles, dark cloven HOOVES.
Proportions: game-sprite proportions like images 7-9 - the head with its horns bigger than in the 3D model (about a third of his height), the body still massive and wide (he is the biggest, bulkiest of them: much broader than image 7), the arms and hands oversized, the legs short; the horns, the cyan mane, the nose ring and the shackles drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both red eyes, the snout and the nose ring clearly visible; never his back.
Pose: League's Pulverize wind-up (image 6): standing up tall in 3/4 view facing image right, BOTH huge fists raised high above his head, clenched together, ready to smash the ground; the shackles and broken chains on the raised wrists; the chest and belly open to the viewer; the head under the raised arms, horns spread, the face turned toward the viewer, snorting; the legs apart and braced, both hooves flat on one ground line. The hooves are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the chains hang above that line.
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The purple skin in clear violet shades with lavender highlights on the muscles (never one flat dark mass - black is only the outline), the mane bright cyan with white-blue tips, the horns ivory with warm grey shading, the iron dark grey with steel-grey engraved lines, the leather brown; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no shockwave, no dust, no aura, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，两只牛角的尖没被切掉。
- 蓝紫色皮肤分出几档紫色；头顶到后背的亮青色尖鬃毛；象牙白大弯角；银鼻环；两只红眼睛看得见。
- 两只手腕上很宽的断铁镣铐和断链；棕色皮带 + 棕色皮围裙；短粗的腿、黑色牛蹄。
- 身体又宽又壮、手臂和手很大，头连角约占身高三分之一；3/4 正面朝右，不是背影。
- 牛蹄是最低点，落在一条水平线上；没有冲击波、尘土、光环等特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/alistar-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
