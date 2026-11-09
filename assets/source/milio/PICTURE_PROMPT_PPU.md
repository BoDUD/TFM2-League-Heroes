# 米利欧：照现在的造型、背后加上英雄联盟里的大背包（葫芦），按 PPU 3 画设计图（给 Codex 的提示词）

> 米利欧现在游戏里的造型**少了英雄联盟里他背后那个很大的葫芦形背包**（用户：「现在我们做的背后没有葫芦」）。这次**男孩本身照附图 6 画**（他现在的造型原稿：长相、卷发、衣服、颜色、姿势、大小、火精灵都照它），**背后加上英雄联盟里的大背包**（附图 1–3、5）。他是**明烛**，一个**开朗的伊施塔尔小男孩**：**蓬松的深靛蓝色卷发**、**两只琥珀色的大眼睛**、**咧嘴笑**；**红色的短上衣**、**青绿色的立领**和胸前**青绿色的圆坠饰**；**金色蓬起的大肩垫**和**米白色的流苏**；**青绿色的斜腰带**和金扣；**品红色的褶裙**；**红色和青绿色的绑腿**、**棕色的凉鞋**。附图 6 已经是放大 6 倍的样子（**一格 = 6 像素，就是这次的格子**），发顶到脚底 **95 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **背包（这次就是为了它，最重要）**：照英雄联盟原版（附图 1–3），**大小照附图 5**（本游戏 Q 版比例下背包和男孩的大小关系）：
>   - **一个很大的葫芦形背包**，**下面圆鼓鼓、上面窄一点**，**比他的上身还大**，从**发顶附近**一直到**膝盖附近**，背在他背后（**画面左边**）；
>   - 主体是**米白色的布**，上面有**弯弯的青绿色鳞纹带**和**金橙色的细边**；**顶上一个青绿色鳞纹的盖子**，盖子下面一圈**棕红色的箍**；
>   - **一根粗粗的紫色绳子**绕在背包上，**两头从他肩膀上绕到胸前**：**他两只拳头握着的就是这两根紫色绳子**（附图 1、2）；
>   - 背包和他背之间有一个**棕色的木架子**。
> - **男孩照附图 6**（**能看见的地方逐格照它画**），**姿势和大小也照附图 6**：3/4 朝右站着、**两只拳头握在胸前**（现在握着背包的紫色绳子）、两脚稍分开站稳。**头的大小和附图 6 一样**（以后每个动作都要保持这个大小）。英雄联盟的渲染里他在抬头往上看，**这一点不要照**：脸照附图 6 平视右前方。
> - **火精灵**：附图 6 里他身后那个**圆滚滚的发光小火精灵**（**黄白色的芯、橙色的圈、深橙红的边、顶上两三簇小火苗、一张可爱的小脸：两只小黑眼睛和一个小嘴**），**样子和大小照附图 6**（约 **19 × 26 格**，算上火苗），和男孩一样密。现在他背后有了背包，火精灵改成**飘在背包顶的上方**（画面左上，**比背包顶高一点**），**和背包、男孩之间留 2 格以上的空隙**，不碰到任何东西。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**发顶到脚底约 570 px（95 格，和附图 6 一样高）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），发顶碰到附图 7 的浅灰线。附图 7 是现在的男孩的剪影（**不含火精灵，也还没有背包**），只看大小和位置；**背包加在他左边**，顶上可以和发顶差不多高；火精灵在背包上方。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（男孩连背包一圈，火精灵自己一圈）；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**两只眼睛、眉毛、嘴各自成块，不要糊成一团；肩垫、流苏、坠饰、背包的纹路、紫色绳子和火精灵的小脸都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（火精灵周围也不要光晕），也不要画黑色或彩色背景。两腿之间、手臂和身体之间、背包和身体之间的空隙也是透明的。
> - 不画特效（没有火球、火焰、营火、护盾、光圈、残影），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
> - **再从同一张成品图分出两层**（同样的画布和位置，不重画）：`milio-A-boy.png`（只有男孩和背包）、`milio-A-spirit.png`（只有火精灵）。
>
> - 交付：`outputs/milio-ppu/milio-A.png`、`milio-A-boy.png`、`milio-A-spirit.png`（都是 1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/milio-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/milio_ppu_done.zip`。

## 附图（在压缩包 `milio_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_milio_idle.png` | 英雄联盟里的米利欧（**背着背包**） | **背包的样子照它** |
| `refs/2_milio_head.png` | 头和肩膀的特写 | 紫色绳子从肩上绕到胸前、两只手握着绳子 |
| `refs/3_milio_back.png` | 从身后看 | 背包的背面、绳子怎么绕、木架子 |
| `refs/4_milio_splash.png` | 官方加载画面 | 气质和配色（火精灵飘在他肩膀上方、背包旁边） |
| `refs/5_milio_chibi.png` | 同一个英雄联盟模型换成本游戏的 Q 版比例（头 1.35 倍、腿 0.9 倍） | **背包和男孩的大小比例照它** |
| `refs/6_milio_now.png` | 他现在的造型原稿（6 倍：一格 = 6 像素，就是这次的格子） | **男孩的长相、衣服、颜色、姿势、大小照它；火精灵的样子照它**（它的位置要改） |
| `refs/7_layout.png` | 布局示意：现在的男孩（不含火精灵）在新画布上的剪影 | 画布上的大小、脚底的线（深灰）、**发顶要碰到的线（浅灰）** |
| `style/8_style_veigar.png` | 本包的维迦（8 倍，PPU 1.8） | **只看风格** |
| `style/9_style_seraphine.png` | 本包的萨勒芬妮（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_ezreal.png` | 本包的伊泽瑞尔（8 倍，PPU 2.19） | **只看风格** |

## 提示词：`milio-A.png`（+ 两层）

附图 1–10，顺序同上表（1 = 1_milio_idle.png, 2 = 2_milio_head.png, 3 = 3_milio_back.png, 4 = 4_milio_splash.png, 5 = 5_milio_chibi.png, 6 = 6_milio_now.png, 7 = 7_layout.png, 8 = 8_style_veigar.png, 9 = 9_style_seraphine.png, 10 = 10_style_ezreal.png）。

```text
10 attached images. Image 6 is THE BOY TO DRAW: the design his current game sprite was made from, shown 6x - each of its squares already 6 px, the grid of this picture: his face, his curly hair, his clothes, his colours, his pose, his size and his round fire spirit. What he lacks is HIS BACKPACK: League of Legends' Milio carries a big gourd-shaped backpack (the user: "the one we made has no gourd on his back"). Images 1-4 show League's Milio WITH his backpack - image 1 a 3D render of him, image 2 his head and shoulders close up, image 3 from behind, image 4 the official illustration. ADD THE BACKPACK, copied from images 1-3: a BIG GOURD-SHAPED BACKPACK on his back on the viewer's left - round and bulging at the bottom, narrower at the top, bigger than his upper body, from about the top of his hair down to about his knees; CREAM CANVAS with curving TEAL SCALE BANDS and thin GOLD-ORANGE trims, a TEAL SCALY CAP on top with a REDDISH-BROWN band under it; a THICK PURPLE ROPE wound round it whose two ends come over his shoulders to his chest - the two fists he holds in front of his chest GRIP THESE PURPLE ROPES; a brown wooden frame between the backpack and his back. Image 5 is the same 3D model in THIS GAME'S CHIBI PROPORTIONS: make the backpack as big against the boy as it is there. Image 7 is THIS picture's layout guide: the boy now (without his spirit, before the backpack) as a flat silhouette on the canvas - where he stands and how tall he is; the dark grey line marks THE SOLES, the light grey line THE TOP OF HIS HAIR; the backpack goes on his left (its top about as high as his hair). Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his hair is about 570 px (95 squares, as tall as image 6) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE BOY (image 6, square for square wherever he shows): the fluffy dark indigo curls; the two big amber eyes, the brows and the grin each a clear shape, never one muddy blob, looking ahead to the front-right as in image 6 (not up as in the 3D renders); the red tunic, the teal stand-up collar and the round teal pendant, the big puffed golden shoulder pads with their cream tassels, the diagonal teal sash with its gold buckle, the magenta pleated kilt, the red-and-teal ankle wraps, the brown sandals planted; both soles on one line. The head exactly as big as in image 6 (it keeps this size in every later animation). His two fists in front of his chest, now gripping the purple ropes.
THE FIRE SPIRIT (as image 6 draws it, as dense as the boy and as big as there - about 19 x 26 squares with its flame tips): the round glowing fireball buddy - a bright yellow-white core, an orange ring, a deep orange-red rim, two or three little flame tips curling up from its top, a cute face (two small dark eyes and a small happy mouth). With the backpack on his back it now FLOATS JUST ABOVE THE TOP OF THE BACKPACK, on the viewer's upper left, a little higher than the backpack, at least 2 squares clear of the backpack and of the boy, touching nothing.
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the boy with his backpack and another around the spirit; inside them every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (no fireballs, no flames, no campfire, no shields, no glow round the spirit, no afterimages), no background, no ground, no shadow, no text, no frame, no other characters.
Then, from the SAME finished picture (do not redraw), save two layers on the same 1024x1024 canvas at the same positions: milio-A-boy.png (the boy with his backpack only) and milio-A-spirit.png (the fire spirit only).
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **背后有英雄联盟的大葫芦形背包**（米白色、青绿色鳞纹、金边、青绿色盖子、紫色绳子、木架子），**大小照附图 5**；他的两只拳头握着紫色绳子。
- **男孩是附图 6 的男孩**（脸、卷发、衣服、颜色、头的大小都一样），平视右前方。
- 火精灵照附图 6 的样子和大小，飘在背包顶上方，和背包、男孩都留着空隙；两层（`milio-A-boy.png`、`milio-A-spirit.png`）和成品图位置一样。
- 发顶到脚底约 570 px（95 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/milio-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/milio_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- 这次是**照现在的男孩、加上英雄联盟的背包**（用户：「再补一个吧 米利欧 现在我们做的背后没有葫芦」）。
- 以前的渲染没有背包：poses.json 的 `hide_submeshes`（pose_ref 的 `--hide-submeshes`）把背包也藏了——`pose_ref.hidden_submeshes` 把蒙皮 bin 里所有"只由子网格名组成"的字符串都当成隐藏名单，而单独写着 `Backpack` 的材质替换（背包自己的贴图）也算一条。这次的渲染按名字只藏 bin 自己的 `initialSubmeshToHide`（字段哈希 0x80b7f78f：BuddyA / BuddyB 两个小火灵和它们的眼睛），再加上背包背面窗口里火精灵的脸（FireBuddy 的两只眼睛和嘴：英雄联盟里平时是显示的，但它们是逐帧动画贴图，pose_ref 会把整张图集都画上去），都在 `pack_milio_ppu.py` 的 HIDE 里；背包用它自己的贴图 `Milio_Base_Backpack_TX_CM`（SUBTEX）。**以后渲染他的动作参考也要这样，不能再用 `--hide-submeshes`。**
- **读原图，不读导出图**：原画、两层和 raw/ 放进 `assets/source/milio/hd/`（新文件名，别盖掉 front*.png），照 `tools/art/design_khazix_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空（平均色会把眼睛糊掉）；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的米利欧按游戏里的大小并排，给用户确认大小、脸、粗细、背包和火精灵的位置。
- 他的 1 倍精灵现在是 33 行（league_main 的 hd.rs 里 PPU 2.2，ppu_restyle 外描边 1）：新设计图按 33 行定 PPU；火精灵是单独一层（`rig_milio.py` 每帧放在他身后、飘动），新的一层照样用。
- **对齐点**：用设计图里的男孩和旧 idle_base 的剪影重叠来定（背包、火精灵不算）。
- 动作包照 `pack_khazix_actions.py`：跑步逐帧写明哪条腿撑地（第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放先按叠合法（`casts_*_hd.py --fits`），再按头（或别的不会变的部件）的大小校正到设计图那么大（第 6 批的 `b6_headzoom.py`；用户：「一定要注意模型不要变大变小」）；外描边 2 格（用户：「避免过度高清」）。
- 和这一批的另外几位在同一个 PR（claude/teemo-ppu）（用户：「最后重做提莫 菲兹 泽丽吧 泽丽虽然是高清帧了 但是模型我不满意」「佐伊的模型我也不满意 完全不像英雄联盟的佐伊」「一起改了」「再补一个吧 米利欧 现在我们做的背后没有葫芦」）。
