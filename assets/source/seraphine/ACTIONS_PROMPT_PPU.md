# 萨勒芬妮：全部动作逐帧重画（给 Codex 的提示词）

> 萨勒芬妮的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，67 × 101 格，每格一个像素）是用户通过的那张（就是你画的 `seraphine-A.png`，按约 11.2 px 一格读回，PPU 2.20；`refs/design_picture.png` 是它的原图）：**粉红色的长发**和头顶**翘起的发卷**；**青色的耳机饰件**；**蓝色的眼睛**（一只眨着）；**白色的上衣**、**深蓝色的胸衣**和**金色的饰边**；**白色的袖子和手套**；**蓝色的短裙**、**青色和粉色的裙片**；**白色的长袜**、**金棕色的鞋**；脚下的**浮空舞台**（金色和青色的台子、中间粉色的屏幕）。请把她的**每个动作每一帧都重新画整个人**。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和别的帧一模一样的 19 帧不用再画，所以一共 23 帧（15 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **两只手照浅色人影**：白手套举起、指向、挥动照浅色人影；**脚下的浮空舞台每帧都在**、和设计图一样大（死亡时她从舞台上摔下来，舞台照浅色人影的位置）；不画音符、声波、回音、发光，**舞台的屏幕不往外发光**。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
>
> **滑行 `run_*`**：**她不走路**：浮空舞台载着她滑行——**每一帧双脚都踩在舞台上**，只有头发、裙子和手照浅色人影动。
>
> - 滑行 `run_*`：**站在浮空舞台上滑行，不走路**：双脚一直踩在舞台上，长发和裙子往后飘（第 1–3 帧；第 4–8 帧 = 第 2、1、2、3、2 帧）。
> - 普攻 `attack_*`：（第 1 帧 = 设计图）举起近侧的手（第 2–3 帧），手臂往前伸直指着前方（第 4–5 帧），收回来（第 6 帧）。
> - Q 高音 `skill_*`：（第 1 帧 = 设计图）举起近侧的手（第 2 帧；第 3 帧 = 普攻第 3 帧），手臂往前上方一挥（第 4 帧），往前指（第 5 帧；第 6 帧 = 普攻第 6 帧）。
> - E→W 节拍顿挫·环绕声 `skill2_*`：（第 1 帧 = 设计图，第 2 帧 = 普攻第 2 帧）手臂往前伸直（第 3 帧；第 4 帧 = Q 第 5 帧），手收到胸前（第 5 帧），往前上方一挥（第 6 帧；第 7 帧 = Q 第 5 帧，第 8 帧 = 普攻第 6 帧）。
> - R 安可 `ult_*`：往前指（第 1 帧），双手收拢（第 2 帧；第 3 帧 = Q 第 4 帧，第 4 帧 = Q 第 5 帧）。
> - 受击 `hit_*`：在舞台上被打得往后一顿（第 1–2 帧）。
> - 死亡 `dead_*`：被打中（第 1–2 帧），往后从舞台上摔下来（第 3–4 帧），躺在舞台旁边的地上、长发散开（第 5 帧；第 6–8 帧 = 第 5 帧）；舞台照浅色人影的位置。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的萨勒芬妮；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时的高度（101 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头顶的头发（发卷不算）到下巴约 27 格，**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **两只手照浅色人影**：白手套举起、指向、挥动照浅色人影；**脚下的浮空舞台每帧都在**、和设计图一样大（死亡时她从舞台上摔下来，舞台照浅色人影的位置）；旧版的特效没有画进去。
4. **滑行不走路**：浮空舞台载着她，双脚每帧都踩在舞台上。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间、武器和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 8 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓一圈 2 格宽的近黑描边（和设计图一样）；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/seraphine-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/seraphine-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/seraphine-actions/HANDOFF.md`（交付说明），再打包成 `outputs/seraphine_actions_done.zip`。

## 附图（压缩包 `seraphine_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 seraphine-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、手和武器在哪（衣服不照它；跑步的腿照上面写的） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a young pop star on a small floating stage - LONG FULL PINK HAIR with a CURL on top, CYAN HEADPHONE ORNAMENTS, BLUE EYES (one winking), a WHITE TOP with a NAVY-BLUE BODICE and GOLD TRIM, WHITE SLEEVES AND GLOVES, a BLUE SKIRT with CYAN AND PINK PANELS, WHITE STOCKINGS, GOLD-BROWN SHOES, the FLOATING STAGE under her feet (gold and cyan, a PINK SCREEN in its middle) - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 27 squares from the top of her hair (the curl above it) to her chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
HER FEET (run sheets only): <LEGS>
NO EFFECTS AT ALL: no music notes, no sound waves, no echoes, no glow; the stage's screen does not glow outward.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the eyes, the curl, the headphones and the stage's screen clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; a 2-square near-black outline around the figure as in image 1; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **两只手照浅色人影**：白手套举起、指向、挥动照浅色人影；**脚下的浮空舞台每帧都在**、和设计图一样大（死亡时她从舞台上摔下来，舞台照浅色人影的位置）；旧版的特效没有画进去。
- **滑行时双脚一直踩在舞台上**，不走路。
- 没有任何特效。
- 最后写 `outputs/seraphine-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/seraphine_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_khazix_hd.py`（读 raw/ 的原图；每帧的缩放按叠合法 `--fits`：画稿叠到模板的浅色人影上取重合最好的比例，重合差时取身高、头、面积的中位数）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；她站在地上（不悬浮）。
- **逐帧量头的大小**；**滑行逐帧对脚**（双脚在舞台上）；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和维迦、基兰、克格莫在同一个 PR（claude/veigar-ppu）。
