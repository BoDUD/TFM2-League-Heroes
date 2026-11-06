# 泰坦（诺提勒斯）：全部动作逐帧重画（给 Codex 的提示词）

> 泰坦（诺提勒斯）的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，73 × 92 格，每格一个像素）是用户通过的那张（就是你画的 `nautilus-A.png`，按约 12.9 px 一格读回，PPU 1.80；`refs/design_picture.png` 是它的原图）：**橙色的潜水头盔**、**深色的面罩**和**两只红色的眼睛**；**灰色的大铁锚**（两个弯钩、红色的标记、棕色缠绕的锚杆）；**灰色的铁甲**和**青色的接缝**；**两只巨大的铁拳**；**古铜橙色的靴子**。请把他的**每个动作每一帧都重新画整个人**。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和别的帧一模一样的 10 帧不用再画，所以一共 38 帧（31 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **铁锚照浅色人影**：拿在拳头里、抡起、连着铁链扔出去（铁链照浅色人影画出链环）、或者竖着背在脑后，都照浅色人影；铁锚和设计图一样大；两只铁拳和设计图一样大；不画水花、气泡、冲击波、护盾的光，**眼睛的红光只画在面罩里**。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
>
> **跑步 `run_*` 的腿逐帧照这里画**（`legs` 里也写了）。**近侧腿**是靠近看画的人的那条（颜色亮），**远侧腿**是另一条（颜色暗一档，有一部分被近侧腿和身子挡住）：
>   1. **近侧腿撑地**：近侧（颜色亮的）腿笔直踩在胯下，古铜橙色的靴子平踩地面线；远侧（颜色暗的）腿弯着往后踢起，脚离地。
>   2. 近侧腿还踩在胯下、开始弯；远侧腿从后面往下摆，脚低低地离地，在撑地那只脚的后面。
>   3. 交错：远侧腿紧贴着撑地的近侧腿往前过，脚刚离地——**两只脚并在一起**。
>   4. 迈步：远侧腿往前（画面右边）伸出去、脚准备落地；近侧腿在后面（画面左边）蹬地，脚尖点地——**两只脚前后分得很开**。
>   5. **换腿——远侧腿撑地**：远侧腿笔直踩在胯下，脚平踩地面线；**近侧腿**弯着往后踢起，脚离地。
>   6. 远侧腿还踩在胯下、开始弯；近侧腿从后面往下摆，脚低低地离地，在撑地那只脚的后面。
>   7. 交错：近侧腿紧贴着撑地的远侧腿往前过，脚刚离地——**两只脚并在一起**。
>   8. 迈步：近侧腿往前伸出去、脚准备落地；远侧腿在后面蹬地，脚尖点地——**两只脚前后分开**。
>
>   **两条腿轮流**：第 1–4 帧近侧（亮）腿撑地、远侧腿往前；第 5–8 帧换成远侧（暗）腿撑地、近侧腿往前。**第 1 帧和第 5 帧必须看得出是不同的腿撑地；8 帧不能是同一个剪影**（第 3、7 帧两只脚并拢，第 4、8 帧两只脚分开）。**腿照这里写的画，不照浅色人影的腿**（旧版 1 倍的腿太小，看不清）；身体、头盔、拳头和铁锚照浅色人影。大铁拳会垂得很低，**它们不是腿**。
>
> - 跑步 `run_*`：迈着沉重的步子往前跑，铁锚扛在肩上（和设计图一样），两只铁拳前后摆，**两条腿照上面逐帧轮流迈步**。
> - 普攻 `attack_*`：站好、铁锚竖着背在脑后（第 1 帧），往后抡到身后（第 2 帧），连着铁链往前甩（第 3 帧），在身前砸下（第 4 帧），再抡回肩上（第 5 帧；第 6 帧 = 第 1 帧）。
> - Q 疏通航道 `skill_*`：把铁锚低低地抡到身后（第 1 帧），举过头顶（第 2–3 帧），连着铁链往前扔出去（第 4 帧），铁链在身前拉直（第 5–6 帧）。
> - Q 拉过去 `skill_pull_*`：身子往后仰拽着铁链、铁链在身前拉直（第 1–2 帧），把铁锚低低地拖回来（第 3 帧；第 4 帧 = 普攻第 1 帧）。
> - W+E 泰坦之怒 `skill2_*`：把铁锚举起来（第 2 帧），蹲低砸下、拳头捶地（第 3 帧），起身、铁锚往上抡（第 4 帧），站好、铁锚竖着背在脑后（第 5–6 帧；第 1 帧 = 普攻第 1 帧）。
> - R 深海冲击 `ult_*`：把铁锚高高举到身后（第 2 帧），连着铁链往前甩（第 4 帧），站好（第 8 帧）；第 1 帧 = 普攻第 1 帧，第 3 帧 = Q 第 3 帧，第 5–6 帧 = 普攻第 4 帧（砸下），第 7 帧 = 普攻第 5 帧。
> - 受击 `hit_*`：被打得往后一顿、铁锚竖着背在脑后（第 1 帧；第 2 帧 = 第 1 帧）。
> - 死亡 `dead_*`：被打中、铁锚往后上方甩起（第 1 帧），铁锚掉在身后地上（第 2 帧），身子往下沉（第 3 帧），蹲低（第 4 帧），往前扑倒、手和膝盖撑地、铁锚落在身边地上（第 5–7 帧；第 8 帧 = 第 7 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的泰坦（诺提勒斯）（跑步的腿照上面写的）；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时的高度（92 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头盔顶到头盔下沿约 29 格，**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **铁锚照浅色人影**：拿在拳头里、抡起、连着铁链扔出去（铁链照浅色人影画出链环）、或者竖着背在脑后，都照浅色人影；铁锚和设计图一样大；两只铁拳和设计图一样大；旧版的特效没有画进去。
4. **跑步要换腿**：两条腿照上面逐帧轮流迈步（第 1–4 帧近侧腿撑地，第 5–8 帧远侧腿撑地），身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间、武器和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 8 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓一圈 2 格宽的近黑描边（和设计图一样）；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/nautilus-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/nautilus-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/nautilus-actions/HANDOFF.md`（交付说明），再打包成 `outputs/nautilus_actions_done.zip`。

## 附图（压缩包 `nautilus_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 nautilus-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、手和武器在哪（衣服不照它；跑步的腿照上面写的） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a giant in an old diving suit - an ORANGE DIVING HELMET with a DARK VISOR and TWO RED EYES, a HUGE GREY ANCHOR with two curved hooks, a red mark and a brown-wrapped shaft, GREY IRON ARMOUR with TEAL SEAMS, TWO MASSIVE IRON FISTS, BRONZE-ORANGE BOOTS - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 29 squares from the top of his helmet to its lower rim) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only - draw them AS WRITTEN, not as the pale figure's): <LEGS>
NO EFFECTS AT ALL: no water, no bubbles, no shockwaves, no shield glow; the eyes' red stays inside the visor.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the visor's eyes, the anchor's hooks and the fists clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; a 2-square near-black outline around the figure as in image 1; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **铁锚照浅色人影**：拿在拳头里、抡起、连着铁链扔出去（铁链照浅色人影画出链环）、或者竖着背在脑后，都照浅色人影；铁锚和设计图一样大；两只铁拳和设计图一样大；旧版的特效没有画进去。
- **跑步两条腿轮流**：第 1 帧和第 5 帧换了一条腿撑地，第 3、7 帧两只脚并拢，第 4、8 帧两只脚分开，8 帧不是同一个剪影。
- 没有任何特效。
- 最后写 `outputs/nautilus-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/nautilus_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_khazix_hd.py`（读 raw/ 的原图；每帧的缩放按叠合法 `--fits`：画稿叠到模板的浅色人影上取重合最好的比例，重合差时取身高、头、面积的中位数）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；他站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**（第 1、5 帧撑地的腿不同）；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和凯隐（三种形态）、维克托、永恩在同一个 PR（claude/kayn-ppu）。
