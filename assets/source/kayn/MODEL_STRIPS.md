# 凯隐：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定了三张造型（都在 `design/`，放大 8 倍，1024×1024，脚底在第 99 行，两脚中间在第 64 列）：
> - **本体** `kayn_design.png`（40 格宽 × 40 行）：黑色刺头、蓝色挑染、背后长辫子、小麦色皮肤、胸口的暗蓝侵蚀纹、近处金色的眼睛和远处被侵蚀的红眼、藕粉色腰带和红色绳结、靛蓝灯笼裤、紫色靴子，和**镰刀拉亚斯特**（暗红月牙刀身、钢蓝刃口、刀根的红眼、紫色长柄、红色柄尖）。
> - **暗裔杀手** `kayn_darkin_design.png`（45 × 43）和 **影流刺客** `kayn_shadow_design.png`（61 × 40）：两种变身形态。
> - **一共两部分**：**第 1 部分**是本体的 9 张动作条（待机已经做好）；**第 2 部分**是两种形态各 4 张「出招」动作条（普攻、Q、W、R 破体）——**和第 1 部分同名的那张完全同样的帧、格子、时机**，只是换成形态的造型。游戏里凯隐变身后，出招时播形态的动作，平时站着、跑步还是本体。**先画完第 1 部分，再画第 2 部分**（第 2 部分可以把你画好的第 1 部分那张当第四张附图，照着它的动作画）。
> - 帧数、每帧时长、出手帧和站位照 `now/kayn_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、镰刀和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（40 行高、头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡时整个头跟着身体转），**不画背影**；③ 原版 W 跳得很高，now 条里已经压低了（最高时脚离地约 7 格），照 now 条的高度；原版 R 会跳出画面，我们只画向前俯冲；原版 R 破体时身体横着转圈，我们缩成一团转、头保持正。
> - **镰刀（最重要的标志）**：RHAAST, the huge war scythe, is in every frame, whole (never broken, shortened or melted into the body): the FIRST image's own scythe - its big crescent blade with the bright cutting edge along the inner curve, the spikes, the eye at the blade's base, the long shaft and the butt spike, in the FIRST image's colours and size - only moved and turned with his hands; the hand that holds it grips the shaft (no gap between hand and shaft)。
> - **辫子**：the hair as in the FIRST image: the long black braid (the Shadow Assassin's long loose hair) hangs from the back of his head down his back and swings with the motion (it trails behind him in the run, the dash and the leap); the blue streak stays at the front of his hair; the Darkin has the horned helm instead。
> - **腿**：in every standing frame (attack, W's slam, R's landing, hit) the legs are the FIRST image's own legs square for square - the same stance, the same trousers and feet; only Q's dash and hop, W's leap and the transformation's lift stretch, bend or lift the same legs, the run alternates them and the death kneels and falls。
> - 出招方向：**挥镰、冲刺、斩击都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧的刀尖位置）和 `generation_prompts.json`，最好打成一个 zip（`kayn_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose；第 2 部分再加你画好的同名本体条）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**不要把细节比方块还小的高清图压缩下来**，也**不要整行整列删格子**（第 1 步的镰刀弧线就是这样被删碎的）。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/kayn_palette.png`）。
4. **贴头**：把造型图的头（`design/kayn_head_1x.png`；暗裔 `kayn_darkin_head_1x.png`、影流 `kayn_shadow_head_1x.png` 里不透明的格子）原样贴进每一帧头的位置（只平移；死亡时整个头跟着转）。本体头在 128×128 画布上的范围 x 57–72、y 60–72（暗裔 x 48–77、y 57–69；影流 x 54–70、y 60–70），**按图里的形状贴，不是整个方框**。头下面直接接肩膀，不要拉出一截脖子；辫子（影流是披下来的长发）从头后面接下去。
5. 对位：每帧按 `kayn_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/kayn_design.png`、`_1x.png` | **本体定稿造型**（8 倍 / 原尺寸）；站位点 (64, 88)，脚底线第 99 行 | 第 1 部分每张的第一张附图 |
| `design/kayn_darkin_design.png`、`_1x.png` | **暗裔杀手定稿造型** | 第 2 部分 `rh_` 每张的第一张附图 |
| `design/kayn_shadow_design.png`、`_1x.png` | **影流刺客定稿造型** | 第 2 部分 `sh_` 每张的第一张附图 |
| `design/kayn_head.png`、`kayn_darkin_head.png`、`kayn_shadow_head.png`（各有 `_1x`） | 要贴进每一帧的头 | 贴头 |
| `design/kayn_palette.png` | 三张造型共用的 24 种颜色（暗到亮） | 色板 |
| `kayn_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/kayn_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、镰刀和身体的动作 |
| `guide/kayn_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `kayn_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/kayn_picture_base/darkin/shadow.png` | 三张造型来源的原画（长相参考；比例和大小以定稿造型为准） | 需要时参考 |
| `style/3_quality_bar.png`、`4_tfm2_style.png` | 我们包里的英雄和团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边（`#0B0710`），描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **手和手臂**：手臂 2–3 格粗、手是实心的拳头；**不要 1 像素的黑细棍、不要飘着的手、不要 90 度的直角手臂**，握镰刀的手和长柄连在一起。
- **镰刀**：RHAAST, the huge war scythe, is in every frame, whole (never broken, shortened or melted into the body): the FIRST image's own scythe - its big crescent blade with the bright cutting edge along the inner curve, the spikes, the eye at the blade's base, the long shaft and the butt spike, in the FIRST image's colours and size - only moved and turned with his hands; the hand that holds it grips the shaft (no gap between hand and shaft)。
- **辫子**：the hair as in the FIRST image: the long black braid (the Shadow Assassin's long loose hair) hangs from the back of his head down his back and swings with the motion (it trails behind him in the run, the dash and the leap); the blue streak stays at the front of his hair; the Darkin has the horned helm instead。
- **腿**：in every standing frame (attack, W's slam, R's landing, hit) the legs are the FIRST image's own legs square for square - the same stance, the same trousers and feet; only Q's dash and hop, W's leap and the transformation's lift stretch, bend or lift the same legs, the run alternates them and the death kneels and falls。
- **头每帧都是造型图的头**（逐格一样），只平移（死亡时整个转）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），刀尖、柄尖都在它上面。now 条有几帧伸到了红线下（普攻、Q 冲刺、W 落地时的脚和刀、R 俯冲时挂在下面的镰刀、死亡时躺下的身体），**这些地方往上收**，全部画在线上面；死亡时倒在地上的镰刀贴着脚底线。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：刀光、斩击、冲击波、地裂、暗影、红色或黑色的光环、血都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，**不要洋红**，会吃掉红色的镰刀和暗裔的身体）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

第 1 部分每张附三张图：第一张 `design/kayn_design.png`，第二张 `now/kayn_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。第 2 部分：第一张换成形态的造型图，`[character]` 换成下面「第 2 部分」那一段，第四张附你画好的同名本体条。`[animation]`、`[R]`、`[grid]`、`[size]` 按表。输出文件名 `kayn_<动作>.png`（第 2 部分 `kayn_rh_<动作>.png` / `kayn_sh_<动作>.png`）。

```text
Attached images (three; four for the forms' strips). FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, clothes, scythe and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same head and face, the same clothes and colours, the same scythe, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the blow, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the scythe and the body from it, but keep the FIRST image's proportions (a big head, the scythe's size); never draw him from the back or upside down. FOURTH (the forms' strips only): the finished base strip of the same action - copy its poses frame for frame, drawn as the FIRST image's form.
The character: [character]
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size as the FIRST image in the idle stance, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the colors of the FIRST image, no new colors (the palette: #0B0710 #141826 #241B45 #232B42 #6E1F33 #3A2C66 #3A4766 #6B3E50 #5C3870 #C60F3E #5B3A8A #5B8498 #FD205B #B8794F #F04060 #9D5FA4 #E9AD37 #38B1FD #C9919B #48E0FF #95C3D4 #FEBF91 #C8CADA #EEEFF7). ONE outline: a 1-square near-black outline (#0B0710) around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added. Hands are solid fists at the ends of arms 2-3 squares wide - never 1-pixel black sticks, floating hands or arms bent at a right angle; the hands that hold the scythe touch its shaft.
The scythe is his signature: RHAAST, the huge war scythe, is in every frame, whole (never broken, shortened or melted into the body): the FIRST image's own scythe - its big crescent blade with the bright cutting edge along the inner curve, the spikes, the eye at the blade's base, the long shaft and the butt spike, in the FIRST image's colours and size - only moved and turned with his hands; the hand that holds it grips the shaft (no gap between hand and shaft).
The hair: the hair as in the FIRST image: the long black braid (the Shadow Assassin's long loose hair) hangs from the back of his head down his back and swings with the motion (it trails behind him in the run, the dash and the leap); the blue streak stays at the front of his hair; the Darkin has the horned helm instead.
The legs: in every standing frame (attack, W's slam, R's landing, hit) the legs are the FIRST image's own legs square for square - the same stance, the same trousers and feet; only Q's dash and hop, W's leap and the transformation's lift stretch, bend or lift the same legs, the run alternates them and the death kneels and falls.
The head (the hair, the face with both eyes, the chin; the Darkin's horned helm with both horns) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the shoulders - no neck.
Feet line: in every cell his lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the scythe's blade or butt spike - because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in kayn_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every swing, dash and slam goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash trails, scythe glow, impact flashes, shockwaves, cracks, dust, shadows of darkness, auras, blood) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green, never magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, the scythe whole in every frame and joined to the hand, the idle's legs in every standing frame, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

第 1 部分的 `[character]`：

```text
Kayn, a lean young shadow assassin: black spiky hair with one bright blue streak at the front and a very long black braid down his back, tan skin, shirtless with dark blue corruption marks on the chest, the near eye amber-gold and the far eye glowing red in a dark patch, a mauve-pink obi sash with a crimson braided rope belt and tassel, baggy indigo trousers with a violet apron, purple boots, and the huge war scythe Rhaast (a crimson crescent blade with a steel-blue edge, spikes and a glowing red eye, a long violet shaft with a crimson butt spike).
```

## 第 1 部分：本体动作条

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `kayn_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `kayn_run.png`（移动） | 8 × 150 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop (8 x 150 ms, League's run): a fast assassin's run, leaning forward; Rhaast carried diagonally across his back as in the THIRD image: the crescent blade up behind his far shoulder (upper left), the shaft running down across his body, gripped by his near hand at the hip, the butt spike pointing down-forward at the lower right, above the ground; the far arm swings back; in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same indigo trousers and purple boots; the braid streams back to the left; the body bobs 1 square down and up over each half; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `kayn_attack.png`（普攻（举镰下劈）） | 6 帧：50 55 62 70 65 65 | 第 4 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK, 6 frames (League's attack: an overhead scythe swing): 1 the idle stance, Rhaast low behind him; 2 standing tall, the scythe swung up behind his head, the blade high over him; 3 the scythe high at the upper left, about to come down, the body turning forward; 4 THE HIT (the blow lands here): a low lunge, the scythe swept forward to the right, level at chest height, the blade at its right end; 5 the follow-through: still low, the scythe level to the right, the braid flying back; 6 he rises, the scythe swung back up behind him (the blade high at the upper left). The slash trail is an effect - do not draw it.` |
| `kayn_skill.png`（Q 巨镰横扫（冲刺 + 旋转）） | 6 帧：50 67 66 84 100 133 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `REAPING SLASH (Q: a dash, then a hop and a spin), 6 frames: 1 he lunges forward, leaning right, the scythe held back over his shoulder; 2 dashing, the body stretched low and forward, the scythe trailing up behind; 3 he lands crouched, the scythe swung out level to the right at knee height; 4 THE SPIN (the blow lands here): he hops up in a tucked spin (as high as in the SECOND image), the scythe level and reaching far out to the right; 5 still in the air, the spin goes on: the scythe swung round to his left, the blade low at the lower left; 6 coming down, the scythe level across his body, back toward the idle stance. The spin's arc is an effect.` |
| `kayn_skill2.png`（W 利刃纵贯（跃起下砸）） | 7 帧：100 140 150 160 117 83 50 | 第 5 帧（tick 33） | 4 列 × 2 行，4096×1536，最后 1 格空 | 第 81 行 | `BLADE'S REACH (W: he leaps and slams the scythe forward), 7 frames: 1 a deep crouch, leaning forward, the scythe held level out to the right; 2 he springs up twisting, the scythe swung down vertical in front of him; 3 rising, the scythe level above his head; 4 the top of the leap (as high as in the SECOND image), stretched up, the scythe level above his head in both hands, the legs hanging; 5 THE SLAM (the blow lands here): landed in a crouch, the scythe brought down in front of him, the blade low ahead of his feet at the lower right; 6 standing, the scythe raised straight up; 7 back toward the idle stance. The long slash along the ground is an effect - do not draw it.` |
| `kayn_ult.png`（R 裂舍影：钻入） | 3 帧：67 67 66 | 第 1 帧（tick 0） | 3 列 × 1 行，3072×768 | 第 81 行 | `UMBRAL TRESPASS - THE DIVE (R: he dives into an enemy and vanishes), 3 frames: 1 the ready stance, the scythe held level across in front of him; 2 he springs forward into the air, the free hand reaching forward, the scythe hanging below him (keep it above the feet line); 3 diving down into the enemy, the body leaning far forward, the scythe raised high above him (he vanishes into the target right after this frame).` |
| `kayn_ult_exit.png`（R 裂舍影：破体而出） | 5 帧：67 67 90 88 88 | 第 1 帧（tick 0） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `UMBRAL TRESPASS - THE EXIT (R: he bursts out of the enemy), 5 frames: 1 THE BURST (the blow lands here): he bursts out in a tight spinning tuck - the body curled, the head kept upright (unlike the THIRD image, never lying level) - the scythe swung round in a wide arc around him; 2 still spinning, the scythe's crescent swung round in front of him to the right; 3 he lands crouched, the scythe raised straight up above him; 4 crouched, the scythe held upright beside him; 5 rising back toward the idle stance. The burst of shadow is an effect.` |
| `kayn_transform.png`（变身（形态定下时播一次）） | 5 帧：100 120 120 130 130 | — | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `TRANSFORMATION (the scythe takes him over: played once when he takes a form), 5 frames: 1 he crouches low, the scythe held upright before him; 2 he rises onto his toes, the scythe raised straight up in front of him; 3 lifted a little off the ground (as in the SECOND image), the scythe straight up above him; 4 landing in a wide stance, the scythe held level, pointing right at chest height; 5 the wide stance, the scythe raised level above his shoulders (a triumphant pose). The red or shadow aura is an effect.` |
| `kayn_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his body and head pushed back 1-2 squares (to the left), the scythe swaying; 2 recovering toward the idle stance.` |
| `kayn_dead.png`（死亡） | 8 帧：120 120 120 140 160 160 200 400 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death): 1 struck, he staggers, hunched, Rhaast planted upright beside him; 2 leaning back, one arm thrown out, still holding the planted scythe; 3-4 sinking to his knees beside the planted scythe, its blade high above him; 5-6 slumping down to the ground at the foot of the scythe; 7-8 lying on the ground (the same pose in 7 and 8), the scythe fallen flat beside him to the right on the feet line; the head stays visible from the 3/4 front (turned with the body, never upside down). Nothing below the feet line.` |

## 第 2 部分：两种形态的出招动作条

**和第 1 部分同名的那张一模一样的帧数、格子、站位、时机和动作**，只是第一张附图换成形态的造型图，头、身体、镰刀都照形态的造型画（暗裔更壮、带大角；影流长发披散、镰刀是银柄青刃）。`[animation]` 用第 1 部分那张的同一段，前面加一句 `The same animation as the FOURTH image (your finished base strip of this action), drawn as this form:`。

暗裔的 `[character]`：

```text
the DARKIN form of this character (FIRST image: a bigger body of crimson demon flesh, blue-grey steel armour plates and spiked bracers, clawed hands and feet, a horned steel helm with two huge curved horns and a skull-like face plate with two glowing red eyes, the same mauve sash, rope belt and indigo trousers, and a bigger crimson scythe with steel spikes and a glowing red eye)
```

影流的 `[character]`：

```text
the SHADOW ASSASSIN form of this character (FIRST image: pale grey-white skin with dark navy shadow markings, the arms dark navy, two glowing pale violet-white eyes, very long LOOSE black hair falling to the knees with the blue streak at the front, the same mauve sash, rope belt and indigo trousers with a long dark-purple robe tail, and the scythe with a silver shaft, a long silver back spike and a dark navy blade with a bright cyan edge)
```

| 文件 | 帧、格子、时机 | 第一张附图 | `[R]` 脚底线 |
|---|---|---|---|
| `kayn_rh_attack.png`（暗裔杀手·普攻（举镰下劈）） | 和 `kayn_attack.png` 一样：6 帧，同一格子、同一站位、同一出手帧（第 4 帧） | `kayn_darkin_design.png` | 第 81 行 |
| `kayn_rh_skill.png`（暗裔杀手·Q 巨镰横扫（冲刺 + 旋转）） | 和 `kayn_skill.png` 一样：6 帧，同一格子、同一站位、同一出手帧（第 4 帧） | `kayn_darkin_design.png` | 第 81 行 |
| `kayn_rh_skill2.png`（暗裔杀手·W 利刃纵贯（跃起下砸）） | 和 `kayn_skill2.png` 一样：7 帧，同一格子、同一站位、同一出手帧（第 5 帧） | `kayn_darkin_design.png` | 第 81 行 |
| `kayn_rh_ult_exit.png`（暗裔杀手·R 裂舍影：破体而出） | 和 `kayn_ult_exit.png` 一样：5 帧，同一格子、同一站位、同一出手帧（第 1 帧） | `kayn_darkin_design.png` | 第 81 行 |
| `kayn_sh_attack.png`（影流刺客·普攻（举镰下劈）） | 和 `kayn_attack.png` 一样：6 帧，同一格子、同一站位、同一出手帧（第 4 帧） | `kayn_shadow_design.png` | 第 81 行 |
| `kayn_sh_skill.png`（影流刺客·Q 巨镰横扫（冲刺 + 旋转）） | 和 `kayn_skill.png` 一样：6 帧，同一格子、同一站位、同一出手帧（第 4 帧） | `kayn_shadow_design.png` | 第 81 行 |
| `kayn_sh_skill2.png`（影流刺客·W 利刃纵贯（跃起下砸）） | 和 `kayn_skill2.png` 一样：7 帧，同一格子、同一站位、同一出手帧（第 5 帧） | `kayn_shadow_design.png` | 第 81 行 |
| `kayn_sh_ult_exit.png`（影流刺客·R 裂舍影：破体而出） | 和 `kayn_ult_exit.png` 一样：5 帧，同一格子、同一站位、同一出手帧（第 1 帧） | `kayn_shadow_design.png` | 第 81 行 |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；第 2 部分和同名的第 1 部分那张一一对应；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡时整个转），两只眼睛都在；
- [ ] **镰刀每帧都在、完整**，样子和造型图一样（月牙刀身、刃口、红眼 / 影流的青刃、长柄、柄尖）；握镰刀的手是实心的、连着长柄；
- [ ] 辫子（影流是长发）连在头后面；站着出招的帧腿和待机一模一样；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交叉迈步、颜色一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点、bbox 和出手帧的刀尖位置都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的每张先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、镰刀是否完整、零散黑格、每帧面积和待机比），不在网格上的重新取样；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`kayn_cells.json` 用包里这份，`kayn_idle.png` 用包里已做好的那张；再加一条全透明的 `r_hidden`（R 钻进体内时播）。
- `import_native.py --hero kayn`：ORDER 待机一张图 + BOB 呼吸，COMPLETE 补描边，NECK 检查头每帧在肩上同一行；形态的 `rh_`/`sh_` 条按同名本体条的格子导入。
- 按出手帧核对技能数据的时机（普攻 tick 10、Q 旋转 tick 11、W 下砸 tick 33、R 破体 tick 0），量刀尖位置定特效挂点，量头像截取点，重跑模拟，做预览 GIF。
