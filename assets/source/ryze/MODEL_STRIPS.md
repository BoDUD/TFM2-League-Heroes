# 瑞兹：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 定稿是用户选的 **A40**：你上一轮生图草稿 A（`ryze_generation_sources/A_concept.png`）按它自己的格子读回，再整行整列删到 40 格（脸和眼睛的行列没删），`design/ryze_design.png`（放大 8 倍，1024×1024；卷轴顶到靴底 40 格，29 格宽，30 色；靴底最下一行在第 99 行、两脚中间在第 64 列）。**你上一轮用代码逐格画的成品 A/B 没有被选中**（脸糊成一团），这一轮请用生图画、再对齐网格，不要用代码拼方块画身体。**造型图就是标准**：光头、蓝紫皮肤和符文纹、皱眉、两只发光的眼睛（近眼 2×2 白、远眼一格浅紫一格白）、深棕长胡子、粗壮的蓝紫手臂和棕色护腕、深海军蓝上衣、交叉皮带、肩甲、圆铜扣腰带、深青布条、灯笼裤、圆铜护膝、棕色靴子、背上的卷轴（米白羊皮纸、铁帽、蓝色徽章），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`ryze_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/ryze_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、腿和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **三处和参考图不一样，以造型图为准**：① 参考图是英雄联盟的比例（手臂细长、腿长），我们**照造型图的比例**：大头、粗短有力的手臂、3×3 的大手、敦实的身体、短腿和灯笼裤；② 头是贴上去的（见下），英雄联盟里他会低头、仰头、转头，我们**头每帧不变形、不旋转、始终是造型图的 3/4 正面**；③ **英雄联盟里瑞兹放技能会跳起、转圈、背对镜头**，我们**每一帧都朝右、看得见脸**，转身只画成肩膀扭一下（卷轴跟着甩到身后），不画背影、不画倒立。
> - **卷轴是他的标志**：每一帧都在背上（画面左侧肩后露出顶端和蓝色徽章），和造型图一样大，只跟着身体平移、最多倾斜一格。
> - **手要像手**：手臂描边里 3 格粗、棕色护腕，末端是 3×3 张开的大手（蓝紫皮肤），连着手臂，不能是 1–2 格的细棍或黑爪子（娑娜的动作帧就出过细棍手臂的问题）。
> - 出招方向：造型是 3/4 正面朝右，**法球、符文禁锢、超负荷都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip（`ryze_strips_pack_done.zip`，放在 outputs 里），HANDOFF.md 最后写。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/ryze_palette.png`，或直接读 `design/ryze_design_1x.png`）。**先把眼睛的两种颜色 #FBFBFD、#B368FD 从色板里去掉**（吸附时会跑到皮肤、羊皮纸、铜扣上），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/ryze_head_1x.png` 里不透明的格子：光头、符文纹、脸、两只发光的眼睛、八字胡和胡子的上半截；在 128×128 画布上的范围 x 56–69、y 61–74，**按图里的形状贴，不是整个方框**——画面左边卷轴的顶端不属于头）原样贴进每一帧头的位置（只平移）。这样每帧的脸都和造型图一模一样。**贴之前先把你自己画的头整个擦掉**，头周围 3 格以内不能留下你自己那张脸、头顶或耳朵的碎块（乐芙兰、阿狸就出过这个问题）。胡子下半截跟着身体画。
5. 对位：每帧按 `ryze_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），靴底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/ryze_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线（靴底）第 99 行 | 每张动作图的第一张附图 |
| `design/ryze_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/ryze_head.png`、`_1x.png` | 要贴进每一帧的头（光头、脸、眼睛、胡子上半截，不含卷轴和身体） | 贴头 |
| `design/ryze_palette.png` | 造型图的全部 30 色（暗到亮） | 色板 |
| `ryze_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/ryze_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、腿和身体的动作 |
| `guide/ryze_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `ryze_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/ryze_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/quality_bar.png`、`tfm2_style_bald.png` | main 里的英雄（德莱厄斯、盖伦、塔里克、李青、维迦）和团战经理2 原版的武僧、大力士、道士，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（卷轴顶到靴底 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 30 种颜色**，不加新颜色；明暗照定稿（铜扣、护膝、铆钉的亮点和头皮、手臂的浅紫高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **手臂 3 格粗、手 3×3**：手臂连着肩膀，手连着护腕，不能是细棍、黑爪子或飘着的手。
- **卷轴每帧都是造型图的卷轴**：同样的大小（顶端露在画面左侧的肩后，米白羊皮纸、铁帽、蓝色徽章），只平移、最多倾斜一格；不能变短、断开或消失。
- **头每帧都是造型图的头**（光头、脸、眼睛、胡子上半截逐格一样），只平移；眼睛的两种颜色 #FBFBFD、#B368FD 只用在眼睛上。
- 头、身体、手臂、腿、卷轴必须连成一个整体，不能有飘在空中的碎块。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），布条、手、卷轴都在它上面。只有死亡最后几帧可以低于红线，最多 1 格。
- **移动循环**：两条腿交替（近腿在前 → 两膝交错 → 远腿在前），靴子最多相距约 10 格，两条腿都用待机的颜色（石板蓝灯笼裤、铜护膝、棕靴子），不要一条亮一条暗；头相对站位点的横向位置每帧不变；身体上下最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：法球、符文、符文禁锢的牢笼、超负荷的光弹、传送门、发光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/ryze_design.png`，第二张 `now/ryze_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `ryze_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, clothes, scroll and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same big bald blue-violet head with the dark rune lines, the stern brow, the two glowing eyes (the near one a 2x2 white, the far one a lilac over a white square) and the long dark-brown beard; the thick bare blue-violet arms with brown bracers and big 3x3 open hands; the dark navy tunic, the brown straps, the bronze-studded pauldron, the belt with the big round bronze buckle, the dark-teal cloth strips, the baggy slate-blue trousers, the round bronze knee guards and the brown boots; the big cream parchment scroll in its brown case with the blue medallion on his back, its top behind his shoulder at image left; the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the legs and the body from it, but keep the FIRST image's proportions (big head, thick short arms, big hands, sturdy body, short legs); never draw him from the back or upside down: where the original spins him, show only a twist of the shoulders, the face still visible.
The character: Ryze, the rune mage (a sturdy bald man with blue-violet skin covered in rune tattoos, glowing eyes and a long brown beard; a sleeveless navy tunic, brown leather straps and a big bronze buckle, baggy trousers, bronze knee guards; a huge parchment scroll carried on his back).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the top of the scroll to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 30 colors of the FIRST image, no new colors: #0F0213 #10041C #321721 #141743 #431F20 #51261D #18235D #112A70 #663322 #23148D #014C78 #7F4226 #494560 #233D98 #097999 #9B592D #511AC4 #329498 #6B44CC #E79845 #9270F2 #C4A68D #40CCFC #B368FD #A88CFB #B59CFC #FBCE84 #C8B5FD #F4EEEA #FBFBFD. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its bronze glints and lavender highlights move with the pose; no dithering, no noise, no random specks added. Arms 3 squares thick inside the outline with a brown bracer, ending in a 3x3 open hand joined to the arm - never 1-2 square sticks, black claws or floating hands; no loose pieces.
The head (the bald head with its rune lines, the face with the glowing eyes, the moustache and the beard's upper part, down to row 74 of the FIRST image) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own drawn head first - nothing of it may stay within 3 squares around the pasted head. The eye colors #FBFBFD、#B368FD appear ONLY in the eyes.
The scroll is the FIRST image's scroll in every frame, the same size, on his back with its top behind the shoulder at image left, only moved with the body and at most tipped by one square; never shortened, broken or missing.
Feet line: in every cell the soles' lowest row is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not a strip of cloth, a hand or the scroll - because the game draws the health bar there (only the last frames of the death may dip 1 square). His place across the cell follows the SECOND image (each frame's standing point is in ryze_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate (near leg forward, the knees crossing, far leg forward), both legs in the idle's colors.
3/4 front view facing right like the FIRST image; every throw, thrust and cast goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (orbs, runes, the rune cage, the bolt, portals, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 104x96 squares (832x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame with nothing of your own head around it, both eyes visible and level, the eye colors only in the eyes, the scroll whole and as big as in the FIRST image in every frame, arms 3 squares thick and hands that read as hands, no loose pieces, the soles on the feet line and nothing below them, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `ryze_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2496×1536 | 第 81 行 | **已做好，不用画** |
| `ryze_run.png`（移动（小跑，两腿交替）） | 8 帧：133 133 134 133 133 134 133 134 | — | 4 列 × 2 行，3328×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop (8 x 133 ms, League's own run cycle): he jogs to the right, upright and sturdy, the legs ALTERNATING: in frames 1-4 the near leg (the one drawn in front) swings forward and plants while the far leg pushes back, in frames 5-8 the other way round, the knees passing each other in frames 3 and 7; the swinging boot lifts 1-2 squares off the feet line, the planted boot stays on it; the shoes at most about 10 squares apart; the arms swing against the legs (the near arm back when the near leg is forward), the hands open; the body bobs down 1 square on the landing frames (1 and 5) and up 1 square between; the scroll rides on his back and bobs with the body; his head keeps the same horizontal place relative to the standing point in all 8 frames; both legs keep the idle's colours (slate-blue trousers, bronze knee guards, brown boots); frame 8 flows into frame 1.` |
| `ryze_attack.png`（普攻（双手推出法球）） | 6 帧：60 70 80 90 100 70 | 第 3 帧（tick 8） | 3 列 × 2 行，2496×1536 | 第 81 行 | `BASIC ATTACK, 6 frames (League's attack1: he flings a rune orb from his open hands): 1 he gathers, the near hand drawn back to his chest, the knees bending; 2 the shoulders turn back a little, both hands cocked back beside his hips; 3 THE FLING (the orb leaves here): a wide low stance, both arms thrust forward to the right at chest height, the palms open, the fingers spread; 4 the arms still out, the body recoiling a little; 5 the arms coming back down; 6 back to the idle stance. The orb is an effect - do not draw it.` |
| `ryze_skill.png`（Q 超负荷（下蹲扭身，单手推出）） | 6 帧：50 50 60 80 90 103 | 第 3 帧（tick 6） | 3 列 × 2 行，2496×1536 | 第 81 行 | `OVERLOAD, 6 frames (League's spell1: a quick crouching spin that hurls the bolt): 1 he dips into a crouch, the near hand drawn back; 2 the shoulders twist back (the scroll swings out behind him), the hand cocked behind his hip - still facing right, the face visible; 3 THE OVERLOAD (the bolt leaves here): a low wide crouch, the near arm thrust straight forward to the right at shoulder height, the palm open toward the target; 4 the arm still out, the body rising; 5 the arms coming back; 6 back to the idle stance. The bolt is an effect - do not draw it.` |
| `ryze_skill2.png`（连招 E→W→Q（法术涌动 → 符文禁锢 → 超负荷）） | 12 帧：78 78 78 78 78 78 78 78 78 78 78 75 | E 第 2 帧、W 第 6 帧、Q 第 9 帧（tick 5 / 23 / 37） | 4 列 × 3 行，3328×2304 | 第 81 行 | `THE COMBO E -> W -> Q, 12 frames of 78 ms (League's spell3, spell2 and spell1 one after the other): 1 SPELL FLUX wind-up: a wide stance, both arms spread out to the sides, palms open; 2 SPELL FLUX (the orb leaves here): the near arm flung forward to the right, the far arm back; 3 the arm recoiling, the body straightening; 4 RUNE PRISON: he rises on his toes, the near hand raised above his head, fingers spread; 5 the hand at its highest; 6 RUNE PRISON (the cage closes on the target here): the hand thrust down and forward to the right, fingers spread, the body leaning in; 7 OVERLOAD: a quick crouch, the near hand drawn back; 8 the shoulders twist back, the hand cocked behind the hip; 9 OVERLOAD (the bolt leaves here): a low crouch, the near arm thrust straight forward to the right; 10 rising, the arm still out; 11 the arms coming back; 12 back to the idle stance. Keep him facing right with the face visible in every frame (League spins him: show it as a twist of the shoulders, never his back). The orb, the cage and the bolt are effects - do not draw them.` |
| `ryze_ult.png`（R 曲境折跃·引导（双手按地开传送门，双臂举起）） | 8 × 125 | — | 4 列 × 2 行，3328×1536 | 第 81 行 | `REALM WARP, the channel, 8 frames of 125 ms (League's spell4: he opens the portal): 1 he spreads both arms wide; 2 he crouches and presses both hands flat on the ground in front of him; 3 and 4 kneeling low, both hands on the ground (drawing the portal), the head bowed a little but the face still visible; 5 he rises, the near arm sweeping up; 6 and 7 standing, both arms raised high and wide; 8 both arms straight up above his head (the moment he warps). The portals and the rune light are effects - do not draw them; his raised hands may reach the top of the cell.` |
| `ryze_ult_land.png`（R 落地（从蹲姿站起）） | 4 帧：67 67 67 66 | — | 4 列 × 1 行，3328×768 | 第 81 行 | `ARRIVAL, 4 frames of 67 ms (League's spell4 wind-down, after the warp): 1 he lands crouched low, both hands touching the ground; 2 rising, the hands leaving the ground; 3 almost up; 4 back to the idle stance.` |
| `ryze_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1664×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: body and head pushed back 1-2 squares (to the left), the scroll tipping back, the arms flung; 2 recovering toward the idle stance.` |
| `ryze_dead.png`（死亡（踉跄后向前扑倒）） | 8 帧：100 100 120 120 150 150 200 400 | — | 4 列 × 2 行，3328×1536 | 第 81 行 | `DEATH, 8 frames (League's death: knocked back, a stagger, then he collapses forward): 1 struck, he reels back, the arms flung out; 2 he staggers upright, a hand pressed to his face; 3 he sways, bowed; 4 still on his feet, swaying; 5 his knees give way, he pitches forward; 6 he falls forward onto the ground; 7 lying flat on his front, the scroll lying on his back; 8 still, the same. Every frame on the feet line; the last frames may reach 1 square below it, nothing lower; never upside down.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头周围 3 格内没有你自己画的头的碎块；两只眼睛都在、同一高度；
- [ ] 眼睛的两种颜色只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 卷轴每帧都完整、和造型图一样大；手臂 3 格粗、手 3×3、连着手臂；没有飘着的碎块；
- [ ] 靴底每帧在脚底线上，脚底线以下没有任何像素（只有死亡最后几帧可以低 1 格）；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：两腿交替、两膝交错，两条腿颜色一样，头的横向位置每帧一样，身体起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧（连招：E 第 2 帧、W 第 6 帧、Q 第 9 帧）；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `ryze_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛颜色只在眼睛上、连通块、手臂粗细、卷轴大小、每帧面积和待机比、头周围 3 格的残留），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`ryze_cells.json` 用包里这份，`ryze_idle.png` 用包里已做好的那张。
- `import_native.py --hero ryze`：ORDER 待机一张图 + BOB 呼吸（上半身往下一格，小腿和靴子不动），EYES = `#FBFBFD`（按眼睛对齐待机和移动），COMPLETE 补描边，PLUG 补描边封出的小洞，NECK 检查肩膀每帧在下巴下面同一行。
- 按出手帧核对技能数据的时机（普攻 tick 8、Q tick 6、连招 E / W / Q tick 5 / 23 / 37、R 引导 60 tick 后落地），量特效挂点（手的高度）和头像截取点，重跑模拟，做预览 GIF。
