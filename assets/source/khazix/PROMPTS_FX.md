# 虚空掠夺者 卡兹克：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型和动作已定（`design/khazix_design.png`，8 倍，连触角和翅膀 45 行、42 格宽）。
> - 大小对照 `design/khazix_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。卡兹克 42×45 格。每条写的大小都是游戏像素（格）。
> - `design/khazix_shots.png`：定稿动作（4 倍），青色十字是特效的起点（尖刺的出手点、脚下），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡兹克自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**虚空是洋红和紫色（被动、Q、R、进化）；尖刺和跃击的冲击是紫色闪电；爪痕是骨白色；W 回血是淡绿色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **围着人的烟雾、光环、火光只画外圈，中间留空**，不然会把人整个挡住。
> - **方向（重要）**：飞出去的尖刺画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。画在他身上、晚于技能开始播放的（`w_heal`、`p_ready`、`e_reset`、`evo`）和挂在他身上、脚下循环的（`ut`、`r_on`、`slow`）要**左右对称**；地上的落地冲击 `e_land` 上下左右都对称。
> - 特效照下面第 1–16 条和「所有特效图的规则」画，每张一个 PNG，文件名 `khazix_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`khazix_fx_done.zip`）放在 outputs 里，或放在 `outputs/khazix-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「无形威胁」 | 镰爪攻击；隐身后或几秒没出手，下一次攻击英雄附加魔法伤害并减速 | `a_hit` · `ut` · `p_ready` · `p_hit` · `slow` |
| 技能 1 = Q「品尝恐惧」 | 爪击；目标身边没有友军（孤立无援）时伤害更高 | `q_hit` · `q_iso_hit` |
| 技能 2 = E「跃击」→ W「虚空突刺」 | 跃向敌方英雄，落地造成伤害，再甩出尖刺（伤害、减速，自己在爆炸里回血） | `e_land` · `e_hit` · `w_spike` · `w_hit` · `w_heal` · `slow` |
| 大招 = R「虚空来袭」 | 隐身并加速，可以再用 1–2 次 | `r_cast` · `r_on` |
| 进化 | 5/8/11 级依次进化 Q、E、R；进化后的 E 击杀英雄刷新 | `evo` · `e_reset` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、爪痕、火星、闪电没有黑描边，也不要用最深的颜色给形状描一圈边**。只有飞出去的尖刺（一件实物）有 1 格深色描边（`#0B0814`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 虚空洋红（被动、Q、R、进化、减速）：`#FFFFFF`、`#FFD8FF`、`#F08CFF`、`#C04CE8`、`#7A22B8`、`#3A0E6A`；
  - 紫色闪电（落地冲击、尖刺爆炸、刷新）：`#FFFFFF`、`#E8E0FF`、`#B8A8FF`、`#7C6CF0`、`#4A3CB0`；
  - 骨白（爪痕）：`#FFFFFF`、`#FFF6F0`、`#F2DCD4`、`#C8A8A8`；
  - 淡绿（W 回血）：`#FFFFFF`、`#ECFFD8`、`#BCF08C`、`#72C84C`、`#2E7A28`；
  - 尖刺本体（紫色甲壳）：`#0B0814`、`#2A1A5C`、`#46309A`、`#6A4ED0`、`#9478F0`、`#F08CFF`、`#FFFFFF`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 23000，孤立判定半径 30000，跃击落地半径 22000，尖刺宽 6000、爆炸回血范围 30000）。

### 1. `khazix_fx_a_hit.png`：普攻镰爪砍中（目标身上），4 帧

镰爪砍中：一道斜着的骨白色爪痕，白色的芯，边上一点紫色的虚空碎光（参考 Q_Slash、Hit_Spark、bolts_HitEffect）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bone ramp (#FFFFFF, #FFF6F0, #F2DCD4, #C8A8A8) and a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a CLAW SLASH HIT, 4 frames: 1 a curved bone-white claw streak 12 squares long through the center (from the top right down to the bottom left), a white core; 2 the streak thinner, a magenta flash 4 squares across at its middle, small violet sparks flying out; 3 sparks scattering; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `khazix_fx_p_hit.png`：被动 无形威胁打中（目标身上），5 帧

无形威胁打出：一颗洋红色的尖星爆开，几缕紫色虚空火焰往上窜（参考 Q_impact、P_OuterRing、Flames2）。约 18 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a VOID BURST HIT, 5 frames: 1 a magenta-white sharp six-pointed star 10 squares across at the center; 2 the star bigger, a ring of magenta sparks 14 squares across; 3 three violet flame tongues licking up 8 squares from the center, the ring breaking into motes; 4 the flames thinner, motes drifting up; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `khazix_fx_ut.png`：被动 无形威胁就绪（他身上，循环），4 帧

无形威胁就绪：他胸前两侧各一团小小的洋红色虚空火光在跳（英雄联盟里是他爪子上的紫光；参考 P_Glow、P_InnerCore）。**左右对称**，**中间留空**（人在中间）。4 帧无缝循环。约 26 格宽、12 格高，两团火光各约 5 格，相距约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: two small VOID FLAMES around a figure's chest (do NOT draw the figure; leave its place empty), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: one magenta-white flame 5 squares across on each side, 16 squares apart, the middle 12 squares empty; each frame the flames flicker (taller, shorter) and 2 tiny motes rise from them.
Layout: one horizontal row of 4 equal 28:14 cells, image size 1792x224 (each cell 448x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `khazix_fx_p_ready.png`：被动就绪的提示（他头顶，一闪），5 帧

无形威胁刚就绪时，他头顶亮一下：一个洋红色的眼睛形状的闪光一闪而过（参考 NegaSparkle、Q_SingleEnemy_Indicator）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: an EYE-SHAPED GLINT, 5 frames, SYMMETRIC LEFT TO RIGHT: 1 a thin magenta horizontal line 6 squares long; 2 it opens into an almond-shaped eye 12 squares wide and 5 tall with a white slit pupil; 3 the eye glowing brightest, 4 short rays around it; 4 the eye closing; 5 a fading magenta dot.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `khazix_fx_q_hit.png`：Q 品尝恐惧打中（目标身上），4 帧

Q 打中：三道并排的斜爪痕（骨白芯、紫边）一齐划过（参考 Q_Slash、Q_Lightning02）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bone ramp (#FFFFFF, #FFF6F0, #F2DCD4, #C8A8A8) and a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a TRIPLE CLAW HIT, 4 frames: 1 three parallel diagonal claw streaks 12 squares long, 2 squares apart, white cores with violet edges; 2 the streaks thinner, a small magenta flash at the center; 3 the streaks breaking into violet sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `khazix_fx_q_iso_hit.png`：Q 打中孤立无援的目标（目标身上），6 帧

打孤立目标时更重的一击：三道大爪痕，后面炸开一颗大大的洋红尖星，一圈紫色的三叶形标记一闪（英雄联盟孤立目标头上的标记；参考 Q_impact、Q_SingleEnemy_Indicator02_Reticle、Q_Impact_04）。约 26 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bone ramp (#FFFFFF, #FFF6F0, #F2DCD4, #C8A8A8) and a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: an ISOLATED-TARGET CRUSHING HIT, 6 frames: 1 three big parallel diagonal claw streaks 18 squares long, white cores with magenta edges; 2 a magenta-white eight-pointed star 16 squares across bursting behind them; 3 a thin violet ring 22 squares across with three curved notches (a three-lobed reticle) flashing round the star; 4 the star shrinking, the ring brightest; 5 the ring fading into sparks; 6 fading sparks.
Layout: one horizontal row of 6 equal square cells, image size 2688x448 (each cell 448x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `khazix_fx_e_land.png`：E 跃击落地：地上的冲击（地上），6 帧

卡兹克从天而降落地：地上一圈紫色的冲击波往外扩，一圈碎土和紫色闪电往外溅（参考 E_Shockwave_1、E_SmokeErode、Z_VoidLightning）。从斜上方看，**冲击波是压扁的椭圆**，**上下左右都对称**。中间是人，不要画人。6 帧。约 40 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet lightning ramp (#FFFFFF, #E8E0FF, #B8A8FF, #7C6CF0, #4A3CB0) and a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a LANDING SHOCKWAVE on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM: 1 a bright violet-white flattened ellipse ring 14 squares wide and 5 tall; 2-4 the ring widening to 38 squares wide and 14 tall, thinner each frame, short violet lightning cracks and dust bits thrown out along it; 5 the ring faint, sparks settling; 6 a few fading sparks.
Layout: one horizontal row of 6 equal 42:18 cells, image size 4032x288 (each cell 672x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `khazix_fx_e_hit.png`：E 落地砍中（目标身上），4 帧

落地砍中：一道竖着劈下的骨白爪痕，紫色闪电在边上一跳（参考 E_glow、Q_Electric_Arcs）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bone ramp (#FFFFFF, #FFF6F0, #F2DCD4, #C8A8A8) and a violet lightning ramp (#FFFFFF, #E8E0FF, #B8A8FF, #7C6CF0, #4A3CB0).
Effect: a DOWNWARD CLAW HIT, 4 frames: 1 a vertical bone-white claw streak 14 squares tall through the center, a white core; 2 the streak thinner, 2 short violet lightning zigzags jumping off its sides; 3 the zigzags breaking into sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `khazix_fx_w_spike.png`：W 虚空突刺：飞出去的尖刺（飞行中，循环），4 帧

卡兹克甩出去的虚空尖刺：一根紫色甲壳质的尖刺，尖头朝右、发洋红色的光，后面拖一小段紫色的虚空光迹（参考 W_Spike、W_Mis_Front、W_Swirl_Core）。朝右飞。**上下对称**。4 帧无缝循环。约 16 格长、6 格高。

```text
Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, a 1-square dark outline #0B0814 around the object, colours only from the spike's violet chitin (#0B0814, #2A1A5C, #46309A, #6A4ED0, #9478F0, #F08CFF, #FFFFFF).
Effect: a VOID SPIKE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a sharp violet chitin spike 10 squares long and 3 tall, pointed at its RIGHT end with a magenta-white glowing tip, a short tapering violet glow trail 5 squares long behind it; the trail flickers and the tip glints each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); the spike's point 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `khazix_fx_w_hit.png`：W 尖刺炸开（目标身上），5 帧

尖刺炸开：一团紫色的虚空爆炸，几根小尖刺碎片往外飞，一圈洋红色的光（参考 W_Tar、W_VoidTentacles、shards）。约 20 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A) and a violet lightning ramp (#FFFFFF, #E8E0FF, #B8A8FF, #7C6CF0, #4A3CB0).
Effect: a VOID SPIKE BURST, 5 frames: 1 a violet-white flash 8 squares across at the center; 2 a magenta burst 16 squares across, 6 small violet spike shards flying outward; 3 the burst ring breaking up, the shards farther; 4 shards and motes fading; 5 a few motes.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `khazix_fx_w_heal.png`：W 在爆炸里回血（他身上），5 帧

卡兹克在尖刺的爆炸范围里回血：身边几缕淡绿色的光往上飘，几个小十字（参考 Default_Glow）。**左右对称**，**中间留空**（人在中间）。5 帧：1–2 从脚边升起，3–4 绕身体往上，5 头顶散开。约 22 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale green ramp (#FFFFFF, #ECFFD8, #BCF08C, #72C84C, #2E7A28).
Effect: HEALING WISPS around a figure (do NOT draw the figure; leave its place empty), 5 frames, SYMMETRIC LEFT TO RIGHT, the middle 10 squares left empty: 4 thin pale green wisps (2 squares wide, white highlights) and 4 small plus-shaped sparkles rising from the ground on both sides, fading above its head; each frame a step higher.
Layout: one horizontal row of 5 equal 24:32 cells, image size 1920x512 (each cell 384x512, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `khazix_fx_slow.png`：减速（目标脚下，循环），4 帧

被无形威胁或虚空突刺减速：脚下一圈紫色的虚空水洼，几缕紫雾往外散（参考 W_Tar、Z_Void）。**左右对称**。4 帧无缝循环。约 16 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a SLOWING VOID PUDDLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: a flat violet ellipse puddle 14 squares wide and 4 tall, 2 thin magenta ripple rings spreading out from it and tiny motes rising each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `khazix_fx_r_cast.png`：R 虚空来袭：隐身时炸开的虚空雾（他身上），6 帧

卡兹克隐身：身边炸开一团紫黑色的虚空烟雾，一圈洋红的光环往外扩，几片甲壳状的碎影散开（参考 R_Ring、R_End_Mult、R_Shed、smoke）。**左右对称**，**中间留空**（人在中间）。6 帧：1 光环亮起，2–4 烟雾炸开、光环扩大，5–6 烟雾散开淡去。约 34 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a VOID SMOKE BURST around a figure (do NOT draw the figure; leave its place empty), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly empty: 1 a thin magenta ring 16 squares across at the center; 2-4 the ring growing to 32 squares, puffs of dark violet and magenta smoke bursting out round it, small chitin-shaped flakes flying off; 5-6 the smoke thinning and fading upward.
Layout: one horizontal row of 6 equal 36:38 cells, image size 3456x608 (each cell 576x608, 16 px a square); the figure's place horizontally centered, its feet 3 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `khazix_fx_r_on.png`：R 隐身中（他身上，循环），4 帧

隐身中：他身体外面一圈淡淡的紫色波纹在闪，像空气被扭曲（参考 R_Evo2_Ring、R_Ring、Z_Void）。**左右对称**，**中间留空**（人在中间，游戏会把隐身的他画淡）。4 帧无缝循环。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a STEALTH SHIMMER outline around a figure (do NOT draw the figure; leave its place empty), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT, the middle 20 squares wide left empty: thin broken violet and magenta wavy lines (1 square thick) tracing a tall oval 28 squares wide and 38 tall, a few motes drifting up; each frame the lines shift and break in different places.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `khazix_fx_e_reset.png`：击杀刷新 E（他身上，一闪），5 帧

进化虫翼后击杀英雄刷新跃击：他身边一圈紫色光环收紧、一对翅膀形状的光闪一下（参考 Ring_Pickup、Lantern_Ring）。**左右对称**。约 24 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet lightning ramp (#FFFFFF, #E8E0FF, #B8A8FF, #7C6CF0, #4A3CB0) and a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A).
Effect: a RESET FLASH, 5 frames, SYMMETRIC LEFT TO RIGHT: 1 a violet ring 22 squares across; 2 the ring shrinking to 14, a pair of thin wing-shaped light streaks flaring out left and right; 3 the ring 8 across and brightest, a white core; 4 a white flash; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 2080x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `khazix_fx_evo.png`：进化（他身上），8 帧

进化：他身边卷起一团紫色和洋红的虚空漩涡往上收，几道紫色闪电，最后一下白光（参考 R_End_Mult 的漩涡、Z_VoidLightning、Magma_Flash）。**左右对称**，**中间留空**（人在中间）。8 帧：1–3 漩涡从脚下卷起，4–5 闪电，6 最亮的白光，7–8 散开。约 34 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFFFFF, #FFD8FF, #F08CFF, #C04CE8, #7A22B8, #3A0E6A) and a violet lightning ramp (#FFFFFF, #E8E0FF, #B8A8FF, #7C6CF0, #4A3CB0).
Effect: an EVOLUTION SURGE around a figure (do NOT draw the figure; leave its place empty), 8 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly empty: 1-3 a magenta-violet spiral of void energy rising from the ground round the figure's place, up to 36 squares high; 4-5 4 violet lightning bolts crackling along the spiral; 6 a white flash 20 squares across at the middle; 7-8 the energy bursting outward into motes and fading.
Layout: one horizontal row of 8 equal 36:42 cells, image size 4608x672 (each cell 576x672, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `khazix_fx_a_hit` | view_effects `league_khazix_a_hit`（跟随，画在人物上面） | 14 |
| `khazix_fx_p_hit` | view_effects `league_khazix_p_hit`（跟随，画在人物上面） | 18 |
| `khazix_fx_ut` | view_buffs `league_khazix_ut`（跟随，画在他身上，左右对称） | 26 × 12 |
| `khazix_fx_p_ready` | view_effects `league_khazix_p_ready`（不跟随，左右对称；中心在站位点上面约 36 格） | 16 |
| `khazix_fx_q_hit` | view_effects `league_khazix_q_hit`（跟随，画在人物上面） | 16 |
| `khazix_fx_q_iso_hit` | view_effects `league_khazix_q_iso_hit`（跟随，画在人物上面） | 26 |
| `khazix_fx_e_land` | view_effects `league_khazix_e_land`（落地点的地上，不跟随，不旋转） | 40 × 16 |
| `khazix_fx_e_hit` | view_effects `league_khazix_e_hit`（跟随，画在人物上面） | 16 |
| `khazix_fx_w_spike` | view_projectiles `league_khazix_w_spike`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 6 |
| `khazix_fx_w_hit` | view_effects `league_khazix_w_hit`（跟随，画在人物上面） | 20 |
| `khazix_fx_w_heal` | view_effects `league_khazix_w_heal`（不跟随，左右对称；中心在站位点上面约 16 格） | 22 × 30 |
| `khazix_fx_slow` | view_buffs `league_khazix_p_slow` 和 `league_khazix_w_slow`（同一张，画在脚下，左右对称） | 16 × 6 |
| `khazix_fx_r_cast` | view_effects `league_khazix_r_cast`（技能第一 tick 播放、跟随；中心在站位点上面约 16 格） | 34 × 36 |
| `khazix_fx_r_on` | view_buffs `league_khazix_r_on`（跟随，画在他身上，左右对称） | 30 × 40 |
| `khazix_fx_e_reset` | view_effects `league_khazix_e_reset`（不跟随，左右对称；中心在站位点上面约 20 格） | 24 |
| `khazix_fx_evo` | view_effects `league_khazix_evo`（不跟随，左右对称；中心在站位点上面约 18 格） | 34 × 40 |

- `w_spike` 从出手点出（甩刺那帧爪尖在站位点前面约 26 格、贴近地面；`y_offset` 定在 2000–6000，画面开头补几帧空的，让尖刺离开爪子再出现）。
- `r_cast` 在动作第一 tick 播放、跟随；`w_heal`、`p_ready`、`e_reset`、`evo` 晚于第一 tick，`is_follow` 为 false，左右对称；`e_land` 在地上，不跟随。`slow` 一张图给 `p_slow` 和 `w_slow` 两个 buff 用（tools/kit/build_khazix.py 的绑定改成同一个 tag）。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim`，尖刺保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；飞行的画面上下对称；Codex 交的如果是要求尺寸的 2 倍，缩一半。
