# 爆爆（金铲铲之战 · 双城之战）：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图和 3 个技能图标。** 造型和动作已定（`design/powder_idle.png`：3/4 正面朝右的 Q 版小女孩，亮蓝色乱蓬蓬的短发、两个金色 X 发夹、两条小辫子，青绿上衣、粉色袖子、深棕护臂、腰后一袋蓝色小炸弹、紫色裤袜、棕靴子）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），36 格高、22 格宽，游戏里显示成 90%；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/powder_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/powder_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里爆爆自己的特效贴图和她的猴子炸弹模型，按用在我们哪张特效分好了行，只在本地用，不要提交。颜色：**她的鞭炮和炸弹都是自制的**（红粉色的纸、黄铜、绳子），**猴子是蓝色的发条玩具**（黄铜钹、肉色的脸），**她的爆炸是橙金色的火加粉紫、蓝色的烟**，**海克斯水晶是青蓝色的光**。
> - **特效要亮**：每团光、每团火都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、头上、脚下、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（小鞭炮、猴子、水晶包）**在空中翻滚**：每帧转四分之一圈，游戏按飞行方向转这张图时怎么转都对。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `powder_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/powder_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/powder_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「伏击者」：技能炸弹可以暴击） | 扔一个自制小鞭炮 | `a_pop` · `a_hit` |
| 技能 1「猴子炸弹」 | 把发条猴子炸弹丢到目标脚下，中心全额、外圈减半，被炸到的灼烧 + 重伤 | `q_monkey` · `q_blast` · `q_hit` · `q_wound` |
| 技能 2「快跑，爆爆！」 | 敌方英雄靠近时摔下闪光烟雾弹，周围敌人致盲，自己向后跳开 | `e_smoke` · `e_blind` |
| 大招「海克斯水晶炸弹」 | 把装着海克斯水晶的包丢向敌方英雄，引线烧完蓝光大爆炸，击飞 | `r_cast` · `r_bag` · `r_warn` · `r_fuse` · `r_blast` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火星、烟、光圈、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**；**实物**（鞭炮、猴子、包、飞出去的零件和水晶碎片）有 1 格近黑描边。
- **要亮**：每个光或火的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 橙金色的火：`#FFFFFF`、`#FFF4B8`、`#FFD24A`、`#FF9A2A`、`#E2541E`、`#8E2A14`；
  - 粉紫色的烟：`#FFE6F4`、`#FFA8D8`、`#E066B8`、`#8E4AB8`、`#5A3A8C`、`#2E2246`；
  - 红粉色的鞭炮纸：`#FFD8D8`、`#FF7A8A`、`#E23A52`、`#A21E36`、`#5E1220`；
  - 黄铜：`#FFF2B0`、`#F2C850`、`#C8902A`、`#8A5A1A`、`#4A2E10`；
  - 蓝色的玩具猴：`#BFF0FF`、`#5ACBF5`、`#1E8ED8`、`#145AA8`、`#0C2E66`；
  - 青蓝色的海克斯水晶光：`#FFFFFF`、`#D8FBFF`、`#7FE8FF`、`#2FB8F0`、`#1A6FD0`、`#123C80`；
  - 绿色的毒液 / 漩涡眼：`#F0FFE0`、`#B8FF7A`、`#5AE85A`、`#22A04A`、`#10582A`；
- 打中、爆发居中画，不旋转；地面上的圆（警示圈、光、冲击波）是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，猴子炸弹的爆炸半径 32000，水晶炸弹 42000）。

### 1. `powder_fx_a_pop.png`：普攻：扔出去的小鞭炮（弹道，循环），4 帧

她普攻扔出去的自制小鞭炮：一根短短的红粉色纸筒，一头扎着黄铜色的引线，引线头冒着金黄的小火星。**在空中翻滚**（每帧转四分之一圈，游戏怎么转这张图都对），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-pink paper ramp (#FFD8D8, #FF7A8A, #E23A52, #A21E36, #5E1220), a brass ramp (#FFF2B0, #F2C850, #C8902A, #8A5A1A, #4A2E10) and an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14).
Effect: A HOMEMADE FIRECRACKER, 4 frames, a seamless loop, TUMBLING through the air: each frame the object a quarter turn further round (so the game may turn the picture any way - it always reads), a short spark trail: a short red-pink paper tube 6 squares long and 3 thick with a brass cap at each end and a lit fuse at one end throwing 3-4 gold spark squares.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `powder_fx_a_hit.png`：普攻：小鞭炮炸开（目标身上），3 帧

小鞭炮在目标身上啪地炸开：一团金白色的小闪光，四周溅出几粒红粉色的纸屑和火星（参考 jinx_skin60_ba_hit_impact、tar_flashglow）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14) and a red-pink paper ramp (#FFD8D8, #FF7A8A, #E23A52, #A21E36, #5E1220).
Effect: A SMALL FIRECRACKER POP, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold star flash 6 squares across; 2 the flash 9 across with 6 gold sparks and red-pink paper bits flying out; 3 only the bits and sparks further out, fading.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `powder_fx_q_monkey.png`：技能1 猴子炸弹：飞出去的猴子（弹道，循环），4 帧

她丢出去的发条猴子炸弹：一只蓝色的玩具猴，肉色的脸咧着大嘴笑，两只手各抓一片黄铜钹，背上一把发条钥匙，头顶一根点着的引线冒火星（参考 monkey_model、monkey_prop_tft13_blue）。**在空中翻滚**（每帧转四分之一圈），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue toy ramp (#BFF0FF, #5ACBF5, #1E8ED8, #145AA8, #0C2E66), a brass ramp (#FFF2B0, #F2C850, #C8902A, #8A5A1A, #4A2E10), an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14) and a peach skin ramp (#FFE2C8, #F2B08A, #C87A5A).
Effect: A WIND-UP TOY MONKEY BOMB, 4 frames, a seamless loop, TUMBLING through the air: each frame the object a quarter turn further round (so the game may turn the picture any way - it always reads), a short spark trail: a chubby blue toy monkey 12 squares tall, a round peach face with a wide toothy grin and two black eyes, a brass cymbal in each hand, a brass wind-up key on its back, a lit fuse on its head spitting 3 gold spark squares; 1-square near-black outline round the monkey.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `powder_fx_q_blast.png`：技能1：猴子炸弹爆炸（地上的点，不跟随，大图），6 帧

猴子炸弹落地爆炸：先一团白金色的大闪光，再炸成橙金色的火球，外面一圈粉紫色和蓝色的烟，碎钹、螺丝、玩具零件往外飞，最后烟散开（参考 broken_monkey_tft13_blue、olaf_skin16_explosion_smoke_mult、jinx_skin60_ba_hit_impact）。中心全额、外圈减半，所以爆炸要看得出一个亮的中心和一圈外围。**左右对称**，底部贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14), a pink-violet smoke ramp (#FFE6F4, #FFA8D8, #E066B8, #8E4AB8, #5A3A8C, #2E2246), a brass ramp (#FFF2B0, #F2C850, #C8902A, #8A5A1A, #4A2E10) and a blue toy ramp (#BFF0FF, #5ACBF5, #1E8ED8, #145AA8, #0C2E66).
Effect: A TOY BOMB EXPLOSION on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 12 squares across on the ground; 2 an orange-gold fireball 24 across, a bright white core 8 across; 3 the fireball 32 across, a ring of pink-violet and blue smoke puffs round it, 6 flying toy bits (brass cymbal halves, screws, blue toy pieces with outlines) at mirrored places; 4 the smoke ring 38 across, the fire shrinking inside it, the bits further out; 5 the smoke rising and thinning, a few embers; 6 only thin pink smoke wisps.
Layout: one horizontal row of 6 equal 40:34 cells, image size 3840x544 (each cell 640x544, 16 px a square); centered across, the blast's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `powder_fx_q_hit.png`：技能1：被炸到的敌人（他身上，跟随），4 帧

被猴子炸弹炸到的敌人：身上一团火焰冒起来，夹着几粒绿色的毒液飞溅（她的炸弹桶里冒的绿光，参考 tft13_blue_base_toxic_splashes2）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14) and a lime-green ramp (#F0FFE0, #B8FF7A, #5AE85A, #22A04A, #10582A).
Effect: A BURNING HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 8 squares across; 2 orange flames 12 across licking upward with 4 lime-green splash drops; 3 the flames 14 tall, flickering, the drops falling; 4 smaller flames and two green drops.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `powder_fx_q_wound.png`：技能1：灼烧 + 重伤（敌人身上，循环），4 帧

灼烧和重伤的 4 秒：敌人身上几小簇橙色的火苗一闪一闪，中间一个裂开的红色小十字（治疗被削弱）。**画在身体中段**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14) and a red ramp (#FFB0B0, #FF4A4A, #B01E2A, #5E0E16).
Effect: A BURN-AND-WOUND MARK, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 3 small orange flames (3 squares wide, 4 tall) at mirrored places flickering in turn, and in the middle a small red cross 5 squares across with a crack through it (solid, near-black outline) that pulses brighter on frames 2 and 4.
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `powder_fx_e_smoke.png`：技能2 快跑，爆爆！：脚下的闪光烟雾弹（她身上，跟随，大图），6 帧

她把闪光烟雾弹摔在脚下：先一下白色的闪光，再从她脚下往两边翻滚出一圈粉紫色、灰紫色的烟，几颗金色的火星迸出来，烟慢慢散开（参考 petchibikaisa_skin3_emote_smoke_trail、olaf_skin16_explosion_smoke_mult、tar_flashglow）。**只画在她脚下和两边，身体位置留空**，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet smoke ramp (#FFE6F4, #FFA8D8, #E066B8, #8E4AB8, #5A3A8C, #2E2246) and an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14).
Effect: A FLASH-SMOKE BOMB at a girl's feet, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small girl stands in the middle, not drawn: 32 squares from her crown to the ground, about 18 squares wide): 1 a white flash 10 squares across on the ground at her feet; 2 a white-pink flash 18 across and the first pink-violet smoke puffs low at both sides; 3 a low rolling smoke bank 34 squares wide and 10 tall round her feet and legs (her body above it left clear), 6 gold spark squares at mirrored places; 4 the smoke 38 wide billowing up to 14 tall at the outer sides; 5 the smoke thinning into puffs; 6 only a few pale puffs.
Layout: one horizontal row of 6 equal 40:26 cells, image size 3840x416 (each cell 640x416, 16 px a square); centered across, the smoke's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `powder_fx_e_blind.png`：技能2：致盲（敌人头上，跟随），4 帧

被闪光烟雾弹致盲的敌人：眼睛高度一圈灰紫色的烟带，几颗白色的小星星在里面转（看不见、打不了普攻）。**画在头部**，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet smoke ramp (#FFE6F4, #FFA8D8, #E066B8, #8E4AB8, #5A3A8C, #2E2246) and a white-gold sparkle ramp (#FFFFFF, #FFF4B8, #FFD24A).
Effect: A BLINDING SMOKE BAND at a unit's eye level, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a band of grey-violet smoke 14 squares wide and 4 tall, 3 tiny white four-pointed stars circling inside it at mirrored places, the band swelling a square on frames 2 and 3 and thinning on 4.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `powder_fx_r_cast.png`：大招 海克斯水晶炸弹：举起包时手上的蓝光（她身上，跟随），3 帧

她举起装着海克斯水晶的包的一下：一团青蓝色的水晶光闪起来，四周几粒蓝色的光点（参考 tft_set6_skin05_glow_64、energymote）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue hex crystal light ramp (#FFFFFF, #D8FBFF, #7FE8FF, #2FB8F0, #1A6FD0, #123C80).
Effect: A HEX CRYSTAL GLINT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small white-cyan diamond glint 5 squares tall; 2 a cyan-blue glow 10 across with a white core and 4 rays; 3 the glow fading, 6 blue motes drifting outward.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `powder_fx_r_bag.png`：大招：飞出去的水晶包（弹道，循环），4 帧

她丢出去的包：一个打着补丁的棕色帆布小包，袋口扎着绳子，缝隙里透出青蓝色的海克斯水晶光，绳头一根引线冒火星（参考 powder_prop_tft13_blue02）。**在空中翻滚**（每帧转四分之一圈），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue hex crystal light ramp (#FFFFFF, #D8FBFF, #7FE8FF, #2FB8F0, #1A6FD0, #123C80), a brass ramp (#FFF2B0, #F2C850, #C8902A, #8A5A1A, #4A2E10), an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14) and a brown canvas ramp (#E8C89A, #B88A5A, #7A5434, #46301E).
Effect: A HOMEMADE BOMB BAG, 4 frames, a seamless loop, TUMBLING through the air: each frame the object a quarter turn further round (so the game may turn the picture any way - it always reads), a short spark trail: a lumpy brown canvas sack 11 squares across with a patch and a brass-tied neck, cyan-blue crystal light glowing out of its seams (white-cyan squares in the cracks), a short lit fuse at the neck spitting 3 gold sparks; 1-square near-black outline round the sack.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `powder_fx_r_warn.png`：大招：落点的警示圈（地上，不跟随，循环），4 帧

包飞在空中时落点上的警示圈：地面上一个青蓝色的虚线椭圆，里面一圈细细的六边形纹路一闪一闪（参考 arcs、tft12_galio_base_r_glow）。**只画在地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue hex crystal light ramp (#FFFFFF, #D8FBFF, #7FE8FF, #2FB8F0, #1A6FD0, #123C80).
Effect: A GROUND WARNING RING, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat dashed ellipse 42 squares wide and 12 tall drawn in cyan-blue dashes 3 squares long, inside it a thinner hexagon outline in pale cyan; each frame the dashes move a step round and the hexagon pulses brighter on frames 2 and 4.
Layout: one horizontal row of 4 equal 44:16 cells, image size 2816x256 (each cell 704x256, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `powder_fx_r_fuse.png`：大招：落地后引线燃烧的包（地上的点，不跟随，循环），4 帧

包落在地上、引线还在烧：棕色的帆布包坐在地上，缝里的青蓝光一闪一闪越来越亮，袋口的引线冒着金色火星往下烧，下面一小片青蓝色的光（参考 powder_prop_tft13_blue02）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue hex crystal light ramp (#FFFFFF, #D8FBFF, #7FE8FF, #2FB8F0, #1A6FD0, #123C80), an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14) and a brown canvas ramp (#E8C89A, #B88A5A, #7A5434, #46301E).
Effect: A FIZZING BOMB BAG on the ground, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the brown canvas sack 11 squares across sitting upright on the ground (1-square near-black outline), its seams glowing cyan-blue - dim on frame 1, brighter each frame, white-cyan on frame 4; a lit fuse straight up from its neck spitting 2-4 gold spark squares at mirrored places; a flat cyan glow ellipse 14 wide and 2 tall under it.
Layout: one horizontal row of 4 equal 16:18 cells, image size 1024x288 (each cell 256x288, 16 px a square); centered across, the glow's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `powder_fx_r_blast.png`：大招：海克斯水晶大爆炸（地上的点，不跟随，大图），6 帧

那颗真炸了的炸弹：先一道白色的大闪光，再炸开一团巨大的青蓝色海克斯光球，蓝色的水晶碎片往外飞，外面一圈粉紫色的烟浪，地上一圈冲击波，最后蓝光散成光点（参考 tft_set6_skin05_lightningerosion03、tft_kennen_skin11_i_lightning03、olaf_skin16_explosion_smoke_mult）。**左右对称**，底部贴着地面，比猴子炸弹大得多、更亮。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue hex crystal light ramp (#FFFFFF, #D8FBFF, #7FE8FF, #2FB8F0, #1A6FD0, #123C80), a pink-violet smoke ramp (#FFE6F4, #FFA8D8, #E066B8, #8E4AB8, #5A3A8C, #2E2246) and an orange-gold fire ramp (#FFFFFF, #FFF4B8, #FFD24A, #FF9A2A, #E2541E, #8E2A14).
Effect: A HEX CRYSTAL EXPLOSION on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 16 squares across with 8 long rays; 2 a huge cyan-blue sphere of light 34 across, white core 14 across, crackling cyan arcs at its edge; 3 the sphere 44 across, 8 cyan crystal shards (solid diamonds with near-black outlines) flying out at mirrored places, a flat shockwave ellipse on the ground 50 wide; 4 a ring of pink-violet smoke 50 across round a fading blue core, shards further out; 5 the smoke rising and thinning, blue motes drifting up; 6 only motes and thin smoke.
Layout: one horizontal row of 6 equal 52:42 cells, image size 4992x672 (each cell 832x672, 16 px a square); centered across, the blast's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `powder_fx_r_hit.png`：大招：被炸飞的敌人（他身上，跟随），3 帧

被海克斯爆炸击飞的敌人：身上一团青蓝色的电火花炸开。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, rings or shockwaves (solid objects - the firecracker, the toy monkey, the bag, flying bits - keep a 1-square near-black outline), BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue hex crystal light ramp (#FFFFFF, #D8FBFF, #7FE8FF, #2FB8F0, #1A6FD0, #123C80).
Effect: A HEX SPARK HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 7 squares across; 2 cyan crackling sparks 12 across in 6 short jagged arcs; 3 only a few fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个）

每个图标一张 **64 × 64** 的像素画（**32 × 32 格、每格 2 px**），方形、画满整张、不透明背景，和游戏里技能图标一样：一个清楚的主体占中间大半，暗色的背景，1 格近黑描边，2–3 档平涂，不要文字。交付 `pixel_1x/powder_icon_<名字>.png`（64 × 64）。

### 1. `powder_icon_skill.png`：技能1 图标：猴子炸弹

蓝色发条猴子炸弹的头像（肉色的脸咧嘴笑，两片黄铜钹，头顶引线冒火星），背景暗橙色

```text
Pixel art skill icon for a small tactics game, 64x64 px (a 32x32 grid of 2-px squares), square, filled edge to edge with an opaque dark background, one clear bold subject filling most of it, a 1-square near-black outline on the subject, 2-3 flat shades a material, a white or brightest highlight, no text, no border, no anti-aliasing. Subject: the head of a blue wind-up toy monkey bomb - a peach face with a wide toothy grin, a brass cymbal on each side, a lit fuse on top spitting gold sparks - on a dark orange background
```

### 2. `powder_icon_skill2.png`：技能2 图标：快跑，爆爆！

一颗砸在地上冒出粉紫色烟和白色闪光的烟雾弹，旁边一道往回跑的蓝色速度线，背景暗紫色

```text
Pixel art skill icon for a small tactics game, 64x64 px (a 32x32 grid of 2-px squares), square, filled edge to edge with an opaque dark background, one clear bold subject filling most of it, a 1-square near-black outline on the subject, 2-3 flat shades a material, a white or brightest highlight, no text, no border, no anti-aliasing. Subject: a smoke bomb smashing on the ground in a burst of pink-violet smoke and a white flash, a blue speed streak running away from it to the left - on a dark violet background
```

### 3. `powder_icon_ult.png`：大招 图标：海克斯水晶炸弹

一个透出青蓝色强光的棕色帆布包，缝里亮着海克斯水晶，引线冒火星，背景深蓝色

```text
Pixel art skill icon for a small tactics game, 64x64 px (a 32x32 grid of 2-px squares), square, filled edge to edge with an opaque dark background, one clear bold subject filling most of it, a 1-square near-black outline on the subject, 2-3 flat shades a material, a white or brightest highlight, no text, no border, no anti-aliasing. Subject: a lumpy brown canvas bomb bag blazing with cyan-blue hex crystal light out of its seams, a lit fuse spitting gold sparks - on a deep blue background
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `powder_fx_a_pop` | view_projectiles `tft_powder_a_pop`（跟着弹道转向；翻滚） | 10 × 10 |
| `powder_fx_a_hit` | view_effects `tft_powder_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `powder_fx_q_monkey` | view_projectiles `tft_powder_q_monkey`（跟着弹道转向；翻滚） | 16 × 16 |
| `powder_fx_q_blast` | view_effects `tft_powder_q_blast`（不跟随，画在人物上面 z 2；左右对称；大图表） | 40 × 34 |
| `powder_fx_q_hit` | view_effects `tft_powder_q_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `powder_fx_q_wound` | view_buffs `tft_powder_q_wound`（跟随，画在人物上面 z 3；左右对称；循环） | 14 × 10 |
| `powder_fx_e_smoke` | view_effects `tft_powder_e_smoke`（CasterViewEffect，跟随她，画在人物上面 z 2；左右对称；大图表） | 40 × 26 |
| `powder_fx_e_blind` | view_effects `tft_powder_e_blind`（跟随目标，画在人物上面 z 3；左右对称） | 16 × 10 |
| `powder_fx_r_cast` | view_effects `tft_powder_r_cast`（CasterViewEffect，跟随她，画在人物上面 z 3；左右对称） | 14 × 14 |
| `powder_fx_r_bag` | view_projectiles `tft_powder_r_bag`（跟着弹道转向；翻滚） | 16 × 16 |
| `powder_fx_r_warn` | view_effects `tft_powder_r_warn`（ParabolicProjectile 的落点提示，画在人物下面 z -2；左右对称；大图表） | 44 × 16 |
| `powder_fx_r_fuse` | view_effects `tft_powder_r_fuse`（不跟随，画在人物下面 z -1；左右对称；每 9 tick 重放） | 16 × 18 |
| `powder_fx_r_blast` | view_effects `tft_powder_r_blast`（不跟随，画在人物上面 z 2；左右对称；大图表） | 52 × 42 |
| `powder_fx_r_hit` | view_effects `tft_powder_r_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 14 |

- 两张表：`asset/tft/effects/tft_powder_fx`（小的）和 `tft_powder_big`（q_blast、e_smoke、r_warn、r_blast），tag = 名字（build_powder.py 的 views）。
- 弹道图（a_pop、q_monkey、r_bag）翻滚不查对称，其余断言左右对称；`r_fuse` 不跟随（每 9 tick 重放），`q_blast` / `r_blast` 不跟随。
- 图标：`tft/icons/tft_powder_skill.png` / `_skill2` / `_ult`（64 × 64）。
- 用 `pixel_1x/` 切格（import_rammus_fx 的做法）；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
