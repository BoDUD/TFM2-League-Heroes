# 卡尔玛：照英雄联盟原版动作重画动作帧（第 2 步重做，给 Codex 的提示词）

## 这一轮为什么重做

上一轮交回的动作条（`karma_strips_pack_done.zip`）用户没有通过：

1. **头和身体脱节**：头是从造型图整块贴进每一帧的，身体在头下面另画——跑步时头一动不动、身体在下面晃，头像浮在身体上（用户：「头和身体协调吗」「头和身体移动时还是脱节的啊 合并在一起了」）。
2. **不像英雄联盟**（用户：「这像英雄联盟里面的吗」）：站着的动作腿、胯、裙摆几乎不动，只有一只手臂在动。英雄联盟里卡尔玛的每个动作都是全身的：Q 是前后大弓步加双掌前推，W 是向前深深俯身再伸掌，E 是单手直举过头再向前挥，R 是交叉站、双手合十、长裙片鼓得像帆，普攻是单脚站、手臂甩出再扬到头顶，跑步是两脚交替向后高踢、身体上下弹、裙片一直向后飘。
3. 身体比造型图瘦小（面积只有造型图的 77–92%），腰边的骨翅漏画。

**这一轮的做法：**

- **每一帧把整个人一起画**：头、脖子、身体、两只手臂、两条腿、裙子、玉环、骨翅在同一个姿势里一起画出来，头永远长在脖子上、跟着身体动——弓步和俯身时头随肩膀一起向前，下蹲时一起下沉，起身时一起升高。**不要先放一个固定的头再在下面画身体，不要贴头，也不要用上一轮的贴头脚本。**
- **头照造型图画**：大小、形状、颜色、发型、额饰、耳坠和造型图一样，每帧一样大；只随身体平移，俯身和倒地时可以稍微倾斜。眼睛画准位置即可（两只一样大、同一高度）——交回后我们会把造型图的眼睛统一换上。
- **长相、比例、衣服、骨翅照造型图**（`design/karma_design.png`），**动作照英雄联盟**：`zoom/lol_zoom_<动作>.png`（原版每帧放大、编号，看动作最清楚）、`now/karma_now_<动作>.png`（原版按游戏尺寸取色，看帧数、大小和站位）、`pose/lol_pose_<动作>.png`（原版高清、和 now 同格子同位置）。下面每帧都写了腿、胯、身体、手、裙片、玉环怎么动。`refs/design_vs_league.png` 是造型图和英雄联盟模型并排：哪个部件对应哪个部件（玉环、四片骨翅、长裙片、开衩、靴子）。
- **跑步也照英雄联盟**：原版一圈 1 秒，8 帧 × 125 毫秒（上一轮的 oppi 阿狸骨架这次不用了）。
- 普攻、Q、W、E 的出手帧按英雄联盟真正发招的那一刻重新取过帧，和上一轮的帧不一样，以这次的 now/zoom 为准。
- 待机不用画（`karma_idle.png` 已做好，游戏里的待机动画由我们的工具生成；它也告诉你造型图在格子里多大、站在哪里）。

## 造型图（每一帧都照它）

定稿 `design/karma_design.png`（放大 8 倍，1024×1024）：玉环顶到脚底 42 行，28 格宽，24 色；脚底在第 99 行，两脚中间在第 64 列。

- **头**：翡翠玉环浮在头的后上方（约 13 格宽、5 行高的扁圆环）；黑色齐下巴短发，金色额饰，额前翠绿宝石；深棕皮肤，洋红色大眼睛；粉色流苏耳坠。头发顶到脚底 37 格，头（发顶到下巴）14 格，Q 版大头。
- **骨翅**：四片象牙色小骨翅，头两侧各一片、腰两侧各一片，浮在身边、跟着身体走。
- **身体**：紫色上衣，胸前白色缠布，金边；脖子 1 行，肩膀在第 77–78 行；**身体宽度和造型图一样，不许变瘦小**。
- **手臂**：光着的深棕色手臂，2 格粗加 1 格描边，手掌 2×2 格；伸出去的手臂从肩膀、手肘到手掌是完整的一条，不是 1 像素的细棍。
- **裙子**：图左边（身后）一大片紫色长裙片垂到靴子，下摆是洋红粉色；图右边（身前）高开衩，露出深棕色的光腿；最右边一条窄窄的紫色前裙片。
- **腿和靴子**：腿短（Q 版），胯到脚底约 12 格，3 格粗加描边，膝盖会弯；深蓝色短靴（4 行高）带金色靴口。**左腿从长裙片下面迈出来时，和右腿一样是深棕色的光腿**（两条腿同样的颜色，后面那条可以暗一级），不要发明新的袜子或裤子。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/karma_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图：长相、比例、颜色 |
| `design/karma_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板 |
| `design/karma_head.png`、`_1x.png` | 造型图的头（玉环、头发、额饰、脸、耳坠），**只是给你看头该画成什么样**，不要贴 | 画头时对照 |
| `design/karma_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `now/karma_now_<动作>.png` | 英雄联盟原版按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、每格位置、人物大小 |
| `zoom/lol_zoom_<动作>.png` | 原版每帧放大、编号（红线 = 脚底线，蓝线 = 站位点） | 第三张附图：**动作照这张** |
| `pose/lol_pose_<动作>.png` | 原版高清，和 now 同格子、同位置 | 需要时核对位置 |
| `guide/karma_guide_<动作>.png` | 格子边框、站位点（蓝十字）、脚底线（红线）和线下禁区、**英雄联盟每帧头的位置（绿圈）**、帧号 | 对位用，不要画进图里 |
| `karma_cells.json` | 每帧站位点 `pivot`、头的位置 `head`（格子里第几列、第几行，单位方块）、帧时长 | 整理对位 |
| `karma_idle.png` | 已做好的待机条 | 不用画；看大小和站位 |
| `refs/design_vs_league.png` | 造型图和英雄联盟模型并排 | 部件对应 |
| `refs/karma_picture.png` | 用户选的原画 A | 长相参考（以造型图为准） |

## 规则（每张都一样）

- **整个人一起画，头跟着身体动**（见上）。每帧的头在 `guide/` 绿圈附近（英雄联盟的头在那里）。
- **动作照英雄联盟**：腿怎么迈、胯怎么沉、身体怎么倾、手到哪里、长裙片怎么飞，照 `zoom/` 和下面的逐帧说明；**不是站着不动只抬一只手**。
- **长相、比例、衣服照造型图**：站直时和造型图一样高（玉环顶到脚底 42 格），头一样大，身体一样宽，手臂一样粗，四片骨翅和玉环每帧都在（死亡按表）。
- 像素：每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明；**只用造型图的 24 种颜色**；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑、不要零散的黑格、不要噪点。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 一直是 3/4 正面朝右（和造型图一样），脸始终看得见；推掌、伸掌、施法朝图的右边；**不画背影、不转头、不倒立**。
- **只画角色**：灵弹、火球、连线、护盾、真言光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯青色 `#00FFFF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/karma_design.png`，第二张 `now/karma_now_<动作>.png`，第三张 `zoom/lol_zoom_<动作>.png`。`[animation]` 在下面每张动作图的说明里，`[R]`、`[grid]`、`[size]` 按表。输出文件名 `karma_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - her exact look, proportions, colors and pixel style; do not redesign anything. SECOND: the same animation from League of Legends sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, the layout, the size of the figure and where she stands in each cell, not its blurry look. THIRD: the same League frames rendered large and numbered - copy the MOTION from it: how the legs step, lunge, cross, kick and kneel, how the hips drop, how the body leans and bows, where the hands go, how the long skirt panel swings, flies and billows, how the ring and the prongs lag.
The character: Karma, the Enlightened One - a graceful spirit mage with dark brown skin, a black chin-length bob, a gold circlet with a green gem, big magenta eyes, pink earring tassels, a floating jade dragon ring above and behind her head, four small ivory spirit prongs (one at each side of her head, one at each side of her waist), a violet top with a white wrap and gold trims, a long violet skirt panel at her back (the left of the image) with a magenta-pink hem, a high slit at her front (the right of the image) showing a bare brown leg, a narrow violet front flap, navy short boots with gold tops.
Task: redraw every frame as clean game-size pixel art of the FIRST image's character doing the THIRD image's motion. Draw the WHOLE figure at once in each frame - the head, the neck, the body, both arms, both legs, the skirt, the ring and the prongs together in one pose - so the head always sits on the neck and moves with the body: it goes forward with the shoulders in a lunge or a bow, sinks when she dips, rises when she straightens. Never paste one fixed head and draw a body under it. The head is drawn like the FIRST image's head in every frame (the same size, hair, circlet, face and earrings), only moved with the body (tilted a little only in a bow or the fall).
Motion like League: the legs, the hips and the body move as in the THIRD image (stepping, lunging, crossing, a foot lifted, kneeling); the long skirt panel swings and flies with the motion; never a stiff standing figure with only one arm moving.
Proportions and clothes from the FIRST image, only the pose changes: standing upright she is exactly as tall as the FIRST image (42 squares from the top of the ring to the soles, 37 from the top of the hair); the same big chibi head (14 squares from the top of the hair to the chin); the torso as wide as in the FIRST image, never slimmer; the bare brown arms 2 squares thick inside a 1-square outline with 2x2-square hands, an outstretched arm whole from the shoulder to an open palm; the short legs about 12 squares from the hip to the sole, 3 squares thick, the knees bending; the navy boots 4 rows tall with gold tops. When the left leg steps out from under the long skirt panel it is the same bare brown leg as the right one (both legs the same colors, the farther one may be one shade darker) - no new stockings or trousers. The ring and all four prongs are in every frame (the death: as described).
Pixel rules (most important): every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. ONLY the 24 colors of the FIRST image, no new colors: #030202 #150616 #220C25 #370644 #2C302A #452320 #222048 #42074B #780C4B #5F0970 #825238 #1BB663 #5C7D5F #E3118E #C7864A #C4815A #91CD9F #EEB956 #BAB0AD #ABDCB3 #CAE7C0 #DDDBC4 #F2E9C6 #F5EDE8. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares; no dithering, no noise, no random specks.
Feet line: in every cell the soles of the standing foot are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image.
3/4 front view facing right like the FIRST image, the face always visible; every palm push, point and cast goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (bolts, fireballs, the tether, shields, the mantra glow) - only the character.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x80 squares (768x640 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FFFF cyan). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid; only the FIRST image's colors; the whole figure drawn together, the head on the neck in every frame and as big as the FIRST image's head; the legs, hips and skirt moving like the THIRD image (not frozen); both arms whole with hands, both boots, the ring and the four prongs in every frame; the body as wide and as tall as the FIRST image; no loose pieces, no stray black squares; nothing below the feet line; never her back or upside down; the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准时用；图1 = now 条，图2 = 造型图，图3 = zoom 原版放大）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色；动作看图3（同一组动作的高清放大，编号和图1的帧一一对应）。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块；站直时人物和图2一样高，不能变大也不能变小。
2. 保留每一帧的全身动作：腿怎么迈步、弓步、交叉、抬脚、跪下，胯怎么下沉，身体怎么前倾、俯身、后仰，手到哪里，长裙片怎么飘、怎么鼓起来，都照图1和图3；不要画成站着不动只抬一只手。
3. 整个人一起画：头、脖子、身体、手、腿、裙子、玉环、骨翅在同一个姿势里，头长在脖子上、跟着身体一起动；不要贴一个固定的头。
4. 长相、比例、配色、细节全部换成图2：翡翠玉环、黑色短发、金额饰翠绿宝石、深棕皮肤、洋红大眼睛、粉色流苏耳坠、四片象牙小骨翅（头两侧、腰两侧）、紫色上衣白缠布金边、身后紫色长裙片（洋红粉下摆）、身前高开衩露出深棕光腿、深蓝短靴；头每帧和图2一样大，身体和图2一样宽，手臂一样粗。两条腿都是深棕光腿。
5. 一直是 3/4 正面朝右，脸看得见；推掌、施法朝右；不画特效。
6. 动作：[animation]
背景保持纯青色 #00FFFF，方便抠图。风格保持与图2一致。重点在于精准复刻图1和图3的"动作骨架"，只是换了"皮囊"。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 |
|---|---|---|---|---|
| `karma_run.png`（跑步） | 8 × 125 | — | 4 列 × 2 行，3072×1280 | 第 65 行 |
| `karma_attack.png`（普攻（甩手射出灵弹）） | 6 帧：60 60 70 70 70 70 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1280 | 第 65 行 |
| `karma_skill.png`（Q 心灵烈焰（大弓步双掌前推）） | 6 帧：55 55 60 60 70 70 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1280 | 第 65 行 |
| `karma_skill2.png`（W 坚定专注（前俯身再伸掌）） | 6 帧：55 55 60 60 70 70 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1280 | 第 65 行 |
| `karma_skill_e.png`（E 鼓舞（单手直举过头再向前挥）） | 5 帧：50 50 55 60 55 | 第 3 帧（tick 6） | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 65 行 |
| `karma_ult.png`（R 真言（交叉站、双手合十、长裙片鼓成帆）） | 5 帧：50 50 60 70 70 | 第 3 帧（tick 6） | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 65 行 |
| `karma_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×640 | 第 65 行 |
| `karma_dead.png`（死亡（玉环骨翅碎落、跪下、向前扑倒）） | 8 帧：100 100 100 120 150 150 200 500 | — | 4 列 × 2 行，3072×1280 | 第 65 行 |

## 逐帧动作（照英雄联盟；左右 = 图里的左右，她朝右）

### `karma_run.png` 跑步

1. 左脚踩在胯下，右脚向后高高踢起（脚跟到另一条腿膝盖高）；左手摆在身后
2. 左脚往后滑，右脚贴着左小腿向前摆过来；身体最低（比第 1 帧低 1–2 格）
3. 右脚向前伸出准备落地，左脚在后面蹬地（脚跟抬起）；身体上升
4. 右脚在前、左脚向后踢起，**两脚都离地**（轻轻一跳，最低的脚底比脚底线高 2 格）；身体最高；左手摆到腰前，右手抬到胸口
5. 右脚踩在胯下，左脚向后高高踢起（脚跟到膝盖高）
6. 右脚往后滑，左脚贴着右小腿向前摆过来；身体最低
7. 左脚向前伸出准备落地，右脚在后面蹬地；身体上升；左手往后摆
8. 左脚在前、右脚向后踢起，**两脚都离地**（最低的脚底比脚底线高 2 格）；身体最高；左手摆在身后（接回第 1 帧）

`[animation]`：

```text
RUN, 8 frames x 125 ms = League's run cycle (1 s), running to the right, light and bouncy: the torso upright and tipped slightly forward, the whole upper body (the head, the ring, the shoulders) bobbing together - lowest in frames 2 and 6, highest in frames 4 and 8 (2-3 squares between low and high); each foot plants ahead of the body, slides back under it, then kicks up high behind her (the heel up to the other leg's knee), then swings forward again, the two legs half a cycle apart, so they pass each other twice a cycle; the left arm swings back and forth (behind the hips in frames 1-2 and 8, forward at the waist in frames 4-5), the right forearm stays forward at chest height pumping up and down (highest in frame 4); the long skirt panel streams back to the left the whole time, flapping; the ring and the prongs ride with the head and the shoulders. 1 the left foot planted under the hips, the right foot kicked up high behind; the left hand back behind the hips. 2 the left foot sliding back, the right foot swinging forward low past the left shin; the body at its lowest. 3 the right foot reaching forward to land, the left foot pushing off behind (heel up); rising. 4 the right foot ahead, the left foot kicked up behind, BOTH feet off the ground (a light hop: the lowest sole 2 squares above the feet line); the body at its highest; the left hand forward at the waist, the right hand up at the chest. 5 the right foot planted under the hips, the left foot kicked up high behind. 6 the right foot sliding back, the left foot swinging forward low past the right shin; the body at its lowest. 7 the left foot reaching forward to land, the right foot pushing off behind; rising; the left hand swinging back. 8 the left foot ahead, the right foot kicked up behind, BOTH feet off the ground (the lowest sole 2 squares above the feet line); the body at its highest; the left hand back behind the hips (then frame 1 again).
```

### `karma_attack.png` 普攻（甩手射出灵弹）

1. 肩膀转向右边：右手抬到脸旁（掌心向前），左手移到胯前；右脚跟抬起
2. 蓄力：身体微微升高、重心在左脚，右脚提起收在左脚踝后面（屈膝）；左手前伸到胸口高，右手收到头旁
3. 向右前倾（头和肩膀向右 3–4 格、低 1–2 格），左臂向前远伸到胸口高、张开手掌；右手还在头旁；右脚仍提在后面；长裙片向左后甩
4. **甩出（灵弹从这里飞出）**：身体弹直、两臂大大张开——右臂向右前方甩出到肩高、掌心朝敌人，左臂向左后方甩到肩高；右脚仍提在左脚踝后；裙片向左飘 **← 出手帧**
5. 收势：右臂继续扬到头顶正上方，左臂在左后方；单靠左脚站直，右脚提在后面；玉环和骨翅慢一拍跟上
6. 落下：右手在身前降到头的高度，左手回到胯边，两脚落地，裙摆落回

`[animation]`：

```text
BASIC ATTACK (a spirit bolt), 6 frames, League's quick dancer-like throw: 1 she turns her shoulders toward the right: the right hand comes up beside her face, palm forward, the left hand forward in front of her hips; the right heel lifting. 2 coiling: she rises a little onto the left foot, the right foot lifted and tucked behind the left ankle (knee bent); the left hand forward at chest height, the right hand drawn up beside her head. 3 leaning forward to the right (the head and shoulders 3-4 squares right and 1-2 lower), the left arm reaching far forward at chest height, palm open; the right hand still by her head; the right foot still lifted; the long skirt panel sweeping back to the left. 4 THE THROW (the bolt leaves here): she snaps upright and flings both arms wide - the right arm whips forward to the right at shoulder height, palm open toward the enemy, the left arm swept back to the left at shoulder height; the right foot still tucked behind the left ankle; the skirt panel flaring left. 5 follow-through: the right arm swung on up straight above her head, the left arm out back-left; standing tall on the left foot, the right foot lifted behind it; the ring and the prongs a square behind. 6 coming down: the right hand lowering in front at head height, the left hand back at the hip, both feet down, the skirt settling.
```

### `karma_skill.png` Q 心灵烈焰（大弓步双掌前推）

1. 蓄力：重心后移到左脚（胯往左 1–2 格），右脚轻点（脚跟抬起）；右手收到胸前，左手拉到胯后
2. 上步：右脚向前跨出一大步（离站位点 6–7 格），身体向前下沉（头向右 2–3 格、低 3 格），两手收在胸前；玉环和骨翅被甩在左上方
3. 弓步落地：左腿在身后伸直（脚在站位点左边约 7 格），右膝弯曲（脚在右边约 8 格），胯低 1–2 格；右臂向右前推到胸口高，左手在腰边；长裙片开始往后飞
4. **双掌推出（火球从这里飞出）**：完整的大弓步，两脚相距约 15 格；**两只手臂一起**向右平推到肩高、两个掌心并排张开（左臂从胸前横过去）；上身直立、略靠在后腿上，头朝右看；长裙片像旗子一样向左水平飞出；前面的窄裙片向右甩 **← 出手帧**
5. 保持推掌（同样的弓步），手掌略抬到头高，长裙片仍向后飞
6. 收回：前脚往回收（离站位点约 4 格），身体升高，右臂还在胸前向右伸，左手垂到胯边，裙片落下

`[animation]`：

```text
INNER FLAME (Q), 6 frames, League's Q: a big lunge and a two-handed palm push. 1 wind-up: her weight back on the left foot (the hips 1-2 squares left), the right heel up; the right hand pulled in front of her chest, the left hand back behind the hip. 2 stepping in: the right foot steps far forward (6-7 squares ahead of the standing point), the body coming forward and down (the head 2-3 squares right and 3 lower), both hands gathered in front of the chest; the ring and the prongs left behind up-left. 3 the lunge lands: the back (left) leg stretched straight behind (its foot about 7 squares left of the standing point), the front (right) knee bent (its foot about 8 squares right); the hips 1-2 squares lower; the right arm thrusting forward at chest height, the left hand at the waist; the skirt panel starting to fly back. 4 THE PUSH (the fireball leaves here): the full lunge, the feet about 15 squares apart; BOTH arms thrust straight forward to the right at shoulder height, the two open palms side by side, pushing (the left arm crosses in front of her chest); the torso upright, leaning back a little over the back leg, the head looking right; the long skirt panel flying straight back to the left like a flag; the narrow front flap swinging forward. 5 holding the push (the same lunge), the palms raised a little to head height, the skirt panel still flying back. 6 recovering: the front foot drawing back (about 4 squares ahead), the body rising, the right arm still forward at chest height, the left hand down at the hip; the skirt falling back.
```

### `karma_skill2.png` W 坚定专注（前俯身再伸掌）

1. 聚气：两手抬到胸口高、掌心向前（右手在身前，左手在胯左边），头微抬
2. 前倾：上身向右前方倾（头向右约 5 格、低约 3 格），膝盖弯曲，右手在腰到胸之间向前，左手在腰前；长裙片向后扫
3. 深深前俯：头和肩膀远远探向右前方（头比待机向右约 8 格、低约 2 格），右臂向前上方推到肩高，左手低低在胯前；长裙片向后上方飞起；玉环和骨翅被留在左上方
4. **伸掌（连线从这里发出）**：从前俯中起身，**左臂**向右前方远远伸到胸口高、掌心张开对准敌人，右手举在脸旁；头仍在前面（向右约 5 格） **← 出手帧**
5. 站直，两手都在脸旁：左手掌心向前张开在头的高度，右手在脸颊边——专注地牵着连线；长裙片落回
6. 回到待机：右手在胸前向前，左手垂下，裙片落定

`[animation]`：

```text
FOCUSED RESOLVE (W, the tether), 6 frames, League's W: a deep forward bow, then an open palm thrust at the target. 1 gathering: both hands come up to chest height, palms forward (the right hand in front, the left hand at the left of the hips), the head lifting. 2 leaning in: the upper body tips forward to the right (the head about 5 squares right and 3 lower than in the idle), the knees bending, the right hand forward at waist-chest height, the left hand in front of the waist; the skirt panel sweeping back. 3 a deep forward bow: the head and shoulders far forward (the head about 8 squares right of its idle place and 2 lower), the right arm thrust forward and up at shoulder height, the left hand low in front of the hips; the skirt panel flying up behind; the ring and the prongs left behind up-left. 4 THE TETHER (it leaves here): rising out of the bow, the LEFT arm thrust far forward to the right at chest height, the palm open toward the enemy; the right hand raised beside her face; the head still forward (about 5 squares right). 5 upright, both hands up by her face: the left palm open forward at head height, the right hand by her cheek - holding the tether with focus; the skirt panel dropping back. 6 settling: the right hand forward at chest height, the left hand down; the skirt settling.
```

### `karma_skill_e.png` E 鼓舞（单手直举过头再向前挥）

1. 右手在胸前抬起，左手垂到胯边；左脚向后退半步
2. 右臂向上伸直举过头顶（手到玉环的高度）、手掌张开；左臂向左后下方伸出；身体后仰，头向左约 3–4 格、抬头看手
3. **施放护盾（从这里出）**：同样高举，右掌张开、五指分开在最高处；后仰更多（头和肩膀比待机向左 4–6 格），左手在左后方低处；长裙片向左摆 **← 出手帧**
4. 右臂从头顶向右前方斜着挥下来（手在头的高度偏右），左臂远远在左后方；长裙片向左水平飞出；身体仍后仰
5. 右臂回到胸口高向前，左手回到胯边，身体回正

`[animation]`：

```text
INSPIRE (E, the shield), 5 frames, League's E: one arm raised straight up, then swept forward. 1 the right hand rising in front of her chest, the left hand dropping to the hip; the left foot stepping back half a step. 2 the right arm raised straight up above her head (the hand as high as the ring), the palm open; the left arm out low behind to the left; she leans back, looking up at her hand (the head 3-4 squares left of its idle place). 3 THE SHIELD (cast here): the same, the right palm wide open with the fingers spread at the top, leaning back further (the head and shoulders 4-6 squares left of idle), the left hand far back-left low; the skirt panel swinging left. 4 the right arm sweeping forward and down diagonally (the hand up-right at head height), the left arm far back; the skirt panel flying left horizontally; still leaning back. 5 the right arm forward at chest height, the left hand at the hip, the body upright again.
```

### `karma_ult.png` R 真言（交叉站、双手合十、长裙片鼓成帆）

1. 两手向胸前合拢（左手在腰胸之间偏前，右手到脸旁）；右脚收到左脚后面（两腿交叉，右脚跟抬起）
2. 合十：两掌在脸前、下巴高合在一起，两肘向两边张开；两腿交叉：左脚踩在前面（站位点右边 2–3 格），右脚在它后面、脚跟抬起；长裙片在身后向左鼓起；玉环悬在头顶
3. **真言（从这里亮起）**：同样合十；长裙片鼓得更大，像一面帆（向左展开到胯左边约 10 格，上沿到胸口高）；骨翅微微张开 **← 出手帧**
4. 保持合十；长裙片还鼓着，轻轻摆动
5. 两手分开放下（左手到腰，右手到胸前），两脚分开，裙片落下

`[animation]`：

```text
MANTRA (R), 5 frames, League's mantra stance: legs crossed, palms pressed together, the long skirt panel billowing like a sail. 1 she draws her hands together in front of her chest (the left hand forward between waist and chest, the right hand by her face); the right foot steps behind the left (legs crossing, the right heel up). 2 PRAYER: the palms pressed together in front of her face at chin height, the elbows out to the sides; the legs crossed - the left foot planted in front (2-3 squares right of the standing point), the right foot behind it, heel up; the long skirt panel billowing out behind her to the left; the ring hovering above her head. 3 THE MANTRA (it lights up here): the same prayer pose; the skirt panel billowing bigger like a sail (out to about 10 squares left of her hips, its top at chest height); the prongs spread a little. 4 holding the prayer; the skirt panel still billowing, swaying. 5 the hands parting and lowering (the left hand to the waist, the right to the chest), the feet uncrossing, the skirt falling.
```

### `karma_hit.png` 受击

1. 被打得一缩：肩膀向前缩、头低 1 格，左手收到身侧，右手在胸前；整个人向左（后）退 1 格；右脚微微抬起
2. 回到待机姿势

`[animation]`：

```text
HIT, 2 frames: 1 she flinches: the shoulders hunched forward, the head dipping 1 square, the left hand pulled to her side, the right hand at the chest; knocked back 1 square to the left; the right foot lifted a little. 2 recovering toward the idle stance.
```

### `karma_dead.png` 死亡（玉环骨翅碎落、跪下、向前扑倒）

1. 被击中：身体一震，两手松开（右手在胸前，左手垂下），翡翠玉环从头顶飘起
2. 向前弯腰（头低下、低约 2 格），两臂甩向两边；玉环和四片骨翅离开身体、向两边飞散（玉环往左上，骨翅往左右）
3. 玉环和骨翅落到地上（躺在脚底线上：玉环在左边，骨翅在两边）；她弯腰站着，头垂下，两手无力；右脚抬起
4. 勉强站直、向后晃，头歪向左后方，两手垂着
5. 跪下：直身跪着（膝盖着地、坐在脚跟上），长裙片在身后向左铺在地上；头比站着时低约 9 格
6. 跪着，两手垂在身侧，低头
7. 跪着向前晃
8. 向右前方扑倒：侧身躺在地上（头在右端贴地，腿折在左边），裙子盖在身上；一动不动。玉环和骨翅从第 3 帧起每帧都留在原来的位置

`[animation]`：

```text
DEATH, 8 frames, League's death: the ring and the prongs break away, she sinks to her knees and falls forward. 1 struck: she jolts, the arms loose (the right hand at the chest, the left hand down), the jade ring lifting off above her head. 2 she doubles over forward (the head bowed, about 2 squares lower), the arms flung out to the sides; the jade ring and the four prongs break away from her and fly apart (the ring up-left, the prongs to both sides). 3 the ring and the prongs drop to the ground around her (lying on the feet line: the ring on the left, the prongs on both sides); she stands hunched, the head hanging, the arms limp; the right foot lifted. 4 she straightens up, swaying back, dazed, the head tilted back-left, the arms hanging. 5 she drops to her knees: kneeling upright (the knees on the ground, sitting back on her heels), the skirt spreading on the ground behind her to the left; her head about 9 squares lower than when standing. 6 kneeling, the arms hanging at her sides, the head bowed. 7 kneeling, swaying forward. 8 collapsed forward onto her side to the right: lying on the ground (the head at the right end on the ground, the legs folded at the left), the skirt draped over her; lying still. The ring and the prongs stay where they fell, the same places in frames 3-8. The lying body is drawn lying, never a rotated standing sprite.
```


## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；只用造型图色板里的颜色；
- [ ] **每帧整个人一起画**，头长在脖子上、跟着身体动（弓步、俯身、下蹲时头跟着走）；头和造型图一样大、一样的样子；
- [ ] **动作像英雄联盟**：把你的帧和 `zoom/` 同一帧并排看——腿、胯、身体倾斜、手的位置、长裙片的形状对得上；
- [ ] 站直时和造型图一样高；身体一样宽（不瘦小）；手臂一样粗，手掌完整；
- [ ] 每帧都有两只手臂和手掌、两条腿和两只靴子、玉环、四片骨翅（死亡按表）；两条腿是同样的深棕光腿；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格和碎点；
- [ ] 没有背影、没有转头、没有倒立；出招朝图的右边；没有特效；
- [ ] 跑步：两脚交替、每步都有一只脚向后高踢，身体（连头带玉环）一起上下弹，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有网格、文字、编号、参考线；`manifest.json` 写全（每帧的格子矩形、站位点 pivot、不透明范围 bbox、**头的位置：额前宝石和两只眼睛的方块坐标**、出手帧手掌的位置）；生图原稿放进 `raw/`；最后写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）。

交付到 `outputs/karma-strips-v2/`，最好打成一个 zip（`karma_strips_pack_v2_done.zip`）。

## Claude 导入时（给 Claude 看）

- 检查（严格方块、二值透明、色板、脚底线、连通块、零散黑格）；**每帧面积和身高对造型图**（瘦小的帧退回）；**每帧和 `zoom/` 同一帧并排看动作**；头按播放顺序排成一排看大小和样子（heads-in-sequence）。
- 眼睛：把造型图的眼睛（POLISH 3 的 C2 眼睛）按 Codex 画的头的位置贴上（按额前宝石和眼睛对齐）；头形状和造型图差得多的帧，按 Codex 头的位置换成造型图的头（头的位置跟着 Codex 画的走，不是固定一个位置），再看脖子接得上。
- 腿：两条腿同色、靴子是造型图的；交叉步和后踢量一下（每帧前后脚的 x）。
- 放进 `assets/source/native/`（`karma_<动作>.png` 按 now 的格子），`karma_cells.json` 用包里这份；`import_native.py` 照旧（COMPLETE 补描边，karma 的待机仍是 rig_karma 的待机）。
- 按出手帧核对技能数据的时机（普攻 tick 11、Q tick 10、W tick 10、E tick 6、R tick 6），跑步 8 × 125 毫秒，量头像截取点，做预览 GIF（和英雄联盟原版并排），给用户审。
