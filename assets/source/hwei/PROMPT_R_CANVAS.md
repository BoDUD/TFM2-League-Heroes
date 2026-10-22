# 异画师 彗：大招画卷 r_canvas（给 GPT 的提示词）

> 彗的特效只差这一张：**大招「焚心绚华绘」打中英雄后，在它脚下展开的旋转画卷**（持续 3 秒，减速并持续伤害，最后炸开——炸开那张已经有了，附图 2）。
> **请用 GPT 的生图画，不要用代码拼方块。** 一张图里画 14 帧，排成 **4 列 × 4 行的格子**（从左到右、从上到下是第 1–14 帧，**最后两格留空**）。
>
> - **风格**照附图 1（Gemini 画的大招颜料团）和附图 2（大招爆炸）：同一套颜色——**深靛蓝的底、紫红和橙色的笔触、几缕金线**，像颜料画出来的：粗笔触、干笔的毛边、平涂，**不要光滑的霓虹光效**。
> - **大小和节奏**照附图 3（我补画的那一版，**只看大小怎么长、格子里放在哪里，不要照它的画法**）：第 1 帧是一个小椭圆，到第 6 帧长到最大，之后保持大小，笔触在上面慢慢旋转、闪动；**第 12–14 帧越来越亮**，中间的裂纹发白，像马上要炸开。
> - **从斜上方看的地面上的椭圆**：宽大约是高的 3 倍，**左右严格对称**（逐格对称：这张图在红色方不会镜像）。每一格里椭圆放在**格子的水平正中、偏下的位置**，所有帧的椭圆中心在同一个位置。
> - 背景**透明**（做不到就用纯黑 `#000000`）；不要网格线、边框、文字、编号；不要画人。
> - 附图 4 是英雄联盟里彗这招自己的贴图（裂纹、旋转的笔触、金线），只参考形状；附图 5 是彗在游戏里的大小（画卷在游戏里最大约 52 × 17 个游戏像素，比他宽一点）。

## 附图（压缩包 `hwei_canvas_gpt_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_style_r_paint.png` | Gemini 画的大招颜料团（4 帧） | **画风、颜色** |
| `2_style_r_burst.png` | Gemini 画的大招爆炸（画卷结束时炸开的样子） | **画风、颜色**；画卷要能接上它 |
| `3_layout_guide.png` | 4 × 4 格的示意（我补画的版本放大）：每帧椭圆的大小和位置 | **只看大小、位置、展开的节奏** |
| `4_lol_ref.png` | 英雄联盟里彗大招的贴图 | 形状参考（裂纹、笔触、金线） |
| `5_hwei_size.png` | 彗在游戏里的大小（4 倍） | 比例 |

## 提示词（附上全部五张图，一次画完）

```text
Five attached images: 1 and 2 are the STYLE to match exactly - pixel-art paint effects of the same character's ultimate (1 a spiralling paint bolt, 2 the explosion that ends this effect): chunky square pixels, flat shades, thick brush strokes with ragged dry-brush ends, dark indigo, magenta, orange and thin gold strands; 3 is a LAYOUT GUIDE only (how big the oval is in each frame and where it sits in its cell - do not copy its drawing); 4 are the game's own textures for this spell (cracks, swirling strokes, gold strands) for shapes only; 5 shows the character's size.
Create ONE pixel-art VFX sprite sheet: a 1536x1024 PNG with a transparent background (if not possible, pure black #000000), divided into a GRID of 4 columns x 4 rows of EQUAL cells (each 384x256); frames 1 to 14 in reading order (left to right, top to bottom); the last two cells (row 4, columns 3 and 4) EMPTY. No grid lines, no borders, no text, no numbers, no characters.
THE EFFECT: A SPIRALING CANVAS PAINTED ON THE GROUND, seen from above at an angle: in every cell an oval three times as wide as tall, centred across the cell and a little below its middle, at the same place in every frame. Frame 1: a small oval about 40% of its full size, just painted; frames 2-6: it spreads to its full size (about 300 px wide and 100 px tall in its cell) and then stays that size. On it: a dark indigo ink ground; magenta and orange brush strokes curling round the middle in a MIRRORED DOUBLE SPIRAL; thin gold strands between the strokes; thin cracks of light in the middle. Frames 7-11: the strokes turn a little each frame and shimmer. Frames 12-14: everything brighter frame by frame - the cracks white-hot, the strokes lighter - as if about to burst.
STRICTLY SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it). Chunky square pixels, hard edges, no anti-aliasing, no blur, no soft glow, no gradients; flat 2-3 shades in each stroke, the lit side one shade lighter; no black outline around the paint; bright enough to read on a dark battlefield (each stroke with its lightest shade, the cracks white).
Colours only from: dark indigo ink #5A5E9A, #33366E, #1C1D44, #0E0E24; magenta #FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060; orange #FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14; gold #FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416.
```

## 交回前请检查

- 一张 1536 × 1024 的图，**4 × 4 格**，第 1–14 帧从左到右、从上到下，**最后两格空**；格子之间没有画线。
- 每帧一个**左右对称**的地面椭圆（宽约是高的 3 倍），在格子水平正中、偏下，每帧位置相同；第 1 帧小，第 6 帧长到最大后不再变大；第 12–14 帧越来越亮。
- 颜色、笔触和附图 1、2 是一套；没有人物、文字、网格线；透明或纯黑背景。
- 画好后**下载到电脑的「下载」文件夹**（`C:\Users\OWNER\Downloads`），告诉 Claude 文件名或时间，Claude 会从那里读回（不会和奇亚娜的图混在一起）。

## Claude 收到后（给 Claude 看）

- 复制到 `C:/t/hw_work/gemini/g23_r_canvas.png`（或 .jpg），`tools/art/process_hwei_fx.py` 里把 r_canvas 从 DRAWN 移到 SOURCES（`("r_canvas", 14, (56, 22))`，LAYOUT `(4, 4)` 取前 14 格，对称左右），再跑 `import_hwei_fx.py`（锚点 `("feet", 9)` 按读回后的椭圆中心重新量）。
