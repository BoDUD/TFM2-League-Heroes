# 牛头酋长 阿利斯塔：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/alistar_design.png`，8 倍，44 行）。
> - 大小对照 `design/alistar_size.png`：定稿造型放大 4 倍，蹄底在红线上，上面是 10 格一段的刻度，右边是原版食人魔。阿利斯塔 41×44 格。每条写的大小都是游戏像素（格）。
> - `design/alistar_shots.png`：Q 砸地、W 头槌、W 冲锋、待机、R 怒吼的定稿动作（4 倍），青色十字是特效的起点（脚下、角尖、头顶），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿利斯塔自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**Q 砸地和 E 践踏是土黄色的尘土、棕色的碎石和白色发光的地裂纹；拳头、头槌是白金色的闪光；E 攒满是发光的铁链图标；R 是白色冲击环加橙红色的怒气光；被动是绿色的治疗光**。
> - **特效要亮**：每个形状都要用最亮的几档和白色或浅色的芯，暗底上一眼能看见；尘土也要有浅色的亮面，不能糊成一块棕色。
> - **套在人身上的光环（R 的怒气）只画人轮廓外面一圈和脚下，中间留空**，不然会把人整个挡住（游戏里画在人物上面）。
> - 特效照下面第 1–15 条和「所有特效图的规则」画，每张一个 PNG，文件名 `alistar_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`alistar_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 双拳重击 | `alistar_fx_a_hit` |
| 被动「凯旋怒吼」 | 控制命中敌方英雄 3 次后怒吼，治疗自己和身边队友 | `alistar_fx_p_roar` · `alistar_fx_p_heal` |
| 技能 1 = E「践踏」接 Q「大地粉碎」 | 先践踏 3 秒（每 0.5 秒一脚），再双拳砸地，击飞周围敌人；踩中英雄 5 次后下一拳眩晕 | `alistar_fx_e_stomp` · `alistar_fx_e_hit` · `alistar_fx_q_slam` · `alistar_fx_q_up` · `alistar_fx_e_ready` · `alistar_fx_e_hit_stun` · `alistar_fx_e_stun` |
| 技能 2 = W「野蛮冲撞」接 Q | 冲向敌方英雄，头槌撞退，落地再砸地击飞 | `alistar_fx_w_dash` · `alistar_fx_w_butt` · `alistar_fx_w_hit` · `alistar_fx_q_slam`（同一张） · `alistar_fx_q_up` |
| 大招 = R「坚定意志」 | 交战时怒吼，免疫控制，7 秒内减伤 | `alistar_fx_r_cast` · `alistar_fx_r_on` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**尘土、光、裂纹、冲击环、速度线没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的物体（碎石、铁链）有 1 格深色描边（`#140A20`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 尘土：`#FFF4DC`、`#EAD2A2`、`#C8A46E`、`#9A7448`、`#6A4A2C`；
  - 碎石：`#F0D4A0`、`#C08E58`、`#8A5E34`、`#563820`；
  - 地裂纹：`#FFFFFF`、`#F2EEFF`、`#CCC6E8`；
  - 白金闪光：`#FFFFFF`、`#FFF6C8`、`#FFD870`、`#FFA830`、`#E06A10`；
  - R 的怒气：`#FFFFFF`、`#FFE0A0`、`#FF9A40`、`#F04A20`、`#B01E18`；
  - 治疗绿光：`#FFFFFF`、`#D8FFD0`、`#8CF078`、`#3CC850`、`#1A8A3A`；
  - 眩晕星星、铁链的光：`#FFFFFF`、`#FFF4A0`、`#FFD23C`、`#E89A10`；
  - 铁链：`#C8C4CC`、`#8A848E`、`#4A4652`、`#2A2730`；
- **从角尖发出的特效朝右画，起点在格子左边的中点**（`w_butt`）；W 冲锋的尘土在人后面（左边）；画在他身上或脚下的画面（`q_slam`、`e_stomp`、`p_roar`、`r_cast`、`r_on`）按每条写的站位画。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（`e_stun`、`r_on`）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：砸地半径 28000、践踏半径 24000、怒吼治疗半径 40000）。

### 1. `alistar_fx_a_hit.png`：普攻打中（目标身上），4 帧

双拳砸中：一下白金色的闪光，周围喷出一小团土黄色的尘土（参考 hiteffect、E_Flash、E_DustCloud）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a flash ramp (#FFFFFF, #FFF6C8, #FFD870, #FFA830, #E06A10) and a dust ramp (#FFF4DC, #EAD2A2, #C8A46E, #9A7448, #6A4A2C).
Effect: a HEAVY PUNCH HIT, 4 frames: 1 a white flash with a gold rim; 2 a four-pointed white-gold star 12 squares across, a ring of tan dust puffs round it; 3 the star fading, the dust spreading; 4 a few fading dust puffs.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `alistar_fx_q_slam.png`：Q 大地粉碎：双拳砸地（地面上，以他为中心），6 帧

Q 砸地：以他为中心，地面裂开一圈白色发光的裂纹，碎石块往上崩、一圈土黄色的尘土冲击波往外扩（从斜上方看是扁椭圆，宽是高的 2 倍，范围半径约 28 格）（参考 Q_groundcrack、Q_groundcracks、Q_rockshards、E_DustCloud、E_Shockwave）。中间是人的位置，不要画人。约 64 格宽、36 格高（地上 60 × 30 的椭圆加上崩起来的石块）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a crack ramp (#FFFFFF, #F2EEFF, #CCC6E8), a rock ramp (#F0D4A0, #C08E58, #8A5E34, #563820) and a dust ramp (#FFF4DC, #EAD2A2, #C8A46E, #9A7448, #6A4A2C).
Effect: a GROUND SMASH seen from above at an angle, round a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a white-gold flash on the ground at the center; 2 glowing white cracks run out across the ground in a flattened ellipse twice as wide as tall (60 squares wide), a ring of tan dust bursting out; 3 at the ellipse's edge a ring of dust waves rises, 8 rock shards (outlined, brown) thrown up 6-10 squares; 4 the dust ring at full size, the shards at the top of their arc; 5 the shards falling, the dust thinning, the cracks dimming; 6 fading dust and faint cracks.
Layout: one horizontal row of 6 equal 16:9 cells, image size 3072x288 (each cell 512x288); the ellipse's center 8 squares (64 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `alistar_fx_q_up.png`：Q 击飞：被击飞的人脚下（目标身上），5 帧

被砸飞的敌人：脚下炸起一小团尘土，几块小碎石往上飞，两侧有向上的速度线（参考 Q_rockshards、E_DustCloud）。中间是人，不要画人；尘土在脚下，石块和速度线往上。约 18 格宽、22 格高，底边贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a dust ramp (#FFF4DC, #EAD2A2, #C8A46E, #9A7448, #6A4A2C) and a rock ramp (#F0D4A0, #C08E58, #8A5E34, #563820).
Effect: a KNOCK-UP BURST at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 5 frames: 1 a puff of tan dust bursts at the feet; 2 four small rock chips (outlined) and two white-tan speed lines shoot upward on both sides of the figure; 3 the chips at shoulder height, the dust spreading on the ground; 4 the chips falling, the dust thinning; 5 fading dust.
Layout: one horizontal row of 5 equal 9:11 cells, image size 1440x352 (each cell 288x352); the feet 4 squares (32 px) above the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `alistar_fx_w_dash.png`：W 冲锋：身后的尘土和速度线（施法者身上，跟随），6 帧

W 低头冲锋：他身后（左边）贴地扬起一串土黄色尘土，身体两侧几道白色的速度线往后拖（参考 E_DustCloud、SRU_dustCloud）。人朝右冲，人的位置空着，尘土和速度线都在人后面（左边）。约 48 格宽、30 格高，脚在格子底部往上 4 格、格子中间偏右。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a dust ramp (#FFF4DC, #EAD2A2, #C8A46E, #9A7448, #6A4A2C) and a crack ramp (#FFFFFF, #F2EEFF, #CCC6E8).
Effect: a CHARGE TRAIL behind a figure running to the RIGHT (do NOT draw the figure; leave its place empty), 6 frames: the figure's place is the RIGHT half of the cell; behind it (the LEFT half) puffs of tan dust kicked up along the ground and 4 white speed lines streaking back at body height; frame by frame new puffs appear at the figure's feet and older ones drift back to the left and fade.
Layout: one horizontal row of 6 equal 8:5 cells, image size 3072x320 (each cell 512x320); the figure's feet 4 squares (32 px) above the bottom, 6 squares right of the middle, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `alistar_fx_w_butt.png`：W 头槌撞上：角前的冲击（施法者身上，不跟随），4 帧

牛角撞上敌人的一下：角尖前面一个白金色的冲击星，往右炸出几道冲击线（参考 hiteffect、E_Flash、R_cas_flash）。朝右画：角尖在格子左边中点。约 20 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a flash ramp (#FFFFFF, #FFF6C8, #FFD870, #FFA830, #E06A10).
Effect: a HEADBUTT IMPACT pointing RIGHT, 4 frames: 1 a white star at the LEFT MIDDLE of the cell (the horn tip); 2 a burst of white-gold light 12 squares across with 5 impact lines shooting to the right; 3 the lines stretched further right, the burst fading; 4 fading sparks.
Layout: one horizontal row of 4 equal 5:4 cells, image size 1280x256 (each cell 320x256); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `alistar_fx_w_hit.png`：W 撞飞（目标身上），4 帧

被撞飞的敌人：一下白色闪光和一圈冲击，几道往右的冲击线（被撞向右边）（参考 hiteffect、E_ImpactRing）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a flash ramp (#FFFFFF, #FFF6C8, #FFD870, #FFA830, #E06A10).
Effect: a KNOCKBACK HIT, 4 frames: 1 a white flash; 2 a white-gold ring 14 squares across with 4 short impact lines streaking to the RIGHT; 3 the ring widening and thinning; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `alistar_fx_e_stomp.png`：E 践踏：每一脚的地面冲击（地面上，以他为中心），4 帧

践踏的每一脚：以他为中心，地面一圈土黄色的冲击波和尘土往外扩，几粒小碎石跳起来（参考 E_ImpactRing、E_Shockwave_Panning、E_Rocks、E_DustCloud）。从斜上方看是扁椭圆（宽是高的 2 倍，范围半径约 24 格）。中间是人，不要画人。比 Q 的砸地小、淡，一秒两次，不要太抢眼。约 52 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a dust ramp (#FFF4DC, #EAD2A2, #C8A46E, #9A7448, #6A4A2C) and a rock ramp (#F0D4A0, #C08E58, #8A5E34, #563820).
Effect: a STOMP SHOCKWAVE on the ground round a figure (do NOT draw the figure; leave its place empty), 4 frames: 1 a small tan dust puff at the center; 2 a thin ring of tan dust spreads over a flattened ellipse twice as wide as tall (40 squares wide), 4 tiny pebbles hop; 3 the ring at 50 squares wide, thinner; 4 the ring fading.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the ellipse's center 6 squares (48 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `alistar_fx_e_hit.png`：E 践踏踩到（目标身上），3 帧

被践踏踩到：一小团尘土和一下浅金色的闪光（参考 E_Tar_Flash、E_DustCloud）。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a dust ramp (#FFF4DC, #EAD2A2, #C8A46E, #9A7448, #6A4A2C) and a flash ramp (#FFFFFF, #FFF6C8, #FFD870, #FFA830, #E06A10).
Effect: a SMALL DUST HIT, 3 frames: 1 a small pale-gold flash; 2 a puff of tan dust 8 squares across; 3 the dust fading.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `alistar_fx_e_ready.png`：E 攒满 5 次：头顶的锁链印记（施法者身上，不跟随），5 帧

践踏踩中英雄 5 次，下次普攻会眩晕：他头顶亮起英雄联盟里那个发光的铁链图标（一段三环的铁链，周围金白色的光），亮一下再散开（参考 E_Stack_1、E_Stacks_Glow）。铁链有描边。约 18 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from an iron ramp (#C8C4CC, #8A848E, #4A4652, #2A2730) and a star ramp (#FFFFFF, #FFF4A0, #FFD23C, #E89A10).
Effect: a GLOWING CHAIN GLYPH, 5 frames: 1 a gold-white flash; 2 a horizontal chain of three iron links (outlined, 16 squares long, grey with white highlights) appears inside a gold-white glow; 3 the chain at full brightness, the glow pulsing; 4 the glow brighter, sparks flying off the links; 5 the chain and glow fading.
Layout: one horizontal row of 5 equal 3:2 cells, image size 1440x192 (each cell 288x192); the chain centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `alistar_fx_e_hit_stun.png`：E 眩晕的一拳（目标身上），5 帧

攒满后那一拳打中：一下大的橙金色闪光和一圈冲击环，铁链印记碎开（参考 E_Flash、E_ImpactRing、E_Stacks_Glow）。约 20 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a flash ramp (#FFFFFF, #FFF6C8, #FFD870, #FFA830, #E06A10) and an iron ramp (#C8C4CC, #8A848E, #4A4652, #2A2730).
Effect: a STUNNING BLOW, 5 frames: 1 a big white-gold flash; 2 an orange-gold ring 18 squares across with a burst of light, 3 small iron chain links (outlined) flying apart; 3 the ring widening, the links further out; 4 the ring thinning, sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `alistar_fx_e_stun.png`：E 眩晕中：头顶转圈的星星（目标身上，循环），8 帧

被眩晕的敌人头顶：三颗金色的小星星绕着转圈（包里所有眩晕都是这样）。左右对称，8 帧无缝循环。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a star ramp (#FFFFFF, #FFF4A0, #FFD23C, #E89A10).
Effect: STUN STARS, 8 frames, a seamless loop: three small five-pointed gold stars (3-4 squares each, white centres) circling on a flat ellipse 16 squares wide and 6 tall, the one in front larger and brighter, the one behind smaller and dimmer.
Layout: one horizontal row of 8 equal 9:4 cells, image size 2304x128 (each cell 288x128); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `alistar_fx_p_roar.png`：被动 凯旋怒吼：治疗的吼声（施法者身上，不跟随），6 帧

凯旋怒吼：以他为中心，地面扩出一圈绿白色的治疗波，周围升起绿色的光点和小十字（参考 P_softglow、Aura_Self）。中间是人，不要画人。约 48 格宽、40 格高，脚在格子底部往上 8 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a heal ramp (#FFFFFF, #D8FFD0, #8CF078, #3CC850, #1A8A3A).
Effect: a HEALING ROAR round a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a green-white flash at chest height; 2 a ring of green-white light spreads over the ground (a flattened ellipse twice as wide as tall, 40 squares wide); 3 green sparkles and small plus signs rise round the figure; 4 the ring at full size, the sparkles at head height; 5 the ring fading, the sparkles higher; 6 a few fading sparkles.
Layout: one horizontal row of 6 equal 6:5 cells, image size 2304x320 (each cell 384x320); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `alistar_fx_p_heal.png`：被动 凯旋怒吼：被治疗的人（目标身上），5 帧

被吼声治疗的人（他自己和身边的队友）：身上冒起绿色的光点和小十字往上飘。中间是人，不要画人。左右对称。约 14 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a heal ramp (#FFFFFF, #D8FFD0, #8CF078, #3CC850, #1A8A3A).
Effect: a HEAL on a figure (do NOT draw the figure; leave its place empty; symmetric left and right), 5 frames: 1 a soft green glow round the body; 2 four green plus signs and sparkles rising from the body; 3 the plus signs at head height; 4 above the head, fading; 5 gone but two sparkles.
Layout: one horizontal row of 5 equal 7:9 cells, image size 1120x288 (each cell 224x288); the figure centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `alistar_fx_r_cast.png`：R 坚定意志：怒吼的冲击（施法者身上，不跟随），6 帧

坚定意志：他怒吼，身边炸开一圈白色的冲击环和橙红色的怒气光芒，往外扩（参考 R_cas_aoe、R_cas_flash、blast_nova、Aura_Self）。中间是人，不要画人。约 56 格宽、56 格高，脚在格子底部往上 8 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a rage ramp (#FFFFFF, #FFE0A0, #FF9A40, #F04A20, #B01E18) and a crack ramp (#FFFFFF, #F2EEFF, #CCC6E8).
Effect: a ROAR SHOCKWAVE round a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a white flash at head height; 2 a white ring bursts out round the figure (round, 30 squares across) with an orange-red glow inside it; 3 the ring at 46 squares, jagged white rays shooting out; 4 the ring at 54 squares, thinner, the glow round the figure's outline; 5 the ring fading; 6 faint orange embers.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `alistar_fx_r_on.png`：R 减伤中：身上的怒气光环（循环），6 帧

坚定意志的 7 秒：他全身外面一圈橙红色的怒气火焰在往上烧，脚下一圈红光（参考 Aura_Self、blast_nova、R_cas_aoe）。**只画人轮廓外面的一圈和脚下，中间留空**（游戏里画在人物上面，不能把人挡住）。左右对称，6 帧无缝循环。约 46 格宽、50 格高，脚在格子底部往上 8 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, dust, glows, cracks or sparks (only solid objects - rock shards, the chain links - get a 1-square dark outline #140A20), BRIGHT colours (each shape lit with its lightest shades and a white or light core - it must read on a dark battlefield), colours only from a rage ramp (#FFFFFF, #FFE0A0, #FF9A40, #F04A20, #B01E18).
Effect: a RAGE AURA round a figure (do NOT draw the figure; leave its place empty - draw only round its outline and at its feet, the middle stays empty), 6 frames, a seamless loop, symmetric left and right: tongues of orange-red flame licking upward round a large hunched figure's silhouette (40 squares wide, 44 tall), a red-orange ellipse glowing on the ground at its feet, small embers rising; the flames shift up a square each frame.
Layout: one horizontal row of 6 equal 23:25 cells, image size 2208x400 (each cell 368x400); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `alistar_fx_a_hit` | view_effects `league_alistar_a_hit`（跟随，画在人物上面） | 14 |
| `alistar_fx_q_slam` | view_effects `league_alistar_q_slam` 和 `w_slam`（同一张，BIG，画在人物下面，不跟随） | 64 × 36 |
| `alistar_fx_q_up` | view_effects `league_alistar_q_up`（跟随，画在人物下面） | 18 × 22 |
| `alistar_fx_w_dash` | view_effects `league_alistar_w_dash`（BIG，施法者身上，第一 tick 跟随） | 48 × 30 |
| `alistar_fx_w_butt` | view_effects `league_alistar_w_butt`（落地时，施法者身上，不跟随；格子左边中点放到头槌那一帧的牛角尖） | 20 × 16 |
| `alistar_fx_w_hit` | view_effects `league_alistar_w_hit`（跟随，画在人物上面） | 16 |
| `alistar_fx_e_stomp` | view_effects `league_alistar_e_stomp`（BIG，画在人物下面，不跟随；每 0.5 秒一次） | 52 × 26 |
| `alistar_fx_e_hit` | view_effects `league_alistar_e_hit`（跟随，画在人物上面） | 10 |
| `alistar_fx_e_ready` | view_effects `league_alistar_e_ready`（施法者身上，不跟随；头顶上方） | 18 × 12 |
| `alistar_fx_e_hit_stun` | view_effects `league_alistar_e_hit_stun`（跟随，画在人物上面） | 20 |
| `alistar_fx_e_stun` | view_buffs `league_alistar_e_stun`（循环，画在人物上面，1 秒） | 18 × 8 |
| `alistar_fx_p_roar` | view_effects `league_alistar_p_roar`（BIG，施法者身上，不跟随） | 48 × 40 |
| `alistar_fx_p_heal` | view_effects `league_alistar_p_heal`（跟随，画在人物上面） | 14 × 18 |
| `alistar_fx_r_cast` | view_effects `league_alistar_r_cast`（BIG，施法者身上，不跟随） | 56 × 56 |
| `alistar_fx_r_on` | view_buffs `league_alistar_r_on`（BIG，循环，画在人物上面，7 秒） | 46 × 50 |

- `q_slam` 一张导成 `q_slam`、`w_slam` 两个标签。
- 施法者身上的画面按 `design/alistar_shots.png` 的十字把格子的起点挪过去；晚于第一 tick 播放的（`q_slam`、`w_slam`、`w_butt`、`e_stomp`、`e_ready`、`p_roar`、`r_cast`）`is_follow` 为 false（红方方向）。
- 清掉 Codex 给光和尘土描的最深色边（`import_riven.py` 的 `unrim`，碎石、铁链保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
