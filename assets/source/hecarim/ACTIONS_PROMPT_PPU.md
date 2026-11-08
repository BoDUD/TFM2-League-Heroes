# 赫卡里姆（人马）：全部动作逐帧重画（给 Codex 的提示词）

> 赫卡里姆（人马）的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，131 × 81 格，每格一个像素）是用户通过的那张（就是你画的 `hecarim-A.png`，按约 10.75 px 一格读回，PPU 1.80；`refs/design_picture.png` 是它的原图）：**黑灰色的牛角头盔**、头盔缝里**两只青色的眼睛**和**青色的獠牙纹**；**黑灰色的重甲**、甲缝里**青色的幽光**；近侧手里的**长戟**（深色长杆、银色弯刃）；**黑灰色的马铠**、腰侧**暗红色的布**、**青色幽灵火焰的尾巴**；**四条装甲腿**。请把他的**每个动作每一帧都重新画整个人**。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和别的帧一模一样的 3 帧不用再画，所以一共 46 帧（44 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **长戟照浅色人影**：深色长杆、银色弯刃，和设计图一样长，拿在近侧手里——举着、抡、转、往前刺、举过头顶或者掉在地上，都照浅色人影；**青色幽灵火焰的尾巴**和暗红色的布照浅色人影；不画幽灵骑兵、暗影、刀光、尘土，**青光只画在盔甲缝和眼睛里**。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
>
> **跑步 `run_*` 的四条腿逐帧照浅色人影画**（`legs` 里也写了）：前面一对、后面一对各自哪条在前、哪条在后，哪只蹄子踩在地面线上、哪只抬起，**每帧都照它**（`refs/old_run_*.png` 里近侧的腿颜色亮、远侧的腿颜色暗）。**前后两对腿都要轮流迈步，不要每帧都一样**；四条腿都要在，和设计图一样长、一样粗，蹄子是深色的。
>
> - 跑步 `run_*`：四条装甲腿奔驰，长戟举在身前、戟刃在画面右上方，青色幽灵火焰的尾巴在身后飘，**四条腿照浅色人影逐帧迈步**。
> - 普攻 `attack_*`：把长戟举在身前、戟刃高高地在画面右上方（第 1 帧），竖直举过头顶（第 2 帧），从头顶往后抡、戟杆横着、戟刃指向画面左边（第 3 帧），整个身子往前下方扑出去、拉得又低又长，长戟劈到右下方、戟刃快碰到很远的地面，尾巴在身后甩起（第 4 帧），压低收回来、长戟扛回肩后（第 5 帧），站好、长戟举在身前（第 6 帧）。
> - Q 暴走 `skill_*`：抡着长戟绕身子转一圈——扛到肩后、戟刃在左上方（第 1 帧），往身后画面左边平伸（第 2–3 帧），往前绕到身前、平着指向画面右边（第 4 帧），往右上方挥起（第 5 帧），又抡回头顶、戟刃在左上方（第 6 帧）——竖着拿在身边站好（第 7 帧）。
> - E 毁灭冲锋·冲锋 `skill2_*`：压低身子往前长距离冲锋，身子往前拉长，长戟像骑枪一样平端在身前、戟刃在画面右边，尾巴在身后飘，**四条腿照浅色人影逐帧奔驰**。
> - E 毁灭冲锋·砍中 `skill2_hit_*`：前身扬起、长戟往后举过头顶（第 1 帧），后腿站立扬得更高、前蹄抬起、长戟横举在头顶（第 2 帧），往前砸下来、长戟往右下方刺下去（第 3 帧），站好、长戟往身前下方指着（第 4 帧）。
> - R 暗影冲锋 `ult_*`：压低身子、长戟低低地端在身前、戟刃快碰到画面右边的地面（第 1–2 帧），后腿站立高高扬起、长戟往头顶竖直举起（第 3 帧），往前冲锋奔驰、长戟平端在身前、尾巴在身后飘（第 4–7 帧）。
> - 受击 `hit_*`：往后一震（第 1 帧；第 2 帧 = 第 1 帧）。
> - 死亡 `dead_*`：长戟竖着插在身边的地上，他身子一沉（第 1 帧），痛得扬起前身、两臂甩起（第 2 帧），扬得更高、头往后仰（第 3 帧）；长戟倒在身前的地上，他踉跄（第 4 帧），往下沉、腿弯下去（第 5 帧），瘫倒在地上、腿收在身下、长戟在旁边（第 6 帧；第 7–8 帧 = 第 6 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的赫卡里姆（人马）（跑步的腿照上面写的）；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时的高度（81 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头盔顶到青色獠牙纹下沿约 30 格（上面的角另算），**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **长戟照浅色人影**：深色长杆、银色弯刃，和设计图一样长，拿在近侧手里——举着、抡、转、往前刺、举过头顶或者掉在地上，都照浅色人影；**青色幽灵火焰的尾巴**和暗红色的布照浅色人影；旧版的特效没有画进去。
4. **跑步四条腿照浅色人影逐帧迈步**：前后两对腿都要轮流迈步，不要每帧都一样，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间、武器和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 9 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓一圈 2 格宽的近黑描边（和设计图一样）；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**头盔缝里的两只眼睛各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/hecarim-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/hecarim-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/hecarim-actions/HANDOFF.md`（交付说明），再打包成 `outputs/hecarim_actions_done.zip`。

## 附图（压缩包 `hecarim_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 hecarim-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、手和武器在哪（衣服不照它；跑步的腿照上面写的） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a spectral centaur knight - a HORNED BLACK-GREY HELMET with TWO GLOWING CYAN EYES and a CYAN GRIN, BLACK-GREY PLATE ARMOUR with SPECTRAL CYAN light in its seams, a LONG HALBERD with a dark shaft and a CURVED SILVER BLADE in his near hand, a HORSE BODY in BLACK-GREY BARDING, a DARK CRIMSON CLOTH at his flank, a CYAN GHOST-FIRE TAIL, FOUR ARMOURED LEGS - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 30 squares from the top of his helmet to the bottom of its cyan grin, the horns above it) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only - as written): <LEGS>
NO EFFECTS AT ALL: no ghost riders, no shadows, no slashes, no dust; the cyan light stays inside his armour's seams and his eyes.
Always 3/4 view facing right as in image 1; the two cyan eyes each a clear shape; the helmet's horns, the halberd's blade, the four legs and the tail's flames clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; a 2-square near-black outline around the figure as in image 1; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **长戟照浅色人影**：深色长杆、银色弯刃，和设计图一样长，拿在近侧手里——举着、抡、转、往前刺、举过头顶或者掉在地上，都照浅色人影；**青色幽灵火焰的尾巴**和暗红色的布照浅色人影；旧版的特效没有画进去。
- **跑步四条腿轮流**：照浅色人影逐帧画，前后两对腿都换过，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/hecarim-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/hecarim_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_xayah_hd.py`（第 6 批：读 raw/ 的原图，透明底按半透明度 128 抠图、白底按白色抠；每帧的缩放按叠合法 `--fits`：画稿叠到模板的浅色人影上取重合最好的比例，重合差时取身高、头、面积的中位数）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；他站在地上（不悬浮）。
- **逐帧量头框的大小**（不只量头发的面积），在评审 GIF 里逐帧比新旧两边的大小变化（洛那次：头画大一号只能交 Codex 重画头，不能整帧缩放）；**跑步逐帧对腿**（四条腿照旧版逐帧换）；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和奥拉夫、伊泽瑞尔、雷克顿（鳄鱼）在同一个 PR（ppu-b7）。
