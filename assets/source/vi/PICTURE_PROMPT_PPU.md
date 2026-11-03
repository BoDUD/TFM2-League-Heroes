# 蔚：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 蔚现在游戏里的造型是 1 倍的（附图 6）：从头发顶到脚底约 40 格。她是 **3/4 侧面朝右的拳击架势**，**两腿大大分开、前腿弓着**；**亮粉色的头发往后梳、飘在脑后**，**头顶架着一副护目镜**（金色框、蓝色镜片）；**蓝色的眼睛**；脖子上**红色的围巾**；两只**巨大的金色海克斯拳套**（钢灰色的指节、**蓝色的能量核心**）：**一只在身前腰的高度**，**另一只举在胸前**；身上是**深灰色的护甲**，**金色的护板**，腿上有**粉色的护膝条**；**深色的靴子**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，头发顶到脚底约 **120 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、拳套的位置和大小、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**粉色的头发**一缕一缕往后飘、**头顶的护目镜**（金框、蓝镜片）；**眼睛、眉、嘴各自成块**，表情是自信的、带点挑衅。**头的大小就是以后每个动作都要保持的大小**。
>   - 身体：**红色的围巾**、**深灰色的护甲**和**金色的护板**、腰带。
>   - 拳套：**两只金色的大拳套**，**钢灰色的指节**一节一节清楚，**蓝色的能量核心**；大小和位置照附图 6，**不要缩小**。
>   - 腿：**深灰色的护腿**、**金色的护板**、**粉色的护膝条**、**深色的靴子**，两脚大开、站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**头发顶到脚底约 720 px（约 120 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），头发顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；拳套的指节和护目镜都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间的空隙也是透明的。
> - 不画特效（拳套的蓝光只画在核心上，不往外发；不要冲击波、残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/vi-ppu/vi-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/vi-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/vi_ppu_done.zip`。

## 附图（在压缩包 `vi_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_vi_idle.png` | 英雄联盟里的蔚（写实比例，**姿势和比例不要照它**） | 头发、护目镜、拳套、护甲的细节 |
| `refs/2_vi_head.png` | 头部特写 | 头发、护目镜、脸、围巾 |
| `refs/3_vi_back.png` | 从身后看 | 头发和护甲的背面 |
| `refs/4_vi_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_vi_first_design.png` | 她现在这版造型的设计图（用户认可的主稿） | 长相、拳套、护甲、颜色 |
| `refs/6_vi_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 40 格高） | **要描的就是它**：姿势、Q 版比例、颜色、拳套 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头发顶要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

## 提示词：`vi-A.png`

附图 1–10，顺序同上表（1 = 1_vi_idle.png, 2 = 2_vi_head.png, 3 = 3_vi_back.png, 4 = 4_vi_splash.png, 5 = 5_vi_first_design.png, 6 = 6_vi_now.png, 7 = 7_layout.png, 8 = 8_style_diana.png, 9 = 9_style_ryze.png, 10 = 10_style_masteryi.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a brawler in a boxing stance, three-quarter view turned to the viewer's right, her legs wide apart and the front knee bent - BRIGHT PINK HAIR swept back and flying behind her head, GOGGLES with a gold rim and blue lenses pushed up on top of her head, blue eyes; a RED SCARF at her neck; two HUGE GOLD HEXTECH GAUNTLETS with steel-grey knuckles and glowing BLUE CORES, one held in front of her at waist height, the other raised in front of her chest; DARK GREY ARMOUR with GOLD PLATES, PINK knee stripes, dark boots; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same gauntlets and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line is where the SOLES go, the light grey line is where THE TOP OF HER HAIR goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her hair is about 720 px (about 120 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG HEAD as in image 6, the pink hair in clear locks swept back, the gold-rimmed goggles on top; the eyes, the brows and the mouth each a clear shape, never one muddy blob; a confident, cocky look. The red scarf, the dark grey armour with its gold plates, the belt. The two big gold gauntlets as big and where they are in image 6, the steel-grey knuckles readable one by one, the blue cores. Dark grey leg armour with gold plates and pink knee stripes, dark boots, the feet wide apart and planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. The gauntlets as big as in image 6 - do not shrink them.
THE VIEW: as image 6, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the arms and the body are transparent.
No effects (the blue light stays inside the gauntlet cores, no glow around them, no shockwaves, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、拳套的位置和大小、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 6。
- 头发顶到脚底约 720 px（约 120 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/vi-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/vi_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/vi/hd/`，照 `tools/art/design_viego_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；几种 PPU 给用户选）读回；和本包其他英雄、现在的蔚按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把拳套算进“两脚中点”）。
- 动作包照 `pack_diana_actions.py`：跑步逐帧写明哪条腿撑地；每帧缩放取身高、头、身体面积三种量法的中位数（读回时旧帧的身体按旧帧的颜色和贴着描边来认，特效不算）；外描边 2 格（用户：「避免过度高清」）。
- 和崔斯特、艾克、萨科在同一个 PR（claude/vi-ppu）。
