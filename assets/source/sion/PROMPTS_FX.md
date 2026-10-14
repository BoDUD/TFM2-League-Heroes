# 亡灵战神 赛恩：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/sion_idle.png`：游戏里的 3/4 正面待机，巨斧垂在近侧腿边）。他在游戏里是**高清**的（这张图是高清造型放大 3 倍），**游戏里显示成 90%：连斧头约 44 格高、60 格宽**（每个游戏格子里约 1.7 个细像素）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/sion_size.png`：待机按游戏里显示的大小放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/sion_shots.png`：定稿动作（按游戏里显示的大小放大 4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里赛恩的特效贴图（原皮的贴图大多是灰色形状、游戏里再上色，所以也放了海克斯皮肤的 Q、怒吼、熔炉的形状——**只看形状**），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**血红色的灵魂光（深红到粉白）、熔炉的橙色火星、亡灵的暗红黑烟、砸碎地面的尘土和碎石**。
> - **特效要亮**：每道光、每团火都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的护盾、火焰、光环只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。
> - **方向（重要，红色方不会镜像）**：地上的 `q_warn`、`q_slam` 和飞出去的 `e_roar` 画成朝右，**上下对称**（往左放时会上下翻）。其余所有画面（打中、身上、脚下、头顶、地上的冲击环）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sion_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `sion_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「灵魂熔炉」 | 巨斧劈砍；每杀一个单位永久加最大生命 | `a_hit` · `k_soul` |
| 技能 1 = Q「残虐猛击」 | 原地蓄力，身前地上出现范围；砸地，范围里的敌人被击飞 | `q_warn` · `q_slam` · `q_hit` |
| 技能 2 = E「杀手怒吼」+ W「灵魂熔炉」 | 怒吼冲击波直线飞出，减速、破甲；被英雄贴近时开熔炉护盾，3 秒后还在就炸开 | `e_roar` · `e_hit` · `e_shred` · `w_sh` · `w_burst` · `w_hit` |
| 大招 = R「蛮横冲撞」 | 免控冲向远处的英雄，撞上击飞，周围减速 | `r_go` · `r_crash` · `r_hit` |
| 附加包被动「死亡荣耀」 | 第一次被打死后变成亡灵继续打一阵 | `p_zombie` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟、冲击环、尘土都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个光和火的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 血红色灵魂光：`#FFFFFF`、`#FFE2D6`、`#FF9C7A`、`#FF4A3A`、`#D41E2C`、`#8E0E1E`；
  - 熔炉火星：`#FFF4D6`、`#FFD27A`、`#FF9A3A`、`#E85A1A`；
  - 亡灵黑烟：`#6A4A52`、`#45303A`、`#2A1C22`；
  - 尘土和碎石：`#E8DECF`、`#C2B39C`、`#94846E`、`#66584A`、`#40362E`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）；`q_warn`、`q_slam` 是从正上方看的地面长条（游戏会把它转到施放方向）。
- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，Q 范围长 50000、半宽 10000，E 飞 52000、半径 6000，W 炸开半径 26000，R 撞上减速半径 24000）。

### 1. `sion_fx_a_hit.png`：普攻打中（目标身上），4 帧

巨斧劈中：目标身上一道竖着的白红色劈痕一闪，裂成两道往两边弯的血红色月牙，溅出几点火星（参考 Q_Hit1_cresent、Q_Hi1_weaponswipe 的形状）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E).
Effect: an AXE CLEAVE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a vertical white-red cleave slash 12 squares tall and 2 wide with a white core; 3 the slash splitting into two blood-red crescents curving outward at mirrored places, 4 red sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sion_fx_k_soul.png`：灵魂熔炉：杀死一个单位，灵魂被他吸进胸口（他身上），5 帧

每杀一个单位永久加生命：一小团血红色的灵魂火（水滴形的小鬼火，两个并排的小黑眼点）从上面落进他胸口，胸口红光一亮，冒出几道短光（参考 Passive_Body_TX 胸口的红光）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E).
Effect: a SOUL DRAWN INTO A CHEST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small blood-red ghost wisp (a teardrop flame 5 squares wide and 7 tall, pointing up, two small dark eye dots side by side on its middle line) at the top of the cell; 2 the wisp lower, stretched downward; 3 the wisp at the cell's middle, shrinking into a red-white glow 6 squares across; 4 the glow 10 squares across with 4 short red rays at mirrored places; 5 a fading glow.
Layout: one horizontal row of 5 equal 16:26 cells, image size 1280x416 (each cell 256x416, 16 px a square); centered across; the glow of frames 3-5 centered 8 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sion_fx_q_warn.png`：Q 残虐猛击：蓄力时身前地上的范围（地上，循环），4 帧

蓄力的时候身前地上一条血红色的长方形范围（敌人看得见要砸哪里，参考英雄联盟 Q 的红色指示）：边框亮红色，里面暗红色（导入时 Claude 把里面调成半透明），中间一排朝右的箭头一闪一闪往前推。**上下对称**，朝右（左端在他脚下）。约 52 格长、24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E).
Effect: a DANGER ZONE ON THE GROUND seen from above, pointing to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a flat rectangle with slightly rounded ends, 52 squares long and 24 wide; its border 1-2 squares thick in bright red with white-pink highlights, the inside filled with flat dark crimson; a row of 4 chevrons (>) in red-pink along the middle line, the brightest chevron moving one step to the right each frame.
Layout: one horizontal row of 4 equal 54:26 cells, image size 3456x416 (each cell 864x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sion_fx_q_slam.png`：Q 砸地：斧头砸下去，裂缝沿着范围往前裂开（地上，播一次），5 帧

斧头砸地：从左端（他脚下）一道发红光的地裂沿着中线往右裂到头，裂缝两边对称地分出小岔，沿路炸起尘土和碎石（参考 Q_Hit2_groundcracks、Q_Hit2_scortch、Q_Hit2_groundsmoke）。**上下对称**，朝右。约 52 格长、24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E) and a dust ramp (#E8DECF, #C2B39C, #94846E, #66584A, #40362E).
Effect: a GROUND SMASH CRACKING FORWARD seen from above, pointing to the RIGHT, 5 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): 1 a white-red flash 8 squares across at the LEFT end (where the axe lands) and a short glowing crack starting from it; 2 a jagged crack along the middle line glowing red with a white core, reaching halfway, small side branches mirrored above and below it, dust puffs bursting at the left end; 3 the crack reaching the RIGHT end, dust and rubble bursting along it at mirrored places, 24 squares across at most; 4 the dust thinning, the crack dark red; 5 a faint dark crack and a few dust specks.
Layout: one horizontal row of 5 equal 54:26 cells, image size 4320x416 (each cell 864x416, 16 px a square); centered in every cell; the crack starts 1 square from the LEFT edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sion_fx_q_hit.png`：Q 砸中、击飞（目标身上），5 帧

被砸中击飞：目标身上血红色的冲击炸开，几道红光往上冲，带一点尘土。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E) and a dust ramp (#E8DECF, #C2B39C, #94846E, #66584A, #40362E).
Effect: a KNOCK-UP SMASH HIT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-red flash 6 squares; 2 a blood-red burst 12 squares across with a white core; 3 the burst's ring 18 squares across, 3 red streaks shooting upward at mirrored places, dust puffs at its bottom; 4 the streaks higher and thinner; 5 fading sparks.
Layout: one horizontal row of 5 equal 20:26 cells, image size 1600x416 (each cell 320x416, 16 px a square); centered across, the burst's middle 9 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sion_fx_e_roar.png`：E 杀手怒吼：飞出去的怒吼冲击波（直线飞，循环），4 帧

从嘴里吼出去的冲击波：三道一层套一层的血红色弧（像 「)))」），最前面那道最大、带白色高光，后面两道小一点，一闪一闪往前推（参考 distortion_soundwaves 的圆波）。**上下对称**，朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E).
Effect: a ROAR SHOCKWAVE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): three nested blood-red arcs like ')))', each 2 squares thick, the front arc 22 squares tall with a white-pink highlight, the two behind it smaller (16 and 10 tall); the arcs brightening one after another from back to front.
Layout: one horizontal row of 4 equal 16:24 cells, image size 1024x384 (each cell 256x384, 16 px a square); the front arc 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sion_fx_e_hit.png`：E 怒吼打中（目标身上），4 帧

被怒吼打中：目标身上一圈血红色的冲击波扩开、碎成火星。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E).
Effect: a ROAR HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a red ring 6 squares across; 2 a blood-red ring 12 squares across, 2 squares thick, white inner edge; 3 the ring 16 squares across breaking into 6 sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sion_fx_e_shred.png`：E 破甲（被吼中的人头顶，循环），4 帧

护甲被削：头顶一个小小的灰色盾牌，正中一道血红色的裂纹从上裂到下，一闪一闪。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E) and a dust ramp (#E8DECF, #C2B39C, #94846E, #66584A, #40362E).
Effect: a CRACKED SHIELD MARK over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small pale grey-beige shield shape 8 squares wide and 9 tall with a blood-red crack straight down its middle line, the crack pulsing brighter and dimmer, two small red chips falling off at mirrored places.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sion_fx_w_sh.png`：W 灵魂熔炉：护盾（他身上，跟着他，循环），4 帧

护盾：他周围一圈血红色和橙色的灵魂火，沿着一个大椭圆的边往上烧（火舌朝上），顶上白热的高光，边上几只小鬼火（带两个小黑眼点）对称地绕着飘。**中间人形位置留空**，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E) and an ember ramp (#FFF4D6, #FFD27A, #FF9A3A, #E85A1A).
Effect: a SOUL FURNACE SHIELD round a big figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 43 squares wide and 43 tall): the rim of an ellipse 54 squares wide and 52 tall made of blood-red and orange flames 2-4 squares tall licking upward, white-hot highlights at its top, 4 small red ghost wisps (teardrop flames with two dark eye dots) on the rim at mirrored places; the flames flickering in turn, the wisps one step higher each frame.
Layout: one horizontal row of 4 equal 56:54 cells, image size 3584x864 (each cell 896x864, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sion_fx_w_burst.png`：W 引爆：护盾炸开（他脚下，不跟随），5 帧

护盾撑满 3 秒还没破就炸开：地上一圈血红色加橙色的火焰冲击环往外扩（扁椭圆），环上火舌往上窜，火星往外飞，最后一点黑烟。**左右对称**，中间人形位置留空。范围约 52 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E), an ember ramp (#FFF4D6, #FFD27A, #FF9A3A, #E85A1A) and a dark smoke ramp (#6A4A52, #45303A, #2A1C22).
Effect: a FURNACE BLAST from a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle above the ring EMPTY (a clear upright area 40 squares wide and 20 tall): 1 a white-red flash ring at the feet 16 squares wide; 2 a blood-red fire ring 36 squares wide and 13 tall, 2 squares thick, with flame tongues rising at mirrored places; 3 the ring 52 wide and 20 tall, flame tongues 8 squares tall round it, orange embers flying outward at mirrored places; 4 the ring breaking into embers and dark smoke puffs; 5 fading smoke.
Layout: one horizontal row of 5 equal 54:30 cells, image size 4320x480 (each cell 864x480, 16 px a square); centered across, the ring's middle 6 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sion_fx_w_hit.png`：W 炸中（目标身上），4 帧

被熔炉炸中：目标身上一团血红色的火焰炸开往上窜，火星，一小团黑烟。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E), an ember ramp (#FFF4D6, #FFD27A, #FF9A3A, #E85A1A) and a dark smoke ramp (#6A4A52, #45303A, #2A1C22).
Effect: a SOUL-FIRE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-red flash 4 squares; 2 a blood-red flame burst 10 squares across, white core; 3 the flames 14 squares across licking upward, orange embers at mirrored places; 4 fading embers and a small puff of dark smoke.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sion_fx_r_go.png`：R 蛮横冲撞：冲锋中（他身上，跟着他，循环），4 帧

冲锋时：脚下一圈发红光的扁椭圆，两边对称地扬起尘土，身体两边几道血红色的光往上飘（像一身红色的怒气）。**中间人形位置留空**，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E) and a dust ramp (#E8DECF, #C2B39C, #94846E, #66584A, #40362E).
Effect: an ONSLAUGHT AURA round a big charging figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 36 squares wide and 27 tall above the ground ring): a flat glowing red ellipse 40 squares wide and 8 tall at the feet; dust clouds kicked up at both of its ends at mirrored places; red light streaks and embers rising along both sides of the figure up to 32 squares high, one step higher each frame.
Layout: one horizontal row of 4 equal 52:38 cells, image size 3328x608 (each cell 832x608, 16 px a square); centered across, the ellipse's middle 4 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `sion_fx_r_crash.png`：R 撞上：砸地冲击（他脚下，不跟随），6 帧

撞上英雄的一下：地上一圈血红色的大冲击环炸开，中间裂开几道发红光的地裂，碎石和尘土往上冲。**左右对称**。大招要大：约 80 格宽（比他自己还宽一截）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E) and a dust ramp (#E8DECF, #C2B39C, #94846E, #66584A, #40362E).
Effect: a HEAVY CRASH on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-red flash 18 squares wide; 2 a flat blood-red shock ring 50 squares wide and 16 tall, a dark crimson inner ring; 3 the ring 80 wide and 26 tall, 2-3 squares thick, glowing red cracks radiating from the middle at mirrored places, rubble and dust clumps rising 16 squares at mirrored places; 4 the dust higher, the ring thinning; 5 the cracks dimmer, the dust settling; 6 faint cracks.
Layout: one horizontal row of 6 equal 82:46 cells, image size 7872x736 (each cell 1312x736, 16 px a square); centered across, the ring's middle 14 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `sion_fx_r_hit.png`：R 撞飞（被撞的人身上），4 帧

被撞飞：目标身上一个血红色的大 X 形冲击一闪，几道红光往上冲。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E).
Effect: a CRIMSON UPWARD HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-red flash 6 squares; 2 a blood-red X-shaped shock 14 squares across with a white core; 3 3 red streaks shooting upward at mirrored places, the X fading; 4 fading motes.
Layout: one horizontal row of 4 equal 20:30 cells, image size 1280x480 (each cell 320x480, 16 px a square); centered across, the X's middle 9 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `sion_fx_p_zombie.png`：被动 死亡荣耀：亡灵状态（他身上，跟着他，循环），4 帧

第一次被打死后变成亡灵继续打：他周围暗红色和黑红色的死亡之火往上烧，几只淡红色的小骷髅鬼火往上飘，脚下一圈暗红色的地光（参考 Passive_Body_TX、Passive_Axe_shards）。**中间人形位置留空**，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red soul ramp (#FFFFFF, #FFE2D6, #FF9C7A, #FF4A3A, #D41E2C, #8E0E1E) and a dark smoke ramp (#6A4A52, #45303A, #2A1C22).
Effect: a DEATH-FIRE AURA round a big figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 43 squares wide and 45 tall): dark crimson and smoky black-red flames 4-7 squares tall rising along both sides of the figure; a dark red glowing ring 47 squares wide and 9 tall at the feet; 4 small pale-red skull wisps rising at mirrored places, one step higher each frame; red embers.
Layout: one horizontal row of 4 equal square cells, image size 3712x928 (each cell 928x928, 16 px a square); centered across, the ring's middle 4 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sion_fx_a_hit` | view_effects `league_sion_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `sion_fx_k_soul` | view_effects `league_sion_k_soul`（跟随，画在人物上面，z 3；左右对称） | 14 × 24 |
| `sion_fx_q_warn` | view_projectiles `league_sion_q_warn`（LineRangeProjectile：画在人物下面，朝施放方向转，画成朝右；上下对称；左端是他站的地方） | 52 × 24 |
| `sion_fx_q_slam` | view_projectiles `league_sion_q_slam`（新加：Q 砸地那一下的 LineRangeProjectile，画在人物下面，朝施放方向转，画成朝右；上下对称；左端是他站的地方；播一次） | 52 × 24 |
| `sion_fx_q_hit` | view_effects `league_sion_q_hit`（跟随，画在人物上面；左右对称） | 18 × 24 |
| `sion_fx_e_roar` | view_projectiles `league_sion_e_roar`（朝飞行方向转，画成朝右飞；上下对称） | 14 × 22 |
| `sion_fx_e_hit` | view_effects `league_sion_e_hit`（跟随，画在人物上面；左右对称） | 16 |
| `sion_fx_e_shred` | view_buffs `league_sion_e_shred`（跟随，画在人物上面；左右对称） | 10 × 10 |
| `sion_fx_w_sh` | view_buffs `league_sion_w_sh`（跟随，画在人物上面；左右对称；中间人形位置留空） | 54 × 52 |
| `sion_fx_w_burst` | view_effects `league_sion_w_burst`（不跟随，画在人物上面；左右对称） | 52 × 28 |
| `sion_fx_w_hit` | view_effects `league_sion_w_hit`（跟随，画在人物上面；左右对称） | 14 |
| `sion_fx_r_go` | view_buffs `league_sion_r_go`（跟随，画在人物下面；左右对称；中间人形位置留空） | 50 × 36 |
| `sion_fx_r_crash` | view_effects `league_sion_r_crash`（不跟随，画在人物下面；左右对称） | 80 × 44 |
| `sion_fx_r_hit` | view_effects `league_sion_r_hit`（跟随，画在人物上面；左右对称） | 18 × 28 |
| `sion_fx_p_zombie` | view_buffs `league_sion_p_zombie`（附加包加的 buff；跟随，画在人物上面；左右对称；中间人形位置留空） | 56 × 56 |

- 两张表：`asset/league/effects/league_sion_fx`（小的）和 `league_sion_big`（q_warn、q_slam、w_sh、w_burst、r_go、r_crash、p_zombie），tag = 名字（build_sion.py 的 views；`q_slam` 这次新加：Q 砸地的 LineRangeProjectile 带上这张，`repeat: false`，delay 拉到画面播完）。
- `q_warn`、`q_slam`、`e_roar` 是投射物，画面朝施放方向转；`q_warn` 的里面导入时调成半透明（只留边框和箭头不透明）；`w_burst`、`r_crash` 不跟随；`e_shred` 头顶；`w_sh`、`r_go`、`p_zombie` 中间必须是空的。
- 用 `pixel_1x/` 切格（import_kassadin / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
