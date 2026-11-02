# 泰隆：全部动作逐帧重画（给 Codex 的提示词）

> 泰隆的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，105 × 86 格，每格一个像素）是用户通过的那张（就是你画的 `talon-A.png`，`refs/design_picture.png` 是它的原图）：**蓝紫色大兜帽**，**银色 V 字护额**和护颊，兜帽下**晒黑的脸**；**蓝紫围巾带青色条纹**、**叠层银护肩**、**银色护臂**；**近侧手臂往前伸、蓝紫手套握拳**；**深蓝上衣**、**青金腰带**；身后**酒红色长披风**，披风上挂着**银色刀片**，下端连着**一把很长的银色刀尖**拖向左下；**深蓝裤子**、**深灰钢护膝护胫靴子**；压低身子向前探的刺客姿势。请把他的**九个动作每一帧都重新画整个人**：跑步、普攻、W、Q 跃击、Q 近身刺、E 翻越、R、受击、死亡。**身体的姿势照他旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画（他的旧帧没有和待机一模一样的），所以一共 57 帧。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：兜帽、护额、脸、围巾、护肩、护臂、衣服、披风、腿甲的样子都照设计图。
> - **腕刃照浅色人影**：浅色人影手上伸出一条长长的灰色刀刃的帧，就在**近侧的拳头上画一把又长又直的单刃银刀**（和前臂一样长，用设计图里钢的颜色）；浅色人影手上没有刀的帧，就画设计图那样**握着拳的蓝紫手套**。
> - **披风跟着浅色人影**：酒红披风、上面的银刀片和下端的长银刀尖照浅色人影飘、甩、卷、铺开。
> - 不画任何特效（飞出去的刀、刀光、残影、速度线、尘土、血都不要）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、腕刃和披风怎么放（下面提示词的 `<BLADE>`），跑步还写了腿（`legs`）。
> - 跑步 `run_*`：压得很低、身子往前倾的快跑，披风在身后飘，近侧手臂和刀放低在前，**两条腿照浅色人影轮流迈步**。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：近侧手臂往后收，再**把腕刃笔直往前刺**（第 3 帧，刀伸得很远），收回到蹲姿。
> - W `skill_*`（斩草除根）：蓄力，**把近侧手臂往前往外一甩**（第 3 帧，飞出去的刀是特效，不画），披风卷起，再收回。
> - Q 跃击 `skill2_*`（诺克萨斯式外交）：**往上跳起**（第 1–2 帧），**在空中翻跟头**（第 4–5 帧**头朝下**，披风和刀片甩向上方），落地成深弓步（第 6 帧），再站起来。
> - Q 近身刺 `skill2_stab_*`：蓄势，**往前挥砍、把刀远远刺出去**（第 2–3 帧，身体伸展），转身回旋（第 4–5 帧），站稳。
> - E `skill_e_*`（刺客之道）：蹲下**翻越**——在空中**抱团翻一个跟头**（第 2–4 帧：蜷着、头朝下、转着），落地（第 5 帧），接着往前跑（第 6–7 帧）。
> - R `ult_*`（暗影突袭）：蹲下，**原地转一圈**，两只手臂带着刀甩开（第 2–7 帧：身体转、披风和刀旋开），再回到蹲姿。
> - 受击 `hit_*`：被打得往后一顿，头往后仰。
> - 死亡 `dead_*`：被打中，往后踉跄，踮起脚，扭身，倒下，最后**脸朝下平趴在地上**，披风和长刀尖铺在身后。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到他的身高），**照它的身体姿势、位置和大小**重新画成设计图里的泰隆；灰色横线是地面，短竖线是站位点，左边灰色竖条是他站着时从兜帽顶到脚底的高度（86 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：兜帽顶到下巴约 **36 格**（蓝紫兜帽、银色 V 字护额、晒黑的脸），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的兜帽、护额、脸、围巾、护肩、护臂、衣服、披风、腿甲；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **腕刃和披风跟着浅色人影**：浅色人影手上有刀就画一把长银刀，没有就画拳头；每帧最多一把手里的刀；披风和长刀尖照浅色人影。
4. **跑步要换腿**：两条腿照浅色人影轮流迈步，身体有起伏。（之前一位英雄的跑步八帧都是两腿大大分开，像在蹦，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；跳起、翻滚、趴下的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样（翻跟头、转圈的帧照浅色人影转）。
- 两腿之间、披风和腿之间的空隙都是**透明**的。

**像素规则**：和设计图同样密度的方块（模板里每格 8 像素，**Q 跃击和 R 的模板 7 像素、E 的模板 6 像素**——这几个动作跳得高，模板缩小了，见 `sheets.json` 的 `square`），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–5 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、眉毛、嘴各自成块，不要糊成一团；V 字护额、护肩、手指和刀刃清楚，没有光晕。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/talon-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/talon-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/talon-actions/HANDOFF.md`（交付说明），再打包成 `outputs/talon_actions_done.zip`。

## 附图（压缩包 `talon_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、披风、比例、头的大小、颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 talon-A） | **每张都附，第五张**：细节（脸、护额、刀刃、手指） |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿、刀和披风在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、腕刃和披风怎么放、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a hooded assassin - a big BLUE-VIOLET HOOD with a SILVER V BROW GUARD and cheek guards, a tanned face under it; a blue-violet scarf with a teal stripe, a layered silver pauldron, silver vambraces, the near arm reaching forward with a blue-violet glove in a fist; a dark navy tunic with a teal and gold sash; a long RUST-RED CLOAK behind him hung with SILVER BLADE TIPS, its lower end ONE LONG SILVER SPEAR TIP; dark navy trousers, gunmetal knee guards, greaves and boots - in a low forward-leaning ready crouch, 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail in the face, the brow guard, the blades and the fingers. Image 2 is a TEMPLATE of <N> animation frame(s) of his <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (his old animation frame scaled to his height), the grey horizontal line is the ground, the short tick his standing point, the grey bar on the left his height standing (the top of the hood to his soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the wrist blade and the cloak are - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when he stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
He must be EXACTLY image 1 in every frame: the same hood, brow guard, face, scarf, pauldron, vambraces, outfit, cloak and greaves, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 36 squares from the top of the hood to his chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
<BLADE>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no thrown blades, no blade trails, no afterimages, no speed lines, no dust, no blood.
Always 3/4 view facing right as in image 1 (turning only where the pale figure flips or spins); the eyes, the brows and the mouth each a clear shape; the brow guard, the pauldron, the fingers and the blades clear with no glow.
THE PIXEL GRID: every square the size of the template's (sheets.json's square: 8 px; Q's leap and R 7 px, E 6 px), on one straight grid; the near-black outline of image 1 around the figure; 3-5 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<BLADE>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头都和设计图一样大**；兜帽、护额、脸、披风、腿甲和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **腕刃和披风跟着浅色人影**：有刀的帧手里一把长银刀，没刀的帧是拳头；Q 跃击第 4–5 帧头朝下；E 第 2–4 帧在翻跟头。
- **跑步两条腿轮流**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/talon-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/talon_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：整帧画稿照 `tools/art/casts_briar_hd.py`（白底抠图；每张的缩放先按整个人的面积量，再乘头的大小 `--heads`——泰隆用蓝紫兜帽和银护额的面积量头；站着的帧再按旧版同一帧的身高对齐）；读的格子和设计图一样（约 10.5 px 一格的原图密度）。`idle_base` 是设计图（静止，不上下晃）；`idle` / `bp` 由 `hero_reels.json`（attack 0–1、skill2_stab 5）生成。
- 对齐点用设计图和旧 idle_base 的剪影重叠来定（别把披风的长刀尖算进“两脚中点”）；他站在地上（不悬浮）。
- **逐帧量头的大小**（兜帽和脸）；**跑步逐帧对腿**；**逐帧确认腕刃**（有刀 / 拳头、每帧最多一把）；查碎块、空洞；披风上的刀片和长刀尖是身体的一部分，检查碎块时别删掉。
- 适配：普攻 / 技能的特效锚点按新的手和刀重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、翻墙附加包 `league_talon_vault`、预览。装游戏前先合进最新 main，版本号接着游戏里现装的往上加。
