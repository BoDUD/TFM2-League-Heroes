# 玛尔扎哈（虚空先知）：第 2 步，照英雄联盟的动作逐帧画细稿（给 Codex 的提示词）

> 造型已经定了：用户选了 **B**（露出蓬松蓝裤子、深灰护胫、尖头洋红靴，**脚尖朝下悬浮**），就是你上一轮的原稿 `design/malzahar_B_draft.png`。**所有动作都用 3/4 正面朝右**（和造型一样，**不画侧面、不转身**）。
> - **这一步只画细稿**：照 `design/malzahar_B_draft.png`（约 8 像素一格的干净像素画）的画法画每一帧，**不要自己缩小、不要按粗格子整理、不要用程序重画**——前两轮糊、走样都是缩小和程序整理造成的，这一次由我这边按格子读回再缩到游戏大小。
> - **大小和位置固定**：每帧都是 **1536×1024 透明画布**；他悬浮不动时和 `design/malzahar_on_canvas.png` 一样大、一样的位置（那张是你的原稿按这一步的大小放在画布上：**最低点（靴尖）在 y=960（红线）**，**身体中间在 x=700（蓝十字）**，兜帽尖约 y=190）。细稿的格子大约 **5 像素一格**（比原稿小一点，因为整个人缩小了），干净、整齐、一格一色。
> - **每帧一张图**：`now/malzahar_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小放在同一张画布上：**姿势、位置、身高照它**（升起、落下的高度也照它）。`guide/` 是同一张加了线：**红线 = 最低点的线**，**蓝十字 = 站位点**，**洋红色轮廓 = 悬浮不动时造型的外轮廓**（大小参考），浅灰线每 50 像素一条——对位用，**不要画进图里**。`refs/` 是骨架在游戏大小下的样子，只作参考。
> - **长相、比例、颜色、细节全部照原稿**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**；玛尔扎哈是偏 Q 版的清瘦法师（兜帽头大、身子短）。
> - **头每帧都是同一个**：洋红尖顶兜帽（帽尖往后弯）+ 额头**四颗发光的浅蓝白菱形**（上 1、中 2、下 1）+ 洋红面巾 + **两只发白光的眼睛**，**3/4 朝右前方，两只眼睛、四颗菱形都看得见**；**不要重新画一张脸、不要画侧脸、不要背对镜头**（英雄联盟里他死亡时会蜷起来，**我们不转身**，脸一直朝右前方）。
> - **他永远悬浮、不走路**：两条腿一直是**脚尖朝下垂着**（像原稿），跟着身体整体动，**不迈步、不踩地**；移动时身体前倾滑行，腿往后飘。
> - **匕首每帧都是同一把**：横插在腰带上（灰蓝刀鞘 + 金色花纹 + 金色护手），**不拔出来**，跟着身体整体动，不变形。
> - **一律 3/4 正面朝右**（和原稿一样）：近侧（画面左边）的手臂和腿颜色亮，远侧（画面右边）的暗一档。
> - **不画特效**（虚空弹、虚空裂隙、虚空虫、紫色能量、手上的光、地上的虚空区域都在第 3 步单独画），**不画地面和影子**；**红线以下什么都不能有**（倒地的帧除外）；出招一律朝画面右边。
> - 交付到 `outputs/malzahar-strips/`：每帧 `malzahar_<动作>_<n>.png`（1536×1024、真透明背景、细稿原样）；生图原稿放 `raw/`；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`malzahar_strips_done.zip`）。
> - 一个动作里的几帧，**画后一帧时附上前一帧**，让人、头、匕首一样大。

## 要画的帧（35 帧，全部 3/4 正面朝右）

| 文件 | 动作 | 这一帧画什么（身体照骨架；手和衣服按这里） |
|---|---|---|
| `malzahar_run_1..6.png` | 移动（6 帧循环，滑行） | 朝右悬浮滑行，身体微微前倾；**两条腿脚尖朝下、往后飘**（不迈步）；两臂略往后放松；围巾、布尾、袍角往后飘，每帧飘的样子略不同；整个人随帧轻轻上下浮 |
| `malzahar_attack_1.png` | 普攻：甩出虚空弹 | 准备：远侧（画面右边）的手收到肩旁，手掌张开 |
| `malzahar_attack_2.png` | | 手往右前方甩出去 |
| `malzahar_attack_3.png` | | 出手：手臂朝右伸直，五指张开（这一刻虚空弹从手心飞出去，弹是特效，不画） |
| `malzahar_attack_4.png` | | 收手，手臂往回 |
| `malzahar_attack_5.png` | | 回到造型的悬浮姿势 |
| `malzahar_skill_1.png` | E 煞星幻象 | 远侧的手抬到胸前，手指弯成爪 |
| `malzahar_skill_2.png` | | 爪手往右前方推 |
| `malzahar_skill_3.png` | | 出手：手臂朝右伸直，五指张开对准右边（幻象飞出去；特效不画） |
| `malzahar_skill_4.png` | | 保持，身体略前倾 |
| `malzahar_skill_5.png` | | 回到悬浮姿势 |
| `malzahar_skill2_1.png` | Q 虚空召唤 | 两臂往身体两侧抬起，掌心朝上 |
| `malzahar_skill2_2.png` | | 两手抬到肩高、往两边张开（打开两道裂隙；裂隙是特效，不画） |
| `malzahar_skill2_3.png` | | 两手猛地往身前合拢（裂隙合上） |
| `malzahar_skill2_4.png` | | 保持合拢，身体略前倾 |
| `malzahar_skill2_5.png` | | 回到悬浮姿势 |
| `malzahar_ult_1.png` | R 冥府之握（起手） | 身体略升起，两手往后收、蓄力 |
| `malzahar_ult_2.png` | | 两手往右前方猛推出去，五指张开 |
| `malzahar_ult_3.png` | | 身体前倾，两臂朝右伸直，手指弯成爪，像抓住了什么 |
| `malzahar_ult_4.png` | | 同上，抓紧（下面接引导循环） |
| `malzahar_ult_loop_1..4.png` | R 引导（4 帧循环） | 骨架里的引导姿势：身体前倾，两臂朝右伸出，爪手抓着（被压制的敌人在右边，不画）；四帧只差一点点：手微微颤、围巾和布尾飘动、整个人轻轻上下浮 |
| `malzahar_dead_1.png` | 死亡 | 被打中，往后一仰，两臂甩开 |
| `malzahar_dead_2.png` | | 蜷起身体，膝盖收起 |
| `malzahar_dead_3.png` | | 在半空蜷成一团 |
| `malzahar_dead_4.png` | | 开始往下掉 |
| `malzahar_dead_5.png` | | （**没有骨架，照文字**）摔落在地上，侧躺着蜷成一团，兜帽在画面右边、脸朝右前方，靴子在画面左边；身体最低处在红线上 |
| `malzahar_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/malzahar_<动作>_<n>.png`（骨架；dead_5、dead_6 没有骨架，附 `guide/` 那张）
2. `design/malzahar_B_draft.png`（你的原稿：长相、画法）
3. `design/malzahar_on_canvas.png`（同一张原稿在这一步的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `guide/malzahar_<动作>_<n>.png`（加了线的骨架：最低点的线、站位点、悬浮不动时的轮廓）

```text
Image 2 is your own detailed pixel-art drawing of this character: Malzahar, a lean void prophet who FLOATS in the air, in 3/4 FRONT view facing image right - a tall pointed magenta hood with its tip bending back, four glowing pale blue-white diamond marks on its front (one on top, two in the middle, one below), the face in shadow behind a magenta face cloth with two glowing white eyes, a big thick magenta scarf, an open royal-blue robe over a bare greyish-tan chest, a magenta inner tunic, a dark belt with a curved dagger thrust through it (blue-grey sheath with golden scrolls, golden hilt guard), big flared lilac-grey metal bracers, big dark navy gloved hands, a long magenta cloth tail, puffy royal-blue trousers, dark grey shin guards and pointed dark magenta boots hanging toes down. Image 3 is that drawing placed on this frame's 1536x1024 canvas at the size and place he must have when floating still (his lowest point, the boot tips, on y 960; his middle on x 700).
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look and NOT its realistic proportions. Image 5 is the same with guide lines (red: the line of his lowest point, blue cross: the standing point, magenta: the floating figure's outline). (Image 4, when attached, is the previous frame of the same action: keep him exactly as big.)
Draw ONE frame: <WHAT>
Rules: a 1536x1024 PNG with a genuine transparent background (hard alpha, no haze); crisp clean pixel art drawn like Image 2 (even squares of about 5 output pixels at this size, every square one flat colour, a one-square near-black outline, 3-4 flat shades per material, no dithering, no gradients, no soft glow, no anti-aliasing); the character as big as Image 3 with Image 2's proportions and big hood; he stays in 3/4 FRONT view facing image right like Image 2, never turned away, never in profile; his head - the hood, the four diamond marks, the face cloth, both glowing eyes - the same as Image 2 in every frame, only moved; he floats and never walks: both legs hang with the toes pointing down and move with the body as a whole; the dagger stays sheathed in the belt, the same piece as in Image 2, only moved with the body; the near arm and leg (image left) in full tone, the far ones (image right) a shade darker; nothing below the red line unless this frame lies on the ground; no effects (no void bolt, no rifts, no creatures, no purple energy, no glow on the hands, no dust), no ground, no shadow, no text, no guide lines. Do NOT reduce it, re-grid it to bigger squares or repaint it with a program: deliver the detailed drawing as drawn.
```

`<WHAT>` 按上表换成英文：

- run 1–6：`gliding to the right, frame <n> of a 6-frame loop: floating, the body leaning a little forward, both legs trailing back with the toes pointing down (never stepping), the arms relaxed a little back, the scarf, the cloth tail and the robe's hem streaming back (a little different in every frame), the whole figure bobbing slightly up or down as in Image 1`
- attack 1–5：`basic attack, flinging a void bolt, frame <n> of 5: <1: the wind-up: the far hand (image right) drawn back beside the shoulder, palm open | 2: the hand thrown forward to the right | 3: the release: the arm straight out to the right, fingers spread | 4: the hand coming back | 5: back to the floating pose of Image 2>`
- skill 1–5：`Malefic Visions, frame <n> of 5: <1: the far hand raised to the chest, fingers curled like a claw | 2: pushing the clawed hand forward to the right | 3: the release: the arm straight out to the right, fingers spread toward the right | 4: holding it, the body leaning a little forward | 5: back to the floating pose>`
- skill2 1–5：`Call of the Void, frame <n> of 5: <1: both arms rising out to the sides, palms up | 2: both hands at shoulder height, spread wide apart (opening two rifts - not drawn) | 3: both hands swept together in front of him (closing the rifts) | 4: holding them together, leaning a little forward | 5: back to the floating pose>`
- ult 1–4：`Nether Grasp, the start, frame <n> of 4: <1: rising a little, both hands drawn back, gathering | 2: both hands thrust forward to the right, fingers spread | 3: leaning forward, both arms straight out to the right, the fingers curled like claws as if gripping something | 4: the same, gripping hard>`
- ult_loop 1–4：`Nether Grasp, the channel, frame <n> of a 4-frame loop: as in Image 1 - leaning forward, both arms reaching out to the right, the clawed hands gripping (the held enemy on the right is not drawn); the four frames differ only a little: the hands trembling, the scarf and the cloth tail fluttering, the figure bobbing slightly`
- dead 1–6：`dying, frame <n> of 6, the face always toward the front right (never turned away): <1: hit, thrown back, the arms flung open | 2: curling up, the knees drawn in | 3: curled into a ball in the air | 4: starting to drop | 5: fallen on the ground, lying on his side curled up, the hood on the image right with the face toward the front right, the boots on the image left, his lowest point on the red line | 6: the same, still (the last frame)>`

## 交回前请检查

- 35 帧都在，文件名对，每张 1536×1024 透明底（全硬 alpha），是细稿原样（没有缩小、没有按粗格子整理、没有程序重画）。
- 每帧和 `design/malzahar_on_canvas.png` 一样大；一直 3/4 正面朝右，不转身、不侧脸；兜帽、四颗菱形、两只白眼每帧一样、都看得见。
- 两条腿一直脚尖朝下垂着，不迈步、不踩地；匕首一直插在腰带上，是同一把。
- 最低点在红线上或红线以上（倒地的帧除外），红线以下没有东西；没有特效、地面、影子、文字和辅助线。
- 全部画完后最后写 `outputs/malzahar-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 先看 raw/；每帧用 `tools/art/design_malzahar.py` 同样的流程缩到游戏大小（regrid → 造型的调色板 → pixelate 到 PPU 2.2：这一步 10 px 一格 → 菱形 / 眼睛 / 金色亮者胜）→ 贴造型的脸（同一张脸，只平移：兜帽前额、四颗菱形、眼睛）→ 补缝 → 描边。
- 待机 = 造型（+ 上下浮动）；受击 = 造型平移 + 闪白。
- 6 倍 / 游戏尺寸逐帧自查（rig-deformation-checks、gap-check：脸不能被手臂挡住、没有缺描边的洞）再给用户看 GIF。
- 写 assets/source/ppu/orig/malzahar_<tag>.png / .json → `ppu_restyle.py --hero malzahar` → `ppu_hd.py --hero malzahar`（lo_ 帧，`--check` 要过）；hd.rs HEROES ("league_malzahar", 2.2) + SIZES 1.15（编 league.dll 前先问千珏当时的最高号）；按动作条的出手帧重排技能数据时机，再跑一次模拟。
