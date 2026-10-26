# 李青（盲僧）：全部动作逐帧重画（给 Codex 的提示词）

> 李青的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，68 × 86 格，每格一个像素）是用户通过的那张：武僧架势，远侧（画面右边）立掌向前、近侧握拳收在身侧。请把他的**八个动作每一帧都重新画整个人**：跑步、普攻、Q1 天音波、Q2 回音击（飞踢）、E 天雷破（捶地）、R 猛龙摆尾（回旋踢）、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：剃短的头顶上往上翘、向后卷的黑色长辫子（红金发箍），红色蒙眼布（侧面金边蓝宝石）和往后飘的两条布尾，赤裸的肌肉上身和淡淡的伤痕，前臂和手上红白相间的绷带，白色布腰带和金色腰扣、前面垂下的红布，深蓝色宽松长裤，红白相间的绑腿，深色布鞋。
> - 不画任何特效（音波、气浪、龙影、速度线、尘土、碎石）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、手怎么摆（下面提示词的 `<HANDS>`）。
> - 跑步 `run_*`：轻快的武者跑，双拳抬在胸前。**左右腿每半圈要明显地交换**（一会儿左脚在前、一会儿右脚在前），**身体随步子上下起伏**；8 帧不能是同一个姿势。
> - 普攻 `attack_*`：一记快拳打出去，再收回架势。
> - Q1 `skill_*`：蓄力后远侧手掌往前推出（音波从掌心出去，但**不画音波**）。
> - Q2 `q2_*`：往前跃起飞踢，落到目标身上。
> - E `skill2_*`：跳起双拳砸地。
> - R `ult_*`：转身回旋踢，踢的那条腿高高扫起。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：往后踉跄、倒下，最后躺在地上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的李青；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站直时从辫子顶到脚底的高度（86 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：剃短的头顶到下巴约 **17 格**，辫子再往上约 **12 格**（设计图里的头），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的辫子、蒙眼布、宝石、绷带、腰带、红布、裤子和绑腿；**体格和设计图一样壮**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **手跟着浅色人影**：握拳、立掌、张开的手照浅色人影画，近侧的手一直是近侧的手。
4. **跑步要有交替**：两条腿轮流在前，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；跳起、飞踢、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 手臂和身体之间、两腿之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 7 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**脸上的鼻子、嘴、下巴和蒙眼布的边各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/leesin-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/leesin-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/leesin-actions/HANDOFF.md`（交付说明），再打包成 `outputs/leesin_actions_done.zip`。

## 附图（压缩包 `leesin_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

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
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a muscular blind martial-arts monk - a shaved head with a long black braid rising from the crown and curling back (red and gold bands), a red blindfold with a gold-rimmed blue gem at its side and two long tails flowing back, a bare muscular torso with faint scars, red-and-white bandages on the forearms and hands, a white cloth belt with a gold buckle and a red cloth hanging in front, loose dark navy-blue trousers, red-and-white shin wraps, dark cloth shoes - in a fighting guard, 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (top of the braid to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose, motion and hands - the old costume is wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar.
He must be EXACTLY image 1 in every frame: the same braid, blindfold and gem, bandages, belt, cloth, trousers and wraps, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 17 squares from the top of the shaved head to the chin, the braid about 12 more above) - never smaller, never bigger. The build as sturdy as image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE HANDS: <HANDS>
NO EFFECTS AT ALL: no sound wave, no shockwave, no dragon, no speed lines, no dust, no rubble.
Always 3/4 view, face toward the front-right as in image 1; the nose, the mouth, the jaw and the blindfold's edge each a clear shape.
THE PIXEL GRID: every square the size of the template's (7 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<HANDS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- **每帧的头和设计图一样大**（头顶到下巴约 17 格、辫子再高约 12 格）；辫子、蒙眼布、衣服和设计图一样，脸朝右前方；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **手跟着浅色人影**：拳、掌照人影画。
- **跑步两腿轮流在前、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/leesin-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/leesin_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_draven_hd.py`，按每格自己的格子原点读回到设计图的格子上（看 export-log；没有就按交付图自己的格子）；`q_throw` 用 `skill` 第 4–7 帧，`idle_base` 用设计图。
- **逐帧把设计图的头轮廓按蒙眼布宝石对齐叠上去**量头的大小；**跑步查换腿和起伏**（旧版跑步本身是否交替也要对照）；查碎块、空洞。
- 适配：Q 音波出手点（远侧手掌）、R 踢中的位置等特效锚点按新的手脚重新定位；头像截取点、选人卡偏移（待机顶到 -28 以上要设）；待机 / 选人卡轮播（`hero_reels.json`：skill 第 1、3 帧）；俄洛伊灵魂、佛耶戈附身帧表、预览。
