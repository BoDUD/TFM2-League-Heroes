# 库奇（英勇投弹手）：高清（PPU）造型——侧面、几个关键姿势、会转的部件（给 Codex 的提示词）

> 用户：「直接用PPU做吧」。库奇不再缩成游戏小图，**直接用用户选的原画第 2 张当高清造型**：我已把它按原画自己的格子读回（`design/corki_front.png`，**146 × 125 格**，48 色，每格 8 px），游戏里用 PPU 4 显示（4 个格子 = 游戏里 1 个像素）。这张就是待机和选人卡片。
> 库奇是**一整架刚性的飞机**：动作由我把整张图平移、上下浮动、换螺旋桨和枪管的转动状态拼出来。**这一轮请你画平移拼不出来的东西**：转到侧面的样子、几个倾斜的姿势、坠毁，以及螺旋桨和枪管的几个转动状态。
> **所有图都画在同一个格子上**：每格 8 × 8 px、一格一个颜色，格子和 `design/corki_front.png` **大小完全一样**（同样的格子大小、同样的高度、同样的颜色和细节）。不要画大了再缩，不要换画风。

## 统一规则（每张都一样）

- 画布 **1536 × 1024 横版、透明背景、8 px 一格（192 列 × 128 行）**，和 `design/empty_grid.png` 一样；`design/corki_front_grid.png` 是正面造型放在这个格子上的样子：**螺旋桨顶在第 1 行（绿线），炸弹底在第 125 行（红线上沿）**。
- **颜色只用 `design/corki_palette.png` 里的 48 色**（实在要加，最多再加 6 色，写进 HANDOFF）。一圈 1 格近黑描边，里面少用黑；不要抖动、渐变、碎点、半透明、抗锯齿。
- **飞行员的头（头盔、尖刺、红羽毛、两片黄色护目镜、粉鼻子、白八字胡）在每张图里都和正面造型一模一样**——同一张 3/4 脸，逐格照抄 `design/corki_front.png` 第 20–55 行、第 64–120 列那一块；我导入时也会把正面的头贴回去，所以头的位置和大小要对得上（头不转，只有飞机转）。
- 没有特效：不画枪口火光、喷口火焰、螺旋桨模糊圈、烟、爆炸（特效第 3 步再画）。不要地面、影子、文字、网格线。
- 每张交大图（8 px 一格）和 `_1x.png`（1 像素 1 格，必须和大图逐格一致）。

## 要画的图（`outputs/corki-ppu/`）

| 文件 | 内容 | 用在 |
|---|---|---|
| `corki-side.png` | **侧面朝右、平飞**：整架飞机转向画面右边，机头、牙和格林机枪朝正右，机身侧面完整露出，近侧机翼在前、远侧机翼大半被机身挡住，两副螺旋桨在机舱后上方（侧面看桨叶是横着的一条），推进器在画面左边，两个炸弹在机身下面一前一后。高度和正面一样：螺旋桨顶第 1 行、炸弹底第 125 行。参考 `refs/2_league_side.png` 第一帧。 | **除待机外所有动作的底子** |
| `corki-side-lean.png` | 同一架侧面飞机**机头朝下倾约 12°**（向前飞）：只是整架转了一点，零件不变形；飞行员的头照旧是正面那张脸（不跟着倾斜）。参考 `refs/3_league_lean.png`。 | 移动、W 俯冲 |
| `corki-side-up.png` | 同一架侧面飞机**机头朝上仰约 10°**（被打退 / 扔炸弹时往上一抬）；头照旧。 | 受击、Q |
| `corki-dead-fall.png` | **坠落**：侧面飞机机头朝下栽约 35°，一副螺旋桨停了歪着，飞行员的护目镜歪到一边、八字胡乱了（这一张头可以不同）。参考 `refs/4_league_death.png` 第 2–3 帧。 | 死亡第 1 段 |
| `corki-dead-crash.png` | **坠毁在地上**：飞机侧躺在地上（机腹着地、稍微歪着），一副螺旋桨断了掉在旁边，炸弹没了，飞行员瘫在机舱里头晕；整体矮下去（约 60–70 行高），**最低处在第 125 行**。参考 `refs/4_league_death.png` 最后一帧的落地。 | 死亡最后 |
| `corki-rotors.png` | **螺旋桨的转动状态**（只画螺旋桨 + 中间的轴心，杆子从轴心下面截掉）：正面造型里左、右两副各画 **4 个状态**——状态 0 就是正面造型里画的样子（逐格照抄），状态 1、2、3 绕轴心依次转约 22°、45°、67°；侧面图里的两副各画 **4 个状态**（侧面看是一条横杆：桨叶转到不同角度时这条杆的长短、亮暗不同）。每个状态放在一个格子里排成网格，**轴心在每格正中间**，格与格之间留 4 格空。 | 待机、移动、所有动作里螺旋桨转起来 |
| `corki-gun.png` | **格林机枪的转动状态**：正面造型里的枪口 3 个状态（状态 0 = 造型里那样，1、2 = 枪管绕枪轴转 1/3 格、2/3 格），侧面图里的枪管 3 个状态（枪管上的亮线位置不同）；排法同上，枪轴中心在每格正中。 | 普攻、E 扫射 |

## 提示词

一次附图：`design/corki_front.png`、`design/corki_palette.png`、`design/corki_front_grid.png`、`refs/2_league_side.png`、`refs/1_picture.png`（能多附时再附 `refs/3`、`refs/4`、`refs/5`）。每张图单独生成，**每张都附 `corki_front.png`**。

```text
The attached sprite (corki_front.png: 146 x 125 squares, 8 px a square, 48 colours in corki_palette.png) is the final high-resolution pixel-art design of this character: Corki, a yordle pilot in a little steel-blue gyrocopter shaped like an open-mouthed monster head (jagged teeth, a four-barrel gatling gun in its mouth, two gold lamp eyes, a brown leather cockpit pad, two wooden four-bladed propellers on steel poles, swept steel wings, red-nozzled thrusters with brass pipes, two yellow-and-red checkered bombs underneath). The pilot: brown leather flying helmet with a silver spike and a red plume, round goggles with glowing yellow lenses, pink nose, a huge white handlebar moustache, red scarf, olive suit, brown gloves.
Draw <WHAT> on a 1536x1024 transparent canvas on the SAME 8-px grid (192 x 128 squares): every square one flat colour from the design's palette, the same square size, the same height (the propellers' top on square row 1, the bottom of the bombs on square row 125), the same parts, colours and level of detail as the design - as if the same artist had drawn the same sprite from another angle. The pilot's head is copied square for square from the design (rows 20-55, columns 64-120 of corki_front.png): the same 3/4 face, not turned. A 1-square near-black outline, little black inside, no dithering, no gradients, no anti-aliasing, no semi-transparency, no effects (no muzzle flash, no flames, no smoke, no propeller blur), no ground, no shadow, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>` 依次换成：

- `corki-side.png`：`the whole craft turned SIDE-ON facing the image right, flying level: the nose, the teeth and the gatling gun pointing straight right, the flank fully showing, the near wing in front and the far wing mostly hidden, the two propellers behind and above the cockpit seen edge-on as flat bars, the thrusters on the image left, the two bombs under the hull one ahead of the other (see the side-on render of his 3D model)`
- `corki-side-lean.png`：`the same side-on craft as corki-side.png tilted NOSE DOWN by about 12 degrees, flying forward - the whole craft turned as one rigid piece, no part bent; the pilot's head stays the design's upright face`
- `corki-side-up.png`：`the same side-on craft tilted NOSE UP by about 10 degrees (recoiling) - the whole craft turned as one rigid piece; the pilot's head stays the design's upright face`
- `corki-dead-fall.png`：`the same side-on craft falling NOSE DOWN at about 35 degrees, one propeller stopped and crooked, the pilot's goggles knocked askew and the moustache ruffled (here the face may differ)`
- `corki-dead-crash.png`：`the craft CRASHED on the ground: lying on its belly, slightly tilted, one propeller broken off lying beside it, no bombs, the pilot slumped dizzy in the cockpit; about 60-70 squares tall, its lowest square on row 125`
- `corki-rotors.png`：`only the PROPELLERS with their hubs (the poles cut off under the hub): for each of the design's two front-view propellers, 4 turn states - state 0 copied square for square from the design, states 1-3 turned about the hub by about 22, 45 and 67 degrees; then for each of the side view's two propellers 4 turn states seen edge-on (the bar's length and shading changing as the blades turn). Each state in its own cell of a grid, the hub at the cell's centre, 4 empty squares between cells`
- `corki-gun.png`：`only the GATLING GUN's muzzle: 3 spin states of the design's front-view muzzle (state 0 copied from the design, states 1-2 the barrels turned a third and two thirds of the way to the next barrel), then 3 spin states of the side view's barrels (the bright stripes moving along); each state in its own cell, the gun's axis at the cell's centre, 4 empty squares between cells`

## 交付

- `outputs/corki-ppu/` 里上表 7 张（大图 + `_1x.png`），`generation-prompts.txt`，生图原稿放 `raw/`；**最后写 `HANDOFF.md`**（每张的格子大小、高度、色数、哪里没做到）；最好再打成 `corki_ppu_done.zip`。

## 交回前自查

- [ ] 每张都在 8 px 格子上，每格一个颜色，透明度只有 0/255，颜色来自 48 色色板（新增不超过 6 色）；
- [ ] 侧面三张（平飞、低头、抬头）高度和正面造型一样（螺旋桨顶第 1 行、炸弹底第 125 行左右），零件、颜色、细节一样，只是转了角度；
- [ ] 飞行员的头在侧面三张里和正面造型逐格一样（同一张 3/4 脸，不跟着飞机转）；
- [ ] 坠落、坠毁两张：坠毁的最低处在第 125 行；
- [ ] 螺旋桨、机枪：状态 0 和造型里逐格一样，轴心在每格正中；
- [ ] 没有特效、地面、影子；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读 `_1x.png`（核对和大图逐格一致、色板），把正面的头逐格贴回侧面三张（一张脸贯穿所有帧），一圈描边整理；侧面三张和正面放在一起给用户看。
- `tools/art/rig_corki_hd.py`：每个动作的帧都由这些图整块平移拼成——待机 = 正面造型上下浮动 1–2 个游戏像素（4–8 格）+ 螺旋桨换状态；移动 = 低头侧面 + 浮动 + 螺旋桨；普攻 / E = 侧面 + 后坐 1–2 格 + 枪管换状态；Q / 受击 = 抬头侧面；W = 低头侧面；R = 侧面 + 后坐；死亡 = 坠落 → 坠毁。不旋转、不拉伸、不重画零件；炸弹底离地 3 个游戏像素（悬停），地面加一块小影子。1 倍帧由高清帧按 4 倍降采样做兜底（没有 league.dll 时用）。
