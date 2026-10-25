# 机械公敌 兰博：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**（上一包 `rumble-sized-v4` 的 `rumble-A/B.png` 就是把大图最近邻压进一个框里、横竖压得还不一样，这样不行）。
> - 第 0 步你画的 **B 稿**（`1_picture_B.png`，更 Q 的那张）**样子、颜色、比例用户认可了，全照它**：蓝毛约德尔人、亮蓝莫西干头、额头上推着的红镜片金框护目镜、黄眼睛、坏笑；黄铜色带锈的敞口驾驶舱、往前伸的长喷火炮管（红箍）、后面那只机械手握着的**带刺铁球**、背上两个红头火箭舱、短粗的关节腿和红色圆盘脚。
> - 这一步要画成**游戏里的格子数**：**从莫西干头顶到红色圆盘脚底 63 格**。我把图直接缩到这个格子数（`2_target_B.png`）：**大小、位置、姿势对，细节是缩坏的**（脸只剩几个色块、锈斑碎成杂斑）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 4 px 一格，约 161 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**每格 12 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 同一段提示词画**两张**（B-1、B-2），都是 3/4 正面朝右、同一个待机姿势，用户从里面挑。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_B.png` 的浅灰线每 5 格一条）。
- 每格 **12 px**；照 `2_target_B.png` / `3_layout_B.png`：莫西干头顶 **y = 432**（橙线），他的眼睛约 **y = 648**（蓝线），红色圆盘脚底 **y = 1188**（红线）：**63 格高、约 92 格宽**（铁球和炮管算在宽里）。
- 全在画布里，莫西干、耳朵、火箭舱、铁球、炮管不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的他的头（8 倍），看位置和颜色。

- **兰博的脸**（最要紧）：**大头**（头连耳朵和莫西干约占全身高的三分之一，和 B 稿一样）；蓝色的毛 3 档、白色的嘴套和下巴，朝右前方；**两只黄眼睛一样高**：近的那只（画面左边）**3 × 2 格**、远的那只 **2 × 2 格**，各一格黑瞳、一格亮黄、一格白高光；眉毛 1 格、往下压，显得坏；粉红色的小鼻子 1–2 格；**坏笑**：一条黑色的嘴线，露出一排**白牙**（1 格高）。
- **头发和耳朵**：**亮蓝色的莫西干**往上往后翘（3 档，一缕一缕的尖，最高点就是它的尖）；**一对大尖耳朵**（近的那只往左后方伸、耳内粉色 2 档；远的那只竖在右边）。
- **护目镜**：两个**红色镜片 + 金色镜框**（八角形的框），推在额头上（近的大、远的小），**不挡眼睛**。
- **身上**：棕色皮夹克（2–3 档）、金色扣子，白毛的胳膊、蓝色的手抓着驾驶舱前沿的**红色操纵杆**。
- **机甲**：**黄铜 / 橄榄色的敞口驾驶舱**（3–4 档 + 一档亮边，几块锈斑用暗一档的整格表示，铆钉一格亮）；**长喷火炮管**往画面右边伸出、稍微朝下（黄铜色，几道**红色箍**，炮口黑的，**不要火**），炮管上绕着**黑色管子**；**后面那条胳膊**（画面左边）是黑色关节加黄铜护甲，机械手握着一个**带刺的黑铁球**（4–6 根银色尖刺，每根 2–3 格）；背上两个**火箭舱**（黑灰色筒身、**红色圆头**、金色箍）；**短粗的黑色关节腿**（金色齿轮关节），脚是**红色的大圆盘**（红 2 档 + 黑色鞋底一圈）。
- 近的腿（画面左）全亮，远的腿暗一档；**两腿之间、铁球和身体之间、炮管和身体之间空出来看得见背景**。
- **一圈 1 格的近黑外描边**，连续不断（管子、炮管、铁球的尖刺也要描边）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的克烈、布里茨、厄加特，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（火焰、烟、电光、火箭尾焰、鱼叉都不画）。

## 附图（压缩包 `rumble_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_B.png` | 第 0 步你画的 B 稿：**样子、颜色、比例全照它** |
| `2_target_B.png` | 直接缩到 63 格：**只看大小、位置、姿势**，细节是坏的 |
| `3_layout_B.png` | 带网格和三条线（橙 = 莫西干头顶，蓝 = 他的眼睛，红 = 脚底） |
| `4_head.png` | 读回的他的头（8 倍）：位置和颜色 |
| `style/5_style_kled.png` `6_style_blitzcrank.png` `7_style_urgot.png` | **只看风格** |

## 提示词（B-1、B-2 各画一次，同一段；附 1_picture_B、2_target_B、3_layout_B、4_head、style 三张）

```text
Attached: 1 the character's approved picture (THE LOOK, COLOURS AND PROPORTIONS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = the tip of his mohawk, blue = his eyes, red = the bottom of the feet), 4 his head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 12 px, aligned on one grid starting at the canvas corner (0, 0). THE LITTLE BLUE-FURRED BIG-EARED PILOT IN HIS COMPACT BRASS SCRAP-METAL MECH at rest in 3/4 view facing right, the pose of images 1-2: the mech standing on its short jointed legs, the long flamethrower cannon held forward and a little down on the image right, the spiked iron ball held low by the back arm's mechanical hand on the image left, the pilot leaning out of the open cockpit with his big head; the tip of his mohawk at y 432, his eyes at about y 648, the bottom of the red disc feet on y 1188 - 63 squares tall, about 92 squares wide. Every detail in whole 12-px squares - never smaller squares. Do NOT shrink or squeeze image 1 - redraw it square by square.
HIS FACE (most important): a BIG chibi HEAD (with the ears and the mohawk about a third of the whole height, as in image 1); BLUE FUR in 3 shades with a WHITE muzzle and chin, turned to the front-right; TWO YELLOW EYES at the SAME height: the near one (image left) 3x2 squares, the far one 2x2, each with one black pupil square, one bright yellow square and one white highlight; a 1-square brow pressed down (cheeky, mean); a 1-2 square pink nose; a CHEEKY GRIN: a black mouth line with a row of WHITE TEETH (1 square tall).
THE HAIR AND EARS: a BRIGHT BLUE MOHAWK sweeping up and back (3 shades, pointed strands; its tip the highest point); TWO BIG POINTED EARS (the near one reaching back to the image left, pink inside in 2 shades; the far one upright on the right).
THE GOGGLES: two RED LENSES in GOLD octagonal RIMS pushed up on his forehead (the near one bigger), NEVER over the eyes.
HIS BODY: a BROWN leather jacket (2-3 shades) with gold buttons, white-furred arms, blue hands on RED control levers at the cockpit's front rim.
THE MECH: a BRASS / OLIVE open cockpit hull (3-4 shades and one lighter edge, a few rust patches as whole squares a shade darker, rivets one bright square each); the LONG FLAMETHROWER CANNON reaching to the image right (brass, a few RED bands, the muzzle dark, NO fire), black hoses wound round it; the BACK ARM (image left) black joints with brass plates, its mechanical hand holding a BLACK SPIKED IRON BALL (4-6 silver spikes, each 2-3 squares); two ROCKET PODS on its back (dark grey bodies, RED round caps, gold bands); SHORT THICK BLACK JOINTED LEGS with gold gear joints; big RED DISC FEET (red in 2 shades, a black sole ring).
The near leg (image left) in full tone, the far one a step darker; the background visible between the legs, between the iron ball and the body and between the cannon and the body.
A continuous 1-square near-black outline round the whole character (the hoses, the cannon and the spikes too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects (no flame, no smoke, no sparks, no rocket exhaust, no harpoon).
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**每格 12 px**，对齐从 (0, 0) 开始的网格；莫西干头顶 y 432、脚底 y 1188（63 格）；**是重新画的，不是把原图缩小或压扁**。
- **兰博的脸**：大头（约三分之一）；蓝毛白嘴套；**两只黄眼睛一样高**（近 3×2、远 2×2）；压低的眉毛；粉鼻子；坏笑露白牙；亮蓝莫西干；大尖耳朵（耳内粉）；**红镜片金框护目镜推在额头上、不挡眼睛**。**B-1 和 B-2 是同一张脸**。
- 棕色皮夹克；红色操纵杆；黄铜驾驶舱 + 锈斑铆钉；长喷火炮管（红箍、黑管子、**炮口没有火**）；后手握着带刺黑铁球；背上两个红头火箭舱；短粗黑关节腿 + 金齿轮；红色圆盘脚。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/rumble-model/rumble-B-1.png`、`rumble-B-2.png`；原始生成图原样放进 `outputs/rumble-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/rumble-model/HANDOFF.md`，再打包成 `outputs/rumble_model_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/rumble/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw；Codex 常画得比要求的粗或细，按它自己的格子读回），裁到 63 行（keep_axis、脸框保留，`design_sejuani_model.py` 的做法），12 倍下看脸（两只黄眼睛一样高、护目镜不挡眼、牙），和 `review_rumble_size.py` 的邻居并排给用户挑稿 -> `hd/idle.png`（PPU 1.75，莫西干到脚底 36 游戏像素，约 53 宽）。
- 第 0 步（`codex_picture/rumble-sized-v4`）没有用英雄联盟的参考图（容器连不上 raw.communitydragon.org，包里缺附图 1–9）；Codex 按用户的纠正画了原版的带刺铁球（不是提示词里的铁钳爪）：普攻按铁球砸做。A 稿（标准比例）在游戏大小下脸只有几个像素，按 B 做。
