# 青钢影：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 青钢影现在游戏里的造型是 1 倍的：从头发顶到刀刃尖只有 46 格，手臂和手几乎是几根黑线，脸也挤（附图 7）。这次和赵信、卡莎一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从头发顶到刀刃尖约 **69 格**，细节更清楚。这次只画**一张**全身设计图，动作帧不用画，我这边按英雄联盟的骨骼来摆。
> - **比例照现在的游戏精灵（附图 7）**：苗条、修长，头（连头发）约占身高的四分之一，两条腿是从膝盖往下伸出的长刀刃；不要大头 Q 版，也不要更高更瘦。
> - **衣服、颜色照附图 6**（之前 Codex 画的干净的 65 格青钢影）：
>   - 头：银白偏薄荷色的尖角短发，后脑一个发髻；青蓝色眼睛，**两只眼睛一样大、一样高**；淡色嘴唇。
>   - 身体：深蓝色高立领，领口一颗深蓝宝石；天蓝色胸甲；深蓝紧身衣上走着金色的线条和饰边；宽胯，胯上的金色护甲，**近侧胯边一个发青光的海克斯核心**。
>   - 手：黑色手套、金色腕带。**手要画清楚**：近侧手叉在腰上（看得出手肘和握拳的手），远侧手举在肩膀前，拇指和食指捏成一个圈、其余三指竖起（附图 4），前臂、金腕带、手套的手指都要分得开（之前的版本手只剩几根黑线，用户：「卡密尔的手部能改精致一点吗？现在太怪了」）。
>   - 腿：金色护膝，膝盖以下是银白发蓝的长刀刃（两条腿就是两把刀，刀尖着地），亮面和暗面分清楚。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。**近侧的手臂和腿在画面左边、颜色亮**，远侧在画面右边、稍暗；两个刀尖在同一条地面线上。
> - **姿势**（附图 1，英雄联盟里的待机，也是现在游戏精灵的姿势）：站直，近侧手叉腰，远侧手举起、拇指和食指捏成圈，两条刀腿略分开站。
> - **画布用方形 1024×1024**：**头发顶到刀尖约 759 px，也就是约 69 格**，刀尖在离画布底边约 64 px 的地方（附图 8 的深灰线），头发顶碰到附图 8 的浅灰线。整个人都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。深蓝衣服要有偏亮的边，不要糊成一团黑；金线要亮；青色核心和眼睛要亮、成块；刀刃的亮面要清楚。附图 9–11 是本包同样密度（PPU 1.5 左右）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**。
> - 不画特效、地面、影子。
> - 交付：`outputs/camille-ppu/camille-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/camille-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/camille_ppu_done.zip`。

## 附图（在压缩包 `camille_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_camille_idle.png` | 英雄联盟里的青钢影待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_camille_side.png` | 同一帧的侧面（朝右） | 发髻、刀腿的侧面形状 |
| `refs/3_camille_head.png` | 头部特写，四分之三朝右 | 脸、发型、高立领 |
| `refs/4_camille_hands.png` | 同一帧，手臂和手的特写 | **叉腰的手和拇指食指捏圈的手** |
| `refs/5_camille_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_camille_picture.png` | 之前 Codex 画的 65 格青钢影（8 倍） | **衣服、颜色照它** |
| `refs/7_camille_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，46 格） | **比例、身材、朝向**；手太粗糙，不要照 |
| `refs/8_layout.png` | 布局示意（只看位置和大小） | 画布上的位置、刀尖线（深灰）、**头发顶要碰到的线（浅灰）** |
| `style/9_style_jax.png` | 本包的贾克斯（8 倍，PPU 1.5，同样用这个方法重画的） | **只看风格** |
| `style/10_style_xinzhao.png` | 本包的赵信（8 倍，PPU 1.5） | **只看风格**：甲片、金边、亮边 |
| `style/11_style_kaisa.png` | 本包的卡莎（8 倍，PPU 1.45，刚用这个方法重画的） | **只看风格**：女性的脸、两只眼睛、细节 |

## 提示词：`camille-A.png`

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): an elegant, slim female duelist whose legs end in long steel blades (1 her idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same from the side, facing right: her hair bun and the side shape of the blade legs; 3 her head in 3/4 view facing right: the face, the short spiky hair, the high collar; 4 the same frame close on her arms: the near hand on her hip and the far hand raised in front of her shoulder, thumb and forefinger touching in a ring, the other three fingers up). Image 5 is the official illustration: the mood and the colours. Image 6 is an earlier clean pixel picture of her (8x): copy its COSTUME and COLOURS. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (the head about a quarter of her height, slim, long blade legs), its build and its facing - not its rough hands. Image 8 is THIS picture's layout guide: where she goes; the dark grey line is the ground where the blade tips stand, the light grey line is where the TOP OF HER HAIR goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view (9 a fighter redrawn the same way, 10 armour plates with gold trim and lit edges, 11 a female face with two clear eyes and fine details).
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque). She is about 759 px (about 69 squares) from the top of her hair to the tips of her blade legs, the blade tips about 64 px above the bottom edge (the dark grey line of image 8); the whole figure inside the picture with comfortable margins, nothing cut off; both blade tips on one ground line.
THE CHARACTER (image 6): a slim, poised young woman, cool and precise. HEAD: short spiky SILVER-MINT hair with a small bun at the back, cyan-blue eyes - TWO EYES of the SAME size at the SAME height, pale lips. BODY: a DARK NAVY high collar with a deep blue gem at the throat; a SKY-BLUE breastplate; a dark navy bodysuit with thin GOLD lines and trims; wide hips with gold armour and a glowing CYAN hextech core on the near hip. HANDS: black gloves with gold cuffs, drawn clearly - the near hand on her hip (the elbow out, a closed glove at the waist), the far hand raised in front of her shoulder, thumb and forefinger touching in a ring and the other three fingers up; forearm, gold cuff and fingers readable, never a few black lines. LEGS: gold knee caps, and below the knees long SILVER-WHITE steel BLADES with a blue tint, their bright and dark faces clear, the blade tips touching the ground.
PROPORTIONS (image 7): the head with the hair about a QUARTER of her height, slim and long-limbed - NOT a big-headed chibi, NOT taller or thinner than image 7.
THE VIEW: 3/4 view FACING RIGHT like images 1, 3, 9 and 11: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker; both blade tips on one ground line.
THE POSE (image 1): standing tall, the near hand on her hip, the far hand raised with thumb and forefinger touching in a ring, the blade legs slightly apart.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark navy suit with LIGHTER EDGES so it never turns into one dark mass, the gold lines bright, the cyan core and the eyes bright and solid, the steel blades with clear highlights, the hair silver-mint with lighter strands, the skin warm light; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景，**每个像素透明度只有 0 或 255，人物外面没有光晕**；1024×1024；整个人都在画面里。
- **比例照附图 7**：头约占身高四分之一，苗条，长刀腿；不是大头 Q 版。
- **四分之三侧身朝右前方**：脸和胸口朝右，两只眼睛一样大、一样高；近侧手臂和腿在画面左边、颜色亮。
- 衣服、颜色和附图 6 一样；深蓝衣服有亮边；金线亮；青色核心亮；刀刃亮面清楚。
- **手画清楚**：近侧手叉腰，远侧手举起、拇指食指捏成圈，前臂、金腕带、手指分得开。
- 头发顶到刀尖约 759 px（约 69 格），刀尖在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/camille-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/camille_ppu_done.zip`，这样我这边才知道已经交付完。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/camille/hd/`，**先量 Codex 实际的格子大小**（赵信那次 12 px、卡莎 19.3 px，都不是 11），**按原始生成图自己的格子读回**（卡莎那次 Codex 自己导出的小图是按格子中心取样的，脸碎了，不用）；需要删行时每段均匀删（`design_rell_cut.even_cut`，脸的行列不删）；眼睛按格修正；和贾克斯、赵信、卡莎、现在的青钢影按游戏里的大小并排，给用户确认大小和 PPU（ppu-too-high-in-game：不超过 1.5）。
- 定下后照 `tools/art/rig_kaisa_hd.py` 的做法按英雄联盟的骨骼摆每个动作：手臂只做无损的原样 / 镜像 / 直角转，上身不偏离髋部太多；刀腿不转；移动先试设计自己的腿，不行就照卡莎让 Codex 只重画腿（`pack_kaisa_walk.py` 的做法）。然后 ppu_restyle / ppu_hd / hd.rs、league.dll 版本、头像点、选人卡，开 PR。
