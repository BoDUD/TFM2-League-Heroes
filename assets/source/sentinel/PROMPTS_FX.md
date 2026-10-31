# 苍蓝雕纹魔像：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图 + 3 个技能图标。** 造型已定（`design/sentinel_design.png`：3/4 朝右、弓着背的深青灰岩石巨人：两只比脑袋大得多的巨拳垂在身前两侧；肩背上堆着浅灰绿大石块；浅色八角石墩小脑袋半埋在两肩之间，深色缺口里一只青色独眼；胸口 V 形青光、腰上青色带子；石块上刻着螺旋符文）。魔像在游戏里是**高清**的（每个游戏格子里约 1.7×1.7 个细像素），40 格高、60 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/sentinel_size.png`：魔像缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是熔岩巨兽（石头护盾、碎石、砸地）和奥恩（地面裂缝、冲击波、石刺）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **魔像是古老的符文石头巨人，特效都是它的味道**：发青光的螺旋符文、地面上透着青光的裂缝、成块的青灰色和浅灰绿色碎石石板、灰褐色的尘土；不要火焰、不要闪电、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：除了往前跑的裂隙 `r_crack`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sentinel_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `sentinel_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/sentinel_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/sentinel_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「岩拳猛击」 | 一只巨拳举过头顶砸下 | `a_hit` |
| 被动「蓝霸符」 | 它每放一个技能，身边友军的技能冷却立刻缩短 | `p_blue` |
| 技能 1 =「双拳重砸」 | 双拳砸在身前地面，周围敌人受伤并减速 | `q_hit` · `q_slow` |
| 技能 2 =「雕纹石肤」 | 符文亮起，获得护盾，嘲讽身边的敌人 | `e_cast` · `e_shield` · `e_taunt` |
| 大招 =「蔚蓝冲击波」 | 护盾，双拳过顶猛砸地面，朝敌人最多的方向裂开一道裂隙：击飞、魔法伤害、破法（下一个技能被封） | `r_slam` · `r_crack` · `r_hit` · `r_reave` · `r_seal` · `e_shield` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 符文青（它的眼睛、发光的缝和符文）：`#F0FFFF`、`#A6F4FF`、`#3FD8F2`、`#1594CF`、`#0C5A86`；
  - 石头（浅灰绿到深青灰）：`#DDE0C6`、`#AEB497`、`#73898A`、`#45606A`、`#263840`；
  - 尘土：`#E2DACA`、`#B3A992`、`#7D7464`、`#4C473E`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `sentinel_fx_a_hit.png`：普攻「岩拳猛击」：石拳砸中，4 帧

石拳砸中：一下青白色的闪光，几块青灰色的碎石和一圈尘土往两边崩开，一两点青色的符文火星。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86), a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A STONE FIST IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale cyan-white flash 5 squares across; 2 a short burst of cyan light with four stubby rays, 12 squares across, a few slate stone chips flying out to both sides (mirrored); 3 the chips falling outward, a low puff of grey-brown dust at the bottom, two tiny cyan sparks; 4 the last dust and one falling chip on each side. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sentinel_fx_q_hit.png`：技能 1「双拳重砸」：砸地冲击环，6 帧

双拳砸地：它身前地面上一下青色的闪光，**一圈带裂缝的冲击环**往外推开（从斜上方看的椭圆，宽是高的 3 倍），环上一道道短裂缝透着青光，碎石和尘土往外翻。**只在地面上**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86), a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A GROUND POUND RING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND only, seen from above at a slant: 1 a bright cyan-white flash in the middle, 12 squares wide; 2 a ring of short jagged CRACKS glowing cyan bursting outward (an ellipse 40 squares wide, 13 tall), stone chips jumping up along it; 3 the ring 60 squares wide, its cracks longer, grey dust rolling out on both sides (mirrored); 4 the ring at 72 squares wide and thinner, the chips falling; 5 only the cracks' cyan glow fading and settling dust; 6 a few dim cracks. The middle stays clear after frame 2. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 76:26 cells, image size 7296x416 (each cell 1216x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sentinel_fx_q_slow.png`：技能 1「双拳重砸」：减速，6 帧循环

被减速的人：脚边**几块青灰色的小石块缠着脚踝**，石缝里一点青光，像脚被石头拖住。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840), a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86).
Effect: STONE SHACKLES, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): on EACH side (mirrored) two or three small slate-teal stone chunks hugging the ankle line, a thin cyan glint in the seam between them, a faint low dust haze; frames 1-6 the chunks grinding a square up and down and the glints moving (every frame left-right symmetric). Subtle. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:8 cells, image size 2304x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sentinel_fx_e_cast.png`：技能 2「雕纹石肤」：符文亮起，5 帧

它身上的螺旋符文一下亮起：身体四周**一圈青色螺旋符文**往外闪开（像刻在石头上的花纹发光飞起），最后化成青色光点往上飘。**它的身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86).
Effect: A RUNE FLARE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the golem stands in the middle, not drawn: about 58 squares wide and 40 tall, hunched, its two huge fists low at its sides, its small head at the upper right: 1 a few cyan sparks at its edges; 2 six to eight glowing cyan SPIRAL RUNE GLYPHS (each a small square spiral 5 squares across, near-white in their middle line) appearing all round the edge of its body, mirrored; 3 the glyphs bright, pushed a little outward, short cyan rays between them; 4 the glyphs breaking into cyan motes drifting UP; 5 the last motes at the top. The middle of the cell (its body) stays EMPTY. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 64:46 cells, image size 5120x736 (each cell 1024x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sentinel_fx_e_shield.png`：技能 2「雕纹石肤」/ 大招护盾：石肤护盾，6 帧循环

它的护盾：身子外面**一圈刻着符文的石板**围成的护壳（竖着的椭圆，只画外圈：一块块浅灰绿的石板，每块上一个发青光的螺旋符文），符文一闪一闪地轮流亮。**里面它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840), a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86).
Effect: A RUNE STONE SHELL, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the golem stands in the middle, not drawn: about 58 squares wide and 40 tall, hunched, its two huge fists low at its sides, its small head at the upper right: a ring of CARVED STONE PLATES (an upright ellipse 66 squares wide and 46 tall, only its 3-square rim drawn, made of eight to ten pale sage stone slabs with dark seams), each slab with a small glowing CYAN SPIRAL RUNE; a thin cyan light line along the inner edge; frames 1-6 the runes lighting up in turn round the ring (mirrored pairs) and the inner line breathing (every frame left-right symmetric). INSIDE the ring stays EMPTY (its body). everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 70:50 cells, image size 6720x800 (each cell 1120x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sentinel_fx_e_taunt.png`：技能 2「雕纹石肤」：被嘲讽，6 帧循环

被嘲讽的人头顶：一个**青色的发光独眼符文**（一个圆圈里一只眼睛，像魔像的眼睛盯着你），一跳一跳地发光。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86), a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840).
Effect: A TAUNT GLYPH, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head: a round slate stone disc 10 squares across with a glowing CYAN EYE glyph cut into it (an almond eye, a near-white pupil square), a thin cyan ring round the disc; frames 1-6 the eye pulsing brighter and dimmer and the disc bobbing one square up and down. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 1152x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sentinel_fx_r_slam.png`：大招「蔚蓝冲击波」：猛砸地面，6 帧

它双拳砸进地面：一下巨大的青白闪光，地面上**一个很大的青色冲击波环**炸开，大块的石板翘起、碎石和尘土往两边飞，地上留下一圈发青光的裂缝。**只在地面和低处**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86), a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A HUGE RUNE SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it, seen from above at a slant: 1 a big cyan-white flash at the middle bottom, 20 squares wide, short rays; 2 a thick bright cyan SHOCKWAVE RING bursting open on the ground (an ellipse 50 squares wide, 16 tall, 3 squares thick), big slate STONE SLABS tilting up out of the ground on both sides (mirrored), chips flying; 3 the ring 84 squares wide, a ring of glowing cyan CRACKS left inside it, grey dust billowing out low; 4 the ring at the cell's edge and thinning, the slabs sinking, the chips falling; 5 the cracks' glow and the settling dust; 6 a few dim cracks. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 96:40 cells, image size 9216x640 (each cell 1536x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sentinel_fx_r_crack.png`：大招「蔚蓝冲击波」：往前跑的裂隙，6 帧循环

裂隙的最前端：地面被撕开**一道往右冲的青色裂缝**，裂缝最前面石头往上崩起、尖尖的石刺一根根冒出来又落下，后面拖着发光的裂缝。**上下对称、朝右**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86), a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A RUNNING FISSURE HEAD, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): on the ground, seen from above: a jagged CRACK of bright cyan light running from the left edge to the right, 6 squares wide at the left and splitting into forks at the front (the right third), near-white along its middle; at its front end slate STONE SPIKES and chips bursting up on both sides of the crack (mirrored top and bottom), grey dust round them; frames 1-6 the spikes rising and falling in turn and the forks flickering forward, the glow pulsing along the crack (every frame top-bottom symmetric). everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 40:18 cells, image size 3840x288 (each cell 640x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sentinel_fx_r_hit.png`：大招「蔚蓝冲击波」：被裂隙击飞，5 帧

被裂隙击中的人：脚下**石刺一下冲上来**、一道青光往上喷，碎石往两边飞。**人站的地方留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86), a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A ROCK ERUPTION, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 a cyan crack flash on the ground under its feet; 2 three sharp slate STONE SPIKES shooting up beside its feet (one each side, one small in front, mirrored), a column of cyan light rising up its sides; 3 the spikes at their tallest (10 squares), chips flying out; 4 the spikes crumbling, the light fading upward; 5 falling chips and dust. The middle of the cell (its body) stays EMPTY. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 22:26 cells, image size 1760x416 (each cell 352x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sentinel_fx_r_reave.png`：大招「蔚蓝冲击波」：破法标记，6 帧循环

被破法的人头顶：**一颗裂开的青色符文水晶**（菱形，中间一道裂缝），缓缓上下浮动、一闪一闪。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86).
Effect: A CRACKED MANA RUNE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head: a cyan diamond crystal 8 squares wide and 10 tall, a near-white spiral rune in it, a dark CRACK running down its middle splitting it in two halves a square apart; frames 1-6 it bobbing one square up and down, the halves glowing brighter and dimmer, one tiny shard falling from the crack. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 14:12 cells, image size 1344x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sentinel_fx_r_seal.png`：大招「蔚蓝冲击波」：破法封印，6 帧循环

被封住技能的人头顶：**一圈青色的符文锁环**（一个转着的符文圆环，中间一个石头小锁），表示技能被封。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86), a stone ramp (#DDE0C6, #AEB497, #73898A, #45606A, #263840).
Effect: A RUNE SEAL, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head: a flat ring of glowing cyan rune marks (an ellipse 16 squares wide, 6 tall) with a small slate STONE PADLOCK 6 squares tall hanging in its middle, a cyan spiral on the lock; frames 1-6 the rune marks moving round the ring (mirrored) and the lock glinting. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 18:14 cells, image size 1728x224 (each cell 288x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sentinel_fx_p_blue.png`：被动「蓝霸符」：友军冷却加快，6 帧

队友拿到蓝霸符：脚下一圈**青色的符文小光环**，几颗青色的小符文光点沿着身子两侧往上升（像英雄联盟里蓝 buff 的感觉）。**人站的地方留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rune-cyan light ramp (#F0FFFF, #A6F4FF, #3FD8F2, #1594CF, #0C5A86).
Effect: A BLUE BUFF GLOW, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 a thin cyan ring appearing on the ground at its feet (an ellipse 22 squares wide, 6 tall); 2 the ring bright, small cyan rune motes (2x2 and 1x1 squares) rising from it up both sides of the body (mirrored); 3-4 the motes rising higher, one small spiral glyph above its head; 5 the motes fading near the top, the ring dimming; 6 the last motes. The middle (its body) stays EMPTY. everything is an ANCIENT RUNE GOLEM's power: glowing CYAN carved runes and spiral glyphs, cyan cracks of light in the ground, chunky slate-teal and pale sage stone chips and slabs, grey-brown dust; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 26:34 cells, image size 2496x544 (each cell 416x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `sentinel_icon_skill.png`：技能 1「双拳重砸」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan rune corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: two huge slate-teal stone fists smashing down together into the ground, a ring of glowing cyan cracks and stone chips bursting out under them. No text, no letters.
```

### 图标 2. `sentinel_icon_skill2.png`：技能 2「雕纹石肤」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan rune corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a round shield of carved pale sage stone plates with a big glowing cyan spiral rune in its middle, small cyan rune sparks round it. No text, no letters.
```

### 图标 3. `sentinel_icon_ult.png`：大招「蔚蓝冲击波」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan rune corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a jagged bright cyan fissure tearing across the ground from the lower left to the upper right, stone spikes bursting up along it, a small one-eyed stone golem head glowing cyan in the lower left corner. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sentinel_fx_a_hit` | view_effects `tft_sentinel_a_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `sentinel_fx_q_hit` | view_effects `tft_sentinel_q_hit`（大表，放在它砸地的地面上，不跟随，z -1；左右对称） | 76 × 26 |
| `sentinel_fx_q_slow` | view_buffs `tft_sentinel_q_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 8 |
| `sentinel_fx_e_cast` | view_effects `tft_sentinel_e_cast`（大表，跟随它，z 3；左右对称） | 64 × 46 |
| `sentinel_fx_e_shield` | view_buffs `tft_sentinel_e_shield` / `tft_sentinel_r_shield`（大表，跟随它，z 3；左右对称） | 70 × 50 |
| `sentinel_fx_e_taunt` | view_buffs `tft_sentinel_e_taunt`（跟随被嘲讽的人，头顶上方，z 4；左右对称） | 12 × 12 |
| `sentinel_fx_r_slam` | view_effects `tft_sentinel_r_slam`（大表，放在它砸地的地面上，不跟随，z -1；左右对称） | 96 × 40 |
| `sentinel_fx_r_crack` | view_projectiles `tft_sentinel_r_crack`（大表，tft.dll 放的直线弹道，随飞行方向旋转；上下对称、朝右） | 40 × 18 |
| `sentinel_fx_r_hit` | view_buffs `tft_sentinel_r_hit`（跟随被击飞的人，z 3；左右对称） | 22 × 26 |
| `sentinel_fx_r_reave` | view_buffs `tft_sentinel_r_reave`（跟随被破法的人，头顶上方，z 4；左右对称） | 14 × 12 |
| `sentinel_fx_r_seal` | view_buffs `tft_sentinel_r_seal`（跟随被封住的人，头顶上方，z 4；左右对称） | 18 × 14 |
| `sentinel_fx_p_blue` | view_buffs `tft_sentinel_p_blue`（跟随拿到的友军，z 3；左右对称） | 26 × 34 |
| `sentinel_icon_skill` | skill_icons[0] `asset/tft/icons/tft_sentinel_skill` | 64 × 64 |
| `sentinel_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_sentinel_skill2` | 64 × 64 |
| `sentinel_icon_ult` | skill_icons[2] `asset/tft/icons/tft_sentinel_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_sentinel_fx`（小的）和 `tft_sentinel_big`（q_hit、e_cast、e_shield、r_slam、r_crack），tag = 名字。
- r_crack 断言上下对称（朝右），其余断言左右对称。
- q_hit、r_slam 放在它砸地的地面上（不跟随，z -1）；e_cast、e_shield 是它身上的 caster 画面（e_shield 也给大招护盾用）；p_blue 是友军身上的 buff；q_slow、e_taunt 是敌人身上的 buff；r_crack 是 tft.dll 放的裂隙弹道，r_hit、r_reave、r_seal 是 tft.dll 给的 buff。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
