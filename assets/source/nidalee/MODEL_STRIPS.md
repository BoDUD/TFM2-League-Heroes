# 奈德丽（狂野女猎手）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户：「可以，动作交给 Codex 画」），两种形态各一张，**都是你第 0 步画的 A 版逐格读回**，共用一套 56 色：
> - **人形**：`design/nidalee_human_design.png`（**101 × 168 格**，3/4 正面朝右，标枪竖在远侧手里）；
> - **美洲狮**：`design/nidalee_cougar_design.png`（**230 × 113 格**，正侧面朝右站着）。
> 这里每格 **5 × 5 px**（不是 6：标枪和她一样长，横着端时要 200 格宽，1536×1020 正好 307 × 204 格）。两张造型就是待机，**待机和受击不用画**。其余动作照英雄联盟里奈德丽 / 美洲狮的动作画。
> - **每帧一张图**：`now/nidalee_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 196 行的下边），**蓝线 = 造型站直时的最高点**，**蓝十字 = 站位点**（人形第 140 列、美洲狮第 160 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/nidalee_<形态>_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势。**和造型一样大**：人形站直时马尾顶到脚底 159 格（头顶到脚底 143 格）；美洲狮站着 113 格高、鼻尖到屁股约 160 格；不要画大也不要画小。
> - **人形的头每帧都是造型的头**：脸、绿眼睛、白色纹彩、额头绿点、耳坠、大马尾和红绳、羽毛逐格照抄造型（第 9–55 行那一块），只平移，脸朝右前方；**不要重新画一张脸**，不要画侧脸。马尾可以随动作稍微摆，但形状照造型。
> - **美洲狮的头每帧都是造型的头**（侧面朝右：绿眼睛、额头绿宝石、剑齿、白口鼻、尖刺鬃毛、项圈和兽牙羽毛），逐格照抄，只平移；张嘴咬的那几帧下巴可以张开，其余照抄。
> - **标枪就是造型里的那根**（木杆红环、黑白羽毛、浅灰白石头枪头，168 格长）：**一根笔直的直线**，整根照抄，**只能平移，或者整根转 90 度变成水平（枪头朝右）**；不能歪、不能斜、不能弯、不能缩放。英雄联盟里她投出去的是手里这根枪，这里也一样：**投出去以后手里是空的**，下一个动作开始前枪回到手里（照下面每帧写的）。
> - **人形一律 3/4 正面朝右**（脸和胸口朝看画的人，和造型一样），**身体不要转成侧面**；骨架是 3/4 视角的，照它的手脚动作就好。腿：近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、暗一档、略高。跑步一前一后交叉迈步。
> - **美洲狮一律正侧面朝右**：近侧的两条腿颜色亮、在前；远侧的两条腿暗一档、在后面露出一点。跑步是四足奔跑：前后腿交替收拢、伸展。
> - 每格 5 × 5 px 一个纯色方块，所有格子对齐同一个网格（`design/*_design_on_canvas.png` 的格子）；**只用造型的 56 色**（`design/nidalee_palette.png`）；一圈 1 格近黑描边；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（标枪的光、夹子、治疗的绿光、变身的光、抓痕、尘土），只画人 / 豹子和标枪；**红线以下什么都不能有**；出招一律朝画面右边。
> - 骨架只是参考：英雄联盟里她和美洲狮死的时候会翻跟头，**我们不翻**——照下表写的倒下；骨架里标枪斜着的地方也一律照下表（竖直或水平）。
> - 交付到 `outputs/nidalee-strips/`：每帧 `nidalee_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `nidalee_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`nidalee_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**；一个动作里的几帧，**画后一帧时附上前一帧**，让人、豹子、头、标枪一样大。

## 要画的帧（人形 32 帧 + 美洲狮 36 帧 = 68 帧）

### 人形（3/4 正面朝右，`design/nidalee_human_design.png`）

| 文件 | 动作 | 这一帧画什么（身体照骨架；标枪按这里） |
|---|---|---|
| `nidalee_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，腿照骨架一前一后交叉；标枪**竖直**握在远侧手里（和造型一样），随步子上下颠，近侧手臂前后摆 |
| `nidalee_attack_1.png` | 普攻：掷枪 | 准备：把标枪整根转成**水平**、枪头朝右，举到肩上（近侧手在肩后握枪） |
| `nidalee_attack_2.png` | | 往后拉到底，身体后仰，远侧手臂向前伸着瞄准 |
| `nidalee_attack_3.png` | | 出手：投掷的手臂向前挥出，**枪已经飞出去了，手里是空的** |
| `nidalee_attack_4.png` | | 收势：身体前倾，手里空的 |
| `nidalee_attack_5.png` | | 回到造型的站姿，标枪竖着回到远侧手里 |
| `nidalee_skill_1.png` | Q 标枪投掷（用力的一投） | 下蹲蓄力，标枪水平、枪头朝右，举到肩上 |
| `nidalee_skill_2.png` | | 身体大幅后仰，标枪拉到最后 |
| `nidalee_skill_3.png` | | 跨步向前，标枪开始往前送 |
| `nidalee_skill_4.png` | | 出手：手臂伸到最前，**手里是空的** |
| `nidalee_skill_5.png` | | 收势，身体前倾，手里空的 |
| `nidalee_skill_6.png` | | 回到造型的站姿，标枪竖着回到远侧手里 |
| `nidalee_skill2_1.png` | 治疗 / 放夹子（同一个施法动作） | 近侧手抬起，标枪仍竖在远侧手里 |
| `nidalee_skill2_2.png` | | 近侧手向前伸出、手掌张开（施法） |
| `nidalee_skill2_3.png` | | 保持伸手 |
| `nidalee_skill2_4.png` | | 收回到站姿 |
| `nidalee_transform_1.png` | 变成美洲狮 | 屈膝下蹲，身体前倾，标枪还竖在手里 |
| `nidalee_transform_2.png` | | 双手撑地，像要扑出去，标枪松开（不画标枪） |
| `nidalee_transform_3.png` | | 四肢着地往前一窜（这一刻变身的光会盖住她） |
| `nidalee_dead_1.png` | 死亡 | 被打中，向后踉跄，标枪还在手里 |
| `nidalee_dead_2.png` | | 往后倒，标枪脱手往画面右边倒下 |
| `nidalee_dead_3.png` | | 倒到快贴地 |
| `nidalee_dead_4.png` | | 摔在地上 |
| `nidalee_dead_5.png` | | 躺在地上，标枪平躺在她旁边（画面右边，整根转 90 度水平） |
| `nidalee_dead_6.png` | | 同上，静止（最后一帧） |

### 美洲狮（正侧面朝右，`design/nidalee_cougar_design.png`）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `nidalee_c_run_1..8.png` | 奔跑（8 帧循环） | 朝右奔跑：前后腿交替收拢、伸展，身体随步子起伏，尾巴在后面平着甩 |
| `nidalee_c_attack_1.png` | 普攻：爪击 | 近侧前爪抬起 |
| `nidalee_c_attack_2.png` | | 前爪向右挥出 |
| `nidalee_c_attack_3.png` | | 爪子挥到最前（命中） |
| `nidalee_c_attack_4.png` | | 收回到站姿 |
| `nidalee_c_skill_1.png` | 推倒（扑咬） | 后腿蹲下蓄力 |
| `nidalee_c_skill_2.png` | | 前半身扑起，张开嘴 |
| `nidalee_c_skill_3.png` | | 扑下去咬住，两只前爪按下 |
| `nidalee_c_skill_4.png` | | 咬住压低 |
| `nidalee_c_skill_5.png` | | 回到站姿 |
| `nidalee_c_pounce_1.png` | 猛扑（跳跃） | 压低身子准备起跳（像第 0 步的 B 版） |
| `nidalee_c_pounce_2.png` | | 后腿蹬地，向右前上方跃起 |
| `nidalee_c_pounce_3.png` | | 空中，身体完全伸展，前爪向前 |
| `nidalee_c_pounce_4.png` | | 下落，前爪向下 |
| `nidalee_c_pounce_5.png` | | 落地，前爪着地，身体压低 |
| `nidalee_c_pounce_6.png` | | 站稳 |
| `nidalee_c_swipe_1.png` | 挥击（双爪横扫） | 前半身抬起，两只前爪举高 |
| `nidalee_c_swipe_2.png` | | 两只前爪向右前方横扫 |
| `nidalee_c_swipe_3.png` | | 扫到最前，身体压低 |
| `nidalee_c_swipe_4.png` | | 收回到站姿 |
| `nidalee_c_transform_1.png` | 变回人形 | 后腿坐下，前半身抬起 |
| `nidalee_c_transform_2.png` | | 坐直，抬头 |
| `nidalee_c_transform_3.png` | | 前爪离地举起（这一刻变身的光会盖住它） |
| `nidalee_c_dead_1.png` | 死亡 | 被打中，身体一缩 |
| `nidalee_c_dead_2.png` | | 腿一软往下倒 |
| `nidalee_c_dead_3.png` | | 侧身倒到地上 |
| `nidalee_c_dead_4.png` | | 躺在地上 |
| `nidalee_c_dead_5.png` | | 侧躺在地上不动 |
| `nidalee_c_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/nidalee_<动作>_<n>.png`（骨架）
2. `design/nidalee_<形态>_design.png`（这个形态的造型：人形 `human`，美洲狮 `cougar`）
3. `design/nidalee_<形态>_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/nidalee-<形态>-A.png`（原画，看长相）

人形的帧：

```text
Image 2 is the final pixel-art design of this character: Nidalee, a jungle huntress in 3/4 front view facing right - tan red-brown skin with white tribal paint, a huge black ponytail tied with red and a black-and-white feather, green eyes, a green dot on the forehead, tusk earrings and a bone-tooth necklace, a white-fur-trimmed leather top, fur bracers, a tusk belt over a ragged fringed loincloth, big brown fur leg wraps bound with olive-green cords, and her javelin (wooden shaft with red bands, a black-and-white feather, a pale stone blade, as long as she is tall) upright in her far hand. It is drawn on a grid of 5x5-pixel squares, 101 x 168 squares, 56 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions. (Image 4, when attached, is the previous frame of the same action: keep her exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 5-pixel grid as Image 3, every square one flat colour from Image 2's 56 colours; the character exactly as big as Image 2 (159 squares from the ponytail's top to the soles when standing); she stays in the 3/4 FRONT view of Image 2 (face and chest toward the viewer), never turned side-on; her head - face, eyes, paint, ponytail, feather, earrings - copied square for square from Image 2, only moved; the javelin copied square for square from Image 2 as ONE STRAIGHT piece, only moved or, where this frame says so, turned a quarter turn to lie level with the blade to the right - never tilted, bent or scaled; when this frame says she has thrown it, her hand is empty; the near leg on the image left in full tone, the far leg on the image right one shade darker; the soles on the red line of the guide (square row 196), nothing below it; a 1-square near-black outline; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no glow, no trail, no trap, no light, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

美洲狮的帧：

```text
Image 2 is the final pixel-art design of this animal: Nidalee's cougar form, side-on facing right - golden-orange fur with white stripes, a white belly and muzzle, long sabre fangs, green eyes, a small green gem on the forehead, a spiky mane swept back, a dark leather collar hung with ivory tusks and a black-and-white feather, dark-brown paws with pale claws, a long tail with a dark-brown tufted tip. It is drawn on a grid of 5x5-pixel squares, 230 x 113 squares, 56 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is a 3D render of the same animal from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look, NOT its proportions. (Image 4, when attached, is the previous frame of the same action: keep it exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 5-pixel grid as Image 3, every square one flat colour from Image 2's 56 colours; the cougar exactly as big as Image 2 (113 squares high and about 160 squares from nose to rump when standing); EXACTLY SIDE-ON facing image right like Image 2; its head - eye, gem, fangs, muzzle, mane, collar - copied square for square from Image 2, only moved (the jaw may open where this frame bites); the near legs in full tone in front, the far legs one shade darker behind; the paws on the red line of the guide (square row 196) unless this frame is in the air, nothing below it; a 1-square near-black outline; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no claw marks, no glow, no light, no dust), no human, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文，例如：

- run：`running to the right, frame <n> of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride`
- attack 1–5：`basic attack, throwing her javelin, frame <n> of 5: <1: the javelin turned a quarter turn to lie level, blade to the right, raised over her near shoulder (her near hand behind the shoulder grips it) | 2: drawn back to the full, leaning back, the far arm stretched forward to aim | 3: the release: the throwing arm swung forward, the javelin already gone - her hand is empty | 4: the follow-through, leaning forward, hands empty | 5: back to the standing pose of Image 2, the javelin upright in her far hand again>`
- skill 1–6：`Javelin Toss, a full-power throw, frame <n> of 6: <1: crouching to gather power, the javelin level over her shoulder, blade to the right | 2: leaning far back, the javelin drawn all the way back | 3: stepping forward, the javelin starting forward | 4: the release, the arm at its farthest forward, her hand empty | 5: the follow-through, leaning forward, hands empty | 6: back to the standing pose of Image 2, the javelin upright in her far hand>`
- skill2 1–4：`casting a spell (a heal or a trap), frame <n> of 4: <1: raising her near hand, the javelin still upright in her far hand | 2: the near hand thrust forward, palm open | 3: holding the cast | 4: back to the standing pose>`
- transform 1–3：`turning into a cougar, frame <n> of 3: <1: bending her knees, crouching low, leaning forward, the javelin still upright in her hand | 2: dropping her hands to the ground as if to pounce, the javelin let go (do not draw it) | 3: lunging forward on all fours (a burst of light will cover her here - do not draw it)>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, staggering back, the javelin still in her hand | 2: falling backward, the javelin slipping from her hand toward the image right | 3: falling, almost on the ground | 4: landing on the ground | 5: lying on the ground, the javelin lying level beside her on the image right | 6: the same, still (the last frame)>`
- c_run：`running to the right, frame <n> of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind`
- c_attack 1–4：`a claw swipe, frame <n> of 4: <1: lifting the near front paw | 2: swiping the paw forward to the right | 3: the paw at its farthest forward (the hit) | 4: back to the standing pose of Image 2>`
- c_skill 1–5：`Takedown, a pouncing bite, frame <n> of 5: <1: crouching on the hind legs to spring | 2: the front half rearing up, jaws open | 3: lunging down, biting, both front paws pressing down | 4: holding the bite, low | 5: back to the standing pose>`
- c_pounce 1–6：`Pounce, a long leap, frame <n> of 6: <1: crouching low, ready to spring | 2: the hind legs pushing off, leaping forward and up to the right | 3: in the air, the body fully stretched, front paws reaching forward | 4: coming down, front paws reaching down | 5: landing on the front paws, body low | 6: standing again>`
- c_swipe 1–4：`Swipe, both front paws, frame <n> of 4: <1: the front half rising, both front paws raised | 2: both paws sweeping forward to the right | 3: the sweep at its farthest, body low | 4: back to the standing pose>`
- c_transform 1–3：`turning back into the huntress, frame <n> of 3: <1: sitting back on the hind legs, the front half rising | 2: sitting up tall, head raised | 3: the front paws lifted off the ground (a burst of light will cover it here - do not draw it)>`
- c_dead 1–6：`dying, frame <n> of 6: <1: hit, flinching | 2: the legs giving way, sinking | 3: collapsing onto its side on the ground | 4: lying on the ground | 5: lying on its side, still | 6: the same, still (the last frame)>`

## 交回前请检查

- 68 帧都在，文件名对，每张 1536×1024 透明底、5 px 一格，`_1x` 和大图逐格一致。
- 人形每帧和造型一样大（站直马尾顶到脚底 159 格），一直是 3/4 正面；头是造型的头（同一张脸）；标枪是造型的标枪，一根直线，只竖直或水平，投出去后手里是空的。
- 美洲狮每帧和造型一样大（站着 113 格高），一直是正侧面朝右；头是造型的头。
- 脚底 / 爪底在红线上（扑跳的空中帧除外），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/nidalee-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 5 px 格读回（regrid --size 5），颜色贴回造型的 56 色；人形的头和标枪、美洲狮的头按造型逐格贴回（一张脸贯穿所有帧，标枪刚体只平移 / 90 度转）；腿查变形和缝（rig-deformation-checks、gap-check）；外描边加粗到约 1 游戏像素；待机 = 造型 + 呼吸（人形和美洲狮各一套）；受击 = 造型平移 + 闪白。
- 写 assets/source/ppu/nidalee_<tag>.png/.json（人形的标签 + 美洲狮的 c_*）、1x 表、ppu_hd.py PPU、hd.rs HEROES（PPU 约 3.83，league.dll 版本先问「铁男」「布隆」当时最高的再往上取）；6 倍 / 游戏尺寸逐帧自查后再给用户看 GIF。
