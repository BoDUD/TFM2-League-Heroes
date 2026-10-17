# 塔姆·肯奇（河流之王）：第 2 步，照英雄联盟的动作逐帧画动作条（给 Codex 的提示词）

> 造型已经定了（用户 2026-10-16：「选A」）：`design/tahmkench_design.png`。它就是你第 0 步画的 A 版原画逐格读回：**151 × 125 格**，40 色，3/4 正面朝右，咧嘴得意地笑。这里每格 **6 × 6 px**，画布 1536×1024 正好 256 × 170 格。造型本身就是待机，**待机和受击不用画**；其余动作照英雄联盟里塔姆的动作画。
> - **每帧一张图**：`now/tahmkench_<动作>_<n>.png` 是**骨架**，就是英雄联盟里这一帧的 3D 模型，已经按造型的大小放在同一个格子里了：**姿势、位置、身高照它**。W 的两段（`skill2_*`、`w_land_*`）的骨架是造型本身平移或转 90° 摆出来的，因为原版的下潜是转向镜头、垂直跳出画面。
> - `guide/` 是同一张加了辅助线：**红线 = 脚底线**（第 160 行的下边），**蓝线 = 造型站直时的帽顶**，**蓝十字 = 站位点**（第 100 列），浅灰线每 10 格一条。这些线只用来对位，**不要画进图里**。`design/tahmkench_design_on_canvas.png` 是造型站在这个画布上的样子（同一个站位点）。
> - **长相、比例、颜色、细节全部照造型**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势。**和造型一样大**：站直时帽顶到脚底 125 格、宽 151 格（连尾巴），不要画大也不要画小。头和身体是一整团，大嘴占上半身，两条很短的粗腿，**不要画成 Q 版大头**。
> - **闭着嘴（咧嘴笑）的帧**：小礼帽、黄绿色眼睛、鲶鱼须和金环、两排牙，都逐格照抄造型，只平移，不要重新画一张脸。
> - **张大嘴的帧**（普攻、Q、W 冒出、R）：嘴怎么张开照 `refs/tahmkench-B.png`（第 0 步的 B 版）：粉红舌头、深紫红口腔、上下两排米白尖牙；**颜色只用造型的 40 色**，眼睛、帽子、鱼须照造型。
> - **一律 3/4 正面朝右**，和造型一样，身体不要转成侧面或背面。近侧的手脚在画面左边、颜色亮；远侧的在画面右边、暗一档。
> - **跑步要交叉步**：两条短腿每半圈交换前后，第 3、7 帧左右两只脚在身体下面交错；脚不能在地上滑；尾巴和燕尾服下摆跟着轻轻摆。
> - 每格 6 × 6 px 一个纯色方块，所有格子对齐同一个网格（就是 `design/tahmkench_design_on_canvas.png` 的格子）；**只用造型的 40 色**（`design/tahmkench_palette.png`）；一圈近黑描边，和造型一样粗；不要抖动、渐变、噪点、抗锯齿、半透明。
> - **不画特效**（长舌头鞭子、水花、气泡、吞人的光、护盾），只画塔姆。普攻的舌头是身体的一部分，可以从嘴里伸出来；**Q 的长舌鞭第 3 步当特效画**，这一步只画舌根伸出嘴外一小截。**红线以下什么都不能有**（W 潜进地里的帧，红线以下的部分不画，身体在红线处平平地截断）。出招一律朝画面右边。
> - 交付到 `outputs/tahmkench-strips/`：每帧一张 `tahmkench_<动作>_<n>.png`（1536×1024、透明背景、和骨架同一个格子），再配一张 `tahmkench_<动作>_<n>_1x.png`（1 像素 1 格，必须和大图逐格一致）。生图原稿放 `raw/`，不要重采样。**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到），最好打成一个 zip（`tahmkench_strips_done.zip`）。
> - 生图后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩放**。一个动作里的几帧，**画后一帧时附上前一帧**，保证身体、头、帽子一样大。
> - 请把附件 `tahmkench_strips_pack.zip` 解压到一个**新的文件夹**，只用这里面的图。

## 要画的帧（37 帧）

| 文件 | 动作 | 这一帧画什么（身体照骨架） |
|---|---|---|
| `tahmkench_run_1..8.png` | 跑步（8 帧循环） | 朝右摇摇摆摆地小跑，两条短腿照骨架一前一后**交叉迈步**，大身子随步子上下颠，尾巴和燕尾服下摆左右轻摆，两只手一前一后摆，咧嘴笑 |
| `tahmkench_attack_1.png` | 普攻：舌头抽打 | 身子后仰，嘴张开 |
| `tahmkench_attack_2.png` | | 嘴张大，舌头从嘴里卷起来 |
| `tahmkench_attack_3.png` | | 出手：身子前扑，舌头从嘴里向画面右边甩出、抽下去（命中） |
| `tahmkench_attack_4.png` | | 舌头收回嘴里，身子回正 |
| `tahmkench_attack_5.png` | | 回到造型的站姿 |
| `tahmkench_skill_1.png` | Q 巨舌鞭笞 | 压低身子蓄力，嘴闭着 |
| `tahmkench_skill_2.png` | | 身子往后仰，嘴开始张开 |
| `tahmkench_skill_3.png` | | 身子往前探，嘴张大朝向画面右边 |
| `tahmkench_skill_4.png` | | 出手：嘴张到最大朝右，舌根伸出嘴外一小截（长舌鞭第 3 步再画） |
| `tahmkench_skill_5.png` | | 回到造型的站姿 |
| `tahmkench_skill2_1.png` | W 深渊潜航：下潜 | 屈腿下蹲，身子压扁一点，准备跳 |
| `tahmkench_skill2_2.png` | | 向右前方小跳起来，离地几格 |
| `tahmkench_skill2_3.png` | | 头朝下扎进地里（照骨架转 90°）：前半身已经在地下，红线以上只剩后半身、燕尾和尾巴，在红线处平平截断 |
| `tahmkench_skill2_4.png` | | 几乎全进去了：红线以上只剩尾鳍和两只脚尖 |
| `tahmkench_w_land_1.png` | W 深渊潜航：冒出 | 嘴朝上从地里冲出来（照骨架转 90°），嘴张到最大，下半身还在地下，在红线处平平截断 |
| `tahmkench_w_land_2.png` | | 整个跳出地面，在空中（脚离红线约 16 格），两手张开，嘴张开 |
| `tahmkench_w_land_3.png` | | 落地：身子压扁、变宽，脚踩在红线上 |
| `tahmkench_w_land_4.png` | | 回到造型的站姿 |
| `tahmkench_ult_1.png` | R 大快朵颐（吞人） | 身子后仰，嘴开始张开 |
| `tahmkench_ult_2.png` | | 嘴张到极大、朝右上方，像要把人整个吞下去，两手张开 |
| `tahmkench_ult_3.png` | | 一口咬合：嘴猛地合上（嘴里不画人），脸颊鼓起来 |
| `tahmkench_ult_4.png` | | 肚子鼓得圆滚滚，两只手拍着肚子，得意地咧嘴笑 |
| `tahmkench_ult_5.png` | | 回到造型的站姿 |
| `tahmkench_dead_1.png` | 死亡 | 被打中，身子一缩往后仰 |
| `tahmkench_dead_2.png` | | 往后踉跄，小礼帽从头上飞起来 |
| `tahmkench_dead_3.png` | | 身子往前一软，开始倒下 |
| `tahmkench_dead_4.png` | | 下巴着地，整个人往前趴倒 |
| `tahmkench_dead_5.png` | | 趴在地上，舌头从嘴里耷拉出来，帽子掉在身旁的地上 |
| `tahmkench_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧画一次。附图按下面的顺序（工具一次最多附 5 张时也按这个顺序）：
1. `now/tahmkench_<动作>_<n>.png`（骨架）
2. `design/tahmkench_design.png`（造型）
3. `design/tahmkench_design_on_canvas.png`（造型在画布上的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `refs/tahmkench-B.png`（张大嘴的帧附它）或 `refs/tahmkench-A.png`（其余的帧）

```text
Image 2 is the final pixel-art design of this character: Tahm Kench, a huge greedy river demon like a giant catfish-toad, in 3/4 front view facing right - his head and body ONE big round mass, a tiny black top hat with a dark red band and a gold curl ornament, pale cream-green skin with darker green stripes over the top and back, one glowing yellow-green eye, an enormous grinning mouth with two rows of cream-white triangular teeth, two long pinkish catfish whiskers with gold rings, a brown leather cape over the shoulders, a wine-red striped waistcoat with gold clasps, dark navy tailcoat tails, a brown leather bracer with a green gem on the near forearm, green clawed hands, a short fish tail with dark red fins, two very short thick legs. It is drawn on a grid of 6x6-pixel squares, 151 x 125 squares, 40 colours. Image 3 shows the design standing on a 1536x1024 canvas: that is the size and the place.
Image 1 is the pose guide for THIS FRAME, already scaled and placed on the same canvas (a 3D render of the same character from the game, or for the dive frames the design itself moved or turned): copy its pose, its place and its size - NOT its 3D look, NOT its proportions (keep the design's build). (Image 4, when attached, is the previous frame of the same action: keep him exactly as big.) Image 5 is the step-0 picture: for an open mouth, copy how image 5's mouth opens (pink tongue, dark magenta inside, both rows of fangs) in Image 2's colours.
Draw ONE frame: <WHAT>
Rules: the same 1536x1024 transparent canvas and the SAME 6-pixel grid as Image 3, every square one flat colour from Image 2's 40 colours; the character exactly as big as Image 2 (125 squares from the top of the hat to the soles when standing, 151 wide with the tail); he stays in the 3/4 FRONT view of Image 2 (facing the image right, the face toward the viewer), never turned side-on or away; NOT chibi - the design's own proportions; with the mouth closed or grinning his face - hat, eye, whiskers, teeth - is copied square for square from Image 2, only moved; the near arm and leg on the image left in full tone, the far ones on the image right one shade darker; the soles on the red line of the guide (square row 160) unless this frame is in the air; NOTHING below the red line (where he is under the ground the body is cut flat at the red line); a near-black outline as thick as Image 2's; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects (no long tongue whip, no water, no splash, no bubbles, no glow, no shield), no other characters, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 按上表换成英文：

- run：`a waddling run to the right, frame <n> of an 8-frame loop: the two short legs CROSSING as in Image 1 (one forward, one back, swapping every half cycle - on frames 3 and 7 the feet pass each other under the body; no foot slides on the ground), the big body bobbing with the steps, the tail and the coat tails swaying, the hands swinging, grinning`
- attack 1–5：`basic attack, a tongue slap, frame <n> of 5: <1: leaning back, the mouth opening | 2: the mouth wide, the tongue curling up out of it | 3: the hit: lunging forward, the tongue lashing out of the mouth to the image right and down in a slap | 4: the tongue back in the mouth, straightening up | 5: back to the standing pose of Image 2>`
- skill 1–5：`Tongue Lash, frame <n> of 5: <1: crouching low to gather, mouth closed | 2: rearing back, the mouth starting to open | 3: lurching forward, the mouth wide open toward the image right | 4: the release: the mouth open as wide as it goes facing right, only the root of the tongue sticking out a little (the long tongue is drawn later as an effect - not here) | 5: back to the standing pose of Image 2>`
- skill2 1–4：`Abyssal Dive, going under, frame <n> of 4: <1: squatting down to jump, the body squashed a little | 2: a small hop up and forward to the right, the feet a few squares off the ground | 3: diving head-first into the ground as in Image 1 (turned a quarter): the front half already under the ground, above the red line only the back half, the coat tails and the tail, cut flat at the red line | 4: almost gone: above the red line only the tail fin and the tips of the two feet>`
- w_land 1–4：`Abyssal Dive, bursting up, frame <n> of 4: <1: shooting up out of the ground mouth-first as in Image 1 (turned a quarter), the mouth open as wide as it goes pointing up, the lower body still under the ground, cut flat at the red line | 2: all the way out, in the air with the feet about 16 squares above the red line, the arms spread, the mouth open | 3: landing: squashed wide and low, the feet on the red line | 4: back to the standing pose of Image 2>`
- ult 1–5：`Devour, swallowing someone whole, frame <n> of 5: <1: leaning back, the mouth starting to open | 2: the mouth opened enormously toward the upper right as if to swallow a whole person, both arms spread | 3: the gulp: the mouth snapping shut (nobody drawn inside), the cheeks bulging | 4: the belly round and full, both hands patting it, a smug grin | 5: back to the standing pose of Image 2>`
- dead 1–6：`dying, frame <n> of 6: <1: hit, flinching back | 2: staggering back, the little top hat flying up off his head | 3: slumping forward, starting to fall | 4: chin on the ground, toppling forward flat | 5: lying flat on his belly, the tongue lolling out of the mouth, the hat on the ground beside him | 6: the same, still (the last frame)>`

## 交回前请检查

- 37 帧都在，文件名对，每张 1536×1024 透明底、6 px 一格，`_1x` 和大图逐格一致。
- 每帧和造型一样大（站直帽顶到脚底 125 格），一直是 3/4 正面朝右，不是 Q 版；闭嘴的帧脸、帽子、眼睛、鱼须照抄造型；张嘴的帧照 B 版的张嘴方式、用造型的颜色。
- 跑步两腿交叉、换前后，脚不滑；脚底在红线上（跳起、空中的帧除外），红线以下没有东西；潜进地里 / 从地里冒出的帧在红线处平平截断。
- 没有特效（Q 的长舌鞭不画）、没有文字和格子线。
- 全部画完后最后写 `outputs/tahmkench-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按 6 px 格读回（regrid --size 6），颜色贴回造型的 40 色；闭嘴帧的脸按造型逐格贴回（一张脸贯穿所有帧）；张嘴帧对照 B 版查嘴和牙；查每帧和造型的大小（帽顶到脚底 125 格），按头对齐。
- 跑步逐帧量脚的 x，两脚必须每半圈换前后（伊莉丝的教训）；不变形、不剪切。
- 写 assets/source/ppu/tahmkench_<tag>.png、1x 表；ppu_restyle 降到 PPU 1.8，ppu_hd 出 hd_ / lo_，hd.rs HEROES 登记（league_main 0.7.11，和卡莉斯塔会话协调）；按帧重定出手时间、重跑平衡；逐帧自查后再给用户看 GIF。
