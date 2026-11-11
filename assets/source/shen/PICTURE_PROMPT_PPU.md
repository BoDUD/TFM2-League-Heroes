# 慎：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 慎现在游戏里的造型是 1 倍的（附图 6）：从背上刀柄的顶端（柄头的浅蓝宝石）到脚底约 42 格。他是**暮光之眼**，一个**忍者**，**面朝右站着**、微微下蹲备战；**深藏青色的忍者长袍**镶着**银白色的边**；头上**深色的兜帽**（两侧**银色的尖角**）；**灰色的面罩**遮住下半张脸，**银色的眉甲**下**只露出一双眼睛**；**背上斜挎着一把刀**，**刀柄**从画面左边的肩膀后面伸出来，**柄头是一颗浅蓝色的宝石**（**最高处**）；画面左边的手臂**裸露**（**棕黄色的皮肤**），手里垂着一把**淡色的弯刃**；画面右边的肩上一大块**银边的深蓝色护肩**，手戴着**棕色的手套**伸向右下方；**紫色的裤子**、**棕色的靴子**（鞋底是紫色）。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，背上刀柄的顶端（柄头的浅蓝宝石）到脚底约 **126 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 1–3）：姿势、Q 版比例、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**深色的兜帽**（两侧银色的尖角）、**灰色的面罩**遮住下半张脸、**银色的眉甲**下**只露出眼睛**。
>   - 身体：**深藏青色的忍者长袍**镶**银白色的边**、腰间的**深蓝腰带**、**紫色的裤子**。
>   - 刀：**背上斜挎的刀**：**刀柄**从画面左边的肩后伸出，**柄头一颗浅蓝宝石**（最高处）；画面左边的手垂着**淡色的弯刃**，**长度和角度照附图 6**。
>   - 手和脚：画面左边的手臂**裸露**（棕黄色），画面右边的肩上**银边的深蓝色大护肩**、手戴**棕色手套**；**棕色的靴子**（紫色鞋底），两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**背上刀柄的顶端（柄头的浅蓝宝石）到脚底约 756 px（约 126 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），背上刀柄的顶端（柄头的浅蓝宝石）碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**露出的眼睛、面罩的褶子各自成块，不要糊成一团；刀柄和宝石、弯刃、面罩和眼睛都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、弯刃和身体之间的空隙也是透明的。
> - 不画特效（没有紫色的灵气、护盾、结界、残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/shen-ppu/shen-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/shen-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/shen_ppu_done.zip`。

## 附图（在压缩包 `shen_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_shen_idle.png` | 英雄联盟里的慎（写实比例，**姿势和比例不要照它**） | 细节 |
| `refs/2_shen_head.png` | 头部特写 | 头和脸 |
| `refs/3_shen_back.png` | 从身后看 | 背面 |
| `refs/4_shen_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_shen_first_design.png` | 他现在造型做出来时的样子（英雄联盟的模型按本游戏的比例摆好、画成像素，没有 Codex 原稿） | 长相、颜色 |
| `refs/6_shen_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 42 格高） | **要描的就是它**：姿势、Q 版比例、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**背上刀柄的顶端（柄头的浅蓝宝石）要碰到的线（浅灰）** |
| `style/8_style_veigar.png` | 本包的维迦（8 倍，PPU 1.8） | **只看风格** |
| `style/9_style_seraphine.png` | 本包的萨勒芬妮（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_ezreal.png` | 本包的伊泽瑞尔（8 倍，PPU 2.19） | **只看风格** |

## 提示词：`shen-A.png`

附图 1–10，顺序同上表（1 = 1_shen_idle.png, 2 = 2_shen_head.png, 3 = 3_shen_back.png, 4 = 4_shen_splash.png, 5 = 5_shen_first_design.png, 6 = 6_shen_now.png, 7 = 7_layout.png, 8 = 8_style_veigar.png, 9 = 9_style_seraphine.png, 10 = 10_style_ezreal.png）。

```text
10 attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a ninja standing turned to the viewer's right in a low ready stance - a DARK NAVY-BLUE NINJA ROBE with SILVER-WHITE TRIMS; a DARK HOOD with SILVER POINTS on its sides; a GREY MASK over the lower face, ONLY THE EYES SHOWING under a SILVER BROW PLATE; a SWORD slung across his back, its HILT rising over the shoulder on the viewer's left with a LIGHT BLUE GEM on the pommel (THE GEM his highest point); the arm on the viewer's left BARE (tan skin), a PALE CURVED BLADE hanging from its hand; a BIG SILVER-RIMMED DARK BLUE SHOULDER PAD on the viewer's right, that hand in a BROWN GLOVE held out to the lower right; PURPLE TROUSERS and BROWN BOOTS with purple soles; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance and the same colours - only at a finer pixel density, with the details the small sprite could not hold. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them. Image 4 is the official illustration: the mood and the colours. Image 5 is the character's design picture: the looks and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big the character is and where it stands; the dark grey line marks THE SOLES, the light grey line THE TOP OF THE SWORD HILT ON HIS BACK. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of the sword hilt on his back is about 756 px (about 126 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): the head as big as in image 6 with the dark hood and the grey mask; the eyes and the folds of the mask each a clear shape, never one muddy blob. The dark navy robe with its silver-white trims, the dark blue belt, the purple trousers. The sword on his back, its hilt and the light blue gem over the shoulder; the pale curved blade in the bare hand on the viewer's left, as long and at the angle it has in image 6; the brown glove on the viewer's right. The brown boots planted; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (no purple ki glow, no shield, no zone, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）；头的大小照附图 6。
- 背上刀柄的顶端（柄头的浅蓝宝石）到脚底约 756 px（约 126 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/shen-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/shen_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/shen/hd/`，照 `tools/art/design_khazix_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空（平均色会把眼睛糊掉）；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的慎按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- 动作包照 `pack_khazix_actions.py`：跑步逐帧写明哪条腿撑地（第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放先按叠合法（`casts_*_hd.py --fits`），再按头（或别的不会变的部件）的大小校正到设计图那么大（用户：「一定要注意模型不要变大变小」「千万别出现模型一大一小的问题」）；外描边 2 格（用户：「避免过度高清」）。
- 单独一个 PR（claude/shen-ppu）（用户：「慎也需要重做」）。
