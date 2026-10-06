# 莎弥拉：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 莎弥拉还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站得笔直、两手叉腰，大刀斜背在背后，两把手枪插在大腿两侧的枪套里）；**B = 英雄联盟的战斗待机**（两脚分开站稳，前手握一把手枪垂在身侧、枪口朝前下方，后手握着大刀的刀柄、刀身扛在后肩上横向身后）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行）。
> - **长相照英雄联盟原版**（附图 1–7）：沙漠玫瑰莎弥拉，一位**自信、健美的女枪手**，古铜色皮肤。**墨绿偏黑的头发**，额前一缕翘起，**一根很长的粗辫子**编着金线、从肩上垂到腰，发间几个**金色发饰**、银色耳坠；**一只眼戴墨绿色眼罩、红色系带**（画面左边那只眼，照附图 1–3、5），另一只眼明亮，红唇，神情挑衅自信。
> - **服装**：**深墨绿 / 黑色的无袖高领紧身上衣**，胸前一条**红色的斜布带**，露出腹部；两条手臂健壮、带细细的纹身线条，戴**黑色露指手套**；腰间红布和皮带；**胯两侧两块金色雕花的大护片 / 枪套**（金色、黑边、花纹）；大腿上各插一把手枪；**深灰绿色的长裤和过膝长靴**，靴子上一圈圈钢色扣带，带一点跟。
> - **武器**：**一把很大的单刃大刀**（约和她身高一样长）：刀身**深钢色、刃口一条亮银白**，刀柄深色缠绳，刀柄末端系着一条**长长的红色飘带**；**两把手枪**：深钢色枪管、金色饰件，一把是长管转轮手枪、一把是短一些的手枪。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的希维尔、伊芙琳、韦鲁斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（约占身高三分之一），身材匀称，腿稍短；眼罩、亮着的那只眼、金发饰、金色胯甲、刀刃的银边、红飘带画大一点，小尺寸下才看得出来。深墨绿衣服、黑靴、深钢刀身容易糊成一片：**衣服用几档墨绿加青绿亮边，靴子用冷灰加亮扣，刀身深钢加亮银刃口，金色和红色是亮点**。
> - **画布用横版 1536×1024**（大刀太长，竖版放不下）：人物从头顶到鞋底约 850 px，整把大刀（刀尖、刀柄、红飘带）都在画面里，不能出画。
> - **3/4 正面朝右**，脸朝向观众：眼罩、亮着的那只眼和眉毛都要看得见，不能画成背影。
> - 不画任何特效（枪口火光、刀光、旋转的刀风第 3 步再单独画）；鞋底是最低点，平平地落在一条地面线上（游戏在脚下画血条），刀也不能低于这条线。
> - 交付：`outputs/samira-picture/samira-model-A.png`、`outputs/samira-picture/samira-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `samira_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_samira_league_front.png` | 英雄联盟原版莎弥拉，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_samira_league_frontal.png` | 同一帧，正面 | 上衣、红布带、金胯甲、枪套、靴子 |
| `refs/3_samira_league_head.png` | 头和肩的特写 | 脸、眼罩、金发饰、发型 |
| `refs/4_samira_league_back.png` | 同一帧的背后 | 长辫子、背上的大刀和红飘带 |
| `refs/5_samira_splash.png` | 官方加载画面 | 气质（自信挑衅）、双枪和大刀的样子 |
| `refs/6_samira_league_combat.png` | 英雄联盟战斗待机：一手枪、大刀扛肩 | B 的姿势 |
| `refs/7_samira_league_weapons.png` | 英雄联盟里开枪、挥刀的几个瞬间 | 两把枪和大刀拿在手里的样子 |
| `style/8_style_sivir.png` | 你之前的希维尔像素图 | **只看风格**（女战士、大兵器） |
| `style/9_style_evelynn.png` | 你之前的伊芙琳像素图 | **只看风格**（女性身材比例） |
| `style/10_style_varus.png` | 你之前的韦鲁斯像素图 | **只看风格**（最近通过的一张） |

## 提示词 A：`samira-model-A.png`（英雄联盟待机：两手叉腰、大刀背在身后）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen from the front: the top, the red sash, the gold hip plates, the holsters, the boots; 3 the head and shoulders close-up: the face, the eyepatch, the gold hair ornaments; 4 the same pose from behind: the long braid and the greatsword on her back with its red ribbon; 5 the official illustration: her mood, the two pistols and the sword; 6 League's combat idle with a pistol in one hand and the greatsword on her shoulder, the pose of version B; 7 a few moments of her shooting and slashing: how she holds the guns and the sword). Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a woman warrior with a big weapon, image 9 a woman's proportions, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 850 px tall from the top of her head to the soles, centred, comfortable transparent margins, nothing cut off (the whole greatsword inside the picture, point, hilt and ribbon).
The character: Samira, the Desert Rose: a confident, athletic woman gunslinger with bronze-brown skin. HEAD: dark teal-black hair with a lock curling up over the forehead and ONE VERY LONG THICK BRAID woven with gold threads, hanging over her shoulder down to the waist, small GOLD hair ornaments and silver earrings; a DARK GREEN EYEPATCH with a RED strap over the eye on image left (as in images 1-3 and 5), the other eye bright, red lips, a cocky confident look. BODY: a sleeveless high-collared fitted top in DARK GREEN-BLACK with a RED cloth sash across the chest, the midriff bare; strong toned arms with thin tattoo lines, BLACK fingerless gloves; a red waist cloth and a belt; two big ornate GOLD hip plates / holsters with black edges at both hips, a PISTOL in a holster on each thigh. LEGS: dark grey-green trousers and tall over-the-knee boots with steel straps and buckles, small heels. WEAPONS: a HUGE single-edged GREATSWORD about as long as she is tall: a dark steel blade with a bright SILVER-WHITE cutting edge, a dark wrapped hilt with a long RED RIBBON tied to its pommel; two PISTOLS of dark steel with gold fittings, one a long-barrelled revolver, one a shorter pistol.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of her height), a fit, balanced feminine body, legs a little shorter; the eyepatch, the bright eye, the gold ornaments and hip plates, the sword's silver edge and the red ribbon drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the eyepatch, the bright eye and both brows visible, nothing covers the face.
Pose: League's own idle (image 1), turned a little more toward the viewer: standing tall facing image right, feet a little apart, BOTH HANDS ON HER HIPS, elbows out; the greatsword slung diagonally across her back, its hilt and red ribbon up behind her shoulder, its blade down behind her back leg; both pistols in the thigh holsters; the braid hanging over her shoulder. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the sword stays above that line.
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the top dark green-black with teal lit edges, the sash and waist cloth red, the hip plates and ornaments gold, the boots and trousers cool dark grey-green with bright steel buckles, the blade dark steel with a bright silver edge, the skin warm bronze-brown, the hair dark teal-black; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no muzzle flash, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`samira-model-B.png`（英雄联盟战斗待机：一手持枪、大刀扛肩）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen from the front: the top, the red sash, the gold hip plates, the holsters, the boots; 3 the head and shoulders close-up: the face, the eyepatch, the gold hair ornaments; 4 the same pose from behind: the long braid and the greatsword on her back with its red ribbon; 5 the official illustration: her mood, the two pistols and the sword; 6 League's combat idle with a pistol in one hand and the greatsword on her shoulder, the pose of version B; 7 a few moments of her shooting and slashing: how she holds the guns and the sword). Copy from the images the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a woman warrior with a big weapon, image 9 a woman's proportions, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 850 px tall from the top of her head to the soles, centred, comfortable transparent margins, nothing cut off (the whole greatsword inside the picture, point, hilt and ribbon).
The character: Samira, the Desert Rose: a confident, athletic woman gunslinger with bronze-brown skin. HEAD: dark teal-black hair with a lock curling up over the forehead and ONE VERY LONG THICK BRAID woven with gold threads, hanging over her shoulder down to the waist, small GOLD hair ornaments and silver earrings; a DARK GREEN EYEPATCH with a RED strap over the eye on image left (as in images 1-3 and 5), the other eye bright, red lips, a cocky confident look. BODY: a sleeveless high-collared fitted top in DARK GREEN-BLACK with a RED cloth sash across the chest, the midriff bare; strong toned arms with thin tattoo lines, BLACK fingerless gloves; a red waist cloth and a belt; two big ornate GOLD hip plates / holsters with black edges at both hips. LEGS: dark grey-green trousers and tall over-the-knee boots with steel straps and buckles, small heels. WEAPONS: a HUGE single-edged GREATSWORD about as long as she is tall: a dark steel blade with a bright SILVER-WHITE cutting edge, a dark wrapped hilt with a long RED RIBBON tied to its pommel; two PISTOLS of dark steel with gold fittings, one a long-barrelled revolver, one a shorter pistol.
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of her height), a fit, balanced feminine body, legs a little shorter; the eyepatch, the bright eye, the gold ornaments and hip plates, the sword's silver edge and the red ribbon drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the eyepatch, the bright eye and both brows visible, nothing covers the face.
Pose: League's combat idle (image 6): standing firm with the feet apart facing image right, the chest open toward the viewer; the FRONT hand (image right) holds the long revolver low at her side, its muzzle pointing forward and down toward image right; the BACK hand holds the greatsword's hilt at her back shoulder, the blade RESTING ON THAT SHOULDER and lying back horizontally behind her toward image left, the silver edge up, the red ribbon hanging from the pommel; the shorter pistol in its thigh holster; the braid hanging over her shoulder. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the top dark green-black with teal lit edges, the sash and waist cloth red, the hip plates and ornaments gold, the boots and trousers cool dark grey-green with bright steel buckles, the blade dark steel with a bright silver edge, the guns dark steel with gold, the skin warm bronze-brown, the hair dark teal-black; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no muzzle flash, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物和整把大刀（刀尖、刀柄、红飘带）都完整。
- 墨绿黑的头发 + 一根编金线、垂到腰的长辫子 + 金发饰；画面左边那只眼戴墨绿眼罩（红系带），另一只眼和眉毛看得见。
- 墨绿黑无袖高领上衣 + 红色斜布带、露腹；黑色露指手套；胯两侧金色雕花护片 / 枪套。
- 深灰绿长裤、过膝长靴和钢扣。
- 大刀：深钢刀身 + 亮银刃口、深色刀柄 + 长红飘带；两把深钢配金的手枪。
- 鞋底是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/samira-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/samira/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40 行；大刀在游戏里要比原画短一些，否则每帧太宽——先给用户看取舍）。
