# 苍蓝哨戒：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 苍蓝哨戒的造型用户已经定稿。`0_design.png` 是你第 0 步交的 A（raw/generation-02.png 左半边），按 12 px 的格子读回、1:1 定稿（28 × 44 格），这里放大成每格 12 px。它的样子：
>   - 稍微 3/4 朝右，**两块漂浮的高瘦水晶石**并排，没有手脚、没有脸；
>   - **左边那块高**，尖尖的多面晶顶；**右边那块矮**，顶是圆钝的；
>   - 上半截**浅灰绿岩面**，下半截**深海军蓝 / 蓝紫**，底下收成尖，缝边一道**暗红紫细边**；
>   - 中间偏上一个圆孔，孔里一颗**发光的蔚蓝能量核**（中间近白）。
>   每个姿势都照它。
> - 请你画 **15 个姿势**（普攻 2 + 技能 7 + 飘移 4 + 死亡 2），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **格子和定稿一样大：每格 12 px**，画布 **1254 × 1254**，网格从画布左上角对齐。红线是地面（y = 1100）。它是**飘着的**，大部分姿势离地几格，**位置和高度照布局图**。
> - **它只有三个部件**（`0_parts.png`：**红 = 左边高尖石，蓝 = 右边矮圆石，黄 = 蓝核**）。每个姿势的**布局图**（`*_layout.png`）就是我把定稿的这三块**原样挪动、转动**拼出来的，`*_parts.png` 是同一个布局的纯色版：
>   - **每块石头的形状、大小、颜色、切面都和定稿一样**，只是**换了位置和角度**；
>   - 布局图是最近邻转的，**斜边上的锯齿、断线、缺格是转出来的毛病**：请按定稿的画法**重新画干净**（整齐的近黑描边、平涂切面），**不要照抄锯齿**，但位置、角度、大小照布局图；
>   - 两块石头分开以后，**中间露出来的地方是透明的**（它们本来就是两块），石头内侧的断面画成这块石头自己最暗的一档 + 近黑描边；
>   - **蓝核**：亮几圈就画多大（布局图里外面那几圈亮蓝就是它变亮变大），最亮的时候中间发白；**死亡时变暗、最后熄灭**（暗灰蓝，不发光）。
> - 有 `*_ref.png` 的三个姿势（a_fire、d_split、d_down）是它在金铲铲里自己的动作那一帧（同一个 3D 模型、同一张画布、同样高），**只看动势**；模型很细长，**大小和长相以定稿为准**。
> - **不画任何特效**：激光、光弹、光柱、碎石、尘土、光晕都不画（后面另外画）。

## 15 个姿势

| 图 | 文件 | 参考 | 姿势 |
|---|---|---|---|
| 2 | `sentry-pose-a_rise.png` | 布局图 | 普攻起手：整只往上一抬、往后仰一点，蓝核亮一圈 |
| 3 | `sentry-pose-a_fire.png` | attack@300 | 开火：往前一倾，蓝核亮两圈（光弹不画） |
| 4 | `sentry-pose-q_open.png` | 布局图 | 技能1「蔚蓝激光」起手：两块石头往两边让开一点，蓝核变亮 |
| 5 | `sentry-pose-q_beam1.png` | 布局图 | 引导激光（循环第 1 帧）：两块石头分开、稍稍前倾，蓝核亮两圈（激光不画） |
| 6 | `sentry-pose-q_beam2.png` | 布局图 | 引导激光（循环第 2 帧）：同上，整只高一格，蓝核亮三圈（一明一暗地闪） |
| 7 | `sentry-pose-e_split.png` | 布局图 | 技能2「裂石跃迁」：两块石头猛地往左右分开，蓝核单独悬在中间（碎石不画） |
| 8 | `sentry-pose-e_close.png` | 布局图 | 合回去：两块石头往中间合拢，快贴上了 |
| 9 | `sentry-pose-r_open.png` | 布局图 | 大招「棱镜扫射」起手：两块石头上端往外张开成 V 字，蓝核亮两圈 |
| 10 | `sentry-pose-r_blast.png` | 布局图 | 扫射：V 字张到最大，蓝核亮到发白、最大（光柱不画） |
| 11 | `sentry-pose-run1.png` | 布局图 | 飘移 1/4：整只往前倾着飘 |
| 12 | `sentry-pose-run2.png` | 布局图 | 飘移 2/4：往上浮一格 |
| 13 | `sentry-pose-run3.png` | 布局图 | 飘移 3/4：浮到最高 |
| 14 | `sentry-pose-run4.png` | 布局图 | 飘移 4/4：往下回一格（4 接回 1，循环） |
| 15 | `sentry-pose-d_split.png` | death@375 | 被打碎：两块石头往两边倒开，蓝核变暗 |
| 16 | `sentry-pose-d_down.png` | death@1125 | 倒地：两块石头左右各一块躺在地上，蓝核熄灭（暗灰蓝色，不发光，掉在两块中间的地上） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`0_parts.png`（三个部件）、`1_core.png`（蓝核放大 12 倍）、这个姿势的 `*_layout.png` 和 `*_parts.png`，有 `*_ref.png` 的也附上。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, a slight 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (the red line is the ground) - TWO TALL CRYSTAL SHARDS FLOATING side by side with NO limbs and NO face: the LEFT shard taller with a pointed faceted tip, the RIGHT shard shorter with a blunt top, PALE SAGE / GREY-GREEN rock above and DARK NAVY / BLUE-VIOLET below tapering to points, a thin dark red-violet edge by the gap, and A GLOWING AZURE CORE (near-white centre) in the round hole between them; B the same design in its THREE PARTS: RED = the left shard, BLUE = the right shard, YELLOW = the core; C the core shown 12x; D the LAYOUT of THIS POSE: the design's own three parts moved and turned (rotated nearest-neighbour, so its slanted edges are jagged and broken - that is NOT the look, only the placement); E the same layout in flat part colours; F (if attached) a 3D render of the creature's own game model in this pose - only its motion, never its thin proportions or 3D shading.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images D and E: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; each part exactly where and at the angle D and E put it, at the same height above the red ground line.
EACH SHARD IS IMAGE A'S SHARD: the same shape, size, colours and flat facets, only moved and turned - redraw its turned edges CLEAN (a tidy continuous near-black outline, flat facets), never copy the jagged rotation; never shrink or stretch a shard. Where the shards have moved apart the space between them is EMPTY (transparent): they are two separate stones; the inner face of a shard its own darkest shade inside the outline. The CORE as big as the layout shows it: its bright blue rings are the core glowing bigger, white in the middle at its brightest; where the pose line says it dims or goes out, make it dark.
The same colours as image A; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no laser, no bolt, no beam, no rubble, no dust, no motion lines, no glow halo outside the core), no background, no ground, no shadow, no text, no grid lines, no guide colours.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_rise: `RISE - the whole figure lifted a little and tipped back slightly, the core one ring brighter.`
- a_fire: `FIRE - tipped forward, the core two rings bright (do NOT draw the bolt).`
- q_open: `PART - the two shards easing apart a little, the core brightening.`
- q_beam1: `LASING 1 of 2 - the shards apart, leaning forward a little, the core two rings bright (do NOT draw the laser).`
- q_beam2: `LASING 2 of 2 - the same one square higher, the core three rings bright (it pulses between the two).`
- e_split: `SPLIT - the two shards flung apart to the left and right, the core hanging alone between them (do NOT draw any rubble).`
- e_close: `CLOSING - the shards coming back together, nearly touching again.`
- r_open: `OPEN - the shards' tops swung outward into a V, the core two rings bright.`
- r_blast: `BLAST - the V opened as wide as it goes, the core at its biggest, white-hot (do NOT draw the beam).`
- run1: `GLIDE 1 of 4 - leaning forward, floating along.`
- run2: `GLIDE 2 of 4 - one square higher.`
- run3: `GLIDE 3 of 4 - at its highest.`
- run4: `GLIDE 4 of 4 - one square lower again (4 runs on into 1).`
- d_split: `BREAKING - the two shards falling apart to either side, the core dimming.`
- d_down: `DOWN - both shards lying on the ground, one to each side, the core gone out (a dull dark grey-blue, no glow) lying between them.`

## 交回

- 每个姿势一张：`outputs/sentry-poses/sentry-pose-<名字>.png`（1254 × 1254、真透明背景、每格 12 px）。
- 原始生成图原样放进 `outputs/sentry-poses/raw/`。
- `generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **15 张都画完再交**。最后写 `outputs/sentry-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sentry_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sentry/codex_poses/`，**先量 Codex 实际的格子**（不一定是 12 px），读 raw。
- **每张按定稿的石头大小读**（codex-fit-shrinks-bodies：分开、张开、倒地时 Codex 容易把石头画小）：以两块石头各自的高度对齐定稿。
- 每帧放大 8 倍检查：两块石头是定稿的形状和颜色；分开处是透明的；蓝核大小随姿势变；没有特效。
- 布局包：`tools/art/pack_sentry_poses.py`（定稿拆成左石、右石、蓝核三块，按 POSES 挪动、转动、加光圈）。这份提示词由 `tools/art/gen_sentry_pose_md.py` 生成。
