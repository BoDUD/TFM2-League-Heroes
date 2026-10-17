# 剑魔：新造型（第 2 版，瘦一点；给 Codex 的提示词）

> **为什么重画**：用户说「剑魔也有点肥胖瘦身一下」。和凯特琳、卡莎、瑞兹一样，**不要把现有的精灵图机械地压窄、切列或切行**
> （凯特琳试过，被用户说「抽象」），请你**重画身体**。凯特琳已经照 oppi 的身材比例重画好了，用户很满意
> （`ref_approved/caitlyn_v1_vs_v2.png`：左边旧的、右边新的）。
>
> 对照 `ours_now/ours_vs_oppi.png`（都是 8 倍，左边的色条标出每一段几行，方框标出哪里太宽）：
> - **我们现在 40 行 × 44 格宽、1084 个像素**，是整个包里最「实」的英雄（oppi 的剑魔 788、锐雯 821、贾克斯 960、德莱厄斯 998）：
>   **身体连手臂 27 格宽**（蓝框：肩甲、胸口、两只手臂挤成一大块）；两边的翅膀各 11–13 格宽（黄框），把人撑到 44 格；
>   两脚分开 34 格宽，腰带以下的腿只有 11 行（橙框）。
> - **oppi 的剑魔** 42 行 × 45 格，却只有 788 个像素：身体只有 12–16 格宽，红色的翼刃收在背后、贴着身体，剑伸在前面；
>   oppi 的贾克斯、盖伦这样的重甲战士，身体连手臂也只有 20–26 格（含武器）。
>
> **`ref_structure/oppi_structure.png` 只看身材比例、身体宽度和翅膀收得多紧，不许照着描、不许复制像素**（那是 oppi 团队的作品），
> 要画**我们自己的**剑魔。

## 保留的东西（用户已经选定）

- **头盔和脸一格都不改**（`keep/aatrox_keep.png` 左边，16 倍）：深色带角的头盔、盔下的阴影脸、两只红眼睛。读回以后我们会把现在的头
  原样贴回去，所以**头的大小和位置要和现在一样**（头盔连角 11 行、约 12 格宽），只改头下面的身体。
- **大剑一格都不改**（`keep/aatrox_keep.png` 右边）：直的、带倒刺的深紫剑身，血红刃口，浅紫亮纹，护手旁边发光的橙色眼睛，
  两叉带钩的剑尖；约 20 格长、4–5 格粗；两手握在胯旁，剑尖朝左下、刚好在地面上方。只能跟着手的位置平移。
- **两只脚一样的爪形铁靴**，脚尖朝外（近侧的脚尖朝左、远侧的朝右，用户刚选的）。
- 配色（`palette/aatrox_palette_now.png` 的 18 色）、一道近黑描边 `#0A0408`、**3/4 正面朝右**、待机站姿（双手握剑在胯旁、
  翅膀半收在背后）。

## 要改的东西（瘦身）

1. **总高（翅尖或角尖到鞋底）40 格**（39–41 都可以）：头盔连角到鞋底 38 格，翅尖最多比角尖高 2 行。
2. **身体窄**：肩甲、胸口连两只手臂，不算翅膀和剑，**最宽 16–20 格**（现在 27）；腰 8–10 格；手臂 3–4 格粗、贴近身体；
   肩甲最多比肩膀多出 2 格。
3. **翅膀收紧**：还是半收在背后的样子（深紫翼膜、血红翼边、钢灰色的翼骨尖），但**贴着身体**：每边最多伸出身体轮廓 4–5 格，
   近侧的翅膀藏在近侧肩膀后面，**不要在身体两边各立一大块**。
4. **腿长一点、细一点**：腰带到鞋底 14–16 行（现在 11）；每条腿 4–5 格宽（护膝、靴子最多 6 格），两腿之间空 2–4 格；
   两只鞋底相距 10–14 格（现在 34 格宽）。
5. 整个人（连翅膀和剑）的像素总数 **780–900**（现在 1084）。

## 三个方案（A、B、C 都要，用户来挑）

| 方案 | 头盔连角 | 上身（下巴到腰带） | 腿（腰带到鞋底） | 身体连手臂 | 每条腿 | 翅膀伸出 | 总像素 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **A** 照 oppi 的瘦 | 11 | 12 | 15 | 16–17 | 4 | ≤ 4 | 780–830 |
| **B** 还是重甲大块头，只是瘦一圈 | 11 | 13 | 14 | 19–20 | 5 | ≤ 5 | 850–900 |
| **C** 腿更长 | 11 | 11 | 16 | 17–18 | 4 | ≤ 4 | 800–860 |

## 规则

- **做法**：生图直接出大方块像素画（方块多大都行），再按方块读回 1 格 1 像素；读回后人 40 格高、读回的图和生图一样干净才合格，
  不合格就重新生成。**不要把细节比方块还小的高清图压缩下来**（会糊成碎点），**也不要用代码一块一块拼**身体（头和剑可以照原样贴回）。
- 一道深色外描边（`#0A0408`），里面用材质自己的暗色；不要半透明，不要抗锯齿；脚下面什么都不要画（血条在那里）。
- 颜色用 `palette/aatrox_palette_now.png` 的颜色，总共 24 色以内；红眼睛的颜色只用在眼睛和剑上已有的地方。
- 背景透明（做不到就纯绿 `#00FF00`；**不要洋红**，会吃掉紫色的翅膀和剑身）。
- 这一包**只画待机造型**（每个方案一张）。用户选定以后，动作条另外出包，都从你这一版画。

## 要交的东西

放在 **`outputs/aatrox-model-v2/`**：
- `aatrox_design_A.png`、`aatrox_design_B.png`、`aatrox_design_C.png`：生图原稿（大方块）；
- `logical/aatrox_design_<A|B|C>_1x.png`：读回的 1 格 1 像素，透明背景；
- `logical/aatrox_design_<A|B|C>_canvas.png`：同一张放在 1024×1024 画布上（每格 8×8，脚底在第 99 行，两脚中间在第 64 列，和
  `ours_now/aatrox_design_now_canvas.png` 一样）；
- `HANDOFF.md`：每张的方块大小（px）、读回后多高多宽、身体连手臂多宽、腿几行、总像素；**最后写它**，写完就是交付了。

## 提示词（生图用）

```text
Pixel art game sprite of Aatrox from League of Legends for a small tactics game, ONE character, full body, 3/4 front
view facing right, standing with feet apart, holding a huge greatsword low in both hands at his hip with the blade
pointing down-left, its tip just above the ground. A LEAN demon knight, not bulky: the figure about 38 squares from
the horn tips to the soles; the head exactly like the attached head (a dark horned helm, the face in shadow, two red
eyes) 11 squares tall; shoulders and both arms together at most 16-20 squares wide, arms 3-4 squares thick close to
the body, a narrow waist; legs 14-16 squares from the belt to the soles, each leg 4-5 squares wide in dark steel-teal
greaves, a clear gap between the legs, both feet the same big clawed boot with the toes pointing outward. Two demon
wings HALF-FOLDED tight behind his shoulders (dark plum membrane, crimson edges, steel bone tips), sticking out at
most 4-5 squares beside the body and at most 2 squares above the horns. Crimson chest armour with a glowing orange
rune, steel-teal pauldrons and gauntlets. The greatsword exactly like the attached sword (straight barbed dark plum
blade, blood-red edges, a glowing orange eye by the guard, a two-pronged hooked tip). Chunky square pixels on a
strict grid, hard edges, no anti-aliasing, one near-black outline, 3-4 shades per material. Transparent background
(else pure green #00FF00, never magenta). No text, no grid lines, no border.
```
附图顺序：`ours_now/aatrox_design_now.png`（现在的造型：配色、头、剑、站姿都照它）、`keep/aatrox_keep.png`（头和剑一格不改）、
`ref_approved/caitlyn_v1_vs_v2.png`（我们自己改好的凯特琳：要的就是这种变化）、`ref_structure/oppi_structure.png`（只看身材比例和翅膀收法）、
`ours_now/ours_vs_oppi.png`（哪里要改）、`picture/aatrox-model-A-gpt.png`（原画，需要时看服装细节）。
