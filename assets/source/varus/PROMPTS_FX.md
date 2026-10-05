# 惩戒之箭 韦鲁斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型和动作已定（`design/varus_design.png`，8 倍，40 行）。
> - 大小对照 `design/varus_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版弓箭手。韦鲁斯 29×40 格。每条写的大小都是游戏像素（格）。
> - `design/varus_shots.png`：普攻放箭、Q 蓄力、Q 放箭、E、R 的定稿动作（4 倍），青色十字是弓的握把（或脚下）的位置，导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里韦鲁斯自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**箭、蓄力、枯萎是暗裔的紫色和品红（亮紫带白芯）；锁链触须是黑紫色的荆棘带紫红色发光边；腐化地面是深紫色带紫红色裂光**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见；黑紫色的触须也要有紫红色亮边，不能糊成一块黑。
> - **缠在人身上的触须、围着人的光只画边，中间留空**，不然会把人整个挡住。
> - 特效照下面第 1–24 条和「所有特效图的规则」画，每张一个 PNG，文件名 `varus_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`varus_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + W「枯萎箭袋」 | 射箭，附带魔法伤害，命中英雄叠枯萎（最多 3 层） | `varus_fx_a_arrow` · `varus_fx_a_flash` · `varus_fx_a_hit` · `varus_fx_b_mark` |
| 枯萎引爆 | Q / E / R 命中英雄时引爆，按层数造成最大生命值伤害并缩短技能冷却 | `varus_fx_b_pop` |
| 技能 1 = Q「穿刺之箭」 | 有英雄在射程内时拉满弓（约 1.1 秒），否则快速出手；穿透一条线；每 40 秒一次满蓄力的箭带枯萎之箭的额外伤害 | `varus_fx_q_charge` · `varus_fx_q_fire` · `varus_fx_q_arrow` · `varus_fx_q_hit` · `varus_fx_w_glow` · `varus_fx_w_pop` |
| 技能 2 = E「恶灵箭雨」 | 朝目标区域射一箭上天，箭雨落下造成伤害，留下 4 秒的腐化地面（减速 + 重伤） | `varus_fx_e_cast` · `varus_fx_e_rain` · `varus_fx_e_field` · `varus_fx_e_hit` · `varus_fx_e_slow` |
| 大招 = R「腐败锁链」 | 甩出触须，禁锢第一个英雄 2 秒并叠满枯萎，半秒后扩散到附近的英雄并禁锢 | `varus_fx_r_cast` · `varus_fx_r_chain` · `varus_fx_r_hit` · `varus_fx_r_bind` · `varus_fx_r_spread` · `varus_fx_r_spread_hit` |
| 被动「复仇之欲」 | 击杀英雄后 5 秒内攻速大涨（击杀小兵野怪小涨） | `varus_fx_p_rage_on` · `varus_fx_p_rage` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、火花、拖尾没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的物体（箭、触须、荆棘、插在地上的箭）有 1 格深色描边（`#0B0410`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 暗裔紫光（箭、蓄力、枯萎）：`#FFFFFF`、`#F6D8FF`、`#E8A0FF`、`#CA2BFB`、`#A112F7`、`#6A1AB8`；
  - 品红（亮芯、被动）：`#FFFFFF`、`#FFC8F0`、`#FF70D8`、`#E838F3`、`#C0208F`；
  - 腐化紫红（触须的光、枯萎爆发）：`#FFD0D0`、`#FF6A6A`、`#F01A1A`、`#D32087`、`#890851`、`#4A0428`；
  - 黑紫（触须本体、腐化地面）：`#8A5CC0`、`#5E3A88`、`#3B185F`、`#261432`、`#140A1E`；
- **飞行物朝右画，而且上下对称**（`a_arrow`、`q_arrow`、`r_chain`）：游戏会把它转到出招方向，朝左时整张会上下翻转。
- **从弓上发出的特效朝右画，起点在格子左边的中点**（`a_flash`、`q_fire`、`r_cast`）；E 朝右上方，起点在左下角（`e_cast`）；蓄力和弓上的光（`q_charge`、`w_glow`）以握把为中心。画在他脚下或身上的画面（`p_rage_on`、`p_rage`）按每条写的站位画。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上或脚下的循环画面（`e_slow`、`r_bind`、`p_rage`）左右对称或不分左右，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：箭雨和腐化地面半径 28000、锁链扩散半径 55000）。

### 1. `varus_fx_a_arrow.png`：普攻飞出去的箭（飞行中循环），4 帧

普攻射出的一支箭：细长的紫色箭杆、发亮的紫白箭头，后面拖一小段紫色光尾（参考 varus_arrow_flat_bw、Arrow_Glow、Arrow_Streaks）。箭是物体，有 1 格深色描边；光尾没有。上下对称。约 14 格长、5 格高（箭约 10 × 3 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a FLYING ARROW moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a slim dark-violet arrow 10 squares long and 3 tall with a bright white-violet arrowhead and a small fletching, a 1-square dark outline; a short violet light streak 4 squares long trailing behind it to the LEFT that flickers each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the arrowhead at the RIGHT half, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `varus_fx_a_flash.png`：普攻放箭：弓上的闪光（施法者身上），3 帧

普攻放箭的一瞬间：弓弦那里一下紫白色的闪光，往右喷几道细光线（参考 crystal-flash、Flare-Sun）。朝右画：弓弦在格子左边中点。约 12 格宽、10 格高。要很短（3 帧），只在放箭那一下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a BOW-SHOT FLASH, pointing RIGHT, 3 frames: 1 a white-violet star at the LEFT MIDDLE of the cell (the bowstring); 2 three short violet light rays shooting right from that point; 3 the rays fading.
Layout: one horizontal row of 3 equal 6:5 cells, image size 720x200 (each cell 240x200); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `varus_fx_a_hit.png`：普攻打中（目标身上），4 帧

箭打中：一下紫白色闪光，几道紫色碎光往外飞（参考 HitEffect、Flare-Sun_red）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: an ARROW HIT, 4 frames: 1 a white flash with a violet rim; 2 a small four-pointed star of white-violet light 10 squares across, 4 tiny violet sparks flying out; 3 the star fading, sparks further out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `varus_fx_b_mark.png`：W 枯萎层数：目标头顶的标记（1、2、3 层，三行），每行 4 帧

被平A叠上枯萎的敌人：头顶出现一排紫色的枯萎标记（参考 varus-counter32：英雄联盟里是头上一圈紫色的小尖刺/鳞片），**第 1 行 1 个、第 2 行 2 个、第 3 行 3 个**，并排、每个约 4 × 5 格的紫色尖刺状小晶体（有描边），亮紫带白色高光，3 层时整排变亮并带一点红光。每行 4 帧：1 出现、2–3 发亮闪烁、4 稍微淡一点（游戏里每次命中重播）。整张约 16 格宽、6 格高一行。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8), a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F) and a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428).
Effect: BLIGHT STACK MARKS over a head, THREE ROWS (row 1: one mark, row 2: two marks side by side, row 3: three marks side by side), 4 frames per row: each mark a small upright spiky violet crystal 4 squares wide and 5 tall (a 1-square dark outline, bright violet with a white glint), marks 1 square apart and centred in the cell; 1 the marks pop in small; 2 full size and bright; 3 glinting; 4 slightly dimmer. In row 3 the marks are brighter with a thin crimson glow round them.
Layout: three horizontal rows of 4 equal 8:3 cells, image size 2048x576 (each cell 512x192); row 1 at the top, the marks centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `varus_fx_b_pop.png`：W 枯萎引爆（目标身上），5 帧

枯萎被 Q/E/R 引爆：目标身上猛地炸开一团紫红色的腐化能量，几根紫色尖刺往外刺，中间白色闪光（参考 HitEffect、shadow_step_red、Base_Ring）。约 22 格（3 层时导入放大）。居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8), a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a BLIGHT DETONATION, 5 frames: 1 a white-magenta flash in the center; 2 a burst of violet and crimson energy 18 squares across with 6 sharp violet spikes (outlined) stabbing outward; 3 a ring of violet light 22 squares across expanding, the spikes fading; 4 the ring thin, crimson sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `varus_fx_w_pop.png`：W 枯萎之箭（满蓄力 Q 的额外伤害，目标身上），5 帧

每 40 秒一次满蓄力的箭命中时的额外爆发：比普通引爆更大更亮，一圈紫红色的冲击波加一根往上冲的紫色光柱（参考 Q2_wisps、light_rays、Base_Ring）。约 28 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8), a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: an EMPOWERED BLIGHT BLAST, 5 frames: 1 a big white flash; 2 a pillar of violet light shooting up from the center (20 squares tall) and a crimson shockwave ring 20 squares across; 3 the ring expands to 28 squares, violet wisps curl up; 4 the pillar thins, wisps; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `varus_fx_w_glow.png`：W 枯萎之箭就绪：弓上的红光（施法者身上），4 帧

满蓄力的 Q 带上枯萎之箭时，弓身上缠绕一圈紫红色的光和几缕红色的腐化光丝（参考 W_ArcsForQ、Q2_wisps、Arrow_Streaks）。约 14 格宽、22 格高（和弓一样高），画在弓上，中间是弓的位置不要画弓。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: a CRIMSON AURA round an upright bow (do NOT draw the bow; leave its place empty), 4 frames, a seamless loop: thin crimson and violet light arcs crawling up along a tall crescent shape 22 squares tall (the bow's place), 5 small red wisps curling off it, a soft crimson glow; the arcs move up a few squares each frame.
Layout: one horizontal row of 4 equal 7:11 cells, image size 896x352 (each cell 224x352); the bow's grip at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `varus_fx_q_charge.png`：Q 蓄力：弓上聚集的紫光（施法者身上，循环），6 帧

Q「穿刺之箭」拉弓蓄力：弓上的紫色能量越聚越亮，几缕紫光从四周往握把那里吸过去，最后整把弓发出强光（参考 Q2_wisps、Base_Ring、crystal-flash、varuscurls3）。中间是弓的位置，不要画弓和人。6 帧：1–2 开始聚光，3–6 满蓄力循环闪烁。约 24 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a CHARGING DARK ARROW ENERGY gathering at a point (the bow's grip), 6 frames: 1 a few violet wisps drawn inward from 12 squares away toward the center; 2 more wisps, a small violet core; 3 a bright white-violet core 6 squares across with a thin violet ring 20 squares across; 4 the ring pulses smaller, sparks drawn in; 5 like 3; 6 like 4 (3-6 loop).
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the center of the energy at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `varus_fx_q_fire.png`：Q 放箭：弓前的爆闪（施法者身上），4 帧

满蓄力的箭射出去：弓前一团紫白色的爆闪，一圈冲击波往右推出去（参考 Flare-Sun、light_rays、Base_Ring）。朝右画：弓弦在格子左边中点。约 24 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a POWERFUL BOW SHOT, pointing RIGHT, 4 frames: 1 a big white-violet flash at the LEFT MIDDLE of the cell; 2 a violet shockwave ring (seen edge-on: a tall thin ellipse) pushing right, light rays streaming right; 3 the ring further right and fainter; 4 fading sparks.
Layout: one horizontal row of 4 equal 12:7 cells, image size 1536x448 (each cell 384x224); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `varus_fx_q_arrow.png`：Q 飞出去的穿刺之箭（飞行中循环），4 帧

Q 的大箭：一支又长又亮的紫色能量箭（箭杆是发光的紫白色，箭头尖锐），后面拖一道长长的紫色光带和细碎的光丝（参考 Q_mis_Ribbon、varus_arrow_flat_bw、Arrow_Streaks、Q2_wisps）。箭有描边，光带没有。上下对称。约 30 格长、10 格高（箭约 16 × 5 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a FLYING PIERCING ARROW moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a long glowing arrow 16 squares long and 5 tall (a white-violet shaft, a sharp bright arrowhead, a 1-square dark outline) pointing right; a long violet light ribbon 14 squares long behind it to the LEFT, tapering, with tiny magenta sparks that shift each frame.
Layout: one horizontal row of 4 equal 3:1 cells, image size 3072x256 (each cell 768x256); the arrowhead at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `varus_fx_q_hit.png`：Q 箭穿过敌人（目标身上），5 帧

Q 的箭穿过敌人：一道往右的紫色穿刺光线贯穿过去，中间一下白色闪光和碎光（参考 HitEffect、sliver、Arrow_Streaks）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a PIERCING HIT, 5 frames: 1 a white flash; 2 a horizontal violet streak 18 squares long piercing through the center to the right, sparks bursting out behind it; 3 the streak thinner, sparks spreading; 4 fading streak; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `varus_fx_e_cast.png`：E 朝天射箭：弓上的闪光（施法者身上），4 帧

E「恶灵箭雨」朝右上方射向天空：弓那里一下紫白色闪光，一道光往右上 45° 冲出去（参考 crystal-flash、sliver）。起点在格子左下角，往右上方画。约 16 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a SKYWARD SHOT FLASH, pointing UP-RIGHT at 45 degrees, 4 frames: 1 a white-violet star at the LOWER LEFT corner of the cell; 2 a violet light streak shooting from it toward the upper right; 3 the streak at the upper right, thin sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the start point at the lower left corner of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `varus_fx_e_rain.png`：E 箭雨落下（地面上，在目标位置），7 帧

E 的箭雨：天上落下一片腐化的紫色箭（十几支细箭从上往下斜着落，箭头朝下），落地的范围是一个扁椭圆（宽是高的 2 倍，半径约 28 格），最后几帧箭插在地上冒出紫红色的腐化光（参考 Arrow_Streaks、varus_arrow_flat_bw、Global_Perma_Freeze、Base_Ring）。约 56 格宽、60 格高（上半部是落下的箭，底部是地上的椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8), a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E).
Effect: a RAIN OF CORRUPTED ARROWS onto a ground area seen from above at an angle, 7 frames: 1 violet streaks appear at the top of the cell; 2-3 twelve slim dark-violet arrows (outlined, glowing tips) falling steeply downward with violet light trails, spread over the width; 4 the arrows strike the ground inside a flattened ellipse twice as wide as tall (56 squares wide) at the bottom of the cell, a crimson-violet flash where each lands; 5 the arrows stuck in the ground, a ring of crimson light over the ellipse; 6 the light fading; 7 fading sparks.
Layout: one horizontal row of 7 equal 14:15 cells, image size 3136x480 (each cell 448x480); the ellipse's center 8 squares (64 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `varus_fx_e_field.png`：E 腐化的地面（循环，4 秒），4 帧

箭雨落下后的地面：一块扁椭圆的腐化地（宽是高的 2 倍），深紫色的地面上冒着紫红色的腐化光、几根插在地上的箭和黑紫色的小尖刺，边缘一圈紫光（参考 Base_Ring、smoke_fade、Global_Perma_Freeze、tendril-thick）。4 帧无缝循环（光一明一暗、几缕紫雾升起）。约 58 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E), a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: a CORRUPTED GROUND PATCH seen from above at an angle, 4 frames, a seamless loop: a flattened ellipse twice as wide as tall (56 squares wide) of dark purple ground with a glowing violet rim, crimson cracks of light inside, 6 arrows stuck upright in it (outlined) and small black-purple thorns; 3 wisps of violet mist rising a square each frame, the cracks pulsing brighter and dimmer.
Layout: one horizontal row of 4 equal 29:15 cells, image size 1856x240 (each cell 464x240); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `varus_fx_e_hit.png`：E 箭雨打中（目标身上），4 帧

被箭雨打中：一支紫色的箭从上往下扎下来，落点一下紫红闪光（参考 HitEffect）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428).
Effect: an ARROW STRIKE FROM ABOVE, 4 frames: 1 a slim violet arrow (outlined) diving down into the center; 2 a crimson-violet flash at the center 10 squares across; 3 sparks flying out; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `varus_fx_e_slow.png`：E 减速 + 重伤：脚下的腐化标记（循环），4 帧

站在腐化地上的敌人：脚下一圈紫红色的腐化光，几根黑紫色的小荆棘缠在脚边（减速和重伤的标记）（参考 tendril-primary、Base_Ring）。中间是人，不要画人。左右对称，4 帧无缝循环。约 18 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428), a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: a CORRUPTION SLOW MARK at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse of crimson-violet light on the ground round the feet (twice as wide as tall), 4 small black-purple thorns (outlined) curling up from its rim, 2 crimson sparks drifting up a square each frame.
Layout: one horizontal row of 4 equal 9:4 cells, image size 2304x256 (each cell 576x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `varus_fx_r_cast.png`：R 甩出锁链：弓前的腐化爆发（施法者身上），4 帧

R「腐败锁链」甩出去的一瞬间：弓前炸开一团紫红色的腐化能量，几根黑紫色的触须往右甩（参考 tendril-primary、R_Secondary_Tendril、shadow_step_red）。朝右画：起点在格子左边中点。约 20 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428), a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: a CORRUPTION BURST at a bow, pointing RIGHT, 4 frames: 1 a crimson-magenta flash at the LEFT MIDDLE of the cell; 2 three black-purple tendrils (outlined, crimson glowing edges) whipping out to the right from that point; 3 the tendrils stretched further right, crimson sparks; 4 fading wisps.
Layout: one horizontal row of 4 equal 5:4 cells, image size 1280x256 (each cell 320x256); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `varus_fx_r_chain.png`：R 飞出去的腐化触须（飞行中循环），4 帧

R 飞出去的锁链：一根黑紫色的腐化触须（像一条扭动的荆棘藤，头部尖锐、带紫红色的发光边），后面拖着紫红色的光（参考 tendril-primary、tendril-thick、R_Secondary_Tendril、root-tendril）。触须有描边。上下对称（扭动在中线上下交替）。约 28 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E), a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: a FLYING CORRUPTION TENDRIL moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC about the middle line: a thorny black-purple tendril 22 squares long and 4 thick (a 1-square dark outline, crimson glowing edges, small thorns), its sharp head pointing right, the body writhing in a gentle wave across the middle line; a crimson-violet glow trailing 6 squares behind it to the LEFT.
Layout: one horizontal row of 4 equal 7:3 cells, image size 2688x384 (each cell 672x288 - keep the 7:3 shape); the head at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `varus_fx_r_hit.png`：R 锁链命中（目标身上），5 帧

锁链打中第一个英雄：一下紫红色的爆闪，几根触须猛地缠上去（参考 HitEffect、root-tendril、shadow_step_red）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428), a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: a TENDRIL STRIKE, 5 frames: 1 a crimson-white flash; 2 a burst of crimson and violet light 18 squares across, 4 short black-purple tendrils (outlined) lashing outward; 3 the tendrils curl back inward; 4 crimson sparks; 5 fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `varus_fx_r_bind.png`：R 禁锢：缠住人的触须（目标身上，循环 2 秒），4 帧

被腐败锁链禁锢的敌人：几根黑紫色的荆棘触须从地上冒出来，缠住他的腿和腰往上绕（参考 root-tendril、tendril-primary、Global_Perma_Freeze）。**只画触须，人的位置留空**：触须在人的两边和前面绕成螺旋，中间能看见人。左右对称或不分左右，4 帧无缝循环（触须慢慢扭动，紫红光沿着走）。约 22 格宽、36 格高，底边贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E), a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: CORRUPTION TENDRILS BINDING a figure (do NOT draw the figure; leave its place empty - the tendrils wind round the empty middle so the figure stays visible), 4 frames, a seamless loop: 4 thorny black-purple tendrils (outlined, crimson glowing edges) rising from a crimson glow on the ground and spiralling up round the figure's place to waist height (24 squares), one reaching the chest (32 squares); a crimson light crawling up along them each frame.
Layout: one horizontal row of 4 equal 11:18 cells, image size 1056x432 (each cell 264x432); the tendrils' base at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `varus_fx_r_spread.png`：R 腐化扩散（地面上，以第一个英雄为中心），6 帧

锁链扩散：从被禁锢的英雄脚下，地面上往外爬出一圈黑紫色的腐化触须和紫红光（扁椭圆，宽是高的 2 倍，半径约 55 格，画的时候外圈约 60 格宽），触须伸向四周（参考 R_Secondary_Tendril、root-tendril、Base_Ring）。中间是人，不要画人。约 60 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E), a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: CORRUPTION SPREADING over the ground from a figure (do NOT draw the figure; leave its place empty), seen from above at an angle, 6 frames: 1 a crimson flash at the center on the ground; 2 a crimson-violet ring expanding over a flattened ellipse twice as wide as tall; 3 eight thorny black-purple tendrils (outlined, crimson edges) crawling outward from the center along the ground to the ellipse's edge (56 squares wide); 4 the tendrils at full length, crimson glow; 5 the tendrils sink, the glow fades; 6 fading wisps.
Layout: one horizontal row of 6 equal 15:8 cells, image size 2880x256 (each cell 480x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `varus_fx_r_spread_hit.png`：R 扩散命中（附近英雄身上），4 帧

锁链扩散到附近的英雄：一根触须从下面窜上来缠住，一下紫红闪光。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428), a dark purple ramp (#8A5CC0, #5E3A88, #3B185F, #261432, #140A1E) and a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8).
Effect: a TENDRIL SNARE, 4 frames: 1 a thorny black-purple tendril (outlined) shooting up from the bottom of the cell; 2 it curls round the center, a crimson flash; 3 crimson sparks; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `varus_fx_p_rage_on.png`：被动 复仇之欲触发：身上爆发的紫光（施法者身上），5 帧

击杀英雄后被动触发：韦鲁斯身上一下爆发紫红色的光，几道光丝往上升（参考 passive_buff_rgb、light_rays、Aura_Self）。中间是人，不要画人。脚在格子底部往上 8 格的中间。约 30 格宽、46 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8), a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F) and a crimson ramp (#FFD0D0, #FF6A6A, #F01A1A, #D32087, #890851, #4A0428).
Effect: a VENGEANCE BURST round a figure (do NOT draw the figure; leave its place empty), 5 frames: 1 a violet-white flash at chest height; 2 a column of violet and crimson light rising round the figure's place, light rays shooting up; 3 violet wisps spiralling up to above the head (40 squares); 4 the wisps thinning; 5 fading sparks.
Layout: one horizontal row of 5 equal 15:23 cells, image size 1200x368 (each cell 240x368); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `varus_fx_p_rage.png`：被动 攻速加成：身上的紫光（循环，5 秒），4 帧

被动攻速加成期间：脚下一圈紫色的光环，几缕紫红色的光丝往上飘（参考 Aura_Self、passive_buff_rgb、Jayce_Aura）。中间是人，不要画人。左右对称，4 帧无缝循环。约 22 格宽、9 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke or sparks (only solid objects - arrows, tendrils, thorns - get a 1-square dark outline #0B0410), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F6D8FF, #E8A0FF, #CA2BFB, #A112F7, #6A1AB8) and a magenta ramp (#FFFFFF, #FFC8F0, #FF70D8, #E838F3, #C0208F).
Effect: a VENGEANCE AURA at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ring of violet light on the ground round the feet (twice as wide as tall, 20 squares wide), 4 magenta wisps rising from its rim a square each frame, small sparks.
Layout: one horizontal row of 4 equal 11:4 cells, image size 2816x256 (each cell 704x256); the ring at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `varus_fx_a_arrow` | view_projectiles `league_varus_a_arrow`（朝右，游戏转到飞行方向，上下对称） | 14 × 5 |
| `varus_fx_a_flash` | view_effects `league_varus_a_flash`（施法者身上，不跟随；格子左边中点放到放箭那一帧的弓弦） | 12 × 10 |
| `varus_fx_a_hit` | view_effects `league_varus_a_hit`（跟随，画在人物上面） | 12 |
| `varus_fx_b_mark` | view_effects `league_varus_b_v1` / `b_v2` / `b_v3`（第 1/2/3 行，跟随，画在人物上面，每次命中播一遍） | 16 × 6 |
| `varus_fx_b_pop` | view_effects `league_varus_b_pop1` / `b_pop2` / `b_pop3`（同一张，按层数放大，跟随，画在人物上面） | 22 |
| `varus_fx_w_pop` | view_effects `league_varus_w_pop`（跟随，画在人物上面） | 28 |
| `varus_fx_w_glow` | view_effects `league_varus_w_glow`（施法者身上，跟随；格子中心放到弓的握把） | 14 × 22 |
| `varus_fx_q_charge` | view_effects `league_varus_q_charge`（施法者身上，跟随；格子中心放到弓的握把）和 `q_charge_s`（快速出手，同一张前 3 帧） | 24 × 24 |
| `varus_fx_q_fire` | view_effects `league_varus_q_fire`（施法者身上，不跟随；格子左边中点放到弓弦） | 24 × 14 |
| `varus_fx_q_arrow` | view_projectiles `league_varus_q_arrow`（满蓄力）和 `q_arrow_s`（快速出手，同一张缩小）（朝右，游戏转到飞行方向，上下对称） | 30 × 10 |
| `varus_fx_q_hit` | view_effects `league_varus_q_hit`（跟随，画在人物上面） | 18 |
| `varus_fx_e_cast` | view_effects `league_varus_e_cast`（施法者身上，跟随第一 tick；格子左下角放到朝右上方的弓弦） | 16 × 16 |
| `varus_fx_e_rain` | view_effects `league_varus_e_rain`（BIG，画在施放点上，不跟随） | 56 × 60 |
| `varus_fx_e_field` | view_projectiles `league_varus_e_field`（BIG，地面，画在人物下面，循环） | 58 × 30 |
| `varus_fx_e_hit` | view_effects `league_varus_e_hit`（跟随，画在人物上面） | 12 |
| `varus_fx_e_slow` | view_buffs `league_varus_e_slow`（循环，画在脚下） | 18 × 8 |
| `varus_fx_r_cast` | view_effects `league_varus_r_cast`（施法者身上，跟随第一 tick；格子左边中点放到 R 第 3 帧的弓） | 20 × 16 |
| `varus_fx_r_chain` | view_projectiles `league_varus_r_chain`（朝右，游戏转到飞行方向，上下对称） | 28 × 12 |
| `varus_fx_r_hit` | view_effects `league_varus_r_hit`（跟随，画在人物上面） | 22 |
| `varus_fx_r_bind` | view_buffs `league_varus_r_bind`（循环，画在人物上面） | 22 × 36 |
| `varus_fx_r_spread` | view_effects `league_varus_r_spread`（BIG，画在命中点，不跟随） | 60 × 32 |
| `varus_fx_r_spread_hit` | view_effects `league_varus_r_spread_hit`（跟随，画在人物上面） | 16 |
| `varus_fx_p_rage_on` | view_effects `league_varus_p_rage_on`（BIG，施法者身上，不跟随） | 30 × 46 |
| `varus_fx_p_rage` | view_buffs `league_varus_p_rage`（循环，画在脚下，人物下面） | 22 × 9 |

- `b_mark` 三行导成 `b_v1`、`b_v2`、`b_v3`；`b_pop` 一张导成 `b_pop1`、`b_pop2`、`b_pop3`（按层数 70% / 85% / 100%）；`q_arrow` 一张导成 `q_arrow` 和缩小的 `q_arrow_s`；`q_charge` 导成 `q_charge` 和只有前 3 帧的 `q_charge_s`。
- 施法者身上的画面按 `design/varus_shots.png` 的十字把起点挪过去；晚于第一 tick 播放的（`a_flash`、`q_fire`、`p_rage_on`）`is_follow` 为 false（红方方向）。
- 飞行物第一帧前加空帧（出生那一 tick 画面朝上、箭还没离开弓）；`r_bind` 画在人物上面，触须只画边；`e_field` 是投射物视图（地面，人物下面）。
- 清掉 Codex 给光和雾描的最深色边（`import_riven.py` 的 `unrim`，实心物体保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
