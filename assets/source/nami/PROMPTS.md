# 娜美：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图。** 造型和 8 个动作已经做完并导入游戏，这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里娜美自己的特效贴图，按用在我们哪张特效分好了行（普攻的水花和水滴、W 的水流、治疗和祝福的水环、Q 的泡泡和落点圈、R 的浪头和水柱），只在本地用，不要提交。颜色和画风对照 `design/nami_design.png`（定稿造型，8 倍）；大小对照 `design/nami_ingame.png`（游戏里的全部帧，4 倍，绿线是站位和脚底）：娜美从金冠到尾鳍尖 50 格，其他英雄约 35 格。
> - 特效照下面第 1–13 条和「所有特效图的规则」画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 手杖宝珠射出一颗水弹 | `nami_fx_bolt` · `nami_fx_hit` |
| 技能 1 = W「冲击之潮」+ E「唤潮之佑」 | 一道水流在敌人和友军之间弹跳：打敌人造成伤害并减速，落到友军身上回血，并让友军 4 秒内攻击和法术更强；没有别的友军时水流飞回娜美 | `nami_fx_w_stream` · `nami_fx_w_hit` · `nami_fx_w_heal` · `nami_fx_e_blessing` |
| 技能 2 = Q「碧波之牢」 | 抛出一颗大水泡，落点先出现提示圈，落地炸开，把范围内的敌人裹进水泡浮空 1.25 秒 | `nami_fx_q_bubble` · `nami_fx_q_mark` · `nami_fx_q_burst` · `nami_fx_q_prison` |
| 大招 = R「怒涛之啸」 | 召唤一道巨浪往前冲，穿过的敌人被击飞并减速 | `nami_fx_r_wave` · `nami_fx_r_hit` |
| 被动「踏浪之行」 | 技能碰到的友军加速 1.5 秒 | `nami_fx_p_haste` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（按每条写的用）：
  - 海水（主体）：`#FFFFFF`、`#D4FFF9`、`#86F2EA`、`#33D1D6`、`#1596AE`、`#0C5F86`、`#083A63`；
  - 治疗的薄荷绿（W 回血、E 祝福的亮部）：`#FFFFFF`、`#E4FFF4`、`#8CF7C8`、`#36D99A`；
  - 宝珠蓝（普攻水弹的芯，和手杖顶上的宝珠同色）：`#F2FDFD`、`#1E8FD6`、`#1B4F92`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- 命中、炸开、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（治疗、祝福、水牢）：格子中间留出一个空的人形位置，不要画人，**不能挡住身体和脸**，只画围在外面的水、泡和光点；水牢的泡里面是透明的。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `nami_fx_bolt.png`：普攻水弹（飞行），4 帧循环

手杖宝珠射出的一颗水弹：亮青色的圆水珠，芯是宝珠的蓝，左上一点白高光，后面拖着一小段水尾和两三颗水滴（参考 BA_Trail、BA_BlurDrops）。约 14 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63) with the staff orb's blue (#F2FDFD, #1E8FD6, #1B4F92).
Effect: a WATER BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round glossy orb of sea water (bright aqua, a blue core #1E8FD6, a white highlight at its upper left) at 70% of the cell width, about 40% of the cell height; behind it a short tapering tail of water with two or three droplets streaming to the left edge; the tail ripples a little each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the bolt on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nami_fx_hit.png`：普攻命中，5 帧

水弹打中目标：一圈青白的水花炸开，碎成弯弯的水滴往外飞（参考 WaterSplash、Splash_2x2）。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: a WATER SPLASH IMPACT, 5 frames: 1 a small bright white-aqua flash at the center; 2 a round splash of aqua water bursting outward, white foam at its edge; 3 the splash breaks into curved droplets flying outward and a thin ring; 4 the droplets fly further and darken to deep teal; 5 a few small teal specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nami_fx_w_stream.png`：W 冲击之潮的水流（飞行，敌我之间弹跳，也用于飞回娜美），4 帧循环

一道跃动的水流：前面是带白色浪花的圆水头，后面拖着起伏的青色水带，越往后越细，边上甩出小水滴（参考 watertrail、WaterTrailLoop、Z_trail）。约 24 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: EBB AND FLOW, a leaping stream of water flying to the RIGHT, 4 frames, a seamless loop, roughly SYMMETRIC above and below the middle line: a bright round head of water with a white foam cap at 75% of the cell width; behind it a wavy ribbon of aqua and teal water, thick at the head and thinning to the left edge, its waves travelling backward each frame, small droplets breaking off.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the stream on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nami_fx_w_hit.png`：W 水流打中敌人，5 帧

水流撞上敌人：一大团青白水花呈皇冠状溅开，白色泡沫，水滴往外飞，一圈细水环（参考 LinearSplashes）。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: a STREAM HIT, 5 frames: 1 a white flash at the center; 2 a large burst of aqua water and white foam spraying outward in a crown shape; 3 droplets fly out, a thin ring of water spreads; 4 the droplets fall and darken; 5 a few teal specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nami_fx_w_heal.png`：W 水流治疗友军（友军身上），5 帧

水流落到友军身上：一圈薄荷绿的水滴和小气泡从腰间往上飘，旁边一个亮的小十字（参考 E_splash_ring、glowwater）。中间留空人形，不画人。约 20 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63) with a mint healing glow (#FFFFFF, #E4FFF4, #8CF7C8, #36D99A).
Effect: a HEALING TIDE rising around a standing figure (leave a figure-shaped empty space in the middle, about 60% of the cell width and 80% of the cell height - do NOT draw the figure), 5 frames: 1 a ring of small aqua-green water droplets around the figure's waist; 2 the droplets rise, a bright pale-green plus sign appears beside the figure's shoulder, small bubbles; 3 droplets, bubbles and the plus sign rise higher, glowing mint (#8CF7C8); 4 they reach the head height and fade to teal; 5 a few faint specks.
Layout: one horizontal row of 5 equal cells, each 2 wide to 3 tall, image size 1280x384 (each cell 256x384); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nami_fx_e_blessing.png`：E 唤潮之佑（被治疗的友军身上，4 秒），4 帧循环

友军得到娜美的祝福：两道细水带绕着友军的腰和胸口转，前面亮、后面暗，周围绕着薄荷绿的小光点和水滴（参考 WateAround、orbswirl）。中间留空人形，不挡脸和胸口。约 28 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63) with a mint healing glow (#FFFFFF, #E4FFF4, #8CF7C8, #36D99A).
Effect: TIDECALLER'S BLESSING, a water aura around a standing figure (leave a figure-shaped empty space in the middle, about 60% of the cell width and 80% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: two thin ribbons of aqua water swirl around the figure at waist and chest height, crossing in front and behind (the parts behind darker), small mint-green sparkles and droplets orbiting with them; the ribbons turn a quarter each frame; nothing covers the face or the chest.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 1152x384 (each cell 288x384); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nami_fx_q_bubble.png`：Q 碧波之牢的泡泡（抛物线飞行），4 帧循环

抛出去的一颗大水泡：青色的边，里面浅青半透明的样子带深色水纹，左上一道白色弧形高光，里面两颗小气泡；飞的时候轻轻晃（参考 BubbleArea、Q_Center_Shine）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: an AQUA PRISON BUBBLE flying (lobbed), 4 frames, a seamless loop: a round bubble of sea water filling about 70% of the cell: a 2-square aqua rim, the inside lighter and see-through-looking (pale aqua with darker swirls), a white curved highlight at its upper left, two tiny bubbles inside; it wobbles: slightly wider in frame 2, round in frame 3, slightly taller in frame 4.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nami_fx_q_mark.png`：Q 落点提示（地面，泡泡飞行的 0.4 秒），4 帧

泡泡要落下的地方：地上一个扁椭圆的青色光圈，里面一圈浅色内圈和往外荡的水波（参考 Q_TeamRing、Q_Floor_Puddle）。宽是高的 2 倍。约 44 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: a TARGET RING on the ground where the bubble will land, 4 frames: a flat ellipse (twice as wide as tall) filling the cell: a 2-square aqua ring with a pale inner ring, faint teal ripples inside; 1 the ring appears bright; 2-4 the inner ripples move outward, the ring stays.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nami_fx_q_burst.png`：Q 泡泡落地炸开（地面），6 帧

泡泡砸在地上：一股水柱冲起又落下，地上一圈扁椭圆的水花往外扩（参考 Q_Splashes、SplashRing）。约 44 格宽、36 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: the BUBBLE BURSTS on the ground, 6 frames: 1 a bright white-aqua flash at the bottom middle; 2 a column of aqua water shoots up to 70% of the cell height, white foam on top, a flat splash ring on the ground (an ellipse twice as wide as tall); 3 the column breaks into big droplets, the ring spreads to the cell's width; 4 the droplets fall, the ring thins; 5 small droplets and a faint ring; 6 a few teal specks.
Layout: one horizontal row of 6 equal cells, each 5 wide to 4 tall, image size 1920x256 (each cell 320x256); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nami_fx_q_prison.png`：Q 水牢（被困的敌方英雄身上，1.25 秒），8 帧

敌人被裹进大水泡：水从脚下卷上来合成一个圆泡，泡里是透明的（**不能挡住人**），只画青色的边、左上的白高光和一道浅色内线，泡里往上冒小气泡；最后泡破成水滴（参考 BubbleArea、Q_WaveDot、Water_10）。约 34 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: an AQUA PRISON around a standing figure (the figure is NOT drawn, and the bubble must not hide it: its inside stays transparent), 8 frames: 1 water swirls up from the bottom around the empty figure; 2 the swirl closes into a round bubble enclosing the figure: a 2-square aqua rim with white highlights at its upper left and a thin pale inner line; 3-6 the bubble holds, wobbling a little (slightly wider, round, slightly taller, round), tiny bubbles rising inside along the rim; 7 the bubble bursts: the rim breaks into curved droplets flying outward; 8 a few falling droplets.
Layout: one horizontal row of 8 equal cells, each 5 wide to 6 tall, image size 2560x384 (each cell 320x384); the bubble centered at half the cell height, about 90% of the cell width. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nami_fx_r_wave.png`：R 怒涛之啸的巨浪（飞行，大图），4 帧循环

一堵从上往下看的月牙形巨浪往右冲：前沿是往前卷的白色浪花，后面是一道厚厚的深青、深蓝的水，带着浅青的水纹，月牙的两个尖往后拖出白色水雾（参考 R_Water02、R_Water04、R_WaterCrescent）。整张图朝右，上下对称。约 40 格长、64 格宽（浪的宽度就是技能宽度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: TIDAL WAVE, a huge crescent-shaped wall of water seen from above, rushing to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: the front (right) edge is a curved crescent of white foam curling forward, behind it a thick band of deep teal and blue water (#1596AE, #0C5F86, #083A63) with lighter aqua streaks, the crescent's two tips trailing back to the left with white spray; the foam churns and the streaks move backward each frame.
Layout: one horizontal row of 4 equal cells, each 5 wide to 8 tall, image size 1280x512 (each cell 320x512); the crescent spans about 90% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `nami_fx_r_hit.png`：R 巨浪打中敌人（击飞），5 帧

被巨浪卷到的敌人脚下冲起一股水柱把人托起，浪花四溅，落下时地上一圈水花（参考 R_LinearSplashes、Splashes）。不画人。约 24 格宽、32 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: a WAVE HIT, 5 frames: a tall spout of water bursting up from the ground under a figure (the figure is NOT drawn): 1 a white foam flash at the bottom; 2 a column of aqua water and foam shoots up to 80% of the cell height; 3 the column peaks and splashes outward, droplets flying; 4 the water falls back, a splash ring on the ground (an ellipse twice as wide as tall); 5 teal droplets and a faint ring.
Layout: one horizontal row of 5 equal cells, each 3 wide to 4 tall, image size 1440x384 (each cell 288x384); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `nami_fx_p_haste.png`：被动 踏浪之行（友军脚下，1.5 秒加速），4 帧循环

被娜美技能碰到的友军脚下：一圈打旋的青色水涡和白色泡沫（扁椭圆），往左拖两三道短水痕（人往右跑）（参考 WetTrail、Puddle_Ripples）。不画人。约 26 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sea-water ramp (#FFFFFF, #D4FFF9, #86F2EA, #33D1D6, #1596AE, #0C5F86, #083A63).
Effect: SURGING TIDES, a swirl of water at a figure's feet (the figure is NOT drawn), 4 frames, a seamless loop: a flat ellipse of swirling aqua water and white foam (twice as wide as tall) at the bottom middle of the cell, two or three short streaks of water trailing to the LEFT (the figure runs right); the swirl turns and the streaks flicker each frame.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 1280x128 (each cell 320x128); the swirl at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nami_fx_bolt` | 14 × 8 | 手杖宝珠射出的一颗水弹：亮青色的圆水珠，芯是宝珠的蓝，左上一点白高光，后面拖着一小段水尾和两三颗水滴（参考 BA_Trail、BA_BlurDrops）。约 14 格长、8 格高。 |
| `nami_fx_hit` | 16 | 水弹打中目标：一圈青白的水花炸开，碎成弯弯的水滴往外飞（参考 WaterSplash、Splash_2x2）。约 16 格宽。 |
| `nami_fx_w_stream` | 24 × 12 | 一道跃动的水流：前面是带白色浪花的圆水头，后面拖着起伏的青色水带，越往后越细，边上甩出小水滴（参考 watertrail、WaterTrailLoop、Z_trail）。约 24 格长、12 格高。 |
| `nami_fx_w_hit` | 20 | 水流撞上敌人：一大团青白水花呈皇冠状溅开，白色泡沫，水滴往外飞，一圈细水环（参考 LinearSplashes）。约 20 格宽。 |
| `nami_fx_w_heal` | 20 × 30 | 水流落到友军身上：一圈薄荷绿的水滴和小气泡从腰间往上飘，旁边一个亮的小十字（参考 E_splash_ring、glowwater）。中间留空人形，不画人。约 20 格宽、30 格高。 |
| `nami_fx_e_blessing` | 28 × 36 | 友军得到娜美的祝福：两道细水带绕着友军的腰和胸口转，前面亮、后面暗，周围绕着薄荷绿的小光点和水滴（参考 WateAround、orbswirl）。中间留空人形，不挡脸和胸口。约 28 格宽、36 格高。 |
| `nami_fx_q_bubble` | 14 | 抛出去的一颗大水泡：青色的边，里面浅青半透明的样子带深色水纹，左上一道白色弧形高光，里面两颗小气泡；飞的时候轻轻晃（参考 BubbleArea、Q_Center_Shine）。约 14 格。 |
| `nami_fx_q_mark` | 44 × 22（半径 22000） | 泡泡要落下的地方：地上一个扁椭圆的青色光圈，里面一圈浅色内圈和往外荡的水波（参考 Q_TeamRing、Q_Floor_Puddle）。宽是高的 2 倍。约 44 格宽、22 格高。 |
| `nami_fx_q_burst` | 44 × 36 | 泡泡砸在地上：一股水柱冲起又落下，地上一圈扁椭圆的水花往外扩（参考 Q_Splashes、SplashRing）。约 44 格宽、36 格高，地面在格子底部。 |
| `nami_fx_q_prison` | 34 × 40 | 敌人被裹进大水泡：水从脚下卷上来合成一个圆泡，泡里是透明的（**不能挡住人**），只画青色的边、左上的白高光和一道浅色内线，泡里往上冒小气泡；最后泡破成水滴（参考 BubbleArea、Q_WaveDot、Water_10）。约 34 格宽、40 格高。 |
| `nami_fx_r_wave` | 40 × 64（半径 32000） | 一堵从上往下看的月牙形巨浪往右冲：前沿是往前卷的白色浪花，后面是一道厚厚的深青、深蓝的水，带着浅青的水纹，月牙的两个尖往后拖出白色水雾（参考 R_Water02、R_Water04、R_WaterCrescent）。整张图朝右，上下对称。约 40 格长、64 格宽（浪的宽度就是技能宽度）。 |
| `nami_fx_r_hit` | 24 × 32 | 被巨浪卷到的敌人脚下冲起一股水柱把人托起，浪花四溅，落下时地上一圈水花（参考 R_LinearSplashes、Splashes）。不画人。约 24 格宽、32 格高，地面在格子底部。 |
| `nami_fx_p_haste` | 26 × 10 | 被娜美技能碰到的友军脚下：一圈打旋的青色水涡和白色泡沫（扁椭圆），往左拖两三道短水痕（人往右跑）（参考 WetTrail、Puddle_Ripples）。不画人。约 26 格宽、10 格高。 |

- `league_nami_p_haste` 目前没有显示：导入时在 `view_buffs` 里加上（被动加速的 1.5 秒）。
- 普攻水弹、W 水流、Q 泡泡的出手点按动作条的出手帧量宝珠的位置（普攻第 4 帧、W 第 3 帧、Q 第 4 帧），写进各自的 `y_offset`；R 的巨浪从第 5 帧插杖处出发。
