# 巨型纳尔的跑步重画：给 Codex 的提示词（8 帧，2 张图）

> 用户 2026-11-22：「纳尔变大后没有动画效果」「像一张图在平移」「纳尔变大后右上腿不动了？」「不然你让codex帮忙 这个大纳尔」。
>
> - 现在游戏里巨型纳尔的跑步（附图 2）四条腿几乎不动，身体也不起伏，看上去像一张图在地上滑。**这次重画他的跑步 8 帧。**
> - **角色照附图 1 的定稿设计**（侧面朝右）：头、獠牙、骨头面具、背上和尾巴上的蓝色晶刺、红色毛、紫色爪子，颜色、大小、比例
>   都不能改，**不能变形**（头、晶刺、獠牙每帧都是同一个形状，只是跟着身子动）。
> - **模板（`templates/run_1.png`、`run_2.png`）**：每格一帧，浅灰的影子是 Claude 先摆的姿势，管的是**位置、大小、每帧在
>   步子的哪个阶段**；你按定稿设计画在影子上，**腿的摆动要比影子大得多**（影子的腿太小，就是现在的毛病）。
> - 附图 3 是影子的连续动作（看身体怎么前后摇）；附图 4 是迷你纳尔已经通过的跑步（同一个英雄的画风）。
> - 只画这 8 帧，别的动作、特效都不画。
> - 交回时附 `HANDOFF.md`：用了哪条提示词、每帧有没有没做到的地方。

## 动作：撑着拳头往前蹦的奔跑（英雄联盟 GnarBig_Run 的样子），8 帧循环，每帧 100 毫秒

他是一只用两只前拳着地、像大猩猩一样蹦着跑的巨兽。一个循环：

| 帧 | 这一帧 |
|---|---|
| 1 | **两只拳头往前落地**，身子往前压在拳头上，头低；后腿在身后蹬直 |
| 2 | 身子从拳头上方压过去，拳头开始往后推；**后腿离地往前收** |
| 3 | 后腿收到肚子底下；拳头推到身子下面偏后 |
| 4 | **后爪落地**；拳头离地 |
| 5 | 后腿蹬地，**前半身抬起**，拳头往前伸 |
| 6 | 身子最高、几乎腾空，**拳头伸到最前**，后腿在后面蹬直 |
| 7 | 拳头往下落，前半身往下压 |
| 8 | 拳头快着地（接回第 1 帧） |

- **四条腿都要动**：近侧（画面前面、颜色亮的）的拳头和后腿动作最大；**远侧（被头和身子挡住一半的）的拳头和后腿也要动**，比近侧晚
  一帧、幅度小一点。远侧前拳在头下面，**每帧位置都要不一样**。
- 拳头往前伸时至少伸出影子 **6–8 格**，往后推时推到身子下面；后腿往前收到肚子底下、往后蹬直，摆动至少 **6 格**。
- 身子跟着步子前后摇（落拳时头低、抬身时头高）、整体上下起伏 2–4 格；尾巴跟着身子甩。
- **着地的拳和爪贴着地面线**（模板里深灰横线），不要沉到线下面，也不要飘着（腾空的第 6 帧除外）。

## 画法规矩

- **一格 8 像素**：模板的影子就画在这张 8 像素的网格上，你画的每个方块也是 8×8，对齐同一张网格。像素画：方块清楚、硬边、
  没有抗锯齿、没有模糊和柔光。
- **颜色只用附图 1 里有的颜色**；外轮廓是设计里那圈近黑的描边。
- **大小照影子**：身子长度（尾尖到鼻尖）、头的大小和影子一样；十字是格子的中心，**不要挪**（游戏里他站的点就是这里）。
- **背景真透明**（每个像素透明度只有 0 或 255；做不到就纯白 `#FFFFFF` 背景）。不要画网格线、格子边框、编号、地面线、影子。
- 不要自己缩放或裁剪：交付的图和模板一样大（每张 2048×1920，2×2 格，每格 1024×960）。

## 提示词

```text
Pixel-art game sprite animation, 8 frames, for a small tactics game. Image 1 is THE character: Mega Gnar, a huge red-furred
beast seen from the side facing RIGHT - a big head with a bone mask, ivory tusks and an angry eye, blue crystal spikes along
his back and tail, a thick red mane, purple claws on his two front fists and two hind paws. Keep his design EXACTLY: the same
head, tusks, mask, crystals, colours and proportions in every frame - nothing stretched or deformed.
Draw his RUN: a powerful bounding gallop on his front fists like a gorilla (League of Legends' GnarBig_Run). Frame 1: both
fists land far ahead, the body pitched down over them, the hind legs stretched back. 2: the body passes over the fists, the
hind legs leave the ground and swing forward. 3: the hind legs gathered under the belly, the fists pushing back. 4: the hind
paws land, the fists lift off. 5: the hind legs push, the front of the body rises, the fists reach forward. 6: the body
highest, nearly airborne, the fists reaching farthest forward, the hind legs stretched back. 7: the fists coming down, the
front pitching down. 8: the fists about to land (loops back to frame 1). All four limbs move clearly - the near (front,
brighter) fist and hind leg swing the most; the far (behind, half hidden by the head and body) fist and hind leg move too,
one frame later and a bit less. The body rocks with each bound and bobs 2-4 squares; the tail swings with it. Planted fists
and paws stay on the ground line.
The two attached templates (images 5 and 6): each cell is one frame; the light grey ghost is a placement guide giving his
SIZE, where he stands and which phase of the stride the frame is - draw him over it at the same size and place, but with
much bigger leg swings than the ghost (fists reaching 6-8 squares beyond it, hind legs swinging at least 6 squares). The
small cross is the cell centre (his standing point - keep it); the dark grey line is the ground.
THE PIXEL GRID: every square exactly 8x8 px on the template's grid, hard edges, no anti-aliasing, no blur, no glow; the
near-black outline of image 1 around him; only the colours of image 1.
Output: two images exactly like the templates, 2048x1920 each, 2x2 cells of 1024x960 (run_1 = frames 1-4, run_2 = frames
5-8, left to right, top to bottom). Transparent background (every pixel fully transparent or fully opaque; if impossible
pure white #FFFFFF). No ghost, no grid lines, no borders, no numbers, no ground line, no shadow.
```

## 附图（在压缩包 `gnar_mega_run_pack.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_mega_design_side_8x.png` | 巨型纳尔定稿设计（侧面，8 倍） | **要画的就是他**：造型、颜色、比例 |
| `refs/2_mega_run_in_game_now_DONT_COPY.png` | 现在游戏里的跑步（3 倍） | 毛病：腿几乎不动、身子不起伏，**不要照它** |
| `refs/3_pose_timing_guide.png` | 模板影子的 8 帧连起来（3 倍） | 只看身体怎么前后摇、四条腿的先后，腿要比它摆得大 |
| `refs/4_mini_run_style.png` | 迷你纳尔已经通过的跑步（4 倍） | 同一个英雄的画风 |
| `templates/run_1.png` | 第 1–4 帧的模板（2048×1920） | 位置、大小、十字、地面线 |
| `templates/run_2.png` | 第 5–8 帧的模板（2048×1920） | 同上 |

## 交回前请检查

- 两张图都是 2048×1920、2×2 格、和模板一样的排法；真透明背景（或纯白）；没有缩放、裁剪；没有影子、网格、边框、编号、地面线。
- 一格 8 像素、对齐模板的网格；硬边、没有抗锯齿和柔光；只用附图 1 的颜色，外面一圈近黑描边。
- 他和附图 1 一模一样（头、獠牙、面具、晶刺、颜色、比例），每帧大小和影子一样，十字没挪；**没有变形**。
- 8 帧连起来是撑着拳头往前蹦的奔跑：**四条腿都在动**（远侧的拳头和后腿也在动，晚一帧），拳头伸到影子前面 6–8 格，
  后腿收到肚子底下再蹬直；身子前后摇、上下起伏；着地的拳和爪贴着地面线。
- 交付放 `outputs/gnar-mega-run/`：`run_1.png`、`run_2.png`，原始生成图放 `raw/`，`generation-prompts.txt`，最后写
  `HANDOFF.md`，打包成 `outputs/gnar_mega_run_done.zip`。

## Claude 收到后（给 Claude 看）

- 按 8 像素一格读回（像 `read_singed_run.py`：找最合适的网格偏移，每格取多数颜色和透明度，归到设计的颜色），得到设计密度（PPU 1.5）
  的 8 帧；头和面具每帧照设计贴准（防抖），数两只前拳、两条后腿都在；着地的拳爪贴地面（格子中心往下 17 格）。
- 当成 `assets/source/ppu/orig/gnar_m_run.png` 的新原稿，照 `D:/TFM2-Workshop/kept/gnar_run_1122` 的拼法：1x `m_run` 拼进整张图、
  `restyle_one.py m_run`、`hd_one.py m_run --write`，`cmp_tags.py` 只有 m_run / hd_m_run / lo_m_run 变；8 × 100 ms。
- 「改前 | 新」的逐像素 GIF（`C:/t/za_work/exact/exact_gif.py`）给用户看，用户点头才装。
