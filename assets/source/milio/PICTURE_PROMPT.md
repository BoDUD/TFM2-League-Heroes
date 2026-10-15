# 米利欧（明烛）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 米利欧是一个**开朗的小男孩**（伊施塔尔的少年火焰治疗师）。这一步请 Codex 画一张全身像素风原图，A、B 两版男孩的长相、衣服、颜色、大小完全一样：**A = 英雄联盟的待机**（双拳握在胸前，咧嘴笑，附图 1）；**B = 同样的待机 + 他肩膀后面飘着一个发光的小火精灵**（加载画面里那个圆圆的、带笑脸的火球伙伴，附图 5、9）。你挑一版，之后第 1 步再按它画正面 + 侧面的高清（PPU）造型。这一版走**高清（PPU）**，按统一画风（**附图 10–12 是游戏里重做后的泽丽、千珏、尼菈**）：像素块清楚、**每个游戏像素约 2.2 格**、**描边粗（约 2 格）**、身材**偏 Q 版、敦实**。你画的原图会直接按格子读回成游戏里的高清造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–8）。
> - **头**（附图 3 特写）：一个小孩，头大一点，约占身高的**三分之一**；**蓬松卷曲的深靛蓝黑色短发**（亮部带一点蓝紫光泽），刘海乱翘；**暖棕色皮肤**；**两只大大的琥珀/橙棕色眼睛**（要看得清，有高光）；**开心地咧嘴笑**（白牙露一点）；**脸朝右前方平视**（附图 3 的模型在抬头看天，画的时候**平视前方**）。
> - **衣服**：**红色短上衣**（领口一圈青绿色立领，胸前一颗**青绿色的扣子/坠饰**），肩上两块**大大的金色/铜色蓬起的肩垫**（像卷起来的布，末端有米白色流苏，附图 8 特写）；腰上**一条宽的青绿色腰带**斜着绕过身体，中间一块金色的扣；下面是**品红/紫红色的短裙式下摆**（褶子，到膝盖上面）；**光着的棕色小腿**；脚踝上**红色 + 青绿色的布绑腿**，**棕色凉鞋**。
> - **手**：**双拳握在胸前**（附图 1），手臂是棕色皮肤。
> - **小火精灵（只有 B 版）**：一个**圆滚滚的发光火球小精灵**，约有男孩的**头那么大或小一点**：中间**亮黄白色**，外圈**橙色**，最外面一圈**深橙红**，顶上**几簇小火苗**往上翘；**一张可爱的小脸**（两个小黑眼睛 + 一个小嘴，开心）。它**飘在男孩背后、肩膀高度、画面左边**（附图 9 的黄色圆只是位置和大小示意，不是画风），**不能挡住他的脸和双手**，不碰地面。
> - **姿势**：3/4 正面朝右（脸朝右前方，胸口朝向看画的人），两脚稍分开站稳：**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗、稍高**，两只凉鞋底落在同一条地面线上。
> - **比例**（统一画风）：**敦实、偏 Q 版**——小孩的头大（约三分之一身高），身体宽度约为身高的一半（算上肩垫），腿短一点；**不要细长的写实比例**。风格完全照附图 10–12。
> - **画布用竖版 1024×1536**：**男孩从头发顶到鞋底约 720 px，也就是约 72 格**（A、B 一样大），鞋底在离画布底边约 200 px 的地方；全部在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 10 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个高清像素）；**外轮廓一圈 2 块宽的近黑描边**（附图 10–12 的粗描边）；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（火球、营火、护盾、光圈都在第 3 步单独画；B 版的小火精灵是角色的一部分，要画）；不画地面和影子。
> - 交付：`outputs/milio-picture/milio-model-A.png`、`outputs/milio-picture/milio-model-B.png`（都是 1024×1536 竖版、真透明背景）；B 版**另外从同一张成品图里分出两层**（同样的画布和位置，不重画）：`milio-model-B-boy.png` / `milio-model-B-spirit.png`（小火精灵那一层把被挡住的部分补完整）；原始生成图原样放进 `outputs/milio-picture/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `milio_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_milio_front.png` | 英雄联盟原版米利欧待机，3/4 朝右 | 颜色、形状、**角度**、姿势 |
| `refs/2_milio_frontal.png` | 同一帧，正面 | 肩垫、腰带、下摆、绑腿怎么做 |
| `refs/3_milio_head.png` | 头部特写 | 卷发、琥珀大眼、笑脸（模型在抬头，画的时候**平视**） |
| `refs/4_milio_back.png` | 同一帧的背后 | 头发和肩垫的背面 |
| `refs/5_milio_splash.png` | 官方加载画面 | 气质（开朗）、**小火精灵的样子**（他肩旁发光的圆火球） |
| `refs/6_milio_actions.png` | 普攻、火爆飞踢、融融情谊、跑动的瞬间（侧面） | 第 2 步用（这一步不画） |
| `refs/7_milio_side.png` | 待机的侧面（朝右） | 第 1 步用（这一步不用） |
| `refs/8_milio_shoulders.png` | 上半身特写 | 金色蓬起的肩垫 + 米白流苏、领口、青绿坠饰、腰带 |
| `refs/9_layout_B.png` | B 的布局示意（模型剪贴 + 一个黄色圆，只看位置和大小） | 小火精灵在他背后肩膀高度、画面左边 |
| `style/10_style_zeri.png` | 游戏里重做后的泽丽高清待机（8 倍放大，一格 = 一个高清像素）——统一画风的样板 | **只看风格**：像素粗细、粗描边、敦实比例、头的大小 |
| `style/11_style_kindred.png` | 重做后的千珏高清待机（8 倍） | **只看风格**（最新做好的英雄） |
| `style/12_style_nilah.png` | 重做后的尼菈高清待机（8 倍） | **只看风格** |

## 提示词 A：`milio-model-A.png`（英雄联盟待机）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-8 are 3D renders and art of a character from the game: a cheerful young boy, a fire healer (1 the boy in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 2 the same from the front: the shoulder pads, the sash, the skirt, the leg wraps; 3 his head close-up: the curly hair, the big amber eyes, the grin - the 3D model looks UP at the sky, draw him looking STRAIGHT AHEAD instead; 4 the same from behind; 5 the official illustration: his cheerful mood and the little glowing fire spirit at his shoulder; 6 moments of his actions from the side - not drawn here; 7 his idle from the side - not used here; 8 a close-up of his upper body: the puffed golden shoulder pads with cream tassels, the collar, the teal pendant, the sash). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Image 9 is the other version's layout guide: ignore it. Images 10, 11 and 12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, STOCKY chunky proportions and head size (image 10 the model of this series' look).
Create ONE pixel-art picture of the boy, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha). The boy about 720 px (about 72 squares) from the top of his hair to the soles of his sandals, the soles about 200 px above the bottom edge; whole, comfortable transparent margins, nothing cut off; both soles level on one ground line.
THE BOY: a cheerful young boy. THE HEAD, BIG, about ONE THIRD of his height: fluffy CURLY short hair, DARK INDIGO-BLACK with a little blue-violet sheen on the lights, messy bangs; WARM BROWN skin; TWO BIG AMBER / ORANGE-BROWN EYES with highlights, clearly readable; a happy open GRIN (a little white of the teeth); the face turned to the front-right, looking STRAIGHT AHEAD (not up). THE CLOTHES: a short RED TUNIC with a TEAL stand-up collar and a TEAL round pendant on the chest; two BIG PUFFED GOLDEN-BRONZE SHOULDER PADS like rolled cloth, cream tassels at their ends (image 8); a wide TEAL SASH wrapped diagonally round his waist with a small gold buckle; below it a MAGENTA / PURPLE-RED pleated skirt-like kilt down to above the knees; bare BROWN shins; RED-AND-TEAL cloth WRAPS round the ankles; BROWN SANDALS. Both FISTS held together in front of his chest (image 1).
Pose: League's own idle (image 1), 3/4 FRONT view facing image right: his face turned to the front-right, chest toward the viewer; standing firm, feet a little apart: the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher, both sandals on the ground line.
Proportions: STOCKY and CHUNKY like images 10-12, NOT a tall slender realistic figure - a child: the head big (about one third of his height), the body about half as wide as he is tall (with the shoulder pads), slightly short legs. Keep the figure COMPACT.
Style: crisp chunky pixel art like images 10-12 - EVEN SQUARE PIXELS OF 10 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around the figure, inside it every material in its own 3-4 flat shades, no stray single odd squares: the hair dark indigo-black with blue-violet lights, the skin warm brown, the eyes amber, the tunic red, the shoulder pads gold-bronze with cream tassels, the collar / pendant / sash teal, the kilt magenta-purple, the wraps red and teal, the sandals brown; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no fireballs, no fire, no glow aura, no rings), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`milio-model-B.png`（待机 + 肩后的小火精灵）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-8 are 3D renders and art of a character from the game: a cheerful young boy, a fire healer (1 the boy in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 2 the same from the front: the shoulder pads, the sash, the skirt, the leg wraps; 3 his head close-up: the curly hair, the big amber eyes, the grin - the 3D model looks UP at the sky, draw him looking STRAIGHT AHEAD instead; 4 the same from behind; 5 the official illustration: his cheerful mood and THE LITTLE GLOWING FIRE SPIRIT at his shoulder - the look of the spirit; 6 moments of his actions from the side - not drawn here; 7 his idle from the side - not used here; 8 a close-up of his upper body: the puffed golden shoulder pads with cream tassels, the collar, the teal pendant, the sash). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Image 9 is a LAYOUT GUIDE ONLY: the yellow disc shows where the fire spirit floats and how big it is - not its look, not the style. Images 10, 11 and 12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the THICK near-black outline, flat 3-4 step shading, STOCKY chunky proportions and head size (image 10 the model of this series' look).
Create ONE pixel-art picture of the boy and his fire spirit, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha). The boy about 720 px (about 72 squares) from the top of his hair to the soles of his sandals, the soles about 200 px above the bottom edge; whole, comfortable transparent margins, nothing cut off; both soles level on one ground line.
THE BOY: a cheerful young boy. THE HEAD, BIG, about ONE THIRD of his height: fluffy CURLY short hair, DARK INDIGO-BLACK with a little blue-violet sheen on the lights, messy bangs; WARM BROWN skin; TWO BIG AMBER / ORANGE-BROWN EYES with highlights, clearly readable; a happy open GRIN (a little white of the teeth); the face turned to the front-right, looking STRAIGHT AHEAD (not up). THE CLOTHES: a short RED TUNIC with a TEAL stand-up collar and a TEAL round pendant on the chest; two BIG PUFFED GOLDEN-BRONZE SHOULDER PADS like rolled cloth, cream tassels at their ends (image 8); a wide TEAL SASH wrapped diagonally round his waist with a small gold buckle; below it a MAGENTA / PURPLE-RED pleated skirt-like kilt down to above the knees; bare BROWN shins; RED-AND-TEAL cloth WRAPS round the ankles; BROWN SANDALS. Both FISTS held together in front of his chest (image 1).
THE FIRE SPIRIT: a small ROUND glowing fireball buddy, about as big as the boy's head or a little smaller: a BRIGHT YELLOW-WHITE core, an ORANGE ring round it, a DEEP ORANGE-RED rim, a few little FLAME TIPS curling up from its top; a CUTE LITTLE FACE (two small dark eyes and a small happy mouth). It floats BEHIND the boy at SHOULDER HEIGHT on the image left (image 9), never covering his face or his hands, never touching the ground. Its outline is the same near-black outline as the boy's.
Pose: League's own idle (image 1), 3/4 FRONT view facing image right: his face turned to the front-right, chest toward the viewer; standing firm, feet a little apart: the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher, both sandals on the ground line.
Proportions: STOCKY and CHUNKY like images 10-12, NOT a tall slender realistic figure - a child: the head big (about one third of his height), the body about half as wide as he is tall (with the shoulder pads), slightly short legs. Keep the figure COMPACT.
Style: crisp chunky pixel art like images 10-12 - EVEN SQUARE PIXELS OF 10 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a TWO-SQUARE-THICK near-black outline around each figure, inside it every material in its own 3-4 flat shades, no stray single odd squares: the hair dark indigo-black with blue-violet lights, the skin warm brown, the eyes amber, the tunic red, the shoulder pads gold-bronze with cream tassels, the collar / pendant / sash teal, the kilt magenta-purple, the wraps red and teal, the sandals brown; the spirit yellow-white / orange / orange-red with dark eyes; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No other effects (no fireballs, no fire trails, no glow aura, no rings), no background, no ground, no shadow, no text, no frame, no other characters.
Then, from the SAME finished picture (do not redraw), save two layers on the same 1024x1536 canvas at the same positions: milio-model-B-boy.png (the boy only) and milio-model-B-spirit.png (the fire spirit only, any part hidden behind him completed in the same style).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，人物完整，不出画。
- 头：深靛蓝黑卷发、暖棕皮肤、**两只琥珀色大眼（看得清）**、咧嘴笑、**平视前方**（不是抬头）；头约占身高三分之一。
- 衣服：红上衣 + 青绿立领 + 青绿坠饰；**两块金色蓬起的肩垫 + 米白流苏**；青绿斜腰带 + 金扣；品红/紫红褶裙下摆；棕色小腿、红青绑腿、棕色凉鞋；双拳在胸前。
- B：圆圆的发光小火精灵（黄白芯、橙圈、橙红边、顶上小火苗、可爱小脸），在他背后肩膀高度、画面左边，**不挡脸和手**，不碰地面。
- 男孩从发顶到鞋底约 720 px（约 72 格，两版一样大）；敦实、偏 Q 版（像附图 10–12），不是细长的写实比例。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；鞋底在同一条水平线上；没有任何特效（B 的小火精灵除外）。
- **每块 10 像素、大小一致、对齐网格**；2 块宽的近黑外描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- B 的分层文件（`-boy` / `-spirit`）和成品图是同一张画、同一个位置。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述（提示词里本来就没写名字）。
- 全部画完后最后写 `outputs/milio-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把原画、分层和 raw/ 放进 `assets/source/milio/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 10 px），按它自己的格子读回（regrid / k-means 调色板后再投票，palette_of 直接用在原图上会全暗），和包里的英雄（league/*#sheet.png 的 hd_idle）并排给用户挑 A / B 和大小。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：**正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子）**两个视图，同一个高度、同一套格子、同样的细节（side-view-design）；原稿 1:1 按格读回，绝不先画大再缩。统一画风：PPU 约 2.2，描边约 1 游戏像素，敦实比例（ppu_restyle crisp）；大小用 hd.rs SIZES 调，不删躯干行。
- 同一张脸贯穿所有帧（one-face-all-frames）；跑步按 Caitlyn 的交叉步、直腿（run-legs-caitlyn-way）。若选 B，小火精灵在每一帧里是一整块（整体移动、不剪切），Q 的踢球 / W 的营火里的火精灵是第 3 步的特效。
