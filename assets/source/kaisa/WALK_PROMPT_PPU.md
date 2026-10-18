# 卡莎 PPU 1.45：走路 8 帧，只重画两条腿（给 Codex 的提示词）

> 卡莎的新造型（附图 2，PPU 1.45，61 格高）已经定了，别的动作我按英雄联盟的骨骼摆好了，只剩走路。附图 1 是我摆的走路 8 帧：位置、节奏、两只脚落在哪里都对，但腿是把设计的腿一行行斜着错开做的，看起来被拉长、变形了。这次请**只重画髋甲以下的两条腿**，让每一帧的腿都和设计的腿一模一样（长度、粗细、甲片、靴子），靠**膝盖和髋部弯曲**迈步，前后交叉换腿。上身一格都不要动。
> - **照附图 1 的版式**：8 帧、4×2 排列，每帧的位置、大小、地面线都不变，背景纯绿 #00FF00，像素格和附图 1 一样（每格 6 px，对齐它的网格）。
> - **髋甲以上原样**：头、头发、发射器、手臂、身体、髋甲，每一帧都照附图 1 原样保留（只有整个人上下起伏，附图 1 已经排好）。
> - **腿照附图 2、3**：大腿约 7 格宽，膝盖 3 格，带爪的高跟靴约 11 格长；深蓝紫甲片、金色细边、亮边都照设计；每一帧两条腿一样长、一样粗，**不许变细、变粗、拉长、缩短**；靴子照设计原样画，只跟着腿移动和稍微转一点。
> - **迈步**：参考附图 4（英雄联盟的跑步：前腿膝盖向前、后腿脚跟向后踢起）和附图 5（之前通过的走路，交叉的节奏）。近侧腿（画面左、颜色亮）在前，画在远侧腿上面；远侧腿暗一档、在后面。照附图 1：第 3 帧近侧脚在前落地、两腿交叉、远侧脚跟踢起；第 7 帧远侧脚在前落地、近侧脚在后；中间帧里着地的脚往后蹬，另一只脚弯膝向前摆过来。**两只脚的前后顺序每个循环换两次**，摆动的那只脚抬起 2–5 格。
> - 不要特效、影子、文字；不要模糊、渐变、半透明边。
> - 交付：`outputs/kaisa-walk/kaisa_walk.png`（1536×1024，和附图 1 同版式，纯绿背景）；原始生成图原样放进 `outputs/kaisa-walk/raw/`；附 `generation-prompts.txt` 写明实际用的提示词；**最后**写 `outputs/kaisa-walk/HANDOFF.md`，再打包成 `outputs/kaisa_walk_done.zip`。

## 附图（在压缩包 `kaisa_walk_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_walk_template.png` | 我摆的走路 8 帧（1536×1024，每格 6 px，纯绿底） | **版式、上身、每只脚落在哪里**；腿要重画 |
| `refs/2_design.png` | 定稿的卡莎设计（8 倍，一格 = 一个像素） | **腿的样子**：甲片、金边、靴子 |
| `refs/3_design_legs.png` | 设计的两条腿特写（16 倍，带格子） | **腿的粗细和长度**，每一帧都照这个 |
| `refs/4_lol_run.png` | 英雄联盟里卡莎的跑步 8 帧（四分之三侧身朝右） | **迈步的姿势**：前腿膝盖向前，后腿脚跟踢起 |
| `refs/5_old_walk.png` | 之前通过的旧走路 8 帧（8 倍，旧造型） | **交叉换腿的节奏**（造型不要照它） |

## 提示词：`kaisa_walk.png`

五张图都附上，顺序同上表。

```text
Five attached images. Image 1 is THE TEMPLATE: an 8-frame walk cycle of a pixel-art character, 4 frames per row, 2 rows, on a flat #00FF00 background, every square 6 px. Its frame positions, sizes, ground lines, its upper body (everything from the hip armour plates up: head, hair, the two weapon pods, arms, torso, hip plates) and where each foot lands are all correct - but its two LEGS were made by sliding the rows of a straight leg sideways, so they look stretched and deformed. Image 2 is the character's approved design (shown 8x, every square one pixel): THE TRUE LEGS. Image 3 is a close-up of those two legs (16x, with the square grid): their exact widths and length. Image 4 is the character's run in the original 3D game, 3/4 view facing right: the POSE of a stride (the front leg's knee forward, the back leg's heel kicked up behind). Image 5 is an earlier approved walk of the same character (an older design, 8x): the RHYTHM of the crossing steps only - do not copy its look.
Redraw ONLY THE TWO LEGS (from under the hip plates down to the soles) in all 8 frames of image 1, and output the same image with nothing else changed:
1. Keep image 1's layout exactly: the same 1536x1024 canvas, the same 8 frame positions, the same ground lines, the same flat #00FF00 background, the same 6 px pixel grid.
2. Keep everything above the legs exactly as image 1 draws it in each frame - do not redraw, move or restyle the head, hair, pods, arms, torso or hip plates.
3. Every leg in every frame is the design's leg (images 2 and 3): the same LENGTH, the same WIDTHS (thigh about 7 squares, knee 3, the clawed high-heeled boot about 11 long), the same dark navy-violet armour plates with thin gold trim and lighter edges, the same boots. Never thinner, thicker, longer or shorter than the design; never stretched or slanted row by row - a leg moves by bending at the hip and the knee, the boot copied from the design and only moved or slightly tilted with the leg.
4. Make it a real walk with crossing steps like images 4 and 5: the NEAR leg (image left, lighter) is drawn in front of the far leg; the FAR leg (image right) is a step darker and behind it. Follow image 1's feet: in frame 3 the near foot lands ahead, in front of the far one, the legs crossed, the far heel kicked up behind; in frame 7 the far foot lands ahead and the near foot is behind; in between, the planted foot pushes back and the other leg swings through with a bent knee, its foot lifted 2-5 squares. The order of the two feet changes twice per cycle.
5. Pixel art matching the design: one 1-square near-black outline, flat shades, hard edges on the 6 px grid; no blur, no gradients, no anti-aliasing, no soft or semi-transparent edges, no effects, no shadow, no text.
```

## 交回前请检查

- 1536×1024，8 帧位置、地面线和附图 1 一样；纯绿 #00FF00 背景；每格 6 px 对齐附图 1 的网格。
- **髋甲以上和附图 1 完全一样**（头、发射器、手臂、身体都没被重画）。
- 每一帧两条腿的长度、粗细、甲片、靴子都和设计一样，没有变细、变粗、拉长；靠弯膝弯髋迈步。
- 近侧腿在前、颜色亮；远侧腿在后、暗一档；第 3 帧近侧脚在前交叉、第 7 帧远侧脚在前；两只脚前后顺序每个循环换两次。
- 最后写 `outputs/kaisa-walk/HANDOFF.md`（列出交付的文件），再打包成 `outputs/kaisa_walk_done.zip`。

## Claude 收到后（给 Claude 看）

- 按附图 1 的 6 px 网格读回每一帧（先量 Codex 实际格子大小），**只取髋甲以下的腿**，贴回 `rig_kaisa_hd.py` 摆好的上身（上身用设计原像素）；逐帧量两条腿的宽度和长度跟设计比（codex-legs-deform：甲片大小每帧变 = 变形），脚前后顺序每循环换两次，再给用户看 GIF。
