# 萨科：重画几帧的腿（动作条第 1 轮修改，给 Codex 的提示词）

> 上次交回的动作条（`shaco-strips-clean-v1`）已经导入游戏，头、上身、手臂、匕首、每帧的位置都很好，**这些一点都不要改**。只有腿有两处问题：
> 1. **移动没有换步**：8 帧里近侧的腿（图里左边那条）一直在后面、远侧的腿一直在前面，看起来一直用同一条腿往前蹭。英雄联盟的跑步每半圈换一次腿（见下表），**第 1 帧和第 5 帧的腿不能一样，第 4 帧和第 8 帧也不能一样**。
> 2. **蹲下的帧没有了格子裤**：普攻第 4 帧、背刺第 3–5 帧、毒刃第 4–5 帧、欺诈魔术第 3–4 帧、幻像第 4 帧、死亡第 5–8 帧，大腿画成了红色和深蓝色的斜条，黑白格子的灯笼裤不见了（造型图里格子裤有 44 个深格，这几帧只剩 4–13 个）。英雄联盟里他蹲下、弯腰时格子裤一直看得见（`pose/` 和 `guide/lol_legs_<动作>.png`）。
> - **只重画下表列出的帧里、从腰带往下的两条腿**（灯笼裤、膝盖的金箍、靴子、鞋）；腰带以上（头、帽子、上衣、褶领、护肩、手臂、匕首、上衣的红色下摆）逐格照 `current/shaco_<动作>.png`，每帧在格子里的位置和高低也不变。其他帧原样交回。
> - 两条腿的位置每帧照 `guide/lol_legs_<动作>.png`（英雄联盟同样的帧、同样的格子：**近腿橙色**，**远腿蓝色**，其余灰色）。对比图 `guide/legs_now_vs_lol_<动作>.png`：上排是现在的腿（错），下排是英雄联盟的腿（对）。
> - 交回 `shaco_legs_fix.zip`：改过的 7 张条带（`shaco_run.png`、`shaco_attack.png`、`shaco_attack_q.png`、`shaco_attack_e.png`、`shaco_skill.png`、`shaco_ult.png`、`shaco_dead.png`，放大 8 倍，尺寸和排版不变）、`native/` 里的 1 倍原图、`manifest.json`（每帧的格子矩形、站位点、bbox、两只脚的位置）、`HANDOFF.md`、`generation_prompts.json`。

## 要重画腿的帧

| 文件 | 帧 | 排版（列 × 行，像素） |
|---|---|---|
| `shaco_run.png`（移动） | 1、2、3、4、5、6、7、8 | 4 列 × 2 行，3584×1536 |
| `shaco_attack.png`（普攻） | 4 | 3 列 × 2 行，2688×1536 |
| `shaco_attack_q.png`（Q 后的背刺普攻） | 3、4、5 | 3 列 × 2 行，2688×1536 |
| `shaco_attack_e.png`（E 双面毒刃，掷刀普攻） | 4、5 | 3 列 × 2 行，2688×1536 |
| `shaco_skill.png`（Q 欺诈魔术） | 3、4 | 3 列 × 2 行，2688×1536 |
| `shaco_ult.png`（R 幻像） | 4 | 3 列 × 2 行，2688×1536 |
| `shaco_dead.png`（死亡） | 5、6、7、8 | 4 列 × 2 行，3584×1536 |

## 腿的材质（照 `design/shaco_legs.png`）

- 大腿到膝盖是**黑白格子的灯笼裤**：2×2 一格，深格 `#2F2E40`、浅格 `#D1CBDE`、阴影一侧的浅格 `#AAA3BE`，鼓鼓的；弯腿时格子跟着大腿的方向排，但每格还是 2×2，不碎成单点。
- 膝盖下面一道**金箍**（`#F3BF27`，暗边 `#8A5D25`）；小腿是**深蓝靴子**（`#1D264A`、`#334782`、`#475C75`）前面一排**银色尖刺**（`#D1CBDE`、`#F7F7F8`）；脚是**红色卷尖鞋**（`#FC2D3F`、`#B3112D`、`#9C0D29`），远侧那只鞋尖往上卷。
- 上衣**红色的下摆**只是从腰上垂下来的一片（造型图里斜着盖在近侧大腿上），它不是腿：蹲下时它跟着身体，但下面必须看得见格子裤和两条腿。
- 两条腿用一样的颜色（不要近亮远暗），前后只看谁的描边压在上面：近腿在前，远腿被近腿挡住一部分。腿连在腰上，不能有飘着的碎块。

## 移动的每一帧（最重要）

萨科的跑法是一蹦一蹦的小丑步：近腿撑地的时间长（第 8–5 帧），远腿只在第 6–7 帧落地一下。照 `guide/lol_legs_run.png`：

| 帧 | 近腿（橙） | 远腿（蓝） |
|---|---|---|
| 1 | 着地：在身体正下方，直的，鞋底踩在脚底线上 | 在近腿后面抬起：膝盖弯，脚离地 |
| 2 | 着地：往前斜，脚在身前 | 在身后抬起：膝盖弯，脚离地 |
| 3 | 着地：在身体下面，直的 | 往前摆：从近腿后面经过，膝盖抬到身前——**两个膝盖在这里交错** |
| 4 | 着地：弯膝下蹲（这一帧身体最低），脚在身体左下 | 在身前：膝盖弯着抬起，脚离地 |
| 5 | 往后蹬：斜在身后（图里左边），脚尖还踩着地 | 在身前：膝盖弯，脚离地，准备落地 |
| 6 | 离地：斜在身后，脚尖离地 | 落地：在身前（图里右边）伸直，鞋底踩到脚底线 |
| 7 | 往前摆：膝盖弯着从远腿前面经过——**两个膝盖交错** | 着地：斜在身前，鞋底踩在脚底线上 |
| 8 | 落地：在身体下面，弯膝（这一帧身体最低），鞋底踩到脚底线 | 往后抬起：膝盖弯，脚离地；接回第 1 帧 |

所以：近腿第 8 帧落地、撑到第 5 帧往后蹬；远腿第 3–5 帧在身前、第 6 帧落地、第 7 帧撑地；第 3、7 帧两个膝盖交错。**第 1 帧和第 5 帧的腿不能一样，第 4 帧和第 8 帧也不能一样。** 上半身（腰带以上）照 `current/shaco_run.png` 每帧原样，包括第 4、8 帧身体低 2 格。

## 其他帧（普攻 4、背刺 3–5、毒刃 4–5、欺诈魔术 3–4、幻像 4、死亡 5–8）

- 腿的姿势照 `guide/lol_legs_<动作>.png`：蹲低、两腿分开、膝盖弯，脚踩在脚底线上；腰带的位置照 `current/` 里这一帧（身体放低了几格，腿就弯得更深，不要把腿画短一截）。
- 死亡第 7–8 帧是第 6 帧整个转 90 度躺下：先把第 6 帧的腿修好，再把修好的第 6 帧整体转 90 度、放在原来第 7、8 帧的位置（第 8 帧比第 7 帧低 1 格，照原来）。

## 提示词（每张附三张图：`design/shaco_design.png`、`current/shaco_<动作>.png`、`guide/lol_legs_<动作>.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - his colors, materials and pixel style, 46 squares tall standing; look at his legs: black-and-white checkered pantaloons in 2x2 checks from the belt to the knees, a gold band under each knee, navy boots with a row of silver spikes, curled crimson shoes. SECOND: his current animation strip at 8x - keep EVERYTHING above the belt exactly as drawn there, square for square (the jester hat, the mask, the gold ruff, the spiked pauldrons, the crimson jacket and its hanging front flap, both arms, both daggers, and the place and height of the body in each cell). THIRD: the same frames of the original animation in the same cells, his legs painted apart: the NEAR leg ORANGE (in front, toward the viewer), the FAR leg BLUE (behind), the rest grey - copy the position of both legs in every listed frame from it.
Redraw ONLY the legs (from the belt down) of the frames [frames]; every other frame and everything above the belt stays as in the SECOND image.
[problem]
Draw both legs in the FIRST image's materials: checkered pantaloons with 2x2 checks (#2F2E40 dark squares, #D1CBDE light squares, #AAA3BE on the shaded side) that stay visible in every frame - also when he crouches - a gold band (#F3BF27, #8A5D25) under each knee, navy boots (#1D264A, #334782, #475C75) with silver spikes, curled crimson shoes (#FC2D3F, #B3112D, #9C0D29). The red front flap of the jacket hangs from the belt over the near thigh as in the FIRST image; it is not a leg and never replaces the pantaloons. Both legs in the same colors (no lighter near leg, no darker far leg); the near leg in front, its outline over the far leg; the legs joined to the belt, no loose pieces.
Pixel rules: exactly the FIRST image's pixel size, every pixel one crisp 8x8 square on one 8-px grid, no anti-aliasing, no blur, no semi-transparency, ONLY the FIRST image's 17 colors: #0F0419 #1D264A #2F2E40 #9C0D29 #B3112D #334782 #8A5D25 #475C75 #FC2D3F #03A7E9 #F3BF27 #8AAAC2 #AAA3BE #D1CBDE #FFF2A3 #B8FAFF #F7F7F8. A 1-square near-black outline round the silhouette and each material's own dark shade inside it; no dithering, no noise, no specks.
Feet line: the lowest row of his shoes is square row 81 of each cell; nothing from row 82 down (only the lying death frames 7-8 may dip 2 squares). Layout: exactly like the SECOND image - the same image size and cells, frame N in the same cell; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.
Before finishing, check: everything above the belt identical to the SECOND image in every frame; the checkered pantaloons visible in every listed frame; [check]; only the FIRST image's colors; nothing below the feet line.
```

`[frames]`、`[problem]`、`[check]` 按动作替换：

- **移动**：`[frames]` = `1-8`；`[problem]` = `In the SECOND image the near leg stays behind and the far leg in front in all 8 frames, so he never changes step. His run is a springy jester's skip that changes legs: frame 1 near leg planted straight under him, far leg lifted behind it with the knee bent; 2 near leg planted, slanting forward, far leg lifted behind; 3 near leg planted straight, far leg swinging forward past it, knee lifted in front (the knees pass each other); 4 near leg planted with the knee bent (the body at its lowest), far leg in front with the knee lifted; 5 near leg pushing off behind him (to the left), toe still on the ground, far leg in front ready to land; 6 near leg lifted behind, far leg landing straight in front (to the right), its sole on the feet line; 7 far leg planted slanting in front, near leg swinging forward past it with the knee bent (the knees pass each other); 8 near leg landing under him with the knee bent (the body at its lowest), far leg lifted behind - it flows into frame 1.`；`[check]` = `frames 1 and 5 with different legs, frames 4 and 8 with different legs, the knees crossing in frames 3 and 7, the far leg planted in front in frames 6-7`。
- **普攻、背刺、毒刃、欺诈魔术、幻像**：`[frames]` = 表里的帧号；`[problem]` = `In those frames he crouches and the SECOND image lost his checkered pantaloons: the thighs became red and navy bars. Draw his legs bent as the THIRD image shows - knees bent, feet apart on the feet line - with the checkered pantaloons clearly visible on both thighs.`；`[check]` = `both thighs checkered, both shoes on the feet line`。
- **死亡**：`[frames]` = `5-8`；`[problem]` 同上，再加 `Frames 7 and 8 are frame 6 turned a quarter turn as a whole and laid down (as in the SECOND image): fix frame 6's legs first, then turn the fixed frame 6 for frames 7 and 8, frame 8 one square lower than frame 7 as before.`；`[check]` = `frames 7-8 are the fixed frame 6 turned`。

## 交回前自查

- [ ] 腰带以上和 `current/` 逐格一样（头、上身、手臂、匕首、每帧位置和高低），没列出的帧原样不动；
- [ ] 列出的每一帧两条大腿都是 2×2 的黑白格子，膝盖金箍、深蓝靴子带银刺、红色卷尖鞋都在；上衣的红下摆没有盖掉整条腿；
- [ ] 移动：第 1、5 帧的腿不一样，第 4、8 帧也不一样，第 3、7 帧两个膝盖交错，第 6–7 帧远腿在身前着地；
- [ ] 两条腿颜色一样，近腿在前；腿连在腰上，没有碎块；脚底线以下没有像素（死亡第 7–8 帧最多低 2 格）；
- [ ] 只用造型图色板，严格 8×8 方块，透明度只有 0 和 255；7 张图的尺寸和排版不变。

## Claude 导入时

- 检查腰带以上是否和上次逐格一样、格子裤（深格数）、第 1/5 帧和第 4/8 帧的腿是否不同、脚底线、色板、连通块；放进 `assets/source/native/`，`import_native.py --hero shaco`，做「我们 vs 英雄联盟」的对比 GIF 给用户看。
