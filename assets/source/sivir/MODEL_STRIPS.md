# 希维尔：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/sivir_design.png`（放大 8 倍，1024×1024；头发顶到脚底 40 格，51 格宽，23 色；脚底在第 99 行，两脚中间在第 64 列）。它是你第二轮第 2 稿按格子读回、删到 40 行的版本。**造型图就是标准**：黑长发、金头冠和青宝石、薄荷青的眼睛、米白围巾、深蓝短上衣、金肩甲、金护臂和棕手套、金腰带和深蓝腰布、紫灰护腿、金护膝、棕靴、**展开的金色十字刃（中间圆环镂空）**，颜色、明暗、身材比例，每一帧都照它，只改姿势。
> - **待机条已经做好**（`sivir_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/sivir_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、十字刃和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（苗条、四肢细长，头约占三分之一）——**不要画胖**，用户否掉过把她画矮画粗的版本；② 头是贴上去的（见下），英雄联盟里她会低头、扭头，我们**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡倒地时整个头跟着身体转），**不画背影**；③ 英雄联盟的十字刃待机时是合起来的长条，我们**一律画成造型图那样展开的四刃十字**；④ Q 原版掷出后会跳一下，我们只在第 3 帧小跳一格，脚落回地面。
> - **十字刃（最重要的标志）**：the CROSSBLADE (her big gold four-bladed throwing cross with its see-through ring) is in her near hand in every frame - open, whole, the four hooked blades and the ring clear, never bent, shrunk or melted into the body - EXCEPT where the animation line says it is thrown (attack frames 4-5, the whole skill_wait strip, skill frame 4 after the release): then her near hand is EMPTY, an open hand at the end of the arm。出手那一帧十字刃中心不要高过站位点（蓝十字）8 格以上（Q 10 格），否则飞出去的刃在游戏里看起来是歪的。
> - 出招方向：**掷刃都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧十字刃中心的位置）和 `generation_prompts.json`，**生图原稿也一起交（不要缩放或重采样过的）**，最好打成一个 zip（`sivir_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。画出来的方块比造型图小（人比造型图大）就重画，**不要缩小**（缩小会把四肢压短压粗）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，读成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/sivir_palette.png`，或直接读 `design/sivir_design_1x.png`）。**先把眼睛专用的薄荷青 `#4FE6D2` 从色板里去掉**（吸附时会跑到宝石上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/sivir_head_1x.png` 里不透明的格子：头发、头冠、脸，到下巴为止；在 128×128 画布上的范围 x 53–75、y 60–72，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡倒地时整个头跟着转）。这样每帧的脸都和造型图一模一样。头下面接围巾，不要拉出一截脖子；先擦掉自己画的头再贴，头周围不要留下多余的头发或描边。
5. 对位：每帧按 `sivir_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/sivir_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/sivir_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/sivir_head.png`、`_1x.png` | 要贴进每一帧的头（头发、头冠、脸，到下巴） | 贴头 |
| `design/sivir_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `sivir_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/sivir_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、十字刃和身体的动作 |
| `guide/sivir_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `sivir_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/sivir_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref.png`、`tfm2_style_ref_undead.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（头发顶到脚底 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；明暗照定稿（金色的高光、十字刃的亮边跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格、不要横穿身体的黑线**。
- **身材**：照造型图，苗条、四肢细长（大腿连描边 4 格左右、小腿 3 格、手臂 2–3 格）；**不要把腿画短画粗**；膝盖、小腿、靴子三段都要有。
- **手**：手臂 2–3 格粗、手是棕色实心的手套；**不要 1 像素的黑细棍、不要飘着的手**，握刃的手和十字刃连在一起。
- **十字刃**：the CROSSBLADE (her big gold four-bladed throwing cross with its see-through ring) is in her near hand in every frame - open, whole, the four hooked blades and the ring clear, never bent, shrunk or melted into the body - EXCEPT where the animation line says it is thrown (attack frames 4-5, the whole skill_wait strip, skill frame 4 after the release): then her near hand is EMPTY, an open hand at the end of the arm。
- **头每帧都是造型图的头**（头发、头冠、脸逐格一样，只平移；死亡倒地时整个转）；薄荷青 `#4FE6D2` 只用在眼睛上。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），十字刃、头发都在它上面。只有死亡掉在地上的十字刃可以贴着脚底线。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），掷刃朝图的右边，**不画背影、不画倒立**。**只画角色**：飞出去的十字刃、拖尾、护盾泡泡、光环、加速线都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/sivir_design.png`，第二张 `now/sivir_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `sivir_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, costume, hands, the crossblade and the pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same long black hair, gold tiara with its teal gem, mint eyes, cream scarf, navy crop top, gold pauldron, gold vambraces and brown gloves, gold belt and navy loincloth, slate-purple leggings, gold knee guards, brown boots, the open gold crossblade with its ring, the same shading and the same SLIM proportions. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the throw, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the crossblade and the body from it, but keep the FIRST image's proportions (a slim athletic body with long thin limbs, the head about a third of the height) and its OPEN crossblade; never draw her from the back or upside down.
The character: Sivir (an athletic desert warrior woman: long black hair, a gold tiara with a teal gem, a cream scarf, a navy crop top, gold armour, a navy loincloth, slate-purple leggings, gold knee guards, brown boots, and a big gold four-bladed crossblade with a ring in its middle).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the top of the hair to the soles in the idle crouch), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. Draw at that size directly; never draw bigger and shrink (shrinking makes the limbs short and fat).
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #14101A #1B2236 #3E2416 #1A2440 #2E2438 #5C3410 #2C3A58 #0C5E58 #2C3E66 #4E3F5E #7A4A28 #A0302A #9A5434 #A8691E #18A890 #D58A5C #E8A830 #4FE6D2 #CBBFA4 #F4B888 #FFE27A #FFF4C0 #F6F0DC. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares, never a black line across the body. Copy the FIRST image's shading - the bright gold and the crossblade's pale edges move with the pose; no dithering, no noise, no random specks added. Hands are solid brown gloves at the ends of arms 2-3 squares wide - never 1-pixel black sticks or floating hands.
The crossblade is her signature: the CROSSBLADE (her big gold four-bladed throwing cross with its see-through ring) is in her near hand in every frame - open, whole, the four hooked blades and the ring clear, never bent, shrunk or melted into the body - EXCEPT where the animation line says it is thrown (attack frames 4-5, the whole skill_wait strip, skill frame 4 after the release): then her near hand is EMPTY, an open hand at the end of the arm. In the throw frames its centre is no higher than the animation line says.
The head (the hair, the tiara and the face with both eyes, down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the scarf - no neck. The mint #4FE6D2 appears ONLY in the eyes.
Feet line: in every cell her lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the crossblade, not the hair - because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in sivir_cells.json). In the move loop her head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every throw goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (the flying crossblade, trails, the shield bubble, auras, speed lines) - only the character. Every animation starts and ends near the FIRST image's crouch.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x80 squares (768x640 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, the mint #4FE6D2 only in the eyes, the crossblade whole and open wherever it is held (an empty hand where it is thrown), hands attached, slim legs with knees, shins and boots, no loose pieces, no stray black squares or lines, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `sivir_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1280 | 第 67 行 | **已做好，不用画** |
| `sivir_run.png`（移动（小跑，十字刃拿在身后胯边，交叉迈步）） | 8 × 125 | — | 4 列 × 2 行，3072×1280 | 第 67 行 | `MOVE, 8 frames, one seamless loop (8 x 125 ms, League's run): an athletic jog, upright, leaning a little forward; the crossblade held open at her near (back) hip, it bounces 1 square with the step; the far arm swings with the stride, the glove loose; the long black hair streams behind her; the steps: in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same colours (slate-purple leggings, gold knee guards, brown boots); the body bobs 1 square down and up over each half; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `sivir_attack.png`（普攻（掷出十字刃、空手、再接回）） | 6 帧：50 50 70 70 80 80 | 第 3 帧（tick 6） | 3 列 × 2 行，2304×1280 | 第 67 行 | `BASIC ATTACK, 6 frames (League's attack: she hurls the crossblade and it comes back): 1 the idle crouch, the near arm drawing the crossblade back behind her hip; 2 the wind-up, the crossblade swung back low behind her, the body twisting; 3 THE THROW (the blade leaves here): the near arm sweeps forward to the right at waist-to-chest height, the crossblade still at the hand, open, about to leave - its centre NO HIGHER than 8 squares above the standing point (the blue cross of the guide); 4 the follow-through, the near hand EMPTY and stretched out to the right; 5 the near hand empty, coming back; 6 the catch: the crossblade back in the near hand at her hip, the idle crouch. The flying blade is an effect - do not draw it in frames 4-5.` |
| `sivir_skill.png`（Q 回旋之刃·掷出（蓄力、转身、掷出）） | 4 帧：50 50 50 60 | 第 4 帧（tick 9） | 4 列 × 1 行，3072×640 | 第 67 行 | `BOOMERANG BLADE (Q, the wind-up and the throw), 4 frames (League's spell1, 0.2 s): 1 from the idle crouch she draws the crossblade back and down behind her near hip; 2 she twists her body back, the crossblade far behind her, the far arm forward for balance; 3 she swings the crossblade forward and up, the whole body turning to the right, a small hop on the far leg; 4 THE THROW (it leaves here): the near arm stretched out to the right at shoulder height, the crossblade just leaving the open hand, its centre NO HIGHER than 10 squares above the standing point. The flying crossblade after the throw is an effect.` |
| `sivir_skill_wait.png`（Q 等待（空手低蹲循环，刃在飞）） | 2 × 150 | — | 2 列 × 1 行，1536×640 | 第 67 行 | `BOOMERANG BLADE (Q, while the blade flies - a loop, 2 frames x 150 ms): she stands in a low ready crouch like the idle, feet planted, her near hand EMPTY and held open a little forward at her hip (no crossblade anywhere), the far arm forward, eyes to the right; frame 2 breathes 1 square down. Frame 2 flows into frame 1.` |
| `sivir_skill_catch.png`（Q 接刃（举手接住、收回胯边）） | 3 × 60 | — | 3 列 × 1 行，2304×640 | 第 67 行 | `BOOMERANG BLADE (Q, the catch), 3 frames (League's spell1 catch): 1 the near hand raised out to the right at shoulder height, open, the returning crossblade arriving at the fingers (drawn open and whole, touching the hand); 2 she catches it and swings it down to her near hip, the body turning back; 3 the idle crouch with the crossblade at her hip.` |
| `sivir_skill2.png`（E 法术护盾（十字刃立在身前当盾）） | 4 帧：60 80 100 100 | 第 2 帧（tick 4） | 4 列 × 1 行，3072×640 | 第 67 行 | `SPELL SHIELD (E), 4 frames (League's spell3, 0.33 s): 1 from the idle crouch she straightens a little; 2 THE SHIELD (it rises here): she raises the crossblade in front of her body, held upright and open beside her near shoulder like a shield, the far hand open toward the right; 3 holding the guard, the hair lifting; 4 back toward the idle crouch. The shield bubble is an effect - do not draw it.` |
| `sivir_ult.png`（R 狩猎（高举十字刃号令）） | 5 帧：80 80 100 120 120 | 第 3 帧（tick 10） | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 67 行 | `ON THE HUNT (R, the war cry), 5 frames (League's spell4, 0.5 s): 1 she crouches, the crossblade low; 2 she rises and lifts the crossblade; 3 THE CRY (the rally here): she stands tall with the crossblade raised high above her head in the near hand, open and spinning (the same blade, tilted), the far arm flung out, her mouth open; 4 holding the pose, the hair streaming; 5 back down to the idle crouch. The golden aura and the speed lines are effects - do not draw them.` |
| `sivir_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×640 | 第 67 行 | `HIT, 2 frames: 1 jolted back by a blow: her body and head pushed back 1-2 squares (to the left), the hair swaying, the crossblade still held; 2 recovering toward the idle crouch.` |
| `sivir_dead.png`（死亡（向后倒地，十字刃掉在身边）） | 8 帧：100 100 110 110 120 150 300 500 | — | 4 列 × 2 行，3072×1280 | 第 67 行 | `DEATH, 8 frames (League's death): 1 struck, she reels back; 2 she falls backward, the crossblade slipping from her hand; 3 falling, the crossblade dropping to the ground beside her; 4 she hits the ground; 5-8 lying on her back (or side), still, the long hair spread out, the crossblade lying flat on the ground next to her (the same pose from frame 6 on). The face stays visible (turned with the body, never upside down). Frames 4-8 lie on the feet line; the dropped crossblade lies on it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高、一样苗条；头就是造型图的头（逐格一样，只平移；死亡时整个转），两只眼睛都在；
- [ ] 薄荷青 `#4FE6D2` 只出现在眼睛上：头部以外 0 个像素；
- [ ] **十字刃**：拿着的帧里完整、展开、圆环镂空；掷出的帧手是空的；出手帧中心不高过站位点 8 格（Q 10 格）；
- [ ] 腿：膝盖、小腿、靴子三段都有，不粗不短；脚底线以下没有任何像素；黑边干净，没有零散黑格和横穿的黑线；
- [ ] 没有背影、没有倒立；掷刃都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交叉迈步、颜色一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿也交；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `sivir_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、薄荷青只在眼睛上、连通块、四肢粗细、十字刃是否完整、零散黑格、每帧面积和待机比），不在网格上的从生图原稿按格子重新取；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`sivir_cells.json` 用包里这份，`sivir_idle.png` 用包里已做好的那张。
- `import_native.py --hero sivir`：ORDER 待机一张图 + BOB 呼吸，EYES = `#4FE6D2`，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 6、Q tick 9、E tick 4、R tick 10），量十字刃出手高度定 `y_offset`（高过站位点 8 px 以上会歪），量特效挂点和头像截取点，重跑模拟，做预览 GIF。
