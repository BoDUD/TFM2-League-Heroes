# 锐雯：两把剑各 8 个角度（给 Codex 的提示词）

> 上一包画的锐雯设计图（`riven-A.png`）人物已经定稿，**人物不改**。问题在剑：设计图里那把断剑太大了，开大的时候才有那么长；而且一把剑只靠旋转，打起来每个角度都一样、还会挡住脸。这次**只画剑**：
> - **平时的断剑**：照她以前游戏精灵里那把（附图 1），宽、厚、中间断开、断口锯齿，剑身深灰、边缘银亮、剑格附近几道绿色符文，剑柄缠皮。**从剑柄末端到剑尖约 31 格，剑身约 10 格宽**。
> - **开大的重铸剑**：**同一把断剑**（同样的剑柄、剑格、符文、断口），断口外接上**亮绿色的能量剑刃**（附图 2、5），**从剑柄末端到剑尖约 52 格**；能量剑刃亮绿到浅绿，中间一条接近白色的亮线，边缘是实心的深绿格（不要半透明发光）。
> - **每把剑画 8 个角度**，正好对应 4 张模板（每张 2×2 = 4 个角度）：`templates/normal_1.png`、`normal_2.png` 是平时的断剑，`reforged_1.png`、`reforged_2.png` 是重铸剑。每一格里：
>   - **红线**从剑柄末端一直到剑尖，剑就沿着这条线画，**剑尖碰到红线的尽头，剑柄末端碰到红线的起点**；
>   - **蓝圈**是她握剑的拳头的位置（剑柄的中间），**短红横线**是剑格的位置；
>   - 角度写在每格左上角（从指向右边起，逆时针量）。**8 把剑除了角度以外完全一样**：同样的长度、宽度、剑柄、符文、断口和配色，只是转了方向（重新画，不是把一张图拉斜：每个角度都要是干净的像素块，剑刃的边不要锯齿乱跳）。
> - **剑的朝向**：剑刃锋利的一边朝**红线的左手边**（从剑柄看向剑尖时的左边），8 个角度都一样，不要翻面。
> - **像素块**：大小一致的方块，**每块 8 像素**，横平竖直对齐成网格；剑的外面**一圈 1 块宽的近黑描边**；剑身 3–4 档平涂（深灰、中灰、银亮边），符文亮绿，不要零散的单个杂色格。附图 4 是她的定稿设计图（8 倍，一格 = 一个像素），**颜色照它**（剑柄的皮、金属的灰、符文的绿）。
> - **背景**：交付图要**真透明背景**，每个像素透明度只能是 0 或 255，剑外面不要任何柔光、光晕、半透明边。**模板上的红线、蓝圈、文字、格子边框全部不要留在交付图里**。
> - 不画手、不画人、不画特效、不画影子。
>
> **第三张（可选）**：`riven-A-normal.png`：把附图 4（定稿设计图）里那把大剑去掉，换成**平时的断剑**，握在同一只手里、角度照模板的 35.5°（第 2 格），剑柄在原来的拳头里。**人物的每一格都不要动**；原来被大剑挡住的地方（如果有）按周围补齐。1024×1024 真透明背景，每块 11 像素，和附图 4 的网格对齐。
>
> - 交付：`outputs/riven-swords/normal_1.png`、`normal_2.png`、`reforged_1.png`、`reforged_2.png`（都是 1536×1024，**和模板一样的布局**，每格的剑放在模板红线的位置上，真透明背景），可选的 `riven-A-normal.png`；原始生成图原样放进 `outputs/riven-swords/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/riven_swords_done.zip`。

## 附图（在压缩包 `riven_swords_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_old_sword.png` | 她以前的游戏精灵（10 倍），剑在右下 | **平时断剑的形状、大小** |
| `refs/2_old_reforged.png` | 同一帧开大时（10 倍） | **重铸剑**的样子 |
| `refs/3_league_blade.png` | 英雄联盟里的断剑特写 | 断口、符文、剑柄的形状 |
| `refs/4_design_colours.png` | 定稿的设计图（8 倍） | **颜色**；第三张的底图 |
| `refs/5_reforged_style.png` | 上一包画的重铸剑（太大，**只看风格**） | 能量剑刃的画法 |
| `templates/normal_1.png` … `reforged_2.png` | 8 个角度的模板（绿底） | **每格剑的位置、长度、角度** |

## 提示词（每张模板一次）

附上这一张模板和 `refs/1`–`5`。

```text
Six attached images. Image 1 is a TEMPLATE sheet, 1536x1024, split into 4 cells; in every cell a RED LINE runs from the end of a sword's pommel to its tip, a BLUE CIRCLE marks where the fist holds the grip, a SHORT RED CROSS-LINE marks the crossguard, and the angle is written in the corner. Image 2 is a small game sprite (10x) of a swordswoman holding her BROKEN greatsword low in front: copy that sword's SHAPE and PROPORTIONS. Image 3 is the same sprite with the sword REFORGED: a bright green energy blade grows out of the break. Image 4 is a 3D close-up of the broken sword: the jagged break, the green runes near the guard, the leather-wrapped grip. Image 5 is the approved pixel picture of her (8x): copy its COLOURS. Image 6 is an earlier reforged sword: STYLE ONLY, it is far too big.
Create ONE pixel-art sheet, 1536x1024 with a genuine transparent background (every pixel fully transparent or fully opaque, no glow), the SAME layout as image 1: in each of the 4 cells draw <THE BROKEN SWORD / THE REFORGED SWORD> lying exactly along that cell's red line - the pommel end at the line's start, the tip at the line's end, the grip under the blue circle, the crossguard on the short cross-line. The four swords are THE SAME SWORD turned to four angles: the same length, width, grip, guard, runes, break and colours, the sharp edge always on the LEFT of the line when looking from the pommel to the tip; each drawn cleanly at its angle on the pixel grid (not a stretched or rotated copy).
THE BROKEN SWORD: wide and thick, broken in the middle with a jagged break, dark grey with bright silver edges, a few glowing green runes near the crossguard, a leather-wrapped grip; about 31 squares from pommel to tip, the blade about 10 squares wide.
THE REFORGED SWORD: the same broken sword with a bright green ENERGY BLADE grown out of the break, light green to pale green with a near-white line along its middle, solid dark green squares at its edges (no translucent glow); about 52 squares from pommel to tip.
THE PIXEL GRID: every square the SAME size, 8 px, aligned on one straight grid; a 1-square near-black outline around each sword; 3-4 flat shades per material; no stray single odd squares, no dithering, no gradients, no blur, no anti-aliasing.
Remove every template mark: no red lines, no blue circles, no text, no cell borders in the result. No hands, no character, no effects, no shadow, no background.
```
