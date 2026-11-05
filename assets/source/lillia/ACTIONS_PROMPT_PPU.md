# 莉莉娅：全部动作逐帧重画（给 Codex 的提示词）

> 莉莉娅的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，96 × 139 格，每格一个像素）是用户通过的那张（就是你画的 `lillia-A.png`，按约 8.5 px 一格读回，PPU 2.62；`refs/design_picture.png` 是它的原图）：**粉红色的长发**、**绿色的藤蔓和叶子**、头顶**紫色和青色的花**、**桃色的脸**、**青色的大眼睛**；**绿色叶子做的上衣**；**蓝紫色宝石、橙色弯钩、橙黄色花铃铛和金色叶子的枝条法杖**；**橙色的小鹿身子**、**紫色的斑点**、**奶白色的肚子和白色的小尾巴**；**四条细长的橙色腿**、**紫色的小蹄子**。请把她的**每个动作每一帧都重新画整个人**。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和别的帧一模一样的 14 帧不用再画，所以一共 32 帧（22 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **两只手和枝条法杖照浅色人影**：举着、抡、转、砸地、摇，照浅色人影；枝条和设计图一样长；**四条腿照浅色人影**，细长、蹄子是紫色的；不画梦尘、花瓣、光晕，**宝石的光只画在宝石上，不往外发**。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：**四条腿照浅色人影逐帧画**——前面两条、后面两条各自哪条在前、哪条在后，哪只蹄子踩在地面线上、哪只抬起，**每帧都照它**（`refs/old_run_*.png` 里近侧的腿颜色亮、远侧的腿颜色暗）。**前后两对腿都要轮流迈步，不要每帧都一样**；四条腿都要在、细长，蹄子是紫色的。
> - 跑步 `run_*`：像小鹿一样往前小跑，枝条举着，**四条腿照浅色人影逐帧迈步**。
> - 普攻 `attack_*`：把枝条往后甩过肩（第 1 帧），举起（第 2 帧），往前横扫出去、花铃铛在末端（第 3 帧），往前下方砸到地上（第 4 帧；第 5 帧 = 设计图）。
> - Q 飞花挞 `skill_*`：抡着枝条转一圈：横在身前、铃铛在身后（第 1 帧），举起（第 2 帧 = 普攻第 2 帧），往前扫出去（第 3 帧 = 普攻第 3 帧），砸到身前（第 4 帧），又横在身前（第 5 帧；第 6 帧 = 设计图）。
> - E 流涡种 `skill2_*`：把枝条横着往下压、铃铛在身后低处（第 1 帧），举起（第 2 帧），往前上方一甩抛出种子（第 3 帧；第 4 帧 = 设计图）。
> - W 惊惶木 `skill2_w_*`：枝条横在身前（第 1 帧 = E 第 1 帧），后腿撑地人立起来、枝条高举（第 2–4 帧；第 4 帧 = 第 3 帧），往前把枝条砸到地上（第 5–6 帧；第 7 帧 = 设计图）。
> - R 夜阑谣 `ult_*`：把枝条高高举起摇晃、铃铛跟着晃：举起（第 1–2 帧），往前倾（第 3 帧），再举起（第 4 帧），再往前倾（第 5 帧；第 6 帧 = 设计图）。
> - 受击 `hit_*`：被打得往后一顿（第 1 帧；第 2 帧 = 设计图）。
> - 死亡 `dead_*`：被打中（第 1–2 帧），侧着翻倒、腿往上踢起（第 3 帧），侧躺在地上、枝条掉在身前（第 4 帧；第 5–8 帧 = 第 4 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的莉莉娅；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时的高度（139 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头发顶（不算头上的花）到下巴约 30 格，**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **两只手和枝条法杖照浅色人影**：举着、抡、转、砸地、摇，照浅色人影；枝条和设计图一样长；**四条腿照浅色人影**，细长、蹄子是紫色的；旧版的特效没有画进去。
4. **跑步要换腿**：四条腿照上面逐帧轮流迈步，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 腿之间、手臂和身体之间、枝条和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 6 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/lillia-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/lillia-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/lillia-actions/HANDOFF.md`（交付说明），再打包成 `outputs/lillia_actions_done.zip`。

## 附图（压缩包 `lillia_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 lillia-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、手和武器在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a fawn spirit, a girl above the waist and a fawn below it - LONG PINK HAIR with GREEN VINES AND LEAVES and a VIOLET AND CYAN FLOWER, a PEACH FACE with BIG CYAN EYES, a top of GREEN LEAVES, a BRANCH STAFF with a BLUE-VIOLET GEM, an ORANGE HOOK, an ORANGE-YELLOW FLOWER BELL and a GOLDEN LEAF, an ORANGE FAWN BODY with VIOLET SPOTS, a CREAM BELLY and a WHITE TAIL, FOUR THIN ORANGE LEGS and VIOLET HOOVES - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 30 squares from the top of her hair (the flower on it not counted) to her chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no dream dust, no petals, no glow, no afterimages; the gem's light stays inside the gem.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the branch, the flower bell and the four legs clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **两只手和枝条法杖照浅色人影**：举着、抡、转、砸地、摇，照浅色人影；枝条和设计图一样长；**四条腿照浅色人影**，细长、蹄子是紫色的；旧版的特效没有画进去。
- **跑步两条腿轮流**，跑步四条腿照浅色人影轮流迈步，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/lillia-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/lillia_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_diana_hd.py`（读 raw/ 的原图；每帧的缩放取身高、头的大小、身体面积三种量法的中位数，旧帧的身体按旧帧的颜色和贴着描边来认，特效不算）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；她站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和螳螂、机器人、烬在同一个 PR（claude/khazix-ppu）。
