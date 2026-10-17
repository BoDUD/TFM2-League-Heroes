# 巴德：游戏大小的正面 + 侧面造型（第 1 步，给 Codex 的提示词）

> 用户选了第 0 步的 **A**（乐器扛在近侧肩上），但要求**缩小到 85%**，并且在格子上**重新画**（不是把 A 缩小）。所以这一步请 Codex 在**同一张 12 像素的格子**上画三张：
> - **`bard-front.png`**：3/4 正面朝右（待机和选人卡用）——就是 A，**同样的设计、同样的姿势、同样的颜色**，但**小 15%**：鬃毛顶到脚底 **51 格**（A 现在是 60 格）。**肩膀那一块重新画清楚**：现在的 A 在游戏大小下，金色喇叭口、象牙号角、近侧手臂和挂着的小铃铛糊成了一团。要能一眼分出：**近侧的手（橄榄褐色的大手）握着金色喇叭口**（里面的青绿圆球），**象牙号角从肩膀上往后、在画面左边弯下来**（一条干净的弯弧，几道棕色皮带），**两三个金色小铃铛**整齐地挂在号角下面。附图 3、4 是 Codex 自己第 0 步的高精度原稿，那里的肩膀、喇叭口、号角画得很清楚，照那个意思在小格子上画。
> - **`bard-side-A.png`**：**正侧面朝右**（所有动作的底子）：身体是侧面——胸口、肚子、挂布朝右，近侧的肩膀和胳膊在前面，两条柱子腿一前一后，乐器还扛在近侧肩上（喇叭口在肩膀前面、号角往后弯到背后画面左边，参考附图 5 英雄联盟的侧面）。**头不变**：还是正面那团圆鬃毛 + 青铜面具，**两个金色眼孔和嘴孔都看得到**（面具往鬃毛团的右边挪一点，表示他朝右看），**不要画侧脸**。
> - **`bard-side-B.png`**：同上，但身体是 **3/4 侧面**（介于正面和正侧面之间，胸前的红色挂布还能看到一半）。
> - 三张**一样高**（鬃毛顶到脚底 51 格）、**一样的格子、一样的颜色、一样的细节**，像同一个角色转了个身。
> - **画布和格子**：1024×1536 竖版、真透明背景；格子**每格 12 像素**，**从 x=2、y=0 开始**（左右各留 2 像素透明边，横向 85 格、纵向 128 格），和你第 0 步的成品一样。**鬃毛顶在第 55 行（附图 9 的绿线）**，**脚底最下一行是第 105 行（红线上面那一行）**，**两脚中间站在第 42 列（蓝线）**。天线、举起的手、乐器可以高过第 55 行。
> - **风格**：和第 0 步一样——**每个游戏像素约 1.5 格**、外轮廓 **2 格宽的近黑描边**、每种材质 3–4 档平涂、不要零散的单个杂色格、不要渐变/柔光/抗锯齿。附图 8 是这个密度的英雄（加里奥、布隆、泽丽、奈德丽）。**宁可少几个细节，也要每一块都清楚**：鬃毛（浅绿白）、面具（青铜 + 金孔）、皮肤（灰绿）、护腕（红 + 暗紫条纹）、挂布（红 + 橙卷纹）、灯笼裤（深酒红）、柱子脚（深铁色）、乐器（象牙 + 棕皮带 + 金喇叭口 + 青绿圆球 + 金铃铛）。
> - 不画特效，不画地面和影子。
> - 交付：`outputs/bard-model/bard-front.png`、`bard-side-A.png`、`bard-side-B.png`（都是 1024×1536、真透明、硬 alpha），原始生成稿放 `outputs/bard-model/raw/`，`generation-prompts.txt` 写实际用的提示词，**最后**写 `outputs/bard-model/HANDOFF.md`。

## 附图（压缩包 `bard_model_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_front_now_grid.png` | 现在的 A 按格子读回（60 格），放在同一张格子上、脚底对齐第 105 行；**粉色小框是 85% 的轮廓**——新正面大约画在这个框里 | 设计（逐格看颜色和部件）、**新的大小** |
| `2_picture_A.png` | 你第 0 步的成品 A | 整体样子 |
| `3_draft_A01.png`、`4_draft_A02.png` | 你第 0 步 A 的两张原始稿（更细的格子） | **肩膀、喇叭口、号角、小铃铛应该怎么读**（只看结构，不要照它的格子大小） |
| `5_league_side.png` | 英雄联盟模型转到侧面朝右（待机 + 两帧跑步） | 侧面的身体、乐器在侧面怎么扛 |
| `6_league_head.png` | 头的特写 | 鬃毛、面具、天线 |
| `7_league_instrument.png` | 乐器扛在肩上的特写 | 号角、皮带、铃铛、喇叭口 |
| `8_style.png` | 1.5 密度的英雄（4 倍） | **只看风格** |
| `9_empty_grid.png` | 空格子，绿线 = 鬃毛顶（第 55 行），红线 = 脚底下沿（第 105 行下面），蓝线 = 站立列（第 42 列） | 三张图都画在这张格子上 |

## 提示词 1：`bard-front.png`

九张图都附上，顺序同上表。

```text
Nine attached images. Image 1 is this character's current pixel design read back square for square on a grid (one square = one pixel of the design), standing on the red line, with a MAGENTA OUTLINE of small squares showing the new, 85% size; image 2 is that design as delivered; images 3 and 4 are its two detailed drafts (look at how the shoulder, the golden bell-mouth, the ivory horn and the little bells are built - NOT at their finer square size); image 5 is the game's 3D model from the side, image 6 its head, image 7 its instrument on the shoulder; image 8 is STYLE ONLY (other characters at this density, 4x); image 9 is the empty grid to draw on.
Redraw image 1's character - Bard, a big gentle wanderer: a big fluffy pale green-white mane round a small round bronze mask with three glowing golden holes and a short antenna with a golden bead, sage-green skin, big olive-brown hands, red-and-dark-purple striped bracers, a long red tabard with orange swirls, a brown belt, a dark blue-grey waist cloth with purple tassels, a golden bell at the hip, loose dark wine-red trousers, two thick dark iron peg feet; the instrument on his near shoulder - SAME design, SAME pose (3/4 front facing image right), SAME colours, but 15% SMALLER: inside the magenta outline of image 1.
Make the near shoulder READABLE (in image 1 it is a muddle): his NEAR HAND (big, olive-brown) grips the GOLDEN BELL-MOUTH at his near shoulder, the GLOWING TEAL ORB with a swirl inside it facing the viewer; the IVORY HORN goes back over that shoulder and CURVES DOWN BEHIND HIM on the image left as ONE CLEAN ARC with two or three BROWN LEATHER BANDS; two or three SMALL GOLDEN BELLS hang neatly under the horn. Keep the mask exactly as it is (both eye holes and the mouth hole, about 10x10 squares) and the mane's round shape.
Draw on the grid of image 9: a 1024x1536 PORTRAIT PNG with a genuine transparent background, squares of EXACTLY 12 x 12 output pixels whose grid starts at x = 2, y = 0 (85 columns, 128 rows, 2 transparent pixels left and right); the TOP OF THE MANE on ROW 55 (the green line), the LOWEST ROW OF THE SOLES ROW 105 (just above the red line), the point between the feet on COLUMN 42 (the blue line); the antenna and the instrument may rise above row 55. That is 51 squares from the mane top to the soles.
Style exactly like image 8 and image 1: crisp chunky pixel art, every square one flat colour, a TWO-SQUARE-THICK near-black outline around the silhouette, each material in 3-4 flat shades, no stray single odd squares, no dithering, no gradients, no glow, no anti-aliasing, hard alpha. Fewer details rather than muddled ones: every part must read at a glance.
No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 2：`bard-side-A.png`（正侧面朝右）

九张图都附上，顺序同上表；如果已经画好了 `bard-front.png`，把它也作为第十张附上（"image 10: the new front"）。

```text
Nine (or ten) attached images, the same as for the front (image 10, if attached, is the new front design you drew - match it exactly).
Draw the SAME character, at the SAME size, with the SAME squares, colours and details as the new front (inside image 1's magenta outline), but turned SIDE-ON FACING IMAGE RIGHT - the base every action will be drawn from: the body in profile, the chest, belly and red tabard facing right, the near shoulder and near arm in front of the body, the far arm mostly hidden behind, the two thick peg legs one in front of the other (the near leg a little to the right, in full tone; the far leg behind it, a shade darker), the peg feet pointing right. The instrument stays on his near shoulder as in image 5: the golden bell-mouth with its teal orb just in front of the shoulder (held by the near hand), the ivory horn arching back over the shoulder and down behind him on the image left, the little golden bells under it.
THE HEAD DOES NOT TURN TO A PROFILE: it is the same round fluffy mane with the same bronze mask, both golden eye holes and the mouth hole visible (the mask moved a little to the right side of the mane, as if he looks right); no side face, no nose, no new face.
Same grid as image 9: 1024x1536 portrait PNG, genuine transparent background, squares of exactly 12 x 12 output pixels from x = 2, y = 0; the top of the mane on row 55, the lowest row of the soles row 105, the point between the feet on column 42. Same style: crisp chunky pixel art, two-square near-black outline, 3-4 flat shades per material, no stray squares, no dithering, no gradients, no glow, no anti-aliasing, hard alpha. No effects, no background, no ground, no shadow, no text.
```

## 提示词 3：`bard-side-B.png`（3/4 侧面朝右）

同提示词 2，只把身体那一句换成：

```text
... but turned THREE-QUARTER SIDE FACING IMAGE RIGHT (between the front and a full profile): the body turned mostly to the right, about half of the red tabard still visible on his chest, the near shoulder and arm in front, the far shoulder just showing behind the mane, the two peg legs a little apart, one ahead of the other, the feet pointing right ...
```

## 交回前请检查

- 三张都是 1024×1536、真透明、硬 alpha；格子 12 像素、从 x=2 开始；**鬃毛顶第 55 行、脚底最下一行第 105 行、两脚中间第 42 列**；三张一样高（51 格）。
- 正面：和 A 同一个设计和姿势，只是小 15%，在粉色框里；**肩膀那块清楚**：大手握着金喇叭口 + 青绿圆球、一条干净弯弧的象牙号角 + 棕皮带、整齐的两三个金铃铛。
- 侧面 A：身体正侧面朝右、两条柱子腿一前一后、乐器还在近侧肩上；侧面 B：身体 3/4 侧面。
- **三张的头完全一样**：圆鬃毛 + 青铜面具，两个眼孔 + 嘴孔都看得到，天线 + 金珠；不画侧脸。
- 2 格近黑描边；每块颜色平涂；没有糊、没有柔光、没有渐变、没有零散杂色格；没有特效。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/bard-model/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/bard/codex_model/`（含 raw/），按格读回（12 px、x=2 起），三张都在游戏大小下和 85% 的旧 A、布隆/奈德丽并排给用户看；用户挑侧面 A / B。
- 正面若有零星杂色或缺描边，按 design 的方式只做最小清理（strips.complete_outline、孤立格），不手画重涂；读回 1:1 当作 hd/front.png。
- 之后写第 2 步 MODEL_STRIPS.md：所有动作从侧面画（side-view-design），头用正面的同一个（one-face-all-frames），跑步按 Caitlyn 的交叉步（run-legs-caitlyn-way），乐器是刚体（只平移或 90 度转）。
