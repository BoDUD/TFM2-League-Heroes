# 镕铁少女 芮尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和动作已定（`design/rell_idle.png`：左边骑着橄榄铁甲战马、平端金色骑枪的她，右边是下马后穿着马化成的铁甲的她；3/4 正面朝右）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），骑马时连骑枪 51 格宽、45 格高，下马时 33 格宽、40 格高；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/rell_size.png`：她两种形态的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/rell_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里芮尔自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**骑枪和裂阵是琥珀金色的光（白芯）**，**马的橄榄铁甲会变成飞来飞去的铁甲碎片**，**轰落是土黄色的尘土和土坑**，**极涌是蓝紫色的磁力场、带金色电弧**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住她。
> - **方向（重要，红色方不会镜像）**：裂阵那条线 `q_line` 画成朝右，**上下对称**（往左时会上下翻）。其余所有画面（打中、身上、脚下、地上、头顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `rell_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `rell_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「溃敌沉力」 | 骑枪突刺；打中英雄削减其护甲魔抗 | `a_hit` · `p_shred` |
| 技能 1 = Q「裂阵」+ E「全速冲锋」 | Q 沿直线刺出冲击波、晕眩、打破护盾；E 和队友加速，下一击爆炸 | `q_line` · `q_hit` · `q_stun` · `e_cast` · `e_ms` · `e_ready` · `e_boom` |
| 技能 2 = W「驭铁术」 | 轰落：跳起砸地、击飞、得护盾、下马作战；驾临：铁甲合回成马、冲锋撞飞 | `w_jump` · `w_crash` · `w_hit` · `w_shield` · `foot` · `w2_mount` · `w2_hit` |
| 大招「极涌」 | 把周围敌人猛拉到身边，2 秒内持续拖拽并造成伤害 | `r_cast` · `r_on` · `r_yank` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火星、尘土、冲击环、磁力光都没有黑描边，也不要用最深的颜色给形状描一圈边**（铁甲碎片例外：可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 琥珀金（骑枪、裂阵、冲击）：`#FFFFFF`、`#FFF4C2`、`#FFD966`、`#F5B21E`、`#D07A0E`、`#8A4A0A`；
  - 磁力紫（极涌、E 的爆炸）：`#FFFFFF`、`#DCE4FF`、`#9AA8FF`、`#6E5CE6`、`#45309E`、`#221650`；
  - 橄榄铁（铁甲碎片、盾）：`#F2E8B0`、`#CDBE7E`、`#969058`、`#625C39`、`#3A3522`；
  - 土黄（尘土、土坑、裂缝）：`#E6D9BE`、`#BFA882`、`#93805E`、`#685843`、`#43392E`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 25000，裂阵 42000 长，轰落砸地半径 24000，极涌半径 34000）。

### 1. `rell_fx_a_hit.png`：普攻命中（目标身上），4 帧

骑枪刺中：一小团琥珀金色的闪光和几颗火星（参考 BA_Tar_Flash、BA_Throw_Sparks）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a SMALL GOLDEN HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a gold flash 7 squares with a white core; 3 the flash 10 squares, 6 short gold sparks at mirrored places; 4 a few fading gold motes.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `rell_fx_p_shred.png`：被动 溃敌沉力：破甲印记（敌人头顶，循环），4 帧

被她的普攻和技能打中的敌人 5 秒内护甲和魔抗降低：敌人头顶一块小小的、裂开的橄榄铁甲片，裂缝里透出金光，一闪一闪（参考 P_Rocks、E_Metal_Scrap）。**左右对称**，要小。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive iron ramp (#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522) and an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a SMALL CRACKED ARMOUR PLATE floating over a unit, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a little olive iron shield plate 8 squares wide and 7 tall cracked down the middle, gold light glowing in the crack, the crack's glow pulsing (dim, bright, brightest, bright), two tiny gold motes at mirrored places.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `rell_fx_q_line.png`：Q 裂阵：直线冲击（一条线，朝目标），6 帧

裂阵：骑枪往前猛刺，一道琥珀金色的冲击波沿直线冲出去，前头是一个尖尖的白金色枪尖光，两边炸开金色碎光和火星，后面一缕淡淡的烟（参考 Q_Streak、Rell_Q_Shockwaves2、Q_Impact_Flare、Q_Trail_Smoke、Skin08_Q_StabPoint）。**上下对称**。这条线出现 0.4 秒后才打中：前 3 帧是一条淡淡的金色预警线（越来越亮），第 4 帧冲击打出去，后 2 帧消散。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a GOLDEN LANCE SHOCKWAVE along a line to the RIGHT, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): 1-3 a thin faint gold guide line the whole 42 squares, a little brighter each frame (frame 3 with a dim glow 4 squares tall); 4 the strike: a white-gold spear point of light 8 squares tall at the RIGHT end, a gold shockwave filling the line 8 squares tall with a white core, gold shards and sparks flying out above and below at mirrored places; 5 the shockwave breaking into gold fragments along the line; 6 fading motes and a thin smoke wisp.
Layout: one horizontal row of 6 equal 44:14 cells, image size 4224x224 (each cell 704x224, 16 px a square); the line through the middle row of every cell, from the LEFT edge to the RIGHT edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `rell_fx_q_hit.png`：Q 裂阵命中：打破护盾（目标身上），5 帧

裂阵打中：一个金白色的十字闪光炸开，像玻璃一样的金色护盾碎片往四周飞（打破护盾），几颗火星（参考 Q_Impact_Cross、Q_Hit_Flash_Spikes_yellow、Q_Spark_tar）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a SHIELD-SHATTERING IMPACT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a white-gold four-pointed cross flash 14 squares across; 3 the cross 18 squares, a ring of pale gold glass-like shield shards breaking outward at mirrored places; 4 the shards flying out and falling, gold sparks; 5 fading shards and motes.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `rell_fx_q_stun.png`：Q 晕眩（目标头顶，循环），4 帧

被晕住：头顶三颗金色小星星绕圈转。**左右对称**（每帧左右对称地摆放），要小。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: STUN STARS over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small white-gold four-pointed stars 3 squares each on a flat ellipse 12 squares wide and 4 tall, one in the middle front and two at mirrored places at the sides, brightening in turn.
Layout: one horizontal row of 4 equal 14:6 cells, image size 896x96 (each cell 224x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `rell_fx_e_cast.png`：E 全速冲锋：起手（她身上，跟随），5 帧

全速冲锋：她和马脚下一圈金色的磁力冲击向外扩，几道金色的速度光线从地面往上冲，几片小铁甲片和金色火星绕着她转一圈（参考 E_LeadingEdge_Ring、E_Clone_Sparkle、E_Metal_Scrap、E_Trail_Persist）。**左右对称**，中间身体位置留空（a rider on a horse 52 squares wide and 44 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A) and an olive iron ramp (#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522).
Effect: a SPEED SURGE round a mounted figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a rider on a horse 52 squares wide and 44 tall stands in the middle, not drawn): 1 a white-gold flash ring on the ground 20 wide and 5 tall under the middle; 2 the ring 40 wide with a bright rim, 4 thin gold speed streaks rising at mirrored places; 3 the ring 56 wide, the streaks 20 squares tall, 4 small olive iron scraps and gold sparks circling at mirrored places; 4 the ring fading, the scraps spinning out; 5 the last sparks.
Layout: one horizontal row of 5 equal 58:32 cells, image size 4640x512 (each cell 928x512, 16 px a square); centered across, the ground ring's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `rell_fx_e_ms.png`：E 全速冲锋：加速（她和队友脚下，循环），4 帧

加速中：脚下两侧扬起小股的金色尘风，几颗金色火星贴着地面往外甩（参考 E_Trail_Persist、R_Dash_DirtTrail）。**左右对称**（两边一样），淡一点，不要盖住人。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A) and an earth ramp (#E6D9BE, #BFA882, #93805E, #685843, #43392E).
Effect: a SPEED WIND at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse of faint gold wind 24 squares wide and 4 tall on the ground, at both ends small dust puffs curling outward and gold sparks skimming out at mirrored places, the puffs taking turns to swell; the middle 8 squares nearly empty.
Layout: one horizontal row of 4 equal 26:8 cells, image size 1664x128 (each cell 416x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `rell_fx_e_ready.png`：E 全速冲锋：下一击会爆炸（她头顶，循环），4 帧

下一次普攻或裂阵会爆炸：她头顶一个金色的磁力印记（一个小小的马蹄形磁铁符号，两端冒着蓝紫色的电火花），一闪一闪。**左右对称**，要小但亮。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A) and a magnetic violet ramp (#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650).
Effect: a MAGNET SIGIL floating over a unit, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small gold horseshoe magnet sign 9 squares wide and 9 tall, its two prongs pointing DOWN, a white core line along it, tiny blue-violet sparks crackling at both prong tips at mirrored places; pulsing dim, bright, brightest, bright.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `rell_fx_e_boom.png`：E 全速冲锋：爆炸（目标身上），5 帧

爆炸：目标身上一团金色的磁力爆炸，中间白芯，外面一圈蓝紫色的磁力冲击环，几片铁甲碎片和火星往外飞（参考 Q_Impact_Flare、Distort_Ring、E_Metal_Scrap）。**左右对称**。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A), a magnetic violet ramp (#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650) and an olive iron ramp (#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522).
Effect: a MAGNETIC BLAST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a gold burst 14 squares with a white core; 3 a blue-violet shock ring 22 squares across round the gold burst, olive iron scraps and gold sparks flying out at mirrored places; 4 the ring breaking up, the scraps falling; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `rell_fx_w_jump.png`：W 轰落：起跳（她身上，跟随），4 帧

轰落起跳：马蹄下炸开两团土黄色的尘土往两边扬，中间几道金色的光线往上冲，马身化成铁甲时冒出的金光碎片（参考 W_Dirt_Takeoff、W_Horse_Erode_Swipe、W_ArmorFlow）。**左右对称**，只画地上的尘土和往上的光。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#E6D9BE, #BFA882, #93805E, #685843, #43392E) and an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a TAKE-OFF BURST on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 10 squares wide on the ground; 2 two dust clouds blasting out to both sides 18 squares each, 3 gold light streaks shooting up 12 squares from the middle; 3 the dust 50 squares wide and rising, gold flecks floating up; 4 the dust settling and thinning.
Layout: one horizontal row of 4 equal 52:18 cells, image size 3328x288 (each cell 832x288, 16 px a square); centered across, the dust's base on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `rell_fx_w_crash.png`：W 轰落：砸地（落点地上，不跟随），6 帧

她披着铁甲砸到地上：地上砸出一个土坑，一圈金色的冲击波向外推开，地面裂开、裂缝里透出金光，尘土往两边炸，几块碎石飞起来（参考 Rell_W_Ground_Crater、W_Ground_Impact、W_GroundCracks_Glow、W_Burst、W_Smoke）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#E6D9BE, #BFA882, #93805E, #685843, #43392E) and an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a GROUND CRASH, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 12 squares wide on the ground; 2 a dark crater ellipse 20 wide and 6 tall, a bright gold shock ring 30 wide and 9 tall round it; 3 the ring 46 wide, gold-glowing cracks spreading out from the crater at mirrored places, dust blasting out at both sides, small rocks flying up; 4 the ring 50 wide and fading, the dust spreading; 5 the dust thinning, the cracks still glowing; 6 faint cracks and the crater.
Layout: one horizontal row of 6 equal 52:24 cells, image size 4992x384 (each cell 832x384, 16 px a square); centered across, the crater's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `rell_fx_w_hit.png`：W 轰落：击飞命中（目标身上），4 帧

被砸飞：目标身上一团金色冲击，脚下一小股尘土往上冲。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A) and an earth ramp (#E6D9BE, #BFA882, #93805E, #685843, #43392E).
Effect: a KNOCK-UP HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a gold burst 12 squares with a white core, a puff of dust shooting up from the bottom; 3 the burst 16 squares, 6 gold rays at mirrored places, the dust column rising; 4 fading motes and dust.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `rell_fx_w_shield.png`：W 轰落：护盾（她身上，循环），4 帧

轰落的护盾：她身体两侧各一片弯弯的金色铁盾光（像两片月牙形的盾），盾面有亮边，外面一层淡淡的金光（参考 W_Shield_Flair、W_template_Shield、W_Shield_Mult）。**左右对称**，中间身体位置留空（an upright figure 20 squares wide and 40 tall stands in the middle, not drawn），淡一点，不要盖住她。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A) and an olive iron ramp (#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522).
Effect: a PAIR OF CURVED GOLDEN SHIELD PLATES round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 20 squares wide and 40 tall stands in the middle, not drawn): one crescent shield of gold-lit iron 8 squares wide and 30 tall at each side of the figure, their hollow sides facing it, bright white-gold rims, a faint gold glow round them; the glow pulsing, a white glint sliding down both rims together.
Layout: one horizontal row of 4 equal square cells, image size 2688x672 (each cell 672x672, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `rell_fx_foot.png`：W 下马作战：铁甲光环（她身上，循环），4 帧

下马作战的状态：几片小小的橄榄铁甲碎片在她身边慢慢绕着漂，每片边上一点金光，偶尔一道蓝紫色的磁力小电弧把两片连起来（参考 W_ArmorFlow、E_Metal_Scrap、R_Metal_Scrap）。**左右对称**（碎片左右对称地摆放），中间身体位置留空（an upright figure 20 squares wide and 40 tall stands in the middle, not drawn），要淡，不要盖住她。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive iron ramp (#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522), an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A) and a magnetic violet ramp (#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650).
Effect: FLOATING IRON SCRAPS round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 20 squares wide and 40 tall stands in the middle, not drawn): 6 small olive iron scraps 2-3 squares each at mirrored places round the figure (2 at the shoulders, 2 at the hips, 2 at the knees), each with a gold glint, bobbing up and down 1 square in turn; in frames 2 and 4 a thin blue-violet magnetic arc joins the two shoulder scraps across the top.
Layout: one horizontal row of 4 equal 38:42 cells, image size 2432x672 (each cell 608x672, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `rell_fx_w2_mount.png`：W 驾临：铁甲合成马（她身上，跟随），5 帧

驾临：四周的铁甲碎片和金光往她身上飞回来、合成马，最后一道金色的光闪一下（参考 W_Mount_Whoosh、W_ArmorFlow、R_Metal_Scrap）。**左右对称**，中间位置留空（a rider on a horse 52 squares wide and 44 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive iron ramp (#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522) and an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: IRON SCRAPS GATHERING into a mount, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a rider on a horse 52 squares wide and 44 tall stands in the middle, not drawn): 1 8 olive iron scraps 3-4 squares each far out at mirrored places, gold trails behind them; 2 the scraps halfway in, gold whooshes curving in from both sides; 3 the scraps reaching the middle, a gold glow outline 50 wide and 40 tall; 4 a white-gold flash line across the middle, the outline brightest; 5 fading gold motes.
Layout: one horizontal row of 5 equal 58:42 cells, image size 4640x672 (each cell 928x672, 16 px a square); centered across, the bottom of the shape on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `rell_fx_w2_hit.png`：W 驾临：冲锋撞飞（目标身上），5 帧

上马冲锋撞中：目标身上一团金色冲击，一道金色的弧光从下往上翻（把人掀起来），几颗火星（参考 W_Flip_Swipe、Q_Impact_Flare）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a FLIPPING CHARGE HIT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a gold burst 12 squares with a white core; 3 two gold arcs sweeping UP from the bottom at both sides like a fountain, 20 squares tall; 4 the arcs at the top, gold sparks falling at mirrored places; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `rell_fx_r_cast.png`：R 极涌：爆发（她身上，跟随），6 帧

极涌：她身上爆出一大圈蓝紫色的磁力冲击波（地上扁椭圆 + 往上的半透明磁力穹顶），金色的电弧和铁甲碎片从四周往她身上吸（参考 R_glow_distort、R_RipplesEdge、R_TrampleAOE_Glow、R_Metal_Scrap、Distort_RGBA）。**左右对称**，中间位置留空（a rider on a horse 52 squares wide and 44 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magnetic violet ramp (#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650), an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A) and an olive iron ramp (#F2E8B0, #CDBE7E, #969058, #625C39, #3A3522).
Effect: a MAGNETIC BURST round a mounted figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a rider on a horse 52 squares wide and 44 tall stands in the middle, not drawn): 1 a white-violet flash 16 squares round the middle; 2 a blue-violet ring on the ground 40 wide and 12 tall with a bright lavender rim, a faint violet dome 36 tall over it; 3 the ring 72 wide and 22 tall, the dome's rim crackling with gold arcs at mirrored places, olive iron scraps far out; 4 the scraps streaking IN toward the middle with gold trails; 5 the ring pulsing, violet ripples; 6 the ring fading to its rim.
Layout: one horizontal row of 6 equal 74:46 cells, image size 7104x736 (each cell 1184x736, 16 px a square); centered across, the ground ring's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `rell_fx_r_on.png`：R 极涌：磁场（她脚下，2 秒循环），6 帧

极涌持续 2 秒，把周围的人往她身边拖：她脚下一大圈蓝紫色的磁力场在转，圈上几道金色电弧，圈里的地面有往中间收的蓝紫色波纹（参考 R_Wave_Texture、R_GroundDrag、R_Mark_distort）。**左右对称**，只画地上的圈和波纹。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magnetic violet ramp (#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650) and an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a SPINNING MAGNETIC FIELD on the ground, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat blue-violet ellipse ring 68 squares wide and 22 tall with a bright lavender rim, 3 ripple rings inside it shrinking toward the middle frame by frame (pulled in), 4 short gold electric arcs on the rim at mirrored places jumping between frames; the middle 20 squares empty.
Layout: one horizontal row of 6 equal 70:24 cells, image size 6720x384 (each cell 1120x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `rell_fx_r_yank.png`：R 极涌：被拉（敌人身上），4 帧

被猛地拉过去：敌人身上一圈蓝紫色的磁力光收紧，几道金色电弧缠在身上。**左右对称**，中间身体留空（一个 12 格宽、24 格高的人站在中间，不要画）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magnetic violet ramp (#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650) and an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a MAGNETIC GRIP round a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a figure 12 squares wide and 24 tall stands in the middle, not drawn): 1 a blue-violet glow outline 18 wide and 26 tall; 2 the outline tightening to 14 wide with a bright lavender rim, 2 gold arcs crossing the figure at mirrored places; 3 the arcs crackling; 4 the glow fading.
Layout: one horizontal row of 4 equal 20:28 cells, image size 1280x448 (each cell 320x448, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `rell_fx_r_hit.png`：R 极涌：持续伤害（敌人身上，每 0.25 秒），3 帧

每跳伤害：一小团蓝紫色的磁力火花加一点金光。**左右对称**，要小（会连续出现很多次）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, dust, smoke, rings or magnetic glow (iron scraps may have a dark edge), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magnetic violet ramp (#FFFFFF, #DCE4FF, #9AA8FF, #6E5CE6, #45309E, #221650) and an amber gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F5B21E, #D07A0E, #8A4A0A).
Effect: a TINY MAGNETIC SPARK on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a violet spark star 7 squares with a gold core; 3 4 fading violet motes.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `rell_fx_a_hit` | view_effects `league_rell_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `rell_fx_p_shred` | view_buffs `league_rell_p_shred`（跟随，画在人物上面；左右对称） | 10 × 8 |
| `rell_fx_q_line` | view_projectiles `league_rell_q_line`（裂阵那条线：朝目标方向转，画成朝右；上下对称；大图表） | 42 × 12 |
| `rell_fx_q_hit` | view_effects `league_rell_q_hit`（跟随，画在人物上面；左右对称） | 18 |
| `rell_fx_q_stun` | view_buffs `league_rell_q_stun`（跟随，画在人物上面；左右对称；W 驾临的晕眩也用这张） | 14 × 6 |
| `rell_fx_e_cast` | view_effects `league_rell_e_cast`（跟随，画在她身上；左右对称） | 56 × 30 |
| `rell_fx_e_ms` | view_buffs `league_rell_e_ms`（跟随，画在人物下面；左右对称） | 26 × 8 |
| `rell_fx_e_ready` | view_buffs `league_rell_e_ready`（跟随，画在她上面；左右对称） | 12 × 12 |
| `rell_fx_e_boom` | view_effects `league_rell_e_boom`（跟随，画在人物上面；左右对称） | 22 |
| `rell_fx_w_jump` | view_effects `league_rell_w_jump`（跟随，画在她身上；左右对称） | 50 × 16 |
| `rell_fx_w_crash` | view_effects `league_rell_w_crash`（不跟随，画在地上、人物下面；左右对称；大图表） | 50 × 22 |
| `rell_fx_w_hit` | view_effects `league_rell_w_hit`（跟随，画在人物上面；左右对称） | 16 |
| `rell_fx_w_shield` | view_buffs `league_rell_w_shield`（跟随，画在她身上；左右对称） | 40 × 40 |
| `rell_fx_foot` | view_buffs `league_rell_foot`（跟随，画在她身上；左右对称） | 36 × 40 |
| `rell_fx_w2_mount` | view_effects `league_rell_w2_mount`（跟随，画在她身上；左右对称） | 56 × 40 |
| `rell_fx_w2_hit` | view_effects `league_rell_w2_hit`（跟随，画在人物上面；左右对称） | 20 |
| `rell_fx_r_cast` | view_effects `league_rell_r_cast`（跟随，画在她身上、人物后面；左右对称；大图表） | 72 × 44 |
| `rell_fx_r_on` | view_buffs `league_rell_r_on`（跟随，画在她下面；左右对称；大图表） | 70 × 24 |
| `rell_fx_r_yank` | view_effects `league_rell_r_yank`（跟随，画在人物上面；左右对称） | 18 × 26 |
| `rell_fx_r_hit` | view_effects `league_rell_r_hit`（跟随，画在人物上面；左右对称） | 10 |

- 两张表：`asset/league/effects/league_rell_fx`（小的）和 `league_rell_big`（q_line、w_jump、w_crash、r_cast、r_on），tag = 名字（build_rell.py 的 views）。
- `q_line` 是投射物（LineRangeProjectile），画面朝方向转，第 4 帧（打中）要落在出现后约 0.38 秒；`w_crash` 不跟随、画在人物下面（z -1）；`r_on` 循环盖满 2 秒；`r_cast` 画在她后面（z -1）。
- 用 `pixel_1x/` 切格（import_pantheon_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
