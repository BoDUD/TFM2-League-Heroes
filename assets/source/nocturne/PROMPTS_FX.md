# 永恒梦魇 魔腾：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型已定（`design/nocturne_design.png`，8 倍，你画的版本 B，削到 40 格）。
> - 大小对照 `design/nocturne_size.png`：定稿造型放大 4 倍，尾巴尖在红色脚底线上，上面是 10 格一段的刻度，右边是原版忍者。魔腾 33×40 格（头冠尖到尾巴尖 40 格），原版英雄约 31–36 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里魔腾自己的特效贴图（多数是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（被动横扫、Q 的飞刃和影径、E 的灵链、W 的屏障、R 的飞扑和落地），只在本地用，不要提交。颜色按下面写的色阶。
> - 特效照下面第 1–17 条和「所有特效图的规则」画，每张一个 PNG，文件名 `nocturne_fx_<名字>.png`，排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。最好打成一个 zip（`nocturne_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「暗影之刃」 | 弯刃砍击；每 12 秒（或第 4 次普攻）横扫身边所有敌人，每打中一个回血 | `nocturne_fx_hit` · `nocturne_fx_p_spin` · `nocturne_fx_p_hit` |
| 技能 1 = Q「梦魇之径」 | 掷出暗影之刃穿过一路的敌人，地上留下 5 秒影径；被打中的英雄身后也拖着影径，魔腾在影径上加速加攻击 | `nocturne_fx_q_blade` · `nocturne_fx_q_path` · `nocturne_fx_q_hit` · `nocturne_fx_q_dusk` |
| 技能 2 = E「无言恐惧」+ W「黑暗庇护」 | 梦魇灵链拴住目标 2 秒（链子、每 0.5 秒的伤害），结束时还在附近就恐惧；同时升起 1.5 秒暗影屏障，挡到攻击就攻速提升 | `nocturne_fx_e_grip` · `nocturne_fx_e_chain` · `nocturne_fx_e_tick` · `nocturne_fx_e_fear` · `nocturne_fx_w_shroud` · `nocturne_fx_w_proc` |
| 大招 = R「鬼影重重」 | 黑暗降临：我方全队隐身 3 秒，敌方英雄头上罩一圈黑雾；魔腾飞扑一名敌方英雄，落地斩击 | `nocturne_fx_r_burst` · `nocturne_fx_r_veil` · `nocturne_fx_r_dark` · `nocturne_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **暗色特效要看得见**：魔腾的特效大多是暗靛色的烟，游戏地面和卡片背景也偏暗，所以每个烟团都要有亮一点的边（浅靛蓝）和几点蓝白的光，不要整团死黑。
- 颜色（按每条写的用）：
  - 暗影烟（魔腾的黑暗）：`#C9D2FF`、`#7E8BE0`、`#46509E`、`#262B5E`、`#12142E`；
  - 蓝白亮光（烟里的光点、屏障的纹路、浪头）：`#FFFFFF`、`#CFE6FF`、`#7FB6FF`、`#3D6BD9`；
  - 刃红（弯刃的刀光、斩痕）：`#FFF2F2`、`#FF8A9A`、`#E8264B`、`#9B1032`、`#560F27`；
  - 刀光银（刃边）：`#FFFFFF`、`#D3D7DC`、`#A1A3AA`、`#777680`；
  - 梦魇紫（恐惧、灵链、敌人头上的黑雾）：`#F0E0FF`、`#B98CF0`、`#7A4BB8`、`#4A2A78`、`#26143F`。
- **飞行类特效朝右画，而且上下对称**（飞刃 `q_blade`、灵链 `e_chain`、地上的影径 `q_path`）：游戏会把它转到飞行方向。灵链一节一节首尾相接，左右两端要能接上。
- 命中、爆炸、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在角色身上的特效（横扫、屏障、攻速、队友的暗影、敌人头上的黑雾）：格子里留出空的人形位置，不要画人；恐惧画在头顶，不挡脸。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `nocturne_fx_hit.png`：普攻命中，5 帧

弯刃砍中目标：一道红色的弧形划光（白芯、红边、银色刀光），几点红色火花往外飞（参考 BA_hit_blend、Gash）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from a crimson ramp (#FFF2F2, #FF8A9A, #E8264B, #9B1032, #560F27) with steel (#FFFFFF, #D3D7DC, #A1A3AA, #777680).
Effect: a CURVED BLADE SLASH HIT, 5 frames: 1 a small white flash at the center; 2 a bright curved slash of light (a narrow crescent, white core, crimson edge, a thin steel-grey rim) across the center from upper left to lower right; 3 the slash at full length with 3-4 small crimson sparks flying outward; 4 the slash thins, the sparks fly further and dim; 5 a few dark red specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nocturne_fx_p_spin.png`：被动 暗影之刃：横扫一圈（围着魔腾，跟随），6 帧

暗影之刃的横扫：魔腾两把刀向两边一挥，围着他一整圈的暗影刀光——一道宽宽的弧形刀光（暗靛色的烟、红色的刃光、蓝白的亮边）从右边扫起，绕着他转一整圈（从斜上方看是扁椭圆，宽是高的 2 倍），然后散成烟（参考 P_SlashUlt、P_Slash_mesh、Temp_P_cleave_AoE_Spark）。中间是魔腾的位置，不要画人；椭圆的中心在格子中间偏下（他的脚底），刀光高度在他的腰到胸口。约 84 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with crimson (#FFF2F2, #FF8A9A, #E8264B, #9B1032, #560F27) and a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a SPINNING CLEAVE all round a figure (do NOT draw the figure), 6 frames: the arc is a wide flattened ellipse (twice as wide as tall) around the middle of the cell: 1 a bright crimson blade-arc appears on the right side; 2 the arc sweeps round the front (the lower half of the ellipse) as a wide band of dark indigo shadow with a crimson cutting edge and a thin blue-white rim; 3 THE FULL CIRCLE: the band closes round the whole ellipse, brightest here, a few crimson sparks thrown outward; 4 the band thins and breaks into curling shadow wisps; 5 the wisps drift outward; 6 a few dark specks. Leave the middle of the ellipse empty (the figure stands there).
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 4608x384 (each cell 768x384); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nocturne_fx_p_hit.png`：暗影之刃打中的每个敌人，4 帧

横扫打中：敌人身上三道平行的红黑色爪痕（参考 P_WolfScratch），一闪就散。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from a crimson ramp (#FFF2F2, #FF8A9A, #E8264B, #9B1032, #560F27) with shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E).
Effect: a CLAW SCRATCH HIT, 4 frames: 1 a white flash; 2 three parallel diagonal scratch marks of light (white cores, crimson edges, dark indigo smoke at their ends) across the center; 3 the marks at full length, smoke puffing from them; 4 the marks fade into dark red and indigo specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nocturne_fx_q_blade.png`：Q 梦魇之径：飞出去的暗影之刃（飞行中循环），4 帧

掷出的暗影之刃：一把旋转的暗影弯刃（像一只张开的暗影爪子，红黑色的刃、蓝白的亮边）朝右飞，后面拖一条暗靛色的烟尾（参考 Q_MissileHead、Q_Claw_02、Q_Mis_smoke_Trail）。上下对称。约 20 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with crimson (#FFF2F2, #FF8A9A, #E8264B, #9B1032, #560F27) and a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a FLYING SHADOW BLADE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a spinning shadow blade like an open dark claw - curved crimson blades with blue-white edges round a dark indigo core; behind it (to the left) a trail of dark indigo smoke that narrows to a point; the blade turns a quarter turn each frame and the smoke trail ripples.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the blade on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nocturne_fx_q_path.png`：Q 梦魇之径：地上的影径（地面，5 秒），11 帧

暗影之刃飞过后地上留下的影径：一条长长的暗靛色烟带（从魔腾脚下一直到刀飞到的地方），边上卷着烟丝，里面一闪一闪几点蓝白的光（参考 Q_GroundSmoke02、Q_Fire_Trail_Up）。1–4 帧从左端向右长出来（跟着飞刀），5–8 帧是持续的样子（循环，烟丝翻动），9–11 帧变淡散掉。上下对称。约 66 格长、10 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a DARK TRAIL ON THE GROUND seen from above (a long horizontal band, SYMMETRIC above and below its middle line), 11 frames: 1-4 the band of dark indigo smoke grows from the LEFT end to the right (a quarter, a half, three quarters, the full length) with a brighter blue-white leading tip; 5-8 the full band (a seamless loop): curling smoke along its edges, a few faint blue-white sparks twinkling inside, the curls shifting each frame; 9-11 the band thins, breaks into wisps and fades from the left.
Layout: one VERTICAL column of 11 equal cells, each 7 wide to 1 tall, image size 1792x2816 (each cell 1792x256); the band on the middle line of every cell, from the left edge to the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nocturne_fx_q_hit.png`：Q 打中，5 帧

暗影之刃穿过敌人：一道暗靛色的烟一炸，带一道红色的划痕（参考 Q_Claw_02）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with crimson (#FFF2F2, #FF8A9A, #E8264B, #9B1032, #560F27).
Effect: a SHADOW BLADE HIT, 5 frames: 1 a blue-white flash at the center; 2 a burst of dark indigo smoke with a crimson slash mark across it; 3 the smoke at full size, the slash brightest; 4 the smoke breaks into curls; 5 a few indigo specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nocturne_fx_q_dusk.png`：Q 打中的敌方英雄身后拖着的影径（脚下循环），4 帧

被 Q 打中的敌方英雄脚下冒着一团暗靛色的烟，向两边飘（表示他身后也拖着影径，魔腾追着他会加速）。循环 4 帧。约 24 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E).
Effect: DARK SMOKE CURLING ON THE GROUND round a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a low, flat ring of dark indigo smoke wisps (twice as wide as tall) curling outward to both sides, a few lighter indigo highlights, shifting each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 2304x256 (each cell 768x256); the smoke at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nocturne_fx_e_grip.png`：E 无言恐惧：抓住目标的暗影之手，5 帧

魔腾的梦魇灵链扎进目标：一只暗影的爪子从下往上一抓，抓住的地方亮起紫蓝色的光，然后变成一圈缠着的烟（参考 E_Flare_02twist、E_WispySmoke01）。约 26 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with terror violet (#F0E0FF, #B98CF0, #7A4BB8, #4A2A78, #26143F) and a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a SHADOW CLAW GRIP on a figure (do NOT draw the figure), 5 frames: 1 a violet flash at the middle; 2 a dark indigo shadow claw with long thin fingers reaches up round the middle; 3 the claw closes, a twisting violet-and-blue-white flare where it grips; 4 the claw becomes a ring of coiling dark smoke round the middle; 5 the smoke thins to wisps.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nocturne_fx_e_chain.png`：E 梦魇灵链：从目标飞回魔腾的一节链（循环），3 帧

灵链的一节：一段扭曲的暗紫色烟雾锁链（像一根拧着的黑紫色烟绳，中间一条亮紫的芯），很多节首尾相接连成一条拴住目标的链（参考 E_Beam）。每节 24 格长、6 格高，左右两端要能接上。上下对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from terror violet (#F0E0FF, #B98CF0, #7A4BB8, #4A2A78, #26143F) with shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E).
Effect: ONE SEGMENT OF A DARK TETHER, horizontal, 3 frames, a seamless loop, SYMMETRIC above and below the middle line: a twisting rope of dark violet-indigo smoke with a thin bright violet core running along the middle, filling the cell from the left edge to the right edge so that segments placed end to end form one continuous chain; the twist and the core shimmer move a little to the right each frame.
Layout: one horizontal row of 3 equal cells, each 4 wide to 1 tall, image size 1536x128 (each cell 512x128); the rope on the middle line, touching both side edges. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nocturne_fx_e_tick.png`：E 灵链每 0.5 秒的伤害，4 帧

灵链在目标身上每跳一次伤害：一小圈紫色的脉冲。约 14 格，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from terror violet (#F0E0FF, #B98CF0, #7A4BB8, #4A2A78, #26143F).
Effect: a SMALL DARK PULSE, 4 frames: 1 a small violet flash; 2 a ring of violet light expands from the center; 3 the ring wider and thinner with 3-4 violet sparks; 4 two violet specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nocturne_fx_e_fear.png`：E 恐惧（被吓到的单位头顶，约 1.3 秒），8 帧

被无言恐惧吓到：头顶一团紫黑色的梦魇漩涡，里面两只发白光的眼睛（魔腾的眼睛）一闪一闪地盯着。8 帧约 1.3 秒，第 1 帧出现、第 8 帧散去。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from terror violet (#F0E0FF, #B98CF0, #7A4BB8, #4A2A78, #26143F) with a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a NIGHTMARE TERROR MARK above a head, 8 frames: 1 a small dark violet swirl appears; 2-7 a swirling spiral of dark violet smoke (wider than tall) turning a little each frame, inside it two glowing white slanted eyes that flicker and narrow; 8 the swirl breaks into a few violet specks.
Layout: one horizontal row of 8 equal cells, each 4 wide to 3 tall, image size 2048x192 (each cell 256x192); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `nocturne_fx_w_shroud.png`：W 黑暗庇护：裹住魔腾的暗影屏障（1.5 秒，跟随），9 帧

黑暗庇护：一个暗靛色的烟雾球罩住魔腾，表面流动着几道蓝白色的弧线（像屏障的纹路），边缘卷着烟（参考 W_Shield_Lines、W_Smoke_Twirl、Shield_01_Activate）。1–3 帧烟从脚下卷上来合成球，4–7 帧维持（循环，纹路流动），8–9 帧散开。中间是魔腾，不要画人，球要半透明感：只画球的边缘和纹路，中间留空。约 44 格宽、52 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a DARK SPELL SHIELD round a figure (do NOT draw the figure; leave the middle empty - only the shell's rim and the lines on it), 9 frames: 1-3 dark indigo smoke swirls up from the bottom and closes into a tall oval shell; 4-7 the shell (a seamless loop): a rim of curling dark smoke with 3-4 thin blue-white arcs flowing over its surface, moving each frame; 8-9 the shell breaks into wisps that drift outward and fade.
Layout: one horizontal row of 9 equal cells, each 6 wide to 7 tall, image size 3456x448 (each cell 384x448); the oval centered in every cell, its bottom near the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `nocturne_fx_w_proc.png`：W 挡下攻击后攻速提升，5 帧

黑暗庇护挡下攻击：屏障向外一炸，几道红色和蓝白色的速度线往上冲（表示攻击速度提升）。约 32 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with crimson (#FFF2F2, #FF8A9A, #E8264B, #9B1032, #560F27) and a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a SHIELD BURST round a figure (do NOT draw the figure), 5 frames: 1 a blue-white flash round the middle; 2 a ring of dark smoke bursts outward; 3 several thin crimson and blue-white speed streaks shoot upward round the figure's place; 4 the streaks rise further and thin; 5 a few sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `nocturne_fx_r_burst.png`：R 鬼影重重：黑暗降临（魔腾原地，不跟随，大图），7 帧

放大招：魔腾脚下炸开一大圈黑暗——一道黑紫色的烟浪从他脚下向四周推开（从斜上方看是扁椭圆，宽是高的 2 倍），浪头上一圈蓝白色的光，地面裂开几道暗纹（参考 R_Indicator_Mult、R_Cracks、R_SmokeErode）。中间不要画人。约 96 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with terror violet (#F0E0FF, #B98CF0, #7A4BB8, #4A2A78, #26143F) and a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a WAVE OF DARKNESS bursting out on the ground (a flattened ellipse, twice as wide as tall; do NOT draw a figure), 7 frames: 1 a dark flash at the middle; 2 a ring of black-violet smoke pushes outward with a thin blue-white crest; 3-4 the ring keeps growing, a few dark cracks spread on the ground inside it; 5 the ring at full size, its crest brightest; 6 the ring breaks into rolling smoke; 7 thin wisps at the edge.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 5376x384 (each cell 768x384); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `nocturne_fx_r_veil.png`：R 鬼影重重：队友隐身时的一团暗影（跟随），5 帧

大招让全队隐身：每个队友身上一团暗影烟一裹、往下一沉散掉（表示他们进了黑暗）。中间不要画人。约 28 格宽、34 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) with terror violet (#F0E0FF, #B98CF0, #7A4BB8, #4A2A78, #26143F).
Effect: a SHADOW VEIL around a figure's place (do NOT draw the figure), 5 frames: 1 dark indigo smoke rises at the bottom; 2 the smoke wraps up round the figure's place like a cloak; 3 at full height, a few violet glints; 4 the smoke sinks back down; 5 wisps at the bottom.
Layout: one horizontal row of 5 equal cells, each 7 wide to 8 tall, image size 2240x512 (each cell 448x512); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `nocturne_fx_r_hit.png`：R 落地斩击（目标身上，大图），6 帧

魔腾飞扑落地：目标身上一个大大的红黑色交叉斩痕（X 形，白芯、红边、暗靛色的烟），地面炸开一圈暗影和几道裂纹（参考 R_MissileHead、StrikeShape、R_Cracks）。约 44 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from a crimson ramp (#FFF2F2, #FF8A9A, #E8264B, #9B1032, #560F27) with shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E) and a blue-white glow (#FFFFFF, #CFE6FF, #7FB6FF, #3D6BD9).
Effect: a HEAVY CROSSING SLASH IMPACT, 6 frames: 1 a bright white flash at the center; 2 two long crossing slashes of light (an X, white cores, crimson edges) filling 80% of the cell; 3 the X at full size, a burst of dark indigo shadow round the center and a few dark cracks on the ground below; 4 the X shrinks, the shadow spreads; 5 the shadow breaks into curls; 6 a few dark red specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `nocturne_fx_r_dark.png`：R 鬼影重重：敌方英雄头上的黑雾（出现、循环、散去），10 帧

黑暗笼罩敌人：敌方英雄的头和肩膀周围一圈黑紫色的雾（他们的视野被遮住了）。1–3 帧雾聚起来，4–7 帧循环翻滚，8–10 帧散去。中间（脸）留空，不要挡住脸，只是一圈雾环。约 30 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke or sparks, colours only from terror violet (#F0E0FF, #B98CF0, #7A4BB8, #4A2A78, #26143F) with shadow smoke (#C9D2FF, #7E8BE0, #46509E, #262B5E, #12142E).
Effect: a RING OF DARK MIST round a head (do NOT draw the head; leave the middle clear), 10 frames: 1-3 wisps of black-violet mist gather into a ring (wider than tall); 4-7 the ring (a seamless loop) rolls slowly, its wisps curling; 8-10 the ring breaks up and fades.
Layout: one horizontal row of 10 equal cells, each 5 wide to 3 tall, image size 3200x192 (each cell 320x192); the ring centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nocturne_fx_hit` | view_effects `league_nocturne_hit`（跟随） | 16 |
| `nocturne_fx_p_spin` | view_effects `league_nocturne_p_spin`（施法者身上，跟随） | 84 × 44（半径 40000） |
| `nocturne_fx_p_hit` | view_effects `league_nocturne_p_hit`（跟随） | 18 |
| `nocturne_fx_q_blade` | view_projectiles `league_nocturne_q_blade`（朝右，游戏转到飞行方向） | 20 × 12 |
| `nocturne_fx_q_path` | view_projectiles `league_nocturne_q_path`（地面，大图 league_nocturne_big；游戏转到掷出的方向） | 66 × 10 |
| `nocturne_fx_q_hit` | view_effects `league_nocturne_q_hit`（跟随） | 20 |
| `nocturne_fx_q_dusk` | view_buffs `league_nocturne_q_dusk`（跟随，画在脚下） | 24 × 8 |
| `nocturne_fx_e_grip` | view_effects `league_nocturne_e_grip`（跟随） | 26 |
| `nocturne_fx_e_chain` | view_projectiles `league_nocturne_e_chain`（朝右，游戏转到飞行方向） | 24 × 6 |
| `nocturne_fx_e_tick` | view_effects `league_nocturne_e_tick`（跟随） | 14 |
| `nocturne_fx_e_fear` | view_effects `league_nocturne_e_fear`（跟随，画在人物上面） | 16 × 12 |
| `nocturne_fx_w_shroud` | view_effects `league_nocturne_w_shroud`（施法者身上，跟随） | 44 × 52 |
| `nocturne_fx_w_proc` | view_effects `league_nocturne_w_proc`（施法者身上，跟随） | 32 |
| `nocturne_fx_r_burst` | view_effects `league_nocturne_r_burst`（施法者身上，不跟随，大图） | 96 × 48 |
| `nocturne_fx_r_veil` | view_effects `league_nocturne_r_veil`（每个队友身上，跟随） | 28 × 34 |
| `nocturne_fx_r_hit` | view_effects `league_nocturne_r_hit`（跟随，大图） | 44 |
| `nocturne_fx_r_dark` | view_buffs `league_nocturne_r_dark`（ThreePhase，跟随，画在人物上面） | 30 × 18 |

- `q_path` 的 5–8 帧循环重复到 5 秒（300 tick，`repeat: false` 的投射物画面），`w_shroud` 的 4–7 帧重复到 1.5 秒（90 tick），`e_fear` 8 帧共 80 tick，`r_dark` 的 4–7 帧是 ThreePhase 的 loop。
- 清掉 Codex 给光和烟描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单。
