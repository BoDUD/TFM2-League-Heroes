# 布里茨 Q「机械飞爪」重画：爪子从手臂飞出去勾人（给 Codex 的提示词）

> 用户：「要的是和联盟一样 从手臂飞出去的爪子勾人」。现在游戏里的问题：手臂水平举在肩高，可是飞出去的爪子在手臂下面 5 格的线上飞、样子是一只握紧的拳头，拉人时钢缆也连不到手臂上。这一轮**只重画两件事**：Q 的出手动作（手臂对准爪子的飞行线）和飞出去的爪子本身。其余全部不动。
> - 交回：`blitzcrank_skill.png`（8 帧，排版和 `now/blitzcrank_skill.png` 完全一样）、`blitzcrank_q_pull.png`（3 帧，同 `now/blitzcrank_q_pull.png`）、爪子三件（`logical/` 原尺寸 + 8 倍预览）、`manifest.json`、`HANDOFF.md`。打成 `blitzcrank_q_redo_done.zip` 放在 outputs 里。

## 游戏怎么画这一招（位置都是游戏像素，以站位点为原点，右正、上负）

站位点就是 `guide/` 图里每格的**蓝十字**（`blitzcrank_cells.json` 的 pivot），鞋底在它下面 11 格。

1. **飞出去**：爪子从站位点**正上方 16.5 格**出发，沿一条直线飞到 (78, 0)——往右、每走 78 格往下降 16.5 格（约向下 12°）。`guide/q_skill_guide.png` 里的**红线**就是这条线。爪子的画面中心永远在红线上，游戏会把爪子的图转到飞行方向。所以**出手那条手臂必须顺着红线往前伸**：手臂从肩膀沿红线伸出，空腕口的中心正好在红线上的 **(24, −11)**（绿圈）。这样爪子就是从腕口正中飞出去的。
2. **拉回来**：抓住人以后，爪子带着人沿一条直线飞回**站位点**（游戏规定，改不了）。`guide/q_pull_guide.png` 里的三条**橙线**是在 35、45、60 格外抓到人时爪子回来的路线。所以**拉人的那只手臂朝橙线伸出**，腕口在 **(30, −5)**（绿圈），比出手时低一点：他抓住后往下、往回拽。钢链从腕口沿橙线连到爪子，由 Claude 按距离逐帧画。
3. 爪子出现、钢链、拉人的画面都由 Claude 拼。你画**身体动作**和**爪子零件**。

## 任务一：重画 Q 的身体动作

只改**出手的那条手臂**（右边、远侧那条，现在伸出去的就是它），头、身体、另一只手臂、腿脚逐格保持 `now/` 里的样子（头已经按用户要求右移过 2 格，不要动）。

| 文件 | 帧 | 要画的 |
|---|---|---|
| `blitzcrank_skill.png` | 1、2、8 | **原样复制** `now/blitzcrank_skill.png` 的这三帧 |
| | 3 | 蓄力：手臂已经顺着红线往前伸，**爪子还装在手上**（张开的机械爪，和任务二的爪子同样子），准备发射 |
| | 4 | **发射**（游戏在这一帧放出爪子）：手臂顺着红线伸直，末端是**空的深色六角形腕口**，腕口中心在绿圈 (24, −11)；腕口里冒一小股白色蒸汽可以画（1–3 格） |
| | 5、6 | 保持发射姿势（腕口空着），身体可以有一点后坐 |
| | 7 | 收回：手臂往回收，爪子已经回到手上 |
| `blitzcrank_q_pull.png` | 1–3 | **拉人**（3 帧循环，抓住人后一直播）：手臂朝橙线方向伸出，**空腕口**中心在绿圈 (30, −5)，身体往后仰、用力拽；3 帧之间手臂和身体有 1–2 格的来回拉扯 |

- 手臂的样子照造型图（肩块—前臂—腕口，金色方块护甲、深色关节），至少 4 格粗，和身体连成一块；伸直的手臂长度和现在差不多（腕口离肩 18–22 格）。
- 参考英雄联盟的 Q 动作 `refs/lol_pose_q.png`：他侧身把手臂对准目标打出去，手飞走后手臂末端是空腕口。
- 每帧整个人连成一块；脚底线以下什么都不能有；只用造型图的 16 种颜色；每个像素一个 8×8 方块。

## 任务二：重画飞出去的爪子

现在的爪子是一只握紧的拳头（`now/q_hand_now_8x.png`），不像英雄联盟。要的是英雄联盟那只**张开的金色机械爪**：手掌朝前、四根粗粗的方块手指张开像要抓东西，钢色指节，手腕后面是深色六角形的腕口接头，接头后面一小股白色蒸汽（火箭推进）。

| 文件 | 内容 | 大小（原尺寸） |
|---|---|---|
| `logical/blitzcrank_fx_q_claw_open_1x.png` | 飞行中：**张开的爪子朝右**（手指在右、腕口在左），2 帧（蒸汽一闪一闪），格子 16×14，每帧爪子中心在格子中心 (8, 7)，腕口贴着左边（x=1–3） | 32×14 |
| `logical/blitzcrank_fx_q_claw_closed_1x.png` | 抓住人：**合拢的爪子朝右**（手指扣起来抓住东西的样子），2 帧，同样的格子和位置 | 32×14 |
| `logical/blitzcrank_fx_q_chain_1x.png` | 一节**钢链**，横着排，左右首尾能无缝接上：钢色链环（亮钢、中钢、暗钢 + 近黑描边），每节 4 格 | 8×3 |

- 颜色只用造型图的金色和钢色（#FDDC36、#F9AF07、#DD8702、#BC6802、#984B01、#672D01、#E2EBFC、#BFCDE0、#A2AECC、#67718F、#454759、#373E56）和描边 #170F1D；蒸汽用 #FFFFFF、#E8ECF0、#C8D0D8、#9AA4B0。爪子是"东西"，要有 1 格近黑描边。
- 爪子上下大致对称（游戏向左扔时会把图上下翻转），透明底，透明度只有 0 和 255。

## 提示词

### 任务一（身体动作，每张附四张图：`design/blitzcrank_design.png`、`now/blitzcrank_<动作>.png`、参考线图（出手用 `guide/q_skill_guide.png`，拉人用 `guide/q_pull_guide.png`）、`refs/lol_pose_q.png`）

```text
Four attached images. FIRST: the approved pixel-art design of this character at 8x (every pixel an 8x8 block) - its colors, head, eyes, smokestacks, chest port, arms and pixel style are the standard. SECOND: the current frames of this animation at 8x in a grid of cells - keep everything in them (the head, the body, the other arm, the legs and feet, each frame's place in its cell) and redraw ONLY the throwing arm (the far arm, on the right, the one stretched forward). THIRD: the same frames with guides: the blue cross is the standing point of each frame; in the throw frames a RED LINE is the exact path the flying claw takes - from 16.5 squares straight above the standing point, going right and slightly down (12 degrees); a GREEN CIRCLE marks where the empty wrist socket must be. FOURTH: the original 3D animation for the motion.
The character: a huge top-heavy steam robot: a round gold-yellow boiler body with a steel-ringed chest port, a small gold dome head with two pink-white eyes in a steel collar, two short steel smokestacks, black hoses over the shoulders, enormous blocky gold arms (shoulder block, forearm, giant hand), short dark piston legs and big flat gold feet.
Task: [task]
The arm is the FIRST image's armor (gold blocks, dark joints), at least 4 squares thick, joined to the shoulder, the whole figure one connected piece. Copy every other pixel of the SECOND image unchanged. Same pixel size, every pixel a crisp 8x8 square on one grid, no anti-aliasing, no blur, only the 16 colors of the FIRST image: #170F1D #292536 #672D01 #373E56 #984B01 #454759 #BC6802 #DD8702 #67718F #F9AF07 #FDDC36 #A2AECC #BFCDE0 #F3A4D9 #E2EBFC #FFF8FD, one 1-square near-black outline. Nothing below the feet line. Do not draw the flying claw, the chain or any effect in the empty-socket frames.
Layout: exactly the SECOND image's size and cells; transparent background. No guide marks, no grid lines, no labels.
```

`[task]`：
- `blitzcrank_skill.png`：`8 frames. Frames 1, 2 and 8: copy the SECOND image's frames unchanged. Frame 3: the arm already stretched forward along the red line with the open mechanical claw still mounted on it, about to fire. Frame 4: the release - the arm stretched straight along the red line, ending in an EMPTY dark hexagonal wrist socket centered exactly in the green circle (24 squares right of and 11 squares above the standing point), a tiny white steam puff in the socket. Frames 5 and 6: the same pose, the socket still empty, a slight recoil of the body. Frame 7: the arm drawing back with the claw back on it.`
- `blitzcrank_q_pull.png`：`3 frames, a loop played while he reels in a caught enemy: the arm stretched forward toward the orange lines (where the chain will run), ending in an EMPTY dark hexagonal wrist socket centered in the green circle (30 squares right of and 5 squares above the standing point), the body leaning back, pulling hard; between the 3 frames the arm and the body tug back and forth by 1-2 squares.`

### 任务二（爪子，附 `design/blitzcrank_design.png` 和 `now/q_hand_now_8x.png`）

```text
Pixel art game VFX pieces at GAME SIZE (one image pixel = one game pixel), for the flying mechanical claw of a gold steam robot (the FIRST attached image shows the robot; the SECOND shows the current claw, a clenched fist, which is WRONG - replace it). Draw: (a) the OPEN claw in flight, pointing RIGHT: a big gold mechanical hand, palm forward, four thick square gold fingers spread wide like grabbing, steel knuckles, a dark hexagonal wrist socket at its LEFT end and a small white steam puff behind the socket (rocket thrust); 2 frames (the steam flickers); each frame in a 16x14 cell, the claw centered at (8, 7), the wrist socket at the cell's left edge (x 1-3); strip 32x14. (b) the CLOSED claw, holding something, pointing RIGHT: the same hand with the fingers curled shut around a grip; 2 frames; same cells; strip 32x14. (c) one tile of STEEL CHAIN, horizontal, 8x3, two links 4 squares each, light, mid and dark steel with a near-black outline, its left and right ends joining seamlessly when repeated. Colors only: #FDDC36 #F9AF07 #DD8702 #BC6802 #984B01 #672D01 #E2EBFC #BFCDE0 #A2AECC #67718F #454759 #373E56, outline #170F1D, steam #FFFFFF #E8ECF0 #C8D0D8 #9AA4B0. The claws have a 1-square near-black outline and are roughly symmetric top to bottom (the game flips them upside down when thrown left). Transparent background, binary alpha (0 or 255), no anti-aliasing. Also an 8x nearest-neighbour preview of each.
```

## 交回前自查

- `blitzcrank_skill.png` 第 4–6 帧、`blitzcrank_q_pull.png` 3 帧：空腕口中心在绿圈里（误差 1 格以内），手臂顺着红线 / 朝橙线伸出；第 1、2、8 帧和 `now/` 逐像素一样；头、身体、腿脚和 `now/` 一样。
- 每个像素 8×8，一个网格；只用造型图 16 色；每帧一整块；脚底线以下没有像素。
- 爪子三件：原尺寸、透明度只有 0/255、只用规定的颜色；张开的爪子手指朝右、腕口在左。
- `HANDOFF.md` 写清每帧腕口的实际位置（相对站位点）。
