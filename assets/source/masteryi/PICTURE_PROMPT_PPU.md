# 易大师：照现在的精灵按 PPU 2.5 重画设计图（给 Codex 的提示词）

> 易大师现在游戏里的造型是 1 倍的（附图 5）：从剑尖到脚底约 56 格。他**压低身子、往前探着冲**（朝画面右边），**前腿弯、后腿蹬**；看到的是他**近侧肩膀和背的那一面**；头上是**一顶圆头盔**，面前一排**六个发着绿光的目镜**，头盔是**灰钢色**、**金色的边**；**灰钢色的大肩甲**、**金色的边和橙色的宝石**；身上是**深棕色的衣服**、**深灰蓝的盔甲**；**近侧手把长剑举在身后**，**剑身是亮绿色的**，从他身后**斜着往画面左上方伸出去**，剑尖是整个人的最高点；**深灰蓝的护腿和靴子**。这次**照着它画密一点**：按 **PPU 2.5**，**每个游戏像素画成 2.5 格**，剑尖到脚底约 **140 格**，和本包其他英雄差不多的密度（附图 7–9）。
> - **照附图 5 描**（细节看附图 1–3）：姿势、Q 版比例、长剑、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**圆头盔**和**一排六个绿色目镜**（和附图 6 一样的比例），**金色的边**清楚。**头的大小就是以后每个动作都要保持的大小**。
>   - 身体：**灰钢色的大肩甲**、**金色的边和橙色的宝石**、深棕色的衣服、深灰蓝的盔甲。
>   - 剑：**近侧手握着长剑举在身后**，手指清楚；**剑身亮绿色**、亮面暗面分清楚，**又长又直**，**角度和长短照附图 6**。
>   - 腿：**深灰蓝的护腿和靴子**，前腿弯、后腿蹬地。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 5 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 5 一样，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 6 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**剑尖到脚底约 840 px（约 140 格）**，脚底在离画布底边约 64 px 的地方（附图 6 的深灰线），剑尖碰到附图 6 的浅灰线（附图 6 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；手指和长剑都清楚。** 附图 7–9 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间的空隙也是透明的。
> - 不画特效（剑光、残影、分身都不要），**目镜的绿光只画在目镜里，不往外发**；不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/masteryi-ppu/masteryi-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/masteryi-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/masteryi_ppu_done.zip`。

## 附图（在压缩包 `masteryi_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_masteryi_idle.png` | 英雄联盟里的易大师待机（写实比例，**姿势和比例不要照它**） | 头盔、目镜、肩甲、长剑的细节 |
| `refs/2_masteryi_head.png` | 头部特写 | 头盔和六个绿色目镜、肩甲 |
| `refs/3_masteryi_back.png` | 从身后看 | 盔甲正面、腰带、护腿 |
| `refs/4_masteryi_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_masteryi_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 56 格高） | **要描的就是它**：姿势、Q 版比例、颜色、长剑 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**剑尖要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_viego.png` | 本包的佛耶戈（8 倍，PPU 2.45） | **只看风格** |
| `style/10_style_talon.png` | 本包的泰隆（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`masteryi-A.png`

附图 1–9，顺序同上表（1 = 1_masteryi_idle.png, 2 = 2_masteryi_head.png, 3 = 3_masteryi_back.png, 4 = 4_masteryi_splash.png, 5 = 6_masteryi_now.png, 6 = 7_layout.png, 7 = 8_style_jinx.png, 8 = 9_style_viego.png, 9 = 10_style_talon.png）。

```text
9 attached images. Image 5 is THE picture to trace: a pixel-art game sprite of a swordsman in a low lunge toward the viewer's right, seen from his near shoulder and back - the front knee bent, the back leg pushing off; a ROUND HELMET with a row of SIX GREEN-GLOWING GOGGLE LENSES, grey steel with GOLD trim; a big GREY STEEL PAULDRON with gold trim and orange gems; dark brown cloth and dark slate armour; his near hand holding a long SWORD with a BRIGHT GREEN BLADE raised behind him, slanting up to the image's UPPER LEFT, its tip the highest point of the picture; dark slate greaves and boots; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 6 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line is where the SOLES go, the light grey line is where THE SWORD'S TIP goes. Images 7-9 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The sword's tip is about 840 px (about 140 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 5, detailed after images 1-3): the ROUND HELMET as in image 6 with its row of six green lenses and gold trim crisp; the big grey steel pauldron with its gold trim and orange gems; the dark brown cloth and slate armour. The near hand gripping the SWORD behind him, the fingers readable; the bright green blade long and straight with clear light and shadow faces, at the same angle and as long as in image 6. Dark slate greaves and boots, the front knee bent, the back leg pushing off; both soles on one line.
The head the size it has in image 5 (it keeps this size in every later animation) - neither enlarge nor shrink it. A lean build, as image 5.
THE VIEW: as image 5, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the arms and the body are transparent.
No effects (no sword trails, no afterimages, no clones; the green glow stays inside the lenses), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、长剑、颜色和附图 5 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 5。
- 剑尖到脚底约 840 px（约 140 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/masteryi-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/masteryi_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/masteryi/hd/`，照 `tools/art/design_viego_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；几种 PPU 给用户选）读回；和本包其他英雄、现在的易大师按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把长剑算进“两脚中点”）。
- 动作包照 `pack_viego_actions.py`：跑步逐帧写明哪条腿撑地；每帧缩放取身高和头的几何平均（瑟提的教训：只按头拉平身体会一大一小）；外描边 2 格（用户：「避免过度高清」）。
- 和戴安娜、易大师、瑞兹在同一个 PR（claude/diana-ppu）。
