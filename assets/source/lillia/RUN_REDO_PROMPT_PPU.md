# 莉莉娅：跑步第 1 张重画（给 Codex 的提示词）

> 上一轮的动作都用上了，**只有跑步的第 1 张模板（`run_1`：第 1、2 帧）要重画**：这一张画得比她别的跑步图**粗一倍左右**（一个像素块约 14 像素，别的跑步图约 10–11 像素），**脸被藤蔓挡住**，头发和藤蔓糊成一团。和第 3–8 帧连起来跑，第 1、2 帧会突然变糙。这次照 `refs/style.png`（你上一轮交的 `run_2`，第 3、4 帧）的**画法和像素大小**重画第 1、2 帧：
> - **像素块和 `refs/style.png` 一样细**（模板里每格 6 像素），描边一样细。
> - **脸露出来**：桃色的脸、青色的大眼睛清清楚楚，**脸上不要有藤蔓**；藤蔓和叶子只在头发里、肩上和上衣上，照设计图。
> - 头发、花、上衣、枝条法杖和铃铛照设计图（`refs/design.png`），和 `refs/style.png` 里的她一模一样。
> - **四条腿照浅色人影**：上一轮这一张的腿已经对了（远侧的前腿补回来了，四只紫色蹄子都在），姿势照旧——后腿往后蹬、前腿往前伸。
>
> 人物照旧全部照定稿设计图：**粉红色的长发**、**绿色的藤蔓和叶子**、头顶**紫色和青色的花**、**桃色的脸**、**青色的大眼睛**；**绿色叶子做的上衣**；**蓝紫色宝石、橙色弯钩、橙黄色花铃铛和金色叶子的枝条法杖**；**橙色的小鹿身子**、**紫色的斑点**、**奶白色的肚子和白色的小尾巴**；**四条细长的橙色腿**、**紫色的小蹄子**。头的大小和设计图一样（头发顶（不算头上的花）到下巴约 30 格）。不画任何特效。

**像素规则、背景、交付**和上一轮一样：和设计图同样密度的方块（模板里每格 6 像素，和 `refs/style.png` 一样细）、近黑描边、只用调色板的颜色、不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**；模板上的浅色人影、线、字全部不要留下。

- 交付：`outputs/lillia-run/run_1.png`（1536×1024，和模板一样两格）；原始生成图放进 `outputs/lillia-run/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/lillia-run/HANDOFF.md`，再打包成 `outputs/lillia_run_done.zip`。

## 附图（压缩包 `lillia_run_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、头的大小、颜色 |
| `templates/run_1.png` | 两格的模板，浅色人影是要摆的姿势 | **第二张**：身体、四条腿、手和枝条的位置和大小 |
| `refs/old_run_1.png` | 旧版这两帧的彩色原图（放大） | **第三张**：身体和腿怎么摆（衣服不照它） |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 lillia-A） | **第五张**：细节 |
| `refs/style.png` | 你上一轮交的 `run_2`（第 3、4 帧） | **第六张**：**照它的画法和像素大小**，脸要像它一样清楚 |
| `sheets.json` | 这张是第几帧、怎么拿枝条（`weapons`）、腿（`legs`） | 填提示词 |

## 提示词（换掉 <...>）

附图顺序：`refs/design.png`、`templates/run_1.png`、`refs/old_run_1.png`、`refs/design_palette.png`、`refs/design_picture.png`、`refs/style.png`。

```text
Six attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a fawn spirit, a girl above the waist and a fawn below it - LONG PINK HAIR with GREEN VINES AND LEAVES and a VIOLET AND CYAN FLOWER, a PEACH FACE with BIG CYAN EYES, a top of GREEN LEAVES, a BRANCH STAFF with a BLUE-VIOLET GEM, an ORANGE HOOK, an ORANGE-YELLOW FLOWER BELL and a GOLDEN LEAF, an ORANGE FAWN BODY with VIOLET SPOTS, a CREAM BELLY and a WHITE TAIL, FOUR THIN ORANGE LEGS and VIOLET HOOVES - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 6 is a sheet of the same run you drew before (frames 3-4): DRAW IN EXACTLY ITS STYLE AND PIXEL SIZE - the same small squares, the same thin outline, the same clear face. Image 2 is a TEMPLATE of 2 animation frames of her RUN, frames 1, 2: in each cell the PALE FIGURE is the body pose to draw, the grey horizontal line the ground, the short tick the standing point, the grey bar on the left the height standing. Image 3 is the same old frames in colour: copy their body pose and legs - not the old costume. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (or flat pure white, no glow, no shadow), the SAME cell layout as image 2: in each cell image 1's character in that cell's pose, at its place and size, the hooves on the ground line. One scale for the sheet, set by the grey bar. Do not rescale, crop or re-lay it.
WHY IT IS DRAWN AGAIN: the last sheet of these two frames came out with squares about twice as big as image 6's and her face hidden under vines. Now: squares as small as image 6's (the template's 6 px), her FACE CLEAR - peach skin, big cyan eyes, nothing across it; the vines and leaves only in her hair, on her shoulders and on her top, as in image 1.
She is EXACTLY image 1 and image 6: the same hair, flower, face, top, branch staff and bell, fawn body, four legs and violet hooves, image 4's colours only. THE HEAD THE SAME SIZE AS IN IMAGE 1 (about 30 squares from the top of her hair, the flower not counted, to her chin). The body, arms and legs the same length and thickness as image 1 (bent, never stretched or shrunk).
<ARMS>
THE LEGS: <LEGS>
NO EFFECTS AT ALL: no dream dust, no petals, no glow, no afterimages; the gem's light stays inside the gem.
THE PIXEL GRID: squares the size of the template's (6 px), as in image 6, on one straight grid; the near-black outline of image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<ARMS>`、`<LEGS>` 照 `sheets.json` 里这张的 `weapons`、`legs` 填。

## 交回前请检查

- **像素块和 `refs/style.png` 一样细**，两张放在一起看不出是两种画法；**脸清楚、脸上没有藤蔓**。
- 四条腿照浅色人影、四只紫色蹄子都在；头和设计图一样大；只用设计图的颜色；没有特效；1536×1024、和模板一样两格、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/lillia-run/HANDOFF.md`，再打包成 `outputs/lillia_run_done.zip`。
