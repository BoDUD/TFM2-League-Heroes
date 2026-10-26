# 薇恩：照现在的精灵按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 薇恩现在游戏里的造型是 1 倍的（附图 6）：从顶上（马尾和背后的大弩）到脚底约 40 格，站着，脸朝右前方，红披风往身后（画面左边）飘到地上，背后的大弩从肩后（画面左边）高过头顶。这次**照着它画密一点**：按 **PPU 2.2**，**每个游戏像素画成 2.2 格**，顶到脚底约 **88 格**，和金克丝、德莱文、拉克丝同样的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 5 和 1–3）：姿势、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势，也**不要换成附图 1–3 的蓝色紧身衣和金色弩**（那些只看形状和结构）。只是格子密了，把 1 倍画不下的细节画出来：
>   - **体格不要细**：矫健的女猎手，四肢有分量、肩膀和大腿结实，**不要画成细长的竹竿身材**（之前别的英雄这样重画后显得太细，用户不满意）。
>   - 头：**黑紫色的头发**，头顶扎**高马尾**往后翘；**红色的墨镜**（两片镜片在同一行，中间深色的镜框，镜片只用这种亮红）；苍白的皮肤；**深红的嘴唇**在镜片下面，下巴干净，不要有别的深色格。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**红色的高立领**；**黑蓝色（深蓝灰）的紧身衣**，上面有**银色的护甲**（肩甲、胸前）；**棕色的皮带**交叉绑着。
>   - 近侧（画面左边）的前臂上是**银色的腕弩**（带一颗红宝石），垂在身体左后方，是一个清楚的形状；**背后的大弩**从肩后（画面左边）露出、高过头顶，银色的弩臂、棕色的弩身。
>   - 下身：黑蓝色的紧身裤、**深色的高跟长靴**；**红色的长披风**从肩膀往身后（画面左边）飘，下摆是撕破的尖角，落到脚边。
> - **朝向**：和附图 6 一样，四分之三侧身，**脸和胸口朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用竖的 1024×1536**：**顶到脚底约 968 px（约 88 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），最高处碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、弩和披风都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的墨镜、嘴、下巴各自成块，不要糊成一团。** 附图 8–10 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间、弩和身体之间的空隙也是透明的。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下），披风的尖角也在脚底线以上。
>
> - 交付：`outputs/vayne-ppu/vayne-A.png`（1024×1536，**真透明背景**）；原始生成图原样放进 `outputs/vayne-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/vayne_ppu_done.zip`。

## 附图（在压缩包 `vayne_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_vayne_idle.png` | 英雄联盟里的薇恩待机，四分之三朝右（头放大到接近游戏精灵的比例） | 马尾、墨镜、披风、两把弩的**形状和结构**（颜色照附图 6） |
| `refs/2_vayne_head.png` | 头部特写 | 马尾、墨镜、脸 |
| `refs/3_vayne_back.png` | 从身后看 | 马尾、背后的大弩、披风 |
| `refs/4_vayne_splash.png` | 官方加载画面 | 看气质 |
| `refs/5_vayne_first_design.png` | 她原来的设计图（1 倍；和附图 6 是同一张，她的精灵就是照它做的） | 头、衣服、颜色 |
| `refs/6_vayne_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 40 格高） | **要描的就是它**：姿势、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**最高处要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍，PPU 2.2） | **只看风格** |
| `style/9_style_draven.png` | 本包的德莱文（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_lux.png` | 本包的拉克丝（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`vayne-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a night huntress standing - a red cape flowing behind her (image left) down to the ground, a big crossbow over her back rising above her head on the image left, a silver wrist crossbow on her near forearm - shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same stance, the same costume and the same COLOURS - only at a much finer pixel density, with the details the small sprite could not hold. Image 5 is her earlier design at game size (the same picture as image 6): the head, clothes and colours. Images 1-3 are 3D renders of the same character from the game (1 her idle, 2 her head close up, 3 from behind): use them ONLY for the shapes and the construction of the ponytail, the glasses, the cape and the two crossbows - NOT their colours (keep image 6's dark navy suit with silver armour and silver crossbows, not the renders' blue suit and gold). Image 4 is the official illustration: the mood. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is the ground where her soles stand, the light grey line is where her HIGHEST POINT goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1536 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). Her highest point is about 968 px (about 88 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, both crossbows and the cape inside the picture; both soles on one ground line; nothing at all below her soles (the cape's points end above the ground line).
THE BUILD: an athletic huntress - limbs with real weight, firm shoulders and thighs; NOT a thin, stick-limbed figure. The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE CHARACTER (as image 6, detailed after images 5 and 1-3): BLACK-PURPLE hair tied in a HIGH PONYTAIL sweeping back from the crown; RED SUNGLASSES - two red lenses on one row joined by a dark frame, that bright red used ONLY on the lenses; pale skin; DEEP RED LIPS below the glasses, a clean chin with no other dark squares; the glasses, the mouth and the chin each a clear shape - never one muddy blob. A RED HIGH COLLAR; a DARK NAVY-SLATE bodysuit with SILVER ARMOUR on the shoulders and chest; BROWN LEATHER STRAPS crossing it. A SILVER WRIST CROSSBOW with a red gem on the near forearm, hanging back at her side, one clear shape; the BIG CROSSBOW over her back showing behind the near shoulder (image left) and rising above her head, silver limbs at least 2 squares thick and a brown stock. Dark navy leggings and DARK HIGH-HEELED BOOTS. A long RED CAPE from her shoulders flowing back (image left) in 3-4 reds, its hem torn into points, reaching down beside her feet.
THE VIEW: 3/4 view FACING RIGHT as image 6: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), the crossbows, arms, hair and cape separated by outline; no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her arms and body, between her legs and between the crossbows and her body are transparent.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1536、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势、比例、衣服、颜色和附图 6 一样**（细节照附图 5 和 1–3 的形状，颜色不照 1–3）；**体格不细**，头的大小照附图 6。
- 最高处到脚底约 968 px（约 88 格）；两只脚底在同一条线上，脚底以下什么都没有。
- 黑紫高马尾、红墨镜（亮红只在镜片上）、深红嘴唇、红立领、深蓝灰紧身衣和银甲、棕色皮带、腕弩（红宝石）、背后的大弩、深色高跟长靴、红披风的撕破下摆都在；墨镜、嘴、下巴清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/vayne-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/vayne_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/vayne/hd/`，照 `tools/art/design_draven_hd.py`（格子正好时逐格读回）或 `design_leesin_hd.py`（原图自己的格子）读回；和德莱文、金克丝、现在的薇恩按游戏里的大小并排（**尺寸表 SIZES 要算进去**），给用户确认大小、脸、粗细；**密度先出对照表**（李青最后用了 1.5）。
- 动作：照李青的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_leesin_actions.py`），再读回到设计图上（`casts_leesin_hd.py`：白底、按头定缩放）；**动作包里写明头和设计图一样大、腕弩在同一只手**，交回后逐帧把设计图的头轮廓叠上去量；**跑步查左右脚轮换和起伏**；她的 tag：attack / attack_q（强化箭）/ skill（翻滚）/ skill_back / skill2（恶魔审判）/ ult，idle_base 8 帧，注意每个 tag 的帧数。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂剪影、待机和选人卡轮播、弩箭的出手点（`vayne_fx_anchors.json`）、头像截取点、选人卡偏移（她现在的待机顶到 -28 以上要设 banpick_center）。
