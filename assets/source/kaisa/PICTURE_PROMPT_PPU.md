# 卡莎：按 PPU 1.5 重画 Q 版设计图（给 Codex 的提示词）

> 卡莎现在游戏里的造型是 1 倍的：从竖起的发射器尖到脚底只有 42 格，颜色挤在一起、偏暗（附图 7）。这次和赵信、贾克斯一样，按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从发射器尖到脚底约 **63 格**，细节更清楚。这次只画**一张**全身设计图，动作帧不用画，我这边按英雄联盟的骨骼来摆。
> - **还是 Q 版**：头（连头发，不算发射器）约占身高的三分之一，腿短一些。**身材要苗条、匀称**，不要宽、不要胖，脸不要太大（之前一版被说「身宽体胖 脸大」）。比例照附图 7（现在的游戏精灵）和附图 1（英雄联盟模型的大头渲染），不要画成附图 6 那样写实的长腿。
> - **衣服、颜色照附图 6**（之前通过的原画 B）：
>   - 头：深紫色长发披在背后，两颊紫色纹路；紫色眼睛，**两只眼睛一样大、一样高**；小嘴。
>   - 身体：胸口和腹部是**浅紫蓝色（长春花色）的虚空活体甲**，有一道道肌理；肩、手臂、胯、腿是**深蓝紫色的甲片**，边上细细的**金色描边**；甲片缝里透出**亮洋红色的光**。
>   - **双肩的艾卡西亚暴雨发射器竖起来**，像一对翅膀立在头两侧，尖端比头顶高；深紫甲壳、金边，里面亮着洋红色的光。
>   - 手：带爪的护手，手心亮洋红色的光。腿：深紫装甲长靴，带爪的高跟。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。**近侧的手臂和腿在画面左边、颜色亮**，远侧在画面右边、稍暗；两只脚底在同一条地面线上。
> - **姿势**（附图 1，英雄联盟里发射器竖起的待机）：站直，两脚略分开；两臂稍离开身体垂着，爪子张开、手心发光；发射器竖在肩后，尖端高过头顶。
> - **画布用方形 1024×1024**：**发射器尖到脚底约 693 px，也就是约 63 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），发射器尖碰到附图 8 的浅灰线。整个人、两个发射器、头发都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。深紫甲片一定要有偏亮的边，不要糊成一团黑；浅紫蓝的活体甲和深紫甲片分得开；洋红光要亮、成块。附图 9–11 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（上一次赵信的交付边缘有一圈半透明光晕，格子也不是 11 px，读回很费事）。
> - 不画特效、地面、影子。
> - 交付：`outputs/kaisa-ppu/kaisa-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/kaisa-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/kaisa_ppu_done.zip`。

## 附图（在压缩包 `kaisa_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_kaisa_idle.png` | 英雄联盟里的卡莎待机（大头比例），发射器竖起，四分之三朝右 | **朝向、姿势、Q 版比例** |
| `refs/2_kaisa_side.png` | 同一帧的侧面（朝右） | 发射器在背后的位置和角度 |
| `refs/3_kaisa_head.png` | 头部特写，四分之三朝右 | 脸、头发、两颊纹路、发射器根部 |
| `refs/4_kaisa_front.png` | 同一帧，更正面 | 只看胸甲、腰胯、甲片的结构 |
| `refs/5_kaisa_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_kaisa_picture.png` | 之前通过的原画 B | **衣服、颜色、发射器的样子照它**（比例不要照它：头太小、腿太长） |
| `refs/7_kaisa_now.png` | 她现在的游戏精灵（8 倍，1 倍密度） | **Q 版比例、苗条的身材和朝向**；颜色太暗，不要照 |
| `refs/8_layout.png` | 布局示意（只看位置和大小） | 画布上的位置、脚底线（深灰）、**发射器尖要碰到的线（浅灰）** |
| `style/9_style_jax.png` | 本包的贾克斯（8 倍，PPU 1.5，同样用这个方法重画的） | **只看风格**：Q 版、四分之三侧身 |
| `style/10_style_katarina.png` | 本包的卡特琳娜（8 倍，PPU 1.5） | **只看风格**：女性的脸、两只眼睛、长发 |
| `style/11_style_xinzhao.png` | 本包的赵信（8 倍，PPU 1.5，刚用这个方法重画的） | **只看风格**：甲片、金边、亮边 |

## 提示词：`kaisa-A.png`

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game with a big CHIBI head: a slim female warrior in a living void suit with two weapon pods raised on her shoulders (1 her idle in 3/4 view facing right - the ANGLE, the POSE and the CHIBI PROPORTIONS for this picture; 2 the same from the side, facing right: where the pods stand on her back; 3 her head in 3/4 view facing right: the face, the hair, the cheek markings, the pods' roots; 4 the same more from the front: the chest plate, the waist and the armour plates only). Image 5 is the official illustration: the mood and the colours. Image 6 is our approved earlier picture of her: copy its COSTUME, COLOURS and the look of the PODS exactly - but NOT its proportions (its head is too small and its legs too long). Image 7 is her small game sprite now, shown 8x: copy its CHIBI PROPORTIONS, its SLIM build and its facing - not its colours, which are too dark. Image 8 is THIS picture's layout guide: where she goes; the dark grey line is the ground, the light grey line is where the TIPS OF THE RAISED PODS go. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view (9 a chibi fighter redrawn the same way, 10 a female face with two clear eyes and long hair, 11 armour plates with gold trim and lit edges).
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque). She is about 693 px (about 63 squares) from the tips of her raised pods to the soles of her feet, the soles about 64 px above the bottom edge (the dark grey line of image 8); the whole figure, both pods and the hair inside the picture with comfortable margins, nothing cut off; both soles on one ground line.
THE CHARACTER (image 6): a slim, athletic young woman, fierce and focused. HEAD: long DARK PURPLE hair falling down her back, purple markings on both cheeks, purple eyes - TWO EYES of the SAME size at the SAME height, a small mouth. BODY: a PALE LAVENDER-BLUE (periwinkle) living-armour plate over the chest and belly with ridged, muscle-like grooves; DARK NAVY-VIOLET armour plates on the shoulders, arms, hips and legs, each edged with a thin GOLD trim line; bright MAGENTA light glowing from the seams of the plates. Two big ICATHIAN RAIN PODS rise from her shoulders like a pair of wings standing beside her head, their tips higher than her head: dark violet shells with gold trim and glowing magenta cores. Clawed gauntlets with magenta light in the palms. Armoured, clawed, high-heeled boots.
CHIBI PROPORTIONS (images 1 and 7): the head with the hair (not the pods) about a THIRD of her height, a readable face that is NOT oversized; a SLIM, slender body - NOT wide, NOT broad-shouldered, NOT heavy; shorter legs. NOT the small head and long legs of image 6.
THE VIEW: 3/4 view FACING RIGHT like images 1, 3, 9 and 10: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker; both soles on one ground line.
THE POSE (image 1, her idle with the pods raised): standing tall, feet slightly apart; both arms hanging a little away from her body, the clawed hands open with glowing palms; the two pods raised behind her shoulders, tips above her head.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark violet plates with LIGHTER EDGES so they never turn into one dark mass, the pale lavender-blue chest plate clearly apart from them, the gold trim bright, the magenta lights bright and solid, the hair dark purple with lighter strands, the skin warm light tan; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底），**每个像素透明度只有 0 或 255，人物外面没有光晕**；1024×1024；两个发射器、头发都在画面里。
- **Q 版**：头（连头发）约占身高三分之一，身材苗条，脸不要太大；不是附图 6 那样的小头长腿。
- **四分之三侧身朝右前方**：脸和胸口朝右，两只眼睛一样大、一样高；近侧手臂和腿在画面左边、颜色亮。
- 衣服、颜色、发射器和附图 6 一样；深紫甲片有亮边，和浅紫蓝的胸甲分得开；洋红光亮。
- 姿势：发射器竖在肩后、尖端高过头顶；两臂稍离身体垂着，手心发光。
- 发射器尖到脚底约 693 px（约 63 格），脚底在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/kaisa-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/kaisa_ppu_done.zip`，这样我这边才知道已经交付完。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/kaisa/hd/`，**先量 Codex 实际的格子大小**（赵信那次是 12 px 不是 11），按它自己的格子读回，再每段均匀删一行 / 一列到 63 行（`design_rell_cut.even_cut`，脸的行列不删；不要用整段 dp_keep，会把发射器和腿压扁），眼睛按格修正；和贾克斯、卡特琳娜、赵信、现在的卡莎按游戏里的大小并排，给用户确认大小和 PPU（ppu-too-high-in-game：不超过 1.5）。
- 定下后照 `tools/art/rig_xinzhao_hd.py` 的做法按英雄联盟的骨骼摆每个动作：部件只做无损的原样 / 镜像 / 直角转（不重采样，否则「变形」），腿不转，跑步照英雄联盟的跑步逐帧（腿按骨骼角度用设计的颜色画、靴子用设计原样整块贴），特效沿用。然后 ppu_restyle / ppu_hd / hd.rs、league.dll 版本、`tfm2_ase.py face` 定头像点、`bp_card_audit.py` 定卡片，开 PR。
