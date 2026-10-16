# 雷克塞：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 你第 0 步画的 **A（地面待机）和 B（钻地）两张都要**（`1_picture_A.png`、`1_picture_B.png`）。用户定的大小是：游戏里 **A 从鳍冠最高点到爪尖 36 像素**，每个游戏像素 1.5 格，也就是要画成 **54 格高**（她很宽，左右约 66 格）。**B 和 A 同一个比例**（鳍冠一样大），约 31 格高、53 格宽。
> - **头放大约 1.3 倍**：A 的嘴和獠牙缩到 54 格只剩几格，看不出是她的脸。这一轮把**头（头盔前端、洋红的嘴、骨白獠牙、下颚两根大獠牙）画大约 1.3 倍**，往前、往下长（盖住前爪的上端没关系）；鳍冠、身体、四肢、尾巴照 A 的比例。
> - 我把 A、B 按这个大小直接缩好了（`2_target_A.png`、`2_target_B.png`，每格 12 px）。**大小、位置、姿势都对，但糊了**：嘴和獠牙糊成几格，甲片的青色高光和纹路断断续续，鳍冠的分节、刀片护甲的边、黑爪都糊在一起；A 的头是单独放大后贴回去的，周围有一道接缝；描边也丢了。
> - **这一轮就是在同样的格子上把它们重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，就像一个像素画师照着第 0 步的原画，在 `2_target_*.png` 的格子里一格一格重画出来。
> - **A 和 B 各画两稿**（一共四张）。

## 大小和位置（照 `2_target_*.png` / `3_layout_*.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A**：**鳍冠最高点在 y = 312**（绿线），**头盔顶在 y ≈ 576**（橙线），**爪尖在 y = 960**（红线）。爪尖落在红线上或略高一点，不能低于它。左右照 `2_target_A.png`：尾巴在左边、末端往上翘，身体在中间，鳍冠高高竖在背上，头在右边压低朝前。
- **B**：**鳍冠最高点在 y = 588**（绿线），**碎土堆的底在 y = 960**（红线）。左右照 `2_target_B.png`：鳍冠在中间，碎土堆左右铺开。B 的鳍冠、甲片和 A 的**一样大、一样的格子、一样的颜色**。

## 要画清楚的地方

- **头**（`4_head.png`，**画大约 1.3 倍**）：
  - **没有眼睛**（她是瞎的）。头顶是**宝蓝色头盔甲片**（3 档，上沿一条亮青色高光），几道尖棱向后。
  - 嘴是**亮洋红色**（3 档），上面一排 **3–4 颗骨白獠牙**（每颗至少 2 格长，米白 + 暗一档），下颚两侧各一根**向前弯的大獠牙**（至少 3 格长）；嘴里深处暗酒红。
- **鳍冠**：镰刀形、向后弯，根部**洋红**、外缘**宝蓝**，2–3 道深色分节槽；鳍尖细而清楚。后面一片小的洋红尖鳍。
- **甲壳**：靛蓝 / 宝蓝（3–4 档），每块甲片**上沿一条亮青色高光**，几条细细的**青色纹路**（1 格宽、连续）；甲片之间暗紫色。
- **四肢**：前肢外侧的**刀片状蓝护甲**轮廓清楚；手腕、脚踝**暗酒红**；每只脚 **3 根黑紫尖爪**（每根至少 2 格长，尖的）。肚子和关节下面暗紫褐色。近侧的腿亮，远侧的腿暗一档，前后看得出来。
- **尾巴**（A）：一节一节的蓝紫甲片，每节一个小尖刺，末端往上翘。
- **碎土堆**（B）：深褐色碎土和碎石块（3 档，块与块之间有暗缝），几块石头上有一条细细的紫色裂纹；碎土堆压在地面线上，左右比鳍冠宽。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包的芮尔、斯莫德、伊莉丝蜘蛛形态、蒙多，每游戏像素 1.5–1.8 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照第 0 步的原画。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步是半透明边，这一轮不行）。不要网格线、文字、边框、影子、地面、特效（虚空能量、紫光、飞尘都不画；B 的碎土碎石照画）。

## 附图（压缩包 `reksai_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_B.png` | 你第 0 步画的 A、B（用户定了两张都用） | **样子、颜色、细节**全照它们 |
| `2_target_A.png` / `2_target_B.png` | 缩到游戏大小（A 的头放大到约 1.3 倍）、每格 12 px 放在画布上（糊的） | **大小、位置、姿势、头的大小**照它们，糊的地方重画 |
| `3_layout_A.png` / `3_layout_B.png` | 同样的图加网格线：A 绿 = 鳍冠顶 y 312，橙 = 头盔顶 y 576，红 = 爪尖 y 960；B 绿 = 鳍冠顶 y 588，红 = 碎土堆底 y 960 | 对齐网格、各部分的高度 |
| `4_head.png` | A 的头（3 倍放大） | 头盔、洋红的嘴、獠牙、下颚大獠牙 |
| `style/5_style_rell.png` … `8_style_drmundo.png` | 本包的芮尔、斯莫德、伊莉丝（蜘蛛）、蒙多（每游戏像素 1.5–1.8 格），8 倍放大 | **只看风格**：这个密度下一格有多大、甲片和爪子怎么分档、描边 |

## 提示词：`reksai-model-A-1.png`、`reksai-model-A-2.png`、`reksai-model-B-1.png`、`reksai-model-B-2.png`

附全部图。**用 image_gen 画。** A 用下面整段；B 用同一段，只把最后的 `POSE` 一句换成 B 的那句、大小位置换成 B 的。

```text
Attached images: 1 (picture_A, picture_B) two approved pixel-art pictures of this creature - a blind Void burrowing beast crouched on four clawed limbs: indigo / royal-blue carapace plates with bright cyan edge highlights and thin teal vein lines, a huge sickle-shaped fin crest on her back curving backwards (magenta at the root turning royal blue), a spiked blue helmet head with NO EYES, a magenta mouth with bone-white fangs and two big curved tusks on the lower jaw, blue blade-like plates on the front limbs, dark wine-red wrists and ankles, three black-purple claws on every foot, a long segmented spiked tail; picture B is the same creature burrowed - only the crest, the upper back and the top of the head out of a heap of broken dark earth and stones (the LOOK, the COLOURS and the DETAILS to keep); 2 (target_A, target_B) the same two shrunk to their final game size on 1024x1024 canvases, 12 px a square, A's HEAD MADE ABOUT 1.3x BIGGER - the SIZE, the PLACE, the POSE and the head size are right, but they are muddy (the mouth and fangs blurred, the cyan highlights and veins broken, the crest's segments, the blade plates and the claws smeared, a seam round A's pasted head, the outline lost); 3 (layout_A, layout_B) the same with grid lines every 5 squares: A green = the crest's top (y 312), orange = the helmet's top (y 576), red = the claw tips (y 960); B green = the crest's top (y 588), red = the bottom of the dirt heap (y 960); 4 the head of picture A enlarged; 5-8 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - copy their pixel-art look.
Draw with the image generator ONE clean pixel-art picture: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of target_A: every square 12 px, aligned on one straight grid starting at the canvas corner, the crest's top at y 312, the helmet's top at y 576, the claw tips on or just above y 960, none below; about 66 squares wide and 54 tall; the tail on the left curling up at its end, the body in the middle, the crest high on the back, the head low and forward on the right - as if a pixel artist redrew picture A square by square on target_A's grid.
Make it CRISP and READABLE at this size: the HEAD about 1.3x bigger than in picture A (grown forward and down, it may overlap the top of the front claw) - NO EYES, a royal-blue helmet of plates in 3 shades with one bright cyan line on its top edge and a few sharp ridges sweeping back; a bright MAGENTA MOUTH in 3 shades with a row of 3-4 BONE-WHITE FANGS (each at least 2 squares long, cream with one darker shade) and two big CURVED TUSKS from the lower jaw pointing forward (at least 3 squares long), dark wine-red deep inside the mouth; the SICKLE FIN CREST, magenta at the root turning royal blue at the edge, 2-3 dark segment grooves, a thin clear tip, a smaller magenta spike fin behind it; the CARAPACE in 3-4 indigo / royal-blue shades, every plate with ONE BRIGHT CYAN LINE on its top edge and a few thin unbroken teal vein lines (1 square wide), dark purple between the plates; the blue BLADE PLATES on the front limbs with clear outlines; DARK WINE-RED wrists and ankles; THREE BLACK-PURPLE POINTED CLAWS on every foot (each at least 2 squares long); the belly and the undersides of the joints dark purple-brown; the near limbs in full tone, the far ones a step darker so front and back read apart; the TAIL in blue-purple plated segments with one small spike each.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing; magenta only for the mouth and the crest.
No effects (no Void energy, no purple glow, no dust), no background, no ground, no shadow, no text, no grid lines. Make two takes.
POSE A (reksai-model-A-1.png, reksai-model-A-2.png): as above.
POSE B (reksai-model-B-1.png, reksai-model-B-2.png): EXACTLY the size, place and pose of target_B instead: the crest's top at y 588, the bottom of the dirt heap on y 960; about 53 squares wide and 31 tall; the SAME square size, colours and crest size as A; only the crest, the upper back and the top of the helmet head show above the ground, ringed by a low heap of BROKEN DARK EARTH AND STONE CHUNKS (dark brown in 3 shades, dark seams between the chunks, a thin purple crack on a few stones) lying on the ground line, wider than the crest.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- A：大小、位置、姿势和 `2_target_A.png` 一样：鳍冠顶 y 312、头盔顶约 y 576、爪尖 y 960（不低于它）、每格 12 px、对齐网格；**头约放大 1.3 倍**，没有眼睛，洋红嘴、骨白獠牙、下颚大獠牙清楚；鳍冠、甲片青色高光、刀片护甲、黑爪、尾巴清楚；近侧亮、远侧暗；外描边连续。
- B：和 `2_target_B.png` 一样：鳍冠顶 y 588、碎土堆底 y 960；格子大小、颜色、鳍冠大小和 A 一样；只露出鳍冠、上背和头顶。
- 颜色照第 0 步；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/reksai-model/`）

- `reksai-model-A-1.png`、`reksai-model-A-2.png`、`reksai-model-B-1.png`、`reksai-model-B-2.png`；**image_gen 的原始生成图原样放 `outputs/reksai-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/reksai_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板）；画大了就按 design_aphelios_cut / dp_keep / design_rell_cut 的 even_cut 删整行整列（不穿过嘴和獠牙）到 54 行，B 按同样的比例，并排给用户挑（用户审核，不要自己判定），和德莱厄斯、赵信、蔚、卡兹克按游戏大小放一起。
- 选定后做动作帧（塔姆 / 芮尔的做法：用造型自己的部件无损摆，做完美了再给用户审核）：鳍冠、刀片护甲、爪子是刚体部件，只平移、整块转直角，不变形；跑步照 RekSai_run（四肢两组交替）；普攻 RekSai_attack1–3（前爪扑咬）；Q 女王之怒 RekSai_spell1，猎物搜寻 RekSai_spell1_burrowed（钻下去再从土里打出一道冲击波）；狂野之噬 RekSai_Spell3（张嘴咬）；W 钻地 = A 沉下去换成 B、土包前进、破土 RekSai_Spell2_unburrow；R RekSai_Spell4_cast → Spell4_hit；死亡 RekSai_death；附加包的地下赶路 = B 的待机 / 跑步（RekSai_idle01_burrowed / run_burrowed）。
