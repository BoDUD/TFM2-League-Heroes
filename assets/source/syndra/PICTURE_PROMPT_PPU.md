# 辛德拉：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 辛德拉现在游戏里的造型是 1 倍的（附图 6）：角尖到脚尖约 42 格，悬浮在空中——脚尖朝下、不着地；近侧（画面左边）的手放在腰旁，远侧（画面右边）的手在腰的高度向右伸出；银白色的长发从两边垂到腰下。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，角尖到脚尖约 **63 格**，和莫甘娜、梅尔、佐伊同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**深紫色的头盔**，左右各一只**向上弯的深紫色角**（带亮紫色的高光，**角的长短照附图 6**，不要照附图 1–2 那么长）；额前一条**金色的冠带**，正中一颗**洋红色的宝石**；**苍白的脸**，几乎正对画面，一双**大大的洋红色眼睛**和深色睫毛，**小小的深红色嘴**（微张），脖子上一条**红色的项圈**。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 头发：**银白色的长发**（淡紫灰色的阴影），从头盔下面沿两边垂到腰下，一缕一缕分得清。
>   - 上身：**金色的领子 / 护肩**，**深紫色的紧身上衣**，金色的饰边；腰间一条**洋红色的腰带**配金色。
>   - 手：近侧的手（画面左边）在腰旁，苍白的手；远侧的手（画面右边）在腰的高度向右伸出，手腕上一圈**洋红色的护腕**。
>   - 下身：**深紫色的裙摆**分成几片，金色的饰边，左边一片长的垂下来；**一条大腿露在外面**（苍白的皮肤）；**深紫色的长袜**，**尖头的靴子、靴尖是金色的**。
> - **朝向**：和附图 6 一样，四分之三侧身，**脸几乎正对画面、身体朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **她是浮在空中的**：脚尖朝下，**下面那只脚的脚尖正好落在附图 7 的深灰线上**（游戏里用这条线定位置），整个人不画地面、不画影子。
> - **画布用 1024×1024**：**角尖到脚尖约 693 px（约 63 格）**，最低的脚尖在离画布底边约 64 px 的地方（附图 7 的深灰线），角尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人和头发都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的眼睛、睫毛、嘴和额前的宝石各自成块，不要糊成一团；头发一缕一缕分得清。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、头发和身体之间的空隙也是透明的。
> - 不画特效（暗黑法球、紫色的能量光等都不要），不画地面、影子；**最低的脚尖以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/syndra-ppu/syndra-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/syndra-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/syndra_ppu_done.zip`。

## 附图（在压缩包 `syndra_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_syndra_idle.png` | 英雄联盟里的辛德拉待机，四分之三朝右（头放大到接近游戏精灵的比例） | 头盔、头发、衣服、手的细节（**角的长短不照它**） |
| `refs/2_syndra_head.png` | 头部特写 | 头盔、冠带和宝石、脸 |
| `refs/3_syndra_back.png` | 从身后看 | 头发、裙摆 |
| `refs/4_syndra_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_syndra_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、衣服、颜色 |
| `refs/6_syndra_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 42 格高） | **要描的就是它**：姿势、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚尖线（深灰）、**角尖要碰到的线（浅灰）** |
| `style/8_style_morgana.png` | 本包的莫甘娜（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_mel.png` | 本包的梅尔（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_zoe.png` | 本包的佐伊（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`syndra-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a dark sorceress hovering in the air - toes pointing down, not standing on anything; the near hand (image left) resting by her waist, the far hand (image right) reaching out to the right at waist height; long silver-white hair falling down both sides past her waist - shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same pose, the same costume and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, clothes and colours. Images 1-3 are 3D renders of the same character from the game (1 her idle - the helmet, the hair, the dress, the hands; 2 her head close up - the helmet, the crown band and its gem, the face; 3 from behind - the hair, the skirt). Her horns keep the SIZE they have in image 6: much shorter than in images 1-2. Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she floats; the dark grey line is where the tip of her LOWER TOE goes, the light grey line is where the TIPS OF HER HORNS go. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The tips of her horns are about 693 px (about 63 squares) above the tip of her lower toe, that toe tip about 64 px above the bottom edge; the whole figure and all of her hair inside the picture; nothing at all below her lowest toe. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a DARK PURPLE HELMET with two curved dark purple HORNS rising from its sides (bright violet highlights, as long as in image 6); a GOLD CROWN BAND across the brow with a MAGENTA GEM in the middle; a pale face turned almost to the viewer, LARGE MAGENTA EYES with dark lashes, a small dark red mouth slightly open, a RED CHOKER - the eyes, the lashes, the mouth and the gem each a clear shape, never one muddy blob. LONG SILVER-WHITE HAIR with pale lavender-grey shading, falling from under the helmet down both sides past her waist, its locks readable. A GOLD COLLAR / shoulder pieces, a fitted DARK PURPLE bodice with gold trim, a MAGENTA SASH with gold at her waist. The near hand (image left) pale, by her waist; the far hand (image right) reaching out to the right at waist height with a MAGENTA CUFF at the wrist. DARK PURPLE SKIRT panels with gold trim, a long one hanging down on the left; one BARE THIGH (pale skin); DARK PURPLE stockings and POINTED BOOTS with GOLD TIPS, toes pointing down.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A slim but not stick-thin figure, as image 6.
THE VIEW: 3/4 view as image 6: the face turned almost to the viewer, the body to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her arms and body and between her hair and body are transparent.
No effects (no dark spheres, no purple energy), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、比例、衣服、颜色和附图 6 一样**（细节照附图 1–3），只是更密、更细；**角的长短照附图 6**；头的大小照附图 6。
- 角尖到最低的脚尖约 693 px（约 63 格）；脚尖朝下、浮在空中，最低的脚尖以下什么都没有。
- 深紫色头盔和弯角、金色冠带和洋红宝石、洋红色大眼睛和睫毛、深红的嘴、红项圈、银白长发、金领子、深紫上衣、洋红腰带、洋红护腕、深紫裙摆和金饰边、露出的大腿、深紫长袜和金色靴尖都在；脸上各部分清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有法球和光效。
- 画完后最后写 `outputs/syndra-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/syndra_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/syndra/hd/`，照 `tools/art/design_rengar_hd.py`（原图自己的格子）读回；和莫甘娜、梅尔、现在的辛德拉按游戏里的大小并排（尺寸表 SIZES 算进去），给用户确认大小、脸、粗细。
- **白色的东西**：她的头发是银白色。抠白底时被围住的白块只有四周是描边时才当背景（`casts_rengar_hd.figure`），读回后逐个检查头发、眼白有没有被抠掉。
- **描述每个部件前先对旧精灵**（狮子狗的教训：提示词把旧精灵的尾巴看错，Codex 画到了身前）：动作包里写的每个部件都要在旧帧上确认过位置。
- 动作：照狮子狗 / 李青的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_rengar_actions.py`），读回到设计图上（`casts_rengar_hd.py`）；她是悬浮的，跑步是滑行（poses.json run flat、rise 0），**不要**要求换腿。她的 tag：idle、run、attack、skill（Q）、skill2（W）、skill2_e（E）、ult、hit、dead。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、法球的出手点、头像截取点、选人卡偏移。
