# 安妮：按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 安妮现在游戏里的造型是 1 倍的：从猫耳尖到脚底只有 34 格，脸、衣服、提伯斯的细节都挤在一起（附图 7）。这次和阿狸、拉克丝、金克丝一样按 **PPU 2.2** 重画：**每个游戏像素画成 2.2 格**，从猫耳尖到脚底约 **75 格**。这次只画**全身设计图**，同一个人画**两张，姿势不同**（A、B），用户挑一张；动作之后再做。
> - **比例照现在的游戏精灵（附图 7）**：小女孩，Q 版大头，头（连头发、不算猫耳）约占身高的五分之二；不要更高更瘦，也不要更矮更胖。
> - **衣服照英雄联盟的模型（附图 1–4）**，这次格子多了，把 1 倍画不下的细节画出来；颜色和附图 6（之前定下的安妮）一致：
>   - 头：**洋红色短发**，齐刘海，两侧垂到下巴下面，后面短；头上一个**粉色的猫耳发箍**（耳朵里面浅粉）；**绿色的眼睛**，两只眼睛一样高、都看得见；倔强、有点坏的表情（附图 3、5）。
>   - 上身：**紫色连衣裙**，泡泡短袖；外面一件**蓝色菱格纹的背心**；白色小翻领；手腕上一个**暗红色的手镯**；背后一个**粉色的小兔子背包**，肩上看得见背包带（附图 4）。
>   - 下身：紫色的蓬蓬短裙，裙摆有深紫的横条；**紫色和深紫横条纹的长袜**；黑色的圆头小皮鞋。
>   - **提伯斯**（小熊玩偶）：**棕色的泰迪熊**，身上有补丁和缝线，一只纽扣眼睛；**要大、要看得见**，大约是她上身那么大；它是安妮最重要的特征。
> - **两张的姿势**（朝向都是四分之三侧身，**脸和胸口朝右前方**，附图 1、3；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗；两只脚底在同一条地面线上）：
>   - **A：照英雄联盟的待机（附图 1）**：近侧（画面左边）的手垂在身侧，**拎着提伯斯的一只胳膊**，提伯斯挂在她腿边（不碰地面线）；远侧的手抬到胸前，手心朝前张开。
>   - **B：照她现在的精灵（附图 6、7）**：远侧的手把**提伯斯抱在胸前**（提伯斯在画面右边、她身前）；近侧的手垂在身侧。
> - **画布用方形 1024×1024**：**猫耳尖到脚底约 825 px，也就是约 75 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），猫耳尖碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照上面）。整个人和提伯斯都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。洋红头发要有明暗层次，不要一片平色；菱格纹、条纹袜、提伯斯的补丁和缝线要清楚；绿色眼睛要清楚。附图 9–11 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。
> - 不画特效（不画火、不画火球）、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/annie-ppu/annie-A.png`、`outputs/annie-ppu/annie-B.png`（都是 1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/annie-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/annie_ppu_done.zip`。

## 附图（在压缩包 `annie_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_annie_idle.png` | 英雄联盟里的安妮待机，四分之三朝右（头按游戏精灵的比例放大了一点） | **朝向**、**A 的姿势**、衣服 |
| `refs/2_annie_side.png` | 同一帧，转得更侧 | 衣服、背包、提伯斯 |
| `refs/3_annie_head.png` | 头部特写 | 脸、头发、猫耳发箍 |
| `refs/4_annie_back.png` | 同一帧，从身后看 | 兔子背包、后脑的头发 |
| `refs/5_annie_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_annie_picture.png` | 之前定下的安妮造型 | **颜色**、**B 的姿势** |
| `refs/7_annie_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，34 格高） | **比例、身材** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**猫耳尖要碰到的线（浅灰）** |
| `style/9_style_lux.png` | 本包的拉克丝（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_ahri.png` | 本包的阿狸（8 倍，PPU 2.2） | **只看风格** |
| `style/11_style_jinx.png` | 本包的金克丝（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`annie-A.png` 和 `annie-B.png`

附图 1–11，顺序同上表。两张用同一段提示词，只换最后的 THE POSE 一段。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged a little toward a game sprite's proportions): a little girl fire mage carrying her teddy bear Tibbers (1 her idle in 3/4 view facing right - the ANGLE, and the POSE of take A; 2 the same turned more to the side: her clothes, the backpack, the bear; 3 her head: the face, the hair, the cat-ear headband; 4 the same frame seen from behind: the bunny backpack, the back of her hair). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved small pixel picture of her: her COLOURS, and the POSE of take B. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (a little girl, a chibi: the head with the hair, not counting the cat ears, about TWO FIFTHS of her height) - not its pose. Image 8 is THIS picture's layout guide: her sprite now as a flat silhouette at the new size - how big she is and where she stands (not the pose); the dark grey line is the ground where her soles stand, the light grey line is where THE TIPS OF HER CAT EARS go. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the same square density: copy their pixel-art look, their detail and their 3/4 front-right view.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). She is about 825 px (about 75 squares) from the tips of her cat ears to her soles, the soles about 64 px above the bottom edge; the whole figure and the bear inside the picture with margins, nothing cut off; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (images 1-4, colours as image 6): a stubborn little girl. HEAD: short MAGENTA hair with straight bangs, the side locks down past her chin, short at the back, shaded in its own deeper magentas (never one flat colour); a PINK CAT-EAR HEADBAND on top (pale pink inside the ears); GREEN eyes, the two eyes at the same height, both visible; a stubborn, slightly mischievous look. BODY: a PURPLE dress with short puffed sleeves; over it a BLUE ARGYLE-PATTERNED vest; a small white collar; a dark red bracelet on her wrist; a small PINK BUNNY BACKPACK on her back, its straps on her shoulders. LEGS: a short full purple skirt with dark purple bands at the hem; long PURPLE AND DARK-PURPLE STRIPED stockings; black round-toed shoes.
TIBBERS (her most important feature - BIG and clearly VISIBLE): a BROWN TEDDY BEAR with patches and stitches and one button eye, about as big as her upper body.
PROPORTIONS (image 7): a little girl, a chibi, the head with the hair about two fifths of her height - NOT taller or thinner, NOT shorter or rounder.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the magenta hair with light and shade, the argyle pattern, the striped stockings, the bear's patches and stitches and the green eyes clear; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no fire, no fireball, no background, no ground, no shadow, no text, no frame, no other characters.
THE POSE (take A, file annie-A.png, image 1): standing; the near hand (image left) hangs at her side HOLDING TIBBERS BY ONE ARM, the bear dangling beside her legs (not touching the ground line); the far hand raised in front of her chest, palm open forward; both soles on one ground line.
```

`annie-B.png`：把上面最后一段换成：

```text
THE POSE (take B, file annie-B.png, image 6): standing; the far arm HUGS TIBBERS IN FRONT OF HER CHEST (the bear on the image right, in front of her body, his face visible); the near arm (image left) hangs at her side; both soles on one ground line.
```

## 交回前请检查

- 两张都是 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- 猫耳尖到脚底约 825 px（约 75 格），两只脚底在同一条线上，脚底以下什么都没有。
- **A**：近侧的手拎着提伯斯的胳膊，提伯斯挂在腿边不碰地面线，远侧的手在胸前张开；**B**：远侧的手把提伯斯抱在胸前。
- 衣服、颜色：洋红短发、粉色猫耳发箍、绿眼睛、紫色泡泡袖连衣裙、蓝色菱格纹背心、白翻领、暗红手镯、粉色兔子背包、紫色条纹长袜、黑皮鞋；提伯斯是棕色带补丁的泰迪熊，够大、看得清。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/annie-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/annie_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**（拉克丝、阿狸的教训：Codex 的导出按大格子采样，脸都没了；阿狸的原图格子比要求的细）：原画和 raw/ 放进 `assets/source/annie/hd/`，照 `tools/art/design_ahri_hd.py` 按原图自己的格子读回；和阿狸、拉克丝、金克丝、现在的安妮按游戏里的大小并排，给用户挑 A / B、确认大小和 PPU。
- 动作开工前先定**手臂要不要动**（拉克丝的教训）；安妮的普攻、Q、W、R 都要抬手放火，提伯斯跟着手走（R 时提伯斯被扔出去，手里空了）。
- 查塞拉斯、佛耶戈 / 妮蔻灵魂表、待机和选人卡轮播、普攻 / Q 火球的出手高度等适配。
