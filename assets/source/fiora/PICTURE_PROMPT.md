# Fiora — 设定图（第 0 步）

## 中文说明（给用户看）
请 Codex 按这份包画**一张高清像素风的剑姬（菲奥娜）设定图**，和之前的戴安娜、薇恩、阿卡丽同一种画风，出两张：
- **A**：英雄联盟里的起手式——右手（近侧手）把细剑平举向右前方，剑尖朝右，身体侧身站立，左手在身后/腰间，披风垂在身后。
- **B**：放松站姿（参考 06）——两手叉腰，握剑的手在腰间，细剑从腰间斜垂向身后（画面左下），**剑尖不低于鞋底**。

两张都要：面朝右的 3/4 正面（看得到脸和胸口，两只眼睛都要看见，绝不画背影），整个人完整在画布里，透明背景，没有光晕、没有地面阴影，**鞋底以下什么都不能有**（游戏里血条在脚下，会挡住）。细剑是一根很细的长剑，剑身要又细又直。
输出：`outputs/fiora-model-A.png`（1536x1024 横图，平举的细剑完整在画内）、`outputs/fiora-model-B.png`（1024x1536 竖图），真透明 PNG。

参考图说明：01–03 只是**画风**参考（之前采用的设定图）；04 是 A 的姿势和服装（权威）；05 是脸部正面（青绿色眼睛、深红刘海、粉色嘴唇），05b 是侧面看的波波头形状；06 是 B 的姿势；07 侧面；08 背面（看披风内侧白色 + 金边 + 青色宝石）；09 剑柄特写。英雄联盟渲染图只做参考，不要照抄 3D 的光影。英雄联盟里深红刘海会遮住一只眼，这里要求刘海扫过额头但**两只眼睛都露出来**（游戏里 40 像素高，看不见眼睛脸就糊了）。

## English prompt (for Codex)

Use case: stylized-concept character picture. Create TWO final character illustrations of **Fiora, the Grand Duelist**
(League of Legends), in her CLASSIC in-game costume, as detailed crisp PIXEL ART in exactly the style of the attached
pictures 01-03 (dark stepped pixel contours, 3-5 flat tones per material, crisp metal highlights). References 01-03 are
ART STYLE ONLY: do NOT copy their characters, backgrounds or glows. References 04-09 (renders of League's own model)
are authoritative for Fiora's costume, hair, face and rapier; do not copy their 3D lighting, redraw them as pixel art.

**Picture A** (reference 04, her en-garde idle): full body, facing RIGHT in a three-quarter FRONT view, face and chest
visible, BOTH eyes visible (the far eye slightly narrower), never a rear view. Standing side-on like a fencer, feet
apart on the SAME horizontal baseline, the near (sword) arm extended forward to the right at shoulder height holding the
long rapier pointing to the RIGHT, blade almost horizontal and slightly raised; the other hand low behind her hip; the
cape hanging behind her. The whole rapier must fit in the canvas. 1536x1024 landscape PNG.

**Picture B** (reference 06): the same character, same camera, a relaxed duelist stance: both hands on her hips, the
sword hand at the hip holding the rapier so the blade slants down and BACK behind her legs (toward the image left), its
tip ABOVE the soles line (nothing below the feet). Face and chest visible, both eyes visible. 1024x1536 portrait PNG.

**Fiora's look (both pictures):**
- Hair: short sleek DARK INDIGO-PURPLE bob, the ends cut at the jaw and pointed toward the chin (references 05, 05b),
  with a broad CRIMSON-RED streak sweeping across the forehead from the parting down past the near cheek. In League the
  red fringe covers one eye; here it sweeps ABOVE the eyes so BOTH eyes stay visible. Fair skin, sharp confident eyes
  with TEAL-CYAN irises and one white highlight each, thin calm brows, small closed pink-red lips, proud chin.
  Reference 05 is a near-front view of the face: turn the head to the RIGHT in the same three-quarter view as the body.
- High-collared WHITE / cream long-sleeved blouse-coat with gold piping, open at the lower front.
- Ornate GOLD armour: big curled gold pauldrons on both shoulders with small CYAN gems, a gold gorget/collar plate, a gold
  armoured gauntlet covering the whole sword forearm, gold plates at the waist and hips with a cyan gem at the buckle.
- Dark TEAL-BLUE fitted bodysuit / leggings, dark teal knee boots with low heels and thin gold trim.
- A long CAPE hanging from the shoulders down her back to the knees: outer side deep wine-maroon, inner side WHITE with a
  gold border and a cyan gem at its lower end (reference 08).
- The RAPIER: a long, very THIN straight silver-white blade (as long as she is tall), a swept GOLD guard curling round the
  hand with a small cyan gem, a dark grip, a gold pommel (reference 09).
- Colour accents: gold + cyan gems + white; the teal-cyan of the eyes also marks the gems, nowhere else on the face.

Head large and readable (the later game sprite is a 40-px chibi, so keep the face clean and the shapes bold). Detailed
PIXEL ART, not vector, not soft painting, not smooth 3D; crisp edges, no blur, no gradients, no noisy texture. REAL
transparent background (alpha 0 outside the silhouette), no backdrop colour, no glow, halo or aura, no ground, no
contact or cast shadow, no pedestal, no frame, no text, no labels. Nothing below the soles. One character per picture,
centred, top of the hair to the soles about 850 px, at least 80 px of empty transparent margin all round.

Deliver: `outputs/fiora-model-A.png` (1536x1024) and `outputs/fiora-model-B.png` (1024x1536), true RGBA PNGs.
