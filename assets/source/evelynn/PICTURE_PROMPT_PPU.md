# 伊芙琳：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 伊芙琳现在游戏里的造型是 1 倍的（附图 6）：从头发顶到脚底约 41 格。她**面朝右站着**；头上是**一大团粉白色的头发**，像火焰一样**往后上方（画面左上）**飘起来，发梢是亮粉色，头顶有几缕**深紫色的尖角**；**淡紫偏白的皮肤**，**眼睛发着黄光**；身上是**深靛蓝色的紧身衣**，有**粉色的拼块**（胸前、腰胯、大腿）；**近侧的手**举在胸前，**远侧手臂**垂着，手是**粉色的长爪**；**粉色和深紫的长腿**，细高跟；背后伸出**两条深紫色的鞭须（Lashers）**，往下垂到两边地上再**卷起来**，末端是**发亮的紫色尖片**（左边那条卷在画面左下，右边那条卷在画面右下）。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，头发顶到脚底约 **123 格**，和金克丝、贝蕾亚、女枪差不多的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是她的设计图，细节看附图 1–3）：姿势、Q 版比例、头发、鞭须、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的头和一大团粉白头发**（和附图 6 一样的比例），发梢的粉色和亮白色分层清楚，头顶的深紫尖角清楚；脸是**淡紫偏白**：**发黄光的眼睛、眉、嘴各自成块**，表情冷艳。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 身体：**深靛蓝紧身衣**和**粉色拼块**，腰身细。
>   - 手：粉色的**长爪**，手指清楚，近侧手在胸前、远侧手垂着，照附图 6。
>   - 鞭须：**两条深紫鞭须**从背后伸出，垂到两边、末端卷起，**紫色发亮的尖片**清清楚楚，长度和卷的位置照附图 6。
>   - 腿：**粉色和深紫的长腿**、细高跟，照附图 6 的站姿。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。**鞭须的最低点也不能低于这条线。**
> - **画布用 1024×1024**：**头发顶到脚底约 738 px（约 123 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），头发顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、整团头发和两条鞭须都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；爪子、手指和鞭须的尖片都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、鞭须和身体之间的空隙也是透明的。
> - 不画特效（黑雾、隐身、残影都不要），**眼睛的黄光只画在眼睛里，不往外发光**；不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/evelynn-ppu/evelynn-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/evelynn-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/evelynn_ppu_done.zip`。

## 附图（在压缩包 `evelynn_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_evelynn_idle.png` | 英雄联盟里的伊芙琳待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 头发、紧身衣、爪、鞭须的细节 |
| `refs/2_evelynn_head.png` | 头部特写 | 头发、尖角、脸、黄眼睛 |
| `refs/3_evelynn_back.png` | 从身后看 | 鞭须从背后长出来的样子、头发背面 |
| `refs/4_evelynn_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_evelynn_first_design.png` | 她最早的设计图（8 倍） | 头发、鞭须、颜色 |
| `refs/6_evelynn_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 41 格高） | **要描的就是它**：姿势、Q 版比例、头发、鞭须、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头发顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_briar.png` | 本包的贝蕾亚（8 倍，PPU 2.94） | **只看风格** |
| `style/10_style_missfortune.png` | 本包的女枪（8 倍，PPU 2.76） | **只看风格** |

## 提示词：`evelynn-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a demon woman standing, turned to the viewer's right - a BIG MASS OF PINK-AND-WHITE HAIR blowing up and back like a flame to the image's upper left, its tips hot pink, a few dark violet horn-like spikes on top; PALE LILAC skin, softly GLOWING YELLOW EYES; a dark indigo bodysuit with PINK panels on the chest, hips and thighs; the near hand raised before her chest, the far arm hanging, both hands long PINK CLAWS; long pink and dark violet legs on thin heels; and TWO DARK VIOLET LASHERS growing from her back, hanging down to either side and CURLING UP at the ends, each ending in a glowing VIOLET BLADE TIP (one curled at the image's lower left, one at its lower right); shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same hair, lashers and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is her first design, enlarged: the hair, the lashers, the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 her idle - the hair, the bodysuit, the claws, the lashers; 2 her head close up - the hair, the spikes, the face, the yellow eyes; 3 from behind - where the lashers grow from her back, the back of the hair). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF HER HAIR goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her hair is about 738 px (about 123 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, all the hair and both lashers inside the picture; nothing at all below the soles (the lashers end at or above the soles' line). Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG HEAD with its big flame of hair as in image 6, layered hot pink and bright white, the dark violet spikes crisp; the PALE LILAC FACE - the glowing yellow eyes, the brows and the lips each a clear shape, never one muddy blob; a cold, alluring look. A slim dark indigo bodysuit with its pink panels. Long pink claws, the fingers readable. The two dark violet lashers, as long and curled as in image 6, their glowing violet blade tips crisp. Long pink and dark violet legs on thin heels; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A slim build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the lashers and the body are transparent.
No effects (no shadow mist, no camouflage shimmer, no afterimages; the yellow glow stays inside the eyes), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、头发、鞭须、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：面朝右站着、头发往左上飘、近侧手在胸前、两条鞭须垂到两边卷起；头的大小照附图 6。
- 头发顶到脚底约 738 px（约 123 格）；脚底碰到深灰线，下面什么都没有，鞭须也不低于这条线。
- 粉白头发和深紫尖角、淡紫皮肤、发黄光的眼睛、深靛蓝紧身衣和粉色拼块、粉色长爪、两条带紫色尖片的深紫鞭须、粉紫长腿和细高跟都在；脸上各部分清楚；眼睛的光不往外发。
- **每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/evelynn-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/evelynn_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/evelynn/hd/`，照 `tools/art/design_senna_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；调色板 64 色；几种 PPU 给用户选）读回；和金克丝、贝蕾亚、女枪、现在的伊芙琳按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把鞭须算进“两脚中点”）。
- **描述每个部件前先对旧精灵**：手怎么放、鞭须怎么卷、腿怎么站；跑步每一帧写明哪条腿撑地（泰隆和赛娜的教训）。
- 动作：她的 tag：idle 26、run 8、attack 6、attack_e 6、attack_e2 9、skill 8、skill2 6、ult 6、hit 2、dead 8、idle_base 8、bp 50（`hero_reels.json`：待机 = attack_e 0–2 + attack 0–1）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移。和赛娜在同一个 PR（claude/senna-ppu）。
