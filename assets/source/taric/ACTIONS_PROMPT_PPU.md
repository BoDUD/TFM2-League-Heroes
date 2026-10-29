# 塔里克：全部动作逐帧重画（给 Codex 的提示词）

> 塔里克的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，48 × 62 格，每格一个像素）是用户通过的那张（就是你画的 `taric-A.png`）：棕色长发、蓝眼睛，两块银白肩甲各嵌一颗大蓝宝石，蓝宝石吊坠，斜披的蓝布带，深棕皮衣，银腰带扣上嵌紫宝石，背后深蓝披风，**近侧的手戴深色护臂、握着银色双刃锤（锤头两片弯刃、中间一颗紫蓝宝石），平时锤头朝下垂在脚边**，**远侧的手臂光着、戴深蓝护腕**，深棕裤子、银灰护膝护胫、深色靴子。请把他的**八个动作每一帧都重新画整个人**：跑步、普攻、被动强化普攻、E、Q、R、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：头发、脸、肩甲、宝石、吊坠、蓝布带、皮衣、腰带、披风、护臂、锤子、光着的手臂、腿和靴子的样子都照设计图。
> - **锤子跟着旧版那一帧走**：平时近侧的手握着、锤头朝下垂在脚边；浅色人影把锤子往后拉、举过头顶、往前横扫、往前刺、砸下去的帧就照着画；死亡时锤子被甩出去、落在地上，也照浅色人影的位置。每帧只有一把锤子。**远侧的手臂每一帧都是光着的。**
> - 不画任何特效（星光、光束、护盾、光柱、闪光、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、锤子怎么拿（下面提示词的 `<HAMMER>`），跑步还写了**每一帧的腿**（`legs`）。
> - 跑步 `run_*`：挺直身子大步走，锤子低低地拖在身后，光着的手臂摆动，**两条腿轮流**：第 1、8 帧近侧（浅色）的脚在前面踩地、远侧（深色）的腿往后踢起；第 2 帧近侧的脚在胯下、远侧的腿抬膝从前面带过；第 3 帧近侧的脚到了身后、远侧的腿往前伸；第 4 帧换远侧的脚在前面踩地、近侧的腿往后踢起；第 5、6 帧远侧的脚在胯下、近侧的腿抬膝带过；第 7 帧远侧的脚到了身后、近侧的腿往前伸。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：把锤子往后拉，再往右前方胸口高度横扫出去，带过身体，收势。
> - 被动强化普攻 `attack_p_*`：把锤子拉到肩后、高高举过头顶，压低身子往右前方砸下去，再站起来。
> - E `skill_*`：把锤子往后拉，再笔直往右前方刺出去，光着的远侧手举在身后，收势。
> - Q `skill2_*`：光着的远侧手高高举过头顶、手掌张开，再放下；锤子一直垂在近侧手里。
> - R `ult_*`：近侧的手把锤子高高举过头顶，光着的远侧手往前张开，举着不动，再收势。
> - 受击 `hit_*`：被打得往后一顿，远侧的手臂甩开。
> - 死亡 `dead_*`：被打得往后仰，锤子脱手飞出去，跪倒，往前扑在地上，锤子落在他面前的地上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的塔里克；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时从头顶到脚底的高度（62 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头顶到下巴约 **17 格**（棕色长发、蓝眼睛），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的头发、脸、肩甲、宝石、吊坠、蓝布带、皮衣、腰带、披风、护臂、锤子、腿和靴子；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **锤子跟着浅色人影**：在近侧手里、锤头朝哪都照浅色人影；死亡时照浅色人影飞出去、落在地上；每帧只有一把；远侧的手臂每帧都光着。
4. **跑步要换腿**：照 `legs` 一帧一帧摆，两条腿轮流，身体有起伏。（之前一位英雄的跑步八帧都是两腿大大分开，像在蹦，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；弓身、跪倒、趴下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 两腿之间、手臂和身体之间、锤子和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 8 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；宝石清楚、没有光晕；锤头的两片刃和中间的宝石清楚。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/taric-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/taric-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/taric-actions/HANDOFF.md`（交付说明），再打包成 `outputs/taric_actions_done.zip`。

## 附图（压缩包 `taric_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、盔甲、锤子、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿和锤子在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、锤子怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a gem knight - long brown hair, blue eyes, two big silver-white shoulder plates each set with a big blue gem, a blue gem pendant, a blue sash falling diagonally from one shoulder, a dark brown leather coat, a silver belt buckle set with a violet gem, a dark navy cape behind him; his NEAR hand in a dark gauntlet holding a silver double-bladed HAMMER (two curved silver-white blades with a violet-blue gem between them) hanging head down by his feet; his FAR arm BARE with a dark blue wrist guard; dark brown trousers, silver-grey knee and shin guards, dark boots - 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (the top of his hair to his soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the arms and the hammer are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
He must be EXACTLY image 1 in every frame: the same hair, face, shoulder plates, gems, pendant, sash, coat, belt, cape, gauntlet, hammer, bare arm, legs and boots, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 17 squares from the top of his hair to his chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE HAMMER AND THE ARMS: <HAMMER>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no starlight, no beams, no shields, no pillars of light, no flashes, no speed lines, no dust.
Always 3/4 view facing right as in image 1; the eyes, the brows and the mouth each a clear shape; the gems clear with no glow; the hammer's two blades and its gem clear.
THE PIXEL GRID: every square the size of the template's (8 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<HAMMER>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**；头发、脸、肩甲、宝石、盔甲、披风和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **锤子跟着浅色人影**，每帧只有一把；远侧的手臂每帧都光着。
- **跑步照 `legs`**：两条腿轮流，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/taric-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/taric_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_zed_hd.py`（白底抠图、被围住的白块看四周是不是描边——他的肩甲和锤头接近白色；每张的缩放取整个人面积和头部匹配的平均，贴回设计图调色板）；`idle_base` 是设计图（静止，不上下晃）；`SAME` 为空，49 帧都是 Codex 画的；`idle` / `bp` 由 `hero_reels.json`（skill2 0–3、ult 0–1）生成。旧待机的帧中心在两脚中点右边 3.5 像素（`OLD_CENTRE` 3.5）。
- 死亡第 2–8 帧锤子和人分开（飞出去、落在地上）：读回时它是单独的一块，检查碎块时别当成杂点删掉。
- 没有烤进身体的特效；星光、光束、护盾是单独的特效条（`taric_fx_*`）。
- **逐帧把设计图的头轮廓叠上去**量头的大小；**跑步逐帧写出哪只脚在前**；**逐帧确认锤子的位置**；查碎块、空洞、第二把锤子；肩甲和锤头抠白底时别被抠掉。
- 适配：普攻 / 技能的特效锚点按新的锤子重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。
