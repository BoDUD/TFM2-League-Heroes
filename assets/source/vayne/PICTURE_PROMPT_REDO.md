# 薇恩：设计图重画（Q 版大头，照现在的精灵，直接按 PPU 1.5 画）（给 Codex 的提示词）

> 上一张（附图 5）的衣服细节很好，但有三个问题，这次要改：
> 1. **头太小**：上一张头只占身高约 1/5，像真人比例。这次要和她**现在的游戏精灵（附图 6）一样是 Q 版大头**：从头顶到下巴约占全身的 **1/3 多一点**（附图 7 的红线就是下巴的位置）。
> 2. **姿势换了**：上一张是两腿大开的新站姿。这次**姿势照附图 6 描**：站着，脸朝右前方，红披风往身后（画面左边）飘到地上，背后的大弩从肩后（画面左边）高过头顶，腕弩在近侧（画面左边）的前臂上。
> 3. **格子太细**：上一张每格只有约 8 像素（太密，缩小后脸会碎）。这次**每格 16 像素**，从最高处到脚底**约 60 格**（960 px）。这就是游戏里最终的密度（PPU 1.5，每个游戏像素画成 1.5 格），之后不会再缩小，所以**每一格都要画得清楚**。
>
> - **衣服和颜色**照附图 5 和附图 6：黑紫色高马尾（红白的发圈）、红墨镜（亮红只用在镜片上）、深红嘴唇、红色高立领、深蓝灰紧身衣和银色护甲、棕色皮带、近侧前臂上带红宝石的银色腕弩、背后银色弩臂棕色弩身的大弩、深色高跟长靴、红披风的撕破下摆。附图 1–3 只看形状和结构，不照它们的颜色。
> - **脸**（最重要，Q 版大头就是为了脸清楚）：两片红色镜片在同一行，中间深色镜框；镜片下面两行是深红的嘴唇；下巴干净，不要有别的深色格；刘海不盖住镜片。
> - **体格不要细**：Q 版的身体，四肢有分量，不要竹竿腿。
> - **朝向**：四分之三侧身，脸和胸口朝右前方；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用竖的 1024×1536**：最高处到脚底约 **960 px（60 格）**，脚底在离画布底边 64 px 的地方（附图 7 的深灰线），最高处碰到浅灰线，**下巴在红线上**（附图 7 只看大小和位置）。整个人、弩和披风都在画面里。
> - **像素块**：大小一致的方块，**每块 16 像素**，横平竖直对齐成网格（Claude 会按 16 像素一格逐格读回）；**外轮廓一圈 1 块宽的近黑描边**；每种材质内部 2–3 档平涂，不要零散的单个杂色格。附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格和格子的粗细**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边、淡淡的杂点**（上一张整个画布上都有很淡的半透明杂点），也不要画黑色或彩色背景。
> - 不画特效、地面、影子；**脚底以下什么都不能有**，披风的尖角也在脚底线以上。
>
> - 交付：`outputs/vayne-redo/vayne-B.png`（1024×1536，**真透明背景**）；原始生成图原样放进 `outputs/vayne-redo/raw/`；附一个 `generation-prompts.txt`。**如果生成图的格子不是正好 16 像素，就在 HANDOFF 里写明实际是多少像素一格、网格从哪个像素开始**。**最后**写 `outputs/vayne-redo/HANDOFF.md`，再打包成 `outputs/vayne_redo_done.zip`。

## 附图（在压缩包 `vayne_redo_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_vayne_idle.png` | 英雄联盟里的薇恩待机 | 马尾、墨镜、披风、两把弩的**形状和结构**（颜色照附图 5、6） |
| `refs/2_vayne_head.png` | 头部特写 | 马尾、墨镜、脸 |
| `refs/3_vayne_back.png` | 从身后看 | 马尾、背后的大弩、披风 |
| `refs/4_vayne_splash.png` | 官方加载画面 | 看气质 |
| `refs/5_vayne_first_take.png` | **上一张设计图** | **只照它的衣服细节和颜色**；头太小、姿势不对、格子太细，这三点不要照 |
| `refs/6_vayne_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，40 格高） | **要描的就是它**：姿势、Q 版比例（大头）、站法 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 大小、脚底线（深灰）、最高处（浅灰）、**下巴（红线）** |
| `style/8_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格和格子粗细** |
| `style/9_style_katarina.png` | 本包的卡特琳娜（8 倍，PPU 1.5） | **只看风格和格子粗细** |
| `style/10_style_leesin.png` | 本包的李青（8 倍，PPU 1.5） | **只看风格和格子粗细** |

## 提示词：`vayne-B.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small chibi pixel-art game sprite of a night huntress standing - a BIG chibi head (crown to chin over a third of her height), a red cape flowing behind her (image left) down to the ground, a big crossbow over her back rising above her head on the image left, a silver wrist crossbow on her near forearm - shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose and those CHIBI PROPORTIONS, at a somewhat finer pixel density (each sprite pixel becomes 1.5 squares). Image 5 is an earlier attempt: copy ONLY its costume details and colours - its head is far too small, its wide stance is wrong and its squares are too fine; do not copy those. Images 1-3 are 3D renders of the same character (1 idle, 2 head close up, 3 from behind): use them ONLY for the shapes of the ponytail, the glasses, the cape and the two crossbows, NOT their colours. Image 4 is the official illustration: the mood. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size; the dark grey line is the ground where her soles stand, the light grey line is her highest point, the RED line is where her CHIN goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at exactly this square density: copy their pixel-art look and how coarse their squares are.
Create ONE pixel-art picture of her, a 1024x1536 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no faint specks anywhere on the canvas, no black or coloured background, no glow). Her highest point is about 960 px (60 squares) above her soles, the soles 64 px above the bottom edge; her chin on the red line of image 7 (the head from crown to chin a bit over a third of her height, as in image 6); the whole figure, both crossbows and the cape inside the picture; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (pose and proportions from image 6, costume and colours from images 5 and 6): BLACK-PURPLE hair in a HIGH PONYTAIL with a red-and-white band; RED SUNGLASSES - two red lenses on one row joined by a dark frame, that bright red used ONLY on the lenses, the fringe not covering them; pale skin; DEEP RED LIPS two rows below the lenses; a clean chin with no other dark squares - the glasses, the mouth and the chin each a clear shape. A RED HIGH COLLAR; a DARK NAVY-SLATE bodysuit with SILVER ARMOUR on the shoulders and knees; BROWN LEATHER STRAPS. A SILVER WRIST CROSSBOW with a red gem on the near forearm; the BIG CROSSBOW behind the near shoulder (image left) rising above her head, silver limbs and a brown stock. DARK HIGH-HEELED BOOTS. A long RED CAPE flowing back (image left), its hem torn into points, reaching down beside her feet. A chibi body with weight - no stick-thin limbs.
THE VIEW: 3/4 view FACING RIGHT as image 6: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 16 px, aligned on one straight grid (the picture is read back square for square); a 1-square near-black outline around the figure; inside it every material in its own 2-3 flat shades, the shadow of a material its own darkest shade (never a second black ring), the crossbows, arms, hair and cape separated by outline; no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her arms and body, between her legs and between the crossbows and her body are transparent.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1536、真透明背景，**每个像素透明度只有 0 或 255**，画布上没有淡淡的杂点、没有光晕、没有黑底。
- **Q 版大头**：下巴在附图 7 的红线上，头顶到下巴占全身 1/3 多一点；**姿势和附图 6 一样**。
- 最高处到脚底约 960 px（60 格）；两只脚底在同一条线上，脚底以下什么都没有。
- **每块 16 像素、大小一致、对齐网格**（做不到就在 HANDOFF 里写明实际格子大小和网格起点）；1 块宽的近黑外描边；没有柔光、渐变、零散杂色格。
- 墨镜、嘴、下巴清楚；马尾、腕弩、背后的大弩、红披风、高跟长靴都在。
- 最后写 `outputs/vayne-redo/HANDOFF.md`，再打包成 `outputs/vayne_redo_done.zip`。

## Claude 收到后（给 Claude 看）

- 原图和 raw/ 放进 `assets/source/vayne/hd/raw/`；`design_vayne_hd.py` 改读 `vayne-B.png`、PITCH 约 16（照 HANDOFF 写的格子），读回后 40 格旧高 → PPU 约 1.5；和李青、锐雯、卡特琳娜、现在的薇恩按游戏大小并排，量头顶到下巴的比例，给用户审。
- 通过后动作包照李青的做法（`pack_leesin_actions.py` → `casts_leesin_hd.py`），头按设计图量，腕弩每帧在同一只手。
