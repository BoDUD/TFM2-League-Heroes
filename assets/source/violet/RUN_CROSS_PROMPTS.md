# 蔚奥莱：跑步交叉步重画（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 上一轮的 8 帧跑步，两条腿已经会轮流在前了，谢谢。但用户看了说**「怎么走路看起来没有明显的交叉步」**。
> - 原因：上一轮**每一帧都画成大劈叉**，两只靴尖相隔 29–55 格；金铲铲里她的步子小得多（8–38 格），而且**有两条腿在胯下交叉、并拢的帧**（run6 两腿交叉成 X，run1 / run8 两只靴子几乎上下对齐）。上一轮从「红靴在前 49 格」一帧就跳到「蓝靴在前 33 格」，中间那一下交叉没画出来。
> - 这一轮**只重画 5 帧：run1、run5、run6、run7、run8**。run2、run3、run4 留用（`0_keep_run2-4.png`：**样子、大小、颜色、画法照它们画**，8 帧要连得上）。
> - 画布、格子、地面、头、腿的颜色规则全和上一轮一样（`RUN_PROMPTS.md` 那一套）：画布 1254 × 1254，每格 **12 px**，脚底 y = 1176；**近侧红腿 = 藏青大腿、亮、永远画在上面；远侧蓝腿 = 整条暗一档、在后面**。

## 最要紧的：两只靴尖之间的距离

**每帧画完，数一数两只靴尖（鞋头最前面那一格）横着差几格**，要等于下表「要画成」那一列（差 3 格以内可以）。整个人画在哪儿没关系，**两只靴子之间的距离一定要对**。

| 帧 | 红靴尖 x | 蓝靴尖 x | **要画成** | 上一轮画成了 | 样子 |
|---|---|---|---|---|---|
| run1 | 50 | 42 | **8 格（红靴在前）** | 29 格（红靴在前） | 红腿（近侧、藏青大腿）膝盖抬起正从蓝腿**前面**摆过来，两只靴子几乎上下对齐（红靴抬起，在蓝靴前上方） |
| run5 | 53 | 37 | **16 格（红靴在前）** | 49 格（红靴在前） | 红腿踩在身体正下方，蓝腿（远侧、暗）从后面收回来、小腿向后弯起，靴子已经回到身体后方不远处 |
| run6 | 41 | 47 | **6 格（蓝靴在前）** | 33 格（蓝靴在前） | **交叉的那一帧**：两条腿在膝盖处交叉成 X，蓝腿（远侧、暗）正从红腿后面迈到前面，两只靴尖只差几格 |
| run7 | 38 | 55 | **17 格（蓝靴在前）** | 55 格（蓝靴在前） | 蓝腿踩下在身体前面一点，红腿（近侧、藏青）在后面抬起、小腿向后弯，但**不要向后踢得很远** |
| run8 | 42 | 51 | **9 格（蓝靴在前）** | 48 格（蓝靴在前） | 蓝腿踩在身体正下方，红腿（近侧、藏青）大腿已经摆到身体下面、膝盖向前，靴子抬起在蓝靴旁边 |

- `0_wide_wrong.png` 是上一轮这 5 帧（**步子太宽，不要这样画**）；`0_run_cycle.png` 是金铲铲原版整个循环，看 run6 两腿怎么交叉、run1 / run8 两只靴子怎么并在一起。
- **交叉的地方**：两条腿重叠时，**近侧红腿（藏青大腿）盖在远侧蓝腿上面**，蓝腿只露出在红腿前后的部分。

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`、`0_head.png`、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`、`0_keep_run2-4.png`、`0_wide_wrong.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character (a lean teenage girl street fighter: magenta-pink hair, a wine-red vest with a red hood, a pale grey-green shirt, baggy dark purple-brown trousers with a DARK NAVY PATCH on the NEAR thigh, olive leg wraps, dark brown boots, a HUGE IRON GAUNTLET on each hand) on a 1254x1254 canvas with 12 px squares, her soles on y 1176. B her HEAD 8x. C a 3D render of her own game model in THIS FRAME of her run, already placed on the canvas. D its SKELETON over C: RED line = her NEAR leg, BLUE line = her FAR leg, grey box = the head. E her whole run, 8 frames. F THREE FRAMES OF THIS RUN ALREADY DRAWN (run2, run3, run4) - match their look, size, colours and style exactly. G the previous try of the frames being redrawn - its strides are FAR TOO WIDE, never draw the legs that far apart.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D, the style of image F: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px on one straight grid from the canvas corner, her lowest point on y 1176.
THE STRIDE IS SHORT: copy C exactly - the two boots CLOSE together as in C, the legs passing each other under her hips. Count the squares between the two toes: it must be the number this frame's line gives.
THE LEGS: the NEAR leg (RED line) always has the dark NAVY thigh patch, full tone, and is drawn OVER the far leg where they overlap or cross. The FAR leg (BLUE line) is a step darker all over (no navy) and always BEHIND.
THE HEAD: copy image B square for square into the grey box, never turned. Both gauntlets up at her chest as in F.
The same colours as image A; a 1-square near-black outline; no stray squares, no dithering, no gradients, no blur, no anti-aliasing; no effects, no background, no ground, no shadow, no text, no grid or skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行：

- run1: `RUN 1 of 8 - the NEAR (red) knee swinging forward past the far leg, the two boots nearly one above the other. The two TOES only 8 squares apart (the RED (near) toe ahead): red toe at square (50, 76), blue toe at square (42, 96); about 67 squares tall.`
- run5: `RUN 5 of 8 - the near (red) boot planted under her hips, the far (blue) leg folding forward behind it, its boot just behind. The two TOES only 16 squares apart (the RED (near) toe ahead): red toe at square (53, 96), blue toe at square (37, 77); about 68 squares tall.`
- run6: `RUN 6 of 8 - THE CROSSING: the legs cross in an X at the knees, the far (blue) leg stepping through past the near one. The two TOES only 6 squares apart (the BLUE (far) toe ahead): red toe at square (41, 94), blue toe at square (47, 93); about 71 squares tall.`
- run7: `RUN 7 of 8 - the far (blue) boot down a little ahead, the near (red) leg lifted behind, folded, NOT kicked far back. The two TOES only 17 squares apart (the BLUE (far) toe ahead): red toe at square (38, 73), blue toe at square (55, 96); about 79 squares tall.`
- run8: `RUN 8 of 8 - the far (blue) boot planted under her hips, the near (red) thigh swinging under the body, its boot lifted beside. The two TOES only 9 squares apart (the BLUE (far) toe ahead): red toe at square (42, 68), blue toe at square (51, 96); about 75 squares tall.`

## 交回

- 每帧一张：`outputs/violet-run-cross/violet-run-<名字>.png`（只有 run1、run5、run6、run7、run8）；`generation-prompts.txt` 写明实际用的提示词；`validation.json` 写下每帧两只靴尖实际在哪一格、**两只靴尖差几格**。
- **画完每帧先自己数两只靴尖的距离**，和上表差 3 格以上就重画那一帧。
- 5 帧都画完再交，写 `outputs/violet-run-cross/HANDOFF.md`，打包成 `outputs/violet_run_cross_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/violet/codex_run_cross/`，和留用的 run2–4 一起按自己的格子读回（design_violet_poses.py），量每帧两只靴尖的距离和原版比，连起来播放看交叉步。
- 这份提示词和图由 `tools/art/pack_violet_run_cross.py` 生成。
