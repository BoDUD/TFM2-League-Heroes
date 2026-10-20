# 愁云使者 薇古丝：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型和动作已定（`design/vex_idle.png`：3/4 正面朝右的 Q 版约德尔小女孩，深青黑色的连帽衫、兜帽上两只尖耳朵，青绿色头发、灰白皮肤、品红色的眼睛，长到小腿的袖子、品红紫灯笼裤）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），28 格高、24 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/vex_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/vex_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里薇古丝自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的魔法是薄荷青绿色的光**（暮气的眼睛符印、暗影弹、寒心波云的前缘），**她的影子是墨一样的靛紫色**，带两只尖耳朵和两只浅蓝白的**螺旋眼**。
> - **影子只出现在特效里**（用户把她身后的影子从人物上拿掉了）：E 影子从她身上飞走、扑到目标点；W 影子护住她；R 影子的头就是飞弹；终焉好了时她头上睁开一对影子的眼睛。
> - **特效要亮**：每团光都要有白色或最亮一档的芯；深色的影子要有靛紫 / 淡紫的亮边，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、头上、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（暗影弹、风波、影子飞弹）**朝右飞、尾巴在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `vex_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/vex_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/vex_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（W「生人勿近」和被动「终焉暮气」在里面） | 甩出暗影弹；敌方英雄靠近时改成护盾 + 身边炸开冲击波；每隔一段时间下一个技能附带恐惧；暮气标记被她引爆 | `a_bolt` · `a_hit` · `w_ring` · `w_shield` · `w_hit` · `g_mark` · `g_pop` · `p_ready` |
| 技能 1 = Q「寒心波云」 | 一道暗风波穿过一条线上的所有敌人 | `q_bolt` · `q_hit` |
| 技能 2 = E「溟濛渐染」 | 影子飞到目标点扩散：伤害、减速、施加暮气 | `e_cast` · `e_land` · `e_slow` · `g_mark` |
| 大招「愁煞」 | 扔出影子飞弹标记英雄，然后冲过去一击，落地放生人勿近 | `r_missile` · `r_mark` · `r_hit` · `w_ring` · `w_shield` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、暗雾、烟、光环、冲击波和影子都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 薄荷青绿色的光：`#FFFFFF`、`#D6FFF2`、`#8CF5D6`、`#3EDDB4`、`#1E9C8A`、`#0E5A5A`；
  - 墨一样的靛紫色影子：`#E8E4FF`、`#A98CFF`、`#7A3CFF`、`#4A1E9E`、`#261055`、`#120830`；
  - 影子的螺旋眼：`#FFFFFF`、`#CFF7FC`、`#8EC8FF`；
- 打中、爆发居中画，不旋转；地面上的圆（冲击环、暗影地面、减速的雾）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，冲击波半径 40000，影子落地的范围半径 22000）。

### 1. `vex_fx_a_bolt.png`：普攻：暗影弹（弹道，循环），4 帧

她普攻甩出去的一小团暗影弹：薄荷青绿色的亮芯，外面裹一层靛紫色的雾，后面拖一小段青绿色的尾迹（参考 ba_streak、ba_glowtrail、ba_tar）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A) and an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830).
Effect: A SMALL GLOOM BOLT, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round mint-white core 4 squares across inside a 6-square indigo-violet mist at the right, a short tapering mint trail 5 squares long behind it to the left; each frame the mist wavers and the trail flickers (symmetric top and bottom).
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); the core's middle on the cell's middle row, 3 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `vex_fx_a_hit.png`：普攻：打中目标，3 帧

暗影弹打中目标：一团青绿色的小闪光，几缕靛紫色的雾散开（参考 hitflash、vex_hiteffect_magic_s_02_star）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A) and an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830).
Effect: A SMALL GLOOM HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a mint-white four-pointed flash 6 squares across; 2 the flash 9 across with 4 indigo-violet mist puffs at mirrored places; 3 only the puffs further out, fading.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `vex_fx_q_bolt.png`：Q 寒心波云：一道暗风波（弹道，循环），4 帧

她推出去的寒心波云：一道往右鼓起的弧形风波，像一弯竖着的月牙（弧顶朝右），弧的前缘是亮的薄荷青绿色，后面是翻滚的靛紫色暗雾，里面隐约一只青绿色的眼睛符印（参考 q_wave、q_missileeye、q_spawntrails）。**朝右飞，弧顶在右边，上下严格对称**，4 帧循环。它穿过一条线上的所有敌人，所以要宽（约 16 格高）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A) and an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830).
Effect: A CRESCENT GUST OF GLOOM, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): an upright crescent wave 16 squares tall bulging to the RIGHT, its leading edge 2 squares of bright mint-white, behind it 5 squares of churning indigo-violet mist that frays into wisps to the left; a small mint eye sigil (an almond eye with a dot) in its middle; each frame the mist churns and the edge shimmers (symmetric top and bottom).
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); the crescent's middle on the cell's middle row, its edge 2 squares from the cell's right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `vex_fx_q_hit.png`：Q：风波打中目标，4 帧

风波打中目标：一团青绿色的闪光，靛紫色的暗雾往两边卷开（参考 q_tar_erode、q_tar_trail_smoke）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A) and an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830).
Effect: A GUST IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a mint-white flash 7 squares across; 2 the flash 11 across, indigo-violet mist curling out to both sides; 3 the mist 16 across, thinning, the flash gone; 4 only faint wisps at the edges.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `vex_fx_w_ring.png`：W 生人勿近：她身边炸开的冲击环（地上，跟随），5 帧

她身边炸开的冲击波：贴着地面的一圈椭圆冲击环往外扩，环是薄荷青绿色的亮线带着靛紫色的暗雾，环上有四个对称的小漩涡花纹（参考 w_ring_normal、w_shockwave、w_smokering_dissolve、w_praxis）。**只画在地面上（她站在中间，不画人）**，**左右对称**，5 帧。范围约 80 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A) and an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830).
Effect: A SHOCK RING bursting out along the ground round her, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small girl stands in the middle, not drawn: 28 squares from her ear tips to the ground, about 24 squares wide): 1 a small bright mint ring (an ellipse 20 wide and 7 tall); 2 the ring 44 wide and 15 tall, 2 squares thick, mint-white with an indigo-violet mist band just inside it; 3 the ring 66 wide and 22 tall, four small mint curl ornaments on it at mirrored places; 4 the ring 80 wide and 27 tall, thinning, the mist fraying; 5 only a faint broken ring and wisps.
Layout: one horizontal row of 5 equal 84:30 cells, image size 6720x480 (each cell 1344x480, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `vex_fx_w_shield.png`：W：影子护住她（她身上，跟随），5 帧

护盾的一下：她的影子从地面升起、张开两只大爪子把她围住，然后化成一圈靛紫色的暗影罩，罩的边是青绿色的亮线（参考 w_shield_shadow、shield_01、w_shieldmask）。**她站在中间不画人**，只画外圈：影子的两只手在她两侧、头（两只尖耳朵、两只螺旋眼）在她头顶上方；**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830), the pale eye colours (#FFFFFF, #CFF7FC, #8EC8FF) and a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: THE SHADOW WRAPPING A GIRL IN A SHIELD, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small girl stands in the middle, not drawn: 28 squares from her ear tips to the ground, about 24 squares wide, her body area left EMPTY): 1 dark indigo-violet mist rising from the ground at both sides of her; 2 two big shadow hands with long claws rising at her left and right, a shadow head with two pointed ears over her head, each eye a little pale blue-white open spiral (a clear @ shape about 4 squares across) - the Shadow's drawn eyes; 3 the hands curling round her, the head looking down; 4 the shadow melting into a dome-shaped shield outline round her, 32 wide and 40 tall, its rim 2 squares of mint-white light over indigo mist; 5 only the dome's rim, thinner, fading.
Layout: one horizontal row of 5 equal 34:42 cells, image size 2720x672 (each cell 544x672, 16 px a square); centered across, the bottom of the mist on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `vex_fx_w_hit.png`：W：冲击波打中，3 帧

冲击波打到身边的敌人：一团青绿色的小闪光和一缕暗雾（参考 tar_flashglow）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A) and an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830).
Effect: A SMALL SHOCK HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a mint-white flash 6 across; 2 a mint ring 10 across with indigo mist inside it; 3 only a faint ring and wisps.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `vex_fx_e_cast.png`：E 溟濛渐染：影子从她身上飞出去（她身上，跟随），5 帧

放 E 的一下：她的影子从她背后升起、往上一跃飞走（飞去落点的那段由落地的画面接上）：靛紫色的影子身形带两只尖耳朵和两只螺旋眼，往上拉长成一缕烟冲出画面顶上（参考 r_shadow、e_missile、vertical_wisp）。**她站在下半部不画人**，影子在她头顶，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830), the pale eye colours (#FFFFFF, #CFF7FC, #8EC8FF) and a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: A SHADOW LEAPING UP AND AWAY, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small girl stands in the middle, not drawn: 28 squares from her ear tips to the ground, about 24 squares wide, her body in the lower part left EMPTY): 1 dark indigo-violet mist gathering over her head; 2 a shadow creature 18 squares wide rising over her head - a round head with two tall pointed ears, each eye a little pale blue-white open spiral (a clear @ shape about 4 squares across) - the Shadow's drawn eyes, a body narrowing to a wisp down to her; 3 the creature 4 squares higher, stretched taller, a mint glow round its eyes; 4 it shooting up to the cell's top, a long indigo wisp trailing; 5 only the wisp's end at the top, fading.
Layout: one horizontal row of 5 equal 26:44 cells, image size 2080x704 (each cell 416x704, 16 px a square); centered across, the mist's bottom 20 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `vex_fx_e_land.png`：E：影子落在目标点扩散（地上，不跟随），6 帧

影子从天上扑下来落在目标点：靛紫色的影子身形（尖耳朵、螺旋眼、张开的大爪子）往下扑，撞地后化成一大片靛紫色的暗影地面，外圈一道青绿色的符文环，然后散成雾（参考 e_decal、e_runedecal、e_ring_01、e_groundlight_01、e_eyesigil）。**左右对称**，6 帧。范围约 44 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830), the pale eye colours (#FFFFFF, #CFF7FC, #8EC8FF) and a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: A SHADOW CRASHING DOWN AND SPREADING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a shadow creature 20 squares wide diving down from the top - a round head with two pointed ears, each eye a little pale blue-white open spiral (a clear @ shape about 4 squares across) - the Shadow's drawn eyes, two clawed hands spread to the sides; 2 it hitting the ground at the bottom middle, splashing; 3 a flat dark indigo-violet pool on the ground (an ellipse 40 wide and 13 tall) with a 1-square mint rune ring round its edge and a small mint eye sigil in its middle; 4 the pool 44 wide, indigo mist rising from it in 6 wisps at mirrored places; 5 the pool fading, the wisps higher; 6 only thin wisps and a broken ring.
Layout: one horizontal row of 6 equal 48:44 cells, image size 4608x704 (each cell 768x704, 16 px a square); centered across, the pool's middle 7 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `vex_fx_e_slow.png`：E：被减速（敌人脚下，循环），4 帧

减速的 2 秒：敌人脚下一小滩靛紫色的暗雾，几缕暗烟往上冒（参考 noisemist、mist_noise）。**只画在脚下的地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830).
Effect: GLOOMY MIST at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat indigo-violet mist ellipse 20 wide and 4 tall, 3 short dark wisps (2-3 squares) rising from it at mirrored places; each frame the wisps rise a square and new ones start.
Layout: one horizontal row of 4 equal 22:6 cells, image size 1408x96 (each cell 352x96, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `vex_fx_g_mark.png`：被动：暮气（敌人头上，循环），4 帧

暮气的标记：敌人头上飘着一个薄荷青绿色的眼睛符印（杏仁形的眼睛、中间一个点，上面三道火苗似的尖），一闪一闪（参考 p_gloomdebuff、e_eyesigil）。**画在头上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: A GLOOM EYE SIGIL over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a mint almond-shaped eye 10 squares wide and 5 tall with a white dot pupil, three short flame-like points above it and two below; each frame it pulses (its glow 1 square wider on frames 2 and 3) and bobs a square.
Layout: one horizontal row of 4 equal 12:10 cells, image size 768x160 (each cell 192x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `vex_fx_g_pop.png`：被动：暮气被引爆（他身上），4 帧

暮气被她引爆：青绿色的眼睛符印猛地睁大、炸成一团青绿色的十字星闪光，碎片四散（参考 vex_hiteffect_magic_s_02_star、tar_flashglow、p_castcrackswipe）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: A GLOOM DETONATION, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a mint eye sigil 10 wide opening wide; 2 it bursting into a mint-white four-pointed star flash 14 across; 3 the flash 18 across with 8 mint shards flying out; 4 only fading shards at the edge.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `vex_fx_p_ready.png`：被动：终焉好了（她头上），4 帧

终焉充好的一下：她头上方一对影子的螺旋眼睁开、亮一下，旁边两只小尖耳朵的影子轮廓，然后消散（参考 r_r1_eyes、r_target_ears）。**画在她头顶上方（不画人）**，**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830), the pale eye colours (#FFFFFF, #CFF7FC, #8EC8FF) and a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: TWO SHADOW EYES OPENING over a head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin dark indigo mist band 12 wide; 2 two eyes opening in it, each eye a little pale blue-white open spiral (a clear @ shape about 4 squares across) - the Shadow's drawn eyes, with two small pointed shadow ears above them; 3 the eyes flashing mint-white; 4 only fading mist.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `vex_fx_r_missile.png`：R 愁煞：影子飞弹（弹道，循环），4 帧

她扔出去的愁煞：影子的头化成一颗彗星——靛紫色的头上两只尖耳朵朝后、两只螺旋眼朝前，后面拖一条长长的靛紫色暗影尾巴，尾巴边上闪着青绿色的光（参考 r_missile_v2、r_head_01、r_comet_flipped、r_galaxysphere_streaks）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830), the pale eye colours (#FFFFFF, #CFF7FC, #8EC8FF) and a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: A SHADOW-HEAD COMET, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the right a round indigo-violet shadow head 9 squares across with two pointed ears swept back (one at the top, one mirrored at the bottom) and two eyes side by side facing forward, each eye a little pale blue-white open spiral (a clear @ shape about 4 squares across) - the Shadow's drawn eyes; behind it to the left a long tapering indigo-violet shadow tail 13 squares long with mint-white sparks along its edges; each frame the tail ripples (symmetric top and bottom) and the sparks move.
Layout: one horizontal row of 4 equal 24:14 cells, image size 1536x224 (each cell 384x224, 16 px a square); the head's middle on the cell's middle row, 5 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `vex_fx_r_mark.png`：R：被标记（敌人头上，循环），4 帧

被愁煞的飞弹打中、她马上冲过来：敌人头上一对影子的眼睛和两只尖耳朵的暗影轮廓盯着他（参考 r_target_ears、r_r1_eyes）。**画在头上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830) and the pale eye colours (#FFFFFF, #CFF7FC, #8EC8FF).
Effect: A SHADOW WATCHING from over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small indigo-violet shadow face 14 wide and 8 tall - two pointed ears and two eyes, each eye a little pale blue-white open spiral (a clear @ shape about 4 squares across) - the Shadow's drawn eyes; each frame it bobs a square and the eyes' spirals turn.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `vex_fx_r_hit.png`：R：冲过去的一击（他身上），4 帧

她冲到目标身边的一击：一团大大的靛紫色暗影炸开，中间青绿白色的闪光，外圈一道青绿色的冲击环，影子的爪痕往四周撕开（参考 r_tar_impact、r_flash、r_land_glow）。**左右对称**，比普通打中大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, mist, smoke, rings, shockwaves or the shadow creature, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ink indigo-violet shadow ramp (#E8E4FF, #A98CFF, #7A3CFF, #4A1E9E, #261055, #120830) and a mint-teal glow ramp (#FFFFFF, #D6FFF2, #8CF5D6, #3EDDB4, #1E9C8A, #0E5A5A).
Effect: A BIG SHADOW STRIKE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a mint-white flash 10 squares across; 2 an indigo-violet shadow burst 18 across round it with 4 claw-mark streaks tearing out at mirrored diagonals; 3 a mint ring 24 across, the burst fading; 4 only the ring's broken arcs and wisps.
Layout: one horizontal row of 4 equal square cells, image size 1664x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `vex_fx_a_bolt` | view_projectiles `league_vex_a_bolt`（跟着弹道转向；上下对称） | 12 × 8 |
| `vex_fx_a_hit` | view_effects `league_vex_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `vex_fx_q_bolt` | view_projectiles `league_vex_q_bolt`（跟着弹道转向；上下对称） | 18 × 18 |
| `vex_fx_q_hit` | view_effects `league_vex_q_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `vex_fx_w_ring` | view_effects `league_vex_w_ring`（跟随她，画在人物下面 z -1；左右对称；大图表） | 84 × 30 |
| `vex_fx_w_shield` | view_effects `league_vex_w_shield`（跟随她，画在人物上面 z 3；左右对称） | 34 × 42 |
| `vex_fx_w_hit` | view_effects `league_vex_w_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `vex_fx_e_cast` | view_effects `league_vex_e_cast`（跟随她，画在人物上面 z 3；左右对称） | 26 × 44 |
| `vex_fx_e_land` | view_effects `league_vex_e_land`（不跟随，画在人物下面 z -1；左右对称；大图表） | 48 × 44 |
| `vex_fx_e_slow` | view_buffs `league_vex_e_slow`（跟随，画在人物下面 z -1；左右对称；循环） | 22 × 6 |
| `vex_fx_g_mark` | view_buffs `league_vex_g_mark`（跟随，画在人物上面 z 3；左右对称；循环） | 12 × 10 |
| `vex_fx_g_pop` | view_effects `league_vex_g_pop`（跟随目标，画在人物上面 z 2；左右对称） | 20 × 20 |
| `vex_fx_p_ready` | view_effects `league_vex_p_ready`（跟随她，画在人物上面 z 3；左右对称） | 16 × 10 |
| `vex_fx_r_missile` | view_projectiles `league_vex_r_missile`（跟着弹道转向；上下对称） | 24 × 14 |
| `vex_fx_r_mark` | view_buffs `league_vex_r_mark`（跟随，画在人物上面 z 3；左右对称；循环） | 16 × 10 |
| `vex_fx_r_hit` | view_effects `league_vex_r_hit`（跟随目标，画在人物上面 z 2；左右对称） | 26 × 26 |

- 两张表：`asset/league/effects/league_vex_fx`（小的）和 `league_vex_big`（w_ring、e_land），tag = 名字（build_vex.py 的 views）。
- 弹道图（a_bolt、q_bolt、r_missile）断言上下对称，其余断言左右对称；`e_land` 不跟随（落点）；`w_ring` 跟随她、画在下面。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（影子的靛紫暗部保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
