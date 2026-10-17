# 雷克顿：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 雷克顿还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**姿势**，长相、盔甲、刀完全一样：**A = 英雄联盟的待机**（附图 1、2：弓着背前倾、两腿岔开，一只手握着大弯刀低低地拖在身侧、刀尖朝后，另一只手爪张开垂着，尾巴拖在身后）；**B = 冷酷捕猎起手那一下**（附图 6、7：身子直一点、张嘴，近侧的手把大弯刀竖着举在身侧，月牙形的刀刃整个立起来）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 38–40 行，和蛮王、德莱厄斯差不多高）。
> - **长相照英雄联盟原版**（附图 1–8）：荒漠屠夫雷克顿，一条**用两条腿站着的大鳄鱼**，块头大、很壮。**青绿色的鳞皮**（背上和手臂颜色深一点、带深色条纹），**喉咙、胸口和肚皮是橙棕色 / 土黄色**；**长长的鳄鱼嘴**，张着，一排**白色尖牙**，嘴里**粉红色**；眼睛是**橙黄色**、很凶。头顶到后颈扣着一块**银灰色的分节头盔**（额头上一颗**绿宝石**）。
> - **盔甲**：两肩是**很大的银灰色护肩**，上背也是银灰色甲片；手腕和腰上缠着**深蓝色的布条**；腰上一条皮带，正中一个**金色的圆扣**，下面垂着**棕色皮裙 + 一片浅土黄色的布**；膝盖和小腿是**深灰银色的护甲**；脚是**黑色带爪的鳄鱼脚**；身后一条**又粗又长的鳄鱼尾巴**，上面一排**尖尖的背棘**（青绿色，下面土黄色）。
> - **武器**：一把**很大的月牙形弯刀**（屠夫之刃）：**象牙白 / 浅银色的弧形刀刃**，内侧一排锯齿；刀背是**金色 / 青铜色的框架**，上面镶一颗**绿宝石**；握柄缠着**深蓝色的布**。刀是他最重要的东西：要画大、画清楚，**握刀的手爪必须看得见，刀的任何一部分都不能藏在身体后面**。
> - **风格和比例照附图 9–11**（之前让你画的图奇、蛮王、卡兹克）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（长嘴、尖牙、橙眼、头盔要在小尺寸下看得出来）。青绿鳞皮、深蓝布条、深灰护甲容易糊成一片：**鳞皮用偏亮的青绿，肚皮用亮的橙棕，护甲用亮的银灰，刀刃是最亮的象牙白，刀框是金色，宝石是亮绿，牙是白色，眼睛是橙黄亮点**。
> - **画布用横版 1536×1024**：人物从头顶到脚爪约 800 px，整把刀、尾巴都在画面里，不能出画。
> - **3/4 正面朝右**，脸朝向观众：眼睛、长嘴、尖牙都要看得见，不能画成背影或纯侧面。
> - 不画任何特效（红色怒气、风沙、刀光第 3 步再单独画）；脚爪是最低点，平平地落在一条地面线上（游戏在脚下画血条），尾巴也不能低于这条线。
> - 交付：`outputs/renekton-picture/renekton-model-A.png`、`outputs/renekton-picture/renekton-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `renekton_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_renekton_league_idle.png` | 英雄联盟原版雷克顿，待机第一帧，3/4 朝右 | 颜色、形状、A 的姿势 |
| `refs/2_renekton_league_side.png` | 同一帧，更侧一点 | 弓背、长嘴、尾巴和背棘、刀的长度 |
| `refs/3_renekton_league_head.png` | 头和肩的特写 | 银灰头盔、绿宝石、橙眼、尖牙、护肩 |
| `refs/4_renekton_league_back.png` | 同一帧的背后 | 背甲、尾巴 |
| `refs/5_renekton_splash.png` | 官方加载画面 | 气质（狂暴、凶残的鳄鱼屠夫） |
| `refs/6_renekton_league_raised.png` | 冷酷捕猎起手：大弯刀竖着举在身侧，3/4 朝右 | B 的姿势、月牙刀的整个形状 |
| `refs/7_renekton_league_raised_side.png` | 同上，更侧一点 | B 的刀和握法 |
| `refs/8_renekton_league_actions.png` | 英雄联盟里普攻、Q、E、跑步的几个瞬间 | 刀、手、腿、尾巴怎么动 |
| `style/9_style_twitch.png` | 你之前的图奇像素图 | **只看风格**（最近通过的一张，非人类角色） |
| `style/10_style_tryndamere.png` | 你之前的蛮王像素图 | **只看风格**（拖着大兵器的壮汉上单） |
| `style/11_style_khazix.png` | 你之前的卡兹克像素图 | **只看风格**（非人类、带爪子） |

## 提示词 A：`renekton-model-A.png`（英雄联盟的待机姿势）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle - the look and pose of this picture; 2 the same, more from the side: the hunched back, the long snout, the spiked tail and the length of the blade; 3 the head and shoulders close-up: the silver-grey helmet with its green gem, the amber eyes, the teeth, the big pauldrons; 4 the same pose from behind: the back armour and the tail; 5 the official illustration: his mood; 6 and 7 the blade raised upright beside him - version B, not for this picture; 8 a few moments of his attack, his spells and his run: how the blade, the hands, the legs and the tail move). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a non-human character; image 10 a big warrior with a large weapon; image 11 a clawed non-human character).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of the head to the foot claws, centred, comfortable transparent margins, nothing cut off (the whole blade and the whole tail inside the picture).
The character: Renekton, the Butcher of the Sands: a big, heavily muscled CROCODILE standing on two legs. HEAD: a long CROCODILE SNOUT, the jaws open, a row of sharp WHITE TEETH, a PINK mouth, fierce AMBER-ORANGE EYES; a SILVER-GREY segmented HELMET over the top of the head and the back of the neck with a GREEN GEM on the forehead. SKIN: TEAL-GREEN scales, darker with dark stripes on the back and the arms; the throat, the chest and the belly ORANGE-TAN. ARMOUR: huge SILVER-GREY PAULDRONS on both shoulders and silver-grey plates on the upper back; DARK BLUE cloth wraps on the wrists and round the waist; a belt with a round GOLD MEDALLION buckle, under it a BROWN leather kilt and a pale tan cloth flap; dark grey-silver knee guards and greaves; black clawed crocodile feet; a long thick CROCODILE TAIL with a row of SPIKED RIDGES along the top (teal-green above, tan below). WEAPON: a HUGE CRESCENT BLADE (the butcher's blade): an IVORY-WHITE / pale silver curved crescent edge with a jagged inner edge, set in a GOLD / BRONZE frame with a GREEN GEM, the grip wrapped in dark blue cloth - drawn big and clear, never hidden behind the body, the hand claws gripping it visible.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the snout, the teeth, the eyes and the helmet drawn a little oversized so they read at small size), a broad powerful body. 3/4 FRONT view facing image right, the face turned toward the viewer: the eyes, the snout and the teeth visible, nothing covers the face.
Pose: League's own idle (images 1 and 2), turned a little toward the viewer: hunched forward facing image right, the legs wide apart and bent, one hand gripping the crescent blade held low at his side with the blade trailing backward (toward image left), the whole crescent visible beside his body and the gripping hand visible; the other arm hanging forward with the claws open; the tail lying out behind him. The foot claws are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the tail stays above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the scales a brighter teal-green, the belly a bright orange-tan, the armour a bright silver-grey, the blade the brightest ivory white, its frame gold, the gem bright green, the teeth white, the eyes an amber highlight, the wraps dark blue; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no red rage aura, no sand, no slash trails, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`renekton-model-B.png`（冷酷捕猎起手：大弯刀竖着举在身侧）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle - the look; 2 the same, more from the side: the long snout, the spiked tail and the length of the blade; 3 the head and shoulders close-up: the silver-grey helmet with its green gem, the amber eyes, the teeth, the big pauldrons; 4 the same pose from behind: the back armour and the tail; 5 the official illustration: his mood; 6 and 7 the moment before his empowered strike, the crescent blade raised upright beside him - the POSE of this picture, from 3/4 and more from the side; 8 a few moments of his attack, his spells and his run: how the blade, the hands, the legs and the tail move). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a non-human character; image 10 a big warrior with a large weapon; image 11 a clawed non-human character).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of the head to the foot claws, centred, comfortable transparent margins, nothing cut off (the whole blade and the whole tail inside the picture).
The character: Renekton, the Butcher of the Sands: a big, heavily muscled CROCODILE standing on two legs. HEAD: a long CROCODILE SNOUT, the jaws open, a row of sharp WHITE TEETH, a PINK mouth, fierce AMBER-ORANGE EYES; a SILVER-GREY segmented HELMET over the top of the head and the back of the neck with a GREEN GEM on the forehead. SKIN: TEAL-GREEN scales, darker with dark stripes on the back and the arms; the throat, the chest and the belly ORANGE-TAN. ARMOUR: huge SILVER-GREY PAULDRONS on both shoulders and silver-grey plates on the upper back; DARK BLUE cloth wraps on the wrists and round the waist; a belt with a round GOLD MEDALLION buckle, under it a BROWN leather kilt and a pale tan cloth flap; dark grey-silver knee guards and greaves; black clawed crocodile feet; a long thick CROCODILE TAIL with a row of SPIKED RIDGES along the top (teal-green above, tan below). WEAPON: a HUGE CRESCENT BLADE (the butcher's blade): an IVORY-WHITE / pale silver curved crescent edge with a jagged inner edge, set in a GOLD / BRONZE frame with a GREEN GEM, the grip wrapped in dark blue cloth - drawn big and clear, never hidden behind the body, the hand claws gripping it visible.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the snout, the teeth, the eyes and the helmet drawn a little oversized so they read at small size), a broad powerful body. 3/4 FRONT view facing image right, the face turned toward the viewer: the eyes, the snout and the teeth visible, nothing covers the face.
Pose: images 6 and 7, turned a little toward the viewer: standing more upright facing image right, the jaws open in a snarl, the NEAR hand gripping the crescent blade at shoulder height and holding it UPRIGHT beside his body (on the image-left side), the whole crescent standing up with its curve clearly visible and the gripping hand visible; the other arm forward with the claws open; the legs apart and bent, the tail curving out behind him. The foot claws are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the tail stays above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the scales a brighter teal-green, the belly a bright orange-tan, the armour a bright silver-grey, the blade the brightest ivory white, its frame gold, the gem bright green, the teeth white, the eyes an amber highlight, the wraps dark blue; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no red rage aura, no sand, no slash trails, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、整把刀、整条尾巴都完整。
- 长鳄鱼嘴（张着、白色尖牙、粉红嘴里）、橙黄眼睛、银灰头盔 + 额头绿宝石。
- 青绿鳞皮 + 橙棕肚皮、银灰大护肩、深蓝布条、金色圆扣 + 棕色皮裙、深灰护膝、带背棘的粗尾巴。
- 象牙白月牙刀刃 + 金色刀框 + 绿宝石；刀没有藏在身体后面，握刀的手爪看得见。
- A：弓背、刀低低地拖在身侧朝后；B：刀竖着举在身侧、整个月牙立起来。
- 脚爪是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/renekton-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/renekton/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 38–40 行，一开始就按蛮王 / 德莱厄斯的个子来；大弯刀 + 尾巴会让每帧很宽——先给用户看取舍）。
