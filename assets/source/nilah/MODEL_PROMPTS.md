# 尼菈（不羁之悦）：在格子上画侧身造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画 A（`nilah/2_picture.png`：收起的鞭刃竖直举在肩旁），游戏里按「每个游戏像素 2.5 格」显示（高清 PPU：**你画的每一格就是游戏里的一个高清像素**，交回后我 1:1 读回，不缩放）。
> 原画 A 按它自己的格子读回后已经很干净（`1_front_grid.png`），**正面版直接用它，这一轮不用重画正面**。
> - **要画的是侧身版 `side`（最重要，所有动作都从它来）**：本包所有英雄除了待机，每个动作都是**侧身朝右**。之前一个英雄的造型只画了正面，动作帧全成了正面站着，被用户全部退回。所以同一个造型再画一个**身体转向画面右边**的版本（英雄联盟里她转过去的样子见 `3_league_side.png`，第一帧是待机，后两帧是跑步）。
>
> **侧身版和正面版必须是同一个人**：同样的格子、同样的高度和头身比、同样的颜色和细节，只是身体转了个角度。

## 大小和位置

- 画布 **1024 × 1536，固定 12 × 12 px 的格子**（85 列 × 128 行，右边 4 px 留透明），**每个格子一个颜色，格子对齐画布左上角**。直接在格子上画，**不要先画大图再缩小**（会糊）。
- 和 `1_front_grid.png` 同样的位置：**头发顶在第 15 行**（绿线），**脚底最低的一行是第 115 行**（红线上面那一行，红线以下什么都不能有：游戏在脚下画血条）——头顶到脚底 101 行。**举起的刃尖约在第 10 行**（紫线）。**站立点（两脚中间）在第 42 列**（蓝线）。
- 画在空格子 `6_empty_grid.png` 上，同样的行和列；最宽不超过 70 格（马尾、武器都算）。

## 侧身版怎么画

- **身体转向画面右边**（像 `3_league_side.png` 第一帧）：黄色单肩上衣、胸前紫青亮边、青铜交叉项圈都侧过来朝右；露出的那边肩膀和**缠黄布条的那条胳膊在身前**（画面右边），手张开在胸前；**缠暗红护臂、拿武器的那条胳膊在身后**（画面左边），把收起的鞭刃**竖直举在肩后**，刃尖朝上，**整把武器一条直线**（青铜握柄、下端青色尖刃、上端暗红紫刀片，和正面版一样的格子画法）。
- **腿**：从侧面看**一前一后**（近侧腿在前、颜色亮；远侧腿在后、暗一档），**深紫红灯笼裤**蓬松，**青铜护膝护腿**在小腿外侧，**黑色平底鞋的鞋尖朝右**，两只脚底都踩在第 115 行。
- **腰**：紫青腰带、**紫色带青铜边的飘带裙片**垂在身侧，**青铜笼子里的深色圆球**挂在近侧腰边（画面右边一点）。
- **长马尾**：从后脑垂下来，**拖在背后（画面左边）**，一直垂到膝盖后面；不能挡住脸和武器。
- **头保持和正面版一样的 3/4 角度**（脸朝看画的人、两只紫眼睛都看得见、齐刘海、两侧短发、青绿耳坠、笑脸）——本包的规矩是所有动作帧都用待机那一张脸，**不另画侧脸**；只是把这颗头放在侧过来的身体上，脖子接得自然。
- 比例和正面版一样敦实（头约占五分之一）；不要把侧身画瘦、画高。

## 干净（照正面版和 `5_style.png` 的统一画风）

- 每个 12 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光）；外轮廓一圈 **2 格粗的近黑描边**，里面少用黑（内部分界用材质自己的暗色）；不要抖动、渐变、碎点、零散杂色格；**颜色用正面版里已有的那些**（深棕皮肤、蓝黑头发、明黄上衣、深紫红裤子、青铜青绿、暗红护臂、紫色飘带、近黑描边），不要新增颜色。
- 背景真透明，**alpha 只能是 0 或 255**（不要半透明光晕——上一轮的原画四周有一圈半透明）。不要网格线、文字、编号、边框、影子、特效。

## 附图（压缩包 `nilah_model_pack.zip` 里；一次只能附五张时先附 1、3、6、4、5）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_front_grid.png` | 原画 A 按格子读回，放在 12 px 格子上；灰线量格子；紫线 = 刃尖第 10 行，绿线 = 头发顶第 15 行，红线 = 第 115 行下沿，蓝线 = 站立点第 42 列 | **她的样子、颜色、格子大小、比例**；头（3/4）逐格照它 |
| `2_picture.png` | 用户选的原画 A | 长相、配色 |
| `3_league_side.png` | 英雄联盟模型转到侧面朝右（待机、跑步两帧） | **侧身版怎么转**：黄色上衣侧过来、拿刃的手在身后、腿一前一后、马尾拖在后面 |
| `4_league_head.png` | 英雄联盟模型的头 | 刘海、耳坠、笑脸 |
| `5_style.png` | 本包重做后的高清英雄（泽丽、奈德丽、卡尔玛） | 统一画风：像素粗细、粗描边、敦实 |
| `6_empty_grid.png` | 空格子，同样的行列标线 | 侧身版的画布 |

## 提示词：侧身版 `nilah-side-A.png`、`nilah-side-B.png`（两稿）

附 1、3、6、4、5、2。

```text
Attached images: 1 this character's approved front design on a fixed grid of 12x12-pixel squares (purple line = row 10, green line = row 15, red line = the bottom of row 115, blue line = column 42) - her LOOK, colours, square size and proportions, and her HEAD square for square; 3 her 3D model turned to the side, facing right (the idle, then two run frames) - how she looks SIDE-ON; 6 an empty grid with the same lines - the canvas; 4 her head on the 3D model; 5 other heroes of this game in the same look (style only); 2 the approved picture the front design was read from.
Draw the SAME character SIDE-ON, her body turned to face the IMAGE RIGHT, on the same fixed grid: one 1024x1536 PORTRAIT PNG with a real transparent background (85 x 128 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same height as the front design: the top of her hair on row 15, the soles' lowest row 115 (nothing below it), the raised blade tip about row 10, the standing point (between the feet) on column 42; at most 70 squares wide.
The character: Nilah, a cheerful melee fighter with DEEP BROWN SKIN - exactly the colours, square size, outline and details of image 1. SIDE-ON (like the first frame of image 3): the BRIGHT YELLOW ONE-SHOULDERED TOP with its purple-teal chest trim and the BRONZE-TEAL CROSSED COLLAR turned to the right; the arm with the YELLOW CLOTH BANDS in FRONT of her body (image right), its hand open before her chest; the arm with the DARK RED ARM WRAP BEHIND her (image left), holding the FOLDED WHIP-BLADE UPRIGHT behind her shoulder, the tip pointing straight UP - the weapon ONE STRAIGHT VERTICAL LINE drawn like in image 1 (bronze-teal grip, a short teal point below it, the folded dark red-purple blade segments above it); the legs ONE IN FRONT OF THE OTHER (the near leg in front in full tone, the far leg behind a shade darker), LOOSE DARK PLUM HAREM TROUSERS, the CURVED BRONZE-TEAL KNEE AND SHIN ARMOUR, FLAT BLACK SLIPPERS with their toes pointing RIGHT, both soles on row 115; the purple-and-teal sash, the PURPLE SKIRT PANEL WITH BRONZE EDGES hanging at her side, the BRONZE CAGE WITH A DARK ORB at the near hip; the VERY LONG BLUE-BLACK PONYTAIL hanging down her back to the back of her knees on the image left, never covering the face or the weapon. THE HEAD STAYS THE SAME 3/4 HEAD AS IN THE FRONT DESIGN, square for square (the face toward the viewer, both purple eyes visible, the straight fringe, the short side locks, the teal earrings, the smile) - every frame of this game keeps the idle's face, no separate profile face - only placed on the side-on body with a natural neck. Keep the front's STOCKY proportions (the head about one fifth of the height); do not make her thinner or taller.
Clean like image 1 and image 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares, no specks, no dithering, no gradients, ONLY the colours of image 1. No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Make TWO takes, A and B: A turned fully side-on (a clean profile body), B turned a little less (about three quarters toward the side, a bit more of the chest showing).
```

## 交回前请检查

- 两张图都是 1024×1536、12 px 格子对齐左上角、每格一个颜色、**alpha 只有 0 / 255**。
- 头发顶第 15 行、脚底第 115 行、站立点第 42 列、刃尖约第 10 行，最宽不超过 70 格。
- 身体真的转向右边（上衣侧过来、黄布条的胳膊在前、暗红护臂拿刃的胳膊在后、腿一前一后鞋尖朝右、马尾拖在左边）；**头和正面版是同一颗 3/4 的头**（逐格照 `1_front_grid.png`）；武器一条直线、竖直；颜色只用正面版的。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。

## 交付（`outputs/nilah-model/`）

- `nilah-side-A.png`、`nilah-side-B.png`；未经处理的生成原稿放 `outputs/nilah-model/raw/`；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 原稿逐格读回（regrid --size 12），检查高度、站立点、头（贴正面的 3/4 头，one-face-all-frames）、颜色映射到正面的调色板；正面 = 原画 A 读回 1:1。
- 设计定稿后：ppu_restyle crisp（统一画风，泽丽为样板），PPU 2.5（hd.rs HEROES + ppu_hd.py PPU + lo_ 帧，league.dll ≥ 0.6.63，先合最新 main，问布隆 / 铁男 / 修正模型 / 加里奥）；第 2 步动作条包 MODEL_STRIPS.md 从侧身版出（动作都是侧面朝右，跑步按 Caitlyn 的直腿交叉步）。
