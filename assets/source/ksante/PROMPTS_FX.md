# 纳祖芒荣耀 奎桑提：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型已定（`design/ksante_designs.png`：左边普通姿态——3/4 正面朝右的大块头，深红外套、金色护肩和金绳徽章、蓝紫围巾、黑络腮胡，两把嵌青色水晶的青石陀斧竖在身边；右边全盛姿态——弓背半蹲、两根长棍甩开）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），普通姿态 48 格高、44 格宽，全盛 37 格高、54 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/ksante_size.png`：两种姿态放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奎桑提自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**陀斧的能量是青色（像水花一样的青白色光），配沙土色的尘烟和青灰色的石屑**；**被动和大招是金色**（肯特布纹样的菱形）；**全盛姿态多了紫蓝色的刀光**。
> - **特效要亮**：每道光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **光、尘烟、光环、冲击波都没有黑描边**；**实物**（石屑、碎石块）有 1 格近黑描边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（`ao_on` 的第 1、2 帧除外）。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`q3_wave`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进他自己帧里的**（`a_swipe`、`q_crack`、`q3_burst`、`w_trail`、`ao_swipe`）**朝右画，不用对称**（跟着他的身体一起翻转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ksante_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/ksante_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/ksante_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「血性本能」 | 陀斧横扫；技能打中过的敌人，下一次普攻额外伤害 | `a_swipe` · `a_hit` · `p_mark` · `p_hit` |
| 技能 1 = Q「无双陀斧」 | 一、二段往前裂地减速；第三段两把陀斧砸地，冲击波把敌人拉回来 | `q_crack` · `q_hit` · `q_slow` · `q3_burst` · `q3_wave` · `q3_hit` |
| 技能 2 = W「辟路先锋」 | 顶着陀斧蓄力减伤（带护盾），然后冲撞击退、晕眩 | `w_brace` · `w_trail` · `w_land` · `w_hit` |
| 大招「傲岸雄姿」 | 盾击撞飞敌人，追上去砸地，进入全盛姿态 15 秒 | `r_hit` · `r_slam` · `ao_on` · `ao_aura` · `ao_swipe` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、尘烟、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**（实物——石屑、碎石块——有 1 格近黑描边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 青色能量：`#FFFFFF`、`#DFFFFC`、`#8EF2EA`、`#3CCFCB`、`#1A8E9A`、`#0C4E5A`；
  - 沙土尘烟：`#FFF4DA`、`#F0D49A`、`#D2A462`、`#A0723E`、`#6A4628`；
  - 青灰石屑（实物）：`#D6E2E0`、`#9CB4B4`、`#6A8488`、`#42585E`、`#26343A`；
  - 金色（被动、大招）：`#FFFFFF`、`#FFF4C8`、`#FFD660`、`#F2A428`、`#B8640E`；
  - 紫蓝刀光（全盛）：`#F2E6FF`、`#BFA2FF`、`#8A62F0`、`#5A38C0`、`#2E1C70`；
- 打中、爆发居中画，不旋转；地面上的圈（冲击环、坑、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 三段冲击波宽 9000，W 撞击半径 16000）。

### 1. `ksante_fx_a_hit.png`：普攻：打中目标，3 帧

陀斧砸中：一团青白色的闪光，几块青灰色的小石屑溅开（参考 ksante_base_hit_region）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a grey-teal stone ramp (#D6E2E0, #9CB4B4, #6A8488, #42585E, #26343A).
Effect: A HEAVY HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white four-pointed flash 6 squares across; 2 the flash 9 across with 4 small stone chips flying out at mirrored places; 3 only the chips further out and a few teal specks. SOLID OBJECTS (stone chips, rock shards) have a 1-square near-black outline; light, dust, rings and waves have none.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `ksante_fx_p_hit.png`：被动 血性本能：被标记后的那一下普攻，4 帧

技能标记过的敌人被下一次普攻打中：一个金色的菱形纹样（肯特布的菱形套菱形）一下亮起又碎成菱形小光点（参考 ksante_base_kentepattern、p_diamond、ba_passive_swipe_bg）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E), a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A).
Effect: A GOLD DIAMOND BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 6 squares across; 2 a gold diamond outline 12 squares tall with a smaller diamond inside it (a kente-cloth motif), white core; 3 the diamonds breaking into 8 tiny gold diamond sparks flying out at mirrored places; 4 fading sparks with a few teal specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `ksante_fx_p_mark.png`：被动：下一次普攻已经强化（他身上，循环），4 帧

他的技能打中敌人后、下一次普攻会更痛的那几秒：他脚下一圈金色的小菱形，一闪一闪地转（参考 ksante_base_p_diamond）。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E).
Effect: A RING OF GOLD DIAMONDS, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring on the ground round his feet (an ellipse 32 squares wide and 6 tall) made of 10 tiny gold diamonds, each winking bright in turn so the light runs round; the middle EMPTY.
Layout: one horizontal row of 4 equal 36:8 cells, image size 2304x128 (each cell 576x128, 16 px a square); the ellipse's middle on the cell's middle; he stands in the middle, not drawn: a big man 26 squares wide and 43 tall (with his ntofos at his sides 44 wide, 48 tall) (only his feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `ksante_fx_a_swipe.png`：普攻：陀斧挥过的弧光（画进他的帧），4 帧

陀斧往前横扫的那一下：一道青白色的宽弧形风光，从他身后上方扫到身前下方，带几粒沙尘（参考 ksante_base_ba_swipe_bg、p_swipe_light）。**朝右**（画进他的帧里，不用对称），4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628).
Effect: A SWING ARC, 4 frames, pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry): 1 the start of a thick crescent of teal-white wind at the upper left; 2 the crescent swept round in front of him (from the upper left over to the lower right, 30 squares long, 6 thick at its middle, white along its leading edge); 3 the crescent at the lower right thinning, sand specks thrown off its tail; 4 fading teal and sand specks.
Layout: one horizontal row of 4 equal 40:32 cells, image size 2560x512 (each cell 640x512, 16 px a square); he stands in the middle, not drawn: a big man 26 squares wide and 43 tall (with his ntofos at his sides 44 wide, 48 tall) - his feet on the cell's bottom row, 14 squares from its left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `ksante_fx_q_crack.png`：Q 无双陀斧一、二段：往前的一道裂地（画进他的帧），5 帧

陀斧砸地，地面往前裂开一道短短的直线：裂缝一路往右延伸，裂缝上冒起沙尘和青色的水花一样的能量（参考 ksante_base_q_ground_crack_fill、q_linearsplashes_02、q_rect_flash、q_melee_dust）。**朝右**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628), a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a grey-teal stone ramp (#D6E2E0, #9CB4B4, #6A8488, #42585E, #26343A).
Effect: A LINE OF CRACKED GROUND, 5 frames, pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry): 1 a flash where the ntofo hits at the left; 2 a crack in the ground running 20 squares to the right, sand puffing up along it; 3 the crack 38 squares long, teal splashes of energy leaping up along it like water (4 to 7 squares tall), stone chips; 4 the splashes falling, dust drifting; 5 the crack and a little dust fading. SOLID OBJECTS (stone chips, rock shards) have a 1-square near-black outline; light, dust, rings and waves have none.
Layout: one horizontal row of 5 equal 44:16 cells, image size 3520x256 (each cell 704x256, 16 px a square); the crack lies on the cell's 3rd row from the bottom; he stands at the cell's left edge (not drawn), the ntofo striking 4 squares from the left. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `ksante_fx_q_hit.png`：Q 一、二段打中的敌人，3 帧

被裂地打中：一团沙尘往上冒，几滴青色能量溅开（参考 ksante_base_q_hit、q_sand_smoke）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628), a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A).
Effect: A SAND BURST HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white flash 6 squares across low in the cell; 2 a puff of sand dust 10 squares wide rising, 4 teal drops flying out at mirrored places; 3 the dust thinning, the drops falling.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `ksante_fx_q_slow.png`：Q 减速（敌人脚下，循环），4 帧

被减速的敌人脚下：一小圈沙尘在打转。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628).
Effect: A SWIRL OF SAND, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring of sand dust round the target's feet (an ellipse 18 squares wide and 4 tall), puffs of dust moving round it in turn; the middle EMPTY.
Layout: one horizontal row of 4 equal 20:6 cells, image size 1280x96 (each cell 320x96, 16 px a square); the ellipse's middle on the cell's middle; the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (only its feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `ksante_fx_q3_burst.png`：Q 三段：两把陀斧砸地的爆发（画进他的帧），5 帧

两把陀斧一起砸在身前：地面炸开，沙土和石块往上往前喷，一道青色的冲击波开始往右推（之后由 q3_wave 接着飞）（参考 ksante_base_q_walldestruction、q_spike2、q_blastshapes）。**朝右**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628), a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a grey-teal stone ramp (#D6E2E0, #9CB4B4, #6A8488, #42585E, #26343A).
Effect: A GROUND ERUPTION, 5 frames, pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry): 1 a white-teal flash on the ground in front of him; 2 the ground bursting up in front: a fan of sand and stone shards thrown up and forward (16 squares tall), a teal glow at its base; 3 a wall of teal energy rising and starting to roll to the right, rocks flying; 4 the wall leaving the cell at the right, dust settling; 5 dust and a few shards. SOLID OBJECTS (stone chips, rock shards) have a 1-square near-black outline; light, dust, rings and waves have none.
Layout: one horizontal row of 5 equal 36:22 cells, image size 2880x352 (each cell 576x352, 16 px a square); the burst's base on the cell's bottom row, starting 6 squares from its left edge; he stands at the cell's left edge (not drawn). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `ksante_fx_q3_wave.png`：Q 三段：往前推的冲击波（弹道，循环），4 帧

往前推、把敌人拉回来的冲击波：一道横着的青色能量浪，里面卷着沙尘，前沿最亮，后面拖着沙尘尾迹（参考 ksante_base_q3_crack_trail、q_waves、q_air_swoosh）。**朝右飞、后面在左，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628).
Effect: A ROLLING SHOCKWAVE, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a horizontal surge of teal energy 24 squares long and 12 tall at its front (a bright white-teal crescent leading edge at the right, curving back above and below the middle line), sand dust churning inside it, a tapering sand trail 14 squares long behind it; each frame the crest and the dust churn.
Layout: one horizontal row of 4 equal 40:16 cells, image size 2560x256 (each cell 640x256, 16 px a square); the wave's middle on the cell's middle row, its leading edge 2 squares from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `ksante_fx_q3_hit.png`：Q 三段打中的敌人（被拉回来），4 帧

被冲击波卷中：青色的能量浪拍在身上，沙尘四溅。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628).
Effect: A WAVE CRASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white flash 8 squares across; 2 a ring of teal energy splashing out 16 squares wide with sand in it; 3 the splash breaking into teal drops and dust at mirrored places; 4 fading drops and dust.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `ksante_fx_w_brace.png`：W 辟路先锋：蓄力减伤（他身上），6 帧

顶着陀斧蓄力的 0.75 秒：他身边一层青色的护盾光一点点合拢，护盾外圈闪着小光点（参考 ksante_base_w_shieldbegin、e_shield_outer）。**只画护盾的外圈，中间他的身体位置留空**，**左右对称**，6 帧（越来越亮）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A).
Effect: A BRACING SHIELD, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a shell of teal light round an upright big body (only its broken outline and a few bright streaks: 48 squares wide, 50 tall, its bottom open at the ground), small sparkles running along it; frame by frame it closes and brightens, frame 6 brightest with a white rim. The middle EMPTY where his body is.
Layout: one horizontal row of 6 equal 52:54 cells, image size 4992x864 (each cell 832x864, 16 px a square); he stands in the middle, not drawn: a big man 26 squares wide and 43 tall (with his ntofos at his sides 44 wide, 48 tall) (his feet on the cell's bottom row, 2 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `ksante_fx_w_trail.png`：W 冲撞时脚下扬起的沙尘（画进他的帧），4 帧

他顶着陀斧往前冲时，脚后跟扬起一路沙尘往后飘（参考 ksante_base_w_wave_texture、q_sand_smoke）。**朝右**（尘往左后方飘），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628).
Effect: A DUST TRAIL, 4 frames, a seamless loop, pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry): clouds of sand dust kicked up at the right (where his feet are) and streaming back to the left along the ground, rising up to 12 squares, thinning towards the left; each frame the clouds roll back.
Layout: one horizontal row of 4 equal 32:18 cells, image size 2048x288 (each cell 512x288, 16 px a square); his feet at the cell's bottom right corner (not drawn). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `ksante_fx_w_land.png`：W 撞上的那一下（地上），5 帧

撞到敌人那一下：地上炸开一圈沙尘冲击环（从斜上方看的椭圆，约 52 格宽、14 格高），石块往外飞，几道青色的光往上冲（参考 ksante_base_w_ring_02、w_wave_rock_mult、w_front_cone_v02）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628), a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a grey-teal stone ramp (#D6E2E0, #9CB4B4, #6A8488, #42585E, #26343A).
Effect: A GROUND IMPACT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-teal flash in the middle of the ground; 2 a flat ring of sand dust spreading on the ground (an ellipse 36 squares wide and 10 tall) with 4 short teal light streaks shooting up; 3 the ring 52 wide, stone chips flying out at mirrored places; 4 the dust ring thinning, chips falling; 5 last dust and specks. SOLID OBJECTS (stone chips, rock shards) have a 1-square near-black outline; light, dust, rings and waves have none.
Layout: one horizontal row of 5 equal 56:24 cells, image size 4480x384 (each cell 896x384, 16 px a square); the ground ellipse's middle 8 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `ksante_fx_w_hit.png`：W 撞中的敌人（击退、晕眩），4 帧

被撞中：青白色的撞击星形一闪、石屑飞散，头上转起一圈小星星（晕眩）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A), a grey-teal stone ramp (#D6E2E0, #9CB4B4, #6A8488, #42585E, #26343A), a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E).
Effect: A RAM HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white impact star 12 squares across in the lower middle with 4 stone chips; 2 the star fading, the chips further out, a ring of 4 tiny gold stars appearing at the top; 3 the star ring turning; 4 the stars fading. SOLID OBJECTS (stone chips, rock shards) have a 1-square near-black outline; light, dust, rings and waves have none.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `ksante_fx_r_hit.png`：R 傲岸雄姿：盾击打中的敌人，4 帧

被大招撞飞的那一下：一团金橙色的爆光，几道光线往四周射出（参考 ksante_base_r_ray_shockwave、r_slam_arrow）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E), a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628).
Effect: A GOLD BLAST HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 10 squares across; 2 a gold burst 18 squares across with 8 short light rays shooting out at mirrored places; 3 the rays longer and thinner, sand specks; 4 fading rays and specks.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `ksante_fx_r_slam.png`：R 追上去砸地（敌人脚下），6 帧

他追上去把敌人砸在地上：地上砸出一个碎裂的坑（从斜上方看的椭圆），金色的光柱从坑里冲起，石块和沙尘飞起来（参考 ksante_base_r_crater、r_rockcrater_mult、r_flame_ring、r_groundsmoke02）。**左右对称**，6 帧：落下一闪、坑裂开、光柱最高、石块飞散、尘土、消失。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E), a sand-dust ramp (#FFF4DA, #F0D49A, #D2A462, #A0723E, #6A4628), a grey-teal stone ramp (#D6E2E0, #9CB4B4, #6A8488, #42585E, #26343A).
Effect: A CRATER SLAM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash on the ground in the middle; 2 a cracked crater on the ground (an ellipse 40 squares wide and 12 tall, its cracks radiating, glowing gold); 3 a column of gold light 30 squares tall rising from the crater, a flat gold shock ring spreading (an ellipse 60 wide and 16 tall, only its rim lit); 4 rocks and sand thrown up and out at mirrored places, the column fading; 5 dust settling round the crater; 6 the crater's last glow and dust. SOLID OBJECTS (stone chips, rock shards) have a 1-square near-black outline; light, dust, rings and waves have none.
Layout: one horizontal row of 6 equal 64:44 cells, image size 6144x704 (each cell 1024x704, 16 px a square); the crater's middle 8 squares above the cell's bottom, centered; the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `ksante_fx_ao_on.png`：R 进入全盛姿态的那一下（他身上），6 帧

他甩开陀斧、进入全盛姿态：胸口一下爆出金白色的光，金色的菱形纹样和紫蓝色的刀光往外旋转散开，最后在他身边留下一圈光（参考 ksante_base_r_weapon_glow、r_rainbow_glow、ao_w_blade_sub_texture、kentepattern）。**左右对称**，6 帧。第 1、2 帧的光可以盖住他，之后中间留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E), a violet-blue light ramp (#F2E6FF, #BFA2FF, #8A62F0, #5A38C0, #2E1C70), a teal-cyan energy ramp (#FFFFFF, #DFFFFC, #8EF2EA, #3CCFCB, #1A8E9A, #0C4E5A).
Effect: AN ALL OUT BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 16 squares across at the chest height of a hunched big body; 2 a big gold burst 34 squares across with 8 gold kente diamonds flying out; 3 the diamonds spinning outward with violet-blue blades of light between them (curved streaks, mirrored), the middle opening up; 4 a ring of gold and violet light round the body (only its rim: 50 squares wide, 50 tall); 5 the ring breaking into gold and violet sparks; 6 last sparks. From frame 3 the middle is EMPTY where his body is.
Layout: one horizontal row of 6 equal 60:58 cells, image size 5760x928 (each cell 960x928, 16 px a square); he stands in the middle, not drawn: hunched, 36 squares wide and 37 tall, his clubs reaching out to 54 wide (his feet on the cell's bottom row, 2 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `ksante_fx_ao_aura.png`：全盛姿态（他身上，循环），4 帧

全盛的 15 秒：他脚下一圈紫蓝色和金色的光焰，边上一闪一闪地往上窜（参考 ksante_base_r_underglow、ao_w_wind）。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue light ramp (#F2E6FF, #BFA2FF, #8A62F0, #5A38C0, #2E1C70), a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E).
Effect: AN ALL OUT AURA, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring of violet-blue light on the ground round his feet (an ellipse 52 squares wide and 8 tall, only its rim lit), small violet and gold flame tongues licking up from the rim (up to 6 squares) in turn, a few gold motes rising; the middle EMPTY.
Layout: one horizontal row of 4 equal 58:14 cells, image size 3712x224 (each cell 928x224, 16 px a square); the ellipse's middle 4 squares above the cell's bottom, centered; he stands in the middle, not drawn: hunched, 36 squares wide and 37 tall, his clubs reaching out to 54 wide (only his feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `ksante_fx_ao_swipe.png`：全盛普攻：两根长棍横扫的弧光（画进他的帧），4 帧

全盛的普攻：两根长棍往两边抡开，两道紫蓝色带金边的宽弧光从他身前往左右两边扫出去（参考 ksante_base_ao_w_wind、ao_w_blade_sub_texture）。画进他的帧里（不用对称），4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue light ramp (#F2E6FF, #BFA2FF, #8A62F0, #5A38C0, #2E1C70), a gold light ramp (#FFFFFF, #FFF4C8, #FFD660, #F2A428, #B8640E).
Effect: A DOUBLE SWEEP, 4 frames, pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry): 1 two thick violet-blue crescents starting in front of his chest; 2 the crescents sweeping out to both sides (the right one a little bigger and in front, 30 squares long each, gold leading edges); 3 the crescents at their widest, thinning, gold sparks thrown off; 4 fading violet and gold specks.
Layout: one horizontal row of 4 equal 70:30 cells, image size 4480x480 (each cell 1120x480, 16 px a square); he stands in the middle, not drawn: hunched, 36 squares wide and 37 tall, his clubs reaching out to 54 wide - his feet on the cell's bottom row, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `ksante_fx_a_hit` | view_effects `league_ksante_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `ksante_fx_p_hit` | view_effects `league_ksante_p_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `ksante_fx_p_mark` | view_buffs `league_ksante_mark`（跟着他，循环，z -1；左右对称） | 36 × 8 |
| `ksante_fx_a_swipe` | 画进他自己的 attack 帧（bake_caster_fx；朝右） | 40 × 32 |
| `ksante_fx_q_crack` | 画进他自己的 skill / skill_b 帧（bake_caster_fx；朝右） | 44 × 16 |
| `ksante_fx_q_hit` | view_effects `league_ksante_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `ksante_fx_q_slow` | view_buffs `league_ksante_q_slow`（跟着目标，循环，z -1；左右对称） | 20 × 6 |
| `ksante_fx_q3_burst` | 画进他自己的 skill_c 帧（bake_caster_fx；朝右） | 36 × 22 |
| `ksante_fx_q3_wave` | view_projectiles `league_ksante_q3_wave`（随飞行方向转；上下对称） | 40 × 16 |
| `ksante_fx_q3_hit` | view_effects `league_ksante_q3_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `ksante_fx_w_brace` | view_effects `league_ksante_w_brace`（他身上，z 3；左右对称） | 52 × 54 |
| `ksante_fx_w_trail` | 画进他自己的 skill2_dash 帧（bake_caster_fx；朝右） | 32 × 18 |
| `ksante_fx_w_land` | view_effects `league_ksante_w_land`（他身上撞到的地方，不跟随，z -1；左右对称） | 56 × 24 |
| `ksante_fx_w_hit` | view_effects `league_ksante_w_hit`（跟随目标，z 2；左右对称） | 18 × 20 |
| `ksante_fx_r_hit` | view_effects `league_ksante_r_hit`（跟随目标，z 2；左右对称） | 22 × 22 |
| `ksante_fx_r_slam` | view_effects `league_ksante_r_slam`（跟随目标，z -1；左右对称） | 64 × 44 |
| `ksante_fx_ao_on` | view_effects `league_ksante_ao_on`（他身上，z 3；左右对称） | 60 × 58 |
| `ksante_fx_ao_aura` | view_buffs `league_ksante_ao`（跟着他，循环，z -1；左右对称） | 58 × 14 |
| `ksante_fx_ao_swipe` | 画进他自己的 ao_attack 帧（bake_caster_fx；朝右） | 70 × 30 |

- 两张表：`asset/league/effects/league_ksante_fx`（小的）和 `league_ksante_big`（q3_wave、w_brace、w_land、r_slam、ao_on、ao_aura），tag = 名字（build_ksante.py 的 views：p_mark 的 tag 是 `p_mark`，buff 名是 `league_ksante_mark`；ao_aura 的 buff 名是 `league_ksante_ao`）。
- 弹道（q3_wave）断言上下对称；朝前的（a_swipe、q_crack、q3_burst、w_trail、ao_swipe）用 tools/fix/bake_caster_fx.py 画进他的帧（attack / skill / skill_b / skill_c / skill2_dash / ao_attack），不进表；其余断言左右对称；w_brace、ao_on、p_mark、ao_aura 跟随他。
- 用 `pixel_1x/` 切格（import_neeko_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
