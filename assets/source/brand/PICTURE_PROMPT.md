# 布兰德：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 布兰德还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（微微弓身、膝盖弯着，两只燃烧的手张开放在身前腰部高度）；**B = 施法**（靠后的手高高举起、掌心朝上托着火，靠前的手在身前张开）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行）。
> - **长相照英雄联盟原版**（附图 1–6）：复仇焰魂布兰德，一个**被烈火烧成焦炭的男人**：瘦削但肌肉线条分明的身体，皮肤是**焦黑 / 深灰紫的炭色**，上面爬满**发光的熔岩裂纹**（亮橙、金黄，胸口正中一道最亮的竖裂）；**光头**，头顶和后脑**燃着一簇火焰**（像头发一样往上窜，附图 5 的加载画面），眼睛是**发光的黄橙色**，脸上带怒意；两条前臂从手肘往下越来越红，**两只手是透亮的橙黄色火焰手**。
> - **服装**：只穿一条**棕褐色的破旧长裤**（到小腿，裤脚撕成参差的布条），腰间一条**粗布腰带**，一条腿外侧有一排**铜色搭扣 / 带扣**；上身赤裸；**光脚**（焦黑的脚，脚背也有细细的熔岩裂纹）。
> - **风格和比例照附图 7–9**（你之前画的泽拉斯、派克、蛮王）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（约占身高三分之一）；**黑色身体在小尺寸下容易糊成一团：裂纹画成清楚的 1–2 格亮橙线**，身体的炭色用几档带紫的深灰（亮面要看得出肌肉块），头顶火焰、发光的眼睛、火焰手、胸口亮裂纹画大一点。
> - **画布竖版 1024×1536**：人物从火焰顶到脚底约 1100 px，居中，四周留边。
> - **3/4 正面朝右**，脸朝向观众：两只发光的眼睛都要看得见，不能画成背影。
> - 头顶的火焰算他身体的一部分（像头发），要画；**除此以外不画任何特效**（火球、火柱、火焰轨迹第 3 步再单独画）；脚底是最低点，平平地落在一条地面线上（游戏在脚下画血条）。
> - 交付：`outputs/brand-picture/brand-model-A.png`、`outputs/brand-picture/brand-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `brand_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_brand_league_front.png` | 英雄联盟原版布兰德，待机第一帧，3/4 朝右 | 身体、裤子、A 的姿势 |
| `refs/2_brand_league_frontal.png` | 同一帧，正面 | 胸口裂纹、腰带、搭扣 |
| `refs/3_brand_league_head.png` | 头和肩的特写 | 脸、发光的眼睛、头上的裂纹 |
| `refs/4_brand_league_back.png` | 同一帧的背后 | 背上的裂纹、裤子背面 |
| `refs/5_brand_splash.png` | 官方加载画面 | **头顶的火焰**、气质（愤怒）、颜色 |
| `refs/6_brand_league_actions.png` | 英雄联盟里普攻、Q、W、E、R 的几个瞬间 | 火焰手的样子、B 的举手姿势（第 1、3 格） |
| `style/7_style_xerath.png` | 你之前的泽拉斯像素图 | **只看风格**（发光的魔法英雄） |
| `style/8_style_pyke.png` | 你之前的派克像素图 | **只看风格**（深色身体怎么保持清楚） |
| `style/9_style_tryndamere.png` | 你之前的蛮王像素图 | **只看风格**（赤裸上身、肌肉） |

## 提示词 A：`brand-model-A.png`（英雄联盟待机：弓身，双手张开在身前）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen from the front: the chest cracks, the belt, the buckles; 3 the head and shoulders close-up: the face, the glowing eyes; 4 the same pose from behind; 5 the official illustration: the FLAMES burning on top of his head, his mood and colours; 6 a few moments of his attack and spells: how his burning hands look, and in frames 1 and 3 a hand raised high). Copy from the images the body, the costume, the colours and the shapes - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (7 a glowing magic hero of this series, 8 a dark-bodied hero kept readable, 9 a bare-chested muscular hero).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), the character about 1100 px tall from the top of the head flames to the soles, centred, comfortable transparent margins, nothing cut off.
The character: Brand, the Burning Vengeance: a man burned into living charcoal. A lean, sinewy, muscular body; the skin CHARRED BLACK / dark purple-grey charcoal, covered with GLOWING LAVA CRACKS in bright orange and golden yellow, the brightest one running straight down the middle of his chest. HEAD: bald, with lava cracks over the skull, a crown of FLAMES burning on top and the back of his head and rising like hair (image 5), GLOWING YELLOW-ORANGE EYES, an angry face. ARMS: the forearms turn redder toward the wrists and his two HANDS are translucent glowing ORANGE-YELLOW FIRE hands. BODY: bare chest; ragged TAN-BROWN trousers down to the calves with torn, jagged hems, a thick cloth belt, a row of COPPER buckles/straps down the outside of one leg; BARE charred feet with thin lava cracks.
Proportions: game-sprite proportions like images 7-9 - a bigger head than in the 3D model (about a third of his height with the flames), a lean body; the head flames, the glowing eyes, the fire hands and the chest crack drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both glowing eyes visible, nothing covers the face.
Pose: League's own idle (image 1), turned a little more toward the viewer: a slight menacing crouch facing image right, knees a little bent, feet apart; both burning hands open in front of him at waist height, fingers spread like claws. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the charcoal skin in purplish dark greys with clear lighter planes on the muscles (so the dark body never turns into one black blob), the lava cracks as clean 1-2 pixel bright orange/yellow lines, the fire hands and head flames in orange, yellow and near-white cores, the trousers tan-brown, the buckles copper; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No fireballs, no flame trails, no pillars of fire, no aura, no particles (only the flames on his head and his fire hands), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`brand-model-B.png`（施法：靠后的手高举托火）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle; 2 the same pose seen from the front: the chest cracks, the belt, the buckles; 3 the head and shoulders close-up: the face, the glowing eyes; 4 the same pose from behind; 5 the official illustration: the FLAMES burning on top of his head, his mood and colours; 6 a few moments of his attack and spells: how his burning hands look, and in frames 1 and 3 a hand raised high - the pose of version B). Copy from the images the body, the costume, the colours and the shapes - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (7 a glowing magic hero of this series, 8 a dark-bodied hero kept readable, 9 a bare-chested muscular hero).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), the character about 1100 px tall from the top of the head flames (or the raised hand) to the soles, centred, comfortable transparent margins, nothing cut off.
The character: Brand, the Burning Vengeance: a man burned into living charcoal. A lean, sinewy, muscular body; the skin CHARRED BLACK / dark purple-grey charcoal, covered with GLOWING LAVA CRACKS in bright orange and golden yellow, the brightest one running straight down the middle of his chest. HEAD: bald, with lava cracks over the skull, a crown of FLAMES burning on top and the back of his head and rising like hair (image 5), GLOWING YELLOW-ORANGE EYES, an angry face. ARMS: the forearms turn redder toward the wrists and his two HANDS are translucent glowing ORANGE-YELLOW FIRE hands. BODY: bare chest; ragged TAN-BROWN trousers down to the calves with torn, jagged hems, a thick cloth belt, a row of COPPER buckles/straps down the outside of one leg; BARE charred feet with thin lava cracks.
Proportions: game-sprite proportions like images 7-9 - a bigger head than in the 3D model (about a third of his height with the flames), a lean body; the head flames, the glowing eyes, the fire hands and the chest crack drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both glowing eyes visible, nothing covers the face.
Pose: casting (image 6, frames 1 and 3): standing facing image right, feet apart, knees slightly bent; the BACK arm (image left side of his body) raised high beside his head, the burning hand open palm up above shoulder level as if gathering fire, the arm beside the head, never across the face; the FRONT hand open forward at chest height, fingers spread. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the charcoal skin in purplish dark greys with clear lighter planes on the muscles (so the dark body never turns into one black blob), the lava cracks as clean 1-2 pixel bright orange/yellow lines, the fire hands and head flames in orange, yellow and near-white cores, the trousers tan-brown, the buckles copper; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No fireballs, no flame trails, no pillars of fire, no aura, no particles (only the flames on his head and his fire hands), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，人物完整（头顶火焰、举起的手都在画面里）。
- 焦黑炭色身体 + 清楚的亮橙熔岩裂纹（胸口正中最亮）；身体有亮面，不是一团黑。
- 光头 + 头顶一簇往上窜的火焰；两只发光的黄橙眼睛看得见。
- 两只透亮的橙黄火焰手；前臂往手腕越来越红。
- 棕褐破长裤（裤脚参差）+ 粗布腰带 + 一条腿外侧的铜搭扣；光脚。
- 脚底是最低点，落在一条水平线上；除了头顶火焰和火焰手，没有别的特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/brand-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/brand/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 40 行）。
