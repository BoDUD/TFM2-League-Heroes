# 拉克丝：施法动作逐帧重画（给 Codex 的提示词）

> 拉克丝的定稿设计图（`refs/design.png`，8 倍放大，一格 = 一个像素块；`refs/design_1x.png` 是 1 倍原图）。这次请把她的**四个施法动作每一帧都重新画整个人和她的法杖**，像隔壁 oppi 的拉克丝那样（`refs/oppi_*.png`）：**手臂挥动、法杖抡起来**，身体随动作前倾、后仰、扭转，腿迈开站稳。**姿势照英雄联盟的同一帧**（`refs/league_*.png`）。待机、跑步、受击、死亡不用画。
>
> 一共 **15 张模板**（`templates/*.png`，每张 1536×1024，一张两帧，每格 768×1024），28 帧：
> - 平A `attack_1/2/3`（6 帧）：法杖从身后抡过头顶，第 4 帧往前推出、杖头对准敌人，收回
> - Q 光之束缚 `skill_1/2/3/4`（7 帧）：举起法杖，第 3 帧往前推出，收回
> - E 透光奇点 `skill2_1/2/3/4`（7 帧）：法杖往后甩，第 5 帧往前甩出光球，收回
> - R 终极闪光 `ult_1/2/3/4`（8 帧）：她跳起，**法杖离手浮在身前**、杖头对准前方蓄力发射，她在空中蜷身，落地站起
>
> **每一格里**：
> - **灰色横线是地面**，短竖线是她的站位点；**左边的灰色竖条是她站直时从头顶到脚底的高度**（81 格）。
> - **火柴人是英雄联盟这一帧的骨骼**，已经按她的身材缩放过：**蓝色是近侧的手脚**（画面前面那一侧，握法杖的手），**灰色是远侧**，**黑圈是她的头（连头发）该在的位置和大小**。火柴人只用来定**位置和大小**；具体姿势（身体怎么倾、怎么扭、手脚怎么摆）看 `refs/league_<同名>.png` 里同一帧的渲染图。
> - **两个蓝色小圆圈是她的两只手**，**红线是法杖**（长度就是设计图里那根法杖的长度），**红色实心圆是月牙杖头**（带蓝宝石的那一端，`refs/staff.png`）：法杖顺着红线画，月牙杖头画在红圆那一端，近侧的手握在杖上；R 里法杖离手时，它浮在红线的位置。
>
> **人物和法杖必须和定稿设计图一模一样**（`refs/design.png`、`refs/design_palette.png` 全部颜色）：
> - 同样的金色长发、深蓝头冠、同样的脸（两只蓝眼睛一样高）、白金轻铠、深蓝腰带和护腿、白裙甲、金色护膝和靴尖；**只用调色板里的颜色**。
> - **大小不变**：头的大小、身体的宽度、**手臂和腿的长度、粗细每一帧都和设计图一样**（不要拉长、压扁或变粗变细；蹲下就是腿弯曲，不是腿变短）。站直的帧从头顶到脚底 = 灰色竖条的高度。
> - **法杖每一帧都一样长、一样粗、笔直**（`refs/staff.png`：白金杖身、金色螺旋，一头是带蓝宝石的金色月牙杖头，另一头是金色小叉）：**杖身是一根刚性的直杆**，握手前后的杖身在同一条直线上，不弯、不断、不变短。
> - 四分之三侧身、**脸朝右前方**，和设计图一样（英雄联盟某些帧转身背对镜头或在空中翻身时，也请画成脸朝右前方的样子，只改姿势）。
>
> **画风照 oppi**（`refs/oppi_<动作>.png`，只看动作的画法和力度，**不要照它的衣服、颜色和比例**）：每帧一个清楚的剪影，挥杖时手臂和法杖一起动，身体顶住动作，脚踩稳；长发随动作摆动。
>
> **像素规则**：每块 **6 像素**的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**不画光球、光束、激光、光晕等任何特效**，不画地面、影子、文字；模板上的线、圈、火柴人、字、格子边框**全部不要留在交付图里**。
> **背景**：真透明（每个像素透明度只能是 0 或 255）；如果做不到透明，就用**纯白 #FFFFFF 平涂背景，人物外面不要任何光晕或阴影**。
>
> - 交付：`outputs/lux-actions/<模板同名>.png`（15 张，都是 1536×1024，**和模板一样的两格布局**，每帧画在模板对应格子的位置上：脚踩地面线、站位点不变；**不用的格子留空，不要多画**）；原始生成图原样放进 `outputs/lux-actions/raw/`；附 `generation-prompts.txt`（实际用的提示词）；**最后**在同一个文件夹写 `HANDOFF.md`（交付说明），再打包成 `outputs/lux_actions_done.zip`。

## 附图（压缩包 `lux_actions_pack.zip`，解压到一个新的文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（8 倍） | **每张都附，第一张**：人物和法杖的样子、比例、颜色 |
| `refs/design_1x.png` | 定稿设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | 只用这些颜色 |
| `refs/staff.png` | 设计图里的法杖单独放大（8 倍） | **第五张**：法杖的样子，哪头是月牙杖头 |
| `templates/<名>.png` | 两帧的模板 | **第二张**：每帧的位置、大小、双手、法杖 |
| `refs/league_<名>.png` | 英雄联盟同样两帧的渲染（Q 版模型；它的法杖两头一样，比我们的短） | **第三张**：每帧的姿势 |
| `refs/oppi_<动作>.png` | oppi 的拉克丝同一种动作（4 倍） | **第四张**：动作画法（只看画法） |
| `sheets.json` | 每张模板是哪个动作的第几帧，配哪张 oppi 图 | 对照 |

oppi 图对应：平A → `oppi_attack.png`；Q → `oppi_skill.png`；E → `oppi_skill2.png`；R → `oppi_ult.png`。

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/league_<名>.png`、`refs/oppi_<动作>.png`、`refs/staff.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a young light mage with long golden blonde hair, a dark blue tiara, two blue eyes, light white-and-gold armour, a dark blue belt and leggings, a white armour skirt, gold knee guards and boot toes, and a long straight white-gold staff wound with a gold spiral, a gold crescent head with a blue gem at one end and a small gold fork at the other, in 3/4 view facing right. Image 2 is a TEMPLATE of animation frames of her <ACTION>, frames <N1>-<N2>: in each 768x1024 cell the grey horizontal line is the ground, the short tick is her standing point, the grey bar on the left is her height when standing straight (hair top to soles); the stick figure is the game's skeleton of that frame fitted to her build (blue = her near arm and leg - the near hand holds the staff -, grey = the far ones, the black circle = where her head with the hair goes and how big it is); the two small BLUE circles are her hands, the RED line is her staff (as long as image 1's) and the filled RED circle is the staff's crescent head. Image 3 is the same frames from the game's 3D animation (a chibi model of the same character; its staff is shorter and the same at both ends): copy each frame's POSE from it - how the body leans and twists, how the arms swing, where the legs and the staff go. Image 4 is another pixel artist's version of this character doing this kind of move: copy only HOW IT IS ANIMATED (a strong readable silhouette, the arms and the staff swinging, the body bracing into the move, feet planted), not its costume, colours or proportions. Image 5 is image 1's staff alone, 8x: the crescent head with the blue gem and the small fork end.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if transparency is impossible, a flat pure white background with no glow and no shadow), the SAME two-cell layout as image 2: in each used cell draw the character of image 1 in that frame's pose of image 3, placed and sized by image 2: her soles on the ground line (unless she is in the air), her head where the black circle is and as big, her hands in the blue circles, the staff along the red line with its crescent head at the red circle (her near hand on it; where image 3 shows the staff floating free of her hands, it floats there). Leave unused cells empty.
She and her staff must be EXACTLY those of image 1 in every frame: the same hair, tiara, face with both eyes at the same height, the same colours (image 1's colours only), the same head size, her arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned), the staff always the same length and thickness and perfectly STRAIGHT - one rigid rod, the same line on both sides of her hand. Always the 3/4 view with the face toward the front-right, as image 1, even where the game model turns away or flips in the air.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material, no stray single odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No light orbs, no beams, no lasers, no sparkles, no effects, no ground, no shadow, no text. Remove every template mark: no lines, circles, stick figures, numbers or cell borders in the result.
```

`<ACTION>` / `<N1>-<N2>` 照 `sheets.json` 的 `action` 和 `frames` 填，例如 `attack_2`：`basic attack, the staff swung round over her and thrust at the foe (lux_attack1)`、`3-4`。

## 交回前请检查

- 15 张，每张 1536×1024、两格布局，背景真透明（或纯白），没有模板的线和圈。
- 每帧：脸朝右前方、两只眼睛一样高；头、手臂、腿的大小和粗细和设计图一样；只用设计图的颜色。
- **法杖每帧笔直、一样长**，月牙杖头在模板红圆那一端；施法出手那一帧（平A 第 4 帧、Q 第 3 帧、E 第 5 帧、R 第 4 帧）杖头对准前方。
- 画完后最后写 `outputs/lux-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/lux_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图）：照 `actions_caitlyn_hd.py` 按脸、头的面积定比例，读回每块的格子，颜色贴回设计图的调色板；歪了的法杖换成 `design_lux_hd.shaft` 那样代码画的直杖身加设计图自己的两端饰件；头照设计图逐格对位；放进 `rig_lux_hd.py` 的施法动作（跑步、受击、死亡、待机不变），光弹、Q、R 的出发高度照出手帧的杖头重算。
