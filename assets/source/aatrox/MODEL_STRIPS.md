# 剑魔：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/aatrox_design.png`（放大 8 倍，1024×1024；翅尖到脚底 40 行，39 格宽，15 色；脚底在第 99 行，两脚中间在第 64 列）。**造型图就是标准**：带角的钢青色头盔、盔下的阴影脸和两只红眼睛、血红胸甲和发光的橙色符文、钢青色肩甲和护手、近侧的钢手和远侧的红色手臂、钢青色护腿和爪形铁靴、**半收在背后的深紫色翅膀**、**大剑**，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`aatrox_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/aatrox_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、剑和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染，**原版的大翅膀已经去掉**，只有大招留着）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（瘦长的身体、大头盔、40 行高）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡低头时整个头跟着身体转），**不画背影**；③ 原版的 Q 会高高跳起、转身，我们 Q1、Q2 站在原地挥剑，只有 Q3 小跳（离地 2–3 格）；④ **翅膀**：the two demon wings stay HALF-FOLDED behind his shoulders exactly as in the design (they sway 1 square with the body), never spread wide - except in the ult, where they open；⑤ 原版 W 没有动作，照表里的文字画（远侧红手向前甩出，剑留在近侧手里）。
> - **大剑（最重要的标志）**：the GREATSWORD is in every frame, whole and STRAIGHT (never bent, broken, shortened or melted into the body): the design's own blade (design/aatrox_sword.png) - dark plum with blood-red barbed edges, the glowing orange eye by the guard, the two-pronged hooked tip - only moved and turned with the hands。剑长约 19–20 格、4–5 格粗，和造型图一样大；砍中的那一帧剑要**直**，剑身平的或斜着砍到地面，不要弯。
> - **腿**：in every standing frame (attacks, Q1, Q2, W, R, hit) the legs are the design's own legs square for square - the same stance, the same clawed boots, toes out; only Q3's leap lifts the same legs off the ground, the run alternates them and the death kneels and falls。
> - 出招方向：**挥剑、砍、甩链子都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧的剑尖或手的位置）和 `generation_prompts.json`，最好打成一个 zip（`aatrox_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**不要把细节比方块还小的高清图压缩下来**（上一轮造型的剑就是这样被缩歪的）。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/aatrox_palette.png`，或直接读 `design/aatrox_design_1x.png`）。
4. **贴头**：把造型图的头（`design/aatrox_head_1x.png` 里不透明的格子：角、头盔、阴影脸和红眼睛、下巴；在 128×128 画布上的范围 x 57–67、y 61–72，**按图里的形状贴，不是整个方框**——翅膀和肩甲不属于头）原样贴进每一帧头的位置（只平移；死亡低头时整个头跟着转）。这样每帧的脸都和造型图一模一样。头下面直接接肩甲和胸甲，不要拉出一截脖子。
5. **剑**：剑的样子照 `design/aatrox_sword_1x.png`（画布上 x 37–58、y 85–95）；剑朝向和造型图一样（往左下）的帧可以原样平移贴上，举起、横扫的帧照它的样子画直。
6. 对位：每帧按 `aatrox_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/aatrox_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/aatrox_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头、贴剑 |
| `design/aatrox_head.png`、`_1x.png` | 要贴进每一帧的头（角、头盔、阴影脸、红眼睛、下巴） | 贴头 |
| `design/aatrox_sword.png`、`_1x.png` | 大剑（剑身、倒刺、护手和橙色的眼、两叉剑尖） | 剑的样子 |
| `design/aatrox_palette.png` | 造型图的全部 15 色（暗到亮） | 色板 |
| `aatrox_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/aatrox_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置（原版翅膀已去掉，大招除外） | 第三张附图：手臂、剑和身体的动作 |
| `guide/aatrox_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `aatrox_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/aatrox_picture.png`、`refs/aatrox_draft_codex.png` | 造型来源的原画和你画的原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref_warrior.png`、`tfm2_style_ref_swordsman.png`、`pack_native_ref.png` | 团战经理2 原版重甲、剑士英雄和我们包里的德莱厄斯、贾克斯、锐雯、魔腾，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（翅尖到脚底 40 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 15 种颜色**，不加新颜色；明暗照定稿（钢甲的亮边、胸口的橙色符文跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边（`#0A0408`），描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **手和手臂**：近侧是钢青色护手，远侧是红色手臂和红爪；手臂 2–3 格粗、手是实心的拳头或张开的爪；**不要 1 像素的黑细棍、不要飘着的手**，握剑的手和剑柄连在一起。
- **大剑**：the GREATSWORD is in every frame, whole and STRAIGHT (never bent, broken, shortened or melted into the body): the design's own blade (design/aatrox_sword.png) - dark plum with blood-red barbed edges, the glowing orange eye by the guard, the two-pronged hooked tip - only moved and turned with the hands。
- **翅膀**：the two demon wings stay HALF-FOLDED behind his shoulders exactly as in the design (they sway 1 square with the body), never spread wide - except in the ult, where they open。
- **腿**：in every standing frame (attacks, Q1, Q2, W, R, hit) the legs are the design's own legs square for square - the same stance, the same clawed boots, toes out; only Q3's leap lifts the same legs off the ground, the run alternates them and the death kneels and falls。
- **头每帧都是造型图的头**（角、头盔、阴影脸、两只红眼睛逐格一样），只平移（死亡低头时整个转）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），剑尖、翅尖都在它上面。只有死亡时掉在地上的剑可以贴着脚底线。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：剑光、砍痕、冲击波、地裂、锁链、红色光环、血都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，**不要洋红**，会吃掉紫色的翅膀和剑身）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/aatrox_design.png`，第二张 `now/aatrox_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `aatrox_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, armour, wings, greatsword and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same horned steel-teal helm with the face in shadow and two red eyes, the blood-red chest armour with the glowing orange rune, the steel-teal pauldrons, the steel near gauntlet and the red far arm, the steel-teal greaves and clawed boots, the half-folded dark plum wings behind his shoulders, the greatsword, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the blow, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (its big wings left out) - copy the motion of the arms, the sword and the body from it, but keep the FIRST image's proportions (a lean body, a big horned helm, the greatsword's size); never draw him from the back or upside down.
The character: Aatrox (a demon warrior in steel-teal armour with a horned helm, the face hidden in shadow with two glowing red eyes, a blood-red chest with a glowing orange rune, one red demonic arm, half-folded dark plum bat wings with crimson edges, and a huge straight greatsword of dark plum with blood-red barbed edges, a glowing orange eye at the guard and a two-pronged hooked tip).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the wing tip to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 15 colors of the FIRST image, no new colors: #0A0408 #270D28 #181F2B #4B0827 #1F2A38 #263647 #42224C #8F0E2B #3B586B #BF1630 #68407A #F2323B #5B8498 #FF7A2A #95C3D4. ONE outline: a 1-square near-black outline (#0A0408) around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading - the lit steel edges and the orange rune move with the pose; no dithering, no noise, no random specks added. Hands are solid fists or open claws at the ends of arms 2-3 squares wide - never 1-pixel black sticks or floating hands; the hands that hold the sword touch its grip.
The greatsword is his signature: the GREATSWORD is in every frame, whole and STRAIGHT (never bent, broken, shortened or melted into the body): the design's own blade (design/aatrox_sword.png) - dark plum with blood-red barbed edges, the glowing orange eye by the guard, the two-pronged hooked tip - only moved and turned with the hands.
The wings: the two demon wings stay HALF-FOLDED behind his shoulders exactly as in the design (they sway 1 square with the body), never spread wide - except in the ult, where they open.
The legs: in every standing frame (attacks, Q1, Q2, W, R, hit) the legs are the design's own legs square for square - the same stance, the same clawed boots, toes out; only Q3's leap lifts the same legs off the ground, the run alternates them and the death kneels and falls.
The head (the horns, the helm, the shadow face with both red eyes, the chin) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns down with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the pauldrons and the chest - no neck.
Feet line: in every cell his lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the sword, not a wing tip - because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in aatrox_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every swing, slam and throw goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash trails, sword glow, impact flashes, shockwaves, cracks, dust, chains, the red aura, blood) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x96 squares (896x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green, never magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both red eyes visible, the greatsword whole and straight in every frame, the hands holding it, the wings half-folded (spread only in the ult), the idle's legs in every standing frame, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `aatrox_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1536 | 第 81 行 | **已做好，不用画** |
| `aatrox_run.png`（移动（剑拖在身后）） | 8 × 125 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop (8 x 125 ms, League's run): a heavy, menacing stride, leaning a little forward; the greatsword held low in the near hand and trailing down-left behind him, its tip above the ground; the far red arm swings with the step; the half-folded wings bob behind his shoulders; in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same steel-teal greaves and clawed boots; the body bobs 1 square down and up over each half; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `aatrox_attack.png`（普攻（横扫）） | 6 帧：70 65 65 80 80 73 | 第 4 帧（tick 12） | 3 列 × 2 行，2688×1536 | 第 81 行 | `BASIC ATTACK, 6 frames (League's attack: a sweeping slash): 1 the idle stance, the greatsword drawn a little further back down-left; 2 the sword swung back, the shoulders turning away; 3 the sword swinging forward low; 4 THE HIT (the blow lands here): the greatsword swept forward to the right, the blade level at hip height pointing right, the body leaning into it; 5 the follow-through, the blade still forward; 6 lifting back toward the idle stance. The slash trail and the hit are effects - do not draw them.` |
| `aatrox_attack_p.png`（被动强化攻击（赐死剑气）） | 6 × 100 | 第 4 帧（tick 18） | 3 列 × 2 行，2688×1536 | 第 81 行 | `EMPOWERED ATTACK (his passive, Deathbringer Stance: a heavier strike), 6 frames: 1 he lifts the greatsword, the far red claw open; 2 the sword pulled far back low behind him, the body twisting (a big wind-up); 3 the wind-up at its fullest; 4 THE HIT (the blow lands here): a huge drive forward - the greatsword thrust out to the right, the blade level at hip height, the body leaning into it; 5 holding the blow; 6 recovering toward the idle stance. The slash and the blood are effects.` |
| `aatrox_skill.png`（Q 第一段（举剑下劈）） | 7 帧：90 90 90 97 100 100 100 | 第 5 帧（tick 22） | 4 列 × 2 行，3584×1536，最后 1 格空 | 第 81 行 | `THE DARKIN BLADE - FIRST CAST (an overhead slam), 7 frames: 1 he gathers, the sword drawn back; 2 the greatsword swung up behind his shoulder; 3 the greatsword raised high overhead in both hands, the blade pointing up and back; 4 swinging down in front of him; 5 THE SLAM (the blow lands here): the blade smashed down in front of him to the right, straight, its tip on the feet line ahead of him; 6 holding the slam; 7 lifting back toward the idle stance. The impact flash and the cracks are effects.` |
| `aatrox_q2.png`（Q 第二段（横扫）） | 7 帧：90 90 90 97 100 100 100 | 第 5 帧（tick 22） | 4 列 × 2 行，3584×1536，最后 1 格空 | 第 81 行 | `THE DARKIN BLADE - SECOND CAST (a wide sweep), 7 frames: 1 he turns his shoulders, the sword drawn back low behind him; 2 the greatsword raised up behind his far shoulder; 3 the wind-up at its fullest, the blade high behind; 4 swinging across in front; 5 THE SWEEP (the blow lands here): the greatsword swept across to the right at hip height, the blade level pointing right; 6 the follow-through; 7 back toward the idle stance. The arc of the sweep is an effect.` |
| `aatrox_q3.png`（Q 第三段（跃起下砸）） | 7 帧：100 100 100 100 100 100 67 | 第 5 帧（tick 24） | 4 列 × 2 行，3584×1536，最后 1 格空 | 第 81 行 | `THE DARKIN BLADE - THIRD CAST (a leaping slam), 7 frames: 1 he crouches a little, the sword raised; 2 he leaps (2-3 squares off the ground, the SAME legs lifted), the greatsword raised overhead in both hands; 3 the top of the leap, the blade high; 4 coming down, the blade swinging down in front; 5 THE SLAM (it lands here): back on the ground on his idle legs, the greatsword smashed straight down in front of him, its tip on the feet line ahead; 6 holding; 7 back toward the idle stance. The crater, the shockwave and the dust are effects.` |
| `aatrox_skill2.png`（W 恶火束链（甩出锁链）） | 6 帧：80 80 73 100 90 77 | 第 4 帧（tick 14） | 3 列 × 2 行，2688×1536 | 第 81 行 | `INFERNAL CHAINS (W: he hurls a chain of darkness with his free hand), 6 frames: 1 the idle stance; 2 the far red arm draws back toward his shoulder, the claw opening; 3 the claw drawn back fully; 4 THE THROW (the chain leaves here): the far red arm thrust straight out to the right at chest height, the claw wide open, palm forward; 5 holding the throw; 6 back to the idle stance. The greatsword stays in his near hand, down-left as in the idle. The chain and its glow are effects - do not draw them.` |
| `aatrox_ult.png`（R 大灭（变身：展翼咆哮）） | 6 帧：90 90 100 130 130 127 | — | 3 列 × 2 行，2688×1536 | 第 81 行 | `WORLD ENDER (R: his transformation), 6 frames: 1 he crouches, gathering; 2 he rises, arms spreading, the chest rune flaring; 3 the WINGS OPEN; 4 THE ROAR: both wings spread WIDE and high (the only strip where they spread: each about as long as he is tall, the same plum membrane, crimson edges and steel bone tips), his head thrown back a little, the arms out, the greatsword held out low in the near hand; 5 the roar goes on, the wings fully spread; 6 settling, the wings folding back toward half-folded. The red aura and the glow are effects - do not draw them.` |
| `aatrox_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1792×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his body and helm pushed back 1-2 squares (to the left), the wings and the sword swaying; 2 recovering toward the idle stance.` |
| `aatrox_dead.png`（死亡） | 8 帧：100 100 110 110 120 150 300 500 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `DEATH, 8 frames (League's death): 1 struck, he staggers back; 2 the greatsword drops from his hand, its tip hitting the ground; 3 he falls to one knee; 4-6 kneeling, slumping forward, the wings drooping; 7-8 he collapses forward in front of his sword (the same pose in 7 and 8); the helm stays visible from the 3/4 front (turned down, never upside down). The fallen sword lies on the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡低头时整个转），两只红眼睛都在；
- [ ] **大剑每帧都在、完整、笔直**，样子和造型图一样（倒刺、两叉剑尖、护手的橙色眼睛）；握剑的手是实心的、连着剑柄；
- [ ] 翅膀半收在背后（只有大招张开）；站着出招的帧腿和待机一模一样；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交叉迈步、颜色一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点、bbox 和出手帧的剑尖位置都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `aatrox_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、剑是否完整笔直、零散黑格、每帧面积和待机比），不在网格上的重新取样；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`aatrox_cells.json` 用包里这份，`aatrox_idle.png` 用包里已做好的那张。
- `import_native.py --hero aatrox`：ORDER 待机一张图 + BOB 呼吸（缝选在护腿的直段），COMPLETE + CLEAN 补描边、清黑边，NECK 检查头盔每帧在肩甲上同一行。
- 按出手帧核对技能数据的时机（普攻 tick 12、被动强化攻击 tick 18、Q1 tick 22、Q2 tick 22、Q3 tick 24、W tick 14），量剑尖和红爪的位置定特效挂点（Q 的砍痕、W 锁链的 y_offset），量头像截取点，重跑模拟，做预览 GIF。
