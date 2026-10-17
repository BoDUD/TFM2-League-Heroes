# 基兰：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 定稿是用户选的 **A2_40**：你上一轮的生图草稿 `A_draft_02.png` 按它自己的格子读回，再整行整列删到 40 格（脸和眼睛的行列没删），`design/zilean_design.png`（放大 8 倍，1024×1024；时钟屋顶到最低的脚趾 40 格，35 格宽，33 色；最低的脚趾在第 99 行、两脚中间在第 64 列）。**造型图就是标准**：背上的大金色时钟（屋顶、象牙白钟面和青色数字、金色齿框、右上的时针、左下的钟摆、两边的小齿轮）、蓝色尖刺头发、尖耳朵、发光的青白眼睛、蓝色长胡子、深灰长袍和红色镶边、红披带、金腰扣、宽袖、掌心向上的手、光脚，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`zilean_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画（大招用 Q 那一条，不用另画）。
> - 帧数、每帧时长、出手帧和站位照 `now/zilean_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **三处和参考图不一样，以造型图为准**：① 参考图是英雄联盟的比例（头小、身体细长），我们**照造型图的比例**：大头大胡子、长袍、宽袖、大时钟；② 头是贴上去的（见下），英雄联盟里他会低头、转头，我们**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（只有死亡倒地的几帧可以整体转倒）；③ 英雄联盟里他施法时会深深弯腰、背上的时钟整个翻到头顶上，我们**只画成上身前倾、时钟往前倾一点**，时钟永远在头的后面，**不能挡住脸**。
> - **时钟是他的标志**：每一帧都在背上，和造型图一样大（屋顶、钟面、数字、齿框、时针、钟摆、小齿轮都在），只跟着身体平移、倾斜；不能变小、断开或消失。
> - **移动是飘着走**（用户选的，和英雄联盟一样）：上身前倾、长袍下摆和红披带往后飘、光脚悬着前后轻轻摆，**不迈步、两腿不交叉**，整个人上下起伏 1 格。
> - **手要像手**：宽袖（描边里 3–4 格粗）、红色袖口，袖口伸出肤色的手（掌心向上或张开推出），连着袖子，不能是 1–2 格的细棍或黑爪子。
> - 出招方向：造型是 3/4 正面朝右，**法球、炸弹、时光发条都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到、是生图画的还是代码拼的）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`；**生图的原稿也请放进 `zilean_strips_sources/`**（瑞兹那一轮原稿比整理后的好），最好打成一个 zip（`zilean_strips_pack_done.zip`，放在 outputs 里），HANDOFF.md 最后写。**请用生图画身体，不要用代码拼方块**（瑞兹那一轮代码拼的成品脸糊成一团）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/zilean_palette.png`，或直接读 `design/zilean_design_1x.png`）。**先把眼睛的三种颜色 #F6F9FA、#BFEBF4、#04749B 从色板里去掉**（吸附时会跑到钟面、头发上），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/zilean_head_1x.png` 里不透明的格子：蓝色头发、尖耳朵、脸、两只发光的眼睛、八字胡和胡子的上半截；在 128×128 画布上的范围 x 54–73、y 68–88，**按图里的形状贴，不是整个方框**——头周围的时钟钟面、金框不属于头）原样贴进每一帧头的位置（只平移）。这样每帧的脸都和造型图一模一样。**贴之前先把你自己画的头整个擦掉**，头周围 3 格以内不能留下你自己那张脸、头发或耳朵的碎块（乐芙兰、阿狸就出过这个问题）。胡子下半截跟着身体画。
5. 对位：每帧按 `zilean_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），最低的脚趾落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/zilean_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线（最低的脚趾）第 99 行 | 每张动作图的第一张附图 |
| `design/zilean_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/zilean_head.png`、`_1x.png` | 要贴进每一帧的头（头发、脸、眼睛、胡子上半截，不含时钟和身体） | 贴头 |
| `design/zilean_palette.png` | 造型图的全部 33 色（暗到亮） | 色板 |
| `zilean_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/zilean_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置（时钟已放大到接近造型） | 第三张附图：手臂和身体的动作 |
| `guide/zilean_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `zilean_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/zilean_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/quality_bar.png`、`tfm2_style_old.png` | main 里的英雄（维迦、娑娜、乐芙兰、塔里克、凯南）和团战经理2 原版的道士、武僧、占星师，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（时钟屋顶到最低的脚趾 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 33 种颜色**，不加新颜色；明暗照定稿（金框、时针、腰扣的亮点和头发里的天蓝高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **宽袖 3–4 格粗、手是肤色的手**：袖子连着肩膀，手连着红色袖口，不能是细棍、黑爪子或飘着的手。
- **时钟每帧都是造型图的时钟**：同样大小（屋顶、钟面、数字、齿框、时针、钟摆、小齿轮），在背上、头的后面，只平移、最多倾斜一点；不能变小、断开、消失，也不能挡住脸。
- **头每帧都是造型图的头**（头发、脸、眼睛、胡子上半截逐格一样），只平移；眼睛的三种颜色 #F6F9FA、#BFEBF4、#04749B 只用在眼睛上。死亡倒地的帧可以把头和身体、时钟一起整体转倒。
- 头、身体、手臂、时钟必须连成一个整体，不能有飘在空中的碎块（时钟两边飘着的小齿轮和造型图一样就可以）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），长袍、披带、钟摆都在它上面。只有死亡最后几帧可以低于红线，最多 1 格。
- **移动循环是飘行**：上身前倾约 15 度，长袍下摆和红披带往后飘，光脚悬着轻轻摆，不迈步；头相对站位点的横向位置每帧不变；身体上下最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：法球、炸弹、时间波纹、时光发条、时钟的发光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/zilean_design.png`，第二张 `now/zilean_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `zilean_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, clothes, clock and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same big spiky blue hair, the pointed ear, the two glowing pale cyan-white eyes and the long blue beard with its moustache; the long dark grey robe with the red trims and the light grey front panel, the red stole, the gold belt buckle, the wide sleeves with red cuffs and the bare tan hands, the bare feet; the giant golden clock on his back (the little roof on top, the ivory face with turquoise numerals, the toothed gold rim, the gold clock hand at the top right, the pendulum at the lower left, the small floating gears); the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms and the body from it, but keep the FIRST image's proportions (big head, big beard, long robe, wide sleeves, the huge clock); where the original bows deeply and tips the clock over his head, show only a forward lean of the shoulders with the clock tipping a little - the clock always behind his head, the face always visible.
The character: Zilean, the time mage (an old man with spiky blue hair and a long blue beard, glowing eyes and pointed ears, a long dark grey robe with red trims and a red stole, bare feet; he floats; a giant golden clock on his back).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the clock's roof to the lowest toe in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 33 colors of the FIRST image, no new colors: #07050B #070514 #17162D #321913 #562910 #70121A #2E2E45 #1A2A74 #81491B #203BA1 #096F97 #A05B16 #04749B #D02B2B #264BCA #B7731A #249BB6 #CF8C20 #76808E #2F6EEE #D17A54 #DD9F26 #3689F8 #ECB432 #3BA5FC #95ACAE #FAD94F #50DBFD #FBC895 #FCF585 #BFEBF4 #F1EAC6 #F6F9FA. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its gold glints and sky-blue highlights move with the pose; no dithering, no noise, no random specks added. Sleeves 3-4 squares thick inside the outline with a red cuff, ending in a tan hand joined to the sleeve - never 1-2 square sticks, black claws or floating hands; no loose pieces (the small gears floating beside the clock as in the FIRST image are fine).
The head (the spiky blue hair, the pointed ear, the face with the glowing eyes, the moustache and the beard's upper part, inside x 54-73, y 68-88 of the FIRST image) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only the lying frames of the death may turn the whole figure). Erase your own drawn head first - nothing of it may stay within 3 squares around the pasted head. The eye colors #F6F9FA、#BFEBF4、#04749B appear ONLY in the eyes.
The clock is the FIRST image's clock in every frame, the same size, on his back behind his head, only moved with the body and at most tipped a little; never shrunk, broken, missing or in front of his face.
Feet line: in every cell the lowest toe's row is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the robe's hem, the stole or the pendulum - because the game draws the health bar there (only the last frames of the death may dip 1 square). His place across the cell follows the SECOND image (each frame's standing point is in zilean_cells.json). In the move loop he floats: no steps, the robe and the stole stream back, his head keeps the same horizontal place relative to the standing point in every frame.
3/4 front view facing right like the FIRST image; every throw, flick and cast goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (the orb, the bomb, time ripples, the warp, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 80x72 squares (640x576 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame with nothing of your own head around it, both eyes visible and level, the eye colors only in the eyes, the clock whole and as big as in the FIRST image in every frame and never over the face, sleeves 3-4 squares thick and hands that read as hands, no loose pieces, the toes on the feet line and nothing below them, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `zilean_idle.png`（待机） | 6 × 180 | — | 3 列 × 2 行，1920×1152 | 第 59 行 | **已做好，不用画** |
| `zilean_run.png`（移动（前倾飘行，不迈步）） | 8 × 97 | — | 4 列 × 2 行，2560×1152 | 第 59 行 | `MOVE, 8 frames of 97 ms, one seamless loop (League's own cycle: he does NOT walk - he FLOATS forward): the body leans forward about 15 degrees and glides to the right, the long robe's hem and the two red stole strips stream back behind him and flutter (their ends wave a little from frame to frame), the bare feet hang under the hem and swing gently back and forth (no steps, the legs never cross like walking), the arms held out a little to his sides with the palms open; the whole figure bobs 1 square up on frames 3-4 and back down on frames 7-8 (the toes never below the feet line); the clock rides on his back and bobs with the body; his head keeps the same horizontal place relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `zilean_attack.png`（普攻（扭肩后单手弹出法球）） | 6 帧：60 70 70 90 100 110 | 第 5 帧（tick 17） | 3 列 × 2 行，1920×1152 | 第 59 行 | `BASIC ATTACK, 6 frames (League's attack1: he twists his shoulders and flicks a time orb from his near hand): 1 he draws the near hand back to his chest; 2 the shoulders turn back, the clock swinging out a little behind him; 3 the twist at its most, the hand cocked behind his shoulder; 4 he starts to turn forward; 5 THE FLICK (the orb leaves here): the near arm thrust forward to the right at chest height, the palm open, the fingers spread; 6 back to the idle stance. The orb is an effect - do not draw it.` |
| `zilean_skill.png`（Q 定时炸弹（弯腰后过顶抛出；大招也用这条）） | 6 帧：60 70 70 90 100 110 | 第 4 帧（tick 12） | 3 列 × 2 行，1920×1152 | 第 59 行 | `TIME BOMB, 6 frames (League's spell1: he bows and lobs the bomb over his head; also played for his ultimate): 1 he lifts the near hand to his shoulder; 2 he bows forward, the clock on his back tipping forward a little over his shoulders, the hand drawn back behind his head; 3 the bow at its deepest - the face still visible, the clock never in front of it; 4 THE THROW (the bomb leaves here): he straightens and swings the near arm up and forward over his head to the right, the palm open; 5 the arm follows through down in front of him; 6 back to the idle stance. The bomb is an effect - do not draw it.` |
| `zilean_w.png`（W 穿梭未来（弯腰，背上的时钟往前倾）） | 5 帧：80 80 90 120 130 | — | 3 列 × 2 行，1920×1152，最后 1 格空 | 第 59 行 | `REWIND, 5 frames (League's spell2: he bows and the clock on his back tips forward as he turns time back): 1 he lifts both open hands in front of his chest; 2 he bows forward, the clock tipping forward over his shoulders; 3 the bow at its deepest, the clock tipped furthest (still behind his head, the face visible under it); 4 he straightens, the clock back on his back; 5 back to the idle stance. The clock's glow and the time spiral are effects - do not draw them.` |
| `zilean_skill2.png`（E 时光发条（弯腰后单手推出）） | 6 帧：60 70 70 90 100 110 | 第 4 帧（tick 12） | 3 列 × 2 行，1920×1152 | 第 59 行 | `TIME WARP, 6 frames (League's spell3): 1 he gathers both hands at his chest; 2 he bows forward a little, the clock tipping; 3 the bow; 4 THE CAST (the warp lands here): he straightens and thrusts the near hand forward to the right, the fingers spread; 5 the arm still out; 6 back to the idle stance. The warp is an effect - do not draw it.` |
| `zilean_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1280×576 | 第 59 行 | `HIT, 2 frames: 1 jolted back by a blow: body and head pushed back 1-2 squares (to the left), the clock tipping back, the arms flung; 2 recovering toward the idle stance.` |
| `zilean_dead.png`（死亡（往后倒在时钟上）） | 8 帧：100 100 110 110 120 150 300 500 | — | 4 列 × 2 行，2560×1152 | 第 59 行 | `DEATH, 8 frames (League's death: he tips backward and falls onto his back, the clock under him): 1 struck, he reels back, the arms flung out; 2 he sways back further; 3 he tips backward, the clock swinging down behind him; 4 falling, the body at about 60 degrees; 5 he lands on his back on top of the clock; 6 lying on his back, the clock flat under and behind him, the beard on his chest; 7 and 8 still, the same. The whole figure turns as one piece (head, body and clock together); never upside down; the last frames may reach 1 square below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头周围 3 格内没有你自己画的头的碎块；两只眼睛都在、同一高度；
- [ ] 眼睛的三种颜色只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 时钟每帧都完整、和造型图一样大，在头后面、没挡脸；宽袖 3–4 格粗、手是肤色的手、连着袖子；没有飘着的碎块；
- [ ] 最低的脚趾每帧在脚底线上，脚底线以下没有任何像素（只有死亡最后几帧可以低 1 格）；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：前倾飘行、长袍和披带往后飘、不迈步，头的横向位置每帧一样，身体起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了；生图原稿在 `zilean_strips_sources/`。

## Claude 导入时（给 Claude 看）

- 交回的 `zilean_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛颜色只在眼睛上、连通块、手臂粗细、时钟大小、每帧面积和待机比、头周围 3 格的残留），不在网格上的重新取样（先看原稿 `zilean_strips_sources/`，每条按它自己的格子大小读）；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`zilean_cells.json` 用包里这份，`zilean_idle.png` 用包里已做好的那张。
- `import_native.py --hero zilean`：ORDER 待机一张图 + BOB 呼吸（上半身往下一格，长袍下摆不动），EYES = `#F6F9FA`（按眼睛对齐待机和移动），COMPLETE 补描边，PLUG 补描边封出的小洞，NECK 检查肩膀每帧在下巴下面同一行。
- 按出手帧核对技能数据的时机（普攻 tick 17、Q tick 12、E tick 12、W 的动作 500 ms），量特效挂点（手的高度）和头像截取点，重跑模拟，做预览 GIF。
