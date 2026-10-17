# 奈德丽：人形跑步重画 8 帧（给 Codex 的提示词）

> 用户：「奈德丽走路有点问题 跑动姿势不像LOL的」。上次画的 8 帧跑步（`refs/previous_run_wrong.png`）**同一条腿一直在前**，像往前蹦；现在游戏里临时用的是站姿抬腿，也不像。这次**只重画人形的跑步 8 帧**，照英雄联盟里她的跑法：**身体明显前倾、大步交叉、两条腿轮流在前**。其他动作都不动。
> - `now/nidalee_run_<n>.png` 是**骨架**：英雄联盟里她跑到这一刻的 3D 模型，已经按造型的大小放在同一个 1536×1024 画布、同一个 5 px 网格上——**身体前倾的角度、步子大小、位置照它**。`guide/` 是同一张加了线：**红线 = 脚底线**（第 196 行的下边，踩地的脚踩在上面，离地的脚可以抬起），蓝十字 = 站位点。线不要画进图里。
> - **长相、比例、颜色、细节全部照造型** `design/nidalee_human_design.png`（101 × 168 格，56 色），**和造型一样大**（站直时马尾顶到脚底 159 格）。
> - **头每帧都是造型的头**：`design/nidalee_head.png` 逐格照抄（脸、绿眼睛、白色纹彩、额头绿点、耳坠、红绳、羽毛），只平移，脸朝右前方；马尾往后飘，形状照造型。**身体是 3/4 正面朝右**（胸口朝看画的人），前倾是整个上半身往前（画面右边）倒，**头和身体不变形、不拉长**。
> - **标枪**：造型里那根（木杆红环、黑白羽毛、浅灰白石头枪头），**一根笔直的直线，每帧都水平**、枪头朝前（画面右边），握在远侧手里、在腰的高度（英雄联盟里是斜着拿在身侧，我们画成水平），随步子上下颠 1–2 格；**长度和造型一样（168 格）**，不能弯、不能缩短。
> - **交叉步**照 `refs/caitlyn_run.png`（通过的凯特琳跑步）：两条腿**轮流在前**，每半个循环换一次，中间在身体下面**交错经过**；**身体前倾**照 `refs/zeri_run.png`（通过的泽丽跑步：上半身整块前倾，臀部在两腿正上方）。英雄联盟里她的跑步见 `refs/league_run.png`（3D 渲染，看节奏和前倾）。
> - **近侧的腿**（画面左边那条，颜色亮）画在前面；**远侧的腿**暗一档，画在近侧腿后面（交错时被挡住一部分）。腿的粗细、颜色、毛皮绑腿、绿绳、靴子都照造型，**腿的长度每帧一样**，不要缩短、不要变形。
> - 每格 5 × 5 px 一个纯色方块，所有格子对齐同一个网格；**只用造型的 56 色**（`design/nidalee_palette.png`）；1 格近黑描边；不要抖动、渐变、抗锯齿、半透明；不画特效、不画影子；红线以下什么都不能有。

## 每帧两条腿的位置

（「前」= 画面右边，她朝右跑。）

| 帧 | 近侧腿（亮） | 远侧腿（暗） |
|---|---|---|
| 1 | 踩在身体正下方，膝盖微弯（承重） | 从后面往前摆，**正好经过近侧腿后面**（交错），脚离地 2–3 格 |
| 2 | 往后蹬，脚跟抬起 | 摆到前面，膝盖抬起 |
| 3 | 在后面，脚抬起离地 | 往前伸直，脚跟落向前方 |
| 4 | 最靠后，小腿往后踢起（步子最大） | 在前面踩地 |
| 5 | 从后面往前摆，**正好经过远侧腿前面**（交错），脚离地 2–3 格 | 踩在身体正下方，膝盖微弯（承重） |
| 6 | 摆到前面，膝盖抬起 | 往后蹬，脚跟抬起 |
| 7 | 往前伸直，脚跟落向前方 | 在后面，脚抬起离地 |
| 8 | 在前面踩地 | 最靠后，小腿往后踢起（步子最大） |

近侧手臂（画面左边那只，空手）和步子反着前后摆：近侧腿在后时它在前。

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：`now/nidalee_run_<n>.png`（骨架）、`design/nidalee_human_design.png`（造型）、`design/nidalee_human_design_on_canvas.png`（大小和位置）、`refs/caitlyn_run.png`（交叉步）、前一帧你刚交付的那张（第 1 帧不附，附 `refs/zeri_run.png`）。

```text
Image 2 is the final pixel-art design of this character: Nidalee, a jungle huntress in 3/4 front view facing right - tan red-brown skin with white tribal paint, a huge black ponytail tied with red and a black-and-white feather, green eyes, a green dot on the forehead, a white-fur-trimmed leather top, fur bracers, a tusk belt over a fringed loincloth, big brown fur leg wraps bound with olive-green cords, and her javelin (wooden shaft with red bands, a black-and-white feather, a pale stone blade, as long as she is tall). It is drawn on a grid of 5x5-pixel squares, 101 x 168 squares, 56 colours. Image 3 shows the design standing on the 1536x1024 canvas: that is her size.
Image 1 is a 3D render of the same character from the game in THIS FRAME'S RUNNING POSE, already scaled and placed on the same canvas: copy its forward lean, its stride and its place - NOT its 3D look, NOT its proportions. Image 4 is another character's approved 8-frame run: how the two legs TAKE TURNS in front and cross under the body. (Image 5 is the previous frame of this run: keep her exactly as big.)
Draw ONE frame: running to the right, frame <n> of an 8-frame loop, the body leaning clearly forward as in Image 1, <LEGS>; the near (empty) arm swinging opposite to the near leg; the javelin held LEVEL in her far hand at hip height, the blade pointing forward to the right, ONE STRAIGHT horizontal line as long as in Image 2, bobbing 1-2 squares with the stride; the ponytail streaming back.
Rules: the same 1536x1024 transparent canvas and the SAME 5-pixel grid as Image 3, every square one flat colour from Image 2's 56 colours; exactly as big as Image 2; she stays in the 3/4 FRONT view (chest toward the viewer), the lean is the whole upper body tilting forward, the head and body not stretched; her head - face, eyes, paint, dot, earrings, red tie, feather - copied square for square from Image 2, only moved; the near leg on the image left side of the stride in full tone and drawn in front, the far leg one shade darker and behind it, both legs as long and as thick as in Image 2 in every frame; the planted sole on the red line of the guide (square row 196), a lifted foot above it, nothing below it; a 1-square near-black outline; no dithering, no gradients, no noise, no anti-aliasing, no semi-transparency; no effects, no shadow, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<LEGS>` 按上表换成英文：

1. `the near leg planted right under the body, knee slightly bent; the far leg swinging forward and passing right behind the near leg, its foot 2-3 squares off the ground`
2. `the near leg pushing back, its heel lifting; the far leg swung to the front, knee raised`
3. `the near leg behind, its foot lifted off the ground; the far leg reaching forward straight, heel coming down ahead`
4. `the widest stride: the near leg farthest back, its shin kicked up behind; the far leg in front, planted`
5. `the far leg planted right under the body, knee slightly bent; the near leg swinging forward and passing right in front of the far leg, its foot 2-3 squares off the ground`
6. `the far leg pushing back, its heel lifting; the near leg swung to the front, knee raised`
7. `the far leg behind, its foot lifted off the ground; the near leg reaching forward straight, heel coming down ahead`
8. `the widest stride: the far leg farthest back, its shin kicked up behind; the near leg in front, planted`

## 交付

`outputs/nidalee-run-fix/`：`nidalee_run_1..8.png`（1536×1024、5 px 网格、透明）+ `nidalee_run_<n>_1x.png`（307×204，逐格一致），`raw/` 原稿，**最后**写 `HANDOFF.md`；打包 `nidalee_run_fix_done.zip`。

交回前检查：
- **两条腿每半个循环换一次前后**：第 1–4 帧和第 5–8 帧前面的是不同的腿，第 1、5 帧在身体下交错（把 8 帧排在一起看，不能是同一条腿一直在前）。
- 身体前倾、3/4 正面、头是造型的头、和造型一样大；标枪每帧水平、一根直线、长度不变；腿长每帧一样；踩地的脚在红线上。

## Claude 收到后（给 Claude 看）

- 按格子读回 `_1x`，用 import_nidalee_strips.py 的做法：脸匹配定大小、脚底贴地、贴回造型的头；查腿的交替（每帧近侧腿 / 远侧腿的脚在哪一边）、腿长、缝（gap-check）、标枪水平；再走 rig_nidalee.py → ppu_restyle.py → ppu_hd.py；其他动作逐字节不变；给用户看前后对比 GIF。
