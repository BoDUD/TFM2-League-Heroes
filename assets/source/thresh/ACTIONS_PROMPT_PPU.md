# 锤石：全部动作逐帧重画（给 Codex 的提示词）

> 锤石的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，90 × 99 格，每格一个像素）是用户通过的那张（就是你画的 `thresh-A.png`，`refs/design_picture.png` 是它的原图）：头顶竖着**一条往后上方弯、链节发绿光的锁链**；**骨白的骷髅脸、发亮的绿眼睛**；**深紫黑长袍**、一层层**青铜灰盔甲板**；**远侧手握锁链镰刀**（发淡绿光的弯刃），锁链缠在身上；**近侧手提着绿色灯笼**；破布下摆和深色靴子。请把他的**七个动作每一帧都重新画整个人**：走路、普攻、Q、E、R、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画（他的旧帧没有和待机一模一样的），所以一共 49 帧。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：头顶的锁链、骷髅脸、长袍、盔甲、镰刀、灯笼的样子都照设计图。
> - **镰刀和灯笼照浅色人影**：镰刀一直在**远侧手**，浅色人影把它甩起来、甩出去的帧，**从手到镰刀的锁链一节一节画出来**，长度和弯法和浅色人影一样（甩出去的锁链和镰刀是这一帧身体的一部分，要画）；**灯笼一直在近侧手**，垂在脚边或举起来，照浅色人影。
> - 不画任何特效（灵魂、绿色拖尾、光圈、钩中的光都不要）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、镰刀和灯笼怎么放（下面提示词的 `<GEAR>`），走路还写了脚（`legs`）。
> - 走路 `run_*`：慢慢地、压迫感地往前飘，长袍摆动，镰刀拖在远侧手里，灯笼在近侧手里晃，**下摆下面的两只脚轮流迈步**（第 1–4 帧近侧脚在前，第 5–8 帧远侧脚在前）。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：把镰刀往身后低处甩（第 2–3 帧），**在头顶抡一圈**（第 4 帧），**连着锁链往前甩出去**（第 5 帧，锁链拉得很长伸向画面右边），再抡回头顶（第 6 帧）收回来。
> - Q `skill_*`（死亡判决）：在头顶抡镰刀（第 2–3 帧），往下甩（第 4 帧），**连着锁链笔直往前掷出去**（第 5 帧），再把**灯笼举到身前**（第 6–7 帧），收势。
> - E `skill2_*`（厄运钟摆）：把镰刀往身后远远甩开（第 2 帧），抡到头顶（第 3 帧），**贴着脚边横扫一大圈**（第 4–5 帧），再抡回头顶（第 6–7 帧），收势。
> - R `ult_*`（幽冥监牢）：压低身子（第 2 帧），站起来，**把灯笼高高举过头顶**（第 4–6 帧），再放下来（第 7–8 帧）。
> - 受击 `hit_*`：被打得往后一顿，两只手甩开。
> - 死亡 `dead_*`：被打中，踉跄，往前倒下，最后**平趴在地上**，镰刀连着锁链落在身前，灯笼立在身边的地上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的锤石；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时从锁链尖到脚底的高度（99 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：骨白的骷髅脸约 **13 格高**、头顶的锁链和设计图一样长，**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的锁链、骷髅脸、长袍、盔甲、镰刀、灯笼；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。深色长袍分出 3–4 档深浅，不要糊成一片黑。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **镰刀、锁链、灯笼跟着浅色人影**：镰刀在远侧手、灯笼在近侧手；甩出去的锁链照浅色人影的长度一节一节画出来；每帧只有一把镰刀、一盏灯笼。
4. **走路要换脚**：两只脚照浅色人影轮流迈步，第 1–4 帧和第 5–8 帧换了一只脚在前。（上一位英雄泰隆的跑步八帧都是同一条腿在前，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、趴下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 镰刀、锁链、灯笼和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 8 像素，**普攻和 Q 的模板 7 像素、E 的模板 5 像素**——这几个动作锁链甩得很高，模板缩小了，见 `sheets.json` 的 `square`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光（锁链和灯笼的绿光也只画成实心的格子）。**骷髅脸的眼窝、绿眼睛、牙齿各自成块，不要糊成一团；盔甲板、镰刀刃、灯笼框清楚，没有光晕。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/thresh-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/thresh-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/thresh-actions/HANDOFF.md`（交付说明），再打包成 `outputs/thresh_actions_done.zip`。

## 附图（压缩包 `thresh_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、锁链、镰刀、灯笼、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 thresh-A） | **每张都附，第五张**：细节（骷髅脸、绿眼睛、盔甲） |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、脚、镰刀锁链和灯笼在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、镰刀和灯笼怎么放、走路的脚 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a spectral jailer - a tall CHAIN rising from his skull, sweeping up and back, its links glowing green; a PALE BONE SKULL FACE with glowing GREEN EYES and sharp teeth; a long dark purple-black robe with layered BRONZE-GREY ARMOUR plates; a CHAIN SICKLE in his FAR hand, its curved blade glowing pale green; a GREEN LANTERN in his NEAR hand; a ragged hem over dark boots - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail in the skull, the eyes and the armour. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (the top of the chain to his soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, feet and where the sickle, its chain and the lantern are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
He must be EXACTLY image 1 in every frame: the same chain on his head, skull, robe, armour, sickle and lantern, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (the skull face about 13 squares tall, the chain on it as long as in image 1) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). The dark robe in 3-4 readable shades, never one flat black mass.
<GEAR>
THE FEET (walk sheets only): <LEGS>
NO EFFECTS AT ALL: no souls, no green trails, no rings, no glow round the hook.
Always 3/4 view facing right as in image 1; the eye sockets, the green eyes and the teeth each a clear shape; the armour plates, the sickle's blade and the lantern's frame clear with no glow - the green light drawn as solid squares.
THE PIXEL GRID: every square the size of the template's (sheets.json's square: 8 px; attack and Q 7 px, E 5 px), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<GEAR>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是走路的模板删掉 `THE FEET` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**；锁链、骷髅脸、长袍、盔甲和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **镰刀、锁链、灯笼跟着浅色人影**：镰刀在远侧手、灯笼在近侧手，甩出去的锁链一节一节画全；R 第 4–6 帧灯笼举过头顶。
- **走路两只脚轮流**，第 1 帧和第 5 帧换了一只脚在前，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/thresh-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/thresh_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_talon_hd.py`（白底抠图；每张的缩放先按整个人的面积量，再乘头的大小——锤石用骨白骷髅脸的面积量头；站着的帧再按旧版同一帧的身高对齐）；读的格子和设计图一样（约 9.75 px 一格的原图密度）。`idle_base` 是设计图（静止，不上下晃）；`idle` / `bp` 由 `hero_reels.json`（skill 7、6 + skill2 3–4）生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定（别把镰刀和灯笼算进“两脚中点”）；他站在地上（不悬浮）。
- **逐帧量头的大小**；**走路逐帧对脚**；**逐帧确认镰刀、锁链和灯笼**；甩出去的锁链和镰刀是身体的一部分，检查碎块时别删掉。
- 适配：普攻 / 技能的特效锚点按新的手、镰刀和灯笼重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、灯笼附加包 `league_thresh_lantern`、预览。和泰隆在同一个 PR（claude/talon-ppu）。
