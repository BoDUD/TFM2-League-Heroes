> 卢锡安重做的第一步（交给 Codex 的原样提示词）。Codex 的交付：`codex_model/redesign_*`；Claude 把它整理成游戏像素的造型（`tools/art/tidy_lucian.py` 的说明），用户确认后做第二步 [`MODEL_REDESIGN_STRIPS.md`](MODEL_REDESIGN_STRIPS.md)。

# 卢锡安：按用户的新立绘重画模型（给 Codex）

> **这一轮只画一张造型图 `lucian_native.png`。** 用户确认后，下一轮再按它画 10 条动作（待机、移动、普攻、连开两枪、Q、E 往前、E 往后、R、受击、死亡），格子、帧数、出手帧和上一轮一样。
> - 用户给了一张新立绘（`lucian_new_look.png`，ChatGPT 生成）：卢锡安的长相、服装、颜色、姿势都照它来。
> - 它的像素格很细（人物约 140 格高），直接缩到游戏尺寸会糊成一团（`lucian_size_guide.png` 就是直接缩的结果：外套的白边和金线被切碎，脸没有五官）。所以要在游戏尺寸**重新画**：保留大块、好认的形状，去掉细花纹。
> - 交回时附 `HANDOFF.md`（用了哪段提示词、颜色表、没做到的地方）和 `manifest.json`（尺寸、脚底行、站位点、不透明区域、眼睛颜色的中心、颜色数）。

## 附图（都在压缩包里）

| 文件 | 内容 | 用法 |
|---|---|---|
| `lucian_new_look.png` | 用户的新立绘 | **照它画**：脸、发型、白色长外套和金边、深色护甲、两把白色手枪、站姿 |
| `tfm2_style_ref_gunner.png` | 团战经理2 原版英雄（用枪、用弩的），8 倍 | 像素大小、干净程度、三行眼睛的画法 |
| `lucian_now_design.png` | 现在游戏里的卢锡安造型，8 倍，1024×1024 | 只看**大小和脚底线**（脚底在第 99 行方块，y = 792–799），不要照它的样子 |
| `lucian_size_guide.png` | 新立绘直接缩到约 40 格高的结果，8 倍，放在同一张画布、同一条脚底线上 | 只看**这个尺寸能放下多少、各部分在哪**；颜色和形状都是糊的，不要照它 |

## 规则（含这几天整理 18 个英雄时学到的）

- **游戏尺寸**：头顶到鞋底约 36 格（举起的枪再高出约 5 格），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 的纯色方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净**：最多 24 种颜色；每种材质 2–3 个平涂色阶（白外套、金边、深色衣裤、灰色护甲、皮肤、头发、外套内衬的紫、手枪的白）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **只有一圈描边**：整个剪影外面一圈 1 格宽的近黑描边；描边里面的边缘和褶皱用那种材质自己最暗的色阶，**不要再画第二圈黑**（原版英雄和 oppi 的包都是这样，内侧一圈黑会显得脏）。
- **脸**（最重要）：头约 11–12 格高；照立绘的短发和两侧剃出的线、浓眉、严肃的表情；**两只眼睛都要看得见**（立绘只画了一只），按原版英雄的三行眼：近处的眼睛 2 格宽、远处的 1 格宽、中间隔一格皮肤，一行眉/睫毛，下面是眼白和深色瞳孔；两只眼睛一样高；眼睛用的颜色只用在眼睛上；**鼻尖不要凸出脸颊的轮廓**（上一版的鼻尖多出一格，像脸边鼓起的疙瘩）；头发不盖住眼睛。
- **双枪**：白色的圣物手枪，黑色枪柄，金色边；一把举在头边、枪口朝上，一把在肩膀高度往前平指（照立绘）；每把枪都是一个清楚的形状（至少 6×3 格），和手臂之间有描边隔开。
- **外套和身体**：白色高领长外套，金色镶边，衣摆在身后（画面左边）飘起、露出紫色内衬；深色背心和金扣的交叉带；深色长裤，灰色护膝带金边，深色靴子；黑手套，白袖子带金色袖口。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：鞋底最低一行正好在第 99 行方块，下面一格都不能有。
- 3/4 正面朝右（照立绘），不画背影。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把 "Lucian" / "League of Legends" 删掉，只保留外观描述。

## 提示词

```text
Four attached images. FIRST: the new look of this character - copy his face, hair, clothes, colors, pistols and stance from it. SECOND: official heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size and cleanliness, and their three-row eyes. THIRD: the character's current game sprite at 8x - use it ONLY for the size and the ground line. FOURTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look.
Task: redraw the FIRST image as clean hand-made pixel art at game size: about 36 pixels from the top of the head to the soles (the raised pistol about 5 more), true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine filigree.
Lucian: a gunslinger with dark brown skin, very short dark hair with lines shaved into the sides, heavy frowning brows. A white high-collared long coat with gold trim, white sleeves with gold cuffs, the coat's tail flowing out behind him (left of the image) showing its violet lining; a dark vest with a gold-buckled cross strap; dark trousers, grey knee guards with gold rims, dark boots, black gloves. Two white relic pistols with black grips and gold edges: one raised beside his head, muzzle up; one held straight out forward at shoulder height.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades (white coat, gold, dark cloth, grey armor, skin, hair, violet lining, pistol white); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area. ONE 1-square near-black outline around the whole silhouette only: inside it, edges and folds use the material's own darkest shade - never a second ring of black inside the outline.
Face (most important detail): the head about 11-12 squares tall; three-row eyes like the SECOND image - the near eye 2 squares wide, the far eye 1 square wide, one square of skin between them; a row of brow, then eye whites with a dark iris; BOTH eyes visible (the FIRST image shows one) and at the same height; the eye colors used nowhere else; the nose tip never sticks out of the cheek line; the hair never covers the eyes.
Pistols: each a clear shape of at least 6x3 squares, separated from the arm by the outline.
Pose and place: the stance of the FIRST image, 3/4 FRONT view facing right; the soles on the line 28 squares (224 px) above the bottom of the image, the same ground as the THIRD image, and NOTHING below it; horizontally where the THIRD image stands.
Layout: one 1024x1024 image (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 36 squares from the top of the head to the soles; every square 8x8 on one grid; at most 24 colors; both eyes visible and level; the outline one square wide everywhere with no black ring inside it; nothing below the soles.
```
