# 贾克斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图。** 造型和全部动作已经做完、导入游戏，用户确认过（两轮返修后灯柱都直了）。这一轮只画特效，不画人。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里贾克斯原皮自己的特效贴图（普攻的橙色火舌和白闪、Q 落地的烟、E 反击风暴的地面旋风环和火焰、R 的冲击波、尘土、裂地纹和光罩），只在本地用，不要提交。英雄联盟的贴图大多是灰白的遮罩，游戏里才上色：**形状照它，颜色照下面的规则**。
> - 颜色和画风对照 `design/jax_design.png`（定稿造型，8 倍）；大小对照 `design/jax_ingame.png`（游戏里的全部帧，3 倍，绿线是脚底线，蓝线是站位点）：贾克斯从羽饰顶到脚底 41 格，其他英雄约 35 格。
> - 特效照下面第 1–10 条和“所有特效图的规则”画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（格子比例不准、半透明边）也可以交：Claude 会按技能范围把每帧取样成游戏尺寸。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「无情连打」 | 抡灯柱砸中目标；每次攻击叠攻速（不用画） | `jax_fx_hit` |
| 普攻里的 W「蓄力一击」 | 下一次攻击（或跳斩落地）变成蓄力重砸，额外魔法伤害 | `jax_fx_w_hit` |
| 大招的被动 | 每第 3 次攻击（大招期间每第 2 次）额外魔法伤害 | `jax_fx_r_proc` |
| 技能 1 = Q「跳斩」 | 跳到目标身上砸下 | `jax_fx_q_hit` |
| 技能 2 = E「反击风暴」 | 1.5 秒架势：躲开所有普攻；结束时灯柱一转，周围一圈伤害并眩晕 1 秒 | `jax_fx_e_stance` · `jax_fx_e_burst` · `jax_fx_stun` |
| 大招 = R「武器大师」 | 跳起砸地，周围一圈伤害；之后 8 秒护甲魔抗大增（每多砸中一个英雄再加） | `jax_fx_r_slam` · `jax_fx_r_hit` · `jax_fx_r_aura` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反），也不要用最深的颜色给形状勾一圈边。
- 颜色（四套，从他的造型取：灯笼的火、青铜、兜帽和披风的紫、落地的尘土；按每条写的用）：
  - 灯火（主体）：`#FFFFFF`、`#FFF3B8`、`#FFD24A`、`#FF9A1F`、`#E0560F`、`#8A2901`；
  - 青铜（火星、金属碎屑、圈的亮边）：`#FFE7A0`、`#E4BE6A`、`#B48340`、`#704A23`；
  - 紫能（反击风暴的旋风、蓄力和大招的能量边）：`#F4C6FF`、`#D06CF0`、`#9A34C8`、`#5E1E86`、`#2E0E48`；
  - 尘土（跳斩和大招砸地）：`#E8D6B0`、`#B89C74`、`#7C6446`、`#4A3A2A`。
- 命中、爆开、标记都画在格子正中，不旋转；地面上的形状按游戏的斜俯视角度画成扁的（宽约是高的 2 倍）。
- 围着贾克斯的特效（反击风暴的架势、大招的光环、两个地面圈）会画在他**身体下层**：身体会自己挡住中间。**不要留人形的空洞，不要画人**，照常画满，只是别把最亮、最重要的部分放在正中间他站的位置。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位；圈要再加上双方的碰撞半径，约 17 格）。

### 1. `jax_fx_hit.png`：普攻命中，5 帧

灯柱砸中目标：中心一下白光（参考 BA_hit_flash），向外炸开几条橙金色的小火舌（参考 BA_bolts_tar），几粒青铜火星。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a lantern-fire ramp (#FFFFFF, #FFF3B8, #FFD24A, #FF9A1F, #E0560F, #8A2901) with bronze sparks (#FFE7A0, #E4BE6A, #B48340).
Effect: a HEAVY STAFF IMPACT, 5 frames: 1 a small white flash at the center; 2 the flash at full size (about 35% of the cell wide) with four or five short orange-gold flame tongues bursting outward from it, like little pointed flames; 3 the flame tongues reach 70% of the cell width and curl, bronze sparks fly out; 4 the flames break into orange flecks and the sparks fly further; 5 a few dim orange specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `jax_fx_w_hit.png`：蓄力一击命中，6 帧

蓄力的重砸：比普攻大、比普攻亮。中心一团紫白色的闪光，一圈锯齿状的紫色能量环炸开，里面夹着橙金的火舌和青铜火星（参考 BA_hit_flash、E_Wave06、BA_bolts_tar）。约 26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, violet energy (#F4C6FF, #D06CF0, #9A34C8, #5E1E86) with a lantern-fire ramp (#FFFFFF, #FFF3B8, #FFD24A, #FF9A1F, #E0560F) and bronze sparks (#FFE7A0, #E4BE6A).
Effect: an EMPOWERED STAFF SMASH, 6 frames: 1 a bright white-violet flash at the center; 2 the flash at full size (about 45% of the cell wide) with a jagged violet energy ring bursting around it and orange-gold flame tongues shooting out between the ring's spikes; 3 the ring at 85% of the cell width, the flames curling outward, bronze sparks flying; 4 the ring breaks into violet arcs, the flames fade to orange flecks; 5 thin violet arcs and a few sparks at the edges; 6 faint violet specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `jax_fx_r_proc.png`：大招被动（每第 3 下），6 帧

每第三下攻击多一次魔法伤害：目标身上一颗金色的四角星光（参考 R_Flare_03），外面一圈细细的紫色光环往外扩，几点金色火星。要和普攻命中一眼分得开（有星光和光环）。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold light ramp (#FFFFFF, #FFF3B8, #FFD24A, #E4BE6A) with violet energy (#F4C6FF, #D06CF0, #9A34C8, #5E1E86).
Effect: a GRANDMASTER STRIKE mark, 6 frames: 1 a small white-gold four-pointed star glint at the center; 2 the star at full size (long thin rays up, down, left and right, about 60% of the cell wide), a thin violet ring appears around its core; 3 the ring expands to 80% of the cell width, small gold sparks around it; 4 the star's rays shorten, the ring thins; 5 the ring breaks into violet dots, the star shrinks to a point; 6 faint gold and violet specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `jax_fx_q_hit.png`：跳斩落地，6 帧

跳到目标身上砸下：中心一下白金色闪光，贴着地面往两边炸开一圈尘土（参考 Q_tar_smoke、R_sand_smoke），几颗青铜火星往上蹦。约 32 格宽、16 格高（扁的，尘土在下半部）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a lantern-fire ramp (#FFFFFF, #FFF3B8, #FFD24A, #FF9A1F) with dust (#E8D6B0, #B89C74, #7C6446, #4A3A2A) and bronze sparks (#FFE7A0, #E4BE6A).
Effect: a LEAP LANDING IMPACT on the ground, 6 frames: 1 a white-gold flash at the middle of the cell; 2 the flash at full size (about 30% of the cell wide), a low burst of dust puffs spreading sideways along the bottom half of the cell (twice as wide as tall), bronze sparks jumping up; 3 the dust at 90% of the cell width, round puffs, the sparks at their highest; 4 the flash gone, the dust puffs drift apart and thin; 5 thin dust wisps; 6 a few faint dust specks.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `jax_fx_stun.png`：反击风暴的眩晕（1 秒，头顶），8 帧

被反击风暴打中的敌人眩晕 1 秒：头顶三颗金色小星星绕着一个扁圆转（参考 R_Flare_03 的星形）。8 帧转一圈多，导入时 Claude 把它放到头顶。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold light ramp (#FFFFFF, #FFF3B8, #FFD24A, #E4BE6A, #B48340).
Effect: a DAZE above a head, 8 frames, a seamless loop: three small gold five-pointed stars with white centers circling on a flat elliptical path (twice as wide as tall, filling 90% of the cell width), each frame an eighth of a turn; the stars at the back of the path smaller and darker (#B48340), the ones in front bigger and brighter.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 2048x128 (each cell 256x128); centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `jax_fx_e_stance.png`：反击风暴架势（在他身上，1.5 秒），4 帧循环

架势期间：脚下一圈贴地的紫色旋风环（参考 E_Ground：一个扭动的环），环上有几道弯弯的紫色风痕绕着他扫（参考 E_Trail02、E_Trail13），夹着几点橙色火星（参考 E_Flecks）。画在他身体下层，**不留空洞，不画人**。4 帧循环。约 44 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, violet energy (#F4C6FF, #D06CF0, #9A34C8, #5E1E86, #2E0E48) with orange flecks (#FFD24A, #FF9A1F).
Effect: a COUNTER STRIKE WHIRL on the ground around a standing warrior (do NOT draw the warrior and do not leave a hole: the picture goes under him), 4 frames, a seamless loop: a flat swirling violet wind ring on the ground (an ellipse twice as wide as tall, 90% of the cell width, its bottom edge at 90% of the cell height), made of two or three curved streaks chasing each other around it, brighter (#F4C6FF) at their heads and fading (#5E1E86) at their tails; two thin curved wind streaks sweeping around at the height of his knees above the ring; a few orange flecks flung from the streaks; each frame the streaks move a quarter turn around the ring.
Layout: one horizontal row of 4 equal cells, each 5 wide to 3 tall, image size 1280x384 (each cell 320x192); the ring centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `jax_fx_e_burst.png`：反击风暴爆发（地面圈，在他身上），7 帧

架势结束，灯柱一转：以他为中心，一圈贴地的冲击环迅速扩开（参考 E_Glow05、E_Wave06、E_smokeRing_dissolve），环是灯火的橙金色，外沿一道紫色，环上窜起一圈小火苗（参考 E_dome_flames），火星四溅。画在他身体下层，不留空洞。约 96 格宽、48 格高（第 3–4 帧环的外沿碰到格子边）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a lantern-fire ramp (#FFFFFF, #FFF3B8, #FFD24A, #FF9A1F, #E0560F, #8A2901) with a violet rim (#D06CF0, #9A34C8, #5E1E86) and bronze sparks (#FFE7A0, #E4BE6A).
Effect: a COUNTER STRIKE SHOCKWAVE on the ground around a standing warrior (do NOT draw him; the picture goes under him, no hole), 7 frames: 1 a bright white-gold flash ring low around the middle of the cell, small; 2 a flat fire ring (an ellipse twice as wide as tall) at 55% of the cell width, orange-gold, a violet line along its outer edge, a crown of small flame tongues rising all along the ring; 3 the ring at 85% of the cell width, the flames tall, sparks flying outward; 4 the ring at full cell width, thinner, the flames shorter; 5 the ring breaks into orange arcs and violet wisps; 6 fading arcs and flecks near the edges; 7 a few faint specks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 1792x128 (each cell 256x128); the ring centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `jax_fx_r_slam.png`：武器大师砸地（地面圈，在他身上），8 帧

大招跳起落下、灯柱砸地：中心一下很亮的白金色闪光，地面裂开几道发光的裂纹（参考 Jax_Skin19_R_AOE_CracksTotal），一圈金色冲击波贴地扩开（参考 R_Wave04、Shockwave01b），环边翻起尘土（参考 R_sand_smoke）。画在他身体下层，不留空洞。约 104 格宽、52 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a lantern-fire ramp (#FFFFFF, #FFF3B8, #FFD24A, #FF9A1F, #E0560F) with dust (#E8D6B0, #B89C74, #7C6446) and violet accents (#D06CF0, #9A34C8).
Effect: a GRANDMASTER GROUND SLAM around a warrior (do NOT draw him; the picture goes under him, no hole), 8 frames: 1 a very bright white-gold flash at the middle of the cell; 2 glowing orange cracks shoot out across the ground from the middle in six or seven jagged lines, a flat gold shockwave ring (an ellipse twice as wide as tall) at 40% of the cell width; 3 the ring at 70% of the cell width, dust puffs thrown up along it, the cracks glowing; 4 the ring at full cell width, the dust thick along it, a thin violet line inside the ring; 5 the ring thins and breaks, the dust drifts outward, the cracks dim to dark orange; 6 dust wisps and dim cracks; 7 faint cracks and specks; 8 almost gone.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 2048x128 (each cell 256x128); the slam centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `jax_fx_r_hit.png`：武器大师砸中（每个敌人身上），5 帧

砸地的冲击打到每个敌人：一个金色的闪光加一小圈紫色碎光，几颗尘土。比蓄力一击小。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold light ramp (#FFFFFF, #FFF3B8, #FFD24A, #E4BE6A) with violet chips (#D06CF0, #9A34C8) and dust (#B89C74, #7C6446).
Effect: a SHOCKWAVE HIT, 5 frames: 1 a white-gold flash at the center; 2 the flash at full size (about 45% of the cell wide), violet chips and a few dust specks bursting outward; 3 the chips fly to 80% of the cell width, the flash shrinks; 4 the chips dim; 5 faint specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `jax_fx_r_aura.png`：武器大师（在他身上，8 秒），4 帧循环

大招期间护甲魔抗大增：脚下一个扁的金色光环（参考 R_buf_glow、R_buf_outer），身后一道淡淡的金色弧形光罩（参考 R_Storm_R_Dome，只看得到头顶和两侧的弧），身体两侧往上飘金色光点和几点紫色火星。画在他身体下层，**不留空洞，不画人**。4 帧循环。约 48 格宽、56 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold light ramp (#FFFFFF, #FFF3B8, #FFD24A, #E4BE6A, #B48340) with violet motes (#D06CF0, #9A34C8, #5E1E86).
Effect: a GRANDMASTER AURA around a standing warrior (do NOT draw him and do not leave a hole: the picture goes under him, his body covers the middle), 4 frames, a seamless loop: a flat gold halo ring on the ground at the feet (an ellipse twice as wide as tall, 80% of the cell width, its bottom at 92% of the cell height), its brightest glints running around it; a faint dome of gold light behind him - only its thin arc shows, from beside his knees on both sides up over the top of the cell (the arc's top at 5% of the cell height); small gold motes and a few violet sparks rising along both sides of the cell from the ring to above the head; the glints and motes move each frame.
Layout: one horizontal row of 4 equal cells, each 6 wide to 7 tall, image size 1152x336 (each cell 288x336); the ring centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） | 锚点（相对站位点，站位点在脚底上方 11.5） |
|---|---|---|---|
| `jax_fx_hit` | `view_effects` `league_jax_hit`（普攻命中，跟随） | 16 | 中心在 -4 |
| `jax_fx_w_hit` | `league_jax_w_hit`（蓄力一击） | 26 | -4 |
| `jax_fx_r_proc` | `league_jax_r_proc`（大招被动） | 22 | -4 |
| `jax_fx_q_hit` | `league_jax_q_hit`（跳斩落地） | 32 × 16 | 尘土底边在脚底线 |
| `jax_fx_stun` | `league_jax_stun`（眩晕 1 秒） | 18 × 8 | -25（头顶） |
| `jax_fx_e_stance` | `view_buffs` `league_jax_e_on`（架势，z -1） | 44 × 26 | 环在脚底线（+10） |
| `jax_fx_e_burst` | `league_jax_e_burst`（CasterViewEffect，z -1） | 96 × 48 | 环中心在 +10 |
| `jax_fx_r_slam` | `league_jax_r_slam`（CasterViewEffect，z -1） | 104 × 52 | 环中心在 +10 |
| `jax_fx_r_hit` | `league_jax_r_hit`（每个敌人） | 20 | -4 |
| `jax_fx_r_aura` | `view_buffs` `league_jax_r_on`（8 秒，z -1） | 48 × 56 | 光环在脚底线 |
