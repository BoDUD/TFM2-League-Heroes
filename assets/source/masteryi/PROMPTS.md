# 无极剑圣 易：给 Codex 的特效提示词

> **这一轮只画 9 张特效图。**
> - 角色不用画：易的模型由 Claude 做（和金克丝、蕾欧娜一样）。头盔是 Claude 照英雄联盟 2013 版模型逐格画的（用户选了方案 A：右下一簇绿色复眼镜片，下颚只在前端留一个小金喙 j3），每帧贴到英雄联盟动画的头部位置；身体用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/masteryi_native.png` 只用来参考配色和人物大小，不要改它。
> - 特效照下面第 1–9 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_masteryi.py --raw` 转成原尺寸条，再按技能范围定大小。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「双重打击」 | 剑砍；连续第 4 次普攻多砍一刀 | `masteryi_fx_hit` · `masteryi_fx_ds_hit` |
| 技能 1 = Q「阿尔法突袭」 | 易消失（不可选中），0.6 秒内在目标和附近敌人之间闪击 4 次，最后回到目标身边 | `masteryi_fx_q_vanish` · `masteryi_fx_q_hit` |
| 技能 2 = E「无极剑道」+ W「冥想」 | 先盘腿冥想 0.75 秒（减伤、回血），然后 5 秒内普攻附加真实伤害 | `masteryi_fx_w_aura` · `masteryi_fx_wuju` · `masteryi_fx_e_hit` |
| 大招 = R「高原血统」 | 7 秒内攻速、移速大幅提高 | `masteryi_fx_r_cast` · `masteryi_fx_highlander` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（易的两种光）：
  - 阿尔法突袭的剑光（黄绿，和他的剑同色）：`#FFFFFF`、`#E8FFB0`、`#B6F24A`、`#6FD02A`、`#3A8A1A`；
  - 无极剑道、冥想、高原血统的金光：`#FFFFFF`、`#FFF3B0`、`#FFD84A`、`#F2A82A`、`#C8741A`。
- 命中、光圈、光环居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（9 张）

9 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `masteryi_fx_hit.png`：普攻命中，5 帧

剑砍中目标时的一道黄绿斩光。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a green blade-light ramp (#FFFFFF, #E8FFB0, #B6F24A, #6FD02A, #3A8A1A).
Effect: a SWORD SLASH HIT, 5 frames: 1 a thin white-hot diagonal cut line appears at the center, from upper left to lower right; 2 the cut widens into a bright crescent of yellow-green light with a white core, a few sparks; 3 the crescent at full size, about 45% of the cell wide, small green sparks flying outward; 4 it breaks into sparks; 5 the last green specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `masteryi_fx_ds_hit.png`：双重打击的第二刀，5 帧

第一刀之后 0.13 秒补上的第二刀：和第一刀交叉成 X，更亮。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a green blade-light ramp (#FFFFFF, #E8FFB0, #B6F24A, #6FD02A, #3A8A1A).
Effect: a DOUBLE STRIKE, the second fast cut crossing the first, 5 frames: 1 a faint green diagonal line from upper left to lower right (the first cut, already fading) and a white-hot line flashing across it from lower left to upper right; 2 both cuts glow as a bright X of yellow-green light with a white center; 3 the X at full size, about 50% of the cell wide, a burst of green sparks at the crossing; 4 the X breaks into sparks and short streaks; 5 the last specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the crossing point at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `masteryi_fx_e_hit.png`：无极剑道的真实伤害，5 帧

剑道期间每次打中目标时在命中点多闪一下金白光（真实伤害）。约 16 格宽，比普攻命中小，叠在它上面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden light ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: a WUJU TRUE-DAMAGE SPARK, 5 frames: 1 a tiny white point at the center; 2 it bursts into a bright four-pointed golden star, white core, the vertical points a little longer; 3 the star at full size, about 35% of the cell wide, with four tiny gold sparks flying diagonally outward; 4 the star shrinks, the sparks drift; 5 two or three gold specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the star at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `masteryi_fx_q_hit.png`：阿尔法突袭的闪斩（跟着目标），6 帧

易消失后在目标身上连斩：每一击在被打中的敌人身上闪出一个 X 形剑光，旁边有一道易的残影一掠而过。约 34 格宽（比普攻大得多）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a green blade-light ramp (#FFFFFF, #E8FFB0, #B6F24A, #6FD02A, #3A8A1A).
Effect: ALPHA STRIKE, a lightning-fast blink strike on an enemy, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a streak of green light shoots in from the LEFT at chest height, its head a small white-hot point; 2 a big white-hot X of two crossing slashes cuts across the chest of the space, a faint green AFTERIMAGE of a swordsman leaping past (only a translucent-looking silhouette made of green light streaks, no details, no face) on the right; 3 the X at full size, about 60% of the cell wide, yellow-green with a white core, sparks exploding outward, the afterimage stretching into speed lines; 4 the X breaks apart into short green slashes and sparks; 5 sparks and a few green streaks fading; 6 the last green specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the crossing of the X on the empty space's chest, the effect at most 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `masteryi_fx_q_vanish.png`：阿尔法突袭的消失 / 现身，6 帧

易出手时原地消失、最后在目标身边现身时各播一次：一团黄绿色的残影和剑光碎片。约 30 格宽，画在他站的位置（格子中间是他的空位）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a green blade-light ramp (#FFFFFF, #E8FFB0, #B6F24A, #6FD02A, #3A8A1A).
Effect: a VANISHING BLUR where a swordsman blinks out of sight, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a tight burst of white light at the chest of the space; 2 the burst turns into a whirl of yellow-green light streaks around the whole space, like the swordsman dissolved into light, sharp shards of green light flying outward; 3 the streaks stretch horizontally, pulled to both sides; 4 they thin into fast speed lines and falling green sparks; 5 a few sparks and a faint green ring on the ground under the feet (a flat ellipse); 6 the last specks fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `masteryi_fx_wuju.png`：无极剑道光环（易身上），10 帧，无缝循环

剑道持续 5 秒，每秒播一遍这张图：金色的剑气在他身上流动（英雄联盟里是剑发金光，游戏里剑的位置每帧都不同，所以画成围着全身的金色剑气）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden light ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: WUJU STYLE, a golden sword-energy aura on a swordsman, 10 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. Thin golden flame-like wisps rise along both sides of the space from the knees to above the head (they flicker and climb a little each frame); small bright golden sparks drift upward around the body; a thin golden shimmer outlines the shoulders; no ring on the ground; frame 10 leads back into frame 1.
Layout: one horizontal row of 10 equal square cells, image size 2560x256; the effect at most 55% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `masteryi_fx_w_aura.png`：冥想（易身上），8 帧

盘腿悬空冥想 0.75 秒：身下亮起莲花形的金光，身边一圈圈金光向上升起。约 44 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a golden light ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: MEDITATE, a swordsman meditating while floating, surrounded by calm golden light, 8 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 50% of the cell height floats there, the lowest point at 80% of the cell height) - never draw the person. 1 a soft golden glow lights up under the space; 2 a golden lotus of light opens under it (a flat ellipse of eight pointed petals, about 60% of the cell wide); 3 a thin golden ring rises from the lotus up around the body; 4-6 more rings rise one after another and fade at head height, small golden motes floating up, the lotus glowing steadily; 7 the rings fade; 8 the lotus closes into a few motes.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the lotus centered under the empty space, the effect at most 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `masteryi_fx_r_cast.png`：高原血统（开启），6 帧

开大时身上爆开一圈金色的气劲，气流向身后甩出。约 40 格宽，跟着易，朝右画（他向左时游戏会水平翻转）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a golden light ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: HIGHLANDER, a swordsman bursting into supernatural speed, facing RIGHT, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a flash of white-gold light on the body; 2 a burst of golden energy explodes around the space, sharp flames of gold pointing outward; 3 the burst at full size, about 70% of the cell wide, with long streaks of gold light whipping back to the LEFT; 4 the flames settle into a tight golden glow around the body with speed lines trailing to the left; 5 the speed lines thin out, sparks drifting left; 6 a faint golden glow fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect centered on the empty space, streaks going to the left, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `masteryi_fx_highlander.png`：高原血统加速光环（易脚下），10 帧，无缝循环

大招持续 7 秒，每秒播一遍：脚下一圈金光，身后拖着金色的速度线。画在人物身后一层（会被人挡住）。约 44 格宽，朝右画（向左时游戏会水平翻转）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a golden light ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: HIGHLANDER SPEED AURA under a swordsman facing RIGHT, 10 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. A glowing golden ring lies on the ground around the feet (a flat ellipse twice as wide as tall, about 45% of the cell wide), bright on its front edge; five or six long thin golden speed lines stream backward to the LEFT from the body at different heights (knees to shoulders), they slide to the left and are replaced frame by frame; tiny gold sparks trail behind; frame 10 leads back into frame 1.
Layout: one horizontal row of 10 equal cells, each twice as wide as tall (2:1), image size 5120x256; the ring centered under the empty space's feet with the empty space in the middle of the cell, the speed lines filling the left half, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，头盔从 `native/masteryi_native.png` 贴上，帧时长写在 `native/masteryi_cells.json`。特效由 `tools/art/import_masteryi.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `masteryi_fx_hit.png` | 5 | 特效 `league_masteryi_hit`（普攻命中） | 5 × 50 |
| `masteryi_fx_ds_hit.png` | 5 | 特效 `league_masteryi_ds_hit`（双重打击第二刀） | 5 × 50 |
| `masteryi_fx_e_hit.png` | 5 | 特效 `league_masteryi_e_hit`（剑道真伤，叠在命中上） | 5 × 50 |
| `masteryi_fx_q_hit.png` | 6 | 特效 `league_masteryi_q_hit`（跟随目标；每 0.2 秒一击） | 6 × 40 |
| `masteryi_fx_q_vanish.png` | 6 | 特效 `league_masteryi_q_vanish`（消失处与现身处，不跟随） | 6 × 60 |
| `masteryi_fx_wuju.png` | 10 | 特效 `league_masteryi_wuju`（跟随易；每秒一遍，5 秒） | 10 × 100 |
| `masteryi_fx_w_aura.png` | 8 | 特效 `league_masteryi_w_aura`（跟随易，冥想 0.75 秒） | 8 × 100 |
| `masteryi_fx_r_cast.png` | 6 | 特效 `league_masteryi_r_cast`（跟随易） | 6 × 70 |
| `masteryi_fx_highlander.png` | 10 | 特效 `league_masteryi_highlander`（跟随易，身后一层；每秒一遍，7 秒） | 10 × 100 |

特效表：`league_masteryi_fx`（hit、ds_hit、e_hit、q_hit、q_vanish、wuju），`league_masteryi_big`（w_aura、r_cast、highlander）。
