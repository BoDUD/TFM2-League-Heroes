# 布里茨：跑步重画（给 Codex 的提示词）

> 上一轮的动作都用上了，**只有跑步要重画**：上一轮 8 帧**每一帧都是前脚踩地、后脚往后翘起**，剪影一模一样，从头到尾没换过腿，放起来像一直单脚往前蹦（用户以前说过：「走路没有换腿」）。这次**腿照下面逐帧写的画**（不照浅色人影的腿——旧版 1 倍的腿太小，看不清）；**身体、头、烟囱和两只大拳头照浅色人影**。
>
> 人物照旧全部照定稿设计图（`refs/design.png`）：**金色的大圆身体**、**银色的仪表圈和铜色的表盘**；**金色小头上两只方形的粉色眼睛**；**两根钢灰色的烟囱**；**深灰色的肩关节**、**两条粗大的金色手臂和方块大拳头**；**深色的活塞短腿**、**金色的大脚**。头的大小每帧和设计图一样（金色小头从头顶到下巴约 12 格），拳头和设计图一样大。不画任何特效（不画蒸汽、电光）。
>
> `sheets.json` 的模板（`templates/run_1.png` … `run_8.png`，每张一格）每格写了**这一帧的腿**（`legs`）。**近侧腿**是靠近看画的人的那条（颜色亮），**远侧腿**是另一条（颜色暗一档，有一部分被近侧腿和身子挡住）：
> 1. **近侧腿撑地**：近侧活塞腿笔直踩在胯下，金色大脚平踩地面线；远侧腿弯着往后踢起，脚离地。
> 2. 近侧腿还踩在胯下、开始弯；远侧腿从后面往下摆，脚低低地离地，在撑地那只脚的后面。
> 3. 交错：两条短腿收在圆身子下面；远侧腿紧贴着撑地的近侧腿往前过，脚刚离地——**两只金色大脚并在一起**。
> 4. 迈步：远侧腿往前（画面右边）伸出去、脚准备落地；近侧腿在后面（画面左边）蹬地，脚尖点地——**两只脚前后分得很开**。
> 5. **换腿——远侧腿撑地**：远侧腿笔直踩在胯下，脚平踩地面线；**近侧腿**弯着往后踢起，脚离地。
> 6. 远侧腿还踩在胯下、开始弯；近侧腿从后面往下摆，脚低低地离地，在撑地那只脚的后面。
> 7. 交错：两条短腿收在身子下面；近侧腿紧贴着撑地的远侧腿往前过，脚刚离地——**两只脚并在一起**。
> 8. 迈步：近侧腿往前伸出去、脚准备落地；远侧腿在后面蹬地，脚尖点地——**两只脚前后分开**。
>
> **两条腿轮流**：第 1–4 帧近侧（亮）腿撑地、远侧腿往前；第 5–8 帧换成远侧（暗）腿撑地、近侧腿往前。**第 1 帧和第 5 帧必须看得出是不同的腿撑地；8 帧不能是同一个剪影**（第 3、7 帧两只脚并拢，第 4、8 帧两只脚分开）。两只大拳头照浅色人影前后摆，**拳头不是腿**。

**像素规则、背景、交付**和上一轮一样：和设计图同样密度的方块（模板里每格 9 像素）、近黑描边、只用调色板的颜色、不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**；模板上的浅色人影、线、字全部不要留下。

- 交付：`outputs/blitzcrank-run/run_1.png` … `run_8.png`（1536×1024，和模板一样的格子布局）；原始生成图放进 `outputs/blitzcrank-run/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/blitzcrank-run/HANDOFF.md`，再打包成 `outputs/blitzcrank_run_done.zip`。

## 附图（压缩包 `blitzcrank_run_pack.zip`，解压到一个新文件夹，只用里面的图）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、拳头和头的大小、颜色 |
| `templates/run_<k>.png` | 一格的模板，浅色人影是身体的姿势 | **第二张**：身体、头、烟囱、拳头的位置和大小 |
| `refs/old_run_<k>.png` | 旧版同一帧的彩色原图（放大） | **第三张**：身体和拳头怎么摆（衣服和腿不照它） |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 blitzcrank-A） | **第五张**：细节 |
| `sheets.json` | 每张是第几帧、腿怎么摆（`legs`）、手臂和拳头怎么放（`weapons`） | 填提示词 |

## 提示词（每张模板一次，换掉 <...>）

附图顺序：`refs/design.png`、`templates/run_<k>.png`、`refs/old_run_<k>.png`、`refs/design_palette.png`、`refs/design_picture.png`。

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a round golden steam golem - a BIG ROUND GOLDEN BODY with a SILVER GAUGE RING and a copper dial, a small golden head with TWO SQUARE PINK EYES, TWO STEEL-GREY CHIMNEYS, DARK GREY SHOULDER JOINTS, two MASSIVE GOLDEN ARMS with BIG SQUARE FISTS, short DARK PISTON LEGS and BIG GOLDEN FEET - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of ONE frame of his RUN (frame <FRAMES>): the PALE FIGURE is the pose of his body, head and fists, the grey line the ground, the tick his standing point, the grey bar his height (the tops of his chimneys to his soles). Image 3 is the same old frame in colour: copy its body, head and fists - not the old costume, and NOT its legs (draw the legs as written below). Image 4 is image 1's palette: use only these colours.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (or flat pure white, no glow, no shadow), the SAME cell layout as image 2: image 1's character in the pale figure's pose, at its place and size, the planted foot on the ground line. One scale for the sheet, set by the grey bar. Do not rescale, crop or re-lay it.
THE LEGS - this is why the run is drawn again: <LEGS> The NEAR leg is the one on the viewer's side, a step LIGHTER; the FAR leg a step DARKER, partly behind it and the body.
He is EXACTLY image 1: the same round golden body, gauge ring and dial, small head with the two square pink eyes, chimneys, shoulder joints, arms, fists, piston legs and golden feet, image 4's colours only. THE HEAD THE SAME SIZE AS IN IMAGE 1 (about 12 squares from the top of his small golden head to its chin). The body, arms and legs the same length and thickness as image 1 (bent, never stretched or shrunk); the fists as big as in image 1.
NO EFFECTS: no steam, no sparks or lightning, no speed lines, no dust, no afterimages; the eyes' pink stays inside the eyes.
THE PIXEL GRID: squares the size of the template's (9 px) on one straight grid; the near-black outline of image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<FRAMES>`、`<LEGS>` 照 `sheets.json` 每张的 `frames`、`legs` 填。

## 交回前请检查

- **第 1–4 帧近侧（亮）腿撑地，第 5–8 帧远侧（暗）腿撑地**；第 1 帧和第 5 帧一眼看得出换了腿；第 3、7 帧两只脚并在一起，第 4、8 帧两只脚前后分开——**8 帧不是同一个剪影**。
- 身体、头、烟囱、拳头照浅色人影；拳头和头都和设计图一样大；只用设计图的颜色；没有特效；每张 1536×1024、和模板一样的格子布局、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/blitzcrank-run/HANDOFF.md`，再打包成 `outputs/blitzcrank_run_done.zip`。
