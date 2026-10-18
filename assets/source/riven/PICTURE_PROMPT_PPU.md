# 锐雯：按 PPU 1.5 重画设计图 + 重铸的剑（给 Codex 的提示词）

> 锐雯现在游戏里的造型是 1 倍的：从头发尖到脚底只有 40 格，脸、肩甲、绷带和断剑的细节都挤在一起（附图 7）。这次和剑姬、诺手一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从头发尖到脚底约 **60 格**。这次画**两张**：一张全身设计图，一张开大招时重铸的剑。动作帧不用画，我这边按英雄联盟的骨骼来摆。
> - **比例照现在的游戏精灵（附图 7）**：头（连头发）约占身高的三分之一，身材结实；不要更高更瘦，也不要更矮。**断剑的大小照附图 6、7**（又宽又厚的大剑）。
> - **衣服、颜色照附图 6**（之前定下的锐雯造型）：
>   - 头：白色（略带暖灰）的短发，几撮向后翘起的尖发，后脑一小束；棕色皮肤，脸上淡色的战纹；**两只眼睛一样高**。
>   - 身体：绿色的上衣；**一块大的绿色肩甲**（带金属边，在哪一侧照附图 1、6）；棕色皮革腰带和护腰，前臂缠着白色绷带。
>   - 腿：短的深紫或棕色裤子，腿上缠绷带，棕色皮靴。
>   - **断剑**：一把又宽又厚的大剑，中间断开（断口是锯齿状），剑身深灰色、边缘银亮，剑格附近嵌着几道**绿色的符文**，剑柄缠皮。
> - **姿势照附图 1**（英雄联盟里的待机，**和现在的游戏精灵不一样**）：**远侧手握剑，把断剑扛在身后，剑尖斜着指向右上方、高过肩膀**（附图 1、2、4）；**近侧手张开放在胸前**；两腿一前一后、略弯，站稳，两只脚底在同一条地面线上。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用方形 1024×1024**：**头发尖到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），头发尖碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照附图 1）。整个人和整把剑都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。绿色衣服和肩甲要有亮边；白发要有浅灰的阴影，不要一片死白；剑身的亮边和绿色符文要清楚。附图 9–11 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。
> - 不画特效、地面、影子。
>
> **第二张：重铸的剑**（`riven-R-blade.png`）：开大招时断剑会重铸，断口处长出一段**亮绿色的能量剑刃**，把剑接成完整的一把长剑，还长出一截（附图 12 是现在游戏里开大时的样子）。请把**第一张里的同一把断剑**（同样的大小、同样的方向和角度、同样的剑柄和符文、同样每块 11 像素）单独画在一张 1024×1024 透明画布上，**断口外接上绿色能量剑刃**：亮绿到浅绿、中间一条接近白色的亮线，边缘是实心的深绿像素（不要半透明发光），长度和断剑本身差不多。只画剑，不画手和人。剑放在和第一张里一样的方向，剑柄末端放在画布中间偏左下。
>
> - 交付：`outputs/riven-ppu/riven-A.png` 和 `outputs/riven-ppu/riven-R-blade.png`（都是 1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/riven-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/riven_ppu_done.zip`。

## 附图（在压缩包 `riven_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_riven_idle.png` | 英雄联盟里的锐雯待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势**（剑扛在身后） |
| `refs/2_riven_side.png` | 同一帧的侧面（朝右） | 剑在背后的位置、肩甲 |
| `refs/3_riven_head.png` | 头部特写 | 脸、发型 |
| `refs/4_riven_blade.png` | 同一帧，断剑特写 | **断剑的形状、断口、符文** |
| `refs/5_riven_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_riven_picture.png` | 之前定下的锐雯造型（8 倍） | **衣服、颜色、断剑照它**（姿势不照它） |
| `refs/7_riven_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，40 格高） | **比例、身材**（姿势不照它） |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头发尖要碰到的线（浅灰）** |
| `refs/12_riven_r_blade_now.png` | 现在游戏里开大时的一帧（8 倍） | **第二张：重铸的剑**的样子 |
| `style/9_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_kaisa.png` | 本包的卡莎（8 倍，PPU 1.45） | **只看风格**：女性的脸、两只眼睛 |
| `style/11_style_camille.png` | 本包的青钢影（8 倍，PPU 1.5） | **只看风格** |

## 提示词 1：`riven-A.png`

附图 1–11（不要附 12），顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): a strong young swordswoman with a huge broken greatsword (1 her idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same from the side, facing right: where the blade rests behind her; 3 her head in 3/4 view facing right: the face and the spiky short hair; 4 the same frame close on the blade: the broken edge and the green runes). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved pixel picture of her (8x): copy its COSTUME, COLOURS and BLADE - not its pose. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (the head with the hair about a THIRD of her height, a sturdy build) - not its pose. Image 8 is THIS picture's layout guide: her sprite now as a flat silhouette at the new size - how big she is and where she stands (not the pose); the dark grey line is the ground where her soles stand, the light grey line is where the TIPS OF HER HAIR go. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). She is about 660 px (about 60 squares) from the tips of her hair to her soles, the soles about 64 px above the bottom edge; the whole figure and the whole blade inside the picture with margins, nothing cut off; both soles on one ground line.
THE CHARACTER (image 6): a determined, battle-worn exile. HEAD: short WHITE hair with a few spiky locks swept back and a small tail at the back, tan skin with faint pale war paint, the two eyes at the same height. BODY: a GREEN top; ONE big GREEN shoulder plate with a metal rim, on the shoulder where images 1 and 6 have it; a brown leather belt and waist guard; WHITE bandages wrapped on the forearms. LEGS: short dark trousers, bandaged legs, brown leather boots. THE BLADE: a huge, wide, thick greatsword BROKEN in the middle (a jagged break), dark grey with bright silver edges, a few glowing GREEN RUNES near the crossguard, a leather-wrapped grip.
PROPORTIONS (image 7): the head with the hair about a THIRD of her height, sturdy - NOT taller or thinner, NOT shorter; the blade as big as in image 6.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE POSE (image 1, NOT the pose of images 6-7): the far hand gripping the broken blade and resting it BEHIND HER BACK, the blade pointing UP AND TO THE RIGHT above her shoulder; the near hand open in front of her chest; the legs one ahead of the other, knees a little bent, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the green cloth and plate with LIT EDGES, the white hair with light grey shading (never one flat white mass), the blade with clear silver edges and bright green runes, the skin warm tan; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 2：`riven-R-blade.png`

附上刚画好的 `riven-A.png` 和 `refs/12_riven_r_blade_now.png`。

```text
Two attached images. Image 1 is a pixel-art character holding a huge BROKEN greatsword (every square 11 px). Image 2 is a small game sprite (8x) of the same character with her sword REFORGED: a bright green energy blade grows out of the broken edge and makes the sword whole and longer.
Draw ONLY THE SWORD of image 1 - the same sword, the same size, the SAME DIRECTION AND ANGLE as it is held in image 1, the same grip, crossguard, runes and broken blade, the same 11 px squares on one straight grid - alone on a 1024x1024 PNG with a genuine transparent background (every pixel fully transparent or fully opaque), the grip's end a little left of and below the middle of the picture. Out of the jagged broken edge, continue the blade with a GLOWING GREEN ENERGY BLADE about as long again as the broken blade: bright green to pale green with a near-white core line along its middle, its edge solid dark green squares (no soft glow, no semi-transparency, no halo), ending in a sharp point. A 2-square near-black outline around the metal parts as in image 1. No hand, no character, no effects, no background, no text.
```

## 交回前请检查

- 两张都是 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- 第一张：**姿势照附图 1**（剑扛在身后指向右上、近侧手张开在胸前），不是附图 6、7 那样剑压在身前；头约占身高三分之一；头发尖到脚底约 660 px（约 60 格），两只脚底在同一条线上。
- 衣服、颜色和附图 6 一样：白色尖短发、绿上衣、一块大绿肩甲（位置照附图 1、6）、棕皮带、白绷带、断剑和绿符文。
- 第二张：和第一张**同一把剑、同样大小、同样方向**，断口接上绿色能量剑刃（实心像素、中间亮线），只有剑。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/riven-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/riven_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/riven/hd/`，照 `tools/art/design_darius_hd.py` 读回：**按整张图拟合一个格距和相位**（拟合范围别包含格距的两倍），背景若不透明先沿描边抠图；行数多于 60 时只删身体、头不删；眼睛、嘴照原样；和剑姬、卡莎、青钢影、现在的锐雯按游戏里的大小并排，给用户确认大小和 PPU（不超过 1.5）。重铸的剑按同一格距读回，对齐到设计图里的剑上（剑柄对剑柄）。
- 定下后照 `tools/art/rig_darius_hd.py` 摆动作：手臂和剑只做无损的原样 / 镜像 / 直角转；腿用设计稿原样，跑步整条腿挪、抬（她没有甲裙，抬腿会露出切口：先量，不行再定）；`_r` 动作换成重铸的剑；烘焙特效照 `riven_bake.json`。给用户看带特效的演示动图。然后 ppu_restyle / ppu_hd / hd.rs、league.dll 版本、头像点、选人卡，开 PR；再按 preview-foes-1x 的做法检查别的英雄演示里有没有用到她。
