# 虚空行者 卡萨丁：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图。** 造型和动作已定（`design/kassadin_idle.png`：游戏里的 3/4 正面待机）。他在游戏里是**高清**的（PPU：每个游戏格子里 3.62×3.62 个细像素，这张图就是高清造型放大 3 倍），连角 36 格高、31 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/kassadin_size.png`：待机放大 4 倍，长袍下摆在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/kassadin_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡萨丁自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**虚空的紫色光（白芯）和品红色火星**，法球和裂缝的中心是**深紫近黑的虚空**；Q 的护盾是冷一点的**蓝紫色外壳**。
> - **特效要亮**：每道光、每圈波纹都要有白色或最亮一档的芯，暗底上一眼能看见；深紫近黑只用在法球和裂缝的最里面。
> - **围着人的护盾、R 出现时的能量只画外圈和两边，中间人形位置留空**，不然会把人整个挡住（`r_out` 例外：他已经走了）。
> - **方向（重要，红色方不会镜像）**：飞出去的法球 `q_orb` 画成朝右飞；E 的冲击波 `e_cone` 是**一整片扇形的画面**：游戏把整张图从他（左端）铺到 42 格外（右端）、朝施放方向转，所以**画成朝右、左端是他**。这两张都要**上下对称**（往左放时会上下翻）。其余所有画面（打中、身上、脚下、头顶、裂缝）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kassadin_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `kassadin_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + W「虚空之刃」 | 带虚空能量的爪击；每 7 秒一次虚空刃强化普攻 | `a_hit` · `w_hit` |
| 技能 1 = Q「虚无法球」 | 向目标发射虚空法球，打断英雄；自己获得护盾 | `q_orb` · `q_hit` · `q_shield` · `q_sil` |
| 技能 2 = E「能量脉冲」 | 向前方扇形推出冲击波，打中的人减速 | `e_cone` · `e_hit` · `e_slow` |
| 大招 = R「虚空行走」 | 从原地消失、闪到敌方英雄身边，周围炸开 | `r_out` · `r_in` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、波纹、火星、光环、护盾都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 虚空紫光：`#FFFFFF`、`#F0DCFF`、`#CC96FF`、`#A055FF`、`#7426DC`、`#4A119A`；
  - 品红火星：`#FFFFFF`、`#FFD6F6`、`#FF80E2`、`#E632C6`、`#A8188E`；
  - 虚空深处（只用在最里面）：`#3A1466`、`#24093F`、`#140426`；
  - 护盾外壳（Q）：`#FFFFFF`、`#E2E6FF`、`#AEB8FF`、`#7280F4`、`#4248C6`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 24000，E 扇形半径 42000、张角约 80 度，R 爆炸半径 20000）。

### 1. `kassadin_fx_a_hit.png`：普攻打中（目标身上），4 帧

手上带着虚空能量的一记爪击：目标身上一个紫色的十字星光（白芯，参考 voidslash），外面几点品红火花。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A) and a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E).
Effect: a VOID CLAW HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a four-point violet star 12 squares across (long horizontal and vertical rays, white core); 3 the star thinner, 4 magenta sparks at mirrored places; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kassadin_fx_w_hit.png`：W 虚空之刃：强化普攻的虚空刃砍中（目标身上），5 帧

虚空之刃出鞘的一刀：两道又长又亮的紫色刀光交叉成 X（白芯、紫光、刀边一点品红，参考 voidblade_glow、W_blade_swirls），中心一团深紫的虚空裂口一闪，碎光往外飞。**左右对称**。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A), a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E) and a deep void ramp used only inside (#3A1466, #24093F, #140426).
Effect: a VOID BLADE SLASH on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 two long violet blade slashes crossing in an X 20 squares across, white cores, magenta edges; 3 the X at its brightest round a small black-violet rift 4 squares across in the middle; 4 violet shards flying out at mirrored places; 5 fading shards.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kassadin_fx_q_orb.png`：Q 虚无法球：飞出去的法球（朝目标飞，循环），4 帧

一颗虚空法球：中心是深紫近黑的虚空，外面一圈亮紫色的光环（白色亮边），后面拖一条短短的紫色尾迹和几颗品红火星（参考 OrbGlow、Q_ChargeMask、darkflame）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A), a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E) and a deep void ramp used only inside (#3A1466, #24093F, #140426).
Effect: a VOID ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a round orb 8 squares across - a black-violet heart 4 squares across inside a bright violet ring with a white rim - pulsing one square bigger and smaller; a short violet tail 4 squares long behind it to the left, tapering, with 2-3 magenta sparks (mirrored top to bottom).
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kassadin_fx_q_hit.png`：Q 打中（目标身上），5 帧

法球在目标身上炸开：一圈紫色的光环往外扩（白边），中心一团深紫虚空收缩，几颗品红火星溅开（参考 OrbGlow、VoidSwirl）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A), a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E) and a deep void ramp used only inside (#3A1466, #24093F, #140426).
Effect: a VOID ORB BURST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a violet ring 10 squares across round a black-violet heart; 3 the ring 16 squares across, white rim, the heart shrinking; 4 magenta sparks flying out at mirrored places, the ring breaking; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kassadin_fx_q_shield.png`：Q 自身护盾（他身上，约 1.5 秒），6 帧

放出法球时多余的能量包住自己：身体外面一层蓝紫色的护盾外壳（只画外轮廓的一圈弧线和几块六边形的亮片，像一个罩住全身的大椭圆的边），**中间人形位置留空**，一闪出现、闪几下、最后碎掉。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue shell ramp (#FFFFFF, #E2E6FF, #AEB8FF, #7280F4, #4248C6).
Effect: a SHIELD SHELL round a tall figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY (a clear upright area 26 squares wide and 36 tall in the middle): only the rim of a tall ellipse 34 squares wide and 42 tall round it - a thin violet-blue arc 2 squares thick with a white inner edge and a few small hexagon glints on it at mirrored places; 1 the rim faint and short (arcs at the shoulders only); 2-4 the whole rim bright, the glints twinkling in turn; 5 the rim cracking into pieces; 6 fading pieces.
Layout: one horizontal row of 6 equal 36:46 cells, image size 3456x736 (each cell 576x736, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kassadin_fx_e_cone.png`：E 能量脉冲：从他身前扇形推出去的冲击波（朝目标转向），6 帧

向前方扇形推出的一圈圈紫色冲击波（参考 Z_PraxisWave、EyeoftheStormSwipe）：**画成朝右**，左端是他，几道弧形的紫色波纹（白芯）从左往右扩散、越往右越宽（扇形，约 80 度张开），最后一帧在最远处散成光点。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A) and a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E).
Effect: a CONE OF FORCE WAVES pointing RIGHT, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): the picture's LEFT edge is where he stands, its RIGHT edge 42 squares away; the cone opens 40 degrees above and below the middle row (56 squares tall at the right end). Arc-shaped violet waves (2-3 squares thick, white cores, magenta trailing edges) curving like ripples: 1 a small arc 6 squares from the left; 2 that arc 16 squares out and a second one behind it; 3 three arcs spread over the cone; 4 the front arc near the right edge, the arcs widening with the cone; 5 the arcs thinning, sparks in the cone; 6 a few fading sparks at the far end.
Layout: one horizontal row of 6 equal 44:58 cells, image size 4224x928 (each cell 704x928, 16 px a square); the cone's tip on the LEFT edge of every cell, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kassadin_fx_e_hit.png`：E 打中（目标身上），4 帧

被冲击波打中：一圈扁的紫色波纹闪一下、中心白光，几道紫色短线往外跳。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A) and a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E).
Effect: a FORCE WAVE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a flat violet ring 12 squares wide and 6 tall with a white core; 3 short violet streaks jumping out at mirrored places; 4 fading streaks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kassadin_fx_e_slow.png`：E 减速（被减速的人脚下，循环），4 帧

脚下一圈紫色的虚空涟漪（从斜上方看的扁椭圆），几缕紫色细丝往下拽着（像被虚空拉住）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A) and a deep void ramp used only inside (#3A1466, #24093F, #140426).
Effect: a VOID RIPPLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse 16 squares wide and 5 tall - a dark violet pool with a bright violet rim - and 2-4 thin violet wisps at mirrored places rising one square and sinking again in turn.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kassadin_fx_q_sil.png`：沉默（被沉默的人头顶，循环），4 帧

E 打中后再被 Q 打中的英雄被沉默：头顶一个小小的紫色虚空符印（一个圆圈中间一道横杠，白芯），一闪一闪。**左右对称**。画在格子上部（人头上方）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A) and a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E).
Effect: a SILENCE SIGIL over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a violet ring 8 squares across with a horizontal bar through it, white cores, pulsing brighter and dimmer, two 1-square magenta sparkles at its sides.
Layout: one horizontal row of 4 equal 12:48 cells, image size 768x768 (each cell 192x768, 16 px a square); the sigil's middle 5 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kassadin_fx_r_out.png`：R 虚空行走：他消失的地方（留在原地），6 帧

他从原地消失：一道竖着的深紫色虚空裂缝撕开（中间近黑、边缘亮紫白光），紫色碎光往裂缝里吸进去，然后裂缝合上、留几点火星（参考 VoidSwirl、voidslash、VoidBackground）。**左右对称**。他已经走了，所以可以画满人形的位置。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A), a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E) and a deep void ramp used only inside (#3A1466, #24093F, #140426).
Effect: a VOID RIFT CLOSING where he stood, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a vertical white-violet slit 2 squares wide and 30 tall; 2 the slit opening into a tall black-violet rift 10 squares wide and 36 tall with a bright violet-white edge; 3 violet and magenta sparks streaming INTO the rift from both sides (mirrored); 4 the rift narrowing; 5 a thin slit again; 6 a few fading sparks.
Layout: one horizontal row of 6 equal 30:42 cells, image size 2880x672 (each cell 480x672, 16 px a square); centered across, the rift's bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kassadin_fx_r_in.png`：R 虚空行走：他出现的地方（落点，爆炸），7 帧

他从虚空里出来、周围炸开：先一道竖着的虚空裂缝，然后地上一圈扁椭圆的紫色冲击环往外炸开（约 40 格宽，白边），裂缝里冒出的紫色能量往上飘，最后散成光点（参考 VoidSwirl、PraxisWave、VoidBackground）。**左右对称**，**中间人形位置在第 3 帧以后留空**（他已经站在那）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A), a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E) and a deep void ramp used only inside (#3A1466, #24093F, #140426).
Effect: a VOID RIFT OPENING with a blast on the ground, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a vertical white-violet slit 2 squares wide and 30 tall; 2 a black-violet rift 10 squares wide with a bright edge; 3 the rift gone, the middle EMPTY (a clear upright area 24 squares wide and 36 tall where he now stands), a flat violet ring on the ground 20 squares wide and 7 tall with a white rim; 4 the ring at 40 x 13, violet wisps rising on both sides of the empty middle (mirrored); 5 the ring breaking into violet and magenta sparks; 6 sparks rising and fading; 7 a few embers.
Layout: one horizontal row of 7 equal 46:42 cells, image size 5152x672 (each cell 736x672, 16 px a square); centered across, the ground ring's middle 5 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kassadin_fx_r_hit.png`：R 打中（被炸到的人身上），4 帧

被虚空冲击打中：一团紫色碎光和品红火星溅在身上，中心一点深紫虚空一闪。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-light ramp (#FFFFFF, #F0DCFF, #CC96FF, #A055FF, #7426DC, #4A119A), a magenta ramp (#FFFFFF, #FFD6F6, #FF80E2, #E632C6, #A8188E) and a deep void ramp used only inside (#3A1466, #24093F, #140426).
Effect: a VOID BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 6 squares; 2 violet shards and magenta sparks bursting 12 squares across round a 2-square black-violet dot; 3 shards at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kassadin_fx_a_hit` | view_effects `league_kassadin_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `kassadin_fx_w_hit` | view_effects `league_kassadin_w_hit`（跟随，画在人物上面；左右对称） | 22 |
| `kassadin_fx_q_orb` | view_projectiles `league_kassadin_q_orb`（朝飞行方向转，画成朝右飞；上下对称） | 12 × 10 |
| `kassadin_fx_q_hit` | view_effects `league_kassadin_q_hit`（跟随，画在人物上面；左右对称） | 16 |
| `kassadin_fx_q_shield` | view_effects `league_kassadin_q_shield`（跟随，画在人物上面；左右对称） | 34 × 44 |
| `kassadin_fx_e_cone` | view_projectiles `league_kassadin_e_cone`（LineRangeProjectile 的画面：整张图从他（左端）铺到 42 格外（右端），朝施放方向转；上下对称） | 44 × 56 |
| `kassadin_fx_e_hit` | view_effects `league_kassadin_e_hit`（跟随，画在人物上面；左右对称） | 14 |
| `kassadin_fx_e_slow` | view_buffs `league_kassadin_e_slow`（跟随，画在人物下面；左右对称） | 16 × 6 |
| `kassadin_fx_q_sil` | view_buffs `league_kassadin_q_sil`（跟随，画在人物上面；左右对称） | 10 × 8 |
| `kassadin_fx_r_out` | view_effects `league_kassadin_r_out`（不跟随，画在人物上面；左右对称） | 28 × 40 |
| `kassadin_fx_r_in` | view_effects `league_kassadin_r_in`（不跟随，画在人物上面；左右对称） | 44 × 40 |
| `kassadin_fx_r_hit` | view_effects `league_kassadin_r_hit`（跟随，画在人物上面；左右对称） | 14 |

- 两张表：`asset/league/effects/league_kassadin_fx`（小的）和 `league_kassadin_big`（e_cone、r_out、r_in），tag = 名字（build_kassadin.py 的 views）。
- `q_orb` 是 TargetProjectile，画面朝飞行方向转；`e_cone` 是 LineRangeProjectile 的画面（从他铺到 42 格外）；`r_out`、`r_in` 不跟随；`e_slow` 脚下 buff（z -1）；`q_sil` 头顶（z 3）；`q_shield` 跟随画在人物上面，中间必须是空的。
- 用 `pixel_1x/` 切格（import_gragas / import_irelia 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
