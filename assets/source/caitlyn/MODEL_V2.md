# 凯特琳：新造型（第 2 版，照 oppi 的身材比例；给 Codex 的提示词）

> **为什么重画**：玩家说现在的凯特琳「腿太短、太胖」。用户：「参考oppi的女警调整一波」「别人oppi的凯特琳身材就没问题」。我们先试过把现有精灵图的腿机械地拉长 3 行、背后头发切掉 2 格（`ours_now/rejected_stretch.png` 右边），用户否了：靴子被拉成两根柱子，头发被切成一块平板。所以这次请你**重画造型**。
>
> 对照 `ours_now/ours_vs_oppi.png`（都是 8 倍，左边的色条标出每一段几行）：
> - **我们现在 41 行**：礼帽 10 + 脸 10 = 20 行，占了一半（红框）；上身 7、裙子 5、腿 9，腿是两根又短又粗的靴子（橙框）；背后的头发往左摊开一大片（黄框）。所以又矮又胖。
> - **oppi 的 37 行**：礼帽 8、脸 7、上身 7、裙子 7、腿 8。头和帽子窄（13–16 格宽），头发顺着后背垂下、贴着身体，两条腿分开站，整个人瘦长。
>
> **`ref_structure/oppi_caitlyn_structure.png` 只看身材比例和结构，不许照着描、不许复制像素**（那是 oppi 团队的作品），要画**我们自己的**凯特琳。

## 造型要求

1. **服装、配色、持枪照我们的原画 `picture/caitlyn-model-A.png`**（用户选的那张）：紫色大礼帽（金色帽带、青色宝石）、深蓝色长直发、蓝眼睛、白衬衫和褶边领、紫色短外套和短裙（金边，裙摆一圈白色褶边）、棕色手套和腰封、藏青裤袜、棕色长靴（金扣）；金色长步枪（青色瞄准镜），**双手斜握在身前：枪托在身后左边的胯旁，枪管朝右上**。
2. **3/4 侧面朝右**，站姿和现在的待机一样：两脚分开站稳。
3. **身材照 oppi 的比例**：
   - 总高（帽顶到鞋底）**40 格**（39–41 都可以）；
   - **头加帽子不超过 16 行**（现在是 20）：礼帽 7–8 行（含帽檐），脸和头发 7–9 行；
   - 上身 7–8 行，短裙 6–7 行（裙摆的白褶边 1 行），**腿 9–12 行**（裙摆下面到鞋底）；
   - **瘦**：每条腿 3 格宽（靴口最多 4 格），两腿之间空 2–4 格；裙子只比胯宽 1–2 格；不算步枪，人最宽 16–18 格；
   - **头发**：顺着后背垂到腰，贴着身体，最多比身体轮廓多出 3–4 格，**不要往左摊成一大片**。
4. **脸**保留我们现在的画法（`ours_now/caitlyn_head_now.png`）：蓝眼睛每只 2×2、小尺寸下看得清，嘴一点红；头宽 11–13 格。
5. **枪**：1 格粗的金色枪管（上下深色描边），末端 2×2 的枪口（金、青），青色瞄准镜；枪身的斜度和现在差不多（约 1/3）。

## 三个方案（A、B、C 都要，用户来挑）

- **A**：照 oppi 的比例放大到 40 格：帽 8、脸 8、上身 8、裙 7、腿 9。
- **B**：腿更长：帽 7、脸 8、上身 7、裙 6、腿 12。
- **C**：脸稍大，保留一点 Q 版感：帽 8、脸 9、上身 7、裙 6、腿 10；腿和头发一样要瘦。

## 规则

- **做法**：生图直接出大方块像素画（方块多大都行），再按方块读回 1 格 1 像素；读回后人 40 格高、读回的图和生图一样干净才合格，不合格就重新生成。**不要把细节比方块还小的高清图压缩下来**（会糊成碎点），**也不要用代码一块一块拼**。
- 一道深色外描边（`#100216` 或 `#1D1C34`），里面用材质自己的暗色；不要半透明，不要抗锯齿。
- 颜色以 `palette/caitlyn_palette_now.png`（现在的 24 色）为主，可以加同色系的过渡色，总共 32 色以内；眼睛的蓝只用在眼睛里。
- 背景透明（做不到就纯绿 `#00FF00`；**不要洋红**，会吃掉紫色）。
- 这一包**只画待机造型**（每个方案一张）。用户选定以后，动作条另外出包，都从你这一版画。

## 要交的东西

放在 **`outputs/caitlyn-model-v2/`**：
- `caitlyn_design_A.png`、`caitlyn_design_B.png`、`caitlyn_design_C.png`：生图原稿（大方块）；
- `logical/caitlyn_design_<A|B|C>_1x.png`：读回的 1 格 1 像素，透明背景；
- `HANDOFF.md`：每张的方块大小（px）、读回后多高多宽、每段（帽、脸、上身、裙、腿）各几行；最后写它，写完就是交付了。

## 提示词（生图用）

```text
Pixel art game sprite of Caitlyn from League of Legends for a small tactics game, ONE character, full body, 3/4 view
facing right, standing with feet apart, holding a long golden rifle diagonally across her body with both gloved hands
(stock at her left hip behind her, barrel pointing up-right, cyan scope). SLIM, LONG-LEGGED proportions: the figure
about 40 squares tall - top hat 7-8 squares, face 8, torso 7-8, short skirt 6-7, legs 9-12 squares from the skirt hem
to the soles, each leg 3 squares wide with a clear gap between the legs. Purple top hat with a gold band and a cyan
gem, long straight navy-blue hair falling down her back close to the body (not spreading out), a small face with blue
eyes, white blouse with a ruffled collar, purple short jacket and short skirt with gold trim and a thin white frill at
the hem, brown gloves and corset belt, navy tights, brown knee boots with gold buckles. Chunky square pixels on a strict
grid, hard edges, no anti-aliasing, one dark outline, 3-4 shades per material. Transparent background (else pure green
#00FF00, never magenta). No text, no grid lines, no border.
```
附图顺序：`picture/caitlyn-model-A.png`（服装、配色、持枪）、`ref_structure/oppi_caitlyn_structure.png`（只看身材比例）、`ours_now/ours_vs_oppi.png`（哪里要改）。
