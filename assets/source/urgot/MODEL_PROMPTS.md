# 厄加特：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户选了你第 0 步画的 **A**（`1_picked_A.png`，炮臂高举），定的大小是：游戏里**从炮臂最高点到腿尖 42 像素**，每个游戏像素 1.5 格，也就是要画成 **63 格高**（他很宽，左右也约 63 格）。
> - **头稍微放大**：A 里从光头顶到面具下沿只占全身约 9%，缩到 63 格只剩 6 格，红眼睛和面具都看不出来。这一轮头画 **约 9 格高**，肩膀和那只人手跟着稍大一点；底盘、六条腿、炮臂照 A 的比例。
> - 我把 A 按这个大小直接缩好了（`2_target_body.png`，每格 12 px）。**大小、位置、姿势都对，但糊了**：脸、红眼睛、面具糊成几格，绿软管断断续续，铜甲的金边和铆钉、膝炮上的孔、炮臂的尖刺齿轮都糊在一起，头和身体之间还有一道接缝（头是单独放大后贴回去的）。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，就像一个像素画师照着 A，在 `2_target_body.png` 的格子里一格一格重画出来。
> - **画两稿。**

## 大小和位置（照 `2_target_body.png` / `3_layout.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **炮臂最高点在 y = 204**（绿线），**光头顶在 y ≈ 336**（橙线），**面具下沿 / 下巴在 y ≈ 444**（蓝线），**腿尖在 y = 960**（红线）。六个腿尖落在红线上或略高一点，不能低于它。
- 左右位置和 `2_target_body.png` 一样：底盘在画布中间，炮臂从远侧肩膀举过头顶、炮口在右上方向下勾，近侧那只人手搭在底盘前沿，左上方是背后的卷轴鼓。

## 要画清楚的地方

- **头**（`4_head.png`，**画大**，约 9 格高）：
  - **光头**，灰白皮肤，头顶 1–2 道深色缝疤；眉骨重，**一只红眼睛**至少 2 格宽，亮红 + 一格白色高光，眼窝发暗；耳朵 2 格。
  - 鼻子以下是**深钢色防毒面具**（暗青灰 3 档，几道亮的横纹），面具一侧伸出 **3 根亮毒绿软管**（亮绿、绿、深绿 3 档，每根 2 格粗），弯下来插进胸口。
  - 脖子周围**深石板蓝高领**，头后面的**青铜盾板**（金色边 + 暗红色里面）。
  - 红色只用在眼睛和炮臂的小红灯上。
- **上身**：**苍白肌肉**（灰白带一点冷色，3 档），大胸肌、粗上臂，几格深色缝线；近侧那只**人手**搭在底盘前沿，看得出手指（2–3 道缝）。背后的**深褐色卷轴鼓**。
- **炮臂**：深铁灰方块枪管（3 档，上沿亮），**青铜金夹箍**，肘部一圈**金色尖刺**（4–5 根，每根 2 格）的齿轮环，方炮口下面一块短短的下颚，侧面一格小红灯。
- **底盘**：青铜圆桶，**亮金色的上沿和铆钉**，前面深铁灰护板，两个圆铜盖。
- **六条腿**：每条腿上一大块**青铜金盾形护甲**（尖底、金边、两道深色槽、1–2 颗铆钉），盾下面一截**深铁灰膝炮**（炮口一圈，几格深色小孔），腿尖**深钢尖爪**；**毒绿软管**从底盘绕到腿上（每根 2 格粗，连续不断）。近侧三条亮，远侧三条暗一档，前后层次看得出来。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。铜甲上沿和铁管边缘要有亮的高光，放在深色地面上不会糊成一团。

## 干净

- 和附图 5–8（本包的蒙多、潘森、杰斯、斯莫德，都是每游戏像素 1.5 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照 A。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效（子弹、枪口火光、绿光都不画；软管本身是亮绿色的，照画）。

## 附图（压缩包 `urgot_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节**全照它 |
| `2_target_body.png` | A 缩到游戏大小（头放大到约 9 格）、每格 12 px 放在画布上（糊的） | **大小、位置、姿势、头的大小**照它，糊的地方重画 |
| `3_layout.png` | 同一张加网格线：绿 = 炮臂最高点 y 204，橙 = 光头顶 y 336，蓝 = 下巴 y 444，红 = 腿尖 y 960 | 对齐网格、各部分的高度 |
| `4_head.png` | A 的头（4 倍放大） | 光头、红眼、面具、软管、高领、盾板 |
| `style/5_style_drmundo.png` … `8_style_smolder.png` | 本包的蒙多、潘森、杰斯、斯莫德（每游戏像素 1.5 格），8 倍放大 | **只看风格**：这个密度下一格有多大、脸怎么画、描边、金属分档 |

## 提示词：`urgot-model-1.png`、`urgot-model-2.png`（两稿）

附全部 8 张图。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art picture of this character - a huge half-man half-machine walker: the upper body of a pale, heavily muscled bald man with one red eye, a dark steel gas mask with bright toxic-green hoses running into his chest, a high slate-blue collar and a curved bronze plate behind his head; his far arm a giant shotgun cannon raised over his head (dark iron-grey barrel, bronze-gold clamps, a ring of gold spikes, a squared muzzle hooking down); his near human hand resting on a bronze barrel-shaped chassis; a dark brown coiled drum on his back; six mechanical spider legs, each with a big bronze-gold shield-shaped armour plate over a perforated dark iron-grey shotgun barrel and a pointed steel claw, green hoses looping to every leg (the LOOK, the COLOURS and the DETAILS to keep); 2 the same figure shrunk to its final game size on a 1024x1024 canvas, 12 px a square, its HEAD MADE A LITTLE BIGGER (about 9 squares from the bald top to the chin) - the SIZE, the PLACE, the POSE and the head size are right, but it is muddy (the face, the red eye and the mask blurred, the hoses broken, the gold trims, rivets, the barrels' holes and the spiked ring smeared, a seam round the pasted head); 3 the same with grid lines every 5 squares: green = the cannon's top (y 204), orange = the bald top of the head (y 336), blue = the chin (y 444), red = the leg tips (y 960); 4 the head of image 1 enlarged; 5-8 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - copy their pixel-art look.
Draw with the image generator ONE clean pixel-art picture of the same figure: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 12 px, aligned on one straight grid starting at the canvas corner, the cannon's top at y 204, the bald top of the head at y 336, the chin at y 444 (the head about 9 squares tall, bigger than in image 1, so the face reads at game size), the six leg tips on or just above y 960, none below; about 63 squares wide and 63 tall; the chassis in the middle, the cannon arm raised from the far shoulder over the head with its muzzle at the upper right hooking down, the near human hand on the chassis' front edge, the coiled drum at the upper left of the chassis - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the BALD grey-white head with one or two dark scar squares, a heavy brow, ONE RED EYE at least 2 squares wide (bright red with one white highlight square) in a dark socket, an ear of 2 squares; the DARK STEEL GAS MASK in 3 teal-grey shades with a few bright ridges, THREE BRIGHT TOXIC-GREEN HOSES (3 green shades, 2 squares thick each) curving from the mask into the chest; the HIGH SLATE-BLUE COLLAR; the BRONZE PLATE behind the head with a gold rim and a dark red inside; PALE MUSCLES in 3 cold grey-white shades with a few dark stitch squares; the near HUMAN HAND on the chassis with 2-3 finger gaps; the DARK BROWN COILED DRUM; the CANNON ARM - a blocky dark iron-grey barrel in 3 shades with a bright top edge, BRONZE-GOLD clamps, a ring of 4-5 GOLD SPIKES (2 squares each) at the elbow, the squared muzzle with a short jaw under it and ONE RED light square; the BRONZE BARREL CHASSIS with a bright gold top rim and rivets, dark iron-grey front plates, two round copper caps; on each of the SIX LEGS a big BRONZE-GOLD SHIELD PLATE (pointed bottom, gold rim, two dark slots, 1-2 rivets), a DARK IRON-GREY KNEE BARREL under it with a ring muzzle and a few dark holes, a DARK STEEL POINTED CLAW at the tip; TOXIC-GREEN HOSES (2 squares thick, unbroken) looping from the chassis to the legs; the three near legs in full tone, the three far legs a step darker so front and back read apart.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); bright highlights on the bronze plates' top edges and the iron barrels' edges so the shapes read on a dark ground; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing; red only for the eye and the cannon's light.
No effects (no bullets, no muzzle flash, no gas, no glow - the hoses themselves are bright green), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_body.png` 一样：炮顶 y 204、光头顶约 y 336、下巴约 y 444、腿尖 y 960（不低于它）、每格 12 px、对齐网格；**头约 9 格高**，红眼睛、面具、绿软管清楚；炮臂的金刺齿轮、铜甲的金边、膝炮、尖爪清楚；近侧三条腿亮、远侧三条暗；外描边连续。
- 颜色照 A；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/urgot-model/`）

- `urgot-model-1.png`、`urgot-model-2.png`；**image_gen 的原始生成图原样放 `outputs/urgot-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/urgot_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板）；画大了就按 design_aphelios_cut / dp_keep 删整行整列（不穿过脸）到 63 行，并排给用户挑（用户审核，不要自己判定），和德莱厄斯、蒙多、赛恩、塔姆按游戏大小放一起；**每个动作的显示高度**以后都和德莱厄斯比（潘森的教训）。
- 选定后做动作帧（塔姆 / 厄斐琉斯的做法：用造型自己的部件无损摆，做完美了再给用户审核）：炮臂、铜甲、膝炮是刚体部件，只平移、整块转直角，不变形；跑步照 Urgot_RunSlow_Fwd（六条腿两组交替，League 的关节 x 比例）；普攻 Urgot_Attack1_InCombat_Fwd（炮臂压下开火，枪口火光画进帧）；W 机枪连射 attack_w；Q Urgot_Spell1_Fwd；E Urgot_spell3 / Spell3_GrabThrow_Fwd；R Urgot_Spell4_Fwd（上身升起、钻头发射器）；死亡 Urgot_death。腿上的霰弹（被动）走投射物画面，枪口火光烘进他自己的帧（红色方规则）。
