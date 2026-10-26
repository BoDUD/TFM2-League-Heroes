# 薇恩：全部动作逐帧重画（给 Codex 的提示词）

> 薇恩的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，85 × 102 格，每格一个像素）是用户通过的那张：站着，脸朝右前方，红披风往身后飘，背后的大弩高过头顶，近侧（画面左边）前臂上是带红宝石的银色腕弩。请把她的**九个动作每一帧都重新画整个人**：跑步、普攻、强化普攻、Q 翻滚（向前）、Q 翻滚（向后）、E 恶魔审判、R 终极时刻、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画，和待机一样的帧也不用画（`sheets.json` 里已经去掉了）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：黑紫色高马尾和红白发圈，红墨镜，深红嘴唇，红色高立领，深蓝灰紧身衣和银色肩甲、护膝，棕色皮带，近侧前臂的银色腕弩（红宝石），背后银色弩臂、棕色弩身的大弩，深色高跟长靴，撕破下摆的红披风。
> - 不画任何特效（弩箭、箭光、烟雾、翻滚的残影、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、两把弩怎么拿（下面提示词的 `<WEAPONS>`）。
> - 跑步 `run_*`：轻快的女猎手跑步，披风往后飘。**左右腿每半圈要明显地交换**（一会儿左脚在前、一会儿右脚在前），**身体随步子上下起伏**；8 帧不能是同一个姿势。
> - 普攻 `attack_*`：抬起**近侧前臂的腕弩**对准目标射一箭，再放下。
> - 强化普攻 `attack_q_*`：压低身子稳住，用腕弩往前射，再站起来。
> - Q 翻滚 `skill_*`：往前缩成一团翻一个跟斗，蹲着起身。
> - Q 向后翻滚 `skill_back_*`：倒地往后滚，再弹起来。
> - E 恶魔审判 `skill2_*`：从背后取下**大弩**，双手端平往前射，再甩回肩后。
> - R 终极时刻 `ult_*`：从背后取下**大弩**，双手端平指向前方。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：踉跄、倒下，最后躺在地上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的薇恩；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站直时从最高处（背后大弩的尖）到脚底的高度（102 格）。

**最重要的六条：**

1. **头的大小每一帧都和设计图一样**：头顶到下巴约 **20 格**，马尾再往上约 **7 格**（设计图里的头），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的马尾、墨镜、立领、衣服、银甲、皮带、披风和靴子；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **腕弩永远在近侧前臂上**（设计图里画面左边那只手臂），**不能换到另一只手**。普攻时伸向目标的那只手就是戴腕弩的近侧手臂，画在身体前面；远侧手臂留在后面。
4. **大弩**：E 和 R 里浅色人影端着长弩的帧，大弩在她**双手**里（背上就没有了）；其他帧大弩都背在背上，和设计图一样从近侧肩后高过头顶。
5. **跑步要有交替**：两条腿轮流在前，身体有起伏。
6. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；翻滚、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 手臂和身体之间、两腿之间、弩和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 7 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**墨镜、嘴、下巴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/vayne-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/vayne-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/vayne-actions/HANDOFF.md`（交付说明），再打包成 `outputs/vayne_actions_done.zip`。

## 附图（压缩包 `vayne_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、衣服、比例、头的大小、颜色、两把弩 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作和弩怎么拿（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、两把弩怎么拿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a night huntress - black-purple hair in a high ponytail with a red-and-white band, red sunglasses, deep red lips, a red high collar, a dark navy-slate bodysuit with silver shoulder and knee armour, brown leather straps, a silver WRIST CROSSBOW with a red gem on her NEAR forearm (image left), a BIG crossbow (silver limbs, brown stock) on her back rising above her head behind the near shoulder, dark high-heeled boots, a long red cape with a torn hem flowing back - standing, 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (top of the big crossbow to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose, motion and how the crossbows are held - the old costume is wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar.
She must be EXACTLY image 1 in every frame: the same ponytail, glasses, collar, suit, armour, straps, cape and boots, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 20 squares from the top of the head to the chin, the ponytail about 7 more above) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE CROSSBOWS: <WEAPONS>
NO EFFECTS AT ALL: no bolts, no arrow light, no smoke, no afterimages, no speed lines, no dust.
Always 3/4 view, face toward the front-right as in image 1; the glasses, the mouth and the chin each a clear shape.
THE PIXEL GRID: every square the size of the template's (7 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<WEAPONS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- **每帧的头和设计图一样大**（头顶到下巴约 20 格、马尾再高约 7 格）；马尾、墨镜、衣服和设计图一样，脸朝右前方；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **腕弩每帧都在近侧前臂上**；E、R 端大弩的帧大弩在双手里，其他帧在背上。
- **跑步两腿轮流在前、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/vayne-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/vayne_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_leesin_hd.py`（白底、按头定缩放，墨镜当头的锚点），或交付图有 export-log 时按每格自己的格子原点读回（`casts_draven_hd.py`）；`SAME_DESIGN` 的帧和 `idle_base` 用设计图。
- **逐帧把设计图的头轮廓按墨镜对齐叠上去**量头的大小；**逐帧查腕弩在哪只手**（Codex 在抬手、翻滚的帧容易换手）；**跑步查换腿和起伏**；查碎块、空洞。
- 适配：ORIG_PPU vayne 2.55 → RESTYLE ppu 2.2（用户定的）；弩箭出手点（`vayne_fx_anchors.json`：腕弩、大弩口）按新的手重新定位；头像截取点、选人卡偏移（待机顶到 -28 以上要设）；待机 / 选人卡轮播（`hero_reels.json`）；俄洛伊灵魂、佛耶戈附身帧表、预览。
