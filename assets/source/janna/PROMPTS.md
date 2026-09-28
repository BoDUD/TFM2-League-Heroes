# 迦娜：给 Codex 的特效提示词

> **这一轮只画 11 张特效图。**
> - 角色不用画：迦娜的模型由 Claude 做。头部（上扬的奶油金色火焰发型、蓝色头环和水晶饰、尖耳、蓝眼睛，用户选了方案 B，一格暗红色的嘴）是逐格画的，每一帧贴在英雄联盟头部关节的位置；身体用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。她一直悬浮在离地 3 像素的地方。
> - 定稿造型图 `native/janna_native.png` 只用来参考配色，不要改它。
> - 风的画风参考 `base_wind_ref.png`：本体风法师的风弹（projectile）、俯视旋涡（skill1_target_effect）、竖直小龙卷（skill2_projectile）和大招风刃（ult 那一行身上的弧形风）。那一套是淡青、白和一点灰蓝，块面清楚、没有描边。
> - `janna_icons_ref.png` 是英雄联盟里 Q、E、R 的技能图标（只在本地用），龙卷风、风暴之眼和季风的样子可以参照；`janna_model_ref.png` 是迦娜在游戏里的全部动作帧（3 倍），用来对大小：套在人身上的特效按她的身高画。
> - 特效照下面第 1–11 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_janna.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 吹出一道风弹 | `janna_fx_bolt` · `janna_fx_hit` |
| 被动「顺风而行」 | 战斗中她和身边的队友移动速度提高（游戏自带的加速图标，不用画） | — |
| 技能 1 = Q「飓风呼啸」 | 放出一道龙卷风，贯穿直线上的敌人，把他们击飞 0.75 秒 | `janna_fx_tornado` · `janna_fx_knockup` |
| 技能 2 = E「风暴之眼」+ W「和风守护」 | 对一名敌方英雄放出风元素（和风守护：伤害 + 减速）；同时给身边一名队友套上风暴护盾 4 秒（护盾在时攻击力提高） | `janna_fx_w_gust` · `janna_fx_w_hit` · `janna_fx_e_cast` · `janna_fx_storm` |
| 大招 = R「复苏季风」 | 一阵狂风把身边的敌人向外吹开，然后原地引导 3 秒，每秒治疗身边的队友 | `janna_fx_r_gale` · `janna_fx_r_storm` · `janna_fx_r_heal` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。风**没有黑描边**（特效和角色相反）。
- 颜色：
  - 风（风弹、龙卷、旋风、风元素、护盾、狂风）：`#FFFFFF`、`#E6FAFF`、`#B8F0FF`、`#7ED8F6`、`#3EA6DC`、`#2C6FB0`，少量灰蓝暗部 `#6C7FA8`、`#4A5A86`（和本体风法师一样块面分明，白色是最亮的风芯）；
  - 风暴护盾的光：`#FFFFFF`、`#E6FAFF`、`#9EE6FF`、`#5CC6F0`，外缘一点金色火花 `#FFE680`、`#FFC040`（迦娜的法杖宝石是橙金色）；
  - 治疗：`#F4FFE8`、`#C8FFB0`、`#8CEB78`、`#48C05A`，搭配几缕白风。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。所以龙卷风（第 3 条）画成**俯视的旋涡**，不要画竖直的漏斗（竖的漏斗朝左飞会倒过来）。
- 命中、击飞、护盾居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（11 张）

11 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位；迦娜本人头顶到脚底 28 格，加上上扬的头发约 35 格）。

### 1. `janna_fx_bolt.png`：普攻风弹（飞行物），3 帧循环

迦娜用法杖吹出的一小团旋转的风，游戏按方向旋转。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC, #2C6FB0).
Effect: a SMALL GUST BOLT flying to the RIGHT, 3 frames, a seamless loop: a small ball of swirling wind with a white core at the RIGHT end, pale cyan curls wrapped around it, two or three thin streaks of wind trailing to the left; SYMMETRIC above and below its middle line; only the curls and streaks change from frame to frame; frame 3 leads back into frame 1.
Layout: one horizontal row of 3 equal cells, each four times as wide as tall (4:1), image size 1536x128; the bolt along the middle height of the cell, about 65% of the cell wide and 50% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `janna_fx_hit.png`：风弹命中，5 帧

风弹打中目标时散开的一小团风。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC).
Effect: a SMALL WIND HIT, 5 frames: 1 a small white flash at the center; 2 four curved gusts burst outward like a pinwheel, white cores, pale cyan edges; 3 the pinwheel at full size, about 45% of the cell wide, small wind flecks flying out; 4 the gusts thin into curls; 5 the last curls fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `janna_fx_tornado.png`：飓风呼啸的龙卷风（飞行物），4 帧循环

Q 放出的龙卷风，贯穿一条直线。**画成俯视的旋涡**（参考 `base_wind_ref.png` 里 skill1_target_effect 那种风车状旋涡，但更大、更猛），游戏会按方向旋转，所以要上下对称、转任何角度都好看。约 30 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC, #2C6FB0) with grey-blue shading (#6C7FA8, #4A5A86).
Effect: a HOWLING GALE, a whirlwind seen from ABOVE, rushing to the RIGHT, 4 frames, a seamless loop: a round spinning vortex with four or five thick curved arms of wind spiraling into a bright white eye at the center, pale cyan and blue arms, darker grey-blue on their trailing edges, small flecks of dust and leaves thrown around its rim, a short wake of wind streaks trailing to the LEFT; the whole picture SYMMETRIC above and below the middle line (the arms curl the same way, the wake is centered); the arms turn by a quarter of their spacing each frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall (3:2), image size 1536x512 (each cell 384x256); the vortex centered in the cell's right two thirds, about 60% of the cell's height across, the wake reaching the left edge, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `janna_fx_knockup.png`：被龙卷风击飞（跟着目标），6 帧（0.75 秒）

被龙卷风打中的敌人被一股小旋风托上天。约 18 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC).
Effect: KNOCKED UP by wind, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 50% of the cell height stands there, feet at 80% of the cell height) - never draw the person. 1 a flat ring of wind spins up around the feet of the space; 2 two ribbons of wind spiral up around the body of the space like a small tornado, white where they pass in front, pale cyan where they curve behind; 3 the ribbons reach above the head, dust puffs at the feet; 4 the spiral at full height, wind flecks flying off; 5 the ribbons thin and loosen; 6 only a few curls fading at the feet.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 40% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `janna_fx_w_gust.png`：和风守护的风元素（飞行物），4 帧循环

W 放出的风元素，飞向敌方英雄。像一只白色的小风精灵（一团带两道弯翼的风，拖着尾巴），游戏按方向旋转。约 14 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC, #2C6FB0).
Effect: ZEPHYR, a small air elemental flying to the RIGHT, 4 frames, a seamless loop: a bright white wind spirit with a rounded head at the RIGHT end, two swept-back curved wings of pale cyan wind above and below it, a tail of three wavy wind streaks trailing to the left; SYMMETRIC above and below its middle line; the wings flap a little and the tail streaks wave from frame to frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each three times as wide as tall (3:1), image size 1536x128 (each cell 384x128); the spirit along the middle height, about 75% of the cell wide and 70% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `janna_fx_w_hit.png`：和风守护命中（跟着目标），5 帧

风元素撞上敌人时炸开一阵风，并在他身上缠一圈拖慢他的风。约 18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC, #2C6FB0).
Effect: a GUST HIT, 5 frames: 1 a white flash at the center; 2 a burst of wind slashes fanning out to the right and a curl of wind wrapping around the center; 3 the burst at full size, about 55% of the cell wide, two curved wind blades and flecks; 4 the blades fade, a thin ring of wind circling the center; 5 the ring thins and fades.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `janna_fx_e_cast.png`：风暴之眼护盾生成（套在队友身上），5 帧

风暴之眼套上的一瞬间：一股旋风卷上来，合成一个风球。约 30 格宽、38 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind glow (#FFFFFF, #E6FAFF, #9EE6FF, #5CC6F0) and a few gold sparks (#FFE680, #FFC040).
Effect: EYE OF THE STORM being cast on an ally, 5 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 50% of the cell height stands there, feet at 80% of the cell height) - never draw the person. 1 three streaks of wind rush in from the sides toward the space; 2 they wrap around it in a spiral from the feet up; 3 the spiral closes into an upright oval bubble of swirling wind around the space, bright white at its rim, a few gold sparks; 4 the bubble flashes brighter; 5 the bubble settles, thinner, the inside see-through.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the oval about 45% of the cell wide and 70% of its height, its bottom at the feet of the space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `janna_fx_storm.png`：风暴护盾（套在队友身上），6 帧，无缝循环

护盾在的时候一直循环，破了就消失。要看得见但不能挡住里面的英雄。约 28 格宽、36 格高。**和第 7 条最后一帧同样大小、同样位置。**

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind glow (#FFFFFF, #E6FAFF, #9EE6FF, #5CC6F0) and a few gold sparks (#FFE680, #FFC040).
Effect: STORM SHIELD around an ally, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 50% of the cell height stands there, feet at 80% of the cell height) - never draw the person. Around the space: an upright oval made of two or three thin bands of swirling wind, white where they pass in front, pale cyan where they curve behind, the inside EMPTY and see-through; one or two tiny gold sparks orbit with the bands; the bands turn a little each frame; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the oval about 42% of the cell wide and 66% of its height, its bottom at the feet of the space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `janna_fx_r_heal.png`：复苏季风治疗（队友身上），6 帧

每秒一次，被季风治疗的队友身上升起一阵带着绿光的风。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, soft healing greens (#F4FFE8, #C8FFB0, #8CEB78, #48C05A) with white wind (#FFFFFF, #E6FAFF, #B8F0FF).
Effect: HEALED BY THE MONSOON, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 50% of the cell height stands there, feet at 80% of the cell height) - never draw the person. 1 a few small green sparkles and white wind curls appear at the feet of the space; 2 they rise in a gentle spiral around the body; 3 at the chest, a soft green glow and small plus-shaped sparkles; 4 the spiral reaches above the head; 5 the sparkles drift up and scatter; 6 the last sparkles fading above the head.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 40% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `janna_fx_r_gale.png`：季风爆发（地面，画在单位下面），6 帧（0.5 秒）

大招起手的一阵狂风：以迦娜为中心，一圈风沿地面向外炸开，把敌人吹走。半径 40000，约 84 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC, #2C6FB0) with grey-blue shading (#6C7FA8).
Effect: a MONSOON BLAST on the ground, 6 frames: a flat ellipse on the ground, twice as wide as tall. 1 a small white burst of wind at the center; 2 a ring of wind rushes outward along the ground, thick white gusts on its rim, pale cyan inside; 3 the ring at two thirds of the size, curved gust blades pointing outward all around its rim, dust flecks thrown outward; 4 the ring at full size, about 95% of the cell wide; 5 the rim breaks into separate gusts flying outward; 6 the last wisps at the rim fading.
Layout: one horizontal row of 6 equal cells, each twice as wide as tall (2:1), image size 3072x256; the ellipse centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `janna_fx_r_storm.png`：季风引导（地面，跟着迦娜，画在单位下面），8 帧，1 秒一循环

引导的 3 秒里，迦娜脚下一直有一圈旋转的季风，每秒从头播一遍。半径 40000，约 84 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a wind ramp (#FFFFFF, #E6FAFF, #B8F0FF, #7ED8F6, #3EA6DC) with a little soft green (#C8FFB0, #8CEB78).
Effect: a MONSOON on the ground, 8 frames, a seamless loop of exactly one second: a flat ellipse on the ground, twice as wide as tall, made of four or five long curved bands of wind circling around the center counter-clockwise, white at their leading ends, pale cyan and blue toward their tails, a few green sparkles and leaves carried along; the center stays mostly empty (Janna floats there); the bands move a little around the circle each frame; frame 8 leads back into frame 1.
Layout: one horizontal row of 8 equal cells, each twice as wide as tall (2:1), image size 4096x256; the ellipse centered in every cell, about 95% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，帧时长写在 `native/janna_cells.json`。特效由 `tools/art/import_janna.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `janna_fx_bolt.png` | 3 | 投射物 `league_janna_bolt`（普攻） | 3 × 50 循环 |
| `janna_fx_hit.png` | 5 | 特效 `league_janna_hit`（普攻命中） | 5 × 50 |
| `janna_fx_tornado.png` | 4 | 投射物 `league_janna_q_tornado`（半径 10000） | 4 × 60 循环 |
| `janna_fx_knockup.png` | 6 | 特效 `league_janna_knockup`（跟随目标，0.75 秒） | 6 × 125 |
| `janna_fx_w_gust.png` | 4 | 投射物 `league_janna_w_gust` | 4 × 60 循环 |
| `janna_fx_w_hit.png` | 5 | 特效 `league_janna_w_hit`（跟随目标） | 5 × 60 |
| `janna_fx_e_cast.png` | 5 | 特效 `league_janna_e_cast`（跟随队友） | 5 × 70 |
| `janna_fx_storm.png` | 6 | buff `league_janna_e_storm`（护盾在时循环） | 6 × 100 循环 |
| `janna_fx_r_heal.png` | 6 | 特效 `league_janna_r_heal`（跟随队友，每秒一次） | 6 × 80 |
| `janna_fx_r_gale.png` | 6 | 特效 `league_janna_r_gale`（迦娜脚下，地面，半径 40000） | 6 × 80 |
| `janna_fx_r_storm.png` | 8 | 特效 `league_janna_r_storm`（跟随迦娜，地面，每秒一段，半径 40000） | 8 × 125 |

特效表：`league_janna_fx`（bolt、hit、knockup、w_gust、w_hit、e_cast、storm、r_heal），`league_janna_big`（tornado、r_gale、r_storm）。
