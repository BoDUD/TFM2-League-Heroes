# 兽灵行者 乌迪尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型已定（`design/udyr_designs.png`，从左到右：平常护头的姿势——光膀子的壮汉，暗红纹身、深色长脏辫和络腮胡、一根蓝羽毛发辫、白绷带拳头、橙红大念珠；熊姿态——披着熊皮、熊头盖在拳头上；公羊姿态——两只大卷羊角；凤凰姿态——两臂张开、胳膊上一排深蓝羽刃）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），平常 40 格高、34 格宽，熊 41×44，公羊 46×43，凤凰 49×60（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/udyr_size.png`：四种姿态放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里乌迪尔自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。**第一行的 stanceicon 是四个兽灵的图腾**（熊、野猪、公羊、凤凰的正面头像），`q_on`、`e_on`、`r_on`、`w_on` 里的图腾照它画。颜色按兽灵分：**熊（Q）紫蓝色闪电**，**公羊（E）橙色火焰**，**凤凰（R）冰蓝色的风和冰晶**，**野猪（被动里的坚铁甲胄）玉绿色**。
> - **特效要亮**：每道光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **光、闪电、火、风、尘土都没有黑描边**；**实物**（冰晶碎片）有 1 格近黑描边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`q_bolt`、`r_rel`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进他自己帧里的**（`q_swipe`、`e_trail`）**朝右画，不用对称**（跟着他的身体一起翻转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `udyr_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/udyr_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/udyr_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 缠绷带的拳头，熊姿态时是熊爪 | `a_hit` · `q_swipe` |
| 技能 1 = Q「狂暴爪击」（熊） | 进入熊姿态，接下来两拳加攻速、加伤；同一姿态再放（觉醒）两拳召来闪电 | `q_on` · `q_wake` · `q_as` · `q_swipe` · `q_hit` · `q_bolt` · `q_bolt_hit` |
| 技能 2 = E「踏火蛮冲」（公羊） | 进入公羊姿态，加速冲到敌人面前撞晕；觉醒时免疫定身 | `e_on` · `e_wake` · `e_ms` · `e_imm` · `e_trail` · `e_hit` · `e_stun` |
| 大招 = R「极凌飓风」（凤凰） | 进入凤凰姿态，冰风暴绕身伤害减速，结束时把风暴放出去追敌人 | `r_on` · `r_storm` · `r_hit` · `r_slow` · `r_rel` · `r_rel_hit` |
| 被动「众灵纽带」+ W「坚铁甲胄」（野猪） | 放技能后两次攻击加攻速；隔一段时间放技能时罩上护盾，接下来两拳回血 | `w_on` · `w_sh` · `w_heal` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、闪电、火、风、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（实物——冰晶碎片——有 1 格近黑描边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 熊·紫蓝闪电：`#FFFFFF`、`#E4E8FF`、`#A8B4FF`、`#6E78F0`、`#4A3CC8`、`#2A1A78`；
  - 公羊·橙色火焰：`#FFFFFF`、`#FFF2B0`、`#FFC850`、`#FF8A1E`、`#E0480E`、`#8A1E08`；
  - 凤凰·冰蓝：`#FFFFFF`、`#E2F8FF`、`#A8E6FF`、`#5CC0F0`、`#2A84C8`、`#164A86`；
  - 野猪·玉绿：`#FFFFFF`、`#E0FFE8`、`#9CF0B8`、`#4ED08A`、`#1E9A5E`、`#0E5A3A`；
  - 尘土：`#F4E8D0`、`#D2BC94`、`#A08A66`、`#6E5C44`；
- 打中、爆发居中画，不旋转；地面上的圈（火圈、霜、风暴的圈）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：冰风暴半径 17000，闪电溅射半径 9000）。

### 1. `udyr_fx_a_hit.png`：普攻：拳头打中，3 帧

缠绷带的拳头砸中：一团白色的冲击闪光带一点尘土。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#F4E8D0, #D2BC94, #A08A66, #6E5C44), an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08).
Effect: A PUNCH HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow four-pointed flash 5 squares across; 2 the flash 8 across with a ring of dust puffs at mirrored places; 3 only a few dust puffs further out.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `udyr_fx_q_on.png`：Q 狂暴爪击：熊之灵的图腾在他头上亮起，5 帧

进入熊姿态：一个**熊头图腾**（正面的熊头，像刻出来的图腾面具，参考 stanceicon 里的熊）在他头顶亮起又散掉，紫蓝色的电光。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue lightning ramp (#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78).
Effect: A SPIRIT SIGIL rising over his head, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small violet-blue flash 4 squares across; 2 the BEAR HEAD SIGIL appearing, a bold flat emblem seen from the front (like a carved totem mask, as in udyr_base_vgu_stanceicon_2x2), 12 squares wide, white core and lit edges; 3 the sigil at full brightness with 4 short rays; 4 the sigil 1 square higher, its inner lines fading; 5 only its outline in its darkest shades, breaking into specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); the sigil's middle on the cell's middle (the cell sits over his head). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `udyr_fx_q_wake.png`：Q 觉醒：熊之灵的闪电在他身上炸开，6 帧

同一姿态再放 Q（觉醒）：紫蓝色的闪电从他身边四周劈下、在他周围一圈噼啪作响（参考 q_ele 系列），熊头图腾在头顶。**左右对称**，6 帧。**身体位置留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue lightning ramp (#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78).
Effect: AN AWAKENING STORM OF LIGHTNING round him, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 four short lightning forks crackling at mirrored places round the edge of the cell; 2 two big jagged bolts striking down on both sides of him from the top of the cell to the ground, white cores; 3 the bolts at full length with branches, a ring of sparks on the ground ellipse round his feet; 4 a BEAR HEAD SIGIL 12 squares wide flashing over his head, the bolts shorter; 5 small arcs jumping round him; 6 fading sparks. The middle (his body: 28 squares wide, 40 tall) stays EMPTY.
Layout: one horizontal row of 6 equal square cells, image size 4800x800 (each cell 800x800, 16 px a square); he stands in the middle, not drawn: hunched like a bear, 43 squares wide and 41 tall (his feet on the cell's bottom row, 2 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `udyr_fx_q_as.png`：Q 熊爪状态：脚下的电光（循环），4 帧

熊姿态的攻速加成还在：他脚下一圈贴着地面的紫蓝色电弧，偶尔往上跳一点火花。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue lightning ramp (#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78).
Effect: A CRACKLING GROUND RING, 4 frames looping, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse of small violet-blue electric arcs 34 squares wide and 8 tall on the ground, a few sparks jumping 2-3 squares up from it, the arcs at different places each frame; the inside of the ellipse empty.
Layout: one horizontal row of 4 equal 34:10 cells, image size 2176x160 (each cell 544x160, 16 px a square); the ellipse's middle on the cell's middle; he stands in the middle, not drawn: hunched like a bear, 43 squares wide and 41 tall (only his feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `udyr_fx_q_swipe.png`：Q 熊爪攻击：往前抓出的三道爪痕弧光（画进他的帧），3 帧

熊姿态的普攻：熊爪往前一抓，三道并排的紫蓝色爪痕弧光（带白芯）。**朝右画**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue lightning ramp (#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78).
Effect: THREE CLAW STREAKS, 3 frames, pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry): 1 three parallel thin arcs starting at the cell's left side, curving down-forward; 2 the three arcs at full length (24 squares), white cores, violet edges, small sparks at their ends; 3 the arcs thinning and breaking into specks.
Layout: one horizontal row of 3 equal 28:24 cells, image size 1344x384 (each cell 448x384, 16 px a square); his fist at the cell's left edge, half way up (not drawn). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `udyr_fx_q_hit.png`：Q 强化攻击打中：三道爪痕，4 帧

熊爪打中敌人：三道竖着的紫蓝色爪痕一闪，四周跳电火花。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue lightning ramp (#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78).
Effect: THREE CLAW MARKS, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 three vertical claw slashes side by side, the middle one longest (14 squares), white cores, violet edges; 3 the slashes with sparks jumping off at mirrored places; 4 fading slashes and specks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `udyr_fx_q_bolt.png`：Q 觉醒的闪电球（弹道，循环），4 帧

觉醒熊爪召来的闪电，飞向目标的一小团电光球。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue lightning ramp (#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78).
Effect: A SMALL BALL OF LIGHTNING, 4 frames looping, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a white core 3 squares across inside a violet-blue crackle, two short arcs trailing behind on the left, the arcs at different places each frame.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); the ball's middle on the cell's middle row, 2 squares from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `udyr_fx_q_bolt_hit.png`：Q 觉醒：闪电劈在目标身上，5 帧

觉醒熊爪的闪电从天上直直劈到敌人身上，落地炸开一圈电花。**左右对称**（中间一道直的主干，两边对称的分叉），5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-blue lightning ramp (#FFFFFF, #E4E8FF, #A8B4FF, #6E78F0, #4A3CC8, #2A1A78).
Effect: A LIGHTNING STRIKE from the sky, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin white line from the top of the cell to the ground row; 2 the bolt at full width (3 squares, white core, violet edges) with MIRRORED zig-zag branches on both sides; 3 the bolt and a flash on the ground ellipse (16 x 5 squares) at its foot; 4 the bolt gone, the ground flash with sparks flying out at mirrored places; 5 fading sparks.
Layout: one horizontal row of 5 equal 22:48 cells, image size 1760x768 (each cell 352x768, 16 px a square); the ground ellipse's middle 3 squares above the cell's bottom, centered; the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `udyr_fx_e_on.png`：E 踏火蛮冲：公羊之灵的图腾在他头上亮起，5 帧

进入公羊姿态：一个**公羊头图腾**（正面的羊头，两只卷角）在他头顶亮起又散掉，橙色的火光。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08).
Effect: A SPIRIT SIGIL rising over his head, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small orange flash 4 squares across; 2 the RAM (two curled horns) HEAD SIGIL appearing, a bold flat emblem seen from the front (like a carved totem mask, as in udyr_base_vgu_stanceicon_2x2), 12 squares wide, white core and lit edges; 3 the sigil at full brightness with 4 short rays; 4 the sigil 1 square higher, its inner lines fading; 5 only its outline in its darkest shades, breaking into specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); the sigil's middle on the cell's middle (the cell sits over his head). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `udyr_fx_e_wake.png`：E 觉醒：他身边腾起一圈火焰，6 帧

同一姿态再放 E（觉醒，免控）：他脚下炸开一圈火焰往上腾起，公羊头图腾在头顶。**左右对称**，6 帧。**身体位置留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08).
Effect: A RING OF FIRE BURSTING UP round him, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ring of embers on the ground ellipse (40 x 10 squares) round his feet; 2 flames rising from the ring on both sides, 12 squares tall; 3 the flames at full height (24 squares) curling inward at the top like horns, white-yellow cores; 4 a RAM HEAD SIGIL 12 squares wide flashing over his head, the flames lower; 5 low flames and embers rising; 6 a few embers. The middle (his body: 30 squares wide, 44 tall) stays EMPTY.
Layout: one horizontal row of 6 equal 50:52 cells, image size 4800x832 (each cell 800x832, 16 px a square); he stands in the middle, not drawn: head low under two big ram horns, 43 squares wide and 46 tall (his feet on the cell's bottom row, 2 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `udyr_fx_e_ms.png`：E 公羊状态：脚下的火（循环），4 帧

公羊姿态的移速加成还在：他脚下贴地的一圈小火苗，往上飘火星。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08).
Effect: LOW FLAMES AT HIS FEET, 4 frames looping, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse of small flame tongues 30 squares wide and 6 tall on the ground, a few embers drifting 2-4 squares up, the flames flickering differently each frame; the inside of the ellipse empty.
Layout: one horizontal row of 4 equal 30:10 cells, image size 1920x160 (each cell 480x160, 16 px a square); the ellipse's middle on the cell's middle; he stands in the middle, not drawn: head low under two big ram horns, 43 squares wide and 46 tall (only his feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `udyr_fx_e_imm.png`：E 觉醒免控：头顶一圈火焰角环（循环），4 帧

觉醒后免疫定身：他头顶一圈燃烧的光环，两边各翘起一只火焰羊角。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08).
Effect: A BURNING HALO over his head, 4 frames looping, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat glowing ellipse 14 squares wide and 3 tall, a small flame horn curling up and out on each end, the flames flickering differently each frame.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); the halo's middle on the cell's middle (the cell sits just over his head). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `udyr_fx_e_trail.png`：E 冲锋：身后拖着的火焰（画进他的帧），4 帧

公羊冲锋：他身后（左边）拖出一道贴地的火焰尾巴，脚下溅火星。**朝右画**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08), a dust ramp (#F4E8D0, #D2BC94, #A08A66, #6E5C44).
Effect: A FIRE TRAIL behind a charge, 4 frames, pointing FORWARD to the RIGHT (it is drawn into his own frames, so it needs no left-right symmetry): a tongue of fire lying low along the ground, thickest at the right end (his feet) and thinning to the LEFT, embers and dust puffs flying back; the flames move each frame.
Layout: one horizontal row of 4 equal 36:18 cells, image size 2304x288 (each cell 576x288, 16 px a square); his feet at the cell's bottom right corner (not drawn). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `udyr_fx_e_hit.png`：E 撞上：晕眩的那一下，4 帧

公羊冲撞的一击打中：一团橙色火焰爆开，地上一圈裂开的尘土。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08), a dust ramp (#F4E8D0, #D2BC94, #A08A66, #6E5C44).
Effect: A FIERY RAM IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 8 squares across; 2 a burst of fire 18 squares across with flame tongues at mirrored places, a ring of dust on the ground ellipse; 3 the fire breaking into embers, the dust ring wider; 4 fading embers and dust.
Layout: one horizontal row of 4 equal square cells, image size 1536x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `udyr_fx_e_stun.png`：E 晕眩（敌人头上，循环），4 帧

被撞晕的敌人头上转着的几颗小火星。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF2B0, #FFC850, #FF8A1E, #E0480E, #8A1E08).
Effect: STUN EMBERS circling, 4 frames looping, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small star-shaped embers on a flat ellipse 14 squares wide and 4 tall, moving round it frame by frame (each frame mirrored left to right as a whole picture).
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); the ellipse's middle on the cell's middle (the cell sits over the target's head). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `udyr_fx_r_on.png`：R 极凌飓风：凤凰之灵的图腾在他头上亮起，5 帧

进入凤凰姿态：一个**凤凰头图腾**（正面的鸟头，两边张开的羽冠）在他头顶亮起又散掉，冰蓝色的光。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E2F8FF, #A8E6FF, #5CC0F0, #2A84C8, #164A86).
Effect: A SPIRIT SIGIL rising over his head, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small ice-blue flash 4 squares across; 2 the PHOENIX (a bird head with a fan of crest feathers) HEAD SIGIL appearing, a bold flat emblem seen from the front (like a carved totem mask, as in udyr_base_vgu_stanceicon_2x2), 12 squares wide, white core and lit edges; 3 the sigil at full brightness with 4 short rays; 4 the sigil 1 square higher, its inner lines fading; 5 only its outline in its darkest shades, breaking into specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); the sigil's middle on the cell's middle (the cell sits over his head). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `udyr_fx_r_storm.png`：R 冰风暴围着他转（循环），6 帧

凤凰的冰风暴绕着他转：几条冰蓝色的风带绕成一个斜着看的大圈，里面卷着冰晶碎片和雪花，前面的风带从他脚前经过、后面的从他背后绕过。**左右对称**（每一帧整体左右对称），6 帧循环。**身体位置留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E2F8FF, #A8E6FF, #5CC0F0, #2A84C8, #164A86).
Effect: A GLACIAL STORM WHIRLING round him, 6 frames looping, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three or four bands of icy wind circling on a big ellipse (60 squares wide, 18 tall, its middle 10 squares above the ground) with small ice shards and snowflakes carried in them, the bands and the shards at new places each frame as if spinning; a faint second ring higher up (at his chest) narrower; white cores on the bands. SOLID OBJECTS (ice shards) have a 1-square near-black outline; light, lightning, fire, wind and dust have none. The middle (his body: 34 squares wide, 46 tall) stays EMPTY except the bands passing in front of his legs.
Layout: one horizontal row of 6 equal 64:44 cells, image size 6144x704 (each cell 1024x704, 16 px a square); he stands in the middle, not drawn: arms spread wide, 59 squares wide and 49 tall (his feet on the cell's bottom row, 4 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `udyr_fx_r_hit.png`：R 风暴刮中的敌人，3 帧

风暴刮中：几片冰晶擦过、一小团寒气。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E2F8FF, #A8E6FF, #5CC0F0, #2A84C8, #164A86).
Effect: AN ICE GRAZE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 four small ice shards flying out at mirrored places with a puff of frost; 3 the shards further out, the frost fading. SOLID OBJECTS (ice shards) have a 1-square near-black outline; light, lightning, fire, wind and dust have none.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `udyr_fx_r_slow.png`：R 减速（敌人脚下，循环），4 帧

被冰风暴减速的敌人：脚下一圈结霜的地面，几颗小冰晶。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E2F8FF, #A8E6FF, #5CC0F0, #2A84C8, #164A86).
Effect: A FROST PATCH, 4 frames looping, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse of frost 20 squares wide and 5 tall on the ground with tiny ice crystals glinting at different places each frame.
Layout: one horizontal row of 4 equal 20:6 cells, image size 1280x96 (each cell 320x96, 16 px a square); the ellipse's middle on the cell's middle; the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (only its feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `udyr_fx_r_rel.png`：R 风暴放出去：飞向敌人的冰风旋涡（弹道，循环），4 帧

风暴结束时被放出去追敌人：一团往前飞的冰风旋涡，前头像一只展翅的冰凤凰的轮廓。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E2F8FF, #A8E6FF, #5CC0F0, #2A84C8, #164A86).
Effect: A FLYING ICE STORM, 4 frames looping, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a spinning ball of icy wind 14 squares across at the right end, two swept-back WING SHAPES of wind and feathers spreading up and down from it (mirrored top to bottom), a trail of snow and shards behind on the left; the wind bands turn each frame. SOLID OBJECTS (ice shards) have a 1-square near-black outline; light, lightning, fire, wind and dust have none.
Layout: one horizontal row of 4 equal 30:20 cells, image size 1920x320 (each cell 480x320, 16 px a square); the ball's middle on the cell's middle row, 2 squares from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `udyr_fx_r_rel_hit.png`：R 风暴炸在敌人身上，6 帧

放出去的风暴砸中：冰风往四周炸开，冰晶飞散，地上一圈霜。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice-blue ramp (#FFFFFF, #E2F8FF, #A8E6FF, #5CC0F0, #2A84C8, #164A86).
Effect: AN ICE STORM BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across; 2 a ring of icy wind 20 squares across with ice shards flying out at mirrored places; 3 the ring 30 across, the shards further out, a frost ellipse on the ground (30 x 8); 4 the wind breaking into curls; 5 the shards falling, snowflakes; 6 fading frost and specks. SOLID OBJECTS (ice shards) have a 1-square near-black outline; light, lightning, fire, wind and dust have none.
Layout: one horizontal row of 6 equal square cells, image size 3456x576 (each cell 576x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `udyr_fx_w_on.png`：被动·坚铁甲胄：野猪之灵的护盾罩上来，6 帧

坚铁甲胄发动：头顶亮起**野猪头图腾**，一层玉绿色的护盾从上往下罩住他（只画护盾的外沿和几道亮纹）。**左右对称**，6 帧。**身体位置留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade-green light ramp (#FFFFFF, #E0FFE8, #9CF0B8, #4ED08A, #1E9A5E, #0E5A3A).
Effect: AN IRON MANTLE CLOSING round him, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a BOAR HEAD SIGIL (a front-facing boar head with tusks) 12 squares wide flashing over his head; 2 a jade-green shell edge appearing at the top, an arch 30 squares wide; 3 the edge sweeping down both sides into a tall rounded dome 44 wide and 48 tall, angular plate lines on it like a boar's bristled hide; 4 the whole dome outline bright; 5 the dome dimmer with a few bright plate edges; 6 a faint outline. Only the dome's EDGE (2-3 squares thick) and a few plate lines are drawn; the middle (his body) stays EMPTY.
Layout: one horizontal row of 6 equal 48:52 cells, image size 4608x832 (each cell 768x832, 16 px a square); he stands in the middle, not drawn: a burly man 33 squares wide and 40 tall, fists raised (his feet on the cell's bottom row, 2 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `udyr_fx_w_sh.png`：被动·坚铁甲胄的护盾（他身上，循环），4 帧

护盾还在：罩着他的玉绿色护盾外沿，一道亮光沿着外沿慢慢流动。**左右对称**，4 帧循环。**身体位置留空**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade-green light ramp (#FFFFFF, #E0FFE8, #9CF0B8, #4ED08A, #1E9A5E, #0E5A3A).
Effect: A SHIMMERING SHIELD DOME, 4 frames looping, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the outline of a tall rounded dome 44 squares wide and 48 tall, 1-2 squares thick, in its middle shades with a few angular plate lines, a bright highlight travelling down both sides at the same height (mirrored) frame by frame. The middle (his body) stays EMPTY.
Layout: one horizontal row of 4 equal 46:50 cells, image size 2944x800 (each cell 736x800, 16 px a square); he stands in the middle, not drawn: a burly man 33 squares wide and 40 tall, fists raised (his feet on the cell's bottom row, 2 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `udyr_fx_w_heal.png`：被动·坚铁甲胄：攻击回血，4 帧

坚铁甲胄期间的攻击回血：玉绿色的光点和几道往上飘的光线从他身上升起。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade-green light ramp (#FFFFFF, #E0FFE8, #9CF0B8, #4ED08A, #1E9A5E, #0E5A3A).
Effect: A HEALING RISE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 four small jade sparkles at mirrored places low on the cell; 2 thin rays of light rising from them, 8 squares tall; 3 the rays higher and a few small plus-shaped sparkles; 4 fading sparkles at the top.
Layout: one horizontal row of 4 equal 24:30 cells, image size 1536x480 (each cell 384x480, 16 px a square); his chest in the cell's middle (not drawn). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `udyr_fx_a_hit` | view_effects `league_udyr_a_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `udyr_fx_q_on` | view_effects `league_udyr_q_on`（他身上，z 3；左右对称） | 16 × 16 |
| `udyr_fx_q_wake` | view_effects `league_udyr_q_wake`（他身上，z 3；左右对称） | 50 × 50 |
| `udyr_fx_q_as` | view_buffs `league_udyr_q_as`（跟着他，循环，z -1；左右对称） | 34 × 10 |
| `udyr_fx_q_swipe` | 画进他自己的 q_attack 帧（bake_caster_fx；朝右） | 28 × 24 |
| `udyr_fx_q_hit` | view_effects `league_udyr_q_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `udyr_fx_q_bolt` | view_projectiles `league_udyr_q_bolt`（随飞行方向转；上下对称） | 10 × 8 |
| `udyr_fx_q_bolt_hit` | view_effects `league_udyr_q_bolt_hit`（跟随目标，z 2；左右对称） | 22 × 48 |
| `udyr_fx_e_on` | view_effects `league_udyr_e_on`（他身上，z 3；左右对称） | 16 × 16 |
| `udyr_fx_e_wake` | view_effects `league_udyr_e_wake`（他身上，z 3；左右对称） | 50 × 52 |
| `udyr_fx_e_ms` | view_buffs `league_udyr_e_ms`（跟着他，循环，z -1；左右对称） | 30 × 10 |
| `udyr_fx_e_imm` | view_buffs `league_udyr_e_imm`（跟着他，循环，z 3；左右对称） | 20 × 8 |
| `udyr_fx_e_trail` | 画进他自己的 e_run 帧（bake_caster_fx；朝右） | 36 × 18 |
| `udyr_fx_e_hit` | view_effects `league_udyr_e_hit`（跟随目标，z 2；左右对称） | 24 × 24 |
| `udyr_fx_e_stun` | view_buffs `league_udyr_e_stun`（跟着目标，循环，z 3；左右对称） | 16 × 6 |
| `udyr_fx_r_on` | view_effects `league_udyr_r_on`（他身上，z 3；左右对称） | 16 × 16 |
| `udyr_fx_r_storm` | view_buffs `league_udyr_r_storm`（跟着他，循环，z 3；左右对称） | 64 × 44 |
| `udyr_fx_r_hit` | view_effects `league_udyr_r_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `udyr_fx_r_slow` | view_buffs `league_udyr_r_slow` 和 `r2_slow`（跟着目标，循环，z -1；左右对称） | 20 × 6 |
| `udyr_fx_r_rel` | view_projectiles `league_udyr_r_rel`（随飞行方向转；上下对称） | 30 × 20 |
| `udyr_fx_r_rel_hit` | view_effects `league_udyr_r_rel_hit`（跟随目标，z 2；左右对称） | 36 × 36 |
| `udyr_fx_w_on` | view_effects `league_udyr_w_on`（他身上，z 3；左右对称） | 48 × 52 |
| `udyr_fx_w_sh` | view_buffs `league_udyr_w_sh`（跟着他，循环，z 3；左右对称） | 46 × 50 |
| `udyr_fx_w_heal` | view_effects `league_udyr_w_heal`（他身上，z 3；左右对称） | 24 × 30 |

- 两张表：`asset/league/effects/league_udyr_fx`（小的）和 `league_udyr_big`（q_wake、q_bolt_hit、e_wake、r_storm、r_rel、r_rel_hit、w_on、w_sh），tag = 名字（build_udyr.py 的 views；r2_slow 的 tag 是 `r_slow`）。
- 弹道（q_bolt、r_rel）断言上下对称；朝前的（q_swipe、e_trail）用 tools/fix/bake_caster_fx.py 画进他的帧（q_attack / e_run），不进表；其余断言左右对称；q_on、e_on、r_on 放在他头顶（view 的 y 偏移），w_on、w_sh、r_storm 跟随他。
- 用 `pixel_1x/` 切格（import_neeko_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
