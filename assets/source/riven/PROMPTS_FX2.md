# 放逐之刃 锐雯：给 Codex 的补充包（特效补全 + 大招换剑）

> 上一次交付的 7 组特效（Q1、Q2 剑弧，Q3 地裂，E 护盾横扫，W 地面爆发，R 剑身绿光，疾风斩月牙）已经导入游戏，画风和颜色很好。这一包补两样东西：
> - **第一部分：9 个特效**（11 个 PNG）：普攻命中、符文普攻命中、Q 命中、疾风斩命中、击飞、眩晕、E 护盾、符文层数（3 个）、大招持续光环。
> - **第二部分：大招换剑**（7 个 PNG）：开大以后，她的断剑被绿色的符文能量补成完整的长剑（英雄联盟 R「放逐之锋」的样子）。游戏在开大期间播放这 7 条"大招版"动作：开大（第 3–6 帧）、疾风斩、普攻、Q 三段、E+W。
>
> 包里的文件：
> - `design/riven_native.png`：定稿造型（8 倍）。
> - `style/riven_fx_final.png`：你上次画的 7 组特效叠在她动作上的样子（导入后、去掉深色描边以后），**这次的画风、颜色、像素大小都照它**。
> - `strips/riven_<动作>.png`：现在游戏里的动作帧（8 倍，每个游戏像素一个 8×8 色块，96×96 格一帧）；`strips/riven_cells.json`：每帧的站位点和时长。第二部分从这些图改。
> - `guides/fx2_<名字>_guide.png`：第一部分每个特效的格子、站位点（蓝十字）、脚底线（红线）和特效套在谁身上（灰色人形，只是参考，不要画）。`guides/riven_<动作>_guide.png`：第二部分每条动作的格子、站位点、脚底线（红线以下的淡红区不能有像素）和脸（品红框，剑不能盖住）。
> - `refs/lol_fx_ref.png`：英雄联盟里锐雯自己的特效贴图（R 的绿光剑身 `sword_profile_glow`、符文 `glove_rune_quad` 等），只在本地用；`refs/blade_mock.png`：Claude 画的换剑示意（只看意思：断剑前面接一段绿色能量剑身，颜色按下面的色板）。
> - `fx2_cells.json`：第一部分每个特效的帧数、帧时长、格子大小和锚点（机器可读）。
>
> 交回：一个文件夹，`effects/` 放第一部分 11 个 PNG，`strips/` 放第二部分 7 个 PNG，文件名照下面写的；附 `HANDOFF.md`（每张画了什么、有没有没做到的）和 `manifest.json`（每个文件的帧数和格子）。

## 所有图的规则

- 像素画，**画在游戏原尺寸上**：每个游戏像素是一个 8×8 的纯色块（PNG 是游戏尺寸的 8 倍），硬边，透明度只有 0 和 255，没有抗锯齿、模糊和渐变光晕。
- 特效色板（和上次一样）：`#F6EADB`（最亮）、`#C9EF9A`、`#87D46A`、`#4BA85A`、`#2D6940`；`#183A2A` 只能用在图形**里面**当最深的阴影，**不能沿着图形描边**（上次每个图形外面都描了一圈 `#183A2A`，导入时已经去掉；特效是光，不是卡通物体，没有描边）。击飞的尘土和碎石可以用上次 Q3 用过的土石色 `#867469`、`#493328`。
- 背景透明。不要网格线、边框、文字、编号；参考图里的线和灰色人形不要画进去。
- 格子一行排开（第二部分照原图的排法），格子之间不留缝，每个格子都是写明的大小。

---

## 第一部分：9 个特效（11 个 PNG）

画风开头统一用这一段（每条的英文提示词前面都加上）：

```text
Pixel art game VFX for a small tactics game, drawn at the game's own size: every game pixel is one flat 8x8 block (the PNG is 8 times the game size), hard edges, alpha only 0 or 255, no anti-aliasing, no blur, no soft glow. Colours only from this palette: #F6EADB, #C9EF9A, #87D46A, #4BA85A, #2D6940 (and #183A2A only as the deepest shade INSIDE a shape, never as an outline around it). NO dark outline around the shapes. The same style, colours and pixel size as the attached riven_fx_final.png. Transparent background, no grid lines, no borders, no text; do not copy the guide's lines or grey figure.
```

### 1. `riven_fx_hit.png`：普攻命中（打在目标上半身），5 帧

断剑砍中目标：一道斜着的亮白斩痕，几点碎光。格子 24×24，斩痕中心在格子正中（游戏里放在目标胸口）。

```text
Effect: a BASIC SWORD HIT, 5 frames (50, 50, 60, 60, 80 ms), centred on the middle of every cell: 1 a short 1-pixel diagonal cut (upper left to lower right) of #F6EADB through the centre; 2 the cut at full length (about 14 pixels), 2 pixels thick, a #F6EADB core with #C9EF9A edges, a small plus-shaped flash at its middle; 3 the cut breaks into 3-4 short dashes, 4-6 single-pixel sparks flying outward; 4 the dashes fade to #87D46A and #4BA85A, the sparks further out; 5 a few #4BA85A and #2D6940 specks.
Layout: one row of 5 cells, each 24x24 game pixels (192x192 px), image 960x192.
```

### 2. `riven_fx_rune_hit.png`：用掉一层符文的普攻命中，6 帧

比普通命中大：一道白绿色的弯斩，再交叉一道绿斩成 X，炸出几块小方形符文。格子 32×32，中心在格子正中。

```text
Effect: a RUNIC BLADE HIT, 6 frames (50, 50, 60, 60, 70, 80 ms), centred on the middle of every cell: 1 a small green-white spark at the centre; 2 a thick crescent slash (#F6EADB core, #C9EF9A and #87D46A rim) cuts diagonally through the centre, about 20 pixels long; 3 a second slash (#87D46A, #4BA85A) crosses it, making an X, a #F6EADB flash where they cross; 4 three or four small square rune glyphs (4-5 pixels, #C9EF9A with #4BA85A strokes) burst out of the X toward the corners; 5 the slashes fade to #4BA85A, the glyphs further out and dimmer (#87D46A); 6 faint #2D6940 specks.
Layout: one row of 6 cells, each 32x32 game pixels (256x256 px), image 1536x256.
```

### 3. `riven_fx_q_hit.png`：Q 斩中的每个敌人，5 帧

一道横的白色斩痕加一点绿边，火星上下迸开。格子 24×24，中心在格子正中。

```text
Effect: a SLASH IMPACT, 5 frames (50, 50, 60, 70, 80 ms), centred on the middle of every cell: 1 a thin horizontal #F6EADB cut through the centre, 1 pixel thick, about 8 pixels long; 2 the cut at full width (about 16 pixels), 2 pixels thick, a #F6EADB flash in the middle, a #87D46A rim; 3 #F6EADB and #C9EF9A sparks burst up and down from the cut; 4 the cut breaks into short #87D46A and #4BA85A dashes, the sparks fading; 5 two or three #2D6940 specks.
Layout: one row of 5 cells, each 24x24 game pixels (192x192 px), image 960x192.
```

### 4. `riven_fx_r_hit.png`：疾风斩打中，6 帧

一道竖的月牙切痕，炸成一团白绿的光，左右飞出绿色风痕。格子 32×32，中心在格子正中。

```text
Effect: a WIND SLASH IMPACT, 6 frames (50, 60, 60, 70, 80, 90 ms), centred on the middle of every cell, symmetric above and below the middle row: 1 a bright #F6EADB point at the centre; 2 a vertical crescent cut (convex to the right, #F6EADB core, #87D46A edges) through the centre, about 20 pixels tall; 3 it bursts into a round flash about 18 pixels wide, #C9EF9A and #87D46A round a #F6EADB core; 4 green wind streaks (#87D46A, #4BA85A, 1-2 pixels thick, 6-10 pixels long) fly out to the left and right; 5 the streaks thin and fade; 6 faint #2D6940 specks.
Layout: one row of 6 cells, each 32x32 game pixels (256x256 px), image 1536x256.
```

### 5. `riven_fx_knockup.png`：被 Q 第三段击飞的目标（0.75 秒），6 帧

目标脚下卷起一圈旋风尘土，碎石往上飞。格子 48×48，目标的站位点在格子的 (24, 32)，脚底线在第 43 行；目标约 36 格高（参考图里的灰色人形，不要画）。中间留给目标的身体。

```text
Effect: a KNOCK-UP DUST SWIRL round a standing unit (shown grey in the guide - do NOT draw it; its standing point is at (24, 32) of each 48x48 cell, its feet on row 43, its head top near row 7), 6 frames (100, 120, 130, 130, 130, 140 ms): 1 a dust puff bursts on the ground at the feet, a flat ellipse about 24x6 centred on (24, 43), #F6EADB, #C9EF9A and #867469; 2 two curved wind streaks (#F6EADB, #C9EF9A, 1 pixel) spiral up from it round the legs, small rocks (#867469, #493328, 1-2 pixels) flying up at both sides; 3 the streaks reach the waist (row 30), the rocks higher at the sides (up to row 12); 4 the streaks thin, the rocks at their highest; 5 the streaks break into wisps, the rocks falling; 6 faint dust at the feet. Keep the unit's body clear (columns 16-32 above row 28: only thin streaks may cross), never over its head.
Layout: one row of 6 cells, each 48x48 game pixels (384x384 px), image 2304x384.
```

### 6. `riven_fx_stun.png`：被 W 眩晕的目标头顶（0.75 秒），6 帧循环

一圈扁的绿色光环，上面三块小方形符文和两颗小白星在转。格子 24×12，光环中心在格子正中（游戏里放在目标头顶上方）。

```text
Effect: a STUN RING over a head, 6 frames (125 ms each), one seamless loop (frame 6 flows into frame 1), centred on the middle of every cell: a flat ellipse of light about 20x7 pixels (a 1-pixel #87D46A line), three small square rune glyphs (3x3, #C9EF9A with a #2D6940 centre) and two tiny 4-point stars (#F6EADB) spaced round it, everything turning one sixth of a circle each frame; the glyphs and stars on the front (lower) half brighter, the back half dimmer (#4BA85A).
Layout: one row of 6 cells, each 24x12 game pixels (192x96 px), image 1152x96.
```

### 7. `riven_fx_shield.png`：E 勇往直前的护盾（套在锐雯身上，护盾在时一直播，最长 1.5 秒），8 帧

五块带符文的淡绿色碎片绕着她腰转一圈。第 1–2 帧出现，第 3–6 帧循环，第 7–8 帧碎开。格子 48×56，她的站位点在 (24, 40)，脚底线第 51 行（参考图里灰色的锐雯，不要画）。碎片只能从腿前面经过，不能盖住胸口、头和脸。

```text
Effect: a RUNE SHARD SHIELD round Riven (shown grey in the guide - do NOT draw her; her standing point is at (24, 40) of each 48x56 cell, her feet on row 51, her head top on row 6, her face about rows 15-24 with the eyes on rows 19-20, her broken sword to the right), 8 frames: frames 1-2 appear (60, 60 ms), frames 3-6 one seamless loop (100 ms each, frame 6 flows into frame 3), frames 7-8 break (70, 90 ms). Five angular rune shards (flat plates about 5x7 pixels, #C9EF9A and #87D46A with a #F6EADB glyph stroke and a #2D6940 inner shade) orbit her waist (row 36) in a tilted ellipse about 44x12, joined by a thin broken #87D46A arc (not a full outline): 1 the shards appear small at her feet; 2 they rise to the waist; 3-6 they orbit a fifth of a turn each frame - shards on the front (lower) half of the ellipse may pass over her legs, but columns 14-34 above row 28 stay clear (never over her chest, head or face); 7 the shards crack into halves; 8 small green fragments falling.
Layout: one row of 8 cells, each 48x56 game pixels (384x448 px), image 3072x448.
```

### 8. `riven_fx_rune_1.png`、`riven_fx_rune_2.png`、`riven_fx_rune_3.png`：符文层数（有符文时浮在她头顶），各 4 帧循环

被动「符文之刃」的层数：有几层就在她头顶亮几块小符文（游戏里 1、2、3 从左到右排成一排）。三个文件画三种**不同**的符文字，大小和画风一样。格子 12×12，符文在格子正中。

```text
Effect: a small FLOATING RUNE GLYPH, 4 frames (150 ms each), one seamless loop, centred on the middle of every cell: one squarish rune sign about 5x6 pixels (strokes of #C9EF9A and #F6EADB on a #4BA85A plate with a #2D6940 inner shade), bobbing 1 pixel up and down, single #87D46A pixels round it pulsing brighter and dimmer, one spark drifting off. Draw a DIFFERENT sign in each of the three files (like three letters of one rune alphabet), the same size and style.
Layout (each file): one row of 4 cells, each 12x12 game pixels (96x96 px), image 384x96.
```

### 9. `riven_fx_r_aura.png`：放逐之锋持续中（画在她身后，开大 15 秒一直循环），6 帧

脚下一圈淡绿的光环和符文，身体两边往上飘绿色光点和小剑形的光。这一层画在她**后面**（落在身体上的像素会被她挡住），所以动的东西放在她两边。格子 56×64，站位点 (28, 46)，脚底线第 57 行。

```text
Effect: a RUNIC AURA round Riven, drawn BEHIND her (shown grey in the guide - do NOT draw her; her standing point is at (28, 46) of each 56x64 cell, her feet on row 57), 6 frames (100 ms each), one seamless loop (frame 6 flows into frame 1): a faint ground ellipse about 40x10 centred on (28, 57) - a 1-pixel #4BA85A ring with a few #87D46A glints and a tiny square rune glyph at four points of it; green sparks (single #87D46A and #C9EF9A pixels) and tiny sword-shaped glints (1x4 pixels, #C9EF9A with a #F6EADB tip) rising along both sides of her (columns 6-18 and 38-50), each frame 3-4 pixels higher, new ones appearing at the ground, the old ones fading out near row 4.
Layout: one row of 6 cells, each 56x64 game pixels (448x512 px), image 2688x512.
```

---

## 第二部分：大招换剑（7 个 PNG）

英雄联盟里开大以后，锐雯的断剑被绿色的符文能量补成一把完整的长剑（参考 `refs/lol_fx_ref.png` 里的 `sword_profile_glow`，意思见 `refs/blade_mock.png`）。游戏在开大的 15 秒里播放下面这 7 条动作。站着和跑步是引擎自己播的，换不了，那时是断剑加第 9 个特效的光环。

规则（每条都一样）：
- **从 `strips/` 里对应的图开始改，只改剑**：图的大小、格子、帧数、排法都不变；她的身体、头、脸、头发、衣服、描边和颜色一个像素都不动。
- **重铸的剑**：断剑本身（灰色的碎块、绑带）照旧，断掉的那一截由绿色符文能量补上：顺着剑身的方向直着接出去，和剑身一样宽，比断剑长约 12 格（整把剑约是断剑的 1.5 倍），末端是尖的；外缘 `#2D6940`，剑身 `#4BA85A`、`#87D46A`，中间一条 `#C9EF9A` / `#F6EADB` 的亮线；碎块之间的缝透出 `#87D46A` 的光。能量剑身没有黑描边。
- **硬性要求**：红线（脚底线）以下什么都不能有，变长的剑如果会伸到红线以下，这一帧就抬高一点角度或短一点；剑不能盖住她的脸（参考图里的品红框）；不能超出每帧 96×96 的格子。原图里剑被身体挡住或正对镜头的帧，照原图露出的部分画，不要凭空多画一把剑。

```text
Redraw of an existing pixel-art animation strip: copy the attached strip EXACTLY - the same image size, cells, frames and layout, every pixel of the character's body, head, face, hair, clothes, outline and colours unchanged - and change ONLY her sword. The sword becomes the reforged Blade of the Exile: her broken blade stays as it is (the grey fragments and bindings), and the missing part is completed by a blade of green rune energy that continues straight on from the broken end, as wide as the blade, about 12 game pixels longer (the whole sword about 1.5 times the broken one), ending in a sharp point: a #2D6940 rim, a #4BA85A and #87D46A body, a #C9EF9A / #F6EADB bright line along its middle; the gaps between the fragments glow #87D46A. No black outline on the energy blade. Every game pixel one flat 8x8 block, alpha only 0 or 255, no anti-aliasing. NOTHING below the red feet line of the guide (angle the blade up or shorten it in that frame if needed), the blade never covers her face (the magenta box of the guide), nothing outside each 96x96 cell. Where the original frame hides the sword behind her body or shows it end-on, draw only what shows.
```

| 交回的文件 | 从哪张改 | 改哪几帧 |
|---|---|---|
| `riven_ult.png` | `strips/riven_ult.png`（开大，6 帧） | 第 1–2 帧不动（还是断剑）；第 3–6 帧换成重铸的剑，第 3 帧是剑成形的一刻，剑身周围多 3–5 点 `#C9EF9A` 火星 |
| `riven_r_slash.png` | `strips/riven_r_slash.png`（疾风斩，6 帧） | 全部 6 帧 |
| `riven_attack_r.png` | `strips/riven_attack.png`（普攻，6 帧） | 全部 6 帧 |
| `riven_skill_r.png` | `strips/riven_skill.png`（Q 第一段，7 帧） | 全部 7 帧 |
| `riven_q2_r.png` | `strips/riven_q2.png`（Q 第二段，7 帧） | 全部 7 帧 |
| `riven_q3_r.png` | `strips/riven_q3.png`（Q 第三段，7 帧） | 全部 7 帧 |
| `riven_skill2_r.png` | `strips/riven_skill2.png`（E+W，8 帧） | 全部 8 帧 |

---

## Claude 导入时的对应关系（给 Claude 看）

- 第一部分：`tools/art/import_riven.py` 读 `effects/`（检查 8×8 色块、硬透明、色板，去掉沿边的 `#183A2A`），按 `fx2_cells.json` 的锚点切帧写进 `league/effects/league_riven_fx`：命中类放在目标站位点上方 8 格（`view_effects` hit / rune_hit / q_hit / r_hit），击飞按目标站位点（knockup），眩晕放在目标站位点上方 28 格（stun），护盾是护盾 buff 的三段（`view_buffs` ThreePhase e_shield，z 1），符文 1–3 放在她站位点上方 40 格、左中右三个位置（`view_buffs` rune_1..rune_3），光环是 R buff 的循环（z −1）。
- 第二部分：`tools/art/tidy_riven.py` 同样检查（头和定稿一致、只有剑变了、脚底线），写进 `assets/source/native/`；`riven_cells.json` 加 `*_r` 标签（格子和时长照原动作）；`import_native.py --hero riven`。技能里开大期间（R buff 在时）普攻、Q 三段、E+W 改播 `*_r` 动作。
