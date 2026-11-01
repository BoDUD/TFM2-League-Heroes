# 暗影狼：大招的小狼（侧身版，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 上一包的小狼（`r_pack`）是**正面朝着我们**画的，游戏里没法让它转向敌人。用户要求：**召唤出来的两只小狼要面向敌人，左右两只都面向敌人**。所以这次只画**一只小狼**，**侧身 3/4 朝右**，和大狼定稿（`0_design.png`）同一个角度。朝左的那只我自己左右翻转做，两只小狼的位置也由我来摆。
> - 小狼的样子照 `1_front_pups.png`（你上次画的小狼，放大 8 倍）和 `0_design.png`（大狼定稿，放大 4 倍）：
>   - **只有一个头**的小暗影狼；
>   - 灰蓝色的毛，胸口和腮边白毛；
>   - 脖子后面一小撮紫色鬃毛，鬃毛里一两个墨绿小尖刺；
>   - 尖耳朵、粉色内耳，**一只看得见的青色发光眼睛**（3/4 侧身，远处那只眼睛被挡住或只露一点）；
>   - 张开的粉色嘴、奶黄色小尖牙；
>   - 四条短腿、黑色弯钩爪，蓬松的尾巴、尾尖发黑。
>   - 画法照大狼定稿：像素格、近黑色描边、平涂 3–4 档，不要 3D 光影。
> - **6 个姿势画在一张图上**：3 列 × 2 行，每格 **400 × 300 px**，整张 **1200 × 600 px**。
>   - **每格 12 px**，网格从每格左上角对齐（整张图也从左上角对齐）。
>   - 每格里红线是地面（**格子顶往下 276 px**），小狼脚踩在红线上。
>   - **站着的时候小狼约 26 格宽、18 格高**，6 个姿势里身体、头、腿的大小都一样。
> - **参考图 `2_refs.png`** 是峡谷里小暗影狼自己的 3D 模型、自己的动作，已经摆在同一张图、同一个格子、同样大小和位置上（`2_refs_<k>_<名字>.png` 是每一格放大 2 倍）。
>   - 姿势、腿、尾巴、头的角度**照参考图**。
>   - 长相和颜色**照小狼和大狼的定稿**。参考图的模型是棕色的旧皮肤，**不要照它的颜色**。
> - **背景透明**（alpha 只有 0 和 255），不要阴影、不要地面、不要特效（不要爪痕、烟、光）、不要文字、不要网格线和红线。

## 6 个姿势（从左到右、从上到下）

| 格 | 名字 | 姿势 |
|---|---|---|
| 1 | stand | 站着龇牙低吼：四条腿压低，头往前伸 |
| 2 | breath | 喘气：和 1 几乎一样，胸口低一格、嘴张大一点 |
| 3 | crouch | 扑之前缩身蓄力：坐到后腿上，头压低 |
| 4 | lunge | 往前扑咬：身子拉长贴地往右冲，嘴张到最大 |
| 5 | recover | 咬完往回收：尾巴翘起，嘴合上一点 |
| 6 | settle | 站回原地：回到低伏的样子，头往前 |

## 提示词（一次画完整张）

上传：`2_refs.png`（姿势和布局）、`1_front_pups.png`（小狼的样子）、`0_design.png`（画法和颜色）。**用 image_gen 画。**

```text
Attached: A the layout and the POSES - a 1200x600 sheet of 3 columns x 2 rows of 400x300 cells, each cell a 3D render of the Rift's small murk wolf in one pose, on a 12 px grid, the red line in each cell its ground (276 px below the cell's top); B the approved small wolf pup of this character seen from the FRONT (its look: ONE head); C the approved big two-headed murk wolf (the style and colours).
Draw with the image generator ONE 1200x600 pixel-art sprite sheet with a real transparent background (alpha only 0 or 255): the SAME small one-headed murk wolf pup in each of the six cells, seen from the SIDE at a 3/4 view FACING RIGHT (the same angle as image C), in the pose of the render in that cell (copy the pose, the legs, the tail, the head's angle and the place in the cell - never the render's brown colours or 3D shading).
The pup: ONE wolf head (never two), slate-blue fur with a lighter belly and a white chest and cheek ruff, a small tuft of dark purple mane behind its neck with one or two tiny dark green-black thorns, upright pointed ears with pink insides, ONE visible glowing cyan eye on the near side (the far eye hidden or a sliver), an open pink mouth with tiny cream-yellow fangs, four short sturdy legs with hooked black claws, a bushy tail with a near-black tip. About 26 squares wide and 18 tall standing; the same body, head and leg sizes in all six poses.
Every square exactly 12 px, on one straight grid from the sheet's top-left corner; the paws on each cell's red line. Style of image C: chunky low-resolution game pixel art, one continuous near-black outline, flat 3-4 shades per material, no anti-aliasing, no gradients, no dithering, no stray single squares.
Cells, left to right, top to bottom: 1 STAND - crouched low on four legs, head forward, snarling with its fangs bared. 2 BREATHE - the same stance, the chest a square lower, the mouth a little more open. 3 WIND UP - drawn back on its hind legs, the head low, about to spring. 4 LUNGE - stretched long and low toward the right, the jaws wide open at the front. 5 PULL BACK - coming back from the lunge, the tail up, the mouth closing. 6 SETTLE - back in its low stance, head forward.
No effects (no claw slashes, no smoke, no glow halo, no motion lines), no shadow, no ground, no background, no text, no grid lines, no red lines, no cell borders.
```

## 交回

- `outputs/murkwolf-pups/murkwolf-pups.png`：1200 × 600、真透明背景、每格 12 px。
- 原始生成图原样放进 `outputs/murkwolf-pups/raw/`。
- `generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**（我自己按格子读）。
- 最后写 `outputs/murkwolf-pups/HANDOFF.md`，打包成 `outputs/murkwolf_pups_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/murkwolf/codex_pups/`，先量实际的格子，按 12 px 读回每格（小狼约 26 × 18 游戏像素）。
- `tools/art/import_murkwolf_fx.py` 把两只小狼摆进大表的 `r_pack_r`（两只都朝右，站在它身体两边），`r_pack_l` 是整张左右翻转。
- 动画从缩身开始：crouch → lunge → recover → settle → stand / breath 循环。tft.dll 在它每次攻击时重新挂上，让扑咬和小狼的咬对上。
- 骨架包：`tools/art/pack_murkwolf_pups.py`（峡谷小暗影狼 `sru_murkwolfmini` 的模型和动作，Map11.wad.client）。
