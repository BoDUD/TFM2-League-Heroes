# 茂凯（扭曲树精）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 茂凯是一棵**巨大的、弓着背的活树**（暗影岛之战后的树精）：身体是**深褐色、发紫的树皮**，背上和头顶盖着一大片**青绿色的苔藓树冠**，几片嫩叶从顶上冒出来；**脸长在树干正中**（不是一颗单独的大头）：木头雕出的眉骨、**两只发蓝光的眼睛**、长着苔藓的胡须一样的下巴；背后伸出一根**弯曲的树枝**，上面挂着一盏**蓝色水晶灯笼**。他的**近侧手臂（画面左边，英雄联盟里是他的左手）巨大**，是浅褐色的木头，拳头上刻着一张**发蓝光的鬼脸**，几乎垂到地面；**远侧的手（画面右边）小一些**，是绿色的爪子，手里拿着一棵**小树苗**。腿是两段**粗短的树根**，腰间垂着一块**紫色的布**。请 Codex 画**两张图**（同一种风格、**同样的格子大小**；两张**都要用**，不是二选一）：
> - **A：茂凯平时的样子**（英雄联盟里的待机，附图 1）。弓着背，巨大的近侧手臂垂在身前（画面左边），远侧的爪子抬在胸前偏右、拿着小树苗。脸朝右前方。
> - **C：他的树苗**（E 树苗投掷扔出去的那个小东西，附图 9）：一棵小小的、站着的木头树苗，**上面一片嫩叶**，身体是浅褐、黄绿色的木头，刻着一张小脸，**一只发蓝光的眼睛**，两侧伸出两片叶子当手臂，底下是尖尖的根。**和 A 用同样每格 11 像素**，约 20 格高（附图 10）。它在游戏里会扔出去、在地上等着、跳起来扑向敌人然后爆炸。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（PPU 1.2）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的塔姆、内瑟斯、厄加特和斯维因，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：他是**大体型的生物，不要画成大头娃娃**。脸就在树干中间，和英雄联盟一样大（从脸顶的木头尖到下巴约占身高的五分之一，约 14 格），不要单独放大。最大的形状是**背上的苔藓树冠**和**巨大的近侧手臂**；腿很短很粗。
> - **脸**（附图 3 特写）：木头眉骨和额头上竖着的木头尖、**两只眼睛一样大、一样高、发蓝光**（平涂的亮蓝色，不要柔光），眼睛下面是暗色的木头，下巴是一圈苔藓绿的"胡子"。
> - **树皮和苔藓**：身体的树皮是深褐色、偏紫的暗色（几档：亮褐、褐、暗紫褐、最暗），有树皮的纹路；苔藓是青绿色（亮绿、绿、暗绿）；树皮很暗，**一定要有偏暖的亮边**，不然在深色背景上会糊成一团。
> - **巨大的近侧手臂**：浅褐色木头（比身体亮），拳头上刻着一张鬼脸，**鬼脸的眼睛和嘴发蓝光**；手臂从肩膀垂到差不多地面，**必须完整地画出来**、形状清楚。
> - **远侧的爪子**：绿色木头的爪子，拿着一棵小树苗（像 C 的缩小版）。
> - **背后**：一根弯曲的树枝从背上伸出来（附图 4、5），上面挂着蓝色水晶灯笼；3/4 角度下灯笼在他身后，能看见多少画多少，不要硬挪到前面。
> - **下身**：腰间一块紫色的布；两条粗短的树根腿，两只"脚"是树根，落在同一条地面线上。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧（画面左边）的颜色亮，远侧（画面右边）稍暗**。
> - **画布用正方形 1536×1536**。**A：从树冠顶（嫩叶不算）到脚底约 792 px，也就是约 72 格**，脚底在离画布底边约 146 px 的地方（附图 8 的灰线）。**C：同样每格 11 像素，从叶尖到根尖约 220 px（约 20 格）**，放在画布中间，底部在同一条线上（附图 10）。手臂、树枝、叶子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（荆棘、冲击波、树根突刺、发光的拖尾都放到第 3 步单独画；眼睛和鬼脸的蓝光是身体的一部分，用平涂的亮色画）；不画地面，不画影子。
> - 交付：`outputs/maokai-picture/maokai-A.png`、`maokai-C.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/maokai-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/maokai_picture_done.zip`。

## 附图（在压缩包 `maokai_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_maokai_idle.png` | 英雄联盟原版茂凯的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_maokai_frontal.png` | 同一帧，正面 | 树冠、脸、两只手臂、紫布、树根腿怎么排 |
| `refs/3_maokai_face.png` | 脸部特写 | 木头眉骨和额头的尖、发蓝光的眼睛、苔藓胡子 |
| `refs/4_maokai_back.png` | 同一帧的背后 | 背上的树枝和蓝色水晶灯笼、远侧爪子里的小树苗 |
| `refs/5_maokai_side.png` | 同一帧，更侧的角度 | 树枝和灯笼的位置、巨大手臂上的鬼脸 |
| `refs/6_maokai_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/7_maokai_r_cast.png` | 大招的一帧：两臂高举 | 巨大手臂的全长和形状 |
| `refs/8_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/9_sapling.png` | 英雄联盟原版的树苗 | C 的长相：小脸、一只蓝眼睛、顶上的叶子、叶子手臂、尖根 |
| `refs/10_layout_C.png` | C 的布局示意（同样的格子） | 树苗的位置和大小、地面线（灰） |
| `style/11_style_tahmkench.png` | 本包的塔姆，8 倍放大，一格 = 一个像素（PPU 1.2，和茂凯一样） | **只看风格**：大个子怎么分档、怎么留亮边 |
| `style/12_style_nasus.png` | 本包的内瑟斯（8 倍，PPU 1.2） | **只看风格**：暗色毛皮的亮边、大体型的头身比例 |
| `style/13_style_urgot.png` | 本包的厄加特（8 倍，PPU 1.2） | **只看风格**：暗色身体的亮边、发光的部分怎么平涂 |
| `style/14_style_swain.png` | 本包的斯维因（8 倍，PPU 1.5） | **只看风格**：脸、眼睛、暗色衣服的亮边 |

## 提示词：`maokai-A.png` / `maokai-C.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-7 are 3D renders and art of a character from the game: a HUGE HUNCHED LIVING TREE - a body of dark brown, violet-tinged BARK under a big TEAL-GREEN MOSS CROWN on his back and head with a few young leaves sprouting on top; his FACE IS IN THE MIDDLE OF THE TRUNK (not a separate big head): a carved wooden brow with an upright wooden spike on the forehead, TWO EYES GLOWING BLUE, a mossy green beard-like chin; a CURVED BRANCH grows from his back with a BLUE CRYSTAL LANTERN hanging from it; his NEAR ARM (image left) is HUGE, of PALE BROWN WOOD, its fist carved into a GRINNING FACE whose eyes and mouth GLOW BLUE, hanging almost to the ground; his FAR HAND (image right) is a smaller GREEN WOODEN CLAW holding a SMALL SAPLING; two short thick ROOT LEGS and a VIOLET CLOTH hanging at the waist (1 his idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the crown, the face, both arms, the cloth, the root legs; 3 the face close-up: the brow, the forehead spike, the glowing eyes, the mossy beard; 4 the same from behind: the branch with the lantern, the sapling in the far claw; 5 a more side-on view: where the branch and the lantern are, the face on the huge fist; 6 the official illustration: his mood and colours; 7 his ultimate: both arms raised, the huge arm's full length and shape). Image 8 is a layout guide for A: where he goes on the canvas and how big, the grey line is the ground. Image 9 is his SAPLING: a small standing wooden seedling, pale brown and yellow-green wood, a small carved face with ONE GLOWING BLUE EYE, a young leaf on top, two leaves as arms, a pointed root at the bottom; image 10 is its layout guide on the SAME squares. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how a huge body is split into clear shades with lit edges (11), a dark furred body with lit edges and big-creature proportions (12), a dark body with lit edges and flat glowing parts (13), a face with two clear eyes and dark clothes with light edges (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the huge arm, the branch, the leaves whole); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 8 and 10).
PROPORTIONS: a BIG CREATURE, NOT a big-headed doll: the face sits in the trunk exactly as big as in images 1-3 (from the wooden spike on the forehead to the chin about a fifth of his height, about 14 squares in A), never enlarged; the biggest shapes are the MOSS CROWN on his back and the HUGE NEAR ARM; the legs short and thick.
THE FACE: the carved wooden brow and the upright forehead spike; TWO EYES of the SAME size at the SAME height glowing bright blue (flat bright squares, no glow halo); dark wood under the eyes; a ring of moss-green beard at the chin.
THE BARK AND MOSS: the body's bark dark brown and violet-tinged in 3-4 shades (light brown, brown, dark violet-brown, darkest) with bark grain; the moss teal-green in 3 shades; the dark bark with WARM LIT EDGES so it never turns into one dark mass.
THE HUGE NEAR ARM: pale brown wood (lighter than the body), the fist carved into a grinning face whose eyes and mouth glow blue, from the shoulder almost down to the ground, drawn WHOLE with a clear shape.
THE FAR CLAW: a green wooden claw holding a small sapling (like a tiny version of image 9).
THE BACK: a curved branch rising from his back with the blue crystal lantern hanging from it; in this 3/4 view the lantern is behind him - show what the view shows, never move it to the front.
THE LOWER BODY: a violet cloth at the waist; two short thick root legs, the root feet on one ground line.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR side on the image left in full tone, the FAR side on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark bark, the teal moss, the pale wood of the huge arm, the green claw, the violet cloth, the blue glow clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no thorns, no shockwave, no roots bursting, no glowing trails), no background, no ground plane, no shadow, no text, no frame, no other characters.
PICTURE A (maokai-A.png): his idle (image 1) - hunched, the huge near arm hanging in front of him (image left), the far claw raised before his chest holding the small sapling; the face to the front-right. He is about 792 px (about 72 squares) from the top of the moss crown (leaves not counted) to his feet.
PICTURE C (maokai-C.png): ONLY HIS SAPLING (image 9) alone in the middle of the canvas, standing upright facing right, with the SAME 11-px squares and the same style as A: about 220 px (about 20 squares) from the leaf tip to the root tip, the root tip on the same ground line (image 10); its one eye glowing blue (flat bright squares).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，巨大手臂、树枝、叶子完整，不出画。
- 比例：大体型的树精，**不是大头娃娃**；脸在树干中间、和英雄联盟一样大（约 14 格）；两只眼睛一样大、一样高、发蓝光。
- 树皮深褐偏紫、有暖色亮边；苔藓青绿；巨大的近侧手臂浅褐色、拳头上的鬼脸发蓝光；远侧绿爪子拿着小树苗；背后树枝上挂蓝色水晶灯笼；腰间紫布、两条粗短树根腿。
- A：待机姿势；从树冠顶到脚底约 792 px（约 72 格），脚底在同一条地面线上。
- C：只有树苗，**同样每格 11 像素**，约 20 格高，一只蓝眼睛、顶上一片叶子、两片叶子手臂、尖根，底部在同一条线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、C 两张都画完后，最后写 `outputs/maokai-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/maokai_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/maokai/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_nasus_hd.py` 的做法），和已合并的辅助、大个子（塔姆、布隆、芮尔、内瑟斯、加里奥、墨菲特）按游戏里的大小并排，给用户定大小；PPU 1.2（用户选的）。树苗按同样的格子读回，和他并排看大小。
- 定下后第 1 步按游戏格子重画 A 和 C，再自己做动作帧（塔姆 / 内瑟斯的方式，无损：只平移、整块直角转、整行移；巨大手臂只能整块平移或直角转）；走路用造型自己的整条腿（不用 Codex 画的腿）。英雄联盟的动作：普攻 maokai_attack1/2（巨臂横扫）；Q 荆棘重击 Maokai_spell1（拳头砸地）；W 扭曲突刺 maokai_spell2_up / spell2_down（化成树根钻地、在目标处冒出）；E 树苗投掷 maokai_spell3（扔树苗）；R 自然之握 maokai_spell4（两臂高举再砸下）；死亡 maokai_death。树苗的动作（落地、等待、跳起扑人、爆炸）放第 3 步特效里画。
