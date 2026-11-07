# 洛：5 张模板只重画头（给 Codex 的提示词）

> 上一轮的动作都用上了，**只有这 5 张要重画：头画大了一号**。用户看动画时说「怎么模型会突然变大变小」：这几帧你把头画成了**正脸、比设计图大约 15%**（白发露出一大片），前后帧的头都是设计图的大小，所以播到这里头会突然变大、下一帧又缩回去。**身体、手臂、腿、披风、姿势、位置、大小都对，一点都不要动，只把头画回设计图的大小。**
>
> | 模板 | 哪一帧 | 头照哪张画 |
> |---|---|---|
> | `skill2_1` | W 冲刺第 1 帧（蹲下蓄力） | `refs/style.png` |
> | `e_dash_1` | E 起跳第 1 帧（朝左跳起、双臂张开） | `refs/style_left.png` |
> | `e_land_1` | E 落地第 1 帧（朝左落地、低蹲） | `refs/style_left.png` |
> | `dead_4` | 死亡第 5 帧（扑倒在地） | `refs/style_dead.png` |
> | `dead_6` | 死亡第 7 帧（趴在地上，第 8 帧同这张） | `refs/style_dead.png` |
>
> - **头和设计图（`refs/design.png`）一样大**：羽冠顶到下巴约 **28 格**，白发约 **20 格高、25 格宽**，四分之三侧脸（E 的两张朝画面左边，就是设计图左右翻过来），**不要画成正脸**。`refs/style*.png` 是你上一轮交的、头大小正好的帧，照它的头画。
> - **照 `refs/prev_<名>.png` 画**：那是你上一轮画的这一张。身体、手臂、腿、披风的形状、大小、位置**和它一模一样**，只换头；头变小了，身子不要跟着变大变小，也不要挪位置。
> - 人物照旧全部照定稿设计图：**红色的羽冠**、**白发**、**红耳尖的长耳朵**、**绿色的眼睛**；**红色金边的高领**、**赤裸的上身**、**金色的护腕**、**鸟头骨的腰带**；**深绿色的灯笼裤**和**红色的绑带**；**紫灰色的鸟爪脚**；**羽毛披风**。不画任何特效。

**像素规则、背景、交付**和上一轮一样：模板每格 9 像素，和 `refs/style*.png` 一样大的方块；2 格近黑描边；只用调色板的颜色，不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**。

- 交付：`outputs/rakan-head/<名>.png`（5 张，1536×1024，和模板一样的格子布局）；原始生成图放进 `outputs/rakan-head/raw/<名>-generated.png`；附 `generation-prompts.txt`；**最后**写 `outputs/rakan-head/HANDOFF.md`，再打包成 `outputs/rakan_head_done.zip`。

## 附图（压缩包 `rakan_head_redo.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、头的大小、颜色 |
| `templates/<名>.png` | 模板，浅色人影是要摆的姿势 | **第二张**：位置和大小 |
| `refs/old_<名>.png` | 旧版同一帧的彩色原图 | **第三张**：身体动作 |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 rakan-A） | **第五张**：细节 |
| `refs/prev_<名>.png` | **你上一轮画的这一张** | **第六张**：身体、披风、姿势照它，**只换头** |
| `refs/style*.png` | 你上一轮交的、头大小正好的一张（朝右 `style`、朝左 `style_left`、趴地 `style_dead`） | **第七张**：**头照它的大小画** |
| `sheets.json` | 每张是第几帧、手怎么摆（`weapons`）、用哪张 style | 填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/<名>.png`、`refs/old_<名>.png`、`refs/design_palette.png`、`refs/design_picture.png`、`refs/prev_<名>.png`、`sheets.json` 里这张的 `style`。

```text
Seven attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a charming feathered dancer - a RED FEATHER CREST, WHITE HAIR, LONG RED-TIPPED EARS, GREEN EYES, a high RED COLLAR with GOLD TRIM, a BARE CHEST, GOLD BRACERS, a BIRD-SKULL BELT, BAGGY DARK GREEN TROUSERS with RED TIES, GREY-VIOLET BIRD-CLAW FEET, a FEATHER CLOAK with red-and-gold shoulders, long gold-orange feathers and rainbow tips - 3/4 view facing right. Image 2 is a TEMPLATE of <N> frame(s) of <ACTION>, frame(s) <FRAMES>: the PALE FIGURE is the pose, the grey line the ground. Image 3 is the same old frame in colour. Image 4 is image 1's palette. Image 5 the picture image 1 was read from. Image 6 is YOUR PREVIOUS DRAWING OF THIS SHEET. Image 7 is a sheet you drew before whose HEAD IS THE RIGHT SIZE.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (or flat pure white, no glow, no shadow), the SAME cell layout as image 2.
THIS SHEET IS DRAWN AGAIN ONLY BECAUSE THE HEAD WAS TOO BIG: in image 6 the head is a frontal face about 15 % bigger than image 1's. Draw it again EXACTLY as image 6 - the same body, arms, legs, feet, cloak and feathers, their shapes, sizes and places, the same pose at the same place - with ONLY THE HEAD redrawn at image 1's and image 7's size: about 28 squares from the top of the feather crest to the chin, the white hair about 20 squares tall and 25 wide, a 3/4 face as in image 1 (<FACING>), never a frontal face, never bigger. The body keeps its size: a smaller head must not make the body bigger or move it.
<ARMS>
He is EXACTLY image 1: the same crest, hair, ears, eyes, collar, bracers, belt, trousers, feet and cloak, image 4's colours only.
NO EFFECTS AT ALL: no flying feathers, no sparkles, no trails, no afterimages.
THE PIXEL GRID: squares the size of the template's (9 px), as in image 7, on one straight grid; a 2-square near-black outline as in image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<ARMS>` 照 `sheets.json` 每张的 `cells`、`action`、`frames`、`weapons` 填；`<FACING>`：`e_dash_1`、`e_land_1` 填 `turned to the picture's LEFT, as image 7 and image 6`，`dead_4`、`dead_6` 填 `lying face down as in image 6 and image 7`，`skill2_1` 填 `facing right`。

## 交回前请检查

- **每张的头都和设计图、`refs/style*.png` 一样大**：羽冠顶到下巴约 28 格，白发约 20 格高、25 格宽，四分之三侧脸，**不是正脸**——比上一轮小一号。
- 除了头，**和 `refs/prev_<名>.png` 一模一样**：身体、手臂、腿、披风的形状、大小、位置不变；只用设计图的颜色；没有特效；每张 1536×1024、和模板一样的格子布局、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/rakan-head/HANDOFF.md`，再打包成 `outputs/rakan_head_done.zip`。

## Claude 收到后（给 Claude 看）

- 五张换进 `assets/source/rakan/hd/casts/`（与选定 raw 逐字节一致），`casts_rakan_hd.py --fits` 重量这 5 帧的缩放、`--heads` 复查（目标 1.00–1.06，他别的帧约 1.04），GIF 逐帧查新版相邻帧的大小变化不超过旧版；再走 `rig_rakan_hd.py` → `ppu_restyle` → `ppu_hd` → `ppu_one` → `--one-ground` → `hero_reels`。
