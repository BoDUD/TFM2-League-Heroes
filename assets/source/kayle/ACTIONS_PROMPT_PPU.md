# 凯尔：全部动作逐帧重画（给 Codex 的提示词）

> 凯尔的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，66 × 112 格，每格一个像素）是用户通过的那张（就是你画的 `kayle-A.png`）：白色短发、琥珀色大眼睛，头后两只淡蓝到淡紫的翅膀（画面左边那只大一些），金色护颈胸甲和肩甲、金腰带，浅灰绿紧身衣，金色护臂，**远侧的手（画面右边）握着金柄青色火焰剑**，金色护膝护胫和靴子，**悬浮在空中、脚尖朝下**。请把她的**八个动作每一帧都重新画整个人**：飞行（移动）、远程普攻、近战普攻、Q、E、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：头发、脸、翅膀、金甲、紧身衣、护臂、剑、腿和靴子的样子都照设计图。
> - **剑跟着旧版那一帧走**：平时远侧的手握着、剑尖斜朝右下；浅色人影把剑往后拉、举过头顶、往前刺、往下劈的帧就照着画。**R 第 6 帧剑自己飞到她头顶很高的地方（和她分开），第 7 帧手里没有剑，第 8 帧剑回到手里**；**死亡第 2 帧起没有剑**。每帧最多一把剑。
> - **两只翅膀照浅色人影**：展开、举起、往后收。
> - 不画任何特效（火焰、焰浪、光圈、光柱、圣剑、闪光、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、剑怎么拿（下面提示词的 `<SWORD>`），飞行还写了**每一帧的翅膀**（`wings`），每张模板一格多少像素（`square`：R 的模板格子小一些，因为她飞得很高）。
> - 飞行 `run_*`：身子前倾往前飞，**脚一直不着地**，两腿弯着拖在身后，**翅膀扇动**（16 帧里扇两次：照 `wings` 一帧一帧摆，举起、举高、往后收），剑低低地握在身后，头发往后飘，身体随着扇动上下起伏。16 帧不能是同一个姿势。
> - 远程普攻 `attack_*`：把剑甩到肩后，往前俯冲，把剑往右前方刺出去，往上升，收势。
> - 近战普攻 `attack_melee_*`：把剑笔直往前刺，高高举过头顶，往前冲，在胸口高度往右前方劈出去，收势。
> - Q `skill_*`：张开翅膀，几乎平着往前冲，蜷身转回来，剑低低的，收势。
> - E `skill2_*`：把剑拉到肩后，往右前方劈下去，收势。
> - R `ult_*`：张开翅膀蹲伏，往高空升起，把剑笔直举过头顶，第 6 帧把剑往上抛到头顶很高的地方，第 7 帧空着手落下来，第 8 帧落地、剑回到手里。
> - 受击 `hit_*`：在空中被打得往后一顿。
> - 死亡 `dead_*`：被打得往后仰，剑没了，跪倒，往前扑倒、趴在地上，翅膀盖在身上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的凯尔；灰色横线是地面（她悬浮，脚不踩它），短竖线是站位点，左边灰色竖条是她的高度（翅膀尖到剑尖，112 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头发顶到下巴约 **23 格**（白色短发、琥珀色眼睛），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的头发、脸、翅膀、金甲、紧身衣、护臂、剑、腿和靴子；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。**每帧都是两只翅膀**，不要多也不要少。
3. **剑跟着浅色人影**：在远侧手里、剑尖朝哪都照浅色人影；R 第 6 帧剑单独飞在头顶上方、第 7 帧没有剑；死亡第 2 帧起没有剑；每帧最多一把。
4. **飞行要扇翅膀**：照 `wings` 一帧一帧摆，脚不着地，身体有起伏。（之前一位英雄的跑步每帧都是同一个姿势，只好重画。）
5. **比例统一、位置照人影**：每张图按灰色竖条定大小，每一帧用同一个比例；**每一帧的位置和高度都照浅色人影**（她悬浮在地面线上方，R 飞得很高）。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间、翅膀和头之间、剑和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格的像素数见 `square`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；翅膀的羽片、金甲的边、剑柄和剑身清楚，剑和翅膀没有光晕。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/kayle-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/kayle-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/kayle-actions/HANDOFF.md`（交付说明），再打包成 `outputs/kayle_actions_done.zip`。

## 附图（压缩包 `kayle_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、翅膀、盔甲、剑、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、翅膀、腿和剑在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、剑怎么拿、飞行的翅膀、格子大小 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a winged angel knight - short white hair, big amber eyes, a pale blue-to-lilac WING rising behind each side of her head (the one on the image left bigger), a gold gorget and breastplate, gold shoulder plates, a gold belt, a pale grey-green bodysuit, gold bracers; her FAR hand (image right) holding a SWORD with a gold hilt and a cyan flame blade; gold knee and shin guards and gold boots; HOVERING in the air, toes pointing down - 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground (she floats above it), the short tick her standing point, the grey bar on the left her height (wing tips to sword tip). Image 3 is the same old frame(s) in colour: copy their body pose, motion, wings, legs and where the arms and the sword are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place, height and size. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same hair, face, two wings, gold armour, bodysuit, bracers, sword, legs and boots, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 23 squares from the top of her hair to her chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). Always TWO wings.
THE SWORD, THE ARMS AND THE WINGS: <SWORD>
THE WINGS IN FLIGHT (run sheets only): <WINGS>
NO EFFECTS AT ALL: no fire, no flame waves, no rings, no pillars or swords of light, no flashes, no speed lines, no dust.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the wing feathers, the armour's edges, the hilt and the blade clear, no glow on the sword or the wings.
THE PIXEL GRID: every square the size of the template's (<SQUARE> px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<SWORD>`、`<WINGS>`、`<SQUARE>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`wings`、`square` 填（不是飞行的模板删掉 `THE WINGS IN FLIGHT` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**；头发、脸、两只翅膀、金甲、紧身衣和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，位置和高度照浅色人影。
- **剑跟着浅色人影**，每帧最多一把；R 第 6 帧剑单独在头顶上方、第 7 帧没有剑；死亡第 2 帧起没有剑。
- **飞行照 `wings`**：翅膀扇动、脚不着地，16 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/kayle-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/kayle_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：Codex 交回的样子决定读法——整帧画稿照 `tools/art/casts_zed_hd.py`（白底抠图、被围住的白块看四周是不是描边——她的头发、翅膀亮边、剑身接近白色；每张的缩放取整个人面积和头部匹配的平均，贴回设计图调色板）；如果又交部件骨架，照 `tools/art/casts_taric_hd.py` 重新切部件、按旧帧摆。`idle_base` 是设计图（静止，不上下晃）；`SAME` 为空，57 帧都是 Codex 画的；`idle` / `bp` 由 `hero_reels.json`（skill2 0、skill 5）生成。
- 她悬浮：旧帧的帧中心在脚尖和剑尖上面；量对齐点用旧 idle_base 和设计图的剪影重叠（塔里克的教训：别把剑尖算进“两脚中点”）。
- R 第 6 帧剑和人分开（抛在头顶上方）：读回时它是单独的一块，检查碎块时别当成杂点删掉；R 的模板格子是 4 像素，读回按它自己的缩放。
- 没有烤进身体的特效；火焰、焰浪、圣剑是单独的特效条（`kayle_fx_*`、`kayle_big`、`kayle_ascend`）。
- **逐帧把设计图的头轮廓叠上去**量头的大小；**飞行逐帧对翅膀**；**逐帧确认剑的位置**；查碎块、空洞、第二把剑、第三只翅膀。
- 适配：普攻 / 技能的特效锚点按新的剑重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、`league_kayle` 升阶附加包、预览。装游戏前先把含猴子 1.53 的 main 合进来（游戏里的 league.dll 已是 0.8.7）。
