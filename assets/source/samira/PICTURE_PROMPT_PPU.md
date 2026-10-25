# 莎弥拉：照现在的精灵按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 莎弥拉现在游戏里的造型是 1 倍的（附图 6，用户自己的图附图 5 缩到游戏尺寸做的）：从身后大剑的剑柄顶到脚底 37 格。用户喜欢现在的造型，这次**照着它画密一点**：按 **PPU 2.2**，**每个游戏像素画成 2.2 格**，剑柄顶到脚底约 **81 格**。和安妮、阿狸、拉克丝一样的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 5）：姿势（**双手叉腰**）、身后大剑的角度和位置、身体比例（Q 版大头）、衣服、颜色**全部照现在的精灵**，不要换姿势、不要改比例；只是格子密了，把 1 倍画不下的细节画出来：
>   - 头发：**墨绿偏黑的长发**往后梳，有层次和高光；画面右边垂下一条**编起来的辫子**，辫子上**几个金色的环**；头上的金色发饰照附图 6。
>   - 脸：棕色皮肤；**近侧（画面左边）的眼睛戴眼罩**，一根**红色的带子**从眼罩斜着绕进头发；露出来的那只眼睛是**绿色**的，有高光和睫毛，眼神自信、带点挑衅的笑；小嘴、嘴唇偏红。
>   - 衣服：**深绿色的短上衣**，胸前斜挎**红色的布带**；露腰；**深绿色的长裤**，腰上**棕黑色的皮带**和金色扣；近侧胯边的**枪套里插着一把银色手枪**（照附图 6 的位置）。
>   - 靴子：深绿色长靴，**红色的靴口**，照附图 6。
>   - **大剑**：照附图 6 斜在她身后——**剑柄在画面左上方**（剑柄尾巴有**红色的穗子**），**银色的长剑身**从她背后斜着往右下方伸出去，剑尖在她右脚旁边；剑身有亮面和暗面。
> - **朝向**：和附图 6 一样，四分之三侧身，**脸和胸口朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用竖的 1024×1536**：**剑柄顶到脚底约 895 px（约 81 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），剑柄顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人和整把剑都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。附图 8–10 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间的空隙也是透明的。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/samira-ppu/samira-A.png`（1024×1536，**真透明背景**）；原始生成图原样放进 `outputs/samira-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/samira_ppu_done.zip`。

## 附图（在压缩包 `samira_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_samira_idle.png` | 英雄联盟里的莎弥拉待机，四分之三朝右（头放大到接近游戏精灵的比例） | 衣服、枪、剑的细节 |
| `refs/2_samira_head.png` | 头部特写 | 脸、发型 |
| `refs/3_samira_back.png` | 从身后看 | 头发、辫子 |
| `refs/4_samira_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_samira_user_picture.png` | 用户自己的莎弥拉图（她现在造型的来源） | **样子照它**：眼罩、红带、辫子、衣服、颜色 |
| `refs/6_samira_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，37 格高） | **要描的就是它**：姿势、大剑、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**剑柄顶要碰到的线（浅灰）** |
| `style/8_style_annie.png` | 本包的安妮（8 倍，PPU 2.2） | **只看风格** |
| `style/9_style_ahri.png` | 本包的阿狸（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_lux.png` | 本包的拉克丝（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`samira-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a gunslinger woman standing with her hands on her hips and a greatsword slanting behind her, shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions (a chibi, the big head), the same hands on hips, the same greatsword behind her at the same angle, the same costume and colours - only at a much finer pixel density, with the details the small sprite could not hold. Image 5 is the picture that sprite was made from: copy its look (the eyepatch and its red strap, the braid with gold rings, the clothes, the colours). Images 1-3 are 3D renders of the same character from the game (1 her idle - the clothes, the pistol, the sword; 2 her head close up - the face and the hair; 3 from behind - the hair and the braid). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is the ground where her soles stand, the light grey line is where the TOP OF THE SWORD'S HILT goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1536 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of the sword's hilt is about 895 px (about 81 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure and the whole sword inside the picture; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (as image 6, detailed after images 5 and 1-3): long DARK TEAL-BLACK hair swept back, layered with highlights, a BRAID hanging on the image right with GOLD RINGS on it, the gold hair ornaments of image 6. Brown skin; an EYEPATCH over the near eye (image left) with a RED STRAP running diagonally from it into the hair; the other eye GREEN with a highlight and lashes, a confident, daring smile; a small mouth with reddish lips. A DARK GREEN short top with a RED SASH across the chest; bare midriff; DARK GREEN trousers with a dark brown leather belt and gold buckle; a SILVER PISTOL in a holster on the near hip (where image 6 has it). Dark green high boots with RED CUFFS.
THE GREATSWORD (as image 6): behind her, its HILT at the upper LEFT with a RED TASSEL at the pommel, the long SILVER BLADE slanting down behind her to the lower right, its tip beside her far foot; the blade with a light and a dark side.
THE VIEW: 3/4 view FACING RIGHT as image 6: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her arms and body and between her legs are transparent.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1536、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势、大剑、比例、衣服、颜色和附图 6 一样**（样子细节照附图 5），只是更密、更细。
- 剑柄顶到脚底约 895 px（约 81 格）；两只脚底在同一条线上，脚底以下什么都没有。
- 眼罩和红带、绿色的眼睛、金环辫子、红色布带、银色手枪、红色靴口都在。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/samira-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/samira_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/samira/hd/`，照 `tools/art/design_gwen_hd.py` / `design_annie_hd.py` 按原图自己的格子读回；和安妮、阿狸、拉克丝、现在的莎弥拉按游戏里的大小并排，给用户确认大小、脸。
- 动作：照格温的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_gwen_actions.py`），再由 `casts_*_hd.py` 修到设计图上；**逐帧查枪和剑在哪只手**（和设计图、旧版一样），**跑步查左右脚有没有轮换、身体有没有起伏**。
- 查塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂剪影、待机和选人卡轮播、枪口和剑光特效的锚点、头像截取点、选人卡偏移等适配。
