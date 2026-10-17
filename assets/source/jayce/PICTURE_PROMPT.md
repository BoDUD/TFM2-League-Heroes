# 杰斯（未来守护者）：先画像素风原图（第 0 步，给 Codex 的提示词）

> 杰斯是一个**自信的青年发明家战士**，手里的海克斯科技武器能在**墨丘利之锤**（大锤）和**墨丘利之炮**（加农炮）之间变形。这一步请 Codex 画**两张**全身像素风原图，**同一个人、同样的长相、衣服、颜色、同样的格子大小**：**A = 锤形**（英雄联盟的近战待机：双手握着大锤竖在身前，金色锤头在肩膀上方，附图 1、5a）；**B = 炮形**（英雄联盟的远程待机：锤子折成加农炮端在腰间，炮口朝画面右边，附图 6、5b）。两张**都要**（两种形态在游戏里都会出现），每张请画 2 版让我挑。之后第 1 步再按选中的画正面 + 侧面的造型。这一版每个游戏像素约 **1.5 格**（附图 11–14 是本包同样密度的加里奥、布隆、泽丽、奈德丽）：像素块清楚、整齐、大小一致，描边约 **2 格**，身材**敦实、偏 Q 版**。你画的原图会直接按格子读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–10）。
> - **头**（附图 3 特写）：一个英俊的青年，头约占身高的**四分之一到三分之一**（Q 版）；**深棕色短发**往后梳、额前一小撮翘起；**麦色皮肤**、方下巴、浓眉；**两只眼睛看得清**；**自信的微笑**（嘴角一边上扬）；**脸朝右前方平视**。
> - **衣服**：**深红色高领围巾**绕在脖子上（一角垂到胸前）；**米白色毛领**；**棕色皮外套**，胸前**米金色 + 红色的胸甲**，中间一个**圆形徽章**（米金色圆盘、中间红色图案）；一边肩膀上**一块很大的米金色肩甲**（红色镶边，附图 10）；腰间**棕色皮带 + 金扣**；身后**深海军蓝的长衣摆**（垂到小腿）；**深灰蓝色裤子**；**米金色护膝和护胫**（尖角造型）+ **深棕色靴子**；**棕色手套**。
> - **A 的武器：墨丘利之锤**（附图 1、2、10）：**笔直的长柄**（银灰色金属，握手处**红色**），底端一个**银灰色的尖钻头**；顶上一个**很大的金色方块双头锤头**（两块方方的金色锤面，中间一个**发橙色光的海克斯核心齿轮**）。整把锤**约和他一样高**，**锤柄必须笔直**，锤头在他肩膀上方、画面左上，**不能挡住他的脸**。
> - **B 的武器：墨丘利之炮**（附图 6、7）：同一把武器折成的加农炮——**金色的方块锤面翻到炮管两侧**，中间**银灰色的炮管**、炮口一圈**小尖刺**，炮尾一个**银灰色尖钻头**朝后；**笔直、水平**，端在腰间、**炮口朝画面右边**，橙色核心发一点光（只是颜色，不画光晕特效）。
> - **姿势**：3/4 正面朝右（脸朝右前方，胸口朝向看画的人），两脚分开站稳：**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗、稍高**，两只靴底落在同一条地面线上。B 的炮形可以照附图 6 **微微弯腿压低重心**（比 A 稍矮一点），但人的大小、头的大小必须和 A 一样。
> - **比例**：**敦实、偏 Q 版**——头大一点，肩膀宽，腿不要太长；风格完全照附图 11–14；**不要细长的写实比例**。
> - **A 用竖版画布 1024×1536**：**他从头发顶到鞋底约 684 px，也就是约 57 格**，鞋底在离画布底边约 196 px 的地方（附图 5a 的灰线），锤头在头顶上方，全部在画面里；**B 用横版画布 1536×1024**：同一个人、同一个格子大小，鞋底在离底边约 124 px 的地方（附图 5b 的灰线），炮口朝右，全部在画面里。
> - **像素块**：大小一致的方块，**每块 12 像素**，横平竖直对齐成网格（这张图会被按格子读回，一格就是一个像素）；**外轮廓一圈 2 块宽的近黑描边**；内部每种材质 3–4 档平涂，不要细碎的单个杂色格。
> - 不画任何特效（电光、闪电、光圈、电球、加速门都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/jayce-picture/jayce-hammer-A1.png`、`jayce-hammer-A2.png`（1024×1536 竖版）、`jayce-cannon-B1.png`、`jayce-cannon-B2.png`（1536×1024 横版），都是**真透明背景**；原始生成图原样放进 `outputs/jayce-picture/raw/`；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `jayce_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_jayce_hammer.png` | 英雄联盟原版杰斯锤形待机，3/4 朝右 | A 的颜色、形状、**角度**、姿势 |
| `refs/2_jayce_hammer_frontal.png` | 同一帧，正面 | 胸甲、徽章、肩甲、衣摆、护膝怎么做 |
| `refs/3_jayce_head.png` | 头部特写 | 发型、浓眉、微笑、红围巾、毛领 |
| `refs/4_jayce_back.png` | 同一帧的背后 | 海军蓝长衣摆、外套背面 |
| `refs/5_jayce_splash.png` | 官方加载画面 | 气质（自信）、炮形的样子 |
| `refs/5a_layout_A_hammer.png` | A 的布局示意（模型剪贴，只看位置和大小） | 竖版画布上人和锤的位置、鞋底线 |
| `refs/5b_layout_B_cannon.png` | B 的布局示意（同一比例） | 横版画布上人和炮的位置、鞋底线 |
| `refs/6_jayce_cannon.png` | 炮形待机，3/4 朝右 | B 的颜色、形状、**角度**、姿势 |
| `refs/7_jayce_cannon_frontal.png` | 炮形待机，几乎正面 | 炮的构造 |
| `refs/8_jayce_actions.png` | 锤击、苍穹之跃、雷霆一击、炮击、电能震荡、跑动（侧面） | 第 2 步用（这一步不画） |
| `refs/9_jayce_side.png` | 锤形和炮形待机的侧面（朝右） | 第 1 步用（这一步不用） |
| `refs/10_jayce_upper.png` | 锤头 + 上半身特写 | 金色锤头 + 橙色核心、大肩甲、红围巾 |
| `style/11_style_galio.png` | 本包同样密度（每游戏像素 1.5 格）的加里奥待机（8 倍放大，一格 = 一个像素） | **只看风格**：像素粗细、描边、敦实比例、头的大小 |
| `style/12_style_braum.png` | 同样密度的布隆（8 倍） | **只看风格** |
| `style/13_style_zeri.png` | 同样密度的泽丽（8 倍） | **只看风格** |
| `style/14_style_nidalee.png` | 同样密度的奈德丽（8 倍） | **只看风格** |

## 提示词 A：`jayce-hammer-A1.png` / `A2.png`（锤形，画两版）

十六张图都附上，顺序同上表。

```text
Sixteen attached images. Images 1-10 are 3D renders and art of a character from the game: a confident young inventor-warrior whose hextech weapon turns between a giant HAMMER and a CANNON (1 the man with the hammer in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 2 the same from the front: the chest armour, the round emblem, the big shoulder plate, the coat tails, the knee guards; 3 his head close-up: the hair, the brows, the smile, the red scarf, the fur collar; 4 the same from behind; 5 the official illustration: his confident mood; 5a THIS picture's layout guide: where the man and the hammer go on the canvas, the grey line is the ground; 5b the other picture's layout guide: ignore it here; 6 and 7 the cannon form - not drawn here; 8 moments of his actions from the side - not drawn here; 9 his idles from the side - not used here; 10 a close-up of the hammer head and his upper body). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, STOCKY chunky proportions and head size.
Create ONE pixel-art picture of the man with the hammer, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha). The man about 684 px (about 57 squares) from the top of his hair to the soles of his boots, the soles about 196 px above the bottom edge (the grey line of image 5a); the hammer head above his shoulder; everything whole, comfortable transparent margins, nothing cut off; both soles level on one ground line.
THE MAN: a handsome confident young man. THE HEAD, a little big (chibi-ish, about a quarter to a third of his height): short DARK BROWN hair swept back with a small quiff over the forehead; TANNED skin, a square jaw, thick brows; TWO EYES clearly readable; a confident half smile; the face turned to the front-right, looking straight ahead. THE CLOTHES: a DEEP RED high scarf round his neck, one end hanging over the chest; a CREAM fur collar; a BROWN leather coat; CREAM-GOLD and RED chest armour with a ROUND EMBLEM in the middle (a cream-gold disc, a red sign in it); ONE BIG CREAM-GOLD SHOULDER PLATE with red inlays on one shoulder; a brown belt with a gold buckle; long DARK NAVY coat tails behind him down to the calves; dark slate-blue trousers; CREAM-GOLD pointed knee guards and shin plates over DARK BROWN boots; brown gloves.
THE HAMMER (the Mercury Hammer): a long PERFECTLY STRAIGHT shaft of silver-grey metal with a RED grip, a silver-grey drill spike at its lower end; at the top a HUGE GOLDEN double hammer head of two big square golden blocks with an ORANGE glowing hextech core-gear between them. The whole hammer about as tall as he is; he holds it upright before his chest in both hands (image 1), the head above his shoulder on the image left, never covering his face; the shaft dead straight.
THE POSE: League's idle (image 1), 3/4 view facing right (face to the front-right, chest toward the viewer), feet apart and planted: the NEAR leg on the image LEFT in full tone, the FAR leg on the image RIGHT a step darker and a little higher; both soles on one ground line.
PROPORTIONS: STOCKY and chibi-ish like images 11-14 - a slightly big head, broad shoulders, short legs; NOT slender realistic proportions.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and the hammer; inside it every material in its own 3-4 flat shades, no stray single odd squares: the hair dark brown, the skin tan, the scarf deep red, the collar cream, the coat brown, the armour cream-gold with red, the coat tails dark navy, the trousers slate blue, the knee guards cream-gold, the boots dark brown, the hammer gold with an orange core, the shaft silver-grey with a red grip; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no lightning, no sparks, no glow aura, no rings), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`jayce-cannon-B1.png` / `B2.png`（炮形，画两版）

十六张图都附上，顺序同上表；**最好把 A 选好的那张也附上**，让人和衣服一模一样。

```text
Sixteen attached images (plus, if you have it, your finished hammer picture of the same man: keep him IDENTICAL). Images 1-10 are 3D renders and art of a character from the game: a confident young inventor-warrior whose hextech weapon turns between a giant HAMMER and a CANNON (6 the man with the CANNON in 3/4 view facing right - the look, the ANGLE and the POSE of this picture; 7 the cannon form nearly from the front: how the cannon is built; 1, 2, 3, 4 and 10 the same man with the hammer: his face, clothes and armour from several sides; 5 the official illustration with the cannon; 5b THIS picture's layout guide: where the man and the cannon go on the canvas, the grey line is the ground; 5a the other picture's layout guide: ignore it here; 8 moments of his actions - not drawn here; 9 his idles from the side - not used here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, STOCKY chunky proportions and head size.
Create ONE pixel-art picture of the man with the cannon, a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha). The SAME man at the SAME size as in the hammer picture (top of the hair to the soles about 684 px = 57 squares standing; here his knees bend a little, so he stands a bit lower - his head and body exactly as big as in the hammer picture), the soles about 124 px above the bottom edge (the grey line of image 5b); everything whole, comfortable transparent margins, nothing cut off; both soles level on one ground line.
THE MAN: exactly as in the hammer picture - short DARK BROWN hair swept back with a small quiff, TANNED skin, square jaw, thick brows, two readable eyes, a confident half smile, face to the front-right looking straight ahead; a DEEP RED high scarf, a CREAM fur collar, a BROWN leather coat, CREAM-GOLD and RED chest armour with a round emblem, ONE BIG CREAM-GOLD shoulder plate with red inlays, a brown belt, long DARK NAVY coat tails, slate-blue trousers, cream-gold pointed knee guards and shin plates, dark brown boots, brown gloves.
THE CANNON (the Mercury Cannon, the same weapon folded): a STRAIGHT, LEVEL cannon held at his hip in both hands, the MUZZLE POINTING TO THE IMAGE RIGHT: a silver-grey barrel with a ring of small spikes round the muzzle, the two big square GOLDEN hammer blocks folded along both sides of the barrel, the ORANGE hextech core glowing a little between them (colour only, no glow effect), a silver-grey drill spike at the back end pointing back-left. About as long as he is tall; never covering his face.
THE POSE: League's ranged idle (image 6), 3/4 view facing right (face to the front-right, chest toward the viewer), knees bent a little, feet apart and planted: the NEAR leg on the image LEFT in full tone, the FAR leg on the image RIGHT a step darker and a little higher; both soles on one ground line.
PROPORTIONS: STOCKY and chibi-ish like images 11-14 - a slightly big head, broad shoulders, short legs; NOT slender realistic proportions.
THE PIXEL GRID: every square the SAME size, 12 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and the cannon; inside it every material in its own 3-4 flat shades, no stray single odd squares (colours as in the hammer picture; the cannon gold with an orange core, the barrel silver-grey); light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no lightning, no muzzle flash, no sparks, no glow aura, no rings), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底）；A 竖版 1024×1536、B 横版 1536×1024；四周留边，人物和武器完整，不出画。
- 头：深棕后梳短发 + 一小撮刘海、麦色皮肤、浓眉、**两只眼睛看得清**、自信微笑、**平视前方**；头约占身高四分之一到三分之一。
- 衣服：深红高领围巾、米白毛领、棕皮外套、米金 + 红胸甲和圆徽章、**一块大米金肩甲**、棕皮带金扣、海军蓝长衣摆、灰蓝裤子、米金尖角护膝护胫、深棕靴子、棕手套。
- A：锤柄**笔直**、银灰 + 红握把 + 底端尖钻；**大金色方块双锤头 + 橙色核心**在肩膀上方画面左边，不挡脸；锤约和他一样高。
- B：炮**笔直水平**、端在腰间、**炮口朝右**（炮口一圈小尖刺）；金色锤块折在炮管两侧、橙色核心；尾端尖钻朝后。
- A 和 B 是同一个人：同样的头、同样的衣服、**同样的格子大小、同样大的头和身体**（B 只是微微弯腿）。
- 从发顶到鞋底约 684 px（约 57 格）；敦实、偏 Q 版（像附图 11–14），不是细长的写实比例。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；鞋底在同一条水平线上；没有任何特效。
- **每块 12 像素、大小一致、对齐网格**；2 块宽的近黑外描边；没有糊、没有柔光、没有渐变、没有零散杂色格；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述（提示词里本来就没写名字）。
- 全部画完后最后写 `outputs/jayce-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/jayce/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 12 px），按它自己的格子读回（regrid / k-means 调色板后再投票，palette_of 直接用在原图上会全暗），和同位置英雄（league/*#sheet.png：darius、garen、renekton、aatrox 等）并排给用户挑 A / B 各一张和大小、密度（选的是 PPU 1.5）。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：锤形和炮形各自 **正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子）**，同一个高度、同一套格子、同样的细节（side-view-design）；原稿 1:1 按格读回，绝不先画大再缩。武器要直、不乱转。
- 同一张脸贯穿所有帧（one-face-all-frames）；跑步按 Caitlyn 的交叉步（run-legs-caitlyn-way），锤形 / 炮形各一套跑步（附加包换整身）。
