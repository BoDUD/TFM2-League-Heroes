# 伊芙琳：全部动作逐帧重画（给 Codex 的提示词）

> 伊芙琳的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，103 × 114 格，每格一个像素）是用户通过的那张（就是你画的 `evelynn-A.png`，按它自己约 10.4 px的格子读回；`refs/design_picture.png` 是它的原图）：**粉白火焰形的大头发**和头顶的**深紫尖角**、**淡紫皮肤**、**发黄光的眼睛**；**深靛蓝紧身衣**和**粉色拼块**、**粉色长爪**、**粉紫长腿和细高跟**；背后两条**深紫鞭须**，末端是**发亮的紫色尖片**。请把她的**九个动作每一帧都重新画整个人**：跑步、普攻、E 鞭笞、强化 E、Q、W、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；旧版有 10 帧和别的帧一模一样（普攻第 1、6 帧、E 第 1、6 帧、强化 E 第 9 帧、R 第 6 帧就是待机姿势；W 第 4 帧 = 第 3 帧；死亡第 2 帧 = 第 1 帧、第 7、8 帧 = 第 6 帧），不用再画，所以一共 49 帧（45 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **两条鞭须照浅色人影**：卷着、往前抽、拉长，照浅色人影；长短粗细和设计图一样，末端的紫色尖片清楚；**浅色人影里的紫色光带、火花是旧版画进去的特效，不要画**。
> - 不画任何特效（紫色能量、飞出去的尖刺、爱心、残影都不要）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：**两条腿照下面逐帧轮流迈步**（这是之前泰隆和赛娜跑步都没做到、只好重画的地方）：
>   1. **近侧腿撑地**：近侧（颜色亮的）腿笔直踩在胯下，整只脚平踩地面；远侧腿弯着往后上方踢起，脚离地很高。
>   2. 近侧腿还踩在胯下、开始弯；远侧腿从后面往下摆，脚离地，在撑地那只脚的后面。
>   3. 交错：两条腿收在身子下面、膝盖弯着；远侧腿贴着撑地的近侧腿往前过，脚刚离地。
>   4. 迈步：远侧腿往前（画面右边）伸出去准备落地，脚跟先着地；近侧腿在后面蹬地，脚尖点地。
>   5. **换腿——远侧腿撑地**：远侧（颜色暗的）腿笔直踩在胯下；**近侧腿**弯着往后上方踢起。
>   6. 远侧腿还踩在胯下、开始弯；近侧腿从后面往下摆。
>   7. 交错：近侧腿贴着撑地的远侧腿往前过。
>   8. 迈步：近侧腿往前伸出去准备落地；远侧腿在后面蹬地。
>
>   **第 1 帧和第 5 帧必须看得出是不同的腿撑地。**
> - 普攻 `attack_*`：爪子往后收（第 2–3 帧），鞭须朝目标往前抽（第 4–5 帧），收回（第 6 帧）。
> - E 鞭笞 `attack_e_*`：近侧手臂高高举起（第 2–3 帧），两条鞭须往前下方抽（第 4–5 帧）。
> - 强化 E `attack_e2_*`：她冲过目标，两条鞭须前后拉得很长（第 1–8 帧）；**旧版这几帧画了一大片紫色光带，那是特效，只画她和鞭须**。
> - Q 憎恨之刺 `skill_*`：近侧手举起（第 1–2 帧），两条鞭须笔直往前刺出去（第 3–7 帧），收回（第 8 帧）。
> - W 引诱 `skill2_*`：近侧手臂朝目标伸出去，把诅咒吹出去（第 2–6 帧；第 4 帧 = 第 3 帧，不用画）。
> - R 最终抚慰 `ult_*`：压低身子，两条鞭须往前大范围横扫（第 2–4 帧），再起身、近侧手臂举起（第 5 帧）。
> - 受击 `hit_*`：被打得往后一顿，鞭须甩开。
> - 死亡 `dead_*`：被打中（第 1 帧），慢慢沉下去（第 3–5 帧），最后**跪坐着垂下头，鞭须软在地上**（第 6 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的伊芙琳；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从头发顶到脚底的高度（114 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头发顶到下巴约 **44 格**（脸本身从眉到下巴约 14 格），**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **鞭须跟着浅色人影**：两条、长短粗细和设计图一样、末端尖片清楚；旧版的紫色光带没有画进去。
4. **跑步要换腿**：两条腿照上面逐帧轮流迈步，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跪坐的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 7 像素（E 第二段每格 6 像素），见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；爪子、手指和鞭须的尖片清楚，眼睛的黄光不往外发。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/evelynn-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/evelynn-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/evelynn-actions/HANDOFF.md`（交付说明），再打包成 `outputs/evelynn_actions_done.zip`。

## 附图（压缩包 `evelynn_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 evelynn-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、手和武器在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a demon woman - a BIG FLAME OF PINK AND WHITE HAIR with dark violet spikes on top, PALE LILAC skin, softly GLOWING YELLOW EYES; a dark indigo bodysuit with PINK panels, long PINK CLAWS, long pink and dark violet legs on thin heels; TWO DARK VIOLET LASHERS growing from her back, each ending in a glowing VIOLET BLADE TIP - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing (the top of her hair to her soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same hair, face, bodysuit, claws, legs and lashers, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 44 squares from the top of her hair to her chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no violet energy, no spikes in flight, no hearts, no trails, no afterimages; the yellow glow stays inside the eyes.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the claws, the fingers and the lashers' blade tips clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **鞭须跟着浅色人影**：两条、长短粗细和设计图一样、末端尖片清楚；旧版的紫色光带没有画进去。
- **跑步两条腿轮流**，第 1 帧和第 5 帧换了一条腿撑地，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/evelynn-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/evelynn_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_senna_hd.py`（白底抠图；每帧的缩放先按身高比旧版同一帧，再按脸的肤色面积把头拉到和设计图一致，身体和旧帧相差不超过 10%）；读的格子和设计图一样（约 10.4 px一格的原图密度）。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；她站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**；**逐帧对照旧版的姿势**（赛娜 Q 前两帧画错过）；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和赛娜在同一个 PR（claude/senna-ppu）。
