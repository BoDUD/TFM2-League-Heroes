# 纳什男爵改腿第 2 步：把选定的 L6 蜘蛛腿画到所有动作和跑步上（给 Codex 的提示词）

> 用户从第 1 步的两版里选了 **L6（每边 3 条腿）**（附图 `design/L6_11px.png`，`design/L6_9px.png` 是同一张按每格 9 像素画的）。
>
> 这一步拿**你之前画好的动作图**：10 个动作（`poses/`）和 8 帧跑步（`run/`），都是 1254×1254、每格 9 像素。**每一张只换腿**：去掉两条紫色后腿、地上的象牙白三趾脚和旧腿根，换成 L6 的蜘蛛腿，按下面表里每个动作的姿势摆；**其余一格都不动**（头、头冠、两只小蛇头、两只象牙白大爪、青绿腹甲、紫色鳞甲、身体的弯曲）。钻地那张（`e_dig`，只露出头冠）没有腿，不用画。

## 要点

- **同一张画布、同一套 9 像素网格、人物位置不变**：交回的每张图和原图叠在一起，腿以外的地方逐格一样（我这边会逐格比对）。
- **腿照 L6**（`design/L6_9px.png` 是按每格 9 像素画的待机图）。**腿和身体的比例照 L6**：动作图画得比待机图大一些，腿跟着身体一起放大——腿尖到腿尖的跨度约是两只象牙白大爪之间宽度的 1.4 倍，膝盖略低于青绿腹甲的底端；腿的粗细仍是靠身体 2 格、腿尖 1 格：
  - 身体底部是一小段**深紫色的分节柱子**，从柱子底部一圈伸出**每边 3 条**细长的蜘蛛腿；
  - 每条腿先往外、往上到膝关节，再往下、往外折到**尖尖的腿尖**；靠身体那头 2 格粗，往腿尖越来越细，腿尖 1 格；
  - **最大的一对在两侧中间**；
  - **近处的腿**在身体前面、亮一档，**远处的腿**在身体后面、暗一档；
  - 颜色和 L6 一样（深紫几档，膝盖一格亮紫高光，腿尖最暗）；**腿上没有象牙白**。
- **腿尖落在地面线上**（`guides/` 里每张图的灰线，是原来脚的最低处）；表里写了抬起、蜷起来的除外。
- 和原图一样：2 格宽的近黑描边，每种材质 3–4 档平涂，不要渐变、柔光、零散杂色格；全硬 alpha，真透明背景。不画特效、地面、地洞、投影。

## 每个动作的腿怎么摆

| # | 文件 | 动作 | 腿 |
|---|---|---|---|
| 01 | `poses/01_a_rear.png` | 普攻前往后仰 | 六条腿都撑地；身体往后仰，后面的腿张得更开撑住，前面一对往前撑 |
| 02 | `poses/02_a_bite.png` | 往前猛咬 | 前腿往前伸、扎地，后腿往后蹬；腿尖都在地面线上 |
| 03 | `poses/03_q_breath.png` | 压低身子喷酸 | 六条腿压低、往两边大大张开撑住 |
| 04 | `poses/04_e_dive.png` | 一头扎进地里 | 腿往身体下面收拢，腿尖朝下，像要缩进地里 |
| 05 | `poses/05_e_rise.png` | 从地里钻出来 | 腿从地面往外张开、刚撑起来，腿尖扎在地面线上 |
| 06 | `poses/06_r_rear.png` | 大招前高高立起 | 后面四条腿撑直、张开把身体顶高；**最前面一对抬在空中**、腿尖朝前（威吓） |
| 07 | `poses/07_r_slam.png` | 往下猛砸 | 六条腿往两边平摊开，身体压得很低 |
| 08 | `poses/08_r_spit.png` | 立着连续喷酸 | 六条腿稳稳撑地 |
| 09 | `poses/09_d_fall.png` | 死亡：侧身倒下 | 近处的腿离地乱蹬，远处的腿还撑着、开始弯曲 |
| 10 | `poses/10_d_down.png` | 死亡：倒在地上 | 腿往身体收拢、蜷起来（像死掉的蜘蛛），腿尖朝里 |

## 跑步：蜘蛛的步法（8 帧一个循环）

两组腿交替：**A 组 = 近处前腿 + 远处中腿 + 近处后腿**，**B 组 = 远处前腿 + 近处中腿 + 远处后腿**。8 帧的上半身原样不动（它们本来就是同一个上半身）。

| 帧 | 腿 |
|---|---|
| `run/run1.png` | A 组在空中迈到一半（腿尖离地 1–2 格），B 组撑地 |
| `run/run2.png` | A 组往前伸、快落地；B 组撑地往后蹬 |
| `run/run3.png` | 两组都着地：A 组在前，B 组在后 |
| `run/run4.png` | B 组抬起离地，A 组撑地 |
| `run/run5.png` | B 组在空中迈到一半，A 组撑地 |
| `run/run6.png` | B 组往前伸、快落地；A 组撑地往后蹬 |
| `run/run7.png` | 两组都着地：B 组在前，A 组在后 |
| `run/run8.png` | A 组抬起离地，B 组撑地 |

`style/skarner_run.png` 是本包的斯卡纳（蝎子）跑步，8 倍放大：**只看**几条细腿怎么一前一后地画。

## 提示词（每张图一次，`{动作}` 换成上表那一行的英文）

```text
Attached: image 1 is a finished pixel-art game sprite to EDIT (a huge purple void serpent, 3/4 view facing right, on a 1254x1254 transparent canvas, every square 9 px on one straight grid); image 2 is the same with its ground line in grey; image 3 shows the NEW LEGS this creature must have, (the idle, drawn at 9 px a square): a short dark purple segmented column at the bottom of its body and THREE long, thin, jointed spider legs on EACH side (each leg goes up and out to a high knee, then down and out to a SHARP POINTED TIP; 2 squares thick at the body, thinning to a 1-square tip; the biggest pair at the middle of the sides; the near legs in front of the body and one shade brighter, the far legs behind it and one shade darker; dark purple shades, a one-square brighter purple highlight on each knee, the tips the darkest purple, NO ivory on the legs). Image 4 is STYLE ONLY (thin legs in a walk cycle, shown 8x).
EDIT IMAGE 1, ONLY ITS LEGS. Remove its two purple hind legs, its two ivory three-toed feet and the old leg roots; give it the new legs of image 3 - in the SAME PROPORTION to the body as in image 3 (this picture may be drawn a little bigger than image 3: scale the legs with its body - tip to tip about 1.4 times the width across the two ivory claws, the knees a little below the bottom of the teal belly; 2 squares thick at the body, a 1-square tip), the same colours - in this pose: {pose}. Everything else stays EXACTLY as it is, square for square: the head, the crest, both small serpent heads, both big ivory claws, the teal belly, the purple scales, the curve of the body. Keep the same canvas, the same 9 px grid and the same position. Leg tips on the grey ground line of image 2 unless the pose lifts or curls them.
Same pixel art as image 1: a 2-square near-black outline joined to the figure's outline; every material in its own 3-4 flat shades; no stray single odd squares; no dithering, no gradients, no blur, no anti-aliasing, no soft glow; every pixel fully opaque on a genuine transparent background. No effects, no ground plane, no hole, no cast shadow, no text, no frame, no other characters.
```

`{pose}`：

- 01 a_rear: `rearing back before a bite: all six legs on the ground, the rear legs spread wider to hold the weight, the front pair braced forward`
- 02 a_bite: `lunging forward to bite: the front legs reaching forward and stabbing the ground, the rear legs pushing back; all tips on the ground line`
- 03 q_breath: `leaning low to breathe acid: all six legs spread wide and low to the sides, braced`
- 04 e_dive: `diving head first into the ground: the legs drawn in under the body, tips pointing down, as if folding into the earth`
- 05 e_rise: `rising out of the ground: the legs just unfolding outward from the ground, tips stabbing the ground line`
- 06 r_rear: `reared up tall before its ultimate: the four rear legs straight and spread to lift the body high; the FRONT PAIR raised in the air, tips pointing forward, threatening`
- 07 r_slam: `slamming down: all six legs splayed flat out to the sides, the body pressed low`
- 08 r_spit: `standing upright spitting acid: all six legs planted steadily`
- 09 d_fall: `toppling over sideways as it dies: the near legs lifted off the ground and flailing, the far legs still on the ground and starting to buckle`
- 10 d_down: `lying dead on the ground: the legs curled in toward the body like a dead spider's, tips pointing inward`
- run1: `walking, a spider's gait (group A = near front, far middle, near rear; group B = far front, near middle, far rear): group A in the air at mid-swing, tips 1-2 squares above the ground; group B planted`
- run2: `walking: group A reaching forward, about to land; group B planted and pushing back`
- run3: `walking: both groups on the ground, group A ahead, group B behind`
- run4: `walking: group B lifting off the ground, group A planted`
- run5: `walking: group B in the air at mid-swing, tips 1-2 squares above the ground; group A planted`
- run6: `walking: group B reaching forward, about to land; group A planted and pushing back`
- run7: `walking: both groups on the ground, group B ahead, group A behind`
- run8: `walking: group A lifting off the ground, group B planted`

附图顺序：1 = `poses/NN_<动作>.png` 或 `run/runK.png`（要改的图），2 = `guides/` 里同名的图（灰色地面线），3 = `design/L6_9px.png`（新腿），4 = `style/skarner_run.png`（只看风格）。`refs/reference_baron.png` 是用户给的金铲铲截图，看不清腿长什么样时参考。

## 交回前请检查

- 1254×1254，真透明背景，**每格 9 像素、和原图同一套网格**，人物位置不变；**腿以外逐格和原图一样**。
- 每张都是**每边 3 条**细长、带关节、腿尖尖的蜘蛛腿，和身体的比例和 L6 一样；**没有原来的两条后腿和白脚、旧腿根**；腿上没有象牙白。
- 姿势照表：抬起的腿（r_rear 的前一对、跑步迈步的那组）离地，蜷起来的（d_down）收在身体旁边，其余腿尖落在灰线上。
- 跑步 8 帧：两组腿交替，run3 / run7 两组都着地，run1 / run5 一组在空中正中间。
- 交付：`outputs/baronnashor-legs2/baronnashor-legs2-<动作>.png`（10 张：a_rear a_bite q_breath e_dive e_rise r_rear r_slam r_spit d_fall d_down）和 `baronnashor-legs2-run1.png` … `run8.png`（8 张）；原始生成图放进 `outputs/baronnashor-legs2/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/baronnashor-legs2/HANDOFF.md`，再打包成 `outputs/baronnashor_legs2_done.zip`。18 张都画完再交，中间不要停。

## Claude 收到后（给 Claude 看）

1. 解压到 `assets/source/baronnashor/codex_legs2/`；每张和原图（`codex_poses`、`codex_run`）逐格比，腿以外不该变；数每边的腿、看腿尖和地面线。
2. 待机：L6 按 11 像素读回成 `hd/idle.png`（80×94，PPU 2.04 不变，宽了 22 格）。
3. `design_baronnashor_poses.py` 的动作和跑步来源换成 `codex_legs2`（跑步仍是一个上半身），`rig_baronnashor.py` 标签和时长不变；然后 `ppu_restyle`、`ppu_hd`、`hero_reels --hero baronnashor`，佛耶戈 / 俄洛伊 / 妮蔻 / 塞拉斯的副本照常 `make_override.py`；出预览（技能 gif、帧表、和邻居的大小对比）给用户看。
