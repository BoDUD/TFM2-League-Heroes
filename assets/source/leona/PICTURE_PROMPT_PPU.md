# 蕾欧娜：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 蕾欧娜现在游戏里的造型是 1 倍的（附图 6）：太阳冠的顶到脚底约 41 格。她**两脚分开站稳**，**橙红色的长发**上戴着**金色的太阳冠**；**金色的盔甲**，腰下**深红色的裙甲**；**近侧的手（画面左边）挎着一面圆形的金色太阳盾**，挡在身前；**远侧的手（画面右边）握着一把剑，剑斜着举向右上方**。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，冠顶到脚底约 **62 格**，和潘森、剑姬、锐雯同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、Q 版比例、盔甲、盾、剑、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节；**3D 模型的盾是深红色的长条鸢形盾，不要照它——盾照附图 6 画成圆形的金色太阳盾**）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的 Q 版头**（和附图 6 一样的比例），**橙红色的长发**，额前有刘海、两侧和背后披下来；头顶戴着**金色的太阳冠**（一圈尖尖的金色光芒）；**琥珀色的眼睛**，浅肤色，小小的嘴。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 身体：**金色的肩甲和胸甲**，**金色的护手**；腰下垂着**深红色的裙甲**（中间一条深红色的布），裙甲边上是金色的甲片。
>   - 近侧的手（画面左边）：**挎着一面圆形的金色太阳盾**，盾面上是太阳的花纹，**挡在身前、在画面左边**。
>   - 远侧的手（画面右边）：**握着一把剑**，**剑斜着举向右上方**：金色的剑柄和护手，**银白色的剑身**。
>   - 腿：**金色的护膝、护胫和金色的靴子**，**两脚分开站稳**。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **两只脚都踩在附图 7 的深灰线上**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**冠顶到脚底约 677 px（约 62 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），冠顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、整面盾和整把剑都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；太阳冠的尖、盾上的太阳花纹、剑柄和剑身都清楚。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（盾和剑也不要发光晕），也不要画黑色或彩色背景。两腿之间、手臂和身体之间、盾和身体之间、剑和身体之间的空隙也是透明的。
> - 不画特效（阳光、日蚀、光柱、光圈都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/leona-ppu/leona-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/leona-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/leona_ppu_done.zip`。

## 附图（在压缩包 `leona_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_leona_idle.png` | 英雄联盟里的蕾欧娜待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 头发、太阳冠、金甲、裙甲、盾、剑的细节 |
| `refs/2_leona_head.png` | 头部特写 | 头发、太阳冠、脸、眼睛 |
| `refs/3_leona_back.png` | 从身后看 | 长发、背后的金甲、盾的背面 |
| `refs/4_leona_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_leona_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、盔甲、盾、剑、颜色 |
| `refs/6_leona_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 41 格高） | **要描的就是它**：姿势、Q 版比例、盔甲、盾、剑、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**冠顶要碰到的线（浅灰）** |
| `style/8_style_pantheon.png` | 本包的潘森（8 倍，PPU 1.5；也拿盾） | **只看风格** |
| `style/9_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`leona-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a sun knight standing firmly with her feet apart, RED-ORANGE long hair under a GOLD SUN CROWN, GOLD armour and a CRIMSON skirt, a ROUND GOLD SUN SHIELD on her NEAR arm (image left) held before her, a SWORD in her FAR hand (image right) raised diagonally up to the right; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same armour, shield, sword and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, the armour, the shield, the sword and the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them; their shield is a tall crimson kite shield - do NOT copy it, her shield is image 6's ROUND GOLD one (1 her idle - the hair, the crown, the gold armour, the crimson skirt, the shield, the sword; 2 her head close up - the hair, the crown, the face, the eyes; 3 from behind - the long hair, the armour on her back, the back of the shield). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF HER CROWN goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her crown is about 677 px (about 62 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, the whole shield and the whole sword inside the picture; nothing at all below her soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG CHIBI HEAD as in image 6; LONG RED-ORANGE HAIR, a fringe over the brow, falling down her sides and back; a GOLD SUN CROWN of sharp golden rays on her head; AMBER EYES, fair skin, a small mouth - the eyes, the brows and the mouth each a clear shape, never one muddy blob. GOLD shoulder plates and breastplate, GOLD gauntlets; a CRIMSON skirt hanging from her waist (a crimson cloth down the middle) edged with gold plates. The NEAR arm (image left) carries a ROUND GOLD SUN SHIELD with a sun pattern on its face, held before her on the image left. The FAR hand (image right) holds a SWORD raised diagonally up to the right: a gold hilt and crossguard, a SILVER-WHITE blade. GOLD knee and shin guards and GOLD BOOTS, her feet apart, standing firmly. No glow around the shield or the sword.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A sturdy build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her legs, her arms and body, the shield and body and the sword and body are transparent.
No effects (no sunlight, no eclipse, no beams, no rings), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、盔甲、盾、剑、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：两脚分开站稳、近侧手挎圆盾挡在身前、远侧手握剑斜举向右上；头的大小照附图 6。
- 冠顶到脚底约 677 px（约 62 格）；两只脚踩在深灰线上，脚底以下什么都没有。
- **盾是圆形的金色太阳盾**（不是 3D 模型那种深红长盾）；橙红长发、金色太阳冠、琥珀色眼睛、金色肩甲胸甲和护手、深红裙甲、金色太阳盾、金柄银剑、金色护膝护胫和靴子都在；脸上各部分清楚，盾和剑没有光晕。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/leona-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/leona_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/leona/hd/`，照 `tools/art/design_kayle_hd.py`（按原图自己的格子读、每条线贴着最近的色边；调色板颜色不够时加到 64 色，别让浅色并掉）读回；和潘森、剑姬、现在的蕾欧娜按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（塔里克、凯尔的教训：别把盾的边或剑尖算进“两脚中点”）。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：盾在哪只手、剑在哪只手、剑尖朝哪。
- 动作：她的 tag：idle 16、run 8、attack 5、skill 7、skill2 6、e_dash 2、ult 7、hit 2、dead 8、idle_base 8、bp 41（`hero_reels.json`：待机 = skill2 0–1 + skill 1）。没有烤进动作的特效（`leona_fx_*` 是单独的特效条）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移。装游戏前先合进最新 main，版本号接着游戏里现装的往上加（现在是 league.dll 0.8.12 / 主包 0.259.4 之后）。
