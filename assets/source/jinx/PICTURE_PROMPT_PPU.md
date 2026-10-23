# 金克丝：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 金克丝现在游戏里的造型是 1 倍的：从头顶到脚底只有 37 格，脸、衣服、两条辫子和机枪“砰砰”的细节都挤成一团（附图 7）。这次和凯特琳、韦鲁斯、锐雯一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从头顶到脚底约 **56 格**。这次只画**一张**全身设计图；动作之后再逐帧画。
> - **比例照现在的游戏精灵（附图 7）**：头（连头发）约占身高的三分之一，身材纤细；不要更高更瘦，也不要更矮。**机枪的大小照附图 6、7**（从她的腰边一直伸到身前，差不多和她的腿一样长）。
> - **衣服、颜色照附图 6**（之前定下的金克丝造型），细节看附图 1–4：
>   - 头：**亮蓝色头发**，刘海斜搭在额前，脑后**两条很长的蓝色麻花辫**一直垂到脚踝附近，辫梢有**粉红色的发圈**，末端散开；苍白的脸、**粉红色的眼睛**、咧嘴坏笑，**两只眼睛一样高、都看得见**。
>   - 上身：苍白的皮肤，纤细；**黑色的细带抹胸**；手臂上**粉红和黑色的护腕、半指手套**，左臂一圈子弹带。
>   - 腰：一条**挂满铜色子弹的子弹腰带**和粉红色腰带；腰侧挂着**电击枪“砰砰枪”**（铜色枪身、一节**发青光的玻璃管**）。
>   - 下身：很短的深色短裤；**一条腿穿粉紫条纹长袜**（附图 1 里画面左边那条腿），另一条腿光着、膝盖有一小块蓝色云朵纹身；**黑色系带作战靴**。
>   - **机枪“砰砰”**：一把**粉紫色的转管机枪**，四根粗枪管、枪身侧面有**发粉光的窗**，枪身上竖着两只**淡绿色的鲨鱼耳朵**；她用**两只手端在腰边**，枪口朝右（附图 1、4、6）。
>   - **背上要画鲨鱼火箭炮“鱼骨头”**（附图 1–3 里背上那个东西，附图 6 里没画清楚，这次照附图 1–3 补上）：一个**紫色的鲨鱼头形火箭筒**，斜挎在背后、**从她身后（画面左边）的肩膀上露出来**，鲨鱼头朝上；**橙黄色的眼睛**、红色的战纹、一排**白色尖牙**、身上有几根尖刺和一排圆孔，一条**铜色皮带**把它绑在身上。它在身体**后面**，**绝对不能挡住脸**，也不要比她的头大太多（大小比例照附图 1）。
> - **姿势照附图 1**（英雄联盟里端机枪的待机）：微微弓身、两腿分开站稳，机枪端在腰边、枪口朝右前方，两条辫子垂在身后；两只脚底在同一条地面线上。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。近侧的手臂和腿颜色亮，远侧稍暗。
> - **画布用方形 1024×1024**：**头顶到脚底约 610 px，也就是约 56 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），头顶碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照附图 1）。整个人、两条辫子、背上的鱼骨头和整把机枪都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。蓝头发要有深蓝的阴影和浅青的高光，一节一节的麻花辫要看得出来，不要一片死蓝；黑色抹胸和短裤要和描边分得开（用深灰紫，不要和描边一样黑）；粉色机枪、铜色子弹、青色玻璃管要清楚。附图 9–11 是本包同样密度（PPU 1.35–1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/jinx-ppu/jinx-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/jinx-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/jinx_ppu_done.zip`。

## 附图（在压缩包 `jinx_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_jinx_idle.png` | 英雄联盟里的金克丝端机枪待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_jinx_side.png` | 同一帧，转得更侧 | 机枪的位置、辫子垂下的样子、**背上的鱼骨头** |
| `refs/3_jinx_head.png` | 头部特写 | 脸、刘海、麻花辫、鱼骨头的鲨鱼头 |
| `refs/4_jinx_minigun.png` | 同一帧，机枪和腰特写 | **机枪的形状**、子弹腰带、电击枪、长袜 |
| `refs/5_jinx_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_jinx_picture.png` | 之前定下的金克丝造型 | **衣服、颜色、机枪照它** |
| `refs/7_jinx_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，37 格高） | **比例、身材** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/9_style_caitlyn.png` | 本包的凯特琳（8 倍，PPU 1.45） | **只看风格**：女性、身材 |
| `style/10_style_varus.png` | 本包的韦鲁斯（8 倍，PPU 1.35） | **只看风格** |
| `style/11_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`jinx-A.png`

附图 1–11，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): a wild, grinning gunner girl with two very long blue braids, carrying a pink minigun and a shark-headed rocket launcher on her back (1 her idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same turned more to the side: where the minigun is held, how the braids hang, the shark launcher on her back; 3 her head: the face, the bangs, the braids, the shark launcher's head; 4 the same frame close on the minigun and the hips: the gun's shape, the bullet belt, the small zapper pistol, the stocking). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved pixel picture of her: copy its COSTUME, COLOURS and MINIGUN. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (the head with the hair about a THIRD of her height, a slim build) - not its pose. Image 8 is THIS picture's layout guide: her sprite now as a flat silhouette at the new size - how big she is and where she stands (not the pose); the dark grey line is the ground where her soles stand, the light grey line is where THE TOP OF HER HEAD goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). She is about 610 px (about 56 squares) from the top of her head to her soles, the soles about 64 px above the bottom edge; the whole figure, both braids, the launcher on her back and the whole minigun inside the picture with margins, nothing cut off; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (image 6): a manic, grinning gunner girl. HEAD: BRIGHT BLUE hair, bangs swept across the brow, TWO VERY LONG BLUE BRAIDS hanging behind her down to about her ankles, PINK hair ties near the ends, the tips fanning out; a pale face, PINK eyes, a wide wicked grin, the two eyes at the same height, both visible. BODY: pale skin, slim; a BLACK strappy bikini top; PINK-and-black arm guards and fingerless gloves, a ring of bullets on one arm. HIPS: a belt of BRASS BULLETS over a pink belt; a small zapper pistol hanging at her hip (brass body, one glowing CYAN glass tube). LEGS: very short dark shorts; ONE leg in a PINK-and-PURPLE striped stocking (the leg on the image left in image 1), the other leg bare with a small blue cloud tattoo at the knee; BLACK laced combat boots. THE MINIGUN: a PINK-PURPLE rotary minigun with four thick barrels, glowing PINK windows on its side and two pale green shark ears standing up on it, held in both hands at her hip, the muzzles pointing right. THE ROCKET LAUNCHER ON HER BACK (images 1-3; image 6 does not show it clearly - add it as images 1-3 show it): a PURPLE SHARK-HEADED rocket launcher slung across her back, showing over her back shoulder (on the image LEFT), the shark head pointing up; an ORANGE-YELLOW eye, red war paint, a row of WHITE TEETH, a few spikes and a row of round holes on its body, a BRASS strap holding it on. It is BEHIND her body: it must NEVER cover her face, and it is about as big as in image 1 (not much bigger than her head).
PROPORTIONS (image 7): the head with the hair about a THIRD of her height, slim - NOT taller or thinner, NOT shorter; the minigun as big as in image 6.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg in full tone, the far ones a step darker.
THE POSE (image 1): slightly crouched, feet apart and planted, the minigun held low at her hip in both hands, the muzzles to the front-right, the two braids hanging behind her; both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the blue hair with dark blue shading and light cyan highlights, the braids' plaits readable (never one flat blue mass); the black top and shorts in dark grey-violet shades that read apart from the outline; the pink minigun, the brass bullets and the cyan glass tube clear; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no rockets or bullets in the air, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势照附图 1**：微弓身、两腿分开，机枪端在腰边、枪口朝右；头顶到脚底约 610 px（约 56 格），两只脚底在同一条线上，脚底以下什么都没有。
- 衣服、颜色和附图 6 一样：亮蓝头发和两条长麻花辫（粉红发圈）、粉红眼睛、黑色抹胸、粉黑护腕、子弹腰带、腰间的电击枪、一条粉紫条纹长袜、黑色作战靴、粉紫色的四管机枪；**背上有紫色的鲨鱼火箭炮“鱼骨头”**（从身后的肩膀露出、不挡脸）。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/jinx-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/jinx_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/jinx/hd/`，照 `tools/art/design_varus_hd.py` 按整张图拟合一个格距和相位读回；量**身体**高度（头顶到脚底，不算辫子和枪），和现在的 37 格对齐选 PPU（不超过 1.5），和凯特琳、韦鲁斯、锐雯按游戏里的大小并排给用户确认。
- 定下后照韦鲁斯的做法由 Claude 按设计图的部件逐帧摆动作（`rig_varus_hd.py`：无损部件、四肢照设计图的颜色和宽度）；火箭炮“鱼骨头”从背上取下来就是 rocket / ult 动作的武器部件（背着时是身体的一部分，扛起时整件无损搬到肩上）；子弹和火箭的出发高度照新枪口重算（FX_AT、y_offset）；ppu_restyle 的 EXACT 宽度规则、塞拉斯 / 佛耶戈 / 妮蔻灵魂表、待机和选人卡轮播等适配。
