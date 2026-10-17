# 丽桑卓：按细节原稿重画 40 行（第 1 步返工，给 Codex 的提示词）

> 上一轮的 A、B（`lissandra_design_A/B`）是从粗的那张生图删行删列拼的：辫子成了一根白柱子、脸很小、形状只有三四种颜色的方块；我把那张**细节原稿**（`raw/lissandra_detailed_rejected.png`，8 px 一格，读回来 79×50，是目标的两倍大）减半也试了，脸丢了、满是杂点。用户选了：**按细节原稿重画 40 行**。
> - **唯一的长相参考是 `lissandra/1_detailed_draft.png`**（你自己画的那张细节原稿）：冰冠两边的长刃和冠前的青色月牙、遮眼面罩、淡蓝下半脸和深蓝嘴唇、脸两边的深色兜帽发绺、带编织纹的冰蓝长辫（末端一道深色发带）、两边亮青色的水晶护肩、深 V 领口、胸甲棱线、发青光的小臂和爪子一样的手、拖地长裙和裙摆的冰晶，没有腿。全部保留。
> - **直接在 40 格的格子上画**（冠顶到裙摆 40 格、最宽 30 格），**不要先画大再缩小，不要用脚本删行删列或拼方块**，每一格都按这个尺寸画，像 `3_quality_bar.png` 里的英雄那样，小细节才保得住。头比原稿大一点：冠顶到下巴 14 格，身体 26 格。位置照 `2_target_size.png`：绿线冠顶、黄线面罩、橙线下巴、红线是裙摆最低一行（第 99 行）、蓝线是裙摆中间（x=512）。
> - **40 格里必须保住的（最重要）**：冰冠两刃 + 2–3 格青色月牙；脸约 7 格宽、面罩到下巴 6 行：面罩 2 行（深蓝、下沿一格钢蓝亮边）、2 行淡蓝皮肤、**一格深蓝嘴唇**在脸的中线上、一行皮肤阴影做下巴、下半张脸一圈完整描边、**脸上没有别的深色方块**；脸旁 1–2 格兜帽发绺；**辫子 3 格宽、有斜向的两色编织纹**（冰白和浅蓝）和末端深色发带；两边水晶护肩是 2–3 格的尖刺、亮青色带一格白高光；V 领口淡蓝皮肤；小臂 2 格宽两档青色，爪手 2–3 格、指尖白青；裙子的褶是 1 格钢蓝线；裙摆冰晶 4–5 个大锯齿尖。
> - **风格**：最多 26 色，一圈 1 格近黑描边（只一种近黑），每种材质 2–4 档平涂，不要抖动、渐变、孤立杂点、抗锯齿，透明度只有 0/255；深蓝部分要有钢蓝亮边，不要糊成一块黑。姿势同原稿：3/4 正面朝右、笔直站着、两臂垂在身侧。裙摆以下什么都没有。
> - **反例**：`lissandra/6_rejected.png` 里三张都不要（白柱子辫子、小脸、方块、缩小后的杂点）。
> - 交付到 `outputs/lissandra-model-v2/`：`lissandra_design_v2.png`（1024×1024，8 倍）、`lissandra_design_v2_1x.png`（原尺寸）、**所有生图原稿**（不管成没成，都放进 `raw/`）、色板、`HANDOFF.md`（**最后写**，写明读回来是多少格、头多少格），最好再打一个 zip（`lissandra_design_v2_pack.zip`）。如果生图怎么都画不到 40 格，**不要用脚本删行缩小**，把最接近的几张原稿交来就行。

## 附图（`lissandra/` 里，按顺序附上）

| 文件 | 内容 |
|---|---|
| `1_detailed_draft.png` | 你画的细节原稿（79 格高）——**唯一的长相参考** |
| `2_target_size.png` | 1024×1024 画布，原稿的剪影缩到 40 格的灰色位置图和那几条线 |
| `3_quality_bar.png` | 包里的乐芙兰、娑娜、伊芙琳、莫甘娜、迦娜 ×8——**细节和干净程度照它们** |
| `4_tfm2_style.png` | 原版的冰法师、魔法少女、灵媒、风法师、暗影法师 ×8 |
| `5_head_hands_big.png` | 原稿的头和手放大 |
| `6_rejected.png` | 不要的三版（反例） |

## 提示词（附上面六张图）

```text
Six attached images. FIRST: your own earlier detailed draft of this character (Lissandra, the Ice Witch) - THE LOOK TO KEEP, everything in it: the wide navy crown-helm with two long blades and the cyan crescent on its front, the dark mask over the eyes, the pale ice-blue lower face with dark blue lips, the dark hood-locks framing the face, the long pale cyan-white braid down her back (with its braid pattern and a dark band near the end), the bright cyan crystal spikes on both shoulders, the V neckline, the bodice ridges, the long glowing cyan forearms with clawed hands, the long navy gown breaking into steel-blue ice crystals at the hem, no legs. It was drawn TWICE TOO BIG (79 squares tall, 8-px squares), and its head is small for this game: at 40 squares make the head 14 squares from the crown's top to the chin (the SECOND image), the body the other 26. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with the FIRST image's shape brought to 40 squares in greys - her SIZE and PLACE: the crown's top on the green line, the mask on the yellow line, the chin on the orange line, the hem's lowest row on the red line (square row 99, y=792-799), the hem's middle on the blue line (x=512). THIRD: heroes of this game at game size as they are now, at 8x - the quality bar: match their pixel size, their detail and their clean look. FOURTH: official heroes of this game at 8x (an ice mage, an enchantress, a spirit caller with an ice crown, a wind mage, a shadowmancer). FIFTH: the FIRST image's head and hands, big. SIXTH: three earlier tries that were REJECTED - do not draw like them: a braid that is one flat white column, a tiny face, blocky 3-colour shapes, noise and lost features from shrinking.
Task: draw the FIRST image again as a SMALL game sprite, DIRECTLY on a 40-square grid - every pixel one crisp 8x8 square on one 8-px grid, 40 squares from the crown's top to the hem and at most 30 across. Do NOT draw it big and shrink it, do NOT build it by deleting rows or columns, do NOT assemble it from blocks by a script: draw each square for this size, like the THIRD image's heroes, so the small features stay.
Keep at 40 squares (most important): the crown's two blades and a 2-3 square cyan crescent on its front; the face about 7 squares wide and 6 rows from the mask to the chin: the mask 2 rows (navy, a steel-blue lit lower edge), 2 rows of pale blue skin, ONE dark-blue lips square on the face's middle line, a skin-shadow chin row, a clean outline round the lower face, NO other dark square on the face; the hood-locks 1-2 squares beside the face; the braid 3 squares wide with a diagonal two-tone braid pattern (pale cyan-white and light blue) and the dark band near its end; both shoulder crystals as sharp 2-3 square bright cyan spikes with a white glint; the V neckline in pale skin; the glowing forearms 2 squares wide in two cyan shades, the clawed hands 2-3 squares with a white-cyan tip; the gown's folds as 1-square steel-blue lines; the hem's crystals as 4-5 big jagged steel-blue points.
Style: at most 26 colours; ONE 1-square near-black outline (one colour); every material 2-4 flat shades; no dithering, no gradients, no lone noise squares, no anti-aliasing, alpha only 0 or 255; the navy parts with steel-blue lit edges, never one flat black mass. Same pose as the FIRST image: upright 3/4 front view facing image right, arms at her sides. Nothing below the hem. Transparent background (or solid #00FF00), no grid, text, border or shadow.
Before finishing, check: 40 squares tall (count them), on the SECOND image's lines; the lips one square; the braid patterned, not one flat colour; both hands and both crystals visible; nothing below the hem.
```

## 交回前自查

- [ ] 冠顶到裙摆 40 格，在第二张图的线上；严格 8×8、0/255 透明、≤26 色、一种近黑描边；
- [ ] 嘴唇一格、脸上没有别的深色块；辫子有编织纹不是一块白；两只手、两个水晶护肩都在；裙摆以下没有像素；
- [ ] 原稿全都放进 `raw/`；最后写 `HANDOFF.md`。
