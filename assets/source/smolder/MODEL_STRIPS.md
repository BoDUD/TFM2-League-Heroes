# 斯莫德（炽炎雏龙）：第 2 步，照英雄联盟的动作逐帧画细稿（给 Codex 的提示词）

> 造型已经定了：用户选了你上一轮的**第 3 张**（四条腿站着、大头、尾巴卷起来，`design/smolder_front_draft.png`），**所有动作都用 3/4 正面朝右**（和造型一样，**不画侧面、不转身**）。
> - **这一步只画细稿**：照你那张正面的画法画每一帧（干净的像素画，一格一色），**不要自己缩小、不要按粗格子整理**——前两步的问题都出在缩小，这一次由我这边按格子读回再缩到游戏大小。
> - **大小和位置固定**：每帧都是 **1536×1024 透明画布**；斯莫德站着时和 `design/smolder_front_on_canvas.png` 一样大、一样的位置（那张就是你的正面稿按这一步的大小放在画布上：**脚底在 y=990（红线）**，**四只脚的中间在 x=760（蓝十字）**，角尖约 y=500）。细稿的格子大约 **6–7 像素一格**（和正面稿在这张画布上的格子一样大），干净、整齐、一格一色。
> - **每帧一张图**：`now/smolder_<动作>_<n>.png` 是**骨架**——英雄联盟里这一帧的 3D 模型，已经按造型的大小放在同一张画布上：**姿势、位置、身高照它**（起飞、立起来的高度也照它）。`guide/` 是同一张加了线：**红线 = 脚底线**，**蓝十字 = 站位点**，**洋红色轮廓 = 站着时造型的外轮廓**（大小参考），浅灰线每 50 像素一条——对位用，**不要画进图里**。
> - **长相、比例、颜色、细节全部照正面稿**（「骨架 + 皮囊」）：骨架是 3D 渲染，只看姿势，**不要照它的写实比例**；斯莫德是圆滚滚的 Q 版小龙（头大、腿短）。
> - **头每帧都是同一个**：杏橙色的脸、**一大一小两只青绿大眼睛**（近侧大、远侧在头的边上）、咧嘴笑 + 小白牙、深红鳞冠 + 紫纹、扇形耳鳍、青绿叶片鳞刺、两只短青绿小角 + 两小撮橙黄火苗；**3/4 朝右前方**，**不要画正脸、不要侧脸、不要背对镜头**（英雄联盟里 Q、W 有几帧他的脸转向镜头或低头——**我们不转**，脸一直朝右前方，只是抬头、低头、张嘴、闭眼）。表情可以变：喷火 / 喊叫时**嘴张大**，打喷嚏那一帧**眼睛闭上**。
> - **尾巴永远不碰地**：骨架里的尾巴常常拖在地上、或在飞的时候垂到红线以下——**一律画成造型那样往上卷在身后**（随动作摆动），尾巴尖在半空。**红线以下什么都不能有**（倒下的帧除外：照骨架躺在红线上）。
> - **翅膀**：平时收起来披在背上像斗篷（和造型一样）；只有 Q、W、E、R 里骨架张开翅膀的帧才张开：**翅膀外面深海军蓝 / 深紫 + 青绿鳞，翼膜里面浅杏色，往边上渐变成深红 → 粉红**；张开的翅膀要完整画在画布里（翅尖碰到画布边就稍微收一点）。
> - **一律 3/4 正面朝右**（和造型一样）：近侧（画面左边那条）的腿颜色亮，远侧的腿暗一档、稍高；四条短腿，跑的时候照骨架前后交替（腿是圆滚滚的短腿，不要折成怪角度、不要拉长）。
> - **不画特效**（火球、龙息、喷嚏的火花、飞行的风、妈妈的火焰都在第 3 步单独画；头顶两小撮火苗算身体，要画），**不画地面和影子**；出招一律朝画面右边。
> - 交付到 `outputs/smolder-strips/`：每帧 `smolder_<动作>_<n>.png`（1536×1024、真透明背景、细稿原样）；生图原稿放 `raw/`；**最后**写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）；最好打成一个 zip（`smolder_strips_done.zip`）。
> - 一个动作里的几帧，**画后一帧时附上前一帧**，让龙、头、翅膀一样大。

## 要画的帧（42 帧，全部 3/4 正面朝右）

| 文件 | 动作 | 这一帧画什么（身体照骨架；头、尾巴、翅膀按这里） |
|---|---|---|
| `smolder_run_1..8.png` | 跑步（8 帧循环，四条腿小跑） | 朝右小跑，抬头笑；四条短腿照骨架前后交替（对角的两条腿一起动）；翅膀收着披在背上，随步子轻轻颠；尾巴往上卷、随步子左右摆，不碰地 |
| `smolder_attack_1.png` | 普攻：吐一颗小火球 | 准备：身子微微下蹲，头往后缩一点 |
| `smolder_attack_2.png` | | 头再往后仰，腮帮子鼓起来（憋火） |
| `smolder_attack_3.png` | | 出手：头朝右前方一伸，嘴张开（这一刻火球从嘴里飞出去，火球是特效，不画） |
| `smolder_attack_4.png` | | 跟随：头还伸在前面，前爪微微离地一跳 |
| `smolder_attack_5.png` | | 回到造型的站姿 |
| `smolder_skill_1.png` | Q 超级灼热龙息 | 吸气：翅膀半张开，胸口鼓起，头微微抬 |
| `smolder_skill_2.png` | | 翅膀张开，身子压低、前爪撑地，嘴张大 |
| `smolder_skill_3.png` | | 出手：朝右前方喷出龙息，嘴张到最大，翅膀张开往后（龙息是特效，不画） |
| `smolder_skill_4.png` | | 同上，喷完的一瞬，翅膀开始收 |
| `smolder_skill_5.png` | | 回到站姿，翅膀收回成斗篷 |
| `smolder_skill2_1.png` | W 阿嚏！ | 鼻子发痒：头抬起，眼睛眯起来，鼻子皱 |
| `smolder_skill2_2.png` | | 吸气「阿——」：后腿站起来、上身立起，翅膀张开，头往后仰，嘴张开 |
| `smolder_skill2_3.png` | | 仰到最高：头往后仰到底，翅膀张得最大 |
| `smolder_skill2_4.png` | | 「嚏！」：头猛地朝右前下方一甩，**眼睛闭上**，嘴张开，翅膀往前收，前爪落地（喷嚏火花是特效，不画） |
| `smolder_skill2_5.png` | | 回到站姿，晃晃脑袋 |
| `smolder_skill2_e_1.png` | E 扑棱扑棱扑棱！（起飞） | 下蹲蓄力，翅膀开始张开 |
| `smolder_skill2_e_2.png` | | 起跳：四条腿离地，翅膀往上举 |
| `smolder_skill2_e_3.png` | 飞行（第 3–6 帧循环） | 在半空：翅膀扇到最上面，四条腿收在肚子下，尾巴往后上方卷 |
| `smolder_skill2_e_4.png` | | 翅膀扇到水平，身体略往前倾 |
| `smolder_skill2_e_5.png` | | 翅膀扇到最下面，身体被托高一点 |
| `smolder_skill2_e_6.png` | | 翅膀往上回到水平 |
| `smolder_skill2_e_7.png` | | 落地：翅膀张开减速，四条腿往下伸 |
| `smolder_skill2_e_8.png` | | 回到站姿，翅膀收回成斗篷 |
| `smolder_ult_1.png` | R 妈——！ | 翅膀往前裹住脑袋（像披风罩住头） |
| `smolder_ult_2.png` | | 缩成一团，被翅膀裹着 |
| `smolder_ult_3.png` | | 猛地后腿站起来、上身立直，头往后仰，**嘴张到最大大喊「妈——！」**，翅膀甩到身后 |
| `smolder_ult_4.png` | | 还在喊，前爪张开，身体略往前倾 |
| `smolder_ult_5.png` | | 回到站姿 |
| `smolder_dead_1.png` | 死亡 | 被打中，往后一缩，眼睛闭上 |
| `smolder_dead_2.png` | | 一屁股坐下去 |
| `smolder_dead_3.png` | | 晃了晃，翅膀耷拉下来 |
| `smolder_dead_4.png` | | 往侧边倒下去（还是面朝右前方，不转身） |
| `smolder_dead_5.png` | | 侧躺在地上，翅膀摊开，眼睛闭着 |
| `smolder_dead_6.png` | | 同上，静止（最后一帧） |

## 提示词

每帧一次，附图（工具一次最多 5 张时按这个顺序）：
1. `now/smolder_<动作>_<n>.png`（骨架）
2. `design/smolder_front_draft.png`（你的正面稿：长相、画法）
3. `design/smolder_front_on_canvas.png`（同一张正面稿在这一步的大小和位置）
4. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）
5. `guide/smolder_<动作>_<n>.png`（加了线的骨架：脚底线、站位点、站着时的轮廓）

```text
Image 2 is your own detailed pixel-art drawing of this character: Smolder, a small cute baby dragon in 3/4 FRONT view facing image right, standing on four short legs - a big head with an apricot-orange scaly face and a pale cream chin, two big teal eyes (the near one big, the far one by the head's edge), a happy grin with small white teeth, a dark crimson crest with a purple stripe, big fan-shaped ear fins, teal leaf-like spikes along the fins, cheeks and neck, two short teal horns each with a small orange-yellow flame tuft, a pale cream belly with belly scales, the wings folded over his back like a cape (dark navy and purple with teal scales, fading to crimson and pink), dark wine-red legs with navy scale plates and small navy claws, and a tail curled up behind him, red on top and apricot underneath, ending in a dark navy fin. Image 3 is that drawing placed on this frame's 1536x1024 canvas at the size and place he must have when standing (soles on y 990, the middle of the feet on x 760).
Image 1 is a 3D render of the same character from the game in THIS FRAME'S POSE, already scaled and placed on the same canvas: copy its pose, its place and its size - NOT its 3D look and NOT its realistic proportions. Image 5 is the same with guide lines (red: the soles' line, blue cross: the standing point, magenta: the standing figure's outline). (Image 4, when attached, is the previous frame of the same action: keep him exactly as big.)
Draw ONE frame: <WHAT>
Rules: a 1536x1024 PNG with a genuine transparent background; crisp clean pixel art drawn like Image 2 (even squares of about 6-7 output pixels at this size, every square one flat colour, a one-square near-black outline, 3-4 flat shades per material, no dithering, no gradients, no soft glow, no anti-aliasing); the character as big as Image 3 with Image 2's round chibi proportions (big head, short legs); he stays in 3/4 FRONT view facing image right like Image 2, never a front face, never in profile, never turned away, even where Image 1 turns his face to the camera or down; his head - the face, both teal eyes, the grin, the crest, the ear fins, the spikes, the horns with their little flames - the same as Image 2 in every frame, only moved, tilted, the mouth opened or the eyes shut where this frame says so; the TAIL always curled up behind him like Image 2, never touching or crossing the red line, even where Image 1's tail drags or hangs down; the wings folded like a cape unless this frame opens them, and opened wings drawn whole inside the canvas; the near legs (image left) in full tone, the far legs a shade darker; the feet on the red line unless this frame is in the air or lying down, nothing below the red line; no effects (no fireball, no fire breath, no sneeze sparks, no wind, no big dragon, no glow, no dust) - only the two little flame tufts on his horns; no ground, no shadow, no text, no guide lines. Do NOT reduce it or re-grid it to bigger squares: deliver the detailed drawing as drawn.
```

`<WHAT>` 按上表换成英文：

- run 1–8：`trotting to the right, frame <n> of an 8-frame loop: his four short legs moving as in Image 1 (diagonal pairs together), head up, smiling; the folded wing cape bouncing a little with the step; the tail curled up behind him swinging a little, never touching the ground`
- attack 1–5：`basic attack, spitting a small fireball, frame <n> of 5: <1: crouching a little, the head pulled back | 2: the head further back, the cheeks puffed (holding the fire) | 3: the release: the head thrust forward to the right, the mouth open (the fireball is not drawn) | 4: the follow-through: the head still forward, the front paws hopping a little off the ground | 5: back to the standing pose of Image 2>`
- skill 1–5：`Super Scorcher Breath, frame <n> of 5: <1: breathing in: the wings half open, the chest puffed, the head a little up | 2: the wings spread, the body low, the front paws braced, the mouth wide | 3: the release: breathing fire forward to the right, the mouth open as wide as it goes, the wings spread back (the fire is not drawn) | 4: the same at the end of the breath, the wings starting to fold | 5: back to the standing pose, the wings folded into the cape>`
- skill2 1–5：`Achooo!, a big sneeze, frame <n> of 5: <1: the nose tickles: the head lifting, the eyes squinting, the nose wrinkled | 2: breathing in "ah-": rearing up on the hind legs, the upper body upright, the wings spread, the head thrown back, the mouth open | 3: the highest point: the head back as far as it goes, the wings at their widest | 4: "CHOO!": the head snapping forward and down to the right, the EYES SHUT, the mouth open, the wings swinging forward, the front paws landing (the sneeze sparks are not drawn) | 5: back to the standing pose, shaking his head a little>`
- skill2_e 1–8：`Flap, Flap, Flap - flying, frame <n> of 8: <1: crouching to jump, the wings starting to open | 2: jumping off: all four legs off the ground, the wings raised | 3: in the air (loop frame 1 of 4): the wings at the top of the flap, the legs tucked under the belly, the tail curled up behind | 4: in the air (loop 2): the wings level, the body leaning a little forward | 5: in the air (loop 3): the wings at the bottom of the flap, the body lifted a little | 6: in the air (loop 4): the wings rising back to level | 7: landing: the wings spread to slow down, the four legs reaching down | 8: back to the standing pose, the wings folded into the cape>`
- ult 1–5：`MMOOOMMMM! - calling his mother, frame <n> of 5: <1: the wings wrapping forward round his head like a hood | 2: curled up small inside the wrapped wings | 3: rearing up on the hind legs, the body straight up, the head thrown back, the MOUTH OPEN AS WIDE AS IT GOES shouting for his mom, the wings flung back | 4: still shouting, the front paws spread, leaning a little forward | 5: back to the standing pose>`
- dead 1–6：`dying, frame <n> of 6, always facing the front right (never turned away): <1: hit, flinching back, the eyes shut | 2: sitting down hard on his bottom | 3: wobbling, the wings drooping | 4: toppling over onto his side | 5: lying on his side on the ground, the wings spread out, the eyes shut | 6: the same, still (the last frame)>`

## 交回前请检查

- 42 帧都在，文件名对，每张 1536×1024 透明底，是细稿原样（没有缩小、没有按粗格子整理）。
- 每帧和 `design/smolder_front_on_canvas.png` 一样大，圆滚滚、头大腿短；一直 3/4 正面朝右，不转身、不正脸、不侧脸；头每帧一样（两只青绿眼睛、笑脸、鳞冠、耳鳍、小角 + 火苗）。
- 尾巴每帧都往上卷，不碰红线；翅膀只在骨架张开的帧张开，完整在画布里。
- 脚底在红线上（飞、倒下的帧照骨架），红线以下没有东西；没有特效、地面、影子、文字和辅助线。
- 全部画完后最后写 `outputs/smolder-strips/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每帧用 `tools/art/design_smolder.py` 的流程缩到游戏大小：raw 细稿按自己的格子读回 → 造型的 26 色调色板 → 按 12 px 一格（这一步的比例：一个造型格）面积投票，脚底对齐红线 → 贴造型的脸（同一张脸，只平移；张嘴 / 闭眼的帧按帧手改）→ 补缝 → 补外描边；待机 = 造型（+ 呼吸、尾巴摆）；受击 = 造型平移 + 闪白。
- 6 倍 / 游戏尺寸逐帧自查（rig-deformation-checks、gap-check、tail-off-ground：尾巴不贴地；脸不能被翅膀挡住）再给用户看 GIF；跑步不对就自己按四足交替画腿。
- 写 assets/source/ppu/smolder_<tag>.png / .json、ppu_hd.py PPU 1.5 + lo_ 帧、hd.rs HEROES（league.dll > 0.7.0，先问 SDK 0.6.4 会话和马尔扎哈当时最高号）；按动作条的出手帧重排技能数据的时机再跑一次模拟。
