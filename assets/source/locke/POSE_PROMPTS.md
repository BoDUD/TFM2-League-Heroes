# 灰烬驱魔人 洛克：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 洛克的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A 第一版，缩到游戏大小定稿：3/4 正面朝右的 Q 版年轻驱魔人——往后梳、头顶翘起的金发，紫 / 品红色的小圆眼镜，咧嘴笑露出白牙；深青绿色长风衣、高领子，袖子挽到小臂；里面宝蓝色敞领衬衫；腰上皮带、深紫棕色小包、一排银钉；深青黑长裤、浅灰皮鞋；风衣下摆在身后分成几条长飘带（深青绿渐到银灰）；**背上斜背着一只黑色六边形长棺匣**（品红紫箍带、银色菱形钉，从近侧肩膀后面斜到近侧大腿）；**近侧那只手（画面中间偏左、在肚子前面）反握一根长长的银钉**，钉尖朝右下；远侧那只手垂在画面右边的腰包旁）。
> - 英雄联盟里他拿钉子捅人、举手甩出三颗钉子、点燃灵魂张开双臂浮起来、瞬移后平着冲刺、用背带把棺匣抡起来扔出去，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **16 个姿势**（10 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个洛克**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 11 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根，高领子下面），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**紫线 = 近侧的手臂（拿钉子的那只）**，**橙线 = 远侧的手臂**；手臂线的第一个点是肩膀，**大一点的圆点是手**；**灰框 = 头的位置**（头发、眼镜、脸）；**深色半透明的长六边形 = 棺匣**（背在背上的姿势它贴在背后，跟着身子转；R 的两张里它飞在空中，**深色细线 = 背带**，一头在抓着它的那只手上）；**浅灰色短线 = 手里的银钉**（从手指向钉尖；没有浅灰线 = 手里没有钉子）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版大头、身子瘦长——**每条腿从胯到脚底约 28 格**；**近侧手臂从肩膀到手指尖约 24 格、远侧约 22 格**；头（头发连脸）27 × 25 格；**棺匣约 38 格长、11 格宽**，**银钉约 12 格长**（都和定稿一样，不放大不缩短）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从风衣肩膀里长出来，不能悬空；风衣、飘带、背上的棺匣跟着身子走。
> - **飘带不能躺在地上**：风衣身后的飘带跟着动作飘（跑和冲刺时往后飞），末端离开地面。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、金发、两片紫色圆镜片一样高、咧嘴笑）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、钉子、棺匣**不要盖住脸**（眼镜和嘴）；从头附近经过时画在头**后面**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的洛克另一只手常拿一把小锤，**我们的定稿没有锤子，不要画锤子**；英雄联盟的他手臂长、大人比例，我们的是 Q 版大头：**照骨架的长短和棺匣、钉子的位置画，不照原版的长短**。

## 16 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `locke-pose-a_wind.png` | 普攻起手：膝盖弯、身子往前压低，拿钉子的手往后上方收到肩膀旁边（钉尖朝前），另一只手往前伸、五指张开，棺匣背在背上（普攻第一下的蓄力） |
| 4 | `locke-pose-a_stab.png` | 普攻捅：弓步往前冲，拿钉子的手往前（画面右边）伸直、钉子往前下方捅出去，另一只手收到身后，棺匣背在背上（普攻捅中） |
| 5 | `locke-pose-q_raise.png` | 举钉：身子往后仰，拿钉子的手从头后面往左上方高高举起（三颗钉子握在手里，钉尖朝上，手在头的左后方，不挡脸），另一只手放在胸前，两腿站开（伏魔三钉起手） |
| 6 | `locke-pose-q_throw.png` | 甩钉：弓步往前，拿钉子的手从头顶往前（画面右边）甩下去、手臂伸直，手张开（钉子飞出去了，手里空），另一只手往后摆（伏魔三钉甩出） |
| 7 | `locke-pose-w_hunch.png` | 缩身：膝盖弯、身子往前缩，两只手握着钉子收在胸前（钉尖朝下，像要刺进自己的心口），头低一点（灵焰仪式起手：点燃灵魂） |
| 8 | `locke-pose-w_spread.png` | 展开：身子挺直、往上浮起（脚离地约 3 格），两只手臂向两边张开伸直（近侧手里拿着钉子），下巴抬起（灵焰仪式：灵魂点燃） |
| 9 | `locke-pose-e_blink.png` | 闪现落地：低低地蹲着、身子往前探，拿钉子的手往后甩在身后（钉子朝后），另一只手撑在身前（灰猎无影：瞬移出现） |
| 10 | `locke-pose-e_dash.png` | 冲刺：整个人几乎平着往前（画面右边）飞扑出去（离地约 6 格），拿钉子的手伸在最前面、钉尖朝前，另一只手收在身侧，两腿往后蹬（灰猎无影：冲向目标） |
| 11 | `locke-pose-r_swing.png` | 抡棺匣：身子扭向画面左边，近侧那只手（平时拿钉子的手，这时钉子插回腰上）抓住背带往左上方甩，棺匣离开背、飞在头的左上方（不挡脸），另一只手往前伸，两腿站稳（万魔狱起手） |
| 12 | `locke-pose-r_throw.png` | 扔棺匣：另一只手（远侧那只）高高甩向前上方（画面右上），背带拉直，棺匣横着飞在他头的右边上方（不挡脸），近侧的手垂在身侧（万魔狱：扔出法器） |
| 13 | `locke-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后蹬）：身子往前倾，拿钉子的手往后摆，另一只手往前摆，棺匣背在背上，飘带往后飞 |
| 14 | `locke-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手摆到身边 |
| 15 | `locke-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后蹬）：身子往前倾，拿钉子的手往前摆，另一只手往后摆 |
| 16 | `locke-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手摆到身边 |
| 17 | `locke-pose-d_fall.png` | 被打倒：被打得往后（画面左边）仰倒、膝盖发软，两只手臂往上甩开，钉子从手里飞出去（手里空），棺匣还背在背上（死亡第一下） |
| 18 | `locke-pose-d_down.png` | 靠坐在地：一屁股坐在地上，背靠着竖在身后的棺匣，膝盖弯起来，两只手臂软软地搭在膝盖上，头微微垂下，钉子掉在他身前的地上（死亡：倒地） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 11 px squares (soles on y 1188) - a chibi SLIM GRINNING YOUNG EXORCIST with a BIG head: golden blond hair swept back with a high flick, small ROUND PURPLE / MAGENTA GLASSES, a cocky grin with white teeth; a long DARK TEAL COAT with a high collar, the sleeves rolled up, a ROYAL BLUE shirt open in a deep V, a belt with dark purple-brown pouches and a row of silver nails, slim dark teal-black trousers, PALE GREY LOAFERS; the coat's skirt splitting behind him into long RIBBONS fading from dark teal to silver-grey; a LONG BLACK HEXAGONAL COFFIN-LIKE CASE slung diagonally on his back (magenta-purple bands, silver diamond studs) from behind his near shoulder down to his near thigh; his NEAR hand (in front of his belly) holding a LONG SILVER NAIL in a reverse grip, point down to the right; his far hand by the pouches on the image right; B its HEAD shown 8x (27 squares wide, 25 tall: the hair, the glasses, the face); C a SKELETON on the same 1254 canvas and 11 px grid: green = the spine (pelvis to the base of the neck, under the collar), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), PURPLE = the NEAR arm (the nail arm), ORANGE = the FAR arm, each arm line starting at the shoulder, the bigger dot on each arm = the hand, GREY BOX = where the head goes, the DARK TRANSLUCENT LONG HEXAGON = where the case goes (on his back, or in the air), a THIN DARK LINE = the case's strap from the hand holding it, the LIGHT GREY SHORT LINE = the silver nail from the hand to its point (no grey line: the hand is empty), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look, its long realistic limbs or its small hammer); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 11 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions - each leg about 28 squares from the hip to the sole, the near arm about 24 squares from the shoulder to the fingertips and the far arm about 22, the case about 38 squares long and 11 wide, the nail about 12 squares long, exactly as in image A. Lay the body along the skeleton: the torso with the open blue shirt and the belt along the green line, the teal coat, its collar and its ribbons moving with the body (the ribbons flying behind, never lying on the ground), each leg along its line (bending at the dots: the slim dark trousers, the pale grey loafer - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the teal sleeve rolled up, the forearm and hand, never floating). THE CASE: the same black case as in image A drawn exactly on the dark hexagon (on his back when it is there; in the air on its strap from the hand when the strap line is there). THE NAIL: the same silver nail in the near hand along the grey line. Where the case, an arm or the nail passes the grey box it goes BEHIND his head. Never stretch or shorten a limb, the case or the nail, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the blond hair, the face to the front-right, both purple lenses at the same height, the grin) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand, nail or case covers the face (the glasses and the grin).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no flying nails, no soul fire, no blink smoke, no dash trail, no glow of the case, no dust, no motion lines), no hammer, no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - knees bent, the body crouched and leaning forward, the NAIL hand pulled back up by his shoulder (the nail's point aimed forward), the free hand reaching forward with the fingers spread, the case on his back.`
- a_stab: `STAB - lunging forward, the NAIL hand thrust straight out to the image right, the nail stabbing forward and down, the free arm swept back behind him, the case on his back.`
- q_raise: `RAISE - leaning back, the NAIL hand raised high behind his head to the upper left (three nails in the fist, points up, the hand beyond the back of his head, never over the face), the free hand at his chest, the feet apart.`
- q_throw: `THROW - lunging forward, the NAIL arm whipped down from over his head to the front (the image right), straight, the hand open (the nails have flown: the hand is empty), the free arm swinging back.`
- w_hunch: `HUNCH - knees bent, the body hunched forward, BOTH hands gripping the nail at his chest (its point down, as if driving it into his own heart), the case on his back.`
- w_spread: `SPREAD - standing tall and rising off the ground (the feet about 3 squares up), BOTH arms spread wide out to the sides, straight (the nail in the near hand), the chin up, the case on his back.`
- e_blink: `BLINK LANDING - crouched very low, leaning forward, the NAIL arm flung back behind him (the nail pointing back), the free hand braced in front of him, the case on his back.`
- e_dash: `DASH - flying forward almost flat (to the image right, about 6 squares off the ground), the NAIL hand out in front with the point forward, the free arm tucked at his side, both legs kicked out behind.`
- r_swing: `SWING - twisting toward the image left, the NEAR hand (the nail hand; the nail tucked back in his belt) gripping the case's strap and swinging it up to the upper left, the case off his back in the air over the upper left of his head (never over the face), the free hand reaching forward, the feet planted.`
- r_throw: `THROW - the FREE (far) arm flung high to the upper right, the strap pulled straight, the case flying crosswise above and to the right of his head (never over the face), the near hand down at his side.`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg pushing off behind, the body leaning forward, the nail arm swinging back, the free arm forward, the case on his back, the coat ribbons flying behind.`
- run2: `RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, both arms passing close to his sides.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg pushing off behind, the body leaning forward, the nail arm swinging forward, the free arm back.`
- run4: `RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, both arms passing close to his sides.`
- d_fall: `KNOCKED BACK - thrown back toward the image left, the knees giving way, both arms flung up, the nail flying out of his hand (the hand empty), the case still on his back.`
- d_down: `SITTING SLUMPED - sat down on the ground leaning back against the case standing upright behind him, the knees drawn up, both arms resting limp on the knees, the head hanging a little, the nail lying on the ground in front of him.`

## 交回前请检查

- **16 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 11 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 28 格、近侧手臂约 24 格、远侧约 22 格、棺匣约 38 格长、银钉约 12 格，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个洛克：**同一个头（照图 B，金发、两片紫色圆镜片一样高、咧嘴笑、脸朝右前方）**、同样粗的手臂和腿、同样的青绿风衣和宝蓝衬衫；棺匣在骨架深色六边形的位置（背在背上或者挂在背带上）；钉子在浅灰线的位置；没有锤子；手、钉子、棺匣没有盖住脸；飘带不拖地；姿势沿着骨架；着地的脚在 y 1188。
- 所有图没有特效（飞出去的钉子、灵魂火、瞬移的烟、冲刺残影、法器的光都不画）、没有骨架线、没有网格线、没有辅助形状。

## 交付（`outputs/locke-poses/`）

- `locke-pose-a_wind.png`、`locke-pose-a_stab.png`、`locke-pose-q_raise.png`、`locke-pose-q_throw.png`、`locke-pose-w_hunch.png`、`locke-pose-w_spread.png`、`locke-pose-e_blink.png`、`locke-pose-e_dash.png`、`locke-pose-r_swing.png`、`locke-pose-r_throw.png`、`locke-pose-run1.png`、`locke-pose-run2.png`、`locke-pose-run3.png`、`locke-pose-run4.png`、`locke-pose-d_fall.png`、`locke-pose-d_down.png`；
- 原始生成图原样放 `outputs/locke-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/locke_poses_done.zip`。中间不要停，16 张都画完再交。

## 附图（压缩包 `locke_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，深色六边形 = 棺匣，浅灰线 = 银钉） |
| `1_head.png` | 定稿的头（8 倍，头发、眼镜、脸）：每个姿势都照它逐格画 |
| `2_design.png` | 洛克定稿（每格 11 px，脚底 y 1188） |
| `3_a_wind_*` … `18_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 11 px），按格读回（design_trundle_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和棺匣、钉子的长短，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_locke.py 的动作里，逐帧自查后才发合成 GIF（带技能的 GIF 也要）。
- 动作安排（照英雄联盟，标签见 tools/kit/build_locke.py）：普攻 attack = a_wind → a_stab → 定稿；伏魔三钉 skill = q_raise → q_throw；灵焰仪式（被动里的 W，`w` 标签：E 落到英雄身边时点燃）= w_hunch → w_spread；灰猎无影 skill2 = e_blink（瞬移出现）；E 之后的冲刺普攻 = e_dash；万魔狱 ult = r_swing → r_throw；死亡 dead = d_fall → d_down；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。W 期间的样子（第 0 步的 B 配色）从这些帧换色得到（`w_` 标签，附加包换）。
