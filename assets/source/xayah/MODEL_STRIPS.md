# 霞：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/xayah_design.png`（放大 8 倍，1024×1024；耳尖到脚底 44 行，34 格宽（连斗篷），28 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生图原稿（`refs/xayah_draft_codex.png`）按格子读回、按比例缩到 44 行的版本，用户说「用这个就行」（只修了头顶的黑线）。**造型图就是标准**：紫色兜帽、两只白尖粉红羽毛耳朵、粉红头发、金色眼睛、鸟头骨护肩和橙黄羽毛、绳子、深红胸衣和前摆、深蓝条纹绑腿、鸟爪脚、紫蓝深红橙金的羽毛大斗篷、手里的紫红羽刃，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`xayah_idle.png`），不用画（游戏里的呼吸动画由导入脚本自动做）；它也告诉你造型图在格子里多大、站在哪里。
> - **跑步用骨架 + 皮囊**（`run/` 里，见下面「跑步」一节），不照英雄联盟的跑步条画。
> - 其余 7 张动作图（普攻、Q、E、W、R、受击、死亡）按下面的表画：帧数、每帧时长、出手帧和站位照 `now/xayah_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、斗篷和身体的动势照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（Q 版大头、44 行高）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**——英雄联盟的 Q、E、R 里她会空翻转身，**我们一律画正面，不画背影**，只借手臂和斗篷的动势；③ **腿**：in every standing frame (idle, attack, W, hit) she stands on the design's OWN legs square for square - the same navy-and-mauve striped leg wraps, taloned bird feet, stance and width as the design, never spread wider, never crossed, never shorter; the shoulders, the arms and the cloak move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares back or forward, never the upper body alone over still legs); only the run steps, Q and E crouch and spring as League's do, and R leaps into the air, with the design's leg materials, knees bent, hips joined；④ 武器：her weapons are FEATHER BLADES: 1 square wide, 4-5 squares long, violet-magenta (the design's blade colours), held between the fingers, two of them fanned out in the near hand (image right) in every frame as in the design; when she throws, the blade leaves the hand toward the right and the hand is empty for that frame and the next; they are never dropped except in the death；⑤ 斗篷：her FEATHER CLOAK hangs from both shoulders in EVERY frame - violet-blue feathers on top, crimson below, orange-gold tips - and trails behind her (image left); it swings and flares with the motion (spread wide like a wing in W, E and R) but keeps the design's colours and feather shapes; the bird skull on the near shoulder and the rope across the chest stay on her；⑥ 手臂：the arms are the design's arms: slim pale arms with crimson bracers, 2 squares wide, the same thickness as in the design in every frame - never thicker, never 1-pixel sticks, never floating hands。
> - 出招方向：**羽刃和匕首都朝图的右边**（游戏里朝左时会整张镜像）；R 是朝右下方掷出。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/xayah_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/xayah_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/xayah-strips/`：8 张 `xayah_<动作>.png`（跑步那张是 3×2 格的 64×64 小格）、`HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`xayah_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/xayah_palette.png`，或直接读 `design/xayah_design_1x.png`）。
4. **贴头**：把造型图的头（`design/xayah_head_1x.png` 里不透明的格子：两只耳朵、兜帽、头发和脸，到下巴为止，不含下面的鸟头骨；在 128×128 画布上的范围 x 55–76、y 56–74，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发、耳朵或描边。
5. 对位：每帧按 `xayah_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/xayah_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/xayah_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/xayah_head.png`、`_1x.png` | 要贴进每一帧的头（耳朵、兜帽、头发、脸和眼睛） | 贴头 |
| `design/xayah_palette.png` | 造型图的全部 28 色（暗到亮） | 色板 |
| `xayah_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `run/1_动作骨架_oppi跑步.png`、`run/2_角色_霞定稿.png`、`run/PROMPT_RUN.md` | 跑步的骨架（oppi 的薇恩跑步，6 帧）、皮囊（我们的定稿，同样 64×64 格）和短提示词 | 跑步 |
| `now/xayah_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、斗篷和身体的动势 |
| `guide/xayah_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `xayah_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/xayah_picture.png`、`refs/xayah_draft_codex.png` | 用户选的原画 A 和你的生图原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（耳尖到脚底 44 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 28 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every standing frame (idle, attack, W, hit) she stands on the design's OWN legs square for square - the same navy-and-mauve striped leg wraps, taloned bird feet, stance and width as the design, never spread wider, never crossed, never shorter; the shoulders, the arms and the cloak move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares back or forward, never the upper body alone over still legs); only the run steps, Q and E crouch and spring as League's do, and R leaps into the air, with the design's leg materials, knees bent, hips joined。
- **羽刃**：her weapons are FEATHER BLADES: 1 square wide, 4-5 squares long, violet-magenta (the design's blade colours), held between the fingers, two of them fanned out in the near hand (image right) in every frame as in the design; when she throws, the blade leaves the hand toward the right and the hand is empty for that frame and the next; they are never dropped except in the death。
- **斗篷**：her FEATHER CLOAK hangs from both shoulders in EVERY frame - violet-blue feathers on top, crimson below, orange-gold tips - and trails behind her (image left); it swings and flares with the motion (spread wide like a wing in W, E and R) but keeps the design's colours and feather shapes; the bird skull on the near shoulder and the rope across the chest stay on her。
- **手臂**：the arms are the design's arms: slim pale arms with crimson bracers, 2 squares wide, the same thickness as in the design in every frame - never thicker, never 1-pixel sticks, never floating hands。
- **头每帧都是造型图的头**（耳朵、兜帽、头发、脸和眼睛逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）；斗篷的羽尖也不能低于脚底线。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色、她的斗篷和手里的羽刃**：飞出去的羽刃、匕首雨、收回的羽毛、刀刃风暴都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 跑步：骨架 + 皮囊（`run/` 里）

oppi 包里没有霞，跑步用同样是女射手的 oppi 薇恩的跑步当动作骨架（6 帧 × 135 毫秒，0.81 秒一圈，英雄联盟的霞是 0.87 秒），它的待机和我们的造型一样是 44 行高，所以 1:1 换皮。上传顺序和提示词见 `run/PROMPT_RUN.md`。交回 `xayah_run.png`：和图1一样 3×2 格、每格 64×64 方块；头每帧贴造型图的头，头相对脚的横向位置每帧不变；两腿交替，上下起伏不超过 1 格；斗篷每帧都在、往身后飘。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/xayah_design.png`，第二张 `now/xayah_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `xayah_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, cloak, blades and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same violet hood with its silver-blue trim, the two long crimson-pink feathered ears with white tips, the crimson-pink hair, the golden eyes, the bird skull with the orange-gold tuft on the near shoulder, the rope, the crimson bodice and tabard, the navy-and-mauve striped leg wraps, the taloned bird feet, the big feather cloak (violet-blue on top, crimson below, orange-gold tips), the violet-magenta feather blades in her fingers, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the cloak and the body from it, but keep the FIRST image's proportions (a big chibi head, 44 squares tall) and, in every standing frame, the FIRST image's own legs; where the original turns her round, keep her facing the viewer - never draw her from the back or upside down.
The character: Xayah, the Rebel (a slim bird-woman marksman: a violet hood, long feathered ears, crimson-pink hair, a huge feather cloak, feather blades as weapons).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (44 squares from the ears' tips to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 28 colors of the FIRST image, no new colors: #0B040E #1A1236 #44041C #5F0A3D #74082F #28255F #753D27 #3B2782 #A71238 #761481 #B84313 #714759 #4E2EAA #B21590 #E06E0B #E91F52 #CF880B #986471 #D7416A #F02D71 #6E71C0 #F7A313 #E89C86 #C5AB9E #969FDD #FAC6AF #FBC9D6 #F6E7E8. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every standing frame (idle, attack, W, hit) she stands on the design's OWN legs square for square - the same navy-and-mauve striped leg wraps, taloned bird feet, stance and width as the design, never spread wider, never crossed, never shorter; the shoulders, the arms and the cloak move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares back or forward, never the upper body alone over still legs); only the run steps, Q and E crouch and spring as League's do, and R leaps into the air, with the design's leg materials, knees bent, hips joined.
The blades: her weapons are FEATHER BLADES: 1 square wide, 4-5 squares long, violet-magenta (the design's blade colours), held between the fingers, two of them fanned out in the near hand (image right) in every frame as in the design; when she throws, the blade leaves the hand toward the right and the hand is empty for that frame and the next; they are never dropped except in the death.
The cloak: her FEATHER CLOAK hangs from both shoulders in EVERY frame - violet-blue feathers on top, crimson below, orange-gold tips - and trails behind her (image left); it swings and flares with the motion (spread wide like a wing in W, E and R) but keeps the design's colours and feather shapes; the bird skull on the near shoulder and the rope across the chest stay on her.
The arms: the arms are the design's arms: slim pale arms with crimson bracers, 2 squares wide, the same thickness as in the design in every frame - never thicker, never 1-pixel sticks, never floating hands.
The head (both ears, the hood, the hair, the face and the eyes, down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair, ear or outline is left beside it.
Feet line: in every cell her soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there (only in R she is in the air above it). Her place across the cell follows the SECOND image (each frame's standing point is in xayah_cells.json).
3/4 front view like the FIRST image; every throw goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (flying blades, the dagger rain, returning feathers, the blade storm) - only the character, her cloak and the blades in her hands. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the cloak, the skull and the blades (unless just thrown) in every frame, both arms, the standing frames on the FIRST image's own legs, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、斗篷、身体的方向和姿势照图1，但一律是 3/4 正面朝右，不画背影；站着的动作腿用图2自己的腿。
3. 长相、配色、细节全部换成图2：紫色兜帽、两只白尖粉红羽毛耳朵、粉红头发、金色眼睛、鸟头骨护肩、深红胸衣和前摆、深蓝条纹绑腿、鸟爪脚、紫蓝深红橙金的羽毛大斗篷、手里的紫红羽刃。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `xayah_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 80 行 | **已做好，不用画** |
| `xayah_run.png`（跑步（骨架换皮）） | 8 × 109 | — | 4 列 × 2 行，4096×1536 | 第 80 行 | `RUN: drawn by skin swap - see the section 「跑步：骨架 + 皮囊」 (oppi's 6-frame run as the skeleton, not this League strip). The League strip here is only for the cloak's swing.` |
| `xayah_attack.png`（普攻（甩羽刃）） | 6 帧：70 70 80 70 60 50 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×1536 | 第 80 行 | `BASIC ATTACK (a flung blade), 6 frames: 1 the near arm draws back across her body, a blade between the fingers; 2 the arm cocked behind, the cloak swinging; 3 THE THROW (the blade leaves here): the near arm flung out straight to the right at chest height, the hand open, both arms spread wide like League's, the cloak flaring out behind; 4 the follow-through, the arm still out; 5 the arm coming back, a new blade in the fingers; 6 back toward the idle stance. The flying blade is an effect - do not draw it. Legs: the design's legs.` |
| `xayah_skill.png`（Q 双刃（跃起双手掷出）） | 4 帧：70 70 80 80 | 第 3 帧（tick 8） | 4 列 × 1 行，4096×768 | 第 80 行 | `DOUBLE DAGGERS (Q), 4 frames, League's springy throw kept FRONT-facing (League flips her round; we never show her back): 1 both arms raised high above her head, a blade fanned in each hand, the knees bending; 2 she springs up a little (the whole figure 2-3 squares up), the arms crossing in front of her chest, the cloak whirling out behind; 3 THE THROW (both daggers leave here): both arms swept out to the right and down, hands open, the cloak spread; 4 landing back toward the idle stance. The daggers are effects.` |
| `xayah_skill_e.png`（E 倒钩（张臂召回羽毛）） | 4 帧：80 80 90 83 | 第 1 帧（tick 0） | 4 列 × 1 行，4096×768 | 第 80 行 | `BLADECALLER (E: she calls her feathers back), 4 frames, FRONT-facing: 1 THE CALL: both arms flung wide to the sides, palms open, the cloak spread like wings (the feathers start flying back now); 2 a quick crouch, the arms pulling in toward her chest as if catching; 3 still low, the hands at her chest catching the returning blades, the cloak folding in; 4 rising back toward the idle stance. The returning feathers are effects.` |
| `xayah_skill2.png`（W 致死羽衣（转身甩斗篷）） | 4 × 100 | 第 1 帧（tick 0） | 4 列 × 1 行，4096×768 | 第 80 行 | `DEADLY PLUMAGE (W: a storm of blades round her), 4 frames: 1 THE CAST: a twirl - the near arm sweeps round in front of her, the cloak swinging out wide behind; 2 the cloak at its widest, flaring like a wing, the arms out; 3 the cloak settling, a blade in each hand at her sides; 4 back toward the idle stance. The blade storm is an effect. Legs: the design's legs (a small turn of the shoulders only).` |
| `xayah_ult.png`（R 暴风羽刃（跃起、俯掷匕首雨）） | 8 帧：120 130 150 200 200 150 120 97 | 第 6 帧（tick 48） | 4 列 × 2 行，4096×1536 | 第 80 行 | `FEATHERSTORM (R), 8 frames, front-facing: 1 a deep crouch, the cloak spread wide; 2-3 she leaps straight up (the whole figure up as in the SECOND image, never out of the cell), the cloak streaming down like wings, the legs tucked; 4-5 high in the air, the arms raised with blades fanned in both hands; 6 THE RAIN (the daggers leave here): both arms thrown forward and down to the right, hands open, the cloak spread wide; 7 dropping down; 8 landed, back toward the idle stance. The dagger rain is an effect.` |
| `xayah_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 80 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left), the cloak swinging; 2 recovering toward the idle stance. The design's legs.` |
| `xayah_dead.png`（死亡（向后倒地）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 80 行 | `DEATH, 8 frames (League's death: she falls back): 1-2 struck, she staggers back, the head thrown back, a blade slipping from her fingers; 3-4 falling back, the cloak spreading on the ground; 5-6 lying on her back on the ground, the cloak spread under her like broken wings (still the design's head, the face seen from the side or above, never upside down); 7-8 lying still, 7 and 8 the same pose. A dropped blade lies on the ground beside her. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样（跑步和 `run/1_动作骨架_oppi跑步.png` 一样），帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、耳朵、描边；
- [ ] 每帧都有斗篷、鸟头骨和两只手臂；手里有羽刃（刚掷出那一两帧除外）；站着的动作是造型图自己的腿（逐格一样），手臂和造型图一样粗；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `xayah_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`xayah_cells.json` 用包里这份（跑步按 oppi 的 64×64 格另记），`xayah_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边，手里的羽刃进 WEAPON_CARRY（呼吸时不被压弯）。
- 按出手帧核对技能数据的时机（普攻 tick 8、Q tick 8、R tick 48），量出手那只手的位置定弹道的出手点（y_offset），量头像截取点，重跑模拟，做预览 GIF。
