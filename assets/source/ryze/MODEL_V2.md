# 瑞兹：新造型（第 2 版，瘦一点；给 Codex 的提示词）

> **为什么重画**：用户说「瑞兹看起来也做的有点胖了」。和凯特琳、卡莎一样，**不要把现有的精灵图机械地压窄或切列**，请你**重画身体**。
> 凯特琳已经照 oppi 的身材比例重画好了，用户很满意（`ref_approved/caitlyn_v1_vs_v2.png`：左边旧的、右边新的）。
>
> 对照 `ours_now/ours_vs_oppi.png`（都是 8 倍，左边的色条标出每一段几行）：
> - **我们现在 40 行 × 29 格宽，828 个像素**：肩膀连手臂 24 格宽（红框），手臂 6 格粗、挂在身体两边（橙框），裤子 18 格宽、
>   两条腿连成一大块（黄框）；腰带以下的腿 13 行，其中靴子只有 5 行（蓝框）。
> - **oppi 的男英雄**（布兰德 40 行、伊泽瑞尔 36 行）：一样高，却只有 540–600 个像素（还包括布兰德手上的火球、伊泽瑞尔的护手）：
>   上身连手臂 16–18 格宽，手臂 3 格粗、贴着身体，两条腿分开、每条 4 格宽，腿 14 行。
>
> **用户对瑞兹的头没有意见**：头（光头、符文、白眼睛、棕色大胡子）保持现在的大小和样子（`ours_now/ryze_head_now.png`：发顶到下巴 10 行、
> 约 13 格宽）。读回以后我们会把现在的头原样贴回去，所以**头的大小和位置要和现在一样**，只改脖子以下。
>
> **`ref_structure/oppi_structure.png` 只看身材比例和结构，不许照着描、不许复制像素**（那是 oppi 团队的作品，而且它没有瑞兹），
> 要画**我们自己的**瑞兹。

## 造型要求

1. **服装、配色照我们的原画 `picture/ryze-model-A.png`**（用户选的那张）：蓝紫色皮肤、身上发光的符文、棕色大胡子、
   深蓝色无袖背心（金色肩甲、金色纽扣）、棕色宽腰带和金色圆扣、深蓝色裤子、青色前摆、棕色皮靴；**背后斜背着那卷大卷轴**（米黄色纸、棕色皮带）。
2. **3/4 侧面朝右**，站姿和现在的待机一样：两脚分开站稳，两手垂在身体两侧、手掌张开。
3. **总高（头顶到鞋底）40 格**（39–41 都可以）；卷轴顶最多比头顶高 2 行。
4. **头不变**：发顶到下巴 10 行、约 13 格宽，胡子垂到胸口约 5 行。
5. **瘦**：上身（下巴到腰带）14–15 行；**肩膀连手臂最多 18 格宽**（现在 24）；**手臂 3–4 格粗、贴近身体**（现在 6，挂在外面）；
   **两条裤腿分开**，每条 4–5 格宽，中间空 1–2 格（现在连成 18 格宽的一块）；腿从腰带到鞋底 14–16 行，靴子 6–7 行（现在 5）。
   不算卷轴，人最宽 20–22 格（现在 28）；整个人（连卷轴）的像素总数 600–680（现在 828）。
6. **卷轴**：保留，但最多 5 格宽，贴着后背，不要比肩膀宽出很多。

## 三个方案（A、B、C 都要，用户来挑）

| 方案 | 肩膀连手臂 | 手臂粗 | 每条裤腿 | 腿（腰带到鞋底） | 说明 |
|---|---:|---:|---:|---:|---|
| **A** 照 oppi（布兰德、伊泽瑞尔）的身材 | 16 | 3 | 4 | 15 | 最瘦 |
| **B** 还保留一点壮实（英雄联盟的瑞兹肩膀宽） | 18 | 4 | 5 | 14 | 稍瘦 |
| **C** 腿更长 | 17 | 3 | 4 | 16 | 修长 |

## 规则

- **做法**：生图直接出大方块像素画（方块多大都行），再按方块读回 1 格 1 像素；读回后人 40 格高、读回的图和生图一样干净才合格，
  不合格就重新生成。**不要把细节比方块还小的高清图压缩下来**（会糊成碎点），**也不要用代码一块一块拼**。
- 一道深色外描边（`#0F0213`），里面用材质自己的暗色；不要半透明，不要抗锯齿；脚下面什么都不要画（血条在那里）。
- 颜色以 `palette/ryze_palette_now.png`（现在的 30 色）为主，总共 32 色以内；眼睛的白色只用在眼睛里。
- 背景透明（做不到就纯绿 `#00FF00`，不要洋红）。
- 这一包**只画待机造型**（每个方案一张）。用户选定以后，动作另外做，都从你这一版来。

## 要交的东西

放在 **`outputs/ryze-model-v2/`**：
- `ryze_design_A.png`、`ryze_design_B.png`、`ryze_design_C.png`：生图原稿（大方块）；
- `logical/ryze_design_<A|B|C>_1x.png`：读回的 1 格 1 像素，透明背景；
- `HANDOFF.md`：每张的方块大小（px）、读回后多高多宽、胸口/裤子多宽、腿几行；**最后写它**，写完就是交付了。

## 提示词（生图用）

```text
Pixel art game sprite of Ryze from League of Legends for a small tactics game, ONE character, full body, 3/4 view
facing right, standing with feet apart, arms hanging close to his sides with open hands. A LEAN, not bulky, build:
the figure about 40 squares tall; the head exactly like the attached head (bald blue-violet head with glowing runes,
white glowing eyes, a long brown beard) about 10 squares from the top of the head to the chin and 13 squares wide;
shoulders including the arms at most 18 squares wide, arms 3-4 squares thick close to the body, two separate trouser legs each 4-5
squares wide with a gap between them, legs 14-16 squares from the belt to the soles. Blue-violet skin with glowing
rune tattoos, dark navy sleeveless vest with gold shoulder plates and gold buttons, brown belt with a round gold
buckle, navy trousers with a short teal front flap, brown leather boots; a big cream paper scroll with brown leather
straps slung diagonally on his back, at most 5 squares wide. Chunky square pixels on a strict grid, hard edges, no
anti-aliasing, one dark outline, 3-4 shades per material. Transparent background (else pure green #00FF00). No text,
no grid lines, no border.
```
附图顺序：`picture/ryze-model-A.png`（服装、配色、卷轴）、`ref_approved/caitlyn_v1_vs_v2.png`（我们自己改好的凯特琳：要的就是这种变化）、
`ref_structure/oppi_structure.png`（只看身材比例）、`ours_now/ours_vs_oppi.png`（哪里要改）、`ours_now/ryze_head_now.png`（头保持这样）。
