# 图奇：按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 图奇现在游戏里的造型是 1 倍的：从背包顶到脚底只有 32 格，脸、背包、弩、衣服的细节全挤在一起，看着很花（附图 7）。这次和凯特琳、锐雯、拉克丝、阿狸一样用 PPU 重画：**每个游戏像素画成 2.2 格**，从背包顶到脚底约 **70 格**。这次只画**一张**全身设计图；动作之后再做。
> - **比例照现在的游戏精灵（附图 7）**：Q 版大头，头（连大耳朵）约占身高的五分之二，身子矮壮、微微弓背；不要更高更瘦。
> - **造型、颜色照附图 6**（之前定下的图奇造型 B）：
>   - 头：**灰色的老鼠头**，长嘴，**红鼻头**，咧嘴露出一排尖牙；一对**很大的粉色耳朵**（里面粉色、外面灰色）；近侧眼睛戴一个**黄铜单片护目镜**（金色圆框、白色镜片、黑色瞳孔），护目镜的金色带子绕过额头；脖子上一条**橙红色的三角围巾**。
>   - 身体：**深绿色**的皮肤和手臂；**棕色皮革**的护腕、腰带和肩带，带金色铆钉；身后一个**绿色的大背包**，黄铜边框，顶上一排**青绿色的圆珠**。
>   - 下身：**蓝色破烂的长衣摆**（下摆一条条撕开，金色镶边），前面垂下一条蓝紫色的布；**紫灰色的腿**，棕色的绑腿，脚上白色的爪子。
>   - **尾巴**：细长的老鼠尾巴，**紫灰和米白的条纹**，从身后往左后方弯起来（照附图 6，但更收一点、不要伸得太远），**不拖在地上**。
>   - **弩**：两只手端着一把**黄铜和木头的弩**，水平指向右前方；弩臂是**淡蓝色的钢**，前端金色的箭头；弩身上面一颗**绿色的宝石**（毒）。弩比附图 6 短一点，弩尖不超过附图 8 剪影的右边。
> - **姿势照附图 1**（英雄联盟里他端弩的样子）：微微弓着身子站着，两只手都握着弩，弩端平朝右；两只脚底在同一条地面线上，一前一后稍微分开。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用 1536×1024**：**背包顶到脚底约 770 px，也就是约 70 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），背包顶 / 耳朵尖碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照附图 1）。整个人、整条尾巴和整把弩都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**比现在的精灵干净**：大块面清楚，少画小铆钉和小装饰。灰色的脸、粉耳朵、红鼻子、橙围巾、绿身体、蓝衣摆、黄铜弩要一眼分得清。附图 9–11 是本包同样密度（PPU 1.45–2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（附图 6 的黑底和光晕都不要），也不要画黑色或彩色背景。
> - 不画特效（不画毒雾、不画箭、不画毒桶）、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/twitch-ppu/twitch-A.png`（1536×1024，**真透明背景**）；原始生成图原样放进 `outputs/twitch-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/twitch_ppu_done.zip`。

## 附图（在压缩包 `twitch_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_twitch_stance.png` | 英雄联盟里的图奇端弩，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_twitch_side.png` | 同一帧，转得更侧 | 手怎么握弩、弩的样子 |
| `refs/3_twitch_head.png` | 头部特写 | 脸、护目镜、牙、耳朵 |
| `refs/4_twitch_back.png` | 同一帧，从身后看 | 尾巴从哪里长出来 |
| `refs/5_twitch_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_twitch_picture.png` | 之前定下的图奇造型 B | **造型、颜色、背包、弩照它** |
| `refs/7_twitch_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，32 格高） | **比例、身材** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**顶要碰到的线（浅灰）**、弩和尾巴的范围 |
| `style/9_style_caitlyn.png` | 本包的凯特琳（8 倍，PPU 1.45） | **只看风格** |
| `style/10_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格**：拿武器的射手 |
| `style/11_style_varus.png` | 本包的韦鲁斯（8 倍） | **只看风格** |

## 提示词：`twitch-A.png`

附图 1–11，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (his head enlarged toward a game sprite's proportions): a plague rat, a hunched rat-man with a crossbow (1 his crossbow stance in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same turned more to the side: how his hands hold the crossbow; 3 his head: the face, the goggle, the teeth, the ears; 4 the same frame seen from behind: where the tail grows from). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved picture of him: copy its COSTUME, COLOURS, BACKPACK and CROSSBOW (not its black background or its glow). Image 7 is his small game sprite now, shown 8x: copy its PROPORTIONS (a chibi: the head with the big ears about TWO FIFTHS of his height, a short stocky hunched body) - not its noisy detail. Image 8 is THIS picture's layout guide: his sprite now as a flat silhouette at the new size - how big he, his crossbow and his tail are and where he stands (not the pose); the dark grey line is the ground where his soles stand, the light grey line is where THE TOP OF HIS BACKPACK AND EARS goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at a similar square density: copy their clean pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of him, a 1536x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). He is about 770 px (about 70 squares) from the top of his backpack to his soles, the soles about 64 px above the bottom edge; the whole figure, the whole tail and the whole crossbow inside the picture with margins, nothing cut off; both soles on one ground line; nothing at all below his soles.
THE CHARACTER (image 6): a sneaky, grinning plague rat. HEAD: a GREY rat head with a long snout, a RED NOSE tip, a wide grin showing a row of sharp white teeth; two BIG EARS, grey outside and PINK inside; a BRASS GOGGLE over his near eye (a gold round frame, white lens, black pupil) on a gold strap across the forehead; an ORANGE-RED triangular BANDANA round his neck. BODY: DARK GREEN skin and arms; BROWN LEATHER bracers, belt and shoulder straps with a few gold studs; a big GREEN BACKPACK on his back with a brass frame and a row of TEAL ORBS on top. LEGS: a long TATTERED BLUE COAT hem (torn into strips, gold trim) with a blue-violet cloth hanging in front; purple-grey legs with brown wraps, white claws on his feet.
THE TAIL: a thin long rat tail striped PURPLE-GREY and CREAM, growing from behind him and curving up and back to the left (as in image 6 but more compact, not reaching as far), never lying on the ground.
THE CROSSBOW: held in BOTH HANDS, level, pointing to the right: a brass-and-wood stock, PALE STEEL-BLUE bow arms, a gold bolt head at the front and a GREEN GEM (poison) on top; a little shorter than in image 6, its tip not beyond the right edge of the silhouette in image 8.
PROPORTIONS (image 7): a chibi, the head with the ears about two fifths of his height, a short hunched stocky body - NOT taller or thinner.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE POSE (image 1): standing slightly hunched, both hands on the crossbow, the crossbow level pointing right; feet a little apart, one ahead of the other, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; CLEANER than his sprite now: big clear shapes, few tiny studs and trinkets; the grey face, pink ears, red nose, orange bandana, green body, blue coat and brass crossbow clearly apart; no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no poison cloud, no bolts in flight, no cask, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1536×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势照附图 1**：微微弓身，两手端弩朝右；背包顶到脚底约 770 px（约 70 格），两只脚底在同一条线上，脚底以下什么都没有。
- 造型、颜色和附图 6 一样：灰色鼠脸、红鼻头、尖牙、粉色大耳朵、黄铜护目镜、橙红围巾、绿身体、绿背包和青绿圆珠、棕色皮带、蓝色破衣摆、紫灰条纹尾巴、黄铜弩和绿宝石。
- 尾巴不拖地、不伸太远；弩不超过附图 8 剪影右边。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格，比现在的精灵干净。
- 画完后最后写 `outputs/twitch-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/twitch_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**（拉克丝的教训：Codex 的导出按大格子采样，脸都没了）：原画和 raw/ 放进 `assets/source/twitch/hd/`，照 `tools/art/design_lux_hd.py` / `design_ahri_hd.py` 按原图自己的格子读回；脸（护目镜、眼、牙）在 12 倍下查，半格画的重画；和凯特琳、金克丝、现在的图奇按游戏里的大小并排，给用户确认大小和 PPU。
- 动作：图奇的普攻、Q、W（扔毒桶）、E、R 都要端弩 / 抬手；拉克丝、阿狸自己绑骨的施法都被否了（「手和法杖一点动作都没有的 不奇怪？」「尾巴和身体分离 不及格」），大概率要 Codex 按旧版同一帧整帧重画再由 Claude 修（`casts_lux_hd.py` / `casts_ahri_hd.py` 的做法：按身体定大小、换上设计图的头、弩换成设计图的直弩、后脚钉住）。
- 尾巴每一帧都要接在身上；查 hd.rs、塞拉斯、佛耶戈 / 妮蔻灵魂表、待机和选人卡轮播、普攻 / R 的出手高度（bolt_y）、W 毒桶出手点、`skill2_e` 标签。
