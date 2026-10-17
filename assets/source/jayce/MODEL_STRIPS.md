# 杰斯：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户选了锤形 A2 / 炮形 B2 的正面 + 各自的侧身 2），共用一套颜色：
> - **锤形侧身**：`design/jayce_hammer_side_design.png`（**84 × 122 格**，约 3/4 侧身朝右，双手斜握大锤、锤头在肩后上方）——**锤形的所有动作都从它画**；
> - **炮形侧身**：`design/jayce_cannon_side_design.png`（**119 × 93 格**，约 3/4 侧身朝右，加农炮水平端在腰间、炮口朝右）——**炮形的所有动作都从它画**；
> - **正面**：`design/jayce_hammer_front_design.png` / `jayce_cannon_front_design.png`（待机和选人卡用，**这一轮不用画**，只给你看样子）；
> - **头**：`design/jayce_head.png`——**每一帧都用这一颗头**（深棕后梳短发 + 一小撮刘海、麦色皮肤、浓眉、两只眼睛、自信微笑）。
> 这里每格 **5 × 5 px**（1536×1024 里 307 × 204 格）。**待机和受击不用画**。
> - **用画图模型（image_gen）画**，不要用脚本逐格写（上一轮第 1 步脚本写的版本被退回了）。
> - **每帧一张图**：`now/jayce_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置照它**。`guide/` 是同一张加了线：**红线 = 鞋底线**（第 196 行的下边），**蓝线 = 造型站直时发顶的高度**，**蓝十字 = 站位点**（第 120 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/jayce_<形态>_side_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照侧身造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**（骨架的头比造型小、腿比造型长——一律照造型）。**和造型一样大**：站直时发顶到鞋底锤形 98 格、炮形 93 格（炮形弯着腿）；不要画大也不要画小。
> - **头每帧都是造型的头**：逐格照抄 `design/jayce_head.png`，**只平移**，脸朝右前方（两只眼睛都看得见）；**不要重新画一张脸**，不要画侧脸，**头不要歪、不要转、不要缩放**。
> - **衣服每帧照造型**：深红围巾、米白毛领、棕皮外套、米金 + 红胸甲和圆徽章、大米金肩甲、棕皮带金扣、**海军蓝长衣摆**、灰蓝裤子、米金尖角护膝护胫、深棕靴子朝右、棕手套。**手臂、腿的粗细和长短每帧一样**（和造型一样敦实，不要画细、画长）。
> - **武器每帧照造型逐格画，永远是笔直的一整块**：锤 = 银灰圆柄 + 红握把 + 底端尖钻 + 大金色方块双锤头 + 橙色核心；炮 = 银灰炮管 + 炮口开口 + 两侧金色锤块 + 橙色核心 + 尾部尖钻。**柄和炮管不能弯、不能变短变长**；武器可以整块转到骨架的角度（举起、挥下），但形状和大小不变。
> - **一律侧身朝右**（和侧身造型一样）：**两条腿一前一后**（近侧腿颜色亮、在前；远侧腿暗一档、在后）。
> - 每格 5 × 5 px 一个纯色方块，所有格子对齐同一个网格（`design/jayce_<形态>_side_on_canvas.png` 的格子）；**只用造型的颜色**（`design/jayce_palette.png`）；外轮廓描边和造型一样粗（约 2 格近黑）；不要抖动、渐变、噪点、抗锯齿、半透明（**alpha 只能是 0 或 255**）。
> - **不画特效**（电光、闪电、电球、加速门、光、尘土），只画角色和武器；**红线以下什么都不能有**；出手一律朝画面右边。
> - 骨架只是参考：英雄联盟里他苍穹之跃时会在空中翻跟头，**我们不翻、不倒立、不转身**——一直侧身朝右、脸朝右前方，照下表写的画。
> - 交付到 `outputs/jayce-strips/`：每帧 `jayce_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `jayce_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（**原样，不要重采样、不要自己整理**——之前英雄你整理过的版本反而糊了，我用的是原稿）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`jayce_strips_done.zip`）。
> - 一个动作里的几帧，**画后一帧时附上前一帧**，让角色、头、武器一样大。

## 要画的帧（锤形 40 帧 + 炮形 31 帧）

### 锤形（全部侧身朝右，`design/jayce_hammer_side_design.png`）

| 文件 | 动作 | 这一帧画什么（身体照骨架；手脚按这里） |
|---|---|---|
| `jayce_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，双手握锤斜扛在身前（锤头在肩后上方，和造型一样），**两条腿照骨架交替迈步**：一前一后，**每一帧前面那条腿要换着来**（1–4 帧近侧腿往前、远侧腿往后蹬；5–8 帧反过来），脚抬起时膝盖弯；身体稍微前倾，随步子上下颠 1–2 格；长衣摆往后飘 |
| `jayce_attack_1.png` | 普攻：大锤横扫 | 锤往后上方举起蓄力，身体稍后仰 |
| `jayce_attack_2.png` | | 身体往右转压，锤从后上方开始往前挥 |
| `jayce_attack_3.png` | | 锤挥到头顶前上方 |
| `jayce_attack_4.png` | | **打中的一刻**：锤**往右前方水平伸直**（锤头在最右边），身体前倾，前腿弓、后腿蹬直 |
| `jayce_attack_5.png` | | 挥完：锤还在前面、开始收回 |
| `jayce_attack_6.png` | | 回到造型的站姿 |
| `jayce_skill_1.png` | Q 苍穹之跃：跳起来砸向敌人 | 下蹲蓄力，锤举到肩上 |
| `jayce_skill_2.png` | | **往右上方跳起**（离开红线约 20 格），双手把锤高高举过头顶 |
| `jayce_skill_3.png` | | 空中最高点往下落：锤举在头顶后上方，身体后仰（**不翻跟头**） |
| `jayce_skill_4.png` | | 往下砸：锤从头顶往右前下方挥下，身体前倾 |
| `jayce_skill_5.png` | | **砸地的一刻**：两脚落回红线、单膝弯，**锤头砸在右前方的地面上**（锤头底边贴着红线），身体压低前倾（电光不画） |
| `jayce_skill_6.png` | | 起身，锤收回肩上，回到站姿 |
| `jayce_skill2_1.png` | E 雷霆一击：把敌人击飞 | 锤收到身后下方，身体稍后仰蓄力 |
| `jayce_skill2_2.png` | | 锤从身后下方开始往前上方抡 |
| `jayce_skill2_3.png` | | 锤抡到身前、齐腰 |
| `jayce_skill2_4.png` | | **击中的一刻**：锤**往右上方用力挑起**（锤头在右上），身体后仰，后腿蹬直 |
| `jayce_skill2_5.png` | | 锤举在头顶上方 |
| `jayce_skill2_6.png` | | 锤收回，回到站姿 |
| `jayce_w_cast_1.png` | W 闪电领域：举锤召唤电场 | 锤开始往上举 |
| `jayce_w_cast_2.png` | | 锤举到头顶斜上方 |
| `jayce_w_cast_3.png` | | **出手的一刻**：锤**竖直高举过头顶**（锤柄笔直竖直），挺胸（电光不画） |
| `jayce_w_cast_4.png` | | 锤放下一半，回到站姿 |
| `jayce_tf_c_1.png` | 变形：锤 → 炮 | 锤从肩上放下到身前 |
| `jayce_tf_c_2.png` | | 锤横到腰间，**两块金色锤头开始往炮管两侧翻折** |
| `jayce_tf_c_3.png` | | 锤块折到一半，炮管从锤柄里伸出来，膝盖开始弯 |
| `jayce_tf_c_4.png` | | 完全变成炮，**和炮形侧身造型一样**（炮水平端在腰间、炮口朝右） |
| `jayce_dead_1.png` | 死亡 | 被打中，身体往后弯，锤往下垂 |
| `jayce_dead_2.png` | | 腿一软，膝盖弯下去，锤头碰到地面 |
| `jayce_dead_3.png` | | 往后倒 |
| `jayce_dead_4.png` | | 仰面躺在地上（头在画面左边），锤躺在身边，整个身体贴着红线 |
| `jayce_dead_5.png` | | 同上 |
| `jayce_dead_6.png` | | 同上，静止（最后一帧） |

### 炮形（全部侧身朝右，`design/jayce_cannon_side_design.png`）

| 文件 | 动作 | 这一帧画什么（身体照骨架；手脚按这里） |
|---|---|---|
| `jayce_c_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，**炮水平端在腰间、炮口朝右**（和造型一样），两腿照骨架交替迈步（1–4 帧近侧腿往前，5–8 帧反过来），身体前倾，随步子上下颠 1–2 格；长衣摆往后飘 |
| `jayce_c_attack_1.png` | 普攻：开炮 | 炮口对准右边，身体压低 |
| `jayce_c_attack_2.png` | | **开炮的一刻**：炮因后坐力往后缩 2–3 格，肩膀往后一顿（炮弹、炮口火光不画） |
| `jayce_c_attack_3.png` | | 炮回到原位 |
| `jayce_c_attack_4.png` | | 回到站姿 |
| `jayce_c_skill_1.png` | Q 电能震荡：发射电球 | 炮口对准右边，身体压低 |
| `jayce_c_skill_2.png` | | 炮口往上抬起约 45°（蓄能） |
| `jayce_c_skill_3.png` | | 炮几乎竖起来，蓄满（电光不画） |
| `jayce_c_skill_4.png` | | **发射的一刻**：炮**压回水平、炮口朝右**，身体往后一顿（电球不画） |
| `jayce_c_skill_5.png` | | 回到站姿 |
| `jayce_c_skill2_1.png` | W 超能电荷：给炮充能 | 炮稍微抬起 |
| `jayce_c_skill2_2.png` | | 炮抬到斜上方，身体挺直 |
| `jayce_c_skill2_3.png` | | **出手的一刻**：炮停在斜上方，像在给炮充能（电光不画） |
| `jayce_c_skill2_4.png` | | 炮放回水平，回到站姿 |
| `jayce_ult_1.png` | 大招 加速电炮：先放加速之门，再打穿门的电能震荡 | 炮往上一抬，一只手往前一挥（放门的动作；门不画） |
| `jayce_ult_2.png` | | 炮举到斜上方 |
| `jayce_ult_3.png` | | 炮口往上抬约 45°（蓄能） |
| `jayce_ult_4.png` | | 炮几乎竖起来，蓄满 |
| `jayce_ult_5.png` | | **发射的一刻**：炮**压回水平、炮口朝右**，身体往后一顿、后腿蹬直（电球不画） |
| `jayce_ult_6.png` | | 回到站姿 |
| `jayce_tf_h_1.png` | 变形：炮 → 锤 | 炮从腰间往上提 |
| `jayce_tf_h_2.png` | | 炮管缩回，**两块金色锤块往上翻开**，身体站直 |
| `jayce_tf_h_3.png` | | 锤头成形一半，锤柄往肩上斜 |
| `jayce_tf_h_4.png` | | 完全变成锤，**和锤形侧身造型一样**（双手斜握锤、锤头在肩后上方） |

## 提示词（每帧一次，用 image_gen）

附图（工具一次最多 5 张时按这个顺序）：
1. `now/jayce_<动作>_<n>.png`（骨架）
2. 这个形态的侧身造型：锤形 `design/jayce_hammer_side_design.png`，炮形 `design/jayce_cannon_side_design.png`（`tf_c_4` 附炮形的，`tf_h_4` 附锤形的）
3. 这个形态的造型在画布上：`design/jayce_hammer_side_on_canvas.png` / `design/jayce_cannon_side_on_canvas.png`
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `design/jayce_head.png`（每一帧的那颗头）

```text
Image 2 is the final pixel-art design of this character: a confident young man seen three quarters SIDE-ON facing right - short dark brown swept-back hair with a small quiff, tanned skin, thick brows, both eyes visible, a confident half smile (a 3/4 head), a deep red scarf, a cream fur collar, a brown leather coat, cream-gold and red chest armour with a round emblem, a big cream-gold shoulder plate, a brown belt with a gold buckle, long dark navy coat tails, slate-blue trousers, cream-gold pointed knee guards and shin plates, dark brown boots, brown gloves; and his hextech weapon <WEAPON>. It is drawn on a grid of 5x5-pixel squares. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place. Image 5 is his head: copy it square for square in every frame.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose and its place - NOT its 3D look and NOT its realistic proportions (its head is smaller and its legs longer than the design's: always keep the design's). (Image 4, when attached, is the previous frame of the same action: keep him and the weapon exactly as big.)
Draw with the image generator ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 5-pixel grid as Image 3, every square one flat colour from Image 2's colours; the character exactly as big as Image 2 (<ROWS> squares from the top of the hair to the soles when standing) with Image 2's stocky proportions - the arms and legs as thick and as long as in Image 2 in every frame; he stays SIDE-ON facing image right like Image 2, never turned away, never upside down, no somersault; his head copied square for square from Image 5, only moved, never tilted, turned, scaled or redrawn as a profile; the weapon copied from Image 2 as ONE RIGID PIECE, PERFECTLY STRAIGHT, the same shape, length and size, only moved or turned whole to the pose's angle; the near leg in front in full tone, the far leg behind one shade darker; the soles on the red line of the guide (square row 196) unless this frame is in the air, nothing below it; the same near-black outline as Image 2 (about 2 squares); alpha only 0 or 255; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no lightning, no sparks, no energy orb, no gate, no muzzle flash, no glow, no trail, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WEAPON>`：锤形 `the MERCURY HAMMER: a long straight round silver-grey shaft with a red grip and a silver-grey drill spike at its lower end, a huge golden double head of two square blocks with an orange hextech core between them, held in both hands slanting across his chest with the head up behind his shoulder`；炮形 `the MERCURY CANNON: a straight silver-grey barrel with a dark open muzzle and a ring round it, the two square golden blocks folded along both sides, an orange hextech core between them, a drill spike at the back end, held level at his hip in both hands, the muzzle pointing RIGHT`。`<ROWS>`：锤形 98，炮形 93。

`<WHAT>` 按上表换成英文：

- run：`running to the right, frame <n> of an 8-frame loop, carrying the hammer slanted across his chest as in Image 2: the legs stepping as in Image 1 - frames 1-4 the near leg forward and the far leg pushing back, frames 5-8 the other way round (the front leg alternates; the lifted foot's knee bent); the body leaning a little forward, bobbing 1-2 squares with the stride; the coat tails flowing back`
- attack 1–6：`basic attack, a horizontal hammer swing, frame <n> of 6: <1: the hammer raised back over his shoulder, gathering, the body leaning back a little | 2: the body turning forward to the right, the hammer starting to swing forward from behind | 3: the hammer swinging over the front of his head | 4: THE HIT (the release moment): the hammer stretched out LEVEL toward the right, its head at the far right, the body leaning forward, the front knee bent, the back leg pushing straight | 5: the hammer still out in front, coming back | 6: back to the standing pose of Image 2>`
- skill 1–6：`To the Skies!, leaping up and smashing down on an enemy, frame <n> of 6: <1: crouching to gather, the hammer up on his shoulder | 2: jumping up toward the upper right (about 20 squares above the red line), both hands lifting the hammer high over his head | 3: at the top, starting to fall: the hammer held high behind his head, the body leaning back (no somersault) | 4: smashing down: the hammer swinging from over his head down toward the lower right, the body leaning forward | 5: THE SMASH (the release moment): both feet back on the red line, one knee bent, the hammer head slammed onto the ground at the front right (its bottom edge on the red line), the body low and leaning forward (no lightning drawn) | 6: rising, the hammer back on his shoulder, back to the standing pose>`
- skill2 1–6：`Thundering Blow, an uppercut swing that knocks an enemy back, frame <n> of 6: <1: the hammer drawn back low behind him, the body leaning back, gathering | 2: the hammer swinging forward and up from low behind | 3: the hammer in front of him at waist height | 4: THE HIT (the release moment): the hammer flung UP toward the upper right (its head at the upper right), the body leaning back, the back leg pushing straight | 5: the hammer raised above his head | 6: the hammer back, back to the standing pose>`
- w_cast 1–4：`Lightning Field, raising the hammer to call a storm, frame <n> of 4: <1: the hammer starting to rise | 2: the hammer raised above his head, slanted | 3: the release moment: the hammer held STRAIGHT UP above his head, the shaft vertical, the chest out (no lightning drawn) | 4: the hammer halfway down, back toward the standing pose>`
- tf_c 1–4：`transforming the hammer into a cannon, frame <n> of 4: <1: the hammer lowered from his shoulder to in front of him | 2: the hammer held across at his waist, the two golden head blocks starting to fold back along the shaft | 3: the blocks half folded, a barrel sliding out of the shaft, the knees starting to bend | 4: fully the cannon, exactly the pose of the CANNON design (attach the cannon side design as Image 2): the cannon level at his hip, the muzzle pointing right>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, the body bending back, the hammer drooping | 2: the legs giving way, the knees bending, the hammer head touching the ground | 3: falling backward | 4: lying on his back on the ground (head toward the image left), the hammer lying beside him, the whole body flat on the red line | 5: the same | 6: the same, still (the last frame)>`
- c_run：`running to the right, frame <n> of an 8-frame loop, the cannon held level at his hip, the muzzle pointing right, as in Image 2: the legs stepping as in Image 1 - frames 1-4 the near leg forward and the far leg pushing back, frames 5-8 the other way round; the body leaning forward, bobbing 1-2 squares; the coat tails flowing back`
- c_attack 1–4：`basic attack, firing the cannon, frame <n> of 4: <1: aiming right, the body low | 2: THE SHOT (the release moment): the cannon recoiling 2-3 squares back, the shoulders jolted back (no shell, no muzzle flash drawn) | 3: the cannon back in place | 4: back to the standing pose of Image 2>`
- c_skill 1–5：`Shock Blast, firing an electric orb, frame <n> of 5: <1: aiming right, the body low | 2: the muzzle lifted up about 45 degrees, charging | 3: the cannon raised almost upright, fully charged (no lightning drawn) | 4: THE SHOT (the release moment): the cannon brought down LEVEL, the muzzle pointing right, the body jolted back (no orb drawn) | 5: back to the standing pose>`
- c_skill2 1–4：`Hyper Charge, charging the cannon, frame <n> of 4: <1: the cannon lifted a little | 2: the cannon raised to slant up, the body upright | 3: the release moment: the cannon held slanting up as if charging it (no lightning drawn) | 4: the cannon level again, back to the standing pose>`
- ult 1–6：`the gated Shock Blast, placing an acceleration gate and firing a huge orb through it, frame <n> of 6: <1: the cannon lifted, one hand sweeping forward (placing the gate - no gate drawn) | 2: the cannon raised to slant up | 3: the muzzle lifted up about 45 degrees, charging | 4: the cannon almost upright, fully charged | 5: THE SHOT (the release moment): the cannon brought down LEVEL, the muzzle pointing right, the body jolted back, the back leg pushing straight (no orb drawn) | 6: back to the standing pose>`
- tf_h 1–4：`transforming the cannon into the hammer, frame <n> of 4: <1: the cannon lifted from his hip | 2: the barrel sliding back in, the two golden blocks folding out upward, standing upright | 3: the hammer head half formed, the shaft slanting up to his shoulder | 4: fully the hammer, exactly the pose of the HAMMER design (attach the hammer side design as Image 2): held slanting across his chest, the head up behind his shoulder>`

## 交回前请检查

- 71 帧都在（锤形 40、炮形 31），文件名对，每张 1536×1024 透明底、5 px 一格、alpha 只有 0 / 255，`_1x` 和大图逐格一致；**都是 image_gen 画的**。
- 每帧和造型一样大（站直发顶到鞋底锤形 98 格、炮形 93 格），一直侧身朝右、不倒立、不翻跟头；头是 `jayce_head.png` 那颗（两只眼睛都看得见、微笑）、只平移；手脚和造型一样粗；跑步前后腿交替。
- 武器每帧是造型那一整块、**笔直**、一样长一样大；锤形动作里是锤，炮形动作里是炮；变形帧（tf_c / tf_h）的最后一帧和另一个形态的侧身造型一样。
- 鞋底在红线上（跳起的空中帧除外），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/jayce-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读原稿（raw/），每张先在 8 倍下数描边台阶量实际格子，再读回到造型密度（锤形 98 行、炮形 93 行），颜色贴回造型的调色板；头按 `head.png` 逐格贴回（一张脸贯穿所有帧）；武器查笔直、大小一致（必要时贴回造型的武器、整块平移 / 90° 转）；腿查变形和缝（rig-deformation-checks、gap-check），跑步按 Caitlyn 的交叉步；待机 = 正面造型（锤形 idle、炮形 c_idle），受击 = 侧身造型平移 + 闪白。
- 写 assets/source/ppu/orig、ppu_restyle 到 PPU 1.5（发顶到鞋底 38 游戏行）、ppu_hd.py + lo_ 帧、hd.rs HEROES（league.dll ≥ 0.7.7，先问其他会话当时最高号）；按出手帧（attack 4、skill 5、skill2 4、w_cast 3、c_attack 2、c_skill 4、c_skill2 3、ult 5、tf 4）重排技能数据的时机再跑一次模拟；逐帧自查后再给用户看 GIF。
