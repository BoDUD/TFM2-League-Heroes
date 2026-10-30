# 琴女：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 琴女现在游戏里的造型是 1 倍的（附图 6）：头顶到裙摆约 40 格。她**安静地站着**，**蓝色的长发扎成两条大大的双马尾**，头发上戴着**金色的发饰**；**青绿色的眼睛**；**蓝色的长裙**，镶着金边；**一把金色的竖琴（etwahl）横着挡在腰前**，从画面左边一直伸到右边，两只手扶在琴上。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，头顶到裙摆约 **60 格**，和娜美、迦娜、剑姬同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、Q 版比例、头发、裙子、竖琴、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的 Q 版头**（和附图 6 一样的比例），**蓝色的长发**，额前有刘海，**两边各扎一条大大的马尾**，发尾带一点浅蓝和金色；头上和马尾根部戴着**金色的发饰**；**青绿色的眼睛**，浅肤色，小小的嘴。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 身体：**蓝色的长裙**，领口和裙边是**金色的镶边**，腰下垂着几条**浅青色、镶金边的长布条**，盖在裙子上；裙摆垂到脚下，分成几片。
>   - 竖琴：**金色的竖琴（etwahl）**，**横着挡在腰前**，**左右两端都伸出身体外面**，两头是弯弯的金色装饰，中间有琴弦；**两只手扶在琴上**。
>   - 脚：裙摆下面露出一点脚尖，**站在地上**。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧（画面左边）颜色亮，远侧稍暗。
> - **裙摆最下面碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**头顶到裙摆约 660 px（约 60 格）**，裙摆在离画布底边约 64 px 的地方（附图 7 的深灰线），头顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、两条马尾和整把竖琴都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；发饰、裙子的金边、竖琴的弯头和琴弦都清楚。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（竖琴也不要发光晕），也不要画黑色或彩色背景。马尾和身体之间、手臂和身体之间、竖琴和身体之间的空隙也是透明的。
> - 不画特效（音符、光圈、光波都不要），不画地面、影子；**裙摆以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/sona-ppu/sona-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/sona-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/sona_ppu_done.zip`。

## 附图（在压缩包 `sona_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sona_idle.png` | 英雄联盟里的琴女待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 头发、发饰、裙子、竖琴的细节 |
| `refs/2_sona_head.png` | 头部特写 | 头发、发饰、脸、眼睛 |
| `refs/3_sona_back.png` | 从身后看 | 双马尾、背后的裙子 |
| `refs/4_sona_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_sona_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、头发、裙子、竖琴、颜色 |
| `refs/6_sona_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 40 格高） | **要描的就是它**：姿势、Q 版比例、头发、裙子、竖琴、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、裙摆线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/8_style_nami.png` | 本包的娜美（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_janna.png` | 本包的迦娜（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`sona-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a serene musician standing still, BLUE hair in two big TWIN TAILS with GOLD hair ornaments, TEAL eyes, a BLUE GOWN edged with GOLD, a GOLD ETWAHL (a harp-like instrument) held LEVEL before her waist, reaching out past both sides of her body, both hands resting on it; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same calm stance, the same hair, gown, instrument and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, the hair, the gown, the instrument and the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 her idle - the hair, the ornaments, the gown, the etwahl; 2 her head close up - the hair, the ornaments, the face, the eyes; 3 from behind - the twin tails, the back of the gown). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where the BOTTOM OF HER GOWN goes, the light grey line is where the TOP OF HER HEAD goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her head is about 660 px (about 60 squares) above the bottom of her gown, that bottom about 64 px above the bottom edge; the whole figure, both twin tails and the whole etwahl inside the picture; nothing at all below the gown. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG CHIBI HEAD as in image 6; LONG BLUE HAIR with a fringe, tied in TWO BIG TWIN TAILS, their ends lighter blue and gold; GOLD HAIR ORNAMENTS on her head and at the roots of the tails; TEAL EYES, fair skin, a small mouth - the eyes, the brows and the mouth each a clear shape, never one muddy blob. A long BLUE GOWN with GOLD trim at the neckline and the hems, PALE TEAL PANELS edged with gold hanging from the waist over the skirt, the skirt falling to her feet in several panels. The GOLD ETWAHL held LEVEL before her waist, both ends reaching out past her body with curled gold ornaments, strings in the middle, both hands resting on it. The tips of her feet just showing under the gown, standing. No glow around the instrument.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A slight build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the near side on the image LEFT in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the tails and the body, the arms and the body and the instrument and the body are transparent.
No effects (no music notes, no rings, no waves of light), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、头发、裙子、竖琴、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：静静站着、金色竖琴横在腰前、两手扶琴；头的大小照附图 6。
- 头顶到裙摆约 660 px（约 60 格）；裙摆碰到深灰线，下面什么都没有。
- 蓝色双马尾、金色发饰、青绿色眼睛、金边蓝裙、浅青色长布条、横在腰前的金色竖琴都在；脸上各部分清楚，竖琴没有光晕。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/sona-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sona_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/sona/hd/`，照 `tools/art/design_leona_hd.py`（按原图自己的格子读、每条线贴着最近的色边；调色板 64 色；眼睛读成深色时那几行改用均匀格子）读回；和娜美、迦娜、现在的琴女按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把竖琴的两头算进“两脚中点”）。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：竖琴怎么拿、手在哪、马尾朝哪。
- 动作：她的 tag：idle 36、run 8、attack 6、attack_p 6、skill 6、skill2 6、ult 8、hit 2、dead 8、idle_base 8、bp 58（`hero_reels.json`：待机 = skill 1–4 + attack_p 1–3）。没有烤进动作的特效。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移。装游戏前先合进最新 main，版本号接着游戏里现装的往上加。
