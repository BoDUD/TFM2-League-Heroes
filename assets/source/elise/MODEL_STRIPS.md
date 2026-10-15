# 伊莉丝（蜘蛛女皇）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户 2026-10-15：「人形选 B，蜘蛛选 A」），两种形态各一张，**都是你第 0 步画的原画逐格读回**，共用一套 40 色：
> - **人形**：`design/elise_human_design.png`（**83 × 124 格**，3/4 正面朝右，一只爪子手高举、背后六条蜘蛛腿高高竖起）；
> - **蜘蛛**：`design/elise_spider_design.png`（**114 × 72 格**，3/4 视角朝右）。
> 这里每格 **7 × 7 px**，画布 1536×1024 正好 219 × 146 格。两张造型就是待机，**待机和受击不用画**。其余动作照英雄联盟里伊莉丝 / 蜘蛛的动作画。
> - **每帧一张图**：`now/elise_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 138 行的下边），**蓝线 = 造型站直时的最高点**，**蓝十字 = 站位点**（人形第 105 列、蜘蛛第 110 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/elise_<形态>_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势；英雄联盟的模型比造型瘦、腿也细，**按造型的身材画**。**和造型一样大**：人形站直时头顶到脚尖 100 格（连背后的蜘蛛腿 124 格）；蜘蛛站着 72 格高、114 格宽；不要画大也不要画小。
> - **人形的头每帧都是造型的头**：深红黑发、两根尖角发髻、深色尖头冠、红眼睛、嘴唇和脸逐格照抄造型（第 0–60 行那一块的头部），只平移，脸朝右前方；**不要重新画一张脸**，不要画侧脸。
> - **背后的六条蜘蛛腿是造型里的那六条**（黑紫色、红色尖爪，形状逐格照抄）：它们长在背上、**跟着身体整块移动**，可以整条张开、收拢、向前探，但**每条腿的粗细、长短、红爪不变**，不能变细、变短、变形，**不能挡住她的脸**。手上的黑色长爪也照造型。
> - **蜘蛛的甲壳和头每帧都是造型的**（黑紫色尖刺甲片、深红色甲边和背脊、背顶红色菱形斑、毒牙、红眼睛），身体平着的时候逐格照抄、只平移；身体抬起 / 翻倒的帧照同样的甲片和颜色画成那个角度。**八条腿和造型一样粗、一样长、红爪一样**。
> - **人形一律 3/4 正面朝右**（脸和胸口朝看画的人，和造型一样），**身体不要转成侧面**；骨架是 3/4 视角的，照它的手脚动作就好。腿：近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、暗一档、略高；她踮着尖脚尖。
> - **蜘蛛一律 3/4 视角朝右**（和造型一样，头在画面右前方，能看到脸、毒牙和背甲顶面）：近侧的四条腿颜色亮、在前；远侧的四条腿暗一档、在后面。跑步是八条腿分两组交替迈步。
> - 每格 7 × 7 px 一个纯色方块，所有格子对齐同一个网格（`design/*_design_on_canvas.png` 的格子）；**只用造型的 40 色**（`design/elise_palette.png`）；一圈近黑描边（和造型一样粗）；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（毒液、蛛网、茧、丝线、小蜘蛛、红光、变身的烟），只画伊莉丝 / 蜘蛛；**红线以下什么都不能有**；出招一律朝画面右边。
> - 骨架只是参考：英雄联盟里蜘蛛死的时候会翻滚出去，**我们原地翻倒**——照下表写的倒下；盘丝升空的帧照下表（不画丝线，丝线第 3 步当特效画）。
> - 交付到 `outputs/elise-strips/`：每帧 `elise_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `elise_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`elise_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**；一个动作里的几帧，**画后一帧时附上前一帧**，让人 / 蜘蛛、头、蜘蛛腿一样大。

## 要画的帧（人形 32 帧 + 蜘蛛 33 帧 = 65 帧）

### 人形（3/4 正面朝右，`design/elise_human_design.png`）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `elise_run_1..8.png` | 跑步（8 帧循环） | 朝右踮着脚尖滑步前进，腿照骨架一前一后交叉迈步，身体保持直立，背后六条蜘蛛腿随步子上下轻轻起伏，两只爪子手微微前后摆 |
| `elise_attack_1.png` | 普攻：甩出毒液 | 近侧的爪子手往后收到肩旁 |
| `elise_attack_2.png` | | 手抬到最高，身体微微后仰 |
| `elise_attack_3.png` | | 出手：爪子手向画面右边甩出、五指张开（毒液第 3 步再画） |
| `elise_attack_4.png` | | 收势，身体前倾 |
| `elise_attack_5.png` | | 回到造型的站姿 |
| `elise_skill_1.png` | Q 神经毒素 | 身体后仰蓄力，两只爪子手在胸前合拢 |
| `elise_skill_2.png` | | 身体前倾，远侧手向前伸 |
| `elise_skill_3.png` | | 出手：两只爪子手一起向画面右边推出 |
| `elise_skill_4.png` | | 保持推出的姿势 |
| `elise_skill_5.png` | | 回到造型的站姿 |
| `elise_skill2_1.png` | E 结茧 / W 自爆蜘蛛（同一个施法动作） | 背后的蜘蛛腿往后收，身体微微下蹲 |
| `elise_skill2_2.png` | | 背后的蜘蛛腿从肩膀上方整条向前探出、指向画面右边，两只手向前 |
| `elise_skill2_3.png` | | 出手：蜘蛛腿和双手一起向右前方一甩（茧 / 小蜘蛛第 3 步再画） |
| `elise_skill2_4.png` | | 收势，蜘蛛腿回到身后 |
| `elise_skill2_5.png` | | 回到造型的站姿 |
| `elise_transform_1.png` | 变成蜘蛛 | 两手高举，背后的蜘蛛腿全部张开到最大 |
| `elise_transform_2.png` | | 屈膝下蹲，背后的蜘蛛腿向前合拢、把自己包起来 |
| `elise_transform_3.png` | | 缩成一团，被自己的六条蜘蛛腿裹住（这一刻变身的光会盖住她） |
| `elise_dead_1.png` | 死亡 | 被打中，向后踉跄 |
| `elise_dead_2.png` | | 往后倒，蜘蛛腿无力地垂下 |
| `elise_dead_3.png` | | 膝盖一软，倒到快贴地 |
| `elise_dead_4.png` | | 摔在地上 |
| `elise_dead_5.png` | | 仰面躺在地上，背后的蜘蛛腿软软地摊在身边 |
| `elise_dead_6.png` | | 同上，静止（最后一帧） |

### 蜘蛛（3/4 视角朝右，`design/elise_spider_design.png`）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `elise_c_run_1..8.png` | 爬行（8 帧循环） | 朝右快速爬行：八条腿分两组交替迈步（一组抬起向前、另一组撑地向后），身体随步子轻轻起伏，甲壳保持水平 |
| `elise_c_attack_1.png` | 普攻：前腿刺击 | 前半身抬起，近侧的一条前腿高高举起 |
| `elise_c_attack_2.png` | | 前腿举到头顶上方，弯成钩子 |
| `elise_c_attack_3.png` | | 刺下：前腿向画面右前方猛地刺下（命中） |
| `elise_c_attack_4.png` | | 回到造型的站姿 |
| `elise_c_skill_1.png` | Q 剧毒之蜇（扑咬） | 压低身子，后腿蓄力 |
| `elise_c_skill_2.png` | | 后腿蹬地，向右前上方扑起 |
| `elise_c_skill_3.png` | | 空中，毒牙张开，前腿向前伸 |
| `elise_c_skill_4.png` | | 落下咬住，前腿往下按，身体压低 |
| `elise_c_skill_5.png` | | 回到造型的站姿 |
| `elise_c_skill2_1.png` | E 盘丝（升空） | 压低身子准备跳 |
| `elise_c_skill2_2.png` | | 笔直往上弹起，腿开始收拢 |
| `elise_c_skill2_3.png` | | 升到半空，八条腿收在身体下面 |
| `elise_c_skill2_4.png` | | 升到画面上方（**整只还在画布里**），腿完全收拢（不画丝线） |
| `elise_c_land_1.png` | 盘丝落地 | 从上方落下，八条腿向下张开 |
| `elise_c_land_2.png` | | 落地，身体压低，腿向四周撑开 |
| `elise_c_land_3.png` | | 回到造型的站姿 |
| `elise_c_transform_1.png` | 变回人形 | 后腿撑地，前半身抬起 |
| `elise_c_transform_2.png` | | 抬得更高，前面几条腿向两侧张开 |
| `elise_c_transform_3.png` | | 前腿向内收拢、把身体包起来（这一刻变身的光会盖住它） |
| `elise_c_dead_1.png` | 死亡 | 被打中，身体一缩 |
| `elise_c_dead_2.png` | | 原地翻倒，侧身 |
| `elise_c_dead_3.png` | | 翻成背朝下，腿向上蜷 |
| `elise_c_dead_4.png` | | 八条腿蜷起来 |
| `elise_c_dead_5.png` | | 背朝下躺着不动，腿蜷着 |
| `elise_c_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/elise_<动作>_<n>.png`（骨架）
2. `design/elise_<形态>_design.png`（这个形态的造型：人形 `human`，蜘蛛 `spider`）
3. `design/elise_<形态>_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/elise-<形态>-<B 或 A>.png`（原画，看长相：人形 `elise-human-B.png`，蜘蛛 `elise-spider-A.png`）

人形的帧：

```text
Image 2 is the final pixel-art design of this character: Elise, a cold, beautiful spider priestess in 3/4 front view facing right - pale grey-lilac skin, dark red-black hair swept up into two horn-like points with red tips, a dark pointed crown, red eyes, dark red lips, a black-purple tight gown with deep red V trim and stripes, long black claw fingers, pointed toes, and SIX long curved black spider legs with red claw tips growing from her back. It is drawn on a grid of 7x7-pixel squares, 83 x 124 squares, 40 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions (the design is stockier and its back legs are bigger: keep the design's build). (Image 4, when attached, is the previous frame of the same action: keep her exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 7-pixel grid as Image 3, every square one flat colour from Image 2's 40 colours; the character exactly as big as Image 2 (100 squares from the top of her head to her toes when standing, 124 with the raised back legs); she stays in the 3/4 FRONT view of Image 2 (face and chest toward the viewer), never turned side-on; her head - hair, horns, crown, face, red eyes - copied square for square from Image 2, only moved; the six back spider legs are the design's six legs, the same thickness, length and red claw tips, moving with her body as whole pieces (spread, folded or reaching forward where this frame says), never thinner, shorter or bent out of shape, never over her face; the near leg on the image left in full tone, the far leg on the image right one shade darker; the toes on the red line of the guide (square row 138), nothing below it; a near-black outline as thick as Image 2's; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no venom, no web, no cocoon, no thread, no spiderlings, no glow, no smoke), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

蜘蛛的帧：

```text
Image 2 is the final pixel-art design of this creature: Elise's spider form, a giant spider in 3/4 view facing right - a black-purple carapace of layered spiky plates with deep red plate edges and back ridge, a red diamond mark on top, eight long curved black / dark teal-grey legs with red claw tips, big curved fangs and small red eyes at the front. It is drawn on a grid of 7x7-pixel squares, 114 x 72 squares, 40 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same spider from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions (the design's legs are longer and spread wider: keep the design's build). (Image 4, when attached, is the previous frame of the same action: keep it exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 7-pixel grid as Image 3, every square one flat colour from Image 2's 40 colours; the spider exactly as big as Image 2 (72 squares high and 114 squares wide when standing); in the 3/4 view of Image 2, facing image right; its carapace and head - plates, red edges, diamond, fangs, red eyes - copied square for square from Image 2 while the body is level, only moved; where the body rears up or turns over, the same plates and colours drawn at that angle; all eight legs as thick and as long as in Image 2 with the same red claw tips; the near legs in full tone in front, the far legs one shade darker behind; the claw tips on the red line of the guide (square row 138) unless this frame is in the air, nothing below it; a near-black outline as thick as Image 2's; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no venom, no web, no silk thread, no spiderlings, no glow, no dust), no human, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run：`gliding forward to the right on her pointed toes, frame <n> of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the body upright, the six back legs bobbing gently with the stride, the clawed hands swinging a little`
- attack 1–5：`basic attack, flinging venom, frame <n> of 5: <1: drawing her near clawed hand back beside her shoulder | 2: the hand at its highest, leaning back a little | 3: the release: the clawed hand flung forward to the image right, fingers spread (no venom drawn) | 4: the follow-through, leaning forward | 5: back to the standing pose of Image 2>`
- skill 1–5：`Neurotoxin, frame <n> of 5: <1: leaning back to gather, both clawed hands together before her chest | 2: leaning forward, the far hand reaching out | 3: the release: both clawed hands thrust forward to the image right | 4: holding the thrust | 5: back to the standing pose of Image 2>`
- skill2 1–5：`casting a cocoon or a spiderling, frame <n> of 5: <1: the six back legs drawn back, a slight crouch | 2: the back legs swung forward over her shoulders pointing to the image right, both hands forward | 3: the release: the back legs and both hands thrust forward together (nothing drawn leaving them) | 4: recovering, the back legs returning behind her | 5: back to the standing pose of Image 2>`
- transform 1–3：`turning into the spider, frame <n> of 3: <1: both hands raised high, the six back legs spread as wide as they go | 2: crouching, the back legs closing forward around her | 3: curled up small, wrapped in her six back legs (a burst of light will cover her here - do not draw it)>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, staggering back | 2: falling backward, the back legs going limp | 3: the knees giving way, almost on the ground | 4: landing on the ground | 5: lying on her back, the back legs sprawled limp beside her | 6: the same, still (the last frame)>`
- c_run：`scuttling to the right, frame <n> of an 8-frame loop as in Image 1: the eight legs stepping in two alternating sets of four (one set lifted and reaching forward, the other planted and pushing back), the body bobbing slightly, the carapace level`
- c_attack 1–4：`a stabbing strike, frame <n> of 4: <1: the front rising, the near front leg raised high | 2: that leg lifted above the head, curled like a hook | 3: the strike: the leg stabbing down forward to the image right (the hit) | 4: back to the standing pose of Image 2>`
- c_skill 1–5：`Venomous Bite, a leaping bite, frame <n> of 5: <1: crouching low, the hind legs gathering | 2: the hind legs pushing off, springing forward and up to the right | 3: in the air, fangs wide open, front legs reaching forward | 4: coming down onto the prey, biting, the front legs pinning down, body low | 5: back to the standing pose of Image 2>`
- c_skill2 1–4：`Rappel, rising out of reach, frame <n> of 4: <1: crouching low to jump | 2: springing straight up, the legs starting to fold | 3: halfway up, the eight legs tucked under the body | 4: high up near the top of the canvas (still entirely inside it), the legs fully tucked (no silk thread drawn)>`
- c_land 1–3：`Rappel, dropping down, frame <n> of 3: <1: dropping from above, the eight legs spreading downward | 2: landing, body low, the legs splayed out around it | 3: back to the standing pose of Image 2>`
- c_transform 1–3：`turning back into the woman, frame <n> of 3: <1: rearing up on the hind legs, the front half rising | 2: rearing higher, the front legs spread wide to the sides | 3: the front legs closing inward, wrapping the body (a burst of light will cover it here - do not draw it)>`
- c_dead 1–6：`dying, frame <n> of 6: <1: hit, flinching | 2: toppling over onto its side where it stands | 3: rolled onto its back, the legs curling up | 4: the eight legs curled up | 5: lying on its back, still, the legs curled | 6: the same, still (the last frame)>`

## 交回前请检查

- 65 帧都在，文件名对，每张 1536×1024 透明底、7 px 一格，`_1x` 和大图逐格一致。
- 人形每帧和造型一样大（站直头顶到脚尖 100 格），一直是 3/4 正面；头是造型的头（同一张脸）；背后六条蜘蛛腿是造型的腿，粗细长短不变、不挡脸。
- 蜘蛛每帧和造型一样大（站着 72 格高、114 格宽），一直是 3/4 视角朝右；甲壳和头是造型的；八条腿粗细长短不变。
- 脚尖 / 爪尖在红线上（扑跳、盘丝的空中帧除外），红线以下没有东西；盘丝升空的最后一帧整只还在画布里；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/elise-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 7 px 格读回（regrid --size 7），颜色贴回造型的 40 色；人形的头、蜘蛛的甲壳按造型逐格贴回（一张脸贯穿所有帧）；背后蜘蛛腿和蜘蛛腿查变形和缝；待机 = 造型 + 呼吸（人形和蜘蛛各一套）；受击 = 造型平移 + 闪白。
- 写 assets/source/ppu/elise_<tag>.png（人形的标签 + 蜘蛛的 c_*）、1x 表；ppu_restyle（泽丽画风、crisp）降到 PPU 1.5，ppu_hd hd_ / lo_，hd.rs HEROES 登记（league.dll 版本号先看 main 上最高的再往上取）；按帧重定出手时间、重跑平衡；逐帧自查后再给用户看 GIF。
