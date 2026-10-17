# 贾克斯：重画 Q 版设计图（给 Codex 的提示词）

> 上一版贾克斯是正面对着镜头的，本包的英雄都是**四分之三侧身、脸朝右前方**（附图 8、9 的德莱厄斯和锐雯）。这次只画**一张**全身像素风设计图：同一个 Q 版贾克斯，衣服、颜色和上一版一样（附图 5），但身体和兜帽转向右前方，姿势照英雄联盟里的待机（附图 1）。动作帧不用画，我这边自己按英雄联盟的骨骼来摆。
> - **衣服和颜色照附图 5**（上一版设计，只是朝向不对）：深紫色兜帽和破边长袍；兜帽里是一张暗色面罩，上面**七个发光的暖黄色小眼点**（一圈六个加中间一个）；一边肩上一块大的**金铜色护肩**；棕色皮带和铜扣；深蓝灰色的裤子；金铜色的护腕和护腿；深棕色靴子。
> - **武器照附图 5 的路灯**：一根直的深色铁杆，顶上一个**金铜色六角灯笼，暖黄色的玻璃**，杆底一个小铜帽。灯杆是**笔直的**。
> - **朝向**（附图 1、6）：四分之三侧身，**兜帽和面罩转向右前方**，七个眼点在兜帽里偏右的位置；拿灯的**近侧手臂和腿在画面左边、颜色亮**，远侧在画面右边、稍暗；两只脚底在同一条地面线上，近侧那只脚低一点。
> - **姿势**（附图 1，英雄联盟里的待机；附图 6 是这个包以前的贾克斯，同样的拿法）：微微弓着身子站稳，近侧的手**横握灯杆**，灯杆从身后斜下来，**灯笼在他前方低处、靠近地面**（不要压住脚），远侧的手握拳垂在身侧。
> - **Q 版比例**：头（兜帽）大，约占身高的四成；身子短而壮，腿短。比例照附图 5。
> - **画布用横版 1536×1024**：**兜帽顶到脚底约 594 px，也就是约 54 格**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线）。灯杆、灯笼、手全在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。附图 8、9 是这个包里同样密度的英雄（8 倍放大，一格 = 一个像素），只看风格。
> - 不画特效、地面、影子。
> - 交付：`outputs/jax-picture/jax-A.png`（1536×1024 横版，**真透明背景**）；原始生成图原样放进 `outputs/jax-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/jax_picture_done.zip`。

## 附图（在压缩包 `jax_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_jax_idle.png` | 英雄联盟里的贾克斯待机（Q 版比例），四分之三朝右 | **朝向、姿势、拿灯的方式** |
| `refs/2_jax_side.png` | 同一帧的侧面（朝右） | 身体的转向、灯杆的角度 |
| `refs/3_jax_head.png` | 头部特写，四分之三朝右 | 兜帽和面罩转向右前方的样子 |
| `refs/4_jax_front.png` | 同一帧的正面 | 只看身体结构 |
| `refs/5_jax_costume.png` | 上一版设计（Q 版，**朝向不对**） | **衣服、颜色、灯、比例**照它 |
| `refs/6_jax_old_sprite.png` | 这个包以前的贾克斯（8 倍） | 朝向和拿灯的方式 |
| `refs/7_layout.png` | 布局示意（只看位置和大小） | 画布上的位置、脚底线（深灰） |
| `style/8_style_darius.png` | 本包的德莱厄斯（8 倍，同样密度） | **只看风格**和四分之三侧身的样子 |
| `style/9_style_riven.png` | 本包的锐雯（8 倍，同样密度） | **只看风格** |

## 提示词：`jax-A.png`

九张图都附上，顺序同上表。

```text
Nine attached images. Images 1-4 are 3D renders of a character from the game, with a big chibi head: a hooded fighter with a street lamp post as his weapon (1 his idle in 3/4 view facing right - the ANGLE, the POSE and how he holds the lamp in this picture; 2 the same from the side, facing right; 3 his head in 3/4 view facing right; 4 the same from the front - body construction only). Image 5 is our previous pixel-art design of him: copy its COSTUME, COLOURS, LAMP and CHIBI PROPORTIONS exactly - only its angle is wrong (it faces the camera). Image 6 is an older small sprite of him in this game: the facing and the lamp held low ahead. Image 7 is THIS picture's layout guide: where he goes, the dark grey line is the ground. Images 8-9 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at the same square density: copy their pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of him, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha). He is about 594 px (about 54 squares) from the top of his hood to the soles of his feet, the soles about 64 px above the bottom edge (the dark grey line of image 7); the lamp post, the lantern and the hands whole inside the picture, comfortable margins, nothing cut off; both soles on one ground line.
THE COSTUME (image 5): a deep PURPLE HOOD and a ragged purple robe; inside the hood a dark MASK with SEVEN small glowing warm-yellow eye dots (a ring of six and one in the middle); one big BRONZE-GOLD PAULDRON; brown leather belts with bronze buckles; dark navy-grey trousers; bronze bracers and greaves; dark brown boots. CHIBI proportions as image 5: a big hood about 40% of his height, a short stocky body, short legs.
THE LAMP (image 5): a STRAIGHT dark iron post, on top a bronze-gold hexagonal LANTERN with warm yellow glass, a small bronze cap at the foot. The post is perfectly straight.
THE VIEW: 3/4 view FACING RIGHT like images 1, 3, 8 and 9: the hood and the mask turned to the front-right, the seven eye dots on the right side inside the hood; the NEAR arm (holding the lamp) and the near leg on the image LEFT in full tone, the far ones on the image RIGHT a step darker; the near foot a little lower; both soles on one ground line.
THE POSE (image 1, his idle; image 6 holds it the same way): standing firm, a little crouched; the near hand holds the post ACROSS his body, the post coming down from behind him at a slant, the LANTERN AHEAD of him LOW near the ground (clear of his feet); the far hand a fist at his side.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, no stray single odd squares; purples for the hood and robe, navy for the trousers, bronze-gold for the pauldron, bracers and lantern, warm yellow only for the eye dots and the lantern glass; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1024 横版；灯杆、灯笼、手都在画面里。
- **四分之三侧身朝右前方**：兜帽和面罩转向右，七个眼点在兜帽里偏右；拿灯的近侧手和腿在画面左边、颜色亮。
- 衣服、颜色、灯、Q 版比例和附图 5 一样；灯杆笔直。
- 姿势：横握灯杆，灯笼在前方低处、不压脚；远侧手握拳。
- 兜帽顶到脚底约 594 px（约 54 格）；脚底在同一条线上；没有特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 画完后最后写 `outputs/jax-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/jax_picture_done.zip`，这样我这边才知道已经交付完。
