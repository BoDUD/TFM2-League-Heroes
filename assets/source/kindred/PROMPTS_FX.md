# 永猎双子 千珏：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图 + 12 张画进她动作帧的图。** 造型和动作已定（`design/kindred_designs.png`：3/4 正面待机（羊灵 + 身后的狼灵）、羊灵侧面、狼灵侧面；动作都是侧面朝右，狼灵浮在她身后）。
> - 她在游戏里是**高清**的：每个游戏像素里 2.86×2.86 个细格子；1 倍时 37×37 格（连弓和狼灵）。
> - **两种画法**：
> 1. 第一部分 14 张普通特效（箭、打中、印记、狼咬、地上的领域和法阵、治疗）**照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。大小对照 `design/kindred_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；`design/kindred_shots.png` 是定稿动作（4 倍），青色十字是她身上、脚下特效的位置。
> 2. 第二部分是**画进她自己动作帧**的图（她的帧会随朝向镜像，特效图不会，所以弦上的箭、松弦的光、跳跃的拖影这些有方向的东西必须画进帧里）。这些按**她的高清细格子**画：`bake/kindred_bake_<名字>_<帧>.png` 是那一帧的定位图（横图 256×170 格或竖图 170×256 格，每格 6 像素；她本人画成淡灰色、只用来对位置；灰框是这一帧的范围，红线是地面，每 10 格一道浅线；青色、黄色十字是起点）。**在同样大小、同样格子的图上只画特效，背景透明，不要画她本人**；Claude 按格子取回，直接叠进她的帧。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里千珏自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**羊灵的箭和光是灵光：白芯、淡青到天蓝**；**狼灵的 E、W 和咬是深紫靛色的烟，淡紫的芯**；**印记是青色和紫色相间的漩涡**；**大招是白亮、淡青和薄荷色的神圣光**。
> - **特效要亮**：每道光、每缕烟都要有白色或最亮一档的芯，暗底上一眼能看见（狼烟的芯用淡紫）。
> - **围着人的光只画两边，中间身体位置留空**；地上的领域和法阵里面基本是空的，不要涂满。
> - **方向（重要，红色方不会镜像）**：飞行的箭画成**朝右飞、上下对称**（游戏会把它转向飞行方向）；打中、目标身上、地上的画面和她身上的 buff 都要**严格左右对称**（逐格对称），只有印记和法阵中间的**漩涡**不用对称（它没有前后，游戏两边画法一样）。第二部分画进帧里的图照定位图的方向画（箭朝右，拖影朝左下），不用对称。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kindred_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），以及 `kindred_bake_<名字>_<帧>.png`（第二部分，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（256×170 或 170×256）。透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `kindred_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**；**每张图单独交付，不要只给一张总览图**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「千珏之印」 | 羊灵拉弓射灵箭；击杀、助攻得到印记（射程、攻速、E 伤害随印记变大） | `a_nock`（帧里）· `a_loose`（帧里）· `a_arrow` · `a_hit` · `p_stack` |
| 技能 1 = Q「乱箭之舞」 | 灵巧地一跳，落地向最多 3 个目标各射一箭，之后攻速变快 | `q_trail`（帧里）· `q_dash` · `q_nock`（帧里）· `q_loose`（帧里）· `q_arrow` · `q_hit` |
| 技能 2 = E「横生惧意」+ W「狼灵狂热」 | E：一箭减速并打上狼的印记，再射中三下后狼灵扑上去咬；E 冷却时开 W：狼灵的领域，每秒咬领域里的敌人 | `e_nock`（帧里）· `e_loose`（帧里）· `e_arrow` · `e_hit` · `e_mark` · `e_bite` · `w_call`（帧里）· `w_zone` · `w_bite` |
| 大招「羊灵生息」 | 羊灵举弓，脚下展开法阵 4 秒，法阵里谁都不会死，结束时给里面的英雄回血 | `r_raise`（帧里）· `r_zone` · `r_heal` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火花、光丝都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 羊灵灵光（箭、普攻、Q、松弦）：`#FFFFFF`、`#E1FBFD`、`#89F7DD`、`#54EDD7`、`#39B4F7`、`#2E78F2`；
  - 狼灵狼烟（E、W、狼咬）：`#E6DEFF`、`#A6AAF8`、`#8E82F7`、`#5C44DE`、`#3E1C76`、`#250E43`；
  - 印记漩涡（E 印记、被动）：`#FFFFFF`、`#6AE3EA`、`#39B4F7`、`#2E78F2`、`#8E82F7`、`#5C44DE`；
  - 羊灵生息（大招法阵、治疗）：`#FFFFFF`、`#E1FBFD`、`#C0E6FC`、`#89F7DD`、`#A6AAF8`；
- 打中、爆发居中画，不旋转；地上的圈是从斜上方看的扁椭圆（宽是高的 2.5 倍左右）。
- 画在别人身上的画面**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 第一部分：特效（14 张，游戏格子）

14 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻射程 55000，W 领域半径 60000，大招法阵半径 50000）。两张大领域按每格 8 像素画，其余每格 16 像素。

### 1. `kindred_fx_a_arrow.png`：普攻灵箭（飞行中，循环），4 帧

羊灵射出的灵箭：一根细细的白色光箭，箭头是青白色的叶片形（参考 BA_Arrow_Tip），后面拖一小段淡青色的光迹（参考 BA_Trail_Wisp、BA_glow_mis）。朝右飞。**上下对称**。4 帧无缝循环（光迹闪一闪）。约 14 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a SPIRIT ARROW flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a thin white light shaft 8 squares long and 1 square thick, a pale cyan glow 1 square above and below it, a leaf-shaped white-cyan arrowhead 3 squares long pointing RIGHT, a wispy pale cyan trail 4 squares long behind; the trail flickers each frame.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kindred_fx_q_arrow.png`：Q 乱箭之舞的箭（飞行中，循环），4 帧

乱箭之舞一次射向最多 3 个目标的箭：比普攻的箭更亮更长，拖一条带亮点的青色光尾（参考 BA_Trail_Wisp、BA_Spark_cas）。朝右飞。**上下对称**。4 帧无缝循环。约 16 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a BRIGHT SPIRIT ARROW flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a white light shaft 9 squares long, a pale cyan glow round it 1 square thick, a leaf-shaped white arrowhead 3 squares long pointing RIGHT, a tapering cyan light trail 5 squares long with 2 white motes; the motes move back along the trail each frame.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kindred_fx_e_arrow.png`：E 横生惧意的箭（飞行中，循环），4 帧

横生惧意：羊灵射出带着狼灵恶意的箭——深紫色的箭身、淡紫色的芯、青白色箭头，箭身上缠着几缕深靛色的狼烟往后飘（参考 E_Muzzle_cas、W_wolf_smoke）。朝右飞。**上下对称**。4 帧无缝循环（烟一缕一缕往后飘）。约 18 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a DREAD ARROW flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a violet shaft 10 squares long with a pale lilac core, a white-cyan arrowhead 3 squares long pointing RIGHT, curls of dark indigo smoke 2 squares thick trailing 6 squares behind it, above and below alike; the curls drift back a square each frame.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kindred_fx_a_hit.png`：普攻打中（目标身上），4 帧

灵箭射中：一团青白色的光炸开，4 片羽毛状的淡蓝光丝往外散（参考 BA_Hit_Feather、BA_flash_tar、BA_Flash_sharp）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a SPIRIT ARROW HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a pale cyan burst 8 squares across with a white core and 4 feather-shaped wisps at mirrored places; 3 the wisps flying out to 12 squares across; 4 a few fading motes.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kindred_fx_q_hit.png`：Q 的箭打中（每个目标身上），4 帧

乱箭之舞射中：一个白亮的十字星光，周围一圈青色的小火花（参考 Q_hit_Sparks、BA_Flare）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a STAR-SPARK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 3 squares; 2 a four-pointed white-cyan star 10 squares across; 3 the star 14 squares across, 6 cyan sparks round it at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kindred_fx_e_hit.png`：E 横生惧意：打中、种下印记（目标身上），5 帧

横生惧意的箭射中：一圈深紫色的环猛地往里收（参考 E_Ring_Cas），中间一闪青白光，几缕狼烟往外甩（参考 E_hit_Flare、W_Dark_flash）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a DREAD MARK HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a dark violet ring 18 squares across; 2 the ring snapping inward to 10 squares, a white-cyan flash 4 squares at the center; 3 the flash at its brightest, 6 curls of indigo smoke thrown out at mirrored places; 4 the smoke drifting, a small violet ring 6 squares; 5 fading wisps.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kindred_fx_e_mark.png`：E 的狼之印记（目标头顶，跟着目标，每 1/3 秒重播一次），4 帧

被横生惧意标记的目标头顶浮着千珏的印记：一个青色和紫色相间的漩涡圆印（参考 P_Mark、P_full_mark、E_Stack_1/2/3），一闪一闪。**漩涡本身不用左右对称**（它没有前后，游戏两边画法一样），其他光点左右对称。4 帧要能接起来循环（每 1/3 秒重播一次）。画在格子中间，导入时 Claude 把它放到头顶。约 11 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a mark ramp (#FFFFFF, #6AE3EA, #39B4F7, #2E78F2, #8E82F7, #5C44DE).
Effect: a SWIRL MARK, 4 frames, a seamless loop: a round swirl sigil 11 squares across - three curling bands (pale cyan, sky blue, violet) spiralling into a white center, a dark indigo rim 1 square thick only where the bands meet the outside - pulsing brighter (frame 2) and dimmer (frame 4), 2 tiny white glints at mirrored places beside it.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kindred_fx_p_stack.png`：被动 千珏之印：得到一层印记（她头顶，1.5 秒，循环），4 帧

千珏收下一层印记（击杀、助攻）：她头顶亮起漩涡印记，下面一道细细的光往上收（参考 P_Mark_activate_ring、P_collect_godlay、P_spark）。**漩涡本身不用左右对称**，其他左右对称。4 帧无缝循环。画在格子中间，导入时 Claude 放到她头顶。约 10 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a mark ramp (#FFFFFF, #6AE3EA, #39B4F7, #2E78F2, #8E82F7, #5C44DE).
Effect: a MARK GAINED, 4 frames, a seamless loop: a round swirl sigil 9 squares across (pale cyan, sky blue and violet bands spiralling into a white center) over a thin vertical beam of pale light 1 square wide and 3 squares tall under it, 4 white motes at mirrored places rising round it and taking turns to brighten.
Layout: one horizontal row of 4 equal 12:14 cells, image size 768x224 (each cell 192x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kindred_fx_e_bite.png`：E 狼灵扑咬（被标记的目标身上，大），6 帧

横生惧意的第三下之后狼灵扑上去咬：狼灵的头从正面画——白色的面具脸、两只发青光的眼睛、深紫色烟一样的鬃毛（参考 E_wolf_head、`design/kindred_designs.png` 里狼的样子），从目标头顶扑下来、张嘴、一口咬合，四周炸开深靛色狼烟。**左右对称**（正面的狼头）。约 28 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a SPIRIT WOLF'S BITE seen from the FRONT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 the Wolf's head small at the top of the cell - a pale bone-white mask face with two glowing cyan eyes, a mane of dark indigo smoke; 2 the head lunging down and larger (20 squares wide), jaws opening, fangs white; 3 the jaws wide open over the middle of the cell, the mane flaring out 26 squares; 4 the jaws snapped shut at the middle, a burst of indigo smoke 28 squares across, a white-cyan flash between the fangs; 5 the head dissolving into smoke curls at mirrored places; 6 fading wisps and two eye glints.
Layout: one horizontal row of 6 equal 30:34 cells, image size 2880x544 (each cell 480x544, 16 px a square); centered across, the bite (frame 4's jaws) at the middle of the cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kindred_fx_w_bite.png`：W 狼灵狂热：狼灵在领域里咬中（目标身上），5 帧

狼灵在自己的领域里每秒咬一口：一对深紫色的狼牙从上下两边合拢（正面看，像一张嘴合上），中间一闪，几缕狼烟（参考 W_wolf_hit_circle、W_wolf_smoke、W_Dark_flash）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a SNAPPING BITE seen from the FRONT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of white fangs in dark indigo smoke, one at the top and one at the bottom of an open mouth 16 squares tall; 2 the jaws closing to 8 squares; 3 the fangs meeting at the middle, a white-cyan flash 6 squares, smoke 18 squares across; 4 smoke curls at mirrored places; 5 fading wisps.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kindred_fx_q_dash.png`：Q 起跳点的尘烟（地上，留在原地），5 帧

乱箭之舞跳开时地上留下的一圈淡淡的灵光尘烟：从斜上方看的扁椭圆，几片羽毛状的光往两边飘（参考 R_light_dust、BA_Hit_Feather）。**左右对称**、**上下对称**。约 24 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a SPIRIT DUST PUFF on the ground seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) and top to bottom: 1 a pale cyan ellipse 10 squares wide and 3 tall; 2 a ring of pale dust 20 squares wide and 7 tall, white specks; 3 the ring 24 squares wide, 4 feather-like wisps drifting out at mirrored places; 4 the ring thinning; 5 a few fading specks.
Layout: one horizontal row of 5 equal 26:10 cells, image size 2080x160 (each cell 416x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kindred_fx_w_zone.png`：W 狼灵狂热：狼灵的领域（地上，8.5 秒，大），10 帧

狼灵的狩猎场：地上一个从斜上方看的扁椭圆领域（半径 60 个游戏像素）——边上一圈深靛色、发着暗紫光的狼烟环（参考 W_area、W_Ring_mult），环里贴地飘着几缕狼烟（参考 W_ground_smoke、W_wolf_smoke），零星几点青色的光（狼灵的眼睛一闪）。要暗、要淡，不能挡住站在里面的人。**左右对称**、**上下对称**。第 1-2 帧出现（环从中间扩开），第 3-8 帧循环（烟在环上流动，但每帧都对称），第 9-10 帧消散。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43).
Effect: a WOLF'S HUNTING GROUND on the ground seen from above at an angle, 10 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) and top to bottom: a flat ellipse 120 squares wide and 46 tall whose rim is a ring of dark indigo smoke 3-4 squares thick glowing violet on its inner edge, faint wisps of smoke curling low inside it, 4 tiny cyan glints at mirrored places; the inside stays mostly empty and dark-transparent (no fill). 1-2 the ring spreading out from a small ellipse at the center to full size; 3-8 a seamless loop, the smoke on the rim flowing round (mirrored in every frame), the glints taking turns; 9-10 the ring breaking into smoke and fading.
Layout: one horizontal row of 10 equal 124:50 cells, image size 9920x400 (each cell 992x400, 8 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kindred_fx_r_zone.png`：R 羊灵生息：羊灵的庇护法阵（地上，4 秒，大），9 帧

羊灵生息：地上一个从斜上方看的发光法阵（半径 50 个游戏像素）——一圈白亮的光环，环上对称的几个符文刻痕（参考 R_symbol_Light_01/02/03），中间一个青白色的漩涡（漩涡不用对称），环的边缘升起一圈细细的光墙（一根根竖着的光条，参考 R_cylinder、R_light_wall），光点往上飘（参考 R_light_dust）。法阵里的人不会死，所以要亮、要神圣，但中间人站的地方别涂满。第 1-2 帧法阵画出来（光环从中间扩开、符文亮起），第 3-6 帧循环（光墙和光点往上飘），第 7 帧一闪白光，第 8-9 帧消散（结束时给法阵里的人治疗）。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a respite ramp (#FFFFFF, #E1FBFD, #C0E6FC, #89F7DD, #A6AAF8).
Effect: a HOLY CIRCLE on the ground seen from above at an angle, 9 frames, the ring, the runes, the light wall and the motes SYMMETRIC LEFT TO RIGHT square for square (only the swirl in the middle may turn): a flat ellipse 100 squares wide and 38 tall - a bright white-cyan ring 2 squares thick, 6 rune marks on it at mirrored places, a pale cyan swirl 18 squares across at the center, a low wall of thin upright light streaks (1 square wide, 4-10 squares tall) rising along the ring's front and back edges, white motes floating up; the inside mostly empty. 1-2 the ring drawn out from the center, the runes lighting one pair at a time; 3-6 a seamless loop, the streaks and motes rising; 7 a white flash over the whole ring; 8-9 the circle fading.
Layout: one horizontal row of 9 equal 104:44 cells, image size 7488x352 (each cell 832x352, 8 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `kindred_fx_r_heal.png`：R 羊灵生息结束时的治疗（每个队友身上），6 帧

法阵结束时法阵里的英雄回血：脚下一圈白光升起，两边几道淡青、薄荷色的光往上飘，羊毛一样软的小光团（参考 R_Heal_Flash、R_Heal_spark、W_heal_sparks、R_outside_light_up）。**左右对称**，中间人形位置留空（8 格宽、26 格高）。格子底部就是脚底。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a respite ramp (#FFFFFF, #E1FBFD, #C0E6FC, #89F7DD, #A6AAF8).
Effect: a HEALING RISE round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 8 squares wide and 26 tall): 1 a white ellipse glow on the ground 14 squares wide at the bottom; 2 pale cyan and mint light streaks rising at both sides to 16 squares; 3 the streaks at their top (30 squares), soft round light puffs and white motes at mirrored places; 4 the light thinning, motes still rising; 5 a few motes; 6 the last glints.
Layout: one horizontal row of 6 equal 20:34 cells, image size 1920x544 (each cell 320x544, 16 px a square); centered across, the ground glow on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 第二部分：画进她动作帧的图（12 张，她的高清格子）

每张都在对应的定位图 `bake/kindred_bake_<名字>_<帧>.png` 上画：同样大小（横图 1536×1020、竖图 1020×1536 像素）、每格 6 像素，格子和定位图完全对齐；**只画特效，不画她**，背景透明。她本人在定位图里是淡灰色，只用来对位置。青色十字一般是拉弦的手（弦的顶点）或起点，黄色十字是握弓的手（箭搭在弓上的地方）或弓尖。画在她**上面**的会盖住她（所以都别盖住她的脸），画在她**后面**的被她挡住的部分不用画。尽量画在灰框里，箭头和松弦的光可以伸出灰框。注意这里 1 格只有游戏里的 0.35 个像素（她的弓弦是 2 格白），所以线条至少 2 格粗，太细的进游戏就看不见了。

### 15. 普攻：搭在弦上的灵箭（画进普攻第 2、3 帧，她拉满弓的时候）

羊灵拉满弓时弦上搭着一支灵箭：从青色十字（拉弦的手、弦的顶点）穿过黄色十字（握弓的手、箭搭在弓上的地方），箭头伸出弓外几格。箭身是一根白色的光线，两边一圈淡青光，叶片形的青白色箭头，尾端两小片羽毛光。画在她**上面**。

**`kindred_bake_a_nock_2.png`**（定位图 `bake/kindred_bake_a_nock_2.png`，256×170 格，青色十字在第 114 列、第 60 行，黄色十字在第 155 列、第 59 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a SPIRIT ARROW nocked on a drawn bow: a straight white light shaft 2 squares thick with a pale cyan glow 1 square each side, from the cyan cross (the drawing hand) through the yellow cross (the bow hand) and 12 squares beyond it, ending in a leaf-shaped white-cyan arrowhead 9 squares long and 7 tall pointing RIGHT; two pale feather wisps 5 squares long at the cyan cross.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (114, 60); the yellow cross of the guide is at square (155, 59), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`kindred_bake_a_nock_3.png`**（定位图 `bake/kindred_bake_a_nock_3.png`，256×170 格，青色十字在第 106 列、第 54 行，黄色十字在第 165 列、第 55 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: the same SPIRIT ARROW at full draw, a little brighter: the shaft 2 squares thick from the cyan cross through the yellow cross and 12 squares beyond it, the leaf-shaped arrowhead 9 squares long pointing RIGHT, 3 white motes 2 squares big along the shaft.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (106, 54); the yellow cross of the guide is at square (165, 55), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. 普攻：松弦的一闪（画进普攻第 4 帧）

箭射出去那一下：握弓的手（黄色十字）前面炸开一团青白色的光，一道细长的光往**右**射出去（箭离弦），几点火花。画在她**上面**。

**`kindred_bake_a_loose_4.png`**（定位图 `bake/kindred_bake_a_loose_4.png`，256×170 格，黄色十字在第 162 列、第 55 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: the LOOSE: a burst of white-cyan light 20 squares across centered 8 squares RIGHT of the yellow cross (the bow hand), a straight streak of white light 2 squares thick and 40 squares long shooting to the RIGHT from it, 4 cyan sparks 2-3 squares big flying off; nothing over her face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the yellow cross of the guide is at square (162, 55), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. E 横生惧意：搭在弦上的狼烟之箭（画进 E 第 2、3 帧）

射横生惧意前弦上搭着一支带狼烟的箭：深紫色箭身、淡紫色芯、青白色箭头，箭身上缠着深靛色的狼烟往上飘。从青色十字（拉弦的手）穿过黄色十字（握弓的手），箭头伸出弓外。画在她**上面**。

**`kindred_bake_e_nock_2.png`**（定位图 `bake/kindred_bake_e_nock_2.png`，256×170 格，青色十字在第 128 列、第 71 行，黄色十字在第 173 列、第 69 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a DREAD ARROW nocked on a drawn bow: a straight violet shaft 3 squares thick with a pale lilac core, from the cyan cross (the drawing hand) through the yellow cross (the bow hand) and 12 squares beyond it, a white-cyan arrowhead 9 squares long and 7 tall pointing RIGHT, 3 curls of dark indigo smoke 3 squares thick rising off the shaft.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (128, 71); the yellow cross of the guide is at square (173, 69), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`kindred_bake_e_nock_3.png`**（定位图 `bake/kindred_bake_e_nock_3.png`，256×170 格，青色十字在第 141 列、第 62 行，黄色十字在第 198 列、第 65 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: the same DREAD ARROW at full draw: the shaft 3 squares thick from the cyan cross through the yellow cross and 12 squares beyond, the white-cyan arrowhead pointing RIGHT, the indigo smoke curls thicker and higher (up to 14 squares), a violet glow round the arrowhead.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (141, 62); the yellow cross of the guide is at square (198, 65), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. E 横生惧意：松弦（画进 E 第 4 帧）

带狼烟的箭射出去：握弓的手（黄色十字）前面炸开一团深靛色的狼烟，中间一点青白光，一道深紫色的光往**右**射出去。画在她**上面**。

**`kindred_bake_e_loose_4.png`**（定位图 `bake/kindred_bake_e_loose_4.png`，256×170 格，黄色十字在第 179 列、第 66 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: the DREAD LOOSE: a puff of dark indigo smoke 22 squares across centered 8 squares RIGHT of the yellow cross (the bow hand) with a white-cyan spark 5 squares big at its middle, a violet streak 3 squares thick and 40 squares long shooting to the RIGHT from it, smoke curls drifting up; nothing over her face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the yellow cross of the guide is at square (179, 66), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. Q 乱箭之舞：弦上扇开的三支灵箭（画进 Q 第 5 帧）

跳完落地拉弓：弦上同时搭着三支灵箭，从青色十字（拉弦的手）出发扇开：中间一支穿过黄色十字（握弓的手），上下两支各偏 12 度，箭头都伸出弓外。画在她**上面**。

**`kindred_bake_q_nock_5.png`**（定位图 `bake/kindred_bake_q_nock_5.png`，256×170 格，青色十字在第 105 列、第 78 行，黄色十字在第 163 列、第 69 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: THREE SPIRIT ARROWS nocked together and fanned: three white light shafts 2 squares thick with pale cyan glows, all starting at the cyan cross (the drawing hand); the middle one through the yellow cross (the bow hand) and 12 squares beyond it, the other two 12 degrees above and below it, each ending in a leaf-shaped white-cyan arrowhead 8 squares long pointing RIGHT.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (105, 78); the yellow cross of the guide is at square (163, 69), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. Q 乱箭之舞：三箭齐发（画进 Q 第 6 帧）

三支箭同时射出去：握弓的手（黄色十字）前面一团青白光，三道细光往**右**扇形射出（中间一道平的，上下各一道斜 12 度）。画在她**上面**。

**`kindred_bake_q_loose_6.png`**（定位图 `bake/kindred_bake_q_loose_6.png`，256×170 格，黄色十字在第 131 列、第 65 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: the VOLLEY: a burst of white-cyan light 18 squares across centered 8 squares RIGHT of the yellow cross (the bow hand), three white light streaks 2 squares thick and 40 squares long fanning out to the RIGHT from it (one level, one 12 degrees up, one 12 degrees down), cyan sparks 2-3 squares big; nothing over her face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the yellow cross of the guide is at square (131, 65), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. Q 乱箭之舞：跳跃时身后的灵光拖影（画进 Q 第 3、4 帧，画在她身后）

乱箭之舞是一个灵巧的跳跃：她身后（**左下**方，跳起的地方）拖着一道淡淡的青白色灵光，几片羽毛状的光丝往后飘。从青色十字（她的后蹄）往**左下**拖出去，第 3 帧长、第 4 帧开始散。画在她**后面**（被她挡住的地方不用画）。

**`kindred_bake_q_trail_3.png`**（定位图 `bake/kindred_bake_q_trail_3.png`，170×256 格，青色十字在第 65 列、第 137 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a GHOSTLY LEAP TRAIL behind the figure: a soft band of pale cyan and white spirit light 10 squares thick streaming from the cyan cross (her hind hooves) down and to the LEFT for 60 squares, toward the ground she jumped from, thinning to its end, 4 feather-shaped wisps 8 squares long and white motes along it.
Layout: ONE image 1020x1536, the same size and 6-px square grid as the guide picture (a 170 x 256 square grid); the cyan cross of the guide is at square (65, 137), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`kindred_bake_q_trail_4.png`**（定位图 `bake/kindred_bake_q_trail_4.png`，256×170 格，青色十字在第 108 列、第 104 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: the TRAIL breaking up: the band 50 squares long from the cyan cross (her hind hooves) down and to the LEFT, its far half turning into feather wisps and fading motes.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (108, 104), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. R 羊灵生息：举起的弓上一闪（画进大招第 5 帧）

羊灵把弓举向天空：弓的顶端（黄色十字）炸开一颗白亮的星光，几道短光芒，光点往下飘落到她身边（大招的法阵就在这一帧出现）。画在她**上面**，别挡住她的脸。

**`kindred_bake_r_raise_5.png`**（定位图 `bake/kindred_bake_r_raise_5.png`，170×256 格，黄色十字在第 101 列、第 18 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a respite ramp (#FFFFFF, #E1FBFD, #C0E6FC, #89F7DD, #A6AAF8).
Effect: a RADIANT STAR at the yellow cross (the raised bow's top): a white four-pointed star 26 squares across with a pale cyan glow, 6 light rays 8 squares long, 10 white and mint motes 2-3 squares big falling below it on both sides of the bow; nothing over her face.
Layout: ONE image 1020x1536, the same size and 6-px square grid as the guide picture (a 170 x 256 square grid); the yellow cross of the guide is at square (101, 18), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. W 狼灵狂热：举起的手里召来狼烟（画进 W 第 2 帧）

羊灵举手召唤狼灵去狩猎：举起的手（青色十字）上方卷起一团深靛色的狼烟，烟里两点青色的狼眼一闪。画在她**上面**，别挡住她的脸。

**`kindred_bake_w_call_2.png`**（定位图 `bake/kindred_bake_w_call_2.png`，170×256 格，青色十字在第 51 列、第 44 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or wisps, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Wolf dread ramp (#E6DEFF, #A6AAF8, #8E82F7, #5C44DE, #3E1C76, #250E43) and a Lamb spirit-light ramp (#FFFFFF, #E1FBFD, #89F7DD, #54EDD7, #39B4F7, #2E78F2).
Effect: a SUMMONING SWIRL above the cyan cross (the raised hand): curls of dark indigo smoke 3-4 squares thick, 28 squares across, rising and swirling up to 32 squares above the hand, a violet glow inside, two glowing cyan eyes 2 squares big in it; nothing over her face.
Layout: ONE image 1020x1536, the same size and 6-px square grid as the guide picture (a 170 x 256 square grid); the cyan cross of the guide is at square (51, 44), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the crosses or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kindred_fx_a_arrow` | view_projectiles `league_kindred_a_arrow`（朝飞行方向转，画成朝右飞；上下对称） | 14 × 4 |
| `kindred_fx_q_arrow` | view_projectiles `league_kindred_q_arrow`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 5 |
| `kindred_fx_e_arrow` | view_projectiles `league_kindred_e_arrow`（朝飞行方向转，画成朝右飞；上下对称） | 18 × 6 |
| `kindred_fx_a_hit` | view_effects `league_kindred_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `kindred_fx_q_hit` | view_effects `league_kindred_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `kindred_fx_e_hit` | view_effects `league_kindred_e_hit`（跟随，画在人物上面；左右对称） | 18 |
| `kindred_fx_e_mark` | view_effects `league_kindred_e_mark`（跟随，画在人物上面；中间的漩涡不用对称） | 11 × 11 |
| `kindred_fx_p_stack` | view_buffs `league_kindred_p_stack`（跟随，画在人物上面；中间的漩涡不用对称） | 10 × 12 |
| `kindred_fx_e_bite` | view_effects `league_kindred_e_bite`（BIG，跟随，画在人物上面；左右对称） | 28 × 32 |
| `kindred_fx_w_bite` | view_effects `league_kindred_w_bite`（跟随，画在人物上面；左右对称） | 18 × 18 |
| `kindred_fx_q_dash` | view_effects `league_kindred_q_dash`（画在人物下面，不跟随；左右对称、上下对称） | 24 × 8 |
| `kindred_fx_w_zone` | view_effects `league_kindred_w_zone`（BIG，画在人物下面，不跟随，留在她放 W 的地方；左右对称、上下对称） | 120 × 46 |
| `kindred_fx_r_zone` | view_effects `league_kindred_r_zone`（BIG，画在人物下面，不跟随，留在她放大招的地方；中间的漩涡不用对称） | 100 × 38 |
| `kindred_fx_r_heal` | view_effects `league_kindred_r_heal`（跟随，画在人物上面；左右对称） | 18 × 32 |
| `kindred_bake_a_nock_<帧>` | 画进 `hd_attack` 第 2、3 帧（人物上面） | 高清格子 |
| `kindred_bake_a_loose_<帧>` | 画进 `hd_attack` 第 4 帧（人物上面） | 高清格子 |
| `kindred_bake_e_nock_<帧>` | 画进 `hd_skill2` 第 2、3 帧（人物上面） | 高清格子 |
| `kindred_bake_e_loose_<帧>` | 画进 `hd_skill2` 第 4 帧（人物上面） | 高清格子 |
| `kindred_bake_q_nock_<帧>` | 画进 `hd_skill` 第 5 帧（人物上面） | 高清格子 |
| `kindred_bake_q_loose_<帧>` | 画进 `hd_skill` 第 6 帧（人物上面） | 高清格子 |
| `kindred_bake_q_trail_<帧>` | 画进 `hd_skill` 第 3、4 帧（人物后面） | 高清格子 |
| `kindred_bake_r_raise_<帧>` | 画进 `hd_ult` 第 5 帧（人物上面） | 高清格子 |
| `kindred_bake_w_call_<帧>` | 画进 `hd_w_cast` 第 2 帧（人物上面） | 高清格子 |

- 两张表：`asset/league/effects/league_kindred_fx`（小的）和 `league_kindred_big`（e_bite、w_zone、r_zone），tag = 名字（build_kindred.py 的 views）。
- e_mark、p_stack 画在格子中间：导入时按目标 / 她的头顶高度垫高；地上的 q_dash、w_zone、r_zone 椭圆中心放在脚底线（站位点下方 11 格）；r_heal 的底放在脚底线。w_zone 的 3-8 帧、r_zone 的 3-6 帧按技能时长（510、240 tick）重复。
- 画进帧的图在 restyle 之后（rig_kindred.py 补洞那一步）按 `bake_cells.json` 从画布上切下这一帧的范围，叠到 `assets/source/ppu/kindred_<tag>.png` 的高清帧上（over 盖在上面，under 只填空白），伸出帧外的地方两边一样加宽；1 倍表按格子投票一起更新。
- 用 `pixel_1x/` 切格（import_nidalee / import_nilah_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
