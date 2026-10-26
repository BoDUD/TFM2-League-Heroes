# 李青（盲僧）：照现在的精灵按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 李青现在游戏里的造型是 1 倍的（附图 6）：辫子顶到脚底约 41 格，摆着武僧的架势——两腿分开半蹲，远侧（画面右边）的手掌向前立起，近侧（画面左边）的手握拳收在身侧。这次**照着它画密一点**：按 **PPU 2.2**，**每个游戏像素画成 2.2 格**，辫子顶到脚底约 **90 格**，和金克丝、德莱文、拉克丝同样的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 5 和 1–3）：姿势、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势。只是格子密了，把 1 倍画不下的细节画出来：
>   - **体格要壮**：武僧的结实身材——宽肩、粗壮的手臂和大腿、结实的胸肌和腹肌，**不要画成细长的身材**（另一位英雄这样重画后显得太细，用户不满意）。
>   - 头：**剃短的头顶上一条黑色的长辫子往上翘、向后卷**（红色和金色的发箍扎着）；**眼睛上蒙着红色的布条**，侧面有一颗**金边的蓝宝石**，布条的两条长尾巴往后飘；看不到眼睛，但**鼻子、嘴、下巴画清楚**，表情沉稳。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**赤裸的肌肉上身**（身上有淡淡的伤痕）；前臂和手缠着**红白相间的绷带**。
>   - 下身：腰间**白色的布腰带和金色的腰扣**，前面垂下一截红布；**深蓝色的宽松长裤**；小腿缠**红白相间的绑腿**；**深色的布鞋**。
> - **朝向**：和附图 6 一样，四分之三侧身，**脸和胸口朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用竖的 1024×1536**：**辫子顶到脚底约 992 px（约 90 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），辫子顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人和飘起的布条都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的鼻子、嘴、下巴和蒙眼布的边各自成块，不要糊成一团。** 附图 8–10 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间的空隙也是透明的。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/leesin-ppu/leesin-A.png`（1024×1536，**真透明背景**）；原始生成图原样放进 `outputs/leesin-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/leesin_ppu_done.zip`。

## 附图（在压缩包 `leesin_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_leesin_idle.png` | 英雄联盟里的李青待机，四分之三朝右（头放大到接近游戏精灵的比例） | 辫子、衣服、绷带、腰带的细节 |
| `refs/2_leesin_head.png` | 头部特写 | 辫子、蒙眼布和宝石、脸 |
| `refs/3_leesin_back.png` | 从身后看 | 辫子、布条尾巴、腰带 |
| `refs/4_leesin_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_leesin_first_design.png` | 他原来的设计图（1 倍） | 头、衣服、颜色 |
| `refs/6_leesin_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 41 格高） | **要描的就是它**：姿势、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**辫子顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍，PPU 2.2） | **只看风格** |
| `style/9_style_draven.png` | 本包的德莱文（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_lux.png` | 本包的拉克丝（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`leesin-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a blind martial-arts monk standing in a wide fighting guard - legs apart and bent, the far hand (image right) raised forward as an open palm, the near hand (image left) a fist held back at his side - shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same stance, the same costume and colours - only at a much finer pixel density, with the details the small sprite could not hold. Image 5 is his earlier design at game size: the head, clothes and colours. Images 1-3 are 3D renders of the same character from the game (1 his idle - the braid, the clothes, the hand wraps, the sash; 2 his head close up - the braid, the blindfold and its gem, the face; 3 from behind). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is the ground where his soles stand, the light grey line is where the TOP OF HIS BRAID goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1536 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his braid is about 992 px (about 90 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure and the flying blindfold tails inside the picture; both soles on one ground line; nothing at all below his soles.
THE BUILD: STURDY and MUSCULAR - a martial artist's broad shoulders, thick arms and thighs, a solid chest and abdomen; NOT a slim, long-limbed figure. The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE CHARACTER (as image 6, detailed after images 5 and 1-3): a shaved head with a long BLACK BRAID rising from the crown and curling back, bound with red and gold bands; a RED BLINDFOLD over his eyes with a GOLD-RIMMED BLUE GEM at its side, its two long tails flowing back; no eyes visible, but the nose, the mouth and the jaw each a clear shape, a calm face - never one muddy blob. A BARE MUSCULAR TORSO with faint scars; RED-AND-WHITE BANDAGES wrapped round the forearms and hands. a WHITE cloth belt with a GOLD BUCKLE, a red cloth hanging in front; loose DARK NAVY-BLUE TROUSERS; RED-AND-WHITE wraps round the shins; dark cloth shoes.
THE VIEW: 3/4 view FACING RIGHT as image 6: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between his arms and body and between his legs are transparent.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1536、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势、比例、衣服、颜色和附图 6 一样**（细节照附图 5 和 1–3），只是更密、更细；**体格壮实**，头的大小照附图 6。
- 辫子顶到脚底约 992 px（约 90 格）；两只脚底在同一条线上，脚底以下什么都没有。
- 黑色长辫子、红色蒙眼布（金边蓝宝石）和飘起的布尾、红白绷带、白腰带金腰扣和红布、深蓝宽裤、红白绑腿、深色布鞋都在；鼻子、嘴、下巴清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/leesin-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/leesin_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/leesin/hd/`，照 `tools/art/design_draven_hd.py`（格子正好时逐格读回）或 `design_samira_hd.py`（原图自己的格子）读回；和德莱文、金克丝、现在的李青按游戏里的大小并排（**尺寸表 SIZES 要算进去**），给用户确认大小、脸、粗细。
- 动作：照德莱文的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_draven_actions.py`），再读回到设计图上；**动作包里写明头和设计图一样大**，交回后逐帧把设计图的头轮廓叠上去量；**跑步查左右脚轮换和起伏**；他的动作多（Q 两段 q_throw / q2、R 回旋踢、待机 idle_base 8 帧），注意每个 tag 的帧数。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂剪影、待机和选人卡轮播、Q 的飞波出手点和特效锚点、头像截取点、选人卡偏移（他现在的待机顶到 -28 以上要设 banpick_center）。
