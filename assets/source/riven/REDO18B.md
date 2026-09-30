# 锐雯 18 帧：第二轮返修（给 Codex）

> 第一轮（`riven_redo18_complete`）把剑都放回了手里、手臂连到肩膀、每帧一整块，**这些保留**。用户看过后选了“再返修一轮”，只改三件事：
> 1. **手臂太细**：现在是肤色 1 格细线加描边，像铁丝，有的横穿胸口压在衣服上。
> 2. **剑是旋转贴上去的**：剑身边缘一圈灰色毛刺、锯齿（Q2 第 5、6 帧最明显）。
> 3. **颜色和前后帧不一致**：改过的帧肤色线条多、整体偏橙，和同一动作没改的帧放在一起不像同一个人。
> 交回：`strips/riven_<动作>.png`（7 张整条，只改 18 帧，其他帧与 `now/` 逐格一样）、`effects/`（剑的位置变了的帧，刀光跟着调）、`manifest.json`（改过的帧的 `head_origin`、`head_rotation_clockwise`、`sword`）、`HANDOFF.md`。

## 附图

| 文件 | 用法 |
|---|---|
| `design/riven_native.png` | **第一张图**：手臂、剑、衣服、颜色全照它 |
| `now/riven_<动作>.png` | 第一轮的 7 条动作：在它上面改这 18 帧 |
| `cards/<序号>_<动作>_<帧>.png` | 每帧一张：定稿 / 同一动作没改的帧 / 第一轮，写了这一帧要修什么 |
| `refs/arms_design.png` | 定稿的手臂放大，标了颜色 |
| `refs/swords.png` | 现有没改的帧（整帧），里面的断剑各种角度都有：找角度最接近的直接复用剑的像素，或照它逐格画 |
| `refs/overview.png` | 第一轮按平时看图的大小（3 倍），★ 是这 18 帧 |
| `fx_now/` | 第一轮的特效 |

## 要求

1. **姿势不变**：第一轮每帧剑的位置和角度、手的位置、手臂的走向、腿，都保留（它们已照原版）。
2. **手臂照定稿画**：连描边 3–4 格粗，里面至少 2 格颜色；近手是肤色加白绷带，手腕到拳头是棕色护腕；握剑那只手的肩上有棕色肩甲，拳头握住棕色剑柄。不要只用肤色画 1 格的线；手臂不要横穿胸口压在衣服上，被身体挡住的部分就不画。
3. **剑不要旋转像素**：断剑的大小、形状、颜色照定稿。角度和 `refs/swords.png` 里某把剑接近（相差 20° 以内）的，直接复用那把剑的像素；否则照定稿逐格重画成需要的角度：直的刃口、一圈描边、刃身几条纯色带、绿色符文一条线，没有毛刺、锯齿、孤立的灰点。
4. **颜色照同一动作没改的帧**：棕色皮衣、深绿布、腰带、皮肤露出的地方和它们一样；肤色只出现在定稿里露皮肤的地方。
5. 规则不变：只用定稿的 27 种颜色（#1C0903 #1E1319 #24181F #2D1D1C #272720 #163A22 #293828 #3F2A24 #493328 #593C2C #434A46 #68432C #426E3B #7E4F30 #3E8E48 #996B3D #A8643F #867469 #CB8053 #C79860 #A89588 #E39F6B #BBAA9C #D0BFB0 #FBC697 #F6EADB #FFFFFF）；8×8 纯色块；透明度只有 0 和 255；一圈描边；头每帧原样贴 `design/head_master_1x.png`；脚底线以下没有像素；每帧连成一块；剑握在看得见的拳头里，拳头连着手臂连到肩膀。
6. 特效：剑的位置变了的帧，刀光跟着剑走；其他格子原样。

```text
Round 2 on 18 frames of this pixel-art character's animation (the strips under now/). Keep every pose of round 1: the sword's place and angle, the hands, the direction of the arms, the legs. Fix only three things, copying the FIRST image (the approved design at 8x): (1) ARMS as thick as the design's: 3-4 squares wide with the outline, at least 2 colour squares inside; the near arm skin with white bandage wraps and a brown leather bracer from wrist to fist; the sword arm with the brown shoulder guard and a fist round the brown grip - never a 1-square skin stroke, never an arm drawn as a line across the chest over the clothes. (2) The SWORD never rotated pixel by pixel: reuse the pixels of the closest-angle sword in refs/swords.png (within 20 degrees), otherwise redraw the design's broken sword square by square at the needed angle - straight edges, one outline, flat colour bands, the green rune as one line, no fringes, no jaggies, no stray grey squares; same size as the design's. (3) COLOURS like the untouched frames of the same action: brown leather top, dark green cloth, belt, skin only where the design shows skin. Only the design's colours, every pixel an 8x8 block, alpha 0 or 255, one outline, the head master pasted unchanged, nothing below the feet line, every frame one connected piece.
```

## 交回前自查

- 按 `refs/overview.png` 的大小（3 倍）看每条动作：改过的帧和前后帧颜色、粗细一致，手臂不是细线，剑没有毛边。
- 18 帧以外逐格不变；每帧连成一块；`manifest.json` 记了改过的帧的 `sword`。
