# 瑞兹：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 瑞兹还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站直，两只手稍微张开垂在身体两侧、手指张开，像随时要施法）；**B = 施法站姿**（照他放 E 时的起手：两脚分开、膝盖微弯，两条手臂向两侧张开到肩高、手掌张开，抬头看前方）。你挑一版，之后第 1 步再按它画游戏尺寸（约 40 格）的精灵。
> - **长相照英雄联盟原版**（附图 1–6）：全身是**蓝紫色皮肤**（长春花蓝 / 薰衣草蓝，暗部深紫），光头，头皮、太阳穴和手臂上有深靛色的**符文纹身线**；浓眉、皱眉的严肃脸，**一双发光的淡紫白色眼睛**，宽鼻子；**深棕色的长胡子**连着八字胡，从脸颊垂到胸口中间、下端收尖。宽肩膀，粗壮赤裸的手臂（蓝紫皮肤 + 符文线），棕色皮护腕，大手。无袖的**深海军蓝上衣**，小立领；胸前交叉的棕色皮带；一边肩膀一个大的**棕色皮肩甲**（铜铆钉、铜扣）；宽**棕色皮腰带**，中间一个**圆形大铜扣**，挂着小皮袋；腰带两侧和后面垂着短的深青色布条；很宽松的**石板蓝灯笼裤**，膝盖处收紧，前面一排小铜扣；高筒**棕色皮靴**，每个膝盖上一个**圆形大铜护膝**。
> - **背上的大卷轴是他的标志，要大要清楚**：一卷巨大的米白 / 象牙色**羊皮纸卷轴**（世界符文），装在棕色皮革 + 木头的**卷轴筒**里，有铜箍，侧面一个圆形的**蓝色符文徽章**，顶端一个深色铁帽；斜背在背上，**顶端（露出毛边的纸）高过头顶、在远侧肩膀后面**，底端在身后腰部。
> - 靴底是最低点 = 脚底线，卷轴、布条、手都不能低于它（游戏在脚下画血条）。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的萨科 A、凯南 A、乐芙兰 A）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；Q 版比例，头（不算胡子）约占身高的三分之一（凯南 A 示范了背上的大道具在这个风格里怎么画清楚）。要求亮的高光：头皮、眉骨、手臂上浅薰衣草色的高光，铜扣、护膝、铆钉的亮点，羊皮纸的浅米色边，发光的眼睛是脸上最亮的地方。
> - 交付：`outputs/ryze-model-A.png`、`outputs/ryze-model-B.png`（1024×1536，真透明背景，人物约 1250 px 高），再附一个 `generation-prompts.txt` 写明实际用的提示词，最后写 `HANDOFF.md`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ryze_league_front.png` | 英雄联盟原版瑞兹，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 |
| `refs/2_ryze_league_frontal.png` | 同一帧，几乎正面 | 上衣、皮带、铜扣、灯笼裤、护膝 |
| `refs/3_ryze_league_head.png` | 头部特写 | 光头、符文纹身、发光的眼睛、胡子 |
| `refs/4_ryze_league_side.png` | 同一帧，更侧面 | 卷轴斜背在背上的位置 |
| `refs/5_ryze_league_scroll.png` | 从背后看卷轴筒 | 卷轴、卷轴筒、铜箍、蓝色符文徽章、铁帽 |
| `refs/6_ryze_league_cast.png` | 放 E 的起手（0 秒）：两脚分开、双臂张开 | B 的姿势 |
| `refs/7_ryze_league_splash.png` | 官方加载画面 | **只看气氛、脸和发光的眼睛**，服装以 1–6 为准 |
| `style/8_style_shaco.png` | 你之前的萨科像素图（A） | **只看风格和 Q 版比例**（男性角色的脸） |
| `style/9_style_kennen.png` | 你之前的凯南像素图（A） | **只看风格、比例、背上大道具的画法** |
| `style/10_style_leblanc.png` | 你之前的乐芙兰像素图（A） | **只看风格和 Q 版比例**（法师） |

## 提示词 A：`ryze-model-A.png`（英雄联盟待机：站直，双手张开垂在身侧）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 nearly frontal; 3 the head close-up; 4 a side view; 5 the scroll case on his back, seen from behind; 6 a casting stance; 7 the official illustration, for the mood, the face and the glowing eyes only - follow 1-6 for the costume and the scroll). Copy from them the costume, the colours, the bald tattooed head, the beard and the scroll - NOT their 3D shading and NOT their adult proportions. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions (image 9 shows how a big prop carried on the back stays readable in this style).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the scroll to the soles, centred, comfortable transparent margins (the scroll, the hands and the boots must not be cut off).
The character: Ryze, the Rune Mage: a tough, battle-worn wandering wizard who carries a huge magic scroll on his back. SKIN: BLUE-VIOLET (periwinkle / lavender blue, deep violet in the shadows) all over - head, face, bare arms - with thin darker indigo RUNE TATTOO lines on his bald scalp, on his temples and down his arms. HEAD: completely BALD, a strong heavy brow, a stern frowning face, two GLOWING pale violet-white EYES, a broad nose; a long full dark BROWN BEARD with a moustache, from his cheeks down to the middle of his chest, ending in a point. BODY: broad shoulders, thick bare muscular arms (blue-violet skin, rune lines) with brown leather WRIST BRACERS, big strong hands. CLOTHES: a sleeveless dark NAVY-SLATE BLUE tunic with a small stand-up collar; brown leather STRAPS crossing his chest; one big brown leather SHOULDER PAULDRON with bronze rivets and a bronze stud (on the shoulder shown in image 1); a wide brown leather BELT with a big round BRONZE BUCKLE disc and small pouches; short dark-teal cloth strips hanging from the belt at his sides and back; very baggy dark SLATE-BLUE TROUSERS gathered at the knees with a row of small bronze toggle buttons down the front; tall brown leather BOOTS with a big round BRONZE KNEE GUARD on each knee. THE SCROLL (his signature - keep it big and clear in every pose): a huge rolled-up cream / ivory PARCHMENT SCROLL (the World Runes) carried on his back in a brown leather and wood SCROLL CASE with bronze bands, a round blue RUNE MEDALLION on its side and a dark iron cap on its top end; it stands slanted on his back, its top end with the frayed parchment edge rising ABOVE his head behind his far shoulder, its bottom end at his hips behind him.
Proportions: chibi like images 8, 9 and 10 - the head (crown to the chin, without the beard) about one third of the height from the crown to the soles, big clear glowing eyes, a sturdy broad body, strong hands; the scroll oversized and clear. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible and level, the beard below the mouth never covering the eyes, the chest and the belt buckle visible (never show his back).
Pose: League's own idle (images 1 and 2): he stands upright and steady, feet a little apart, weight even; both arms hang down a little away from his sides, elbows slightly bent, the big hands open with the fingers spread like a mage ready to cast; the head turned toward image right with both glowing eyes visible; the scroll on his back, its top end rising above his head behind his far shoulder (image left), the case showing on both sides of his body; the soles of the boots are the lowest thing in the picture. Nothing hangs below the soles: the scroll, the belt strips and the hands end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (blue-violet skin, brown beard, navy tunic, slate-blue trousers, brown leather, bronze, cream parchment) - coloured darks, never black fill (black is only the outline); bright highlights: light-lavender highlights on the scalp, the brow and the arms, glints on the bronze buckle, knee guards and rivets, the parchment's light cream edge, the glowing eyes the brightest spot of the face; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no magic effects, no runes floating in the air, no text, no frame, no other characters.
```

## 提示词 B：`ryze-model-B.png`（施法站姿：两脚分开，双臂向两侧张开）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 nearly frontal; 3 the head close-up; 4 a side view; 5 the scroll case on his back, seen from behind; 6 a casting stance; 7 the official illustration, for the mood, the face and the glowing eyes only - follow 1-6 for the costume and the scroll). Copy from them the costume, the colours, the bald tattooed head, the beard and the scroll - NOT their 3D shading and NOT their adult proportions. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions (image 9 shows how a big prop carried on the back stays readable in this style).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the scroll to the soles, centred, comfortable transparent margins (the scroll, the hands and the boots must not be cut off).
The character: Ryze, the Rune Mage: a tough, battle-worn wandering wizard who carries a huge magic scroll on his back. SKIN: BLUE-VIOLET (periwinkle / lavender blue, deep violet in the shadows) all over - head, face, bare arms - with thin darker indigo RUNE TATTOO lines on his bald scalp, on his temples and down his arms. HEAD: completely BALD, a strong heavy brow, a stern frowning face, two GLOWING pale violet-white EYES, a broad nose; a long full dark BROWN BEARD with a moustache, from his cheeks down to the middle of his chest, ending in a point. BODY: broad shoulders, thick bare muscular arms (blue-violet skin, rune lines) with brown leather WRIST BRACERS, big strong hands. CLOTHES: a sleeveless dark NAVY-SLATE BLUE tunic with a small stand-up collar; brown leather STRAPS crossing his chest; one big brown leather SHOULDER PAULDRON with bronze rivets and a bronze stud (on the shoulder shown in image 1); a wide brown leather BELT with a big round BRONZE BUCKLE disc and small pouches; short dark-teal cloth strips hanging from the belt at his sides and back; very baggy dark SLATE-BLUE TROUSERS gathered at the knees with a row of small bronze toggle buttons down the front; tall brown leather BOOTS with a big round BRONZE KNEE GUARD on each knee. THE SCROLL (his signature - keep it big and clear in every pose): a huge rolled-up cream / ivory PARCHMENT SCROLL (the World Runes) carried on his back in a brown leather and wood SCROLL CASE with bronze bands, a round blue RUNE MEDALLION on its side and a dark iron cap on its top end; it stands slanted on his back, its top end with the frayed parchment edge rising ABOVE his head behind his far shoulder, its bottom end at his hips behind him.
Proportions: chibi like images 8, 9 and 10 - the head (crown to the chin, without the beard) about one third of the height from the crown to the soles, big clear glowing eyes, a sturdy broad body, strong hands; the scroll oversized and clear. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible and level, the beard below the mouth never covering the eyes, the chest and the belt buckle visible (never show his back).
Pose: a casting stance like his spells (image 6): feet wide apart, knees bent, a solid low stance; both arms spread out to the sides at shoulder height, the hands open with the fingers spread and the palms forward (no effects in the hands); his head up, looking ahead toward image right with both glowing eyes visible; the scroll on his back, its top end above his far shoulder; keep the pose compact: the hands no wider than about one head beyond the shoulders on each side; the soles of the boots are the lowest thing in the picture. Nothing hangs below the soles: the scroll, the belt strips and the hands end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (blue-violet skin, brown beard, navy tunic, slate-blue trousers, brown leather, bronze, cream parchment) - coloured darks, never black fill (black is only the outline); bright highlights: light-lavender highlights on the scalp, the brow and the arms, glints on the bronze buckle, knee guards and rivets, the parchment's light cream edge, the glowing eyes the brightest spot of the face; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no magic effects, no runes floating in the air, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，卷轴顶端、双手、靴子都没被切掉。
- 两只发光的眼睛都在、同一高度、看得清；胡子在嘴下面，没挡住眼睛；皮肤是蓝紫色，头是光头、有符文纹身线。
- 卷轴完整：米白羊皮纸 + 棕色卷轴筒 + 铜箍 + 蓝色符文徽章 + 铁帽，斜背在背上，顶端高过头顶。
- 靴底是最低点，卷轴、布条、手都不低于它。
- 大像素块清楚，没有糊、没有柔光、没有渐变、没有魔法特效。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
