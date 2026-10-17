# 塔里克：只重画游戏尺寸造型的头（脸 + 头发），给 Codex 的提示词

> 用户看了你上一轮的游戏尺寸 A、B（`taric-game-design-pack.zip`），两版都没选，原因只有一个：**「脸和头发不像」**（不像用户选的原画里的塔里克）。身体、肩甲、披风、武器都没问题，所以**这一轮只改头**：在 A、B 两版里各只重画红框里的格子，框外的每一格都保持原样（同一色板、同一大小、同一脚底线）。
> - **头发（最重要）**：原画是**中分**——头顶正中一道分线，两半从脸的两侧垂下来：远侧（图右）的头发贴着远侧脸颊一直垂到下颌，近侧（图左）的头发盖过耳朵、垂到肩甲后面；脸两边各有一缕长前发垂到下颌。头顶是圆的，额头上方有 2–3 格头发的高度。**不要**像现在这样一顶往后推的平帽子、偏到一边，也不要一道深色竖线划过脸。
> - **脸**：暖色皮肤 3 档（受光面 + 近侧脸颊/下颌的阴影），脸稍长、**方下巴**，下巴下一行阴影；两眼之间下方一格阴影表示鼻子。**浓眉**（深棕）**直接压在眼睛上**（眉和眼之间不要留一行皮肤），稍向鼻子一侧下斜，神情自信。眼睛：两只一样大、同一行，各 2 格：一小格眼白 + 右边一格亮天蓝的瞳孔（他看向右边），两眼之间 2 格皮肤；天蓝色只用在眼睛上。嘴：**闭着的自信微笑**，2 格比皮肤深一档的唇色（不要黑、不要深红的洞），远侧那一格高一行；**绝不要张嘴**。近侧的耳朵露 1–2 格皮肤带阴影。
> - 头的大小不变：A 13 行（y 60–72），B 15 行（y 60–74）。
> - 交回前用对比检查：**只有红框里的格子变了**。交付 `taric_design_A2.png`、`taric_design_B2.png`（1024×1024）和各自的 1x 图，附 `HANDOFF.md`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `taric/picture_head.png`、`taric/picture_full.png` | 用户选的原画（头部特写 / 全身） | **头发和脸要像它** |
| `taric/design_A_box.png`、`taric/design_B_box.png` | 你上一轮的 A、B ×8，红框 = 只能改的范围 | 改哪里 |
| `taric/design_A_1x.png`、`taric/design_B_1x.png` | 你上一轮的 1x 原图 | 在它上面改 |
| `taric/not_this.png` | 现在的两个头 ×12，打叉 + 问题说明 | 不能再这样 |
| `taric/structure_guide.png` | 原画直接缩到游戏尺寸，头部 ×12（带格线，糊的） | 只看分线、两侧头发、脸、眼睛大概在哪 |
| `taric/main_faces.png` | main 里盖伦、德莱厄斯的脸，×10 | 小尺寸男性脸怎么画才好认 |

## 提示词（A、B 各做一次，同一段）

```text
This is an EDIT of your own game-size sprites, only the head. Attached: FIRST the approved big picture of this character, cropped to the head (picture_head.png, the full figure in picture_full.png); SECOND and THIRD your game-size designs A and B at 8x with a red box (design_A_box.png, design_B_box.png) - edit design_A_1x.png / design_B_1x.png; FOURTH the current heads crossed out (not_this.png); FIFTH the picture shrunk straight to game size, head at 12x (structure_guide.png) - use it ONLY to see where the hair masses, the part and the face go, it is blurry; SIXTH two approved male faces of other heroes at game size (main_faces.png) - how a small face reads.
Task: in each design redraw ONLY the squares inside its red box - the hair and the face - so the head looks like the FIRST image; every square outside the box stays exactly as it is (body, pauldrons, cape, weapon, the same 26-colour palette; the canvas, the size and the feet do not change). Head size in squares: A 13 rows (y 60-72), B 15 rows (y 60-74), as now.
Hair (as in the FIRST image): auburn-brown in 4 shades with a few lighter strand squares; parted in the MIDDLE - a clear dark parting line at the top centre of the head; the two halves sweep down on both sides of the face: on the far side (image right) the hair frames the far cheek down to the jaw, on the near side (image left) it falls over and behind the ear down to the pauldron; a long front lock hangs beside each side of the face to the jaw line. A rounded crown 2-3 squares of hair above the forehead, never a flat cap, never swept to one side. No dark line across the face.
Face: 3/4 front facing right, warm skin in 3 shades (a lit side and a shaded near cheek / jaw), a longer face with a strong SQUARE jaw and a one-row chin shade; a hint of the nose as one shade square below and between the eyes. Thick dark brown brows lying DIRECTLY on the eyes (no skin row between brow and eye), sloping slightly down toward the nose - a confident look. Eyes: both the same size and on the same row, each 2 squares: a small white square + a bright sky-blue iris square on its right (he looks right), 2 skin squares between the eyes; the sky blue only in the eyes. Mouth: a CLOSED confident smile - 2 squares of a darker lip/skin shade (not black, not a dark-red hole), the far end one row higher; never an open mouth. The near ear as 1-2 skin squares with a shade beside the hair.
Pixel rules as before: true 1-square pixels on the 8 px grid, the one near-black outline around the head's silhouette, no second black ring inside, no specks, no blur, no semi-transparency.
Deliver: taric_design_A2.png and taric_design_B2.png (1024x1024, 8x) and their 1x files (128x128), plus HANDOFF.md; check with a diff that only squares inside the red box changed.
```

## 交回前自查

- [ ] 对比原来的 1x：只有红框里的格子变了；
- [ ] 头顶有中分线，两边头发从脸两侧垂下，远侧头发贴着脸颊到下颌，两缕前发在脸两边；不是一顶平帽子；
- [ ] 方下巴、浓眉压在眼上、两只蓝眼睛一样大同一行、嘴是闭着的微笑；
- [ ] 和 `picture_head.png` 放在一起看，一眼认得出是同一个人。

## Claude 收到后（给 Claude 看）

- 逐格对比 1x：框外不变；看脸 12x 和 3x（竞技场、暗色卡片），和原画头部并排给用户挑 A2/B2；通过后补描边（`strips.complete_outline`），再出动作帧包。
