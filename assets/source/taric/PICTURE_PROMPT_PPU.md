# 塔里克：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 塔里克现在游戏里的造型是 1 倍的（附图 6）：头顶到脚底约 40 格，站得笔直，**近侧的手（画面左边）垂在身旁，握着他的银色双刃锤，锤头朝下、在脚边**，远侧的手臂（画面右边）是光着的，垂在身旁。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，头顶到脚底约 **60 格**，和李青、潘森、锐雯同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、身体比例、盔甲、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型把锤子往外伸，**不要照它的姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**棕色的长发**，从头顶往后披到肩上，一缕刘海垂在额前；**蓝色的眼睛**，浅肤色，方下巴。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 肩膀：**两块很大的银白色肩甲**，**上面各嵌一颗大大的蓝宝石**。
>   - 身体：敞开的领口露出胸口，**脖子上挂着一颗蓝宝石吊坠**；**一条蓝色的布带从肩膀斜着披下来**；**深棕色的皮衣**；**银色的腰带扣上嵌着紫色宝石**，腰带下垂着深蓝色的布；**背后一件深蓝色的披风**，从两腿后面露出来。
>   - 近侧的手（画面左边）：**深色的护臂**，手垂在身旁，**握着银色的双刃锤**：锤头是两片弯弯的银白色刃，中间嵌一颗**紫蓝色的宝石**，**锤头朝下、在脚边**。
>   - 远侧的手臂（画面右边）：**光着的胳膊**（浅肤色），**手腕上一圈深蓝色的护腕**，手垂在身旁。
>   - 腿：**深棕色的裤子**，**银灰色的护膝和护胫**，**深色的靴子**；两脚稍微分开站着。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **两只脚都踩在附图 7 的深灰线上**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**头顶到脚底约 660 px（约 60 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），头顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、两块肩甲和整把锤子都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；肩甲上的蓝宝石、吊坠、腰带上的紫宝石、锤头的两片刃和中间的宝石都清楚。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（宝石也不要发光晕），也不要画黑色或彩色背景。两腿之间、手臂和身体之间、锤子和腿之间的空隙也是透明的。
> - 不画特效（星光、护盾、光束等都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/taric-ppu/taric-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/taric-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/taric_ppu_done.zip`。

## 附图（在压缩包 `taric_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_taric_idle.png` | 英雄联盟里的塔里克待机，四分之三朝右（锤子往外伸，**姿势不要照它**） | 头发、肩甲、蓝布带、皮衣、腰带、披风、锤子的细节 |
| `refs/2_taric_head.png` | 头部特写 | 头发、脸、眼睛、吊坠、肩甲上的宝石 |
| `refs/3_taric_back.png` | 从身后看 | 长发、披风、肩甲、锤头 |
| `refs/4_taric_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_taric_first_design.png` | 他的设计图（就是附图 6 放大到 8 倍） | 头、盔甲、颜色 |
| `refs/6_taric_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 40 格高） | **要描的就是它**：姿势、比例、盔甲、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/8_style_leesin.png` | 本包的李青（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_pantheon.png` | 本包的潘森（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`taric-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a gem knight standing upright, long brown hair, big silver shoulder plates set with blue gems, his NEAR hand (image left) hanging at his side holding a silver double-bladed HAMMER with its head DOWN by his feet, his far arm (image right) BARE and hanging; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same upright pose, the same armour and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, the armour and the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - he holds the hammer out there, do NOT copy that pose (1 his idle - the hair, the shoulder plates, the blue sash, the coat, the belt, the cape, the hammer; 2 his head close up - the hair, the face, the eyes, the pendant, the gems on the shoulder plates; 3 from behind - the long hair, the cape, the shoulder plates, the hammer head). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is where his SOLES go, the light grey line is where the TOP OF HIS HEAD goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his head is about 660 px (about 60 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure, both shoulder plates and the whole hammer inside the picture; nothing at all below his soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): LONG BROWN HAIR falling back over his shoulders, a lock over the brow; BLUE EYES, fair skin, a square jaw - the eyes, the brows and the mouth each a clear shape, never one muddy blob. Two big SILVER-WHITE SHOULDER PLATES, each set with a big BLUE GEM. An open collar showing his chest with a BLUE GEM PENDANT on a cord; a BLUE SASH falling diagonally from one shoulder; a DARK BROWN LEATHER COAT; a SILVER BELT BUCKLE set with a VIOLET GEM, dark blue cloth hanging below it; a DARK NAVY CAPE behind him, showing behind his legs. The NEAR hand (image left) in a dark gauntlet hangs at his side holding the SILVER DOUBLE-BLADED HAMMER, its head DOWN by his feet: two curved silver-white blades with a VIOLET-BLUE GEM between them. The FAR arm (image right) BARE, fair skin, a DARK BLUE WRIST GUARD, the hand hanging at his side. Dark brown trousers, SILVER-GREY knee and shin guards, dark boots, feet a little apart. The gems clear shapes with no glow around them.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A broad, heroic build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between his legs, his arms and body and the hammer and his legs are transparent.
No effects (no starlight, no shields, no beams), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、比例、盔甲、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型伸出锤子的姿势**）：笔直站着、近侧的手垂着握锤、锤头朝下在脚边、远侧光着的手臂垂着；头的大小照附图 6。
- 头顶到脚底约 660 px（约 60 格）；两只脚踩在深灰线上，脚底以下什么都没有。
- 棕色长发、蓝眼睛、两块银白肩甲（蓝宝石）、蓝宝石吊坠、蓝布带、深棕皮衣、银腰带扣（紫宝石）、深蓝披风、深色护臂、银色双刃锤（紫蓝宝石）、光着的远侧手臂和深蓝护腕、深棕裤子、银灰护膝护胫和深色靴子都在；脸上各部分清楚，宝石没有光晕。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/taric-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/taric_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/taric/hd/`，照 `tools/art/design_zed_hd.py`（Codex 的格子均匀时用一张均匀网格逐格读，漂移时贴线读）读回；和李青、潘森、现在的塔里克按游戏里的大小并排，给用户确认大小、脸、粗细。
- **白色的东西**：肩甲和锤头接近白色。抠白底时被围住的白块只有四周是描边时才当背景（`casts_rengar_hd.figure`），读回后检查肩甲和锤头有没有被抠掉。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：动作包里写的每个部件（锤子在哪只手、锤头朝哪、光着的手臂、披风）都要在旧帧上确认过位置。
- 动作：照劫的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_zed_actions.py`），读回到设计图上（`casts_zed_hd.py`：每张的缩放取整个人面积和头部匹配的平均）；跑步一开始就逐帧写清腿怎么摆。他的 tag：idle、run、attack、attack_p（被动强化普攻）、skill、skill2、ult、hit、dead；没有烤进动作的特效（星光、护盾、光束是单独的特效条，`taric_fx_*`）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移。
