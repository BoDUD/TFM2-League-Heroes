# 诺手：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 诺手现在游戏里的造型是 1 倍的：从斧柄顶的圆环到脚底只有 42 格，甲片、脸和斧头的细节都挤在一起（附图 7）。这次和剑姬、青钢影一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从斧柄顶的圆环到脚底约 **63 格**，头发顶到脚底约 51 格，细节更清楚。这次只画**一张**全身设计图，动作帧不用画，我这边按英雄联盟的骨骼来摆。
> - **比例照现在的游戏精灵（附图 7）**：魁梧的战士，头（连头发）约占身高的三分之一，肩宽、腿短而结实；不要更高更瘦，也不要更矮。**斧头的大小和长度也照附图 7**。
> - **衣服、颜色照附图 6**（之前定下的诺手造型）：
>   - 头：深棕色往后竖起的尖短发，鬓角剃短；严肃的脸，粗眉、紧闭的嘴；**两只眼睛一样高**（远侧那只可以窄一点）。
>   - 身体：深钢灰色的板甲，每块甲片有银白色的亮边；**近侧肩膀一块很大的圆形肩甲**（带铆钉），远侧肩甲小一些；胸口和腰间露出深红色的布；腰前一条长长的深红前摆，背后深红披风，从两腿之间和身后露出来。
>   - 手：钢甲手套。
>   - 腿：钢灰色腿甲、银边护膝，黑色靴子。
>   - **斧头**：近侧手（画面左边）握着一根竖直的深色长斧柄，斧柄顶端一个银色圆环（高过肩膀），斧头朝下立在脚边：两片银灰色的大月牙斧刃，内侧一圈深红。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。**近侧（画面左边）的手臂、肩甲和腿颜色亮**，远侧（画面右边）稍暗。
> - **姿势**（附图 1，英雄联盟里的待机，也是现在游戏精灵的姿势）：站稳，近侧手握着竖直的斧柄、斧头立在脚边，远侧手握拳垂在身侧；两腿略分开，两只脚底在同一条地面线上。
> - **画布用方形 1024×1024**：**斧柄顶的圆环到脚底约 693 px，也就是约 63 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），圆环顶碰到附图 8 的浅灰线；人的位置和大小照附图 8 的剪影。整个人和整把斧头都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。钢甲要有清楚的亮边和暗面，不要糊成一团灰；深红布要亮、成块；斧刃的亮面要清楚。附图 9–11 是本包同样密度（PPU 1.5）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也**不要画黑色或彩色背景**（上次剑姬的图是黑底加光晕，要我这边抠图）。
> - 不画特效、地面、影子。
> - 交付：`outputs/darius-ppu/darius-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/darius-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/darius_ppu_done.zip`。

## 附图（在压缩包 `darius_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_darius_idle.png` | 英雄联盟里的诺手待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势** |
| `refs/2_darius_side.png` | 同一帧的侧面（朝右） | 肩甲、披风、斧头的侧面 |
| `refs/3_darius_head.png` | 头部特写，四分之三朝右 | 脸、发型 |
| `refs/4_darius_axe.png` | 同一帧，握斧的手和斧头特写 | **手套、斧柄、斧刃** |
| `refs/5_darius_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_darius_picture.png` | 之前定下的诺手造型（8 倍） | **衣服、颜色、斧头照它** |
| `refs/7_darius_now.png` | 他现在的游戏精灵（8 倍，1 倍密度，42 格高） | **比例、身材、朝向、斧头大小** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影（只看位置和大小） | 画布上的位置、脚底线（深灰）、**圆环顶要碰到的线（浅灰）** |
| `style/9_style_jax.png` | 本包的贾克斯（8 倍，PPU 1.5，同样用这个方法重画的） | **只看风格** |
| `style/10_style_xinzhao.png` | 本包的赵信（8 倍，PPU 1.5） | **只看风格**：甲片、亮边、男性的脸 |
| `style/11_style_fiora.png` | 本包的剑姬（8 倍，PPU 1.5，刚用这个方法重画的） | **只看风格** |

## 提示词：`darius-A.png`

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (his head enlarged toward a game sprite's proportions): a big armoured warrior with a huge axe (1 his idle in 3/4 view facing right - the ANGLE and the POSE for this picture; 2 the same from the side, facing right: the shoulder plates, the cape and the axe; 3 his head in 3/4 view facing right: the face and the spiky hair; 4 the same frame close on his axe hand and the axe: the gauntlet, the shaft, the two crescent blades). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved pixel picture of him (8x): copy its COSTUME, COLOURS and AXE. Image 7 is his small game sprite now, shown 8x: copy its PROPORTIONS (the head with the hair about a THIRD of his height, broad shoulders, short strong legs), its build, its facing and the SIZE of the axe. Image 8 is THIS picture's layout guide: his sprite now as a flat silhouette at the new size - where he goes and how big; the dark grey line is the ground where his soles stand, the light grey line is where the TOP OF THE AXE'S RING goes. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the SAME square density: copy their pixel-art look and their 3/4 front-right view (9 a fighter redrawn the same way, 10 armour plates with lit edges and a male face, 11 the latest one redrawn this way).
Create ONE pixel-art picture of him, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). He is about 693 px (about 63 squares) from the top of the axe's ring to his soles, the soles about 64 px above the bottom edge (the dark grey line of image 8); his place and size as the silhouette of image 8; the whole figure and the whole axe inside the picture with margins, nothing cut off; both soles on one ground line.
THE CHARACTER (image 6): a grim, powerful general. HEAD: short spiky DARK BROWN hair swept up and back, shaved sides, a stern face with heavy brows and a closed mouth, the two eyes at the same height. BODY: DARK STEEL-GREY plate armour, every plate with a SILVER-WHITE lit edge; a very big ROUND riveted shoulder plate on the NEAR shoulder, a smaller one on the far shoulder; DEEP CRIMSON cloth at the chest and waist, a long crimson front tabard and a crimson cape behind him showing between and behind the legs. ARMS: steel gauntlets. LEGS: steel-grey greaves with silver-edged knee guards, black boots. THE AXE: held in the NEAR hand (image left) by a long dark UPRIGHT shaft with a silver RING on its top end (higher than his shoulder), the axe head DOWN at his feet: two big silver-grey CRESCENT blades with a crimson inner edge.
PROPORTIONS (image 7): the head with the hair about a THIRD of his height, broad and heavy - NOT taller or thinner, NOT shorter; the axe as big as in image 7.
THE VIEW: 3/4 view FACING RIGHT like images 1, 3 and 10: the face and the chest turned to the front-right; the NEAR arm, shoulder plate and leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker.
THE POSE (image 1): standing firm, the near hand gripping the upright axe shaft with the axe head standing by his feet, the far hand a fist at his side; the legs a little apart, both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the steel plates with clear LIT EDGES and dark faces so they never turn into one grey mass, the crimson cloth bright and solid, the axe blades with clear highlights, the hair dark brown with lighter strands, the skin warm tan; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景，**每个像素透明度只有 0 或 255，没有黑底、没有光晕**；1024×1024；整个人和整把斧头都在画面里。
- **比例照附图 7**：头约占身高三分之一，魁梧；斧头和附图 7 一样大。
- **四分之三侧身朝右前方**：脸和胸口朝右，两只眼睛一样高；近侧手臂、大肩甲和腿在画面左边、颜色亮。
- 衣服、颜色和附图 6 一样：深棕尖发、钢灰板甲带银亮边、深红布和披风、竖直斧柄顶上的银环、朝下的双月牙斧刃。
- 斧柄顶的圆环到脚底约 693 px（约 63 格），两只脚底在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/darius-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/darius_ppu_done.zip`，这样我这边才知道已经交付完。

## Claude 收到后（给 Claude 看）

- 原画和 raw/ 放进 `assets/source/darius/hd/`，照 `tools/art/design_fiora_hd.py` 读回：**按整张图拟合一个格距和相位**（不要用 regrid.py 逐格找边，剑姬那次脸碎了），背景若不透明先沿描边抠图；缩行时整个头不删；眼睛、嘴照原样，不要自作主张改（用户：「你不要缺失像素啊」）；和贾克斯、赵信、剑姬、现在的诺手按游戏里的大小并排，给用户确认大小和 PPU（不超过 1.5）。
- 定下后照 `tools/art/rig_fiora_hd.py` 摆动作：手臂和斧头只做无损的原样 / 镜像 / 直角转（斧头有斧刃，不能像剑身那样重画）；迈步、弓步的腿按英雄联盟每帧的骨骼画，粗细固定、颜色取设计稿腿的原色，护膝和靴子原样贴上（不要让 Codex 画腿：「腿部变形了吧？」）。做完动作给用户看带特效的演示动图，不要只发空挥。然后 ppu_restyle / ppu_hd / hd.rs、league.dll 版本、头像点、选人卡，开 PR。
