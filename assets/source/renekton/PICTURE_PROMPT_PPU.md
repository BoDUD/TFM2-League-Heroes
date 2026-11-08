# 雷克顿（鳄鱼）：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 雷克顿（鳄鱼）现在游戏里的造型是 1 倍的（附图 6）：从头冠顶到脚底约 37 格。他是**沙漠死神**，一只**鳄鱼人**，**面朝右、弓着身子站着**；**青绿色的鳞片**；头上和背上是**骨白色的头冠和背甲**（**头冠顶是最高处**）；**往右伸的长嘴张开着**，**红色的口腔**、**白色的尖牙**；**黄色的眼睛**；**肩上和胸口是金橙色的铠甲**；**深蓝色的缠腰布和护腿**；**一把巨大的金橙色弯刃**握在身后，**弯刃在画面左边**；**爪子一样的手脚**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，头冠顶到脚底约 **111 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**骨白色的头冠**（最高处）、**往右伸的张开的长嘴**、**红色的口腔**、**白色的尖牙**、**黄色的眼睛**。
>   - 上身：**青绿色的鳞片**、**金橙色的肩甲和胸甲**、**骨白色的背甲**。
>   - 弯刃：**巨大的金橙色弯刃**握在身后、**在画面左边**，**大小和位置照附图 6**。
>   - 腿：**深蓝色的缠腰布和护腿**、**爪子一样的脚**，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1536×1024**：**头冠顶到脚底约 666 px（约 111 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），头冠顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。画布是横的：整个人、整把弯刃和尾巴也都在画面里，不要截掉。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**两只黄色的眼睛各自成块，不要糊成一团；头冠、尖牙、弯刃和爪子都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、弯刃和身体之间的空隙也是透明的。
> - 不画特效（弯刃不发光，没有怒气的红光、血花、残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1536×1024 的原图。
>
> - 交付：`outputs/renekton-ppu/renekton-A.png`（1536×1024，**真透明背景**）；原始生成图原样放进 `outputs/renekton-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/renekton_ppu_done.zip`。

## 附图（在压缩包 `renekton_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_renekton_idle.png` | 英雄联盟里的雷克顿（鳄鱼）（写实比例，**姿势和比例不要照它**） | 细节 |
| `refs/2_renekton_head.png` | 头部特写 | 头和脸 |
| `refs/3_renekton_back.png` | 从身后看 | 背面 |
| `refs/4_renekton_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_renekton_first_design.png` | 他现在这版造型的设计图（当初做精灵用的原稿，1 倍图放大 8 倍） | 长相、颜色 |
| `refs/6_renekton_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 37 格高） | **要描的就是它**：姿势、Q 版比例、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**头冠顶要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

## 提示词：`renekton-A.png`

附图 1–10，顺序同上表（1 = 1_renekton_idle.png, 2 = 2_renekton_head.png, 3 = 3_renekton_back.png, 4 = 4_renekton_splash.png, 5 = 5_renekton_first_design.png, 6 = 6_renekton_now.png, 7 = 7_layout.png, 8 = 8_style_diana.png, 9 = 9_style_ryze.png, 10 = 10_style_masteryi.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a crocodile warrior standing hunched, turned to the viewer's right - TEAL-GREEN SCALES; a BONE-CREAM HEADDRESS and back plates, the top of the headdress his highest point; a LONG SNOUT reaching to the viewer's right with its JAWS OPEN, a RED MOUTH and WHITE FANGS; YELLOW EYES; GOLD-ORANGE ARMOUR on his shoulders and chest; a DARK BLUE LOINCLOTH and leg guards; a GREAT CURVED GOLD-ORANGE GLAIVE held behind him, its blade on the viewer's left; CLAWED HANDS and FEET; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line marks THE SOLES, the light grey line THE TOP OF HIS HEADDRESS. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1536x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his headdress is about 666 px (about 111 squares) above the soles, the soles about 64 px above the bottom edge; the picture is wide: the whole figure, the whole glaive and the tail inside it, nothing cut off; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): the head as big as in image 6: the bone-cream headdress, the long open snout with its red mouth and white fangs, the two yellow eyes each a clear shape, never one muddy blob. The teal-green scales, the gold-orange shoulder and chest armour, the bone-cream back plates. The great curved glaive as big and where it is in image 6. The dark blue loincloth and leg guards and the clawed feet planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (the glaive does not glow; no red fury aura, no blood, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1536×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 6。
- 头冠顶到脚底约 666 px（约 111 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/renekton-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/renekton_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/renekton/hd/`，照 `tools/art/design_xayah_hd.py`（Codex 的原图是软边透明底：半透明度 128 抠图；按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的雷克顿（鳄鱼）按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- 动作包照 `pack_xayah_actions.py`：跑步逐帧写明哪条腿撑地（第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放按叠合法（`casts_xayah_hd.py --fits`）；外描边 2 格（细四肢的英雄 1 格，稻草人那次）；读回后逐帧量头的大小，GIF 里逐帧比新旧两边的大小变化（洛那次：「怎么模型会突然变大变小」是 Codex 把几帧的头画大了，只能交 Codex 重画头，不能整帧缩放）。
- 奥拉夫、伊泽瑞尔、赫卡里姆（人马）、雷克顿（鳄鱼）在同一个 PR（ppu-b7）（用户：「接下来重做奥拉夫 EZ 人马 鳄鱼」）。
