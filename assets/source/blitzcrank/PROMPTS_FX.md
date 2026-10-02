# 蒸汽机器人 布里茨：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图。** 造型已定（`design/blitzcrank_design.png`，8 倍），动作条已经画好；这一轮只画特效。
> - 大小对照 `design/blitzcrank_size.png`：定稿造型放大 4 倍，站在红色脚底线上，上面是 10 格一段的刻度，右边是原版骑士。布里茨 46×44 格（烟囱顶到鞋底 44 格），原版英雄约 35 格高。每条写的大小都是游戏像素（格）。
> - **请直接按游戏尺寸画**（1 个图片像素 = 1 个游戏像素），每张一个原尺寸条 `logical/blitzcrank_fx_<名字>_1x.png`，再附一张 8 倍预览；和菲兹那次一样。附 `manifest.json`：每帧在原尺寸条里的区域 `assets[].frames[].rect_1x` = [x, y, 宽, 高]。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里布里茨自己的特效贴图，按用在我们哪张特效分好了行，只在本地用，不要提交。
> - W 的蒸汽、R 的蓄电和被动护盾挂在他身上：`design/steam_guide.png` 是那个格子（48×56，8 倍）里淡淡的造型、站位点（蓝十字）和两根烟囱口（红圈，格子里 (15, 15) 和 (31, 17)）。
> - 交回时附 `HANDOFF.md`（每张画了几帧、有没有没做到的地方）。最好打成一个 zip（`blitzcrank_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + R 的被动 | 铁拳；大招没在冷却时，被打的目标挂上静电，1 秒后头顶劈下一道闪电 | `hit` · `p_mark` · `p_bolt` |
| 被动「法力屏障」 | 被围攻或被控制时套上金色能量罩（护盾在时一直循环） | `mb_on` |
| 技能 1 = Q「机械飞爪」 | 右手带着钢缆飞出去，抓住第一个敌方英雄拉回来 | `q_parts`（Claude 拼成飞出/收回的画面）· `q_grab` |
| 技能 2 = E「能量铁拳」+ W「过载运转」 | 上勾拳把人打飞；敌方英雄靠近时自动过载：两根烟囱喷蒸汽 | `e_hit` · `w_steam` |
| 大招 = R「静电力场」 | 浑身冒电，然后地上一圈电光炸开，电到周围敌人并沉默英雄 | `r_charge` · `r_field` · `r_hit` · `r_silence` |

## 所有特效图的规则

- 像素画：一个像素就是一格，硬边、没有抗锯齿、没有模糊和柔光，透明度只有 0 和 255。**没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。飞出去的手是例外：它是「东西」，可以用造型图的 1 格深色描边。
- 颜色（按每条写的用）：
  - 电（静电、闪电、电圈）：`#FFFFFF`、`#E6F6FF`、`#9ED8FF`、`#4FA0FF`、`#3A5CE0`、`#2A2A9A`；
  - 火星和冲击（铁拳、抓取、护盾）：`#FFFFFF`、`#FFF2B0`、`#FFD24A`、`#F9AF07`、`#DD8702`、`#984B01`；
  - 蒸汽：`#FFFFFF`、`#E8ECF0`、`#C8D0D8`、`#9AA4B0`、`#6E7884`；
  - 沉默：`#FFFFFF`、`#F0E0FF`、`#C8A0FF`、`#9A60F0`、`#6A30C0`；
  - 飞出去的手：造型图拳头的金色和钢色。
- 命中和范围特效居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 2 倍）。
- 挂在身上的特效（静电标记、蒸汽、蓄电、护盾、沉默）：不要画人，**不能挡住脸和胸口炉门**。
- 不要网格线、边框、文字、编号。

---

## 特效（12 张）

### 1. `blitzcrank_fx_hit`：普攻命中，5 帧

铁拳打中目标：中心一团白黄的冲击闪光，四周迸出几颗橙色火星和一两片钢屑（参考 Q_Impact、Z_hiteffect）。约 16 格。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a spark ramp (#FFFFFF, #FFF2B0, #FFD24A, #F9AF07, #DD8702, #984B01) with steel #BFCDE0, #67718F.
Effect: a HEAVY PUNCH HIT, 5 frames: 1 a small white flash at the center; 2 a white-yellow four-pointed impact star; 3 the star at full size (about 14 px) with 5-6 orange sparks and two tiny steel chips flying outward; 4 the star breaks up, sparks flying further; 5 a few fading orange sparks.
Layout: one row of 5 cells of 16x16 px (strip 80x16); centered in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 2. `blitzcrank_fx_p_mark`：静电标记（被普攻的目标身上，1 秒），6 帧

大招被动：普攻打中的目标身上挂着一团静电，几道蓝白的小电弧在一个点周围噼啪跳动（参考 W_Lightn、Z_zapspark）。约 18 格，中心留空看得见身体。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a zap ramp (#FFFFFF, #E6F6FF, #9ED8FF, #4FA0FF, #3A5CE0, #2A2A9A).
Effect: a STATIC CHARGE crackling on a target, 6 frames (1 s, the next frame always different): 3-4 small jagged blue-white electric arcs (each 4-7 px, one pixel thick, a white core with blue ends) jumping round a center point at different angles each frame, 2-3 tiny blue sparks; the very center stays empty.
Layout: one row of 6 cells of 18x18 px (strip 108x18); centered in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 3. `blitzcrank_fx_p_bolt`：静电雷击（1 秒后落在目标身上），6 帧

1 秒后从目标头顶上方劈下一道闪电：一道折线的白蓝闪电从格子顶部劈到目标胸口，落点炸开一团电光和火星，然后很快消失（参考 R_Lightn、Z_runeWars_lightning、Z_lightningbolt）。宽 20 格、高 44 格，落点在格子下部（离底 12 格）。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a zap ramp (#FFFFFF, #E6F6FF, #9ED8FF, #4FA0FF, #3A5CE0, #2A2A9A).
Effect: a LIGHTNING BOLT STRIKING a target from above, 6 frames: 1 a thin flicker at the top; 2 a jagged white-and-blue bolt (2 px thick, white core, blue edges, 4-6 sharp bends) from the top of the cell down to the strike point 12 px above the bottom; 3 the bolt at full brightness and a round blue-white burst (about 12 px) at the strike point; 4 the bolt breaks into 3-4 pieces, the burst with small arcs; 5 the burst fades to a few sparks; 6 two blue sparks.
Layout: one row of 6 cells of 20x44 px (strip 120x44); the strike point at x=10, y=31 in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 4. `blitzcrank_fx_q_parts`：Q 机械飞爪的零件（飞出去的手 + 链条），静态

Q 飞出去的是他的右手：一只握拳的金色方块大手（和造型图的拳头一样：三块方块手指、钢色指节螺栓，腕口是深色六角形），**拳头朝右**，腕后喷一小股白色蒸汽（2 帧闪动）；再画一段**钢缆链条**（12 格长、3 格粗，左右能无缝接上，钢色带深色箍，参考 Z_cable）。我用它们按每 2 tick 一帧拼出飞出去时越来越长、拉回来时越来越短的链条。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from the design's gold #FDDC36, #F9AF07, #DD8702, #BC6802, #984B01, #672D01, steel #E2EBFC, #BFCDE0, #A2AECC, #67718F, #454759, #373E56 and its outline #170F1D, the steam ramp (#FFFFFF, #E8ECF0, #C8D0D8, #9AA4B0, #6E7884).
Effect: THE ROCKET HAND and its CABLE, as separate pieces: (a) 2 frames of the flying hand: a clenched blocky gold fist pointing to the RIGHT (three square gold finger blocks, two or three steel knuckle bolts, a dark hexagonal wrist socket at its left end), 11 px wide and 10 px tall, with a small white steam puff behind the wrist that flickers between the two frames; this object may have the design's 1-px dark outline #170F1D; (b) one horizontal tile of steel CABLE, 12 px long and 3 px thick (a light top line, a mid line, a dark bottom line, with two dark bands), whose left and right ends join seamlessly when repeated.
Layout: (a) a strip of 2 cells of 16x12 px (32x12), the fist centered with its wrist at x=3; (b) the cable tile alone, 12x3 px. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 5. `blitzcrank_fx_q_grab`：Q 钩中英雄，5 帧

手抓住英雄的一瞬：白色闪光，一圈黄色火星向外炸开，加两三道蓝白电弧（参考 Q_Impact 星形）。约 22 格，中心留空。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a spark ramp (#FFFFFF, #FFF2B0, #FFD24A, #F9AF07, #DD8702, #984B01) with the zap ramp (#FFFFFF, #E6F6FF, #9ED8FF, #4FA0FF, #3A5CE0, #2A2A9A).
Effect: a GRAB IMPACT on a target, 5 frames: 1 a white flash ring at the center; 2 a ring of 8 yellow-orange spark rays bursting outward and two blue-white arcs; 3 the rays at full length (about 20 px across), the center clear; 4 the rays break into sparks; 5 a few fading sparks.
Layout: one row of 5 cells of 22x22 px (strip 110x22); centered in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 6. `blitzcrank_fx_e_hit`：E 能量铁拳的上勾拳命中（击飞），6 帧

上勾拳打中：目标胸口一团白黄冲击光，然后一道向上的冲击气流（几条往上的白色速度线和火星），表示把人打飞（参考 Q_ConeTe、Z_overdrivelines）。宽 24 格、高 40 格，冲击点离底 14 格。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a spark ramp (#FFFFFF, #FFF2B0, #FFD24A, #F9AF07, #DD8702, #984B01) with white speed lines.
Effect: an UPPERCUT HIT that launches the target, 6 frames: 1 a white flash at the impact point; 2 a big white-yellow impact star (about 16 px) at the impact point; 3 the star with an upward burst: 4-5 white speed lines and orange sparks shooting straight up from it toward the top of the cell; 4 the star fades, the lines at full height; 5 the lines thin and break into sparks near the top; 6 a few sparks.
Layout: one row of 6 cells of 24x40 px (strip 144x40); the impact point at x=12, y=26 in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 7. `blitzcrank_fx_w_steam`：W 过载运转：两根烟囱冒蒸汽（1 秒，挂在他身上），6 帧

过载时两根烟囱往上喷白色蒸汽（每秒放一次，共 4 秒）：从两根烟囱口（`design/steam_guide.png` 里标的两个点）各冒出一股往上翻滚的白烟，越往上越大越淡，偶尔夹一两道黄色小电弧（参考 W_Lightn、Z_overdrivelines）。**只画蒸汽，不画人**；格子大小和站位点照 steam_guide。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from the steam ramp (#FFFFFF, #E8ECF0, #C8D0D8, #9AA4B0, #6E7884) with two yellow sparks #FFF2B0, #FFD24A.
Effect: STEAM PUFFING from two smokestacks, 6 frames (1 s), drawn on the 48x56 cell of the guide where the two stack openings are marked (do NOT draw the robot): 1 a small white puff appears at each opening; 2 the puffs grow and rise as round rolling clouds; 3 a second puff follows from each opening while the first rises higher and spreads; 4 the upper clouds thin to grey; 5 they break into wisps near the top of the cell, small new puffs at the openings; 6 faint wisps. One or two tiny yellow electric arcs flicker near the openings in frames 2-4.
Layout: one row of 6 cells of 48x56 px (strip 288x56); the robot's standing point at x=24, y=47 in every cell, the openings where steam_guide.png marks them. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 8. `blitzcrank_fx_r_charge`：R 静电力场：蓄电（身上电弧，0.4 秒），5 帧

放大招前浑身噼啪冒电：蓝白电弧在他身体轮廓上乱窜，越来越密（参考 R_ChainE、R_Elec、Z_zapball）。格子和站位点同 W 的蒸汽格（站位点 x=30, y=47），只画电弧，不画人，电弧沿着身体外缘走，不盖住脸和胸口炉门。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a zap ramp (#FFFFFF, #E6F6FF, #9ED8FF, #4FA0FF, #3A5CE0, #2A2A9A).
Effect: ELECTRICITY BUILDING UP over a big robot's body (do NOT draw the robot; it stands on the standing point, about 46 px wide and 44 px tall), 5 frames: 1 two small blue arcs on the outline of the body; 2 four arcs crawling along the outline and the arms; 3 six arcs, brighter, a few white sparks; 4 arcs all round the outline, white-hot; 5 the arcs pull in toward the body. Keep the middle of the body (the face and the chest) clear.
Layout: one row of 5 cells of 60x56 px (strip 300x56); the standing point at x=30, y=47 in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 9. `blitzcrank_fx_r_field`：R 静电力场：爆发（地面大圈，大图），7 帧

静电向四周炸开：地上一个蓝紫色的电光椭圆环从他脚下扩散到最大（宽 128 格、高 64 格），环上和环内有一道道向外劈的白蓝闪电，第一帧中心白光一闪，最后电环散成火星消失（参考 R_Circle、R_Shockwave、R_Lightn）。椭圆中心在他脚下（格子中间、离底 36 格）。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a zap ramp (#FFFFFF, #E6F6FF, #9ED8FF, #4FA0FF, #3A5CE0, #2A2A9A).
Effect: a STATIC FIELD DISCHARGE on the ground around a unit (do NOT draw the unit), 7 frames: 1 a white flash at the center and a small ellipse ring; 2 the ring (a flat ellipse twice as wide as tall, 2-3 px thick, blue-violet with a white inner edge) expands to half size with 6-8 jagged white-blue lightning bolts shooting outward from the center to the ring; 3 the ring at full size (128 px wide, 64 px tall), bolts touching it, sparks along it; 4 the bolts fade, the ring flickers; 5 the ring breaks into dashed arcs; 6 the arcs into sparks; 7 a few fading sparks on the ellipse.
Layout: one row of 7 cells of 132x72 px (strip 924x72); the ellipse's center at x=66, y=36 in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 10. `blitzcrank_fx_r_hit`：R 电到每个敌人，5 帧

大招电中敌人：一团蓝白的电光在目标身上炸开，几道小电弧（参考 Z_zapspark、R_Impact）。约 18 格，中心留空看得见身体。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a zap ramp (#FFFFFF, #E6F6FF, #9ED8FF, #4FA0FF, #3A5CE0, #2A2A9A).
Effect: an ELECTRIC HIT on a target, 5 frames: 1 a white flash; 2 a blue-white zap burst (a ring of 5-6 short jagged arcs round the center, about 16 px); 3 the arcs at full length, a few sparks; 4 the arcs break; 5 two blue sparks.
Layout: one row of 5 cells of 18x18 px (strip 90x18); centered in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 11. `blitzcrank_fx_r_silence`：R 沉默（敌人头顶，1 秒），6 帧

被沉默：头顶上一个紫色的小电圈（横着的椭圆），上面有一道斜杠的「禁止」符号，噼啪闪（表示不能放技能）。宽 22 格、高 12 格，在头顶上方，不盖住脸。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a silence ramp (#FFFFFF, #F0E0FF, #C8A0FF, #9A60F0, #6A30C0).
Effect: a SILENCE MARK hovering over a head, 6 frames (1 s): a small flat violet electric ring (an ellipse 18 px wide, 6 px tall) crackling with tiny sparks, and inside it a small violet 'forbidden' sign (a circle with a slash, about 7 px) that pulses brighter and dimmer across the frames.
Layout: one row of 6 cells of 22x12 px (strip 132x12); centered in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

### 12. `blitzcrank_fx_mb_on`：被动 法力屏障：护盾（护盾在时循环），6 帧

被动护盾：围着他的一圈金色能量罩（参考 Z_steamgolemshield 的金色火边和 Z_shieldgrid 的竖线）：只画罩子的边缘（一圈 1–2 格的金白色亮边，边上几格六角形的格纹闪动），**中间留空**，不盖住身体和脸。格子和站位点同 R 蓄电格。

```text
Pixel art game VFX sprite strip for a small tactics game, drawn at GAME SIZE (one image pixel = one game pixel): chunky single pixels, hard edges, no anti-aliasing, NO outline, colours only from a spark ramp (#FFFFFF, #FFF2B0, #FFD24A, #F9AF07, #DD8702, #984B01) with white.
Effect: a GOLDEN ENERGY SHIELD round a big robot (do NOT draw the robot; it stands on the standing point, about 46 px wide and 44 px tall), 6 frames, a seamless loop: the outline of a dome-shaped bubble round him (about 56 px wide and 52 px tall, its bottom on the standing point's ground line), 1-2 px thick, golden with white highlights, a few small hexagon cells shimmering along its edge, the shimmer moving round the bubble from frame to frame. The inside of the bubble stays EMPTY (fully transparent).
Layout: one row of 6 cells of 60x56 px (strip 360x56); the standing point at x=30, y=47 in every cell. Transparent background, binary alpha (0 or 255). No gaps, no borders, no labels. Also an 8x preview of the same strip (nearest neighbour).
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `blitzcrank_fx_hit` | view_effects `league_blitzcrank_hit`（跟随，胸口） | 16 |
| `blitzcrank_fx_p_mark` | view_effects `league_blitzcrank_p_mark`（跟随，胸口） | 18 |
| `blitzcrank_fx_p_bolt` | view_effects `league_blitzcrank_p_bolt`（跟随，脚下为底） | 20 × 44 |
| `blitzcrank_fx_q_parts` | Claude 拼成 `league_blitzcrank_q_hand`（飞出，链条越来越长）和 `q_back`（收回，链条越来越短）两个投射物画面 | 手 11 × 10，链条 12 × 3 |
| `blitzcrank_fx_q_grab` | view_effects `league_blitzcrank_q_grab`（跟随，胸口） | 22 |
| `blitzcrank_fx_e_hit` | view_effects `league_blitzcrank_e_hit`（跟随，脚下为底） | 24 × 40 |
| `blitzcrank_fx_w_steam` | view_effects `league_blitzcrank_w_steam`（施法者，跟随，画在人物上面） | 48 × 56 |
| `blitzcrank_fx_r_charge` | view_effects `league_blitzcrank_r_charge`（施法者，跟随，画在人物上面） | 60 × 56 |
| `blitzcrank_fx_r_field` | view_effects `league_blitzcrank_r_field`（施法者，跟随，画在人物下面；大图 league_blitzcrank_big） | 132 × 72（半径 40000） |
| `blitzcrank_fx_r_hit` | view_effects `league_blitzcrank_r_hit`（跟随，胸口） | 18 |
| `blitzcrank_fx_r_silence` | view_effects `league_blitzcrank_r_silence`（跟随，头顶上方） | 22 × 12 |
| `blitzcrank_fx_mb_on` | view_buffs `league_blitzcrank_mb_on`（护盾在时一直循环） | 60 × 56 |

- `q_parts` 拼成两个投射物画面：`q_hand`（每 2 tick 一帧，链条每帧长 12 格 = 钩子 6000/tick，手在画面中心朝右，链条往左拖回起点，`repeat: false`，最后一帧留得比最长飞行久）和 `q_back`（收回：手在中心朝左，链条往右通向布里茨，按收回速度每帧变短；拉人慢收 1500/tick 和落空快收 4500/tick 各一份）。
- R 的地面大圈按半径 40000（加上双方体积约 60000）定大小；蓄电、蒸汽、护盾按站位点对到他身上。
