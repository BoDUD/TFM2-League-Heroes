# 希尔科：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图 + 3 个技能图标。** 造型已定（`design/silco_design.png`：拄着黑手杖、举着微光药剂瓶的祖安化工男爵，往后梳的黑发、橙红伤疤眼，洋红衬衫、金边棕马甲）。希尔科在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），40 格高、22 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/silco_size.png`：希尔科缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里希尔科自己的特效贴图（**灰色的形状，游戏里再染色**：微光液体、化学气体、黏液、护盾），按用在我们哪张特效分好了行；`refs/monstrosity_35.png` / `_90.png` / `_0.png` 是金铲铲里他的**畸变体**模型（一条粗短的紫色蠕虫，前端一张圆嘴、一圈金色尖牙，嘴上面一只粉色小眼睛）。只在本地用。
> - **希尔科是祖安的化工男爵，特效都是他的炼金术**：发光的洋红**微光**液体和蒸汽、有毒的**化学绿**气体、凹凸不平的铜铁储罐、紫色的畸变体；不要光滑的霓虹光束，不要火。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、气体、液体没有黑描边**（畸变体、储罐、药剂瓶这些实物可以有一圈深色描边）。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：除了弹道和 `m_bite`，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道 `a_vial`、`q_can`、`r_can` 朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。`m_bite` 是畸变体咬在人的左边，**不对称**（我导入时左右翻转一份当右边那只）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `silco_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入）；图标交付 `silco_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/silco_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/silco_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「统领」 | 每次出生 / 复活得到一层护盾；每放一次技能叠一层法强，叠满 5 层头顶亮起伤疤眼印记 | `p_shield` · `p_dom` |
| 普攻 | 甩出一支微光药剂瓶 | `a_vial` · `a_hit` |
| 技能 1 =「罐装畸变体」 | 扔一个储罐，砸地炸开，放出 2 只畸变体扑到附近的敌人身上连咬几口，咬死了就跳到下一个 | `q_can` · `q_warn` · `q_burst` · `m_leap` · `m_bite` · `m_die` |
| 技能 2 =「微光注射」 | 把药剂瓶抛给身边攻击力最高的队友（没有就自己）：攻速、移速提高，药效过去掉一点血 | `e_dose` · `e_shimmer` · `e_crash` |
| 大招 =「炼金狂潮」 | 扔一个巨型储罐：地上预警，砸地大爆炸，放出 4 只畸变体，地上留一片减速的微光毒雾 | `r_can` · `r_warn` · `r_burst` · `r_fog` · `r_slow` · `m_*` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、气体、液体没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 微光（洋红）：`#FFF0FF`、`#FF9CF4`、`#E848DC`、`#A824B4`、`#5C1070`；
  - 化学绿：`#F2FFD8`、`#BEF26A`、`#78CC34`、`#3E8A22`、`#1C4412`；
  - 铜铁（储罐）：`#FFDCA4`、`#D88E44`、`#9A5A24`、`#5A3214`、`#2C1A0C`；
  - 畸变体的紫色：`#D8C8FF`、`#9A84F0`、`#6A50C8`、`#42288E`、`#22104C`；
  - 畸变体的金牙：`#FFF6C8`、`#F0C850`、`#B0882A`；
  - 灰绿烟雾：`#E4ECD8`、`#AEBE98`、`#76866A`、`#46523E`；
  - 金色（图标边框）：`#FFE9A8`、`#E2B85A`、`#B08530`、`#7A5418`、`#42280A`；
- 打中、爆炸居中画，不旋转；地面上的圈（落点、预警圈、冲击圈、毒雾）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `silco_fx_a_vial.png`：普攻：飞出去的微光药剂瓶，4 帧循环

他甩出去的**微光药剂瓶**：一支横着飞的小玻璃瓶，铜盖朝前（右边），瓶里发光的洋红液体在晃，后面拖两三滴紫色的液滴。**朝右飞，上下对称**，4 帧循环（液体的高光来回晃）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C).
Effect: A FLYING SHIMMER VIAL, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a small glass vial lying along the flight (8 squares long, 3 tall), its copper cap at the FRONT (right), glowing magenta liquid inside with a white highlight, two or three magenta droplets trailing 3 squares behind it; frames 1-4 the highlight sliding back and forth in the liquid. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 12:6 cells, image size 768x96 (each cell 192x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `silco_fx_a_hit.png`：普攻：药剂瓶打中，4 帧

药剂瓶在人身上碎开：一下洋红的闪光，玻璃碎片和紫色液体往两边溅开，冒一点点紫烟。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E).
Effect: A SHATTERING VIAL, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a magenta-white flash 6 squares across; 2 tiny white glass shards and magenta droplets bursting out to both sides (mirrored) 12 across; 3 droplets falling, a small puff of purple vapour in the middle; 4 the vapour fading. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `silco_fx_q_can.png`：罐装畸变体：飞出去的储罐，4 帧循环

他扔出去的**储罐**：一个小铁皮罐（铜色的箍、中间一扇发绿光的玻璃窗，窗里隐约有个扭动的影子），横着翻滚着飞。**朝右飞，上下对称**，4 帧循环（窗里的绿光一明一暗）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C), a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C).
Effect: A THROWN CANISTER, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a small metal canister lying along the flight (9 squares long, 7 tall), dark iron ends with copper bands, one round glowing GREEN GLASS WINDOW in its middle with a dim violet squirming shape behind it; frames 1-4 the window's green glow pulsing brighter and dimmer, a thin green vapour wisp trailing from the left end. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 12:10 cells, image size 768x160 (each cell 192x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `silco_fx_q_warn.png`：罐装畸变体：地上的落点，4 帧循环

储罐要落下的地方：地上一圈细细的**绿色化学警示圈**（从斜上方看的椭圆），圈里几点绿色光斑。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E).
Effect: A TARGET MARK, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a thin dashed ring of chemical green light 22 squares wide and 7 tall, four small brighter green ticks at its left, right, front and back; frames 1-4 the dashes running round and the ticks blinking. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 26:10 cells, image size 1664x160 (each cell 416x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `silco_fx_q_burst.png`：罐装畸变体：储罐炸开，7 帧

储罐砸到地上炸开：铜色的碎铁片往两边飞，一团**翻滚的绿色化学气体**冲起来，洋红的液体溅开（畸变体本身是另外的图）。砸的地方在格子底部往上 4 格。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070).
Effect: A BURSTING CANISTER, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the burst sits on the ground line 4 squares above the bottom. 1 a white-green flash 10 squares across; 2 jagged copper and iron shards flying out to both sides (mirrored), a round billow of chemical GREEN GAS 18 across rising; 3 the gas 30 across and 20 tall, magenta Shimmer splashes thrown to both sides, a green ring 34 wide and 8 tall on the ground; 4 the gas at its biggest (36 x 26), shards falling; 5-6 the gas thinning into rolling grey-green puffs; 7 a few last wisps. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 7 equal 40:34 cells, image size 4480x544 (each cell 640x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `silco_fx_m_leap.png`：畸变体：扑到人身上，5 帧

一只**畸变体**（参考 `refs/monstrosity_*.png`：一条粗短的紫色蠕虫，前端一张圆嘴、一圈金色尖牙，嘴上面一只发光的粉色小眼睛）从高处扑下来：圆嘴张开朝下，落到人的头肩上（最后一帧落到头顶的高度，溅开一点紫色黏液）。**正面看，左右对称**；身体位置留空。5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C), a gold teeth ramp (#FFF6C8, #F0C850, #B0882A), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070).
Effect: A POUNCING MONSTROSITY, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: a MONSTROSITY: a stubby violet GRUB about 9 squares long and 6 thick (darker violet back, paler belly), its front end one big ROUND MOUTH ringed with GOLD fangs, a small glowing PINK eye above the mouth (refs monstrosity_*.png), seen from the front, its round mouth wide open and pointing DOWN; 1 it appears at the top of the cell curled up; 2-3 it drops straight down the middle, stretching out, the mouth gaping; 4 it lands on the top of the unit's head (the top 12 squares of the cell), a small splash of violet slime; 5 it squashes down, fangs clamped, slime drops falling at mirrored places. The middle below the head left empty. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 5 equal 22:46 cells, image size 1760x736 (each cell 352x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `silco_fx_m_bite.png`：畸变体：咬住不放，4 帧循环

畸变体**咬在人身体的左边**（画面左边、腰和肩之间）：身子挂在人身上、尾巴往外甩，圆嘴咬住人的身侧，一口一口地啃（嘴一张一合、身子一缩一伸，溅出几滴紫色黏液）。**这一张不对称**：畸变体在左边、嘴朝右（朝着身体）。身体位置留空。4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C), a gold teeth ramp (#FFF6C8, #F0C850, #B0882A), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070).
Effect: A GNAWING MONSTROSITY, 4 looping frames, NOT symmetric, the unit stands in the middle, not drawn: 16 squares wide and 36 tall: a MONSTROSITY: a stubby violet GRUB about 9 squares long and 6 thick (darker violet back, paler belly), its front end one big ROUND MOUTH ringed with GOLD fangs, a small glowing PINK eye above the mouth (refs monstrosity_*.png), clinging to the LEFT side of the unit's body between the hip and the shoulder (its mouth at the body's left edge, about 6 squares left of the middle, its tail curling out to the image left); 1 the mouth wide open; 2 the mouth clamped on, the body squeezing shorter; 3 the body pulling back, two violet slime drops flying; 4 the mouth opening again. The middle (the body) left empty, only the grub's mouth overlaps its edge. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 24:38 cells, image size 1536x608 (each cell 384x608, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `silco_fx_m_die.png`：畸变体：化掉，5 帧

畸变体咬完了化成一摊**紫色黏液**：缩成一团、塌下去、在地上冒泡、蒸发成几缕紫烟。**正面看，左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E).
Effect: A MELTING MONSTROSITY, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the ground line 2 squares above the bottom. 1 a curled violet grub 8 squares across seen from the front, its gold fangs showing; 2 it sags and spreads into a violet slime puddle 12 wide; 3 the puddle 16 wide and 4 tall, bubbles popping, the fangs sinking; 4 the puddle shrinking, thin purple wisps rising; 5 the last wisps. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 5 equal 18:12 cells, image size 1440x192 (each cell 288x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `silco_fx_e_dose.png`：微光注射：药剂打在队友身上，5 帧

希尔科抛来的药剂瓶在队友头顶碎开：洋红的微光液体浇下来，身体两边一下亮起一道道**发光的紫色血管纹**，往上冒一股洋红的蒸汽。身体位置留空。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C).
Effect: A SHIMMER DOSE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a small vial over the unit's head (the top of the cell) shattering in a magenta-white flash; 2 glowing magenta liquid pouring down both sides of the body (mirrored); 3 jagged glowing purple VEIN lines lighting up along both sides of the body like cracks of light, a burst of magenta vapour rising; 4 the veins at their brightest; 5 the veins fading to thin lines, the vapour drifting up. The middle (the body) left empty. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 5 equal 20:44 cells, image size 1600x704 (each cell 320x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `silco_fx_e_shimmer.png`：微光注射：药效（攻速、移速加成），6 帧循环

嗑了微光的人：脚下一圈洋红的光（从斜上方看的椭圆），身体两边一缕缕**洋红的微光蒸汽**往上飘，几颗洋红的光点一闪一闪。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070).
Effect: A SHIMMER HIGH, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: a faint magenta ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 22 squares wide and 7 tall, thin wavy wisps of glowing magenta vapour rising on both sides of the body (mirrored) up to the shoulders, three small magenta sparks; frames 1-6 the wisps flowing upward and the sparks winking in turn. The middle (the body) left empty. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 26:42 cells, image size 2496x672 (each cell 416x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `silco_fx_e_crash.png`：微光注射：药效过去（掉血），5 帧

药效过去的那一下：一股**灰紫色的烟**从人身上往下沉、散开，头顶冒两三个灰色的小泡泡（虚脱）。身体位置留空。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070).
Effect: A SHIMMER COMEDOWN, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn (its top 30 squares fill the cell): 1 a dull purple flash at the chest; 2 a heavy grey-purple smoke sinking down both sides of the body (mirrored); 3 the smoke pooling at the bottom, two small grey bubbles over the head; 4-5 the smoke and bubbles fading. The middle (the body) left empty. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 5 equal 22:30 cells, image size 1760x480 (each cell 352x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `silco_fx_r_can.png`：炼金狂潮：飞出去的巨型储罐，4 帧循环

大招扔出去的**巨型储罐**：和小储罐一样的样子，大一倍多，铁皮上有铆钉和凹痕，三扇发绿光的玻璃窗，窗里挤着好几条扭动的紫色影子，罐口漏出绿色的气。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C), a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C).
Effect: A HUGE THROWN CANISTER, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a big riveted, dented metal canister lying along the flight (18 squares long, 13 tall), iron ends with copper bands, THREE round glowing GREEN windows along its side with dim violet squirming shapes behind them, green gas leaking from its left end; frames 1-4 the windows pulsing and the gas streaming back. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 22:18 cells, image size 1408x288 (each cell 352x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `silco_fx_r_warn.png`：炼金狂潮：地上的预警圈，6 帧

巨型储罐要砸下来的地方：地上一圈越来越亮的**绿色危险圈**（从斜上方看的椭圆），圈边一圈黄黑相间的警示条纹，圈里一片绿色的影子慢慢变大。最大 **横 54 格、纵 18 格**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E), a gold ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A).
Effect: A HAZARD ZONE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a thin chemical green ring 20 squares wide; 2 the ring 36 wide, a faint green shadow inside it; 3 the ring 54 wide and 18 tall with short yellow-and-black hazard stripes around its edge, the green shadow filling it; 4-6 the ring brightening, the shadow darkening, little green bubbles rising from the edge. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 60:22 cells, image size 5760x352 (each cell 960x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `silco_fx_r_burst.png`：炼金狂潮：巨型储罐炸开，10 帧

巨型储罐砸地炸开：一大团**翻滚的绿色化学气体**像蘑菇云一样冲起来，铜铁碎片和洋红的液体往四周飞，地上一圈绿色冲击波，气体里四条畸变体的影子一闪（畸变体本身是另外的图）。砸的地方在格子底部往上 6 格。**左右对称**，10 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E).
Effect: A GIANT CHEMICAL BLAST, 10 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the blast sits on the ground line 6 squares above the bottom. 1 a white-green flash 20 squares across; 2 big copper and iron shards flying out to both sides (mirrored), a billow of chemical GREEN GAS 30 across rising; 3 the gas 50 across and 34 tall like a mushroom, magenta Shimmer splashes thrown wide, a green shockwave ellipse 60 wide and 14 tall on the ground; 4 the gas at its biggest (64 x 48), four dark violet grub silhouettes flashing inside it at mirrored places; 5-6 shards falling, the gas rolling; 7-9 the gas thinning into grey-green puffs that settle low; 10 low wisps. Frames 3-6 MUST fill 60 squares across. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 10 equal 72:60 cells, image size 11520x960 (each cell 1152x960, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `silco_fx_r_fog.png`：炼金狂潮：微光毒雾，6 帧循环

巨型储罐炸完后留在地上的**微光毒雾**：一层贴着地面、慢慢翻滚的绿色雾（从斜上方看的椭圆，横约 80 格、纵约 26 格），雾里夹着几缕洋红的微光，几个绿泡泡冒上来破掉。这一张会**接着重播**（6 帧循环，头尾接得上）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070).
Effect: A LINGERING SHIMMER FOG, 6 looping frames (the last flows into the first), SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a low layer of rolling chemical green fog filling an ellipse 80 squares wide and 26 tall, its edge made of soft billows, a few thin magenta Shimmer streaks inside it, small green bubbles rising and popping at mirrored places; frames 1-6 the billows rolling slowly outward and back, the bubbles rising in turn. Mostly flat shades, its middle a little thinner so the units standing in it stay readable. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 84:32 cells, image size 8064x512 (each cell 1344x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `silco_fx_r_slow.png`：炼金狂潮：毒雾里的减速，4 帧循环

站在毒雾里的人：**脚边缠着一圈绿色的雾**，几个小绿泡往上冒。身体位置留空（只画脚下这一截）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a grey-green smog ramp (#E4ECD8, #AEBE98, #76866A, #46523E).
Effect: A CHOKING FOG AT THE FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a band of chemical green fog wrapped round the unit's feet on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 18 squares wide and 6 tall, two small green bubbles rising at mirrored places; frames 1-4 the fog curling and the bubbles rising. The upper part of the cell empty. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 20:14 cells, image size 1280x224 (each cell 320x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `silco_fx_p_shield.png`：统领：护盾，6 帧循环

统领的护盾：一层**洋红色的六边形光壳**罩住他（只画外圈的轮廓和几块亮一点的六边形，身体位置留空），光壳上流过一道亮光。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a gold ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A).
Effect: A DOMINATOR'S SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: a tall oval shell of light around the whole unit (26 squares wide, 44 tall) drawn as a ring of small HEXAGON outlines in glowing magenta, a few hexagons filled a shade brighter, a thin gold glint; frames 1-6 a bright band sweeping up the shell from the bottom to the top. The middle (the body) left empty. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 28:46 cells, image size 2688x736 (each cell 448x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `silco_fx_p_dom.png`：统领：叠满 5 层，6 帧循环

统领的法强叠满 5 层：**他头顶上方一只发光的橙红伤疤眼印记**（一只横着的眼睛形状，周围一圈暗紫的裂纹），慢慢一明一暗，两三缕洋红的微光往上飘。**身体位置留空**，印记在格子最上面 10 格里。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a gold ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A), a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C).
Effect: A DOMINATOR'S EYE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the unit's head (the top 10 squares of the cell) a glowing ORANGE-RED EYE sigil 8 squares wide and 5 tall seen from the front, ringed by thin dark purple cracks, two or three thin magenta wisps rising from it at mirrored places; frames 1-6 the eye brightening and dimming slowly, the wisps rising. The middle (the body) left empty. everything is a ZAUN CHEM-BARON'S alchemy: glowing magenta SHIMMER liquid and vapour, toxic CHEMICAL GREEN gas, dented copper-and-iron canisters, violet grub-like monstrosities with round mouths of gold teeth; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 16:48 cells, image size 1536x768 (each cell 256x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `silco_icon_skill.png`：技能 1「罐装畸变体」图标

一个铁皮储罐裂开，一只畸变体（紫色蠕虫，圆嘴金牙）从绿光里扑出来。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a murky dark green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a cracked metal CANISTER with copper bands, its glowing green window burst open, a violet MONSTROSITY grub with a round mouth of gold fangs lunging out of it toward the viewer in a puff of green gas. Colours: a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C), a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C), a gold teeth ramp (#FFF6C8, #F0C850, #B0882A), a gold ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A). No text, no letters.
```

### 图标 2. `silco_icon_skill2.png`：技能 2「微光注射」图标

一支发洋红光的微光药剂瓶斜放着，瓶口滴下一滴发光的液体，周围几道洋红的蒸汽。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a murky dark green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a glowing magenta SHIMMER VIAL with a copper cap, tilted, one glowing drop falling from it, wavy magenta vapour curling around it, two small sparks. Colours: a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C), a gold ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A). No text, no letters.
```

### 图标 3. `silco_icon_ult.png`：大招「炼金狂潮」图标

一个巨型储罐在绿色的化学蘑菇云里炸开，碎片飞出，几只畸变体的影子。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a murky dark green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a HUGE riveted canister bursting apart in a rising mushroom of chemical GREEN gas, copper shards flying, two dark violet grub silhouettes in the gas, magenta splashes. Colours: a copper and iron ramp (#FFDCA4, #D88E44, #9A5A24, #5A3214, #2C1A0C), a chemical green ramp (#F2FFD8, #BEF26A, #78CC34, #3E8A22, #1C4412), a Shimmer magenta ramp (#FFF0FF, #FF9CF4, #E848DC, #A824B4, #5C1070), a violet flesh ramp (#D8C8FF, #9A84F0, #6A50C8, #42288E, #22104C), a gold ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `silco_fx_a_vial` | view_projectiles `tft_silco_a_vial`（弹道，z 2；朝右、上下对称） | 12 × 6 |
| `silco_fx_a_hit` | view_effects `tft_silco_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `silco_fx_q_can` | view_projectiles `tft_silco_q_can`（抛物线弹道，z 2；朝右、上下对称） | 12 × 10 |
| `silco_fx_q_warn` | view_effects `tft_silco_q_warn`（落点，地面，z -2，不跟随；左右对称） | 26 × 10 |
| `silco_fx_q_burst` | view_effects `tft_silco_q_burst`（大表，落点，z 3，不跟随；左右对称） | 40 × 34 |
| `silco_fx_m_leap` | view_effects `tft_silco_m_leap`（跟随被扑的人，z 3；左右对称） | 22 × 46 |
| `silco_fx_m_bite` | view_effects `tft_silco_m_bite_l`（跟随被咬的人，z 3）；导入时左右翻转一份给 `tft_silco_m_bite_r`（咬在右边的那只） | 24 × 38 |
| `silco_fx_m_die` | view_effects `tft_silco_m_die`（地面，z 2，不跟随；左右对称） | 18 × 12 |
| `silco_fx_e_dose` | view_effects `tft_silco_e_dose`（跟随队友，z 3；左右对称） | 20 × 44 |
| `silco_fx_e_shimmer` | view_buffs `tft_silco_e_shimmer`（跟随队友，z 3；左右对称） | 26 × 42 |
| `silco_fx_e_crash` | view_effects `tft_silco_e_crash`（跟随队友，z 3；左右对称） | 22 × 30 |
| `silco_fx_r_can` | view_projectiles `tft_silco_r_can`（大表，抛物线弹道，z 2；朝右、上下对称） | 22 × 18 |
| `silco_fx_r_warn` | view_effects `tft_silco_r_warn`（大表，落点，地面，z -2，不跟随；左右对称） | 60 × 22 |
| `silco_fx_r_burst` | view_effects `tft_silco_r_burst`（大表，落点，z 3，不跟随；左右对称） | 72 × 60 |
| `silco_fx_r_fog` | view_effects `tft_silco_r_fog`（大表，落点，地面，z -2，不跟随，每秒重播一次；左右对称） | 84 × 32 |
| `silco_fx_r_slow` | view_buffs `tft_silco_r_slow`（跟随被减速的人，z 3；左右对称） | 20 × 14 |
| `silco_fx_p_shield` | view_buffs `tft_silco_p_shield`（跟随他，护盾在就一直在，z 3；左右对称） | 28 × 46 |
| `silco_fx_p_dom` | view_buffs `tft_silco_d5`（tag p_dom，跟随他，z 4；左右对称） | 16 × 48 |
| `silco_icon_skill` | skill_icons[0] `asset/tft/icons/tft_silco_skill` | 64 × 64 |
| `silco_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_silco_skill2` | 64 × 64 |
| `silco_icon_ult` | skill_icons[2] `asset/tft/icons/tft_silco_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_silco_fx`（小的）和 `tft_silco_big`（q_burst、r_can、r_warn、r_burst、r_fog），tag = 名字；m_bite 切成 m_bite（tag，m_bite_l 用它）和左右翻转的 m_bite_r；p_dom 是 view_buffs 里 d5 的 tag。
- 弹道（a_vial、q_can、r_can）断言上下对称；m_bite 不断言；其余断言左右对称。
- q_warn 在储罐飞行的 q_fall 帧里一直显示、r_warn 在 r_fall 帧里（拉长到那么长）；r_fog 每 60 拍由 tft.dll 重播一次（6 帧放满 60 拍）；m_bite 每口（m_gap 拍）播一遍。
- 用 `pixel_1x/` 切格（import_locke_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
