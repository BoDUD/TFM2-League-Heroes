# 佛耶戈：照现在的精灵按 PPU 3 重画设计图（给 Codex 的提示词）

> 佛耶戈现在游戏里的造型是 1 倍的（附图 6）：从剑尖到脚底约 47 格。他**面朝右站着，两脚分开**；**白色的头发**，头上戴着**一圈青绿色水晶尖刺的王冠**；**苍白的皮肤**，**眼睛发着青绿色的光**；身上是**敞开的深色板甲**（深靛蓝到近黑，**钢灰色的边**），**胸口露出来**，腰上一条**暗红色的腰带**；**巨大的青绿色水晶大剑扛在肩上**：**剑柄和十字护手**（青绿水晶、带尖钩）在**画面左边**、他头旁边，他的手在那里握着，**剑身从他头后面斜着伸向画面右上方**，剑尖是整个人的最高点；**深色铠甲的腿**，护膝上有尖刺，靴子深色。这次**照着它画密一点**：按 **PPU 3**，**每个游戏像素画成 3 格**，剑尖到脚底约 **141 格**，和金克丝、贝蕾亚、锤石差不多的密度（附图 8–10）。
> - **照附图 6 描**（附图 5 是他的设计图，细节看附图 1–3）：姿势、Q 版比例、王冠、铠甲、大剑、颜色**全部照现在的精灵**，不要换姿势（附图 1 的 3D 模型是写实比例，**不要照它的比例和姿势**，只看细节）。只是格子密了，把 1 倍画不下的细节画出来：
>   - 头：**大大的头**（和附图 6 一样的比例），**白头发**和**青绿水晶王冠的尖刺**清清楚楚；脸是**苍白的**：**发青绿光的眼睛、眉、嘴各自成块**，表情阴郁、执拗。**头的大小就是以后每个动作都要保持的大小**，按附图 6 的比例画，不要放大也不要缩小。
>   - 上身：**敞开的深色板甲**、**钢灰色的甲边**、露出的苍白胸口、**暗红腰带**。
>   - 剑：**很大、完整、笔直的青绿水晶大剑**：剑柄、带尖钩的十字护手、剑身中线和亮面暗面分清楚，**扛在肩上的角度和大小照附图 6**；握剑的手和手指清楚。
>   - 腿：**深色铠甲的腿**，护膝的尖刺，两脚分开站稳，深色靴子。
> - **朝向**：和附图 6 一样，四分之三侧身，**朝画面右边**；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**剑尖到脚底约 846 px（约 141 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），剑尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人和整把大剑都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴各自成块，不要糊成一团；王冠尖刺、护手尖钩、手指和甲边都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、剑和身体之间的空隙也是透明的。
> - 不画特效（黑雾、灵魂、剑光都不要），**眼睛和水晶的青光只画在它们身上，不往外发光**；不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/viego-ppu/viego-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/viego-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/viego_ppu_done.zip`。

## 附图（在压缩包 `viego_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_viego_idle.png` | 英雄联盟里的佛耶戈待机，四分之三朝右（写实比例，**姿势和比例不要照它**） | 王冠、铠甲、腰带、大剑的细节 |
| `refs/2_viego_head.png` | 头部特写 | 白头发、水晶王冠、大剑的护手 |
| `refs/3_viego_back.png` | 从身后看 | 铠甲背面、大剑扛在肩上的样子 |
| `refs/4_viego_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/5_viego_first_design.png` | 他最早的设计图（8 倍） | 王冠、铠甲、大剑、颜色 |
| `refs/6_viego_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，约 47 格高） | **要描的就是它**：姿势、Q 版比例、王冠、铠甲、大剑、颜色 |
| `refs/7_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**剑尖要碰到的线（浅灰）** |
| `style/8_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格** |
| `style/9_style_briar.png` | 本包的贝蕾亚（8 倍，PPU 2.94） | **只看风格** |
| `style/10_style_thresh.png` | 本包的锤石（8 倍，PPU 2.48） | **只看风格** |

## 提示词：`viego-A.png`

附图 1–10，顺序同上表。

```text
Ten attached images. Image 6 is THE picture to trace: a pixel-art game sprite of a ruined king standing with his feet apart, turned to the viewer's right - WHITE HAIR under a CROWN of TEAL CRYSTAL SPIKES; PALE skin, softly GLOWING TEAL EYES; OPEN DARK PLATE ARMOUR, deep indigo to near-black with STEEL-GREY edges, his pale chest bare, a DARK RED SASH at his waist; a HUGE TEAL CRYSTAL GREATSWORD RESTING ON HIS SHOULDER - its hilt and hooked crystal CROSSGUARD at the image's LEFT beside his head, where his hand grips it, its long BLADE slanting up behind his head to the image's UPPER RIGHT, the sword's tip the highest point of the picture; dark armoured legs with spiked knee guards and dark boots; shown 8x (every square one pixel). Redraw EXACTLY that character in EXACTLY that pose - the same chibi proportions, the same stance, the same crown, armour, greatsword and colours - only at a finer pixel density, with the details the small sprite could not hold. Image 5 is his first design, enlarged: the crown, the armour, the sword, the colours. Images 1-3 are 3D renders of the same character from the game for the DETAILS ONLY - realistic proportions and a different pose, do NOT copy them (1 his idle - the crown, the armour, the sash, the greatsword; 2 his head close up - the white hair, the crystal crown, the sword's crossguard; 3 from behind - the back of the armour, the sword on his shoulder). Image 4 is the official illustration: the mood and the colours. Image 7 is THIS picture's layout guide: the sprite now as a flat silhouette at the new size - how big he is and where he stands; the dark grey line is where his SOLES go, the light grey line is where the SWORD'S TIP goes. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The sword's tip is about 846 px (about 141 squares) above his soles, the soles about 64 px above the bottom edge; the whole figure and the whole greatsword inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (as image 6, detailed after images 1-3): a BIG HEAD as in image 6 with its white hair and the TEAL CRYSTAL CROWN's spikes crisp; the PALE FACE - the glowing teal eyes, the brows and the mouth each a clear shape, never one muddy blob; a brooding, obsessive look. The open dark plate armour with its steel-grey edges, the bare pale chest, the dark red sash. The GREATSWORD as large and at the same angle as in image 6, whole and straight: the hilt, the hooked crystal crossguard, the blade's ridge and its light and shadow faces; the gripping hand and fingers readable. Dark armoured legs, the spiked knee guards, the feet apart and planted, dark boots; both soles on one line.
The head the size it has in image 6 (it keeps this size in every later animation) - neither enlarge nor shrink it. A lean build, as image 6.
THE VIEW: 3/4 view as image 6, turned to the viewer's right; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps between the legs and between the sword and the body are transparent.
No effects (no black mist, no souls, no sword glow; the teal glow stays inside the eyes and the crystal), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **姿势、Q 版比例、王冠、铠甲、大剑、颜色和附图 6 一样**（细节照附图 1–3，但**不照 3D 模型的比例和姿势**）：面朝右、两脚分开站、大剑扛在肩上（剑柄护手在画面左边头旁、剑身斜伸向右上）；头的大小照附图 6。
- 剑尖到脚底约 846 px（约 141 格）；脚底碰到深灰线，下面什么都没有。
- 白头发和青绿水晶王冠、苍白的脸、发青绿光的眼睛、敞开的深色板甲和钢灰甲边、暗红腰带、青绿水晶大剑和带尖钩的护手、深色铠甲腿和护膝尖刺都在；脸上各部分清楚；青光不往外发。
- **每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/viego-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/viego_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/viego/hd/`，照 `tools/art/design_senna_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸按均匀格子读（FACES）；调色板 64 色；几种 PPU 给用户选）读回；和金克丝、贝蕾亚、锤石、现在的佛耶戈按游戏里的大小并排，给用户确认大小、脸、粗细。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定（别把大剑算进“两脚中点”）。
- **描述每个部件前先对旧精灵**：剑怎么扛、怎么挥，腿怎么站；跑步每一帧写明哪条腿撑地（泰隆和赛娜的教训）。
- 动作：他的 tag：idle 20、run 8、attack 6、skill 6、skill2 7、ult 8、possess 4、hit 2、dead 8、idle_base 8、bp 47（`hero_reels.json`：待机 = attack 0–1 + ult 4–5）。
- 适配：**佛耶戈附身（`league_viego_soul` 的灵魂表、possess 动作）**、塞拉斯、妮蔻灵魂表、俄洛伊的灵魂、待机和选人卡轮播、头像截取点、选人卡偏移。和赛娜在同一个 PR（claude/senna-ppu）。
