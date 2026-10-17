# 莎弥拉：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/samira_design.png`（放大 8 倍，1024×1024；头发顶到脚底 40 行，32 格宽（连刀），28 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生图原稿 attempt1_A（`refs/samira_draft_codex.png`）按格子读回、整行整列删到 40 行的版本（每一格都是原稿的像素），再把刀身、枪管露到轮廓外、两只靴子理直，用户确认的。**造型图就是标准**：墨绿黑头发和金发饰、画面左眼的墨绿眼罩和红系带、亮绿的右眼、金箍长辫、墨绿黑无袖高领上衣和红斜布带、露腹、黑露指手套、胯边金色枪套和手枪、墨绿过膝长靴（红靴口、金鞋跟）、斜背的大刀（深钢刀身、银刃口、金护手、红刀柄头和短红飘带），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`samira_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/samira_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、刀枪和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（40 行高、头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 侧脸（眼罩在画面左眼）**，**不画背影**（参考渲染里旋转时身体会转过去，我们的头不转）；长辫子你自己画，跟着动作甩；③ **腿**：in the standing frames (idle, the shots, the wind-ups, the hit) she stands on the design's OWN legs square for square - the same stance, the same dark green over-the-knee boots with the red cuffs and gold heels, never spread wider, never crossed, never shorter; in the sword swings, the dash and the spins she may step, lunge or crouch as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls；④ 刀和枪：her weapons are the design's own: the HUGE greatsword (a dark steel blade with a bright silver edge, a dark hilt with a gold guard, a red pommel and a short red ribbon) at the design's length in every frame - slung across her back while she shoots, swung in her hand for the sword moves (never shrunk, never bent, never broken into pieces) - and the two pistols (dark steel with gold, silver barrels) drawn from the gold hip holsters when she shoots, back in them when she does not; the weapons are never dropped except in the death；⑤ 手臂：the arms are the design's arms: bronze skin, black fingerless gloves, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands, and the hand holding a gun or the sword always in sight in front of or beside her body, never hidden behind it; the dark green top with the red sash, the gold hip holsters and the braid stay on her。
> - 出招方向：**开枪、挥刀、冲刺都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/samira_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/samira_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/samira-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧枪口 / 刀尖和握武器那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`samira_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/samira_palette.png`，或直接读 `design/samira_design_1x.png`）。
4. **贴头**：把造型图的头（`design/samira_head_1x.png` 里不透明的格子：头发和金发饰、脸、眼罩和红系带、绿眼睛、下巴；不含刀柄和长辫子；在 128×128 画布上的范围 x 58–76、y 60–74，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发或描边；长辫子接在后脑，跟着动作甩。
5. 对位：每帧按 `samira_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/samira_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/samira_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/samira_head.png`、`_1x.png` | 要贴进每一帧的头（头发和金发饰、脸、眼罩、绿眼睛、下巴） | 贴头 |
| `design/samira_palette.png` | 造型图的全部 28 色（暗到亮） | 色板 |
| `samira_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/samira_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、刀枪和身体的动作 |
| `guide/samira_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `samira_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/samira_picture.png`、`refs/samira_draft_codex.png` | 用户选的原画 A 和你的生图原稿 attempt1_A（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（头发顶到脚底 40 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 28 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：in the standing frames (idle, the shots, the wind-ups, the hit) she stands on the design's OWN legs square for square - the same stance, the same dark green over-the-knee boots with the red cuffs and gold heels, never spread wider, never crossed, never shorter; in the sword swings, the dash and the spins she may step, lunge or crouch as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls。
- **刀和枪**：her weapons are the design's own: the HUGE greatsword (a dark steel blade with a bright silver edge, a dark hilt with a gold guard, a red pommel and a short red ribbon) at the design's length in every frame - slung across her back while she shoots, swung in her hand for the sword moves (never shrunk, never bent, never broken into pieces) - and the two pistols (dark steel with gold, silver barrels) drawn from the gold hip holsters when she shoots, back in them when she does not; the weapons are never dropped except in the death。
- **手臂**：the arms are the design's arms: bronze skin, black fingerless gloves, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands, and the hand holding a gun or the sword always in sight in front of or beside her body, never hidden behind it; the dark green top with the red sash, the gold hip holsters and the braid stay on her。
- **头每帧都是造型图的头**（头发、金发饰、脸、眼罩、绿眼睛逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条），刀尖也不能伸到线下。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的脚踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色和她的刀枪**：枪口火光、子弹、刀光、冲刺的拖尾、旋转的刀圈都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/samira_design.png`，第二张 `now/samira_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `samira_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, costume, weapons and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same dark teal-black hair with gold ornaments, the dark green EYEPATCH with its red strap over the eye on image left, the bright green eye on image right, the long braid with gold rings, the sleeveless dark green-black top with the red sash, the bare midriff, the bronze skin, the black fingerless gloves, the gold hip holsters with the pistols, the dark green over-the-knee boots with red cuffs and gold heels, the huge greatsword with its dark steel blade, silver edge, gold guard and red pommel, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the guns, the sword and the body from it, but keep the FIRST image's proportions (40 squares tall, a big head); never draw her from the back or upside down.
The character: Samira, the Desert Rose (a confident gunslinger with an eyepatch, two pistols and a huge greatsword on her back).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the top of the hair to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 28 colors of the FIRST image, no new colors: #0C080D #023D08 #440B13 #232B29 #3B241D #6E020F #262936 #38433D #6A381D #951517 #B20413 #2B5664 #94510B #DB0316 #2CB137 #D47603 #8D983A #777B90 #DA6D40 #EB9607 #AC8C69 #F6B205 #F1955D #F8D824 #BCBFB6 #B5BAD2 #FAEF8F #E9EBF2. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in the standing frames (idle, the shots, the wind-ups, the hit) she stands on the design's OWN legs square for square - the same stance, the same dark green over-the-knee boots with the red cuffs and gold heels, never spread wider, never crossed, never shorter; in the sword swings, the dash and the spins she may step, lunge or crouch as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls.
The weapons: her weapons are the design's own: the HUGE greatsword (a dark steel blade with a bright silver edge, a dark hilt with a gold guard, a red pommel and a short red ribbon) at the design's length in every frame - slung across her back while she shoots, swung in her hand for the sword moves (never shrunk, never bent, never broken into pieces) - and the two pistols (dark steel with gold, silver barrels) drawn from the gold hip holsters when she shoots, back in them when she does not; the weapons are never dropped except in the death.
The arms: the arms are the design's arms: bronze skin, black fingerless gloves, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands, and the hand holding a gun or the sword always in sight in front of or beside her body, never hidden behind it; the dark green top with the red sash, the gold hip holsters and the braid stay on her.
The head (the hair with the gold ornaments, the face with the eyepatch and its red strap, the green eye, the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it; the braid joins the back of the head and swings with the motion.
Feet line: in every cell her soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in samira_cells.json). In the run her head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every shot, slash and dash goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (muzzle flashes, bullets, slash arcs, the dash's trail, the spinning blade's ring) - only the character and her weapons. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the whole greatsword and the guns where the animation needs them, both arms and the hands holding the weapons in sight in every frame, the legs the design's legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、刀、枪、身体的方向和姿势照图1；站着的动作腿用图2自己的腿；拿刀拿枪的手不能藏到身体后面。
3. 长相、配色、细节全部换成图2：墨绿黑头发和金发饰、画面左眼的墨绿眼罩和红系带、亮绿的右眼、金箍长辫、墨绿黑无袖上衣和红斜布带、露腹、黑露指手套、金色枪套和手枪、墨绿过膝长靴（红靴口、金鞋跟）、斜背的大刀（深钢刀身、银刃口、金护手、红刀柄头）。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `samira_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `samira_run.png`（跑步） | 8 × 133 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 1.07 s a cycle): the design's legs swing from the hips, left and right alternate (the leading foot changes every half cycle, the feet at most 12 squares apart), the planted foot on the feet line; the body leans a little forward, bobbing at most 1 square; the sword stays slung across her back as in the design, the pistols in the holsters; the arms swing; the braid swings behind; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `samira_attack.png`（普攻（开枪）） | 6 帧：60 60 60 70 80 100 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `GUN SHOT (basic attack at range), 6 frames: 1 the front hand drawing the long revolver from the hip holster; 2 the arm coming up; 3 the gun aimed level to the image right at shoulder height; 4 THE SHOT (the bullet leaves here): the gun level, the arm straight, a small kick; 5 the gun still raised; 6 lowering it back toward the idle stance (hands back on the hips). The sword stays on her back. The muzzle flash is an effect - do not draw it.` |
| `samira_attack_m.png`（普攻（近身挥刀）） | 6 帧：50 40 50 90 100 110 | 第 4 帧（tick 8） | 3 列 × 2 行，3072×1536 | 第 81 行 | `SWORD SLASH (basic attack in melee range), 6 frames: 1 the back hand reaching over her shoulder to the sword's hilt; 2 the greatsword drawn up over her head; 3 swung forward; 4 THE BLOW (the hit lands here): the blade swept down and forward across her front to the image right, the body lunging 1-2 squares; 5 the blade low in front; 6 the sword back across her back, toward the idle stance. The slash arc is an effect.` |
| `samira_skill.png`（Q 交火（开枪）） | 6 帧：60 60 90 90 80 100 | 第 3 帧（tick 7） | 3 列 × 2 行，3072×1536 | 第 81 行 | `FLAIR, GUN (Q at range), 6 frames: 1 both hands go to the holsters; 2 the long revolver drawn and spun; 3 THE SHOT (the bullet leaves here): the gun aimed level to the image right at shoulder height, the body turned side-on; 4 the gun kicked up; 5 the gun twirled; 6 back toward the idle stance. The muzzle flash and the tracer are effects.` |
| `samira_skill_m.png`（Q 交火（近身横斩）） | 6 帧：50 50 40 100 100 110 | 第 4 帧（tick 8） | 3 列 × 2 行，3072×1536 | 第 81 行 | `FLAIR, SWORD (Q in melee range, a wide slash), 6 frames: 1 the sword drawn from her back; 2 lifted high behind her; 3 a crouch, the sword swinging; 4 THE SLASH (it lands here): a low lunge, the greatsword swept out level and far to the image right; 5 the blade held out; 6 the sword back across her back, toward the idle stance. The slash arc is an effect.` |
| `samira_skill2.png`（E 狂飙接 W 锋旋（冲刺后旋转）） | 12 帧：50 50 67 90 90 90 90 90 90 90 90 100 | 第 4 帧（tick 10） | 4 列 × 3 行，4096×2304 | 第 81 行 | `WILD RUSH then BLADE WHIRL (E then W), 12 frames: 1-2 the dash: leaning low and far forward to the image right, the sword in hand trailing low behind; 3 landing on both feet; 4-11 THE SPIN (the first cut lands on 5, the second on 11): she spins on the spot, the greatsword held out level and swung all round her - in front, out to the image right, behind, out to the image left - a pistol in the other hand, the body turning with it (the head still the design's 3/4 head, never her back); 12 the sword back across her back, toward the idle stance. The dash's trail and the spinning blade's ring are effects.` |
| `samira_ult.png`（R 炼狱扳机（双枪旋转连射）） | 10 帧：150 184 184 184 184 184 184 184 184 380 | 第 2 帧（tick 9） | 4 列 × 3 行，4096×2304，最后 2 格空 | 第 81 行 | `INFERNO TRIGGER (R, a 2-second spin firing both guns), 10 frames: 1 both pistols drawn, the arms opening; 2-9 THE FIRING SPIN (the shots go out from 2): she turns on the spot with BOTH ARMS STRETCHED OUT to the sides, a pistol in each hand, the guns pointing out level - frame by frame the arms sweep round her (out to the right and left, one in front, one behind), the body turning with them, the sword slung on her back; 10 the guns lowered, back toward the idle stance. Muzzle flashes and bullets are effects.` |
| `samira_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left), the braid swinging; 2 recovering toward the idle stance. The design's legs.` |
| `samira_dead.png`（死亡（跪倒后倒下）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death: she staggers, drops to her knees and falls): 1 struck, she staggers back; 2-4 sinking to her knees, the head bowed; 5-6 tipping over; 7-8 lying on the ground, the sword fallen beside her; 7 and 8 the same pose. The head is the design's head turned with the body, never upside down. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、描边；长辫子接在后脑；
- [ ] 每帧大刀完整（深钢刀身、银刃口、金护手、红头）、该拿枪时枪在手里；两只手臂都在，拿武器的手看得见、不藏在身后；腿和造型图一样的材质和粗细；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `samira_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比、手和武器看不看得见），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；放技能时的身体换回待机的身体，手臂连武器整块转（rigkit），不画骨骼。
- 放进 `assets/source/native/`，`samira_cells.json` 用包里这份，`samira_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 11、普攻 tick 8、Q 交火 tick 7、Q 交火 tick 8、E 狂飙接 W 锋旋 tick 10、R 炼狱扳机 tick 9），量枪口和头像截取点；枪口火光、刀光按红方规则画进动作帧（samira_bake.json）；重跑模拟，做预览 GIF。
