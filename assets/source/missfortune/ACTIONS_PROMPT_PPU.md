# 厄运小姐：全部动作逐帧重画（给 Codex 的提示词）

> 厄运小姐的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，80 × 105 格，每格一个像素）是用户通过的那张（就是你画的 `missfortune-A.png`，`refs/design_picture.png` 是它的原图）：**金边深蓝三角帽**、**长长的红色卷发**、**蓝色眼睛**和红唇；**深蓝短上衣**、**白色大喇叭袖**、露出的腰腹、**金腰带**；**两把金饰手枪**（远侧的垂在大腿边、近侧的端在身前）；**深蓝长靴**。请把她的**七个动作每一帧都重新画整个人**：跑步、普攻、Q、E、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画（她的旧帧没有和待机一模一样的），所以一共 43 帧。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：帽子、头发、脸、衣服、腰带、靴子、两把枪的样子都照设计图。
> - **两把枪照浅色人影**：远侧的枪在远侧手、近侧的枪在近侧手，往前瞄、举向天空、垂着，照浅色人影；**每帧最多两把枪**。
> - 不画任何特效（枪口火光、子弹、硝烟、弹壳都不要）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、两把枪怎么放（下面提示词的 `<GUNS>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：轻快、神气地跑，两手拿着枪，头发和袖子飘起来，**两条腿照浅色人影轮流迈步**：
>   1. 大步：**近侧（颜色亮的）腿**往前（画面右边）伸，远侧腿在后面蹬地。
>   2. 近侧脚落到身下，远侧腿在后面离地。
>   3. 交错：近侧腿踩在胯下；**远侧腿**从身下往前摆，膝盖抬起。
>   4. 远侧腿往前伸准备落地，近侧腿在后面蹬地。
>   5. **换腿**大步：**远侧（颜色暗的）腿**往前伸，近侧腿在后面蹬地。
>   6. 远侧脚落到身下，近侧腿在后面离地。
>   7. 交错：远侧腿踩在胯下；**近侧腿**从身下往前摆，膝盖抬起。
>   8. 近侧腿往前伸准备落地，远侧腿在后面蹬地。
>
>   **第 1 帧和第 5 帧必须看得出是不同的腿在前。**
> - 普攻 `attack_*`：近侧的枪往前瞄准**开火**（第 1–3 帧），再把枪甩到头边、枪口朝天（第 4–6 帧）。
> - Q `skill_*`（一箭双雕）：近侧的枪往前瞄（第 2–3 帧）**开火**，后坐力把枪抬到头边（第 4–6 帧）。
> - E `skill2_*`（枪林弹雨）：两把枪一起举起来，**朝天开火**，两个枪口都在头顶上方（第 2–6 帧）。
> - R `ult_*`（弹幕时间）：叉开腿站稳，**近侧的枪往前连续开火**，远侧的枪举在脑后，每帧随着后坐力晃动。
> - 受击 `hit_*`：被打得往后一顿，两把枪甩开。
> - 死亡 `dead_*`：被打中，踉跄，枪脱手，**跪下**（第 4–6 帧），最后**平趴在地上**（第 7 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的厄运小姐；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从帽顶到脚底的高度（105 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：帽顶到下巴约 **42 格**（深蓝三角帽、红色卷发、蓝眼睛），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的帽子、头发、脸、衣服、腰带、靴子、两把枪；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **两把枪跟着浅色人影**：远侧的在远侧手、近侧的在近侧手；每帧最多两把枪；脱手的帧照浅色人影。
4. **跑步要换腿**：两条腿照上面逐帧轮流迈步，身体有起伏。（上一位英雄泰隆的跑步八帧都是同一条腿在前，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；跪下、趴下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 8 像素，见 `sheets.json` 的 `square`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；帽子的金边、枪的金饰和手指清楚，没有光晕。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/missfortune-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/missfortune-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/missfortune-actions/HANDOFF.md`（交付说明），再打包成 `outputs/missfortune_actions_done.zip`。

## 附图（压缩包 `missfortune_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、帽子、枪、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 missfortune-A） | **每张都附，第五张**：细节（眼睛、红唇、金饰） |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、两把枪在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、两把枪怎么放、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a pirate captain - a WIDE NAVY TRICORN with GOLD trim, long wavy RED HAIR, BLUE EYES and red lips; a short NAVY TOP, big WHITE BELL SLEEVES, a bare midriff, a GOLD BELT; TWO PISTOLS with dark barrels, gold fittings and flared muzzles, one in each hand; tall NAVY BOOTS - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail in the eyes, the lips and the gold fittings. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (the top of the hat to her soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the two pistols are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same hat, hair, face, outfit, belt, boots and pistols, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 42 squares from the top of the hat to her chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<GUNS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no muzzle flash, no bullets, no smoke, no shells.
Always 3/4 view facing right as in image 1; the eyes, the brows and the lips each a clear shape; the hat's gold trim, the pistols' gold fittings and the fingers clear with no glow.
THE PIXEL GRID: every square the size of the template's (sheets.json's square: 8 px), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<GUNS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**；帽子、头发、脸、衣服、靴子和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **两把枪跟着浅色人影**：远侧的在远侧手、近侧的在近侧手；E 两个枪口都朝天；死亡时枪脱手照浅色人影。
- **跑步两条腿轮流**，第 1 帧和第 5 帧换了一条腿在前，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/missfortune-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/missfortune_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_talon_hd.py`（白底抠图；每张的缩放先按整个人的面积量，再乘头的大小——厄运小姐用脸的肤色面积量头，腰腹和手臂也是肤色，只量帽子下面那一块；站着的帧再按旧版同一帧的身高对齐）；读的格子和设计图一样（约 9.75 px 一格的原图密度）。`idle_base` 是设计图（静止，不上下晃）；`idle` / `bp` 由 `hero_reels.json`（attack 2–5 + skill 1–2）生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定（别把两把枪算进“两脚中点”）；她站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**；**逐帧确认两把枪**；查碎块、空洞。
- 适配：普攻 / 技能的特效锚点按新的枪口重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、目标标记附加包、预览；旧版的逐帧补丁 `assets/source/missfortune/modelfix/` 不再用。和泰隆在同一个 PR（claude/talon-ppu）。
