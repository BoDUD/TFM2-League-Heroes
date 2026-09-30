> 薇恩造型的第一步（交给 Codex 的原样提示词，第二版：直接画游戏尺寸）。第一版要的是约 1.7 倍，Codex 画得更大（A 96 格、B 76 格），缩到游戏尺寸后细节碎了，用户要求照 main 上卢锡安重做成功的方式重做（skill 的 art-spec "A design drawn at game size"）。Codex 的交付按原稿自己的格子读回（`.claude/skills/tfm2-hero-mod/scripts/regrid.py`），不缩小。

# 薇恩：按用户的图在游戏尺寸重画造型（给 Codex，第二版）

> **这一轮只画造型图（A、B 两版），不画动作。** 用户确认后，下一轮再按它画动作（待机、移动、普攻、翻滚后的强化普攻、Q 翻滚、E 恶魔审判、R、受击、死亡）。
> - 照 `vayne_source.png` 画：薇恩的长相、墨镜、发型、服装、颜色、两把弩、披风、站姿都照它来。
> - **这次直接画游戏尺寸**（头顶到脚底约 38 格，马尾和背后的大弩再高出约 6 格），8 倍放大，每个像素一个 8×8 方块。上一轮画成了约 1.7 倍（实际 A 约 96 格、B 约 76 格），Claude 再缩小时墨镜、银边和护甲碎成了点，用户要细节清楚、不模糊，所以这次不再缩小：你画的每一格就是游戏里的一个像素。
> - 这就是卢锡安重做那次成功的做法（直接在游戏尺寸画，Claude 只按格子读回像素）。
> - 交回时附 `HANDOFF.md`（用了哪段提示词、颜色表、没做到的地方）和 `manifest.json`（尺寸、脚底行、站位点、不透明区域、镜片颜色的中心、颜色数）。文件名 `vayne_design_A.png`、`vayne_design_B.png`，最好打成一个 zip。

## 附图（都在压缩包里）

| 文件 | 内容 | 用法 |
|---|---|---|
| `vayne_source.png` | 用户给的造型图 | **照它画**：脸和红墨镜、黑紫色高马尾、立领、黑蓝紧身衣和银甲、棕色皮带、红披风、右前臂的银色腕弩、背后的大弩、站姿 |
| `tfm2_style_ref_ranged.png` | 团战经理2 原版的 9 个远程英雄，8 倍 | 像素大小、干净程度、脸的画法 |
| `size_ref_lucian.png` | 本包卢锡安的游戏造型，8 倍，1024×1024 | 只看**大小和脚底线**（脚底在第 99 行方块，y = 792–799，红线下面），不要照它的样子 |
| `vayne_size_guide.png` | 用户的图直接缩到游戏尺寸（头顶到脚底 38 格），8 倍，同一张画布、同一条脚底线 | 只看**这个尺寸能放下多少、各部分在哪**；颜色和形状都是糊的，不要照它 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，8 倍 | 干净程度：大块平涂、颜色少、形状清楚 |

## 规则（含之前的英雄学到的）

- **游戏尺寸**：头顶到鞋底约 38 格（高马尾和背后的大弩再高出约 6 格），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 的纯色方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净**：最多 24 种颜色；每种材质 2–3 个平涂色阶（头发、皮肤、镜片红、嘴唇、黑蓝紧身衣、银甲、棕色皮带、红披风）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **只有一圈描边**：整个剪影外面一圈 1 格宽的近黑描边；描边里面的边缘和褶皱用那种材质自己最暗的色阶，**不要再画第二圈黑**（原版英雄和 oppi 的包都是这样，内侧一圈黑会显得脏）。紧身衣是黑蓝色，用带颜色的深蓝灰，和描边分开。
- **脸**（最重要）：眼睛在墨镜后面：两片红色镜片在同一行，近处（画面左边，她朝右）2–3 格宽、远处 2 格宽，中间 1 格深色镜框，每片 1–2 行高；镜片的亮红**只用在镜片上**（披风、领子内衬和宝石是更深的暗红）；镜片和刘海之间留一行皮肤，刘海不盖住镜片。嘴：脸中线上 1–2 格深红嘴唇，在镜片下面两行；脸颊、下巴不要有别的深色格（之前的英雄出现过下巴两角的阴影连成歪嘴笑）。
- **两把弩**：右前臂的银色腕弩照原图垂在身体左后方，是一个清楚的形状（至少 7×4 格，带 1 格红宝石）；背后的大弩从肩后（画面左边）露出、高过头顶，银色弩臂至少 2 格粗，看得到棕色弩身。弩和手臂、头发、披风之间都有描边隔开。
- **披风**：红色 2–3 个色阶，从肩膀往身后（画面左边）飘，下摆撕破的尖角。
- **两版**：A 照原图比例（头至少 10 格高，墨镜才看得清）；B 按原版英雄的 Q 版比例（头约占头顶到鞋底的三分之一，腿稍长），两把弩、披风、脸和颜色不变。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：鞋底最低一行正好在第 99 行方块，下面一格都不能有；腕弩、披风尖角、大弩都在脚底线以上。
- 3/4 正面朝右（照原图），不画背影。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，就不提名字，只保留外观描述（下面的提示词里已经没有名字）。

## 提示词（A、B 各生成一张，只把 Two versions 那句换成对应的一版）

```text
Four attached images. FIRST: the look of this character - copy her face, hair, glasses, clothes, colors, both crossbows, cape and stance from it. SECOND: official heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size and cleanliness. THIRD: another hero of this game's pack at game size, 8x - use it ONLY for the size and the ground line. FOURTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look.
Task: redraw the FIRST image as clean hand-made pixel art AT GAME SIZE: about 38 pixels from the crown of the head to the soles (the high ponytail and the big crossbow on her back rise up to about 6 more), true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine filigree.
The character: a slim crossbow huntress, pale skin, long straight black hair with a cold violet sheen tied in a HIGH PONYTAIL with a silver-and-red clasp, a side fringe and a lock framing the face; narrow angular GLASSES with glowing RED lenses; dark-red lips; a tall standing collar, black outside, crimson inside; a black-navy leather bodysuit with silver armour pieces (pointed shoulder pauldrons, a chest piece, knee plates) and brown leather straps with silver buckles; a torn CRIMSON cape from the shoulders flowing out behind her (left of the image); black heeled boots with silver toe caps. Her two weapons: a spiky SILVER WRIST CROSSBOW with a red gem strapped on her right forearm - the arm on the image-left, hanging down and back as in the FIRST image; and a BIG SILVER CROSSBOW with a brown wooden stock carried on her BACK, its spiky silver limbs rising behind her shoulder and head on the image-left.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades (hair, skin, lens red, lips, navy suit, silver armour, brown leather, crimson cape); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area. ONE 1-square near-black outline around the whole silhouette only: inside it, edges and folds use the material's own darkest shade - never a second ring of black inside the outline.
Face (most important detail): the eyes are behind the glasses - two RED lenses side by side on the same rows, the near lens (left, she faces right) 2-3 squares wide, the far lens 2 squares wide, one dark square of frame between them, each lens 1-2 rows tall; the lens red is a bright red used NOWHERE else (the cape, collar lining and gems are a deeper crimson); one row of skin between the lenses and the fringe; the fringe never covers the lenses. The mouth: 1-2 squares of dark red lips on the face's middle line, two rows under the lenses; no other dark squares on the cheeks or the jaw (a shadow joining the jaw corners to the chin reads as a grin).
Weapons: the wrist crossbow a clear shape of at least 7x4 squares with one red gem square, the big crossbow's limbs at least 2 squares thick with its brown stock showing; each separated from the arm, hair and cape by the outline.
Two versions: A: the FIRST image's proportions, the head at least 10 squares tall so the glasses read. B: official-hero chibi proportions - the head about a third of the height from the crown to the soles, slightly longer legs; the same crossbows, cape, face and colors.
Pose and place: the stance of the FIRST image, 3/4 FRONT view facing right; the soles on the line 28 squares (224 px) above the bottom of the image, the same ground as the THIRD image, and NOTHING below it (the game draws the health bar there): the wrist crossbow, the cape's torn points and the big crossbow all end above the soles; horizontally where the THIRD image stands.
Layout: one 1024x1024 image per version (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 38 squares from the crown to the soles; every square 8x8 on one grid; at most 24 colors; both lenses visible and level, their red used only in the lenses; the outline one square wide everywhere with no black ring inside it; nothing below the soles.
```

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（颜色变化的峰值定格子边界，每格取中心 3×3 的中位色），**不缩小**；压色板到 24 色以内，只留一圈描边，镜片红只用在镜片；手修脸（两片镜片同高、嘴在中线）。游戏尺寸预览（和原版英雄、包里英雄比大小，在对战场地色和深色头像卡上各看一遍）给用户挑 A/B。
