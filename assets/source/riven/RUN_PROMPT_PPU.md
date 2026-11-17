# 锐雯：跑步逐帧重画（给 Codex 的提示词）

> 用户：「锐雯这个跑步姿势不太对吧 不然让codex补一补动作？」→「只做跑步」。

> 现在游戏里的跑步有三处不对（对照英雄联盟的 `riven_run`）：
> - **剑**：她每一圈把断剑从身前低处甩到肩膀后面再甩回来。英雄联盟里剑一直**平举在身前、剑尖朝前**。
> - **腿**：现在是小碎步，两脚离得很近。英雄联盟里是**大步跑**，后腿往后高高踢起，前腿抬膝。
> - **身体**：现在是半蹲、直着身子。英雄联盟里**明显往前倾**。
>
> 这次按定稿设计图把跑步的 8 帧（英雄联盟一圈 0.968 秒、两步，每 121 毫秒一帧）逐帧重画，画法和之前平A / Q / E 那一包一样。

## 交付

- 一共 **3 张模板**（`templates/run_1.png` 第 1–3 帧、`run_2.png` 第 4–6 帧、`run_3.png` 第 7–8 帧，第三格空着），每张 1536×1024，一张三格，每格 512×1024。
- 交付 `outputs/riven-run/run_1.png`、`run_2.png`、`run_3.png`。都是 1536×1024，**和模板一样的三格布局**，每帧画在模板对应格子的位置上。`run_3.png` 的第三格留空（透明）。
- 原始生成图原样放进 `outputs/riven-run/raw/`，不要裁、不要缩放。

**每一格里**（和平A那一包一样）：
- **灰色横线是地面**，短竖线是她的站位点。**左边的灰色竖条是她站直时从头发尖到脚底的高度**（56 格）。
- **火柴人是英雄联盟这一帧的骨骼**，已经按她的身材缩放过：
  - **蓝色是近侧的手脚**（画面前面那一侧），**灰色是远侧**；
  - **黑圈是她的头（连头发）该在的位置和大小**；
  - 脚的那个点是**脚踝**，不是脚底：踩地的那只脚，鞋底在地面线上。有的帧两只脚都离地（跑步腾空），就按火柴人的高度画，不要硬拉到地上。
  - 火柴人只定**位置和大小**。具体姿势（身体怎么倾、腿怎么踢、手怎么摆）看 `refs/league_run_<同名>.png` 里同一帧的渲染图。
- **蓝色小圆圈是她握剑的那只手（远侧手）**：画成**握紧的拳头**，正好在圆圈里，**拳头握的方向顺着红线**。跑步时这只手一直在身前、和胸口差不多高，红线朝前。
- **红线是剑的方向。剑不要画！** 剑由我们之后按角度贴上去（平时的断剑和开大的重铸剑共用这些帧）。画面里**不要有任何剑、剑柄、剑光**，只画握着空拳的手。
- **近侧（空着的）手**照渲染图前后摆，握成拳。

**跑步要注意的**：
- 8 帧是**一圈两步**：第 1–4 帧一条腿在前，第 5–8 帧换另一条腿在前。两条腿要**交替、交叉**着走，腿的远近照火柴人的颜色（蓝近灰远）。
- 每一步都是大步：后腿往后高高踢起（脚跟接近屁股），前腿抬膝往前迈，落地时身体最低。
- 身体一直往前倾；头跟着身体起伏，**头发跟着头一起动，不要自己飘**（英雄联盟里她的头发是硬的）。
- **8 帧的人一样大**：头、身体、手臂、腿的长短粗细每帧都和设计图一样，只是摆法不同。

**人物必须和定稿设计图一模一样**（`refs/design_no_sword.png`、`refs/design_1x.png` 1 倍原图、`refs/design_palette.png` 全部颜色）：
- 外观：同样的白发和发型、同样的脸（两只眼睛一样高）、**绿色大肩甲在同一侧**、绿色上衣、棕色腰带和护腰、前臂白绷带、深紫短裤、腿上绷带、棕色靴子。**只用调色板里的颜色**。
- **大小不变**：手臂和腿弯曲，不拉长、不压扁、不变粗变细。
- 朝向：四分之三侧身、**脸朝右前方**，和设计图一样。

**画风照 oppi**（`refs/oppi_run.png`，只看跑步的画法和力度，**不要照它的衣服、颜色和比例**）：每帧一个清楚的剪影，腿的交替一眼能看出来。

**像素规则**：
- 每块 **8 像素**的方块，横平竖直对齐成网格。
- 外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂。
- 不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。
- **不画特效、剑、剑光、地面、影子、文字**；模板上的线、圈、字、格子边框**全部不要留在交付图里**。

**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明的话，用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

## 附图（压缩包 `riven_run_pack.zip`，解压到一个新的文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design_no_sword.png` | 定稿设计图（8 倍，去掉了剑） | **每张都附，第一张**：人物的样子、比例、颜色 |
| `refs/design_1x.png` | 定稿设计图 1 倍原图（带旧的大剑，剑不用管） | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | 只用这些颜色 |
| `templates/run_<k>.png` | 三帧的模板 | **第二张**：每帧的位置、大小、拳头、剑的方向 |
| `refs/league_run_<k>.png` | 英雄联盟同样几帧的渲染（Q 版模型） | **第三张**：每帧的姿势 |
| `refs/oppi_run.png` | oppi 的锐雯跑步（4 倍） | **第四张**：跑步的画法（只看画法） |
| `sheets.json` | 每张模板是第几帧 | 对照 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design_no_sword.png`、`templates/run_<k>.png`、`refs/league_run_<k>.png`、`refs/oppi_run.png`。`<N1>-<N3>` 按 `sheets.json` 填：run_1 是 1-3，run_2 是 4-6，run_3 是 7-8（第三格留空）。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a swordswoman with short spiky white hair, tan skin, a green top with ONE big green shoulder plate, a brown belt and waist guard, white bandages on the forearms, short dark purple trousers, bandaged legs and brown boots, in 3/4 view facing right. Her sword is left out on purpose. Image 2 is a TEMPLATE of animation frames <N1>-<N3> of her RUN CYCLE (one loop of two strides, 8 frames in all): in each 512x1024 cell the grey horizontal line is the ground, the short tick is her standing point, the grey bar on the left is her height when standing straight (hair tips to soles); the stick figure is the game's skeleton of that frame fitted to her build (blue = her near arm and leg, grey = the far ones, the black circle = where her head with its hair goes and how big it is; the leg ends are her ANKLES - a planted foot's sole sits on the ground line, and in the airborne frames both feet stay off the ground as drawn); the small BLUE circle is her far hand that holds the sword and the RED line is the way the sword will point from it (held level in front of her, pointing forward). Image 3 is the same frames from the game's 3D run animation (a chibi model of the same character): copy each frame's POSE from it - the strong forward lean, the long stride, the back leg kicked up high behind, the front knee lifted, the near arm swinging. Image 4 is another pixel artist's version of this character running: copy only HOW IT IS ANIMATED (a strong readable silhouette, the legs clearly alternating), not its costume, colours or proportions.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if transparency is impossible, a flat pure white background with no glow and no shadow), the SAME three-cell layout as image 2: in each used cell draw the character of image 1 in that frame's pose of image 3, placed and sized by the stick figure of image 2: her head where the black circle is and as big, her far hand a CLOSED FIST inside the blue circle, gripping along the red line, her near hand a fist swinging as in image 3. Leave any unused cell empty. DO NOT DRAW THE SWORD - no blade, no hilt, no sword trail: only the empty fist.
She must be EXACTLY the character of image 1 in every frame: the same hair (it moves with her head, it does not flow on its own), the same face with both eyes at the same height, the green shoulder plate on the same shoulder, the same colours (image 1's colours only), the same head size, and her arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). The same size in every frame. Always the 3/4 view with the face toward the front-right, as image 1.
THE PIXEL GRID: every square the SAME size, 8 px, aligned on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material, no stray single odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No sword, no effects, no ground, no shadow, no text. Remove every template mark: no lines, circles, stick figures, numbers or cell borders in the result.
```

## 回来以后（我们这边）

1. 读回 3 张图，按格子切出 8 帧。
2. 每帧的头和设计图比大小，差了就单独缩放头；脸每帧不一样就锁成同一张。
3. 剑按红线的角度贴到拳头上。
4. 做成跑步（帧数和节奏照英雄联盟），出像素原样的动图给用户看，点头才装。
