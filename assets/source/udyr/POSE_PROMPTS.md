# 兽灵行者 乌迪尔：动作关键姿势（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 乌迪尔四个姿态的造型用户已经定了（`0_design_A.png` 平常、`0_design_Q.png` 熊、`0_design_E.png` 公羊、`0_design_R.png` 凤凰，就是你上一步画的 A-1 / Q-1 / E-1 / R-1 缩到游戏格子数）。这一步照**英雄联盟的动作**画 **29 个关键姿势**，Claude 再用它们拼成动作帧。
> - 每个姿势附一张**参考图**（`<编号>_<名字>_guide.png`）：英雄联盟里那一帧，按我们的大小放在画布上，格子和地面线（红线）都画好了。**姿势、位置、大小照参考图**；**样子、颜色、格子、身材照造型**（参考图是 3D 渲染、身材比我们的瘦，不要照它的光影和细节，**要画得和造型一样壮、一样宽**）。
> - **一张图只画一个乌迪尔**，用这个姿势所属姿态的造型（编号后面写着 A / Q / E / R）。每格多少像素写在每个姿势里（大多和造型一样，几个特别高或特别宽的姿势格子小一点，好放进画布）。画布 **1254 × 1254**，网格从左上角 (0, 0) 对齐。
> - **头和脸照造型**（`1_head_*.png` 是四个头放大 8 倍）：两只冷蓝色的眼睛、浓眉、深色络腮胡、脸左边的蓝羽毛发辫、脏辫。头可以低、可以抬，但**脸的画法和颜色不变**，**不要比造型的头大或小**；**手臂、爪子、拳头、羊角、羽刃都不要挡住脸**。
> - **手臂和腿不能变形**：每条手臂、每条腿的粗细、长短和造型一样，关节往正确的方向弯（肘往后、膝盖往前），近处的腿全亮、远处的暗一档，两条腿分得开；**身子不要压扁到腿上**；兽灵部件（熊皮熊头、羊角、羽刃）的形状、颜色和造型一样，跟着手臂、身子动。

## 附图（压缩包 `udyr_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_A.png` / `_Q` / `_E` / `_R` | 四个造型（用户定的），在网格上，脚踩红线：**样子、颜色、格子、身材** |
| `1_head_A.png` / `_Q` / `_E` / `_R` | 四个头放大 8 倍：**脸** |
| `<编号>_<名字>_guide.png` | 每个姿势的参考图（英雄联盟那一帧，按要画的大小放好）：**姿势、位置、大小** |
| `<编号>_<名字>_league.png` | 同一帧的大图：看清楚手臂、腿、头怎么摆 |

## 姿势

| 参考图 | 名字 | 造型 | 每格 | 画什么 |
|---|---|---|---|---|
| `2_a_punch_guide.png` | **a_punch** | A 平常护头的造型 | 18 px | 出拳：远侧（画面右边）的拳头往前（右）直直打出去，手臂几乎伸直、和肩膀一样高，身子跟着往前转一点；近侧的拳头还举在脸旁边护着（普攻命中）；脚踩红线（y = 1188） |
| `3_run1_guide.png` | **run1** | A 平常护头的造型 | 18 px | 跑步 1：近侧（左）腿往前迈、脚跟着地，远侧腿在后面蹬地；两只拳头仍举在胸前护着；脚踩红线（y = 1188） |
| `4_run2_guide.png` | **run2** | A 平常护头的造型 | 18 px | 跑步 2：两腿交错、近侧腿在身下撑地，远侧腿抬起往前收（膝盖抬高）；拳头护着；脚踩红线（y = 1188） |
| `5_run3_guide.png` | **run3** | A 平常护头的造型 | 18 px | 跑步 3：远侧（右）腿往前迈、脚跟着地，近侧腿在后面蹬地；拳头护着；脚踩红线（y = 1188） |
| `6_run4_guide.png` | **run4** | A 平常护头的造型 | 18 px | 跑步 4：两腿交错、远侧腿在身下撑地，近侧腿抬起往前收；拳头护着；脚踩红线（y = 1188） |
| `7_d_hit_guide.png` | **d_hit** | A 平常护头的造型 | 13 px | 中招后仰：被打得往后仰，胸口挺出、头往后甩，两臂往后甩开，两腿还站着（阵亡第一下）；脚踩红线（y = 1209） |
| `8_d_kneel_guide.png` | **d_kneel** | A 平常护头的造型 | 18 px | 跪倒：两膝跪在地上，上身往前垂、头低下（看得见脸的上半部分），两只拳头撑在膝前的地上（阵亡）；脚踩红线（y = 1188） |
| `9_q_wind_guide.png` | **q_wind** | Q 熊姿态的造型 | 15 px | 熊爪蓄力：两只爪子张开甩到身后两边，身子微微往后仰，熊头护臂在远侧手臂上（熊姿态普攻的起手）；脚踩红线（y = 1200） |
| `10_q_swipe_guide.png` | **q_swipe** | Q 熊姿态的造型 | 15 px | 熊爪横扫：两只爪子从身后往前一起扫到身前（远侧爪子在前、往前下方抓），身子往前扑、压低（熊姿态普攻命中）；脚踩红线（y = 1200） |
| `11_q_roar_guide.png` | **q_roar** | Q 熊姿态的造型 | 12 px | 熊之怒吼：整个人直立起来、挺胸，两只爪子高高举过头顶，熊皮在背后（Q 狂暴爪击的施放）；脚踩红线（y = 1212） |
| `12_q_run1_guide.png` | **q_run1** | Q 熊姿态的造型 | 15 px | 熊跑 1：近侧腿往前迈，身子弓着往前冲，两只爪子垂在身前摆动；脚踩红线（y = 1200） |
| `13_q_run2_guide.png` | **q_run2** | Q 熊姿态的造型 | 15 px | 熊跑 2：两腿交错、远侧腿抬起往前收，两只爪子往后摆；脚踩红线（y = 1200） |
| `14_q_run3_guide.png` | **q_run3** | Q 熊姿态的造型 | 15 px | 熊跑 3：远侧腿往前迈，近侧腿在后面蹬，两只爪子往前摆；脚踩红线（y = 1200） |
| `15_q_run4_guide.png` | **q_run4** | Q 熊姿态的造型 | 15 px | 熊跑 4：两腿交错、近侧腿抬起往前收，两只爪子往后摆；脚踩红线（y = 1200） |
| `16_e_hook_guide.png` | **e_hook** | E 公羊姿态的造型 | 15 px | 公羊冲拳：往前大步弓步，身子往前探，远侧的拳头往前上方勾出去，头低着、两只羊角朝前（公羊姿态普攻命中）；脚踩红线（y = 1200） |
| `17_e_leap_guide.png` | **e_leap** | E 公羊姿态的造型 | 11 px | 跃起：整个人跳离地面，两腿收起，两只拳头举过头，头低着准备往下撞（晕眩那一击的起跳）；离地（照参考图的高度） |
| `18_e_slam_guide.png` | **e_slam** | E 公羊姿态的造型 | 15 px | 砸下：落地蹲得很低，头和羊角往前下方撞下去，两只拳头砸在地上（晕眩那一击命中）；脚踩红线（y = 1200） |
| `19_e_stomp_guide.png` | **e_stomp** | E 公羊姿态的造型 | 14 px | 跺脚：近侧的膝盖抬高准备往下跺，头往后一甩，两只拳头握在身前（E 踏火蛮冲的施放）；脚踩红线（y = 1204） |
| `20_e_run1_guide.png` | **e_run1** | E 公羊姿态的造型 | 14 px | 冲锋 1：近侧腿往前大步迈，身子前倾、头低着用羊角对着前面，两只拳头摆动；脚踩红线（y = 1204） |
| `21_e_run2_guide.png` | **e_run2** | E 公羊姿态的造型 | 15 px | 冲锋 2：两腿交错、远侧腿抬起往前收，身子前倾；脚踩红线（y = 1200） |
| `22_e_run3_guide.png` | **e_run3** | E 公羊姿态的造型 | 14 px | 冲锋 3：远侧腿往前大步迈，近侧腿在后面蹬，头低着；脚踩红线（y = 1204） |
| `23_e_run4_guide.png` | **e_run4** | E 公羊姿态的造型 | 15 px | 冲锋 4：两腿交错、近侧腿抬起往前收，身子前倾；脚踩红线（y = 1200） |
| `24_r_thrust_guide.png` | **r_thrust** | R 凤凰姿态的造型 | 13 px | 凤凰掌击：往前弓步，远侧手臂带着羽刃往前直推出去，近侧手臂往后伸，像展翅一扫（凤凰姿态普攻命中）；脚踩红线（y = 1209） |
| `25_r_crouch_guide.png` | **r_crouch** | R 凤凰姿态的造型 | 11 px | 蓄势：蹲低，两臂带着羽刃往后下方收，像收拢翅膀（R 极凌飓风的起手）；脚踩红线（y = 1221） |
| `26_r_flap_guide.png` | **r_flap** | R 凤凰姿态的造型 | 11 px | 振翅腾空：整个人跳到空中，两臂带着羽刃高高举起张开，像凤凰展翅，头发往上飘（R 极凌飓风的施放）；离地（照参考图的高度） |
| `27_r_run1_guide.png` | **r_run1** | R 凤凰姿态的造型 | 12 px | 凤凰跑 1：近侧腿往前迈，两臂带着羽刃往后张开，像滑翔的翅膀；脚踩红线（y = 1212） |
| `28_r_run2_guide.png` | **r_run2** | R 凤凰姿态的造型 | 13 px | 凤凰跑 2：两腿交错、远侧腿抬起往前收，两臂往后张开；脚踩红线（y = 1209） |
| `29_r_run3_guide.png` | **r_run3** | R 凤凰姿态的造型 | 12 px | 凤凰跑 3：远侧腿往前迈，近侧腿在后面蹬，两臂往后张开；脚踩红线（y = 1212） |
| `30_r_run4_guide.png` | **r_run4** | R 凤凰姿态的造型 | 13 px | 凤凰跑 4：两腿交错、近侧腿抬起往前收，两臂往后张开；脚踩红线（y = 1209） |

## 提示词（同一段，每个姿势换最后一句）

附这个姿势所属姿态的 `0_design_*`、`1_head_*`，和这个姿势的 `guide`、`league` 两张图。**用 image_gen 画。**

```text
Attached images: 0 the character's approved pixel-art design at game size in the stance this pose belongs to (see the last line); 1 his head enlarged 8x; the GUIDE: League's own frame of the pose, a 3D render placed at exactly the size and place to draw it on the grid, the red line the ground (the render's body is slimmer than ours); the LEAGUE image: the same frame large, to read the arms, the legs and the head.
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), BIG SQUARES aligned on one straight grid from the canvas corner (the square size is given in the last line), ONE character. Copy the POSE, the PLACE and the SIZE from the guide; copy the LOOK, the COLOURS, the BUILD (as burly and broad as the design, never as slim as the render) and the HEAD from the design - never the render's 3D shading or extra detail.
The head and face exactly as the design's: both cold blue eyes, the heavy brows, the dark beard, the bright blue feather braid by the left of his face, the dreadlocks (the head lowered or raised as the pose needs, never bigger or smaller); the arms, fists, claws, horns and blades NEVER cover his face. Every arm and leg as thick and as long as the design's, the joints bending the right way (elbows back, knees forward), the legs clearly apart, the near leg in full tone and the far leg a step darker, the body never squashed onto the legs; the spirit parts (the bear hide and head, the ram horns, the feather blades) the same shape and colours as the design's, moving with the arms and the body. One continuous 1-square near-black outline round the figure; every material in its own 2-4 flat shades; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No spell effects (no lightning, no fire, no ice, no shield glow, no ghostly spirit animals, no motion trails), no background, no ground, no cast shadow, no text, no grid lines.
```

最后一句，按要画的那一个姿势换：

- **a_punch**（`udyr-pose-a_punch.png`）：
  ```text
  POSE A_PUNCH: PUNCH - the FAR fist (image right) driven straight forward to the right at shoulder height, the arm nearly straight, the body turned a little into the blow; the NEAR fist stays up beside his face as a guard (not over the face). Draw his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee guards over grey-blue fur, dark teal leg wraps and sandals - in exactly the pose of guide image 2, at the guide's place and size, every square exactly 18 px, his soles on the red line (y 1188).
  ```
- **run1**（`udyr-pose-run1.png`）：
  ```text
  POSE RUN1: RUN 1 - the NEAR leg (image left) stepping forward with its heel down, the FAR leg behind pushing off; both fists still up before his chest in the guard. Draw his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee guards over grey-blue fur, dark teal leg wraps and sandals - in exactly the pose of guide image 3, at the guide's place and size, every square exactly 18 px, his soles on the red line (y 1188).
  ```
- **run2**（`udyr-pose-run2.png`）：
  ```text
  POSE RUN2: RUN 2 - passing: the near leg under him on the ground, the far leg lifted and swinging forward (its knee raised); the fists up in the guard. Draw his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee guards over grey-blue fur, dark teal leg wraps and sandals - in exactly the pose of guide image 4, at the guide's place and size, every square exactly 18 px, his soles on the red line (y 1188).
  ```
- **run3**（`udyr-pose-run3.png`）：
  ```text
  POSE RUN3: RUN 3 - the FAR leg (image right) stepping forward with its heel down, the NEAR leg behind pushing off; the fists up in the guard. Draw his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee guards over grey-blue fur, dark teal leg wraps and sandals - in exactly the pose of guide image 5, at the guide's place and size, every square exactly 18 px, his soles on the red line (y 1188).
  ```
- **run4**（`udyr-pose-run4.png`）：
  ```text
  POSE RUN4: RUN 4 - passing: the far leg under him on the ground, the near leg lifted and swinging forward (its knee raised); the fists up in the guard. Draw his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee guards over grey-blue fur, dark teal leg wraps and sandals - in exactly the pose of guide image 6, at the guide's place and size, every square exactly 18 px, his soles on the red line (y 1188).
  ```
- **d_hit**（`udyr-pose-d_hit.png`）：
  ```text
  POSE D_HIT: STRUCK - thrown back by the killing blow: the chest pushed out, the head thrown back, both arms flung out behind him, still on his feet (the death's first moment). Draw his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee guards over grey-blue fur, dark teal leg wraps and sandals - in exactly the pose of guide image 7, at the guide's place and size, every square exactly 13 px, his soles on the red line (y 1209).
  ```
- **d_kneel**（`udyr-pose-d_kneel.png`）：
  ```text
  POSE D_KNEEL: KNEEL - fallen to both knees on the ground, the upper body slumped forward, the head bowed (the brows and eyes still visible), both fists resting on the ground before his knees (death). Draw his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee guards over grey-blue fur, dark teal leg wraps and sandals - in exactly the pose of guide image 8, at the guide's place and size, every square exactly 18 px, his soles on the red line (y 1188).
  ```
- **q_wind**（`udyr-pose-q_wind.png`）：
  ```text
  POSE Q_WIND: CLAWS BACK - both clawed paws flung out wide to the sides and back, the body rocked back a little, the bear's head still over the far fist (the bear's swipe winding up). Draw his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed - in exactly the pose of guide image 9, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **q_swipe**（`udyr-pose-q_swipe.png`）：
  ```text
  POSE Q_SWIPE: SWIPE - both clawed paws raked from behind to in front of him, the far paw (with the bear's head) clawing forward and down, the body lunging forward and low (the bear's swipe landing). Draw his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed - in exactly the pose of guide image 10, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **q_roar**（`udyr-pose-q_roar.png`）：
  ```text
  POSE Q_ROAR: ROAR - risen upright to his full height, the chest out, both clawed paws raised high over his head, the bear hide hanging down his back (casting Wilding Claw). Draw his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed - in exactly the pose of guide image 11, at the guide's place and size, every square exactly 12 px, his soles on the red line (y 1212).
  ```
- **q_run1**（`udyr-pose-q_run1.png`）：
  ```text
  POSE Q_RUN1: BEAR RUN 1 - the near leg stepping forward, the body hunched and charging forward, both paws hanging low before him. Draw his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed - in exactly the pose of guide image 12, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **q_run2**（`udyr-pose-q_run2.png`）：
  ```text
  POSE Q_RUN2: BEAR RUN 2 - passing, the far leg lifted and swinging forward, both paws swinging back. Draw his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed - in exactly the pose of guide image 13, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **q_run3**（`udyr-pose-q_run3.png`）：
  ```text
  POSE Q_RUN3: BEAR RUN 3 - the far leg stepping forward, the near leg pushing off behind, both paws swinging forward. Draw his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed - in exactly the pose of guide image 14, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **q_run4**（`udyr-pose-q_run4.png`）：
  ```text
  POSE Q_RUN4: BEAR RUN 4 - passing, the near leg lifted and swinging forward, both paws swinging back. Draw his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed - in exactly the pose of guide image 15, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **e_hook**（`udyr-pose-e_hook.png`）：
  ```text
  POSE E_HOOK: HOOK - a long lunge forward, the body thrust ahead, the FAR fist hooking forward and up at the target, the head down with both great horns pointing forward (the ram's punch landing). Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 16, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **e_leap**（`udyr-pose-e_leap.png`）：
  ```text
  POSE E_LEAP: LEAP - sprung up off the ground, the legs tucked under him, both fists raised over his head, the head lowered to ram down (the stunning blow taking off). Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 17, at the guide's place and size, every square exactly 11 px, his lowest point as high off the ground as in the guide.
  ```
- **e_slam**（`udyr-pose-e_slam.png`）：
  ```text
  POSE E_SLAM: SLAM - landed in a deep crouch, the head and the horns driven forward and down, both fists smashed on the ground (the stunning blow landing). Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 18, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **e_stomp**（`udyr-pose-e_stomp.png`）：
  ```text
  POSE E_STOMP: STAMP - the near knee raised high to stamp down, the head tossed back, both fists clenched before him (casting Blazing Stampede). Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 19, at the guide's place and size, every square exactly 14 px, his soles on the red line (y 1204).
  ```
- **e_run1**（`udyr-pose-e_run1.png`）：
  ```text
  POSE E_RUN1: CHARGE 1 - the near leg striding far forward, the body leaning ahead, the head down with the horns aimed forward, the fists pumping. Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 20, at the guide's place and size, every square exactly 14 px, his soles on the red line (y 1204).
  ```
- **e_run2**（`udyr-pose-e_run2.png`）：
  ```text
  POSE E_RUN2: CHARGE 2 - passing, the far leg lifted and swinging forward, the body leaning ahead. Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 21, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **e_run3**（`udyr-pose-e_run3.png`）：
  ```text
  POSE E_RUN3: CHARGE 3 - the far leg striding forward, the near leg pushing off behind, the head down. Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 22, at the guide's place and size, every square exactly 14 px, his soles on the red line (y 1204).
  ```
- **e_run4**（`udyr-pose-e_run4.png`）：
  ```text
  POSE E_RUN4: CHARGE 4 - passing, the near leg lifted and swinging forward, the body leaning ahead. Draw his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a white-grey wrapping) growing from his shoulders and back over his head - in exactly the pose of guide image 23, at the guide's place and size, every square exactly 15 px, his soles on the red line (y 1200).
  ```
- **r_thrust**（`udyr-pose-r_thrust.png`）：
  ```text
  POSE R_THRUST: WING THRUST - a lunge forward, the FAR arm with its feather blades thrust straight out ahead, the near arm stretched back behind him, like a wing sweeping forward (the phoenix's strike landing). Draw his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots along both arms and his back, his dreadlocks swept up - in exactly the pose of guide image 24, at the guide's place and size, every square exactly 13 px, his soles on the red line (y 1209).
  ```
- **r_crouch**（`udyr-pose-r_crouch.png`）：
  ```text
  POSE R_CROUCH: GATHER - crouched low, both arms with their feather blades swept back and down like folded wings (Wingborne Storm winding up). Draw his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots along both arms and his back, his dreadlocks swept up - in exactly the pose of guide image 25, at the guide's place and size, every square exactly 11 px, his soles on the red line (y 1221).
  ```
- **r_flap**（`udyr-pose-r_flap.png`）：
  ```text
  POSE R_FLAP: TAKE WING - leapt into the air, both arms with their feather blades raised high and spread like a phoenix's wings, the hair streaming up (casting Wingborne Storm). Draw his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots along both arms and his back, his dreadlocks swept up - in exactly the pose of guide image 26, at the guide's place and size, every square exactly 11 px, his lowest point as high off the ground as in the guide.
  ```
- **r_run1**（`udyr-pose-r_run1.png`）：
  ```text
  POSE R_RUN1: PHOENIX RUN 1 - the near leg stepping forward, both arms with their blades spread back like gliding wings. Draw his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots along both arms and his back, his dreadlocks swept up - in exactly the pose of guide image 27, at the guide's place and size, every square exactly 12 px, his soles on the red line (y 1212).
  ```
- **r_run2**（`udyr-pose-r_run2.png`）：
  ```text
  POSE R_RUN2: PHOENIX RUN 2 - passing, the far leg lifted and swinging forward, the arms spread back. Draw his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots along both arms and his back, his dreadlocks swept up - in exactly the pose of guide image 28, at the guide's place and size, every square exactly 13 px, his soles on the red line (y 1209).
  ```
- **r_run3**（`udyr-pose-r_run3.png`）：
  ```text
  POSE R_RUN3: PHOENIX RUN 3 - the far leg stepping forward, the near leg pushing off behind, the arms spread back. Draw his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots along both arms and his back, his dreadlocks swept up - in exactly the pose of guide image 29, at the guide's place and size, every square exactly 12 px, his soles on the red line (y 1212).
  ```
- **r_run4**（`udyr-pose-r_run4.png`）：
  ```text
  POSE R_RUN4: PHOENIX RUN 4 - passing, the near leg lifted and swinging forward, the arms spread back. Draw his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots along both arms and his back, his dreadlocks swept up - in exactly the pose of guide image 30, at the guide's place and size, every square exactly 13 px, his soles on the red line (y 1209).
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；每个姿势的格子大小照表。
- 用对了姿态的造型（A 平常、Q 熊、E 公羊、R 凤凰）；身材和造型一样壮；脸照造型、两只眼睛看得见、蓝羽毛发辫在；**手臂、爪子、羊角、羽刃不挡脸**。
- 手臂和腿的粗细长短和造型一样、关节方向对、两条腿分开；兽灵部件和造型一样；外描边连续；没有任何技能特效。

## 交付（`outputs/udyr-poses/`）

- 29 张 `udyr-pose-<名字>.png`；原始生成图原样放 `outputs/udyr-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/udyr_poses_done.zip`。中间不要停，全部画完再交。

## Claude 收到后（给 Claude 看）

- 读回（design_shyvana_poses.py 的做法）：每张按造型的头匹配出 Codex 实际的格子和身体比例，按造型的格子取样、颜色贴到造型的色板、把造型的头原样贴在 Codex 的头上（一张脸用在所有帧），描边闭合；8 倍检查手臂和腿。
- 拼帧（rig_udyr.py）：普攻 = 待机 → a_punch；q_attack = q_wind → q_swipe；skill = q_roar；e_attack = e_hook；e_stun = e_leap → e_slam；skill2 = e_stomp；r_attack = r_thrust；ult = r_crouch → r_flap；跑步各 4 张；死亡 = 姿态受击 → d_hit → d_kneel；时长照英雄联盟的动作。
