# 泽拉斯：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 泽拉斯还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（悬浮站立，两臂垂在身侧略张开，爪子手半张）；**B = 英雄联盟 Q（奥能脉冲）蓄力**（身体后仰，后手高举，前手向前伸出，手心聚着一团青白色奥术能量）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行，从兜帽顶到腿尖）。
> - **长相照英雄联盟原版**（附图 1–7）：泽拉斯是一个**纯奥术能量组成的身体**（亮青蓝色到白色、发光），被**一块块深紫灰色的石质封印铠甲**锁住，能量从铠甲的缝隙里透出来。
> - **头**：一顶**圆顶石兜帽**（深紫灰色，中间一道竖棱、边缘一圈铆钉条），兜帽的开口里是**发光的能量脸**——画出**两只发白光的三角形眼睛**，小尺寸下也要看得见两只眼睛。
> - **上身**：两肩各一块**大肩甲**（深紫灰色石板，顶上有小尖刺，刻着回纹花纹）；**两条粗铁链**从肩膀斜挂到胸前，交汇在胸口一块**金色五边形封印**上（中间一个发橙光的符文）；胸口、腰、上臂、前臂都有刻花纹的石板，板与板之间露出发光的能量身体。
> - **手**：手是**蓝色的能量爪子**（亮天蓝色，指尖细长），从前臂石板里伸出来。
> - **下身**：**没有脚**——两条腿是一节节往下变细的石板，最后收成**两个锋利的尖头**，他是悬浮的；尖头之间和板缝里透出能量光。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的丽桑卓、基兰、蛮王）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头（兜帽）比英雄联盟模型大一些（约占身高三分之一），肩甲宽，下身稍短；眼睛、金色封印、蓝色爪子、铁链画大一点，小尺寸下才看得出来。铠甲是深紫灰色的，要用**深紫灰、蓝灰几档颜色加亮紫灰的边缘高光**画出石板和花纹，不要糊成一整块黑；能量身体用**亮青、浅青、白**几档，让它看起来在发光（但不要柔光、不要渐变）。
> - **3/4 正面朝右**，兜帽的开口朝向观众：两只眼睛都要看得见。
> - 除了能量身体本来的光和 B 版手里的那团能量，不画任何特效（光束、法球、炮击第 3 步再单独画）；**两条腿的尖头是最低点**，落在一条地面线上（游戏在这条线下画血条）。
> - 交付：`outputs/xerath-picture/xerath-model-A.png`、`outputs/xerath-picture/xerath-model-B.png`（都是 1024×1536 竖版、真透明背景，人物从兜帽顶到腿尖约 1200 px）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_xerath_league_front.png` | 英雄联盟原版泽拉斯，待机第一帧，3/4 朝右 | 铠甲、颜色、A 的姿势 |
| `refs/2_xerath_league_frontal.png` | 同一帧，更正面一点 | 兜帽、铁链、金色封印、两只手、两条尖腿 |
| `refs/3_xerath_league_head.png` | 兜帽和肩膀的特写 | 兜帽形状、两只发光的眼睛、肩甲尖刺、铁链 |
| `refs/4_xerath_league_side.png` | 同一帧的侧面 | 石板的厚度、尖腿 |
| `refs/5_xerath_splash.png` | 官方加载画面 | **看气氛和能量的颜色**（渲染图里能量是白色的，游戏里是亮青蓝色发光） |
| `refs/6_xerath_league_q_charge.png` | 英雄联盟 Q 蓄力那一帧 | B 的姿势（后仰、后手高举、前手前伸） |
| `refs/7_xerath_league_r_channel.png` | 英雄联盟 R 引导那一帧 | 看手臂抬起时铠甲的样子 |
| `style/8_style_lissandra.png` | 你之前的丽桑卓像素图 | **只看风格**（悬浮、没有脚的法师） |
| `style/9_style_zilean.png` | 你之前的基兰像素图 | **只看风格**（法师） |
| `style/10_style_tryndamere.png` | 你之前的蛮王像素图 | **只看风格**（最近通过的一张，深灰金属怎么画亮边） |

## 提示词 A：`xerath-model-A.png`（英雄联盟待机：悬浮站立，两臂垂在身侧）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the hood, the chains, the gold seal, both hands, the two pointed legs; 3 the hood and shoulders close-up: the hood's shape, the two glowing eyes, the spiked shoulder plates, the chains; 4 the same pose in profile: the thickness of the plates, the pointed legs; 5 the official illustration, for the mood and the colour of the energy; 6 League's Arcanopulse charge, the pose of version B; 7 League's Rite of the Arcane channel, the armour with the arms raised). Copy from them the armour, the colours and the shapes - NOT their 3D shading. In the 3D renders his energy body shows as flat white: in the game it is a glowing bright cyan-blue, as in image 5. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a floating mage without feet, image 9 a mage, image 10 the latest approved picture of this series, dark metal drawn with lit edges).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1200 px tall from the top of the hood to the tips of the legs, centred, comfortable transparent margins, nothing cut off.
The character: Xerath, the Magus Ascendant: an ancient sorcerer whose body is PURE ARCANE ENERGY - glowing bright cyan-blue and white - bound inside a sarcophagus of separate DARK PURPLE-GREY STONE ARMOUR PLATES; the energy shows in every gap between the plates. HEAD: a rounded stone HOOD (dark purple-grey, a ridge down its middle, a riveted rim), and inside its opening a face of glowing energy with TWO bright white glowing TRIANGULAR EYES. SHOULDERS: a big carved stone PAULDRON on each shoulder with small spikes on top and engraved meander patterns. CHEST: two heavy iron CHAINS run from the shoulders down across the chest and meet at a GOLD PENTAGON SEAL in the middle of the chest with a glowing orange rune; carved stone plates on the chest, the waist, the upper arms and the forearms, the glowing energy body between them. HANDS: bright AZURE-BLUE clawed hands of energy with long thin fingers, coming out of the forearm plates. LOWER BODY: NO FEET - two legs of stacked stone plates that taper down to two SHARP POINTS; he floats; energy light between the plates and between the points.
Proportions: game-sprite proportions like images 8-10 - a bigger head (the hood) than in the 3D model (about a third of his height), broad shoulders, a shorter lower body; the eyes, the gold seal, the blue claws and the chains drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the opening of the hood turned toward the viewer: both glowing eyes visible.
Pose: League's own idle (image 1): floating upright in 3/4 view facing image right, the arms hanging at his sides held a little away from the body, the clawed hands half open; the two pointed legs close together under him. The tips of the two legs are the lowest thing in the picture, both on one horizontal ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The armour is DARK PURPLE-GREY stone: draw it in dark purple-grey and blue-grey shades with light lilac-grey lit edges and highlights (never one flat black mass - black is only the outline), so its plates, spikes and carved patterns read; the energy body bright cyan, pale cyan and white flat shades so it looks lit from inside; the hands azure blue with white-blue highlights; the chains steel grey; the seal gold with an orange centre; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects beyond the energy body's own light, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`xerath-model-B.png`（英雄联盟 Q 奥能脉冲蓄力：后仰，后手高举，前手前伸聚能）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the hood, the chains, the gold seal, both hands, the two pointed legs; 3 the hood and shoulders close-up: the hood's shape, the two glowing eyes, the spiked shoulder plates, the chains; 4 the same pose in profile: the thickness of the plates, the pointed legs; 5 the official illustration, for the mood and the colour of the energy; 6 League's Arcanopulse charge, the pose of version B; 7 League's Rite of the Arcane channel, the armour with the arms raised). Copy from them the armour, the colours and the shapes - NOT their 3D shading. In the 3D renders his energy body shows as flat white: in the game it is a glowing bright cyan-blue, as in image 5. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a floating mage without feet, image 9 a mage, image 10 the latest approved picture of this series, dark metal drawn with lit edges).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1200 px tall from the top of the hood to the tips of the legs, centred, comfortable transparent margins, nothing cut off.
The character: Xerath, the Magus Ascendant: an ancient sorcerer whose body is PURE ARCANE ENERGY - glowing bright cyan-blue and white - bound inside a sarcophagus of separate DARK PURPLE-GREY STONE ARMOUR PLATES; the energy shows in every gap between the plates. HEAD: a rounded stone HOOD (dark purple-grey, a ridge down its middle, a riveted rim), and inside its opening a face of glowing energy with TWO bright white glowing TRIANGULAR EYES. SHOULDERS: a big carved stone PAULDRON on each shoulder with small spikes on top and engraved meander patterns. CHEST: two heavy iron CHAINS run from the shoulders down across the chest and meet at a GOLD PENTAGON SEAL in the middle of the chest with a glowing orange rune; carved stone plates on the chest, the waist, the upper arms and the forearms, the glowing energy body between them. HANDS: bright AZURE-BLUE clawed hands of energy with long thin fingers, coming out of the forearm plates. LOWER BODY: NO FEET - two legs of stacked stone plates that taper down to two SHARP POINTS; he floats; energy light between the plates and between the points.
Proportions: game-sprite proportions like images 8-10 - a bigger head (the hood) than in the 3D model (about a third of his height), broad shoulders, a shorter lower body; the eyes, the gold seal, the blue claws and the chains drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the opening of the hood turned toward the viewer: both glowing eyes visible.
Pose: League's Arcanopulse charge (image 6): floating in 3/4 view facing image right, the upper body leaning back a little; the back arm raised high behind his head, its claw open upward; the front arm stretched forward toward image right with the palm open, a round ball of bright cyan-white arcane energy gathering in front of that hand; the two pointed legs angled a little back under him. The tips of the two legs are the lowest thing in the picture, both on one horizontal ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The armour is DARK PURPLE-GREY stone: draw it in dark purple-grey and blue-grey shades with light lilac-grey lit edges and highlights (never one flat black mass - black is only the outline), so its plates, spikes and carved patterns read; the energy body bright cyan, pale cyan and white flat shades so it looks lit from inside; the hands azure blue with white-blue highlights; the chains steel grey; the seal gold with an orange centre; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects beyond the energy body's own light and the energy ball in the front hand, no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整。
- 圆顶石兜帽，开口里两只发白光的三角眼睛，看得见。
- 两肩带尖刺的大肩甲、两条铁链交汇在胸口的金色五边形封印（橙色符文）。
- 石板之间透出亮青蓝色的能量身体；两只亮蓝色能量爪子。
- 没有脚：两条一节节变细的石板腿收成尖头，尖头是最低点，落在一条水平线上；没有多余特效。
- 铠甲是深紫灰色，有亮紫灰的边缘高光，不是一整块黑。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/xerath-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
