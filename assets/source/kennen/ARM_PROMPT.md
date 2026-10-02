# 凯南：只画举手里剑的手臂（给 Codex）

> **这一轮只在底图上加一条手臂和手里剑，其他一格都不改。** 用户看了你上一轮画的 B1、B2，说「都不满意 质量太差了」，要用现在游戏里的头。
> Claude 用现在的头和身体拼了底图（`kennen/1_base_8x.png`：A37 的兜帽和脸、变瘦的长袍、近侧的爪子、腿和鞋；背上的手里剑和胸前远侧的爪子已经去掉），
> 自己画了四版举手里剑的手臂，用户都说怪：「这个手臂画的有点奇怪 不自然 90度角」「都不行 你不觉得奇怪吗」（`kennen/4_rejected_arms.png`），
> 然后说「让 Codex 只画手臂」。
>
> - **只加**：远侧那只手臂（袖子、手套）和大手里剑，姿势照原画 B（`kennen/2_picture_B.png`）：上臂从远侧肩膀（下巴右边）伸出，**手肘弯曲朝右下**，
>   前臂在兜帽旁边举起，宽袖子、金色袖口，深梅紫爪子手套（手背一格钢蓝）在**眼睛高度**握住手里剑下面的叶片；手里剑在兜帽右上角旁边，可以压住兜帽的角，**不能挡脸和眼睛**。
> - **位置**：`kennen/3_picture_B_at_scale.png` 右半是原画 B 按底图的比例、眼睛对齐底图眼睛描出来的样子，手和手里剑放在那个位置。
> - **不要像被否掉的那几版**：从肩膀直上的一根竖柱子（90 度角）、脸旁边的一团袖子、贴在脸上的扁袖子。手臂要在这个尺寸下一眼看得出是手臂：2–3 格粗、手肘有清楚的弯折，自然、放松。
> - **规则**：只在蓝线右边（x ≥ 592，第 74 列）、腰以上画；底图的每一格都不能改（头、脸、兜帽、身体、近侧爪子、腿脚逐像素保留）；
>   手里剑顶不能高过橙线（y = 504，第 63 行）；严格 8×8 网格；只用底图的颜色；新画的部分外面一圈 1 格 `#0B060E` 描边；没有抗锯齿和半透明。
> - **交付三版**（A、B、C：手肘弯法 / 手的高度不同），每版是整张精灵（底图 + 手臂 + 手里剑）：`kennen_arm_A.png`、`kennen_arm_B.png`、`kennen_arm_C.png`（1024×1024）
>   和 `kennen_arm_A_1x.png` 等（128×128），透明底；`HANDOFF.md` **最后写**，说明三版的区别；最好打成 `kennen_arm_pack_done.zip`。

## 附图（压缩包 `kennen/` 里）

| 文件 | 内容 |
|---|---|
| `1_base_8x.png` / `1_base_1x.png` | 底图（透明），**在它上面加手臂和手里剑，其他不改** |
| `1_base_guide.png` | 底图放在灰底上：蓝线 = 只在右边画（第 74 列），橙线 = 手里剑顶的上限（第 63 行），红线 = 脚底下沿 |
| `2_picture_B.png` / `_white` | 原画 B：举手里剑的姿势 |
| `3_picture_B_at_scale.png` | 左：底图；右：原画 B 按底图比例、眼睛对齐描出来的样子（手和手里剑的位置） |
| `4_rejected_arms.png` | 用户否掉的手臂（不要这样画） |
| `5_quality_bar.png` | main 里的约德尔英雄 ×8（像素大小和干净程度） |

## 提示词

```text
Attached: FIRST the base sprite (1_base_8x.png, 1024x1024 = a 128x128-square canvas at 8x, transparent) - a tiny yordle ninja at game size, approved by the user: keep EVERY one of its squares exactly as it is. SECOND the illustration (2_picture_B.png) - copy its POSE of the raised arm: his far hand raised beside his head, holding a huge four-pointed GOLD SHURIKEN (a round hole in its centre, curved blades, engraved lightning lines) ready to throw. THIRD the illustration traced at the base's scale with its eyes on the base's eyes (3_picture_B_at_scale.png, right half) - where the hand and the shuriken go. FOURTH arms that the user rejected as unnatural (4_rejected_arms.png): a straight vertical column from the shoulder (a 90-degree angle), a lump of sleeve beside the face, a sleeve stuck flat against the face - do NOT draw the arm like these. FIFTH heroes of this game at 8x (the quality bar).
Task: ADD ONLY the raised far arm (sleeve, glove) and the shuriken to the FIRST image, as a pixel artist would at this tiny size, following the illustration: the upper arm out from the far shoulder (right of his chin), the elbow bent and pointing out to the right and down, the forearm rising beside the hood in a wide violet sleeve with a gold cuff, the dark plum clawed glove (a steel-blue plate on its back) gripping the shuriken's lower blade at about the height of his eyes, the shuriken beside and above the hood's top right corner, partly over the hood's corner but never over the face or the eyes. The arm must read as an arm at this size (2-3 squares thick, a clear bend at the elbow), natural and relaxed, not a stick, not a column, not a blob.
Rules: draw only to the right of the blue line (x >= 592, square column 74) and above his waist; do not change any square of the base (the head, the face, the hood, the body, the near claw, the legs stay pixel for pixel); the shuriken's top no higher than the orange line (y = 504, square row 63); every square a crisp 8x8 block on the base's 8-px grid; only the base's colours (outline #0B060E; violet #3A1452 #5E2386 #8A36B8 #B657DE; plum #251324 #452348 #6E3E75; gold #7A3E1C #CB7420 #F8A23B #FEDC80; steel #4A4E70 #8A8FB0); a 1-square #0B060E outline round the new parts; no anti-aliasing, no semi-transparency.
Deliver three versions of the arm (A, B, C: different bends of the elbow / heights of the hand), each the whole sprite (the base plus your arm and shuriken) as kennen_arm_A.png, kennen_arm_B.png, kennen_arm_C.png (1024x1024) and kennen_arm_A_1x.png ... (128x128), transparent background.
```

## 交回前自查

- [ ] 底图的每一格都没变（只多了手臂和手里剑）；
- [ ] 手臂 2–3 格粗、手肘有弯，手套在眼睛高度握住手里剑，不是竖柱子、不是一团；
- [ ] 手里剑顶不高过第 63 行，不挡脸和眼睛；
- [ ] 严格 8×8、只用底图颜色、新部分有一圈描边；三版都交，最后写 `HANDOFF.md`。
