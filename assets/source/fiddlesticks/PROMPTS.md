# 远古恐惧 费德提克：给 Codex 的特效提示词

> **这一轮只画 13 张特效图。**
> - 角色不用画：费德提克的模型由 Claude 做（麻袋头逐格画好贴在头部骨骼上，身体用英雄联盟原版动画重新上色，`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/fiddlesticks_native.png` 只用来参考配色和人物大小（约 40 格高：白色蛋形麻袋头、一只红眼、满口尖牙的大嘴、头顶暗紫色羽刺；黑紫色的瘦长身体和高跷腿，麻布袖子，身后拖一把锈红刀刃的长镰刀），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里费德提克自己的特效贴图（Q 的乌鸦和幽灵稻草人、恐惧螺旋眼、夜割的新月印记和橙色地裂、吸魂触须、大招的鸦群符文和羽毛、焦油色渐变），只在本地用，不要提交。
> - 特效照下面第 1–13 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_fiddlesticks.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「巫骇草人」 | 远程射出一道焦油色的小弯刃；3 秒没有行动后，第一次普攻或夜割会恐惧命中的英雄 1 秒 | `fiddlesticks_fx_bolt` · `fiddlesticks_fx_hit` · `fiddlesticks_fx_fear` |
| 技能 1 = Q「恐惧」 | 放出一只乌鸦扑向目标，吓得它逃跑 1.25 秒 | `fiddlesticks_fx_q_crow` · `fiddlesticks_fx_q_hit` · `fiddlesticks_fx_fear` |
| 技能 2 = W「五骨丰登」+ E「夜割」 | 先在目标处挥出一道新月形的斩击（减速，正中心沉默），再原地引导 2 秒，吸取周围所有敌人的灵魂 | `fiddlesticks_fx_e_reap` · `fiddlesticks_fx_silence` · `fiddlesticks_fx_w_souls` · `fiddlesticks_fx_w_drain` · `fiddlesticks_fx_w_final` |
| 大招 = R「群鸦风暴」 | 引导 1 秒（落点出现鸦群印记），化成一群乌鸦飞走，传送到落点；鸦群绕着他盘旋 5 秒，落地时恐惧周围英雄 | `fiddlesticks_fx_r_mark` · `fiddlesticks_fx_r_depart` · `fiddlesticks_fx_r_storm` · `fiddlesticks_fx_fear` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（都从英雄联盟费德提克的特效里取）：
  - 焦油暗色（阴影、烟、乌鸦）：`#120A10`、`#24141E`、`#3A2230`、`#5A3446`；乌鸦身上的紫色光泽 `#2A2238`、`#4A3C60`；
  - 暗红（血色、符文、眼睛）：`#4E0E14`、`#8A1A1E`、`#C42A22`、`#FF4A30`；
  - 余烬橙（斩击边缘、地裂、火星）：`#E8561E`、`#FF8A2A`、`#FFC050`、`#FFEFB0`（白热的芯）；
  - 灵魂白（被吸出的魂、幽灵稻草人）：`#F4F0DC`、`#D8D0A8`、`#A89C74`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。乌鸦要画成**从上往下看**的样子（翅膀一上一下张开），这样转过来也不会肚皮朝天。
- 命中、爆裂、标记居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在费德提克身上的特效（吸魂、化鸦飞走、鸦群风暴）：格子中间留出一个空的人形位置（按那条写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `fiddlesticks_fx_bolt.png`：普攻弯刃（飞行），4 帧循环

费德提克甩出的一道小弯刃：一弯焦油色的新月（凸面朝前），边缘一线暗红，后面拖着黑烟和两三颗橙色火星。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a tar-dark ramp (#120A10, #24141E, #3A2230, #5A3446), a dark red ramp (#4E0E14, #8A1A1E, #C42A22) and ember accents (#FF8A2A, #FFC050).
Effect: a small dark CRESCENT BLADE of shadow flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. At the right part of the cell a crescent about 70% of the cell tall, bulging toward the RIGHT: a tar-black body, a thin dark red inner rim and a brighter red outer edge; behind it to the left a short trail of black smoke puffs and two or three tiny orange ember squares that flicker from frame to frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 1024x170 (each cell 256x170); the crescent at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `fiddlesticks_fx_hit.png`：普攻命中，5 帧

弯刃打中目标：一圈黑烟向外炸开，中间闪一下暗红，飞出几颗橙色火星（像原版的焦油冲击环）。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a tar-dark ramp (#120A10, #24141E, #3A2230, #5A3446), a dark red ramp (#4E0E14, #8A1A1E, #C42A22) and ember accents (#FF8A2A, #FFC050, #FFEFB0).
Effect: a SHADOW HIT, 5 frames: 1 a small dark red flash at the center with a white-hot dot; 2 a ragged ring of black smoke about 40% of the cell wide bursting out, red inside; 3 the ring at 65% of the cell wide, jagged like torn cloth, four ember squares flying out diagonally; 4 the ring breaking into black smoke puffs, embers further out; 5 two or three puffs and one ember fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `fiddlesticks_fx_q_crow.png`：恐惧的乌鸦（飞行，从上往下看），4 帧循环

Q 放出的乌鸦扑向目标：**从上往下看**的一只黑乌鸦，头朝右，翅膀一上一下张开拍动，头两侧各一点红眼，身后几片散落的黑羽。约 16 格长、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, crow blacks with a violet sheen (#14101A, #2A2238, #4A3C60), red eyes (#FF4A30) and a dark red accent (#8A1A1E).
Effect: a CROW seen from ABOVE (top-down view) flying to the RIGHT, 4 frames, a seamless flapping loop, SYMMETRIC above and below the middle line: the body a black oval along the middle line, the head and pointed beak at the right, one tiny red eye on each side of the head; the two wings spread one UP and one DOWN from the body (mirror images of each other), black with violet highlights on the feather edges; frame 1 wings fully spread, frame 2 wings swept back, frame 3 wings folded close to the body, frame 4 wings swept forward; two or three loose black feathers trailing behind to the left.
Layout: one horizontal row of 4 equal cells, each 1 wide to 1 tall, image size 1024x256 (each cell 256x256); the crow in the middle of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `fiddlesticks_fx_q_hit.png`：恐惧命中，6 帧

乌鸦扑中目标的一下：一个灵魂白色的幽灵稻草人脸（麻袋头、张开的锯齿大嘴、一只红眼，像原版的 Q 幽灵）从目标身上猛地冒出来尖叫，周围炸开黑色的触须和羽毛，然后散掉。约 26 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, soul whites (#F4F0DC, #D8D0A8, #A89C74), a tar-dark ramp (#120A10, #24141E, #3A2230), a dark red ramp (#8A1A1E, #C42A22, #FF4A30).
Effect: TERRIFY IMPACT on an enemy, 6 frames: 1 a black crow shape hits the center with a dark red flash; 2 a pale ghostly SCARECROW FACE bursts up out of the center, a pointed burlap-sack head with one glowing red eye and a huge open jagged mouth of sharp teeth, about 50% of the cell tall, black tentacle wisps whipping out around it; 3 the ghost face at its biggest, 70% of the cell tall, screaming (mouth widest), black feathers and wisps flying out; 4 the face stretching upward and thinning, its edges tearing into pale strands; 5 the face dissolving into rising pale wisps, a few black feathers; 6 the last wisps and one feather fading.
Layout: one horizontal row of 6 equal cells, each 4 wide to 5 tall, image size 1536x320 (each cell 256x320); centered across every cell, the burst center at 60% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `fiddlesticks_fx_fear.png`：恐惧标记（跟着目标，头顶，循环），6 帧

被恐惧的单位头顶：一只灵魂白色的螺旋"恐惧之眼"（像原版的 Q 螺旋眼：一只竖起的眼睛，瞳孔是一圈螺旋），一只小黑乌鸦绕着它转。这张会连续播放（1.25 秒内放两遍），最后一帧要能接回第一帧。约 16 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, soul whites (#F4F0DC, #D8D0A8, #A89C74), a dark red ramp (#4E0E14, #8A1A1E, #C42A22), crow blacks (#14101A, #2A2238).
Effect: FEAR MARK above a frightened unit's head, 6 frames, a seamless loop: in the center an upright almond-shaped eye about 45% of the cell wide, pale bone-white, its pupil a dark red SPIRAL that turns one step each frame; the eye trembles slightly (one pixel up or down every other frame); a tiny black crow (a few pixels, wings spread) circles around the eye, at the left in frame 1, above in frame 2, at the right in frame 3, below and in front in frame 4, back to the left in frame 6.
Layout: one horizontal row of 6 equal cells, each 8 wide to 7 tall, image size 1536x224 (each cell 256x224); the eye at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `fiddlesticks_fx_silence.png`：沉默标记（跟着目标，头顶，循环），4 帧

被夜割正中心沉默的英雄头顶：一张被粗线缝死的嘴（一道暗红的横线，上面交叉着三针灵魂白色的缝线，像费德提克的麻袋缝线），轻轻颤动。这张会连续播放，最后一帧要能接回第一帧。约 12 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark red ramp (#4E0E14, #8A1A1E, #C42A22), soul whites (#F4F0DC, #D8D0A8).
Effect: SILENCE MARK above a unit's head, 4 frames, a seamless loop: a STITCHED-SHUT MOUTH symbol about 80% of the cell wide: a thick horizontal dark red line with slightly curved ends, crossed by three short pale X-shaped stitches evenly spaced along it; the whole symbol twitches a pixel up in frame 2 and a pixel down in frame 4, the stitches pulling tight in frame 3.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `fiddlesticks_fx_w_drain.png`：五骨丰登吸魂（每个被吸的敌人身上，每 0.25 秒一次），4 帧

被吸的敌人身上：一缕灵魂白色的魂从胸口被扯出来，往上飘，一条暗红的细触须缠着它。约 14 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, soul whites (#F4F0DC, #D8D0A8, #A89C74), a dark red ramp (#4E0E14, #8A1A1E, #C42A22), tar dark (#24141E).
Effect: SOUL DRAIN on an enemy, 4 frames: 1 a small pale wisp appears at the lower middle of the cell (the chest of the unit), a thin dark red tendril curling around it; 2 the wisp stretches upward into a thin ghostly strand about half the cell tall, the tendril spiralling with it; 3 the strand at full length, its top a small pale soul shape with two dark eye dots, the red tendril pulling it up; 4 the strand snapping and fading upward in pale squares.
Layout: one horizontal row of 4 equal cells, each 1 wide to 2 tall, image size 512x512 (each cell 128x256); the wisp's start at 70% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `fiddlesticks_fx_w_final.png`：五骨丰登最后一下（每个被吸的敌人身上），6 帧

引导结束时的收割：一个完整的灵魂白色人形魂影被猛地从敌人身上撕出来，暗红色的光一闪，魂影被扯成碎片飞散。约 24 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, soul whites (#F4F0DC, #D8D0A8, #A89C74), a dark red ramp (#4E0E14, #8A1A1E, #C42A22, #FF4A30), tar darks (#120A10, #24141E).
Effect: HARVEST, the final soul rip on an enemy, 6 frames: 1 a dark red flash at the middle of the cell (the unit's chest) with a jagged black ring; 2 a pale ghostly human-shaped soul silhouette, about 60% of the cell tall, is torn upward out of the center, its arms stretched up; 3 the soul at the top half of the cell, stretched and screaming, dark red tendrils ripping at its lower edge; 4 the soul tearing apart into three pale shreds, red sparks; 5 the shreds flying up and out; 6 the last pale squares fading.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1536x341 (each cell 256x341); the burst center at 65% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `fiddlesticks_fx_e_reap.png`：夜割的新月斩击（地面，按施法方向转），6 帧

在目标位置挥出的一道新月形斩击，躺在地上：一弯焦油黑的新月（凸面朝右，上下对称），前缘一线余烬橙的亮边，弧上刻着几个暗红符文，后面拖着黑色的爪痕烟迹，最后化成焦油烟散掉。约 30 格宽、60 格高（**图会按施法方向转，向左施放时整张转 180°**）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a tar-dark ramp (#120A10, #24141E, #3A2230, #5A3446), a dark red ramp (#4E0E14, #8A1A1E, #C42A22) and an ember ramp (#E8561E, #FF8A2A, #FFC050, #FFEFB0).
Effect: REAP, a giant crescent scythe slash LYING ON THE GROUND, seen from a 3/4 top-down view, 6 frames, SYMMETRIC above and below the middle line (it is rotated 180 degrees when cast to the left). The crescent spans the full cell height and bulges toward the RIGHT, about 40% of the cell wide at its thickest (the middle), tapering to sharp points at the top and bottom. 1 a thin bright orange line sweeps across the right edge of the arc (the leading edge), only its middle drawn; 2 the full crescent appears: a tar-black body, a white-hot to orange leading edge on the right, a thin dark red inner edge on the left; 3 the crescent at full strength, three small jagged dark red sigils glowing along its middle, black claw-like streaks trailing to the left, a thin orange crack glowing on the ground along the arc; 4 the edge dims to red, the body begins to break into black smoke puffs; 5 the crescent shredding into smoke drifting left, the crack cooling to dark red; 6 a few smoke puffs and one faint red crack line.
Layout: one horizontal row of 6 equal cells, each 1 wide to 2 tall, image size 768x512 (each cell 128x256); the crescent's middle at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `fiddlesticks_fx_w_souls.png`：五骨丰登引导（套在费德提克身上，循环），4 帧

费德提克引导吸魂的 2 秒里：一缕缕灵魂白色的魂从四周被拉向他的胸口，暗红色的光在他身前旋转，脚下一圈暗红的地面光环。这张会连续播放，最后一帧要能接回第一帧。约 48 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, soul whites (#F4F0DC, #D8D0A8, #A89C74), a dark red ramp (#4E0E14, #8A1A1E, #C42A22, #FF4A30), tar darks (#24141E, #3A2230).
Effect: BOUNTIFUL HARVEST CHANNEL, souls being sucked in toward an EMPTY person-sized space (a thin person about 80% of the cell tall stands in the middle, feet at 90% of the cell height, chest at 45% - never draw the person), 4 frames, a seamless loop: six thin pale ghostly wisps curve in from the edges of the cell toward the chest point, each wisp moving one step closer every frame (a new wisp starts at the edge when one arrives); a small dark red glow pulses at the chest point; a thin dark red ring on the ground around the feet (a flat ellipse, twice as wide as tall, 70% of the cell wide). Keep the middle mostly clear.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the feet at 90% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `fiddlesticks_fx_r_mark.png`：群鸦风暴落点印记（地面，1 秒），8 帧

引导的 1 秒里，落点地上出现的预警：一个扁的暗红符文圈（像原版大招的符文和爪痕），圈里几只乌鸦的影子开始盘旋，越来越亮，最后一帧一闪。约 90 格宽、45 格高（地面的扁椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark red ramp (#4E0E14, #8A1A1E, #C42A22, #FF4A30), tar darks (#120A10, #24141E, #3A2230) and an ember accent (#FF8A2A).
Effect: CROWSTORM LANDING MARK on the ground, a flat ellipse seen from a 3/4 top-down view (twice as wide as tall, filling 95% of the cell), 8 frames over one second: 1 a faint thin dark red ring; 2-3 the ring thickens and jagged dark red sigils like scratched runes appear around it one by one, three claw-scratch marks inside; 4-5 dark shadows of crows (small black V shapes) begin circling inside the ring, the sigils glowing brighter red; 6-7 the crow shadows speed up and multiply, the ring's inner edge glowing orange; 8 the brightest frame: the whole ring flashing red-orange, the crow shadows at the rim.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 2048x128 (each cell 256x128); the ellipse centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `fiddlesticks_fx_r_depart.png`：化鸦飞走（起点，套在人形上），6 帧

传送时费德提克原地化成一群乌鸦飞散：一团黑烟里窜出一群黑乌鸦和羽毛，向上、向四周散开。约 48 格宽、56 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, crow blacks with a violet sheen (#14101A, #2A2238, #4A3C60), red eyes (#FF4A30), tar darks (#120A10, #24141E, #3A2230).
Effect: DISSOLVING INTO CROWS, where a thin person-sized figure stood (about 70% of the cell tall, feet at 90% of the cell height - never draw the person), 6 frames: 1 a column of black smoke the size of the person with a few red eye dots inside; 2 the column bursts: eight small black crows in side view (wings up or down, one red eye each) burst out of it; 3 the crows fly outward and upward in all directions, black feathers swirling; 4 the crows near the top and sides of the cell, the smoke thinning; 5 three crows flying off the cell edges, feathers drifting down; 6 only a few falling feathers.
Layout: one horizontal row of 6 equal cells, each 6 wide to 7 tall, image size 1536x299 (each cell 256x299); the feet at 90% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `fiddlesticks_fx_r_storm.png`：群鸦风暴（套在费德提克身上，循环），6 帧

大招的 5 秒里绕着他盘旋的鸦群：十几只黑乌鸦（侧面，红眼）在他周围一个扁椭圆上绕圈飞，有高有低（从脚边到头顶上方），羽毛乱飞，脚下一圈暗红的光。这张会连续播放，最后一帧要能接回第一帧。约 90 格宽、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, crow blacks with a violet sheen (#14101A, #2A2238, #4A3C60), red eyes (#FF4A30), a dark red ramp (#4E0E14, #8A1A1E, #C42A22).
Effect: CROWSTORM, a murder of crows circling around an EMPTY person-sized space (a thin person about 60% of the cell tall stands in the middle, feet at 85% of the cell height - never draw the person), 6 frames, a seamless loop: about fourteen small black crows in side view (wings up or down, a red eye dot each) fly around the person along a wide flat ellipse (the ellipse 95% of the cell wide, its center at the person's waist), at different heights from the feet to above the head; crows passing in front of the person are drawn bigger, crows behind are smaller and never cover the middle; every frame each crow moves one sixth of the way around the ellipse (counter-clockwise) and flaps; black feathers tumble; a thin dark red glow ring on the ground around the feet (a flat ellipse, 80% of the cell wide).
Layout: one horizontal row of 6 equal cells, each 3 wide to 2 tall, image size 1536x341 (each cell 256x171); the feet at 85% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，麻袋头从 `native/fiddlesticks_native.png` 贴在头部骨骼上，帧时长写在 `native/fiddlesticks_cells.json`。特效由 `tools/art/import_fiddlesticks.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `fiddlesticks_fx_bolt.png` | 4 | 投射物 `league_fiddlesticks_bolt`（普攻，朝飞行方向转） | 4 × 60 循环 |
| `fiddlesticks_fx_hit.png` | 5 | 特效 `league_fiddlesticks_hit`（普攻命中，跟随目标） | 5 × 50 |
| `fiddlesticks_fx_q_crow.png` | 4 | 投射物 `league_fiddlesticks_q_crow`（Q，朝飞行方向转） | 4 × 60 循环 |
| `fiddlesticks_fx_q_hit.png` | 6 | 特效 `league_fiddlesticks_q_hit`（跟随目标） | 6 × 60 |
| `fiddlesticks_fx_fear.png` | 6 | 特效 `league_fiddlesticks_fear`（恐惧，头顶，跟随目标；放两遍 = 1.2 秒） | 12 × 100 |
| `fiddlesticks_fx_silence.png` | 4 | 特效 `league_fiddlesticks_silence`（沉默，头顶，跟随目标；1.25 秒） | 12 × 104 |
| `fiddlesticks_fx_w_drain.png` | 4 | 特效 `league_fiddlesticks_w_drain`（每 0.25 秒一次，跟随目标） | 4 × 62 |
| `fiddlesticks_fx_w_final.png` | 6 | 特效 `league_fiddlesticks_w_final`（引导结束，跟随目标） | 6 × 60 |
| `fiddlesticks_fx_e_reap.png` | 6 | 投射物 `league_fiddlesticks_e_reap`（夜割范围，半径 30000，按施法方向转） | 6 × 66 |
| `fiddlesticks_fx_w_souls.png` | 4 | 特效 `league_fiddlesticks_w_souls`（引导中每 0.25 秒一次，跟随费德提克） | 4 × 62 |
| `fiddlesticks_fx_r_mark.png` | 8 | 特效 `league_fiddlesticks_r_mark`（落点，地面，1 秒） | 8 × 125 |
| `fiddlesticks_fx_r_depart.png` | 6 | 特效 `league_fiddlesticks_r_depart`（起点，不跟随） | 6 × 70 |
| `fiddlesticks_fx_r_storm.png` | 6 | 特效 `league_fiddlesticks_r_storm`（每 0.5 秒一次，跟随费德提克，半径 45000） | 6 × 83 循环 |

特效表：`league_fiddlesticks_fx`（bolt、hit、q_crow、q_hit、fear、silence、w_drain、w_final），`league_fiddlesticks_big`（e_reap、w_souls、r_mark、r_depart、r_storm）。
