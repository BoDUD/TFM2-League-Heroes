# 丽桑卓：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`lissandra/1_lissandra_picture.png`，原画 A：笔直站着，两臂垂在身侧）在**游戏尺寸**重新画。
> - **大小**：从**冠顶到裙摆 40 格**、最宽 30 格（冰冠约 24 格）。她没有腿，**裙摆就是脚底**：裙摆最低一行在第 99 行（y=792–799，红线），裙摆中间在中间那一列（x=512，蓝线）；绿线 = 冠顶，黄线 = 面罩（眼睛那一行），橙线 = 下巴（A 版；B 版这三条都低 2 行，裙摆不变）。大小、姿势、头的大小和位置照 `lissandra/2_target_size.png`（原画按游戏比例重新拼好再缩小的灰剪影：深一点的灰是冰冠和头，中灰是身体和长裙）。
> - **原画是成人比例**（冠顶到下巴只占身高 14%），**游戏里是 Q 版大头**：**版本 A** 冠顶到下巴 **16 格**（冰冠约 6 行、面罩 2 行、下半张脸 3–4 行，脸约 8 格宽，和原版的冰法师、灵媒一个比例）；**版本 B** **14 格**（冰冠约 5 行、脸约 7 格宽）。两版都是 40 格高，身材修长：窄肩、细腰、长裙。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。冰冠、胸甲、长裙在游戏里是深蓝黑色的，要用**深蓝、靛蓝几档颜色加钢蓝亮边**画出冰冠两边的尖刃、胸甲的棱线和裙子的褶，不要糊成一块黑；水晶护肩、发光的手、辫子要亮。去掉这个尺寸看不清的细节：冠前的月牙 = 2–3 格青色，胸甲棱线 = 1 格钢蓝线，裙摆的冰晶 = 底部几个大的锯齿尖。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，冠顶到裙摆只有 40 格**。
> - **脸（最重要）**：英雄联盟里她的眼睛被冰冠的面罩挡住，**不画眼睛**：眼睛那一行是 2 行深色面罩（底边一格钢蓝亮边），下面 2 行淡蓝皮肤、**一格深蓝嘴唇**在脸的中线上、一行皮肤阴影做下巴，下半张脸外面一圈完整描边；**脸上不要有别的深色方块**（面罩下面的一道黑线或一对黑点会看成伤口）。深色的兜帽发绺在脸后面，辫子从头后面出来。
> - **直接按游戏尺寸画**，不要先画大再缩小。`lissandra/7_size_guide.png` 是拼好的原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 `outputs/lissandra-model/`：`lissandra_design_A.png`、`lissandra_design_B.png`（1024×1024）和各自的原尺寸图 `lissandra_design_A_1x.png`、`lissandra_design_B_1x.png`，**生图原稿**（未经脚本拼装的那几张），色板，`HANDOFF.md`（**最后写**，写明每张读回来冠顶到裙摆是多少格、头是多少格），最好再打成一个 zip（`lissandra_design_pack.zip`）。

## 附图（都在压缩包的 `lissandra/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_lissandra_picture.png` | 用户选的原画 A | **长相和姿势**：深蓝黑尖菱形冰冠（钢蓝边、冠前青色月牙）、遮眼面罩、淡蓝下半脸和深蓝嘴唇、冰蓝长辫、青色水晶护肩、深 V 领口胸甲、发光的手、拖地长裙和裙摆冰晶、没有腿 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画按游戏比例重新拼好再缩小的灰剪影；红线 = 裙摆那一行的下沿，蓝线 = 裙摆中间，绿线 = 冠顶（40 格），黄线 = 面罩，橙线 = 下巴（A 版） | **大小、姿势、头的大小和位置照它** |
| `3_quality_bar.png` | main 里的leblanc（43×32）、sona（40×34）、evelynn（41×36）、morgana（45×35）、janna（45×30），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们** |
| `4_tfm2_style.png` | 团战经理2 原版的ice_mage（35×24）、enchanter（35×24）、spirit_caller（35×17）、wind_mage（38×20）、shadowmancer（33×17） ×8 | **冠冕怎么戴在小头上、长袍长裙和发光的手怎么画**：大块平涂、少色、形状清楚 |
| `5_head_ref.png` | 原画的头，放大（1120×580） | 冰冠、面罩、嘴唇、兜帽发绺、辫子的起点 |
| `6_torso_ref.png` | 原画的上身，放大（1180×1020） | 水晶护肩、领口、胸甲棱线、发光的手臂和手 |
| `7_size_guide.png` | 按游戏比例拼好的原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：冠顶到裙摆 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材修长；3/4 正面朝右；两臂垂在身侧，辫子垂在身后。
- **干净**：最多 26 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：冰冠和长裙是深靛蓝，皮肤暗部是灰蓝），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0B0A14 outline (the only near-black); the NAVY-BLACK crown, bodice and gown in navy and indigo shades #151833 #222A4E #34406E #4E5E96 with steel-blue lit edges #7C92C8; the gown's ice-crystal hem in steel blues #2C3C70 #4A64A8 #7F9CDA; pale ice-blue skin #6C8CC0 #9CB8E4 #CFE0F8; the glowing forearms and hands #3FA8E8 #7AD8FF #C8F4FF; the shoulder crystals bright cyan #1E78D0 #40B4FF #A8ECFF with white glints #F2FCFF; the braid pale cyan-white #6FA0C8 #A8D4EE #E2F4FF; the dark hair and hood ridges #1A1830 #2E2C50; the lips dark blue #24305E。
- **裙摆以下什么都不能有**（游戏在脚下画血条）：裙摆在第 99 行，下面一格都不能有。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`lissandra_design_A.png` 和 `lissandra_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`lissandra/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Lissandra, the Ice Witch, a tall slender regal sorceress: a large NAVY-BLACK CROWN-HELM shaped like a wide flat pointed diamond (two long sharp blades reaching out to both sides, the back one longer) with steel-blue edges and a bright cyan crescent mark on its front; the crown comes down at the front as a smooth dark MASK over her eyes (no eyes are seen - that is League's look); below it only the lower face: pale ICE-BLUE skin, dark-blue lips, a calm cold chin; dark ridged hood-locks of hair frame the face; one very long thick BRAID of pale cyan-white hair hangs behind her to her knees (a dark band near its end); bright cyan CRYSTAL spikes on both shoulders; a fitted navy-black bodice with raised steel-blue ridges and a deep V neckline showing pale blue skin; long arms, the forearms and long clawed hands glowing bright cyan; one long navy-black GOWN from the waist to the ground, its lower half breaking into jagged steel-blue ICE-CRYSTAL points. She has NO legs or feet: the gown reaches the ground all round. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat shape in greys - the FIRST image recomposed at GAME proportions and shrunk to game size (dark-mid grey the crown and head, mid grey the body and gown) - use it for her SIZE, her POSE, her HEAD SIZE and her PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look. FOURTH: official heroes of this game at 8x - an ice mage, an enchantress, a spirit caller with an ice crown, a wind mage in a long robe, a shadowmancer - copy how a crown sits on a small head, how a long robe or gown and glowing magic hands are drawn at this size: big flat areas, few colours, bold readable shapes. FIFTH: the FIRST image's head, big - the crown, the mask, the lips, the hood-locks, the braid's start. SIXTH: the FIRST image's torso, big - the shoulder crystals, the neckline, the bodice ridges, the glowing arms and hands. SEVENTH: the SECOND image's composition in the FIRST image's colours, shrunk straight to game size - use it ONLY to see what fits where; it is blurry, do not copy its look.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of the crown to the gown's hem and at most 30 squares across (the crown about 24). Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD and FOURTH images. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: standing perfectly upright and still in 3/4 FRONT view facing image right; both arms hanging close to her sides, the glowing hands beside the gown; the braid hanging down behind her (on the image-left side); the gown falling straight to the ground and widening a little at the hem; the head turned toward the viewer under the crown.
Game proportions: the HEAD line at the end says how many squares from the crown's top to the chin (the crown about a third of that); the rest shares the remaining squares. She is slim and tall: narrow shoulders under the crystals, a slim waist, the long gown; the crown, the shoulder crystals, the braid and the glowing hands drawn big enough to read.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The crown, the bodice and the gown are NAVY-BLACK in the game: draw them in the navy and indigo shades with steel-blue lit edges (never one flat black mass - near-black is only the outline), so the crown's blades, the bodice ridges and the gown's folds read; the crystals, the hands and the braid bright. Drop what does not read at this size: the crown's crescent is 2-3 cyan squares, the bodice ridges 1-square steel-blue lines, the gown's crystals a few big jagged steel-blue points at the bottom.
Palette (from the FIRST image, adjust if needed): #0B0A14 outline (the only near-black); the NAVY-BLACK crown, bodice and gown in navy and indigo shades #151833 #222A4E #34406E #4E5E96 with steel-blue lit edges #7C92C8; the gown's ice-crystal hem in steel blues #2C3C70 #4A64A8 #7F9CDA; pale ice-blue skin #6C8CC0 #9CB8E4 #CFE0F8; the glowing forearms and hands #3FA8E8 #7AD8FF #C8F4FF; the shoulder crystals bright cyan #1E78D0 #40B4FF #A8ECFF with white glints #F2FCFF; the braid pale cyan-white #6FA0C8 #A8D4EE #E2F4FF; the dark hair and hood ridges #1A1830 #2E2C50; the lips dark blue #24305E.
Face (most important detail), as the FIFTH image: under the crown a dark MASK band across the eye line (2 rows, navy with a 1-square steel-blue lit edge along its bottom) - NO eyes; under it two rows of pale-blue skin, ONE dark-blue lips square on the face's middle line, a skin-shadow row for the chin; a clean closed outline round the lower face; NO other dark squares on the face (a dark line or pair of squares under the mask reads as a gash). The dark hood-locks frame the face at the back and the braid starts behind the head.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the hem's lowest row at y=792-799 (square row 99, the red line), the middle of the hem on the middle column (x=512, the blue line), the crown's top on the green line, the mask on the yellow line and the chin on the orange line (version A; version B puts the crown's top, the mask and the chin 2 rows lower and keeps the hem). Nothing below the hem (the game draws the health bar right under it).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the crown's top to the hem (compare with the SECOND image); the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 26 colours; one outline colour; the mask covering the eye line, the lips one dark-blue square; both shoulder crystals, the braid and both glowing hands visible; nothing below the hem.
VERSION A (lissandra_design_A.png): HEAD 16 squares from the crown's top to the chin (a game-size chibi head like the FOURTH image's heroes: the crown about 6 rows, the mask 2 rows, the lower face 3-4 rows, the face about 8 squares wide); 40 squares in all.
VERSION B (lissandra_design_B.png): HEAD 14 squares from the crown's top to the chin (the crown about 5 rows, the face about 7 squares wide), a longer body; 40 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 冠顶到裙摆 40 格（最多 48），A 头 16 格、B 头 14 格；裙摆在第 99 行、裙摆中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png`、`4_tfm2_style.png` 一个像素大小；冰冠和长裙有钢蓝亮边和褶，不是一块黑；
- [ ] 面罩挡住眼睛那一行，下面淡蓝皮肤、一格深蓝嘴唇，脸上没有别的深色方块；
- [ ] 两边水晶护肩、长辫、两只发光的手都看得见；没有腿和脚；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、面罩那几行几列不删），检查色数、裙摆线、脸，只补缺的描边。
- A、B 两版和包里的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
