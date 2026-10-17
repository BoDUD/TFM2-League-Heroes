# 艾尼维亚：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。上一轮你最后用"格子中心采样"缩出来的 anivia-A/B.png 也一样糊，我们没有用，用的是 raw/ 里的原稿。）
> - 用户采用了你第 0 步画的 **A（平时）** 和 **B（寒霜涅槃的冰蛋）**（`1_picked_A.png`、`1_picked_B.png`，就是你 raw/ 里的原稿），定的大小（每个游戏像素 1.2 格）：
>   - **A：从头冠顶到最低的翼尖 53 格**（游戏里 44 行），两只翅膀张开约 80 格宽。
>   - **B：冰蛋连冰晶巢 26 格高**（游戏里 22 行，是她身高的一半），约 38 格宽。**格子大小和 A 一样**（上一轮 B 的格子比 A 大了快一倍，这次不要）。
> - **比例照原画，头保持原样**（用户原话：「头保持原样」），不要放大头。
> - 我把 A、B 按这个大小直接缩好了（`2_target_A.png`、`2_target_B.png`，每格 11 px），**大小、位置、姿势都对，但糊了**：头冠的冰刺糊成一团、紫色额晶和洋红眼睛只剩一两个散格；翅膀里的冰晶羽毛分不出一片片，深蓝裂纹断断续续；深蓝的身体和爪子糊成一片黑；冰蛋的棱面和冰晶巢的尖块分不清。
> - **这一轮就是在同样的格子上把它们重画清楚**：同样大小、同样位置、同样姿势，**每块 11 px，横平竖直对齐网格**，像一个像素画师照着原画在格子里一格一格画出来的。**A、B 各画两稿。**

## 大小和位置（照 `2_target_*.png` / `3_layout_*.png`）

- 画布 **1024 × 1024**，**每格 11 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A**：**头冠顶（远侧翅膀的翼尖）在 y = 407**（绿线），**最低的翼尖碰到 y = 990**（红线）；两只翅膀从 x ≈ 66 到 x ≈ 946，位置照 `2_target_A.png`。
- **B**：**蛋顶在 y = 704**（绿线），**冰晶巢的底在 y = 990**（红线）；从 x ≈ 297 到 x ≈ 715，位置照 `2_target_B.png`。

## 要画清楚的地方

- **头**（`4_head.png` 是 A 的头，第 0 步读回后 8 倍放大）：
  - **冰刺头冠**：几根尖刺分得开（中间一根最高），3–4 档冰蓝（亮青、冰蓝、蓝、深蓝），每根刺有亮边。
  - **紫色菱形额晶**：至少 2×2 格，中间一格亮紫。
  - **眼睛亮洋红色**（至少 2 格），在额晶下面、喙的上面；洋红只用在眼睛上。
  - **尖鸟喙**向前（画面右边），冰蓝色、有一格亮边。
- **翅膀**：一片片有棱角的冰晶羽毛，每片外缘亮（亮青 / 近白），里面有**连续的深蓝裂纹**（1 格宽）；**近侧翅膀（画面左边）大而亮**，向下展开几乎到地面；**远侧翅膀（画面右边）扬起、稍暗**，翼尖向下弯。翼尖、尾羽都完整，不要散成碎格。
- **身体**：深蓝色的胸口和脖子（暗处是它自己最暗的蓝，**一定要有冰蓝亮边**），背上一小块**紫色花纹**；**两条腿、两只海军蓝弯钩爪子**垂在身体下面，每只爪子能数出 3 个爪尖。
- **B 冰蛋**：**直立的椭圆冰蛋**（浅冰蓝带霜白高光，下半部更深更蓝，2–3 道棱面），**坐在一圈向外张开的冰晶巢里**（一块块尖尖的冰块，亮青 / 冰蓝 / 深蓝三档，每块有亮边）；蛋里**不画**她的影子。
- **一圈很深的海军蓝（接近黑）外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 干净

- 和附图 5–8（本包的塔姆、内瑟斯，每游戏像素 1.2 格，和艾尼维亚一样；斯维因 1.5 格；丽桑卓 1 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照原画（冰蓝羽毛、深蓝裂纹、深蓝身体、紫色花纹和额晶、洋红眼睛、海军蓝爪子）。深色部分**一定要有亮边**，不然在游戏里会糊成一团。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效（冰雾、雪花、风暴都不画）。

## 附图（压缩包 `anivia_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` / `1_picked_B.png` | 你第 0 步画的 A、B 原稿（用户采用） | **样子、颜色、细节**全照它 |
| `2_target_A.png` / `2_target_B.png` | 按新大小缩到每格 11 px 放在画布上（糊的） | **大小、位置、姿势**照它，糊的地方重画 |
| `3_layout_A.png` / `3_layout_B.png` | 同一张加网格线：绿线 = 顶，红线 = 地面 | 对齐网格、顶和地面线的位置 |
| `4_head.png` | A 的头（第 0 步读回后 8 倍放大） | 冰刺头冠、紫色额晶、洋红眼睛、尖喙 |
| `style/5_style_tahmkench.png` … `8_style_lissandra.png` | 本包的塔姆、内瑟斯（每游戏像素 1.2 格）、斯维因（1.5 格）、丽桑卓（1 格，冰系），8 倍放大 | **只看风格**：这个密度下一格有多大、暗色身体怎么留亮边、冰蓝怎么分档 |

## 提示词 1：`anivia-model-A-1.png`、`anivia-model-A-2.png`（平时，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1B approved pixel-art pictures of this character - a large bird made of ice crystal: huge long wings of angular ice-crystal feathers (light ice-blue outsides, dark-blue cracks inside), a dark-blue body and neck with a violet marking on the back, a crown of ice spikes on her head (the middle one tallest) with a violet diamond gem on the brow, a sharp ice-blue beak, bright magenta eyes, two legs with hooked dark-navy talons; hovering in her idle, the near wing spread down almost to the ground, the far wing raised high with its tip curling down; 1B her rebirth egg - an upright oval ice egg sitting in a ring of outward-pointing ice crystals (the LOOK, the COLOURS and the DETAILS to keep); 2A and 2B the same two pictures shrunk to their final game size on a 1024x1024 canvas, 11 px squares - the SIZE, the PLACE and the POSE are right, but they are muddy (the crown's spikes blurred into one lump, the violet gem and the magenta eye down to a loose square or two, the feathers no longer separate, the dark-blue cracks broken, the dark body and talons smeared into black, the egg's facets and the nest's shards mixed); 3A and 3B the same with grid lines every 5 squares: the green line = the top, the red line = the ground; 4 her head enlarged; 5-8 STYLE ONLY: other characters from the same game, shown 8x so every square is one pixel (5 and 6 at this same square density) - copy their pixel-art look, the lit edges on a dark body, ice blues in clear steps.
Draw with the image generator ONE clean pixel-art picture of the character in her NORMAL form (picture A): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2A: every square 11 px, aligned on one straight grid starting at the canvas corner, the top (the far wing's tip) at y 407, her lowest wing tip touching the ground line y 990, about 53 squares from top to bottom, both wings from about x 66 to about x 946 - hovering, the near wing (image left) spread down almost to the ground, the far wing (image right) raised high with its tip curling down, the head to the front-right, the talons hanging under the body - as if a pixel artist redrew image 1A square by square on image 2A's grid. Keep the head the size it is in 1A (do not enlarge it).
Make it CRISP and READABLE at this size: the ICE-SPIKE CROWN with separate spikes (the middle one tallest) in 3-4 ice blues (bright cyan, ice blue, blue, dark blue), each spike with a lit edge; the VIOLET DIAMOND GEM on the brow at least 2x2 squares with one bright violet square; the eye BRIGHT MAGENTA (at least 2 squares, that colour on the eye only) under the gem, above the beak; the sharp ice-blue beak pointing forward with a 1-square light; the wings in angular ice-crystal feathers, each feather's outer edge bright cyan / near white, CONTINUOUS dark-blue cracks (1 square wide) inside; the near wing big and bright, the far wing a step darker; the dark-blue chest and neck with LIGHT ICE-BLUE LIT EDGES, the small violet marking on the back; two legs and two dark-navy talons, three hooked claw tips each.
One continuous very dark navy (almost black) outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`anivia-model-B-1.png`、`anivia-model-B-2.png`（冰蛋，两稿）

附同样的图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of her REBIRTH EGG (picture B): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and shape of image 2B: every square 11 px (the SAME square size as picture A - last time the egg's squares were almost twice as big, not this time), aligned on one straight grid starting at the canvas corner, the egg's top at y 704, the bottom of the nest on the ground line y 990, about 26 squares tall and 38 squares wide, from about x 297 to about x 715 - as if a pixel artist redrew image 1B square by square on image 2B's grid.
Make it CRISP and READABLE at this size: an UPRIGHT OVAL ICE EGG - pale ice blue with frosty white highlights on its upper left, deeper blue in its lower half, 2-3 clear facet lines - sitting in a RING OF OUTWARD-POINTING ICE CRYSTALS: separate sharp shards in three steps (bright cyan, ice blue, dark blue), each with a lit edge, the ones in front overlapping the egg's bottom. Nothing inside the egg (no bird silhouette).
One continuous very dark navy (almost black) outline round the egg and the nest; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no frost mist, no sparkles), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图，也不要再做"格子中心采样"缩图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 大小、位置、姿势和 `2_target_A.png` / `2_target_B.png` 一样：每格 11 px、对齐网格；A 顶 y 407、蛋顶 y 704，最低处都在 y 990。
- A：头冠冰刺分得开、紫色额晶 ≥ 2×2、洋红眼睛 ≥ 2 格、尖喙清楚；冰晶羽毛一片片、深蓝裂纹连续；深色身体和爪子有亮边，两只爪子各 3 个爪尖；头没有放大。
- B：和 A **同样的格子大小**；直立冰蛋 + 一圈尖冰晶巢；蛋里没有影子。
- 外描边连续；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/anivia-model/`）

- `anivia-model-A-1.png`、`anivia-model-A-2.png`、`anivia-model-B-1.png`、`anivia-model-B-2.png`；**image_gen 的原始生成图原样放 `outputs/anivia-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/anivia_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），需要时删整行整列到 53 / 26 行（不经过头和额晶、眼睛），和 `2_target_*.png` 并排、按游戏大小和赫卡里姆、塔姆、内瑟斯、斯维因放一起给用户挑一稿（用户审核，不要自己判定）。
- 选定后做第 2 步动作，参考英雄联盟片段：待机 anivia_idle1（扇翅膀悬停）、飞行 anivia_run（= 跑步，扇翅膀，没有换腿）、普攻 anivia_attack1/2、Q anivia_spell1、E anivia_spell3、R anivia_spell4 / anivia_channel、受击、死亡 anivia_death；冰蛋：变蛋 egg_in（她收翅缩进蛋里）、蛋待机 egg（RebirthEgg_Idle1）、蛋裂 egg_crack（RebirthEgg_death）、孵化 hatch（蛋裂开、她展翅飞出）。翅膀是硬的冰晶，摆动作时整片平移或直角转，不要任意角度旋转变形。
