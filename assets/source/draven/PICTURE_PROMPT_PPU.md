# 德莱文：照现在的精灵按 PPU 2.2 重画设计图（给 Codex 的提示词）

> 德莱文现在游戏里的造型是 1 倍的（附图 6）：头顶到脚底约 35 格，两把旋转飞斧握在身体两侧、斧刃朝外。这次**照着它画密一点**：按 **PPU 2.2**，**每个游戏像素画成 2.2 格**，头顶到脚底约 **77 格**，和金克丝、安妮、拉克丝同样的密度（附图 8–10）。
> - **照附图 6 描**（细节看附图 5 和 1–3）：姿势（**两手各握一把飞斧，垂在身体两侧、斧刃朝外**，两腿分开站稳）、身体比例、衣服、颜色**全部照现在的精灵**，不要换姿势。只是格子密了，把 1 倍画不下的细节画出来：
>   - **体格要壮**：宽肩、粗壮的手臂和大腿、结实的胸肌和腰，**不要画成细长的身材**（另一位英雄这样重画后显得太细，用户不满意）。
>   - 头：**深红棕色的头发往后梳成一簇簇尖刺**，额头系着**金色的头箍，正中一颗青绿色的宝石**；浓密的深色八字胡；咧嘴笑、露出牙齿，眼神张狂得意。附图 6 头顶如果被切平了，按附图 5 把头发补完整。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大。
>   - 上身：**赤裸的肌肉胸膛**，胸前交叉的深色皮带（X 形）；两肩**白色和青绿色的护肩**（毛边）；手腕缠**红色的护腕**。
>   - 下身：腰间**红色的长布条**垂到膝盖、金色腰扣；深色长裤，小腿和膝盖上**银灰色的护甲片**；深色靴子。
>   - **两把飞斧**：照附图 6 握在两只手里——斧头是**银白色的弯刃（三叉形的旋转斧）**，带红色和金色的装饰，斧柄被手握住；近侧（画面左边）那把在左手外侧，远侧那把在右边腿旁。
> - **朝向**：和附图 6 一样，四分之三侧身，**脸和胸口朝右前方**；近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用横的 1536×1024**：**头顶到脚底约 847 px（约 77 格）**，脚底在离画布底边约 44 px 的地方（附图 7 的深灰线），头顶碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人和两把斧都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。**脸上的五官画清楚**：眼睛、胡子、牙齿各自成块，不要糊成一团。附图 8–10 是本包同样密度（PPU 2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。手臂和身体之间、两腿之间的空隙也是透明的。
> - 不画特效、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/draven-ppu/draven-A.png`（1536×1024，**真透明背景**）；原始生成图原样放进 `outputs/draven-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/draven_ppu_done.zip`。

## 附图（在压缩包 `draven_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_draven_idle.png` | 英雄联盟里的德莱文待机，四分之三朝右（头放大到接近游戏精灵的比例） | 衣服、护肩、斧子的细节 |
| `refs/2_draven_head.png` | 头部特写 | 脸、头发、胡子、头箍 |
| `refs/3_draven_back.png` | 从身后看 | 头发、护肩、布条 |
| `refs/4_draven_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_draven_first_design.png` | 他最早的设计图（远侧的斧子举过头顶，姿势不用照） | 头发、脸、斧子、衣服的细节 |
| `refs/6_draven_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 35 格高） | **要描的就是它**：姿势、两把斧、比例、衣服、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**头顶要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍，PPU 2.2） | **只看风格** |
| `style/9_style_annie.png` | 本包的安妮（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_lux.png` | 本包的拉克丝（8 倍，PPU 2.2） | **只看风格** |

## 提示词：`draven-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a small pixel-art game sprite of a muscular axe-wielding showman standing with his legs apart and a spinning throwing axe in each hand, held low at his sides with the blades out, shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same proportions, the same stance, the same two axes in the same places, the same costume and colours - only at a much finer pixel density, with the details the small sprite could not hold. Image 5 is his first design (its raised axe is NOT the pose): the detail of his hair, face, axes and clothes. Images 1-3 are 3D renders of the same character from the game (1 his idle - the clothes, the shoulder guards, the axes; 2 his head close up - the face, the hair, the moustache, the headband; 3 from behind). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is the ground where his soles stand, the light grey line is where the TOP OF HIS HAIR goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x at the same square density: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1536x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The top of his hair is about 847 px (about 77 squares) above his soles, the soles about 44 px above the bottom edge; the whole figure and both axes inside the picture; both soles on one ground line; nothing at all below his soles.
THE BUILD: STURDY and MUSCULAR - broad shoulders, thick arms and thighs, a solid chest and waist; NOT a slim, long-limbed figure. The head the size it has in image 6 (it keeps this size in every later animation) - do not enlarge it.
THE CHARACTER (as image 6, detailed after images 5 and 1-3): DARK RED-BROWN hair swept back in spikes (if image 6 cuts the top of the hair flat, complete it as image 5); a GOLD HEADBAND across the forehead with a TEAL GEM in the middle; a thick dark MOUSTACHE; a wide grin showing his teeth, cocky eyes - the eyes, moustache and teeth each a clear shape, never one muddy blob. A BARE MUSCULAR CHEST with dark leather straps crossing in an X; WHITE-AND-TEAL fur-trimmed SHOULDER GUARDS; RED WRIST WRAPS. A long RED CLOTH hanging from the waist to the knees with a gold buckle; dark trousers with SILVER-GREY ARMOUR PLATES on the knees and shins; dark boots.
THE AXES (as image 6): one in each hand, held low at his sides, the blades turned outwards - SILVER-WHITE curved three-pronged spinning blades with red and gold trim, the handle inside his fist; the near one (image left) out beside his near hand, the far one beside his far leg.
THE VIEW: 3/4 view FACING RIGHT as image 6: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between his arms and body and between his legs are transparent.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1536×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势、两把斧、比例、衣服、颜色和附图 6 一样**（细节照附图 5 和 1–3），只是更密、更细；**体格壮实**，头的大小照附图 6。
- 头顶到脚底约 847 px（约 77 格）；两只脚底在同一条线上，脚底以下什么都没有。
- 金色头箍和青绿宝石、八字胡、白青护肩、交叉皮带、红色护腕、红色长布条、银灰护甲、两把银白飞斧都在；脸上的眼睛、胡子、牙齿清楚。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/draven-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/draven_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/draven/hd/`，照 `tools/art/design_samira_hd.py` 按原图自己的格子读回；和金克丝、安妮、莎弥拉、现在的德莱文按游戏里的大小并排（**尺寸表 SIZES 要算进去**），给用户确认大小、脸、粗细。
- 动作：照莎弥拉的做法，Codex 照旧版同一帧整帧重画（`tools/art/pack_samira_actions.py`），再读回到设计图上；**动作包里写明头和设计图一样大**，交回后逐帧量头顶到下巴（莎弥拉的动作头小了一号，待机和动作之间头一大一小）；**逐帧查斧子在哪只手**，**跑步查左右脚轮换和起伏**。
- 降密度时脸保持原样（`ppu_restyle.py` 的 `look` + `look_keep`）；查塞拉斯、佛耶戈 / 妮蔻灵魂表、俄洛伊的灵魂剪影、待机和选人卡轮播、飞斧落点和特效锚点、头像截取点、选人卡偏移等适配。
