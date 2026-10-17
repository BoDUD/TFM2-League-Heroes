# 布隆（弗雷尔卓德之心）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了：`design/braum_design.png`（你第 0 步画的 A 版原稿逐格读回，**134 × 121 格、48 色**，这里每格 6 × 6 px）。它就是待机，**待机不用画**。用户：「参考英雄联盟里的动作帧吧 现在这个只能算待机姿势」——其余动作照英雄联盟里布隆的动作画。
> - **每帧一张图**：`now/braum_<动作>_<n>.png` 是**骨架**——英雄联盟里布隆这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 163 行的下边），**蓝线 = 造型站直时的头顶**（第 43 行），**蓝十字 = 站位点**（第 110 列，两脚中间），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/braum_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势。**人和盾都和造型一样大**：站直时头顶到脚底 121 格，盾高 92 格、宽 64 格；不要画大也不要画小。
> - **头每帧都是造型的头**：光头、八字胡、眉毛、眼睛、胡茬、坠子逐格照抄造型（第 0–30 行那一块），只平移，脸朝右前方；不要重新画一张脸。
> - **盾就是造型里的那面盾**（金框、横梁回纹、羊头、发光的青蓝眼睛和宝石、棕色皮带）：整块照抄，只能平移，或者在下面写明的几帧里整块转 90 度平放；**不能歪、不能斜、不能变形、不能缩放**。
> - **盾在哪一边**：英雄联盟里盾挂在他另一只手上（骨架图里盾在画面左边、挡在他身前）。**我们的布隆盾永远在他远侧的手臂上、画面右边、他的身前**（和造型一样）——身体、腿、近侧手臂照骨架动，盾按下面每帧写的位置画，**不要照骨架把盾画到左边**。
> - 腿：近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、暗一档、略高。跑步一前一后交叉迈步。
> - 每格 6 × 6 px 一个纯色方块，所有格子对齐同一个网格（`design/braum_design_on_canvas.png` 的格子）；**只用造型的 48 色**（`design/braum_palette.png`）；一圈 1 格近黑描边；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（冰、冲击波、裂隙、光、尘土），只画人和盾；**不画骨架图里他脚边的小魄罗**；**红线以下什么都不能有**；出招一律朝画面右边。
> - 交付到 `outputs/braum-strips/`：每帧 `braum_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `braum_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`braum_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**；一个动作里的几帧，**画后一帧时附上前一帧**，让人、盾、头一样大。

## 要画的帧（38 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架；盾按这里） |
|---|---|---|
| `braum_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，盾竖着挂在远侧手臂上、在身前（画面右边），离地几格，随步子上下颠；腿照骨架一前一后交叉，近侧手臂前后摆 |
| `braum_attack_1.png` | 普攻：盾击 | 准备：身体微微后仰，把盾往怀里收（盾仍竖着在画面右边） |
| `braum_attack_2.png` | | 蓄力到底：盾收到最靠近胸口，近侧拳头抬起 |
| `braum_attack_3.png` | | 出击：向右前冲，远侧手臂伸直把盾往右推出去，身体前倾 |
| `braum_attack_4.png` | | 命中：盾推到最右，身体完全压上去，两脚分开踩稳（骨架的站姿） |
| `braum_attack_5.png` | | 收招：回到造型的站姿 |
| `braum_skill_1.png` | Q 寒冬之咬 | 扭身，把盾往身后一侧（远侧）抡 |
| `braum_skill_2.png` | | 盾从后往前划弧 |
| `braum_skill_3.png` | | 盾在胸口高度向右甩出，羊头朝右——冰从盾里飞出的那一刻（冰不画） |
| `braum_skill_4.png` | | 保持甩出的姿势，身体前倾 |
| `braum_skill_5.png` | | 收回到站姿 |
| `braum_skill2_1.png` | E 坚不可摧 | 把盾从地上提起来 |
| `braum_skill2_2.png` | | 盾举在身前（画面右边、胸口高度），两只手握着，羊头朝外；他蹲在盾后面，盾上面露出头和毛皮披肩，盾下面露出腿 |
| `braum_skill2_3.png` | | 同样的姿势撑住（这一帧会一直停着） |
| `braum_w_leap_1.png` | W 挺身而出 | 下蹲准备起跳，盾在远侧手臂上 |
| `braum_w_leap_2.png` | | 向右前上方跃起，盾举在身前 |
| `braum_w_leap_3.png` | | 空中，收腿，盾在前 |
| `braum_w_leap_4.png` | | 落地，屈膝，盾立在身前地上 |
| `braum_w_leap_5.png` | | 站起来 |
| `braum_ult_1.png` | R 冰川裂隙 | 两手抓住盾 |
| `braum_ult_2.png` | | 两手把盾举过头顶，**盾整块转 90 度横着**举在头上 |
| `braum_ult_3.png` | | 小跳一下，盾举到最高 |
| `braum_ult_4.png` | | 把盾砸到身前（画面右边）的地上：**盾整块转 90 度平躺在地上**，他弯腰压在盾上 |
| `braum_ult_5.png` | | 砸地的一刻：蹲到最低，两手按在平躺的盾上 |
| `braum_ult_6.png` | | 站起来，盾还平躺在身前地上 |
| `braum_dead_1.png` | 死亡 | 被打中，踉跄后退，盾往下滑 |
| `braum_dead_2.png` | | 向后倒，盾往画面右边倒下 |
| `braum_dead_3.png` | | 膝盖一软，倒下 |
| `braum_dead_4.png` | | 背着地摔在地上 |
| `braum_dead_5.png` | | 仰躺在地上，盾平躺在他旁边（画面右边） |
| `braum_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/braum_<动作>_<n>.png`（骨架）
2. `design/braum_design.png`（造型）
3. `design/braum_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/braum_picture_A.png`（原画，看长相）

```text
Image 2 is the final pixel-art design of this character: Braum, a huge bald Freljord strongman with a big dark-brown handlebar moustache, pink skin with mauve tattoo bands, a white fur mantle on a blue-steel pauldron, a gold-rimmed round belt buckle, dark-brown trousers, grey fur below the knees, dark blue-grey boots, and his huge door-like shield (slate-grey slab, gold frame and crossbar, a dark-steel ram's head with glowing cyan eyes and gem). It is drawn on a grid of 6x6-pixel squares, 134 x 121 squares, 48 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions. (Image 4, when attached, is the previous frame of the same action: keep the character exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 6-pixel grid as Image 3, every square one flat colour from Image 2's 48 colours; the character exactly as big as Image 2 (121 squares from the crown to the soles when standing); his head copied square for square from Image 2 (the same face turned to the right, only moved); the shield copied square for square from Image 2, only moved (or, where this frame says so, turned a quarter turn as one piece) - never tilted, bent or scaled; the shield is ALWAYS on his far arm on the image right in front of him, NOT on the image left as in the 3D render; the near leg on the image left in full tone, the far leg on the image right one shade darker; the soles on the red line of the guide (square row 163), nothing below it; a 1-square near-black outline; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no ice, no shockwave, no cracks, no glow, no dust), no small creature, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文，例如：

- run：`running to the right, frame <n> of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the shield upright on his far arm in front of him (image right), lifted a few squares off the ground, bobbing with the stride`
- attack 1–5：`shield bash, frame <n> of 5: <1: leaning back a little, pulling the shield in toward his body | 2: the wind-up's peak, the shield drawn in closest to his chest, the near fist raised | 3: lunging forward to the right, the far arm shoving the shield out to the right, the body leaning in | 4: the hit, the shield at its farthest right, his weight fully behind it, feet wide as in Image 1 | 5: recovering toward the standing pose of Image 2>`
- skill 1–5：`Winter's Bite (he flings ice from his shield), frame <n> of 5: <1: twisting, swinging the shield back to his far side | 2: swinging the shield forward in an arc | 3: the shield flung out to the right at chest height, the ram's face toward the right - the moment the ice flies (do not draw the ice) | 4: holding the thrust, leaning forward | 5: recovering to the standing pose>`
- skill2 1–3：`Unbreakable, frame <n> of 3: <1: lifting the shield off the ground | 2: the shield raised in front of him on the image right at chest height, held with both hands, the ram's face outward; he crouches behind it, his head and fur mantle showing above it and his legs below it | 3: the same braced stance, held>`
- w_leap 1–5：`leap to an ally, frame <n> of 5: <1: crouching to jump, the shield on his far arm | 2: leaping forward and up to the right, the shield held in front | 3: in the air, legs tucked, the shield in front | 4: landing with bent knees, the shield planted upright on the ground in front of him | 5: standing up>`
- ult 1–6：`Glacial Fissure, frame <n> of 6: <1: gripping the shield with both hands | 2: lifting the shield high over his head with both hands, the shield turned a quarter turn as one piece so it lies flat above him | 3: a short hop, the shield at its highest above his head | 4: slamming the shield down onto the ground in front of him (image right): the shield lying flat on the ground (a quarter turn, one piece), he bends over it | 5: the impact, crouched lowest, both hands on the flat shield | 6: rising, the shield still lying flat on the ground in front of him>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, staggering back, the shield slipping | 2: falling backward, the shield toppling to the image right | 3: his knees giving way | 4: landing on his back on the ground | 5: lying on his back on the ground, the shield lying flat beside him on the image right | 6: the same, still (the last frame)>`

## 交回前请检查

- 38 帧都在，文件名对，每张 1536×1024 透明底、6 px 一格，`_1x` 和大图逐格一致。
- 人和盾在每帧都和造型一样大（站直 121 格高）；头是造型的头（同一张脸）；盾是造型的盾，竖直不歪（R 和死亡写明的几帧整块平放）。
- **盾在画面右边、他身前**（不是骨架里的左边）。
- 脚底在红线上，红线以下没有东西；没有特效、没有小魄罗、没有文字和格子线。
- 全部画完后最后写 `outputs/braum-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 6 px 格读回（regrid --size 6），颜色贴回造型的 48 色；头和盾按造型逐格贴回（一张脸贯穿所有帧，盾刚体）；腿查变形和缝（rig-deformation-checks、gap-check）；外描边加粗到约 1 游戏像素；待机 = 造型 + 呼吸；受击 = 造型平移 + 闪白。
- 写 assets/source/ppu/braum_<tag>.png/.json、1x 表、ppu_hd.py PPU、hd.rs HEROES（league.dll 0.6.11，先问「修正模型」）；6 倍 / 游戏尺寸逐帧自查后再给用户看 GIF。
