# 佐伊：照英雄联盟原版重新设计，按 PPU 3 画设计图（给 Codex 的提示词）

> 佐伊现在游戏里的造型（附图 6）**用户不满意，说完全不像英雄联盟的佐伊，这次不要照它画**，而是**照英雄联盟原版的佐伊重新设计**（附图 1–4；附图 5 是同一个英雄联盟模型换成本游戏 Q 版比例的样子）。她是**暮光星灵**，一个**活泼的小女孩**：**又长又多的粉色头发**（**发梢渐变成紫色**，编着辫子，往身后飘，上面套着**金色的发环**），**头顶的头发是最高处**；**一只紫色、一只蓝色的大眼睛**，**咧嘴大笑**；脖子上围着**青色的围巾**；**深色的短上衣**、**青色的短裙**和**金色的饰边**、胸前一个**金色的挂坠**；手腕上**金色的手镯**；**深蓝色的护踝**、**光着的脚趾**。按 **PPU 3**，**每个游戏像素画成 3 格**，头顶到脚底约 **108 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **长相、发型、衣服、颜色全部照英雄联盟原版**（附图 1–4），**头发是粉色、发梢紫色**（**不是深蓝色**：附图 6 的深蓝头发是错的），**头和身体的比例照附图 5**（本游戏的 Q 版比例：头大一些、腿短一些）：
>   - 头：**粉色的长头发**（发梢紫色、编辫子、金色发环，往身后飘）、**一只紫眼睛一只蓝眼睛**、**咧嘴大笑**。
>   - 上身：**青色的围巾**、**深色的短上衣**、胸前**金色的挂坠**、手腕上**金色的手镯**。
>   - 下身：**青色的短裙**和**金色的饰边**、**深蓝色的护踝**、**光着的脚趾**，两脚站稳。
>   - **头的大小就是以后每个动作都要保持的大小**，照附图 5 的比例画；长头发往身后飘，**不要比附图 7 的剪影宽太多**。
> - **姿势和大小照附图 6**（**只看这两样，它的长相、发色、衣服、颜色都不要照**）：面朝右站着、身子微微转向看画的人，**两只手张开放在身体两侧**，两脚站稳，长头发往身后（画面左边）飘起来。整个人的高度和站的位置照附图 7。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**头顶到脚底约 648 px（约 108 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），头顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**两只眼睛（一紫一蓝）、眉毛和嘴各自成块，不要糊成一团；辫子、发环、围巾、挂坠和手镯都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、头发和身体之间的空隙也是透明的。
> - 不画特效（没有星星、光点、传送门、光晕、残影），也**不画她的玩具**（跳绳、球拍、悠悠球、冰淇淋），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/zoe-ppu/zoe-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/zoe-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/zoe_ppu_done.zip`。

## 附图（在压缩包 `zoe_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zoe_idle.png` | 英雄联盟里的佐伊 | **长相、发型、发色、衣服、颜色照它** |
| `refs/2_zoe_head.png` | 头部特写 | 脸、眼睛、头发 |
| `refs/3_zoe_back.png` | 从身后看 | 背面、头发后面 |
| `refs/4_zoe_splash.png` | 官方加载画面 | 气质和配色（粉橙色的头发、发梢紫色） |
| `refs/5_zoe_chibi.png` | 同一个英雄联盟模型换成本游戏的 Q 版比例（头 1.6 倍、腿 0.9 倍） | **头和身体的比例照它** |
| `refs/6_zoe_now.png` | 她现在的游戏造型（3 倍，**用户不满意；深蓝头发是错的**） | **只看姿势和大小**；长相、发色、衣服、颜色都不要照 |
| `refs/7_layout.png` | 布局示意：现在的造型放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/8_style_veigar.png` | 本包的维迦（8 倍，PPU 1.8） | **只看风格** |
| `style/9_style_seraphine.png` | 本包的萨勒芬妮（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_ezreal.png` | 本包的伊泽瑞尔（8 倍，PPU 2.19） | **只看风格** |

## 提示词：`zoe-A.png`

附图 1–10，顺序同上表（1 = 1_zoe_idle.png, 2 = 2_zoe_head.png, 3 = 3_zoe_back.png, 4 = 4_zoe_splash.png, 5 = 5_zoe_chibi.png, 6 = 6_zoe_now.png, 7 = 7_layout.png, 8 = 8_style_veigar.png, 9 = 9_style_seraphine.png, 10 = 10_style_ezreal.png）。

```text
10 attached images. Images 1-4 show THE CHARACTER TO DRAW: Zoe from League of Legends - image 1 a 3D render of her, image 2 her head close up, image 3 from behind, image 4 the official illustration. Copy her LOOK from them: a cheerful little girl with VERY LONG, FULL PINK HAIR fading to VIOLET at its ends, braided, with GOLD HAIR RINGS, streaming out behind her (the top of her hair her highest point); ONE PURPLE EYE AND ONE BLUE EYE, a wide open grin; a TEAL SCARF round her neck; a DARK CROP TOP with a GOLD PENDANT; a TEAL SKIRT with GOLD TRIM; GOLD BRACELETS; DARK BLUE ANKLE WRAPS and bare toes. Her hair is PINK, never dark navy. Image 5 is the same 3D model in THIS GAME'S CHIBI PROPORTIONS (a bigger head, shorter legs): give her these proportions. Image 6 is her CURRENT game sprite, which the user REJECTED as looking nothing like League's Zoe (its dark navy hair is wrong): take ONLY its POSE and its SIZE - standing turned to the viewer's right, the body turned a little towards the viewer, both arms held open at her sides, both feet planted, the long hair streaming out behind her on the viewer's left - and copy NOTHING of its looks (not its hair colour, face, clothes or colours). Image 7 is THIS picture's layout guide: the current sprite as a flat silhouette at the new size - how big the character is and where she stands; the dark grey line marks THE SOLES, the light grey line THE TOP OF HER HAIR. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her hair is about 648 px (about 108 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (League's Zoe, in image 5's proportions and image 6's pose): the long pink hair with its violet ends, the braid and the gold rings, streaming behind her - not much wider than image 7's silhouette; the purple eye, the blue eye, the brows and the grin each a clear shape, never one muddy blob. The teal scarf, the dark crop top with its gold pendant, the gold bracelets, the teal skirt with its gold trim. The dark blue ankle wraps and the bare toes planted; both soles on one line.
The head the size image 5's proportions give it (it keeps this size in every later animation).
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (no stars, no sparkles, no portals, no glow, no afterimages) and none of her toys (no jump rope, paddle, yo-yo or ice cream), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **长相、发型、衣服、颜色是英雄联盟的佐伊**（附图 1–4）：**粉色头发、发梢紫色**，一紫一蓝的眼睛；**比例照附图 5**；**只有姿势和大小照附图 6**（附图 6 的长相一点都不要）。
- 头顶到脚底约 648 px（约 108 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效、没有玩具。
- 画完后最后写 `outputs/zoe-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zoe_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- 这次是**照英雄联盟原版重新设计**（用户：「佐伊的模型我也不满意 完全不像英雄联盟的佐伊」「一起改了」「佐伊原版不是粉头发吗？」）。
- 现在的模型头发是深蓝的，因为她的长头发是单独的网格 `Zoe_Base_Hair_Mat`，有自己的贴图 `Zoe_Base_Hair_TX_CM`，以前渲染时套了身体的贴图；这次的渲染用 `--submesh-texture Zoe_Base_Hair_Mat=Zoe_Base_Hair_TX_CM`（`pack_zoe_ppu.py` 的 SUBTEX），玩具按名字隐藏（HIDE），镜头 yaw -10、镜像。**以后渲染她的动作参考也要带上这两项。**
- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/zoe/hd/`，照 `tools/art/design_khazix_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空（平均色会把眼睛糊掉）；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的佐伊按游戏里的大小并排，给用户确认大小、脸、粗细。
- 她的 1 倍精灵现在是 36 行（hd.rs 里 PPU 1.5，外描边 1）：新设计图按 36 行定 PPU。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- 动作包照 `pack_khazix_actions.py`：跑步逐帧写明哪条腿撑地（第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放先按叠合法（`casts_*_hd.py --fits`），再按头（或别的不会变的部件）的大小校正到设计图那么大（第 6 批的 `b6_headzoom.py`；用户：「一定要注意模型不要变大变小」）；外描边 2 格（用户：「避免过度高清」）。
- 和这一批的另外几位在同一个 PR（claude/teemo-ppu）（用户：「最后重做提莫 菲兹 泽丽吧 泽丽虽然是高清帧了 但是模型我不满意」「佐伊的模型我也不满意 完全不像英雄联盟的佐伊」「一起改了」）。
