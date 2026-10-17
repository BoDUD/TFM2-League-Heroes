# 杰斯：在格子上画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了锤形 **A2** 和炮形 **B2**，游戏里的大小定为**头发顶到鞋底 57 格**（炮形弯着腿，54 格）。**你画的每一格就是游戏里的一个像素格**（每游戏像素 1.5 格），交回后我 1:1 读回，不缩放。
> - `1_hammer_grid.png` / `2_cannon_grid.png` 是我把 A2 / B2 缩到这个大小放在格子上的样子——**大小、位置、颜色对，但脸和细节糊了**（眼睛、嘴、胸甲、锤头核心都看不清）。所以**第一件事：在同样的格子上把两张正面重新画干净**（样子照 `3_hammer_A2.png` / `4_cannon_B2.png`，就是你上一轮画的）。
> - **第二件事：侧身版（最重要，所有动作都从它来）**：本包所有英雄除了待机，每个动作都是**侧身朝右**。之前一个英雄的造型只画了正面，动作帧全成了正面站着，被用户全部退回。所以锤形、炮形**各自再画身体转向画面右边的版本**，各两稿（A 完全侧面、B 稍带 3/4）。
>
> **侧身版和正面版必须是同一个人**：同样的格子、同样的高度和头身比、同样的颜色和细节，只是身体转了个角度。**锤形和炮形也必须是同一个人**（同一颗头、同样的衣服、同样大），只是武器和站姿不同。**武器永远是笔直的**（锤柄、炮管都不能弯）。

## 大小和位置

- **锤形**：画布 **1024 × 1536 竖版，固定 12 × 12 px 的格子**（85 列 × 128 行，最右边 4 px 留透明）；**头发顶在第 44 行**（绿线），**鞋底最低的一行是第 100 行**（红线上面那一行，红线以下什么都不能有：游戏在脚下画血条）——发顶到鞋底 57 行；**站立点（两只靴子中间）在第 48 列**（蓝线）。锤头在他头的左上方（约第 30–53 行、第 18–44 列），和 `1_hammer_grid.png` 一样。
- **炮形**：画布 **1536 × 1024 横版，同样 12 × 12 px 的格子**（128 列 × 85 行，最下面 4 px 留透明）；**头发顶在第 17 行**（绿线），**鞋底最低的一行是第 70 行**（红线上面那一行）——54 行（弯着腿，人和锤形一样大）；**站立点在第 54 列**（蓝线）。炮从第 12 列（尾部尖钻）到第 92 列（炮口）、约第 38–56 行，和 `2_cannon_grid.png` 一样。
- **每个格子一个颜色，格子对齐画布左上角**。直接在格子上画，**不要先画大图再缩小**（会糊）。

## 正面怎么画（`jayce-hammer-front.png`、`jayce-cannon-front.png` + 分层）

- **照 `3_hammer_A2.png` / `4_cannon_B2.png` 的样子**、**照 `1_hammer_grid.png` / `2_cannon_grid.png` 的大小和位置**，在 12 px 格子上逐格重画：3/4 正面朝右，两脚分开站稳（近侧腿在画面左边亮色，远侧腿在右边稍暗、稍高）。
- **脸一定要清楚**（全身最重要的地方）：深棕后梳短发 + 额前一小撮翘起；麦色皮肤；**两只眼睛**（每只至少 2 格宽：深色瞳孔 + 一格白色高光）；**浓眉**清楚；**自信的微笑**（嘴角一边上扬）；方下巴；脸朝右前方平视。**两张正面的头逐格一样**（先画锤形，炮形的头照锤形的抄）。
- 衣服：深红高领围巾（一角垂到胸前）、米白毛领、棕皮外套、**米金 + 红色胸甲，中间圆形徽章**、**一块大米金肩甲（红色镶边）**、棕皮带 + 金扣、海军蓝长衣摆、灰蓝裤子、**米金尖角护膝护胫**、深棕靴子、棕手套。
- **锤**：**笔直**的银灰长柄 + 红色握把 + 底端银灰尖钻；**大金色方块双锤头**，中间**橙色海克斯核心**（一圈深色 + 橙色芯 + 一格亮黄）；锤面上的红色凹槽清楚；**锤头不能挡住他的脸**。
- **炮**：**笔直水平**，炮口朝右：银灰炮管、**炮口开口一圈**（深色洞口）、金色锤块折在炮管两侧、橙色核心、尾部银灰尖钻朝左。
- 从同一张成品图分出两层（同样的画布和位置，**不重画**）：`-body.png`（只有人，被武器挡住的手臂/身体补完整）、`-weapon.png`（只有武器，被手挡住的部分补完整）。

## 侧身怎么画（`jayce-hammer-side-A.png` / `-B.png`、`jayce-cannon-side-A.png` / `-B.png`）

- **身体转向画面右边**（像 `5_league_side.png`）：胸口朝右，**近侧（画面右边）的手臂和肩在前**、大肩甲转到侧面；腰带、长衣摆跟着转过来（衣摆在身后）。
- **锤形侧身**：双手握锤**竖在身体前面**，锤柄**笔直竖直**，**锤头在他头的右上方（身前）**，底端尖钻在前脚旁边，不碰地；锤头不挡脸。
- **炮形侧身**：炮**笔直水平**端在腰间，**炮口朝右**、尾部尖钻在身后；膝盖微弯。
- **腿**：从侧面看**一前一后**（近侧腿在前、颜色亮；远侧腿在后、暗一档），**靴子朝右**，两只鞋底都踩在鞋底那一行；腿不要画细、画长。
- **头保持和正面版一样的 3/4 头**（后梳短发、两只眼睛都看得见、微笑），**逐格照你画的正面版**——本包的规矩是所有动作帧都用待机那一张脸，**不另画侧脸**；只是把这颗头放在侧过来的身体上，脖子接得自然。
- 比例和正面版一样敦实；不要把侧身画瘦、画高。行列位置和同形态的正面版一样（锤形：发顶第 44 行、鞋底第 100 行、站立点第 48 列；炮形：发顶第 17 行、鞋底第 70 行、站立点第 54 列）。
- **A**：完全侧面（干净的侧身轮廓）；**B**：转得少一点（约 3/4 朝侧面，多露一点胸甲和徽章）。

## 干净（照 `6_style.png` 的统一画风）

- 每个 12 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光）；外轮廓一圈 **2 格粗的近黑描边**，里面少用黑（内部分界用材质自己的暗色）；不要抖动、渐变、碎点、零散杂色格；**所有图用同一套颜色**（照 `3_hammer_A2.png`）。
- 背景真透明，**alpha 只能是 0 或 255**（不要半透明光晕——上一轮的图四周有一圈半透明，alpha 从来没到 255）。不要网格线、文字、编号、边框、影子、特效（电光、光晕都不画）。

## 附图（压缩包 `jayce_model_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_hammer_grid.png` | A2 缩到游戏大小放在 12 px 格子上（每 2 格一条浅线、每 10 格一条深线并编号）；绿线 = 发顶第 44 行，红线 = 第 100 行下沿，蓝线 = 站立点第 48 列 | 锤形的**大小、位置、颜色、比例**（细节糊了，要重画） |
| `2_cannon_grid.png` | B2 缩到游戏大小放在横版格子上；绿线 = 第 17 行，红线 = 第 70 行下沿，蓝线 = 第 54 列 | 炮形的**大小、位置、颜色、比例** |
| `3_hammer_A2.png` | 你上一轮画的锤形 A2（大图） | **样子**：脸、衣服、锤都照它 |
| `4_cannon_B2.png` | 你上一轮画的炮形 B2（大图） | **样子**：炮照它 |
| `5_league_side.png` | 英雄联盟的杰斯转到侧面朝右：上排锤形、炮形待机（80°），下排锤形待机、锤形跑步、炮形待机、炮形跑步（90°） | **侧身怎么转**：武器怎么拿、腿一前一后、靴子朝右 |
| `6_style.png` | 本包同样密度的英雄（加里奥、布隆、泽丽、奈德丽） | 统一画风：像素粗细、粗描边、敦实 |
| `7_hammer_empty.png` / `8_cannon_empty.png` | 空格子，同样的行列标线 | 画布 |

## 提示词 1：锤形正面重画 `jayce-hammer-front.png`（+ 两个分层）

附 1、3、6、7。

```text
Attached images: 1 this character's front design (with his giant hammer) cut down to its game size on a fixed grid of 12x12-pixel squares (a thin line every 2 squares, a numbered line every 10; green line = row 44, red line = the bottom of row 100, blue line = column 48) - the SIZE, POSITION, COLOURS and PROPORTIONS to keep, but its face and details came out MUDDY; 3 the same character as a bigger picture (the previous take) - the LOOK to keep, crisp: the face, the clothes, the hammer; 6 other heroes of this game in the same look (style only); 7 an empty grid with the same lines - the canvas.
REDRAW the front design of image 1 cleanly, square by square, ON THE SAME FIXED GRID: one 1024x1536 PORTRAIT PNG with a real transparent background (85 x 128 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same size and place as image 1: the top of his hair on row 44, the boots' lowest row 100 (nothing below it), the standing point (between the boots) on column 48; the hammer head up at the upper left of his head (about rows 30-53, columns 18-44) as in image 1.
The man, exactly as image 3: 3/4 FRONT view facing image right, holding the hammer upright before his chest in both hands, standing firm with the feet apart (the near leg on the image left in full tone, the far leg on the image right a shade darker). THE FACE MUST READ CLEARLY, the most important part: short DARK BROWN hair swept back with a small quiff; TANNED skin; TWO EYES, each at least 2 squares wide (a dark pupil and one white highlight square); clear thick dark brows; a confident half smile; a square jaw; looking straight ahead to the front-right. A DEEP RED high scarf (one end hanging on the chest), a CREAM fur collar, a BROWN leather coat, CREAM-GOLD and RED chest armour with a ROUND EMBLEM in the middle, ONE BIG CREAM-GOLD SHOULDER PLATE with red inlays, a brown belt with a gold buckle, long DARK NAVY coat tails, slate-blue trousers, CREAM-GOLD pointed knee guards and shin plates, dark brown boots, brown gloves. THE HAMMER, exactly as image 3: a PERFECTLY STRAIGHT silver-grey shaft with a RED grip and a silver-grey drill spike at its lower end; a HUGE GOLDEN double head of two square blocks with red grooves and an ORANGE hextech core between them (a dark ring, an orange centre, one bright yellow square); it never covers his face.
Clean like image 6: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round each silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares except the eye highlights, no specks, no dithering, no gradients, the colours of image 3. No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Then, from the SAME finished picture (do not redraw), save two layers on the same canvas at the same positions: jayce-hammer-front-body.png (the man only, the parts the hammer hid completed) and jayce-hammer-front-weapon.png (the hammer only, the parts his hands hid completed).
```

## 提示词 2：炮形正面重画 `jayce-cannon-front.png`（+ 两个分层）

附 2、4、你刚画好的 `jayce-hammer-front.png`、6、8。

```text
Attached images: 2 this character's front design (with his weapon folded into a CANNON) cut down to its game size on a fixed grid of 12x12-pixel squares (a thin line every 2 squares, a numbered line every 10; green line = row 17, red line = the bottom of row 70, blue line = column 54) - the SIZE, POSITION, COLOURS and PROPORTIONS to keep, but its face and details came out MUDDY; 4 the same as a bigger picture (the previous take) - the LOOK to keep, crisp: the cannon and the stance; then the hammer front you just drew (jayce-hammer-front.png) - the SAME MAN: copy his HEAD square for square and his clothes and colours exactly; 6 other heroes of this game in the same look (style only); 8 an empty grid with the same lines - the canvas.
REDRAW the front design of image 2 cleanly, square by square, ON THE SAME FIXED GRID: one 1536x1024 LANDSCAPE PNG with a real transparent background (128 x 85 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same size and place as image 2: the top of his hair on row 17, the boots' lowest row 70 (nothing below it), the standing point (between the boots) on column 54; the cannon from about column 12 (the drill spike at its back) to column 92 (the muzzle), about rows 38-56.
The man: the SAME man as the hammer front - the same head square for square (short dark brown swept-back hair with a quiff, tanned skin, two readable eyes with highlights, thick brows, a confident half smile), the same clothes, armour and colours, the same size; 3/4 FRONT view facing image right, knees bent a little, feet apart and planted (the near leg on the image left in full tone, the far leg on the image right a shade darker). THE CANNON, exactly as image 4: PERFECTLY STRAIGHT and LEVEL, held at his hip in both hands, the MUZZLE to the image RIGHT with a clear dark opening and a ring round it; a silver-grey barrel; the square GOLDEN hammer blocks folded along both sides; the ORANGE hextech core between them; a silver-grey drill spike at the back end pointing left; it never covers his face.
Clean like image 6: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round each silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares except the eye highlights, no specks, no dithering, no gradients, ONLY the colours of the hammer front. No effects, no glow, no muzzle flash, no background, no ground, no shadow, no text, no grid lines.
Then, from the SAME finished picture (do not redraw), save two layers on the same canvas at the same positions: jayce-cannon-front-body.png (the man only, the parts the cannon hid completed) and jayce-cannon-front-weapon.png (the cannon only, the parts his hands hid completed).
```

## 提示词 3：锤形侧身 `jayce-hammer-side-A.png`、`-B.png`（两稿）

附你画好的 `jayce-hammer-front.png`、5、7、3、6。

```text
Attached images: first this character's approved front design on a fixed grid of 12x12-pixel squares (the picture you just drew: jayce-hammer-front.png) - the LOOK, colours, square size and proportions of the man and his hammer, and his HEAD square for square; 5 his 3D model turned to the side, facing right (top row: the hammer idle and the cannon idle; bottom row: the hammer idle, a hammer run frame, the cannon idle, a cannon run frame) - how he looks SIDE-ON; 7 an empty grid with numbered lines (green line = row 44, red line = the bottom of row 100, blue line = column 48) - the canvas; 3 the same character as a bigger picture; 6 other heroes of this game in the same look (style only).
Draw the man WITH THE HAMMER SIDE-ON, his body turned to face the IMAGE RIGHT, on the same fixed grid: one 1024x1536 PORTRAIT PNG with a real transparent background (85 x 128 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same height as the front design: the top of his hair on row 44, the boots' lowest row 100 (nothing below it), the standing point (between the boots) on column 48.
The man: exactly the colours, square size, outline and details of the front design. SIDE-ON (like image 5): his chest turned to the right; the near arm and shoulder (image right) in front, the big shoulder plate turned to the side; the belt turned with him, the navy coat tails behind him; both hands hold the hammer UPRIGHT IN FRONT OF HIS BODY: the shaft PERFECTLY STRAIGHT and VERTICAL, the golden hammer head up at the UPPER RIGHT of his head (in front of him), the drill spike beside his front foot, not touching the ground, the head never covering his face; the legs ONE IN FRONT OF THE OTHER (the near leg in front in full tone, the far leg behind a shade darker), the boots pointing RIGHT, both on row 100; do not make the legs thinner or longer. THE HEAD STAYS THE SAME 3/4 HEAD AS IN THE FRONT DESIGN, square for square (the swept-back hair, BOTH eyes visible, the half smile) - every frame of this game keeps the idle's face, no separate profile face - only placed on the side-on body with a natural neck. Keep the front's STOCKY proportions; do not make him thinner or taller.
Clean like the front design and image 6: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares except the eye highlights, no specks, no dithering, no gradients, ONLY the colours of the front design. No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Make TWO takes, A and B: A turned fully side-on (a clean profile body), B turned a little less (about three quarters toward the side, a bit more of the chest armour and the emblem showing).
```

## 提示词 4：炮形侧身 `jayce-cannon-side-A.png`、`-B.png`（两稿）

附你画好的 `jayce-cannon-front.png`、`jayce-hammer-side-A.png`（或你更满意的那稿）、5、8、6。

```text
Attached images: first this character's approved CANNON front design on a fixed grid of 12x12-pixel squares (jayce-cannon-front.png) - the LOOK, colours, square size and proportions of the man and his cannon, and his HEAD square for square; then his hammer side-on view you just drew - how his body, coat and legs turn side-on; 5 his 3D model turned to the side, facing right (top row: the hammer idle and the cannon idle; bottom row: the hammer idle, a hammer run frame, the cannon idle, a cannon run frame); 8 an empty grid with numbered lines (green line = row 17, red line = the bottom of row 70, blue line = column 54) - the canvas; 6 other heroes of this game in the same look (style only).
Draw the man WITH THE CANNON SIDE-ON, his body turned to face the IMAGE RIGHT, on the same fixed grid: one 1536x1024 LANDSCAPE PNG with a real transparent background (128 x 85 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same height as the cannon front: the top of his hair on row 17, the boots' lowest row 70 (nothing below it), the standing point (between the boots) on column 54.
The man: exactly the colours, square size, outline and details of the cannon front, his body turned like the hammer side-on view. The CANNON PERFECTLY STRAIGHT and LEVEL at his hip in both hands, the MUZZLE pointing RIGHT (its dark opening and ring clear), the golden blocks along the barrel, the orange core, the drill spike behind him; knees bent a little; the legs ONE IN FRONT OF THE OTHER (the near leg in front in full tone, the far leg behind a shade darker), the boots pointing RIGHT, both on row 70; do not make the legs thinner or longer. THE HEAD STAYS THE SAME 3/4 HEAD AS IN THE FRONT DESIGN, square for square (both eyes visible, the half smile) - no separate profile face. Keep the STOCKY proportions; do not make him thinner or taller.
Clean like the front design and image 6: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares except the eye highlights, no specks, no dithering, no gradients, ONLY the colours of the front design. No effects, no glow, no muzzle flash, no background, no ground, no shadow, no text, no grid lines.
Make TWO takes, A and B: A turned fully side-on (a clean profile body), B turned a little less (about three quarters toward the side, a bit more of the chest armour and the emblem showing).
```

## 交回前请检查

- 锤形图 1024×1536、炮形图 1536×1024，12 px 格子对齐左上角、每格一个颜色、**alpha 只有 0 / 255**。
- 正面：大小位置和格子图一样（锤形发顶第 44 行、鞋底第 100 行、站立点第 48 列；炮形第 17 / 70 行、第 54 列）；**脸清楚**（两只眼睛 + 高光、浓眉、微笑）；**两张正面的头逐格一样**；锤柄 / 炮管**笔直**；武器不挡脸；分层和成品同一张画。
- 侧身：身体真的转向右边（近侧手臂在前、腿一前一后、靴子朝右）；**头和正面版是同一颗 3/4 头**（两只眼都看得见）；颜色只用正面版的；锤形侧身锤竖在身前、炮形侧身炮口朝右；不比正面瘦、不比正面高。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/jayce-model/`）

- `jayce-hammer-front.png`、`jayce-hammer-front-body.png`、`jayce-hammer-front-weapon.png`、`jayce-cannon-front.png`、`jayce-cannon-front-body.png`、`jayce-cannon-front-weapon.png`、`jayce-hammer-side-A.png`、`jayce-hammer-side-B.png`、`jayce-cannon-side-A.png`、`jayce-cannon-side-B.png`；未经处理的生成原稿放 `outputs/jayce-model/raw/`；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 原稿逐格读回（先在 8 倍下数描边台阶量实际格子大小，再 regrid；Codex 从来不在要求的格子上），检查高度（57 / 54 行）、站立点、脸（眼睛 / 嘴清楚）、两形态同一颗头、武器笔直；颜色映射到一套调色板；侧身贴正面的 3/4 头（one-face-all-frames）。
- 用户选侧身 A / B 后：第 2 步动作条包 MODEL_STRIPS.md 从侧身版出（锤形动作：attack、skill 苍穹之跃、skill2 雷霆一击、w_cast 闪电领域、tf_c 变炮、run、dead；炮形：c_attack、c_skill 电能震荡、c_skill2 超能电荷、ult 加速电炮、tf_h 变锤、c_run、c_dead）；跑步按 Caitlyn 的交叉步；武器永远笔直、整块移动。
