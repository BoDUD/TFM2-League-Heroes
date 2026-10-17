# 尼菈（不羁之悦）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户选了侧面 A），共用一套颜色：
> - **侧面**：`design/nilah_side_design.png`（**56 × 106 格**，正侧面朝右，收起的鞭刃竖直举在身后的手里）——**所有动作都从它画**；
> - **正面**：`design/nilah_front_design.png`（待机和选人卡用，**这一轮不用画**，只给你看她的样子）。
> 这里每格 **7 × 7 px**（1536×1022 正好 219 × 146 格）。**待机和受击不用画**。其余动作照英雄联盟里尼菈的动作画。
> - **每帧一张图**：`now/nilah_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 140 行的下边），**蓝线 = 造型站直时的最高点（刃尖）**，**蓝十字 = 站位点**（第 80 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/nilah_side_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照侧面造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**。**和造型一样大**：站直时头发顶到脚底 101 格；不要画大也不要画小，**头和身子的比例照造型**（敦实、头大）。
> - **头每帧都是造型的头**：脸、紫眼睛、齐刘海、两侧短发、青绿耳坠、笑脸逐格照抄造型（造型的第 3–25 行那一块），**只平移**，脸朝右前方（3/4，两只眼睛都看得见）；**不要重新画一张脸**，不要画侧脸。长马尾可以随动作摆动，但粗细、颜色照造型。
> - **鞭刃（武器）每帧都是造型里那把收起来的短刃**（青铜握柄、下端青色尖刃、上端暗红紫刀片，造型左上角那一竖条）：**一根笔直的直线，整把照抄，只能平移，或者整把转 90 度变成水平**（刃尖朝右或朝左）；不能歪、不能斜、不能弯、不能缩放、不能伸长。**骨架里那条甩出去的长鞭子不要画**——鞭子甩出去的样子是特效，第 3 步单独画。
> - **一律正侧面朝右**（和侧面造型一样）：黄色上衣侧过来、缠黄布条的胳膊在身前、缠暗红护臂的胳膊拿刃；腿一前一后（近侧腿颜色亮、在前；远侧腿暗一档、在后）；黑色平底鞋鞋尖朝右。跑步一前一后交叉迈步，两条腿都是直的（从胯到脚踝一条直线，不要折成怪角度）。
> - 每格 7 × 7 px 一个纯色方块，所有格子对齐同一个网格（`design/nilah_side_design_on_canvas.png` 的格子）；**只用造型的 29 色**（`design/nilah_palette.png`）；外轮廓描边和造型一样粗（约 2 格近黑）；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（鞭子的长影、旋风、水雾、光、尘土），只画人和那把短刃；**红线以下什么都不能有**；出招一律朝画面右边。
> - 骨架只是参考：英雄联盟里她有几帧转身背对或者翻身，**我们不转身**——一直侧身朝右、脸朝右前方，照下表写的画。
> - 交付到 `outputs/nilah-strips/`：每帧 `nilah_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `nilah_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`nilah_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**；一个动作里的几帧，**画后一帧时附上前一帧**，让人、头、短刃一样大。

## 要画的帧（50 帧，全部侧身朝右，`design/nilah_side_design.png`）

| 文件 | 动作 | 这一帧画什么（身体照骨架；短刃按这里） |
|---|---|---|
| `nilah_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，腿照骨架一前一后交叉、两腿都直；短刃**竖直**握在身后的手里（和造型一样），随步子上下颠，身前的手臂前后摆；马尾在身后飘 |
| `nilah_attack_1.png` | 普攻：鞭击 | 准备：拿刃的手举到头后上方，短刃竖直 |
| `nilah_attack_2.png` | | 手臂从头上往前挥，短刃仍竖直在肩上方 |
| `nilah_attack_3.png` | | 手臂挥到身前，短刃整把转成**水平**、刃尖朝右 |
| `nilah_attack_4.png` | | 命中：手臂朝右前方伸直，短刃水平、刃尖朝右，身体前倾、前腿弓步 |
| `nilah_attack_5.png` | | 回到造型的站姿，短刃竖着回到身后的手里 |
| `nilah_attack_q_1.png` | 强化普攻：横扫 | 两臂张开，拿刃的手举在身后高处，短刃竖直 |
| `nilah_attack_q_2.png` | | 扭腰蓄力，身体略压低 |
| `nilah_attack_q_3.png` | | 手臂从身后往前横扫，短刃转成**水平**、刃尖朝右 |
| `nilah_attack_q_4.png` | | 扫到最前：手臂伸直在身前、比肩略低，短刃水平朝右 |
| `nilah_attack_q_5.png` | | 回到站姿 |
| `nilah_skill_1.png` | Q 游刃万变：大力鞭击 | 下蹲蓄力，拿刃的手收到身后低处，短刃竖直 |
| `nilah_skill_2.png` | | 前腿向右跨出一大步，身体前倾，手臂拉到最后 |
| `nilah_skill_3.png` | | 手臂从头上往前甩，短刃竖直在头顶上方 |
| `nilah_skill_4.png` | | 出手：大弓步，手臂朝右伸到最前、和肩一样高，短刃水平、刃尖朝右（这一刻鞭子甩出去，鞭子是特效，不画） |
| `nilah_skill_5.png` | | 收回到站姿 |
| `nilah_q_spin_1.png` | 旋斩（E 之后的 Q） | 原地压低身子，拿刃的手在身前，短刃水平朝右 |
| `nilah_q_spin_2.png` | | 手臂举到头上方，短刃竖直（在头顶划圈） |
| `nilah_q_spin_3.png` | | 手臂甩到身后，短刃水平、刃尖朝左 |
| `nilah_q_spin_4.png` | | 手臂再举回头上方，短刃竖直 |
| `nilah_q_spin_5.png` | | 回到站姿 |
| `nilah_skill2_1.png` | E 纵情逐流：冲刺 | 压低身子前倾，准备冲出去，短刃水平、刃尖朝左（在身后） |
| `nilah_skill2_2.png` | | 冲刺：身体几乎平着朝右前方冲，前腿伸出、后腿蹬直，手臂在身后，短刃水平朝左 |
| `nilah_skill2_3.png` | | 落地：双腿弯曲蹲着落地，身体前倾 |
| `nilah_skill2_4.png` | | 站起回到站姿 |
| `nilah_w_cast_1.png` | W 轻纱飞漾 | 轻轻一跳，两臂在胸前交叉，短刃竖直 |
| `nilah_w_cast_2.png` | | 在空中转身舒展：两臂举高张开，短刃竖直在头上方（身体还是侧身朝右，脸朝右前方） |
| `nilah_w_cast_3.png` | | 落地，两臂向两边张开 |
| `nilah_w_cast_4.png` | | 回到站姿 |
| `nilah_ult_1.png` | R 神恩激荡：旋转鞭刃 1 秒 | 下蹲蓄力，拿刃的手收到身后 |
| `nilah_ult_2.png` | | 跳起，手臂甩到身前，短刃水平朝右 |
| `nilah_ult_3.png` | | 手臂甩到头上，短刃竖直 |
| `nilah_ult_4.png` | | 手臂甩到身后，短刃水平朝左 |
| `nilah_ult_5.png` | | 手臂甩到身前，短刃水平朝右 |
| `nilah_ult_6.png` | | 手臂甩到头上，短刃竖直 |
| `nilah_ult_7.png` | | 最后一拉：手臂从右前方往回拉到胸前，身体后仰（把敌人拉过来） |
| `nilah_ult_8.png` | | 回到站姿 |
| `nilah_dead_1.png` | 死亡 | 被打中，向后踉跄，短刃还在手里 |
| `nilah_dead_2.png` | | 腿一软往后倒，短刃脱手 |
| `nilah_dead_3.png` | | 跪坐下去 |
| `nilah_dead_4.png` | | 侧身往地上倒 |
| `nilah_dead_5.png` | | 躺在地上，短刃水平躺在她身边（画面右边） |
| `nilah_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/nilah_<动作>_<n>.png`（骨架）
2. `design/nilah_side_design.png`（侧面造型）
3. `design/nilah_side_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `design/nilah_front_design.png`（正面，看长相）

```text
Image 2 is the final pixel-art design of this character: Nilah, a cheerful melee fighter seen SIDE-ON facing right - deep brown skin, blue-black hair with a straight fringe and short side locks and one very long ponytail down her back, purple eyes, a smile, teal earrings, a bright yellow one-shouldered top with a bronze-teal crossed collar, one arm wrapped in yellow cloth bands, the other in a dark red arm wrap holding her FOLDED WHIP-BLADE upright behind her (a bronze-teal grip, a short teal point below, folded dark red-purple blade segments above - one short straight piece), a purple-and-teal sash, a purple skirt panel with bronze edges, a bronze cage holding a dark orb at the hip, loose dark plum harem trousers, curved bronze-teal knee and shin armour, flat black slippers. Her head is a 3/4 head (both eyes visible) on the side-on body. It is drawn on a grid of 7x7-pixel squares, 56 x 106 squares, 29 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place. Image 5 is the same character from the front (her look only).
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its realistic proportions, and NOT the long stretched whip in it. (Image 4, when attached, is the previous frame of the same action: keep her exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 7-pixel grid as Image 3, every square one flat colour from Image 2's 29 colours; the character exactly as big as Image 2 (101 squares from the top of her hair to the soles when standing) with Image 2's stocky proportions and big head; she stays SIDE-ON facing image right like Image 2, never turned away; her head - face, purple eyes, fringe, side locks, earrings, smile - copied square for square from Image 2, only moved, never redrawn as a profile; the folded whip-blade copied square for square from Image 2 as ONE STRAIGHT piece, only moved or, where this frame says so, turned a quarter turn to lie level - never tilted, bent, stretched or scaled; NO long whip; the near leg in front in full tone, the far leg behind one shade darker, legs straight from hip to ankle; the soles on the red line of the guide (square row 140) unless this frame is in the air, nothing below it; the same near-black outline as Image 2 (about 2 squares); no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no whip trail, no swirl, no mist, no glow, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文，例如：

- run：`running to the right, frame <n> of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), both legs straight; the folded blade upright in her back hand as in Image 2, bobbing with the stride; the front arm swinging; the ponytail streaming behind`
- attack 1–5：`basic attack, a whip strike, frame <n> of 5: <1: the blade hand raised high behind her head, the blade upright | 2: the arm swinging over from behind her head, the blade still upright above her shoulder | 3: the arm swung down in front of her, the blade turned a quarter turn to lie level, point to the right | 4: the hit: the arm stretched forward to the right, the blade level pointing right, leaning forward in a lunge | 5: back to the standing pose of Image 2, the blade upright behind her again>`
- attack_q 1–5：`empowered attack, a wide sweep, frame <n> of 5: <1: both arms spread, the blade hand high behind her, the blade upright | 2: twisting her waist to gather power, a little lower | 3: the arm sweeping forward from behind, the blade turned level, point to the right | 4: the sweep at its farthest: the arm straight in front a little below the shoulder, the blade level pointing right | 5: back to the standing pose>`
- skill 1–5：`Formless Blade, a full-power lash, frame <n> of 5: <1: crouching to gather power, the blade hand pulled back low behind her, the blade upright | 2: a big step forward to the right, leaning forward, the arm drawn all the way back | 3: the arm whipping forward over her head, the blade upright above her head | 4: the release: a deep lunge, the arm stretched forward to the right at shoulder height, the blade level pointing right | 5: back to the standing pose>`
- q_spin 1–5：`a spinning slash on the spot, frame <n> of 5: <1: crouching, the blade hand in front of her, the blade level pointing right | 2: the arm raised above her head, the blade upright | 3: the arm swung behind her, the blade level pointing left | 4: the arm raised above her head again, the blade upright | 5: back to the standing pose>`
- skill2 1–4：`Slipstream, a dash, frame <n> of 4: <1: crouching low and leaning forward, ready to dash, the blade level behind her pointing left | 2: dashing forward to the right, the body stretched almost level, the front leg reaching forward, the back leg pushing straight, the blade hand behind her with the blade level pointing left | 3: landing in a crouch, knees bent, leaning forward | 4: standing up, back to the standing pose>`
- w_cast 1–4：`Jubilant Veil, a light twirl, frame <n> of 4: <1: a small hop, arms crossed before her chest, the blade upright | 2: in the air, arms raised high and open, the blade upright above her head (still side-on, face toward the front right) | 3: landing, arms spread to both sides | 4: back to the standing pose>`
- ult 1–8：`Apotheosis, spinning her blade for a second, frame <n> of 8: <1: crouching, the blade hand pulled behind her | 2: jumping up, the arm swung in front, the blade level pointing right | 3: the arm above her head, the blade upright | 4: the arm behind her, the blade level pointing left | 5: the arm in front again, the blade level pointing right | 6: the arm above her head, the blade upright | 7: the final pull: the arm drawn back from the front right to her chest, leaning back | 8: back to the standing pose>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, staggering back, the blade still in her hand | 2: the legs giving way, falling back, the blade slipping from her hand | 3: sinking to her knees | 4: falling sideways to the ground | 5: lying on the ground, the blade lying level beside her on the image right | 6: the same, still (the last frame)>`

## 交回前请检查

- 50 帧都在，文件名对，每张 1536×1024 透明底、7 px 一格，`_1x` 和大图逐格一致。
- 每帧和造型一样大（站直头发顶到脚底 101 格），比例敦实头大，一直侧身朝右；头是造型的头（同一张 3/4 的脸）。
- 短刃是造型里那把，一根直线，只竖直或水平，**没有长鞭子**。
- 脚底在红线上（跳起、冲刺的空中帧除外），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/nilah-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 7 px 格读回（regrid --size 7），颜色贴回造型的调色板；头和短刃按造型逐格贴回（一张脸贯穿所有帧，短刃刚体只平移 / 90 度转）；腿查变形和缝（rig-deformation-checks、gap-check），跑步不对就按 Caitlyn 的直腿交叉步自己画；待机 = 正面造型（+ 呼吸）；受击 = 侧面造型平移 + 闪白。
- 写 assets/source/ppu/nilah_<tag>.png/.json、1x 表、ppu_restyle crisp（统一画风）、ppu_hd.py PPU 2.5 + lo_ 帧、hd.rs HEROES（league.dll ≥ 0.6.63，先问布隆 / 铁男 / 修正模型 / 加里奥当时最高号）；按动作条的出手帧重排技能数据的时机再跑一次模拟；6 倍 / 游戏尺寸逐帧自查后再给用户看 GIF。
