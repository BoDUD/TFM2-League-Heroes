# 贝蕾亚：全部动作逐帧重画（给 Codex 的提示词）

> 贝蕾亚的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，110 × 135 格，每格一个像素）是用户通过的那张（就是你画的 `briar-A.png`，`refs/design_picture.png` 是它的原图）：**黑铁大刑枷**套在脖子上（金色铆钉、尖角、顶上红宝石），**两只手腕锁在刑枷左右两端**，手从两端伸出来；白色乱发带粉红，浅蓝色眼睛；黑色短衣溅着红色、金扣；光腿，小腿缠着黑绑带，露着脚趾。请把她的**十一个动作每一帧都重新画整个人**：跑步、普攻、Q、W、E 尖叫、R（起跳、飞行、落地）、受击、死亡、吸血啃咬。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；和待机一模一样的帧也不用画（`sheets.json` 的 `same`），所以一共 56 帧。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：刑枷、头发、脸、衣服、腿、绑带的样子都照设计图。
> - **刑枷一直锁着她**：每帧都套在脖子上、两只手腕锁在两端，跟着浅色人影倾斜、转动；**Q 第 3–5 帧和 R 飞行时她头朝前平着飞，刑枷在最前面**。每帧只有一副刑枷。
> - 不画任何特效（血雾、冲击波、尖叫的声波、速度线、尘土），**只有吸血啃咬第 1–3 帧嘴边几滴红色的血、第 4–7 帧下巴上的血**照旧版画。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、刑枷和手怎么放（下面提示词的 `<PILLORY>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：野性地往前跑，刑枷扛在肩上，两只手在两边，**两条腿照浅色人影轮流迈步**，头发跳动。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：蹲下，往右前方低低地扑出去咬（第 3–4 帧身体在空中伸直，后腿往后蹬），再落地站好。
> - Q `skill_*`（头槌冲撞）：蹲下，**头朝前平着飞出去**（第 3–5 帧，刑枷在最前面），落地。
> - W `skill2_*`（嗜血狂乱）：低低地蹲着，再站起来叉开腿摇晃，准备扑出去。
> - E `skill2_scream_*`（寒意尖叫）：站稳，**张大嘴尖叫**，往前探身（第 2–3 帧），再站直。
> - R `ult_*`（必死之局）：抬膝**往前高踢**（第 3 帧），踩下来蹲低，准备飞出去。
> - R 飞行 `ult_fly_*`：往右**平着飞**，刑枷在前，两腿拖在后面。
> - R 落地 `ult_land_*`：落地时蹲得很低，再站起来。
> - 受击 `hit_*`：被打得往后一顿，眼睛紧闭。
> - 死亡 `dead_*`：被打中，踉跄，跪下，往前倒，最后平趴在地上，刑枷还套着。
> - 吸血啃咬 `attack_fx1_*`：往前扑出去咬（第 1–3 帧，嘴边几滴血），落地站好，下巴上有血（第 4–7 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的贝蕾亚；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从刑枷顶到脚底的高度（135 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头发顶到下巴约 **36 格**（白色乱发、浅蓝色眼睛），**刑枷的大小也和设计图一样**，**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的刑枷、头发、脸、衣服、腿、绑带；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **刑枷跟着浅色人影**：一直套在脖子上、两只手腕锁在两端；飞的帧刑枷在最前面；每帧只有一副刑枷。
4. **跑步要换腿**：两条腿照浅色人影轮流迈步，身体有起伏。（之前一位英雄的跑步八帧都是两腿大大分开，像在蹦，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；蹲下、飞起、趴下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、刑枷和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 6 像素，**Q 的模板 5 像素**——Q 飞得很宽，模板缩小了，见 `sheets.json` 的 `square`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；刑枷的铆钉、尖角、红宝石和手指清楚，没有光晕。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/briar-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/briar-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/briar-actions/HANDOFF.md`（交付说明），再打包成 `outputs/briar_actions_done.zip`。

## 附图（压缩包 `briar_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、刑枷、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 briar-A） | **每张都附，第五张**：细节（眼睛、铆钉、手指） |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、刑枷和手在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、刑枷和手怎么放、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a wild girl with a big DARK IRON PILLORY locked round her neck - a wide black iron frame with gold studs, spikes and edging and a red gem on top - BOTH WRISTS LOCKED in its two ends, her hands sticking out; messy white hair touched with pink, pale blue eyes, an open mouth; a short black outfit splashed with red with a gold buckle; bare legs with black wraps round the shins and bare toes - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail in the eyes, the studs and the fingers. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (the top of the pillory to her soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the pillory and the hands are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same pillory, hair, face, outfit, legs and wraps, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 36 squares from the top of her hair to her chin), the pillory the same size too - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE PILLORY AND THE HANDS: <PILLORY>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no blood mist, no shockwaves, no scream waves, no speed lines, no dust - only the Snack's few blood drops at her mouth where the pale figure has them.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the studs, the spikes, the red gem and the fingers clear with no glow.
THE PIXEL GRID: every square the size of the template's (sheets.json's square: 6 px, Q's sheets 5 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<PILLORY>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和刑枷都和设计图一样大**；头发、脸、衣服、腿和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **刑枷跟着浅色人影**：一直锁着脖子和两只手腕，每帧一副；Q 第 3–5 帧和 R 飞行时刑枷在最前面。
- **跑步两条腿轮流**，8 帧不是同一个姿势。
- 没有特效，只有吸血啃咬的几滴血。
- 最后写 `outputs/briar-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/briar_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_sona_hd.py`（白底抠图；每张的缩放先按整个人的面积量，再乘头的大小 `--heads`；站着的帧再按旧版同一帧的身高对齐）；读的格子和设计图一样（约 8.5 px 一格的原图密度）。`idle_base` 是设计图（静止，不上下晃）；`SAME` 里的帧（普攻、Q、E 尖叫、R、R 落地的最后一帧，受击 2）就是设计图；`idle` / `bp` 由 `hero_reels.json`（skill2_scream 0–1、skill2 2–4）生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定（别把刑枷的两端算进“两脚中点”）；她站在地上（不悬浮）。
- **逐帧量头的大小**（白发和脸）；**跑步逐帧对腿**；**逐帧确认刑枷**；查碎块、空洞、第二副刑枷；吸血啃咬的血滴是单独的小块，检查碎块时别当成杂点删掉。
- `attack_fx1` 是技能在她身上播放的身体动画（吸血啃咬），和别的动作一样进 hd_ 帧。
- 适配：普攻 / 技能的特效锚点按新的头和刑枷重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。装游戏前先合进最新 main，版本号接着游戏里现装的往上加。
