# 阿卡丽：跑步重画（给 Codex 的提示词）

> 上一轮的动作都用上了，**只有跑步要重画**：上一轮的 8 帧两条腿一直是大大分开、后脚抬起的同一个样子，**没有一帧是腿从身体下面换过去的**，放起来像原地蹦，不像跑。这次照模板里浅色人影的**腿**画：她旧版的跑步只有第 1、4、6 帧两腿分开，其余几帧都是**一只脚踩在胯下、另一条腿弯着从身体下面带过来**。
>
> 人物照旧全部照定稿设计图（`refs/design.png`）：深蓝刺头、甩向左上的高马尾和黄绿发带、橙色眼睛、黄绿面罩、青绿短上衣、手臂上的淡紫色纹身、橙色腰绳、暗红腰包、青绿前摆、深蓝灯笼裤、黄绿裤脚带；**弯钩镰刀在近侧的手（画面左边），长直刀在远侧的手（画面右边）**，手臂照浅色人影。头的大小每帧和设计图一样（头顶到面罩下沿约 21 格）。不画任何特效。
>
> `sheets.json` 的四张模板（`templates/run_1.png` … `run_4.png`，每张两格）每格写了**这一帧的腿**（`legs`）：
> 1. 大步：两脚都着地、分得很开——后脚在后（画面左），前脚在前（画面右）。
> 2. 换步：后脚蹬地后踩到了胯下；另一条腿的膝盖往前上方摆，脚离地、在肚子下面。
> 3. 换步：一只脚踩在胯下；另一条腿膝盖抬高在前，脚收在下面。
> 4. 腾空：后腿往后伸直、脚抬离地面到膝盖高；前脚往前伸、准备落地。
> 5. **换另一条腿**：刚落地的脚踩到胯下；原来在后面的腿弯着从身体下面带过来，膝盖往前、脚离地。
> 6. **另一条腿**腾空：这次换另一条腿往后伸直抬起，另一只脚往前伸、准备落地。
> 7. 换步：一只脚踩在胯下，另一条腿膝盖抬在前面。
> 8. 换步：两条腿收在身体下面，一只脚踩在胯下，另一只脚收起来在旁边。
>
> **两条腿轮流**：第 1–4 帧近侧（颜色亮的）那条腿最后到前面，第 5–8 帧换成远侧（颜色暗的）那条腿。

**像素规则、背景、交付**和上一轮一样：和设计图同样大小的方块（模板里每格 8 像素）、近黑描边、只用调色板的颜色、不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**；模板上的浅色人影、线、字全部不要留下。

- 交付：`outputs/akali-run/run_1.png` … `run_4.png`（1536×1024，和模板一样的格子布局）；原始生成图放进 `outputs/akali-run/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/akali-run/HANDOFF.md`，再打包成 `outputs/akali_run_done.zip`。

## 附图（压缩包 `akali_run_pack.zip`）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、衣服、武器、头的大小、颜色 |
| `templates/run_<k>.png` | 两格模板，浅色人影是要摆的姿势 | **第二张**：**腿**、身体、手臂的位置和大小 |
| `refs/old_run_<k>.png` | 旧版同两帧的彩色原图（放大） | **第三张**：看清两条腿怎么摆（衣服和武器不照它） |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `sheets.json` | 每格是第几帧、腿怎么摆（`legs`）、手怎么摆（`weapons`） | 填提示词 |

## 提示词（每张模板一次，换掉 <...>）

```text
Four attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a ninja girl - spiky dark blue hair and a thick high ponytail swept up to the upper left tied with lime-yellow ribbons; an orange eye; a lime-yellow face mask; a teal crop top, a bare midriff, bare arms with pale violet tattoos, lime wrist wraps; an orange rope belt, a dark red pouch on her near hip, a teal front panel; baggy dark blue trousers with lime ankle wraps; a HOOKED silver kama in her NEAR hand (image left), a long STRAIGHT silver blade in her FAR hand (image right) - 3/4 view facing right. Image 2 is a TEMPLATE of 2 frames of her RUN (frames <FRAMES>): in each cell the PALE FIGURE is the body pose to draw, the grey line the ground, the tick her standing point, the grey bar her height (top of the ponytail to soles). Image 3 is the same old frames in colour: copy their LEGS, body and arms - not the old costume or weapons. Image 4 is image 1's palette.
Create ONE 1536x1024 pixel-art sheet, genuine transparent background (or flat pure white), the SAME two-cell layout as image 2: in each cell image 1's character in that cell's pose, at its place and size, the planted foot on the ground line. One scale for the sheet, set by the grey bar. Do not rescale, crop or re-lay it.
THE LEGS - this is why the run is drawn again: <LEGS> Never both legs stretched apart in every frame: a run passes one leg under the body.
She is EXACTLY image 1: the same hair, ponytail, ribbons, eye, mask, clothes, tattoos and weapons, image 4's colours only. THE HEAD THE SAME SIZE AS IN IMAGE 1 (about 21 squares from the top of the head to the bottom of the mask). The body, arms and legs the same length and thickness as image 1 (bent, never stretched or shrunk).
THE HANDS: <HANDS>
NO EFFECTS: no speed lines, no dust, no afterimages.
THE PIXEL GRID: squares the size of the template's (8 px) on one straight grid; the near-black outline of image 1; 3-4 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<FRAMES>`、`<LEGS>`、`<HANDS>` 照 `sheets.json` 每张的 `frames`、`legs`、`weapons` 填。

## 交回前请检查

- 8 帧里**只有第 1、4、6 帧两腿分开**，其余都是一只脚踩在胯下、另一条腿从下面带过来；第 1–4 帧和第 5–8 帧换了一条腿在前。
- 头和设计图一样大；弯钩在近侧手、直刀在远侧手；只用设计图颜色；没有特效；每张 1536×1024、两格布局、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/akali-run/HANDOFF.md`，再打包成 `outputs/akali_run_done.zip`。
