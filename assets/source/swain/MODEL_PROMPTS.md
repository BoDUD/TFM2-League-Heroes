# 斯维因：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（平时）** 和 **B（恶魔升华）**（`1_picked_A.png`、`1_picked_B.png`），定的大小（每个游戏像素 1.5 格）：
>   - **A：从头发顶到鞋底 60 格**（游戏里 40 行），约 36 格宽。
>   - **B：同一个人、同一个比例**：他本人从头发顶到鞋底也是 60 格；翅膀照原画的大小跟着缩，约 74 格宽，翼尖比头发顶高 2 格左右（共约 62 格高）。
> - 用户还要求**头画大一点**，让脸在游戏里看得清：从头发顶到下巴 **约 15 格**（身高的四分之一；原画里只有七分之一左右）。A、B 里他的头一样大。脸（皮肤部分）占头的一半左右，**不要被白发盖得只剩一条**。身体比例照原画（高个子、宽肩、长大衣），只放大头，不要变成大头娃娃。
> - 我把 A、B 按这个比例直接缩好了（`2_target_A.png`、`2_target_B.png`，每格 12 px），**大小、位置、姿势都对，但糊了**：脸和眼睛糊成几格，白发分不出层次，大衣和胸甲糊成一片深色，衣摆的灰色饰边断了，下巴那里头和领子有一道接缝，B 的翅膀羽片边缘有零散的格子。
> - **这一轮就是在同样的格子上把它们重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**A、B 各画两稿。**

## 大小和位置（照 `2_target_*.png` / `3_layout_*.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A**：**头发顶在 y = 240**（绿线），**下巴在 y ≈ 420**（蓝线），**两只鞋底在 y = 960**（红线）；左右位置照 `2_target_A.png`（人在画布中间）。
- **B**：**他的头发顶在 y = 240**（绿线），**下巴在 y ≈ 420**（蓝线），**两只鞋底在 y = 960**（红线）；翅膀向两边、向上张开，翼尖最高在 y ≈ 216，左右从 x ≈ 60 到 x ≈ 950，位置照 `2_target_B.png`。他本人的大小、位置和 A 一样。

## 要画清楚的地方

- **头**（`4_head.png`，A、B 一样）：
  - **银白长发**向后梳、两侧垂到肩，分 3–4 档（亮白、浅灰、灰、暗灰），一绺绺的方向用档次分出来，不要糊成一片白；发际线高、额头露出来。
  - **偏白的脸**，窄长、颧骨和眉骨的阴影清楚；**两只眼睛一样大、在同一行**（每只至少 2 格宽），眉头紧锁、压低，嘴是 1 格深色线、嘴角向下，下巴清楚。A 的眼睛深色瞳孔带 1 格亮点；**B 的眼睛是红白色发光的亮格**（平涂，不要光晕）。
- **大衣**：近黑偏紫灰，**一定要有偏紫灰的亮边和褶子高光**（3–4 档），高高的翻领，衣摆到脚踝，下沿有**连续的灰色方折纹饰边**（1–2 格宽）；敞开的前襟露出**暗红内衬**（2–3 档）。肩上深色带尖棱的肩甲（暗铜高光）。
- **大衣里面**：深色弧形胸甲，**一道道暗铜色高光**数得出来；腰上深色皮带、方形铜扣；腿上深色护甲、长靴。
- **A 平时**：双手垂在身侧，深色手套，手在大衣袖口外。
- **B 恶魔升华**：
  - 大衣向身后两边张开成**一对恶魔翅膀**：外面是近黑大衣面料（亮边），里面是**暗红内衬**（3 档），翅膀边缘撕成**一片片乌鸦羽毛一样的尖片**，每片尖片的形状清楚，**不要零散的单格**。
  - **近侧（画面左边）是赤红到洋红的恶魔手臂**，五根尖爪张开，3 档红色；远侧手还是深色手套。
  - 胸甲缝里几道**暗红裂纹**（1 格宽）。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包的潘森、卡特琳娜、莫甘娜，每游戏像素 1.5 格，和斯维因一样；弗拉基米尔 1.8 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（银白发、偏白皮肤、近黑紫灰大衣、暗红内衬、暗铜胸甲、赤红恶魔手臂）。大衣很黑，**一定要有亮边**，不然在游戏里会糊成一团。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（乌鸦、光雾、魂屑都不画）。

## 附图（压缩包 `swain_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` / `1_picked_B.png` | 你第 0 步画的 A、B（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` / `2_target_B.png` | 按新大小（头放大）缩到每格 12 px 放在画布上（糊的） | **大小、位置、姿势、头身比**照它，糊的地方重画 |
| `3_layout_A.png` / `3_layout_B.png` | 同一张加网格线：绿线 = 头发顶，蓝线 = 下巴，红线 = 地面 | 对齐网格、头和地面线的位置 |
| `4_head.png` | A 的头（第 0 步读回后 8 倍放大） | 白发、脸、眼睛 |
| `style/5_style_pantheon.png` … `8_style_vladimir.png` | 本包的潘森、卡特琳娜、莫甘娜（每游戏像素 1.5 格）、弗拉基米尔（1.8 格），8 倍放大 | **只看风格**：这个密度下一格有多大、深色衣服怎么留亮边、翅膀怎么画、脸怎么画 |

## 提示词 1：`swain-model-A-1.png`、`swain-model-A-2.png`（平时，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1B approved pixel-art pictures of this character - a tall grim old general with swept-back silver-white hair falling to his shoulders, a narrow pale frowning face, an ankle-length near-black purple-grey greatcoat with a grey meander trim and a dark crimson lining, dark curved chest plates with dark-bronze highlights, a belt with a bronze buckle, dark armoured legs and boots; in 1B the same man in his demon form: the coat flung open behind him into a pair of huge demon wings (black outside, crimson inside, torn raven-feather edges), the near arm a crimson-magenta demon arm with five claws, glowing red-white eyes (the LOOK, the COLOURS and the DETAILS to keep); 2A and 2B the same two pictures shrunk to their final game size on a 1024x1024 canvas, 12 px squares, with a bigger head - the SIZE, the PLACE, the POSE and the HEAD-TO-BODY PROPORTION are right, but they are muddy (the face and eyes blurred, the white hair's shades lost, the coat and chest plates smeared into one dark mass, the hem trim broken, a seam between the head and the collar, stray squares on the wing feathers); 3A and 3B the same with grid lines every 5 squares: the green line = the top of his hair, the blue line = his chin, the red line = the ground; 4 his head enlarged; 5-8 STYLE ONLY: other characters from the same game at this same square density (5-7; 8 a little denser), shown 8x so every square is one pixel - copy their pixel-art look, the lit edges on dark clothes, how wings are drawn (7).
Draw with the image generator ONE clean pixel-art picture of the character in his NORMAL form (picture A): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2A: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of his hair at y 240, his chin at y 420 (the head from the hair's top to the chin about 15 squares - bigger than in image 1A, so his face reads at game size: the pale face about half of the head, not hidden by the hair), both soles on the ground line y 960, standing straight, both gloved hands at his sides - as if a pixel artist redrew image 1A square by square on image 2A's grid.
Make it CRISP and READABLE at this size: the SILVER-WHITE HAIR combed back and falling to the shoulders in 3-4 shades (bright white, light grey, grey, dark grey) showing each lock; the PALE narrow face with clear cheekbone and brow shadows, TWO EYES the same size on the same row (at least 2 squares wide each, dark pupils with a 1-square light), a deep frown, a 1-square dark mouth line turned down, a clear chin; the NEAR-BLACK purple-grey GREATCOAT with PURPLE-GREY LIT EDGES and fold highlights in 3-4 shades, the high lapels, a CONTINUOUS GREY MEANDER TRIM along the hem (1-2 squares), the DARK CRIMSON lining showing at the open front; dark spiked pauldrons with bronze highlights; the dark CURVED CHEST PLATES with countable DARK-BRONZE highlights, a dark belt with a square bronze buckle, dark armoured legs and boots.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`swain-model-B-1.png`、`swain-model-B-2.png`（恶魔升华，两稿）

附同样的图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of the character in his DEMON form (picture B): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2B: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of his hair at y 240, his chin at y 420 (the head about 15 squares from the hair's top to the chin, the same head as in picture A), both soles on the ground line y 960, the man himself exactly as big and in the same place as in picture A; the WINGS spread to both sides and upwards as in image 2B (their tips at most y 216 at the top, from about x 60 to about x 950) - as if a pixel artist redrew image 1B square by square on image 2B's grid.
Make it CRISP and READABLE at this size: the same SILVER-WHITE HAIR and PALE frowning face as in picture A, but BOTH EYES GLOW RED-WHITE (flat bright squares, the same size on the same row, no glow halo); the greatcoat FLUNG OPEN BEHIND HIM INTO A PAIR OF HUGE DEMON WINGS: near-black coat cloth with purple-grey lit edges outside, the DARK CRIMSON lining in 3 shades inside, the edges torn into SHARP RAVEN-FEATHER POINTS, every point a clear shape (no loose single squares); the NEAR arm (image left) a CRIMSON-MAGENTA DEMON ARM in 3 shades with FIVE LONG CLAWS spread, the far hand a dark glove; the dark curved chest plates with dark-bronze highlights and a few 1-square DARK-CRIMSON CRACKS between them; the belt, the bronze buckle, the hem's grey meander trim, the dark armoured legs and boots as in picture A.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no ravens, no mist, no drain beams), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` / `2_target_B.png` 一样：每格 12 px、对齐网格；头发顶 y 240、下巴约 y 420、鞋底 y 960（A、B 都是）；B 的翼尖不高过 y ≈ 216、左右在 x 60–950 之间。
- **头比原画大**（约 15 格），脸看得清：**两只眼睛一样大、同一行**；A、B 里他的头一样大；身体比例照原画。
- 大衣有亮边、衣摆饰边连续；胸甲暗铜高光数得出来；B 的翅膀外黑内红、羽片尖片清楚、恶魔手臂五根爪；外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/swain-model/`）

- `swain-model-A-1.png`、`swain-model-A-2.png`、`swain-model-B-1.png`、`swain-model-B-2.png`；**image_gen 的原始生成图原样放 `outputs/swain-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/swain_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 60 行（不经过脸），和 `2_target_*.png` 并排、按游戏大小和弗拉基米尔、维克托、辛德拉、奥莉安娜、德莱厄斯放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，塔姆 / 芮尔 / 雷克塞的方式）：A 待机、跑 Swain_Run、普攻 Swain_Attack1–3、Q Swain_Spell1、E Swain_Spell3、R Swain_DemonWindup → DemonLand、受击、死亡 Swain_Death；B（附加包整身换图 + 主包 R 期间的出手）：b_idle、b_run、r_attack、r_skill、r_skill2、r_flare、b_hit、b_dead。
