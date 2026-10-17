# 莉莉娅：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 莉莉娅还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**拿枝条的姿势**，长相、身体、衣服、枝条完全一样：**A = 英雄联盟的待机**（附图 1、2：两只手把长枝条竖着抱在胸前，枝头挂着的梦之灯笼高高吊在头顶右上方）；**B = 枝条往前平伸**（附图 6、7：一只手把枝条朝前方伸出去、放得低，灯笼吊在她胸口高度的前方，整个人比 A 矮）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40–42 行，和萨勒芬妮、格温差不多高）。
> - **长相照英雄联盟原版**（附图 1–8）：含羞蓓蕾莉莉娅，**半人半鹿**：腰以上是一个害羞的小姑娘，腰以下是一头**小鹿的身体，四条细长的鹿腿**（像人马那样）。**一头长长的洋红 / 紫红色头发**披在背后，头顶扎着一个**蓝紫色的花苞**；耳朵两边各有一个**绿色的叶子卷**（像螺旋形的嫩芽）；**大大的紫色眼睛**，表情有点害羞、怯生生的；皮肤是浅奶油色。
> - **衣服 / 身体**：上身是**浅奶油色的肌肤**，胸前和肩上包着**绿色的叶片**（像叶子做的小上衣），手腕上也缠着绿叶；腰下接着**橙棕色的鹿身**，鹿的肚子和胸前是**浅米色**，鹿背上有几道**深一点的条纹**；**一条短短的、蓬起来的米白色鹿尾巴**翘在身后；四条腿**下半截颜色深一点（深棕红）**，**蹄子是紫色**。
> - **武器**：一根**又细又长的紫色枝条**（梦满枝）：深紫色、扭成一点点麻花，顶端弯成一个**金色的钩**，钩上开着一朵**青蓝色的小花**；钩下吊着一个**圆圆的藤编灯笼**（棕色和绿色的藤条，里面透出一点暖橙色的光），灯笼底下垂一个**小流苏**。枝条和灯笼是她最重要的东西：**握枝条的手必须看得见**，枝条、灯笼的任何一部分都不能藏在身体后面。
> - **风格和比例照附图 9–11**（之前让你画的萨勒芬妮、格温、雷克顿）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（大眼睛、花苞、紫红长发在小尺寸下要看得出来）；**鹿身和腿要收得紧凑**：腿可以比原版短一点、粗一点，不要让人物太宽太高（游戏里一帧很小）。紫红头发、紫色枝条、紫色蹄子容易糊成一片：**头发用亮洋红 + 浅粉高光 + 深紫红阴影，枝条用偏蓝的深紫，蹄子用亮一点的蓝紫，鹿身是亮橙棕，肚皮是米白，叶子是亮绿，花苞是蓝紫，灯笼的光是暖橙**。
> - **画布用横版 1536×1024**：人物从（A：灯笼 / 枝头；B：花苞）最高点到蹄底约 800 px，枝条、灯笼、尾巴都在画面里，不能出画。
> - **3/4 正面朝右**：她的脸、上身朝向观众，鹿身朝右；眼睛、花苞、握枝条的手都要看得见。
> - 不画任何特效（梦尘、花瓣、光圈第 3 步再单独画）；四只蹄子是最低点，平平地落在一条地面线上（游戏在脚下画血条），尾巴、灯笼都不能低于这条线。
> - 交付：`outputs/lillia-picture/lillia-model-A.png`、`outputs/lillia-picture/lillia-model-B.png`（都是 1536×1024 横版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `lillia_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_lillia_league_idle.png` | 英雄联盟原版莉莉娅，待机，3/4 朝右 | 颜色、形状、A 的姿势 |
| `refs/2_lillia_league_side.png` | 同一帧，更侧一点 | 鹿身的长度、四条腿、尾巴、枝条的长度 |
| `refs/3_lillia_league_head.png` | 头和上身的特写 | 紫红长发、花苞、叶子耳饰、大眼睛、叶片上衣、握枝的手、灯笼 |
| `refs/4_lillia_league_back.png` | 同一帧的背后 | 长发、鹿背的条纹、尾巴 |
| `refs/5_lillia_splash.png` | 官方加载画面 | 气质（害羞、可爱的林中小鹿） |
| `refs/6_lillia_league_low.png` | 待机里枝条朝前平伸的一刻，3/4 朝右 | B 的姿势：枝条低、灯笼吊在前方 |
| `refs/7_lillia_league_low_side.png` | 同上，更侧一点 | B 的枝条和握法 |
| `refs/8_lillia_league_actions.png` | 普攻、W、E、跑动两帧 | 枝条怎么挥、鹿腿怎么跑 |
| `style/9_style_seraphine.png` | 你之前的萨勒芬妮像素图 | **只看风格**（最近通过的一张，少女角色） |
| `style/10_style_gwen.png` | 你之前的格温像素图 | **只看风格** |
| `style/11_style_renekton.png` | 你之前的雷克顿像素图 | **只看风格**（兽类身体的画法） |

## 提示词 A：`lillia-model-A.png`（英雄联盟待机：枝条竖着抱在胸前，灯笼吊在头顶）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture; 2 the same from more to the side: the length of the fawn body, the four legs, the tail and the length of the bough; 3 the head and upper body close-up: the hair, the flower bud, the leaf ear ornaments, the big eyes, the leaf top, the hands holding the bough and the lantern; 4 the same pose from behind; 5 the official illustration: her mood; 6 and 7 a moment with the bough held forward low - not this picture's pose; 8 moments of her attack, spells and run). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a girl; image 11 how an animal body is drawn).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of the lantern to the hooves, centred, comfortable transparent margins, nothing cut off (all the bough, the lantern and the tail inside the picture).
The character: Lillia, the Bashful Bloom, a shy FAWN CENTAUR: from the waist up a timid young girl, from the waist down the body of a young DEER standing on FOUR slender DEER LEGS. HEAD: long MAGENTA / RED-PURPLE HAIR falling down her back, a BLUE-VIOLET FLOWER BUD on top of her head, a GREEN LEAF CURL (a spiral sprout) at each side of the head by the ears; big PURPLE EYES, a shy, timid expression; pale cream skin. BODY: a girl's pale cream upper body wrapped in GREEN LEAVES (a small leaf top on the chest and shoulders, leaves round the wrists); below it the ORANGE-BROWN FAWN BODY with a pale beige belly and chest, a few darker stripes on the back, a short fluffy CREAM TAIL sticking up behind; the lower legs a darker red-brown, the HOOVES PURPLE.
THE BOUGH: a long thin DARK PURPLE branch, slightly twisted, its top bent into a GOLD HOOK with a small CYAN-BLUE BLOSSOM; from the hook hangs a round WICKER DREAM LANTERN (brown and green woven strands, a warm orange glow inside) with a small TASSEL under it.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the eyes, the bud and the hair drawn a little oversized so they read at small size); keep the fawn body and the legs COMPACT: the legs a bit shorter and sturdier than in the 3D model, so the figure is not much wider or taller than needed. 3/4 FRONT view facing image right, the girl's face and chest turned toward the viewer, the deer body pointing right; nothing covers the face or the hands.
Pose: League's idle (images 1 and 2): standing on all four legs, holding the bough UPRIGHT in both hands in front of her chest, the lantern hanging from the bough's tip high up at the upper right above her head. The four hooves are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the tail and the lantern stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the hair bright magenta with light pink highlights and deep purple-red shadows, the bough a bluish dark purple, the hooves a brighter blue-violet, the fawn body bright orange-brown, the belly off-white, the leaves bright green, the bud blue-violet, the lantern's glow warm orange; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no dream dust, no petals, no light rings, no particles, no bird, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`lillia-model-B.png`（枝条朝前平伸，灯笼吊在胸前高度）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-8 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look of this picture; 2 the same from more to the side: the length of the fawn body, the four legs, the tail and the length of the bough; 3 the head and upper body close-up: the hair, the flower bud, the leaf ear ornaments, the big eyes, the leaf top, the hands and the lantern; 4 the same pose from behind; 5 the official illustration: her mood; 6 and 7 a moment with the bough held forward low - THIS picture's pose; 8 moments of her attack, spells and run). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 9, 10 and 11 are STYLE ONLY, other characters: copy their pixel-art style (image 9 the latest approved picture of this series, a girl; image 11 how an animal body is drawn).
Create ONE full-body pixel-art picture of this character, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha), the character about 800 px tall from the top of the flower bud to the hooves, centred, comfortable transparent margins, nothing cut off (all the bough, the lantern and the tail inside the picture).
The character: Lillia, the Bashful Bloom, a shy FAWN CENTAUR: from the waist up a timid young girl, from the waist down the body of a young DEER standing on FOUR slender DEER LEGS. HEAD: long MAGENTA / RED-PURPLE HAIR falling down her back, a BLUE-VIOLET FLOWER BUD on top of her head, a GREEN LEAF CURL (a spiral sprout) at each side of the head by the ears; big PURPLE EYES, a shy, timid expression; pale cream skin. BODY: a girl's pale cream upper body wrapped in GREEN LEAVES (a small leaf top on the chest and shoulders, leaves round the wrists); below it the ORANGE-BROWN FAWN BODY with a pale beige belly and chest, a few darker stripes on the back, a short fluffy CREAM TAIL sticking up behind; the lower legs a darker red-brown, the HOOVES PURPLE.
THE BOUGH: a long thin DARK PURPLE branch, slightly twisted, its top bent into a GOLD HOOK with a small CYAN-BLUE BLOSSOM; from the hook hangs a round WICKER DREAM LANTERN (brown and green woven strands, a warm orange glow inside) with a small TASSEL under it.
Proportions: game-sprite proportions like images 9-11 - a bigger head than in the 3D model (the eyes, the bud and the hair drawn a little oversized so they read at small size); keep the fawn body and the legs COMPACT: the legs a bit shorter and sturdier than in the 3D model, so the figure is not much wider or taller than needed. 3/4 FRONT view facing image right, the girl's face and chest turned toward the viewer, the deer body pointing right; nothing covers the face or the hands.
Pose: images 6 and 7: standing on all four legs, the near hand holding the bough out FORWARD and LOW, roughly level, toward image right, so the lantern hangs from its tip in front of her at about chest height; the other hand raised shyly near her chest. The bough is not taller than her head. The four hooves are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them); the tail and the lantern stay above that line.
Style: detailed crisp pixel art like images 9-11 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the hair bright magenta with light pink highlights and deep purple-red shadows, the bough a bluish dark purple, the hooves a brighter blue-violet, the fawn body bright orange-brown, the belly off-white, the leaves bright green, the bud blue-violet, the lantern's glow warm orange; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no dream dust, no petals, no light rings, no particles, no bird, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），横版 1536×1024，四周留边，人物、枝条、灯笼、尾巴都完整。
- 半人半鹿：上身小姑娘、下身小鹿、**四条鹿腿**、紫色蹄子、米白色的短尾巴翘着。
- 洋红长发、头顶蓝紫花苞、两边绿色叶子卷、**大大的紫色眼睛**、害羞的表情、绿叶小上衣。
- 深紫色细长枝条 + 金色弯钩 + 青蓝小花 + 圆藤编灯笼（暖橙光）+ 小流苏；握枝条的手看得见。
- A：枝条竖着抱在胸前、灯笼在头顶右上方；B：枝条朝前平伸、灯笼吊在胸前高度，不比头高。
- 四只蹄子是最低点，落在一条水平线上；没有任何特效，没有那只小鸟。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/lillia-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/lillia/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40–42 行；鹿身让每帧更宽——宽度要先给用户看取舍）。
- A 的枝条和灯笼会把高度顶上去：第 1 步的 40–42 行算到哪里（灯笼顶 / 花苞顶）要和用户确认。
