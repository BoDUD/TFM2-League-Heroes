# 菲兹移动重做交接

只交付 run 的替换素材。其他八张动作未写入或修改，与上次交付 ZIP 中的 PNG 逐字节一致，校验值在 validation.json。

## 文件与坐标

- fizz_run.png：3584×1792，4 列×2 行，单格 896×896，透明背景。
- fizz_run_1x.png：448×224，单格 112×112；8 倍版本由它最近邻放大。
- manifest.json：每帧格子、站位点、包围盒、时间、头部位置、双腿关节及武器信息。rect/bbox 使用左闭右开坐标；bbox_local_1x 是整个人物和武器合计。
- fizz_run_preview.webp：无损循环预览，保留 107/108 ms 时间；GIF 仅用于快速观看，格式会把时间量化到 10 ms。
- index.html：可播放、暂停和逐帧查看，按 manifest 中时间播放，站位点固定。
- reference_comparison.png：原版部位图与新动作逐帧对照。
- drafts/imagegen_run_raw.png：本次内置 imagegen 生成的原始草稿，不是游戏用素材。

## 制作方式

使用内置 imagegen，附定稿造型、原版部位分色和高清动作三张参考，完整提示词见下文和 prompt.txt。原始草稿恢复了直立身体和空手前伸，但头部、像素网格、双腿交替和武器长度不够精确。依据用户此前“允许”的像素整理授权，在 112×112 逻辑格上逐帧修正身体、手臂、腿与持戟位置；近腿/远腿身份依照橙色/蓝色参考，成品均换回定稿的蓝色大腿、海军蓝小腿和蹼足。

头部直接复制定稿中的 29×16 逻辑像素，只平移，没有缩放、旋转或改色。锚点固定在站位点右方 5 格，头部左边缘相对站位点始终为 -11 格。头顶行依次 66、67、66、65、66、67、66、65，总起伏 2 格。奶黄色喉咙的首行位于最低眼睛行下方 4 格。

身体从头顶到踩地脚底为 31–33 格。第 1–4 帧由近腿完成前方落地和交叉，第 5–8 帧换为远腿支撑、近腿前摆；第 4 帧两膝相交。空手向右前方伸出，手掌有分开的短指。另一只手握戟，武器斜角依次 35、37、45、62、65、58、50、40 度。三叉戟金环、叉头、宝石沿用定稿，完整模板长 55 格，叉头最低在 96 行，脚底为 97 行。

## 检查与保留的差异

所有 8 帧均通过：原头逐像素一致、相对横向位置固定、严格 8×8 网格、23 色板、0/255 透明度、8 邻域单一连通块、无 98 行以下像素、每帧脚底落在 97 行、武器完整且在格内。身体姿势和膝部交叉另以 reference_comparison.png 人工逐帧检查。

这里是按定稿的矮小像素角色比例转译原版步态，并非原版 3D 轮廓的逐像素复制。原参考有腾空或被武器遮住的脚，成品按要求补成至少一脚落地；为使直立腹部可读，持戟整体稍移向人物前侧的左方，叉头落在脚边，部分帧仍遮住远腿。原版耳鳍的摆动没有复刻，定稿头的完整位图保持固定。

RUN_REDO.md 写了“8×107 ms”，但 fizz_cells.json 的第八帧是 108 ms。本交付沿用 JSON：前七帧 107 ms、第八帧 108 ms，总计 857 ms，以保持上一版动画时间和站位数据。

没有导入游戏、执行包内导入指令，或修改游戏目录。

## 实际 imagegen 提示词

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - his colors, materials, head, trident and pixel style. SECOND: the original run, 8 frames in a 4x2 grid of 112x112-square cells, painted by part: the NEAR leg ORANGE (in front, toward the viewer), the FAR leg BLUE (behind), the TRIDENT GREEN, the head and body grey - copy the pose of the body, both legs and the trident in every frame from it. THIRD: the same 8 frames rendered normally - how the body, the arms and the trident look.
Task: redraw his RUN as clean pixel art identical in style to the FIRST image, at exactly the same pixel size (about 32 squares from the crown to the soles), every pixel one crisp 8x8 square on a single 8-px grid, no anti-aliasing, no blur, no semi-transparency.
The run (League's own, 8 frames x 107 ms, one seamless loop): an upright little trot - the body standing as tall as in the FIRST image, NOT squashed or crouched; the two legs long and clearly visible, ALTERNATING like the SECOND image: frames 1-4 one stride, frames 5-8 the other, the knees passing each other in between, one foot on the ground line in every frame; the free arm reaching forward to the right with the hand open; the trident held in the other hand, slanting across the front of him: the round gold butt end up behind his shoulder (image upper left), the jade three-prong head down in front by his feet (image lower right) - never below the feet line; the fin-ears flowing back a little.
The head (crown spots, fin-ears with their orange frills, face, eyes, grin) is COPIED from the FIRST image in every frame, square for square, facing right as in the FIRST image, and only moved: the same horizontal place relative to the standing point in all 8 frames, at most 1-2 squares up or down; the cream throat starts 4 rows under the eyes' lowest row; never sink the head into the body.
Legs: both legs in the FIRST image's leg colours - blue thighs, deep navy-blue shins and big webbed feet - the far leg at most one shade darker, never a different material; each leg at least 3 squares wide with its outline, one 1-square near-black outline round each leg, no black lines inside a leg, a hidden part of a leg simply not drawn (never a black block).
Trident: as long as in the FIRST image (about 55 squares end to end), a crimson shaft ONE square thick with the outline on both sides, a straight unbroken stepped line, the jade three-prong head with pale steel edges and a blue gem, the round gold ring end.
Pixel rules: ONLY the 23 colors of the FIRST image, a 1-square near-black outline round the silhouette and each material's own dark shade inside it, big flat areas, no dithering or noise, the whole figure ONE connected piece in every frame. 3/4 FRONT view facing right, the face always visible. No effects.
Feet line: the lowest row of his feet is square row 97 of each cell; nothing from row 98 down. Layout: 4 columns x 2 rows of 112x112-square cells, 3584x1792 pixels, frame N in the same cell as in the SECOND image, the standing points as in fizz_cells.json; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.

Precise frame pivots, in logical pixels: (55,86),(56,86),(59,86),(60,86),(61,86),(59,86),(56,86),(55,86). Entire body from crown to soles is approximately 32 logical pixels; preserve the large copied head but make torso upright and legs visibly long. Do not substitute a side-on crouch. Follow the orange/blue reference legs individually and their front/back ordering, with both final legs blue/navy. Keep weapon in the foreground but head entirely unobstructed. Finish one complete 8-frame sprite sheet.

```
