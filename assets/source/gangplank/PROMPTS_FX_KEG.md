# 普朗克：给 Codex 的特效提示词（第 3 步）

> **这一份是 3 张特效图。** 造型和动作已定（`design/gangplank_idle.png`：3/4 正面朝右的海盗船长，黑色月牙海盗帽、花白长胡子，青绿领子、赤膊，红腰带，背后深紫长外套，近侧手把金色手炮扛在肩上，远侧手拿一把刀尖烧红的锯齿弯刀）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连弯刀 42 格高、39 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/gangplank_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/gangplank_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里普朗克自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**被动和刀是烧红的橙色火**，**手枪的火光和金币是金色**，**火药桶是棕色木桶加黑铁箍、爆炸是橙黄色的火加黑灰色火药烟**，**W 是橘子的柑橘橙**，**大招的范围是焦橙红色，炮弹是黑铁色**。
> - **特效要亮**：每团光、每次爆炸都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **飞行中的东西（q_bullet 子弹、e_throw 火药桶）上下对称**：游戏会把飞行的图按飞的方向转，往左飞时整张图上下翻过来。
> - **q_flash 枪口火光、w_cast 橘子、r_cast 信号弹三张会画进他自己的动作帧**（会跟着他一起翻面），所以可以有方向，按每条写的朝向画。
> - **其余全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他朝左时也是同一张图。
> - **围着人的画面中间身体位置留空**，不要盖住人。
> **这是重画包**：只重画下面几张，其余已经导入不用动。第一版的问题（按游戏像素量的）：
> - `e_throw`：第一版 12×10 格（桶约 8×6）太小，用户：「桶最大点吧 也太小了」。样子照第一版，画大到 16×13 格（桶约 12×9）
> - `e_keg`：第一版 14×16 格（桶约 10×12）太小，用户：「桶最大点吧 也太小了」。样子照第一版（骷髅交叉骨、三道铁箍、麻绳引线），画大到 20×22 格（桶约 15×18，骷髅约 5 格宽，要清楚）
> - `e_keg_lit`：和 e_keg 一起画大到 20×25 格：桶身和新的 e_keg 逐格相同，引线上的火星约 4 格
>
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `gangplank_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的名字 `name`、帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/gangplank_keg/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/gangplank_keg_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

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

## 特效（3 张）

3 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：火药桶爆炸半径 30000，大招范围半径 44000）。

### 1. `gangplank_fx_e_throw.png`：E 火药桶（飞行中），3 帧循环

扔到敌人脚下的火药桶：一个木桶横躺着顺着飞行方向（约 12 格长、9 格高，两道深色铁箍竖着），**上下对称**，所以桶上不画图案；三帧里木纹高光轮换，像在翻滚。木桶是实心的，可以有一圈深色边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A) and a dark iron ramp (#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418).
Effect: a POWDER KEG in flight, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over): a wooden barrel lying along the flight, 12 squares long and 9 tall, two dark iron hoops across it, bulging in the middle; the stave highlights shift each frame as if it tumbles. Solid: a 1-square dark outline round the barrel is allowed.
Layout: one horizontal row of 3 equal 16:13 cells, image size 768x208 (each cell 256x208, 16 px a square); it flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `gangplank_fx_e_keg.png`：E 地上的火药桶（还不能引爆），2 帧循环

放在地上的火药桶（刚落地，还没到能引爆的时候）：一个**正立的木桶**（约 15 格宽、18 格高），三道深色铁箍，桶身正面一个白色的**骷髅交叉骨**（约 5 格宽）标记，顶上一截短短的麻绳引线（**没点着**）。两帧只是木头上的高光微微闪一下（参考 E_barrel_image）。**左右对称**。木桶是实心的，可以有一圈深色边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A) and a dark iron ramp (#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418).
Effect: A POWDER KEG standing on the ground, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an upright wooden barrel 15 squares wide and 18 tall, bulging in the middle, three dark iron hoops, a white skull-and-crossbones mark 5 squares wide on its front, a short unlit rope fuse on top; the frames differ only in a faint shimmer on the staves. Solid: a 1-square dark outline round the barrel is allowed.
Layout: one horizontal row of 2 equal 20:22 cells, image size 640x352 (each cell 320x352, 16 px a square); centered across, the barrel's lowest square on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `gangplank_fx_e_keg_lit.png`：E 能引爆的火药桶（引线点着），2 帧循环

同一个火药桶（和 e_keg 一模一样，逐格相同），但引线**已经点着**：顶上一团闪动的黄橙色火星，桶底周围一圈淡淡的橙光，表示现在一枪就能引爆（参考 e_fuze_glow、Gangplank_base_e_fuze_center_glow）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#F2D2A2, #C89058, #94602E, #64401E, #3E2612, #1E120A) and a dark iron ramp (#E8E8EC, #A8AAB2, #6E727C, #464A52, #2A2C32, #141418) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: THE SAME POWDER KEG, ripe, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the barrel of e_keg square for square (the same place in the cell), its rope fuse LIT: a bright yellow-orange spark 4 squares on top flickering between the frames, a faint orange glow 1 square round the barrel's base.
Layout: one horizontal row of 2 equal 20:25 cells, image size 640x400 (each cell 320x400, 16 px a square); centered across, the barrel's lowest square on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `gangplank_fx_e_throw` | view_projectiles `league_gangplank_e_throw`（随飞行方向转动；上下对称；循环） | 16 × 13 |
| `gangplank_fx_e_keg` | view_effects `league_gangplank_e_keg`（不跟随，画在人物上面 z 1；左右对称；每 0.17 秒重贴） | 20 × 22 |
| `gangplank_fx_e_keg_lit` | view_effects `league_gangplank_e_keg_lit`（不跟随，画在人物上面 z 1；左右对称） | 20 × 25 |

- 两张表：`asset/league/effects/league_gangplank_fx`（小的）和 `league_gangplank_big`（e_boom、r_warn、r_wave），tag = 名字（build_gangplank.py 的 views）。
- 画进动作帧的三张（q_flash、w_cast、r_cast）：按 rig_gangplank 的帧把它们放到炮口 / 嘴边的手 / 朝天的炮口（skill 第 3 帧、skill_w 第 2–3 帧、ult 第 3–4 帧），用 Rig.bake 的 over 层画进 PPU 帧，kit 里不再播 CasterViewEffect。
- 投射物 `q_bullet`、`e_throw` 是 view_projectiles（随飞行方向转动，断言上下对称）；其余（画进动作的三张除外）断言左右对称。`e_keg`、`e_keg_lit` 每 10 tick 在落点重贴一次（2 帧 × 83 ms），`r_wave` 每 30 tick 一波（6 帧铺满 500 ms），`r_warn` 8 帧铺满信号弹飞行的 60 tick。
- 用 `pixel_1x/` 切格（import_ziggs_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。
