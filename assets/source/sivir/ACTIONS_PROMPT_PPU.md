# 希维尔：全部动作逐帧重画（给 Codex 的提示词）

> 希维尔的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，98 × 81 格，每格一个像素）是用户通过的那张（就是你画的 `sivir-A.png`）：压低身子大开步，往后甩的深蓝黑长发、金头冠和额前青绿宝石、青绿眼睛、红唇、米白围巾，金肩甲和胸甲、露出的腰腹、金腰带、深蓝布片，**近侧的手（画面左边）在腰旁竖握着巨大的金色十字回旋刃**，**远侧的手（画面右边）戴棕色皮手套、张开往右伸**，淡紫灰紧身裤、金护膝护腿、棕靴。请把她的**九个动作每一帧都重新画整个人**：跑步、普攻、Q 掷出、Q 等回、Q 接回、W、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：头发、头冠、脸、围巾、盔甲、腰带、布片、手套、裤子、护腿、靴子和回旋刃的样子都照设计图。
> - **回旋刃跟着旧版那一帧走**：平时竖握在近侧的手里；浅色人影把它举过头顶、往前甩、用手接住的帧就照着画；**浅色人影手里空着的帧（回旋刃飞出去了）就不画回旋刃**。每帧最多一把回旋刃，不要画两把。
> - 不画任何特效（飞出去的回旋刃、刀光、护盾、金光、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、回旋刃怎么拿（下面提示词的 `<HANDS>`），跑步还写了**每一帧的腿**（`legs`）。
> - 跑步 `run_*`：近侧手拿着回旋刃快跑，**两条腿轮流**：第 1、5 帧两只脚收在胯下，第 2、6 帧迈大步，第 3、7 帧后腿高高往后踢起，第 4、8 帧后腿收回来；第 1–4 帧和第 5–8 帧换一条腿。8 帧不能是同一个姿势。
> - 普攻 `attack_*`：挥臂把回旋刃往前甩出去，飞出去的那几帧手里是空的，最后回到手里。
> - Q `skill_*`：把回旋刃举过头顶，往前甩出去。Q 等回 `skill_wait_*`：站着等，远侧的手伸出来准备接，手里是空的。Q 接回 `skill_catch_*`：远侧的手接住回旋刃，再拿回近侧的手。
> - W `skill2_*`：把回旋刃举到脑后，准备掷出。
> - R `ult_*`：把回旋刃高高举过头顶，号召队友。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：踉跄、倒下，最后躺在地上，回旋刃掉在身边。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的希维尔；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从头顶到脚底的高度（81 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头冠顶到下巴约 **23 格**（头发顶比头冠再高一点），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的头发、头冠、脸、盔甲、腰带、布片、手套、裤子、护腿、靴子和回旋刃；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **回旋刃跟着浅色人影**：在哪只手、举多高、有没有（飞出去的帧不画）都照浅色人影；远侧的手一直戴棕手套。
4. **跑步要换腿**：照 `legs` 一帧一帧摆，两只脚收在胯下的帧要画出来，两条腿轮流在前，身体有起伏。（上一位英雄的跑步八帧都是两腿大大分开，像在蹦，只好重画。）
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝画面右前方**，和设计图一样。
- 手臂和身体之间、两腿之间、回旋刃中间的空洞都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 6 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、嘴、宝石各自成块，不要糊成一团；回旋刃的四片刃清楚。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/sivir-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/sivir-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/sivir-actions/HANDOFF.md`（交付说明），再打包成 `outputs/sivir_actions_done.zip`。

## 附图（压缩包 `sivir_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、衣服、回旋刃、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作、腿和回旋刃在哪（衣服不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、回旋刃怎么拿、跑步的腿 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a desert warrior woman in a low, wide stance - long dark navy-black hair swept back to the left, a gold crown with a teal brow gem, teal eyes, red lips, a cream scarf; gold shoulder plates and breastplate, a bare midriff, a gold belt with a teal gem, dark navy cloth panels with gold trim; a HUGE GOLD CROSS-SHAPED THROWING BLADE (the Chakram) upright in her NEAR hand (image left) by her hip; her FAR hand (image right) open, reaching right, in a BROWN LEATHER GLOVE; mauve-grey leggings, gold knee and shin guards, brown boots - 3/4 view, face to the front-right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (top of the hair to soles). Image 3 is the same old frame(s) in colour: copy their body pose, motion, legs and where the Chakram is - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same hair, crown, face, scarf, armour, belt, cloth panels, glove, leggings, guards, boots and Chakram, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 23 squares from the top of the crown to the chin) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE CHAKRAM AND THE HANDS: <HANDS>
THE LEGS (run sheets only): <LEGS>
NO EFFECTS AT ALL: no flying Chakram, no blade trails, no spell shield, no golden glow, no speed lines, no dust.
Always 3/4 view, face to the front-right as in image 1; the eyes, the lips and the gems each a clear shape, the Chakram's four blades clear.
THE PIXEL GRID: every square the size of the template's (6 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<HANDS>`、`<LEGS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons`、`legs` 填（不是跑步的模板删掉 `THE LEGS` 那一行）。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**（头冠顶到下巴约 23 格）；头发、脸、盔甲、衣服和设计图一样，脸朝右前方；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **回旋刃跟着浅色人影**：在哪只手、举多高；浅色人影手空着的帧没有回旋刃；每帧最多一把；远侧手一直戴棕手套。
- **跑步照 `legs`**：第 1、5 帧两只脚收在胯下，两条腿轮流在前，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/sivir-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sivir_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_akali_hd.py`（白底抠图、被围住的白块看四周是不是描边——回旋刃的米白亮边和围巾、按头的大小找缩放、贴回设计图调色板），读原始生成图不读 Codex 的导出图；`idle_base` 就是设计图（旧版一帧不动），`idle` / `bp` 由 `hero_reels.json`（skill_catch 3、2、1，attack 1–2）生成；`SAME` 的帧照 `sheets.json`。
- `skill_wait` 画的是身体帧（2 帧），Q 掷出的特效由 `sivir_bake.json` 照旧烤进去（`Rig.bake`），`attack_fx1`、`skill_catch_fx1` 也由它生成。
- **逐帧把设计图的头轮廓叠上去**量头的大小；**跑步逐帧写出哪只脚在前、有没有收腿帧**；**逐帧确认回旋刃的位置和有无**；查碎块、空洞、第二把回旋刃。
- 适配：普攻 / Q / W 的出手点等特效锚点按新的手重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、塞拉斯副本、预览。
