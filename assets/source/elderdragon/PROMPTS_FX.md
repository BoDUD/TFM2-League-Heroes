# 远古巨龙：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图 + 3 个技能图标。** 造型已定（`design/elderdragon_design.png`：3/4 朝右、四条腿压低站着的翼龙：两只深紫色大蝙蝠翼半张开往上举，翼指尖是青色发光的爪尖；背上、尾巴上一排排青色水晶尖刺；白色晶体鬃毛盖住脖子和胸口；深色尖嘴、两只蓝色弯角、发青光的嘴、青色眼睛；尾巴往上卷）。远古巨龙在游戏里是**高清**的（每个游戏格子里约 2.84×2.84 个细像素），44 格高、60 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/elderdragon_size.png`：远古巨龙缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是斯莫德（龙焰、吐息、火花、落地）和墨菲特（冲击、碎石）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **远古巨龙的龙焰是青色的**（和它发光的嘴、眼睛、水晶尖刺一样）：近白色的火芯、亮青色的火焰、边上深青到深蓝；**不要橙色的火**；少量深紫色（翅膀）、白色水晶；不要闪电、不要光滑的霓虹光束、不要符文。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**火焰、光、风没有黑描边**；水晶碎片可以有深色描边。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：喷出去的龙焰（`q_fire`）**上下对称、朝右**（游戏按飞行方向旋转它）；其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `elderdragon_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `elderdragon_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/elderdragon_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/elderdragon_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「龙焰撕咬」 | 咬目标，目标身边的敌人被溅射 | `a_hit` · `a_splash` |
| 被动「远古巨龙霸符」 | 对生命很低的敌方英雄造成伤害时直接处决 | `p_exec` |
| 技能 1 =「烈焰吐息」 | 朝穿过目标、敌人最多的直线喷青色龙焰，伤害逐个递减，并【引燃】 | `q_fire` · `q_hit` · `ig` |
| 技能 2 =「龙翼风暴」 | 立起身两翼猛拍，扇开身边的敌人并减速，自己减伤 | `e_cast` · `e_slow` · `e_guard` |
| 大招 =「绝伦火热」 | 无敌飞上天空再砸落：大范围晕眩并【引燃】，自己全能吸血，落地立刻再喷一口烈焰吐息 | `r_slam` · `r_stun` · `r_vamp` · `ig` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火焰、光、风没有黑描边，也不要用最深的颜色给形状描一圈边**（水晶碎片可以有深色描边）。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 青色龙焰（它的嘴、眼睛、水晶尖刺）：`#FFFFFF`、`#C8FFFF`、`#3DF2F2`、`#12B5C8`、`#0B6E8A`、`#12305A`；
  - 深紫翅膀：`#B9A6E8`、`#7A5CC2`、`#4E3590`、`#2E1F5C`、`#1A1236`；
  - 白色水晶鬃毛：`#FFFFFF`、`#E4E6EC`、`#B4B6C4`、`#7C7E92`；
  - 风：`#F2FBFF`、`#BFE8F5`、`#7FC4DE`、`#4A8DB0`；
- 打中居中画，不旋转；地面上的冲击波是从斜上方看的扁平椭圆。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `elderdragon_fx_a_hit.png`：普攻「龙焰撕咬」：咬中，4 帧

咬中：**上下两排青色的尖牙印**一合，中间一下青白色的火花，几点青色火星往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A).
Effect: A BITE IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of three pointed cyan FANG marks, one row above and one below, open, 12 squares wide; 2 the fang rows snapped shut in the middle, a near-white flash 6 squares across where they meet; 3 a cyan flame burst 14 squares across, small cyan sparks flying out to both sides (mirrored); 4 the last sparks and two thin teal wisps. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `elderdragon_fx_a_splash.png`：普攻「龙焰撕咬」：被溅到，4 帧

目标身边的人被溅到：一小团青色火星炸开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A).
Effect: A SPLASH OF SPARKS, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tiny near-white point; 2 a small cyan flame puff 7 squares across; 3 four cyan sparks flying out (mirrored); 4 two sparks fading. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `elderdragon_fx_q_fire.png`：技能 1「烈焰吐息」：喷出去的龙焰，6 帧循环

它喷出去的龙焰：**一团往右冲的青色火焰**，前端是近白色的火头、往后变成亮青、再到深青色的火舌，火舌一条条往后甩开（像一团巨大的喷火头）。**上下对称、朝右**，6 帧循环（火舌翻滚）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A).
Effect: A ROARING BREATH OF DRAGONFIRE flying RIGHT, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a big rolling ball of cyan flame 16 squares long and 14 tall at the RIGHT end, its front a near-white hot core, behind it long cyan to teal FLAME TONGUES streaming back to the left (3 above the middle line and 3 below, mirrored), 34 squares in all, a few cyan crystal sparks inside; frames 1-6 the tongues rolling and flickering backward, the core pulsing. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 34:18 cells, image size 3264x288 (each cell 544x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `elderdragon_fx_q_hit.png`：技能 1「烈焰吐息」：被龙焰烧到，4 帧

被龙焰烧到：一下**青色火焰从脚下往上窜**、身体两侧各一条火舌，近白色的火芯，火星往上飘。**身体位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A).
Effect: A BURST OF DRAGONFIRE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn (only its feet line and its sides): 1 a flat near-white flash at its feet 10 squares wide; 2 cyan flames leaping up both its sides (mirrored), 18 squares tall, near-white cores; 3 the flames at their highest, sparks rising; 4 the flames sinking, two teal wisps. The middle of the cell (the body) stays EMPTY. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 4 equal 18:22 cells, image size 1152x352 (each cell 288x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `elderdragon_fx_ig.png`：引燃：持续燃烧，6 帧循环

被【引燃】的人：**脚下和身体两侧一直有小小的青色火苗在烧**，火星往上飘。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A).
Effect: AN IGNITE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: small cyan flames (3-6 squares tall) licking up along its feet line and up both its sides to its shoulders (mirrored), near-white tips, two or three cyan sparks drifting up; frames 1-6 the flames flickering and the sparks rising in turn. The middle of the cell (the body) stays EMPTY. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 22:30 cells, image size 2112x480 (each cell 352x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `elderdragon_fx_p_exec.png`：被动「远古巨龙霸符」：处决，6 帧

被处决：**一只青色的巨龙之眼**在人身上猛地睁开，然后**一道青色龙焰柱从上往下砸穿**，火焰往两边炸开。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A), a dark purple wing ramp (#B9A6E8, #7A5CC2, #4E3590, #2E1F5C, #1A1236).
Effect: AN EXECUTION, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 a slit-pupil cyan DRAGON EYE 10 squares wide opening over its chest; 2 the eye wide, glowing; 3 a near-white pillar of cyan dragonfire crashing straight down through it from the top of the cell, 8 squares wide; 4 the pillar at its brightest, flames bursting out to both sides at the feet (mirrored); 5 the flames rolling out, the eye gone; 6 the last cyan wisps rising. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 28:34 cells, image size 2688x544 (each cell 448x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `elderdragon_fx_e_cast.png`：技能 2「龙翼风暴」：翅膀扇出的风暴，6 帧

它两只翅膀猛地往下一拍：**一圈风浪从它身边贴着地面往两边扫开**，风里卷着青色的火星和紫色的碎羽。**它的身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale wind ramp (#F2FBFF, #BFE8F5, #7FC4DE, #4A8DB0), a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A), a dark purple wing ramp (#B9A6E8, #7A5CC2, #4E3590, #2E1F5C, #1A1236).
Effect: A WING STORM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon stands in the middle, not drawn: about 59 squares wide and 44 tall, a four-legged winged dragon, its head low at the right, its wings raised over its back, its feet on the bottom line of the cell: 1 two pale wind arcs at its feet on both sides; 2 broad curling GUST WAVES (pale blue-white with cyan edges) rolling out low along the ground to both sides (mirrored), 70 squares wide, cyan sparks and dark purple wing scraps caught in them; 3 the waves 90 squares wide, thinner, curling over at their ends; 4 swirls of wind spinning at both ends; 5 the waves breaking into wisps; 6 the last wisps and sparks. The middle of the cell (its body) stays EMPTY. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 96:40 cells, image size 9216x640 (each cell 1536x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `elderdragon_fx_e_slow.png`：技能 2「龙翼风暴」：被风缠住减速，6 帧循环

被减速的人脚下：**两圈淡蓝色的小旋风**绕着脚转。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale wind ramp (#F2FBFF, #BFE8F5, #7FC4DE, #4A8DB0).
Effect: A CLINGING GUST, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): at a unit's feet: two flat pale blue-white wind loops 18 squares wide and 3 tall, one swirling each way (mirrored), a few tiny cyan specks; frames 1-6 the loops turning. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 20:8 cells, image size 1920x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `elderdragon_fx_e_guard.png`：技能 2「龙翼风暴」：龙鳞护体（减伤），6 帧循环

它减伤的几秒：**身体轮廓外一圈青色的水晶鳞片光**一闪一闪，几片小水晶在身边绕。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A), a white crystal ramp (#FFFFFF, #E4E6EC, #B4B6C4, #7C7E92).
Effect: A CRYSTAL SCALE GUARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon stands in the middle, not drawn: about 59 squares wide and 44 tall, a four-legged winged dragon, its head low at the right, its wings raised over its back, its feet on the bottom line of the cell: small pointed CYAN CRYSTAL SCALES (2-4 squares) set in a ring just outside its outline, glinting near-white one after another, two little white crystal shards orbiting on each side (mirrored); frames 1-6 the glints running round. The middle of the cell (its body) stays EMPTY. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 70:52 cells, image size 6720x832 (each cell 1120x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `elderdragon_fx_r_slam.png`：大招「绝伦火热」：从天上砸落，8 帧

它从天上砸回地面：**地面一圈青色龙焰冲击波往四周扫开**（从斜上方看是扁扁的一个椭圆环），中间一下近白色的强光、地面裂开、碎石和青色火柱往上窜。**只在地面和低处**。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A), a dark purple wing ramp (#B9A6E8, #7A5CC2, #4E3590, #2E1F5C, #1A1236).
Effect: A DRAGON'S SLAM, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND seen from above at a slant: 1 a near-white flash 20 squares wide at the bottom middle; 2 a flat ELLIPSE RING of cyan dragonfire 60 squares wide and 14 tall rushing out, the ground cracked under it with glowing cyan seams; 3 the ring 100 squares wide, cyan flame pillars (6-14 squares tall) shooting up along it, rock chips flying (mirrored); 4 the ring 126 squares wide, the pillars at their highest; 5-6 the ring thinning, the pillars falling into embers; 7 glowing cracks and drifting sparks; 8 the last cyan embers. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 8 equal 130:44 cells, image size 16640x704 (each cell 2080x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `elderdragon_fx_r_stun.png`：大招「绝伦火热」：被震晕，6 帧循环

被晕眩的人头顶：**一圈青色的小火星**在转。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A).
Effect: A DAZE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head: a flat ring 14 squares wide of four small cyan flame stars circling (mirrored); frames 1-6 the stars going round. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 16:8 cells, image size 1536x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `elderdragon_fx_r_vamp.png`：大招「绝伦火热」：全能吸血，6 帧循环

它全能吸血的几秒：**一缕缕青色的生命之火从四周往它身上流**，身体轮廓边上一圈青光一闪一闪。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan dragonfire ramp (#FFFFFF, #C8FFFF, #3DF2F2, #12B5C8, #0B6E8A, #12305A), a dark purple wing ramp (#B9A6E8, #7A5CC2, #4E3590, #2E1F5C, #1A1236).
Effect: A DRAGON'S HUNGER, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon stands in the middle, not drawn: about 59 squares wide and 44 tall, a four-legged winged dragon, its head low at the right, its wings raised over its back, its feet on the bottom line of the cell: thin streams of cyan life-fire curling in from the corners of the cell toward its outline (mirrored), small near-white motes riding them, a flickering cyan edge glow along its outline; frames 1-6 the streams flowing inward. The middle of the cell (its body) stays EMPTY. everything is the ELDER DRAGON's: CYAN DRAGONFIRE (near-white hot cores, bright cyan flames, deep teal and navy at the edges, never orange), sharp pointed CYAN CRYSTAL SHARDS, a little dark purple; flat shades, crisp blocky flame tongues; no lightning, no smooth neon beams, no runes.
Layout: one horizontal row of 6 equal 76:56 cells, image size 7296x896 (each cell 1216x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `elderdragon_icon_skill.png`：技能 1「烈焰吐息」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little cyan crystal corner studs, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a dark dragon head with blue curved horns at the left, jaws wide open, a roaring stream of cyan dragonfire blasting out to the right, near-white at its core. No text, no letters.
```

### 图标 2. `elderdragon_icon_skill2.png`：技能 2「龙翼风暴」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little cyan crystal corner studs, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge dark purple bat wing with glowing cyan claw tips beating down, pale curling gust waves rushing out beneath it. No text, no letters.
```

### 图标 3. `elderdragon_icon_ult.png`：大招「绝伦火热」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark navy frame with little cyan crystal corner studs, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a dark winged dragon diving down from the top with wings spread, a white crystal mane and a glowing cyan mouth, a ring of cyan dragonfire bursting on the ground below it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `elderdragon_fx_a_hit` | view_effects `tft_elderdragon_a_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `elderdragon_fx_a_splash` | view_buffs `tft_elderdragon_a_splash`（跟随被溅射的人，z 3；左右对称） | 12 × 12 |
| `elderdragon_fx_q_fire` | view_projectiles `tft_elderdragon_q_fire`（tft.dll 沿直线放出、穿透一路的敌人，随飞行方向旋转；上下对称、朝右） | 34 × 18 |
| `elderdragon_fx_q_hit` | view_buffs `tft_elderdragon_q_hit`（跟随被烧到的人，z 3；左右对称） | 18 × 22 |
| `elderdragon_fx_ig` | view_buffs `tft_elderdragon_ig`（跟随被引燃的人，z 3；左右对称） | 22 × 30 |
| `elderdragon_fx_p_exec` | view_buffs `tft_elderdragon_p_exec`（跟随被处决的人，z 4；左右对称） | 28 × 34 |
| `elderdragon_fx_e_cast` | view_effects `tft_elderdragon_e_cast`（大表，跟随它，z 3；左右对称） | 96 × 40 |
| `elderdragon_fx_e_slow` | view_buffs `tft_elderdragon_e_slow`（跟随被减速的人，脚下，z 3；左右对称） | 20 × 8 |
| `elderdragon_fx_e_guard` | view_buffs `tft_elderdragon_e_guard`（大表，跟随它，z 3；左右对称） | 70 × 52 |
| `elderdragon_fx_r_slam` | view_effects `tft_elderdragon_r_slam`（大表，放在它落地的地方，不跟随，z -1；左右对称） | 130 × 44 |
| `elderdragon_fx_r_stun` | view_buffs `tft_elderdragon_r_stun`（跟随被晕的人，头顶上方，z 4；左右对称） | 16 × 8 |
| `elderdragon_fx_r_vamp` | view_buffs `tft_elderdragon_r_vamp`（大表，跟随它，z 3；左右对称） | 76 × 56 |
| `elderdragon_icon_skill` | skill_icons[0] `asset/tft/icons/tft_elderdragon_skill` | 64 × 64 |
| `elderdragon_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_elderdragon_skill2` | 64 × 64 |
| `elderdragon_icon_ult` | skill_icons[2] `asset/tft/icons/tft_elderdragon_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_elderdragon_fx`（小的）和 `tft_elderdragon_big`（e_cast、e_guard、r_slam、r_vamp），tag = 名字。
- q_fire 断言上下对称（朝右），其余断言左右对称。
- q_fire 是 tft.dll 沿直线放出的穿透弹道；a_hit 在被咬的人身上；a_splash、q_hit、ig、p_exec 是 tft.dll 给敌人上的 buff；e_cast 跟随它；r_slam 放在它落地的地方（不跟随，z -1）；e_slow、r_stun 是数据给敌人的 buff；e_guard、r_vamp 是它身上的 buff。
- 用 `pixel_1x/` 切格（import_sentinel_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
