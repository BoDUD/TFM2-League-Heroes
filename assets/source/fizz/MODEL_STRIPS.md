# 潮汐海灵 菲兹：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：A**（你上一轮的游戏尺寸原稿 A，Claude 按它自己的格子逐格读回，没有缩放；两种近黑描边合成一种，三叉戟杆尾宝石那一格改成三叉戟的青绿色，让亮绿只留在眼睛上）：`design/fizz_design.png`（放大 8 倍，1024×1024，55×32 格、23 色，鞋底在 y=792–799）。**造型图就是标准**，颜色、形状、头、脸、三叉戟一律照它。用户没有选你后来逐格重画的 34 行正面版。
> - **待机条已经做好**（`fizz_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/fizz_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。**三叉戟长度照造型图**（两端约 55 格）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。最好打成一个 zip（`fizz_strips_pack_done.zip`）放在 outputs 里。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/fizz_palette.png`，或直接读 `design/fizz_design_1x.png`）。**先把眼睛的亮绿 `#20AE56` 从色板里去掉**（它和三叉戟的绿很近，一吸附就会跑到身上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/fizz_head_1x.png`：蓝色大圆头、两片下垂的耳鳍和它们的橙色褶边、眼睛、嘴和描边；在 128×128 画布上的范围 x 44–77、y 68–83）原样贴进每一帧头的位置，只平移；身体倾斜时整体倾斜。**E 倒立的那几帧，头是造型图的头上下翻转**（脸仍朝右）；**Q 翻跟头的帧，头按四分之一圈转**（0°、90°、180°、270°，像素原样转，不重画）；死亡倒地的帧可以不贴。贴的头的下巴下面，奶黄色的喉咙从眼睛最下一行往下第 4 行开始，每一帧都一样（菲兹没有脖子：下巴直接接喉咙和肩膀，但不能把头压进身体）。受击第 1 帧把眼睛改成闭眼（眼睛那一行各一段深色短线）。
5. **三叉戟**：杆是 1 格粗的深红色，上下各一格描边（共 3 行），不断开；翠绿的三根叉齿、钢色刃边、蓝宝石和杆尾的金环都照造型图；长度和造型图一样；斜着的时候也是一格一格连着的直线，不断开、不弯。
6. 对位：每帧按 `fizz_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人连成一块（死亡里掉在地上的三叉戟除外），手至少 2×2 格、连着至少 3 格粗的手臂。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/fizz_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，鞋底第 99 行 | 每张动作图的第一张附图 |
| `design/fizz_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/fizz_head.png`、`fizz_head_1x.png` | 只有头（头、耳鳍、脸），在画布上原来的位置 | 贴头 |
| `design/fizz_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `fizz_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/fizz_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体和三叉戟的动作 |
| `guide/fizz_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `fizz_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/fizz_picture.png` | 用户选的设定图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_pole.png`、`style/quality_bar.png` | 团战经理2 原版拿长柄武器的英雄、本包的小个子英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（32 格，头顶到鞋底），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（头顶的浅色斑点、两片耳鳍和橙色褶边、眼睛、嘴逐格一样），只平移或整体倾斜（E 倒立时上下翻转，Q 翻跟头时按四分之一圈转）；亮绿 `#20AE56` 只用在眼睛上。
- **三叉戟每帧都在**（死亡第 2 帧飞出去之后，平躺在他前面的地上）：杆 1 格深红加上下描边，叉头三根齿，杆尾金环；握在手里，不能断开、不能飘开、不能挡脸。
- **手和手臂**：小手至少 2×2 格，手臂从肩膀到手至少 3 格粗（含描边），不能画成 1–2 格的细线（在游戏里像"无影手"）；每帧整个人连成一块。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），叉尖、杆尾也不能低于它。只有死亡趴倒的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间有两膝交叉的帧），两条腿颜色和待机一样（小腿和脚是深海军蓝），每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，看得到脸，不画背影（E 倒立时脸也朝右）。**只画角色**：水花、刺击的风压、鱼、鲨鱼这些都是单独的特效，不要画。每个动作开始和结束都接近造型图的待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/fizz_design.png`，第二张 `now/fizz_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `fizz_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, trident and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms and the trident from it.
The character: a small mischievous amphibious trickster: smooth sky-blue skin with pale spots on the crown, a big round head with two long blue fin-ears drooping past the shoulders (orange-red frills on their inner edges), big round eyes with heavy blue lids, white eyeballs and bright green irises, a thin sly grin, a pale cream throat and belly, thin arms with small hands, legs and big webbed feet turning deep navy-blue below the knees, a short tail with a small gold ring. His weapon is a long trident: a crimson shaft ONE square thick with the outline above and below it, a jade three-prong head with pale steel edges and a blue gem at the right end, a round gold ring end at the left end.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (32 squares tall from the crown to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #121122 #0F3B3C #3D3223 #4C2029 #0A5B4A #23405E #1C3775 #811C2C #078E76 #2651A5 #8A6431 #20AE56 #AA4A36 #2D69BB #CE5F37 #7B7D7A #3596C6 #39A1C6 #C59B4C #BBB798 #96B9C6 #E4DDC0 #DEDFD5. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (crown spots, fin-ears with their orange frills, face, eyes, grin) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); in the handstand frames it is the FIRST image's head flipped upside down (top to bottom, the face still toward the right); in the somersault frames it is turned by quarter turns; never redraw it, or it flickers when the frames play. Under the chin keep the FIRST image's rows: the cream throat starts 4 rows under the eyes' lowest row in every frame; never sink the head into the body. The eyes are the FIRST image's eyes; the bright green #20AE56 appears ONLY in the eyes. The trident is in every frame (until it flies off in the death), whole, straight and as long as in the FIRST image (about 55 squares end to end), held in his hands; the hands at least 2x2 squares and the arms at least 3 squares thick from the shoulder to the hand, never a 1-2 square line; the whole figure is ONE connected piece in every frame.
Feet line: in every cell the lowest row of his feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the prongs, not the butt end - because the game draws the health bar there (the lying frames of the death may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in fizz_cells.json). In a move loop his head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, his face always visible, never his back. Do not draw effects (water splashes, thrust waves, the fish, the shark, glows) - only the character. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x112 squares (896x896 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame (flipped or turned only where the animation says), the green only in the eyes, the trident whole with a 1-square crimson shaft, the arms at least 3 squares thick with the hands on the shaft, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `fizz_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1792 | 第 97 行 | **已做好，不用画** |
| `fizz_run.png`（移动） | 8 帧：107 107 107 107 107 107 107 108 | — | 4 列 × 2 行，3584×1792 | 第 97 行 | `MOVE, 8 frames, one seamless loop of League's run (0.86 s, 8 x 107 ms; the SECOND and THIRD images): he scampers forward a little hunched, the trident held slanting across the front of him in both hands as in the THIRD image (the prongs low in front to the right, the round butt end up behind his shoulder); the legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames, the big webbed feet flat on the ground line when planted; the fin-ears bounce a little; his head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `fizz_attack.png`（普攻） | 6 帧：70 70 60 60 70 70 | 第 3 帧（tick 8） | 3 列 × 2 行，2688×1792 | 第 97 行 | `BASIC ATTACK, 6 frames, a quick trident jab as in the THIRD image: 1 from the idle he draws the trident back; 2 cocked, the prongs pulled back beside his body; 3 THE RELEASE (the hit lands here): he lunges and jabs the trident straight out to the right at waist height, the prongs far forward; 4 holding the jab; 5 pulling it back; 6 back toward the idle of the FIRST image.` |
| `fizz_attack_w.png`（W 海石三叉戟的强化打击） | 7 帧：60 60 70 70 80 80 80 | 第 5 帧（tick 16） | 4 列 × 2 行，3584×1792，最后 1 格空 | 第 97 行 | `SEASTONE TRIDENT, the empowered strike, 7 frames as in the THIRD image: 1 he crouches; 2 he hops up, the trident swinging up; 3 at the top of the hop (about 6-8 squares above the ground), the trident raised; 4 coming down, the trident lifted high; 5 THE RELEASE (the hit lands here): he drives the trident down and forward into the enemy in front of him to the right; 6 landed, crouching over the trident; 7 back toward the idle. His feet are on the ground line again from frame 5.` |
| `fizz_skill.png`（Q 淘气打击） | 7 帧：50 50 50 50 50 60 57 | 第 4 帧（tick 9） | 4 列 × 2 行，3584×1792，最后 1 格空 | 第 97 行 | `URCHIN STRIKE, the dash through the target, 7 frames as in the SECOND and THIRD images: 1 he crouches low, the trident pulled back; 2 he launches forward, body leaning far forward; 3 he tumbles head over heels along the ground (body upside down), the trident thrust ahead; 4 THE STRIKE (he passes through the enemy here): coming round the somersault, a quarter turn on, the trident still ahead; 5 coming out of the roll onto his feet; 6 landing in a crouch, the trident forward; 7 back toward the idle. The game moves him along the ground; keep him inside his cell, his lowest point on the feet line or above it.` |
| `fizz_skill2.png`（E 古灵精怪（倒立在三叉戟上）） | 8 帧：50 70 100 200 200 80 60 73 | 第 7 帧（tick 42） | 4 列 × 2 行，3584×1792 | 第 97 行 | `PLAYFUL / TRICKSTER, 8 frames as in the THIRD image: 1 he crouches; 2 he springs up with the trident; 3 he plants the trident UPRIGHT in the ground - the prongs down on the feet line, the shaft standing straight up, the round butt end on top - and lands UPSIDE DOWN in a one-handed HANDSTAND on the top end of the shaft, his feet up in the air; 4-5 balancing in that handstand on top of the trident (these two frames last 200 ms each); 6 he flips off and down, pulling the trident out of the ground; 7 THE SLAM (the hit lands here): he lands on his feet and slams the trident down in front of him to the right; 8 back toward the idle. The planted trident is as long as in the FIRST image (about 55 squares), so the handstand frames are tall - that is right, keep them inside the cell.` |
| `fizz_ult.png`（R 巨鲨强袭（甩鱼）） | 7 帧：60 60 50 70 80 90 90 | 第 3 帧（tick 7） | 4 列 × 2 行，3584×1792，最后 1 格空 | 第 97 行 | `CHUM THE WATERS, the fish throw, 7 frames as in the THIRD image: 1 he winds up, the trident in his near hand; 2 he reaches back with the free hand, which holds a small fish; 3 THE RELEASE (the fish leaves here): he flings his free arm forward to the right, the hand open (the flying fish is a separate effect - draw no fish from this frame on); 4-5 the follow-through, the arm stretched forward; 6-7 back toward the idle, the trident held across him again.` |
| `fizz_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1792×896 | 第 97 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back, eyes squeezed shut (two short dark lines on the eyes' rows); 2 recovering toward the idle.` |
| `fizz_dead.png`（死亡） | 8 帧：100 100 110 120 130 150 250 500 | — | 4 列 × 2 行，3584×1792 | 第 97 行 | `DEATH, 8 frames as in the THIRD image: 1 struck; 2 thrown up, the trident flying out of his hands (from here it lies flat on the ground in front of him, apart from his body, the only loose piece allowed); 3-4 tumbling in the air (at most about 10 squares above the ground); 5-6 falling; 7-8 lying flat on his belly on the ground line, the fin-ears spread. Frames 7-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移；E 倒立上下翻转、Q 翻跟头按四分之一圈转），两只眼睛都在、同一行；
- [ ] 亮绿 `#20AE56` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 三叉戟每帧都在（死亡第 2 帧起躺在地上），杆 1 格深红加上下描边、不断开，长度照造型图；
- [ ] 手至少 2×2 格、手臂至少 3 格粗；每帧整个人连成一块（死亡里地上的三叉戟除外）；
- [ ] 脚底线以下没有任何像素（只有死亡趴倒的帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替、颜色和待机一样，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `fizz_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、亮绿只在眼睛上、每帧连成一块、三叉戟完整、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头；每帧量眼睛到喉咙的行数，和造型图（4）对照，做成表再给用户看。
- 放进 `assets/source/native/`，`fizz_cells.json` 用包里这份，`fizz_idle.png` 用包里已做好的那张。
- `import_native.py --hero fizz`：ORDER 待机一张图 + BOB 呼吸（分界线选在小腿，不切过尾巴和脚），EYES = `#20AE56`，补描边（COMPLETE），NECK，走路 STEP 起伏（照英雄联盟落脚那帧最低、之后最高，约 2 格）。
- 按出手帧核对技能数据的时机（普攻 tick 8、海石三叉戟 tick 16、E 砸地 tick 42、R 甩鱼 tick 7），量特效挂点和头像截取点、选人卡片 banpick_center，重跑模拟，做预览 GIF。
