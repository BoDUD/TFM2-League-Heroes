# 艾达丝：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图 + 3 个技能图标。** 造型已定（`design/idas_design.png`：正侧面朝右、两条反关节腿直立的金色巨龙，有棱角的金鳞甲、深棕的胸腹、青蓝宝石，龙头上青蓝的鬃冠和角，发光的青蓝眼睛；两只翅膀手臂，前臂上是金色的羽刃翼，手腕上是深灰三指爪；长尾巴尖上一片刀刃）。艾达丝在游戏里是**高清**的（每个游戏格子里约 2.45×2.45 个细像素），40 格高、52 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/idas_size.png`：艾达丝缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里艾达丝自己的特效贴图（熔金的流体、降护甲的标记、护盾模板、龙鳞、金币）和英雄联盟里洛（Rakan）护盾、回血的贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **艾达丝是金鳞龙，特效都是金色的龙的魔法**：熔金、金光、一片片**有棱角的金色龙鳞**（像她身上的鳞甲）、几枚闪光的金币，点缀她自己的**青蓝色**（宝石、鬃冠的颜色）；不要火、不要红色、不要紫色，不要光滑的霓虹光束。
> - **特效要亮**：每团光都有最亮一档或白金色的芯，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**。
> - **护盾和围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：画在人身上和地上的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**飞行的画面（q_breath）朝右、严格上下对称**（游戏会按方向转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `idas_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `idas_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/idas_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/idas_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「护卫之誓」 | 血量低于一半时，她和最近的一名队友各得一层金鳞护盾（30 秒一次） | `p_burst` · `p_shield` |
| 普攻「龙爪」 | 往前扑一爪 | `a_hit` |
| 技能 1 =「黄金龙息」 | 往前喷一片扇形的熔金龙息：魔法伤害、降低护甲 | `q_breath` · `q_shred` |
| 技能 2 =「龙威振翅」 | 振翅一吼：附近敌人眩晕一下并减速，她和附近队友得一层小护盾 | `e_roar` · `e_slow` · `e_shield` |
| 大招 =「黄金龙鳞」 | 双翼裹身、金鳞外壳减伤 2 秒，然后外壳炸开：回血，附近队友得护盾，护盾在时攻速提高 | `r_wrap` · `r_burst` · `r_heal` · `r_shield` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 金色（熔金、金光、金鳞、金币）：`#FFFFFF`、`#FFF6C8`、`#FFE07A`、`#FFC23A`、`#E8920E`、`#A85E08`；
  - 她的青蓝（宝石、边上的光、图标的角）：`#F0FFFF`、`#9AF6FA`、`#2ED2E0`、`#108A9E`；
  - 回血的绿光：`#F8FFE8`、`#D6F79A`、`#8EDC5E`、`#3E9E4A`；
  - 尘土：`#F6EAC8`、`#CDB88A`、`#92784E`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `idas_fx_a_hit.png`：普攻：龙爪打中，4 帧

龙爪打中：三道金色的爪痕交叉成一个对称的「米」字闪光，中间一下白光，几片小金鳞崩飞出去。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08).
Effect: A CLAW HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 4 squares across; 2 three short golden claw rakes crossing over it in a symmetric star (one upright, two leaning out to each side), a few tiny golden scale chips flying out; 3 the rakes thinner, the chips farther; 4 a few fading gold sparks. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `idas_fx_q_breath.png`：黄金龙息：喷出的金色龙息，6 帧循环

她喷出的**金色龙息**：从左端（她的嘴）往右喷出一道越来越宽的熔金洪流，像一把扇子，里面翻滚着金光、熔化的金滴和几片金鳞，边上一点青色的光。左端窄（嘴边约 6 格高），右端最宽（约 20 格高）。**朝右、上下对称**，6 帧循环（洪流翻滚）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a cyan gem ramp (#F0FFFF, #9AF6FA, #2ED2E0, #108A9E).
Effect: A GOLDEN DRAGON BREATH, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a cone of MOLTEN GOLD breath pouring out from the LEFT edge (6 squares tall there: her mouth) to the RIGHT, widening to 20 squares tall at the right end like a fan; inside it rolling waves of golden light with a white-gold core along the middle, drops of molten gold and a few small golden scales tumbling in it, a thin cyan glint along its two edges; frames 1-6 the waves rolling to the right. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:22 cells, image size 5376x352 (each cell 896x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `idas_fx_q_shred.png`：黄金龙息：护甲被熔，6 帧循环

护甲被熔化：被喷到的人肩头和胸前粘着几块正在往下滴的熔金，旁边一块裂开的小金色盾牌碎片（表示护甲降低），每隔一会儿掉下一滴金。**左右对称**，6 帧循环。身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08).
Effect: MOLTEN ARMOUR, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the unit stands in the middle, not drawn: 16 squares wide and 36 tall; molten gold clinging to the unit's shoulders (two small blobs, one each side, 3 squares across) dripping down the sides, a tiny CRACKED golden shield shard above the head (4 squares, split by a crack) showing the armour broken; frames 1-6 one drop of gold running down and falling off each side. Only at the shoulders, the sides and above the head: the body area stays EMPTY. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 18:26 cells, image size 1728x416 (each cell 288x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `idas_fx_e_roar.png`：龙威振翅：振翅一吼的冲击波，6 帧

她振翅一吼：她身边炸开一圈金色的冲击波（一个往外扩的椭圆环，宽是高的 2 倍左右），两边各一道金色的翅风弧线往外扫，环上带几片金鳞和一点尘土。她在中间，**身体位置留空**。**左右对称**，6 帧（环越扩越大、越来越淡）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a light dust ramp (#F6EAC8, #CDB88A, #92784E).
Effect: A DRAGON'S ROAR SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the golden dragon stands in the middle, not drawn: 52 squares wide and 40 tall, her head at the upper right; 1 a bright golden ring tight round her body (an ellipse twice as wide as tall), 2-3 the ring bursting outward to 60 squares wide, two sweeping golden wind arcs (one each side) curving out from her wings, a few golden scales and puffs of light dust riding on the ring; 4-6 the ring at the cell's edge, thinner, breaking into fading golden dashes. The ring only: her body area stays EMPTY. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 64:44 cells, image size 6144x704 (each cell 1024x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `idas_fx_e_slow.png`：龙威振翅：被震慑减速，6 帧循环

被减速：被吼到的人脚下一圈沉甸甸的金色鳞片（一个从斜上方看的椭圆，宽是高的 3 倍），鳞片之间压着几道往下的金色小箭头。**左右对称**，6 帧循环（鳞片微微闪光）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08).
Effect: A HEAVY SLOW, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet, an ellipse seen from above, about 18 squares wide and 6 tall: a ring of heavy faceted golden scales lying on the ground, between them three small golden arrows pointing DOWN; frames 1-6 a glint running round the scales. Nothing above the feet. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:10 cells, image size 1920x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `idas_fx_e_shield.png`：龙威振翅：队友的小护盾，6 帧循环

队友身上的小护盾：一圈淡淡的、由一片片金色小鳞片拼成的蛋形护盾轮廓，**里面是空的**，人从中间露出来；轮廓上一点青色宝石光。**左右对称**，6 帧循环（一道光沿着轮廓转）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a cyan gem ramp (#F0FFFF, #9AF6FA, #2ED2E0, #108A9E).
Effect: A LIGHT SCALE SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the unit stands in the middle, not drawn: 16 squares wide and 36 tall; a SHIELD round the unit: only an OUTLINE of overlapping faceted golden scale plates (a tall egg shape round the unit, 2 squares thick), the inside EMPTY so the unit shows through, thin and pale (the lighter golden shades), one small cyan gem at its top; frames 1-6 a glint running up both sides together. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 22:38 cells, image size 2112x608 (each cell 352x608, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `idas_fx_p_burst.png`：护卫之誓：护盾亮起，5 帧

护卫之誓触发：一下金光闪亮，一片片金色鳞片从四周飞回来、合成一圈蛋形的护盾，最后亮一下。人在中间，**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a cyan gem ramp (#F0FFFF, #9AF6FA, #2ED2E0, #108A9E).
Effect: A GUARDIAN'S VOW FLASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the unit stands in the middle, not drawn: 16 squares wide and 36 tall; 1 a white-gold flash round the unit; 2-3 golden scale plates flying IN from all sides and locking together into a SHIELD round the unit: only an OUTLINE of overlapping faceted golden scale plates (a tall egg shape round the unit, 2 squares thick), the inside EMPTY so the unit shows through; 4 the shield complete and shining, a cyan gem flaring at its top; 5 the shine fading. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 5 equal 30:38 cells, image size 2400x608 (each cell 480x608, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `idas_fx_p_shield.png`：护卫之誓：护盾在身上，6 帧循环

护卫之誓的护盾：比小护盾更厚、更亮的一圈金鳞蛋形护盾轮廓，顶上一颗青色宝石，**里面是空的**。**左右对称**，6 帧循环（鳞片一片片轮流闪光）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a cyan gem ramp (#F0FFFF, #9AF6FA, #2ED2E0, #108A9E).
Effect: A GUARDIAN'S SCALE SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the unit stands in the middle, not drawn: 16 squares wide and 36 tall; a SHIELD round the unit: only an OUTLINE of overlapping faceted golden scale plates (a tall egg shape round the unit, 2 squares thick), the inside EMPTY so the unit shows through, bold and bright (the brightest golden shades), a cyan gem at its top; frames 1-6 the scales lighting up one pair at a time from the bottom to the top. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:40 cells, image size 2304x640 (each cell 384x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `idas_fx_r_wrap.png`：黄金龙鳞：裹翼时的金鳞外壳，6 帧循环

她用双翼裹住自己时：她身外罩着一个由大片金鳞拼成的半透明感的**穹顶外壳轮廓**（只有外圈，像金色的龙鳞铠甲把她包起来），外圈上的鳞片一片片闪光，脚下一圈金光。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a cyan gem ramp (#F0FFFF, #9AF6FA, #2ED2E0, #108A9E).
Effect: A GOLDEN SCALE SHELL, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the golden dragon stands in the middle, not drawn: 52 squares wide and 40 tall, her head at the upper right crouching (about 32 squares tall); a DOME of big overlapping faceted golden scale plates arching over her, only its OUTLINE (3 squares thick) from the ground on the left over her to the ground on the right, a short golden glow line on the ground under her, two small cyan gems on the dome; frames 1-6 a glint sweeping across the plates. The inside stays EMPTY. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 58:46 cells, image size 5568x736 (each cell 928x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `idas_fx_r_burst.png`：黄金龙鳞：外壳炸开，7 帧

她展开双翼的一下：金鳞外壳往外炸开，一大圈金光冲击波，几十片金鳞和金币往四周飞散，中间一道往上冲的金光。**身体位置留空**。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a cyan gem ramp (#F0FFFF, #9AF6FA, #2ED2E0, #108A9E).
Effect: THE SHELL BURSTS, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the golden dragon stands in the middle, not drawn: 52 squares wide and 40 tall, her head at the upper right; 1 the dome of golden scales (as in a crouching shell) cracking with white-gold light; 2 a white-gold flash, the plates blowing OUTWARD; 3-4 a wide golden shockwave ring (an ellipse 70 squares wide) with dozens of golden scales and a few gold coins flying out to both sides, a golden light beam rising above her; 5-7 the ring at the edge thinning, the scales falling and fading into gold sparks. Her body area stays EMPTY. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 7 equal 76:52 cells, image size 8512x832 (each cell 1216x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `idas_fx_r_heal.png`：黄金龙鳞：回血，6 帧

她回血：身边升起几道金绿色的光柱和一颗颗往上飘的小十字、小金鳞。**身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fresh green healing ramp (#F8FFE8, #D6F79A, #8EDC5E, #3E9E4A), a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08).
Effect: A GOLDEN HEAL, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the unit stands in the middle, not drawn: 16 squares wide and 36 tall; at both sides of the unit thin rising columns of green-gold light, small green plus signs and tiny golden scales floating up; 1 low at the feet, 2-4 rising past the shoulders, 5-6 fading above the head. The body area stays EMPTY. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 32:40 cells, image size 3072x640 (each cell 512x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `idas_fx_r_shield.png`：黄金龙鳞：队友的护盾 + 攻速，6 帧循环

队友身上大招的护盾：金鳞蛋形护盾轮廓，**里面是空的**，两侧各有两道往上冲的金色速度线（表示攻速提高），顶上一颗青色宝石。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden light ramp (#FFFFFF, #FFF6C8, #FFE07A, #FFC23A, #E8920E, #A85E08), a cyan gem ramp (#F0FFFF, #9AF6FA, #2ED2E0, #108A9E).
Effect: A GOLDEN SCALES SHIELD WITH HASTE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the unit stands in the middle, not drawn: 16 squares wide and 36 tall; a SHIELD round the unit: only an OUTLINE of overlapping faceted golden scale plates (a tall egg shape round the unit, 2 squares thick), the inside EMPTY so the unit shows through, bright, a cyan gem at its top, outside it on each side two short golden SPEED LINES streaking UPWARD; frames 1-6 the speed lines running up and starting again, a glint running round the shield. everything is a GOLDEN DRAGON's magic: molten GOLD and golden light, faceted golden DRAGON SCALES (small angular plates like her armour), a few glinting gold coins, touches of her CYAN gems; flat shades, crisp angular shapes; no fire, no red, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 26:40 cells, image size 2496x640 (each cell 416x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `idas_icon_skill.png`：技能 1「黄金龙息」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little cyan gem corners, a deep warm brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: at the left a golden dragon's open jaws (a cyan crest above them), a wide cone of molten golden breath pouring out to the right with a cracked shield shard in it. No text, no letters.
```

### 图标 2. `idas_icon_skill2.png`：技能 2「龙威振翅」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little cyan gem corners, a deep warm brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a pair of golden wings (rows of gold feather-blades) spread wide, a golden shockwave ring bursting out between them. No text, no letters.
```

### 图标 3. `idas_icon_ult.png`：大招「黄金龙鳞」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little cyan gem corners, a deep warm brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big shield made of overlapping faceted golden dragon scales with a cyan gem in its middle, golden light rays behind it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `idas_fx_a_hit` | view_effects `tft_idas_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `idas_fx_q_breath` | view_projectiles `tft_idas_q_breath`（大表，一道从她嘴边指向目标的线，随方向旋转；上下对称、朝右） | 56 × 22 |
| `idas_fx_q_shred` | view_buffs `tft_idas_q_shred`（跟随被喷到的人，身上，z 3；左右对称） | 18 × 26 |
| `idas_fx_e_roar` | view_effects `tft_idas_e_roar`（大表，在她身上，z 3；左右对称） | 64 × 44 |
| `idas_fx_e_slow` | view_buffs `tft_idas_e_slow`（跟随被减速的人，脚下地面，z -1；左右对称） | 20 × 10 |
| `idas_fx_e_shield` | view_buffs `tft_idas_e_shield`（跟随被套盾的队友，z 3；左右对称） | 22 × 38 |
| `idas_fx_p_burst` | view_effects `tft_idas_p_burst`（tft.dll 播，在她和被保护的队友身上，z 3；左右对称） | 30 × 38 |
| `idas_fx_p_shield` | view_buffs `tft_idas_p_shield`（tft.dll 挂，跟随她和被保护的队友，z 3；左右对称） | 24 × 40 |
| `idas_fx_r_wrap` | view_buffs `tft_idas_r_wrap`（跟随她，z 3；左右对称） | 58 × 46 |
| `idas_fx_r_burst` | view_effects `tft_idas_r_burst`（大表，在她身上，z 3；左右对称） | 76 × 52 |
| `idas_fx_r_heal` | view_effects `tft_idas_r_heal`（在她身上，z 3；左右对称） | 32 × 40 |
| `idas_fx_r_shield` | view_buffs `tft_idas_r_shield`（跟随被套盾的队友，护盾在时一直在，z 3；左右对称） | 26 × 40 |
| `idas_icon_skill` | skill_icons[0] `asset/tft/icons/tft_idas_skill` | 64 × 64 |
| `idas_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_idas_skill2` | 64 × 64 |
| `idas_icon_ult` | skill_icons[2] `asset/tft/icons/tft_idas_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_idas_fx`（小的）和 `tft_idas_big`（q_breath、e_roar、r_burst），tag = 名字。
- q_breath 断言上下对称（朝右），其余断言左右对称。
- p_burst、p_shield 由 tft.dll 播 / 挂（护卫之誓）；q_breath 是从她嘴边出发的一条只有画面的线（它的左端对着她的嘴）；e_roar、r_burst 是她身上的 CasterViewEffect；r_wrap 是她身上的 caster buff；r_shield 是 WithShield buff（护盾在时一直在）。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
