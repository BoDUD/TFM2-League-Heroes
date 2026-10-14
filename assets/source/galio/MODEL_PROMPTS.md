# 加里奥（正义巨像）：在格子上画造型——正面版（改拳头）+ 侧身版（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画 A（`galio/2_picture.png`：两只金翅膀高高竖起），游戏里按「每个游戏像素 2 格」显示（高清 PPU：**你画的每一格就是游戏里的一个高清像素**，交回后我 1:1 读回，不缩放）。
> 原画 A 按它自己的格子读回后已经很干净（`1_front_grid.png`），所以：
> - **正面版 `front`（待机和选人卡片用）**：**照 `1_front_grid.png` 逐格保留，只改两只拳头**——原画把两只手都画成了卷起来的螺旋（像蜗牛壳），用户要**握紧的大石拳**（`3_league_fists.png` 右边那只就是握紧的样子：四根粗指节朝前、拇指压在外面，石头的棱角分明）。其他所有格子（翅膀、头冠、脸、胸口、肩甲、腿、尾巴、描边）**一格都不要动**。
> - **侧身版 `side`（最重要，所有动作都从它来）**：本包所有英雄除了待机，每个动作都是**侧身朝右**。之前一个英雄的造型只画了正面，动作帧全成了正面站着，被用户全部退回。所以同一个造型再画一个**身体转向画面右边**的版本（英雄联盟里他转过去的样子见 `4_league_side.png`，第一帧最像）。
>
> **两个版本必须是同一个人**：同样的格子、同样的高度和头身比、同样的颜色和细节，只是身体转了个角度。

## 大小和位置（两个版本一样）

- 画布 **1024 × 1536，固定 12 × 12 px 的格子**（85 列 × 128 行，右边 4 px 留透明），**每个格子一个颜色，格子对齐画布左上角**。直接在格子上画，**不要先画大图再缩小**（会糊）。
- **头冠尖在第 40 行**（绿线），**脚底最低的一行是第 115 行**（红线上面那一行，红线以下什么都不能有：游戏在脚下画血条）——头冠到脚底 76 行。**翅尖在第 14 行**（紫线）。**站立点（两脚中间）在第 49 列**（蓝线）。
- 侧身版画在空格子 `7_empty_grid.png` 上，同样的行和列；侧身版最宽不超过 80 格（尾巴、翅膀都算）。

## 侧身版怎么画

- **身体转向画面右边**：胸口、金徽章、肩甲都侧过来朝右——**近侧的大方块肩甲在前、远侧的肩甲大半藏在后面**；近侧手臂垂在身前（**握紧的石拳**看得见，在身体前面、画面右边一点），远侧手臂大半藏在身后。
- **腿**：反关节的兽腿从侧面看，**一前一后**（近侧腿在前、颜色亮；远侧腿在后、暗一档），大腿往前、小腿往后折、**三爪石脚的爪尖朝右**，两只脚底都踩在第 115 行。
- **翅膀**：两只金翅膀从背上竖起来，从侧面看**一前一后叠在背后（画面左边）**，翅尖同样到第 14 行左右；不能挡住脸和近侧的拳头。
- **尾巴**：从身后（画面左边）拖到地上，**尖端金箭头**朝左。
- **头保持和正面版一样的 3/4 角度**（脸朝看画的人、两只蓝眼睛都看得见、金头冠三根尖角）——本包的规矩是所有动作帧都用待机那一张脸，**不另画侧脸**；只是把这颗头放在侧过来的身体上。

## 干净（照正面版和 `6_style.png` 的统一画风）

- 每个 12 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光）；外轮廓一圈 **2 格粗的近黑描边**，里面少用黑（内部分界用材质自己的暗色）；不要抖动、渐变、碎点、零散杂色格；**颜色用正面版里已有的那些**（石头淡青灰、金色、蓝眼睛、近黑描边），不要新增颜色。
- 背景真透明，**alpha 只能是 0 或 255**（不要半透明光晕——上一轮的原画四周有一圈半透明）。不要网格线、文字、编号、边框、影子、特效。

## 附图（压缩包 `galio_model_pack.zip` 里；一次只能附五张时先附 1、3、4、2、6）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_front_grid.png` | 原画 A 按格子读回，放在 12 px 格子上；灰线量格子；紫线 = 翅尖第 14 行，绿线 = 头冠第 40 行，红线 = 第 115 行下沿，蓝线 = 站立点第 49 列 | **正面版：逐格照它，只改两只拳头**（不要画线） |
| `2_picture.png` | 用户选的原画 A | 长相、配色 |
| `3_league_fists.png` | 英雄联盟模型的两只手（右边那只是握紧的拳头） | **两只手都画成右边那样握紧的石拳** |
| `4_league_side.png` | 英雄联盟模型转到侧面朝右（待机、跑步两帧） | **侧身版怎么转**：肩甲一前一后、翅膀叠在背后、兽腿一前一后、尾巴拖在后面 |
| `5_league_head.png` | 英雄联盟模型的头 | 头冠、石头脸 |
| `6_style.png` | 本包重做后的高清英雄（莫德凯撒、布隆、泽丽） | 统一画风：像素粗细、粗描边、敦实 |
| `7_empty_grid.png` | 空格子，同样的行列标线 | 侧身版的画布 |

## 提示词 1：正面版 `galio-front.png`（一张：逐格保留，只改拳头）

附 1、2、3、6。

```text
Attached images: 1 this character's approved front design already drawn on a fixed grid of 12x12-pixel squares (grey measuring grid; purple line = row 14, green line = row 40, red line = the bottom of row 115, blue line = column 49); 2 the approved picture it was read from; 3 his hands on his in-game 3D model - the RIGHT one is a clenched fist; 6 other heroes of this game in the same look (style only).
Redraw image 1 square for square on the same grid as one 1024x1536 PORTRAIT PNG with a real transparent background (85 columns x 128 rows of 12x12-pixel squares aligned to the top-left corner, the right 4 px transparent; every square one flat colour; alpha only 0 or 255). KEEP EVERY SQUARE EXACTLY AS IN IMAGE 1 - the wings, the gold crown, the face and blue eyes, the chest emblem, the shoulder blocks, the arms, the legs, the clawed feet, the tail, the thick outline, the colours and the position (wing tips row 14, crown row 40, soles row 115, standing point column 49) - EXCEPT THE TWO HANDS: both are drawn as curled spirals like snail shells; replace each with a BIG CLENCHED STONE FIST like the right hand in image 3 - four thick knuckles toward the viewer, the thumb pressed over them, angular stone facets, in the same pale green-grey stone shades and the same thick near-black outline as the arms, about as big as the spirals were and at the same place at the end of each forearm. Use only the colours already in image 1. No grid lines, no text, no background, no shadow, no effects.
```

## 提示词 2：侧身版 `galio-side-A.png`、`galio-side-B.png`（两稿）

附 1、4、3、5、6、7（先画完正面版，侧身版用正面版的拳头）。

```text
Attached images: 1 this character's approved front design on a fixed grid of 12x12-pixel squares (purple line = row 14, green line = row 40, red line = the bottom of row 115, blue line = column 49) - his LOOK, colours, square size and proportions; 4 his 3D model turned to the side, facing right (idle, two run frames) - how he looks SIDE-ON; 3 his hands on the 3D model - the right one a clenched fist; 5 his head on the 3D model; 6 other heroes of this game in the same look (style only); 7 an empty grid with the same lines - the canvas.
Draw the SAME character SIDE-ON, his body turned to face the IMAGE RIGHT, on the same fixed grid: one 1024x1536 PORTRAIT PNG with a real transparent background (85 x 128 squares of 12x12 pixels aligned to the top-left corner; every square one flat colour; alpha only 0 or 255). Directly on the grid - do NOT draw a bigger picture and shrink it. The same height as the front design: the crown spike's top on row 40, the soles' lowest row 115 (nothing below it), the wing tips about row 14, the standing point (between the feet) on column 49; at most 80 squares wide.
The character: Galio, the Colossus, a living winged statue of PALE GREEN-GREY STONE with EARTHY GOLD TRIM - exactly the colours, square size, outline and details of image 1. SIDE-ON (like the first frame of image 4): the chest, the gold chest emblem and the shoulder blocks turned to the right - the NEAR huge blocky shoulder in front, the FAR one mostly hidden behind; the near arm hanging in front of his body with a BIG CLENCHED STONE FIST (four thick knuckles, the thumb over them, like the right hand of image 3), the far arm mostly hidden behind; the DIGITIGRADE BEAST LEGS one in front of the other (the near leg in front in full tone, the far leg behind a shade darker), thighs forward, shins bending back, the THREE-CLAWED STONE FEET pointing right, both soles on row 115; the TWO HUGE GOLD WINGS rising from his back, seen from the side one behind the other on the image left, their tips about row 14, never covering the face or the near fist; the STONE TAIL trailing behind him to the ground on the image left with its GOLD ARROWHEAD tip pointing left. THE HEAD STAYS THE SAME 3/4 HEAD AS IN THE FRONT DESIGN (the face toward the viewer, both blue eyes visible, the gold crown with its tall middle spike and two short side spikes) - every frame of this game keeps the idle's face, no separate profile face - only placed on the side-on body.
Clean like image 1 and image 6: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette, inner edges in each material's own dark shade, every detail at least 2x2 squares, no specks, no dithering, no gradients, ONLY the colours of image 1. No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Make TWO takes, A and B, that differ mainly in how far the body is turned and how the wings overlap.
```

## 交回前请检查

- 三张图都是 1024×1536、12 px 格子对齐左上角、每格一个颜色、**alpha 只有 0 / 255**。
- 正面版：和 `1_front_grid.png` 相比**只有两只手变了**（握紧的石拳），其他格子一格不差。
- 侧身版：头冠第 40 行、脚底第 115 行、站立点第 49 列、翅尖约第 14 行，最宽不超过 80 格；身体真的转向右边（肩甲一前一后、兽腿一前一后爪尖朝右、翅膀叠在背后、尾巴拖在左边）；**头和正面版是同一颗 3/4 的头**；颜色只用正面版的。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。

## 交付（`outputs/galio-model/`）

- `galio-front.png`、`galio-side-A.png`、`galio-side-B.png`；未经处理的生成原稿放 `outputs/galio-model/raw/`；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 原稿逐格读回（regrid / 12 px 网格采样），正面版和 `1_front_grid.png` 逐格比较：拳头以外有差的格子一律用原读回的；侧身版检查高度、站立点、头（贴正面的 3/4 头，one-face-all-frames）、颜色映射到正面的调色板。
- 设计定稿后：PPU 2.0（hd.rs HEROES + ppu_hd.py PPU，league.dll 版本 ≥ 0.6.41，先合 ppu-chunky / 最新 main，问「布隆」「修正模型」）；第 2 步动作条包从侧身版出（PPU 原稿路线：库奇 / 莫德凯撒 / 布隆）。
