# 奥莉安娜（发条魔灵）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 奥莉安娜是一个**纤细的发条机械人偶少女**：金色金属的齐耳短发、头顶一个圆发髻；瓷白色的脸，**青绿色发光的眼睛**；银白色的金属胸甲，脖子前一枚金色齿轮徽章；手臂和腿是一节一节的橄榄灰金属，关节处是金色的小圆球；腰上一圈**金色齿轮尖刺短裙**；身边漂着她的武器——**一颗银色金属球（发条球）**，球腰上两道铜金色的环。请 Codex 用同一段提示词画**两版**全身像素风原图，我从中挑一张：两版是同一个奥莉安娜，长相、衣服、颜色、格子大小都一样，只有姿势不同。
> - **A**：英雄联盟里的待机（附图 1）。站着，一只手在胸前，另一只手垂在身侧、手指张开；球漂在她身前一侧。
> - **B**：指挥球（附图 6）。一只手高高举起、手指张开指向球，像在指挥它；球漂在她身前一侧。
>
> **球要和她分开画**：球悬在空中，和她的身体、手之间**至少隔开 2 格透明的空隙**，不能重叠、不能碰到。游戏里球是单独的一张图（Q 会把球扔出去、E 会把球送到队友身上），我要把它从原画里单独剪下来。
>
> 选定一张后，第 1 步再按它做游戏尺寸的造型。这一版每个游戏像素约 **1.8 格**，读回后再降到选定的 PPU。附图 9–12 是本包里的伊莉丝、卡特琳娜、加里奥、卡莉丝塔，其中伊莉丝也是 1.8 格。你画的原图会按格子直接读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：纤细的少女人偶，**头稍大一点**（连发髻约占身高的四分之一多一点），细腰、细胳膊细腿，关节处的小金球看得出来；不要画成大头小身子的娃娃，也不要写实的细长比例。
> - **头**（附图 3 特写）：
>   - **金色金属的齐耳短发**（波波头），前面齐刘海斜着遮住一点额头，两侧包到下巴，头顶一个**圆圆的金色发髻**；金色要分出亮金、金、暗金、棕金几档，不要糊成一片黄。
>   - **瓷白色的脸**（带一点冷灰紫），脸颊和下巴边上有细细的人偶接缝线；**两只青绿色发光的眼睛**（一样大、一样高），小小的深色嘴唇。
> - **身体**：
>   - 脖子前一枚**金色齿轮徽章**；**银白色的金属胸甲**（像瓷器一样亮），上面有浅浅的刻纹；胸甲下面露出橄榄灰的金属躯干。
>   - **手臂**：一节一节的**橄榄灰 / 青铜灰金属**，肩膀和手肘是**金色小圆球关节**；手是银白色的，**手指又细又长、指尖尖尖的**。
>   - **短裙**：腰上一圈**金色的齿轮刀片短裙**，一片片尖尖地向外张开（像太阳光芒 / 齿轮齿），里层是深青铜色。
>   - **腿**：细长的橄榄灰金属腿，膝盖和脚踝是金色小圆球关节，小腿外侧有银白色的护甲片，脚上是**尖头的银灰金属靴**。
> - **球**（附图 7 特写，附图 1、6 看大小和位置）：**一颗银色的金属球**，直径大约是她身高的五分之一（约 15 格）；球面是钢银色，刻着深色的花纹，有几块**淡紫色的小窗格**；球腰上**两道铜金色的环**，球顶有一道金色的弧形脊。它悬在空中，和她分开。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**，两只脚底落在同一条地面线上。球在她身前（画面右边），大约腰到胸口的高度。
> - **画布用正方形 1536×1536**：**从发髻顶到脚底约 792 px，也就是约 72 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。她、球、举起的手都在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（她和球各自一圈）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金色（头发、齿轮、裙子、关节）、银白（脸、胸甲、手、护甲片、球）、橄榄灰金属（四肢、躯干）要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**青绿色只用在眼睛上**，淡紫只用在球的小窗格上。
> - 不画任何特效（球的电光、冲击波、护盾、轨迹都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/orianna-picture/orianna-A.png`、`orianna-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/orianna-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/orianna_picture_done.zip`。

## 附图（在压缩包 `orianna_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_orianna_idle.png` | 英雄联盟原版奥莉安娜的待机，3/4 朝右，带球 | 颜色、形状、**角度**、A 的姿势、球在哪 |
| `refs/2_orianna_frontal.png` | 同一帧，正面（不带球） | 头发、胸甲、齿轮徽章、短裙、四肢的关节 |
| `refs/3_orianna_head.png` | 头部特写 | 齐耳短发、发髻、瓷白的脸、青绿眼睛、接缝线 |
| `refs/4_orianna_back.png` | 同一帧的背后（不带球） | 发髻、背后的短裙、腿 |
| `refs/5_orianna_splash.png` | 官方加载画面 | 气质（精致、冷静的人偶） |
| `refs/6_orianna_command.png` | 一只手举起来指挥球 | B 的姿势、球在哪 |
| `refs/7_orianna_ball.png` | 球的特写 | 球的花纹、小窗格、两道环、顶上的脊 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上她和球的位置、大小、脚底线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（同一比例） | 画布上她和球的位置、大小、脚底线（灰） |
| `style/9_style_elise.png` | 本包的伊莉丝，8 倍放大，一格 = 一个像素（和这张一样每游戏像素 1.8 格） | **只看风格**：这个密度下格子有多细、脸怎么画 |
| `style/10_style_katarina.png` | 本包的卡特琳娜（8 倍） | **只看风格**（纤细的女英雄） |
| `style/11_style_galio.png` | 本包的加里奥（8 倍） | **只看风格**：金色怎么分档 |
| `style/12_style_kalista.png` | 本包的卡莉丝塔（8 倍） | **只看风格**（冷色调、细胳膊细腿） |

## 提示词：`orianna-A.png` / `orianna-B.png`（同一段提示词，只换最后一句姿势）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-7 are 3D renders and art of a character from the game: a SLENDER CLOCKWORK DOLL GIRL with a golden metal bob haircut and a bun, a porcelain face with glowing teal eyes, a silver-white metal bodice, segmented olive-grey metal limbs with small golden ball joints, a short skirt of golden gear blades, and her weapon - a SILVER METAL BALL that floats beside her (1 her idle in 3/4 view facing right, with the ball - the look, the ANGLE, pose A and where the ball floats; 2 the same from the front without the ball: the hair, the bodice, the gear emblem, the skirt, the joints of her limbs; 3 the head close-up: the bob, the bun, the porcelain face, the teal eyes, the thin doll seams; 4 the same from behind; 5 the official illustration: her mood, a delicate calm automaton; 6 one hand raised to command the ball - pose B; 7 the ball close-up: its engraved pattern, the small pale violet window panels, the two bands round its middle, the ridge over its top). Images 8a and 8b are the layout guides of A and B: where she and the ball go on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 9-12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how gold is split into clear shades (11), how a face reads at this size (9). Image 9 has the same square density this picture needs.
Create ONE pixel-art picture of her, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). She is about 792 px (about 72 squares) from the top of her bun to the soles of her feet, the soles about 146 px above the bottom edge (the grey line of images 8a / 8b); she, the ball and her raised hand whole inside the picture, comfortable transparent margins, nothing cut off; both soles level on one ground line.
PROPORTIONS: a slender doll girl with a slightly big head - the head with the bun a little over a quarter of her height - a narrow waist, thin arms and legs, the small golden ball joints visible; not a big-headed baby doll, not slender realistic proportions.
THE HEAD: a GOLDEN METAL BOB: straight bangs sweeping across the forehead, the sides reaching down to the jaw, a ROUND GOLDEN BUN on top; the gold in clear shades: bright gold highlights, gold, dark gold, brown-gold in the deepest shadow - never one flat yellow. A PORCELAIN-WHITE face with a faint cool grey-violet tint, thin doll seam lines at the cheeks and jaw, TWO GLOWING TEAL EYES (the same size, on the same row), small dark lips.
THE BODY: a GOLDEN GEAR EMBLEM at the throat; a SILVER-WHITE METAL BODICE, bright like porcelain, with faint engraved lines, the olive-grey metal torso showing below it; ARMS of segmented OLIVE-GREY / BRONZE-GREY metal with SMALL GOLDEN BALL JOINTS at the shoulders and elbows; silver-white hands with LONG THIN POINTED FINGERS; a SHORT SKIRT of GOLDEN GEAR BLADES flaring out in sharp points like sun rays, a dark bronze layer under it; slim olive-grey metal LEGS with golden ball joints at the knees and ankles, silver-white plates on the shins, POINTED silver-grey metal boots.
THE BALL: a SILVER METAL SPHERE about a fifth of her height across (about 15 squares): steel-silver with dark engraved swirls and a few small PALE VIOLET window panels, TWO COPPER-GOLD BANDS round its middle, a golden curved ridge over its top. It FLOATS IN THE AIR in front of her (image right) at about waist-to-chest height, SEPARATE from her: at least 2 transparent squares between the ball and her body or hand - never touching, never overlapping (it will be cut out as its own picture).
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image LEFT in full tone, the FAR ones on the image RIGHT a step darker; both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her and around the ball; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the gold (hair, bun, emblem, skirt, joints) in bright gold / gold / dark gold / brown-gold, the silver-white (face, bodice, hands, shin plates, ball) in cool white / light grey / steel grey, the limbs olive-grey metal; the teal used ONLY for the two eyes, the pale violet ONLY for the ball's window panels; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no electric field, no shockwave, no shield, no trail, no glow round the ball), no background, no ground, no shadow, no text, no frame, no other characters.
POSE A (orianna-A.png): her idle (image 1) - standing with the feet a little apart, the near hand down at her side with the fingers spread, the far hand before her chest, the ball floating in front of her (image right).
POSE B (orianna-B.png): commanding the ball (image 6) - one hand raised HIGH toward the ball with the fingers spread as if conducting it, the other arm down at her side, the ball floating in front of her (image right), a little higher than in A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，她、球、举起的手都完整，不出画。
- 比例：纤细的人偶少女，头稍大（连发髻约占身高四分之一多一点），不是大头娃娃，也不是写实的细长身材。
- 头：金色齐耳短发 + 齐刘海 + 头顶圆发髻；瓷白的脸 + **两只一样大、一样高的青绿色眼睛**（这个颜色只用在眼睛上）。
- 身体：金色齿轮徽章；银白胸甲；橄榄灰的分节手臂和腿 + **金色小圆球关节**；细长尖指；金色齿轮刀片短裙；尖头金属靴。
- 球：银色金属球，直径约 15 格；深色花纹、淡紫小窗格、两道铜金色环、顶上金色弧脊；**和她之间至少隔 2 格透明空隙，不重叠、不碰到**。
- 从发髻顶到脚底约 792 px（约 72 格）；近侧手脚在画面左边、颜色亮，远侧在右边、稍暗；脚底在同一条水平线上；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- A、B 两版都画完后，最后写 `outputs/orianna-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/orianna_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两版都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/orianna/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_pantheon_hd.py` 的做法），把球单独剪出来，和中路英雄（拉克丝、阿狸、辛德拉）以及德莱厄斯、慎按游戏里的大小并排，给用户挑 A / B 和大小；PPU 按用户选的定。
- 第 1 步造型包：她和球分开画（球是单独的图：她身边漂着、扔出去停在地上、挂在队友身上都用这一张）。
- 第 2 步动作包：**待机由 Codex 画**（潘森的教训：待机和动作帧要同一比例、同样的站姿），动作帧里**不画球**；跑步照英雄联盟（Orianna_run）；普攻 = 手一挥射出一个小发条弹（Orianna_attack1-3）；Q / W / E / R 都是指挥球的手势（spell1、spell2、spell3、spell4），R 原版会跳起来；死亡（Orianna_death）。
