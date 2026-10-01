# 萨科：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 萨科还没有原图。这一步请 Codex 画一张全身像素风原图。A、B 两版姿势一样（英雄联盟的待机），只差小丑服朝向我们的是哪一半：**A 红色那一半在前**（和加载画面的红色外套一致），**B 深蓝那一半在前**。你挑一版，之后第 1 步再按它画游戏尺寸（约 40 格，帽子算在内）的精灵。
> - **长相照英雄联盟原版**（附图 1–6）：白色瓷面具、长长的尖下巴往前勾、冰蓝发光的细长眼睛、满脸的大咧嘴笑（一排白牙）；红/深蓝对半的双角小丑帽，角尖挂金色菱形铃铛；金色锯齿领圈；银色带尖刺的肩甲；红/深蓝对半的小丑外套、金菱形扣子、金腰带，下摆是带小金铃的尖角；袖子是深蓝上臂加红色大泡泡袖口，手是淡蓝灰色；黑白菱格的大灯笼裤；深色靴子加银色尖刺护胫，红色尖头翘鞋；两只手各握一把锯齿银刃的短匕首。
> - **风格和比例照附图 7、8**（你之前让 Codex 画的卢锡安、维迦）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；Q 版比例，头（帽檐到下巴尖）约占身高的三分之一，帽子的两只角在这之上。3/4 正面朝右，面具和笑容朝向我们，两只蓝眼睛都看得见。
> - **姿势 = 英雄联盟待机**：双脚分开、膝盖微弯、含胸低头坏笑，两手垂在胯边：近侧手（图左）的匕首朝后，远侧手的匕首朝下偏后。
> - 脚底线以下什么都不能有（游戏在脚下画血条）：翘鞋尖、匕首都在脚底以上结束。
> - 交付：`outputs/shaco-model-A.png`、`outputs/shaco-model-B.png`（1024×1536，真透明背景，人物约 1250 px 高），再附一个 `generation-prompts.txt` 写明实际用的提示词。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_shaco_league_front_red.png` | 英雄联盟原版萨科，待机第一帧，3/4 正面朝右，红色一半在前 | A 的服装、颜色、姿势 |
| `refs/2_shaco_league_front_navy.png` | 同一帧，深蓝一半在前 | B 的服装、颜色、姿势 |
| `refs/3_shaco_league_head_red.png` | A 那一面的头部特写 | 面具、笑容、眼睛、帽子、领圈、肩甲 |
| `refs/4_shaco_league_head_navy.png` | B 那一面的头部特写 | 同上 |
| `refs/5_shaco_league_daggers.png` | 两只手和匕首（放大） | 匕首的形状和拿法 |
| `refs/6_shaco_league_splash.png` | 官方加载画面 | **只看脸和气质**，颜色以游戏模型为准 |
| `style/7_style_lucian.png` | 你之前的卢锡安像素图 | **只看风格和比例** |
| `style/8_style_veigar.png` | 你之前的维迦像素图 | **只看风格、Q 版比例和帽子的画法** |

## 提示词 A：`shaco-model-A.png`（红色一半在前）

八张图都附上，顺序同上表。

```text
Eight attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front, red side; 2 the same, navy side; 3 and 4 head close-ups of both sides; 5 the daggers in his hands; 6 the official illustration, for the face and the attitude only): copy from them the costume, the colours, the mask, the hat and the daggers - NOT their 3D shading and NOT their adult proportions. Images 7 and 8 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions. Image 1 is the costume side and the pose for THIS picture.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hat to the soles, centred, comfortable transparent margins.
The character: Shaco, the Demon Jester: a lanky, menacing harlequin. FACE: a white porcelain jester MASK with soft lavender-grey shading, long and narrow, ending in a long pointed chin that hooks forward; two narrow slanted eyes glowing ICE-CYAN inside dark navy eye sockets; a HUGE wide grin across the whole mask showing two rows of white teeth with dark lines between them - the grin is his signature, keep it big and readable. HAT: a two-horned jester cap split down the middle, one half crimson red and one half dark navy blue; one horn stands up and the other curls back and down, each horn tipped with a small GOLD diamond-shaped bell. A jagged GOLD ruff collar of spikes round his neck under the chin. Big SILVER-STEEL spiked pauldrons on both shoulders (two or three sharp spikes pointing up, gold rims, a gold diamond stud). A harlequin jacket split down the middle in the same crimson red and dark navy, gold diamond buttons down the front, a gold belt with a diamond buckle; the jacket's tails hang to mid-thigh in jagged points tipped with small gold bells. Sleeves: navy upper arms with gold bands and BIG puffy crimson-red forearm cuffs; pale blue-grey hands. Very puffy knee-length pantaloons in a black-and-white diamond CHECKERBOARD pattern. Lower legs in dark charcoal-navy boots with flaring silver spiked shin guards, ending in pointed crimson jester shoes whose toes curl up. WEAPONS: one short dagger in EACH hand - a silver-white blade with jagged serrated (zig-zag) edges and a sharp point, a small gold cross-guard and a dark grip.
Proportions: chibi like images 7 and 8 - the head (the top of the cap's band to the tip of the chin) about one third of the height from the cap band to the soles, the hat's horns on top of that; slim body, long thin arms, the puffy pantaloons and the spiky boots kept big and clear. 3/4 FRONT view facing image right, the mask and its grin turned toward the viewer, BOTH glowing cyan eyes visible and level, nothing covering the mask.
Costume side A - the RED side toward us, exactly as image 1: the front of his jacket and the near half of his chest crimson red, the far half navy; the hat's NAVY horn curls back over the near side (image left) with its gold bell, the RED horn stands up at the far side (image right).
Pose: League's own idle: he stands with his feet apart and his knees a little bent, shoulders hunched forward, chin down with a sly grin; both arms hang a little out from his sides at hip height, the near hand (image left) holding its dagger pointing backward (to image left), the far hand (image right) holding its dagger pointing down and slightly back - both blades clearly visible against the body, both daggers end ABOVE the soles line. Both soles on the same horizontal line; the curled shoe tips, the daggers and everything else end AT OR ABOVE the soles line (the game draws the health bar under the feet).
Style: detailed crisp pixel art like images 7 and 8 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks, black is only the outline and the gaps between the teeth); bright white-silver highlights on the blades, the spikes and the pauldrons; the cyan eyes the brightest spot of the face; the checkerboard pantaloons in clean black and pale grey-white squares; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 提示词 B：`shaco-model-B.png`（深蓝一半在前）

八张图都附上，顺序同上表。

```text
Eight attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front, red side; 2 the same, navy side; 3 and 4 head close-ups of both sides; 5 the daggers in his hands; 6 the official illustration, for the face and the attitude only): copy from them the costume, the colours, the mask, the hat and the daggers - NOT their 3D shading and NOT their adult proportions. Images 7 and 8 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions. Image 2 is the costume side and the pose for THIS picture.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the hat to the soles, centred, comfortable transparent margins.
The character: Shaco, the Demon Jester: a lanky, menacing harlequin. FACE: a white porcelain jester MASK with soft lavender-grey shading, long and narrow, ending in a long pointed chin that hooks forward; two narrow slanted eyes glowing ICE-CYAN inside dark navy eye sockets; a HUGE wide grin across the whole mask showing two rows of white teeth with dark lines between them - the grin is his signature, keep it big and readable. HAT: a two-horned jester cap split down the middle, one half crimson red and one half dark navy blue; one horn stands up and the other curls back and down, each horn tipped with a small GOLD diamond-shaped bell. A jagged GOLD ruff collar of spikes round his neck under the chin. Big SILVER-STEEL spiked pauldrons on both shoulders (two or three sharp spikes pointing up, gold rims, a gold diamond stud). A harlequin jacket split down the middle in the same crimson red and dark navy, gold diamond buttons down the front, a gold belt with a diamond buckle; the jacket's tails hang to mid-thigh in jagged points tipped with small gold bells. Sleeves: navy upper arms with gold bands and BIG puffy crimson-red forearm cuffs; pale blue-grey hands. Very puffy knee-length pantaloons in a black-and-white diamond CHECKERBOARD pattern. Lower legs in dark charcoal-navy boots with flaring silver spiked shin guards, ending in pointed crimson jester shoes whose toes curl up. WEAPONS: one short dagger in EACH hand - a silver-white blade with jagged serrated (zig-zag) edges and a sharp point, a small gold cross-guard and a dark grip.
Proportions: chibi like images 7 and 8 - the head (the top of the cap's band to the tip of the chin) about one third of the height from the cap band to the soles, the hat's horns on top of that; slim body, long thin arms, the puffy pantaloons and the spiky boots kept big and clear. 3/4 FRONT view facing image right, the mask and its grin turned toward the viewer, BOTH glowing cyan eyes visible and level, nothing covering the mask.
Costume side B - the NAVY side toward us, exactly as image 2: the front of his jacket and the near half of his chest dark navy, the far half crimson; the hat's RED horn curls back over the near side (image left) with its gold bell, the NAVY horn stands up at the far side (image right).
Pose: League's own idle: he stands with his feet apart and his knees a little bent, shoulders hunched forward, chin down with a sly grin; both arms hang a little out from his sides at hip height, the near hand (image left) holding its dagger pointing backward (to image left), the far hand (image right) holding its dagger pointing down and slightly back - both blades clearly visible against the body, both daggers end ABOVE the soles line. Both soles on the same horizontal line; the curled shoe tips, the daggers and everything else end AT OR ABOVE the soles line (the game draws the health bar under the feet).
Style: detailed crisp pixel art like images 7 and 8 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks, black is only the outline and the gaps between the teeth); bright white-silver highlights on the blades, the spikes and the pauldrons; the cyan eyes the brightest spot of the face; the checkerboard pantaloons in clean black and pale grey-white squares; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，帽角没被切掉。
- 面具上两只冰蓝眼睛都在、同一高度；大笑的白牙清楚；面具没被匕首、手或帽角挡住。
- 两只手各一把匕首，刀刃完整；匕首、翘鞋尖都不低于脚底线，两只脚底在同一条水平线上。
- 灯笼裤是干净的黑白菱格；大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
