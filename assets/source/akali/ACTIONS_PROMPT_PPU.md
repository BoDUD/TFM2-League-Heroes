# 阿卡丽：全部动作逐帧重画（给 Codex 的提示词）

> 阿卡丽的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，71 × 72 格，每格一个像素）是用户通过的那张（就是你画的第四稿 `akali-pixel-v3`）：压低身子大开步的忍者，深蓝色的刺头和甩向左上的高马尾、黄绿发带，橙色眼睛、黄绿色的面罩，青绿短上衣、露出的腰腹，手臂上淡紫色的纹身，**近侧的手（画面左边）往左伸，握着弯钩镰刀**，**远侧的手（画面右边）往右下，握着长长的直刀**。请把她的**十个动作每一帧都重新画整个人**：跑步、普攻、强化普攻、Q、E 掷出、E 二段冲刺、R、R 二段、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏，**不要加新动作**）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - **人物本身全部照设计图**：深蓝刺头和刘海、甩向左上的高马尾和黄绿发带、橙色眼睛、黄绿面罩、青绿短上衣和黄绿饰边、露出的腰腹、手臂上的淡紫色纹身、黄绿护腕、橙色腰绳、近侧胯上的暗红腰包、青绿前摆和黄绿饰边、深蓝灯笼裤、黄绿裤脚带、深蓝的鞋。
> - **武器照设计图，不照旧版**：**弯钩镰刀一直在近侧的手（画面左边），长直刀一直在远侧的手（画面右边）**。旧版两只手拿的刚好反过来，所以**只照浅色人影的手臂位置**（手在哪里、举起还是放低、甩开还是刺出），手里的武器换成设计图的。
> - 不画任何特效（苦无、手里剑、烟雾、刀光、冲刺的残影、速度线、尘土）。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、手怎么摆（下面提示词的 `<HANDS>`）。
> - 跑步 `run_*`：压低身子快跑，**两条腿每半个周期交换一次**（左脚在前、然后右脚在前），身体随步子起伏；8 帧不能是同一个姿势。
> - 普攻 `attack_*`：往前快速一挥，收回架势。强化普攻 `attack_p_*`：往前探身长长地一劈，再收回。
> - Q `skill_*`：手臂一扫，往前甩出一扇苦无（**苦无不画**）。
> - E `skill2_*`：往后翻身，往前掷出手里剑（**手里剑不画**），落地。E 二段 `skill2_dash_*`：贴地往前冲、出刀，站起。
> - R `ult_*`：往前冲过目标、刀刃向外，转身站定。R 二段 `ult2_*`：再一次压低快冲，收回架势。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：踉跄、倒下，最后躺在地上，武器掉在身边。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的阿卡丽；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站着时从马尾顶到脚底的高度（72 格）。

**最重要的五条：**

1. **头的大小每一帧都和设计图一样**：头顶到面罩下沿约 **21 格**（马尾顶比头顶再高约 9 格），**不要画小、也不要画大**。之前一位英雄的动作把头画小了一号，结果待机和动作之间头一大一小，用户很不满意。
2. **人物和设计图一模一样，不变形**：同样的头发和马尾、发带、眼睛、面罩、衣服、纹身、腰包、裤子和两把武器；**体格和设计图一样**，身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
3. **武器在设计图的手里，手臂跟着浅色人影**：弯钩镰刀一直在近侧的手，长直刀一直在远侧的手。
4. **跑步要换腿**：两条腿轮流在前，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；翻身、冲刺、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**朝画面右边**，和设计图一样。
- 手臂和身体之间、两腿之间、武器和身体之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块（模板里每格 8 像素），横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**眼睛、面罩的边各自成块，不要糊成一团；两把武器的刃清楚。** 不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。**不要自己缩放、裁剪或重新排版交付图**；原始生成图原样放进 raw/。

- 交付：`outputs/akali-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/akali-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/akali-actions/HANDOFF.md`（交付说明），再打包成 `outputs/akali_actions_done.zip`。

## 附图（压缩包 `akali_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、衣服、武器、比例、头的大小、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作和手臂（衣服和武器不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、手怎么摆 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a ninja girl in a low, wide stance - spiky dark blue hair with bangs and a thick high ponytail swept up to the upper left, tied with lime-yellow ribbons; an orange eye; a lime-yellow face mask; a teal crop top with lime trim, a bare midriff, bare arms with pale violet tattoos, lime wrist wraps; an orange rope belt, a dark red pouch on her near hip, a teal front panel with lime trim; baggy dark blue trousers with lime ankle wraps, dark blue shoes; her NEAR hand (image left) reaching out left with a HOOKED silver kama, her FAR hand (image right) low to the right with a long STRAIGHT silver blade - 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (top of the ponytail to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose, motion and arms - the old costume and the old weapons are wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, feet on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar. Do not rescale, crop or re-lay the sheet afterwards.
She must be EXACTLY image 1 in every frame: the same hair and ponytail, ribbons, eye, mask, top, tattoos, wraps, belt, pouch, front panel, trousers, shoes and weapons, image 4's colours only. THE HEAD IS THE SAME SIZE AS IN IMAGE 1 IN EVERY FRAME (about 21 squares from the top of the head to the bottom of the mask, the ponytail about 9 squares higher) - never smaller, never bigger. The build as in image 1: the body, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE HANDS: <HANDS>
NO EFFECTS AT ALL: no kunai, no shuriken, no smoke, no slash trails, no dash afterimages, no speed lines, no dust.
Always 3/4 view facing right as in image 1; the eye and the mask's edge each a clear shape, both blades clear.
THE PIXEL GRID: every square the size of the template's (8 px), on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<HANDS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字；没有被缩放或裁剪。
- **每帧的头和设计图一样大**（头顶到面罩下沿约 21 格）；头发、马尾、脸、衣服、纹身和设计图一样，朝画面右边；身体、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **弯钩镰刀在近侧的手、长直刀在远侧的手**（每一帧），手臂跟着浅色人影。
- **跑步两条腿轮流在前、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/akali-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/akali_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回：照 `tools/art/casts_rengar_hd.py`（白底抠图、被围住的白块看四周是不是描边、按头缩放、贴回设计图调色板），读原始生成图不读 Codex 的导出图；`idle_base` 由设计图下沉呼吸做出（旧版 0,0,1,2,2,2,1,0 行，脚不动），`idle` / `bp` 由 `hero_reels.json`（attack 1–2）生成；`SAME` 的帧照 `sheets.json`（跨动作：attack 6 是五个动作的收招帧）。
- `skill2_dash`、`ult` 画的是身体帧（5、6 帧），特效由 `akali_bake.json` 照旧烤进去（`Rig.bake`），`ult2_fx1` 也由它从 `ult2` 生成。
- **逐帧把设计图的头轮廓按眼睛对齐叠上去**量头的大小；**跑步逐帧写出哪只脚在前**；**逐帧确认弯钩在近侧手、直刀在远侧手**；查碎块、空洞、第三只手；镰刀的银白刃抠白底时别被抠掉。
- 适配：普攻 / 强化普攻 / Q / E 的出手点等特效锚点按新的手重新定位；头像截取点、选人卡偏移；俄洛伊灵魂、佛耶戈附身 / 妮蔻变身帧表、预览。
