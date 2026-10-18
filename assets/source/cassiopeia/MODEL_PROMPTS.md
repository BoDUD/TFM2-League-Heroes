# 魔蛇之拥 卡西奥佩娅：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户采用了你第 0 步画的 **A（待机：上身挺直、两只金爪抬在胸前、蛇尾平铺在身后地上）**（`1_picked_A.png`），定的大小（每个游戏像素 1.3 格）：
>   - **从尖冠顶到蛇尾贴地的最低处 57 格**（游戏里 44 行），**宽约 60 格**（蛇尾往左边伸得很长）。
> - 比例照原画，不用改。
> - 我把 A 按这个大小直接缩好了（`2_target_A.png`，每格 18 px，放在 1254 × 1254 的画布上），**大小、位置、姿势都对，但糊了**：**两只眼睛只剩几个灰点**，紫色眼影和皮肤混在一起，小毒牙看不出来；兜帽的翠绿和金边碎成一片杂色格，蓝宝石只剩两三格；金爪手套的爪尖断了；腰带两侧的金色弯钩鳍刺断成几截；蛇尾背上的亮绿菱形花纹成了零散的绿点，浅黄绿腹鳞的一节一节横纹没了。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 18 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**画两稿。**

## 大小和位置（照 `2_target_A.png` / `3_layout_A.png`）

- 画布 **1254 × 1254**（就是你平时出图的大小），**每格 18 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **尖冠顶在 y = 180**（绿线），**蛇尾贴地的最低处在 y = 1206**（红线），中间正好 57 格；人从 **x ≈ 72**（尾巴尖）到 **x ≈ 1152**（近侧金爪），位置照 `2_target_A.png`。人几乎占满画布，这是对的——**照这个大小画满，不要缩小留大边**。

## 要画清楚的地方

- **脸**（`4_face.png` 是 A 的头，第 0 步读回后 8 倍放大）：
  - 翠绿兜帽有**连续的金色边框**，额头正中一颗**蓝宝石**（至少 3×3 格，带一格亮蓝高光），头顶**金色尖冠**（2–3 档金色）；
  - 兜帽里的脸是小麦色皮肤，**两只眼睛一样大、一样高、都看得见**：**每只至少 2×2 格**（发白发亮的眼睛 + 一格深色瞳孔），上面一条**紫色眼影**，这是这一轮最重要的一点；
  - 嘴角两颗**白色小毒牙**（各 1 格）；脑后垂下一点墨绿头发。脸不要放大，就照原画的大小。
- **上身**：金色和翠绿的胸衣；上臂和手腕的**金臂环**；**两只金爪手套**，每只能看出 3–4 根弯着的金色爪尖（近侧的手在前面张开，远侧的在胸口）。
- **腰**：一圈**金色腰带**，两侧各伸出一根**向下弯的金色弯钩鳍刺**（每根是连续的一条弧线，2 格粗，不要断）。
- **蛇尾**：从腰下先往下弯，再平平地铺在地面上往左边伸出去，尾巴尖收细。
  - **背鳞**：深翠绿 3–4 档，上面一排**亮绿的菱形花纹**（每个菱形至少 2 格宽，排成一条连续的花纹，不要零散的绿点）；
  - **腹鳞**：在朝向我们的那一侧是一条**浅黄绿色的腹鳞带**，**每隔 2 格一条稍暗的横纹**，一节一节的；
  - 两种颜色之间要分得开；**蛇尾的上沿要有一条偏亮的边**，不然深绿在游戏里会糊成一团；轮廓圆滑、粗细连续变细。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–7（本包的娜美（鱼尾，每游戏像素 1.5 格）、卡莉丝塔（1.4 格）、玛尔扎哈（1.38 格），8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。卡西奥佩娅是每游戏像素 1.3 格，比它们稍粗一点。
- 颜色照原画（小麦色皮肤、翠绿兜帽、金色、蓝宝石、紫眼影、白眼睛、墨绿头发、深翠绿背鳞、亮绿菱纹、浅黄绿腹鳞）。
- **真透明背景，alpha 只能是 0 或 255**（第 0 步的图边缘是半透明的，这次不要）。不要网格线、文字、边框、影子、地面、特效（毒雾、绿光、石化光都不画）。

## 附图（压缩包 `cassiopeia_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` | 按新大小缩到每格 18 px 放在画布上（糊的） | **大小、位置、姿势**照它，糊的地方重画 |
| `3_layout_A.png` | 同一张加网格线：绿线 = 尖冠顶，红线 = 地面 | 对齐网格、尖冠顶和地面线的位置 |
| `4_face.png` | A 的头（第 0 步读回后 8 倍放大） | 兜帽、尖冠、蓝宝石、脸、眼睛、眼影、毒牙 |
| `style/5_style_nami.png` … `7_style_malzahar.png` | 本包的娜美、卡莉丝塔、玛尔扎哈（每游戏像素 1.4–1.5 格），8 倍放大 | **只看风格**：这个密度下一格有多大、鱼尾和鳞片怎么画、暗色材质怎么留亮边 |

## 提示词：`cassiopeia-model-A-1.png`、`cassiopeia-model-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art picture of a SERPENT WOMAN - a human upper body with tan skin on a long thick dark-green snake tail; a cobra-hood helmet, emerald with gold rims, a blue gem on the forehead and a tall gold crest; inside the hood her face with purple eye shadow, pale glowing white eyes and two small white fangs; a little dark teal hair behind; a gold-and-emerald bra top, gold arm bands, gold clawed gauntlets; a gold belt with two down-curved gold hook-fins at her sides; the tail's back dark emerald scales with a brighter green diamond pattern, its belly a band of pale yellow-green segmented scales; upright, both clawed hands raised in front of her chest, the tail bending down from her waist and lying flat on the ground stretching out behind her to the image left (the LOOK, the COLOURS and the DETAILS to keep); 2 the same picture shrunk to its final game size on a 1254x1254 canvas, 18 px squares - the SIZE, the PLACE and the POSE are right, but it is muddy (the eyes a few grey dots, the eye shadow mixed into the skin, the fangs gone, the hood's emerald and gold broken into speckles, the gem two or three squares, the claws broken, the gold hook-fins broken into pieces, the tail's diamond pattern scattered green dots, the belly's segments gone); 3 the same with grid lines every 5 squares: the green line = the crest tip, the red line = the ground; 4 her head enlarged; 5-7 STYLE ONLY: other characters from the same game at a similar square density, shown 8x so every square is one pixel - copy their pixel-art look, a scaled fish tail on the grid (5), lit edges on dark materials.
Draw with the image generator ONE clean pixel-art picture of the serpent woman: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 18 px, aligned on one straight grid starting at the canvas corner, the crest tip at y 180, the lowest part of the tail on the ground line y 1206 (57 squares from the crest tip to the ground), the figure from about x 72 (the tail tip) to about x 1152 (the near claws) - it nearly fills the canvas, keep it that big - upright, both clawed hands raised in front of her chest (the near hand forward with spread claws, the far hand at her chest), the tail bending down from her waist and lying flat on the ground stretching out behind her to the image left, tapering to a thin tip, the face to the front-right - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the emerald hood with a CONTINUOUS gold rim, the blue gem on the forehead at least 3x3 squares with one bright highlight, the gold crest in 2-3 shades; the tan face inside the hood: TWO EYES of the SAME size at the SAME height, both visible, EACH AT LEAST 2x2 SQUARES (pale glowing white with one dark pupil square) under a line of PURPLE EYE SHADOW - the most important point; two small white fangs (one square each); dark teal hair behind; the face exactly as big as in image 1 (never enlarged); the gold-and-emerald bra; the gold arm bands; both gold clawed gauntlets with 3-4 curved claw tips each readable; the gold belt and its two down-curved gold hook-fins, each ONE CONTINUOUS ARC 2 squares thick; the tail's back in 3-4 shades of dark emerald with a CONTINUOUS row of bright green diamonds (each at least 2 squares wide), the pale yellow-green belly band on the side facing us with a slightly darker cross line every 2 squares (segments), the two clearly separated, a LIGHTER EDGE along the top of the tail; the tail's outline smooth and its thickness tapering steadily to the tip.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` 一样：每格 18 px、对齐网格；尖冠顶 y 180、蛇尾最低处 y 1206（57 格）；人几乎占满画布。
- **两只眼睛一样大、一样高、每只至少 2×2 格**、紫眼影；两颗白毒牙；兜帽金边连续、蓝宝石清楚。
- 金爪的爪尖认得出；两根金弯钩鳍刺是连续的弧线；蛇尾背上亮绿菱纹连成一排、腹鳞一节一节、上沿有亮边。
- 外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/cassiopeia-model/`）

- `cassiopeia-model-A-1.png`、`cassiopeia-model-A-2.png`；**image_gen 的原始生成图原样放 `outputs/cassiopeia-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/cassiopeia_model_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 57 行（尖冠到地面，不经过脸和眼睛；删完检查爪子、弯钩鳍刺、尾巴尖这些细的连接处——茂凯的教训），和 `2_target_A.png` 并排、按游戏大小和娜美、辛德拉、莫甘娜、伊莉丝放一起给用户看（用户审核，不要自己判定）。
- 选定后做第 2 步动作（自己用造型部件无损摆，塔姆 / 普朗克 / 悟空的方式：只平移、整块直角转、整行移，不变形、不缺像素）。**没有腿**：跑 = 上身前探、蛇尾整段 S 形摆（英雄联盟 cassiopeia_run），蛇尾按造型自己的一段段整块移；普攻 = 双生毒牙（cassiopeia_spell3 / attack1：手往前一挥），Q 瘟毒爆炸 cassiopeia_spell1，W 剧毒迷雾 cassiopeia_spell2，R 石化凝视 cassiopeia_spell4（身体前探、眼睛发光），受击、死亡 cassiopeia_death。毒牙、毒雾、石化光放第 3 步特效。
