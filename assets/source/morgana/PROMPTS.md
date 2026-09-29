# 堕落天使 莫甘娜：给 Codex 的特效提示词

> **这一份是 11 张特效图。** 模型和 8 个动作已经做完（造型 B，`MODEL_PROMPTS.md`，已导入游戏），这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里莫甘娜自己的特效贴图（Q 的紫蓝星形弹核和锁链拖尾、W 的暗紫焦油地面和洋红碎光、E 的紫蓝护盾环和六边形纹、R 的锁链、爆环和眩晕法阵），只在本地用，不要提交。颜色和画风对照 `design/morgana_native.png`（定稿造型，8 倍）；大小对照 `design/morgana_ingame.png`（游戏里的 50 帧，4 倍，绿线是脚底和站位）：莫甘娜从羽冠到脚底 45 格，其他英雄约 35 格。
> - 特效照下面第 1–11 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_morgana.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「灵魂吸取」 | 射出一团暗影弹；技能伤到英雄时按伤害的约 15% 回血 | `morgana_fx_bolt` · `morgana_fx_hit` |
| 技能 1 = Q「暗之禁锢」+ W「折磨之影」 | 射出暗影弹核，穿过小兵和野怪（沿途造成伤害），停在第一个敌方英雄身上并禁锢 2 秒；每 12 秒同时在他脚下留下一片暗影焦油地，4 秒内持续伤害 | `morgana_fx_q_orb` · `morgana_fx_q_hit` · `morgana_fx_q_bind` · `morgana_fx_w_pool` |
| 技能 2 = E「黑暗之盾」 | 给身边一名友方英雄（没有就自己）套上黑暗护盾，5 秒，护盾在时免疫控制 | `morgana_fx_e_shield` |
| 大招 = R「灵魂镣铐」 | 用锁链锁住身边所有敌方英雄（伤害 + 减速），3 秒后锁链崩断，仍在附近的敌人再受伤害并被眩晕 1.5 秒 | `morgana_fx_r_cast` · `morgana_fx_r_hit` · `morgana_fx_r_chain` · `morgana_fx_r_snap` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（四套，按每条写的用）：
  - 暗影紫（普攻、Q、R 的主体）：`#FFFFFF`、`#EAD6FF`、`#B478F0`、`#7A3AD0`、`#4A1C90`、`#24104A`；
  - 冰蓝点缀（Q 的弹核、E 护盾的下沿）：`#FFFFFF`、`#A8FAFF`、`#40C8EC`、`#2466C8`；
  - 洋红（W 的碎光、R 的锁链光）：`#FFD0F2`、`#FF6AD8`、`#D02CA8`、`#7A1060`；
  - 焦油黑紫（W 的地面、R 的阴影）：`#3A1A4E`、`#24102F`、`#12081A`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- 命中、爆开、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（禁锢、护盾、锁链、眩晕）：格子中间留出一个空的人形位置（约 18 格宽、34 格高，脚在格子下方），不要画人，**不能挡住身体和脸**，只画套在外面的环、链和光。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（11 张）

11 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `morgana_fx_bolt.png`：普攻的暗影弹（飞行），4 帧循环

一团暗紫色的魔法弹：前端是白紫色的亮核，外面裹着紫色火舌，后面拖一条渐暗的紫色尾巴。约 12 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90, #24104A).
Effect: a DARK MAGIC BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white-violet core (a small round orb) at 80% of the cell width, wrapped in violet flame tongues, a tapering tail of violet and dark violet wisps streaming to the left behind it over 70% of the cell width, the wisps flickering differently in each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the bolt on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `morgana_fx_hit.png`：普攻命中，5 帧

暗影弹打中目标：一团紫色的暗影炸开，几缕黑紫色烟丝散开。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90, #24104A).
Effect: a SHADOW MAGIC IMPACT, 5 frames: 1 a small white-violet point at the center; 2 a round burst of violet energy about 40% of the cell wide, white core; 3 the burst at full size, dark violet smoke curls spreading out of it; 4 the burst gone, the smoke curls drifting outward and darkening; 5 a few faint dark violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `morgana_fx_q_orb.png`：暗之禁锢的弹核（飞行），4 帧循环

Q 射出的弹：一颗星形的紫蓝色能量球（参考 `lol_fx_ref.png` 的 Q_Mis_Core：冰蓝色的核，外面一圈紫色的尖刺光），后面拖一条紫色的锁链状能量尾（参考 Q_ChainTrail）。约 24 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90) with an icy cyan core (#FFFFFF, #A8FAFF, #40C8EC).
Effect: a DARK BINDING ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round orb at 75% of the cell width with a bright cyan-white core, surrounded by a ring of sharp violet spikes of light (like a spiky star, turning a little each frame); behind it a trail shaped like a chain of violet energy links (small diamond links joined in a row) streaming to the left edge of the cell, fading to dark violet, with a few violet sparks.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the orb on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `morgana_fx_q_hit.png`：弹核穿过小兵、野怪时的命中，5 帧

弹核擦过的单位身上：一道紫白色的星芒闪光（参考 Q_Impact_Flare），几点碎光。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90) with a touch of cyan (#A8FAFF).
Effect: a PIERCING SHADOW FLARE, 5 frames: 1 a thin white-violet diagonal streak through the center; 2 a sharp four-pointed star flash, white core, violet points, about 50% of the cell wide; 3 the star at full size with small violet sparks flying off; 4 the star shrinks into a small violet cross, the sparks fade to dark violet; 5 two faint dark violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the flash centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `morgana_fx_q_bind.png`：禁锢（套在被定住的英雄身上，2 秒），9 帧

被 Q 定住的英雄：脚下一个紫色的发光圆环，三道暗影锁链从地面缠上来，绕着他的腿和腰转，锁链上有冰蓝色的亮点（参考 Q_Tar_ChainScroll、R_tar_snare）。第 1–3 帧锁链缠上来，第 4–7 帧循环（导入时重复到 2 秒），第 8–9 帧消散。约 26 格宽、30 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90, #24104A) with icy cyan glints (#A8FAFF, #40C8EC).
Effect: DARK SHACKLES binding a standing figure (leave a figure-shaped empty space in the middle of the cell, about 60% of the cell width and 80% of the cell height, feet at 85% of the cell height - do NOT draw the figure), 9 frames: 1 a glowing violet ring appears flat on the ground at the feet (an ellipse twice as wide as tall); 2 three dark violet energy chains of small diamond links shoot up from the ring; 3 the chains wrap around the empty figure's legs and waist in diagonal bands, bright cyan glints on the links; 4-7 a seamless loop: the chains pulse and their links shift one step each frame, violet wisps rise from the ring; 8 the chains crack into loose links; 9 faint dark violet links and specks fading.
Layout: one horizontal row of 9 equal cells, each 4 wide to 5 tall, image size 2304x320 (each cell 256x320); the ring centered horizontally at 85% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `morgana_fx_w_pool.png`：折磨之影（地面，4 秒），8 帧

被禁锢的英雄脚下铺开一片暗紫色的焦油地（参考 W_Tar_Ground：黑紫色的碎块地面上有洋红色的裂光），边缘冒着黑紫色的烟，中间有洋红色的碎光和一个缓缓转动的暗影漩涡往上飘。第 1–2 帧铺开，第 3–6 帧循环（导入时重复到 4 秒），第 7–8 帧收缩消失。约 48 格宽、24 格高的椭圆。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a tar ramp (#3A1A4E, #24102F, #12081A) with magenta glow (#FFD0F2, #FF6AD8, #D02CA8, #7A1060) and violet wisps (#B478F0, #7A3AD0).
Effect: a CURSED POOL OF SHADOW on the ground, 8 frames: 1 a small dark ellipse of black-violet tar appears at the center (an ellipse twice as wide as tall); 2 it spreads to 90% of the cell width, its surface broken into dark cracked plates with glowing magenta cracks between them; 3-6 a seamless loop: the magenta cracks pulse brighter and darker, small magenta sparks and dark violet smoke wisps rise from the pool in different places each frame, a faint dark swirl turns in the middle; 7 the pool shrinks, the cracks dim; 8 a small fading dark patch with two magenta specks.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 2048x128 (each cell 256x128); the pool centered in every cell, the rising wisps may reach the top of the cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `morgana_fx_e_shield.png`：黑暗之盾（套在友方英雄身上，最长 5 秒），10 帧

一个暗紫色的护盾球罩住英雄（参考 E_Shield_RingBurnOff_Colored：紫色的圆环、下沿泛蓝；E_Shield_UpperHexagon：顶上一圈六边形纹）：只画球的外圈（2–3 格厚的紫色描边环，下沿冰蓝）、顶上一圈小六边形纹和几缕黑紫色的烟，中间留空，看得见里面的人。第 1–3 帧护盾从脚下升起合拢（出现），第 4–7 帧循环（护盾在的时候一直播），第 8–10 帧护盾碎开消失。约 34 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#EAD6FF, #B478F0, #7A3AD0, #4A1C90, #24104A) with an icy blue lower rim (#A8FAFF, #40C8EC, #2466C8).
Effect: a BLACK SHIELD sphere around a standing figure (leave the inside of the sphere EMPTY so the figure shows through - do NOT draw the figure or fill the sphere), 10 frames: 1 a flat violet ring on the ground at the feet (an ellipse); 2 the ring rises into the lower half of a sphere, dark violet smoke curling up its sides; 3 the sphere closes over the top: a violet outline ring 2-3 squares thick, its lower edge glowing icy blue, a small band of hexagon links across its top; 4-7 a seamless loop: the sphere holds, a bright glint slides around the ring a quarter turn each frame, the hexagons and a few dark smoke wisps flicker; 8 the ring cracks into curved shards; 9 the shards fly outward; 10 faint violet specks fading.
Layout: one horizontal row of 10 equal cells, each 5 wide to 6 tall, image size 3200x384 (each cell 320x384); the sphere centered horizontally, its bottom at 90% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `morgana_fx_r_cast.png`：灵魂镣铐出手（她脚下的地面），7 帧

她张开双臂的一刻，从她身上炸开一圈暗紫色的冲击环贴着地面向外扩散到大招的范围（参考 R_Cas_BurstRing：一圈向外的尖刺光；R_Donut_normal：紫蓝色的圆环），环上有锁链的影子，地上留下一圈暗影。约 100 格宽、50 格高的椭圆（大招半径约 50000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90, #24104A) with magenta glints (#FF6AD8, #D02CA8).
Effect: SOUL SHACKLES BURST on the ground around the caster (the caster stands at the center - leave a small empty space for her feet), 7 frames: 1 a bright violet flash at the center; 2 a flat ring of violet light (an ellipse twice as wide as tall) bursts outward to 40% of the cell width, spiky rays of light pointing outward along its edge; 3 the ring at 70%, dark chain-link shapes running around it; 4 the ring at 95% of the cell width, thinner, magenta glints on its links; 5 the ring fades to dark violet, a dim shadow circle left on the ground inside it; 6 broken dark ring segments; 7 the last faint specks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `morgana_fx_r_hit.png`：锁链扣上敌人，5 帧

每个被锁住的敌方英雄身上：一段暗紫色的锁链甩过来扣在他身上，紫色的闪光。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90) with magenta glints (#FF6AD8, #D02CA8).
Effect: a SHADOW CHAIN LATCHING onto an enemy, 5 frames: 1 a short dark violet chain of diamond links whips in from the left edge toward the center; 2 its end snaps shut at the center with a bright violet-white flash; 3 the flash spreads into a ring of violet sparks, the chain glowing magenta; 4 the chain dims, the sparks fly out; 5 faint dark violet links fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the latch point centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `morgana_fx_r_chain.png`：被锁住的敌人身上的锁链（3 秒循环），4 帧

被锁住的敌人：一圈暗紫色的锁链绕在他腰上，一段锁链从腰上向左后方垂出去（像连着莫甘娜），锁链发着洋红色的光，时亮时暗（参考 R_ChainGlow、R_Chains_Inverse）。4 帧循环。约 30 格宽、30 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#EAD6FF, #B478F0, #7A3AD0, #4A1C90, #24104A) with magenta glow (#FFD0F2, #FF6AD8, #D02CA8).
Effect: a SOUL CHAIN on a standing figure (leave a figure-shaped empty space in the middle of the cell, about 60% of the cell width and 85% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: a ring of dark violet chain links around the figure's waist (an ellipse, the front links in front of the empty figure, the back links behind), and one length of chain hanging from the ring out to the left edge of the cell, pulled taut; magenta light runs along the links, shifting one link each frame; a few violet wisps rise from the ring.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the ring centered horizontally at 55% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `morgana_fx_r_snap.png`：锁链崩断 + 眩晕（1.5 秒），8 帧

3 秒后锁链崩断：一道紫白色的闪光炸开，锁链碎成几段飞散；然后被眩晕的敌人头顶转着一圈暗紫色的小星和法阵光（参考 R_Stun_Circle：一个带四个尖角的圆形法阵）。第 1–3 帧崩断，第 4–7 帧眩晕循环（导入时重复到 1.5 秒），第 8 帧消失。约 32 格宽、40 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a shadow-violet ramp (#FFFFFF, #EAD6FF, #B478F0, #7A3AD0, #4A1C90) with magenta glints (#FF6AD8, #D02CA8).
Effect: SHACKLES SNAP and STUN on a standing figure (leave a figure-shaped empty space in the middle of the cell, about 55% of the cell width and 75% of the cell height, feet at 90% of the cell height - do NOT draw the figure), 8 frames: 1 a bright violet-white flash bursts at the figure's waist; 2 the flash spreads into a ring, broken chain links flying outward in all directions; 3 the links scatter and fade, violet sparks; 4-7 a seamless loop above the figure's head (at 12% of the cell height): a small flat ornate circle of violet light with four sharp points (an ellipse, like a magic sigil) turning a quarter each frame, three small violet stars circling on it; 8 the sigil fades to a few specks.
Layout: one horizontal row of 8 equal cells, each 4 wide to 5 tall, image size 2048x320 (each cell 256x320); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

- `tools/art/import_morgana.py --raw <交付文件夹>`：按 `manifest.json` 或等宽格子切帧，按技能范围缩放（Q 弹核半径 7000、W 地面半径 22000、R 半径 50000、人物约 35 像素高，莫甘娜 45），合成 `league/effects/league_morgana_fx`（小特效）和 `league_morgana_big`（W 地面、R 爆环）两张图集；禁锢、W 地面、护盾、眩晕的循环帧重复到各自的时长（2 秒、4 秒、护盾循环、1.5 秒）。
- 视图绑定在 `league_morgana.data_champion`：`view_projectiles` bolt / q_orb；`view_effects` hit / q_hit / q_bind / w_pool / r_cast / r_hit / r_snap；`view_buffs` e_shield（三段：e_shield_in / e_shield / e_shield_out）、r_chain。
