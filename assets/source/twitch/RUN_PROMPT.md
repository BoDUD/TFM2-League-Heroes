# 图奇的跑步重画：给 Codex 的提示词（8 帧，2 张图）

> 用户 2026-11-22：「老鼠的跑步姿势有点怪 让codex帮忙重做一下」。
>
> - 现在游戏里的跑步（附图 4）：头、背包、弩八帧钉在一个地方，弩一直平端不动；两条腿在斗篷下面只挪小碎步、
>   脚尖吊着点地；第 7 帧整个人往上窜一截。**这次重画他的跑步 8 帧。**
> - **角色照附图 1 的定稿设计**（侧面偏四分之三，朝右）：大耳朵、金色护目镜、咧着嘴的尖牙、背上的背包和绿色药瓶、
>   深青色的破斗篷、带环纹的长尾巴、金色的大弩和弩上的绿色药罐。附图 2 是同一个他的大图（设计图就是从它读出来的），
>   细节看它。颜色、大小、比例都不能改，**不能变形**（头、护目镜、弩每帧都是同一个形状，只是跟着身子动）。
> - **动作照英雄联盟图奇的跑步**（附图 3：联盟的模型在我们这个镜头下的同 8 帧，左上是第 1 帧）。**第 k 帧就照附图 3 的
>   第 k 格**：压低身子往前蹿，两步一圈，两条腿大步交替，远侧那只手往后甩，尾巴和斗篷在身后甩，身子一高一低。
> - 联盟的模型和我们的设计比例不一样（联盟的耳朵更高；我们的头更靠前、弩更长、尾巴和斗篷更长）：**只学它的动作，
>   造型照我们的设计。**
> - **模板（`templates/run_1.png`、`run_2.png`）**：每格一帧。浅灰的影子**只有头和弩**（连握弩的手和弩上的药罐），
>   管的是大小和这一帧头、弩在哪；身子、背包、斗篷、两条腿、远侧的手和尾巴照附图 3 同一帧画上去，接到头和弩上。
> - 只画这 8 帧，别的动作、特效都不画。
> - 交回时附 `HANDOFF.md`：用了哪条提示词、每帧有没有没做到的地方。

## 动作：压低身子往前蹿（英雄联盟 twitch_base_run），8 帧循环，每帧 100 毫秒

| 帧 | 这一帧（对照附图 3 同一帧） |
|---|---|
| 1 | 身子在高处往前探：前面那条腿往前下方伸、快落地，后面那条腿在身后弯着；远侧的手往后甩 |
| 2 | **前脚踩地**，腿伸直撑住身子（身子最高）；后腿离地往前收；尾巴往上翘 |
| 3 | 身子往下压、往前送：踩地的腿弯下去，另一条腿从身子底下往前迈 |
| 4 | 身子最低，两条腿都收在身子底下，**换腿** |
| 5–8 | 和 1–4 一样，换另一条腿在前 |

- **两条腿都要动**，每条腿前后摆至少 **8–10 格**（现在只有两三格，就是毛病）：近侧（画面前面、亮的）那条动作最大；
  远侧（被身子挡住一半、暗的）那条也要动，和近侧错开半圈。
- 身子跟着步子一高一低（影子已经按联盟的高低摆好），**整个人往前倾**，比站着时更低、更往前探；背包跟着背走。
- 弩一直端在身前朝右，跟着身子上下动，**形状和长度不变**；握弩的手握着它，远侧那只手跟着步子前后甩。
- 尾巴和破斗篷在身后甩，**尾巴的形状、环纹和长度不变**，只是弯的地方不同。
- **着地的脚贴着地面线**（模板里深灰横线），不要沉到线下面，也不要飘着。

## 画法规矩

- **一格 8 像素**：模板的影子就画在这张 8 像素的网格上，你画的每个方块也是 8×8，对齐同一张网格。像素画：方块清楚、硬边、
  没有抗锯齿、没有模糊和柔光。
- **颜色只用附图 1 里有的颜色**；外轮廓是设计里那圈近黑的描边。
- **大小照影子**：头和弩和影子一样大，身子、腿、尾巴照附图 1 的比例接上去；十字是这一帧的站位点，**不要挪**（游戏里他站的点就是这里）。
- **背景真透明**（每个像素透明度只有 0 或 255；做不到就纯白 `#FFFFFF` 背景）。不要画网格线、格子边框、编号、地面线、影子。
- 不要自己缩放或裁剪：交付的图和模板一样大（每张 2048×1920，2×2 格，每格 1024×960）。

## 提示词

```text
Pixel-art game sprite animation, 8 frames, for a small tactics game. Image 1 is THE character: Twitch, a hunched plague
rat seen from the side (three-quarter) facing RIGHT - big ears, a golden goggle over one eye, a wide grin full of fangs, a
backpack with green vials on his back, a ragged dark-teal cloak, a long ringed tail, a big golden crossbow with a green
chem tank on top held in front of him. Image 2 is the same character drawn large (the design was read from it). Keep the
design EXACTLY: the same head, goggle, grin, crossbow, colours and proportions in every frame - nothing stretched or
deformed.
Draw his RUN as League of Legends' Twitch run (image 3: League's model at our camera, the same 8 frames, frame 1 at the
top left): a low, hunched scurry forward, two strides per loop. Frame k follows image 3's frame k. 1: the body high and
leaning forward, the front leg reaching down to land, the back leg bent behind, the far hand swinging back. 2: the front
foot planted, the leg straight (the body highest), the back leg leaving the ground and swinging forward, the tail up.
3: the body sinking and driving forward, the planted leg bending, the other leg passing under the body. 4: the body
lowest, both legs gathered under it (the legs swap). 5-8: the same with the other leg in front. League's model has other
proportions (taller ears there; our head sits further forward, our crossbow, tail and cloak are longer): take only its
MOTION, keep OUR design.
Both legs move clearly, each swinging at least 8-10 squares - the near (front, brighter) leg the most, the far (half
hidden, darker) leg too, half a cycle apart. The whole body leans forward, lower than standing; the backpack rides on his
back. The crossbow stays held in front pointing right, the same shape and length, moving with the body; the near hand
grips it, the far hand swings with the stride. The tail and the ragged cloak swing behind him with the same shape and
length. Planted feet stay on the ground line.
The two attached templates (images 5 and 6): each cell is one frame; the light grey ghost shows ONLY the head and the
crossbow (with the gripping hand and the chem tank) - their SIZE and where they are in that frame. Draw him over it at
the same size and place, with the body, backpack, cloak, legs, far hand and tail posed as in image 3's frame and joined
to the head and the crossbow. The small cross is the standing point (keep it); the dark grey line is the ground.
THE PIXEL GRID: every square exactly 8x8 px on the template's grid, hard edges, no anti-aliasing, no blur, no glow; the
near-black outline of image 1 around him; only the colours of image 1.
Output: two images exactly like the templates, 2048x1920 each, 2x2 cells of 1024x960 (run_1 = frames 1-4, run_2 = frames
5-8, left to right, top to bottom). Transparent background (every pixel fully transparent or fully opaque; if impossible
pure white #FFFFFF). No ghost, no grid lines, no borders, no numbers, no ground line, no shadow, no bolts or effects.
```

## 附图（在压缩包 `twitch_run_pack.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_twitch_design_8x.png` | 图奇定稿设计（8 倍） | **要画的就是他**：造型、颜色、比例 |
| `refs/2_twitch_picture_large.png` | 同一个他的大图（设计图从它读出来） | 看细节：脸、背包、弩、尾巴 |
| `refs/3_league_run_8_frames.png` | 英雄联盟跑步的同 8 帧（我们的镜头） | **动作照它**：第 k 帧照第 k 格 |
| `refs/4_twitch_run_in_game_now_DONT_COPY.png` | 现在游戏里的跑步（3 倍） | 毛病：上半身和弩钉住、腿小碎步，**不要照它** |
| `templates/run_1.png` | 第 1–4 帧的模板（2048×1920） | 头和弩的大小和位置，十字，地面线 |
| `templates/run_2.png` | 第 5–8 帧的模板（2048×1920） | 同上 |

## 交回前请检查

- 两张图都是 2048×1920、2×2 格、和模板一样的排法；真透明背景（或纯白）；没有缩放、裁剪；没有影子、网格、边框、编号、地面线。
- 一格 8 像素、对齐模板的网格；硬边、没有抗锯齿和柔光；只用附图 1 的颜色，外面一圈近黑描边。
- 他和附图 1 一模一样（头、护目镜、牙、背包、弩、斗篷、尾巴、颜色、比例），头和弩和影子一样大，十字没挪；**没有变形**。
- 8 帧连起来是联盟那样压低身子往前蹿：**两条腿都在动**（远侧的也在动，错开半圈），每条腿前后摆 8–10 格；
  身子前倾、一高一低；远侧的手往后甩；尾巴和斗篷在身后甩；着地的脚贴地面线。
- 交付放 `outputs/twitch-run/`：`run_1.png`、`run_2.png`，原始生成图放 `raw/`，`generation-prompts.txt`，最后写
  `HANDOFF.md`，打包成 `outputs/twitch_run_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回（像 `tools/art/read_shyvana_dragon_run.py`：先查是不是正好 8 像素一格、对齐模板网格、只用设计图的颜色；不是就照
  `tools/art/read_gnar_mega_run.py` 量出格子大小、每格取多数颜色、归到设计图 `hd/design.png` 的颜色），得到 PPU 2.2 的 8 帧；
  放进 `rig_twitch_hd.py` 的画布：模板第 64 列 = 站位点，第 85 行 = 地面（脚在它上面一行）。头、护目镜、弩每帧和设计图比形状
  （变了就重来），整条身子帧和帧之间的前后跳动（龙女那次 Codex 的帧整体跳 6–8 格，做过整帧平移的版本给用户挑）。
- 当成 run 的新原稿：`rig_twitch_hd.py` 有这 8 帧就拿它们当 run；照 `D:/TFM2-Workshop/kept/run_splice_1122` 的拼法（README；
  先拿旧帧走一遍，和提交逐像素一致）：导出 run → 1x 拼进整张图 → `restyle_one.py twitch run` → `hd_one.py` → 
  `thin_outline.py --hero twitch`；`cmp_tags.py` 只有 run / hd_run / lo_run 变；8 × 100 ms。图奇的帧表编在 league.dll
  （`addons/league_main/src/hd.rs`）里：league.dll 跟着重编、换号。
- 「现在 | 新」的逐像素 GIF（`C:/t/za_work/exact/exact_gif.py`）给用户看，用户点头才装。
