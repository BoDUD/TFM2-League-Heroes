# 布里茨：跑步第 1 帧重画（给 Codex 的提示词）

> 跑步重画的 8 帧，第 2–8 帧都用上了，**只有第 1 帧（`run_1`）要再画一次**：这一帧画成了**正对着看画的人**——头在身子正中间、两只拳头左右对称张开、仪表圈在正中，而旧版第 1 帧（`refs/old_run_1.png`）和你画的第 2–8 帧都是**四分之三侧身、朝画面右边**（头在身子偏右、身子往右伸）。连起来跑，每一圈都会突然转正一下。这一帧也画大了一圈。
>
> 这次照 `refs/style.png`（你交的 `run_2`，第 2 帧）的**朝向和大小**重画第 1 帧：
> - **四分之三侧身，朝画面右边**，和 `refs/style.png` 一样：头在身子偏右，仪表圈偏右，近侧（左边）的肩和手臂在前、远侧的手臂在身子后面往右前方伸。
> - **身体和两只拳头照模板的浅色人影**：近侧拳头在左下方，远侧手臂往右前方伸、拳头在右边。
> - **大小和 `refs/style.png` 一样**：整张按灰色竖条定大小，头（金色小头从头顶到下巴约 12 格）、身子、拳头都和第 2 帧一样大。
> - **腿照上一轮第 1 帧的写法**（`sheets.json` 的 `legs`）：近侧（颜色亮）活塞腿笔直踩在胯下，金色大脚平踩地面线；远侧（颜色暗）腿弯着往后踢起，脚离地。
>
> 人物照旧全部照定稿设计图（`refs/design.png`），只用调色板的颜色，不画任何特效（不画蒸汽、电光）。

**像素规则、背景、交付**和上一轮一样：和设计图同样密度的方块（模板里每格 9 像素，和 `refs/style.png` 一样）、近黑描边、不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**；模板上的浅色人影、线、字全部不要留下。

- 交付：`outputs/blitzcrank-run1/run_1.png`（1536×1024，和模板一样一格）；原始生成图放进 `outputs/blitzcrank-run1/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/blitzcrank-run1/HANDOFF.md`，再打包成 `outputs/blitzcrank_run1_done.zip`。

## 附图（压缩包 `blitzcrank_run1_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、颜色 |
| `templates/run_1.png` | 一格的模板，浅色人影是身体和拳头的姿势 | **第二张**：身体、头、拳头的位置和大小 |
| `refs/old_run_1.png` | 旧版第 1 帧的彩色原图（放大） | **第三张**：四分之三侧身的朝向、拳头怎么摆（衣服和腿不照它） |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 blitzcrank-A） | **第五张**：细节 |
| `refs/style.png` | 你交的 `run_2`（第 2 帧） | **第六张**：**照它的朝向、大小和画法** |
| `sheets.json` | 这一帧的腿（`legs`）、手臂和拳头（`weapons`） | 填提示词 |

## 提示词（换掉 <...>）

附图顺序：`refs/design.png`、`templates/run_1.png`、`refs/old_run_1.png`、`refs/design_palette.png`、`refs/design_picture.png`、`refs/style.png`。

```text
Six attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a round golden steam golem - a BIG ROUND GOLDEN BODY with a SILVER GAUGE RING and a copper dial, a small golden head with TWO SQUARE PINK EYES, TWO STEEL-GREY CHIMNEYS, DARK GREY SHOULDER JOINTS, two MASSIVE GOLDEN ARMS with BIG SQUARE FISTS, short DARK PISTON LEGS and BIG GOLDEN FEET - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 6 is frame 2 of the same run, which you drew before: MATCH ITS VIEW, ITS SIZE AND ITS STYLE - 3/4 view facing right, the head right of the body's middle, the gauge ring right of the middle, the near shoulder and arm in front at the left, the far arm behind the body reaching forward to the right. Image 2 is a TEMPLATE of ONE frame of his RUN (frame 1): the PALE FIGURE is the pose of his body, head and fists, the grey line the ground, the tick his standing point, the grey bar his height (the tops of his chimneys to his soles). Image 3 is the same old frame in colour: copy its 3/4 view, body and fists - not the old costume, and NOT its legs. Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (or flat pure white, no glow, no shadow), the SAME cell layout as image 2: image 1's character in the pale figure's pose, at its place and size, the planted foot on the ground line. The scale set by the grey bar: as big as image 6, not bigger. Do not rescale, crop or re-lay it.
WHY IT IS DRAWN AGAIN: the last frame 1 faced the viewer (the head over the middle, the fists spread alike, the ring in the middle) and came out bigger, where the old frame and frames 2-8 are 3/4 to the right. Now 3/4 to the right exactly as image 6, as big as image 6; the near fist low at the left, the far arm reaching forward to the right as the pale figure.
THE LEGS: <LEGS> The NEAR leg is the one on the viewer's side, a step LIGHTER; the FAR leg a step DARKER, partly behind it and the body.
He is EXACTLY image 1 and image 6: the same round golden body, gauge ring and dial, small head with the two square pink eyes, chimneys, shoulder joints, arms, fists, piston legs and golden feet, image 4's colours only. THE HEAD THE SAME SIZE AS IN IMAGE 6 (about 12 squares from the top of his small golden head to its chin); the fists as big as in image 6.
NO EFFECTS: no steam, no sparks or lightning, no speed lines, no dust, no afterimages; the eyes' pink stays inside the eyes.
THE PIXEL GRID: squares the size of the template's (9 px) on one straight grid, as image 6; the near-black outline of image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<LEGS>` 照 `sheets.json` 里这张的 `legs` 填。

## 交回前请检查

- **四分之三侧身朝右**，和 `refs/style.png` 并排看是同一个朝向；**大小和它一样**（不能比它大）；近侧拳头在左下，远侧手臂往右前伸。
- 近侧（亮）腿踩在胯下、远侧（暗）腿往后踢起；头和拳头和第 2 帧一样大；只用设计图的颜色；没有特效；1536×1024、和模板一样一格、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/blitzcrank-run1/HANDOFF.md`，再打包成 `outputs/blitzcrank_run1_done.zip`。
