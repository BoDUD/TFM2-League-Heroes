# 布里茨：造型返修（第 1 步第 2 轮，给 Codex 的提示词）

> 用户选了 **B 版**（9×9 圆顶、3×3 眼睛），要你在**同一尺寸、同一位置**上返修四处（`blitzcrank/issues_B.png` 里标了 1、2、3、3h）：
> 1. **烟囱**：现在是两个金色圆环插在细杆上，像两只耳朵。改成原画那样的**钢色短烟囱**：底宽约 5 格、顶宽 4 格的圆锥/圆筒，3–4 档钢色（左边亮），顶上一圈细金边和 2 格的深色开口；近处（画面左）的稍大，远处的被圆顶挡住一部分；烟囱顶仍是最高点（第 56 行）。
> 2. **胸口炉门**缩小：钢圈约 **12 格宽、12 格高**、2 格粗（左上亮、右下暗），里面青铜金色圆盘和一道深色闪电纹；周围多露出一些带铆钉的金色锅炉。
> 3. **手臂**要看得清：每条手臂分成三段，用描边或深色缝隔开——**肩块**（金色，一个小银钢刺）、**前臂**（一两块金色方块，一个钢螺丝头）、**拳头**（三块叠着的方块手指，之间有暗缝，外侧 2–3 个钢指节螺栓）；手臂和身体重叠的地方留 1 格深色缝。近处手臂（画面左）垂在近侧前面，拳头在近处腿边；远处手臂在远侧；两只拳头最低一行至少在脚底线上方 2 格。**3h 黑软管**：从背后绕过两边肩膀进手臂的清楚的环，2 格粗（近黑 + 一道深灰高光、两端小钢箍），不是黑团。
> 4. **金色更暖更深**：照 `blitzcrank/palette_from_picture.png`，5–6 档从深棕金到浅高光（#672d01、#984b01、#bc6802、#dd8702、#f9af07、#fddc36 或很接近），像原画那样用：暗的一半盖住背光面（锅炉右下、圆顶下面、手臂下面、拳头方块的内侧），最亮的只在左上边缘和小高光；不要大片最亮的黄。钢色 3–4 档。
>
> **不要改**：头（9×9 圆顶和中间竖棱、两只 3×3 眼睛——浅粉加中间一格白、深色眼窝、下面的钢领口）、腿和脚、姿势、朝向（3/4 正面朝右）。大小和位置也不变：烟囱顶到脚底约 44 格、约 46 格宽，脚底最低一行在第 99 行（y=792–799），两脚中间在第 64 列（x=512）。
>
> 交付 `blitzcrank_design_B2.png`（1024×1024）和 `blitzcrank_design_B2_1x.png`（128×128），附 `HANDOFF.md`（哪里没做到）和色板，最好打成 `blitzcrank_design_B2_pack.zip` 放在 outputs 里。每个像素严格 8×8 同色块，透明度只有 0/255，不超过 24 色。

## 附图（都在压缩包的 `blitzcrank/` 里）

| 文件 | 内容 |
|---|---|
| `design_B_current.png` / `design_B_current_1x.png` | 你上一轮交的 B 版（8× / 1× 128 画布）：**头保留**，其余按下面改 |
| `blitzcrank_source.png` | 用户选的原画 A：烟囱、手臂、软管、金色都照它 |
| `issues_B.png` | B 版放大 12 倍，标了四处问题（1 烟囱、2 炉门、3 手臂、3h 软管），右边是原画 |
| `quality_bar.png` | main 里的大块头英雄（游戏里现在的样子 ×8），细节和明暗的标准 |
| `palette_from_picture.png` | 原画的 6 档金色（各占金色面积的比例）和 4 档钢色 |

## 提示词

附图顺序：`design_B_current.png`、`blitzcrank_source.png`、`issues_B.png`、`quality_bar.png`、`palette_from_picture.png`。

```text
Attached images. FIRST: the current game-size design of this character (design B, 46x44 squares at 8x) - the user approved its HEAD and wants it FIXED in four places. SECOND: the approved illustration - the look to match. THIRD: the four problems marked on the design (numbers 1, 2, 3, 3h), the illustration beside it. FOURTH: big heroes of this game at game size, approved by the user - the quality bar (detail, shading, lit edges). FIFTH: the gold and steel shades of the illustration with how much of the gold each shade covers.
Task: redraw design B at the same game size and place - about 44 squares from the top of the smokestacks to the soles and about 46 squares wide, the soles' lowest row on square row 99 (y=792-799), the feet's middle on column 64 (x=512), true pixel art shown 8x, every pixel one crisp 8x8 square on one grid. KEEP exactly: the head (the 9x9 gold dome with its middle ridge, the two 3x3 eyes - pale pink with a white centre square - in dark sockets, the steel collar under it), the legs and feet, the pose, the facing (3/4 front, facing right). FIX:
1. SMOKESTACKS (marked 1): two short gunmetal STEEL stacks rising behind the head as in the SECOND image - each a short cone or cylinder about 5 squares wide at its base and 4 at its top, 3-4 steel shades (lit on the left), a thin gold rim round the top with a dark 2-square opening; the near stack (image left) a little bigger, the far one partly behind the dome; NOT gold rings on thin stalks. Their tops stay the highest point (row 56).
2. CHEST PORT (marked 2) smaller: the steel ring about 12 squares across and 12 tall, 2 squares thick (light steel on the upper left, darker on the lower right), the bronze-gold disc inside with one dark zigzag lightning seam; more gold boiler with a few rivets shows round it.
3. ARMS (marked 3) that read at this size: each arm in three clear parts separated by the outline or a dark seam - the big SHOULDER block (gold, a small silver pyramid spike), the FOREARM (one or two gold blocks with a steel screw head) and the FIST (three stacked square finger blocks with darker seams between them and 2-3 steel knuckle bolts on the outer side). Where an arm overlaps the body a 1-square dark gap separates them. The near arm (image left) hangs in front of his near side with its fist down by the near leg; the far arm (image right) hangs at the far side; both fists' lowest row at least 2 squares above the soles. 3h - the BLACK HOSES: clear ribbed loops 2 squares thick (near-black with a dark grey highlight band, a small steel cuff at each end) from the back over each shoulder into the arm, not dark blobs.
4. WARMER, DEEPER GOLD everywhere (FIFTH image): 5-6 shades from deep brown-gold to a pale highlight (#672d01, #984b01, #bc6802, #dd8702, #f9af07, #fddc36 or very close), used the way the illustration uses them - the darker half covers the shadow side (the right and lower part of the boiler, under the dome, under each arm, the inner faces of the fist blocks), the lightest only on upper-left edges and small highlights; no large flat areas of the lightest yellow. Steel in 3-4 shades of the FIFTH image.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 24 colours; ONE 1-square near-black outline round the whole silhouette and inside it every material in its own dark, mid and light shade plus a small highlight (hue-shifted darks; never a second black ring inside the outline); every square describes something (a rivet, a screw head, a spike, a seam, a knuckle bolt, a band of a hose, the lightning seam) - no random specks, no dithering, no gradients, no noise. The eye colours (pale pink, white) only in the eyes. Nothing below the soles. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: the head unchanged; about 44 squares tall and 46 wide; soles on row 99; steel smokestacks (not rings); the port ring about 12 squares; each arm reads as shoulder - forearm - fist; the hoses are clear loops; the gold has 5-6 shades and the dark ones cover the shadow side; at most 24 colours; one outline ring.
```

## 交回前自查

- [ ] 头和上一轮 B 版一模一样（圆顶 9×9、眼睛 3×3）；
- [ ] 烟囱是钢色短圆锥、顶上金边和深色开口，不是金圈；炉门钢圈约 12 格；
- [ ] 每条手臂看得出肩块—前臂—拳头三段，黑软管是清楚的环；
- [ ] 金色 5–6 档，暗的盖住背光面，没有大片最亮的黄；
- [ ] 约 44 格高、46 格宽，脚底在第 99 行，下面没有像素；严格 8×8，不超过 24 色，一圈描边。
