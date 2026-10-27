# 辛德拉：9 个动作姿势（给 Codex 的提示词）

> 辛德拉的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，54 × 78 格，每格一个像素）是用户通过的那张：英雄联盟的角盔、肩甲、分片裙摆，悬浮在空中。她旧版的动作几乎都是待机那一帧，只有**远侧（画面右边）的手**和**腿**换了几种样子，其余部分（头、脸、头发、身体、裙子、近侧的手）完全不动。所以这次**只画 9 个姿势**（A–I），每个姿势画一张完整的她，其余由我拼成动画。
>
> **最重要的一条：除了这个姿势要改的地方，其余每一格都照抄 `refs/design_1x.png`**——头、角、脸、眼睛、头发、身体、裙子、近侧的手，**一格都不要改**，大小、位置也一模一样。旧版的动作很细微，哪怕脸差一格，动画里也会闪。
>
> `sheets.json` 列出每张模板（`templates/pose_1.png` … `pose_5.png`，每张 1536×1024，**两格**，每格 768 宽，最后一张一格）：每格是哪个姿势、**改哪里**（`change`）。
> - A：远侧的手稍微放低、转一点（悬浮到最高点时）。
> - B：远侧的手抬到肩膀高度，手心朝外。
> - C：远侧的手在腰的高度向右推出去。
> - D：远侧的手抬得更高，过肩。
> - E / F / G：滑行时的三帧：小腿往后弯一点 / 小腿摆起、远侧的手伸出 / 腿收回、远侧的手伸出。
> - H / I：死亡：腿软下去、人往下沉一点 / 坐沉在弯下的腿上、身体塌下来。
>
> **每一格里**：浅色的人影就是这个姿势（旧版那一帧放大到她现在的身高），**照它改手或腿的位置**，其余照设计图；灰色横线是地面（站着的姿势脚尖踩在线上，有的姿势浮高一点、按浅色人影的位置），短竖线是站位点，左边灰色竖条是她从角尖到脚尖的高度（78 格）。

**像素规则**：和设计图同样大小的方块（模板里每格 8 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；**只用设计图的颜色**（`refs/design_palette.png`）；不要渐变、模糊、抗锯齿、发光。不画任何特效（暗黑法球、紫色能量、速度线），不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要缩放、裁剪或重新排版交付图**，原始生成图原样放进 raw/。

- 交付：`outputs/syndra-actions/pose_1.png` … `pose_5.png`（都是 1536×1024，**和模板一样的格子布局**）；原始生成图原样放进 `outputs/syndra-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/syndra-actions/HANDOFF.md`（交付说明），再打包成 `outputs/syndra_actions_done.zip`。

## 附图（压缩包 `syndra_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：除了要改的地方，**照抄它** |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度、每一格的颜色 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/pose_<k>.png` | 两格模板，浅色人影是要摆的姿势 | **第二张**：手 / 腿的位置、大小 |
| `refs/old_pose_<k>.png` | 旧版同样两个姿势的彩色原图（放大） | **第三张**：看清手和腿怎么摆（衣服不照它） |
| `sheets.json` | 每格是哪个姿势、改哪里 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/pose_<k>.png`、`refs/old_pose_<k>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a dark sorceress hovering in the air - a dark purple horned helmet with gold trim and a magenta gem, a pale face with large magenta eyes, long silver-white hair down both sides, gold shoulder armour, a dark purple bodice, plated dark purple skirt panels with gold trim, dark purple stockings and pointed boots, toes pointing down - 3/4 view. Image 2 is a TEMPLATE of <N> pose(s): <POSES>. In each cell the PALE FIGURE is her old animation frame in that pose, scaled to her height; the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height (horn tips to toe). Image 3 is the same old frame(s) in colour: copy ONLY where the hand / the legs are - the old costume is wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 EXACTLY - copy image 1 square for square: the same helmet, horns, face, eyes, hair, body, skirt and near hand, the same size and the same place - and change ONLY what that cell's pose changes: <CHANGES>. At the pale figure's place and size (in some poses she floats a little above the line, as the pale figure does). One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
NO EFFECTS AT ALL: no dark spheres, no purple energy, no speed lines.
THE PIXEL GRID: every square the size of the template's (8 px), on one straight grid; the near-black outline of image 1 around the figure; image 4's colours only; no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, letters or cell borders in the result.
```

`<N>`、`<POSES>`、`<CHANGES>` 照 `sheets.json` 的 `cells`、每格的 `pose` 和 `change` 填（例如 `pose B: her far hand (image right) raised to her shoulder, the palm out`）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **除了要改的手 / 腿，每一格都和设计图一样**：头、角、脸、眼睛、头发、身体、裙子、近侧的手，大小、位置都不变。
- 手 / 腿的位置照浅色人影；只用设计图的颜色；没有任何特效。
- 最后写 `outputs/syndra-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/syndra_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- `tools/art/rig_syndra_hd.py` 用设计图拼每一帧：旧帧对待机 1 的整体平移 × PPU（悬浮上下、R 升起、受击后退、死亡下沉），每帧改变的区域（旧帧和待机 1 的差别：远侧的手 A–D、腿 E–I，按 PPU 放大再外扩几格）从 Codex 画的那个姿势里取（`casts_rengar_hd` 的读法：白底、按头定倍数、换回设计图色板）。她的头发是白色：抠白底时被围住的白块只在四周是描边时才当背景。
- 待机、选人卡轮播由 `hero_reels.py` 照旧（skill2、skill2_e 的帧）；出 1 倍帧用 `ppu_one.py` + `--one-ground`；扫残留像素。
