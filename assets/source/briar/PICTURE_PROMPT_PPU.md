# 贝蕾亚：照现在的精灵按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 贝蕾亚现在游戏里的造型是 1 倍的（附图 6）：从刑枷顶到脚底约 46 格。她**叉开腿站着**；脖子上**套着一副黑铁大刑枷**，刑枷是一大圈黑色的铁框，上面有**金色的铆钉和尖角**，顶上有一块**红色的宝石**，**两只手腕也锁在刑枷两边**，手从刑枷左右两端伸出来；**白色的乱蓬蓬短发**，带一点**粉红**；**浅蓝色的眼睛**，张着嘴；**黑色的短衣**，上面溅着**红色**；**光着的腿**，**小腿缠着黑色绑带**，**露着脚趾**。这次**照着它画密一点**：按 **PPU 2.2**，**每个游戏像素画成 2.2 格**，刑枷顶到脚底约 **101 格**，和金克丝、阿狸、安妮同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、Q 版比例、刑枷、头发、衣服、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的 Q 版头**（和附图 6 一样的比例），**白色的乱蓬蓬短发**，带一点粉红；**浅蓝色的眼睛**，浅肤色，张着的嘴。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 刑枷：**黑铁的大刑枷**套在脖子上，比头还宽，**金色的铆钉、尖角和镶边**，顶上一块**红宝石**；**两只手腕锁在刑枷的左右两端**，手从两端伸出来。
>   - 身体：**黑色的短衣**，溅着**红色**；**光着的腿**，**小腿缠着黑色绑带**、**露着脚趾**（不是靴子）。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧（画面左边）颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**刑枷顶到脚底约 708 px（约 101 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），刑枷顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人和整副刑枷都在画面里。
> - **像素块**：大小一致的方块，**每块 7 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；刑枷的铆钉、尖角、红宝石和手指都清楚。** 附图 8–10 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、刑枷和身体之间的空隙也是透明的。
> - 不画特效（血雾、光圈、飞溅都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/briar-ppu/briar-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/briar-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/briar_ppu_done.zip`。

## 附图（在压缩包 `briar_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_briar_idle.png` | 英雄联盟里的贝蕾亚待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 刑枷、头发、衣服的细节 |
| `refs/2_briar_head.png` | 头部特写 | 头发、脸、眼睛、刑枷 |
| `refs/3_briar_back.png` | 从身后看 | 刑枷的背面、头发、衣服 |
| `refs/4_briar_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_briar_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、刑枷、衣服、颜色 |
| `refs/6_briar_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 46 格高） | **要描的就是它**：姿势、Q 版比例、刑枷、头发、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**刑枷顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍，PPU 2.2） | **只看风格** |
| `style/9_style_ahri.png` | 本包的阿狸（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_annie.png` | 本包的安妮（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`briar-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a wild girl standing with her feet apart, a big DARK IRON PILLORY locked round her neck - a wide black iron frame wider than her head, with GOLD studs, spikes and edging and a RED GEM on top, BOTH HER WRISTS LOCKED in its two ends, her hands sticking out of them - short messy WHITE hair with a touch of pink, PALE BLUE eyes, an open mouth, a short BLACK outfit splashed with RED and a gold buckle, bare legs with BLACK WRAPS round the shins and bare toes; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same pillory, hair, outfit and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, the pillory, the outfit and the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 her idle - the pillory, the hair, the outfit; 2 her head close up - the hair, the face, the eyes, the pillory; 3 from behind - the back of the pillory, the hair, the outfit). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF THE PILLORY goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of the pillory is about 708 px (about 101 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure and the whole pillory inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG CHIBI HEAD as in image 6; short messy WHITE hair with a touch of pink; PALE BLUE EYES, fair skin, an open mouth - the eyes, the brows and the mouth each a clear shape, never one muddy blob. The DARK IRON PILLORY round her neck, wider than her head, its GOLD studs, spikes and edging and the RED GEM on top clear; her two wrists locked in its two ends, the hands and fingers sticking out. A short BLACK outfit splashed with RED with a gold buckle, bare legs with BLACK WRAPS round the shins and bare toes (no boots), standing with her feet apart.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A slight build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the near side on the image LEFT in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 7 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the pillory and the body are transparent.
No effects (no blood mist, no rings, no splashes in the air), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、刑枷、头发、衣服、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：叉开腿站着、黑铁刑枷套在脖子上、两只手腕锁在刑枷两端；头的大小照附图 6。
- 刑枷顶到脚底约 708 px（约 101 格）；脚底碰到深灰线，下面什么都没有。
- 白色短发（带粉红）、浅蓝色眼睛、黑铁刑枷（金色铆钉、尖角、红宝石）、黑色短衣和红色、光腿、小腿的黑绑带和脚趾都在；脸上各部分清楚。
- **每块 7 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/briar-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/briar_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/briar/hd/`，照 `tools/art/design_sona_hd.py`（按原图自己的格子读、每条线贴着最近的色边；调色板 64 色；原画的细节比格子还细时，用更细的格子读，几种 PPU 给用户选）读回；和金克丝、阿狸、现在的贝蕾亚按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把刑枷的两端算进“两脚中点”）。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：刑枷怎么套、手在哪、腿怎么站。
- 动作：她的 tag：idle 24、run 8、attack 6、skill 6、skill2 6、skill2_scream 4、ult 6、ult_fly 4、ult_land 5、hit 2、dead 8、idle_base 8、bp 48；`attack_fx1` 是烤进图里的特效条（7 帧），不是身体（`hero_reels.json`：待机 = skill2_scream 0–1 + skill2 2–4）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移。装游戏前先合进最新 main，版本号接着游戏里现装的往上加；附加包合集要带上还没合并的别的会话的分支（见记忆 game-dll-versions）。
