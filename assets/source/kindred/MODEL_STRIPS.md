# 千珏（永猎双子）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户选了侧身 A），共用一套颜色：
> - **羊的侧身**：`design/kindred_side_design.png`（**142 × 166 格**，完全侧面朝右，正面那颗 3/4 面具头，弓竖直握在身前，白毛披肩拖在身后）——**羊的所有动作都从它画**；
> - **狼的侧面**：`design/kindred_wolf_design.png`（**82 × 48 格**，只有狼头 + 往后飘的鬃毛）——**狼的两组小动作从它画**；
> - **正面**：`design/kindred_front_design.png`（待机和选人卡用，**这一轮不用画**，只给你看两个角色的样子）。
> 这里每格 **5 × 5 px**（1536×1024 里 307 × 204 格）。**待机和受击不用画**。
> - **羊和狼分开画**：羊的每一帧**只画羊**（不画狼）；狼单独画两组（漂浮循环、扑咬），狼放进羊的帧里由我来做。
> - **每帧一张图**：`now/kindred_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小、按同一个格子放好：**姿势、位置、身高照它**。`guide/` 是同一张加了线：**红线 = 蹄底线**（第 196 行的下边），**蓝线 = 造型站直时面具耳尖的高度**，**蓝十字 = 站位点**（第 165 列），浅灰线每 10 格一条——对位用，**不要画进图里**。`design/kindred_side_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照侧身造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**。**和造型一样大**：站直时面具耳尖到蹄底 154 格；不要画大也不要画小，头和身子的比例照造型（敦实）。
> - **头每帧都是造型的头**：深紫羊面具、尖耳、月牙纹、**两只发光青绿眼睛**逐格照抄造型（造型最上面那一块），**只平移**，脸朝右前方（3/4，两只眼睛都看得见）；**不要重新画一张脸**，不要画侧脸。白色毛发兜帽和身后的长白毛可以随动作飘动，但颜色、毛尖的画法照造型。
> - **弓每帧都是造型里那把弓**（深紫弓身、青绿涡纹、上下两个淡青弯钩弓梢、细弓弦）：**整把照抄，只能平移**，竖直握在近侧（身前）的手里；不能歪、不能斜、不能弯、不能缩放。**拉弓时弓身不变，只有弓弦被拉成一个「<」形**（弦的两端还在弓梢上，中间被后手拉到脸旁）。**箭不要画**——射出去的箭是特效，第 3 步单独画。
> - **一律正侧面朝右**（和侧身造型一样）：近侧手（画面右边）握弓，远侧手拉弦；**羊腿一前一后**（近侧腿颜色亮、在前；远侧腿暗一档、在后），反关节的羊腿（大腿、往后弯的膝盖、长小腿、羊蹄）照造型的腿画，**粗细、长短每帧一样**；黑褐羊蹄朝右。
> - 每格 5 × 5 px 一个纯色方块，所有格子对齐同一个网格（`design/kindred_side_design_on_canvas.png` 的格子）；**只用造型的颜色**（羊 34 色、狼在同一套里，合起来 39 色：`design/kindred_palette.png`）；外轮廓描边和造型一样粗（约 2 格近黑）；不要抖动、渐变、噪点、抗锯齿、半透明（**alpha 只能是 0 或 255**——前两轮交回的图都有一圈半透明光晕）。
> - **不画特效**（箭、光、狼的幻影、尘土），只画角色；**红线以下什么都不能有**；射箭一律朝画面右边。
> - 骨架只是参考：英雄联盟里她有几帧转身背对或者翻跟头，**我们不转身、不倒立**——一直侧身朝右、脸朝右前方，照下表写的画。
> - 交付到 `outputs/kindred-strips/`：每帧 `kindred_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子）+ `kindred_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）；生图原稿放 `raw/`（不要重采样）；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`kindred_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**；一个动作里的几帧，**画后一帧时附上前一帧**，让角色、头、弓一样大。

## 要画的帧（羊 40 帧 + 狼 9 帧）

### 羊（全部侧身朝右，`design/kindred_side_design.png`，不画狼）

| 文件 | 动作 | 这一帧画什么（身体照骨架；弓按这里） |
|---|---|---|
| `kindred_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，羊腿照骨架一前一后交叉迈步；弓**竖直**握在身前的手里（和造型一样），随步子上下颠；后手前后摆；白毛兜帽和身后的长白毛往后飘 |
| `kindred_attack_1.png` | 普攻：射箭 | 近侧手把弓往前伸到身前（手臂伸直朝右），弓竖直；远侧手搭上弓弦 |
| `kindred_attack_2.png` | | 拉弓：远侧手把弦往后拉到胸前，弦成「<」形；身体压低，两腿分开站稳 |
| `kindred_attack_3.png` | | **满弓**（这一刻放箭）：弦拉到脸旁，弓臂伸直，身体前倾、弓步 |
| `kindred_attack_4.png` | | 放完：弦弹回成一条直线，后手张开留在脸后 |
| `kindred_attack_5.png` | | 回到造型的站姿 |
| `kindred_skill_1.png` | Q 乱箭之舞：翻跃射箭 | 下蹲蓄力，弓收在身前 |
| `kindred_skill_2.png` | | 蹬地往右前方跃起：身体前倾、后腿蹬直、前腿收起（**不翻跟头**） |
| `kindred_skill_3.png` | | 空中：身体缩成一团往右飞，两腿收在身下，弓竖直贴在身前 |
| `kindred_skill_4.png` | | 下落：两腿往下伸准备落地 |
| `kindred_skill_5.png` | | 落地成射击的蹲姿，满弓朝右（**这一刻放三支箭**） |
| `kindred_skill_6.png` | | 回到站姿 |
| `kindred_skill2_1.png` | E 横生惧意：瞄准一箭 | 弓伸到身前，后手搭弦 |
| `kindred_skill2_2.png` | | 两腿大大分开、身体压很低（弓步），慢慢拉弓 |
| `kindred_skill2_3.png` | | 满弓瞄准（**这一刻放箭**），身体仍压低 |
| `kindred_skill2_4.png` | | 放完：弦弹直，后手张开，保持低姿势 |
| `kindred_skill2_5.png` | | 站起回到站姿 |
| `kindred_w_cast_1.png` | W 狼灵狂热：召狼 | 微微下蹲，弓收在身前 |
| `kindred_w_cast_2.png` | | 原地轻跳，弓竖直举过头顶（召唤狼），后手张开 |
| `kindred_w_cast_3.png` | | 落地，弓放回身前 |
| `kindred_w_cast_4.png` | | 回到站姿 |
| `kindred_ult_1.png` | R 羊灵生息：守护 | 开始下蹲，弓收在身前 |
| `kindred_ult_2.png` | | 单膝跪下，后手按在地上（**蹄底和手都在红线上**），弓竖直在身前 |
| `kindred_ult_3.png` | | 同上，头低下（静止的一刻） |
| `kindred_ult_4.png` | | 站起，弓开始往上举 |
| `kindred_ult_5.png` | | 站直，弓竖直**高举过头顶** |
| `kindred_ult_6.png` | | 弓放回身前，回到站姿 |
| `kindred_dead_1.png` | 死亡 | 被打中，向后踉跄，弓还在手里 |
| `kindred_dead_2.png` | | 羊腿一软，跪下去 |
| `kindred_dead_3.png` | | 跪坐，身体往前垂，弓垂到地上 |
| `kindred_dead_4.png` | | 侧身往地上倒 |
| `kindred_dead_5.png` | | 躺在地上（侧躺，头在画面右边），弓水平躺在她身边 |
| `kindred_dead_6.png` | | 同上，静止（最后一帧） |

### 狼（正侧面朝右，`design/kindred_wolf_design.png`，不画羊）

画在同一个格子上，**狼站直时鼻尖在第 150 列、第 120 行**（`design/kindred_wolf_design_on_canvas.png`）。狼头（白骨面具、蓝眼、尖耳、鼻子）**逐格照抄造型，只平移**；只有鬃毛的毛尖和下巴（张嘴 / 合嘴）可以动。没有身体、没有腿，不碰地面。

| 文件 | 动作 | 这一帧画什么 |
|---|---|---|
| `kindred_wolf_float_1..4.png` | 漂浮循环（4 帧） | 狼头悬在空中，**整个狼只上下浮动 0–2 格**；身后的鬃毛毛尖像火焰一样一帧一帧往后飘、换形状（鬃毛总长度不变）；嘴微张 |
| `kindred_wolf_bite_1.png` | 扑咬 | 往后一缩蓄力：狼头往左缩 6 格，鬃毛挤在一起 |
| `kindred_wolf_bite_2.png` | | 往右猛扑：狼头往右冲出 15 格，鬃毛被拉长拖在后面 |
| `kindred_wolf_bite_3.png` | | 扑到最远：**嘴张到最大**，尖牙全露（这一刻咬中） |
| `kindred_wolf_bite_4.png` | | 嘴猛地合上，狼头还在最远处 |
| `kindred_wolf_bite_5.png` | | 退回到原位（和造型一样） |

## 提示词

### 羊：每帧一次

附图（工具一次最多 5 张时按这个顺序）：
1. `now/kindred_<动作>_<n>.png`（骨架）
2. `design/kindred_side_design.png`（侧身造型）
3. `design/kindred_side_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `design/kindred_front_design.png`（正面，看长相）

```text
Image 2 is the final pixel-art design of this character: a lamb-masked huntress seen SIDE-ON facing right - covered in white fur, a dark violet lamb mask with pointed ears, a pale crescent mark and two glowing teal eyes (a 3/4 head: both eyes visible), a fluffy white fur hood and long white shoulder fur streaming back behind her with lilac tips, a pale icy blue-white body, blue-violet goat legs bent backwards like a deer's ending in dark hooves, and a big BOW held upright in her front hand (dark violet limbs with glowing teal swirls, a pale teal hooked tip curling outward at each end, a thin pale string). It is drawn on a grid of 5x5-pixel squares, 142 x 166 squares, 34 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place. Image 5 is the same character from the front (her look only; the wolf in it is NOT drawn here).
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look and NOT its realistic proportions. (Image 4, when attached, is the previous frame of the same action: keep her exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 5-pixel grid as Image 3, every square one flat colour from Image 2's 34 colours; the character exactly as big as Image 2 (154 squares from the mask's ear tips to the hooves when standing) with Image 2's stocky proportions; she stays SIDE-ON facing image right like Image 2, never turned away, never upside down; her masked head - the mask, pointed ears, crescent, both teal eyes - copied square for square from Image 2, only moved, never redrawn as a profile; the bow copied square for square from Image 2 as ONE RIGID piece held upright in her front hand, only moved - never tilted, bent, stretched or scaled; when she draws it only the string bends into a "<" toward her face; NO arrow; NO wolf; the near leg in front in full tone, the far leg behind one shade darker, both legs the same thickness and length as in Image 2; the hooves on the red line of the guide (square row 196) unless this frame is in the air, nothing below it; the same near-black outline as Image 2 (about 2 squares); alpha only 0 or 255; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no arrow, no glow, no trail, no dust), no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run：`running to the right, frame <n> of an 8-frame loop: the goat legs crossing as in Image 1 (one forward, one back); the bow upright in her front hand as in Image 2, bobbing with the stride; the back arm swinging; the fur hood and the long white fur streaming behind`
- attack 1–5：`basic attack, shooting the bow, frame <n> of 5: <1: the front arm pushing the upright bow forward to the right, the back hand on the string | 2: drawing: the back hand pulls the string to her chest, the string bent into a "<", legs apart and firm | 3: full draw (the release moment): the string pulled to her cheek, the bow arm straight, leaning forward in a lunge | 4: just released: the string straight again, the back hand open behind her face | 5: back to the standing pose of Image 2>`
- skill 1–6：`Dance of Arrows, a leap and a volley, frame <n> of 6: <1: crouching to gather power, the bow close in front of her | 2: springing forward to the right, leaning forward, the back leg pushing off straight, the front leg tucked (no somersault) | 3: in the air flying right, curled up, both legs tucked under her, the bow upright against her front | 4: coming down, both legs reaching down to land | 5: landed in a shooting crouch at full draw toward the right (the volley's release) | 6: back to the standing pose>`
- skill2 1–5：`Mounting Dread, one aimed shot, frame <n> of 5: <1: the bow pushed forward, the back hand on the string | 2: legs spread wide, the body very low in a lunge, slowly drawing | 3: full draw, aiming (the release moment), still low | 4: just released: the string straight, the back hand open, still low | 5: standing up, back to the standing pose>`
- w_cast 1–4：`Wolf's Frenzy, calling the wolf, frame <n> of 4: <1: a small crouch, the bow in front of her | 2: a light hop on the spot, the bow raised upright above her head, the back hand open | 3: landing, the bow back in front of her | 4: back to the standing pose>`
- ult 1–6：`Lamb's Respite, a guarding blessing, frame <n> of 6: <1: starting to crouch, the bow in front of her | 2: down on one knee, the back hand pressed on the ground (hooves and hand on the red line), the bow upright in front | 3: the same, the head bowed (a still moment) | 4: rising, the bow starting to lift | 5: standing tall, the bow held upright HIGH above her head | 6: the bow back in front of her, back to the standing pose>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, staggering back, the bow still in her hand | 2: the goat legs giving way, sinking to her knees | 3: kneeling, the body slumping forward, the bow touching the ground | 4: falling sideways to the ground | 5: lying on her side on the ground (head toward the image right), the bow lying level beside her | 6: the same, still (the last frame)>`

### 狼：每帧一次

附图：
1. `design/kindred_wolf_design.png`（狼的侧面造型）
2. `design/kindred_wolf_design_on_canvas.png`（狼在画布上的大小和位置）
3. 同一个动作的前一帧（第 1 帧不附）
4. `refs/league_wolf_w_attack1.png`（扑咬时）或 `refs/league_wolf_idle_base_movement.png`（漂浮时）——英雄联盟里狼的动作，只看动作

```text
Image 1 is the final pixel-art design of a spirit wolf seen in PROFILE facing right: ONLY A WOLF HEAD, no body, no legs - a dark indigo-violet shaggy mane streaming back to the left and breaking into ragged smoky tufts like flames, a pointed ear, a white bone mask with a dark violet swirl over its brow, one glowing blue eye, open jaws with white fangs, a dark nose. It is drawn on a grid of 5x5-pixel squares, 82 x 48 squares. Image 2 shows it on a 1536x1024 canvas: that is its size and its resting place (the nose tip at square column 150, row 120). Image 4 (when attached) is the 3D wolf from the game in this motion - its motion only. (Image 3, when attached, is the previous frame: keep it exactly as big.)
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 5-pixel grid as Image 2, every square one flat colour from Image 1's colours; the wolf exactly as big as Image 1; its head - the bone mask, the swirl, the eye, the ear, the nose - copied square for square from Image 1, only moved; only the mane tufts and the lower jaw may change; floating, never touching the bottom of the canvas; the same near-black outline as Image 1 (about 2 squares); alpha only 0 or 255; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no glow, no trail, no smoke cloud), no huntress, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

- wolf_float 1–4：`floating in place, frame <n> of a 4-frame loop: the whole wolf <1: at its resting place | 2: 1 square higher | 3: 2 squares higher | 4: 1 square higher>; the mane tufts flickering backward like flames, a little different each frame (the mane keeps its length); the jaws slightly open`
- wolf_bite 1–5：`a lunging bite, frame <n> of 5: <1: drawing back: the head 6 squares to the left of its resting place, the mane bunched up | 2: lunging: the head 15 squares to the right of its resting place, the mane stretched long behind it | 3: at its farthest reach: the jaws open as WIDE as possible, all fangs showing (the bite) | 4: the jaws snapped shut, still at its farthest reach | 5: back at its resting place, as in Image 1>`

## 交回前请检查

- 49 帧都在，文件名对，每张 1536×1024 透明底、5 px 一格、alpha 只有 0 / 255，`_1x` 和大图逐格一致。
- 羊：每帧和造型一样大（站直耳尖到蹄底 154 格），一直侧身朝右、不倒立；头是造型的面具头（两只青绿眼都看得见）；弓是造型里那把、竖直、只平移，拉弓只弯弦；没有箭、没有狼。
- 狼：和造型一样大，狼头逐格照抄，只有鬃毛和下巴动；没有羊。
- 蹄底在红线上（跳起的空中帧除外），红线以下没有东西；没有特效、没有文字和格子线。
- 全部画完后最后写 `outputs/kindred-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张先在 8 倍下数描边台阶量实际格子，再读回，颜色贴回造型的 40 色调色板；面具头和弓按造型逐格贴回（一张脸贯穿所有帧，弓刚体只平移）；腿查变形和缝（rig-deformation-checks、gap-check），跑步不对就按 Caitlyn 的交叉步自己画；待机 = 正面造型（+ 呼吸，狼上下浮动）；受击 = 侧身造型平移 + 闪白。
- 狼放进羊的每一帧（在羊身后、胯部高度，漂浮循环；扑咬帧给 E 第 4 下和 W 用）；写 assets/source/ppu/kindred_<tag>.png/.json、1x 表、ppu_restyle 到泽丽密度（羊耳尖到蹄底 34 游戏行）、ppu_hd.py + lo_ 帧、hd.rs HEROES（league.dll ≥ 0.6.68，先问巴德 / 尼拉 / 加里奥 / 布隆 / 铁男 / 修正模型 / 塞恩当时最高号）；按动作条的出手帧重排技能数据的时机再跑一次模拟；逐帧自查后再给用户看 GIF。
