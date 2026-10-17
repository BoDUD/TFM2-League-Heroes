# 狂野女猎手 奈德丽：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型和动作已定（`design/nidalee_idle.png`：人形 3/4 正面待机，标枪竖在远侧手里；美洲狮侧面朝右）。她在游戏里是**高清**的（每个游戏格子里 2.2×2.2 个细像素），人形连标枪 44 格高、27 格宽，美洲狮 30 格高、61 格长；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/nidalee_size.png`：两种形态的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/nidalee_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奈德丽自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**标枪和美洲狮的爪痕是暖金橙色的光（白芯）**，**捕猎的标记是白金色的箭镞**，**野性奔腾的治疗是绿色的光、绿叶和白色星光**，**扑跳的尘土是土黄色**；变身是**绿色和金色的灵光加绿叶**。
> - **特效要亮**：每道光、每片叶子都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光圈、冲击环只画外圈和两边，中间身体位置留空**（变身 `tf_cougar` / `tf_human` 例外：那一下就是要把她盖住）。
> - **方向（重要，红色方不会镜像）**：飞出去的标枪 `a_spear`、`q_spear` 画成朝右，**上下对称**（往左飞时会上下翻）。其余所有画面（打中、身上、脚下、头顶、地上的夹子、扑跳的尘土、挥击的爪痕）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）——所以爪痕一律竖直或两边同时扫开，不要画成往一个方向斜的。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nidalee_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `nidalee_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「寻觅」 | 人形投标枪 / 美洲狮爪击；标枪和夹子打中英雄就捕猎它，捕猎时加速 | `a_spear` · `a_hit` · `c_hit` · `hunted` · `hunt` · `brush`（附加包） |
| 技能 1 = Q「标枪投掷 / 推倒」 | 人形：全力投标枪，飞得越远越疼；美洲狮：下一击变成致命的扑咬 | `q_spear` · `q_hit` · `cq_arm` · `cq_hit` |
| 技能 2 = E「野性奔腾」+ W「丛林伏击」/ W「猛扑」+ E「挥击」 | 人形：治疗队友加攻速、丢夹子；美洲狮：扑过去、双爪横扫 | `e_heal` · `e_as` · `w_lob` · `w_trap` · `w_snap` · `cw_dust` · `cw_land` · `cw_hit` · `ce_swipe` · `ce_hit` |
| 变身（普攻时自动）+ 大招「美洲狮形态」猛扑猎杀 | 人和美洲狮来回切换；5 级大招扑向被捕猎或残血的英雄 | `tf_cougar` · `tf_human` · `r_roar` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火花、叶子、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（飞出去的两根标枪例外：木杆和石头枪头可以有一圈深色边）。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 暖金光（标枪、爪痕、标记）：`#FFFFFF`、`#FFF4C2`、`#FFD966`、`#F2A93B`、`#C9701E`、`#7A3E12`；
  - 绿叶光（治疗、变身）：`#FFFFFF`、`#E8FFD6`、`#A8F07A`、`#5CC84A`、`#2E8B3A`、`#145A2A`；
  - 尘土：`#F2E6CF`、`#D6C3A0`、`#B39B76`、`#8A7255`、`#5E4C39`；
  - 木头枪杆（只用于标枪）：`#E9C79A`、`#C58C4E`、`#9A5E2C`、`#6B3A1A`、`#3A1E0E`；
  - 石头枪头（只用于标枪）：`#FFFFFF`、`#E4E6EE`、`#B9BCC9`、`#8C8FA0`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人或豹子**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：人形普攻距离 50000，标枪射程 85000，夹子半径 7000，猛扑落地半径 13000，挥击半径 20000）。

### 1. `nidalee_fx_a_spear.png`：普攻：投出去的小标枪（朝目标飞，循环），2 帧

她普攻投出去的标枪：木头枪杆、浅灰白石头枪头朝右，后面一道短短的白金色风痕。**上下对称**（不画羽毛）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#E9C79A, #C58C4E, #9A5E2C, #6B3A1A, #3A1E0E) and a stone ramp (#FFFFFF, #E4E6EE, #B9BCC9, #8C8FA0) and a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a THROWN JAVELIN flying to the RIGHT, 2 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a straight wooden shaft 11 squares long and 1 square thick ending in a pale stone blade 4 squares long pointing right (white tip); 3-4 squares of a pale gold speed streak behind the shaft's end, flickering between the two frames.
Layout: one horizontal row of 2 equal 18:6 cells, image size 576x96 (each cell 288x96, 16 px a square); the blade's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nidalee_fx_q_spear.png`：Q 标枪投掷：发光的大标枪（朝目标飞，循环），4 帧

全力投出的标枪：枪身裹着一层金色的光，枪头白亮，后面拖一条渐细的金色光尾和几点火星（参考 SpearGlow、Q_TrailShadow、Q_Mote）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wood ramp (#E9C79A, #C58C4E, #9A5E2C, #6B3A1A, #3A1E0E) and a stone ramp (#FFFFFF, #E4E6EE, #B9BCC9, #8C8FA0) and a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a GLOWING JAVELIN flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a straight shaft 14 squares long with a stone blade 5 squares long pointing right, the whole javelin wrapped in a warm gold glow 3 squares thick with a white core along the shaft; a tapering gold light trail 8 squares long behind it; 2-3 gold motes at mirrored places flickering in turn.
Layout: one horizontal row of 4 equal 26:10 cells, image size 1664x160 (each cell 416x160, 16 px a square); the blade's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nidalee_fx_a_hit.png`：普攻打中（目标身上），4 帧

标枪打中：一个小小的白金色星形闪光，几道短短的光线往外散（参考 BA_hit01）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a SMALL SPEAR-HIT FLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a four-point gold star 8 squares across with a white core; 3 the star 10 squares, thin rays outward; 4 a few fading gold sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nidalee_fx_q_hit.png`：Q 标枪打中（目标身上），5 帧

标枪全力命中：一团金色的冲击光炸开（白芯），一圈尖尖的光刺往外射，几片金色火花溅出。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a JAVELIN IMPACT BURST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a gold burst 12 squares across with a white core and 8 sharp rays; 3 the burst 20 squares across, the rays longest; 4 the burst breaking into gold sparks at mirrored places; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nidalee_fx_hunted.png`：被动 寻觅：被捕猎的标记（被捕猎的英雄头顶，循环），4 帧

被标枪或夹子打中的英雄头顶出现猎人的标记：一个白金色的箭头印记（尖头朝下的箭镞，两边一对弯钩，参考 Q_Mark），一闪一闪。**左右对称**。画在格子上部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a HUNTER'S MARK over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an arrowhead sigil 8 squares wide and 10 tall pointing DOWN - a white core outline, gold inside, two curved barbs at its sides - pulsing brighter and dimmer.
Layout: one horizontal row of 4 equal 12:48 cells, image size 768x768 (each cell 192x768, 16 px a square); the sigil's middle 7 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nidalee_fx_hunt.png`：被动 寻觅：她在捕猎时的加速（她脚下，循环），4 帧

捕猎中移速加成：她脚下一圈淡淡的金色风痕（扁椭圆，几道短短的速度线和光点轮流闪，参考 P_speedlines）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a GOLD SPEED RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ellipse 18 squares wide and 5 tall in pale gold, 4 short speed streaks and 2 white motes on it at mirrored places taking turns to light up.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nidalee_fx_e_heal.png`：E 野性奔腾：治疗（被治疗的队友身上），6 帧

治疗：队友身上一阵绿色的光从脚下往上升，几片绿叶和白色的星光闪闪往上飘（参考 Leaves、Soraka_Heal_Sparkle、heal_shapes）。**左右对称**，中间人形位置留空（只画两边和上面）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A).
Effect: a HEALING SURGE round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 10 squares wide and 22 tall): 1 a green glow on the ground 12 squares wide; 2 green light rising at both sides 20 squares tall, 2 leaves; 3 the light at full height, 4 leaves and 4 white star sparkles at mirrored places; 4 the leaves higher, a green ring over the head; 5 the light fading, sparkles at the top; 6 a few last sparkles.
Layout: one horizontal row of 6 equal 22:30 cells, image size 2112x480 (each cell 352x480, 16 px a square); centered across, the glow's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nidalee_fx_e_as.png`：E 攻速加成（队友脚下，循环），4 帧

攻速加成的几秒：脚下一圈绿色的旋风（扁椭圆，几片小叶子绕着转，靠亮暗交替表现转动）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A).
Effect: a LEAFY GREEN SWIRL under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat green ellipse 16 squares wide and 5 tall, 4 small leaves on it at mirrored places, the pairs taking turns to flash bright.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nidalee_fx_w_lob.png`：W 丛林伏击：丢出去的夹子（抛物线飞，循环），2 帧

抛向敌人的夹子：一个合拢的小兽夹（深色铁齿、绿色藤蔓缠着，参考 W_15），两帧轻轻闪。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A) and an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39).
Effect: a SMALL CLOSED SNARE in the air, 2 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a round closed jaw trap 7 squares wide and 5 tall, dark iron teeth, green vines wound round it, a green glint at the top that flickers.
Layout: one horizontal row of 2 equal 10:8 cells, image size 320x128 (each cell 160x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nidalee_fx_w_trap.png`：W 夹子落地（地上，约 4 秒），8 帧

埋在地上的夹子：地上一圈张开的兽夹（尖齿朝内，从斜上方看的扁椭圆），外面一圈淡淡的绿色光圈（参考 W_Underglow、W_circle）。第 1–2 帧张开，第 3–6 帧光圈慢慢闪（第 4 帧会停很久，夹子在地上约 4 秒），最后两帧暗下去消失。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A) and an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39).
Effect: an OPEN SNARE on the ground seen from above at an angle, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse 14 squares wide and 6 tall of earthy jaws with pale teeth pointing inward, a faint green glow ring 18 x 8 round it; 1 the jaws closed small; 2 the jaws open; 3 the glow ring brightest; 4 the trap steady (this frame is held for seconds); 5 the same, the ring dimmer; 6 the ring brighter again; 7 the ring fading; 8 only the dim jaws.
Layout: one horizontal row of 8 equal 20:10 cells, image size 2560x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nidalee_fx_w_snap.png`：W 夹子夹住（踩中的人身上），5 帧

夹子咬合：脚下一对兽夹的齿啪地合上（上下两排尖齿），一团绿色和金色的火花往上溅。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A), a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12) and an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39).
Effect: a SNARE SNAPPING SHUT at a figure's feet, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of pale teeth 14 squares wide, open; 2 the teeth closing, a white flash between them; 3 shut, green and gold sparks bursting upward 16 squares; 4 the sparks higher at mirrored places; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered across, the teeth 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `nidalee_fx_c_hit.png`：美洲狮普攻打中（目标身上），4 帧

爪击打中：三道竖着的金橙色爪痕一闪（中间长、两边短，参考 BA_Swipe、Claws），几点火星。**左右对称**（爪痕竖直，不要斜）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: CLAW MARKS on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 three VERTICAL gold claw streaks, the middle one 10 squares tall, the side ones 7, white cores; 3 the streaks full, a few sparks at mirrored places; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `nidalee_fx_cq_arm.png`：推倒：准备好下一击（她身上），4 帧

美洲狮准备推倒：她身上一圈金色的光一闪而过，上方三道小小的金色爪痕亮起又消失（提示下一击）。**左右对称**，中间身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a GOLD READY FLASH over a crouching beast, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 18 squares wide and 9 tall at the bottom): 1 a faint gold rim round the empty area; 2 the rim bright, 3 small vertical claw marks above it; 3 the marks brightest; 4 fading.
Layout: one horizontal row of 4 equal 26:16 cells, image size 1664x256 (each cell 416x256, 16 px a square); centered across, the empty area's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `nidalee_fx_cq_hit.png`：推倒打中（目标身上），5 帧

推倒的致命一击：一个大大的金橙色撕咬冲击（上下两排利齿形状的光一合，中间白光炸开），几道爪痕和火花往外溅。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a FATAL BITE BURST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an upper and a lower row of sharp gold fang-shaped light, open, 16 squares wide; 2 the rows snapping together, a white flash between; 3 a gold burst 20 squares across with a white core; 4 three vertical claw streaks and sparks at mirrored places; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `nidalee_fx_cw_dust.png`：猛扑：起跳的尘土（她脚下，跟着她），4 帧

起跳的一瞬间：脚下一圈被蹬起的尘土往两边飞溅（扁椭圆的土雾，几块小土块往上弹，参考 Dust01）。**左右对称**（不要画成往一个方向拖的尾巴：红色方不会镜像）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39).
Effect: a DUST KICK-UP under a leaping beast's paws, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat dust puff 12 squares wide and 4 tall; 2 the puff 24 squares wide, small clods flying up and outward at mirrored places; 3 the puff 30 squares wide and thin, the clods higher; 4 fading dust.
Layout: one horizontal row of 4 equal 32:12 cells, image size 2048x192 (each cell 512x192, 16 px a square); centered across, the puff's middle 3 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `nidalee_fx_cw_land.png`：猛扑：落地（地上，不跟随），5 帧

落地的一下：地上一圈尘土冲击环往外扩（扁椭圆，浅色边），中间几道金色的裂光一闪。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39) and a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a LANDING SHOCK on the ground, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash on the ground 8 squares wide; 2 a flat dust ring 16 squares wide and 5 tall with a pale rim, 4 short gold cracks inside at mirrored places; 3 the ring 30 x 10, dust clods flying up; 4 the ring breaking into dust; 5 fading dust.
Layout: one horizontal row of 5 equal 34:14 cells, image size 2720x224 (each cell 544x224, 16 px a square); centered across, the ring's middle 4 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `nidalee_fx_cw_hit.png`：猛扑打中（目标身上），4 帧

被扑中：一团金橙色的冲击光（白芯），几块尘土溅开。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12) and an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39).
Effect: a POUNCE IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a gold burst 10 squares across with a white core; 3 the burst 14 squares, dust clods at mirrored places; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `nidalee_fx_ce_swipe.png`：挥击：双爪横扫（她身上），5 帧

挥击：她周围划开一圈金橙色的爪痕光弧（三道并排的弯弧，从中间往两边同时扫开，像一个扁扁的爪痕圆环，参考 E_Swipe、Claws_02）。**左右对称**（两边同时扫，红色方不会镜像）；中间身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a RING OF CLAW SWEEPS round a crouching beast, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 30 squares wide and 14 tall at the bottom): 1 three short parallel gold arcs starting at the top middle; 2 the three arcs sweeping outward to both sides along a flat ellipse 44 squares wide and 20 tall, white cores; 3 the arcs reaching both sides, brightest; 4 the arcs thinning; 5 a few fading gold streaks.
Layout: one horizontal row of 5 equal 46:24 cells, image size 3680x384 (each cell 736x384, 16 px a square); centered across, the ellipse's bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `nidalee_fx_ce_hit.png`：挥击打中（目标身上），3 帧

挥击打中：一个金色的小十字爪痕一闪。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a SMALL CLAW CROSS on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 an X of two gold claw streaks 10 squares across with a white core and a vertical streak through it; 3 fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `nidalee_fx_tf_cougar.png`：变成美洲狮（她身上），6 帧

人变豹：一团绿金色的灵光把她整个包住（这一下要盖住她：人形最后一帧正好变成豹子），绿叶和光丝绕着转一圈，然后往外散开（参考 Leaves、WispLayerTrail、Glow、transformGlow）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A) and a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a SPIRIT TRANSFORMATION BURST covering a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 green wisps rising at both sides 30 squares tall; 2 the wisps closing over the middle, a gold glow inside, 6 leaves at mirrored places; 3 a solid bright cloud of green and gold light 36 squares wide and 40 tall with a white core (covering everything in the middle); 4 the cloud bursting outward, leaves flying; 5 thin rings of light and leaves farther out; 6 a few fading leaves and sparkles.
Layout: one horizontal row of 6 equal 42:46 cells, image size 4032x736 (each cell 672x736, 16 px a square); centered across, the cloud's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `nidalee_fx_tf_human.png`：变回人形（她身上），6 帧

豹变人：同样的绿金色灵光，但形状是横着的（包住美洲狮），最后往上收成一束光（人站起来）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A) and a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a SPIRIT TRANSFORMATION BURST covering a beast, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 green wisps low at both sides 40 squares wide; 2 the wisps closing, a gold glow, 6 leaves at mirrored places; 3 a solid bright cloud of green and gold light 46 squares wide and 30 tall with a white core; 4 the cloud drawing up into a tall column of light 20 squares wide and 34 tall; 5 the column thinning, leaves falling; 6 fading sparkles.
Layout: one horizontal row of 6 equal 52:38 cells, image size 4992x608 (each cell 832x608, 16 px a square); centered across, the cloud's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `nidalee_fx_r_roar.png`：大招 猛扑猎杀：发动（她身上），5 帧

猎杀扑击发动：她周围一圈金色的冲击波（咆哮的声波环，扁椭圆，两三层），几道速度线往外射。**左右对称**，中间身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12).
Effect: a ROAR SHOCKWAVE round a beast, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 28 squares wide and 14 tall at the bottom): 1 a gold ring rim 30 squares wide; 2 two concentric gold rings 36 squares wide and 20 tall, white inner edges; 3 three rings, the outer 40 x 24, 6 short speed lines outward at mirrored places; 4 the rings thinning; 5 fading.
Layout: one horizontal row of 5 equal 42:26 cells, image size 3360x416 (each cell 672x416, 16 px a square); centered across, the rings' bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `nidalee_fx_r_hit.png`：大招 猛扑猎杀：扑中（目标身上），5 帧

猎杀扑中：一团大大的金橙色冲击（白芯），一圈尖尖的爪痕光往外射，地上溅起尘土。**左右对称**。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold ramp (#FFFFFF, #FFF4C2, #FFD966, #F2A93B, #C9701E, #7A3E12) and an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39).
Effect: a HUNT POUNCE IMPACT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares; 2 a gold burst 16 squares across with a white core; 3 the burst 22 squares, 6 sharp claw-streak rays at mirrored places; 4 the rays breaking into sparks, dust at the bottom; 5 fading.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `nidalee_fx_brush.png`：附加包 草丛加速（她脚下，循环），4 帧

在草丛里和刚出草丛时的移速加成：脚下几片小绿叶绕着转（比 E 的攻速圈小一点、淡一点）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, leaves, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #E8FFD6, #A8F07A, #5CC84A, #2E8B3A, #145A2A).
Effect: LEAVES under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a faint flat green ellipse 14 squares wide and 4 tall, 3 small leaves on it at mirrored places taking turns to brighten.
Layout: one horizontal row of 4 equal 16:7 cells, image size 1024x112 (each cell 256x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nidalee_fx_a_spear` | view_projectiles `league_nidalee_a_spear`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 4 |
| `nidalee_fx_q_spear` | view_projectiles `league_nidalee_q_spear`（朝飞行方向转，画成朝右飞；上下对称） | 24 × 8 |
| `nidalee_fx_a_hit` | view_effects `league_nidalee_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `nidalee_fx_q_hit` | view_effects `league_nidalee_q_hit`（跟随，画在人物上面；左右对称） | 20 |
| `nidalee_fx_hunted` | view_buffs `league_nidalee_hunted`（跟随，画在人物上面；左右对称） | 10 × 12 |
| `nidalee_fx_hunt` | view_buffs `league_nidalee_hunt`（跟随，画在人物下面；左右对称） | 18 × 6 |
| `nidalee_fx_e_heal` | view_effects `league_nidalee_e_heal`（跟随，画在人物上面；左右对称） | 20 × 28 |
| `nidalee_fx_e_as` | view_buffs `league_nidalee_e_as`（跟随，画在人物下面；左右对称） | 16 × 6 |
| `nidalee_fx_w_lob` | view_projectiles `league_nidalee_w_lob`（抛物线；左右对称） | 8 × 6 |
| `nidalee_fx_w_trap` | view_effects `league_nidalee_w_trap`（不跟随，画在地上；左右对称） | 18 × 8 |
| `nidalee_fx_w_snap` | view_effects `league_nidalee_w_snap`（跟随，画在人物上面；左右对称） | 16 |
| `nidalee_fx_c_hit` | view_effects `league_nidalee_c_hit`（跟随，画在人物上面；左右对称） | 12 |
| `nidalee_fx_cq_arm` | view_effects `league_nidalee_cq_arm`（跟随，画在人物上面；左右对称） | 24 × 14 |
| `nidalee_fx_cq_hit` | view_effects `league_nidalee_cq_hit`（跟随，画在人物上面；左右对称） | 20 |
| `nidalee_fx_cw_dust` | view_effects `league_nidalee_cw_dust`（跟随，画在人物下面；左右对称） | 30 × 10 |
| `nidalee_fx_cw_land` | view_effects `league_nidalee_cw_land`（不跟随，画在地上；左右对称） | 32 × 12 |
| `nidalee_fx_cw_hit` | view_effects `league_nidalee_cw_hit`（跟随，画在人物上面；左右对称） | 14 |
| `nidalee_fx_ce_swipe` | view_effects `league_nidalee_ce_swipe`（跟随，画在人物上面；左右对称） | 44 × 22 |
| `nidalee_fx_ce_hit` | view_effects `league_nidalee_ce_hit`（跟随，画在人物上面；左右对称） | 12 |
| `nidalee_fx_tf_cougar` | view_effects `league_nidalee_tf_cougar`（跟随，画在人物上面；左右对称） | 40 × 44 |
| `nidalee_fx_tf_human` | view_effects `league_nidalee_tf_human`（跟随，画在人物上面；左右对称） | 50 × 36 |
| `nidalee_fx_r_roar` | view_effects `league_nidalee_r_roar`（跟随，画在人物上面；左右对称） | 40 × 24 |
| `nidalee_fx_r_hit` | view_effects `league_nidalee_r_hit`（跟随，画在人物上面；左右对称） | 22 |
| `nidalee_fx_brush` | view_buffs `league_nidalee_brush`（附加包的副本才用；跟随，画在人物下面；左右对称） | 14 × 5 |

- 两张表：`asset/league/effects/league_nidalee_fx`（小的）和 `league_nidalee_big`（cw_land、ce_swipe、tf_cougar、tf_human、r_roar），tag = 名字（build_nidalee.py 的 views）。
- `a_spear`、`q_spear` 是飞行投射物，画面朝飞行方向转；`w_trap`、`cw_land` 不跟随；`e_as`、`hunt`、`brush` 脚下 buff（z -1）；`hunted` 头顶（z 3）；`w_trap` 第 4 帧拉长到夹子的 4 秒（w_life 240 tick）。
- 用 `pixel_1x/` 切格（import_kassadin / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
