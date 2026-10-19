# 妖姬：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 妖姬现在游戏里的造型是 1 倍的：从发冠尖到脚底只有 43 格，脸、手和裙子的细节都挤在一起（附图 7）。这次和剑姬、锐雯、卡莎一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从发冠尖到脚底约 **65 格**，细节更清楚。动作帧不用画，我这边按英雄联盟的骨骼来摆。这次画**两张**全身设计图：**A 四分之三侧身朝右**（待机），**S 正侧面朝右**（后面的动作从它摆）。
> - **一定是 Q 版**：上次重画的妖姬比例是真人的（长腿、小头），太逼真，这次**比例照现在的游戏精灵（附图 7）**：头（连头发和发冠）约占身高的**五分之二**，身子和腿短，不要变高变瘦。附图 1–4 的英雄联盟渲染已经把头放大了，但还是没有附图 7 那么 Q，**以附图 7 为准**。
> - **衣服、颜色照附图 6**（之前定下的妖姬原画 A）：
>   - 头：深蓝紫色的齐肩直发，额头上一顶**金色的尖角发冠**（中间一根尖角向上），耳边金色耳饰；**金色眼睛，两只眼睛一样大、一样高**；深色口红；脸颊上有细细的金色纹路。
>   - 身体：金色的立领和胸口金饰；**深蓝色的长裙，胸口深 V**；裙子内衬和背后的**披风是酒红色**，边上是金色的饰边；
>   - 手：黑色长手套，指尖是金色的爪；
>   - 腿：裙子高开衩，露出深色的丝袜和**金色的高跟鞋**。
>   - **法杖**：深酒红色的长杖，比她还高；上半截有一对**黑色的蝙蝠翼状护手**，顶上是一块**亮红色的水晶**；杖底是金色的尖。**法杖一定要直**：杖身是**一条竖直的直线**，从杖底到水晶都在同一列格子上，**不能倾斜、不能弯、不能抖**，粗细一致（约 2 格），护手和水晶左右对称地套在这条直线上。
> - **A 的朝向和姿势**（附图 1）：四分之三侧身，**脸和胸口朝右前方**；**远侧的手（画面右边）握着法杖**，法杖竖直立在她右边、杖底着地；近侧的手（画面左边）垂在身侧、手指微张；两腿并拢稍分开站直，裙子垂下，**两只脚底在同一条地面线上**。近侧的手臂和腿在画面左边、颜色亮，远侧在画面右边、稍暗。
> - **S 的朝向和姿势**（附图 2）：**正侧面朝右**，只看得到一只眼睛；和 A 同样的衣服、颜色、比例、像素格；握法杖的手在身前，法杖竖直；披风和裙摆在身后；两只脚一前一后站在同一条地面线上。
> - **画布**：两张都是 **1024×1024**；**发冠尖到脚底约 715 px，也就是约 65 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），发冠尖碰到附图 8 的浅灰线；头和身子的大小照附图 8 的剪影。法杖顶可以高出发冠。整个人和整根法杖都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金饰要有亮面和暗面；深蓝裙子和深色丝袜要有**偏亮的边**，不要糊成一团黑；红水晶和金色眼睛要亮、成块。附图 9–11 是本包同样密度（PPU 1.5 左右）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**。
> - 不画特效、地面、影子。
> - 交付：`outputs/leblanc-ppu/leblanc-A.png`、`outputs/leblanc-ppu/leblanc-S.png`（都是 1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/leblanc-ppu/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/leblanc_ppu_done.zip`。

## 附图（在压缩包 `leblanc_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_leblanc_idle.png` | 英雄联盟里的妖姬待机，四分之三朝右（头放大了） | **A 的朝向、姿势**、法杖 |
| `refs/2_leblanc_side.png` | 同一帧的正侧面（朝右） | **S 的朝向**、披风、裙摆和腿的前后位置 |
| `refs/3_leblanc_head.png` | 头部特写，四分之三朝右 | 发型、发冠、脸 |
| `refs/4_leblanc_staff_arm.png` | 握法杖的手臂和法杖的特写 | **手套、金爪、蝙蝠翼护手、红水晶** |
| `refs/5_leblanc_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_leblanc_picture.png` | 之前定下的妖姬原画 A | **衣服、颜色、Q 版的感觉照它** |
| `refs/7_leblanc_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，43 格高） | **比例（大头）、身材、朝向** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影（只看位置和大小） | 画布上的位置、脚底线（深灰）、**发冠尖要碰到的线（浅灰）** |
| `style/9_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5，用同样方法重画的） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5，用同样方法重画的） | **只看风格** |
| `style/11_style_kaisa.png` | 本包的卡莎（8 倍，PPU 1.45） | **只看风格**：女性的脸、两只眼睛、细节 |

## 提示词：`leblanc-A.png` 和 `leblanc-S.png`

十一张图都附上，顺序同上表。两张用同一段提示词，各生成一张（第一张 A、第二张 S）。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): an elegant, sly sorceress with a tall staff (1 her idle in 3/4 view facing right - the ANGLE and the POSE for picture A; 2 the same from the exact side, facing right - the view for picture S: the cape, the gown's hem and where the legs stand; 3 her head in 3/4 view facing right: the straight bob, the gold horned crown, the face; 4 her staff arm close up: the black glove with gold claw tips, the staff's black bat-wing guard and red crystal). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved CHIBI picture of her: copy its COSTUME, its COLOURS and its cute big-headed feel. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS - CHIBI: the head with the hair and the crown about TWO FIFTHS of her height, a short body and short legs - its build and its facing. Image 8 is the layout guide: her sprite now as a flat silhouette at the new size - where she goes and how big; the dark grey line is the ground where her soles stand, the light grey line is where the TIP OF HER CROWN goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look (9 and 10 redrawn the same way, 11 a female face with two clear eyes and fine details).
Create TWO pixel-art pictures of her, each a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque): A in 3/4 view facing right, S in exact side view facing right. In both she is about 715 px (about 65 squares) from the tip of her crown to her soles, the soles about 64 px above the bottom edge (the dark grey line of image 8); her head's and body's size as the silhouette of image 8; the staff may rise above the crown; the whole figure and the whole staff inside the picture with margins, nothing cut off; the soles on one ground line.
THE CHARACTER (image 6): HEAD: a shoulder-length straight DARK BLUE-VIOLET bob, a GOLD CROWN on her forehead with one pointed horn rising in the middle, gold ear ornaments, GOLDEN eyes - TWO EYES of the SAME size at the SAME height (picture A), thin gold marks on her cheeks, dark lips. BODY: a high gold collar and gold chest ornament; a DEEP NAVY-BLUE long gown with a deep V neckline; its lining and the CAPE behind her WINE-RED with gold trims. HANDS: long black gloves with GOLD CLAW fingertips. LEGS: the gown slit high, dark sheer stockings, GOLD high heels. THE STAFF: a long dark crimson staff taller than her, a pair of BLACK BAT-WING guards on its upper part, a bright RED CRYSTAL on top, a gold spike at the foot. THE STAFF MUST BE PERFECTLY STRAIGHT: its shaft ONE STRAIGHT VERTICAL LINE of squares from the foot to the crystal, in one column of the grid, NOT tilted, NOT bent, NOT wobbly, the same thickness all along (about 2 squares), the bat-wing guards and the crystal centred on that line.
PROPORTIONS (images 6 and 7): CHIBI - the head with the hair and crown about two fifths of her height, a short body and short legs. NOT realistic proportions, NOT tall and slender.
PICTURE A - THE VIEW AND POSE (image 1): 3/4 view FACING RIGHT like images 1, 3 and 11: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker; the FAR hand (image right) holds the staff standing upright beside her, its foot on the ground; the near hand hangs at her side, fingers a little open; the legs close together and straight, the gown hanging down, both soles on one ground line.
PICTURE S - THE VIEW AND POSE (image 2): EXACT SIDE VIEW FACING RIGHT, only one eye seen; the same costume, colours, proportions and grid as A; the hand holding the staff in front of her, the staff upright; the cape and the gown's hem behind her; one foot a little ahead of the other, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the pictures are read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the gold with clear light and dark faces, the navy gown and the dark stockings with LIGHTER EDGES so they never turn into one dark mass, the red crystal and the golden eyes bright and solid, the hair blue-violet with lighter strands, the skin pale and warm; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 两张都是 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，人物外面没有光晕**；整个人和整根法杖都在画面里。
- **Q 版**：比例照附图 7，头约占身高五分之二，身子和腿短；不是真人比例。
- A **四分之三侧身朝右前方**：两只眼睛一样大、一样高；远侧的手握着竖直的法杖；近侧手臂和腿在画面左边、颜色亮。S **正侧面朝右**。
- 衣服、颜色和附图 6 一样：深蓝紫头发和金发冠、金色眼睛、深蓝长裙、酒红披风和内衬、金饰、黑手套和金爪、金高跟鞋；法杖有黑色蝙蝠翼护手和红水晶，**杖身是竖直的直线、不歪不弯**。
- 发冠尖到脚底约 715 px（约 65 格），脚底在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/leblanc-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/leblanc_ppu_done.zip`，这样我这边才知道已经交付完。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/leblanc/hd/`，**先量 Codex 实际的格子大小**，**按原始生成图自己的格子读回**（`design_fiora_hd.py` / `design_camille_hd.py` 的做法）；需要删行时每段均匀删（`design_rell_cut.even_cut`，脸的行列不删）；12 倍检查脸、按格修眼睛；法杖读回后按一列拉直（用户：「另外法杖别做歪啊」），所有动作里法杖只做平移和直角转，不能歪；和剑姬、锐雯、现在的妖姬按游戏里的大小并排，给用户确认大小和 PPU（不超过 1.5）。
- 定下后照 `tools/art/rig_fiora_hd.py` 的做法按英雄联盟的骨骼摆每个动作（tag、帧数、每帧毫秒数都不变；烤进帧的 `_fx` tag 在新身体上重做），造型给不出的姿势出带骨架的 Codex 部件包；然后 ppu_restyle（`fx=True`）/ ppu_hd / hd.rs、league.dll 版本、头像点、选人卡、预览，开 PR。
