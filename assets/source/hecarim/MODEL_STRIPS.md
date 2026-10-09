# 赫卡里姆：照英雄联盟原版动作画动作帧（第 2 步，给 Codex 的提示词）

## 这一步做什么

造型定稿了（`design/hecarim_design.png`，用户从 oppi 画法的第二版里挑的 2_45）。这一步照英雄联盟原版赫卡里姆的动作，按游戏尺寸画出全部动作条：跑步、普攻、Q、E 冲锋、E 落地一击、R、受击、死亡。

**做法（卡尔玛那一轮用户通过的做法）：**

- **每一帧把整个半人马一起画**：头盔、新月角、护肩、上身、两只手臂、戟、马身、四条腿、前襟、尾巴在同一个姿势里一起画出来，头盔永远长在肩膀中间、跟着身体动——前冲时跟着肩膀往前，人立时跟着上身往后上方立起，倒地时跟着身体倒下。**不要先放一个固定的头再在下面画身体，不要贴头。**
- **长相、比例、颜色照造型图**（头盔小，夹在两个大护肩中间；暗色分层的黑甲；青绿鬼火只在眼睛、牙、胸口大嘴、马胸骷髅甲、裂纹和尾巴；酒红前襟；戟刃最亮），**动作照英雄联盟**：`zoom/lol_zoom_<动作>.png`（原版每帧放大、编号，看动作最清楚）、`now/hecarim_now_<动作>.png`（原版按游戏尺寸取色，看帧数、大小和站位）、`pose/lol_pose_<动作>.png`（原版高清，和 now 同格子同位置）。下面每帧都写了四条腿、胯、上身、手和戟怎么动。`refs/design_vs_league.png` 是造型图和英雄联盟模型并排。
- **四条腿是真正的疾驰**（跑步、E、R 冲锋）：每条腿在前面落地、着地时往后蹬、抬起折叠（蹄子收到肚子下面）、再向前摆；两条前腿交替、两条后腿交替，后腿比前腿晚半步——**不要四条腿一起动，不要画成直棍**。原版疾驰一步 0.68 秒，8 帧 × 85 毫秒。
- 待机不用画（`hecarim_idle.png` 已做好，游戏里的待机动画由我们的工具生成；它也告诉你造型图在格子里多大、站在哪里）。

## 造型图（每一帧都照它）

定稿 `design/hecarim_design.png`（放大 8 倍，1024×1024）：新月角尖到马蹄 45 行，66 格宽（连戟和尾巴），16 色；马蹄底在第 99 行，马身中间在第 64 列。

- **头**：新月角 6 行；头盔小（约 9 行高、10 格宽），深色骷髅面甲上**两只眼睛各 1 格**青绿、下面一行青绿牙；两侧是大护肩的高尖刺。
- **上身**：大护肩、胸甲，胸口一张青绿锯齿大嘴；两只手握戟。
- **戟**：长杆，右上方是银色带钩的戟刃，铜色护手。
- **马身**：黑甲马铠，马胸两块骷髅甲（青绿眼睛），青绿裂纹；酒红前襟挂在前面；左边一条长长的青绿幽灵火尾巴。
- **四条腿**：粗壮的披甲马腿，大马蹄；近的两条（画在前面）亮一点，远的两条（画在后面）暗一级。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/hecarim_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图：长相、比例、颜色 |
| `design/hecarim_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板 |
| `design/hecarim_head.png`、`_1x.png` | 造型图的头盔和新月角，**只是给你看头该画成什么样**，不要贴 | 画头时对照 |
| `design/hecarim_palette.png` | 造型图的全部 16 色（暗到亮） | 色板 |
| `now/hecarim_now_<动作>.png` | 英雄联盟原版按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、每格位置、人物大小 |
| `zoom/lol_zoom_<动作>.png` | 原版每帧放大、编号（红线 = 脚底线，蓝线 = 站位点） | 第三张附图：**动作照这张** |
| `pose/lol_pose_<动作>.png` | 原版高清，和 now 同格子、同位置 | 需要时核对位置 |
| `guide/hecarim_guide_<动作>.png` | 格子边框、站位点（蓝十字）、脚底线（红线）和线下禁区、**英雄联盟每帧头的位置（绿圈）**、帧号 | 对位用，不要画进图里 |
| `hecarim_cells.json` | 每帧站位点 `pivot`、头的位置 `head`（格子里第几列、第几行，单位方块）、帧时长 | 整理对位 |
| `hecarim_idle.png` | 已做好的待机条 | 不用画；看大小和站位 |
| `refs/design_vs_league.png` | 造型图和英雄联盟模型并排 | 部件对应 |
| `refs/hecarim_picture.png` | 用户选的原画 A | 长相参考（以造型图为准） |

## 规则（每张都一样）

- **整个半人马一起画，头跟着身体动**（见上）。每帧的头在 `guide/` 绿圈附近（英雄联盟的头在那里）。
- **动作照英雄联盟**：四条腿怎么迈、胯怎么沉、马身怎么前倾和人立、骑士怎么后仰和前冲、手和戟到哪里、尾巴怎么飘，照 `zoom/` 和下面的逐帧说明。
- **长相、比例照造型图**：站着时和造型图一样高（角尖到马蹄 45 格），头盔一样小，马身一样长，腿一样粗；戟每帧都在（死亡按表）。
- 像素：每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明；**只用造型图的 16 种颜色**；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要零散的黑格、不要噪点。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：站着的蹄子落在脚底线上，戟刃砸地也只到脚底线。
- 一直是马身朝右、骑士胸口朝向观众（和造型图一样）；出招、冲锋朝图的右边；**不画背影、不倒立**。
- **只画角色**：刀光、旋风、幽灵骑兵、冲锋的烟尘都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/hecarim_design.png`，第二张 `now/hecarim_now_<动作>.png`，第三张 `zoom/lol_zoom_<动作>.png`。`[animation]` 在下面每张动作图的说明里，`[R]`、`[grid]`、`[size]` 按表。输出文件名 `hecarim_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - his exact look, proportions, colors and pixel style; do not redesign anything. SECOND: the same animation from League of Legends sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, the layout, the size of the figure and where he stands in each cell, not its blurry look. THIRD: the same League frames rendered large and numbered - copy the MOTION from it: how the four legs gallop, plant, fold, rear and kick, how the horse body pitches and rears, how the rider leans and lunges, where the hands and the glaive go, how the tail streams.
The character: a spectral centaur knight - an armoured knight's upper body on an armoured war-horse body, black plate shaded in dark greys; a SMALL closed helm with a crescent horn, set low between two big spiked pauldrons, a dark skull visor with two single glowing teal eye squares and a row of teal teeth; a glowing teal fanged grin on the breastplate; a long glaive with a hooked silver blade and a copper guard, held in both hands; two skull plates with teal eyes on the horse's chest, teal cracks; a maroon tabard in front; a long teal ghost-flame tail at the back (the left of the image); four thick armoured legs with big dark hooves.
Task: redraw every frame as clean game-size pixel art of the FIRST image's character doing the THIRD image's motion. Draw the WHOLE centaur at once in each frame - the helm, the horn, the pauldrons, the torso, both arms, the glaive, the horse body, all four legs, the tabard and the tail together in one pose - so the helm always sits between the pauldrons and moves with the body: forward in a lunge, up and back when he rears, down when he falls. Never paste one fixed head and draw a body under it. The helm is drawn like the FIRST image's helm in every frame (the same small size, the horn, the two single eye squares, the teeth), only moved with the body.
Motion like League: the legs, the horse body and the rider move as in the THIRD image; in every gallop each leg plants ahead, sweeps back on the ground, lifts and folds with the hoof tucked under the belly and swings forward again, the front pair and the hind pair each alternating, the hind pair half a stride after the front pair - never all four legs moving together, never stiff sticks; never a stiff standing figure with only the arms moving.
Proportions from the FIRST image, only the pose changes: standing he is exactly as tall as the FIRST image (45 squares from the horn tip to the hooves); the same small helm; the horse body as long and the legs as thick as in the FIRST image; the near legs a shade lighter than the far legs; the glaive in every frame (the death: as described).
Pixel rules (most important): every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. ONLY the 16 colors of the FIRST image, no new colors: #000000 #282828 #3C1428 #005A5A #3C3C3C #642828 #505050 #148C82 #646464 #786464 #787878 #28C8B4 #C8A078 #50F0DC #B4C8C8 #F0F0F0. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it; no stray black squares, no dithering, no noise, no random specks.
Feet line: in every cell the standing hooves are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image.
The horse body facing right and the rider's chest toward the viewer like the FIRST image; every strike and charge goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash trails, the spin, the spectral riders, dust) - only the character.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 120x100 squares (960x800 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid; only the FIRST image's colors; the whole centaur drawn together, the small helm between the pauldrons in every frame; the four legs galloping like the THIRD image (not frozen, not moving together); the glaive, the tail and the tabard in every frame; as tall and as long as the FIRST image; no loose pieces, no stray black squares; nothing below the feet line; never his back or upside down; the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准时用；图1 = now 条，图2 = 造型图，图3 = zoom 原版放大）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色；动作看图3（同一组动作的高清放大，编号和图1的帧一一对应）。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块；站着时人物和图2一样高，不能变大也不能变小。
2. 保留每一帧的全身动作：四条马腿怎么疾驰（前面落地、往后蹬、抬起折叠、再向前摆，前后两对腿交替）、马身怎么前倾和人立，骑士怎么后仰和前冲，手和戟到哪里，尾巴怎么飘，都照图1和图3。
3. 整个半人马一起画：头盔、护肩、上身、戟、马身、四条腿、前襟、尾巴在同一个姿势里，头盔跟着身体一起动；不要贴一个固定的头。
4. 长相、比例、配色、细节全部换成图2：小头盔加新月角、骷髅面甲上两只单格青绿眼睛和一行青绿牙、大护肩高尖刺、胸口青绿锯齿大嘴、黑色分层盔甲、马胸两块骷髅甲、青绿裂纹、酒红前襟、左边长长的青绿幽灵火尾巴、银色戟刃铜色护手；头盔每帧和图2一样小。
5. 一直是马身朝右、骑士胸口朝向观众；出招和冲锋朝右；不画特效。
6. 动作：[animation]
背景保持纯品红 #FF00FF，方便抠图。风格保持与图2一致。重点在于精准复刻图1和图3的"动作骨架"，只是换了"皮囊"。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 |
|---|---|---|---|---|
| `hecarim_run.png`（跑步（疾驰）） | 8 × 85 | — | 4 列 × 2 行，3840×1600 | 第 89 行 |
| `hecarim_attack.png`（普攻（举戟过头、向前下劈）） | 6 帧：60 60 70 70 70 80 | 第 4 帧（tick 11） | 3 列 × 2 行，2880×1600 | 第 89 行 |
| `hecarim_skill.png`（Q 暴走（拉开、横扫一圈、扬起）） | 7 帧：50 50 55 55 60 60 70 | 第 4 帧（tick 9） | 4 列 × 2 行，3840×1600，最后 1 格空 | 第 89 行 |
| `hecarim_skill2.png`（E 毁灭冲锋（压低戟疾驰）） | 7 帧：60 75 75 75 75 75 75 | — | 4 列 × 2 行，3840×1600，最后 1 格空 | 第 89 行 |
| `hecarim_skill2_hit.png`（E 落地一击（前腿扬起、举戟砸下）） | 4 帧：50 50 60 70 | 第 3 帧（tick 6） | 4 列 × 1 行，3840×800 | 第 89 行 |
| `hecarim_ult.png`（R 暗影冲击（人立举戟、平端戟冲锋）） | 7 帧：50 60 60 80 80 80 90 | 第 3 帧（tick 7） | 4 列 × 2 行，3840×1600，最后 1 格空 | 第 89 行 |
| `hecarim_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1920×800 | 第 89 行 |
| `hecarim_dead.png`（死亡（人立、扭身、侧倒）） | 8 帧：100 100 100 120 150 150 200 500 | — | 4 列 × 2 行，3840×1600 | 第 89 行 |

## 逐帧动作（照英雄联盟；左右 = 图里的左右，他朝右；"近" = 靠观众、画在前面的腿，"远" = 画在后面的腿）

### `hecarim_run.png` 跑步（疾驰）

1. 近前蹄踩在胸下（站位点右 14 格），远前蹄向前伸出正要落地（右 23 格）；远后蹄踩在胯下（左 10 格），近后蹄向后踢起（左 21 格、抬起 5 格）
2. 两只前蹄都着地往后蹬（远的右 18 格、近的右 7 格）；远后蹄向后蹬到最远（左 17 格、抬起 3 格），近后蹄抬起往前收（左 18 格、抬起 3 格）
3. 远前蹄踩在胸下（右 9 格），近前蹄在它后面抬起（左 4 格、抬起 3 格）；近后蹄落地（左 13 格），远后蹄在后面抬起；**身体最低**
4. 远前蹄往后蹬起（右 2 格），近前蹄高高收起（抬起 6 格）；近后蹄踩地（左 8 格），远后蹄往前摆（左 12 格）
5. **收拢腾空**：四只蹄子都收到肚子下面，前后蹄靠得很近；远前蹄收起 5 格、近前蹄 7 格；身体开始升高
6. 近前蹄向前伸出准备落地（右 10 格、抬起 3 格），远前蹄高高收起（抬起 6 格）；两只后蹄在肚子下面，近后蹄着地；**身体最高**（比第 3 帧高 4 格）
7. 近前蹄落在前面（右 17 格），远前蹄往前摆（右 8 格、抬起 3 格）；远后蹄踩在肚下（0 格），近后蹄往后蹬（左 11 格）
8. 两只前蹄都伸在前面（近的右 19 格踩地，远的右 17 格正落地）；远后蹄着地（左 3 格），近后蹄向后踢起（左 19 格）；身体最低，接回第 1 帧

`[animation]`：

```text
RUN, 8 frames x 85 ms = League's gallop stride (0.68 s), galloping to the right. A real four-legged GALLOP: each leg plants ahead, sweeps back under the body while it is on the ground, lifts and folds (the hoof tucked up under the belly), then swings forward again; the two front legs alternate (near and far a step apart), the two hind legs alternate, the hind pair half a stride after the front pair - never all four legs moving together like one leg, never stiff sticks. The horse body rocks: the chest dips when the front legs land (frames 3 and 8 the lowest), it rises when the hind legs push (frames 5-6 the highest, about 4 squares higher). The rider rides with it: he sits upright and rocks with the horse, the glaive held across the body as in the idle (blade up to the upper right), the tail streams back to the left and flaps. 1 the near front hoof planted under the chest (14 squares right of the standing point), the far front hoof reaching forward to land (23 right); the far hind hoof planted under the hips (10 left), the near hind hoof kicked back (21 left, lifted 5). 2 both front hooves on the ground sweeping back (far 18 right, near 7 right); the far hind pushed back furthest (17 left), the near hind lifted coming forward. 3 the far front planted under the chest (9 right), the near front lifting behind it (4 left, lifted 3); the near hind landing (13 left), the far hind lifted behind; the body at its LOWEST. 4 the far front pushing off (2 right), the near front folded up high (lifted 6); the near hind planted (8 left), the far hind swinging forward (12 left). 5 GATHERED: all four hooves tucked under the belly, the front and hind hooves close together, the front ones lifted 5-7; the body rising. 6 the near front reaching forward to land (10 right, lifted 3), the far front folded high (lifted 6); both hind hooves under the belly, the near hind on the ground; the body at its HIGHEST. 7 the near front planted far forward (17 right), the far front swinging forward (8 right, lifted 3); the far hind planted under the belly, the near hind pushing back (11 left). 8 both front hooves forward (near 19 right planted, far 17 right landing); the far hind on the ground (3 left), the near hind kicked back (19 left); the body low (then frame 1 again).
```

### `hecarim_attack.png` 普攻（举戟过头、向前下劈）

1. 从待机开始：两手握戟往上抬，戟刃从右上方转向上方；身体不动
2. **举戟过头**：两手把戟竖直举到头顶上方（手在头上方 3 格，戟刃朝天），骑士上身微微后仰（头往左 2–3 格）；马站稳
3. **蓄力**：戟横在头顶上方，戟刃在**左边**（身后），戟尾在右边；上身后仰最多（头比待机往左 3 格、高 3 格）；马的前蹄踩稳
4. **劈下（出手帧）**：整个身体向右前方猛冲——骑士头和胸往右 16 格、低 11 格，两手伸到身前胸口以下，戟从上往前下方劈出，戟刃远远落在右前方（离站位点右约 35 格、腰的高度）；马身前倾，**两条后腿向后扬起离地**（抬起 4–5 格），近前蹄踩在前面（右 20 格），远前蹄抬起 **← 出手帧**
5. **收势**：戟继续往下往后扫，扫到身体左后方（戟刃在左边、胸的高度），两手在胸前；身体还低着前倾，后腿还扬着
6. 回到待机：后腿落地，身体抬起，戟回到身前斜握（戟刃右上方）

`[animation]`：

```text
BASIC ATTACK (a glaive chop), 6 frames, League's attack: 1 from the idle, both hands start lifting the glaive, the blade turning from the upper right to straight up. 2 RAISED: both hands hold the glaive straight up above his head (the hands 3 squares above the helm, the blade to the sky), the rider leaning back a little (the head 2-3 squares left); the horse standing firm. 3 WIND-UP: the glaive held level above his head, the blade at the LEFT (behind him), the pommel at the right; leaning back the most (the head 3 left and 3 higher than in the idle). 4 THE CHOP (it hits here): the whole centaur lunges forward to the right - the rider's head and chest 16 squares right and 11 lower, both hands thrust forward below the chest, the glaive chopping down and forward so the blade lands far ahead at the right (about 35 squares right of the standing point, at hip height); the horse pitched forward, the HIND LEGS KICKED UP off the ground behind (lifted 4-5), the near front hoof planted forward (20 right), the far front lifted. 5 follow-through: the glaive sweeps on down and back to his left side (the blade behind at the left, at chest height), the hands in front of the chest; still low and pitched forward, the hind legs still up. 6 back to the idle: the hind legs down, the body rising, the glaive across the body again (blade up-right).
```

### `hecarim_skill.png` Q 暴走（拉开、横扫一圈、扬起）

1. **拉开**：两手把戟往上往后拉，戟刃转到头的左上方；上身后仰（头往左 6 格）
2. **蓄力到底**：戟水平拉到身体**左后方**、头的高度（戟刃在左边离站位点约 16 格），两手在头后面；上身向左扭到底
3. **开始转**：上身往回扭，戟在胸口高度水平扫回来（两手在胸前，戟从身后横扫到身侧）
4. **横扫（出手帧）**：戟在身前**腰的高度画一个又大又平的圆弧**扫到右前方，两手伸到前面（右 24 格）；骑士向右前方倾（头往右 10 格）；马四蹄站稳，远前蹄微抬 **← 出手帧**
5. **扬起**：戟顺势往上扬到右上方（两手一高一低，戟刃在头的右上方），身体抬起
6. 戟继续扬到头顶上方、戟刃指向左后方（举得最高，戟刃比头高 10 格），上身直立后仰
7. 落下：戟收回到身前竖着（戟刃朝上），回到待机

`[animation]`：

```text
RAMPAGE (Q, a spinning glaive sweep), 7 frames, League's Q: 1 DRAWING BACK: both hands pull the glaive up and back, the blade swinging to the upper left of his head; the rider leaning back (the head 6 squares left). 2 FULLY WOUND: the glaive held level far behind him at the LEFT at head height (the blade about 16 squares left of the standing point), the hands behind his head, the torso twisted to the left. 3 UNWINDING: the torso turns back, the glaive sweeping round level at chest height (the hands in front of the chest, the glaive swinging from behind to his side). 4 THE SWEEP (it hits here): the glaive sweeps a WIDE FLAT ARC in front of him at waist height out to the front right, both hands thrust forward (24 squares right); the rider leaning forward to the right (the head 10 right); the horse on all four hooves, the far front hoof lifted a little. 5 RISING: the glaive swings on up to the upper right (the blade above-right of his head), the body rising. 6 the glaive swung on over his head, the blade pointing back to the upper left (the highest: the blade 10 squares above the helm), the rider upright, leaning back. 7 settling: the glaive brought down to stand upright in front of him (blade up), back to the idle.
```

### `hecarim_skill2.png` E 毁灭冲锋（压低戟疾驰）

1. 从待机进入冲锋：戟往前放低，身体前倾，马开始起步
2. **冲锋疾驰**（第 2–7 帧和跑步一样的疾驰步，但更低更快）：**戟像骑枪一样压低**——戟刃在右前方、马胸前面、接近腰下的高度，戟杆斜着贴在马身侧；**空着的那只手向前伸出、五指张开**（在头的右前方）；骑士上身前倾、头往前；近前蹄踩地、远前蹄前伸，后腿向后蹬
3. 前蹄踩在胸下，后蹄向后蹬到最远；身体最低
4. 前蹄往后蹬起，近后蹄落地
5. **收拢**：四只蹄子收到肚子下面；身体升高
6. 近前蹄向前伸出，后蹄在肚子下面；身体最高
7. 前蹄落在前面，后蹄往后蹬；接回第 2 帧

`[animation]`：

```text
DEVASTATING CHARGE (E), 7 frames, League's charge gallop: the same four-legged gallop as the run but lower and faster, with the glaive LOWERED LIKE A LANCE. 1 from the idle into the charge: the glaive lowering forward, the body leaning in, the horse starting off. 2-7 THE CHARGE: the glaive held low and forward like a lance - the blade ahead at the right in front of the horse's chest, below waist height, the shaft slanting along the horse's side; the FREE HAND REACHED FORWARD with the fingers spread like a claw (in front of his helm at the right); the rider leaning forward, the head forward. 2 the near front hoof planted, the far front reaching forward, the hind legs pushing back. 3 the front hooves planted under the chest, the hind hooves pushed back furthest; the body lowest. 4 the front hooves pushing off, the near hind landing. 5 GATHERED: all four hooves tucked under the belly; the body rising. 6 the near front reaching forward, the hind hooves under the belly; the body highest. 7 the front hooves landing ahead, the hind pushing back (then frame 2 again).
```

### `hecarim_skill2_hit.png` E 落地一击（前腿扬起、举戟砸下）

1. **人立**：马的前腿抬起（远前蹄抬起 7 格），骑士后仰，两手把戟举到头顶上方，戟刃朝左上方
2. **举到最高**：戟横在头顶上方、戟刃在**左边**（身后），骑士后仰（头往左 3 格）；远前蹄向前高高踢出
3. **砸下（出手帧）**：前腿重重落下，整个身体向右前方扑（头往右 16 格、低 6 格），戟从头顶向前下方猛砸，**戟刃砸到右前方的地面**（离站位点右约 30 格，贴着脚底线） **← 出手帧**
4. 保持：戟刃还压在右前方地面附近，身体慢慢抬起

`[animation]`：

```text
THE CHARGE'S BLOW (E landing, the knockback), 4 frames, League's empowered strike: 1 REARING: the horse lifts its front legs (the far front hoof lifted 7), the rider leaning back, both hands raising the glaive above his head, the blade to the upper left. 2 HIGHEST: the glaive held level above his head, the blade at the LEFT behind him, the rider leaning back (the head 3 left); the far front hoof kicked high forward. 3 THE SMASH (it hits here): the front legs come down hard, the whole body lunging forward to the right (the head 16 right and 6 lower), the glaive slammed down forward so the BLADE STRIKES THE GROUND at the front right (about 30 squares right of the standing point, at the feet line). 4 holding: the blade still down near the ground at the front right, the body slowly rising.
```

### `hecarim_ult.png` R 暗影冲击（人立举戟、平端戟冲锋）

1. **蓄势**：身体微微下沉，戟放低到身前
2. **后蹲**：马的后腿弯曲、胯往下沉 5 格（像要起跳），前腿撑着；骑士前倾，戟压低
3. **人立（出手帧，幽灵骑兵从这里冲出）**：马**用后腿站起来**——胯低、胸和头高高向后上方立起（头往左 10 格），两只前蹄高高抬起（远的抬起 8 格）；骑士把戟高高举起（戟刃朝天）；尾巴拖在地上向左 **← 出手帧**
4. **冲锋**：落下来向右疾驰，身体压低拉长，骑士前倾，**两手平端着戟像骑枪一样指向右边**（戟刃在右边、胸口高度）；近前蹄踩地、远前蹄收起
5. 冲锋：前蹄向前伸，后蹄向后蹬，头低（比待机低 5 格）
6. 冲锋：前蹄踩地，近后蹄向后踢到最远
7. 冲锋：两只前蹄都伸在前面，后蹄向后高高踢起（近后蹄抬起 6 格）；接得上第 4 帧

`[animation]`：

```text
ONSLAUGHT OF SHADOWS (R), 7 frames, League's ult: 1 GATHERING: the body sinking a little, the glaive lowered in front. 2 CROUCH: the hind legs bent, the hips sinking 5 squares (about to spring), the front legs bracing; the rider leaning forward, the glaive low. 3 REARING (the spectral riders burst out here): the horse STANDS UP ON ITS HIND LEGS - the hips low, the chest and the rider reared up high and back (the head 10 squares left), both front hooves raised high (the far one lifted 8), the rider raising the glaive high (blade to the sky); the tail low on the ground at the left. 4 THE CHARGE: down again and galloping to the right, the body low and stretched long, the rider leaning forward, BOTH HANDS HOLDING THE GLAIVE LEVEL LIKE A LANCE pointing to the right (the blade at the right at chest height); the near front hoof planted, the far front folded. 5 charging: the front hooves reaching forward, the hind hooves pushing back, the head low (5 squares lower than in the idle). 6 charging: the front hooves planted, the near hind kicked back furthest. 7 charging: both front hooves stretched forward, the hind hooves kicked up behind (the near hind lifted 6); it can loop back to frame 4.
```

### `hecarim_hit.png` 受击

1. **被击中**：骑士上身向后仰（头往左 9 格、往上 2 格），胯往下沉 2 格，戟被震得向上倾；后蹄稍稍着地
2. 恢复到一半：回到接近待机的姿势

`[animation]`：

```text
HIT, 2 frames: 1 struck: the rider rocked back (the head 9 squares left and 2 higher), the hips sinking 2, the glaive jolted upward; the hooves stay on the ground. 2 halfway back to the idle.
```

### `hecarim_dead.png` 死亡（人立、扭身、侧倒）

1. **僵住**：骑士松开戟——戟竖着立在他身旁右边（戟刃朝上），他身体僵直、低头
2. **人立惨叫**：马的前腿高高扬起（前蹄抬起 15 格以上），骑士上身和头向后仰（头往左 25 格），两臂向两边甩开；戟还立在右边原地
3. 继续向后仰到最高，两臂乱甩；戟还立在右边原地
4. 开始向左侧倒：前腿还在空中，身体扭向左边；戟倒下来横在身体左下方
5. 前腿往下落，身体继续扭倒；戟躺在左边地上
6. **瘫倒**：胯落到地面，骑士上身前垂，头低下（比站着低 2 格）
7. **侧倒在地**：整个身体侧躺在地上（头在右边贴近地面），四条腿向右边伸出、离开地面；戟横躺在身后左上方
8. 躺着不动（同上），尾巴的幽灵火变小；戟和第 7 帧同一个位置

`[animation]`：

```text
DEATH, 8 frames, League's death: 1 STIFF: he lets go of the glaive - it stands upright by itself at his right side (blade up); his body goes rigid, the head bowed. 2 THE DEATH REAR: the horse rears, both front legs kicked up high (the front hooves 15+ squares off the ground), the rider's torso and head thrown far back (the head 25 squares left), the arms flung out; the glaive still standing upright at the right where it was. 3 still rearing, the highest, the arms flailing; the glaive still standing at the right. 4 toppling to the left: the front legs still in the air, the body twisting to the left; the glaive falls and lies across at his lower left. 5 the front legs coming down, the body twisting further; the glaive on the ground at the left. 6 COLLAPSING: the hips down on the ground, the rider slumped forward, the head low. 7 FALLEN ON HIS SIDE: the whole body lying on the ground on its side (the head at the right, near the ground), the four legs stretched out to the right, off the ground; the glaive lying behind him at the upper left. 8 lying still (as 7), the ghost-flame tail smaller; the glaive where it was in frame 7. The lying body is DRAWN lying, never a rotated standing sprite.
```


## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；只用造型图色板里的颜色；
- [ ] **每帧整个半人马一起画**，头盔夹在护肩中间、跟着身体动；头盔和造型图一样小、一样的样子（两只单格眼睛）；
- [ ] **动作像英雄联盟**：把你的帧和 `zoom/` 同一帧并排看——四条腿、马身倾斜、骑士姿势、手和戟的位置对得上；
- [ ] 疾驰（跑步、E、R）：四条腿前后交替，蹄子会折到肚子下面，不是四条直棍一起摆；身体随步子起伏，首尾能接上；
- [ ] 站着时和造型图一样高、马身一样长、腿一样粗；戟、尾巴、前襟每帧都在；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格和碎点；
- [ ] 没有背影、没有倒立；出招朝图的右边；没有特效；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有网格、文字、编号、参考线；`manifest.json` 写全（每帧的格子矩形、站位点 pivot、不透明范围 bbox、**头的位置：两只眼睛的方块坐标**、出手帧戟刃的位置）；**生图原稿（没缩过的）放进 `raw/`**；最后写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）。

交付到 `outputs/hecarim-strips/`，最好打成一个 zip（`hecarim_strips_pack_done.zip`）。

## Claude 导入时（给 Claude 看）

- 生图原稿按自己的格子读回（不要用 Codex 自己隔格取样的版本）；检查严格方块、二值透明、色板、脚底线、连通块、零散黑格；**每帧面积和身高对造型图**；**每帧和 `zoom/` 同一帧并排看动作**；头按播放顺序排成一排看大小和样子。
- 疾驰：量每帧四只蹄子的 x，确认前后两对交替、着地的蹄子往后蹬得均匀（不滑步）。
- 放进 `assets/source/native/`（`hecarim_<动作>.png` 按 now 的格子），`hecarim_cells.json` 用包里这份；`import_native.py`（COMPLETE 补描边，待机由 idle_breathe 生成）。
- 按出手帧核对技能数据的时机（普攻 tick 11、Q tick 9、E 落地 tick 6、R tick 7），跑步 8 × 85 毫秒，量头像截取点，做预览 GIF（和英雄联盟原版并排），给用户审。
