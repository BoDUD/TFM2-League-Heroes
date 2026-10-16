# 厄斐琉斯（残月之肃）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 厄斐琉斯是一个**清瘦、苍白、沉默的年轻刺客**：黑发，长刘海遮住半边脸，后脑翘着一撮短发；眼睛半闭，神情忧郁；穿一件**灰蓝色的高领长外套**，脖子上围一条**很宽的青绿色围巾**，两条长长的围巾尾巴垂到膝盖，领口和腰带是**紫色**的；下身是**深藏青色的紧身裤**和尖头靴，戴黑手套。他用的五把武器都是**淡冰蓝色、月牙形的月石金属**。请 Codex 画**三张图**：两张全身像（同一个厄斐琉斯，长相、衣服、颜色、格子大小都一样，只是姿势不同，我从中挑一张），外加一张五把武器的武器表。
> - **A**：英雄联盟里拿通碧的待机（附图 1）。长长的步枪「通碧」竖着靠在身后的近侧肩上，近侧的手举到脸边（他的招牌手势），远侧手臂垂着。
> - **B**：通碧开枪的瞬间（附图 6）。两腿大大分开压低身子，通碧端平架在肩上，两只手臂向两边张开。
> - **W**：五把武器的武器表（附图 8c、10–14），和 A 同一个比例、同一个格子大小，彼此分开放在一张图上，以后按它把武器画到他手里。
>
> 选定一张后，第 1 步再按它做游戏尺寸的造型。这一版每个游戏像素约 **1.8 格**，读回后再降到 PPU 1.5。附图 15–18 是本包里的杰斯、卡莉丝塔、卡特琳娜、潘森，都是 1.4–1.5 的密度。你画的原图会按格子直接读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：清瘦修长的人形，**头稍大一点**（约占身高的五分之一），肩窄、腰细、腿长；不要画成大头娃娃，也不要壮汉。
> - **头和脸**（附图 3 特写）：
>   - **黑发**带一点蓝紫色的高光，**长刘海斜着盖住画面右边那只眼睛**，后脑一撮短短翘起的头发。
>   - **苍白的皮肤**，**半闭的眼睛**（只露出一只，眼皮下垂，眼下有一点暗紫色），**淡紫色的嘴唇**；脸颊上有几道很淡的**月光裂纹**。
>   - 眼睛的颜色（淡紫 / 淡蓝）只用在眼睛上。
> - **衣服**（附图 1、2、4）：
>   - **灰蓝色（石板青）的高领长外套**，下摆到大腿中间，肩头圆圆鼓起，袖子是同色的；外套边缘有更深一档的青灰色滚边。
>   - 脖子上一条**很宽的青绿色围巾**（亮青绿到深青绿，上面有浅色的花纹），在胸前打结，两条长尾巴一直垂到膝盖下面。
>   - **紫色的里领和衣襟**，腰上一条**紫色的麻绳腰带**，胸口一枚**金色的小月牙扣**。
>   - **深藏青色的紧身裤**，**黑色尖头长靴**；**黑手套**，举起的那只手腕上戴一串**金色的珠子手链**。
> - **武器**（附图 1、6、9–14）：五把都是**淡冰蓝色的月石金属**（亮白蓝、冰蓝、蓝紫三四档），月牙形的弧刃，接口和握把是**深青灰色的金属**。
>   - **通碧 Calibrum**（附图 10）：一把**比他还高一截的细长步枪**，枪身是两片并排的长月牙刃，中间一个弯弯的握把。A 里竖着靠在近侧肩后，B 里端平架在肩上。
>   - **断魄 Severum**（附图 11）：一把**镰刀形的手枪**，一片弯月刃包着一个小握把。
>   - **坠明 Gravitum**（附图 12）：一门**月炮**，像一只开口朝上的大月牙杯，旁边浮着一颗**星形的小部件**。
>   - **荧焰 Infernum**（附图 13）：一把**很宽的喷火枪**，两片大翼形刃向两边展开，中间一道弯弯的握把。
>   - **折镜 Crescendum**（附图 14）：一把**双月牙回旋刃**，两片弯刃中间一个圆环握把。
>   - 每把武器加一点**它自己的颜色**（只在刃口内侧的一两格）：通碧 青绿、断魄 红、坠明 紫、荧焰 蓝、折镜 白。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**，两只脚底落在同一条地面线上。
> - **画布用正方形 1536×1536**：**从头顶（不算翘起的那撮头发）到脚底约 792 px，也就是约 72 格**，脚底在离画布底边约 136 px 的地方（附图 8a、8b 的灰线）。通碧、围巾全在画面里，B 里端平的通碧也不能出画。武器表 W 按附图 8c 的大小和位置摆。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。灰蓝外套、青绿围巾、紫色领子和腰带、深藏青裤子、冰蓝武器要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。冰蓝武器边上的高光要亮，免得在深色背景上看不清。
> - 不画任何特效（子弹、月光、火焰、回旋的刃、身边的月亮都放到第 3 步单独画）；不画地面，不画影子；也不画他姐姐（月光里的女孩）。
> - 交付：`outputs/aphelios-picture/aphelios-A.png`、`aphelios-B.png`、`aphelios-W.png`（都是 1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/aphelios-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/aphelios_picture_done.zip`。

## 附图（在压缩包 `aphelios_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_aphelios_idle.png` | 英雄联盟原版厄斐琉斯拿通碧的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_aphelios_frontal.png` | 同一帧，正面 | 外套、围巾、紫色领子、绳腰带、月牙扣、裤子、靴子 |
| `refs/3_aphelios_head.png` | 头部特写 | 刘海、翘起的头发、半闭的眼睛、嘴唇、脸上的裂纹 |
| `refs/4_aphelios_back.png` | 同一帧的背后 | 外套背面、围巾、通碧怎么靠在背后 |
| `refs/5_aphelios_splash.png` | 官方加载画面 | 气质（沉默、忧郁、月光） |
| `refs/6_aphelios_shot.png` | 通碧开枪的瞬间，3/4 朝右 | B 的姿势 |
| `refs/7_aphelios_shot_side.png` | 同一帧，接近侧面 | B 里通碧怎么端、两只手怎么张开 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上他的位置、大小、脚底线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（同一比例） | 画布上他的位置、大小、脚底线（灰） |
| `refs/8c_layout_W.png` | 武器表的布局示意（和 A 同一比例） | 五把武器各自的大小和摆放位置 |
| `refs/9_weapons_in_hand.png` | 五套待机，从左到右：通碧、断魄、坠明、荧焰、折镜各自拿在手里 | 每把武器多大、怎么拿 |
| `refs/10_weapon_calibrum.png` … `14_weapon_crescendum.png` | 五把武器单独的特写：通碧、断魄、坠明、荧焰、折镜 | 武器的形状 |
| `style/15_style_jayce.png` | 本包的杰斯（拿炮的远程英雄），8 倍放大，一格 = 一个像素 | **只看风格**：像素粗细、描边、金属怎么分档 |
| `style/16_style_kalista.png` | 本包的卡莉丝塔（8 倍） | **只看风格**（冷色调、细长的武器） |
| `style/17_style_katarina.png` | 本包的卡特琳娜（8 倍） | **只看风格**（清瘦的身材、脸和头发） |
| `style/18_style_pantheon.png` | 本包的潘森（8 倍） | **只看风格**：这个密度下格子有多细 |

## 提示词：`aphelios-A.png` / `aphelios-B.png` / `aphelios-W.png`（同一段提示词，只换最后一句）

二十张图都附上，顺序同上表。

```text
Twenty attached images. Images 1-7 are 3D renders and art of a character from the game: a SLENDER, PALE, SILENT YOUNG ASSASSIN with black hair and a long fringe over one eye, a slate grey-blue high-collared long coat, a very wide teal scarf whose long tails hang to his knees, purple collar and rope belt, dark navy tight trousers and pointed black boots, black gloves, carrying moonstone weapons of pale ice-blue crescent metal (1 his idle holding the long rifle Calibrum, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the coat, the scarf, the purple collar, the rope belt, the small golden crescent clasp, the trousers, the boots; 3 the head close-up: the fringe, the short tuft sticking up at the back, the half-closed eyes, the lips, the faint moonlight cracks on the cheek; 4 the same from behind: the coat, the scarf, how Calibrum rests behind his shoulder; 5 the official illustration: his mood, silent and melancholic, moonlit; 6 the instant he fires Calibrum - pose B; 7 the same from nearer the side: how he holds the levelled rifle and spreads his arms). Images 8a, 8b and 8c are layout guides of A, B and the weapon sheet W: where things go on the canvas and how big, the grey line is the ground. Image 9 shows his five idles holding each weapon in turn (left to right: Calibrum, Severum, Gravitum, Infernum, Crescendum); images 10-14 are close-ups of the five weapons in the same order. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 15-18 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how metal is split into clear shades (15, 16), how a slim face and hair are drawn (17). Image 18 shows the square density this picture needs.
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). In the full-body pictures he is about 792 px (about 72 squares) from the top of his head (not counting the tuft) to the soles of his feet, the soles about 136 px above the bottom edge (the grey line of images 8a / 8b); Calibrum and the scarf whole inside the picture (the levelled rifle of pose B too), comfortable transparent margins, nothing cut off; both soles level on one ground line.
PROPORTIONS: a slender human with a slightly big head - the head about a fifth of his height - narrow shoulders, a slim waist, long legs; not a big-headed doll, not a muscular build.
THE HEAD: BLACK HAIR with blue-violet highlights, a LONG SWEPT FRINGE falling across the eye on the image right, a short tuft sticking up at the back of the head; PALE skin; HALF-CLOSED drooping eyes (one eye showing under the fringe), a touch of dark violet under the eye, pale violet lips, a few faint moonlight cracks on the cheek. The eye colour (pale violet-blue) used ONLY in the eye.
THE CLOTHES: a SLATE GREY-BLUE HIGH-COLLARED LONG COAT down to mid-thigh, rounded padded shoulders, sleeves of the same cloth, edges trimmed one shade darker; a VERY WIDE TEAL SCARF (bright teal to deep teal with a faint lighter pattern) wrapped round the neck, knotted on the chest, its two long tails hanging below the knees; a PURPLE inner collar and lapel, a PURPLE TWISTED ROPE BELT, a small GOLDEN CRESCENT CLASP on the chest; DARK NAVY tight trousers, POINTED BLACK BOOTS; BLACK GLOVES, a bracelet of GOLDEN BEADS on the wrist of the raised hand.
THE WEAPONS: all five of PALE ICE-BLUE MOONSTONE METAL (bright white-blue, ice blue, blue-violet in 3-4 shades) shaped as crescent blades, with DARK TEAL-GREY metal joints and grips; each with a tiny accent of its own colour on the inner edge of its blade (one or two squares): Calibrum teal-green, Severum red, Gravitum violet, Infernum blue, Crescendum white. CALIBRUM (image 10): a slim RIFLE TALLER THAN HE IS, two long parallel crescent blades with a curved grip between them. SEVERUM (image 11): a SCYTHE-SHAPED PISTOL, one curved blade round a small grip. GRAVITUM (image 12): a MOON CANNON like a big crescent cup opening upward, a small STAR-SHAPED piece floating beside it. INFERNUM (image 13): a WIDE FLAMETHROWER, two big wing blades spread to the sides with a curved grip in the middle. CRESCENDUM (image 14): a DOUBLE-CRESCENT CHAKRAM, two curved blades round a ring grip.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image LEFT in full tone, the FAR ones on the image RIGHT a step darker; both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and every weapon; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the coat slate grey-blue, the scarf teal, the collar and belt purple, the trousers dark navy, the boots and gloves black-blue, the skin pale, the hair black with blue-violet highlights, the weapons ice blue with bright highlights on their edges so they read on a dark background; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no bullets, no moonlight, no flames, no flying blades, no moons around him), no background, no ground, no shadow, no text, no frame, no other characters (not his sister in the moonlight).
POSE A (aphelios-A.png): his Calibrum idle (image 1) - standing upright, the long rifle Calibrum held upright behind his near shoulder, the near hand raised beside his face, the far arm hanging down, the scarf tails hanging in front.
POSE B (aphelios-B.png): the instant he fires Calibrum (image 6) - the legs spread wide in a low lunge, the body lowered, Calibrum levelled across his shoulder pointing forward (image right), both arms spread out to the sides, the scarf tails swinging.
SHEET W (aphelios-W.png): no character - the five weapons apart, each at the scale it has in A (the same 11 px squares), laid out like image 8c: Calibrum upright on the left, then Severum, Gravitum (with its floating star) and Crescendum on the top row, the wide Infernum below; every weapon whole, at least 3 squares of transparent space between them.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，通碧、围巾完整，不出画。
- 比例：清瘦修长，头稍大（约占身高五分之一），不是大头娃娃，也不是壮汉。
- 头：黑发带蓝紫高光、**长刘海遮住一只眼**、后脑一撮翘发；苍白皮肤、**半闭的眼睛**、淡紫嘴唇；眼睛的颜色只用在眼睛上。
- 衣服：灰蓝高领长外套、**很宽的青绿围巾**（尾巴垂过膝盖）、紫色里领和绳腰带、金色月牙扣、深藏青紧身裤、黑色尖头靴、黑手套、金珠手链。
- 武器：冰蓝月石金属、深青灰接口；五把形状和附图 10–14 对得上；每把只在刃口内侧一两格带自己的颜色。
- A：通碧竖着靠在近侧肩后，近侧手举到脸边；B：弓步压低，通碧端平，两臂张开；W：五把武器按 8c 摆开，和 A 同一个比例。
- 从头顶（不算翘发）到脚底约 792 px（约 72 格）；近侧手脚在画面左边、颜色亮，远侧在右边、稍暗；脚底在同一条水平线上；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B、W 三张都画完后，最后写 `outputs/aphelios-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/aphelios_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/aphelios/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_<hero>_hd.py` 的做法），和同位置英雄（金克丝、卡莎、烬、卡莉丝塔、泽丽）按游戏里的大小并排，给用户挑 A / B；PPU 已定 1.5，再出 2–3 个大小（约 38 / 40 / 42 行）的对比让用户定。武器表 W 按 A 的格子读回，每把武器单独存一张。
- 选定后写第 2 步动作包：五把武器是刚体部件，动作里只平移和整块转直角，不变形；跑步照英雄联盟（aphelios_A_Run1，通碧）；普攻五套（aphelios_A..E_Attack1：通碧、断魄、坠明、荧焰、折镜）；Q 五套（A_Spell1_Attack1 / B_Spell1 / C_Spell1 / D_Spell1A / E_Spell1）；W 换枪（A_Spell2）；R（aphelios_spell4）；死亡（aphelios_death）。附加包的整身换武器：待机、跑步按每把武器的待机姿势和握法，把武器表里那把平移到手上。
