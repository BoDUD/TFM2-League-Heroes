# 泰坦（诺提勒斯）：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 泰坦（诺提勒斯）现在游戏里的造型是 1 倍的（附图 6）：从背上锚的顶到脚底约 51 格。他是**深海泰坦**，**面朝右、魁梧地站着**；头是一顶**大大的橙色潜水头盔**，正面是**深色的面窗**、里面**两只发红光的眼睛**；**背上扛着一只巨大的灰色铁锚**，锚的弯钩从头顶上方绕过来（**最高处**），锚冠在画面左上方；身上是**灰色的铁甲**，接缝里透出**青色的光**；**两只巨大的灰色铁拳**；**铜橙色的靴子**站稳。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，背上锚的顶到脚底约 **153 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**橙色的潜水头盔**、**深色的面窗**、**两只发红光的眼睛**。
>   - 锚：**巨大的灰色铁锚**扛在背上，弯钩从头顶上方绕过来（最高处），**大小和位置照附图 6**。
>   - 身体：**灰色的铁甲**、接缝里**青色的光**、**两只巨大的灰色铁拳**。
>   - 腿：**灰色的护腿**、**铜橙色的靴子**，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**背上锚的顶到脚底约 918 px（约 153 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），背上锚的顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**两只红眼各自成块，不要糊成一团；锚、头盔的面窗、铁拳和靴子都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、锚和身体之间的空隙也是透明的。
> - 不画特效（眼睛的红光和接缝的青光只画在它们自己身上、不往外发，没有水花、气泡、残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/nautilus-ppu/nautilus-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/nautilus-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/nautilus_ppu_done.zip`。

## 附图（在压缩包 `nautilus_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_nautilus_idle.png` | 英雄联盟里的泰坦（诺提勒斯）（写实比例，**姿势和比例不要照它**） | 细节 |
| `refs/2_nautilus_head.png` | 头部特写 | 头和脸 |
| `refs/3_nautilus_back.png` | 从身后看 | 背面 |
| `refs/4_nautilus_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_nautilus_first_design.png` | 他造型最初的原稿（Codex 的 A，用户选的） | 长相、颜色 |
| `refs/6_nautilus_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 51 格高） | **要描的就是它**：姿势、Q 版比例、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**背上锚的顶要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

## 提示词：`nautilus-A.png`

附图 1–10，顺序同上表（1 = 1_nautilus_idle.png, 2 = 2_nautilus_head.png, 3 = 3_nautilus_back.png, 4 = 4_nautilus_splash.png, 5 = 5_nautilus_first_design.png, 6 = 6_nautilus_now.png, 7 = 7_layout.png, 8 = 8_style_diana.png, 9 = 9_style_ryze.png, 10 = 10_style_masteryi.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of the titan of the depths standing broad and heavy, turned to the viewer's right - a BIG ORANGE DIVING HELMET with a DARK VISOR and TWO GLOWING RED EYES behind it; a HUGE GREY IRON ANCHOR carried on his back, its hooks curving over the top of his head (his highest point), its crown at the viewer's upper left; GREY IRON ARMOUR with TEAL light glowing in its seams; two MASSIVE GREY IRON FISTS; BRONZE-ORANGE BOOTS; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line marks THE SOLES, the light grey line THE TOP OF THE ANCHOR ON HIS BACK. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of the anchor on his back is about 918 px (about 153 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): the orange diving helmet as big as in image 6, the dark visor and the two red eyes each a clear shape. The huge grey anchor on his back as big and where it is in image 6, its hooks over his head. The grey iron armour with its teal seams, the two massive iron fists. The bronze-orange boots planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (the eyes' red and the seams' teal stay inside them; no water, no bubbles, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 6。
- 背上锚的顶到脚底约 918 px（约 153 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/nautilus-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/nautilus_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/nautilus/hd/`，照 `tools/art/design_khazix_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空（平均色会把眼睛糊掉）；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的泰坦（诺提勒斯）按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- 动作包照 `pack_khazix_actions.py`：跑步逐帧写明哪条腿撑地（照布里茨跑步重画的写法：第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放按叠合法（`casts_khazix_hd.py --fits`：画稿叠到模板的浅色人影上取重合最好的比例）；外描边 2 格（用户：「避免过度高清」）。
- 和这一批的另外几位在同一个 PR（claude/kayn-ppu）（用户：「下面重做凯隐 维克托 永恩 泰坦」）。
