# 纳祖芒荣耀 奎桑提：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 奎桑提的两个造型用户已经定稿：**普通姿态**（`2_design_base.png`，你上一轮画的 A-2：3/4 正面朝右、两把青石陀斧竖在身体两侧）和**全盛姿态**（`2_design_ao.png`，O-1：弓背半蹲、两根长棍甩开拖向地面；**用户把它缩到了和普通姿态一样的身体大小**）。英雄联盟里他的普攻、Q、W、R、跑步、死亡都是**全身动作**——把巨大的陀斧举过头顶砸下、两把陀斧并成墙往前顶、压低身子盾击、飞扑、跪倒，这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **27 个姿势，每个一张图**：普通姿态 17 个（13 个动作 + 4 帧跑步），全盛姿态 10 个（6 个动作 + 4 帧跑步）。待机和受击我从定稿本身来做，不用画。
> - **每张图都是同一个奎桑提**：样子、颜色、粗细、长短全照这个姿势所属的定稿（普通姿势照 `2_design_base.png`，全盛姿势照 `2_design_ao.png`），**格子和定稿一样大：每格 10 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1180**），网格从画布左上角对齐。**两种姿态的身体一样大**（头、肩膀、手臂、腿一样粗一样长）。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）到拳头**，**紫线 = 远侧的手臂（画面右边）到拳头**；**粗的深青线 = 近侧手里的陀斧**，**粗的亮青线 = 远侧手里的陀斧**，线穿过拳头（就是握的地方），**带圆圈的一头是陀斧的长头**（普通姿态：陀斧顶端；全盛：长棍的棍头）；**灰框 = 头的位置**。`0_design_skeleton_base.png` / `0_design_skeleton_ao.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂、陀斧的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；**陀斧是硬的石头，不会弯**，拳头握在骨架线穿过的地方。
> - **头一格一格照这个姿态的头画在灰框里**（普通照 `1_head_base.png`，23 × 19 格；全盛照 `1_head_ao.png`，26 × 21 格，咧嘴露牙），同样朝右前方、两只眼睛都看得见。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。**手臂、拳头和陀斧都不要盖住脸**（眼睛、胡子、嘴）——骨架已经避开了脸。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作的感觉照它**，长相照定稿。**原版和骨架在"哪只手拿哪把陀斧、陀斧朝哪边"上不一样的地方，以骨架为准**（为了不挡脸调过）。

## 普通姿态的 17 个姿势（照 `2_design_base.png`、`1_head_base.png`）

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| 3 | `ksante-pose-a-back.png` | 普攻蓄力：两腿分开站稳，身子微微后仰，近侧手把陀斧往身后拉（陀斧斜着指向左上方），远侧手的陀斧斜着伸向前下方 | 普攻起手 |
| 4 | `ksante-pose-a-strike.png` | 普攻命中：弓步压低前冲，身子往前倾，两把陀斧一起往前横推到腰前（陀斧水平指向右边） | 普攻命中 |
| 5 | `ksante-pose-q-up.png` | Q 起跳：整个人跳离地面（脚离地约 8 格），远侧手高高举起，把陀斧横着举在头顶上方（陀斧水平指向左边），近侧手提着另一把陀斧竖在身旁，两膝收起 | Q 一段起跳 |
| 6 | `ksante-pose-q-down.png` | Q 砸下：落地蹲低，身子前倾，远侧手的陀斧砸到身前地面（陀斧斜着指向右下，末端着地），近侧手的陀斧举在身后 | Q 一段砸下 |
| 7 | `ksante-pose-q2-down.png` | Q 第二下砸下：和上一个相反——近侧手的陀斧砸到身前地面，远侧手把另一把陀斧斜着举向右上方（在头的右边，不挡脸） | Q 二段砸下 |
| 8 | `ksante-pose-q3-up.png` | Q 三段起跳：跳离地面（脚离地约 10 格），两只手都高高举起，两把陀斧一上一下横着举在头顶上方（都水平指向左边） | Q 三段起跳 |
| 9 | `ksante-pose-q3-slam.png` | Q 三段砸地：深蹲，身子压得很低，两把陀斧一起砸在身前地面上（都指向右边，末端着地） | Q 三段砸地（冲击波） |
| 10 | `ksante-pose-w-wall.png` | W 蓄力：两把陀斧并在一起斜着顶在身前（往前倾约 30 度），像一面往前推的墙，他在后面用肩膀顶住，近侧腿往后蹬；墙在头的右边，不挡脸 | W 蓄力减伤 |
| 11 | `ksante-pose-w-dash.png` | W 冲撞：和蓄力一样把两把陀斧并成墙顶在身前，墙往前倾得更多（约 40 度），身子更往前倾、迈开大步往前冲；墙在头的右边，不挡脸 | W 冲撞 |
| 12 | `ksante-pose-r-bash.png` | R 盾击：整个人压低往前猛冲，身子几乎平着，两把陀斧一起往前平推出去（指向右边） | R 盾击 |
| 13 | `ksante-pose-r-fly.png` | R 飞扑：整个人平着往前扑在空中（离地约 8 格），远侧手的陀斧伸向前方，近侧手的陀斧扬在身后上方，两腿拖在后面 | R 追上去的飞扑 |
| 14 | `ksante-pose-d-slump.png` | 倒下 1：身子往前栽、弯下腰，头垂下，两只手垂到膝盖前，近侧的陀斧往左上方歪倒，远侧的陀斧往右下方倒向地面 | 死亡第一下 |
| 15 | `ksante-pose-d-kneel.png` | 倒下 2：单膝跪地（近侧膝盖着地），身子往前塌，两只空手往前垂，两把陀斧已经脱手、平躺在地上（一把在身后、一把在身前） | 死亡（最后一帧） |
| 16 | `ksante-pose-run1.png` | 跑步 1（近侧腿在前着地）：身子微微前倾，两把陀斧竖着提在身体两侧，远侧手往前摆、近侧手往后摆 | 跑 |
| 17 | `ksante-pose-run2.png` | 跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，陀斧竖在两侧 | 跑 |
| 18 | `ksante-pose-run3.png` | 跑步 3（远侧腿在前着地）：近侧手往前摆、远侧手往后摆，陀斧竖在两侧，不挡脸 | 跑 |
| 19 | `ksante-pose-run4.png` | 跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，陀斧竖在两侧 | 跑 |

## 全盛姿态的 10 个姿势（照 `2_design_ao.png`、`1_head_ao.png`）

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| 20 | `ksante-pose-ao-swing-back.png` | 全盛普攻蓄力：身子稍微直起来，近侧手把长棍高高抡到身后上方（指向左上），远侧手的长棍垂向右下方 | 全盛普攻起手 |
| 21 | `ksante-pose-ao-swing.png` | 全盛普攻横扫：蹲低，两只手把两根长棍往左右两边横着甩开（近侧指向左、远侧指向右，几乎水平） | 全盛普攻命中 |
| 22 | `ksante-pose-ao-leap.png` | 全盛跳起：整个人跳离地面（脚离地约 10 格），两膝收起，远侧手举起长棍横在头顶上方（指向左边），近侧手的长棍横在腰前（指向右边） | 全盛 Q 起跳 |
| 23 | `ksante-pose-ao-smash.png` | 全盛砸地：落地蹲低，远侧手的长棍砸到身前地面（几乎水平指向右边，棍头着地），近侧手的长棍举在头顶后上方（指向左上） | 全盛 Q 砸地 |
| 24 | `ksante-pose-ao-cross.png` | 全盛 W 蓄力：直起身子，两根长棍在头顶交叉成 X 字（近侧指向右上、远侧指向左上） | 全盛 W 蓄力 |
| 25 | `ksante-pose-ao-charge.png` | 全盛 W 冲撞：压低身子往前冲，身子前倾，两根长棍斜着伸向前下方，近侧腿往后蹬 | 全盛 W 冲撞 |
| 26 | `ksante-pose-ao-run1.png` | 全盛跑步 1（近侧腿在前着地）：弓着背往前冲，两根长棍拖在身体两侧，棍头贴近地面 | 全盛跑 |
| 27 | `ksante-pose-ao-run2.png` | 全盛跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，长棍拖在两侧 | 全盛跑 |
| 28 | `ksante-pose-ao-run3.png` | 全盛跑步 3（远侧腿在前着地）：弓着背往前冲，长棍拖在两侧 | 全盛跑 |
| 29 | `ksante-pose-ao-run4.png` | 全盛跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，长棍拖在两侧 | 全盛跑 |

## 提示词（每个姿势一次，换掉最后一行的姿势）

每次上传：这个姿态的 `2_design_*.png`（定稿）、`1_head_*.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton_*.png`。**用 image_gen 画。**

**普通姿态的姿势用这段：**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (soles on y 1180) - a huge broad-shouldered tank warrior: dark brown skin, short black twists of hair, a black full beard, a gold earring, a blue-violet scarf, a thick crimson coat with gold-and-violet diamond patterns, huge bronze-gold pauldrons, bracers and knee guards, gold ropes and round gold medallions over his chest, a violet jagged tabard, dark plum trousers, brown boots, and TWO GIANT teal-grey STONE SHIELD-TONFAS (ntofos) set with bright teal crystals, gold trim and a gold medallion, each about as tall as he is, gripped a third of the way up; B its HEAD shown 8x (23 squares wide, 19 tall); C a SKELETON on the same canvas and 10 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left) to its fist, PURPLE = the FAR arm (image right) to its fist, a THICK DARK TEAL line = the ntofo in the NEAR hand, a THICK BRIGHT CYAN line = the ntofo in the FAR hand (each line runs through the fist that grips it; the end with a RING is the ntofo's long top end), GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the feel of the POSE from it, never its 3D look; where D and the skeleton disagree about which hand holds which ntofo or where it points, follow the SKELETON); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1180.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the thigh, the shin with its gold knee guard, the brown boot the SAME thickness, length and colours as in image A), each arm from its shoulder (with its huge gold pauldron) along its line to its fist (the arms grow from the shoulders, never floating). Each ntofo is a RIGID stone slab drawn along its thick line, as long and as wide as in image A, its long top end at the ring, gripped by the fist where the line passes it - never bent, never shortened. The near arm and the near ntofo in front of the body in full tone; the far leg, the far arm and the far ntofo behind it a step darker. Never stretch or shorten a limb.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both eyes, the beard, the black twists) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, fist or ntofo covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no shock waves, no dust, no shield glow, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

**全盛姿态的姿势用这段：**

```text
Attached images: A the APPROVED pixel-art character in his ALL OUT stance, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (soles on y 1180) - a huge broad-shouldered tank warrior hunched forward in a wide half-squat: dark brown skin, short black twists of hair, a black full beard, a fierce grin with white teeth, a gold earring, a blue-violet scarf, a thick crimson coat with gold-and-violet diamond patterns, huge bronze-gold pauldrons and bracers, gold ropes and round gold medallions, a violet jagged tabard, dark plum trousers, brown boots, and TWO teal-grey stone CLUBS (his tonfas swung out long) set with bright teal crystals and a gold medallion at each club's head; B its HEAD shown 8x (26 squares wide, 21 tall); C a SKELETON on the same canvas and 10 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left) to its fist, PURPLE = the FAR arm (image right) to its fist, a THICK DARK TEAL line = the club in the NEAR hand, a THICK BRIGHT CYAN line = the club in the FAR hand (each line runs through the fist that grips it near the club's butt; the end with a RING is the club's head), GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the feel of the POSE from it, never its 3D look; where D and the skeleton disagree about which hand holds which club or where it points, follow the SKELETON); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1180.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots, the same thickness, length and colours as in image A), each arm from its shoulder (with its huge gold pauldron) along its line to its fist (the arms grow from the shoulders, never floating). Each club is a RIGID stone club drawn along its thick line, as long and as thick as in image A, its head at the ring, gripped near its butt by the fist where the line passes it - never bent, never shortened. The near arm and the near club in front of the body in full tone; the far leg, the far arm and the far club behind it a step darker. Never stretch or shorten a limb.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both eyes, the beard, the grin, the black twists) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, fist or club covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no shock waves, no dust, no glow, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

普通姿态：

- a-back: `WIND-UP - standing with the legs apart, leaning back a little, the NEAR arm pulling its ntofo back behind him (the ntofo slanting up to the image left), the FAR arm's ntofo slanting forward and down.`
- a-strike: `STRIKE - a low forward lunge, the body leaning forward, BOTH ntofos thrust forward together, held level at waist height pointing to the image right.`
- q-up: `LEAP UP - jumping off the ground (the feet about 8 squares up), the FAR arm raised high holding its ntofo LEVEL above his head (pointing to the image left), the NEAR arm low carrying the other ntofo upright beside him, both knees drawn up.`
- q-down: `SLAM - landed in a low crouch leaning forward, the FAR arm's ntofo slammed down in front of him (slanting down to the image right, its end on the ground), the NEAR arm's ntofo held up behind him.`
- q2-down: `SLAM 2 - the other side: landed low, the NEAR arm's ntofo slammed down in front of him (its end on the ground at the image right), the FAR arm holding the other ntofo raised and slanting up to the image right (to the right of his head, never over the face).`
- q3-up: `BIG LEAP - jumping high (the feet about 10 squares up), BOTH arms raised high, BOTH ntofos held LEVEL above his head one over the other (both pointing to the image left).`
- q3-slam: `GROUND SLAM - a deep crouch, the body very low, BOTH ntofos slammed together onto the ground in front of him (both pointing to the image right, their ends on the ground).`
- w-wall: `BRACE - BOTH ntofos side by side held before him like a wall LEANING FORWARD about 30 degrees, he pushes into it from behind with his shoulders, the near leg braced back; the wall stays to the right of his face.`
- w-dash: `RAM - the same wall of both ntofos held before him, leaning further forward (about 40 degrees), charging with a long stride (the near leg far back, the far leg forward); the wall stays to the right of his face.`
- r-bash: `SHIELD BASH - lunging forward very low, the body almost level, BOTH ntofos shoved forward together (level, pointing to the image right), the near leg stretched far back.`
- r-fly: `DIVE - flying forward level through the air (about 8 squares off the ground), the FAR arm's ntofo reaching forward, the NEAR arm's ntofo swung up behind him, both legs trailing behind.`
- d-slump: `SLUMP - pitching forward, bent at the waist, the head dropping, both hands sagging down before his knees, the near ntofo toppling over to the image left (leaning up-left), the far ntofo falling forward and down to the ground at the image right.`
- d-kneel: `KNEEL - down on one knee (the near knee on the ground), slumped forward, both empty hands hanging forward; the two ntofos have dropped and lie FLAT on the ground (one behind him, one in front).`
- run1: `RUN 1 - running leaning a little forward, both ntofos carried upright at his sides: the NEAR leg forward landing, the far leg pushing off behind, the far arm swinging forward, the near arm swinging back.`
- run2: `RUN 2 - running: the near leg under the body carrying him, the far knee lifted forward, the body one square higher, both ntofos upright at his sides.`
- run3: `RUN 3 - running: the FAR leg forward landing, the near leg pushing off behind, the near arm swinging forward (its ntofo upright, never over the face), the far arm swinging back.`
- run4: `RUN 4 - running: the far leg under the body carrying him, the near knee lifted forward, the body one square higher, both ntofos upright at his sides.`

全盛姿态：

- ao-swing-back: `ALL OUT WIND-UP - rising a little out of the crouch, the NEAR arm swinging its club high up behind him (pointing up to the image left), the FAR arm's club hanging down to the image right.`
- ao-swing: `ALL OUT SWEEP - crouched low, both arms swinging both clubs out wide to the sides (the near one to the image left, the far one to the image right, almost level).`
- ao-leap: `ALL OUT LEAP - jumping off the ground (the feet about 10 squares up), the knees drawn up, the FAR arm raised holding its club level over his head (pointing to the image left), the NEAR arm's club held level before his waist (pointing to the image right).`
- ao-smash: `ALL OUT SMASH - landed low, the FAR arm's club slammed down in front of him (almost level, pointing to the image right, its head on the ground), the NEAR arm's club raised up behind his head (pointing up to the image left).`
- ao-cross: `ALL OUT BRACE - standing up tall, both clubs crossed in an X over his head (the near one pointing up to the image right, the far one up to the image left).`
- ao-charge: `ALL OUT CHARGE - charging forward low, the body leaning forward, both clubs reaching forward and down, the near leg pushing off far behind.`
- ao-run1: `ALL OUT RUN 1 - running hunched forward, both clubs trailing at his sides with their heads near the ground: the NEAR leg forward landing, the far leg pushing off behind.`
- ao-run2: `ALL OUT RUN 2 - running hunched: the near leg under the body carrying him, the far knee lifted forward, the body one square higher, both clubs trailing at his sides.`
- ao-run3: `ALL OUT RUN 3 - running hunched forward: the FAR leg forward landing, the near leg pushing off behind, both clubs trailing at his sides.`
- ao-run4: `ALL OUT RUN 4 - running hunched: the far leg under the body carrying him, the near knee lifted forward, the body one square higher, both clubs trailing at his sides.`

## 交回前请检查

- **27 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 10 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是这个姿态定稿里的同一个奎桑提：**同一个头（照图 B，脸朝右前方、两只眼睛、黑胡子；全盛咧嘴露牙）**、同样粗的腿和手臂、同样大的金护肩；**两种姿态身体一样大**；手臂从肩膀长出来；**陀斧 / 长棍是硬的、不弯、长短和定稿一样**，拳头握在骨架线穿过的地方；没有东西盖住脸；姿势沿着骨架；着地的脚在 y 1180。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/ksante-poses/`）

- 上面两张表里的 27 个文件（`ksante-pose-a-back.png` … `ksante-pose-ao-run4.png`）；原始生成图原样放 `outputs/ksante-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ksante_poses_done.zip`。中间不要停，27 张都画完再交。

## 附图（压缩包 `ksante_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton_base.png` / `0_design_skeleton_ao.png` | 两个定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head_base.png` / `1_head_ao.png` | 两个定稿的头（8 倍）：这个姿态的每个姿势都照它逐格画 |
| `2_design_base.png` / `2_design_ao.png` | 两个定稿（每格 10 px，脚底 y 1180） |
| `3_a_back_*` … `29_ao_run4_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 10 px），按格读回（regrid），颜色对到各自定稿的调色板；**先在 8 倍下量每条腿、手臂、陀斧的长短粗细，和定稿比**（codex-legs-need-skeletons），头换成各自定稿的头（每帧同一张脸，脸不重画），再拼进 rig_ksante.py 的动作里，逐帧自查后才发一个合成 GIF（用户：「动作帧请做到完美后喊我review」）。
- 动作安排（照英雄联盟）：普攻 = a_back → a_strike → 定稿；Q 一段（skill）= q_up → q_down；Q 二段（skill_b）= q_up → q2_down；Q 三段（skill_c）= q3_up → q3_slam；W（skill2）= w_wall（蓄力），skill2_dash = w_dash；R（ult）= r_bash → 变身闪光，ult_dash = r_fly；死亡 = d_slump → d_kneel；跑 = run1–4；全盛：ao_attack = ao_swing_back → ao_swing，ao_skill / ao_skill_b = ao_leap → ao_smash，ao_skill_c = ao_leap → ao_smash 加冲击波，ao_skill2 = ao_cross，ao_skill2_dash = ao_charge，ao_run = ao_run1–4；待机 = 定稿呼吸（只在腰以上）；受击 = 定稿后退一格闪白。
