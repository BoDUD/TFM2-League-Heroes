# 烬：全部动作逐帧重画（给 Codex 的提示词）

> 烬的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，55 × 74 格，每格一个像素）是用户通过的那张（就是你画的 `jhin-A.png`，按约 15.3 px 一格读回，PPU 1.80；`refs/design_picture.png` 是它的原图）：**深紫色的兜帽**、**白色的面具**和**粉色的眼睛**；**白金色的披风**和**金色的花纹**、**玫红色的里衬**；**深紫色的衣服**；**金色铠甲的手臂**、**缠着青色的手杖枪**、**象牙色枪托、深灰色枪管的长枪「低语」**；**金色的护腿和靴子**。请把他的**每个动作每一帧都重新画整个人**。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和别的帧一模一样的 10 帧不用再画，所以一共 46 帧（38 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **两只手和枪照浅色人影**：手杖枪、长枪「低语」、Q 的手雷、R 的大炮，举起、瞄准、耍枪、扔出去，照浅色人影；枪和设计图一样长（R 的大炮照浅色人影）；不画枪口火光、子弹、花瓣、烟，**眼睛的粉色只画在面具上**；普攻、第四枪、Q、W、R 开炮的浅色人影是旧版不带火光的身体格，**火光不要画**。
> - **`attack`、`attack4`、`skill`、`skill2`、`ult_shot` 的浅色人影是旧版不带特效的身体格**（旧版那几帧上叠着特效，这里只给身体），照它画。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：**两条腿照浅色人影逐帧画**——哪条腿在前、哪条在后，哪只脚平踩在地面线上、哪只抬起，**每帧都照它**（`refs/old_run_*.png` 里近侧腿颜色亮、远侧腿颜色暗）。**两条腿要轮流在前，不要每帧都是同一条腿在前**（之前泰隆和赛娜跑步都犯过这个错，只好重画）。他旧版跑步是交叉步，脚的位置每帧照浅色人影。
> - 跑步 `run_*`：快步往前走，金色的手拿着手杖枪、另一只手垂着拿「低语」，**两条腿照浅色人影逐帧轮流迈步**。
> - 普攻 `attack_*`：举起「低语」（第 2 帧），往前瞄准、手臂伸直（第 3 帧），后坐力把枪往上一抬（第 4–5 帧；第 1、6 帧 = 设计图）。
> - 第四枪 `attack4_*`：蹲下、披风甩开（第 1 帧），把「低语」举过头顶耍一圈（第 2 帧），蹲低瞄准（第 3 帧），开枪、手臂伸直（第 4–5 帧；第 6 帧 = 设计图）。
> - Q 曼舞手雷 `skill_*`：举起握着手雷的金色拳头（第 1–2 帧），往前一甩扔出去、手臂伸直（第 3–4 帧），收回（第 5 帧；第 6 帧 = 设计图）。
> - W 致命华彩 `skill2_*`：蹲低（第 1 帧），起身把手杖枪往上一挥（第 2 帧），举过头顶耍一圈（第 3 帧），放下来（第 4 帧），端平在肩上往前瞄准（第 5–7 帧；第 8 帧 = 设计图）。
> - R 完美谢幕 `ult_*`：蹲低架炮（第 1 帧），把大炮举过头顶（第 2 帧），跪下、大炮扛在肩上往前瞄准（第 3–4 帧）。
> - R 瞄准 `ult_aim_*`：跪着扛炮往前瞄准（第 2–4 帧；第 1 帧 = R 第 4 帧）。
> - R 开炮 `ult_shot_*`：跪着瞄准（第 1 帧），后坐力把炮往上一抬（第 2 帧），放回来（第 3 帧；第 4 帧 = 第 1 帧）。
> - 受击 `hit_*`：被打得往后一顿（第 1 帧；第 2 帧 = 设计图）。
> - 死亡 `dead_*`：被打中、弓着身子（第 1 帧），往后踉跄、「低语」从手里飞出去（第 2 帧），跪倒（第 3–4 帧），往前垮下去（第 5 帧），脸朝下趴在地上（第 6 帧；第 7–8 帧 = 第 6 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的烬；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时的高度（74 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：兜帽顶到面具下巴约 19 格，**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **两只手和枪照浅色人影**：手杖枪、长枪「低语」、Q 的手雷、R 的大炮，举起、瞄准、耍枪、扔出去，照浅色人影；枪和设计图一样长（R 的大炮照浅色人影）；旧版的特效没有画进去。
4. **跑步要换腿**：两条腿照上面逐帧轮流迈步，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 9 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/jhin-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/jhin-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/jhin-actions/HANDOFF.md`（交付说明），再打包成 `outputs/jhin_actions_done.zip`。

## 附图（压缩包 `jhin_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 jhin-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、手和武器在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a masked gunman - a DEEP VIOLET HOOD, a WHITE MASK with PINK EYES, a WHITE-AND-GOLD CAPE with GOLD PATTERNS and a CRIMSON LINING, deep violet clothes, a GOLD-ARMOURED ARM, a CANE GUN wound in TEAL, the long rifle WHISPER (ivory stock, dark grey barrel, gold fittings), GOLD GREAVES AND BOOTS - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 19 squares from the top of his hood to the chin of his mask) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no muzzle flashes, no bullets, no petals, no smoke; the eyes' pink stays on the mask.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the mask, the cape's patterns and the two guns clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **两只手和枪照浅色人影**：手杖枪、长枪「低语」、Q 的手雷、R 的大炮，举起、瞄准、耍枪、扔出去，照浅色人影；枪和设计图一样长（R 的大炮照浅色人影）；旧版的特效没有画进去。
- **跑步两条腿轮流**，跑步两条腿照浅色人影轮流在前，8 帧不是同一个姿势、不是同一条腿一直在前。
- 没有任何特效。
- 最后写 `outputs/jhin-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/jhin_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_diana_hd.py`（读 raw/ 的原图；每帧的缩放取身高、头的大小、身体面积三种量法的中位数，旧帧的身体按旧帧的颜色和贴着描边来认，特效不算）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。被烘焙的 attack、attack4、skill、skill2、ult_shot 按原生身体格的支点读回，特效由烘焙文件重新叠上。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；他站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和螳螂、机器人、莉莉娅在同一个 PR（claude/khazix-ppu）。
