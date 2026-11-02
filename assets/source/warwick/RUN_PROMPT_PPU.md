# 狼人：跑步重画（给 Codex 的提示词）

> 狼人现在的跑步是我们用设计图拼出来的：两条腿只是上下挪几格、身子一浮一沉，看起来像在原地蹭（用户：「狼人的走路姿势现在有点奇怪」）。这次请把**跑步 8 帧每一帧都重新画整个人**，照**英雄联盟里狼人的跑步**（`refs/lol_run.png`，从侧前方看的 8 帧）：**弓着背、往前扑着跑，两条腿轮流蹬地和迈步，手臂和腿反着摆，尾巴在身后甩**。
>
> 人物全部照定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，94 × 69 格；`refs/design_picture.png` 是它的原图）：**深蓝的毛、白色的胸毛和下巴、张开的血盆大口和黄眼睛**、**头顶向后的尖耳和鬃毛**、**近侧手臂上铜色的护臂、绿色的药瓶和高高的尖刺**、**远侧手上张开的利爪**、**卡其色的短裤**、**深蓝的兽腿和爪子**、**身后的大尾巴**。**四分之三侧身、朝画面右边，和设计图一样**（不要画成正面）。
>
> `sheets.json` 的 4 张模板（`templates/run_1.png` … `run_4.png`，每张两格，第 1–2、3–4、5–6、7–8 帧）每格写了**这一帧的腿**（`legs`）。**近侧腿**是靠近看画的人的那条（颜色亮），**远侧腿**是另一条（颜色暗一档，有一部分被挡住）：
> 1. **近侧腿撑地**：近侧腿踩在胯下，爪子平踩地面；远侧腿弯着往后上方踢起，脚离地很高。
> 2. 近侧腿还踩着、往下弯，身子下沉；远侧腿从后面往下摆。
> 3. 交错：远侧腿从撑地的近侧腿旁边往前摆过去，脚刚离地；身子最低。
> 4. 迈步：远侧腿往前（画面右边）伸出去准备落地；近侧腿在后面（画面左边）蹬地，脚尖点地；身子往上起。
> 5. **换腿——远侧腿撑地**：远侧腿踩在胯下；**近侧腿**弯着往后上方踢起。
> 6. 远侧腿还踩着、往下弯；近侧腿从后面往下摆。
> 7. 交错：近侧腿从撑地的远侧腿旁边往前摆过去。
> 8. 迈步：近侧腿往前伸出去准备落地；远侧腿在后面蹬地。
>
> **第 1 帧和第 5 帧必须看得出是不同的腿撑地。**
>
> **每一格里的浅色人影是现在的跑步帧**：**只看它站在哪、有多大**（照它定位置和大小，脚踩灰色地面线、站位点不动，身子可以随步子上下起伏一两格），**它的腿就是要重画的那部分，不要照它的腿**——腿照上面的文字和附图 3（英雄联盟的跑步）。左边灰色竖条是他站着时从护臂尖刺到脚底的高度（69 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**，**不要画小、也不要画大**；八帧连起来播，头和身子不能一会儿大一会儿小。
2. **人物和设计图一模一样，不变形**：同样的毛色、胸毛、脸、耳朵、护臂和药瓶尖刺、利爪、短裤、腿、尾巴；身体宽度、手臂和腿的粗细**每帧都和设计图一样**。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **跑步要换腿**：两条腿照上面逐帧轮流撑地和迈步，身子跟着起伏，手臂和腿反着摆。
4. **四分之三侧身、朝画面右边**，和设计图一样；不画正面、不画背面。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧同一个比例。

- 两腿之间、手臂和身体之间、尾巴和身体之间的空隙都是**透明**的。
- 不画任何特效（尘土、速度线、残影、血都不要）。

**像素规则**：和设计图同样密度的方块（模板里每格 8 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、牙齿、药瓶和爪子清楚。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/warwick-run/run_1.png` … `run_4.png`（1536×1024，和模板一样的两格布局）；原始生成图放进 `outputs/warwick-run/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/warwick-run/HANDOFF.md`，再打包成 `outputs/warwick_run_done.zip`。

## 附图（压缩包 `warwick_run_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、比例、头的大小、颜色 |
| `templates/run_<k>.png` | 两格模板，浅色人影是现在的跑步帧 | **第二张**：只看**站的位置和大小**（腿要重画） |
| `refs/lol_run.png` | 英雄联盟里狼人的跑步 8 帧（3D，从侧前方看） | **第三张**：**腿怎么交替、身子怎么起伏、手臂怎么摆**（不照它的写实比例） |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图 | **第五张**：细节 |
| `refs/old_run_<k>.png` | 现在的跑步帧（彩色） | 对照：它的腿就是要改的 |
| `sheets.json` | 每张模板是第几帧、腿怎么摆（`legs`）、手臂和尾巴（`weapons`） | 填提示词 |

## 提示词（每张模板一次，换掉 <...>）

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a hulking werewolf - dark blue fur, a white chest ruff and jaw, a gaping fanged mouth and yellow eyes, swept-back pointed ears and mane, a bronze GAUNTLET on the near arm with green vials and a tall spike, open claws on the far hand, khaki shorts, dark blue beast legs with claws, a big tail behind him - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of 2 frames of his RUN (frames <FRAMES>): in each cell the PALE FIGURE is the run frame now - use it ONLY for where he stands and how big he is, NOT for his legs (they hardly move: that is why the run is drawn again); the grey line is the ground, the tick his standing point, the grey bar his height (the gauntlet's spike to his soles). Image 3 is League of Legends' own Warwick run, 8 frames, a 3D render: copy how the legs take turns, how the body rises and sinks and how the arms swing - not its realistic proportions. Image 4 is image 1's palette.
Create ONE 1536x1024 pixel-art sheet, genuine transparent background (or flat pure white), the SAME two-cell layout as image 2: in each cell image 1's character running, at the pale figure's place and size, the planted foot on the ground line. One scale for the sheet, set by the grey bar. Do not rescale, crop or re-lay it.
THE LEGS - this is why the run is drawn again: <LEGS> The NEAR leg is the one on the viewer's side, a step LIGHTER; the FAR leg a step DARKER, partly behind it.
<ARMS>
He is EXACTLY image 1: the same fur, chest ruff, face, ears, gauntlet with its vials and spike, claws, shorts, legs and tail, image 4's colours only. THE HEAD THE SAME SIZE AS IN IMAGE 1 in every frame. The body, arms and legs the same thickness as image 1. Always 3/4 view facing right as image 1, never front-on.
NO EFFECTS: no dust, no speed lines, no afterimages, no blood.
THE PIXEL GRID: squares the size of the template's (8 px) on one straight grid; the near-black outline of image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<FRAMES>`、`<LEGS>`、`<ARMS>` 照 `sheets.json` 每张的 `frames`、`legs`、`weapons` 填。

## 交回前请检查

- **第 1–4 帧近侧（亮）腿撑地，第 5–8 帧远侧（暗）腿撑地**；第 1 帧和第 5 帧一眼看得出换了腿；8 帧不是同一个姿势，身子有起伏，手臂和腿反着摆。
- 头和设计图一样大；人物和设计图一样、四分之三侧身朝右；只用设计图颜色；没有特效；每张 1536×1024、两格布局、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/warwick-run/HANDOFF.md`，再打包成 `outputs/warwick_run_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_senna_hd.py` 的读法（白底抠图、读到设计图 1.5 格的密度上；缩放按身高和头的大小），写进 `assets/source/ppu/orig/warwick_run.png`（每帧的大小照 `warwick_run.json`，站位点在帧中心、脚底在中心下 17.25 格），其余动作不动；再跑 `ppu_restyle.py --hero warwick`（PPU 1.2、描边）、`ppu_hd.py`、`hero_reels.py`。`rig_warwick.py` 以后重跑会把跑步改回旧的拼法：跑步要从读回的帧来。
- 逐帧对腿；和待机、普攻放在一起看头的大小。和赛娜在同一个 PR（claude/senna-ppu）。
