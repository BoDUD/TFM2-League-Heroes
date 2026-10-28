# 劫：全部动作逐帧重画（给 Codex 的提示词）

> 劫的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，40 × 65 格，每格一个像素）是用户通过的那张（就是你画的 `zed-A.png`）：深钢色头盔、金色镶边、面甲缝里两只红眼睛，红围巾，**背上一个银色大手里剑**（弯尖从头盔后面往上伸），两块金色肩甲，深蓝黑钢甲，从胸口斜垂到右腰的红布（金边），**两只金色护腕，每只手腕两三把银色长钢刃，平时刃尖朝下贴着腿**，深蓝裤子、钢灰护胫和钢靴。请把他的**八个动作每一帧都重新画整个人**：跑步、普攻、W、Q、E、R、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机和跟别的帧一模一样的帧不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：头盔、红眼睛、围巾、手里剑、肩甲、钢甲、红布、护腕、钢刃、腿和靴子的样子都照设计图。
> - **钢刃跟着旧版那一帧走**：平时垂在两腿边、刃尖朝下；浅色人影把手臂举起、往前刺、往两边甩开的帧，钢刃就指向那只前臂指的方向。**背上的手里剑每一帧都在背上。**
> - 不画任何特效（影子分身、飞出去的手里剑、刀光、残影、速度线、烟雾、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、钢刃怎么摆（下面提示词的 `<BLADES>`），跑步还写了**每一帧的腿**（`legs`）。
> - 跑步 `run_*`：前倾的忍者跑，两臂放低、钢刃往后拖，**两条腿轮流**：第 1、2 帧前脚踩地、后腿往后踢起；第 3、4 帧踩地的脚在胯下、另一条腿抬膝从前面交叉带过；第 5、6 帧踩地的脚到了身后、另一条腿往前伸、落地；第 7、8 帧换另一只脚在前面踩地、第一条腿往后踢起。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：蓄力、上步，一只手的钢刃往右前方刺出，再收回。
> - W `skill_*`：一只手臂举起、刃尖朝上，再往右前方甩出去（放出影子）。
> - Q `skill2_*`：举手、双臂上扬、下蹲，两臂往两边低低甩开（扔出手里剑），再站直。**飞出去的手里剑是特效，不画；背上的那个一直在背上。**
> - E `skill_e_*`：两臂收在胸前，再一转身**两臂往左右两边伸直甩开**，钢刃横扫一圈，然后收势。
> - R `ult_*`：下蹲、弹起，低低往右前方突进、钢刃前指，斩过去，低身落地、两臂张开。
> - 受击 `hit_*`：被打得往后一顿，一只手臂甩开。
> - 死亡 `dead_*`：被打得往后仰，跪倒，然后**往前扑倒、趴在地上**。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的劫；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时从手里剑尖到脚底的高度（65 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头盔顶到面甲下沿约 **15 格**，红眼睛在头盔偏右的地方，**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的头盔、手里剑、肩甲、钢甲、红布、护腕、钢刃、腿和靴子；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **钢刃跟着浅色人影**：每只手腕一组，刃尖指向那只前臂指的方向；背上的手里剑每帧都在；不画别的武器。
4. **跑步要换腿**：照 `legs` 一帧一帧摆，两条腿轮流，身体有起伏。（之前一位英雄的跑步八帧都是两腿大大分开，像在蹦，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；跳起来、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样；**只有浅色人影转过身的帧照人影转**：Q 第 2、3 帧（举手上扬时脸转向画面左前方）、E 第 4 帧（旋身横斩时正面对着画面）。
- 两腿之间、手臂和身体之间、钢刃和腿之间、手里剑的尖之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 8 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**两只红眼睛清楚、不发光晕；每把钢刃是一条清楚的长条，刃和刃之间有空隙。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/zed-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/zed-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/zed-actions/HANDOFF.md`（交付说明），再打包成 `outputs/zed_actions_done.zip`。

## 附图（压缩包 `zed_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、盔甲、钢刃、手里剑、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿和钢刃在哪（盔甲不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、钢刃怎么摆、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): an armoured ninja - a dark steel helmet with gold trim and two red eyes in its visor slit, a red scarf, a big silver SHURIKEN on his back with its curved points rising over the helmet, two gold shoulder plates, navy-black steel armour, a red cloth with gold trim hanging diagonally from his chest to his right hip, two gold bracers each with two or three long silver WRIST BLADES pointing down along his legs, navy trousers, steel-grey greaves and steel boots - 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (the shuriken's top point to his soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms and blades are - not the old armour. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
He must be EXACTLY image 1 in every frame: the same helmet, eyes, scarf, shuriken, shoulder plates, armour, red cloth, bracers, blades, legs and boots, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 15 squares from the top of the helmet to the bottom of the visor) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE BLADES AND THE ARMS: <BLADES>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no shadow clones, no flying shuriken, no slash trails, no afterimages, no speed lines, no smoke, no dust.
3/4 view facing right as in image 1, EXCEPT where the pale figure has turned (Q frames 2-3: his face turned toward the viewer's left as he rears up; E frame 4: his front to the viewer mid-spin) - there turn him as the pale figure; the two red eyes clear with no glow, each blade a clear long strip with gaps between the blades.
THE PIXEL GRID: every square the size of the template's (8 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<BLADES>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**；头盔、红眼睛、围巾、手里剑、盔甲、红布和设计图一样，朝画面右边（Q 2、3 和 E 4 照浅色人影转身）；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **钢刃跟着浅色人影**，每只手腕一组；背上的手里剑每帧都在；没有别的武器。
- **跑步照 `legs`**：两条腿轮流，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/zed-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zed_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_tristana_hd.py`（白底抠图、被围住的白块看四周是不是描边——他的钢刃和手里剑亮面接近白色、按头的大小找缩放、贴回设计图调色板）；`idle_base` 是设计图（静止，不上下晃）；`SAME` 里的 `design 0` 帧（W 4、受击 2）直接用设计图，其余 `SAME` 帧（Q 6 = 普攻 6、E 5 = E 3、R 2 = E 2、R 4 = R 3、死亡 5 = 死亡 4、死亡 7 / 8 = 死亡 6）用源帧的画，**但放在旧帧自己的位置**（有几帧是同一张图挪了位置：E 5、R 2、R 4、死亡 7 / 8、受击 2 比待机左移一格）；`idle` / `bp` 由 `hero_reels.json`（skill2 0–2、ult 0–1）生成。
- 没有烤进身体的特效；影子分身和刀光是单独的特效条（`zed_fx_*`），注册时看影子分身是不是用他的身体图画的、要不要一起换。
- **逐帧把设计图的头轮廓叠上去**量头的大小；**跑步逐帧写出哪只脚在前**；**逐帧确认钢刃的位置**；查碎块、空洞、多出来的武器；钢刃和手里剑抠白底时别被抠掉。
- 适配：普攻 / 技能的特效锚点按新的钢刃重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。
