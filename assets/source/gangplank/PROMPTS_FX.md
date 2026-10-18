# 普朗克：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和动作已定（`design/gangplank_idle.png`：3/4 正面朝右的海盗船长，黑色月牙海盗帽、花白长胡子，青绿领子、赤膊，红腰带，背后深紫长外套，近侧手把金色手炮扛在肩上，远侧手拿一把刀尖烧红的锯齿弯刀）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连弯刀 42 格高、39 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/gangplank_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/gangplank_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里普朗克自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**被动和刀是烧红的橙色火**，**手枪的火光和金币是金色**，**火药桶是棕色木桶加黑铁箍、爆炸是橙黄色的火加黑灰色火药烟**，**W 是橘子的柑橘橙**，**大招的范围是焦橙红色，炮弹是黑铁色**。
> - **特效要亮**：每团光、每次爆炸都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **飞行中的东西（q_bullet 子弹、e_throw 火药桶）上下对称**：游戏会把飞行的图按飞的方向转，往左飞时整张图上下翻过来。
> - **q_flash 枪口火光、w_cast 橘子、r_cast 信号弹三张会画进他自己的动作帧**（会跟着他一起翻面），所以可以有方向，按每条写的朝向画。
> - **其余全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他朝左时也是同一张图。
> - **围着人的画面中间身体位置留空**，不要盖住人。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `gangplank_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的名字 `name`、帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/gangplank_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/gangplank_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「烈火审讯」 | 弯刀砍；每隔一段时间下一刀点燃敌人（真实伤害的灼烧），自己加速 | `a_hit` · `p_hit` · `p_ms` |
| 技能 1 = Q「枪火谈判」 | 手枪平端开一枪（会暴击、带被动），打中能引爆旁边能引爆的火药桶 | `q_flash`（画进动作） · `q_bullet` · `q_hit` |
| 技能 2 = E「火药桶」 | 把火药桶扔到敌人脚下，落地 1 秒后引线点着；被他的枪或刀引爆，炸伤并减速范围里的敌人 | `e_throw` · `e_land` · `e_keg` · `e_keg_lit` · `e_boom` · `e_hit` · `e_slow` |
| 自动吃的 W「坏血病疗法」 | 被控住或被围时咬一口橘子，回血并短暂免控 | `w_cast`（画进动作） · `w_imm` |
| 大招「加农炮幕」 | 朝天打信号弹，海上的船往一大片范围里一波一波地砸炮弹（12 波、6 秒），每波伤害并减速 | `r_cast`（画进动作） · `r_warn` · `r_wave` · `r_hit` · `r_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：火药桶、炮弹、橘子可以有一圈深色边）。
- **要亮**：每个光和火的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 火和火星（所有爆炸、灼烧、刀痕）：`#FFFFFF`、`#FFF6C0`、`#FFD25A`、`#FF9A28`、`#E2541A`、`#8E2410`；
  - 金色光（手枪火光、金币、加速）：`#FFFFFF`、`#FFF4C8`、`#FFD86A`、`#F2A82E`、`#B86A18`、`#5E3008`；
  - 木头（火药桶、木屑）：`#F2D2A2`、`#C89058`、`#94602E`、`#64401E`、`#3E2612`、`#1E120A`；
  - 黑铁（铁箍、炮弹）：`#E8E8EC`、`#A8AAB2`、`#6E727C`、`#464A52`、`#2A2C32`、`#141418`；
  - 火药烟和尘土：`#F4F0EA`、`#CFC8BE`、`#A29A90`、`#756E68`、`#4A4644`、`#262424`；
  - 柑橘橙（橘子、W 的光，叶子用 #7CC24A / #3E7A28）：`#FFFFFF`、`#FFF2B0`、`#FFD04A`、`#FF9E1E`、`#E06A10`、`#8A3A08`；
  - 焦橙红（大招范围、信号弹）：`#FFFFFF`、`#FFD0B0`、`#FF8A4A`、`#E2481E`、`#A0241A`、`#56100C`；
- 打中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：火药桶爆炸半径 30000，大招范围半径 44000）。

### 1. `gangplank_fx_a_hit.png`：普攻命中：弯刀砍中（目标身上），4 帧

弯刀砍中：两道交叉的橙红色灼热刀痕（一个 X），白色的芯，几粒火星往外飞（参考 BA_sword_trail、P_sword_blade、hit_sparks）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a CUTLASS SLASH HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 two crossed orange-hot slash streaks (an X 10 squares, one stroke the mirror of the other) with a white core; 3 the X 12 squares fading, sparks flying out at mirrored places; 4 two embers drifting.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `gangplank_fx_p_hit.png`：被动「烈火审讯」点燃（目标身上），5 帧

被动的那一刀点着了敌人：先一下白黄色的闪光，然后橙色的火苗从敌人身上往上窜，两边各几道火舌，火星往上飘，最后火小下去冒点烟（参考 P_sword_flames、taunt_flames）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a FIRE IGNITION on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares; 2 orange flames bursting up 10 squares from the middle; 3 flames 14 squares tall licking up both sides (mirrored), embers rising; 4 the flames dying down, embers floating up; 5 small flames and a little grey smoke.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `gangplank_fx_p_ms.png`：被动加速（他脚下，2 秒，循环），4 帧

被动点着敌人后他跑得更快：脚下两边几道白金色的速度线（参考 P_speedstreaks），一闪一闪。**左右对称**（两边都画），只画在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD86A, #F2A82E, #B86A18, #5E3008).
Effect: SPEED STREAKS at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three short white-gold streak lines on each side of the feet (the middle 8 squares left clear), 3-7 squares long, low along the ground; they slide outward and fade in turn so the loop flows.
Layout: one horizontal row of 4 equal 22:8 cells, image size 1408x128 (each cell 352x128, 16 px a square); centered across, the streaks' lowest row on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `gangplank_fx_q_flash.png`：Q 枪火谈判：枪口火光（画进他开枪那一帧），3 帧

开枪时炮口喷出的火光：炮口（格子左边中间）一团白黄色的星形闪光，往右喷出一锥橙黄色的火焰，接着一团灰色的火药烟（参考 cast_muzzleflash、Gangplank_base_cast_muzzelflash、q_smoketrail）。（这张画进他自己的动作帧，会跟着他一起翻，所以可以有方向），**朝右画**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD86A, #F2A82E, #B86A18, #5E3008) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a MUZZLE FLASH from a cannon pointing RIGHT, 3 frames (drawn into his own action frames, which the game mirrors with him, so it may point one way): 1 a white-yellow star burst 6 squares at the cell's left edge (the muzzle) with a cone of white-gold flame 8 squares pointing right; 2 the cone 14 squares orange-gold with sparks flying ahead; 3 a grey powder smoke puff 8 squares drifting right, two embers.
Layout: one horizontal row of 3 equal 16:12 cells, image size 768x192 (each cell 256x192, 16 px a square); the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `gangplank_fx_q_bullet.png`：Q 子弹（飞行中），2 帧循环

飞出去的子弹：一颗发白金色光的圆弹（约 3 格），身后（左边）拖一小段橙金色的光尾（参考 Q_missile_bullet、q_smoketrail）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD86A, #F2A82E, #B86A18, #5E3008) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a PISTOL SHOT in flight, 2 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over): a glowing white-gold round shot 3 squares with a short orange-gold trail 6 squares behind it (to the left, mirrored top to bottom); the trail flickers between the frames.
Layout: one horizontal row of 2 equal 10:6 cells, image size 320x96 (each cell 160x96, 16 px a square); it flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `gangplank_fx_q_hit.png`：Q 打中（目标身上），4 帧

子弹打中：白光一闪，一团橙金色的火光带几道星芒，然后两枚金币从两边弹起来一闪（枪火谈判会抢金币，参考 Q_tar_hitflash、Q_coin、q_tar_sparks）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD86A, #F2A82E, #B86A18, #5E3008) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a SHOT HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 an orange-gold burst 9 squares with four short star rays; 3 the burst 12 squares fading, two GOLD COINS (3 squares each, a white glint) popping up at mirrored places; 4 the coins higher and glinting, two embers.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `gangplank_fx_e_throw.png`：E 火药桶（飞行中），3 帧循环

扔到敌人脚下的火药桶：一个小木桶横躺着顺着飞行方向（约 8 格长、6 格高，两道深色铁箍竖着），**上下对称**，所以桶上不画图案；三帧里木纹高光轮换，像在翻滚。木桶是实心的，可以有一圈深色边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A) and a dark iron ramp (#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418).
Effect: a POWDER KEG in flight, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over): a small wooden barrel lying along the flight, 8 squares long and 6 tall, two dark iron hoops across it, bulging in the middle; the stave highlights shift each frame as if it tumbles. Solid: a 1-square dark outline round the barrel is allowed.
Layout: one horizontal row of 3 equal 12:10 cells, image size 576x160 (each cell 192x160, 16 px a square); it flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `gangplank_fx_e_land.png`：E 火药桶落地（地上，不跟随），4 帧

桶落地：地上往两边溅起一圈灰尘（参考 E_barrel_smoke、E_ground_shadow）。**左右对称**，中间空着（桶本身在 e_keg 里画）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a KEG LANDING on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 dust puffs 8 squares wide on the ground at both sides of the middle (the middle 6 squares clear); 2 the dust thrown out 18 squares wide and 4 tall; 3 24 squares wide and thinner; 4 faint dust.
Layout: one horizontal row of 4 equal 26:10 cells, image size 1664x160 (each cell 416x160, 16 px a square); centered across, the dust's base on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `gangplank_fx_e_keg.png`：E 地上的火药桶（还不能引爆），2 帧循环

放在地上的火药桶（刚落地，还没到能引爆的时候）：一个**正立的木桶**（约 10 格宽、12 格高），三道深色铁箍，桶身正面一个白色的**骷髅交叉骨**标记，顶上一截短短的麻绳引线（**没点着**）。两帧只是木头上的高光微微闪一下（参考 E_barrel_image）。**左右对称**。木桶是实心的，可以有一圈深色边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A) and a dark iron ramp (#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418).
Effect: A POWDER KEG standing on the ground, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an upright wooden barrel 10 squares wide and 12 tall, bulging in the middle, three dark iron hoops, a small white skull-and-crossbones mark on its front, a short unlit rope fuse on top; the frames differ only in a faint shimmer on the staves. Solid: a 1-square dark outline round the barrel is allowed.
Layout: one horizontal row of 2 equal 14:16 cells, image size 448x256 (each cell 224x256, 16 px a square); centered across, the barrel's lowest square on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `gangplank_fx_e_keg_lit.png`：E 能引爆的火药桶（引线点着），2 帧循环

同一个火药桶（和 e_keg 一模一样，逐格相同），但引线**已经点着**：顶上一团闪动的黄橙色火星，桶底周围一圈淡淡的橙光，表示现在一枪就能引爆（参考 e_fuze_glow、Gangplank_base_e_fuze_center_glow）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A) and a dark iron ramp (#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: THE SAME POWDER KEG, ripe, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the barrel of e_keg square for square (the same place in the cell), its rope fuse LIT: a bright yellow-orange spark 3 squares on top flickering between the frames, a faint orange glow 1 square round the barrel's base.
Layout: one horizontal row of 2 equal 14:18 cells, image size 448x288 (each cell 224x288, 16 px a square); centered across, the barrel's lowest square on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `gangplank_fx_e_boom.png`：E 火药桶爆炸（地上，不跟随），7 帧

火药桶炸开（半径约 30 格）：白光一闪，一团橙黄色的火球从地上冒起，木桶碎片和铁箍往四周飞，地上一圈火往外推，接着变成翻滚的黑灰色火药烟，最后地上一块焦黑淡去（参考 E_barrel_lightflash、E_barrel_spikes、E_crit_woodpieces、E_barrel_smoke）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A).
Effect: A POWDER KEG EXPLOSION on the ground, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 12 squares at the middle just above the ground; 2 an orange-yellow fireball 24 squares wide rising with a white core, wooden splinters flying out at mirrored places; 3 the fireball 40 squares wide and 30 tall, a ring of fire along the ground (an ellipse 56 wide and 18 tall), splinters and iron hoop pieces flying out and up; 4 rolling black-grey powder smoke 50 squares wide with fire inside; 5 the smoke thinner and higher, embers; 6 faint smoke, a dark scorch ellipse on the ground; 7 the scorch fading.
Layout: one horizontal row of 7 equal 64:48 cells, image size 7168x768 (each cell 1024x768, 16 px a square); centered across, the ground (the blast's base) 5 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `gangplank_fx_e_hit.png`：E 被火药桶炸中（目标身上），4 帧

被桶炸中的敌人身上：橙色的爆炸火光加几片木屑（参考 E_crit_woodpieces、hit_flash）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A).
Effect: a KEG BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 an orange burst 10 squares with a white core; 3 the burst 14 squares breaking up, four wooden splinters flying out at mirrored places; 4 grey smoke puffs.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `gangplank_fx_e_slow.png`：E 减速（敌人脚下，2 秒，循环），4 帧

被桶炸到减速的敌人脚下：地上一圈灰色的火药烟，几粒橙色余烬。**左右对称**，只画在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a SLOW at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a grey powder smoke ring on the ground (an ellipse 14 squares wide and 4 tall), 4 orange embers on it at mirrored places; 1 dim, 2 bright, 3 brightest, 4 bright.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); centered across, the ellipse's middle 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `gangplank_fx_w_cast.png`：W 坏血病疗法：咬一口橘子（画进他吃东西的帧），3 帧

他咬的橘子：第 1 帧一个完整的圆橘子（约 6 格，橙色，顶上一片小绿叶）；第 2 帧咬掉一口，几滴黄橙色的果汁飞出来；第 3 帧剩下半个，几点果汁亮光（参考 w_spit、Gangplank_W_Heal_Light）。（这张画进他自己的动作帧，会跟着他一起翻，所以可以有方向）。橘子是实心的，可以有一圈深色边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a citrus orange ramp (#FFFFFF, #FFF2B0, #FFD04A, #FF9E1E, #E06A10, #8A3A08) with a small leaf in #7CC24A and #3E7A28.
Effect: an ORANGE being bitten, 3 frames (drawn into his own action frames, which the game mirrors with him, so it may point one way): 1 a whole round orange 6 squares with a highlight and a tiny green leaf on top; 2 the orange with a bite taken out of its right side, three bright juice drops flying right; 3 half an orange left, small juice sparkles. Solid: a 1-square dark outline round the fruit is allowed.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `gangplank_fx_w_imm.png`：W 吃完后的免控光（他脚下和身边，1 秒，循环），4 帧

吃完橘子后的 1 秒免控：脚下一圈金橙色的光环（扁椭圆宽 30 格、高 8 格），两边往上飘几粒柑橘色的亮点（参考 Gangplank_base_W_heal_glow、common_Aura_Self）。**左右对称**，中间身体的位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a citrus orange ramp (#FFFFFF, #FFF2B0, #FFD04A, #FF9E1E, #E06A10, #8A3A08) with a small leaf in #7CC24A and #3E7A28.
Effect: A CLEANSE GLOW round a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a golden-orange ring on the ground (an ellipse 30 squares wide and 8 tall, 1-2 squares thick, brightest at the front), small citrus sparkles rising at both sides (mirrored); the ring's light runs round and the sparkles rise and fade in turn.
Layout: one horizontal row of 4 equal 36:14 cells, image size 2304x224 (each cell 576x224, 16 px a square); centered across, the ellipse's middle 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `gangplank_fx_r_cast.png`：R 加农炮幕：朝天打出的信号弹（画进他举炮的帧），4 帧

他朝天开出的信号弹：炮口（格子底边中间）先一团白黄色的闪光，一颗红橙色的信号弹拖着亮尾巴直直往上冲，到顶上炸开成一颗小星，下面留一条渐淡的烟（参考 R_cas_glowspark、R_cast_sparks）。（这张画进他自己的动作帧，会跟着他一起翻，所以可以有方向）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a burnt orange-red ramp (#FFFFFF, #FFD0B0, #FF8A4A, #E2481E, #A0241A, #56100C) and a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: A SIGNAL FLARE shot straight up from a cannon's muzzle at the middle of the cell's bottom edge, 4 frames (drawn into his own action frames, which the game mirrors with him, so it may point one way): 1 a white-yellow muzzle burst 6 squares; 2 a bright red-orange flare with a white head streaking up 24 squares, a bright trail; 3 the flare at the top (38 squares up) bursting into a red-orange star 8 squares, a grey smoke trail below it; 4 the star's sparks falling, the smoke trail fading.
Layout: one horizontal row of 4 equal 12:44 cells, image size 768x704 (each cell 192x704, 16 px a square); the muzzle at the middle of the cell's bottom edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `gangplank_fx_r_warn.png`：R 落点预警（地上，不跟随，1 秒），8 帧

信号弹飞向落点的 1 秒里，地上的范围圈（从斜上方看的扁椭圆：宽 88 格、高 30 格）：一圈焦橙红色的虚线外圈，中间一个淡一点的内圈（宽 34 格），几个小小的准星标记，8 帧里越来越亮，最后一帧最亮（马上开炮）（参考 R_land_Outerring、R_center_AoE_ring、R_ground_decal）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a burnt orange-red ramp (#FFFFFF, #FFD0B0, #FF8A4A, #E2481E, #A0241A, #56100C).
Effect: THE BARRAGE AREA marked on the ground seen from above at an angle, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a burnt orange-red dashed outer ring (an ellipse 88 squares wide and 30 tall, 1-2 squares thick), a fainter inner ring (an ellipse 34 wide and 12 tall), four small crosshair marks inside at mirrored places; over the 8 frames the rings grow brighter, frame 8 the brightest with white edges.
Layout: one horizontal row of 8 equal 92:34 cells, image size 11776x544 (each cell 1472x544, 16 px a square); centered across, the ellipse's middle 15 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `gangplank_fx_r_wave.png`：R 一波炮弹落下（地上，不跟随，0.5 秒），6 帧

从海上船里打过来的一波炮弹砸进范围里（范围是地上的扁椭圆宽 88 格、高 30 格）：**三颗铁炮弹**（每颗约 5 格，黑铁色带白色高光，一颗在中间，两颗在左右对称的位置）从天上拖着火尾巴砸下来，落地炸开三团橙色的火光，泥土碎块往上飞，冒黑灰烟，地上留下裂纹淡去（参考 R_cannonball_large、R_cannonball_trail、R_hit_dirtbits、R_hit_groundcrack、R_hit_aoering）。**左右对称**，画面是正立的（不会被转）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark iron ramp (#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: ONE WAVE of a cannon barrage falling into an area, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright picture, never turned): the area is an ellipse 88 squares wide and 30 tall on the ground whose middle is 16 squares above the cell's bottom; three dark iron cannonballs 5 squares each (a white highlight) fall at mirrored places - one in the middle, two 26 squares to either side - with fiery orange trails: 1 the balls high, their bottoms 60 squares above the ground, trails 10 squares; 2 the balls 25 squares above the ground; 3 hitting the ground: three orange-white explosions 14 squares, dirt chunks flying up; 4 the explosions 20 squares with dark smoke, ground cracks; 5 grey smoke puffs rising; 6 faint smoke and cracks fading.
Layout: one horizontal row of 6 equal 96:84 cells, image size 9216x1344 (each cell 1536x1344, 16 px a square); centered across, the ellipse's middle 16 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `gangplank_fx_r_hit.png`：R 被炮弹打中（敌人身上），4 帧

被炮弹炸到的敌人身上：橙红色的火光加泥土碎块。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a CANNONBALL HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 an orange-red burst 11 squares with a white core; 3 the burst 14 squares, dirt chunks and embers at mirrored places; 4 smoke wisps.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `gangplank_fx_r_slow.png`：R 减速（敌人脚下，0.5 秒，循环），4 帧

被炮弹减速的敌人脚下：地上一圈泥土和灰烬。**左右对称**，只画在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a powder smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a SLOW at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a ring of dirt and ash on the ground (an ellipse 14 squares wide and 4 tall) with small dirt bits at mirrored places; 1 dim, 2 bright, 3 brightest, 4 bright.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); centered across, the ellipse's middle 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `gangplank_fx_a_hit` | view_effects `league_gangplank_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `gangplank_fx_p_hit` | view_effects `league_gangplank_p_hit`（跟随，画在人物上面；左右对称） | 16 |
| `gangplank_fx_p_ms` | view_buffs `league_gangplank_p_ms`（跟随，画在人物下面 z -1；左右对称；循环） | 22 × 8 |
| `gangplank_fx_q_flash` | 画进他的动作帧（skill 第 3 帧的炮口）；可以有方向 | 16 × 12 |
| `gangplank_fx_q_bullet` | view_projectiles `league_gangplank_q_bullet`（随飞行方向转动；上下对称；循环） | 10 × 6 |
| `gangplank_fx_q_hit` | view_effects `league_gangplank_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `gangplank_fx_e_throw` | view_projectiles `league_gangplank_e_throw`（随飞行方向转动；上下对称；循环） | 12 × 10 |
| `gangplank_fx_e_land` | view_effects `league_gangplank_e_land`（不跟随，画在人物下面 z -1；左右对称） | 26 × 10 |
| `gangplank_fx_e_keg` | view_effects `league_gangplank_e_keg`（不跟随，画在人物上面 z 1；左右对称；每 0.17 秒重贴） | 14 × 16 |
| `gangplank_fx_e_keg_lit` | view_effects `league_gangplank_e_keg_lit`（不跟随，画在人物上面 z 1；左右对称） | 14 × 18 |
| `gangplank_fx_e_boom` | view_effects `league_gangplank_e_boom`（不跟随，画在人物上面 z 2；左右对称；大图表） | 64 × 48 |
| `gangplank_fx_e_hit` | view_effects `league_gangplank_e_hit`（跟随，画在人物上面；左右对称） | 14 |
| `gangplank_fx_e_slow` | view_buffs `league_gangplank_e_slow`（跟随，画在人物下面 z -1；左右对称；循环） | 16 × 6 |
| `gangplank_fx_w_cast` | 画进他的动作帧（skill_w 第 2–3 帧，嘴边的手上）；可以有方向 | 10 × 10 |
| `gangplank_fx_w_imm` | view_buffs `league_gangplank_w_imm`（跟随，画在人物下面 z -1；左右对称；循环） | 36 × 14 |
| `gangplank_fx_r_cast` | 画进他的动作帧（ult 第 3–4 帧，朝天的炮口上方）；可以有方向 | 12 × 44 |
| `gangplank_fx_r_warn` | view_effects `league_gangplank_r_warn`（不跟随，画在人物下面 z -2；左右对称；大图表） | 92 × 34 |
| `gangplank_fx_r_wave` | view_effects `league_gangplank_r_wave`（不跟随，画在人物上面 z 2；左右对称；大图表；每 0.5 秒一波，共 12 波） | 96 × 84 |
| `gangplank_fx_r_hit` | view_effects `league_gangplank_r_hit`（跟随，画在人物上面；左右对称） | 14 |
| `gangplank_fx_r_slow` | view_buffs `league_gangplank_r_slow`（跟随，画在人物下面 z -1；左右对称；循环） | 16 × 6 |

- 两张表：`asset/league/effects/league_gangplank_fx`（小的）和 `league_gangplank_big`（e_boom、r_warn、r_wave），tag = 名字（build_gangplank.py 的 views）。
- 画进动作帧的三张（q_flash、w_cast、r_cast）：按 rig_gangplank 的帧把它们放到炮口 / 嘴边的手 / 朝天的炮口（skill 第 3 帧、skill_w 第 2–3 帧、ult 第 3–4 帧），用 Rig.bake 的 over 层画进 PPU 帧，kit 里不再播 CasterViewEffect。
- 投射物 `q_bullet`、`e_throw` 是 view_projectiles（随飞行方向转动，断言上下对称）；其余（画进动作的三张除外）断言左右对称。`e_keg`、`e_keg_lit` 每 10 tick 在落点重贴一次（2 帧 × 83 ms），`r_wave` 每 30 tick 一波（6 帧铺满 500 ms），`r_warn` 8 帧铺满信号弹飞行的 60 tick。
- 用 `pixel_1x/` 切格（import_ziggs_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。
