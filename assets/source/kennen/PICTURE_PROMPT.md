# 凯南：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 凯南还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站直、微屈膝的忍者架势，两只爪手举在胸前，大金色手里剑斜背在背上，两个尖角从头后和远侧肩膀后面露出来）；**B = 准备投掷**（微蹲，远侧手把大手里剑高举在头旁边，近侧爪手放低在肚子前）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（凯南是约德尔人，会画得比大人英雄小，和小炮、提莫差不多）。
> - **长相照英雄联盟原版**（附图 1–5）：整个头包在一顶圆圆的**紫色忍者兜帽**里，帽顶立着两只尖尖的**耳朵**（帽子里面是他的约德尔耳朵），耳根有深紫色的十字缝线；帽子上和脸周围是**金色闪电折线**镶边。脸上只露出眼睛：一条暖肤色的眼带，两只**又大又亮的蓝眼睛**，粗粗的深棕色眉毛往鼻梁方向压低（机灵又自信）；鼻子、嘴、下巴被**紫色面罩**盖住，面罩上沿一道金色折线。
> - **衣服**：宽袖紫色忍者袍，前襟和下摆是金色闪电折线；腰间深紫色腰带，结打在背后；近侧肩膀一块深紫肩甲，上面是**金色闪电标志**；深紫护腕；深紫灰色的**爪子手套**（每只手三根弯爪，手背一小块钢蓝色护片）；很短的腿缠着深紫绑带、脚踝系带，尖头的深紫色忍者鞋。
> - **手里剑**：一枚巨大的**四角金色手里剑**，差不多和兜帽一样宽，金铜色、刻着闪电花纹，中间一个圆孔——他的标志道具，A 版要背在背上也能清楚看到（以后每个动作都要看得见）。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的菲兹、乐芙兰、萨科）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；保持约德尔人的比例（兜帽头约占身高 40%、小身体、短腿，像菲兹那样）。紫色衣服要有亮边和高光（帽子和肩膀的淡紫高光、所有金色折线和手里剑的亮金），蓝眼睛是脸上最亮的点。
> - 不画闪电、电光和任何特效（特效第 3 步再单独画）；脚底是最低点，袍子下摆和手里剑都不能低于脚底线（游戏在脚下画血条）。
> - 交付：`outputs/kennen-model-A.png`、`outputs/kennen-model-B.png`（1024×1536，真透明背景，人物约 1150 px 高），附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_kennen_league_front.png` | 英雄联盟原版凯南，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 |
| `refs/2_kennen_league_side.png` | 同一帧，更侧一点 | 背上的手里剑怎么露出来、肩甲的闪电标志 |
| `refs/3_kennen_league_head.png` | 头部特写 | 兜帽、帽顶的耳朵、金色镶边、蓝眼睛和眉毛、面罩 |
| `refs/4_kennen_league_back.png` | 背面 | 背上的手里剑和背带、帽子的耳朵、腰带结 |
| `refs/5_kennen_league_throw.png` | 准备投掷：手里剑举在头旁边 | B 的姿势、手里剑的样子 |
| `refs/6_kennen_splash.png` | 官方加载画面 | **只看气氛**（原画里眼睛发光，提示词要求照模型画蓝眼睛） |
| `style/7_style_fizz.png` | 你之前的菲兹像素图 | **只看风格和约德尔人的比例** |
| `style/8_style_leblanc.png` | 你之前的乐芙兰像素图 | **只看风格、紫/蓝色衣服和金色镶边的画法** |
| `style/9_style_shaco.png` | 你之前的萨科像素图 | **只看风格和服装细节的画法** |

## 提示词 A：`kennen-model-A.png`（英雄联盟待机：两只爪手举在胸前，手里剑背在背上）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 the same pose seen more from the side: the shuriken strapped on his back and the shoulder emblem; 3 the head close-up; 4 a back view: the shuriken on his back, the hood's ears, the sash knot; 5 the ready-to-throw pose with the shuriken in his hand; 6 the official illustration, for the mood - it shows his eyes glowing, but use the model's BLUE eyes from images 1, 3 and 5). Copy from them the costume, the colours, the hood, the mask and the shuriken - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style; image 7 (another small yordle) also shows the proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the top of the highest point (a shuriken point or a hood ear) to the soles, centred, comfortable transparent margins.
The character: Kennen, the Heart of the Tempest: a tiny, quick yordle NINJA, small and nimble, about knee-high to a human. HEAD: a big round VIOLET-PURPLE ninja hood that covers his whole head; two short POINTED EARS stand up on top of the hood like cat ears (his yordle ears inside it), each with a small dark-purple cross-stitched strap at its base; zigzag GOLD LIGHTNING-BOLT trims run over the top of the hood and a thick gold rim frames the face opening. FACE: only his eyes show - a band of warm peach skin with two BIG BRIGHT BLUE EYES (black pupils, a white highlight, dark lashes) under thick dark-brown brows slanting down toward the nose (a determined, cheeky look); a violet cloth MASK covers his nose, mouth and chin, its top edge trimmed with a gold zigzag line and a thin darker seam down its middle. OUTFIT: a loose violet-purple ninja ROBE with wide sleeves, zigzag gold lightning trims down the front opening and along the hem; a dark-purple sash belt tied at the waist with its knot at his back; on his near shoulder a dark plum shoulder plate with a GOLD LIGHTNING-BOLT emblem; dark purple wrist wraps; dark plum-grey CLAWED GLOVES (three sharp curved claws on each hand) with a small steel-blue plate on the back of each hand; very short legs in dark purple wrappings tied at the ankle, small dark-purple ninja TABI shoes with pointed toes. SHURIKEN: a huge four-pointed THROWING STAR, about as wide as his hood, polished GOLD-BRONZE with engraved lightning swirls and a round hole in its centre - his signature prop.
Proportions: keep his own yordle proportions as in images 1 and 5 and like image 7 - a BIG hooded head (hood top to chin about 40% of his height without the shuriken and the ears), a small round body, very short legs, hands and the shuriken a little oversized. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible inside the hood opening, level and the same size, nothing covering the eyes (the hood rim frames them, the shuriken stays beside or behind the head, never in front of the face).
Pose: League's own idle (images 1 and 2): he stands upright in a light ninja ready stance, body in 3/4 view facing image right, knees slightly bent, feet a little apart; BOTH clawed hands held forward in front of his chest, claws spread, ready to throw; the huge gold SHURIKEN is strapped diagonally ON HIS BACK and must be clearly seen: two of its points stick out behind his head and his far shoulder (up and to the left of the hood, like image 2), a thin dark strap crossing his chest holds it; his eyes look toward the viewer. The soles are the lowest thing in the picture: the robe's hem and the shuriken end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep violet for the robe and the hood, plum for the gloves and shoes, never black fill - black is only the outline); lit edges and bright highlights so the purple reads: light lavender highlights on the hood and the shoulders, bright gold on every zigzag trim, on the shuriken and the shoulder emblem, the blue eyes the brightest spots of the face; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No lightning, no sparks, no electricity, no magic effects, no background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 提示词 B：`kennen-model-B.png`（准备投掷：远侧手把手里剑举在头旁边，近侧爪手放低）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 the same pose seen more from the side: the shuriken strapped on his back and the shoulder emblem; 3 the head close-up; 4 a back view: the shuriken on his back, the hood's ears, the sash knot; 5 the ready-to-throw pose with the shuriken in his hand; 6 the official illustration, for the mood - it shows his eyes glowing, but use the model's BLUE eyes from images 1, 3 and 5). Copy from them the costume, the colours, the hood, the mask and the shuriken - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style; image 7 (another small yordle) also shows the proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1150 px tall from the top of the highest point (a shuriken point or a hood ear) to the soles, centred, comfortable transparent margins.
The character: Kennen, the Heart of the Tempest: a tiny, quick yordle NINJA, small and nimble, about knee-high to a human. HEAD: a big round VIOLET-PURPLE ninja hood that covers his whole head; two short POINTED EARS stand up on top of the hood like cat ears (his yordle ears inside it), each with a small dark-purple cross-stitched strap at its base; zigzag GOLD LIGHTNING-BOLT trims run over the top of the hood and a thick gold rim frames the face opening. FACE: only his eyes show - a band of warm peach skin with two BIG BRIGHT BLUE EYES (black pupils, a white highlight, dark lashes) under thick dark-brown brows slanting down toward the nose (a determined, cheeky look); a violet cloth MASK covers his nose, mouth and chin, its top edge trimmed with a gold zigzag line and a thin darker seam down its middle. OUTFIT: a loose violet-purple ninja ROBE with wide sleeves, zigzag gold lightning trims down the front opening and along the hem; a dark-purple sash belt tied at the waist with its knot at his back; on his near shoulder a dark plum shoulder plate with a GOLD LIGHTNING-BOLT emblem; dark purple wrist wraps; dark plum-grey CLAWED GLOVES (three sharp curved claws on each hand) with a small steel-blue plate on the back of each hand; very short legs in dark purple wrappings tied at the ankle, small dark-purple ninja TABI shoes with pointed toes. SHURIKEN: a huge four-pointed THROWING STAR, about as wide as his hood, polished GOLD-BRONZE with engraved lightning swirls and a round hole in its centre - his signature prop.
Proportions: keep his own yordle proportions as in images 1 and 5 and like image 7 - a BIG hooded head (hood top to chin about 40% of his height without the shuriken and the ears), a small round body, very short legs, hands and the shuriken a little oversized. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible inside the hood opening, level and the same size, nothing covering the eyes (the hood rim frames them, the shuriken stays beside or behind the head, never in front of the face).
Pose: ready to throw (image 5): he stands in a light crouch, body in 3/4 view facing image right, feet apart; his FAR hand raises the huge gold SHURIKEN high beside his head, gripping its centre ring, the star's points clear of the face (behind and above his far shoulder, toward image right-top); his NEAR clawed hand is held low in front of his belly, claws spread; the robe flares a little; his eyes look toward the viewer, determined. The soles are the lowest thing in the picture: the robe's hem and the shuriken end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep violet for the robe and the hood, plum for the gloves and shoes, never black fill - black is only the outline); lit edges and bright highlights so the purple reads: light lavender highlights on the hood and the shoulders, bright gold on every zigzag trim, on the shuriken and the shoulder emblem, the blue eyes the brightest spots of the face; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No lightning, no sparks, no electricity, no magic effects, no background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，帽子的耳朵和手里剑的尖角都没被切掉。
- 两只蓝眼睛都在兜帽开口里、同一高度、一样大，能看清；面罩盖住鼻子和嘴；眼睛没被帽檐或手里剑挡住。
- A 版背上的手里剑看得清楚（至少两个尖角露在头后和肩膀后面）；B 版手里剑在头旁边，不挡脸。
- 手是三根爪的爪子手套，不是普通手指，也不是细黑线。
- 脚底是最低点，袍子下摆和手里剑都不低于它；没有闪电、电光、光晕。
- 大像素块清楚，没有糊、没有柔光、没有渐变，紫色衣服不是一团暗色。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
