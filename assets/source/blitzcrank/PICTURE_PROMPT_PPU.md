# 机器人：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 机器人现在游戏里的造型是 1 倍的（附图 6）：从烟囱顶到脚底约 44 格。他是**蒸汽动力的金色机器人**，**几乎正面朝着我们**（只微微朝右）；**身体是一个大大的金色圆球**，胸口正中是**银色的仪表圈**（圈里是铜色的表盘）；**头很小**，嵌在身体顶上，**两只方形的粉色眼睛**；**两根钢灰色的烟囱**竖在头两边（画面左边的那根更高，是最高处）；**两肩是深灰色的机械关节**，**两条粗大的金色手臂**往下垂，**方块大拳头**几乎碰到地；**两条深色的活塞短腿**，**金色的大脚**站稳。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，烟囱顶到脚底约 **132 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头和烟囱：**小小的金色的头**、**两只方形的粉色眼睛**；**两根钢灰色的烟囱**（画面左边的更高）。
>   - 身体：**金色的大圆身体**、**银色的仪表圈**和里面**铜色的表盘**，金色上有深浅几档和划痕。
>   - 手臂：**深灰色的肩关节**，**两条粗大的金色手臂**往下垂，**方块大拳头**几乎碰到地，大小和位置照附图 6。
>   - 腿和脚：**深色的活塞短腿**、**金色的大脚**，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**烟囱顶到脚底约 792 px（约 132 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），烟囱顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**两只眼睛各自成块，不要糊成一团；烟囱、仪表圈、拳头和手指都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间的空隙也是透明的。
> - 不画特效（烟囱不冒蒸汽、没有电光、残影，**眼睛的粉光只画在眼睛上，不往外发**），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/blitzcrank-ppu/blitzcrank-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/blitzcrank-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/blitzcrank_ppu_done.zip`。

## 附图（在压缩包 `blitzcrank_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_blitzcrank_idle.png` | 英雄联盟里的机器人（写实比例，**姿势和比例不要照它**） | 细节 |
| `refs/2_blitzcrank_head.png` | 头部特写 | 头和脸 |
| `refs/3_blitzcrank_back.png` | 从身后看 | 背面 |
| `refs/4_blitzcrank_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_blitzcrank_first_design.png` | 他造型最初的设计图（Codex 的 B2） | 长相、颜色 |
| `refs/6_blitzcrank_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 44 格高） | **要描的就是它**：姿势、Q 版比例、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**烟囱顶要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

## 提示词：`blitzcrank-A.png`

附图 1–10，顺序同上表（1 = 1_blitzcrank_idle.png, 2 = 2_blitzcrank_head.png, 3 = 3_blitzcrank_back.png, 4 = 4_blitzcrank_splash.png, 5 = 5_blitzcrank_first_design.png, 6 = 6_blitzcrank_now.png, 7 = 7_layout.png, 8 = 8_style_diana.png, 9 = 9_style_ryze.png, 10 = 10_style_masteryi.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a round golden steam golem standing almost facing the viewer, turned only slightly to the right - a BIG ROUND GOLDEN BODY with a SILVER GAUGE RING on the middle of his chest (a copper dial inside it); a SMALL HEAD set on top of the body with TWO SQUARE PINK EYES; TWO STEEL-GREY CHIMNEYS standing on either side of the head (the one on the viewer's left the taller - his highest point); DARK GREY MECHANICAL SHOULDER JOINTS, two massive golden arms hanging down, BIG SQUARE FISTS nearly touching the ground; two short DARK PISTON LEGS, BIG GOLDEN FEET; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line marks THE SOLES, the light grey line THE TOPS OF HIS CHIMNEYS. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The tops of his chimneys is about 792 px (about 132 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): the small head as in image 6 on top of the round body; the two square pink eyes each a clear shape, never one muddy blob. The two steel-grey chimneys, the one on the viewer's left the taller. The big round golden body in its shades and scratches, the silver gauge ring with its copper dial. The dark grey shoulder joints, the two massive golden arms, the big square fists nearly touching the ground, as big and where they are in image 6. The short dark piston legs and the big golden feet planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (no steam from the chimneys, no electric sparks, no afterimages; the eyes' pink stays inside the eyes), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 6。
- 烟囱顶到脚底约 792 px（约 132 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/blitzcrank-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/blitzcrank_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/blitzcrank/hd/`，照 `tools/art/design_vi_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子取整格平均色、过半近黑记成黑线（FACES）；几种 PPU 给用户选）读回；和本包其他英雄、现在的机器人按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- 动作包照 `pack_vi_actions.py`：跑步逐帧写明哪条腿撑地；每帧缩放取身高、头、身体面积三种量法的中位数；外描边 2 格（用户：「避免过度高清」）。
- 和另外三位在同一个 PR（claude/khazix-ppu）（用户：「接下来重做螳螂 机器人 莉莉娅 烬」）。
