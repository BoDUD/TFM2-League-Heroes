# 娑娜：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 娑娜还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（站在琴后面，琴平着浮在腰前，双手轻放在琴弦上弹奏，头微低）；**B = 弹奏姿势**（照她放 E 时的样子：琴斜着浮在身前，后端的弯角抬到近肩旁，前端的金色卷翼低在腰前；近手抬在高的一端，远手在低的一端拨弦，抬头看前方）。你挑一版，之后第 1 步再按它画游戏尺寸（约 40 格）的精灵。
> - **长相照英雄联盟原版**（附图 1–6）：两条很长的高双马尾，亮青蓝色，发梢是金黄色，向后上方飘；头顶扎马尾的地方一个金色发饰；侧分刘海（不挡眼睛）；温柔安静的脸、蓝绿色眼睛、小小的闭着的嘴。宝蓝色长裙：深蓝紧身上衣、金边领口（Q 版里画得简单、端庄），肩后立起一圈金边的高领，露肩，宽大飘逸的长袖、金色袖口，腰间金色腰带；裙摆向下展开拖到地面，前面和两侧垂着长长的浅青色裙片，所有裙片和下摆都镶金边、有金色卷纹；裙子盖住脚。
> - **琴（叶琴 Etwahl）是她的标志，要大要清楚**：一架浮在空中的金色雕花木琴（木纹金色 + 琥珀色），像一条浅浅的船，中间下面有一个尖的龙骨；琴面上 3–4 根细的青色琴弦，两个小木码；**前端（画面右边）向上卷成一个大的金色翅膀形卷饰**，后端（画面左边）是一根细一点的弯金角；琴上飘着两条金边的浅青色长飘带。A 版要求琴不要太宽（大约是裙摆宽度加两头的卷饰），方便之后缩到游戏尺寸。
> - 裙子下摆是最低点 = 脚底线，飘带、琴、马尾都不能低于它（游戏在脚下画血条）。
> - **风格和比例照附图 8–10**（你之前让 Codex 画的乐芙兰 A、萨科 A、菲兹 A）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；Q 版比例，头约占身高的三分之一（乐芙兰 A 正好示范了长裙和温柔女性脸在这个风格里怎么画）。要求亮的高光：金边和卷饰上白金色的亮点，头发和裙片上浅青的高光，琴弦要亮。
> - 交付：`outputs/sona-model-A.png`、`outputs/sona-model-B.png`（1024×1536，真透明背景，人物约 1250 px 高），再附一个 `generation-prompts.txt` 写明实际用的提示词，最后写 `HANDOFF.md`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sona_league_front.png` | 英雄联盟原版娑娜，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 |
| `refs/2_sona_league_frontal.png` | 同一帧，几乎正面 | 领子、上衣、腰带、裙片 |
| `refs/3_sona_league_head.png` | 头部特写 | 脸、刘海、双马尾、金发饰 |
| `refs/4_sona_league_side.png` | 同一帧，更侧面 | 琴浮在身前的位置、裙摆的形状 |
| `refs/5_sona_league_etwahl.png` | 琴的特写 | 琴身、琴弦、两头的卷饰、飘带 |
| `refs/6_sona_league_cast.png` | 放技能时（E 第 0.4 秒），琴斜着抬起 | B 的姿势 |
| `refs/7_sona_league_splash.png` | 官方加载画面 | **只看气氛和头发**，服装以 1–6 为准 |
| `style/8_style_leblanc.png` | 你之前的乐芙兰像素图（A） | **只看风格、Q 版比例、长裙和脸的画法** |
| `style/9_style_shaco.png` | 你之前的萨科像素图（A） | **只看风格和比例** |
| `style/10_style_fizz.png` | 你之前的菲兹像素图（A） | **只看风格、Q 版比例、亮的蓝色怎么分档** |

## 提示词 A：`sona-model-A.png`（英雄联盟待机：琴平浮在腰前，双手抚弦）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 nearly frontal; 3 the head close-up; 4 a side view; 5 the instrument (the Etwahl) close-up; 6 a spell pose with the instrument tilted up; 7 the official illustration, for the mood and the hair only - its look differs from the game model, follow 1-6 for the costume and the instrument). Copy from them the costume, the colours, the hair and the instrument - NOT their 3D shading and NOT their adult proportions. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions (image 8 shows how a long gown and a gentle female face look in this style).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hair to the hem of the skirt, centred, comfortable transparent margins (the hair tails and the instrument's finials must not be cut off).
The character: Sona, the Maven of the Strings: a graceful, gentle musician who never speaks and plays a floating magical string instrument. HAIR: two very long, thick high TWIN TAILS of bright CYAN-BLUE hair tied at the top back of her head, sweeping back and up behind her like flowing silk, each tail ending in GOLDEN-YELLOW tips; a side-swept fringe over her forehead (not over her eyes) and a lock framing each cheek; a small GOLD hair ornament (a curved gold crest / crescent) on top of her head where the tails are tied. FACE: soft and calm, fair skin, two clear BLUE-TEAL eyes, a small closed mouth. GOWN: a long royal-BLUE gown: a dark-blue fitted bodice with a gold-trimmed neckline (draw it simply and modestly at chibi scale), a tall stand-up blue COLLAR with gold edges rising behind her shoulders, bare shoulders, long wide flowing blue SLEEVES with gold cuffs, a gold sash at the waist; the skirt flares out wide down to the floor in deep blue with long light-CYAN panels that hang in front and at the sides, every panel and the hem edged in GOLD with gold swirl motifs; the skirt hides her feet. THE ETWAHL (her instrument, her signature - keep it big and clear): a long floating zither/harp of GOLDEN carved wood (wood-grain gold and amber shades) shaped like a shallow boat, with a pointed keel under its middle; along its top run 3-4 thin CYAN strings between two small wooden bridges; its FRONT end (image right) curls up into a big gold wing-shaped SCROLL finial, its back end (image left) into a slimmer curved gold horn; two long light-CYAN RIBBONS with gold edges stream back from it.
Proportions: chibi like images 8, 9 and 10 - the head (crown to chin, without the twin tails) about one third of the height from the crown to the hem, big clear eyes, small hands; the instrument oversized and clear. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible and level, the fringe and the instrument never covering the eyes.
Pose: League's own idle (images 1 and 2): she stands upright behind the Etwahl, which floats LEVEL in front of her hips, both hands resting lightly on its strings, playing; her head tilted a little down toward the strings but the face still turned to the viewer with both eyes open; the twin tails flow back and up behind her head; the instrument's ribbons trail back past her skirt; keep the instrument compact: about as wide as her skirt plus the two finials, not much wider; the hem of the skirt is the lowest thing in the picture. Nothing hangs below the hem: the ribbons, the instrument and the hair tails end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (blue gown, cyan panels and ribbons, gold trim, golden wood, cyan hair with golden tips, skin) - coloured darks, never black fill (black is only the outline); bright highlights: white-gold glints on the trim and the finials, light-cyan highlights on the hair and the panels, the cyan strings bright; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no music notes, no text, no frame, no other characters.
```

## 提示词 B：`sona-model-B.png`（弹奏姿势：琴斜着抬起，抬头看前方）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-7 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 nearly frontal; 3 the head close-up; 4 a side view; 5 the instrument (the Etwahl) close-up; 6 a spell pose with the instrument tilted up; 7 the official illustration, for the mood and the hair only - its look differs from the game model, follow 1-6 for the costume and the instrument). Copy from them the costume, the colours, the hair and the instrument - NOT their 3D shading and NOT their adult proportions. Images 8, 9 and 10 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions (image 8 shows how a long gown and a gentle female face look in this style).
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hair to the hem of the skirt, centred, comfortable transparent margins (the hair tails and the instrument's finials must not be cut off).
The character: Sona, the Maven of the Strings: a graceful, gentle musician who never speaks and plays a floating magical string instrument. HAIR: two very long, thick high TWIN TAILS of bright CYAN-BLUE hair tied at the top back of her head, sweeping back and up behind her like flowing silk, each tail ending in GOLDEN-YELLOW tips; a side-swept fringe over her forehead (not over her eyes) and a lock framing each cheek; a small GOLD hair ornament (a curved gold crest / crescent) on top of her head where the tails are tied. FACE: soft and calm, fair skin, two clear BLUE-TEAL eyes, a small closed mouth. GOWN: a long royal-BLUE gown: a dark-blue fitted bodice with a gold-trimmed neckline (draw it simply and modestly at chibi scale), a tall stand-up blue COLLAR with gold edges rising behind her shoulders, bare shoulders, long wide flowing blue SLEEVES with gold cuffs, a gold sash at the waist; the skirt flares out wide down to the floor in deep blue with long light-CYAN panels that hang in front and at the sides, every panel and the hem edged in GOLD with gold swirl motifs; the skirt hides her feet. THE ETWAHL (her instrument, her signature - keep it big and clear): a long floating zither/harp of GOLDEN carved wood (wood-grain gold and amber shades) shaped like a shallow boat, with a pointed keel under its middle; along its top run 3-4 thin CYAN strings between two small wooden bridges; its FRONT end (image right) curls up into a big gold wing-shaped SCROLL finial, its back end (image left) into a slimmer curved gold horn; two long light-CYAN RIBBONS with gold edges stream back from it.
Proportions: chibi like images 8, 9 and 10 - the head (crown to chin, without the twin tails) about one third of the height from the crown to the hem, big clear eyes, small hands; the instrument oversized and clear. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH eyes visible and level, the fringe and the instrument never covering the eyes.
Pose: a playing pose like her spells (image 6): she stands upright, head raised, looking ahead and slightly at the viewer, both eyes clearly open; the Etwahl floats in front of her body TILTED on a diagonal - its back horn end (image left) raised high beside her near shoulder, its front scroll-finial end (image right) low in front of her hip; her near hand raised at the high end, her far hand plucking the strings near the low end; the twin tails flow back behind her; the ribbons trail back; the hem of the skirt is the lowest thing in the picture. Nothing hangs below the hem: the ribbons, the instrument and the hair tails end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 8-10 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (blue gown, cyan panels and ribbons, gold trim, golden wood, cyan hair with golden tips, skin) - coloured darks, never black fill (black is only the outline); bright highlights: white-gold glints on the trim and the finials, light-cyan highlights on the hair and the panels, the cyan strings bright; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no music notes, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，马尾、发饰、琴两头的卷饰都没被切掉。
- 两只眼睛都在、同一高度、睁开、看得清；刘海和琴都没挡住脸。
- 琴完整：金色琴身、青色琴弦、前端大卷翼、后端弯角、两条飘带都在；A 版琴是平的，B 版琴是斜的。
- 裙子下摆是最低点，飘带、琴、马尾都不低于它；裙子盖住脚。
- 大像素块清楚，没有糊、没有柔光、没有渐变、没有音符特效。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
