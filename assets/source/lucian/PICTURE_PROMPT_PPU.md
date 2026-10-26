# 卢锡安：按英雄联盟的样子、照现在精灵的姿势，PPU 2.2 重画设计图（给 Codex 的提示词）

> 卢锡安现在游戏里的精灵（附图 6，1 倍）是旧设计：米白配金的外套，**和英雄联盟里的他不太像**。用户要求：**「模型要和英雄联盟像一点」**。这次：
> - **样子照英雄联盟**（附图 1–5；附图 4 是英雄联盟原比例，看衣服最准）：衣服、颜色、发型、两把枪都照英雄联盟画，不照附图 6 的颜色。
> - **姿势和 Q 版比例照附图 6**：近侧（画面左边）的手把枪竖着举在肩旁、枪口朝上；远侧（画面右边）的手把枪平端向前、枪口朝右；两腿分开站稳，长衣摆往后垂到小腿。**头是 Q 版大头**（头顶到下巴约占身体的三成，和附图 6 一样），不要画成附图 4 那样的真人比例。以后每个动作都按这张图画，所以**姿势不能换**。
> - **密度**：按 **PPU 2.2**，**每个游戏像素画成 2.2 格**，和金克丝、德莱文、薇恩一样（附图 8–10）。
>
> **英雄联盟里的卢锡安**（照附图 1–5 画）：
> - **头**：深棕色皮肤；短发，两侧剃短，头顶的头发往后梳成几条贴头皮的辫子；**绿色的眼睛**，眉头紧锁、神情坚毅；下巴有棱角。**头的大小就是以后每个动作都要保持的大小。**
> - **上身**：**银白色的长外套**，肩上是**带金色饰边的银甲护肩**，高领；外套里面是**黑色带银边的胸甲**；腰间棕色腰带和金色扣。
> - **下身**：**黑色长裤**，**黑色高靴**（膝盖和小腿有银色护甲）；外套后摆分成**长长的白色衣摆**，里面是淡紫色的衬里（附图 3）。
> - **两把圣物手枪**（附图 1、3）：方方正正的大手枪，银白色和古铜色的枪身，枪身上有**发青蓝色光的符文**。两只手都戴**深棕色的手套**。
> - **体格不要细**：Q 版的身体，四肢有分量。
>
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用横的 1536×1024**：从最高处（竖着举的枪口）到脚底约 **909 px（约 101 格）**，头顶到脚底约 90 格；脚底在离画布底边约 44 px 的地方（附图 7 的深灰线），枪口碰到浅灰线（附图 7 只看大小和位置）。整个人和两把枪都在画面里。
> - **像素块**：大小一致的方块，**每块 9 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的眼睛、眉毛、鼻子、嘴各自成块，不要糊成一团。** 附图 8–10 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边或淡淡的杂点**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间、枪和身体之间的空隙也是透明的。
> - 不画特效（枪口火光、光束）、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/lucian-ppu/lucian-A.png`（1536×1024，**真透明背景**）；原始生成图原样放进 `outputs/lucian-ppu/raw/`；附 `generation-prompts.txt`，写明实际用的提示词；**如果格子不是正好 9 像素，在 HANDOFF 里写明实际是多少像素一格**；**最后**写 `outputs/lucian-ppu/HANDOFF.md`（交付说明），再打包成 `outputs/lucian_ppu_done.zip`。

## 附图（在压缩包 `lucian_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_lucian_idle.png` | 英雄联盟里的卢锡安待机，头放大到 Q 版比例 | **样子**：衣服、颜色、两把枪 |
| `refs/2_lucian_head.png` | 头部特写 | **脸和发型** |
| `refs/3_lucian_back.png` | 从身后看 | 发辫、衣摆和淡紫色衬里、枪 |
| `refs/4_lucian_league.png` | 英雄联盟原比例的待机 | **衣服最准的样子**（比例不照它） |
| `refs/5_lucian_splash.png` | 官方加载画面 | 气质和配色 |
| `refs/6_lucian_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，46 格高） | **只照姿势和 Q 版比例**（颜色和衣服是旧的，不照） |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、枪口要碰到的线（浅灰） |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍，PPU 2.2） | **只看风格** |
| `style/9_style_draven.png` | 本包的德莱文（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_vayne.png` | 本包的薇恩（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`lucian-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Images 1-5 show THE LOOK to draw: League of Legends' Lucian (1 his idle with an enlarged chibi head, 2 his head close up, 3 from behind, 4 his idle at the game's own proportions - the costume at its truest, 5 the official illustration). Image 6 is his current small pixel-art game sprite shown 8x (every square one pixel): use it ONLY for THE POSE AND THE CHIBI PROPORTIONS - the near hand (image left) holds a pistol upright beside the shoulder, muzzle up; the far hand (image right) points the other pistol straight ahead, muzzle to the right; legs apart, planted; the long coat tails hanging back to the calves; a big chibi head (crown to chin about 30 % of the body). Its colours and costume are OLD and WRONG - do not copy them. Image 7 is THIS picture's layout guide: the sprite as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is the ground where his soles stand, the light grey line is where the raised pistol's muzzle goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1536x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no faint specks anywhere, no black or coloured background, no glow). The raised muzzle about 909 px (about 101 squares) above his soles, the top of his head about 90 squares above them, the soles about 44 px above the bottom edge; the whole figure and both pistols inside the picture; both soles on one ground line; nothing at all below his soles.
THE CHARACTER, exactly as League's Lucian (images 1-5): dark brown skin; short hair, the sides cut short, the top swept back in a few tight braids along the scalp; GREEN EYES under a frowning brow, a determined face, an angular jaw - the eyes, brows, nose and mouth each a clear shape, never one muddy blob. A long SILVER-WHITE COAT with a high collar and SILVER SHOULDER ARMOUR TRIMMED IN GOLD; under it a BLACK CHEST PLATE edged in silver; a brown belt with a gold buckle; BLACK TROUSERS; BLACK HIGH BOOTS with silver plates at the knees and shins; the coat's back split into LONG WHITE TAILS with a pale lavender lining (image 3). DARK BROWN GLOVES. Two big, blocky RELIC PISTOLS (images 1 and 3): silver-white and bronze bodies with CYAN-GLOWING RUNES. A chibi body with weight - not thin.
THE POSE AND PROPORTIONS exactly image 6's: the near pistol held upright by the shoulder, the far pistol levelled forward, legs apart, the head chibi-big (it keeps this size in every later animation).
THE VIEW: 3/4 view FACING RIGHT: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 9 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), the pistols, arms and coat separated by outline; no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between his arms and body, between his legs and between the pistols and his body are transparent.
No effects (no muzzle flash, no light beam), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1536×1024、真透明背景，**每个像素透明度只有 0 或 255**，画布上没有淡淡的杂点、没有光晕、没有黑底。
- **样子是英雄联盟的卢锡安**：银白长外套、金边银护肩、黑色胸甲、黑裤黑靴、白色长衣摆（淡紫衬里）、深棕手套、两把发青蓝光符文的大手枪、编辫的短发、绿眼睛。
- **姿势和 Q 版大头照附图 6**：近侧枪竖举、远侧枪平端向前，两腿分开。
- 枪口到脚底约 909 px（约 101 格）；两只脚底在同一条线上，脚底以下什么都没有。
- **每块 9 像素、大小一致、对齐网格**（做不到就在 HANDOFF 里写明实际格子大小）；2 块宽的近黑外描边；没有柔光、渐变、零散杂色格；脸清楚。
- 最后写 `outputs/lucian-ppu/HANDOFF.md`，再打包成 `outputs/lucian_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/lucian/hd/`，照 `tools/art/design_vayne_hd.py`（原图自己的格子）读回；和英雄联盟的渲染、现在的卢锡安、德莱文、薇恩按游戏里的大小并排（**尺寸表 SIZES 要算进去**），给用户确认样子、大小、脸；**密度先出对照表**。
- 动作：照薇恩的做法（`pack_vayne_actions.py` → `casts_vayne_hd.py`：按头定缩放，跑步按头摆），**两把枪每帧在同一只手、枪的样子不变**；他的 tag：attack / passive（光明哨兵连射）/ skill（Q 透体圣光）/ skill2（E 冷酷追击）/ skill2_back / ult（R 圣枪洗礼），idle_base 8 帧。
- 适配：子弹出手点（`lucian_fx_anchors.json`，枪口位置）按新的枪口重新量；头像截取点、选人卡偏移；待机 / 选人卡轮播；俄洛伊灵魂、佛耶戈附身帧表、预览。
