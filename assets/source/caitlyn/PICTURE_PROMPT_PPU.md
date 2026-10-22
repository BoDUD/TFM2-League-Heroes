# 凯特琳：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 凯特琳现在游戏里的造型是 1 倍的：从帽顶到脚底只有 45 格，脸、帽子上的饰条和宝石、步枪的瞄具都挤在一起（附图 7）。这次和锐雯、剑姬、诺手一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从帽顶到脚底约 **68 格**。这次只画**一张**全身设计图；动作之后再逐帧画。
> - **比例照现在的游戏精灵（附图 7）**：头（连帽子和头发）约占身高的三分之一出头；不要更高更瘦，也不要更矮。**步枪的长度照附图 6、7**（细长的狙击枪，比她的身体短一点）。
> - **衣服、颜色照附图 6**（之前定下的凯特琳造型）：
>   - 头：**紫色高礼帽**，前面有金色 V 形饰条和一颗**蓝色圆宝石**；深紫黑色的长发垂到腰；**两只蓝眼睛一样高**，红唇；白色褶边领巾。
>   - 身体：紫色的裙装、棕色皮外套和皮带，金色的扣和饰边。
>   - 腿：深色长袜，棕色长靴，靴口金边。
>   - **步枪**：金色枪身，象牙白护板，青蓝色发光能量线，两个**金框蓝镜片的圆形瞄具**，细长枪管，镂空枪托。
> - **姿势照附图 1**（英雄联盟里的待机）：**双手把长枪斜握在身前，枪托在腰后，枪管斜向右上方，枪口高过肩膀**；两腿站稳，两只脚底在同一条地面线上。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。**帽檐和头发不能挡住眼睛**。
> - **画布用方形 1024×1024**：**帽顶到脚底约 742 px，也就是约 68 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），帽顶碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照附图 1）。整个人和整把枪都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。紫色衣服和帽子要有亮边；长发要有深紫的高光，不要一片死黑；步枪的金色、瞄具的蓝镜片要清楚。附图 9–11 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/caitlyn-ppu/caitlyn-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/caitlyn-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/caitlyn_ppu_done.zip`。

## 附图（在压缩包 `caitlyn_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_caitlyn_idle.png` | 英雄联盟里的凯特琳待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_caitlyn_side.png` | 同一帧，转得更侧 | 枪的位置、外套、帽子的高度 |
| `refs/3_caitlyn_head.png` | 头部特写 | 脸、帽子、头发 |
| `refs/4_caitlyn_rifle.png` | 同一帧，步枪特写 | **步枪的形状、瞄具** |
| `refs/5_caitlyn_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_caitlyn_picture.png` | 之前定下的凯特琳造型 | **衣服、颜色、步枪照它** |
| `refs/7_caitlyn_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，45 格高） | **比例、身材** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**帽顶要碰到的线（浅灰）** |
| `style/9_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5） | **只看风格** |
| `style/11_style_kaisa.png` | 本包的卡莎（8 倍，PPU 1.45） | **只看风格**：女性的脸、两只眼睛 |

## 提示词：`caitlyn-A.png`

附图 1–11，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): a sheriff with a long sniper rifle (1 her idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same turned more to the side: where the rifle sits; 3 her head: the face, the tall hat, the long hair; 4 the same frame close on the rifle: its shape and its two round scopes). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved pixel picture of her: copy its COSTUME, COLOURS and RIFLE. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (the head with the hat and hair a little over a THIRD of her height) - not its pose. Image 8 is THIS picture's layout guide: her sprite now as a flat silhouette at the new size - how big she is and where she stands (not the pose); the dark grey line is the ground where her soles stand, the light grey line is where THE TOP OF HER HAT goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). She is about 742 px (about 68 squares) from the top of her hat to her soles, the soles about 64 px above the bottom edge; the whole figure and the whole rifle inside the picture with margins, nothing cut off; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (image 6): a confident sheriff. HEAD: a tall PURPLE TOP HAT with a gold V-shaped band and ONE round BLUE GEM on the front; long dark purple-black hair falling to her waist; fair skin, two BLUE EYES at the same height, red lips; a white ruffled cravat. BODY: a purple dress, a brown leather coat and belts with gold buckles and trims. LEGS: dark stockings, tall brown boots with gold rims. THE RIFLE: a long slim sniper rifle - a gold body, ivory-white panels, glowing cyan energy lines, TWO round scopes with gold rims and blue lenses, a long thin barrel, an open-frame stock.
PROPORTIONS (image 7): the head with the hat and hair a little over a THIRD of her height - NOT taller or thinner, NOT shorter; the rifle as long as in images 6-7.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker; the hat brim and the hair never cover the eyes.
THE POSE (image 1): both hands holding the rifle diagonally across her body, the stock at her hip behind her, the barrel pointing UP AND TO THE RIGHT, the muzzle above her shoulder; the legs standing firm, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the purple hat and dress with LIT EDGES, the dark hair with purple highlights (never one flat black mass), the rifle's gold and the scopes' blue lenses clear; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势照附图 1**：双手斜握长枪在身前，枪管指向右上；帽顶到脚底约 742 px（约 68 格），两只脚底在同一条线上，脚底以下什么都没有。
- 衣服、颜色和附图 6 一样：紫色高礼帽（金饰条、蓝宝石）、长发、两只蓝眼睛、白领巾、紫裙、棕外套、长靴、金色步枪和两个蓝镜片瞄具。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/caitlyn-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/caitlyn_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**（Codex 的导出图常被重新取样、边上有杂点）：原画和 raw/ 放进 `assets/source/caitlyn/hd/`，照 `tools/art/design_riven_hd.py` 按整张图拟合一个格距和相位读回（拟合范围别包含格距的两倍；背景不透明就先沿描边抠图）；眼睛、嘴照原样；和锐雯、剑姬、卡莎、现在的凯特琳按游戏里的大小并排，给用户确认大小和 PPU（不超过 1.5）。
- 定下后，动作照锐雯第二轮的做法：Codex 按定稿逐帧重画整个人（`tools/art/pack_riven_actions.py` 那种模板：英雄联盟的骨骼按她的身材缩放、地面线、站位点），参考英雄联盟关键帧和 oppi 的凯特琳（`caitlyn2.aseprite`）的画法；她是双手持枪，枪由 Codex 一起画。读回照 `tools/art/actions_riven_hd.py`。烘焙特效照 `caitlyn_bake.json`，给用户看带特效的演示动图。然后 ppu_restyle / ppu_hd / hd.rs、league.dll 版本、头像点、选人卡，开 PR。
