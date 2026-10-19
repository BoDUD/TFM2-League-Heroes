# 不灭狂雷 沃利贝尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型和动作已定（`design/volibear_idle.png`：3/4 正面朝右、用后腿站立的白色雷霆巨熊，白毛带冰蓝、腿和脚掌深灰紫、两条白毛辫、冰蓝水晶爪子）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），45 格高、42 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/volibear_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/volibear_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里沃利贝尔自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**他的雷电是白芯的青蓝色电光**，**雷云是深蓝色**，**护盾和爪子是冰蓝色**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **弹道图 `p_bolt` 画成朝右飞、上下对称**：游戏会按飞的方向把它转过去，往左飞时转半圈，上下对称才不会倒过来。**其余所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `volibear_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/volibear_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/volibear_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「狂雷渐起」（在普攻里） | 攻击叠攻速，满 5 层后攻击放出闪电打附近的敌人 | `p_bolt` · `p_hit` |
| 普攻 | 熊掌往前下方抓 | `a_hit` |
| W「暴怒撕咬」（每 5 秒普攻变成撕咬） | 撕咬并标记，再咬带标记的敌人加伤并回血 | `w_hit` · `w_mark` · `w_heal` |
| 技能 1 = Q「擂首一击」 | 四脚着地冲向敌人，扑上去砸晕 | `q_ms` · `q_hit` · `q_stun` |
| 技能 2 = E「霹天雳地」 | 远处落下一道大雷，减速；他站在雷里得到护盾 | `e_cloud` · `e_bolt` · `e_hit` · `e_slow` · `e_sh` |
| 大招「天声震落」 | 跳过去砸地，周围敌人受伤减速，之后 12 秒风暴形态；附近的敌方防御塔失效（扩展包） | `r_land` · `r_hit` · `r_form` · `r_tower` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、闪电、雷云、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：碎冰可以有一圈深蓝色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 青蓝色电光（闪电、雷击、冲击环）：`#FFFFFF`、`#E8FBFF`、`#A8F0FF`、`#52D2FF`、`#2290F0`、`#1D48B4`；
  - 深蓝色雷云：`#C6D0E8`、`#8A98C2`、`#5C6898`、`#3C4472`、`#262B50`、`#151832`；
  - 冰蓝色（护盾、爪子、碎冰）：`#FFFFFF`、`#E4F6FF`、`#B4E0FF`、`#7CC0F4`、`#4888D4`、`#2A549C`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：E 落雷的半径 30000，大招落地的半径 32000）。

### 1. `volibear_fx_p_bolt.png`：被动狂雷渐起：满层后攻击放出的闪电（弹道），4 帧（循环）

满 5 层后他攻击时从目标身上跳出去的闪电：一道**横着的锯齿形闪电**，白色的芯、青蓝色的外光，两头分出几根细小的电叉，每帧锯齿的折法都不一样（参考 Passive_Static_01、jacobsLadder、wiggleSpark_01）。**朝右、上下对称**。约 20 × 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A CRACKLING LIGHTNING BOLT in flight, 4 frames, a seamless loop, pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight: flying left it is turned half round and must not stand upside down): a horizontal jagged lightning bolt 18 squares long, a 1-square white core inside a 1-square cyan glow, 3 zigzag bends, 2 thin forks at each end at mirrored places; each frame the zigzag bends differently and a few cyan sparks flicker round it.
Layout: one horizontal row of 4 equal 20:10 cells, image size 1280x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `volibear_fx_p_hit.png`：被动：闪电打中（目标身上），4 帧

闪电打中的敌人：一下白色的电光，几道细小的闪电从上往下劈在身上，电火花往外溅（参考 Passive_tar_flipbook、Static_01、sparkMote）。**左右对称**。约 16 × 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A LIGHTNING STRIKE on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 2 thin jagged bolts striking down from 18 squares up onto it at mirrored places, a cyan burst 10 squares with a white core; 3 the bolts fading, 8 small cyan sparks flying out at mirrored angles; 4 a few fading sparks.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered across, the burst's middle 7 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `volibear_fx_a_hit.png`：普攻：熊掌抓中（目标身上），4 帧

冰蓝色的熊爪抓中目标：三道交叉的爪痕一闪，冰蓝色的光（参考 Swipe_A、Slash_B、Scratch、Flash_01）。**左右对称**（爪痕成 X 形交叉）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C) and an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A CLAW STRIKE on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 6 squares; 2 two crossing sets of 3 claw marks (an X of curved light streaks 14 squares across, white cores, ice-blue edges); 3 the marks thinner, small ice chips and sparks flying out at mirrored places; 4 fading marks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `volibear_fx_w_hit.png`：W 暴怒撕咬：撕咬命中（目标身上），5 帧

他扑上去撕咬：一张**冰蓝色发光的熊嘴虚影**（上下两排尖牙）猛地合上，咬合处炸开电光和爪痕（参考 W_Head_Mesh、W_Head_Teeth、W_Slash_B、W_Scratch）。**左右对称**（熊嘴正面朝外）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C) and an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A GLOWING BEAR BITE on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ghostly ice-blue bear jaw seen from the front, open (an upper and a lower row of 5 sharp white fangs each, 18 squares across, light edges, no outline); 2 the jaws closing; 3 the jaws shut with a white flash 12 squares where they meet and 6 cyan sparks; 4 two sets of claw marks crossing (an X, 18 squares) as the jaw fades; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `volibear_fx_w_mark.png`：W：标记（被咬的敌人头上，循环），4 帧

被咬过的敌人头上：一个**蓝白色发光的爪痕标记**（三道竖着的爪痕，下面一道弧线，像熊掌的符文），一闪一闪（参考 W_Marked_02、W_Marked_X_01）。**画在头上**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，标记在 38–48 格高）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C) and an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A CLAW MARK RUNE over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 3 short vertical claw strokes side by side over a curved stroke (a bear-paw sign 10 squares wide and 9 tall, white cores, ice-blue edges, no outline); 1 dim, 2 brighter, 3 brightest with 4 small sparks round it at mirrored places, 4 like 2.
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `volibear_fx_w_heal.png`：W：第二口回血（他身上），4 帧

咬第二口回血的时候他身上：一圈冰蓝色的光从脚下往上冲，几道蓝白色的光点往上飘（参考 Aura_Self、glowspecks、Flare_Omnimax）。**他的身体位置留空**（the huge bear stands in the middle, not drawn: 44 squares from his ears to the ground, about 42 squares wide, his head 32-44 squares above the ground）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C) and an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: AN ICE-BLUE HEALING SURGE round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the huge bear stands in the middle, not drawn: 44 squares from his ears to the ground, about 42 squares wide, his head 32-44 squares above the ground): 1 an ice-blue ring on the ground (an ellipse 34 squares wide and 9 tall) with a white glint; 2 light streaks rising from it 18 squares at mirrored places, blue sparkles; 3 the streaks 36 squares up and thinner, sparkles round his chest; 4 fading sparkles high up; the middle (his body) left clear.
Layout: one horizontal row of 4 equal 40:48 cells, image size 2560x768 (each cell 640x768, 16 px a square); centered across, the figure's ground 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `volibear_fx_q_ms.png`：Q 擂首一击：冲锋时身上的电光（他身上，循环），4 帧

他四脚着地冲锋时：身上缠着几道跳动的电光，背后拖着青蓝色的电火花，脚下一闪一闪（参考 Q_Underlit、Q_Footprint、Static_01、lightningMist_01）。**只画他身体的外围和脚下**（他四脚着地时约 60 格长、30 格高），**身体中间留空**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: CRACKLING ELECTRICITY round a running beast, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a four-legged bear 52 squares long and 30 tall stands in the middle, not drawn): 6 short jagged electric arcs (white cores, cyan glow) jumping on its outline at mirrored places, small cyan sparks round it, a flat cyan glow on the ground under it (an ellipse 48 wide and 6 tall); each frame the arcs jump to new places; the body's middle left clear.
Layout: one horizontal row of 4 equal 56:40 cells, image size 3584x640 (each cell 896x640, 16 px a square); centered across, the ground glow 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `volibear_fx_q_hit.png`：Q：扑砸命中（目标身上），5 帧

他扑上去把敌人砸晕：一道很粗的闪电从上劈下来，砸中的地方炸开一圈白色电光和冲击环，碎冰和电火花往外飞（参考 Q_Swipe_A、Star_Flash、Nova、flying_shards）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4) and an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C).
Effect: A THUNDERING SMASH on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thick white-cyan lightning bolt striking straight down onto it from 28 squares up; 2 a white star burst 16 squares where it lands, a cyan shock ring 22 squares wide and 6 tall on the ground; 3 ice shards (2x2 / 3x2 squares, a dark blue edge: solid) and cyan sparks flying out at mirrored places; 4 the ring fading; 5 a few sparks.
Layout: one horizontal row of 5 equal 26:30 cells, image size 2080x480 (each cell 416x480, 16 px a square); centered across, the ring's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `volibear_fx_q_stun.png`：Q：眩晕（敌人头上，循环），4 帧

被砸晕的敌人头上：几道转圈的小电光和电火花（参考 sparkMote、wiggleSpark_01）。**画在头上**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，电光在 36–44 格高）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: STUN SPARKS circling over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 3 small zigzag sparks (3x3 squares, white cores, cyan glow) on a flat ellipse 14 squares wide and 4 tall; each frame they move a quarter round it.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `volibear_fx_e_cloud.png`：E 霹天雳地：落雷前的预警（地上，不跟随），4 帧

雷落下来之前地上的预警：地上一圈**深蓝色的雷云阴影**（从斜上方看是扁椭圆），边上一圈青蓝色的电光慢慢变亮，中间几道细电弧（参考 E_AOE_Warning_A、E_AOE_Warning_B、E_Tornado_Indicator_Mult、Ult_Clouds_A）。**只画地面**，站在上面的人要看得见。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark storm-cloud ramp (#C6D0E8, #8A98C2, #5C6898, #3C4472, #262B50, #151832) and an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A STORM WARNING CIRCLE on the ground seen from above at an angle, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 60 squares wide and 20 tall - a dark storm-blue shadow inside (half transparent look: sparse dark squares, the ground showing through), a 1-2 square cyan rim; 1 the rim dim; 2 brighter, 3 thin cyan arcs crackling across the inside at mirrored places; 4 the rim brightest with a white top edge; nothing taller than 3 squares above the ground.
Layout: one horizontal row of 4 equal 64:24 cells, image size 4096x384 (each cell 1024x384, 16 px a square); centered across, the ellipse's middle 10 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `volibear_fx_e_bolt.png`：E：从天而降的大雷（地上，不跟随），5 帧

一道**从天上劈下来的巨大闪电柱**：又粗又亮，白色的芯、青蓝色的外光，顶上一团深蓝的雷云，劈到地上炸开一大团电光（参考 E_skyBolt_01、skyBolt_01、E_skyBolt_Hit_01、E_Glow_01）。**竖直的、左右对称**（游戏不转它）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4) and a dark storm-cloud ramp (#C6D0E8, #8A98C2, #5C6898, #3C4472, #262B50, #151832).
Effect: A HUGE LIGHTNING BOLT FROM THE SKY, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a vertical jagged lightning column from the top of the cell to the ground (6 squares thick, a 2-square white core, cyan glow; its zigzag mirrored left to right), a small dark storm cloud at its top (24 squares wide); 1 a thin bolt; 2 the full thick bolt and a white flash 20 squares on the ground; 3 the bolt flickering, a cyan burst on the ground 36 squares wide and 12 tall; 4 the bolt thin, sparks on the ground; 5 fading sparks.
Layout: one horizontal row of 5 equal 40:96 cells, image size 3200x1536 (each cell 640x1536, 16 px a square); centered across, the ground point 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `volibear_fx_e_hit.png`：E：被雷劈中（目标身上），4 帧

被落雷劈中的敌人：身上一下白光，电弧缠着身体跳动（参考 E_skyBolt_Hit_01、Static_01）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: AN ELECTROCUTED UNIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares; 2 a cyan burst 14 squares and 4 jagged arcs round it at mirrored places; 3 the arcs crackling, small sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `volibear_fx_e_slow.png`：E：减速（敌人脚下，循环），4 帧

被雷劈过减速的敌人脚下：一圈淡淡的青蓝色电光，几颗小电火花（参考 lightningMist_01、sparkMote）。**只画地面**。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A FAINT ELECTRIC RING at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin cyan ring on the ground (an ellipse 20 squares wide and 5 tall, 1 square thick) with 4 small sparks on it at mirrored places; each frame the sparks move along the ring.
Layout: one horizontal row of 4 equal 24:8 cells, image size 1536x128 (each cell 384x128, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `volibear_fx_e_sh.png`：E：护盾（他身上，循环），4 帧

他站在落雷里得到的护盾：**一圈冰蓝色的电光罩**围着他（只画边缘：一道冰蓝色的弧形轮廓，顶上最亮），上面几道电光流动（参考 E_ShieldAura、E_bubbleGrad_01、E_wigglRipple_01）。**只画外圈，他的身体位置留空**（the huge bear stands in the middle, not drawn: 44 squares from his ears to the ground, about 42 squares wide, his head 32-44 squares above the ground）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C) and an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: AN ICE-BLUE ELECTRIC SHIELD BUBBLE round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the huge bear stands in the middle, not drawn: 44 squares from his ears to the ground, about 42 squares wide, his head 32-44 squares above the ground): a rounded shield outline (an upright oval 46 squares wide and 48 tall, sitting on the ground) drawn only as a 1-2 square ice-blue edge, brightest at its top, a lighter inner line on the top third; 4 small electric arcs running along it at mirrored places; each frame the arcs move 3 squares along the edge; everything inside the oval left clear.
Layout: one horizontal row of 4 equal 50:52 cells, image size 3200x832 (each cell 800x832, 16 px a square); centered across, the oval's bottom 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `volibear_fx_r_land.png`：R 天声震落：落地砸地（他身上，跟随），6 帧

他跳起来砸到地上：地上一下白光，一圈巨大的青蓝色电光冲击环往外扩，地面裂开一个坑，几道闪电从坑里往上窜，碎冰和电火花往外飞（参考 R_landingCrater_Add、R_landingCrater_Blend_01、R_AOE_Warning、Nova、R_landing_blowBack）。**左右对称**，落点在格子中间偏下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4), a dark storm-cloud ramp (#C6D0E8, #8A98C2, #5C6898, #3C4472, #262B50, #151832) and an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C).
Effect: A THUNDEROUS LANDING seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash on the ground 20 squares wide; 2 a cyan shock ring on the ground (an ellipse 44 wide and 12 tall) and a dark storm-blue crater (an ellipse 30 wide and 9 tall, cracked); 3 the ring 66 wide and 18 tall, 4 jagged lightning arcs shooting up from the crater 16 squares at mirrored places, ice shards (a dark blue edge: solid) flung out; 4 the ring 76 wide, thinner, the arcs fading; 5 sparks and the crater; 6 the crater fading.
Layout: one horizontal row of 6 equal 80:40 cells, image size 7680x640 (each cell 1280x640, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `volibear_fx_r_hit.png`：R 命中（目标身上），4 帧

被大招砸中的敌人：一下很大的白色电光，青蓝色的冲击环，几道往外的电弧（参考 Star_Flash、R_tar_flipbook、Flash_01）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4).
Effect: A HEAVY THUNDER HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 9 squares; 2 a cyan star burst 17 squares with a white core, 6 jagged arcs at mirrored angles; 3 a cyan ring 19 squares, sparks flying out; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `volibear_fx_r_form.png`：R：风暴形态（他身上，循环），4 帧

大招落地后 12 秒的风暴形态：他背后一圈**深蓝色的雷云光晕**，上面电光不停地跳，肩膀上方几道竖着的冰蓝色电光尖刺（英雄联盟里他变大、背上长出冰刺和雷电鬃毛）（参考 R_auraArc_underLight_01、R_Background、R_Avatar_Blend_01、Ult_Clouds_A、R_iceGrad）。**画在他身体外围和背后，身体留空**（the huge bear stands in the middle, not drawn: 44 squares from his ears to the ground, about 42 squares wide, his head 32-44 squares above the ground）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark storm-cloud ramp (#C6D0E8, #8A98C2, #5C6898, #3C4472, #262B50, #151832), an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4) and an ice-blue ramp (#FFFFFF, #E4F6FF, #B4E0FF, #7CC0F4, #4888D4, #2A549C).
Effect: A STORM AURA behind and round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the huge bear stands in the middle, not drawn: 44 squares from his ears to the ground, about 42 squares wide, his head 32-44 squares above the ground): a dark storm-blue halo behind his upper body (a ring 52 squares wide and 40 tall around his shoulders and head, 3-4 squares thick, cloudy edge, no outline), 6 upright ice-blue spikes of light 6-10 squares tall rising from his shoulders at mirrored places, small jagged lightning arcs jumping on the halo; each frame the arcs jump to new places and the spikes flicker; the middle (his body) left clear.
Layout: one horizontal row of 4 equal square cells, image size 3840x960 (each cell 960x960, 16 px a square); centered across, the figure's ground 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `volibear_fx_r_tower.png`：R：防御塔失效（敌方防御塔身上，扩展包用，循环），4 帧

被大招打失效的防御塔：塔身上缠着跳动的电弧，顶上一团小雷云，一闪一闪（参考 R_Tower_Static_01、Static_01、jacobsLadder）。**左右对称**（一座 26 格宽、46 格高的塔站在中间，不画塔）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, lightning, cloud, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric lightning ramp (#FFFFFF, #E8FBFF, #A8F0FF, #52D2FF, #2290F0, #1D48B4) and a dark storm-cloud ramp (#C6D0E8, #8A98C2, #5C6898, #3C4472, #262B50, #151832).
Effect: ELECTRIC ARCS CRAWLING OVER A TOWER, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a tower 26 squares wide and 46 tall stands in the middle, not drawn): a small dark storm cloud over its top (20 squares wide), 6 jagged arcs (white cores, cyan glow) clinging to its sides at mirrored places, small sparks; each frame the arcs jump to new places.
Layout: one horizontal row of 4 equal 30:50 cells, image size 1920x800 (each cell 480x800, 16 px a square); centered across, the tower's base 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `volibear_fx_p_bolt` | view_projectiles `league_volibear_p_bolt`（随飞行方向转；画成**朝右**、**上下对称**） | 20 × 10 |
| `volibear_fx_p_hit` | view_effects `league_volibear_p_hit`（跟随，画在人物上面；左右对称） | 16 × 20 |
| `volibear_fx_a_hit` | view_effects `league_volibear_a_hit`（跟随，画在人物上面；左右对称） | 16 |
| `volibear_fx_w_hit` | view_effects `league_volibear_w_hit`（跟随，画在人物上面；左右对称） | 22 × 22 |
| `volibear_fx_w_mark` | view_buffs `league_volibear_w_mark`（跟随，画在人物上面 z 3；左右对称；循环，8 秒内一直在） | 14 × 12 |
| `volibear_fx_w_heal` | view_effects `league_volibear_w_heal`（跟随，画在人物上面 z 2；左右对称） | 40 × 48 |
| `volibear_fx_q_ms` | view_buffs `league_volibear_q_ms`（跟随，画在人物下面 z -1；左右对称；循环，冲锋 4 秒内一直在） | 56 × 40 |
| `volibear_fx_q_hit` | view_effects `league_volibear_q_hit`（跟随，画在人物上面；左右对称） | 26 × 30 |
| `volibear_fx_q_stun` | view_buffs `league_volibear_q_stun`（跟随，画在人物上面 z 3；左右对称；循环） | 16 × 10 |
| `volibear_fx_e_cloud` | view_effects `league_volibear_e_cloud`（不跟随，画在人物下面 z -1；左右对称；大图表） | 64 × 24 |
| `volibear_fx_e_bolt` | view_effects `league_volibear_e_bolt`（不跟随，画在人物上面 z 3；左右对称；大图表） | 40 × 96 |
| `volibear_fx_e_hit` | view_effects `league_volibear_e_hit`（跟随，画在人物上面；左右对称） | 18 |
| `volibear_fx_e_slow` | view_buffs `league_volibear_e_slow`（跟随，画在人物下面 z -1；左右对称；循环，2 秒） | 24 × 8 |
| `volibear_fx_e_sh` | view_buffs `league_volibear_e_sh`（跟随，画在人物上面 z 3；左右对称；循环，3 秒） | 50 × 52 |
| `volibear_fx_r_land` | view_effects `league_volibear_r_land`（跟随，画在人物下面 z -1；左右对称；大图表） | 80 × 40 |
| `volibear_fx_r_hit` | view_effects `league_volibear_r_hit`（跟随，画在人物上面；左右对称） | 20 |
| `volibear_fx_r_form` | view_buffs `league_volibear_r_form`（跟随，画在人物下面 z -1；左右对称；循环，12 秒；大图表） | 60 × 60 |
| `volibear_fx_r_tower` | view_effects `league_volibear_r_tower`（跟随，画在防御塔上面 z 3；左右对称；扩展包里落地附近的敌方塔每 15 tick 放一次） | 30 × 50 |

- 两张表：`asset/league/effects/league_volibear_fx`（小的）和 `league_volibear_big`（q_ms、e_cloud、e_bolt、e_sh、w_heal、r_land、r_form、r_tower），tag = 名字（build_volibear.py 的 views）。
- `e_cloud`、`e_bolt` 不跟随（地上的点）；`q_ms`、`e_sh`、`r_form`、`w_mark`、`q_stun`、`e_slow` 是循环的 buff 图；弹道图朝右、上下对称（随飞行转）；其余全部左右对称。
- 用 `pixel_1x/` 切格（import_poppy_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（碎冰保留描边）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（Codex 自己的 1 倍图可能洗白颜色，必要时从 raw/ 读回）。
