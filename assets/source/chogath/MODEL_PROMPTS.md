# 虚空恐惧 科加斯：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（举镰刀的待机）**（`1_picture_A.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把他画成**游戏里的格子数**：**从举起的镰刀尖到脚底 46 格**，约 70 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、牙、甲片碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **要画两个角度**（同一只科加斯、同样的格子、同样的颜色）：
>   - **3/4 正面朝右**（和 A 一样）：游戏里的待机。
>   - **侧面朝右**（附图 5、6）：身体转成侧面，**头在画面右边**，近侧的前爪、后腿和镰刀臂在前面、颜色亮，远侧的大部分被身体挡住、只露一点、稍暗；四条腿前后错开，爪子朝右。**头保持和 3/4 正面一样**（脸朝右前方、两只青色眼睛都看得见，同样的格子），只把身体转成侧面。他的跑步和攻击动作都从这张侧面图来做。
> - **每格画大：16 px 一格，人物撑满画布宽度**。画布用你平时的 **1254 × 1254**：**镰刀尖 y = 384，眼睛约 y = 816，脚底 y = 1120**。每一格都是 16 × 16 px 的方块，不要用更小的格子画细节。**每个角度画两稿，一共四张。**

## 大小和位置（照 `2_target.png` / `3_layout.png` / `6_side_layout.png`）

- 画布 **1254 × 1254**，**每格 16 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **最高点 y = 384**（绿线，3/4 正面是举起的镰刀刃尖），**眼睛约 y = 816**（蓝线），**脚底 y = 1120**（红线）：最高点到脚底 **46 格**。
- 3/4 正面：宽约 70 格，从 x ≈ 64 到 x ≈ 1184，全在画布里。侧面：照 `6_side_layout.png` 的淡色剪影的大小和地面线（宽约 66 格），放在画布中间。

## 在 46 格里要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头，8 倍）：酒红色甲片头冠（3 档红）；张开的大嘴，**上下两排白牙**，每颗牙 1 格宽、1–2 格长，牙之间留黑色的嘴；嘴里**紫色的舌头**（2 档紫），舌尖 1 格青白色的光；**两只发光的青色眼睛：每只 2 格，一样高**，眼睛上面 1 格深色的眉甲；下巴两边**一对弯的红獠牙**（浅色的牙尖 1–2 格）。
- **身体**：甲壳主体**深紫 / 紫罗兰 3 档**，甲片的边、头冠、爪子、镰刀刃、尾尖**酒红 3 档**，平涂色块；**深紫的腿和尾巴要有偏亮的边**；背上一排紫色骨刺（每根 2–3 格）。
- **两条镰刀臂**：从肩膀长出来、高高举在背上，臂 2 格粗（深紫），末端长长的**红色刃爪**（弯的，2 档红）；远侧那条在后面、稍暗。
- **四条腿**：两只粗前爪撑地、两条短后腿，爪子都是**红色钩爪**（每只 2–3 根，每根 1 格宽）。四只脚都落在地面线上。
- **尾巴**：分节的甲壳尾巴往后伸，尾尖红色尖刺；**尾巴离开地面**，抬在大约后腿膝盖的高度，不要拖在地上。
- **姿势**（3/4 正面）和 A 一样：四肢着地、身子压低，两条镰刀臂高高举起，头低低地往前探、张着嘴；**近侧在画面左前、颜色亮；远侧在后面、稍暗**。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的雷克塞、沃利贝尔、拉莫斯、厄加特——**和科加斯同一个密度 PPU 1.2**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画地刺、声波、尖刺弹）。

## 附图（压缩包 `chogath_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | A 缩到游戏格子数、每格 16 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、46 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 头冠甲片、大嘴、白牙、紫舌头、青色眼睛、红獠牙 |
| `5_side_ref.png` | 英雄联盟原版的待机，接近侧面、朝右 | **侧面图的身体**：身子的长度和厚度、四条腿怎么前后错开、镰刀臂、尾巴 |
| `6_side_layout.png` | 5 缩到同样的 46 格高放在网格上（淡色，只看大小） | 侧面图的大小、位置、地面线 |
| `style/7_style_reksai.png` … `10_style_urgot.png` | 本包的雷克塞、沃利贝尔、拉莫斯、厄加特，8 倍放大（同密度） | **只看风格**：这么粗的格子里甲壳、脸、眼睛、暗色身体的亮边怎么画 |

## 提示词 1：`chogath-model-A-1.png`、`chogath-model-A-2.png`（3/4 正面，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a huge void beast on all fours: dark violet-purple carapace with crimson / wine-red plate edges, a wine-red plated crown, a big low head with a wide open maw, two rows of white fangs, a purple tongue, two glowing cyan eyes, curved red tusks at the jaw; two thick front claws and two short hind legs with red hooked talons; TWO LONG SCYTHE ARMS RAISED HIGH over his back ending in long red blade-claws; purple spines along the back; a long segmented armoured tail with a spiked red tip - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 46 squares from the raised scythe tip to his soles, about 70 squares wide - shown with 16 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the eyes, the fangs and the plates are specks); 3 the same with grid lines every 5 squares: green = the top, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 5 and 6 are for the side view (not this picture); 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel, at this same square density - how carapace, a face, eyes and the lit edges of a dark body are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 16 px, aligned on one straight grid from the canvas corner; the raised scythe tip at y 384, the eyes at about y 816, all four soles on y 1120 - exactly 46 squares from the top to the soles, about 70 squares wide, the figure filling the canvas width as in image 2. Every detail drawn with whole 16 px squares, never with smaller pixels.
With only 46 squares make every part READ: the head - the wine-red plated crown in 3 reds; the wide open maw with an upper and a lower row of WHITE FANGS (each fang 1 square wide, 1-2 long, black mouth between them) and a PURPLE TONGUE (2 purples, a 1-square pale cyan glow at its tip); TWO GLOWING CYAN EYES, each 2 squares, at the SAME height, under a 1-square dark brow plate; a pair of curved red tusks at the jaw with pale tips; the dark violet-purple carapace in 3 shades and the wine-red plate edges in 3 shades, flat areas, the dark legs and tail with LIGHTER EDGES; a row of purple back spines (2-3 squares each); the two SCYTHE ARMS (2 squares thick, dark purple) raised high with long curved red blade-claws, the far one behind a step darker; two thick front claws and two short hind legs, each foot with 2-3 RED HOOKED TALONS (1 square wide), all four feet on the ground line; the segmented tail reaching back, its red spiked tip, the tail HELD OFF THE GROUND at about the hind knee height, never lying on the ground.
THE POSE as image 1: on all fours, the body low, BOTH SCYTHE ARMS RAISED HIGH, the head low and thrust forward with the maw open; 3/4 view facing right (the head on the image right, the face to the front-right), the NEAR limbs in front in full tone, the FAR ones behind a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no ground spikes, no sound wave, no flying spikes), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`chogath-model-side-1.png`、`chogath-model-side-2.png`（侧面朝右，两稿）

附全部图。**用 image_gen 画。**

```text
Same attached images and the SAME character, colours, square size (16 px) and square count as prompt 1 - now SIDE-ON, FACING RIGHT. Image 5 is the original character nearly from the side, facing right: copy from it the BODY seen side-on - the length and depth of the body, the four legs one behind the other, the scythe arms, the tail; image 6 is that view brought to the same 46 squares on the grid (faded: size, place and ground line only).
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px on one straight grid from the canvas corner; the raised scythe tip at y 384, the eyes at about y 816, all soles on y 1120 - exactly 46 squares from the top to the soles, about 66 squares wide, in the middle of the canvas.
THE BODY SIDE-ON: the head on the image right; the NEAR front claw, NEAR hind leg and NEAR scythe arm in front, full tone; the FAR ones mostly hidden behind the body, a step darker; the four legs one behind the other (front claws under the head and shoulders, hind legs under the hips), the talons pointing right; the back spines in profile; both scythe arms raised high over the back; the tail reaching back to the image left, HELD OFF THE GROUND at about the hind knee height.
THE HEAD stays the SAME as the 3/4 view of prompt 1 (the face to the front-right, BOTH glowing cyan eyes visible, the same squares, the open maw with the white fangs and the purple tongue, the red tusks, the crown plates) - only the body is turned side-on.
The same colours and details as prompt 1: dark violet-purple carapace with wine-red plate edges and lighter edges on the dark parts, the red blade-claws and talons, the red tail tip; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 16 px**：最高点 y 384、脚底 y 1120，**最高点到脚底正好 46 格**（数一下台阶数：**如果是 70–110 格就是格子画小了，请重画**）。
- 两只发光的青色眼睛一样高；白牙一颗颗分得清、紫舌头；红獠牙；镰刀臂和红刃爪；红钩爪；尾巴离地；外描边连续；没有任何特效。
- 3/4 正面：镰刀臂高举、头低；侧面：头朝右、近侧的腿和镰刀臂在前、四条腿前后错开、**头和 3/4 正面一样**。

## 交付（`outputs/chogath-model/`）

- `chogath-model-A-1.png`、`chogath-model-A-2.png`、`chogath-model-side-1.png`、`chogath-model-side-2.png`；原始生成图原样放 `outputs/chogath-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/chogath_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px、最高点到脚底 46 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在 12 倍下查脸（眼睛、牙、舌头有没有画在半格上，`codex-face-half-squares`），在游戏大小下和雷克塞、沃利贝尔、拉莫斯、厄加特并排自查（PPU 1.2，38 游戏像素），给用户挑 3/4 和侧面各一张。
- 动作帧自己摆（rig_chogath.py，照 rig_rammus.py / rig_volibear.py：只整格平移、绕半格枢轴的四分之一转、镜像；一张脸用在所有帧）。英雄联盟的动作：普攻 chogath_attack1 / _2；E 恐惧之刺的攻击 chogath_crit；Q 破裂 chogath_spell4；W 野性尖叫 chogath_spell1；R 盛宴 chogath_spell2；跑 chogath_run；死亡 chogath_death（8 帧带落地回弹）；挨打第 1 帧白闪并后退。
