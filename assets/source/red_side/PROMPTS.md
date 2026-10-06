# 红色方朝向：艾克大招的全息残影改成正面（给 Codex）

> **这一份只有 1 张图：艾克的正面站姿。** 其他造型、动作、特效都不动。
> - 为什么要画：游戏从来不把特效图左右翻转，只翻转英雄本体的动作图（2026-10-06 查明，见 `.claude/skills/tfm2-hero-mod/references/champion-data.md` 第 6 节）。艾克的大招「时空断裂」会在他放大招的地方留一个 4 秒的全息残影，这个残影是用他**侧身朝右**的待机图做的；艾克在红色方（朝左）放大招时，残影还是朝右，看起来是反的。画成**正面朝向屏幕**的站姿，左右都对。
> - 包里的图：
>   - `design/ekko_design.png`：定稿造型（8 倍，每 8×8 像素是 1 格），侧身朝右。**正面图的配色、比例、发型、头带、围巾、外套、裤子、鞋、武器都照它画，只是转成正面。**
>   - `now/ekko_r_ghost.png`：现在游戏里的残影（左：蓝色方，右：镜像后的样子）。残影是 Claude 从你画的站姿自动生成的：所有颜色按亮度换成 4 档薄荷绿，每隔 3 行一条暗扫描线，半透明。所以**轮廓和明暗要清楚**——深色描边、脸和头发亮、衣服中间调，转成单色后还能一眼认出是艾克。
>   - `size/ekko_canvas.png`：画布（56×56 格，8 倍 = 448×448 像素），细网格每格 8 像素。**红线是鞋底**（第 46 行的下沿），**青色竖线是中线**（第 28 列），**黄线是头发顶**（第 12 行，和侧身待机一样高：头发顶到鞋底 35 格）。
>   - `refs/ekko_front_league_45.png`、`refs/ekko_front_league_70.png`：英雄联盟里艾克模型接近正面的样子（待机动作），只用来看正面长什么样。Riot 的素材，只在本地用，不要提交、不要发出去。
> - 交回 `ekko_front.png`，放在 outputs 里；再附一个 `HANDOFF.md`（用了哪条提示词、有没有没做到的地方），最后写。最好打成 `ekko_front_done.zip`。

## 要画的图：`ekko_front.png`，1 帧

艾克**正面站立，面朝屏幕**（不是 3/4 侧身，也不是背面），身体放松站直，不是侧身待机那样的半蹲。

- 姿势：两脚分开约与肩同宽，脚尖朝前，重心在中间；头正对前方，眼睛看着屏幕。
- 武器（青绿色发光的球棒 / 时光刃）：一只手握着，竖直垂在身体一侧，棒头朝下靠近地面；另一只手自然垂下或叉腰。
- **左右要大致平衡**：人站在中线上，头、身体、两腿以中线为轴；武器在一侧没关系，但不要整个人朝左或朝右倾、朝某一边迈步或出手。这张图左右翻不翻转都会被看到，所以不能有明显的「朝哪边」。
- 大小：头发顶（最高的那撮白发）在黄线，鞋底在红线，**35 格高**；宽度自然（大约 20–24 格）。人物中线对准青色竖线。
- 配色：**只用 `design/ekko_design.png` 里已有的颜色**（白发、深棕皮肤、红围巾、米色外套、深色裤子和鞋、青色发光件）。描边和定稿一样：外轮廓 1 格深色描边。
- 像素画：每格是一个 8×8 的纯色方块，硬边，没有抗锯齿、没有模糊、没有渐变；背景透明（做不到就用纯黑 `#000000`）；不要网格线、边框、文字。

给图像模型的提示词（英文，附上 `design/ekko_design.png`、`size/ekko_canvas.png` 和 `refs/` 两张）：

```text
Pixel art game sprite, one frame, chunky square pixels (every game pixel an exact 8x8 block on a 448x448 canvas = 56x56 squares), hard edges, no anti-aliasing, no blur, transparent background, no grid, no text.
Character: EKKO exactly as in the attached design sheet (white spiky hair, dark brown skin, red scarf, beige vest/jacket, dark trousers and boots, glowing teal gear and a teal glowing bat-blade), same colours (only colours that appear in the design), same 1-square dark outline, same proportions and level of detail.
Pose: standing upright and relaxed, FACING THE VIEWER (front view, not three-quarter, not side view), feet shoulder-width apart pointing forward, head straight, eyes to the viewer; one hand holds the glowing bat-blade hanging straight down beside the leg, tip near the ground; the other arm hangs naturally. The body is balanced on the vertical centre line: it must not lean, step or reach to the left or right.
Size and placement: the top of the hair on row 12, the soles on the bottom of row 46 (35 squares tall), the body centred on column 28, as marked on the attached canvas.
```

## 交回之后（Claude 做）

1. 按 8×8 方块读回游戏像素（生图原稿用 `.claude/skills/tfm2-hero-mod/scripts/regrid.py` 按它自己的格子读回），核对 35 格高、鞋底和中线。
2. `tools/art/import_ekko.py` 的 `hologram()` 改为读这张正面图（不再读侧身待机第 1 帧），生成 8 帧 × 500 毫秒的薄荷绿全息残影，写进 `league_ekko_big` 的 `r_ghost`。
3. lint 不再报 `league_ekko_r_ghost`；出蓝色方 / 红色方对比 GIF。

## 另外两个不用画

- **永恩 E 留下的本体**（`league_yone` 的 `e_body`）本来就是正面站姿，只是比落点偏右 4 格；已在 `assets/source/native/yone_cells.json` 里把它挪回中间，镜像前后基本一样。
- **小丑 R 的分身**挂在被攻击的敌方英雄身上，固定站在目标左边、面朝目标出手；不管小丑从哪边放，都是「站在目标一侧朝目标砍」，不算反，正面站姿反而不能出手。

打包：`python tools/art/pack_red_side_figures.py --out <文件夹> --zip`。

已完成（2026-10-06）：Codex 交回的正面图存为 `assets/source/red_side/ekko_front.png`，`tools/art/import_ekko.py` 的全息残影改由它生成。
