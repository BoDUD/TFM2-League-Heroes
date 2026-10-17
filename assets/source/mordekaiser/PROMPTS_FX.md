# 莫德凯撒 铁铠冥魂：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已定：重甲巨人扛着大锤（`design/mordekaiser_idle.png`，游戏里连锤子约 34 格宽、50 格高，图是高清帧，游戏里按 5 倍密度显示）。特效照常按游戏像素画（1 格 = 1 个游戏像素），和其他英雄一样。
> - 大小对照 `design/mordekaiser_size.png`：他和原版斗士按游戏大小放大 4 倍，红线是地面，上面是 10 格一段的刻度。每条写的大小都是游戏像素（格）。
> - `design/mordekaiser_shots.png`：定稿动作（游戏大小 x4），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里莫德凯撒自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。颜色照英雄联盟原版：**青绿色的灵魂光**（被动、E 鬼爪、R 领域）、**黑色的烟**、铁灰色碎片、Q 砸地的灰色碎石和尘土。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **方向（重要，红色方会镜像）**：两条直线（`q_crack` 地裂、`e_beam` 鬼爪）画成朝右，游戏会按施法方向转，而且要**上下对称**（往左放时会上下翻）。其余所有画面（打中、光环、护盾、漩涡、头顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `mordekaiser_fx_<名字>.png` 和原尺寸的 `pixel_1x/`，附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `mordekaiser_fx_pack_done.zip`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「黑暗起兮」 | 锤子砸人；叠满 3 层后身边一圈黑暗光环持续烧周围的敌人 | `a_hit` · `p_aura` · `p_hit` |
| 技能 1 = Q「破灭之锤」 | 锤子砸地，往前裂开一条直线；只砸中一个人时更重 | `q_crack` · `q_slam` · `q_hit` · `q_iso_hit` |
| 技能 2 = E「断魂一扼」+ W「不坏之身」 | 甩出鬼爪把敌人拉过来；被贴脸时升起护盾，最后化成生命 | `e_beam` · `e_hit` · `w_shield` · `w_heal` |
| 大招 = R「轮回绝境」 | 诅咒对面核心，把两人拖进死亡领域单挑（原地留漩涡）；跑远被拉回；领域里击杀吸走灵魂 | `r_cast` · `r_mark` · `r_realm` · `r_pull` · `r_win` · `r_curse` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、尘土、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 灵魂青绿：`#FFFFFF`、`#D8FFF8`、`#7CFFEE`、`#22E0D0`、`#0E9C98`、`#0A5A5C`；
  - 黑烟：`#5A6478`、`#343A48`、`#1E2230`、`#0E1016`；
  - 铁色碎片：`#E0E6F0`、`#A8B0C0`、`#6E7688`、`#3E4452`；
  - 碎石尘土：`#E6DCC8`、`#B8AC94`、`#8A7E6A`、`#5C5446`；
- 打中、爆发居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在人身上、脚下的画面按每条写的站位画，**格子里留出空的位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，被动光环半径 24000，Q 直线 42000 长、半宽 6000，E 直线 54000 长、半宽 6000）。

### 1. `mordekaiser_fx_a_hit.png`：普攻打中（目标身上），4 帧

锤子砸中：中间一下灰白色的金属冲击闪光，四周溅出几块铁色碎片和一点青绿色的灵魂火星（参考 AutoAttackSwipe、Z_Flash）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an iron ramp (#E0E6F0, #A8B0C0, #6E7688, #3E4452) and a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C).
Effect: a HEAVY MACE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-grey impact flash 5 squares across; 2 an iron starburst 11 squares across with 4-6 blunt rays and two teal sparks at mirrored places; 3 iron shards and teal sparks flying out at mirrored places; 4 a few fading shards.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `mordekaiser_fx_p_aura.png`：被动「黑暗起兮」光环（他脚下，每 0.5 秒一下），4 帧

叠满 3 层后他身边的黑暗光环：地上一圈扁椭圆的暗色旋风（约 48 格宽、16 格高），里面绕着几缕青绿色的灵魂火和黑烟（参考 Passive_Ring、Passive_Cyclone、Passive_RipplesEdge）。**左右对称**。每 0.5 秒播一次，4 帧连起来像在转。**椭圆中间（他站的地方，约 20 格宽）留空**，只画外圈。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a DARK AURA RING on the ground, 4 frames played once every half second, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse 48 squares wide and 16 tall, its middle 20 squares wide EMPTY; along the ring dark smoke wisps (2-4 squares thick) and 4-6 short teal soul-flame tongues at mirrored places, all moving a little each frame as if circling; frame 1 the ring forming brighter, frames 2-3 swirling, frame 4 fading.
Layout: one horizontal row of 4 equal 52:20 cells, image size 3328x320 (each cell 832x320, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `mordekaiser_fx_p_hit.png`：被动光环烧到的敌人（身上），3 帧

被黑暗光环烧到：身上冒起一小团青绿色的灵魂火和黑烟，一闪就没。**左右对称**。约 10 格，要小、要快。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a SMALL SOUL BURN on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two teal flame tongues 3-4 squares tall at mirrored places with a white core; 2 the flames taller with a wisp of dark smoke; 3 fading smoke.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `mordekaiser_fx_q_crack.png`：Q 破灭之锤砸出的地裂（一条直线，0.4 秒），6 帧

锤子砸地后，从他身前往目标方向裂开的一条地面裂纹：一道锯齿状的暗色裂缝，裂缝里透出青绿色的光，两边翻起碎石和尘土（参考 Q_GroundHit、Q_Ground_ShockWave、Q_Impact_Dust）。**画成朝右的一条横线，上下对称**（往左放时游戏会上下翻）。6 帧依次播放：裂开、发光、尘土扬起、变暗消失。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C), a stone dust ramp (#E6DCC8, #B8AC94, #8A7E6A, #5C5446) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a GROUND CRACK LINE pointing to the RIGHT, 6 frames played once, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it toward the cast; cast to the left it is flipped upside down): a jagged dark crack 42 squares long (2-3 squares wide) along the middle with teal light glowing inside it; frame 1 the crack running out from the left end to two thirds; frame 2 the whole length, the teal glow brightest; frame 3 stone dust and small rubble puffing up on both sides (mirrored top to bottom), 4-5 squares out; frame 4 the dust higher, the glow dimmer; frame 5 fading dust; frame 6 only the dark crack.
Layout: one horizontal row of 6 equal 46:16 cells, image size 4416x256 (each cell 736x256, 16 px a square); the line along the middle of each cell, from 2 squares in at the left to 2 squares in at the right. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `mordekaiser_fx_q_slam.png`：Q 锤子砸地的冲击（他身前，留在原地），5 帧

砸地那一下：他脚下一圈扁椭圆的冲击波，地面裂开几道短裂纹，碎石和灰尘往两边扬起（参考 Q_Ground_ShockWave、Rocks、Impact_Dust）。**左右对称**，中间上半部分留空（不要挡住他）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone dust ramp (#E6DCC8, #B8AC94, #8A7E6A, #5C5446) and a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C).
Effect: a GROUND SLAM SHOCKWAVE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the upper middle 12 squares wide EMPTY: 1 a white-teal flash 8 squares across at the bottom middle; 2 a ring of dust and teal light bursting out, an ellipse 20 squares wide and 6 tall, 4 short cracks at mirrored places; 3 the ring at 28 x 9, rubble chunks flying at mirrored places; 4 dust puffs rising; 5 fading dust.
Layout: one horizontal row of 5 equal 32:16 cells, image size 2560x256 (each cell 512x256, 16 px a square); centered across, the ring's middle 4 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `mordekaiser_fx_q_hit.png`：Q 砸中（被砸中的人身上），4 帧

被锤子砸中：一团青绿色和铁灰色的冲击闪光，碎片溅开。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and an iron ramp (#E0E6F0, #A8B0C0, #6E7688, #3E4452).
Effect: a SMASH HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-teal flash 6 squares; 2 a teal-and-iron starburst 13 squares across; 3 shards and teal sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `mordekaiser_fx_q_iso_hit.png`：Q 孤立砸中（只砸中一个人，更重），5 帧

只砸中一个敌人时伤害更高：比上一张更大更亮，中间一团白色到青绿色的爆裂，外面一圈青绿色的冲击环（参考 Q_GroundHitGlow）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and an iron ramp (#E0E6F0, #A8B0C0, #6E7688, #3E4452).
Effect: a HEAVY ISOLATED SMASH on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares; 2 a white-teal burst 16 squares across with sharp rays; 3 a teal ring 20 squares across around fading rays, iron shards at mirrored places; 4 the ring breaking into teal sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `mordekaiser_fx_e_beam.png`：E 断魂一扼（从他手里伸出去的一道鬼爪，0.3 秒），5 帧

他伸手甩出的鬼爪：一道青绿色的灵魂光束从左端（他的手）往右伸出去，右端是一只张开的幽灵爪子（三根爪尖，上下对称排列），然后爪子收拢、光束往回拉（参考 E_Cast_Beam、E_Cast_Trail、E_Souls、E_Slash_A）。**画成朝右的一条横线，上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a GHOSTLY GRASPING BEAM pointing to the RIGHT, 5 frames played once, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it toward the cast; cast to the left it is flipped upside down): frame 1 a teal soul beam 3 squares thick shooting from the left end to the middle; frame 2 the beam reaching the right end, an open spectral claw there 10 squares tall with three hooked claw tips spread up, middle and down (mirrored top to bottom), white-teal core; frame 3 the claw closing (the tips curling in), dark smoke wisps along the beam; frame 4 the beam pulling back toward the left, the claw small; frame 5 fading wisps.
Layout: one horizontal row of 5 equal 58:14 cells, image size 4640x224 (each cell 928x224, 16 px a square); the beam along the middle of each cell, from 1 square in at the left to 1 square in at the right. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `mordekaiser_fx_e_hit.png`：E 抓中（被拉的人身上），4 帧

被鬼爪抓住：几道青绿色的爪痕从两边往中间合拢，身上冒一圈暗色的烟（参考 E_Slash_A、E_Souls）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a CLAW GRIP on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 three teal claw streaks on each side, 6 squares long, curving in toward the middle (mirrored); 2 the streaks meeting in the middle with a white-teal flash; 3 a ring of dark smoke 14 squares across with teal sparks; 4 fading smoke.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `mordekaiser_fx_w_shield.png`：W 不坏之身的护盾（他身上），6 帧

护盾升起：他身体四周一圈青绿色的灵魂碎片和铁色的盔甲碎片往上飞旋，聚成一个竖着的椭圆光圈（参考 W_Glow、W_LightRay、W_Small_Mote、W_Concuss）。**左右对称**。**中间（他的身体，约 18 格宽、30 格高）留空**，只画外圈。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and an iron ramp (#E0E6F0, #A8B0C0, #6E7688, #3E4452).
Effect: a SHIELD AURA around a big body, 6 frames played once, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle 18 squares wide and 30 tall EMPTY: 1 teal motes rising from the ground at mirrored places; 2 the motes and small iron shards spiralling up both sides; 3 a tall teal ellipse outline 28 squares wide and 38 tall forming from them (2 squares thick, white highlights); 4 the ellipse full and bright; 5 the ellipse thinner, motes drifting off; 6 a few fading motes.
Layout: one horizontal row of 6 equal 32:42 cells, image size 3072x672 (each cell 512x672, 16 px a square); centered across, the ellipse's bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `mordekaiser_fx_w_heal.png`：W 消耗护盾回血（他身上），5 帧

护盾化成生命：几缕青绿色的灵魂从他身边往上升，在头顶附近散开成亮点（参考 W_LightRay、W_Small_Mote）。**左右对称**，中间身体部分只画细的升起光线，不要整块盖住他。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C).
Effect: a SOUL HEAL rising, 5 frames played once, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 four teal soul wisps 2 squares wide at the bottom at mirrored places; 2 the wisps rising 12 squares, curling; 3 the wisps at the top, bright white-teal heads; 4 the wisps bursting into small teal stars at the top; 5 fading stars.
Layout: one horizontal row of 5 equal 24:34 cells, image size 1920x544 (each cell 384x544, 16 px a square); centered across, the wisps starting at the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `mordekaiser_fx_r_cast.png`：R 轮回绝境出手（他身上，留在原地），7 帧

开大那一下：他周围炸开一团暗绿色到黑色的漩涡，里面窜出几道青绿色的灵魂闪电（参考 R_Malestrom、R_SoulLightning、R_energy_ball）。**左右对称**。中间（他的身体，约 16 格宽、28 格高）只留细的闪电，不要整块挡住他。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a DARK VORTEX BURST, 7 frames played once, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle 16 squares wide and 28 tall nearly EMPTY (only thin lightning crossing it): 1 a teal flash 8 squares at the middle; 2 a dark smoke ring 24 squares across spinning out; 3 the ring 36 squares across with 4 jagged teal lightning bolts at mirrored places; 4 the lightning reaching outward, dark wisps; 5 the ring breaking into dark wisps; 6 fading wisps and sparks; 7 a few sparks.
Layout: one horizontal row of 7 equal 42:34 cells, image size 4704x544 (each cell 672x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `mordekaiser_fx_r_mark.png`：R 被诅咒的人（身上，开大那一下），5 帧

被诅咒：身上浮现一个青绿色的诅咒印记（像他头盔的冠形），一闪后化成青烟（参考 R_Crown_Glow、R_CausticSpecter）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a CURSE SIGIL on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-teal flash 6 squares; 2 a teal crown-shaped sigil 12 squares wide (three upward spikes, the middle one tallest) with a ring under it; 3 the sigil bright with dark smoke around; 4 the sigil breaking into teal motes; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `mordekaiser_fx_r_realm.png`：R 死亡领域（两人被拖进去后原地留下的漩涡，循环），8 帧

两人被拖进领域后，原地留下的一个暗色领域入口：地上一圈扁椭圆的黑绿色漩涡（约 44 格宽），外圈是一道青绿色的灵魂墙光边，里面的黑烟和青色丝线一圈圈往中间转（参考 R_Malestrom、R_SoulWall、R_Tendrils、R_Ground_A）。**左右对称**。8 帧**无缝循环**（会一直播到领域结束）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C) and a dark smoke ramp (#5A6478, #343A48, #1E2230, #0E1016).
Effect: a DARK REALM PORTAL on the ground, 8 frames, a SEAMLESS LOOP, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse 44 squares wide and 14 tall, its rim a teal soul-light wall 2 squares thick with short upright teal flames along it (3-6 squares tall) at mirrored places; inside, black-green smoke and thin teal threads spiralling toward the middle, the pattern advancing a little each frame so frame 8 leads back into frame 1; a soft darker core in the middle.
Layout: one horizontal row of 8 equal 48:26 cells, image size 6144x416 (each cell 768x416, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `mordekaiser_fx_r_pull.png`：R 拉回（跑远的被诅咒者身上），4 帧

跑远了被拉回：身上缠起一圈青绿色的灵魂锁链光，往中间一收（参考 R_SoulTether）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C).
Effect: a SOUL TETHER YANK on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal ring 12 squares across made of short chain-like dashes; 2 the ring tightening to 8 squares, brighter; 3 a white-teal flash at the middle; 4 fading motes.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `mordekaiser_fx_r_win.png`：R 领域里击杀（他身上，吸走灵魂），6 帧

领域里杀死对手：一团青绿色的灵魂从上方旋转落进他身体，身上闪一下（参考 R_Wispy、R_energy_ball）。**左右对称**，中间身体部分只画细的灵魂丝，不要整块盖住他。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C).
Effect: a SOUL ABSORBED, 6 frames played once, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal soul orb 6 squares wide at the top middle with two wisp tails curling down at mirrored places; 2 the orb lower, the tails spiralling; 3 the orb at the chest height splitting into wisps that wrap both sides; 4 a white-teal flash ring 20 squares across at the middle; 5 motes rising; 6 fading motes.
Layout: one horizontal row of 6 equal 28:36 cells, image size 2688x576 (each cell 448x576, 16 px a square); centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `mordekaiser_fx_r_curse.png`：R 诅咒（被诅咒的人头顶，循环），4 帧

被诅咒期间头顶一个小小的青绿色冠形印记（三根尖），轻轻闪。**左右对称**。4 帧无缝循环，画在格子上部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, dust or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghost-teal soul ramp (#FFFFFF, #D8FFF8, #7CFFEE, #22E0D0, #0E9C98, #0A5A5C).
Effect: a SMALL CURSE CROWN above a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a crown shape 7 squares wide and 5 tall in teal with a light rim (three spikes, the middle one tallest), pulsing brighter on frames 2-3.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered across, the crown in the top half of the cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `mordekaiser_fx_a_hit` | view_effects `league_mordekaiser_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `mordekaiser_fx_p_aura` | view_effects `league_mordekaiser_p_aura`（跟随，画在人物下面一层；左右对称） | 50 × 18 |
| `mordekaiser_fx_p_hit` | view_effects `league_mordekaiser_p_hit`（跟随，画在人物上面；左右对称） | 10 |
| `mordekaiser_fx_q_crack` | view_projectiles `league_mordekaiser_q_crack`（朝施法方向转，画成朝右；上下对称） | 44 × 14 |
| `mordekaiser_fx_q_slam` | view_effects `league_mordekaiser_q_slam`（不跟随，画在人物下面一层；左右对称） | 30 × 14 |
| `mordekaiser_fx_q_hit` | view_effects `league_mordekaiser_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `mordekaiser_fx_q_iso_hit` | view_effects `league_mordekaiser_q_iso_hit`（跟随，画在人物上面；左右对称） | 20 |
| `mordekaiser_fx_e_beam` | view_projectiles `league_mordekaiser_e_beam`（朝施法方向转，画成朝右；上下对称） | 56 × 12 |
| `mordekaiser_fx_e_hit` | view_effects `league_mordekaiser_e_hit`（跟随，画在人物上面；左右对称） | 16 |
| `mordekaiser_fx_w_shield` | view_effects `league_mordekaiser_w_shield`（跟随，画在人物上面；左右对称） | 30 × 40 |
| `mordekaiser_fx_w_heal` | view_effects `league_mordekaiser_w_heal`（跟随，画在人物上面；左右对称） | 22 × 32 |
| `mordekaiser_fx_r_cast` | view_effects `league_mordekaiser_r_cast`（不跟随，画在人物上面；左右对称） | 40 × 32 |
| `mordekaiser_fx_r_mark` | view_effects `league_mordekaiser_r_mark`（跟随，画在人物上面；左右对称） | 16 |
| `mordekaiser_fx_r_realm` | 附加包放逐时的画面 `league_mordekaiser_r_realm`（不跟随，画在人物下面一层；左右对称；循环播放约 7 秒） | 46 × 24 |
| `mordekaiser_fx_r_pull` | view_effects `league_mordekaiser_r_pull`（跟随，画在人物上面；左右对称） | 14 |
| `mordekaiser_fx_r_win` | view_effects `league_mordekaiser_r_win`（跟随，画在人物上面；左右对称） | 26 × 34 |
| `mordekaiser_fx_r_curse` | view_buffs `league_mordekaiser_r_curse`（跟随，画在人物上面；左右对称） | 10 × 6 |

- 两张表：`asset/league/effects/league_mordekaiser_fx`（小的）和 `league_mordekaiser_big`（p_aura、q_crack、q_slam、e_beam、r_cast、r_realm），tag = 名字（build_mordekaiser.py 的 views；r_realm 由附加包放逐时播放）。
- `q_crack`、`e_beam` 是只带画面的 LineRangeProjectile（画在直线中点，朝施法方向转）；`q_slam`、`r_cast`、`r_realm` 不跟随；`p_aura`、`q_slam`、`r_realm` 画在人物下面（z -1）；`r_curse` 头顶 buff（z 3）。
- 用 `pixel_1x/` 切格（import_gragas 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
