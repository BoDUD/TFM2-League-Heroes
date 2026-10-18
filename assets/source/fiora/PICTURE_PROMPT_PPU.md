# 剑姬：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 剑姬现在游戏里的造型是 1 倍的：从头发顶到脚底只有 40 格，脸、手和护甲的细节都挤在一起（附图 7）。这次和卡莎、青钢影一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从头发顶到脚底约 **60 格**，细节更清楚。这次只画**一张**全身设计图，动作帧不用画，我这边按英雄联盟的骨骼来摆。
> - **比例照现在的游戏精灵（附图 7）**：头（连头发）约占身高的三分之一，身子和腿照附图 7，不要更高更瘦，也不要更矮更胖。**细剑的长度也照附图 7**（剑尖伸到附图 8 剪影的右端）。
> - **衣服、颜色照附图 6**（之前定下的设计图 B）：
>   - 头：靛紫色的齐肩短发，**一侧一缕深红色的刘海**垂在脸边；青色眼睛，**两只眼睛一样大、一样高**；淡粉嘴唇。
>   - 身体：金色的大肩甲，肩甲上嵌天蓝色宝石；白色的紧身上衣，金色饰边；腰上金甲；背后一条酒红色的披风，披风边是白色和金色。
>   - 腿：青绿色（深青）紧身裤，侧面走着金色的线；金色护膝；深青色靴子、金色鞋尖和鞋跟。
>   - 手和剑：金色的护臂，深色手套；**细剑**：金色的护手（剑柄护盘）嵌一颗天蓝宝石，**剑身是一条水平的直线**，银白色，**2 格粗**，上沿一条更亮的线，剑身**不要黑描边**，从护手笔直伸到剑尖。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。**近侧的手臂和腿在画面左边、颜色亮**，远侧在画面右边、稍暗。
> - **姿势照附图 1**（英雄联盟里的待机）：站直，持剑的手臂向右前方伸出，剑平举指向右边，另一只手垂在身侧、贴着胯；**两腿照附图 1 稍微分开站直**（近侧脚略靠前），**不要照附图 6、7、8 那样大弓步**，两只脚底在同一条地面线上。
> - **画布用横的 1536×1024**（剑很长）：**头发顶到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），头发顶碰到附图 8 的浅灰线；头的大小、剑尖的位置照附图 8 的剪影（剪影是现在的大弓步，腿不要照它）。整个人和整把剑都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（剑身除外）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金甲要有亮面和暗面；白色上衣要有浅灰的阴影；深青裤子要有偏亮的边，不要糊成一团黑；天蓝宝石和眼睛要亮、成块。附图 9–11 是本包同样密度（PPU 1.5 左右）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（之前的设计图 B 就有半透明边，这次不要）。
> - 不画特效、地面、影子。
> - 交付：`outputs/fiora-ppu/fiora-A.png`（1536×1024，**真透明背景**）；原始生成图原样放进 `outputs/fiora-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/fiora_ppu_done.zip`。

## 附图（在压缩包 `fiora_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_fiora_idle.png` | 英雄联盟里的剑姬待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_fiora_side.png` | 同一帧的侧面（朝右） | 披风、腿的前后位置 |
| `refs/3_fiora_head.png` | 头部特写，四分之三朝右 | 脸、发型、深红刘海 |
| `refs/4_fiora_sword_arm.png` | 同一帧，持剑手臂和剑的特写 | **护臂、手套、护手和宝石** |
| `refs/5_fiora_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_fiora_picture.png` | 之前定下的剑姬设计图 B | **衣服、颜色照它**；它的边是半透明的，不要照 |
| `refs/7_fiora_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，40 格高） | **比例、身材、朝向、剑的长度** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影（只看位置和大小） | 画布上的位置、脚底线（深灰）、**头发顶要碰到的线（浅灰）**、剑尖的位置；腿不照它 |
| `style/9_style_xinzhao.png` | 本包的赵信（8 倍，PPU 1.5，同样用这个方法重画的） | **只看风格**：甲片、金边、亮边 |
| `style/10_style_kaisa.png` | 本包的卡莎（8 倍，PPU 1.45） | **只看风格**：女性的脸、两只眼睛、细节 |
| `style/11_style_camille.png` | 本包的青钢影（8 倍，PPU 1.5，刚用这个方法重画的） | **只看风格** |

## 提示词：`fiora-A.png`

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): an elegant female fencer with a rapier (1 her idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same from the side, facing right: the cape and where the legs stand; 3 her head in 3/4 view facing right: the face, the bob haircut, the crimson lock; 4 the same frame close on her sword arm: the gold bracer, the glove, the gold hand guard with its blue gem). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved design picture of her: copy its COSTUME and COLOURS (not its soft semi-transparent edges). Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (the head with the hair about a THIRD of her height), its build, its facing and the LENGTH of the rapier. Image 8 is THIS picture's layout guide: her sprite now as a flat silhouette at the new size - where she goes and how big; the dark grey line is the ground where her soles stand, the light grey line is where the TOP OF HER HAIR goes, the silhouette's right end is where the rapier's tip goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view (9 armour plates with gold trim and lit edges, 10 a female face with two clear eyes and fine details, 11 a female fighter redrawn the same way).
Create ONE pixel-art picture of her, a 1536x1024 PNG (landscape, for the long rapier) with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque). She is about 660 px (about 60 squares) from the top of her hair to her soles, the soles about 64 px above the bottom edge (the dark grey line of image 8); her head's size and the rapier tip's place as the silhouette of image 8 (its legs are the old wide stance: do not copy them); the whole figure and the whole rapier inside the picture with margins, nothing cut off; both soles on one ground line.
THE CHARACTER (image 6): a proud, poised young duelist. HEAD: a chin-length INDIGO-PURPLE bob with one DEEP CRIMSON lock falling beside her face, cyan eyes - TWO EYES of the SAME size at the SAME height, pale pink lips. BODY: big GOLD shoulder plates set with SKY-BLUE gems; a WHITE fitted top with gold trims; a gold waist guard; a WINE-RED cape behind her with white and gold edges. LEGS: DARK TEAL tights with thin gold side lines, gold knee guards, dark teal boots with gold toes and heels. ARMS AND RAPIER: gold bracers and dark gloves; the rapier's GOLD hand guard with a sky-blue gem, and its BLADE ONE STRAIGHT HORIZONTAL LINE, silver-white, 2 squares thick with a brighter top edge, NO black outline around the blade, from the guard straight to the tip.
PROPORTIONS (image 7): the head with the hair about a THIRD of her height, the body and legs as image 7 - NOT taller or thinner, NOT shorter or stockier; the rapier as long as in image 7.
THE VIEW: 3/4 view FACING RIGHT like images 1, 3, 10 and 11: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker.
THE POSE (image 1, NOT the wide lunge stance of images 6-8): standing tall, the sword arm reaching to the front-right, the rapier held level and pointing right, the other hand down at her side by the hip; the legs straight and only slightly apart as in image 1, the near foot a little forward, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure (not around the blade); inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the gold armour with clear light and dark faces, the white top with light grey shading, the dark teal tights with LIGHTER EDGES so they never turn into one dark mass, the blue gems and the eyes bright and solid, the hair indigo with lighter strands, the skin warm light; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景，**每个像素透明度只有 0 或 255，人物外面没有光晕**；1536×1024；整个人和整把剑都在画面里。
- **比例照附图 7**：头约占身高三分之一；剑和附图 7 一样长。
- **四分之三侧身朝右前方**：脸和胸口朝右，两只眼睛一样大、一样高；近侧手臂和腿在画面左边、颜色亮。
- 衣服、颜色和附图 6 一样：靛紫头发和深红刘海、金肩甲和天蓝宝石、白上衣、酒红披风、深青裤子和金线。
- **剑身是一条水平直线，2 格粗，没有黑描边**；护手金色、有宝石。
- 姿势照附图 1：站直、两腿稍分开，不是大弓步；头发顶到脚底约 660 px（约 60 格），两只脚底在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/fiora-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/fiora_ppu_done.zip`，这样我这边才知道已经交付完。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/fiora/hd/`，**先量 Codex 实际的格子大小**（赵信那次 12 px、卡莎 19.3 px，都不是 11），**按原始生成图自己的格子读回**（`design_camille_hd.py` 的做法）；需要删行时每段均匀删（`design_rell_cut.even_cut`，脸的行列不删）；眼睛按格修正；剑身读回后按 2 格粗拉直；和卡莎、青钢影、现在的剑姬按游戏里的大小并排，给用户确认大小和 PPU（ppu-too-high-in-game：不超过 1.5）。
- 定下后照 `tools/art/rig_camille_hd.py` 的做法按英雄联盟的骨骼摆每个动作：手臂和剑只做无损的原样 / 镜像 / 直角转，上身不偏离髋部太多；移动先试设计自己的腿，不行就让 Codex 只重画腿（`pack_camille_legs.py` 的做法）。然后 ppu_restyle / ppu_hd / hd.rs、league.dll 版本、头像点、选人卡，开 PR。
