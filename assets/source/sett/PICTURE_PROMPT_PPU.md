# 瑟提：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 瑟提现在游戏里的造型是 1 倍的（附图 6）：从头发顶到脚底约 42 格。他**几乎正对着看画的人、稍微朝右**，**两脚分开站稳**；**红色的短刺头**，头顶两侧有**尖尖的兽耳**；**晒黑的皮肤**、**金色的眼睛**；肩上披着**一大圈深紫色的毛皮披肩**，毛尖往外炸开；**光着上身**，胸肌和腹肌明显，脖子上一圈**金色的项圈**，两边肩头各有一个**金色的兽头扣**；外面是**敞开的深酒红长外套**，**金色滚边**，下摆垂到膝盖；**白色的长裤**，裤缝有**金色的条纹**；**两只手臂垂在身体两侧**，小臂是**深紫毛皮护臂**和**白色绷带**，手上是**金色的拳套**；**深酒红的靴子**，**金色的护片**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，头发顶到脚底约 **126 格**，和金克丝、贝蕾亚、锤石差不多的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是他的设计图，细节看附图 1–3）：姿势、Q 版比例、头发、毛皮披肩、外套、拳套、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的头**（和附图 6 一样的比例），**红色刺头和两只尖兽耳**清楚；脸是**晒黑的肤色**：**金色的眼睛、浓眉、嘴各自成块**，表情自信、带点痞气。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**深紫毛皮披肩**（一簇簇往外炸开的毛尖）、**金项圈**、两肩的**金兽头扣**；**光着的胸腹**，肌肉用 3–4 档肤色分清楚。
>   - 外套：**敞开的深酒红长外套**和**金色滚边**，下摆垂到膝盖。
>   - 手：**两只手臂垂在两侧**，**深紫毛皮护臂、白绷带、金拳套**，拳头和手指清楚。
>   - 腿：**白色长裤和金条纹**，两脚分开站稳，**深酒红靴子和金护片**。
> - **朝向**：和附图 6 一样，**几乎正面、稍微朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**头发顶到脚底约 756 px（约 126 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），头发顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、整圈毛皮和整件外套都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；兽耳、金兽头扣、拳套和手指都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间的空隙也是透明的。
> - 不画特效（拳风、汗水、气势都不要）；不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/sett-ppu/sett-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/sett-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/sett_ppu_done.zip`。

## 附图（在压缩包 `sett_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sett_idle.png` | 英雄联盟里的瑟提待机（写实比例，**姿势和比例不要照它**） | 毛皮披肩、金兽头扣、外套、拳套的细节 |
| `refs/2_sett_head.png` | 头部特写 | 红头发、兽耳、脸、金项圈、金兽头扣 |
| `refs/3_sett_back.png` | 从身后看 | 毛皮披肩和外套的背面 |
| `refs/4_sett_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_sett_first_design.png` | 他最早的设计图（8 倍） | 头发、毛皮、外套、颜色 |
| `refs/6_sett_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 42 格高） | **要描的就是它**：姿势、Q 版比例、头发、毛皮、外套、拳套、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头发顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_briar.png` | 本包的贝蕾亚（8 倍，PPU 2.94） | **只看风格** |
| `style/10_style_thresh.png` | 本包的锤石（8 倍，PPU 2.48） | **只看风格** |

## 提示词：`sett-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a brawler standing with his feet apart, facing almost straight at the viewer, turned slightly to the viewer's right - short spiky RED HAIR with two pointed beast EARS on top; TANNED skin, GOLD EYES; a big DARK VIOLET FUR MANTLE round his shoulders, its tufts bursting outwards; a BARE MUSCLED CHEST and abs, a GOLD COLLAR round his neck, a GOLD BEAST-HEAD CLASP on each shoulder; an open DARK WINE-RED LONG COAT with GOLD TRIM hanging to his knees; WHITE TROUSERS with gold stripes; BOTH ARMS hanging at his sides, dark violet fur bracers, white wrist wraps and GOLD KNUCKLE GAUNTLETS; dark wine-red boots with gold plates; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same hair, fur, coat, gauntlets and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is his first design, enlarged: the hair, the fur, the coat, the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 his idle - the fur mantle, the beast-head clasps, the coat, the gauntlets; 2 his head close up - the hair, the ears, the face, the gold collar and clasps; 3 from behind - the back of the fur mantle and the coat). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is where his SOLES go, the light grey line is where the TOP OF HIS HAIR goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his hair is about 756 px (about 126 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure, all the fur and the whole coat inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG HEAD as in image 6 with its spiky red hair and two pointed beast ears; the TANNED FACE - the gold eyes, the thick brows and the mouth each a clear shape, never one muddy blob; a cocky, confident look. The dark violet fur mantle in bursting tufts, the gold collar, the gold beast-head clasps crisp; the bare chest and abs shaded in 3-4 skin tones. The open dark wine-red coat with its gold trim to his knees. Both arms hanging at his sides: violet fur bracers, white wraps, gold knuckle gauntlets, the fists readable. White trousers with gold stripes, the feet apart and planted, dark wine-red boots with gold plates; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A broad, muscular build, as image 6.
THE VIEW: as image 6, facing almost straight at the viewer, turned slightly to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the arms and the body are transparent.
No effects (no punch trails, no sweat, no aura), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、头发、毛皮、外套、拳套、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：几乎正面、两脚分开站、两手垂在两侧；头的大小照附图 6。
- 头发顶到脚底约 756 px（约 126 格）；脚底碰到深灰线，下面什么都没有。
- 红刺头和兽耳、晒黑的脸和金眼睛、深紫毛皮披肩、金项圈和金兽头扣、光着的胸腹、金边深酒红长外套、白裤金条纹、毛皮护臂和金拳套、深酒红靴子和金护片都在；脸上各部分清楚。
- **每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/sett-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sett_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/sett/hd/`，照 `tools/art/design_senna_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；调色板 64 色；几种 PPU 给用户选）读回；和金克丝、贝蕾亚、锤石、现在的瑟提按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- **描述每个部件前先对旧精灵**：拳头怎么握、毛皮怎么炸开、腿怎么站；跑步每一帧写明哪条腿撑地（泰隆和赛娜的教训）。
- 动作：他的 tag：idle 16、run 8、attack 5、attack2 5、skill 11、skill2 7、ult 4、ult_dash 4、ult_slam 4、hit 2、dead 8、idle_base 8、bp 43（`hero_reels.json`：待机 = attack2 0–1 + skill 10）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移、豪意附加包 `league_sett_grit`。和赛娜在同一个 PR（claude/senna-ppu）。
