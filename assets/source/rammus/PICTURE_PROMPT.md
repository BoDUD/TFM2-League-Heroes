# 披甲龙龟 拉莫斯：第 0 步，先画像素风原图（给 Codex 的提示词）

> 拉莫斯是一只**矮胖的犰狳 / 乌龟样的怪兽**：背上一个**巨大的拱形甲壳**，甲壳由**橙金色的鳞片甲板**拼成，几条**深棕色的皮带**把甲板箍在一起；甲壳的脊上竖着几根**又高又尖的浅黄色锥形尖刺**（最高的在背中间），甲壳边缘一圈**小一些的尖刺**向外伸。甲壳前缘像一顶**帽檐**，下面探出一个**小小的绿色乌龟头**，两只**发光的红橙色眼睛**。四肢是**青绿色、带深绿色斑点的鳞皮**，手臂很长、垂到地面附近，手和脚上是**米白色的爪子**。肚子是**黄褐色**的，上面斜挎着一条**暗红色的皮质挽具**，挽具上钉着**灰色的钢钉**（肚子下面一根大钢刺朝下）。请 Codex 画**两张全身像**（同一个拉莫斯，长相、颜色、**格子大小**都一样）：
> - **A：英雄联盟里的待机**（附图 1、2、8a）。3/4 正面朝右：甲壳拱在背上和头顶，**头从甲壳前缘下面探出来朝右前方**，两只长手臂垂在身体两侧，爪子快到地面，两条短腿分开站稳。
> - **B：缩成球的样子**（动力冲刺滚动时，附图 6，附图 8b 只看大小和地面线）。他**整个缩进甲壳里变成一个圆球**：四肢和头都收进去看不见，外面一圈都是橙金色甲板和皮带，**尖刺朝四面八方伸出**（像一颗带刺的球），侧面看。**球是圆的、左右上下大致对称**（游戏里要靠整张图转 90° 做出滚动），**球的直径大约和 A 里甲壳的宽度一样**，球底落在地面线上。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（3/4 正面、侧面、滚球）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的雷克塞（怪兽）、塔姆（矮胖的大个子）和波比（金色甲片），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：矮胖，**甲壳（连尖刺）约占身高的三分之二**，头小、腿短、手臂长；不要细长的写实比例。
> - **头**（附图 3 特写）：小小的绿色乌龟头，从甲壳前缘下面探出，**比附图里多露出一点**（游戏里很小，要看得清是个头）；**两只红橙色的眼睛一样大、一样高、都看得见**（每只至少 2 格，带一个亮色高光点）。
> - **甲壳**：橙金色鳞片甲板分 3–4 档（亮面金黄、暗面橙褐），每块甲板有一圈浅色的边；深棕色皮带清楚；尖刺浅黄到奶白，朝外的一面亮、背光的一面偏橙。
> - **画布用正方形 1536×1536**。**A 从最高的尖刺尖到鞋底约 660 px，也就是约 60 格**，鞋底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。尖刺、爪子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。橙金甲板、深棕皮带、浅黄尖刺、青绿鳞皮、深绿斑点、米白爪子、黄褐肚子、暗红挽具、灰钢钉要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（滚动的尘土、嘲讽的光、砸地的冲击波都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/rammus-picture/rammus-A.png`、`rammus-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/rammus-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/rammus_picture_done.zip`。

## 附图（在压缩包 `rammus_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_rammus_idle.png` | 英雄联盟原版拉莫斯的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_rammus_frontal.png` | 同一帧，正面 | 肚子、挽具和钢钉、两只手臂怎么垂 |
| `refs/3_rammus_head.png` | 头部特写 | 甲壳前缘下的乌龟头、红橙色眼睛 |
| `refs/4_rammus_back.png` | 同一帧的背后 | 甲壳背面的甲板、皮带和尖刺怎么排 |
| `refs/5_rammus_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_rammus_ball.png` | 动力冲刺缩成球的一帧（侧面） | **B 的球**：甲板、皮带、四面伸出的尖刺（这一帧手还没完全收进去，**你画的球里四肢和头都收进去**） |
| `refs/7_rammus_side.png` | 待机，接近侧面 | 甲壳的厚度、尖刺从侧面看 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 球的大小（和他的甲壳一样宽）、地面线（灰）；**形状按文字：圆球** |
| `style/11_style_reksai.png` | 本包的雷克塞，8 倍放大，一格 = 一个像素 | **只看风格**：怪兽的甲壳、鳞片和爪子在格子上怎么画 |
| `style/12_style_tahmkench.png` | 本包的塔姆（8 倍） | **只看风格**：矮胖的大身子、短腿在格子上怎么画 |
| `style/13_style_poppy.png` | 本包的波比（8 倍） | **只看风格**：格子密度、描边、金色甲片在格子上怎么画 |

## 提示词：`rammus-A.png` / `rammus-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a SQUAT ARMADILLO-TURTLE CREATURE under a HUGE DOMED SHELL made of ORANGE-GOLD SCALE PLATES held together by DARK-BROWN LEATHER STRAPS, with TALL PALE-YELLOW CONE SPIKES along its crest (the tallest in the middle of the back) and SMALLER SPIKES round its rim; the front edge of the shell overhangs like a hood, and under it a SMALL GREEN TURTLE HEAD peeks out with two GLOWING RED-ORANGE EYES; TEAL-GREEN SCALY arms and legs with DARK-GREEN SPOTS, LONG arms hanging almost to the ground, CREAM CLAWS on the hands and feet; a YELLOW-TAN BELLY crossed by a DARK-RED LEATHER HARNESS studded with GREY STEEL SPIKES (one big steel spike pointing down under the belly) (1 his idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the belly, the harness and its spikes, how the arms hang; 3 the head close-up: the hood of the shell, the turtle head, the red-orange eyes; 4 the same from behind: the plates, straps and spikes of the shell's back; 5 the official illustration: his mood and colours; 6 a frame of him curling into his rolling ball, from the side - the plates, the straps and the spikes all round (in this frame an arm still sticks out: in YOUR ball everything is tucked in); 7 the idle nearly from the side: the depth of the shell and its spikes). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a creature's carapace, scales and claws on the grid (11), a squat heavy body with short legs (12), the square density, the outline and gold plates on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (every spike and claw whole); the lowest point level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b).
PROPORTIONS: squat - the shell with its spikes about TWO THIRDS of his height; a small head, short legs, long arms; NOT realistic slim proportions.
THE HEAD: the small green turtle head under the hood of the shell, showing a little MORE of it than the renders do (it must read as a head at game size); TWO RED-ORANGE EYES of the SAME size at the SAME height, both visible (each at least 2 squares, with one bright highlight square).
THE SHELL: the orange-gold scale plates in 3-4 shades (golden lit faces, orange-brown shaded faces), each plate with a light rim; the dark-brown straps clearly readable; the spikes pale yellow to cream, their lit side bright and their shaded side warmer orange.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the orange-gold plates, the dark-brown straps, the pale-yellow spikes, the teal-green scaly skin, the dark-green spots, the cream claws, the yellow-tan belly, the dark-red harness and the grey steel studs clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no dust, no speed lines, no glow, no shockwave), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (rammus-A.png): his idle (images 1, 2 and 8a) - 3/4 view facing right (the head to the front-right): the shell domed over his back and head, the head peeking out under the front of the shell, the two long arms hanging at his sides with the claws near the ground, the two short legs apart and planted; the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker; both soles on the ground line. He is about 660 px (about 60 squares) from the tip of the tallest spike to his soles.
POSE B (rammus-B.png): POWERBALL - the SAME Rammus with the SAME 11-px squares, CURLED UP INTO A ROUND SPIKED BALL, seen from the side: the head, arms and legs all tucked inside and NOT visible, the whole outside made of the orange-gold plates and the dark-brown straps, the spikes pointing outward ALL ROUND like a spiked ball; the ball ROUND and roughly symmetric left-right and top-bottom (it will be turned by quarter turns to roll); its diameter about the width of his shell in pose A (about 44 squares without the spikes); resting on the ground line (image 8b shows only its size and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尖刺、爪子完整，不出画。
- A：矮胖、甲壳（连尖刺）约占身高三分之二；小乌龟头从甲壳前缘下探出，**两只红橙色眼睛一样大、一样高**、带高光；长手臂垂在两侧、爪子快到地面；两条短腿分开站稳；从最高尖刺尖到鞋底约 660 px（约 60 格），鞋底在地面线上。
- B：**完整的圆球**，头和四肢都收进去看不见；外面一圈橙金甲板和深棕皮带，尖刺朝四面八方伸出；球大致左右上下对称；直径约等于 A 里甲壳的宽度；球底在地面线上。
- 甲壳：橙金甲板分几档、每块有浅色边；深棕皮带；浅黄尖刺。肚子黄褐、暗红挽具、灰钢钉（A）。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/rammus-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/rammus_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/rammus/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回，和已合并的打野、坦克（雷克塞、皇子、悟空、塔姆、布隆、加里奥）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画：3/4 正面（待机、选人卡片）、**侧面朝右**（所有动作的底子）、滚球（侧面，圆）、尖刺防御的蜷缩姿势。动作帧不找 Codex，自己从造型的像素无损摆（`rig_rammus.py`：只整格平移、绕半格点的四分之一转、镜像；滚动 = 整颗球四分之一转）。英雄联盟的动作：普攻 rammus_attack1 / attack2 / crit（爪击）；Q rammus_spell1_windup（缩成球）、滚动、撞击；W Rammus_channel（蜷缩防御）；E rammus_spell3（嘲讽）；R rammus_spell4 / Spell4_Jump（跳起砸地）；跑 rammus_run；死亡 rammus_death。
