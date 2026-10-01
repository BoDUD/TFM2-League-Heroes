# 魔腾：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 魔腾还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差姿势：**A = 英雄联盟的待机**（弓着身子浮在空中，头压在两块大肩甲之间，双拳在胸前，手臂上的刀刃向后扫）；**B = 直立浮空**（头高出肩甲，双臂垂在身侧，刀刃朝下向后）。你挑一版，之后第 1 步再按它画游戏尺寸（约 40 格）的精灵。
> - **长相照英雄联盟原版**（附图 1–5）：深靛蓝色的暗影身体，光头的长颅骨，脸上有深沟纹、尖下巴、看不到嘴，头顶一道尖冠向后扫；两只细长上挑、发白光的眼睛；两块比头宽得多的大圆肩甲（银灰钢板 + 暗紫色内层，顶上一圈淡蓝发光的同心圆符文，边上一圈钢刺）；深色钢胸甲，腰下垂一块暗红色的腰布（银边圆环纹章、下摆锯齿）；带刺的钢护手和大拳头；**两条前臂外侧各长一把大弯刃**（暗红刀身 + 银白火焰纹 + 银色带钩的刃边，向后扫过手肘，前端是一根细长银刺）。
> - **他没有腿**：英雄联盟里他腰下是一股暗影烟雾（特效，不在模型里，渲染图上看不到），提示词里写成「腰布下面化成深蓝紫色的烟雾尾巴，越往下越细，卷成一个尖」。尾巴尖就是最低点 = 脚底线，刀刃、拳头、烟丝都不能低于它（游戏在脚下画血条）。
> - **风格和比例照附图 7–9**（你之前让 Codex 画的萨科、维迦、贾克斯）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；Q 版比例，头约占身高的三分之一。身体很暗，所以要求亮边和高光（肩、头、拳头的淡蓝描亮，刺和刀刃的银白高光），白眼睛是全图最亮的点。
> - 交付：`outputs/nocturne-model-A.png`、`outputs/nocturne-model-B.png`（1024×1536，真透明背景，人物约 1250 px 高），再附一个 `generation-prompts.txt` 写明实际用的提示词。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_nocturne_league_front.png` | 英雄联盟原版魔腾，待机第一帧，3/4 正面朝右 | 服装、颜色、A 的姿势 |
| `refs/2_nocturne_league_frontal.png` | 同一帧，几乎正面 | 两块肩甲、胸甲、腰布、两把刀 |
| `refs/3_nocturne_league_head.png` | 头部特写 | 脸、白眼睛、头冠、肩甲上的符文和刺 |
| `refs/4_nocturne_league_side.png` | 同一帧，更侧面 | 弓背的身形、刀刃怎么长在前臂上 |
| `refs/5_nocturne_league_blade.png` | 前臂刀刃特写 | 刀的形状、红色和银色的花纹 |
| `refs/6_nocturne_league_splash.png` | 官方加载画面 | **只看气氛、发光的眼睛和烟雾身体**，服装以 1–5 为准 |
| `style/7_style_shaco.png` | 你之前的萨科像素图 | **只看风格和比例** |
| `style/8_style_veigar.png` | 你之前的维迦像素图 | **只看风格、Q 版比例、暗色脸上的发光眼睛** |
| `style/9_style_jax.png` | 你之前的贾克斯像素图 | **只看风格、盔甲和肩甲的画法** |

## 提示词 A：`nocturne-model-A.png`（英雄联盟待机：弓身浮空，双拳在前，刀刃后扫）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 nearly frontal, both pauldrons and the tabard; 3 the head close-up; 4 a side view; 5 the forearm blade close-up; 6 the official illustration, for the mood, the glowing eyes and the shadow-smoke body only - its look differs from the game model, follow 1-5 for the costume). The renders show NO lower body: in the game his tail is a smoke effect, described below. Copy from them the costume, the colours, the head, the pauldrons and the blades - NOT their 3D shading and NOT their adult proportions. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the crest to the tip of the smoke tail, centred, comfortable transparent margins.
The character: Nocturne, the Eternal Nightmare: a living shadow in spiked armour, a demon that hunts in the dark. HEAD: a long hairless skull of dark NAVY-INDIGO shadow-flesh (no hair, no helmet), the face deeply grooved with ridges, a narrow jaw that ends in a pointed chin, NO visible mouth; a tall pointed crest rises from the top of the skull and sweeps back like a fin; two narrow slanted EYES glowing pure WHITE with a faint pale-blue glow, angry, set under a heavy brow ridge - the glowing eyes are his signature, keep them big, bright and readable. ARMOUR: two HUGE rounded pauldrons, much wider than his head, made of layered silver-grey steel plates with MAUVE / dusky-purple inner panels, each with a glowing pale-blue concentric RING rune on top and a crown of short sharp steel spikes along its rim; a dark steel cuirass over a navy chest; a dark CRIMSON tabard hangs from his belt with a silver-trimmed ring emblem and a jagged lower edge; dark steel gauntlets and bracers with spikes; big navy fists. WEAPONS: a huge curved BLADE grows from the outside of EACH forearm - a broad crimson-red blade with wavy silver-white flame inlays, a silver hooked and barbed edge, sweeping back past the elbow like a scythe and ending in a long thin silver spike past the fist. LOWER BODY: he has NO LEGS - below the tabard his body dissolves into a dark navy-violet SHADOW-SMOKE TAIL of ragged wisps that narrows and curls down to a point, with a few small wisps trailing off it, darker and more transparent looking toward the tip.
Proportions: chibi like images 7, 8 and 9 - the head (crest base to chin) about one third of the height from the crest base to the tail tip, the pauldrons big and clear, the fists and blades oversized, the smoke tail about one third of the height. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH glowing white eyes visible and level, nothing covering the face.
Pose: League's own idle (images 1 and 2): he floats hunched forward, his head low between the two huge pauldrons, both fists forward in front of his chest at shoulder height, ready to strike; the two forearm blades lie along the outside of his forearms and sweep back past his elbows - the near blade (image left) trails behind him at hip height, the far blade behind his far shoulder; the smoke tail curls down under him and ends in a point ON the soles line. The tail's point is the lowest thing in the picture: the blades, the fists and every wisp end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: navy and indigo for the body, never black fill - black is only the outline); lit edges and bright highlights so the dark body still reads: pale-blue rims on the shoulders, head and fists, white-silver highlights on the spikes, the pauldron plates and the blade edges, the crimson blades and tabard in clear reds; the glowing white eyes the brightest spot of the picture; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 提示词 B：`nocturne-model-B.png`（直立浮空：头高出肩甲，双臂垂下，刀刃朝下向后）

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-6 are 3D renders and art of the character from the game (1 full figure 3/4 front; 2 nearly frontal, both pauldrons and the tabard; 3 the head close-up; 4 a side view; 5 the forearm blade close-up; 6 the official illustration, for the mood, the glowing eyes and the shadow-smoke body only - its look differs from the game model, follow 1-5 for the costume). The renders show NO lower body: in the game his tail is a smoke effect, described below. Copy from them the costume, the colours, the head, the pauldrons and the blades - NOT their 3D shading and NOT their adult proportions. Images 7, 8 and 9 are STYLE ONLY, other characters: copy their pixel-art style and their chibi game-character proportions.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha), the character about 1250 px tall from the top of the crest to the tip of the smoke tail, centred, comfortable transparent margins.
The character: Nocturne, the Eternal Nightmare: a living shadow in spiked armour, a demon that hunts in the dark. HEAD: a long hairless skull of dark NAVY-INDIGO shadow-flesh (no hair, no helmet), the face deeply grooved with ridges, a narrow jaw that ends in a pointed chin, NO visible mouth; a tall pointed crest rises from the top of the skull and sweeps back like a fin; two narrow slanted EYES glowing pure WHITE with a faint pale-blue glow, angry, set under a heavy brow ridge - the glowing eyes are his signature, keep them big, bright and readable. ARMOUR: two HUGE rounded pauldrons, much wider than his head, made of layered silver-grey steel plates with MAUVE / dusky-purple inner panels, each with a glowing pale-blue concentric RING rune on top and a crown of short sharp steel spikes along its rim; a dark steel cuirass over a navy chest; a dark CRIMSON tabard hangs from his belt with a silver-trimmed ring emblem and a jagged lower edge; dark steel gauntlets and bracers with spikes; big navy fists. WEAPONS: a huge curved BLADE grows from the outside of EACH forearm - a broad crimson-red blade with wavy silver-white flame inlays, a silver hooked and barbed edge, sweeping back past the elbow like a scythe and ending in a long thin silver spike past the fist. LOWER BODY: he has NO LEGS - below the tabard his body dissolves into a dark navy-violet SHADOW-SMOKE TAIL of ragged wisps that narrows and curls down to a point, with a few small wisps trailing off it, darker and more transparent looking toward the tip.
Proportions: chibi like images 7, 8 and 9 - the head (crest base to chin) about one third of the height from the crest base to the tail tip, the pauldrons big and clear, the fists and blades oversized, the smoke tail about one third of the height. 3/4 FRONT view facing image right, the face turned toward the viewer, BOTH glowing white eyes visible and level, nothing covering the face.
Pose: an upright floating stance (more like the attached style images): he floats tall and upright, his head clearly above the pauldrons, chin a little down, glaring at the viewer; both arms hang a little out from his sides with the fists at hip height, the forearm blades pointing down and back along his sides (their tips behind him at knee height); the smoke tail hangs straight down under him and ends in a point ON the soles line, a few wisps curling back. The tail's point is the lowest thing in the picture: the blades, the fists and every wisp end AT OR ABOVE that line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 7-9 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: navy and indigo for the body, never black fill - black is only the outline); lit edges and bright highlights so the dark body still reads: pale-blue rims on the shoulders, head and fists, white-silver highlights on the spikes, the pauldron plates and the blade edges, the crimson blades and tabard in clear reds; the glowing white eyes the brightest spot of the picture; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no ground, no shadow, no glow halo, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），四周留边，人物完整，头冠、肩刺、刀尖都没被切掉。
- 两只白眼睛都在、同一高度，是全图最亮的地方；脸没被拳头、刀或肩甲挡住；没有嘴。
- 没有腿：腰布下面是一股越来越细的烟雾尾巴，尾巴尖是最低点；刀尖、拳头、烟丝都不低于它。
- 身体是深靛蓝而不是纯黑，肩甲、拳头、头上有亮边；两把红刀完整、长在前臂外侧。
- 大像素块清楚，没有糊、没有柔光、没有渐变。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
