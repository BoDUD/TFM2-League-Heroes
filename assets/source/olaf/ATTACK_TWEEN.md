# 奥拉夫普攻：补两帧过渡（Olaf attack: two in-between frames）

## 为什么

游戏里奥拉夫每一刀都很顿：待机是**正面站、两把斧垂在身体两侧**，普攻第 1 帧一下子变成**侧身、两腿大开、斧举在身前**；
第 5 帧是**低位前冲、斧扫到另一边地上**，第 6 帧又一下子站直，然后回到正面待机。两处都是一帧之内整个姿势全换。

用户的要求：「奥拉夫普攻首尾各补一帧过渡（起手从待机姿势转过去、收招回到待机），其余帧不动」。

## 要画的两帧

`now/` 里是现在游戏里用的帧（8 倍，一格 112×96 个游戏像素，脚底在格子第 81 行，两脚中点在第 56 列）：
`idle.png`（待机第 1 帧）、`attack_1.png` … `attack_6.png`。`now/sequence.png` 是现在的顺序，空着的两格就是要画的位置。

- **T1 起手过渡**（放在 待机 → 普攻 1 之间）：正好是待机和普攻 1 的**中间**。
  - 身体从正面转到普攻 1 的侧身，转到一半；
  - 两脚从待机的站位往普攻 1 的站位张开一半（脚底仍在第 81 行，脚不离地）；
  - 拿斧的那只手（普攻 1 里举在身前的那把）从身侧抬起到一半；另一把斧还在身侧；
  - 头的高度在两帧之间。
- **T2 收招过渡**（放在 普攻 5 → 普攻 6 之间）：正好是普攻 5 和普攻 6 的**中间**。
  - 从低位前冲起身到一半：上身抬起、重心收回；
  - 两脚从普攻 5 的站位往普攻 6 的站位收拢一半；
  - 扫到地上的斧收回到一半（往普攻 6 里斧的位置去）。

## 必须守的

1. **身体就是这几帧里的身体**：头盔、角、脸、胡子、毛领、皮带、靴子、斧的形状和大小都照 `now/` 的帧，一格不改；
   头（头盔、角、脸）直接用 `now/head.png` 那一块（8 倍），不要重画。不要变胖变瘦、不要拉长压扁。
2. **只用 `now/palette.png` 里的颜色**，外轮廓 1 格深色描边，和现有帧一样。
3. 像素格对齐：8 倍图里每个游戏像素是 8×8 的整块，不要抗锯齿、不要半透明。
4. 不要改动现有的 7 帧。

## 交付（放在 `outputs/olaf-attack-tween/`）

- `t1.png`、`t2.png`：8 倍，896×768，透明底，和 `now/` 的帧同一个格子（脚底第 81 行、两脚中点第 56 列）；
- `native/t1.png`、`native/t2.png`：1 倍，112×96；
- `preview_sequence.png`：待机、T1、普攻 1–5、T2、普攻 6、待机 排成一行（4 倍）；
- 最后写 `HANDOFF.md`（写了它就算交付完成，之后不要再改文件）。

---

**English summary.** Draw two in-between frames for Olaf's basic attack, on the same 112×96 cell (8× = 896×768,
soles on row 81, feet centred on column 56), same body, head (`now/head.png` pasted as is), palette
(`now/palette.png`) and 1-square dark outline as the current frames in `now/`:
**T1** halfway from `idle.png` to `attack_1.png` (half turned, feet half spread, the front axe half raised, the other
still at his side); **T2** halfway from `attack_5.png` to `attack_6.png` (rising half out of the lunge, feet half
drawn together, the low axe half way back). No anti-aliasing, no size change, the existing frames untouched.
Deliver `t1.png`, `t2.png`, `native/`, `preview_sequence.png`, then `HANDOFF.md` last in `outputs/olaf-attack-tween/`.
