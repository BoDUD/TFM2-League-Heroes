# 灰烬驱魔人 洛克：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型已定（`design/locke_design.png`：Q 版年轻驱魔人，金发、紫色圆眼镜、咧嘴笑、深青绿长风衣、宝蓝敞领衬衫、背上黑色棺匣、手里银钉）。洛克在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），44 格高、28 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/locke_size.png`：洛克缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里洛克自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**洛克是灰烬驱魔人，特效都是灵魂火和灰烬**：**冷色的灵魂火**（白、浅青、亮蓝到靛蓝——就是他 W 变身时的颜色）、**灰烬**（浅灰到深灰）、封印用的**品红紫**（和他棺匣的箍带一样）、钉子的**银色**，偶尔几点**橙黄火星**；不要光滑的霓虹光束，也不要橙红色的普通火。
> - **特效要亮**：每道光、每团火都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、火、灰烬、符文没有黑描边**；**只有棺匣这个“东西”（`r_case`、`r_land` 里的匣子）有 1 格近黑描边**。
> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。
> - **对称**：除了两个弹道，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）——棺匣落地 `r_land` **正面**看。**弹道**（`q_nail`、`r_case`）**朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `locke_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/locke_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/locke_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「圣银穿心」 | 拿钉子捅，附带魔法伤害；打英雄会引爆 Q 的钉子印记 | `a_hit` · `q_pop` |
| 被动里的 W「灵焰仪式」 | E 落到英雄身边时点燃灵魂：攻速、移速变快，每秒烧掉一点自己的血，结束时补回来 | `w_ign` · `w_aura` · `w_end` |
| 技能 1 =「伏魔三钉」 | 连扔三颗钉：伤害、减速、在英雄头上留下钉子印记 | `q_nail` · `q_hit` · `q_mark` · `slow` |
| 技能 2 =「灰猎无影」 | 化成灰烬瞬移到英雄身边、落地冲击，下一次普攻冲刺穿过目标；参与击杀刷新 | `e_out` · `e_in` · `e_hit` · `e_dash` · `p_reset` |
| 大招 =「万魔狱」 | 抡起棺匣扔出去：落地伤害、减速、给英雄打上封印标记，血量低于处决线就被封印 | `r_case` · `r_land` · `r_hit` · `r_mark` · `r_tick` · `r_seal` · `slow` |

连招：**钉子扎中英雄 → 灰猎无影马上好**，**闪到英雄身边 → 立即点燃灵魂**，**参与击杀 → 灰猎无影刷新**，**大招标记 → 伏魔三钉马上好**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、灰烬没有黑描边，也不要用最深的颜色给形状描一圈边**（棺匣除外）。
- **都是灵魂火和灰烬**：冷蓝的灵魂火、灰烬、品红紫的封印、银色的钉；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 灵魂火：`#FFFFFF`、`#D6F6FF`、`#8CE4FF`、`#3FA8FF`、`#2A5CF0`、`#2A2CA8`；
  - 灰烬：`#F2EEE8`、`#C8C0B8`、`#8C847E`、`#57524F`、`#2E2B2C`；
  - 封印·品红紫：`#FFE6FA`、`#F48CE6`、`#C83CC0`、`#7E1E8A`、`#3E1050`；
  - 银钉：`#FFFFFF`、`#E2ECF2`、`#AEC0CC`、`#6E8496`；
  - 火星：`#FFF4C8`、`#FFC46A`、`#F07A32`；
- 打中、爆发居中画，不旋转；地面上的圈（光环、法阵、灰烬）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `locke_fx_q_nail.png`：伏魔三钉：飞出去的钉子，4 帧循环

扔出去的**驱魔大钉**：一根银色的长钉，钉尖朝右，钉身裹着一层冷蓝白的灵魂火，后面拖着一条蓝色的火尾和几点灰烬（参考 q_trail、q_mis_nailedgeblend、q_cursed_trail）。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #E2ECF2, #AEC0CC, #6E8496), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A FLYING SOUL NAIL, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a long silver nail 9 squares long with its point on the right and a flat round head on the left, wrapped in thin white-cyan soul flame, a tapering blue flame tail 6 squares long behind it with a few ash flecks; frames 1-4 the tail flickering. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `locke_fx_r_case.png`：万魔狱：飞出去的棺匣，4 帧循环

扔出去的**封印棺匣**：横着飞的黑色六边形长匣（品红紫箍带、银色菱形钉），匣身缝隙里透出品红紫的光，后面拖着一条紫蓝的烟尾（参考 r_mis_firemask、r_totem_idle_blurtrail）。**朝右飞，上下对称**（匣子正面、背面一样），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-purple seal ramp (#FFE6FA, #F48CE6, #C83CC0, #7E1E8A, #3E1050), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A FLYING BINDING CASE, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a long black hexagonal case 16 squares long and 6 tall lying along the flight, magenta-purple bands round it and small silver diamond studs, a magenta glow leaking from its seams; a short trail of violet-blue smoke and ash behind it on the left; frames 1-4 the glow pulsing and the trail curling. The case has a 1-square near-black outline. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 24:12 cells, image size 1536x192 (each cell 384x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `locke_fx_a_hit.png`：普攻：钉子刺中，3 帧

钉子捅中：一个银白的十字星闪，四周迸出几点冷蓝的灵魂火星（被动「圣银穿心」的附加魔法伤害）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #E2ECF2, #AEC0CC, #6E8496), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8).
Effect: A SILVER STAKE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white four-point star flash 6 squares across; 2 the star 10 across with cold blue sparks bursting out at mirrored places; 3 the sparks further out, dimming into ash flecks. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `locke_fx_q_hit.png`：伏魔三钉：钉子扎中，3 帧

钉子扎中敌人：一圈冷蓝的火花炸开、中间一下白光，几点灰烬往外飞（参考 q_proc_tar、q_tar）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A NAIL STRIKING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bright white-cyan spiky star 8 squares across; 2 a ring of cold blue soul sparks 12 across bursting out at mirrored places; 3 the sparks dimming into ash flecks. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `locke_fx_q_mark.png`：伏魔三钉：头顶的钉子印记，4 帧循环

被钉上印记的人头顶：**三根小银钉**，中间一根竖着、两边两根往外斜，下面托着一弯冷蓝的月牙（参考 nail_ui_01：洛克在英雄联盟里就是这个印记）。一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #E2ECF2, #AEC0CC, #6E8496), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8).
Effect: A NAIL MARK OVER THE HEAD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small silver nails pointing down, the middle one upright and 6 squares tall, the side ones leaning out, resting on a thin cold-blue crescent moon 12 squares wide that cups them from below; frames 1-4 the nails glinting in turn and the crescent pulsing. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `locke_fx_q_pop.png`：伏魔三钉：印记被引爆，4 帧

洛克普攻把钉子印记引爆：几根灵魂钉从四周往目标身上一起扎进去，冷蓝的火一下炸开（参考 q_consume_inward）。**身体位置留空**，钉子和火只在外圈。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), a silver ramp (#FFFFFF, #E2ECF2, #AEC0CC, #6E8496), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: THE NAILS DRIVEN IN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 three ghostly silver-blue nails in a ring around the unit's middle, 20 across, points inward; 2 the nails darting inward; 3 a burst of cold blue soul flame 18 across at the middle with white sparks; 4 ash flecks drifting away. The middle (the body) mostly empty. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 22:26 cells, image size 1408x416 (each cell 352x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `locke_fx_slow.png`：减速：脚下一圈灰烬，4 帧循环

被减速：脚下一圈灰黑的灰烬和几缕冷蓝的火苗，灰烬往上飘。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8).
Effect: AN ASH SLOW AT THE FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a thin ellipse of grey ash 14 wide with a few small cold blue flames on it; frames 1-4 the flames flickering in turn and ash flecks drifting up. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `locke_fx_e_out.png`：灰猎无影：原地消散，5 帧

洛克瞬移走：原地他的身影**化成一团灰烬**往上散开，脚下一圈冷蓝的符文圈一闪（参考 e_ash_erosion、e_sigilring）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8).
Effect: VANISHING INTO ASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Locke stands in the middle, not drawn: about 27 squares wide and 44 tall: 1 a cold blue sigil ring 22 wide flashing on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) and a tall column of grey ash flakes in his shape 18 wide and 40 tall; 2 the column breaking up into drifting ash; 3 the ash scattering up and out, a few blue embers; 4 thin ash wisps high up; 5 the last flakes fading. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 5 equal 30:48 cells, image size 2400x768 (each cell 480x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `locke_fx_e_in.png`：灰猎无影：在目标身边出现，5 帧

洛克从灰烬里出现：一团灰烬从四周**往中间卷回来**、凝成他的身形，脚下冷蓝的符文圈亮起（参考 e_blinkend_swirlin、e_sigilring）。**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8).
Effect: REAPPEARING FROM ASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Locke stands in the middle, not drawn: about 27 squares wide and 44 tall: 1 ash flakes scattered wide 28 across; 2 the ash swirling inward at both sides; 3 the ash drawn into a tall column 18 wide, a cold blue sigil ring 22 wide lighting up on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 4 a bright white-blue flash at the column's edges; 5 the last ash and the ring fading. The middle (his body) left empty from frame 3. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 5 equal 30:48 cells, image size 2400x768 (each cell 480x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `locke_fx_e_hit.png`：灰猎无影：落地的灵魂冲击，4 帧

落地时一圈冷蓝的灵魂火**贴地往外推开**，带起灰烬（参考 e_groundwave），打到周围的敌人。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A SOUL SHOCKWAVE ON THE GROUND, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a white-blue flash ellipse 12 wide; 2 a ring of cold blue soul flame 28 wide pushing out; 3 the ring 40 wide, breaking into blue flames and ash; 4 ash puffs fading at both ends. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 44:18 cells, image size 2816x288 (each cell 704x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `locke_fx_e_dash.png`：灰猎无影：冲刺的残影，4 帧

E 之后那一下冲刺普攻：他身后（两边都是）一道横着的灰烬残影和冷蓝的斩痕（参考 e_slash_front、e_slash_mid、e_string_trail）。这张在红色方也不翻，所以**左右对称**画成一条横着的斩痕，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C), a silver ramp (#FFFFFF, #E2ECF2, #AEC0CC, #6E8496).
Effect: A DASH SLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin horizontal white-blue slash line 30 squares long at the middle; 2 the slash 38 long and 4 tall with a silver edge and cold blue flame along it; 3 the slash breaking into a row of ash streaks; 4 ash streaks fading. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 40:20 cells, image size 2560x320 (each cell 640x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `locke_fx_p_reset.png`：灰猎无影：参与击杀、E 刷新，4 帧

参与击杀后 E 重置：洛克头顶一圈冷蓝的符文环亮一下，几点灰烬往上冒。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A RESET SIGIL OVER HIS HEAD, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin cold blue ring 10 wide; 2 the ring 22 wide with four small rune marks at its top, bottom, left and right; 3 the ring flashing white; 4 the ring fading into ash flecks rising. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal 26:16 cells, image size 1664x256 (each cell 416x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `locke_fx_w_ign.png`：灵焰仪式：点燃灵魂，6 帧

洛克点燃自己的灵魂：脚下一圈冷蓝的光环，**一圈冷蓝白的灵魂火从脚下往上卷起来**、包住他的外圈，顶上散出火星（参考 w_fire_swirl、w_cas_sheenring、w_groundwind）。火只在他身体外圈，**身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A SOUL IGNITING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Locke stands in the middle, not drawn: about 27 squares wide and 44 tall: 1 a bright white-blue ring 20 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 tongues of cold blue-white soul flame rising at both sides of him to his waist; 3 the flames swirling up to his shoulders; 4 the flames over his head, a white flash ring at his chest height at the sides; 5 the flames thinning, blue sparks flying up; 6 a few sparks and ash flecks. The middle (his body) left empty. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 6 equal 36:52 cells, image size 3456x832 (each cell 576x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `locke_fx_w_aura.png`：灵焰仪式：身上燃着的灵魂火，6 帧循环

W 持续时（4 秒）他身边一直燃着冷蓝的灵魂火：几缕火苗贴着他身体两侧往上飘、脚下一圈淡淡的光（他这时攻速、移速变快，同时被灵魂火灼烧）。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A SOUL FIRE AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Locke stands in the middle, not drawn: about 27 squares wide and 44 tall: a soft ellipse of cold blue light on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 22 wide, thin tongues of white-blue soul flame licking up both sides of his body to above his shoulders; frames 1-6 the flames rising and flickering in turn, a few blue sparks drifting up. The middle (his body) left empty. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 6 equal 34:50 cells, image size 3264x800 (each cell 544x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `locke_fx_w_end.png`：灵焰仪式：结束时回血，5 帧

W 结束、把烧掉的血补回来：灵魂火**往里收回他身上**，几点冷蓝的光点从四周飘回来、头顶一个小小的白光（参考 q_consume_inward）。**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8).
Effect: A SOUL FIRE DRAWN BACK IN, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Locke stands in the middle, not drawn: about 27 squares wide and 44 tall: 1 cold blue motes scattered around him 28 wide; 2 the motes drifting inward at both sides; 3 thin blue streaks converging on his chest height at both sides; 4 a small white plus sparkle over his head; 5 the last motes fading. The middle (his body) left empty. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 5 equal 30:46 cells, image size 2400x736 (each cell 480x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `locke_fx_r_land.png`：万魔狱：棺匣落地、封印圈，8 帧

棺匣砸在地上：**黑色棺匣竖着插进地面**（正面看，品红紫箍带、银菱形钉，有近黑描边），地上一大圈**品红紫的封印法阵**亮起来（圆圈、四个符文、中间十字，参考 r_tell_outercircle、r_totem_timer_runes、r_aoe_flash_totem），冷蓝的冲击和灰烬往外推开。法阵最大时**横向 50 格、纵向 16 格**。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-purple seal ramp (#FFE6FA, #F48CE6, #C83CC0, #7E1E8A, #3E1050), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A BINDING CASE SLAMMING DOWN, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the case seen from the FRONT, standing upright in the middle with its foot on the ground line 6 squares above the bottom: a black hexagonal case 10 squares wide and 26 tall with magenta-purple bands and silver diamond studs and a 1-square near-black outline. 1 the case dropping in from the top, a white flash where it lands; 2 the case planted, a cold blue shockwave ring 24 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 3 a magenta-purple seal circle 40 wide lighting up on the ground round it, ash bursting out at both sides; 4 the circle 50 wide and 16 tall with four rune marks at its left, right, front and back and a cross through it, magenta light rising from the case's seams; 5-6 the runes glowing, ash settling; 7 the circle dimming; 8 the case and a faint circle. Frames 4-6 MUST fill 50 squares across. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 8 equal 60:46 cells, image size 7680x736 (each cell 960x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `locke_fx_r_hit.png`：万魔狱：被砸中，4 帧

被棺匣的冲击打中：一下品红紫的闪光，四周迸出冷蓝的火花和灰烬。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-purple seal ramp (#FFE6FA, #F48CE6, #C83CC0, #7E1E8A, #3E1050), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8), an ash ramp (#F2EEE8, #C8C0B8, #8C847E, #57524F, #2E2B2C).
Effect: A SEAL BLAST HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a magenta-white flash 8 squares across; 2 a burst of magenta-purple and cold blue sparks 16 across at mirrored places; 3 the sparks further out, ash flecks; 4 fading ash. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `locke_fx_r_mark.png`：万魔狱：被标记的人，6 帧循环

被大招标记的人（4 秒内血量低于处决线就会被封印）：身体外圈一圈**品红紫的封印符文**慢慢转，头顶一个小小的品红紫十字符号（参考 r_tell_outercircle、r_totem_timer_runes）。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-purple seal ramp (#FFE6FA, #F48CE6, #C83CC0, #7E1E8A, #3E1050).
Effect: A SEAL MARK ON A UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: a loose ring of small magenta-purple rune marks around the unit's middle 22 wide seen slightly from above, and a small magenta cross sigil 6 squares tall over its head; frames 1-6 the runes glowing in turn around the ring and the sigil pulsing. The middle (the body) left empty. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 6 equal 24:40 cells, image size 2304x640 (each cell 384x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `locke_fx_r_tick.png`：万魔狱：处决检查，3 帧

标记每隔一会儿收紧一下：目标身上一个小小的品红紫符文一闪。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-purple seal ramp (#FFE6FA, #F48CE6, #C83CC0, #7E1E8A, #3E1050).
Effect: A SEAL PULSE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small magenta rune mark 4 squares tall; 2 the rune 6 tall with a thin magenta ring 10 wide round it; 3 the ring fading. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `locke_fx_r_seal.png`：万魔狱：封印成功，6 帧

封印了一个英雄、法器回到洛克手里：一道品红紫的灵魂光从高处**落进他身后的棺匣**，他身上闪一下品红紫的光、往上冒符文（大招冷却减少、处决线变高）。**身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-purple seal ramp (#FFE6FA, #F48CE6, #C83CC0, #7E1E8A, #3E1050), a soul fire ramp (#FFFFFF, #D6F6FF, #8CE4FF, #3FA8FF, #2A5CF0, #2A2CA8).
Effect: A SOUL SEALED, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Locke stands in the middle, not drawn: about 27 squares wide and 44 tall: 1 a magenta-white soul wisp high above him; 2 the wisp streaking down toward him; 3 a magenta flash around his outline at both sides; 4 three small magenta runes rising at both sides of him; 5 the runes higher, dimmer; 6 the last motes fading. The middle (his body) left empty. everything is an EXORCIST'S SOUL FIRE and ASH: cold white-cyan-blue soul flames with an indigo edge, drifting ash and soot, silver nails, magenta-purple seal runes and circles; flat shades, crisp shapes; no smooth neon beams, no orange fire (only a few ember sparks where written).
Layout: one horizontal row of 6 equal 30:48 cells, image size 2880x768 (each cell 480x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `locke_fx_q_nail` | view_projectiles `league_locke_q_nail`（弹道，z 2；朝右、上下对称） | 16 × 8 |
| `locke_fx_r_case` | view_projectiles `league_locke_r_case`（弹道，z 2；朝右、上下对称） | 24 × 12 |
| `locke_fx_a_hit` | view_effects `league_locke_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `locke_fx_q_hit` | view_effects `league_locke_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `locke_fx_q_mark` | view_buffs `league_locke_q_mark`（跟随目标，头顶，z 3；左右对称） | 14 × 10 |
| `locke_fx_q_pop` | view_effects `league_locke_q_pop`（跟随目标，z 2；左右对称） | 22 × 26 |
| `locke_fx_slow` | view_buffs `league_locke_q_slow` / `league_locke_r_slow`（跟随，脚下，z -1；左右对称） | 16 × 8 |
| `locke_fx_e_out` | view_effects `league_locke_e_out`（在洛克出发的地方，z 2，不跟随；左右对称） | 30 × 48 |
| `locke_fx_e_in` | view_effects `league_locke_e_in`（在洛克落脚的地方，z 2，不跟随；左右对称） | 30 × 48 |
| `locke_fx_e_hit` | view_effects `league_locke_e_hit`（跟随，z 2；左右对称） | 44 × 18 |
| `locke_fx_e_dash` | view_effects `league_locke_e_dash`（在洛克身上，z 2，不跟随；左右对称） | 40 × 20 |
| `locke_fx_p_reset` | view_effects `league_locke_p_reset`（跟随洛克，z 2；左右对称） | 26 × 16 |
| `locke_fx_w_ign` | view_effects `league_locke_w_ign`（跟随洛克，z 2；左右对称） | 36 × 52 |
| `locke_fx_w_aura` | view_buffs `league_locke_w_on`（跟随洛克，z -1；左右对称） | 34 × 50 |
| `locke_fx_w_end` | view_effects `league_locke_w_end`（跟随洛克，z 2；左右对称） | 30 × 46 |
| `locke_fx_r_land` | view_effects `league_locke_r_land`（大表，落点，z 1，不跟随；左右对称） | 60 × 46 |
| `locke_fx_r_hit` | view_effects `league_locke_r_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `locke_fx_r_mark` | view_buffs `league_locke_r_mark`（跟随目标，z 3；左右对称） | 24 × 40 |
| `locke_fx_r_tick` | view_effects `league_locke_r_tick`（跟随目标，z 2；左右对称） | 12 × 12 |
| `locke_fx_r_seal` | view_effects `league_locke_r_seal`（跟随洛克，z 2；左右对称） | 30 × 48 |

- 两张表：`asset/league/effects/league_locke_fx`（小的）和 `league_locke_big`（r_land），tag = 名字（build_locke.py 的 views；buff 的 tag：w_on → w_aura、q_slow / r_slow → slow）。
- 弹道（q_nail、r_case）断言上下对称；其余断言左右对称。
- 用 `pixel_1x/` 切格（import_trundle_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
