> 卢锡安重做的第二步（交给 Codex 的原样提示词）。画动作之前，脸又在用户的 Codex 会话里改了 10 格：眉毛换成头发的深棕、下巴上方加两格闭着的嘴（`codex_model/redesign_strips_face_edit_record.json`），动作都用改后的脸。Codex 的交付说明：`codex_model/redesign_strips_*`。

# 卢锡安：按新造型画 9 条动作（给 Codex，第二步）

> **这一轮画 9 张动作图**：移动、普攻、连开两枪、Q、E 往前冲、E 往后冲、R、受击、死亡。待机不用画（`lucian_idle.png` 已经用造型图拼好）。
> - 造型图 `lucian_native.png` 是用户确认的新卢锡安（由你上一轮的原稿整理到游戏尺寸：每格 8×8，19 色，一圈描边，两只眼睛）。**每一帧都照它画**：同样的大小、颜色、头、外套、双枪和像素风格。
> - 格子、帧数、每帧时长、出手帧都和上一版一样；参考图按新造型的身高（头顶到鞋底约 41 格）重新渲染过，站位点跟着重算（和上一版左右差 1–2 格，以这次的 `lucian_cells.json` 为准）。
> - 交回时附 `HANDOFF.md`（每张用了哪段提示词、没做到的地方）和 `manifest.json`（文件名、尺寸、每帧格子、站位点、不透明区域、眼睛颜色的中心）。

## 附图

| 文件 | 内容 | 用法 |
|---|---|---|
| `lucian_native.png` | 确认的新造型，8 倍，1024×1024，脚底第 99 行、站位点 (64, 88) | **第一张图**：颜色、形状、头、像素风格全照它 |
| `lucian_now_<动作>.png` | 每个动作按新身高渲染的游戏尺寸参考条，8 倍，每格 96×96 个方块 | **第二张图**：帧数、每帧的时机、在格子里的位置（它是 3D 渲染的平均色，很糊，不要照它的样子） |
| `lol_pose_<动作>.png` | 英雄联盟原版同一帧的动作渲染，同样的格子、同样的位置 | **第三张图**：身体的动作照它 |
| `lucian_guide_<动作>.png` | 每帧的站位点（蓝十字）和脚底线（红线），红线以下的淡红区不能有像素 | 对位用，不要画进图里 |
| `lucian_cells.json` | 每帧的站位点（格子里第几列、第几行）和帧时长 | 整理对位 |
| `lucian_idle.png` | 待机条（已拼好，不用画） | 只作参考：每个动作从这个站姿开始、回到这个站姿结束 |
| `tfm2_style_ref_gunner.png` | 团战经理2 原版英雄 | 像素大小和干净程度 |

## 规则（含这几天整理 18 个英雄时学到的）

- **只用造型图的 19 种颜色**：#181118 #2D2327 #28272F #2F2D36 #432541 #423536 #4F352C #3A3A42 #562E48 #77532D #3F6A74 #955F44 #66717C #B48D3E #CBA04B #A29690 #CFC1B4 #F3E6D1 #F4F2EA。不加新颜色。
- **头每帧照造型图逐格复制**：轮廓、头发（两侧剃出的线）、眉毛、两只眼睛都和造型图一样，只随动作整体移动（死亡倒地时可以倾斜），不重新画；两只眼睛一样大、一样高，不连成横杠；眉毛是皱眉：每条一格粗、往鼻子方向斜下（外端高一格），不要画成平的横杠或中间拱起；眼白 `#F4F2EA` 和虹膜 `#3F6A74` 只用在眼睛上；鼻尖不凸出脸颊。
- **只有一圈描边**：剪影外一圈 1 格宽的近黑描边，里面的边缘和褶皱用材质自己最暗的色阶，不要第二圈黑。
- **干净**：大块纯色，每种材质 2–3 个色阶；不要抖动、渐变、噪点、孤立的杂色方块。
- **站姿**：每个动作从造型图的站姿开始、回到它结束——后手（画面左边）一把枪举在头边、枪口朝上，前手（画面右边）一把枪在肩膀高度往前平指。
- **脚底线**：每格里鞋底最低一行是那一帧站位点下方第 11 行（`lucian_cells.json`），红线以下什么都不能有（游戏在脚下画血条）；只有死亡倒地的帧可以低于红线，最多 2 格。
- 3/4 正面朝右，不画背影；手臂和枪从肩膀、胸口伸出，不挡脸。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、参考线。

## 提示词

9 张的提示词都以同一段开头，每张只换最后的动作说明和排版。

```text
Three attached images. FIRST: the approved pixel-art design of this character at 8x (every pixel an 8x8 block) - copy his colors, shapes, head, coat, pistols and pixel style exactly, the head the same size in every frame. SECOND: a game-size reference of the animation at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the shot, the recoil, the recovery) and where he stands in his cell, but NOT its look (it is a blurry average of a 3D render). THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
Task: draw every frame as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size (about 41 pixels from the top of the head to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): only the colors of the FIRST image, no new ones; big flat areas, 2-3 shades per material as in the FIRST image; no dithering, no gradients, no noise, no lone square of a different color inside an area; ONE 1-square near-black outline around the silhouette, and inside it the material's own darkest shade - never a second ring of black.
Head and face: copy the head of the FIRST image into every frame square for square - the same outline, hair, brows and both eyes, only moved (or tilted in the fall), never redrawn, never merged into a bar; the brows frown - each a line one square thick sloping down toward the nose (its outer end one square higher), never a flat bar or an arch; the eye colors #F4F2EA and #3F6A74 used nowhere else. Arms and pistols come from the shoulders and the chest and never cover the face. 3/4 FRONT view facing right, never his back.
Stance: every animation starts and ends in the FIRST image's stance - the rear pistol (left of the image) raised beside his head, the front pistol (right of the image) held out forward at shoulder height.
Feet line: in every cell the lowest row of his soles is the row 11 squares below that frame's standing point (lucian_cells.json); NOTHING below it - not a pistol, not the coat - because the game draws the health bar there. His place across the cell follows the SECOND image.
[animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size]; frame N in the same cell as in the SECOND image. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
```

| 文件 | 帧 × 毫秒 | 排版 | 出手帧 | `[animation]` |
|---|---|---|---|---|
| `lucian_run.png` | 8 × 117 | 4 列 × 2 行，3072×1536 | — | `Animation: MOVE loop, 8 frames, one second like the original: his run from the THIRD image - a running stride, the front pistol held forward, the rear pistol raised, the coat tail flying behind; frames 1-4 one stride, 5-8 the other; the head stays in the same place across the cell in every frame (at most 1 square up or down), facing right like the FIRST image; the feet touch the ground line in the stride frames.` |
| `lucian_attack.png` | 6 帧：60 60 70 70 80 90 | 3 列 × 2 行，2304×1536 | 第 3 帧（tick 7） | `Animation: BASIC ATTACK, 6 frames, one shot with the front pistol (the bullet is a separate effect - do not draw it): 1 the front arm pulls back a little, 2 aiming right, 3 THE SHOT: the pistol kicks up with a small white-cyan muzzle flash (2-3 squares), 4 the recoil held, 5 lowering, 6 back to the stance. The rear pistol stays raised beside his head.` |
| `lucian_passive.png` | 7 帧：50 50 60 60 60 70 90 | 4 列 × 2 行，最后一格空，3072×1536 | 第 3、5 帧（tick 6、13） | `Animation: DOUBLE SHOT, 7 frames: 1-2 the rear pistol comes down so BOTH pistols point forward at shoulder height, one a little above the other; 3 the upper pistol fires (kicks up, small muzzle flash); 4 it comes back level; 5 the lower pistol fires (kicks up, small muzzle flash); 6 both level; 7 back to the stance. Keep his face visible.` |
| `lucian_skill.png` | 7 帧：60 60 70 70 80 80 90 | 4 列 × 2 行，最后一格空，3072×1536 | 第 4 帧（tick 12） | `Animation: PIERCING LIGHT, 7 frames: 1-3 he turns a little side-on and braces, both pistols pushed forward together at SHOULDER height, a faint glow gathering at the muzzles; 4 THE BEAM: a bright white-cyan flash at both muzzles, the pistols still at shoulder height (the beam itself is a separate effect); 5 holding the shot, a slight recoil; 6 recovering; 7 back to the stance. Keep his face visible.` |
| `lucian_skill2.png` | 8 帧：50 50 50 60 60 70 80 90 | 4 列 × 2 行，3072×1536 | 第 6 帧（tick 14） | `Animation: DASH FORWARD then ARDENT BLAZE, 8 frames: 1 he crouches into the dash; 2-3 a low flat dive forward to the RIGHT, the body nearly horizontal, both pistols pointing forward, the coat streaming behind (off the ground, never below the feet line); 4 landing in a crouch on the ground line; 5 rising, the front arm reaching toward the target; 6 THE SHOT: the front pistol fires with a golden muzzle flash; 7 the recoil; 8 back to the stance.` |
| `lucian_skill2_back.png` | 8 帧：50 50 50 60 60 70 80 90 | 4 列 × 2 行，3072×1536 | 第 6 帧（tick 14） | `Animation: DASH BACKWARD then ARDENT BLAZE, 8 frames: 1 he pushes off; 2-3 he leaps BACKWARD to the LEFT while still facing right, leaning back, both pistols pointing forward at the enemy, the coat flying forward (above the feet line); 4 landing on the ground line; 5-8 like frames 5-8 of the forward dash: the front arm reaching out, the shot with a golden muzzle flash, the recoil, back to the stance.` |
| `lucian_ult.png` | 4 × 75（循环） | 4 列 × 1 行，3072×768 | 第 1、3 帧交替开枪 | `Animation: THE CULLING, 4 frames, a seamless fast loop: a planted wide stance, both pistols held forward at chest height, firing one after the other (the bullets are a separate effect): 1 the upper pistol kicks up with a small muzzle flash, 2 both level, 3 the lower pistol kicks up with a small muzzle flash, 4 both level. The legs, the body and the head do not move; only the pistols and the coat tail.` |
| `lucian_hit.png` | 2 × 100 | 2 列 × 1 行，1536×768 | — | `Animation: HIT, 2 frames: 1 jolted back by a blow, the pistols thrown up a little, 2 recovering toward the stance.` |
| `lucian_dead.png` | 8 帧：100 100 100 100 120 150 150 400 | 4 列 × 2 行，3072×1536 | — | `Animation: DEATH, 8 frames: struck, he staggers backward, falls to his knees and then onto his back on the ground line; the pistols drop from his hands and lie beside him from frame 5; the last frame lies still. Only here the body may reach 2 squares below the feet line.` |

## Claude 导入时（给 Claude 看）

- 交回的 9 张 `lucian_<动作>.png` 和已拼好的 `lucian_idle.png`、`lucian_native.png` 放进 `assets/source/native/`，`lucian_cells.json` 换成这一版（新身高）。
- 先查：8×8 网格、只用造型图的颜色、脚底线、每帧的头和造型图一致（眼睛位置、大小）、描边只有一圈；需要时整理（参考阿狸会话的 `tidy_codex18.py`：描边毛刺、内侧黑圈、杂点；每帧的脸贴回造型图的脸）。
- `import_native.py --hero lucian`：`EYES` 用虹膜色 `#3F6A74`；然后重新量子弹、Q 光束载体、R 子弹的高度（`y_offset`）、头像截取点，重跑 `preview_lucian.py`。
