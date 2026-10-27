# 雷恩加尔（狮子狗）：全部动作逐帧重画（给 Codex 的提示词）

> 雷恩加尔的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，76 × 59 格，每格一个像素）是用户通过的那张：弓背半蹲的野兽猎手，近侧（画面左边）是米黄色的大爪子，远侧（画面右边）握着刀尖暗红的骨质弯刀，尾巴从身后卷到右边。请把他的**八个动作每一帧都重新画整个人**：跑步、普攻、被动扑跳、Q 残忍无情、E 套索打击、W 战争咆哮、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机和 R 不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：灰白色编成粗辫子的大鬃毛，两只米黄色的弯角，灰白的猫科脸、金黄色的独眼和另一只眼上的伤疤、粉色猫鼻子、尖牙和白胡须，棕色皮甲和镶金铆钉的大肩甲，蓝灰色的毛皮手臂，米黄色的爪子，刀尖暗红的骨质弯刀，金色方腰扣和棕色皮短裙，兽脚，带金环的蓝灰色尾巴。
> - 不画任何特效（刀光、套索、咆哮的声波、烟雾、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、手怎么摆（下面提示词的 `<HANDS>`）。
> - 跑步 `run_*`：弓着背的小跑，**两条小腿原地轮流迈步**（用户选的是这种，**不要交叉步**），**身体随步子上下起伏**；8 帧不能是同一个姿势。
> - 普攻 `attack_*`：举起爪子，再往后甩、把弯刀往前砍，然后收回蹲姿。
> - 被动扑跳 `leap_*`：扑向目标，爪子往后甩、弯刀往前刺，落地蹲下。
> - Q `skill_*`：直起身把弯刀举过头顶，再往前下方撕砍。
> - E `skill2_*`：举起爪子把套索往前甩出去（**套索本身不画**）。
> - W `skill_w_*`：双臂张开——爪子往后、弯刀往前——张嘴咆哮。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：踉跄、仰面倒下，最后躺在地上，弯刀掉在身边。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的雷恩加尔；灰色横线是地面，短竖线是站位点，左边灰色竖条是他蹲着站时从角尖到脚底的高度（59 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：鬃毛顶到胡须底约 **33 格**（设计图里的头，角尖比鬃毛顶再高一点），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的鬃毛辫子、角、脸、皮甲、肩甲、爪子、弯刀、腰扣、短裙和尾巴；**体格和设计图一样壮**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **手跟着浅色人影**：爪子一直是近侧的手，弯刀一直在远侧的手里；举起、甩开、刺出照浅色人影画。
4. **跑步要有交替**：两条小腿轮流迈步（不交叉），身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；扑跳、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 手臂和身体之间、两腿之间、尾巴和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 8 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**脸上的眼睛、伤疤、鼻子、嘴和牙各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**（上次的设计图被压成了方形，读不回来）；原始生成图原样放进 raw/。

- 交付：`outputs/rengar-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/rengar-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/rengar-actions/HANDOFF.md`（交付说明），再打包成 `outputs/rengar_actions_done.zip`。

## 附图（压缩包 `rengar_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、衣服、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作和手（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、手怎么摆 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a hulking lion-like beast hunter in a hunched stalking crouch - a big grey-white mane of thick braided locks, two curved cream horns, a pale feline face with one glowing golden eye and a scar over the other, a pink cat nose, fangs and a white beard, brown leather armour with a big gold-riveted pauldron, blue-grey furry arms, a big cream claw on the near hand (image left), a curved cream bone blade with a dark red tip in the far hand (image right), a square gold belt buckle and a brown leather kilt, beast feet with cream claws, a thin blue-grey tail with gold rings curling out behind - 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (tip of the horn to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose, motion and hands - the old costume is wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
He must be EXACTLY image 1 in every frame: the same braided mane, horns, face, armour, pauldron, claw, blade, buckle, kilt and tail, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 33 squares from the top of the mane to the bottom of the beard, the horn tip a little higher) - never smaller, never bigger. The build as heavy as image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE HANDS: <HANDS>
NO EFFECTS AT ALL: no slash trails, no bola, no roar waves, no smoke, no speed lines, no dust.
Always 3/4 view, face toward the front-right as in image 1; the eye, the scar, the nose, the mouth and the fangs each a clear shape.
THE PIXEL GRID: every square the size of the template's (8 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<HANDS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**（鬃毛顶到胡须底约 33 格）；鬃毛、角、脸、衣服和设计图一样，脸朝右前方；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **手跟着浅色人影**：爪子在近侧、弯刀在远侧。
- **跑步两条小腿轮流迈步（不交叉）、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/rengar-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/rengar_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_leesin_hd.py`（白底抠图、按头缩放、贴回设计图调色板），读原始生成图不读 Codex 的导出图；`ult` 和 `idle_base` 由设计图下蹲 / 呼吸做出（旧版 ult = idle_base 第 3、4 帧），`idle` / `bp` 由 `hero_reels.json`（attack 1–3、skill2 1–4）生成；`SAME` / `SAME_DESIGN` 的帧照 `sheets.json`。
- **逐帧把设计图的头轮廓按独眼对齐叠上去**量头的大小；**跑步查小腿轮换和起伏**；查碎块、空洞、第三只手。
- 适配：普攻 / 扑跳出手点、E 套索出手点等特效锚点按新的手重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身帧表、预览；卡兹克彩蛋和草丛扑跳附加包只读精灵，不用改。
