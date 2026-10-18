# 影哨 阿克尚：瘦身定稿（游戏格子上重画，给 Codex 的提示词）

> **用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户在游戏里看了：「阿克尚怎么体型这么胖？」。量过：他腰身一段实心宽 **26–29 个游戏像素**，本包别的射手是 12–24（卡莎 19–24、烬 19–23）。原因：上一轮的定稿只删了行没删列，人横向宽了约 10%；披风和外袍画得很厚，两边都铺开了。
> - 用户的要求：**按英雄联盟里阿克尚的身材重画一张瘦一点的定稿**（`2_英雄联盟阿克尚_待机.png`：细长、腰细、腿长、披风贴着身体垂下）。之后所有动作都照新定稿重做，所以这张要画准。
> - **姿势、服装、配色、枪都和现在的定稿一样**（`1_现在的定稿_太胖.png`），只是**变瘦**。画两稿。

## 大小和位置（照 `3_layout.png`）

- 画布 **1254 × 1254**，**每格 10 px**，网格从画布左上角 (0, 0) 开始对齐（浅灰线每 5 格一条）。
- **头顶头发在 y = 740**（绿线），**两只鞋底在 y = 1200**（红线），中间正好 **46 格（460 px）**。这就是游戏里的大小（38 个游戏像素高、每个游戏像素 1.2 格），**人在画布上很小，这是对的，不要放大**。
- **身体宽度最多 24 格**（蓝框）：肩膀、手臂、披风、外袍都在蓝框里；只有举起的枪可以伸出蓝框上方和侧面。**腰最窄处约 12–14 格**，两条腿分开站，腿要显得长。
- 人在画布下面中间，上面和两边大片透明是对的。

## 要画的样子

- **姿势和现在的定稿一样**：站直，近侧手把回旋镖手枪举在头边、枪口朝上；远侧手叉腰；两腿分开站稳。
- **身材照英雄联盟**：头不要太大（约占身高 1/4 多一点），**肩窄、腰细、腿长**；披风是**一条窄窄的暗红长披风，从肩后垂下、贴着身体**，下摆只比腿稍宽，不要往两边铺开成三角形；橙红外袍/饰带只在胸前斜挎一条，不要把整个躯干包宽。
- **脸**：深棕长卷发 3 档、头顶小发髻；**两只眼睛一样大、一样高、都看得见，每只 2 格宽**（1 格眼白 + 1 格深色瞳孔，上面 1 格深色眉毛）；短胡子比头发浅一档；棕色皮肤。
- **上身**：浅蓝白围巾（2 档）；灰色金边护肩；赤膊胸口有亮边；橙红饰带**一条完整的斜带**、中间一块金箍。
- **手**：金护腕 + 浅蓝手套。
- **下身**：青绿腰带和**一条直的青绿长布片**（2 格宽，中间 1 个金环）；深灰黑裤子 3 档有亮边；黑靴有亮边和 1 行金饰。
- **枪**：和现在一样大、一样颜色，**轮廓完整连续**：枪身直，暗红带青铜，前端两道弯钩朝上张开，每道 2 格粗、有亮边和橙色高光。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立杂色格。

## 干净

- 和 `style/` 里的图一样的像素画（**6_style_akshan 就是现在游戏里的阿克尚，格子密度和这次一样**）：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `akshan_slim_pack.zip`）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_现在的定稿_太胖.png` | 现在的定稿（8 倍放大） | **姿势、服装、颜色、枪**照它；**宽度不要照它** |
| `2_英雄联盟阿克尚_待机.png` | 英雄联盟里的阿克尚 | **身材比例**照它：细长、腰细、腿长、披风贴身 |
| `3_layout.png` | 网格、绿线 = 头顶、红线 = 地面、蓝框 = 身体最宽 | 大小和位置 |
| `style/4_style_kaisa.png`、`5_style_jhin.png` | 本包的卡莎、烬（8 倍放大） | 射手该有的**瘦长体型** |
| `style/6_style_akshan.png` | 现在游戏里的阿克尚（8 倍放大） | **格子密度**（一样），体型不要照它 |

## 提示词：`akshan-slim-1.png`、`akshan-slim-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 our current pixel-art design of a ROGUE GUNSLINGER (brown skin, long wavy dark-brown hair with a small topknot, a short beard; a pale blue-white scarf, grey gold-trimmed shoulder pads, a bare chest, an orange-red sash slung diagonally with a gold band, a long dark-red cape, a teal belt and a long teal front cloth with a gold ring, dark grey-black trousers, tall black boots, gold bracers, pale blue fingerless gloves; a big dark-crimson-and-bronze relic pistol with two curved boomerang-like hooks at its front; standing upright, the near hand raising the gun beside his head pointing up, the far hand on his hip) - keep its POSE, COSTUME, COLOURS and GUN, but it is far TOO WIDE AND BULKY; 2 the same character in the original 3D game - his BUILD to follow: slim, narrow shoulders, a thin waist, long legs, the cape hanging close behind him; 3 the layout: grid lines every 5 squares, green line = top of his hair, red line = the ground, blue box = the widest his body may be; 4-5 STYLE: slim marksmen from the same game; 6 the current in-game sprite at this SAME square density.
Draw with the image generator ONE clean pixel-art picture of the gunslinger, SLIMMER: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square 10 px, aligned on one straight grid starting at the canvas corner. The top of his hair at y 740, both soles on the ground line y 1200 (46 squares from the hair to the soles). His body - shoulders, arms, cape, tabard - at most 24 squares wide, the waist about 12-14 squares; only the raised gun may stick out of that box above and to the side. The figure is SMALL on the canvas, in the lower middle, with wide transparent space around it - do NOT enlarge it.
The same pose as image 1 (upright, the gun raised beside his head pointing up, the far hand on the hip, legs apart and planted), the build of image 2: head a bit more than a quarter of his height, narrow shoulders, thin waist, long legs; the dark-red cape a NARROW band hanging close behind him, its hem only a little wider than his legs, never spread into a wide triangle; the orange-red sash one unbroken diagonal band across the chest with its gold band.
Crisp at this size: the hair in 3 shades with the small topknot; TWO EYES of the SAME size at the SAME height, both visible, EACH 2 SQUARES WIDE (one white square and one dark pupil square) with a dark brow above; the beard a shade lighter than the hair; the pale blue-white scarf; the grey shoulder pads with a gold rim; gold bracers and pale blue gloves; one straight teal front cloth 2 squares wide with a gold ring; the trousers in 3 shades; black boots with one row of gold; the gun WHOLE, the same size and colours as image 1, its two hooks 2 squares thick with lit edges and orange highlights.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- 两张图都是 image_gen 画的；1254 × 1254；真透明背景，alpha 只有 0 / 255。
- **人小**：头顶 y 740、鞋底 y 1200（46 格，每格 10 px）；身体在 24 格宽以内（枪除外）。
- **比现在的定稿明显瘦**：腰细、腿长、披风贴身。
- 两只眼睛一样大、一样高、每只 2 格宽；小发髻；胡子；枪完整。

## 交付（`outputs/akshan-slim/`）

- `akshan-slim-1.png`、`akshan-slim-2.png`；**image_gen 的原始生成图原样放 `outputs/akshan-slim/raw/`**；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/akshan_slim_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 在 8 倍下数描边台阶量格子（应是 10 px），按它自己的格子读回；头顶到鞋底应是 46 行左右（PPU 1.2，ORIG_PPU 改 1.2，`ppu_restyle` 的 akshan 不再缩放）。量腰身宽度和卡莎、烬比；发给用户挑。定稿后动作照新定稿重做：平端枪手臂的姿势包、走路换皮包（和上一轮一样的做法）。
