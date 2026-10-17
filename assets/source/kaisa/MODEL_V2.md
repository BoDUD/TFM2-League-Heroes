# 卡莎：新造型（第 2 版，瘦一点、脸小一点；给 Codex 的提示词）

> **为什么重画**：用户说现在的卡莎「身宽体胖 脸大」——和凯特琳之前被玩家说的问题一样。凯特琳已经照 oppi 的身材比例重画好了，
> 用户很满意（`ref_approved/caitlyn_v1_vs_v2.png`：左边旧的、右边新的）。卡莎也要这样改。**不要把现有的精灵图机械地拉长或切行**
> （凯特琳试过，靴子变柱子、头发变平板，被否了），请你**重画造型**。
>
> 对照 `ours_now/ours_vs_oppi.png`（都是 8 倍，左边的色条标出每一段几行）：
> - **我们现在 44 行 × 33 格宽、932 个像素**：头发 12 行 + 脸 11 行 = 头占了 23 行，一半多（红框）；脸的皮肤区 11 行 × 10 格（粉框），
>   额头露出 4 行皮肤、眼睛下面还有 5 行；上身 7 行，腰以下的腿只有 14 行（橙框）；肩甲连手臂 28 格宽（蓝框），
>   两侧的背囊再把人撑到 33 格宽（黄框）。
> - **oppi 的女英雄**（莎弥拉 37 行、金克丝 36 行、凯特琳 37 行）：头只有 11–12 行（约 30%；凯特琳连礼帽 15 行），脸 6–7 行 × 5–6 格，
>   腿 15–16 行（40–43%），每条腿 3–4 格宽、两腿分开；连她们的大武器在内也只有 630–700 个像素。
>
> **`ref_structure/oppi_structure.png` 只看身材比例和结构，不许照着描、不许复制像素**（那是 oppi 团队的作品，而且它没有卡莎），
> 要画**我们自己的**卡莎。

## 造型要求

1. **服装、配色照我们的原画 `picture/kaisa-model-B.png`**（用户选的那张）：深紫色长发、虚空紫色铠甲（金色描边、洋红色发光纹路）、
   浅蓝灰色的贴身战衣、两只手是带爪的护手（掌心洋红发光）、**背后两片翅膀一样的背囊竖起来**（洋红发光、金边）。
2. **3/4 侧面朝右**，站姿和现在的待机一样：两脚分开站稳，两手垂在身体两侧、稍微张开。
3. **总高（发顶到鞋底）40 格**（39–41 都可以）；背囊尖最多比发顶高 3 行（整张图最多 43 行）。
4. **头小**：发顶到下巴 11–14 行（现在 23）；**脸的皮肤区最多 7 行 × 7 格**（现在 11 × 10）：刘海盖到眉毛（额头最多露 1 行皮肤），
   眼睛下面只留 2 行皮肤再到下巴。头连头发最多 13 格宽；长发顺着后背垂下、贴着身体，不要在头顶堆成一大团。
5. **瘦**：上身（领口到腰带）9–10 行；肩膀连手臂最多 16–18 格宽（现在 28）；腰 6–7 格；**腿从腰带到鞋底 17–20 行**（现在 14），
   每条腿 3–4 格宽（护甲片最多 5 格），两腿之间空 1–3 格；手臂 3 格粗，贴近身体。
6. **背囊**：保留竖起来的样子，但要**窄**：每片最多 5 格宽，最多伸出身体轮廓 3–4 格；**不算背囊人最宽 18 格，算上最宽 26 格**（现在 33）。
   整个人（连背囊）的像素总数 650–750（现在 932）。
7. **脸**保留我们现在的画法（`ours_now/kaisa_head_now.png`），只是变小：每只眼睛 2 格宽、3 行（最上面一行深色睫毛，下面两行是浅色高光、
   白色和紫色瞳孔 `#823EA3` / `#74368E`），近处的眼睛在左、远处的眼睛靠右边脸颊，两眼之间 2–3 格皮肤；额头/脸颊的紫色虚空纹最多 1–2 格；
   可以有 1 格深粉色的嘴，也可以不画嘴。

## 三个方案（A、B、C 都要，用户来挑）

| 方案 | 头发 | 脸 | 上身 | 大腿（腰带到膝盖） | 小腿 + 鞋 | 合计 |
|---|---:|---:|---:|---:|---:|---:|
| **A** 照 oppi（莎弥拉、金克丝）的比例 | 5 | 7 | 10 | 8 | 10 | 40 |
| **B** 腿更长，像原画那样修长 | 4 | 7 | 9 | 9 | 11 | 40 |
| **C** 头稍大一点，保留一点 Q 版感（头约占 1/3） | 6 | 8 | 9 | 7 | 10 | 40 |

三个方案都要瘦（上面第 5、6 条），只是头和腿的比例不同。

## 规则

- **做法**：生图直接出大方块像素画（方块多大都行），再按方块读回 1 格 1 像素；读回后人 40 格高、读回的图和生图一样干净才合格，
  不合格就重新生成。**不要把细节比方块还小的高清图压缩下来**（会糊成碎点），**也不要用代码一块一块拼**。
- 一道深色外描边（`#160722`），里面用材质自己的暗色；不要半透明，不要抗锯齿；脚下面什么都不要画（血条在那里）。
- 颜色以 `palette/kaisa_palette_now.png`（现在的 34 色）为主，总共 32 色以内；眼睛的紫色只用在眼睛里。
- 背景透明（做不到就纯绿 `#00FF00`；**绝对不要洋红**，卡莎身上有洋红，会被一起抠掉）。
- 这一包**只画待机造型**（每个方案一张）。用户选定以后，动作另外做，都从你这一版来。

## 要交的东西

放在 **`outputs/kaisa-model-v2/`**：
- `kaisa_design_A.png`、`kaisa_design_B.png`、`kaisa_design_C.png`：生图原稿（大方块）；
- `logical/kaisa_design_<A|B|C>_1x.png`：读回的 1 格 1 像素，透明背景；
- `HANDOFF.md`：每张的方块大小（px）、读回后多高多宽、每段（头发、脸、上身、大腿、小腿）各几行；**最后写它**，写完就是交付了。

## 提示词（生图用）

```text
Pixel art game sprite of Kai'Sa from League of Legends for a small tactics game, ONE character, full body, 3/4 view
facing right, standing with feet apart, arms hanging slightly away from her sides with clawed gauntlets. SLIM,
LONG-LEGGED proportions with a SMALL head: the figure about 40 squares tall from the top of the hair to the soles -
head 11-14 squares from the hair top to the chin, a small face (at most 7 x 7 squares of skin, the fringe down to the
eyebrows, two eyes each 2 squares wide with a dark lash row over a white highlight and a purple iris), torso 9-10,
legs 17-20 squares from the belt to the soles, each leg 3-4 squares wide with a clear gap between the legs, arms 3
squares thick close to the body. Long dark purple hair falling down her back close to the body. Pale blue-grey
bodysuit, dark void-purple armour plates on shoulders, forearms, hips, thighs and shins with gold trim and glowing
magenta lines, magenta glowing palms. Two narrow wing-like pods raised behind her shoulders (dark purple, gold rims,
magenta glow), at most 5 squares wide each and no higher than 3 squares above her head. Chunky square pixels on a
strict grid, hard edges, no anti-aliasing, one dark outline, 3-4 shades per material. Transparent background (else
pure green #00FF00, never magenta). No text, no grid lines, no border.
```
附图顺序：`picture/kaisa-model-B.png`（服装、配色、背囊）、`ref_approved/caitlyn_v1_vs_v2.png`（我们自己改好的凯特琳：要的就是这种变化）、
`ref_structure/oppi_structure.png`（只看身材比例）、`ours_now/ours_vs_oppi.png`（哪里要改）、`ours_now/kaisa_head_now.png`（脸的画法）。
