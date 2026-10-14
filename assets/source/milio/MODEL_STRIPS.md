# 米利欧（明烛）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户选了侧身 B），共用一套颜色：
> - **男孩的侧身**：`design/milio_side_design.png`（**45 × 96 格**，约 3/4 侧身朝右，正面那颗头：深靛卷发、两只琥珀大眼、咧嘴笑；双拳握在胸前）——**男孩的所有动作都从它画**；
> - **火精灵**：`design/milio_spirit_design.png`（约 19 × 26 格（算上顶上的火苗），圆滚滚的发光火球 + 小脸）——**只画它自己的 4 帧飘动循环**；
> - **正面**：`design/milio_front_design.png`（待机和选人卡用，**这一轮不用画**，只给你看样子）。
> 这里每格 **6 × 6 px**（1536×1024 里 256 × 170 格）。**待机和受击不用画**。
> - **男孩和火精灵分开画**：男孩的每一帧**只画男孩**（不画火精灵）；火精灵单独画一组，放进他的帧里由我来做。
> - **每帧一张图**：`now/milio_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置照它**。`guide/` 是同一张加了线：**红线 = 鞋底线**（第 160 行的下边），**蓝线 = 造型站直时发顶的高度**，**蓝十字 = 站位点**（第 120 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/milio_side_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照侧身造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**（骨架的头比造型小、腿比造型长——一律照造型）。**和造型一样大**：站直时发顶到鞋底 96 格；不要画大也不要画小。
> - **头每帧都是造型的头**：深靛蓝黑卷发、暖棕皮肤、**两只琥珀色大眼（深色瞳孔 + 白色高光）**、咧嘴笑，逐格照抄造型（造型最上面那一块，到下巴和脖子为止），**只平移**，脸朝右前方（两只眼睛都看得见）；**不要重新画一张脸**，不要画侧脸，**头不要歪、不要转、不要缩放**。
> - **衣服每帧照造型**：红上衣 + 青绿立领 + 青绿圆坠饰；金色蓬起的肩垫 + 米白流苏（近侧那块在前）；青绿斜腰带 + 金扣；品红/紫红褶裙下摆；棕色小腿；红 + 青绿绑腿；棕色凉鞋朝右。**手臂、腿的粗细和长短每帧一样**（和造型一样敦实，不要画细、画长）。
> - **一律侧身朝右**（和侧身造型一样）：**两条腿一前一后**（近侧腿颜色亮、在前；远侧腿暗一档、在后）。
> - 每格 6 × 6 px 一个纯色方块，所有格子对齐同一个网格（`design/milio_side_design_on_canvas.png` 的格子）；**只用造型的颜色**（40 色：`design/milio_palette.png`）；外轮廓描边和造型一样粗（约 2 格近黑）；不要抖动、渐变、噪点、抗锯齿、半透明（**alpha 只能是 0 或 255**——前两轮交回的图都有一圈半透明光晕）。
> - **不画特效**（火球、火焰、护盾、光、尘土），只画角色；**红线以下什么都不能有**；出手一律朝画面右边。
> - 骨架只是参考：英雄联盟里他有几帧转身、翻滚或者跳得很高，**我们不转身、不倒立**——一直侧身朝右、脸朝右前方，照下表写的画。
> - 交付到 `outputs/milio-strips/`：每帧 `milio_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `milio_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（**原样，不要重采样、不要自己整理**——上一轮你整理过的 12 px 版本反而糊了，我用的是原稿）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`milio_strips_done.zip`）。
> - 一个动作里的几帧，**画后一帧时附上前一帧**，让角色、头一样大。

## 要画的帧（男孩 36 帧 + 火精灵 4 帧）

### 男孩（全部侧身朝右，`design/milio_side_design.png`，不画火精灵）

| 文件 | 动作 | 这一帧画什么（身体照骨架；手脚按这里） |
|---|---|---|
| `milio_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，**两条腿照骨架交替迈步**：一前一后，**每一帧前面那条腿要换着来**（1–4 帧近侧腿往前、远侧腿往后蹬；5–8 帧反过来），脚抬起时膝盖弯；双臂弯着前后摆（拳头）；身体稍微前倾，随步子上下颠 1–2 格 |
| `milio_attack_1.png` | 普攻：甩出一颗小火球 | 近侧手往后收到肩后蓄力，身体稍后仰 |
| `milio_attack_2.png` | | 身体往右前方压，手臂开始往前甩 |
| `milio_attack_3.png` | | **甩出的一刻**：近侧手臂伸直朝右前方，**手掌张开**（火球从这里飞出——火球不画），身体前倾，后腿蹬直 |
| `milio_attack_4.png` | | 甩完：手臂还伸在前面，身体开始回正 |
| `milio_attack_5.png` | | 回到造型的站姿 |
| `milio_skill_1.png` | Q 火爆飞踢：踢出一颗火球 | 下蹲蓄力，双拳在胸前 |
| `milio_skill_2.png` | | 往上轻跳，近侧腿往后收（准备踢） |
| `milio_skill_3.png` | | 空中：身体后仰，近侧腿在身后弯起来 |
| `milio_skill_4.png` | | **踢出的一刻**：近侧腿**往右前方用力踢直**（脚尖朝右上），身体后仰保持平衡，双臂张开（火球不画） |
| `milio_skill_5.png` | | 落地：两脚踩回红线，身体前倾缓冲 |
| `milio_skill_6.png` | | 回到站姿 |
| `milio_skill2_1.png` | E 融融情谊（+ W 依依不舍）：给队友送护盾 | 稍微下蹲，双拳收在胸前 |
| `milio_skill2_2.png` | | 近侧手臂**往右上方高高举起**，手掌张开 |
| `milio_skill2_3.png` | | **出手的一刻**：手臂举到最高、伸直，踮起脚尖，开心地笑（护盾不画） |
| `milio_skill2_4.png` | | 手臂放下一半 |
| `milio_skill2_5.png` | | 回到站姿 |
| `milio_ult_1.png` | R 生生不息：为身边的队友净化回血 | 下蹲蓄力，双臂交叉收在胸前 |
| `milio_ult_2.png` | | **原地往上跳起**（离开红线约 10 格），双臂往上举 |
| `milio_ult_3.png` | | 空中最高点：双臂高举、手掌张开 |
| `milio_ult_4.png` | | **落地的一刻**（两脚回到红线）：双臂**往两边大大张开**，像拥抱大家（这一刻放出治疗的火焰——火焰不画） |
| `milio_ult_5.png` | | 双臂还张开，身体站直 |
| `milio_ult_6.png` | | 双臂收回，回到站姿 |
| `milio_dead_1.png` | 死亡 | 被打中，身体往前弯，双手垂下 |
| `milio_dead_2.png` | | 腿一软，膝盖弯下去 |
| `milio_dead_3.png` | | 往前扑倒，双手撑地 |
| `milio_dead_4.png` | | 趴在地上（脸朝下、头在画面右边），整个身体贴着红线 |
| `milio_dead_5.png` | | 同上 |
| `milio_dead_6.png` | | 同上，静止（最后一帧） |

### 火精灵（`design/milio_spirit_design.png`，不画男孩）

画在同一个格子上，**火精灵静止时中心在第 128 列、第 80 行**（`design/milio_spirit_design_on_canvas.png`）。圆滚滚的身体和**小脸（两只小黑眼 + 小嘴）逐格照抄造型，只平移**；只有顶上的小火苗可以动。不碰地面。

| 文件 | 动作 | 这一帧画什么 |
|---|---|---|
| `milio_spirit_float_1..4.png` | 飘动循环（4 帧） | 整个火精灵**只上下浮动 0–2 格**（1：原位；2：高 1 格；3：高 2 格；4：高 1 格）；顶上的两三簇小火苗一帧一帧换形状，像火焰在跳（大小不变） |

## 提示词

### 男孩：每帧一次

附图（工具一次最多 5 张时按这个顺序）：
1. `now/milio_<动作>_<n>.png`（骨架）
2. `design/milio_side_design.png`（侧身造型）
3. `design/milio_side_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `design/milio_front_design.png`（正面，看长相）

```text
Image 2 is the final pixel-art design of this character: a cheerful young boy seen three quarters SIDE-ON facing right - fluffy curly dark indigo-black hair, warm brown skin, TWO BIG AMBER EYES with dark pupils and white highlights, a happy grin (a 3/4 head: both eyes visible), a short red tunic with a teal stand-up collar and a round teal pendant, big puffed golden-bronze shoulder pads with cream tassels, a diagonal teal sash with a gold buckle, a magenta pleated kilt, bare brown shins, red-and-teal ankle wraps and brown sandals; both fists held in front of his chest. It is drawn on a grid of 6x6-pixel squares, 45 x 96 squares, 40 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place. Image 5 is the same character from the front (his look only; the fire spirit in it is NOT drawn here).
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose and its place - NOT its 3D look and NOT its realistic proportions (its head is smaller and its legs longer than the design's: always keep the design's). (Image 4, when attached, is the previous frame of the same action: keep him exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 6-pixel grid as Image 3, every square one flat colour from Image 2's 40 colours; the character exactly as big as Image 2 (96 squares from the top of the hair to the soles when standing) with Image 2's stocky proportions - the arms and legs as thick and as long as in Image 2 in every frame; he stays SIDE-ON facing image right like Image 2, never turned away, never upside down; his head - the curly hair, both amber eyes, the grin, down to the chin and neck - copied square for square from Image 2, only moved, never tilted, turned, scaled or redrawn as a profile; the near leg in front in full tone, the far leg behind one shade darker; the soles on the red line of the guide (square row 160) unless this frame is in the air, nothing below it; the same near-black outline as Image 2 (about 2 squares); alpha only 0 or 255; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no fireball, no fire, no shield, no glow, no trail, no dust), no fire spirit, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run：`running to the right, frame <n> of an 8-frame loop: the legs stepping as in Image 1 - frames 1-4 the near leg forward and the far leg pushing back, frames 5-8 the other way round (the front leg alternates; the lifted foot's knee bent); both arms bent, swinging back and forth with fists; the body leaning a little forward, bobbing 1-2 squares with the stride`
- attack 1–5：`basic attack, flinging a small fireball, frame <n> of 5: <1: the near hand drawn back behind his shoulder, gathering, the body leaning back a little | 2: the body pressing forward to the right, the arm starting to swing forward | 3: the fling (the release moment): the near arm straight toward the front-right with the hand OPEN, the body leaning forward, the back leg pushing straight (no fireball drawn) | 4: just thrown: the arm still out in front, the body coming upright | 5: back to the standing pose of Image 2>`
- skill 1–6：`Ultra Mega Fire Kick, kicking a fireball, frame <n> of 6: <1: crouching to gather power, fists at his chest | 2: a small hop upward, the near leg drawn back ready to kick | 3: in the air, leaning back, the near leg bent behind him | 4: THE KICK (the release moment): the near leg swung forward and kicked out STRAIGHT toward the upper right, toes pointing up-right, the body leaning back for balance, both arms open (no ball drawn) | 5: landing, both feet back on the red line, leaning forward to absorb it | 6: back to the standing pose>`
- skill2 1–5：`Warm Hugs, sending a shield to an ally, frame <n> of 5: <1: a small crouch, fists together at his chest | 2: the near arm raised HIGH toward the upper right, the hand open | 3: the release moment: the arm at its highest, straight, up on his toes, grinning (no shield drawn) | 4: the arm halfway down | 5: back to the standing pose>`
- ult 1–6：`Breath of Life, a healing blessing for everyone near, frame <n> of 6: <1: crouching to gather, both arms crossed at his chest | 2: jumping straight up on the spot (about 10 squares above the red line), both arms going up | 3: at the top of the jump, both arms raised high, hands open | 4: landing (the release moment; both feet back on the red line): both arms spread WIDE to the sides like a big hug (no flames drawn) | 5: standing straight, the arms still spread | 6: the arms back, back to the standing pose>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, the body bending forward, the hands hanging down | 2: the legs giving way, the knees bending | 3: falling forward onto his hands | 4: lying face down on the ground (head toward the image right), the whole body flat on the red line | 5: the same | 6: the same, still (the last frame)>`

### 火精灵：每帧一次

附图：
1. `design/milio_spirit_design.png`（火精灵造型）
2. `design/milio_spirit_design_on_canvas.png`（火精灵在画布上的大小和位置）
3. 同一个动作的前一帧（第 1 帧不附）

```text
Image 1 is the final pixel-art design of a little fire spirit: a ROUND glowing fireball buddy - a bright yellow-white core, an orange ring, a deep orange-red rim, two or three little flame tips curling up from its top, a cute face (two small dark eyes and a small happy mouth). It is drawn on a grid of 6x6-pixel squares. Image 2 shows it on a 1536x1024 canvas: that is its size and its resting place (its middle at square column 128, row 80). (Image 3, when attached, is the previous frame: keep it exactly as big.)
Draw ONE frame: floating in place, frame <n> of a 4-frame loop: the whole spirit <1: at its resting place | 2: 1 square higher | 3: 2 squares higher | 4: 1 square higher>; the flame tips on its top flickering, a little different each frame (the same size).
Rules: the same 1536x1024 transparent canvas and the SAME 6-pixel grid as Image 2, every square one flat colour from Image 1's colours; the spirit exactly as big as Image 1; its round body and its face copied square for square from Image 1, only moved; only the flame tips may change; the same near-black outline as Image 1; alpha only 0 or 255; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no glow, no sparks, no boy, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

## 交回前请检查

- 40 帧都在，文件名对，每张 1536×1024 透明底、6 px 一格、alpha 只有 0 / 255，`_1x` 和大图逐格一致。
- 男孩：每帧和造型一样大（站直发顶到鞋底 96 格），一直侧身朝右、不倒立；头是造型的头（两只琥珀眼都看得见、咧嘴笑）、只平移；手脚和造型一样粗；跑步前后腿交替；没有火球、没有火精灵。
- 火精灵：和造型一样大，身体和小脸逐格照抄，只有火苗动；没有男孩。
- 鞋底在红线上（跳起的空中帧除外），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/milio-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读原稿（raw/），每张先在 8 倍下数描边台阶量实际格子，再读回到 96 行的造型密度，颜色贴回造型的 40 色调色板；头按造型逐格贴回（一张脸贯穿所有帧）；腿查变形和缝（rig-deformation-checks、gap-check），跑步前后腿不交替就按 Caitlyn 的交叉步自己调；待机 = 正面造型（+ 火精灵上下浮动）；受击 = 侧身造型平移 + 闪白。
- 火精灵放进男孩每一帧（在他身后肩膀高度，飘动循环；死亡时淡出）；写 assets/source/ppu/milio_<tag>.png/.json、1x 表、ppu_restyle 到 2.2（发顶到鞋底 32 游戏行）、ppu_hd.py + lo_ 帧、hd.rs HEROES（league.dll ≥ 0.7.5，先问斯莫德 / SDK 0.6.4 当时最高号）；按动作条的出手帧（attack 3、skill 4、skill2 3、ult 4）重排技能数据的时机再跑一次模拟；逐帧自查后再给用户看 GIF。
