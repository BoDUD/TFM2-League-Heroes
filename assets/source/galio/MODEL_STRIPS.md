# 加里奥（正义巨像）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了：`design/galio_design.png`（原画 A 逐格读回，拳头按 oppi 的画法手画过，**85 × 104 格、22 色（泽丽式平涂）**，这里每格 7 × 7 px；游戏里每 2 格 = 1 个游戏像素）。它就是待机，**待机不用画**。其余动作照英雄联盟里加里奥的动作画，**全部 3/4 正面朝右**（和造型同一个角度：脸、胸口徽章朝向看画的人；用户定的，不画侧身）。
> - **每帧一张图**：`now/galio_<动作>_<n>.png` 是**骨架**——英雄联盟里加里奥这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 140 行的下边），**蓝线 = 造型站直时的翅尖**，**蓝十字 = 站位点**（第 92 列，两脚中间），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/galio_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势。**和造型一样大**：站直时头冠到脚底 76 格、翅尖到脚底 104 格；不要画大也不要画小。
> - **头每帧都是造型的头**：金头冠（中间一根高尖角、两边各一根矮的）、石头脸、两只蓝眼睛、金领口逐格照抄造型，只平移；不要重新画一张脸，也不要画侧脸。
> - **拳头就是造型里的拳头**：比小臂窄、圆、和手臂连着画（中间没有黑线），左上一点高光，几格暗色表示拇指和指节；两只拳头一样大。出拳时拳头整块平移/朝前，不要画成球、不要画成螺旋。
> - **翅膀**：两只金色刀片羽毛的大翅膀，是刚体——整块平移，或者照骨架展开/收拢（展开时就是同样的羽毛往两边张开），羽毛的形状、颜色和造型一样；不能挡住脸和胸口徽章。**尾巴**：石头尾巴 + 金箭头，拖在画面左边。
> - 腿：反关节兽腿。待机式站立时近侧的腿在画面左边、颜色亮，远侧的腿在画面右边、暗一档、略高（和造型一样）；跑步一前一后交叉迈步，三爪石脚。
> - 每格 7 × 7 px 一个纯色方块，所有格子对齐同一个网格（`design/galio_design_on_canvas.png` 的格子）；**只用造型的 22 色**（`design/galio_palette.png`）；外轮廓一圈 2 格粗的近黑描边（和造型一样）；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（龙卷风、风、护盾光、冲击波、尘土），只画加里奥本人；**红线以下什么都不能有**（跳起来的帧离开红线没关系）；出招一律朝画面右边。
> - 交付到 `outputs/galio-strips/`：每帧 `galio_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `galio_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`galio_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**；一个动作里的几帧，**画后一帧时附上前一帧**，让人、头、翅膀一样大。

## 要画的帧（52 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `galio_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，兽腿照骨架一前一后交叉，两只拳头前后摆，翅膀收在背后随步子上下颠，尾巴拖在后面 |
| `galio_attack_1.png` | 普攻：石拳 | 准备：身体后仰，近侧拳头往后收 |
| `galio_attack_2.png` | | 蓄力到底：拳头收到最后 |
| `galio_attack_3.png` | | 出拳：远侧（画面右边）的手臂向右前方打出，拳头在最右，身体前压 |
| `galio_attack_4.png` | | 命中后：保持出拳，两脚分开踩稳 |
| `galio_attack_5.png` | | 收招：回到造型的站姿 |
| `galio_attack2_1.png` | 被动 巨像重击（跳起砸地） | 下蹲，翅膀往上张开 |
| `galio_attack2_2.png` | | 跳起，两只拳头举过头顶，翅膀张开 |
| `galio_attack2_3.png` | | 在最高处，拳头往下 |
| `galio_attack2_4.png` | | 砸地：双拳砸在身前（画面右边）地上，身体压低，翅膀往前收 |
| `galio_attack2_5.png` | | 保持砸地的低姿态 |
| `galio_attack2_6.png` | | 站起来回到站姿 |
| `galio_skill_1.png` | Q 战争罡风（扇翅送出风） | 翅膀往后上方张开蓄力，身体后仰 |
| `galio_skill_2.png` | | 翅膀开始往前扇 |
| `galio_skill_3.png` | | 翅膀猛地向前（画面右边）扇到底，一只手臂朝右指——风送出去的那一刻（风不画） |
| `galio_skill_4.png` | | 保持扇出的姿势，身体前倾 |
| `galio_skill_5.png` | | 收回到站姿 |
| `galio_skill2_1.png` | E 正义冲拳 | 后撤一步，身体压低，近侧拳头往后拉 |
| `galio_skill2_2.png` | | 蓄力：重心在后脚，翅膀收紧 |
| `galio_skill2_3.png` | | 向右冲出：身体前倾几乎水平，拳头在前 |
| `galio_skill2_4.png` | | 冲拳打中：拳头打到最右，身体完全压上去 |
| `galio_skill2_5.png` | | 冲拳后保持 |
| `galio_skill2_6.png` | | 收招回到站姿 |
| `galio_w_charge_1.png` | W 杜朗护盾：蓄力 | 两腿分开蹲稳，两只前臂交叉挡在胸前，翅膀往两边张开护住身体 |
| `galio_w_charge_2.png` | | 同样的姿势，微微下沉（这两帧会循环） |
| `galio_w_burst_1.png` | W 放开（嘲讽） | 从蓄力姿势开始，身体往上起 |
| `galio_w_burst_2.png` | | 两臂往两边展开，胸口挺出 |
| `galio_w_burst_3.png` | | 完全展开：两臂、翅膀都张到最大，挺胸（嘲讽的一刻） |
| `galio_w_burst_4.png` | | 收回到站姿 |
| `galio_ult_1.png` | R 英雄登场：起势 | 下蹲，两臂向下收 |
| `galio_ult_2.png` | | 翅膀高高展开，两臂张开，准备起飞 |
| `galio_ult_3.png` | | 脚尖离地，往上升，翅膀张到最大 |
| `galio_ult_loop_1.png` | R 引导（悬在空中） | 悬在空中（离地几格），两臂张开，翅膀张开 |
| `galio_ult_loop_2.png` | | 同上，翅膀往下扇一点（两帧循环） |
| `galio_ult_land_1.png` | R 落地 | 从空中落下，两拳朝下 |
| `galio_ult_land_2.png` | | 砸地：双拳和身体砸在地上，蹲到最低，翅膀往前收 |
| `galio_ult_land_3.png` | | 保持落地的低姿态 |
| `galio_ult_land_4.png` | | 开始站起 |
| `galio_ult_land_5.png` | | 回到站姿 |
| `galio_dead_1.png` | 死亡 | 被打中，踉跄后退 |
| `galio_dead_2.png` | | 仰头，翅膀垂下 |
| `galio_dead_3.png` | | 膝盖一软，跪下 |
| `galio_dead_4.png` | | 跪坐在地上，身体前倾，翅膀垂在两边 |
| `galio_dead_5.png` | | 变回不动的石像：跪坐、低头 |
| `galio_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/galio_<动作>_<n>.png`（骨架）
2. `design/galio_design.png`（造型）
3. `design/galio_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/galio_picture_A.png`（原画，看长相）

```text
Image 2 is the final pixel-art design of this character: Galio, the Colossus, a living winged statue of pale green-grey stone with earthy gold trim - a gold crown-helm with one tall middle spike and two short side spikes over a stern stone face with two blue eyes, a gold collar, a gold winged emblem on the chest, huge blocky shoulders, long thick arms ending in rounded clenched stone fists, digitigrade beast legs with gold knee guards and three-clawed stone feet, two huge gold wings of blade-like feathers rising behind him, a stone tail with a gold arrowhead trailing on the image left. It is drawn on a grid of 7x7-pixel squares, 85 x 104 squares, 22 colours (flat areas like the series' model look), a thick 2-square near-black outline. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions. (Image 4, when attached, is the previous frame of the same action: keep the character exactly as big.)
Draw ONE frame, in the same 3/4 FRONT view as Image 2 (facing image right, the face and the chest emblem toward the viewer): <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 7-pixel grid as Image 3, every square one flat colour from Image 2's 22 colours; the character exactly as big as Image 2 (76 squares from the crown to the soles when standing, 104 to the wing tips); his head copied square for square from Image 2 (the same face, only moved - no profile face); the fists like Image 2's (rounded clenched stone fists joined to the forearm, both the same size - never balls, never spirals); the wings are Image 2's wings, moved or spread as in Image 1 but with the same feathers and colours, never covering the face or the chest emblem; the near leg on the image left in full tone, the far leg on the image right one shade darker; the soles on the red line of the guide (square row 140) unless the pose is in the air, nothing below it; a 2-square near-black outline round the silhouette; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no tornado, no wind, no shield glow, no shockwave, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文，例如：

- run：`running to the right, frame <n> of an 8-frame loop: the beast legs crossing as in Image 1 (one forward, one back), the fists swinging, the wings folded behind him bobbing with the stride, the tail trailing behind`
- attack 1–5：`a stone punch, frame <n> of 5: <1: leaning back, the near fist drawn back | 2: the wind-up's peak, the fist drawn back furthest | 3: the punch, the far arm (image right) thrown forward to the right, the fist at its farthest right, the body pressing in | 4: holding the punch, feet wide as in Image 1 | 5: recovering toward the standing pose of Image 2>`
- attack2 1–6：`Colossal Smash (a leap and a two-fisted slam), frame <n> of 6: <1: crouching, the wings opening upward | 2: leaping up, both fists raised over his head, the wings spread | 3: at the top, the fists coming down | 4: the slam, both fists on the ground in front of him (image right), the body low, the wings swept forward | 5: holding the low slam pose | 6: rising back to the standing pose>`
- skill 1–5：`Winds of War (he beats his wings to send the wind), frame <n> of 5: <1: the wings drawn back and up, leaning back | 2: the wings starting to beat forward | 3: the wings beaten fully forward toward the image right, one arm pointing right - the moment the wind flies (do not draw the wind) | 4: holding the beat, leaning forward | 5: recovering to the standing pose>`
- skill2 1–6：`Justice Punch, frame <n> of 6: <1: a step back, the body low, the near fist pulled back | 2: the wind-up, the weight on the back foot, the wings tucked | 3: dashing to the right, the body leaning forward almost level, the fist in front | 4: the punch lands, the fist at its farthest right, his weight fully behind it | 5: holding after the punch | 6: recovering to the standing pose>`
- w_charge 1–2：`Shield of Durand, bracing, frame <n> of 2: feet wide and low, both forearms crossed in front of his chest, the wings spread out to both sides shielding him<2: the same pose sunk one square lower (the two frames loop)>`
- w_burst 1–4：`Shield of Durand, the release (a taunt), frame <n> of 4: <1: rising out of the brace | 2: the arms swinging open to both sides, the chest pushed out | 3: fully open, the arms and wings spread widest, the chest out - the taunt | 4: recovering to the standing pose>`
- ult 1–3：`Hero's Entrance, the take-off, frame <n> of 3: <1: crouching, the arms drawn down | 2: the wings spread high, the arms open, about to fly | 3: the feet leaving the ground, rising, the wings at their widest>`
- ult_loop 1–2：`Hero's Entrance, hovering, frame <n> of 2: hanging in the air a few squares above the red line, the arms open, the wings spread<2: the wings beating down a little (the two frames loop)>`
- ult_land 1–5：`Hero's Entrance, the landing, frame <n> of 5: <1: dropping from the air, the fists down | 2: the impact, the fists and the body slamming onto the ground, crouched lowest, the wings swept forward | 3: holding the low landing pose | 4: starting to rise | 5: back in the standing pose>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, staggering back | 2: the head thrown back, the wings drooping | 3: the knees giving way, kneeling down | 4: kneeling on the ground, leaning forward, the wings hanging at his sides | 5: turned back into a still statue, kneeling, the head bowed | 6: the same, still (the last frame)>`

## 交回前请检查

- 52 帧都在，文件名对，每张 1536×1024 透明底、7 px 一格，`_1x` 和大图逐格一致。
- 每帧都和造型一样大（站直头冠到脚底 76 格）；头是造型的头（同一张脸，3/4 正面）；两只拳头一样大、是造型的圆石拳；翅膀是造型的翅膀。
- 全部 3/4 正面朝右，没有侧脸、没有侧身。
- 脚底在红线上（空中的帧除外），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/galio-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 7 px 格读回（regrid --size 7），颜色贴回造型的 22 色；头按造型逐格贴回（一张脸贯穿所有帧），拳头查大小一致；洋红底 8 倍逐帧自查（缝、碎片、变形：rig-deformation-checks、gap-check），**先自己 review 再给用户看**；待机 = 造型 + 呼吸；受击 = 造型平移 + 闪白。
- 写 assets/source/ppu/galio_<tag>.png/.json、1x 表、ppu_hd.py PPU 2.0、hd.rs HEROES（league.dll ≥ 0.6.41，先合 ppu-chunky / 最新 main，问「布隆」「修正模型」）；按真实出手帧重新计时（attack 3、attack2 4、skill 3、skill2 4、w_burst 3、ult_land 2），再跑平衡模拟。
