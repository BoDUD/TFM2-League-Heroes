# 泰拉：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/terra_design.png`：3/4 朝右、四条腿趴伏的大地巨龙：灰绿色的大块岩石甲板（几片苔藓绿）、黄色发光的眼睛、两排米白石牙；米白石骨 + 橙色翼膜的翅膀收在背上；红褐色的肚子、四条粗腿和深色大爪；细长的尾巴末端一簇灰绿石刺）。泰拉在游戏里是**高清**的（每个游戏格子里约 1.45×1.45 个细像素），36 格高、60 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/terra_size.png`：泰拉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里泰拉自己的特效贴图（地震的陨坑和发光裂纹、碎石、声浪、护盾光）和熔岩巨兽的碎石（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **泰拉是大地巨龙，特效都是大地的力量**：灰绿色的石块和石板、裂开的地面里**发光的金橙色裂纹**（最亮处奶黄色）、褐色的尘土、一点点苔藓绿；不要火焰、不要蓝色紫色、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶黄色的芯，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**（石块可以有深色描边）。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `terra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `terra_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/terra_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/terra_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「岩爪」 | 前爪一拍、张嘴一咬 | `a_hit` |
| 被动「巨岩之躯」 | 受到的伤害永久减少 18%（不用画） | — |
| 技能 1 =「裂地咬」 | 低头扑上去猛咬一口，伤害吃护甲魔抗，被咬的减速 | `q_hit` · `q_slow` |
| 技能 2 =「龙威咆哮」 | 仰头咆哮，身边的敌人被嘲讽过来打她，自己套一层岩石护盾 | `e` · `e_taunt` · `e_shield` |
| 大招 =「地震」 | 抬身重踏三次，每一踏一圈地震；结束后岩甲发光，护甲魔抗大涨 8 秒 | `r` · `r_quake` · `r_hit` · `r_res` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（石块、石板可以用石头最深一档描边）。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 石头（她的岩甲）：`#ECEAD6`、`#BDBC9C`、`#8C8E70`、`#5E6249`、`#3A3D2E`；
  - 金橙（发光的裂纹）：`#FFF7CC`、`#FFD75C`、`#F59B20`、`#C2580F`、`#6E2C08`；
  - 土和尘：`#E6D9BE`、`#BBA680`、`#8B7452`、`#5B4732`；
  - 苔藓：`#A9C474`、`#73923F`、`#48622B`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `terra_fx_a_hit.png`：普攻「岩爪」：石爪打中，4 帧

岩爪打中：一下金橙色的闪光，两组交叉成 X 的石色爪痕，几块灰绿碎石往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E), an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08).
Effect: A ROCK CLAW HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a cream-yellow flash 4 squares across; 2 two sets of three thick stone-grey claw marks crossing in an X, 14 squares across, gold-orange along their middles; 3 the marks breaking into small grey-green stone chips flying out to both sides (mirrored); 4 a few falling chips and a puff of brown dust. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `terra_fx_q_hit.png`：技能 1「裂地咬」：石牙咬下，5 帧

咬中：上下两排**米白色的石牙虚影**从上下合拢咬在一起，咬合的一下金橙色光爆开，地面一样的裂纹从咬合处往外裂开，几块碎石崩出去。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E), an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08).
Effect: A STONE BITE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two glowing jaw outlines open wide, an upper row of 5 cream stone fangs pointing down at the top and a lower row of 5 pointing up at the bottom, 20 squares wide; 2 the jaws snapping half shut; 3 the fangs meeting in the middle with a bright gold-orange burst 12 squares across, thin glowing cracks shooting out from it; 4 grey-green stone chips flying out to both sides (mirrored), the fangs fading; 5 a few fading chips and dust. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `terra_fx_q_slow.png`：技能 1「裂地咬」：减速，6 帧循环

被减速：脚下地面裂开（从斜上方看的椭圆，宽是高的 3 倍），几道金橙色的细裂纹在发光，几块小碎石缠在脚边一起一落。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#E6D9BE, #BBA680, #8B7452, #5B4732), an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E).
Effect: A CRACKED-GROUND SNARE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND round the unit's feet, an ellipse seen from above, about 18 squares wide and 6 tall, of cracked brown earth; a few thin gold-orange glowing cracks in it pulsing brighter and dimmer; two or three small grey-green stone chips at its edge rising a square or two and dropping back (keep every frame left-right symmetric). Nothing above the feet. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:8 cells, image size 1920x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `terra_fx_e.png`：技能 2「龙威咆哮」：咆哮冲击波，6 帧

她仰头咆哮的一下：从她身上往外**一圈圈扩散的金橙色声浪环**（从斜上方看的椭圆，一圈比一圈大），地面上一圈尘土被吹开，两侧几块碎石被震飞。**身体位置留空**（只画外面的环、脚下和两侧）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), an earth-dust ramp (#E6D9BE, #BBA680, #8B7452, #5B4732), a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E).
Effect: A ROAR SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon stands in the middle, not drawn: 60 squares wide and 36 tall, crouched on all fours, her head at the right: 1 a gold flash ring on the ground under her (an ellipse 48 squares wide, 12 tall); 2-4 three concentric gold-orange SOUND-WAVE RINGS (ellipses, each 2 squares thick, cream-yellow on their front edge, deep orange behind) bursting outward from her one after another, the outer one reaching the cell edge; brown dust blown out low to both sides, a few stone chips tossed up; 5 the rings thinning; 6 the last ring fading. The middle of the cell (her body) stays EMPTY. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 72:48 cells, image size 6912x768 (each cell 1152x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `terra_fx_e_taunt.png`：技能 2「龙威咆哮」：被嘲讽，6 帧循环

被嘲讽的人头顶上：一个**金橙色发光的龙爪印 / 裂纹印记**（三道爪痕组成，像被巨龙盯上），一闪一闪地脉动。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E).
Effect: A TAUNT MARK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head, in the cell's upper part: a small glowing gold-orange mark of three claw slashes side by side (the middle one longest), 10 squares wide, inside a thin stone-grey cracked frame; frames 1-6 it pulses brighter and dimmer, a cream-yellow core on the brightest frames (every frame left-right symmetric). everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 14:10 cells, image size 1344x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `terra_fx_e_shield.png`：技能 2「龙威咆哮」：岩石护盾，6 帧循环

她的岩石护盾：身体**两侧**各浮着三四块灰绿色的岩石板（边缘金橙色描一圈光），上下缓缓浮动，地上一圈淡淡的金光。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E), an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), a moss ramp (#A9C474, #73923F, #48622B).
Effect: A FLOATING ROCK-SLAB SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon stands in the middle, not drawn: 60 squares wide and 36 tall, crouched on all fours, her head at the right: three or four grey-green stone slabs floating on EACH side of her (mirrored), each 6-9 squares tall with a 1-square gold-orange glowing rim and a fleck of moss, slowly bobbing up and down; a faint gold ring on the ground under her (an ellipse 48 squares wide, 12 tall); frames 1-6 the slabs bobbing (every frame left-right symmetric). The middle of the cell (her body) stays EMPTY. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 72:48 cells, image size 6912x768 (each cell 1152x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `terra_fx_r.png`：大招「地震」：抬身时脚下裂开，4 帧

她抬起前身的一下：脚下地面**金橙色的裂纹一下亮起来**往两边蔓延，几缕尘土从裂缝里冒出来。**只在地面上**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), an earth-dust ramp (#E6D9BE, #BBA680, #8B7452, #5B4732).
Effect: THE GROUND WAKING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND only (the bottom of the cell), an ellipse about 54 squares wide and 12 tall under her: 1 a gold glint at the middle; 2 thin gold-orange glowing cracks running out to both sides (mirrored); 3 the cracks branching, cream-yellow at their joins, small brown dust puffs rising from them; 4 the glow dimming. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 4 equal 56:14 cells, image size 3584x224 (each cell 896x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `terra_fx_r_quake.png`：大招「地震」：一圈地震，7 帧

每一踏掀起的一圈地震：以她为中心，**地面裂成一圈陨坑**（从斜上方看的大椭圆，宽是高的 3 倍），金橙色的裂纹从中间往外放射，椭圆外沿一圈**石块和土墙往上掀起**，碎石飞起、尘土翻滚，再落下去。**中间她站的地方留空**。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E), an earth-dust ramp (#E6D9BE, #BBA680, #8B7452, #5B4732).
Effect: AN EARTHQUAKE RING, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon stands in the middle, not drawn: 60 squares wide and 36 tall, crouched on all fours, her head at the right, on and just above the GROUND: 1 glowing gold-orange cracks shooting out from under her across an ellipse 104 squares wide and 34 tall, like a cracked crater seen from above; 2 the cracks reaching the ellipse's edge, a ring of broken earth lifting there; 3 along the WHOLE outer edge of the ellipse a low wall of grey-green rock slabs and brown earth heaving up (up to 10 squares high at the back and the sides, lower at the front), cream-yellow glow in the cracks; 4 stone chips flying up out of the ring (mirrored), brown dust rolling outward; 5 the slabs falling back, the dust spreading; 6 the cracks dimming, dust settling; 7 faint cracks only. The middle of the cell where she stands stays EMPTY (only cracks on the ground under her). everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 7 equal 112:48 cells, image size 12544x768 (each cell 1792x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `terra_fx_r_hit.png`：大招「地震」：被震到，5 帧

被地震打中：脚下一下金光，一圈尖尖的石刺从地下往上戳出来又碎掉，尘土往两边扬。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E), an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), an earth-dust ramp (#E6D9BE, #BBA680, #8B7452, #5B4732).
Effect: A ROCK SPIKE ERUPTION, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a unit standing in the middle (not drawn): 1 a gold-orange crack flash on the ground under it; 2 a ring of five sharp grey-green stone spikes jabbing up from the ground round it (mirrored, the middle one tallest, up to 16 squares), cream-yellow light at their bases; 3 the spikes cracking; 4 the spikes shattering into falling chips, brown dust puffing out to both sides; 5 dust settling. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `terra_fx_r_res.png`：大招「地震」之后：岩甲发光，6 帧循环

地震之后她的岩甲：身体**两侧**和背上方飘起一点点金橙色的光尘往上升，脚下一圈金色的符文裂纹环慢慢亮暗（和护盾不一样：没有浮着的石板）。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember-gold ramp (#FFF7CC, #FFD75C, #F59B20, #C2580F, #6E2C08), a stone ramp (#ECEAD6, #BDBC9C, #8C8E70, #5E6249, #3A3D2E).
Effect: A STONE ARMOUR GLOW, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon stands in the middle, not drawn: 60 squares wide and 36 tall, crouched on all fours, her head at the right: small gold-orange light motes and tiny stone flecks rising slowly along BOTH sides of her and above her back (mirrored), cream-yellow on the brightest; a ring of glowing gold crack runes on the ground under her (an ellipse 52 squares wide, 13 tall) pulsing; frames 1-6 the motes drifting up and the ring breathing (every frame left-right symmetric; no floating slabs). The middle of the cell (her body) stays EMPTY. everything is an EARTH DRAGON's power: chunky grey-green stone shards and slabs, cracked earth with GLOWING GOLD-ORANGE CRACKS, cream-yellow cores in the brightest light, brown dust puffs, a few moss-green flecks; flat shades, crisp blocky shapes; no fire flames, no blue, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 72:48 cells, image size 6912x768 (each cell 1152x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `terra_icon_skill.png`：技能 1「裂地咬」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-stone frame with little gold corners, a deep brown-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a rock dragon's grey-green stone head from the side, jaws with cream stone fangs snapping shut low over cracked ground, gold-orange glowing cracks and flying stone chips under the bite. No text, no letters.
```

### 图标 2. `terra_icon_skill2.png`：技能 2「龙威咆哮」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-stone frame with little gold corners, a deep brown-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a rock dragon's head roaring upward with its jaws wide open, glowing yellow eye, three gold-orange sound-wave arcs coming out of its mouth, a grey-green rock slab shield behind it. No text, no letters.
```

### 图标 3. `terra_icon_ult.png`：大招「地震」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-stone frame with little gold corners, a deep brown-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge clawed dark-brown dragon foot stomping down onto the ground, the ground split by glowing gold-orange cracks in a ring, grey-green rock slabs heaving up around it, dust. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `terra_fx_a_hit` | view_effects `tft_terra_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `terra_fx_q_hit` | view_effects `tft_terra_q_hit`（跟随目标，z 3；左右对称） | 22 × 22 |
| `terra_fx_q_slow` | view_buffs `tft_terra_q_slow`（跟随被减速的人，脚下地面，z 3；左右对称） | 20 × 8 |
| `terra_fx_e` | view_effects `tft_terra_e`（大表，跟随她，z 4；左右对称） | 72 × 48 |
| `terra_fx_e_taunt` | view_buffs `tft_terra_e_taunt`（跟随被嘲讽的人，头顶上方，z 3；左右对称） | 14 × 10 |
| `terra_fx_e_shield` | view_buffs `tft_terra_e_shield`（大表，跟随她，z 3；左右对称） | 72 × 48 |
| `terra_fx_r` | view_effects `tft_terra_r`（跟随她，脚下地面，z 3；左右对称） | 56 × 14 |
| `terra_fx_r_quake` | view_effects `tft_terra_r_quake`（大表，每一踏放在她脚下的地面上，不跟随，z -1；左右对称） | 112 × 48 |
| `terra_fx_r_hit` | view_effects `tft_terra_r_hit`（跟随被打中的人，z 3；左右对称） | 20 × 20 |
| `terra_fx_r_res` | view_buffs `tft_terra_r_res`（大表，跟随她，z 3；左右对称） | 72 × 48 |
| `terra_icon_skill` | skill_icons[0] `asset/tft/icons/tft_terra_skill` | 64 × 64 |
| `terra_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_terra_skill2` | 64 × 64 |
| `terra_icon_ult` | skill_icons[2] `asset/tft/icons/tft_terra_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_terra_fx`（小的）和 `tft_terra_big`（e、e_shield、r_quake、r_res），tag = 名字。
- 全部断言左右对称。
- e 是她身上的一下（跟随她，z 4）；r 是她脚下地面的一下（跟随她，z 3）；r_quake 每一踏放在她脚下的地面上（不跟随，z -1）；e_shield、r_res 是她身上的 caster buff（z 3）；q_slow 是敌人脚下的 buff，e_taunt 是敌人头上的 buff（z 3）；a_hit、q_hit、r_hit 打在目标身上。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
