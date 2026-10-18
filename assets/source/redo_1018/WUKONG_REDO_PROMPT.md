# 齐天大圣 孙悟空：重做定稿（游戏格子上重画，给 Codex 的提示词）

> **用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户在游戏里看了：「猴子在局内很奇怪啊 走路了 平A 放技能 都像一个僵尸」「身形又大走路又奇怪」。原因在定稿的**姿势**：弓着腰、**两只空手往前伸、手指弯着**（像僵尸），金箍棒竖在身边**没有握在手里**（`5_现在的…_像僵尸_不要.png`，每个动作都是这一个姿势整体挪动）。
> - 这次**重画定稿的姿势**，照英雄联盟里悟空的待机（`2_英雄联盟悟空_待机_照这个姿势.png`）：**两腿大大分开、低低地蹲稳、背挺直；远侧（后面）的手握住金箍棒中段，金箍棒从他肩后斜着伸到身后下方；近侧（前面）的手握成拳头举在脸前方护着**，尾巴在身后卷起来，头抬起看前方（右边）。之后所有动作都照新定稿重做，所以这张要画准。
> - **服装和颜色照旧定稿**（`1_旧定稿_服装颜色照它_姿势不要.png`），只是姿势换掉、**人也画小**（用户：「船长猴子局内太大」）。画两稿。

## 大小和位置（照 `4_layout.png`）

- 画布 **1254 × 1254**，**每格 10 px**，网格从画布左上角 (0, 0) 开始对齐（浅灰线每 5 格一条）。
- **头顶那撮头发在 y = 810**（绿线），**两只鞋底在 y = 1200**（红线），中间正好 **39 格（390 px）**。这就是游戏里的大小（32 个游戏像素、每个游戏像素 1.2 格，比原来小 15%），**人在画布上很小，这是对的，不要放大**。尾巴尖、金箍棒两端可以超出这两条线和两边。
- 金箍棒总长约 **36 格**（直的、粗细一样：中间钢段 2 格粗，两头金箍和红色棒头 3 格粗）。
- 人在画布下面中间，四周大片透明是对的。

## 要画的样子

- **姿势照图 2**：两脚分开一大步、膝盖弯、重心低但**背是挺的、胸口朝前**，不是驼背；**远侧的手（在身后）拳头包住金箍棒中段**，金箍棒一头从他近侧肩膀后面露出来、另一头斜向身后下方；**近侧的手握紧拳头、举在脸的右前方**（护在前面的拳头，不是张开的爪子）；**没有张开手指往前伸的手**；尾巴从身后往上卷成一个弯；头抬起、脸朝右前方（3/4 侧脸）。
- **头**：约占身高 1/3（Q 版）；棕色猴毛、头顶一撮往上翘的深棕头发；猴脸：浅粉的脸心，眼睛周围红色，**两只发光的绿眼睛一样大、一样高、都看得见，每只 2 格宽**（1 格亮绿 + 1 格深色），圆耳朵，嘴 1 行（可露 1–2 格白牙）。
- **身体**（照旧定稿的颜色）：大红围巾高领；金红大护臂、银灰圆纹章；远侧肩上一个金色猴头饰；金色胸甲和兽面扣；长长的金色鳞纹前摆、红边，下面暗栗色袍裙；暗钢色圆护膝；紫色鞋子金色鞋带。
- **金箍棒**：橙红棒头、金箍、红色两端、灰色钢段中间，**笔直、轮廓连续、两手握住的地方棒身从拳头前后连贯穿过**。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立杂色格。

## 干净

- 和 `style/` 里的图一样的像素画（**6_style_akshan 是同一个格子密度**，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效、云。

## 附图（压缩包 `wukong_redo_pack.zip`）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_旧定稿_服装颜色照它_姿势不要.png` | 旧定稿（8 倍放大） | **服装、颜色、细节**照它；**姿势不要照它** |
| `2_英雄联盟悟空_待机_照这个姿势.png`、`2b_…另一帧.png` | 英雄联盟里的悟空待机 | **姿势**照图 2：低蹲、后手握棍斜在身后、前手握拳护在前面、尾巴卷起；2b 是同一段待机的另一刻（棍子平握在腰边），参考 |
| `3_英雄联盟悟空_跑步_只看.png` | 英雄联盟里的悟空跑步 | 只看他怎么拿棍子（之后做走路用） |
| `4_layout.png` | 网格、绿线 = 头顶、红线 = 地面 | 大小和位置 |
| `5_现在的idle/run/attack_像僵尸_不要.png` | 现在游戏里的样子 | **不要画成这样**：空手前伸、棍子不在手里 |
| `style/6_style_akshan.png`、`7_style_tahmkench.png`、`8_style_leesin.png` | 本包的阿克尚、塔姆、李青 | 只看**风格和格子密度** |

## 提示词：`wukong-redo-1.png`、`wukong-redo-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 our old pixel-art design of a MONKEY KING warrior - brown monkey fur, a tuft of spiky dark-brown hair sweeping up, a monkey face (a pale pinkish face centre, red round the eyes, two glowing GREEN eyes, round monkey ears), a big red scarf with a high collar; huge gold-and-red arm guards with silver-grey rosette badges, a gold monkey-head ornament on the far shoulder; a gold chest plate with a gold beast-face clasp; a long gold tabard with a scale pattern and a red border over a dark maroon-brown robe skirt; round dark-steel knee guards; purple shoes with gold laces; a long brown tail; his staff with orange-red caps, gold bands, red ends and a grey steel middle - keep its COSTUME, COLOURS and DETAILS, but NOT its pose (hunched, both empty hands reaching forward like a zombie, the staff standing apart); 2 and 2b the same character in the original 3D game - the POSE to follow: a wide low stance, legs far apart and knees bent, the back straight and the chest forward, the FAR (back) hand gripping the middle of the staff, which runs diagonally from behind his near shoulder down and back behind him, the NEAR (front) hand a clenched FIST raised guard-like in front of his face, the tail curled up behind; 3 him running in the 3D game, for reference only; 4 the layout: grid lines every 5 squares, green line = top of his hair tuft, red line = the ground; 5 the current in-game sprites - what NOT to draw; 6-8 STYLE: other characters from the same game at this SAME square density, shown 8x.
Draw with the image generator ONE clean pixel-art picture of the monkey king in the pose of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square 10 px, aligned on one straight grid starting at the canvas corner. The top of the hair tuft at y 810, both soles on the ground line y 1200 (39 squares from the tuft to the soles); the tail tip and the staff ends may go beyond. The figure is SMALL on the canvas, in the lower middle, with wide transparent space around it - do NOT enlarge it.
A chibi head about a third of his height, the face three-quarter turned to the right; TWO glowing green EYES of the SAME size at the SAME height, both visible, EACH 2 SQUARES WIDE (one bright green square and one dark square); round ears; a 1-row mouth. The far fist wrapped round the staff; the near hand a tight clenched fist raised in front of his face; NO open clawed hand reaching forward. The staff STRAIGHT and unbroken, about 36 squares long, the steel middle 2 squares thick, the gold bands and red ends 3 squares thick, passing whole through the far fist. The tail curling up behind him in one smooth curve. The costume and colours of image 1.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing. No effects, no clouds, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- 两张图都是 image_gen 画的；1254 × 1254；真透明背景，alpha 只有 0 / 255。
- **人小**：头顶那撮头发 y 810、鞋底 y 1200（39 格，每格 10 px）。
- **后手握着金箍棒**（棍子直的、不断），**前手是握紧的拳头**；背挺直，不像僵尸。
- 两只绿眼睛一样大、一样高、每只 2 格宽；尾巴卷起；服装颜色和旧定稿一样。

## 交付（`outputs/wukong-redo/`）

- `wukong-redo-1.png`、`wukong-redo-2.png`；**image_gen 的原始生成图原样放 `outputs/wukong-redo/raw/`**；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/wukong_redo_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 在 8 倍下数描边台阶量格子（应是 10 px），按它自己的格子读回；头顶到鞋底应是 39 行左右（PPU 1.2，ORIG_PPU 1.2，`ppu_restyle` 的 wukong 不再缩放 85%）。发给用户挑。定稿后动作重做：走路（照英雄联盟跑步的换皮包）、平 A、Q、E、W、R 转圈、死亡，交给 Codex 照定稿画关键姿势，金箍棒按定稿原样盖章、只做整格移动和直角转。
