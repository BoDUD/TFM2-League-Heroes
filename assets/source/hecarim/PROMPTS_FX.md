# 战争之影 赫卡里姆：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已定（`design/hecarim_design.png`，66×45 格，8 倍）。
> - 大小对照 `design/hecarim_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人（普通英雄的大小：命中特效按它画）。每条写的大小都是游戏像素（格）。
> - `design/hecarim_shots.png`：普攻砍下、Q 横扫、E 冲锋、E 砸下、R 扬蹄、R 冲锋那几帧的动作（4 倍），青色十字是脚下中心——他是半人马，身体很宽，**围着他的特效都以这个十字左右对称**。
> - 参考图：`refs/lol_icons.png` 是英雄联盟里他的 Q、E、R 技能图标——**颜色照它**；`refs/lol_fx_ref.png` 是他自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行。两张都只在本地用。
> - 颜色：**他的灵能全是幽灵青绿色，白色的芯**（和他眼睛、胸口裂纹一个颜色）；暗影烟用暗石板灰（只做点缀和 R 的幽灵刀身）；E 的尘土用灰褐色。
> - **特效要亮**：每个形状都要有白色或最亮一档的芯，暗底上一眼能看见；最深的一档颜色只给很少的点缀。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。R 的幽灵骑兵会转到冲锋方向，所以**朝右画、上下对称**（从上往下看）。E 的撞击是**竖着的画面**（碎石往上飞），上下不能颠倒。
> - 特效照下面第 1–17 条和「所有特效图的规则」画，每张一个 PNG，文件名 `hecarim_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - **最好直接交游戏尺寸的 1 倍条**（一格 = 一个游戏像素，每张另存 `hecarim_fx_<名字>_1x.png`，附 `manifest.json` 写每张的格子大小和锚点，卡尔玛那次就是这样交的）；生图原稿（半透明边、格子比例不准）也可以一起交，Claude 会读回。每张保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`hecarim_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 长柄刀砍 | `hecarim_fx_a_hit` |
| 技能 1 = Q「暴走」 | 挥刀转一圈（半径 26 格），打中东西叠层（最多 2 层），层数越多伤害越高 | `hecarim_fx_q_spin` · `hecarim_fx_q_hit` · `hecarim_fx_q1` · `hecarim_fx_q2` |
| W「恐惧之灵」（自动） | 身边有敌方英雄时放 Q/E/R 自动开启：4 秒里每秒烧周围敌人（半径 30 格）、给自己回血、加护甲魔抗 | `hecarim_fx_w_start` · `hecarim_fx_w_aura` · `hecarim_fx_w_hit` |
| 技能 2 = E「毁灭冲锋」 | 冲向敌人，冲得越久越疼，最后一刀砸下把敌人击退，之后加速 | `hecarim_fx_e_dust` · `hecarim_fx_e_ride` · `hecarim_fx_e_hit` · `hecarim_fx_e_haste` |
| 大招 = R「暗影冲击」 | 带一群幽灵骑兵冲过去（穿过的敌人都受伤），落地时周围的敌人被恐惧（半径 26 格） | `hecarim_fx_r_cast` · `hecarim_fx_r_riders` · `hecarim_fx_r_hit` · `hecarim_fx_r_land` · `hecarim_fx_r_fear` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火花、烟、灵气没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。暗影烟（暗石板灰）只占一小部分，旁边一定有亮青绿色。
- 颜色（按每条写的用）：
  - 幽灵青绿（所有技能）：`#FFFFFF`、`#E0FFFA`、`#A4FAEE`、`#50F0DC`、`#28C8B4`、`#148C82`、`#005A5A`；
  - 暗影烟（W 幽灵、R）：`#5A6672`、`#3C4650`、`#262E36`、`#161B20`；
  - 尘土（E）：`#E6DCC8`、`#C2B496`、`#9A8C70`、`#6E644E`；
- **飞行的画面朝右画，而且上下对称**（`r_riders`）：游戏会把它转到冲锋方向，往左时整张会上下翻过来，所以骑兵是从上往下看的一排刀刃和灵火，不画侧面的马和人。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。`e_hit` 是竖着的画面（碎石往上飞），不能颠倒。
- 套在角色身上的特效（Q 层数、R 起手、W 灼烧、恐惧骷髅）：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 半径 26000，W 半径 30000，R 落地半径 26000，幽灵骑兵宽 24000）。

### 1. `hecarim_fx_a_hit.png`：普攻命中：长柄刀砍中的幽灵刀光（目标身上），4 帧

长柄刀砍中：一下白光，两道交叉成 X 的青绿色刀光（像他的刀刃划过），几颗青绿色火星往外溅。X 左右对称，居中画。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A).
Effect: a GLAIVE SLASH HIT, 4 frames: 1 a white flash 4 squares across; 2 two crossed slash streaks of ghost-teal light forming an X 12 squares across, white along their middles; 3 the streaks thinning, teal sparks flying out; 4 a few fading sparks. The X and the sparks are mirrored left and right. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `hecarim_fx_q_spin.png`：Q 暴走：身边转一圈的幽灵刀光（地上，围着他），6 帧

Q 他挥刀转一圈（伤害半径 26 格）：两道青绿色的刀光从他左右两边同时扫出去，沿着地上一个大椭圆（从斜上方看，宽 54 格、高 27 格）绕过前面合拢成一整圈，圈上掠过白色的刀锋高光，刀光扫过的地方带起一点灵火火星，然后整圈变细淡出（参考 Q_Swoosh_Framesheet、Q_Sharp_Ray）。**中间留空**（他站在中间），圈的后半段（上面那一段，会压在他身上）画细、断开、淡一些，前半段（下面那一段）最亮最粗。左右对称（两道刀光一左一右镜像）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A).
Effect: A SPINNING GLAIVE SWEEP round a figure standing in the middle (do NOT draw the figure; leave the inside EMPTY), seen from above at an angle, 6 frames: an ellipse on the ground 54 x 27 squares; 1 two short crescent slashes of ghost-teal light starting at the left and right ends of the ellipse; 2 the two slashes sweeping forward along the ellipse's front (lower) half, white edges; 3 they meet at the front: a full bright crescent along the front half, 2-3 squares thick, and a thin broken arc along the back (upper) half; 4 the whole ring at its brightest, teal sparks flung outward; 5 the ring thinning; 6 fading sparks along the ring. The back (upper) arc always stays thin, broken and dimmer than the front. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 960x576 (image 5760x576) (16 px a square here); the ellipse's middle 15 squares (240 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `hecarim_fx_q_hit.png`：Q 命中：被刀光扫到（目标身上），4 帧

被 Q 扫到的每个敌人身上：一下白光，一道横着扫过的青绿色刀光（两头尖、中间宽、白芯），火星往两边溅，然后散掉。左右对称（刀光水平、两头一样），居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A).
Effect: a SWEEPING SLASH HIT, 4 frames: 1 a white flash 4 squares across; 2 a level slash of ghost-teal light 14 squares long, pointed at both ends and widest (3 squares) in the middle, white core; 3 the slash thinning, sparks flying off both ends; 4 a few fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `hecarim_fx_q1.png`：Q 层数 1：身体两侧各一团小幽灵火（循环），4 帧

Q 打中东西后叠一层（下一次 Q 伤害更高）：他马身的前后两头（离中心左右各 22 格、离脚底 14 格高）各一团小小的青绿色幽灵火（约 3 格宽 5 格高，白芯），火苗一跳一跳往上飘几颗火星。**中间空着**，只画这两团火，不要画人。左右对称。整格约 52 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A).
Effect: A LOOPING STACK MARK on a wide horse-like figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: two small ghost-teal flames, each 3 squares wide and 5 tall with a white core, one 22 squares LEFT and one 22 squares RIGHT of the middle, both 14 squares above the feet; they flicker and shed a mote upward each frame. Nothing else. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 896x512 (image 3584x512) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `hecarim_fx_q2.png`：Q 层数 2：身体两侧各两团更亮的幽灵火（循环），4 帧

Q 叠满两层：和层数 1 一样的位置，但每边两团火（离中心左右各 22 格和 15 格，离脚底 14 格和 20 格高），火更大更亮（约 4 格宽 6 格高），火星更多。**中间空着**。左右对称。整格约 52 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A).
Effect: A LOOPING FULL-STACK MARK on a wide horse-like figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: four ghost-teal flames, each 4 squares wide and 6 tall with a bright white core: on each side one 22 squares from the middle at 14 squares above the feet and one 15 squares from the middle at 20 squares above the feet; they flicker and shed two or three motes upward each frame. Nothing else. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 896x512 (image 3584x512) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `hecarim_fx_w_start.png`：W 恐惧之灵：开启时地上炸开一圈幽灵（地上），6 帧

W 开启（身边有敌方英雄时放 Q/E/R 自动开）：他脚下地上一圈青绿色的灵火往外扩到范围边（半径 30 格，从斜上方看的椭圆 60 × 30），圈边上冒出几个半透明的幽灵脸（骷髅一样的小鬼魂，青绿色的光勾出轮廓，往上飘 10 格），然后火圈变细、幽灵散成烟（参考 W_Ghoul_Swirl、W_Flame_Mult）。左右对称（两边的幽灵镜像）。**中间留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a few dark slate shadow-smoke shades (#5A6672, #3C4650, #262E36, #161B20).
Effect: A RING OF GHOSTS BURSTING OUT on the ground round a figure (do NOT draw the figure; leave the inside EMPTY), seen from above at an angle, 6 frames: 1 a flash of ghost-teal light at the middle 10 x 5 squares; 2 a ring of teal ghost-fire expanding to 36 x 18; 3 the ring at its full size (an ellipse 60 x 30 squares, 2 squares thick) with small flames along it; 4 four ghost faces (little skull-like wraiths, outlined in bright teal light, dark slate smoke inside) rising 10 squares from the ring, two on each side, mirrored; 5 the ring thinning, the wraiths higher and fading into smoke; 6 wisps and fading embers. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 1024x704 (image 6144x704) (16 px a square here); the ellipse's middle 16 squares (256 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `hecarim_fx_w_aura.png`：W 持续中：脚下一圈绕着转的幽灵（循环），4 帧

W 开着的 4 秒（每秒烧周围敌人、给他回血）：他脚下地上一圈细细的青绿色灵火圈（60 × 30 的椭圆，1 格粗），四团小幽灵（青绿色的小鬼火、带一点暗灰烟尾）沿着圈绕着走，左边两团和右边两团镜像着动。**中间留空**。不要太亮太满（要开 4 秒），但每个形状都有亮的芯。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a few dark slate shadow-smoke shades (#5A6672, #3C4650, #262E36, #161B20).
Effect: A LOOPING GHOST CIRCLE on the ground round a figure (do NOT draw the figure; leave the inside EMPTY), seen from above at an angle, 4 frames, a seamless loop: a thin ring of ghost-teal fire (an ellipse 60 x 30 squares, 1 square thick) with tiny flames along it; four small ghost wisps (teal heads with a bright core and a short dark slate smoke tail) travelling along the ring - two on the left half and two on the right half moving as mirror images. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 1024x544 (image 4096x544) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `hecarim_fx_w_hit.png`：W 灼烧：敌人身上被抽出一缕灵魂（目标身上），5 帧

W 每秒烧到的敌人身上：胸口一点青绿色的光，两缕青绿色的灵魂丝从身上左右两边绕出来、往上飘、散掉（像被抽走，参考 Wispy）。**中间空着**，不要盖住人。左右对称。约 12 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A).
Effect: A SOUL DRAIN on a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a small teal glow 3 squares across at the middle; 2 two thin wisps of ghost-teal soul-light curling out from the left and right of the middle; 3 the wisps rising and curling inward above, white tips; 4 the wisps higher, thinning; 5 a few fading motes at the top. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 224x320 (image 1120x320) (16 px a square here); the glow 7 squares (112 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `hecarim_fx_e_dust.png`：E 毁灭冲锋：起步时蹄下扬起的尘土（地上），5 帧

E 起步：他起跑的地上猛地扬起一片灰褐色的尘土，往左右两边翻开，里面夹几颗青绿色的灵火火星，然后尘土落下淡出（参考 E_GroundSmoke02、E_Rocks_2X2）。左右对称（尘土往两边一样翻）。约 32 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a grey-brown dust ramp (#E6DCC8, #C2B496, #9A8C70, #6E644E).
Effect: A DUST KICK-UP on the ground, 5 frames: 1 two puffs of grey-brown dust bursting out at the ground point, 8 squares across; 2 the dust rolling out to both sides, 22 squares wide, 8 high, a few teal sparks in it; 3 the cloud at full size (32 x 14 squares), small pebbles flying; 4 the dust settling and thinning; 5 a few fading dust wisps. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 576x256 (image 2880x256) (16 px a square here); the ground point 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `hecarim_fx_e_ride.png`：E 冲锋中：蹄下的幽灵火和尘土（循环），4 帧

冲锋的那一段：他四只蹄子下面一片青绿色的幽灵火在舔地，两边翻起小团灰褐色的尘土，几道短短的青绿色速度线（**左右两边一样**，游戏不会左右翻，不能只往后吹）。只画蹄下的一片。左右对称，从斜上方看的椭圆。约 42 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a grey-brown dust ramp (#E6DCC8, #C2B496, #9A8C70, #6E644E).
Effect: LOOPING CHARGE FIRE at a galloping figure's hooves (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 42 x 10 squares of ghost-teal flames licking the ground, small grey-brown dust puffs rolling off both ends, a few short teal streak-lines on both sides; the flames and puffs change every frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 704x192 (image 2816x192) (16 px a square here); the ellipse's middle at the middle of every cell (the hooves). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `hecarim_fx_e_hit.png`：E 撞击：一记重击把敌人撞飞（目标身上），5 帧

E 冲到敌人面前一刀砸下（敌人被击退）：一下大白光，一圈青绿色的冲击波往外一炸，碎石和尘土往左右两边飞起来，青绿色的灵火往上蹿，然后散成烟和碎石落下（参考 E_Spear_Impact_Diust_burst、E_Shield_Slam_Glow）。竖着的画面（碎石往上飞），上下不能颠倒。左右对称。约 22 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A), a grey-brown dust ramp (#E6DCC8, #C2B496, #9A8C70, #6E644E) and dark slate smoke (#5A6672, #3C4650, #262E36, #161B20).
Effect: A HEAVY SMASH IMPACT, UPRIGHT (debris flies up; never upside down), 5 frames: 1 a big white flash 8 squares across; 2 a ring of ghost-teal shock 16 squares across bursting out, white rim; 3 rocks and grey-brown dust flung up and out to both sides, teal ghost-fire leaping 10 squares up from the middle; 4 the fire falling apart into dark slate smoke, rocks dropping; 5 smoke wisps and a few falling pebbles. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 384x352 (image 1920x352) (16 px a square here); the impact's middle 8 squares (128 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `hecarim_fx_e_haste.png`：E 加速：撞完后蹄下的幽灵风（循环），4 帧

撞完后的加速：他蹄下一片淡淡的青绿色光，几缕青绿色的风和光点绕着蹄子打转往上飘（不能只往一边吹）。只画蹄下。左右对称，从斜上方看的椭圆。约 40 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A).
Effect: LOOPING HASTE WISPS at a figure's hooves (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse of soft ghost-teal light 40 x 8 squares on the ground, small teal wisps and motes swirling round it and lifting off, brighter at the front. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 672x160 (image 2688x160) (16 px a square here); the ellipse's middle at the middle of every cell (the hooves). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `hecarim_fx_r_riders.png`：R 暗影冲击：和他一起冲出去的幽灵骑兵（朝右，从上往下看，循环），4 帧

R 他带着一群幽灵骑兵冲出去（穿过的敌人都受伤）。游戏会把这张转到冲锋方向，往左冲时整张上下翻过来，所以**从上往下看**画：一个朝右的楔形（箭头形）青绿色幽灵火团，前沿排成 V 字的五把黑色幽灵长柄刀刃（刀刃朝右，暗灰色的刀身、亮青绿色的刀边，像 R 技能图标里那些黑刀），中间那把在最前面；刀后面拖着长长的青绿色灵火和暗灰色的烟尾巴（参考 R 技能图标、R_Ult_AoE_03）。**朝右画，上下对称**。约 36 格长、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a few dark slate shadow-smoke shades (#5A6672, #3C4650, #262E36, #161B20).
Effect: A CHARGING WEDGE OF GHOST RIDERS seen FROM ABOVE, pointing RIGHT, 4 frames, a seamless loop: an arrowhead of ghost-teal spirit-fire 36 squares long and 24 tall; along its front edge five dark spectral glaive blades pointing right in a V formation (the middle one farthest right), each blade dark slate with a bright teal edge and a white glint; behind them long streaming tails of teal ghost-fire and dark slate smoke flowing left; the flames flicker from frame to frame. Symmetric above and below its middle line (it is seen from above).
Layout: one horizontal row of 4 equal cells, each 640x416 (image 2560x416) (16 px a square here); the wedge's middle line on the middle line of every cell, its tip near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `hecarim_fx_r_cast.png`：R 起手：他身边腾起幽灵火和暗影（他身上），5 帧

R 起手（他扬起前蹄嘶鸣、召出幽灵骑兵）：他身边一下青绿色的光，暗灰色的暗影烟从脚下往上翻涌，左右两边各蹿起一道青绿色的灵火，烟里浮出两三个骑兵的幽灵影子（青绿色轮廓），然后被风吹散。**中间空着**，不要盖住他。左右对称。约 56 格宽、46 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a few dark slate shadow-smoke shades (#5A6672, #3C4650, #262E36, #161B20).
Effect: SHADOWS RISING round a big figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a ghost-teal flash at the middle 12 squares across; 2 dark slate shadow smoke surging up from the ground round the figure, a column of teal ghost-fire leaping up on each side 30 squares high; 3 inside the smoke, on each side, a faint ghost rider silhouette outlined in bright teal (mirrored); 4 the smoke and fire torn apart upward, teal motes; 5 fading wisps. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 960x768 (image 4800x768) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `hecarim_fx_r_land.png`：R 落地：地面裂开、冲击波扩散（地上），6 帧

R 冲到终点落地（半径 26 格内的敌人被恐惧）：地上一下白光，一圈青绿色的冲击波往外扩到范围边（从斜上方看的椭圆 52 × 26），地面从中心裂开青绿色发光的裂纹，暗灰色的烟沿着圈翻起来，几块碎石跳起来，然后裂纹慢慢暗下去（参考 R_Cracks_V04、Shockwave、R_Ult_AoE_03）。左右对称。约 56 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A), a grey-brown dust ramp (#E6DCC8, #C2B496, #9A8C70, #6E644E) and dark slate smoke (#5A6672, #3C4650, #262E36, #161B20).
Effect: A GROUND SLAM SHOCKWAVE seen from above at an angle, 6 frames: 1 a white-teal flash at the middle 12 x 6 squares; 2 a ring of ghost-teal shock expanding to 30 x 15, glowing teal cracks splitting out from the middle; 3 the ring at its full size (an ellipse 52 x 26 squares, 2 squares thick, white rim), the cracks reaching it, a few rocks jumping up; 4 dark slate smoke rolling along the ring, the cracks still glowing; 5 the ring gone, the cracks dimming; 6 faint cracks and smoke wisps. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 960x544 (image 5760x544) (16 px a square here); the ellipse's middle 15 squares (240 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `hecarim_fx_r_hit.png`：R 骑兵穿过：暗影刀光（目标身上），4 帧

被幽灵骑兵穿过的敌人身上：两道交叉成 X 的暗影刀光——暗灰色的刀痕、亮青绿色的边——一下白光，火星和暗影烟往外散。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a few dark slate shadow-smoke shades (#5A6672, #3C4650, #262E36, #161B20).
Effect: a SHADOW SLASH HIT, 4 frames: 1 a white-teal flash 4 squares across; 2 two crossed slashes forming an X 14 squares across, each a dark slate streak with bright teal edges and a white glint; 3 the slashes breaking into teal sparks and dark smoke puffs; 4 a few fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `hecarim_fx_r_fear.png`：R 恐惧：头上冒出幽灵骷髅（目标身上），6 帧

被 R 落地吓到（恐惧，乱跑）的敌人：头顶上方冒出一个青绿色的幽灵骷髅（约 10 格宽 11 格高，黑眼窝、张着嘴、下面拖一条烟尾巴），从离脚底 30 格高处升到 36 格，周围几缕灵气打转，然后淡出。**下面空着**，不要画人。左右对称。整格约 18 格宽、46 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a spectral ghost-teal ramp (#FFFFFF, #E0FFFA, #A4FAEE, #50F0DC, #28C8B4, #148C82, #005A5A) and a few dark slate shadow-smoke shades (#5A6672, #3C4650, #262E36, #161B20).
Effect: A FEAR GHOST over a figure's head (do NOT draw the figure; leave the inside EMPTY), 6 frames: 1 a puff of teal mist 30 squares above the feet; 2 a ghost skull 10 squares wide and 11 tall forming in it: bright teal outline-light, pale teal face, dark slate eye sockets and an open screaming mouth, a wispy smoke tail below; 3 the skull at full brightness, two wisps circling it; 4 the skull rising to 36 squares above the feet; 5 the skull fading, the wisps thinning; 6 a few fading motes. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 288x736 (image 1728x736) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `hecarim_fx_a_hit` | view_effects `league_hecarim_a_hit`（跟随，画在人物上面） | 12 |
| `hecarim_fx_q_spin` | view_effects `league_hecarim_q_spin`（不跟随，画在人物上面；他脚下） | 54 × 27 |
| `hecarim_fx_q_hit` | view_effects `league_hecarim_q_hit`（跟随，画在人物上面） | 14 |
| `hecarim_fx_q1` | view_buffs `league_hecarim_q1`（循环，跟随，画在人物上面；Q 叠 1 层，8 秒） | 52 × 30 |
| `hecarim_fx_q2` | view_buffs `league_hecarim_q2`（循环，跟随，画在人物上面；Q 叠满 2 层，8 秒） | 52 × 30 |
| `hecarim_fx_w_start` | view_effects `league_hecarim_w_start`（不跟随，画在人物下面；他脚下） | 60 × 30 |
| `hecarim_fx_w_aura` | view_buffs `league_hecarim_w_aura`（循环，跟随，画在人物下面；4 秒） | 60 × 30 |
| `hecarim_fx_w_hit` | view_effects `league_hecarim_w_hit`（跟随，画在人物上面；每秒一次） | 12 × 18 |
| `hecarim_fx_e_dust` | view_effects `league_hecarim_e_dust`（不跟随，画在人物下面；起步的地方） | 32 × 14 |
| `hecarim_fx_e_ride` | view_buffs `league_hecarim_e_ride`（循环，跟随，画在人物下面；冲锋时） | 42 × 10 |
| `hecarim_fx_e_hit` | view_effects `league_hecarim_e_hit`（跟随，画在人物上面） | 22 × 20 |
| `hecarim_fx_e_haste` | view_buffs `league_hecarim_e_haste`（循环，跟随，画在人物下面；2 秒） | 40 × 8 |
| `hecarim_fx_r_riders` | view_projectiles `league_hecarim_r_riders`（循环，朝飞行方向转；和他同速冲过去） | 36 × 24 |
| `hecarim_fx_r_cast` | view_effects `league_hecarim_r_cast`（不跟随，画在人物上面；起手的地方） | 56 × 46 |
| `hecarim_fx_r_land` | view_effects `league_hecarim_r_land`（不跟随，画在人物下面；落地点） | 56 × 30 |
| `hecarim_fx_r_hit` | view_effects `league_hecarim_r_hit`（跟随，画在人物上面） | 14 |
| `hecarim_fx_r_fear` | view_effects `league_hecarim_r_fear`（跟随，画在人物上面；落地时被恐惧的敌人） | 16 × 14 |

- `league_hecarim_fx`（跟随的小图、buff）和 `league_hecarim_big`（大图：`q_spin`、`w_start`、`w_aura`、`r_riders`、`r_cast`、`r_land`）两张 sheet，和技能数据（tools/kit/build_hecarim.py）里写的一致。
- 他身上的 caster 画面在第一个 tick 之后播放时都不跟随（红色方的镜像问题），全部左右对称；`r_riders` 是 LinearProjectile 的 view（朝飞行方向转），起手的 `r_cast` 是 CasterViewEffect。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半；红蓝两边逐张量对称。
