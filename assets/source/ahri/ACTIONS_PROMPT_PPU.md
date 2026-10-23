# 阿狸：施法动作逐帧重画（给 Codex 的提示词）

> 阿狸的定稿设计图（`refs/design.png`，8 倍放大，一格 = 一个像素块；`refs/design_1x.png` 是 1 倍原图）。这次请把她的**四个施法动作每一帧都重新画整个人**，像隔壁 oppi 的阿狸那样（`refs/oppi_*.png`）：**手臂挥动，身体随动作前倾、后仰、扭转，腿迈开站稳，九条尾巴跟着甩动**。**姿势照英雄联盟的同一帧**（`refs/league_*.png`）。待机、跑步、受击、死亡不用画。
>
> 一共 **17 张模板**（`templates/*.png`，每张 1536×1024，一张两帧，每格 768×1024），31 帧：
> - 平A `attack_1..4`（7 帧）：手一挥，第 4 帧把狐火法球甩向敌人，收回
> - Q 欺诈宝珠 `skill_1..4`（8 帧）：手臂往后蓄力，第 4 帧往前甩出宝珠，收回
> - E 魅惑妖术 `skill2_1..4`（7 帧）：手放到嘴边，第 4 帧往前吹出一个飞吻，收回
> - R 灵魄突袭 `ult_1..5`（9 帧）：身体压低往前冲刺，**尾巴拉成一束拖在身后**，冲完站稳
>
> **每一格里**：
> - **灰色横线是地面**，短竖线是她的站位点；**左边的灰色竖条是她站直时从狐耳尖到脚底的高度**（88 格）。
> - **火柴人是英雄联盟这一帧的骨骼**，已经按她的身材缩放过：**蓝色是近侧的手脚**（画面前面那一侧），**灰色是远侧**，**黑圈是她的头（连头发和狐耳）该在的位置和大小**，**两个蓝色小圆圈是她的两只手**，**紫线是英雄联盟里尾巴的走向**。火柴人只用来定**位置和大小**；具体姿势（身体怎么倾、怎么扭、手脚怎么摆）看 `refs/league_<同名>.png` 里同一帧的渲染图。
>
> **人物必须和定稿设计图一模一样**（`refs/design.png`、`refs/design_palette.png` 全部颜色）：
> - 同样的深蓝黑长发、黑色狐耳（粉色耳内）、同样的脸（金黄色眼睛，两只眼睛一样高）、红白和风短上衣、红腰带和紫色挂饰、红色短裙、红色长靴；**只用调色板里的颜色**。
> - **大小不变**：头的大小、身体的宽度、**手臂和腿的长度、粗细每一帧都和设计图一样**（不要拉长、压扁或变粗变细；蹲下就是腿弯曲，不是腿变短）。站直的帧从狐耳尖到脚底 = 灰色竖条的高度。**整张图按灰色竖条定大小，每一帧都用同一个比例**，不要按头的大小一帧一帧单独缩放。
> - **脚踩在地面线上、站位点不变**：每一帧的脚按模板放（不要为了对齐头去挪脚）；在空中的帧按模板的高度。
> - **尾巴是阿狸最重要的特征，每一帧都要大、都要看得见**：设计图里那一大束白色、尾尖淡紫的九尾，从后腰长出来，**每帧都露在身后**（不要被身体或头发挡住）；跟着动作甩动，尾尖比尾根慢半拍；大小和设计图一样（约 36–40 格宽），不要变小。R 冲刺时尾巴拉成一束水平拖在身后。膝盖以下、身前不要有尾巴。
> - 四分之三侧身、**脸朝右前方**，和设计图一样（英雄联盟某些帧转身背对镜头时，也请画成脸朝右前方的样子，只改姿势）。
>
> **画风照 oppi**（`refs/oppi_<动作>.png`，只看动作的画法和力度，**不要照它的衣服、颜色和比例**）：每帧一个清楚的剪影，手臂挥出去时身体顶住动作，脚踩稳；长发和尾巴随动作摆动。
>
> **像素规则**：每块 **6 像素**的方块，横平竖直对齐成网格；外轮廓和设计图一样的近黑描边；每种材质 3–4 档平涂，不要零散的杂色格，不要渐变、模糊、抗锯齿、发光。**不画法球、狐火、爱心、光效等任何特效**（它们是单独的特效图），不画地面、影子、文字；模板上的线、圈、火柴人、字、格子边框**全部不要留在交付图里**。
> **背景**：真透明（每个像素透明度只能是 0 或 255）；如果做不到透明，就用**纯白 #FFFFFF 平涂背景，人物外面不要任何光晕或阴影**。
>
> - 交付：`outputs/ahri-actions/<模板同名>.png`（17 张，都是 1536×1024，**和模板一样的两格布局**，每帧画在模板对应格子的位置上：脚踩地面线、站位点不变；**不用的格子留空，不要多画**）；原始生成图原样放进 `outputs/ahri-actions/raw/`；附 `generation-prompts.txt`（实际用的提示词）；**最后**在同一个文件夹写 `HANDOFF.md`（交付说明），再打包成 `outputs/ahri_actions_done.zip`。

## 附图（压缩包 `ahri_actions_pack.zip`，解压到一个新的文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（8 倍） | **每张都附，第一张**：人物和尾巴的样子、比例、颜色 |
| `refs/design_1x.png` | 定稿设计图 1 倍原图 | 像素块的密度 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第五张**：只用这些颜色 |
| `templates/<名>.png` | 两帧的模板 | **第二张**：每帧的位置、大小、双手、尾巴的走向 |
| `refs/league_<名>.png` | 英雄联盟同样两帧的渲染（Q 版模型；它的尾巴贴着地面，**我们的尾巴照设计图张开**） | **第三张**：每帧的姿势 |
| `refs/oppi_<动作>.png` | oppi 的阿狸同一种动作（4 倍） | **第四张**：动作画法（只看画法） |
| `sheets.json` | 每张模板是哪个动作的第几帧，配哪张 oppi 图 | 对照 |

oppi 图对应：平A → `oppi_attack.png`；Q → `oppi_skill.png`；E → `oppi_skill2.png`；R → `oppi_ult.png`。

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/league_<名>.png`、`refs/oppi_<动作>.png`、`refs/design_palette.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (8x: every square one pixel): a fox-girl mage with long dark navy-black hair, black fox ears with pink insides, golden-yellow eyes, a short red-and-white Korean-style robe with gold trim, a red sash with a violet tassel, a short red skirt, long red boots, and NINE big fluffy WHITE tails with pale violet tips fanned out behind her, in 3/4 view facing right. Image 2 is a TEMPLATE of animation frames of her <ACTION>, frames <N1>-<N2>: in each 768x1024 cell the grey horizontal line is the ground, the short tick is her standing point, the grey bar on the left is her height when standing straight (ear tips to soles); the stick figure is the game's skeleton of that frame fitted to her build (blue = her near arm and leg, grey = the far ones, the black circle = where her head with the hair and ears goes and how big it is, the two small BLUE circles = her hands, the VIOLET line = which way the game model's tails point). Image 3 is the same frames from the game's 3D animation (a chibi model of the same character; its tails hang low): copy each frame's POSE from it - how the body leans and twists, how the arms swing, where the legs go. Image 4 is another pixel artist's version of this character doing this kind of move: copy only HOW IT IS ANIMATED (a strong readable silhouette, the arms swinging, the body bracing into the move, feet planted, hair and tails swinging), not its costume, colours or proportions. Image 5 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if transparency is impossible, a flat pure white background with no glow and no shadow), the SAME two-cell layout as image 2: in each used cell draw the character of image 1 in that frame's pose of image 3, placed and sized by image 2: her soles on the ground line at the standing point as image 2 shows them (unless she is in the air), her head where the black circle is and as big, her hands in the blue circles. The whole sheet at ONE scale set by the grey bar - never rescale a frame on its own to fit its head. Leave unused cells empty.
She must be EXACTLY image 1 in every frame: the same hair, ears, face with both golden eyes at the same height, the same robe, sash, skirt and boots, the same colours (image 5 only), the same head size, her arms and legs the SAME LENGTH AND THICKNESS as in image 1 (bent, never stretched, shortened, thickened or thinned). HER NINE TAILS ARE HER MOST IMPORTANT FEATURE: in EVERY frame the big white fan of tails of image 1, the same size (about 36-40 squares wide), growing from her lower back and clearly VISIBLE behind her - never hidden behind her body or hair, never shrunk; they swing with the move, the tips lagging behind the roots; in the dash (Spirit Rush) they stream out in one bundle level behind her; no tail below her knees or in front of her. Always the 3/4 view with the face toward the front-right, as image 1, even where the game model turns away.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid; the near-black outline of image 1 around the figure; 3-4 flat shades per material, no stray single odd squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
No orb, no fox-fire, no hearts, no sparkles, no effects, no ground, no shadow, no text. Remove every template mark: no lines, circles, stick figures, numbers or cell borders in the result.
```

`<ACTION>` / `<N1>-<N2>` 照 `sheets.json` 的 `action` 和 `frames` 填，例如 `attack_2`：`basic attack, a spirit orb flicked from her hand at the foe (Ahri_Attack1)`、`3-4`。

## 交回前请检查

- 17 张，每张 1536×1024、两格布局，背景真透明（或纯白），没有模板的线和圈。
- 每帧：脸朝右前方、两只眼睛一样高；头、手臂、腿的大小和粗细和设计图一样；只用设计图的颜色；**整张一个比例，脚踩地面线、站位点不变**。
- **每帧都看得见九尾**，和设计图一样大，白色带淡紫尾尖，从后腰长出来；R 冲刺时拉成一束拖在身后。
- 出手那一帧（平A 第 4 帧、Q 第 4 帧、E 第 4 帧）手朝前方伸出。
- 画完后最后写 `outputs/ahri-actions/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ahri_actions_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原始生成图（不读导出图），照 `tools/art/casts_lux_hd.py` 的办法修：按站直那帧的眼睛到地面的高度定每张的比例，头换成设计图的头（对准近侧眼睛，挡在脸前的手臂保留），脚站稳；查每帧尾巴的大小和是否露出；放进阿狸的 rig（跑步、受击、死亡、待机由设计图的部件摆）；平A、Q 的出手高度照出手帧的手重算。
