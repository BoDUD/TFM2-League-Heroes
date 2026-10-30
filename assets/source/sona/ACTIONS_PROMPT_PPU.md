# 琴女：全部动作逐帧重画（给 Codex 的提示词）

> 琴女的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，117 × 155 格，每格一个像素）是用户通过的那张；`refs/design_picture.png` 是设计图读回前的**原画**，**用户要的就是这张原画的效果**：蓝色双马尾、发尾和发饰是金色，青绿色眼睛，金边蓝色长裙，腰下垂着浅青色、镶金边的长布条，**一把金色竖琴（etwahl）横在腰前，两只手扶在琴上**。请把她的**八个动作每一帧都重新画整个人**：移动、普攻、强化普攻、技能、技能 2、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和待机一模一样的帧也不用画（`sheets.json` 的 `same`），所以一共 36 帧。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图和原画**：头发、发饰、脸、长裙、长布条、竖琴的样子都照设计图。
> - **竖琴跟着旧版那一帧走**：平时横在腰前、两手扶琴；普攻、强化普攻、技能 2 远侧的手（画面右边）抬到琴的右端上方拨弦；技能两只手臂往两边张开扫过琴弦；**R 第 3–5 帧竖琴飞到她头顶上方悬空**（和人分开，中间有空隙），她站在下面举着手臂指挥，整条裙子露出来；死亡时竖琴跟着她一起沉下去，最后只剩头和竖琴露在铺开的裙子上。每帧只有一把竖琴。
> - **她是飘着走的**：裙子盖住脚，移动时没有迈步的腿，只有裙摆和双马尾跟着节奏摆动、身体轻轻起伏。
> - 不画任何特效（音符、光环、光波、闪光、速度线）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、竖琴和手怎么放（下面提示词的 `<HARP>`），移动还写了裙摆（`legs`）。
> - 移动 `run_*`：飘着往前走，竖琴横在腰前，裙摆和双马尾摆动，身体轻轻起伏。6 帧不能是同一张图。
> - 普攻 `attack_*`：远侧的手抬到琴的右端上方拨弦，再放下。
> - 强化普攻 `attack_p_*`：远侧的手抬得更高，用力拨弦，再放下。
> - 技能 `skill_*`：两只手臂从中间往琴的两端张开扫过琴弦，再收回来。
> - 技能 2 `skill2_*`：远侧的手抬到琴的右端上方拨一个长音，再放下。
> - R `ult_*`（终乐章）：第 2 帧把竖琴抬起来，第 3–5 帧竖琴飞到头顶上方悬空、她在下面举手指挥，第 7 帧收回腰前。
> - 受击 `hit_*`：被打得往后一顿，竖琴还在身前。
> - 死亡 `dead_*`：被打中，慢慢沉下去，裙子铺在地上，竖琴跟着沉下去，最后趴在竖琴后面，只露出头和竖琴。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的琴女；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从头顶到裙摆的高度（155 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：发饰顶到下巴约 **58 格**（蓝色双马尾、金色发饰、青绿色眼睛），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的头发、发饰、脸、长裙、长布条、竖琴；**体格和设计图一样**，身体宽度、手臂的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）；**竖琴一直是设计图那把金色竖琴，大小不变**。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **画得和原画一样细**：设计图是按原画最细的像素读回的（117 × 155 格），**眼睛、睫毛、嘴、手指、琴弦、裙子上的金色花纹都要像原画那样画清楚**，不要画成粗大的方块。
4. **竖琴跟着浅色人影**：平时横在腰前、两手扶琴；手抬起来拨弦的帧照浅色人影；R 第 3–5 帧竖琴悬在头顶上方、和人分开；每帧只有一把竖琴。
5. **站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧裙摆底边踩在地面线上、站位点不动；沉下去、趴下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 双马尾和身体之间、手臂和身体之间、竖琴和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 5 像素，**R 的模板 3.8 像素**——竖琴飞得高，模板缩小了，见 `sheets.json` 的 `square`；原画的外描边约 3 格宽），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；发饰、竖琴的弯头和琴弦清楚，没有光晕。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/sona-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/sona-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/sona-actions/HANDOFF.md`（交付说明），再打包成 `outputs/sona_actions_done.zip`。

## 附图（压缩包 `sona_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、裙子、竖琴、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原画 | **每张都附，第五张**：用户要的效果、细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、手和竖琴在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、竖琴和手怎么放、移动的裙摆 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a serene musician - blue hair in two big twin tails with gold ends and gold hair ornaments, teal eyes, a long blue gown edged with gold, pale teal panels edged with gold hanging from her waist over the skirt, a GOLD ETWAHL (a harp-like instrument) held LEVEL before her waist, its curled gold ends out past both sides of her body, both hands on it - 3/4 view facing right. Image 5 is the original picture image 1 was read from: THE LOOK TO MATCH - its fine detail in the eyes, lashes, mouth, fingers, strings and the gown's gold scrolls. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (the top of her hair to the hem). Image 3 is the same old frame(s) in colour: copy their body pose, motion and where the arms, the hands and the etwahl are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, the hem on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same hair, ornaments, face, gown, panels and etwahl, image 4's colours only, as finely drawn as image 5. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 58 squares from the top of her hair ornaments to her chin) - never smaller, never bigger. The build as in image 1: the body and arms the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). The etwahl is always image 1's gold etwahl, the same size.
THE ETWAHL AND THE HANDS: <HARP>
THE GOWN (run sheets only): <LEGS>
NO EFFECTS AT ALL: no music notes, no rings, no waves of light, no flashes, no speed lines.
Always 3/4 view facing right as in image 1; the eyes, the lashes, the brows and the mouth each a clear shape; the ornaments, the etwahl's curled ends and its strings clear with no glow.
THE PIXEL GRID: every square the size of the template's (sheets.json's square: 5 px, R's sheets 3.8 px), on one straight grid; the near-black outline of image 1 (about 3 squares thick) around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<HARP>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是移动的模板删掉 `THE GOWN` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**；头发、发饰、脸、长裙、长布条和设计图一样，朝画面右边；身体、手臂的大小粗细和设计图一样；只用设计图的颜色；**细节和原画一样细**；整张一个比例，站着时裙摆踩地面线、站位点不变。
- **竖琴跟着浅色人影**：一直是同一把金色竖琴，每帧一把；R 第 3–5 帧悬在头顶上方、和人分开。
- **移动的 6 帧裙摆和双马尾在摆**，不是同一张图；没有迈步的腿。
- 没有任何特效。
- 最后写 `outputs/sona-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sona_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_leona_hd.py`（白底抠图；每张的缩放先按整个人的面积量，再乘头的大小 `--heads`，因为竖琴的摆法会让面积失真）；读的格子要和设计图一样细（约 5.5 px 一格的原画密度，`design_sona_hd.py --pitch 5.5`）。`idle_base` 是设计图（静止，不上下晃）；`SAME` 里的帧（移动、普攻、强化普攻、技能、技能 2 的首尾帧，R 1、8，受击 2）就是设计图，R 6 = R 2；`idle` / `bp` 由 `hero_reels.json`（skill 1–4、attack_p 1–3）生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定（别把竖琴的两头算进“两脚中点”）；她站在地上（不悬浮）。
- R 第 3–5 帧竖琴和人分开：读回时是单独的块，检查碎块时别当成杂点删掉。
- **逐帧量头的大小**（头发和脸）；**逐帧确认竖琴和手的位置**；查碎块、空洞、第二把竖琴。
- PPU 3.88 是全游戏最高的：注册时先跑 `tools/ci/ui_sheets.py` 看选人卡的内存。
- 适配：普攻 / 技能的特效锚点按新的竖琴重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。装游戏前先合进最新 main，版本号接着游戏里现装的往上加。
