# 瑟提：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/sett_design.png`（放大 8 倍，1024×1024；耳尖到脚底 42 格，26 格宽，26 色；脚底在第 99 行，两脚中间在第 64 列，站位点 (64, 88)）。它是你第一轮的生图原稿 B 按自己的格子读回、读到 42 行、再手画了脸和清掉身体里的黑线的版本。**造型图就是标准**：红色刺头和两只兽耳（外面绯红、里面深紫）、脑后的细辫和红珠子、一行琥珀色眼睛、金色项圈和两只金色兽头扣饰、两边炸开的紫色毛领、赤裸的胸肌和腹肌、梅子色长外套和金边、白裤子和金色侧条、梅子色手套加金色指节和金腕环的大拳头、缠白绷带的前臂、金色尖头鞋，颜色、明暗、身材比例，每一帧都照它，只改姿势。
> - **待机条已经做好**（`sett_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/sett_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、拳头和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（42 行高，头约 12 行，宽胸、长腿）——**不要画大、画胖**：之前几个英雄的动作条每帧都画了一个比待机大一圈的身体，最后只能全部用造型的部件重拼；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡倒地时整个头跟着身体转），**不画背影**——英雄联盟里 W 出拳后和 R 飞扑时背对镜头，我们一律胸口朝着画面；③ 英雄联盟的 R 是抓着敌人一起跳起来砸地，我们是**把敌人往前扔出去、再飞扑过去砸地**（被扔的是游戏里真的单位）；E 两边被拽过来的敌人、R 抓住的敌人**都不画**，只画瑟提。
> - **拳头（最重要的标志）**：BOTH FISTS are his weapons and must read in every frame: each one about as big as the FIRST image's fists (about 5 x 5 squares: a plum glove, 3-4 gold knuckle squares, a gold wrist ring, the pale bandages of the forearm above it), CLENCHED (open hands only where the animation line says so), attached to arms as thick as the FIRST image's - never shrunk, never a 1-pixel stick, never melted into the body.
> - **毛领**：the VIOLET FUR MANTLE stays on his shoulders in every frame, bursting out 3-4 squares past both shoulders, pinned by the two gold beast-head clasps; it swings with his shoulders, flares out in the punches, streams back in the flight - and never covers his face.
> - 出招方向：**出拳、扔人、飞扑都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧出拳那只拳头的中心位置）和 `generation_prompts.json`，**生图原稿也一起交（不要缩放或重采样过的）**，最好打成一个 zip（`sett_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。画出来的方块比造型图小（人比造型图大）就重画，**不要缩小**（缩小会把四肢压短压粗）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，读成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**不要把细节比方块还小的高清图压缩下来**，也**不要整行整列删格子**。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/sett_palette.png`，或直接读 `design/sett_design_1x.png`）。**先把眼睛专用的琥珀色 `#C8700A` 从色板里去掉**（吸附时会跑到金饰上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/sett_head_1x.png` 里不透明的格子：头发、两只兽耳、脸，到下巴为止；在 128×128 画布上的范围 x 57–68、y 58–69，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡倒地时整个头跟着转）。这样每帧的脸都和造型图一模一样。头下面接金项圈，不要拉出一截脖子；先擦掉自己画的头再贴，头周围不要留下多余的头发或描边；脑后的细辫从头后面接下去。
5. 对位：每帧按 `sett_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/sett_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/sett_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/sett_head.png`、`_1x.png` | 要贴进每一帧的头（头发、两只兽耳、脸，到下巴） | 贴头 |
| `design/sett_palette.png` | 造型图的全部 26 色（暗到亮） | 色板 |
| `sett_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/sett_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、拳头和身体的动作 |
| `guide/sett_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区（粉色）、帧号和时长 | 对位用，不要画进图里 |
| `sett_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/sett_picture.png` | 造型来源的原画 A（长相参考；比例和大小以定稿造型为准） | 需要时参考 |
| `style/3_quality_bar.png` | 包里的德莱厄斯、亚托克斯、蔚、凯隐、贾克斯，游戏里的样子 ×8 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（耳尖到脚底 42 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 26 种颜色**，不加新颜色；明暗照定稿（金饰的高光、肌肉的亮面跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边 `#050302`，描边里面用材质自己的暗色（外套 `#1F0917`、毛领 `#290B42`、头发 `#55011B`、金 `#361F05`、皮肤 `#B06B44`、裤子 `#9FA8C3`），**不要再画一圈黑、不要零散的黑格、不要横穿身体的黑线**（用户刚让我们把造型身体里的黑线全部清掉）。
- **身材**：照造型图，宽肩、厚胸、窄腰、长腿；**不要把人画大、画胖**；手臂和造型图一样粗（上臂 3 格左右），腿有大腿、膝盖、小腿和鞋。
- **拳头**：BOTH FISTS are his weapons and must read in every frame: each one about as big as the FIRST image's fists (about 5 x 5 squares: a plum glove, 3-4 gold knuckle squares, a gold wrist ring, the pale bandages of the forearm above it), CLENCHED (open hands only where the animation line says so), attached to arms as thick as the FIRST image's - never shrunk, never a 1-pixel stick, never melted into the body。
- **毛领**：the VIOLET FUR MANTLE stays on his shoulders in every frame, bursting out 3-4 squares past both shoulders, pinned by the two gold beast-head clasps; it swings with his shoulders, flares out in the punches, streams back in the flight - and never covers his face。
- **头每帧都是造型图的头**（头发、兽耳、脸逐格一样，只平移；死亡倒地时整个转）；琥珀色 `#C8700A` 只用在眼睛上。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），外套下摆、辫子、毛领都在它上面。只有 R 砸地那一帧砸在地上的拳头可以贴着脚底线。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出拳、扔人、飞扑朝图的右边，**不画背影、不画倒立**。**只画瑟提**：被抓、被拽、被扔的敌人，拳风、巨拳虚影、冲击波、地坑、尘土、速度线都是单独的特效或真的单位，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，不要用洋红——头发是绯红的）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/sett_design.png`，第二张 `now/sett_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `sett_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, costume, fists and the pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same crimson spiky hair with two pointed beast ears (crimson outside, dark violet inside) and the thin braid with its red bead, the same face with amber eyes, the gold torc and the two gold beast-head clasps, the violet fur mantle bursting out on both sides, the bare muscular chest and abs, the long plum coat with its gold trim, the white trousers with the gold stripe, the plum-gloved fists with gold knuckles and wrist rings and the bandaged forearms, the gold curled shoes, the same shading and the same proportions. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the fists and the body from it, but keep the FIRST image's proportions (broad shoulders, a big chest, a narrow waist, long legs, the head about 12 of his 42 squares) and his face toward the viewer; never draw him from the back or upside down.
The character: Sett (a towering half-beast pit fighter: crimson spiky hair with two pointed furry ears, a long thin braid, amber eyes, a gold torc and two gold beast-head clasps holding a huge shaggy violet fur mantle, a bare muscular chest, a long sleeveless plum coat with gold trim, white trousers with gold stripes, big plum-gloved fists with gold knuckles and bandaged forearms, gold curled shoes).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (42 squares from the tips of his ears to his soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. Draw at that size directly; never draw bigger and shrink (shrinking makes the limbs short and fat), and never draw him bigger or bulkier than the FIRST image.
Pixel rules (most important): ONLY the 26 colors of the FIRST image, no new colors: #050302 #1F0917 #290B42 #340F1E #55011B #361F05 #3C1268 #451A2A #810426 #531E8E #AA0C35 #693B08 #C7153E #D51B45 #925B11 #B06B44 #BD7702 #C8700A #DF9704 #DC9263 #9FA8C3 #B2B9D2 #F7C414 #F9BC89 #C4C9DB #DCDFE8. ONE outline: a 1-square near-black (#050302) outline around the silhouette and each material's own dark shade inside it (the coat #1F0917, the mantle #290B42, the hair #55011B, the gold #361F05, the skin #B06B44, the trousers #9FA8C3) - never a second black ring, never stray black squares, never a black line across the body. Copy the FIRST image's shading - the bright gold and the muscles' highlights move with the pose; no dithering, no noise, no random specks added.
The fists are his weapons: BOTH FISTS are his weapons and must read in every frame: each one about as big as the FIRST image's fists (about 5 x 5 squares: a plum glove, 3-4 gold knuckle squares, a gold wrist ring, the pale bandages of the forearm above it), CLENCHED (open hands only where the animation line says so), attached to arms as thick as the FIRST image's - never shrunk, never a 1-pixel stick, never melted into the body.
The mantle: the VIOLET FUR MANTLE stays on his shoulders in every frame, bursting out 3-4 squares past both shoulders, pinned by the two gold beast-head clasps; it swings with his shoulders, flares out in the punches, streams back in the flight - and never covers his face.
The head (the hair, both ears and the face with both eyes, down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the gold torc - no neck. The amber #C8700A appears ONLY in the eyes.
Feet line: in every cell his lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the coat tails, not the braid, not the mantle - because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in sett_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every punch, throw and leap goes to the RIGHT of the image; never his back, never upside down. Draw ONLY him: never the enemies he grabs, pulls or throws, and no effects (punch flashes, the giant fist of energy, shockwaves, craters, dust, speed lines). Every animation starts and ends near the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x80 squares (768x640 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green, never magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, the amber #C8700A only in the eyes, both fists big and clenched (open only where the animation says), the mantle on both shoulders, arms as thick as the FIRST image's, legs with knees and shoes, no loose pieces, no stray black squares or lines, nobody else drawn, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

`[R]` 都是第 67 行（格子 96×80，脚底线在格子底边往上 12 格）。出手帧和技能数据（`tools/kit/sett_kit.py`）对齐：画出来的出手帧必须在表里写的那一帧。

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[animation]` |
|---|---|---|---|---|
| `sett_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1280 | **已做好，不用画** |
| `sett_run.png`（移动（挺胸大步跑，双拳前后摆）） | 8 × 125 | — | 4 列 × 2 行，3072×1280 | `MOVE, 8 frames, one seamless loop (8 x 125 ms, League's run): a heavy, swaggering run, upright, leaning a little forward, chest out; both fists swing with the stride (the near one back when the far one is forward), loosely clenched, never opening; the violet mantle bounces on his shoulders, the coat tails and the braid trail behind him; the steps: in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same white trousers and gold shoes; the body bobs 1 square down and up over each half; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `sett_attack.png`（普攻·左拳刺拳（远处那只拳头）） | 5 帧：67 67 66 100 100 | 第 4 帧（tick 12） | 3 列 × 2 行，2304×1280，最后 1 格空 | `BASIC ATTACK, LEFT JAB, 5 frames (League's attack 1): 1 from the idle stance he raises both fists into a boxer's guard, the knees bending; 2 he shifts his weight forward, the shoulders turning; 3 the FAR fist (his left, on the image right) shoots forward; 4 THE HIT (it lands here): the far arm fully stretched to the right at chest height, the big fist clenched, the near fist guarding his chin, the body leaning into the punch; 5 back toward the idle stance, the fists lowering. The impact flash is an effect - do not draw it.` |
| `sett_attack2.png`（普攻·右拳重拳（近处那只拳头，更快）） | 5 帧：50 50 80 85 85 | 第 3 帧（动作第 3 tick 开播，第 9 tick 打中） | 3 列 × 2 行，2304×1280，最后 1 格空 | `BASIC ATTACK, RIGHT CROSS, 5 frames (League's attack 2, quicker and heavier): 1 the guard, the NEAR fist (his right, on the image left) drawn back by his hip; 2 the hips and shoulders twist to the right, the near fist starting forward; 3 THE HIT (it lands here): the near arm fully stretched to the right across his body at chest height, the big fist in front, the far fist back at his chin, the back heel lifted; 4 the follow-through, the mantle swinging; 5 back toward the idle stance. The impact flash is an effect - do not draw it.` |
| `sett_skill.png`（E 强手裂颅（双臂张开、两边抓住、往中间对撞）） | 7 帧：50 50 67 67 66 100 100 | 第 4 帧抓住（tick 10），第 6 帧对撞（tick 18） | 4 列 × 2 行，3072×1280，最后 1 格空 | `FACEBREAKER (E), 7 frames (League's spell 3 start and front): 1 he crouches, both fists low; 2 he rises and swings both arms out to the sides; 3 both arms stretched wide to the left and right at shoulder height, the hands OPEN like claws (a wide T), the chest open; 4 THE GRAB (it hooks here): still wide, the open hands closing as if seizing someone on each side; 5 he hauls both arms in toward his chest, leaning forward; 6 THE SMASH (here): both fists meet in front of his chest with a clap, his body leaning forward, a step forward; 7 back toward the idle stance. The arms keep the FIRST image's length when they spread (the cell is wide enough). The enemies he grabs are real units - do not draw them; the clash flash is an effect.` |
| `sett_skill2.png`（W 蓄意轰拳（拳头后拉蓄力、一拳轰出）） | 7 帧：80 100 150 153 150 130 137 | 第 5 帧（tick 29） | 4 列 × 2 行，3072×1280，最后 1 格空 | `HAYMAKER (W), 7 frames (League's spell 2, its 0.78-s wind-up shortened to 0.48 s): 1 from the idle stance he starts to coil, the NEAR fist rising; 2 the near fist raised high behind his head, the far arm forward for balance, the knees bending; 3 he coils further, the fist cocked high behind him, the face and chest still to the viewer; 4 the deepest coil, the weight on the back leg - about to explode; 5 THE PUNCH (it lands here): a huge straight punch to the right - the near arm fully stretched to the right at chest height, the body lunging low and forward (the front knee bent, the back leg straight behind him), the mantle and the coat flung back; 6 holding the stretched punch, the fist still out; 7 back toward the idle stance. League turns his back to the camera in frames 5-7: keep him 3/4 front facing right, chest to the viewer. The giant fist of energy and the shockwave are effects - do not draw them.` |
| `sett_ult.png`（R 叹为观止·抓住扔出） | 4 帧：40 40 53 100 | 第 4 帧扔出（tick 8） | 4 列 × 1 行，3072×640 | `THE SHOW STOPPER (R, the grab and the throw), 4 frames (League's spell 4 grab): 1 he lunges forward low, both arms reaching to the right; 2 both hands grab at chest height in front of him (someone is there - do not draw anyone), the body low; 3 he heaves upward, lifting the weight with both arms, the back straightening; 4 THE THROW (it leaves here): he hurls the weight forward and up - both arms flung forward-up to the right, the hands open, the body rising onto the toes, ready to leap. The thrown champion is a real unit - do not draw anyone.` |
| `sett_ult_dash.png`（R 飞扑（平飞着追上去，循环）） | 4 × 125 | — | 4 列 × 1 行，3072×640 | `THE SHOW STOPPER (R, the flight - a loop, 4 frames x 125 ms, League's spell 4 dash): he flies forward through the air after the champion he threw, the body almost horizontal and facing right, about 6-10 squares above the feet line: the near fist stretched forward to the right, the far arm back by his side, both legs trailing behind him slightly bent, the mantle, the coat tails and the braid streaming back; the 4 frames differ only by the cloth and hair streaming (and 1 square of bob); frame 4 flows into frame 1. Keep the chest and face toward the viewer - never his back. No speed lines.` |
| `sett_ult_slam.png`（R 砸地（从上往下双拳砸地、起身）） | 4 帧：67 100 100 133 | 第 2 帧（tick 4） | 4 列 × 1 行，3072×640 | `THE SHOW STOPPER (R, the slam), 4 frames (the end of League's spell 4 power bomb): 1 dropping down from above at an angle, both fists raised together over his head, about to smash down; 2 THE SLAM (here): he lands crouched with both fists smashed into the ground in front of him (the fists ON the feet line, nothing lower), the knees bent wide, the mantle flaring; 3 rising out of the crouch, the fists lifting off the ground; 4 back toward the idle stance. The crater, the dust and the shockwave are effects - do not draw them.` |
| `sett_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×640 | `HIT, 2 frames: 1 jolted back by a blow: his body and head pushed back 1-2 squares (to the left), the fists still clenched, the mantle swaying; 2 recovering toward the idle stance.` |
| `sett_dead.png`（死亡（往后倒、仰躺）） | 8 帧：100 100 110 110 120 150 300 500 | — | 4 列 × 2 行，3072×1280 | `DEATH, 8 frames (League's death): 1 struck, he staggers back; 2 his knees buckle, the fists dropping open; 3 he topples backward; 4 he hits the ground; 5-8 lying on his back, still, the arms spread, the mantle spread under him (the same pose from frame 6 on). The face stays visible (turned with the body, never upside down). Frames 4-8 lie on the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高、一样宽，没有画大画胖；头就是造型图的头（逐格一样，只平移；死亡时整个转），两只眼睛都在；
- [ ] 琥珀色 `#C8700A` 只出现在眼睛上：头部以外 0 个像素；
- [ ] **拳头**：两只都在、都和造型图一样大、握紧（只有表里写张开的帧张开），手臂和造型图一样粗；
- [ ] **毛领**两边都在肩上，没有挡脸；
- [ ] 腿：大腿、膝盖、小腿、鞋都有；脚底线以下没有任何像素；黑边干净，身体里没有零散黑格和横穿的黑线；
- [ ] 没有背影、没有倒立；出拳、扔人、飞扑都朝图的右边；没有画敌人、没有特效；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交叉迈步、颜色一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有网格、文字、编号、参考线；`manifest.json` 写全；生图原稿也交；最后写 `HANDOFF.md`。

## 包怎么做的（给有英雄联盟客户端的那台机器）

```
python tools/lol/native_pose.py assets/source/sett/poses.json --out <渲染文件夹>
python tools/art/pack_sett_strips.py --renders <渲染文件夹> --out <包文件夹>/sett_strips_pack --zip
```

- `poses.json` 的动画名照 `sett_refs.zip` 里 `pose_refs/` 的文件名写的（`Sett_Idle`、`Sett_Run`、`Sett_Attack1`、`Sett_attack2`、`Sett_Spell3_Start`、`Sett_Spell3_Front`、`Sett_spell2`、`Sett_Spell4_Grab`、`Sett_Spell4_Dash`、`Sett_Spell4_PowerBomb`、`Sett_Death`）；名字不对时 `native_pose.py` 会列出所有动画名。
- 渲染出来先看几处再打包：① `sett_native_design.png` 和定稿造型比，头和腿的大小不对就调 `chibi` 的 `head` / `legs`（现在是 2.4 / 0.9）；② 普攻两条：`pose_refs` 每 133 毫秒取一帧，看不出出拳在哪一刻，`attack` 第 4 帧、`attack2` 第 3 帧要是拳头伸到最远的那一刻，不是就改这两帧的时间点；③ R 砸地：`Sett_Spell4_PowerBomb` 约 0.93 秒，`ult_slam` 第 2 帧要是拳头砸到地上的那一刻；④ W 第 5–7 帧和 R 飞扑如果背对镜头，给那几帧加 `"turn"`（见 `native_pose.py` 的说明）。
- 渲染图是 Riot 的模型，只放进包里，不进仓库。

## Claude 导入时（给 Claude 看）

- 交回的 `sett_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、琥珀色只在眼睛上、连通块、四肢粗细、拳头大小、零散黑格、每帧面积和待机比），不在网格上的从生图原稿按格子重新取；头不对的帧换回造型图的头。
- **身体比待机大一圈的帧**（希维尔、凯隐、亚托克斯都发生过）：用造型自己的部件重拼（头、躯干和毛领、两条手臂和拳头、两条腿、外套下摆，`rig_sett.py`，同 `rig_sivir.py`），Codex 的动作条只当姿势参考。
- 放进 `assets/source/native/`，`sett_cells.json` 用包里这份，`sett_idle.png` 用包里已做好的那张。
- `import_native.py --hero sett`：ORDER 待机一张图（要不要 BOB 呼吸给用户看了再定），EYES = `#C8700A`，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 12、右拳 tick 9、E tick 10 / 18、W tick 29、R 扔出 tick 8、砸地 tick 4），量特效挂点和头像截取点（`tfm2_ase.py face`，`champion_view` 现在的 (0, −37) 是临时的），重跑模拟（E、R 是控制技，亚索 R 的模拟也要重跑），做预览 GIF（`tools/art/preview_sett.py`）。
