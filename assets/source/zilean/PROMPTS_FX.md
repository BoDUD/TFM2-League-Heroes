# 时光守护者 基兰：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型已定（`design/zilean_design.png`，8 倍，A2_40，40 格），动作帧也做好了。
> - 大小对照 `design/zilean_size.png`：定稿造型放大 4 倍，脚尖在红色脚底线上，上面是 10 格一段的刻度，右边是原版道士。基兰 35×40 格（时钟屋顶到脚尖 40 格），原版英雄约 33–36 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里基兰自己的特效贴图（多数是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行（炸弹和爆炸、钟形圆圈、电弧和拖尾、指针/减速/沙粒/光柱/瓶子拖尾；炸弹那张是别的皮肤的，只看圆形炸弹的样子，颜色按金色），只在本地用，不要提交。颜色按下面写的色阶：**时间的光（爆炸、电弧、钟形圆圈、法球）用亮青色，钟、炸弹、符文、瓶子用金色，时光发条的减速用紫色**，和英雄联盟一样。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **钟形圆圈要像钟**：英雄联盟基兰的时间圈是一圈细细的亮环，外面一圈 12 个短刻度（像没有数字的钟面）；炸弹是圆的金色炸弹，正面一个小钟面。
> - 特效照下面第 1–19 条和「所有特效图的规则」画，每张一个 PNG，文件名 `zilean_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块。**
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`zilean_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「瓶中时光」 | 时光法球；每 90 秒攒一瓶，下次加速友军时送给他（他和基兰各得属性） | `zilean_fx_a_orb` · `zilean_fx_a_cast` · `zilean_fx_a_hit` · `zilean_fx_p_bottle` |
| 技能 1 = Q「定时炸弹」+ W「穿梭未来」 | 炸弹抛到目标脚下，粘在第一个敌人身上（没粘到就落在地上），3 秒后爆炸；W 好了时炸弹粘上英雄就倒转时间再扔一颗，两颗立刻爆炸并眩晕 | `zilean_fx_q_cast` · `zilean_fx_q_bomb` · `zilean_fx_q_bomb_on` · `zilean_fx_q_bomb_ground` · `zilean_fx_q_boom` · `zilean_fx_q_boom2` · `zilean_fx_q_hit` · `zilean_fx_q_stun` · `zilean_fx_w_rewind` |
| 技能 2 = E「时光发条」 | 减速一个敌方英雄，同时加速身边一个友方英雄 | `zilean_fx_e_cast` · `zilean_fx_e_slow` · `zilean_fx_e_haste` |
| 大招 = R「时光倒流」 | 给有危险的友军（或自己）挂 5 秒时光符文，不会阵亡；结束时回溯回血 | `zilean_fx_r_cast` · `zilean_fx_r_rune` · `zilean_fx_r_rewind` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、圆圈、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的第四档，第五档（最深）只给很少的点缀。
- 颜色（按每条写的用）：
  - 时间青（爆炸、电弧、钟形圆圈、法球）：`#FFFFFF`、`#D8FFFF`、`#7FF4FF`、`#2FC8E8`、`#1A7FB0`；
  - 钟金（炸弹、钟、符文、瓶子）：`#FFFFFF`、`#FFF2B0`、`#FFD24A`、`#E39A1E`、`#9C5A10`；
  - 减速紫（时光发条减速）：`#FFFFFF`、`#EAD8FF`、`#B98CFF`、`#7B4BF0`、`#4724A8`。
- **飞行类特效朝右画，而且上下对称**（普攻法球 `a_orb`）：游戏会把它转到飞行方向，朝左飞时整张会上下翻转。炸弹 `q_bomb` 是圆的，居中画。
- 命中、爆炸居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（减速、加速、符文、眩晕）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `zilean_fx_a_orb.png`：普攻：飞出去的时光法球（飞行中循环），4 帧

基兰的普攻：一颗青白色的小时光球朝右飞，后面拖一小段青色光尾，尾巴里有一两粒金色的火星。上下对称（飞向左边时会上下翻转）。约 10 格长、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0) and a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10).
Effect: a small FLYING TIME ORB moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round glowing head 4-5 squares across (white core, light-cyan rim) at the front (right), a short tapering cyan tail behind it to the left, one or two tiny gold sparks flickering in the tail.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the orb on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `zilean_fx_a_cast.png`：普攻出手：手上的青色闪光（施法者身上），4 帧

普攻出手：手掌前一个青色的小光点一闪。只画闪光，不画人。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a SMALL CYAN FLASH at a hand, 4 frames: 1 a white point; 2 a four-pointed cyan star with a white core; 3 the star wider and thinner, a few cyan specks; 4 fading specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `zilean_fx_a_hit.png`：普攻命中，4 帧

时光球打中：一个青白色的小星形光闪，带一点金色火星。约 12 格，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0) and a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10).
Effect: a SMALL TIME HIT, 4 frames: 1 a white flash at the center; 2 a four-pointed light-cyan star; 3 the star wider and thinner, a few cyan and gold sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `zilean_fx_q_cast.png`：Q 出手：手上的金色闪光（施法者身上），4 帧

定时炸弹出手：举起的手上方一个金色和青色的小闪光（炸弹本身另一张画）。只画闪光。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a SMALL FLASH at a raised hand, 4 frames: 1 a white point; 2 a gold four-pointed star with a white core and a thin cyan ring; 3 the ring wider, gold sparks flying up; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `zilean_fx_q_bomb.png`：Q 定时炸弹：飞行中的炸弹（抛物线飞，循环），4 帧

定时炸弹在空中飞：圆形的金色炸弹（金色外壳、一圈深一点的金带、正面一个白色小钟面和一根青色指针、顶上短短的引信冒一点青色火花）。炸弹是圆的，游戏转方向时看起来一样。指针每帧转一格、引信的火花闪。约 9 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: the TIME BOMB (a round golden bomb 7-8 squares across: a gold shell with a darker gold band, a small white clock face on its front with one cyan hand, a tiny cyan spark on a short fuse at the top) flying, 4 frames, a seamless loop: the clock hand turns a quarter each frame, the fuse spark flickers, a few cyan sparks trailing behind it to the LEFT. Keep the bomb round and centered so it looks the same when the game turns it.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the bomb centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `zilean_fx_q_bomb_on.png`：Q 炸弹粘在单位身上（倒计时，循环），4 帧

炸弹粘在敌人身上倒计时：画面中间是金色的炸弹（同上一张），周围一圈青色的钟形光环（12 个小刻度）跟着闪，指针在转，表示快要爆了。中间那一块就是炸弹，不要画人。约 14 格见方，居中画（导入时放到目标胸口的高度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: the TIME BOMB (a round golden bomb 7-8 squares across: a gold shell with a darker gold band, a small white clock face on its front with one cyan hand, a tiny cyan spark on a short fuse at the top) stuck on a target (do NOT draw the target), 4 frames, a seamless loop: the bomb in the middle, the clock hand turning a quarter each frame, round it a CLOCK RING (League's time circle: a thin bright ring with 12 short tick marks round it, like a clock face without numbers) in light cyan 12-14 squares across that pulses (bright in frames 1 and 3, fainter in 2 and 4), the fuse spark flickering.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `zilean_fx_q_bomb_ground.png`：Q 炸弹落在地上倒计时 3 秒，12 帧

没粘到人的炸弹落在地上：地上一个青色的钟形圆圈（从斜上方看的椭圆，宽是高的 2 倍，12 个刻度，像英雄联盟里定时炸弹的地面提示圈），圈中间放着金色的炸弹，指针在转、引信在闪；最后两帧圈和炸弹一起变亮（快爆了）。约 28 格宽、14 格高，圈的中心在格子底部往上 5 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: the TIME BOMB (a round golden bomb 7-8 squares across: a gold shell with a darker gold band, a small white clock face on its front with one cyan hand, a tiny cyan spark on a short fuse at the top) lying on the ground, 12 frames (the game loops frames 1-10, then 11-12 just before it blows): on the ground round it a CLOCK RING (League's time circle: a flat ellipse twice as wide as tall with 12 short tick marks round it, like a clock face without numbers) in light cyan, about 28 squares wide, centered 5 squares above the bottom of the cell; the bomb in its middle; frames 1-10: the hand turning, the fuse flickering, the ring's ticks lighting one after another round it; frames 11-12: the ring and the bomb flash bright white-cyan.
Layout: one horizontal row of 12 equal cells, each 2 wide to 1 tall, image size 3072x192 (each cell 256x128). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `zilean_fx_q_boom.png`：Q 爆炸（单颗炸弹），7 帧

定时炸弹爆炸（伤害半径约 30 格）：白色闪光，然后一圈青白色的星爆光环（像英雄联盟的 Q_Nova），地上一个青色的钟形圆圈一闪扩散，几道青色的电弧和金色碎片飞出去（参考 Q_Nova、Q_Clock_01、Q_Flash_02、Q_Arcs）。约 56 格宽、34 格高，爆炸中心在格子底部往上 12 格（脚底线的位置在中心下面 5 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0) and a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10).
Effect: a TIME BOMB EXPLOSION, 7 frames: 1 a white flash at the center; 2 a round burst of light cyan with a white core; 3 a jagged starburst ring of light cyan expanding (League's nova: a ring with spiky edges), a CLOCK RING (League's time circle: a thin bright ring with 12 short tick marks round it, like a clock face without numbers) flat on the ground under it flashing; 4 the ring at full size, 4-5 thin cyan lightning arcs and a few gold bomb shards flying out; 5 the ring thinner and breaking; 6 sparks and fading arcs; 7 a few last sparks.
Layout: one horizontal row of 7 equal cells, each 8 wide to 5 tall, image size 2240x280 (each cell 320x200); the explosion centered 12 squares above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `zilean_fx_q_boom2.png`：QWQ 双炸弹爆炸（带眩晕），8 帧

两颗炸弹同时爆炸（会眩晕范围里的敌人）：比上一张更大更亮，白色闪光后是金色和青色两层星爆光环，地上金色的钟面圆圈（12 个刻度、两根指针）亮起来，一圈青色电弧向外劈开（参考 Q_Nova、Q_Clock_02、Q_BoltsThin、Q_Flash_01）。约 64 格宽、40 格高，中心在格子底部往上 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0) and a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10).
Effect: a DOUBLE TIME BOMB EXPLOSION, bigger and brighter than a single one, 8 frames: 1 a big white flash; 2 a white-cyan burst; 3 two starburst rings, a gold one inside a light-cyan one, expanding; a CLOCK RING (League's time circle: a gold clock face ring with two hands with 12 short tick marks round it, like a clock face without numbers) flat on the ground under it lighting up; 4 both rings at full size, 6-8 cyan lightning arcs crackling outward; 5 the arcs at their longest, gold sparks raining; 6 the rings thin and break; 7 fading arcs and sparks; 8 a few last sparks.
Layout: one horizontal row of 8 equal cells, each 8 wide to 5 tall, image size 2560x320 (each cell 320x200); the explosion centered 14 squares above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `zilean_fx_q_hit.png`：Q 每个被炸到的单位身上的小闪光，4 帧

被炸到：单位身上一个青色和金色的小火花闪一下。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0) and a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10).
Effect: a SMALL BLAST HIT, 4 frames: 1 a white point; 2 a cyan four-pointed star with a few gold specks; 3 wider, thinner; 4 fading specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `zilean_fx_q_stun.png`：QWQ 眩晕标记（头顶，1.25 秒，循环），6 帧

眩晕：被眩晕的敌人头顶三个小小的金色钟（各 4–5 格，白色钟面、黑色指针）绕着转，带一点青色火花（时间停住了的感觉）。中间是头，不要画人。约 18 格宽、10 格高，绕一个扁椭圆转，6 帧能无缝接上。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a STUN MARK over a head (do NOT draw the head), 6 frames, a seamless loop: three tiny golden clocks (each 4-5 squares: a gold rim, a white face, a dark hand) spaced round a flattened ellipse (twice as wide as tall) circling it, moving a third of the way to the next one over the 6 frames, a few cyan sparks between them.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `zilean_fx_w_rewind.png`：W 穿梭未来：基兰身后倒转的大钟面，6 帧

穿梭未来：基兰身后亮起一个青色的大钟面圆圈（12 个刻度），两根金色指针飞快地倒着转（逆时针），一圈青色的光弧跟着往回卷，最后一帧收成光点散开（参考 Q_Clock_01、Skin05_W_ChronoRefresh 的月牙光）。中间是人，不要画人，钟面画在人身后（人会挡住中间）。约 40 格，中心在格子底部往上 17 格（人的胸口高度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0) and a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10).
Effect: a REWIND behind a figure (do NOT draw the figure), 6 frames: 1 a faint a CLOCK RING (League's time circle: a thin bright ring with 12 short tick marks round it, like a clock face without numbers) 36-40 squares across appears in light cyan; 2 it brightens, two gold clock hands in its middle start spinning BACKWARDS (counter-clockwise); 3 and 4 the hands spin fast (motion arcs of cyan light curling counter-clockwise inside the ring); 5 the ring flashes white; 6 the ring breaks into cyan and gold specks.
Layout: one horizontal row of 6 equal square cells, image size 1920x320 (each cell 320x320); the ring centered 17 squares above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `zilean_fx_e_cast.png`：E 出手：手上的紫色和青色闪光（施法者身上），4 帧

时光发条出手：手掌前一个紫色和青色的小钟形闪光（一个小圆圈带两根指针一闪）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a SMALL TIME WARP FLASH at a hand, 4 frames: 1 a white point; 2 a tiny clock ring (8 squares across) in light cyan with two violet hands; 3 the ring wider, violet and cyan sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `zilean_fx_e_slow.png`：E 减速：敌人身上的紫色慢转钟面（2.5 秒，循环），6 帧

时光发条减速敌人：敌人腰部一圈紫色的钟形光环（扁椭圆，宽是高的 2 倍，12 个刻度）慢慢倒着转，几粒紫色的光点往下飘（时间变慢）。中间是人，不要画人，中间留空。左右对称（人朝左朝右都用这张）。约 22 格宽、12 格高，6 帧能无缝接上。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8).
Effect: a SLOW MARK round a figure's waist (do NOT draw the figure; leave the middle empty), 6 frames, a seamless loop: a CLOCK RING (League's time circle: a flat ellipse twice as wide as tall with 12 short tick marks round it, like a clock face without numbers) in light violet round the middle of the cell, its ticks shifting slowly backwards (counter-clockwise) one step per frame, a few violet motes drifting downward; LEFT-RIGHT SYMMETRIC.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `zilean_fx_e_haste.png`：E 加速：友军脚下的金色和青色快转钟面（2.5 秒，循环），6 帧

时光发条加速友军：友军脚下一圈金色和青色的钟形光圈（地上的扁椭圆，12 个刻度）飞快地顺着转，几粒青色光点向上飞（时间变快）。左右对称（人朝左朝右都用这张）。约 24 格宽、10 格高，中心在格子底部往上 4 格，6 帧能无缝接上。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a HASTE RING at a figure's feet (do NOT draw the figure), 6 frames, a seamless loop: a CLOCK RING (League's time circle: a flat ellipse twice as wide as tall on the ground with 12 short tick marks round it, like a clock face without numbers) in gold with light-cyan ticks, its ticks running fast clockwise (two steps per frame), small cyan motes rising from it; LEFT-RIGHT SYMMETRIC.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the ellipse centered 4 squares above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `zilean_fx_p_bottle.png`：被动瓶中时光：送给友军的时间瓶，6 帧

瓶中时光：友军头顶出现一个金色的小瓶子（沙漏形，金色瓶框、里面青色发光的沙），瓶子一闪，沙子化作一道金色和青色的光往下流进人身上，最后散成光点（参考 P_Recourse_Trail、P_LvlUp_BeamUp）。不要画人。约 12 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a TIME BOTTLE over a head (do NOT draw the figure), 6 frames: 1 a small gold sparkle at the top of the cell; 2 a tiny hourglass-shaped bottle (6 squares tall: a gold frame, glowing cyan sand inside) appears; 3 the bottle glows bright; 4 it tips and pours a stream of gold-and-cyan light downward; 5 the stream reaches the bottom of the cell, the bottle fading; 6 a few gold and cyan specks.
Layout: one horizontal row of 6 equal cells, each 2 wide to 3 tall, image size 1536x768 (each cell 256x384); the bottle near the top of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `zilean_fx_r_cast.png`：R 施放：基兰脚下的金色符文钟，5 帧

时光倒流施放：基兰脚下亮起一个金色的符文钟（地上的扁椭圆，外圈 12 个刻度、里面一圈小符文），然后向上升起一道金色的光。约 36 格宽、16 格高，中心在格子底部往上 5 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a CHRONOSHIFT CAST at a figure's feet (do NOT draw the figure), 5 frames: 1 a gold point on the ground; 2 a CLOCK RING (League's time circle: a flat gold ellipse twice as wide as tall on the ground with 12 short tick marks round it, like a clock face without numbers) with an inner ring of tiny cyan glyphs, about 34 squares wide; 3 it shines, a column of gold light rising from it; 4 the column fades upward; 5 the ring fades.
Layout: one horizontal row of 5 equal cells, each 2 wide to 1 tall, image size 1600x400 (each cell 320x160); the ellipse centered 5 squares above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `zilean_fx_r_rune.png`：R 时光符文：挂在友军身上 5 秒的钟（循环），8 帧

时光倒流的符文：受保护的友军头顶上方浮着一个金色的钟（白色钟面、金色外框、两根青色指针），指针慢慢转，钟下面垂下一圈淡淡的金色光环罩着这个人（参考 Skin05_R_tar_Object、Q_Clock_02）。中间是人，不要画人，人的位置留空。约 26 格见方：钟在格子上半部（约 10 格），光环往下罩到格子底部。8 帧能无缝接上。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10) and a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0).
Effect: a CHRONOSHIFT RUNE over a figure (do NOT draw the figure; leave its place empty), 8 frames, a seamless loop: a golden clock 10 squares across floating in the top part of the cell (a gold rim with 12 ticks, a white face, two cyan hands turning slowly - the long hand a quarter round over the 8 frames), under it a faint thin gold ring hanging round the figure's place down to the bottom of the cell, a few gold motes drifting up.
Layout: one horizontal row of 8 equal square cells, image size 2048x256 (each cell 256x256). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `zilean_fx_r_rewind.png`：R 回溯：符文结束时的倒流加回血，8 帧

时光倒流回溯：受保护的友军身上，一个大的青色钟面圆圈（12 个刻度）一闪，两根金色指针飞快倒转，然后一道青白色的光柱从脚下升起，金色和青色的光点向上飘（回血）。不要画人，人的位置留空。约 32 格宽、40 格高，钟面的中心在格子底部往上 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, rings or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright cyan ramp (#FFFFFF, #D8FFFF, #7FF4FF, #2FC8E8, #1A7FB0) and a gold ramp (#FFFFFF, #FFF2B0, #FFD24A, #E39A1E, #9C5A10).
Effect: a REWIND REVIVAL on a figure (do NOT draw the figure), 8 frames: 1 a white flash at the figure's chest; 2 a CLOCK RING (League's time circle: a thin bright ring with 12 short tick marks round it, like a clock face without numbers) 28-30 squares across in light cyan appears round it; 3 two gold hands spin backwards inside it; 4 the hands spin fast, cyan motion arcs curling counter-clockwise; 5 the ring flashes white and a column of white-cyan light rises from the bottom of the cell; 6 the column at its brightest, gold and cyan motes rising; 7 the column and ring fading; 8 a few rising motes.
Layout: one horizontal row of 8 equal cells, each 4 wide to 5 tall, image size 2048x320 (each cell 256x320); the ring centered 18 squares above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `zilean_fx_a_orb` | view_projectiles `league_zilean_a_orb`（朝右，游戏转到飞行方向） | 10 × 7 |
| `zilean_fx_a_cast` | view_effects `league_zilean_a_cast`（施法者身上，跟随；导入时放到手的位置） | 10 |
| `zilean_fx_a_hit` | view_effects `league_zilean_a_hit`（跟随） | 12 |
| `zilean_fx_q_cast` | view_effects `league_zilean_q_cast`（施法者身上，跟随；导入时放到举起的手的位置） | 12 |
| `zilean_fx_q_bomb` | view_projectiles `league_zilean_q_bomb`、`q_bomb2`（游戏转到飞行方向） | 9 × 9 |
| `zilean_fx_q_bomb_on` | view_effects `league_zilean_q_bomb_on`（跟随目标，每 30 tick 播一次，4 帧正好 0.5 秒） | 14 × 14 |
| `zilean_fx_q_bomb_ground` | view_effects `league_zilean_q_bomb_ground`（地上，不跟随；Claude 把循环帧排满 3 秒） | 28 × 14 |
| `zilean_fx_q_boom` | view_effects `league_zilean_q_boom`（地上，不跟随；大图） | 56 × 34 |
| `zilean_fx_q_boom2` | view_effects `league_zilean_q_boom2`（地上，不跟随；大图） | 64 × 40 |
| `zilean_fx_q_hit` | view_effects `league_zilean_q_hit`（跟随） | 12 |
| `zilean_fx_q_stun` | view_effects `league_zilean_q_stun`（跟随，画在头顶；Claude 把循环帧排满 1.25 秒） | 18 × 10 |
| `zilean_fx_w_rewind` | view_effects `league_zilean_w_rewind`（施法者身上，跟随，画在人后面；大图） | 40 × 40 |
| `zilean_fx_e_cast` | view_effects `league_zilean_e_cast`（施法者身上，跟随；导入时放到手的位置） | 12 |
| `zilean_fx_e_slow` | view_buffs `league_zilean_e_slow`（跟着目标，画在人上面） | 22 × 12 |
| `zilean_fx_e_haste` | view_buffs `league_zilean_e_haste`（跟着友军，画在脚下） | 24 × 10 |
| `zilean_fx_p_bottle` | view_effects `league_zilean_p_bottle`（跟随友军，画在头顶） | 12 × 18 |
| `zilean_fx_r_cast` | view_effects `league_zilean_r_cast`（施法者身上，跟随，画在脚下；大图） | 36 × 16 |
| `zilean_fx_r_rune` | view_buffs `league_zilean_r_rune`（跟着目标，画在人上面；大图；Claude 把循环帧排满 5 秒） | 26 × 26 |
| `zilean_fx_r_rewind` | view_effects `league_zilean_r_rewind`（跟随，画在人上面；大图） | 32 × 40 |

- `a_cast` / `q_cast` / `e_cast` 放到动作帧里手的位置（普攻第 5 帧、Q 第 4 帧举起的手、E 第 4 帧）；`q_bomb_on` 每 30 tick 播一次（4 帧 × 125 ms），放在目标胸口；`q_bomb_ground` 前 10 帧循环排满 3 秒、最后两帧在爆炸前；`q_boom` 伤害半径 30000、`q_boom2` 同半径更亮；`q_stun`、`e_slow`、`e_haste`、`r_rune` 循环帧排满各自的时长（1.25 秒、2.5 秒、2.5 秒、5 秒）；`w_rewind`、`r_cast` 画在施法者身上（人后面 / 脚下）。
- 清掉 Codex 给光和圆圈描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
