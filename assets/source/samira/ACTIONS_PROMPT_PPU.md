# 莎弥拉：全部动作逐帧重画（给 Codex 的提示词）

> 莎弥拉的定稿设计图（`refs/design.png`，6 倍放大；`refs/design_1x.png` 是 1 倍原图，77 × 105 格）就是你画的 v3（头缩小那版），背后的大剑已经拉成一条直线，用户选定了它。请把她的**九个动作每一帧都重新画整个人**：跑步、枪普攻、剑普攻、枪 Q、剑 Q、E→W、R、受击、死亡。**身体的姿势照她旧版的同一帧**（`refs/old_<同名>.png`，用户以前认可过的动作和节奏）。待机不用画。
>
> **旧版的样子和新的不一样，只照旧版的身体动作**：
> - 旧版是另一套衣服（绿上衣、绿裤子），**人物本身全部照设计图**：侧梳的墨绿长发和金链、眼罩和红带、绿色的眼睛、耳环、手臂纹身、深色护甲上衣和红色、金色枪套、靴子。
> - **大剑照设计图**：剑柄带红穗子、金色护手、银色长剑身，**剑身是一条直线**，不要弯、不要折。**枪照设计图**：银色手枪。
> - 旧版每帧里画着枪口火光、红色的剑光、冲刺扬起的沙尘，这些是特效，**全部不画**，只画人和武器。
>
> `sheets.json` 列出每张模板（`templates/*.png`，每张 1536×1024；**一张一格或两格**：两格的每格 768 宽，一格的整张 1536 宽，照模板画）：是哪个动作的第几帧、武器怎么拿（下面提示词的 `<WEAPONS>`）。`same` 里写了哪些帧沿用哪一帧，这些不用画。
> - 跑步 `run_*`：快跑，大剑背在背上。**左右腿每半圈要明显地交换**（一会儿左脚在前、一会儿右脚在前），**身体随步子上下起伏**；8 帧不能是同一个姿势。
> - 枪普攻 `attack_*`：**远侧的手（画面右边）**举枪往前开枪，再放下。
> - 剑普攻 `attack_m_*`：从背上拔出大剑，在身前往下劈，再收回背上。
> - 枪 Q `skill_*`：远侧的手往前开枪。
> - 剑 Q `skill_m_*`：大剑举起、在身前横斩，再收回背上。
> - E→W `skill2_*`：握着大剑往前冲刺，然后挥剑在身边旋一圈，再站定。
> - R `ult_*`：**两只手各拿一把枪**，轮流往两边开火。
> - 受击 `hit_*`：被打得往后一缩。
> - 死亡 `dead_*`：往后倒、躺下，大剑掉在她旁边地上。
>
> **每一格里**：**浅色的人影就是这一帧要摆的姿势**（旧版同一帧放大到她的身高），**照它的身体姿势、位置和大小**重新画成设计图里的莎弥拉；灰色横线是地面，短竖线是站位点，左边灰色竖条是她站直时从头顶到脚底的高度（105 格）。

**最重要的五条：**

1. **人物和设计图一模一样，不变形**：同样的发型、脸（眼罩、绿眼睛）、衣服、纹身、枪套和靴子；头的大小、身体宽度、手臂和腿的长度粗细**每帧都和设计图一样**（弯曲可以，拉长、压扁、变粗变细不行）。**只用调色板里的颜色**（`refs/design_palette.png`）。
2. **武器每帧都在同一只手里**：同一个动作里，枪或剑**一直是同一只手拿**，照 `<WEAPONS>` 写的；不要这一帧右手、下一帧左手。剑身永远是直的。
3. **不画任何特效**：没有火光、剑光、沙尘、烟、速度线。
4. **跑步要有交替**：两条腿轮流在前，身体有起伏。
5. **脚站稳、比例统一**：整张图按灰色竖条定大小，每一帧用同一个比例；站着的帧脚踩在地面线上、站位点不动；冲刺、倒地的帧按浅色人影的位置和高度。

- 四分之三侧身、**脸朝右前方**，和设计图一样。
- 手臂和身体之间、两腿之间的空隙都是**透明**的。

**像素规则**：和设计图同样大小的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。不画地面、影子、文字；模板上的浅色人影、线、字、格子边框**全部不要留在交付图里**。
**背景**：真透明（每个像素透明度只能是 0 或 255）；做不到透明就用**纯白 #FFFFFF 平涂背景**，人物外面不要任何光晕或阴影。

- 交付：`outputs/samira-actions/<模板同名>.png`（都是 1536×1024，**和模板一样的格子布局**，每帧画在模板对应格子的位置上）；原始生成图原样放进 `outputs/samira-actions/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/samira-actions/HANDOFF.md`（交付说明），再打包成 `outputs/samira_actions_done.zip`。

## 附图（压缩包 `samira_actions_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **每张都附，第一张**：人物、武器、衣服、比例、颜色 |
| `refs/design_1x.png` | 设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：每帧的姿势、位置、大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清身体动作（衣服、特效都不照它） |
| `sheets.json` | 每张模板是哪个动作的第几帧、武器怎么拿、哪些帧沿用 | 对照，填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`。

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a gunslinger woman with long dark teal-black hair swept to the side with gold chains, an eyepatch with a red strap, one green eye, earrings, a tattooed arm, a dark armoured top with red, a gold holster with a silver pistol on her near hip, dark boots, and a greatsword on her back (the hilt with a red tassel at the upper left, the long silver blade one straight line), in 3/4 view facing right. Image 2 is a TEMPLATE of <N> animation frame(s) of her <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose to draw (her old animation frame scaled to her height), the grey horizontal line is the ground, the short tick her standing point, the grey bar on the left her height standing (crown to soles). Image 3 is the same old frame(s) in colour: copy ONLY their body pose and motion - the old costume and the old effects (muzzle flashes, red sword trails, dust) are all wrong. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell draw the character of image 1 in the body pose of that cell's pale figure, at its place and size, soles on the ground line at the standing point when she stands. One scale for the whole sheet, set by the grey bar.
She must be EXACTLY image 1 in every frame: the same hair, face, eyepatch and eye, the same armour, tattoo, holster and boots, image 4's colours only, the same head size, arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned).
THE WEAPONS are image 1's: the silver pistol, the greatsword with its blade ALWAYS ONE STRAIGHT LINE. A weapon stays in the SAME HAND in every frame of this action. <WEAPONS>
NO EFFECTS AT ALL: no muzzle flash, no sword trail, no sparks, no dust, no smoke, no speed lines.
Always 3/4 view, face toward the front-right as in image 1.
THE PIXEL GRID: every square the size of image 1's squares, on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material; no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing.
No ground, no shadow, no text. Remove every template mark: no pale figure, no lines, numbers or cell borders in the result.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<WEAPONS>` 照 `sheets.json` 的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- 每张 1536×1024、和模板一样的格子布局，背景真透明（或纯白），没有模板的浅色人影、线和字。
- 每帧：发型、脸、衣服、纹身和设计图一样，脸朝右前方；头、手臂、腿的大小粗细和设计图一样；只用设计图的颜色；整张一个比例，站着时脚踩地面线、站位点不变。
- **同一个动作里武器一直在同一只手**；剑身是直的。
- **跑步两腿轮流在前、身体有起伏**，8 帧不是同一个姿势。
- 没有任何特效。
- 最后写 `outputs/samira-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/samira_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图），照 `tools/art/casts_gwen_hd.py` 的办法修：脚站稳、`same` 里的帧沿用；**逐帧查武器在哪只手、剑身直不直、跑步换不换腿**（格温的教训）。
- 旧版画进帧里的特效（`samira_bake.json` / `import_samira.py` 的枪口和剑光锚点）要按新枪口、新剑重新定位；做完连同待机、选人卡轮播一起给用户审。
