# 塞薇卡：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图 + 3 个技能图标。** 造型已定（`design/sevika_design.png`：祖安的女打手、炼金男爵，肩宽结实，深棕往后梳的头发；左臂是一条被金克丝涂成洋红 / 青色的巨大黄铜机械臂，肩上一台小老虎机，手是一副亮青色的大爪钳）。塞薇卡在游戏里是**高清**的（每个游戏格子里约 1.8×1.8 个细像素），39 格高、30 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/sevika_size.png`：塞薇卡缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里塞薇卡自己的特效贴图（**灰色的形状，游戏里再染色**：火焰、伸缩拳、火箭、金币、油漆、冲击环），按用在我们哪张特效分好了行。只在本地用。
> - **塞薇卡的特效是她那条被金克丝改装过的机械臂**：喷火器的**橙色火焰**、黄铜和青绿色的金属、金克丝的**洋红 / 青色油漆和涂鸦**、老虎机的**金币**和彩色灯珠、**微光（Shimmer）的紫粉色光**；不要魔法符文，不要光滑的霓虹光束，不要闪电。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、火焰、冲击波、烟、油漆溅射没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：留在原地的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**三张会飞的图（`q_flame` 火焰、`p_rocket` 火箭、`e_fist` 拳头）都朝右画、严格上下对称**：游戏按飞行方向把它们转过去，转到左边时上下颠倒也要看起来一样。出拳、平举机械臂、冲刺、咬下的动作都画在她自己的动作帧里，这里不画。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sevika_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `sevika_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/sevika_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/sevika_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「百变铁手」 | 每次放技能，肩上的老虎机转一圈，随机一个改件：火箭（向随机敌人连射几枚小火箭）/ 护盾 / 微光（攻速）/ 三倍（中头奖：这次技能强化） | `p` · `p_rocket` · `p_rocket_hit` · `p_shield` · `p_shimmer` · `p_jackpot` · `p_triple` |
| 普攻「机械铁拳」 | 机械臂一记重拳；每第三下爪钳一夹，伤害更高 | `a_hit` · `a2_hit` |
| 技能 1 =「喷火器」 | 机械臂平举，对前方扇形持续喷火、灼烧，喷火时自己减伤 | `q_flame` · `q_burn` |
| 技能 2 =「伸缩拳」 | 拳头带着弹簧射出去打中目标、击退；撞到后面的敌人，两人都眩晕 | `e_fist` · `e_hit` · `e_stun` |
| 大招 =「嚼一嚼」 | 冲到目标面前，爪钳像嘴一样连咬两口：眩晕 + 流血；血量很低时直接咬死，再冲向附近下一个 | `r_hit` · `r_bleed` · `r_kill` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火焰、冲击波、烟没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 火焰（喷火器）：`#FFFFFF`、`#FFF4B0`、`#FFC840`、`#F07A18`、`#B8360C`、`#5A1606`；
  - 洋红油漆（金克丝）：`#FFE0FA`、`#FF7AE8`、`#F030C8`、`#A0168A`、`#4E0A44`；
  - 青色油漆、爪钳：`#F0FFFF`、`#9AF6FF`、`#34D8F4`、`#1A8CB8`、`#0C3E5C`；
  - 黄铜（机械臂）：`#FFF2C0`、`#F2C860`、`#C88A28`、`#7E5014`、`#3E240A`；
  - 青绿金属（机械臂装甲）：`#C8FFF0`、`#6EE0C8`、`#2AA894`、`#146A5E`、`#0A3430`；
  - 金币（老虎机）：`#FFFFFF`、`#FFF6A0`、`#FFD830`、`#E09A10`、`#8A5206`；
  - 微光紫粉：`#FFE6FF`、`#F4A8FF`、`#C858F0`、`#7C24B8`、`#3C0E66`；
  - 烟、尘土：`#E8E4E0`、`#B0A8A4`、`#7A7270`、`#4A4444`、`#262222`；
  - 暗红（流血）：`#FF9A9A`、`#E83A4A`、`#A8162A`、`#5E0A18`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 不要文字、字母、数字（老虎机的转轮里画金币、星星、菱形这些对称的图案）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `sevika_fx_a_hit.png`：普攻：铁拳打中，4 帧

机械臂一拳打在人身上：一个白热的**冲击闪光**，一圈**黄铜色的冲击环**，几点洋红和青色的漆点往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C).
Effect: A HEAVY PUNCH IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot flash 7 squares across; 2 a brass-yellow shock ring 14 squares wide and 6 tall, a few magenta and cyan PAINT flecks (1-2 squares) knocked out to both sides (mirrored); 3 the ring wider and thinner, the flecks farther; 4 the last flecks fading. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sevika_fx_a2_hit.png`：第三下：爪钳夹住，5 帧

每第三下爪钳一夹：上下两排**亮青色的爪尖**猛地合拢（像一张嘴咬下），合上的地方炸开白光和洋红色的漆点。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A).
Effect: A CLAW CLAMP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of bright CYAN claw tips with magenta points, one above and one below the middle, wide open (16 squares wide, 14 apart); 2 the rows snapping toward each other; 3 the claws shut in the middle, a white flash 8 squares across where they meet, magenta paint flecks bursting out to both sides (mirrored); 4 the claws gone, the flecks flying; 5 the last flecks. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sevika_fx_p.png`：百变铁手：老虎机转起来，8 帧

每次放技能，她肩上的老虎机转一圈：她**头顶**冒出一个小老虎机面板——红棕色的框、**三个奶白色的转轮窗**，转轮里的图案（金币、星星、菱形，都要左右对称的图案）**往下滚动**，最后三个转轮一个接一个停下、框上的小灯珠一闪。**左右对称**（图案也对称），8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a gold coin ramp (#FFFFFF, #FFF6A0, #FFD830, #E09A10, #8A5206), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C).
Effect: A SLOT MACHINE SPIN over her head, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small slot machine panel 26 squares wide and 12 tall (a red-brown frame with a brass rim, a row of tiny pink, purple and cyan bulbs along the top and bottom, THREE cream-white REEL windows side by side); 1 the panel pops up; 2-5 the reels spinning (their symbols - a gold coin, a star, a diamond, all symmetric shapes, never letters or numbers - streaking downward); 6 the left and right reels stop, 7 the middle one stops, 8 the bulbs flash. The panel and every symbol mirrored square for square. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 8 equal 30:16 cells, image size 3840x256 (each cell 480x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sevika_fx_p_rocket.png`：改件·火箭：飞行中，4 帧循环

从老虎机里射出的小火箭（金克丝的）：一枚**洋红和青色涂鸦的小火箭**，头朝右，尾巴喷着橙色的火和一小串灰烟。**朝右、上下对称**（游戏会按飞行方向转），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a fire ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #B8360C, #5A1606), a smoke grey ramp (#E8E4E0, #B0A8A4, #7A7270, #4A4444, #262222).
Effect: A SMALL ROCKET IN FLIGHT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a little rocket 8 squares long and 3 tall, the nose pointing RIGHT, the body painted MAGENTA with a CYAN stripe and a cyan nose cone, two tiny fins (one above, one below); at its tail a flickering orange-white FLAME 3 squares long and a short puff of grey smoke behind it; frames 1-4 the flame flickering. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal 14:8 cells, image size 896x128 (each cell 224x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sevika_fx_p_rocket_hit.png`：改件·火箭：炸开，5 帧

小火箭炸在人身上：一团**橙色的小爆炸**，夹着洋红和青色的彩色碎纸 / 漆点四溅，最后一缕灰烟。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #B8360C, #5A1606), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a smoke grey ramp (#E8E4E0, #B0A8A4, #7A7270, #4A4444, #262222).
Effect: A SMALL ROCKET BLAST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares across; 2 an orange fireball 12 squares across, magenta and cyan CONFETTI / paint bits (1-2 squares) bursting out to both sides (mirrored); 3 the fireball breaking up, dark orange edges; 4 a grey smoke puff, the confetti falling; 5 the last wisps. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sevika_fx_p_shield.png`：改件·护盾：亮起，6 帧

随到护盾：她身体两侧亮起两道**黄铜框的青色护盾弧**（像拼起来的铁板），弧上几颗金色铆钉一闪，洋红色的涂鸦条纹。身体位置留空。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal metal ramp (#C8FFF0, #6EE0C8, #2AA894, #146A5E, #0A3430), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44).
Effect: A SHIELD PLATING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad-shouldered woman stands in the middle, not drawn: 30 squares wide and 39 tall: 1 two bright glints at both sides of her chest; 2 at both sides of her (mirrored) a tall curved TEAL shield arc 4 squares wide and 32 tall made of riveted plates with a BRASS rim and a magenta graffiti stripe, a white flash where it locks on; 3 the arcs whole, gold rivets glinting; 4 a glint running up the arcs; 5 the arcs dimmer; 6 only the rims glinting. The middle (the body) left empty. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 40:44 cells, image size 3840x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sevika_fx_p_jackpot.png`：改件·三倍：中头奖！8 帧

中头奖：她头顶炸开一个**金币喷泉**——一大把金币往上喷、再往两边落下，夹着洋红和青色的彩带碎纸，头顶一圈金光，最后金币落到她脚边闪一闪。身体位置留空（金币从头顶和两侧落下）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold coin ramp (#FFFFFF, #FFF6A0, #FFD830, #E09A10, #8A5206), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C).
Effect: A JACKPOT FOUNTAIN, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad-shouldered woman stands in the middle, not drawn: 30 squares wide and 39 tall (her head near the middle of the cell's upper half): 1 a gold flash 10 squares across over her head; 2 a column of GOLD COINS (round, 3 squares, a white glint each) shooting up from over her head, a gold light ring 30 squares wide and 8 tall; 3 the coins at the top of the cell spreading out to both sides (mirrored), magenta and cyan CONFETTI strips among them; 4-6 the coins and confetti raining down both sides of her; 7 the coins bouncing at her feet with glints; 8 the last glints. The middle (the body) left empty. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 8 equal 56:60 cells, image size 7168x960 (each cell 896x960, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sevika_fx_p_shimmer.png`：改件·微光：药劲上头（攻速），6 帧循环

随到微光：身体两侧一闪一闪的**紫粉色光焰**（只画外圈几格亮边），几点紫粉色光点往上飘，脚下一圈淡淡的紫光。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shimmer violet-pink ramp (#FFE6FF, #F4A8FF, #C858F0, #7C24B8, #3C0E66).
Effect: A SHIMMER RUSH, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad-shouldered woman stands in the middle, not drawn: 30 squares wide and 39 tall: at both sides of her (mirrored) tall flickering violet-pink FLAME tongues 3 squares wide and 20 tall hugging her outline (only a bright edge and a few lit squares), a faint violet ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 28 squares wide and 7 tall at the bottom, a few pink motes drifting up; frames 1-6 the flames flickering and the motes rising. The middle (the body) left empty. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 36:44 cells, image size 3456x704 (each cell 576x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sevika_fx_p_triple.png`：改件·三倍：头奖待命，6 帧循环

中了头奖、下一个技能强化：她头顶转着**三枚金币**，一闪一闪。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold coin ramp (#FFFFFF, #FFF6A0, #FFD830, #E09A10, #8A5206), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44).
Effect: A JACKPOT READY over her head, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three GOLD COINS (3 squares round, a white glint) circling on a flat ring 20 squares wide and 4 tall, two tiny magenta sparkles between them; frames 1-6 the coins going round and glinting in turn. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 24:10 cells, image size 2304x160 (each cell 384x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sevika_fx_q_flame.png`：喷火器：火焰，6 帧循环

机械臂爪钳里喷出来的**火焰**：从格子**左边中间**（她的爪钳）喷出，往右越喷越宽，像一个横放的喇叭；中心白黄、外圈橙红，前端翻滚着火舌和几缕黑烟，夹着几点洋红色的火星（金克丝的改装）。**朝右、上下对称**（游戏会按方向转，转到左边也一样），6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #B8360C, #5A1606), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a smoke grey ramp (#E8E4E0, #B0A8A4, #7A7270, #4A4444, #262222).
Effect: A FLAMETHROWER JET, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): the fire starts at the LEFT EDGE of the cell, in the middle of its height (her claws), and roars out to the RIGHT, widening like a horizontal cone: 4 squares tall at the left edge, 20 squares tall at the right end; a white-yellow core along the middle, orange around it, red-orange tongues at the edges, curling fire tongues and a few dark smoke puffs at the far right end, a few magenta sparks in the flame; frames 1-6 the tongues rolling forward and flickering. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 48:22 cells, image size 4608x352 (each cell 768x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sevika_fx_q_burn.png`：喷火器：被灼烧，6 帧循环

被喷火烧着的人身上：几簇**小火苗**往上窜，带着几点火星和一缕烟。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #B8360C, #5A1606), a smoke grey ramp (#E8E4E0, #B0A8A4, #7A7270, #4A4444, #262222).
Effect: A BURN, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two or three small FLAMES (3 squares wide, 6-9 tall) licking upward over the unit, white-yellow cores and orange-red tips, a few sparks and a thin grey smoke wisp rising above; frames 1-6 the flames flickering. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 16:20 cells, image size 1536x320 (each cell 256x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sevika_fx_e_fist.png`：伸缩拳：飞出去的拳头，4 帧循环

伸缩拳：机械臂的**大铁拳**（合上的爪钳像一张闭着的嘴）往右飞，后面拖着一根**黄铜色的弹簧**，弹簧一圈一圈地伸长。**朝右、上下对称**（爪钳上下两半一样），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal metal ramp (#C8FFF0, #6EE0C8, #2AA894, #146A5E, #0A3430), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44).
Effect: AN EXTENDO-PUNCH FIST IN FLIGHT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): at the RIGHT end a big closed fist 12 squares long and 12 tall - teal armour plates with magenta spikes (as many above as below) and bright CYAN closed claws at its front (an upper and a lower claw, like a shut jaw); behind it, to the left, a BRASS coiled SPRING 4 squares tall stretching back to the left edge of the cell (6-7 coils); frames 1-4 the spring coils stretching and a short white streak or two behind the fist. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal 30:14 cells, image size 1920x224 (each cell 480x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `sevika_fx_e_hit.png`：伸缩拳：打中，6 帧

铁拳打中人：一个大的白热闪光，一圈**黄铜色的冲击波**，洋红和青色的漆点大把溅开，几颗螺栓崩飞。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C).
Effect: A BIG PUNCH IMPACT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-hot flash 12 squares across; 2 a thick brass-yellow shock ring 20 squares wide and 8 tall, a burst of MAGENTA and CYAN paint splats (2-3 squares) thrown out to both sides (mirrored), two little gold bolts flying; 3 the ring wider and thinner, the splats farther; 4 the splats falling; 5 a puff of dust; 6 the last specks. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `sevika_fx_e_stun.png`：伸缩拳：撞晕，6 帧循环

被撞晕的人头顶：几颗**洋红和青色的小星星**转圈。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A).
Effect: A STUN OVER THE HEAD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small stars (3 squares) in magenta, cyan and brass circling on a flat ring 16 squares wide and 4 tall; frames 1-6 the stars going round. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 20:10 cells, image size 1920x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `sevika_fx_r_hit.png`：嚼一嚼：咬一口，5 帧

爪钳像一张大嘴咬下：上下两排**大的亮青色尖牙**（洋红尖头）猛地咬合在人身上，咬合处一道白光，洋红色的漆和金属碎片四溅。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A).
Effect: A BIG CHOMP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a huge jaw - an upper and a lower row of big bright CYAN fangs with magenta tips - wide open around the middle (22 squares wide, 18 apart); 2 the jaws slamming shut; 3 the fangs interlocked across the middle, a white flash 12 squares wide along the bite, magenta paint and brass shards spraying out to both sides (mirrored); 4 the jaw gone, the shards falling; 5 the last specks. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal square cells, image size 2080x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `sevika_fx_r_bleed.png`：嚼一嚼：流血，6 帧循环

被咬过之后流血：身上几道**暗红色的爪痕**一闪，几滴暗红的血珠往下滴。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FF9A9A, #E83A4A, #A8162A, #5E0A18).
Effect: A BLEED, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two short dark crimson claw SCRATCHES (1 square thick, 5 long, slanted, mirrored) on the unit, glinting in turn, and two or three crimson DROPS (1-2 squares) dripping down and fading; frames 1-6 the drops falling. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 14:16 cells, image size 1344x256 (each cell 224x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `sevika_fx_r_kill.png`：嚼一嚼：咬死（斩杀），8 帧

目标血太少被一口咬死：一张**巨大的青色铁嘴**从上下合拢，咬合时爆出一大片**洋红和青色的油漆喷溅**（金克丝的涂鸦），中间一个白色的大星形闪光，最后漆点慢慢落下。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a gold coin ramp (#FFFFFF, #FFF6A0, #FFD830, #E09A10, #8A5206).
Effect: AN EXECUTION CHOMP, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a HUGE jaw (upper and lower rows of bright CYAN fangs with magenta tips, brass gums) wide open, 40 squares wide; 2 the jaws slamming shut; 3 the fangs locked across the middle, a big white STAR flash 20 squares across; 4 a big burst of MAGENTA and CYAN PAINT SPLATTER blasting out to both sides (mirrored) with a few gold sparks, the jaw fading; 5 the splatter at its widest, 40 squares; 6-7 the paint drops falling; 8 a few last drops. everything is a Zaun BRAWLER's loud machinery painted over by a graffiti girl: hot orange FIRE, brass and teal metal, MAGENTA and CYAN paint splats and spray, gold coins from a slot machine, Shimmer's violet-pink glow; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 8 equal square cells, image size 5632x704 (each cell 704x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `sevika_icon_skill.png`：技能 1「喷火器」图标

机械臂的爪钳张开朝右，从里面喷出一大团橙色的火焰。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark brown frame with little riveted brass corners and a few magenta and cyan graffiti scratches, a deep murky teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: her MECHANICAL ARM (brass, teal plates with magenta spikes, a huge pair of bright cyan claws with magenta tips)'s claws open at the left, a big roaring cone of orange-white FIRE blasting out of them to the right, a few magenta sparks. Colours: a fire ramp (#FFFFFF, #FFF4B0, #FFC840, #F07A18, #B8360C, #5A1606), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a teal metal ramp (#C8FFF0, #6EE0C8, #2AA894, #146A5E, #0A3430). No text, no letters.
```

### 图标 2. `sevika_icon_skill2.png`：技能 2「伸缩拳」图标

一个合着爪钳的大铁拳从左下往右上飞出，后面拖着一根黄铜弹簧，拳头前面一道冲击光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark brown frame with little riveted brass corners and a few magenta and cyan graffiti scratches, a deep murky teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big closed mechanical FIST (teal plates, magenta spikes, cyan claws shut) flying from the lower left to the upper right on a stretched BRASS SPRING, a white impact flash in front of it. Colours: a teal metal ramp (#C8FFF0, #6EE0C8, #2AA894, #146A5E, #0A3430), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44). No text, no letters.
```

### 图标 3. `sevika_icon_ult.png`：大招「嚼一嚼」图标

一张巨大的青色铁嘴（上下两排尖牙）正在咬合，洋红色的油漆四溅。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark brown frame with little riveted brass corners and a few magenta and cyan graffiti scratches, a deep murky teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a HUGE mechanical JAW seen from the front - an upper and a lower row of bright CYAN fangs with magenta tips biting shut in the middle, MAGENTA paint splattering out, a gold glint. Colours: a cyan paint ramp (#F0FFFF, #9AF6FF, #34D8F4, #1A8CB8, #0C3E5C), a magenta paint ramp (#FFE0FA, #FF7AE8, #F030C8, #A0168A, #4E0A44), a brass ramp (#FFF2C0, #F2C860, #C88A28, #7E5014, #3E240A), a gold coin ramp (#FFFFFF, #FFF6A0, #FFD830, #E09A10, #8A5206). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sevika_fx_a_hit` | view_effects `tft_sevika_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `sevika_fx_a2_hit` | view_effects `tft_sevika_a2_hit`（跟随目标，z 2；左右对称） | 20 × 20 |
| `sevika_fx_p` | view_effects `tft_sevika_p`（跟随她，在她头顶，z 4；左右对称） | 30 × 16 |
| `sevika_fx_p_rocket` | view_projectiles `tft_sevika_p_rocket`（飞向目标，随飞行方向旋转；上下对称、朝右） | 14 × 8 |
| `sevika_fx_p_rocket_hit` | view_effects `tft_sevika_p_rocket_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `sevika_fx_p_shield` | view_effects `tft_sevika_p_shield`（跟随她，z 3；左右对称） | 40 × 44 |
| `sevika_fx_p_jackpot` | view_effects `tft_sevika_p_jackpot`（大表，跟随她，z 4；左右对称） | 56 × 60 |
| `sevika_fx_p_shimmer` | view_buffs `tft_sevika_p_shimmer`（跟随她，z 3；左右对称） | 36 × 44 |
| `sevika_fx_p_triple` | view_buffs `tft_sevika_p_triple`（跟随她，头顶，z 4；左右对称） | 24 × 10 |
| `sevika_fx_q_flame` | view_projectiles `tft_sevika_q_flame`（大表，一道从她指向目标的线，随方向旋转；上下对称、朝右） | 48 × 22 |
| `sevika_fx_q_burn` | view_buffs `tft_sevika_q_burn`（跟随被烧的人，身上，z 3；左右对称） | 16 × 20 |
| `sevika_fx_e_fist` | view_projectiles `tft_sevika_e_fist`（飞向目标，随飞行方向旋转；上下对称、朝右） | 30 × 14 |
| `sevika_fx_e_hit` | view_effects `tft_sevika_e_hit`（跟随目标，z 2；左右对称） | 24 × 24 |
| `sevika_fx_e_stun` | view_buffs `tft_sevika_e_stun`（跟随被晕的人，头顶，z 4；左右对称） | 20 × 10 |
| `sevika_fx_r_hit` | view_effects `tft_sevika_r_hit`（跟随目标，z 2；左右对称） | 26 × 26 |
| `sevika_fx_r_bleed` | view_buffs `tft_sevika_r_bleed`（跟随被咬的人，身上，z 3；左右对称） | 14 × 16 |
| `sevika_fx_r_kill` | view_effects `tft_sevika_r_kill`（大表，跟随目标，z 3；左右对称） | 44 × 44 |
| `sevika_icon_skill` | skill_icons[0] `asset/tft/icons/tft_sevika_skill` | 64 × 64 |
| `sevika_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_sevika_skill2` | 64 × 64 |
| `sevika_icon_ult` | skill_icons[2] `asset/tft/icons/tft_sevika_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_sevika_fx`（小的）和 `tft_sevika_big`（q_flame、p_jackpot、r_kill），tag = 名字。
- 留在原地的全部断言左右对称；q_flame、p_rocket、e_fist 断言上下对称（朝右）。
- 老虎机（p）每次 Q / E / R 都播；火箭、护盾、微光、头奖由 tft.dll 摇到后播 / 挂上（--plain 的数据每次放三分之一的火箭、护盾、微光）。
- q_flame 是 LineRangeProjectile 的图（从她到目标的线，锚点在线的起点那头：导入时核对）。
- 用 `pixel_1x/` 切格（import_renni_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
