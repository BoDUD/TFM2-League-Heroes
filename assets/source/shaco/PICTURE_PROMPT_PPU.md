# 萨科：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 萨科现在游戏里的造型是 1 倍的（附图 5）：从帽顶到脚底约 43 格。他**面朝右站着，两脚分开**；头上是**双角小丑帽**：**深蓝色的角往左后方卷**、**红色的角往上翘**，两个角尖各挂一个**金铃**；脸是**白色的面具**，**冰青色的眼睛**、**咧开的大嘴**；脖子上是**白色尖角的褶领**，**金色的滚边**；身上是**红色和深蓝色斜着拼开的小丑服**，**金色的滚边和纽扣**、**棕色的腰带**；**红色的灯笼袖**；**两只手各拿一把匕首**：**远侧的手往左边伸出去，刀尖朝左**，**近侧的手垂在身边，刀尖朝下**；**黑白格子的裤子**；**红色的尖头鞋往上卷**、金色的鞋口。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，帽顶到脚底约 **129 格**，和本包其他英雄差不多的密度（附图 7–9）。
> - **照附图 5 描**（细节看附图 1–3）：姿势、Q 版比例、帽子、匕首的位置和方向、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**双角小丑帽**（深蓝的角往左卷、红角往上，**两个金铃**）；**白色面具**上**冰青色的眼睛、眉、咧开的大嘴各自成块**，表情是阴森的笑。**头的大小就是以后每个动作都要保持的大小**。
>   - 身体：**白色尖角的褶领**和**金色滚边**；**红色和深蓝色斜拼的小丑服**、**金色的滚边和纽扣**、**棕色的腰带**；**红色的灯笼袖**。
>   - 手和匕首：**两把匕首**（白色刀身、深色刀柄），**远侧的往左伸、近侧的朝下**，位置和方向照附图 5；手指清楚。
>   - 腿：**黑白格子的裤子**（格子整齐、清楚）、**红色的卷尖鞋**和金色的鞋口，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 5 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 5 一样，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 6 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**帽顶到脚底约 774 px（约 129 格）**，脚底在离画布底边约 64 px 的地方（附图 6 的深灰线），帽顶碰到附图 6 的浅灰线（附图 6 只看大小和位置）。整个人和两把匕首都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；帽角、金铃、匕首和裤子的格子都清楚。** 附图 7–9 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、匕首和身体之间的空隙也是透明的。
> - 不画特效（没有烟雾、分身、毒液、残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/shaco-ppu/shaco-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/shaco-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/shaco_ppu_done.zip`。

## 附图（在压缩包 `shaco_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_shaco_idle.png` | 英雄联盟里的萨科待机（写实比例，**姿势和比例不要照它**） | 帽子、面具、褶领、衣服、匕首的细节 |
| `refs/2_shaco_head.png` | 头部特写 | 帽子、金铃、面具、褶领 |
| `refs/3_shaco_back.png` | 从身后看 | 帽子和小丑服的背面 |
| `refs/4_shaco_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_shaco_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 43 格高） | **要描的就是它**：姿势、Q 版比例、颜色、帽子、匕首 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**帽顶要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

（没有设计图那一张：他现在的精灵就是 Codex 那张 46 行的定稿。）

## 提示词：`shaco-A.png`

附图 1–9，顺序同上表（1 = 1_shaco_idle.png, 2 = 2_shaco_head.png, 3 = 3_shaco_back.png, 4 = 4_shaco_splash.png, 5 = 6_shaco_now.png, 6 = 7_layout.png, 7 = 8_style_diana.png, 8 = 9_style_ryze.png, 9 = 10_style_masteryi.png）。

```text
9 attached images. Image 5 is THE picture to trace: a pixel-art game sprite of a sinister jester standing with his feet apart, turned to the viewer's right - a TWO-HORNED JESTER HAT, the DARK BLUE horn curling back to the left, the RED horn rising up, a GOLD BELL on each tip; a WHITE MASK face with ICE-BLUE eyes and a WIDE GRIN; a white spiky RUFF with gold trim; a jester suit split diagonally in RED and DARK NAVY with GOLD trim and buttons, a brown belt, puffed RED sleeves; a DAGGER in each hand - the far hand reaching out to the left with its blade pointing left, the near hand hanging at his side with its blade pointing down; BLACK-AND-WHITE CHECKED trousers; curled RED pointed shoes with gold cuffs; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same hat and daggers and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 6 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line is where the SOLES go, the light grey line is where THE TOP OF HIS HAT goes. Images 7-9 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his hat is about 774 px (about 129 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure and both daggers inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 5, detailed after images 1-3): a BIG HEAD as in image 5 under the two-horned hat - dark blue horn curling left, red horn up, the two gold bells; on the white mask the ice-blue eyes, the brows and the wide grin each a clear shape, never one muddy blob; a creepy smile. The white spiky ruff with its gold trim; the red-and-navy diagonal jester suit with its gold trim and buttons, the brown belt, the puffed red sleeves. The two daggers (white blades, dark grips) where and as they point in image 5, the fingers readable. The black-and-white checked trousers with an even, clear check; the curled red shoes with gold cuffs, the feet planted; both soles on one line.
The head the size it has in image 5 (it keeps this size in every later animation) - neither enlarge nor shrink it. The hat as big as in image 5.
THE VIEW: as image 5, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs, between the arms and the body and between the daggers and the body are transparent.
No effects (no smoke, no clones, no poison, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、帽子、匕首的位置和方向、颜色和附图 5 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 5。
- 帽顶到脚底约 774 px（约 129 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/shaco-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/shaco_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/shaco/hd/`，照 `tools/art/design_viego_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；几种 PPU 给用户选）读回；和本包其他英雄、现在的萨科按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把匕首和帽角算进“两脚中点”）。
- 动作包照 `pack_diana_actions.py`：跑步逐帧写明哪条腿撑地（萨科的旧跑步换过腿，`LEGS_FIX.md`）；每帧缩放取身高、头、身体面积三种量法的中位数（读回时旧帧的身体按旧帧的颜色和贴着描边来认，特效不算）；外描边 2 格（用户：「避免过度高清」）。
- 和蔚、崔斯特、艾克在同一个 PR（claude/vi-ppu）。
