# 诺克萨斯统领 斯维因：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/swain_idle.png`：3/4 正面朝右的高个将军，银白长发，近黑紫灰长大衣、暗红内衬，古铜胸甲；右边是他化身恶魔的样子：画面右边那只手是赤红的恶魔手臂，眼睛发红光，身后的黑红翅膀是大招期间的光环，**翅膀 Claude 自己做，不用画**）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），41 格高、26 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/swain_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/swain_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。**他出招用的是画面右边那只恶魔手**（普攻、Q、E 都从这只手的手掌射出）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里斯维因自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**恶魔的魂火是深红（白芯）**，**恶魔手和闪电带亮洋红**，**乌鸦、烟和恶魔的影子是黑紫色**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。
> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bolt`、`q_bolts`、`e_out`、`e_back` 都画成朝右，**上下对称**（往左时会上下翻）。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `swain_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `swain_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「狂食鸦群」 | 恶魔手射出乌鸦弹；打中英雄、W 和 E 抓到英雄、英雄阵亡时，乌鸦叼来魂屑：回血、加最大生命 | `a_bolt` · `a_hit` · `p_frag` |
| 技能 1 = Q「解脱之触」 | 恶魔手往前射出五道扇形散开的恶魔闪电 | `q_bolts` · `q_hit` |
| 技能 2 = E「永不复行」 | 恶魔之手飞出去再飞回来，路上的敌人被禁锢，被禁锢的英雄被拽近 | `e_out` · `e_back` · `e_hit` · `e_pull` |
| 被动自动放的 W「帝国视界」 | 远处地上睁开一只恶魔之眼，1.5 秒后爆炸、减速 | `w_eye` · `w_hit` |
| 大招「恶魔升华」 | 化身恶魔（身后黑红翅膀），持续吸取周围敌人的生命，再放出恶魔耀光（魂火新星） | `r_cast` · `r_drain` · `r_flare` · `r_fl_hit`（翅膀光环 Claude 做） |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（乌鸦和羽毛例外：实心的东西可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 深红魂火：`#FFFFFF`、`#FFD6E0`、`#FF6B8A`、`#E0204A`、`#9E0F2F`、`#4A0614`；
  - 亮洋红（恶魔爪、闪电）：`#FFFFFF`、`#FFC8F0`、`#FF5FD2`、`#D9208F`、`#7A0F52`；
  - 黑紫（乌鸦、烟、恶魔的影子）：`#9A86B8`、`#5E4E7A`、`#3A2D52`、`#22182F`、`#120B1A`；
  - 蓝紫（只用在恶魔耀光的内缘）：`#FFFFFF`、`#E2D4FF`、`#A88BFF`、`#6A4BE0`、`#3A2290`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 52000，解脱之触扇形 62000 长，永不复行 70000 长，帝国视界半径 30000，恶魔升华吸取和恶魔耀光半径 60000）。

### 1. `swain_fx_a_bolt.png`：普攻：恶魔手射出的乌鸦弹（飞行，循环），4 帧

从恶魔手掌心射出的一只**小乌鸦**：从上往下看的黑紫色乌鸦，两只翅膀**上下对称**地张开，胸口一团红白色的魂火，身后拖一小段深红尾迹，翅膀一扇一扇（参考 BA_Front、BA_mis_trail、BA_leadingedge_add）。**朝右飞，上下对称**。约 10 格长。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A) and a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614).
Effect: a small RAVEN OF SOULFIRE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a black-violet raven seen from above, its head (2 squares) pointing right, its two wings spread symmetrically up and down (each 3 squares long, the wing tips beating: open, half, closed, half), a crimson-white glowing core at its chest (2 squares, white centre), a short crimson trail of 3 fading squares behind its tail.
Layout: one horizontal row of 4 equal 12:9 cells, image size 768x144 (each cell 192x144, 16 px a square); the raven's beak 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `swain_fx_a_hit.png`：普攻命中（目标身上），4 帧

乌鸦弹打中：一团深红的魂火炸开，四片黑羽毛往外飞散（参考 BA_Flash_sharp、BA_Spark_cas）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: a SOULFIRE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 a crimson burst 8 squares with a white core; 3 the burst 10 squares, 4 small black-violet feathers (2 squares each) flying out at mirrored places; 4 fading crimson motes and two falling feathers.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `swain_fx_q_bolts.png`：Q 解脱之触：五道恶魔之力扇形飞出（飞行，播一次），5 帧

五道**深红到洋红的恶魔闪电**一起朝前飞、越飞越散开成扇形：第 1 帧五道挤在一起，到第 5 帧上下张开约 18 格；每道是一条带白芯的闪电短箭（参考 Q_lightning2、Q_lightning3、Q_energyBall）。**朝右飞，上下对称**（中间一道，上下各两道对称）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52).
Effect: FIVE DEMONIC LIGHTNING BOLTS flying to the RIGHT and fanning out, 5 frames, played once, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): five short bolts pointing right (each a jagged crimson-magenta lightning streak 6 squares long with a white core, a bright head at its right end), one in the middle and two above and two below it, symmetric: frame 1 their heads 2 squares apart (the five bunched, 9 squares tall in all), 2 four squares apart, 3 six, 4 eight, 5 nine squares apart (the fan 19 squares tall), the bolts a little longer each frame.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); the bolts' heads 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `swain_fx_q_hit.png`：Q 命中（目标身上），4 帧

恶魔闪电打中：一团洋红深红的闪电炸开，几道细闪电往外窜（参考 Q_hit_flash、Q_hit_flash_large、Q_Crack）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52).
Effect: a DEMONIC LIGHTNING HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-magenta flash 4 squares; 2 a crimson burst 10 squares with a white core and 4 short magenta lightning forks at mirrored places; 3 the burst 12 squares, the forks longer; 4 fading crimson sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `swain_fx_e_out.png`：E 永不复行：飞出去的恶魔之手（飞行，循环），4 帧

一只**张开的恶魔手**朝前飞：深红到洋红的魂火手掌，五根长爪**上下对称**地张开（中间一根朝前，上下各两根），身后拖一团黑紫色的烟（参考 E_birdshape、E_birdshape2_tip、E_wisps）。**朝右飞，上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52) and a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: an OPEN DEMON HAND flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a spectral palm of crimson-magenta soulfire (6 squares, a white core) with five long curved claws reaching forward and spreading symmetrically up and down (the middle claw 6 squares long pointing right, two above and two below curving outward, each 4-5 squares, bright magenta tips), a trail of black-violet smoke and crimson wisps 6 squares long behind the palm, flickering.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); the middle claw's tip 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `swain_fx_e_back.png`：E：恶魔之手收回来（飞行，循环），4 帧

同一只恶魔手**攥着往回飞**：爪子收拢成一个钩爪（上下对称），身后的烟更长更乱（参考 E_return_mis_mult、E_turning_mis_flash）。画成**朝右飞、上下对称**（游戏会把它转向飞回的方向）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52) and a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: the DEMON HAND CLOSING as it flies back, drawn flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): the same crimson-magenta palm (6 squares, white core) with its five claws curled forward into a hooked grasp (symmetric up and down, the claw tips meeting in front of the palm), a longer trail of black-violet smoke and crimson wisps 8 squares behind it, flickering.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); the claws' front 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `swain_fx_e_hit.png`：E 命中：被禁锢（目标身上，1.5 秒），6 帧

从地面伸出几只**深红的恶魔爪**抓住目标的腿，黑紫色的烟缠在脚边，最后三帧保持抓住的样子（参考 E_hit_ground、E_Tar_BlastShapes、E_Deathshards）。**左右对称**，中间身体位置留空（an upright figure 14 squares wide and 24 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: DEMON CLAWS ROOTING a unit, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 14 squares wide and 24 tall stands in the middle, not drawn): 1 a crimson crack ring on the ground round the feet (an ellipse 16 squares wide, 4 tall); 2 four crimson-magenta claws rising out of it at mirrored places beside the legs (each 5 squares tall); 3 the claws 9 squares tall curling in over the shins, black-violet smoke at the feet; 4-6 the claws closed round the legs (up to knee height), flickering softly, the smoke curling (frames 4-6 nearly the same: the hold).
Layout: one horizontal row of 6 equal 24:28 cells, image size 2304x448 (each cell 384x448, 16 px a square); centered across, the ground ring's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `swain_fx_e_pull.png`：E 拉拽（目标身上），4 帧

目标被拽向斯维因时：一团深红的魂火炸开，几片黑羽毛和魂火往两边甩（参考 E_DemonDrainSwoosh、E_Explode_Shards）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: a SOUL TORN OUT of a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-crimson flash 5 squares at its chest; 2 a crimson burst 12 squares, a small crimson soul shard (3 squares, white core) at the top; 3 the burst ring 14 squares, 6 black-violet feathers flung out at mirrored places, the shard higher; 4 fading crimson wisps.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `swain_fx_w_eye.png`：W 帝国视界：地上睁开的恶魔之眼（地上，不跟随，约 1.6 秒），8 帧

地上睁开一只**巨大的恶魔之眼**（从斜上方看，是个扁的椭圆）：先是一道深红裂缝，眼皮张开，露出黑紫色的眼白圈和发光的深红虹膜、白色竖瞳，一闪一闪地盯着，最后一帧收缩后爆成一团深红的光柱（参考 W_Eye_Alpha_V02、W_Eye_Alpha_V03、W_Explode_Iris、W_Ground_Circle_Alpha_V01、W_portal_ring_colors、W_Pulses_V02）。**左右对称**。约 60 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: a GIANT DEMON EYE OPENING ON THE GROUND seen from above at an angle, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin crimson crack 30 squares wide on the ground; 2 the crack opening into an almond-shaped eye 40 squares wide and 8 tall, dark lids with a crimson rim; 3 the eye 56 squares wide and 16 tall: a black-violet sclera ring, a glowing crimson iris (an ellipse 20 wide and 10 tall) with a white vertical slit pupil (2 squares wide, 8 tall), a faint crimson glow ring round the whole eye; 4 the same, the iris brighter, two thin magenta pulse rings round it; 5 the same as 3; 6 the same as 4; 7 the eye narrowing to a slit, the iris a bright white-crimson line; 8 a burst: a white-crimson flash ellipse 50 squares wide and 14 tall on the ground with a light column 12 squares wide and 20 tall rising from its middle.
Layout: one horizontal row of 8 equal 64:40 cells, image size 8192x640 (each cell 1024x640, 16 px a square); centered across, the eye's middle 10 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `swain_fx_w_hit.png`：W 命中（目标身上），4 帧

恶魔之眼爆炸打中：一团深红的光炸开，一圈洋红的波纹往外扩（减速），参考 W_Flash_tar、W_Spark_cas。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52).
Effect: an EYE BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a crimson burst 10 squares with a white core; 3 a magenta ripple ring 12 squares round it, crimson sparks; 4 the ring fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `swain_fx_p_frag.png`：被动 狂食鸦群：乌鸦叼来魂屑（他身上，跟随），6 帧

两只**小黑乌鸦**从左右两边飞进来，各叼着一团深红的魂屑，飞到他胸口时魂屑合成一团红光被吸进身体，乌鸦往上飞走（参考 W_Raven_TX_CM、Z_SoulWispsAlpha、R_Feathers）。**左右对称**，中间身体位置留空（an upright figure 26 squares wide and 40 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A) and a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614).
Effect: TWO RAVENS BRINGING A SOUL FRAGMENT to a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 26 squares wide and 40 tall stands in the middle, not drawn): 1 two small black-violet ravens (5 squares each, wings spread) at the left and right edges at chest height, each carrying a crimson soul spark (2 squares, white core); 2 the ravens halfway in; 3 the ravens at the figure's sides, the sparks touching its chest; 4 the sparks merged into one crimson glow 6 squares at the chest middle, the ravens rising; 5 the glow sinking into the chest (smaller), the ravens higher at the top corners; 6 a few crimson motes, the ravens leaving the cell.
Layout: one horizontal row of 6 equal square cells, image size 4224x704 (each cell 704x704, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `swain_fx_r_cast.png`：R 恶魔升华：变身爆发（他身上，不跟随），6 帧

他化身恶魔的一瞬间：一圈深红的魂火和黑羽毛从他身上往外爆开，地上裂出一圈红色裂纹，几道深红闪电往上窜（参考 R_Cast_Dust_v03、R_Cas_Symbol_V01、R_Lightning、R_Shockwave、R_Feathers）。**左右对称**，中间身体位置留空（an upright figure 26 squares wide and 40 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: a DEMONIC TRANSFORMATION BURST round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 26 squares wide and 40 tall stands in the middle, not drawn): 1 a crimson flash ring on the ground round the feet (an ellipse 20 wide, 5 tall); 2 black-violet smoke and crimson soulfire bursting out on both sides of the figure up to its shoulders, a ring of red ground cracks 36 squares wide; 3 the burst at its widest: soulfire flames 16 squares tall on both sides, 6 crimson-magenta lightning bolts rising at mirrored places above the shoulders, 10 black-violet feathers flying out; 4 the flames lower, the feathers further out; 5 smoke and falling feathers; 6 fading cracks and embers.
Layout: one horizontal row of 6 equal 56:52 cells, image size 5376x832 (each cell 896x832, 16 px a square); centered across, the figure's feet (the ground ring's middle) 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `swain_fx_r_drain.png`：R 吸取（被吸的目标身上，跟随），4 帧

被恶魔吸取：目标身上冒出几缕深红的魂魄往上飘、打着旋（参考 R_DemonDrainSwoosh、R_drainRing、R_Absorb_Scroll_Alpha）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: SOUL WISPS DRAWN OUT of a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): crimson soul wisps (each a curl 2 squares wide and 5 tall, white core) rising from the unit's chest at mirrored places, spiralling up and fading at the top; a faint black-violet smoke ring round the chest; each frame the wisps a little higher (a loop that also reads played once).
Layout: one horizontal row of 4 equal 16:22 cells, image size 1024x352 (each cell 256x352, 16 px a square); centered across, the wisps' start 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `swain_fx_r_flare.png`：R 恶魔耀光：魂火新星（他身上，不跟随），6 帧

举起恶魔爪放出的**魂火新星**：从他身上炸开一圈深红的火环（内缘蓝紫色，和英雄联盟的恶魔耀光一样），在地上（从斜上方看的扁椭圆）越扩越大，环上跳着洋红的闪电，最后剩一圈余烬（参考 R_Nova_Mis_Core、R_Nova_Mis_Energy、R_Nova_Mis_Front、R_Nova_Mis_Dark_Background、R_Ring_Shockwave）。**左右对称**，环的中间留空（an upright figure 26 squares wide and 40 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a violet-blue ramp (#FFFFFF, #E2D4FF, #A88BFF, #6A4BE0, #3A2290) and a hot magenta ramp (#FFFFFF, #FFC8F0, #FF5FD2, #D9208F, #7A0F52).
Effect: a NOVA OF SOULFIRE spreading on the ground round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 26 squares wide and 40 tall stands in the middle, not drawn): 1 a white and violet-blue flash 12 squares at the figure's chest; 2 a ring of crimson fire on the ground (an ellipse 40 wide, 12 tall, flames 4 squares tall) with a violet-blue inner edge; 3 the ring 72 wide and 22 tall, crimson flames with a violet-blue inner glow, magenta lightning crackling on it at mirrored places; 4 the ring 100 wide and 30 tall, the flames 6 squares tall; 5 the ring 116 wide and 36 tall, thinner; 6 a fading ring of crimson and violet embers.
Layout: one horizontal row of 6 equal 124:56 cells, image size 11904x896 (each cell 1984x896, 16 px a square); centered across, the ring's middle (the figure's feet) 18 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `swain_fx_r_fl_hit.png`：R 恶魔耀光命中（目标身上），4 帧

被魂火新星打中：一团深红的火焰炸开，暗紫色的火星往外飞（减速），参考 R_tar_Flash、R_Tar_Impact。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson soulfire ramp (#FFFFFF, #FFD6E0, #FF6B8A, #E0204A, #9E0F2F, #4A0614) and a black-violet shadow ramp (#9A86B8, #5E4E7A, #3A2D52, #22182F, #120B1A).
Effect: a SOULFIRE BURN on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-crimson flash 5 squares; 2 crimson flames 12 squares rising round the unit's middle with a white core; 3 the flames 14 squares, dark violet sparks flying out at mirrored places; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `swain_fx_a_bolt` | view_projectiles `league_swain_a_bolt`（朝目标飞，画面随方向转；上下对称） | 10 × 7 |
| `swain_fx_a_hit` | view_effects `league_swain_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `swain_fx_q_bolts` | view_projectiles `league_swain_q_bolts`（朝目标飞，画面随方向转；上下对称；不循环） | 20 × 20 |
| `swain_fx_q_hit` | view_effects `league_swain_q_hit`（跟随，画在人物上面；左右对称） | 12 |
| `swain_fx_e_out` | view_projectiles `league_swain_e_out`（朝目标飞，画面随方向转；上下对称） | 16 × 14 |
| `swain_fx_e_back` | view_projectiles `league_swain_e_back`（飞回斯维因，画面随方向转；上下对称） | 16 × 14 |
| `swain_fx_e_hit` | view_effects `league_swain_e_hit`（跟随，画在人物脚下到腰；左右对称） | 22 × 26 |
| `swain_fx_e_pull` | view_effects `league_swain_e_pull`（跟随，画在人物上面；左右对称） | 14 |
| `swain_fx_w_eye` | view_effects `league_swain_w_eye`（不跟随，画在人物下面；左右对称；大图表） | 60 × 36 |
| `swain_fx_w_hit` | view_effects `league_swain_w_hit`（跟随，画在人物上面；左右对称） | 12 |
| `swain_fx_p_frag` | view_effects `league_swain_p_frag`（跟随，画在人物上面；左右对称） | 40 × 40 |
| `swain_fx_r_cast` | view_effects `league_swain_r_cast`（他身上播一次，不跟随；左右对称；大图表） | 56 × 52 |
| `swain_fx_r_drain` | view_effects `league_swain_r_drain`（跟随，画在人物上面；左右对称） | 14 × 20 |
| `swain_fx_r_flare` | view_effects `league_swain_r_flare`（他身上播一次，不跟随；左右对称；大图表） | 120 × 52 |
| `swain_fx_r_fl_hit` | view_effects `league_swain_r_fl_hit`（跟随，画在人物上面；左右对称） | 14 |

- 两张表：`asset/league/effects/league_swain_fx`（小的）和 `league_swain_big`（w_eye、r_cast、r_flare，还有 Claude 从 B-1 的翅膀做的 `r_wings` 光环），tag = 名字（build_swain.py 的 views；r_wings 绑在 buff `league_swain_r_on`）。
- 投射物 `a_bolt`、`q_bolts`、`e_out`、`e_back` 画面朝方向转；`w_eye`、`r_cast`、`r_flare` 不跟随（地上 / 他身上的晚播画面，红色方规则）；`w_eye`、`e_hit` 的地面部分画在人物下面（z -1）。
- 用 `pixel_1x/` 切格（import_rell_fx / import_urgot_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
