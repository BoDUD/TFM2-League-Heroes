# 斯特卜：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/steb_design.png`：皮尔特沃夫的鱼人执法官、战地军医，浅海绿皮肤、青绿飞机头、鱼鳍耳，蓝色制服，背着大棕皮背包，两根带黄铜头和青色符文的侧把手警棍）。斯特卜在游戏里是**高清**的（每个游戏格子里约 2.6×2.6 个细像素），41 格高、32 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/steb_size.png`：斯特卜缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里斯特卜自己的特效贴图（**灰色的形状，游戏里再染色**：警棍的海克斯火花、冲击环、治疗的光、地上的圈），按用在我们哪张特效分好了行。只在本地用。
> - **斯特卜的特效是执法官军医的装备**：警棍上**青色的海克斯火花和符文光**、军医的**绿色治疗光和白色小十字**、执法官的**蓝色和金色徽章**、通缉令的**红色准星**；不要火焰，不要闪电，不要黑魔法。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、冲击波、光圈没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：每张都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。这一份没有会飞的图。挥警棍、打针、举棍、下蹲的动作都画在他自己的动作帧里，这里不画。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `steb_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `steb_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/steb_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/steb_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「战地医疗」 | 他受到治疗时，最近的两名队友也回复这次治疗量的 25% | `p_heal` |
| 普攻「双警棍连击」 | 左右两根警棍轮流往前抡 | `a_hit` |
| 技能 1 =「战地医疗」 | 给自己打一针回血，然后一警棍砸在目标身上：魔法伤害 + 短暂眩晕 | `q_heal` · `q_hit` · `q_stun` |
| 技能 2 =「通缉令」 | 给生命值最高的敌人挂上通缉：它受到的伤害更高；它倒下后，他和附近队友攻速提升 | `e_mark` · `e_wanted` · `e_kill` · `e_rush` |
| 大招 =「医疗背包」 | 打开背包：他和周围队友得到护盾，他自己减伤，之后每隔一会儿治疗一次（治疗还会经被动分出去） | `r_pack` · `r_heal` · `r_guard` · `r_shield` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、光圈没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 海克斯青（警棍符文）：`#F0FFFF`、`#A8F4FF`、`#4CD8F0`、`#1C96C8`、`#0C4C7A`；
  - 治疗绿：`#F4FFF0`、`#B4FFB0`、`#5CE878`、`#20A850`、`#0C5A2C`；
  - 金色（徽章、赏金）：`#FFFFFF`、`#FFF0A0`、`#FFD040`、`#D89418`、`#7A4E08`；
  - 执法官蓝：`#E0ECFF`、`#8AB0FF`、`#3E6CE8`、`#2238A0`、`#101C50`；
  - 通缉红（准星）：`#FFE0D8`、`#FF8A70`、`#E8402A`、`#A01818`、`#500A0A`；
  - 速度橙（攻速）：`#FFF4D0`、`#FFC860`、`#F08A20`、`#B04E0C`、`#5A2406`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 不要文字、字母、数字（通缉令用准星和徽章表示，不写 WANTED 字样）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `steb_fx_a_hit.png`：普攻：警棍打中，4 帧

警棍打在人身上：一个白色的**冲击闪光**，一圈**青色的海克斯火花环**，几点金色火星往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08).
Effect: A BATON IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a cyan hextech spark ring 14 squares wide and 6 tall, a few gold sparks (1-2 squares) knocked out to both sides (mirrored); 3 the ring wider and thinner, the sparks farther; 4 the last sparks fading. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `steb_fx_q_heal.png`：技能1 战地医疗：给自己打一针，6 帧

他把警棍按在胸口给自己打一针：胸口一个**绿色的闪光**（小，只在胸前正中），然后一圈绿光从脚下亮起，几个**白色小十字**和绿色光点绕着他往上飘。身体其余位置留空。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a healing green ramp (#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C), a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A).
Effect: A FIELD MEDICINE DOSE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the tall enforcer stands in the middle, not drawn: 31 squares wide and 41 tall: 1 a small bright green flash 6 squares across at his chest (the middle of the cell, a little above the centre) with a cyan glint; 2 a green light ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 28 squares wide and 8 tall at the bottom, a few green motes; 3 several a WHITE CROSS (a plus sign, 3 squares across, a 1-square bar each way) and green motes rising at both sides of him (mirrored); 4 the crosses higher, a faint green glow along his outline at both sides; 5 the crosses near the top, fading; 6 the last glints. The body left empty except the small chest flash. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal 36:44 cells, image size 3456x704 (each cell 576x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `steb_fx_q_hit.png`：技能1：警棍重击打中，6 帧

一警棍重重砸在目标身上：一个大的白色闪光，一圈**粗的青色海克斯冲击波**，几条青色的符文碎光和金色火星往两边飞。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08), an enforcer blue ramp (#E0ECFF, #8AB0FF, #3E6CE8, #2238A0, #101C50).
Effect: A HEAVY HEXTECH BATON STRIKE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white flash 12 squares across; 2 a thick cyan hextech shock ring 20 squares wide and 8 tall, short cyan rune shards and gold sparks thrown out to both sides (mirrored); 3 the ring wider and thinner, a few blue glints; 4 the shards falling; 5 a faint cyan haze; 6 the last specks. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `steb_fx_q_stun.png`：技能1：被砸晕，6 帧循环

被砸晕的人头顶：几个**青色的小齿轮 / 星星**转圈。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08).
Effect: A STUN OVER THE HEAD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small symmetric shapes (3 squares: a cyan cog, a gold star, a cyan star) circling on a flat ring 16 squares wide and 4 tall; frames 1-6 them going round. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal 20:10 cells, image size 1920x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `steb_fx_e_mark.png`：技能2 通缉令：贴上通缉，6 帧

通缉令打在目标身上：头顶上方猛地落下一个**红色的准星**（一个圆圈 + 上下左右四道短线），落定时闪一下，中间一个**金色的执法官徽章**亮起。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crosshair red ramp (#FFE0D8, #FF8A70, #E8402A, #A01818, #500A0A), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08).
Effect: A WANTED MARK SLAMMING DOWN, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big thin RED crosshair (a ring 18 squares across with four short ticks pointing in, up, down, left and right) high in the cell; 2 it shrinking and dropping to the middle, 12 squares across, bright; 3 it locks: a white flash at its centre; 4 a small GOLD shield-shaped badge (5 squares wide, 6 tall) shining in its centre; 5 the crosshair and badge steady; 6 dimmer. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal square cells, image size 2112x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `steb_fx_e_wanted.png`：通缉中：头顶的准星，6 帧循环

被通缉的人头顶一直挂着一个小小的**红色准星 + 金色徽章**，一亮一暗地跳动。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crosshair red ramp (#FFE0D8, #FF8A70, #E8402A, #A01818, #500A0A), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08).
Effect: A WANTED MARK HANGING OVER THE HEAD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small RED crosshair (a ring 10 squares across with four short ticks) around a tiny GOLD badge (3 squares wide, 4 tall); frames 1-6 it pulsing - brighter, a little bigger, back. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal square cells, image size 1344x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `steb_fx_e_kill.png`：通缉犯倒下：领赏，8 帧

被通缉的人倒下了：他头顶闪出一个**大的金色执法官徽章**，徽章四周炸开金光和金色火花，两边几道**橙色的速度光**往上冲。身体位置留空。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08), an orange speed ramp (#FFF4D0, #FFC860, #F08A20, #B04E0C, #5A2406), a crosshair red ramp (#FFE0D8, #FF8A70, #E8402A, #A01818, #500A0A).
Effect: A BOUNTY CLAIMED, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the tall enforcer stands in the middle, not drawn: 31 squares wide and 41 tall: 1 a gold flash 8 squares across over his head; 2 a big GOLD shield-shaped ENFORCER BADGE (10 squares wide, 12 tall, a blue gem in its middle) bursting out over his head with a ring of gold sparks; 3 the badge bright, short ORANGE speed streaks (1 square wide, 6-10 tall) shooting up at both sides of him (mirrored); 4 more streaks, a red crosshair breaking apart behind the badge; 5-6 the streaks rising, the badge glinting; 7 the badge fading; 8 the last glints. The middle (the body) left empty. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 8 equal 40:44 cells, image size 5120x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `steb_fx_e_rush.png`：领赏后：攻速提升，6 帧循环

领了赏的队友身上：身体两侧几道**橙色的速度光**一闪一闪往上窜，脚下一圈淡淡的橙光。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange speed ramp (#FFF4D0, #FFC860, #F08A20, #B04E0C, #5A2406), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08).
Effect: AN ATTACK SPEED RUSH, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a champion stands in the middle, not drawn: 20 squares wide and 36 tall: at both sides (mirrored) short ORANGE speed streaks (1 square wide, 5-8 tall) flicking upward along the outline, a faint orange ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 24 squares wide and 6 tall at the bottom, a few gold sparks; frames 1-6 the streaks rising and flickering. The middle (the body) left empty. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal 30:40 cells, image size 2880x640 (each cell 480x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `steb_fx_p_heal.png`：被动 战地医疗：分到治疗，6 帧

他受到治疗时，最近的队友也回一点血：那个队友身上冒出两三个**白色小十字**和绿色光点往上飘，脚下一个小小的绿圈。身体位置留空。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a healing green ramp (#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C).
Effect: A SHARED HEAL, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a champion stands in the middle, not drawn: 20 squares wide and 36 tall (smaller cell: the crosses at both sides): 1 a small green ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 18 squares wide and 5 tall at the bottom; 2 two a WHITE CROSS (a plus sign, 3 squares across, a 1-square bar each way) appearing at both sides of the body (mirrored), green motes; 3-4 them rising and a third one over the head; 5 fading at the top; 6 the last motes. The middle (the body) left empty. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal 24:32 cells, image size 2304x512 (each cell 384x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `steb_fx_r_pack.png`：大招 医疗背包：地上的医疗圈，8 帧

他打开背包：脚下的地上亮起一个**大的绿色医疗圈**（从斜上方看的椭圆），圈上一圈小的**白色十字**和青色的海克斯刻度，圈里铺着淡淡的绿光，从中间往外扩。**左右对称**，8 帧（地上的图，不画人）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a healing green ramp (#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C), a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A).
Effect: A MEDIC'S CIRCLE ON THE GROUND, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), lying on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a bright green ring 20 squares wide and 7 tall in the middle; 2 it spreading to 50 x 17, a white flash along it; 3 the full ring 80 squares wide and 26 tall, a thin second ring inside, eight small a WHITE CROSS (a plus sign, 3 squares across, a 1-square bar each way) evenly round it (mirrored), cyan hextech tick marks between them, a faint green fill; 4-6 the ring steady, the crosses glinting one pair after another, green motes rising a little from the ring; 7 dimmer; 8 only the crosses glinting. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 8 equal 84:30 cells, image size 10752x480 (each cell 1344x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `steb_fx_r_heal.png`：大招：一次治疗脉冲，5 帧

医疗背包每隔一会儿治疗一次：人身上一圈**绿光从脚下往上扫过**，几个白色小十字跟着往上飘。身体位置留空（只画外圈和脚下）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a healing green ramp (#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C).
Effect: A HEALING PULSE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a champion stands in the middle, not drawn: 20 squares wide and 36 tall: 1 a green ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 24 squares wide and 7 tall at the bottom; 2 a band of green light sweeping up both sides of the outline (mirrored), two a WHITE CROSS (a plus sign, 3 squares across, a 1-square bar each way); 3 the band at the shoulders, more crosses; 4 crosses over the head; 5 fading motes. The middle (the body) left empty. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 5 equal 30:40 cells, image size 2400x640 (each cell 480x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `steb_fx_r_guard.png`：大招：他自己减伤，6 帧循环

打开背包时他自己减伤：身体两侧各立着一块半透明的**蓝色执法官盾牌**的轮廓（金边、上面一道青色的海克斯光纹），一闪一闪。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an enforcer blue ramp (#E0ECFF, #8AB0FF, #3E6CE8, #2238A0, #101C50), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08), a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A).
Effect: AN ENFORCER GUARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the tall enforcer stands in the middle, not drawn: 31 squares wide and 41 tall: at both sides of him (mirrored) a tall riot SHIELD outline 6 squares wide and 26 tall - a BLUE rim with GOLD corners and a thin cyan hextech line down its middle, only the rim and the line drawn (see-through inside); frames 1-6 a glint running up each shield and the cyan line pulsing. The middle (the body) left empty. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal 40:44 cells, image size 3840x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `steb_fx_r_shield.png`：大招：队友的护盾，6 帧循环

队友身上的护盾：一圈淡淡的**青绿色海克斯护罩**的边（只画外圈的六边形格子边），几格六边形一闪一闪。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A), a healing green ramp (#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C).
Effect: A HEXTECH BARRIER, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a champion stands in the middle, not drawn: 20 squares wide and 36 tall: the RIM of a rounded barrier 28 squares wide and 38 tall around the unit, drawn as a band of small hexagon cells 2 squares wide in cyan with a hint of green, only the rim (the middle and the body left empty); frames 1-6 a few hexagons on both sides lighting up in turn (mirrored), a glint running round. everything is a city ENFORCER-MEDIC's gear: crisp HEXTECH cyan sparks and rune glints from his batons, a medic's soft GREEN healing light with little WHITE CROSSES (plus signs), the enforcers' BLUE and GOLD badge, a RED crosshair for the WANTED mark; flat shades, crisp shapes; no flames, no lightning, no dark magic.
Layout: one horizontal row of 6 equal 30:40 cells, image size 2880x640 (each cell 480x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `steb_icon_skill.png`：技能 1「战地医疗」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little gold corner rivets, a deep blue-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a blue steel SIDE-HANDLE BATON (a tonfa: a brass head with glowing cyan runes at one end, a silver-grey rod at the other, a wooden side grip) lying diagonally from the lower left to the upper right, its glowing brass head at the upper right, crossed behind by a big bright green MEDICAL CROSS with a white core, a few cyan sparks; colours from a hextech cyan ramp (#F0FFFF, #A8F4FF, #4CD8F0, #1C96C8, #0C4C7A), a healing green ramp (#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08). No text, no letters.
```

### 图标 2. `steb_icon_skill2.png`：技能 2「通缉令」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little gold corner rivets, a deep blue-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big RED CROSSHAIR (a ring with four ticks) over a GOLD shield-shaped ENFORCER BADGE with a blue gem in its middle, a white glint on the badge; colours from a crosshair red ramp (#FFE0D8, #FF8A70, #E8402A, #A01818, #500A0A), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08), an enforcer blue ramp (#E0ECFF, #8AB0FF, #3E6CE8, #2238A0, #101C50). No text, no letters.
```

### 图标 3. `steb_icon_ult.png`：大招「医疗背包」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little gold corner rivets, a deep blue-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big BROWN LEATHER BACKPACK seen from the front, its flap thrown open, bright GREEN light and two WHITE CROSSES spilling up out of it, gold buckles; colours from a brown leather ramp (#E8B070, #B07038, #7A4420, #4A2610), a healing green ramp (#F4FFF0, #B4FFB0, #5CE878, #20A850, #0C5A2C), a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #D89418, #7A4E08). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `steb_fx_a_hit` | view_effects `tft_steb_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `steb_fx_q_heal` | view_effects `tft_steb_q_heal`（跟随他，z 3；左右对称） | 36 × 44 |
| `steb_fx_q_hit` | view_effects `tft_steb_q_hit`（跟随目标，z 2；左右对称） | 24 × 24 |
| `steb_fx_q_stun` | view_buffs `tft_steb_q_stun`（跟随被晕的人，头顶，z 3；左右对称） | 20 × 10 |
| `steb_fx_e_mark` | view_effects `tft_steb_e_mark`（跟随目标，头顶，z 4；左右对称） | 22 × 22 |
| `steb_fx_e_wanted` | view_buffs `tft_steb_e_wanted`（跟随被通缉的人，头顶，z 4；左右对称） | 14 × 14 |
| `steb_fx_e_kill` | view_effects `tft_steb_e_kill`（跟随他，z 3；左右对称） | 40 × 44 |
| `steb_fx_e_rush` | view_buffs `tft_steb_e_rush`（跟随队友，身上，z 3；左右对称） | 30 × 40 |
| `steb_fx_p_heal` | view_effects `tft_steb_p_heal`（跟随队友，z 3；左右对称） | 24 × 32 |
| `steb_fx_r_pack` | view_effects `tft_steb_r_pack`（大表，在他脚下的地上，z -1；左右对称） | 84 × 30 |
| `steb_fx_r_heal` | view_effects `tft_steb_r_heal`（跟随他和每个队友，z 3；左右对称） | 30 × 40 |
| `steb_fx_r_guard` | view_buffs `tft_steb_r_guard`（跟随他，z 3；左右对称） | 40 × 44 |
| `steb_fx_r_shield` | view_buffs `tft_steb_r_shield`（跟随队友，z 3；左右对称） | 30 × 40 |
| `steb_icon_skill` | skill_icons[0] `asset/tft/icons/tft_steb_skill` | 64 × 64 |
| `steb_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_steb_skill2` | 64 × 64 |
| `steb_icon_ult` | skill_icons[2] `asset/tft/icons/tft_steb_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_steb_fx`（小的）和 `tft_steb_big`（r_pack），tag = 名字。
- 全部断言左右对称。r_pack 在地上（z -1，不跟随）。
- p_heal、e_kill、e_rush 由 tft.dll 播 / 挂上（--plain 的数据没有：分享治疗按范围给、没有赏金）。
- 用 `pixel_1x/` 切格（import_renni_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
