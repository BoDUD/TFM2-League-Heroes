# 奥莉安娜：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户选了你第 0 步画的 **A**（`1_picked_A.png`），定的大小是：游戏里**从发髻顶到脚底 38 行**，每个游戏像素 1.5 格，也就是她要画成 **57 格高**（约 32 格宽）。
> - 用户还要求两处改动：
>   - **头画大一点**：从发髻顶到下巴约 **16 格**（全身 57 格的 28%，A 里约 25%），脸、眼睛在游戏里看得清；身体仍然纤细，下巴以下约 41 格。
>   - **球画小一点**：直径约 **14 格**（她身高的 25%，A 里是 31%）。
> - **她和球分开画成两张图**：游戏里球是单独的一张图（漂在她身边、扔出去停在地上、挂在队友身上都用这一张）。
> - 我把 A 按这个比例直接缩好了（`2_target_body.png`，每格 12 px；`5_target_ball.png` 是球），**大小、位置、姿势都对，但糊了**：脸和眼睛糊成几格，发髻和刘海的金色分不出层次，关节小金球没了，裙子的齿轮尖刺糊成一片，脖子那里还有一道接缝。
> - **这一轮就是在同样的格子上把它们重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，像一个像素画师照着 A 在 32 × 57 的格子里一格一格画出来的。**每样画两稿。**

## 大小和位置（照 `2_target_body.png` / `3_layout.png` / `5_target_ball.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **她**：**发髻顶在 y = 276**（绿线），**下巴在 y ≈ 468**（蓝线），**脚底在 y = 960**（红线），两只脚底在同一条线上；左右位置、手臂伸出去的位置、两腿分开的样子照 `2_target_body.png`。**这张图里不画球。**
- **球**：单独一张 1024 × 1024 的图，**直径约 14 格（168 px）**，放在画布正中（`5_target_ball.png`）。`3_layout.png` 里画出了球漂在她身边的位置，只是参考，不要画进她那张图。

## 要画清楚的地方（她）

- **头**（`4_head.png`）：
  - 金色金属的齐耳短发，刘海斜着遮一点额头，两侧包到下巴，头顶一个圆发髻；金色分 3–4 档（亮金、金、暗金、棕金），发丝的方向用档次分出来，不要糊成一片。
  - 瓷白的脸（冷灰白，带一点灰紫），**两只青绿色眼睛一样大、在同一行**（每只至少 2 格宽，眼睛里有 1 格亮点），小小的深色嘴唇，下巴尖。
- **身体**：
  - 脖子前一枚**金色齿轮徽章**（2–3 格），**银白色的胸甲**分 3 档，胸甲下面露出橄榄灰的金属躯干。
  - 手臂是一节一节的**橄榄灰金属**，**肩膀和手肘的金色小圆球关节**看得出来（每个约 2 格）；手是银白色，手指细长、指尖尖。
  - 腰上一圈**金色齿轮刀片短裙**：一片片尖尖地向外张开，每片尖刺都能数得出来，里层深青铜色。
  - 细长的橄榄灰金属腿，**膝盖和脚踝的金色小圆球关节**，小腿外侧银白色护甲片，尖头银灰金属靴。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 要画清楚的地方（球）

- 一颗**银色金属球**，钢银色分 3–4 档，有一边亮一边暗的立体感（亮面在左上）。
- 球面上深色的刻纹，几块**淡紫色的小窗格**（每块 2 格左右）。
- 球腰上**两道铜金色的环**（各 1–2 格宽，环之间一道深缝），球顶一道金色的弧形脊。
- 一圈近黑外描边。

## 干净

- 和附图 6–9（本包的卡特琳娜、杰斯、斯莫德都是每游戏像素 1.5 格，伊莉丝 1.8 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照 A（金、银白、橄榄灰、青绿眼睛、淡紫小窗格）。**青绿只用在眼睛上，淡紫只用在球的小窗格上。**
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `orianna_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节**全照它 |
| `2_target_body.png` | A 的人按新比例（头稍大）缩到 32 × 57 格、每格 12 px 放在画布上（糊的） | **她的大小、位置、姿势、头身比**照它，糊的地方重画 |
| `3_layout.png` | 同一张加网格线：绿线 = 发髻顶 y 276，蓝线 = 下巴 y 468，红线 = 脚底 y 960；球漂在旁边的位置 | 对齐网格、头和脚底的位置 |
| `4_head.png` | A 的头（读回后 8 倍放大） | 头发、发髻、脸、眼睛 |
| `5_target_ball.png` | A 的球缩到 14 × 14 格（糊的），画布正中 | **球的大小和位置**照它 |
| `style/6_style_katarina.png` … `9_style_elise.png` | 本包的卡特琳娜、杰斯、斯莫德（每游戏像素 1.5 格）、伊莉丝（1.8 格），8 倍放大 | **只看风格**：这个密度下一格有多大、脸怎么画、描边、分档 |

## 提示词 1：`orianna-model-1.png`、`orianna-model-2.png`（她，两稿）

附全部 9 张图。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art picture of this character - a slender clockwork doll girl with a golden metal bob and a round bun, a porcelain face with glowing teal eyes, a silver-white metal bodice, segmented olive-grey metal limbs with small golden ball joints and a short skirt of golden gear blades, a silver metal ball floating beside her (the LOOK, the COLOURS and the DETAILS to keep); 2 the same girl WITHOUT the ball, shrunk to her final game size, 32 x 57 squares of 12 px on a 1024x1024 canvas, with a slightly bigger head than image 1 - the SIZE, the PLACE, the POSE and the HEAD-TO-BODY PROPORTION are right, but it is muddy (the face and eyes blurred, the hair's gold shades lost, the ball joints gone, the skirt's blades smeared, a seam at the neck); 3 the same with grid lines every 5 squares: the green line = the top of her bun (y 276), the blue line = her chin (y 468), the red line = her soles (y 960), and where the ball floats beside her (for reference only); 4 the head of image 1 enlarged; 5 the ball alone at its final size (for the other picture); 6-9 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - copy their pixel-art look.
Draw with the image generator ONE clean pixel-art picture of the same girl WITHOUT the ball: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of her bun at y 276, her chin at y 468 (the head from the bun to the chin about 16 squares - a little bigger than in image 1, so the face reads at game size), her soles at y 960 on one ground line, the near hand down at her side with the fingers spread, the far hand before her chest - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: the GOLDEN METAL BOB with the bangs across the forehead, the sides to the jaw and the ROUND BUN on top, the gold in 3-4 shades (bright gold, gold, dark gold, brown-gold) showing the hair's strands; a PORCELAIN face (cool grey-white with a faint violet tint), TWO TEAL EYES the same size on the same row (at least 2 squares wide each with a 1-square highlight), small dark lips, a pointed chin; the GOLDEN GEAR EMBLEM at the throat; the SILVER-WHITE BODICE in 3 shades, the olive-grey metal torso below it; segmented OLIVE-GREY metal arms with readable SMALL GOLDEN BALL JOINTS at the shoulders and elbows (about 2 squares each); silver-white hands with long thin pointed fingers; the SHORT SKIRT of GOLDEN GEAR BLADES flaring out with every pointed blade countable, a dark bronze layer under it; slim olive-grey legs with golden ball joints at the knees and ankles, silver-white shin plates, pointed silver-grey boots.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing; the teal only for the eyes.
No ball, no effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`orianna-ball-1.png`、`orianna-ball-2.png`（球，两稿）

附同样 9 张图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of the character's BALL alone (the ball floating beside her in image 1, at the size of image 5): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255), the ball about 14 squares across (168 px) in the middle of the canvas, every square 12 px aligned on one straight grid starting at the canvas corner.
A SILVER METAL SPHERE in 3-4 steel-silver shades, lit from the upper left (a bright side and a dark side), dark engraved swirls on its surface and a few small PALE VIOLET window panels (about 2 squares each); TWO COPPER-GOLD BANDS round its middle (1-2 squares each, a dark seam between them), a golden curved ridge over its top; one continuous near-black outline round it; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing; the pale violet only for the window panels.
No girl, no effects, no glow, no background, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 她：大小、位置、姿势和 `2_target_body.png` 一样：发髻顶 y 276、下巴约 y 468、脚底 y 960、每格 12 px、对齐网格；**头比 A 稍大**、身体仍然纤细；**两只青绿眼睛一样大、同一行**；关节小金球、裙子尖刺清楚；外描边连续；**图里没有球**。
- 球：直径约 14 格、画布正中；两道铜金环、淡紫小窗格、顶上金脊清楚；外描边连续。
- 颜色照 A；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/orianna-model/`）

- `orianna-model-1.png`、`orianna-model-2.png`、`orianna-ball-1.png`、`orianna-ball-2.png`；**image_gen 的原始生成图原样放 `outputs/orianna-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/orianna_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），和 `2_target_body.png` 并排、按游戏大小和拉克丝、辛德拉、德莱厄斯、慎放一起给用户挑一稿（用户审核，不要自己判定）。球的两稿也一起给用户挑。
- 选定后写第 2 步动作包：**待机由 Codex 画**（潘森的教训：待机要和动作帧同一比例、同样的站姿，所以待机也在动作包里画，5–7 帧呼吸），每帧在同样的格子上画（每游戏像素 1.5 格，不再缩放），**动作帧里不画球**；跑步照英雄联盟（Orianna_run）；普攻 = 手一挥射出小发条弹（Orianna_attack1-3）；Q / W / E / R 都是指挥球的手势（orianna_spell1、Orianna_spell2、Orianna_spell3、Orianna_spell4，R 原版会跳起来）；死亡（Orianna_death）。
