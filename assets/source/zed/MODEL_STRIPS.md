# 劫：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/zed_design.png`（放大 8 倍，1024×1024）：背后刃饰齿尖到脚底 40 行，27 格宽，19 色；脚底在第 99 行，两脚中间在第 64 列。这张是在你上一轮生图稿（`refs/zed_draft_codex.png`）的基础上逐格读回、整行整列删到 40 行的，**造型图就是标准**：封闭枪灰头盔、金色中脊和金眉、两道红眼缝、深红兜帽、两肩青铜金边肩甲、背后多齿银色刃饰、胸前银 V、深红前摆（金边、骨色尖刺）、藏青裤、黑钢护胫和尖头甲靴、两只金护臂、每腕两根银刃。颜色、明暗每一帧都照它，只改姿势。
> - **待机条已经做好**（`zed_idle.png`），不用画（游戏里的待机呼吸由我们的工具自动生成）；它也告诉你造型图在格子里多大、站在哪里。
> - 其余 8 张动作图（包括跑步）按下面的表画：帧数、每帧时长、出手帧和站位照 `now/zed_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **跑步**：两条腿一定要前后交替、膝盖交叉，两条腿颜色一样（以前好几个英雄跑步是平行走路、或者一条腿变了颜色，被退回过）。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头大、手脚短，英雄联盟的手脚更长，不要照）；② 头（深红兜帽 + 封闭头盔 + 金脊金眉 + 红眼缝 + 面甲）是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**，**不画背影**（英雄联盟 Q 的第 2–3 帧是背影，不要照）；③ **腿**：in every STANDING frame (attack 1-2 and 5-6, W, E, hit) he stands on the design's OWN legs square for square: navy-black baggy trousers, the tall black-steel greaves and the pointed armoured boots with their steel-blue highlights, the same place and width as the design, never spread, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the LUNGING, CROUCHING and KNEELING frames (attack 3-4, Q, R, death) the legs follow League's pose (a long step forward, bent low, kneeling) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body；④ 装备：the crimson hood over the shoulders, the bronze-and-gold pauldrons on both shoulders, the silver V plates on the dark chest, the dark sash belt, the long crimson tabard with its gold borders and bone-tan hem spikes hanging in front of the hips, and the big spiky silver blade ornament on his back (its curved prongs rising above and behind both shoulders) stay in every frame and move with the body；⑤ 手臂：each forearm is the design's arm with the big ornate GOLD bracer and its silver hooked spurs, and from each wrist TWO long straight SILVER blades (each 1 square wide with a white highlight, a square apart, as long as in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; the four wrist blades never lost。
> - 出招方向：**刺、扔、斩、突进都朝图的右边**（游戏里朝左时会整张镜像）。
> - **死亡照英雄联盟**：单膝跪地，再向前扑倒趴在地上（见表），**不画倒立**。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/zed_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/zed_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**（以前用脚本拼的木板手臂、火柴腿都被退回了）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/zed-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`zed_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/zed_palette.png`，或直接读 `design/zed_design_1x.png`）。眼缝的红（#F70209）**只用在眼缝上**。
4. **贴头**：把造型图的头（`design/zed_head_1x.png` 里不透明的格子：深红兜帽、封闭头盔、金脊金眉、两道红眼缝、面甲；在 128×128 画布上的范围 x 59–71、y 64–77，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡趴下的几帧整块转 90°）。贴之前先擦掉你自己画的头和兜帽，不要在头旁边留下多余的兜帽、头盔或描边。**头下面要接上肩甲和胸口**，不要留出空隙或长出一截脖子；背后刃饰的银齿从头盔后面伸出来，跟着身体走。
5. 对位：每帧按 `zed_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/zed_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/zed_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/zed_head.png`、`_1x.png` | 要贴进每一帧的头（兜帽、头盔、金脊金眉、眼缝、面甲） | 贴头 |
| `design/zed_palette.png` | 造型图的全部 19 色（暗到亮） | 色板 |
| `zed_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/zed_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/zed_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `zed_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/zed_picture.png`、`refs/zed_draft_codex.png` | 用户选的原画 A 和你上一轮的生图稿（长相参考；比例、大小和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 19 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every STANDING frame (attack 1-2 and 5-6, W, E, hit) he stands on the design's OWN legs square for square: navy-black baggy trousers, the tall black-steel greaves and the pointed armoured boots with their steel-blue highlights, the same place and width as the design, never spread, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the LUNGING, CROUCHING and KNEELING frames (attack 3-4, Q, R, death) the legs follow League's pose (a long step forward, bent low, kneeling) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body。
- **装备**：the crimson hood over the shoulders, the bronze-and-gold pauldrons on both shoulders, the silver V plates on the dark chest, the dark sash belt, the long crimson tabard with its gold borders and bone-tan hem spikes hanging in front of the hips, and the big spiky silver blade ornament on his back (its curved prongs rising above and behind both shoulders) stay in every frame and move with the body。
- **手臂**：each forearm is the design's arm with the big ornate GOLD bracer and its silver hooked spurs, and from each wrist TWO long straight SILVER blades (each 1 square wide with a white highlight, a square apart, as long as in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; the four wrist blades never lost。
- **头每帧都是造型图的头**（兜帽、头盔、金脊金眉、两道红眼缝、面甲逐格一样），只平移（死亡趴下时整块转 90°）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：刀光、手里剑、影子、黑烟、斩击圈都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（8 张都用这一段，只替换中括号）

每张附三张图：第一张 `design/zed_design.png`，第二张 `now/zed_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `zed_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, gear, blades and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the closed gunmetal helmet with the gold crest and gold brows, the two red eye slits and the barred face plate, the crimson hood, the bronze-and-gold pauldrons, the spiky silver blade ornament on his back, the silver V on the dark chest, the dark sash, the long crimson tabard with gold borders and bone hem spikes, the navy trousers, the black-steel greaves and pointed boots, the gold bracers with two long silver blades on each wrist, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the blades and the body from it, but keep the FIRST image's proportions (big head, short limbs - not the long limbs of the 3D model) and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Zed, the Master of Shadows (an armoured ninja assassin with a closed helmet, a crimson hood and two blades on each wrist).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the ornament's tip to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 19 colors of the FIRST image, no new colors: #020206 #73011C #292A3E #95001F #363955 #424462 #C80823 #785634 #F70209 #5A5D80 #B0722E #686B8B #E39B33 #8991B1 #FBBB40 #A3ABC6 #FCCD5E #D7DEF0 #E6EBF8. The eye red #F70209 only on the eye slits. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every STANDING frame (attack 1-2 and 5-6, W, E, hit) he stands on the design's OWN legs square for square: navy-black baggy trousers, the tall black-steel greaves and the pointed armoured boots with their steel-blue highlights, the same place and width as the design, never spread, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the LUNGING, CROUCHING and KNEELING frames (attack 3-4, Q, R, death) the legs follow League's pose (a long step forward, bent low, kneeling) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body.
Gear: the crimson hood over the shoulders, the bronze-and-gold pauldrons on both shoulders, the silver V plates on the dark chest, the dark sash belt, the long crimson tabard with its gold borders and bone-tan hem spikes hanging in front of the hips, and the big spiky silver blade ornament on his back (its curved prongs rising above and behind both shoulders) stay in every frame and move with the body.
The arms: each forearm is the design's arm with the big ornate GOLD bracer and its silver hooked spurs, and from each wrist TWO long straight SILVER blades (each 1 square wide with a white highlight, a square apart, as long as in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; the four wrist blades never lost.
The head (the crimson hood, the closed helmet with its gold crest and brows, the two red eye slits and the face plate) is COPIED from the FIRST image in every frame, square for square, and only moved (turned a quarter only while he lies dead); never redraw, squash or tilt it otherwise, or it flickers when the frames play. Erase your own head and hood before pasting it, so no extra hood, helmet or outline is left beside it; the hood's lower edge meets the pauldrons and the chest - no gap and no neck.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in zed_cells.json).
3/4 front view like the FIRST image; every stab, throw, slash and dash points to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash trails, the shuriken, the shadow, smoke, the slash ring) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x96 squares (896x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both bracers with two blades each, both legs and boots in every frame, the pauldrons, the tabard and the back ornament, the arms as thick as in the FIRST image, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、腕刃、身体的方向和姿势照图1，不转成背影；站着的动作腿用图2自己的腿（藏青裤、黑钢护胫、尖头甲靴），跨步、蹲下、跪地的动作腿照图1弯，但还是图2的腿。
3. 长相、配色、细节全部换成图2：封闭枪灰头盔、金色中脊和金眉、两道红眼缝、面甲竖条、深红兜帽、两肩青铜金边肩甲、背后多齿银色刃饰、胸前银 V、深色腰带、深红前摆（金边、骨色尖刺）、藏青裤、黑钢护胫和尖头甲靴、两只金护臂、每腕两根银刃。头（兜帽 + 头盔）每帧照图2逐格贴，只平移。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的「动作骨架」，只是换了「皮囊」。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `zed_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1536 | 第 81 行 | **已做好，不用画** |
| `zed_run.png`（跑步（前倾的忍者跑）） | 8 × 120 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `RUN (League's ninja run: leaning forward, the arms trailing back), 8 frames: copy the SECOND image's legs frame by frame - the two legs stepping in turn, one forward and one back, the knees crossing, the lifted foot off the ground and the other foot on the feet line; the body leaning forward and bobbing 1 square; both arms held low and back, the wrist blades pointing back; the tabard swinging behind the front knee. Both legs in the design's colours.` |
| `zed_attack.png`（普攻（腕刃前刺）） | 6 帧：60 50 40 80 100 110 | 第 4 帧（tick 9） | 3 列 × 2 行，2688×1536 | 第 81 行 | `BASIC ATTACK (League's: a fast forward stab with the wrist blades), 6 frames: 1 the near arm (image right) drawn back, the body turning; 2 coiling, the blades high by his shoulder; 3 stepping in (the WHOLE figure 1-2 squares to the right), the arm starting forward; 4 THE STAB (the hit lands here): the near arm thrust straight forward to the right at chest height, its two blades pointing at the enemy, the far arm back by his hip; 5 the arm still forward, pulling back; 6 back toward the idle stance. The slash trail is an effect - do not draw it.` |
| `zed_skill.png`（W 影分身（单手把影子甩出去）） | 4 帧：50 60 80 90 | 第 2 帧（tick 3） | 4 列 × 1 行，3584×768 | 第 81 行 | `LIVING SHADOW (W; League's W: he flings his shadow forward with one hand), 4 frames: 1 the near arm (image right) raised up and back by his head, the body turning a little; 2 THE THROW (the shadow leaves here): the near arm swept forward and down to the right, the open hand reaching out, the blades pointing forward; 3 the follow-through, the arm low in front; 4 back toward the idle stance. The shadow is an effect - do not draw it.` |
| `zed_skill2.png`（Q 影奥义！诸刃（从背上抽出手里剑压低扔出）） | 6 帧：60 50 60 80 100 120 | 第 4 帧（tick 10） | 3 列 × 2 行，2688×1536 | 第 81 行 | `RAZOR SHURIKEN (Q; League's Q: he whips a big shuriken from his back and throws it), 6 frames: 1 the near hand reaching back over his shoulder to the blade ornament; 2 rearing up, the hand high above his head; 3 winding down, the body twisting; 4 THE THROW (the shuriken leaves here): bent low and forward, the near arm flung forward to the right close to the ground, the far arm back; 5 crouched low, recovering; 6 back toward the idle stance. Turn his front toward the viewer in every frame (League's frames 2-3 show his back - do not). The shuriken is an effect - do not draw it.` |
| `zed_skill_e.png`（E 影奔（双臂张开旋身横斩）） | 6 帧：50 40 43 70 70 100 | 第 4 帧（tick 8） | 3 列 × 2 行，2688×1536 | 第 81 行 | `SHADOW SLASH (E; League's E: a spinning slash with both arms flung wide), 6 frames: 1 both arms pulled in, crossed in front of the chest, the blades up; 2 starting the spin, the arms opening; 3 the body half turned, the arms going out; 4 THE SLASH (the ring of blades hits here): standing tall, BOTH arms flung straight out to his sides at shoulder height, the four wrist blades pointing outward left and right, his front to the viewer; 5 the arms still wide, one a square higher; 6 back toward the idle stance. The slash ring is an effect - do not draw it.` |
| `zed_ult.png`（R 禁奥义！瞬狱影杀阵（跃起双刃前突）） | 7 帧：50 50 80 80 80 90 110 | 第 3 帧（tick 6） | 4 列 × 2 行，3584×1536，最后 1 格空 | 第 81 行 | `DEATH MARK (R; League's R: he leaps and dashes through the enemy with both blades forward), 7 frames: 1 a quick crouch; 2 springing up, the arms drawn back; 3 THE DASH (he flies forward here): the body stretched forward low to the right, BOTH arms thrust forward, all four blades pointing at the enemy, the back leg trailing; 4 still dashing, the same pose a little lower; 5 THE CUT: the near arm swept across in front, the far arm back; 6 landing in a low crouch, the blades out at his sides; 7 rising back toward the idle stance. He vanishes in the game while he dashes - draw him fully visible.` |
| `zed_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1792×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body pushed back 1-2 squares (to the left), the design's head moved back a little (not turned), the arms flung out; 2 recovering toward the idle stance. The design's legs.` |
| `zed_dead.png`（死亡（单膝跪地后向前扑倒）） | 8 帧：100 100 120 150 200 150 150 500 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `DEATH, 8 frames (League's death: he drops to one knee, then falls face down): 1 struck, he jolts back; 2 sinking, one knee bending; 3 down on one knee, the body hunched, the arms hanging, the wrist blades touching the ground; 4-5 kneeling, slumped forward, the head low; 6 tipping forward; 7 fallen forward onto the ground, lying face down, stretched toward the right, the arms by his sides; 8 the same as 7. The head turned a quarter (lying) in 7-8. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；眼缝的红只在眼缝上；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的兜帽、头盔、描边，兜帽下面没有空隙；
- [ ] 每帧都有两只金护臂、四根腕刃、肩甲、前摆、背后刃饰、两条腿和靴子；手臂和造型图一样粗；站着的动作是造型图自己的腿；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步：两条腿前后交替、膝盖交叉、颜色一样，头的横向位置每帧一样，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `zed_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；不合格的动作用 rig 从造型图无损重摆（tools/art/rig_zed.py，照 rig_rengar.py）。
- 放进 `assets/source/native/`，`zed_cells.json` 用包里这份，`zed_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 9、W tick 3、Q tick 10、E tick 8、R tick 6），量头像截取点，重跑模拟，做预览 GIF。
