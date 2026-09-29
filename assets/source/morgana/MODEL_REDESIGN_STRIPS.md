# 堕落天使 莫甘娜：按新造型画 8 张动作图（给 Codex 的提示词）

> **造型已定：方案 A（翅膀半张开）**，Claude 整理到游戏尺寸：`design/morgana_native.png`（35×45 格含角，放大 8 倍放在 1024×1024 画布上，脚底在 y=792–799）。这一轮照它画 8 张动作图。
> - 每帧的大小照造型图（头顶到脚底约 38 格，含角 45 格）画，不要画成大图再缩小。做不到严格网格时，照同样的排版（每格 768×768 px，帧的位置和 `now/` 那张一样）交原稿也可以，Claude 会按格取色、换回造型图的头、脚底对齐到站位线。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、有没有没做到的地方）、`manifest.json`（每帧所在的格子 `assets[].frames[].rect`）和 `generation_prompts.json`（实际用的提示词）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/morgana_native.png` | **定稿造型**（第一张附图）：颜色、形状、头、脸、角冠、头发、翅膀、长裙、像素画法都照它 | 全部 8 张 |
| `now/morgana_now_<动作>.png` | 原版每个动作按游戏尺寸取色，放大 8 倍，按格子排好（每格 96×96 个方块 = 768×768 px） | 各自的动作图（帧数、每帧的时机、大小和站位） |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 各自的动作图（动作照它） |
| `guide/morgana_guide_<动作>.png` | 每帧的站位点（蓝十字）和脚底线（红线），红线以下的淡红区不能有任何像素 | 对位用，不要画进图里 |
| `morgana_cells.json` | 每帧的站位点和帧时长 | 整理对位 |
| `refs/morgana_target.png` | 用户给的原始立绘（长相参考；比例以定稿造型为准） | 需要时参考 |

`now/`、`pose/`、`guide/`、`morgana_cells.json` 和上一轮一样（原版的动作和时长没变），只是造型换了。

## 规则（每张都一样）

- **头每帧照搬造型图**：轮廓、头发、角冠、脸一格不差，只能整体移动（身体弯的时候整体倾斜）；不要重画，否则播放时会闪。
- **眼睛**：每帧和造型图一模一样。两只眼睛一样大、在同一行：各 2 格宽 2 格高，左上一格白色高光、其余粉紫色，上面各一段深色睫毛；两眼之间隔 2 格皮肤；近眼左边留一格脸颊，远眼贴着脸的右边缘。脸约 7 格宽，不要画窄（窄了眼睛会贴到头发上）。眼睛的粉紫色 `#C83CA6` **只用在眼睛上**。
- **翅膀**：和造型图一样半张开在身后，不挡脸和胸口；只有大招第 3–4 帧可以完全展开。
- **描边只有一圈**：轮廓外面一格近黑色描边；描边里面用材质自己的暗色，不要再画一圈黑。
- 手臂从肩膀长出来，不要挡在脸前面。3/4 正面朝右，不画背影（死亡最后趴下的帧除外）。
- **脚底线**：每格里脚和裙摆的最低一行都在第 78 行（像素 624–631）；632 以下什么都不能有（游戏在那里画血条）。只有死亡倒地的帧可以低于这条线，最多 2 格。
- **只用造型图里的颜色**（26 色）。背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、边框、文字、编号、参考线。

## 2–9. 动作图

每张附三张图：第一张 `design/morgana_native.png`，第二张 `now/morgana_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。输出文件名 `morgana_<动作>.png`，排版和第二张附图完全一样。

```text
Three attached images. FIRST: the approved clean pixel-art design of this character at 8x (every pixel an 8x8 block, 35x45 squares with the horns) - copy her colors, shapes, head, face, horned crown, hair, half-spread wings, gown and pixel style exactly. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), her size and where she stands in her cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
Task: draw every frame as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size as the FIRST image (about 38 squares from the top of the head to the feet when standing, 45 with the horns), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 26 colors of the FIRST image. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise. 3/4 FRONT view facing right, never her back.
The head is COPIED from the FIRST image in every frame - the same outline, horns, hair and face, square for square - and only moved (or tilted as a whole where the body bends); never redraw it, or it flickers when the frames play. The eyes stay exactly as in the FIRST image in every frame: both eyes the SAME size on the same rows, each 2 squares wide and 2 tall with one white highlight square at its top left and a dark lash row above it; two skin squares between the eyes; the near eye one skin square in from the face's left edge, the far eye on the face's right edge; the face about 7 squares wide - never narrower, or the eyes touch the hair; the pink-violet eye color #C83CA6 appears ONLY in the eyes. Her arms come out of her shoulders and never cross in front of her face. Her wings stay half-spread behind her as in the FIRST image, never covering her face or chest.
Feet line: in every cell the lowest row of her feet and gown is square row 78 from the top of the cell (pixels 624-631), the same line in every frame; NOTHING from pixel 632 down - not the gown, not the wings - because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in morgana_cells.json).
[animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size]; frame N in the same cell as in the SECOND image. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
```

| # | 文件 | 帧 × 毫秒 | 排版 | `[animation]` |
|---:|---|---|---|---|
| 2 | `morgana_idle.png` | 6 × 200 | 3 列 × 2 行，2304×1536 | `Animation: IDLE, 6 frames: all 6 frames are exactly the FIRST image, unchanged (the game adds the breathing).` |
| 3 | `morgana_run.png` | 8 × 143 | 4 列 × 2 行，3072×1536 | `Animation: MOVE loop, 8 frames, her walk from the THIRD image: an upright gliding walk, the gown swaying and one heel stepping out under the hem in turn (frames 1-4 one step, 5-8 the other), the arms held slightly out, the wings half-spread and swaying a little. Her HEAD stays in the same place across the cell relative to her standing point in all 8 frames (at most 1 square up or down) - only the gown, the feet, the arms and the wings move.` |
| 4 | `morgana_attack.png` | 6 帧：60 70 80 90 100 100 | 3 列 × 2 行，2304×1536 | `Animation: BASIC ATTACK, 6 frames: she flings a bolt of dark magic with her right hand (the bolt is a separate effect - do not draw it): 1 the hand drawn back to her shoulder, 2 the arm swinging forward, 3 the arm stretched fully forward to the right, palm open (the release), 4 held, 5-6 back toward idle. The feet stay planted.` |
| 5 | `morgana_skill.png` | 6 帧：70 70 80 90 110 150 | 3 列 × 2 行，2304×1536 | `Animation: DARK BINDING, 6 frames: she whirls and hurls the binding orb (a separate effect): 1 gathering, arms drawn in, the gown starting to swirl; 2 turning, the gown flaring wide around her; 3 the throw - the right arm flung far forward to the right (the release); 4-5 the gown settling, the arm still reaching; 6 back toward idle. Keep her face toward the viewer in every frame.` |
| 6 | `morgana_skill2.png` | 6 帧：60 60 80 100 100 100 | 3 列 × 2 行，2304×1536 | `Animation: BLACK SHIELD, 6 frames: she casts a shield on an ally: 1 the right hand before her chest; 2-5 the right hand raised beside her head, elbow bent, palm open toward the right (the shield is a separate effect), the arm a normal length, the hand never over her face; 6 back toward idle.` |
| 7 | `morgana_ult.png` | 8 帧：80 80 80 90 100 100 110 120 | 4 列 × 2 行，3072×1536 | `Animation: SOUL SHACKLES, 8 frames: 1 she crouches a little, gathering; 2 she rises, lifting off the ground as in the THIRD image, her head staying on her shoulders; 3-4 arms thrown wide open to both sides, her wings spread FULLY wide behind her and the gown flaring (the chains are a separate effect); 5-6 she leans forward with her arms pulling, as if dragging chains; 7-8 back toward idle, the wings half-spread again.` |
| 8 | `morgana_hit.png` | 2 × 120 | 2 列 × 1 行，1536×768 | `Animation: HIT, 2 frames: 1 jolted back by a blow, eyes squeezed shut (two short dark lines), 2 recovering toward idle.` |
| 9 | `morgana_dead.png` | 8 帧：100 100 120 120 120 150 150 500 | 4 列 × 2 行，3072×1536 | `Animation: DEATH, 8 frames, going down in ONE movement (each frame lower than the one before): 1 struck, head thrown back; 2 she staggers, arms spread; 3 she sinks to her knees; 4 on her knees, bending forward; 5 on her hands and knees, head bowed; 6 sinking lower onto her side; 7 lying on the ground, the wings sinking; 8 lying face down on the ground line, the wings flat on her back, the gown spread around her. Frames 4-8 may reach 2 squares below the feet line, nothing lower.` |
