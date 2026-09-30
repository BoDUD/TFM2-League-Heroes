# 塔里克：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：B2**。你按游戏尺寸画的 B 版（头 15 格），头部照原画重画过一次（中分、两侧垂发、浓眉、闭嘴微笑），用户选定；Claude 只补了 5 格描边：`design/taric_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799，发顶到脚底 40 格）。**造型图就是标准**，颜色、形状、明暗、头发、脸、肩甲、斧锤一律照它。
> - **待机条已经做好**（`taric_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/taric_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。英雄联盟的长发在有些帧里会甩成很长的一条，**头发照造型图，只轻微摆动**；英雄联盟里转身露背的帧，**我们保持 3/4 正面**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/taric_palette.png`，或直接读 `design/taric_design_1x.png`）。**先把瞳孔的天蓝 `#279FF6` 从色板里去掉**（它只随第 4 步贴的头回来）。
4. **贴头**：把造型图的头（`design/taric_head_1x.png`：头发、脸、眼睛和它们的描边；肩甲不在里面；在 128×128 画布上的范围 x 54–75、y 60–74）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡跪倒低头的帧可以不贴）。头贴在肩甲和衣领上，下巴下面不要露出一截脖子；移动循环各帧肩膀都在下巴下同一行。垂到肩后的头发每帧自己画。
5. 对位：每帧按 `taric_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人和斧锤连成一块（死亡倒地后掉在地上的斧锤除外）、手臂至少 3 格粗、斧锤握在近侧（图左）的手里。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/taric_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/taric_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/taric_head.png`、`_1x.png` | 要贴进每一帧的头（头发、脸、眼睛；不含肩甲） | 贴头 |
| `design/taric_palette.png` | 造型图的全部 26 色（暗到亮） | 色板 |
| `taric_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/taric_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体的动作 |
| `guide/taric_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `taric_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/taric_picture.png` | 用户选的原画（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（发顶到脚底 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 26 种颜色**，不加新颜色；明暗照定稿（亮边、褶、高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **身体粗细照定稿**：结实的 Q 版身材，巨大的银白肩甲各有一颗蓝宝石，手臂从肩膀到手至少 3 格粗（加描边），不能画成 1–2 格的细线（在游戏里像“无影手”）；腰带、前摆、护腿、披风照定稿，只随姿势移动。
- **头每帧都是造型图的头**（头发、脸、眼睛逐格一样），只平移或整体倾斜；两只眼睛一样大、同一行，不能连成横杠，天蓝 `#279FF6` 只用在两颗瞳孔上。长发照定稿（中分、垂在脸两侧和肩后），只轻微摆动，**不要**照参考图甩成很长的一条。
- **斧锤在近侧的手（图里左边那只），远侧的手臂光着、手张开**，每帧斧锤都握在手里（死亡帧脱手落地除外），不能飘开、不能挡脸；斧头是两片弯弯的银紫刃夹一颗紫蓝宝珠，短而深色的握柄。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），斧头、披风下摆也不能低于它。只有死亡跪倒的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间有两膝交叉的帧），每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，看得到脸，不画背影。**只画角色**：星光、光束、宝石的光、天降的光柱都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/taric_design.png`，第二张 `now/taric_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `taric_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, hair, face, pauldrons, mace-axe and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it (but not its long flying hair, and never turn his back to us).
The character: a sturdy heroic chibi gem knight: long auburn-brown hair parted in the middle, a square-jawed face with heavy brows and blue eyes, huge silver-white pauldrons each set with a big sapphire, a teal-blue tunic wrapped across his chest, a dark brown sleeve and silver gauntlet on the near arm, the far arm bare, a heavy silver belt with a violet-blue gem buckle, a navy tabard, dark plum trousers, grey-green greaves and boots, a long navy-violet cape; in his near hand a short crystal mace-axe with two curved lilac-silver blades round a violet-blue orb.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the top of the hair to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 26 colors of the FIRST image, no new colors: #15111C #22213C #3A202C #161469 #432739 #123F66 #633338 #7C3B38 #44575D #14618C #70415C #984D3C #363AC8 #746970 #A26058 #C07850 #259DCC #7E979A #279FF6 #785AF0 #F39B77 #A99BDD #B7D1D5 #FFD1A1 #F5F5ED #FFFFFF. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its lit edges, folds and highlights move with the pose; no dithering, no noise, no random specks added.
The head (hair on top of the head, face, brows, eyes) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play; it sits on the pauldrons and the collar with no neck showing. The hair falling behind the shoulders is drawn in each frame and sways a little with the motion. The mace-axe is always in his NEAR hand (the left one in the image) and the far arm is bare with an open hand, as in the FIRST image; the weapon moves with his hand, never floats free, never covers his face. Its head is the FIRST image's: two curved lilac-silver blades round a violet-blue orb, on a short dark grip. His eyes are the FIRST image's eyes (each a white square and a sky-blue square, the heavy brows right above them, on the same row), never merged into a bar; that sky blue appears ONLY in the two eyes. The long hair is the FIRST image's hair - parted in the middle, falling on both sides of the face and behind the shoulders; League's hair flies out in long streams in some frames of the THIRD image: do not copy that, let the design's hair only sway a little. His arms are at least 3 squares thick from the shoulder to the hand - never a 1-2 square line; the whole figure and the mace-axe are ONE connected piece in every frame (except the death frames where it lies on the ground).
Feet line: in every cell the lowest row of his feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the mace-axe, not the cape - because the game draws the health bar there (the death may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in taric_cells.json). In a move loop his head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, the face always visible, never his back. Do not draw effects (starlight, beams, glows, light from the sky) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible and level, the sky blue only in the two eyes, arms at least 3 squares thick, the mace-axe in the near hand, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `taric_idle.png` | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `taric_run.png` | 8 × 150 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of League's run (1.2 s cycle, 8 x 150 ms, the SECOND and THIRD images): he strides forward, upright and powerful, the mace-axe held low in his near hand and trailing a little behind him (its head never below the feet line), the bare far arm swinging; the legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames; the cape and the long hair sway behind; his head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `taric_attack.png` | 6 帧：60 60 70 70 80 90 | 第 3 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, 6 frames: 1 he draws the mace-axe back to his near side (image left), shoulders turning; 2 he steps in, the swing starting; 3 the release (the hit lands here): a wide horizontal sweep - the mace-axe swung out in front of him to the right at chest height, the near arm extended; 4 follow-through, the weapon carried across his body; 5-6 back toward the idle stance. Where the THIRD image turns his back, keep him 3/4 front.` |
| `taric_attack_p.png` | 6 帧：50 50 60 70 80 90 | 第 3 帧（tick 9） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BRAVADO STRIKE (the empowered attack, faster and heavier), 6 frames: 1 he lifts the mace-axe behind his near shoulder; 2 raised high over his head; 3 the release (the hit lands here): a powerful downward smash in front of him to the right, body lunging forward and low; 4 still low, the weapon down in front of him; 5-6 back toward the idle stance. The glow of his gems is an effect - do not draw it.` |
| `taric_skill.png` | 6 帧：60 70 80 90 100 100 | 第 3 帧（tick 12） | 3 列 × 2 行，2304×1536 | 第 81 行 | `DAZZLE, 6 frames: 1 gathering, the mace-axe drawn back; 2 he swings it forward; 3 the release (the beam of starlight leaves the weapon here): the mace-axe thrust out straight in front of him to the right, the near arm extended, the bare far hand raised up behind; 4 holding that pose; 5-6 back toward the idle stance. The beam is an effect - do not draw it.` |
| `taric_skill2.png` | 6 帧：60 70 80 90 100 100 | 第 3 帧（tick 12） | 3 列 × 2 行，2304×1536 | 第 81 行 | `STARLIGHT'S TOUCH, 6 frames: 1 he gathers, the bare far hand drawn in; 2 the far hand rising; 3 the release (the heal happens here): the bare far hand raised high above his head, open, palm up, his face turned up a little; 4 still raised; 5 lowering; 6 back toward the idle stance. The mace-axe stays low in the near hand. The starlight is an effect - do not draw it.` |
| `taric_ult.png` | 7 帧：80 90 100 100 100 100 97 | 第 3 帧 | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `COSMIC RADIANCE, 7 frames: 1 he plants his feet; 2 he raises the mace-axe in front of him; 3 the call (the heavens answer here): he leans back a little and looks up, the mace-axe held up high in the near hand, the bare far hand open to the sky; 4-6 holding that pose, the cape settling; 7 back toward the idle stance. The light coming down is an effect - do not draw it.` |
| `taric_hit.png` | 2 × 100 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back; 2 recovering toward the idle stance.` |
| `taric_dead.png` | 8 帧：100 100 100 120 120 120 150 400 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames, as in the THIRD image: 1 struck, head thrown back; 2 staggering back, the mace-axe flung out of his hand; 3 the mace-axe falling away; 4-5 he sinks to his knees; 6-8 kneeling slumped forward on the ground line, head bowed, the mace-axe lying on the ground in front of him (the only frames where it is apart from his hand). Frames 6-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、一样大、同一高度；
- [ ] `#279FF6` 只出现在两颗瞳孔上：头部范围以外 0 个像素；
- [ ] 斧锤每帧都握在近侧（图左）的手里（死亡落地除外），不挡脸；手臂至少 3 格粗；每帧整个人和斧锤连成一块；
- [ ] 头发照定稿，没有甩成长条；没有背影；脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `taric_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、瞳孔色只在眼睛上、每帧面积和待机比、连通块、手臂粗细、武器在近侧手），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`taric_cells.json` 用包里这份，`taric_idle.png` 用包里已做好的那张。
- `import_native.py --hero taric`：ORDER 待机一张图 + BOB 呼吸，EYES = `#279FF6`（按眼睛对齐待机和移动），COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 10、强化普攻 tick 9、E tick 12、Q tick 12、R 的动画 40 tick），做预览 GIF，逐帧检查后给用户看。
