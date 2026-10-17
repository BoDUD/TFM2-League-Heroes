# 蒸汽机器人 布里茨：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：B2**（你返修后的 B 版，Claude 逐格读回，没有缩放）：`design/blitzcrank_design.png`（放大 8 倍，1024×1024，46×44 格、16 色，鞋底在 y=792–799）。**造型图就是标准**，颜色、形状、头、眼睛、烟囱、炉门、手臂和拳头一律照它。
> - **待机条已经做好**（`blitzcrank_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画（其中 `q_pull` 是 Q 钩中敌人后拉人时循环的 3 帧）。
> - 帧数、每帧时长、出手帧和站位照 `now/blitzcrank_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。出拳、飞爪、上勾拳这几张，参考图里他朝右转了一些（让拳头往右打），身体照参考图转，头仍然是造型图的头。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。最好打成一个 zip（`blitzcrank_strips_pack_done.zip`）放在 outputs 里。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/blitzcrank_palette.png`，或直接读 `design/blitzcrank_design_1x.png`）。**先把眼睛的颜色 `#F3A4D9`、`#FFF8FD` 从色板里去掉**，它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/blitzcrank_head_1x.png`：金色圆顶、中间竖棱、两只 3×3 的眼睛和深色眼窝、下面的钢领口；在 128×128 画布上的范围 x 60–68、y 59–68）原样贴进每一帧头的位置，只平移；身体倾斜时整体倾斜。死亡倒地的帧可以不贴（眼睛变暗）。头下面的钢领口和锅炉身体的位置关系每一帧都和造型图一样（不要把头压进身体，也不要让它飘起来）。
5. **身体部件照造型图**：两根钢烟囱、胸口钢圈炉门和闪电纹、肩块、黑色软管环、手臂（肩块—前臂—拳头三段）、方块手指和钢指节螺栓、短腿和大扁脚，都是造型图上的样子和颜色，跟着身体动；手臂转动时整段一起转，方块不能散开。
6. 对位：每帧按 `blitzcrank_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人连成一块，拳头至少 8×8 格、连着至少 4 格粗的手臂。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/blitzcrank_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，鞋底第 99 行 | 每张动作图的第一张附图 |
| `design/blitzcrank_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/blitzcrank_head.png`、`blitzcrank_head_1x.png` | 只有头（圆顶、眼睛、钢领口），在画布上原来的位置 | 贴头 |
| `design/blitzcrank_palette.png` | 造型图的全部 16 色（暗到亮） | 色板 |
| `blitzcrank_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/blitzcrank_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体和手臂的动作 |
| `guide/blitzcrank_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `blitzcrank_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/blitzcrank_picture.png` | 用户选的原画（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_big.png`、`style/quality_bar.png` | 团战经理2 原版的大块头和机器人、本包的大块头英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（44 格，烟囱顶到鞋底），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 16 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（圆顶、竖棱、两只眼睛、领口逐格一样），只平移或整体倾斜；眼睛的颜色 `#F3A4D9`、`#FFF8FD` 只用在眼睛上。
- **手臂和拳头**：拳头至少 8×8 格（三块方块手指和钢指节螺栓），手臂从肩块到拳头至少 4 格粗（含描边），分得清肩块、前臂、拳头；每帧整个人连成一块。**Q 的第 4–6 帧和 `q_pull` 的 3 帧，出手那条手臂末端没有手**，是一个深色六角形的腕口（飞出去的手和锁链是特效，不画）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），垂下的拳头也不能低于它。只有死亡躺倒的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间两腿交错），腿和脚的颜色和待机一样，两只大拳头和腿反向摆动；每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，看得到胸口炉门和眼睛，不画背影。**只画角色**：蒸汽、电光、飞出去的手和锁链、冲击波这些都是单独的特效，不要画。每个动作开始和结束都接近造型图的待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/blitzcrank_design.png`，第二张 `now/blitzcrank_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `blitzcrank_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, eyes, smokestacks, chest port, arms and fists and its pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms and the fists from it.
The character: a huge top-heavy steam robot: a round gold-yellow boiler body with a big round steel-ringed chest port (a bronze disc with a zigzag lightning seam), a small gold dome head with two glowing pink-white eyes sitting low in a steel collar, two short steel smokestacks behind the head, black ribbed hoses looping over the shoulders, enormous blocky gold arms (a shoulder block, a forearm, a giant fist of three square finger blocks with steel knuckle bolts), short dark steel piston legs and big flat gold feet.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (44 squares tall from the top of the smokestacks to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 16 colors of the FIRST image, no new colors: #170F1D #292536 #672D01 #373E56 #984B01 #454759 #BC6802 #DD8702 #67718F #F9AF07 #FDDC36 #A2AECC #BFCDE0 #F3A4D9 #E2EBFC #FFF8FD. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (the gold dome with its middle ridge, the two eyes in their dark sockets, the steel collar) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play; keep it sitting in the collar on the boiler exactly as in the FIRST image, never sunk into the body or floating above it. The eye colors appear ONLY in the eyes. The smokestacks, the chest port, the shoulder blocks, the hoses, the arms and the fists are the FIRST image's, moving with the body; each fist at least 8x8 squares, each arm at least 4 squares thick from the shoulder block to the fist, never a thin line; the whole figure is ONE connected piece in every frame. In the frames the animation names, the throwing arm ends in an empty dark hexagonal wrist socket with no hand.
Feet line: in every cell the lowest row of his feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not a fist, not a foot - because the game draws the health bar there (the lying frames of the death may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in blitzcrank_cells.json). In a move loop his head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, the chest port and the eyes visible, never his back. Do not draw effects (steam, lightning, sparks, the flying hand, its chain, shock waves, glows) - only the character. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x112 squares (1024x896 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the eye colors only in the eyes, the fists at least 8x8 on arms at least 4 squares thick, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `blitzcrank_idle.png`（待机） | 6 × 160 | — | 3 列 × 2 行，3072×1792 | 第 97 行 | **已做好，不用画** |
| `blitzcrank_run.png`（移动） | 8 帧：83 83 83 84 83 83 83 85 | — | 4 列 × 2 行，4096×1792 | 第 97 行 | `MOVE, 8 frames, one seamless loop of League's run (0.67 s, 8 x 83 ms; the SECOND and THIRD images): the heavy robot stomps forward, the big body rocking a little from side to side, the two huge arms swinging opposite to the legs (the near fist forward while the far leg steps, then the other way); the short piston legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees passing each other in the middle frames, the big flat feet flat on the ground line when planted; the head keeps the same place across the cell relative to the standing point (at most 1 square up or down); frame 8 flows into frame 1.` |
| `blitzcrank_attack.png`（普攻） | 6 帧：70 70 70 70 80 80 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×1792 | 第 97 行 | `BASIC ATTACK, 6 frames, a heavy punch as in the THIRD image (he turns a little to the right as he swings): 1 from the idle he draws the near fist back; 2 the fist cocked high beside his body; 3 THE RELEASE (the hit lands here): he slams the fist forward to the right at chest height, the arm stretched; 4 holding the punch; 5 swinging both arms back out; 6 back toward the idle.` |
| `blitzcrank_skill.png`（Q 机械飞爪） | 8 帧：60 60 70 80 120 120 80 80 | 第 4 帧（tick 11） | 4 列 × 2 行，4096×1792 | 第 97 行 | `ROCKET GRAB, 8 frames as in the THIRD image: 1-2 he draws the near arm back; 3 he thrusts it forward to the right, the fist still on; 4 THE RELEASE (the hand flies off here): the arm stretched straight out to the right at shoulder height and the HAND GONE - the arm ends in a dark hexagonal wrist socket (the flying hand and its chain are a separate effect, do not draw them); 5-6 holding the arm out with the empty socket; 7 the hand back on the arm, the arm lowering; 8 back toward the idle.` |
| `blitzcrank_q_pull.png`（Q 拉人（手飞出去时的拉拽姿势）） | 3 × 100 | — | 3 列 × 1 行，3072×896 | 第 97 行 | `ROCKET GRAB, THE PULL, 3 frames, a loop (played while a hooked enemy is dragged in): the arm stretched straight out to the right with the empty hexagonal wrist socket, as frame 5 of ROCKET GRAB, the body leaning back a little as if hauling a heavy chain, rocking slightly from frame to frame; no hand.` |
| `blitzcrank_skill2.png`（E 能量铁拳（上勾拳）） | 7 帧：70 70 60 60 90 100 90 | 第 4 帧（tick 12） | 4 列 × 2 行，4096×1792，最后 1 格空 | 第 97 行 | `POWER FIST, 7 frames as in the THIRD image: 1-2 he crouches and swings the near fist down and back; 3 the low wind-up, the fist near the ground behind him; 4 THE RELEASE (the hit lands here): a huge UPPERCUT - the fist sweeps up in front of him to the right, at head height; 5 the fist high above his head, the arm straight up, the body stretched; 6-7 back toward the idle. Draw no glow or sparks: they are effects.` |
| `blitzcrank_ult.png`（R 静电力场） | 7 帧：70 70 70 80 90 100 100 | 第 6 帧（tick 23） | 4 列 × 2 行，4096×1792，最后 1 格空 | 第 97 行 | `STATIC FIELD, 7 frames as in the THIRD image: 1-3 he hunches and pulls both huge arms in, the fists crossing in front of the chest port; 4-5 charging: crouched low, both fists raised in front of him, the body tense; 6 THE RELEASE (the field bursts here): he throws both arms wide open to the sides, the chest port pushed forward; 7 back toward the idle. Draw no lightning: it is an effect.` |
| `blitzcrank_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，2048×896 | 第 97 行 | `HIT, 2 frames: 1 jolted back by a blow, the body tilted back, the eyes dimmed (their white centre squares turned to the pink); 2 recovering toward the idle.` |
| `blitzcrank_dead.png`（死亡） | 8 帧：100 100 100 110 120 130 150 500 | — | 4 列 × 2 行，4096×1792 | 第 97 行 | `DEATH, 8 frames as in the THIRD image: 1 struck, sputtering; 2-4 the arms flail and he sags, the head drooping; 5-6 he topples over backwards; 7-8 lying on his back on the ground line, the huge arms spread out to both sides, the eyes dark (the eye colours gone: dark sockets only). Frames 7-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、同一行；
- [ ] 眼睛的颜色只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 拳头至少 8×8、手臂至少 4 格粗，分得清肩块—前臂—拳头；Q 第 4–6 帧和 q_pull 出手的手臂末端是空腕口；每帧整个人连成一块；
- [ ] 脚底线以下没有任何像素（只有死亡躺倒的帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替、颜色和待机一样，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `blitzcrank_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛颜色只在眼睛上、每帧连成一块、拳头和手臂粗细、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`blitzcrank_cells.json` 用包里这份，`blitzcrank_idle.png` 用包里已做好的那张。
- `import_native.py --hero blitzcrank`：ORDER 待机一张图 + BOB 呼吸（分界线选在腰下，不切过拳头），EYES，补描边（COMPLETE），NECK，走路 STEP 起伏（照英雄联盟落脚那帧最低、之后最高）。
- 按出手帧核对技能数据的时机（普攻 tick 8、Q 出手 tick 11、E tick 12、R 爆发 tick 23），量飞爪的出手高度（y_offset）、特效挂点和头像截取点、选人卡片 banpick_center，重跑模拟，做预览 GIF。
