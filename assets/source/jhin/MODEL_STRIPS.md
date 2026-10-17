# 烬：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/jhin_design.png`（放大 8 倍，1024×1024；头套顶到脚底 41 格，29 格宽，23 色；脚底在第 99 行，两脚中间在第 64 列）。**造型图就是标准**：深紫头套、白瓷面具和粉紫眼睛、品红立领和绿宝石金扣、米白披风、紫红衬里、金色机械臂、肤色近侧手臂和紫护腕、紫裤子、金色腿撑、**手杖枪和手炮「低语」**，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`jhin_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/jhin_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、枪和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（大头、细长身子）；② 头是贴上去的（见下），英雄联盟里他会低头、扭头，我们**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡低头时整个头跟着身体转），**不画背影**；③ W 原版有一段转身背对镜头的腾空踢腿，我们一律画 3/4 正面；④ 大招原版把两把枪合成一门大炮，扛在肩上单膝跪地瞄准：照 `pose/lol_pose_ult*.png` 的大炮样子画（深铁灰长炮管、金环、手杖枪贴在炮管上、下面挂品红流苏），大小差不多和他身高一样长。
> - **两把枪（最重要的标志）**：Whisper (the hand cannon in his near hand) and the cane-rifle (hanging at his far hip, or in his hands where the animation says) are in every frame, whole and STRAIGHT (never bent, broken, shortened or melted into the body)。开枪的那一帧枪要**平**：手炮或手杖枪水平指向右边，枪口不要高过站位点（蓝十字）8 格以上（W 10 格），否则子弹在游戏里看起来是歪的。
> - 出招方向：**开枪、扔手雷都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及开枪帧的枪口位置）和 `generation_prompts.json`，最好打成一个 zip（`jhin_strips_pack_done.zip`，放在 outputs 里）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/jhin_palette.png`，或直接读 `design/jhin_design_1x.png`）。**先把眼睛专用的粉紫 `#FF6EB4` 从色板里去掉**（吸附时会跑到别的地方），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/jhin_head_1x.png` 里不透明的格子：头套、面具和眼睛、立领两边的尖角；在 128×128 画布上的范围 x 55–68、y 59–71，**按图里的形状贴，不是整个方框**——披风不属于头，它跟着身体走）原样贴进每一帧头的位置（只平移；死亡低头时整个头跟着转）。这样每帧的脸都和造型图一模一样。头下面接立领和披风，不要拉出一截脖子。
5. 对位：每帧按 `jhin_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/jhin_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/jhin_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/jhin_head.png`、`_1x.png` | 要贴进每一帧的头（头套、面具、眼睛、立领尖角，不含披风） | 贴头 |
| `design/jhin_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `jhin_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/jhin_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、枪和身体的动作 |
| `guide/jhin_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `jhin_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/jhin_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref.png`、`tfm2_style_ref_undead.png`、`4_tfm2_style.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（头套顶到脚底 41 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；明暗照定稿（面具的亮白、金色的高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **手**：远侧是金色机械臂和金手，近侧是肤色手臂和紫护腕；手臂 2–3 格粗、手是实心的拳头或手掌；**不要 1 像素的黑细棍、不要飘着的手**，手和枪连在一起。
- **两把枪**：Whisper (the hand cannon in his near hand) and the cane-rifle (hanging at his far hip, or in his hands where the animation says) are in every frame, whole and STRAIGHT (never bent, broken, shortened or melted into the body)。
- **头每帧都是造型图的头**（头套、面具、眼睛、立领尖角逐格一样），只平移（死亡低头时整个转）；粉紫 `#FF6EB4` 只用在眼睛上。
- **披风**：每帧都有，跟着动作摆；披风下面能看到紫裤子和金色腿撑。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），流苏、枪口、披风都在它上面。只有死亡掉在地上的枪可以贴着脚底线。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：子弹、枪口火光、烟、手雷、莲花、花瓣、光线都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/jhin_design.png`，第二张 `now/jhin_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `jhin_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, mask, costume, hands, both guns and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same dark purple hood cap and white porcelain mask with the pink-magenta eyes, the crimson collar and the green brooch, the ivory cape with tan swirls, the crimson lining, the gold armoured far arm, the bare near arm with the purple wrist guard, the purple trousers, the gold leg braces, the cane-rifle and the hand cannon Whisper, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the shot, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the guns and the body from it, but keep the FIRST image's proportions (a big masked head, a slim tall body, its guns); never draw him from the back or upside down.
The character: Jhin (a tall, slender theatrical gunman: a white porcelain mask with pink-magenta eyes, a dark purple hood cap, a high crimson collar with a green brooch, a big ivory cape over his far shoulder, a crimson lining, a gold armoured far arm, purple trousers, gold leg braces, a cane-rifle with a teal wrap and a crimson tassel, and an ornate hand cannon with an ivory grip).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (41 squares from the hood's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #0E0814 #22162F #262A3A #5E0A2C #5A2E10 #3A2052 #A01248 #5E2E7A #4A5470 #A0581A #2E9696 #A86450 #D42A62 #D8902C #74859E #A89C7C #E0A07E #FF6EB4 #D2CAB0 #FFD878 #BCCEDC #F2EEDC #F4F8FA. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading - the white mask, the ivory cape and the bright gold move with the pose; no dithering, no noise, no random specks added. Hands are solid fists or palms at the ends of arms 2-3 squares wide - the gold far arm and the bare near arm with its purple wrist guard - never 1-pixel black sticks or floating hands; each hand holds its gun.
The two guns are his signature: Whisper (the hand cannon in his near hand) and the cane-rifle (hanging at his far hip, or in his hands where the animation says) are in every frame, whole and STRAIGHT (never bent, broken, shortened or melted into the body). In every shot frame the gun is level and points to the RIGHT, its muzzle no higher than the animation line says.
The head (the hood cap, the mask with both eyes, the collar's tips beside the jaw) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns down with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the collar and the cape - no neck. The pink-magenta #FF6EB4 appears ONLY in the eyes.
The cape is in every frame and moves with the pose; the purple trousers and the gold leg braces show under it.
Feet line: in every cell his lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not a gun, not the tassel, not the cape - because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in jhin_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every shot and throw goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (bullets, muzzle flashes, smoke, the grenade after it leaves his hand, lotus flowers, petals, beams) - only the character. Every animation starts and ends in the FIRST image's stance (the ult's three strips: in the kneeling aim pose).
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x80 squares (768x640 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, the pink-magenta #FF6EB4 only in the eyes, both guns whole and straight in every frame (the big cannon in the ult), hands holding them, the cape in every frame, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `jhin_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1280 | 第 67 行 | **已做好，不用画** |
| `jhin_run.png`（移动（优雅的步行，金手扶着手杖枪，手炮垂下）） | 8 × 100 | — | 4 列 × 2 行，3072×1280 | 第 67 行 | `MOVE, 8 frames, one seamless loop (8 x 100 ms, League's walk): an elegant, unhurried theatrical walk, upright, shoulders back; the gold armoured far arm stays bent with the gold fist on the cane-rifle at his far hip (the cane swings a little with the step); the near arm swings gently with Whisper hanging pointed down; the cape and the crimson lining sway; long slim steps on the gold leg braces: in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same colours; the body bobs 1 square down and up over each half; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `jhin_attack.png`（普攻（举起手炮平射）） | 6 帧：50 50 70 70 80 80 | 第 3 帧（tick 6） | 3 列 × 2 行，2304×1280 | 第 67 行 | `BASIC ATTACK, 6 frames (League's attack1: he raises Whisper and fires): 1 the idle stance, the near arm starting to lift Whisper; 2 the near arm brings Whisper up and forward; 3 THE SHOT (the bullet leaves here): the near arm straight out to the right at chest height, Whisper level and pointing right, its muzzle NO HIGHER than 8 squares above the standing point (the blue cross of the guide); 4 the recoil, Whisper kicked up a little; 5 he twirls Whisper up beside his mask, barrel up; 6 back to the idle stance. The gold fist stays on the cane-rifle at his hip in every frame. The bullet and the muzzle flash are effects - do not draw them.` |
| `jhin_attack4.png`（第四发（转身亮相后平射，必定暴击的那一枪）） | 6 帧：40 60 50 80 120 150 | 第 4 帧（tick 9） | 3 列 × 2 行，2304×1280 | 第 67 行 | `THE FOURTH SHOT (his flourish before the fourth, always-critical bullet), 6 frames: 1 he turns on one leg, the far knee lifted, Whisper close to his chest; 2 a showman's flourish: Whisper raised high above his head in the near hand, the gold hand open beside his shoulder; 3 he brings Whisper down and aims; 4 THE SHOT: the near arm straight out to the right at chest height, Whisper level and pointing right, the muzzle NO HIGHER than 8 squares above the standing point; 5 holding the aim, the cape settling; 6 back to the idle stance (the gold fist back on the cane). Never upside down, never his back. The bullet and its flash are effects - do not draw them.` |
| `jhin_skill.png`（Q 曼舞手雷（金手扔出手雷）） | 6 帧：50 50 70 70 80 80 | 第 3 帧（tick 6） | 3 列 × 2 行，2304×1280 | 第 67 行 | `DANCING GRENADE (Q: he tosses a grenade with the gold hand), 6 frames (League's spell1): 1 the gold far arm lifts off the cane, reaching back; 2 the gold arm swings back behind his far shoulder, a small round grenade in the fist; 3 THE THROW (it leaves here): the gold arm sweeps across his body to the right at chest height, the fist opening; 4 the follow-through, the gold arm out to the right; 5 the gold arm coming back; 6 the idle stance, the gold fist back on the cane. Whisper stays in the near hand, pointed down. The grenade is an effect - do not draw it after frame 3.` |
| `jhin_skill2.png`（W 致命华彩（手杖枪平举射出远程一枪）） | 8 帧：100 100 100 100 150 100 100 50 | 第 7 帧（tick 39） | 4 列 × 2 行，3072×1280 | 第 67 行 | `DEADLY FLOURISH (W: the cane-rifle's long shot), 8 frames (League's spell2, ~0.8 s): 1 he crouches low, taking the cane-rifle from his hip with both hands; 2 rising, the cane-rifle swung up across his body; 3 a theatrical high step, the cane-rifle raised; 4 landing, the cane-rifle coming down to aim; 5 aiming: the cane-rifle level at shoulder height pointing right, the gold hand under its barrel, the near hand at its grip (Whisper tucked in that hand); 6 holding the aim; 7 THE SHOT (the long shot leaves here): the cane-rifle level, a small kick of recoil, its muzzle NO HIGHER than 10 squares above the standing point; 8 the cane-rifle swung back down to his hip, the idle stance. Always 3/4 front view facing right - never his back, even where the THIRD image turns away. The shot, the lotus he throws and every flash are effects - do not draw them.` |
| `jhin_ult.png`（R 完美谢幕·架枪（蹲下、合成大炮、单膝跪地扛炮）） | 4 帧：80 100 120 200 | — | 4 列 × 1 行，3072×640 | 第 67 行 | `CURTAIN CALL - THE DEPLOY (R begins), 4 frames: 1 he crouches, both arms spread, the cane-rifle and Whisper in his hands; 2 he raises his weapons together above his head and they become one BIG CANNON (the THIRD image: a long heavy gunmetal barrel with gold rings and his cane-rifle along it, about as long as he is tall, the crimson tassel hanging under it); 3 he drops to one knee and lays the big cannon on his near shoulder, aiming right; 4 kneeling, the big cannon level on his shoulder pointing right - this pose is the first frame of the aim loop. Never his back.` |
| `jhin_ult_aim.png`（R 瞄准（跪姿扛炮循环）） | 4 × 250 | — | 4 列 × 1 行，3072×640 | 第 67 行 | `CURTAIN CALL - THE AIM (a loop while he channels), 4 frames x 250 ms: kneeling on one knee, the BIG CANNON level on his near shoulder pointing right (as in the last frame of the deploy), the gold hand under the barrel, his mask turned to the right along the barrel; the cape and the tassel move a little (1 square), the body breathes (1 square). Frame 4 flows into frame 1.` |
| `jhin_ult_shot.png`（R 开枪（每一枪的后坐）） | 4 帧：50 70 70 60 | 第 1 帧（tick 0） | 4 列 × 1 行，3072×640 | 第 67 行 | `CURTAIN CALL - A SHOT (the recoil after each of the four shots), 4 frames: 1 THE SHOT: kneeling, the big cannon level pointing right (the aim pose); 2 the recoil: the barrel kicks up about 20 degrees and his shoulder rocks back 1 square; 3 settling, the barrel coming down; 4 back to the aim pose. The bullet, the smoke and the muzzle flash are effects - do not draw them.` |
| `jhin_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×640 | 第 67 行 | `HIT, 2 frames: 1 jolted back by a blow: his body and mask pushed back 1-2 squares (to the left), the cape swaying, both guns still held; 2 recovering toward the idle stance.` |
| `jhin_dead.png`（死亡（谢幕：跪下低头，手炮掉在地上）） | 8 帧：100 100 110 110 120 150 300 500 | — | 4 列 × 2 行，3072×1280 | 第 67 行 | `DEATH, 8 frames (League's death: his final bow): 1 struck, he hunches forward; 2 he straightens, arms flung out, Whisper falling out of his hand onto the ground in front of him; 3 he sinks to his knees; 4-8 kneeling, his head and shoulders bowing forward lower and lower, the gold hand on the ground, the cane-rifle lying beside him, Whisper lying on the ground in front of him (the same pose from frame 6 on). The mask stays visible (the 3/4 front view, turned down, never upside down). Frames 3-8 kneel on the feet line; the dropped guns lie on it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡低头时整个转），两只眼睛都在；
- [ ] 粉紫 `#FF6EB4` 只出现在眼睛上：头部以外 0 个像素；
- [ ] **两把枪每帧都在、完整、笔直**；开枪帧枪平指向右、枪口不高过站位点 8 格（W 10 格）；大招三张画的是合成的大炮；手是实心的、连着手臂和枪；
- [ ] 每帧都有披风；脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交叉迈步、颜色一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点、bbox 和开枪帧的枪口位置都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `jhin_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、粉紫只在眼睛上、连通块、手臂粗细、两把枪是否完整笔直、零散黑格、每帧面积和待机比），不在网格上的重新取样；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`jhin_cells.json` 用包里这份，`jhin_idle.png` 用包里已做好的那张。
- `import_native.py --hero jhin`：ORDER 待机一张图 + BOB 呼吸（缝选在裤子或腿撑的直段），EYES = `#FF6EB4`，COMPLETE + CLEAN 补描边、清黑边，NECK 检查立领每帧在面具下沿同一行。
- 按出手帧核对技能数据的时机（普攻 tick 6、第四发 tick 9、Q tick 6、W tick 39），量枪口高度定子弹的 `y_offset`（枪口高过站位点 8 px 以上子弹会歪），量特效挂点和头像截取点，重跑模拟，做预览 GIF。
