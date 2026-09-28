# 提莫：给 Codex 的特效提示词

> **这一轮只画 12 张特效图。**
> - 角色不用画：提莫的模型由 Claude 做。头部（帽子、护目镜、羽毛、耳朵、脸）是逐格画的（用户选了方案 A：原版的眯眼笑和一道暗红小嘴），每一帧贴在英雄联盟头部关节的位置；身体用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/teemo_native.png` 只用来参考配色，不要改它。
> - 特效照下面第 1–12 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_teemo.py --raw` 转成原尺寸条，再按技能范围定大小。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「毒性射击」 | 吹出毒镖，命中时附带魔法伤害并让目标中毒 | `teemo_fx_dart` · `teemo_fx_hit` |
| 技能 1 = Q「致盲吹箭」 | 追踪的紫色飞镖，命中造成伤害并致盲 1.5 秒（无法普攻） | `teemo_fx_q_dart` · `teemo_fx_q_hit` · `teemo_fx_blind` |
| 技能 2 = W「小莫快跑」+ 被动「游击队军备」 | 敌人靠近时拔腿就跑：加速 3 秒，伪装（隐身）1.5 秒，随后攻速提高 | `teemo_fx_w_cast` · `teemo_fx_stealth` |
| 大招 = R「种蘑菇」 | 往敌方英雄脚下扔一个蘑菇，落地 1 秒后布置好并潜伏；敌人靠近时爆出毒云，周围敌人中毒 4 秒并减速 | `teemo_fx_r_throw` · `teemo_fx_r_arm` · `teemo_fx_r_trap` · `teemo_fx_r_burst` · `teemo_fx_poisoned` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色：
  - 毒（毒性射击、毒云、中毒）：`#F4FFB0`、`#D2F06A`、`#9ED83A`、`#5FAE2A`、`#2F6E1E`、`#183E14`，点缀紫色孢子 `#E08AF0`、`#B04CC8`；
  - 致盲（Q）：`#F2E6FF`、`#C58CF0`、`#8A4FD0`、`#5A2A96`、`#2E1650`、`#140A24`；
  - 蘑菇：伞盖 `#E4F27A`、`#B6DA3C`、`#7FB022`、`#4A7A16`、`#26420E`，伞盖上的圆斑 `#E08AF0`、`#B04CC8`、`#6A1E7A`，菌柄 `#C8A08A`、`#9E7466`、`#6E4C44`（粉棕色）；
  - 飞镖：木杆 `#8C6B45`、`#5A3A20`，金属头 `#F2D46A`、`#C9A13A`；
  - 烟尘和草叶（W）：`#EBD2A0`、`#C9A36E`、`#8C6B45`，叶子 `#A7B84E`、`#7A8F35`、`#4E6326`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、毒云、标记居中画，不旋转；地面上的圈和毒雾按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `teemo_fx_dart.png`：毒镖（飞行物），3 帧循环

普攻吹出的小毒镖，游戏按方向旋转。约 14 格长、4 格粗。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wood-and-brass dart (#8C6B45, #5A3A20, #F2D46A, #C9A13A) with a toxic green glow (#F4FFB0, #D2F06A, #9ED83A, #5FAE2A).
Effect: a TOXIC BLOWGUN DART flying to the RIGHT, 3 frames, a seamless loop: a short thin wooden dart, its sharp brass point to the RIGHT, a small tuft of fletching at the left end; the point glows toxic green with a white-green core; a short trail of green poison droplets and specks streaming to the left; SYMMETRIC above and below its middle line; only the trail and the glow flicker from frame to frame; frame 3 leads back into frame 1.
Layout: one horizontal row of 3 equal cells, each four times as wide as tall (4:1), image size 1536x128; the dart along the middle height of the cell, dart plus trail about 80% of the cell wide and 30% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `teemo_fx_hit.png`：毒镖命中，5 帧

毒镖扎中目标时一小团毒液溅开。约 18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a toxic green ramp (#F4FFB0, #D2F06A, #9ED83A, #5FAE2A, #2F6E1E) with a few purple spores (#E08AF0, #B04CC8).
Effect: a TOXIC DART HIT, 5 frames: 1 a small white-green flash at the center where the dart strikes; 2 a burst of toxic green liquid splashing outward, bright core; 3 the splash at full size, about 45% of the cell wide, green droplets and two or three purple spores flying out; 4 the droplets fall and fade, a small green puff remains; 5 the last green specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `teemo_fx_q_dart.png`：致盲飞镖（飞行物），4 帧循环

Q 的紫色大飞镖，游戏按方向旋转。约 20 格长、6 格粗。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark venom purple ramp (#F2E6FF, #C58CF0, #8A4FD0, #5A2A96, #2E1650, #140A24).
Effect: a BLINDING DART flying to the RIGHT, 4 frames, a seamless loop: a bigger dart made of dark purple venom, a sharp glowing violet point to the RIGHT with a pale lilac core; behind it a thick swirling trail of dark purple smoke curling in little spirals and streaming to the left; SYMMETRIC above and below its middle line; only the smoke trail and the glow change from frame to frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each four times as wide as tall (4:1), image size 2048x128; the dart along the middle height of the cell, dart plus trail about 90% of the cell wide and 40% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `teemo_fx_q_hit.png`：致盲飞镖命中（跟着目标），5 帧

飞镖命中时溅开一团深紫色的毒墨。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark venom purple ramp (#F2E6FF, #C58CF0, #8A4FD0, #5A2A96, #2E1650, #140A24).
Effect: a BLINDING VENOM SPLASH, 5 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a violet flash hits the head of the space from the LEFT; 2 dark purple venom splashes over the face area in a star-shaped burst, lilac core; 3 the splash at full size, about 45% of the cell wide, drops of dark ink flying to the right; 4 the drops fall, a smear of purple smoke stays around the eyes of the space; 5 the smoke thins and fades.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the splash centered on the head of the empty space, at most 50% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `teemo_fx_blind.png`：致盲标记（敌人头顶），6 帧，无缝循环

被致盲的敌人眼前绕着一圈深紫色的烟雾，持续 1.5 秒（导入时重复两遍）。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark venom purple ramp (#C58CF0, #8A4FD0, #5A2A96, #2E1650, #140A24) with a few lilac sparks (#F2E6FF).
Effect: BLINDED, a dark cloud swirling in front of the eyes, 6 frames, a seamless loop: a small flat band of dark purple smoke wound in a spiral, like a blindfold of smoke, with two or three tiny lilac sparks circling in it; the spiral turns a little each frame and the puffs roll along it; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the cloud centered in every cell, about 55% of the cell wide and 30% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `teemo_fx_w_cast.png`：小莫快跑的起跑烟尘（提莫脚下），5 帧

W 施放时脚下扬起一团尘土，身后几道速度线。约 30 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, dust (#EBD2A0, #C9A36E, #8C6B45) and a few green leaves (#A7B84E, #7A8F35).
Effect: a QUICK DASH START, 5 frames. In the middle of every cell there is an EMPTY small person-sized space (a small person about 40% of the cell height stands there, feet at 80% of the cell height, facing RIGHT) - never draw the person. 1 a puff of dust bursts at the feet of the space, mostly behind it (to the LEFT); 2 the dust spreads backward along the ground, three short horizontal speed lines appear behind the space at knee and waist height; 3 the dust cloud at full size, about 60% of the cell wide, two small leaves kicked up; 4 the speed lines stretch and thin, the dust sinks; 5 the last dust and a leaf fading.
Layout: one horizontal row of 5 equal cells, each twice as wide as tall (2:1), image size 2560x256; the dust on the ground line under the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `teemo_fx_stealth.png`：伪装（提莫隐身），6 帧

提莫进入伪装的一瞬间：绿叶和草屑旋起来把他裹住，一圈亮点闪过。约 28 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, leaves (#A7B84E, #7A8F35, #4E6326) and a pale green shimmer (#F4FFB0, #D2F06A).
Effect: CAMOUFLAGE, a small scout vanishing into the grass, 6 frames. In the middle of every cell there is an EMPTY small person-sized space (a small person about 45% of the cell height stands there, feet at 80% of the cell height) - never draw the person. 1 a ring of small green leaves lifts off the ground around the feet; 2 the leaves spiral upward around the space, a few pale green sparkles; 3 the leaves wrap around the whole space like a whirl, thin white-green shimmer lines inside; 4 a soft flash of pale green over the space, the leaves at the top of the whirl; 5 the leaves drift apart and fall; 6 the last two leaves and sparkles fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `teemo_fx_poisoned.png`：中毒（跟着目标），6 帧

踩到蘑菇的敌人身上冒出毒泡。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a toxic green ramp (#F4FFB0, #D2F06A, #9ED83A, #5FAE2A, #2F6E1E) with a few purple spores (#E08AF0, #B04CC8).
Effect: POISONED, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a green haze clings to the body of the space; 2-5 toxic green bubbles rise from the shoulders and head, pop into small puffs at the top, a few purple spores drift among them; 6 the haze thins, the last bubbles pop.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 50% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `teemo_fx_r_throw.png`：扔出的蘑菇（飞行物），4 帧循环

提莫扔出去的蘑菇，在空中打转。约 12 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a mushroom: bright yellow-green cap (#E4F27A, #B6DA3C, #7FB022, #4A7A16, #26420E) with round magenta spots (#E08AF0, #B04CC8, #6A1E7A) and a thick pinkish-brown stem (#C8A08A, #9E7466, #6E4C44).
Effect: a TOXIC MUSHROOM TUMBLING through the air, 4 frames, a seamless loop: a small round mushroom with a domed yellow-green cap with big round magenta spots and a thick short pinkish-brown stem, turning a quarter turn each frame (cap up, cap right, cap down, cap left), a few green spores trailing behind it; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the mushroom centered in every cell, about 45% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `teemo_fx_r_arm.png`：蘑菇落地布置（落点），6 帧（1 秒）

蘑菇落地、弹一下、长大，然后慢慢隐进草里（最后两帧变暗，像被伪装起来）。约 16 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a mushroom: bright yellow-green cap (#E4F27A, #B6DA3C, #7FB022, #4A7A16, #26420E) with round magenta spots (#E08AF0, #B04CC8, #6A1E7A) and a thick pinkish-brown stem (#C8A08A, #9E7466, #6E4C44), a little grass (#7A8F35, #4E6326).
Effect: a NOXIOUS TRAP being set, 6 frames. The ground is a line at 80% of the cell height; the mushroom stands on it. 1 a small mushroom lands on the ground with a tiny puff of dust; 2 it squashes flat as it lands; 3 it springs up taller than normal; 4 it settles at its full size: a round mushroom about 35% of the cell wide, a domed yellow-green cap with big magenta spots and a thick pinkish-brown stem, two blades of grass at its foot; 5 it dims: the cap turns a darker muted green, the spots dull; 6 even darker, almost hidden, only the top of the cap and two faint spots showing among grass blades.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the mushroom centered horizontally, standing on the ground line at 80% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `teemo_fx_r_trap.png`：潜伏的蘑菇（落点），2 帧循环

布置好的蘑菇在草里潜伏：和第 10 条第 6 帧一样暗，隐约可见。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a hidden mushroom in dark muted colours (#4A7A16, #26420E, #6A1E7A, #6E4C44) among grass blades (#4E6326, #2E3A18).
Effect: a HIDDEN NOXIOUS TRAP waiting, 2 frames, a seamless loop: the same mushroom as in the trap-setting sheet, almost hidden: a dark muted green domed cap with two dull magenta spots, half covered by a few dark grass blades; in frame 2 the grass blades sway a little and one spot glints faintly.
Layout: one horizontal row of 2 equal square cells, image size 512x256; the mushroom centered horizontally, standing on the ground line at 80% of the cell height, about 35% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `teemo_fx_r_burst.png`：蘑菇爆炸（落点），8 帧（约 1 秒）

敌人靠近时蘑菇炸开：一团蘑菇形的毒云升起，同时一圈毒雾沿地面铺开到约 60 格宽（半径 30000），紫色孢子四散。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a toxic green ramp (#F4FFB0, #D2F06A, #9ED83A, #5FAE2A, #2F6E1E, #183E14) with magenta spores (#E08AF0, #B04CC8, #6A1E7A).
Effect: a NOXIOUS TRAP BURSTING into a toxic cloud, 8 frames. The ground is a line at 80% of the cell height. 1 a bright green-white flash where the mushroom stood; 2 a puffy cloud of toxic green gas bursts up in a small mushroom shape, pale core, dark green bottom edge; 3 the cloud swells, and a ring of green mist rolls out along the ground (a flat ellipse twice as wide as tall, 60% of the cell wide); 4 the ring of mist at full size, 90% of the cell wide, the cloud above it big and billowing, magenta spores flying out; 5 the cloud starts to thin, the mist on the ground bubbling; 6 the cloud breaks into several smaller puffs drifting up, the ground mist fading at its edges; 7 thin wisps and floating spores; 8 the last wisps fading.
Layout: one horizontal row of 8 equal cells, each twice as wide as tall (2:1), image size 4096x256; the cloud centered horizontally, the mist ring on the ground line at 80% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，帧时长写在 `native/teemo_cells.json`。特效由 `tools/art/import_teemo.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `teemo_fx_dart.png` | 3 | 投射物 `league_teemo_dart`（普攻） | 3 × 50 循环 |
| `teemo_fx_hit.png` | 5 | 特效 `league_teemo_hit`（普攻命中） | 5 × 50 |
| `teemo_fx_q_dart.png` | 4 | 投射物 `league_teemo_q` | 4 × 50 循环 |
| `teemo_fx_q_hit.png` | 5 | 特效 `league_teemo_q_hit`（跟随目标） | 5 × 60 |
| `teemo_fx_blind.png` | 6 | 特效 `league_teemo_blind`（跟随目标，1.5 秒） | 6 × 125，重复两遍 |
| `teemo_fx_w_cast.png` | 5 | 特效 `league_teemo_w_cast`（跟随提莫，地面） | 5 × 70 |
| `teemo_fx_stealth.png` | 6 | 特效 `league_teemo_stealth`（跟随提莫） | 6 × 80 |
| `teemo_fx_poisoned.png` | 6 | 特效 `league_teemo_poisoned`（跟随目标） | 6 × 100 |
| `teemo_fx_r_throw.png` | 4 | 投射物 `league_teemo_r_throw`（抛物线 0.33 秒） | 4 × 80 循环 |
| `teemo_fx_r_arm.png` | 6 | 特效 `league_teemo_r_arm`（落点，1 秒） | 80，80，120，120，300，300 |
| `teemo_fx_r_trap.png` | 2 | 特效 `league_teemo_r_trap`（落点，每 0.25 秒一段，最多 12 秒） | 2 × 125 |
| `teemo_fx_r_burst.png` | 8 | 特效 `league_teemo_r_burst`（落点，半径 30000） | 8 × 120 |

特效表：`league_teemo_fx`（dart、hit、q_dart、q_hit、blind、w_cast、stealth、poisoned），`league_teemo_big`（r_throw、r_arm、r_trap、r_burst）。
