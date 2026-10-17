# 卡萨丁（虚空行者）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 卡萨丁还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**近侧那只手**，人、头盔、衣服完全一样：**A = 英雄联盟里的待机：两只手张开垂在身体两侧，近侧手掌心微微朝上、带一点青色微光**（附图 1、2）；**B = 虚空之刃出鞘：近侧前臂上长出一把紫色的虚空能量刃，手臂往前伸**（附图 8）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 36–38 行，侧面和 3/4 正面两张）。
> - **长相照英雄联盟原版**（附图 1–9）：卡萨丁，一个**高大的虚空法师**。头上是**深紫色的头盔面具**，头盔两边各有一只**向上弯的深紫色大角**，面具中间一条**银灰色的金属竖条**，面具下是**两只发光的橙色眼睛**（全身最亮的地方）；嘴的位置是**一个银灰色的金属呼吸罩**，从呼吸罩垂下**几根黑紫色的粗软管**，像胡子一样垂到胸前和肚子上。
> - **身体**：**赤裸的上身，青蓝色皮肤**（青绿偏蓝，肌肉块明显），**双手是更浅的发光青色**，手指细长张开；**两个肩膀上是深紫色肩甲，每个肩甲上竖着一只又大又弯的银灰色骨刺**（像弯刀）；前臂套着**深紫色护腕，护腕上有小银刺**；**背后背着一排黑灰色的金属罐**（附图 4）。
> - **下半身**：**一件很长的深紫色多层长袍从腰一直拖到地面**，像裙子一样往下张开，一层一层，每层下摆是**尖角**，镶着**银灰色的边**；**看不到腿和脚**（这是他的特色），长袍下摆就是最低点。腰上一圈深色的腰带，腰带前面一块尖角护片。
> - **姿势**（附图 1、2 = A；附图 8 = B）：3/4 正面朝右，站得笔直、高大。A：两只手张开垂在身体两侧，近侧（画面右边）的手掌心朝上、手指张开（**不要举过肩**）。B：近侧手臂往前伸（朝画面右边），**前臂上长出一把紫色的虚空能量刃**（又长又直、亮紫色到深紫色、刃边发白），远侧手张开垂在身旁。**脸（面具、两只橙色眼睛）和两只手都不能被挡住**。
> - **风格和比例照附图 10–12**（之前让你画的古拉加斯、泽拉斯、维克托）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；**头按原版比例，不要画成大头娃娃**（他又高又壮，头盔加角也只占身高的五分之一左右）；**整体收紧凑，不要画成巨大的块**（游戏里他和其他英雄差不多大）。颜色：**皮肤青蓝（亮部浅青、暗部深青蓝）、手发光浅青、头盔和长袍深紫（亮部紫、暗部近黑紫）、角深紫、骨刺和镶边银灰、眼睛橙色发光、软管黑紫、背后金属罐黑灰**；深色和浅色之间要有清楚的分界，不要糊成一团。
> - **画布用竖版 1024×1536**：从角尖到长袍下摆约 600 px；角、骨刺、虚空刃都在画面里，不能出画。
> - 不画任何特效（虚无法球、能量脉冲、虚空行走第 3 步再单独画；B 的虚空刃是他身体的一部分，可以画）；长袍下摆是最低点，平平地落在一条地面线上（游戏在脚下画血条）。
> - 交付：`outputs/kassadin-picture/kassadin-model-A.png`、`outputs/kassadin-picture/kassadin-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `kassadin_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_kassadin_league_front.png` | 英雄联盟原版卡萨丁待机，3/4 朝右 | 颜色、形状、A 的姿势 |
| `refs/2_kassadin_league_frontal.png` | 同一帧，正面 | 头盔面具、软管、胸口肌肉、长袍层次 |
| `refs/3_kassadin_league_head.png` | 头的特写 | 角、面具竖条、橙色眼睛、呼吸罩和垂下的软管、肩上骨刺 |
| `refs/4_kassadin_league_back.png` | 同一帧的背后 | 背后的金属罐 |
| `refs/5_kassadin_splash.png` | 官方加载画面 | 气质（阴沉、神秘、虚空的紫色） |
| `refs/6_kassadin_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 长袍拖地、身体前倾地飘着走 |
| `refs/7_kassadin_league_actions.png` | 普攻、Q 虚无法球、E 能量脉冲、R 虚空行走的瞬间 | 手怎么动 |
| `refs/8_kassadin_league_blade.png` | 第二段普攻：近侧手臂往前挥 | **B 的手臂姿势**（虚空刃长在这只前臂上） |
| `refs/9_kassadin_league_side.png` | 待机的侧面（朝右） | 侧面看头盔、角、长袍 |
| `style/10_style_gragas.png` | 你之前的古拉加斯像素图 | **只看风格**（最近通过的一张） |
| `style/11_style_xerath.png` | 你之前的泽拉斯像素图 | **只看风格**（同是长袍法师） |
| `style/12_style_viktor.png` | 你之前的维克托像素图 | **只看风格**（同是中路法师） |

## 提示词 A：`kassadin-model-A.png`（待机，两手张开）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and pose of this picture; 2 the same from the front: the helmet mask, the hoses, the chest, the layers of the robe; 3 the head close-up: the horns, the silver strip on the mask, the two glowing orange eyes, the metal breathing guard and the dark hoses hanging from it, the shoulder spikes; 4 the same pose from behind: the canisters on his back; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells: how the hands move; 8 his second attack with the near arm swung forward - not used in this version; 9 the same idle from the side). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 another robed mage, image 12 another mid-lane mage).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 600 px from the tips of his horns to the hem of his robe, centred, comfortable transparent margins, nothing cut off (both horns and both shoulder spikes inside the picture).
The character: Kassadin, the Void Walker, a tall, broad void mage. HEAD: a DARK-VIOLET HELMET MASK with TWO BIG DARK-VIOLET HORNS curving upward on its sides, a SILVER-GREY METAL STRIP down the middle of the mask, TWO GLOWING ORANGE EYES (the brightest thing on him), a SILVER-GREY METAL BREATHING GUARD over the mouth with several THICK DARK-VIOLET HOSES hanging from it down over his chest like a beard. BODY: a BARE MUSCULAR CHEST AND ARMS with CYAN-TEAL SKIN (clear muscle blocks), the HANDS a PALER GLOWING CYAN with long open fingers; DARK-VIOLET SHOULDER PLATES, each with ONE BIG CURVED SILVER-GREY BONE SPIKE standing up like a scimitar; dark-violet bracers with small silver spikes on the forearms; a row of dark-grey metal canisters on his back. LOWER BODY: a VERY LONG LAYERED DARK-VIOLET ROBE from the waist to the ground, flaring out like a skirt, layer under layer, each hem cut into POINTED TIPS and trimmed in SILVER-GREY; NO LEGS OR FEET SHOW - the robe's hem is his lowest part. A dark belt at the waist with a pointed plate in front.
Here both hands hang OPEN at his sides, the near hand (image right) turned palm-up with the fingers spread (NOT raised above the shoulder).
Proportions: game-sprite proportions like images 10-12, but keep HIS OWN proportions: tall and broad, the helmet with its horns about one fifth of his height - do NOT make a big-headed chibi. Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, the mask turned toward the viewer, nothing covers the mask, the eyes or the hands.
Pose: League's own idle (images 1 and 2): standing tall and straight. The hem of the robe is the lowest thing in the picture, flat on one ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 10-12 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the skin cyan-teal (pale cyan highlights, deep teal-blue shadows), the hands paler glowing cyan, the helmet and the robe dark violet (violet highlights, near-black violet shadows), the horns dark violet, the spikes and the trims silver-grey, the eyes glowing orange, the hoses black-violet, the canisters dark grey; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no orbs, no particles, no void energy around him, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`kassadin-model-B.png`（虚空之刃出鞘）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look of this picture; 2 the same from the front: the helmet mask, the hoses, the chest, the layers of the robe; 3 the head close-up: the horns, the silver strip on the mask, the two glowing orange eyes, the metal breathing guard and the dark hoses hanging from it, the shoulder spikes; 4 the same from behind: the canisters on his back; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells: how the hands move; 8 HIS SECOND ATTACK WITH THE NEAR ARM SWUNG FORWARD - the arm position of this picture; 9 the idle from the side). Copy from the images the shapes, the colours and the anatomy - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 another robed mage, image 12 another mid-lane mage).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 600 px from the tips of his horns to the hem of his robe, centred, comfortable transparent margins, nothing cut off (both horns, both shoulder spikes and the whole blade inside the picture).
The character: Kassadin, the Void Walker, a tall, broad void mage. HEAD: a DARK-VIOLET HELMET MASK with TWO BIG DARK-VIOLET HORNS curving upward on its sides, a SILVER-GREY METAL STRIP down the middle of the mask, TWO GLOWING ORANGE EYES (the brightest thing on him), a SILVER-GREY METAL BREATHING GUARD over the mouth with several THICK DARK-VIOLET HOSES hanging from it down over his chest like a beard. BODY: a BARE MUSCULAR CHEST AND ARMS with CYAN-TEAL SKIN (clear muscle blocks), the HANDS a PALER GLOWING CYAN with long open fingers; DARK-VIOLET SHOULDER PLATES, each with ONE BIG CURVED SILVER-GREY BONE SPIKE standing up like a scimitar; dark-violet bracers with small silver spikes on the forearms; a row of dark-grey metal canisters on his back. LOWER BODY: a VERY LONG LAYERED DARK-VIOLET ROBE from the waist to the ground, flaring out like a skirt, layer under layer, each hem cut into POINTED TIPS and trimmed in SILVER-GREY; NO LEGS OR FEET SHOW - the robe's hem is his lowest part. A dark belt at the waist with a pointed plate in front.
Here his NETHER BLADE is drawn: his near arm reaches forward toward image right (image 8), and from that forearm grows a LONG STRAIGHT BLADE OF VOID ENERGY along and beyond the hand - bright violet in the middle, deep violet at the back, a white-lilac cutting edge, hard pixel shapes like a solid blade (not a glow, not smoke); his far hand hangs open at his side.
Proportions: game-sprite proportions like images 10-12, but keep HIS OWN proportions: tall and broad, the helmet with its horns about one fifth of his height - do NOT make a big-headed chibi. Keep the whole figure COMPACT, not a giant block. 3/4 FRONT view facing image right, the mask turned toward the viewer, nothing covers the mask, the eyes or the hands.
Pose: standing tall and straight, only the near arm forward. The hem of the robe is the lowest thing in the picture, flat on one ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 10-12 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the skin cyan-teal (pale cyan highlights, deep teal-blue shadows), the hands paler glowing cyan, the helmet and the robe dark violet (violet highlights, near-black violet shadows), the horns dark violet, the spikes and the trims silver-grey, the eyes glowing orange, the hoses black-violet, the canisters dark grey, the blade bright violet with a white-lilac edge; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No other effects, no orbs, no particles, no void energy around him, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，人物、两只角、两只骨刺（B 还有整把刃）都完整。
- 深紫头盔面具、两只向上弯的角、面具中间银灰竖条、两只发光橙眼；银灰呼吸罩、垂到胸前的黑紫软管。
- 青蓝色赤裸上身、肌肉块清楚；双手浅青；深紫肩甲上各一只银灰弯骨刺；深紫护腕；背后黑灰金属罐。
- 深紫多层长袍拖地、尖角下摆、银灰镶边；**看不到腿和脚**。
- A 两手张开垂在两侧；B 近侧手往前伸、前臂长出紫色虚空刃（实心像素刃，不是光雾）。
- 头按原版比例，不要大头娃娃；面具、眼睛和两只手没被挡住；整体紧凑。
- 长袍下摆是最低点，落在一条水平线上；除了 B 的刃没有任何特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/kassadin-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画放进 `assets/source/kassadin/codex_picture/`，和包里的英雄并排给用户挑 A / B；选定后写第 1 步 `MODEL_PROMPTS.md`（游戏尺寸造型，约 36–38 行，**侧面朝右 + 3/4 正面两张**，记忆 side-view-design；Codex 直接画游戏尺寸，用原稿 2:1 描，绝不先画大再缩）。
- 长袍没有腿：跑动是整件长袍飘着前倾（英雄联盟里他就是飘着走），下摆轻轻摆动，不画交叉步的腿。动作全用侧面造型、同一张脸（面具）贯穿所有帧，只有待机和 BP 卡用 3/4 正面。
