# 拉克丝：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 拉克丝现在游戏里的造型是 1 倍的：从头顶到脚底只有 35 格，脸、头冠、铠甲和法杖的细节都挤在一起（附图 7）。这次和凯特琳、锐雯、韦鲁斯一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从头顶到脚底约 **53 格**。这次只画**一张**全身设计图；动作之后再做。
> - **比例照现在的游戏精灵（附图 7）**：Q 版大头，头（连头发）约占身高的三分之一，身材纤细；不要更高更瘦，也不要更矮。
> - **衣服、颜色照附图 6**（之前定下的拉克丝造型）：
>   - 头：**金色长发**（长度照附图 6），发梢有深一点的金棕色阴影；额前一顶**深蓝色头冠 / 发箍**，金色镶边；**蓝色大眼睛**，两只眼睛一样高、都看得见；表情自信、微笑。
>   - 上身：**白色和金色的轻铠**：白色胸甲、金色镶边和肩甲；腰间一条**深蓝色腰带**。
>   - 下身：白色短裙甲片，金色镶边；**深蓝色紧身护腿**；靴子深蓝色、**金色的靴尖和护膝**。
>   - **法杖**：一根**笔直的长法杖**，白金色的杆身，**金色螺旋**缠绕；两端是金色的饰件，大的一端（杖头）带月牙形的金饰和一颗**蓝色宝石**。法杖是刚性直杆：握手前后的杆身在同一条直线上，两端的饰件和杆身同轴。
> - **姿势照附图 1**（英雄联盟里的待机）：站着，近侧的手握着法杖**斜着拿在身前**，杖头朝左下、另一端朝右上（照附图 1），另一只手照附图 1；两腿站稳，两只脚底在同一条地面线上。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用方形 1024×1024**：**头顶到脚底约 578 px，也就是约 53 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），头顶碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照附图 1）。整个人和整根法杖都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金发要有明暗层次，不要一片死黄；白色铠甲要有浅灰蓝的阴影，不要一片死白；蓝眼睛、蓝宝石、深蓝头冠要清楚。附图 9–11 是本包同样密度（PPU 1.45–1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。
> - 不画特效（法杖不发光晕）、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/lux-ppu/lux-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/lux-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/lux_ppu_done.zip`。

## 附图（在压缩包 `lux_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_lux_idle.png` | 英雄联盟里的拉克丝待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_lux_side.png` | 同一帧，转得更侧 | 法杖的位置 |
| `refs/3_lux_head.png` | 头部特写 | 脸、头发、头冠 |
| `refs/4_lux_staff.png` | 同一帧，更正面 | **法杖的形状**、铠甲 |
| `refs/5_lux_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_lux_picture.png` | 之前定下的拉克丝造型 | **衣服、颜色、法杖照它** |
| `refs/7_lux_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，35 格高） | **比例、身材** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/9_style_caitlyn.png` | 本包的凯特琳（8 倍，PPU 1.45） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |
| `style/11_style_janna.png` | 本包的迦娜（8 倍，PPU 1.5） | **只看风格**：女法师、身材 |

## 提示词：`lux-A.png`

附图 1–11，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): a young light mage in white and gold armour with a long staff (1 her idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same turned more to the side: how she holds the staff; 3 her head: the face, the hair, the tiara; 4 the same frame seen more from the front: the staff's shape and the armour). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved pixel picture of her: copy its COSTUME, COLOURS and STAFF. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (a chibi: the head with the hair about a THIRD of her height, a slender build) - not its pose. Image 8 is THIS picture's layout guide: her sprite now as a flat silhouette at the new size - how big she is and where she stands (not the pose); the dark grey line is the ground where her soles stand, the light grey line is where THE TOP OF HER HEAD goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). She is about 578 px (about 53 squares) from the top of her head to her soles, the soles about 64 px above the bottom edge; the whole figure and the whole staff inside the picture with margins, nothing cut off; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (image 6): a bright, confident young mage. HEAD: long GOLDEN BLONDE hair (as long as in image 6), shaded with deeper gold-brown; a DARK BLUE tiara / circlet with gold trim on the brow; big BLUE eyes, the two eyes at the same height, both visible; a confident smile. BODY: light WHITE AND GOLD armour - a white breastplate with gold trim and gold shoulder pieces; a DARK BLUE belt at the waist. LEGS: short white armour skirt plates with gold trim, DARK BLUE fitted leggings, dark blue boots with GOLD toes and knee guards. THE STAFF: a long STRAIGHT staff, white-gold shaft wound with a GOLD SPIRAL, gold ornaments at both ends, the bigger one (the head) a gold crescent holding a BLUE GEM; it is RIGID: the shaft above and below her hand lies on ONE straight line, both end pieces on the same axis.
PROPORTIONS (image 7): a chibi, the head with the hair about a THIRD of her height, slender - NOT taller or thinner, NOT shorter.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE POSE (image 1): standing, the near hand holding the staff DIAGONALLY in front of her, its head down to the lower left and its other end up to the upper right, the other arm as in image 1; the legs standing firm, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the blonde hair with light and deep gold shading (never one flat yellow mass), the white armour with pale grey-blue shading (never flat white), the blue eyes, the blue gem and the dark blue tiara clear; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no light from the staff, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势照附图 1**：站着，法杖斜拿在身前、杖头朝左下；头顶到脚底约 578 px（约 53 格），两只脚底在同一条线上，脚底以下什么都没有。
- 衣服、颜色和附图 6 一样：金色长发、深蓝头冠、蓝眼睛、白金轻铠、深蓝腰带和护腿、金色靴尖，笔直的白金法杖带金色螺旋、月牙杖头和蓝宝石。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/lux-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/lux_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/lux/hd/`，照 `tools/art/design_varus_hd.py` 按整张图拟合格距和相位读回；和韦鲁斯、凯特琳、锐雯、现在的拉克丝按游戏里的大小并排，给用户确认大小和 PPU（不超过 1.5）。
- 定下后动作由 Claude 用设计图自己的格子摆（`rig_varus_hd.py`、`rig_jinx_hd.py` 的做法：部件逐格切开、只整格平移和转 90°，手臂不动露不出没画的身体，跑步的腿用设计图自己的行沿骨头排）；法杖必须笔直；光弹、Q、R 的出发高度照新法杖头重算；烘焙特效照 `lux_bake.json`（如有）。查塞拉斯、佛耶戈 / 妮蔻灵魂表、待机和选人卡轮播等适配。
