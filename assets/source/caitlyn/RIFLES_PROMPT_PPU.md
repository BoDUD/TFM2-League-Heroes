# 凯特琳：步枪画直的四个角度（给 Codex 的提示词）

> 凯特琳的动作帧已经画好了，但每一帧里的步枪角度、粗细都不一样，像素台阶也不整齐，枪看起来是"歪"的。这次**只画步枪**，画**四个角度**，之后每一帧的枪都换成这四把（转 90° 和左右翻转能凑出 16 个方向）：
> 1. **水平**（枪口朝右）
> 2. **每横走 2 格升高 1 格**（约 26.6°，枪口朝右上）
> 3. **每横走 2 格降低 1 格**（约 −26.6°，枪口朝右下）
> 4. **每横走 1 格升高 1 格**（45°，枪口朝右上）
>
> 这几个角度的像素台阶是**完全规则的**：水平就是一整排；1:2 就是每 2 格上 1 格（2、2、2……绝不出现 1 或 3）；1:1 就是每格斜走一格。**枪管的每一条边都必须严格按这个台阶走，整把枪是一条笔直的线，不能弯、不能抖、不能一段粗一段细。**
>
> - **步枪照定稿设计图**（`refs/1_design.png`、`refs/2_design_rifle.png`，8 倍放大）：金色枪身、象牙白护板、青蓝色能量线、**两个金框蓝镜片的圆形瞄具**（在枪身上方）、细长的枪管和枪口、镂空的枪托。英雄联盟的步枪特写（`refs/3_league_rifle.png`）只看结构。
> - **长度**：从枪托末端到枪口 **59 格**；枪管约 2 格粗，枪身（有瞄具的部分）约 5–6 格粗，枪托约 6 格。四把枪**除了角度以外完全一样**：同样长、同样粗、同样的瞄具和配色。
> - **瞄具永远在枪的上方**（往上斜的、往下斜的、水平的都一样：瞄具朝天），这是同一把枪在不同角度，不是翻面。
> - **模板**（`templates/rifles.png`，1536×1024，2×2 四格）：每格里**红线从枪托末端到枪口**，红点每 2 格一个，用来数台阶。枪就沿着这条红线画。
> - **像素块**：每块 **8 像素**，横平竖直对齐成网格；外面一圈 1 格宽的近黑描边；每种材质 3–4 档平涂，不要零散杂色格、不要渐变、不要模糊和抗锯齿。
> - **背景**：真透明（透明度只有 0 或 255）；做不到就用**纯白 #FFFFFF** 平涂，枪外面不要光晕。模板上的红线、红点、文字、边框都不要留在交付图里。
> - 不画手、不画人、不画特效。
>
> - 交付：`outputs/caitlyn-rifles/rifles.png`（1536×1024，**和模板一样的四格布局**，每把枪在模板红线的位置上）；原始生成图放进 `outputs/caitlyn-rifles/raw/`；附 `generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/caitlyn_rifles_done.zip`。

## 提示词

附图：`templates/rifles.png`、`refs/2_design_rifle.png`、`refs/1_design.png`、`refs/3_league_rifle.png`。

```text
Four attached images. Image 1 is a TEMPLATE sheet, 1536x1024, four cells: in each a RED LINE runs from a rifle's stock end to its muzzle, with a red dot every 2 squares; cell 1 is level, cell 2 climbs exactly 1 square for every 2 squares across, cell 3 falls exactly 1 square for every 2 across, cell 4 climbs exactly 1 square for every 1 across. Image 2 is the approved pixel-art rifle (8x, every square one pixel, in the character's hands): copy its LOOK and COLOURS - a gold body, ivory-white panels, glowing cyan energy lines, TWO round scopes with gold rims and blue lenses on top of the body, a long thin barrel, an open-frame stock. Image 3 is the whole approved character (8x) for the colours. Image 4 is the game's 3D rifle: its structure only.
Create ONE 1536x1024 pixel-art sheet with a genuine transparent background (every pixel fully transparent or fully opaque; if impossible, flat pure white with no glow), the SAME four-cell layout: in each cell draw the rifle lying exactly along that cell's red line, the stock's end at the line's start, the muzzle at its end - 59 squares long, the barrel about 2 squares thick, the scoped body about 5-6, the stock about 6. The four rifles are THE SAME RIFLE at four angles: the same length, thickness, scopes and colours, the scopes ALWAYS on the upper side. Every edge of the barrel and body follows the cell's slope with perfectly regular pixel steps (level: one straight row; 1 in 2: steps of exactly 2 squares; 1 in 1: steps of exactly 1 square) - one dead-straight rifle, no bends, no wobble, no thickness changes.
THE PIXEL GRID: every square the SAME size, 8 px, aligned on one straight grid; a 1-square near-black outline; 3-4 flat shades per material; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing, no glow.
Remove every template mark: no red lines, dots, text or cell borders in the result. No hands, no character, no effects.
```
