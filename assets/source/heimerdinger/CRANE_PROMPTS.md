# 大发明家 黑默丁格：B 包 背包机械臂和大招装置（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小。**
> - 英雄联盟里他的 **Q（放炮台）、E（扔手雷）、W（发射导弹）** 都是从背包里（藏在那团头发后面）伸出一条**机械臂**：橄榄绿的金属臂一节一节，关节是圆形的转轴，末端一只**红色的爪子**抓着一枚**火箭**（淡黄色的弹身、红色的环和尾翼、淡色的弹头）。机械臂举高、晃一晃，把火箭放到地上（Q）、往前甩出去（E）或者发射出去（W），然后折回背包。**大招 R「升级！！！」**是背包顶上弹出一个圆鼓，两根带红球的弹簧天线高高弹起，头顶外面张开一圈红边的深色圆环。
> - 定稿里看不到这些（平时藏在背包里），所以请你画 **20 张道具图**：**机械臂 17 个位置**（p2–p18）和 **R 的装置 3 个样子**（p19–p21）。
> - **每张只画道具本身，不要画黑默丁格**：引导图里的灰色小人只是告诉你道具在哪里、多大；画布 **1254 × 1254**，**每格 12 px**（和 `0_design.png` 一样大），红线是地面（y = 1200），网格从画布左上角对齐。
> - **机械臂**：引导图（`p*_guide.png`）里的橄榄绿粗线就是机械臂的位置和每一节的长短（我照英雄联盟这一帧的关节画的），圆点是关节，红色是爪子，黄色是火箭（标了 HELD 的才有火箭，GONE 的爪子是空的）。请照引导图的位置、照英雄联盟这一帧（`p*_league.png`）的样子画出**干净的像素机械臂**。**机械臂整条都画出来**，包括被头发挡住的根部（我会把它放在他身后，头发自然挡住根部）。
> - **17 张机械臂是同一条机械臂**：第一张定下样子后，后面每节的粗细、颜色、螺栓、关节、爪子、火箭都一样，只是位置不同。大小：最粗的一节约 5–6 格宽，关节约 6 格，爪子约 5 格，**火箭约 11 格长、4–5 格粗**。
> - **R 的装置**（p19–p21）：圆鼓在头发顶上偏后；弹簧天线是一圈一圈的灰绿弹簧，顶上一个约 3 格的红球；圆环是深灰色的盘边、外圈红色，横着套在头发顶上。**圆环被头发挡住的后半圈不要画**（这张会盖在他身上，只要露在外面的部分）。
> - 颜色：机械臂橄榄绿 3 档（亮边偏黄绿）+ 深色螺栓；关节转轴深橄榄 2 档；爪子红 3 档；火箭淡黄 3 档 + 红色环和尾翼 + 浅色弹头；R 的弹簧灰绿 3 档，红球 3 档，圆环深灰 2 档 + 红边 2 档。一圈 1 格的近黑外描边。

## 20 张道具

| 图 | 文件 | 画什么 |
|---|---|---|
| p2 | `heimerdinger-prop-crane_peek.png` | 机械臂刚从头发后面伸出来，折着，爪子抓着火箭竖在头顶后面 |
| p3 | `heimerdinger-prop-crane_peek2.png` | 机械臂刚伸出来，往上抬，爪子抓着火箭朝右上 |
| p4 | `heimerdinger-prop-crane_up.png` | 机械臂高高举起，爪子抓着火箭竖在最上面 |
| p5 | `heimerdinger-prop-crane_up_empty.png` | 同 p4 的位置，**爪子空着**（火箭已经放出去了） |
| p6 | `heimerdinger-prop-crane_up_back.png` | 机械臂举高，稍往后仰，抓着火箭 |
| p7 | `heimerdinger-prop-crane_up_high.png` | 机械臂举到最高，抓着火箭 |
| p8 | `heimerdinger-prop-crane_place.png` | 机械臂从头顶往前弯下来，把火箭（炮台套件）放到他身前右边的地上 |
| p9 | `heimerdinger-prop-crane_lift.png` | 放完往回抬，爪子空着，机械臂在头顶前方 |
| p10 | `heimerdinger-prop-crane_return.png` | 机械臂竖回头顶，爪子空着往右 |
| p11 | `heimerdinger-prop-crane_fold.png` | 机械臂折回背包里，只露出一小截在头发后面，爪子空着 |
| p12 | `heimerdinger-prop-crane_cock.png` | 机械臂往前上方伸，抓着火箭（准备甩出去） |
| p13 | `heimerdinger-prop-crane_throw.png` | 机械臂往前一甩，爪子空着（手雷刚扔出去） |
| p14 | `heimerdinger-prop-crane_recoil.png` | 甩完往回收，爪子空着 |
| p15 | `heimerdinger-prop-crane_aim.png` | 机械臂举高，抓着火箭准备发射 |
| p16 | `heimerdinger-prop-crane_fire.png` | 火箭刚发射，机械臂往后一震，爪子空着张开 |
| p17 | `heimerdinger-prop-crane_recover.png` | 发射后往回收，爪子空着 |
| p18 | `heimerdinger-prop-crane_aim_empty.png` | 机械臂举高，爪子空着 |
| p19 | `heimerdinger-prop-gear_drum.png` | R：背包顶上弹出一个橄榄绿的圆鼓（在头发顶上偏后），还没有弹簧 |
| p20 | `heimerdinger-prop-gear_burst.png` | R：两根带红球的弹簧天线从头顶两边高高弹起，头顶外面张开一圈红边的深色圆环，圆鼓还在 |
| p21 | `heimerdinger-prop-gear_settle.png` | R：弹簧天线回弹，矮一点，红球还在顶上；圆环和圆鼓还在 |

## 提示词（每张一次，换掉最后一段）

每次上传：`0_design.png`（定稿，看格子大小和他在哪里）、这一张的 `p*_guide.png`、这一张的 `p*_league.png`，有余量再加 p4 画好的那张（保持同一条机械臂）。**用 image_gen 画。**

```text
Attached images: A the approved pixel-art character on a 1254x1254 canvas with 12 px squares (soles on y 1200) - a short old yordle inventor, 3/4 view facing right, with a huge golden mane - shown ONLY so you know the square size and where he stands; B a GUIDE on the same canvas and grid: the character in grey (only to place the prop, NOT to be drawn) and a rough of the prop - for a crane: its olive arm through its joints (dots), the red claw, the yellow rocket when it is held; for R's gear: the drum, the two antennas with red balls, the ring round the top of the mane; C the original game's frame, 3/4 view facing right (copy the prop's LOOK and its position from it, never its 3D shading); D (if attached) the crane already drawn for this set: draw the SAME crane.
Draw with the image generator ONE clean pixel-art picture of ONLY THE PROP, exactly where guide B has it: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner. DO NOT draw the character: everything but the prop stays transparent.
THE CRANE: a mechanical arm out of his backpack - olive-green metal segments in 3 shades (yellow-green lit edges) with dark bolts, round dark-olive joint housings, the widest segment about 5-6 squares thick, a RED CLAW with two jaws at its end; when held, a ROCKET in the claw about 11 squares long and 4-5 thick: a pale yellow body in 3 shades, red bands and red tail fins, a pale nose. Draw the WHOLE arm, also its root where his mane would hide it (it is laid behind him). The same crane in every picture of the set.
R'S GEAR: an olive drum on top of the mane, two springy grey-green coil antennas each ending in a red ball about 3 squares wide, a dark grey ring with a red rim lying round the top of the mane - draw only the parts in front of and above the mane, leave out the half of the ring behind the mane (this picture is laid over him).
One continuous 1-square near-black outline; flat 2-3 shade colours; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no fire, no smoke, no sparks, no lightning), no character, no background, no ground, no shadow, no text, no grid lines.
THE PROP: <one line from the list below>
```

最后一段，按图换（英文）：

- crane_peek: `THE PROP: the crane just coming out from behind the mane, folded, its claw holding the rocket upright behind the top of his head.`
- crane_peek2: `THE PROP: the crane just out and rising, its claw holding the rocket pointing up-right.`
- crane_up: `THE PROP: the crane raised high, the rocket held upright at the very top.`
- crane_up_empty: `THE PROP: the crane raised high as guide B, the claw EMPTY (no rocket).`
- crane_up_back: `THE PROP: the crane raised high and leaning back a little, holding the rocket.`
- crane_up_high: `THE PROP: the crane at its highest, holding the rocket.`
- crane_place: `THE PROP: the crane bent forward over his head and down in front of him on the image right, setting the rocket (the turret kit) down near the ground.`
- crane_lift: `THE PROP: the crane lifting back up after setting it down, the claw EMPTY, the arm in front of the top of his head.`
- crane_return: `THE PROP: the crane upright over his head again, the claw EMPTY, pointing right.`
- crane_fold: `THE PROP: the crane folding back into the backpack, only a short piece showing behind the mane, the claw EMPTY.`
- crane_cock: `THE PROP: the crane reaching forward and up, holding the rocket, about to fling it.`
- crane_throw: `THE PROP: the crane flung forward, the claw EMPTY and open (the grenade just thrown).`
- crane_recoil: `THE PROP: the crane pulling back after the throw, the claw EMPTY.`
- crane_aim: `THE PROP: the crane raised high, holding the rocket ready to fire.`
- crane_fire: `THE PROP: the crane jolted back by the launch, the claw EMPTY and open (the rocket just fired).`
- crane_recover: `THE PROP: the crane coming back after firing, the claw EMPTY.`
- crane_aim_empty: `THE PROP: the crane raised high, the claw EMPTY.`
- gear_drum: `THE PROP: R's gear starting: only the olive drum popped up on top of the mane, toward the back; no antennas, no ring yet.`
- gear_burst: `THE PROP: R's gear bursting out: the two coil antennas sprung up high from both sides of the top of his head with their red balls, the dark red-rimmed ring opened round the top of the mane, the drum still on top.`
- gear_settle: `THE PROP: R's gear settling: the coil antennas bounced back a little lower, the red balls still on top; the ring and the drum still there.`

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px，和 `0_design.png` 一样大**。
- **只有道具，没有黑默丁格本人**；位置和引导图一样。
- 17 张是同一条机械臂（每节粗细、颜色、关节、爪子、火箭都一样）；HELD 的有火箭，GONE 的爪子空着。
- R 的圆环只画露在头发外面的部分。外描边连续；没有任何特效。

## 交付（`outputs/heimerdinger-props/`）

- 20 张 `heimerdinger-prop-<名字>.png`；原始生成图原样放 `outputs/heimerdinger-props/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/heimerdinger_props_done.zip`。中间不要停，20 张都画完再交。**不要另做平滑缩小的"修复版"**。

## Claude 收到后（给 Claude 看）

- 量格子（约 12 px），从 raw/ 按格读回，颜色收成一套调色板，每张按引导图的位置对回画布（机械臂的根对准 `pack_heimerdinger_poses.py` 里 crane0 的位置）；机械臂放在他身后（头发挡住根部），R 的装置盖在他身上；拼进 `rig_heimerdinger.py` 的 skill（Q）、skill2（E）、attack_w（W，第三下普攻）、ult（R）。
