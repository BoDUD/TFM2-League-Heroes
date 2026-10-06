# 影流之镰 凯隐：给 Codex 的穿墙特效提示词（掠影步，2026-10-06）

> **这一份是 2 张特效图**，用在附加包 `league_kayn_form` 的「掠影步穿墙」：Q 转完后的 2 秒里，凯隐会笔直穿过地图树林里的墙；人在墙格里时，身体换成半透明的暗影剪影（已经做好，附图 `refs/kayn_wall_bodies.png`：本体、暗裔、影流各一列，左边是平时，右边是墙里）。用户：「穿墙效果和英雄联盟里面不一样 实在不行就让codex帮忙做」。
> - 英雄联盟里凯隐穿墙：**进墙时墙面上溅开一团暗影；人在墙里时周身裹着一团翻涌的暗影雾，看得出身形但很暗，身后拖着烟；出墙时又炸开一团暗影**。这两张就画这个。
> - 附图 `design/kayn_design.png`、`kayn_darkin_design.png`、`kayn_shadow_design.png`：三种形态的定稿造型（8 倍），看大小用：本体约 40 格高，暗裔约 44 格、宽 60 格，影流约 40 格高、宽 70 格。
> - 附图 `refs/kayn_fx_ghost.png`：现在掠影步脚下的那摊影子（原尺寸条，8 倍），颜色和画法照它。
> - **只画本体配色**（暗影紫转深红）：暗裔（黑红、血红、橙、淡金）和影流（靛蓝、蓝、青、淡青）两套由 Claude 按色带一档对一档换色。
> - 生图原稿也可以交（半透明边、格子比例不准都行，Claude 会转成游戏像素），每张保持等宽格子，不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），打成一个 zip（`kayn_wall_fx_done.zip`）放在 outputs 里。

## 规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火星没有黑描边，也不要用最深的颜色给形状描边**。
- **要亮**：烟用烟色带里亮的几档，每团烟有最亮一档的高光；深红火星有白色或淡粉的芯。最深一档只做很少的点缀（凯隐本身就很暗，雾太暗会和他糊成一团）。
- 颜色：
  - 本体（影子转深红）：`#FFFFFF`、`#FFC2CC`、`#FF4058`、`#D61C39`、`#8E1834`、`#46205E`、`#22163A`；
  - 暗影烟（亮的在前）：`#9A8EC8`、`#6A5C9E`、`#463A74`、`#2C2250`、`#181030`。
- **两张都左右严格对称**（以格子中线为轴）：雾是挂在人身上的循环画面，游戏不按朝向翻转；进出墙的爆开按人的位置播放，也要两边一样。
- 套在人身上的那张：格子中间留出空的人形位置（约 18 格宽、36 格高，脚底在格子底边往上 6 格），**不要画人**；雾从空位的边缘往外翻，可以有少量烟丝伸进空位的边上，但不要盖住空位中间。

---

### 1. `kayn_fx_wall_aura.png`：人在墙里（裹身暗影雾，循环），6 帧

凯隐在墙里时一直播放：一团围着人形空位翻涌的暗影雾（像从墙里渗出来的黑紫色烟），两侧和头顶往外飘出烟丝，底下一圈贴地的暗影；雾里零星几点深红火星往上飘。6 帧循环，烟丝每帧往上、往外挪一点，第 6 帧接回第 1 帧。整团约 44 格宽、52 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around smoke or sparks, BRIGHT colours (each smoke puff lit with its lightest shades - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and a shadow-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a SHADOW SHROUD around a hidden figure, 6 frames that loop: a swirling cloud of dark violet smoke wrapped around an EMPTY human-shaped space in the middle of the cell (about 18 squares wide, 36 squares tall, its feet 6 squares above the cell's bottom edge) - do not draw any person; wisps of smoke curl outward from both sides and rise above the head space, a flat ring of shadow lies on the ground round the feet; a few crimson sparks with white cores drift upward through the smoke. Each frame the wisps move a little up and outward; frame 6 leads back into frame 1. The whole cloud about 44 squares wide and 52 squares tall. EXACTLY left-right symmetric about the cell's vertical middle line.
Layout: one horizontal row of 6 equal cells, each cell 64x64 squares, image size 1536x256; the empty figure space centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kayn_fx_wall_burst.png`：进墙、出墙（暗影溅开），6 帧

进墙、出墙的那一下各播一次：一团暗影从中间炸开、往四周溅出碎烟和深红火星，再散掉。约 40 格宽、28 格高（从斜上方看，宽是高的约 1.5 倍），居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and a shadow-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a SHADOW SPLASH as a figure passes into or out of a stone wall, 6 frames: 1 a small dark violet blot with a crimson-white flash in its middle; 2 the blot bursts outward into a ring of thick violet smoke with crimson sparks; 3 the full splash, about 40 squares wide and 28 squares tall (an ellipse seen from above at an angle), jagged smoke tongues flying outward, sparks with white cores; 4 the smoke breaks into separate wisps drifting outward and up; 5 thinner wisps, a few sparks; 6 the last faint wisps. EXACTLY left-right symmetric about the cell's vertical middle line.
Layout: one horizontal row of 6 equal square cells, each cell 48x48 squares, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

## 附图清单（打包在 `kayn_wall_pack.zip`，`tools/art/pack_kayn_wall.py` 生成，只在本地）

| 文件 | 内容 |
|---|---|
| `PROMPTS_WALL.md` | 这一份 |
| `design/kayn_design.png`、`kayn_darkin_design.png`、`kayn_shadow_design.png` | 三种形态的定稿造型（8 倍） |
| `refs/kayn_fx_ghost.png` | 现在掠影步脚下的影子（原尺寸条，8 倍） |
| `refs/kayn_wall_bodies.png` | 已做好的墙里暗影剪影（本体、暗裔、影流；左平时、右墙里） |
