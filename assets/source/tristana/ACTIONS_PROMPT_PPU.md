# 崔丝塔娜：全部动作逐帧重画（给 Codex 的提示词）

> 崔丝塔娜的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，103 × 87 格，每格一个像素）是用户通过的那张（就是你画的 `tristana-v2.png`）：小个子约德尔人，头顶黄铜红框、浅蓝镜片的护目镜，白色蓬发，两只往两边伸出的大尖耳朵（外淡紫、内粉红），淡紫色皮肤、琥珀黄大眼睛，棕皮背心、橄榄绿衣裤、红绑带、棕腰带和皮包、棕色无指手套，**双手在腰的高度横端大炮、炮口朝右**（黄铜木色炮身、蓝灰色喇叭炮口和炮尾），淡紫色光腿和光脚。请把她的**七个动作每一帧都重新画整个人**：跑步、普攻、E / Q、W 火箭跳、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机和跟待机一模一样的帧不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：护目镜、头发、耳朵、脸、衣服、手套、腿脚和大炮的样子都照设计图。
> - **大炮跟着旧版那一帧走**：平时双手在腰的高度横端、炮口朝右；浅色人影把炮口压低、甩起来、骑着它跳、把它丢在地上的帧就照着画。每帧只有一门大炮。
> - 不画任何特效（炮弹、炮口火光、烟雾、爆炸、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、大炮怎么拿（下面提示词的 `<HANDS>`），跑步还写了**每一帧的腿**（`legs`）。
> - 跑步 `run_*`：横端着大炮的约德尔小跑，**两条腿轮流**：第 1、5 帧一只脚踩在胯下、另一条腿往后踢起；第 2、6 帧后脚落地；第 3、7 帧两脚分得最开；第 4、8 帧后腿从身体下面带过来；第 1–4 帧和第 5–8 帧换一条腿。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：往右开炮，后坐力把炮往后一顶，再端平。
> - E / Q `skill_*`：把炮口往右下压低开炮，再端平。
> - W `skill2_*`：用大炮把自己炸上天，抱着炮在空中翻一圈，落地站好。
> - R `ult_*`：把大炮甩起来，往右轰出一发大的，后坐力把炮掀起，再端平。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：大炮掉在地上，她往后踉跄、倒下。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的崔丝塔娜；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从护目镜顶到脚底的高度（87 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：护目镜顶到下巴约 **46 格**（大大的约德尔脑袋，耳朵往两边伸出去），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的护目镜、头发、耳朵、脸、衣服、手套、腿脚和大炮；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **大炮跟着浅色人影**：怎么端、炮口朝哪、有没有丢在地上都照浅色人影；每帧只有一门。
4. **跑步要换腿**：照 `legs` 一帧一帧摆，两条腿轮流，身体有起伏。（之前一位英雄的跑步八帧都是两腿大大分开，像在蹦，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；跳起来、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间、炮管和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 5 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、嘴、护目镜镜片各自成块，不要糊成一团；炮管的金属箍和炮口清楚。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/tristana-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/tristana-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/tristana-actions/HANDOFF.md`（交付说明），再打包成 `outputs/tristana_actions_done.zip`。

## 附图（压缩包 `tristana_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、衣服、大炮、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿和大炮在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、大炮怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a small yordle gunner - a big head with goggles on top (brass and red frames, light blue lenses), fluffy white hair, two huge pointed ears sticking out to the sides (lavender outside, pink inside), lavender skin, large amber eyes; a brown leather vest, an olive top and shorts, red wraps, a brown belt with pouches, brown fingerless gloves; a big CANNON held LEVEL at her hip in both hands, the MUZZLE to the RIGHT (brass and wood body, a flared blue-grey steel muzzle and butt); bare lavender legs and bare feet - 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (top of the goggles to soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the cannon is - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same goggles, hair, ears, face, clothes, gloves, legs, feet and cannon, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 46 squares from the top of the goggles to the chin, the ears as wide as in image 1) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE CANNON AND THE HANDS: <HANDS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no cannonball, no muzzle flash, no smoke, no explosion, no speed lines, no dust.
Always 3/4 view facing right as in image 1; the eyes, the mouth and the lenses each a clear shape, the cannon's bands and muzzle clear.
THE PIXEL GRID: every square the size of the template's (5 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<HANDS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**；护目镜、头发、耳朵、脸、衣服和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **大炮跟着浅色人影**，每帧只有一门。
- **跑步照 `legs`**：两条腿轮流，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/tristana-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/tristana_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_sivir_hd.py`（白底抠图、被围住的白块看四周是不是描边——她的白发、按头的大小找缩放、贴回设计图调色板）；`idle_base` 是设计图（第 3–5 帧下沉一格），`SAME` 里的 `design 0` 帧（普攻 1、技能 5、大招 7、受击 2、W 7）直接用设计图；`idle` / `bp` 由 `hero_reels.json`（skill 0–2、attack 0–3）生成。
- `attack`、`skill`、`ult` 画的是身体帧（6、5、7 帧），炮口特效由 `tristana_bake.json` 照旧烤进去（`Rig.bake`）。
- **逐帧把设计图的头轮廓叠上去**量头的大小；**跑步逐帧写出哪只脚在前**；**逐帧确认大炮的位置**；查碎块、空洞、第二门炮；白发抠白底时别被抠掉。
- 适配：普攻 / E / Q / R 的炮口出手点等特效锚点按新的大炮重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。
