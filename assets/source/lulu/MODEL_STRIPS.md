# 璐璐：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/lulu_design.png`（放大 8 倍，1024×1024）：你交的版本 2（帽子矮 3 格）**加上用户改过的脸**（圆脸颊、尖下巴——脸照这张，**不要画回方脸**）。法杖顶到脚底 44 行（帽顶到脚底 37 行），43 格宽，22 色；脚底在第 99 行，两脚中间在第 64 列。**造型图就是标准**：大红女巫帽（金边、往后卷的帽尖）、淡紫皮肤、黄绿眼睛、尖耳朵、深紫长发、红袍金边、白手套、小黑靴、扭曲木杖、帽子后面的小皮克斯，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`lulu_idle.png`），不用画（游戏里的待机呼吸由我们的工具自动生成）；它也告诉你造型图在格子里多大、站在哪里。
> - **跑步单独做，用「骨架 + 皮囊」**：`run_swap/` 里 图1 = oppi 的璐璐跑步（动作骨架，7 帧），图2 = 定稿造型（皮囊），照 `run_swap/PROMPT.md` 的中文提示词画，交 `lulu_run.png`，排版和图1一样。
> - 其余 6 张动作图按下面的表画：帧数、每帧时长、出手帧和站位照 `now/lulu_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、法杖和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例；② 头（帽子 + 脸 + 耳朵）是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**，**不画背影**（英雄联盟的 Q 和 R 会跳很高、转身——我们**不跳高、不转成背影**，最多小跳 3 格、转身时用侧身代替）；③ **腿**：in every standing frame (idle, attack, Q, W/E, R, hit) she stands on the design's OWN two little dark boots under the robe's hem square for square - the same place and width as the design, never spread, never longer; the arms, the staff, the hat, the hair and the robe move, the boots stay (a cast may move the WHOLE figure, boots included, 1-2 squares forward or back, or lift it in a small hop of at most 3 squares, never the upper body alone sliding over still boots)；④ 装备：the huge red witch hat with its gold brim and the curled tip behind (the head piece, see below), the long violet hair falling to the ground behind her, the red robe with gold edges, the white gloves, the twisted brown staff with its hooked top (always in her hands, never lost, the design's thickness: 2 squares with a lit edge) and Pix, the little faerie hovering behind the hat (the design's tiny dark body, magenta face and lilac wings, flapping: wings up / down every frame) stay in every frame；⑤ 手臂：the arms are the design's short robed arms with WHITE GLOVES, as thick as in the design (the sleeves 3-4 squares, the gloves 2x2 or 3x2) - never thinner, never 1-pixel sticks, never floating hands; the hand holding the staff stays on the staff。
> - 出招方向：**法杖指向、魔弹都朝图的右边**（游戏里朝左时会整张镜像）。
> - **死亡照英雄联盟**：她"噗"地消失，最后只剩空帽子扣在倒地的法杖上（见表）；那团烟是特效，不用画。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/lulu_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/lulu_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**（以前用脚本拼的木板手臂、火柴腿都被退回了）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/lulu-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧法杖顶端的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`lulu_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/lulu_palette.png`，或直接读 `design/lulu_design_1x.png`）。
4. **贴头**：把造型图的头（`design/lulu_head_1x.png` 里不透明的格子：大红帽、帽檐、耳朵、脸、两只眼睛、头顶的头发；在 128×128 画布上的范围 x 39–77、y 63–82，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的帽檐、头发或描边。
5. 对位：每帧按 `lulu_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/lulu_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/lulu_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/lulu_head.png`、`_1x.png` | 要贴进每一帧的头（帽子、耳朵、脸、眼睛、头顶的头发） | 贴头 |
| `design/lulu_palette.png` | 造型图的全部 22 色（暗到亮） | 色板 |
| `lulu_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `run_swap/` | 跑步的骨架（oppi 的璐璐跑步，已按我们的大小放大）、皮囊（定稿）和中文提示词 | **跑步照这里画** |
| `now/lulu_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、法杖和身体的动作 |
| `guide/lulu_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `lulu_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/lulu_picture.png`、`refs/lulu_draft_codex.png` | 用户选的原画 A 和你的造型生图原稿（长相参考；比例、大小和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 22 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every standing frame (idle, attack, Q, W/E, R, hit) she stands on the design's OWN two little dark boots under the robe's hem square for square - the same place and width as the design, never spread, never longer; the arms, the staff, the hat, the hair and the robe move, the boots stay (a cast may move the WHOLE figure, boots included, 1-2 squares forward or back, or lift it in a small hop of at most 3 squares, never the upper body alone sliding over still boots)。
- **装备**：the huge red witch hat with its gold brim and the curled tip behind (the head piece, see below), the long violet hair falling to the ground behind her, the red robe with gold edges, the white gloves, the twisted brown staff with its hooked top (always in her hands, never lost, the design's thickness: 2 squares with a lit edge) and Pix, the little faerie hovering behind the hat (the design's tiny dark body, magenta face and lilac wings, flapping: wings up / down every frame) stay in every frame。
- **手臂**：the arms are the design's short robed arms with WHITE GLOVES, as thick as in the design (the sleeves 3-4 squares, the gloves 2x2 or 3x2) - never thinner, never 1-pixel sticks, never floating hands; the hand holding the staff stays on the staff。
- **头每帧都是造型图的头**（帽子、帽檐、耳朵、脸、眼睛逐格一样，**圆脸、尖下巴**），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：魔弹、闪光、星星、变形烟雾、小动物、生长光环都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（普攻、Q、W+E、R、受击、死亡都用这一段，只替换中括号）

每张附三张图：第一张 `design/lulu_design.png`，第二张 `now/lulu_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `lulu_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, hat, face, staff, Pix and pixel style exactly; do not redesign anything (keep its ROUND face with the small pointed chin). Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the huge red witch hat with the gold brim and the curled tip behind, the lilac skin, the yellow-green eyes, the pointed ears, the long violet hair, the red robe with gold edges, the white gloves, the little dark boots, the twisted brown staff with its hooked top, the tiny faerie Pix hovering behind the hat, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the staff and the body from it, but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own boots; never draw her from the back or upside down, never a high jump (a small hop of at most 3 squares).
The character: Lulu, the Fae Sorceress (a tiny yordle witch with lilac skin, a huge red witch hat, long violet hair, a red robe, white gloves, a twisted wooden staff and her faerie Pix).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (44 squares from the staff's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 22 colors of the FIRST image, no new colors: #180A14 #2E160E #2A0E4A #5A2E1A #4E3040 #4A1A7A #7A1450 #9A1830 #8A4A12 #D2283A #6E2CA8 #B47A4E #8AD82A #F2584E #C030D0 #8A7AD8 #F6C040 #9A9AC8 #B4A8F0 #FF80FF #DCD4FF #E6E6F6. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every standing frame (idle, attack, Q, W/E, R, hit) she stands on the design's OWN two little dark boots under the robe's hem square for square - the same place and width as the design, never spread, never longer; the arms, the staff, the hat, the hair and the robe move, the boots stay (a cast may move the WHOLE figure, boots included, 1-2 squares forward or back, or lift it in a small hop of at most 3 squares, never the upper body alone sliding over still boots).
Gear: the huge red witch hat with its gold brim and the curled tip behind (the head piece, see below), the long violet hair falling to the ground behind her, the red robe with gold edges, the white gloves, the twisted brown staff with its hooked top (always in her hands, never lost, the design's thickness: 2 squares with a lit edge) and Pix, the little faerie hovering behind the hat (the design's tiny dark body, magenta face and lilac wings, flapping: wings up / down every frame) stay in every frame.
The arms: the arms are the design's short robed arms with WHITE GLOVES, as thick as in the design (the sleeves 3-4 squares, the gloves 2x2 or 3x2) - never thinner, never 1-pixel sticks, never floating hands; the hand holding the staff stays on the staff.
The head (the hat with its brim and curled tip, the ears, the round face, both eyes, the hair on top) is COPIED from the FIRST image in every frame, square for square, and only moved (tilted a little only while she falls in the death); never redraw, squash or tilt it otherwise, or it flickers when the frames play. Erase your own head before pasting it, so no extra brim, hair or outline is left beside it.
Feet line: in every cell her soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in lulu_cells.json).
3/4 front view like the FIRST image; every staff thrust and cast points to the RIGHT of the image; never her back, never upside down. Do not draw effects (bolts, sparkles, the polymorph puff, the critter, the growth aura, the death puff) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the staff, both gloves, both boots and Pix in every frame (the death: as the table says), the arms as thick as in the FIRST image, the standing frames on the FIRST image's own boots, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、法杖、身体的方向和姿势照图1，不跳高（最多小跳 3 格）、不转成背影；站着的动作腿用图2自己的小靴子。
3. 长相、配色、细节全部换成图2：大红女巫帽（金边、往后卷的帽尖）、淡紫皮肤、圆脸尖下巴、黄绿眼睛、尖耳朵、深紫长发、红袍金边、白手套、小黑靴、扭曲木杖、帽子后面的小皮克斯。头每帧照图2逐格贴，只平移。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的「动作骨架」，只是换了「皮囊」。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `lulu_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `lulu_run.png`（跑步（在 run_swap/ 换皮）） | 8 × 125 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | **不用这一行：用 `run_swap/` 的换皮画** |
| `lulu_attack.png`（普攻（挥杖射出魔弹）） | 6 帧：60 60 70 70 70 70 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK (a flick of the staff), 6 frames: 1 she draws the staff back over her shoulder, the hat tilting back; 2 the staff swinging forward; 3 the staff thrust forward level to the right, its hooked top pointing at the enemy; 4 THE SHOT (the bolt leaves the staff's top here): the staff fully stretched forward at chest height, Pix leaning forward beside the hat; 5 the follow-through, the staff dipping; 6 back toward the idle stance. The bolt and Pix's bolts are effects - do not draw them.` |
| `lulu_skill.png`（Q 闪耀长枪（平举法杖向前）） | 6 帧：55 55 57 60 70 70 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `GLITTERLANCE (Q), 6 frames (League's Q cast, picture B's pose): 1 she crouches a little, both hands bringing the staff down in front of her; 2-3 leaning forward, BOTH gloved hands levelling the staff forward like a lance, the hat tilted forward with its curled tip flying back, the hair streaming; 4 THE CAST (both bolts leave here): the staff thrust straight forward to the right at chest height, a mischievous grin, Pix spread beside the hat; 5 holding the thrust; 6 back toward the idle stance. A small hop is allowed (at most 3 squares) but never League's high jump. The lances are effects - do not draw them.` |
| `lulu_skill2.png`（W+E 奇思妙想 / 帮忙皮克斯（举杖旋一圈再指向前）） | 6 帧：55 55 57 55 55 56 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `WHIMSY + HELP, PIX! (W and E in one cast), 6 frames (League's E cast): 1 she lifts the staff; 2-3 the staff raised high above the hat with both hands, the hooked top up, twirling it once, the robe flaring; 4 THE CAST (the polymorph bolt flies and Pix leaves here): she swings the staff down and points its top forward to the right, the free hand flung back; 5 holding the point; 6 back toward the idle stance. The bolt, the sparkles and the critter are effects - do not draw them.` |
| `lulu_ult.png`（R 狂野生长（指向队友，转身举杖）） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `WILD GROWTH (R), 6 frames (League's R cast): 1 she lifts the staff in both hands; 2 the staff thrust forward level to the right at an ally, the hat flying back; 3 THE CAST (the ally grows here): she spins once, the staff raised high over the hat, the hair and the robe swirling round her (a small hop of at most 3 squares); 4 landing, the staff still high; 5 the staff coming down, pointing forward; 6 back toward the idle stance. The growth burst and the aura are effects - do not draw them.` |
| `lulu_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body, the hat and the staff pushed back 1-2 squares (to the left), the hat tilting back, Pix startled; 2 recovering toward the idle stance. The design's boots.` |
| `lulu_dead.png`（死亡（人消失，只剩帽子落在法杖上）） | 8 帧：100 100 100 100 120 150 200 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames (League's death: she vanishes and only her hat and staff are left): 1 struck, she jolts back, the hat tilting; 2 she staggers, the staff slipping from her hands; 3 she shrinks down into her robe under the hat (smaller, the hat sinking); 4 only the empty hat and the crumpling robe, the staff falling to the ground in front; 5 the hat dropping onto the ground; 6-8 the empty red hat lying on the ground on top of the staff (the staff lying flat along the feet line), Pix gone; 7 and 8 the same pose. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样（跑步和 `run_swap/1_动作骨架_oppi跑步.png` 一样），帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（圆脸尖下巴，逐格一样，只平移），头旁边没有多余的帽檐、头发、描边；
- [ ] 每帧都有法杖、两只白手套、两只小靴子、皮克斯（死亡按表）；手臂和造型图一样粗；站着的动作是造型图自己的靴子；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有高跳；出招都朝图的右边；
- [ ] 跑步：两只靴子交替，头的横向位置每帧一样，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `lulu_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、靴子和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`lulu_cells.json` 用包里这份（跑步用 `run_swap/run_layout.json`，时长按英雄联盟的步频改），`lulu_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边，法杖进 WEAPON_CARRY（待机呼吸不压弯法杖）。
- 按出手帧核对技能数据的时机（普攻 tick 11、Q tick 10、W+E tick 10、R tick 7），量头像截取点，重跑模拟，做预览 GIF。
