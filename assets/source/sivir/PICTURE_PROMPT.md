# 希维尔：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 用户选了「Codex 重画」，按包里的流程先画原图。A、B 两版只差姿势：**A = 英雄联盟的待机**（压低重心的宽站姿蹲伏，前手张开向前探，后手把十字刃低低地拿在身后胯边）；**B = 直立站姿**（站得高、放松，重心在后腿，十字刃拿在身后胯边，前手叉腰或自然垂下）。两版的十字刃都画成**展开的四刃十字、正面朝外**（附图 4），这样缩到游戏尺寸还认得出来。你挑一版，第 1 步再按它画游戏尺寸的精灵。
> - **长相照英雄联盟原版**（附图 1–3、6）：**黑色长直发**披过肩膀垂到背后，额前几缕碎发；额头一顶**金色头冠**，中间尖起、镶一颗**青绿色宝石**；暖棕色皮肤；脖子围一条**米白色围巾**。
> - **衣服**：**深青蓝色短上衣**（金边），露出腰腹；**远侧肩上一个大金肩甲**（镶青色宝石）；上臂深色缠布，前臂**金色护臂**加深色皮手套；**金腰带**，圆形**青色宝石扣**；前面垂一块到膝盖的**深青蓝色腰布**（金边，下端一颗小青宝石），两侧金色胯甲；**深紫灰色缠绑长筒护腿**，**金色护膝**（小青宝石），深棕色金边铠甲靴。
> - **十字刃「恰丽喀尔」是她的标志道具，必须画清楚**：一把华丽的**金色四刃回旋十字刃**——四片宽大的弯刃呈十字，每片末端带钩，围着中间一个**圆环**，刃和圆环相接处镶**青绿色宝石**，刃口是发亮的浅金色；**展开、正面朝外**，大小约等于她的头加身体（以后每个动作都要看得到它）。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的乐芙兰、娑娜、凯特琳）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（头加头发约占身高 28–30%），身材苗条健美。金色（头冠、肩甲、护臂、腰带、护膝、整把十字刃）要亮，青色宝石要亮，米白围巾是浅色。深色都用有颜色的深色（上衣和腰布深海军蓝、护腿深紫灰、靴子深棕、头发深蓝黑），黑色只用在描边。
> - 不画旋转拖尾、法术护盾、光晕等任何特效（特效第 3 步再单独画）；脚底是最低点，十字刃、腰布和头发都不能低于脚底线（游戏在脚下画血条）。
> - 交付：`outputs/sivir-model-A.png`、`outputs/sivir-model-B.png`（1024×1536，真透明背景，人物约 1150 px 高），附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sivir_league_front.png` | 英雄联盟原版希维尔，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 |
| `refs/2_sivir_league_side.png` | 同一帧，更侧一点 | 蹲伏的腿、前手、肩甲和护臂 |
| `refs/3_sivir_league_head.png` | 头部特写 | 黑长发、金头冠和青宝石、米白围巾 |
| `refs/4_sivir_league_back.png` | 背面：十字刃展开背在身后，正面朝外 | **十字刃的形状**（四片带钩弯刃、中间圆环、青宝石） |
| `refs/5_sivir_league_blade_open.png` | 大招时十字刃展开旋转 | 十字刃展开的样子 |
| `refs/6_sivir_splash.png` | 官方加载画面 | 服装（上衣、腰布、围巾）和气质 |
| `style/7_style_leblanc.png` | 你之前的乐芙兰像素图 | **只看风格**（金色镶边、布料的画法） |
| `style/8_style_sona.png` | 你之前的娑娜像素图 | **只看风格**（金色配青蓝色） |
| `style/9_style_caitlyn.png` | 你之前的凯特琳像素图 | **只看风格**（女射手拿大武器） |

## 提示词 A：`sivir-model-A.png`（英雄联盟待机：低重心蹲伏，前手前探，十字刃展开拿在身后胯边）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure 3/4 front in her idle crouch; 2 the same pose seen more from the side; 3 the head close-up: the tiara, the gem, the hair and the scarf; 4 a back view: the crossblade OPEN on her back, face-on - copy its shape; 5 the crossblade open and spinning; 6 the official illustration, for the outfit and the mood). Copy from them the costume, the colours and the crossblade - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 9 also shows a woman holding a big weapon).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the highest point to the soles, centred, comfortable transparent margins.
The character: Sivir, the Battle Mistress: a confident, athletic desert mercenary warrior woman. HEAD: long straight BLACK hair falling past her shoulders down her back, a few locks framing her face; a GOLD TIARA (diadem) on her forehead with a pointed peak and a TEAL-GREEN gem in its centre; warm tan skin; a calm, determined face. A CREAM-WHITE SCARF wrapped round her neck. OUTFIT: a dark TEAL-NAVY crop top edged with gold trim, a bare toned midriff; one big GOLD PAULDRON with a TEAL gem on her far shoulder; dark wrapped sleeves on the upper arms, GOLD vambraces and dark leather gloves; a gold belt with a round TEAL gem buckle, a long dark TEAL-NAVY loincloth panel hanging in front down to the knees (gold edges, a small teal gem at its tip), gold hip plates at both sides; dark SLATE-PURPLE wrapped thigh-high leggings, GOLD knee guards with a small teal gem, dark brown armoured boots with gold trim. WEAPON (her signature prop, it must read clearly): the CHALICAR, a big ornate GOLD four-bladed throwing crossblade - four wide curved blades in a cross, each with a hooked tip, round a central RING, TEAL-GREEN gems where the blades meet the ring, the blade edges a pale glowing gold; drawn OPEN and FACE-ON (all four blades and the ring visible, like image 4), about as tall as her head and torso together.
Proportions: game-sprite proportions like images 7 and 8 - a bigger head than in the 3D model (the head with its hair about 28-30% of her height), a slim athletic figure, the crossblade a little oversized so it reads at small size. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible, level and the same size, nothing covering the face (the crossblade stays beside or behind the body, never in front of the face).
Pose: League's own idle (images 1 and 2): a low, wide fighting crouch, body in 3/4 view facing image right, knees bent, feet apart; her FRONT (far) hand reaching forward, fingers spread like claws; her BACK (near) hand holding the open crossblade low behind her hip, the four blades face-on to the viewer; her face turned toward the viewer. The soles are the lowest thing in the picture: the crossblade, the loincloth and the hair end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep navy for the top and the loincloth, dark plum-slate for the leggings, dark brown for the boots, dark bronze for the gold, a dark blue-black for the hair - never black fill, black is only the outline); lit edges and bright highlights: bright gold on the tiara, the pauldron, the vambraces, the belt, the knee guards and the whole crossblade, small bright teal gems, the cream scarf light; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spinning trails, no magic shield, no glow, no effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`sivir-model-B.png`（直立站姿：重心在后腿，十字刃展开拿在身后胯边）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure 3/4 front in her idle crouch; 2 the same pose seen more from the side; 3 the head close-up: the tiara, the gem, the hair and the scarf; 4 a back view: the crossblade OPEN on her back, face-on - copy its shape; 5 the crossblade open and spinning; 6 the official illustration, for the outfit and the mood). Copy from them the costume, the colours and the crossblade - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 9 also shows a woman holding a big weapon).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the highest point to the soles, centred, comfortable transparent margins.
The character: Sivir, the Battle Mistress: a confident, athletic desert mercenary warrior woman. HEAD: long straight BLACK hair falling past her shoulders down her back, a few locks framing her face; a GOLD TIARA (diadem) on her forehead with a pointed peak and a TEAL-GREEN gem in its centre; warm tan skin; a calm, determined face. A CREAM-WHITE SCARF wrapped round her neck. OUTFIT: a dark TEAL-NAVY crop top edged with gold trim, a bare toned midriff; one big GOLD PAULDRON with a TEAL gem on her far shoulder; dark wrapped sleeves on the upper arms, GOLD vambraces and dark leather gloves; a gold belt with a round TEAL gem buckle, a long dark TEAL-NAVY loincloth panel hanging in front down to the knees (gold edges, a small teal gem at its tip), gold hip plates at both sides; dark SLATE-PURPLE wrapped thigh-high leggings, GOLD knee guards with a small teal gem, dark brown armoured boots with gold trim. WEAPON (her signature prop, it must read clearly): the CHALICAR, a big ornate GOLD four-bladed throwing crossblade - four wide curved blades in a cross, each with a hooked tip, round a central RING, TEAL-GREEN gems where the blades meet the ring, the blade edges a pale glowing gold; drawn OPEN and FACE-ON (all four blades and the ring visible, like image 4), about as tall as her head and torso together.
Proportions: game-sprite proportions like images 7 and 8 - a bigger head than in the 3D model (the head with its hair about 28-30% of her height), a slim athletic figure, the crossblade a little oversized so it reads at small size. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible, level and the same size, nothing covering the face (the crossblade stays beside or behind the body, never in front of the face).
Pose: an upright stance: she stands tall and relaxed, body in 3/4 view facing image right, weight on the back leg, the front foot a step ahead; her BACK (near) hand holds the open crossblade at her back hip, face-on, its lower blade ending well above the soles; her FRONT (far) hand rests on her hip or hangs loosely; her face turned toward the viewer. The soles are the lowest thing in the picture: the crossblade, the loincloth and the hair end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep navy for the top and the loincloth, dark plum-slate for the leggings, dark brown for the boots, dark bronze for the gold, a dark blue-black for the hair - never black fill, black is only the outline); lit edges and bright highlights: bright gold on the tiara, the pauldron, the vambraces, the belt, the knee guards and the whole crossblade, small bright teal gems, the cream scarf light; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spinning trails, no magic shield, no glow, no effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，十字刃四片刃都没被切掉。
- 两只眼睛都看得见、同一高度、一样大；脸没被十字刃或手挡住；黑长发、金头冠和青宝石、米白围巾都有。
- 十字刃是展开的四刃十字、正面朝外，中间圆环和青宝石清楚；金色明亮，不是一团暗褐色。
- 脚底是最低点，十字刃、腰布、头发都不低于它；没有拖尾、光晕、护盾。
- 大像素块清楚，没有糊、没有柔光、没有渐变；深色部分有颜色（不是一片纯黑）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
