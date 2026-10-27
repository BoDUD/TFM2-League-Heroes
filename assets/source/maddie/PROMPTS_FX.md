# 麦迪：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/maddie_design.png`：把海克斯步枪扛在肩上的皮城女执法官，橙红短发、歪戴贝雷帽，金边宝蓝制服，步枪上一颗蓝水晶）。麦迪在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），38 格高、30 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/maddie_size.png`：麦迪缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里麦迪自己的特效贴图（**灰色的形状，游戏里再染色**：子弹、弹道尾迹、枪口火光、打中的闪光、硝烟），按用在我们哪张特效分好了行。只在本地用。
> - **麦迪是皮尔特沃夫的执法官神枪手，特效都是她的枪火**：步枪蓝水晶的**海克斯蓝**能量、白黄色的枪口火光、铜金色的火花、一点灰色硝烟，「通缉令」是红金色的执法官徽章和准星；不要光滑的霓虹光束，不要魔法符文，不要火球。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、火、烟没有黑描边**（徽章、金币这些实物可以有一圈深色描边）。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人（`r_sight` 的准星是细线，可以压在人身上）。
> - **对称**：打中、标记、身上和脚下的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道 `a_bullet`、`q_bullet`、`r_round` 朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。**枪口火光 `a_flash`、`r_flash` 朝右画、上下对称**（我把它们画进她自己的开枪帧里，跟着她一起翻转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `maddie_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入）；图标交付 `maddie_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/maddie_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/maddie_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「狙神」 | 离她越远的目标受到的伤害越高；被通缉的敌人死了她领一份赏金（攻速提高，最多 4 份） | `p_bounty` · `p_bounty_loop` |
| 普攻 | 步枪开一枪，后坐力把枪口顶起来 | `a_flash` · `a_bullet` · `a_hit` |
| 技能 1 =「连拨击锤」 | 半蹲朝最远的敌人连开 6 枪，每枪打中路上第一个敌人 | `a_flash` · `q_bullet` · `q_hit` |
| 技能 2 =「通缉令」 | 给附近血最多的敌方英雄打上通缉标记，所有人打它都更痛 | `e_mark` · `e_wanted` |
| 大招 =「执法狙杀」 | 瞄准 1 秒，一发穿透狙击弹射向血量比例最低的敌方英雄，路上的人都挨打 | `r_sight` · `r_flash` · `r_round` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 海克斯蓝：`#F2FFFF`、`#AEF2FF`、`#50CCF4`、`#1E7ACC`、`#0C3A7A`；
  - 金色（制服、火花、图标边框）：`#FFF2B8`、`#F2C858`、`#C8902C`、`#8A5A14`、`#4A2C08`；
  - 枪口火光：`#FFFFF4`、`#FFF2A0`、`#FFC444`、`#E8762A`、`#8A3812`；
  - 通缉红：`#FFE0D8`、`#FF7A60`、`#E0302C`、`#9A1420`、`#4A0A12`；
  - 硝烟灰：`#EEEEF0`、`#BCBCC6`、`#868694`、`#545462`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `maddie_fx_a_bullet.png`：普攻：飞出去的子弹，4 帧循环

她的步枪打出去的**海克斯子弹**：一颗发蓝白光的小弹头，后面拖一道细细的蓝色光尾。**朝右飞，上下对称**，4 帧循环（光尾一闪一闪）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08).
Effect: A FLYING HEXTECH BULLET, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a bright white-blue bullet head 3 squares long and 2 tall at the front (right), a thin hextech blue tracer tail 8 squares long behind it, tapering; frames 1-4 the tail flickering longer and shorter, one gold spark winking. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 4 equal 12:4 cells, image size 768x64 (each cell 192x64, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `maddie_fx_a_hit.png`：普攻：子弹打中，4 帧

子弹打在人身上：一下蓝白的闪光，几道蓝色的火花往四周溅开，一小团灰色硝烟。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a gun smoke grey ramp (#EEEEF0, #BCBCC6, #868694, #545462).
Effect: A BULLET IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue star flash 6 squares across; 2 short hextech blue sparks bursting out in an X and to both sides (mirrored), two gold sparks; 3 the sparks flying farther and thinning, a small grey smoke puff in the middle; 4 the smoke fading. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `maddie_fx_a_flash.png`：枪口火光（画进她的开枪帧），3 帧

她开枪那一下枪口喷出的火光：白黄色的一团，往右喷开成三叉的尖焰，带一点蓝色的海克斯电光。**朝右**，左边贴着枪口；**上下对称**。3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a muzzle-flash ramp (#FFFFF4, #FFF2A0, #FFC444, #E8762A, #8A3812), a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A).
Effect: A MUZZLE FLASH, 3 frames, pointing RIGHT (it comes out of a muzzle on the left edge of the cell, its middle on the cell's middle row), NOT symmetric left to right, SYMMETRIC TOP TO BOTTOM: 1 a white-yellow burst 6 squares across at the left edge with three pointed flame tongues shooting to the right (the middle one longest, 10 squares), a thin hextech blue spark inside; 2 the tongues shorter and orange, a little grey smoke; 3 a small smoke puff only. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 3 equal 14:10 cells, image size 672x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `maddie_fx_q_bullet.png`：连拨击锤：连发的子弹，4 帧循环

连拨击锤快速连开的子弹：比普攻更**热**的一颗**金黄色**弹头，后面一道金色和蓝色交错的光尾，速度感更强。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a muzzle-flash ramp (#FFFFF4, #FFF2A0, #FFC444, #E8762A, #8A3812), a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A).
Effect: A RAPID-FIRE ROUND, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a hot gold-white bullet head 3 squares long and 2 tall at the front (right), a gold tracer tail 10 squares long with a hextech blue core line, tapering; frames 1-4 the tail streaking and flickering. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 4 equal 14:4 cells, image size 896x64 (each cell 224x64, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `maddie_fx_q_hit.png`：连拨击锤：子弹打中，4 帧

连射的子弹打中：一下金色的闪光，铜色的弹片和金色火花往两边溅开，一点硝烟。比普攻的打中更狠一点。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a muzzle-flash ramp (#FFFFF4, #FFF2A0, #FFC444, #E8762A, #8A3812), a gun smoke grey ramp (#EEEEF0, #BCBCC6, #868694, #545462).
Effect: A HEAVY BULLET IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 8 squares across; 2 gold and brass sparks and tiny shrapnel bursting out to both sides (mirrored), a short orange ring 12 across; 3 the sparks farther, a grey smoke puff in the middle; 4 the smoke fading. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `maddie_fx_e_mark.png`：通缉令：打上通缉标记，6 帧

被通缉的人头顶上方「啪」地砸下来一枚**皮城执法官的金色徽章**（盾形，中间一颗蓝宝石），落下时撞出一圈红色的光环，然后变成一个红金色的**准星标记**悬在头顶。身体位置留空，标记在格子最上面 14 格里。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a wanted red ramp (#FFE0D8, #FF7A60, #E0302C, #9A1420, #4A0A12), a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A).
Effect: A WANTED MARK SLAMMING DOWN, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: everything over the unit's head, in the top 14 squares of the cell: 1 a gold Piltover ENFORCER BADGE (a shield shape 8 squares wide and 9 tall with a blue gem in its middle) appearing high up; 2 it drops down; 3 it lands just above the head with a red ring of light 16 squares wide and 4 tall bursting out flat from it; 4 the badge flashes white, red sparks to both sides (mirrored); 5 it shrinks into a red-and-gold CROSSHAIR RETICLE (a circle 7 squares across with four ticks); 6 the reticle settling. The middle (the body) left empty. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 6 equal 22:48 cells, image size 2112x768 (each cell 352x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `maddie_fx_e_wanted.png`：通缉令：通缉中（受伤加深），6 帧循环

通缉中的人：头顶一个**红金色的准星**慢慢转、一明一暗，脚下一圈淡淡的红色光圈。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wanted red ramp (#FFE0D8, #FF7A60, #E0302C, #9A1420, #4A0A12), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08).
Effect: A WANTED TARGET, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 10 squares of the cell) a red-and-gold CROSSHAIR RETICLE 7 squares across (a circle with four short ticks, a gold dot in the middle), and a faint red ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 squares wide and 4 tall at the bottom; frames 1-6 the reticle pulsing brighter and dimmer, its ticks flicking in and out in turn (mirrored), the ring breathing. The middle (the body) left empty. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 6 equal 16:46 cells, image size 1536x736 (each cell 256x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `maddie_fx_p_bounty.png`：赏金：通缉的人死了，她领赏，6 帧

被通缉的敌人死了、麦迪领到一份赏金：她身边「叮」地蹦出几枚**金币**往上飞，一圈蓝色的海克斯光从脚下往上扫（攻速提高）。身体位置留空。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A).
Effect: A BOUNTY COLLECTED, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a gold flash at her chest; 2 four small GOLD COINS (2x2 squares, a bright glint) popping out to both sides of the body (mirrored); 3 the coins arcing up past her shoulders, a hextech blue ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 18 squares wide rising from her feet; 4 the blue ring at her waist, the coins at the top spinning; 5 the ring at her head thinning, the coins twinkling; 6 the last sparkles. The middle (the body) left empty. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 6 equal 24:46 cells, image size 2304x736 (each cell 384x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `maddie_fx_p_bounty_loop.png`：赏金：领过赏金（攻速加成），6 帧循环

领过赏金的麦迪：脚下一圈淡淡的**金色光圈**，几颗小金星一闪一闪（不要太显眼，她会一直带着）。只画脚下这一截。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08).
Effect: A BOUNTY GLOW, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a faint thin gold ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 20 squares wide and 6 tall round the unit's feet, three tiny gold star glints on it at mirrored places; frames 1-6 the glints winking in turn and a soft brighter arc running round the ring. Subtle: thin lines, few squares. The upper part of the cell empty. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 6 equal 22:10 cells, image size 2112x160 (each cell 352x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `maddie_fx_r_sight.png`：执法狙杀：瞄准（准星锁定），8 帧

麦迪瞄准的那一秒：目标身上出现一个**很大的红色狙击准星**（一个圆、十字线、四个刻度），从大慢慢缩小、锁定在目标身上，最后两帧一闪一闪。准星的中心在格子中间往下一点（人的胸口）。准星是细线，**可以盖在人身上**。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wanted red ramp (#FFE0D8, #FF7A60, #E0302C, #9A1420, #4A0A12), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08).
Effect: A SNIPER'S LOCK-ON, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a big red SNIPER SCOPE RETICLE centred on the middle of the cell, 4 squares below the centre (the unit's chest): a thin circle, a thin cross of lines with a gap in the middle, four short gold ticks on the circle; 1 the circle 34 squares across, faint; 2-5 it shrinks steadily (28, 22, 16, 12 across) and grows brighter, the cross lines shortening with it; 6 locked at 10 across, a small gold diamond in the centre; 7 a bright white-red flash of the whole reticle; 8 it dims a step. Thin 1-square lines only, so the unit under it stays readable. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 8 equal 36:48 cells, image size 4608x768 (each cell 576x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `maddie_fx_r_flash.png`：执法狙杀：大口径枪口火光（画进她的狙击帧），5 帧

狙击那一枪的**巨大枪口火光**：白黄色的一大团，往右喷出长长的尖焰，外面一圈蓝色的海克斯冲击波环，后面拖一大团硝烟。**朝右**，左边贴着枪口；**上下对称**。5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a muzzle-flash ramp (#FFFFF4, #FFF2A0, #FFC444, #E8762A, #8A3812), a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A), a gun smoke grey ramp (#EEEEF0, #BCBCC6, #868694, #545462).
Effect: A HEAVY MUZZLE BLAST, 5 frames, pointing RIGHT (it comes out of a muzzle on the left edge of the cell, its middle on the cell's middle row), NOT symmetric left to right, SYMMETRIC TOP TO BOTTOM: 1 a big white-yellow burst 10 squares across at the left edge, a long pointed flame tongue shooting 26 squares to the right with two shorter ones at angles; 2 a hextech blue shockwave ring (an upright ellipse 6 wide and 16 tall) pushed out to the right of the burst, the flame orange; 3 the ring farther right and thinner, grey smoke billowing at the muzzle; 4 smoke 12 across drifting; 5 thin smoke. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 5 equal 30:20 cells, image size 2400x320 (each cell 480x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `maddie_fx_r_round.png`：执法狙杀：飞出去的狙击弹，4 帧循环

狙击打出去的**穿甲海克斯弹**：一颗大的蓝白色尖头弹，后面一道很长、很亮的蓝色能量尾迹，尾迹两边有一圈圈的螺旋。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08).
Effect: A PIERCING HEXTECH ROUND, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a big pointed white-blue round 6 squares long and 4 tall at the front (right) with a gold ring at its base, a long bright hextech blue energy trail 26 squares long behind it with small spiral rings around it, tapering to the left; frames 1-4 the spiral rings sliding back along the trail. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 4 equal 34:8 cells, image size 2176x128 (each cell 544x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `maddie_fx_r_hit.png`：执法狙杀：狙击命中，7 帧

狙击弹打中（它会穿过去继续飞）：一下巨大的蓝白闪光，一道**横向的冲击线**往两边炸开，蓝色和金色的碎光四溅，一圈冲击环，留下一点硝烟。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a gun smoke grey ramp (#EEEEF0, #BCBCC6, #868694, #545462).
Effect: A SNIPER ROUND PUNCHING THROUGH, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-blue star flash 14 squares across in the middle; 2 a thin bright horizontal shock line 36 squares long through the middle, hextech blue and gold sparks bursting out to both sides (mirrored); 3 a hextech blue shock ring 30 wide and 12 tall around the middle, sparks farther; 4 the ring bigger and thinner, the shock line breaking up; 5-6 grey smoke puffs in the middle, the last sparks; 7 thin smoke. everything is a PILTOVER ENFORCER SHARPSHOOTER's gunfire: crisp HEXTECH blue energy from her rifle's crystal, hot white-yellow muzzle flashes, brass-gold sparks, a little grey gun smoke, a red-and-gold WANTED mark; flat shades, crisp shapes; no smooth neon beams, no magic runes, no fire balls.
Layout: one horizontal row of 7 equal square cells, image size 4480x640 (each cell 640x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `maddie_icon_skill.png`：技能 1「连拨击锤」图标

一只握枪的手快速扳动击锤，枪口喷出一串扇形排开的六颗金色子弹。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a gloved hand fanning the hammer of a dark navy-and-gold hextech gun, the muzzle at the upper right spitting SIX gold bullets in a fan, each with a short tracer, a white-yellow flash at the muzzle. Colours: a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a muzzle-flash ramp (#FFFFF4, #FFF2A0, #FFC444, #E8762A, #8A3812). No text, no letters.
```

### 图标 2. `maddie_icon_skill2.png`：技能 2「通缉令」图标

一枚金色的皮城执法官徽章（中间蓝宝石），外面套着一个红色的准星。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a gold Piltover ENFORCER BADGE (a shield shape with a glowing blue gem in its middle) inside a red CROSSHAIR RETICLE (a circle with four ticks), a few red sparks. Colours: a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08), a wanted red ramp (#FFE0D8, #FF7A60, #E0302C, #9A1420, #4A0A12), a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A). No text, no letters.
```

### 图标 3. `maddie_icon_ult.png`：大招「执法狙杀」图标

瞄准镜里的视野：一个红色的十字准星，中间一颗拖着蓝色长尾迹的狙击弹正冲出来。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: the round view of a SNIPER SCOPE with a thin red cross and gold ticks, a big hextech blue ROUND with a long glowing trail bursting out of its centre toward the viewer, a white flash. Colours: a wanted red ramp (#FFE0D8, #FF7A60, #E0302C, #9A1420, #4A0A12), a hextech blue ramp (#F2FFFF, #AEF2FF, #50CCF4, #1E7ACC, #0C3A7A), a gold ramp (#FFF2B8, #F2C858, #C8902C, #8A5A14, #4A2C08). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `maddie_fx_a_bullet` | view_projectiles `tft_maddie_a_bullet`（弹道，z 2；朝右、上下对称） | 12 × 4 |
| `maddie_fx_a_hit` | view_effects `tft_maddie_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `maddie_fx_a_flash` | 画进她的动作帧（a_fire、q_fire：枪口那一点）；不做单独的画面 | 14 × 10 |
| `maddie_fx_q_bullet` | view_projectiles `tft_maddie_q_bullet`（弹道，z 2；朝右、上下对称） | 14 × 4 |
| `maddie_fx_q_hit` | view_effects `tft_maddie_q_hit`（跟随被打中的人，z 2；左右对称） | 16 × 16 |
| `maddie_fx_e_mark` | view_effects `tft_maddie_e_mark`（跟随被通缉的人，z 4；左右对称） | 22 × 48 |
| `maddie_fx_e_wanted` | view_buffs `tft_maddie_e_wanted`（跟随被通缉的人，z 4；左右对称） | 16 × 46 |
| `maddie_fx_p_bounty` | view_effects `tft_maddie_p_bounty`（跟随她，z 4；左右对称） | 24 × 46 |
| `maddie_fx_p_bounty_loop` | view_buffs `tft_maddie_p_bounty`（tag p_bounty_loop，跟随她，z 3；左右对称） | 22 × 10 |
| `maddie_fx_r_sight` | view_effects `tft_maddie_r_sight`（大表，跟随大招的目标，z 4；左右对称） | 36 × 48 |
| `maddie_fx_r_flash` | 画进她的动作帧（r_fire：枪口那一点）；不做单独的画面 | 30 × 20 |
| `maddie_fx_r_round` | view_projectiles `tft_maddie_r_round`（大表，弹道，z 2；朝右、上下对称） | 34 × 8 |
| `maddie_fx_r_hit` | view_effects `tft_maddie_r_hit`（大表，跟随被打中的人，z 3；左右对称） | 40 × 40 |
| `maddie_icon_skill` | skill_icons[0] `asset/tft/icons/tft_maddie_skill` | 64 × 64 |
| `maddie_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_maddie_skill2` | 64 × 64 |
| `maddie_icon_ult` | skill_icons[2] `asset/tft/icons/tft_maddie_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_maddie_fx`（小的）和 `tft_maddie_big`（r_sight、r_round、r_hit），tag = 名字；p_bounty_loop 是 view_buffs 里 p_bounty 的 tag；a_flash / r_flash 不进表，画进 a_fire、q_fire、r_fire 那几帧的枪口。
- 弹道（a_bullet、q_bullet、r_round）和枪口火光（a_flash、r_flash）断言上下对称；其余断言左右对称。
- r_sight 在大招瞄准的 r_rel 拍里放完（8 帧拉到那么长）；q_hit / r_hit / p_bounty 由 tft.dll 在打中、领赏时播。
- 用 `pixel_1x/` 切格（import_silco_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
