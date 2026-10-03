# 亚托克斯（剑魔）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 剑魔还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（照附图 1 的站姿和握剑位置：弯膝、重心前压，一只手握着巨剑垂向身前，剑尖靠近地面但不低于脚底；另一只手张开利爪；双翼收在背后）；**B = 拄剑站姿**（站直，巨剑剑尖朝下立在身体近侧、剑尖落在脚底线上，近侧的手按在护手上，远侧的手张开利爪；双翼收在背后）。你挑一版，之后第 1 步再按它画游戏尺寸（约 42 格）的精灵。
> - **长相照英雄联盟经典皮肤**（附图 1–8）：高大魁梧的恶魔战士，全身是**深红色的血肉**（暗部是深褐红），粗壮的手臂、**带利爪的手**；头是一颗**长角的恶魔头**——深色的盔甲骷髅面、两只**向后掠的大角**（黑色、炭灰高光）、粗眉骨、**一双发光的橙红色眼睛**、带獠牙的下颌，没有头发。**黑铁盔甲**带暗红色亮边：带尖刺的大肩甲、胸前和小臂的甲片、腰带、腰前垂着破烂的暗红布、带甲的小腿和利爪脚。背上一对**蝙蝠一样的恶魔翅膀**（暗红膜、黑色骨节和小尖刺），**收拢贴在背后、画小一点**——张开大翅膀是大招的事（以后的步骤）。
> - **巨剑是他的标志，要大要清楚**：暗裔巨剑，和他差不多一样长（剑柄到剑尖），宽而厚、略带弧度的**深红色剑身**，黑色锯齿状的剑脊和牙齿一样的锯齿刃，剑身上有红色血管纹，深色护手和剑柄，**护手上方的剑身里嵌着一只发光的橙红色眼睛**。
> - 脚底是最低点 = 脚底线，剑尖、布、翅膀都不能低于它（游戏在脚下画血条）。剑不要高过角尖，轮廓要紧凑（游戏里只有约 42 格高）。
> - **风格和比例照附图 9–10**（你之前让 Codex 画的凯南 A、乐芙兰 A）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；Q 版比例但身材魁梧，头（不算角）约占身高的 30%。他是暗色角色，要有亮的高光才看得清：肌肉上的红粉色高光、盔甲边缘和角上的灰红色轮廓光、剑刃和剑脊的亮边，眼睛和剑上的眼睛是全图最亮的地方。
> - 不画特效、血、红光和地面；只画人物本身。
> - 交付：`outputs/aatrox-picture/aatrox-model-A.png`、`outputs/aatrox-picture/aatrox-model-B.png`（1024×1536，真透明背景，人物约 1200 px 高），附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**写 `outputs/aatrox-picture/HANDOFF.md`（交付说明）。

**怎么打包（在你自己的电脑上，需要本机的英雄联盟客户端）：**

```bash
python tools/lol/aatrox_picture_pack.py --lol "D:\WeGameApps\lol"
```

它从本机客户端渲染剑魔的参考图（附图 1–7）、取出加载画面原画（附图 8），再放进仓库里凯南 A、乐芙兰 A 两张风格图和这份提示词，生成 `dist/aatrox_picture_pack.zip`。把整个 zip 交给 Codex 就行。渲染图是拳头公司的模型，只留在本机（`dist/` 不进仓库）。某张图渲染失败时脚本会说明、照样打包其余的，缺的那几张在下表里都标了能不能省。

Codex 的生图工具一次最多收五张参考图（凯南那次 Codex 说的）。五张时用：**1a 或 1b**（看得到脸和胸口的那张）、**3a 或 3b**（同样挑看得到脸的）、**4**、**9**、**10**。

## 附图

| 文件 | 内容 | 用在 | 能省吗 |
|---|---|---|---|
| `refs/1a_aatrox_league_front.png` | 英雄联盟经典皮肤剑魔，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 | 和 1b 留一张 |
| `refs/1b_aatrox_league_front_mirror.png` | 同一帧从另一侧渲染再左右翻转 | 1a 看到的是背面时用这张 | 和 1a 留一张 |
| `refs/2_aatrox_league_frontal.png` | 同一帧，几乎正面 | 胸口、甲片、腰前的布 | 能 |
| `refs/3a_aatrox_league_head.png` | 头部特写（从 1a 那一侧） | 角、骷髅面、发光的眼睛、獠牙 | 和 3b 留一张 |
| `refs/3b_aatrox_league_head_mirror.png` | 头部特写（从 1b 那一侧） | 同上 | 和 3a 留一张 |
| `refs/4_aatrox_league_side.png` | 正侧面 | 翅膀收在背上的样子、巨剑的侧影 | 尽量留 |
| `refs/5_aatrox_league_back.png` | 3/4 背面 | 翅膀怎么长在背上、背后的甲 | 能 |
| `refs/6_aatrox_league_ult.png` | 大招「大灭」，翅膀张开的几帧 | **只用来看懂翅膀的结构，不要画张开的翅膀** | 能 |
| `refs/7_aatrox_league_q.png` | Q「暗裔利刃」挥剑的几帧 | **只用来看懂他怎么握剑，不画这些姿势** | 能 |
| `refs/8_aatrox_loadscreen.png` | 官方加载画面原画 | **只看气氛和脸**，服装以 1–5 为准 | 能 |
| `style/9_style_kennen.png` | 你之前的凯南像素图（A） | **只看风格和 Q 版比例**（背上大道具的画法） | 留 |
| `style/10_style_leblanc.png` | 你之前的乐芙兰像素图（A） | **只看风格和 Q 版比例**（暗红、深色衣服的亮边画法） | 留 |

## 提示词 A：`aatrox-model-A.png`（英雄联盟待机：单手握剑垂向身前，双翼收拢）

附图都附上，顺序同上表（只能附五张时见上面）。

```text
Attached images: 1a/1b, 2, 3a/3b, 4, 5, 6, 7 and 8 are 3D renders and art of the character from the game (1a and 1b are the same idle frame rendered from both sides - use the one where his face and chest face the viewer; 2 nearly frontal; 3a/3b the head close-up from the same two sides; 4 a side view showing the folded wings and the sword's profile; 5 a back view showing how the wings sit on his back; 6 his ultimate with the wings opening - ONLY to understand the wings, do NOT draw them spread; 7 his sword swings - ONLY to understand how he holds the sword; 8 the official illustration, for the mood and the face only - follow 1-5 for the costume). Copy from them the costume, the colours, the horned head, the folded wings and the sword - NOT their 3D shading and NOT their adult proportions. Images 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions (image 9 shows how a big prop stays readable in this style). If only some of these images are attached, use the ones you have in the same roles.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1200 px tall from the tips of the horns to the soles, centred, comfortable transparent margins (the horns, the wings, the sword and the feet must not be cut off).
The character: Aatrox, the Darkin Blade: a towering demonic warrior bound to a living greatsword. BODY: huge and heavily muscled, broad shoulders, a powerful chest, thick arms ending in CLAWED hands; his flesh is DEEP CRIMSON red (3-4 reds from blood red to dark maroon in the shadows) with darker muscle lines. HEAD: a demonic horned head - a dark armoured skull-like face with two big HORNS sweeping back from the brow (black with charcoal-grey highlights), a heavy brow ridge, two GLOWING red-orange EYES (the brightest spots of the head), a fanged jaw; no hair. ARMOUR: blackened dark-iron plates with crimson rim highlights, as in the renders - a big spiked pauldron, plates on the chest and the forearms, a belt, a tattered dark-red cloth hanging in front of the hips, armoured greaves and clawed armoured feet. WINGS: two dark bat-like DEMON WINGS (dark maroon membranes, black bony fingers with small spikes) FOLDED behind his shoulders - keep them small and close to his back, their tops a little above the shoulders, their lower ends at the hips. THE SWORD (his signature - keep it big and clear): the Darkin greatsword, about as long as he is tall from the pommel to the tip, a broad, heavy, slightly curved CRIMSON blade with a black jagged spine and serrated tooth-like edges, red veins running along it, a dark crossguard and hilt, and one glowing orange-red EYE set in the blade just above the crossguard.
Proportions: chibi like images 9 and 10, but a big bruiser - the head (from the horn base to the chin, without the horns) about 30% of the height from the crown to the soles, big clear glowing eyes, a massive chest and arms, sturdy legs; the sword oversized. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH glowing eyes visible and level (the horns sweep back, never in front of the face), the chest visible (never show his back).
Pose: League's own idle (image 1a/1b): copy its stance and where the sword is held. He stands heavy and menacing, knees bent, the weight forward like a predator about to strike; the greatsword in one hand, lowered, its blade slanting down toward the ground in front of him, the tip close to but NOT below the soles line; the free hand open with its claws spread; the wings folded on his back; his head turned toward image right with both glowing eyes visible. Keep the silhouette compact: no part of the sword higher than the tips of his horns. The soles are the lowest thing in the picture: the sword tip, the cloth and the wings end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 9 and 10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (crimson flesh, dark iron armour, black horns, maroon wing membranes, crimson blade) - coloured darks, never black fill (black is only the outline); bright highlights so the dark character reads: crimson-pink highlights on the muscles, a grey-red rim light on the armour edges and the horns, the blade's edge and spine lit, the eyes and the sword's eye glowing orange-red; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no blood, no flames, no magic effects, no text, no frame, no other characters.
```

## 提示词 B：`aatrox-model-B.png`（拄剑站姿：剑尖朝下立在近侧，手按护手）

附图同 A。

```text
Attached images: 1a/1b, 2, 3a/3b, 4, 5, 6, 7 and 8 are 3D renders and art of the character from the game (1a and 1b are the same idle frame rendered from both sides - use the one where his face and chest face the viewer; 2 nearly frontal; 3a/3b the head close-up from the same two sides; 4 a side view showing the folded wings and the sword's profile; 5 a back view showing how the wings sit on his back; 6 his ultimate with the wings opening - ONLY to understand the wings, do NOT draw them spread; 7 his sword swings - ONLY to understand how he holds the sword; 8 the official illustration, for the mood and the face only - follow 1-5 for the costume). Copy from them the costume, the colours, the horned head, the folded wings and the sword - NOT their 3D shading and NOT their adult proportions. Images 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions (image 9 shows how a big prop stays readable in this style). If only some of these images are attached, use the ones you have in the same roles.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1200 px tall from the tips of the horns to the soles, centred, comfortable transparent margins (the horns, the wings, the sword and the feet must not be cut off).
The character: Aatrox, the Darkin Blade: a towering demonic warrior bound to a living greatsword. BODY: huge and heavily muscled, broad shoulders, a powerful chest, thick arms ending in CLAWED hands; his flesh is DEEP CRIMSON red (3-4 reds from blood red to dark maroon in the shadows) with darker muscle lines. HEAD: a demonic horned head - a dark armoured skull-like face with two big HORNS sweeping back from the brow (black with charcoal-grey highlights), a heavy brow ridge, two GLOWING red-orange EYES (the brightest spots of the head), a fanged jaw; no hair. ARMOUR: blackened dark-iron plates with crimson rim highlights, as in the renders - a big spiked pauldron, plates on the chest and the forearms, a belt, a tattered dark-red cloth hanging in front of the hips, armoured greaves and clawed armoured feet. WINGS: two dark bat-like DEMON WINGS (dark maroon membranes, black bony fingers with small spikes) FOLDED behind his shoulders - keep them small and close to his back, their tops a little above the shoulders, their lower ends at the hips. THE SWORD (his signature - keep it big and clear): the Darkin greatsword, about as long as he is tall from the pommel to the tip, a broad, heavy, slightly curved CRIMSON blade with a black jagged spine and serrated tooth-like edges, red veins running along it, a dark crossguard and hilt, and one glowing orange-red EYE set in the blade just above the crossguard.
Proportions: chibi like images 9 and 10, but a big bruiser - the head (from the horn base to the chin, without the horns) about 30% of the height from the crown to the soles, big clear glowing eyes, a massive chest and arms, sturdy legs; the sword oversized. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH glowing eyes visible and level (the horns sweep back, never in front of the face), the chest visible (never show his back).
Pose: a warlord at rest: he stands upright and menacing, feet apart, chest out, head up; the greatsword stands upright BESIDE him on his near side (image right of his body), point down, its tip resting ON the soles line (not below it), the blade beside his leg and hip, the crossguard at about his shoulder height, the pommel at about his head height; his near clawed hand rests on the crossguard, the far hand hangs open at his side with its claws spread; the wings folded on his back; both glowing eyes look toward image right / the viewer. The blade must not cover his face or his chest. Keep the silhouette compact: no part of the sword higher than the tips of his horns. The soles are the lowest thing in the picture: the sword tip, the cloth and the wings end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 9 and 10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (crimson flesh, dark iron armour, black horns, maroon wing membranes, crimson blade) - coloured darks, never black fill (black is only the outline); bright highlights so the dark character reads: crimson-pink highlights on the muscles, a grey-red rim light on the armour edges and the horns, the blade's edge and spine lit, the eyes and the sword's eye glowing orange-red; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no blood, no flames, no magic effects, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，角尖、翅膀、巨剑、脚都没被切掉。
- 两只发光的橙红色眼睛都在、同一高度、看得清；角向后掠，没有挡住脸；看得到胸口（不是背面）。
- 巨剑完整：深红剑身、黑色锯齿剑脊、锯齿刃、护手上方那只发光的眼睛；剑和他差不多一样长，但不高过角尖。
- 翅膀收拢、贴在背后、比较小（大招才张开）。
- 脚底是最低点，剑尖、布、翅膀都不低于它。
- 暗色身体有亮边和高光，缩小看也分得清头、身体、剑、翅膀；大像素块清楚，没有糊、没有柔光、没有渐变、没有特效。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
