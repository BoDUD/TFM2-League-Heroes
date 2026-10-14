# 正义巨像 加里奥：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已定（`design/galio_idle.png`：游戏里的 3/4 正面待机，金色翅膀高高竖起）。他在游戏里是**高清**的（PPU：每个游戏格子里 2×2 个细像素，这张图是高清造型放大 3 倍），1 倍图连翅膀 52 格高、43 格宽，**游戏里显示成 85%（约 36 × 44 格）**；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/galio_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/galio_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里加里奥自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**白青色的风、蓝色的禁魔石魔法光（护盾、被动冲击）、德玛西亚的金色光（大招、嘲讽徽记）、石头的尘土和碎石**。
> - **特效要亮**：每道光、每股风都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的护盾、光罩、冲击环只画外圈和两边，中间人形位置留空**，不然会把人整个挡住。
> - **方向（重要，红色方不会镜像）**：飞出去的风 `q_wind` 画成朝右，**上下对称**（往左放时会上下翻）。其余所有画面（打中、身上、脚下、头顶、地上的冲击环、龙卷风）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `galio_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `galio_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「巨像重击」 | 石拳；每几秒一次双拳砸地的范围魔法伤害；杜朗护盾被动的魔法护盾 | `a_hit` · `p_hit` · `p_ring` · `w_ps` |
| 技能 1 = Q「战争罡风」 | 扇出两道风，落地炸开并留下龙卷风 | `q_wind` · `q_burst` · `q_tornado` · `q_hit` |
| 技能 2 = E「正义冲拳」+ W「杜朗护盾」 | 冲锋击飞第一个英雄；蓄力护盾减伤，放开时嘲讽周围敌人 | `e_dash` · `e_hit` · `w_charge` · `w_burst` · `w_taunt` |
| 大招 = R「英雄登场」 | 给苦战的队友护盾，引导后飞过去，落地击飞敌人 | `r_cast` · `r_shield` · `r_land` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、风、魔法、冲击环、尘土都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 风：`#FFFFFF`、`#E8FBFF`、`#BDEFFF`、`#7FD6F2`、`#3FA9D6`；
  - 蓝色魔法光：`#FFFFFF`、`#D6ECFF`、`#8CC4FF`、`#4A8EF0`、`#2457C9`、`#142F80`；
  - 金色光：`#FFF8D6`、`#FFE27A`、`#F5BE3C`、`#C98A1E`、`#8A5A12`；
  - 尘土和碎石：`#F2EEE4`、`#D6CDBB`、`#B3A68E`、`#8A7D66`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，被动范围半径 16000，Q 落点半径 15000、龙卷风半径 13000，W 半径 26000，R 落地半径 22000）。

### 1. `galio_fx_a_hit.png`：普攻打中（目标身上），4 帧

石拳打中：目标身上白色冲击一闪，一圈淡淡的碎石尘往外弹（参考 BA_BlastShapes、P_ImpactPuffs）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: a STONE-FIST HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a pale cyan-white burst 10 squares across with a white core; 3 a ring of grey-beige dust puffs 12 squares across with 4 small pebbles flying out at mirrored places; 4 a few fading dust specks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `galio_fx_p_hit.png`：被动 巨像重击：砸中的目标（目标身上），5 帧

被动重击砸中：目标身上蓝色的魔法冲击炸开（白芯，蓝色光圈），几块碎石往外飞（参考 P_Nova_Ground、P_Pebbles）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: a BLUE MAGIC SLAM HIT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a blue magic burst 12 squares across, white core; 3 the burst 18 squares across with a bright blue rim, 4 pebbles flying out at mirrored places; 4 the rim breaking into blue sparks; 5 fading sparks and dust.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `galio_fx_p_ring.png`：被动 巨像重击：他身前地上的冲击波（地上，不跟随），5 帧

双拳砸地的冲击波：地上一圈蓝色的魔法冲击环往外扩（从斜上方看的扁椭圆），里面一圈尘土（参考 P_Ring_Shockwave）。**左右对称**。范围约 34 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: a GROUND SHOCK RING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash on the ground 8 squares wide; 2 a flat blue ring 20 squares wide and 7 tall, 2 squares thick, white inner edge; 3 the ring 30 wide and 10 tall with grey-beige dust puffs on its inner edge; 4 the ring 34 wide and 12 tall, thinning, dust rising a little; 5 a faint broken ring and dust.
Layout: one horizontal row of 5 equal 36:14 cells, image size 2880x224 (each cell 576x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `galio_fx_w_ps.png`：杜朗护盾 被动：魔法护盾一闪（他身上），5 帧

被动护盾生成：他周围一层蓝色的护盾光一闪（大椭圆的外圈，参考 W_ShieldRing、Wings_Glow），**中间人形位置留空**，几点白光在边上闪。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80).
Effect: a SHIELD SHIMMER round a big figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 34 squares wide and 40 tall): 1 a faint blue rim at the figure's sides; 2 the rim of an ellipse 40 squares wide and 46 tall, 1-2 squares thick, white highlights at the top; 3 the rim brightest, 4 white sparkles on it at mirrored places; 4 the rim fading from the bottom up; 5 a few fading sparkles.
Layout: one horizontal row of 5 equal 42:48 cells, image size 3360x768 (each cell 672x768, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `galio_fx_q_wind.png`：Q 战争罡风：飞出去的两道风（朝落点飞，循环），4 帧

翅膀扇出的两道风合在一起往前飞：两股白青色的风刃上下各一，前端尖、后面拖着风痕（参考 Q_Mis_Front、Q_Mis_Tail、Q_Mis_Dirt_Sides）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6).
Effect: TWIN WIND BLASTS flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): two curved white-cyan wind blades, one above and one below the middle line, 8 squares long, their points meeting at the front (right); behind them wispy wind streaks 6 squares long, flickering in turn.
Layout: one horizontal row of 4 equal 18:14 cells, image size 1152x224 (each cell 288x224, 16 px a square); the blades' tips 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `galio_fx_q_burst.png`：Q 风落地炸开（落点，不跟随），5 帧

风落地的一下：地上一圈白青色的风圈炸开（扁椭圆），往上冲起几股风，夹着一点尘土（参考 Q_Land_Nova、Q_BlastStreaks）。**左右对称**。地上圈约 30 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: a WIND BURST on the ground, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares; 2 a flat white-cyan wind ring 20 squares wide and 7 tall; 3 the ring 30 wide and 10 tall with 4 upward wind streaks 12 squares tall at mirrored places; 4 the streaks higher and thinner, a little dust at the ring; 5 fading wisps.
Layout: one horizontal row of 5 equal 32:24 cells, image size 2560x384 (each cell 512x384, 16 px a square); centered across, the ring's middle 5 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `galio_fx_q_tornado.png`：Q 龙卷风（落点，不跟随，持续 2 秒），8 帧

落点留下一个竖着的龙卷风，转 2 秒：下窄上宽的漏斗形，白青色的风一圈圈绕着，夹着几块碎石和尘土（参考 Q_Tar_Tornado_BurstWind、Q_Tornado_swirl）。**左右对称**（旋转靠一圈圈风带的亮暗交替往上移表现，每帧逐格左右对称）。第 1 帧刚升起，第 8 帧散开。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: an UPRIGHT TORNADO, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a funnel narrow at the bottom (8 squares) and wide at the top (26 squares), 36 squares tall, made of white-cyan wind bands; the bright bands move up one step each frame (the spin shown by light and dark bands, every frame mirrored); a few grey pebbles and dust specks at mirrored places; 1 the funnel half grown; 2-7 full; 8 breaking into wisps.
Layout: one horizontal row of 8 equal 28:38 cells, image size 3584x608 (each cell 448x608, 16 px a square); centered across, the funnel's tip on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `galio_fx_q_hit.png`：Q 风打中（目标身上），4 帧

风刃打中目标：白青色的风交叉一闪（一个 X 形的风痕），散成几缕风。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6).
Effect: a WIND SLASH HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 an X of two white-cyan wind slashes 12 squares across; 3 the X 14 squares across, curling wisps at its ends; 4 fading wisps.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `galio_fx_e_dash.png`：E 正义冲拳：冲锋时脚下（他身上，跟着他），4 帧

冲出去时脚下扬起的尘土和风：地面上一团扁扁的尘土往两边散，夹着白青色的风痕（参考 E_Dirt_Takeoff、E_Ground_Slide）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66) and a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6).
Effect: a DUST KICK-UP under a charging figure's feet, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat dust puff 14 squares wide and 4 tall; 2 the puff 24 wide and 7 tall, white-cyan wind streaks at both sides; 3 the dust 30 wide spreading out, 4 pebbles; 4 thinning dust.
Layout: one horizontal row of 4 equal 32:14 cells, image size 2048x224 (each cell 512x224, 16 px a square); centered across, the puff's middle 3 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `galio_fx_e_hit.png`：E 冲拳打中（被击飞的人身上），5 帧

冲拳打中、把人打飞：目标身上金白色的冲击一闪，一圈蓝色光环，往上冲起几道风（击飞，参考 E_Hit_Flash、E_Tar_BlastShapes、E_Tar_Complete）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF8D6, #FFE27A, #F5BE3C, #C98A1E, #8A5A12), a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80) and a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6).
Effect: a KNOCK-UP PUNCH HIT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 6 squares; 2 a gold star burst 12 squares across with a white core; 3 a blue ring 18 squares across round it and 4 white-cyan wind streaks shooting upward at mirrored places; 4 the streaks higher, the ring fading; 5 fading sparks.
Layout: one horizontal row of 5 equal 22:26 cells, image size 1760x416 (each cell 352x416, 16 px a square); centered across, the burst's middle 9 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `galio_fx_w_charge.png`：W 杜朗护盾：蓄力的护盾（他身上，跟着他），4 帧

蓄力时罩住他的蓝色护盾：一层蓝色光罩（只画外圈和几道光纹，**中间人形位置留空**），外圈上几点白光一闪，脚下一圈尘土（参考 W_ShieldRing、W_Cast_Dust、W_wisps）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: a BLUE SHIELD DOME round a big crouching figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 36 squares wide and 42 tall): 1 the dome's rim forming, an ellipse 44 squares wide and 50 tall, 1 square thick; 2 the rim 2 squares thick with white highlights at the top and sides, a ring of dust at its foot; 3 the rim brightest, 4 white sparkles moving up it at mirrored places; 4 the same, sparkles one step higher.
Layout: one horizontal row of 4 equal 46:52 cells, image size 2944x832 (each cell 736x832, 16 px a square); centered across, the dome's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `galio_fx_w_burst.png`：W 放开：嘲讽冲击波（他脚下，不跟随），5 帧

护盾一放，蓝色冲击波往四周扩开（地上一圈大的扁椭圆环），往上冒几道蓝白的光，碎石和尘土往外飞（参考 W_ShieldRing、W_rock_debris、W_Dust_Balls）。**左右对称**，中间人形位置留空。范围约 52 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: a BLUE SHOCKWAVE from a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle above the ring EMPTY (a clear upright area 30 squares wide and 20 tall): 1 a white flash ring at the feet 16 squares wide; 2 a blue ring 34 squares wide and 12 tall, 2 squares thick, with 4 blue-white light streaks rising at mirrored places; 3 the ring 52 wide and 18 tall, rocks and dust flying outward at mirrored places; 4 the ring breaking into blue sparks; 5 fading dust.
Layout: one horizontal row of 5 equal 56:28 cells, image size 4480x448 (each cell 896x448, 16 px a square); centered across, the ring's middle 6 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `galio_fx_r_cast.png`：R 英雄登场：引导（他身上，跟着他，约 2 秒），6 帧

准备飞向队友时的金色光：他周围金色的光点和光带往上升，脚下一圈金色光环（参考 R_Cas_Glow、R_Cas_Hover_Ringflare），**中间人形位置留空**。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF8D6, #FFE27A, #F5BE3C, #C98A1E, #8A5A12) and a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6).
Effect: a RISING GOLDEN LIGHT round a big figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 32 squares wide and 44 tall): a flat gold ring at the feet 36 squares wide and 10 tall; gold light streaks and motes rising along both sides at mirrored places, each frame one step higher; 1 the ring forming; 2-5 the ring bright, motes rising; 6 the ring and streaks brightest (the take-off).
Layout: one horizontal row of 6 equal 42:54 cells, image size 4032x864 (each cell 672x864, 16 px a square); centered across, the ring's middle 4 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `galio_fx_r_land.png`：R 落地砸地（落点，不跟随），6 帧

从天上砸下来的一下：地上金色和蓝色的大冲击环炸开，地面裂开几道发光的裂纹，尘土冲天（参考 R_Impact_Ground_Cracks、R_Tar_Impact、R_Ground_Indicator 的金色翅膀圈）。**左右对称**。范围约 46 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF8D6, #FFE27A, #F5BE3C, #C98A1E, #8A5A12), a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80) and a stone dust ramp (#F2EEE4, #D6CDBB, #B3A68E, #8A7D66).
Effect: a HEAVY LANDING on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 14 squares wide; 2 a flat gold ring 28 squares wide and 9 tall, a blue inner ring; 3 the rings 46 wide and 14 tall, glowing gold cracks radiating from the middle, dust clumps rising 14 squares at mirrored places; 4 the dust higher, the rings thinning; 5 cracks glowing dimmer, dust settling; 6 faint cracks.
Layout: one horizontal row of 6 equal 48:32 cells, image size 4608x512 (each cell 768x512, 16 px a square); centered across, the rings' middle 7 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `galio_fx_r_hit.png`：R 击飞（被打中的人身上），4 帧

被落地冲击击飞：目标身上金色的冲击一闪，几道光往上冲（参考 R__Tar_Stylized_Hit、R_centerFlare）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF8D6, #FFE27A, #F5BE3C, #C98A1E, #8A5A12) and a wind ramp (#FFFFFF, #E8FBFF, #BDEFFF, #7FD6F2, #3FA9D6).
Effect: a GOLDEN UPWARD HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 6 squares; 2 a gold star 12 squares across; 3 3 gold streaks shooting upward at mirrored places, the star fading; 4 fading motes.
Layout: one horizontal row of 4 equal 18:24 cells, image size 1152x384 (each cell 288x384, 16 px a square); centered across, the star's middle 8 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `galio_fx_w_taunt.png`：W 嘲讽（被嘲讽的人头顶，循环），4 帧

被嘲讽的人头顶：一个小小的金色德玛西亚翅膀徽记（两只展开的小翅膀中间一个盾形，参考 R_Ground_Indicator 的翅膀图案），一闪一闪。**左右对称**。画在格子上部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF8D6, #FFE27A, #F5BE3C, #C98A1E, #8A5A12).
Effect: a GOLD WINGED SIGIL over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two small spread wings 4 squares each round a small shield shape 4 squares wide, 12 squares wide in all, pulsing brighter and dimmer, two white sparkles.
Layout: one horizontal row of 4 equal 14:48 cells, image size 896x768 (each cell 224x768, 16 px a square); the sigil's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `galio_fx_r_shield.png`：R 给队友的护盾（队友身上，循环），4 帧

英雄登场给队友的护盾：一层蓝金色的护盾光罩罩住队友（普通英雄大小，只画外圈，**中间人形位置留空**），外圈上金色光点慢慢转（亮暗交替）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, wind, magic, rings or dust, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue magic ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8EF0, #2457C9, #142F80) and a gold ramp (#FFF8D6, #FFE27A, #F5BE3C, #C98A1E, #8A5A12).
Effect: a SHIELD BUBBLE round a normal-size figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 16 squares wide and 24 tall): the rim of an ellipse 22 squares wide and 30 tall, 1 square thick, blue with white highlights at the top, 4 small gold motes on it at mirrored places taking turns to brighten.
Layout: one horizontal row of 4 equal 24:32 cells, image size 1536x512 (each cell 384x512, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `galio_fx_a_hit` | view_effects `league_galio_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `galio_fx_p_hit` | view_effects `league_galio_p_hit`（跟随，画在人物上面；左右对称） | 18 |
| `galio_fx_p_ring` | view_effects `league_galio_p_ring`（不跟随，画在人物下面；左右对称） | 34 × 12 |
| `galio_fx_w_ps` | view_effects `league_galio_w_ps`（跟随，画在人物上面；左右对称） | 40 × 46 |
| `galio_fx_q_wind` | view_projectiles `league_galio_q_wind`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 12 |
| `galio_fx_q_burst` | view_effects `league_galio_q_burst`（不跟随，画在人物上面；左右对称） | 30 × 22 |
| `galio_fx_q_tornado` | view_effects `league_galio_q_tornado`（不跟随，画在人物上面；左右对称；8 帧铺满 2 秒） | 26 × 36 |
| `galio_fx_q_hit` | view_effects `league_galio_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `galio_fx_e_dash` | view_effects `league_galio_e_dash`（跟随，画在人物下面；左右对称） | 30 × 12 |
| `galio_fx_e_hit` | view_effects `league_galio_e_hit`（跟随，画在人物上面；左右对称） | 20 |
| `galio_fx_w_charge` | view_effects `league_galio_w_charge`（跟随，画在人物上面；左右对称；蓄力约 0.8 秒） | 44 × 50 |
| `galio_fx_w_burst` | view_effects `league_galio_w_burst`（不跟随，画在人物上面；左右对称） | 52 × 26 |
| `galio_fx_r_cast` | view_effects `league_galio_r_cast`（跟随，画在人物上面；左右对称；6 帧铺满引导时间） | 40 × 52 |
| `galio_fx_r_land` | view_effects `league_galio_r_land`（不跟随，画在人物下面；左右对称） | 46 × 30 |
| `galio_fx_r_hit` | view_effects `league_galio_r_hit`（跟随，画在人物上面；左右对称） | 16 |
| `galio_fx_w_taunt` | view_buffs `league_galio_w_taunt`（跟随，画在人物上面；左右对称） | 12 × 8 |
| `galio_fx_r_shield` | view_buffs `league_galio_r_shield`（跟随，画在人物上面；左右对称） | 22 × 30 |

- 两张表：`asset/league/effects/league_galio_fx`（小的）和 `league_galio_big`（p_ring、q_burst、q_tornado、w_charge、w_burst、r_land），tag = 名字（build_galio.py 的 views）。
- `q_wind` 是投射物（抛物线），画面朝飞行方向转；`p_ring`、`q_burst`、`q_tornado`、`w_burst`、`r_land` 不跟随；`w_taunt` 头顶（z 3）；`w_charge`、`w_ps`、`r_cast`、`r_shield` 中间必须是空的；`q_tornado` 8 帧铺满 2 秒，`r_cast` 6 帧铺满 2 秒，`w_charge` 循环到蓄力结束。
- 用 `pixel_1x/` 切格（import_kassadin / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
