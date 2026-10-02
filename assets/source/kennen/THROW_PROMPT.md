# 凯南：扔手里剑的 4 个手臂姿势（给 Codex，普攻和 Q 用）

> 用户选了你上一轮画的手臂 **B**（举在头旁边握着大手里剑）。凯南的造型定下来了（`kennen/2_start_pose_8x.png`）。
> 现在普攻和 Q 要把手里剑扔出去，需要远侧手臂的 4 个姿势。**和上一轮一样：只画手臂和手里剑，底图一格都不改**。
> 其他动作（待机、跑、冲刺、受击、死亡……）Claude 用这张造型自己做，不用你画。
>
> 四个姿势（一个扔的过程，参考 `kennen/4_league_attack.png` 英雄联盟里他自己的普攻：手里剑先举到头后上方，再在胸口高度往前扔）：
> 1. **后摆**：手臂弯到头上方往后，手里剑举在兜帽顶后上方（兜帽左上），一部分被兜帽挡住（只画在透明格上，等于在头后面）；
> 2. **前甩**：手臂从头上往前挥，手里剑在脸的前上方、比兜帽顶稍高；
> 3. **出手**：手臂向前（右边）伸直、在下巴高度，手套张开，手里剑刚离手：它的中心在手套前面 2–4 格、**第 80–84 行之间（两条绿线之间）**（游戏里飞出去的手里剑从这个高度飞向目标，太高会看起来歪）；
> 4. **收手**：手臂向前稍往下，手套张开、**空手**（没有手里剑），爪子张开。
>
> - 每个姿势里手臂都要一眼看得出是手臂：2–3 格粗、弯着时手肘看得出来、连在远侧肩膀（下巴右边），自然；**不要直棍、不要细长手臂、不要一团**（用户之前说过手臂「突然伸的很长 有点诡异」「90度角」「奇怪」）。
> - 手里剑就是 `2_start_pose_8x.png` 里那一个（转动时可以转角度）；画法、大小、颜色都和你上一轮的手臂 B 一样。
> - **规则**：底图每一格不改（只有上一轮手臂已经盖住的兜帽右边金边可以再盖，其余只画在透明格上）；橙线（第 63 行）以上、脚底以下不能有东西；严格 8×8 网格；只用底图的颜色；新部分外面一圈 1 格 `#0B060E` 描边；没有抗锯齿和半透明。
> - **交付**：`kennen_throw_1.png` … `kennen_throw_4.png`（1024×1024，整张：底图 + 手臂 + 手里剑）、`kennen_throw_1_1x.png` …（128×128），还有只含手臂层的 `throw_arm_1_1x.png` …，透明底；`HANDOFF.md` **最后写**；最好打成 `kennen_throw_pack_done.zip`。

## 附图（压缩包 `kennen/` 里）

| 文件 | 内容 |
|---|---|
| `1_base_8x.png` / `1_base_1x.png` | 底图（没有远侧手臂），**在它上面画** |
| `1_base_guide.png` | 灰底：橙线 = 最高到第 63 行；两条绿线 = 出手时手里剑的高度（第 80–84 行）；红线 = 脚底下沿 |
| `2_start_pose_8x.png` / `_1x` | 定稿造型（底图 + 你画的手臂 B）：起始姿势，也是画法的标准 |
| `3_picture_B.png` | 原画 B |
| `4_league_attack.png` | 英雄联盟里凯南的普攻 6 帧（游戏尺寸）：动作参考 |

## 提示词

```text
Attached: FIRST the base sprite (1_base_8x.png: 1024x1024 = 128x128 squares at 8x, transparent) - a tiny yordle ninja at game size without his far arm; keep every one of its squares. SECOND the approved start pose (2_start_pose_8x.png): the same base with his far arm raised beside the head holding the big four-pointed gold shuriken - YOUR OWN earlier drawing, which the user picked: draw the new arms in exactly that style, size and palette. THIRD the illustration (3_picture_B.png). FOURTH League of Legends' own attack of this character at game size (4_league_attack.png): he brings the shuriken back over his head and throws it forward at his chest's height.
Task: draw FOUR poses of the far arm (sleeve, gold cuff, dark plum clawed glove with a steel plate) and the shuriken on the FIRST image, one image each - a throw in four steps:
1 WIND-UP: the arm bent back over the head, the shuriken held up behind the top of the hood (up and to the left of the hood's top), partly hidden behind the hood (draw it only on transparent squares: behind the head);
2 SWING: the arm coming forward over the head, the shuriken above the face's front edge, a little higher than the hood's top;
3 RELEASE: the arm stretched forward (to the right) at chin height, the glove open, the shuriken just leaving it - its middle 2-4 squares in front of the glove, at rows 80-84 (between the green lines);
4 FOLLOW-THROUGH: the arm forward and a little down, the glove open and EMPTY (no shuriken), claws spread.
The arm must read as an arm at this size in every pose: 2-3 squares thick, a visible bend at the elbow when bent, joined to the far shoulder (right of the chin), natural - never a straight stick, never a long thin arm, never a lump. The shuriken is the same one as in the SECOND image (turned as it spins).
Rules: do not change any square of the base (draw over the base only where the SECOND image's arm already covers it - the hood's right rim - else only on transparent squares); nothing above the orange line (row 63) or below the soles; every square a crisp 8x8 block on the base's grid; only the base's colours; a 1-square #0B060E outline round the new parts; no anti-aliasing, no semi-transparency.
Deliver kennen_throw_1.png ... kennen_throw_4.png (1024x1024, each the whole sprite: base + arm + shuriken) and kennen_throw_1_1x.png ... (128x128), plus the arm layers alone (throw_arm_1_1x.png ...), transparent background.
```

## 交回前自查

- [ ] 4 张里底图每一格都没变；
- [ ] 每个姿势的手臂 2–3 格粗、自然，连在肩膀上；出手那张手里剑中心在第 80–84 行、手套前 2–4 格；收手那张空手；
- [ ] 第 63 行以上、脚底以下没有东西；严格 8×8、只用底图颜色、新部分有描边；最后写 `HANDOFF.md`。
