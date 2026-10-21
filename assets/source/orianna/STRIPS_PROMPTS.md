# 奥莉安娜（Q 版）：第 2 步，照英雄联盟的动作逐帧画动作（给 Codex 的提示词）

> 造型已经定了（用户挑的 A：你上次画的 Q1，头缩小、身体加长）：
> - `design/orianna_side.png`：**侧面朝右**，48 × 87 格、28 色，这里每格 8 × 8 px。**所有动作都照这张画**（侧面朝右）。
> - `design/orianna_front.png`：3/4 正面（待机用，我来做），只用来看细节和颜色。
> - 待机和受击我自己做，**这次只画 60 帧动作**。
>
> **每帧一张图**：
> - `now/orianna_<动作>_<n>.png` 是**骨架**：英雄联盟里奥莉安娜这一帧的 3D 模型（已经按 Q 版比例、按造型的大小，放在同一个格子上）。**姿势、位置、身高照它**，长相不照它。
> - `guide/` 是同一张加了线，只用来对位，**不要画进图里**：
>   - **红线** = 脚底线（第 117 行的下边）；
>   - **蓝线** = 造型站直时的发髻顶；
>   - **蓝十字** = 站位点；
>   - 浅灰线每 10 格一条。
> - `design/orianna_side_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点、同样大小）。
>
> **长相、比例、颜色、细节全部照侧面造型**（「骨架 + 皮囊」：骨架只看姿势）：
> - **头每帧都是造型的头**：古铜金短发 + 圆发髻、瓷蓝灰的侧脸、一只青蓝色发光的眼睛，逐格照抄 `orianna_side.png`，只平移（身体倒下时整个头跟着转）。不要重新画脸，不要画正脸或背影。
> - **一样大**：站直时发髻顶到脚底 87 格。头不能画大，身体不能画短。
> - **背后的发条钥匙**每帧都在背上（画面左边），跟着身体动。
> - **手臂**：分节的银灰金属手臂，肩、肘、腕有深棕色小圆球关节；手是银白色的细长尖爪。
> - **裙子**：古铜金的齿轮刀片，每片尖刺数得出来。
> - **腿**（最重要）：照骨架的姿势，**长度和粗细和造型的腿一样**：
>   - 大腿、小腿不能拉长也不能压短；
>   - 膝盖、脚踝的小圆球关节都在；
>   - 尖头小靴；
>   - 近侧的腿颜色亮，远侧的腿暗一档。
> - **不画球**（球是单独的图），**不画特效**（电光、冲击波、护盾光、轨迹、尘土）。
>
> **格子和颜色**：
> - 每格 8 × 8 px 一个纯色方块，对齐同一个网格（就是 `orianna_side_on_canvas.png` 的格子）。
> - **只用造型的 28 色**（`design/orianna_palette.png`）。
> - 一圈 1 格的近黑外描边，里面不要第二圈黑。
> - 不要抖动、渐变、噪点、抗锯齿、半透明。
>
> **位置**：脚底踩在红线上（跳起来的帧离开红线没关系）；红线以下什么都不能有；动作一律朝画面右边。
>
> **交付**到 `outputs/orianna-strips/`：
> - 每帧 `orianna_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）；
> - 加一张 `orianna_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；
> - 生图原稿放 `raw/`，原样放，不要缩放；
> - **最后**写 `HANDOFF.md`：每帧用了哪条提示词、哪里没做到。最好再打成 `orianna_strips_done.zip`。
>
> **两条做法**：
> - 生图后按格子取回（每格取多数颜色，不要取中心点）。**不要用脚本缩放**：上一轮你把大图缩到格子上，结果糊了。
> - 一个动作里画后一帧时，**附上前一帧**，让人、头、腿一样大。

## 要画的帧（60 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `orianna_run_1..8.png` | 跑步（8 帧循环） | 朝右小跑：两腿照骨架一前一后交叉，手臂前后摆，钥匙在背上跟着颠 |
| `orianna_attack_1..8.png` | 普攻：指挥发条（上身一甩） | 1 站姿；2 上身前倾；3 低头往前压（蓄力）；4 抬起来；5–6 上身和头往后仰，手往前一甩（发条弹射出，弹不画）；7 回正；8 站姿 |
| `orianna_skill_1..8.png` | Q 指令：攻击（扔出球） | 1 站姿；2 微蹲；3 低头蓄力；4 跳起，两臂张开，手指向右前方（球飞出去，球不画）；5–6 在空中；7 落地屈膝；8 站姿 |
| `orianna_skill_w_1..8.png` | W 指令：杂音 | 1 站姿；2 下蹲；3 后仰起跳；4 跳到最高、收腿；5–6 在空中往后仰；7 落地蹲下；8 站姿 |
| `orianna_skill_e_1..8.png` | E 指令：防卫 | 1 站姿；2 下蹲；3 起身踮脚，手抬起；4–7 踮着一只脚尖立直（像芭蕾），手臂收在身前；8 站姿 |
| `orianna_ult_1..10.png` | R 指令：冲击波 | 1 站姿；2 抬手；3 上身后仰；4 下蹲；5 身体往前往下压；6–8 蹲到最低、头朝前快贴地；9 起身（冲击波放出，不画）；10 站姿 |
| `orianna_dead_1..10.png` | 死亡（发条停了） | 1 被打中一顿；2 一抖；3 头往后仰；4 头垂下；5–8 身体软下去，像断了线的木偶；9 往后倒；10 仰面躺在地上 |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/orianna_<动作>_<n>.png`（骨架）
2. `design/orianna_side.png`（侧面造型）
3. `design/orianna_side_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交的那张；第 1 帧不附）
5. `design/orianna_front.png`（正面造型，看细节）

```text
Image 2 is the final pixel-art design of this character seen side-on facing right: a chibi clockwork doll girl - a bronze-gold metal bob with a round bun on top, a porcelain blue-grey face in profile with one glowing cyan eye, a golden gear at the throat, a silver-white metal bodice, segmented silver-grey metal arms with small dark-brown ball joints and silver-white claw-like hands, a wind-up key on her back (image left), a short skirt of bronze-gold gear blades, short silver-grey metal legs with ball joints at the knees and ankles and small pointed boots. It is drawn on a grid of 8x8-pixel squares, 48 x 87 squares, 28 colours, a 1-square near-black outline. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place. Image 5 is the same design from the 3/4 front, for the details only.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions. (Image 4, when attached, is the previous frame of the same action: keep the character exactly as big.)
Draw ONE frame, side-on facing image right like Image 2: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 8-pixel grid as Image 3, every square one flat colour from Image 2's 28 colours; the character exactly as big as Image 2 (87 squares from the bun to the soles when standing); her head copied square for square from Image 2 (the same profile face, only moved, or turned whole when her body lies down - never a front face, never the back of the head); the wind-up key always on her back; the legs as long and as thick as Image 2's, with the knee and ankle ball joints and the pointed boots, posed like Image 1 - never stretched, never squashed; the near leg in full tone, the far leg one shade darker; the soles on the red line of the guide (square row 117) unless she is in the air, nothing below it; a 1-square near-black outline round the silhouette; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; NO BALL and no effects (no electricity, no shockwave, no shield glow, no trail, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run 1–8：`running to the right, frame <n> of an 8-frame loop: the legs crossing as in Image 1 (one forward, one back), the arms swinging, the key bobbing on her back`
- attack 1–8：`commanding her ball with a whip of the upper body, frame <n> of 8: <1: standing | 2: leaning forward | 3: the head bowed forward, winding up | 4: straightening up | 5: the upper body and head thrown back, the hand flicking forward | 6: still leaning back, the arm out forward | 7: coming upright | 8: standing>`
- skill 1–8：`Command: Attack (sending the ball), frame <n> of 8: <1: standing | 2: a small dip | 3: the head bowed, winding up | 4: hopping up, the arms spread, the hand pointing ahead to the right | 5: in the air | 6: in the air, coming down | 7: landing, the knees bent | 8: standing>`
- skill_w 1–8：`Command: Dissonance (a jump), frame <n> of 8: <1: standing | 2: crouching | 3: pushing off, leaning back | 4: at the top of the jump, the legs tucked | 5: in the air, leaning back | 6: in the air, coming down | 7: landing in a crouch | 8: standing>`
- skill_e 1–8：`Command: Protect (a pirouette), frame <n> of 8: <1: standing | 2: crouching | 3: rising onto her toes, the hands lifting | 4-7: standing straight up on the tip of one foot like a ballet dancer, the arms held in front | 8: standing>`
- ult 1–10：`Command: Shockwave, frame <n> of 10: <1: standing | 2: the arms lifting | 3: leaning back | 4: crouching down | 5: the body pressing forward and down | 6-8: crouched lowest, the head forward near the ground | 9: rising - the moment the shockwave goes out (do not draw it) | 10: standing>`
- dead 1–10：`dying - her clockwork winding down, frame <n> of 10: <1: hit, a jolt | 2: a twitch | 3: the head thrown back | 4: the head dropping | 5-8: the body going slack like a puppet whose strings were cut | 9: falling backward | 10: lying on her back on the ground>`

## 交回前请检查

- 60 帧都在，文件名对；每张 1536×1024、透明底、8 px 一格，`_1x` 和大图逐格一致。
- 每帧都和侧面造型一样大（站直发髻顶到脚底 87 格）；头是造型的侧脸（不是正脸、不是背影）；钥匙在背上。
- **腿和造型的腿一样长、一样粗**，关节小球和尖头靴都在，没有拉长、压扁或扭曲。
- 脚底在红线上（空中的帧除外），红线以下没有东西；没有球、没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/orianna-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 8 px 格读回（regrid --size 8，先看原稿），颜色贴回侧面造型的 28 色；头按造型逐格贴回（一张脸贯穿所有帧）。
- 洋红底 8 倍逐帧自查：腿的长短粗细和关节对比造型、缝、碎片、变形（rig-deformation-checks、gap-check）；**先自己修好再给用户看**，整理成一个 GIF（左边英雄联盟、右边我们的）。
- 待机 = 正面造型 + 呼吸；受击 = 侧面造型后退 + 闪白；写 assets/source/ppu/orianna_<tag>.png、1x 表、PPU（86 行 / 39 px ≈ 2.2）、hd.rs；按真实出手帧重新计时（poses.json 的 release），跑平衡模拟。
