# 李青（盲僧）：跑步重画 + E 最后一帧（给 Codex 的提示词）

> 上一轮的动作整体很好，只有两处要重画：
>
> 1. **跑步 8 帧**：上一轮每一帧都是同一条腿在前（近侧的腿一直在后面），旧版第 2–3、6–7 帧那种**两条腿在胯下交错而过**的帧也画成了大跨步。循环播放时看起来像一条腿瘸着跳。这次**腿照 `legs/run_<帧>.png` 画**：英雄联盟里同一帧的腿，**洋红 = 他的近侧腿（离我们近、画在前面的那条）**，**青色 = 远侧腿**——每一帧哪条腿在前、哪条在后、哪条着地、哪条抬起、两条腿在哪交错，都照它；8 帧连起来两条腿轮流在前。身体、手臂、头的姿势和位置照浅色人影（旧版同一帧）和你上一轮的画。
> 2. **E（天雷破）第 7 帧**（`skill2_4`）：旧版最后一帧是**站回架势**（和待机一样的站姿），上一轮画成了蹲着双手撑地。这次照浅色人影画**站起来的架势**。
>
> **身上、手臂、头、辫子、布条都照上一轮你自己画的样子**（`prev/<同名>.png`：颜色、大小、细节都保持），只是腿（和 E 第 7 帧的整个姿势）照这次的说明画。**头的大小和设计图一样**（头顶到下巴约 17 格，辫子再高约 12 格），每帧同一个比例。
>
> 不画特效、地面、影子、文字。背景真透明；做不到就**纯白平涂**，人物外面不要光晕。
>
> 交付：`outputs/leesin-run-redo/<模板同名>.png`（run_1–run_4、skill2_4，1536×1024，和模板一样的格子布局）；原始生成图放进 `raw/`；附 `generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/leesin_run_redo_done.zip`。

## 附图（压缩包 `leesin_run_redo_pack.zip`）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/design.png` | 定稿设计图（6 倍） | 第一张：人物、比例、头的大小、颜色 |
| `templates/<名>.png` | 模板：浅色人影是这一帧要摆的姿势 | 第二张：姿势、位置、大小 |
| `prev/<名>.png` | 你上一轮画的同一张 | 第三张：**保持这个样子**（身体、头、布条），只改腿 |
| `legs/run_<帧>.png` | 英雄联盟同一帧的腿：洋红 = 近侧腿，青色 = 远侧腿 | 第四张（跑步）：哪条腿在前、哪条腿在后、在哪交错 |
| `refs/old_<名>.png` | 旧版同样几帧的彩色原图 | 对照身体动作 |
| `refs/design_palette.png` | 设计图的全部颜色 | 只用这些颜色 |

## 提示词（跑步每张一次：run_1 是第 1、2 帧，run_2 是 3、4，run_3 是 5、6，run_4 是 7、8）

附图顺序：`refs/design.png`、`templates/run_<n>.png`、`prev/run_<n>.png`、该张两帧的 `legs/run_<帧>.png`、`refs/design_palette.png`。

```text
Attached: image 1 the approved pixel-art character (6x); image 2 a TEMPLATE of two frames of his run (frames <A> and <B>): in each cell the pale figure is the pose, the grey line the ground, the tick his standing point; image 3 YOUR OWN previous drawing of this sheet - keep exactly its look, size, colours, head, braid, blindfold, arms and upper body; images 4-5 the same two frames of the run from the game, LEGS ONLY: the MAGENTA leg is his NEAR leg (closer to us, drawn in front), the CYAN leg his FAR leg; image 6 the palette.
Redraw image 3 with the LEGS fixed: in each cell draw his two legs exactly as the coloured legs of that frame in images 4-5 - the near leg where the MAGENTA leg is, the far leg where the CYAN leg is: which one is in front, which behind, which foot is on the ground, which is lifted, where they cross. The near leg is drawn over the far leg where they overlap. The two legs keep the same trousers, red-and-white shin wraps and shoes as image 1, the same length and thickness. Everything else as image 3. The head the size of image 1 (about 17 squares from the top of the shaved head to the chin) in both frames.
One 1536x1024 sheet, the same two-cell layout as image 2; transparent background (or flat pure white), no glow, no shadow, no ground, no text, no template marks. Pixel art on one even square grid, the near-black outline of image 1, only image 6's colours.
```

`<A>`、`<B>` 填这张的两帧（run_1 是 1、2，run_2 是 3、4，run_3 是 5、6，run_4 是 7、8）。

## 提示词（`skill2_4`，E 第 7 帧，一格）

附图顺序：`refs/design.png`、`templates/skill2_4.png`、`prev/skill2_4.png`、`refs/old_skill2_4.png`、`refs/design_palette.png`。

```text
Attached: image 1 the approved pixel-art character (6x); image 2 a TEMPLATE of the last frame of his ground-slam: the pale figure is the pose - he has STOOD BACK UP in his fighting guard, legs apart and slightly bent, the far palm forward, the near fist back, as image 1 stands; image 3 your own previous drawing of this frame (a deep crouch - wrong pose, but keep its look, size and colours); image 4 the old frame in colour; image 5 the palette.
Draw him standing back up in his guard exactly as the pale figure, the look and size of image 3, the head the size of image 1 (about 17 squares from the top of the shaved head to the chin). One 1536x1024 sheet, one cell as image 2; transparent background (or flat pure white), no glow, no shadow, no ground, no text, no template marks. Pixel art on one even square grid, the near-black outline of image 1, only image 5's colours.
```

## 交回前请检查

- 跑步：每一帧的近侧腿、远侧腿和 `legs/run_<帧>.png` 的洋红、青色一样；连起来看两条腿轮流在前，不是同一条腿一直在前。
- 身体、头、辫子、布条和上一轮一样；头的大小和设计图一样；腿的裤子、绑腿、鞋和设计图一样。
- E 第 7 帧是站起来的架势，不是蹲着。
- 最后写 `HANDOFF.md`，再打包成 `outputs/leesin_run_redo_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/leesin/hd/casts/`（换掉 run_1–4、skill2_4），`casts_leesin_hd.py --measure` 重算这几张的缩放，再看头的叠加图、跑步左右脚的前后（每帧近侧脚 - 远侧脚的 x 一个循环里换两次号）。
