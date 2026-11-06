# 维克托：Q 第 3–4 帧、R 第 1–3 帧重画（给 Codex 的提示词）

> 上一轮的动作都用上了，**只有这三张模板要重画：`skill_2`（Q 第 3、4 帧）、`ult_1`（R 第 1、2 帧）、`ult_2`（R 第 3 帧）**——这几帧的**头画大了一号**：面具从帽冠下沿到下巴约 17–18 格、宽 13–14 格，设计图是 **15 格高、12 格宽**；整个头（金色帽冠顶到面具下巴）也比设计图的约 22 格多出两三格。身体、法杖和姿势都对，**只要把头画回设计图的大小**。
> - **头和 `refs/style.png` 里的他一样大**（那是你上一轮交的 `skill_1`，头的大小正好）：金色帽冠顶到面具下巴约 **22 格**，银蓝色面具约 **15 格高、12 格宽**，一只青色的眼睛。
> - 身体、手臂、腿、披风、法杖照浅色人影，和上一轮一样；身高（灰色竖条）不变——头变小了，身子不要跟着变大或变小。
> - 第 3、4 帧（`skill_2`）：身子前倾，法杖往前、往下挥（照浅色人影）；R 第 1、2 帧（`ult_1`）：近侧手臂笔直往前指；R 第 3 帧（`ult_2`）：法杖的金色杖头离开杖顶浮在上方，杖身上的金环还在。
>
> 人物照旧全部照定稿设计图（`refs/design.png`）：**棕色的兜帽和金色的帽冠**、**银蓝色的面具和一只青色的眼睛**、**蓝色的披肩和金色的扣子**、**深石板色的盔甲、金色的镶边和发光的金色核心**、**深红色的披风**、**高高的金色法杖、金环和镶着蓝宝石的金色杖头**、**深色的靴子**。四分之三侧身、朝画面右边。不画任何特效（没有光束、重力场、风暴、光晕）。

**像素规则、背景、交付**和上一轮一样：和设计图同样密度的方块（模板里每格 10 像素，和 `refs/style.png` 一样）、2 格近黑描边、只用调色板的颜色、不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**。

- 交付：`outputs/viktor-head/skill_2.png`、`ult_1.png`、`ult_2.png`（1536×1024，和模板一样的格子布局）；原始生成图放进 `outputs/viktor-head/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/viktor-head/HANDOFF.md`，再打包成 `outputs/viktor_head_done.zip`。

## 附图（压缩包 `viktor_head_redo.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、头的大小、颜色 |
| `templates/<名>.png` | 一格或两格的模板，浅色人影是要摆的姿势 | **第二张**：身体、手臂、法杖的位置和大小 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：身体动作、手和法杖在哪 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 viktor-A） | **第五张**：细节 |
| `refs/style.png` | 你上一轮交的 `skill_1`（Q 第 1、2 帧） | **第六张**：**头照它的大小画**，像素块一样大 |
| `sheets.json` | 每张是第几帧、怎么拿法杖（`weapons`） | 填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`、`refs/style.png`。

```text
Six attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a hextech inventor - a BROWN HOOD with a GOLD CREST, a SILVER-BLUE MASK with ONE CYAN EYE, a BLUE MANTLE with a GOLD CLASP, DARK SLATE ARMOUR with GOLD TRIM and a GLOWING GOLD CORE, a CRIMSON CAPE, a TALL GOLD STAFF with a GOLD RING and a GOLD HEAD holding a BLUE GEM, DARK BOOTS - 3/4 view facing right. Image 2 is a TEMPLATE of <N> frame(s) of <ACTION>, frame(s) <FRAMES>: in each cell the PALE FIGURE is the body pose (the old frame scaled to his height), the grey line the ground, the grey bar on the left his height standing. Image 3 is the same old frame(s) in colour. Image 4 is image 1's palette. Image 5 the picture image 1 was read from. Image 6 is a sheet you drew before whose HEAD IS THE RIGHT SIZE.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (or flat pure white, no glow, no shadow), the SAME cell layout as image 2: image 1's character in the pale figure's pose, at its place and size, standing on the ground line.
THIS SHEET IS DRAWN AGAIN BECAUSE THE HEAD WAS TOO BIG: draw the head EXACTLY as big as in image 1 and image 6 - about 22 squares from the top of his gold crest to the chin of his mask, the silver-blue mask about 15 squares tall and 12 wide, one cyan eye. Never bigger. The body keeps its height: a smaller head must not make the body bigger.
<ARMS>
He is EXACTLY image 1: the same hood, crest, mask, mantle, armour, core, cape, staff and boots, image 4's colours only; the body, arms and legs the same length and thickness as in image 1 (bent, never stretched).
NO EFFECTS: no rays, no gravity field, no storm, no lightning, no glow; the eye's cyan stays inside the eye.
THE PIXEL GRID: squares the size of the template's (10 px), as in image 6, on one straight grid; a 2-square near-black outline as in image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>` 照 `sheets.json` 每张的 `cells`、`action`、`frames`、`weapons` 填。

## 交回前请检查

- **每帧的头都和设计图、`refs/style.png` 一样大**：帽冠顶到下巴约 22 格，面具约 15 格高、12 格宽——比上一轮小一号。
- 身体、手臂、法杖照浅色人影；身高不变；只用设计图的颜色；没有特效；每张 1536×1024、和模板一样的格子布局、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/viktor-head/HANDOFF.md`，再打包成 `outputs/viktor_head_done.zip`。

## Claude 收到后（给 Claude 看）

- 三张换进 `assets/source/viktor/hd/casts/`（与选定 raw 逐字节一致），`casts_viktor_hd.py --fits` 重量这 5 帧的缩放、`--heads` 复查（目标 0.95–1.08），再走 `rig_viktor_hd.py` → `ppu_restyle` → `ppu_hd` → `ppu_one` → `--one-ground` → `hero_reels`。
