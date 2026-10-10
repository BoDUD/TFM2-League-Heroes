# 赛娜：照英雄联盟原版动作画动作帧（第 2 步，给 Codex 的提示词）

> 造型已定稿（用户选的 2_40：兜帽顶到脚底 40 格，`design/senna_design.png`）。这一步画动作：**每一帧单独生成一张图**，直接画在 1024×1024 画布（128×128 格 ×8）上，脚底在第 99 行（红线），站位点在蓝十字。**整个人一起画**（头、身体、手脚、飘带、遗物炮同一个姿势里一起画），不要贴头、不要先放固定的头再在下面画身体。
> - **长相、比例、衣服、遗物炮的大小照造型图**；**动作照英雄联盟**：`frames/<动作>_<帧>/2_league_game.png`（原版按游戏尺寸，看姿势、动作幅度和站位）和 `3_league_hd.png`（原版高清，看腿、胯、手、炮的位置）。英雄联盟的身体更瘦、炮更长更平，**不要照它的体型和炮的大小**。
> - **遗物炮每帧都要完整、笔直**：金爪握把、带深色圆眼的金环、酒红翅板（金边）、水晶刃、圆筒都在，不能断、不能弯、不能缺；只按原版这一帧的方向转。**炮口是酒红翅板那一头**（开炮从这头打出去），金爪是握把。
> - 像素：每格一个 8×8 方块对齐同一网格；**只用造型图的 27 色**；一圈近黑描边 `#1E1424`；没有抗锯齿、半透明、杂点。
> - **脚底第 99 行以下什么都不能有**（游戏在脚下画血条）；3/4 正面朝右，脸看得见，炮朝图的右边开；不画背影、不倒立。
> - **只画角色和炮**：光束、炮口火光、黑雾、灵魂、水晶碎片都是单独的特效，不要画。
> - 待机不用画（我们的工具用造型图生成待机呼吸）。
> - 交付到 `outputs/senna-strips/`：每帧一张 `<动作>_<帧>.png`（1024×1024，例如 `run_1.png`），**生图原稿**放 `raw/`（没做任何缩放、移动、重采样的那张），**最后**写 `HANDOFF.md`，最好再打成 `senna_strips_done.zip`。**生成以后不要再移动、缩放、重采样画好的身体部件**——不对就重新生成。

## 附图

| 文件 | 内容 |
|---|---|
| `design/senna_design.png` | **定稿造型** ×8（128×128 格，透明底）；每一帧都照它 |
| `design/senna_head.png` | 造型图的头 ×16，只是看头该画成什么样，**不要贴** |
| `design/senna_cannon.png` | 造型图的遗物炮 ×16，看炮每个部件，**不要贴** |
| `frames/<动作>_<帧>/1_design.png` | 同定稿（每帧文件夹里一份，方便一起附上） |
| `frames/<动作>_<帧>/2_league_game.png` | 英雄联盟这一帧，按游戏尺寸，站位点挪到我们的站位点；红线脚底，蓝十字站位点 |
| `frames/<动作>_<帧>/3_league_hd.png` | 英雄联盟这一帧的高清渲染 |

## 每一帧（每帧附 1_design、2_league_game、3_league_hd 三张图，用下面的通用提示词，把 `[motion]` 换成这一帧的英文）

| 文件 | 帧时长 | 动作 | `[motion]` |
|---|---|---|---|
| `run_1.png` | 125 ms | 跑步 1：跑步：近侧腿向前迈，远侧腿向后高踢 | running to the right: the near leg (image right) reaching forward, the far leg kicked back with its heel high |
| `run_2.png` | 125 ms | 跑步 2：两腿交错：近侧膝盖抬起，远侧脚在后面离地 | running: the legs passing under her, the near knee up, the far foot leaving the ground behind |
| `run_3.png` | 125 ms | 跑步 3：远侧腿向前，近侧腿在后蹬地 | running: the far leg now reaching forward, the near leg pushing off behind |
| `run_4.png` | 125 ms | 跑步 4：近侧腿向后高踢，远侧脚在前着地 | running: the near leg kicked back with its heel high, the far foot planted ahead |
| `run_5.png` | 125 ms | 跑步 5：同第 1 帧，身体低一格（颠一下） | running: like frame 1 again, the body one square lower (the bounce) |
| `run_6.png` | 125 ms | 跑步 6：同第 2 帧，低一格 | running: like frame 2, the body one square lower |
| `run_7.png` | 125 ms | 跑步 7：同第 3 帧 | running: like frame 3 |
| `run_8.png` | 125 ms | 跑步 8：同第 4 帧 | running: like frame 4 |
| `attack_1.png` | 70 ms | 普攻 1：压低成大弓步：近侧膝前弯、远侧腿后伸；炮放平在腰间，金爪握把在身后，酒红翅板和水晶刃（炮口）朝右 | drops into a low, wide lunge facing right: the near knee bent forward, the far leg stretched back; the cannon brought down level at her hip, the claw grip at her back, the maroon wing plates and the crystal reaching forward to the right (the muzzle) |
| `attack_2.png` | 80 ms | 普攻 2：同样的弓步再低一点，炮平端朝右 | the same lunge, a little lower, the cannon level and aimed right |
| `attack_3.png` | 100 ms | 普攻 3：弓步稳住，顺着炮瞄准 | the same lunge, steady, aiming along the cannon |
| `attack_4.png` | 90 ms | 普攻 4：开火：弓步不变，炮被后坐力推后一格 | FIRE: the same lunge, the cannon pushed back a square by the shot |
| `attack_5.png` | 110 ms | 普攻 5：后坐：身体抬起，炮口被顶得朝右上，金爪握把落到腰间 | recoil: her body rises, the cannon kicked up - the muzzle pointing up-right, the claw grip down at her hip |
| `attack_6.png` | 120 ms | 普攻 6：收回：重新压低，炮放平 | recovering: back into a lower stance, the cannon level again |
| `skill_1.png` | 70 ms | Q 黑暗洞灭 1：蹲在炮后，把炮从肩上甩下来：炮斜着，金爪握把在肩，炮口朝前下方 | crouched behind the cannon, swinging it down from her shoulder: the cannon diagonal, the claw grip up at her shoulder, the muzzle down-forward near her feet |
| `skill_2.png` | 80 ms | Q 黑暗洞灭 2：继续甩：炮更陡，她站起来 | still swinging: the cannon steeper, she rises |
| `skill_3.png` | 90 ms | Q 黑暗洞灭 3：站直，双手握炮，炮口朝前下方 | standing, the cannon pointing down-forward, both hands on it |
| `skill_4.png` | 120 ms | Q 黑暗洞灭 4：开火：炮抬到胸口高度平端朝右，炮口的翅板张开 | FIRE: the cannon raised level at chest height, aimed straight right, the wing plates opening at the muzzle |
| `skill_5.png` | 100 ms | Q 黑暗洞灭 5：炮平端，后坐力让她微微后仰 | the cannon level, the shot's recoil leaning her back a little |
| `skill_6.png` | 100 ms | Q 黑暗洞灭 6：炮继续平端，身体后仰，远侧脚后撤 | holding the cannon level, leaning back, the far foot back |
| `skill2_1.png` | 60 ms | W 无尽厮守 1：压低下蹲，炮斜着放在身前 | crouching low, the cannon held diagonally down in front of her |
| `skill2_2.png` | 70 ms | W 无尽厮守 2：蹲得更低，蓄势，炮仍斜着 | crouching lower, gathering, the cannon still diagonal |
| `skill2_3.png` | 70 ms | W 无尽厮守 3：蹲着把炮甩平，朝右瞄准 | swinging the cannon up level, aimed right, still crouched |
| `skill2_4.png` | 110 ms | W 无尽厮守 4：开火：蹲着，炮平端朝右，被后坐力推后 | FIRE: crouched, the cannon level and aimed right, pushed back by the shot |
| `skill2_5.png` | 90 ms | W 无尽厮守 5：站起来，把炮甩到身后近侧腰边，金爪朝下，另一只手伸出 | standing up, the cannon swung down behind her near hip, the claw grip down, her far hand reaching out |
| `skill2_6.png` | 100 ms | W 无尽厮守 6：站直，炮收在身侧后方，回到待机 | standing, the cannon held behind her at her side, back toward the idle |
| `ult_1.png` | 120 ms | R 暗影燎原 1：压低蹲在炮上方，蓄力 | crouching low over the cannon, gathering |
| `ult_2.png` | 120 ms | R 暗影燎原 2：站起，把炮竖着举到身前 | rising, lifting the cannon upright in front of her |
| `ult_3.png` | 150 ms | R 暗影燎原 3：蓄力：站直，双臂向右把炮平举到肩高，翅板张开 | CHARGE: standing tall, both arms out to the right holding the cannon level at shoulder height, the wing plates opening |
| `ult_4.png` | 160 ms | R 暗影燎原 4：蓄力：同上，炮再高一点，翅板全开 | CHARGE: the same, the cannon a little higher, the wings fully open |
| `ult_5.png` | 200 ms | R 暗影燎原 5：把炮收到胸前，炮口朝右下 | bringing the cannon down to her chest, aimed down-right |
| `ult_6.png` | 120 ms | R 暗影燎原 6：开火：炮在胸前平端朝右，双脚站稳 | FIRE: the cannon level at her chest, aimed straight right, her feet set |
| `ult_7.png` | 120 ms | R 暗影燎原 7：持续开火：同上，后坐力让她后仰 | firing: the same, the recoil leaning her back |
| `ult_8.png` | 100 ms | R 暗影燎原 8：持续开火：保持 | firing: the same, holding |
| `hit_1.png` | 100 ms | 受击 1：受击：身体后仰退缩，炮被顶在肩上 | hit: flinching back, the body leaning back, the cannon pushed up against her shoulder |
| `dead_1.png` | 100 ms | 倒地 1：重创：向后踉跄，炮从手中滑落 | hit hard: staggering back, the cannon slipping from her hands |
| `dead_2.png` | 100 ms | 倒地 2：单膝跪下，炮掉在身前 | dropping to one knee, the cannon falling in front of her |
| `dead_3.png` | 120 ms | 倒地 3：单膝跪地前倾，炮躺在身前地上 | on one knee, bent forward, the cannon lying on the ground in front |
| `dead_4.png` | 150 ms | 倒地 4：再低一点，一只手撑地 | sinking lower, one hand on the ground |
| `dead_5.png` | 200 ms | 倒地 5：侧身倒下 | falling onto her side |
| `dead_6.png` | 400 ms | 倒地 6：躺在地上不动，炮在身边 | lying on the ground, still, the cannon beside her |

## 通用提示词

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every square an 8x8 block, 128x128 squares) - her exact look, proportions, colours and pixel style; do not redesign anything. SECOND: one frame of the same animation from League of Legends at game size on the same canvas (the red line is the feet line, the blue cross the standing point) - copy the POSE, the size of the motion and where she stands from it, not its blurry look or its slim body. THIRD: the same League frame rendered large - read the pose from it: where each leg and foot is, how the hips and the body lean, where both hands are, how the relic cannon is held and where it points.
The character (as in the FIRST image): Senna - dark brown skin, green eyes, red lips, long black locs with gold rings, a short white hood with a gold edge, a long pale teal-white sash, a plum-purple top with a bare midriff, dark purple-black leggings, purple gloves, pale grey-teal boots with gold toes; and the RELIC CANNON: at one end the gold claw GRIP (two hooked gold claws), in the middle a gold ring with a dark eye, at the other end the MUZZLE - the long dark maroon wing plates edged in gold with the pale teal-white crystal blade and the teal drum under them. She fires from the maroon wing end.
Task: draw ONE frame: this character in the THIRD image's pose - [motion]. Draw the WHOLE figure at once - head, neck, body, both arms, both legs, the sash and the cannon in one pose - so the head sits on the neck and moves with the body. The head as the FIRST image's head (the same size, hood, locs, face with two green eyes and red lips), only moved with the body. The cannon as the FIRST image's cannon - the same size (shorter than League's), complete and STRAIGHT, every part there (claws, ring with its eye, maroon plates with their gold edges, crystal blade, drum), never broken, bent or cut off - only turned to where League's cannon points in this frame. Proportions and clothes from the FIRST image: standing upright she is 40 squares from the top of the hood to the soles, the same big head, the same body width, the arms 2 squares thick inside a 1-square outline with whole hands, the legs 3 squares thick with bending knees, the same boots.
Pixel rules (most important): every square one crisp 8x8 block on one 8-px grid of a 1024x1024 canvas, nothing smaller, no anti-aliasing, no blur, no half-transparent pixels. ONLY the FIRST image's 27 colours. ONE outline: a 1-square near-black (#1E1424) outline round the silhouette, each material's own dark shade inside it; no second black ring, no stray black squares, no dithering or noise.
Place: the soles of the standing foot (both, when both stand) on square row 99 (pixels 792-799, the red line) - in a fall her lowest point; NOTHING below it (the game draws the health bar there); her place across the canvas like the SECOND image (a lunge or a fall moves her the way the SECOND image does). Her cannon may reach below the feet only if it rests on the ground - never below row 99. 3/4 front view facing right like the FIRST image, the face visible; the cannon fires to the RIGHT of the image; never her back, never upside down. No effects (no beam, no muzzle flash, no black mist, no souls, no shards) - only the character and her cannon.
Output: 1024x1024 PNG, transparent background (if impossible: solid #00FFFF). No grid lines, no text, no guide marks.
Before finishing, check: 8x8 squares on one grid; only the FIRST image's colours; the head and the cannon as big as in the FIRST image; the cannon whole and straight; both hands, both boots; nothing below row 99; the pose matches the THIRD image.
```

## 交回前自查

- [ ] 41 张都在：run_1–8、attack_1–6、skill_1–6、skill2_1–6、ult_1–8、hit_1、dead_1–6；
- [ ] 每张 1024×1024，严格 8×8 网格，只用造型图的 27 色，透明度 0/255；
- [ ] 头和造型图一样大，脸看得见（两只绿眼）；遗物炮和造型图一样大、完整笔直；
- [ ] 站立帧兜帽顶到脚底 40 格；脚底在第 99 行，下面没有像素；
- [ ] 姿势和英雄联盟这一帧一样（腿、胯、手、炮的方向），不是站着不动；
- [ ] 没有特效；附生图原稿；最后写 `HANDOFF.md`。
