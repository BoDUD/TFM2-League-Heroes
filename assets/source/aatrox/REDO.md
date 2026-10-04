# 剑魔：重画跑步的腿、Q 三段、大招变身和开大翅膀（给 Codex 的提示词）

> **为什么重画**（用户 2026-10-04）：「剑魔Q的还原度太差了」「腿部还是有点怪」「大招的效果也和原本LOL里面不一样吧」，然后「让codex重画」。
> - **Q**（`ref/ours_vs_lol_q.png`，上灰底 = 英雄联盟，下绿底 = 现在的）：原版三段都是**全身动作**——Q1 蓄力后单脚拔高、把剑举过头顶，再整个人蹲下把剑砸在身前很远的地上；Q2 拧身把剑举到身后，再压低身子向前横扫；Q3 跃起、在空中举剑，再扑下来砸地。现在的版本身体一直是待机站姿，只有手臂和剑在转，像原地挥棍子；而且太快（0.37 秒就砍中，原版 0.6 秒）。
> - **跑步的腿**（`now/aatrox_run_now.png`）：现在的腿是把待机的直腿整条斜推出来的，没有膝盖弯曲，脚尖朝外，大跨步那几帧像倒 V 字的高跷。
> - **大招**（`ref/ours_vs_lol_r.png`）：原版变身是背后展开一对**很长的暗红色翅膀**（像飘动的披风/膜翼，不是蝙蝠翼），人浮起来咆哮，最后两翼向两边垂下；现在的是左右对称的紫色蝙蝠翼，之后头顶还叠了一层橙色火焰翅膀——颜色、形状都不对。
>
> **造型不变**：`design/aatrox_design.png`（8 倍，1024×1024；翅尖到脚底 40 行、39 格宽、15 色；脚底在第 99 行，两脚中间在第 64 列）就是标准：带角的钢青色头盔、阴影脸和两只红眼睛、血红胸甲和橙色符文、钢青色肩甲和护手、近侧钢手和远侧红手臂、钢青色护腿和爪形铁靴、半收的深紫色翅膀、大剑。每一帧都照它的颜色、明暗和大小，只改姿势。

## 要交的 6 张图

| 文件 | 内容 | 帧（毫秒） | 排版（列 × 行，像素） |
|---|---|---|---|
| `aatrox_run.png` | 跑步：**只重画腿** | 125 125 125 125 125 125 125 125 | 4 x 2，3584 x 1536 |
| `aatrox_skill.png` | Q1：跳起举剑、蹲下砸地（全身） | 100 150 150 100 100 100 50 50；**第 6 帧砍中**（600 毫秒） | 4 x 2，3584 x 1536 |
| `aatrox_q2.png` | Q2：拧身举剑、压低横扫（全身） | 100 150 150 100 100 100 50 50；**第 6 帧砍中** | 4 x 2，3584 x 1536 |
| `aatrox_q3.png` | Q3：跃起举剑、扑下砸地（全身） | 100 150 150 100 100 100 50 50；**第 6 帧砸中** | 4 x 2，3584 x 1536 |
| `aatrox_ult.png` | 大招变身：暗红长翼展开、浮起咆哮、两翼垂下 | 100 100 100 100 100 100 100 100 | 4 x 2，3584 x 1536 |
| `aatrox_rwings.png` | 开大期间的翅膀（**只画翅膀**，循环） | 150 150 150 150 150 150 | 3 x 2，2688 x 1536 |

每张的格子都是 112×96 格（8 倍 = 896×768 像素），排版和 `guide/aatrox_guide_<动作>.png` 一模一样：帧 N 在同一格，蓝十字是站位点，红线是脚底线（红线下面的粉色区域什么都不能画，游戏在那里画血条），空格留空。

## 附图

| 文件 | 内容 |
|---|---|
| `design/aatrox_design.png`、`_1x.png` | 定稿造型（8 倍 / 原尺寸） |
| `design/aatrox_head.png`、`_1x.png` | 头（角、头盔、阴影脸、红眼睛、下巴）：在 128×128 画布上 x 60–70、y 61–72，**按形状贴，不是整个方框** |
| `design/aatrox_sword.png`、`_1x.png` | 大剑（画布上 x 37–58、y 85–95）：剑身、倒刺、护手的橙色眼睛、两叉剑尖 |
| `design/aatrox_palette.png` | 造型的 15 种颜色 |
| `now/aatrox_<动作>_now.png` | 游戏里现在的动作条（8 倍）：跑步、Q1–Q3、变身，还有待机和普攻（手臂、剑的画法照它们） |
| `now/aatrox_rwings_body_under.png` | 翅膀循环每格下面的待机身体（只是对位用，不要画进去） |
| `lol/lol_pose_<动作>.png` | 英雄联盟原版同一帧的高清渲染，格子和位置一样（Q 和跑步去掉了原版翅膀，变身和翅膀循环留着） |
| `lol/lol_now_<动作>.png` | 同一帧按游戏尺寸取色，8 倍 |
| `guide/aatrox_guide_<动作>.png` | 格子、站位点（蓝十字）、脚底线（红线）、帧号；跑步图上的橙色虚线是**腰线** |
| `ref/shoe_schedule.png` | 跑步每帧两只鞋的位置和抬起高度 |
| `ref/approved_run_vi.png` | 我们包里另一个英雄（蔚）已经通过的跑步，**只看腿怎么动**（每半个周期前后脚交换） |
| `ref/lol_rform.png` | 原版开大后的样子（浮空待机、跑、普攻、Q1），看翅膀的形状和颜色 |
| `ref/ours_vs_lol_q.png`、`ours_vs_lol_r.png` | 现在的问题：我们的 Q、大招和原版并排 |
| `aatrox_cells.json` | 每张图每帧的站位点（格子里第几列、第几行，单位方块）和时长 |

## 共同规则（6 张都一样）

- **像素**：每个像素一个 8×8 方块，对齐同一个网格；没有抗锯齿、模糊、半透明；透明度只有 0 和 255。站直时和造型一样高（40 行）。
- **颜色**：只用造型的 15 种颜色（`#0A0408 #270D28 #181F2B #4B0827 #1F2A38 #263647 #42224C #8F0E2B #3B586B #BF1630 #68407A #F2323B #5B8498 #FF7A2A #95C3D4`）——翅膀要用的暗红色也在里面（胸甲和剑刃的血红、`#8F0E2B` 一类的暗红、近黑描边）。外轮廓 1 格近黑描边（`#0A0408`），描边里面用材质自己的暗色，不要第二圈黑、不要零散的黑格、不要抖动噪点。
- **头**：每一帧都把造型的头原样贴上（只平移，不旋转、不压扁、不重画），所以头永远是 3/4 正面朝右、两只红眼睛都在；头下面直接接肩甲，不要脖子。
- **大剑**：每帧都在、完整、笔直，和造型一样大（约 19–20 格长、4–5 格粗）；只跟着手移动和转动；握剑的手是实心的、连着剑柄。
- **手臂**：和现在的动作条一样粗（3 格左右，带描边），近侧钢手、远侧红手臂和红爪；不要 1 像素的细棍、不要飘着的手。
- **身体是一整块**：胸甲、腰、胯和两条腿连在一起，**不能上下身脱节、不能掏空胯部**（上一次重画就是这样被退回的）；腿用造型自己的钢青色护腿和爪形铁靴，两条腿同样的颜色和粗细（大腿约 4 格、小腿约 3 格），近侧的腿压在远侧的腿上面。
- **方向**：3/4 正面朝右，挥剑、砸地、冲刺都朝图的右边；**不画背影、不画倒立**（原版有转身背对镜头的帧，我们画成侧身蓄力就好）。
- **不画特效**：剑光、砍痕、冲击波、地裂、尘土、红色光环都是另外的特效；只画角色（翅膀循环那张只画翅膀）。
- **脚底线**：每格里最低的像素在脚底线上（红线），红线下面什么都没有。跳起的帧整个人离开地面，影子也不要画。
- **排版**：和 guide 一模一样的尺寸和格子。背景透明（做不到时用纯绿 `#00FF00`，**不要洋红**，会吃掉紫色的翅膀和剑身）。不要网格线、文字、编号、参考线。

## 1. 跑步：只重画腿（`aatrox_run.png`）

1. **腰线（橙色虚线）以上一个像素都不要动**：头、翅膀、身体、两只手和大剑都照 `now/aatrox_run_now.png` 原样保留（导入时我们会把现在的上半身贴回去）。大剑从腰线往下伸到左下方的那一段也保留，压在腿上面。
2. 只重画腰线以下的两条腿，照 `ref/shoe_schedule.png`：
   - A = 近侧的腿，B = 远侧的腿；
   - 第 1–4 帧：A 踩在地上，从 +3 格往后滑到 −3 格（在身体下面往后推，第 4 帧脚跟离地）；B 从身后 −4 格抬起（第 2、3 帧抬到 3 格高，膝盖弯、小腿往后收），第 3 帧经过 A（两膝交叉），第 4 帧伸到前面 +4 格准备落地；
   - **第 5–8 帧：和 1–4 一样，A、B 对调**；
   - 两只鞋**最多相距 7–8 格**（不要弓步、不要倒 V 字），**两只鞋尖都朝右**（前进方向）；
   - 踩地的鞋底贴在脚底线上，抬起的鞋按表里的格数抬高；**膝盖自然弯曲**（大腿和小腿之间有角度），不要直棍腿；
   - 两条腿都是待机里腿的材质（钢青色护腿、深色甲片、爪形铁靴），近处的腿永远压在远处的腿上面，交换的是前后位置，不是谁在上层；不要近亮远暗。
3. 腿的动法看 `lol/lol_pose_run.png`（原版跑步：重心前倾、膝盖弯、后脚踢起）和 `ref/approved_run_vi.png`（我们已经通过的交叉步）。

## 2. Q 三段：照原版画全身动作（`aatrox_skill.png`、`aatrox_q2.png`、`aatrox_q3.png`）

- 每张 8 帧，**第 6 帧是砍中的那一帧**（第 1–5 帧加起来正好 600 毫秒，原版的 0.6 秒前摇）；第 7 帧停在砍中的姿势，第 8 帧收回到待机。
- 姿势照 `lol/lol_pose_<动作>.png` 同一格的那一帧（身体高度、跳多高、蹲多低、剑在哪里），比例照造型（大头盔、瘦身体、剑的大小），站位照 guide 的蓝十字。
- **全身都动**：膝盖弯、身体前倾或后仰、单脚拔高、蹲下、跳起都照原版；腿还是造型的护腿和铁靴，只是弯曲和移动，和胯连在一起。
- 翅膀：保持造型里半收在背后的样子，跟着身体转一点；不要张开（张开只在大招）。
- **剑每帧完整笔直**；砍中那一帧剑尖落在身前远处的地面上（Q1 正前方砸地，Q2 平着扫到身前，Q3 在身前砸地）。guide 里原版的影子在第 6–7 帧剑尖伸到了红线下面（透视造成的），**我们的剑尖停在脚底线上**，不能进粉色区域。

`skill`（Q1）：1 待机开始蓄力，剑往后收；2–3 侧身蓄力，剑举在肩后（原版这里转过身去，我们**不画背影**，画成侧身、剑在肩后）；4 单脚拔高、身体拉长，双手把剑举过头顶；5 剑从头顶往前劈下来，身体还在高处；6 **砍中**：整个人蹲下，剑笔直地砸在身前远处的地上；7 保持；8 起身回到待机。

`q2`（Q2）：1 待机开始拧身；2–3 拧身蓄力，剑举到身后；4 单脚拔高，剑高举在身后；5 向前冲、剑往前横扫；6 **砍中**：压低身子成低弓步，剑平着横扫到身前（剑尖朝右，和地面平行，大约腰下的高度）；7 保持；8 回到待机。

`q3`（Q3）：1 下蹲蓄力；2 起跳，剑举起（原版这里把剑抛起来转，我们**剑一直握在手里**，举过头顶）；3 跃到半空，双手举剑过头；4 继续上升；5 跳到最高，身体拉长；6 **砸中**：扑下来落地成低弓步，剑笔直地砸在身前地上；7 保持；8 回到待机。跳起最高时离地大约 10 格（照 guide 里原版的高度）。

## 3. 大招变身（`aatrox_ult.png`）

- 8 帧 × 100 毫秒，照 `lol/lol_pose_ult.png`：1 待机、身体压低聚力；2 起身离地，背后开始长出暗红色翅膀；3 翅膀向两边展开；4 一只翅膀高高扬起、一只向后拖得很长，人浮在空中，张开手臂咆哮；5–6 翅膀在身后扇动、拖曳；7 翅膀往下收；8 **落地成待机的站姿，两只翅膀向身体两边垂下**（这一帧要和 `aatrox_rwings.png` 的第 1 帧一样）。
- **翅膀的样子照原版**（`lol/lol_pose_ult.png`、`ref/lol_rform.png`）：很长（展开时每只大约和他一样高）、尖细的暗红色膜翼，边缘像撕开的布一样有几道尖角，几根细长的骨；颜色用造型里的暗红、血红和近黑描边，亮边用血红，**不要紫色、不要橙色火焰、不要平板多边形**。
- 剑一直握在近侧手里（原版开大时看不清剑，我们保留）。

## 4. 开大期间的翅膀（`aatrox_rwings.png`）

- 这张是开大 10 秒里一直跟着他的「光环」：**只画翅膀**，身体不画（`now/aatrox_rwings_body_under.png` 是每格下面待机身体的位置，只用来对位）。翅膀根部藏在身体后面（游戏里身体画在翅膀上面），从肩胛向两边、向下垂。
- **左右对称**（游戏里这张图不会跟着他转身翻转）：两只翅膀以站位点为中心，一左一右，形状一样，像原版开大站着时那样向下垂、尖端拖到膝盖附近，宽度每边大约 16–22 格。
- 6 帧 × 150 毫秒循环：翅膀慢慢扇动（尖端上下 1–2 格、翼膜张合 1 格），第 6 帧能接回第 1 帧；第 1 帧 = 变身最后一帧里的翅膀。
- 颜色和变身里的翅膀一样（暗红、血红亮边、近黑描边），翅膀之外的地方全透明。

## 英文提示词（每张都附：造型图 + 这张的 now 条或 guide + 这张的 lol_pose）

```text
Attached: FIRST the approved pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, head, armour, greatsword, wings and pixel style exactly; SECOND the current strip or the guide of this animation (cells, standing points, feet line); THIRD the original 3D animation at the same frames in the same cells - copy its poses (the whole body: knees, hips, lean, jumps, crouches, the sword) but keep the FIRST image's proportions and size.
The character: a demon warrior in steel-teal armour with a horned helm, the face hidden in shadow with two glowing red eyes, a blood-red chest with a glowing orange rune, one red demonic arm, half-folded dark plum wings, and a huge straight greatsword of dark plum with blood-red barbed edges, an orange eye at the guard and a two-pronged hooked tip.
Pixel rules: every pixel one crisp 8x8 square on one grid, no anti-aliasing, no blur, no semi-transparency; ONLY the FIRST image's 15 colors: #0A0408 #270D28 #181F2B #4B0827 #1F2A38 #263647 #42224C #8F0E2B #3B586B #BF1630 #68407A #F2323B #5B8498 #FF7A2A #95C3D4; one 1-square near-black outline (#0A0408), each material's own dark shade inside it, no second black ring, no stray black squares, no dithering. The head (horns, helm, shadow face, both red eyes) is COPIED from the FIRST image in every frame and only moved. The greatsword is whole and straight in every frame. Arms about 3 squares thick ending in solid fists or claws that hold the grip. The body is one piece: chest, waist, hips and both legs connected; both legs use the design's steel-teal greaves and clawed boots, bent at the knees, the near leg drawn over the far leg. 3/4 front view facing right, every swing to the right, never his back, never upside down. Nothing below the red feet line. No effects (no slash trails, glows, shockwaves, dust, auras) - only the character. Layout exactly like the guide: [grid], each cell 112x96 squares (896x768 px), [size] px; transparent background (else solid #00FF00, never magenta); no grid lines, labels or guide marks.
Animation: [animation]
```

`[animation]` 用上面各节的文字（跑步：只重画腰线以下的腿，照鞋子的表；Q：8 帧，第 6 帧砍中；变身：暗红长翼；翅膀循环：只画对称的翅膀）。

## 交付

放在 **`outputs/aatrox-redo/`**：`aatrox_run.png`、`aatrox_skill.png`、`aatrox_q2.png`、`aatrox_q3.png`、`aatrox_ult.png`、`aatrox_rwings.png`（8 倍，尺寸和 guide 一样），`manifest.json`（每帧的格子矩形、站位点、不透明范围，Q 砍中那一帧的剑尖位置），打包成 `outputs/aatrox_redo_done.zip`，**最后写 `HANDOFF.md`**（每张怎么做的、哪里没做到）——写完 HANDOFF 就算交付。

## 交回前自查

- [ ] 6 张图尺寸、格子和 guide 一样，帧 N 在同一格；每个像素是对齐的 8×8 方块，透明度只有 0 和 255；
- [ ] 只用造型的颜色；头每帧都是造型的头（两只红眼睛）；剑每帧完整笔直，手握着剑柄；
- [ ] 跑步：腰线以上和现在一模一样；两条腿每半个周期交换前后，膝盖弯，鞋尖朝右，两只鞋最多相距 7–8 格，颜色一样；
- [ ] Q：全身动作照原版，第 6 帧砍中，剑尖在身前地上（Q2 平扫）；没有背影；上下身连在一起；
- [ ] 变身：暗红长翼（不是紫色蝙蝠翼、不是火焰），最后一帧站回地上、两翼下垂；翅膀循环左右对称、只有翅膀、首尾相接；
- [ ] 脚底线以下没有像素；黑边干净；没有特效、网格、文字。

## Claude 导入时（给 Claude 看）

- 检查（方块、透明度、色板、脚底线、连通块、手臂粗细、剑完整、头和造型一样）；跑步把现在的上半身贴回腰线以上；头不对的帧换回造型的头；`import_native.py` 的 COMPLETE 补描边。
- 用包里的 `aatrox_cells.json`；技能数据改成 Q 第 6 帧（tick 36）砍中、动作 48 tick，大招动作 48 tick；`rwings` 做成 `r_aura` 的新特效（跟随、z −1），在变身结束后才出现（单独的标记 buff）；量 Q 砍中帧的剑尖重新定砍痕挂点；重跑模拟、做预览 GIF 给用户审核。
