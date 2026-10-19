# 阿狸：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 阿狸现在游戏里的造型是 1 倍的：从狐耳尖到脚底只有 40 格，脸、衣服的金饰和尾巴的层次都挤在一起（附图 6）。这次和妖姬、剑姬、卡莎一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从狐耳尖到脚底约 **60 格**，细节更清楚。动作帧不用画，我这边按英雄联盟的骨骼来摆。这次画**两张**全身设计图：**A 四分之三侧身朝右**（待机），**S 正侧面朝右**（后面的动作从它摆）。
> - **一定是 Q 版**：比例照现在的游戏精灵（附图 6）：头（连头发和狐耳）约占身高的**五分之二**，身子和腿短，不要变高变瘦。附图 1–4 的英雄联盟渲染已经把头放大了，但还是没有附图 6 那么 Q，**以附图 6 为准**。
> - **衣服、颜色照附图 1、3、5**（英雄联盟原版的阿狸）：
>   - 头：**很深的藏青黑色长发**，有蓝色的亮丝，前面的刘海和两侧的发束垂到胸前，**身后一条粗辫子**；头顶一对**狐耳：外面是黑色，里面是粉色**；**金色眼睛，两只眼睛一样大、一样高**；两颊各有三道**暗红色的狐须纹**；嘴是淡淡的粉色。
>   - 身体：**露肩的红色上衣**，领口一圈**白边**；**紫色的腰封**，上面有金色的饰纹和一个金色的圆扣，腰侧挂一条**紫色的流苏**；**白色的短裙**，裙摆有红边和金色的花纹；
>   - 手臂：**红色的长袖套**，袖口是**白色**的宽边，袖上有金色的纹样；手指上是**暗红色的指甲**；
>   - 腿：皮肤白皙，**大腿上一条红色的腿环**；**红色的长靴，靴口白边**，靴筒下面露出深色的绑腿。
>   - **九条尾巴**：**淡紫白色的狐尾**（白里带一点淡紫，暗面是淡紫灰），毛尖略带紫色；**九条收成身后的一束**：从**后腰**长出来，向**画面左上方**扬开成扇形，**尾尖在腰和头顶之间**，像附图 6 那样；**膝盖以下不要有尾巴，尾巴不能拖到地上，也不能挡在身前**；尾巴要看得出是一条条分开的（每条有自己的描边和亮面），但**不要大过身体**：整束大约是附图 6 里的大小（按新尺寸约 35 × 42 格）。附图 1、2、4 里英雄联盟的尾巴太大、一直拖到地上，**不要照它的大小**，只看毛色和形状。
> - **A 的朝向和姿势**（附图 1、6）：四分之三侧身，**脸和胸口朝右前方**；近侧的手臂和腿在画面左边、颜色亮，远侧在画面右边、稍暗；手臂放松：近侧的手垂在身侧，远侧的手微微抬到胸前（照附图 6）；两腿并拢稍分开站直，**两只脚底在同一条地面线上**；尾巴在身后左上方。
> - **S 的朝向和姿势**（附图 2）：**正侧面朝右**，只看得到一只眼睛；和 A 同样的衣服、颜色、比例、像素格；辫子和尾巴在身后（画面左边），尾巴同样从后腰向左上方扬开、不拖地；两只脚一前一后站在同一条地面线上。
> - **画布**：两张都是 **1024×1024**；**狐耳尖到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），狐耳尖碰到附图 7 的浅灰线；头、身子和尾巴的大小照附图 7 的剪影。整个人和整束尾巴都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金饰要有亮面和暗面；深色头发要有**偏亮的蓝色发丝**，不要糊成一团黑；白色的尾巴和裙子要有淡紫灰的暗面，**不要一片白看不出层次**；金色眼睛要亮、成块。附图 8–10 是本包同样密度（PPU 1.5–2.0）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**。
> - 不画特效（宝珠、狐火、爱心都不要）、地面、影子。
> - 交付：`outputs/ahri-ppu/ahri-A.png`、`outputs/ahri-ppu/ahri-S.png`（都是 1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/ahri-ppu/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/ahri_ppu_done.zip`。

## 附图（在压缩包 `ah_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ahri_idle.png` | 英雄联盟里的阿狸待机，四分之三朝右（头放大了） | **A 的朝向**、衣服、颜色 |
| `refs/2_ahri_side.png` | 同一帧的正侧面（朝右） | **S 的朝向**、辫子、腿的前后位置 |
| `refs/3_ahri_head.png` | 头部特写，四分之三朝右 | 发型、狐耳、脸、狐须纹 |
| `refs/4_ahri_tails.png` | 尾巴的特写 | **尾巴的毛色和形状**（大小不要照它） |
| `refs/5_ahri_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_ahri_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，40 格高） | **比例（大头）、身材、朝向、尾巴收成一束的样子和大小** |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影（只看位置和大小） | 画布上的位置、脚底线（深灰）、**狐耳尖要碰到的线（浅灰）** |
| `style/8_style_leblanc.png` | 本包的妖姬（8 倍，PPU 2.0，用同样方法重画的） | **只看风格** |
| `style/9_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_kaisa.png` | 本包的卡莎（8 倍，PPU 1.45） | **只看风格**：女性的脸、两只眼睛、细节 |

## 提示词：`ahri-A.png` 和 `ahri-S.png`

十张图都附上，顺序同上表。两张用同一段提示词，各生成一张（第一张 A、第二张 S）。

```text
Ten attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): a graceful fox-spirit girl with nine tails (1 her idle in 3/4 view facing right - the ANGLE, the costume and the colours for picture A; 2 the same from the exact side, facing right - the view for picture S: the braid and where the legs stand; 3 her head in 3/4 view facing right: the long hair, the fox ears, the face with the whisker marks; 4 her tails close up: the fur colour and the tail shape ONLY - NOT their size). Image 5 is the official illustration: the mood and the colours. Image 6 is her small game sprite now, shown 8x: copy its PROPORTIONS - CHIBI: the head with the hair and the ears about TWO FIFTHS of her height, a short body and short legs - its build, its facing and HOW THE NINE TAILS SIT: ONE BUNCH behind her, fanning up and back to the image left, about that size. Image 7 is the layout guide: her sprite now as a flat silhouette at the new size - where she goes and how big; the dark grey line is the ground where her soles stand, the light grey line is where the TIPS OF HER FOX EARS go. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look (10 a female face with two clear eyes and fine details).
Create TWO pixel-art pictures of her, each a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque): A in 3/4 view facing right, S in exact side view facing right. In both she is about 660 px (about 60 squares) from the tips of her ears to her soles, the soles about 64 px above the bottom edge (the dark grey line of image 7); her head's, body's and tails' size as the silhouette of image 7; the whole figure and all the tails inside the picture with margins, nothing cut off; the soles on one ground line.
THE CHARACTER (images 1, 3, 5): HEAD: long VERY DARK NAVY-BLACK hair with blue highlights, bangs and side locks falling to her chest, ONE THICK BRAID down her back; a pair of FOX EARS on top, BLACK outside and PINK inside; GOLDEN eyes - TWO EYES of the SAME size at the SAME height (picture A); three thin dark red WHISKER MARKS on each cheek; soft pink lips. BODY: an OFF-SHOULDER RED top with a WHITE collar trim; a PURPLE sash with gold ornaments and a round gold clasp, a PURPLE TASSEL hanging at her hip; a short WHITE skirt with a red hem and gold patterns. ARMS: long detached RED SLEEVES with wide WHITE cuffs and gold patterns; dark red nails. LEGS: fair skin, a RED garter on one thigh, RED knee boots with WHITE tops and dark wraps below. THE NINE TAILS: soft LAVENDER-WHITE fox tails (white with a faint lavender tint, lavender-grey in the shade, the tips a little violet), gathered in ONE BUNCH that grows from her LOWER BACK and fans UP AND BACK to the image LEFT, the tips between her waist and the top of her head, as in image 6; each tail readable on its own (its own outline and light side) but the bunch NOT bigger than her body (about 35 x 42 squares); NO tail below her knees, NO tail on the ground, NO tail in front of her. Images 1, 2 and 4 show the tails far too big and trailing on the ground: DO NOT copy their size.
PROPORTIONS (image 6): CHIBI - the head with the hair and ears about two fifths of her height, a short body and short legs. NOT realistic proportions, NOT tall and slender.
PICTURE A - THE VIEW AND POSE (images 1 and 6): 3/4 view FACING RIGHT: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker; relaxed arms: the near hand hanging at her side, the far hand raised a little in front of her chest (as image 6); the legs close together and straight, both soles on one ground line; the tails behind her to the upper left.
PICTURE S - THE VIEW AND POSE (image 2): EXACT SIDE VIEW FACING RIGHT, only one eye seen; the same costume, colours, proportions and grid as A; the braid and the tails behind her (image left), the tails fanning up and back from her lower back, off the ground; one foot a little ahead of the other, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the pictures are read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the gold with clear light and dark faces, the dark hair with LIGHTER BLUE STRANDS so it never turns into one dark mass, the white tails and skirt with lavender-grey shades so they never turn into one flat white, the golden eyes bright and solid, the skin fair and warm; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects (no orb, no fox-fire, no hearts), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 两张都是 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，人物外面没有光晕**；整个人和整束尾巴都在画面里。
- **Q 版**：比例照附图 6，头约占身高五分之二，身子和腿短；不是真人比例。
- A **四分之三侧身朝右前方**：两只眼睛一样大、一样高；近侧手臂和腿在画面左边、颜色亮。S **正侧面朝右**。
- 衣服、颜色和附图 1、3、5 一样：藏青黑长发和辫子、黑外粉里的狐耳、金色眼睛、狐须纹、露肩红上衣和白领边、紫腰封和金扣、紫流苏、白短裙、红袖套和白袖口、红腿环、红靴白边。
- **九条尾巴收成身后一束**：从后腰向左上方扬开，尾尖在腰和头顶之间，**膝盖以下没有尾巴、不拖地、不挡在身前**，整束不大过身体。
- 狐耳尖到脚底约 660 px（约 60 格），脚底在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/ahri-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ahri_ppu_done.zip`，这样我这边才知道已经交付完。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/ahri/hd/`，**先量 Codex 实际的格子大小**，**按原始生成图自己的格子读回**（`design_fiora_hd.py` / `design_leblanc_hd.py` 的做法）；需要删行时每段均匀删（脸的行列不删）；12 倍检查脸、按格修眼睛；和妖姬、剑姬、现在的阿狸按游戏里的大小并排，给用户确认大小和 PPU。
- 定下后照 `tools/art/rig_leblanc_hd.py` 的做法按英雄联盟的骨骼摆每个动作（tag、帧数、每帧毫秒数都不变）；尾巴是一个部件，跟着骨盆走，只做无损的平移 / 镜像 / 直角转，不贴地；移动的腿按妖姬的做法出带骨架的 Codex 腿包（腿和待机的一样）；然后 ppu_restyle（`fx=True`）/ ppu_hd / hd.rs、league.dll 版本、头像点、选人卡、预览，开 PR。
