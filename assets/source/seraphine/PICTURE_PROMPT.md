# 萨勒芬妮：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 萨勒芬妮还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**脚下有没有浮空舞台**，长相、头发、衣服完全一样：**A = 英雄联盟里她移动、放技能时的样子：站在她的浮空小舞台上**（附图 1、2、6）；**B = 同样的站姿，但直接站在地上，没有舞台**（舞台以后只在特效里出现）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 38–40 行，和格温、莎米拉差不多高）。
> - **长相照英雄联盟原版**（附图 1–8）：星籁歌姬萨勒芬妮，一个温柔开朗的少女歌手。**一头又长又多的亮粉色波浪长发**，头顶翘起一撮呆毛，长发大把地披在身后、往后飘，发梢是一绺一绺的尖；**白皙的皮肤**，**蓝紫色的大眼睛**（英雄联盟的待机是闭眼，**这里要睁眼**，带一点微笑），粉色的嘴唇；背后肩胛那里伸出几片**蓝 / 青色的水晶羽片**（像小翅膀，扇形张开）。
> - **衣服**：**白色的泡泡袖、露肩**，袖口有**金色的星星饰**和金色臂环；**紫色的抹胸 / 紧身上衣**，胸前一颗小青色宝石项链；**白色手套**；腰上一条**棕色皮带**，上面有几颗**金框蓝宝石**，右胯挂着一个**大的金色菱形扣饰**；**很短的百褶裙，深蓝底泛彩虹光**（青、粉、金的炫彩），下摆一圈白色褶边；**两条腿的长筒袜不一样**：近侧是**银紫色闪闪的亮片袜，小腿上有金色花纹**，远侧是**浅紫白色的素袜**；**棕色短靴**，靴口金边。
> - **A 的舞台**：一块**浮空的小舞台 / 悬浮板**，像一只扁扁的金边小船：上面是**青绿色的彩绘玻璃台面**，正面中间是一个**圆形的蓝色花朵徽章**，花心是一颗**发光的粉色圆球**，两边各有一个**金框水滴形的蓝水晶**；她的两只靴子稳稳踩在台面上。舞台**比她的肩宽一些就够了**（不要太长），和她一起是一个整体。
> - **姿势**（附图 1、2）：3/4 正面朝右，站得很直很优雅，**一只手抬到耳边 / 脸颊旁**（像在听音乐、戴耳返的样子），另一只手放松地垂在腰旁、手指微张；长发往身后飘（她朝右，所以头发朝**画面左边**飘）。**手和脸都不能被头发挡住**。
> - **风格和比例照附图 9–11**（之前让你画的格温、莎米拉、伊芙琳）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（大眼睛、粉色头发、白泡泡袖在小尺寸下要看得出来）；**头发虽然多，也要收得紧凑一些**，不要比身体宽太多（游戏里一帧很小）。粉色头发、紫色上衣、粉色宝石容易糊成一片：**头发用亮粉色 + 浅粉高光 + 深一点的玫红阴影，上衣用偏蓝的紫色，白色泡泡袖要亮，金饰用最亮的金色，水晶羽片是亮青蓝**。
> - **画布用横版 1536×1024**：人物从呆毛到（A：舞台底；B：靴底）约 800 px，头发、羽片、舞台都在画面里，不能出画。
> - 不画任何特效（音符、声波、光圈第 3 步再单独画）；A 的舞台底 / B 的靴底是最低点，平平地落在一条地面线上（游戏在脚下画血条），头发也不能低于这条线。
> - 交付：`outputs/seraphine-picture/seraphine-model-A.png`、`outputs/seraphine-picture/seraphine-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `seraphine_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_seraphine_league_front.png` | 英雄联盟原版萨勒芬妮站在舞台上，3/4 朝右 | 颜色、形状、姿势、A 的舞台 |
| `refs/2_seraphine_league_frontal.png` | 同一帧，正面 | 两条不一样的长筒袜、裙子、舞台正面的花朵徽章 |
| `refs/3_seraphine_league_head.png` | 头和上身的特写 | 粉色长发、呆毛、脸、泡泡袖、金星、皮带、金扣饰、背后的水晶羽片 |
| `refs/4_seraphine_league_back.png` | 同一帧的背后 | 长发、水晶羽片 |
| `refs/5_seraphine_splash.png` | 官方加载画面 | 气质（温柔、闪亮的少女歌手）、睁眼的脸 |
| `refs/6_seraphine_league_glide.png` | 英雄联盟里她移动的两个瞬间：踩着舞台滑行 | 头发怎么飘、舞台怎么托着她 |
| `refs/7_seraphine_league_actions.png` | 普攻、Q、E、W、大招的瞬间 | 手和头发怎么动 |
| `refs/8_seraphine_league_sit.png` | 她闲着时坐在舞台上 | 只看舞台的形状和颜色（不用这个姿势） |
| `style/9_style_gwen.png` | 你之前的格温像素图 | **只看风格**（最近通过的一张，少女角色） |
| `style/10_style_samira.png` | 你之前的莎米拉像素图 | **只看风格** |
| `style/11_style_evelynn.png` | 你之前的伊芙琳像素图 | **只看风格**（长发、亮色） |

## 提示词 A：`seraphine-model-A.png`（站在浮空舞台上）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure standing on her floating stage in 3/4 view facing right - the look and pose of this picture; 2 the same from the front: her two different stockings, the skirt and the medallion on the stage's front; 3 the head and upper body close-up: the pink hair, the face, the puffy sleeves, the gold stars, the belt, the gold clasp and the blue crystal fins on her back; 4 the same pose from behind; 5 the official illustration: her mood and her open eyes; 6 two moments of her gliding on the stage: how the hair streams and how the stage carries her; 7 moments of her attack and spells: how the hands and the hair move; 8 her sitting on the stage when idle - only for the stage's shape and colours, not the pose). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a girl).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of her hair to the bottom of the stage, centred, comfortable transparent margins, nothing cut off (all the hair, the crystal fins and the stage inside the picture).
The character: Seraphine, the Starry-Eyed Songstress, a gentle cheerful young singer. HEAD: a big mass of long wavy BRIGHT PINK HAIR with one curled strand sticking up on top, flowing down her back and streaming behind her in pointed locks; fair skin; big BLUE-VIOLET EYES, OPEN, a soft smile (League's idle has her eyes closed - draw them open), pink lips. On her back a fan of a few BLUE / CYAN CRYSTAL FINS like small wings. CLOTHES: WHITE PUFFY OFF-SHOULDER SLEEVES with GOLD STAR ornaments and gold arm bands; a VIOLET corset top with a small cyan gem necklace; WHITE GLOVES; a BROWN BELT with gold-framed blue gems and a big GOLD DIAMOND-SHAPED CLASP hanging at her hip; a very short PLEATED SKIRT, dark blue with an IRIDESCENT rainbow sheen (cyan, pink, gold) and a white frill at the hem; two DIFFERENT THIGH-HIGH STOCKINGS: the near leg SPARKLY SILVER-LILAC sequins with gold filigree on the shin, the far leg plain pale lavender-white; BROWN ANKLE BOOTS with gold trim.
THE STAGE: she stands on her small FLOATING STAGE, a flat gold-rimmed hover board shaped like a little boat: a TEAL STAINED-GLASS deck on top, on its front a round BLUE FLOWER MEDALLION with a GLOWING PINK ORB in its centre, flanked by two gold-framed teardrop BLUE CRYSTALS. Both boots stand firmly on the deck. The stage is only a little wider than her shoulders, one piece with her.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the eyes, the pink hair and the white sleeves drawn a little oversized so they read at small size), a slim body. Keep the hair voluminous but COMPACT: it streams behind her (toward image LEFT, since she faces right) without making the figure much wider than her body. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: League's own (images 1 and 2): standing straight and graceful on the stage, facing image right, ONE HAND RAISED TO HER EAR / CHEEK as if listening to the music, the other arm relaxed at her hip with the fingers slightly open, the legs close together. The bottom of the stage is the lowest thing in the picture, flat on one ground line (the game draws the health bar under it); the hair stays above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the hair bright pink with light pink highlights and deeper rose shadows, the top a bluish violet, the sleeves and gloves bright white, the gold the brightest gold, the crystal fins bright cyan-blue, the deck teal, the orb glowing pink; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no music notes, no sound waves, no light rings, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`seraphine-model-B.png`（同样的站姿，直接站在地上，没有舞台）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture, but WITHOUT the floating stage under her feet; 2 the same from the front: her two different stockings and the skirt; 3 the head and upper body close-up: the pink hair, the face, the puffy sleeves, the gold stars, the belt, the gold clasp and the blue crystal fins on her back; 4 the same pose from behind; 5 the official illustration: her mood and her open eyes; 6 two moments of her moving: how the hair streams; 7 moments of her attack and spells: how the hands and the hair move; 8 her sitting when idle - not used for the pose). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a girl).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of her hair to the soles of her boots, centred, comfortable transparent margins, nothing cut off (all the hair and the crystal fins inside the picture).
The character: Seraphine, the Starry-Eyed Songstress, a gentle cheerful young singer. HEAD: a big mass of long wavy BRIGHT PINK HAIR with one curled strand sticking up on top, flowing down her back and streaming behind her in pointed locks; fair skin; big BLUE-VIOLET EYES, OPEN, a soft smile (League's idle has her eyes closed - draw them open), pink lips. On her back a fan of a few BLUE / CYAN CRYSTAL FINS like small wings. CLOTHES: WHITE PUFFY OFF-SHOULDER SLEEVES with GOLD STAR ornaments and gold arm bands; a VIOLET corset top with a small cyan gem necklace; WHITE GLOVES; a BROWN BELT with gold-framed blue gems and a big GOLD DIAMOND-SHAPED CLASP hanging at her hip; a very short PLEATED SKIRT, dark blue with an IRIDESCENT rainbow sheen (cyan, pink, gold) and a white frill at the hem; two DIFFERENT THIGH-HIGH STOCKINGS: the near leg SPARKLY SILVER-LILAC sequins with gold filigree on the shin, the far leg plain pale lavender-white; BROWN ANKLE BOOTS with gold trim.
NO STAGE: she stands directly on the ground, no floating board, no platform.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the eyes, the pink hair and the white sleeves drawn a little oversized so they read at small size), a slim body. Keep the hair voluminous but COMPACT: it streams behind her (toward image LEFT, since she faces right) without making the figure much wider than her body. 3/4 FRONT view facing image right, the face turned toward the viewer, nothing covers the face or the hands.
Pose: League's own (images 1 and 2): standing straight and graceful, facing image right, ONE HAND RAISED TO HER EAR / CHEEK as if listening to the music, the other arm relaxed at her hip with the fingers slightly open, the legs close together. The boot soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the hair stays above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the hair bright pink with light pink highlights and deeper rose shadows, the top a bluish violet, the sleeves and gloves bright white, the gold the brightest gold, the crystal fins bright cyan-blue; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no music notes, no sound waves, no light rings, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、头发、羽片（A 还有舞台）都完整。
- 亮粉色波浪长发 + 呆毛、**睁开的蓝紫色眼睛**、微笑、背后的蓝青水晶羽片。
- 白色露肩泡泡袖 + 金星、紫色上衣、白手套、棕皮带 + 金框蓝宝石 + 金色菱形扣饰、彩虹光的深蓝短百褶裙 + 白褶边。
- 两条不一样的长筒袜（近侧银紫亮片 + 金花纹，远侧浅紫白素袜）、棕色短靴。
- A：脚踩金边青绿台面的浮空小舞台，正面有蓝色花朵徽章 + 粉色发光球 + 两颗水滴蓝水晶，舞台只比肩宽一点；B：没有舞台，直接站地上。
- 一只手抬到耳边、另一只手垂在腰旁；脸和手没被头发挡住；头发往画面左边飘、但不要太宽。
- A 的舞台底 / B 的靴底是最低点，落在一条水平线上；没有任何特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/seraphine-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/seraphine/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 38–40 行；A 的舞台会让每帧更宽、更高——先给用户看取舍）。
- A 的移动按英雄联盟的做法是踩着舞台滑行（不迈步，头发和裙摆飘）；B 的移动要交叉步。
