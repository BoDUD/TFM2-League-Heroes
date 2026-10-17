# 莉莉娅：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/lillia_design.png`（放大 8 倍，1024×1024；46 行高、32 格宽，26 色；蹄底在第 99 行，站位点在第 64 列）——是按你上一轮第 7 张生图原稿（`refs/lillia_draft_codex.png`）自己的格子取回、慢慢缩到 46 行再逐格修过的版本（用户一路看着改：「改的挺好的」）。**造型图就是标准**：洋红长发、头顶蓝紫花苞、耳边绿叶卷、紫色大眼睛、绿叶上衣和叶裙、橙色鹿身 + 紫斑、米白肚皮胸口和尾巴、四条细长鹿腿（后腿有关节）、蓝紫蹄子；**竖着握在两手里的紫色长枝条**（顶端金钩 + 青蓝小花，钩上吊着圆的橙金色灯笼和金流苏），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`lillia_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/lillia_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色；原版的腿比我们长，**大小以造型图为准**）；手臂、枝条和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。英雄联盟的 Q、E、R 会腾空翻转（有背影、倒立）：**我们不照这些**：Q 站着正面把枝条抡一圈，E 站着把枝条往头顶上方一甩，R 稍微人立、把枝条举过头顶摇；W 人立蓄力后往前砸；死亡跪倒侧躺。
> - **放技能时的鹿身就是待机的鹿身**（同一套像素）：鹿身、紫斑、米白肚皮和尾巴、四条腿和蹄子的形状和大小不能变，只动女孩的上身、手臂和枝条；整个人可以前后挪 1–2 格。只有跑步、W 的人立蓄力、R 的小人立和死亡会动到腿。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（腿比原版短、头比原版大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的花苞、叶卷、头发顶和脸**，**不画背影**（只有死亡侧躺时整个人连头一起转）；③ **腿**：the fawn body and the four legs are the design's own - the orange deer body with its purple spots, the cream belly, chest and tail, the four slender legs with the hocks on the hind ones and the blue-violet hooves - square for square in every standing frame (idle, the attack, Q, E, W's slam, R, hit): never redrawn, never thicker or shorter; a cast may move the WHOLE figure 1-2 squares forward or back, never the girl alone over a still deer; only the run, W's rearing wind-up, R's small rear and the death change them. In the run (a light trot) the legs move in diagonal pairs: the near hind leg with the far front leg, the far hind leg with the near front leg; the lifted hooves 2 rows up, passing beside the planted ones; the far legs one shade darker so they do not melt together; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares)；④ **手臂和枝条**：the girl's arms are the design's arms: pale skin with green leaf bracers, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from its shoulder (never from the chest), the near arm over the body, the far arm drawn under it; the bough (the long dark purple branch with the gold hook at its top, the small cyan blossom on its tip and the round orange-gold lantern with its gold tassel hanging from the hook) stays in her two hands and moves with them as ONE piece - turned whole in steps of 45 degrees, never bent like a rubber hose, never shifted row by row, never redrawn smaller or thinner; the lantern always hangs from the hook, its tassel down; the hands and the bough are NEVER hidden behind her body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours；⑤ the long magenta hair down her back, the green leaf top and the leaf skirt at her waist, the blue-violet bud on her head and the green leaf curl by her ear stay on her in every frame, the same shapes and sizes as in the design (the hair may sway a little with the steps in the run, as one piece)。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/lillia_now_<动作>.png`（骨架），图2 = `design/lillia_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/lillia-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧灯笼中心的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`lillia_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/lillia_palette.png`，或直接读 `design/lillia_design_1x.png`）。
4. **贴头**：把造型图的头（`design/lillia_head_1x.png` 里不透明的格子：花苞、头发顶、脸、耳边叶卷；不含旁边的枝条和背后的长发；在 128×128 画布上的范围 x 57–73、y 58–75，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡侧躺的帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `lillia_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），蹄底落在蹄底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/lillia_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，蹄底线第 99 行 | 每张动作图的第一张附图 |
| `design/lillia_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/lillia_head.png`、`_1x.png` | 要贴进每一帧的头（花苞、头发顶、脸、耳边叶卷） | 贴头 |
| `design/lillia_palette.png` | 造型图的全部 26 色（暗到亮） | 色板 |
| `lillia_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/lillia_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、枝条和身体的动作 |
| `guide/lillia_guide_<动作>.png` | 每格边框、站位点（蓝十字）、蹄底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `lillia_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/lillia_picture.png`、`refs/lillia_draft_codex.png` | 用户选的原画 A 和你上一轮第 7 张生图原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 26 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **鹿身和腿**：the fawn body and the four legs are the design's own - the orange deer body with its purple spots, the cream belly, chest and tail, the four slender legs with the hocks on the hind ones and the blue-violet hooves - square for square in every standing frame (idle, the attack, Q, E, W's slam, R, hit): never redrawn, never thicker or shorter; a cast may move the WHOLE figure 1-2 squares forward or back, never the girl alone over a still deer; only the run, W's rearing wind-up, R's small rear and the death change them. In the run (a light trot) the legs move in diagonal pairs: the near hind leg with the far front leg, the far hind leg with the near front leg; the lifted hooves 2 rows up, passing beside the planted ones; the far legs one shade darker so they do not melt together; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares)。
- **手臂和枝条**：the girl's arms are the design's arms: pale skin with green leaf bracers, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from its shoulder (never from the chest), the near arm over the body, the far arm drawn under it; the bough (the long dark purple branch with the gold hook at its top, the small cyan blossom on its tip and the round orange-gold lantern with its gold tassel hanging from the hook) stays in her two hands and moves with them as ONE piece - turned whole in steps of 45 degrees, never bent like a rubber hose, never shifted row by row, never redrawn smaller or thinner; the lantern always hangs from the hook, its tassel down; the hands and the bough are NEVER hidden behind her body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours。
- **身上**：the long magenta hair down her back, the green leaf top and the leaf skirt at her waist, the blue-violet bud on her head and the green leaf curl by her ear stay on her in every frame, the same shapes and sizes as in the design (the hair may sway a little with the steps in the run, as one piece)。
- **头每帧都是造型图的头**（花苞、叶卷、头发顶、脸逐格一样），只平移。
- **蹄底线以下什么都不能有**（游戏在这条线下画血条），灯笼、流苏、尾巴也不能低于这条线。
- **跑步循环**：每帧头相对站位点的横向位置不变；四条腿按对角两两交替；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不腾空翻转**。**只画角色本身**：花瓣、光环、种子、梦境波、星星都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/lillia_design.png`，第二张 `now/lillia_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `lillia_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same shy fawn centaur - a girl from the waist up (long magenta hair, a blue-violet bud on her head, a green leaf curl by her ear, big purple eyes, a green leaf top, a leaf skirt) on an orange deer body with purple spots, a cream belly, chest and tail, four slender legs and blue-violet hooves - holding a long dark purple bough upright in both hands (a gold hook at its top with a small cyan blossom, a round orange-gold lantern with a gold tassel hanging from the hook), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing and where the character stands in its cell, but NOT its blurry look and NOT its size (the FIRST image's size wins: shorter legs, a bigger head). THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the bough and the body from it, but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own deer body and legs; every swing goes to the RIGHT of the image; never draw her from the back, upside down or flipping in the air (the original leaps and flips - we do not).
The character: Lillia, the Bashful Bloom (a shy fawn centaur girl with a dream lantern on a bough).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 26 colors of the FIRST image, no new colors: #140808 #2A0838 #2E4A10 #036A2E #9A2A08 #5A1078 #3E8A2A #8A5A10 #3A2C9A #4A1AA0 #B8075E #D84A0A #F00480 #FF7F00 #E8A010 #8A4AF0 #D88C68 #B1DC43 #FBD70B #56C8FE #FF6EB8 #9499FC #E8C890 #F8C8A0 #FFF0C8 #FFFFFF. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The deer is the idle deer: in every standing frame the deer body, its spots, the cream belly, chest and tail, the four legs and the hooves keep the FIRST image's shapes and sizes square for square; only the girl's upper body, her arms and the bough move, and the whole figure may move 1-2 squares.
Legs: the fawn body and the four legs are the design's own - the orange deer body with its purple spots, the cream belly, chest and tail, the four slender legs with the hocks on the hind ones and the blue-violet hooves - square for square in every standing frame (idle, the attack, Q, E, W's slam, R, hit): never redrawn, never thicker or shorter; a cast may move the WHOLE figure 1-2 squares forward or back, never the girl alone over a still deer; only the run, W's rearing wind-up, R's small rear and the death change them. In the run (a light trot) the legs move in diagonal pairs: the near hind leg with the far front leg, the far hind leg with the near front leg; the lifted hooves 2 rows up, passing beside the planted ones; the far legs one shade darker so they do not melt together; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares).
The arms and the bough: the girl's arms are the design's arms: pale skin with green leaf bracers, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from its shoulder (never from the chest), the near arm over the body, the far arm drawn under it; the bough (the long dark purple branch with the gold hook at its top, the small cyan blossom on its tip and the round orange-gold lantern with its gold tassel hanging from the hook) stays in her two hands and moves with them as ONE piece - turned whole in steps of 45 degrees, never bent like a rubber hose, never shifted row by row, never redrawn smaller or thinner; the lantern always hangs from the hook, its tassel down; the hands and the bough are NEVER hidden behind her body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours.
The body parts: the long magenta hair down her back, the green leaf top and the leaf skirt at her waist, the blue-violet bud on her head and the green leaf curl by her ear stay on her in every frame, the same shapes and sizes as in the design (the hair may sway a little with the steps in the run, as one piece).
The head (the bud, the leaf curl, the top of the hair, the face with the big purple eyes) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the death frames where she lies on her side is it turned with the whole body). Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell the hooves are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in lillia_cells.json). In the run her head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every swing goes to the RIGHT of the image; never her back, never upside down, never flipping in the air. Do not draw effects (petals, flower rings, the seed, the dream wave, sleep bubbles, stars) - only the character. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms growing from the shoulders in every frame, the hands and the bough never behind the body and the lantern always hanging from the hook, the standing frames on the FIRST image's own deer body and legs, the run's legs moving in diagonal pairs, no loose pieces, no stray black squares, nothing below the feet line, never her back, upside down or flipping, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、排列顺序和格子，每一格是 8×8 像素的纯色方块；人物大小照图2（图1的腿太长，按图2的比例画）。
2. 保留每一帧的动作：手臂、枝条和身体的方向和姿势照图1（挥动都朝图的右边，不画背影、不倒立、不腾空翻转）；站着的帧鹿身和四条腿用图2自己的。
3. 长相、配色、细节全部换成图2：洋红长发、蓝紫花苞、绿叶卷、紫色大眼睛、绿叶上衣和叶裙、橙色鹿身和紫斑、米白肚皮胸口尾巴、四条细长鹿腿、蓝紫蹄子、紫色长枝条（金钩、青蓝小花、圆的橙金灯笼和金流苏）。
4. 两只手握着枝条，手和枝条任何一帧都不能藏在身体后面，灯笼始终吊在金钩上。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 蹄底线 | `[animation]` |
|---|---|---|---|---|---|
| `lillia_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `lillia_run.png`（跑步（小跑，对角两腿一起动）） | 8 × 92 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's trot, 0.73 s): the fawn trots, the legs moving in diagonal pairs (near hind with far front, far hind with near front): in frames 1 and 5 the pairs are furthest apart, in frames 3 and 7 the lifted pair passes 2 rows up beside the planted pair; the girl's upper body stays upright holding the bough upright as in the design, the lantern swinging a little; the body bobs 1 row with each landing; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `lillia_attack.png`（普攻（抡枝条往前劈）） | 5 帧：60 60 80 80 100 | 第 3 帧（tick 7） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `BASIC ATTACK (a swing of the bough), 5 frames: 1 the design's stance; 2 the wind-up: the bough swung back over her far shoulder, the lantern behind her head; 3 THE SWING (the hit lands here): both arms and the bough brought down forward to the image right, the bough pointing down-right in front of her, the lantern flung forward; 4 the follow-through, the bough low in front of the deer's chest; 5 back to the design's stance. The deer body and legs: the design's.` |
| `lillia_skill.png`（Q 飞花挞（正面转一圈）） | 6 帧：60 60 70 70 70 80 | 第 3 帧（tick 7） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BLOOMING BLOWS (Q, the bough spun round her), 6 frames, drawn from the FRONT the whole time (League's Lillia leaps and flips in the air - we do not): 1 the bough held level to the image left behind her, the lantern at its end; 2 the bough swung up over her head; 3 THE SPIN (the hit lands here): the bough swept round to the image right, level at chest height, the lantern far out to the right; 4 the bough carried on round, low in front of the deer's chest; 5 the bough coming back up on the left; 6 back to the design's stance. The deer body and legs: the design's. The spinning flower ring is an effect.` |
| `lillia_skill2.png`（E 流涡种（往头顶抛种子）） | 4 帧：60 60 70 80 | 第 3 帧（tick 7） | 4 列 × 1 行，4096×768 | 第 81 行 | `SWIRLSEED (E, a seed tossed overhead), 4 frames: 1 the bough lowered behind her, both hands low; 2 the bough swung up past her shoulder; 3 THE THROW (the seed leaves here): the bough raised high and forward to the image right, her arms up, as if tossing something over her head; 4 back to the design's stance. The deer body and legs: the design's. The seed is a separate effect.` |
| `lillia_skill2_w.png`（W 惊惶木（人立蓄力后往前砸）） | 7 帧：80 100 100 150 80 120 120 | 第 5 帧（tick 26） | 4 列 × 2 行，4096×1536，最后 1 格空 | 第 81 行 | `WATCH OUT! EEP! (W, a wound-up slam), 7 frames: 1 crouching a little, the bough pulled back; 2 rearing: the deer's front legs lifted 2-3 rows, the body tilted back at most 20 degrees, the bough raised behind her head; 3 the bough raised high, straight up over her head, still rearing; 4 holding the wind-up (as 3); 5 THE SLAM (the strike lands here): the front hooves back down, the bough slammed down in front of her to the image right, the lantern striking the ground; 6 the bough still down, recovering; 7 back to the design's stance.` |
| `lillia_ult.png`（R 夜阑谣（举枝摇晃）） | 6 帧：80 80 100 100 100 100 | 第 3 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `LILTING LULLABY (R, the lullaby), 6 frames: 1 gathering, the deer's legs bent 1 row; 2 rearing up a little (the front hooves 1-2 rows up), the bough raised; 3 THE LULLABY (released here): the bough held high over her head, the lantern swinging, her eyes closed and smiling; 4-5 swaying the bough gently left and right overhead; 6 back to the design's stance. The dream wave and the petals are effects.` |
| `lillia_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: her upper body and head pushed back 1-2 squares (to the left), the deer flinching; 2 recovering toward the design's stance. The deer body and legs: the design's.` |
| `lillia_dead.png`（死亡（跪倒侧躺）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 staggering, the front legs buckling; 3 the deer kneeling, the legs folding under the body, sinking 3-4 rows; 4 lying down on the ground on her side (the girl slumped forward over the deer's back, the bough dropped beside her, the head to the image right); 5-8 the same as 4, still. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样大；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 站着的帧鹿身、紫斑、米白肚皮胸口尾巴、四条腿和蹄子和造型图一样；两只手臂都在、和造型图一样粗；手和枝条没有藏在身体后面，灯笼始终吊在金钩上、枝条没有变小变细；
- [ ] 跑步四条腿按对角两两交替、远侧腿暗一档、腿没有缺格子；
- [ ] 蹄底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有腾空翻转；挥动都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `lillia_<动作>.png` 先检查（严格方块、二值透明、色板、蹄底线、连通块、手臂粗细、鹿身和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；鹿身不是待机鹿身的帧用造型图的部件重摆（rigkit：手臂连枝条整块按 45° / 90° 转）。
- 放进 `assets/source/native/`，`lillia_cells.json` 用包里这份，`lillia_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边；红色方：朝向特效烘进动作帧（`lillia_bake.json`）。
- 按出手帧核对技能数据的时机（普攻 tick 7、Q tick 7、E 抛出 tick 7、W 砸下 tick 26、R tick 10），量头像截取点，重跑模拟，做预览 GIF。
