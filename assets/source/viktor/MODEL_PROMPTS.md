# 维克托：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 B（`viktor/1_picture.png`：英雄联盟的待机，站得笔直，近侧的手竖握深色扭曲长法杖，深红斗篷垂在身后，背后的机械臂收在肩后、三叉金爪在后脑旁边）在**游戏尺寸**重新画。
> - **大小**：**版本 A** 从**金爪顶（他最高的地方）到脚底 40 格**，**版本 B** 42 格。脚底在第 99 行（y=792–799，红线），两脚中间在中间那一列（x=512，蓝线），绿 / 橙线 = 最高点。姿势和位置照 `viktor/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是斗篷下摆）。**不要超过 42 格**：本包的萨勒芬妮、格温画到 45–46 行，在游戏里太大，后来都缩到了 42。
> - **宽度**：整个造型连法杖、斗篷**不能超出两条紫线**：A 最宽 **30 格**，B 最宽 **32 格**（原画缩下来约 24 格，正好）。
> - **头大一点（游戏比例）**：他又瘦又高，照原画的比例头只有 6–7 格高，**看不清面具和眼睛**。请把头（面具 + 头冠）画到 **9–10 格高**，身体相应短一点（腿稍短，像 `3_quality_bar.png` 里的布兰德、泽拉斯），总高度还是 40 / 42 格。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。**身体是偏紫的蓝灰；面具是浅一点的钢蓝 + 白高光；眼睛亮橙；头冠和铠甲片是亮金；披肩是鲜亮的青蓝 + 一枚金徽章；斗篷深红；法杖黑紫 + 一点红和金；机械臂蓝灰，金爪 + 青蓝光核**。去掉这个尺寸看不清的细节：身体上的肌肉纹路 = 不画（只用 2–3 档平涂）；铠甲片 = 胸口一块金、腰一块金、大腿上一条金；法杖的缠绕 = 两档颜色交替；脚 = 每只 4–5 格的深蓝灰，脚踝一圈 1 格金环；手 = 2×3 的深蓝灰块。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，最高点到脚底只有 40（B 42）格**。
> - **头和脸**：3/4 朝右，**蓝灰长喙面具**往右下方伸（面具前端比眼睛靠前 3–4 格），**两只亮橙色的眼睛**（各 1–2 格）清楚看得见；头顶**金色尖角头冠**（中间一个高尖、两边弯角），头冠后面一撮**棕色头发**；**三叉金爪 + 青蓝光核**在后脑勺左上方，只比头冠高一点，一根蓝灰机械臂从肩后连过去。面具不能被挡住。
> - **法杖**：近侧（画面左边那只）手竖握，法杖从手里一直到快到地面（不低于脚底），顶端在肩膀上方弯成两三个钩环（有一点红和金）。**握法杖的手看得见**。
> - **直接按游戏尺寸画**，不要先画大再缩小。`viktor/6_size_guide.png` 是原画直接缩到 40 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 / 42 格时，把最接近的那一张也交来（不要超过 44 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/viktor-model/`：`viktor_design_A.png`、`viktor_design_B.png`（1024×1024）和各自的原尺寸图 `viktor_design_A_1x.png`、`viktor_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来最高点到脚底是多少格、整个造型多宽），最好再打成一个 zip（`viktor_design_pack.zip`）。

## 附图（都在压缩包的 `viktor/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 B | **长相和姿势**：蓝灰长喙面具 + 橙眼、金头冠 + 棕发、青蓝披肩 + 金徽章、深红斗篷、蓝灰身体 + 金铠甲、黑紫扭曲法杖、收在肩后的机械臂 + 三叉金爪 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 A 的大小（最高点到脚底 40 格）的灰剪影（浅灰 = 斗篷下摆）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿 / 橙线 = 最高点，两条紫线 = 最宽的范围（30 格） | **A 的大小、姿势和位置照它** |
| `2_target_B.png` | 同上，B 的大小（42 格），紫线 = 32 格 | **B 的大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的布兰德、泽拉斯、雷克顿、萨勒芬妮、图奇，游戏里现在的样子 ×8，同一条脚底线 | **像素大小、头身比和干净程度照它们**（布兰德 43 行、泽拉斯 44 行，都是中路法师） |
| `4_head.png` | 原画的头和收起的金爪，放大 | 面具、眼睛、头冠、头发、金爪 |
| `5_parts.png` | 原画的机械臂、法杖顶 + 握杖的手、披肩和胸口铠甲、斗篷下摆、两只脚，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到 A 的大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的待机（模型渲染，机械臂是举高的——**不用这个机械臂**） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：最高点到脚底 A 40 格、B 42 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画、头放大**：3/4 正面朝右；站得笔直；近侧手竖握法杖；远侧手垂在身旁、手指微张；斗篷在身后往画面左边垂；机械臂收在肩后，金爪在后脑左上方；**面具、两只手都看得见**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0B0910 outline (the only near-black); body #3E4270 #5B6194 #7E86B8 #A3AAD6; mask #6F86AE #A2B6D6 #DCE6F4 (#DCE6F4 highlight only); eyes #C8400A #FF8A1E; gold #8A5A10 #D49A1E #F7D04A #FFF1A0; shawl #0E4FA8 #1E86E0 #5CC0F4; medallion gold as above; cape #5A0A1E #95142E #C62A44; staff #1A1420 #3A2C40 #6A4A5A, red #A0202A, gold as above; hair #4A2410 #7A4420 #A8662E; claw core #1A8AD0 #4AD8F8 #C8F6FF.
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，法杖尾和斗篷也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`viktor_design_A.png` 和 `viktor_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`viktor/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Viktor, a tall thin hextech inventor, half man half machine: a long BLUE-GREY BEAKED METAL MASK with TWO GLOWING ORANGE EYES, a GOLD SPIKED CROWN with a tuft of BROWN HAIR behind it, a wide BRIGHT CYAN-BLUE SHAWL with a ROUND GOLD MEDALLION, a long DEEP CRIMSON CAPE with a torn hem, a slim violet-tinged BLUE-GREY body with GOLD ARMOUR plates on the chest, waist and thighs, gold rings at the wrists and ankles, bare dark feet; a very long DARK TWISTED STAFF (black-violet, touches of red and gold, its top curled into hooked loops) held upright in his near hand; a thin blue-grey MECHANICAL ARM folded behind his shoulders, its THREE CURVED GOLD CLAWS around a GLOWING CYAN CORE beside the back of his head. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the cape's hem in lighter grey - use it for his SIZE, his POSE and his PLACE in the canvas; everything must fit between the two purple lines. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size, their head-to-body proportions and their crisp, clean look (the first two are mages of this size). FOURTH: the FIRST image's head and folded claw, big - the mask, the eyes, the crown, the hair, the claw. FIFTH: the FIRST image's mechanical arm, the staff's top with the gripping hand, the shawl and chest armour, the cape's hem and the feet, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading, and NOT its raised mechanical arm (keep the FIRST image's folded arm).
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only the TOTAL number of squares (the VERSION line) from his highest point (the claw / the crown) to his soles, and at most the WIDTH number of squares across (staff and cape included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose: standing straight in 3/4 FRONT view facing image right; the NEAR hand (image left) gripping the staff upright, the staff from above his shoulder down to just above the ground; the far arm hanging at his side with the fingers slightly open; the cape hanging behind him toward image left; the mechanical arm folded behind his shoulders, the gold claw above and behind his head, only a little higher than the crown; the mask turned toward the viewer, both eyes visible; both hands visible.
Game proportions: a BIGGER HEAD than the picture - the mask and crown together 9-10 squares tall - and a slightly shorter body (shorter legs), like the mages in the THIRD image, the total height still TOTAL squares; the orange eyes, the crown's spikes, the gold medallion and the claw's cyan core drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no muscle lines, no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the violet-tinged blue-grey body, the lighter steel-blue mask, the bright orange eyes, the bright gold crown and armour, the bright cyan-blue shawl, the deep crimson cape, the black-violet staff, the cyan claw core, the brown hair. Drop what does not read at this size: the body no pattern at all, the armour one gold plate on the chest, one at the waist and one strip on each thigh, the staff's winding two alternating shades, each foot 4-5 dark squares with a 1-square gold ankle ring, each hand a 2x3 dark block.
Palette (from the FIRST image, adjust if needed): #0B0910 outline (the only near-black); body #3E4270 #5B6194 #7E86B8 #A3AAD6; mask #6F86AE #A2B6D6 #DCE6F4 (#DCE6F4 highlight only); eyes #C8400A #FF8A1E; gold #8A5A10 #D49A1E #F7D04A #FFF1A0; shawl #0E4FA8 #1E86E0 #5CC0F4; cape #5A0A1E #95142E #C62A44; staff #1A1420 #3A2C40 #6A4A5A with red #A0202A; hair #4A2410 #7A4420 #A8662E; claw core #1A8AD0 #4AD8F8 #C8F6FF.
Face (most important detail), as the FOURTH image: the head in 3/4, the long beaked steel-blue mask reaching down and to image right (its tip 3-4 squares in front of the eyes), two bright ORANGE eyes (1-2 squares each) clearly visible, the gold spiked crown on top (one tall middle spike, a curved horn each side), the brown hair tuft behind it. Nothing covers the mask.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the highest point on the green/orange line, nothing outside the two purple lines. Nothing below the soles (the game draws the health bar right under them): the staff's foot and the cape stay above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: TOTAL squares from the highest point to the soles (compare with the SECOND image); at most WIDTH squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the mask, the orange eyes, the crown, the shawl's medallion, the gripping hand, the staff, the folded claw with its cyan core and the cape all readable; nothing below the soles.
VERSION A (viktor_design_A.png): TOTAL 40, WIDTH 30 (use the SECOND image 2_target_A).
VERSION B (viktor_design_B.png): TOTAL 42, WIDTH 32 (use the SECOND image 2_target_B); everything else as version A.
```

## 交回前自查

- [ ] 最高点到脚底 A 40 格、B 42 格（最多 44）；A 不超过 30 格宽、B 不超过 32 格宽；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；头（面具 + 头冠）9–10 格高；
- [ ] 长喙面具 + 两只亮橙眼睛 + 金头冠 + 棕发；青蓝披肩 + 金徽章；深红斗篷；金铠甲片；竖握的黑紫法杖、握杖的手看得见；收在肩后的机械臂 + 三叉金爪 + 青蓝光核；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- 先给用户看 Codex 自己整理好的 A、B，再附我按格子读回的版本；和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步：idle run attack skill(Q) skill2(W) skill2_e(E) ult hit dead）。
