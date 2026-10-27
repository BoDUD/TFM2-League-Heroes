# 卢锡安：边走边开大（给 Codex 的提示词）

> 卢锡安的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，111 × 93 格，每格一个像素）就是游戏里现在的他。这次只画**一个新动作**：**R 圣枪洗礼时边走边开枪**，8 帧一个循环。
>
> - **腿和步子照他的跑步**（`refs/run_1.png` … `refs/run_8.png`，他现在的跑步 8 帧）：左右腿每半圈交换，身体随步子起伏，衣摆往后飘。
> - **上半身照他的 R**（`refs/ult.png`）：身体朝前，**两只手都向前伸，两把枪都平端朝前（画面右边）**，一把略高一把略低，一直在开枪的样子。
> - 模板里每一格的**浅色人影是这一帧的姿势参考**：腿怎么迈、身体高低、两把枪朝哪，照它。**但它是把两张图硬拼起来的，胯部和衣摆缺了一截、腿看起来又细又短——这些比例不要照它**：胯、腰带、白色长衣摆、腿的长短粗细，**全部照设计图**。
> - 不画任何特效（枪口火光、子弹、光束、烟、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/r_run_*.png`，每张 1536×1024，两格，每格 768 宽）：是第几帧、枪怎么拿（下面提示词的 `<WEAPONS>`）。灰色横线是地面，短竖线是站位点，左边灰色竖条是他站直时从竖举的枪口到脚底的高度（93 格）。

**最重要的六条：**

1. **头的大小每一帧都和设计图一样**：头顶到下巴约 **20 格**，不要画小、也不要画大。
2. **人物和设计图一模一样，不变形**：同样的发型、外套、护肩、胸甲、腰带、白色长衣摆、裤子和靴子；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细每帧都和设计图一样（弯曲可以，拉长、压扁、变粗变细不行）。**胯部和衣摆要完整**，不能像参考人影那样缺一截。只用调色板里的颜色（`refs/design_palette.png`）。
3. **两把枪每帧一只手一把，两把都平端朝前**：不能有一把竖举在肩旁，不能两把都在一只手里、不能交换、不能丢掉；枪的形状、大小、颜色和设计图一样。
4. **腿要有交替**：两条腿轮流在前，身体有起伏，8 帧不能是同一个姿势；腿的动作照 `refs/run_*.png` 同号那一帧。
5. **不画特效**：没有枪口火光、子弹、光束、烟。
6. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；脚踩在地面线上，人的中心对着站位点。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 手臂和身体之间、两腿之间、枪和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 7 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、鼻子、嘴各自成块。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/lucian-runshoot/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**）；原始生成图原样放进 `outputs/lucian-runshoot/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/lucian-runshoot/HANDOFF.md`（交付说明），再打包成 `outputs/lucian_runshoot_done.zip`。

## 附图（压缩包 `lucian_runshoot_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、衣服、比例、头的大小、颜色、两把枪 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第五张**：只用这些颜色 |
| `templates/r_run_<n>.png` | 两格模板，浅色人影是姿势参考 | **第二张**：每帧的姿势、位置、大小 |
| `refs/run_<k>.png` | 他现在的跑步第 k 帧（彩色，6 倍） | **第三张**：同号帧的腿和步子 |
| `refs/ult.png` | 他现在的 R（彩色，6 倍） | **第四张**：上半身、双枪平端朝前 |
| `refs/old_r_run_<n>.png` | 浅色人影的彩色版 | 对照（比例不对，只看姿势） |
| `sheets.json` | 每张模板是第几帧、枪怎么拿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/r_run_<n>.png`、这张模板两帧对应的 `refs/run_<k>.png`（两张都附）、`refs/ult.png`、`refs/design_palette.png`。

```text
Attached: image 1 is the APPROVED pixel-art character (6x: every square one pixel): League of Legends' Lucian - dark brown skin, short hair with tight braids along the scalp, green eyes, a long silver-white coat with gold-trimmed silver shoulder armour, a black chest plate, a brown belt with a gold buckle, black trousers, black boots with silver plates, long white coat tails with a lavender lining, dark brown gloves, and two big white-and-gold RELIC PISTOLS with cyan runes; 3/4 view facing right. Image 2 is a TEMPLATE of 2 animation frames, frames <FRAMES> of a NEW move: <ACTION>. In each cell the PALE FIGURE is the pose guide (where the legs are, how high the body is, where both pistols point), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing. The pale figure was pasted together from two poses, so its hips and coat skirt are cut short and its legs look thin and short: DO NOT copy those proportions - the hips, belt, long white coat tails and the legs' length and thickness must be exactly image 1's. The next images are his current RUN frames with the same numbers (copy their legs and stride) and his current ULT frame (copy its upper body: squared to the front, both arms out, both pistols level and pointing forward). The last image is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME two-cell layout as image 2: in each cell draw the character of image 1 walking and shooting in that cell's pose, at its place and size, soles on the ground line, his middle over the standing point. One scale for the whole sheet, set by the grey bar.
He must be EXACTLY image 1 in every frame: the same hair, coat, shoulder armour, chest plate, belt, coat tails, trousers, boots, gloves and pistols, the palette's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 20 squares from the top of the head to the chin). The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned); the hips and the coat skirt complete.
THE PISTOLS: <WEAPONS>
THE LEGS: they swap every half cycle like his run (left foot forward, then right foot forward), the body bobbing with the steps.
NO EFFECTS AT ALL: no muzzle flash, no bullets, no light beam, no smoke, no speed lines, no dust.
Always 3/4 view, face toward the front-right as in image 1; the eyes, brows, nose and mouth each a clear shape.
THE PIXEL GRID: every square the size of the template's (7 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<FRAMES>`、`<ACTION>`、`<WEAPONS>` 照 `sheets.json` 的 `frames`、`action`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、两格布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- **每帧的头和设计图一样大**；衣服和设计图一样，脸朝右前方；**胯部和衣摆完整，腿的长短粗细和设计图一样**；只用设计图的颜色；整张一个比例，脚踩地面线。
- **两把枪每帧一只手一把、都平端朝前**，没有竖举、没有交换、没有丢。
- **两腿轮流在前、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/lucian-runshoot/HANDOFF.md`，再打包成 `outputs/lucian_runshoot_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_lucian_hd.py`（白底、按头定缩放、跑步按头摆一列）读成 2.02 的 `r_run`，放进 `assets/source/ppu/orig/`，再 `ppu_restyle.py --hero lucian`（1.5）、`ppu_hd.py`、`hero_reels.py`。
- 逐帧量头、查两把枪都朝前、查换腿和起伏、查碎块空洞；和 `hd_run` 同号帧比腿的位置。
- 游戏里：新附加包在 `league_lucian_r_ch` 存在时把 `run`（和 `idle`）换成 `r_run`（league_anivia / league_aphelios 的 view.rs FORM_TAGS 做法）；佛耶戈灵魂表、整合包。
