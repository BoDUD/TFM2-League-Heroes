# 塔姆·肯奇（河流之王）：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型和动作已定（`design/tahmkench_idle.png`：3/4 正面朝右的待机）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），连帽子和尾巴 43 格高、51 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/tahmkench_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/tahmkench_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - `design/code_fx.png`：Claude 先用代码画的占位特效（6 倍），**只看大小和位置，不要照它的画法**。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里塔姆自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**河水是青绿色的（白色水沫芯）**，**舌头和口水是粉红色的**，**被动的叠层标记是青绿色的小鱼**，**W 落点的预警是一圈红色的环（上面有小鱼花纹）**，**厚实表皮的护盾是蓝紫色的流光**。
> - **特效要亮**：每团水、每道光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光圈、护盾、气泡只画外圈和两边，中间身体位置留空**（他很宽：约 50 格宽、40 格高）。
> - **方向（重要，红色方不会镜像）**：飞出去的舌头 `q_tongue` 画成朝右，**上下对称**（往左飞时会上下翻）。其余所有画面（打中、他身上、脚下、头顶、地上的水花和预警环、标记）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `tahmkench_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `tahmkench_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「培养品味」 | 舌头抽打；打中英雄叠一层，最多 3 层（头顶的小鱼标记） | `a_hit` · `t_pip1` · `t_pip2` · `t_pip3` |
| 技能 1 = Q「巨舌鞭笞」 | 舌头甩出去打中第一个单位：伤害、减速；打中英雄回血、叠层，3 层眩晕 | `q_tongue` · `q_hit` · `q_slow` · `q_heal` · `q_stun` |
| 被动里的 E「厚实表皮」 | 被两名敌方英雄围住时获得护盾 | `e_shield` |
| 技能 2 = W「深渊潜航」 | 潜进地里，在目标处冒出来，击飞周围的敌人 | `w_down` · `w_warn` · `w_up` · `w_hit` |
| 大招 = R「大快朵颐」 | 吞下队友（保护）或叠满 3 层的敌人（伤害），再吐出来 | `r_gulp` · `r_in` · `r_spit` · `r_full` · `r_bubble` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水、光、水沫、星星、环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 河水（水花、水柱、气泡、漩涡）：`#FFFFFF`、`#D8FFF5`、`#8BE8D4`、`#3FB3A5`、`#1F7A7A`、`#0E4A52`；
  - 舌头和口水：`#FFE8DE`、`#F7B2A0`、`#E07C78`、`#B8475A`、`#7A1E3C`；
  - 眩晕星星：`#FFFFFF`、`#FFF2A8`、`#FFD23F`、`#E39A1E`、`#9E5A12`；
  - 回血：`#F2FFE0`、`#B6F57A`、`#5ED45A`、`#2A9A44`；
  - 厚实表皮护盾：`#FFFFFF`、`#E2E8FF`、`#A9B6F2`、`#7B7FD6`、`#4E4AA0`；
  - W 预警环：`#FFE0DA`、`#FF6A5A`、`#D62A2A`、`#8E1414`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 射程 60000、宽 3000，W 落地击飞半径 14000）。

### 1. `tahmkench_fx_q_tongue.png`：Q 巨舌鞭笞：甩出去的舌头（朝目标飞，循环），2 帧

Q 的长舌头：一条湿漉漉的粉红色长舌头从左往右伸出去（舌尖在最右边，圆的），上面一道亮光，后段带一点口水滴（参考 Q_WaterTrail、TongueSaliva）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C) and a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a LASHING TONGUE flying to the RIGHT, 2 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a long wet pink tongue 26 squares long, 3 squares thick at its rounded tip on the right, thinning to 2 at the left end, a white wet highlight along its middle; 2 small teal-white drool drops trailing at mirrored places; a gentle wave along it that alternates between the frames.
Layout: one horizontal row of 2 equal 30:8 cells, image size 960x128 (each cell 480x128, 16 px a square); the tongue tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `tahmkench_fx_a_hit.png`：普攻打中（目标身上），3 帧

舌头抽中：一小团粉红色的口水溅开（白芯），夹着几点青绿色的水花（参考 ImpactTest、BA_Tar）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C) and a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a SLAP SPLAT on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 a pink drool splat 9 squares across with a white core and teal water flecks; 3 the splat 12 squares, droplets flying out at mirrored places, fading.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `tahmkench_fx_q_hit.png`：Q 巨舌鞭笞打中（目标身上），4 帧

舌鞭命中：一团青绿色的河水尖刺状溅开（参考 Q_SpikeSplashes：一根根弯弯的水刺往外甩），中间一点粉红的口水和白色水沫。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52) and a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C).
Effect: a TONGUE-LASH IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-and-pink flash 6 squares; 2 curved teal water spikes bursting out to both sides, 14 squares across, white foam at their tips; 3 the spikes 20 squares across, pink drool drops between them; 4 the spikes falling apart into fading droplets.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `tahmkench_fx_q_stun.png`：Q 三层眩晕（头顶），4 帧

眩晕：头顶三颗金色的小星星绕着转（白芯），中间夹两滴青绿色水珠。**左右对称**，4 帧合起来转一圈。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2A8, #FFD23F, #E39A1E, #9E5A12) and a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: STUN STARS circling over a head, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) in every frame: three gold 5-point stars 3 squares across with white cores on a flat ellipse 18 squares wide and 5 tall (the front one bigger), two teal water drops between them; each frame the stars a quarter of the way further round, kept mirrored by placing them in mirrored pairs.
Layout: one horizontal row of 4 equal 20:9 cells, image size 1280x144 (each cell 320x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `tahmkench_fx_q_heal.png`：Q 命中英雄时回血（他身上），4 帧

回血：几缕绿色的治疗光（参考 Heal_Wisps），从他身体两边往上飘，带几个小加号。**左右对称**，中间身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a heal-green ramp (#F2FFE0, #B6F57A, #5ED45A, #2A9A44).
Effect: HEALING WISPS rising round a big body, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY where he stands (his body is about 50 squares wide and 40 tall, not drawn: only the outer edge and the sides): green wisps and small plus signs 3 squares across rising up both sides and fading at the top, white cores.
Layout: one horizontal row of 4 equal square cells, image size 2816x704 (each cell 704x704, 16 px a square); the body's middle on the cell's center, its feet on row 33. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `tahmkench_fx_e_shield.png`：厚实表皮：护盾（他身上），4 帧

厚实表皮护盾：一层蓝紫色的半透明感的气泡壳包住他（参考 E_Shield_Glow / Wisps：蓝紫色的流光），只画外圈和几道流光高光，中间身体位置留空。第 1 帧张开、第 2–3 帧罩住、第 4 帧碎掉。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet shield ramp (#FFFFFF, #E2E8FF, #A9B6F2, #7B7FD6, #4E4AA0).
Effect: a SHIELD SHELL round a big body, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY where he stands (his body is about 50 squares wide and 40 tall, not drawn: only the outer edge and the sides): an oval shell 56 squares wide and 50 tall drawn as a 2-square rim with blue-violet wisps flowing along it and a few white glints; 1 the shell forming, 36 wide; 2 full; 3 full, the wisps moved round; 4 breaking into pieces that fade.
Layout: one horizontal row of 4 equal 60:54 cells, image size 3840x864 (each cell 960x864, 16 px a square); the shell's middle on the cell's center, the body's feet on row 44. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `tahmkench_fx_w_down.png`：W 深渊潜航：潜下去的水花（他脚下），4 帧

潜下去：他脚下的地面变成一圈河水，水从四周往上翻起又落下（参考 W_Splashes、Z_LinearSplashes），中间留空让他沉下去。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a DIVE SPLASH round a big body's feet, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY above the ground where he sinks: 1 a ring of river water opening on the ground, an ellipse 30 squares wide and 8 tall; 2 water walls splashing up at both sides 18 squares high with white foam crests; 3 the splashes falling back, drops; 4 the ring closing, ripples.
Layout: one horizontal row of 4 equal 48:36 cells, image size 3072x576 (each cell 768x576, 16 px a square); the ring's middle 2 squares above the cell's bottom, centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `tahmkench_fx_w_warn.png`：W 深渊潜航：冒出地点的预警（地上，不跟随），6 帧

他要冒出来的地方：地上一圈红色的预警环（参考 W_Decal：红色的环，上面三条小鱼的花纹），环里面是翻滚的深色河水和一串冒上来的气泡。6 帧循环约 1 秒。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red marker ramp (#FFE0DA, #FF6A5A, #D62A2A, #8E1414) and a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a GROUND WARNING where he will burst up, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a red ring seen from above at an angle, an ellipse 30 squares wide and 12 tall, 1 square thick, with three small fish shapes on it at mirrored places; inside it dark churning river water with bubbles rising and popping, a different pair of bubbles each frame.
Layout: one horizontal row of 6 equal 32:14 cells, image size 3072x224 (each cell 512x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `tahmkench_fx_w_up.png`：W 深渊潜航：冒出来的水柱（他身上），4 帧

冒出来：一根粗水柱从地里冲上来（白色水沫芯，青绿色），落地时四周溅起一圈水花（参考 W_portal、Z_Splases）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a WATER BURST as a big body shoots out of the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thick column of river water 16 squares wide shooting up 46 squares from the ground, a white foam core; 2 the column breaking at the top into drops, a splash ring on the ground 30 squares wide; 3 the drops falling at both sides, the ring 44 wide; 4 ripples and the last drops.
Layout: one horizontal row of 4 equal 48:54 cells, image size 3072x864 (each cell 768x864, 16 px a square); the ground ring's middle 2 squares above the cell's bottom, centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `tahmkench_fx_w_hit.png`：W 击飞（被击飞的单位脚下），3 帧

被掀飞：单位脚下溅起一小团河水（参考 WaterSplash）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a SMALL SPLASH under a unit thrown up, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): water splashing up from the ground at both sides, 12 squares high with white foam tips, then falling as drops.
Layout: one horizontal row of 3 equal 20:14 cells, image size 960x224 (each cell 320x224, 16 px a square); the splash's base on the cell's bottom row, centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `tahmkench_fx_r_gulp.png`：R 大快朵颐：一口吞下（他头上），4 帧

一口吞下：他嘴巴的位置上一对大牙齿（参考 R_UI：上下两排米黄色的尖牙）从上下合拢「咔嚓」咬合，四周甩出粉红色的口水滴和青绿色水珠。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C) and a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a CHOMP over a big head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two rows of cream-white fangs (upper and lower jaws, 22 squares wide) snapping shut; 1 the jaws wide apart 16 squares; 2 closing; 3 shut with a white flash where they meet, pink drool drops flung out to both sides; 4 the teeth gone, drops falling.
Layout: one horizontal row of 4 equal 32:24 cells, image size 2048x384 (each cell 512x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `tahmkench_fx_r_in.png`：R 大快朵颐：被吞的单位（目标身上），3 帧

被吞进去：被吞的英雄身上卷起一团青绿色的河水漩涡把他裹住缩小（参考 R_Target_waterwave）。**左右对称**（漩涡用两股对称的水流）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a SWALLOWING WHIRL on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two mirrored streams of river water swirling up round an upright figure 10 squares wide and 22 tall (not drawn), closing in; 1 the streams wide 22 squares; 2 wrapping the figure; 3 shrunk to a small whirl 8 squares with a white core.
Layout: one horizontal row of 3 equal 24:28 cells, image size 1152x448 (each cell 384x448, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `tahmkench_fx_r_spit.png`：R 吐出来（目标身上），3 帧

吐出来：一团粉红色的口水加青绿色的水哗地溅开（白芯）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C) and a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a SPIT-OUT SPLASH on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-and-pink burst 8 squares; 2 a splash of pink drool and teal water 16 squares across, drops at mirrored places; 3 the drops falling and fading.
Layout: one horizontal row of 3 equal square cells, image size 1056x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `tahmkench_fx_t_pip1.png`：被动 培养品味：第 1 层的标记（英雄头顶，循环），2 帧

被动叠层标记：一条小小的青绿色鱼头标记（参考 P_Marker_Update 的鱼），朝上、正面，**左右对称**，画在格子左边，三张图位置不同、可以叠在一起显示 1–3 层。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52) and a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C).
Effect: a TASTE MARK over a champion's head, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a tiny teal FISH HEAD seen from the front, 5 squares wide and 5 tall, mouth up, a white glint, a pink tongue-tip dot; the second frame lifted 1 square (a bob); drawn at the LEFT of the cell's top row band of the cell (three cells side by side make the 1-3 stack row).
Layout: one horizontal row of 2 equal 21:7 cells, image size 672x112 (each cell 336x112, 16 px a square); the mark's middle on the cell's middle row; slot 1 at column 4, slot 2 at column 10, slot 3 at column 16. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `tahmkench_fx_t_pip2.png`：被动 培养品味：第 2 层的标记（英雄头顶，循环），2 帧

被动叠层标记：一条小小的青绿色鱼头标记（参考 P_Marker_Update 的鱼），朝上、正面，**左右对称**，画在格子中间，三张图位置不同、可以叠在一起显示 1–3 层。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52) and a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C).
Effect: a TASTE MARK over a champion's head, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a tiny teal FISH HEAD seen from the front, 5 squares wide and 5 tall, mouth up, a white glint, a pink tongue-tip dot; the second frame lifted 1 square (a bob); drawn in the MIDDLE of the cell (three cells side by side make the 1-3 stack row).
Layout: one horizontal row of 2 equal 21:7 cells, image size 672x112 (each cell 336x112, 16 px a square); the mark's middle on the cell's middle row; slot 1 at column 4, slot 2 at column 10, slot 3 at column 16. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `tahmkench_fx_t_pip3.png`：被动 培养品味：第 3 层的标记（英雄头顶，循环），2 帧

被动叠层标记：一条小小的青绿色鱼头标记（参考 P_Marker_Update 的鱼），朝上、正面，**左右对称**，画在格子右边，三张图位置不同、可以叠在一起显示 1–3 层。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52) and a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C).
Effect: a TASTE MARK over a champion's head, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a tiny teal FISH HEAD seen from the front, 5 squares wide and 5 tall, mouth up, a white glint, a pink tongue-tip dot; the second frame lifted 1 square (a bob); drawn at the RIGHT of the cell (three cells side by side make the 1-3 stack row).
Layout: one horizontal row of 2 equal 21:7 cells, image size 672x112 (each cell 336x112, 16 px a square); the mark's middle on the cell's middle row; slot 1 at column 4, slot 2 at column 10, slot 3 at column 16. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `tahmkench_fx_q_slow.png`：Q 减速（目标脚下，循环），2 帧

减速：目标脚下一滩粉红色的黏口水，表面一两点亮光（参考 TongueSaliva）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a tongue-pink ramp (#FFE8DE, #F7B2A0, #E07C78, #B8475A, #7A1E3C).
Effect: a STICKY DROOL PUDDLE at a unit's feet, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat pink puddle seen from above at an angle, an ellipse 22 squares wide and 6 tall, two white glints that move between the frames, a drip at each side.
Layout: one horizontal row of 2 equal 24:8 cells, image size 768x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `tahmkench_fx_r_full.png`：R 消化中（他身上，循环），3 帧

吞着人的时候：他身体周围冒几个青绿色的小气泡往上飘。**左右对称**，中间身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: DIGESTION BUBBLES round a big body, 3 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY where he stands (his body is about 50 squares wide and 40 tall, not drawn: only the outer edge and the sides): small teal bubbles 2-3 squares with white glints rising at both sides, a different height each frame.
Layout: one horizontal row of 3 equal square cells, image size 2112x704 (each cell 704x704, 16 px a square); the body's middle on the cell's center, its feet on row 33. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `tahmkench_fx_r_bubble.png`：R 被吞的单位的标记（循环），2 帧

被吞的单位：裹在一个青绿色的水泡里（只画水泡的外圈和高光）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water, foam, smoke, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D8FFF5, #8BE8D4, #3FB3A5, #1F7A7A, #0E4A52).
Effect: a WATER BUBBLE round a unit, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a teal bubble rim 1 square thick round an upright figure 10 squares wide and 22 tall (not drawn), 22 wide and 26 tall, two white glints moving between the frames.
Layout: one horizontal row of 2 equal 24:28 cells, image size 768x448 (each cell 384x448, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 交回前请检查

- 19 张都在、文件名对；每张有 8 倍图和 `pixel_1x/` 原尺寸图，透明度只有 0 和 255。
- 舌头上下对称、舌尖朝右；其余每张逐格左右对称。
- 围着他的画面中间留空；没有黑描边；每个形状有亮芯。
- 全部画完后最后写 `outputs/tahmkench-fx/HANDOFF.md`，打包成 `outputs/tahmkench_fx_pack_done.zip`。

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `tahmkench_fx_q_tongue` | view_projectiles `league_tahmkench_q_tongue`（朝飞行方向转，画成朝右；上下对称） | 28 × 6 |
| `tahmkench_fx_a_hit` | view_effects `league_tahmkench_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `tahmkench_fx_q_hit` | view_effects `league_tahmkench_q_hit`（跟随，画在人物上面；左右对称） | 20 |
| `tahmkench_fx_q_stun` | view_effects `league_tahmkench_q_stun`（跟随，头顶，约 1.25 秒） | 18 × 7 |
| `tahmkench_fx_q_heal` | view_effects `league_tahmkench_q_heal`（跟随，画在他上面；左右对称） | 40 × 40 |
| `tahmkench_fx_e_shield` | view_effects `league_tahmkench_e_shield`（跟随，画在他上面；左右对称） | 56 × 50 |
| `tahmkench_fx_w_down` | view_effects `league_tahmkench_w_down`（跟随，画在他身后；大图） | 44 × 32 |
| `tahmkench_fx_w_warn` | view_effects `league_tahmkench_w_warn`（地上，不跟随，画在人物下面；大图） | 30 × 12 |
| `tahmkench_fx_w_up` | view_effects `league_tahmkench_w_up`（跟随，画在他身后；大图） | 44 × 50 |
| `tahmkench_fx_w_hit` | view_effects `league_tahmkench_w_hit`（跟随，画在人物上面；左右对称） | 18 × 12 |
| `tahmkench_fx_r_gulp` | view_effects `league_tahmkench_r_gulp`（跟随，画在他上面；左右对称） | 30 × 22 |
| `tahmkench_fx_r_in` | view_effects `league_tahmkench_r_in`（跟随，画在人物上面） | 22 × 26 |
| `tahmkench_fx_r_spit` | view_effects `league_tahmkench_r_spit`（跟随，画在人物上面；左右对称） | 20 |
| `tahmkench_fx_t_pip1` | view_buffs `league_tahmkench_t_pip1`（头顶，第 1 个位置；三张叠在一起就是 3 层；左右对称） | 5 × 5 |
| `tahmkench_fx_t_pip2` | view_buffs `league_tahmkench_t_pip2`（头顶，第 2 个位置；三张叠在一起就是 3 层；左右对称） | 5 × 5 |
| `tahmkench_fx_t_pip3` | view_buffs `league_tahmkench_t_pip3`（头顶，第 3 个位置；三张叠在一起就是 3 层；左右对称） | 5 × 5 |
| `tahmkench_fx_q_slow` | view_buffs `league_tahmkench_q_slow`（脚下，画在人物下面；左右对称） | 22 × 6 |
| `tahmkench_fx_r_full` | view_buffs `league_tahmkench_r_full`（他身上；左右对称） | 40 × 40 |
| `tahmkench_fx_r_bubble` | view_buffs `league_tahmkench_r_bubble`（被吞的单位身上；左右对称） | 22 × 26 |

- 两张表：`asset/league/effects/league_tahmkench_fx`（小的）和 `league_tahmkench_big`（w_down、w_warn、w_up），tag = 名字（build_tahmkench.py 的 views；现在是 tools/art/fx_tahmkench.py 用代码画的占位，导入后替换）。
- `q_tongue` 是飞行投射物，画面朝飞行方向转；`w_warn` 不跟随、画在地上；`q_slow` 脚下 buff（z -1）；`t_pip1-3` 头顶三个位置。
- 用 `pixel_1x/` 切格，断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
