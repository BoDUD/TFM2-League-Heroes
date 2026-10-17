# 千珏（永猎双子）：在格子上画侧身造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画 B（羊两蹄着地、狼在她身后胯部高度），已经按它自己的格子逐格读回成造型（`1_front_grid.png`），狼缩小到原来的 55%。游戏里是高清 PPU：**你画的每一格就是一个高清像素**，交回后我 1:1 读回，不缩放。
> **正面版直接用它，这一轮不用重画正面。**
> - **要画的是侧身版（最重要，所有动作都从它来）**：本包所有英雄除了待机，每个动作都是**侧身朝右**。之前一个英雄的造型只画了正面，动作帧全成了正面站着，被用户全部退回。所以同一个造型再画**身体转向画面右边**的版本。
> - **羊和狼分开画，各画一张**（动作里两个要分开摆）：羊的侧身两稿（A 完全侧面、B 稍带 3/4），狼的侧面一张。
>
> **侧身版和正面版必须是同一个角色**：同样的格子、同样的高度和头身比、同样的颜色和细节，只是身体转了个角度。

## 大小和位置

- 画布 **1536 × 1024，固定 6 × 6 px 的格子**（256 列 × 170 行，最下面 4 px 留透明），**每个格子一个颜色，格子对齐画布左上角**。直接在格子上画，**不要先画大图再缩小**（会糊）。
- **羊**：和 `1_front_grid.png` 同样的位置——**面具耳尖在第 14 行**（绿线），**蹄底最低的一行是第 167 行**（红线上面那一行，红线以下什么都不能有：游戏在脚下画血条）——耳尖到蹄底 154 行；**弓尖约在第 2 行**（紫线）；**站立点（两只蹄子中间）在第 170 列**（蓝线）。宽度不超过 130 格（毛发、弓都算）。
- **狼**：和 `2_front_layers.png` 左边那只狼**一样大**（约 52 行高、74 列长，鼻尖到最后一缕毛尖），**单独一张图**，鼻尖放在**第 110 列、第 100 行**附近，不碰画布边。

## 羊的侧身版怎么画（`kindred-side-lamb-A.png` / `-B.png`）

- **身体转向画面右边**（像 `3_league_lamb.png` 第一帧）：白色长毛披肩和毛发兜帽**往后飘、拖在背后（画面左边）**；淡冰蓝白的身体侧过来朝右；**近侧（画面右边）的手在身前把弓竖直握着**，弓在她身体前面（画面右边），**整把弓竖直、一条直线**（深紫弓身、青绿涡纹、上下两个淡青弯钩弓梢、细弓弦朝她这边），和正面版一样的格子画法；远侧的手在身后、被身体挡住大半。
- **腿**：从侧面看**一前一后**（近侧腿在前、颜色亮；远侧腿在后、暗一档），**蓝紫色的反关节羊腿**（膝盖往后弯、往下越来越深），**黑褐色羊蹄朝右**，两只蹄底都踩在第 167 行。
- **头保持和正面版一样的 3/4 面具头**（深紫羊面具、尖耳、月牙纹、**两只发光青绿大眼都看得见**），逐格照 `1_front_grid.png`——本包的规矩是所有动作帧都用待机那一张脸，**不另画侧脸**；只是把这颗头放在侧过来的身体上，脖子接得自然。
- 比例和正面版一样敦实；不要把侧身画瘦、画高。
- **A**：完全侧面（干净的侧身轮廓）；**B**：转得少一点（约 3/4 朝侧面，多露一点胸口和披肩）。

## 狼的侧面怎么画（`kindred-side-wolf.png`）

- **只有狼头**，没有身体、没有腿：**正侧面朝右**（像 `4_league_wolf.png`），鼻尖朝右，**深靛紫的鬃毛往后（画面左边）飘散成一缕缕参差的烟雾状毛尖**；尖耳朝上；**白色骨面具**盖在额头和眼睛上（侧面只看到一只**亮蓝色的眼睛**和面具上的深紫涡纹）；**张着嘴，白色尖牙**，鼻头深紫黑色。
- 颜色、描边、格子大小和正面版里的狼完全一样（`2_front_layers.png` 左边那只），**大小也一样**（约 52 × 74 格）。

## 干净（照正面版和 `5_style.png` 的统一画风）

- 每个 6 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光）；外轮廓一圈 **2 格粗的近黑描边**，里面少用黑（内部分界用材质自己的暗色）；不要抖动、渐变、碎点、零散杂色格；**颜色只用正面版里已有的那些**，不要新增颜色。
- 背景真透明，**alpha 只能是 0 或 255**（不要半透明光晕——上一轮的原画四周有一圈半透明，alpha 从来没到 255）。不要网格线、文字、编号、边框、影子、特效。

## 附图（压缩包 `kindred_model_pack.zip` 里；一次只能附五张时先附 1、3、4、6、5）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_front_grid.png` | 原画 B 逐格读回的造型，放在 6 px 格子上（每 2 格一条浅线、每 10 格一条深线并编号）；紫线 = 弓尖第 2 行，绿线 = 耳尖第 14 行，红线 = 第 167 行下沿，蓝线 = 站立点第 170 列 | **两个角色的样子、颜色、格子大小、比例**；羊的头（3/4 面具）逐格照它 |
| `2_front_layers.png` | 同一个造型分成两层：左边狼、右边羊 | 狼的大小和画法；羊被狼挡住的地方 |
| `3_league_lamb.png` | 英雄联盟的羊转到侧面朝右（待机、跑步两帧） | **羊的侧身怎么转**：毛发拖在后面、腿一前一后、蹄子朝右 |
| `4_league_wolf.png` | 英雄联盟的狼正侧面朝右（两个待机瞬间） | **狼的侧面**：鬃毛怎么往后飘 |
| `5_style.png` | 本包重做后的高清英雄（泽丽、尼菈、奈德丽） | 统一画风：像素粗细、粗描边、敦实 |
| `6_empty_grid.png` | 空格子，同样的行列标线 | 侧身版的画布 |

## 提示词 1：羊的侧身 `kindred-side-lamb-A.png`、`kindred-side-lamb-B.png`（两稿）

附 1、3、6、2、5。

```text
Attached images: 1 this character's approved front design on a fixed grid of 6x6-pixel squares (a thin line every 2 squares, a numbered line every 10; purple line = row 2, green line = row 14, red line = the bottom of row 167, blue line = column 170) - the LOOK, colours, square size and proportions of the huntress on the right, and her HEAD square for square; 3 her 3D model turned to the side, facing right (the idle, then two run frames) - how she looks SIDE-ON; 6 an empty grid with the same lines - the canvas; 2 the same design split in two layers (the wolf on the left, the huntress on the right); 5 other heroes of this game in the same look (style only).
Draw ONLY THE HUNTRESS (no wolf) SIDE-ON, her body turned to face the IMAGE RIGHT, on the same fixed grid: one 1536x1024 LANDSCAPE PNG with a real transparent background (256 x 170 squares of 6x6 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same height as the front design: the mask's ear tips on row 14, the hooves' lowest row 167 (nothing below it), the bow tip about row 2, the standing point (between the hooves) on column 170; at most 130 squares wide.
The huntress: a lamb-masked huntress covered in white fur - exactly the colours, square size, outline and details of image 1. SIDE-ON (like the first frame of image 3): the fluffy WHITE FUR HOOD and the long WHITE SHOULDER FUR streaming BACK behind her (image left), lilac tips; her PALE ICY BLUE-WHITE body turned to the right; her NEAR HAND (image right) holds the BOW UPRIGHT in front of her chest - the bow drawn like in image 1 (dark violet limbs with glowing teal swirls, a pale teal hooked tip curling outward at each end, the thin pale bowstring on her side), ONE STRAIGHT VERTICAL bow; the far arm behind her body, mostly hidden; BLUE-VIOLET GOAT LEGS (bent backwards like a deer's) ONE IN FRONT OF THE OTHER (the near leg in front in full tone, the far leg behind a shade darker), DARK BROWN-BLACK HOOVES pointing RIGHT, both on row 167. THE HEAD STAYS THE SAME 3/4 MASK HEAD AS IN THE FRONT DESIGN, square for square (the dark violet lamb mask, the pointed ears, the pale crescent mark, BOTH glowing teal eyes visible) - every frame of this game keeps the idle's face, no separate profile face - only placed on the side-on body with a natural neck. Keep the front's STOCKY proportions; do not make her thinner or taller.
Clean like image 1 and image 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares, no specks, no dithering, no gradients, ONLY the colours of image 1. No wolf, no effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Make TWO takes, A and B: A turned fully side-on (a clean profile body), B turned a little less (about three quarters toward the side, a bit more of the chest and fur cape showing).
```

## 提示词 2：狼的侧面 `kindred-side-wolf.png`

附 2、4、6、1、5。

```text
Attached images: 2 an approved design split in two layers - the WOLF on the left is the one to draw (its colours, square size, outline and size), the huntress on the right is not drawn here; 4 the wolf's 3D model in profile facing right (two idle moments) - how it looks SIDE-ON; 6 an empty grid of 6x6-pixel squares with numbered lines - the canvas; 1 the same design whole; 5 other heroes of this game in the same look (style only).
Draw ONLY THE WOLF in PROFILE facing the IMAGE RIGHT, on the same fixed grid: one 1536x1024 LANDSCAPE PNG with a real transparent background (256 x 170 squares of 6x6 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The SAME SIZE as the wolf of image 2: about 52 squares tall and 74 squares long from the nose tip to the last mane tuft; its nose tip near column 110, row 100; nothing touching the canvas edges.
The wolf: ONLY A BIG WOLF HEAD, no body, no legs - exactly the colours, square size and outline of the wolf in image 2. In profile (like image 4): the nose pointing right; the DARK INDIGO-VIOLET shaggy mane streaming back to the image left and breaking into ragged SMOKY TUFTS like trailing flames; a POINTED EAR up; the WHITE BONE MASK over its brow and eye with the dark violet swirl mark; ONE GLOWING BRIGHT BLUE EYE; the jaws open with WHITE FANGS; a dark violet-black nose.
Clean like images 2 and 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette, every detail at least 2x2 squares, no specks, no dithering, no gradients, ONLY the colours of image 2. No huntress, no effects, no glow, no background, no ground, no shadow, no text, no grid lines.
```

## 交回前请检查

- 三张图都是 1536×1024、6 px 格子对齐左上角、每格一个颜色、**alpha 只有 0 / 255**。
- 羊：耳尖第 14 行、蹄底第 167 行、站立点第 170 列、弓尖约第 2 行，最宽不超过 130 格；身体真的转向右边（毛发拖在左边、弓竖直在身前、腿一前一后、蹄子朝右）；**头和正面版是同一颗 3/4 面具头**（两只青绿眼都看得见）；颜色只用正面版的；图里没有狼。
- 狼：正侧面朝右、和 `2_front_layers.png` 里的狼一样大（约 52 × 74 格）、鬃毛往左飘、白骨面具 + 一只蓝眼 + 白牙；图里没有羊。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/kindred-model/`）

- `kindred-side-lamb-A.png`、`kindred-side-lamb-B.png`、`kindred-side-wolf.png`；未经处理的生成原稿放 `outputs/kindred-model/raw/`；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 原稿逐格读回（先在 8 倍下数描边台阶量实际格子大小，再 regrid），检查高度、站立点、头（贴正面的 3/4 面具头，one-face-all-frames）、颜色映射到正面的 40 色调色板；正面 = 原画 B 读回 1:1。狼侧面按正面狼的大小核对。
- 用户选侧身 A / B 后：第 2 步动作条包 MODEL_STRIPS.md 从侧身版出（动作都是侧面朝右，羊和狼各自成层；跑步羊腿按 Caitlyn 的直腿交叉步，狼整块移动）。最后全部帧走 ppu_restyle 到泽丽密度，羊耳尖到蹄底 34 游戏行。
