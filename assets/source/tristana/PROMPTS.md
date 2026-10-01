# 崔丝塔娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型和 8 个动作已经做完并导入游戏，这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里崔丝塔娜经典皮肤自己的特效贴图（E 的爆炸闪光和烟团、R 的光环、W 落地的光晕），只在本地用，不要提交。颜色和画风对照 `design/tristana_design.png`（定稿造型，8 倍）；大小对照 `design/tristana_ingame.png`（游戏里的全部帧，4 倍）：崔丝塔娜从护目镜顶到脚底 41 格，其他英雄约 35–40 格。
> - 特效照下面每一条和「所有特效图的规则」画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最好打成一个 zip。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动 | 大炮打出铁炮弹；被动「瞄准」射程随等级变长；「爆炸火花」被动：普攻打死的敌人原地爆炸 | `tristana_fx_bolt` · `tristana_fx_shot` · `tristana_fx_hit` · `tristana_fx_p_boom` |
| 技能 1 = E「爆炸火花」+ Q「急速射击」 | 炮口朝下把炸弹射到目标身上，4 秒后爆炸；她每打中一下加一层（炸弹上的红灯数），满 4 层立刻大爆炸；同时开急速射击，7 秒内攻速大涨，炮管冒蒸汽 | `tristana_fx_e_shot` · `tristana_fx_e_charge` · `tristana_fx_e_bomb` · `tristana_fx_e_stack` · `tristana_fx_e_boom` · `tristana_fx_e_boom4` · `tristana_fx_q_cast` · `tristana_fx_q_rapid` |
| 技能 2 = W「火箭跳跃」 | 炮口朝地一轰跳起来，落地炸开一圈火环，减速周围的敌人；击杀英雄或满层引爆时冷却刷新（头顶一个小火箭金光） | `tristana_fx_w_land` · `tristana_fx_w_ready` |
| 大招 = R「毁灭射击」 | 一发大炮弹，炮口大爆风，打中目标后落点一圈冲击波，把目标和身边的敌人击退，落地眩晕 | `tristana_fx_r_muzzle` · `tristana_fx_r_ball` · `tristana_fx_r_hit` · `tristana_fx_r_blast` · `tristana_fx_r_stun` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（按每条写的用）：
  - 火焰：`#FFFFFF`、`#FFF6C8`、`#FFD84A`、`#FF9A1F`、`#F2561B`、`#B8260F`、`#5E1208`；
  - 烟和尘土：`#E6E0D8`、`#B9B0A6`、`#857B72`、`#574F4A`、`#36302D`；
  - 铁（炮弹、炸弹）：`#1A1A22`、`#34343F`、`#585866`、`#8A8A99`；铜箍：`#87602E`、`#C8994E`、`#E6BF86`（和她的炮一样）；
  - 红灯：`#821D3F`、`#D13845`、`#FF6A6A`；金光、星星：`#FFFFFF`、`#FFF6C8`、`#FFD84A`、`#C8994E`。
- **飞行类特效（炮弹、炸弹、大炮弹）一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- **炮口火光（普攻、E、R）画在她自己身上**：格子的左边中间（E 是左上角）就是炮口的位置，火往右喷；她朝左时游戏会整张左右镜像。
- 命中、爆炸、地面特效居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 2 倍）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `tristana_fx_bolt.png`：普攻炮弹（飞行），4 帧循环

从炮口打出去的一颗铁炮弹：深灰的圆球，右上一点亮高光，外面裹一圈橙红的火光，后面拖着一小段火焰和灰烟（往左）。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an iron cannonball (#1A1A22, #34343F, #585866, #8A8A99) wrapped in fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) with a little smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a CANNONBALL flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round dark iron ball with a bright highlight at its upper right at 70% of the cell width, about half the cell height, a thin rim of orange fire round it; behind it a short tapering tail of flame and grey smoke to the left edge, flickering each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the ball on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `tristana_fx_shot.png`：普攻炮口火光（她的炮口，朝右），5 帧

开炮时炮口喷出的火光：白热的芯，往右喷出一团橙黄的火焰，上下两边翻出两小团灰白的烟，最后散成烟。格子的左边中间就是炮口。约 18 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a MUZZLE FLASH blasting to the RIGHT from the middle of the cell's LEFT edge (the muzzle is there), 5 frames: 1 a white-hot burst at the left edge; 2 a cone of orange and yellow flame shooting right to 80% of the cell width, two small puffs of smoke curling up and down beside it; 3 the flame shrinks, the smoke puffs grow; 4 grey smoke puffs drifting right; 5 faint smoke.
Layout: one horizontal row of 5 equal cells, each 4 wide to 3 tall, image size 1280x192 (each cell 256x192); the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `tristana_fx_e_shot.png`：E 炮口喷出炸弹的火光（炮口朝右下 45 度），4 帧

E 出手时炮口朝右下 45 度喷出的一小团火光和烟：格子的左上角是炮口，火往右下喷。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a small MUZZLE PUFF blasting DOWN-RIGHT at 45 degrees from the cell's upper-left corner (the muzzle is there), 4 frames: 1 a white-hot spark at the corner; 2 a short cone of orange flame pointing down-right; 3 a puff of grey smoke; 4 faint smoke.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the muzzle at each cell's upper-left corner. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `tristana_fx_e_charge.png`：E 爆炸火花：炸弹（飞行），4 帧循环

扔向目标的炸弹：一个黑铁圆弹，中间一道铜箍，顶上一截引信冒着火星；飞的时候引信的火星闪动（参考 E 的爆炸闪光图）。约 10 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a black iron bomb (#1A1A22, #34343F, #585866, #8A8A99) with a brass band (#87602E, #C8994E, #E6BF86) and a sparking fuse (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208).
Effect: an EXPLOSIVE CHARGE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round black iron bomb at 60% of the cell width with a brass band across its middle and a white highlight; a short fuse sticking out of its back (left), its tip a bright spark that flickers yellow-white each frame, two or three tiny sparks trailing left.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the bomb on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `tristana_fx_e_bomb.png`：E 炸弹粘在目标身上（4 行：0–3 层），每行 2 帧闪烁

粘在敌人身上的炸弹：黑铁圆弹、铜箍、一盏红色指示灯，引信冒火星；上面一排小红灯表示她打了几下（第 1 行 0 个、第 2 行 1 个、第 3 行 2 个、第 4 行 3 个），第 2 帧红灯和火星更亮（闪烁）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a black iron bomb (#1A1A22, #34343F, #585866, #8A8A99) with a brass band (#87602E, #C8994E, #E6BF86), red lights (#821D3F, #D13845, #FF6A6A) and fuse sparks (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208).
Effect: a BOMB STUCK ON A TARGET, 4 rows x 2 frames (the rows are 4 separate states): every cell shows the same round black iron bomb (about 60% of the cell width, in the lower middle of the cell) with a brass band, a small red light on its front and a short fuse on top with a spark; above the bomb a row of small bright RED dots counting her hits: row 1 no dots, row 2 one dot, row 3 two dots, row 4 three dots (dots 2 squares each, 1 square apart, centred). Frame 1: the light and the dots dark red; frame 2: bright red with a white core and a brighter spark (a blink).
Layout: 4 rows of 2 equal square cells, image size 512x1024 (each cell 256x256); the bomb in the lower middle of every cell, the dots above it. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `tristana_fx_e_stack.png`：E 加一层时的火花（目标身上），3 帧

她每打中一下炸弹加一层时，炸弹上闪一下的红白火花。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, red (#821D3F, #D13845, #FF6A6A) and white-yellow sparks (#FFFFFF, #FFF6C8, #FFD84A, #C8994E).
Effect: a small STACK SPARK, 3 frames: 1 a bright white four-pointed spark with a red glow at the centre; 2 the spark larger, four short red rays and tiny sparks flying out; 3 a few fading red specks.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `tristana_fx_e_boom.png`：E 炸弹爆炸（地面上，不跟随），8 帧

炸弹爆炸：白热的闪光，炸开一团橙黄的火球，火球往外鼓、顶上翻出黑红的烟，地上一圈扁椭圆的冲击波，碎片往外飞；最后是一团慢慢散开的灰烟（参考 E 的爆炸闪光和烟团）。约 50 格宽、40 格高，地面在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: an EXPLOSION on the ground, 8 frames: 1 a white-hot flash at the lower middle; 2 a round fireball of yellow and orange bursting up and out, a flat shockwave ring on the ground (an ellipse twice as wide as tall) spreading to 80% of the cell width; 3 the fireball at its biggest (70% of the cell height), dark red flames at its edge, small debris flying out; 4 the fire turns red and orange, dark smoke rising from its top; 5 a mushroom of dark smoke with embers; 6 the smoke grey and spreading; 7 thin grey smoke; 8 a few faint wisps.
Layout: one horizontal row of 8 equal cells, each 5 wide to 4 tall, image size 2560x256 (each cell 320x256); the ground line at 85% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `tristana_fx_e_boom4.png`：E 满 4 层立即引爆（更大更亮），9 帧

满层的大爆炸：比上一张更大、更亮，白色和亮黄的芯更大，火球外面加一圈红色的冲击环和往外射的火星，烟更浓。约 60 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208), red (#821D3F, #D13845, #FF6A6A) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a BIG EXPLOSION on the ground (a stronger version of a normal explosion), 9 frames: 1 a big white flash; 2 a huge white-yellow fireball bursting out, a bright red shock ring and a ground shockwave ellipse; 3 the fireball at its biggest (80% of the cell height) with rays of sparks shooting out; 4 orange and red fire rolling outward; 5 thick dark smoke rising with embers; 6-7 grey smoke spreading; 8 thin smoke; 9 faint wisps.
Layout: one horizontal row of 9 equal cells, each 5 wide to 4 tall, image size 2880x256 (each cell 320x256); the ground line at 85% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `tristana_fx_p_boom.png`：爆炸火花被动：普攻击杀的敌人爆炸（地面，不跟随），6 帧

被她普攻打死的敌人原地炸开：比 E 的爆炸小的一团橙色火球和灰烟。约 34 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a SMALL EXPLOSION on the ground, 6 frames: 1 a white flash; 2 an orange fireball bursting out, a thin ground ring; 3 the fireball at its biggest (60% of the cell height), red at its edge; 4 red fire and dark smoke; 5 grey smoke; 6 faint wisps.
Layout: one horizontal row of 6 equal cells, each 5 wide to 4 tall, image size 1920x256 (each cell 320x256); the ground line at 85% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `tristana_fx_hit.png`：普攻命中（目标身上），5 帧

炮弹打中目标：一团小小的橙黄火花炸开，碎片和烟往外飞。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a CANNONBALL IMPACT, 5 frames: 1 a white-hot flash at the centre; 2 a small burst of orange and yellow fire with sparks flying out; 3 the burst breaks into red embers and a puff of grey smoke; 4 smoke and a few embers; 5 faint smoke.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `tristana_fx_q_cast.png`：Q 急速射击开启（她身上，炮口），5 帧

开急速射击的一瞬：炮口周围冒出一圈白色的蒸汽和金色的火星，往上飘散（像炮管突然烧热）。格子左下是她的身体，火星在格子右半边（炮口在那）。约 24 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, steam (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D) and golden sparks (#FFFFFF, #FFF6C8, #FFD84A, #C8994E).
Effect: RAPID FIRE starts: steam and sparks bursting from a hot cannon muzzle placed at 75% of the cell width and 60% of the cell height, 5 frames: 1 a ring of bright golden sparks round the muzzle; 2 white steam puffs shooting up and back from it, sparks flying up; 3 more steam, the sparks rising; 4 the steam drifting up and fading; 5 faint wisps.
Layout: one horizontal row of 5 equal cells, each 6 wide to 5 tall, image size 1920x320 (each cell 384x320). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `tristana_fx_q_rapid.png`：Q 急速射击持续（她身上，7 秒循环），4 帧循环

急速射击期间炮管发烫：炮口上方一缕一缕往上冒的白色蒸汽和零星的金色火星，炮口一圈淡淡的橙色热光。格子的位置和上一张一样（炮口在格子右半边）。约 24 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, steam (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D), a hot glow (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and golden sparks (#FFFFFF, #FFF6C8, #FFD84A, #C8994E).
Effect: RAPID FIRE lasting, 4 frames, a seamless loop: at a cannon muzzle placed at 75% of the cell width and 60% of the cell height, a faint orange heat glow round the muzzle, thin wisps of white steam rising from it and drifting up and back (left), one or two small golden sparks; the wisps move up each frame.
Layout: one horizontal row of 4 equal cells, each 6 wide to 5 tall, image size 1536x320 (each cell 384x320). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `tristana_fx_w_land.png`：W 火箭跳跃落地（地面，画在人物下面），6 帧

落地的冲击：地上一圈扁椭圆的火环往外扩，扬起一圈尘土和碎石，火环里带红色的火苗（参考 W 落地的光晕）。约 44 格宽、28 格高，地面在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and dust (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a LANDING BLAST on the ground seen from above at an angle, 6 frames: 1 a bright flash at the lower middle; 2 a flat ring of fire (an ellipse twice as wide as tall) spreading from the middle, dust and pebbles thrown up at its edge; 3 the ring at 90% of the cell width, orange and red flames standing on it, a dust cloud rising; 4 the flames sink, the dust spreads; 5 dust settling, a scorched ring; 6 faint dust.
Layout: one horizontal row of 6 equal cells, each 11 wide to 7 tall, image size 2112x224 (each cell 352x224); the ground line at 80% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `tristana_fx_w_ready.png`：W 刷新提示（她头顶），5 帧

击杀或满层引爆时火箭跳跃冷却刷新：头顶闪出一个小小的火箭形金光，往上一跳后散成火星。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, golden light (#FFFFFF, #FFF6C8, #FFD84A, #C8994E) and fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208).
Effect: a RESET CUE above a head, 5 frames: 1 a small bright golden spark; 2 a tiny golden rocket shape pointing up (a pointed body and a flame tail), glowing; 3 it jumps up a little, brighter; 4 it bursts into golden sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `tristana_fx_r_muzzle.png`：R 毁灭射击炮口爆风（她的炮口，朝右），6 帧

大招开炮：炮口喷出一大团白热火光，往右冲出一个火焰锥，炮口外一圈白色的冲击烟环，最后是大团翻滚的烟。格子的左边中间是炮口。约 30 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a HUGE MUZZLE BLAST to the RIGHT from the middle of the cell's LEFT edge, 6 frames: 1 a big white-hot flash at the left edge; 2 a wide cone of yellow and orange flame blasting right to 90% of the cell width, a white smoke ring round the muzzle; 3 the flame at its biggest with red edges, the smoke ring spreading; 4 the flame breaks up, thick grey smoke rolling; 5 the smoke drifting right; 6 faint smoke.
Layout: one horizontal row of 6 equal cells, each 5 wide to 4 tall, image size 1920x256 (each cell 320x256); the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `tristana_fx_r_ball.png`：R 毁灭射击的大炮弹（飞行），4 帧循环

大招打出去的大炮弹：比普攻大的铁弹，外面裹着一层白黄的亮光和火焰，后面拖着长长的火焰尾和烟（参考 R 的光环）。约 18 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an iron ball (#1A1A22, #34343F, #585866, #8A8A99) in bright fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) with smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a BIG BLAZING CANNONBALL flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a big round iron ball at 70% of the cell width wrapped in a bright white-yellow glow and orange flames; behind it a long tapering tail of flame and smoke to the left edge, flickering each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 1152x256 (each cell 384x256); the ball on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `tristana_fx_r_hit.png`：R 大炮弹命中（目标身上），6 帧

大炮弹砸中目标：一团大的白黄火光炸开，火星和碎片往右后方飞（目标被往后打飞）。约 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a BIG IMPACT, 6 frames: 1 a large white flash at the centre; 2 a burst of yellow and orange fire, sparks and debris flying out mostly to the right; 3 the burst at its biggest with red edges; 4 embers and dark smoke; 5 grey smoke; 6 faint smoke.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `tristana_fx_r_blast.png`：R 冲击波（地面，目标周围的人被击退），6 帧

大炮弹落点的冲击波：地上一圈扁椭圆的白色冲击环带着火焰往外扩，扬起尘土。约 40 格宽、26 格高，地面在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, white shock light and fire (#FFFFFF, #FFF6C8, #FFD84A, #FF9A1F, #F2561B, #B8260F, #5E1208) and dust (#E6E0D8, #B9B0A6, #857B72, #574F4A, #36302D).
Effect: a SHOCKWAVE on the ground, 6 frames: 1 a white flash at the lower middle; 2 a flat bright white ring (an ellipse twice as wide as tall) with orange fire on it spreading from the middle; 3 the ring at 90% of the cell width, dust thrown up at its edge; 4 the ring fades to orange, the dust rises; 5 dust settling; 6 faint dust.
Layout: one horizontal row of 6 equal cells, each 3 wide to 2 tall, image size 2304x256 (each cell 384x256); the ground line at 80% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `tristana_fx_r_stun.png`：R 眩晕的星星（头顶），4 帧循环

被大招击退后眩晕：头顶转圈的三颗金色小星星。约 16 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, golden stars (#FFFFFF, #FFF6C8, #FFD84A, #C8994E).
Effect: STUN STARS circling above a head, 4 frames, a seamless loop: three small golden four-pointed stars moving round a flat ellipse (twice as wide as tall), the star in front brighter and bigger, the ones behind smaller; they move a quarter of the way round each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `tristana_fx_bolt` | view_projectiles `league_tristana_bolt` | 12 × 8 |
| `tristana_fx_shot` | view_effects `league_tristana_shot`（她身上，不跟随） | 18 × 14 |
| `tristana_fx_e_shot` | view_effects `league_tristana_e_shot`（她身上，不跟随） | 14 × 14 |
| `tristana_fx_e_charge` | view_projectiles `league_tristana_e_charge` | 10 × 8 |
| `tristana_fx_e_bomb` | view_effects `league_tristana_e_bomb0`…`e_bomb3`（跟随，每 10 tick 播一次） | 12 × 12 |
| `tristana_fx_e_stack` | view_effects `league_tristana_e_stack`（跟随） | 10 × 10 |
| `tristana_fx_e_boom` | view_effects `league_tristana_e_boom`（大图，不跟随） | 50 × 40（半径 25000） |
| `tristana_fx_e_boom4` | view_effects `league_tristana_e_boom4`（大图，不跟随） | 60 × 48 |
| `tristana_fx_p_boom` | view_effects `league_tristana_p_boom`（不跟随） | 34 × 28（半径 20000） |
| `tristana_fx_hit` | view_effects `league_tristana_hit`（跟随） | 14 |
| `tristana_fx_q_cast` | view_effects `league_tristana_q_cast`（跟随） | 24 × 20 |
| `tristana_fx_q_rapid` | view_buffs `league_tristana_q_rapid` | 24 × 20 |
| `tristana_fx_w_land` | view_effects `league_tristana_w_land`（大图，不跟随，z −1） | 44 × 28（半径 22000） |
| `tristana_fx_w_ready` | view_effects `league_tristana_w_ready`（跟随） | 14 × 14 |
| `tristana_fx_r_muzzle` | view_effects `league_tristana_r_muzzle`（她身上，不跟随） | 30 × 24 |
| `tristana_fx_r_ball` | view_projectiles `league_tristana_r_ball` | 18 × 12 |
| `tristana_fx_r_hit` | view_effects `league_tristana_r_hit`（跟随） | 24 |
| `tristana_fx_r_blast` | view_effects `league_tristana_r_blast`（大图，不跟随） | 40 × 26（半径 20000） |
| `tristana_fx_r_stun` | view_effects `league_tristana_r_stun`（跟随） | 16 × 8 |

- 炸弹 `e_bomb` 的 4 行分成 `e_bomb0`–`e_bomb3` 四个标签，挂在目标胸口；每 10 tick 重播一次，所以每行 2 帧各 5 tick。
- 普攻炮弹、E 炸弹、R 大炮弹的出手点按动作条出手帧的炮口位置量，写进各自的 `y_offset`；三个炮口火光按同一帧的炮口放。
