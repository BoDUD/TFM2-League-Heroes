# 青钢影 PPU 1.5：8 个动作只画两条腿（给 Codex 的提示词）

> 青钢影的新设计图（`refs/design.png`，PPU 1.5，69 格高）已经定了。动作里的头、身体、手臂我照英雄联盟的骨骼摆好了，但她的动作几乎都是用腿：踢腿、飞踢、扫腿、跃起、横飞。设计的腿是硬的，我这边没法弯，所以**请只画两条腿**。
> - **8 张模板**（`templates/<动作>.png`，每张 1536×1024、4×2 排、纯绿 #00FF00 底、每格 6 px）：每一帧里身体和手臂已经摆好，**腿的位置用两根引导线标出来**：**红线 = 近侧腿（画面里在前）**，**蓝线 = 远侧腿（在后）**；每根线从髋部到膝盖（小圆圈）是大腿，从膝盖往下是刀刃，长度就是设计腿的长度。
> - **请沿着引导线画出设计的腿**（照 `refs/design.png`、`refs/design_legs.png`）：深蓝大腿带金色饰线，金色护膝，膝盖以下是银白发蓝的长刀刃，刀尖是尖的。**每一帧的腿和设计一样长、一样粗**（大腿约 6–7 格宽，刀刃约 4 格宽、18 格长），不许变细、变粗、变短、变长；膝盖照引导线弯。画完后**红线、蓝线都不能留下**。
> - 近侧腿颜色亮、画在前面（会挡住远侧腿和身体）；远侧腿暗一档、画在后面。
> - **身体、头、手臂一格都不要改**，地面线、帧号、绿底都保持原样，图的大小和每帧的位置不变，像素格对齐模板的 6 px 网格。
> - 参考 `refs/lol_<动作>.png`（英雄联盟里同一个动作的每一帧，顺序一样）看腿是怎么踢、怎么弯的。
> - 不要特效、影子、文字；不要模糊、渐变、半透明边。
> - 交付：`outputs/camille-legs/<动作>.png`（8 张，文件名和模板一样）；原始生成图原样放进 `outputs/camille-legs/raw/`；`generation-prompts.txt`；**最后**写 `outputs/camille-legs/HANDOFF.md`，再打包成 `outputs/camille_legs_done.zip`。

## 文件（在压缩包 `camille_legs_pack.zip` 里）

| 文件 | 内容 |
|---|---|
| `templates/run.png` 等 8 张 | 移动、普攻、Q 第一踢、Q 第二踢、W、E 射钩、E 冲刺落地、R：身体摆好、腿是引导线 |
| `refs/design.png` | 定稿的设计（8 倍，一格 = 一个像素）：腿的样子 |
| `refs/design_legs.png` | 设计的腿部特写（16 倍，带格子）：腿的粗细和长度 |
| `refs/lol_<动作>.png` | 英雄联盟里同一动作的每一帧：腿怎么动 |

## 提示词（每张模板一次，附上模板、design.png、design_legs.png 和同名的 lol_ 图）

```text
Four attached images. Image 1 is THE TEMPLATE: a sheet of animation frames of a pixel-art character (4 frames per row, 2 rows, flat #00FF00 background, every square 6 px). In every frame her head, body and arms are finished and correct, but her two LEGS are missing: each leg is marked by a guide line - RED for the NEAR leg (in front), BLUE for the FAR leg (behind); from the hip to the small circle is the thigh, from the circle (the knee) on is the blade. Image 2 is the character's approved design (8x, every square one pixel): THE LEGS TO DRAW - dark navy thighs with thin gold lines, gold knee caps, and below the knees long silver-white steel BLADES with a blue tint and a sharp tip (she has blades instead of feet). Image 3 is a close-up of those legs (16x, with the grid): their exact widths and lengths. Image 4 shows the same action in the original 3D game, frame for frame: how the legs kick, bend and swing.
Draw ONLY THE TWO LEGS in every frame of image 1, along the guide lines, and output the same image with nothing else changed:
1. Each leg follows its guide: the thigh from the hip to the knee circle, the blade from the knee along the rest of the line. Every leg in every frame has the design's LENGTH and WIDTHS (thigh about 6-7 squares wide, blade about 4 squares wide and 18 long) - never thinner, thicker, shorter or longer.
2. The NEAR (red) leg is a step lighter and drawn in front of the far leg and of the body; the FAR (blue) leg is a step darker and behind. No red or blue guide line may remain.
3. Do not change anything else: the head, body, arms, the ground line, the frame numbers, the flat #00FF00 background, the canvas size and every frame's position stay exactly as in image 1; keep its 6 px pixel grid.
4. Pixel art like the design: a 1-square near-black outline, flat shades, hard edges; no blur, no gradients, no anti-aliasing, no semi-transparent edges, no effects, no shadow, no text.
```

## 交回前请检查

- 8 张都在，文件名和模板一样，1536×1024，帧的位置、地面线、帧号、绿底不变，6 px 网格对齐。
- 身体、头、手臂没被改。
- 每帧两条腿都沿引导线，长度和粗细和设计一样；红线、蓝线一点不剩。
- 近侧腿亮、在前；远侧腿暗、在后。
- 最后写 `HANDOFF.md`，再打包成 `outputs/camille_legs_done.zip`。

## Claude 收到后

- `tools/art/import_camille_legs.py` 按模板的格子读回（每帧找网格相位，每格取中间的中值，颜色归到设计腿上的颜色），只取模板里身体以外的格子当腿，贴回 `rig_camille_hd.py` 摆好的上身下面；逐帧量腿的宽度、长度（codex-legs-deform：甲片大小每帧变 = 变形）。
