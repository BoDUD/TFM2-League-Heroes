# 潘森：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户选了你第 0 步画的 **A**（`1_picked_A.png`），定的大小是：游戏里**从头盔顶（不算冠饰）到脚底 40 行**，每个游戏像素 1.5 格。也就是 A 要缩成 **68 × 72 格**（不算冠饰是 60 格高）。
> - 我把 A 直接缩到这个大小（`2_target_auto.png`，每格 12 px），**大小、位置、姿势、长矛和盾的位置都对，但糊了**：头盔的 T 形眼缝没了，弯月冠饰断成几截，描边断断续续，腰带和布帘上的纹章糊成一团，长矛杆时断时续。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，像一个像素画师照着 A 在 68 × 72 的格子里一格一格画出来的。**画两稿**。

## 大小和位置（照 `2_target_auto.png` / `3_layout.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **头盔顶在 y ≈ 240**（绿线，冠饰高出去），**脚底在 y = 960**（红线），两只脚底在同一条线上。
- 人物的宽度、长矛伸出去的位置（左上的矛尾、右下的矛头）、左边飘起的披风、右边的圆盾，都和 `2_target_auto.png` 一样。

## 要画清楚的地方

- **头盔**（`4_helmet.png`）：金色全脸头盔要有**清楚的深色 T 形眼缝**（至少 1 格宽，横一道、竖一道往下），护颊包到下巴；头顶的**弯月冠饰是一整条连续的弯钩**（2 格宽，往上往后弯），两侧短尖角清楚；金色分 3–4 档（亮金高光、金、暗金、古铜阴影），头盔轮廓一圈近黑描边。
- **身体**：古铜色皮肤分 3 档，胸肌、腹肌、手臂的肌肉块看得出来；胸前一道暗红疤；棕色斜挎皮带连续；近侧手臂的金色护肩、护臂清楚。
- **腰和下身**：深红麻绳腰带一整条横过去，正中金色圆环扣；腰前的深蓝布帘上**金色纹章（弯月 + 圆环）**看得出来；金护胫一节一节，露脚趾的凉鞋。
- **长矛**：矛杆**一条连续的金色斜线**（1–2 格宽，不能断），握把处一段深红；右下的**矛头大而清楚**：金色叶形刃 + 淡蓝宝石（宝石 2×2 格左右）；左上的矛尾小尖刺。
- **披风**：深宝蓝到海军蓝 3 档，轮廓干净，末端撕成几条，不要碎点。
- **圆盾**：大金圆盾，一圈一圈的金边看得出来，暗处用古铜，不要糊成一片褐色。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包同密度的卡特琳娜、杰斯、斯莫德、盖伦，8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照 A（金、古铜皮肤、深宝蓝、深红、棕、淡蓝宝石），淡蓝只用在矛头宝石上。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `pantheon_model_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节**全照它 |
| `2_target_auto.png` | A 直接缩到 68 × 72 格、每格 12 px 放在画布上（糊的） | **大小、位置、姿势**照它，糊的地方重画 |
| `3_layout.png` | 同一张加网格线：绿线 = 头盔顶 y 240，红线 = 脚底 y 960 | 对齐网格、头盔顶和脚底的位置 |
| `4_helmet.png` | A 的头盔（读回后 4 倍放大） | 头盔、T 形眼缝、弯月冠饰、尖角 |
| `style/5_style_katarina.png` … `8_style_garen.png` | 本包的卡特琳娜、杰斯、斯莫德（都是每游戏像素 1.5 格）、盖伦，8 倍放大 | **只看风格**：这个密度下一格有多大、描边、分档 |

## 提示词：`pantheon-model-1.png`、`pantheon-model-2.png`（两稿）

附全部 8 张图。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art picture of this character - a Spartan-style warrior in a full-face golden helmet with a tall crescent crest, a bare muscular bronze-skinned torso, a deep blue cape, a golden spear held low in his near hand and a big round golden shield on his far arm (the LOOK, the COLOURS and the DETAILS to keep); 2 the same picture shrunk to its final game size, 68 x 72 squares of 12 px on a 1024x1024 canvas - the SIZE, the PLACE and the POSE are right, but it is muddy (the helmet's eye slit lost, the crest broken, the outline broken, the emblems blurred, the spear shaft broken); 3 the same with grid lines every 5 squares: the green line = the top of the helmet (y 240, the crest rises above it), the red line = the soles (y 960); 4 the helmet of image 1 enlarged; 5-8 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - copy their pixel-art look.
Draw with the image generator ONE clean pixel-art picture of the same warrior: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 12 px, aligned on one straight grid starting at the canvas corner, the helmet's top at y 240, the soles at y 960 on one ground line, the cape flying out to the image left, the spear from the upper left down to its big head at the lower right, the round shield on the image right - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the golden full-face HELMET with a clear dark T-SHAPED EYE SLIT (at least 1 square wide) and cheek guards to the chin, the tall CRESCENT CREST one continuous curved hook 2 squares wide, the short side horns; the gold in 3-4 shades (bright gold highlight, gold, dark gold, bronze shadow); bronze-tan skin in 3 shades with readable chest, abs and arm muscles and a dark red scar on the chest; a continuous brown strap across the chest; the golden pauldron and arm guard on the near arm; the dark red rope belt across the waist with a round golden ring buckle; the deep blue loincloth with a readable golden crescent-and-ring emblem; golden greaves in segments and open-toed sandals; the SPEAR SHAFT one continuous golden diagonal line 1-2 squares thick with a dark red grip, the BIG SPEARHEAD clear: a golden leaf blade with a pale blue gem of about 2x2 squares, a small spike at the butt end; the cape in 3 deep royal-blue to navy shades with ragged ends; the round shield with readable layered golden rims, bronze in the shadow.
One continuous near-black outline round the figure, the spear and the shield; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing; the pale blue only for the gem.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_auto.png` 一样：头盔顶约 y 240、脚底 y 960、每格 12 px、对齐网格。
- 头盔 T 形眼缝清楚、冠饰是连续的一整条弯钩；长矛杆不断、矛头和淡蓝宝石清楚；腰带、纹章看得出来；外描边连续。
- 颜色照 A；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/pantheon-model/`）

- `pantheon-model-1.png`、`pantheon-model-2.png`；**image_gen 的原始生成图原样放 `outputs/pantheon-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/pantheon_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两稿都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），和 `hd/A_ppu15.png` 并排、按游戏大小和盖伦、诺手放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后写第 2 步动作包：造型就是待机，每帧在同样的格子上画（每游戏像素 1.5 格，不再缩放）；长矛和圆盾是刚体部件，动作里只平移和整块转直角，不变形；跑步照英雄联盟（Pantheon_Run_base）；普攻 = 长矛突刺（Pantheon_attack1-3）；Q = 近戳（spell1_hit）和举矛投掷（spell1_longhit）；W = 举盾跃起砸下（spell2 / spell2_hit）；E = 举盾向前、矛从盾边连刺（spell3_loop_nomove_0）+ 盾击（spell3_hit）；R = 蹲下蓄力（spell4）+ 跃起（spell4_leap）+ 落地（spell4_hit）；死亡（Pantheon_Death）。
