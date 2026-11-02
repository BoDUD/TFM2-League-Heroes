# 赛娜：跑步和 Q 前两帧重画（给 Codex 的提示词）

> 上一轮的普攻、W、R、受击、死亡和 Q 的第 3–6 帧都用上了，**要重画的是跑步（4 张）和 Q 的第 1–2 帧（`skill_1`，1 张）**。
>
> **跑步**有两个问题：
> 1. **没有换腿**：8 帧一直是同一条腿撑地、同一条腿往后踢，第 1 帧和第 5 帧几乎一样，放起来像滑着走（泰隆当初也是这样，用户：「走路没有换腿」）。
> 2. **大小不一致**：`run_1`（第 1–2 帧）的头画得特别大、身体短；`run_2`、`run_4`（第 3–4、7–8 帧）的头又画小了、身体长。8 帧连起来播，头和身子一会儿大一会儿小。
>
> 这次照模板里浅色人影的**腿**画，每帧的腿写在 `sheets.json` 的 `legs` 里。**近侧腿**是靠近看画的人的那条（颜色亮），**远侧腿**是另一条（颜色暗一档，有一部分被近侧腿挡住）：
> 1. **近侧腿撑地**：近侧腿笔直踩在胯下，整只脚平踩地面；远侧腿弯着往后上方踢起，脚离地很高。
> 2. 近侧腿还踩在胯下、开始弯；远侧腿从后面往下摆，脚离地，在撑地那只脚的后面。
> 3. 交错：两条腿收在身子下面、膝盖弯着；远侧腿贴着撑地的近侧腿往前过，脚刚离地。
> 4. 迈步：远侧腿往前（画面右边）伸出去准备落地，脚跟先着地；近侧腿在后面（画面左边）蹬地，脚尖点地。
> 5. **换腿——远侧腿撑地**：远侧腿笔直踩在胯下，整只脚平踩地面；**近侧腿**弯着往后上方踢起，脚离地很高。
> 6. 远侧腿还踩在胯下、开始弯；近侧腿从后面往下摆，脚离地，在撑地那只脚的后面。
> 7. 交错：两条腿收在身子下面；近侧腿贴着撑地的远侧腿往前过，脚刚离地。
> 8. 迈步：近侧腿往前（画面右边）伸出去准备落地；远侧腿在后面蹬地，脚尖点地。
>
> **两条腿轮流**：第 1–4 帧近侧（颜色亮的）腿撑地、远侧腿往前；第 5–8 帧换成远侧（颜色暗的）腿撑地、近侧腿往前。**第 1 帧和第 5 帧必须看得出是不同的腿撑地。**
>
> **大小**：8 帧的头一样大、身子一样高，**和你上一轮画的普攻第 3 帧一样的头身比例**（附图 6 `refs/proportion_attack_3.png`）：兜帽顶到下巴约 **24 格**，身体、手臂和腿的长度粗细和设计图一样。整张按灰色竖条定大小，每帧同一个比例。
>
> **Q 第 1–2 帧（`skill_1`）**：上一轮把炮画成了端平朝前，可旧版这两帧是**蹲下蓄力、炮压低、炮口（水晶刃那头）朝后下方（画面左下）**，第 3 帧炮往下一摆、第 4–6 帧再端平开火。照浅色人影和 `refs/old_skill_1.png` 画：**压低身子、两腿弯，炮斜着压在身侧、炮口朝左下**，不要端平朝前。头和身子的大小同样照附图 6。
>
> 人物照旧全部照定稿设计图（`refs/design.png`）：金边白兜帽、深紫发辫、深棕皮肤、青绿眼睛、红唇；深紫紧身衣和金饰件、金边白长饰带；浅钢蓝靴子和金护片。**遗物炮照浅色人影斜端在身前**：每帧一门、完整、笔直、和设计图一样大。不画任何特效（速度线、尘土、残影都不要）。

**像素规则、背景、交付**和上一轮一样：和设计图同样大小的方块（模板里每格 8 像素）、近黑描边、只用调色板的颜色、不要渐变模糊；真透明或纯白 #FFFFFF 背景；**不要缩放、裁剪或重新排版**；模板上的浅色人影、线、字全部不要留下。

- 交付：`outputs/senna-run/run_1.png` … `run_4.png` 和 `skill_1.png`（1536×1024，和模板一样的格子布局）；原始生成图放进 `outputs/senna-run/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/senna-run/HANDOFF.md`，再打包成 `outputs/senna_run_done.zip`。

## 附图（压缩包 `senna_run_pack.zip`）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | **第一张**：人物、兜帽、炮、头的大小、颜色 |
| `templates/run_<k>.png`、`templates/skill_1.png` | 两格模板，浅色人影是要摆的姿势 | **第二张**：**腿**、身体、手臂和炮的位置和大小 |
| `refs/old_run_<k>.png`、`refs/old_skill_1.png` | 旧版同样几帧的彩色原图（放大） | **第三张**：看清两条腿和炮怎么摆（衣服不照它） |
| `refs/design_palette.png` | 设计图的全部颜色 | **第四张**：只用这些颜色 |
| `refs/design_picture.png` | 设计图读回前的原图（你画的 senna-A） | **第五张**：细节（脸、兜帽、金饰） |
| `refs/proportion_attack_3.png` | 你上一轮画的普攻第 3 帧 | **第六张**：头身比例和大小照它 |
| `sheets.json` | 每格是哪个动作的第几帧（`action`）、腿怎么摆（`legs`，跑步）、炮怎么放（`weapons`） | 填提示词 |

## 提示词（每张模板一次，换掉 <...>）

```text
Six attached images. Image 1 is the APPROVED pixel-art character (6x: every square one pixel): a woman in a WHITE HOOD with GOLD TRIM over dark violet locs, DARK BROWN SKIN, softly GLOWING TEAL EYES and red lips; a dark violet bodysuit with small gold fittings, a long WHITE SASH with gold trim down her front to her knees; pale steel-blue boots with gold plates; a HUGE RELIC CANNON - a gold claw grip, a gold ring with a dark round eye, a pale ice-blue crystal blade, a wine-red wing panel with gold ribs - 3/4 view facing right. Image 5 is the original picture image 1 was read from: its fine detail. Image 2 is a TEMPLATE of <N> frame(s) of her <ACTION> (frame(s) <FRAMES>): in each cell the PALE FIGURE is the body pose to draw, the grey line the ground, the tick her standing point, the grey bar her height (the top of the cannon's claw to her soles). Image 3 is the same old frame(s) in colour: copy their LEGS, body, arms and cannon - not the old costume. Image 4 is image 1's palette. Image 6 is one of her finished action frames: draw her head and body at exactly ITS size and proportions.
Create ONE 1536x1024 pixel-art sheet, genuine transparent background (or flat pure white), the SAME cell layout as image 2: in each cell image 1's character in that cell's pose, at its place and size, the planted foot on the ground line. One scale for the sheet, set by the grey bar. Do not rescale, crop or re-lay it.
THE LEGS (run sheets only) - this is why the run is drawn again: <LEGS> The NEAR leg is the one on the viewer's side, a step LIGHTER; the FAR leg a step DARKER, partly behind it.
THE SIZE - the other reason: the head and the body the SAME size in every frame and in both cells, as in image 6 (about 24 squares from the top of the hood to the chin); never a bigger head on a shorter body, never a smaller head on a longer body.
She is EXACTLY image 1: the same hood, locs, face, bodysuit, sash, boots and cannon, image 4's colours only. The body, arms and legs the same length and thickness as image 1 (bent, never stretched or shrunk).
<CANNON>
NO EFFECTS: no speed lines, no dust, no afterimages, no beam, no glow.
THE PIXEL GRID: squares the size of the template's (8 px) on one straight grid; the near-black outline of image 1; 3-5 flat shades per material; no dithering, gradients, blur or anti-aliasing. No ground, no shadow, no text, no template marks.
```

`<N>`、`<ACTION>`、`<FRAMES>`、`<LEGS>`、`<CANNON>` 照 `sheets.json` 每张的 `cells`、`action`、`frames`、`legs`、`weapons` 填（`skill_1` 删掉 `THE LEGS` 那一行，并在 `<CANNON>` 后加一句：`Frames 1-2 of Piercing Darkness: crouched low, gathering, the cannon held DOWN at her side, its muzzle (the crystal blade end) pointing to the image's LOWER LEFT, as the pale figure - NOT levelled forward.`）。

## 交回前请检查

- **第 1–4 帧近侧（亮）腿撑地，第 5–8 帧远侧（暗）腿撑地**；第 1 帧和第 5 帧一眼看得出换了腿；每帧的腿照浅色人影（撑地、往后踢、交错、迈步），不是 8 帧同一个姿势。
- **Q 第 1–2 帧蹲着、炮压低、炮口朝左下**，不是端平朝前。
- **8 帧的头一样大、身子一样高**，和附图 6 的比例一样；遗物炮每帧一门、完整、笔直；只用设计图颜色；没有特效；每张 1536×1024、和模板一样的格子布局、没有模板痕迹、没有缩放裁剪。
- 最后写 `outputs/senna-run/HANDOFF.md`（列出交付的 5 张），再打包成 `outputs/senna_run_done.zip`。
