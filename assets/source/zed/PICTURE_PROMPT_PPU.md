# 劫：照现在的精灵按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 劫现在游戏里的造型是 1 倍的（附图 6）：背后手里剑的尖到脚底约 40 格，站得笔直，两条胳膊垂在身体两侧，**两只手腕上的钢刃朝下，贴着两条腿**。这次**照着它画密一点**：按 **PPU 1.5**，**每个游戏像素画成 1.5 格**，手里剑尖到脚底约 **60 格**，和李青、锐雯、奇亚娜同样的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是同一张精灵放大到 8 倍，细节看附图 1–3）：姿势、身体比例、盔甲、颜色**全部照现在的精灵**，不要换姿势（附图 1、3 的 3D 模型是弓着身子的，**不要照它的姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**深钢色的头盔**，有**金色的镶边**，**面甲上一道横缝里是两只发光的红眼睛**；头盔下面围着**红色的围巾 / 兜帽**。**头盔的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 背后：**一个很大的银色手里剑**背在背上，几个弯弯的尖从头盔后面往**上方和左上方**伸出来（附图 6 头顶上那些银白色的尖就是它，附图 3 从身后看得最清楚）。
>   - 身体：**两块很大的金色肩甲**；**深蓝黑色的钢甲**护着胸口和腰；**红色的布从胸口斜着垂到右边的腰下**，有**金色的镶边**。
>   - 手臂：两只胳膊垂在身体两侧，**金色的护腕**；每只手腕上有**两三把银色的长钢刃**，**刃尖朝下**，贴着大腿垂下来（画面左边一组、右边一组）。
>   - 腿：**深蓝黑色的裤子**，**钢灰色的护胫**和**钢靴**；两脚稍微分开站着。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**（红眼睛在头盔偏右的地方）；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **两只脚都踩在附图 7 的深灰线上**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**手里剑尖到脚底约 660 px（约 60 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），手里剑尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人、整个手里剑和四把钢刃都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**两只红眼睛各自成块、清楚；头盔的金边、肩甲、红布的金边清楚；每把钢刃是一条清楚的长条，刃和刃之间有空隙。** 附图 8–10 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**（红眼睛也不要发光晕），也不要画黑色或彩色背景。两腿之间、手臂和身体之间、钢刃和腿之间、手里剑的尖之间的空隙也是透明的。
> - 不画特效（影子分身、刀光、烟雾等都不要），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/zed-ppu/zed-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/zed-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/zed_ppu_done.zip`。

## 附图（在压缩包 `zed_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zed_idle.png` | 英雄联盟里的劫待机，四分之三朝右（弓着身子，**姿势不要照它**） | 头盔、手里剑、肩甲、红布、钢刃的细节 |
| `refs/2_zed_head.png` | 头部特写 | 头盔、金边、红眼睛、围巾、肩甲 |
| `refs/3_zed_back.png` | 从身后看 | 背上的手里剑、红布 |
| `refs/4_zed_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_zed_first_design.png` | 他的设计图（就是附图 6 放大到 8 倍） | 头盔、盔甲、颜色 |
| `refs/6_zed_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 40 格高） | **要描的就是它**：姿势、比例、盔甲、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**手里剑尖要碰到的线（浅灰）** |
| `style/8_style_leesin.png` | 本包的李青（8 倍，PPU 1.5） | **只看风格** |
| `style/9_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |
| `style/10_style_qiyana.png` | 本包的奇亚娜（8 倍，PPU 1.5） | **只看风格** |

## 提示词：`zed-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of an armoured ninja standing upright, both arms hanging at his sides, a set of long steel BLADES on each wrist pointing DOWN along his legs, a big steel SHURIKEN on his back with its curved points sticking up over his helmet; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same upright pose, the same armour and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is the same sprite enlarged: the helmet, the armour and the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - they crouch, do NOT copy their pose (1 his idle - the helmet, the shuriken, the shoulder plates, the red cloth, the blades; 2 his head close up - the helmet, its gold trim, the red eyes, the scarf; 3 from behind - the shuriken on his back, the red cloth). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is where his SOLES go, the light grey line is where the TOP POINT OF THE SHURIKEN goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top point of the shuriken is about 660 px (about 60 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure, the whole shuriken and all the blades inside the picture; nothing at all below his soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a DARK STEEL HELMET with GOLD TRIM, a horizontal visor slit with TWO GLOWING RED EYES, a RED SCARF / hood wrapped round the neck under it - the two eyes each a clear shape, no glow around them; a big SILVER SHURIKEN on his back, its curved points sticking out UP and UP-LEFT behind the helmet (the silver-white spikes over his head in image 6); two big GOLD SHOULDER PLATES; DARK NAVY-BLACK STEEL armour on the chest and waist; a RED CLOTH hanging diagonally from the chest down past the right hip, with GOLD trim. Both arms hang at his sides with GOLD BRACERS; on each wrist two or three long SILVER BLADES, POINTS DOWN, hanging along his thighs (one set on the image left, one on the right) - each blade a clear long strip with gaps between them. DARK NAVY trousers, STEEL-GREY greaves and STEEL BOOTS, feet a little apart.
The helmet the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A lean, upright build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right (the red eyes on the right of the helmet); the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between his legs, his arms and body, the blades and his legs, and between the shuriken's points are transparent.
No effects (no shadow clones, no slash trails, no smoke), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、比例、盔甲、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型弓身的姿势**）：笔直站着、两臂垂在两侧、腕刃朝下贴着腿；头盔的大小照附图 6。
- 手里剑尖到脚底约 660 px（约 60 格）；两只脚踩在深灰线上，脚底以下什么都没有。
- 深钢头盔（金边、两只红眼睛）、红围巾、背后的银色大手里剑、两块金色肩甲、深蓝黑钢甲、红布（金边）、金色护腕、每只手腕两三把朝下的银色钢刃、深蓝裤子、钢灰护胫和钢靴都在；眼睛清楚、没有光晕。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/zed-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zed_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/zed/hd/`，照 `tools/art/design_tristana_hd.py`（Codex 的格子均匀时用一张均匀网格逐格读，漂移时贴线读）读回；和李青、锐雯、现在的劫按游戏里的大小并排，给用户确认大小、脸、粗细。
- **白色的东西**：手里剑和钢刃的亮面接近白色。抠白底时被围住的白块只有四周是描边时才当背景（`casts_rengar_hd.figure`），读回后检查刃和手里剑有没有被抠掉。
- **描述每个部件前先对旧精灵**（狮子狗的教训）：动作包里写的每个部件（腕刃朝哪、手里剑的位置、红布）都要在旧帧上确认过位置。
- 动作：照崔丝塔娜的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_tristana_actions.py`），读回到设计图上（`casts_tristana_hd.py`：按头的大小找缩放）；跑步一开始就逐帧写清腿怎么摆。他的 tag：idle、run、attack、skill、skill2、skill_e、ult、hit、dead；没有烤进动作的特效（影子和刀光是单独的特效条，`zed_fx_*`）。
- 适配：塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移；影子分身（`zed_fx_sh_*`）和本体的大小要一起看。
