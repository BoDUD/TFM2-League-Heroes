# 齐天大圣 悟空：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（悟空待机：半蹲、金箍棒斜向下、远侧手臂张开）**（`1_picked_A.png`），定的大小（每个游戏像素 1.5 格）：
>   - **从头发尖到鞋底 57 格**（游戏里 38 行）；尾巴尖高出头顶，**连尾巴整个人约 70 格高、约 77 格宽**（金箍棒和张开的远侧手臂把人撑宽了）。
> - 比例照原画（Q 版，头连尖刺头发约占身高三分之一），不用改。
> - 我把 A 按这个大小直接缩好了（`2_target_A.png`，每格 15 px，放在 1254 × 1254 的画布上），**大小、位置、姿势都对，但糊了**：**绿眼睛几乎没了**（只剩一两个散格），猴脸的浅粉肉色和眼眶的红混成一片，尖刺头发成了一块棕色，护臂上的银灰圆章只剩灰点，金色前襟的鳞片花纹和红边糊在一起，金箍棒的金箍、灰钢、红棒身断断续续，紫鞋和暗红褐长袍混在一起。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 15 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**画两稿。**

## 大小和位置（照 `2_target_A.png` / `3_layout_A.png`）

- 画布 **1254 × 1254**（就是你平时出图的大小），**每格 15 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **头发尖在 y = 345**（绿线），**两只鞋底在 y = 1200**（红线），中间正好 57 格；**尾巴尖在 y ≈ 150**；人从 **x ≈ 45**（金箍棒下端）到 **x ≈ 1200**（远侧手指），位置照 `2_target_A.png`。人几乎占满画布，这是对的——**照这个大小画满，不要缩小留大边**。

## 要画清楚的地方

- **脸**（`4_face.png` 是 A 的头，第 0 步读回后 8 倍放大）：
  - 深棕色的**尖刺头发**向上翘，3 档颜色，能看出一簇簇的尖；
  - **猴脸的浅粉肉色脸心**清楚，眼眶周围一圈红；
  - **两只绿眼睛一样大、一样高、都看得见**：**每只至少 2×2 格**（亮绿 + 一格白色高光），这是这一轮最重要的一点；
  - 圆圆的猴耳朵（浅粉）；嘴龇着露出一点白牙；**红围巾**竖领包住下巴。脸不要放大，就照原画的大小。
- **护臂**：两只金红护臂（金色的边框、红色的筒身），筒上的**银灰色花纹圆章**要能看出是一个圆章（至少 3×3 格，中间一格亮）；远侧肩膀上的**金色猴头肩饰**（外圈红白）。
- **身体**：金色护胸和中间的**金色兽面扣**（一对绿色小眼睛可以有）；**长长的金色前襟**（金底、两三档鳞片花纹、**红边清楚**、尖角朝下）；两边的**暗红褐长袍下摆**（3 档，**一定要有偏亮的边**）；两块**圆形暗钢护膝**（灰色、有高光）；**紫鞋**和金色鞋带。
- **金箍棒**：**直**、粗细一致（**3 格粗**），从上到下：橙红端头—金箍—红棒身—金箍—**灰钢中段**—金箍—红棒身—金箍—橙红端头，每一段颜色分得开；近侧的棕毛手握在灰钢段上。
- **尾巴**：棕色长尾巴从腰后翘起，弯成一道弧，尾尖浅一些，**和头发、身体之间有描边分开**。
- **远侧手臂**向外张开，棕毛的手指弯着，每根手指能看出来。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–7（本包的嘉文四世、潘森、斯维因，**每游戏像素 1.5 格，和悟空一样**，8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（棕毛、深棕头发、浅粉脸、绿眼、红围巾、金色、红护臂筒、银灰圆章、暗红褐长袍、暗钢护膝、紫鞋、灰钢棒身）。长袍和棕毛很暗，**一定要有亮边**，不然在游戏里会糊成一团。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（分身、筋斗云、旋风、冲击、发光拖尾都不画）。

## 附图（压缩包 `wukong_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` | 按新大小缩到每格 15 px 放在画布上（糊的） | **大小、位置、姿势**照它，糊的地方重画 |
| `3_layout_A.png` | 同一张加网格线：绿线 = 头发尖，红线 = 地面 | 对齐网格、头发尖和地面线的位置 |
| `4_face.png` | A 的头（第 0 步读回后 8 倍放大） | 尖刺头发、猴脸、绿眼睛、猴耳、红围巾 |
| `style/5_style_jarvaniv.png` … `7_style_swain.png` | 本包的嘉文四世、潘森、斯维因（每游戏像素 1.5 格），8 倍放大 | **只看风格**：这个密度下一格有多大、金甲和长兵器怎么画、暗色衣服怎么留亮边 |

## 提示词：`wukong-model-A-1.png`、`wukong-model-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art picture of a MONKEY KING warrior - brown monkey fur, a tuft of spiky dark-brown hair sweeping up, a monkey face (a pale pinkish face centre, red round the eyes, two glowing GREEN eyes, round monkey ears, a snarl with a few white teeth), a big red scarf with a high collar; huge gold-and-red arm guards with silver-grey rosette badges, a gold monkey-head ornament on the far shoulder; a gold chest plate with a gold beast-face clasp; a long gold tabard with a scale pattern and a red border over a dark maroon-brown robe skirt; round dark-steel knee guards; purple shoes with gold laces; a long brown tail curving up behind him; his staff: orange-red caps, gold bands, red ends, a grey steel middle; half crouching, the near hand holding the staff slanted down, the far arm held out with curled fingers (the LOOK, the COLOURS and the DETAILS to keep); 2 the same picture shrunk to its final game size on a 1254x1254 canvas, 15 px squares - the SIZE, the PLACE and the POSE are right, but it is muddy (the green eyes almost gone, the pale face and the red round the eyes mixed, the spiky hair one brown block, the rosettes grey dots, the tabard's scales and red border blurred, the staff's bands broken, the purple shoes lost in the dark robe); 3 the same with grid lines every 5 squares: the green line = the hair tip, the red line = the ground; 4 his head enlarged; 5-7 STYLE ONLY: other characters from the same game at this SAME square density, shown 8x so every square is one pixel - copy their pixel-art look, gold armour and a long polearm on the grid, lit edges on dark cloth.
Draw with the image generator ONE clean pixel-art picture of the monkey king: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 15 px, aligned on one straight grid starting at the canvas corner, the hair tip at y 345, both soles on the ground line y 1200 (57 squares from the hair tip to the soles), the tail tip at about y 150, the figure from about x 45 (the staff's lower end) to about x 1200 (the far fingers) - it nearly fills the canvas, keep it that big - half crouching, the near hand holding the staff slanted down (image left), the far arm out with curled fingers (image right), the tail curving up behind him, the face to the front-right - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the spiky dark-brown hair in 3 shades with clear tufts; the pale pinkish face centre clear, red round the eyes; TWO GREEN EYES of the SAME size at the SAME height, both visible, EACH AT LEAST 2x2 SQUARES (bright green with one white highlight square) - the most important point; round pale monkey ears; a snarl with a few white teeth; the red scarf's high collar round the chin; the face exactly as big as in image 1 (never enlarged); the gold-and-red arm guards with each silver-grey rosette readable as a round badge (at least 3x3 squares with a bright centre); the gold monkey-head ornament on the far shoulder; the gold chest plate and its beast-face clasp; the long gold tabard with 2-3 shades of scale pattern, a CLEAR RED BORDER and its pointed tip; the dark maroon-brown robe skirt in 3 shades with LIGHTER EDGES; round dark-steel knee guards with a highlight; purple shoes with gold laces; the staff STRAIGHT and 3 squares thick all along: orange-red cap - gold band - red - gold band - GREY STEEL middle - gold band - red - gold band - orange-red cap, every part clearly separated, the brown furry near hand on the steel part; the brown tail with a lighter tip, outlined apart from the hair and the body; the far hand's curled fingers readable one by one.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` 一样：每格 15 px、对齐网格；头发尖 y 345、鞋底 y 1200（57 格），尾巴尖约 y 150；人几乎占满画布。
- **两只绿眼睛一样大、一样高、每只至少 2×2 格**；猴脸浅粉清楚；尖刺头发有一簇簇的尖；红围巾竖领。
- 护臂的银灰圆章认得出；金色前襟有鳞片和红边；长袍有亮边；护膝是圆的灰钢；紫鞋。
- 金箍棒直、3 格粗、每一段颜色分得开；尾巴和头发身体分开；远侧手指一根根看得见。
- 外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/wukong-model/`）

- `wukong-model-A-1.png`、`wukong-model-A-2.png`；**image_gen 的原始生成图原样放 `outputs/wukong-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/wukong_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 57 行（头发尖到鞋底，不经过脸和眼睛；删完检查前臂、手腕、尾巴、金箍棒这些细的连接处——茂凯的教训），和 `2_target_A.png` 并排、按游戏大小和嘉文四世、潘森、赵信、李青放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，塔姆 / 茂凯的方式：只平移、整块直角转、整行移，不变形、不缺像素；**金箍棒是刚体**，伸长 = 整格接长同一根的灰钢中段；腿先做材质图再切）：待机（呼吸）、走路（造型自己的整条腿）、普攻 MonkeyKing_attack1 / attack2、Q 粉碎打击 monkeyking_spell1（伸棒戳）、E 腾云突击 monkeyking_spell3（冲刺）、W 真假猴王 monkeyking_spell2（隐身一闪）、R 大闹天宫 monkeyking_spell4（金箍棒伸长转圈的循环）、受击、死亡。分身（正面）、筋斗云、旋风放第 3 步特效。
