# 雷恩加尔：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/rengar_design.png`（放大 8 倍，1024×1024）：骨角尖到脚底 40 行，41 格宽，25 色；脚底在第 99 行，两脚中间在第 64 列。这张是在你上一轮生图稿（`refs/rengar_draft_codex.png`）的基础上逐格整理出来的，**造型图就是标准**：灰白辫子大鬃毛、肩后两根弯骨角、白色狮脸（粉耳朵、金眼罩、冰蓝眼、粉鼻子、獠牙、胡须）、近侧钢蓝肩甲（铜铆钉）、胸前皮带（金钉）、腰带金扣、皮条短裙、蓝灰身体毛、红棕护膝、交叉金绳的皮绑腿、骨色爪子的猫爪脚、带环纹白尾尖的长尾巴；画面左手腕三根骨爪刃，画面右手握刃口血红的锯齿弯刀。颜色、明暗每一帧都照它，只改姿势。
> - **待机条已经做好**（`rengar_idle.png`），不用画（游戏里的待机呼吸由我们的工具自动生成）；它也告诉你造型图在格子里多大、站在哪里。
> - **跑步单独做，用「骨架 + 皮囊」**：`run_swap/` 里 图1 = oppi 画的雷恩加尔跑步（同一个英雄，动作骨架，8 帧），图2 = 定稿造型（皮囊），照 `run_swap/PROMPT.md` 的中文提示词画，交 `rengar_run.png`，排版和图1一样。**两条腿一定要前后交替、膝盖交叉，两条腿颜色一样**（以前好几个英雄跑步是平行走路、或者一条腿变了颜色，被退回过）。
> - 其余 8 张动作图按下面的表画：帧数、每帧时长、出手帧和站位照 `now/rengar_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。`refs/oppi/` 里有 oppi 画的同一个英雄的几个动作（游戏尺寸），想看这个动作在小尺寸下怎么画时可以参考，**只看动作，不要照它的长相和颜色**。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头和鬃毛大、手脚短粗，英雄联盟的手脚更长，不要照）；② 头（辫子鬃毛 + 两根骨角 + 白色狮脸 + 胡须）是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**，**不画背影**；③ **腿**：in every STANDING frame (attack 1-2 and 5-6, E, W, hit) he stands on the design's OWN legs square for square: the two bent cat legs in dark-brown leather wraps with crossed gold laces, the round red-brown knee pads, the blue-grey clawed feet with bone-tan claws, the same place and width as the design, never spread, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the CROUCHING and LEAPING frames (attack 3-4, the leap, Q, R) the legs follow League's pose (bent deeper, pushing off, tucked in the air, landing) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body；④ 装备：the steel-blue pauldron with gold rivets on the near shoulder (image left; three plates), the red-brown chest strap with its gold studs running down to the belt, the belt with the square gold buckle, the short kilt of leather straps, the steel bits and the gold rivet on the far shoulder (image right), the bone necklace tooth under the beard, and the long blue-grey tail with brown rings and a white tuft stay in every frame；⑤ 手臂：the image-LEFT arm is the design's blue-grey fur arm with the red-brown bracer and the gauntlet of THREE long curved bone-tan claw blades (each a 1-2 square wide wedge with a lit edge); the image-RIGHT arm is the design's blue-grey fur arm with the red-brown bracer, its hand holding the long curved serrated bone-tan blade with the blood-red edge (2 squares wide, never shorter than in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; the claws and the blade never lost。
> - 出招方向：**挥刀、飞扑、甩套索都朝图的右边**（游戏里朝左时会整张镜像）。
> - **飞扑在空中**：第 3–5 帧整个人离地（脚底在脚底线上方 4–8 格），第 6 帧落地；Q 第 2–3 帧跳起来时刀尖可以碰到格子顶。
> - **死亡照英雄联盟**：被打飞后仰面倒在地上，刀掉在手边（见表）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/rengar_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/rengar_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**（以前用脚本拼的木板手臂、火柴腿都被退回了）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/rengar-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手 / 刀的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`rengar_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/rengar_palette.png`，或直接读 `design/rengar_design_1x.png`）。金眼罩的黄、冰蓝眼的蓝（#0297EA）、耳朵的粉（#F9AED8、#E47FB4）、鼻子的玫红（#D03379）**只用在脸上**。
4. **贴头**：把造型图的头（`design/rengar_head_1x.png` 里不透明的格子：辫子鬃毛、两根骨角和它们的皮带、白色狮脸、耳朵、金眼罩、冰蓝眼、鼻子、獠牙、胡须；在 128×128 画布上的范围 x 53–77、y 60–83，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡躺倒的几帧整块转 90°）。贴之前先擦掉你自己画的头、鬃毛和骨角，不要在头旁边留下多余的鬃毛、角或描边。**头下面要接上肩膀和胸口**（鬃毛下沿紧挨着肩甲和胸前皮带），不要留出空隙或长出一截脖子。
5. 对位：每帧按 `rengar_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），站着的帧脚底落在脚底线上（飞扑空中的帧离地）；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/rengar_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/rengar_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/rengar_head.png`、`_1x.png` | 要贴进每一帧的头（鬃毛、骨角、脸、胡须） | 贴头 |
| `design/rengar_palette.png` | 造型图的全部 25 色（暗到亮） | 色板 |
| `rengar_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `run_swap/` | 跑步的骨架（oppi 的雷恩加尔跑步，已按我们的大小放好）、皮囊（定稿）和中文提示词 | **跑步照这里画** |
| `now/rengar_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/rengar_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `rengar_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/oppi/oppi_<动作>.png` | oppi 画的同一个英雄的动作（游戏尺寸 ×6）：普攻、飞扑、套索、战吼、死亡 | **只看小尺寸下的动作**，长相颜色以定稿为准 |
| `refs/rengar_picture.png`、`refs/rengar_draft_codex.png` | 用户选的原画 A 和你上一轮的生图稿（长相参考；比例、大小和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 25 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every STANDING frame (attack 1-2 and 5-6, E, W, hit) he stands on the design's OWN legs square for square: the two bent cat legs in dark-brown leather wraps with crossed gold laces, the round red-brown knee pads, the blue-grey clawed feet with bone-tan claws, the same place and width as the design, never spread, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the CROUCHING and LEAPING frames (attack 3-4, the leap, Q, R) the legs follow League's pose (bent deeper, pushing off, tucked in the air, landing) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body。
- **装备**：the steel-blue pauldron with gold rivets on the near shoulder (image left; three plates), the red-brown chest strap with its gold studs running down to the belt, the belt with the square gold buckle, the short kilt of leather straps, the steel bits and the gold rivet on the far shoulder (image right), the bone necklace tooth under the beard, and the long blue-grey tail with brown rings and a white tuft stay in every frame。
- **手臂**：the image-LEFT arm is the design's blue-grey fur arm with the red-brown bracer and the gauntlet of THREE long curved bone-tan claw blades (each a 1-2 square wide wedge with a lit edge); the image-RIGHT arm is the design's blue-grey fur arm with the red-brown bracer, its hand holding the long curved serrated bone-tan blade with the blood-red edge (2 squares wide, never shorter than in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; the claws and the blade never lost。
- **头每帧都是造型图的头**（鬃毛、骨角、白脸、耳朵、金眼罩、冰蓝眼、鼻子、獠牙、胡须逐格一样），只平移（死亡躺倒时整块转 90°）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：刀光、爪痕、套索、吼声波纹、隐身烟雾都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（普攻、飞扑、Q、E、W、R、受击、死亡都用这一段，只替换中括号）

每张附三张图：第一张 `design/rengar_design.png`，第二张 `now/rengar_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `rengar_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, mane, face, gear, weapons and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the huge pale braided mane, the two curved bone horn trophies behind the far shoulder, the white lion face with the pink ear, the gold eye-piece, the icy blue eye, the pink nose and the fangs, the steel-blue pauldron with gold rivets, the chest strap with gold studs, the gold belt buckle, the leather strap kilt, the blue-grey fur, the red-brown knee pads, the laced leather shin wraps, the clawed cat feet, the striped tail with the white tuft, the three bone claw blades on the image-left wrist and the serrated blood-edged blade in the image-right hand, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the weapons, the tail and the body from it, but keep the FIRST image's proportions (big head and mane, short thick limbs - not the long limbs of the 3D model) and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Rengar, the Pridestalker (a hunched lion beast-man hunter with a braided mane, a gold eye-piece, claw blades and a serrated blade).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the horn's tip to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 25 colors of the FIRST image, no new colors: #0E0206 #3A1A26 #70292B #A8031E #7D512D #444B6F #923937 #B04218 #5068A0 #5F6A90 #D5800F #D03379 #0297EA #C4843C #F4B507 #7593CE #E0A65A #909BBB #E47FB4 #F4D05A #FBD88C #C2C7DB #A9C9F4 #F9AED8 #EFF0F5. The eye colors (the gold and yellow of the eye-piece, the blue #0297EA), the ear pinks (#F9AED8, #E47FB4) and the nose (#D03379) only on the face. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every STANDING frame (attack 1-2 and 5-6, E, W, hit) he stands on the design's OWN legs square for square: the two bent cat legs in dark-brown leather wraps with crossed gold laces, the round red-brown knee pads, the blue-grey clawed feet with bone-tan claws, the same place and width as the design, never spread, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the CROUCHING and LEAPING frames (attack 3-4, the leap, Q, R) the legs follow League's pose (bent deeper, pushing off, tucked in the air, landing) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body.
Gear: the steel-blue pauldron with gold rivets on the near shoulder (image left; three plates), the red-brown chest strap with its gold studs running down to the belt, the belt with the square gold buckle, the short kilt of leather straps, the steel bits and the gold rivet on the far shoulder (image right), the bone necklace tooth under the beard, and the long blue-grey tail with brown rings and a white tuft stay in every frame.
The arms: the image-LEFT arm is the design's blue-grey fur arm with the red-brown bracer and the gauntlet of THREE long curved bone-tan claw blades (each a 1-2 square wide wedge with a lit edge); the image-RIGHT arm is the design's blue-grey fur arm with the red-brown bracer, its hand holding the long curved serrated bone-tan blade with the blood-red edge (2 squares wide, never shorter than in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; the claws and the blade never lost.
The head (the braided mane, the two horn trophies with their strap, the white face with the ear, the eye-piece, the blue eye, the nose, the fangs and the beard) is COPIED from the FIRST image in every frame, square for square, and only moved (turned a quarter only while he lies dead); never redraw, squash or tilt it otherwise, or it flickers when the frames play. Erase your own head, mane and horns before pasting it, so no extra mane, horn or outline is left beside it; the mane's lower edge meets the pauldron and the chest strap - no gap and no neck.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]) - except the leap's frames 3-5, where he is in the air above it; NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in rengar_cells.json).
3/4 front view like the FIRST image; every slash, pounce and throw points to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash trails, claw marks, the bola, the roar wave, the camouflage smoke) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x96 squares (896x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms with the claw blades and the blade, both legs and feet in every frame, the pauldron, the chest strap and the buckle, the tail, the arms as thick as in the FIRST image, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、骨爪刃、弯刀、尾巴、身体的方向和姿势照图1，不转成背影；站着的动作腿用图2自己的腿（皮绑腿、交叉金绳、护膝、猫爪脚），蹲下和跳起的动作腿照图1弯，但还是图2的腿。
3. 长相、配色、细节全部换成图2：灰白辫子大鬃毛、肩后两根弯骨角、白色狮脸（粉耳朵、金眼罩、冰蓝眼、粉鼻子、獠牙、胡须）、近侧钢蓝肩甲（铜铆钉）、胸前皮带（金钉）、腰带金扣、皮条短裙、蓝灰身体毛、护膝、绑腿、猫爪脚、带环纹白尾尖的长尾巴；画面左手腕三根骨爪刃，画面右手握刃口血红的锯齿弯刀。头（鬃毛 + 骨角 + 脸 + 胡须）每帧照图2逐格贴，只平移。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的「动作骨架」，只是换了「皮囊」。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `rengar_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1536 | 第 81 行 | **已做好，不用画** |
| `rengar_run.png`（跑步（在 run_swap/ 换皮）） | 8 × 120 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | **不用这一行：用 `run_swap/` 的换皮画** |
| `rengar_attack.png`（普攻（扑上去挥刀横扫）） | 6 帧：60 60 60 70 80 90 | 第 4 帧（tick 11） | 3 列 × 2 行，2688×1536 | 第 81 行 | `BASIC ATTACK (League's: he springs at the enemy and rips the serrated blade across), 6 frames: 1 crouched a little, the blade arm held in front of his body with the blade hanging low, the claw arm raised; 2 coiling, the blade lifted; 3 he springs forward (the WHOLE figure 1-2 squares to the right), both arms flung wide; 4 THE SLASH (the hit lands here): the blade arm swept forward to the right at chest height, the blade's edge leading, the claw arm back by his hip; 5 the follow-through, the blade low at the right; 6 back toward the idle stance. The slash trail is an effect - do not draw it.` |
| `rengar_leap.png`（飞扑（被动草丛飞扑 + R 扑杀）） | 8 帧：50 50 60 60 60 70 80 80 | 第 6 帧（tick 17） | 4 列 × 2 行，3584×1536 | 第 81 行 | `THE POUNCE (his passive leap from the brush and his ult's leap; League's leap), 8 frames: 1 crouching low, ready to pounce, the weapons drawn back; 2 launching up and forward, the legs pushing off; 3-5 IN THE AIR: the body stretched forward toward the right, the claws and the blade reaching ahead, the tail streaming behind, the feet tucked - his soles 4-8 squares ABOVE the feet line at the top of the arc (frame 4), lower in 3 and 5; 6 THE LANDING STRIKE (the hit lands here): landed crouched on the feet line, the blade and the claws raking down to the right; 7 crouched, rising; 8 back toward the idle stance.` |
| `rengar_skill.png`（Q 野蛮打击（跳起猛砸再上挑）） | 8 帧：50 50 60 50 50 70 70 80 | 第 6 帧（tick 16） | 4 列 × 2 行，3584×1536 | 第 81 行 | `SAVAGERY (Q; League's Q: he jumps up and slams down, then rips upward), 8 frames: 1 crouching; 2 springing up, rearing tall on his toes, the blade raised high above his head; 3 at the top, the blade highest (its tip may reach the top of the cell), the claws up; 4 coming down; 5 THE SLAM: crashing down low, the blade driven down in front of him to the right; 6 THE RIP (the hit lands here): a rising slash, the blade swung up and forward to the right; 7 the blade high at the right, the follow-through; 8 back toward the idle stance. The slash trails are effects - do not draw them.` |
| `rengar_skill2.png`（E 套索打击（抡起套索甩出去）） | 6 帧：70 70 80 70 80 90 | 第 4 帧（tick 13） | 3 列 × 2 行，2688×1536 | 第 81 行 | `BOLA STRIKE (E; League's E: he whirls a bola and throws it), 6 frames: 1 crouched a little, the CLAW hand (image left) reaching back; 2 rising, the claw arm swinging up behind his head; 3 the claw arm high above his head, whirling; 4 THE THROW (the bola leaves the hand here): the claw arm whipped forward to the right at shoulder height, the body leaning in, the blade arm back; 5 the follow-through, the claw arm low in front; 6 back toward the idle stance. The bola is an effect - do not draw it.` |
| `rengar_skill_w.png`（W 战吼（挺身咆哮）） | 7 帧：60 70 80 120 120 90 80 | 第 3 帧（tick 8） | 4 列 × 2 行，3584×1536，最后 1 格空 | 第 81 行 | `BATTLE ROAR (W; League's W: a terrifying roar), 7 frames: 1 crouching, gathering breath; 2 rising, the chest swelling; 3 THE ROAR (the roar wave starts here): standing tall, chest out, both arms flung down and out to his sides (the blade and the claws spread), the design's head moved 1-2 squares higher (not turned); 4-5 holding the roar (the arms one square higher / lower, the tail lashing); 6 easing down; 7 back toward the idle stance. The roar wave is an effect - do not draw it.` |
| `rengar_ult.png`（R 狩猎律动（伏低身子准备隐身）） | 4 帧：70 90 150 100 | 第 3 帧（tick 10） | 4 列 × 1 行，3584×768 | 第 81 行 | `THRILL OF THE HUNT (R; he drops into a stalking crouch and vanishes), 4 frames: 1 lowering into a crouch; 2 crouched low like a stalking cat, the body pressed toward the ground, the blade and the claws held low at his sides, the tail low; 3 THE VANISH (his camouflage starts here): the same low crouch; 4 rising a little back toward the idle stance. Draw him fully visible - the game fades him.` |
| `rengar_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1792×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body pushed back 1-2 squares (to the left), the design's head moved back a little (not turned), the arms flung out; 2 recovering toward the idle stance. The design's legs.` |
| `rengar_dead.png`（死亡（被击飞后仰面倒地）） | 8 帧：100 100 100 120 120 150 200 500 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `DEATH, 8 frames (League's death: knocked into the air, he falls on his back): 1 struck, he jolts back; 2 knocked off his feet, flying back and up, the blade slipping from his hand; 3 falling backward, the body turning level; 4 crashing down on his back; 5-8 lying on his back on the ground, the legs and the tail limp, the blade lying on the ground beside his hand, the design's head turned a quarter on its side at the left end; 6, 7 and 8 the same pose. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样（跑步和 `run_swap/1_动作骨架_oppi雷恩加尔跑步.png` 一样），帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；眼睛、耳朵、鼻子的颜色只在脸上；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的鬃毛、角、描边，鬃毛下面没有空隙；
- [ ] 每帧都有三根骨爪刃和锯齿弯刀、肩甲、胸前皮带和金扣、两条腿和脚、尾巴；手臂和造型图一样粗；站着的动作是造型图自己的腿；
- [ ] 脚底线以下没有任何像素（飞扑空中的帧离地）；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步：两条腿前后交替、膝盖交叉、颜色一样，头的横向位置每帧一样，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `rengar_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`rengar_cells.json` 用包里这份（跑步用 `run_swap/run_layout.json`，8 × 120 毫秒），`rengar_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 11、飞扑落地 tick 17、Q tick 16、E tick 13、W tick 8、R tick 10），量头像截取点，重跑模拟，做预览 GIF。
