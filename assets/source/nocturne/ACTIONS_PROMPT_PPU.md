# 魔腾：全部动作逐帧重画（给 Codex 的提示词）

> 魔腾的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，64 × 72 格，每格一个像素）是用户通过的那张（就是你画的 `nocturne-A.png`，按约 16 px 一格读回，PPU 1.80；`refs/design_picture.png` 是它的原图）：**往上弯的冠**、暗影的脸上**两只白色发光的眼睛**；**带尖刺的肩甲**和肩甲上的**蓝色眼睛**；**深蓝色的暗影身体**、**红色和银色的甲片**；**两条手臂上的红银大弯刃**；**没有腿**，身体下面收成**一缕暗影尾巴**。请把他的**每个动作每一帧都重新画整个人**。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画；`attack_fx1`、`ult_fx1` 是普攻、R 加了特效的副本，也不用画；和别的帧一模一样的 7 帧不用再画，所以一共 43 帧（28 张模板）。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**。
> - **两条手臂上的大弯刃照浅色人影**：举起、挥砍、张开，照浅色人影；刀刃和设计图一样大；**没有腿**，下面是暗影尾巴；不画暗影烟雾、拖尾、残影。
> - 不画任何特效。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
> - 飘行 `run_*`：身子前倾往前飘，两把刀刃往后收，暗影尾巴往后飘（**没有腿**，不要画腿和脚；第 5 帧 = 第 4 帧、第 7 帧 = 第 3 帧、第 8 帧 = 第 1 帧，不用画）。
> - 普攻 `attack_*`：先挥一边的刀刃，再挥另一边，照每格的浅色人影（第 1–6 帧）。
> - 被动的回旋 `attack_p_*`：转身一圈，两把刀刃大大张开（第 1–5 帧；第 6 帧是待机，不用画）。
> - Q 梦魇之径 `skill_*`：把刀刃手臂往前一甩、掷出暗影刃（第 1–4 帧；第 5 帧 = 普攻第 6 帧）。
> - E 无言恐惧 `skill2_*`：两把刀刃往前伸，照每格的浅色人影（第 1–5 帧）。
> - R 鬼影重重 `ult_*`：蓄势、身子往上一扬、刀刃举起（第 1–4、6 帧；第 5 帧 = 第 3 帧）。
> - R 扑到时的一击 `ult_hit_*`：两把刀刃大大挥开（第 1、2、4 帧；第 3 帧 = E 第 5 帧）。
> - 受击 `hit_*`：被打得往后一顿。
> - 死亡 `dead_*`：被打中（第 1–2 帧），缩成一团（第 3–4 帧），沉成地上一片扁扁的暗影（第 5–8 帧）。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的魔腾；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时的高度（72 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：冠顶到脸的下沿约 28 格，**不要画小、也不要画大**。之前的英雄动作里头画大了一号或小了一号，待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**同一张模板里的两格、不同模板之间，头和身子的大小都一样。**
3. **两条手臂上的大弯刃照浅色人影**：举起、挥砍、张开，照浅色人影；刀刃和设计图一样大；**没有腿**，下面是暗影尾巴；旧版的特效没有画进去。
4. **飘行没有腿**：照浅色人影摆动暗影尾巴，身体有起伏，**不要画腿和脚**。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧尾尖碰到地面线、站位点不动；蹲下、跳起、躺下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 7 像素，见 `sheets.json` 的 `square` / `square_of`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素的透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/nocturne-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/nocturne-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/nocturne-actions/HANDOFF.md`（交付说明），再打包成 `outputs/nocturne_actions_done.zip`。

## 附图（压缩包 `nocturne_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 nocturne-A） | **每张都附，第五张**：细节 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、手和武器在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a floating nightmare spirit with NO LEGS - a CURVED CREST over his head, a face of shadow with only TWO GLOWING WHITE EYES, SPIKED PAULDRONS with a BLUE EYE on each, a DARK BLUE SHADOW body with RED and SILVER plates, HUGE CURVED RED-AND-SILVER BLADES on both arms, his body tapering into a WISP OF SHADOW TAIL - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> animation frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (the old animation frame scaled to the character's height), the grey horizontal line is the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms and the weapon are - not the old costume, and not the old frames' effects. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when standing. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
The character must be EXACTLY image 1 in every frame: the same head, face, hair, costume and colours, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME AND IN BOTH CELLS (about 28 squares from the top of his crest to the bottom of his face) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<ARMS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no shadow smoke, no trails, no afterimages; the white light stays in his eyes.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the eyes, the pauldrons' eyes and the blades clear.
THE PIXEL GRID: every square the size of the template's (sheets.json's square), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**、身子一样高；人物和设计图一样，朝画面右边；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **两条手臂上的大弯刃照浅色人影**：举起、挥砍、张开，照浅色人影；刀刃和设计图一样大；**没有腿**，下面是暗影尾巴；旧版的特效没有画进去。
- **飘行没有画腿和脚**，尾巴照浅色人影摆动。
- 没有任何特效。
- 最后写 `outputs/nocturne-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/nocturne_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_diana_hd.py`（读 raw/ 的原图；每帧的缩放取身高、头的大小、身体面积三种量法的中位数，旧帧的身体按旧帧的颜色和贴着描边来认，特效不算）；读的格子和设计图一样。`idle_base` 是设计图（静止）；`idle` / `bp` 由 `hero_reels.json` 生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定；他站在地上（不悬浮）。
- **逐帧量头的大小**；**跑步逐帧对腿**；**逐帧对照旧版的姿势**；查碎块、空洞。
- 适配：头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。和蔚、崔斯特、艾克、萨科、凯南、剑魔、丽桑卓在同一个 PR（claude/vi-ppu；蔚、崔斯特、艾克、萨科先单独进了 claude/vi4-ppu）。
