# 奎因：腿部姿势（给 Codex 的提示词）

> **用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - `0_design.png` 是用户选定的奎因待机造型（每格 22 px，头盔尖 y = 132，脚底 y = 1210，49 格高）。**红线以上的上半身（头、面甲、兜帽、肩甲、披风、胸甲、举着连弩的手臂）一格都不要改**。
> - 这次**只画腿**：同一个奎因、同样的格子、同样的颜色，红线以下的两条腿画成 6 种姿势（照英雄联盟原版的动作，附图 `*_lol.png`）。游戏里的动作帧会把她的上半身和这些腿拼起来。
> - 每种姿势有一张目标图（`*_target.png`）：上半身已经放好（有的往下移了几格，表示人蹲低了），**红线是腰（腿从这里开始）**，**蓝线是地面**。请把腿画在红线下面，和上半身的腰连上，脚底（跪着的膝盖、小腿）落在蓝线上（空中收腿那张除外）。

## 6 种腿

| 图 | 姿势 | 上半身下移 | 腿 |
|---|---|---|---|
| 1 kneel | 单膝跪地（附图 `1_kneel_lol.png`，开大召鹰时） | 8 格 | **远侧（画面右边）的腿屈膝、脚踩在地上；近侧（画面左边）的腿膝盖和小腿跪在地上**，靴尖朝后 |
| 2 lunge | 向前弓步（`2_lunge_lol.png`，放鹰时往前一扑） | 3 格 | **前腿（画面右边）向前迈出一大步、膝盖弯**，后腿（画面左边）**向后伸直**，脚跟抬起 |
| 3 wide | 宽站瞄准（`3_wide_lol.png`，普攻） | 2 格 | 两腿左右分得很开、膝盖都微弯，两只脚踩实 |
| 4 back | 重心后撤（`4_back_lol.png`，挨打 / 后坐） | 1 格 | 后腿（画面左边）弯膝承重，前腿（画面右边）**向前伸直**、脚跟着地脚尖翘起 |
| 5 tuck | 空中收腿（`5_tuck_lol.png`，后空翻） | 0 格 | **两条腿都屈膝收到身体下面**（膝盖往前上方），脚离开地面，靴底朝下后方 |
| 6 step | 两脚并拢（`6_step_lol.png`，待机换重心） | 0 格 | 两腿笔直、两只脚靠在一起站着 |

## 要求

- 腿的样子和 `0_design.png` 一样：**深紫色护腿**（要有偏亮的边）、**膝盖和小腿前面的金色护板**、**尖头深棕靴子**、腰两侧垂下的金边羽毛护甲片跟着腿动；粗细和定稿一样（不要变细、变粗、变长、变短，弯曲时整段一起转）；近侧腿颜色亮、远侧腿暗一档。
- **每格 22 px**，网格从画布左上角对齐；**1 格近黑外描边**，和上半身的描边连成一圈；每种材质 2–3 档平涂；不要抖动、渐变、柔光、抗锯齿。
- **真透明背景，alpha 只能是 0 或 255**；1254 × 1254；不要网格线、文字、影子、地面、特效。
- 上半身照目标图原样画上（可以照抄），**不许改上半身的样子和位置**。
- 红线以下除了腿，还有**披风的下摆**（画面左边，往下垂到膝盖附近）和腰两侧的金边护甲片：照 `0_design.png` 补上，跟着姿势摆（蹲下时披风下摆可以拖到地上）。

## 提示词（每种姿势一张，共 6 张；附 `0_design.png`、该姿势的 `*_target.png` 和 `*_lol.png`）

```text
Attached: image 1 is an approved pixel-art character on a 22 px grid (1254x1254 canvas, visor crest at y 132, soles at y 1210): a young woman ranger in a gold winged visor, a deep-blue hood, a gold feather pauldron, a blue-violet cape, a brown leather corset, a gold and steel crossbow held out to the right, dark violet greaves with gold knee and shin plates and pointed dark brown boots; the red line is her hip, the blue line the ground. Image 2 is the TARGET for this picture: her upper body already placed (moved down some whole squares when she is lower) with NO LEGS - the red line is where the legs start, the blue line the ground. Image 3 is the original 3D character in this pose: copy ONLY THE LEGS' POSE from it.
Draw with the image generator ONE clean pixel-art picture, 1254x1254, real transparent background (alpha only 0 or 255): the upper body EXACTLY as image 2 (same squares, same place, unchanged), and under the red line her TWO LEGS in this pose: <POSE>. The legs drawn like image 1's: dark violet greaves with lighter edges, the gold knee and shin plates, pointed dark brown boots, the gold-edged feathered tassets at the hips following the legs, and the lower part of the blue-violet cape (on the image left, hanging to about the knees as in image 1; on the ground when she is low); the same thickness and length as image 1's legs (a bent leg turns as whole segments, never thinner or longer); the near leg (image left) in full tone, the far leg (image right) a step darker. Every square exactly 22 px on one straight grid from the canvas corner; one continuous 1-square near-black outline joined to the upper body's; 2-3 flat shades a material; no dithering, no gradients, no glow, no blur, no anti-aliasing. No background, no ground, no shadow, no text, no grid lines, no effects.
```

把 `<POSE>` 换成：

1. `kneel`：`DOWN ON ONE KNEE - the far leg (image right) bent with its boot flat on the ground in front, the near leg (image left) kneeling with its knee and shin on the ground line and the boot tip behind`
2. `lunge`：`A BIG LUNGE FORWARD - the front leg (image right) stepped far forward with the knee bent over the foot, the back leg (image left) stretched straight behind with the heel lifted`
3. `wide`：`A WIDE AIMING STANCE - the feet planted far apart to the left and right, both knees a little bent`
4. `back`：`THE WEIGHT ON THE BACK LEG - the back leg (image left) bent under her carrying the weight, the front leg (image right) stretched straight forward with the heel on the ground and the toe up`
5. `tuck`：`BOTH LEGS TUCKED UP IN THE AIR - both knees bent and pulled up under her body (the knees forward and up), the boots off the ground pointing down and back`
6. `step`：`THE FEET CLOSE TOGETHER - both legs straight, the two boots side by side under her`

## 交付（`outputs/quinn-legs/`）

- `quinn-legs-kneel.png`、`quinn-legs-lunge.png`、`quinn-legs-wide.png`、`quinn-legs-back.png`、`quinn-legs-tuck.png`、`quinn-legs-step.png`；原始生成图放 `raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/quinn_legs_done.zip`。中间不要停，六张都画完再交。

## Claude 收到后（给 Claude 看）

- 按 22 px 网格读回（regrid，必要时量 Codex 实际的格子），只取红线（腰 + 下移格数）以下的腿，颜色归到定稿的调色板，上半身用定稿原样（`tools/art/design_quinn_legs.py`，照 design_volibear_poses.py）；腿和腰的接缝查缺口（gap-check），每种腿在 8 倍下看有没有变形，再拼进 rig_quinn.py 的各个动作。
