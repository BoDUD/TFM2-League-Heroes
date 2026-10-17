# 丽桑卓：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 丽桑卓还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（笔直站着、一动不动，两只手臂垂在身体两侧）；**B = 英雄联盟 Q（寒冰碎片）的起手**（两臂向两侧张开到肩高、手指张开像爪子，手里还没有法术）。你挑一版，之后第 1 步再按它画游戏尺寸的精灵（约 40 行，连冠冕）。
> - **长相照英雄联盟原版**（附图 1–6）：头上是一顶**深蓝黑色的冰冠头盔**，形状像一块又宽又平的尖菱形（两边各伸出一个尖角，往后的那一边更长），边缘是钢蓝色；**冠的前面垂下来盖住眼睛，英雄联盟里她的眼睛是被遮住的**（不画眼睛）。脸只露出下半张：**淡冰蓝色的皮肤**、小鼻子、**深蓝色嘴唇**、冷冷的表情，脸周围是一圈深色带棱的兜帽领。
> - **头发**：一条**很长很粗的冰蓝色辫子**从冠后面出来，垂在身后一直到膝盖。
> - **身体和衣服**：手臂和手是淡冰蓝色皮肤，**小臂和细长带尖的手指发出更亮的青色光**、有细细的冰纹；肩上是**尖尖的冰蓝水晶护肩**（亮青色、向上向外刺）；上身是贴身的深蓝黑胸甲，有凸起的钢蓝色棱线，胸口是一个**深 V 领口、露出淡冰蓝色的皮肤**；腰以下是一条**拖到地上的深蓝黑长裙**，褶子是钢蓝色，**裙摆底部碎成一圈锯齿状的深色冰晶尖**。**她没有腿和脚**：长裙一圈都拖到地面，英雄联盟里她是滑着走的。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的乐芙兰、娑娜、伊芙琳）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；头比英雄联盟模型大一些（连冠冕约占身高三分之一），身材修长、长裙；冠冕、水晶护肩和发光的手画大一点，小尺寸下才看得出来。冠冕、胸甲、长裙在游戏里是深蓝黑色的，要用**深蓝、靛蓝的几档颜色加钢蓝亮边和高光**画出褶子和棱线，不要糊成一整块黑。
> - 不画任何特效（冰锥、冰环、光环第 3 步再单独画）；裙摆是最低点，平平地落在一条地面线上（游戏在脚下画血条）。
> - 交付：`outputs/lissandra-picture/lissandra-model-A.png`、`outputs/lissandra-picture/lissandra-model-B.png`（都是 1024×1536 竖版、真透明背景，人物从冠顶到裙摆约 1250 px）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_lissandra_league_front.png` | 英雄联盟原版丽桑卓，待机第一帧，3/4 朝右 | 服装、颜色、A 的姿势 |
| `refs/2_lissandra_league_frontal.png` | 同一帧，更正面一点 | 冠冕、遮眼的面罩、脸、胸口 |
| `refs/3_lissandra_league_head.png` | 头和肩的特写 | 冠冕的形状、面罩、蓝色嘴唇、兜帽领、水晶护肩 |
| `refs/4_lissandra_league_side.png` | 同一帧的侧面 | 冠冕往后伸的长尖角、辫子 |
| `refs/5_lissandra_splash.png` | 官方加载画面 | **看气氛** |
| `refs/6_lissandra_league_cast.png` | 英雄联盟 Q 起手那一帧 | B 的姿势（双臂张开） |
| `style/7_style_leblanc.png` | 你之前的乐芙兰像素图 | **只看风格**（深色长袍的法师） |
| `style/8_style_sona.png` | 你之前的娑娜像素图 | **只看风格**（拖到地上的长裙） |
| `style/9_style_evelynn.png` | 你之前的伊芙琳像素图 | **只看风格**（深色衣服配发光的点缀） |

## 提示词 A：`lissandra-model-A.png`（英雄联盟待机：笔直站着，两臂垂在身侧）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the crown, the mask over the eyes, the face, the chest; 3 the head and shoulders close-up: the crown-helm, the mask, the lips, the hood-collar, the crystal shoulder spikes; 4 the same pose in profile: the crown's long back point and the braid; 5 the official illustration, for the mood; 6 League's Ice Shard wind-up, the pose of version B). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 7 a mage in a long dark gown, image 8 a long dress down to the ground, image 9 a dark costume with glowing accents).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the crown to the gown's hem, centred, comfortable transparent margins, nothing cut off (both points of the crown inside the picture).
The character: Lissandra, the Ice Witch: an ancient, tall, slender and regal sorceress of ice. CROWN: a large dark navy-black ice CROWN-HELM shaped like a wide flat pointed diamond (a broad brim reaching out to a sharp point on each side, longer toward the back), with steel-blue edges; at its front it comes down as a smooth MASK over her eyes - in League her eyes are hidden by it. FACE: only the lower face shows under the mask: pale ice-blue skin, a small nose, dark blue lips, a calm cold expression; a tall dark ridged hood-collar rises behind and around the face. HAIR: one very long thick BRAID of pale ICE-BLUE / cyan hair coming out from under the crown at the back and hanging down behind her to her knees. BODY: pale ICE-BLUE skin on the arms and hands, the forearms and long clawed fingers glowing brighter cyan with thin frost veins. ARMOUR AND GOWN: sharp ICE-BLUE CRYSTAL shoulder spikes (bright cyan, pointing up and out); a fitted dark navy-black bodice with raised steel-blue ridges and a deep V-shaped neckline showing pale ice-blue skin; one long flowing dark navy-black GOWN from the waist to the ground with flowing steel-blue folds, its hem breaking into jagged dark ICE-CRYSTAL points at the bottom. She has NO visible legs or feet: the gown reaches the ground all round and she glides on it.
Proportions: game-sprite proportions like images 7-9 - a bigger head than in the 3D model (the head with the crown about a third of her height), a slim upright body, the gown long; the crown, the shoulder spikes and the glowing hands drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the mask covers the eyes as in League (no eyes drawn), the lower face - pale blue skin and dark blue lips - clearly visible below it; nothing else covers the face.
Pose: League's own idle (image 1): standing perfectly upright and still in 3/4 view facing image right, regal and cold; both arms hanging close to her sides, the long glowing hands relaxed beside the gown, fingers pointing down; the braid hanging straight down behind her; the gown falling straight to the ground, widening a little at the hem; the head turned toward the viewer under the crown. The gown's hem is the lowest thing in the picture, flat on one ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The crown, the bodice and the gown are NAVY-BLACK in the game: draw them in dark navy and indigo shades with steel-blue lit edges and highlights (never one flat black mass - black is only the outline), so their folds and ridges read; the skin pale ice blue, the hands and forearms a brighter glowing cyan, the braid pale cyan-white with darker blue braid lines, the shoulder crystals bright cyan with white glints; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no ice shards in the air, no aura, no snow, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`lissandra-model-B.png`（英雄联盟 Q 的起手：两臂向两侧张开，手指张开）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right: League's idle, the pose of version A; 2 the same pose seen more from the front: the crown, the mask over the eyes, the face, the chest; 3 the head and shoulders close-up: the crown-helm, the mask, the lips, the hood-collar, the crystal shoulder spikes; 4 the same pose in profile: the crown's long back point and the braid; 5 the official illustration, for the mood; 6 League's Ice Shard wind-up, the pose of version B). Copy from them the costume, the colours and the shapes - NOT their 3D shading. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style (image 7 a mage in a long dark gown, image 8 a long dress down to the ground, image 9 a dark costume with glowing accents).
Create ONE full-body pixel-art picture of this character, a 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the crown to the gown's hem, centred, comfortable transparent margins, nothing cut off (both points of the crown inside the picture).
The character: Lissandra, the Ice Witch: an ancient, tall, slender and regal sorceress of ice. CROWN: a large dark navy-black ice CROWN-HELM shaped like a wide flat pointed diamond (a broad brim reaching out to a sharp point on each side, longer toward the back), with steel-blue edges; at its front it comes down as a smooth MASK over her eyes - in League her eyes are hidden by it. FACE: only the lower face shows under the mask: pale ice-blue skin, a small nose, dark blue lips, a calm cold expression; a tall dark ridged hood-collar rises behind and around the face. HAIR: one very long thick BRAID of pale ICE-BLUE / cyan hair coming out from under the crown at the back and hanging down behind her to her knees. BODY: pale ICE-BLUE skin on the arms and hands, the forearms and long clawed fingers glowing brighter cyan with thin frost veins. ARMOUR AND GOWN: sharp ICE-BLUE CRYSTAL shoulder spikes (bright cyan, pointing up and out); a fitted dark navy-black bodice with raised steel-blue ridges and a deep V-shaped neckline showing pale ice-blue skin; one long flowing dark navy-black GOWN from the waist to the ground with flowing steel-blue folds, its hem breaking into jagged dark ICE-CRYSTAL points at the bottom. She has NO visible legs or feet: the gown reaches the ground all round and she glides on it.
Proportions: game-sprite proportions like images 7-9 - a bigger head than in the 3D model (the head with the crown about a third of her height), a slim upright body, the gown long; the crown, the shoulder spikes and the glowing hands drawn a little oversized so they read at small size. 3/4 FRONT view facing image right, the face turned toward the viewer: the mask covers the eyes as in League (no eyes drawn), the lower face - pale blue skin and dark blue lips - clearly visible below it; nothing else covers the face.
Pose: League's Ice Shard wind-up (image 6): standing upright in 3/4 view facing image right, both arms spread out to the sides at shoulder height, elbows a little bent, the long glowing hands open with the fingers spread like claws (no magic in them yet); the braid swinging a little behind her; the gown falling to the ground; the head turned toward the viewer under the crown, chin up. The gown's hem is the lowest thing in the picture, flat on one ground line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades. The crown, the bodice and the gown are NAVY-BLACK in the game: draw them in dark navy and indigo shades with steel-blue lit edges and highlights (never one flat black mass - black is only the outline), so their folds and ridges read; the skin pale ice blue, the hands and forearms a brighter glowing cyan, the braid pale cyan-white with darker blue braid lines, the shoulder crystals bright cyan with white glints; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No magic effects, no ice shards in the air, no aura, no snow, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，冠冕两边的尖角没被切掉。
- 深蓝黑的尖菱形冰冠，前面的面罩盖住眼睛；下半张脸（淡蓝皮肤、深蓝嘴唇）清楚可见。
- 冰蓝长辫垂到膝盖；亮青色水晶护肩；胸口深 V 领口露出淡蓝皮肤；小臂和手发青光。
- 长裙拖地、裙摆一圈冰晶尖，没有腿和脚；裙摆是最低点，落在一条水平线上。
- 深色部分有钢蓝亮边和褶子，没有糊成一块黑；没有冰锥、光环、雪花等特效。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/lissandra-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。
