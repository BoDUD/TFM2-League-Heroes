# 齐天大圣 悟空：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型和动作已定（`design/wukong_idle.png`：3/4 正面朝右的猴王，棕色猴毛、尖刺头发、绿眼睛、红围巾、金红护臂、金色前襟、暗红褐长袍、紫鞋，背后翘着长尾巴，手里竖着一根金箍棒：红色两头、金箍、灰钢中段）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），46 格高、51 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/wukong_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/wukong_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - **三张分身图（`w_clone`、`w_clone_atk`、`w_clone_spin`）是他本人的样子**：W 留在原地的分身和悟空一模一样（英雄联盟里就是这样），但要**画成正面朝前、左右对称**（游戏在红色方不会把图镜像，侧身的分身到了红色方会背对敌人）。颜色和细节照 `design/wukong_idle.png`，正面的样子参考 `design/wukong_front_ref.png`（英雄联盟里他的正面）。分身**有一圈深色描边**（他是实心的人），头发尖到鞋底 38 格（按游戏格子画，不是高清）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里悟空自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**金箍棒的打击和大闹天宫是橙金色的光**，**筋斗云是白云带淡蓝阴影**，**真假猴王的烟是灰白色**，**破甲是一个裂开的红盾**，**金刚不坏是灰色的石头**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人（`w_poof` 例外：那团烟就是要把他盖住）。
> - **所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `wukong_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/wukong_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/wukong_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + Q「粉碎打击」 | 金箍棒横扫；Q 好了的那一下棒子伸长戳出去，打掉目标的护甲 | `a_hit` · `q_hit` · `q_shred` |
| 技能 1 = E「腾云突击」 | 踩着筋斗云冲到目标身边，分身打中目标和身边最多两个敌人，之后攻速变快 | `e_cloud` · `e_land` · `e_hit` |
| 技能 2 = W「真假猴王」 | 嘭的一团烟隐身冲到目标身后，原地留下一个一模一样的分身（站着、每秒打一下身边的敌人；悟空放大招时也跟着转） | `w_poof` · `w_clone` · `w_clone_atk` · `w_clone_spin` · `w_hit` |
| 大招「大闹天宫」 | 金箍棒伸长转两秒，第一下把身边的敌人击飞，转完还能再转一次 | `r_on` · `r_hit` |
| 被动「金刚不坏」 | 打中英雄叠护甲，叠满 5 层时身边浮着石片 | `p_stone` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、云、风、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：分身本人、盔甲碎片、石片、破甲盾牌可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 橙金色的光（打击、大招旋风、分身的闪光）：`#FFFFFF`、`#FFF4C8`、`#FFD36A`、`#FFA62B`、`#E2681A`、`#9C3A12`；
  - 白云（筋斗云）：`#FFFFFF`、`#F4F6FF`、`#D8E2F4`、`#AFC2E2`、`#8197C4`、`#56688F`；
  - 灰白烟（真假猴王）：`#F4F2EE`、`#D6D2CC`、`#AEA8A2`、`#86807C`、`#5E5A58`、`#3A3838`；
  - 红色（破甲、盔甲碎片）：`#FFFFFF`、`#FFD0C0`、`#FF7A5A`、`#E8341C`、`#A8160E`、`#600A08`；
  - 灰色石头（金刚不坏）：`#F0ECE4`、`#CBC3B6`、`#A1978A`、`#786E64`、`#534B45`、`#322D2A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**（三张分身图除外：那就是要画的人）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头（光的特效一段，三张分身图另一段）。大小写在每条里（1 个游戏像素约等于 1000 距离单位：大闹天宫的半径 28000，E 分身打中的半径 22000，分身打人的范围 30000）。

### 1. `wukong_fx_a_hit.png`：普攻命中：金箍棒打中（目标身上），4 帧

金箍棒打中目标：一团橙金色的星形闪光，中间白色，几道短短的橙色光条往外甩，几颗火星（参考 E_Impact_Flash、Flare-Omnimax、Wukong_Base_Glow）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a HEAVY STAFF BLOW on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares with a gold rim; 2 an orange-gold star burst 10 squares with a white core, 4 short orange light streaks flung out at mirrored angles; 3 the burst thinner and 12 squares, a few gold sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `wukong_fx_q_hit.png`：Q 粉碎打击命中：伸长的棒狠狠戳中（目标身上），5 帧

伸长的金箍棒狠狠戳中目标、打碎他的护甲：一道大的白金色冲击闪光，一圈橙金色的冲击环往外扩，几块红色的盔甲碎片往外飞（参考 Wukong_Base_R_Suck_flash、Wukong_Base_Shockwave1、MonkeyKing_metal_shards）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12) and a red ramp (#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08).
Effect: a CRUSHING STAFF THRUST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 7 squares; 2 a gold-white star burst 14 squares, a thin orange shock ring starting round it; 3 the ring 18 squares (1 square thick), 4 small red armour shards (2x2 squares, a dark red edge) flying out at mirrored places; 4 the ring fading, the shards farther; 5 a few sparks and shards.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `wukong_fx_q_shred.png`：Q 破甲（敌人头顶，循环），4 帧

被粉碎打击打掉护甲的敌人：头顶上方浮着一个**红色的盾牌，中间一道裂缝**，一闪一闪（参考 Jarvan_Base_P_armor_shred、MonkeyKing_armordebuff）。**左右对称**，只画在头顶上方（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，盾牌在他头顶上面 2 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red ramp (#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08).
Effect: an ARMOUR BREAK MARK floating over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): a small red shield 8 squares wide and 9 tall (a pale red rim, darker red inside) with a jagged white crack down its middle, its bottom edge 2 squares above the champion's head (38 squares above the cell's bottom row); 1 dim, 2 brighter, 3 brightest (the crack flashing white), 4 like 2; nothing below it.
Layout: one horizontal row of 4 equal 12:46 cells, image size 768x736 (each cell 192x736, 16 px a square); centered across, the shield's bottom edge 38 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `wukong_fx_e_cloud.png`：E 腾云突击：脚下的筋斗云（他身上，跟随），5 帧

他冲向目标时脚下踩着一朵白色的筋斗云：一团圆滚滚的白云（几团云朵叠在一起，淡蓝的阴影，边缘一圈白），左右两边拖着淡淡的风线，云团里有几颗金色的光点（参考 Wukong_Base_Clouds、Clouds2、NimbusSides、E_Mis_self_01_Wind）。**左右对称**（游戏在红色方不会镜像，所以云不能只往一边拖），画在他脚下（the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn，云在他脚下和小腿两边，上半身留空）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white cloud ramp with pale blue shadows (#FFFFFF, #F4F6FF, #D8E2F4, #AFC2E2, #8197C4, #56688F) and an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: A NIMBUS CLOUD under a figure's feet, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): a puffy white cloud 40 squares wide and 10 tall made of round cloud puffs (pale blue shadows underneath, white tops, no outline) under its feet, a few gold sparkles in the puffs, thin pale wind streaks trailing out to BOTH sides (mirrored); 1 the cloud forming (24 wide); 2 full; 3 full, the puffs rolled a little; 4 like 2; 5 the cloud thinning out at both sides.
Layout: one horizontal row of 5 equal 56:24 cells, image size 4480x384 (each cell 896x384, 16 px a square); centered across, the figure's feet 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `wukong_fx_e_land.png`：E 落地：云朵四散（他脚下，不跟随），5 帧

他落到目标身边：脚下一圈白云猛地往两边炸开（扁椭圆的云环），中间一道金色闪光，几团小云朵往外飘、慢慢散掉（参考 Wukong_Base_Clouds、FloorShockwave、Flare-Rainbow）。**左右对称**，中间留空（他站在中间）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white cloud ramp with pale blue shadows (#FFFFFF, #F4F6FF, #D8E2F4, #AFC2E2, #8197C4, #56688F) and an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: CLOUDS BURSTING OUT AT A LANDING seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the middle 14 squares wide left empty above the ground (he lands there); 1 a gold-white flash on the ground 12 squares wide; 2 a ring of white cloud puffs bursting out (an ellipse 30 squares wide and 8 tall, pale blue shadows); 3 the ring 44 wide and 12 tall, small puffs drifting out at mirrored places; 4 the puffs thinning; 5 faint wisps.
Layout: one horizontal row of 5 equal 50:26 cells, image size 4000x416 (each cell 800x416, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `wukong_fx_e_hit.png`：E 分身打中（目标和身边敌人身上），4 帧

腾云突击的分身打中敌人：一个金色半透明的猴子剪影一闪（只是一团金色光的轮廓，不用画细节）扑到目标身上，一道金色斜劈闪光，一小团白云散开（参考 MonkeyKing_shadow_step、Wukong_Base_Flicker、Wukong_Base_Clouds）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12) and a white cloud ramp with pale blue shadows (#FFFFFF, #F4F6FF, #D8E2F4, #AFC2E2, #8197C4, #56688F).
Effect: a GOLDEN CLONE STRIKE on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale gold glow 8 squares (a soft monkey-like silhouette of light, no details); 2 a gold-white flash 12 squares, two gold slash streaks crossing in an X (mirrored); 3 a small white cloud puff bursting at the middle, gold sparks at mirrored places; 4 the puff and the sparks fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `wukong_fx_w_poof.png`：W 真假猴王：隐身的一团烟（他身上，不跟随），5 帧

他隐身冲走的那一下：在他站的地方嘭地冒出一团灰白色的烟（几团圆滚滚的烟朵），里面一道金色闪光，烟往两边和上面散开，留下分身站在原地（参考 MonkeyKing_Poof、P_Smoke01、P_SmokeErode、MonkeyKing_monkey_king_P）。**左右对称**，烟围着人，中间偏下可以盖住身体（the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-white smoke ramp (#F4F2EE, #D6D2CC, #AEA8A2, #86807C, #5E5A58, #3A3838) and an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: A SMOKE POOF round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): 1 a gold-white flash at the figure's chest 10 squares; 2 a burst of round grey-white smoke puffs (each puff 6-10 squares, white tops, grey shadows, no outline) round the figure 30 squares wide and 34 tall, covering it; 3 the puffs 40 wide, opening in the middle; 4 the puffs drifting out and up at both sides, thinning; 5 a few small wisps at the sides.
Layout: one horizontal row of 5 equal 44:50 cells, image size 3520x800 (each cell 704x800, 16 px a square); centered across, the figure's feet 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `wukong_fx_w_clone.png`：W 分身：站着（地上，不跟随），4 帧（每段 1/3 秒反复播）

留在原地的分身站着：**正面朝前**（脸对着看的人，左右对称），两只手叠在一起拄着竖立在身前正中的金箍棒（棒子立在两脚中间的地上，棒顶到胸口），尾巴从背后正中竖起来；轻轻地一起一伏（呼吸），尾巴尖左右摆一点也要对称（或者不摆）。**分身和悟空本人一模一样**（颜色、护臂、前襟、眼睛），参考 `design/wukong_idle.png`（他侧身的定稿，颜色和细节照它）和 `design/wukong_front_ref.png`（英雄联盟里他正面的样子）。**按游戏格子画**：头发尖到鞋底 38 格。

```text
Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, a 1-square near-black outline round the figure, flat 3-4 step shading per material, the colours of the attached design picture.
Effect: HIS DECOY CLONE: the SAME monkey king as the attached design picture (brown fur, spiky dark-brown hair, a pale monkey face with TWO GREEN EYES, a red scarf, huge gold-and-red arm guards with silver rosettes, a gold chest plate, a long gold tabard with a red border over a dark maroon robe, purple shoes, a long brown tail, his staff: red ends with gold bands and a grey steel middle) seen FROM THE FRONT, facing the viewer, SYMMETRIC LEFT TO RIGHT (the tail rising straight up behind his head), 38 squares from his hair to his soles (his feet on one ground line), in his own colours - the clone looks exactly like him. Standing still, 4 frames, a seamless loop: BOTH HANDS stacked on top of his staff, which stands upright on the ground in front of him between his feet (its top at his chest), his elbows out; 1 standing; 2 his body a square lower (breathing); 3 like 2; 4 like 1.
Layout: one horizontal row of 4 equal 44:48 cells, image size 2816x768 (each cell 704x768, 16 px a square); centered across, his soles 1 square above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `wukong_fx_w_clone_atk.png`：W 分身：出手打人（地上，不跟随），4 帧（1/3 秒）

分身每秒打一下身边的敌人：还是**正面朝前、左右对称**，两手横握金箍棒举过头顶，然后竖着往身前正中砸下去，砸到地上冒一点金光和尘土，再收回。分身和悟空一模一样，头发尖到鞋底 38 格。

```text
Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, a 1-square near-black outline round the figure, flat 3-4 step shading per material, the colours of the attached design picture.
Effect: HIS DECOY CLONE: the SAME monkey king as the attached design picture (brown fur, spiky dark-brown hair, a pale monkey face with TWO GREEN EYES, a red scarf, huge gold-and-red arm guards with silver rosettes, a gold chest plate, a long gold tabard with a red border over a dark maroon robe, purple shoes, a long brown tail, his staff: red ends with gold bands and a grey steel middle) seen FROM THE FRONT, facing the viewer, SYMMETRIC LEFT TO RIGHT (the tail rising straight up behind his head), 38 squares from his hair to his soles (his feet on one ground line), in his own colours - the clone looks exactly like him. A two-handed overhead smash, 4 frames: 1 both hands holding the staff LEVEL high above his head (the staff 36 squares long, centered); 2 the staff brought down halfway, still level, in front of his face; 3 the staff slammed down UPRIGHT in front of him in the middle (its foot on the ground between his feet), his body a square lower, a small gold flash and a puff of dust at its foot (mirrored); 4 standing again, both hands on the upright staff as in the standing pose.
Layout: one horizontal row of 4 equal 48:60 cells, image size 3072x960 (each cell 768x960, 16 px a square); centered across, his soles 1 square above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `wukong_fx_w_clone_spin.png`：W 分身：跟着大招转棒（地上，不跟随），4 帧（1/3 秒反复播）

悟空放大招时分身也跟着转：**正面朝前、左右对称**，两手在腰前横握伸长的金箍棒，棒子两头伸得很长，转起来：长、短（转到朝着看的人，看起来变短）、长、短，身边一圈橙金色的弧形风（参考 Wukong_Base_RStaffSwirl、Swirl3/4/5）。分身和悟空一模一样。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12). The figure: Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, a 1-square near-black outline round the figure, flat 3-4 step shading per material, the colours of the attached design picture.
Effect: HIS DECOY CLONE: the SAME monkey king as the attached design picture (brown fur, spiky dark-brown hair, a pale monkey face with TWO GREEN EYES, a red scarf, huge gold-and-red arm guards with silver rosettes, a gold chest plate, a long gold tabard with a red border over a dark maroon robe, purple shoes, a long brown tail, his staff: red ends with gold bands and a grey steel middle) seen FROM THE FRONT, facing the viewer, SYMMETRIC LEFT TO RIGHT (the tail rising straight up behind his head), 38 squares from his hair to his soles (his feet on one ground line), in his own colours - the clone looks exactly like him. Whirling his lengthened staff level at his waist with both hands, 4 frames, a seamless loop: 1 the staff LEVEL and LONG, 70 squares, centered; 2 the staff foreshortened (turned toward the viewer) to 24 squares; 3 like 1; 4 like 2; round him an orange-gold whirl of curved streaks (an ellipse 76 squares wide and 18 tall at his waist, crescent shapes, white edges, no outline) in every frame, turned a little each frame; the figure itself with a 1-square dark outline, the whirl without.
Layout: one horizontal row of 4 equal 84:48 cells, image size 5376x768 (each cell 1344x768, 16 px a square); centered across, his soles 1 square above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `wukong_fx_w_hit.png`：W 分身打中（目标身上），4 帧

分身的棒子打中敌人：比普攻小一点的金色闪光，带一点淡金色的残影（参考 Wukong_Base_Flicker、Glow2）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a LIGHT STAFF TAP on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale gold flash 4 squares; 2 a gold burst 9 squares with a white core; 3 a thin gold ring 11 squares, a few sparks at mirrored places; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `wukong_fx_r_on.png`：R 大闹天宫：转棒时身边的旋风（他身上，跟随，循环），4 帧

他伸长金箍棒转起来的时候，身边一圈橙金色的旋风：一圈扁扁的金色弧形风（几道月牙形的光，白色的亮边，像棒子转过留下的残影），脚下一圈淡淡的尘土，一帧一帧转（参考 Wukong_Base_RStaffSwirl、RStaffSwirl_、Swirl、Swirl3/4/5、MonkeyKing_staff_twirl、P_Swoop）。**左右对称**，中间身体位置留空（the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn，风圈在他腰和脚的高度绕一圈）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12) and a grey-white smoke ramp (#F4F2EE, #D6D2CC, #AEA8A2, #86807C, #5E5A58, #3A3838).
Effect: A WHIRLWIND OF STAFF STREAKS round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): an orange-gold ring of crescent-shaped light streaks (an ellipse 70 squares wide and 16 tall at the figure's waist, the streaks 1-2 squares thick with white edges, no outline), the middle 30 squares wide left empty where it crosses the body, a faint dust ring on the ground (an ellipse 56 wide and 8 tall); each frame the streaks moved along the ring (frame 4 flows back into frame 1).
Layout: one horizontal row of 4 equal 76:40 cells, image size 4864x640 (each cell 1216x640, 16 px a square); centered across, the figure's feet 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `wukong_fx_r_hit.png`：R 命中：被转棒扫中（目标身上），4 帧

被大闹天宫扫中的敌人：一道金色的弧形横扫闪光（左右对称的两道弧），中间白色，几颗火星（参考 Wukong_Base_Swirl、R_Suck_flash）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a SWEEPING STAFF HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 two gold crescent slashes curving away from the middle (mirrored, 14 squares across, white edges); 3 the crescents thinner and wider, gold sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `wukong_fx_p_stone.png`：被动金刚不坏：叠满 5 层时的石皮（他身上，跟随，循环），4 帧

金刚不坏叠满 5 层（护甲最高）时：他身边浮着几块灰色的小石片，绕着他慢慢转，石片上一闪一闪的白色高光，脚下一圈淡淡的灰色石尘（参考 P_Rocks、P_rock_debris、P_shield_circle）。**左右对称**，中间身体位置留空（the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn，石片只在身体两边和头顶上方）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey stone ramp (#F0ECE4, #CBC3B6, #A1978A, #786E64, #534B45, #322D2A).
Effect: FLOATING STONE CHIPS round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the monkey king, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): 6 small grey stone chips (3x3 to 4x4 squares, a light top face, a darker side, a 1-square dark outline: solid things) floating at both sides of the figure and over its head at mirrored places, a white glint on 2 of them; a faint grey dust ring at its feet (an ellipse 30 wide and 6 tall); each frame the chips bob up or down a square (mirrored).
Layout: one horizontal row of 4 equal square cells, image size 3200x800 (each cell 800x800, 16 px a square); centered across, the figure's feet 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `wukong_fx_a_hit` | view_effects `league_wukong_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `wukong_fx_q_hit` | view_effects `league_wukong_q_hit`（跟随，画在人物上面；左右对称） | 18 |
| `wukong_fx_q_shred` | view_buffs `league_wukong_q_shred`（跟随，画在人物上面；左右对称；循环） | 12 × 46 |
| `wukong_fx_e_cloud` | view_effects `league_wukong_e_cloud`（跟随，画在人物下面 z 2 前后都可；左右对称；大图表） | 56 × 24 |
| `wukong_fx_e_land` | view_effects `league_wukong_e_land`（不跟随，画在人物下面 z -1；左右对称；大图表） | 50 × 26 |
| `wukong_fx_e_hit` | view_effects `league_wukong_e_hit`（跟随，画在人物上面；左右对称） | 16 |
| `wukong_fx_w_poof` | view_effects `league_wukong_w_poof`（不跟随，画在人物上面 z 2；左右对称；大图表） | 44 × 50 |
| `wukong_fx_w_clone` | view_effects `league_wukong_w_clone`（不跟随，画在人物位置 z 1；**正面、左右对称**；大图表） | 44 × 48 |
| `wukong_fx_w_clone_atk` | view_effects `league_wukong_w_clone_atk`（不跟随；**正面、左右对称**；大图表） | 48 × 60 |
| `wukong_fx_w_clone_spin` | view_effects `league_wukong_w_clone_spin`（不跟随；**正面、左右对称**；大图表） | 84 × 48 |
| `wukong_fx_w_hit` | view_effects `league_wukong_w_hit`（跟随，画在人物上面；左右对称） | 12 |
| `wukong_fx_r_on` | view_buffs `league_wukong_r_on`（跟随，画在人物下面 z -1；左右对称；循环；大图表） | 76 × 40 |
| `wukong_fx_r_hit` | view_effects `league_wukong_r_hit`（跟随，画在人物上面；左右对称） | 16 |
| `wukong_fx_p_stone` | view_buffs `league_wukong_s_5`（tag p_stone；跟随，画在人物上面 z 2；左右对称；循环） | 50 × 50 |

- 两张表：`asset/league/effects/league_wukong_fx`（小的）和 `league_wukong_big`（e_cloud、e_land、w_poof、w_clone、w_clone_atk、w_clone_spin、r_on），tag = 名字（build_wukong.py 的 views；`p_stone` 绑 buff `league_wukong_s_5`）。
- `w_clone`、`w_clone_atk`、`w_clone_spin` 每段 20 tick（W 的 w_slot）：4 帧共 333 毫秒，分身站的地方由锚点（W 的 w_anchor）定，脚底对齐落点；`e_land`、`w_poof` 不跟随（晚播画面）。
- 用 `pixel_1x/` 切格（import_maokai_fx 的做法），断言左右对称；清掉 Codex 给光描的最深色边（分身、碎片、石片、盾牌保留描边）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。
