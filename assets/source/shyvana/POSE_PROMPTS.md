# 龙血武姬 希瓦娜：人形的动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 希瓦娜人形的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右、淡紫皮肤、金橙长发、深红龙角冠、青银胸甲金边、深紫红护腿、银金鳞片护膝、龙爪脚、金色尾尖的深红长尾巴）。英雄联盟里她的普攻、技能、跑步、死亡都是**全身动作**——蓄势下蹲、扬爪、挥爪横斩、空翻、落地甩尾、掷出火球、腾空跃起、中招后仰、跪倒、伏倒，还有跑步——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **14 个姿势，每个一张图**（10 个动作姿势 + 4 帧跑步）。待机我从定稿本身来做，龙形我自己做，都不用画。
> - **每张图都是同一个希瓦娜**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 14 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边）**，两条手臂的末端是金色的龙爪；**黄线 = 尾巴**（从屁股后面长出来，一直到金色的尾尖）；**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂、尾巴的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；尾巴和定稿一样粗、一样长，背上一排尖刺，尾尖金色。
> - **头一格一格照 `1_head.png` 画在灰框里**（连龙角冠和头发 27 × 21 格，同样朝右前方、两只眼睛都看得见）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（「中招后仰」的头可以整个往后仰一点，脸还是这张脸）。手臂、爪子和尾巴**不要盖住脸**（眼睛）。长发跟着头，披在背后。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。

## 14 个姿势

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| 3 | `shyvana-pose-crouch.png` | **蓄势下蹲**：两腿深蹲，身子压低前倾，两只爪子收在胸前，尾巴在身后卷起 | 普攻、E、R 的起手 |
| 4 | `shyvana-pose-rise.png` | **扬爪**：身子挺直往上，远侧手臂高高举过头顶，近侧手臂垂在身侧，两腿前后分开，尾巴平甩在身后 | 普攻出手前、Q 一段起手 |
| 5 | `shyvana-pose-slash.png` | **挥爪横斩**：两腿大开蹲低，身子前倾，远侧手臂往前下方斩到身前（爪子在腰的高度），近侧手臂垂在身后，尾巴往后上方扬起 | 普攻命中、Q 一段命中 |
| 6 | `shyvana-pose-flip.png` | **空翻**：在空中蜷成一团往前翻（脚离地约 9 格），两膝收到胸前，头埋向前下方，尾巴从背后绕过头顶划一道大弧 | Q 二段起手 |
| 7 | `shyvana-pose-sweep.png` | **落地甩尾**：蹲得很低，远侧手臂往前上方扬起、近侧手臂弯在胸前，尾巴贴着地面往前扫到身前 | Q 二段命中 |
| 8 | `shyvana-pose-throw.png` | **掷出火球**：两腿前后弓步，身子前倾，远侧手臂朝前伸直（爪子张开，和肩一样高），近侧手臂往身后拉直，尾巴平伸在身后 | E 爆炎吐息 |
| 9 | `shyvana-pose-leap.png` | **腾空跃起**：整个人往上跃起（脚离地约 10 格），身子挺直、头仰起，近侧手臂往后下方甩、远侧手臂弯在身前，两腿在下面拖着，尾巴垂在身后 | R 起跳（在空中化龙） |
| 10 | `shyvana-pose-stagger.png` | **中招后仰**：两腿大开站着，身子往后仰、头往后甩，两只手臂往两边甩开，尾巴从身后甩到肩膀上方 | 死亡第一下 |
| 11 | `shyvana-pose-kneel.png` | **跪倒**：两膝往里弯、身子往下塌，头往后仰，远侧手臂往前伸、近侧手臂垂着，尾巴拖在身后 | 死亡第二下 |
| 12 | `shyvana-pose-collapse.png` | **伏倒**：跪着往前趴，两只手撑在身前地上，头低到地面附近（朝画面右边），尾巴贴着地面伸在身后 | 死亡 |
| 13 | `shyvana-pose-run1.png` | **跑步 1**：近侧腿在前着地，身子前倾，远侧手臂往前摆、近侧手臂往后摆，尾巴平伸在身后 | 跑 |
| 14 | `shyvana-pose-run2.png` | **跑步 2**：近侧腿在身下撑地，远侧腿屈膝抬到前面，身子高一格，尾巴平伸在身后 | 跑 |
| 15 | `shyvana-pose-run3.png` | **跑步 3**：远侧腿在前着地，近侧手臂往前摆（在下巴下面，不挡脸）、远侧手臂往后摆，尾巴平伸在身后 | 跑 |
| 16 | `shyvana-pose-run4.png` | **跑步 4**：远侧腿在身下撑地，近侧腿屈膝抬到前面，身子高一格，尾巴平伸在身后 | 跑 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 14 px squares (soles on y 1176) - a tall half-dragon warrior woman: pale lavender skin, long golden-orange hair falling down her back, a crown of crimson dragon horns with black tips sweeping back from her brow, a teal-silver scale breastplate with gold trim, crimson cloth wraps on her forearms ending in golden claws, dark plum leggings with silver-gold scale knee and shin guards, clawed dragon feet, and a long crimson scaly TAIL with a row of spikes along its top and a golden tip; B its HEAD with the horn crown and the hair shown 8x (27 squares wide, 21 tall); C a SKELETON on the same 1254 canvas and 14 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left) ending at its golden claws, PURPLE = the FAR arm (image right) ending at its golden claws, YELLOW = the TAIL (from its root behind the hips to its golden tip), GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 14 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1176.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the thigh, the shin with its silver-gold guards, the clawed foot the SAME thickness, length and colours as in image A), each arm from its shoulder along its line to its claws (the arms grow from the shoulders, never floating), the tail along the yellow line from behind the hips, as thick and as long as in image A, its spikes and its golden tip. Never stretch or shorten a limb or the tail, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both golden eyes, the crimson horn crown, the golden-orange hair) - the same head in every pose, only moved, never turned, never redrawn as a profile; the long hair goes with it down her back. No arm, claw or tail covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no fire, no flames, no fireball, no glow), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- crouch: `CROUCH - both knees deeply bent, the body low and leaning forward, both clawed hands held up before her chest, the tail curled up behind her.`
- rise: `RISE - standing tall and reaching up, the FAR arm raised high over her head with the claws open, the near arm down at her side, the legs apart (the near leg bent behind, the far leg straight), the tail swung out level behind her.`
- slash: `SLASH - landed in a wide low stance, the body leaning forward, the FAR arm slashed forward and down so its claws end in front of her at waist height, the near arm hanging back, the tail raised up and back behind her.`
- flip: `FLIP - curled up in the air somersaulting forward (the feet about 9 squares above the ground), both knees pulled up to the chest, the head tucked forward and down, the tail swinging from her back up over the top of her head in a big arc.`
- sweep: `SWEEP - landed in a very low crouch, the FAR arm flung up and forward, the near arm bent before her chest, the tail sweeping forward low along the ground in front of her.`
- throw: `THROW - a forward lunge, the body leaning forward, the FAR arm thrust straight forward at shoulder height with the claws open, the near arm pulled straight back behind her, the tail stretched out level behind.`
- leap: `LEAP - launching straight up into the air (the feet about 10 squares above the ground), the body stretched tall, the head up, the near arm swept down and back, the far arm bent before her, both legs trailing below, the tail hanging down behind her.`
- stagger: `STAGGER - struck: standing with the legs wide apart, bending back, the head thrown back a little, both arms flung out to both sides, the tail whipped up behind her above the shoulder.`
- kneel: `KNEEL - the knees buckling inwards, the body sinking down, the head tipped back, the far arm reaching forward, the near arm hanging, the tail trailing behind her.`
- collapse: `COLLAPSE - fallen forward onto both knees and both hands, the head low near the ground at the image right, the tail lying along the ground stretched out behind her.`
- run1: `RUN 1 - running leaning forward: the NEAR leg forward with its foot landing, the far leg pushing off behind, the far arm swinging forward, the near arm swinging back, the tail stretched out level behind.`
- run2: `RUN 2 - running: the near leg under the body carrying her, the far knee lifted forward, the body one square higher, the arms at her sides, the tail level behind.`
- run3: `RUN 3 - running leaning forward: the FAR leg forward with its foot landing, the near leg pushing off behind, the near arm swinging forward (below the chin, never over the face), the far arm swinging back, the tail level behind.`
- run4: `RUN 4 - running: the far leg under the body carrying her, the near knee lifted forward, the body one square higher, the arms at her sides, the tail level behind.`

## 交回前请检查

- **14 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 14 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一个希瓦娜：**同一个头（照图 B，脸朝右前方、两只金色眼睛、深红龙角冠）**、同样粗的腿和手臂、同样粗长的尾巴（背上尖刺、金色尾尖）；手臂从肩膀长出来，没有盖住脸；姿势沿着骨架；着地的脚在 y 1176。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/shyvana-poses/`）

- `shyvana-pose-crouch.png`、`-rise.png`、`-slash.png`、`-flip.png`、`-sweep.png`、`-throw.png`、`-leap.png`、`-stagger.png`、`-kneel.png`、`-collapse.png`、`-run1.png`、`-run2.png`、`-run3.png`、`-run4.png`；原始生成图原样放 `outputs/shyvana-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/shyvana_poses_done.zip`。中间不要停，14 张都画完再交。

## 附图（压缩包 `shyvana_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 14 px，脚底 y 1176） |
| `3_crouch_*` … `16_run4_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 14 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、尾巴的长短粗细，和定稿比**（codex-legs-need-skeletons），头换成定稿的头（每帧同一张脸，脸不重画），再拼进 rig_shyvana.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟）：普攻 = crouch → rise → slash → 定稿；Q 一段（skill）= rise → slash；Q 二段（skill_b）= crouch → flip → sweep；E（skill2）= crouch → throw；R（ult）= crouch → leap → 变身闪光 → 龙飞起 → 龙落地；龙变回人（revert）= 龙收翅 → 闪光 → crouch → 定稿；死亡 = stagger → kneel → collapse；跑 = run1–4；待机 = 定稿呼吸（只在腰以上）；受击 = 定稿后退一格闪白。
