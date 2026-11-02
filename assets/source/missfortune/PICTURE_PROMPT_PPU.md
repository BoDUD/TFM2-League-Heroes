# 厄运小姐：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 厄运小姐现在游戏里的造型是 1 倍的（附图 6）：从帽顶到脚底约 38 格。她**正面偏右站着、两腿分开**；头上一顶**宽大的深蓝色三角海盗帽**，帽檐镶着**金边**、两边翘起尖角；**长长的红色卷发**从帽子下面披到肩上；**蓝色的眼睛**、浅肤色、红唇；上身**深蓝色短上衣**，**白色的大喇叭袖**，露着**腰腹**；腰上一条**金色的腰带**；**两把金色装饰的手枪**——**远侧（画面左边）的枪垂在大腿边、枪口朝下**，**近侧（画面右边）的枪端在腰间、枪口朝前**；**深蓝色的长靴**。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，帽顶到脚底约 **114 格**，和琴女、贝蕾亚差不多的密度（附图 9–10）。
> - **照附图 6 描**（附图 5 是她的设计图，放大的样子；细节看附图 1–3）：姿势、Q 版比例、帽子、头发、脸、衣服、两把枪、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的 Q 版头**（和附图 6 一样的比例），**宽大的深蓝三角帽**、金色帽边和两个尖角；**红色卷发**、刘海；**蓝色的眼睛**、眉毛、红唇各自成块。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 身体：深蓝色短上衣、**白色的大喇叭袖**、露出的腰腹（有明暗，不是一块白）、金色腰带、深蓝色长靴。
>   - 枪：**两把带握把和喇叭口的手枪**，枪身深色、**金色的装饰**；远侧的垂在大腿边、近侧的端在腰间，**手握着枪柄**，手指清楚。
> - **朝向**：和附图 6 一样，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。**枪的最低点也不能低于这条线。**
> - **画布用 1024×1024**：**帽顶到脚底约 684 px（约 114 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），帽顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、帽子和两把枪都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；帽子的金边、枪的金饰和手指都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间的空隙也是透明的。
> - 不画特效（枪口火光、子弹、硝烟都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/missfortune-ppu/missfortune-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/missfortune-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/missfortune_ppu_done.zip`。

## 附图（在压缩包 `missfortune_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_missfortune_idle.png` | 英雄联盟里的厄运小姐待机（写实比例，**姿势和比例不要照它**） | 帽子、头发、衣服、枪的细节 |
| `refs/2_missfortune_head.png` | 头部特写 | 帽子、头发、脸、眼睛 |
| `refs/3_missfortune_back.png` | 从身后看 | 帽子背面、头发、衣服 |
| `refs/4_missfortune_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_missfortune_first_design.png` | 她的设计图（放大） | 头、帽子、衣服、颜色 |
| `refs/6_missfortune_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 38 格高） | **要描的就是它**：姿势、Q 版比例、帽子、头发、衣服、枪、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**帽顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_sona.png` | 本包的琴女（8 倍，PPU 3.88） | **只看风格** |
| `style/10_style_briar.png` | 本包的贝蕾亚（8 倍，PPU 2.94） | **只看风格** |

## 提示词：`missfortune-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a pirate captain standing with her feet apart, turned a little to the right; a WIDE NAVY TRICORN HAT with GOLD trim and two upturned points; long wavy RED HAIR falling to her shoulders, a fringe; BLUE EYES, fair skin, red lips; a short NAVY TOP with big WHITE BELL SLEEVES and a bare midriff; a GOLD BELT; TWO PISTOLS with gold fittings, flared muzzles and grips - the FAR one (image left) hanging by her thigh, muzzle down, the NEAR one (image right) held at her waist, muzzle forward; tall NAVY BOOTS; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same hat, hair, outfit, pistols and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is her first design, enlarged. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 her idle - the hat, the hair, the outfit, the pistols; 2 her head close up - the hat, the hair, the face; 3 from behind - the hat, the hair, the outfit). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF THE HAT goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of the hat is about 684 px (about 114 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, the hat and both pistols inside the picture; nothing at all below the soles (the pistols end above the soles' line). Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG CHIBI HEAD as in image 6 under the WIDE NAVY TRICORN, its gold trim and two upturned points crisp; long wavy RED HAIR with a fringe; BLUE EYES, the brows and the red lips each a clear shape, never one muddy blob. A short navy top, big WHITE BELL SLEEVES, a bare midriff shaded (never one flat white patch), a gold belt, tall navy boots. TWO PISTOLS with dark barrels, gold fittings, flared muzzles and grips, her hands round the grips with readable fingers: the far one hanging by her thigh, muzzle down; the near one at her waist, muzzle forward.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it.
THE VIEW: as image 6, turned a little to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the arms and the body are transparent.
No effects (no muzzle flash, no bullets, no smoke), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、帽子、头发、衣服、两把枪、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：远侧的枪垂在大腿边、近侧的枪端在腰间；头的大小照附图 6。
- 帽顶到脚底约 684 px（约 114 格）；脚底碰到深灰线，下面什么都没有。
- 深蓝三角帽和金边、红色卷发、蓝眼睛和红唇、白色喇叭袖、深蓝上衣和腰腹、金腰带、两把金饰手枪、深蓝长靴都在；脸上各部分清楚。
- **每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/missfortune-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/missfortune_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/missfortune/hd/`，照 `tools/art/design_talon_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸用均匀格子读；几种 PPU 给用户选）读回；和泰隆、贝蕾亚、琴女、现在的厄运小姐按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把两把枪算进“两脚中点”）。
- 动作：她的 tag：idle 28、run 8、attack 6、skill 6、skill2 6、ult 8、hit 2、dead 7、idle_base 8、bp 54（`hero_reels.json`：待机 = attack 2–5 + skill 1–2）；旧版的逐帧补丁在 `assets/source/missfortune/modelfix/`（`tools/art/fix_missfortune_model.py`），重做后不再用。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移、目标标记附加包。和泰隆在同一个 PR（claude/talon-ppu）。
