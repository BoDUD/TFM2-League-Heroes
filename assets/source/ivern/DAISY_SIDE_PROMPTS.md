# 小菊：四分之三侧面、朝右（给 GPT 的提示词）

用户（2026-11-21）：「小菊做成召唤物的话 行走动作也没做 都要补」「起码像安妮的熊那样吧 方向也不对」。

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 小菊的样子用户已经定稿（`0_daisy_front.png`：正面的石头巨人——长着青苔的绿石块和浅紫灰石面、刻着深绿色漩涡，胸口两朵小白花和一颗绿水晶，深灰色尖尖的小石头脑袋缩在两肩之间、头顶一株三叶草嫩芽，两只垂到地面的大石拳，两条短粗的石腿）。
> - 她现在是战场上会走、会打的召唤物，可图只有正面，走起来不转身、也看不出往哪走。请把**同一个小菊**画成**四分之三侧面、朝右**，像我们游戏里安妮的熊（`1_tibbers_example.png`）那样——游戏往左走时会自己把图翻过来。
> - **先画第 0 张（侧面定稿）给用户看，用户说可以，再按它画 1–14。** 1–14 每张都照第 0 张的小菊画，只换姿势。
> - 每个姿势附一张英雄联盟原版小菊的那一帧（`B_*_league.png`，四分之三侧面朝右）：**动作照它，长相照我们的定稿。**
> - 画布 **1254 × 1254**，**每格 12 px**（和定稿一样），网格从画布左上角对齐，**着地的脚底在 y = 1200**。

## 要画的 15 张

| # | 文件 | 姿势 | 附的原版 |
|---|---|---|---|
| 0 | `daisy-side-0_design.png` | 侧面定稿：站着，两只大拳头垂在身边快碰到地 | `B_00_idle_league.png` |
| 1 | `daisy-side-1_walk1.png` | 走 1：一条腿往前迈一大步着地、另一条在后面蹬地（哪条在前照原版那一帧），身子往前倾、低一格，两只拳头和腿反着摆 | `B_01_walk1_league.png` |
| 2 | `daisy-side-2_walk2.png` | 走 2：一条腿在身下撑着，另一条抬起几格往前跨（照原版），身子高一格，两只拳头在身边晃 | `B_02_walk2_league.png` |
| 3 | `daisy-side-3_walk3.png` | 走 3：和走 1 一样迈大步，但换成**另一条腿**在前（照原版），拳头也反过来摆 | `B_03_walk3_league.png` |
| 4 | `daisy-side-4_walk4.png` | 走 4：和走 2 一样，但换成另一条腿抬起往前跨（照原版），身子高一格 | `B_04_walk4_league.png` |
| 5 | `daisy-side-5_punch_up.png` | 举拳：近侧的大拳头高高举过头顶，身子往后仰一点（出拳起手） | `B_05_punch_up_league.png` |
| 6 | `daisy-side-6_punch_down.png` | 砸拳：那只拳头往右前方砸下去，砸在她身前（右边）的地上，身子往前压 | `B_06_punch_down_league.png` |
| 7 | `daisy-side-7_slam_up.png` | 双拳举起：两只大拳头一起高高举过头顶，身子挺直（第三拳起手） | `B_07_slam_up_league.png` |
| 8 | `daisy-side-8_slam.png` | 双拳砸地：两只拳头一起砸在身前（右边）的地上，深深蹲下（第三拳：震飞） | `B_08_slam_league.png` |
| 9 | `daisy-side-9_hit.png` | 挨打：身子往左后方一缩，头低一点，两只拳头往胸前收（挡） | 没有，照文字 |
| 10 | `daisy-side-10_fall.png` | 从天而降：在空中往下掉（脚底离地约 20 格），一只拳头举过头顶，两腿蜷起 | `B_10_fall_league.png` |
| 11 | `daisy-side-11_land.png` | 落地：重重落地蹲低，两只拳头撑在地上，身子往前压（之后站起来就是第 0 张） | `B_11_land_league.png` |
| 12 | `daisy-side-12_wave.png` | 挥手告别：远侧那只手抬到肩膀上方挥手（手掌张开），近侧拳头垂着，身子开始往地里沉 | 没有，照文字 |
| 13 | `daisy-side-13_slump.png` | 倒下 1：膝盖一软，往前扑倒，两只拳头撑在地上，头垂下来 | `B_13_slump_league.png` |
| 14 | `daisy-side-14_crumble.png` | 倒下 2：整个趴在地上，身子塌下去，石块散开一点 | `B_14_crumble_league.png` |

## 提示词 A：第 0 张，侧面定稿（先画这一张）

每次上传：`0_daisy_front.png`、`B_00_idle_league.png`、`1_tibbers_example.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art ROCK GOLEM "Daisy" seen from the FRONT, on a 1254x1254 canvas with 12 px squares (soles on y 1200) - a big hunched golem of mossy green stones and pale violet-grey stone faces with carved dark green spirals, two small white flowers and a small green crystal on the chest, a small dark grey pointed stone head sunk between the shoulders with a green clover sprout on top, two huge stone fists hanging almost to the ground, two short thick stone legs; B League of Legends' Daisy standing, seen in a 3/4 view facing right (only for the TURN: how her body, head, fists and legs sit when she is turned that way - never her look); C how our game draws a summon: Annie's bear Tibbers in a 3/4 view facing right.
Draw with the image generator ONE clean pixel-art picture of the SAME golem of image A turned to a 3/4 VIEW FACING RIGHT, like image B and image C: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - on one straight grid from the canvas corner; soles on y 1200.
The SAME golem as image A: the same height in squares (76 squares from the tip of the clover sprout to the soles), the same chunky proportions, the same stones, colours and carved spirals, the two white flowers and the green crystal on her chest (now seen from the front-right), the same small pointed head with the clover sprout, the same huge stone fists and short thick legs. Her chest and head face the right front; the NEAR arm and leg (nearer to us, on the image left) fully seen and bright; the FAR fist and leg (on the image right) partly behind her body and a little darker. Standing calmly, both fists hanging close to the ground, both feet on y 1200.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines.
```

## 提示词 B：第 1–14 张（每个姿势一次，换掉最后一行）

每次上传：你画的 `daisy-side-0_design.png`（用户认可的侧面定稿）、这个姿势的 `B_*_league.png`（第 9、12 张没有，只传定稿）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art golem Daisy in a 3/4 view facing right (daisy-side-0_design.png, 1254x1254, 12 px squares, soles on y 1200); B League of Legends' Daisy in this pose, 3/4 view facing right (the POSE only: copy how her body, legs and fists move - never her look).
Draw with the image generator ONE clean pixel-art picture of the golem of image A in the POSE below (as image B shows it), still in a 3/4 view facing right: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px on one straight grid from the canvas corner; the feet that stand on the ground on y 1200.
The SAME golem as image A: the same size in squares, the same stones, colours, spirals, flowers, crystal, head and clover sprout, the same huge fists and short thick legs - only the pose changes. The fists and legs keep their size and shape in every pose (never longer, thinner, bigger or smaller); a raised fist stays inside the canvas.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no dust, no shockwave, no cracks, no motion lines, no clods), no background, no ground, no shadow, no text, no grid lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- 1 walk1: `WALK 1 - a heavy step, the legs as in image B: one leg reaching forward with its foot landing on y 1200, the other pushing off behind, the body leaning a little forward and one square lower, the fists swinging against the legs.`
- 2 walk2: `WALK 2 - the legs as in image B: one leg under the body carrying her, the other lifted a few squares off the ground swinging forward, the body one square higher, both fists swaying close to her sides.`
- 3 walk3: `WALK 3 - the same heavy step as WALK 1 but with the OTHER leg in front (as in image B), the other leg pushing off behind, the fists swinging the other way, the body one square lower.`
- 4 walk4: `WALK 4 - the same as WALK 2 but with the OTHER leg lifted and swinging forward (as in image B), the body one square higher, both fists swaying close to her sides.`
- 5 punch_up: `RAISE A FIST - the NEAR fist raised high above her head, the body leaning back a little, the far fist hanging, both feet on the ground.`
- 6 punch_down: `SMASH - that fist smashed down to the ground in front of her on the image right, the body pressing forward and down, both feet on the ground.`
- 7 slam_up: `BOTH FISTS UP - both huge fists raised high above her head together, the body upright, both feet on the ground.`
- 8 slam: `SLAM - both fists slammed into the ground in front of her on the image right together, crouching deep.`
- 9 hit: `FLINCH - shrinking back toward the image left, the head lowered, both fists drawn in before her chest as a guard, both feet on the ground.`
- 10 fall: `FALLING - in the air, dropping down (the soles about 20 squares above y 1200), the near fist raised above her head, both legs tucked under her.`
- 11 land: `LANDING - landed hard, crouching low on bent legs, both fists planted on the ground in front of her, the body pressing forward.`
- 12 wave: `WAVE GOODBYE - the FAR hand raised above her shoulder, open, waving, the near fist hanging, the body starting to sink: everything below her knees hidden under y 1200 (cut off flat at y 1200).`
- 13 slump: `COLLAPSING - the knees giving way, falling forward toward the image right, both fists propped on the ground, the head hanging.`
- 14 crumble: `COLLAPSED - lying flat on her front on the ground (her lowest squares on y 1200), the body slumped, a few stones loosened from her back.`

## 交回前请检查

- 15 张都是 image_gen 画的；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样）。
- 第 0 张和正面定稿是**同一个小菊**：高 76 格（嫩芽尖到脚底）、同样的石块、颜色、漩涡、两朵白花、绿水晶、尖脑袋和三叶草嫩芽、同样大的拳头、同样短粗的腿；**四分之三侧面朝右**（胸口、脸朝右前方）。
- 1–14 每张都是第 0 张的同一个小菊，只换姿势；拳头、腿的大小和形状每张都一样；着地的脚在 y 1200（第 10 张在空中、第 12 张往地里沉、第 14 张趴在地上除外）。
- 所有图没有特效、没有地面、没有阴影、没有网格线。

## 交付（`outputs/daisy-side/`）

- `daisy-side-0_design.png` … `daisy-side-14_crumble.png`（15 张，名字照上表）；
- 原始生成图原样放 `outputs/daisy-side/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/daisy_side_done.zip`。
- 第 0 张画完先停，给用户看；用户说可以再一口气画完 1–14。

## 附图（压缩包 `daisy_side_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_daisy_front.png` | 小菊正面定稿（每格 12 px，脚底 y 1200） |
| `1_tibbers_example.png` | 我们游戏里安妮的熊：四分之三侧面朝右（站、走、挥爪），召唤物就是这样画的 |
| `B_00_idle_league.png` … `B_14_crumble_league.png` | 英雄联盟原版小菊每个姿势的那一帧（四分之三侧面朝右）：只照动作 |

## Claude 收到后（给 Claude 看）

- 量格子（约 12 px），按格读回、颜色对到定稿的调色板；第 0 张先和正面定稿逐部件比（白花、水晶、嫩芽、拳头大小），1–14 每张和第 0 张比拳头、腿的大小（不变形）。
- 缩到游戏里：和现在的单位一样高（嫩芽到脚底 57 游戏像素，高清帧 PPU 1.333），`tools/art/unit_ivern_daisy.py` 改成读这 15 张：idle = 第 0 张（呼吸：膝盖以上低一格）；run = 1–4（每帧 0.12 秒）；attack = 5、6（拳在 0.35 秒落下，附加包第 21 tick）；hit = 9；dead = 12（再往下沉两帧）或 13–14；drop（附加包落地时用动画定身播）= 10、11、0。
- 做逐帧 GIF（exact_gif.py）给用户看，认可了再装。
