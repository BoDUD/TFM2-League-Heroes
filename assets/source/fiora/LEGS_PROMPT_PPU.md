# 剑姬 PPU 1.5：5 个动作只画两条腿 + 一张 45° 护手（给 Codex 的提示词）

> 剑姬的新设计图（`refs/design.png`，PPU 1.5，60 格高）已经定了。动作里的头、身体、持剑的手臂我照英雄联盟的骨骼摆好了，但移动、普攻、强化普攻、Q、W 都要迈步、弓步、下蹲，设计的腿是硬的，我这边没法弯，所以**请只画两条腿**。
> - **5 张模板**（`templates/<动作>.png`，每张 1536×1024、4×2 排、纯绿 #00FF00 底、每格 6 px）：每一帧里身体和手臂已经摆好，**腿的位置用两根引导线标出来**：**红线 = 前面那条腿（画面右边、离镜头近）**，**蓝线 = 后面那条腿（画面左边、在后）**；每根线从髋部到膝盖（小圆圈）是大腿，从膝盖往下是小腿和靴子，长度就是设计腿的长度。
> - **请沿着引导线画出设计的腿**（照 `refs/design.png`、`refs/design_legs.png`）：深青色紧身裤，侧面一条金色细线；金色护膝；深青色高跟靴，金色鞋尖和鞋跟。**每一帧的腿和设计一样长、一样粗**（大腿约 6 格宽，小腿约 5 格宽，髋到脚底约 24 格），不许变细、变粗、变短、变长；膝盖照引导线弯，脚底照引导线落地。画完后**红线、蓝线都不能留下**。
> - 前面的腿（红线）颜色亮、画在前面（会挡住后面的腿）；后面的腿（蓝线）暗一档、画在后面，可以被披风挡住一部分。
> - **身体、头、手臂、披风一格都不要改**，地面线、帧号、绿底都保持原样，图的大小和每帧的位置不变，像素格对齐模板的 6 px 网格。剑身我这边自己画，模板里没有剑身，**不要画剑身**。
> - **例外：`skill.png` 的第 2、3 帧（帧号旁写着 WHOLE FIGURE）是 Q 的突进**：英雄联盟里她压低身子几乎贴地往前冲（看 `refs/lol_skill.png` 第 2、3 帧）。这两帧请**照英雄联盟的姿势把整个人重画**：同样的服装、颜色、头和像素大小（照 `refs/design.png`），身体前倾压低、后腿蹬直、前腿弓，持剑的手臂往后拖；剑身不画。人还在这一帧的格子里，脚底贴着地面线。
> - 参考 `refs/lol_<动作>.png`（英雄联盟里同一个动作的每一帧，顺序一样）看腿是怎么迈、怎么弯的。
> - 不要特效、影子、文字；不要模糊、渐变、半透明边。
> - **另外一张：45° 的护手**（`templates/guard45.png`）：左上角是设计里的手套、金色护手和一小段剑身（16 倍，一格 16 px）。请在右边照它画**同一个手套和护手，整体转 45°（剑身方向朝右上）**：手套中心放在蓝色圆圈上，剑身沿着红线往右上画 **8 格**（白色一边在上、蓝灰一边在下，每格 16 px，两格宽），格子大小和左边完全一样；左边原图不要动，画完红线和蓝圈不能留下。
> - 交付：`outputs/fiora-legs/<动作>.png`（5 张）和 `outputs/fiora-legs/guard45.png`，文件名和模板一样；原始生成图原样放进 `outputs/fiora-legs/raw/`；`generation-prompts.txt`；**最后**写 `outputs/fiora-legs/HANDOFF.md`，再打包成 `outputs/fiora_legs_done.zip`。

## 文件（在压缩包 `fiora_legs_pack.zip` 里）

| 文件 | 内容 |
|---|---|
| `templates/run.png` 等 5 张 | 移动、普攻、强化普攻（E）、Q、W：身体摆好、腿是引导线（Q 的第 2、3 帧画整个人） |
| `templates/guard45.png` | 手套 + 护手：左边原样，右边画转 45° 的 |
| `refs/design.png` | 定稿的设计（8 倍，一格 = 一个像素）：腿的样子、整个人的样子 |
| `refs/design_legs.png` | 设计的腿部特写（16 倍，带格子）：腿的粗细和长度 |
| `refs/guard.png` | 手套和护手特写（16 倍，带格子） |
| `refs/lol_<动作>.png` | 英雄联盟里同一动作的每一帧：腿怎么动 |

## 提示词（每张动作模板一次，附上模板、design.png、design_legs.png 和同名的 lol_ 图）

```text
Four attached images. Image 1 is THE TEMPLATE: a sheet of animation frames of a pixel-art character (4 frames per row, 2 rows, flat #00FF00 background, every square 6 px). In every frame her head, body, cape and sword arm are finished and correct, but her two LEGS are missing: each leg is marked by a guide line - RED for the FRONT leg (nearer the viewer), BLUE for the BACK leg; from the hip to the small circle is the thigh, from the circle (the knee) on is the shin and the boot, ending at the sole. Image 2 is the character's approved design (8x, every square one pixel): THE LEGS TO DRAW - dark teal tights with one thin gold line down the side, gold knee guards, dark teal high-heeled boots with gold toes and heels. Image 3 is a close-up of those legs (16x, with the grid): their exact widths and lengths. Image 4 shows the same action in the original 3D game, frame for frame: how the legs step, lunge and bend.
Draw ONLY THE TWO LEGS in every frame of image 1, along the guide lines, and output the same image with nothing else changed:
1. Each leg follows its guide: the thigh from the hip to the knee circle, the shin and boot from the knee along the rest of the line, the sole at the line's end. Every leg in every frame has the design's LENGTH and WIDTHS (thigh about 6 squares wide, shin about 5, hip to sole about 24 squares) - never thinner, thicker, shorter or longer.
2. The FRONT (red) leg is a step lighter and drawn in front of the back leg; the BACK (blue) leg is a step darker and behind, the cape may cover part of it. No red or blue guide line may remain.
3. Do not change anything else: the head, body, cape, arm, the ground line, the frame numbers, the flat #00FF00 background, the canvas size and every frame's position stay exactly as in image 1; keep its 6 px pixel grid. Do not draw a sword blade.
4. Pixel art like the design: a 1-square near-black outline, flat shades, hard edges; no blur, no gradients, no anti-aliasing, no semi-transparent edges, no effects, no shadow, no text.
```

`skill.png` 加上这一段：

```text
EXCEPTION - frames 2 and 3 of this sheet (marked WHOLE FIGURE) are a low forward dash: redraw THE WHOLE CHARACTER in those two frames in the pose of image 4's frames 2 and 3 - the body leaning far forward and low, close to the ground, the back leg stretched straight behind, the front leg bent under her, the sword arm trailing back - with exactly the design's costume, colours, head and square size (image 2), no sword blade; she stays inside her frame, her lowest foot on the ground line.
```

## 提示词：`guard45.png`（附上 guard45.png 和 refs/guard.png）

```text
Two attached images. Image 2 is a close-up of a pixel-art sword hand (16 px a square, with the grid): a dark glove holding a gold cup hilt set with a blue gem, and the first squares of a straight two-colour blade (white edge on top, blue-grey under it). Image 1 is the canvas: the same picture at the top left, and on the right a red guide line going up-right at exactly 45 degrees with a blue circle at its lower end. Draw, on the right, THE SAME glove and hilt TURNED 45 DEGREES so the blade points up-right: the glove's middle on the blue circle, the blade along the red line for 8 squares (two squares wide, the white edge on the upper-left side, the blue-grey on the lower-right). Same 16 px squares, same colours and details as image 2, 1-square near-black outline round the glove and hilt (none round the blade), hard pixel edges, no blur, no anti-aliasing. Leave the top-left picture and the green background unchanged; no red line or blue circle may remain.
```

## 交回前请检查

- 6 张都在（5 个动作 + guard45），文件名和模板一样，1536×1024，帧的位置、地面线、帧号、绿底不变，6 px 网格对齐。
- 身体、头、手臂、披风没被改（Q 的第 2、3 帧除外，那两帧是整个人重画）；没有画剑身。
- 每帧两条腿都沿引导线，长度和粗细和设计一样；红线、蓝线一点不剩。
- 前腿亮、在前；后腿暗、在后。
- guard45：手套和护手和原图一样大、一样的格子，剑身朝右上 45°。
- 最后写 `HANDOFF.md`，再打包成 `outputs/fiora_legs_done.zip`。

## Claude 收到后

- `tools/art/import_fiora_legs.py`（照 `import_camille_legs.py`）按模板的格子读回（每帧找网格相位，每格取中间的中值，颜色归到设计的颜色），只取模板里身体以外的格子当腿，贴回 `rig_fiora_hd.py` 摆好的上身下面；Q 的第 2、3 帧整帧取用；逐帧量腿的宽度、长度（codex-legs-deform：每帧粗细变 = 变形）。guard45 读回成 `hd/guard45.png`，`rig_fiora_hd.py` 的剑就能走 8 个方向（SWORD_STEP 45）。
