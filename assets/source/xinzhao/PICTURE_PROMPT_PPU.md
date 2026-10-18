# 赵信：按 PPU 1.5 重画 Q 版设计图（给 Codex 的提示词）

> 赵信现在游戏里的造型是 1 倍的：从发髻顶到脚底只有 42 格，颜色挤在一起，看着暗、糊（附图 7）。这次和贾克斯一样，按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从发髻顶到脚底约 **63 格**，细节更清楚。这次只画**一张**全身设计图，动作帧不用画，我这边按英雄联盟的骨骼来摆。
> - **还是 Q 版**：头（连发髻）大，约占身高的三分之一；身体匀称结实，腿短一些。比例照附图 7（现在的游戏精灵）和附图 1（英雄联盟模型的大头渲染），**不要画成附图 6 那样头小、腿长**。
> - **衣服、颜色和长枪照附图 6**（之前通过的原画 A）：
>   - 头：黑发往后梳，鬓角和额前银白挑染；头顶高高束起的发髻，**金色发冠**，后面两条**深紫色长发带**。剑眉、眼神凌厉，**两只眼睛一样大、一样高**。
>   - 上身：深色高领；**银白色的鳞甲 / 板甲胸甲**；外面**皇家紫（蓝紫）的长战袍**，衣边一圈**金色滚边**，前襟紫布垂在两腿之间；**后肩（画面左边）金色大护肩**；**前肩（画面右边）银白大护肩，嵌亮蓝色装饰**；棕色皮护臂，深色露指手套；棕色皮腰带，金扣；胯两侧银白甲片。
>   - 下身：**浅紫灰（薰衣草色）宽松裤子**，深灰钢色护胫和靴子，带金边。
>   - 长枪：深棕木杆，隔一段一道**金箍**；枪头是**紫色长刃**，旁边一个**银白月牙倒钩**和一条紫色飘带；枪尾一小截深铁尖锥。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。**近侧的手臂和腿在画面左边、颜色亮**，远侧在画面右边、稍暗；两只脚底在同一条地面线上。
> - **姿势**（附图 1，英雄联盟待机，附图 6 同样的拿法）：两脚分开、膝盖微弯；画面左边那只手在肩膀高度握枪，长枪斜架在肩后：**紫刃枪头在身后左下方，枪尾尖锥在前肩上方右上方**；另一只手张开在身前，像爪子一样蓄势。
> - **画布用横版 1536×1024**：**发髻顶到脚底约 693 px，也就是约 63 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线）。整杆长枪、发带、手都在画面里，两头都不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。紫色用几档蓝紫，**一定要有偏亮的边**；银甲用几档冷灰加白色高光，不要和紫色糊成一片。附图 9–11 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - 不画特效、地面、影子。
> - 交付：`outputs/xinzhao-ppu/xinzhao-A.png`（1536×1024 横版，**真透明背景**）；原始生成图原样放进 `outputs/xinzhao-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/xinzhao_ppu_done.zip`。

## 附图（在压缩包 `xinzhao_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

注意：英雄联盟的渲染图（附图 1–4、8）**没有发髻**（模型里的发髻渲染出来是一团坏掉的黑块，已经去掉了），发髻和金发冠照附图 5、6 画。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_xinzhao_idle.png` | 英雄联盟里的赵信待机（大头比例），四分之三朝右 | **朝向、姿势、拿枪的方式、Q 版比例** |
| `refs/2_xinzhao_side.png` | 同一帧的侧面（朝右） | 身体的转向、长枪的角度和长度 |
| `refs/3_xinzhao_head.png` | 头部特写，四分之三朝右 | 脸、发型、发髻的位置、两块护肩 |
| `refs/4_xinzhao_front.png` | 同一帧，更正面 | 只看胸甲、战袍、腰带的结构 |
| `refs/5_xinzhao_splash.png` | 官方加载画面 | **发髻和金发冠照它**；看气质 |
| `refs/6_xinzhao_picture.png` | 之前通过的原画 A | **衣服、颜色、长枪照它**（比例不要照它：头太小、腿太长） |
| `refs/7_xinzhao_now.png` | 他现在的游戏精灵（8 倍，1 倍密度） | **Q 版比例**和朝向；颜色太暗、太糊，不要照 |
| `refs/8_layout.png` | 布局示意（只看位置和大小） | 画布上的位置、脚底线（深灰）、**发髻顶要碰到的线（浅灰）** |
| `style/9_style_jax.png` | 本包的贾克斯（8 倍，PPU 1.5，同样用这个方法重画的） | **只看风格**：Q 版、四分之三侧身 |
| `style/10_style_katarina.png` | 本包的卡特琳娜（8 倍，PPU 1.5） | **只看风格**：脸、两只眼睛、头发 |
| `style/11_style_pantheon.png` | 本包的潘森（8 倍，PPU 1.5） | **只看风格**：长矛在格子上怎么画 |

## 提示词：`xinzhao-A.png`

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game with a big CHIBI head: a spear warrior (1 his idle in 3/4 view facing right - the ANGLE, the POSE, how he holds the spear and the CHIBI PROPORTIONS for this picture; 2 the same from the side, facing right: the spear's angle and length; 3 his head in 3/4 view facing right: the face, the hair, both shoulder pieces; 4 the same more from the front: the breastplate, the coat and the belt only). Image 5 is the official illustration: copy the TOPKNOT and its GOLD CROWN CLASP from it, and the stern mood. Image 6 is our approved earlier pixel-art picture of him: copy its COSTUME, COLOURS and SPEAR exactly - but NOT its proportions (its head is too small and its legs too long). Image 7 is his small game sprite now, shown 8x: copy its CHIBI PROPORTIONS and facing - not its colours, which are too dark and muddy. Image 8 is THIS picture's layout guide: where he goes; the dark grey line is the ground, the light grey line is where the TOP OF HIS TOPKNOT goes. The 3D renders (images 1-4 and 8) leave the topknot out (in the model it renders as a broken dark lump): draw the topknot as images 5 and 6 show. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view (9 a chibi fighter redrawn the same way, 10 a face with two clear eyes, 11 a long spear on the grid).
Create ONE pixel-art picture of him, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha). He is about 693 px (about 63 squares) from the top of his topknot to the soles of his feet, the soles about 64 px above the bottom edge (the dark grey line of image 8); the whole spear (both ends), the ribbons and the hands inside the picture with comfortable margins, nothing cut off; both soles on one ground line.
THE CHARACTER (image 6, the topknot as image 5): a fit, athletic male spear warrior, noble and stern. HEAD: black hair combed back with SILVER-WHITE streaks at the temples and the front, a high TOPKNOT held by a GOLD crown clasp, two long DARK PURPLE RIBBONS trailing back from it; sharp dark brows, fierce eyes - TWO EYES of the SAME size at the SAME height; a small gold earring. BODY: a dark high collar; a SILVER-WHITE scale-and-plate breastplate; a long ROYAL PURPLE (blue-violet) war coat with GOLD trim on every edge, its front panel hanging between his legs; a big flaring GOLD shoulder guard on the back shoulder (image left) and a large SILVER-WHITE PAULDRON with BRIGHT BLUE insets on the front shoulder (image right); brown leather forearm guards, dark fingerless gloves; a brown leather belt with a gold buckle; silver-white tasset plates at the hips. LEGS: loose pale LAVENDER-GREY trousers, dark steel greaves and boots with gold trim. SPEAR: a dark brown wooden shaft with GOLD rings along it; its HEAD a long PURPLE blade with a SILVER CRESCENT HOOK beside it and a purple streamer; its BUTT a short dark iron spike.
CHIBI PROPORTIONS (images 1 and 7): the head with the topknot about a THIRD of his height, a big readable face; a fit, sturdy body; shorter legs. NOT the small head and long legs of image 6.
THE VIEW: 3/4 view FACING RIGHT like images 1, 3, 9 and 10: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker; both soles on one ground line.
THE POSE (image 1, his idle; image 6 holds the spear the same way): a wide stance, feet apart, knees slightly bent; the arm on the image-LEFT side holds the spear at shoulder height, the spear slanting across behind his shoulders: its PURPLE-BLADED HEAD with the crescent hook low behind him at the image left, its iron BUTT SPIKE high in front, past his front shoulder at the image right; the other hand open in front of his belly, clawed, ready; the ribbons hanging behind the topknot.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the purple coat in blue-violet shades with LIGHTER EDGES so it never turns into one dark mass, the silver armour in cool greys with white highlights and bright blue insets, the gold trim and shoulder guard in bright gold / gold / dark gold, the leather brown, the trousers pale lavender-grey, the boots dark steel, the skin warm light tan, the hair black with silver-white streaks; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1024 横版；整杆长枪（两头）、发带、手都在画面里。
- **Q 版**：头（连发髻）约占身高三分之一，腿短一些；不是附图 6 那样的小头长腿。
- **四分之三侧身朝右前方**：脸和胸口朝右，两只眼睛一样大、一样高；近侧手臂和腿在画面左边、颜色亮。
- 衣服、颜色、长枪和附图 6 一样；发髻和金发冠照附图 5；紫色战袍有亮边，银甲和紫色分得开。
- 姿势：长枪斜架在肩后，紫刃枪头在身后左下，枪尾尖锥在前肩右上；另一只手张开在身前。
- 发髻顶到脚底约 693 px（约 63 格），脚底在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/xinzhao-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/xinzhao_ppu_done.zip`，这样我这边才知道已经交付完。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/xinzhao/hd/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回，和贾克斯、卡特琳娜、现在的赵信按游戏里的大小并排，给用户确认大小和 PPU（ppu-too-high-in-game：不超过 1.5）。
- 定下后照贾克斯的做法（`tools/art/rig_jax_hd.py` on `ppu_rig.Driver`）按英雄联盟的骨骼摆每个动作：长枪是刚体，每帧都用设计里同一根枪，只能整根平移或直角转；走路用设计自己的两条腿整块移动。特效沿用。然后 ppu_restyle / ppu_hd / hd.rs、league.dll 版本、`tfm2_ase.py face` 定头像点，开 PR。
