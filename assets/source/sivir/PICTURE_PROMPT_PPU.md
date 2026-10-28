# 希维尔：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 希维尔现在游戏里的造型是 1 倍的（附图 6）：头顶到脚底约 36 格，压低身子、两腿大大分开地站着，**近侧的手（画面左边）在腰旁握着一把很大的金色十字回旋刃**，**远侧的手（画面右边）戴着棕色皮手套、张开往右伸**。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，头顶到脚底约 **54 格**，和奇亚娜、锐雯、李青同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**深蓝黑色的长发**，很多，**往后（画面左边）甩出去**，一缕一缕分得清；头顶一个**金色的头冠**，额前一颗**青绿色的宝石**；**脸**是小麦色的皮肤，朝画面右前方，**青绿色的眼睛**、黑眉毛、**红色的嘴唇**；脖子上一条**米白色的围巾**。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**金色的肩甲和胸甲**，露出小麦色的**腰腹**；腰上一条**金色的腰带**，正中一颗**青绿色的宝石**；身前和两边垂下**深蓝色的布片**，镶金边。
>   - 武器：**近侧的手（画面左边）**放在腰旁，握着她的**十字回旋刃**——很大（差不多有她半个身子高），**金色的四片弯刃**拼成十字，刃上有**米白色的亮边**和**青绿色、红色的宝石**，竖着立在她身体左边。
>   - 远侧的手（画面右边）：手臂往右伸直，**手腕上金色的护腕**，**手上戴棕色的皮手套**，手张开。
>   - 下身：**淡紫灰色的紧身裤**，两腿大大分开、膝盖弯曲；**金色的护膝和护腿**；**棕色的靴子**。
> - **朝向**：和附图 6 一样，四分之三侧身，**脸朝画面右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **两只脚都踩在附图 7 的深灰线上**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**头顶到脚底约 594 px（约 54 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），头顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、头发和回旋刃都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的眼睛、嘴、额前的宝石各自成块，不要糊成一团；头发一缕一缕分得清；回旋刃的四片刃和宝石清楚。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间、回旋刃中间的空洞也是透明的。
> - 不画特效（刀光、护盾、金色的光等都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/sivir-ppu/sivir-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/sivir-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/sivir_ppu_done.zip`。

## 附图（在压缩包 `sivir_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sivir_idle.png` | 英雄联盟里的希维尔待机，四分之三朝右（头放大到接近游戏精灵的比例） | 头发、头冠、盔甲、回旋刃的细节 |
| `refs/2_sivir_head.png` | 头部特写 | 头冠和宝石、脸、围巾 |
| `refs/3_sivir_back.png` | 从身后看 | 头发、腰带、布片 |
| `refs/4_sivir_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_sivir_first_design.png` | 她的设计图（就是附图 6 放大到 8 倍） | 头、衣服、颜色 |
| `refs/6_sivir_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，约 36 格高） | **要描的就是它**：姿势、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/8_style_qiyana.png` | 本包的奇亚娜（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_leesin.png` | 本包的李青（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`sivir-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a desert warrior woman in a low, wide stance - legs far apart, knees bent, both feet on the ground - her NEAR hand (image left) by her hip gripping a huge golden cross-shaped throwing blade (the Chakram) standing upright at her side, her FAR hand (image right) reaching out to the right, open, in a brown leather glove; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same pose, the same costume and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the head, clothes and colours. Images 1-3 are 3D renders of the same character from the game (1 her idle - the hair, the crown, the armour, the Chakram; 2 her head close up - the crown and its gem, the face, the scarf; 3 from behind - the hair, the belt, the cloth panels). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big she is and where she stands; the dark grey line is where her SOLES go, the light grey line is where the TOP OF HER HEAD goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of her head is about 594 px (about 54 squares) above her soles, the soles about 64 px above the bottom edge; the whole figure, all of her hair and the whole Chakram inside the picture; nothing at all below her soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): LONG DARK NAVY-BLACK HAIR, a big mass swept BACK to the image LEFT, its locks readable; a GOLD CROWN on her head with a TEAL GEM at the brow; a sun-tanned face turned to the front-right, TEAL EYES, dark brows, RED LIPS - the eyes, the lips and the gem each a clear shape, never one muddy blob; a CREAM SCARF round her neck. GOLD SHOULDER PLATES and a gold breastplate, a BARE MIDRIFF, a GOLD BELT with a TEAL GEM in the middle, DARK NAVY CLOTH PANELS with gold trim hanging in front and at the sides. The NEAR hand (image left) by her hip holds THE CHAKRAM: huge (about half her height), four curved GOLD blades in a cross, CREAM highlights on the edges, TEAL and RED gems, upright at her left side, a hole in its middle. The FAR arm (image right) stretched out to the right, a GOLD BRACER at the wrist, the hand open in a BROWN LEATHER GLOVE. PALE MAUVE-GREY LEGGINGS, legs wide apart, knees bent, GOLD KNEE AND SHIN GUARDS, BROWN BOOTS.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. An athletic figure, as image 6.
THE VIEW: 3/4 view as image 6: the face to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between her arms and body, between her legs and the Chakram's hole are transparent.
No effects (no blade trails, no spell shield, no golden glow), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、比例、衣服、颜色和附图 6 一样**（细节照附图 1–3）：压低的大开步、近侧手在腰旁握着竖立的十字回旋刃、远侧手戴棕手套往右伸；头的大小照附图 6。
- 头顶到脚底约 594 px（约 54 格）；两只脚踩在深灰线上，脚底以下什么都没有。
- 往后甩的深蓝黑长发、金头冠和青绿宝石、青绿眼睛、红唇、米白围巾、金肩甲和胸甲、露出的腰腹、金腰带和青绿宝石、深蓝布片、十字回旋刃（四片金刃、米白亮边、青绿和红宝石）、金护腕、棕手套、淡紫灰紧身裤、金护膝护腿、棕靴都在；脸上各部分清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/sivir-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sivir_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/sivir/hd/`，照 `tools/art/design_akali_hd.py`（原图自己的格子；Codex 的格子均匀时用一张均匀网格逐格读）读回；和奇亚娜、锐雯、现在的希维尔按游戏里的大小并排，给用户确认大小、脸、粗细。
- **白色的东西**：回旋刃的米白亮边、围巾是浅色。抠白底时被围住的白块只有四周是描边时才当背景（`casts_rengar_hd.figure`），读回后检查有没有被抠掉。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：动作包里写的每个部件（哪只手握回旋刃、头发甩的方向、手套在哪只手）都要在旧帧上确认过位置。
- 动作：照阿卡丽的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_akali_actions.py`），读回到设计图上（`casts_akali_hd.py`：按头的大小找缩放）；跑步逐帧写出哪只脚在前、要有换步帧。她的 tag：idle、run、attack（`attack_fx1` 是烤了特效的副本）、skill（Q 掷出）、skill_wait、skill_catch（`skill_catch_fx1`）、skill2、ult、hit、dead；`assets/source/native/sivir_bake.json` 照旧烤特效。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、回旋刃的出手点、头像截取点、选人卡偏移。
