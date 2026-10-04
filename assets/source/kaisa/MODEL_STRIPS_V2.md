# 卡莎：第二版造型的动作帧（给 Codex 的提示词）

> **为什么重画**：用户说卡莎「身宽体胖 脸大」。新造型已经定了：`design/kaisa_design.png` —— 你画的 v2 草稿 **A**（52 格）按第一版 B44 的办法整行整列删到 42 格（用户选的「42 格」）：小脸、可爱的眼睛和小嘴、头后两只金边品红的翼状肩炮、带品红宝石的圆金肩甲和胸口宝石、深色紧身衣上的金色护甲片、带品红爪子的护手、金片护甲的细长腿和金底靴子。站着 **42 格高、25 格宽**，33 色。**造型图就是标准**。
> **你上一轮交的卡莎动作作废**：它建在我上次压坏的 42 格读图上（脸、肩甲、手都糊了），用户看了说「各种模型丢失 走路怪异 模型异常」。这一轮请全部照这张新造型重画。
> - **待机条已经做好**（`kaisa_idle.png`，每帧就是造型图），不用画。其余 7 张动作图按下面的表重画（R 的起跳和冲刺是一张 4 帧的图，第 4 帧是飞行姿势）。
> - **动作照第一版的动作条**（`old/kaisa_old_<动作>.png`，第一版的胖身体、大脸，用户都看过、认可了这些动作和节奏，跑步是用户定稿的 v13）；帧数、每帧时长、出手帧、站位照 `now/kaisa_now_<动作>.png`（英雄联盟原版按游戏尺寸取色）；身体怎么动看 `pose/lol_pose_<动作>.png`（同一帧的渲染；它是第一版的比例，**比例以造型图为准**）。**头、身体、手臂、腿、肩炮照新造型**。
> - **腿（用户定的规矩）**：站着放技能、受击、普攻的每一帧，**腿就是待机的腿**——同样直、同样宽、同样的位置，靴子平踩在脚底线上；不要岔开成大弓步、不要蹲、不要外八字、不要一条腿斜着（卡莎第一版就因为这个返工过：「待机时的腿部更好」）。只有 R 的起跳/落地蹲下（腿还是待机的腿弯下来，一样粗、一样颜色），死亡最后跪倒、趴下。
> - 交回的图每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`、`manifest.json`（每帧的格子矩形、站位点、bbox），打包成 `kaisa_strips_v2_done.zip` 放在 outputs 里（`outputs/kaisa-strips-v2/`），HANDOFF.md 最后写。

## 建议流程（每一张动作条）

1. 生图：附图顺序见通用提示词（造型图、now 条、lol_pose、第一版的动作条）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/kaisa_palette.png`）。**先把眼睛的两种颜色 #FDFCFC、#FDFCFD、#8B17B2、#7B0D9F 从色板里去掉**，它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/kaisa_head_1x.png` 里不透明的格子：深紫头发、脸、眼睛；不含肩炮；在 128×128 画布上的范围 x 59–70、y 63–77，按图里的形状贴）原样贴进每一帧头的位置，只平移；**贴之前先把你自己画的头整个擦掉**，头周围 3 格内不能留下你自己的脸或头发的碎块；肩炮和长发下半截跟着身体画。受击第 1 帧把眼睛改成闭眼。
5. **站着的帧贴待机的腿**：把造型图从胯下到靴底的两条腿（`design/kaisa_legs_1x.png`）原样贴回每一个站着的帧（普攻、Q、W、受击、R 落地第 3–4 帧、死亡第 1 帧），只左右平移，靴底踩在脚底线上。
6. 对位：每帧按 `kaisa_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/kaisa_design.png` | **新造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，靴底第 99 行 | 每张的第一张附图 |
| `design/kaisa_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头、贴腿 |
| `design/kaisa_head.png`、`_1x.png` | 只有头（头发、脸、眼睛，不含肩炮），在画布上原来的位置 | 贴头 |
| `design/kaisa_legs.png`、`_1x.png` | 只有两条腿（胯下到靴底），在画布上原来的位置 | 站着的帧贴腿 |
| `design/kaisa_palette.png` | 造型图的全部 33 色（暗到亮） | 色板 |
| `kaisa_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/kaisa_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的渲染（第一版的比例），同样的格子 | 第三张附图：手臂、肩炮和身体的动作 |
| `old/kaisa_old_<动作>.png` | **第一版造型的动作条（用户认可的动作）**，同样的格子 | 第四张附图：照它的姿势和节奏（身体换成新造型、腿换成待机的腿） |
| `guide/kaisa_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `kaisa_cells.json` | 每帧的站位点（格子里第几列、第几行）和帧时长 | 整理对位 |
| `refs/kaisa_design_A_master.png` | 你画的 v2 草稿 A 原图（新造型的来源） | 需要时参考画法 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（肩炮尖到靴底 42 格），每个像素一个 8×8 方块，同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 33 种颜色**，大块纯色，不要抖动、噪点、零散的碎点；外轮廓 1 格近黑描边，里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（小脸、深紫长发，逐格一样，只平移）；眼睛的两种颜色 #FDFCFC、#FDFCFD、#8B17B2、#7B0D9F 只用在眼睛上。
- **身体照造型图（瘦）**：细腰、细胳膊、细长的腿、金色靴子；不要画回第一版的大脸、宽身体、粗腿。
- **手臂和手**：手臂和造型图一样细，连着肩膀；手肘自然弯曲，不要伸成笔直的细棍；手是带品红爪子的护手，连着手臂，不能是 1 格的黑棍或飘着的手。
- **肩炮每帧都在头后**，和造型图一样大（Q 张开时更宽，但还是同样的颜色和画法），连着背，不能断开或飘开。
- **腿（用户定的规矩）**：站着的每一帧腿就是待机的腿；只有表里写了的帧才蹲下或跪下；跑步两腿交替；死亡最后跪倒趴下。
- 每帧整个人连成一块，没有飘着的碎块，手臂和身体之间不要留透底的小洞。
- **脚底线以下什么都不能有**（游戏在脚下画血条），只有死亡最后两帧可以低 1–2 格。
- **移动循环**：两条腿交替、前后交叉，两只鞋最多相距 10 格，两条腿颜色一样；头相对站位点的横向位置每帧一样，上下起伏最多 1 格；首尾能接上。
- 3/4 正面朝右，看得到脸；出招朝图的右边；不画背影、不画倒立。**只画角色**：电浆弹、导弹、光束、拖尾、发光都是单独的特效，不要画。每个动作开始和结束都接近待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，不要品红：会吃掉她的品红光）。不要网格线、边框、文字、编号、参考线。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附四张图：`design/kaisa_design.png`、`now/kaisa_now_<动作>.png`、`pose/lol_pose_<动作>.png`、`old/kaisa_old_<动作>.png`。输出 `kaisa_<动作>.png`。

```text
Four attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, small face, slim body, thin arms, long slim legs, boots and wing-pods exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames in the same grid - the motion of the arms, the pods and the upper body. FOURTH: the previous, approved version of these frames drawn on an older body with a bigger head and a wider body - copy its poses, gestures and timing, but draw the FIRST image's small head, slim body and long slim legs instead.
The character: a chibi young woman in a living alien battle-suit: long dark purple hair falling behind her back, a small pale face with violet eyes and a small pink mouth; two tall WING-PODS raised behind her head (gold rims, magenta insides); round gold shoulder plates with magenta gems, a magenta gem on the chest, a dark slate bodysuit with gold armour plates and glowing magenta lines; dark gauntlets with bright magenta claws; long slim legs in violet armour with gold plates and gold-soled boots. She has no weapon in her hands: she fires from her palms, her forearm and the pods.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (42 squares from the pods' tips to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 33 colors of the FIRST image, no new colors: #0F0715 #14011B #17011E #300739 #271A43 #440F52 #2F2952 #342C62 #561F67 #651A68 #4B3675 #484D78 #7B0D9F #722A8C #8F1089 #9D346A #8B17B2 #5A6299 #A97F3C #B50EB1 #D69732 #8C8A95 #EE777C #F7CA4E #FB2CFB #FCD685 #FBBCA5 #FDDBCD #FCDDCD #FDDFD2 #FEE4D3 #FDFCFC #FDFCFD. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no random specks.
Arms and hands: the arms as thin as in the FIRST image, joined to the shoulders, the elbows bent naturally - never a straight stick; the clawed gauntlets joined to the arms - never 1-square black sticks or floating hands.
LEGS (the art director's rule): in every STANDING frame (the attack, the spells, the hit, standing up after the landing) her legs are the FIRST image's legs exactly: straight, the same width apart, in the same place under her, the boots flat on the feet line - never a wide stance, never crouching, never toes turned out, never one leg slanted. Show the action with the upper body, the arms and the pods. She crouches ONLY in the ult's launch and landing (the FIRST image's legs bent at the knees, the same thickness and colors, both boots flat) and kneels only at the end of the death.
The head (the dark purple hair round the face, the small face and the eyes) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, enlarge, squash or turn it. The eye colors #FDFCFC、#FDFCFD、#8B17B2、#7B0D9F appear ONLY in the eyes. The two wing-pods are in every frame, joined to her back, as big as in the FIRST image (wider when they open in Q, same colors and style).
The whole figure is ONE connected piece in every frame, with no little holes of background walled in between an arm and the body.
Feet line: in every cell the soles' lowest row is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down (only the last two frames of the death may dip 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in kaisa_cells.json). In the move loop her head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate and cross, both in the FIRST image's leg colors.
3/4 front view facing right like the FIRST image; every shot and dash goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (plasma bolts, missiles, beams, trails, glows) - only the character. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `kaisa_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `kaisa_run.png`（移动（跑步，两腿交替）） | 8 × 116 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop (8 x 116 ms; the FOURTH image's run on the FIRST image's slim body): she runs forward leaning a little, the clawed hands swinging against the legs with the elbows bent; the two wing-pods stay raised behind her head as in the FIRST image and ride with her upper body; the long slim legs ALTERNATE - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames, the boots at most 10 squares apart, the planted boot flat on the feet line; the long hair swings a little behind her; her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); both legs in the FIRST image's leg colours; frame 8 flows into frame 1.` |
| `kaisa_attack.png`（普攻（手掌电浆弹）） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, a plasma shot from her NEAR hand, 6 frames (the FOURTH image's motion): 1 the near arm drawing back; 2 the near arm cocked at her side; 3 THE SHOT (the plasma bolt leaves here): she thrusts the near hand forward to the right at the height of her belly, the palm out, the elbow a little bent; 4 the arm still out; 5 drawing it back; 6 back toward the idle. On the FIRST image's legs in every frame; the pods stay raised.` |
| `kaisa_skill.png`（Q 艾卡西亚暴雨（肩炮张开）） | 6 帧：70 70 80 80 100 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2304×1536 | 第 81 行 | `ICATHIAN RAIN, 6 frames (the FOURTH image's motion): 1 the pods start to open; 2 the pods swing open like wings, up and outward, their magenta bays glowing; 3 THE LAUNCH (the missiles leave here): the pods fully spread, flared up and outward, her arms thrown back a little; 4 still spread; 5 the pods folding back to the FIRST image's raised pose; 6 back toward the idle. The opened pods (2-5) are wider than in the FIRST image but in its colours and style (gold rims, magenta insides, dark violet shells) and stay joined to her back. On the FIRST image's legs in every frame. Draw NO missiles.` |
| `kaisa_skill2.png`（W 虚空索敌（前臂炮）） | 7 帧：80 90 100 110 80 70 70 | 第 5 帧（tick 23） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `VOID SEEKER, 7 frames (the FOURTH image's motion): 1 the near arm drawn back; 2 its forearm armour folding open into a cannon (dark violet and gold with magenta glow) along the forearm; 3 aiming: the cannon arm stretched forward to the right, level at chest height; 4 charging, the cannon's magenta glow brightens; 5 THE SHOT (the void blast leaves here): the recoil pushes her arm up 1 square and the pods flare open; 6 recovering, the cannon folding away; 7 back toward the idle. On the FIRST image's legs in every frame. Draw NO beam or blast.` |
| `kaisa_ult.png`（R 猎手本能·起跳和冲刺（第 4 帧是飞行姿势）） | 4 帧：60 60 60 600 | 第 3 帧（tick 7） | 4 列 × 1 行，3072×768 | 第 81 行 | `KILLER INSTINCT, the launch and the dash, 4 frames (the FOURTH image's motion): 1 she crouches, the knees bent, both boots flat on the ground, the pods raised high; 2 she coils forward; 3 THE LAUNCH: she springs forward to the right, the body leaning low; 4 THE DASH (held while she flies to the target): the body almost horizontal, flying to the right, the clawed hands forward, the pods swept back, the hair streaming back - keep it inside its cell and above the feet line. The crouching legs are the FIRST image's legs bent (same thickness and colours). Draw NO trail.` |
| `kaisa_ult_land.png`（R 猎手本能·落地） | 4 × 60 | — | 4 列 × 1 行，3072×768 | 第 81 行 | `KILLER INSTINCT, the landing, 4 frames (the FOURTH image's motion): 1 landing in a crouch, the knees bent, both boots flat on the ground, a clawed hand near the ground, the pods spread; 2 still crouched, rising a little; 3 rising onto the FIRST image's legs; 4 back to the idle.` |
| `kaisa_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, the head and shoulders pushed back 1 square, the eyes squeezed shut (two short dark lines on the eyes' row), the pods jolted with her back - the legs stay the FIRST image's legs; 2 recovering toward the idle.` |
| `kaisa_dead.png`（死亡） | 8 帧：100 100 110 110 120 130 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames (the FOURTH image's motion): 1 struck, she reels back, the pods flaring up (on the FIRST image's legs); 2-3 she twists and sags, the pods drooping; 4-5 she sinks; 6 she falls to her knees; 7-8 kneeling and slumped forward on the ground, the pods folded down over her back like a closed shell, their magenta dimmed. Frames 7-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；只用造型图色板里的颜色；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），头周围 3 格内没有你自己画的头的碎块；两只眼睛都在、同一行；眼睛的两种颜色只在眼睛上；
- [ ] **站着的帧腿就是待机的腿**；只有 R 起跳/落地蹲下、死亡最后跪倒趴下；
- [ ] 身体是新造型的瘦身体、小脸；手臂细、手肘自然弯；手是带爪的护手；
- [ ] 肩炮每帧都在、连着背；每帧整个人连成一块，没有透底的小洞；脚底线以下没有像素（死亡最后两帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替、前后交叉，两只鞋最多相距 10 格，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；没有背影、没有倒立；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `kaisa_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛颜色只在眼睛上、连通块、站着的帧腿和待机一样、肩炮大小），不对的帧换回造型图的头和腿。
- R 的 4 帧拆成 `kaisa_ult.png`（1–3）和 `kaisa_ult_dash.png`（4），放进 `assets/source/native/`；`import_native.py --hero kaisa`。
- 量特效挂点（手掌、W 炮口、Q 两只肩炮的位置）、头像截取点和 banpick_center，做预览 GIF。
