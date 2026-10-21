# 山脊之下的火焰 奥恩：第 2 步，动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 奥恩的造型用户已经定稿（`2_design.png`，你上一轮画的 A-3：3/4 正面朝右、大羊角、深红鬃毛胡子、青铜胸甲、近侧大锤、远侧熔岩手臂握小锤）。英雄联盟里他的普攻、技能、跑步、死亡都是**全身动作**——举锤、抡锤砸下、举起熔岩拳、熔岩拳砸地、喷火、低头冲撞、撞上后挺起、召唤、砸锤召唤、蓄力头槌、头槌、中招后仰、跪倒、趴倒，还有跑步——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **18 个姿势，每个一张图**（14 个动作姿势 + 4 帧跑步）。待机我从定稿本身来做，不用画。
> - **每张图都是同一个奥恩**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 16 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1248**），网格从画布左上角对齐。定稿上方特意留了 12 格空白，给举过头顶的锤子用。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边，戴青铜护肩）**，**紫线 = 远侧的熔岩手臂（画面右边）**，两条手臂的末端是拳头；**黄线 = 大锤**（锤柄尾 → 近侧拳头 → 锤头），**橄榄色线 = 小锤**（远侧拳头 → 锤头）；**灰框 = 头的位置（连羊角）**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；**两把锤子和定稿一样大**（钢青方锤头、深色锤柄），**锤柄笔直**。
> - **头一格一格照 `1_head.png` 画在灰框里**（连羊角、鬃毛、胡子 62 × 41 格，同样朝右前方、两只发光的眼睛都看得见）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（「中招后仰」「蓄力头槌」头可以整个往后仰一点、「低头冲撞」「头槌」可以整个往前低一点，脸还是这张脸）。手臂和锤子**不要盖住脸**（眼睛、鼻子、胡子）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。

## 18 个姿势

普通动作：

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| 3 | `ornn-pose-raise.png` | **举锤**：身子稍往后仰，近侧手把大锤举过头顶（锤头朝上、在头后面），远侧熔岩手握小锤垂在身侧，两腿分开 | 普攻起手 |
| 4 | `ornn-pose-smash.png` | **抡锤砸下**：身子前倾，近侧手把大锤砸到身前右边的地上（锤头着地），两腿大开 | 普攻出手 |
| 7 | `ornn-pose-breath.png` | **喷火**：身子前倾，头往前伸、张嘴（**不画火**），两只手和锤子压低在身侧，两腿大开站稳 | W 风箱烈息 |
| 14 | `ornn-pose-stagger.png` | **中招后仰**：站直往后仰、头往后甩，两只手臂垂在身体两边 | 死亡第一下 |
| 15 | `ornn-pose-kneel.png` | **跪倒**：双膝跪地，身子往前塌，两只拳头撑在身前地上，大锤掉在身边地上 | 死亡第二下 |
| 16 | `ornn-pose-lie.png` | **趴倒**：整个人趴在地上，头和羊角在画面右边，两腿往左伸，锤子落在身前地上 | 死亡 |
| 17–20 | `ornn-pose-run1.png` … `run4.png` | **跑步 4 帧**（见下面的英文） | 跑 |

**连招动作**（单独列出，用户：「有连招要做连招」）：

| 图 | 文件 | 姿势 | 连招里的位置 |
|---|---|---|---|
| 5 | `ornn-pose-q_raise.png` | **举起熔岩拳**：站直挺胸，远侧熔岩手握着小锤高高举过头顶，近侧手的大锤垂在身侧 | **Q → E** 第 1 下：Q 起手 |
| 6 | `ornn-pose-q_slam.png` | **熔岩拳砸地**：蹲低前扑，远侧熔岩拳（握小锤）砸在身前右边的地上，近侧大锤拖在身后 | **Q → E** 第 2 下：Q 火山裂隙，裂隙尽头升起熔岩柱 |
| 8 | `ornn-pose-charge.png` | **低头冲撞**：身子压得很低往前冲，羊角朝前像公羊顶人，两只手臂甩在身后，后腿离地往后蹬 | **Q → E** 第 3 下：E 灼热冲撞冲向柱子 |
| 9 | `ornn-pose-impact.png` | **撞上后挺起**：撞上之后身子往后一挺、挺胸抬头，两只手臂往两边张开，两腿大开站稳 | **Q → E** 第 4 下：撞碎柱子、周围的人被击飞 |
| 10 | `ornn-pose-summon.png` | **召唤**：近侧手把大锤高高举过头顶，远侧熔岩拳朝前伸直，两腿站稳 | **R1 → R2** 第 1 下：R 起手 |
| 11 | `ornn-pose-call.png` | **砸锤召唤**：大锤砸在身前地上，远侧熔岩拳朝前上方举起，身子前倾 | **R1 → R2** 第 2 下：公羊从远处冲过来 |
| 12 | `ornn-pose-butt_wind.png` | **蓄力头槌**：身子往后缩、头往后仰、羊角往后收，两只手垂在身侧，准备往前顶 | **R1 → R2** 第 3 下：公羊冲到身边 |
| 13 | `ornn-pose-headbutt.png` | **头槌**：往前猛扑，头压低、羊角朝前顶出去，近侧手臂和大锤甩在身后，前腿弓、后腿蹬 | **R1 → R2** 第 4 下：把公羊顶回去，沿路的人被击飞 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 16 px squares (soles on y 1248) - a huge hunched ram-horned demigod blacksmith with slate blue-grey skin: two enormous curled dark-iron horns with dark red runes and red-orange tips; a shaggy crimson mane and beard, glowing red-orange eyes, a dark ram nose, braids with steel rings; a bronze chest plate with curled ram horns, leather straps with bronze buckles, a belt with iron tongs, a dark plum apron, short legs in plum boots; the NEAR arm in a big bronze pauldron holding a BIG STEEL-BLUE HAMMER, the FAR arm MOLTEN from the elbow down (red-orange cracks, a red-hot fist) holding a SMALLER STEEL HAMMER; B its HEAD with the horns, the mane and the beard shown 8x (62 squares wide, 41 tall); C a SKELETON on the same 1254 canvas and 16 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left) ending at its fist, PURPLE = the FAR molten arm (image right) ending at its fist, YELLOW = the BIG HAMMER (handle end -> the near fist -> the hammer head), OLIVE = the SMALL HAMMER (the far fist -> its head), GREY BOX = where the head with its horns goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1248.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the thigh, the shin, the boot the SAME thickness, length and colours as in image A), each arm from its shoulder along its line to its fist (the arms grow from the shoulders, never floating), each hammer along its yellow / olive line, the SAME size as in image A with a STRAIGHT handle. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the horns, the mane, the face to the front-right, both glowing eyes, the nose, the beard and its rings) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm or hammer covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no fire, no sparks, no lava, no ram, no glow round the molten arm), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- raise: `RAISE - leaning back a little, the near arm lifting the big hammer high over his head (its head up, behind the horns), the molten far arm hanging at his side with the small hammer, the legs apart.`
- smash: `SMASH - leaning forward, the near arm swinging the big hammer down onto the ground ahead of him to the right (the hammer head on the ground), the legs wide apart.`
- q_raise: `RAISE THE MOLTEN FIST - standing tall, chest out, the molten far arm raised high over his head gripping the small hammer, the near arm and the big hammer hanging at his side.`
- q_slam: `FIST SLAM - crouching low and lunging forward, the molten far fist with the small hammer slammed onto the ground ahead of him to the right, the big hammer dragged behind him in the near hand.`
- breath: `FIRE BREATH - leaning forward, the head thrust forward with the mouth open (draw NO fire), both arms and hammers held low at his sides, the legs wide and planted.`
- charge: `RAM CHARGE - rushing forward very low, the horns pointed forward like a charging ram, both arms swept back behind him, the back foot off the ground pushing.`
- impact: `IMPACT - after the crash, rearing up, chest out and head up, both arms flung out to the sides, the legs wide and planted.`
- summon: `SUMMON - the near arm lifting the big hammer high over his head, the molten far fist thrust straight forward at chest height, the legs planted.`
- call: `CALL - the big hammer slammed on the ground in front of him, the molten far fist raised forward and up, the body leaning forward, the legs wide.`
- butt_wind: `HEADBUTT WIND-UP - drawing back, the head pulled back and the horns tucked back, both arms low at his sides, about to lunge forward.`
- headbutt: `HEADBUTT - lunging hard forward, the head low and the horns thrust forward, the near arm and the big hammer flung back behind him, the front knee bent, the back leg pushing.`
- stagger: `STAGGER - struck: standing tall and bending back, the head thrown back a little, both arms hanging at his sides.`
- kneel: `KNEEL - down on both knees, the body slumping forward, both fists propped on the ground in front of him, the big hammer dropped on the ground beside him.`
- lie: `LIE - lying face down on the ground, the head and horns at the image right, both legs stretched out to the left, the hammers on the ground in front of him.`
- run1: `RUN 1 - running hunched forward: the NEAR leg forward with its foot landing, the far leg pushing off behind, the molten far arm swinging forward, the near arm with the big hammer swinging back.`
- run2: `RUN 2 - running: the near leg under the body carrying him, the far knee lifted forward, the body one square higher, both arms at his sides.`
- run3: `RUN 3 - running: the FAR leg forward with its foot landing, the near leg pushing off behind, the near arm with the big hammer swinging forward low (never over the face), the molten far arm swinging back.`
- run4: `RUN 4 - running: the far leg under the body carrying him, the near knee lifted forward, the body one square higher, both arms at his sides.`

## 交回前请检查

- **18 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 16 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一个奥恩：**同一个头（照图 B，连羊角，脸朝右前方、两只发光的眼睛）**、同样粗的腿和手臂、同样大的两把锤（锤柄笔直）；手臂从肩膀长出来，没有盖住脸；姿势沿着骨架；着地的脚在 y 1248；羊角、锤子不出画。
- 所有图没有特效（不画火、熔岩柱、公羊）、没有骨架线、没有网格线。

## 交付（`outputs/ornn-poses/`）

- `ornn-pose-raise.png`、`-smash.png`、`-q_raise.png`、`-q_slam.png`、`-breath.png`、`-charge.png`、`-impact.png`、`-summon.png`、`-call.png`、`-butt_wind.png`、`-headbutt.png`、`-stagger.png`、`-kneel.png`、`-lie.png`、`-run1.png`、`-run2.png`、`-run3.png`、`-run4.png`；原始生成图原样放 `outputs/ornn-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ornn_poses_done.zip`。中间不要停，18 张都画完再交。

## 附图（压缩包 `ornn_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head.png` | 定稿的头连羊角（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 16 px，脚底 y 1248） |
| `3_raise_*` … `20_run4_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、锤子的长短粗细，和定稿比**（codex-legs-need-skeletons），头换成定稿的头（每帧同一张脸，脸不重画），再拼进 rig_ornn.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，`tools/kit/build_ornn.py` 的动作名）：`attack` = raise → smash → 定稿；`skill_w` = breath（撑满 0.75 秒）；`skill` = q_raise → q_slam；`skill2` = charge（冲刺中循环），`skill2_hit` = impact；`ult` = summon → call（撑到公羊回来），`ult_butt` = butt_wind → headbutt；`dead` = stagger → kneel → lie；`run` = run1–4；`idle` = 定稿呼吸；`hit` = stagger 的前半。
