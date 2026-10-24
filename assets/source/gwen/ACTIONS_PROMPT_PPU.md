# 格温：全部动作逐帧重画（给 Codex 的提示词）

> 格温的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，93 × 116 格）就是你上一轮画的 `gwen-v2.png`，用户选定了它。请把她的**七个动作每一帧都重新画整个人**：跑步、平A、Q、E→W、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - 旧版是另一套衣服和颜色（紫色裙子、心形剪刀环），**人物本身全部照设计图**：深蓝白分层的蓬蓬裙、白色荷叶边头饰、蓝绿色螺旋卷（粉色发梢）、大大的蓝色圆眼睛。
> - **剪刀照设计图**：金色框的裁缝大剪刀，**合拢时两片淡蓝色刀刃并成一把长刃**，金色刀背；手柄一侧是**一个大圆环、一个小圆环**，环中间是**透明的孔**。不要画旧版的心形环。
> - 旧版每帧里画着剪刀的蓝光、剪开的光效、冲刺的雾，这些是特效，**全部不画**，只画人和剪刀。
>
> 一共 **31 张模板**（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画），39 帧（重复的姿势只画一次，`sheets.json` 的 `same` 里写了哪些帧沿用哪一帧，这些不用画）：
> - 跑步 `run_*`：轻快的小跳步，剪刀扛在肩上跟着颠
> - 平A `attack_*`：剪刀从肩上甩下来往前刺（**第 4 帧刺到最前**），收回肩上
> - Q 快刀剪乱 `skill_*`：剪刀往前平举，**一张一合地剪**（第 2 帧张开成 V，第 3 帧合拢，第 9 帧张开），**第 12 帧最后一大剪**，收回肩上
> - E 断续疾走 → W 丝缕缠流 `skill2_*`：往前冲（第 1–4 帧），然后把剪刀举高（第 6、7 帧），放下
> - R 引针簇射 `ult_*`：剪刀扛在肩上，**空着的手往前甩出针**（第 4 帧甩出）
> - 受击 `hit_1`：被打得往后一缩
> - 死亡 `dead_*`：往后倒、躺下，剪刀掉在她旁边地上
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的格温；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站直时从呆毛尖到脚底的高度（116 格）。

**最重要的四条：**

1. **人物和设计图一模一样，不变形**：同样的头饰、发型和螺旋卷、同样的脸（大大的蓝色圆眼睛，两只眼睛一样高）、同样的裙子、手套、袜子和鞋；头的大小、身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
2. **剪刀每帧都是设计图里那把**，大小一样、形状一样，手一直握在大小两个环之间的手柄上；剪刀和手之间不能有空隙。每张写在 `sheets.json` 的 `scissors` 里（下面提示词的 `<SCISSORS>`）：除了 Q 张开的那几帧，剪刀都是合拢的。
3. **不画任何特效**：没有蓝光、剪开的光、雾、针的光、速度线。R 甩出的针也不画（针是特效）。
4. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；冲刺、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 剪刀环的孔、腿和裙子之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/gwen-actions/<模板同名>.png`（31 张，都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/gwen-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/gwen-actions/HANDOFF.md`（交付说明），再打包成 `outputs/gwen_actions_done.zip`。

## 附图（压缩包 `gwen_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、剪刀、衣服、比例、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作（衣服、剪刀、特效都不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、剪刀怎么样、哪些帧沿用 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a chibi doll-like girl with turquoise blue drill curls with pink tips and an ahoge, a white frilled headband with navy bows, big round blue eyes, a navy-and-white layered puffy dress with gold trim, navy gloves, white stockings and navy shoes with blue bows, carrying giant CLOSED gold-framed dressmaker scissors over her shoulder (the long pale blue blade up to the upper left; one BIG and one SMALL ROUND finger loop with transparent holes by her hand on the right), in 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (ahoge tip to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose and motion - the old costume, the old heart-looped scissors and the old blue glow effects are all wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar.
She must be EXACTLY image 1 in every frame: the same hair and curls, headband and bows, face with both big blue eyes at the same height, the same dress, gloves, stockings and shoes, image 4's colours only, the same head size, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE SCISSORS are image 1's in every frame - the same size and shape, her hand gripping the handle between the two round loops, no gap between hand and scissors, the loops' holes see-through. <SCISSORS>
NO EFFECTS AT ALL: no glow, no slash light, no sparks, no mist, no needles, no speed lines.
Always 3/4 view, face toward the front-right as in image 1.
THE PIXEL GRID: every square the size of image 1's squares, on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<SCISSORS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`scissors` 填。

## 交回前请检查

- 31 张，每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- 每帧：衣服、头饰、发型、脸和设计图一样，脸朝右前方、两只眼睛一样高；头、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- 剪刀每帧都是设计图那把（大小两个圆环、孔透明），Q 张开的帧两片刀刃从轴那里张开；其他都合拢。
- 没有任何特效。
- 最后写 `outputs/gwen-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/gwen_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图），照 `tools/art/casts_annie_hd.py` 的办法修：每张按站直时的身高定比例，头换成设计图的头，脚站稳，`same` 里的帧沿用；逐帧查剪刀大小、手和剪刀的缝、环的透明孔。
- 旧版的剪刀特效（`gwen_bake.json`：普攻和 Q 的剪光）要按新剪刀的刀尖重新定锚点；做完连同待机、选人卡轮播一起给用户审。
