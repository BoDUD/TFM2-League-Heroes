# 泰隆：跑步重画（给 Codex 的提示词）

> 上一轮的动作都用上了，**只有跑步要重画**：上一轮的 8 帧**一直是同一条腿在前、同一条腿在后**，从头到尾没换过腿，放起来像滑着走（用户：「走路没有换腿」）。这次照模板里浅色人影的**腿**画：他旧版的跑步是**一条腿撑在胯下、另一条腿往后踢起**，再交错、迈步，**第 5 帧起换另一条腿**。
>
> 人物照旧全部照定稿设计图（`refs/design.png`）：蓝紫色大兜帽、银色 V 字护额和护颊、晒黑的脸；蓝紫围巾带青色条纹、叠层银护肩、银护臂；深蓝上衣、青金腰带；酒红长披风挂着银刀片，下端一把长银刀尖；深蓝裤子、深灰钢护膝护胫靴子。**近侧手上照浅色人影握着一把长银刀**。头的大小每帧和设计图一样（兜帽顶到下巴约 36 格）。不画任何特效。
>
> `sheets.json` 的模板（`templates/run_1.png` … `run_6.png`：第 1、2、5、6 张一格，第 3、4 张两格）每格写了**这一帧的腿**（`legs`）。**近侧腿**是靠近看画的人的那条（颜色亮），**远侧腿**是另一条（颜色暗一档，有一部分被近侧腿挡住）：
> 1. **近侧腿撑地**：近侧腿笔直踩在胯下，整只脚平踩地面；远侧腿弯着往后上方踢起，脚离地很高。
> 2. 近侧腿还踩在胯下、开始弯；远侧腿从后面往下摆，脚离地，在撑地那只脚的后面。
> 3. 交错：两条腿收在压低的身子下面、膝盖弯得很深；远侧腿贴着撑地的近侧腿往前过，脚刚离地。
> 4. 迈步：远侧腿往前（画面右边）伸出去准备落地，脚跟先着地；近侧腿在后面（画面左边）蹬地，脚尖点地。
> 5. **换腿——远侧腿撑地**：远侧腿笔直踩在胯下，整只脚平踩地面；**近侧腿**弯着往后上方踢起，脚离地很高。
> 6. 远侧腿还踩在胯下、开始弯；近侧腿从后面往下摆，脚离地，在撑地那只脚的后面。
> 7. 交错：两条腿收在身子下面；近侧腿贴着撑地的远侧腿往前过，脚刚离地。
> 8. 迈步：近侧腿往前（画面右边）伸出去准备落地；远侧腿在后面蹬地，脚尖点地。
>
> **两条腿轮流**：第 1–4 帧近侧（颜色亮的）腿撑地、远侧腿往前；第 5–8 帧换成远侧（颜色暗的）腿撑地、近侧腿往前。**第 1 帧和第 5 帧必须看得出是不同的腿撑地。**

**像素规则、背景、交付**和上一轮一样：和设计图同样大小的方块（模板里每格 8 像素）、近黑描边、只用调色板的颜色、不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**；模板上的浅色人影、线、字全部不要留下。

- 交付：`outputs/talon-run/run_1.png` … `run_6.png`（1536×1024，和模板一样的格子布局）；原始生成图放进 `outputs/talon-run/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/talon-run/HANDOFF.md`，再打包成 `outputs/talon_run_done.zip`。

## 附图（压缩包 `talon_run_pack.zip`）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、披风、刀、头的大小、颜色 |
| `templates/run_<k>.png` | 一格或两格模板，浅色人影是要摆的姿势 | **第二张**：**腿**、身体、手臂和刀的位置和大小 |
| `refs/old_run_<k>.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清两条腿怎么摆（衣服不照它） |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 talon-A） | **第五张**：细节（脸、护额、刀刃） |
| `sheets.json` | 每格是第几帧、腿怎么摆（`legs`）、刀和披风怎么放（`weapons`） | 填提示词 |

## 提示词（每张模板一次，换掉 <...>）

```text
Five attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a hooded assassin - a big BLUE-VIOLET HOOD with a SILVER V BROW GUARD and cheek guards, a tanned face under it; a blue-violet scarf with a teal stripe, a layered silver pauldron, silver vambraces, blue-violet gloves; a dark navy tunic with a teal and gold sash; a long RUST-RED CLOAK behind him hung with SILVER BLADE TIPS, its lower end ONE LONG SILVER SPEAR TIP; dark navy trousers, gunmetal knee guards, greaves and boots - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> frame(s) of his RUN (frame(s) <FRAMES>): in each cell the PALE FIGURE is the body pose to draw, the grey line the ground, the tick his standing point, the grey bar his height (top of the hood to soles). Image 3 is the same old frame(s) in colour: copy their LEGS, body, arms and blade - not the old costume. Image 4 is image 1's palette.
Create ONE 1536x1024 pixel-art sheet, genuine transparent background (or flat pure white), the SAME cell layout as image 2: in each cell image 1's character in that cell's pose, at its place and size, the planted foot on the ground line. One scale for the sheet, set by the grey bar. Do not rescale, crop or re-lay it.
THE LEGS - this is why the run is drawn again: <LEGS> The NEAR leg is the one on the viewer's side, a step LIGHTER; the FAR leg a step DARKER, partly behind it.
He is EXACTLY image 1: the same hood, brow guard, face, scarf, pauldron, vambraces, outfit, cloak and greaves, image 4's colours only. THE HEAD THE SAME SIZE AS IN IMAGE 1 (about 36 squares from the top of the hood to the chin). The body, arms and legs the same length and thickness as image 1 (bent, never stretched or shrunk).
<BLADE>
NO EFFECTS: no speed lines, no dust, no afterimages, no blade trails.
THE PIXEL GRID: squares the size of the template's (8 px) on one straight grid; the near-black outline of image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<N>`、`<FRAMES>`、`<LEGS>`、`<BLADE>` 照 `sheets.json` 每张的 `cells`、`frames`、`legs`、`weapons` 填。

## 交回前请检查

- **第 1–4 帧近侧（亮）腿撑地，第 5–8 帧远侧（暗）腿撑地**；第 1 帧和第 5 帧一眼看得出换了腿；每帧的腿照浅色人影（撑地、往后踢、交错、迈步），不是 8 帧同一个姿势。
- 头和设计图一样大；近侧手握长银刀；只用设计图颜色；没有特效；每张 1536×1024、和模板一样的格子布局、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/talon-run/HANDOFF.md`，再打包成 `outputs/talon_run_done.zip`。
