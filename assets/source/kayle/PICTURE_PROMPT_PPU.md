# 凯尔：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 凯尔现在游戏里的造型是 1 倍的（附图 6）：翅膀尖到剑尖约 49 格。她**悬浮在空中**，脚尖朝下、没有踩地；**大大的 Q 版头**，白色短发；头后两边各竖起一只**淡蓝到淡紫的翅膀**；**金色的盔甲**套在浅灰绿的紧身衣外面；**远侧的手（画面右边）握着青色火焰剑，剑尖斜着朝右下**，是整个人最低的地方；近侧的手臂（画面左边）戴着金色护臂垂在身旁。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，翅膀尖到剑尖约 **74 格**，和莫甘娜、剑姬、锐雯同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、Q 版比例、翅膀、盔甲、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**很大的 Q 版头**（和附图 6 一样占身体的一大半），**白色到浅银灰的短发**，齐刘海、两侧垂到下巴；**琥珀色的大眼睛**，浅肤色，小小的嘴。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 翅膀：**头后两边各一只竖起的翅膀**，羽片尖尖的，**上面淡蓝、带冰蓝的亮边，下面渐变成淡紫**；画面左边那只大一些、紫色多一些。
>   - 身体：**金色的护颈和胸甲**，**金色的肩甲**，金色的腰带；里面是**浅灰绿色的紧身衣**（手臂和腿上露出来）。
>   - 近侧的手（画面左边）：**金色的护臂**，手垂在身旁。
>   - 远侧的手（画面右边）：金色护臂，**握着一把青色火焰剑**：**金色的剑柄**，**青绿到青白的剑身**，剑身边上一圈小火苗似的锯齿；**剑尖斜着朝右下**，在全身最低的地方。
>   - 腿：浅灰绿的紧身裤，**金色的护膝、护胫和金色的靴子**，**脚尖朝下**，两腿稍微一前一后，悬在空中。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **最低的一点（剑尖）碰到附图 7 的深灰线**（她是悬浮的，脚不踩地，这条线只用来定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**翅膀尖到剑尖约 809 px（约 74 格）**，剑尖在离画布底边约 64 px 的地方（附图 7 的深灰线），翅膀尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、两只翅膀和整把剑都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；翅膀的羽片、金甲的边、剑柄和剑身都清楚。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（剑和翅膀也不要发光晕），也不要画黑色或彩色背景。两腿之间、手臂和身体之间、翅膀和头之间、剑和腿之间的空隙也是透明的。
> - 不画特效（剑上的火焰只画剑身边缘的锯齿，不要飘出去的火光、光圈、光柱），不画地面、影子；**深灰线以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/kayle-ppu/kayle-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/kayle-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/kayle_ppu_done.zip`。

## 附图（在压缩包 `kayle_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_kayle_idle.png` | 英雄联盟里的凯尔待机（满级的样子），四分之三朝右（写实比例，**姿势和比例不要照它**） | 头发、翅膀、金甲、紧身衣、剑的细节 |
| `refs/2_kayle_head.png` | 头部特写 | 头发、脸、眼睛、护颈、翅膀根部 |
| `refs/3_kayle_back.png` | 从身后看 | 翅膀、头发、背后的金甲 |
| `refs/4_kayle_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_kayle_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、翅膀、盔甲、颜色 |
| `refs/6_kayle_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 49 格高） | **要描的就是它**：姿势、Q 版比例、翅膀、盔甲、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、剑尖的线（深灰）、**翅膀尖要碰到的线（浅灰）** |
| `style/8_style_morgana.png` | 本包的莫甘娜（8 倍，PPU 1.5；也有翅膀） | **只看风格** |
| `style/9_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`kayle-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a winged angel knight HOVERING in the air, toes pointing down, a BIG chibi head with short white hair, a pale blue-to-lilac WING rising behind each side of her head, GOLD armour over a pale grey-green bodysuit, her FAR hand (image right) holding a cyan FLAME SWORD pointing down to the right (its tip is her lowest point), her NEAR arm (image left) in a gold bracer hanging at her side; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same hovering pose, the same wings, armour and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, the wings, the armour and the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 her idle - the hair, the wings, the gold armour, the bodysuit, the sword; 2 her head close up - the hair, the face, the eyes, the gorget, the wing roots; 3 from behind - the wings, the hair, the armour on her back). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she floats; the dark grey line is where the SWORD'S TIP (her lowest point) goes, the light grey line is where the TOPS OF HER WINGS go. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The wing tops are about 809 px (about 74 squares) above the sword's tip, the tip about 64 px above the bottom edge; the whole figure, both wings and the whole sword inside the picture; nothing at all below the sword's tip. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG CHIBI HEAD as in image 6; SHORT WHITE TO PALE SILVER HAIR, a straight fringe, the sides falling to her chin; BIG AMBER EYES, fair skin, a small mouth - the eyes, the brows and the mouth each a clear shape, never one muddy blob. Behind each side of her head a tall pointed WING of sharp feathers, PALE BLUE above with icy light edges, shading to LILAC below; the one on the image left bigger and more lilac. A GOLD gorget and breastplate, GOLD shoulder plates, a gold belt, over a PALE GREY-GREEN BODYSUIT that shows on her arms and legs. The NEAR arm (image left) in a GOLD BRACER hangs at her side. The FAR hand (image right), gold-bracered, holds the FLAME SWORD: a GOLD HILT and a CYAN-TO-WHITE TEAL BLADE with small flame-like serrations along its edges, pointing down to the right, its tip her lowest point. Grey-green leggings, GOLD knee and shin guards and GOLD BOOTS, TOES POINTING DOWN, one leg a little ahead of the other, floating. No glow around the sword or the wings.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A slight, airy build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her legs, her arms and body, her wings and head and the sword and her legs are transparent.
No effects (no fire flying off the sword, no rings, no beams of light), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、翅膀、盔甲、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：悬浮、脚尖朝下、远侧的手握剑斜朝右下、近侧戴金护臂的手垂着；头的大小照附图 6。
- 翅膀尖到剑尖约 809 px（约 74 格）；剑尖碰到深灰线，深灰线以下什么都没有。
- 白色短发、琥珀色眼睛、两只淡蓝到淡紫的翅膀、金色护颈胸甲和肩甲、浅灰绿紧身衣、金色护臂、金柄青色火焰剑、金色护膝护胫和靴子都在；脸上各部分清楚，剑和翅膀没有光晕。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/kayle-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/kayle_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/kayle/hd/`，照 `tools/art/design_taric_hd.py`（按原图自己的格子读、每条线贴着最近的色边）读回；和莫甘娜、剑姬、现在的凯尔按游戏里的大小并排，给用户确认大小、脸、粗细。
- **浅色的东西**：头发、翅膀的亮边、剑身接近白色。抠白底时被围住的白块只有四周是描边时才当背景（`casts_rengar_hd.figure`），读回后检查头发、翅膀和剑有没有被抠掉。
- **她悬浮**：旧精灵最低的是剑尖，脚尖比它高一格；帧的中心在旧 idle 里（31 × 79 的帧，人在上面 49 行）。量 OLD_CENTRE 和高度时按脚和剑尖分开量。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：剑在哪只手、剑尖朝哪、翅膀几只、近侧护臂。
- 动作：她的 tag：idle 6、run 16、attack 6（远程）、attack_melee 6（近战）、skill 6、skill2 6、ult 8（飞上高空，帧很高）、hit 2、dead 7；**没有 idle_base 和 bp**（`hero_reels.json`：待机 = skill2 第 0 帧 + skill 第 5 帧）。没有烤进动作的特效（`kayle_fx_*` 是单独的特效条）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、`league_kayle` 附加包（升华）、待机和选人卡轮播、头像截取点、选人卡偏移。
