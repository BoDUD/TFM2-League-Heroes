# 韦鲁斯：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 韦鲁斯现在游戏里的造型是 1 倍的：从头顶到脚底只有 40 格，脸、护符、腐化的手臂和大弓的细节都挤在一起（附图 7）。这次和凯特琳、锐雯、诺手一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从头顶到脚底约 **60 格**。这次只画**一张**全身设计图；动作之后再逐帧画。
> - **比例照现在的游戏精灵（附图 7）**：头（连头发）约占身高的三分之一，身材精瘦；不要更高更瘦，也不要更矮。**大弓的大小照附图 6、7**（差不多和他的身体一样高）。
> - **衣服、颜色照附图 6**（之前定下的韦鲁斯造型）：
>   - 头：**银白色头发往后梳、在脑后扎起**；额头一条细细的深色头带，中间一颗**红宝石**；瘦长的脸、表情阴沉，**两只眼睛一样高、都看得见**。脖子上一条**鲜红色围巾**，红布尾巴飘在身后。
>   - 上身：赤裸的灰白色皮肤，精瘦有肌肉，右肩一道青色纹身；胸前斜挎一条深色皮带，挂着一个**大圆护符（金边、中间深青色玻璃）**。
>   - 腐化：两只手臂**从手肘往下变成暗红再变成紫色**，手是爪子，指尖发**紫光**；肚子和胯部渐变成暗红色。
>   - 下身：贴身的**深紫黑色铠甲裤**，一节一节的甲片、膝盖有小尖刺、点缀发紫光的小点；深紫色厚靴子；腰前垂几条暗红布条。
>   - **弓**：一把**巨大的深紫黑色活体暗裔之弓**，由带尖刺、像爪子和骨头的弯甲组成，有发**紫光的纹路**，握把处一团亮紫光；拿在**远侧的手**（附图 1、6 里拿弓的那只手）。
> - **姿势照附图 1**（英雄联盟里的待机）：站着、微微驼背，**握弓的手提着大弓垂在腿边**，另一只手垂在身侧；两腿站稳，两只脚底在同一条地面线上。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用方形 1024×1024**：**头顶到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），头顶碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照附图 1）。整个人和整把弓都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。银发要有浅灰的阴影，不要一片死白；红围巾、金色护符、紫色发光纹路要清楚。附图 9–11 是本包同样密度（PPU 1.45–1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/varus-ppu/varus-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/varus-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/varus_ppu_done.zip`。

## 附图（在压缩包 `varus_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_varus_idle.png` | 英雄联盟里的韦鲁斯待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_varus_side.png` | 同一帧，转得更侧 | 弓的位置、围巾尾巴、扎起的头发 |
| `refs/3_varus_head.png` | 头部特写 | 脸、头发、头带、围巾、护符 |
| `refs/4_varus_bow.png` | 同一帧，弓和手臂特写 | **弓的形状、腐化的手** |
| `refs/5_varus_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_varus_picture.png` | 之前定下的韦鲁斯造型 | **衣服、颜色、弓照它** |
| `refs/7_varus_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，40 格高） | **比例、身材** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/9_style_caitlyn.png` | 本包的凯特琳（8 倍，PPU 1.45） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |
| `style/11_style_darius.png` | 本包的诺手（8 倍，PPU 1.45） | **只看风格**：男性、身材 |

## 提示词：`varus-A.png`

附图 1–11，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (his head enlarged toward a game sprite's proportions): a gaunt archer corrupted by darkness, carrying a huge living bow (1 his idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same turned more to the side: where the bow hangs, the scarf's tail, the tied-back hair; 3 his head: the face, the hair, the headband, the scarf and the amulet; 4 the same frame close on the bow and the corrupted hands). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved pixel picture of him: copy its COSTUME, COLOURS and BOW. Image 7 is his small game sprite now, shown 8x: copy its PROPORTIONS (the head with the hair about a THIRD of his height, a lean build) - not its pose. Image 8 is THIS picture's layout guide: his sprite now as a flat silhouette at the new size - how big he is and where he stands (not the pose); the dark grey line is the ground where his soles stand, the light grey line is where THE TOP OF HIS HEAD goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). He is about 660 px (about 60 squares) from the top of his head to his soles, the soles about 64 px above the bottom edge; the whole figure and the whole bow inside the picture with margins, nothing cut off; both soles on one ground line; nothing at all below his soles.
THE CHARACTER (image 6): a grim, haunted archer. HEAD: SILVER-WHITE hair swept back and tied behind; a thin dark headband with one RED GEM on the brow; a gaunt face, the two eyes at the same height, both visible. A bright RED SCARF round the neck, its tail trailing behind. BODY: bare grey-white skin, lean and muscled, a teal tattoo on the shoulder; a dark strap across the chest holding a big round AMULET (gold rim, dark teal glass). CORRUPTION: both arms turn from dark red to PURPLE below the elbows, the hands are claws with glowing PURPLE fingertips; the belly and hips shade into dark red. LEGS: fitted dark purple-black segmented armour trousers with small spikes at the knees and glowing purple dots, heavy dark purple boots, a few short dark red cloth strips hanging from the belt. THE BOW: a HUGE dark purple-black living bow almost as tall as he is, made of spiked claw- and bone-like curved plates with glowing PURPLE lines and a bright purple glow at the grip.
PROPORTIONS (image 7): the head with the hair about a THIRD of his height, lean - NOT taller or thinner, NOT shorter; the bow as big as in image 6.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE POSE (image 1): standing, slightly hunched, the bow hand holding the great bow low by his leg, the other arm hanging at his side; the legs standing firm, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the silver hair with light grey shading (never one flat white mass), the red scarf, the gold amulet and the glowing purple lines clear; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no arrows, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势照附图 1**：站着、微驼，大弓提在腿边；头顶到脚底约 660 px（约 60 格），两只脚底在同一条线上，脚底以下什么都没有。
- 衣服、颜色和附图 6 一样：银白后梳的头发、红宝石头带、红围巾、金边护符、腐化的紫红手臂和发光爪子、深紫铠甲裤和靴子、巨大的紫黑活体弓。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/varus-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/varus_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/varus/hd/`，照 `tools/art/design_caitlyn_hd.py` 按整张图拟合一个格距和相位读回；和凯特琳、锐雯、诺手、现在的韦鲁斯按游戏里的大小并排，给用户确认大小和 PPU（不超过 1.5）。
- 定下后照凯特琳的做法：Codex 逐帧重画动作（`pack_caitlyn_actions.py` 的模板），读回照 `actions_caitlyn_hd.py`；弓如果歪了、变形了，按 `rifle_caitlyn.py` 的思路由 Claude 逐格画正再贴；箭的出发高度和空帧照新弓口重算；烘焙特效照 `varus_bake.json`。查塞拉斯、佛耶戈 / 妮蔻灵魂表、待机和选人卡轮播等适配。
