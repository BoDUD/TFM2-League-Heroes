# 崔丝塔娜：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 崔丝塔娜现在游戏里的造型是 1 倍的（附图 6）：护目镜顶到脚底约 34 格，是个小个子约德尔人，两腿分开站着，**双手在腰的高度横端着她的大炮，炮口朝右**。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，护目镜顶到脚底约 **51 格**，和纳尔、薇古丝、锐雯同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**很大的约德尔脑袋**；头顶戴着一副**护目镜**（**黄铜色和红色的镜框**、**浅蓝色的镜片**，两个圆筒朝上）；**白色蓬松的头发**，刘海盖着额头，**脑后和耳朵下面也有白发垂下来**（画面左边耳朵下面那团浅色就是头发）；**两只很大的尖耳朵**往左右两边伸出去，**外面淡紫色、里面粉红色**；**淡紫色的皮肤**，一双**大大的琥珀黄色眼睛**，小小的深红色嘴。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 身体：**棕色的皮背心 / 皮甲**，**橄榄绿色的上衣和短裤**，**红色的绑带**，**棕色的腰带和小皮包**；**棕色的无指皮手套**。
>   - 大炮：**很长的炮管横在她身前、腰的高度，炮口朝右**——炮身是**黄铜色和木头的棕色**，有金属箍；**炮口是很大的喇叭形，蓝灰色的钢**；**炮尾在画面左边，也是蓝灰色的钢**。两只手都握在炮身上。
>   - 腿：**淡紫色的光腿**，有棕色的绑腿；**光着的约德尔脚**（淡紫色），两腿分开站着。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **两只脚都踩在附图 7 的深灰线上**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**护目镜顶到脚底约 561 px（约 51 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），护目镜顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、两只耳朵和整门大炮都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**眼睛、嘴、护目镜的镜片各自成块，不要糊成一团；耳朵的粉色内侧清楚；炮管的金属箍和炮口清楚。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、炮管和身体之间的空隙也是透明的。
> - 不画特效（炮弹、火光、烟雾等都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/tristana-ppu/tristana-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/tristana-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/tristana_ppu_done.zip`。

## 附图（在压缩包 `tristana_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_tristana_idle.png` | 英雄联盟里的崔丝塔娜待机，四分之三朝右 | 护目镜、头发、耳朵、衣服、大炮的细节 |
| `refs/2_tristana_head.png` | 头部特写 | 护目镜、头发、耳朵、眼睛 |
| `refs/3_tristana_back.png` | 从身后看 | 头发、背心、大炮 |
| `refs/4_tristana_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_tristana_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、衣服、颜色 |
| `refs/6_tristana_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 34 格高） | **要描的就是它**：姿势、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**护目镜顶要碰到的线（浅灰）** |
| `style/8_style_gnar.png` | 本包的纳尔（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_vex.png` | 本包的薇古丝（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`tristana-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a yordle gunner - a small creature with a big head and huge pointed ears - standing with her legs apart, holding a big CANNON level at her hip with both hands, its muzzle pointing RIGHT; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same pose, the same costume and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, clothes and colours. Images 1-3 are 3D renders of the same character from the game (1 her idle - the goggles, the hair, the ears, the clothes, the cannon; 2 her head close up - the goggles, the hair, the ears, the eyes; 3 from behind - the hair, the vest, the cannon). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF HER GOGGLES goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her goggles is about 561 px (about 51 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, both ears and the whole cannon inside the picture; nothing at all below her soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG yordle HEAD; GOGGLES pushed up on top of it (BRASS AND RED frames, LIGHT BLUE lenses, two short tubes pointing up); FLUFFY WHITE HAIR with bangs over the brow, more white hair hanging behind the ears (the pale shape under her ear on the image left is her hair); two HUGE POINTED EARS sticking out to the left and right, LAVENDER outside and PINK inside; LAVENDER skin, LARGE AMBER-YELLOW EYES, a small dark red mouth - the eyes, the mouth and the lenses each a clear shape, never one muddy blob. A BROWN LEATHER VEST, an OLIVE-GREEN top and shorts, RED wraps, a BROWN BELT with small pouches, BROWN FINGERLESS GLOVES. THE CANNON: a long barrel held LEVEL across in front of her at hip height, the MUZZLE TO THE RIGHT - a BRASS and WOOD-BROWN body with metal bands, a big FLARED BLUE-GREY STEEL MUZZLE on the right end, a blue-grey steel butt on the left end; both hands on it. Bare LAVENDER legs with brown leg wraps and BARE yordle FEET, legs apart.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A small yordle build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her legs, her arms and body and the cannon and her body are transparent.
No effects (no cannonball, no muzzle flash, no smoke), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、比例、衣服、颜色和附图 6 一样**（细节照附图 1–3）：两腿分开站着、双手在腰的高度横端大炮、炮口朝右；头的大小照附图 6。
- 护目镜顶到脚底约 561 px（约 51 格）；两只脚踩在深灰线上，脚底以下什么都没有。
- 护目镜（黄铜红框、浅蓝镜片）、白色蓬发、两只大尖耳朵（外淡紫内粉红）、琥珀黄大眼睛、淡紫色皮肤、棕皮背心、橄榄绿衣裤、红绑带、棕腰带和皮包、棕色无指手套、大炮（黄铜木色炮身、蓝灰喇叭炮口和炮尾）、淡紫光腿和光脚都在；脸上各部分清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/tristana-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/tristana_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/tristana/hd/`，照 `tools/art/design_sivir_hd.py`（原图自己的格子：Codex 的格子均匀时用一张均匀网格逐格读）读回；和纳尔、薇古丝、现在的崔丝塔娜按游戏里的大小并排，给用户确认大小、脸、粗细。
- **白色的东西**：她的头发是白色。抠白底时被围住的白块只有四周是描边时才当背景（`casts_rengar_hd.figure`），读回后检查头发有没有被抠掉。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：动作包里写的每个部件（大炮怎么端、炮口方向、耳朵、头发）都要在旧帧上确认过位置。
- 动作：照希维尔的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_sivir_actions.py`），读回到设计图上（`casts_sivir_hd.py`：按头的大小找缩放）；跑步一开始就逐帧写清腿怎么摆。她的 tag：idle、run、attack、skill、skill2、ult、hit、dead；`assets/source/native/tristana_bake.json` 把普攻、技能、大招的炮口特效直接烤进这些动作帧（不是副本）——身体帧从 native 的格子取。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、炮口的出手点、头像截取点、选人卡偏移。
