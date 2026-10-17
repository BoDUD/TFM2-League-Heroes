# 卡莉丝塔（复仇之矛）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户 2026-10-15：「选A」）：`design/kalista_design.png`，**就是你第 0 步画的 A 逐格读回**（122 × 98 格，3/4 正面朝右，低低地弓步蹲着，近侧的手低握长矛、矛头指向画面左下方，背上两支备用矛，40 色）。这里每格 **7 × 7 px**，画布 1536×1024 正好 219 × 146 格。造型就是待机，**待机和受击不用画**。其余动作照英雄联盟里卡莉丝塔的动作画。
> - **每帧一张图**：`now/kalista_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 138 行的下边），**蓝线 = 造型的最高点**，**蓝十字 = 站位点**（第 130 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/kalista_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势；**按造型的身材画**（造型比骨架壮一点、手脚更粗）。**和造型一样大**：蹲着时头盔顶到脚底 78 格，站直时约 82 格；不要画大也不要画小。
> - **头每帧都是造型的头**：深古铜色带尖角的头盔、很长的紫色羽冠、两侧的黑色长发、青色的脸、发亮的淡青白色眼睛——逐格照抄造型（第 0–40 行那一块），只平移，脸朝右前方；**不要重新画一张脸**，不要画侧脸。羽冠可以随动作往后飘一点，但形状、颜色、长短照造型。
> - **长矛是造型里那支**（黑色矛杆、青色发光条纹、黑色叶形长刃，**长短粗细不变**）：整支跟着手移动、转角度，不能变短、变细、弯曲。**背上两支备用矛**跟着身体整块移动，形状不变。
> - **投出去的矛不画**：普攻是远侧的手（画面右边那只）甩手投出一支**幽灵矛**——飞出去的矛第 3 步当特效画；**近侧手里的长矛一直握着**。Q 是她把手里的长矛举过肩**整支投出去**：出手前两帧长矛在手里，出手那帧和之后一帧**手里空着**（飞出去的矛是特效），最后一帧长矛**又回到手里**（和造型一样）。
> - **一律 3/4 正面朝右**（脸和胸口朝看画的人，和造型一样），**身体不要转成侧面**；骨架是 3/4 视角的，照它的手脚动作就好。近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、暗一档。
> - **跑步**：她像幽灵一样**贴着地面飘着往前冲**，身体前倾，长矛斜拖在身后；**两条腿轮流在前**：第 1–4 帧近侧的腿在前、第 5–8 帧远侧的腿在前（第 3、7 帧两条腿交叉而过）——**不能 8 帧都是同一条腿在前**。脚尖最多离地 1–2 格，不要大步跳。
> - 每格 7 × 7 px 一个纯色方块，所有格子对齐同一个网格（`design/kalista_design_on_canvas.png` 的格子）；**只用造型的 40 色**（`design/kalista_palette.png`）；一圈近黑描边（和造型一样粗）；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（飞出去的矛、矛插在敌人身上、灵魂锁链、光晕、残影、烟），只画卡莉丝塔；**红线以下什么都不能有**；出招一律朝画面右边。
> - 骨架只是参考：英雄联盟里她死的时候会往后飞出去一段，**我们原地倒下**——照下表写的倒下；长矛倒下时**仍握在手里或贴着身体**，不要掉在旁边。
> - 交付到 `outputs/kalista-strips/`：每帧 `kalista_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `kalista_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`kalista_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**；一个动作里的几帧，**画后一帧时附上前一帧**，让人、头、长矛一样大。

## 要画的帧（46 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `kalista_run_1..8.png` | 跑步（8 帧循环） | 贴地飘着向右冲，身体前倾，长矛斜拖在身后；两条腿轮流在前（1–4 近侧腿在前，5–8 远侧腿在前，3、7 交叉），羽冠向后飘 |
| `kalista_attack_1.png` | 普攻：投出幽灵矛 | 远侧的手往后收到肩旁，身体微微后坐 |
| `kalista_attack_2.png` | | 远侧的手抬起蓄力，身体扭转 |
| `kalista_attack_3.png` | | 出手：身体前扑，远侧的手向画面右边甩出、五指张开（飞出去的矛不画） |
| `kalista_attack_4.png` | | 收势，压低身子 |
| `kalista_attack_5.png` | | 回到造型的蹲姿 |
| `kalista_hop_b_1..4.png` | 投矛后往后小跳 | 1 蹬地，2–3 身体腾空向后（画面左边）跃开、膝盖收起，4 落地成蹲姿 |
| `kalista_hop_f_1..4.png` | 投矛后往前小跳 | 1 蹬地，2–3 身体腾空向前（画面右边）跃出、膝盖收起，4 落地成蹲姿 |
| `kalista_skill_1.png` | Q 穿刺 | 站起身，把长矛举到肩后、矛尖朝前 |
| `kalista_skill_2.png` | | 长矛举过肩，身体后仰蓄力 |
| `kalista_skill_3.png` | | 出手：身体前扑，投矛的手向画面右边伸直，**手里空了**（飞出去的矛不画） |
| `kalista_skill_4.png` | | 收势，弓步压低，手里空着 |
| `kalista_skill_5.png` | | 回到造型的蹲姿，长矛回到手里 |
| `kalista_skill2_1.png` | E 撕裂 | 远侧的手向前伸出、五指张开（像抓住看不见的线） |
| `kalista_skill2_2.png` | | 出手：手猛地握拳往回一扯，身体后坐 |
| `kalista_skill2_3.png` | | 握拳的手拉到身侧，弓步更低 |
| `kalista_skill2_4.png` | | 保持，慢慢松开 |
| `kalista_skill2_5.png` | | 回到造型的蹲姿 |
| `kalista_ult_1..5.png` | R 命运的召唤（召唤） | 照骨架：站起身，**远侧的手高高举过头顶**、五指张开，近侧的手仍握着长矛斜向下；第 5 帧手开始放下 |
| `kalista_ult2_1..4.png` | R 命运的召唤（甩出） | 1 站直蓄力，2–3 照骨架**跳到半空**，远侧的手向画面右边猛地甩出，4 落地回到蹲姿 |
| `kalista_dead_1.png` | 死亡 | 被打中，身体一僵 |
| `kalista_dead_2.png` | | 往后仰，站起身 |
| `kalista_dead_3.png` | | 往后倒，手脚无力 |
| `kalista_dead_4.png` | | 摔到地上 |
| `kalista_dead_5.png` | | 仰面躺在地上，长矛贴着身体 |
| `kalista_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/kalista_<动作>_<n>.png`（骨架）
2. `design/kalista_design.png`（造型）
3. `design/kalista_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/kalista-A.png`（你第 0 步画的原画，看长相）

```text
Image 2 is the final pixel-art design of this character: Kalista, a vengeful ghost warrior woman in 3/4 front view facing right, crouched in a low lunge - glowing cyan-teal ghost skin (brightest on the hands and bare feet), a dark bronze horned helm with a very long violet crest sweeping back, long black hair at both sides of the face, pale white-cyan glowing eyes, dark grey-black armour with bronze trim, a dark maroon torn skirt, black shin guards, two spare spears across her back, and a VERY LONG black spear with cyan streaks held low in her near hand, its leaf-shaped blade pointing to the image lower left. It is drawn on a grid of 7x7-pixel squares, 122 x 98 squares, 40 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions (the design is a little stockier with thicker limbs: keep the design's build). (Image 4, when attached, is the previous frame of the same action: keep her exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 7-pixel grid as Image 3, every square one flat colour from Image 2's 40 colours; the character exactly as big as Image 2 (78 squares from the top of her helm to her soles in the crouch, about 82 standing); she stays in the 3/4 FRONT view of Image 2 (face and chest toward the viewer), never turned side-on; her head - helm, horns, crest, black hair, cyan face, glowing eyes - copied square for square from Image 2, only moved (the crest may sway back a little, same shape and colours); the long spear and the two spare spears on her back are the design's, the same length, thickness and colours, moved and turned as whole pieces, never shorter, thinner or bent; the near leg on the image left in full tone, the far leg on the image right one shade darker; the soles on the red line of the guide (square row 138) unless this frame is in the air, nothing below it; a near-black outline as thick as Image 2's; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no thrown spear, no spears stuck in anything, no soul chain, no glow, no afterimage, no smoke), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run：`running forward to the right like a ghost gliding low over the ground, frame <n> of an 8-frame loop: the body leaning forward, the long spear trailing diagonally behind her in the near hand, the crest streaming back; the legs as in Image 1 - the NEAR leg in front in frames 1-4 and the FAR leg in front in frames 5-8, the legs crossing in frames 3 and 7 (never the same leg in front in all eight); the feet at most 1-2 squares off the ground`
- attack 1–5：`basic attack, hurling a spirit spear with her FAR hand while the near hand keeps holding the long spear low, frame <n> of 5: <1: the far hand drawn back beside her shoulder, sitting back a little | 2: the far hand raised to gather, the body twisting | 3: the release: lunging forward, the far hand flung out to the image right, fingers spread (the thrown spear is NOT drawn) | 4: the follow-through, crouching low | 5: back to the crouch of Image 2>`
- hop_b 1–4：`a quick hop BACKWARD after a throw, frame <n> of 4: <1: pushing off the ground | 2: in the air, springing back toward the image left, knees tucked | 3: still in the air, coming down | 4: landing back in the crouch of Image 2>`
- hop_f 1–4：`a quick hop FORWARD after a throw, frame <n> of 4: <1: pushing off the ground | 2: in the air, springing forward toward the image right, knees tucked | 3: still in the air, coming down | 4: landing back in the crouch of Image 2>`
- skill 1–5：`Pierce, hurling her long spear, frame <n> of 5: <1: rising, the long spear lifted behind her shoulder, its blade pointing forward | 2: the spear raised over the shoulder, leaning back to gather | 3: the release: lunging forward, the throwing arm straight out to the image right, the hand now EMPTY (the flying spear is NOT drawn) | 4: the follow-through, a low lunge, the hand still empty | 5: back to the crouch of Image 2, the long spear back in her hand>`
- skill2 1–5：`Rend, ripping the spears out, frame <n> of 5: <1: the far hand reaching out forward, fingers spread as if gripping invisible threads | 2: the release: the hand clenched into a fist and yanked back, the body sitting back | 3: the fist pulled to her side, the lunge deeper | 4: holding, the fist slowly opening | 5: back to the crouch of Image 2>`
- ult 1–5：`Fate's Call, calling her bound ally, frame <n> of 5 as in Image 1: rising to stand, the FAR hand raised high above her head with the fingers spread, the near hand still holding the long spear slanting down <5: the raised hand starting to come down>`
- ult2 1–4：`Fate's Call, hurling her ally, frame <n> of 4: <1: standing tall, gathering | 2: leaping up into the air as in Image 1, the far hand flinging forward to the image right | 3: high in the air, the arm fully thrown out to the image right | 4: landing back in the crouch of Image 2>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, the body stiffening | 2: rearing back, rising up | 3: falling backward, limbs going limp | 4: hitting the ground | 5: lying on her back, the long spear along her body | 6: the same, still (the last frame)>`

## 交回前请检查

- 46 帧都在，文件名对，每张 1536×1024 透明底、7 px 一格，`_1x` 和大图逐格一致。
- 每帧和造型一样大（蹲着头盔顶到脚底 78 格），一直是 3/4 正面；头是造型的头（同一张脸）；长矛和背上两支备用矛长短粗细不变。
- 普攻：近侧手里的长矛一直握着，远侧的手投出（不画飞出去的矛）；Q 出手那帧和下一帧手里空着，最后一帧长矛回到手里。
- 跑步两条腿轮流在前（1–4 近侧腿、5–8 远侧腿），不是 8 帧同一条腿在前。
- 脚底在红线上（小跳、R 甩出的空中帧除外），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/kalista-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 7 px 格读回（regrid --size 7），颜色贴回造型的 40 色；头按造型逐格贴回（一张脸贯穿所有帧，**整颗头连头盔和羽冠一起贴**，伊莉丝的教训：只贴脸会出现两个头）；量每帧头和身体、髋和腿的相对位置（Codex 贴的部件会漂）；跑步逐帧量两只脚的 x，确认换步；长矛和备用矛查变形和缝。
- 待机 = 造型 + 呼吸；受击 = 造型平移 + 闪白；写 assets/source/ppu/kalista_<tag>.png、1x 表；ppu_restyle 降到用户定的 PPU（先出 1.5 / 1.8 / 2.0 / 2.05 对比），ppu_hd hd_ / lo_，hd.rs HEROES 登记（league.dll 0.7.10）；按帧重定出手时间、重跑平衡；逐帧自查后再给用户看 GIF。
