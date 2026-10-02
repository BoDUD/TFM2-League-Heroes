# 蔚：动作条重画（第 2 步重做，给 Codex 的提示词）

> **上一轮被用户否掉了，请全部重画（10 张动作条）。** 上一轮交付（`outputs/vi-strips`）是用 Python 把造型图拆成部件、旋转拼起来的（manifest 写着 "approved-pixel-parts, hand-authored rig poses"，生图调用 0 次）。用户看了说：「跑动姿势好怪 完全不像LOL里面的蔚」「感觉上面 下面全是错的」「实在太差劲了 让codex重画吧」。
>
> **这一轮的要求：**
> 1. **用生图把每一张动作条整张画出来**（每张一次生图，三张附图照下面的通用提示词），再按「建议流程」对齐 8×8 网格、换成造型图色板、贴造型图的头。**身体、手臂、拳套、腿必须是画出来的**，不能用脚本把造型图的部件切下来旋转、平移、拼装（只有头可以从造型图逐格贴）。
> 2. **移动（最重要）**：照 `lol_side/lol_run_side.png`（侧面）和 `lol_side/lol_run_front.png`（游戏镜头）：身体**直立**，不蹲、不前趴；**两只大拳套抬在胸前**，近处那只往前下方伸、远处那只高一点也往前，像举着两块盾在跑，拳头在胸口到腰带的高度、在身体前面；**大步跑**，后面那只脚往后踢到膝盖高，前腿膝盖抬起，两腿在身体下面交替（前 4 帧一步、后 4 帧另一步）。上一轮的错误（`rejected/rejected_vi_run.png`）：蹲低前倾、两只拳套连成一根横杆伸在腰前、腿短还岔开——**不要这样画**。
> 3. **E 透体之劲**：照 `lol_side/lol_e_side.png`：第 1–2 帧远处的拳头高举过头；第 3–5 帧**向右深弓步**，前膝弯、后腿伸直，**近处的大拳套往右前下方砸到膝盖高度**。上一轮第 4–5 帧画成了正面蹲下、两只拳头垂在两边（`rejected/rejected_vi_attack_e.png`）——**不要这样画**。
> 4. **拳套每帧都和造型图一样大**（上一轮好几帧只有待机的 60–80%）；**腿每帧都和造型图一样粗、一样的颜色和靴子**。
> 5. 交付放在 **`outputs/vi-strips-redo/`**（文件名不变：`vi_<动作>.png` 等），最后附 `HANDOFF.md`；`generation_prompts.json` 里写清楚每张用了哪次生图。

## 新增附图

| 文件 | 内容 |
|---|---|
| `lol_side/lol_run_side.png` | 英雄联盟的跑步，侧面（同样 8 帧）：身体直立、两只拳套举在胸前、大步 |
| `lol_side/lol_run_front.png` | 同样 8 帧，游戏镜头（3/4 正面朝右） |
| `lol_side/lol_e_side.png` | 英雄联盟的 E，侧面：高举 → 深弓步往前下方砸 |
| `rejected/rejected_vi_run.png`、`rejected/rejected_vi_attack_e.png` | **上一轮被否掉的图，不要这样画** |

下面是原来的提示词包（通用提示词、每张的帧数和动作说明都不变，只是 `[animation]` 里移动和 E 的说明更新了），其余规则照旧。

---

# 皮城执法官 蔚：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：A40**（你上一轮的简洁原稿 A——双拳垂在两侧——Claude 按它自己的格子逐格读回，删整行整列缩到 40 行，脸和眼睛一格没删）：`design/vi_design.png`（放大 8 倍，1024×1024，27×40 格、32 色，鞋底在 y=792–799）。**造型图就是标准**，颜色、形状、头、护目镜、脸、两只大拳套、腿和靴子一律照它。
> - **待机条已经做好**（`vi_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/vi_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；渲染里的头已经转成待机的朝向，头巨大是 Q 版放大，**头一律照造型图**；渲染里的拳套比造型图小，**拳套的大小和样子一律照造型图**）。
> - **腿**：上一个英雄（卡莎）交回来以后，技能、大招、死亡里的腿和待机不一样，是一帧帧补的。这次每张动作图的腿都用造型图的腿（同样粗细、同样的深蓝腿甲和黑靴，两条腿一样粗），只摆姿势。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。都放在 **`outputs/vi-strips-redo/`** 文件夹里，最好再打成一个 zip（`vi_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**读图时不要用品红抠背景**——她的粉色头发会被一起抠掉；用透明背景，或者纯绿 `#00FF00` 背景。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/vi_palette.png`，或直接读 `design/vi_design_1x.png`）。**先把眼睛的颜色从色板里去掉**（虹膜蓝 `#006CFB`、`#0067F8`、深蓝 `#012D84`、`#012D82` 和两种眼白，和拳套水晶的蓝容易混），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/vi_head_1x.png`：粉色短发、额头上的护目镜、脸、眉毛、两只眼睛、嘴，到下巴为止；在 128×128 画布上的范围 x 54–73、y 60–74）原样贴进每一帧头的位置，只平移；身体倾斜时整体倾斜；倒地的死亡帧可以不贴。贴的头的下巴下面，围巾从眼睛最下一行往下第 4 行开始，每一帧都一样（不能把头压进身体，也不要拉出一截脖子）。受击第 1 帧把眼睛改成闭眼（眼睛那一行各一段深色短线）。
5. **拳套**：两只大拳套每一帧都在，大小和样子照造型图（金色外壳、钢灰指节块、蓝水晶），和手臂连在一起不留缺口；出拳的那只就是同一只大拳套，伸直的手臂至少 3 格粗（含描边）。
6. **腿**：每一帧都用造型图的两条腿（同样粗细、深蓝腿甲、黑色厚底靴），只按动作摆姿势；两条腿一样粗，颜色和待机一样。
7. 对位：每帧按 `vi_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
8. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人（连同两只拳套）连成一块，眼睛颜色只在眼睛上，腿和待机一样。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/vi_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，鞋底第 99 行 | 每张动作图的第一张附图 |
| `design/vi_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/vi_head.png`、`vi_head_1x.png` | 只有头（头发、护目镜、脸到下巴），在画布上原来的位置 | 贴头 |
| `design/vi_palette.png` | 造型图的全部 32 色（暗到亮） | 色板 |
| `vi_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/vi_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体、手臂和腿的动作 |
| `guide/vi_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `vi_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/vi_picture.png` | 用户选的原画 B（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref_melee.png`、`style/pack_quality_ref.png` | 团战经理2 原版近战英雄、本包英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（40 格，护目镜顶到鞋底），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 32 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（头发、护目镜、眉毛、眼睛、嘴逐格一样），只平移或整体倾斜；眼睛的颜色（虹膜蓝 `#006CFB`、`#0067F8`）只用在眼睛上。
- **拳套每帧都在**，两只一样，大小和样子照造型图，和手臂连着；伸直出拳的手臂至少 3 格粗。
- **腿每帧都是造型图的腿**：同样粗细、同样的深蓝腿甲和黑靴，两条腿一样粗，只摆姿势。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面）。只有死亡跪地、倒地的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间有两膝交叉的帧），每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。R 冲锋的循环同样两腿交替。
- 3/4 正面朝右，看得到脸，不画背影。**只画角色**：冲击波、冲刺拖尾、地裂、护盾、光环都是单独的特效，不要画。每个动作开始和结束都接近造型图的待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，**不要用品红或粉色**）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/vi_design.png`，第二张 `now/vi_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `vi_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, the head with the goggles, the face, the two huge gauntlets, the legs and boots and the pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the blow, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms and the legs from it (its head is oversized and turned like the idle on purpose, and its gauntlets are smaller than the FIRST image's: the head and the gauntlets' size and look always come from the FIRST image).
The character: a chibi young woman brawler: short hot-pink hair with dark goggles pushed up on her head, a fair face with blue eyes, a red scarf, a steel-blue breastplate, dark navy-violet leg armour, heavy black boots, and two HUGE mechanical gauntlets - gold housings, steel-grey knuckle blocks and a glowing blue crystal on the back of each hand. She fights only with the gauntlets.
Task: DRAW (image generation, not by assembling cut-out parts of the FIRST image) every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares tall from the goggles to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 32 colors of the FIRST image, no new colors: #200C05 #1F1E2F #2A272C #47241A #2C1E3F #012D82 #012D84 #3C2B55 #643826 #3D435B #A3152B #144296 #824726 #9D5D28 #57607C #D62C32 #005DE7 #0067F8 #006CFB #E22467 #007CFC #CE8827 #DC9A2C #01C6FD #8591AE #DA9666 #FB5D99 #FCC846 #FCC9A2 #F4E9DA #FCF2E4 #FBF2E6. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (the pink hair with the goggles down to the chin, the face, the brows, the eyes and the mouth) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. Under the chin keep the FIRST image's rows: the scarf starts 4 rows under the eyes' lowest row in every frame; never sink the head into the body. The eye blues #006CFB and #0067F8 and the eyes' dark blues appear ONLY in the eyes (the crystals keep their own blues).
GAUNTLETS (her signature): both huge gauntlets are in every frame, the same size and look as the FIRST image (gold housing, steel-grey knuckle blocks, the blue crystal), each joined to its arm with no gap; a punching fist is the same big gauntlet, never shrunk to a small hand.
LEGS (most important, an earlier hero's legs had to be fixed frame by frame): in EVERY frame of EVERY action - attacks, skills, the ult, the hit, the death included - her legs are the FIRST image's legs: the same thickness (both legs equally thick), the same dark navy-violet leg armour and the same heavy boots, only posed (bent, striding, lunging, kneeling); never thinner, longer, shorter or in other colours.
The whole figure with both gauntlets is ONE connected piece in every frame; an extended arm is at least 3 squares thick from the shoulder to the gauntlet, never a 1-2 square line.
Feet line: in every cell the lowest row of her boots is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there (the kneeling and lying frames of the death may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in vi_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, her face always visible, never her back. Do not draw effects (shockwaves, dash trails, ground cracks, shields, glows around her) - only the character. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x88 squares (768x704 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid pure green #00FF00 - never magenta or pink, her hair is pink). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the eye blues only in the eyes, both gauntlets in every frame at the FIRST image's size and joined to the arms, the legs as thick and in the same colors as the FIRST image in every frame, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `vi_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1408 | 第 75 行 | **已做好，不用画** |
| `vi_run.png`（移动） | 8 × 105 | — | 4 列 × 2 行，3072×1408 | 第 75 行 | `MOVE, 8 frames, one seamless loop of the run in the SECOND and THIRD images (0.84 s, 8 x 105 ms): she runs forward leaning a little, the two big gauntlets held in front of her at chest-to-belly height and swinging a little with the steps (never dropped to the ground); the legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames, the boots planted flat on the ground line; the short pink hair bounces a little; her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1. Like League's run (side view lol_run_side.png): the body UPRIGHT (no crouch, no forward slump); BOTH huge gauntlets lifted in front of the chest like two shields - the near one pointing forward-down, the far one a little higher, the fists in front of the body between chest and belt height; LONG strides: the back foot kicked up behind to knee height, the front knee lifted. NOT a horizontal bar of both gauntlets at the waist, NOT short splayed legs (that was the rejected strip).` |
| `vi_attack.png`（普攻（直拳）） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1408 | 第 75 行 | `BASIC ATTACK, a straight punch with her NEAR gauntlet, 6 frames as in the THIRD image: 1 from the idle she raises both fists into a boxer's guard; 2 the near fist drawn back at her side; 3 THE PUNCH (the blow lands here): she steps in and drives the near gauntlet straight forward to the right at chest height, the arm extended; 4 the fist still out; 5 pulling it back; 6 back toward the idle of the FIRST image.` |
| `vi_attack_e.png`（E 透体之劲（高举砸拳）） | 6 帧：60 60 50 80 80 70 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1408 | 第 75 行 | `RELENTLESS FORCE, an overhead hammer punch, 6 frames as in the THIRD image: 1 from the idle she winds up; 2 the far gauntlet raised high over her head; 3 she lunges forward; 4 THE SLAM (the blow lands here): a deep lunge to the right, the front knee bent, the gauntlet smashing down-forward in front of her at knee height, the other fist pulled back; 5 holding the lunge; 6 rising back toward the idle. Draw NO shockwave or blast (separate effect). Like League's E (side view lol_e_side.png): frames 1-2 the far fist raised high over the head; frames 3-5 a DEEP LUNGE to the right (front knee bent, back leg stretched behind), the near huge gauntlet smashing down-forward at knee height in front of her. NOT a frontal squat with both fists hanging at her sides (that was the rejected strip).` |
| `vi_skill.png`（Q 强能冲拳·蓄力） | 4 × 125 | — | 4 列 × 1 行，3072×704 | 第 75 行 | `VAULT BREAKER, the charge, 4 frames as in the THIRD image (she stays in place for 0.5 s): 1 she drops into a low stance; 2 the near gauntlet pulled far back behind her hip, the body coiled, the other fist forward; 3-4 holding the coil, straining (a slight shake: the gauntlet 1 square further back in frame 4). The crystal of the drawn-back gauntlet may glow brighter (only its own blue/cyan squares). Draw NO charge effect.` |
| `vi_skill_dash.png`（Q 强能冲拳·冲刺） | 3 帧：90 90 87 | 第 1 帧（tick 0） | 3 列 × 1 行，2304×704 | 第 75 行 | `VAULT BREAKER, the dash, 3 frames as in the THIRD image (held while she rockets forward): a low, forward-leaning lunge to the right, the near gauntlet thrust straight out in front of her at chest height, the other fist back, the legs trailing; frames 1-3 almost the same pose (small changes in the trailing leg). Keep every frame inside its cell and above the feet line (the game moves her); draw NO trail (separate effect).` |
| `vi_ult.png`（R 天霸横空烈轰·起步） | 2 帧：66 67 | 第 2 帧（tick 4） | 2 列 × 1 行，1536×704 | 第 75 行 | `CEASE AND DESIST, the launch, 2 frames as in the THIRD image: 1 she plants her feet and raises the far gauntlet; 2 crouching, ready to spring forward.` |
| `vi_ult_dash.png`（R 天霸横空烈轰·冲锋） | 6 × 125 | — | 3 列 × 2 行，2304×1408 | 第 75 行 | `CEASE AND DESIST, the charge, 6 frames, a loop as in the THIRD image (held while she rushes at the target): a fast forward sprint leaning hard to the right, the far gauntlet cocked back over her shoulder, the near gauntlet low in front, long strides (the legs alternate like the run). Keep it inside the cell and above the feet line; draw NO trail (separate effect).` |
| `vi_ult_slam.png`（R 天霸横空烈轰·上勾拳砸地） | 5 帧：60 70 70 70 63 | 第 2 帧（tick 4） | 3 列 × 2 行，2304×1408，最后 1 格空 | 第 75 行 | `CEASE AND DESIST, the slam, 5 frames as in the THIRD image: 1 arriving low, both fists close; 2 THE UPPERCUT (the knock-up lands here): she drives the near gauntlet up high above her head; 3 the fist coming down from above; 4 crouched low after the slam, both gauntlets near the ground in front; 5 rising back toward the idle. Draw NO ground crack (separate effect).` |
| `vi_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×704 | 第 75 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back 1 square, eyes squeezed shut (two short dark lines on the eyes' rows), the gauntlets jolting with her; 2 recovering toward the idle.` |
| `vi_dead.png`（死亡） | 8 帧：100 100 110 120 130 150 200 500 | — | 4 列 × 2 行，3072×1408 | 第 75 行 | `DEATH, 8 frames as in the THIRD image: 1-2 struck, she staggers back, the gauntlets sagging; 3-4 she drops to one knee, then both knees; 5-6 kneeling and slumping forward, the gauntlets on the ground; 7-8 lying face down on the ground, the two gauntlets beside her. Frames 5-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、同一行；
- [ ] 眼睛的蓝（`#006CFB`、`#0067F8`、`#012D84`、`#012D82`）只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 两只拳套每帧都在、和造型图一样大、和手臂连着；出拳的手臂至少 3 格粗；每帧整个人连成一块；
- [ ] **每一帧的两条腿都和造型图一样粗、一样的颜色和靴子**（逐帧和 `vi_idle.png` 比）；
- [ ] 脚底线以下没有任何像素（只有死亡跪地、倒地的帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 身体、手臂、拳套、腿是生图画出来的，不是把造型图部件拼装的（只有头是贴的）；移动和 E 和 `lol_side/` 的英雄联盟动作一致，不像 `rejected/`；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `vi_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛的蓝只在眼睛上、每帧连成一块、两只拳套都在、每帧面积和待机比），不在网格上的重新取样（不用品红抠图键）；眼睛不对的帧换回造型图的头；每帧量眼睛到围巾的行数，和造型图（4）对照；**每帧的腿和待机的腿逐帧对比**（粗细、颜色、靴子），不一样的用待机自己的腿摆上（`legs_onto` 的做法）。
- 放进 `assets/source/native/`，`vi_cells.json` 用包里这份，`vi_idle.png` 用包里已做好的那张。
- `import_native.py --hero vi`：ORDER 待机一张图 + BOB 呼吸（分界线选在腰下的腿甲直段），EYES = `#006CFB`，补描边（COMPLETE），NECK，走路 STEP 起伏。
- 按出手帧核对技能数据的时机（普攻 tick 7、E tick 10、R 上勾拳 tick 4），量出手点挂点（拳头）、头像截取点、选人卡片 banpick_center，重跑模拟，做预览 GIF。
