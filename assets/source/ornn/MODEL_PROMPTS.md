# 山脊之下的火焰 奥恩：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（原版大羊角、两把锤）**（`1_picture_A.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把他画成**游戏里的格子数**：**从羊角最高处到脚底 66 格**，宽约 74 格（左边的大锤到右边的羊角尖）。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、鼻子、胡子的小辫和钢环、羊角的符文、青铜胸甲的羊角花纹、皮带扣、铁钳碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **只画 3/4 正面朝右**（和 A 一样；**不画侧面**）：游戏里的待机，所有动作也都从这张图来做。
> - **每格画大：16 px 一格**。画布用你平时的 **1254 × 1254**：**羊角最高处、眼睛、脚底的 y 照 `3_layout.png` 上的三条线**（绿 / 蓝 / 红，数字写在图的上方）。每一格都是 16 × 16 px 的方块，不要用更小的格子画细节。**画三稿。**

## 大小和位置（照 `2_target.png` / `3_layout.png`）

- 画布 **1254 × 1254**，**每格 16 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **羊角最高处**（绿线）到**脚底**（红线）**66 格**；**眼睛**在蓝线上。
- 宽约 74 格，放在 `2_target.png` 的位置；**左边的大锤和右边的羊角尖都不能出画**。

## 在 66 格里要画清楚的地方

- **羊角**（两只都看得见）：深铁灰 3 档，**暗红色的回纹符文**（整格的粗线，不要碎点），**角尖红橙 2 档**；近侧的羊角往画面左边盘开、角尖朝下，远侧的往右上盘成一个弯钩。
- **头**（`4_head.png` 是第 0 步读回的头，8 倍）：一大蓬**深红鬃毛和大胡子**（3 档，亮边偏橙红，一簇簇的毛尖，不要糊成一块红）；**两只发光的红橙色眼睛：每只至少 2 格，一样高，都看得见**（中间一格亮黄的高光），眼睛中间是**深色的羊鼻**；胡子两边**两束小辫，扎着灰色钢环**，胡子下面一对**嵌红宝石的钢环**。
- **身体**：灰蓝 / 淡紫灰的皮肤（3 档，**不要发绿、不要变成纯灰**），粗壮的肩膀和手臂，肩上披着深红的鬃毛；**青铜胸甲上一对盘起来的羊角花纹**（3 档）；**深棕皮背带**、肩上**青铜方扣**；腰上**宽皮带**、挂着**铁钳**；前面**深紫红的皮围裙**；短粗的腿、深紫红的靴子（有偏亮的边，**不要一团黑**）。
- **两只手**：**近侧**（画面左边）的手臂戴**很大的青铜护肩和皮护腕**，手里低低握着**大锤**（钢青色 3 档的方形大锤头，像个小铁砧，深色锤柄）；**远侧**（画面右边）的手臂**从肘部往下是熔岩**（灰蓝皮肤上的红橙裂纹、**烧得通红的拳头**，3 档，最亮一档偏黄），握着**小一些的钢锤**。
- **一圈 1 格的近黑外描边**，连续不断（羊角、锤子也有）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的蒙多、巨型纳尔、格雷福斯——**和奥恩同一个密度 PPU 1.5**——以及沃利贝尔；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（熔岩手臂不往外发光，不画火花）。

## 附图（压缩包 `ornn_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | A 缩到游戏格子数、每格 16 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 羊角最高处，蓝 = 眼睛，红 = 地面 | 对齐网格、66 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 羊角符文、鬃毛、眼睛、鼻子、小辫和钢环 |
| `style/7_style_drmundo.png` … `10_style_volibear.png` | 本包的蒙多、巨型纳尔、格雷福斯（同密度）、沃利贝尔，8 倍放大 | **只看风格**：这么粗的格子里大块头、毛发、胡子、发光的眼睛、金属和深色的亮边怎么画 |

## 提示词：`ornn-model-A-1.png`、`ornn-model-A-2.png`、`ornn-model-A-3.png`（3/4 正面，三稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a huge hunched ram-horned demigod blacksmith with slate blue-grey skin; two enormous curled dark-iron horns with dark red rune grooves and red-orange tips; a shaggy crimson mane and beard with glowing red-orange eyes, a dark ram nose, small braids tied with steel rings and a pair of steel rings set with red gems under the beard; a bronze chest plate cast with curled ram horns, dark brown leather harness straps with bronze square buckles, a wide belt with iron tongs and a dark plum leather apron; short thick legs in dark plum boots; the near arm in a big bronze pauldron and leather bracer holding a big steel-blue hammer low, the far arm molten from the elbow down (red-orange cracks, a red-hot fist) holding a smaller steel hammer - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 66 squares from the top of the horns to his soles, about 74 squares wide - shown with 16 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the eyes, the nose, the braids and rings, the horns' runes, the ram motif on the chest plate, the buckles and the tongs are specks); 3 the same with grid lines every 5 squares: green = the top of the horns, blue = the eyes, red = the ground (their y values are written at the top); 4 the head of image 1 enlarged; 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel (7, 8 and 9 at this same square density) - how a big heavy body, fur, a beard, glowing eyes, metal and the lit edges of dark colours are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 16 px, aligned on one straight grid from the canvas corner; the top of the horns on the green line, the eyes on the blue line, both soles on the red line of image 3 - exactly 66 squares from the top of the horns to the soles, about 74 squares wide, placed as in image 2, the big hammer on the left and the horn tip on the right both whole inside the canvas. Every detail drawn with whole 16 px squares, never with smaller pixels.
With only 66 squares make every part READ: the two HORNS in dark iron grey (3 shades) with thick DARK RED RUNE lines of whole squares and RED-ORANGE TIPS (2 shades), the near horn curling out to the image left with its tip down, the far one curling up to the right into a hook; the SHAGGY CRIMSON MANE AND BEARD in 3 shades (orange-red lit edges, tufts of fur - never one red blob); TWO GLOWING RED-ORANGE EYES, each at least 2 squares with one bright yellow centre square, at the SAME height, both visible, the DARK RAM NOSE between them; two small BRAIDS with grey STEEL RINGS at the sides of the beard and the two red-gem steel rings under it; the slate blue-grey skin in 3 shades (never greenish, never plain grey) on the thick shoulders and arms, crimson fur over the shoulders; the BRONZE CHEST PLATE with its pair of curled RAM HORNS (3 shades); the dark brown leather straps with BRONZE SQUARE BUCKLES; the wide belt with the iron TONGS; the dark plum APRON; the short legs in dark plum BOOTS with lighter edges; the NEAR arm with the BIG BRONZE PAULDRON and leather bracer holding the BIG STEEL-BLUE HAMMER low (a square head like a small anvil, 3 shades, a dark handle); the FAR arm MOLTEN from the elbow down - red-orange cracks and a RED-HOT FIST (3 shades, the brightest yellowish) - holding the SMALLER STEEL HAMMER.
THE POSE as image 1: leaning forward, hunched, legs apart and planted, a hammer hanging low at each side; 3/4 view facing right (the face to the front-right), the NEAR side in front in full tone, the FAR side a step darker.
One continuous 1-square near-black outline round the figure, the horns and the hammers; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no glow round the molten arm, no sparks), no background, no ground, no shadow, no text, no grid lines. Make three takes.
```

## 交回前请检查

- **三张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px**：羊角最高处在绿线、脚底在红线，**羊角最高处到脚底正好 66 格**（数一下台阶数：**如果是 90 格以上就是格子画小了，请重画**）；大锤和羊角尖都在画布里。
- 3/4 正面朝右；两只发光的眼睛一样高、看得见，中间是深色的鼻子；羊角的暗红符文、红橙角尖；深红鬃毛分档、小辫和钢环；青铜羊角胸甲、皮背带方扣、腰带铁钳、深紫红围裙和靴子；近侧大锤、远侧熔岩手臂和小锤；外描边连续；没有任何特效。

## 交付（`outputs/ornn-model/`）

- `ornn-model-A-1.png`、`ornn-model-A-2.png`、`ornn-model-A-3.png`；原始生成图原样放 `outputs/ornn-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ornn_model_done.zip`。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、羊角最高处到脚底 66 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在 12 倍下查脸（**优先用 Codex 原本画的脸，不要自己把脸重画成方块**——薇古丝的教训），在游戏大小下和蒙多、巨型纳尔、沃利贝尔并排自查（PPU 1.5，44 游戏像素），给用户挑一张。
- 用户 2026-10-21 的选择：A 原版大羊角、44 游戏像素、PPU 1.5、只做 3/4、动作由 **Codex 照骨架画关键姿势**（第 2 步 `POSE_PROMPTS.md`，像塞拉斯、格雷福斯）：英雄联盟的 Attack1 / attack2 / attack3（抡锤）、Q spell1（火山裂隙：举锤砸地）、W Spell2 + spell2_attack（风箱烈息：低头喷火）、E spell3 → spell3_dash → spell3_hit（灼热冲撞：压低身子冲刺、撞上）、R spell4_windup → spell4（召唤公羊：举起熔岩手、砸地）、spell4_charge → spell4_hit（第二段：低头前冲、用羊角头槌）、跑 Run、死亡 death。连招（Q 立柱 → E 撞柱、R 召唤 → 头槌）的动作在第 2 步单独列出。
