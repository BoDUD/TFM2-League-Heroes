# 锐雯：动作逐帧重画（给 Codex 的提示词）

> 锐雯的定稿设计图已经通过（`refs/design_no_sword.png`，8 倍放大，一格 = 一个像素块）。之前的动作是把设计图拆成几块（剑、手、腿）转来转去拼出来的，身体本身从来不动，所以每个动作看起来都是同一个姿势。这次请**每一帧都重新画整个人**，像隔壁 oppi 的锐雯那样（`refs/oppi_*.png`）：身体前倾、扭转，腿迈开，手臂挥动。**姿势照英雄联盟的同一帧**（`refs/league_*.png`）。
>
> 一共 **18 张模板**（`templates/*.png`，每张 1536×1024，一张三帧，每格 512×1024）：
> - 平A 三套：`attack_1/2`、`attack2_1/2`、`attack3_1/2`（各 6 帧）
> - Q 三段：`skill_1/2/3`（第一段）、`q2_1/2/3`（第二段）、`q3_1/2/3`（第三段，跳起翻身下劈）（各 7 帧）
> - E：`skill2_1/2/3`（8 帧：前 4 帧 E 冲刺，后 4 帧 W 举剑）
>
> **每一格里**：
> - **灰色横线是地面**，短竖线是她的站位点；**左边的灰色竖条是她站直时从头发尖到脚底的高度**（56 格）。
> - **火柴人是英雄联盟这一帧的骨骼**，已经按她的身材缩放过：**蓝色是近侧的手脚**（画面前面那一侧），**灰色是远侧**，**黑圈是她的头（连头发）该在的位置和大小**。火柴人只用来定**位置和大小**；具体姿势（身体怎么倾、怎么扭、手脚怎么摆）看 `refs/league_<同名>.png` 里同一帧的渲染图。
> - **蓝色小圆圈是她握剑的那只手（远侧手）**：画成**握紧的拳头**，正好在圆圈里，**拳头握的方向顺着红线**。
> - **红线是剑的方向。剑不要画！** 剑由我们之后按角度贴上去（平时的断剑和开大的重铸剑共用这些帧）。所以画面里**不要有任何剑、剑柄、剑光**，只画握着空拳的手。
>
> **人物必须和定稿设计图一模一样**（`refs/design_no_sword.png`、`refs/design_1x.png` 1 倍原图、`refs/design_palette.png` 全部颜色）：
> - 同样的白发和发型、同样的脸（两只眼睛一样高）、**绿色大肩甲在同一侧**、绿色上衣、棕色腰带和护腰、前臂白绷带、深紫短裤、腿上绷带、棕色靴子。**只用调色板里的颜色**。
> - **大小不变**：头的大小、身体的宽度、**手臂和腿的长度、粗细每一帧都和设计图一样**（不要拉长、压扁或变粗变细；蹲下就是腿弯曲，不是腿变短）。站直的帧从头发尖到脚底 = 灰色竖条的高度。
> - 四分之三侧身、**脸朝右前方**，和设计图一样（英雄联盟某些帧转身背对镜头时，也请画成脸朝右前方的样子，只改姿势）。
>
> **画风照 oppi**（`refs/oppi_<动作>.png`，只看动作的画法和力度，**不要照它的衣服、颜色和比例**）：每帧一个清楚的剪影，出招时身体大幅倾斜扭转，脚踩稳；冲刺时身体前倾、大步。
>
> **像素规则**：每块 **8 像素**的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**不画特效、剑光、地面、影子、文字**；模板上的线、圈、字、格子边框**全部不要留在交付图里**。
> **背景**：真透明（每个像素透明度只能是 0 或 255）；如果做不到透明，就用**纯白 #FFFFFF 平涂背景，人物外面不要任何光晕或阴影**。
>
> - 交付：`outputs/riven-actions/<模板同名>.png`（18 张，都是 1536×1024，**和模板一样的三格布局**，每帧画在模板对应格子的位置上：脚踩地面线、站位点不变）；原始生成图原样放进 `outputs/riven-actions/raw/`；附 `generation-prompts.txt`（实际用的提示词）；**最后**在同一个文件夹写 `HANDOFF.md`（交付说明），再打包成 `outputs/riven_actions_done.zip`。

## 附图（压缩包 `riven_actions_pack.zip`，解压到一个新的文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design_no_sword.png` | 定稿设计图（8 倍，去掉了剑） | **每张都附，第一张**：人物的样子、比例、颜色 |
| `refs/design_1x.png` | 定稿设计图 1 倍原图（带旧的大剑，剑不用管） | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | 只用这些颜色 |
| `templates/<名>.png` | 三帧的模板 | **第二张**：每帧的位置、大小、拳头、剑的方向 |
| `refs/league_<名>.png` | 英雄联盟同样三帧的渲染（Q 版模型） | **第三张**：每帧的姿势 |
| `refs/oppi_<动作>.png` | oppi 的锐雯同一种动作（4 倍） | **第四张**：动作画法（只看画法） |
| `sheets.json` | 每张模板是哪个动作的第几帧，配哪张 oppi 图 | 对照 |

oppi 图对应：平A 三套 → `oppi_attack.png`；Q 第一段 → `oppi_skill.png`；Q 第二段 → `oppi_skillp2.png`；Q 第三段 → `oppi_flip.png`；E → `oppi_skill2.png`。

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design_no_sword.png`、`templates/<名>.png`、`refs/league_<名>.png`、`refs/oppi_<动作>.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a swordswoman with short spiky white hair, tan skin, a green top with ONE big green shoulder plate, a brown belt and waist guard, white bandages on the forearms, short dark purple trousers, bandaged legs and brown boots, in 3/4 view facing right. Her sword is left out on purpose. Image 2 is a TEMPLATE of three animation frames of her <ACTION>, frames <N1>-<N3>: in each 512x1024 cell the grey horizontal line is the ground, the short tick is her standing point, the grey bar on the left is her height when standing straight (hair tips to soles); the stick figure is the game's skeleton of that frame fitted to her build (blue = her near arm and leg, grey = the far ones, the black circle = where her head with its hair goes and how big it is); the small BLUE circle is her far hand that holds the sword and the RED line is the way the sword will point from it. Image 3 is the same three frames from the game's 3D animation (a chibi model of the same character): copy each frame's POSE from it - how the body leans and twists, where the arms and legs go. Image 4 is another pixel artist's version of this character doing this kind of move: copy only HOW IT IS ANIMATED (a strong readable silhouette, the body leaning and twisting into the move, feet planted wide), not its costume, colours or proportions.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if transparency is impossible, a flat pure white background with no glow and no shadow), the SAME three-cell layout as image 2: in each cell draw the character of image 1 in that frame's pose of image 3, placed and sized by the stick figure of image 2: her soles on the ground line (unless she is in the air), her head where the black circle is and as big, her far hand a CLOSED FIST inside the blue circle, gripping along the red line. DO NOT DRAW THE SWORD - no blade, no hilt, no sword trail: only the empty fist.
She must be EXACTLY the character of image 1 in every frame: the same hair, the same face with both eyes at the same height, the green shoulder plate on the same shoulder, the same colours (image 1's colours only), the same head size, and her arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). Always the 3/4 view with the face toward the front-right, as image 1, even where the game model turns away.
THE PIXEL GRID: every square the SAME size, 8 px, aligned on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material, no stray single odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No sword, no effects, no ground, no shadow, no text. Remove every template mark: no lines, circles, stick figures, numbers or cell borders in the result.
```

`<ACTION>` / `<N1>-<N3>` 照 `sheets.json` 的 `action` 和 `frames` 填，例如 `attack_1`：`basic attack 1 (riven_attack1)`、`1-3`。
