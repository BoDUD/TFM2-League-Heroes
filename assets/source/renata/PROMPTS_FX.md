# 炼金男爵 烈娜塔·戈拉斯克：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型和动作已定（`design/renata_idle.png` 左边：3/4 正面朝右的女士，黑紫长发、银色面罩、白色短披肩、深藏青马甲、白色喇叭裤，画面左边那只手是金色机械臂，手枪插在另一边胯上；右边是她开大招召出的金红大机甲——**机甲已经画进她的大招动作里，不用画**）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），37 格高、22 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清（只有 `a_flash` 枪口火光例外，见那一条）。
> - 请把这个压缩包解压到**一个新的文件夹**，只用这个包里的文件（不要用以前烈娜塔模型包、走路包里的图）。
> - 大小对照 `design/renata_size.png`：她的待机（游戏格子）放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/renata_shots.png`：定稿动作（游戏格子，4 倍），**青色十字是她的站位点，黄色十字是特效出来的地方**（枪口、机械手）；每张写了特效从哪里出来。**E 和 Q 都从她的金色机械手往前射出**（待机时垂在画面左边，出招时甩到身前），普攻从另一只手的手枪射出。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里烈娜塔自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版（最后一行是原版的颜色条）：**她的化学药剂是玫红色**（从深酒红到白芯，**最亮的地方带一点淡青白**），**W 的烟偏品红紫**，**金色只做点缀**（彩虹光环、回血的光点）。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。
> - **方向（重要，红色方不会镜像）**：飞出去的 `a_shot`、`e_missile`、`q_hand`、`r_wave` 都画成朝右，**上下对称**（往左时会上下翻）。`a_flash` 画进她自己的动作帧（跟着她翻面），也画成朝右、上下对称。其余所有画面（打中、身上、脚下、地上、头顶）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `renata_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张一条：`name`、`file`、`frames`、`cell_1x` = [宽, 高]、`symmetry` = `top_bottom` 或 `left_right`）和生图原稿 `raw/`，打包成 `renata_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「物尽其用」 | 手枪射出化学子弹；打中敌方英雄挂上印记，队友在旁边打它时印记炸开 | `a_shot` · `a_flash` · `a_hit` · `p_mark` · `p_pop` |
| 技能 1 = E「忠诚激励」 | 机械手射出两枚并排的化学飞弹，碰到敌人在落点炸开、减速；飞弹经过的队友得到护盾 | `e_missile` · `e_boom` · `e_hit` · `e_slow` · `e_shield` |
| 技能 2 = Q「铁腕竞合」 | 机械手射出化学之手，抓住第一个敌人定身，再把它甩过她身边砸到地上 | `q_hand` · `q_hit` · `q_fling` · `q_land` · `q_crash_hit` |
| 被动自动放的 W「及时救难」 | 给陷入危险的队友打一针：加攻速移速、不会阵亡，结束时回血 | `w_cast` · `w_buff` · `w_save` |
| 大招「恶意收购」 | 召出机甲，放出一大波化学毒气浪，扫中的敌方英雄陷入狂暴：不能攻击她这边、不能放技能，还会朝身边自己人乱打 | `r_cast` · `r_wave` · `r_hit` · `r_berserk` · `r_lash` · `r_lash_hit`（机甲已在她的动作里） |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、毒气、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 玫红化学药剂（主色）：`#FFFFFF`、`#FFC2D6`、`#F2648E`、`#DE2D62`、`#A8124A`、`#5E0634`；
  - 淡青白（最亮处的彩光）：`#FFFFFF`、`#E2FAF6`、`#A6E4EA`、`#6FBCCB`；
  - 品红紫（W 的烟）：`#F7B4EA`、`#D53DB4`、`#A51791`、`#6E0C70`、`#3E0846`；
  - 金色（只做点缀）：`#FFFFFF`、`#FFF0A8`、`#FFCB4A`、`#F29A12`、`#A65A0A`；
  - 酒红（烟尘、毒气的暗部）：`#D07AA0`、`#A23E6E`、`#6E1C4A`、`#42102E`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 55000，E 爆炸半径 12000，Q 落地半径 14000，R 毒气浪宽 28000、长 100000，狂暴发作半径 25000）。

### 1. `renata_fx_a_shot.png`：普攻：手枪射出的化学子弹（飞行，循环），4 帧

从手枪枪口射出的一颗**玫红化学子弹**：白热的弹头（约 3 格长、2 格高，白芯），外面一圈玫红的光，身后拖一道约 7 格长、越往后越细的玫红光迹，光迹中间一条淡青白的细线，上下各一缕酒红的小烟（上下对称）（参考 BA_Bullet_Glow、BA_Beam_01、BA_Smoke_Trail）。**朝右飞，上下对称**。约 10 格长。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a CHEMTECH PISTOL BULLET flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white-hot bullet 3 squares long and 2 tall with a rose-pink glow round it, a tapered rose-pink tracer 7 squares long behind it with a thin pale cyan line in its middle, two small wine-pink smoke wisps curling off the tracer at mirrored places above and below, flickering.
Layout: one horizontal row of 4 equal 12:6 cells, image size 768x96 (each cell 192x96, 16 px a square); the bullet's tip 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `renata_fx_a_flash.png`：普攻：枪口火光（画进她的普攻帧，**按她的细格子画**），3 帧

开枪一瞬间枪口喷出的火光：白芯，三片玫红的火舌（往前一片最长，斜上、斜下各一片，上下对称），第 2 帧变小、带一点淡青白的光，第 3 帧只剩一小团玫红的烟（参考 BA_Flash_sharp、BA_Embers、BA_Screen_Flames_Soft）。**朝右，上下对称**。**这一张按她身上的细格子画**（她是高清的：她的 1 格 = 游戏的 2/3 格，见 `design/renata_idle.png`），10 × 9 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: a PISTOL MUZZLE FLASH pointing to the RIGHT, 3 frames, played once, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): 1 a white core 2 squares wide and 3 tall at the left edge with three rose-pink flame tongues (one forward 6 squares long, one up-forward and one down-forward 3 squares long, mirrored); 2 the flame smaller (the forward tongue 3 squares), a pale cyan glint at the core; 3 a small puff of rose-pink smoke 4 squares, no white.
Layout: one horizontal row of 3 equal 10:9 cells, image size 480x144 (each cell 160x144, 16 px a square); the flash's root (where the barrel ends) on the LEFT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `renata_fx_a_hit.png`：普攻命中（目标身上），4 帧

子弹打中：一颗四角星形的玫红闪光（白芯），中间横穿一道细长的镜头光（中间白、两头淡青），几粒玫红火星往外溅（参考 BA_Tar_Flare、BA_Hit_Lens_Flare、BA_Flash_sharp）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: a CHEMTECH BULLET HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 a four-pointed star flash 9 squares (white core, rose-pink rays up, down, left and right) with a thin horizontal lens-flare streak 13 squares long through its middle (white centre, pale cyan ends); 3 the star 11 squares, the streak fading, 4 rose-pink embers flying out at mirrored places; 4 fading pink embers.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `renata_fx_p_mark.png`：被动 物尽其用：头顶的化学印记（敌方英雄身上，循环），4 帧

被她打中的敌方英雄挂上印记：头顶浮着一滴发光的**玫红化学药剂**（水滴形，尖头朝上，白色高光，约 4 格宽 6 格高），外面一圈细细的彩虹光环（玫红、淡青、金三色交替，像英雄联盟的 P_Rainbow_Flash），一闪一闪，水滴底下偶尔滴下一小滴（参考 P_Rainbow_Flash、Renata_P_Puddle_Goop、P_SmokeTrail）。**左右对称**，4 帧无缝循环。导入时 Claude 把它放到头顶上方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a gold ramp (#FFFFFF, #FFF0A8, #FFCB4A, #F29A12, #A65A0A).
Effect: a HOVERING CHEMTECH DROP MARK, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a glowing rose-pink teardrop of chemical (4 squares wide and 6 tall, pointed at the top, a white highlight 2 squares in its upper middle), inside a thin ring of iridescent light (a circle 12 squares across, 1 square thick, its squares alternating rose-pink, pale cyan and gold, mirrored left to right); frame 1 as described, 2 the ring brighter, 3 the drop swollen by a square, 4 a small droplet (2 squares) falling from the drop's round bottom.
Layout: one horizontal row of 4 equal 12:14 cells, image size 768x224 (each cell 192x224, 16 px a square); centered across, the ring in the upper 12 rows, the falling droplet below it. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `renata_fx_p_pop.png`：被动引爆：印记炸开（敌方英雄身上），5 帧

队友打中带印记的敌人时印记引爆：一圈彩虹光环猛地扩开（玫红、淡青、金），中间一团玫红的化学爆炸（白芯），几滴玫红药剂和金色的小光点往外飞溅（参考 P_Rainbow_Flash、Q_Burst_Hit、Z_Flecks_02）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a gold ramp (#FFFFFF, #FFF0A8, #FFCB4A, #F29A12, #A65A0A).
Effect: a CHEMTECH MARK BURSTING on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a rose-pink chemical burst 10 squares with a white core inside a thin iridescent ring 12 squares across (its squares rose-pink, pale cyan and gold); 3 the burst 14 squares with spiky splash tips, the ring 16 squares, 6 pink goo drops (2 squares each) flying out at mirrored places; 4 the ring breaking into gold and pink motes, the drops further out; 5 fading pink motes.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `renata_fx_e_missile.png`：E 忠诚激励：两枚并排的化学飞弹（飞行，循环），4 帧

从金色机械手射出的**两枚并排的化学飞弹**：上下各一颗玫红的彗星头（约 3 格，白芯），各拖一道约 8 格长、闪着彩光的尾迹（玫红里夹着淡青和白的亮点，每帧往后流），两道尾迹微微往外弯，上下完全对称（参考 E_Comet、E_Missile_Head_2、E_Shimmer_Trail、E_Ribbon_01）。**朝右飞，上下对称**。约 14 格长、10 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: TWO CHEMTECH MISSILES flying side by side to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): two comet heads, one above and one below the middle line (their centres 6 squares apart), each 3 squares with a white core and a rose-pink glow, each trailing a shimmering ribbon 8 squares long (rose-pink with pale cyan and white glints that move back along it each frame) curving slightly outward away from the middle; the two missiles exact mirror images.
Layout: one horizontal row of 4 equal 16:12 cells, image size 1024x192 (each cell 256x192, 16 px a square); the comet heads 1 square from the RIGHT edge, the pair vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `renata_fx_e_boom.png`：E 爆炸（飞弹的落点，地上，不跟随），6 帧

飞弹在落点炸开：一团玫红的化学爆炸，地上一圈尖刺状的冲击环往外扩（从斜上方看的扁椭圆，约 24 格宽），炸完落成一摊冒泡的玫红药剂（参考 E_Burst_Hit、E_Mis_AoE_Wind、E_LeadingEdge_Ring、E_shockwave、E_Puddle_Mask、E_Bubble_01）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a CHEMTECH BLAST on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 6 squares; 2 a rose-pink burst 12 squares wide and 10 tall with spiky splash tips and a white core, a ring on the ground (an ellipse 16 wide, 5 tall); 3 the spiky ring 24 squares wide and 8 tall (rose-pink with pale cyan glints on its rim), the burst at its tallest; 4 the burst falling into a glossy rose-pink puddle (an ellipse 14 wide, 4 tall) with 3 bubbles at mirrored places, the ring fading; 5 the bubbles popping (white rings 2 squares); 6 the puddle shrinking, a few drops.
Layout: one horizontal row of 6 equal 26:18 cells, image size 2496x288 (each cell 416x288, 16 px a square); centered across, the ground ring's middle 5 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `renata_fx_e_hit.png`：E 命中（目标身上），4 帧

被飞弹炸到：一团玫红的药剂溅开（白芯），几滴药剂往两边甩（参考 E_Burst_Hit、Froth）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: a CHEMICAL SPLASH on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 4 squares; 2 a rose-pink splash 10 squares with a white core and spiky goo tips; 3 the splash 12 squares, 4 goo drops (2 squares) flung out at mirrored places, small bubbles; 4 fading drops.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `renata_fx_e_slow.png`：E 减速：脚下一摊化学药剂（目标身上，循环），4 帧

被减速的敌人脚下一摊发亮的**玫红药剂**（从斜上方看的扁椭圆，约 16 格宽 5 格高，边缘波浪形），表面两道白色高光，几个小泡冒出来又破掉（参考 E_Puddle_Mask、Renata_E_Puddle_Erode、E_Bubble_01）。**左右对称**，4 帧无缝循环。画在人物下面，中间会被人挡住。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a GLOSSY CHEMICAL PUDDLE on the ground under a unit, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a rose-pink puddle (an ellipse 16 squares wide and 5 tall with a wavy edge, darker wine-pink squares along its rim, two white highlight streaks at mirrored places), small bubbles (1-2 squares, white-pink rims) at mirrored places: frame 1 two small bubbles, 2 the bubbles bigger, 3 popped (white rings), 4 calm.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered across, the puddle's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `renata_fx_e_shield.png`：E：队友身上的化学泡泡护盾（队友身上，跟随），6 帧

飞弹经过的队友得到护盾：一个**玫红色的泡泡**把队友罩住——先在胸口一闪，泡泡从中间长大成一个竖着的椭圆，边缘 1–2 格玫红，左上和右上各一道白色高光（左右对称），顶上一层淡青白的彩光，最后泡泡边缘闪一闪碎成小点（参考 E_Shield_Bubble、E_Shield_Edges、E_Shield_Front_1、E_Bubble_01）。**左右对称**，**泡泡里面（身体位置）留空**（an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: a CHEMICAL BUBBLE SHIELD forming round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn): 1 a white-pink flash 4 squares at the figure's chest; 2 a rose-pink bubble rim (a circle 14 squares across, 1 square thick) round the chest; 3 the bubble an upright ellipse 24 squares wide and 34 tall round the whole figure, its rim 1-2 squares rose-pink, a curved white highlight (3 squares) at its upper left and the same at its upper right, a pale cyan shimmer band along its top; 4 the same bubble, the shimmer lower; 5 the same, the rim flickering lighter; 6 the rim breaking into scattered pink squares. Inside the rim the bubble is EMPTY (the figure shows through).
Layout: one horizontal row of 6 equal 26:38 cells, image size 2496x608 (each cell 416x608, 16 px a square); centered across, the bubble's bottom (the figure's feet) 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `renata_fx_q_hand.png`：Q 铁腕竞合：飞出去的化学之手（飞行，循环），4 帧

从金色机械手射出的一只**发光的玫红化学之手**往前抓：手掌约 5 格（淡青白的芯），五根手指往前张开、上下对称（中间一根朝前最长，上下各两根往外张），手腕后面拖一段约 6 格的发光玫红管子（一节一节的暗酒红环），几粒玫红火星（参考 Q_Avatar_Mask、Q_Inner_Arm_Tubes、Q_Inner_Arm_Tubes_Gradient、Q_Constraint）。**朝右飞，上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: an OPEN CHEMTECH HAND reaching to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a glowing rose-pink palm (5 squares, a pale cyan-white core) with five fingers spread forward, symmetric up and down (the middle finger 4 squares long pointing right, two fingers above and two below fanning outward, each 3 squares, bright pink tips), behind the wrist a glowing arm of rose-pink tubes 6 squares long with dark wine segment rings, a few pink sparks trailing; the fingers flexing a little between frames (open, wider, open, narrower).
Layout: one horizontal row of 4 equal 16:13 cells, image size 1024x208 (each cell 256x208, 16 px a square); the middle fingertip 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `renata_fx_q_hit.png`：Q 抓住：化学之手攥住目标（目标身上，跟随），6 帧

被化学之手抓住（定身）：一闪白光，左右两边各两根发光的玫红大手指从两边伸过来把目标攥住（左右对称），手指尖停在身体边上，后三帧保持攥住、手指上的淡青高光一闪一闪（参考 Q_Burst_Hit、Q_Constraint、Q_Inner_Arm_Tubes）。**左右对称**，中间身体位置留空（an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a GIANT CHEMTECH HAND GRIPPING a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn): 1 a white-pink flash 6 squares at its middle; 2 two glowing rose-pink fingers on each side of the figure (each 3 squares thick, 10 long) reaching in, mirrored; 3 the fingers curled round its waist and chest from both sides, their tips stopping at the figure's outline (the middle 12 squares stay empty), pink sparks; 4-6 the grip held (nearly the same frames), pale cyan-white highlights moving along the fingers.
Layout: one horizontal row of 6 equal 26:32 cells, image size 2496x512 (each cell 416x512, 16 px a square); centered across, the figure's feet 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `renata_fx_q_fling.png`：Q 甩人：被拽着甩出去的一瞬间（目标身上，跟随），4 帧

被拽着甩过来的一瞬间：目标两边各一道玫红的弧形气流（像被猛地一拽带起的风），脚下扬起一团酒红的烟尘（参考 W_speed_blur、Q_GroundSmoke02、Q_Smoke_Erode）。**左右对称**，中间身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a VIOLENT YANK round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn): 1 a white-pink flash 4 squares at its middle; 2 a curved rose-pink swoosh arc on each side of the figure (each 3 squares thick, 16 tall, bowing outward, mirrored), wine-pink dust puffs at its feet; 3 the arcs further out and thinner with pale cyan glints, the dust spreading; 4 the arcs breaking into pink streaks, the dust fading.
Layout: one horizontal row of 4 equal 24:30 cells, image size 1536x480 (each cell 384x480, 16 px a square); centered across, the figure's feet (the dust) 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `renata_fx_q_land.png`：Q 落地：被甩的人砸到地上（地上，不跟随），6 帧

被甩出去的人砸到地上：地面一闪，一圈玫红的冲击环往外扩（从斜上方看的扁椭圆，约 28 格宽），两边扬起酒红到玫红的烟尘，地上留下几道发光的裂纹，慢慢散去（参考 Q_GroundSmoke02、Q_Ground_Light、Q_Radial_Erosion、Q_Smoke_Scroll）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a CRASH LANDING on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash on the ground (an ellipse 10 wide, 3 tall); 2 a rose-pink shock ring (an ellipse 18 wide, 5 tall) and wine-pink dust puffs thrown up on both sides (6 squares tall); 3 the ring 28 wide and 8 tall, the dust at its highest, short glowing pink cracks on the ground at mirrored places; 4 the ring thinner and fading, the dust spreading low; 5 the dust settling, the cracks glowing faintly; 6 the last dust wisps.
Layout: one horizontal row of 6 equal 30:16 cells, image size 2880x256 (each cell 480x256, 16 px a square); centered across, the ring's middle 5 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `renata_fx_q_crash_hit.png`：Q 落地命中（目标身上），4 帧

被砸中：一团玫红的冲击炸开（白芯），四道短短的碎片光斜着往外射（参考 Q_Burst_Hit、R_land_splash2）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: an IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a rose-pink impact burst 10 squares (white core) with 4 short white-pink shards shooting out diagonally at mirrored places; 3 the burst 12 squares, the shards further, wine-pink dust; 4 fading dust and sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `renata_fx_w_cast.png`：W 及时救难：给队友打一针（队友身上，跟随），6 帧

她给陷入危险的队友打一针：队友脚下冒出一圈**品红紫色的化学烟**，烟顺着身体两侧往上卷，几道玫红的小闪电噼啪闪，两边各两道淡青色的风线往上冲（加速）（参考 W_Smoke_Shape、W_Smoke_Shape_03、W_Lightning、W_Wind、W_Hand_Glow）。**左右对称**，中间身体位置留空（an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-violet smoke ramp (#F7B4EA, #D53DB4, #A51791, #6E0C70, #3E0846) and a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: a CHEMTECH STIMULANT BURST round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn): 1 a magenta-violet smoke ring bursting on the ground round the feet (an ellipse 18 wide, 4 tall) with a white-pink flash at its front middle; 2 magenta-violet smoke puffs (each 6-8 squares, lighter rims) rising on both sides of the figure to its waist, 2 short rose-pink lightning zigzags at mirrored places; 3 the smoke up to its shoulders, curling outward, 2 pale cyan wind streaks (1 square wide, 6 long, slanting up and out) on each side; 4 the smoke at its widest (26 squares across), the lightning crackling at head height on both sides; 5 the smoke thinning into rose-pink flakes rising; 6 a few pink flakes and cyan glints.
Layout: one horizontal row of 6 equal 28:36 cells, image size 2688x576 (each cell 448x576, 16 px a square); centered across, the figure's feet 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `renata_fx_w_buff.png`：W 期间：队友脚下的增益光环（队友身上，循环），4 帧

救难期间队友脚下：一圈品红紫色的化学光环（从斜上方看的扁椭圆，约 20 格宽 5 格高，内圈玫红、一抖一抖），光环两头冒着小烟，几片玫红的小薄片往上飘，两边各一道淡青的风线（参考 W_WobbleLine、W_Flakes、W_Glow_Noise、W_Wind）。**左右对称**，4 帧无缝循环。画在人物下面，中间会被人挡住。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-violet smoke ramp (#F7B4EA, #D53DB4, #A51791, #6E0C70, #3E0846) and a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: a CHEMTECH AURA ON THE GROUND under a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a ring of magenta-violet chemical light on the ground (an ellipse 20 squares wide and 5 tall, 1-2 squares thick, a wobbling rose-pink inner edge), small smoke curls rising from its left and right ends, 2-3 rose-pink flakes (1-2 squares) drifting up above the ring at mirrored places (each frame a little higher), a pale cyan wind streak (1 square wide, 4 tall) at each side; the ring's brightest squares moving round it from frame to frame (mirrored).
Layout: one horizontal row of 4 equal 22:12 cells, image size 1408x192 (each cell 352x192, 16 px a square); centered across, the ring's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `renata_fx_w_save.png`：W 结束：队友回一口血（队友身上，跟随），6 帧

救难结束时队友回血：脚下一圈玫红白光亮起，玫红的小薄片和淡青白的光点沿身体两侧往上升，最后在头顶散成一圈金色的小光点（参考 W_Flakes、W_Glow_Noise、Z_Mote、Z_Flecks_02）。**左右对称**，中间身体位置留空（an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a gold ramp (#FFFFFF, #FFF0A8, #FFCB4A, #F29A12, #A65A0A).
Effect: a RESTORING SURGE round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright hero figure 16 squares wide and 36 tall stands in the middle, not drawn): 1 a white-pink ring lighting on the ground round the feet (an ellipse 16 wide, 4 tall); 2 rose-pink flakes and pale cyan sparkles (1-2 squares) rising on both sides of the figure to its knees; 3 the sparkles at its waist, the ring brighter; 4 the sparkles at its shoulders, a soft white-pink glow line up each side; 5 the sparkles above its head turning into gold motes; 6 a few gold and pink motes fading above the head.
Layout: one horizontal row of 6 equal 24:40 cells, image size 2304x640 (each cell 384x640, 16 px a square); centered across, the figure's feet 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `renata_fx_r_cast.png`：R 恶意收购：召出机甲、喷出化学毒气（她身上，画在她下面），6 帧

她召出机甲开大的一瞬间：脚下一圈玫红光环亮起，机甲往两边喷出大团**玫红化学毒气**，贴着地面往外滚，地上一圈冲击环往外扩，最后剩一层薄薄的毒雾（参考 R_FlareOmni、R_Groundsmoke、R_Reset_Ground、R_Smoke_Strong、R_OilySmoke_erode）。**左右对称**，中间她和机甲的位置只有地上的光环（she and her machine stand in the middle (30 squares wide, 56 tall), not drawn；整张画在她下面，被她挡住的地方看不见）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: CHEMTECH GAS VENTING round a big figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (she and her machine stand in the middle (30 squares wide, 56 tall), not drawn): 1 a white-pink flare 8 squares on the ground under the figure and a rose-pink ring on the ground round the feet (an ellipse 24 wide, 6 tall); 2 rose-pink gas clouds (8-10 squares each, lighter rims) bursting out low on both sides of the figure; 3 the gas rolling outward along the ground to 50 squares across, up to 14 squares tall at the sides, a thin shock ring on the ground 44 wide and 10 tall; 4 the gas clouds at their widest (62 squares across), lower; 5 the gas thinning into wine-pink mist on the ground; 6 a few fading wisps.
Layout: one horizontal row of 6 equal 64:32 cells, image size 6144x512 (each cell 1024x512, 16 px a square); centered across, the figure's feet (the ground ring's middle) 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `renata_fx_r_wave.png`：R：涌出去的化学毒气浪（飞行，循环），4 帧

从机甲前面涌出的一大波**玫红化学毒气浪**往前推（从上往下看）：一道往前鼓的弧形浪头（约 32 格高，上下对称），浪头边缘最亮（白到淡青白，再到亮玫红），后面是翻滚的玫红到酒红的毒气云，往后拖约 10 格，几滴药剂往后甩（参考 R_Wave、R_Wave_Edge、R_Wave_Texture、R_Smoke_Strong、R_Groundsmoke、R_Puddles）。**朝右飞，上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a WAVE OF CHEMTECH GAS rolling to the RIGHT seen from above, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a crescent wave front bulging forward (32 squares from top to bottom, 6 squares deep at its middle, its convex edge facing right), the front edge brightest (white and pale cyan rim squares, then bright rose-pink), behind it billowing rose-pink and wine-pink gas clouds 10 squares deep with lighter rims, drops of pink goo trailing behind at mirrored places; the clouds churning from frame to frame.
Layout: one horizontal row of 4 equal 20:34 cells, image size 1280x544 (each cell 320x544, 16 px a square); the wave front's middle 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `renata_fx_r_hit.png`：R 命中：被毒气浪扫中、陷入狂暴（目标身上，跟随），6 帧

被毒气浪扫中、陷入狂暴：一团玫红的毒气裹住目标的头和肩，几道玫红的小闪电往外噼啪，最后毒气往上散开（参考 R_Lightning02、R_Whisp、R_Mark_distort_RGBA、R_Smoke_Strong）。**左右对称**，中间脸的位置淡一些。导入时 Claude 把格子中间放到头部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: CHEMTECH GAS ENGULFING a unit's head, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 5 squares; 2 rose-pink gas swirling round the head and shoulders (a ring of puffs 16 squares wide, lighter rims), the middle 8 squares left faint; 3 the gas thicker, 4 short rose-pink lightning zigzags crackling out at mirrored places; 4 the lightning brighter (white cores); 5 the gas thinning into wisps rising; 6 fading wisps.
Layout: one horizontal row of 6 equal 20:22 cells, image size 1920x352 (each cell 320x352, 16 px a square); centered in every cell (the cell's middle is the head). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `renata_fx_r_berserk.png`：R 狂暴中：头顶的小毒气云（目标身上，循环），4 帧

狂暴期间目标头顶：一小团翻滚的玫红毒气云（约 12 格宽 6 格高），云下两边各一道小闪电噼啪闪（左右对称），表示被控制（参考 R_Lightning02、R_Whisp、Z_Sparks）。**左右对称**，4 帧无缝循环。导入时 Claude 把它放到头顶上方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a SMALL CHEMTECH STORM CLOUD hovering over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a churning rose-pink gas cloud 12 squares wide and 6 tall (lighter rims, a few wine-pink shadow squares at its bottom), a short rose-pink lightning zigzag (1 square wide, 4 tall, white core) under its left and right ends (mirrored); each frame the cloud's puffs shifting, the lightning on in frames 1 and 3 and off in 2 and 4.
Layout: one horizontal row of 4 equal 16:12 cells, image size 1024x192 (each cell 256x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `renata_fx_r_lash.png`：R 狂暴发作：被控制的人朝身边自己人乱打（地上，不跟随），6 帧

狂暴的敌人朝身边自己人乱打一下：脚下炸开一圈玫红的冲击环（从斜上方看的扁椭圆，约 50 格宽），环上跳着几道玫红的小闪电（左右对称），很快散去（参考 Shockwave01b、R_Grid_Edges、R_Lightning02、R_Puddles）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a pale cyan shimmer ramp (#FFFFFF, #E2FAF6, #A6E4EA, #6FBCCB).
Effect: a BERSERK SHOCKWAVE on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash on the ground (an ellipse 10 wide, 3 tall); 2 a rose-pink ring (an ellipse 24 wide, 6 tall, 1-2 squares thick); 3 the ring 40 wide and 10 tall, 4 short pink lightning zigzags standing on it at mirrored places; 4 the ring 50 wide and 13 tall, thinner, the lightning fading; 5 the ring breaking into pink dashes; 6 fading pink specks.
Layout: one horizontal row of 6 equal 52:16 cells, image size 4992x256 (each cell 832x256, 16 px a square); centered across, the ring's middle 7 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `renata_fx_r_lash_hit.png`：R 狂暴发作命中（目标身上），4 帧

被狂暴的同伴打中：两道交叉的玫红爪痕（X 形，白芯），一圈酒红的小火星（参考 R_ErosionShapes01、Z_Sparks）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, gas or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose-pink chemical ramp (#FFFFFF, #FFC2D6, #F2648E, #DE2D62, #A8124A, #5E0634) and a wine-pink dust ramp (#D07AA0, #A23E6E, #6E1C4A, #42102E).
Effect: a BERSERK STRIKE on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 two crossing rose-pink slash marks forming an X 10 squares wide (white cores, mirrored); 3 the X 12 squares, wine-pink sparks flying out at mirrored places; 4 the X fading into sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `renata_fx_a_shot` | view_projectiles `league_renata_a_shot`（朝目标飞，画面随方向转；上下对称） | 10 × 4 |
| `renata_fx_a_flash` | 不进特效表：Claude 画进她自己的 attack 第 3、4 帧（枪口；跟着她翻面） | 10 × 9（她的细格子） |
| `renata_fx_a_hit` | view_effects `league_renata_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `renata_fx_p_mark` | view_buffs `league_renata_p_mark`（跟随，头顶上方；左右对称） | 12 × 13 |
| `renata_fx_p_pop` | view_effects `league_renata_p_pop`（跟随，画在人物上面；左右对称） | 16 |
| `renata_fx_e_missile` | view_projectiles `league_renata_e_missile`（朝目标飞，画面随方向转；上下对称） | 14 × 10 |
| `renata_fx_e_boom` | view_effects `league_renata_e_boom`（不跟随，画在人物上面；左右对称） | 26 × 16 |
| `renata_fx_e_hit` | view_effects `league_renata_e_hit`（跟随，画在人物上面；左右对称） | 12 |
| `renata_fx_e_slow` | view_buffs `league_renata_e_slow`（跟随，画在人物下面；左右对称） | 16 × 6 |
| `renata_fx_e_shield` | view_effects `league_renata_e_shield`（跟随，画在人物上面；左右对称） | 26 × 36 |
| `renata_fx_q_hand` | view_projectiles `league_renata_q_hand`（朝目标飞，画面随方向转；上下对称） | 14 × 11 |
| `renata_fx_q_hit` | view_effects `league_renata_q_hit`（跟随，画在人物上面；左右对称） | 24 × 30 |
| `renata_fx_q_fling` | view_effects `league_renata_q_fling`（跟随，画在人物上面；左右对称） | 22 × 28 |
| `renata_fx_q_land` | view_effects `league_renata_q_land`（不跟随，画在人物下面；左右对称） | 30 × 14 |
| `renata_fx_q_crash_hit` | view_effects `league_renata_q_crash_hit`（跟随，画在人物上面；左右对称） | 12 |
| `renata_fx_w_cast` | view_effects `league_renata_w_cast`（跟随，画在人物上面；左右对称） | 28 × 34 |
| `renata_fx_w_buff` | view_buffs `league_renata_w_buff`（跟随，画在人物下面；左右对称） | 22 × 10 |
| `renata_fx_w_save` | view_effects `league_renata_w_save`（跟随，画在人物上面；左右对称） | 24 × 38 |
| `renata_fx_r_cast` | view_effects `league_renata_r_cast`（她身上播一次，跟随，画在她和机甲下面；左右对称；大图表） | 64 × 30 |
| `renata_fx_r_wave` | view_projectiles `league_renata_r_wave`（朝目标飞，画面随方向转；上下对称；大图表） | 18 × 32 |
| `renata_fx_r_hit` | view_effects `league_renata_r_hit`（跟随，画在人物上面；左右对称） | 18 × 20 |
| `renata_fx_r_berserk` | view_buffs `league_renata_r_berserk`（跟随，头顶上方；左右对称） | 14 × 10 |
| `renata_fx_r_lash` | view_effects `league_renata_r_lash`（不跟随，画在人物下面；左右对称） | 50 × 14 |
| `renata_fx_r_lash_hit` | view_effects `league_renata_r_lash_hit`（跟随，画在人物上面；左右对称） | 12 |

- 两张表：`asset/league/effects/league_renata_fx`（小的）和 `league_renata_big`（r_cast、r_wave），tag = 名字（build_renata.py 的 views）。
- `a_flash` 不进表：rig_renata.py 按她的细格子把它画进 attack 第 3、4 帧的枪口（1 倍时枪口在站位点前 24.5、上 4.5）。
- 投射物 `a_shot`、`e_missile`、`q_hand`、`r_wave` 画面朝方向转；`e_boom`、`q_land`、`r_lash` 不跟随（落点 / 地上的晚播画面，红色方规则）；`q_land`、`r_lash`、`r_cast`、`w_buff`、`e_slow` 画在人物下面（z -1；`r_lash` 在 build_renata.py 里还是 2，导入时改）。`p_mark`、`r_berserk` 放到头顶上方，`r_hit` 的格子中间放到头部。
- 用 `pixel_1x/` 切格（import_swain_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；量每张的亮度（平均 / 90% 分位）和包里其他英雄比。
