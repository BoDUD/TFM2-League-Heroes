# 酒桶 古拉加斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型和动作已定（`design/gragas_idle.png`：游戏里的 3/4 正面待机，8 倍，连背上的酒桶 44 行、36 格宽）。
> - 大小对照 `design/gragas_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/gragas_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里酒桶自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**金黄色的酒和白色泡沫**；扔出去的酒桶是木头加铁箍；R 的爆炸是火光裹着酒浪；E 是尘土和金星；W 的狂暴是红橙色热气；被动回血是清新的绿金色。
> - **特效要亮**：每团酒花、火光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的热气、酒泡、回血光点只画两边，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的两只酒桶（`q_barrel`、`r_cask`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。其余所有画面（打中、落地、爆炸、脚下、头顶、身上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `gragas_fx_<名字>.png` 和原尺寸的 `pixel_1x/`，附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `gragas_fx_pack_done.zip`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「欢乐时光」 | 重拳；每放一个技能先喝一口回血 | `a_hit` · `p_heal` |
| 技能 1 = Q「滚动酒桶」 | 扔出酒桶，落地冒泡 0.75 秒后爆炸，炸到的人减速 | `q_barrel` · `q_land` · `q_boom` · `q_hit` · `q_slow` |
| 技能 2 = E「肉弹冲击」+ W「醉酒狂暴」 | 冲过去用肚子撞，撞到的人眩晕；随后扛桶喝酒，下一拳炸开一圈酒浪 | `e_dust` · `e_hit` · `e_stun` · `w_drink` · `w_on` · `w_hit` |
| 大招 = R「爆破酒桶」 | 扔出大酒桶，落地爆炸，把人炸飞到他这边 | `r_cask` · `r_boom` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**酒、泡沫、火光、尘土、热气、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**；只有飞出去的两只酒桶（实物）有 1 格深棕描边。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 酒和泡沫：`#FFFFFF`、`#FFF6D8`、`#FFE08A`、`#FFC23D`、`#E8901A`、`#B85E12`；
  - 酒桶的木头（#2E1A10 是描边）：`#F2B868`、`#C47A34`、`#8A4E22`、`#5A2F16`、`#2E1A10`；
  - 铁箍：`#D8DCE6`、`#9EA6B8`、`#6A7088`、`#3E4256`；
  - 火光（R）：`#FFFFFF`、`#FFF2B0`、`#FFD24A`、`#FF9A1E`、`#E8501A`、`#A8280E`；
  - 尘土（E）：`#F4E8D0`、`#D8C4A0`、`#B09A78`、`#806E58`；
  - 狂暴热气（W）：`#FFE2C0`、`#FF9A5A`、`#F05A28`、`#B8301A`；
  - 眩晕星星：`#FFFFFF`、`#FFF6A0`、`#FFD84A`、`#E8A21A`；
  - 回血（被动）：`#FFFFFF`、`#E8FFD0`、`#B8F070`、`#6CC83A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，Q 爆炸半径 19000，W 酒浪半径 17000，E 撞击半径 20000，R 爆炸半径 26000）。

### 1. `gragas_fx_a_hit.png`：普攻拳头打中（目标身上），4 帧

一记重拳打中：中间一道白色闪光，四周溅开几颗金黄色的酒滴和白沫（参考 ImpactGlow、Foam_Splash）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: a FIST HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white impact flash 5 squares across; 2 a burst of white foam and golden ale drops 10 squares across; 3 the burst thinner, drops flying out at mirrored places; 4 a few fading drops.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `gragas_fx_w_hit.png`：W 醉酒狂暴：强化普攻的酒浪爆发（目标身上），5 帧

喝过酒后的下一拳：以目标为中心炸开一圈金黄色的酒浪和白沫（从斜上方看的扁椭圆，约 34 格宽），中间一团白光，酒滴往外飞（参考 Z_WineSplash、Splash_2x2、Z_Splashes_Anim_4x4）。**左右对称**，中间留出人的位置不要盖满。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: an ALE SHOCKWAVE round a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across at the middle; 2 a ring of white foam and golden ale bursting out, an ellipse 24 squares wide and 9 tall; 3 the ring at 34 x 13, splashes rising at mirrored places on its rim; 4 the ring breaking into drops; 5 fading drops. The middle stays mostly clear.
Layout: one horizontal row of 5 equal 38:22 cells, image size 3040x352 (each cell 608x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `gragas_fx_q_barrel.png`：Q 滚动酒桶：飞出去的酒桶（抛物线飞行，循环），4 帧

Q 扔出去的小酒桶：从侧面看的木酒桶在翻滚（桶身横着，两头是圆桶盖，两道铁箍），后面拖一小串白沫（参考 Q_Mis、Q_Wood）。**上下对称**（滚动用铁箍和木纹的位置变化表现，不画朝一边转的斜线）。桶是实物，有 1 格深棕描边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from the keg's wood (#F2B868, #C47A34, #8A4E22, #5A2F16, #2E1A10; #2E1A10 is its 1-square outline), iron hoops (#D8DCE6, #9EA6B8, #6A7088, #3E4256) and an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: a SMALL TUMBLING KEG flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a wooden keg seen from the side, 10 squares long and 8 tall, warm brown staves, two grey iron hoops, a round lid at each end, a 1-square dark brown outline; its rolling shown by the staves' lines and the hoops shifting each frame (mirrored top to bottom); a short trail of white foam bubbles behind it to the left (mirrored).
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); the keg's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `gragas_fx_q_land.png`：Q 酒桶落地后在地上冒泡（落点，0.75 秒），6 帧

酒桶落在地上：一只立着的小酒桶（正面看，上面的桶盖和方木塞朝上），桶缝里往外冒白沫和金色酒泡，越来越多、桶在抖（参考 Q_Bubbles、Q_Floor_Puddle、Goo_Q）。**左右对称**。6 帧依次播放，最后一帧泡沫最满（下一刻就爆）。桶底在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from the keg's wood (#F2B868, #C47A34, #8A4E22, #5A2F16, #2E1A10; #2E1A10 is its 1-square outline), iron hoops (#D8DCE6, #9EA6B8, #6A7088, #3E4256) and an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: a SMALL KEG ON THE GROUND ABOUT TO BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an upright wooden keg 8 squares wide and 9 tall seen from the front (two grey iron hoops, a dark brown outline), standing on a small golden puddle; frame by frame more white foam and golden bubbles squirt out of its seams and lid at mirrored places, the keg trembling one square (1, 3, 5 up, 2, 4, 6 down), frame 6 brimming with foam.
Layout: one horizontal row of 6 equal square cells, image size 1536x256 (each cell 256x256, 16 px a square); centered across, the keg's foot on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `gragas_fx_q_boom.png`：Q 酒桶爆炸（落点），6 帧

酒桶炸开：一大团金黄色的酒浪和白沫往四周炸，地上一圈扁椭圆的酒浪（约 38 格宽），几块木片飞起来（参考 Z_WineSplash、Z_BarrelPiece、Q_hit_aoering）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12) and the keg's wood (#F2B868, #C47A34, #8A4E22, #5A2F16, #2E1A10; #2E1A10 is its 1-square outline).
Effect: a KEG BLAST on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares across; 2 a dome of white foam and golden ale 20 squares wide bursting up; 3 a ring of ale on the ground, an ellipse 32 squares wide and 12 tall, splashes and 4 wooden stave pieces flying up at mirrored places; 4 the ring at 38 x 14, the pieces higher; 5 drops falling, the ring thinning; 6 a fading puddle ring.
Layout: one horizontal row of 6 equal 42:26 cells, image size 4032x416 (each cell 672x416, 16 px a square); centered across, the ring's middle 7 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `gragas_fx_q_hit.png`：Q 炸中（被炸中的人身上），4 帧

被酒浪泼中：一团金色酒花和白沫溅在身上（参考 Foam_Splash）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: an ALE SPLASH on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white burst 4 squares; 2 golden ale and white foam splashing 10 squares across; 3 drops at mirrored places; 4 fading drops.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `gragas_fx_q_slow.png`：Q 减速（被减速的人脚下，循环），4 帧

脚下一滩黏糊糊的金色酒水（从斜上方看的扁椭圆），表面几个泡泡冒起又破（参考 Puddle_Ripples、Q_Floor_Puddle）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: a STICKY ALE PUDDLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse 16 squares wide and 5 tall of golden amber ale with a lighter rim, 2-4 bubbles at mirrored places that swell and pop in turn.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `gragas_fx_e_dust.png`：E 肉弹冲击：起步的尘土（他脚下，留在原地），5 帧

冲出去的那一下：脚下扬起一圈尘土（从斜上方看的扁椭圆，往外散开）和几颗碎石（参考 E_Dirt_Takeoff、E_EdgeDust、Dust）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#F4E8D0, #D8C4A0, #B09A78, #806E58).
Effect: a DUST KICK-OFF on the ground, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a low dust puff 8 squares wide; 2 a ring of dust clouds, an ellipse 18 squares wide and 6 tall, grit specks flying at mirrored places; 3 the ring at 24 x 8; 4 thinning; 5 fading wisps.
Layout: one horizontal row of 5 equal 26:12 cells, image size 2080x192 (each cell 416x192, 16 px a square); centered across, the ring's middle 4 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `gragas_fx_e_hit.png`：E 撞中（被撞的人身上），5 帧

肚子撞上去：一个大的白色冲击星（四到八个尖角）炸开，一圈尘土往外，几颗星星溅出来（参考 E_Cas_01、E_CloudRing、ImpactGlow）。**左右对称**。约 20 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#F4E8D0, #D8C4A0, #B09A78, #806E58) and a star-gold ramp (#FFFFFF, #FFF6A0, #FFD84A, #E8A21A).
Effect: a BODY SLAM IMPACT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white starburst 8 squares across with sharp points; 2 the starburst 16 squares, a ring of dust puffs round it; 3 the ring 20 squares across, 4 little gold stars flying out at mirrored places; 4 dust and stars fading; 5 a few wisps.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `gragas_fx_e_stun.png`：E 眩晕（被晕的人头顶，循环），4 帧

头顶一圈打转的金色小星星（从斜上方看的扁圆，3 颗星）。**每帧左右对称**（星星换到对称的位置，不画成朝一个方向转）。4 帧无缝循环。画在格子的上部（头顶上方）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a star-gold ramp (#FFFFFF, #FFF6A0, #FFD84A, #E8A21A).
Effect: DIZZY STARS above a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small 5-point gold stars (3 squares each) on a flat ellipse 14 squares wide and 4 tall, their places mirrored left-right in every frame and moving to new mirrored places each frame; a faint gold trail between them.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `gragas_fx_w_drink.png`：W 醉酒狂暴：喝酒时头边冒的酒泡（他身上），6 帧

扛起酒桶灌酒：头部周围冒出一串金色酒泡和白沫，往上飘、一个个破掉（参考 W_Bubble、W_Flare）。**左右对称、中间留空**（不要挡住他的脸）。画在格子上部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: ALE BUBBLES round a drinking head, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the MIDDLE 8 squares wide EMPTY: golden and white bubbles (1-3 squares) rising on both sides from the bottom of the cell to the top, mirrored, popping into tiny white sparks near the top; frame by frame more bubbles, frame 6 fewer.
Layout: one horizontal row of 6 equal 22:18 cells, image size 2112x288 (each cell 352x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `gragas_fx_w_on.png`：W 醉酒狂暴：下一拳蓄满（他身上，循环），4 帧

喝完酒的狂暴：他身体两侧往上冒红橙色的热气（一股一股往上飘），头顶几缕蒸汽（参考 W_Buff_Avatar、flame_Ring）。**中间留空、左右对称**，只画身体外沿和头顶。4 帧无缝循环。约 36 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot steam ramp (#FFE2C0, #FF9A5A, #F05A28, #B8301A).
Effect: HOT RAGE STEAM round a big figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 26 squares wide and 40 tall in the middle): puffs of red-orange steam rising along both sides from the waist up and 3 wisps above the head, mirrored, each puff moving up 2-3 squares a frame and fading at the top.
Layout: one horizontal row of 4 equal 38:46 cells, image size 2432x736 (each cell 608x736, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `gragas_fx_p_heal.png`：被动欢乐时光：喝一口回血（他身上），5 帧

每放一个技能先喝一口：身上冒出一圈绿金色的小光点和小酒泡往上飘（参考 W_Global_Heal、Rengar_Base_W_Heal_Spark）。**左右对称、中间留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fresh green-gold ramp (#FFFFFF, #E8FFD0, #B8F070, #6CC83A).
Effect: a FRESH SWIG HEAL round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle 12 squares EMPTY: small green-gold plus-shaped sparks (3 squares) and bubbles rising on both sides from the feet to above the head, mirrored, frame 3 the most, frame 5 a few fading.
Layout: one horizontal row of 5 equal 26:32 cells, image size 2080x512 (each cell 416x512, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `gragas_fx_r_cask.png`：R 爆破酒桶：飞出去的大酒桶（抛物线飞行，循环），4 帧

R 扔出去的大酒桶：比 Q 的大，桶身横着翻滚，桶盖上一圈火光，拖着火星和酒沫（参考 Z_Cask、Z_Grog、Goo_R）。**上下对称**。桶是实物，有 1 格深棕描边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from the keg's wood (#F2B868, #C47A34, #8A4E22, #5A2F16, #2E1A10; #2E1A10 is its 1-square outline), iron hoops (#D8DCE6, #9EA6B8, #6A7088, #3E4256), a fire ramp (#FFFFFF, #FFF2B0, #FFD24A, #FF9A1E, #E8501A, #A8280E).
Effect: a BIG TUMBLING CASK flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a wooden cask seen from the side, 14 squares long and 11 tall, warm brown staves, three grey iron hoops, a dark brown outline; a small burning fuse of fire at its front lid; a trail of sparks and foam to the left (mirrored); the staves and hoops shifting each frame to show it rolling.
Layout: one horizontal row of 4 equal 20:16 cells, image size 1280x256 (each cell 320x256, 16 px a square); the cask's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `gragas_fx_r_boom.png`：R 爆炸（落点），7 帧

大酒桶爆炸：一团橙黄色的火球往上冲，外面裹着金色酒浪和白沫，地上一圈扁椭圆的冲击波（约 52 格宽）往外扩，几块木桶碎片飞出（参考 Z_Color_WineSplash、Z_Splashes_Anim、Z_BarrelPiece、Flare_1）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF2B0, #FFD24A, #FF9A1E, #E8501A, #A8280E), an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12) and the keg's wood (#F2B868, #C47A34, #8A4E22, #5A2F16, #2E1A10; #2E1A10 is its 1-square outline).
Effect: a BIG CASK EXPLOSION on the ground, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 12 squares across; 2 a fireball 20 squares wide rising, white-yellow core, orange edge; 3 the fireball 28 wide inside a ring of golden ale and foam, a ground shockwave ellipse 36 squares wide and 12 tall; 4 the shockwave at 52 x 16, 6 wooden stave pieces flying out at mirrored places, the fire rising into smoke-free orange puffs; 5 ale drops raining, the ring thinning; 6 fading puffs and drops; 7 a few embers.
Layout: one horizontal row of 7 equal 58:38 cells, image size 6496x608 (each cell 928x608, 16 px a square); centered across, the ground ring's middle 8 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `gragas_fx_r_hit.png`：R 炸中（被炸飞的人身上），4 帧

被炸到：一团橙黄色的小火花和酒沫溅在身上（参考 R_cone_hit、R_Drops）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, liquid, smoke or rings, BRIGHT colours (each splash lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF2B0, #FFD24A, #FF9A1E, #E8501A, #A8280E) and an ale-and-foam ramp (#FFFFFF, #FFF6D8, #FFE08A, #FFC23D, #E8901A, #B85E12).
Effect: a BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange-white flash 6 squares; 2 fire sparks and golden ale splashing 12 squares across; 3 sparks and drops at mirrored places; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `gragas_fx_a_hit` | view_effects `league_gragas_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `gragas_fx_w_hit` | view_effects `league_gragas_w_hit`（跟随，画在人物上面；左右对称） | 36 × 20 |
| `gragas_fx_q_barrel` | view_projectiles `league_gragas_q_barrel`（朝飞行方向转，画成朝右飞；上下对称） | 12 × 10 |
| `gragas_fx_q_land` | view_effects `league_gragas_q_land`（不跟随，画在人物下面一层；左右对称） | 14 × 14 |
| `gragas_fx_q_boom` | view_effects `league_gragas_q_boom`（不跟随，画在人物上面；左右对称） | 40 × 24 |
| `gragas_fx_q_hit` | view_effects `league_gragas_q_hit`（跟随，画在人物上面；左右对称） | 12 |
| `gragas_fx_q_slow` | view_buffs `league_gragas_q_slow`（跟随，画在人物下面；左右对称） | 16 × 6 |
| `gragas_fx_e_dust` | view_effects `league_gragas_e_dust`（不跟随，画在人物下面；左右对称） | 24 × 10 |
| `gragas_fx_e_hit` | view_effects `league_gragas_e_hit`（跟随，画在人物上面；左右对称） | 20 |
| `gragas_fx_e_stun` | view_buffs `league_gragas_e_stun`（跟随，画在人物上面；左右对称） | 14 × 6 |
| `gragas_fx_w_drink` | view_effects `league_gragas_w_drink`（跟随，画在人物上面；左右对称） | 20 × 16 |
| `gragas_fx_w_on` | view_buffs `league_gragas_w_on`（跟随，画在人物上面；左右对称） | 36 × 44 |
| `gragas_fx_p_heal` | view_effects `league_gragas_p_heal`（跟随，画在人物上面；左右对称） | 24 × 30 |
| `gragas_fx_r_cask` | view_projectiles `league_gragas_r_cask`（朝飞行方向转，画成朝右飞；上下对称） | 18 × 14 |
| `gragas_fx_r_boom` | view_effects `league_gragas_r_boom`（不跟随，画在人物上面；左右对称） | 56 × 36 |
| `gragas_fx_r_hit` | view_effects `league_gragas_r_hit`（跟随，画在人物上面；左右对称） | 14 |

- 两张表：`asset/league/effects/league_gragas_fx`（小的）和 `league_gragas_big`（w_hit、q_boom、r_cask、r_boom），tag = 名字（build_gragas.py 的 views）。
- `q_barrel`、`r_cask` 是抛物线（ParabolicProjectile），画面朝飞行方向转；`q_land`、`q_boom`、`r_boom`、`e_dust` 不跟随（落点 / 起步点）；`q_slow` 脚下 buff（z -1）；`w_on`、`e_stun` 画在人物上面（z 3），所以 `w_on` 中间必须是空的。
- 用 `pixel_1x/` 切格（import_viktor / import_seraphine 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
