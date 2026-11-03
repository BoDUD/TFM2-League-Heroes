# 崔斯特：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 崔斯特现在游戏里的造型是 1 倍的（附图 6）：从帽顶到脚底约 41 格。他**面朝右站直**；头上是**宽檐的深色帽子**，**金色的帽边**、**红色的帽带和羽饰**；**黑色的长发**垂到肩后；**棕色的皮肤**、**青色发光的眼睛**；身上是**深藏青色的长外套**，**金色的滚边**、**红色的内衬**；里面是**白衬衫**、**红色的马甲**；**棕色的腰带**和金扣；**近侧的手在腰间拿着一扇三张牌**（蓝、红、金），**远侧的手垂着**；**棕色的靴子**、金色的靴口。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，帽顶到脚底约 **123 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、帽子、牌、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**宽檐帽**（深色帽身、金色帽边、红色帽带和羽饰）、**黑色长发**；帽檐下的脸：**青色的眼睛、眉、嘴各自成块**，表情是从容的、带点狡黠的笑。**头的大小就是以后每个动作都要保持的大小**。
>   - 身体：**深藏青色的长外套**和**金色滚边**、**红色内衬**；**白衬衫**、**红马甲**、**棕色腰带**和金扣。
>   - 手：**近侧的手在腰间拿着三张牌**（蓝、红、金，牌面清楚），**远侧的手垂着**，手指清楚。
>   - 腿：外套的下摆、**深色的裤子**、**棕色的靴子**和金色的靴口，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**帽顶到脚底约 738 px（约 123 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），帽顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；帽檐、牌和手指都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间的空隙也是透明的。
> - 不画特效（牌不发光、没有魔法、没有残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/twistedfate-ppu/twistedfate-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/twistedfate-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/twistedfate_ppu_done.zip`。

## 附图（在压缩包 `twistedfate_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_twistedfate_idle.png` | 英雄联盟里的崔斯特待机（写实比例，**姿势和比例不要照它**） | 帽子、外套、牌的细节 |
| `refs/2_twistedfate_head.png` | 头部特写 | 帽子、头发、脸 |
| `refs/3_twistedfate_back.png` | 从身后看 | 帽子和外套的背面 |
| `refs/4_twistedfate_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_twistedfate_first_design.png` | 他现在这版造型的设计图（用户选的生图草稿） | 长相、帽子、外套、颜色 |
| `refs/6_twistedfate_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 41 格高） | **要描的就是它**：姿势、Q 版比例、颜色、牌 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**帽顶要碰到的线（浅灰）** |
| `style/8_style_diana.png` | 本包的黛安娜（8 倍，PPU 1.81） | **只看风格** |
| `style/9_style_ryze.png` | 本包的瑞兹（8 倍，PPU 1.66） | **只看风格** |
| `style/10_style_masteryi.png` | 本包的易（8 倍，PPU 2.23） | **只看风格** |

## 提示词：`twistedfate-A.png`

附图 1–10，顺序同上表（1 = 1_twistedfate_idle.png, 2 = 2_twistedfate_head.png, 3 = 3_twistedfate_back.png, 4 = 4_twistedfate_splash.png, 5 = 5_twistedfate_first_design.png, 6 = 6_twistedfate_now.png, 7 = 7_layout.png, 8 = 8_style_diana.png, 9 = 9_style_ryze.png, 10 = 10_style_masteryi.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a card-playing gambler standing upright, turned to the viewer's right - a WIDE-BRIMMED DARK HAT with a GOLD brim edge and a RED band and plume, LONG BLACK HAIR down to his shoulders, brown skin, glowing CYAN eyes; a long DARK NAVY COAT with GOLD trim and RED lining, a white shirt and a RED VEST, a brown belt with a gold buckle; his near hand at his waist holding a FAN OF THREE CARDS (blue, red, gold), his far hand hanging; brown boots with gold tops; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same hat and cards and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line is where the SOLES go, the light grey line is where THE TOP OF HIS HAT goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his hat is about 738 px (about 123 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG HEAD as in image 6 under the wide hat - dark crown, gold brim edge, red band and plume - with the long black hair; under the brim the cyan eyes, the brows and the mouth each a clear shape, never one muddy blob; a calm, sly smile. The long dark navy coat with its gold trim and red lining, the white shirt, the red vest, the brown belt with its gold buckle. The near hand at his waist holding the three cards fanned (blue, red, gold, their faces readable), the far hand hanging, the fingers readable. The coat tails, dark trousers, brown boots with gold tops, the feet planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. The hat as wide as in image 6.
THE VIEW: as image 6, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the arms and the body are transparent.
No effects (the cards do not glow, no magic, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、帽子、牌、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 6。
- 帽顶到脚底约 738 px（约 123 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/twistedfate-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/twistedfate_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/twistedfate/hd/`，照 `tools/art/design_viego_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；几种 PPU 给用户选）读回；和本包其他英雄、现在的崔斯特按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把帽檐和外套下摆算进“两脚中点”）。
- 动作包照 `pack_diana_actions.py`：跑步逐帧写明哪条腿撑地；每帧缩放取身高、头、身体面积三种量法的中位数（读回时旧帧的身体按旧帧的颜色和贴着描边来认，特效不算）；外描边 2 格（用户：「避免过度高清」）。
- 和蔚、艾克、萨科在同一个 PR（claude/vi-ppu）。
