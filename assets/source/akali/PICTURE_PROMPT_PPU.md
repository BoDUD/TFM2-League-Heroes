# 阿卡丽：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 阿卡丽现在游戏里的造型是 1 倍的（附图 6）：马尾顶到脚底约 40 格，压低身子、两腿大大分开地站着，两只手各握一把**镰刀（kama）**。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，马尾顶到脚底约 **60 格**，和李青、锐雯、奇亚娜同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**深蓝色的头发**，前面有刘海，脸的右边垂下一缕；头顶扎起**高马尾**，马尾很粗，**向上、向后（画面左上方）甩出去**，上面有亮蓝色的高光；马尾上绑着**亮黄色的发带**，靠近头的地方和马尾中段各一处，交叉成 X 形。**脸**是浅肤色，一双**橙色的大眼睛**（带白色高光），朝画面右前方看；**青绿色的面罩**遮住鼻子以下和脖子。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**青绿色的无袖短上衣**，胸前有一条**亮黄色的斜饰边**（从领口斜到腰）；肩膀、手臂、**腰腹露在外面**（浅肤色）。
>   - 手：两只前臂都缠着**青绿色的护腕**，上面有亮黄色的带子。**近侧的手（画面左边）**放低在身体左侧、腰下的高度，握着一把镰刀，**刀身是细长的银白色刃，斜着朝左下方指向地面**；**远侧的手（画面右边）**在右侧胯旁，握着另一把镰刀，**弯钩形的银白色刀刃朝上、朝右弯起来**（像一个问号的弯）。
>   - 腰：**近侧的胯上（画面左边）挂着一个暗红色的腰包**，上面一个黄绿色的扣；一条**橙棕色的腰绳**横过腰，在右边垂下来；身前垂下一片**青绿色的布**，边上是黄色饰边，挂在两腿之间。
>   - 下身：**深蓝色的宽大灯笼裤**，两腿大大分开、膝盖微弯；裤脚在脚踝收紧，绑着**亮黄色的带子**；**深色的鞋**。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **两只脚都踩在附图 7 的深灰线上**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**马尾顶到脚底约 660 px（约 60 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），马尾顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、马尾和两把镰刀都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的眼睛、面罩的边各自成块，不要糊成一团；马尾的发丝分得清；两把镰刀的刃清楚。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间、镰刀和身体之间的空隙也是透明的。
> - 不画特效（烟雾、刀光等都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/akali-ppu/akali-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/akali-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/akali_ppu_done.zip`。

## 附图（在压缩包 `akali_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_akali_idle.png` | 英雄联盟里的阿卡丽待机，四分之三朝右（头放大到接近游戏精灵的比例） | 头发、面罩、衣服、镰刀的细节 |
| `refs/2_akali_head.png` | 头部特写 | 刘海、马尾和发带、眼睛、面罩 |
| `refs/3_akali_back.png` | 从身后看 | 马尾、腰包、裤子 |
| `refs/4_akali_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_akali_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、衣服、颜色 |
| `refs/6_akali_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 40 格高） | **要描的就是它**：姿势、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**马尾顶要碰到的线（浅灰）** |
| `style/8_style_leesin.png` | 本包的李青（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_qiyana.png` | 本包的奇亚娜（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`akali-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a ninja girl in a low, wide stance - legs far apart, knees a little bent, both feet on the ground - holding a KAMA (sickle) in each hand, shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same pose, the same costume and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, clothes and colours. Images 1-3 are 3D renders of the same character from the game (1 her idle - the hair, the mask, the clothes, the kamas; 2 her head close up - the bangs, the ponytail and its ties, the eyes, the mask; 3 from behind - the ponytail, the pouch, the trousers). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF HER PONYTAIL goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her ponytail is about 660 px (about 60 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, the ponytail and both kamas inside the picture; nothing at all below her soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): DARK BLUE HAIR with bangs over the brow and a lock down the right side of her face; a thick HIGH PONYTAIL swept UP AND BACK to the upper LEFT of the picture (behind her), with bright blue highlights, tied with BRIGHT YELLOW RIBBONS crossed in an X - one near her head, one halfway along the ponytail. A light-skinned face turned to the viewer's right, LARGE ORANGE EYES with white highlights, a TEAL MASK covering her nose, mouth and neck - the eyes and the mask's edge each a clear shape, never one muddy blob. A sleeveless TEAL CROP TOP with a BRIGHT YELLOW trim running diagonally down the front; bare shoulders, bare arms and a BARE MIDRIFF. TEAL WRIST WRAPS with yellow bands on both forearms. The NEAR hand (image left) held low by her left side below the waist, gripping a kama whose long thin SILVER-WHITE blade points DOWN-LEFT toward the ground; the FAR hand (image right) by her right hip, gripping a kama whose HOOKED silver-white blade curls UP and to the RIGHT (like the curve of a question mark). A DARK RED POUCH on her near hip (image left) with a yellow-green buckle; an ORANGE-BROWN ROPE BELT across her waist, its end hanging on the right; a TEAL CLOTH PANEL with yellow trim hanging down the front between her legs. WIDE BAGGY DARK BLUE TROUSERS, gathered at the ankles with BRIGHT YELLOW bands; dark shoes.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. An athletic, lean figure, as image 6.
THE VIEW: 3/4 view as image 6: turned to the viewer's right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her arms and body, between her legs and between the kamas and her body are transparent.
No effects (no smoke, no blade trails), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、比例、衣服、颜色和附图 6 一样**（细节照附图 1–3）：压低的大开步、近侧的镰刀朝左下、远侧的弯钩镰刀朝右上；头的大小照附图 6。
- 马尾顶到脚底约 660 px（约 60 格）；两只脚踩在深灰线上，脚底以下什么都没有。
- 深蓝头发和刘海、甩向左上的高马尾和两处黄色发带、橙色眼睛、青绿面罩、青绿短上衣和黄色斜饰边、露出的腰腹、青绿护腕、两把银白镰刀、暗红腰包、橙棕腰绳、青绿前摆、深蓝灯笼裤和黄色裤脚带都在；脸上各部分清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/akali-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/akali_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/akali/hd/`，照 `tools/art/design_syndra_hd.py`（原图自己的格子）读回；和李青、锐雯、现在的阿卡丽按游戏里的大小并排，给用户确认大小、脸、粗细。
- **白色的东西**：镰刀的刃是银白色。抠白底时被围住的白块只有四周是描边时才当背景（`casts_rengar_hd.figure`），读回后检查刀刃、眼睛的高光有没有被抠掉。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：动作包里写的每个部件（哪只手握哪把镰刀、马尾甩的方向、腰包在哪边）都要在旧帧上确认过位置。
- 动作：照狮子狗的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_rengar_actions.py`），读回到设计图上（`casts_rengar_hd.py`）；跑步检查两条腿是否轮流交换（逐帧写出哪只脚在前）。她的 tag：idle、run、attack、attack_p（被动强化普攻）、skill（Q）、skill2（E 掷出）、skill2_dash（E 冲刺）、ult、ult2、hit、dead。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、特效的出手点、头像截取点、选人卡偏移。
