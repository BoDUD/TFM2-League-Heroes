# 凯隐（暗裔形态）：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 凯隐（暗裔形态）现在游戏里的造型是 1 倍的（附图 6）：从角尖到脚底约 43 格。这是凯隐被拉亚斯吞噬后的**暗裔形态**，**面朝右、弓着身子半蹲着**；头上是**钢灰蓝色的头盔**，顶着**一对巨大的弯角**（最高处），盔下是**骷髅般的面甲**和**两只红色的眼睛**；全身是**深红色的血肉**，外面套着**钢灰蓝色的盔甲**（肩甲、臂甲、护腿上都有尖刺）；**手是红色的利爪**；**和本体一样的藕粉色腰布、深红色绳结腰带**，**靛蓝色的宽裤子、紫色的围裙**；**拉亚斯**在**身前右下方**：**深红色的月牙刀刃**、**红色的眼睛**；腿上是**钢灰蓝色的护腿**、**红色的爪脚**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，角尖到脚底约 **129 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、颜色**全部照现在的精灵**，不要换姿势（附图 1 的原画是写实比例，**不要照它的比例和姿势**，只看长相和细节；附图 3 是本体，腰布、绳结腰带、裤子、围裙、靴子每种形态都一样）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**钢灰蓝色的头盔**、**一对巨大的弯角**（最高处）、骷髅面甲、**两只红色的眼睛**在同一行。
>   - 身体：**深红色的血肉**、**钢灰蓝色的盔甲**和尖刺、**红色的利爪**；**藕粉色的腰布**、**深红色的绳结腰带**（和本体一样）。
>   - 镰刀：**拉亚斯**：**深红色的月牙刀刃**、**红色的眼睛**，在身前右下方，**大小和方向照附图 6**。
>   - 腿：**靛蓝色的宽裤子**、**紫色的围裙**、**钢灰蓝色的护腿**、**红色的爪脚**，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**角尖到脚底约 774 px（约 129 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），角尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**两只红眼各自成块，不要糊成一团；弯角、盔甲的尖刺、利爪和镰刀都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、镰刀和身体之间的空隙也是透明的。
> - 不画特效（没有红色的雾气、光晕、残影，**眼睛的红光只画在眼睛上**），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/kayn_darkin-ppu/kayn_darkin-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/kayn_darkin-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/kayn_darkin_ppu_done.zip`。

## 附图（在压缩包 `kayn_darkin_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_kayn_darkin_picture.png` | 用户选的暗裔形态原画（写实比例，**姿势和比例不要照它**） | 长相、颜色、细节 |
| `refs/2_kayn_darkin_head.png` | 原画的头部特写 | 头和脸 |
| `refs/3_kayn_darkin_base.png` | 凯隐本体的原画 | **腰布、绳结腰带、裤子、围裙、靴子每种形态都一样**，颜色照它 |
| `refs/4_kayn_darkin_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_kayn_darkin_first_design.png` | 他暗裔形态最初的原稿（Codex 的 A，用户选的） | 长相、颜色 |
| `refs/6_kayn_darkin_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 43 格高） | **要描的就是它**：姿势、Q 版比例、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**角尖要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

## 提示词：`kayn_darkin-A.png`

附图 1–10，顺序同上表（1 = 1_kayn_darkin_picture.png, 2 = 2_kayn_darkin_head.png, 3 = 3_kayn_darkin_base.png, 4 = 4_kayn_darkin_splash.png, 5 = 5_kayn_darkin_first_design.png, 6 = 6_kayn_darkin_now.png, 7 = 7_layout.png, 8 = 8_style_diana.png, 9 = 9_style_ryze.png, 10 = 10_style_masteryi.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of the same young assassin turned DARKIN, crouching, turned to the viewer's right - a BLUE-GREY STEEL HELM with a PAIR OF HUGE CURVED HORNS (his highest point), a skull-like faceplate with TWO RED EYES; DEEP CRIMSON FLESH all over under BLUE-GREY STEEL ARMOUR with spikes (shoulders, arms, shins); CRIMSON CLAWED HANDS; the same MAUVE-PINK SASH and CRIMSON ROPE BELT as his base form, BAGGY INDIGO TROUSERS with a VIOLET APRON; the scythe RHAAST low in front of him to the viewer's lower right: a CRIMSON CRESCENT BLADE with a RED EYE; crimson clawed feet; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Image 1 is the approved picture of this form and image 2 its head close up: the looks, the colours and the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 3 is the same character in his base form: the sash, the rope belt, the trousers, the apron and the boots are the same in every form - keep their colours. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line marks THE SOLES, the light grey line THE TIPS OF HIS HORNS. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The tips of his horns are about 774 px (about 129 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): the horned helm as big as in image 6, the two red eyes level and each a clear shape. The crimson flesh, the blue-grey steel armour with its spikes, the crimson claws; the mauve sash and the crimson rope belt the same as in image 3. Rhaast as big and where it is in image 6. The baggy indigo trousers, the violet apron, the steel shin guards and the crimson clawed feet planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (no red mist, no glow, no afterimages; the eyes' red stays inside the eyes), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、颜色和附图 6 一样**（细节照附图 1–3，但**不照原画的比例和姿势**）；头的大小照附图 6。
- 角尖到脚底约 774 px（约 129 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/kayn_darkin-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/kayn_darkin_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/kayn_darkin/hd/`，照 `tools/art/design_khazix_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空（平均色会把眼睛糊掉）；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的凯隐（暗裔形态）按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- **凯隐的三种形态（本体、暗裔、影流）一起读回，三张设计图用同一个 PPU**（变身前后一样密）；墙里的暗影剪影（`w_` / `rw_` / `hw_`）以后从新帧生成，不用画。
- 动作包照 `pack_khazix_actions.py`：跑步逐帧写明哪条腿撑地（照布里茨跑步重画的写法：第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放按叠合法（`casts_khazix_hd.py --fits`：画稿叠到模板的浅色人影上取重合最好的比例）；外描边 2 格（用户：「避免过度高清」）。
- 和这一批的另外几位在同一个 PR（claude/kayn-ppu）（用户：「下面重做凯隐 维克托 永恩 泰坦」）。
