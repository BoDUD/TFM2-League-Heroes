# 赛恩（亡灵战神）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了：`design/sion_design.png`（你画的正面原稿 A 逐格读回，**101 × 75 格、27 色**，这里每格 7 × 7 px；游戏里约 1.5 格 = 1 个游戏像素）。它就是待机，**待机不用画、跑步不用画**（跑步我这边用造型自己的腿做）。其余动作照英雄联盟里赛恩的动作画，**全部 3/4 正面朝右**（和造型同一个角度：脸、胸口、肚子上的熔炉朝向看画的人；用户定的，不画侧身）。
> - **每帧一张图**：`now/sion_<动作>_<n>.png` 是**骨架**——英雄联盟里赛恩这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 140 行的下边），**蓝线 = 造型站直时的最高处（头顶断剑）**，**蓝十字 = 站位点**（第 100 列，两脚中间），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/sion_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势。**和造型一样大**：站直时光头顶到脚底 67 格、头顶断剑到脚底 75 格；不要画大也不要画小。
> - **头每帧都是造型的头**：小光头、两只红眼、黑铁下颌笼 + 尖刺、头顶断剑 + 红飘带，逐格照抄造型，只平移；不要重新画一张脸，也不要画侧脸、背影。
> - **身体始终正面朝向看画的人**：骨架里身体转过去露出后背的帧（比如普攻挥到底），只照它的手臂和斧头的位置画，身体、熔炉、腰带仍然朝前。
> - **巨斧是刚体**：宽弧形钢斧刃 + 缠皮条的长柄 + 骨环 + 铁箍，形状、长度、颜色和造型一样；只整块平移或旋转到骨架的方向，不要拉长、缩短、弯曲；斧头不能挡住脸和熔炉。
> - **远侧肩甲**（画面右边、三根尖角的黑铁大肩甲）和**铁护手**跟着身体走，形状不变。
> - 腿：近侧的腿在画面左边、颜色亮，远侧的腿在画面右边、暗一档、略高（和造型一样）；黑铁大靴平踩在红线上。
> - 每格 7 × 7 px 一个纯色方块，所有格子对齐同一个网格（`design/sion_design_on_canvas.png` 的格子）；**只用造型的 27 色**（`design/sion_palette.png`）；外轮廓一圈 1 格的近黑描边（和造型一样）；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（冲击波、裂地、怒吼的声波、护盾、火焰、尘土），只画赛恩本人；**红线以下什么都不能有**；出招一律朝画面右边。
> - 交付到 `outputs/sion-strips/`：每帧 `sion_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `sion_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`sion_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本把整个人缩放或重画成方块**（上一步你用脚本画的方块造型被换掉了）；一个动作里的几帧，**画后一帧时附上前一帧**，让人、头、斧头一样大。

## 要画的帧（36 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `sion_attack_1.png` | 普攻：巨斧劈砍 | 准备：近侧手把斧头往后上方提起，身体微微后仰 |
| `sion_attack_2.png` | | 举到最高：斧头举过头顶到身后，双腿蹲稳 |
| `sion_attack_3.png` | | 劈下：斧头从上往右前方猛劈，身体前压（身体仍朝前） |
| `sion_attack_4.png` | | 劈到底：斧刃砍在右前方低处，手臂伸直 |
| `sion_attack_5.png` | | 收招：回到造型的站姿 |
| `sion_skill_charge_1.png` | Q 残虐猛击：蓄力 | 下蹲，斧头往后拉到身体左后方 |
| `sion_skill_charge_2.png` | | 继续蓄力：斧头拉到最后，身体压低 |
| `sion_skill_charge_3.png` | | 斧头双手高举过头顶，身体挺直（蓄满） |
| `sion_skill_charge_4.png` | | 同上，斧头再高一点（这两帧会循环） |
| `sion_skill_1.png` | Q 砸地 | 从头顶开始往下砸 |
| `sion_skill_2.png` | | 斧头砸到身前一半高度 |
| `sion_skill_3.png` | | 斧头砸在身前（画面右边）地上，身体压到最低 |
| `sion_skill_4.png` | | 保持砸地的低姿态 |
| `sion_skill_5.png` | | 站起来回到站姿 |
| `sion_skill2_1.png` | E 杀手怒吼 | 吸气：身体往后仰，两臂张开 |
| `sion_skill2_2.png` | | 蓄力：重心在后，胸口挺起 |
| `sion_skill2_3.png` | | 怒吼：身体往前压低，头往右前方伸出，嘴（下颌笼）张开（声波不画） |
| `sion_skill2_4.png` | | 保持怒吼的前压姿势 |
| `sion_skill2_5.png` | | 收回到站姿 |
| `sion_skill2_w_1.png` | W 灵魂熔炉（护盾） | 两臂往两边张开，挺胸，熔炉露出来 |
| `sion_skill2_w_2.png` | | 两臂收到身前握拳发力 |
| `sion_skill2_w_3.png` | | 发力到最大：两拳握紧在身前，肌肉鼓起（护盾不画） |
| `sion_skill2_w_4.png` | | 回到站姿 |
| `sion_ult_1.png` | R 蛮横冲撞：冲锋姿势 | 低头冲锋：身体前倾，肩膀和头往右前方顶，斧头拖在身后（**只要上半身好看；腿我这边换成走路的腿，腿照骨架画即可**） |
| `sion_ult_2.png` | | 同上，下一步（两帧循环） |
| `sion_ult_hit_1.png` | R 撞上 | 撞上的一刻：肩膀往前猛顶 |
| `sion_ult_hit_2.png` | | 斧头往右前方挥出 |
| `sion_ult_hit_3.png` | | 身体压低滑停，斧头在身前 |
| `sion_ult_hit_4.png` | | 保持低姿态 |
| `sion_ult_hit_5.png` | | 回到站姿 |
| `sion_dead_1.png` | 死亡 | 被打中，身体一晃 |
| `sion_dead_2.png` | | 头往后仰，手臂垂下 |
| `sion_dead_3.png` | | 膝盖一软，往下跪 |
| `sion_dead_4.png` | | 跪在地上，身体前倾 |
| `sion_dead_5.png` | | 扑倒在地上（仍是正面朝向看画的人那一侧，不要翻成背面） |
| `sion_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/sion_<动作>_<n>.png`（骨架）
2. `design/sion_design.png`（造型）
3. `design/sion_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/sion_picture_A.png`（你的正面原稿，看长相）

```text
Image 2 is the final pixel-art design of this character: Sion, the Undead Juggernaut, a huge hunched undead warrior - an enormous pale grey-lilac muscular upper body with dark red stitched scars and black iron plates nailed into the chest, a SMALL bald head with two red glowing eyes and a black iron jaw cage with spikes, a broken blade stuck in the top of his head with a red ribbon, a huge black-iron spiked pauldron on the far shoulder (image right), an iron gauntlet on the far forearm, a glowing red furnace in his belly on a wide iron belt with round buckles, brown and plum trousers, an olive loin cloth, big black iron boots, and a great axe (a broad curved steel blade, a long leather-wrapped haft, a bone ring) in his near hand. It is drawn on a grid of 7x7-pixel squares, 101 x 75 squares, 27 colours, a 1-square near-black outline. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions. (Image 4, when attached, is the previous frame of the same action: keep the character exactly as big.)
Draw ONE frame, in the same 3/4 FRONT view as Image 2 (facing image right, the face, the chest and the belly furnace toward the viewer - where Image 1 turns his back, keep the body facing the viewer and copy only where the arms and the axe go): <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 7-pixel grid as Image 3, every square one flat colour from Image 2's 27 colours; the character exactly as big as Image 2 (67 squares from the crown of the bald head to the soles when standing); his head copied square for square from Image 2 (the same face, only moved - no profile, no back of the head); the axe is Image 2's axe as one rigid piece - the same blade, haft length, bone ring and colours, only moved or turned to Image 1's angle, never stretched, bent or shortened, never covering the face or the furnace; the spiked pauldron and the gauntlet keep their shapes; the near leg on the image left in full tone, the far leg on the image right one shade darker; the soles on the red line of the guide (square row 140), nothing below it; a 1-square near-black outline round the silhouette; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no shockwave, no cracks, no sound waves, no shield, no flames, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文，例如：

- attack 1–5：`an axe chop, frame <n> of 5: <1: lifting the axe up and back with the near hand, leaning back a little | 2: the axe raised highest, over and behind his head, feet planted | 3: the chop, the axe swinging down toward the front right, the body pressing in (still facing the viewer) | 4: the end of the chop, the blade low at the front right, the arm straight | 5: recovering to the standing pose of Image 2>`
- skill_charge 1–4：`Decimating Smash, charging, frame <n> of 4: <1: crouching, the axe drawn back to his left behind him | 2: the axe drawn back furthest, the body low | 3: the axe raised high over his head in both hands, the body upright, fully charged | 4: the same, the axe a square higher (frames 3 and 4 loop)>`
- skill 1–5：`Decimating Smash, the slam, frame <n> of 5: <1: the axe starting down from overhead | 2: the axe halfway down in front of him | 3: the axe slammed onto the ground in front of him (image right), the body at its lowest | 4: holding the low slam pose | 5: rising back to the standing pose>`
- skill2 1–5：`Roar of the Slayer, frame <n> of 5: <1: drawing breath, leaning back, the arms opening | 2: the wind-up, the weight back, the chest raised | 3: the roar, the body thrust forward and low, the head pushed toward the front right, the jaw cage open (do not draw the sound wave) | 4: holding the roar, leaning forward | 5: recovering to the standing pose>`
- skill2_w 1–4：`Soul Furnace, frame <n> of 4: <1: the arms opening wide, the chest and the glowing furnace pushed out | 2: the arms coming in, the fists in front of him | 3: flexing hardest, both fists clenched in front, the muscles bulging (do not draw the shield) | 4: back to the standing pose>`
- ult 1–2：`Unstoppable Onslaught, the charge, frame <n> of 2: charging head-down, the body leaning far forward, the shoulder and the head pushing toward the front right, the axe dragging behind him (the upper body is what matters; the legs may follow Image 1)<2: the next stride, the same upper body (the two frames loop)>`
- ult_hit 1–5：`Unstoppable Onslaught, the crash, frame <n> of 5: <1: the impact, the shoulder thrust forward | 2: the axe swung forward to the front right | 3: skidding to a stop low, the axe in front of him | 4: holding the low pose | 5: back to the standing pose>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, the body jolting | 2: the head thrown back, the arms dropping | 3: the knees giving way, sinking down | 4: on his knees, leaning forward | 5: fallen forward onto the ground, still the side facing the viewer (never turned to his back) | 6: the same, still (the last frame)>`

## 交回前请检查

- 36 帧都在，文件名对，每张 1536×1024 透明底、7 px 一格，`_1x` 和大图逐格一致。
- 每帧都和造型一样大（站直光头顶到脚底 67 格）；头是造型的头（同一张脸，3/4 正面）；斧头是造型的斧头（整块，长短不变）。
- 全部 3/4 正面朝右，没有侧脸、没有背影。
- 脚底在红线上，红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/sion-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 7 px 格读回（regrid --size 7），颜色贴回造型的 27 色；头按造型逐格贴回（一张脸贯穿所有帧），斧头查长度一致；洋红底 8 倍逐帧自查（缝、碎片、变形：rig-deformation-checks、gap-check），**先自己 review、再开独立审查子代理，审查说可以才给用户看**；待机 = 造型 + 呼吸；受击 = 造型平移 + 闪白；跑步 = rig_galio.walk_frame 的走法（造型自己的腿轮流抬、小步前移、身体微浮）；R 冲锋 = ult 的上半身 + 走路的腿。
- 写 1x 帧 + PPU 帧（ppu_hd.py PPU 1.52）、hd.rs HEROES（league.dll 版本号高于游戏里的，先问「千珏」「巴德」）；按真实出手帧重新计时，再跑平衡模拟。
