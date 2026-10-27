# 雷恩加尔（狮子狗）：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 雷恩加尔现在游戏里的造型是 1 倍的（附图 6）：角尖顶到脚底约 41 格，弓着背、半蹲的猎手架势——近侧（画面左边）的爪子低垂在身前，远侧（画面右边）的手臂握着弯刀垂在身侧，尾巴从身后卷到右下。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，角尖顶到脚底约 **62 格**，和盲僧、乌迪尔、赵信同样的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 5 和 1–3）：姿势、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势。只是格子密了，把 1 倍画不下的细节画出来：
>   - **体格要壮**：野兽猎手的结实身材——宽厚的肩背、粗壮的手臂和大腿、**弓着背往前探**，**不要画成细长的身材**，也不要站直。
>   - 头：**一大团灰白色的长鬃毛，编成一条条粗辫子**从头顶垂到背后；**两只弯弯的米黄色角**（一只在头顶右边往上翘，一只从鬃毛里伸出）；**灰白的猫科脸**，一只**发光的金黄色眼睛**，另一只眼睛上有**伤疤**；**粉灰色的猫鼻子**（中间一个小三角）、张开的嘴露出**尖牙**、下巴上白色的胡须。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**棕色的皮甲**，肩上一块**大的深色肩甲**，镶**金色的铆钉**和蓝灰色的金属片；胸前一条皮带；手臂是**蓝灰色的毛皮**。
>   - 手和武器：近侧的手是**米黄色的长爪子**（几根弯指甲张开）；远侧的手握着一把**米黄色的骨质弯刀**，刀尖往下弯，**刀尖一截暗红色**。
>   - 下身：腰间**金色的方形腰扣**，**棕色的皮短裙**分成几片；粗壮的腿，**护膝**；脚是**带米黄色爪子的兽脚**。
>   - 尾巴：一条**蓝灰色的细尾巴**从身后卷出来，尾巴上套着**金色的环**。
> - **朝向**：和附图 6 一样，四分之三侧身，**脸和胸口朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用 1024×1024**：**角尖顶到脚底约 676 px（约 62 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），角尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、爪子、弯刀和尾巴都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的眼睛、伤疤、鼻子、嘴和牙各自成块，不要糊成一团；鬃毛的辫子一条条分得清。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间、尾巴和身体之间的空隙也是透明的。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/rengar-ppu/rengar-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/rengar-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/rengar_ppu_done.zip`。

## 附图（在压缩包 `rengar_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_rengar_idle.png` | 英雄联盟里的雷恩加尔待机，四分之三朝右 | 鬃毛、角、皮甲、爪子、弯刀、尾巴的细节 |
| `refs/2_rengar_head.png` | 头部特写 | 鬃毛辫子、角、脸、眼睛和伤疤 |
| `refs/3_rengar_back.png` | 从身后看 | 鬃毛辫子、尾巴、皮甲 |
| `refs/4_rengar_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_rengar_first_design.png` | 他原来的设计图（1 倍） | 头、衣服、颜色 |
| `refs/6_rengar_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 41 格高） | **要描的就是它**：姿势、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**角尖要碰到的线（浅灰）** |
| `style/8_style_leesin.png` | 本包的李青（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_udyr.png` | 本包的乌迪尔（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_xinzhao.png` | 本包的赵信（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`rengar-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a hulking lion-like beast hunter in a hunched stalking crouch - back bent forward, knees bent, the near hand (image left) a big clawed hand hanging low in front, the far hand (image right) gripping a curved bone blade that hangs down at his side, a thin tail curling out behind him to the lower right - shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same stance, the same costume and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is his earlier design at game size: the head, clothes and colours. Images 1-3 are 3D renders of the same character from the game (1 his idle - the mane, the horns, the leather armour, the claws, the blade, the tail; 2 his head close up - the braided mane, the horns, the face, the eye and the scar; 3 from behind). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is the ground where his soles stand, the light grey line is where the TIP OF HIS HORN goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The tip of his horn is about 676 px (about 62 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure, the claws, the blade and the tail inside the picture; both feet on one ground line; nothing at all below his feet.
THE BUILD: HEAVY and POWERFUL - a beast hunter's broad hunched back and shoulders, thick furry arms and thighs, leaning forward; NOT a slim, long-limbed or upright figure. The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE CHARACTER (as image 6, detailed after images 5 and 1-3): a big GREY-WHITE MANE of thick BRAIDED locks falling from the top of the head down the back, each braid readable; two curved CREAM-COLOURED HORNS (one rising from the top right of the head, one pushing out of the mane); a pale grey-white FELINE FACE with ONE GLOWING GOLDEN-YELLOW EYE and a SCAR over the other eye, a small pinkish-grey CAT NOSE with a triangle tip, an open mouth showing sharp FANGS, a white beard under the chin - eye, scar, nose, mouth and fangs each a clear shape, never one muddy blob. BROWN LEATHER ARMOUR with a big dark PAULDRON studded with GOLD RIVETS and blue-grey metal plates, a strap across the chest; BLUE-GREY FURRY ARMS. The near hand a big CREAM CLAW with long curved nails spread; the far hand gripping a curved CREAM BONE BLADE pointing down, its tip DARK RED. A square GOLD BELT BUCKLE, a BROWN LEATHER KILT in several flaps, knee guards, beast feet with cream claws. A thin BLUE-GREY TAIL curling out from behind with GOLD RINGS on it.
THE VIEW: 3/4 view FACING RIGHT as image 6: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between his arms and body, between his legs and between the tail and the body are transparent.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势、比例、衣服、颜色和附图 6 一样**（细节照附图 5 和 1–3），只是更密、更细；**体格壮实、弓着背**，头的大小照附图 6。
- 角尖到脚底约 676 px（约 62 格）；两只脚在同一条线上，脚底以下什么都没有。
- 灰白辫子鬃毛、两只米黄色角、金黄独眼和伤疤、猫鼻子和尖牙、棕色皮甲和金铆钉肩甲、蓝灰毛皮手臂、米黄爪子、刀尖暗红的骨质弯刀、金腰扣和皮短裙、兽脚、带金环的蓝灰尾巴都在；脸上各部分清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/rengar-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/rengar_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/rengar/hd/`，照 `tools/art/design_leesin_hd.py`（原图自己的格子，Samira 的读法）或 `design_draven_hd.py`（格子正好时逐格读回）读回；和李青、乌迪尔、现在的狮子狗按游戏里的大小并排（**尺寸表 SIZES 要算进去**），给用户确认大小、脸、粗细。密度超过 1.5 先给密度表（`review_leesin_ppu.py` 的做法），不要直接用。
- 动作：照李青 / 德莱文的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_leesin_actions.py`），再读回到设计图上（`casts_leesin_hd.py`）；**动作包里写明头和设计图一样大**，交回后逐帧把设计图的头轮廓叠上去量；**跑步查左右脚轮换和起伏**（他的跑步用户选的是 A：小腿原地交替，不交叉步）。他的 tag：idle、run、attack、leap（被动扑跳）、skill（W 怒吼）、skill_w、skill2（E 套索）、ult、hit、dead、idle_base 8 帧、bp。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂剪影、待机和选人卡轮播、E 套索出手点和特效锚点、头像截取点、选人卡偏移；卡兹克彩蛋、草丛扑跳附加包（league_rengar_bush）只读精灵，不用改。
