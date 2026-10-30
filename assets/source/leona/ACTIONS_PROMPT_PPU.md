# 蕾欧娜：全部动作逐帧重画（给 Codex 的提示词）

> 蕾欧娜的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，69 × 72 格，每格一个像素）是用户通过的那张（就是你画的 `leona-A.png`）：橙红长发、金色太阳冠、琥珀色眼睛，金色肩甲胸甲和护手，深红裙甲，**近侧的手（画面左边）挎着圆形金色太阳盾**，**远侧的手（画面右边）握着金柄银剑**，金色护膝护胫和靴子。请把她的**八个动作每一帧都重新画整个人**：跑步、普攻、Q、W、E 冲刺、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：头发、太阳冠、脸、金甲、裙甲、护手、盾、剑、腿和靴子的样子都照设计图。
> - **盾和剑跟着旧版那一帧走**：盾平时挎在近侧手臂上挡在身前，**Q 的第 4–5 帧把盾往右前方推出去（盾击）**；剑在远侧手里，浅色人影把剑举起、拉到肩后、往前刺、往下劈、举过头顶的帧就照着画。**死亡第 3 帧起盾和剑都掉在地上**：盾在她左边、剑在她右边。每帧只有一面盾、一把剑。
> - 不画任何特效（阳光、日蚀、光柱、光圈、闪光、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、盾和剑怎么拿（下面提示词的 `<ARMS>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：穿着盔甲稳稳地跑，盾挡在身前，剑低低地握在远侧手里，**两条腿照浅色人影轮流迈步**，头发和裙甲摆动。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：举剑，拉到肩后，往右前方刺出去，压低身子往前下方劈，收势。
> - Q `skill_*`（盾击）：剑举在身后，躲在盾后蓄力，往前冲**把盾往右前方撞出去**，再收回身前。
> - W `skill2_*`（日蚀）：剑举过肩，绕到身后再从上方抡下来，往右前方平刺，盾一直挡在身前。
> - E 冲刺 `e_dash_*`：剑往前上方举着往前冲，再压低身子、剑指前方冲过去。
> - R `ult_*`（日炎耀斑）：剑往前平伸，举起，笔直举过头顶停住，再放下到前方。
> - 受击 `hit_*`：被打得往后一顿，剑举着。
> - 死亡 `dead_*`：被打中，盾和剑脱手掉在地上（第 3 帧起），跪倒，往前扑在地上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的蕾欧娜；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从冠顶到脚底的高度（72 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：冠顶到下巴约 **29 格**（橙红头发、太阳冠、琥珀色眼睛），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的头发、太阳冠、脸、金甲、裙甲、护手、盾、剑、腿和靴子；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）；**盾一直是圆形的金色太阳盾**。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **盾和剑跟着浅色人影**：盾在近侧手臂上、剑在远侧手里，位置朝向照浅色人影；Q 第 4–5 帧盾推到右前方；死亡第 3 帧起两样都在地上；每帧只有一面盾、一把剑。
4. **跑步要换腿**：两条腿照浅色人影轮流迈步，身体有起伏。（之前一位英雄的跑步八帧都是两腿大大分开，像在蹦，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；弓身、跪倒、趴下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间、盾和身体之间、剑和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 8 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；太阳冠的尖、盾上的太阳花纹、剑柄和剑身清楚，没有光晕。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/leona-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/leona-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/leona-actions/HANDOFF.md`（交付说明），再打包成 `outputs/leona_actions_done.zip`。

## 附图（压缩包 `leona_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、盔甲、盾、剑、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、盾和剑在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、盾和剑怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a sun knight - long red-orange hair under a gold sun crown, amber eyes, gold shoulder plates, breastplate and gauntlets, a crimson skirt edged with gold; her NEAR arm (image left) carrying a ROUND GOLD SUN SHIELD before her; her FAR hand (image right) holding a SWORD with a gold hilt and a silver blade; gold knee and shin guards and gold boots - 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (the top of her crown to her soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms, the shield and the sword are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same hair, crown, face, gold armour, crimson skirt, gauntlets, shield, sword, legs and boots, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 29 squares from the top of her crown to her chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). The shield is always the ROUND GOLD SUN SHIELD.
THE SHIELD, THE SWORD AND THE ARMS: <ARMS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no sunlight, no eclipse, no beams, no pillars of light, no rings, no flashes, no speed lines, no dust.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the crown's rays, the sun on the shield, the hilt and the blade clear with no glow.
THE PIXEL GRID: every square the size of the template's (8 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**；头发、太阳冠、脸、盔甲、裙甲和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **盾和剑跟着浅色人影**：盾一直是圆形金盾，每帧一面盾、一把剑；Q 第 4–5 帧盾推到右前方；死亡第 3 帧起两样都掉在地上。
- **跑步两条腿轮流**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/leona-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/leona_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_kayle_hd.py`（白底抠图；每张的缩放先按整个人的面积量，再乘头的大小 `--heads`，因为盾、剑的摆法会让面积失真）；如果又交部件骨架，照 `tools/art/casts_taric_hd.py`。`idle_base` 是设计图（静止，不上下晃）；`SAME` 为空，45 帧都是 Codex 画的；`idle` / `bp` 由 `hero_reels.json`（skill2 0–1、skill 1）生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定（别把盾边或剑尖算进“两脚中点”）。
- 死亡第 3–8 帧盾和剑和人分开：读回时是单独的块，检查碎块时别当成杂点删掉。
- 没有烤进身体的特效；阳光、日蚀、耀斑是单独的特效条（`leona_fx_*`）。
- **逐帧量头的大小**（头发和脸）；**跑步逐帧对腿**；**逐帧确认盾和剑的位置**；查碎块、空洞、第二面盾或第二把剑。
- 适配：普攻 / 技能的特效锚点按新的剑和盾重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。装游戏前先合进最新 main，版本号接着游戏里现装的往上加。
