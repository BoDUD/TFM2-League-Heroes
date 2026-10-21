# 万花通灵 妮蔻：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 妮蔻的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右的变色龙女孩——紫蓝色头发、品红紫的羽刺、珊瑚粉百合花、黄色大眼睛、青绿色鳞片皮肤、珊瑚橙抹胸、白贝壳腰带、深棕短裤、橙色叶子腰布、浅桃色大腿上的紫色螺旋纹、深棕绑带加金环、光脚紫脚趾、往上卷的青绿色长尾巴）。英雄联盟里她的动作很杂技——低身架势、往前扑、踢腿、低身扑击、空翻、空中扔种子、旋身绕尾、甩尾、蓄力下蹲、腾空跳起、落地、旋转、跪坐倒地，还有跑步——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **17 个姿势，每个一张图**（13 个动作姿势 + 4 帧跑步）。待机、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个妮蔻**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 10 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1180**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边）**，两条手臂的末端是紫色的手指；**黄线 = 尾巴**（从屁股后面长出来，一直到紫色的尾尖）；**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂、尾巴的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；尾巴和定稿一样粗、一样长，背上一排紫色的鳞，尾尖紫色。
> - **头一格一格照 `1_head.png` 画在灰框里**（连羽刺和头发 45 × 41 格，同样朝右前方、两只黄眼睛都看得见）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、尾巴**不要盖住脸**（眼睛和嘴）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的妮蔻是正常比例的，我们的是 Q 版大头：身子短、头大，所以手臂举不过头顶——**手臂往两边伸、往前伸，不要从脸前面横过去**。

## 17 个姿势

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| 3 | `neeko-pose-stance.png` | 低身架势：两腿大开压低，前倾，近侧手臂朝前伸、手掌张开，远侧手臂弯在身前，尾巴贴地伸在身后、尾尖卷起（普攻、Q 的起手） | 普攻、Q 的起手 |
| 4 | `neeko-pose-thrust.png` | 扑出出手：离地往前扑（脚离地约 6 格），身子大幅前倾，近侧手臂朝前伸直（和肩一样高，手掌张开对着前方），远侧手臂往身后甩开，近侧腿屈膝在前、远侧腿往后收，尾巴在身后低低地卷着（普攻出手） | 普攻出手 |
| 5 | `neeko-pose-kick.png` | 旋身踢腿：远侧腿踮脚站直，近侧腿往后高高抬起（屈膝，脚到腰的高度），身子挺直微微后仰，两只手臂往两边平伸保持平衡，尾巴从身后往上甩成一道大弧（第三下强化普攻） | 第三下强化普攻 |
| 6 | `neeko-pose-pounce.png` | 低身扑击：身子压得很低往前扑（几乎和地面平行），头在右前方，两只手往前伸到地面，前面的腿（远侧）屈膝，后面的腿（近侧）往后蹬直，尾巴在身后竖起来（第三下强化普攻打中） | 第三下强化普攻打中 |
| 7 | `neeko-pose-tuck.png` | 空中抱团：在空中蜷成一团（脚离地约 12 格），两膝收到胸前，两只手抱住小腿，头往前低，尾巴绕着身子卷一圈（Q 的空翻：我会把这一张整张转 90°、180°、270° 做成翻跟头；英雄联盟的参考图是 E 起手时在空中蹲着的那一帧，这一张要蜷得更紧、手抱小腿） | Q 的空翻（我整张转着用） |
| 8 | `neeko-pose-throw_air.png` | 空中掷出：在空中挺直（脚离地约 14 格），两只手臂往上甩开：近侧手臂往左上方、远侧手臂往右上方（手掌张开，种子从这只手飞出），都不挡脸，近侧腿屈膝抬起、远侧腿垂着，尾巴在身下卷着（Q 扔出种子） | Q 扔出种子 |
| 9 | `neeko-pose-coil.png` | 旋身绕尾：在空中蹲着旋转（脚离地约 8 格），尾巴在腰上绕成一个大圈，近侧手臂往左边伸开，远侧手臂往右前方伸，两腿收起（E 的起手） | E 的起手 |
| 10 | `neeko-pose-fling.png` | 甩出倒刺：站定，近侧手臂往身后左边平平甩开，远侧手臂朝前伸（手掌张开），尾巴从身后往前猛甩、在她身前（画面右边）伸得又平又长（E 甩出倒刺） | E 甩出倒刺 |
| 11 | `neeko-pose-hunch.png` | 蓄力下蹲：蹲得很低往前探（弓步），头低在前面，两只手垂在两膝之间，后面的腿（近侧）往后伸，前面的腿（远侧）屈膝，尾巴在身后卷成一个大螺旋竖起来（R 蓄力） | R 蓄力 |
| 12 | `neeko-pose-soar.png` | 腾空跃起：整个人笔直地跳起来（脚离地约 20 格），身子挺直、头仰起，两只手臂垂在身侧，近侧腿伸直往下、远侧腿屈膝，尾巴在身后往上卷（R 跳起） | R 跳起 |
| 13 | `neeko-pose-land.png` | 落地半蹲：屈膝落地、身子前倾，近侧手撑在身前右边的地上，远侧手臂往后扬，尾巴在身后高高竖起（R 落地） | R 落地、Q 落地 |
| 14 | `neeko-pose-run1.png` | 跑步 1（远侧腿在前着地，近侧腿往后抬起）：身子前倾一点，两只手收在胸前，尾巴在身后卷成螺旋 | 跑 |
| 15 | `neeko-pose-run2.png` | 跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格 | 跑 |
| 16 | `neeko-pose-run3.png` | 跑步 3（近侧腿在前着地，远侧腿往后抬起） | 跑 |
| 17 | `neeko-pose-run4.png` | 跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格 | 跑 |
| 18 | `neeko-pose-twirl.png` | 旋转踉跄：远侧腿踮脚站着，近侧腿屈膝抬起（脚贴在远侧膝盖旁），两只手臂往两边平伸，尾巴往右前方低低地甩出去（死亡第一下） | 死亡第一下 |
| 19 | `neeko-pose-sit.png` | 跪坐倒地：坐到地上，近侧腿跪着折在身下，远侧腿立起膝盖，近侧手撑在身边的地上，远侧手搭在膝盖上，身子微微往后靠，尾巴在身前的地上卷着（死亡） | 死亡 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (soles on y 1180) - a chibi chameleon-like lizard girl with a BIG head: a fluffy mop of violet-blue hair with magenta strands, a crest of long magenta-violet quills, coral-pink lilies at her temple and ear, big yellow slit-pupil eyes, a pale-peach face with a few teal scales, green-teal scaled skin on her arms and shoulders, violet fingers, a teal-blue gem necklace, a coral-orange woven top, a brown belt of white shell beads, dark brown shorts, an orange leaf loincloth, pale peach thighs with violet swirls turning teal down the shins, dark brown ankle wraps with gold rings, bare feet with violet toes, and a long teal TAIL with violet scales along its top and a violet tip; B its HEAD with the quills and the hair shown 8x (45 squares wide, 41 tall); C a SKELETON on the same 1254 canvas and 10 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left) ending at its violet fingers, PURPLE = the FAR arm (image right), YELLOW = the TAIL (from its root behind the hips to its violet tip), GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its realistic proportions); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1180.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the thigh with its violet swirl, the teal shin, the brown wrap with its gold ring, the bare foot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line to its violet fingers (the arms grow from the shoulders, never floating), the tail along the yellow line from behind the hips, as thick and as long as in image A, its violet top scales and its violet tip. Never stretch or shorten a limb or the tail, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both yellow eyes, the pink mouth, the quills, the lilies, the violet-blue hair) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or tail covers the face (the eyes and the mouth).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no magic, no flowers flying, no seeds, no petals, no glow), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- stance: `STANCE - a wide low fighting stance, both knees bent, the body leaning forward, the NEAR arm reaching forward with the hand open, the far arm bent before her, the tail stretched low behind her along the ground with its tip curling up.`
- thrust: `THRUST - springing forward off the ground (the feet about 6 squares up), the body leaning far forward, the NEAR arm thrust straight forward at shoulder height with the palm open toward the target, the far arm flung back behind her, the near knee bent forward, the far leg folded back, the tail low behind her curling at its end.`
- kick: `KICK - standing tall on the tiptoe of the FAR leg, the NEAR leg kicked up high behind her (the knee bent, the foot at waist height), the body upright and leaning back a little, both arms stretched out level to both sides for balance, the tail swung up behind her in a big arc.`
- pounce: `POUNCE - lunging forward very low, the body almost level with the ground, the head at the front (image right), both hands reaching forward to the ground, the front (far) leg bent, the back (near) leg pushed straight out behind, the tail standing up high behind her.`
- tuck: `TUCK - curled up into a ball in mid-air (the feet about 12 squares up), both knees pulled up to the chest, both hands holding the shins, the head bent forward, the tail wrapped once round her body.`
- throw_air: `THROW IN THE AIR - upright in mid-air (the feet about 14 squares up), both arms flung up and out: the NEAR arm up to the upper left, the FAR arm up to the upper right with the palm open (the seed leaves it), neither over the face, the near knee lifted, the far leg hanging, the tail curled below her.`
- coil: `COIL - spinning crouched in mid-air (the feet about 8 squares up), the tail looped round her waist in a big ring, the NEAR arm stretched out to the image left, the far arm reaching to the front right, both legs tucked.`
- fling: `FLING - standing firm, the NEAR arm flung back level to the image left, the far arm reaching forward with the palm open, the tail whipped round from behind her and stretched out long and level in front of her to the image right.`
- hunch: `HUNCH - crouched very low and leaning forward in a lunge, the head low at the front, both hands hanging between the knees, the back (near) leg stretched behind, the front (far) leg bent, the tail rolled up behind her into a big upright spiral.`
- soar: `SOAR - leaping straight up into the air (the feet about 20 squares up), the body stretched tall, the head up, both arms down at her sides, the near leg straight down, the far knee bent, the tail curling up behind her.`
- land: `LAND - landed in a crouch, the knees bent, the body leaning forward, the NEAR hand pressed on the ground in front of her (image right), the far arm swept back, the tail raised high up behind her.`
- run1: `RUN 1 - bounding along: the FAR leg forward with its foot landing, the NEAR leg kicked up behind her, the body leaning forward a little, both hands held before her chest, the tail curled into a spiral behind her.`
- run2: `RUN 2 - bounding along: the near leg under the body carrying her, the FAR knee lifted forward, the body one square higher, both hands before her chest, the tail curled into a spiral behind her.`
- run3: `RUN 3 - bounding along: the NEAR leg forward with its foot landing, the FAR leg kicked up behind her, the body leaning forward a little, both hands before her chest, the tail curled into a spiral behind her.`
- run4: `RUN 4 - bounding along: the far leg under the body carrying her, the NEAR knee lifted forward, the body one square higher, both hands before her chest, the tail curled into a spiral behind her.`
- twirl: `TWIRL - spinning on the tiptoe of the FAR leg, the NEAR knee lifted with its foot by the far knee, both arms stretched out level to both sides, the tail swung out low to the front right.`
- sit: `SIT - sunk down sitting on the ground, the near leg folded under her with its knee on the ground, the far knee raised, the near hand propped on the ground beside her, the far hand resting on the raised knee, the body leaning back a little, the tail curled on the ground in front of her.`

## 交回前请检查

- **17 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 10 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一个妮蔻：**同一个头（照图 B，脸朝右前方、两只黄眼睛、品红紫羽刺、百合花）**、同样粗的腿和手臂、同样粗长的尾巴（紫色背鳞、紫色尾尖）；手臂从肩膀长出来，没有盖住脸；姿势沿着骨架；着地的脚在 y 1180。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/neeko-poses/`）

- `neeko-pose-stance.png`、`neeko-pose-thrust.png`、`neeko-pose-kick.png`、`neeko-pose-pounce.png`、`neeko-pose-tuck.png`、`neeko-pose-throw_air.png`、`neeko-pose-coil.png`、`neeko-pose-fling.png`、`neeko-pose-hunch.png`、`neeko-pose-soar.png`、`neeko-pose-land.png`、`neeko-pose-run1.png`、`neeko-pose-run2.png`、`neeko-pose-run3.png`、`neeko-pose-run4.png`、`neeko-pose-twirl.png`、`neeko-pose-sit.png`；原始生成图原样放 `outputs/neeko-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/neeko_poses_done.zip`。中间不要停，17 张都画完再交。

## 附图（压缩包 `neeko_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 10 px，脚底 y 1180） |
| `3_stance_*` … `19_sit_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 10 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、尾巴的长短粗细，和定稿比**（codex-legs-need-skeletons），头换成定稿的头（每帧同一张脸，脸不重画），再拼进 rig_neeko.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟）：普攻 = stance → thrust → 定稿；第三下强化普攻（attack_w）= kick → pounce → 定稿；Q（skill）= stance → tuck 整张转 90° / 180° / 270°（空翻）→ throw_air → land；E（skill2）= coil → fling；R 蓄力（ult）= hunch（呼吸）；R 跳起落地（ult_b）= soar （升高）→ land；死亡 = twirl → sit；跑 = run1–4；待机 = 定稿呼吸（只在腰以上）；受击 = 定稿后退一格闪白。
