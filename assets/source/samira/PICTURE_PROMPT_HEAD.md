# 莎弥拉 v2：头画小一点（给 Codex 的提示词）

> 附图 1 是你上次画的莎弥拉 v2（`samira-lol-refined.png`），用户选定了它的样子，但觉得**头太大**（「这头怎么这么大」）。现在从头顶到下巴占全身（头顶到脚底）的 **32%**，要改成约 **26%**。
> - **只改头的大小**：头（连头发、眼罩、耳环）整体缩小，头顶到下巴从约 350 px 缩到约 **285 px**（附图 2：红线是现在的下巴，**绿线是要的下巴**）。
> - **总高度不变**：头顶还在附图 2 最上面的灰线，脚底还在最下面的灰线。头缩小空出来的高度给**脖子、上身和腿**，人显得更修长，腿更长一点（附图 3 是英雄联盟模型的比例，看比例用）。
> - **其他全部照附图 1**：双手叉腰的姿势、背后的大剑（剑柄在左上带红穗子、剑尖在右下）、侧梳的墨绿长发和金链、眼罩和红带、绿色的眼睛、耳环、手臂纹身、深色护甲上衣和红色、金色枪套、靴子、颜色，都不要改。脸的五官照附图 1 画清楚（附图 4 是头部参考）。
> - **像素格和附图 1 一样**：每块约 8 像素，大小一致、横平竖直对齐成网格；外轮廓近黑描边；每种材质 3–4 档平涂。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，没有光晕、没有半透明边，**直接交原图那个尺寸（1024×1536）的像素图，不要再缩到别的格子大小**。
> - 不画特效、地面、影子；脚底以下什么都没有。
>
> - 交付：`outputs/samira-head/samira-v3.png`（1024×1536，**真透明背景**）；原始生成图原样放进 `outputs/samira-head/raw/`；附 `generation-prompts.txt`；**最后**写 `outputs/samira-head/HANDOFF.md`，再打包成 `outputs/samira_head_done.zip`。

## 附图（压缩包 `samira_head_pack.zip`，解压到新文件夹，按顺序附上）

| 文件 | 内容 |
|---|---|
| `refs/1_samira_v2.png` | **要改的图**：上次画的 v2，除了头的大小全部照它 |
| `refs/2_guide.png` | 尺寸线：头顶（灰，不变）、**现在的下巴（红）**、**要的下巴（绿）**、脚底（灰，不变） |
| `refs/3_samira_league_idle.png` | 英雄联盟模型的待机（看头身比例） |
| `refs/4_samira_league_head.png` | 英雄联盟模型的头部特写（五官参考） |

## 提示词

```text
Four attached images. Image 1 is THE picture to redraw: a pixel-art character (a gunslinger woman, hands on hips, a greatsword slanting behind her). Keep EVERYTHING of image 1 - the pose, the sword, the hair, the eyepatch and red strap, the green eye, the earrings, the tattoo, the dark armour top with red, the gold holster, the boots, the colours, the square size - EXCEPT ONE CHANGE: her HEAD IS TOO BIG. Draw the whole head (hair, face, eyepatch, earrings) smaller: from the top of her head to her chin about 26 % of her height (now 32 %). Image 2 is the guide on image 1: the top grey line is the top of her head and the bottom grey line her soles - BOTH STAY where they are; the red line is her chin now, the GREEN line is where her chin goes. The rows the smaller head frees go to her neck, torso and legs (she becomes a little taller-bodied, longer-legged), as the game model's proportions in image 3. Image 4 is her head close up in the game: draw the face clearly (the eye, the eyepatch, the mouth).
ONE pixel-art picture, 1024x1536 PNG, the same pixel grid as image 1 (squares of about 8 px, one straight grid), a near-black outline, 3-4 flat shades per material, no stray odd squares, no dithering, no gradients, no blur, no anti-aliasing; a genuine transparent background (every pixel fully transparent or fully opaque, no glow, no halo); deliver it at this size and grid, do not resample it to another square size. No effects, no ground, no shadow, nothing below her soles.
```

## 交回前请检查

- 头顶和脚底的位置和附图 1 一样；下巴在附图 2 的绿线附近（头顶到下巴约占身高 26%）。
- 除了头小了、身子和腿相应长了，姿势、剑、衣服、颜色都和附图 1 一样。
- 1024×1536、真透明背景、约 8 像素一格、对齐网格，没有缩成别的格子大小。
- 最后写 `outputs/samira-head/HANDOFF.md`，再打包成 `outputs/samira_head_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原图（`tools/art/design_samira_hd.py` 换成新图，PPU 2.84，删整行、脸部行列不删），量头身比，和 v2 并排给用户看。
