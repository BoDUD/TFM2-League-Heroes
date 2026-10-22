# 凯特琳：动作逐帧重画（给 Codex 的提示词）

> 凯特琳的定稿设计图已经通过（`refs/design.png`，8 倍放大，一格 = 一个像素块；`refs/design_1x.png` 是 1 倍原图）。这次请**每一帧都重新画整个人和她的步枪**，像隔壁 oppi 的凯特琳那样（`refs/oppi_*.png`）：身体随动作倾斜、扭转，腿迈开或下蹲，双手端枪。**姿势照英雄联盟的同一帧**（`refs/league_*.png`）。待机不用画（用设计图）。
>
> 一共 **22 张模板**（`templates/*.png`，每张 1536×1024，一张三帧，每格 512×1024），61 帧：
> - 跑步 `run_1/2/3`（8 帧）
> - 平A `attack_1/2`（6 帧：从腰间放低枪口开火）
> - 爆头 `passive_1/2`（6 帧：端平瞄准的一枪）
> - Q `skill_1/2/3`（8 帧：长时间瞄准后的一枪）
> - W `skill2_1/2`（6 帧：扔出夹子）
> - E `e_1/2/3`（8 帧：开枪的后坐力把她向后弹起，落地）
> - R `ult_1/2/3`（9 帧：单膝跪下长瞄，最后一枪）
> - 受击 `hit_1`（2 帧），死亡 `dead_1/2/3`（8 帧：倒下）
>
> **每一格里**：
> - **灰色横线是地面**，短竖线是她的站位点；**左边的灰色竖条是她站直时从帽顶到脚底的高度**（65 格）。
> - **火柴人是英雄联盟这一帧的骨骼**，已经按她的身材缩放过：**蓝色是近侧的手脚**（画面前面那一侧），**灰色是远侧**，**黑圈是她的头（连帽子和头发）该在的位置和大小**。火柴人只用来定**位置和大小**；具体姿势（身体怎么倾、怎么扭、手脚怎么摆）看 `refs/league_<同名>.png` 里同一帧的渲染图。
> - **两个蓝色小圆圈是她的两只手**，**红线是步枪**（从枪托末端到枪口，长度就是设计图里那把枪的长度）：双手握在枪上，枪顺着红线画。
>
> **人物和步枪必须和定稿设计图一模一样**（`refs/design.png`、`refs/design_palette.png` 全部颜色）：
> - 同样的紫色高礼帽（金饰条、蓝宝石）、同样的脸（两只蓝眼睛一样高）、紫黑长发、白领巾、紫裙、棕色外套和皮带、长靴；**只用调色板里的颜色**。
> - **大小不变**：头和帽子的大小、身体的宽度、**手臂和腿的长度、粗细每一帧都和设计图一样**（不要拉长、压扁或变粗变细；蹲下就是腿弯曲，不是腿变短）；**步枪每一帧都一样长、一样粗**（金色枪身、白护板、两个蓝镜片瞄具）。站直的帧从帽顶到脚底 = 灰色竖条的高度。
> - 四分之三侧身、**脸朝右前方**，和设计图一样（英雄联盟某些帧转身背对镜头或倒向镜头时，也请画成脸朝右前方的样子，只改姿势）。
>
> **画风照 oppi**（`refs/oppi_<动作>.png`，只看动作的画法和力度，**不要照它的衣服、颜色和比例**）：每帧一个清楚的剪影，开枪时身体顶住后坐力，脚踩稳；跑步时前后迈步、长发和外套摆动。
>
> **像素规则**：每块 **6 像素**的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**不画枪口火光、子弹、夹子以外的特效、地面、影子、文字**（W 扔出去的夹子可以画在手里，飞出去以后不画）；模板上的线、圈、火柴人、字、格子边框**全部不要留在交付图里**。
> **背景**：真透明（每个像素透明度只能是 0 或 255）；如果做不到透明，就用**纯白 #FFFFFF 平涂背景，人物外面不要任何光晕或阴影**。
>
> - 交付：`outputs/caitlyn-actions/<模板同名>.png`（22 张，都是 1536×1024，**和模板一样的三格布局**，每帧画在模板对应格子的位置上：脚踩地面线、站位点不变；**不用的格子留空，不要多画**）；原始生成图原样放进 `outputs/caitlyn-actions/raw/`；附 `generation-prompts.txt`（实际用的提示词）；**最后**在同一个文件夹写 `HANDOFF.md`（交付说明），再打包成 `outputs/caitlyn_actions_done.zip`。

## 附图（压缩包 `caitlyn_actions_pack.zip`，解压到一个新的文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（8 倍） | **每张都附，第一张**：人物和步枪的样子、比例、颜色 |
| `refs/design_1x.png` | 定稿设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | 只用这些颜色 |
| `templates/<名>.png` | 三帧的模板 | **第二张**：每帧的位置、大小、双手、步枪 |
| `refs/league_<名>.png` | 英雄联盟同样三帧的渲染（Q 版模型） | **第三张**：每帧的姿势 |
| `refs/oppi_<动作>.png` | oppi 的凯特琳同一种动作（4 倍） | **第四张**：动作画法（只看画法） |
| `sheets.json` | 每张模板是哪个动作的第几帧，配哪张 oppi 图 | 对照 |

oppi 图对应：跑步 → `oppi_run.png`；平A、爆头、W → `oppi_attack.png`；Q → `oppi_skill.png`；E → `oppi_skill2.png`；R → `oppi_ult.png`；受击 → `oppi_hit.png`；死亡 → `oppi_death.png`。

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/league_<名>.png`、`refs/oppi_<动作>.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a sheriff with a tall purple top hat (gold V band, one round blue gem), long dark purple-black hair, two blue eyes, a white ruffled cravat, a purple dress, a brown leather coat and belts, tall brown boots, and a long gold sniper rifle with ivory panels and two blue-lensed scopes, in 3/4 view facing right. Image 2 is a TEMPLATE of animation frames of her <ACTION>, frames <N1>-<N3>: in each 512x1024 cell the grey horizontal line is the ground, the short tick is her standing point, the grey bar on the left is her height when standing straight (hat top to soles); the stick figure is the game's skeleton of that frame fitted to her build (blue = her near arm and leg, grey = the far ones, the black circle = where her head with the hat and hair goes and how big it is); the two small BLUE circles are her hands and the RED line is her rifle from the stock's end to the muzzle. Image 3 is the same frames from the game's 3D animation (a chibi model of the same character): copy each frame's POSE from it - how the body leans and twists, where the arms, legs and rifle go. Image 4 is another pixel artist's version of this character doing this kind of move: copy only HOW IT IS ANIMATED (a strong readable silhouette, the body bracing into the move, feet planted), not its costume, colours or proportions.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if transparency is impossible, a flat pure white background with no glow and no shadow), the SAME three-cell layout as image 2: in each used cell draw the character of image 1 in that frame's pose of image 3, placed and sized by image 2: her soles on the ground line (unless she is in the air), her head where the black circle is and as big, her hands in the blue circles holding the rifle along the red line. Leave unused cells empty.
She and her rifle must be EXACTLY those of image 1 in every frame: the same hat, hair, face with both eyes at the same height, the same colours (image 1's colours only), the same head size, her arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned), the rifle always the same length and thickness. Always the 3/4 view with the face toward the front-right, as image 1, even where the game model turns away.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material, no stray single odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No muzzle flash, no bullets, no effects, no ground, no shadow, no text. Remove every template mark: no lines, circles, stick figures, numbers or cell borders in the result.
```

`<ACTION>` / `<N1>-<N3>` 照 `sheets.json` 的 `action` 和 `frames` 填，例如 `attack_1`：`basic attack, a shot from the hip (attack1)`、`1-3`。
