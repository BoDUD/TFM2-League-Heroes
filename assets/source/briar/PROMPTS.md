# 贝蕾亚：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型（B 版）和 10 个动作已经做完并导入游戏，这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里贝蕾亚自己的特效贴图（普攻的焦油飞溅、狂热的血色爪痕、噬击的獠牙、惊吼的能量波、毙除的血石和爆炸、落地的符文），只在本地用，不要提交。颜色和画风对照 `design/briar_design.png`（定稿造型，8 倍）；大小对照 `design/briar_ingame.png`（游戏里的全部帧，4 倍，绿线是脚底和站位）：贝蕾亚从宝石顶到脚底 46 格，其他英雄约 35 格。
> - 特效照下面第 1–15 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「猩红诅咒」 | 扑咬；命中叠流血（游戏自带流血图标，不用画） | `briar_fx_hit` |
| 技能 1 = Q「冲头」+ W「血莽」「噬击」 | 扑向目标头槌，眩晕并降低护甲魔抗；落地进入血莽 5 秒（攻速、移速、普攻溅射）；2 秒后的一口噬击加伤害并回血 | `briar_fx_q_hit` · `briar_fx_frenzy` · `briar_fx_snack` · `briar_fx_snack_heal` |
| 技能 2 = E「惊吼」 | 蓄力 1 秒（减伤、回血），向前尖啸：伤害、减速、击退，被击退的英雄眩晕 1 秒 | `briar_fx_e_guard` · `briar_fx_e_wave` · `briar_fx_e_hit` · `briar_fx_e_stun` |
| 大招 = R「毙除」 | 踢出血石，标记第一个命中的英雄为猎物，飞过去落地爆炸，恐惧其他敌人，进入彻底血狂 6 秒 | `briar_fx_r_gem` · `briar_fx_r_mark` · `briar_fx_r_boom` · `briar_fx_r_hit` · `briar_fx_r_fear` · `briar_fx_hema` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（三套，按每条写的用）：
  - 血红（主体）：`#FFFFFF`、`#FFD0DA`、`#FF4A6E`、`#D81E48`、`#9A0E32`、`#5A061E`；
  - 焦油黑红（暗部、烟、地面）：`#3A0A1A`、`#22060F`、`#120308`；
  - 骨白獠牙和冰白（噬击的牙、惊吼的声波亮边）：`#FFFFFF`、`#F4ECE4`、`#CFC4BE`、`#EAF6FF`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- 命中、爆开、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（血莽、血狂、蓄力、眩晕、恐惧、猎物标记）：格子中间留出一个空的人形位置（约 20 格宽、36 格高，脚在格子下方），不要画人，**不能挡住身体和脸**，只画围在外面的光、烟和符号。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `briar_fx_hit.png`：普攻命中，5 帧

扑咬打中目标：一道血红的弧形爪痕（参考 BA_Frenzy_Swipe），接着一团黑红色的焦油飞溅（参考 BA_Impact_TarSplash）。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with black-red tar (#3A0A1A, #22060F).
Effect: a FERAL BITE IMPACT, 5 frames: 1 a thin bright crimson curved slash across the center from upper left to lower right; 2 the slash at full size (about 60% of the cell wide), white-pink core, a round splash of black-red tar bursting from its middle; 3 the tar splash spreads into spiky droplets flying outward, the slash fading; 4 the droplets fly further and darken; 5 a few small dark red specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `briar_fx_snack.png`：噬击（大口咬），6 帧

2 秒血莽后的那一口：一张血红的大嘴虚影从上下合拢——上下两排骨白色的尖牙（参考 W_Bite_Tar、W_Bite_Tar_Shockwave）"咔"地咬住，咬合处爆出血红的飞溅。约 24 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E), bone-white fangs (#FFFFFF, #F4ECE4, #CFC4BE) and black-red tar (#3A0A1A, #22060F).
Effect: a GHOSTLY BITE, 6 frames: 1 two rows of sharp bone-white fangs appear far apart, the upper row near the top of the cell, the lower row near the bottom, each row on a curved band of dark crimson (like open jaws seen from the front); 2 the jaws move halfway toward each other; 3 the jaws snap shut at the middle, a bright white-pink flash where the fangs meet; 4 a burst of crimson blood droplets and black-red tar sprays out sideways from the bite; 5 the jaws fade, the droplets fly outward; 6 a few dark red specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `briar_fx_snack_heal.png`：噬击回血（在她身上），5 帧

咬中后她身上冒起血红色的回血光点和一个小十字，往上飘。约 20 格宽、30 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32).
Effect: a BLOOD HEAL rising around a standing figure (leave a figure-shaped empty space in the middle, about 60% of the cell width and 80% of the cell height - do NOT draw the figure), 5 frames: 1 small crimson motes appear around the empty figure's waist; 2 the motes rise, a small bright pink-white plus sign appears beside the figure's shoulder; 3 the motes and the plus sign rise higher, glowing; 4 they reach the figure's head height and fade to dark red; 5 a few faint specks.
Layout: one horizontal row of 5 equal cells, each 2 wide to 3 tall, image size 1280x384 (each cell 256x384); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `briar_fx_q_hit.png`：冲头撞中（眩晕 0.5 秒），6 帧

头槌撞到目标：一个白色的星形闪光（参考 Q_BlastShapes 的尖刺），外面一圈血红的冲击波，然后目标头顶转着两颗血红的小星（眩晕）。约 24 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E).
Effect: a HEADBUTT IMPACT then a short daze, 6 frames: 1 a sharp white four-pointed star flash at 55% of the cell height; 2 the star with spiky white-pink rays, a round crimson shock ring around it; 3 the ring spreads to 80% of the cell width and thins, crimson chips flying out; 4 the ring fades; 5-6 (a loop) two small crimson stars circling on a flat ring at 15% of the cell height (above a head).
Layout: one horizontal row of 6 equal cells, each 6 wide to 7 tall, image size 1440x280 (each cell 240x280), centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `briar_fx_frenzy.png`：血莽（在她身上，5 秒），4 帧循环

进入血莽时她全身冒着血红色的狂热气焰：从脚下往上飘的血红火舌和黑红焦油烟丝，围着身体两侧（参考 BA_Frenzy_Swipe 的颜色），**不挡脸和胸口**。4 帧循环。约 30 格宽、44 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with black-red tar smoke (#3A0A1A, #22060F).
Effect: a BLOOD FRENZY AURA around a standing figure (leave a figure-shaped empty space in the middle of the cell, about 60% of the cell width and 80% of the cell height, feet at 92% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: crimson flame tongues and black-red smoke wisps rise along both sides of the empty figure from the feet to the shoulders, a flat crimson glow ring on the ground at the feet (an ellipse); the flames flicker to new shapes each frame; nothing crosses the middle of the figure.
Layout: one horizontal row of 4 equal cells, each 2 wide to 3 tall, image size 1024x384 (each cell 256x384); the ground ring centered horizontally at 92% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `briar_fx_hema.png`：彻底血狂（在她身上，6 秒），4 帧循环

毙除后的血狂：比血莽更浓——血红的火舌更高、更亮，脚下一圈暗红的符文光环（参考 R_RuneDecal），身边飘着几缕黑红色的血丝触须（参考 R_BerserkTar）。4 帧循环。约 36 格宽、48 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with black-red tar (#3A0A1A, #22060F, #120308).
Effect: a HEMOMANIA AURA around a standing figure (leave a figure-shaped empty space in the middle of the cell, about 55% of the cell width and 75% of the cell height, feet at 92% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: tall bright crimson flame tongues rise along both sides of the empty figure up to above its head, a jagged ring of dark crimson rune marks on the ground at the feet (a flat ellipse), three thin black-red tendrils curling in the air around the figure; the flames and tendrils move each frame; nothing crosses the middle of the figure.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 1152x384 (each cell 288x384); the ground ring centered horizontally at 92% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `briar_fx_e_guard.png`：惊吼蓄力（在她身上，1 秒，减伤），4 帧循环

蓄力时她身前聚起一团暗红的能量，嘴边一圈白色的光在收紧（参考 E_Mouth_Charge），身体外面一层薄薄的暗红护罩。4 帧循环。约 30 格宽、40 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with white (#FFFFFF, #EAF6FF).
Effect: a CHARGING SCREAM around a standing figure (leave a figure-shaped empty space in the middle of the cell, about 60% of the cell width and 80% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: a thin dark crimson shell outline around the empty figure (2 squares thick, broken into arcs); crimson energy motes drawn inward from the edges of the cell toward a point at the figure's mouth height on its right side (at 40% of the cell height, 65% of the cell width), where a small white ring pulses smaller each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 1152x384 (each cell 288x384); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `briar_fx_e_wave.png`：惊吼声波（向前），5 帧

向前尖啸：一道道弧形的血红声波从左边（她的嘴）向右扩散成扇形（参考 E_EnergyWave），亮边是冰白色，后面拖着黑红色的碎石和烟。整张图朝右，上下对称，左端是起点。约 50 格长、30 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with icy white edges (#FFFFFF, #EAF6FF) and black-red debris (#3A0A1A, #22060F).
Effect: a SCREAM SHOCKWAVE travelling to the RIGHT, SYMMETRIC above and below the middle line, starting at the left edge of the cell, 5 frames: 1 a small bright arc at the left edge; 2 three nested curved crimson arcs (like ")))" opening to the right) spread to 40% of the cell width, the front arc edged in icy white; 3 the arcs reach 75% of the cell width, wider (a fan about 60% of the cell height at its front), small dark debris chips flying with them; 4 the arcs reach the right edge, thinner and darker; 5 faint dark crimson arc fragments.
Layout: one horizontal row of 5 equal cells, each 5 wide to 3 tall, image size 2400x288 (each cell 480x288); the fan on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `briar_fx_e_hit.png`：声波打中敌人，4 帧

每个被尖啸打中的敌人身上：一圈血红的冲击波和几片碎光。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32).
Effect: a SONIC HIT, 4 frames: 1 a small white-pink flash at the center; 2 a round crimson ring with three short curved ")" arcs on its right side; 3 the ring spreads and breaks into crimson chips; 4 faint dark red specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `briar_fx_e_stun.png`：惊吼眩晕（英雄头顶，1 秒），4 帧循环

被击退的英雄头顶：一圈血红的小星星在转（撞墙晕眩）。4 帧循环。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32).
Effect: STUN STARS above a head, 4 frames, a seamless loop: three small crimson five-pointed stars with white-pink centers circling on a flat elliptical path (twice as wide as tall), each frame a quarter turn, the stars at the back drawn smaller and darker.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `briar_fx_r_gem.png`：毙除的血石（飞行），4 帧循环

她踢出的血石：一颗血红的菱形宝石（参考 R_Gem、R_Mis_GemShine，和造型图枷锁顶上的红宝石一样），带金色的小边框，一边转一边往前飞，后面拖着血红色的尾焰和火星。约 20 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with small gold accents (#E6C780, #CEAB61, #A48149).
Effect: a HEMOLITH GEM flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a faceted crimson diamond gem with a thin gold setting at 75% of the cell width, a white glint on its facet moving each frame as it spins; behind it a tapering crimson flame trail with small sparks streaming to the left edge of the cell.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the gem on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `briar_fx_r_mark.png`：猎物标记（被命中的英雄头顶，直到血狂结束），4 帧循环

被标记为猎物的英雄头顶：一个血红色的菱形标记（像血石的形状，外面一圈尖刺光，参考 R_Target_Flare），一闪一闪。4 帧循环。约 14 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E).
Effect: a PREY MARK floating above a head, 4 frames, a seamless loop: a crimson diamond sigil (a hollow diamond outline 2 squares thick with a small solid diamond inside), four short sharp rays pointing up, down, left and right from it; the sigil pulses: brighter with longer rays in frames 2-3, dimmer in frames 1 and 4.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `briar_fx_r_boom.png`：毙除落地爆炸（地面），7 帧

她落在猎物身边：地上炸开一圈血红的冲击环，环上是尖角的符文（参考 R_Explosion_CF、R_RuneDecal），中心一团白红闪光和黑红烟，向外喷出碎石。约 70 格宽、36 格高的椭圆（爆炸半径约 35000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with black-red tar smoke (#3A0A1A, #22060F, #120308).
Effect: a CRIMSON LANDING BLAST on the ground (the caster lands at the center - leave a small empty space for her feet), 7 frames: 1 a bright white-red flash at the center; 2 a flat ring of crimson light (an ellipse twice as wide as tall) bursts outward to 45% of the cell width, jagged rune spikes along its edge, black-red smoke puffing up from the center; 3 the ring at 80%, dark debris chips flying outward; 4 the ring at 98% of the cell width, thinner; 5 the ring fades to dark crimson, a cracked dark stain left on the ground inside it; 6 broken dark ring pieces; 7 the last faint specks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `briar_fx_r_hit.png`：爆炸打中敌人，4 帧

每个被落地爆炸打中的敌人：一道血红的尖刺闪光（参考 R_Flashes）。约 18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFFFFF, #FFD0DA, #FF4A6E, #D81E48, #9A0E32).
Effect: a CRIMSON BURST HIT, 4 frames: 1 a small white flash; 2 a spiky crimson star flash with white core, about 60% of the cell wide; 3 the star breaks into crimson shards flying outward; 4 faint dark red specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `briar_fx_r_fear.png`：恐惧（其他敌人头顶，1.5 秒），4 帧循环

被恐惧的敌人头顶：一个暗红色的小骷髅（或一张惊恐的鬼脸），周围飘着黑红色的烟，一抖一抖。4 帧循环。约 14 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-crimson ramp (#FFD0DA, #FF4A6E, #D81E48, #9A0E32, #5A061E) with black-red smoke (#3A0A1A, #22060F).
Effect: a FEAR ICON floating above a head, 4 frames, a seamless loop: a small crimson skull with two dark eye holes and a jagged mouth, black-red smoke wisps curling around it; it trembles one square left and right between frames and its eye holes flash pink in frame 3.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `briar_fx_hit` | `view_effects` `league_briar_hit`（普攻命中，跟随） | 16 宽 |
| `briar_fx_snack` | `league_briar_snack`（噬击，目标身上） | 24 |
| `briar_fx_snack_heal` | `league_briar_snack_heal`（她身上） | 20 × 30 |
| `briar_fx_q_hit` | `league_briar_q_hit`（冲头命中 + 0.5 秒眩晕星） | 24 × 28 |
| `briar_fx_frenzy` | `view_buffs` `league_briar_frenzy` | 30 × 44 |
| `briar_fx_hema` | `view_buffs` `league_briar_hema` | 36 × 48 |
| `briar_fx_e_guard` | `view_buffs` `league_briar_e_guard` | 30 × 40 |
| `briar_fx_e_wave` | `view_projectiles` `league_briar_e_wave`（LineRangeProjectile，朝施法方向转） | 50 × 30（锥形半径 50000） |
| `briar_fx_e_hit` | `league_briar_e_hit` | 16 |
| `briar_fx_e_stun` | `league_briar_e_stun`（头顶，1 秒） | 18 × 8 |
| `briar_fx_r_gem` | `view_projectiles` `league_briar_r_gem` | 20 × 10 |
| `briar_fx_r_mark` | `view_buffs` `league_briar_r_mark`（猎物头顶） | 14 |
| `briar_fx_r_boom` | `league_briar_r_boom`（CasterViewEffect，地面，不跟随） | 70 × 36（半径 35000） |
| `briar_fx_r_hit` | `league_briar_r_hit` | 18 |
| `briar_fx_r_fear` | `league_briar_r_fear`（头顶，1.5 秒） | 14 × 16 |
