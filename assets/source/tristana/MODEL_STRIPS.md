# 崔丝塔娜：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选的是你按游戏尺寸画的 **A 版**（护目镜筒高）：`design/tristana_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799；护目镜顶到脚底 41 格，56 格宽，26 色；你按用户说的把炮改成了短粗炮）。**造型图就是标准**：护目镜、白发、大耳朵、琥珀色眼睛、衣服、短粗大炮、颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`tristana_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/tristana_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **两处和参考图不一样，以造型图为准**：① 炮是造型图里的**短粗炮**，英雄联盟的炮更长更细，不要照参考图画长；② 英雄联盟的 W 在空中翻跟头、死亡时倒栽葱，我们的头是贴上去的，**最多整体转 90 度，不画倒立**（具体见表里的 W 和死亡）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/tristana_palette.png`，或直接读 `design/tristana_design_1x.png`）。**先把眼睛的琥珀色 `#F6BA30` 从色板里去掉**（它和铜箍、护目镜的铜边很近，一吸附就会跑到别处），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/tristana_head_1x.png`：两只护目镜筒和皮带、白发、两只大耳朵和耳环、脸、眼睛、嘴；在 128×128 画布上的范围 x 40–79、y 58–76）原样贴进每一帧头的位置（只平移；身体倾斜时整体倾斜，最多转 90 度）。这样每帧的脸都和造型图一模一样。受击第 1 帧把两只眼睛改成闭眼（眼睛那两行各一段深色短线）；死亡第 2–4 帧可以把嘴改成张开（一格深红变两格）。
5. 对位：每帧按 `tristana_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/tristana_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/tristana_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/tristana_head.png`、`_1x.png` | 要贴进每一帧的头（护目镜、白发、耳朵、脸，不含身体和炮） | 贴头 |
| `design/tristana_palette.png` | 造型图的全部 26 色（暗到亮） | 色板 |
| `tristana_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/tristana_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体和炮的动作 |
| `guide/tristana_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `tristana_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/tristana_picture.png` | 造型来源的原画 B（长相参考；比例和炮以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ranged.png` | 团战经理2 原版射手，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（护目镜顶到脚底 41 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 26 种颜色**，不加新颜色；明暗照定稿（亮边、金属高光、铜箍的 X 纹跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **身体粗细照定稿**：手臂至少 3 格宽（加描边），不能只有 1–2 格（在小尺寸下会像手脱离了身体）；腿短、站得开；各部分之间有描边隔开，但身体、手臂、大炮必须连成一个整体，不能有飘在空中的碎块（死亡里掉在地上的炮除外）。
- **头每帧都是造型图的头**（护目镜、白发、大耳朵、耳环、脸、眼睛、嘴逐格一样），只平移或整体倾斜（最多 90 度）；两只眼睛一样大、同一行，琥珀色 `#F6BA30` 只用在眼睛上。
- **大炮每帧都在两只手里**（死亡第 1 帧飞出手之前）：远侧的手（图里右边，棕色大手套）握在炮身上面的钢把手上，近侧的手（左边，红色袖口）在腰后握着炮尾；炮是造型图的**短粗炮**（钢蓝八角炮口、两道刻 X 的铜箍、钢蓝炮尾），不要画成参考图里那么长；炮不能飘开，不能挡脸。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），炮尾也在它上面。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交替（前 4 帧一步、后 4 帧另一步，中间膝盖交错）；上下起伏最多 2 格；首尾能无缝接上。
- 3/4 正面朝右，**不画背影、不画倒立**（死亡最后倒地的帧是躺着，不算）。**只画角色**：炮弹、炸弹、火箭尾焰、爆炸、烟、落地的尘土都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/tristana_design.png`，第二张 `now/tristana_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `tristana_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, goggles, hair, ears, face, cannon and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same chibi yordle proportions, the same goggles, white hair, huge pink-lined ears, olive vest and shorts, quilted brown leather sleeves and leg wraps, red cuff and pouches, the same short, thick cannon, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body and the cannon from it, but keep the FIRST image's short, thick cannon (the THIRD image's cannon is longer and thinner), and never draw her upside down (where the original somersaults or falls head first, turn her body and head together at most a quarter turn).
The character: Tristana (a small cheerful yordle gunner: lavender skin, fluffy white hair, huge pointed ears pink inside with a brass ring, two tall red-and-brass goggle cups pushed up on her head, big amber eyes, an olive vest over a tan shirt, olive shorts, quilted brown leather sleeves and leg wraps, a red cuff, bare lavender feet; a short, thick bronze cannon with two X-engraved brass bands, a steel-blue octagonal muzzle and a steel-blue rear cap, held level at her hip and pointing right).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (41 squares from the top of the goggles to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 26 colors of the FIRST image, no new colors: #191421 #442A23 #283447 #41492D #821D3F #734832 #87602E #445E80 #727745 #D13845 #A36A43 #835B9E #C35C80 #7E879E #C8994E #A3A26B #CE9560 #7397C3 #F6BA30 #B889D1 #E6BF86 #F699B4 #BFCCD8 #DFB4EB #B9DDED #FFF4E4. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its lit edges and metal highlights move with the pose; no dithering, no noise, no random specks added. Arms at least 3 squares wide with the outline, joined to the body; no loose pieces.
The head (the two goggle cups and their strap, the white hair, both huge ears with the brass ring, the face with the eyes and the mouth) is COPIED from the FIRST image in every frame, square for square, and only moved (or turned as a whole with the body, at most a quarter turn); never redraw it, or it flickers when the frames play. Her eyes are the FIRST image's eyes (a dark lash row over each eye, then a white catch-light and a dark pupil, then two amber squares), both the same size on the same rows, never merged into a bar; the amber #F6BA30 appears ONLY in the eyes. The cannon is in her hands in EVERY frame (until it flies out of them in the death): the far hand (the brown glove, on the right of the image) on the steel handle on top of the cannon, the near hand (the red cuff, on the left) holding the rear end at her hip - whatever the THIRD image shows. It is the FIRST image's SHORT, THICK cannon with the steel-blue octagonal muzzle; it moves with her hands, never floats free, and never covers her face.
Feet line: in every cell the lowest row of her feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the cannon - because the game draws the health bar there (only the lying frames of the death may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in tristana_cells.json). In the move loop her head keeps the same horizontal place relative to the standing point in every frame and the legs alternate.
3/4 FRONT view facing right, never her back, never upside down. Do not draw effects (cannonballs, the charge, rocket fire, explosions, smoke, dust) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, level and the same size, the amber only in the eyes, the short thick cannon in both hands in every frame, arms at least 3 squares wide, no loose pieces, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `tristana_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `tristana_run.png`（移动） | 8 帧：117 117 117 117 117 117 117 114 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of League's run (0.93 s cycle, 8 x 117 ms, the SECOND and THIRD images): Tristana's bouncy little run, the cannon held level at her hip pointing right in both hands exactly as in the FIRST image; the body bobs up and down with the hops (at most 2 squares); the legs ALTERNATE as in the THIRD image (frames 1-4 one stride, 5-8 the other: the near leg forward in one half, the far leg in the other, the knees passing each other in between); the ears and the white hair bounce a little; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `tristana_attack.png`（普攻） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, 6 frames (League's attack1): 1 she braces, the cannon level at her hip; 2 she leans in and aims, the muzzle pointing right; 3 THE RELEASE (the cannonball leaves the muzzle here): she yanks the top handle with her far hand, a small kick at the muzzle; 4 the recoil: the cannon kicks back and turns a little toward the viewer, the muzzle lower, her body pushed back; 5 recovering, the cannon coming level again; 6 back to the idle stance. The cannonball and the muzzle flash are effects - do not draw them.` |
| `tristana_skill.png`（E 爆炸火花（+Q）） | 5 × 60 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536，最后 1 格空 | 第 81 行 | `EXPLOSIVE CHARGE, 5 frames (League's spell3): 1 she tips the cannon's muzzle down toward the ground in front of her; 2 the cannon pointing down and forward at about 45 degrees, both hands on it, her weight forward; 3 THE RELEASE (the charge leaves the muzzle here, down and forward to the right): a small kick; 4 held, the muzzle still down; 5 back toward the idle stance. The charge is an effect - do not draw it.` |
| `tristana_skill2.png`（W 火箭跳跃） | 7 帧：60 60 60 70 70 80 133 | 第 6 帧（tick 19），落地 | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `ROCKET JUMP, 7 frames (League's spell2: the game moves her across the ground while frames 4-5 play; draw the jump in place, over the standing point): 1 she crouches, the cannon swinging down behind her; 2 crouched lower, the muzzle pointing down at the ground behind her; 3 she blasts off (the cannon fires down and pushes her up): her feet leave the ground; 4 high in the air, tumbling forward: her whole body (head, body and cannon together) turned a QUARTER turn forward, head to the right; 5 still high, coming back upright, tilted about 45 degrees; 6 THE LANDING: she lands in a deep crouch on the feet line, the cannon held up behind her; 7 back to the idle stance. In frames 4-5 her lowest pixel is 10-14 squares above the feet line (the SECOND image shows the height); never upside down. The rocket blast and the landing dust are effects - do not draw them.` |
| `tristana_ult.png`（R 毁灭射击） | 7 帧：70 70 90 90 100 110 137 | 第 3 帧（tick 8） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `BUSTER SHOT, 7 frames (League's spell4): 1 she hops and swings the cannon up; 2 she lands braced, the cannon swinging down level; 3 THE RELEASE (the huge cannonball leaves here): the cannon level at her hip, pointing right, both hands on it, legs wide; 4 the big recoil: she is pushed back, the muzzle kicks up; 5 the recoil flips the cannon up over her shoulder; 6 the cannon held up high, the muzzle pointing up; 7 back toward the idle stance. The cannonball, the muzzle blast and the smoke are effects - do not draw them.` |
| `tristana_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, eyes squeezed shut (a short dark line on each eye's rows), the cannon still in her hands; 2 recovering toward the idle stance.` |
| `tristana_dead.png`（死亡） | 8 帧：100 100 110 110 120 130 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames, as in the THIRD image: 1 struck, thrown back, the cannon flying out of her hands; 2-4 blown up into the air, arms and legs flailing, mouth open; 5 turning a quarter over as she falls; 6 falling, tilted head first (at most a quarter turn past lying flat, never upside down); 7 landed on her back on the ground line; 8 lying still. From frame 2 the cannon lies on the ground behind her (to the left), level, in the same place in every frame. Frames 7-8 lie on the feet line and may reach 2 squares below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移或整体转，最多 90 度），两只眼睛都在、一样大、同一高度；
- [ ] 琥珀色 `#F6BA30` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 短粗炮每帧都在两只手里（死亡第 2 帧起躺在地上），不挡脸；手臂至少 3 格宽，没有飘着的碎块；
- [ ] 没有背影、没有倒立；脚底线以下没有任何像素（只有死亡倒地的帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交替，上下起伏不超过 2 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧（W 第 6 帧是落地）；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `tristana_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、琥珀色只在眼睛上、连通块、手臂粗细、每帧面积和待机比、跑步两腿交替），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`tristana_cells.json` 用包里这份，`tristana_idle.png` 用包里已做好的那张。
- `import_native.py --hero tristana`：ORDER 待机一张图 + BOB 呼吸，EYES = `#F6BA30`（按眼睛对齐待机和移动），COMPLETE 补描边，头是贴的：NECK 检查肩膀每帧在下巴下同一行。
- 按出手帧核对技能数据的时机（普攻 tick 7、E tick 7、W 落地 tick 19、R tick 8），量特效挂点（炮口高度）和头像截取点，重跑模拟，做预览 GIF。
