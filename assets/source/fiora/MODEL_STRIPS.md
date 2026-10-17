# 无双剑姬 菲奥娜：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：B40**。Claude 按你交回的 B 版逐格读回（没有缩放模糊），压到 24 色、只留一圈描边，在脸以外删整行整列缩到 40 行；细剑剑身改成 1 格亮银线、两侧不描边；近侧眼睛上面两格浅灰改成睫毛黑、眼角白格改成深色瞳孔（用户选的）：`design/fiora_design.png`（放大 8 倍，1024×1024，62×40 格、25 色，鞋底在 y=792–799）。**造型图就是标准**，颜色、形状、头、脸、细剑一律照它。
> - **待机条已经做好**（`fiora_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/fiora_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。**细剑长度照造型图**（剑身约 20 格，护手之外），参考图的剑已经按它放大过。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。最好打成一个 zip 放在 outputs 里。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/fiora_palette.png`，或直接读 `design/fiora_design_1x.png`）。**先把眼睛的青色 `#18B4C8` 从色板里去掉**（它和宝石的蓝很近，一吸附就会跑到身上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/fiora_head_1x.png`：靛紫波波头、深红刘海、脸、眼睛、嘴和它们的描边；金色肩甲已去掉；在 128×128 画布上的范围 x 65–81、y 60–72）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡倒地的帧可以不贴）。头贴在白色高领和肩上，下巴下面不要露出一截脖子；移动循环各帧肩膀都在下巴下同一行。受击第 1 帧把眼睛改成闭眼（眼睛那一行各一段深色短线）。
5. **细剑**：剑身是一条 1 格粗的 `#E6E8F0` 直线、两侧不描边（造型图就是这样），长度和造型图一样；斜着的时候也是一格一格连着的直线，不断开、不弯。
6. 对位：每帧按 `fiora_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人连成一块（死亡里掉在地上的剑除外），握剑的手臂至少 3 格粗、金色护手包住拳头。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/fiora_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，鞋底第 99 行 | 每张动作图的第一张附图 |
| `design/fiora_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/fiora_head.png`、`fiora_head_1x.png` | 只有头（头发、刘海、脸），在画布上原来的位置 | 贴头 |
| `design/fiora_palette.png` | 造型图的全部 25 色（暗到亮） | 色板 |
| `fiora_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/fiora_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体和细剑的动作 |
| `guide/fiora_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `fiora_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/fiora_picture.png` | 用户选的设定图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref_melee.png`、`style/pack_quality_ref.png` | 团战经理2 原版近战英雄、本包女英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（40 格，头顶到鞋底），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 25 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑；细剑剑身不描边。
- **头每帧都是造型图的头**（波波头、深红刘海、脸、眼睛、嘴逐格一样），只平移或整体倾斜；青色 `#18B4C8` 只用在眼睛上；眼睛上没有白色方块。
- **细剑每帧都在**（死亡第 2 帧掉到地上之后，平躺在她前面的地上）：金色护手包住拳头，剑身 1 格粗 `#E6E8F0` 直线、不描边，长度照造型图；握在拳头里，不能断开、不能飘开、不能挡脸。
- **手和手臂**：握剑的是造型图里戴金色护臂的那只手（画面右边、伸向细剑的手臂），每一帧都照造型图的手来画——参考图里剑换到另一只手的地方，也照造型图；拳头至少 3×3 格，手臂从肩膀到拳头至少 3 格粗，不能画成 1–2 格的细线（在游戏里像"无影手"）；每帧整个人连成一块。
- **披风**：造型图的酒红外面、白色里子、金边和下角的蓝宝石，跟着动作在身后飘。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），剑尖、披风也不能低于它。只有死亡躺倒的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间有两膝交叉的帧），每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，看得到脸，不画背影。**只画角色**：剑光、刺击的风压、破绽标记、治疗光这些都是单独的特效，不要画。每个动作开始和结束都接近造型图的起手式。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/fiora_design.png`，第二张 `now/fiora_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `fiora_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, rapier and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms and the rapier from it.
The character: an elegant chibi duelist woman: a sleek dark indigo bob cut at the jaw with a broad crimson streak across the forehead, fair skin, teal eyes, a small red mouth; a white high collar and a white blouse-coat with gold piping; big curled gold pauldrons with sky-blue gems; a big gold armoured gauntlet on her sword arm; gold waist and hip plates; dark teal fitted leggings with gold stripes and teal heeled boots with gold trims; a cape behind her, wine-red outside, white inside with a gold border and a sky-blue gem at its point. Her weapon is a long thin rapier: a swept gold guard round her fist and a straight blade ONE square thick.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares tall from the top of the hair to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 25 colors of the FIRST image, no new colors: #030912 #1F1509 #0E0E28 #022539 #3F2A09 #5C0522 #222046 #003754 #730928 #014D70 #784C17 #383676 #AE173D #02728F #AE7225 #0189D8 #6D8E69 #C99631 #18B4C8 #80889C #C7A951 #F9C740 #FCD7BC #E6E8F0 #F2F2F6. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. The rapier's blade is a bare 1-square line of #E6E8F0 with NO outline along it, straight and unbroken, as long as in the FIRST image. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (hair, crimson streak, face, eyes, mouth) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play; it sits on the white collar and the shoulders with no neck showing. Her eyes are the FIRST image's eyes: teal #18B4C8 with a dark pupil and a dark lash row, NO white square on or above them; the teal appears ONLY in the eyes. The rapier is in every frame (until it falls in the death), held in the FIRST image's sword hand - the gold-gauntleted arm reaching toward the rapier - even where the THIRD image holds it in the other hand; the fist is at least 3x3 squares and the arm at least 3 squares thick from the shoulder to the fist, never a 1-2 square line; the whole figure is ONE connected piece in every frame. The cape keeps the FIRST image's colors and swings with the motion.
Feet line: in every cell the lowest row of her feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the rapier's tip, not the cape - because the game draws the health bar there (the lying frames of the death may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in fiora_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, her face always visible, never her back. Do not draw effects (sword trails, thrust waves, marks, glows) - only the character. Every animation starts and ends near the FIRST image's en-garde stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 120x112 squares (960x896 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the teal only in the eyes, no white square on the eyes, the rapier one straight 1-square line without outline, the sword arm at least 3 squares thick with the fist on the hilt, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `fiora_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2880×1792 | 第 97 行 | **已做好，不用画** |
| `fiora_run.png`（移动） | 8 × 114 | — | 4 列 × 2 行，3840×1792 | 第 97 行 | `MOVE, 8 frames, one seamless loop of League's walk in guard (0.91 s, 8 x 114 ms; the SECOND and THIRD images): she walks forward upright in her en-garde stance, the rapier held forward and a little up to the right in her gauntleted sword hand as in the FIRST image, the other arm back; the legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames; the cape swings behind her; her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `fiora_attack.png`（普攻） | 6 帧：60 60 50 70 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2880×1792 | 第 97 行 | `BASIC ATTACK, 6 frames, an overhead cut as in the THIRD image: 1 from the guard she lifts the rapier; 2 the rapier raised high over her head; 3 she swings it down over her head; 4 THE RELEASE (the hit lands here): the blade cuts down across the front of her to the right, her body stepping into it; 5 the follow-through, the blade low; 6 back toward the guard of the FIRST image. The blade never goes below the feet line.` |
| `fiora_attack_e.png`（夺命连刺的暴击） | 6 帧：60 60 50 70 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2880×1792 | 第 97 行 | `BLADEWORK, the critical thrust, 6 frames as in the THIRD image: 1 from the guard she draws the rapier back to her shoulder; 2 coiled, knees bent; 3 she springs forward; 4 THE RELEASE (the hit lands here): a long low LUNGE, the front knee bent far forward, the back leg straight, the rapier thrust straight out to the right at chest height; 5 holding the lunge; 6 back toward the guard.` |
| `fiora_skill.png`（Q 破空斩） | 6 帧：60 60 60 60 90 100 | 第 4 帧（tick 11） | 3 列 × 2 行，2880×1792 | 第 97 行 | `LUNGE, the dash and the stab, 6 frames as in the SECOND and THIRD images: 1 she crouches, the rapier pulled back; 2-3 she dives forward low along the ground, her body almost level, the rapier trailing behind her; 4 THE RELEASE (the stab lands here): she lands in a long lunge and thrusts the rapier straight out to the right at chest height; 5 holding the thrust; 6 back toward the guard. Her lowest point never goes below the feet line.` |
| `fiora_skill2.png`（W 劳伦特心眼刀） | 7 帧：250 250 250 80 80 80 80 | 第 4 帧（tick 45） | 4 列 × 2 行，3840×1792，最后 1 格空 | 第 97 行 | `RIPOSTE, 7 frames: 1 she snaps into a parry, knees bent, the rapier held level across the front of her body; 2-3 holding the parry guard (these three frames last 250 ms each; the rapier crosses in front of her chest, her face stays visible); 4 THE RELEASE (the stab leaves here): she lunges and stabs forward, the rapier thrust out LEVEL to the right at chest height; 5-6 holding the stab, the cape flying behind her; 7 back toward the guard. In the stab frames the rapier stays level (horizontal) and above the feet line - the THIRD image's blade points down only because of its camera.` |
| `fiora_ult.png`（R 无双挑战（致敬）） | 5 帧：80 80 100 120 120 | 第 3 帧（tick 10） | 3 列 × 2 行，2880×1792，最后 1 格空 | 第 97 行 | `GRAND CHALLENGE, a duelist's salute, 5 frames as in the THIRD image: 1 from the guard she raises the rapier; 2 the rapier slants up; 3 THE SALUTE: the rapier held straight UP in front of her face, the guard at her chin; 4 holding the salute; 5 she swings the rapier down and forward, back toward the guard.` |
| `fiora_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1920×896 | 第 97 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back, eyes squeezed shut (two short dark lines on the eyes' rows); 2 recovering toward the guard.` |
| `fiora_dead.png`（死亡） | 8 帧：100 100 100 120 120 120 150 400 | — | 4 列 × 2 行，3840×1792 | 第 97 行 | `DEATH, 8 frames as in the THIRD image: 1 struck; 2 the rapier falls from her hand and lies flat on the ground in front of her (from here it stays there, apart from her body, the only loose piece allowed); 3-4 she staggers, bent over, clutching her side; 5 she falls backward; 6 falling; 7-8 lying on her back on the ground line, the cape spread. Frames 7-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、同一行，眼睛上没有白格；
- [ ] 青色 `#18B4C8` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 细剑每帧都在（死亡第 2 帧起躺在地上），剑身一条 1 格粗、不描边、不断开的直线，长度照造型图；
- [ ] 握剑手臂至少 3 格粗、拳头包在金色护手里；每帧整个人连成一块（死亡里地上的剑除外）；
- [ ] 脚底线以下没有任何像素（只有死亡躺倒的帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `fiora_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、青色只在眼睛上、每帧连成一块、剑身直线、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`fiora_cells.json` 用包里这份，`fiora_idle.png` 用包里已做好的那张。
- `import_native.py --hero fiora`：ORDER 待机一张图 + BOB 呼吸（分界线选在小腿，不切过披风下摆和靴口），EYES = `#18B4C8`，补描边（COMPLETE，1 格的剑身不补），NECK。
- 按出手帧核对技能数据的时机（普攻和暴击 tick 10、Q 刺 tick 11、W 刺 tick 45、R 致敬 tick 10），量特效挂点和头像截取点、选人卡片 banpick_center，重跑模拟，做预览 GIF。
