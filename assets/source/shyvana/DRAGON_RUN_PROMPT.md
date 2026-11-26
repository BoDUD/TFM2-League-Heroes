# 龙女龙形态的跑步重画：给 Codex 的提示词（8 帧，2 张图）

> 用户 2026-11-22：「龙女变形的龙的跑步姿势也可以让codex重画一下 现在也很僵硬」。
>
> - 现在游戏里龙的跑步（附图 4）：身子原样不动，四只爪各自前后挪三格，翅膀转几度，看上去像在原地蹭。**这次重画龙形态的跑步 8 帧。**
> - **角色照附图 1 的定稿设计**（四分之三侧面，朝右，头在右下）。附图 2 是同一条龙的大图（你以前画的那张，一格 11 像素），
>   细节看它。头、火焰鬃毛、角、两只翅膀、身上的青色甲片、金色爪子、尾巴末端的金色尾鳍：颜色、大小、比例都不能改，**不能变形**。
> - **动作照英雄联盟龙形态的 run1**（附图 3：联盟的模型在我们这个镜头下的同 8 帧，左上是第 1 帧）。**第 k 帧就照附图 3 的第 k 帧**：
>   前后腿轮流着地、一蹦一蹦地跑，身子跟着起伏、前后俯仰，尾巴上下卷，远侧翅膀前后扫。
> - 联盟的模型和我们的设计比例不一样（我们的尾巴更长、身子更低、近侧翅膀矮一截）：**只学它的动作，造型照我们的设计。**
> - **模板（`templates/run_1.png`、`run_2.png`）**：每格一帧。浅灰的影子**只有头、身子和两只翅膀**（腿和尾巴故意没画），管的是
>   大小、位置和这一帧身子的高低；四条腿和尾巴照附图 3 同一帧画上去。
> - 只画这 8 帧，别的动作、特效（喷火之类）都不画。
> - 交回时附 `HANDOFF.md`：用了哪条提示词、每帧有没有没做到的地方。

## 动作：一蹦一蹦的奔跑（英雄联盟 ShyvanaDragon run1），8 帧循环，每帧 100 毫秒

| 帧 | 这一帧（对照附图 3 同一帧） |
|---|---|
| 1 | 前爪着地：一只前爪在胸口下面撑地，另一只在头下面往前伸着落地；两条后腿在身后往后蹬；尾巴往后伸直 |
| 2 | 身子从前爪上压过去、头最低：前爪撑着往后斜；**后腿离地往前收**；尾巴往上翘；近侧翅膀抬到最高 |
| 3 | 前爪往后推到身子下面偏后；后腿收到肚子底下；尾巴放平往下摆；远侧翅膀往后放 |
| 4 | **后爪落地**（落在肚子底下）；前爪离地往前收；尾巴往后平伸；远侧翅膀往后平伸 |
| 5 | 后腿撑地，**前半身抬起，前爪往前伸到头前面**；尾巴往上卷、尾尖朝上 |
| 6 | **前爪往前落地**、伸到最前，后腿还在肚子底下：四只爪都着地，身子缩得最短；尾巴卷到最高；两只翅膀往上抬 |
| 7 | 后腿往后蹬，身子往前送；前爪撑地；尾巴往下甩 |
| 8 | 后腿在身后蹬直，前爪往前下方伸、快着地（接回第 1 帧）；尾巴往后甩直 |

- **四条腿都要动**，每条腿的前后摆动至少 **6–8 格**（现在只有 3 格，就是毛病）：近侧（画面前面、亮的）的腿动作最大；
  远侧（被身子挡住一半、暗的）的腿也要动，比近侧晚一帧、幅度小一点。
- 身子跟着步子起伏 2–3 格、前后俯仰（落前爪时前低后高，前爪往前伸时前高）；尾巴跟着身子上下卷，**尾巴形状和长度不变**，
  只是弯的地方不同；远侧翅膀前后扫、近侧翅膀上下动几格，**翅膀形状不变**（整只转，不拉长不压扁）。
- 头、角、火焰鬃毛每帧都是同一个形状，只是跟着身子动。
- **着地的爪子贴着地面线**（模板里深灰横线），不要沉到线下面，也不要飘着。

## 画法规矩

- **一格 8 像素**：模板的影子就画在这张 8 像素的网格上，你画的每个方块也是 8×8，对齐同一张网格。像素画：方块清楚、硬边、
  没有抗锯齿、没有模糊和柔光。
- **颜色只用附图 1 里有的颜色**；外轮廓是设计里那圈近黑的描边。
- **大小照影子**：头、身子、翅膀和影子一样大；十字是这一帧的站位点，**不要挪**（游戏里她站的点就是这里）。
- **背景真透明**（每个像素透明度只有 0 或 255；做不到就纯白 `#FFFFFF` 背景）。不要画网格线、格子边框、编号、地面线、影子。
- 不要自己缩放或裁剪：交付的图和模板一样大（每张 2048×1920，2×2 格，每格 1024×960）。

## 提示词

```text
Pixel-art game sprite animation, 8 frames, for a small tactics game. Image 1 is THE character: Shyvana's dragon form, a
red dragon in a three-quarter view facing RIGHT (head at the lower right): a flaming orange-yellow mane over the neck and
head, golden horns, two wings (the near crimson wing standing up over the shoulders, the far dark-violet wing sweeping up
to the left), teal armour plates, golden claws on four legs, a long tail ending in a golden fin. Image 2 is the same
dragon drawn large. Keep the design EXACTLY: the same head, mane, horns, wings, plates, colours and proportions in every
frame - nothing stretched or deformed.
Draw its RUN as League of Legends' ShyvanaDragon run1 (image 3: League's model at our camera, the same 8 frames, frame 1
at the top left): a bounding gallop. Frame k follows image 3's frame k. 1: the fore paws land, the hind legs pushing back,
the tail straight back. 2: the body passes over the fore legs, the head lowest, the hind legs leave the ground and swing
forward, the tail rising, the near wing highest. 3: the fore legs push back under the body, the hind legs gathered under
the belly, the tail sweeping down, the far wing lowering back. 4: the hind paws land under the belly, the fore paws lift
off, the far wing stretched back flat. 5: the hind legs push, the front of the body rises, the fore paws reach out ahead
of the head, the tail curling up. 6: the fore paws land farthest forward with the hind legs still under the belly (all
four paws down, the body shortest), the tail curled highest, both wings lifting. 7: the hind legs push back, the body
driving forward, the tail swinging down. 8: the hind legs stretched back, the fore paws reaching down to land (loops back
to frame 1). League's model has other proportions (our tail is longer, the body lower, the near wing shorter): take only
its MOTION, keep OUR design.
All four legs move clearly, each swinging at least 6-8 squares - the near (front, brighter) legs the most, the far (half
hidden, darker) legs too, one frame later and a bit less. The body bobs 2-3 squares and pitches with each bound; the tail
curls up and down with the same shape and length; the far wing sweeps back and forth and the near wing lifts and settles
a few squares, turned whole, never stretched. Planted paws stay on the ground line.
The two attached templates (images 5 and 6): each cell is one frame; the light grey ghost shows ONLY the head, the body
and the two wings (the legs and the tail are left out on purpose) - their SIZE, where they are and how high the body is in
that frame. Draw the dragon over it at the same size and place, with the legs and the tail posed as in image 3's frame.
The small cross is the standing point (keep it); the dark grey line is the ground.
THE PIXEL GRID: every square exactly 8x8 px on the template's grid, hard edges, no anti-aliasing, no blur, no glow; the
near-black outline of image 1 around the dragon; only the colours of image 1.
Output: two images exactly like the templates, 2048x1920 each, 2x2 cells of 1024x960 (run_1 = frames 1-4, run_2 = frames
5-8, left to right, top to bottom). Transparent background (every pixel fully transparent or fully opaque; if impossible
pure white #FFFFFF). No ghost, no grid lines, no borders, no numbers, no ground line, no shadow, no fire breath.
```

## 附图（在压缩包 `shyvana_dragon_run_pack.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_dragon_design_8x.png` | 龙形态定稿设计（四分之三侧面，8 倍） | **要画的就是它**：造型、颜色、比例 |
| `refs/2_dragon_design_full_size.png` | 同一条龙的大图（一格 11 像素） | 看细节：鬃毛、角、翅膀骨、甲片 |
| `refs/3_league_run1_8_frames.png` | 英雄联盟 run1 的同 8 帧（我们的镜头） | **动作照它**：第 k 帧照第 k 格 |
| `refs/4_dragon_run_in_game_now_DONT_COPY.png` | 现在游戏里的跑步（3 倍） | 毛病：腿只挪 3 格、身子不动，**不要照它** |
| `templates/run_1.png` | 第 1–4 帧的模板（2048×1920） | 头、身子、翅膀的大小和位置，十字，地面线 |
| `templates/run_2.png` | 第 5–8 帧的模板（2048×1920） | 同上 |

## 交回前请检查

- 两张图都是 2048×1920、2×2 格、和模板一样的排法；真透明背景（或纯白）；没有缩放、裁剪；没有影子、网格、边框、编号、地面线。
- 一格 8 像素、对齐模板的网格；硬边、没有抗锯齿和柔光；只用附图 1 的颜色，外面一圈近黑描边。
- 龙和附图 1 一模一样（头、鬃毛、角、翅膀、甲片、尾鳍、颜色、比例），头、身子、翅膀和影子一样大，十字没挪；**没有变形**。
- 8 帧连起来是联盟 run1 那样一蹦一蹦的奔跑：**四条腿都在动**（远侧的也在动，晚一帧），每条腿前后摆 6–8 格；
  身子起伏、前后俯仰；尾巴上下卷；远侧翅膀前后扫；着地的爪子贴地面线。
- 交付放 `outputs/shyvana-dragon-run/`：`run_1.png`、`run_2.png`，原始生成图放 `raw/`，`generation-prompts.txt`，最后写
  `HANDOFF.md`，打包成 `outputs/shyvana_dragon_run_done.zip`。

## Claude 收到后（给 Claude 看）

- 读回（像 `tools/art/read_gnar_mega_run.py`：量出一格多少像素，每格取多数颜色和透明度，归到设计图 `hd/d_idle.png` 的颜色），
  得到设计密度（PPU 1.5）的 8 帧；放进 rig_shyvana.py 的画布：站的那一列（`D_STAND` = 58）对站位点，最低的爪子落在地面
  （`GY` 上一行）。头、鬃毛、翅膀每帧和设计图比形状（`变形` 就重来），数四条腿都在。
- 当成 `assets/source/ppu/orig/shyvana_d_run.png` 的新原稿，照 `D:/TFM2-Workshop/kept/gnar_run_1122` 的拼法：1x `d_run`
  拼进整张图、`restyle_one.py d_run`、`hd_one.py d_run --write`，`cmp_tags.py` 只有 d_run / hd_d_run / lo_d_run 变；8 × 100 ms。
  龙女的帧表编在 league.dll（`addons/league_main/src/hd.rs`）里：league.dll 跟着重编、换号。
- 「现在 | 新」的逐像素 GIF（`C:/t/za_work/exact/exact_gif.py`）给用户看，用户点头才装。
