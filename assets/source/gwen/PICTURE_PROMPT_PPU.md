# 格温：照现在的精灵按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 格温现在游戏里的造型是 1 倍的（附图 7）：头顶到脚底 38 格，扛在肩上的剪刀尖再高出 12 格，整张 50 格高。用户喜欢现在的造型，这次**照着它画密一点**：按 **PPU 2.2**，**每个游戏像素画成 2.2 格**，头顶到脚底约 **84 格**，剪刀尖到脚底约 **110 格**。和安妮、阿狸、拉克丝一样的密度（附图 9–11）。
> - **照附图 7 描**：姿势、剪刀扛在肩上的角度和位置、两只手的位置、身体比例（Q 版大头）、衣服、颜色**全部照现在的精灵**，不要换姿势、不要改比例；只是格子密了，把 1 倍画不下的细节画出来：
>   - 头发：**亮蓝色**，头顶一根呆毛，刘海；两边是**大的螺旋卷**（照附图 7 的位置和大小），卷上要有明暗看得出一圈一圈；头两侧**深紫色的大蝴蝶结**，结上有金色小坠。
>   - 衣服：**紫色的蓬蓬洋装**，胸前金色十字/菱形饰扣，裙子**白色和紫色分层**，裙摆的金色菱形饰片；紫色手套。
>   - 腿：**紫色菱格长袜**；**白色的高跟短靴**，金色饰片（照附图 7 的位置）。
>   - **剪刀**：照附图 7 扛在肩上——**淡蓝色的长刀刃斜着朝左上方**伸出去，刀刃带白色高光；**两个心形的剪刀环在画面右边**她的身前，环中间是**透明的心形孔**（能看到背景）；刀尖别出画面。
> - **眼睛改成英雄联盟的格温那样**（附图 2、6）：**大大的、圆圆的亮蓝色眼睛**，有白色高光，长睫毛，眼神甜、带一点俏皮的微笑；两只眼睛一样高、一样大、都看得见（不要被刘海挡住）。**不要**现在那种半闭着的粗黑眼皮和挑眉；不画眉毛。小小的粉色嘴，淡淡的腮红。
> - **朝向**：和附图 7 一样，四分之三侧身，**脸和胸口朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用竖的 1024×1536**：**头顶到脚底约 925 px（约 84 格），剪刀尖到脚底约 1210 px（约 110 格）**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），剪刀尖碰到附图 8 的浅灰线（附图 8 只看大小和位置）。整个人和整把剪刀都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。附图 9–11 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。剪刀环中间的心形孔也是透明的。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/gwen-ppu/gwen-A.png`（1024×1536，**真透明背景**）；原始生成图原样放进 `outputs/gwen-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/gwen_ppu_done.zip`。

## 附图（在压缩包 `gwen_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_gwen_carry.png` | 英雄联盟里的格温跑步时扛剪刀的姿势，四分之三朝右（头放大到接近游戏精灵的比例） | 剪刀扛在肩上的样子 |
| `refs/2_gwen_head.png` | 头部特写 | **眼睛**、脸、发型 |
| `refs/3_gwen_idle.png` | 英雄联盟里的待机 | 衣服、裙子、靴子的细节 |
| `refs/4_gwen_back.png` | 从身后看 | 蝴蝶结、螺旋卷 |
| `refs/5_gwen_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_gwen_codex_picture.png` | 之前画过的一张格温像素原画 | **眼睛和脸的画法**（姿势不照它，它的剪刀是拿在手里的） |
| `refs/7_gwen_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，50 格高） | **要描的就是它**：姿势、剪刀、比例、衣服、颜色 |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**剪刀尖要碰到的线（浅灰）** |
| `style/9_style_annie.png` | 本包的安妮（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_ahri.png` | 本包的阿狸（8 倍，PPU 2.2） | **只看风格** |
| `style/11_style_lux.png` | 本包的拉克丝（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`gwen-A.png`

附图 1–11，顺序同上表。

```text
Eleven attached images. Image 7 is THE picture to trace: a small pixel-art game sprite of a doll-like girl carrying giant scissors over her shoulder, shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions (a chibi, the big head), the same scissors over her shoulder at the same angle, the same hands, the same costume and colours - only at a much finer pixel density, with the details the small sprite could not hold. Images 1-4 are 3D renders of the same character from the game (1 her run's carry of the scissors - the hold; 2 her head close up - HER EYES; 3 her idle - the dress, skirt and boots; 4 from behind - the bows and ringlets). Image 5 is the official illustration: the mood and the colours. Image 6 is an earlier pixel picture of her: copy how its FACE and EYES are drawn, not its pose. Image 8 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is the ground where her soles stand, the light grey line is where the TIP OF THE SCISSORS' BLADE goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1536 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). She is about 925 px (about 84 squares) from the top of her head to her soles and the scissors' tip is about 1210 px (about 110 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure and the whole scissors inside the picture; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (as image 7, detailed after images 1-4): bright BLUE hair with an ahoge and bangs, BIG DRILL RINGLETS on both sides (where image 7 has them), each ringlet shaded so its coils read; big DARK PURPLE BOWS on both sides of her head with small gold charms. A PURPLE puffy dress with a gold cross / diamond brooch on the chest, the skirt layered WHITE AND PURPLE with gold diamond studs along the hem; purple gloves. PURPLE ARGYLE stockings; WHITE high-heeled ankle boots with gold studs.
THE SCISSORS (as image 7): carried over her shoulder - the long PALE BLUE BLADE slanting up to the upper LEFT with white highlights; the two HEART-SHAPED FINGER LOOPS on the image right in front of her, each with a see-through heart-shaped hole (transparent); the tip inside the picture.
HER EYES (changed - as League's Gwen, images 2 and 6): BIG ROUND BRIGHT BLUE EYES with white highlights and long lashes, a sweet look with a playful little smile; both eyes at the same height, the same size, both visible (not hidden by the bangs). NOT the half-closed heavy black lids of image 7; no eyebrows. A small pink mouth, a soft blush.
THE VIEW: 3/4 view FACING RIGHT as image 7: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1536、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；剪刀环的心形孔透明。
- **姿势、剪刀、比例、衣服、颜色和附图 7 一样**，只是更密、更细。
- 头顶到脚底约 925 px（约 84 格），剪刀尖到脚底约 1210 px；两只脚底在同一条线上，脚底以下什么都没有。
- **眼睛**：大大的圆眼睛、亮蓝色、有高光和长睫毛，两只一样高一样大，都看得见；没有粗黑眼皮、没有眉毛。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/gwen-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/gwen_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/gwen/hd/`，照 `tools/art/design_annie_hd.py` 按原图自己的格子读回；和安妮、阿狸、拉克丝、现在的格温按游戏里的大小并排，给用户确认大小、眼睛。
- 动作：照安妮的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_annie_actions.py` 的做法），再由 `casts_*_hd.py` 修到设计图上；剪刀环的透明心形孔每帧都要保留（旧版 `clean_gwen.py` 的标记）。
- 查塞拉斯、佛耶戈 / 妮蔻灵魂表、待机和选人卡轮播、普攻 / Q 剪刀特效的锚点（`gwen_bake.json`）、头像截取点、选人卡偏移等适配。
