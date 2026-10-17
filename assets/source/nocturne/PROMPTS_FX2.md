# 魔腾：补做 11 张特效（第 3 步补充，给 Codex）

> **上一轮你拿到的是动作帧包（`nocturne_strips_pack.zip`），不是特效包，所以只按自己的理解做了 8 张特效**（`nocturne_effects_pack_done.zip`：普攻刀光、被动横扫、Q 飞刃、Q 影径、E 灵链、W 护罩、R 飞行黑雾、R 落地冲击）。那 8 张都会用上，做得不错。这一份只要**补齐下面 11 张**。
> - **格式和风格完全照你那 8 张**：每张 4 帧，2×2 排，每格 120×104 游戏像素、放大 8 倍（整张 1920×1664），严格 8×8 方块、二值透明；锚点 (60, 88) 是效果所在单位的**脚底（尾巴尖）**，单位站在锚点上，身高约 40 格（见 `guide/nocturne_fx_guide.png`：淡色的魔腾、锚点、地面、胸口/头部/头顶上方的高度）。
> - **颜色只用你那 8 张的 19 色**（角色色板去掉眼睛的纯白）：#080611 #101029 #171C43 #202952 #284C85 #30437B #33323E #342039 #465DAC #555160 #560F27 #583262 #777680 #794786 #888BA2 #9B1032 #A1A3AA #D3143E #D3D7DC。暗色的烟要有亮一点的蓝边，在暗色地面上也看得见；光、烟、火花不要描黑边。
> - `refs/nocturne_effects_overview.png` 是你那 8 张的总览，**照它的画法**；`refs/nocturne_design.png` 是角色定稿。
> - 「循环」的几张（`q_dusk`、`e_fear`、`r_dark`）4 帧首尾要接得上，游戏会一直重复播放；其余几张从出现到消失播一次。
> - 交付：`nocturne_fx2_<名字>.png`（8 倍）和 `_1x`，`manifest.json`（和上次同样的字段：每帧格子、锚点、bbox、建议时长），`HANDOFF.md`，打成 `nocturne_effects2_pack_done.zip` 放在 outputs 里。

## 11 张特效

| # | 文件 | 内容 | 位置 | 绑定（给 Claude 看） |
|---|---|---|---|---|
| 1 | `nocturne_fx2_hit.png` | 普攻打中敌人 | 敌人胸口（锚点上方约 18 格） | view_effects `league_nocturne_hit`（敌人身上，跟随） |
| 2 | `nocturne_fx2_p_hit.png` | 暗影之刃横扫打中的每个敌人 | 敌人胸口 | view_effects `league_nocturne_p_hit`（敌人身上，跟随） |
| 3 | `nocturne_fx2_q_hit.png` | Q 暗影之刃穿过敌人 | 敌人胸口 | view_effects `league_nocturne_q_hit`（敌人身上，跟随） |
| 4 | `nocturne_fx2_q_dusk.png` | 被 Q 打中的敌方英雄身后拖着影径（循环） | 敌人脚下（锚点） | view_buffs `league_nocturne_q_dusk`（敌人脚下，循环） |
| 5 | `nocturne_fx2_e_grip.png` | E 无言恐惧：灵链抓住目标 | 目标身体（锚点上方约 16 格） | view_effects `league_nocturne_e_grip`（目标身上，跟随） |
| 6 | `nocturne_fx2_e_tick.png` | E 灵链每 0.5 秒的伤害 | 目标胸口 | view_effects `league_nocturne_e_tick`（目标身上，跟随） |
| 7 | `nocturne_fx2_e_fear.png` | E 恐惧：被吓到的单位头顶（循环） | 敌人头顶（锚点上方约 44 格） | view_effects `league_nocturne_e_fear`（敌人身上，跟随，画在人物上面） |
| 8 | `nocturne_fx2_w_proc.png` | W 黑暗庇护挡下攻击：攻速提升 | 魔腾全身（锚点上方） | view_effects `league_nocturne_w_proc`（魔腾身上，跟随） |
| 9 | `nocturne_fx2_r_burst.png` | R 鬼影重重：黑暗降临（魔腾脚下，大） | 魔腾脚下（锚点），向四周推开 | view_effects `league_nocturne_r_burst`（魔腾原地，不跟随） |
| 10 | `nocturne_fx2_r_veil.png` | R 鬼影重重：队友进入黑暗（隐身） | 队友全身（锚点上方） | view_effects `league_nocturne_r_veil`（每个队友身上，跟随） |
| 11 | `nocturne_fx2_r_dark.png` | R 鬼影重重：敌方英雄头上的黑雾（循环） | 敌人头部周围（锚点上方约 30 格） | view_buffs `league_nocturne_r_dark`（敌人身上，循环） |

## 通用提示词（每张都用这一段，最后换成那张的 Effect）

```text
Pixel art game VFX for a small tactics game, in EXACTLY the style of the attached overview of eight effects (the same chunky 8x8 squares, the same dark navy, purple, crimson and silver-grey colours, light blue rims on the dark smoke so it reads on a dark ground): ONLY these 19 colours: #080611 #101029 #171C43 #202952 #284C85 #30437B #33323E #342039 #465DAC #555160 #560F27 #583262 #777680 #794786 #888BA2 #9B1032 #A1A3AA #D3143E #D3D7DC; no pure white; no black outline round light, smoke or sparks; no anti-aliasing, no blur, no semi-transparency. One image, 1920x1664: a 2x2 grid of four equal cells, each 120x104 squares of 8x8 px (960x832 px), frames 1-2 on the top row, 3-4 on the bottom row. In every cell the anchor is square (60, 88) - the feet of the unit the effect sits on (a hero about 40 squares tall standing on it, as in the guide image); place the effect where the line below says, the same place in every frame. Do NOT draw the unit, only the effect. Transparent background (if not possible: pure #FF00FF magenta). No grid lines, no borders, no labels.
Effect: [下面每张的 Effect]
```

### 1. `nocturne_fx2_hit.png`：普攻打中敌人

位置：敌人胸口（锚点上方约 18 格）。

```text
Effect: a SMALL CRIMSON SLASH HIT on an enemy's chest (about 14 squares wide, centred about 18 squares above the anchor): 1 a small silver-grey flash; 2 a short curved crimson slash mark with a silver edge across the chest; 3 the mark at full size with 3-4 crimson sparks flying out; 4 the mark breaks into a few dark red specks.
```

### 2. `nocturne_fx2_p_hit.png`：暗影之刃横扫打中的每个敌人

位置：敌人胸口。

```text
Effect: a CLAW SCRATCH HIT on an enemy's chest (about 16 squares wide, centred about 18 squares above the anchor): 1 a flash; 2 three parallel diagonal scratch marks (crimson with silver edges, dark navy smoke at their ends); 3 the marks at full length, smoke puffing from them; 4 the marks fade into dark red and navy specks.
```

### 3. `nocturne_fx2_q_hit.png`：Q 暗影之刃穿过敌人

位置：敌人胸口。

```text
Effect: a SHADOW BLADE HIT on an enemy's body (about 18 squares wide, centred about 16 squares above the anchor): 1 a blue flash; 2 a burst of dark navy smoke with a crimson slash mark across it; 3 the smoke at full size, the slash brightest, light blue rims on the smoke; 4 the smoke breaks into curls and specks.
```

### 4. `nocturne_fx2_q_dusk.png`：被 Q 打中的敌方英雄身后拖着影径（循环）

位置：敌人脚下（锚点）。

```text
Effect: DARK SMOKE CURLING ON THE GROUND round an enemy's feet (a low flat ring of dark navy smoke wisps, about 24 squares wide and 6 tall, centred on the anchor's row), a seamless 4-frame LOOP: the wisps curl outward to both sides, a few lighter blue highlights, shifting each frame; it must not cover the enemy's body above its feet.
```

### 5. `nocturne_fx2_e_grip.png`：E 无言恐惧：灵链抓住目标

位置：目标身体（锚点上方约 16 格）。

```text
Effect: a SHADOW CLAW GRIP round an enemy's body (about 24 squares wide, centred about 16 squares above the anchor; leave the middle of the body clear): 1 a purple flash; 2 a dark navy shadow claw with long thin fingers reaches up round the body; 3 the claw closes, a twisting purple-and-light-blue flare where it grips; 4 the claw becomes a ring of coiling dark smoke and fades.
```

### 6. `nocturne_fx2_e_tick.png`：E 灵链每 0.5 秒的伤害

位置：目标胸口。

```text
Effect: a SMALL DARK PULSE on an enemy's chest (about 12 squares wide, centred about 18 squares above the anchor): 1 a small purple flash; 2 a ring of purple light expands; 3 the ring wider and thinner with 3-4 purple sparks; 4 two specks. Small - it plays four times in two seconds.
```

### 7. `nocturne_fx2_e_fear.png`：E 恐惧：被吓到的单位头顶（循环）

位置：敌人头顶（锚点上方约 44 格）。

```text
Effect: a NIGHTMARE TERROR MARK above an enemy's head (about 16 squares wide and 12 tall, centred about 44 squares above the anchor, never covering the face), a seamless 4-frame LOOP: a swirling spiral of dark purple smoke turning a little each frame, inside it two small slanted pale grey-white eyes (the #D3D7DC grey, not white) that flicker and narrow.
```

### 8. `nocturne_fx2_w_proc.png`：W 黑暗庇护挡下攻击：攻速提升

位置：魔腾全身（锚点上方）。

```text
Effect: a SHIELD BURST round Nocturne's body (about 32 squares wide, round his body; leave the body clear): 1 a light blue flash round him; 2 a ring of dark navy smoke bursts outward; 3 several thin crimson and light blue speed streaks shoot upward round him; 4 the streaks rise further and fade.
```

### 9. `nocturne_fx2_r_burst.png`：R 鬼影重重：黑暗降临（魔腾脚下，大）

位置：魔腾脚下（锚点），向四周推开。

```text
Effect: a WAVE OF DARKNESS bursting out on the ground round Nocturne (a flattened ellipse twice as wide as tall, centred on the anchor's row, growing to the whole cell width): 1 a dark flash at his feet; 2 a ring of black-navy and purple smoke pushes outward with a thin light blue crest; 3 the ring at full size, a few dark cracks on the ground inside it; 4 the ring breaks into rolling smoke at the edges. Do not draw over his body.
```

### 10. `nocturne_fx2_r_veil.png`：R 鬼影重重：队友进入黑暗（隐身）

位置：队友全身（锚点上方）。

```text
Effect: a SHADOW VEIL round an ally's body (about 28 squares wide and 34 tall, standing on the anchor's row; leave the middle clear, do not draw the ally): 1 dark navy smoke rises at the feet; 2 the smoke wraps up round the body like a cloak, a few purple glints; 3 at full height; 4 the smoke sinks back down into wisps at the feet.
```

### 11. `nocturne_fx2_r_dark.png`：R 鬼影重重：敌方英雄头上的黑雾（循环）

位置：敌人头部周围（锚点上方约 30 格）。

```text
Effect: a RING OF DARK MIST round an enemy's head and shoulders (about 30 squares wide and 14 tall, centred about 30 squares above the anchor; leave the face clear), a seamless 4-frame LOOP: wisps of black-navy and dark purple mist roll slowly round the head, curling, a few lighter navy highlights.
```

## 交回前自查

- [ ] 11 张都在，每张 1920×1664、4 帧、严格 8×8 方块、透明度只有 0 和 255；
- [ ] 只用这 19 色，没有纯白；暗色的烟有亮蓝边；
- [ ] 每张的位置照表（胸口 / 头部 / 头顶上方 / 脚下），没有画人；
- [ ] 循环的三张（`q_dusk`、`e_fear`、`r_dark`）首尾接得上；
- [ ] `manifest.json`、`HANDOFF.md`、zip 都在 outputs 里。
