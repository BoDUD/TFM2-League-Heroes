# 图奇：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 图奇还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**姿势**，长相、衣服、弩完全一样：**A = 英雄联盟的待机**（附图 1、2：微微驼背前倾，近侧的手把弩端在腰前、弩口朝前，另一只手爪垂在身侧）；**B = 英雄联盟普攻起手那一下的站姿**（附图 6、7：身子更直一点，两只手一起把弩横端在腰前、弩口朝前，尾巴在身后卷起）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 36–38 行，和德莱厄斯、卡兹克缩小后差不多高）。
> - **长相照英雄联盟原版**（附图 1–8）：瘟疫之源图奇，一只**用两条腿站着的大老鼠**。**灰绿色的毛**；一对**很大的老鼠耳朵**，耳朵里面是粉色；**红色的鼻头**；嘴里一排**又大又尖的黄白牙**，常咧着嘴；眼睛上戴着一副**黄铜护目镜**（一圈铜框，镜片发亮，像单片眼镜一样醒目），一条铜色带子绕过头；脖子上围一条**锈橙色的围巾**。
> - **衣服**：一件**又长又破的深青色斗篷 / 长外套**（下摆是碎布条、带一圈浅棕褐色的边），身后背着一个**绿色的大背包 / 兜帽**（铜色包边、几颗铜铆钉、上面插着青色的小药瓶）；肩上是**棕色皮护肩**（铜铆钉）；腰上一条**棕色皮带**，铜扣；**手臂是深绿色的**，**手是长指甲的绿色爪子**；**腿是深灰紫色的反关节鼠腿**，脚是**带爪的鼠脚**；身后一条**很长的、灰色和深色一节一节相间的老鼠尾巴**。
> - **弩**：一把**黄铜 / 金色的连发弩**，弩臂是**浅青蓝色**，弩身上顶着一颗**大大的翠绿色宝石 / 毒液瓶**，弩箭是**金色的箭头**。弩是他最重要的东西：要画大、画清楚，**任何一部分都不能藏在身体后面**，握弩的手爪要看得见。
> - **风格和比例照附图 9–11**（之前让你画的卡兹克、派克、韦鲁斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（大耳朵、护目镜、龇牙要在小尺寸下看得出来）。深青、深绿、深灰紫容易糊成一片：**斗篷用偏亮的青色加浅棕褐色边，手臂用亮一点的绿，腿用灰紫，护目镜和弩用最亮的黄铜色，宝石是亮翠绿，牙是亮黄白，鼻头是红色亮点**。
> - **画布用横版 1536×1024**：人物从耳朵尖到脚爪约 800 px，弩、尾巴、斗篷都在画面里，不能出画。
> - **3/4 正面朝右**，脸朝向观众：护目镜、鼻子、牙都要看得见，不能画成背影或纯侧面。
> - 不画任何特效（毒烟、绿色毒液、隐身第 3 步再单独画）；脚爪是最低点，平平地落在一条地面线上（游戏在脚下画血条），尾巴和斗篷下摆也不能低于这条线。
> - 交付：`outputs/twitch-picture/twitch-model-A.png`、`outputs/twitch-picture/twitch-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `twitch_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_twitch_league_idle.png` | 英雄联盟原版图奇，待机第一帧，3/4 朝右 | 颜色、形状、A 的姿势 |
| `refs/2_twitch_league_side.png` | 同一帧，更侧一点 | 驼背、反关节腿、尾巴、弩的长度 |
| `refs/3_twitch_league_head.png` | 头和肩的特写 | 大耳朵、护目镜、红鼻头、龇牙、围巾、背包 |
| `refs/4_twitch_league_back.png` | 同一帧的背后 | 背包、斗篷、尾巴 |
| `refs/5_twitch_splash.png` | 官方加载画面 | 气质（阴险、疯癫的瘟疫老鼠） |
| `refs/6_twitch_league_upright.png` | 普攻起手的站姿，3/4 朝右 | B 的姿势（两手横端弩） |
| `refs/7_twitch_league_upright_side.png` | 同上，更侧一点 | B 的弩、尾巴 |
| `refs/8_twitch_league_actions.png` | 英雄联盟里普攻、大招、E、跑步的几个瞬间 | 弩和手、腿、尾巴怎么动 |
| `style/9_style_khazix.png` | 你之前的卡兹克像素图 | **只看风格**（最近通过的一张，非人类角色） |
| `style/10_style_pyke.png` | 你之前的派克像素图 | **只看风格**（驼背、深色系） |
| `style/11_style_varus.png` | 你之前的韦鲁斯像素图 | **只看风格**（拿远程武器的角色） |

## 提示词 A：`twitch-model-A.png`（英雄联盟的待机姿势）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle - the look and pose of this picture; 2 the same, more from the side: the hunched back, the backward-bending rat legs, the tail and the length of the crossbow; 3 the head and shoulders close-up: the big ears, the brass goggles, the red nose, the grinning teeth, the scarf, the backpack; 4 the same pose from behind: the backpack, the coat and the tail; 5 the official illustration: his mood; 6 and 7 a more upright stance with the crossbow held in both hands - version B, not for this picture; 8 a few moments of his attack, his ultimate, a spell and his run: how the crossbow, the hands, the legs and the tail move). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a non-human character; image 10 a hunched dark-palette character; image 11 a character with a ranged weapon).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the ear tips to the foot claws, centred, comfortable transparent margins, nothing cut off (the whole crossbow, the tail and the coat inside the picture).
The character: Twitch, the Plague Rat: a big rat standing on two legs. HEAD: GREY-GREEN fur, two very BIG RAT EARS pink inside, a RED NOSE, a wide grin of big sharp YELLOW-WHITE TEETH, BRASS GOGGLES over the eyes (a round brass rim with a bright lens, very readable) on a brass strap round the head, a RUSTY ORANGE SCARF round the neck. CLOTHES: a long ragged DARK TEAL COAT / cloak with a tan-brown trim and a hem of torn strips; on his back a big GREEN BACKPACK / hood with brass rims, brass rivets and small teal vials; brown leather shoulder pads with brass rivets; a brown leather belt with a brass buckle; DARK GREEN ARMS ending in green clawed hands with long nails; digitigrade GREY-PURPLE RAT LEGS bending backward at the knee, clawed rat feet; a very long RINGED RAT TAIL banded grey and dark. WEAPON: a BRASS / GOLD repeating CROSSBOW with LIGHT TEAL-BLUE limbs, a big EMERALD-GREEN GEM / venom vial on top of the stock, a bolt with a gold arrowhead loaded - drawn big and clear, never hidden behind the body, the hand claws holding it visible.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the ears, the goggles and the grin drawn a little oversized so they read at small size), a wiry hunched body. 3/4 FRONT view facing image right, the face turned toward the viewer: the goggles, the nose and the teeth visible, nothing covers the face.
Pose: League's own idle (images 1 and 2), turned a little toward the viewer: slightly hunched forward facing image right, the near hand holding the crossbow at hip height with its tip pointing forward (image right), the other arm hanging at his side with the claws open, the legs apart and bent the rat way, the tail curving out behind him. The foot claws are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the tail and the coat hem stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat a brighter teal with a tan trim, the arms a brighter green, the legs grey-purple, the fur grey-green, the goggles and the crossbow the brightest brass, the gem bright emerald, the teeth bright yellow-white, the nose a red highlight; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no poison smoke, no green venom, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`twitch-model-B.png`（普攻起手的站姿：两手横端弩）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle - the look; 2 the same, more from the side: the backward-bending rat legs, the tail and the length of the crossbow; 3 the head and shoulders close-up: the big ears, the brass goggles, the red nose, the grinning teeth, the scarf, the backpack; 4 the same pose from behind: the backpack, the coat and the tail; 5 the official illustration: his mood; 6 and 7 the more upright stance League's attack starts from, the crossbow held level in both hands - the POSE of this picture, from 3/4 and more from the side; 8 a few moments of his attack, his ultimate, a spell and his run: how the crossbow, the hands, the legs and the tail move). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a non-human character; image 10 a hunched dark-palette character; image 11 a character with a ranged weapon).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the ear tips to the foot claws, centred, comfortable transparent margins, nothing cut off (the whole crossbow, the tail and the coat inside the picture).
The character: Twitch, the Plague Rat: a big rat standing on two legs. HEAD: GREY-GREEN fur, two very BIG RAT EARS pink inside, a RED NOSE, a wide grin of big sharp YELLOW-WHITE TEETH, BRASS GOGGLES over the eyes (a round brass rim with a bright lens, very readable) on a brass strap round the head, a RUSTY ORANGE SCARF round the neck. CLOTHES: a long ragged DARK TEAL COAT / cloak with a tan-brown trim and a hem of torn strips; on his back a big GREEN BACKPACK / hood with brass rims, brass rivets and small teal vials; brown leather shoulder pads with brass rivets; a brown leather belt with a brass buckle; DARK GREEN ARMS ending in green clawed hands with long nails; digitigrade GREY-PURPLE RAT LEGS bending backward at the knee, clawed rat feet; a very long RINGED RAT TAIL banded grey and dark. WEAPON: a BRASS / GOLD repeating CROSSBOW with LIGHT TEAL-BLUE limbs, a big EMERALD-GREEN GEM / venom vial on top of the stock, a bolt with a gold arrowhead loaded - drawn big and clear, never hidden behind the body, both hand claws holding it visible.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the ears, the goggles and the grin drawn a little oversized so they read at small size), a wiry body. 3/4 FRONT view facing image right, the face turned toward the viewer: the goggles, the nose and the teeth visible, nothing covers the face.
Pose: images 6 and 7, turned a little toward the viewer: standing more upright facing image right, BOTH hands holding the crossbow level across the front of his body at hip height, its tip pointing forward (image right), the legs apart and bent the rat way, the coat hanging behind, the tail curling out behind him. The foot claws are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the tail and the coat hem stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the coat a brighter teal with a tan trim, the arms a brighter green, the legs grey-purple, the fur grey-green, the goggles and the crossbow the brightest brass, the gem bright emerald, the teeth bright yellow-white, the nose a red highlight; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no poison smoke, no green venom, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、整把弩、尾巴、斗篷都完整。
- 大老鼠耳朵（里面粉色）、黄铜护目镜、红鼻头、龇着的黄白尖牙、锈橙围巾、绿色背包。
- 深青色破斗篷 + 浅棕褐色边、深绿手臂和绿爪子、灰紫色反关节鼠腿、一节一节的长尾巴。
- 黄铜连发弩、浅青蓝弩臂、翠绿宝石、金色箭头；弩没有藏在身体后面，握弩的手爪看得见。
- A：近侧一只手在腰前端弩、另一只手垂着；B：两只手一起横端弩。
- 脚爪是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/twitch-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/twitch/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 36–38 行，一开始就按德莱厄斯 / 缩小后的卡兹克的个子来；弩 + 尾巴会让每帧很宽——先给用户看取舍）。
