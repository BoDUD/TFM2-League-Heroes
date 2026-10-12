# 莫德凯撒（铁铠冥魂）：高清（PPU）动作关键姿势（第 2 步，给 Codex 的提示词）

> 第 0 步你画的 A 版用户选定了。我已把 **raw/mordekaiser-model-A.png 按它自己的格子读回**成高清造型 `design/mordekaiser_front.png`（**166 × 246 格**，48 色），游戏里用 PPU 5 显示，这张就是待机和选人卡片。所有动作都用这个 **3/4 正面角度**（用户：「侧面只要四分之三那种就行」）。
> 待机里锤子扛在肩上、在头盔和肩甲**后面**：锤柄有一段被头盔挡住，锤头下半截被肩甲挡住，握锤的手下面的肩膀也没画——所以挥锤的动作没法从待机图里剪出来。**这一轮请你画动作的关键姿势**：身体、盔甲、锤子和造型完全一样，只是摆出不同的姿势。
> **所有图都画在同一个格子上**：每格 **4 × 4 px**、一格一个颜色，格子和 `design/mordekaiser_front.png` **大小完全一样**（同样大小的格子、同样的身高、同样的颜色和细节）。不要画大了再缩，不要换画风。

## 统一规则（每张都一样）

- 画布两种（看每张的「画布」一栏），都是透明背景、**4 px 一格**：
  - **横版 1536 × 1024（384 列 × 256 行）**：`design/grid_landscape.png` 是造型放在这个格子上的样子——**绿线 = 头盔两根角的尖（第 36 行）**，**红线 = 靴底（第 252 行，靴底最后一格在红线上面）**；
  - **竖版 1024 × 1536（256 列 × 384 行）**：`design/grid_portrait.png`，绿线第 164 行、红线第 380 行（上面留了空位给举起来的锤子）。
  - 站着的姿势：**角尖在绿线、靴底在红线**，身高和造型一模一样；蹲下、跪下、倒地的姿势：最低处落在红线上。
- **颜色只用 `design/mordekaiser_palette.png` 里的 48 色**（实在要加，最多再加 6 色，写进 HANDOFF）。一圈 1 格近黑描边，里面少用黑；不要抖动、渐变、碎点、半透明、抗锯齿。
- **头盔（两根高角、面甲、两只青绿眼睛）在每张站姿里都和造型逐格一样**：照抄 `design/mordekaiser_front.png` **第 28–92 行、第 66–104 列**那一块，不转、不缩；我导入时也会把造型的头盔贴回去，所以位置和大小要对得上。倒地两张头盔可以跟着身体倒下。
- **锤子「夜临」每张都是同一把**：四面尖刺的黑铁锤头 + 中间青绿裂纹、长锤柄（偏绿的深灰）、柄尾铁箍和一小段铁链，大小和造型里一样（锤头约 60 × 90 格），**锤柄始终是直的**，不弯、不变短。
- 身体其他部分（尖刺肩甲、胸口和关节的青绿光、暗红破布、尖角护膝、铁靴、带爪铁手套）和造型一样，只是跟着姿势动；**3/4 正面角度不变**（身体朝画面右前方）。
- 没有特效：不画砸地的冲击、黑暗光环、拉人的爪影、大招领域、残影、拖尾（特效第 3 步再画）。不要地面、影子、文字、网格线。
- 每张交大图（4 px 一格）和 `_1x.png`（1 像素 1 格，必须和大图逐格一致）。

## 要画的图（`outputs/mordekaiser-poses/`）

| 文件 | 画布 | 内容 | 参考 | 用在 |
|---|---|---|---|---|
| `mordekaiser-mace.png` | 横版 | **只画锤子**：和造型里同一个角度（锤头在右上、柄尾和铁链在左下），**完整不被挡**：锤柄整根画出来，锤头被肩甲挡住的下半截补全；握锤的那只手也去掉。位置随意，四周留空。 | `refs/1_picture_A.png` 里的锤子 | 死亡掉落、核对锤子 |
| `mordekaiser-attack-raise.png` | 竖版 | **普攻蓄力**：握锤的手把锤子从肩上抬起，**锤子高高举在头盔后上方**（锤头朝上偏后），身体微微后仰，两脚不动。 | `refs/2_league_attack.png` 第 2 格 | 普攻第 1–2 帧 |
| `mordekaiser-attack-strike.png` | 横版 | **普攻砸下**：同一只手把锤子**向前下方挥下**，锤头砸在身前右下方（锤头底在红线上方几格），手臂伸直，上身前倾，近侧脚往前迈半步。 | `refs/2_league_attack.png` 第 3 格 | 普攻命中 |
| `mordekaiser-q-raise.png` | 竖版 | **Q 破灭之锤蓄力**：**双手**握住锤柄，把锤子**竖直高举过头顶**（锤头朝上），身体挺直、微微踮起。 | `refs/3_league_q.png` 第 2 格 | Q 第 1–2 帧 |
| `mordekaiser-q-slam.png` | 横版 | **Q 砸地**：双手握锤，把锤子**狠狠砸进身前的地面**（锤头底在红线上），**膝盖弯下、身体前压**（比站姿矮一些，靴底仍在红线上）。 | `refs/3_league_q.png` 第 3 格 | Q 命中 |
| `mordekaiser-e-grasp.png` | 横版 | **E 断魂一扼**：**没拿锤子的那只手（画面右边、带爪铁手套）向前伸直**，手臂平举到肩膀高度、指向画面右边，五根铁爪张开；锤子仍然扛在肩上（和造型一样）。 | `refs/4_league_e.png` 第 2 格 | E |
| `mordekaiser-r-point.png` | 横版 | **R 轮回绝境**：握锤的手把锤子**向前平举、锤头指向画面右边的敌人**（锤柄水平），另一只手垂在身旁，站得很稳。 | `refs/5_league_r.png` 第 2 格 | R |
| `mordekaiser-walk-1.png` … `walk-4.png` | 横版 | **走路 4 个相位**（沉重地迈步）：1 = 近侧腿（画面左边那条）在前、脚跟着地；2 = 两脚交错、身体最低；3 = 远侧腿在前；4 = 两脚交错、身体最高。**上半身、头盔、扛在肩上的锤子和造型一样**（只随步子上下 1–2 格），只有腿在动；腿的长短、粗细、护膝和铁靴和造型一样，**不要变形**。 | `refs/6_league_walk.png` | 移动 |
| `mordekaiser-dead-kneel.png` | 横版 | **死亡 1**：**单膝跪地**，锤子脱手掉在身旁地上，头低下，一只手撑地。 | `refs/7_league_death.png` 第 2–3 格 | 死亡 |
| `mordekaiser-dead-lying.png` | 横版 | **死亡 2**：**仰面倒在地上**（身体横躺，头在画面左边），锤子躺在身旁地上，最低处在红线上。 | `refs/7_league_death.png` 第 4 格 | 死亡最后 |

## 提示词

一次附图：`design/mordekaiser_front.png`、`design/mordekaiser_palette.png`、对应画布的 `design/grid_landscape.png` 或 `design/grid_portrait.png`、表里那张 `refs/`，再加 `refs/1_picture_A.png`。每张图单独生成，**每张都附 `mordekaiser_front.png`**。

```text
The attached sprite (mordekaiser_front.png: 166 x 246 squares, 4 px a square, 48 colours in mordekaiser_palette.png) is the final high-resolution pixel-art design of this character in 3/4 front view facing the image right: Mordekaiser, a towering undead warlord in spiked black iron plate armour (dark gunmetal with grey-blue highlights), ghostly teal-green light glowing from the gaps (chest, upper arms, waist, knees), a tall spiked helm with two tall horns and two glowing teal eyes in the visor slit, huge spiked pauldrons, a tattered dark-maroon cloth hanging from the belt, clawed iron gauntlets, heavy iron boots; his weapon Nightfall is a huge long-handled mace: a black iron head with spikes on every side and a glowing teal crack, a straight greenish-dark iron haft, an iron cap and a short chain at its butt end. In the design the mace rests on his shoulder behind the helm.
Draw <WHAT> on a <CANVAS> transparent canvas on the SAME 4-px grid (the attached grid picture shows the design placed on it): every square one flat colour from the design's palette, the same square size, the same body height (the horn tips on the green line, the soles on the red line), the same armour, mace, colours and level of detail as the design - as if the same artist had drawn the same sprite in another pose, still in 3/4 front view facing the image right. The helm is copied square for square from the design (rows 28-92, columns 66-104 of mordekaiser_front.png): the same helm, not turned, not resized. The mace is the design's mace, the same size, its haft always straight. A 1-square near-black outline, little black inside, no dithering, no gradients, no anti-aliasing, no semi-transparency, no effects (no impact, no aura, no trails, no glow halo), no ground, no shadow, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<CANVAS>` 横版填 `1536x1024 (384 x 256 squares)`，竖版填 `1024x1536 (256 x 384 squares)`；`<WHAT>` 依次换成：

- `mordekaiser-mace.png`（横版）：`ONLY THE MACE, alone, at the same angle as in the design (head up-right, cap and chain down-left), COMPLETE: the whole straight haft drawn, the head's lower half that the pauldron hides in the design completed, no hand; anywhere on the canvas with empty margins`
- `mordekaiser-attack-raise.png`（竖版）：`his basic attack wind-up: the hand holding the mace lifts it off the shoulder and RAISES IT HIGH behind and above the helm (the mace head up and back), the body leaning back a little, both feet planted as in the design (see the second moment of the attached render)`
- `mordekaiser-attack-strike.png`（横版）：`his basic attack strike: the same hand SWINGS THE MACE DOWN IN FRONT of him, the mace head hitting the ground ahead to the image right (its bottom a few squares above the red line), the arm straight, the upper body leaning forward, the near foot half a step forward (see the third moment of the attached render)`
- `mordekaiser-q-raise.png`（竖版）：`his Obliterate wind-up: BOTH HANDS gripping the haft, the mace RAISED STRAIGHT UP OVER HIS HEAD (the head pointing up), the body stretched upright (see the second moment of the attached render)`
- `mordekaiser-q-slam.png`（横版）：`his Obliterate slam: both hands driving the mace HEAD-FIRST INTO THE GROUND in front of him (the mace head's bottom on the red line), knees bent, the body pressed forward and lower than standing, the soles still on the red line (see the third moment of the attached render)`
- `mordekaiser-e-grasp.png`（横版）：`his Death's Grasp: the FREE CLAWED HAND (the arm on the image right, not holding the mace) THRUST STRAIGHT FORWARD at shoulder height toward the image right, the five iron claws spread open; the mace still resting on the shoulder exactly as in the design (see the second moment of the attached render)`
- `mordekaiser-r-point.png`（横版）：`his Realm of Death cast: the hand holding the mace HOLDS IT OUT FORWARD, the haft horizontal and the mace head pointing at an enemy to the image right; the other arm hanging at his side, standing firm (see the second moment of the attached render)`
- `mordekaiser-walk-1.png`（横版）：`a heavy walking step, phase 1 of 4: the near leg (on the image left) forward with its heel down, the far leg back; the upper body, the helm and the mace on the shoulder exactly as in the design, only the legs move; the legs the same length, thickness, knee guards and boots as the design, not deformed (see the attached walking render)`
- `mordekaiser-walk-2.png`：同上，把 `phase 1 of 4: ...` 换成 `phase 2 of 4: the legs passing each other, the body at its lowest (one square down)`
- `mordekaiser-walk-3.png`：`phase 3 of 4: the far leg forward with its heel down, the near leg back`
- `mordekaiser-walk-4.png`：`phase 4 of 4: the legs passing each other the other way, the body at its highest (one square up)`
- `mordekaiser-dead-kneel.png`（横版）：`his death, part 1: DOWN ON ONE KNEE, the mace fallen from his hand onto the ground beside him, the head bowed, one hand on the ground (see the attached death render); the lowest square on the red line`
- `mordekaiser-dead-lying.png`（横版）：`his death, part 2: LYING ON HIS BACK on the ground, the body horizontal with the head on the image left, the mace lying on the ground beside him; the lowest square on the red line`

## 交付

- `outputs/mordekaiser-poses/` 里上表 13 张（大图 + `_1x.png`），`generation-prompts.txt`，生图原稿放 `raw/`；**最后写 `HANDOFF.md`**（每张的格子大小、身高、色数、哪里没做到）；最好再打成 `mordekaiser_poses_done.zip`。

## 交回前自查

- [ ] 每张都在 4 px 格子上，每格一个颜色，透明度只有 0/255，颜色来自 48 色色板（新增不超过 6 色）；
- [ ] 站姿的角尖在绿线、靴底在红线，身高和造型一样；跪、躺两张最低处在红线；
- [ ] 头盔在每张站姿里和造型逐格一样（第 28–92 行、第 66–104 列）；
- [ ] 锤子是同一把：大小一样，锤柄直的，锤头四面尖刺 + 青绿裂纹，柄尾铁箍和铁链都在；
- [ ] 走路 4 张：只有腿在动，腿不变形，上半身和扛着的锤子和造型一样；
- [ ] 都是 3/4 正面朝右；没有特效、地面、影子；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 先看 `raw/` 原稿，用 `regrid.py` 按原稿自己的格子读回；Codex 自己的 `_1x` 可能缩放走样（库奇的教训），两种并排比较。读回的格子数要和造型对得上（头盔宽度、身高），对不上就按头盔量出比例再说，不要拉伸。
- 每帧把造型的头盔逐格贴回（one-face-all-frames）；姿势里没动的部分（腿、身体）尽量用造型自己的像素；锤子和锤柄要直。
- 动作：idle = 造型 + 呼吸；run = walk 1–4；attack = 造型 → attack-raise → attack-strike → 回到造型；skill (Q) = q-raise → q-slam；skill2 (E) = e-grasp，W = 造型 + 护盾特效；ult = r-point；dead = dead-kneel → dead-lying；hit = 造型后退 + 白闪。
- 自查：边缘 / 6–8 倍 / 游戏尺寸 / 部件 / 只在角上的方块 / 缝隙（gap-check）/ 变形（rig-deformation-checks），再给用户看 GIF。
