# 解脱者 塞拉斯：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 塞拉斯的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右、赤裸上身、两只白色石头镣铐、金色长锁链）。英雄联盟里他的普攻、技能、跑步、死亡都是**全身动作**——蓄力、甩链、挥链横扫、跃起、突刺、单膝砸地、冲刺、甩出锁链、被锁链拉过去、中招后仰、跪倒、趴倒，还有跑步——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **16 个姿势，每个一张图**（12 个动作姿势 + 4 帧跑步）。待机我从定稿本身来做，不用画。
> - **每张图都是同一个塞拉斯**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 16 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1168**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边）**，两条手臂的末端是戴着白色石头镣铐的拳头；**黄线 = 近侧那条锁链**，**橄榄色线 = 远侧那条锁链**（都从各自的镣铐上垂下来）；**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；**镣铐和定稿一样大**（白石金边，比拳头大），锁链和定稿一样粗、一环一环的金链。
> - **头一格一格照 `1_head.png` 画在灰框里**（连头发和围巾 17 × 14 格，同样朝右前方、两只眼睛都看得见、黑胡子）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（死亡的「中招后仰」头可以整个往后仰一点，脸还是这张脸）。手臂、镣铐和锁链**不要盖住脸**（眼睛、胡子）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。

## 16 个姿势

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| 3 | `sylas-pose-wind.png` | **蓄力**：身子往后仰，近侧手臂甩到身后、远侧拳头收在胸前，两腿前后分开 | 普攻起手 |
| 4 | `sylas-pose-lash.png` | **甩链**：身子前冲，远侧手臂往前甩直、锁链跟着往前抽出去，近侧手臂在身后，前腿弓、后腿蹬 | 普攻出手 |
| 5 | `sylas-pose-spin.png` | **挥链横扫**：两腿大开蹲低，两只镣铐收到肚子前面，两条锁链往两边横着甩开 | 被动的横扫 |
| 6 | `sylas-pose-leap.png` | **跃起**：整个人腾空（脚离地约 8 格），两只镣铐高举过头，两腿收起，锁链在头顶两边甩开 | W 起跳、Q 起手 |
| 7 | `sylas-pose-stab.png` | **突刺**：落地往前扑，身子压低，两只镣铐一起往前捅出去（腰的高度），后腿往后蹬直 | W 弑君突刺 |
| 8 | `sylas-pose-slam.png` | **单膝砸地**：后腿跪地、前腿弓起，身子前倾，两只镣铐砸在身前地上，锁链往前平铺在地上 | Q 锁链鞭击 |
| 9 | `sylas-pose-dash.png` | **冲刺**：身子压低往前冲，两只手臂往身后甩，锁链拖在身后飘起来，后腿离地往后蹬 | E 潜掠 |
| 10 | `sylas-pose-throw.png` | **甩出锁链**：两腿大开站稳，远侧手臂朝前伸直、和肩一样高，近侧手臂拉到身后 | E 强掳、R 出手 |
| 11 | `sylas-pose-pull.png` | **被锁链拉过去**：整个人往前横着飞，远侧手臂朝前伸直，两腿在身后拖直 | E 把自己拉过去 |
| 12 | `sylas-pose-stagger.png` | **中招后仰**：站直往后仰、头往后甩，两只手臂垂在身体两边 | 死亡第一下 |
| 13 | `sylas-pose-kneel.png` | **跪倒**：双膝跪地，身子往前塌，两只镣铐撑在身前地上 | 死亡第二下 |
| 14 | `sylas-pose-lie.png` | **趴倒**：整个人趴在地上，头在画面右边，两腿往左伸，镣铐落在身前地上，锁链散在地上 | 死亡 |
| 15 | `sylas-pose-run1.png` | **跑步 1**：近侧腿在前着地，远侧手臂往前摆、近侧手臂往后摆，锁链拖在身后 | 跑 |
| 16 | `sylas-pose-run2.png` | **跑步 2**：近侧腿在身下撑地，远侧腿屈膝抬到前面，身子高一格 | 跑 |
| 17 | `sylas-pose-run3.png` | **跑步 3**：远侧腿在前着地，近侧手臂往前摆到身前（在下巴下面，不挡脸）、远侧手臂往后摆 | 跑 |
| 18 | `sylas-pose-run4.png` | **跑步 4**：远侧腿在身下撑地，近侧腿屈膝抬到前面，身子高一格 | 跑 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 16 px squares (soles on y 1168) - a lean, muscular, bare-chested man: long black hair swept back, a short black beard, warm skin, a dark red diamond brand on his near shoulder; a high dark teal-grey scarf round his neck with a gold neck plate and a dark diamond pendant; HUGE WHITE STONE MANACLES with gold trim on both forearms (bigger than his fists) and heavy GOLD square-link CHAINS hanging from them; a wide brown belt with teal cloth flaps, dark teal-green trousers, grey shin wraps, bare feet; B its HEAD with the hair and the scarf shown 8x (17 squares wide, 14 tall); C a SKELETON on the same 1254 canvas and 16 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left) ending at its manacled fist, PURPLE = the FAR arm (image right) ending at its manacled fist, YELLOW = the near chain and OLIVE = the far chain (each hanging from its manacle), GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1168.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the thigh, the shin, the bare foot the SAME thickness, length and colours as in image A), each arm from its shoulder along its line to its fist (the arms grow from the shoulders, never floating), the manacles the SAME size as in image A, each chain along its yellow / olive line with the same gold links as in image A. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both eyes, the black beard, the hair, the scarf) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, manacle or chain covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no blue magic, no lightning, no glow), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- wind: `WIND-UP - leaning back, the near arm swung far behind him at shoulder height, the far fist pulled in to his chest (below the chin), the legs apart one forward one back, the chains dangling.`
- lash: `LASH - lunging forward, the far arm flung straight forward with its chain whipping out ahead, the near arm behind him, the front knee bent, the back leg pushing.`
- spin: `WHIRL - a wide low crouch, both manacles pulled in before the belly, both chains swung out sideways to the left and right.`
- leap: `LEAP - in the air (the feet about 8 squares above the ground), both manacles raised high over his head, both legs tucked up, the chains flung out on both sides above him.`
- stab: `STAB - landed lunging forward low, both manacles thrust forward together at waist height, the back leg straight behind him.`
- slam: `SLAM - down on the back knee with the front knee up, the body leaning forward, both manacles slammed onto the ground in front of him, the chains lying flat on the ground ahead.`
- dash: `DASH - rushing forward low, both arms swept back behind him, the chains streaming behind, the back foot off the ground.`
- throw: `THROW - a wide planted stance, the far arm thrust straight forward at shoulder height, the near arm drawn back behind him.`
- pull: `PULLED - flying forward almost level, the far arm stretched straight ahead, both legs trailing straight behind him.`
- stagger: `STAGGER - struck: standing tall and bending back, the head thrown back a little, both arms hanging at his sides.`
- kneel: `KNEEL - down on both knees, the body slumping forward, both manacles resting on the ground in front of him.`
- lie: `LIE - lying face down on the ground, the head at the image right, both legs stretched out to the left, the manacles on the ground in front, the chains lying loose on the ground.`
- run1: `RUN 1 - running: the NEAR leg forward with its foot landing, the far leg pushing off behind, the far arm swinging forward, the near arm swinging back, the chains trailing behind.`
- run2: `RUN 2 - running: the near leg under the body carrying him, the far knee lifted forward, the body one square higher, both arms at his sides.`
- run3: `RUN 3 - running: the FAR leg forward with its foot landing, the near leg pushing off behind, the near arm swinging forward across below the chin (never over the face), the far arm swinging back.`
- run4: `RUN 4 - running: the far leg under the body carrying him, the near knee lifted forward, the body one square higher, both arms at his sides.`

## 交回前请检查

- **16 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 16 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一个塞拉斯：**同一个头（照图 B，脸朝右前方、两只眼睛、黑胡子）**、同样粗的腿和手臂、同样大的白石镣铐、同样的金链；手臂从肩膀长出来，没有盖住脸；姿势沿着骨架；着地的脚在 y 1168。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/sylas-poses/`）

- `sylas-pose-wind.png`、`-lash.png`、`-spin.png`、`-leap.png`、`-stab.png`、`-slam.png`、`-dash.png`、`-throw.png`、`-pull.png`、`-stagger.png`、`-kneel.png`、`-lie.png`、`-run1.png`、`-run2.png`、`-run3.png`、`-run4.png`；原始生成图原样放 `outputs/sylas-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/sylas_poses_done.zip`。中间不要停，16 张都画完再交。

## 附图（压缩包 `sylas_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 16 px，脚底 y 1168） |
| `3_wind_*` … `18_run4_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），头换成定稿的头（每帧同一张脸，脸不重画），再拼进 rig_sylas.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟）：普攻 = wind → lash → 定稿；被动横扫 = wind → spin；W 突刺 = leap → stab；Q = leap → slam；E = dash → throw，被拉过去 = pull；R 偷 = throw；R 放出夺来的大招 = leap → slam；死亡 = stagger → kneel → lie；跑 = run1–4；待机 = 定稿呼吸。
