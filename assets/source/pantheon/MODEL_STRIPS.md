# 潘森（不屈之枪）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户 2026-10-16：「选A 40尺寸 PPU1.5」，然后「造型用第1稿删行列的版本」）：`design/pantheon_design.png`，**就是你第 1 步画的第 1 稿，逐格读回、缩到游戏尺寸**。它是 66 × 66 格，3/4 正面朝右；金色全脸头盔（T 形眼缝、高高的弯月冠饰）；近侧的手（画面左边）低握金色长矛，矛头朝右下；远侧手臂（画面右边）挎着大金圆盾；深蓝披风往左飘；39 色。这里每格 **10 × 10 px**，画布 1536×1536 正好 153 × 153 格。**这就是最终的像素密度，你画的每一格就是游戏里的一格，不会再缩放**。造型就是待机，**待机和受击不用画**；其余动作照英雄联盟里潘森的动作画。
> - **每帧一张图**：`now/pantheon_<动作>_<n>.png` 是**骨架**，也就是英雄联盟里这一帧的 3D 模型，已经按造型的大小、在同一个格子里放好了，**姿势、位置、身高都照它**。`guide/` 里是同一张图加了参考线：**红线 = 脚底线**（第 140 行的下边），**蓝线 = 造型最高的地方**（冠饰顶），**蓝十字 = 站位点**（第 66 列），浅灰线每 10 格一条。这些线只是对位用的，**不要画进图里**。`design/pantheon_design_on_canvas.png` 是造型站在这张画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（骨架只管姿势，造型管样子）：骨架是 3D 渲染，只看它的姿势；**身材按造型画**。**大小和造型一样**：站直时冠饰顶到脚底 66 格，不要画大，也不要画小。
> - **每一帧的头都是造型的头**：金色全脸头盔、深色 T 形眼缝、弯月冠饰、两侧短尖角，**逐格照抄造型最上面那一块（第 0–17 行）**，只平移，朝右前方。**不要重新画一个头盔，也不要画成侧面。**
> - **长矛和圆盾是硬的**：长矛就是造型里那支（金杆、深红握把、右端带淡蓝宝石的大矛头、另一端的小尖刺），**长短、粗细不能变**，整支跟着手移动、转角度，不能变短、弯曲、断开。圆盾就是造型里那面（一圈圈金边），**大小不能变**，整面跟着远侧手臂移动。披风可以跟着动作飘，但颜色、质感照造型。
> - **一律 3/4 正面朝右**（头盔和胸口朝着看画的人，和造型一样），**身体不要转成侧面或背面**（骨架有几帧转过去了，只照它的手脚动作）。近侧的腿和拿矛的手臂在画面左边、颜色亮；远侧的腿和挎盾的手臂在画面右边、暗一档。
> - **跑步**：照英雄联盟，身体前倾跑，长矛横握在近侧手里，盾护在身前。**两条腿轮流在前**：第 1–4 帧近侧的腿在前，第 5–8 帧远侧的腿在前（第 3、7 帧两腿交叉而过）。**不能 8 帧都是同一条腿在前。** 脚尖最多离地 2–3 格。
> - **Q 投矛**：出手那帧（`skill_throw` 第 4 帧）**手里是空的**（飞出去的长矛是第 3 步的特效），第 5 帧也空着，第 6 帧长矛**回到手里**，和造型一样。
> - **R 起跳**：`ult_leap` 第 3 帧他跳得最高；**下落**（`ult_land` 第 1 帧）矛尖朝下从空中落下，第 2 帧落地蹲着、矛插在地上。
> - **死亡**：骨架里盾和矛飞了出去、身体浮在半空（3D 模型往镜头这边倒，投到画面上就高了）。**我们让他仰面倒下、背直接贴在红线上躺平，盾和矛掉在他身边的地上（也在红线上）**。
> - 每格 10 × 10 px 一个纯色方块，所有格子对齐同一个网格（`design/pantheon_design_on_canvas.png` 的格子）；**只用造型的 39 色**（`design/pantheon_palette.png`）；外面一圈近黑描边（和造型一样粗）；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（飞出去的矛、彗星、星光、盾上的光、残影、尘土），只画潘森；**红线以下什么都不能有**；出招一律朝画面右边。
> - 交付到 `outputs/pantheon-strips/`：每帧 `pantheon_<动作>_<n>.png`（1536×1536、透明背景、和骨架同一个格子）+ `pantheon_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图的原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到），再打成一个 zip（`pantheon_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**。画一个动作的后一帧时，**附上前一帧**，让人、头、长矛、盾一样大。
> - 额度不够画完全部 61 帧时，**按这个顺序画**：run、attack、skill、skill_throw、skill2、e_hold、e_bash、ult、ult_leap、ult_land、attack_w、dead；画到哪交到哪，在 HANDOFF 里写清楚。

## 要画的帧（61 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `pantheon_run_1..8.png` | 跑步（8 帧循环） | 向右跑，身体前倾，长矛横握在近侧手里，盾护在身前，披风往后飘；两条腿轮流在前（1–4 近侧腿在前，5–8 远侧腿在前，3、7 交叉） |
| `pantheon_attack_1.png` | 普攻：长矛突刺 | 收矛蓄力：近侧手把长矛往后拉，盾在身前 |
| `pantheon_attack_2.png` | | 身体压低，长矛对准前方 |
| `pantheon_attack_3.png` | | 出手：弓步前冲，长矛向画面右边刺出、手臂伸直 |
| `pantheon_attack_4.png` | | 收势，长矛往回收 |
| `pantheon_attack_5.png` | | 回到造型的站姿 |
| `pantheon_attack_w_1..6.png` | 强化普攻：连刺三下 | 1 收矛，2 第一刺（向右刺出），3 收矛，4 第二刺，5 第三刺（最远），6 回到站姿 |
| `pantheon_skill_1.png` | Q 近戳 | 收矛，身体侧压 |
| `pantheon_skill_2.png` | | 蓄力，长矛对准前方 |
| `pantheon_skill_3.png` | | 出手：大弓步，长矛向右猛刺到最远 |
| `pantheon_skill_4.png` | | 回到造型的站姿 |
| `pantheon_skill_throw_1.png` | Q 投矛 | 近侧手把长矛举起来，往肩后拉 |
| `pantheon_skill_throw_2.png` | | 蓄力：长矛举过肩头，矛头朝右，盾举在身前，两腿分开站稳 |
| `pantheon_skill_throw_3.png` | | 身体前倾，手臂开始往前甩 |
| `pantheon_skill_throw_4.png` | | 出手：手臂向画面右边伸直，**手里空了**（飞出去的矛不画） |
| `pantheon_skill_throw_5.png` | | 收势，手里仍空着 |
| `pantheon_skill_throw_6.png` | | 回到造型的站姿，长矛回到手里 |
| `pantheon_skill2_1..6.png` | W 斗盾跃击 | 1 下蹲起跳，2 跃起、盾举高，3 空中、盾举过头，4 盾高举准备砸，5 落地：盾和身体一起往右下砸（出手），6 回到站姿 |
| `pantheon_e_hold_1..4.png` | E 神佑枪阵：举盾连刺（循环） | 盾牢牢挡在身前朝右，身体压低；长矛从盾的上沿往右刺：1 收、2 刺出、3 收、4 刺出 |
| `pantheon_e_bash_1..5.png` | E 结束：盾击 | 1 盾往回收，2 蓄力，3 出手：盾向右猛撞出去，4 收势，5 回到站姿 |
| `pantheon_ult_1..4.png` | R 大荒星陨：蓄力 | 1 长矛竖起来，2 长矛竖直举着，3 蹲低、盾罩在身上、披风扬起，4 同上蹲得更低 |
| `pantheon_ult_leap_1..3.png` | R 起跳 | 1 蹬地，2 跃起，长矛向上，3 跳得最高 |
| `pantheon_ult_land_1..4.png` | R 落地 | 1 从空中落下、矛尖朝下，2 落地：单膝蹲下、矛插在地上（出手），3 起身，4 回到站姿 |
| `pantheon_dead_1.png` | 死亡 | 被打中，身体一僵往后仰 |
| `pantheon_dead_2.png` | | 往后倒，盾和矛脱手 |
| `pantheon_dead_3.png` | | 摔到地上（背贴着红线，不要浮在半空） |
| `pantheon_dead_4.png` | | 仰面躺在地上，盾和矛掉在身边 |
| `pantheon_dead_5.png` | | 同上，一条腿抽动一下 |
| `pantheon_dead_6.png` | | 同第 4 帧，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/pantheon_<动作>_<n>.png`（骨架）
2. `design/pantheon_design.png`（造型）
3. `design/pantheon_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/pantheon-model-1.png`（你第 1 步画的那稿，看长相）

```text
Image 2 is the final pixel-art design of this character: a Spartan-style warrior in 3/4 front view facing right - a golden full-face helmet with a dark T-shaped eye slit, a tall golden crescent crest and two short side horns; a bare muscular bronze-tan torso with a dark red scar and a brown strap across the chest; a deep royal-blue cape flying back to the image left; a golden pauldron and arm guard on the near arm; a dark red rope belt with a round golden buckle; a deep blue loincloth with a golden crescent emblem; golden greaves and open-toed sandals; a long GOLDEN SPEAR (dark red grip, a big golden leaf-shaped head with a pale blue gem, a small spike at the butt) held low in his NEAR hand, the head pointing to the lower right; a big ROUND GOLDEN SHIELD on his FAR arm. It is drawn on a grid of 10x10-pixel squares, 66 x 66 squares, 39 colours. Image 3 shows the design standing on a 1536x1536 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions (keep the design's build). (Image 4, when attached, is the previous frame of the same action: keep him, the spear and the shield exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1536 transparent canvas and the SAME 10-pixel grid as Image 3, every square one flat colour from Image 2's 39 colours; the character exactly as big as Image 2 (66 squares from the top of the crest to his soles standing); he stays in the 3/4 FRONT view of Image 2 (helmet and chest toward the viewer), never turned side-on or away; his helmet - the gold, the T-shaped eye slit, the crescent crest, the side horns - copied square for square from Image 2, only moved; the spear is the design's, the same length and thickness, moved and turned as one rigid piece, never shorter, bent or broken; the shield is the design's, the same size, moved with the far arm as one piece; the near leg and the spear arm on the image left in full tone, the far leg and the shield arm on the image right one shade darker; the soles on the red line of the guide (square row 140) - when lying, the back on it - nothing below it; a near-black outline as thick as Image 2's; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no flying spear, no comet, no starlight, no glow, no afterimage, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run：`running forward to the right, frame <n> of an 8-frame loop: the body leaning forward, the spear held level in the near hand, the shield guarding in front, the cape streaming back; the legs as in Image 1 - the NEAR leg in front in frames 1-4 and the FAR leg in front in frames 5-8, the legs crossing in frames 3 and 7 (never the same leg in front in all eight); the toes at most 2-3 squares off the ground`
- attack 1–5：`basic attack, a spear thrust with the NEAR hand, frame <n> of 5: <1: drawing the spear back, the shield in front | 2: crouching, the spear aimed ahead | 3: the strike: lunging forward, the spear thrust straight out to the image right, the arm straight | 4: pulling the spear back | 5: back to the stance of Image 2>`
- attack_w 1–6：`an empowered attack, three fast spear thrusts, frame <n> of 6: <1: drawing the spear back | 2: the first thrust out to the image right | 3: drawing back | 4: the second thrust | 5: the third thrust, the farthest | 6: back to the stance of Image 2>`
- skill 1–4：`Comet Spear, the quick thrust, frame <n> of 4: <1: drawing the spear back, the body turning in | 2: gathering, the spear aimed ahead | 3: the strike: a deep lunge, the spear stabbed out to the image right as far as it goes | 4: back to the stance of Image 2>`
- skill_throw 1–6：`Comet Spear, the throw, frame <n> of 6: <1: lifting the spear and drawing it back over the shoulder | 2: the spear cocked high over his shoulder, the head pointing right, the shield held out in front, the legs planted wide | 3: leaning forward, the arm starting to whip forward | 4: the release: the throwing arm straight out to the image right, the hand now EMPTY (the flying spear is NOT drawn) | 5: the follow-through, the hand still empty | 6: back to the stance of Image 2, the spear back in his hand>`
- skill2 1–6：`Shield Vault, frame <n> of 6 as in Image 1: <1: crouching to spring | 2: leaping up, the shield raised | 3: in the air, the shield over his head | 4: the shield held high, about to slam down | 5: the impact: landing, the shield and his body slamming down to the image lower right, the spear in the near hand | 6: back to the stance of Image 2>`
- e_hold 1–4：`Aegis Assault, a loop: the shield planted firmly in front of him facing right, the body low behind it, the spear stabbing out past the top edge of the shield to the image right, frame <n> of 4: <1: the spear drawn back | 2: the spear stabbed out | 3: drawn back | 4: stabbed out>`
- e_bash 1–5：`Aegis Assault's shield bash, frame <n> of 5: <1: drawing the shield back | 2: gathering | 3: the strike: the shield rammed out to the image right | 4: the follow-through | 5: back to the stance of Image 2>`
- ult 1–4：`Grand Starfall, gathering his strength, frame <n> of 4 as in Image 1: <1: raising the spear upright | 2: the spear held straight up | 3: crouching low, the shield over him, the cape flaring up | 4: the same, lower>`
- ult_leap 1–3：`Grand Starfall, the leap into the sky, frame <n> of 3 as in Image 1: <1: pushing off the ground | 2: springing up, the spear raised | 3: at the top of the leap>`
- ult_land 1–4：`Grand Starfall, the landing, frame <n> of 4 as in Image 1: <1: dropping out of the sky, the spear point down | 2: the impact: landed on one knee, the spear driven into the ground | 3: rising | 4: back to the stance of Image 2>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, the body stiffening, leaning back | 2: falling backward, the shield and the spear slipping from his hands | 3: hitting the ground | 4: lying on his back, the shield and the spear on the ground beside him (frames 3-6: Image 1 floats above the ground and throws the shield away - lay his back ON the red line, the shield and the spear on the red line beside him) | 5: the same, one leg twitching | 6: the same as frame 4, still (the last frame)>`

## 交回前请检查

- 61 帧都在（或按顺序画到哪交到哪，HANDOFF 写明），文件名对，每张 1536×1536 透明底、10 px 一格，`_1x` 和大图逐格一致。
- 每帧和造型一样大（站直冠饰顶到脚底 66 格），一直是 3/4 正面；头盔是造型的头盔（同一个）；长矛长短粗细不变、盾大小不变。
- Q 投矛出手的第 4、5 帧手里空着，第 6 帧长矛回到手里。
- 跑步两条腿轮流在前（1–4 近侧腿、5–8 远侧腿），不是 8 帧同一条腿在前。
- 脚底在红线上（死亡躺下的帧是背贴红线），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/pantheon-strips/HANDOFF.md`，再打包 `outputs/pantheon_strips_done.zip`。

## Claude 收到后（给 Claude 看）

- 每张按 10 px 格读回（regrid --size 10），颜色贴回造型的 39 色；头盔按造型逐格贴回（**整个头盔连冠饰一起贴**）；量每帧头和身体、髋和腿的相对位置（Codex 贴的部件会漂）；跑步逐帧量两只脚的 x，确认换步；长矛和盾查变形和缝。
- 待机 = 造型 + 呼吸（import_native 的 idle_breathe，长矛和盾整块跟着）；受击 = 造型平移 + 闪白；帧已经是 PPU 1.5，不再缩放：ppu_restyle 只加外描边（edge 1）；ppu_hd 生成 hd_ / lo_ 帧（lo_ 用 grow()），在 hd.rs HEROES 里登记 league_pantheon 1.5（league.dll 0.7.14）；按帧重定出手时间，重跑平衡；逐帧自查后再给用户看 GIF。
- Codex 额度不够时：按塔姆、卡莉丝塔的做法，用定稿自己的像素摆动作（`rig_pantheon.py`，只做无损变换），并告诉用户。
