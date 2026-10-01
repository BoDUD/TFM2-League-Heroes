# 阿卡丽：按游戏尺寸画角色像素画（给 Codex 的提示词，新对话）

> **这一轮只画 1 张游戏尺寸的造型图（A、B 两版），不画动作、不画特效。做法和 main 上那 18 个英雄重画时一样（用户认可那 18 个的效果）。**
> - 用户认可的造型原稿是 `akali/akali_source.png`（你之前画的第 4 版 B：修长身材、收尖的脸、琥珀色眼睛、贴脸的青绿面罩、低马尾往左后方甩、亮黄绿蝴蝶结）。原稿是插画尺寸，游戏里英雄只有 40 个像素高：这一轮把它画成游戏里真正用的像素精灵。
> - **用户对上一版最不满意的两点**：脸和眼睛看不清；像素乱、不干净。所以这次：**干净、不要细节**（大块平涂、少颜色、醒目的形状），**眼睛一定要清楚**。
> - 生图原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请你自己整理好**：每个像素一个严格对齐的 8×8 纯色块，所有方块在同一个网格上；透明度只有 0 和 255；不超过 24 色；脚底在参考线上。做不到正好 40 格时，也把最接近的原稿一起交（不要超过 56 格），Claude 可以按格子取回再删行。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）和 `generation_prompts.json`。

## 附图（英雄联盟渲染图、原版英雄对照图只在本地用，不要提交）

| 文件 | 内容 | 用在 |
|---|---|---|
| `akali/akali_source.png` | 你画的造型原稿（用户认可） | 长相：脸、眼睛、发型、服装、武器、颜色、比例 |
| `akali/akali_now_design.png` | 现在游戏里的阿卡丽待机第 1 帧，放大 8 倍（1024×1024，浅灰底） | **只看大小和站位**（40 格高，脚底在第 99 行）；长相不要照它（用户否掉了：太暗、糊） |
| `akali/lol_pose_design.png` | 英雄联盟原模型的待机 | 看清衣服、腰包、武器的结构 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄（上排待机、下排攻击），放大 8 倍 | **像素大小和干净程度照它们** |

## 规则

- **像素尺寸（最重要）**：身高 40 格（从头发最高处到脚底，和现在游戏里的一样高）。按真正的低分辨率像素画来画，再整体放大 8 倍输出：每个像素一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净，不要细节**：最多 24 种颜色（下面的建议色板取自原稿，可以微调）；每种材质 2–3 个平涂色阶（亮、中、暗）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；轮廓 1 个方块宽的近黑色描边，内部深色线条越少越好；这个尺寸下看不清的细节去掉（发丝只要几绺大块，纹身只要一两个卷纹，绳子只要两三道斜纹）。
- **脸（最重要的细节）**：两只眼睛都清楚，每只至少 2 格高（版本 B 3 格高）：白色眼白或高光 + 琥珀色虹膜 + 深色瞳孔，和原稿一样的颜色和神情（斜的睫毛）；两只眼睛在同一行，中间隔开，不能连成一条横杠，不能糊掉；**琥珀色只用在眼睛上**；眼睛下面是青绿面罩，挡住鼻子和嘴，和原稿一样贴着脸往下巴收；刘海不盖住眼睛。
- **手臂和武器从肩膀、胸口伸出**，不挡脸；近侧手（画面左边）握苦无放低，远侧手（画面右边）握镰刀；两把刀都是清楚的形状。
- **脚底线以下什么都不能有**：游戏在脚下画血条。两只脚最低一行在第 99 行（y=792–799），下面一格都不能有。
- 3/4 正面朝右（脸朝右边的敌人），姿势照原稿的待机。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

建议色板（取自原稿，可以微调，一共不超过 24 色）：#0A0A14 outline; hair and trousers #111C3E #182E61 #1A3E8A #1C4AAE #3D72D9; lime bow, trims and wraps #789336 #AEC926 #EFF92A; teal mask and top #063242 #094658 #1E6E7E; skin #E07A45 #FC9C5D #FDC58D; eyes #D46A0A (iris, eyes only) #FDFDFD (eye white, blade glint); red satchel #441221 #A42D2F; rope #7A3A14 #C0602A; lilac tattoos #9B90BF; steel #5F5E69 #B8BCC8。

## 提示词：`akali_native_A.png` 和 `akali_native_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附三张图：`akali/akali_source.png`、`akali/akali_now_design.png`、`style/` 里的原版英雄图（`tfm2_style_ref_martial.png` 和 `tfm2_style_ref_swordsman.png` 最接近）；`akali/lol_pose_design.png` 可以一起附上看结构。

```text
Three attached images. FIRST: the approved design illustration of this character - copy its look exactly: the face, the eyes, the hair, the costume, the colors, the weapons and the proportions. SECOND: our game's current in-game sprite of this character at 8x (every game pixel an 8x8 block) on a 1024x1024 canvas - use it ONLY for the size and the place in the canvas; its look is rejected (dark, muddy, not refined). THIRD: official heroes of the game Teamfight Manager 2 at 8x - match this pixel size and cleanliness: big flat areas, few colors, bold readable shapes.
Task: draw the character of the FIRST image as clean hand-made pixel art at game size: a sprite 40 pixels tall (from the top of the hair to the soles), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid.
Akali (a slim masked ninja girl: layered navy-blue hair with a low ponytail sweeping back to the left, tied with a big bright lime bow with two tails; big amber eyes with angled lashes; a teal cloth mask hugging her face down to the neck, with a lime edge; a teal sleeveless crop top with lime edges, bare tan midriff and arms, a lilac swirl tattoo on the upper arms; lime wrist wraps; a red cylindrical satchel on an orange rope at her hip; teal loincloth panels; baggy blue trousers; lime-wrapped shins; dark blue shoes; a steel kunai held low in her near hand, a steel kama with a curved blade in her far hand).
Pixel rules (most important): true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 24 colors; every material 2-3 flat shades (light, mid, dark); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the whole silhouette and very few inner dark lines. Drop details that do not read at this size.
Palette (taken from the FIRST image, adjust if needed): #0A0A14 outline; hair and trousers #111C3E #182E61 #1A3E8A #1C4AAE #3D72D9; lime bow, trims and wraps #789336 #AEC926 #EFF92A; teal mask and top #063242 #094658 #1E6E7E; skin #E07A45 #FC9C5D #FDC58D; eyes #D46A0A (iris, eyes only) #FDFDFD (eye white, blade glint); red satchel #441221 #A42D2F; rope #7A3A14 #C0602A; lilac tattoos #9B90BF; steel #5F5E69 #B8BCC8.
Face: the eyes clearly visible, each at least 2 squares tall, with the same color and look as in the FIRST image (white, amber iris, dark pupil, angled lashes); both eyes on the same rows, apart, never merged into a bar; the amber used for nothing else; the teal mask covering the nose and mouth as in the FIRST image. Keep the proportions of the FIRST image.
Pose, size and place: the idle stance of the FIRST image, 40 squares tall like the SECOND image, the soles on the same line (the lowest row of the feet at y=792-799, 28 squares above the bottom of the image), horizontally where the SECOND image stands. Nothing below the soles (the game draws the health bar right under the feet). Arms and weapons come out of the shoulders and chest, never across the face. 3/4 FRONT view facing right.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares tall, all squares 8x8 on one grid, at most 24 colors, both eyes visible and clear, big clean flat areas without noise, the weapons easy to read, nothing below the soles.
VERSION A (akali_native_A.png): the proportions of the FIRST image; each eye 2 squares tall.
VERSION B (akali_native_B.png): the head 2 squares bigger than in version A and each eye 3 squares tall, everything else the same, still slim.
```

## Claude 收到后（给 Claude 看）

- 在严格 8×8 网格上的：直接按格读回（`regrid.py` 核对），检查色数、脚底线、眼睛；不在网格上或不是 40 格的：按原稿自己的格子取回，照 `tools/art/design_jax.py` 删到 40 格（脸的行列不删，刀的格子加权）。
- A、B 两版和 main 的英雄放在一起给用户挑；通过后出动作帧包（第 2 步，照 `model_pack18.py` 的动作图部分）。
