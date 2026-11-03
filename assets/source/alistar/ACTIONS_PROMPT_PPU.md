# 牛头：全部动作逐帧重画（给 Codex 的提示词）

> 牛头的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，71 × 76 格，每格一个像素）是用户通过的那张（就是你画的 `alistar-A.png`，按约 15 px 一格读回，PPU 1.73；`refs/design_picture.png` 是它的原图）：**一对米白色的弯角**、**红色的眼睛**、**银色的鼻环**；**冰蓝色的水晶鬃毛**从头后沿着背竖起来；**紫色的皮肤**、背上**粉红色的伤疤**；**两条粗壮的手臂**、手腕上**深灰色的宽镣铐**；**棕色的腰带、金色的扣、棕色的围布**；**棕色的蹄子**。请把他的**每个动作每一帧都重新画整个人**。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；`skill_fx1`、`ult_fx1` 是 Q、R 加了特效的副本，也不用画；和别的帧一模一样的 7 帧不用再画，所以一共 42 帧（34 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **两条手臂和拳头照浅色人影**：举起、砸下、张开，照浅色人影；手腕上的镣铐、头上的角和背上的鬃毛和设计图一样；不画尘土、地裂、冲击波，**冰蓝色只画在鬃毛上，不往外发光**。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：**两条腿照下面逐帧轮流迈步**（9 帧；这是之前泰隆和赛娜跑步都没做到、只好重画的地方）：
>   1. 迈步落地：远侧（颜色暗的）腿刚在前面（画面右边）落地，蹄子平踩；近侧（颜色亮的）腿在后面蹬地。
>   2. **远侧腿撑地**：远侧腿踩在胯下；近侧腿弯着往后抬起，蹄子离地。
>   3. 远侧腿还踩在胯下、开始弯；近侧腿从后面往前摆，蹄子离地。
>   4. 交错：两条腿收在身子下面；近侧腿贴着撑地的远侧腿往前过，蹄子刚离地。
>   5. 近侧腿落到胯下接住身体；远侧腿在后面离地。
>   6. **换腿——近侧腿撑地**：近侧腿踩在胯下；**远侧腿**弯着往后上方踢起，蹄子离地很高。
>   7. 近侧腿还踩在胯下、开始弯；远侧腿从后面往下摆。
>   8. 交错：远侧腿贴着撑地的近侧腿往前过，蹄子刚离地。
>   9. 迈步：远侧腿往前（画面右边）伸出去准备落地；近侧腿在后面蹬地。
>
>   **第 2 帧和第 6 帧必须看得出是不同的腿撑地。**
> - 跑步 `run_*`：弓着背往前冲，两臂摆动，**两条腿照上面逐帧轮流迈步**（9 帧）。
> - 普攻 `attack_*`：近侧的拳头高高举起（第 2–3 帧），往身前狠狠砸下（第 4–5 帧），收回（第 6 帧）。
> - Q 大地粉碎 `skill_*`：蹲下（第 1 帧），两只拳头合在一起举过头顶（第 2–3 帧），往地上砸（第 4–5 帧），站起来（第 6 帧）。
> - W 头槌 `skill2_*`：低下头、角朝前往前冲（第 1–4 帧），猛地把头往上一顶（第 5 帧），收回（第 6 帧）。
> - W 撞头 `butt_*`、W→Q 砸地 `slam_*`：全部和上面 W、Q 的帧一模一样，不用画。
> - R 坚定意志 `ult_*`：收身蓄力（第 1–2 帧），站起来（第 3 帧），**挺直身子、正面朝外怒吼，两臂大大张开**（第 4–5 帧），回到站姿（第 6 帧）。
> - 受击 `hit_*`：被打得往后一仰、两臂甩开（第 1 帧），收回（第 2 帧）。
> - 死亡 `dead_*`：被打中往上一仰（第 2–3 帧），往后倒（第 4–5 帧），仰面躺平（第 6–7 帧；第 8 帧 = 第 7 帧，不用画）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的牛头；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时的高度（76 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：角尖到鼻环约 26 格，**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **两条手臂和拳头照浅色人影**：举起、砸下、张开，照浅色人影；手腕上的镣铐、头上的角和背上的鬃毛和设计图一样；旧版的特效没有画进去。
4. **跑步要换腿**：两条腿照上面逐帧轮流迈步，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 9 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/alistar-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/alistar-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/alistar-actions/HANDOFF.md`（交付说明），再打包成 `outputs/alistar_actions_done.zip`。

## 附图（压缩包 `alistar_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 alistar-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、手和武器在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a huge purple minotaur - CREAM CURVED HORNS, RED EYES and a SILVER NOSE RING; an ICY BLUE CRYSTAL MANE rising along his back; PURPLE SKIN with PINK SCARS; two massive arms with WIDE DARK GREY SHACKLES on the wrists; a BROWN BELT with a GOLD BUCKLE and a brown loincloth; BROWN HOOVES - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 26 squares from the tips of his horns to his nose ring) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no dust, no cracks in the ground, no shockwaves, no afterimages; the icy blue stays on the mane.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the horns, the nose ring, the mane and the shackles clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **两条手臂和拳头照浅色人影**：举起、砸下、张开，照浅色人影；手腕上的镣铐、头上的角和背上的鬃毛和设计图一样；旧版的特效没有画进去。
- **跑步两条腿轮流**，第 2 帧和第 6 帧换了一条腿撑地，9 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/alistar-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/alistar_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_diana_hd.py`（读 raw/ 的原图；每帧的缩放取身高、头的大小、身体面积三种量法的中位数，旧帧的身体按旧帧的颜色和贴着描边来认，特效不算）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；他站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和蛮王、派克、布兰德在同一个 PR（claude/alistar-ppu）。
