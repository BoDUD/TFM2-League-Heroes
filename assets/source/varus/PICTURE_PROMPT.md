# 韦鲁斯：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 韦鲁斯还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站着、微微驼背，左手提着大弓垂在腿边，右手垂在身侧）；**B = 英雄联盟 Q（穿刺之箭）蓄力**（拉弓站稳，左手把张开的弓举在身前，右手把弦拉到脸旁，搭着一支发紫光的箭）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行）。
> - **长相照英雄联盟原版**（附图 1–7）：**银白色头发往后梳、在脑后扎起**；额头一条细细的深色头带，中间一颗**红宝石**；瘦长的脸、颧骨高、表情阴沉，两只眼睛都要看得见。脖子上一条**鲜红色围巾**，长长的红布尾巴垂在背后到臀部下面。
> - **上身**：赤裸的灰白色皮肤，精瘦有肌肉，右肩一道青色纹身；胸前斜挎一条深褐灰色皮带，挂着一个**大圆护符（金边、中间深青色玻璃）**；一根细绳项链挂一颗红色菱形吊坠。
> - **腐化**：两只手臂**从手肘往下变成暗红再变成紫色**，手是爪子，指尖发**紫光**；肚子和胯部也渐变成暗红色。
> - **下身**：贴身的**深紫黑色铠甲裤**，一节一节的甲片，胯部和膝盖有小尖刺、点缀着发紫光的小点；深紫色厚靴子；腰带前垂着几条短短的暗红布条。
> - **弓**：一把**巨大的深紫黑色活体暗裔之弓**，差不多和他的身体一样高，由一片片带尖刺、像爪子和骨头的弯甲组成，有发**紫光的纹路**，握把处一团亮紫光；拿在**左手**（画面右边那只手）。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的烬、凯隐、崔斯特）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（约占身高三分之一），身材精瘦，腿稍短；护符、红围巾、发光的手和弓画大一点，小尺寸下才看得出来。裤子、靴子和弓在游戏里是紫黑色的，要用**深紫、梅紫的几档颜色加紫色亮边和高光**画出甲片和尖刺，不要糊成一整块黑。
> - 除了弓和手上本来的紫光（B 版再加一支搭在弦上的箭），不画任何特效（箭雨、锁链第 3 步再单独画）；鞋底是最低点，平平地落在一条地面线上（游戏在脚下画血条）。
> - 交付：`outputs/varus-picture/varus-model-A.png`、`outputs/varus-picture/varus-model-B.png`（都是 1024×1536 竖版、真透明背景，人物从头顶到鞋底约 1250 px）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_varus_league_front.png` | 英雄联盟原版韦鲁斯，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_varus_league_frontal.png` | 同一帧，更正面一点 | 脸、头发、围巾、护符、腐化的手臂 |
| `refs/3_varus_league_head.png` | 头和肩的特写 | 后梳的头发、红宝石头带、脸、红围巾、护符 |
| `refs/4_varus_league_side.png` | 同一帧的侧面 | 扎起的头发、围巾尾巴、弓的厚度 |
| `refs/5_varus_splash.png` | 官方加载画面 | **看气氛** |
| `refs/6_varus_league_cast.png` | 英雄联盟 Q 蓄力那一帧 | B 的姿势（拉弓、弓张开） |
| `refs/7_varus_league_attack.png` | 英雄联盟平A第一帧 | 弓端平时的样子 |
| `style/8_style_jhin.png` | 你之前的烬像素图 | **只看风格**（远程英雄） |
| `style/9_style_kayn.png` | 你之前的凯隐像素图 | **只看风格**（深紫色的腐化战士） |
| `style/10_style_twistedfate.png` | 你之前的崔斯特像素图 | **只看风格**（最近通过的一张） |

## 提示词 A：`varus-model-A.png`（英雄联盟待机：左手提弓垂在腿边）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the face, the hair, the scarf, the medallion, the corrupted arms; 3 the head and shoulders close-up: the swept-back hair, the headband with the red gem, the face, the red scarf, the medallion; 4 the same pose in profile: the tied hair, the scarf tail, the bow; 5 the official illustration, for the mood; 6 League's Piercing Arrow charge, the pose of version B; 7 League's basic attack, the bow held level). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a ranged hero, image 9 a dark-purple corrupted fighter, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hair to the soles, centred, comfortable transparent margins, nothing cut off (the whole bow inside the picture).
The character: Varus, the Arrow of Retribution: a lean, tall, athletic male archer, half corrupted by a dark purple living bow. HEAD: SILVER-WHITE hair with pale blue shading, swept straight back from the forehead and tied at the back of the head; a thin dark headband across the forehead with a small RED gem in its middle; a narrow pale face, sharp cheekbones, a stern brooding look, dark eyes under heavy brows. NECK: a bright RED SCARF wrapped round the neck, its long red tail hanging down his back to below the hips. TORSO: bare pale grey-white skin, a lean muscled chest, a thin teal tattoo on his right shoulder; a dark brown-grey leather HARNESS strap across the chest holding a big round MEDALLION on his chest - a gold rim round a dark teal glass disc; a thin cord necklace with a small red diamond pendant. CORRUPTION: from the elbows down both forearms and hands turn DARK CRIMSON then PURPLE, the hands clawed, the fingertips glowing VIOLET; the belly and hips fade into the same dark crimson. LEGS: tight dark PURPLE-BLACK armoured leggings with plate segments, small spikes at the hips and knees and tiny glowing violet dots; heavy dark purple boots; short dark red cloth strips hanging from the belt. BOW: a huge dark PURPLE-BLACK LIVING Darkin bow, almost as tall as his torso and legs, made of curved spiked plates like claws and bone, glowing VIOLET veins and a bright violet glow at the grip, held in his LEFT hand (the hand on the image-right side).
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height), a lean athletic body, legs a little shorter; the medallion, the red scarf, the glowing hands and the bow drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes visible, nothing covers the face.
Pose: League's own idle (image 1): standing upright in 3/4 view facing image right, feet a little apart, shoulders slightly hunched, brooding; the right arm hanging at his side, the clawed hand relaxed; the left arm lowered and holding the big bow by its grip beside his left leg, the bow hanging down vertical with its spiked tips pointing up and down; the red scarf tail hanging behind him; the head turned toward the viewer. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The leggings, boots and the bow are PURPLE-BLACK in the game: draw them in dark purple and plum shades with violet lit edges and highlights (never one flat black mass - black is only the outline), so their plates and spikes read; the skin pale grey-white with cool shadows, the hair silver-white with pale blue shades, the scarf a strong red, the medallion gold with a teal centre, the glow on the hands and the bow bright violet; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects beyond the glow drawn on the bow and hands (and the nocked arrow in version B), no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`varus-model-B.png`（英雄联盟 Q 蓄力：举弓拉弦，搭一支紫光箭）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the face, the hair, the scarf, the medallion, the corrupted arms; 3 the head and shoulders close-up: the swept-back hair, the headband with the red gem, the face, the red scarf, the medallion; 4 the same pose in profile: the tied hair, the scarf tail, the bow; 5 the official illustration, for the mood; 6 League's Piercing Arrow charge, the pose of version B; 7 League's basic attack, the bow held level). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style (image 8 a ranged hero, image 9 a dark-purple corrupted fighter, image 10 the latest approved picture of this series).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hair to the soles, centred, comfortable transparent margins, nothing cut off (the whole bow inside the picture).
The character: Varus, the Arrow of Retribution: a lean, tall, athletic male archer, half corrupted by a dark purple living bow. HEAD: SILVER-WHITE hair with pale blue shading, swept straight back from the forehead and tied at the back of the head; a thin dark headband across the forehead with a small RED gem in its middle; a narrow pale face, sharp cheekbones, a stern brooding look, dark eyes under heavy brows. NECK: a bright RED SCARF wrapped round the neck, its long red tail hanging down his back to below the hips. TORSO: bare pale grey-white skin, a lean muscled chest, a thin teal tattoo on his right shoulder; a dark brown-grey leather HARNESS strap across the chest holding a big round MEDALLION on his chest - a gold rim round a dark teal glass disc; a thin cord necklace with a small red diamond pendant. CORRUPTION: from the elbows down both forearms and hands turn DARK CRIMSON then PURPLE, the hands clawed, the fingertips glowing VIOLET; the belly and hips fade into the same dark crimson. LEGS: tight dark PURPLE-BLACK armoured leggings with plate segments, small spikes at the hips and knees and tiny glowing violet dots; heavy dark purple boots; short dark red cloth strips hanging from the belt. BOW: a huge dark PURPLE-BLACK LIVING Darkin bow, almost as tall as his torso and legs, made of curved spiked plates like claws and bone, glowing VIOLET veins and a bright violet glow at the grip, held in his LEFT hand (the hand on the image-right side).
Proportions: game-sprite proportions like images 8-10 - a bigger head than in the 3D model (about a third of his height), a lean athletic body, legs a little shorter; the medallion, the red scarf, the glowing hands and the bow drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: both eyes visible, nothing covers the face.
Pose: League's Piercing Arrow charge (image 6): standing in a wide steady archer's stance in 3/4 view facing image right, both feet on the ground; the left arm stretched forward holding the bow up in front of him, the bow opened wide like spread claws; the right hand drawn back beside his face pulling the string, a long glowing VIOLET-PINK arrow nocked and pointing to the image right; the red scarf tail swinging behind him; the head turned toward the viewer, eyes narrowed on the target. The soles are the lowest thing in the picture, flat on one ground line (the game draws the health bar under them).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The leggings, boots and the bow are PURPLE-BLACK in the game: draw them in dark purple and plum shades with violet lit edges and highlights (never one flat black mass - black is only the outline), so their plates and spikes read; the skin pale grey-white with cool shadows, the hair silver-white with pale blue shades, the scarf a strong red, the medallion gold with a teal centre, the glow on the hands and the bow bright violet; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects beyond the glow drawn on the bow and hands (and the nocked arrow in version B), no aura, no particles, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物和整把弓都完整。
- 银白后梳头发、红宝石头带；两只眼睛看得见；鲜红围巾和背后的红布尾巴。
- 胸前金边青色圆护符和斜挎皮带；小臂到手是暗红到紫色的爪子，指尖紫光。
- 深紫黑甲裤和靴子有紫色亮边；巨大的紫黑活体弓在左手（画面右边），有紫光纹路。
- 鞋底是最低点，落在一条水平线上；没有多余特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/varus-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
