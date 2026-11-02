# 泰隆：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 泰隆现在游戏里的造型是 1 倍的（附图 6）：从兜帽顶到脚底约 39 格。他**压低身子、向前探着站**（刺客的预备姿势）：**一条腿在前、膝盖弯着，后腿蹬着**；**蓝紫色的大兜帽**拉得很低，兜帽边缘是一道**银色的护额**，在额头中间收成一个**尖尖的 V 字**，两边有**银色的护颊**；兜帽下面**露着脸**：**晒黑的肤色**，眼睛藏在兜帽的阴影里；**近侧的手臂往前伸**，**深灰钢护腕**、**蓝紫色手套**握着拳；脖子上围着**蓝紫色的围巾**，有一道**青色的细条纹**，肩上有**银色的护肩**；身后是**酒红色的长披风**，披风下端连着**一把很长的银色刀尖**，斜着拖向**画面左下方**；**深蓝色的上衣和裤子**，**深灰钢的护膝、护胫和靴子**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，兜帽顶到脚底约 **117 格**，和琴女、贝蕾亚差不多的密度（附图 9–10）。
> - **照附图 6 描**（附图 5 是他的设计图，细节看附图 1–3）：姿势、Q 版比例、兜帽、披风、刀尖、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的兜帽**（和附图 6 一样的比例），**银色 V 字护额**和两边的护颊清清楚楚；兜帽下**露着晒黑的脸**：**眼睛（在兜帽阴影里）、眉、嘴各自成块**，表情冷硬。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：蓝紫色围巾和**青色细条纹**，**银色的护肩**（几片叠起来的钢片），**深蓝色的上衣**、腰上的**青色和金色腰带**。
>   - 手：**近侧手臂往前伸**，深灰钢护腕、**蓝紫色手套握拳**，手指清楚。
>   - 披风和刀尖：**酒红色的长披风**从肩后垂下，**下端连着一把很长的银色刀尖**，像矛头一样斜着拖向画面左下方，银色亮面和暗面分清楚。
>   - 腿：**深蓝色裤子**，**深灰钢的护膝、护胫和靴子**，前腿弯、后腿蹬。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。**刀尖的最低点也不能低于这条线。**
> - **画布用 1024×1024**：**兜帽顶到脚底约 702 px（约 117 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），兜帽顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、整件披风和整把刀尖都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；V 字护额、护肩、手指和刀尖都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、披风和腿之间的空隙也是透明的。
> - 不画特效（刀光、残影、血都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/talon-ppu/talon-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/talon-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/talon_ppu_done.zip`。

## 附图（在压缩包 `talon_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_talon_idle.png` | 英雄联盟里的泰隆待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 兜帽、护额、护肩、披风、刀刃的细节 |
| `refs/2_talon_head.png` | 头部特写 | 兜帽、V 字护额、护颊、脸 |
| `refs/3_talon_back.png` | 从身后看 | 披风、披风上的刀尖、兜帽背面 |
| `refs/4_talon_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_talon_first_design.png` | 他最早的设计图（8 倍） | 兜帽、披风、刀尖、颜色 |
| `refs/6_talon_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 39 格高） | **要描的就是它**：姿势、Q 版比例、兜帽、披风、刀尖、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**兜帽顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_sona.png` | 本包的琴女（8 倍，PPU 3.88） | **只看风格** |
| `style/10_style_briar.png` | 本包的贝蕾亚（8 倍，PPU 2.94） | **只看风格** |

## 提示词：`talon-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a hooded assassin in a low ready stance leaning forward - one leg forward with the knee bent, the back leg pushing off - a big BLUE-VIOLET HOOD pulled low, its rim edged by a SILVER BROW GUARD that comes to a sharp V point in the middle of the forehead, with silver cheek guards; under it a TANNED FACE, the eyes in the hood's shadow; the NEAR ARM reaching forward, a dark gunmetal vambrace and a blue-violet glove clenched in a fist; a blue-violet scarf with a thin TEAL stripe, a SILVER PAULDRON; a long dark RUST-RED CLOAK behind him whose lower end becomes ONE LONG SILVER BLADE TIP trailing down and back to the image's lower left like a spear point; a dark navy tunic and trousers, a teal and gold sash, dark gunmetal knee guards, greaves and boots; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same crouch, the same hood, cloak, blade tip and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is his first design, enlarged: the hood, the cloak, the blade tip, the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 his idle - the hood, the brow guard, the pauldron, the cloak, the blades; 2 his head close up - the hood, the V brow guard, the cheek guards, the face; 3 from behind - the cloak and its blade tips, the back of the hood). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is where his SOLES go, the light grey line is where the TOP OF THE HOOD goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of the hood is about 702 px (about 117 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure, the whole cloak and the whole blade tip inside the picture; nothing at all below the soles (the blade tip ends at or above the soles' line). Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG HOOD as in image 6, deep blue-violet with bright violet-blue highlights; the SILVER V BROW GUARD and the cheek guards crisp and bright; the TANNED FACE under it - the eyes in the hood's shadow, the brows and the hard mouth each a clear shape, never one muddy blob. A blue-violet scarf with a thin teal stripe, a layered SILVER PAULDRON (a few overlapping steel plates), a dark navy tunic, a teal and gold sash. The near arm reaching forward: a gunmetal vambrace, a blue-violet glove in a fist, the fingers readable. The rust-red cloak from dark maroon to a warm red highlight, its lower end one LONG SILVER BLADE TIP trailing to the lower left, bright steel with a white glint and a darker back edge. Dark navy trousers, dark gunmetal knee guards, greaves and boots with blue-grey highlights; the front knee bent, the back leg pushing off, both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A lean build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the cloak and the legs are transparent.
No effects (no blade trails, no afterimages, no blood), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、兜帽、披风、刀尖、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：压低身子向前探、近侧手臂往前伸握拳、披风下端的长银刀尖拖向左下；头的大小照附图 6。
- 兜帽顶到脚底约 702 px（约 117 格）；脚底碰到深灰线，下面什么都没有，刀尖也不低于这条线。
- 蓝紫兜帽、银色 V 字护额和护颊、晒黑的脸、青色条纹的围巾、银护肩、青金腰带、酒红披风和银刀尖、深灰钢护膝护胫靴子都在；脸上各部分清楚。
- **每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/talon-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/talon_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/talon/hd/`，照 `tools/art/design_briar_hd.py`（按原图自己的格子读、每条线贴着最近的色边；调色板 64 色；原画的细节比格子还细时，用更细的格子读，几种 PPU 给用户选）读回；和贝蕾亚、琴女、现在的泰隆按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把披风的长刀尖算进“两脚中点”）。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：手臂怎么伸、披风和刀尖怎么拖、腿怎么站。
- 动作：他的 tag：idle 14、run 8、attack 5、skill 6、skill2 7、skill2_stab 6、skill_e 7、ult 8、hit 2、dead 8、idle_base 6、bp 42（`hero_reels.json`：待机 = attack 0–1 + skill2_stab 5）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移、翻墙附加包 `league_talon_vault`。装游戏前先合进最新 main，版本号接着游戏里现装的往上加；附加包合集要带上还没合并的别的会话的分支（见记忆 game-dll-versions）。
