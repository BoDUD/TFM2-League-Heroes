# 虚空恐惧 科加斯：第 1 步补画，侧面朝右在游戏格子上重画（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 上一轮你画的 3/4 正面 **A-1 用户选定了**（`5_idle.png`，已经是游戏格子：46 格高、每格 16 px）。
> - 上一轮的两张侧面都**没有按格子画**：侧面-1 用了约 7.5 px 的小格子（115 格高），侧面-2 约 11 px（71 格高）。缩到 46 格以后，整行删的版本头变得特别大、身子挤扁，按比例取色的版本又糊成一片。所以这一轮**只重画侧面**。
> - **样子和姿势照侧面-1**（`1_side_look.png`）：四肢着地朝右、两条镰刀臂高举、背上一排骨刺、尾巴往后伸。**大小、位置照 `2_target.png`**（侧面-1 缩到 46 格，形状对，细节是糊的）。
> - **头一格一格照 `4_idle_head.png` 画**（选定的待机 A-1 的头，24 × 21 格，8 倍放大）：同样的格子、同样的颜色、同样朝右前方、两只青色眼睛都看得见。动作帧里每一帧都用这一个头，所以侧面的头必须和它一样。
> - **颜色和格子密度照 `5_idle.png`**：同样的深紫甲壳、酒红甲片、红钩爪，每格 16 px，**不要用更小的格子**。
> - 画布 **1254 × 1254**，**每格 16 px**：**镰刀尖 y = 384，眼睛约 y = 800，脚底 y = 1120**，最高点到脚底 **正好 46 格**，宽约 72 格。**画两稿。**

## 在 46 格里要画清楚的地方

- **头**：照 `4_idle_head.png` 逐格画（头冠甲片、张开的大嘴、上下两排白牙、紫舌头、两只 2 格的青色眼睛、两边红獠牙）。
- **身体侧面**：近侧的前爪、后腿和镰刀臂在前面、颜色亮；远侧的大部分被身体挡住、只露一点、稍暗；前爪在头和肩膀下面，后腿在屁股下面，四只脚都落在地面线上，爪子朝右。
- **镰刀臂**：两条都高高举在背上（臂 2 格粗，末端弯的红刃爪），远侧那条在后面、稍暗。
- **背上的骨刺**：一排侧面看的紫色骨刺（每根 2–3 格）。
- **尾巴**：往画面左边伸，分节、尾尖红刺；**离开地面**，抬在大约后腿膝盖的高度。
- **一圈 1 格的近黑外描边**，连续不断；每种材质 3 档平涂，深色的腿和尾巴有亮边；没有孤立的单个杂色格。

## 附图（压缩包 `chogath_side_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_side_look.png` | 你上一轮画的侧面-1（格子太小） | **样子、姿势**照它 |
| `2_target.png` | 侧面-1 缩到 46 格、每格 16 px 放在画布上（细节是糊的） | **大小、位置、比例、姿势**照它 |
| `3_layout.png` | 同一张加网格线：绿 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、46 格的高度、地面线 |
| `4_idle_head.png` | 选定的待机 A-1 的头（8 倍，一格 = 8 px） | **头逐格照画** |
| `5_idle.png` | 选定的待机 A-1，每格 16 px 放在画布上 | **颜色、格子大小**照它 |
| `style/7_style_reksai.png` … `10_style_urgot.png` | 本包的雷克塞、沃利贝尔、拉莫斯、厄加特，8 倍放大（同密度） | **只看风格** |

## 提示词：`chogath-side-1.png`、`chogath-side-2.png`（侧面朝右，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier SIDE view of this character - a huge void beast on all fours facing right, dark violet-purple carapace with wine-red plate edges, two long scythe arms raised high over the back ending in red blade-claws, a row of purple back spines, a long segmented tail with a red spiked tip, red hooked talons - its LOOK and POSE are right, but it is drawn with squares far too SMALL (about 7.5 px; 115 squares tall); 2 that side view brought down to the RIGHT count, 46 squares tall, shown with 16 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but its details are muddy; 3 the same with grid lines every 5 squares: green = the top, blue = the eyes, red = the ground; 4 the APPROVED HEAD (from the approved 3/4 view), shown 8x so every square is one 8 px block - 24 squares wide, 21 tall; 5 the APPROVED 3/4 view at the right count with 16 px squares - its colours and its square size are the target; 7-10 STYLE ONLY: other characters from the same game shown 8x, at this same square density.
Draw with the image generator ONE clean pixel-art picture of the character SIDE-ON, FACING RIGHT: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 16 px, aligned on one straight grid from the canvas corner (the same square size as image 5 - NEVER smaller squares); the raised scythe tip at y 384, the eyes at about y 800, all soles on y 1120 - exactly 46 squares from the top to the soles, about 72 squares wide, placed as in image 2.
THE HEAD: copy image 4 SQUARE FOR SQUARE onto the front of the body (the same squares, the same colours, the face to the front-right, both cyan eyes visible, the open maw with the white fangs and the purple tongue, the red tusks, the crown plates) - the same head as image 5.
THE BODY SIDE-ON as image 1: the NEAR front claw, NEAR hind leg and NEAR scythe arm in front in full tone; the FAR ones mostly hidden behind the body, a step darker; the front claws under the head and shoulders, the hind legs under the hips, all four feet on the ground line, the talons pointing right; both scythe arms (2 squares thick) raised high with long curved red blade-claws; a row of purple back spines in profile (2-3 squares each); the segmented tail reaching back to the image left with its red spiked tip, HELD OFF THE GROUND at about the hind knee height.
THE COLOURS of image 5: dark violet-purple carapace in 3 shades, wine-red plate edges in 3 shades, flat areas, the dark legs and tail with LIGHTER EDGES; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px（和 `5_idle.png` 一样大）**：最高点 y 384、脚底 y 1120，**最高点到脚底正好 46 格**（数一下台阶数：**超过 50 格就是格子画小了，请重画**）。
- 头和 `4_idle_head.png` 一样；镰刀臂高举、四条腿前后错开、尾巴离地；外描边连续；没有任何特效。

## 交付（`outputs/chogath-side/`）

- `chogath-side-1.png`、`chogath-side-2.png`；原始生成图原样放 `outputs/chogath-side/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/chogath_side_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、46 行），从 raw/ 按格读回（regrid，`design_chogath_model.py`），颜色对到待机的调色板；头换成待机的头（一张脸用在所有帧）；8 倍下自查腿、镰刀臂、尾巴，给用户挑一张。
