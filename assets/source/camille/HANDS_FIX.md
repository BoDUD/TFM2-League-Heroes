# 卡蜜尔：重画动作帧里的手臂和手（动作条第 1 轮修改，给 Codex 的提示词）

> 上次交回的动作条已经导入游戏，头、身体、胯、刀刃腿、每帧的位置都很好，**这些一点都不要改**。用户说「卡密尔的手部能改精致一点吗？现在太怪了」：动作帧里她的手臂画成了 1～2 格宽的黑线，手画成了三根尖指头的黑爪子，游戏里看着像小黑爪。造型图（`design/camille_design.png`）里的手臂不是这样：**深蓝的袖子 2～3 格粗、外面一圈 1 格的黑描边，手腕一道金色袖口，手是 2×2 到 3×3 的圆手套**（远侧那只举在脸旁）。造型图已经按你最初那张 65 格的图修好了手，待机和各动作最后一帧（直接用的造型图）也已经换好，不用画。
> - **只重画下表列出的帧里的两条手臂**：从肩甲往下的上臂、手肘、前臂、袖口、手。手臂以外的每一格（头、头发、脸、立领、胸甲、肩甲、胯、发光的核心、金色电路纹、刀刃腿）逐格照 `current/camille_<动作>.png`，每帧在格子里的位置和高低也不变。没列出的帧原样交回。
> - 两条手臂每帧的位置和方向照 `guide/lol_arms_<动作>.png`（英雄联盟同样的帧、同样的格子：**近侧手臂橙色**，**远侧手臂蓝色**，其余灰色）。对比图 `guide/arms_now_vs_lol_<动作>.png`：上排是现在的手臂（黑线、黑爪），下排是英雄联盟的手臂。现在的方向已经对的，保留方向，只把手臂和手画成造型图的样子。
> - 手臂的材质照 `design/camille_hands.png`（造型图里只亮出两条手臂）：
>   - 袖子：深蓝 `#1B2445`、`#283357`、`#35416D`，2～3 格粗，一圈 1 格的近黑描边 `#03010F`，描边要闭合；
>   - 袖口：手腕一道金色 `#FAC20A`（暗面 `#CF9D03` 或 `#B48200`），1～2 格；
>   - 手：2×2 到 3×3 的圆手套，深蓝 `#283357` 加一格亮一点的 `#35416D`，有描边；握拳、平伸的手或者造型图里举起的手，**不要爪子**。
>   - 两条手臂用一样的颜色（不要近亮远暗）；手臂压在身体前面时，用描边和胸甲分开；手要连在手臂上，不能有飘着的碎块。
> - 只用造型图的 49 种颜色（`design/camille_palette.png`），每一格都是严格对齐的 8×8 纯色块，透明底；脚底线在第 97 行，脚底线以下不画（躺倒的死亡最后两帧最多低 2 格）。
> - 交回 `camille_hands_fix.zip`：改过的 10 张条带（`camille_run.png`、`camille_attack.png`、`camille_attack_q.png`、`camille_attack_q2.png`、`camille_skill.png`、`camille_skill2.png`、`camille_skill2_dash.png`、`camille_ult.png`、`camille_hit.png`、`camille_dead.png`，放大 8 倍，尺寸和排版不变）、`native/` 里的 1 倍原图、`manifest.json`（每帧的格子矩形、站位点、bbox、两只手的位置）、`HANDOFF.md`、`generation_prompts.json`。

## 要重画手臂的帧

| 文件 | 帧 | 排版（列 × 行，像素） |
|---|---|---|
| `camille_run.png`（移动） | 1、2、3、4、5、6、7、8 | 4 列 × 2 行，4096×1792 |
| `camille_attack.png`（普攻（刀刃踢）） | 1、2、3、4、5 | 3 列 × 2 行，3072×1792 |
| `camille_attack_q.png`（Q 精准礼仪第一踢） | 1、2、3、4、5 | 3 列 × 2 行，3072×1792 |
| `camille_attack_q2.png`（Q 精准礼仪第二踢（下劈）） | 1、2、3、4、5 | 3 列 × 2 行，3072×1792 |
| `camille_skill.png`（W 战术横扫） | 1、2、3、4、5、6、7 | 4 列 × 2 行，4096×1792 |
| `camille_skill2.png`（E 钩索（射钩）） | 1、2、3、4、5 | 3 列 × 2 行，3072×1792 |
| `camille_skill2_dash.png`（E 冲刺 + 落地） | 1、2、3、4、5 | 3 列 × 2 行，3072×1792 |
| `camille_ult.png`（R 海克斯最后通牒（跳跃落地）） | 1、2、3、4、5 | 3 列 × 2 行，3072×1792 |
| `camille_hit.png`（受击） | 1、2 | 2 列 × 1 行，2048×896 |
| `camille_dead.png`（死亡） | 1、2、3、4、5、6、7、8 | 4 列 × 2 行，4096×1792 |

## 提示词（每张条带一样，换掉 [文件] 和 [帧]）

每张附三张图：第一张 `design/camille_design.png`，第二张 `current/camille_<动作>.png`，第三张 `guide/lol_arms_<动作>.png`（可以再附 `guide/arms_now_vs_lol_<动作>.png` 和 `design/camille_hands.png`）。

```text
Two attached images, plus the guide. FIRST: the approved pixel-art design of this character at 8x (every pixel an 8x8 block). SECOND: the current animation strip of her at 8x - keep EVERY pixel of it except her two arms. Redraw only her arms from the shoulder pads down (upper arm, elbow, forearm, wrist cuff, hand) in the frames listed, in the same place and direction as the THIRD image (League's same frames in the same cells: her near arm ORANGE, her far arm BLUE, the rest grey). Her arms exactly like the FIRST image's: dark navy sleeves (#1B2445, #283357, #35416D), two to three squares thick, inside a closed one-square near-black outline (#03010F); a gold cuff at the wrist (#FAC20A, shade #CF9D03 or #B48200), one or two squares; a small rounded gloved hand, two by two to three by three squares, navy (#283357) with a lighter #35416D square, outlined - a fist, a flat open hand or the raised hand of the FIRST image, never claws. No black sticks one square wide, no three-fingered black claws, no hand drawn apart from its arm. Both arms in the same colours (not a lighter near arm and a darker far one); where an arm crosses the body, its outline separates it from the bodice. Everything else - the head, hair, face, collar, bodice, shoulder pads, hips, glowing core, gold circuit lines and leg blades, and where each frame stands in its cell - stays exactly as in the SECOND image. Only the FIRST image's colors, every square an exact 8x8 block, transparent background, the same size and layout as the SECOND image.
File: [文件]. Frames to redraw (numbered left to right, top to bottom): [帧]. Every other frame unchanged.
```

## 交回前检查

- 和 `current/` 比：手臂以外没有一格变了（头部、身体、刀刃腿逐格相同），每帧的位置不变；
- 每只手都是有描边的圆手套，连在手臂上；没有 1 格宽的黑线手臂，没有黑爪子；
- 只用造型图的颜色，8×8 方块对齐，透明底，脚底线以下不画。
