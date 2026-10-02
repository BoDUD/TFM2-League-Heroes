# 蔚：只重画「移动」（跑步）（给 Codex 的提示词）

> 上一轮重画（`outputs/vi-strips-redo`）的其他 9 个动作已经采用、导入了，**只有移动要再画一次**。上一版跑步的身体直立、大步、后脚抬起都对，问题是**两只拳套只有待机的一半大**（量出来只有待机拳套面积的 47–50%），看起来像普通的小拳头，不像蔚的大海克斯拳套（`rejected/rejected_vi_run_small_fists.png`）。
>
> **这一轮只画 `vi_run.png`（8 帧）：**
> 1. 用生图整张画出来（附图顺序：`design/vi_design.png`、`now/vi_now_run.png`、`pose/lol_pose_run.png`），再对齐 8×8 网格、换成造型图色板、贴造型图的头（流程和上一轮一样）。
> 2. **两只拳套每帧都和造型图一样大**：每只约 6–8 格宽、连前臂外壳约 19 格长（`ref/vi_gauntlet_size.png`）。跑步时两只都**抬在胸前、往前伸**，像举着两块盾：近处那只往前下方，远处那只高一点也往前，拳头在胸口到腰带之间、在身体前面（照 `lol_side/lol_run_side.png`、`lol_side/lol_run_front.png`）。拳套会挡住大半个上身，这是对的。
> 3. 身体直立、大步、后脚往后踢到膝盖高、两腿交替（前 4 帧一步、后 4 帧另一步）——保持上一版做对的部分。腿和造型图一样粗、一样的颜色和靴子。
> 4. 格子、站位点、脚底线、头的位置都和上一轮一样（`vi_cells.json`、`guide/vi_guide_run.png`）；头每帧逐格贴造型图的头，上下起伏最多 1 格。
> 5. 交付放在 **`outputs/vi-run-redo/`**：`vi_run.png`（8 倍）、`logical/vi_run_1x.png`、`manifest.json`、`generation_prompts.json`，最后附 `HANDOFF.md`。

## 提示词（上一轮的通用提示词，[animation] 用下面这段）

[animation] =
`MOVE, 8 frames, one seamless loop of the run in the SECOND and THIRD images (0.84 s, 8 x 105 ms): the body UPRIGHT (no crouch), BOTH HUGE GAUNTLETS - each as big as in the FIRST image, about 6-8 squares wide and 19 squares long with the forearm housing - lifted in front of the chest like two shields: the near one pointing forward-down, the far one a little higher and also forward, the fists in front of the body between chest and belt height, covering most of the torso; LONG strides: the back foot kicked up behind to knee height, the front knee lifted; the legs ALTERNATE - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames, the boots planted on the ground line; the head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1. NOT small fists (the previous run drew the gauntlets at half size - rejected).`
[R] = 75，[grid] = 4 列 × 2 行，[size] = 3072×1408。

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

