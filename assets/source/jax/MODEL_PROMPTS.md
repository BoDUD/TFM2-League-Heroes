# 贾克斯：按用户的图在游戏尺寸画造型（给 Codex，第 1 步）

> **这一轮只画造型图（A、B 两版），不画动作。** 用户挑好以后，下一轮再按它画动作条（待机、移动、普攻、蓄力一击重击、反击风暴期间的普攻、武器大师期间的普攻、跳斩、反击风暴起手和反击、武器大师砸地、受击、死亡）。
> - 照 `jax_source.png` 画：贾克斯的兜帽和面具、蓝色马尾、服装、颜色、灯柱、站姿都照它来。
> - **直接画游戏尺寸**：兜帽顶到脚底约 34 格，蓝色马尾再高出最多约 7 格（整体约 41 行），8 倍放大，每个像素一个 8×8 方块。你画的每一格就是游戏里的一个像素，Claude 只按格子读回来，不再缩小（之前先画大再缩的英雄，细节都碎成了点）。
> - 这就是卢锡安、薇恩重做那次成功的做法。用户觉得 46–48 行的英雄在游戏里太大，锐雯和薇恩都改成了 40 行，所以这次整体控制在约 41 行。
> - 交回时附 `HANDOFF.md`（用了哪段提示词、颜色表、没做到的地方）和 `manifest.json`（尺寸、脚底行、站位点、不透明区域、四个青色灯眼的坐标、颜色数）。文件名 `jax_design_A.png`、`jax_design_B.png`，最好打成一个 zip。

## 附图（都在压缩包里）

| 文件 | 内容 | 用法 |
|---|---|---|
| `jax_source.png` | 用户给的造型图 | **照它画**：品红兜帽、青铜面具和四个青色灯眼、深紫羽毛领、蓝色马尾、淡紫色的粗壮手臂、护腕、品红背心和披风、腰带和皮包、深蓝裤子、护膝、凉鞋、灯柱（钩形柄尾、紫色握把、发橙光的灯笼、带刺圆盘）、站姿 |
| `tfm2_style_ref_melee.png` | 团战经理2 原版的近战英雄，8 倍 | 像素大小、干净程度、手臂和武器的画法 |
| `size_ref_riven.png` | 本包锐雯的游戏造型（40 行，用户认可的大小），8 倍，1024×1024 | 只看**大小和脚底线**（脚底在第 99 行方块，y = 792–799，红线上面），不要照它的样子 |
| `jax_size_guide.png` | 用户的图直接缩到游戏尺寸（42 行 × 44 列，兜帽顶到脚底 34 行），8 倍，同一张画布、同一条脚底线 | 只看**这个尺寸能放下多少、各部分在哪**；颜色和形状都是糊的，不要照它 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，8 倍 | 干净程度：大块平涂、颜色少、形状清楚 |

## 规则（含之前的英雄学到的）

- **游戏尺寸**：兜帽顶到鞋底约 34 格，马尾最多再高约 7 格；真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 的纯色方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净**：最多 24 种颜色；每种材质 2–3 个平涂色阶；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **只有一圈描边**：整个剪影外面一圈 1 格宽的近黑描边；描边里面的边缘和褶皱用那种材质自己最暗的色阶，**不要再画第二圈黑**。深紫的衬衣、羽毛领和深蓝裤子用带颜色的深紫、深蓝，和描边分开。
- **脸就是面具**（最重要）：兜帽里的青铜面具约 5 格宽、5–6 行高，3/4 朝右；四个青色灯眼**各 1 格**，2×2 排列，横竖之间各隔 1 格金色（3×3：青 金 青 / 金 金 金 / 青 金 青），略偏面具中线右边；青色**只用在灯眼上**（灯笼是橙色）。没有嘴、没有鼻子，面具上除了自己最深的金色棱线不要别的深色格；面具上方留一行兜帽；羽毛领不盖住灯眼。
- **灯柱**：一根连续的长杆，双手握住斜在身前：钩形青铜柄尾在画面左边肩膀高度，前端在画面右边膝盖高度——青铜灯笼（至少 4×4 格，看得到橙光）+ 带刺圆盘（至少 6×6 格，5–6 根刺，中间一根长刺）。杆子 2 格粗，两手之间是紫色缠绳和金环。
- **手和手臂**：两只拳头都清楚地握在杆上（每只至少 3×3 格），手臂从肩膀到拳头至少 3 格粗，和杆子、背心、披风之间有描边隔开；整个人和灯柱连成一块（之前有英雄的手臂画成 1–2 格细线，在游戏里像“无影手”）。
- **披风**：品红和深紫的长条在身后（画面左边），下摆的青铜钩子保留 2–3 个、画大一点，都在脚底线以上。
- **两版**：A 照原图比例（兜帽约 8–9 格高）；B 头大一点，像原版英雄（兜帽顶到面具下约 11 格，面具 6 格宽，灯眼更清楚），躯干和腿相应短一点，兜帽顶到脚底仍约 34 格；服装、武器、披风、颜色不变。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：鞋底最低一行正好在第 99 行方块，下面一格都不能有；灯笼、刺、披风、钩子都在脚底线以上。
- 3/4 正面朝右（照原图），看得到面具和胸口，不画背影。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，就不提名字，只保留外观描述（下面的提示词里已经没有名字）。

## 提示词（A、B 各生成一张，只把 Two versions 那句换成对应的一版）

```text
Four attached images. FIRST: the look of this character - copy his hooded mask, plume, clothes, colors, weapon and stance from it. SECOND: official melee heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size and cleanliness. THIRD: another hero of this game's pack at game size, 8x - use it ONLY for the size and the ground line. FOURTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look.
Task: redraw the FIRST image as clean hand-made pixel art AT GAME SIZE: about 34 pixels from the top of the hood to the soles (the blue plume rises up to about 7 more), true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine filigree.
The character: a hulking warrior with pale lavender-purple skin and huge muscular arms. HEAD: a magenta hood with a spiky dark-purple feather collar round it (a few big spikes, not many thin ones), a small gold clasp on top of the hood and a compact royal-blue ponytail plume sweeping up and back from it (image left); the opening of the hood is filled by a bronze-gold faceplate MASK. BODY: a sleeveless magenta vest with salmon-pink piping and two round gold buttons over a dark purple shirt; a magenta cape behind him (image left) with long dark-purple panels whose hems end in bronze claw-shaped hooks; brown-red leather wraps on both forearms and a brown leather glove-bracer with gold studs on the raised hand; a brown belt with a leather pouch (a gold emblem) and a gold ring; dark navy baggy trousers, a magenta knee pad, bare lavender feet with grey sandal straps and a pink band.
WEAPON (the lamppost): one continuous long pole held diagonally across his body in both fists: its bronze HOOK-shaped cap up and back at shoulder height on the image-left, its forward end low on the image-right at knee height: a bronze lantern cage with a bright orange light inside, then a round bronze disc ringed with spikes and one long spike in its middle. The pole 2 squares thick (mauve-brown, a purple wrapped grip with gold rings between the hands), the lantern at least 4x4 squares with its orange showing, the spiked disc at least 6x6 squares with 5-6 spikes.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades (lavender skin, magenta hood/vest/cape, dark purple shirt/panels/feathers, royal blue plume, bronze-gold mask/buttons/hooks/lantern, brown-red leather, navy trousers, mauve pole, orange lantern light, cyan eye lights); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area. ONE 1-square near-black outline around the whole silhouette only: inside it, edges and folds use the material's own darkest shade - never a second ring of black inside the outline.
Face (most important detail): there is no human face - the MASK is his face: a bronze-gold faceplate about 5 squares wide and 5-6 rows tall inside the magenta hood, turned 3/4 toward the right like the FIRST image, with FOUR bright CYAN eye lights, each exactly one square, in a 2x2 cluster with one gold square between them horizontally and vertically (a 3x3 block: cyan, gold, cyan / gold, gold, gold / cyan, gold, cyan), the cluster a little to the right of the mask's middle; the cyan used NOWHERE else (the lantern light is orange). No mouth, no nose, no dark squares on the mask except its own darkest gold for its facets; one row of hood above the mask; the feather collar never covers the lights.
Arms and hands: both fists clearly on the pole, each fist at least 3x3 squares, each arm at least 3 squares thick from the shoulder to the fist, separated from the pole, the vest and the cape by the outline; the whole figure and the lamppost form one connected piece.
Two versions: A: the FIRST image's proportions (the hood about 8-9 squares tall). B: a bigger head, like the official heroes - the hood about 11 squares tall from its top to under the mask, the mask 6 wide so the four lights read clearly; the torso and legs a little shorter so the hood top to the soles stays about 34 squares; the same clothes, weapon, cape and colors.
Pose and place: the stance of the FIRST image, 3/4 FRONT view facing right (his mask and chest toward us, never his back): feet wide apart, knees bent, hunched forward; the soles on the line 28 squares (224 px) above the bottom of the image, the same ground as the THIRD image, and NOTHING below it (the game draws the health bar there): the lantern, its spikes, the cape panels and the hooks all end above the soles; horizontally centred like the THIRD image.
Layout: one 1024x1024 image per version (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 34 squares from the top of the hood to the soles and at most about 41 with the plume; every square 8x8 on one grid; at most 24 colors; the four cyan lights visible, level in pairs, one square each; the outline one square wide everywhere with no black ring inside it; nothing below the soles.
```

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`.claude/skills/tfm2-hero-mod/scripts/regrid.py`：颜色变化的峰值定格子边界，每格取中心的中位色），**不缩小**；压色板到 24 色以内，只留一圈描边（`tools/art/tidy_codex18.one_outline`），青色只用在四个灯眼；游戏尺寸预览（和原版英雄、包里英雄比大小，在对战场地色和深色头像卡上各看一遍，面具看 6 倍和 12 倍）给用户挑 A/B。
