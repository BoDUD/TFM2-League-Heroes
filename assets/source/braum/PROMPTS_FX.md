# 弗雷尔卓德之心 布隆：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型和动作已定（`design/braum_idle.png`：游戏里的 3/4 正面待机，盾立在他身前画面右边）。他在游戏里是**高清**的（PPU：每个游戏格子里 2.88×2.88 个细像素，这张图是高清造型放大 3 倍），连盾 43 格高、48 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/braum_size.png`：待机放大 4 倍，鞋底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/braum_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里布隆自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**冰蓝色的光（白芯）、淡淡的霜雾和雪**；E 和 W 的加成里可以有几点**盾上金边的金色反光**。
> - **特效要亮**：每道光、每块冰都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的冰壳、冲击环只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。
> - **方向（重要，红色方不会镜像）**：飞出去的冰 `q_ice` 和沿直线冲出去的冰刺 `r_wave` 画成朝右，**上下对称**（往左放时会上下翻）。其余所有画面（打中、身上、脚下、头顶、地上的裂隙、砸地）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `braum_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `braum_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「震荡猛击」 | 盾击；普攻和 Q 给英雄叠层，第 4 层眩晕，之后几秒普攻追加伤害 | `a_hit` · `p_mark` · `p_stun` · `p_proc` · `p_extra` |
| 技能 1 = Q「寒冬之咬」 | 从盾里甩出寒冰，打中的人减速 | `q_ice` · `q_hit` · `q_slow` |
| 技能 2 = E「坚不可摧」+ W「挺身而出」 | 举盾减伤，盾后的队友也减伤；跳到队友身边，两人加护甲魔抗 | `e_raise` · `e_on` · `e_ally` · `w_dash` · `w_land` · `w_guard` |
| 大招 = R「冰川裂隙」 | 盾砸地，冰沿直线冲出去击飞敌人，留下减速的裂隙 | `r_slam` · `r_wave` · `r_crack` · `r_hit` · `q_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冰、霜、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 冰蓝光：`#FFFFFF`、`#DFF8FF`、`#9EE6FF`、`#4FC3F7`、`#1E88E5`、`#0D47A1`；
  - 霜雾和雪：`#FFFFFF`、`#EEF7FF`、`#CFE6F5`、`#A5C8E1`、`#7FA6C6`；
  - 金色反光（只用于 E、W 的小亮点）：`#FFF6C8`、`#FFE07A`、`#F2B83C`、`#B98322`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，R 的直线长 80000、半宽 9000，裂隙每段减速半径 10000、沿线每 20000 一段，E 盾后队友范围 25000）。

### 1. `braum_fx_a_hit.png`：普攻打中（目标身上），4 帧

盾击打中：目标身上一圈白蓝色的冲击光环一闪（参考 BA_Ring、BA_Flash），外面几根短短的冰刺往外弹（参考 BA_spikes）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: a FROSTY SHIELD-BASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a thin ice-blue ring 10 squares across with a white rim and a white core; 3 the ring 12 squares across, 4 short ice spikes pointing outward at mirrored places; 4 a few fading frost sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `braum_fx_p_mark.png`：被动 震荡猛击：层数标记（被叠层的英雄头顶，循环），4 帧

被布隆打中的英雄头顶出现一个小小的冰蓝色拳头印记（一个圆形的冰徽，中间一个白色的拳头形状，参考 P_Cooldowntimer、P_ice_shards），一闪一闪。每多一层就多叠一个同样的标记（游戏里同一位置重叠），所以**每帧都画一个**。**左右对称**。画在格子上部（人头上方）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: a FROST FIST MARK over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a round ice-blue badge 8 squares across with a white fist shape in it, pulsing brighter and dimmer, two 1-square white sparkles at its sides.
Layout: one horizontal row of 4 equal 12:48 cells, image size 768x768 (each cell 192x768, 16 px a square); the badge's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `braum_fx_p_stun.png`：被动 第 4 层：眩晕（被眩晕的人头顶，循环），4 帧

第 4 层眩晕：头顶一圈转着的小冰晶（三四颗白蓝色的小雪花沿一个扁椭圆转圈），一闪一闪。**左右对称**（每帧逐格对称：转圈靠亮暗交替表现，不要画成不对称）。画在格子上部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: STUN SNOWFLAKES over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 4 small white-blue snowflakes 3 squares across placed on a flat ellipse 14 squares wide and 5 tall at mirrored places, the near ones brighter, the pairs taking turns to flash white.
Layout: one horizontal row of 4 equal 16:48 cells, image size 1024x768 (each cell 256x768, 16 px a square); the ellipse's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `braum_fx_p_proc.png`：被动 第 4 层：眩晕炸开（目标身上），5 帧

叠满 4 层的一下：目标身上冻住一下又炸开——一团冰晶包住他（大块冰蓝色冰片拼成的菱形外壳），然后碎成冰片往外飞（参考 P_Flash、P_ice_shards）。**左右对称**，中间人形位置在第 2 帧以后留空。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: an ICE SHELL SHATTERING round a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its middle EMPTY from frame 2 (a clear upright area 12 squares wide and 24 tall): 1 a white star flash 8 squares across; 2 sharp ice-blue crystal plates with white edges round the empty middle, 20 squares wide and 30 tall; 3 the plates cracking (white lines); 4 the plates flying outward as shards at mirrored places; 5 small fading shards and frost.
Layout: one horizontal row of 5 equal 22:32 cells, image size 1760x512 (each cell 352x512, 16 px a square); centered across, the shell's bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `braum_fx_p_extra.png`：被动：眩晕后的追加伤害（目标身上），3 帧

眩晕后几秒内布隆普攻的追加魔法伤害：目标身上一个小小的冰蓝色十字星光一闪。**左右对称**。约 8 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1).
Effect: a SMALL ICE STAR, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a four-point ice-blue star 8 squares across with a white core; 3 the star fading to a few sparkles.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `braum_fx_q_ice.png`：Q 寒冬之咬：飞出去的冰（朝目标飞，循环），4 帧

从盾里甩出去的一大块冰：前面一颗尖尖的白蓝色冰晶（像一颗冰牙），后面拖一条冰雾尾巴和几粒冰屑（参考 Q_frost_tail、Q_End_spark）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: an ICE CHUNK flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a pointed ice crystal 7 squares long and 5 tall (white core, ice-blue facets, pointing right); a frost tail 6 squares long behind it to the left, tapering, with 2-3 small ice flakes (mirrored top to bottom) flickering in turn.
Layout: one horizontal row of 4 equal 16:12 cells, image size 1024x192 (each cell 256x192, 16 px a square); the crystal's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `braum_fx_q_hit.png`：Q 打中（目标身上），5 帧

冰打中目标：一圈冰蓝色的霜雾炸开（白芯），几块冰片往外溅（参考 Q_hit_tar_slow）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: an ICE BURST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 an ice-blue frost puff 10 squares across with a white core; 3 the puff 16 squares across, 4 ice shards flying out at mirrored places; 4 the shards farther, the frost thinning; 5 a few fading flakes.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `braum_fx_q_slow.png`：Q / R 减速（被减速的人脚下，循环），4 帧

脚下一圈结冰的地面（从斜上方看的扁椭圆），冰面上几根小冰刺冒出来又缩回去，冒一点白色冷气。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: FROZEN GROUND under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse 16 squares wide and 5 tall - pale ice with an ice-blue rim - and 2-4 small ice spikes at mirrored places rising one square and sinking in turn, a wisp of white frost.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `braum_fx_e_raise.png`：E 坚不可摧：举盾的一刻（他身上），5 帧

举盾那一下：他周围一圈冰蓝色的寒气猛地一冲（像一阵冰风往外扩的大椭圆边），边上几块冰片和几点金色火花（盾上的金边反光，参考 E_shield_inchant、E_ice）。**中间人形位置留空**（不要盖住他）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1), a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6) and a gold ramp used only for small glints (#FFF6C8, #FFE07A, #F2B83C, #B98322).
Effect: a BURST OF COLD round a broad figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 30 squares wide and 38 tall in the middle): 1 a faint ice-blue rim at the figure's sides; 2 the rim of a wide ellipse 36 squares wide and 42 tall, 2 squares thick, white inner edge; 3 ice flakes and 3-4 small gold glints flying off the rim at mirrored places; 4 the rim breaking into flakes; 5 fading frost.
Layout: one horizontal row of 5 equal 38:46 cells, image size 3040x736 (each cell 608x736, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `braum_fx_e_on.png`：E 举盾期间（他身上，循环），4 帧

举盾的几秒里：他周围一层淡淡的冰蓝色冰壳（只画外轮廓的一圈弧线和几块六边形的冰片亮光），冰片轮流闪光。**中间人形位置留空**。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: an ICE SHELL round a broad figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 30 squares wide and 38 tall): only the rim of a wide ellipse 36 squares wide and 42 tall - a thin ice-blue arc 1-2 squares thick with a white inner edge - and 4-6 small hexagonal ice glints on it at mirrored places, twinkling in turn.
Layout: one horizontal row of 4 equal 38:46 cells, image size 2432x736 (each cell 608x736, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `braum_fx_e_ally.png`：E 盾后的队友（队友头顶，循环），4 帧

躲在布隆盾后面的队友受到的伤害降低：头顶一个小小的冰蓝色盾牌徽记（门板一样的方盾轮廓，中间一点白光），一闪一闪。**左右对称**。画在格子上部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: a SMALL SHIELD SIGIL over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ice-blue square shield outline 8 squares wide and 9 tall with a white core in its middle, pulsing brighter and dimmer.
Layout: one horizontal row of 4 equal 12:48 cells, image size 768x768 (each cell 192x768, 16 px a square); the sigil's middle 6 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `braum_fx_w_dash.png`：W 挺身而出：跳向队友（他身上，跟着他），4 帧

跳起来的一瞬间：他脚下一圈被踩碎的冰雪往两边飞溅（扁椭圆的雪雾，几块冰屑往上弹）。**左右对称**（不要画成往一个方向拖的尾巴：红色方不会镜像）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6) and an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1).
Effect: a SNOW KICK-UP under a jumping figure's feet, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat snow puff 12 squares wide and 4 tall; 2 the puff 24 squares wide, ice chips flying up and outward at mirrored places; 3 the puff 30 squares wide and thin, the chips higher; 4 fading flakes.
Layout: one horizontal row of 4 equal 32:14 cells, image size 2048x224 (each cell 512x224, 16 px a square); centered across, the puff's middle 3 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `braum_fx_w_land.png`：W 落在队友身边（队友身上），5 帧

落地的一下：队友脚下一圈冰蓝色的冲击环往外扩（扁椭圆，白边），几块冰片弹起。**左右对称**，中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: a LANDING RING on the ground round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle above the ring EMPTY (a clear upright area 10 squares wide and 14 tall): 1 a white flash on the ground 6 squares wide; 2 a flat ice-blue ring 14 squares wide and 5 tall with a white rim; 3 the ring 24 x 8, ice chips flying up at mirrored places; 4 the ring breaking into flakes; 5 fading frost.
Layout: one horizontal row of 5 equal 28:20 cells, image size 2240x320 (each cell 448x320, 16 px a square); centered across, the ring's middle 4 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `braum_fx_w_guard.png`：W 护甲魔抗加成（布隆和队友身上，循环），4 帧

两人护甲魔抗提高的几秒：胸口高度一圈淡淡的冰蓝色环（扁椭圆，几块冰片亮光、一点金色火花），慢慢闪。**左右对称**，中间留空。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1), a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6) and a gold ramp used only for small glints (#FFF6C8, #FFE07A, #F2B83C, #B98322).
Effect: a GUARD RING round a figure's chest, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ice-blue ring 14 squares wide and 5 tall (the middle empty), 2 small ice glints and 2 tiny gold glints on it at mirrored places twinkling in turn.
Layout: one horizontal row of 4 equal 16:48 cells, image size 1024x768 (each cell 256x768, 16 px a square); the ring's middle 22 squares above the cell's bottom, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `braum_fx_r_slam.png`：R 冰川裂隙：砸地（他身前，不跟随），6 帧

盾砸到地上的一下：地面一圈大大的冰蓝色冲击波往外炸开（扁椭圆，白边，参考 R_ground_nova、R_Frozen_ground），冰块和雪雾往上飞，地面结一层冰。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: a GROUND NOVA, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash on the ground 10 squares wide; 2 a flat ice-blue shock ring 24 squares wide and 8 tall with a white rim, frozen ground inside it; 3 the ring 44 x 14, ice chunks flying up at mirrored places; 4 the ring breaking, the chunks highest, snow mist rising; 5 the mist spreading, chunks falling; 6 fading frost on the ground.
Layout: one horizontal row of 6 equal 50:26 cells, image size 4800x416 (each cell 800x416, 16 px a square); centered across, the ring's middle 6 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `braum_fx_r_wave.png`：R 冰川裂隙：沿直线冲出去的冰（朝施放方向，循环），4 帧

沿着直线往前冲的冰：一排从地里拱出来的冰刺（中间高两边低，像一道往前推的冰浪），前面最高最亮，后面的在缩回去（参考 R_flying_shards、W_Ice_shard）。**上下对称**（游戏会把它转向，往左时上下翻）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: a RUSH OF ICE SPIKES moving RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a cluster of sharp ice spikes bursting from the middle row, the front (right) ones tallest and brightest (white tips), shorter toward the back (left), spreading above and below the middle row the same; the spikes taking turns to grow and sink; frost mist trailing behind.
Layout: one horizontal row of 4 equal 24:20 cells, image size 1536x320 (each cell 384x320, 16 px a square); the front spike 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `braum_fx_r_crack.png`：R 留下的裂隙（地上，一段一段，约 4 秒），8 帧

裂隙的一段：地上一道冰蓝色的裂缝（参考 I_Ground_Crack、R_Frozen_ground），从中间裂开、发亮、结霜，最后慢慢暗下去消失。游戏沿着直线每隔 20 格放一段，几段连起来就是一整条冰川裂隙。**左右对称**，扁的（从斜上方看地面）。第 4 帧会停很久（裂隙持续约 4 秒），最后两帧是消失。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: a GLOWING ICE CRACK in the ground, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat jagged crack 22 squares wide and 7 tall seen from above at an angle (zigzag branches), white-blue glowing inside, pale frost round it; 1 a short crack 6 squares; 2 the crack 14 squares; 3 the full crack, brightest; 4 the full crack steady (this frame is held for seconds); 5 the same with fresh frost; 6 the glow dimming; 7 only frost and a thin dark-blue line; 8 a few frost specks.
Layout: one horizontal row of 8 equal 26:12 cells, image size 3328x192 (each cell 416x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `braum_fx_r_hit.png`：R 击飞（被打中的人身上），4 帧

被冰川裂隙击飞：一团冰蓝色的冰片和雪雾从下往上溅（中心白光）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice, frost, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #DFF8FF, #9EE6FF, #4FC3F7, #1E88E5, #0D47A1) and a pale frost ramp (#FFFFFF, #EEF7FF, #CFE6F5, #A5C8E1, #7FA6C6).
Effect: an ICE ERUPTION HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 6 squares; 2 ice shards and frost bursting upward 14 squares across, a white core; 3 the shards higher at mirrored places; 4 fading flakes.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `braum_fx_a_hit` | view_effects `league_braum_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `braum_fx_p_mark` | view_buffs `league_braum_p_mark`（跟随，画在人物上面；左右对称） | 10 × 8 |
| `braum_fx_p_stun` | view_buffs `league_braum_p_stun`（跟随，画在人物上面；左右对称） | 14 × 8 |
| `braum_fx_p_proc` | view_effects `league_braum_p_proc`（跟随，画在人物上面；左右对称） | 20 |
| `braum_fx_p_extra` | view_effects `league_braum_p_extra`（跟随，画在人物上面；左右对称） | 8 |
| `braum_fx_q_ice` | view_projectiles `league_braum_q_ice`（朝飞行方向转，画成朝右飞；上下对称） | 14 × 10 |
| `braum_fx_q_hit` | view_effects `league_braum_q_hit`（跟随，画在人物上面；左右对称） | 16 |
| `braum_fx_q_slow` | view_buffs `league_braum_q_slow`（跟随，画在人物下面；左右对称；R 裂隙的减速也用这张） | 16 × 6 |
| `braum_fx_e_raise` | view_effects `league_braum_e_raise`（跟随，画在人物上面；左右对称） | 36 × 44 |
| `braum_fx_e_on` | view_buffs `league_braum_e_on`（跟随，画在人物上面；左右对称） | 36 × 44 |
| `braum_fx_e_ally` | view_buffs `league_braum_e_ally`（跟随，画在人物上面；左右对称） | 10 × 10 |
| `braum_fx_w_dash` | view_effects `league_braum_w_dash`（跟随，画在人物下面；左右对称） | 30 × 12 |
| `braum_fx_w_land` | view_effects `league_braum_w_land`（跟随，画在人物上面；左右对称） | 26 × 18 |
| `braum_fx_w_guard` | view_buffs `league_braum_w_guard`（跟随，画在人物上面；左右对称；布隆自己的 w_self 也用这张） | 14 × 6 |
| `braum_fx_r_slam` | view_effects `league_braum_r_slam`（不跟随，画在人物下面；左右对称） | 48 × 22 |
| `braum_fx_r_wave` | view_projectiles `league_braum_r_wave`（朝飞行方向转，画成朝右跑；上下对称） | 22 × 18 |
| `braum_fx_r_crack` | view_effects `league_braum_r_crack`（不跟随，画在地上；左右对称；沿直线每 20 格放一段） | 24 × 10 |
| `braum_fx_r_hit` | view_effects `league_braum_r_hit`（跟随，画在人物上面；左右对称） | 16 |

- 两张表：`asset/league/effects/league_braum_fx`（小的）和 `league_braum_big`（e_on、r_wave、r_slam、r_crack），tag = 名字（build_braum.py 的 views；w_self 用 w_guard 的画、r_slow 用 q_slow 的画）。
- `q_ice`、`r_wave` 是飞行投射物，画面朝飞行方向转；`r_slam`、`r_crack` 不跟随；`q_slow` 脚下 buff（z -1）；`p_mark`、`p_stun`、`e_ally` 头顶（z 3）；`e_on`、`e_raise` 跟随画在人物上面，中间必须是空的；`r_crack` 第 4 帧拉长到裂隙的 4 秒。
- 用 `pixel_1x/` 切格（import_kassadin / import_gragas 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
