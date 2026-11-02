# 锤石：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 锤石现在游戏里的造型是 1 倍的（附图 6）：从头顶锁链的尖到脚底约 40 格。他**微微前倾地站着**，整个人裹在**深紫黑色的长袍**里；头顶上竖着**一条高高的锁链**，往后上方弯，链节边上**发着绿光**；头是一颗**深色兜帽似的骷髅头**，脸是**惨白的骨色**，眼窝里一只**发亮的绿眼睛**；肩上、胸前、手臂上有一片片**青铜灰色的盔甲板**；**远侧（画面左边）拿着锁链镰刀**——一把**发着绿光的弯刃**竖在身后；**近侧（画面右边）的手垂着提一盏绿色的灯笼**，灯笼在他脚边、发着绿光；袍子下摆是**破破烂烂的深紫色布条**，下面露出两只**深色的靴子**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，锁链尖到脚底约 **120 格**，和琴女、贝蕾亚差不多的密度（附图 9–10）。
> - **照附图 6 描**（附图 5 是他的设计图，放大的样子；细节看附图 1–3）：姿势、Q 版比例、头顶的锁链、骷髅脸、盔甲、镰刀、灯笼、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**深色的骷髅头**（和附图 6 一样的比例），**头顶竖着一条高高的锁链**，往后上方弯，一节一节的**链节边上发着绿光**（附图 1–2）；**惨白的骨色脸**：眼窝、**一只发亮的绿眼睛**、鼻孔和**一排尖牙**各自成块。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 身体：**深紫黑色的长袍**，一层层的**青铜灰色盔甲板**（肩甲、胸甲、护臂），盔甲板上的铆钉和边缘清楚；下摆是破烂的布条。
>   - 镰刀：**远侧手**握着锁链镰刀，**发着淡绿光的弯刃**竖在身后（画面左边），刀柄缠着锁链。
>   - 灯笼：**近侧手**垂着，提着**一盏绿色的灯笼**（画面右下），灯笼的金属框是深色的，里面发着亮绿光。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。**灯笼和镰刀的最低点也不能低于这条线。**
> - **画布用 1024×1024**：**锁链尖到脚底约 720 px（约 120 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），锁链尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、整把镰刀和灯笼都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**骷髅脸的眼窝、绿眼睛、牙齿各自成块，不要糊成一团；盔甲板、镰刀刃、灯笼框都清楚。** 深色的袍子也要分出 3–4 档深浅，**不要整片糊成黑色**。附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（锁链的绿光和灯笼的光也只画成实心的像素块，不要发光晕），也不要画黑色或彩色背景。
> - 不画特效（锁链飞出、钩子、光圈、灵魂都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/thresh-ppu/thresh-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/thresh-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/thresh_ppu_done.zip`。

## 附图（在压缩包 `thresh_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_thresh_idle.png` | 英雄联盟里的锤石待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 头顶的锁链、盔甲、镰刀、灯笼的细节 |
| `refs/2_thresh_head.png` | 头部特写 | 头顶的锁链、骷髅脸、绿眼睛、牙 |
| `refs/3_thresh_back.png` | 从身后看 | 锁链、袍子、盔甲 |
| `refs/4_thresh_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_thresh_first_design.png` | 他的设计图（放大） | 头、锁链、脸、盔甲、颜色 |
| `refs/6_thresh_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 40 格高） | **要描的就是它**：姿势、Q 版比例、锁链、脸、盔甲、镰刀、灯笼、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**锁链尖要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_sona.png` | 本包的琴女（8 倍，PPU 3.88） | **只看风格** |
| `style/10_style_briar.png` | 本包的贝蕾亚（8 倍，PPU 2.94） | **只看风格** |

## 提示词：`thresh-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a spectral jailer standing slightly hunched forward, wrapped in a long DARK PURPLE-BLACK ROBE; a dark skull head with a tall CHAIN rising from its crown, sweeping up and back, its links edged in glowing GREEN; a PALE BONE SKULL FACE with ONE GLOWING GREEN EYE and a row of sharp teeth; plates of BRONZE-GREY ARMOUR on his shoulders, chest and forearms; in his FAR hand (image left) a CHAIN SICKLE - a curved blade glowing pale GREEN held upright behind him; his NEAR hand (image right) hanging down holding a GREEN LANTERN by his feet, its dark iron frame glowing bright green inside; the robe's hem in ragged dark purple strips over dark boots; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same chain, skull, armour, sickle, lantern and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is his first design, enlarged. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 his idle - the chain on his head, the armour, the sickle, the lantern; 2 his head close up - the chain, the skull, the green eyes, the teeth; 3 from behind - the chain, the robe, the armour). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is where his SOLES go, the light grey line is where the TIP OF THE CHAIN on his head goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The tip of the chain on his head is about 720 px (about 120 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure, the whole sickle and the lantern inside the picture; nothing at all below the soles (the lantern and the sickle end at or above the soles' line). Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a dark skull head as in image 6 with the tall CHAIN rising from its crown, swept up and back, link by link, its green glow drawn as solid pixel squares; the PALE BONE FACE - the eye sockets, the ONE GLOWING GREEN EYE, the nose hole and the row of teeth each a clear shape, never one muddy blob. A dark purple-black robe in 3-4 readable shades (never one flat black mass), layered bronze-grey armour plates on the shoulders, chest and forearms with clear rivets and edges, a ragged hem over dark boots. The FAR hand holding the chain sickle upright behind him, its curved blade glowing pale green, chain wound round its handle; the NEAR hand hanging down holding the green lantern by his feet, a dark iron frame, bright green inside.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing - the chain's green glow and the lantern's light are solid squares too.
No effects (no flying chain, no hook, no rings, no souls), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**（锁链的绿光和灯笼也没有光晕）；没有被缩放或裁剪。
- **姿势、Q 版比例、头顶的锁链、骷髅脸、盔甲、镰刀、灯笼、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：远侧手的镰刀竖在身后、近侧手提着灯笼垂在脚边；头的大小照附图 6。
- 锁链尖到脚底约 720 px（约 120 格）；脚底碰到深灰线，下面什么都没有，灯笼和镰刀也不低于这条线。
- 头顶发绿光的锁链、骷髅脸（绿眼睛、牙齿）、青铜灰盔甲、深紫黑长袍（分得出深浅）、绿光镰刀、绿灯笼、破布下摆和靴子都在。
- **每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/thresh-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/thresh_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/thresh/hd/`，照 `tools/art/design_talon_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸用均匀格子读；几种 PPU 给用户选）读回；和泰隆、贝蕾亚、琴女、现在的锤石按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把镰刀和灯笼算进“两脚中点”）。
- 动作：他的 tag：idle 20、run 8、attack 7、skill 8、skill2 8、ult 8、hit 2、dead 8、idle_base 8、bp 51（`hero_reels.json`：待机 = skill 7、6 + skill2 3–4）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移、灯笼附加包 `league_thresh_lantern`。和泰隆在同一个 PR（claude/talon-ppu）。
