# 影哨 阿克尚：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型和动作已定（`design/akshan_idle.png`：3/4 正面朝右的游侠枪手，深棕长卷发和小发髻、短胡子、浅蓝白围巾、橙红饰带、暗红长披风、青绿布片，近侧手把一把暗红青铜的回旋镖手枪举在头边）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），46 格高、31 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/akshan_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/akshan_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿克尚自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**子弹和命中是金色的光**，**哨兵之光（被动爆发、护盾、伪装）是淡天蓝色**，**大招和恶徒标记是红金色**，**回旋镖和钩索是青铜色**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **飞行物（子弹、回旋镖、大子弹）朝右画**：游戏会按飞行方向转。**其他所有图严格左右对称**（逐格对称）：这些画面在红色方不会镜像。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `akshan_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/akshan_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/akshan_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「无所不用」 | 每次普攻开两枪；对同一目标第 3 下多一段伤害，打英雄还给自己护盾 | `a_shot` · `a_hit` · `p_hit` · `p_sh` |
| 技能 1 = Q「去而复还」 | 扔出回旋镖，去和回各打一次，接回手里 | `q_rang` · `q_hit` · `q_catch` |
| 技能 2 = E「骄行荡寇」 | 朝天甩出钩索，荡过去一路开枪，最后翻滚落地 | `e_hook` · `a_shot` · `a_hit` |
| W「赴险夺人」 | 被围住时伪装加速；（扩展包）杀了队友的敌人头顶出现恶徒标记 | `w_camo` · `w_ms` · `w_mark` |
| 大招「恩怨相抵」 | 锁定受伤的英雄蓄力，然后连射大子弹 | `r_lock` · `r_bullet` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、风、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：回旋镖、钩索和绳子、恶徒标记里的小骷髅可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 金色的光（子弹、命中）：`#FFFFFF`、`#FFF4C8`、`#FFD36A`、`#FFA62B`、`#E2681A`、`#9C3A12`；
  - 淡天蓝的哨兵之光（被动、护盾、伪装）：`#FFFFFF`、`#E8FBFF`、`#B8ECF4`、`#7FD3E2`、`#3FA9BF`、`#1F6E86`；
  - 红色（大招、恶徒标记）：`#FFFFFF`、`#FFD0C0`、`#FF7A5A`、`#E8341C`、`#A8160E`、`#600A08`；
  - 青铜色（回旋镖、钩索）：`#FFF6E0`、`#F2C77A`、`#C98A3A`、`#8E5524`、`#5A3216`、`#2E180C`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头（光的特效一段，有实心东西的另一段）。大小写在每条里（1 个游戏像素约等于 1000 距离单位：普攻射程 55000）。

### 1. `akshan_fx_a_shot.png`：普攻 / E 的子弹（飞行，跟着方向转），3 帧

遗迹手枪打出的子弹：一颗金白色的小光弹，后面拖一道短短的橙金色光尾（参考 Missile、Trail07、Glow01）。**朝右画**（游戏会按飞行方向转）。约 10 × 4 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a SMALL GLOWING BULLET in flight, 3 frames, a loop, pointing RIGHT (the game turns it to its flight), centered vertically, its nose at the right of the cell: a white-gold bolt 3x2 squares at the front, a short orange-gold tail 6 squares behind it thinning out; the tail flickers a little frame to frame.
Layout: one horizontal row of 3 equal 10:4 cells, image size 480x64 (each cell 160x64, 16 px a square); the bolt's nose 1 square from the cell's right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `akshan_fx_q_rang.png`：Q 去而复还：转着飞的回旋镖（飞行），4 帧

从枪上甩出去的回旋镖：一把青铜色的弯刃（像他枪口那两道弯钩，V 字形，刃口一圈金白色的亮边），一帧一帧转（每帧转 90 度），身后一圈淡金色的残影弧（参考 Boomerang、Boomerang02、Swirl02）。约 12 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, solid objects with a 1-square near-black outline and flat 3-4 step shading, light on them without an outline, colours only from a bronze ramp (#FFF6E0, #F2C77A, #C98A3A, #8E5524, #5A3216, #2E180C) and a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a SPINNING BOOMERANG BLADE in flight, 4 frames, a seamless loop: a bronze V-shaped curved blade 10 squares across (a 1-square dark outline, a lit gold-white cutting edge, a dark bronze inner edge), turned a quarter turn more each frame (0, 90, 180, 270 degrees), a faint gold motion arc (no outline) following its tips.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `akshan_fx_r_bullet.png`：R 恩怨相抵：大子弹（飞行），3 帧

大招打出的子弹：比普攻大的金红色光弹，中心白色，后面一道长长的红金色光尾，尾巴两边几颗火星（参考 Beam05B、Trail01、P_LensFlare）。**朝右画**。约 16 × 6 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12) and a red ramp (#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08).
Effect: a HEAVY GLOWING ROUND in flight, 3 frames, a loop, pointing RIGHT (the game turns it to its flight), centered vertically, its nose at the right of the cell: a white-hot core 4x3 squares wrapped in gold at the front, a red-gold tail 11 squares behind it tapering to a point, 2 sparks beside the tail; the tail flickers frame to frame.
Layout: one horizontal row of 3 equal 16:6 cells, image size 768x96 (each cell 256x96, 16 px a square); the core's nose 1 square from the cell's right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `akshan_fx_a_hit.png`：普攻 / E 命中（目标身上），4 帧

子弹打中：一个小小的金白色星形闪光，几颗火星往外蹦（参考 BA_LensFlare、Glow02、Impact01）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a SMALL BULLET IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 3 squares; 2 a gold-white 4-point star 8 squares; 3 the star thinner, 4 gold sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `akshan_fx_p_hit.png`：被动无所不用：第 3 下爆发（目标身上），5 帧

同一目标打中 3 下时的额外伤害：一圈淡蓝白色的哨兵之光猛地炸开（一个菱形 + 一个圆环叠在一起，像他那一族哨兵的纹章），中间一道金白色闪光（参考 SacGeo01、ShieldGeometry03、Glow01B、Shockwave）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sky-blue Sentinel light ramp (#FFFFFF, #E8FBFF, #B8ECF4, #7FD3E2, #3FA9BF, #1F6E86) and a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a SENTINEL BURST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 6 squares; 2 a pale sky-blue diamond outline 12 squares (1 square thick) round a ring 9 squares, a white core; 3 the diamond and the ring 16 squares, light rays at the diamond's 4 points; 4 the shapes thinner and 18 squares, breaking into sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `akshan_fx_q_hit.png`：Q 回旋镖划过（目标身上），4 帧

回旋镖划过目标：两道交叉的青铜金色弧形刀光（X 字，左右对称），中间白色，几颗火星（参考 Swirl02、Impact01）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12) and a bronze ramp (#FFF6E0, #F2C77A, #C98A3A, #8E5524, #5A3216, #2E180C).
Effect: a BOOMERANG SLASH on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 two gold crescent slashes crossing in an X (mirrored, 12 squares across, white edges, no outline); 3 the slashes thinner and wider, bronze sparks at mirrored places; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `akshan_fx_r_hit.png`：R 子弹命中（目标身上），4 帧

大招子弹打中：一团金红色的爆闪，中心白色，一圈红色的冲击环往外扩，几颗火星（参考 Shockwave、P_LensFlare、Glow02）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12) and a red ramp (#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08).
Effect: a HEAVY ROUND IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a red-gold burst 12 squares with a white core, a thin red shock ring round it; 3 the ring 18 squares (1 square thick), gold sparks at mirrored places; 4 the ring fading, a few sparks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `akshan_fx_q_catch.png`：Q 接住回旋镖（他手上，跟随），3 帧

回旋镖飞回到他手里的一下：胸前一道金白色的小闪光，一圈淡金色的小环（参考 Glow02、BA_LensFlare）。**左右对称**，画在他胸口高度（the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn，闪光在他脚底以上 24 格的位置）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: a CATCH GLINT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): 1 a white-gold 4-point star 6 squares, its middle 24 squares above the cell's bottom row; 2 a thin gold ring 10 squares round it; 3 fading.
Layout: one horizontal row of 3 equal 12:30 cells, image size 576x480 (each cell 192x480, 16 px a square); centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `akshan_fx_e_hook.png`：E 骄行荡寇：甩出的钩索（他身上，不跟随），5 帧

他朝天上甩出钩索：一根青铜色的绳子从他头顶笔直地射上去，顶上是一个金色的三叉抓钩，抓住时一闪；之后绳子绷直、轻轻抖动（参考 Rope、RopeB、Arrows）。**左右对称**（绳子在正中竖直），绳子下端在他头顶（the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn，绳子从他头顶 2 格往上画到格子顶）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, solid objects with a 1-square near-black outline and flat 3-4 step shading, light on them without an outline, colours only from a bronze ramp (#FFF6E0, #F2C77A, #C98A3A, #8E5524, #5A3216, #2E180C) and a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: A GRAPPLING HOOK SHOT STRAIGHT UP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): a bronze rope 2 squares thick (a twisted pattern, a 1-square dark outline) going straight up the middle from 2 squares above his head (42 squares above the cell's bottom row) to a gold three-pronged hook (8 squares across, outlined) at its top; 1 the rope half way up with the hook flying; 2 the rope at the top, the hook there; 3 a gold-white flash 10 squares round the hook as it bites; 4 the rope taut; 5 like 4, the rope shaking a square side to side (kept symmetric by shaking only its texture).
Layout: one horizontal row of 5 equal 24:70 cells, image size 1920x1120 (each cell 384x1120, 16 px a square); centered across, the rope's bottom 42 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `akshan_fx_w_camo.png`：W 赴险夺人：伪装（他身上，不跟随），5 帧

他被围住时伪装起来：身上泛起一层淡蓝白色的哨兵之光，几片像羽毛一样的光片从身上飘起、向两边散开，最后淡去（参考 W_feather、W_SmokeShape01、W_cloudRing_edge、W_glow_distort）。**左右对称**，围着身体画，中间身体位置的光要淡（the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sky-blue Sentinel light ramp (#FFFFFF, #E8FBFF, #B8ECF4, #7FD3E2, #3FA9BF, #1F6E86).
Effect: A CAMOUFLAGE SHIMMER round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): 1 a thin pale sky-blue outline glow hugging the figure's edge (1 square wide, no dark outline); 2 a faint shimmer ring at its feet (an ellipse 30 wide and 6 tall) and 6 small feather-like light flakes (2x4 squares) rising at both sides at mirrored places; 3 the flakes higher and spreading out; 4 the flakes fading, the glow thinner; 5 a few faint flakes.
Layout: one horizontal row of 5 equal 40:48 cells, image size 3200x768 (each cell 640x768, 16 px a square); centered across, the figure's feet 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `akshan_fx_r_lock.png`：R 恩怨相抵：锁定（他身上，不跟随），5 帧

他开大锁定目标的那一下：身边亮起一个金红色的瞄准纹章（一个大菱形套一个圆环，四个角上有小三角，像准星），由小变大、一闪后淡去（参考 SacGeo01、ShieldGeometry03、Counter、P_LensFlare）。**左右对称**，围着他的上半身画，中间身体位置留空（the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12) and a red ramp (#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08).
Effect: A TARGET-LOCK SIGIL round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): a red-gold reticle centred on his chest (24 squares above the cell's bottom row): a diamond outline round a ring, small triangles at the diamond's 4 points (lines 1 square thick, white cores, no dark outline), the middle 16 squares left empty; 1 the sigil 14 squares; 2 30 squares; 3 40 squares, brightest; 4 the same, thinner; 5 fading.
Layout: one horizontal row of 5 equal square cells, image size 3520x704 (each cell 704x704, 16 px a square); centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `akshan_fx_p_sh.png`：被动护盾（他身上，跟随，循环），4 帧

打中英雄后得到的护盾：一个淡蓝白色的半透明光罩（只画一圈边，边上有菱形的哨兵花纹），一闪一闪（参考 P_shield、ShieldGeometry03b、P_SheildMult）。**左右对称**，中间身体位置留空（the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn，光罩把他整个人罩住）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sky-blue Sentinel light ramp (#FFFFFF, #E8FBFF, #B8ECF4, #7FD3E2, #3FA9BF, #1F6E86).
Effect: A SHIELD BUBBLE round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): an oval outline 34 squares wide and 42 tall round the figure (1-2 squares thick, white highlights at the top, no dark outline), 4 small diamond marks on it at mirrored places; the inside left EMPTY; 1 dim, 2 brighter, 3 brightest, 4 like 2.
Layout: one horizontal row of 4 equal 40:46 cells, image size 2560x736 (each cell 640x736, 16 px a square); centered across, the figure's feet 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `akshan_fx_w_ms.png`：W 伪装加速（他脚下，跟随，循环），4 帧

伪装加速时脚下的风：一圈淡蓝色的风线贴着地面往后吹（两边对称的几道短风线），一帧一帧流动（参考 P_Speed_Pierce、Trail02、Trail03）。**左右对称**，只画在脚下（the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, shimmer or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sky-blue Sentinel light ramp (#FFFFFF, #E8FBFF, #B8ECF4, #7FD3E2, #3FA9BF, #1F6E86).
Effect: SPEED STREAKS at a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the gunslinger, 38 squares tall from his hair to his soles and about 30 wide, stands in the middle, not drawn): a faint pale sky-blue ellipse 30 wide and 6 tall on the ground, 3 short wind streaks on each side (mirrored, 4-6 squares long, 1 square thick, no outline) flowing outward a square each frame.
Layout: one horizontal row of 4 equal 36:10 cells, image size 2304x160 (each cell 576x160, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `akshan_fx_w_mark.png`：恶徒标记（敌人头顶，循环），4 帧

杀了阿克尚队友的敌人被标记成恶徒：头顶上方浮着一个红色的骷髅准星标记（一个小骷髅头套在菱形准星里），一闪一闪（参考 Counter、SacGeo02、Shuriman01）。**左右对称**，只画在头顶上方（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，标记在他头顶上面 2 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, solid objects with a 1-square near-black outline and flat 3-4 step shading, light on them without an outline, colours only from a red ramp (#FFFFFF, #FFD0C0, #FF7A5A, #E8341C, #A8160E, #600A08) and a gold light ramp (#FFFFFF, #FFF4C8, #FFD36A, #FFA62B, #E2681A, #9C3A12).
Effect: A SCOUNDREL MARK floating over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): a small red diamond reticle 10 squares wide and 10 tall (a white-red rim) with a little pale skull 5x5 squares inside (a 1-square dark outline on the skull), its bottom 2 squares above the champion's head (38 squares above the cell's bottom row); 1 dim, 2 brighter, 3 brightest (the rim flashing white), 4 like 2; nothing below it.
Layout: one horizontal row of 4 equal 14:48 cells, image size 896x768 (each cell 224x768, 16 px a square); centered across, the mark's bottom 38 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `akshan_fx_a_shot` | view_projectiles `league_akshan_a_shot`、`a_shot2`、`e_shot` | 10 × 4 |
| `akshan_fx_q_rang` | view_projectiles `league_akshan_q_out`、`q_back`（去和回同一张） | 12 |
| `akshan_fx_r_bullet` | view_projectiles `league_akshan_r_bullet` | 16 × 6 |
| `akshan_fx_a_hit` | view_effects `league_akshan_a_hit`、`e_hit`（跟随，画在人物上面；左右对称） | 10 |
| `akshan_fx_p_hit` | view_effects `league_akshan_p_hit`（跟随，画在人物上面；左右对称） | 18 |
| `akshan_fx_q_hit` | view_effects `league_akshan_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `akshan_fx_r_hit` | view_effects `league_akshan_r_hit`（跟随，画在人物上面；左右对称） | 18 |
| `akshan_fx_q_catch` | view_effects `league_akshan_q_catch`（跟随，画在人物上面；左右对称） | 12 |
| `akshan_fx_e_hook` | view_effects `league_akshan_e_hook`（不跟随，画在人物上面 z 2；左右对称；大图表） | 24 × 70 |
| `akshan_fx_w_camo` | view_effects `league_akshan_w_camo`（不跟随，画在人物上面 z 2；左右对称；大图表） | 40 × 48 |
| `akshan_fx_r_lock` | view_effects `league_akshan_r_lock`（不跟随，画在人物上面 z 2；左右对称；大图表） | 44 × 44 |
| `akshan_fx_p_sh` | view_buffs `league_akshan_p_sh`（跟随，画在人物上面；左右对称；循环） | 40 × 46 |
| `akshan_fx_w_ms` | view_buffs `league_akshan_w_ms`（跟随，画在人物下面 z -1；左右对称；循环） | 36 × 10 |
| `akshan_fx_w_mark` | view_buffs `league_akshan_w_mark`（跟随，画在人物上面；左右对称；循环；扩展包加在恶徒身上） | 14 × 48 |

- 两张表：`asset/league/effects/league_akshan_fx`（小的）和 `league_akshan_big`（e_hook、w_camo、r_lock），tag = 名字（build_akshan.py 的 views：`a_shot2` / `e_shot` 用 `a_shot`，`q_out` / `q_back` 用 `q_rang`，`e_hit` 用 `a_hit`；`w_mark` 由扩展包加在恶徒身上）。
- 用 `pixel_1x/` 切格（import_wukong_fx 的做法），断言非飞行物左右对称；清掉 Codex 给光描的最深色边（回旋镖、钩索、骷髅保留描边）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。
