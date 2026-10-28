# 伦妮：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/renni_design.png`：祖安的炼金男爵，结实的女人，橘红背头、苍白脸、灰色鼻夹和荧光绿导管，背后一大团墨绿羽毛，双手端着一把洋红引擎、黄铜双导板的大链锯）。伦妮在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），39 格高、44 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/renni_size.png`：伦妮缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里伦妮自己的特效贴图（**灰色的形状，游戏里再染色**：链锯旋转、火花、砸地冲击环、碎石、尘土、光点），按用在我们哪张特效分好了行。只在本地用。
> - **伦妮是祖安的炼金男爵，特效都是她的大链锯和化学药剂**：链锯的**橙黄色火花**和钢屑、黄铜的闪光、炼金男爵的**荧光绿化学液**（她导管和药剂罐的颜色）、**微光（Shimmer）的紫粉色光**、祖安的**泥浆**和碎石（她是「泥奔者」）；不要魔法符文，不要光滑的霓虹光束，不要闪电，不要血。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、火花、冲击波、尘土、泥浆溅射没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。她没有飞行道具。冲撞、竖锯格挡、把人举起来的动作都画在她自己的动作帧里，这里不画。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `renni_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `renni_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/renni_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/renni_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「微光狂热」 | 血量低于 40% 时给自己打一针微光：几秒内加攻速，并持续回复最大生命的一部分（30 秒一次） | `p` · `p_rush` |
| 普攻「链锯研磨」 | 链锯往前一顶，一次锯三下 | `a_hit` |
| 技能 1 =「链锯冲撞」 | 端着链锯冲向目标，在前方扇形里连锯三下：物理伤害 + 减速 | `q_hit` · `q_slow` |
| 技能 2 =「锯刃格挡」 | 把链锯竖起来挡在身前：护盾 + 减伤 | `e` · `e_guard` |
| 大招 =「泥奔者重击」 | 链锯把目标挑起来举过头顶（晕眩，她自己回血），再狠狠砸在面前的地上：砸地范围伤害 | `r_hit` · `r_up` · `r_slam` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火花、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 火花（链锯）：`#FFFFFF`、`#FFF4B0`、`#FFC840`、`#F07A18`、`#A0380C`；
  - 黄铜（导板、铆钉）：`#FFF2C0`、`#F2C860`、`#C88A28`、`#7E5014`、`#3E240A`；
  - 钢（锯齿、护盾弧）：`#F0F4FA`、`#B8C2D2`、`#7E8AA0`、`#4A5468`、`#242A36`；
  - 荧光绿化学液（导管、药剂）：`#F0FFE0`、`#B8FF7A`、`#6EE830`、`#2FA818`、`#145A10`；
  - 微光紫粉：`#FFE6FF`、`#F4A8FF`、`#C858F0`、`#7C24B8`、`#3C0E66`；
  - 泥浆：`#D8D0A8`、`#A89868`、`#74684A`、`#4A422E`、`#262014`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `renni_fx_a_hit.png`：普攻：链锯咬一下，4 帧

链锯咬在人身上（一次普攻锯三下，每下播一次）：一个白热的**小闪光**，一把**橙黄色的火花**往两边喷开，几颗钢屑。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C), a steel ramp (#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36).
Effect: A CHAINSAW BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot flash 6 squares across; 2 a fan of short orange-yellow SPARK streaks (1 square thick, 3-5 long) spraying out to both sides (mirrored), a few grey steel chips; 3 the sparks farther and fewer; 4 the last sparks fading. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `renni_fx_q_hit.png`：链锯冲撞：前方锯切（减速），5 帧

冲撞后链锯在前方扇形里连锯三下，每下打中一个人播一次：比普攻大，白热闪光外面一圈**火花喷泉**，夹着几滴**荧光绿的化学液**，钢屑往两边飞。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10), a steel ramp (#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36).
Effect: A HEAVY GRIND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot flash 10 squares across; 2 a fountain of orange-yellow SPARKS spraying up and out to both sides (mirrored) 20 squares wide, a few neon-green chemical drops (1-2 squares) among them; 3 the sparks wider and falling, steel chips flying; 4 the sparks thinning, the green drops falling; 5 the last glints. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `renni_fx_q_slow.png`：链锯冲撞：被减速，6 帧循环

被锯中后减速：脚下一摊**泥浆**，泥里冒着几个**荧光绿的化学泡泡**，泡泡鼓起来又破掉。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mud brown ramp (#D8D0A8, #A89868, #74684A, #4A422E, #262014), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10).
Effect: A SLOWING MUD PUDDLE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) a puddle of dark Zaun MUD 20 squares wide and 6 tall with a lighter rim, two or three neon-green chemical BUBBLES (2-3 squares) swelling in it and popping into a tiny green splash, in turn; frames 1-6 the bubbles rising and bursting. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 6 equal 24:10 cells, image size 2304x160 (each cell 384x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `renni_fx_p.png`：微光狂热：给自己打一针微光，6 帧

血量低于 40% 时给自己注射微光：胸口「嘭」地炸开一团**紫粉色的微光**，往两边冲出一圈光环，一串紫粉色的光点往上窜到头顶，最后几缕紫色的烟。身体位置留空（光从胸口位置的两侧和外圈冒出来）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer violet-pink ramp (#FFE6FF, #F4A8FF, #C858F0, #7C24B8, #3C0E66), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10).
Effect: A SHIMMER SHOT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the sturdy woman stands in the middle, not drawn: 34 squares wide and 38 tall: 1 a violet-pink flash at her chest height, two bright spots 4 squares across at both sides of the body; 2 a violet-pink shock ring 30 squares wide and 10 tall around her waist, a few neon-green drops flicked out (mirrored); 3 the ring wider and fading, two columns of violet-pink motes (1-2 squares) rushing up both sides of her; 4 the motes over her head, a pink glint at the top; 5 thin violet smoke curls rising; 6 the last motes. The middle (the body) left empty. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 6 equal 36:44 cells, image size 3456x704 (each cell 576x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `renni_fx_p_rush.png`：微光狂热：药劲上头（加攻速），6 帧循环

打完微光那几秒：身体两侧一闪一闪的**紫粉色光焰**（只画外圈几格亮边），几点紫粉色的光点往上飘，脚下一圈淡淡的紫光。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer violet-pink ramp (#FFE6FF, #F4A8FF, #C858F0, #7C24B8, #3C0E66).
Effect: A SHIMMER RUSH, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the sturdy woman stands in the middle, not drawn: 34 squares wide and 38 tall: at both sides of her (mirrored) tall flickering violet-pink FLAME tongues 3 squares wide and 20 tall hugging her outline (only a bright edge and a few lit squares), a faint violet ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 28 squares wide and 7 tall at the bottom, a few pink motes drifting up; frames 1-6 the flames flickering and the motes rising. The middle (the body) left empty. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 6 equal 36:44 cells, image size 3456x704 (each cell 576x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `renni_fx_e.png`：锯刃格挡：竖锯挡住，5 帧

她把链锯竖起来挡在身前的一瞬间：身体两侧各「锵」地亮起一道**钢蓝色和黄铜色的护盾弧**，弧上几颗铆钉一闪，几颗火花往外崩。身体位置留空。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C).
Effect: A SAW GUARD RAISED, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the sturdy woman stands in the middle, not drawn: 34 squares wide and 38 tall: 1 two bright glints at both sides of her chest; 2 at both sides of her (mirrored) a tall curved steel-blue SHIELD ARC 4 squares wide and 32 tall with a brass rim and three rivet glints, a white flash where it rings; 3 a few orange sparks knocked off the arcs; 4 the arcs dimmer; 5 only the rims glinting. The middle (the body) left empty. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 5 equal 40:44 cells, image size 3200x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `renni_fx_e_guard.png`：锯刃格挡：护盾和减伤，6 帧循环

格挡的那几秒：身体两侧淡淡的**钢蓝色护盾弧**（只画轮廓的亮边），一道亮光沿着弧往上跑，黄铜铆钉一闪一闪。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A).
Effect: A GUARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the sturdy woman stands in the middle, not drawn: 34 squares wide and 38 tall: at both sides of her (mirrored) a tall curved steel-blue shield ARC 3 squares wide and 32 tall (only a bright rim and a few lit squares, the inside empty), three brass rivet glints on each arc; frames 1-6 a white glint running up the arcs, the rivets blinking in turn. The middle (the body) left empty. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 6 equal 40:44 cells, image size 3840x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `renni_fx_r_up.png`：泥奔者重击：被举在半空（晕眩），6 帧循环

被链锯挑起来、挂在半空晕着的人头顶：几颗**黄铜色和荧光绿的小星星**转圈，中间几颗火花。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10), a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C).
Effect: A STUN OVER THE HEAD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): in the cell (it rides over the unit's head) three small stars (3 squares) in brass and neon green circling on a flat ring 16 squares wide and 4 tall, two tiny orange sparks in the middle; frames 1-6 the stars going round. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 6 equal 20:10 cells, image size 1920x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `renni_fx_r_hit.png`：泥奔者重击：挑起 / 砸中，5 帧

把人挑起来的那一下、和砸地时被砸到的人：一个大的白热闪光，**火花和泥点**往两边四溅，一圈冲击环。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C), a mud brown ramp (#D8D0A8, #A89868, #74684A, #4A422E, #262014), a steel ramp (#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36).
Effect: A CRUSHING HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-hot flash 12 squares across; 2 an orange shock ring 20 squares wide and 8 tall, orange-yellow sparks and brown MUD clots (2-3 squares) flying out to both sides (mirrored); 3 the ring wider and thinner, the mud falling; 4 a puff of dust; 5 the last specks. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 5 equal 22:24 cells, image size 1760x384 (each cell 352x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `renni_fx_r_slam.png`：泥奔者重击：砸地，8 帧

链锯把人狠狠砸在面前的地上：地面炸开**一圈很大的泥浆和碎石冲击波**，中间裂开几道地缝，泥浆和石块往四周飞，环上溅着火花和几滩荧光绿的化学液，最后尘土慢慢落下、地缝暗下去。画在**地上**（从斜上方看的扁椭圆），中心在格子底部中间。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mud brown ramp (#D8D0A8, #A89868, #74684A, #4A422E, #262014), a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10).
Effect: A BIG GROUND SLAM, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell: 1 a white-hot flash 16 squares wide; 2 a thick shock ring of brown MUD 34 squares wide and 12 tall with an orange spark edge, CRACKS splitting out from the middle; 3 the ring 54 wide and 18 tall, mud clots, rock chunks and orange sparks thrown up to both sides (mirrored), neon-green chemical splashes on the ring; 4 the ring 76 wide and 26 tall, thinner; 5 the ring breaking into clumps at the edge, the cracks glowing dull orange; 6 the dust settling; 7 the cracks dimming; 8 faint mud specks and thin dust. everything is a CHEM-BARON's brutal machinery: a CHAINSAW's hot orange SPARKS and steel chips, brass glints, NEON-GREEN chemtech splashes, SHIMMER's violet-pink drug glow, Zaun MUD and rubble; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning, no blood.
Layout: one horizontal row of 8 equal 84:34 cells, image size 10752x544 (each cell 1344x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `renni_icon_skill.png`：技能 1「链锯冲撞」图标

一把链锯从左下往右上猛冲，后面拖着几道速度线，导板前端喷出一大把橙色火花。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little riveted brass corners, a deep murky green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: her CHAINSAW (a round magenta engine with a glowing neon-green rotor disc, a grey-blue handle, two parallel brass guide bars with a dark slot and grey round holes) thrust from the lower left to the upper right, bars first, three speed streaks behind it, a big fan of orange-yellow sparks spraying from the bar tips. Colours: a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a steel ramp (#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36), a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10). No text, no letters.
```

### 图标 2. `renni_icon_skill2.png`：技能 2「锯刃格挡」图标

一把链锯竖着立在画面中间，前面一道钢蓝色的护盾弧，弧上一闪白光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little riveted brass corners, a deep murky green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: her CHAINSAW (a round magenta engine with a glowing neon-green rotor disc, a grey-blue handle, two parallel brass guide bars with a dark slot and grey round holes) standing UPRIGHT in the middle, bars up, a curved steel-blue SHIELD ARC in front of it with a white glint and brass rivets. Colours: a steel ramp (#F0F4FA, #B8C2D2, #7E8AA0, #4A5468, #242A36), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10). No text, no letters.
```

### 图标 3. `renni_icon_ult.png`：大招「泥奔者重击」图标

一把链锯从上往下狠狠砸在地上，地面裂开，泥浆和碎石往两边喷，导板上溅着火花。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little riveted brass corners, a deep murky green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: her CHAINSAW (a round magenta engine with a glowing neon-green rotor disc, a grey-blue handle, two parallel brass guide bars with a dark slot and grey round holes) slamming DOWN from the top, bars first, into cracked ground at the bottom, a burst of brown mud and rock chunks to both sides, orange sparks off the bars, a neon-green splash. Colours: a mud brown ramp (#D8D0A8, #A89868, #74684A, #4A422E, #262014), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a hot spark ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #A0380C), a chemtech green ramp (#F0FFE0, #B8FF7A, #6EE830, #2FA818, #145A10). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `renni_fx_a_hit` | view_effects `tft_renni_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `renni_fx_q_hit` | view_effects `tft_renni_q_hit`（跟随目标，z 2；左右对称） | 24 × 24 |
| `renni_fx_q_slow` | view_buffs `tft_renni_q_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 10 |
| `renni_fx_p` | view_effects `tft_renni_p`（跟随她，z 3；左右对称） | 36 × 44 |
| `renni_fx_p_rush` | view_buffs `tft_renni_p_rush`（跟随她，z 3；左右对称） | 36 × 44 |
| `renni_fx_e` | view_effects `tft_renni_e`（跟随她，z 3；左右对称） | 40 × 44 |
| `renni_fx_e_guard` | view_buffs `tft_renni_e_guard`（跟随她，z 3；左右对称） | 40 × 44 |
| `renni_fx_r_up` | view_buffs `tft_renni_r_up`（跟随被举起的人，头顶，z 3；左右对称） | 20 × 10 |
| `renni_fx_r_hit` | view_effects `tft_renni_r_hit`（跟随目标，z 2；左右对称） | 22 × 24 |
| `renni_fx_r_slam` | view_effects `tft_renni_r_slam`（大表，留在她面前的地上，z -1；左右对称） | 84 × 34 |
| `renni_icon_skill` | skill_icons[0] `asset/tft/icons/tft_renni_skill` | 64 × 64 |
| `renni_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_renni_skill2` | 64 × 64 |
| `renni_icon_ult` | skill_icons[2] `asset/tft/icons/tft_renni_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_renni_fx`（小的）和 `tft_renni_big`（r_slam），tag = 名字。
- 全部断言左右对称。
- p 和 p_rush 由 tft.dll 在血量低于线时播 / 挂上（--plain 的数据在格挡时自己播）。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
