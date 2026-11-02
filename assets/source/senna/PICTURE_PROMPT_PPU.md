# 赛娜：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 赛娜现在游戏里的造型是 1 倍的（附图 6）：从炮的金爪顶到脚底约 39 格。她**面朝右站着，两脚分开**；头上是**白色的兜帽**，**金色滚边**，兜帽里露出**深紫色的发辫**；**深棕色的皮肤**，**眼睛发着青绿色的光**，**红色的嘴唇**；身上是**深紫色的紧身衣**，有金色的小饰件；兜帽前面垂下**一条长长的白色饰带**，金色滚边，从胸前一直垂到膝盖；**靴子**是**浅钢蓝色**，有**金色的护片**。**巨大的遗物炮扛在肩上**：炮尾的**金色爪形握把**翘在她**头的后上方（画面右上）**，她的手在那里握着；炮身从肩后斜着伸向**画面左下方**，上面是**一大片浅冰蓝的水晶刃**，下面是**酒红色、带金色细筋的翅板**，肩头那里是**带深色圆眼的金环**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，头顶到脚底约 **117 格**，和金克丝、贝蕾亚、女枪差不多的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是她的设计图，细节看附图 1–3）：姿势、Q 版比例、兜帽、饰带、遗物炮、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的头**（和附图 6 一样的比例），**白色兜帽和金色滚边**清清楚楚，兜帽里露出**深紫色发辫**；脸是**深棕色**：**青绿发光的眼睛、眉、红嘴唇各自成块**，表情沉静。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**深紫色紧身衣**和金色小饰件，兜帽前面垂到膝盖的**白色长饰带**和**金色滚边**。
>   - 手和炮：**遗物炮扛在肩上**，手握着头后上方的**金色爪形握把**，手指清楚；**遗物炮很大、完整、笔直**：金爪握把、**带深色圆眼的金环**、浅冰蓝的**水晶刃**（亮面、暗面分清楚）、**酒红色带金筋的翅板**，从肩后斜着伸向画面左下方，**炮的大小和角度照附图 6**。
>   - 腿：**深紫色的腿**，两脚分开站稳，**浅钢蓝色的靴子和金色护片**。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。**炮的最低点也不能低于这条线。**
> - **画布用 1024×1024**：**炮的金爪顶到脚底约 702 px（约 117 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），炮的金爪顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、整条饰带和整门炮都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；兜帽滚边、手指和炮的每个部件都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、炮和身体之间、饰带和腿之间的空隙也是透明的。
> - 不画特效（光束、炮口火光、黑雾、灵魂都不要），**眼睛的青光只画在眼睛里，不往外发光**；不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/senna-ppu/senna-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/senna-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/senna_ppu_done.zip`。

## 附图（在压缩包 `senna_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_senna_idle.png` | 英雄联盟里的赛娜待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 兜帽、饰带、紧身衣、遗物炮的细节 |
| `refs/2_senna_head.png` | 头部特写 | 兜帽、发辫、脸 |
| `refs/3_senna_back.png` | 从身后看 | 炮扛在肩上的样子、炮的另一面、靴子 |
| `refs/4_senna_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_senna_first_design.png` | 她最早的设计图（8 倍） | 兜帽、饰带、遗物炮、颜色 |
| `refs/6_senna_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 39 格高） | **要描的就是它**：姿势、Q 版比例、兜帽、饰带、遗物炮、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**炮的金爪顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_briar.png` | 本包的贝蕾亚（8 倍，PPU 2.94） | **只看风格** |
| `style/10_style_missfortune.png` | 本包的女枪（8 倍，PPU 2.76） | **只看风格** |

## 提示词：`senna-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a woman standing with her feet apart, turned to the viewer's right - a WHITE HOOD with GOLD TRIM over dark violet locs; DARK BROWN SKIN, softly GLOWING TEAL EYES, RED LIPS; a dark violet bodysuit with small gold fittings; a long WHITE SASH with gold trim hanging from the hood down her front to her knees; pale steel-blue boots with gold plates; a HUGE RELIC CANNON RESTING ON HER SHOULDER - its GOLD CLAW GRIP sticking up behind her head at the image's upper right, where her hand holds it, a GOLD RING with a dark round eye at her shoulder, and its long head slanting down behind her to the image's lower left: a big pale ICE-BLUE CRYSTAL BLADE along its top, a WINE-RED WING PANEL with gold ribs under it; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same hood, sash, cannon and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is her first design, enlarged: the hood, the sash, the cannon, the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 her idle - the hood, the sash, the bodysuit, the cannon on her shoulder; 2 her head close up - the hood, the locs, the face; 3 from behind - how the cannon rests on her shoulder, its other side, the boots). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF THE CANNON'S GOLD CLAW GRIP goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of the gold claw grip is about 702 px (about 117 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, the whole sash and the whole cannon inside the picture; nothing at all below the soles (the cannon ends at or above the soles' line). Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG HEAD as in image 6 in its WHITE HOOD with crisp GOLD TRIM, dark violet locs showing inside it; the DARK BROWN FACE - the glowing teal eyes, the brows and the red lips each a clear shape, never one muddy blob; a calm, resolute look. A dark violet bodysuit with small gold fittings, the long white sash with its gold trim down her front. The RELIC CANNON on her shoulder, as large and at the same angle as in image 6, whole and straight: the gold claw grip behind her head with her hand on it (the fingers readable), the gold ring with its dark round eye, the pale ice-blue crystal blade with clear light and shadow faces, the wine-red wing panel with its gold ribs, slanting down behind her to the lower left. Dark violet legs, the feet apart and planted, pale steel-blue boots with gold plates; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A slim build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs, between the cannon and the body and between the sash and the legs are transparent.
No effects (no beams, no muzzle flash, no black mist, no souls; the teal glow stays inside the eyes), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、兜帽、饰带、遗物炮、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：面朝右、两脚分开站、遗物炮扛在肩上（金爪握把在头后上方、炮身斜伸向左下）；头的大小照附图 6。
- 炮的金爪顶到脚底约 702 px（约 117 格）；脚底碰到深灰线，下面什么都没有，炮也不低于这条线。
- 金边白兜帽和里面的深紫发辫、深棕皮肤、青绿发光的眼睛、红唇、深紫紧身衣、金边白长饰带、浅钢蓝靴子和金护片、金爪握把、带圆眼的金环、浅冰蓝水晶刃和酒红金筋翅板的遗物炮都在；脸上各部分清楚；眼睛的光不往外发。
- **每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/senna-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/senna_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/senna/hd/`，照 `tools/art/design_talon_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；调色板 64 色；原画的细节比格子还细时，用更细的格子读，几种 PPU 给用户选）读回；和金克丝、贝蕾亚、女枪、现在的赛娜按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把遗物炮算进“两脚中点”；最高点是炮的金爪，不是头）。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：炮怎么扛、饰带怎么垂、腿怎么站；跑步每一帧写明哪条腿在前（泰隆的教训）。
- 动作：她的 tag：idle 10、run 8、attack 6、skill 6、skill2 6、ult 8、hit 1、dead 6、idle_base 1、bp 29（`hero_reels.json`：待机 = skill2 5 + skill 1）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移、黑雾附加包 `league_senna_mist`。装游戏前先合进最新 main，版本号接着游戏里现装的往上加；附加包合集要带上还没合并的别的会话的分支（见记忆 game-dll-versions）。
