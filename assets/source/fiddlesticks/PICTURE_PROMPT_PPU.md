# 费德提克（稻草人）：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 费德提克（稻草人）现在游戏里的造型是 1 倍的（附图 6）：从镰刀顶到脚底约 46 格。它是**远古恐惧**，**面朝右、驼着背站着**；头是**一只往前垂的土黄色粗麻布袋**，布面上几道深色缝线，麻袋正面**两只发光的黄绿色眼睛**；**头后面露出一只灰紫色的圆锯盘**；**画面左边**一条**缠着麻布的手臂**竖着握着**长长的黑木镰刀柄**，柄顶是**一把生锈的红褐色大弯刃**，**刀刃弧在头顶上方**（**最高处**）、刃尖往画面右边弯；另一条是**黑色细长的木手臂**；**深色的木头身子**、胸口一点**红色的光**；**细长的高跷腿**、**钩爪一样的脚**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，镰刀顶到脚底约 **138 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**往前垂的土黄色麻布袋头**、深色缝线、**两只发光的黄绿色眼睛**；**头后面灰紫色的圆锯盘**。
>   - 镰刀：**黑木的长柄**竖在画面左边，顶上**生锈的红褐色大弯刃**弧在头顶上方（最高处），**大小和位置照附图 6**。
>   - 身体：**缠着麻布的手臂**握着镰刀柄、**黑色细长的木手臂**、**深色的木头身子**。
>   - 腿：**细长的高跷腿**、**钩爪一样的脚**，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**镰刀顶到脚底约 828 px（约 138 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），镰刀顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**两只黄绿色的眼睛各自成块，不要糊成一团；麻布袋头、锯盘、镰刀的弯刃和高跷腿都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、镰刀柄和身体之间的空隙也是透明的。
> - 不画特效（眼睛的光只画在眼睛上，不往外发；没有乌鸦、烟雾、残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/fiddlesticks-ppu/fiddlesticks-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/fiddlesticks-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/fiddlesticks_ppu_done.zip`。

## 附图（在压缩包 `fiddlesticks_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_fiddlesticks_idle.png` | 英雄联盟里的费德提克（稻草人）（写实比例，**姿势和比例不要照它**） | 细节 |
| `refs/2_fiddlesticks_head.png` | 头部特写 | 头和脸 |
| `refs/3_fiddlesticks_back.png` | 从身后看 | 背面 |
| `refs/4_fiddlesticks_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_fiddlesticks_first_design.png` | 它现在这版造型的设计图（Codex 的 B，选定的那张，已经是 8 倍） | 长相、颜色 |
| `refs/6_fiddlesticks_now.png` | 它现在的游戏精灵（8 倍，1 倍密度，约 46 格高） | **要描的就是它**：姿势、Q 版比例、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**镰刀顶要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

## 提示词：`fiddlesticks-A.png`

附图 1–10，顺序同上表（1 = 1_fiddlesticks_idle.png, 2 = 2_fiddlesticks_head.png, 3 = 3_fiddlesticks_back.png, 4 = 4_fiddlesticks_splash.png, 5 = 5_fiddlesticks_first_design.png, 6 = 6_fiddlesticks_now.png, 7 = 7_layout.png, 8 = 8_style_diana.png, 9 = 9_style_ryze.png, 10 = 10_style_masteryi.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of an ancient scarecrow horror standing hunched, turned to the viewer's right - its head a DROOPING TAN BURLAP SACK hanging forward like a hood, a few dark stitches on it, TWO GLOWING YELLOW-GREEN EYES on its front; a GREY-VIOLET ROUND SAW DISC showing behind the head; on the viewer's left a BURLAP-WRAPPED ARM holding a LONG BLACK WOODEN SCYTHE SHAFT upright, a big RUSTY RED-BROWN CURVED BLADE on top arching over its head (its highest point), the blade's point curving to the viewer's right; its other arm THIN BLACK WOOD; a DARK WOODEN BODY with a small RED glow on the chest; THIN STILT LEGS with HOOKED CLAW FEET; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line marks THE SOLES, the light grey line THE TOP OF ITS SCYTHE BLADE. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of its scythe blade is about 828 px (about 138 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): the burlap sack head as big as in image 6 with its stitches; the two yellow-green eyes each a clear shape, never one muddy blob. The grey-violet saw disc behind the head with its teeth. The long black wooden shaft and the rusty curved blade as big and where they are in image 6, the blade over the head. The burlap-wrapped arm, the thin black wooden arm, the dark wooden body. The thin stilt legs and the hooked claw feet planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (the eyes' light stays inside the eyes; no crows, no smoke, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 6。
- 镰刀顶到脚底约 828 px（约 138 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/fiddlesticks-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/fiddlesticks_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/fiddlesticks/hd/`，照 `tools/art/design_khazix_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空（平均色会把眼睛糊掉）；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的费德提克（稻草人）按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- 动作包照 `pack_khazix_actions.py`：跑步逐帧写明哪条腿撑地（照布里茨跑步重画的写法：第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放按叠合法（`casts_khazix_hd.py --fits`：画稿叠到模板的浅色人影上取重合最好的比例）；外描边 2 格（用户：「避免过度高清」）。
- 霞、洛、费德提克（稻草人）、璐璐在同一个 PR（ppu-b6）（用户：「接下来利用PPU重做霞 洛 稻草人 璐璐 在一个pr里」）。
