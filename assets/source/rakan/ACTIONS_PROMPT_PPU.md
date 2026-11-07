# 洛：全部动作逐帧重画（给 Codex 的提示词）

> 洛的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，57 × 72 格，每格一个像素）是用户通过的那张（就是你画的 `rakan-A.png`，按约 12.99 px 一格读回，PPU 1.80；`refs/design_picture.png` 是它的原图）：**红色的羽冠**、**白发**、**红耳尖的长耳朵**、**绿色的眼睛**；**红色金边的高领**、**赤裸的上身**、**金色的护腕**、**鸟头骨的腰带**；**深绿色的灯笼裤**和**红色的绑带**；**紫灰色的鸟爪脚**；**羽毛披风**（红色金边的肩部、金橙色的长羽毛、彩虹色的羽毛尖）。请把他的**每个动作每一帧都重新画整个人**。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和别的帧一模一样的 3 帧不用再画，所以一共 51 帧（46 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **手照浅色人影**：旧版手里拿着金色羽毛的帧照着画出羽毛；**羽毛披风**和设计图一样大，形状照浅色人影（裹在身上、旋转时绕着身子甩开、出手时像翅膀一样张开、冲刺时拖在身后）；不画飞散的羽毛、光点、残影。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
>
> **跑步 `run_*` 的腿逐帧照这里画**（`legs` 里也写了）。**近侧腿**是靠近看画的人的那条（颜色亮），**远侧腿**是另一条（颜色暗一档，有一部分被近侧腿和身子挡住）：
>   1. **近侧腿撑地**：近侧（颜色亮的）腿笔直踩在胯下，紫灰色的鸟爪脚平踩地面线；远侧（颜色暗的）腿弯着往后踢起，脚离地。
>   2. 近侧腿还踩在胯下、开始弯；远侧腿从后面往下摆，脚低低地离地，在撑地那只脚的后面。
>   3. 交错：远侧腿紧贴着撑地的近侧腿往前过，脚刚离地——**两只脚并在一起**。
>   4. 迈步：远侧腿往前（画面右边）伸出去、脚准备落地；近侧腿在后面（画面左边）蹬地，脚尖点地——**两只脚前后分得很开**。
>   5. **换腿——远侧腿撑地**：远侧腿笔直踩在胯下，脚平踩地面线；**近侧腿**弯着往后踢起，脚离地。
>   6. 远侧腿还踩在胯下、开始弯；近侧腿从后面往下摆，脚低低地离地，在撑地那只脚的后面。
>   7. 交错：近侧腿紧贴着撑地的远侧腿往前过，脚刚离地——**两只脚并在一起**。
>   8. 迈步：近侧腿往前伸出去、脚准备落地；远侧腿在后面蹬地，脚尖点地——**两只脚前后分开**。
>
>   **两条腿轮流**：第 1–4 帧近侧（亮）腿撑地、远侧腿往前；第 5–8 帧换成远侧（暗）腿撑地、近侧腿往前。**第 1 帧和第 5 帧必须看得出是不同的腿撑地；8 帧不能是同一个剪影**（第 3、7 帧两只脚并拢，第 4、8 帧两只脚分开）。**腿照这里写的画，不照浅色人影的腿**（旧版 1 倍的腿太小，看不清）；身体、头、手臂和羽毛披风照浅色人影。披风拖得很低，**它不是腿**。
>
> - 跑步 `run_*`：轻快地往前跑，手臂前后摆，羽毛披风低低地拖在身后（和设计图一样），**两条腿照上面逐帧轮流迈步**。
> - 普攻 `attack_*`：站好、披风的边往后上方甩起（第 1 帧），转一圈、羽毛披风绕着身子甩成一个大圆（第 2 帧），压低往前一扑、近侧手臂伸直甩向画面右边、羽毛脱手，披风在身后拉得很长（第 3–4 帧），蹲着收回来、披风落下（第 5 帧），站好（第 6 帧）。
> - Q 微光飞翎 `skill_*`：压得很低、身子往前探、一只手靠近地面，披风低低地在身后（第 1 帧），蹲着起身、手臂往后收（第 2 帧），原地转身、披风紧紧裹住身子（第 3 帧），甩出羽毛——披风像翅膀一样张开、近侧手臂往前上方甩、两腿分开（第 4–5 帧），站好（第 6 帧）。
> - W 盛大登场·俯冲 `skill2_*`：蹲低蓄力、披风在身后张开（第 1 帧），压低往前俯冲、身子几乎是平的、头朝画面右边，披风在身后拉长（第 2–4 帧）。
> - W 盛大登场·旋上空中 `w_spin_*`：落地深蹲、披风低低地张开（第 1 帧），起身、手臂张开（第 2 帧），旋转着升到空中、脚离地、羽毛披风绕着身子大大地甩开（第 3–5 帧），落地蹲低（第 6 帧）。
> - E 轻舞成双·飞向队友 `e_dash_*`：**朝画面左边**：跳起、手臂张开、披风打开（第 1 帧），头朝画面左边平着滑翔过去、披风在身后（画面右边）拉长（第 2–3 帧）。
> - E 轻舞成双·落地 `e_land_*`：**还是朝画面左边**：落地蹲低、一条腿弯着、披风卷起（第 1 帧），起身、手臂张开（第 2 帧），站好、一只手臂往画面左边伸出去（第 3 帧）。
> - R 惊鸿过隙 `ult_*`：疾跑 8 帧：身子前倾、手臂往后，羽毛披风张开、在身后拉得很长，腿照浅色人影逐帧跑。
> - 死亡 `dead_*`：被打中（第 1 帧），踉跄、一只手臂甩起（第 2 帧），往前跪下（第 3–4 帧），脸朝下倒在地上、披风盖在身上（第 5–7 帧；第 8 帧 = 第 7 帧）。
> - 受击：两帧都和设计图一样，不用画。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的洛（跑步的腿照上面写的）；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时的高度（72 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：羽冠顶到下巴约 28 格，**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **手照浅色人影**：旧版手里拿着金色羽毛的帧照着画出羽毛；**羽毛披风**和设计图一样大，形状照浅色人影（裹在身上、旋转时绕着身子甩开、出手时像翅膀一样张开、冲刺时拖在身后）；旧版的特效没有画进去。
4. **跑步要换腿**：两条腿照上面逐帧轮流迈步（第 1–4 帧近侧腿撑地，第 5–8 帧远侧腿撑地），身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- **E 的两个动作（`e_dash_*`、`e_land_*`）他朝画面左边**（飞回队友身边），照浅色人影画，**不要转回右边**；其余动作都朝右。
- 两腿之间、手臂和身体之间、武器和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 9 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓一圈 2 格宽的近黑描边（和设计图一样）；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/rakan-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/rakan-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/rakan-actions/HANDOFF.md`（交付说明），再打包成 `outputs/rakan_actions_done.zip`。

## 附图（压缩包 `rakan_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 rakan-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、手和武器在哪（衣服不照它；跑步的腿照上面写的） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a charming feathered dancer - a RED FEATHER CREST, WHITE HAIR, LONG RED-TIPPED EARS, GREEN EYES, a high RED COLLAR with GOLD TRIM, a BARE CHEST, GOLD BRACERS, a BIRD-SKULL BELT, BAGGY DARK GREEN TROUSERS with RED TIES, GREY-VIOLET BIRD-CLAW FEET, a FEATHER CLOAK with red-and-gold shoulders, long gold-orange feathers and rainbow tips - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 28 squares from the top of his feather crest to his chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only - draw them AS WRITTEN, not as the pale figure's): <LEGS>
NO EFFECTS AT ALL: no flying feathers, no sparkles, no trails, no afterimages.
Always 3/4 view as in image 1, facing right - except the E sheets (e_dash, e_land): there he faces the picture's LEFT, as the pale figure does; the eyes, the brows and the mouth each a clear shape; the crest, the ears, the bracers and the cloak's feathers clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; a 2-square near-black outline around the figure as in image 1; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **手照浅色人影**：旧版手里拿着金色羽毛的帧照着画出羽毛；**羽毛披风**和设计图一样大，形状照浅色人影（裹在身上、旋转时绕着身子甩开、出手时像翅膀一样张开、冲刺时拖在身后）；旧版的特效没有画进去。
- **跑步两条腿轮流**：第 1 帧和第 5 帧换了一条腿撑地，第 3、7 帧两只脚并拢，第 4、8 帧两只脚分开，8 帧不是同一个剪影。
- 没有任何特效。
- 最后写 `outputs/rakan-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/rakan_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_khazix_hd.py`（读 raw/ 的原图；每帧的缩放按叠合法 `--fits`：画稿叠到模板的浅色人影上取重合最好的比例，重合差时取身高、头、面积的中位数）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；他站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**（第 1、5 帧撑地的腿不同）；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和霞、费德提克（稻草人）、璐璐在同一个 PR（ppu-b6）。
