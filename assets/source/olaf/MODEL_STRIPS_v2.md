# 奥拉夫：照英雄联盟原版动作重画动作帧（第 2 步重做，给 Codex 的提示词）

## 这一轮为什么重做

上一轮交回的动作条（`olaf_strips_pack_done.zip`）和我们后来自己修的版本，用户都没有通过：

1. **人物比造型图大**（`refs/round1_too_big.png`）：跑步帧 55–62 行高（造型图只有 42 行），靴子大 1.3–1.7 倍，手臂和大腿的皮肤面积大到 3 倍多；站着的动作腿也不是造型图的腿。
2. **头是整块贴的**：头旁边带着一条肩毛贴进每一帧，身体在头下面另画。
3. 我们用造型图的零件重新摆的版本被用户退回：「身体太奇怪了吧……和英雄联盟也不一样啊」——只动手臂、身体和腿僵着，不像英雄联盟的动作。

**这一轮的做法（卡尔玛就是这样做通过的）：**

- **每一帧把整个人一起画**：头盔和双角、脸、胡子、鬃发、身体、两只手臂、两把斧、腰带、毛皮围腰、两条腿在同一个姿势里一起画出来，头永远长在身体上、跟着身体动——前冲和下劈时头随肩膀一起向前向下，挺身怒吼时一起抬高，跪下时一起下沉。**不要先放一个固定的头再在下面画身体，不要贴头，也不要用上一轮的贴头脚本。**
- **大小、比例、长相照造型图**（`design/olaf_design.png`），**动作照英雄联盟**：`zoom/lol_zoom_<动作>.png`（原版每帧放大、编号，看动作最清楚）、`now/olaf_now_<动作>.png`（原版按游戏尺寸取色，看帧数、大小和站位）、`pose/lol_pose_<动作>.png`（原版高清、和 now 同格子同位置）。下面每帧都写了腿、胯、身体、两只手和两把斧怎么动。`refs/design_vs_league.png` 是造型图和英雄联盟模型并排：哪个部件对应哪个部件。
- **头照造型图画**：大小、形状、颜色和造型图一样（两只弯角、蓝灰角盔、涡纹、帽檐、护鼻、两只眼睛、张开的嘴），每帧一样大；只随身体移动，弯腰砸地和倒地时可以倾斜。眼睛和嘴画准位置即可——交回后我们会把造型图的脸统一换上。
- 站直的动作（普攻举斧、Q 蓄力、R 怒吼、死亡挺身）他会比待机的半蹲站得更高——**这是姿势变了，不是人变大**：头、手臂、斧、靴子都和造型图一样大。
- 待机不用画（`olaf_idle.png` 已做好，游戏里的待机动画由我们的工具生成；它也告诉你造型图在格子里多大、站在哪里）。

## 造型图（每一帧都照它）

定稿 `design/olaf_design.png`（放大 8 倍，1024×1024）：高的那只角尖到脚底 42 行，39 格宽，21 色；脚底在第 99 行，两脚中间在第 64 列。

- **左右的叫法**：「左手」= 造型图里**图左边那只粗壮的手臂**（离我们近，肩上白毛、棕皮护腕，拳头握着斧柄，斧头横在肚子前）；「右手」= 造型图里**图右边那只手臂**（离我们远，握着右腰边那把斧，斧刃在最右边）。「左腿/右腿」= 造型图里图左边/右边的那条腿。名字跟着手和腿走（跑步时两条腿会交叉换位）。方向「前」= 图的右边（他朝右），「后」= 图的左边。
- **头**（角尖到下巴 18 行）：蓝灰钢角盔，两只弯角（右边那只高），盔上有涡纹、亮帽檐和护鼻；盔下两只蓝眼睛、大张的嘴（红色、露出牙齿）；亮橙色鬃发从盔后披到左肩，橙色编辫大胡子从嘴下垂到胸口下面。
- **身体**：光膀子，两肩白色毛皮，深棕皮背心，钢铆钉腰带，白灰毛皮围腰和中间的棕皮片；**身体宽度和造型图一样，不许变大或变小**。
- **手臂**：古铜色粗壮的肌肉手臂（左手最粗，约 10 格宽），前臂有棕皮护腕，拳头约 5×4 格；每只手握一把斧：棕色斧柄 1 格宽，蓝钢斧刃（亮边、暗色符文方块）和造型图一样大（左手那把斧刃约 9×7 格，右手那把约 6×10 格）。
- **腿和靴子**：腿短（Q 版），大腿 4 行（光大腿），带尖刺的浅钢毛皮护胫约 5 行，棕色靴子 4 行高、约 10 格长。两条腿同样的颜色（后面那条可以暗一级）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/olaf_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图：长相、比例、颜色 |
| `design/olaf_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、量尺寸 |
| `design/olaf_head.png`、`_1x.png` | 造型图的头（双角、角盔、脸、头顶橙发），**只是给你看头该画成什么样**，不要贴 | 画头时对照 |
| `design/olaf_palette.png` | 造型图的全部 21 色（暗到亮） | 色板 |
| `now/olaf_now_<动作>.png` | 英雄联盟原版按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、每格位置、人物大小 |
| `zoom/lol_zoom_<动作>.png` | 原版每帧放大、编号（红线 = 脚底线，蓝线 = 站位点） | 第三张附图：**动作照这张** |
| `pose/lol_pose_<动作>.png` | 原版高清，和 now 同格子、同位置 | 需要时核对位置 |
| `guide/olaf_guide_<动作>.png` | 格子边框、站位点（蓝十字）、脚底线（红线）和线下禁区、**英雄联盟每帧头的位置（绿圈）**、帧号 | 对位用，不要画进图里 |
| `olaf_cells.json` | 每帧站位点 `pivot`、头的位置 `head`（格子里第几列、第几行，单位方块）、帧时长 | 整理对位 |
| `olaf_idle.png` | 已做好的待机条 | 不用画；看大小和站位 |
| `refs/design_vs_league.png` | 造型图和英雄联盟模型并排 | 部件对应 |
| `refs/round1_too_big.png` | 上一轮的帧和造型图按同一比例并排：**上一轮画大了，这次不要** | 大小对照 |
| `refs/olaf_picture.png`、`refs/olaf_picture_B_q.png` | 用户选的原画 A、原画 B（Q 举斧蓄力） | 长相参考（以造型图为准） |

## 规则（每张都一样）

- **整个人一起画，头跟着身体动**（见上）。每帧的头在 `guide/` 绿圈附近（英雄联盟的头在那里）。
- **动作照英雄联盟**：腿怎么迈、跳、跪，胯怎么沉，身体怎么弯、怎么挺，两只手到哪里、两把斧怎么抡，照 `zoom/` 和下面的逐帧说明；**不是站着不动只抬一只手**。
- **大小、比例、衣服照造型图**：头、手臂、斧、靴子每帧和造型图一样大；身体一样宽；待机那样半蹲时和造型图一样高（42 格），站直时可以高一些（见上）。两把斧每帧都在（Q 掷出后左手空着）。
- 像素：每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明；**只用造型图的 21 种颜色**（眼睛的蓝和嘴的红、粉、牙白只用在脸上）；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑、不要零散的黑格、不要噪点。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：普攻第 4 帧和 E 第 5 帧斧刃落在脚底线上就停。
- 一直是 3/4 正面朝右（和造型图一样），脸始终看得见（E 砸地和倒地时低头可以）；劈、掷、砸都朝图的右边；**不画背影、不倒立**。
- **只画角色**：斧光、飞出去的斧头、红色怒气、砸地冲击都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯青色 `#00FFFF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/olaf_design.png`，第二张 `now/olaf_now_<动作>.png`，第三张 `zoom/lol_zoom_<动作>.png`。`[animation]` 在下面每张动作图的说明里，`[R]`、`[grid]`、`[size]` 按表。输出文件名 `olaf_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - his exact look, size, proportions, colors and pixel style; do not redesign anything. SECOND: the same animation from League of Legends sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, the layout, the size of the figure and where he stands in each cell, not its blurry look. THIRD: the same League frames rendered large and numbered - copy the MOTION from it: how the legs step, leap, lunge and kneel, how the hips drop, how the body bends forward, straightens and leans back, where the two fists go and how the two axes swing, chop, throw and slam.
The character: Olaf, the Berserker - a huge squat viking: a blue-grey steel helmet with two curved horns (the right one taller), a swirl, a lit brim and a nose guard; two blue eyes and a wide-open shouting red mouth; a bright orange mane falling over his left shoulder and a huge braided orange beard hanging onto his chest; bare tanned muscular arms (the left, near one the biggest) with brown leather wrist wraps and big fists; white fur on both shoulders; a dark brown vest; a steel belt with studs; a white-grey fur loincloth with a brown flap; short legs: bare thighs, spiky pale steel-and-fur greaves, brown boots; a blue-steel axe in each fist (a brown handle 1 square wide, a big blade with a lit edge and a dark rune square).
Task: redraw every frame as clean game-size pixel art of the FIRST image's character doing the THIRD image's motion. Draw the WHOLE figure at once in each frame - the helmet and horns, the face, the beard and the mane, the body, both arms, both axes, the belt, the loincloth and both legs together in one pose - so the head always sits on the body and moves with it: forward and down when he charges, chops or slams, up when he straightens and roars, down when he kneels. Never paste one fixed head and draw a body under it. The head is drawn like the FIRST image's head in every frame (the same size, horns, helmet, eyes and mouth), only moved with the body (tilted only when he bows into the slam or falls).
Motion like League: the legs, the hips and the body move as in the THIRD image (striding, leaping, lunging, kneeling, falling); the beard and the mane swing with the motion; never a stiff standing figure with only one arm moving.
Size and proportions from the FIRST image, only the pose changes: in the idle's half-crouch he is exactly as tall as the FIRST image (42 squares from the tip of the high horn to the soles); when he straightens up he stands taller because of the pose, never because the parts grow. The head (18 squares from the horn tip to the chin), the arms (the left one about 10 squares wide), the fists, the axes, the greaves and the boots (4 rows tall, about 10 squares long) are exactly as big as in the FIRST image in every frame; the body is as wide as in the FIRST image - never bigger, never slimmer. Both legs the same colors (the farther one may be one shade darker). Both axes in every frame; in Undertow the left hand is EMPTY from the throw on.
Pixel rules (most important): every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. ONLY the 21 colors of the FIRST image, no new colors: #2A1208 #022460 #4A2A1E #2E3448 #B30729 #74442C #A83410 #0455A6 #A4542E #4E5E7E #E94101 #A06A44 #CA4A60 #FC8302 #D47C48 #8494B2 #FCB870 #BCC4D8 #F4E6E8 #ECEAF0 #FFFFFF. The eye blues and the mouth reds, pink and tooth white only on the face. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares; no dithering, no noise, no random specks.
Feet line: in every cell the soles of the standing foot are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there - an axe chopped or slammed into the ground stops ON that row. His place across the cell follows the SECOND image.
3/4 front view facing right like the FIRST image, the face visible (bowed only in the slam and the fall); every chop, throw and slam goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (swing trails, the flying axe, the red rage glow, the ground impact) - only the character.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x96 squares (896x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FFFF cyan). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid; only the FIRST image's colors; the whole figure drawn together, the head on the body in every frame and as big as the FIRST image's head; the legs, hips and body moving like the THIRD image (not frozen); both arms whole with fists, both axes (the left hand empty after the Undertow throw), both legs and boots; the parts as big as in the FIRST image, never bigger; no loose pieces, no stray black squares; nothing below the feet line; never his back or upside down; the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准时用；图1 = now 条，图2 = 造型图，图3 = zoom 原版放大）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色；动作看图3（同一组动作的高清放大，编号和图1的帧一一对应）。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块；半蹲时人物和图2一样高，头、手臂、斧头、靴子每帧和图2一样大，不能变大也不能变小。
2. 保留每一帧的全身动作：腿怎么迈步、跃起、弓步、跪下，胯怎么下沉，身体怎么前弯、挺直、后仰，两只手到哪里、两把斧怎么举、劈、掷、砸，都照图1和图3；不要画成站着不动只抬一只手。
3. 整个人一起画：头、胡子、鬃发、身体、手、斧、腿在同一个姿势里，头长在身体上、跟着身体一起动；不要贴一个固定的头。
4. 长相、比例、配色、细节全部换成图2：蓝灰角盔（两只弯角、涡纹、帽檐、护鼻）、蓝眼睛、张开的红嘴、亮橙鬃发、橙色编辫大胡子、古铜色粗壮光膀子、肩上白毛、棕皮护腕、深棕皮背心、钢铆钉腰带、白灰毛皮围腰、光大腿、尖刺浅钢护胫、棕靴、两手各一把蓝钢斧（Q 掷出后左手空着）。两条腿同样的颜色。
5. 一直是 3/4 正面朝右，脸看得见；劈、掷、砸都朝右；不画特效；脚底线以下不能有像素。
6. 动作：[animation]
背景保持纯青色 #00FFFF，方便抠图。风格保持与图2一致。重点在于精准复刻图1和图3的"动作骨架"，只是换了"皮囊"。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 |
|---|---|---|---|---|
| `olaf_run.png`（跑步（弓身冲锋，双斧大幅摆动）） | 8 × 120 | — | 4 列 × 2 行，3584×1536 | 第 81 行 |
| `olaf_attack.png`（普攻（右手举斧过头，向前下劈）） | 6 帧：60 70 70 80 60 60 | 第 4 帧（tick 12） | 3 列 × 2 行，2688×1536 | 第 81 行 |
| `olaf_skill.png`（Q 逆流投掷（左手举斧过头，大弓步掷出，左手空了）） | 6 帧：60 70 70 80 60 60 | 第 4 帧（tick 12） | 3 列 × 2 行，2688×1536 | 第 81 行 |
| `olaf_skill2.png`（E 鲁莽挥击（下蹲、跃起、双斧举过头、落地向前砸地）） | 6 帧：50 60 57 70 70 60 | 第 5 帧（tick 14） | 3 列 × 2 行，2688×1536 | 第 81 行 |
| `olaf_ult.png`（R 诸神黄昏（挺身仰头怒吼，双斧举在脸前交叉）） | 6 帧：60 60 70 80 90 100 | 第 3 帧（tick 7） | 3 列 × 2 行，2688×1536 | 第 81 行 |
| `olaf_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1792×768 | 第 81 行 |
| `olaf_dead.png`（死亡（后仰、跪下高举双斧、向前扑倒趴在地上）） | 8 帧：100 100 120 150 150 150 150 500 | — | 4 列 × 2 行，3584×1536 | 第 81 行 |

## 逐帧动作（照英雄联盟；左手/右手、左腿/右腿 = 造型图里在图左边/右边的那只，方向 = 图里的方向，他朝右）

### `olaf_run.png` 跑步（弓身冲锋，双斧大幅摆动）

1. 身体向前弓（头比待机向前约 4 格、高 1–2 格）；左脚踩在胯下，右腿向后高高踢起（靴子在身后、胯的高度）；左手向后上方摆，斧头垂在身后左下方；右手在身前右边、胸口高，斧头竖着
2. 身体下沉（头比待机低约 2 格）；左脚往后滑到站位点下面，右腿还在身后、靴子开始往下往前摆；左手还在身后，右手在身前腰高
3. 向前跃起一小步（两只靴子都离地，最低的是左手那把斧：斧刃垂到快碰脚底线）；左手向前下方摆，斧头低低地挂在膝盖前；右手在右肩前，斧刃朝下；右腿从胯下往前摆，左腿收在后面
4. 大步落地：右脚踩在前面（站位点右边约 8 格），左腿向后伸直、脚尖点地（站位点左边约 10 格）；身体低（头比待机低约 5 格）；左手向前下方摆到底，斧头横在脚前、斧刃朝前；右手举到头后，斧头从右肩后面翘起来
5. 右脚踩在前面，左腿向后踢起（靴子在身后、膝盖高）；身体升高；左手在身前，斧头斜着朝前上方；右手还举在头后，斧柄从头顶后面露出来
6. 右脚往后滑到胯下，左腿还在身后踢着、开始往前摆；身体下沉（头比待机低约 3 格）；左手在身前，右手在头后
7. 两脚在胯下交错（左脚从后面往前摆、右脚在后面蹬地）；身体弓得最深最低（头比待机低约 7 格、向前约 8 格）；左手往后摆到腰边，斧刃在胸前；右手甩到身前右边，斧头朝下快碰到地
8. 腾空：两只靴子都离地（左脚在胯下离地 3–4 格，右腿向后高高踢起到胯的高度）；身体最高、最直（头比待机高约 3 格）；左手摆到身后胸口高，斧柄朝后横着；右手在身前右边，斧头垂下（接回第 1 帧）

`[animation]`：

```text
RUN, 8 frames x 120 ms = League's run cycle (0.97 s), a heavy charging run to the right: the body bent forward at the hips the whole time (the head 2-8 squares ahead of its idle place), the head and shoulders bobbing (highest in frames 8, 1 and 3, lowest in 4 and 7); the hips turned side-on (only a few squares apart, NOT the wide idle stance) so the legs pass each other; each foot plants ahead, slides back under the body, pushes off behind, kicks up high behind (the boot up to hip height), then swings forward again - the two legs half a cycle apart; the arms swing big and opposite to the legs, each fist keeping its axe; the orange mane and the braided beard swing with the bob. 1 the left foot planted under the hips, the right leg kicked up high behind (the boot at hip height); the left arm swung back and up, its axe hanging down behind; the right fist forward at chest height, its axe upright. 2 lower (the head 2 below idle); the left foot sliding back under the standing point, the right boot coming down and forward behind; the left arm still back, the right fist forward at the waist. 3 a short leap, both boots off the ground (the lowest thing is the left axe, its blade hanging just above the feet line); the left arm swinging forward and down, its axe low in front of the knees; the right fist in front of the right shoulder, the blade down; the right leg swinging forward under the hips, the left leg tucked behind. 4 the long stride lands: the right foot planted ahead (about 8 squares right of the standing point), the left leg stretched back, toe on the ground (about 10 left); the body low (the head 5 below idle); the left axe swung forward and low, lying across in front of the feet, blade forward; the right arm raised behind the head, its axe sticking up over the right shoulder. 5 the right foot planted, the left leg kicked up behind (the boot at knee height); the body rising; the left fist in front, its axe slanting forward and up; the right arm still up behind the head, the handle showing above it. 6 the right foot sliding back under the hips, the left leg still up behind and starting forward; lower (the head 3 below idle). 7 the feet passing under the hips (the left swinging forward, the right pushing off behind); the deepest bend (the head 7 below idle and 8 ahead); the left fist swung back to the waist, its blade in front of the chest; the right arm flung forward, its axe pointing down at the ground in front. 8 airborne: both boots off the ground (the left under the hips 3-4 squares up, the right leg kicked up high behind at hip height); the body highest and most upright (the head 3 above idle); the left arm swung back at chest height, its handle sticking out behind; the right fist forward, its axe hanging down (then frame 1 again).
```

### `olaf_attack.png` 普攻（右手举斧过头，向前下劈）

1. 起手：身体微微抬起（头高约 2 格），右手向前上方伸，斧头举在身前右上方；左手收到肚子前，斧头横在身前
2. **举斧过头**：站直挺高（头比待机高约 10 格，略向后仰），右手高高举到头的后上方，斧头在头顶左上方竖起来；左手弯起来挡在脸前，拳头在脸的高度、斧刃朝前；两腿还是待机的大跨步
3. 开始劈下：身体向前压（头向前约 6 格、低约 3 格），右手从头顶往前抡，斧柄横在头顶上方、斧刃还在头后；左手落到胸前
4. **劈中（伤害在这里）**：右手那把斧劈到身前地面——右拳低到膝盖前，斧刃落在前脚前面、贴着脚底线（**不能低过脚底线**）；身体向前弯（头向前约 3 格、低约 6 格）；左手反向甩到身后左上方，斧头举在头的左上方 **← 出手帧**
5. 收势：右手那把斧顺势甩过两腿到身后左下方（斧刃在左后方、接近地面）；左手还举着，斧头在头的左上方；身体还低（头低约 5 格）
6. 回到待机姿势（头低约 1 格），两把斧收回身体两侧

`[animation]`：

```text
BASIC ATTACK, 6 frames, League's overhead axe chop with the RIGHT arm (the one holding the axe at the right hip in the design). 1 rising a little (the head 2 higher), the right arm reaching forward and up, its axe held up ahead of him; the left fist moving in front of the belly, its axe across the body. 2 RAISE: standing up tall (the head about 10 squares higher than idle, leaning back a little), the right arm raised high behind and above the head, its axe standing up above the top-left of the helmet; the left arm bent up in front of the face, the fist at face height, its blade pointing forward; the legs in the idle's wide stance. 3 the chop starts: the body driving forward and down (the head 6 forward, 3 lower), the right arm swinging the axe over the head - the handle across above the helmet, the blade still behind the head; the left fist dropping to the chest. 4 THE CHOP (the hit lands here): the right axe hacked down in front of him - the right fist low in front of the knees, the blade on the ground in front of the front foot, resting ON the feet line (never below it); the body bent forward (the head 3 forward, 6 lower); the left arm flung back up behind, its axe raised up-left of the head. 5 follow-through: the right axe swung on past the legs to the back-left, the blade low behind him near the ground; the left axe still raised up-left; still low (the head 5 lower). 6 back into the idle stance (the head 1 lower), both axes back at his sides. The swing trail is an effect - do not draw it.
```

### `olaf_skill.png` Q 逆流投掷（左手举斧过头，大弓步掷出，左手空了）

1. 起手：身体向左后转，左手向左伸出，斧头横在身体左边胸口高；右手斧头垂在身前右下方
2. **蓄力**：挺身后仰（头比待机向左约 5 格、高约 10 格），左手笔直高举在头的左上方、斧头竖在最高处（参考 `refs/olaf_picture_B_q.png`）；右手那把斧横在肚子前；两腿大跨步站稳
3. 开始掷：身体向前倾（头向前约 3 格、高约 2 格），左手从头顶往前抡，斧柄横在头顶上方、斧刃在头的左后方；右手斧头垂在右边
4. **掷出（斧头从这里飞出）**：向前的大弓步——左腿向后伸直，右膝弯曲；身体深深向前压（头向前约 6 格、低约 8 格）；左手向前下方甩到底、**手掌张开、空的**（低到膝盖前）；右手那把斧扛在肩后，斧刃朝右。飞出去的斧头是特效，不要画 **← 出手帧**
5. 保持弓步、更低一点（头向前约 6 格、低约 9 格），空着的左手还在身前低处
6. 收回待机姿势（头回到原位），**左手还是空的**，右手握着斧

`[animation]`：

```text
UNDERTOW (Q), 6 frames, League's Q: the LEFT arm (the design's big near arm) raises its axe straight up, then hurls it forward in a deep lunge; after the throw that hand is EMPTY. 1 turning back to wind up: the left arm out to the left, its axe across at chest height on his left; the right axe hanging down in front at the right. 2 WIND-UP: he rears up and leans back (the head about 5 squares left and 10 higher than idle), the left arm straight up high above the top-left of his head, its axe standing at the very top (picture B in refs/ shows this wind-up); the right axe held across his belly; the legs planted wide. 3 the throw starts: leaning forward (the head 3 forward, 2 higher), the left arm swinging the axe over the head - the handle across above the helmet, the blade behind at the upper left; the right axe hanging at the right. 4 THE THROW (the axe leaves here): a deep forward lunge - the left leg stretched far back, the right knee bent - the body thrown far forward (the head 6 forward, 8 lower), the left arm whipped forward and down to the right, the hand OPEN and EMPTY low in front at knee height; the right axe carried on the shoulder behind his head, blade to the right. 5 holding the lunge, a bit lower (the head 6 forward, 9 lower), the empty left hand low in front. 6 back into the idle stance, the left hand still EMPTY, the right fist holding its axe. The flying axe is an effect - do not draw it.
```

### `olaf_skill2.png` E 鲁莽挥击（下蹲、跃起、双斧举过头、落地向前砸地）

1. 深蹲蓄力（头比待机低约 7 格），两膝弯曲，两把斧低低地握在身前（左手那把横在膝盖前，右手那把在右腰边朝下）
2. **跃起**：整个人离地（脚底比脚底线高约 8 格；头比待机高约 17 格），身体伸直，两腿垂在下面；右手把斧头高高举在右上方（斧头竖着），左手那把斧在胸前
3. 跃到最高（脚底比脚底线高约 16 格；头比待机高约 11 格）：两膝收到胸前，身体后仰，两手把两把斧举过头顶向后抡（左手那把斧在头后左边、斧刃朝下，右手那把竖在头顶上方）
4. 落地：两脚落回脚底线（在站位点右边几格），身体挺直拉长（头比待机高约 13 格、向前约 4 格），两把斧都高举在头顶上方（左手那把横在头顶、斧刃朝左，右手那把竖着），准备砸下
5. **砸地（伤害在这里）**：身体猛地向前弯到底（头向前约 9 格、低约 3 格，低头、盔顶朝右），两膝弯曲；两手把两把斧一起砸到身前地面，两个斧刃落在前面、贴着脚底线（**不能低过脚底线**）。砸地的冲击是特效，不要画 **← 出手帧**
6. 起身回到待机姿势（头低约 5 格），两把斧收回身体两侧

`[animation]`：

```text
RECKLESS SWING (E), 6 frames, League's E: crouch, a big leap with both axes swung up over the head, land, then a two-handed slam into the ground in front. 1 a deep crouch (the head 7 lower than idle), the knees bent, both axes low in front (the left one across the knees, the right one at the right hip pointing down). 2 THE LEAP: the whole figure off the ground (the soles about 8 squares above the feet line; the head 17 higher than idle), the body stretched upright, the legs hanging below; the right arm lifting its axe high at the upper right (the axe upright), the left axe in front of the chest. 3 the top of the leap (the soles about 16 above the feet line; the head 11 higher than idle): the knees pulled up to the chest, leaning back, both axes swung up over the head and back (the left axe behind the head on the left, blade down; the right axe standing up above the helmet). 4 landing: both feet back on the feet line a few squares right of the standing point, the body stretched tall (the head 13 higher, 4 forward), both axes raised high above the head (the left one across above the helmet, blade to the left; the right one upright), about to slam. 5 THE SLAM (the hit lands here): he bends all the way forward (the head 9 forward and 3 lower, bowed so the helmet's top faces right), the knees bent, both axes slammed down together in front of him, both blades on the ground ahead resting ON the feet line (never below it). 6 rising back toward the idle stance (the head 5 lower), both axes back at his sides. The ground impact is an effect - do not draw it.
```

### `olaf_ult.png` R 诸神黄昏（挺身仰头怒吼，双斧举在脸前交叉）

1. 收势：身体微微下沉（头低约 2 格），两手带着斧往身前收
2. 挺身：站直、挺胸、仰头（头比待机高约 10 格、略向左），嘴张开；两臂向两边低低张开——右手那把斧伸向右下方，左手那把横在胯前
3. **怒吼（诸神黄昏从这里开始）**：挺胸站直（头高约 8 格），仰头朝天大吼；两臂弯起，两把斧竖着举在脸前、在头顶交叉成 X（左手那把在脸前，右手那把在头的右边）。红色怒气是特效，不要画 **← 出手帧**
4. 保持怒吼，两把斧在头顶前交叉，微微抖动
5. 还在吼，两把斧稍微放低到脸前
6. 回到待机姿势

`[animation]`：

```text
RAGNAROK (R), 6 frames, League's R: he rises, throws out his chest and roars at the sky with both axes raised crossed in front of his face. 1 drawing in: a slight dip (the head 2 lower), both axes coming in front. 2 rearing up: standing tall, chest out, the head thrown back (the head 10 higher than idle, a little to the left), the mouth open; the arms spread low - the right axe out to the lower right, the left one across the hips. 3 THE ROAR (Ragnarok starts here): standing tall, chest out (the head 8 higher), roaring up at the sky; both arms bent up, both axes held upright in front of the face and crossed in an X above the head (the left axe in front of the face, the right one beside the head on the right). 4 holding the roar, the crossed axes shaking a little. 5 still roaring, the axes a little lower in front of the face. 6 back into the idle stance. The red rage glow is an effect - do not draw it.
```

### `olaf_hit.png` 受击

1. 被打得一震：上身向后（左）仰、挺起来（头比待机向左约 7 格、高约 6 格），两臂带着斧向两边甩开；前面那只脚（右脚）微微离地
2. 回到待机姿势（头还偏左约 3 格、高约 3 格）

`[animation]`：

```text
HIT, 2 frames: 1 jolted: the upper body thrown back to the left and up (the head 7 left and 6 higher than idle), the arms flung out to the sides with the axes, the front (right) foot lifting a little off the ground. 2 recovering toward the idle stance (the head 3 left, 3 higher).
```

### `olaf_dead.png` 死亡（后仰、跪下高举双斧、向前扑倒趴在地上）

1. 被击中：身体一震（头低约 2 格），姿势像待机
2. 挺身后仰：站直、头向后仰（头比待机高约 12 格、向左约 4 格），两臂向两边张开，两把斧向左右伸出到肩高
3. **跪下**：两膝跪在地上（胯落到离地很近），两臂向两边举起（拳头在头的两侧），两把斧竖着、斧刃高过头顶，头向左后仰（盔顶朝左上方）
4. 跪着，手放下来：左手那把斧垂到左边地上，右手向前伸、斧头横在胸前朝右
5. 跪着往后一仰（头低约 5 格、盔顶朝左上），右手又把斧头举到右上方
6. **向前扑倒**：整个人向右前方扑在地上——趴着，头在右端贴近地面，身体横着，两条小腿向上翘在身后左边（靴子在空中）；两把斧落在头前面的地上
7. 趴在地上，小腿慢慢落下，斧头留在原处
8. 趴着一动不动：脸朝下贴地（盔顶朝右下），腿在左边，两把斧在头旁边的地上。躺着的身体要真的画成趴着的样子，不是把站着的图转 90°

`[animation]`：

```text
DEATH, 8 frames, League's death: he rears up, drops to his knees with both axes raised to the sky, then topples forward onto his front. 1 struck: a jolt (the head 2 lower), otherwise the idle stance. 2 rearing up: standing tall with the head thrown back (the head 12 higher than idle, 4 left), the arms spread wide, both axes held out left and right at shoulder height. 3 ON HIS KNEES: both knees on the ground (the hips low, close to the ground), both arms lifted out to the sides (the fists beside the head), both axes upright with the blades above the head, the head tipped back to the upper left. 4 kneeling, the arms coming down: the left axe hanging down to the ground on the left, the right arm forward with its axe across in front of the chest. 5 kneeling, swaying back (the head 5 lower, tipped back to the upper left), the right arm lifting its axe up at the upper right once more. 6 FALLEN FORWARD: he topples forward to the right onto his front - lying on his belly, the head at the right end near the ground, the body lying across, the lower legs bent up in the air behind him on the left (the boots up); both axes on the ground in front of his head. 7 lying on his front, the lower legs sinking. 8 lying still face down (the helmet's top toward the lower right), the legs on the left, both axes on the ground beside the head. The lying body is drawn lying, never a rotated standing sprite. Nothing below the feet line.
```


## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；只用造型图色板里的颜色；
- [ ] **每帧整个人一起画**，头长在身体上、跟着身体动（冲锋、下劈、砸地时头跟着向前向下）；头和造型图一样大、一样的样子；
- [ ] **动作像英雄联盟**：把你的帧和 `zoom/` 同一帧并排看——腿、胯、身体弯曲、两只手的位置、两把斧的方向对得上；
- [ ] **大小和造型图一样**：把第 1 帧和造型图叠在一起比——头、手臂、斧、靴子一样大，身体一样宽；跑步帧不比造型图高（跳起时整个人往上移，不是变高）；
- [ ] 每帧都有两只手臂和拳头、两把斧（Q 掷出后左手空着）、两条腿和两只靴子、肩上白毛、胡子、围腰；两条腿同样的颜色；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格和碎点；
- [ ] 没有背影、没有倒立；出招朝图的右边；没有特效；
- [ ] 跑步：两腿前后交替、每步都有一只脚向后高踢，身体（连头带胡子）一起上下起伏，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有网格、文字、编号、参考线；`manifest.json` 写全（每帧的格子矩形、站位点 pivot、不透明范围 bbox、**头的位置：两只眼睛和嘴的方块坐标**、出手帧拳头/斧刃的位置）；生图原稿放进 `raw/`；最后写 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）。

交付到 `outputs/olaf-strips-v2/`，最好打成一个 zip（`olaf_strips_pack_v2_done.zip`）。

## Claude 导入时（给 Claude 看）

- 检查（严格方块、二值透明、色板、脚底线、连通块、零散黑格）；**每帧的头、靴子、斧刃大小对造型图**（画大的帧退回）；**每帧和 `zoom/` 同一帧并排看动作**；头按播放顺序排成一排看大小和样子（heads-in-sequence）。
- 脸：把造型图的脸（眼睛、护鼻、嘴）按 Codex 画的头的位置贴上（按两只眼睛和嘴对齐）；头形状和造型图差得多的帧，按 Codex 头的位置换成造型图的头（头的位置跟着 Codex 画的走，不是固定一个位置），再看胡子和肩膀接得上。
- 腿：两条腿同色、靴子是造型图的；跑步量每帧两只靴子的 x（前后交替、不超过约 20 格）。
- 放进 `assets/source/native/`（`olaf_<动作>.png` 按 now 的格子），`olaf_cells.json` 用包里这份；`import_native.py` 照旧（COMPLETE 补描边，BREATHE_SKIP 用 rig_olaf 的待机）。
- 按出手帧核对技能数据的时机（普攻 tick 12、Q tick 12、**E tick 14（砸地在第 5 帧，kit 的 e_st 10 → 14）**、R tick 7），跑步 8 × 120 毫秒，量头像截取点，做预览 GIF（和英雄联盟原版并排），给用户审。
