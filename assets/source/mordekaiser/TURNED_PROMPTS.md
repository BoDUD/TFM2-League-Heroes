# 莫德凯撒（铁铠冥魂）：走路和技能转向右边 65°（第 2b 步，给 Codex 的提示词）

> 上一轮你画的 13 张姿势已经拼成动作，用户看了说：**走路时腿朝右走，身体却还是待机那样正对观众**——「走路的时候腿既然是那个方向 身体也要那个方向吧？」「待机姿势和走路放技能的时候应该不一样的」。用户从英雄联盟模型的 30° / 50° / 65° / 80° 里选了 **65°**（`refs/1_league_turn.png` 右边那个）。
> **待机和选人卡片不变**（仍是 `design/mordekaiser_front.png`，约 30°）。这一轮请你：
> 1. **先画一张转向 65° 的造型** `mordekaiser-turned.png`：同一个人、同一副盔甲、同一把锤子，站姿和待机一样（锤子扛在肩上），只是**整个身体转向画面右边约 65°**——胸口和肩甲转向右边，近侧（画面左边）的肩甲在前、远侧肩甲大半被身体挡住，头盔也跟着转（还能看到两只青绿眼睛，远侧那只小一点），两腿一前一后、靴尖朝右。
> 2. **再按这张 65° 造型重画 10 个动作姿势**：构图照上一轮你画的（`poses_front/` 里的正面版），**只是身体都转成 65° 这个角度**，和腿、锤子挥动的方向一致。
> **倒地两张（跪地、仰面倒地）不用重画。**

## 统一规则（和上一轮一样）

- 同一套格子：**每格 4 × 4 px、一格一个颜色**，和 `design/mordekaiser_front.png` 同样大小的格子、同样的身高（站姿角尖在绿线、靴底在红线）、同样的颜色和细节；不要画大了再缩，不要换画风。
- 画布：横版 1536 × 1024（384 × 256 格，绿线第 36 行、红线第 252 行），竖版 1024 × 1536（256 × 384 格，绿线第 164 行、红线第 380 行），看 `design/grid_landscape.png`、`design/grid_portrait.png`。
- **颜色只用 `design/mordekaiser_palette.png` 的 48 色**（最多再加 6 色，写进 HANDOFF）；一圈 1 格近黑描边；不要抖动、渐变、碎点、半透明、抗锯齿。
- **10 个姿势里的头盔都和 `mordekaiser-turned.png` 的头盔逐格一样**（同一个 65° 头盔，不再转、不缩放；Q 双手举锤那张被手臂挡住的部分可以挡住）。
- **锤子是同一把**（大小和造型一样，锤柄始终是直的）；身体的盔甲、青绿光、暗红破布、护膝、铁靴都和造型一样，只是转了角度、摆了姿势，**不要变形**。
- 没有特效、地面、影子、文字、网格线。每张交大图和逐格一致的 `_1x.png`。

## 要画的图（`outputs/mordekaiser-turned/`）

| 文件 | 画布 | 内容 | 构图照 | 角度参考 |
|---|---|---|---|---|
| `mordekaiser-turned.png` | 横版 | **65° 造型**：待机站姿（锤子扛在肩上、锤头在头后上方、柄尾和铁链在前面垂着），身体转向画面右边约 65°，两腿一前一后、靴尖朝右 | `design/mordekaiser_front.png` | `refs/1_league_turn.png` 右边 |
| `mordekaiser-walk-1.png` … `walk-4.png` | 横版 | 走路 4 个相位（同上一轮：1 近侧腿在前脚跟着地，2 交错最低，3 远侧腿在前，4 交错最高），**上半身就是 65° 造型**，只随步子上下 1–2 格 | `poses_front/walk-1..4.png` | `refs/6_league_walk_65.png` 的腿 |
| `mordekaiser-attack-raise.png` | 竖版 | 普攻蓄力：锤子高举在头后上方，身体 65° | `poses_front/attack-raise.png` | `refs/2_league_attack_65.png` 第 2 格 |
| `mordekaiser-attack-strike.png` | 横版 | 普攻砸下：锤子向前下方挥到身前右下方，上身前倾，身体 65° | `poses_front/attack-strike.png` | `refs/2_league_attack_65.png` 第 3 格 |
| `mordekaiser-q-raise.png` | 竖版 | Q 蓄力：双手握柄把锤子竖直举过头顶，身体 65° | `poses_front/q-raise.png` | `refs/3_league_q_65.png` 第 2 格 |
| `mordekaiser-q-slam.png` | 横版 | Q 砸地：双手把锤子砸进身前地面，屈膝前压，身体 65° | `poses_front/q-slam.png` | `refs/3_league_q_65.png` 第 3 格 |
| `mordekaiser-e-grasp.png` | 横版 | E：没拿锤子的那只手（带爪铁手套）向画面右边平伸、五爪张开，锤子仍扛在肩上，身体 65° | `poses_front/e-grasp.png` | `refs/4_league_e_65.png` 第 2 格 |
| `mordekaiser-r-point.png` | 横版 | R：**握锤的还是待机里握锤的那只手**，把锤子向前平举、锤头指向画面右边，身体 65° | `poses_front/r-point.png` | `refs/5_league_r_65.png` 第 2 格 |

## 提示词

先画 `mordekaiser-turned.png`（附 `design/mordekaiser_front.png`、`design/mordekaiser_palette.png`、`design/grid_landscape.png`、`refs/1_league_turn.png`）：

```text
The attached sprite (mordekaiser_front.png: 166 x 246 squares, 4 px a square, 48 colours in mordekaiser_palette.png) is the final high-resolution pixel-art design of this character in a 3/4 front view (about 30 degrees toward the image right): Mordekaiser, a towering undead warlord in spiked black iron plate armour (dark gunmetal with grey-blue highlights), ghostly teal-green light glowing from the gaps, a tall spiked helm with two tall horns and two glowing teal eyes in the visor slit, huge spiked pauldrons, a tattered dark-maroon cloth hanging from the belt, clawed iron gauntlets, heavy iron boots; his huge mace Nightfall (a black iron head with spikes on every side and a glowing teal crack, a straight greenish-dark haft, an iron cap and a short chain at its butt end) rests on his shoulder.
Draw the SAME character in the SAME standing pose, the mace on the shoulder, but with the WHOLE BODY TURNED TOWARD THE IMAGE RIGHT BY ABOUT 65 DEGREES (see the right figure of the attached render, compared with its left figure = the design's angle): the chest and the pauldrons facing more to the right, the near pauldron (image left) in front and the far one mostly hidden behind the body, the helm turned with the body (both teal eyes still visible, the far one smaller), the legs one in front of the other with the boots pointing right. On a 1536x1024 transparent canvas on the SAME 4-px grid (384 x 256 squares): every square one flat colour from the design's palette, the same square size, the same height (the horn tips on the green line at square row 36, the soles on the red line at row 252), the same armour, mace, colours and level of detail - as if the same artist had drawn the same sprite from a more turned angle. A 1-square near-black outline, no dithering, no gradients, no anti-aliasing, no semi-transparency, no effects, no ground, no shadow, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

然后每个姿势单独生成，附 `mordekaiser-turned.png`（你刚画的）、`design/mordekaiser_palette.png`、对应画布的 grid 图、表里「构图照」那张 `poses_front/` 和「角度参考」那张 `refs/`：

```text
The attached mordekaiser-turned.png is the final design of this character turned about 65 degrees toward the image right (4 px a square, 48 colours in mordekaiser_palette.png). The attached <FRONT POSE> shows the pose to draw as it was drawn in the earlier 30-degree view. Draw <WHAT> with the body in the 65-degree view of mordekaiser-turned.png - the same composition and motion as <FRONT POSE>, the chest, pauldrons and helm turned toward the image right as in mordekaiser-turned.png, consistent with the legs and the direction of the mace. On a <CANVAS> transparent canvas on the SAME 4-px grid: every square one flat colour from the palette, the same square size and body height (the horn tips on the green line, the soles on the red line), the same armour, mace (its haft always straight, the same size) and level of detail. The helm is copied square for square from mordekaiser-turned.png (not turned further, not resized). A 1-square near-black outline, no dithering, no gradients, no anti-aliasing, no semi-transparency, no effects (no impact, no aura, no trails), no ground, no shadow, no text, no grid lines. Also deliver a 1x copy that matches square for square.
```

`<CANVAS>`：横版 `1536x1024 (384 x 256 squares)`，竖版 `1024x1536 (256 x 384 squares)`；`<FRONT POSE>` 换成 `poses_front/<姿势>.png`；`<WHAT>` 依次换成：

- `walk-1`：`a heavy walking step, phase 1 of 4: the near leg forward with its heel down, the far leg back; the upper body, the helm and the mace on the shoulder exactly as in mordekaiser-turned.png, only the legs move, the legs not deformed`
- `walk-2`：`phase 2 of 4: the legs passing each other, the body one square lower`（其余同 walk-1）
- `walk-3`：`phase 3 of 4: the far leg forward with its heel down, the near leg back`
- `walk-4`：`phase 4 of 4: the legs passing each other the other way, the body one square higher`
- `attack-raise`（竖版）：`his basic attack wind-up: the hand that holds the mace in the design lifts it off the shoulder and raises it high behind and above the helm, the body leaning back a little`
- `attack-strike`（横版）：`his basic attack strike: the same hand swings the mace down in front of him, the mace head hitting the ground ahead to the image right, the arm straight, the upper body leaning forward, the near foot half a step forward`
- `q-raise`（竖版）：`his Obliterate wind-up: both hands gripping the haft, the mace raised straight up over his head`
- `q-slam`（横版）：`his Obliterate slam: both hands driving the mace head-first into the ground in front of him (the head's bottom on the red line), knees bent, the body pressed forward and lower, the soles on the red line`
- `e-grasp`（横版）：`his Death's Grasp: the free clawed hand (not the mace hand) thrust straight forward at shoulder height toward the image right, the claws spread; the mace still on the shoulder as in mordekaiser-turned.png`
- `r-point`（横版）：`his Realm of Death cast: THE SAME HAND THAT HOLDS THE MACE IN THE DESIGN holds it out forward, the haft horizontal, the mace head pointing at an enemy to the image right; the other arm at his side`

## 交付

- `outputs/mordekaiser-turned/`：`mordekaiser-turned.png` + 10 个姿势（大图 + `_1x.png`），`generation-prompts.txt`，原稿放 `raw/`；**最后写 `HANDOFF.md`**；最好再打成 `mordekaiser_turned_done.zip`。

## 交回前自查

- [ ] 65° 造型：身体、肩甲、头盔都明显朝右，两只眼睛都还看得到；身高、格子、色板和待机造型一样；
- [ ] 10 个姿势的身体都是 65°，和腿、锤子方向一致；头盔和 `mordekaiser-turned.png` 逐格一样；
- [ ] 锤子同一把、锤柄直；R 用的是待机里握锤的那只手；
- [ ] 每张 4 px 格子、透明度只有 0/255、颜色来自色板；站姿角尖绿线、靴底红线；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读 `raw/` 原稿和 `_1x` 并排比较；量头盔和身高是否与造型一致。
- 用 `mordekaiser-turned.png` 的头盔逐格贴回 10 个姿势（rig_mordekaiser.py 的 HELM_AT / CLEAR 做法，这次的模板是 65° 头盔）；待机、W、受击仍用 A 造型；死亡保留上一轮的两张。
- 自查：针孔、碎块、接缝、位置跳动（死亡对齐）、走路上半身是否稳定，再给用户 GIF。
