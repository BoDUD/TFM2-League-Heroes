# 瑞兹：第二版造型的动作帧（给 Codex 的提示词）

> **为什么重画**：用户觉得瑞兹「有点胖了」。新造型已经定了：`design/ryze_design.png` —— 你画的 v2 方案 **B** 的瘦身体（瘦、窄肩、细手臂、窄裤腿），头换回第一版的头（光头、符文纹、发光的眼睛、长胡子，用户认可的脸），手重画过。站着 **41 格高、25 格宽**，30 色。**造型图就是标准**。
> 我（Claude）先用代码按造型图的零件拼了动作，用户看了说「太僵硬了手臂」「手还是有点怪」「腿部和身体分离」「死亡的时候姿势也是很奇怪」「还是太奇怪了」，最后说「改不好就让gpt重画吧」。所以这一轮请**用生图画**，再对齐网格。
> - **待机条已经做好**（`ryze_idle.png`，每帧就是造型图），不用画。其余 8 张动作图按下面的表重画。
> - **动作照第一版的动作条**（`old/ryze_old_<动作>.png`，第一版的胖身体，用户都看过、认可了这些动作和节奏）；帧数、每帧时长、出手帧、站位照 `now/ryze_now_<动作>.png`（英雄联盟原版按游戏尺寸取色）；身体怎么动看 `pose/lol_pose_<动作>.png`（同一帧的渲染，已经按新身材的比例出图）。**身体、手臂、腿、卷轴照新造型**。
> - **腿（用户定的规矩）**：站着放技能、受击、普攻的每一帧，**腿就是待机的腿**——同样直、同样宽、同样的位置，靴子平踩在脚底线上；**不要岔开成大弓步、不要蹲、不要外八字、不要一条腿斜着**（凯特琳、卡莎都因为这个返工过，用户每个动作都拿待机比腿）。动作靠上半身表现：身体前倾或后仰、肩膀扭转、手臂。只有表里写了的帧才单膝跪地（R 引导、R 落地、连招第 7 帧、死亡），跑步照跑步的规矩，死亡最后趴在地上。
> - 交回的图每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`、`manifest.json`（每帧的格子矩形、站位点、bbox），打包成 `ryze_strips_v2_done.zip` 放在 outputs 里（`outputs/ryze-strips-v2/`），HANDOFF.md 最后写。

## 建议流程（每一张动作条）

1. 生图：附图顺序见通用提示词（造型图、now 条、lol_pose、第一版的动作条）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/ryze_palette.png`）。**先把眼睛的两种颜色 #FBFBFD、#B368FD 从色板里去掉**，它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/ryze_head_1x.png` 里不透明的格子：光头、符文纹、脸、两只发光的眼睛、胡子上半截；在 128×128 画布上的范围 x 57–71、y 59–70，按图里的形状贴，左边卷轴的顶端不属于头）原样贴进每一帧头的位置，只平移；**贴之前先把你自己画的头整个擦掉**，头周围 3 格内不能留下你自己的脸、头顶、耳朵的碎块；胡子下半截跟着身体画。死亡趴地的帧也贴（下巴贴地、脸朝右看得见）。
5. **站着的帧贴待机的腿**：把造型图从腰带下面到靴底的两条腿（`design/ryze_legs_1x.png`）原样贴回每一个站着的帧（普攻、Q、连招除第 7 帧以外、受击、R 第 1、5–8 帧、R 落地第 3–4 帧、死亡第 1–2 帧），只左右平移，靴底踩在脚底线上。
6. 对位：每帧按 `ryze_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/ryze_design.png` | **新造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，靴底第 99 行 | 每张的第一张附图 |
| `design/ryze_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头、贴腿 |
| `design/ryze_head.png`、`_1x.png` | 只有头，在画布上原来的位置 | 贴头 |
| `design/ryze_legs.png`、`_1x.png` | 只有两条腿（腰带下面到靴底），在画布上原来的位置 | 站着的帧贴腿 |
| `design/ryze_palette.png` | 造型图的全部 30 色（暗到亮） | 色板 |
| `ryze_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/ryze_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的渲染（新身材比例），同样的格子 | 第三张附图：手臂和身体的动作 |
| `old/ryze_old_<动作>.png` | **第一版造型的动作条（用户认可的动作）**，同样的格子 | 第四张附图：照它的姿势和节奏（身体换成新造型、腿换成待机的腿） |
| `guide/ryze_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `ryze_cells.json` | 每帧的站位点（格子里第几列、第几行）和帧时长 | 整理对位 |
| `refs/ryze_design_B_master.png` | 你画的 v2 方案 B 原图（新身体的来源） | 需要时参考身体和手臂的画法 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（卷轴顶到靴底 41 格），每个像素一个 8×8 方块，同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 30 种颜色**，大块纯色，不要抖动、噪点、零散的碎点；外轮廓 1 格近黑描边，里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（逐格一样，只平移）；眼睛的两种颜色 #FBFBFD、#B368FD 只用在眼睛上。
- **身体照造型图（瘦）**：窄肩、细手臂、海军蓝上衣、交叉皮带、肩甲、铜扣腰带、深青布条、窄裤腿、棕靴；不要画回第一版的粗胳膊、宽身体、灯笼裤。
- **手臂和手**：手臂和造型图一样粗（描边里 3 格），连着肩膀；手肘自然弯曲，不要伸成笔直的细棍；手是造型图那样的蓝紫色手（握拳 3×3，出招时张开的手掌 3×4，手指并拢），连着棕色护腕；**不能是细棍、黑爪子、叉子一样的手指、球一样的手**。远侧的手臂（画面左边那条）大多贴着身体或藏在身体后面，不要甩成一根长棍伸出去。
- **腿（用户定的规矩）**：站着的每一帧腿就是待机的腿（同样直、同样宽、同样位置），只有表里写了的帧才跪下；跑步两腿交替；死亡最后趴地。
- **卷轴每帧都在背上**，和造型图一样大，只平移、最多倾斜一格；不能变短、断开或消失。
- 每帧整个人连成一块，没有飘着的碎块，手臂和身体之间不要留透底的小洞。
- **脚底线以下什么都不能有**（游戏在脚下画血条），只有死亡趴地的帧可以低 1 格。
- **移动循环**：两条腿交替、前后交叉，两只鞋最多相距 10 格，两条腿颜色一样；头相对站位点的横向位置每帧一样，上下起伏最多 1 格；首尾能接上。
- 3/4 正面朝右，看得到脸；出招朝图的右边；**不画背影、不画倒立**。**只画角色**：法球、符文、牢笼、光弹、传送门、发光都是单独的特效，不要画。每个动作开始和结束都接近待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附四张图：`design/ryze_design.png`、`now/ryze_now_<动作>.png`、`pose/lol_pose_<动作>.png`、`old/ryze_old_<动作>.png`。输出 `ryze_<动作>.png`。

```text
Four attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, lean body, arms, hands, legs, boots and scroll exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames in the same grid - the motion of the arms and the upper body. FOURTH: the previous, approved version of these frames drawn on an older, bulkier body - copy its poses, gestures and timing, but draw the FIRST image's lean body, thin arms and narrow trousers instead.
The character: Ryze, the rune mage: a bald man with blue-violet skin and dark rune lines, a stern brow, two glowing eyes and a long dark-brown beard; a sleeveless dark navy tunic with brown leather straps crossing it, a bronze-studded shoulder pad, a belt with a round bronze buckle, a dark-teal cloth strip hanging in front, narrow navy trousers and brown boots with bronze cuffs; bare blue-violet arms with brown leather bracers; a big cream parchment scroll in its case strapped on his back, its top behind his shoulder at image left.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (41 squares from the top of the scroll to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 30 colors of the FIRST image, no new colors: #0F0213 #10041C #321721 #141743 #431F20 #51261D #18235D #112A70 #663322 #23148D #014C78 #7F4226 #494560 #233D98 #097999 #9B592D #511AC4 #329498 #6B44CC #E79845 #9270F2 #C4A68D #40CCFC #B368FD #A88CFB #B59CFC #FBCE84 #C8B5FD #F4EEEA #FBFBFD. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no random specks.
Arms and hands: the arms as thick as in the FIRST image (3 squares inside the outline), joined to the shoulders, the elbows bent naturally - never a straight thin stick; the hands like the FIRST image's hands (a blue-violet fist of 3x3 squares; an open palm of 3x4 with the fingers together when he casts), joined to the brown bracers - never claws, forks of single-square fingers, balls or floating hands. The far arm (image left) mostly stays close to the body or behind it; it is never flung out as a long stick.
LEGS (the art director's rule): in every STANDING frame (attacks, casts, the hit, standing up after the ult) his legs are the FIRST image's legs exactly: straight, the same width apart, in the same place under him, the boots flat on the feet line - never a wide stance, never crouching, never toes turned out, never one leg slanted. Show the action with the upper body only: the torso leaning forward or back, the shoulders twisting, the arms. He kneels ONLY where the animation says so (the far knee on the ground with its shin flat behind, the near foot planted ahead).
The head (the bald head with its rune lines, the face with the glowing eyes, the moustache and the beard's upper part) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it. The eye colors #FBFBFD、#B368FD appear ONLY in the eyes. The scroll is the FIRST image's scroll in every frame, the same size, on his back, only moved with the body.
The whole figure is ONE connected piece in every frame, with no little holes of background walled in between an arm and the body.
Feet line: in every cell the soles' lowest row is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down (only the lying frames of the death may dip 1 square). His place across the cell follows the SECOND image (each frame's standing point is in ryze_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate and cross, both in the FIRST image's leg colors.
3/4 front view facing right like the FIRST image; every throw, thrust and cast goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (orbs, runes, the rune cage, the bolt, portals, glows) - only the character. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 104x96 squares (832x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `ryze_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2496×1536 | 第 81 行 | **已做好，不用画** |
| `ryze_run.png`（移动（小跑，两腿交替）） | 8 帧：133 133 134 133 133 134 133 134 | — | 4 列 × 2 行，3328×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop (8 x 133 ms; the FOURTH image's run on the FIRST image's lean body): he jogs to the right, the upper body leaning a little forward, the legs ALTERNATING - frames 1-4 the near leg (drawn in front) swings forward and plants while the far leg pushes back, frames 5-8 the other way round, the knees passing each other in frames 3 and 7; the swinging boot lifts 1-3 squares, the planted boot stays on the feet line, the shoes at most 10 squares apart; the arms swing against the legs with the elbows bent and the hands loosely closed; the body bobs down 1 square on the landing frames (1 and 5); the scroll rides on his back; his head keeps the same horizontal place relative to the standing point in all 8 frames; both legs in the FIRST image's leg colours; frame 8 flows into frame 1.` |
| `ryze_attack.png`（普攻（单手推出法球）） | 6 帧：60 70 80 90 100 70 | 第 3 帧（tick 8） | 3 列 × 2 行，2496×1536 | 第 81 行 | `BASIC ATTACK, 6 frames (the FOURTH image's motion, League's attack1: he flings a rune orb from his open near hand): 1 he gathers, the far fist in front of his chest, the near hand low in front; 2 the shoulders turn back, the near hand drawn back to his hip; 3 THE FLING (the orb leaves here): the near arm thrust forward to the right at chest height, the elbow a little bent, the palm open toward the target, the far fist pulled back to his hip, the upper body leaning into the throw; 4 the arm still out, a little higher; 5 the arm coming back down; 6 back to the idle. On the FIRST image's legs in every frame.` |
| `ryze_skill.png`（Q 超负荷（单手推出）） | 6 帧：50 50 60 80 90 103 | 第 3 帧（tick 6） | 3 列 × 2 行，2496×1536 | 第 81 行 | `OVERLOAD, 6 frames (the FOURTH image's motion, League's spell1): 1 he gathers, both hands low in front of him; 2 the shoulders twist back, the near hand cocked at his hip, the far hand raised behind his shoulder - still facing right, the face visible; 3 THE OVERLOAD (the bolt leaves here): the near arm thrust straight forward to the right at shoulder height, the palm open toward the target, the upper body leaning into it; 4 the arm sweeping up and forward, the palm open; 5 the arms coming back; 6 back to the idle. On the FIRST image's legs in every frame.` |
| `ryze_skill2.png`（连招 E→W→Q（法术涌动 → 符文禁锢 → 超负荷）） | 12 帧：78 78 78 78 78 78 78 78 78 78 78 75 | E 第 2 帧、W 第 6 帧、Q 第 9 帧（tick 5 / 23 / 37） | 4 列 × 3 行，3328×2304 | 第 81 行 | `THE COMBO E -> W -> Q, 12 frames of 78 ms (the FOURTH image's motion; League's spell3, spell2 and spell1 one after the other): 1 SPELL FLUX wind-up: both arms spread out to the sides, the palms open; 2 SPELL FLUX (the orb leaves here): the near arm flung forward and up to the right, the palm open, the far arm back; 3 the near hand drawn back to his chest; 4 RUNE PRISON: the far hand raised high above his head, the fingers spread; 5 the hand at its highest; 6 RUNE PRISON (the cage closes on the target here): the near hand thrust down and forward to the right, the palm open, the upper body leaning in; 7 OVERLOAD: he drops onto one knee (the far knee on the ground, its shin flat behind, the near foot planted ahead), the near hand drawn back; 8 up again on the FIRST image's legs, the near hand cocked behind his hip; 9 OVERLOAD (the bolt leaves here): the near arm thrust straight forward to the right, the palm open; 10 the arm sweeping up; 11 the arms coming back; 12 the idle. Facing right with the face visible in every frame (League spins him: show it as a twist of the shoulders, never his back).` |
| `ryze_ult.png`（R 曲境折跃·引导（单膝跪地双手按地，起身举手）） | 8 × 125 | — | 4 列 × 2 行，3328×1536 | 第 81 行 | `REALM WARP, the channel, 8 frames of 125 ms (the FOURTH image's motion, League's spell4): 1 he spreads both arms wide, the palms open; 2 he drops onto one knee and presses both hands flat on the ground in front of him; 3 and 4 kneeling, both hands on the ground (drawing the portal), the head a little bowed but the face visible; 5 he stands up on the FIRST image's legs, the far arm sweeping up; 6 standing, the far arm raised high, the palm open; 7 and 8 both arms raised high and wide, the hands closed (the moment he warps). The portals and the rune light are effects - do not draw them.` |
| `ryze_ult_land.png`（R 落地（单膝跪地起身）） | 4 帧：67 67 67 66 | — | 4 列 × 1 行，3328×768 | 第 81 行 | `ARRIVAL, 4 frames of 67 ms (League's spell4 wind-down, after the warp): 1 he lands on one knee, a hand touching the ground in front; 2 rising onto the FIRST image's legs, the arms out for balance; 3 almost the idle; 4 the idle.` |
| `ryze_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1664×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: the upper body and head pushed back 1-2 squares (to the left), the scroll tipping back, the arms flung out - the legs stay the FIRST image's legs; 2 recovering toward the idle.` |
| `ryze_dead.png`（死亡（被击退、跪倒、向前扑倒趴地）） | 8 帧：100 100 120 120 150 150 200 400 | — | 4 列 × 2 行，3328×1536 | 第 81 行 | `DEATH, 8 frames (the FOURTH image's motion, League's death): 1 struck, he reels back, the arms flung out (on the FIRST image's legs); 2 he staggers, a hand pressed to his face; 3 his knees give way: down on one knee; 4 down on both knees, slumping forward; 5 pitching forward, the hands reaching for the ground; 6 he falls forward onto the ground; 7 lying flat on his front on the feet line, the scroll lying on his back, the head up with the chin on the ground and the face visible; 8 still, the same. Never upside down; the lying frames may dip 1 square under the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；只用造型图色板里的颜色；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），头周围 3 格内没有你自己画的头的碎块；两只眼睛都在、同一行；眼睛的两种颜色只在眼睛上；
- [ ] **站着的帧腿就是待机的腿**（同样直、同样宽、同样位置）；跪的帧只在表里写的地方；
- [ ] 身体是新造型的瘦身体；手臂和造型图一样粗、手肘自然弯；手是造型图那样的手（拳头 3×3、张开的手掌 3×4），没有细棍、爪子、叉子、球；
- [ ] 卷轴每帧都在、和造型图一样大；每帧整个人连成一块，没有透底的小洞；脚底线以下没有像素（死亡趴地的帧可以低 1 格）；
- [ ] 移动循环：两腿交替、前后交叉，两只鞋最多相距 10 格，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧（连招：E 第 2 帧、W 第 6 帧、Q 第 9 帧）；没有背影、没有倒立；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `ryze_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛颜色只在眼睛上、连通块、手臂粗细、卷轴大小、站着的帧腿和待机一样），不对的帧换回造型图的头和腿。
- 放进 `assets/source/native/`，`ryze_cells.json` 用包里这份（就是仓库里的），`ryze_idle.png` 用包里已做好的那张；`import_native.py --hero ryze`。
- 按出手帧核对技能数据的时机（普攻 tick 8、Q tick 6、连招 E / W / Q tick 5 / 23 / 37），量特效挂点（Q / E 的手掌）、头像截取点和 banpick_center，做预览 GIF。
