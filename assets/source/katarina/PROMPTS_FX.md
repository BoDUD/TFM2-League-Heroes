# 卡特琳娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图 + 3 张画进她动作帧的图。** 造型和动作已定（`design/katarina_designs.png`：正面、侧身；动作都是侧身朝右）。**全部用生图（image_gen）画，不要用代码拼方块。**
> - 她在游戏里是**高清**的：每个游戏像素里 1.5×1.5 个细格子；1 倍时待机 34×39 格（连匕首）。
> - **两种画法**：
> 1. 第一部分 18 张普通特效（飞刀、刀光、打中、瞬步的烟、地上的匕首、旋斩、死亡莲华的刀圈、身上的 buff）**照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。大小对照 `design/katarina_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；`design/katarina_shots.png` 是定稿动作（4 倍），青色十字是飞刀飞出、刀尖的位置。
> 2. 第二部分是**画进她自己动作帧**的图（她的帧会随朝向镜像，特效图不会，所以刺击的刀光、甩刀的光弧、瞬步挥刀这些有方向的东西必须画进帧里）。这些按**她的高清细格子**画：`bake/katarina_bake_<名字>_<帧>.png` 是那一帧的定位图（横图 256×170 格或竖图 170×256 格，每格 6 像素；她本人画成淡灰色、只用来对位置；灰框是这一帧的范围，红线是地面，每 10 格一道浅线；青色十字是起点：刀尖或甩出去的手）。**在同样大小、同样格子的图上只画特效，背景透明，不要画她本人**；Claude 按格子取回，直接叠进她的帧。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡特琳娜自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**刀光是深红，芯是白亮的**；**匕首是银白的钢**；**瞬步是暗红的烟**；**地上的匕首脚下一圈金色火线**。
> - **特效要亮**：每道刀光、每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画两边，中间身体位置留空**；旋斩和死亡莲华的刀圈是扁椭圆、中间留空，不要涂满。
> - **方向（重要，红色方不会镜像）**：旋转的飞刀画成**转半圈看起来一样（点对称）**；死亡莲华飞出的匕首画成**朝右飞、上下对称**（游戏会把它们转向飞行方向）；打中、目标身上、地上的画面、瞬步、旋斩、刀圈和身上的 buff 都要**严格左右对称**（逐格对称）。第二部分画进帧里的图照定位图的方向画（往右），不用对称。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `katarina_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），以及 `katarina_bake_<名字>_<帧>.png`（第二部分，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（256×170 或 170×256）。透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`（**原样，不要自己整理**），打包成 `outputs/katarina_fx_pack_done.zip`。**每张图单独交付，不要只给一张总览图**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「贪婪」 | 匕首刺击；被她伤过的英雄阵亡时 Q、W 刷新、瞬步就绪；地上的匕首她走过去就捡起、原地旋斩 | `a_slash`（帧里）· `a_hit` · `p_reset` · `d_fall` · `d_stuck` · `spin` · `p_hit` |
| 技能 1 = Q「弹射之刃」（+ E 瞬步跳到匕首） | 甩出旋转的匕首打中目标、再弹两个敌人；匕首从第一个目标身上弹到天上、落在他站的地方 | `q_throw`（帧里）· `q_blade` · `q_hit` · `q_arc` · `d_fall` · `e_out` · `e_in` |
| 技能 2 = W「伺机待发」（+ E 瞬步切入） | 先瞬步到敌方英雄身边砍一刀，再把匕首抛到天上、1.25 秒后落回原地，加速 | `e_out` · `e_in` · `e_slash`（帧里）· `e_hit` · `w_toss` · `d_fall` · `w_ms` |
| 大招「死亡莲华」 | 原地旋转 2.5 秒，不停向周围的敌方英雄掷出匕首，附带重伤 | `r_lotus` · `r_dagger` · `r_hit` · `r_gw` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、光、火星、烟都没有黑描边，也不要用最深的颜色给形状描一圈边**（匕首本身是实物，刀柄可以有深色）。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 深红刀光：`#FFFFFF`、`#FFE3E6`、`#FF7A84`、`#E8283C`、`#A8122A`、`#5C0A18`；
  - 匕首的钢：`#FFFFFF`、`#EEF2F8`、`#C2CCDA`、`#8A97AA`、`#56627A`；
  - 瞬步的暗红烟：`#FFD6DC`、`#E8455A`、`#A8203A`、`#6C1428`、`#3A0C18`；
  - 地上匕首的金色火线：`#FFFFFF`、`#FFF4C8`、`#FFD86A`、`#F5A93A`、`#C8741E`；
- 打中居中画，不旋转；地上的圈是从斜上方看的扁椭圆（宽是高的 2.5 倍左右）。
- 画在别人身上的画面**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 第一部分：特效（18 张，游戏格子）

18 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：捡刀旋斩半径 30000）。大图（r_lotus、spin）按每格 8 像素画，其余每格 16 像素。

### 1. `katarina_fx_q_blade.png`：Q 弹射之刃：旋转飞行的匕首（循环），4 帧

Q 扔出的匕首在空中高速旋转：两把交叉的银白弯刃组成的小风车，刃尖带一圈深红的刀光残影（参考 Q_Blade_Trail、Q_Blade_Loopies）。**转半圈看起来一样（点对称）**，4 帧依次转 45°，无缝循环。约 11 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A) and a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a SPINNING THROWN DAGGER, 4 frames, a seamless loop, POINT-SYMMETRIC in every frame: it looks exactly the same turned half round about its centre, square for square (the game turns it to its flight; flying left it is upside down): two curved silver blades crossed at the centre (a small pinwheel 11 squares across), a thin crimson blur arc trailing each blade's tip; each frame turned 45 degrees further than the last.
Layout: one horizontal row of 4 equal square cells, image size 832x208 (each cell 208x208, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `katarina_fx_r_dagger.png`：R 死亡莲华：飞向敌人的匕首（循环），2 帧

死亡莲华每 1/6 秒掷向敌人的匕首：一把朝右飞的细长银白匕首，后面一条深红的刀光尾巴（参考 R_Mis_Trail、R_BlurryBlade）。**上下对称**。2 帧（尾巴一闪）。约 10 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A) and a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a FLYING DAGGER to the RIGHT, 2 frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a slim silver blade 5 squares long with a white edge pointing right, a dark hilt 1 square, a crimson trail 5 squares long tapering behind it; the trail flickers.
Layout: one horizontal row of 2 equal 12:6 cells, image size 384x96 (each cell 192x96, 16 px a square); the blade's point 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `katarina_fx_a_hit.png`：普攻刺中（目标身上），4 帧

匕首刺中：一个白亮的小十字闪光，两道交叉的深红刀痕（X 形）（参考 z_hit_flash、CritTrail）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a DAGGER HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white star flash 4 squares across; 2 two crossed crimson slash marks (an X) 11 squares across with white cores; 3 the X at its brightest with 4 tiny sparks; 4 the X fading to wine red.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `katarina_fx_q_hit.png`：Q 飞刀打中（每个目标身上），4 帧

旋转的匕首打中：一圈横着的深红刀光划过，中间一个白闪（参考 Q_Blade_Glows、z_hit_flash）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18) and a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A).
Effect: a SPINNING-BLADE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a flat crimson slash ring 12 squares wide and 4 tall round the flash; 3 the ring with silver glints at its two ends; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `katarina_fx_q_arc.png`：Q 匕首从第一个目标身上弹起、飞向空中（目标处，不跟随），5 帧

飞刀打中第一个目标后匕首往天上弹起：一把旋转的银白匕首从下往上飞出画面，拖一道竖直的深红刀光（参考 Q_Blade_Trail）。**左右对称**（匕首画成竖直、刀光在正中）。约 8 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A) and a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a DAGGER FLYING STRAIGHT UP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an upright silver dagger 6 squares long spinning end over end (drawn point-up or point-down, centered) rising from the bottom of the cell to the top over the 5 frames, a thin crimson trail 2 squares wide below it growing longer then fading; in frame 5 only the trail's top is left.
Layout: one horizontal row of 5 equal 10:32 cells, image size 800x512 (each cell 160x512, 16 px a square); centered across; frame 1's dagger on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `katarina_fx_p_hit.png`：捡起匕首旋斩打中的敌人（每个目标身上），3 帧

旋斩扫到的敌人：一道横着的深红刀痕，中间白闪（参考 Dagger_Pickup_Slash）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a SWEEPING SLASH HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat crimson slash line 12 squares wide and 2 tall with a white core; 2 the line with a white flash 4 squares in its middle; 3 fading.
Layout: one horizontal row of 3 equal 14:10 cells, image size 672x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `katarina_fx_e_hit.png`：E 瞬步落地打中的敌人（目标身上），4 帧

瞬步落地顺手一刀：一道竖着的深红刀光劈下，带几缕暗红烟（参考 E_LeadingEdge、z_hit_flash）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18) and a crimson smoke ramp (#FFD6DC, #E8455A, #A8203A, #6C1428, #3A0C18).
Effect: a SHUNPO STRIKE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a crimson V-shaped double slash 14 squares across with white cores; 3 the slash fading, 4 small crimson smoke puffs at mirrored places; 4 smoke fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `katarina_fx_r_hit.png`：R 每把匕首打中（目标身上），3 帧

死亡莲华每把匕首打中：一个小小的白闪 + 深红刀痕（参考 R_Tar_Impact）。**左右对称**。约 8 格（一秒打好几下，要小）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a SMALL DAGGER HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 a small crimson X slash 8 squares across; 3 fading.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `katarina_fx_e_out.png`：E 瞬步消失（她原来站的地方，不跟随），5 帧

瞬步离开的一瞬：她站的地方炸开一团深红的烟，几道往外散的刀光残影，烟往上飘散（参考 base_z_smoke、E_trail、E_LeadingEdge）。**左右对称**，中间人形位置**留空**（8 格宽）。约 20 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson smoke ramp (#FFD6DC, #E8455A, #A8203A, #6C1428, #3A0C18) and a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a SHUNPO VANISH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a clear upright gap 8 squares wide in the middle (where she stood): 1 a ring of crimson smoke puffs at her feet 20 squares across; 2 the smoke rising up both sides to 26 squares with 4 crimson streaks flying out; 3 the smoke at full height 30 squares; 4 thinning; 5 the last wisps at the top.
Layout: one horizontal row of 5 equal 22:32 cells, image size 1760x512 (each cell 352x512, 16 px a square); centered across, the smoke's foot on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `katarina_fx_e_in.png`：E 瞬步出现（她落地的地方，不跟随），4 帧

瞬步落地：从上往下一道深红的刀光闪下，脚下炸开一圈暗红烟和刀光（参考 E_Mis_Ring、E_LeadingEdge、base_z_smoke）。**左右对称**，中间人形位置**留空**（8 格宽）。约 22 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson smoke ramp (#FFD6DC, #E8455A, #A8203A, #6C1428, #3A0C18) and a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a SHUNPO ARRIVAL, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a clear upright gap 8 squares wide in the middle: 1 two crimson streaks diving down both sides to her feet; 2 a flat burst of crimson smoke and slash light at her feet 22 squares across; 3 the burst spreading, 6 tiny sparks; 4 wisps fading.
Layout: one horizontal row of 4 equal 24:26 cells, image size 1536x416 (each cell 384x416, 16 px a square); centered across, the burst on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `katarina_fx_w_toss.png`：W 伺机待发：抛向空中的匕首（她身边，不跟随），6 帧

W 把匕首往正上方抛：一把银白匕首旋转着往天上飞出画面，带一道细细的深红光（参考 Q_Blade_Trail、R_BlurryBlade）。**左右对称**（匕首竖直、在正中）。约 8 格宽、40 格高（底部在她举起的手的高度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A) and a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a DAGGER TOSSED STRAIGHT UP, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an upright silver dagger 6 squares long spinning end over end, rising from the bottom of the cell to the top over the 6 frames, a thin crimson glint trail 1-2 squares wide under it; in frame 6 only a glint at the very top.
Layout: one horizontal row of 6 equal 10:42 cells, image size 960x672 (each cell 160x672, 16 px a square); centered across; frame 1's dagger on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `katarina_fx_d_fall.png`：匕首落地（地上，不跟随），4 帧

Q / W 的匕首从天上落下、插进地面：一把竖直的银白匕首从上往下扎进地里，落点一圈尘土和金色火线（参考 Dagger_FireLine、Q_Blade_Ground_Crack）。**左右对称**。约 14 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A), a gold fire ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E) and a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a DAGGER FALLING INTO THE GROUND, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an upright silver dagger point-down near the top of the cell; 2 the dagger halfway down, a thin gold streak above it; 3 the dagger stuck point-down in the ground (its point on the bottom row), a flat ring of gold sparks and dust 14 squares wide round its foot; 4 the dagger stuck, the ring fading.
Layout: one horizontal row of 4 equal 16:24 cells, image size 1024x384 (each cell 256x384, 16 px a square); centered across, the ground on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `katarina_fx_d_stuck.png`：插在地上的匕首（地上，不跟随，每 2/3 秒重放一次，等她来捡），4 帧

插在地上的匕首：一把竖直的银白匕首刀尖朝下插在地上，刀柄朝上，脚下一小圈金色火线一闪一闪（参考 Dagger_FireLine、R_Ring_Pickup）。**左右对称**。约 10 格宽、14 格高。4 帧连起来正好 2/3 秒（每帧约 10 tick）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A) and a gold fire ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a DAGGER STUCK IN THE GROUND, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an upright silver dagger 11 squares tall point-down in the ground (the point on the bottom row, the dark hilt up), the same in every frame; a flat ring of gold fire 10 squares wide and 3 tall at its foot glowing brighter and dimmer frame by frame.
Layout: one horizontal row of 4 equal 12:16 cells, image size 768x256 (each cell 192x256, 16 px a square); centered across, the ground on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `katarina_fx_p_reset.png`：被动贪婪刷新（她身上，跟随），5 帧

击杀刷新冷却：她身上一圈深红光往上一冲，几把小小的光刃绕着她转一下（参考 R_Reset_Ground、R_Success_Ray）。**左右对称**，中间人形位置**留空**（10 格宽）。约 26 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a RESET SURGE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a clear upright gap 10 squares wide in the middle: 1 a flat crimson ring at her feet 20 squares across; 2 crimson rays rising up both sides 20 squares; 3 the rays at 34 squares with 4 small white blade glints at mirrored places; 4 the rays fading upward; 5 a few sparks at the top.
Layout: one horizontal row of 5 equal 28:36 cells, image size 2240x576 (each cell 448x576, 16 px a square); centered across, the ring on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `katarina_fx_spin.png`：捡起匕首旋斩（她身边一圈，不跟随，大），5 帧

捡起匕首原地旋身一斩：围着她一圈扁扁的深红刀光（从斜上方看的椭圆），刀光前沿白亮，后面拖着淡下去（参考 Dagger_Pickup_Slash、R_BlurryBlades）。**左右对称**，中间人形位置**留空**（12 格宽）。约 60 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18) and a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A).
Effect: a SPIN SLASH round her, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a clear upright gap 12 squares wide in the middle: a flat ellipse of crimson blade light 60 squares wide and 22 tall seen from above at a slant (the ring's front half lower, the back half higher), drawn as two mirrored arcs sweeping from the back round both sides to the front; 1 short arcs at the back; 2 the arcs halfway round with white leading edges; 3 the full ring, 6 silver glints; 4 the ring fading; 5 wisps.
Layout: one horizontal row of 5 equal 64:30 cells, image size 2560x240 (each cell 512x240, 8 px a square); centered, the ring's bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `katarina_fx_r_lotus.png`：R 死亡莲华：围着她旋转的刀圈（跟随，引导时每半秒重放），6 帧

死亡莲华：她身边一圈快速旋转的刀光——扁椭圆上几把模糊的银白刀刃和深红残影一圈圈转，脚下一圈暗红光（参考 R_BlurryBlades_v2–v5、R_Ring_Indicator、R_Color）。**左右对称**，中间人形位置**留空**（12 格宽）。约 50 格宽、30 格高。6 帧正好半秒、首尾无缝。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18) and a dagger-steel ramp (#FFFFFF, #EEF2F8, #C2CCDA, #8A97AA, #56627A).
Effect: a WHIRL OF BLADES round her, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a clear upright gap 12 squares wide in the middle: a flat ellipse 50 squares wide and 20 tall seen from above (back half higher, front half lower) of 6 blurred silver blades with crimson trails sweeping round it, placed in mirrored pairs and moving round a step each frame; a faint crimson ring at her feet 40 squares wide.
Layout: one horizontal row of 6 equal 54:34 cells, image size 2592x272 (each cell 432x272, 8 px a square); centered, the feet ring 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `katarina_fx_w_ms.png`：W 的加速（她脚下，跟随，循环），4 帧

伺机待发的加速：她脚下两边几缕往后飘的深红风痕（参考 Global_SpeedBuff_Swirl，换成深红）。**左右对称**，中间留空 8 格。约 20 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a SPEED SWIRL at the feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a clear gap 8 squares wide in the middle: 2-3 short curved crimson wisps at each side near the ground, drifting outward and up a little each frame.
Layout: one horizontal row of 4 equal 22:10 cells, image size 1408x160 (each cell 352x160, 16 px a square); centered across, the wisps on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `katarina_fx_r_gw.png`：R 的重伤（敌人头上，跟随，循环），4 帧

重伤（治疗减少）：敌人头上一个小小的深红破碎心形 / 裂开的十字标记一闪一闪（参考英雄联盟的重伤图标）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a GRIEVOUS WOUNDS mark, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small crimson cracked heart 8 squares across with a dark crack down its middle and a white glint, pulsing brighter and dimmer.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 第二部分：画进她动作帧的图（3 张，她的高清格子）

每张都在对应的定位图 `bake/katarina_bake_<名字>_<帧>.png` 上画：同样大小（横图 1536×1020、竖图 1020×1536 像素）、每格 6 像素，格子和定位图完全对齐；**只画特效，不画她**，背景透明。她本人在定位图里是淡灰色，只用来对位置。青色十字是起点（刀尖或甩出去的手）。画在她**上面**的会盖住她（所以都别盖住她的脸）。尽量画在灰框里，往前的刀光可以伸出灰框。注意这里 1 格只有游戏里的 0.67 个像素，所以线条至少 3 格粗，太细的进游戏就看不见了。

### 19. 普攻：匕首刺击的刀光（画进普攻第 3 帧）

匕首往前刺到最远（青色十字是刀尖）：刀尖后面一道往前刺的细长深红刀光（直的，从她手边到刀尖再往前 6 格），刀尖一个白闪。画在她**上面**，别挡住脸。

**`katarina_bake_a_slash_3.png`**（定位图 `bake/katarina_bake_a_slash_3.png`，256×170 格，青色十字在第 179 列、第 61 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a THRUST TRAIL along the dagger: a straight crimson streak of light 3-4 squares thick from her hand to the cyan cross (the dagger's point) and 6 squares beyond it, a white core, a small white star flash at the cyan cross; nothing over her face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (179, 61), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. Q：甩出飞刀的一瞬（画进 Q 第 3 帧）

空手往前甩出（青色十字是她伸出去的手）：手前方一道往前弯的深红刀光弧，手边一个白闪（匕首已经飞走，不画匕首）。画在她**上面**，别挡住脸。

**`katarina_bake_q_throw_3.png`**（定位图 `bake/katarina_bake_q_throw_3.png`，256×170 格，青色十字在第 160 列、第 62 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18).
Effect: a THROW ARC in front of the flung hand: a curved crimson arc of light 3 squares thick sweeping from above her shoulder down to the cyan cross (her empty hand) and 8 squares past it, a white flash 6 squares across at the cyan cross; no dagger; nothing over her face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (160, 62), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. E 瞬步落地挥刀（画进瞬步第 2 帧）

落地顺势往前挥（青色十字是前手的刀尖）：刀尖划出一道往右上弯的深红刀光弧，脚边几缕暗红烟。画在她**上面**，别挡住脸。

**`katarina_bake_e_slash_2.png`**（定位图 `bake/katarina_bake_e_slash_2.png`，256×170 格，青色十字在第 174 列、第 61 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, sparks or smoke, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson blade-light ramp (#FFFFFF, #FFE3E6, #FF7A84, #E8283C, #A8122A, #5C0A18) and a crimson smoke ramp (#FFD6DC, #E8455A, #A8203A, #6C1428, #3A0C18).
Effect: a SLASH ARC: a curved crimson arc of blade light 3-4 squares thick swept from low behind her up to the cyan cross (the front dagger's point), a white leading edge at the cyan cross, 4 small crimson smoke puffs low at her feet; nothing over her face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (174, 61), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `katarina_fx_q_blade` | view_projectiles `league_katarina_q_blade`（朝飞行方向转；转半圈看起来一样） | 11 × 11 |
| `katarina_fx_r_dagger` | view_projectiles `league_katarina_r_dagger`（朝飞行方向转，画成朝右飞；上下对称） | 10 × 4 |
| `katarina_fx_a_hit` | view_effects `league_katarina_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `katarina_fx_q_hit` | view_effects `league_katarina_q_hit`（跟随，画在人物上面；左右对称） | 12 |
| `katarina_fx_q_arc` | view_effects `league_katarina_q_arc`（不跟随，画在人物上面；左右对称） | 8 × 30 |
| `katarina_fx_p_hit` | view_effects `league_katarina_p_hit`（跟随，画在人物上面；左右对称） | 12 |
| `katarina_fx_e_hit` | view_effects `league_katarina_e_hit`（跟随，画在人物上面；左右对称） | 14 |
| `katarina_fx_r_hit` | view_effects `league_katarina_r_hit`（跟随，画在人物上面；左右对称） | 8 |
| `katarina_fx_e_out` | view_effects `league_katarina_e_out`（不跟随，画在人物上面；左右对称） | 20 × 30 |
| `katarina_fx_e_in` | view_effects `league_katarina_e_in`（不跟随，画在人物上面；左右对称） | 22 × 24 |
| `katarina_fx_w_toss` | view_effects `league_katarina_w_toss`（不跟随，画在人物上面；左右对称） | 8 × 40 |
| `katarina_fx_d_fall` | view_effects `league_katarina_d_fall`（不跟随，地上；左右对称） | 14 × 22 |
| `katarina_fx_d_stuck` | view_effects `league_katarina_d_stuck`（不跟随，地上；左右对称） | 10 × 14 |
| `katarina_fx_p_reset` | view_effects `league_katarina_p_reset`（跟随，画在人物上面；左右对称） | 26 × 34 |
| `katarina_fx_spin` | view_effects `league_katarina_spin`（大表；不跟随，画在人物上面；左右对称） | 60 × 26 |
| `katarina_fx_r_lotus` | view_effects `league_katarina_r_lotus`（大表；跟随，画在人物上面；左右对称） | 50 × 30 |
| `katarina_fx_w_ms` | view_buffs `league_katarina_w_ms`（她脚下；左右对称） | 20 × 8 |
| `katarina_fx_r_gw` | view_buffs `league_katarina_r_gw`（敌人头上；左右对称） | 10 |
| `katarina_bake_a_slash_<帧>` | 画进 `hd_attack` 第 3 帧（人物上面） | 高清格子 |
| `katarina_bake_q_throw_<帧>` | 画进 `hd_skill` 第 3 帧（人物上面） | 高清格子 |
| `katarina_bake_e_slash_<帧>` | 画进 `hd_blink` 第 2 帧（人物上面） | 高清格子 |

- 两张表：`asset/league/effects/league_katarina_fx`（小的）和 `league_katarina_big`（r_lotus、spin），tag = 名字（build_katarina.py 的 views）。
- 目标身上的画面、地上的 d_fall / d_stuck、她身上的 e_out / e_in / p_reset / spin / r_lotus 底边放在脚底线（站位点下方 11.5 格）；q_arc / w_toss 底边放在她手（或目标身体中部）的高度；d_stuck 4 帧摊满 40 tick（主包每 40 tick 重放一次）；r_lotus 6 帧摊满 30 tick；飞刀的 y_offset 按 `design/katarina_shots.png` 的出手高度重设（build_katarina q_y / r_y）。
- 画进帧的图在 restyle 之后（rig_katarina.py --pinholes 那一步）按 `fx_bake_cells.json` 从画布上切下这一帧的范围，叠到 `assets/source/ppu/katarina_<tag>.png` 的高清帧上，伸出帧外的地方两边一样加宽；1 倍表按格子投票一起更新（rig_jayce.bake 的做法）。
- 用 `pixel_1x/` 切格（import_jayce_fx 的做法；Codex 自己读回太小太糊时从 raw 重读），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
