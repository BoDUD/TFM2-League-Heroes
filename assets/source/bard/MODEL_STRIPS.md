# 巴德（星界游神）：第 2 步，照英雄联盟的动作逐帧画细稿（给 Codex 的提示词）

> 造型已经定了：用户选了 **A**（乐器扛在近侧肩上），**所有动作都用 3/4 正面朝右**（和正面造型一样，**不画侧面、不转身**）。
> - **这一步只画细稿**：照你自己的正面细稿（`design/bard_front_draft.png`，约 8 像素一格的干净像素画）的画法画每一帧，**不要自己缩小、不要按粗格子整理**——上两步糊就是缩小造成的，这一次由我这边按格子读回再缩到游戏大小。
> - **大小和位置固定**：每帧都是 **1536×1024 透明画布**；巴德站直时和 `design/bard_front_on_canvas.png` 一样大、一样的位置（那张是你的正面细稿按这一步的大小放在画布上：**脚底在 y=980（红线）**，**两脚中间在 x=640（蓝十字）**，鬃毛顶约 y=420）。细稿的格子大约 **4–5 像素一格**（比正面细稿小一点，因为整个人缩小了），干净、整齐、一格一色。
> - **每帧一张图**：`now/bard_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小放在同一张画布上：**姿势、位置、身高照它**（跳起、倒下的高度也照它）。`guide/` 是同一张加了线：**红线 = 脚底线**，**蓝十字 = 站位点**，**洋红色轮廓 = 站直时造型的外轮廓**（大小参考），浅灰线每 50 像素一条——对位用，**不要画进图里**。
> - **长相、比例、颜色、细节全部照正面细稿**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**；巴德是敦实的 Q 版大个子（鬃毛团大、腿短）。
> - **头每帧都是同一个**：浅绿白的大鬃毛团 + 小小的**青铜面具**（两个金色眼孔 + 一个嘴孔）+ 天线金珠，**3/4 朝右前方，两个眼孔都看得见**；**不要重新画一张脸、不要画侧脸、不要背对镜头**（英雄联盟里他死亡时会转身背对，**我们不转身**，一直面朝右前方）。
> - **乐器每帧都是同一件**：象牙弯号角 + 棕色皮带 + 两三个小金铃 + 金色喇叭口 + 发光的青绿圆球；**大小、形状、颜色每帧一样**，可以整件移动、整件转动，**不能变形、不能变长变短**。手握着金色喇叭口那一端。
> - **一律 3/4 正面朝右**（和正面细稿一样）：近侧（画面左边）的腿颜色亮，远侧（画面右边）的腿暗一档、稍高；两条粗短的柱子腿，跑步时一前一后交叉迈步（两条腿都是直的，不要折成怪角度）。
> - **不画特效**（星光弹、米普小精灵、圣坛、传送门、金色时停穹顶都在第 3 步单独画），**不画地面和影子**；**红线以下什么都不能有**（倒下和落地的帧除外：照骨架）；出招一律朝画面右边。
> - 交付到 `outputs/bard-strips/`：每帧 `bard_<动作>_<n>.png`（1536×1024、真透明背景、细稿原样）；生图原稿放 `raw/`；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`bard_strips_done.zip`）。
> - 一个动作里的几帧，**画后一帧时附上前一帧**，让人、头、乐器一样大。

## 要画的帧（38 帧，全部 3/4 正面朝右）

| 文件 | 动作 | 这一帧画什么（身体照骨架；乐器和手按这里） |
|---|---|---|
| `bard_run_1..8.png` | 跑步（8 帧循环） | 朝右跑，身体微微前倾；两条柱子腿照骨架一前一后交叉、两腿都直；**乐器还扛在近侧肩上**（和造型一样），随步子上下颠；远侧的手臂前后摆；鬃毛随步子轻轻弹 |
| `bard_attack_1.png` | 普攻：甩出星光 | 准备：近侧的手把乐器从肩上拿下来，喇叭口垂在身前低处 |
| `bard_attack_2.png` | | 乐器从低处往右前方甩，手臂往前伸 |
| `bard_attack_3.png` | | 出手：手臂朝右前上方伸直，喇叭口朝右上方（这一刻星光从喇叭口飞出去，星光是特效，不画） |
| `bard_attack_4.png` | | 甩到最高：乐器举在右上方 |
| `bard_attack_5.png` | | 回到造型的站姿，乐器扛回近侧肩上 |
| `bard_skill_1.png` | Q 星界束缚 | 乐器从肩上举起到头旁边 |
| `bard_skill_2.png` | | 往后蓄力，身体略压低 |
| `bard_skill_3.png` | | 把喇叭口朝右前方推出去 |
| `bard_skill_4.png` | | 出手：手臂朝右伸直，喇叭口对准右边（星界能量是特效，不画） |
| `bard_skill_5.png` | | 回到站姿 |
| `bard_skill2_1.png` | W 游神圣坛 | 远侧（画面右边）的手开始抬起，乐器还在近侧肩上 |
| `bard_skill2_2.png` | | 远侧的手举过肩，手掌张开 |
| `bard_skill2_3.png` | | 远侧的手高举过头，五指张开（召唤圣坛；圣坛是特效，不画） |
| `bard_skill2_4.png` | | 手往下放 |
| `bard_skill2_5.png` | | 回到站姿 |
| `bard_skill2_e_1.png` | E 神奇旅程（开门） | 乐器从肩上拿到身前 |
| `bard_skill2_e_2.png` | | 乐器举在身前右边、胸口高度，喇叭口朝右（打开传送门；门是特效，不画） |
| `bard_skill2_e_3.png` | | 同上，身体略往前倾 |
| `bard_skill2_e_4.png` | | 回到站姿 |
| `bard_ult_1.png` | R 调和命运 | 蓄力：乐器拿到身前，身体略压低 |
| `bard_ult_2.png` | | 把乐器高举过头（像在吹奏），喇叭口朝上 |
| `bard_ult_3.png` | | 乐器举得最高，身体舒展 |
| `bard_ult_4.png` | | 把乐器朝右前方挥下去（金色法球飞出去；法球是特效，不画） |
| `bard_ult_5.png` | | 回到站姿 |
| `bard_dead_1.png` | 死亡 | 被打中，往后踉跄，乐器还在手里 |
| `bard_dead_2.png` | | 两臂张开，乐器脱手往下掉 |
| `bard_dead_3.png` | | 腿一软跪坐下去（面朝右前方，不转身） |
| `bard_dead_4.png` | | 往前倒 |
| `bard_dead_5.png` | | 趴在地上，乐器横躺在他身边（画面右边） |
| `bard_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/bard_<动作>_<n>.png`（骨架）
2. `design/bard_front_draft.png`（你的正面细稿：长相、画法）
3. `design/bard_front_on_canvas.png`（同一张细稿在这一步的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `guide/bard_<动作>_<n>.png`（加了线的骨架：脚底线、站位点、站直时的轮廓）

```text
Image 2 is your own detailed pixel-art drawing of this character: Bard, a big gentle wanderer in 3/4 FRONT view facing image right - a big fluffy pale green-white mane round a small round bronze mask with two glowing golden eye holes and one golden mouth hole, a short antenna with a golden bead, sage-green skin, big olive-brown hands, red-and-dark-purple striped bracers, a long red tabard with orange swirls, a brown belt, a dark blue-grey waist cloth with purple tassels, a golden bell at the hip, loose dark wine-red trousers, two thick dark iron peg feet, and his instrument (a long curved ivory horn with brown leather bands and two or three small golden bells under it, a golden bell-mouth holding a glowing teal orb) carried on his near shoulder. Image 3 is that drawing placed on this frame's 1536x1024 canvas at the size and place he must have when standing (soles on y 980, the point between the feet on x 640).
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look and NOT its realistic proportions. Image 5 is the same with guide lines (red: the soles' line, blue cross: the standing point, magenta: the standing figure's outline). (Image 4, when attached, is the previous frame of the same action: keep him exactly as big.)
Draw ONE frame: <WHAT>
Rules: a 1536x1024 PNG with a genuine transparent background; crisp clean pixel art drawn like Image 2 (even squares of about 4-5 output pixels at this size, every square one flat colour, a one-square near-black outline, 3-4 flat shades per material, no dithering, no gradients, no soft glow, no anti-aliasing); the character as big as Image 3 with Image 2's stocky proportions and big mane; he stays in 3/4 FRONT view facing image right like Image 2, never turned away, never in profile; his head - the mane, the bronze mask with both eye holes and the mouth hole, the antenna - the same as Image 2 in every frame, only moved; the instrument the same piece as in Image 2 (same size, shape and colours), only moved or turned as a whole, the hand on the golden bell-mouth end; the near leg (image left) in full tone, the far leg (image right) a shade darker; the soles on the red line unless this frame is in the air or lying down, nothing below it; no effects (no star bolt, no little spirits, no shrine, no portal, no golden dome, no glow, no dust), no ground, no shadow, no text, no guide lines. Do NOT reduce it or re-grid it to bigger squares: deliver the detailed drawing as drawn.
```

`<WHAT>` 按上表换成英文，例如：

- run：`running to the right, frame <n> of an 8-frame loop: the body leaning a little forward, the two short peg legs crossing as in Image 1 (one forward, one back), both legs straight; the instrument still carried on his near shoulder as in Image 2, bobbing with the stride; the far arm swinging; the mane bouncing a little`
- attack 1–5：`basic attack, flinging a star, frame <n> of 5: <1: the near hand takes the instrument down from the shoulder, the bell-mouth low in front of him | 2: swinging the instrument forward to the right, the arm reaching out | 3: the release: the arm stretched forward and up to the right, the bell-mouth pointing up-right | 4: the follow-through: the instrument high on the right | 5: back to the standing pose of Image 2, the instrument on his shoulder again>`
- skill 1–5：`Cosmic Binding, frame <n> of 5: <1: lifting the instrument from the shoulder up beside his head | 2: drawing it back, body a little lower | 3: pushing the bell-mouth forward to the right | 4: the release: the arm straight out to the right, the bell-mouth aimed right | 5: back to the standing pose>`
- skill2 1–5：`Caretaker's Shrine, frame <n> of 5: <1: the far arm (image right) starting to rise, the instrument still on the near shoulder | 2: the far hand above the shoulder, palm open | 3: the far hand raised high above his head, fingers spread (summoning) | 4: the hand coming down | 5: back to the standing pose>`
- skill2_e 1–4：`Magical Journey, opening a door, frame <n> of 4: <1: taking the instrument from the shoulder to the front of his body | 2: holding the instrument out in front of him to the right at chest height, the bell-mouth pointing right | 3: the same, leaning a little forward | 4: back to the standing pose>`
- ult 1–5：`Tempered Fate, frame <n> of 5: <1: gathering: the instrument in front of him, body a little lower | 2: raising the instrument above his head as if playing it, the bell-mouth up | 3: the instrument at its highest, body stretched | 4: swinging the instrument down forward to the right (the orb flies off - not drawn) | 5: back to the standing pose>`
- dead 1–6：`dying, frame <n> of 6, always facing the front right (never turned away): <1: hit, staggering back, the instrument still in his hand | 2: arms thrown open, the instrument slipping from his hand | 3: the legs giving way, sinking down | 4: falling forward | 5: lying face down on the ground, the instrument lying beside him on the image right | 6: the same, still (the last frame)>`

## 交回前请检查

- 38 帧都在，文件名对，每张 1536×1024 透明底，是细稿原样（没有缩小、没有按粗格子整理）。
- 每帧和 `design/bard_front_on_canvas.png` 一样大，敦实、鬃毛团大；一直 3/4 正面朝右，不转身、不侧脸；头和面具每帧一样（两个眼孔都看得见）。
- 乐器每帧是同一件（大小、形状、颜色一样），手握着喇叭口那一端。
- 脚底在红线上（倒下的帧照骨架），红线以下没有东西；没有特效、地面、影子、文字和辅助线。
- 全部画完后最后写 `outputs/bard-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每帧用 `tools/art/design_bard_hd.py` 同样的流程缩到游戏大小：前面造型的 32 色调色板 → 按 11 px 一格（这一步的比例）多数投票，脚底对齐红线 → 贴正面造型的面具（同一张脸，只平移）→ 乐器喇叭口按需要贴正面的金环 → 补缝 → 外描边加 1 格 → 两遍平整；待机 = 正面造型（+ 呼吸）；受击 = 正面造型平移 + 闪白。
- 6 倍 / 游戏尺寸逐帧自查（rig-deformation-checks、gap-check：面具不能被手臂挡住、没有缺描边的洞）再给用户看 GIF；跑步不对就按 Caitlyn 的交叉步自己画腿。
- 写 assets/source/ppu/bard_<tag>.png / .json、ppu_hd.py PPU 1.5 + lo_ 帧、hd.rs HEROES（league.dll ≥ 0.6.66，先问尼拉 / 加里奥当时最高号）；按动作条的出手帧重排技能数据的时机再跑一次模拟。
