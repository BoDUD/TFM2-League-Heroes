# 卢锡安：全部动作逐帧重画（给 Codex 的提示词）

> 卢锡安的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，111 × 93 格，每格一个像素）是用户通过的那张：英雄联盟的样子，近侧（画面左边）的手把枪竖举在肩旁，远侧（画面右边）的手把枪平端向前。请把他的**九个动作每一帧都重新画整个人**：跑步、普攻、被动（光明哨兵，双枪连射）、Q 透体圣光、E 冷酷追击（向前冲）、E 向后翻、R 圣枪洗礼、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画，和待机一样的帧、和别的帧一样的帧也不用画（`sheets.json` 里已经去掉了）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：编辫的短发、绿眼睛，银白长外套和金边银护肩，黑色胸甲，棕腰带金扣，黑裤和带银甲的黑靴，白色长衣摆（淡紫衬里），深棕手套，两把白金色、带青蓝光符文的大手枪。
> - 不画任何特效（枪口火光、光束、子弹、烟、速度线、尘土）——旧版有几帧画了枪口火光，**新的一律不画**。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、枪怎么拿（下面提示词的 `<WEAPONS>`）。
> - 跑步 `run_*`：枪手的跑步，衣摆往后飘。**左右腿每半圈要明显地交换**（一会儿左脚在前、一会儿右脚在前），**身体随步子上下起伏**；8 帧不能是同一个姿势。
> - 普攻 `attack_*`：朝目标开枪，再回到架势。
> - 被动 `passive_*`：双枪先后各开一枪。
> - Q `skill_*`：站稳，双枪向前射出一道长光束（**不画光束**）。
> - E `skill2_*`：贴地往前快速冲刺（身体几乎放平），然后站起来开枪。
> - E 向后 `skill2_back_*`：往后翻滚躲开，再站起来开枪。
> - R `ult_*`：站稳，双枪向前连续射击。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：踉跄、倒下，最后躺在地上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的卢锡安；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站直时从竖举的枪口到脚底的高度（93 格）。

**最重要的六条：**

1. **头的大小每一帧都和设计图一样**：头顶到下巴约 **20 格**（设计图里的头），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的发型、外套、护肩、胸甲、衣摆、裤子和靴子；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **两把枪每帧一只手一把**：近侧的手（设计图里竖举的那只）一直拿它的枪，远侧的手一直拿它的枪，**不能两把都在一只手里、不能交换、不能丢掉**；枪的形状、大小、颜色和设计图一样，枪口朝向照浅色人影。
4. **跑步要有交替**：两条腿轮流在前，身体有起伏。
5. **不画特效**：没有枪口火光、光束、子弹、烟。
6. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；冲刺、翻滚、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 手臂和身体之间、两腿之间、枪和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 7 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、鼻子、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/lucian-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/lucian-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/lucian-actions/HANDOFF.md`（交付说明），再打包成 `outputs/lucian_actions_done.zip`。

## 附图（压缩包 `lucian_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、衣服、比例、头的大小、颜色、两把枪 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作和枪怎么拿（衣服不照它，火光不画） |
| `sheets.json` | 每张模板是哪个动作的第几帧、枪怎么拿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): League of Legends' Lucian - dark brown skin, short hair with tight braids along the scalp, green eyes, a long silver-white coat with gold-trimmed silver shoulder armour, a black chest plate, a brown belt with a gold buckle, black trousers, black boots with silver plates, long white coat tails with a lavender lining, dark brown gloves, and two big white-and-gold RELIC PISTOLS with cyan runes - the near hand (image left) holding one upright by the shoulder, the far hand pointing the other forward; 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (raised muzzle to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose, motion and how the pistols are held - the old costume is wrong, and their muzzle flashes are NOT to be drawn. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar.
He must be EXACTLY image 1 in every frame: the same hair, coat, shoulder armour, chest plate, tails, trousers, boots, gloves and pistols, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 20 squares from the top of the head to the chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE PISTOLS: <WEAPONS>
NO EFFECTS AT ALL: no muzzle flash, no light beam, no bullets, no smoke, no speed lines, no dust.
Always 3/4 view, face toward the front-right as in image 1; the eyes, brows, nose and mouth each a clear shape.
THE PIXEL GRID: every square the size of the template's (7 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<WEAPONS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- **每帧的头和设计图一样大**（头顶到下巴约 20 格）；衣服和设计图一样，脸朝右前方；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **两把枪每帧一只手一把**，没有交换、没有丢；枪的样子和设计图一样。
- **跑步两腿轮流在前、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效（包括枪口火光）。
- 最后写 `outputs/lucian-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/lucian_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_vayne_hd.py`（白底、按头定缩放：设计图的头滑着比；跑步按头摆一列）；`SAME_DESIGN` 的帧和 `idle_base` 用设计图，`skill2_back` 5–7 用 `skill2` 5–7。
- **逐帧量头的大小**；**逐帧查两把枪在哪只手**（Codex 在抬手、冲刺、翻滚的帧容易换手或丢枪）；**跑步查换腿、相位和头的起伏**；查碎块、空洞。
- 适配：子弹出手点（`lucian_fx_anchors.json`）按新的枪口重新量；旧版烤在帧里的枪口火光没了，看要不要做成特效；头像截取点、选人卡偏移；待机 / 选人卡轮播（`hero_reels.json`）；俄洛伊灵魂、佛耶戈附身帧表、预览。
