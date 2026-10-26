# 不落魔锋 亚恒：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 亚恒的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A 选定稿，缩到游戏大小定稿：3/4 正面朝右的 Q 版暗裔武士——浅蓝灰色皮肤、红眼睛、白金长发；金色头冠和两只高高的金角；白金板甲、金色腰带、深宝蓝长腰布；深蓝灰护腿、金护膝、光脚踩在金脚环里；**背后两只收拢的暗裔翅膀**（外面深海军蓝、里面浅白蓝带暗红纹、金色骨架）垂到小腿；**一把比他还长的金色暗裔长刀**斜在身前：近侧那只手（画面左上、胸口旁）握在刀杆上，刀刃一头在画面左上，矛头一头在画面右下，远侧那只手在画面右边腰旁握着刀杆）。`2b_wings.png` 是第 0 步的 B（同一个人展开翅膀、举刀），**翅膀张开的姿势照它的翅膀画**。
> - 英雄联盟里他抡长刀横扫、两连斩、蹲下再往上挑、往前直刺再拽回来、压低身子冲刺后绕身一斩、展翼升空再落地插刀、倒下后单膝跪起复活，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **20 个姿势**（14 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打、复活站起之后的样子我从定稿和 B 本身来做，不用画。
> - **每张都是同一个亚恒**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆的金腰带到脖子根），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**紫线 = 近侧的手臂（主要握刀的那只）**，**橙线 = 远侧的手臂**；手臂线的第一个点是肩膀，**大一点的圆点是手**；**灰框 = 头的位置**（金角、头冠、头发、脸）；**深色长线 = 长刀的刀杆**，**粗的金色一段 = 刀刃那一头**（弯弯的金色大刃），**细的金色一小段 = 矛头那一头**（没有手握着的时候它就是掉落 / 飞出去的长刀）；**深蓝半透明的形状 = 翅膀**（一块 = 收拢垂在背后；两块 = 向两边张开，后面那块暗一点）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版大头、高大宽肩——**每条腿从胯到脚底约 29 格**；**手臂从肩膀到手指尖约 23–25 格**；头（金角、头冠、头发连脸）22 × 33 格；**长刀从刀刃尖到矛头尖约 116 格**（比他人还长，和定稿一样，不放大不缩短；手握在刀杆上的位置可以变）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩甲里长出来，不能悬空；腰布、翅膀跟着身子走。
> - **翅膀和腰布不能躺在地上**：收拢的翅膀最低到小腿、翅尖离地；跑和冲刺时翅膀往后掠；张开时照 `2b_wings.png`。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只金角、头冠、两只红眼睛一样高、冷脸）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、长刀**不要盖住脸**（眼睛和嘴）；从头附近经过时画在头**后面**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作的感觉照它**，长相照定稿。英雄联盟的模型在空中的几个片段里长刀会掉在地上（渲染的问题），**长刀一律照骨架的深色长线画**；英雄联盟的他手臂长、大人比例，我们的是 Q 版大头：**照骨架的长短和长刀、翅膀的位置画，不照原版的长短**。

## 20 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `zaahen-pose-a_wind.png` | 普攻起手：两腿站开、膝盖微弯，双手把长刀高高举到头的左后上方（刀刃一头朝上、朝后，不挡脸），翅膀收在身后（横扫前的蓄力） |
| 4 | `zaahen-pose-a_sweep.png` | 普攻横扫：弓步往前，双手把长刀往前下方（画面右边）横扫出去，刀刃一头在身前低处、朝右，矛头一头甩到身后，翅膀收在身后（横扫打中） |
| 5 | `zaahen-pose-q_cut1.png` | 第一斩：身子往前压，双手握刀从左往右横着斩出（刀刃一头平平地伸在身前胸口高、朝右），翅膀收在身后（暗裔长刀：第一下） |
| 6 | `zaahen-pose-q_cut2.png` | 第二斩：身子一转，双手把长刀从下往右上方斜着挑斩（刀刃一头指向右上方高处），翅膀半张开（暗裔长刀：第二下） |
| 7 | `zaahen-pose-q_crouch.png` | 下蹲蓄力：深深地蹲下、身子前倾，双手把长刀压低在身前（刀刃一头朝右下方、快碰到地面），翅膀收在身后（暗裔长刀第二段：挑飞前） |
| 8 | `zaahen-pose-q_up.png` | 上挑：猛地站直、往上一跃（脚离地约 2 格），双手把长刀往上挑（刀刃一头竖直朝上、在头的右前上方，不挡脸），翅膀半张开（暗裔长刀第二段：挑飞） |
| 9 | `zaahen-pose-w_thrust.png` | 直刺：大弓步往前冲，近侧的手把长刀直直地往前（画面右边）刺出去、手臂伸直，刀刃一头朝前平伸，远侧的手在后面握着刀杆，翅膀收在身后（厄影回锋：刺出） |
| 10 | `zaahen-pose-w_pull.png` | 回拽：身子往后仰、重心落在后脚，双手把长刀往怀里拽回来（刀刃一头在身前、略朝下），翅膀半张开（厄影回锋：把人拽回来） |
| 11 | `zaahen-pose-e_dash.png` | 冲刺：身子压得很低、几乎平着往前（画面右边）冲（脚离地约 3 格），双手把长刀拖在身前右下方（刀刃一头朝右下），翅膀往后掠（赤金突袭：冲刺） |
| 12 | `zaahen-pose-e_spin.png` | 绕身斩：身子转了大半圈，双手把长刀在身后横着抡开（刀刃一头甩到画面左边、平平的），翅膀半张开（赤金突袭：绕身一斩） |
| 13 | `zaahen-pose-r_crouch.png` | 起跳下蹲：深深地蹲下，两只翅膀在身后向两边大大张开（照附图 2b 的翅膀），双手把长刀压在身侧（刀刃一头朝左下），抬头（大赦：升空前） |
| 14 | `zaahen-pose-r_rise.png` | 升空：飞在空中（脚离地约 14 格），两只翅膀向上、向两边张开，双手在胸前反握长刀、刀刃一头竖直朝下（准备往下插），两腿并拢垂着（大赦：升空） |
| 15 | `zaahen-pose-r_stab.png` | 落地插刀：单膝跪地落下（近侧膝盖着地），双手把长刀狠狠插进身前的地里（刀刃一头竖直朝下、插在右前方地上），翅膀半张开（大赦：向下戳刺） |
| 16 | `zaahen-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后蹬）：身子往前倾，近侧的手把长刀拖在身后（刀刃一头朝左下、离地），另一只手往前摆，翅膀往后掠 |
| 17 | `zaahen-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手摆到身边，长刀还拖在身后 |
| 18 | `zaahen-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后蹬）：身子往前倾，近侧拿刀的手往前摆（长刀斜在身侧），另一只手往后摆 |
| 19 | `zaahen-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手摆到身边 |
| 20 | `zaahen-pose-d_fall.png` | 被打倒：被打得往后（画面左边）仰倒、膝盖发软，两只手臂往上甩开，长刀从手里飞出去（手里空），翅膀松松地张开（死亡第一下） |
| 21 | `zaahen-pose-d_down.png` | 跪倒：双膝跪在地上，身子往前垂、两只手撑在膝盖前的地上，翅膀垂下来盖在背上，长刀横躺在他身前的地上（死亡：倒地） |
| 22 | `zaahen-pose-rv_kneel.png` | 复活跪起：单膝跪地（近侧膝盖着地），近侧的手把长刀竖直拄在身旁的地上（刀刃一头朝上），另一只手按在膝盖上，翅膀收拢裹在身后，抬头看向右前方（被动复活：重新站起之前；站起来之后就是 B 的样子） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`；翅膀张开的姿势再加 `2b_wings.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (soles on y 1188) - a chibi TALL PROUD DARKIN WARRIOR with a BIG head: PALE BLUE-GREY skin, RED eyes, long WHITE-BLOND hair, a GOLD CIRCLET with TWO TALL GOLDEN HORNS; WHITE-AND-GOLD plate armour on the chest, shoulders and forearms, a gold belt, a long DEEP ROYAL BLUE loincloth, dark blue-grey leggings with gold knee guards, bare feet in gold ankle bands; TWO FOLDED DARKIN WINGS hanging from his back to his calves (dark navy outside, pale white-blue inside with dark red veins, a gold bone edge); a GLAIVE LONGER THAN HE IS held diagonally in front of him: a dark shaft, a big CURVED GOLDEN BLADE at one end (upper left), a golden SPEAR POINT at the other (lower right), his NEAR hand on the shaft by his chest (upper left of his body), his FAR hand on the shaft at his far hip; B its HEAD shown 8x (22 squares wide, 33 tall: the horns, the circlet, the hair, the face); C a SKELETON on the same 1254 canvas and 9 px grid: green = the spine (the gold belt to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), PURPLE = the NEAR arm, ORANGE = the FAR arm, each arm line starting at the shoulder, the bigger dot on each arm = the hand, GREY BOX = where the head goes, the LONG DARK LINE = the glaive's shaft with its THICK GOLD END = the curved blade and its THIN GOLD END = the spear point (a glaive no hand holds is falling or flying), the TRANSLUCENT NAVY SHAPES = the wings (one shape = folded behind him; two shapes = spread out to both sides, the far one darker), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the feel of the POSE from it, never its 3D look or its long realistic limbs; where its glaive lies on the ground the skeleton's glaive line rules); E (if attached) the wings-spread picture of the same character: the shape and colours of his OPEN wings; F (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions - each leg about 29 squares from the hip to the sole, each arm about 23-25 squares from the shoulder to the fingertips, the glaive about 116 squares from the blade's tip to the spear point, exactly as in image A. Lay the body along the skeleton: the armoured torso and the gold belt along the green line, the blue loincloth moving with the body (never lying on the ground), each leg along its line (bending at the dots: the dark leggings, the gold knee guard, the bare foot - the SAME thickness, length and colours as in image A), each arm from its shoulder plate along its line (the gold-and-white forearm armour and the hand, never floating). THE GLAIVE: the same glaive as in image A drawn exactly on the dark line - the curved golden blade on the thick gold end, the spear point on the thin gold end, the hands gripping the shaft where the hand dots are. THE WINGS: on the navy shapes - folded like image A when there is one shape, spread like image E when there are two. Where the glaive or an arm passes the grey box it goes BEHIND his head. Never stretch or shorten a limb or the glaive, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (both golden horns, the circlet, the white-blond hair, the face to the front-right, both red eyes at the same height) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or glaive covers the face (the eyes and the mouth).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no blade trails, no dark red mist, no dash trail, no shockwave, no revive light, no dust, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - feet apart, knees a little bent, BOTH hands raising the glaive high behind the upper left of his head (the blade end up and back, never over the face), the wings folded behind him.`
- a_sweep: `SWEEP - lunging forward, BOTH hands sweeping the glaive out low to the front (the image right), the blade end out in front low down, the spear end swung behind him, the wings folded.`
- q_cut1: `FIRST CUT - leaning in, BOTH hands slashing the glaive across from left to right, the blade end out level in front at chest height (the image right), the wings folded.`
- q_cut2: `SECOND CUT - turning through, BOTH hands slashing the glaive up and across to the upper right (the blade end high at the upper right), the wings half open.`
- q_crouch: `CROUCH - squatting deep, leaning forward, BOTH hands holding the glaive low in front of him (the blade end down to the lower right, almost touching the ground), the wings folded.`
- q_up: `UPPERCUT - springing up straight (the feet about 2 squares off the ground), BOTH hands thrusting the glaive up (the blade end straight up beside the front of his head, never over the face), the wings half open.`
- w_thrust: `THRUST - a long lunge forward, the NEAR arm stabbing the glaive straight out to the front (the image right), the arm straight, the blade end level in front, the far hand behind it on the shaft, the wings folded.`
- w_pull: `PULL - leaning back, the weight on the back foot, BOTH hands yanking the glaive back toward his chest (the blade end in front of him, a little down), the wings half open.`
- e_dash: `DASH - very low, rushing forward almost flat (to the image right, about 3 squares off the ground), BOTH hands trailing the glaive low in front (the blade end down to the lower right), the wings swept back.`
- e_spin: `SPIN - turned most of the way round, BOTH hands swinging the glaive out level behind him (the blade end out to the image left, level), the wings half open.`
- r_crouch: `CROUCH TO LEAP - squatting deep, BOTH WINGS spread wide behind him (the wings of image 2b), BOTH hands holding the glaive low at his side (the blade end down to the lower left), the chin up.`
- r_rise: `RISEN - flying in the air (the feet about 14 squares off the ground), BOTH WINGS spread up and out, BOTH hands at his chest holding the glaive reversed, the blade end straight DOWN (ready to stab down), the legs together hanging.`
- r_stab: `LANDING STAB - landed on one knee (the near knee on the ground), BOTH hands driving the glaive down into the ground in front of him (the blade end straight down into the ground at the front right), the wings half open.`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg pushing off behind, the body leaning forward, the near hand trailing the glaive behind him (the blade end down to the lower left, clear of the ground), the far arm swinging forward, the wings swept back.`
- run2: `RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, both arms passing close to his sides, the glaive still trailing behind.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg pushing off behind, the body leaning forward, the near (glaive) hand swinging forward (the glaive slanting at his side), the far arm back.`
- run4: `RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, both arms passing close to his sides.`
- d_fall: `KNOCKED BACK - thrown back toward the image left, the knees giving way, both arms flung up, the glaive flying out of his hands (the hands empty), the wings loosely open.`
- d_down: `COLLAPSED - down on both knees, the body slumped forward, both hands propped on the ground in front of the knees, the wings hanging down over his back, the glaive lying flat on the ground in front of him.`
- rv_kneel: `RISING AGAIN - kneeling on one knee (the near knee on the ground), the near hand planting the glaive upright on the ground beside him (the blade end up), the far hand on his knee, the wings folded round behind him, looking up to the front-right (after it he stands as B).`

## 交回前请检查

- **20 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 9 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 29 格、手臂约 23–25 格、长刀约 116 格，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个亚恒：**同一个头（照图 B，两只金角、头冠、白金长发、两只红眼睛一样高、脸朝右前方）**、同样粗的手臂和腿、同样的白金板甲和深宝蓝腰布；长刀在骨架深色长线的位置（刀刃在粗金色那一头）；翅膀在深蓝形状的位置（收拢或照 B 张开）；手和长刀没有盖住脸；翅膀和腰布不拖地；姿势沿着骨架；着地的脚在 y 1188。
- 所有图没有特效（刀光、暗红血雾、冲刺残影、冲击波、复活的光都不画）、没有骨架线、没有网格线、没有辅助形状。

## 交付（`outputs/zaahen-poses/`）

- `zaahen-pose-a_wind.png`、`zaahen-pose-a_sweep.png`、`zaahen-pose-q_cut1.png`、`zaahen-pose-q_cut2.png`、`zaahen-pose-q_crouch.png`、`zaahen-pose-q_up.png`、`zaahen-pose-w_thrust.png`、`zaahen-pose-w_pull.png`、`zaahen-pose-e_dash.png`、`zaahen-pose-e_spin.png`、`zaahen-pose-r_crouch.png`、`zaahen-pose-r_rise.png`、`zaahen-pose-r_stab.png`、`zaahen-pose-run1.png`、`zaahen-pose-run2.png`、`zaahen-pose-run3.png`、`zaahen-pose-run4.png`、`zaahen-pose-d_fall.png`、`zaahen-pose-d_down.png`、`zaahen-pose-rv_kneel.png`；
- 原始生成图原样放 `outputs/zaahen-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/zaahen_poses_done.zip`。中间不要停，20 张都画完再交。

## 附图（压缩包 `zaahen_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，深色长线 + 金色两头 = 长刀，深蓝形状 = 翅膀） |
| `1_head.png` | 定稿的头（8 倍，金角、头冠、头发、脸）：每个姿势都照它逐格画 |
| `2_design.png` | 亚恒定稿（每格 9 px，脚底 y 1188） |
| `2b_wings.png` | 第 0 步的 B（8 倍）：翅膀张开的样子 |
| `3_a_wind_*` … `22_rv_kneel_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 9 px），按格读回（design_locke_poses / design_trundle_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和长刀的长短，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_zaahen.py 的动作里，逐帧自查后才发合成 GIF（带技能的 GIF 也要）。
- 动作安排（照英雄联盟，标签见 tools/kit/build_zaahen.py）：普攻 attack = a_wind → a_sweep → 定稿；暗裔长刀 skill = q_cut1 → q_cut2（两连斩）；再按 skill_up = q_crouch → q_up（挑飞）；厄影回锋 skill2 = w_thrust → w_pull（主包末尾接 e_spin：并进 W 的绕身斩）；赤金突袭（附加包自己的 E，skill3 标签）= e_dash → e_spin；大赦 ult = r_crouch → r_rise → r_stab；死亡 dead = d_fall → d_down；被动复活（附加包：禁锢期间的画面 rv_rise）= d_down → rv_kneel → B（展翼举刀）；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。
