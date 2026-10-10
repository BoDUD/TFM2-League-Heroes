# 破败之王 佛耶戈：给 Codex 的特效提示词（第 3 步）

> **这一份是 25 张特效图**（最后 8 张 `s_*` 给附加包用）。造型和动作已定（`design/viego_design.png`，8 倍，连剑 51 行、51 格宽，头顶到脚底 42 行）。
> - 大小对照 `design/viego_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。佛耶戈连剑 51×51 格（人 42 行高）。每条写的大小都是游戏像素（格）。
> - `design/viego_shots.png`：定稿动作（4 倍），青色十字是特效的起点（剑尖、剑刺下去的地方、脚下），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里佛耶戈自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**破败的黑雾 = 他剑上的青绿色光（白芯）+ 暗青黑色的雾**，灵魂是苍白的青白色。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见；黑雾可以用深色，但**深色只在雾的里面，雾的边缘一定是亮的青绿色**。
> - **围着人的灵魂光、黑雾气、护壳只画外圈和两边，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的剑气、巨口、灵魂光弹（`q_thrust`、`w_maw`、`s_bolt`、`s_line`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻；巨口的上下颚对称张开）。画在人身上、脚下、头顶的（打中、标记、晕眩、黑雾气、夺魂、护壳、加速、治疗）都要**严格左右对称**（逐格对称，游戏不会给它们镜像；剑光画成对称的 X 或竖直的一道）；地上的 `e_mist`、`r_land`、`s_ring` 上下左右都对称。
> - 特效照下面第 1–25 条和「所有特效图的规则」画，每张一个 PNG，文件名 `viego_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`viego_fx_done.zip`）放在 outputs 里，或放在 `outputs/viego-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 大剑砍；Q 标记过的英雄被打中时补一剑并回血 | `a_hit` · `a_double` |
| 技能 1 = Q「破败王剑」 | 往前刺出一道剑气，穿过一条线上的人；刺中的英雄带标记 | `q_thrust` · `q_hit` · `q_marked` |
| 技能 2 = E「茫茫焦土」→ W「千载幽咽」 | 先放黑雾（加移速攻速、短暂隐身），再往前冲、喷出黑雾巨口，咬中第一个敌人并晕住 | `e_mist` · `e_on` · `w_maw` · `w_hit` · `w_stun` |
| 大招 = R「痛贯天灵」 | 跳到被围攻的敌方英雄身上一剑刺下，周围的人被击退 | `r_cast` · `r_hit` · `r_land` |
| 被动「君命已决」 | 打过的英雄死了就夺取它的灵魂：1 秒无敌、回血、附身 10 秒（黑雾气）；放大招结束附身 | `p_take` · `p_safe` · `p_on` · `p_end` |
| 附加包：附身后的技能 | 按被附身英雄的类型换一套技能：光弹、穿透射击、爆裂、身边一圈震荡、减速、治疗、加速 | `s_bolt` · `s_line` · `s_hit` · `s_burst` · `s_ring` · `s_slow` · `s_heal` · `s_haste` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、剑气、雾、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯；黑雾的里面可以暗，但边缘一定用亮的青绿色，一眼看得出形状。
- 颜色（按每条写的用）：
  - 青绿剑光（剑气、咬合、闪光、光环）：`#FFFFFF`、`#C8FFF6`、`#91F9F7`、`#60E7D6`、`#0AB79C`；
  - 破败黑雾（雾的身体：深色只在里面）：`#39D7C1`、`#03A188`、`#037C70`、`#03615B`、`#042D31`；
  - 苍白灵魂（夺魂、灵魂光弹、治疗）：`#FFFFFF`、`#EAF8F6`、`#B4F0E6`、`#7FD8CB`、`#3FA89C`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（25 张）

25 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 26000，Q 刺出 40000，W 巨口飞 42000，R 击退半径 18000，附身的震荡半径 20000）。

### 1. `viego_fx_a_hit.png`：普攻打中（目标身上），4 帧

大剑砍中：一个青绿色的 X 形剑光（两道对称的斜线交叉），中间白芯，再散出几颗光点（参考 Swipes、SwipeBase、graphicFlash）。**左右对称**（不要画成一道单向的斜砍）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a SWORD HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 two bright teal slash streaks crossing as an X, 10 squares across, white along their middles; 3 the X thinner with small sparks flying out at mirrored places; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `viego_fx_a_double.png`：Q 标记后的二连击打中（目标身上），5 帧

Q 标记过的敌人被普攻打中时，佛耶戈再补一剑并回血：先一个大的 X 剑光，接着一圈黑雾往外炸开，带几颗往上飘的苍白灵魂光点（回血）（参考 Swipes_BG、BA_Tar、SoulBits）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C), a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C).
Effect: a DOUBLE STRIKE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bright teal X slash 12 squares across, white cores; 2 a second, wider X over it and a white flash in the middle; 3 a ring of black mist puffs 14 squares across bursting out, bright teal edges; 4 the mist thinning, pale soul sparks rising at mirrored places; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `viego_fx_q_thrust.png`：Q 破败王剑：往前刺出的剑气（飞行中，循环），4 帧

Q 的突刺：一道朝右的青绿色剑气，最前面是尖的白色剑尖，后面拖一段越来越细的雾气光尾（参考 Q_Streak、Q_ball01、BA_spearNoise）。朝右飞。**上下对称**。4 帧无缝循环。约 16 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a SPECTRAL SWORD THRUST flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a sharp white-teal spear point at the right 4 squares long, a teal streak behind it 12 squares long tapering to the left, thin dark mist wisps along its top and bottom edges (mirrored); the wisps flicker frame to frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); the point's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `viego_fx_q_hit.png`：Q 刺中（每个被刺中的人身上），4 帧

Q 刺穿：一道横向的白青色光刺穿过目标（左右两头对称地伸出去），中间一团小的黑雾（参考 lightRay_Tar、energyRing）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a PIERCING HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a thin bright teal horizontal spike 14 squares wide through the middle (pointed at both ends), a small puff of black mist round its center; 3 the spike thinner, teal sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `viego_fx_q_marked.png`：Q 的标记（被刺中的英雄头顶，循环），4 帧

被 Q 刺中的英雄 4 秒内带着标记，下一次普攻会二连击：头顶一个小的青绿色荆棘王冠形状的光印（像佛耶戈的王冠，3 个尖），一闪一闪（参考 P_RuneShard、spiritGlow）。**左右对称**。4 帧无缝循环。约 12 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a THORN CROWN MARK over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small glowing teal crown shape 10 squares wide and 6 tall (a thin band with 3 sharp spikes, the middle one tallest), a white core along the band; it brightens and dims, 2 tiny sparks at mirrored places.
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `viego_fx_w_maw.png`：W 千载幽咽：喷出去的黑雾巨口（飞行中，循环），4 帧

W 的飞弹：一团朝右飞的黑雾，前端张开一张怪物的嘴——上颚和下颚**上下对称**地张开，边上一排尖牙，嘴里一点青白的光，后面拖黑雾尾巴（参考 W_Missile_Hound、MissileLead、mistTrail）。**上下对称**（不要画成侧面的狗头）。4 帧无缝循环。约 16 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a MIST MAW flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): at the right an open monster mouth made of black mist, its upper and lower jaws mirrored (each jaw 7 squares long with a row of 3 small pale-teal fangs), a teal glow deep in the mouth, the jaws' edges bright teal; behind it a ragged black mist trail 8 squares long to the left; the jaws open and close a little each frame (always mirrored).
Layout: one horizontal row of 4 equal 18:14 cells, image size 1152x224 (each cell 288x224, 16 px a square); the jaws' tips 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `viego_fx_w_hit.png`：W 咬中（被咬中的人身上），4 帧

黑雾巨口咬中：上下两排尖牙从上下往中间合拢（上下、左右都对称），咬合处一道白青色的闪光，再炸成一圈黑雾（参考 W_Missile_Hound、Mist）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a MAW BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an upper and a lower jaw of black mist (each 14 squares wide, a row of pale-teal fangs) apart at the top and bottom of the cell; 2 the jaws snapping together at the middle; 3 a white-teal flash line where they meet, black mist bursting out; 4 fading mist wisps.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `viego_fx_w_stun.png`：W 晕眩（被晕的人头顶，循环），4 帧

被巨口晕住：头顶绕着一圈扁扁的黑雾小幽魂（青绿色的边），几颗苍白的小光点在环上（参考 Wispy、spiritGlow）。**左右对称**（光点每帧换到对称的位置，不画朝一个方向转）。4 帧无缝循环。约 16 格宽、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C).
Effect: a DAZE HALO over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 16 squares wide and 5 tall of small black mist wisps with bright teal edges, 4 pale soul dots on it at mirrored places that step to new mirrored places each frame.
Layout: one horizontal row of 4 equal 18:9 cells, image size 1152x144 (each cell 288x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `viego_fx_e_mist.png`：E 茫茫焦土：他周围升起的黑雾（地上，画在人物下面），8 帧

W+E 起手时佛耶戈先放出黑雾：地上一大片从斜上方看的扁椭圆黑雾，边缘是一缕一缕往外卷的青绿色雾气，里面暗、边上亮（参考 Mist、E_Ground_Palette、E_Glow、E_Trail_4）。**上下左右都对称**。约 60 格宽、24 格高。帧 1–2 从中间涌出，3–6 雾边翻卷，7–8 淡去。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a BLACK MIST POOL on the ground seen from above at an angle, 8 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical cloud of dark teal mist 60 squares wide and 24 tall, curling teal wisps along its whole edge (bright), the inside dark with a few teal glints; 1-2 the mist spilling out from the center to full size; 3-6 the edge wisps curling (mirrored each frame); 7-8 thinning and fading.
Layout: one horizontal row of 8 equal 62:26 cells, image size 7936x416 (each cell 992x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `viego_fx_e_on.png`：E 黑雾里的加速（他脚边，循环），4 帧

黑雾里加移速、攻速：他脚边两侧缭绕着低低的黑雾，几缕青绿色的雾气往后飘（左右对称，中间脚的位置留空）（参考 mistTrailSoft、groundDust）。**左右对称**。4 帧无缝循环。约 26 格宽、10 格高，只在脚边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: LOW MIST round a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle 10 squares EMPTY (the feet): two drifts of black mist 8 squares wide and 6 tall at the left and right of the feet, bright teal wisp edges curling outward and upward, changing each frame.
Layout: one horizontal row of 4 equal 28:12 cells, image size 1792x192 (each cell 448x192, 16 px a square); centered across, the mist's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `viego_fx_p_take.png`：被动 君命已决：夺取灵魂（他身上），6 帧

击杀英雄后佛耶戈夺取灵魂：一股苍白的灵魂光从两边地面盘旋升起、汇向他的头顶，头顶闪一下白光，然后黑雾裹住他的两边（**中间人的位置留空**）（参考 SoulBits、soul_drops、passive_cloudRing、P_Decal）。**左右对称**（两股灵魂光对称地升起，不画单向的螺旋）。约 36 格宽、50 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C), a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a SOUL TAKEN round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (16 x 40 squares) EMPTY: 1 a pale glowing ellipse 30 squares wide on the ground; 2 two streams of pale soul light rising from it at the left and right sides, wavy; 3 the streams at shoulder height, bright, sparks; 4 they meet above the head in a white flash 8 squares across; 5 black mist with teal edges wrapping both sides of the figure; 6 the mist fading, a few soul sparks.
Layout: one horizontal row of 6 equal 38:52 cells, image size 3648x832 (each cell 608x832, 16 px a square); centered across, the ground ellipse on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `viego_fx_p_on.png`：附身中：他身上的黑雾气（循环），4 帧

附身期间佛耶戈身上冒着黑雾：身体两侧往上窜的黑雾火焰（青绿色的亮边），脚下一圈淡淡的雾，**中间人的位置留空**，不挡脸（参考 passive_cloudRing_edge、vertical_Wisp、edgeSmoke_Noise）。**左右对称**。4 帧无缝循环。约 34 格宽、46 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a POSSESSION AURA round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (16 x 40 squares) EMPTY: tongues of black mist with bright teal edges rising up both sides of the figure from a faint mist ring at the feet (30 x 8 squares), up to shoulder height, wisps breaking off at the top; the tongues change each frame (mirrored).
Layout: one horizontal row of 4 equal 36:48 cells, image size 2304x768 (each cell 576x768, 16 px a square); centered across, the feet ring's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `viego_fx_p_safe.png`：夺魂时无敌的 1 秒（他身上，循环），4 帧

夺取灵魂时 1 秒不受伤害：他周围一层细的苍白青光外壳（竖的椭圆，只画外圈），外圈上几颗闪光点（参考 spiritGlow、energyRing）。**中间留空、左右对称**。4 帧无缝循环。约 28 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a WARD SHELL round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY: an upright ellipse outline 26 squares wide and 40 tall, 1 square thick, pale teal with white glints at mirrored places that move to new mirrored places each frame.
Layout: one horizontal row of 4 equal 30:44 cells, image size 1920x704 (each cell 480x704, 16 px a square); the shell centered in every cell, its bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `viego_fx_p_end.png`：附身结束（他身上），5 帧

附身结束：裹在他身上的黑雾一下子往两边散开，几颗苍白的灵魂光点往上飘走（参考 Viego_Emote_Death_Dissolve、SmokeErode）。**中间留空、左右对称**。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C).
Effect: MIST LEAVING a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (14 x 36 squares) EMPTY: 1 black mist with teal edges on both sides of the figure; 2 the mist puffing outward; 3 the mist torn into wisps, pale soul sparks rising; 4 thin wisps and sparks high; 5 a few fading sparks.
Layout: one horizontal row of 5 equal 32:42 cells, image size 2560x672 (each cell 512x672, 16 px a square); centered across, the bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `viego_fx_r_cast.png`：R 痛贯天灵：起跳（他脚下），5 帧

R 起跳：他脚下一圈黑雾往外喷，中间一道往上的青白光（参考 R_Flash、groundDust）。**左右对称**，只在脚边。约 24 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a LEAP PUFF at a figure's feet, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat white-teal flash 10 squares wide on the ground; 2 black mist puffs bursting out to both sides, 20 squares wide, a thin teal light line rising in the middle; 3 the puffs 24 wide; 4 thinning; 5 fading wisps.
Layout: one horizontal row of 5 equal 26:14 cells, image size 2080x224 (each cell 416x224, 16 px a square); centered across, the bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `viego_fx_r_hit.png`：R 落下刺中（目标身上），6 帧

R 落地刺穿目标：一道竖直的青白色剑光从上往下刺进目标，落点炸开一个碎裂的光（像心碎），再喷出一圈黑雾（参考 R_Comet、R_Tar_Impact、R_OnKillRay）。**左右对称**（剑光竖直居中）。约 30 格宽、38 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a HEART-PIERCING STAB, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin white-teal vertical blade of light 4 squares wide striking down the middle from the top, 30 squares tall; 2 the blade brightest, a white flash 10 squares across at its foot; 3 the flash breaking into sharp teal shards flying out at mirrored places; 4 black mist bursting out 26 squares wide with teal edges; 5 the mist thinning, shards fading; 6 fading wisps.
Layout: one horizontal row of 6 equal 32:40 cells, image size 3072x640 (each cell 512x640, 16 px a square); the blade centered across, its foot 6 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `viego_fx_r_land.png`：R 落地冲击（地上，画在人物下面），6 帧

R 落地把周围的人击退：地上从斜上方看的一圈扁椭圆冲击波，外圈是青绿色的光环，里面裂开的黑色焦土和往外冲的黑雾（参考 R_Decal、R_PraxisWaves、R_decalBase）。**上下左右都对称**。这是击退的范围（半径 18 格），约 44 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a LANDING SHOCKWAVE on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a white-teal flash 10 squares wide at the center; 2 a bright teal ring 22 squares wide, dark cracked ground inside; 3 the ring 34 wide, black mist rushing outward; 4 the ring 44 wide and 18 tall; 5 the ring thinner, mist wisps; 6 fading.
Layout: one horizontal row of 6 equal 46:20 cells, image size 4416x320 (each cell 736x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `viego_fx_s_bolt.png`：附身技能：灵魂光弹（飞行中，循环），4 帧（附加包）

附身远程/法师英雄后的普攻和技能：一颗苍白青色的灵魂光球，后面拖一小段黑雾尾巴（参考 Q_ball01、mistTrail）。朝右飞。**上下对称**。4 帧无缝循环。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a SOUL BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a pale white-teal orb 4 squares across at the right, a short black mist trail with teal edges 6 squares long behind it, flickering.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `viego_fx_s_line.png`：附身技能：穿透的灵魂射击（飞行中，循环），4 帧（附加包）

附身射手后的穿透射击：一道细长的苍白青色光箭，前尖后细，两边各一缕黑雾（参考 Q_Streak、generalTrail）。朝右飞。**上下对称**。4 帧无缝循环。约 18 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a PIERCING SOUL SHOT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a long thin pale-teal bolt 18 squares long, a white pointed head at the right, thin black mist wisps along its top and bottom (mirrored), flickering.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); the head's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `viego_fx_s_hit.png`：附身技能打中（目标身上），4 帧（附加包）

附身技能打中：一小团苍白青光炸开，带一点黑雾（参考 graphicFlash、Wispy）。**左右对称**。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a SOUL HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale white flash 4 squares across; 2 a pale teal burst 8 squares across with black mist puffs round it; 3 sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `viego_fx_s_burst.png`：附身法师技能：灵魂爆裂（目标身上），5 帧（附加包）

附身法师后的 Q：目标处一团大的苍白灵魂光爆开，一圈黑雾往外冲（参考 R_Flash、Mist）。**左右对称**。约 24 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C), a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a SOUL BLAST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across; 2 a round pale-teal blast 18 squares across; 3 a ring of black mist with teal edges 24 squares across bursting out; 4 the ring thinning, sparks; 5 fading wisps.
Layout: one horizontal row of 5 equal square cells, image size 2080x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `viego_fx_s_ring.png`：附身战士/辅助技能：身边一圈震荡（地上，画在人物下面），6 帧（附加包）

附身战士、坦克、辅助后的范围技能：他脚下从斜上方看的一圈扁椭圆光环往外扩，带黑雾（参考 RingMult、passive_cloudRing）。**上下左右都对称**。范围半径 20 格，约 44 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C) and a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades).
Effect: a SOUL RING on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a teal ellipse 12 squares wide; 2 the ring 24 wide, black mist inside; 3 the ring 36 wide; 4 the ring 44 wide and 18 tall, brightest; 5 thinner, mist wisps; 6 fading.
Layout: one horizontal row of 6 equal 46:20 cells, image size 4416x320 (each cell 736x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `viego_fx_s_slow.png`：附身技能的减速（被减速的人脚下，循环），4 帧（附加包）

被附身技能减速：脚下一圈细的黑雾环，青绿色亮边，环里有往中间收的短线（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black mist ramp (#39D7C1, #03A188, #037C70, #03615B, #042D31; its darkest shades only inside the mist, every edge in the lighter shades) and a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a MIST SLOW RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin black mist ellipse 14 squares wide and 4 tall with a bright teal edge, 4 short inward ticks at mirrored places sliding toward the center each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `viego_fx_s_heal.png`：附身辅助的治疗（被治疗的友军身上，循环），4 帧（附加包）

附身辅助后治疗友军：人身两边往上飘的苍白青色小光点和小十字（左右对称，中间留空）（参考 Dance_Heal_Fire_Trail、SoulBits）。**左右对称**。4 帧无缝循环。约 18 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale soul ramp (#FFFFFF, #EAF8F6, #B4F0E6, #7FD8CB, #3FA89C).
Effect: HEALING MOTES round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle 8 squares EMPTY: small pale-teal plus signs (3 squares) and dots rising at mirrored places on both sides, each frame 2 squares higher, new ones appearing at the bottom.
Layout: one horizontal row of 4 equal 20:26 cells, image size 1280x416 (each cell 320x416, 16 px a square); centered across, the bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. `viego_fx_s_haste.png`：附身技能的加速（他脚下，循环），4 帧（附加包）

附身辅助/刺客后的加速：脚下一圈细的青绿色光环，两边各几道往外的短光线（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, slashes or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea-green teal light ramp (#FFFFFF, #C8FFF6, #91F9F7, #60E7D6, #0AB79C).
Effect: a SPEED RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin teal ellipse 16 squares wide and 4 tall, 2 short horizontal light dashes on each side at mirrored places sliding outward each frame.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `viego_fx_a_hit` | view_effects `league_viego_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `viego_fx_a_double` | view_effects `league_viego_a_double`（跟随，画在人物上面；左右对称） | 16 |
| `viego_fx_q_thrust` | view_projectiles `league_viego_q_thrust`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 6 |
| `viego_fx_q_hit` | view_effects `league_viego_q_hit`（跟随；左右对称） | 14 |
| `viego_fx_q_marked` | view_buffs `league_viego_q_marked`（跟随；左右对称） | 12 × 8 |
| `viego_fx_w_maw` | view_projectiles `league_viego_w_maw`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 12 |
| `viego_fx_w_hit` | view_effects `league_viego_w_hit`（跟随；左右对称） | 16 |
| `viego_fx_w_stun` | view_buffs `league_viego_w_stun`（跟随；左右对称） | 16 × 7 |
| `viego_fx_e_mist` | view_effects `league_viego_e_mist`（施法时，不跟随，画在人物下面；上下左右都对称） | 60 × 24 |
| `viego_fx_e_on` | view_buffs `league_viego_e_on`（跟随，画在人物上面；左右对称） | 26 × 10 |
| `viego_fx_p_take` | view_effects `league_viego_p_take`（跟随，画在人物上面；左右对称） | 36 × 50 |
| `viego_fx_p_on` | view_buffs `league_viego_p_on`（跟随，画在人物上面；左右对称） | 34 × 46 |
| `viego_fx_p_safe` | view_buffs `league_viego_p_safe`（跟随，画在人物上面；左右对称） | 28 × 42 |
| `viego_fx_p_end` | view_effects `league_viego_p_end`（跟随，画在人物上面；左右对称） | 30 × 40 |
| `viego_fx_r_cast` | view_effects `league_viego_r_cast`（跟随，画在人物上面；左右对称） | 24 × 12 |
| `viego_fx_r_hit` | view_effects `league_viego_r_hit`（跟随，画在人物上面；左右对称） | 30 × 38 |
| `viego_fx_r_land` | view_effects `league_viego_r_land`（落点上，不跟随，画在人物下面；上下左右都对称） | 44 × 18 |
| `viego_fx_s_bolt` | view_projectiles `league_viego_s_bolt`（朝飞行方向转；上下对称） | 10 × 6 |
| `viego_fx_s_line` | view_projectiles `league_viego_s_line`（朝飞行方向转；上下对称） | 18 × 6 |
| `viego_fx_s_hit` | view_effects `league_viego_s_hit`（跟随；左右对称） | 10 |
| `viego_fx_s_burst` | view_effects `league_viego_s_burst`（跟随，画在人物上面；左右对称） | 24 |
| `viego_fx_s_ring` | view_effects `league_viego_s_ring`（跟随，画在人物下面；上下左右都对称） | 44 × 18 |
| `viego_fx_s_slow` | view_buffs `league_viego_s_slow`（画在脚下；左右对称） | 16 × 6 |
| `viego_fx_s_heal` | view_buffs `league_viego_s_heal`（跟随，画在人物上面；左右对称） | 18 × 24 |
| `viego_fx_s_haste` | view_buffs `league_viego_s_haste`（画在脚下；左右对称） | 18 × 6 |

- 两张表：`asset/league/effects/league_viego_fx`（小的）和 `league_viego_big`（e_mist、p_take、p_on、r_hit、r_land、s_burst、s_ring），tag = 名字（build_viego.py 的 views）。
- `q_thrust`、`w_maw`、`s_line` 是直线飞的（line），`y_offset` 4000；`s_bolt` 是追踪弹：画面开头补一帧空的（追踪弹第一 tick 朝上）。
- `e_mist`、`r_land` 不跟随、画在人物下面（z -1）；`s_ring` 跟随、z -1；`e_on`、`p_on`、`p_safe` 是 buff 循环，画在人物上面（z 3），所以中间必须是空的。
- 用 `pixel_1x/` 切格（import_viktor / import_seraphine 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
