# 机械公敌 兰博：第 0 步，先画像素风原图（给 Codex 的提示词）

> 兰博是英雄联盟里**开着一台自己拿废铁拼起来的机甲的约德尔人**：人小，机甲大，坐在机甲胸口敞开的驾驶舱里，**人和机甲算一个角色**。机甲一只手是**喷火器**（Q 喷火），另一只手是**大铁钳爪**；背上竖着**冒烟的排气管**；E 从机甲上射出**电鱼叉**，R 从背后发射一排**火箭**。这一步画两张，用户从里面挑定样子（**颜色和零件以附图 1–5 为准**，下面的文字只是帮你认部件）：
> - **兰博（驾驶员）**：约德尔人，个子很小，**一对又大又尖的长耳朵**往两边伸；额头上推着一副**大大的焊工护目镜**；一撮**乱糟糟的头发**；**咧嘴坏笑**、露出牙；身上是皮夹克 / 背带，**只露出上半身**（腰以下在驾驶舱里）；手扶着操纵杆。
> - **机甲（Tristana 叫它"破铜烂铁"的那台）**：**敦实、方头方脑的铁皮身子**，到处是**铆钉、补丁、锈斑和焊缝**；胸口是**敞开的驾驶舱**，兰博从里面露出来；**一条胳膊末端是喷火器喷嘴**（粗管子、喷口发黑），**另一条胳膊末端是一只大铁钳爪**（附图 1 里哪只是哪只就照哪只画）；**肩后 / 背上竖着几根排气管**；**两条短粗的铁腿**，大铁脚稳稳踩地；身上挂着管线和小零件。
>
> 请 Codex 画**两张全身像**（**格子大小一样**，都是 **3/4 正面朝右**，同一个待机姿势），用户从里面挑**比例**：
> - **A：标准 Q 版**——英雄联盟里的待机：机甲站稳、两只胳膊垂在两边，兰博从驾驶舱里探出上半身朝右前方看（附图 1、2、3、9a）。**兰博的头放大**到大约和机甲的"头 / 驾驶舱顶"一样宽，机甲按原版比例略缩。
> - **B：更 Q 的版本**——**同样的姿势、同样的格子大小、同样的总高度**，但**兰博的头和上半身再大一圈**（头大约占整个高度的三分之一），机甲**更矮更圆**、腿更短更粗、两只手臂的喷火器和钳爪相对更大（附图 9b）。这一张是为了在游戏里只有 40 来个像素高时也能看清他的脸。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的克烈（约德尔人 + 大坐骑）、布里茨（蒸汽机器人）、大发明家（约德尔工程师）、厄加特（人坐在机械上），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7；附图 5 官方原画看气质和颜色——**大尖耳朵、额头上的护目镜、坏笑、敞开驾驶舱里露出的小个子、喷火器手臂、铁钳爪手臂、背上的排气管、满身补丁铆钉锈斑的铁皮机甲最重要**）。
> - **脸要清楚**（附图 3 特写）：**两只眼睛一样高**，每只至少 2×2 格（一格高光）；护目镜**推在额头上**、不挡眼睛；咧开的嘴和牙清楚；耳朵完整。机甲的任何零件（驾驶舱边、排气管、喷火器）都**不能挡住他的脸**。
> - **颜色**：照附图 1–5 取色。皮肤 / 毛、头发、护目镜（镜片一格亮）、衣服各 2–3 档；机甲铁皮 3–4 档 + 一档亮边，锈斑 / 补丁用铁皮色之外的 1–2 档（不要零散杂色格），铆钉一格亮；喷火器管子和喷嘴 2–3 档（喷口最暗）；钳爪 3 档 + 亮边；排气管 2–3 档。
> - **画布用正方形 1536×1536**。**A 和 B：从排气管顶 / 兰博的耳朵尖（取高的那个）到铁脚底约 500 px，也就是约 45 格**；宽约 36 格（机甲比人宽，最多 44 格，含两只手臂）。脚底在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站在画布中间。耳朵、排气管、喷火器、钳爪全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（火焰、烟、电光、鱼叉、火箭、护盾都放到后面单独画；**排气管口不冒烟**）；不画地面，不画投影。
> - 交付：`outputs/rumble-picture/rumble-A.png`、`rumble-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/rumble-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/rumble_picture_done.zip`。

## 附图（在压缩包 `rumble_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_rumble_idle.png` | 英雄联盟原版兰博的待机，3/4 朝右 | 颜色、形状、**角度**、姿势；**哪只手是喷火器、哪只是钳爪** |
| `refs/2_rumble_frontal.png` | 同一帧，正面 | 驾驶舱、机甲胸口、两条腿 |
| `refs/3_rumble_head.png` | 驾驶员和驾驶舱特写（3/4） | **耳朵、护目镜、脸、头发**；驾驶舱边 |
| `refs/4_rumble_back.png` | 同一帧的背后 | **排气管**、机甲的背 |
| `refs/5_rumble_splash.png` | 官方加载画面 | 气质、**坏笑**、颜色 |
| `refs/6_rumble_q.png` | Q 喷火的一帧 | 喷火器手臂抬起来的样子（这一步不画动作，后面用） |
| `refs/7_rumble_e.png` | E 射电鱼叉的一帧 | 同上（这一步不画） |
| `refs/7b_rumble_r.png` | R 发射火箭的一帧 | 同上（这一步不画） |
| `refs/9a_layout_rumble.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 在画布上的位置、大小、地面线（灰）；浅灰线 = 最高点 |
| `refs/9b_layout_rumble_chibi.png` | B 的布局示意（同一个模型，驾驶员的头放大、机甲腿缩短） | 同上；**B 的比例** |
| `style/10_style_kled.png` | 本包的克烈，8 倍放大，一格 = 一个像素 | **只看风格**：约德尔人的大耳朵、大头 + 一个大块头"坐骑" |
| `style/11_style_blitzcrank.png` | 本包的布里茨（8 倍） | **只看风格**：铆钉铁皮身子、肩后的管子、粗短的铁腿 |
| `style/12_style_heimerdinger.png` | 本包的大发明家（8 倍） | **只看风格**：约德尔工程师、护目镜、金属零件 |
| `style/13_style_urgot.png` | 本包的厄加特（8 倍） | **只看风格**：人坐在一台机械身子上面、脸露在上面不被挡 |

## 提示词：`rumble-A.png` / `rumble-B.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-7b are 3D renders and art of ONE character from a game: a TINY FURRY HUMANOID PILOT (a short big-eared creature) SITTING IN A BIG HOME-MADE SCRAP-METAL MECH - one character. THE PILOT: HUGE POINTED EARS sticking out sideways; a pair of BIG WELDING GOGGLES pushed up on his forehead; a messy tuft of hair; a CHEEKY WIDE GRIN showing his teeth; a leather jacket / harness; only his upper body shows, out of the mech's open cockpit, his hands on the controls. THE MECH: a STOCKY, BOXY body of riveted sheet metal, PATCHED, WELDED and RUSTY all over; an OPEN COCKPIT in its chest where the pilot sits; ONE ARM ENDS IN A FLAMETHROWER NOZZLE (a thick pipe, the muzzle sooty dark), THE OTHER ARM ENDS IN A BIG STEEL CLAW (follow image 1 for which arm is which); several EXHAUST PIPES standing up behind its shoulders; TWO SHORT THICK METAL LEGS with big flat steel feet; hoses and small parts hanging on it. (1 the idle, 3/4 view facing right - the look, the ANGLE, the pose and which arm is which; 2 the same from the front: the cockpit, the chest, the legs; 3 the pilot and the cockpit close-up: the ears, goggles, FACE and hair; 4 the same from behind: the exhaust pipes, the mech's back; 5 the official illustration: the mood, the colours, the grin; 6 a flamethrower blast, 7 a harpoon shot and 7b a rocket launch - all three for later.) Images 9a-9b are layout guides: where the character goes on the canvas and how big, the grey line is the ground, the light line the top of the figure. Take the COLOURS and the parts from images 1-5. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a chibi big-eared little rider on a big body (10), a riveted metal robot body with pipes behind its shoulders and short thick legs (11), a little engineer with goggles (12), a figure riding on top of a machine body with the face clear above it (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the ears, the exhaust pipes, the flamethrower, the claw); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows the character (the centre). The whole character is about 500 px (about 45 squares) from its highest point (the tips of the exhaust pipes or of the pilot's ears, whichever is higher) to the steel feet and about 36 squares wide (never more than 44, with both arms), in both pictures.
PROPORTIONS: chibi. The pilot's HEAD MUCH BIGGER than in the renders so the face reads clearly, turned to the front-right; the mech chunky and solid. The mech NEVER covers the pilot's face (not the cockpit rim, not a pipe, not an arm).
THE FACE CLEAR: fur / skin in 3 shades; TWO EYES at the SAME height, each at least 2x2 squares with one highlight square; the goggles pushed UP on the forehead, never over the eyes; the grin and the teeth clear; both ears whole.
THE COLOURS: as in images 1-5. The pilot's skin / fur, hair, goggles (one bright square on each lens) and clothes each in 2-3 shades; the mech's sheet metal in 3-4 shades with one lighter edge, the rust and the patches in 1-2 shades of their own (no stray odd squares), rivets one bright square each; the flamethrower pipe and nozzle in 2-3 (the muzzle darkest); the claw in 3 with a bright edge; the exhaust pipes in 2-3. Every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the pilot's fur, hair, goggles and jacket, the mech's metal, rust and patches, the flamethrower and the claw clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no fire, no smoke from the pipes, no sparks, no electricity, no harpoon, no rockets, no shield); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (rumble-A.png): the idle in 3/4 view facing right (images 1, 2, 3 and 9a) - the mech standing firm on its two legs, both arms hanging at its sides (the flamethrower and the claw low, as in image 1); the mech's NEAR leg on the image left in full tone, the FAR one a step darker; the pilot leaning out of the cockpit with his head and shoulders above the mech's chest, looking to the front-right; his head about as wide as the top of the cockpit; the exhaust pipes behind the shoulders.
PICTURE B (rumble-B.png): the SAME character and pose, MORE CHIBI (image 9b) - the SAME total height and square size as A, but the pilot's head and upper body clearly bigger (the head about a third of the whole height), the mech SHORTER and ROUNDER with shorter, thicker legs, the flamethrower and the claw a little bigger; the same parts, the same colours.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，耳朵、排气管、喷火器、钳爪完整，不出画。
- 兰博：Q 版，**头比原版大很多**、脸清楚；**大尖耳朵**；**护目镜推在额头上、不挡眼睛**；**两只眼睛一样高**；**坏笑露牙**；只露上半身、从驾驶舱里探出来。
- 机甲：方头方脑的铁皮身子、**铆钉补丁锈斑**；**敞开的驾驶舱**；**一只手喷火器、一只手铁钳爪**（和附图 1 一致）；**背上的排气管**；两条短粗铁腿；**不挡兰博的脸**。
- A 是标准 Q 版、B 是更 Q 的版本（头更大、机甲更矮更圆）；都是 3/4 正面朝右、同一个待机姿势；都约 500 px（约 45 格）高；脚底在地面线上。
- 两张图里兰博的**脸是同一张**（B 只是更大）。
- 没有技能特效（排气管不冒烟）。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/rumble-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/rumble_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：兰博的头（一张脸用在所有帧）、喷火器手臂（Q 要抬起来朝前喷，火焰会画进他自己的动作帧）、钳爪手臂（普攻挥砸）、肩上 / 背上的排气管（R 发射火箭、过热时冒烟）、两条短腿（跑）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 | idle / run / attack | 普攻是机甲抡钳爪砸下去 |
| **喷火**（Q 纵火盛宴） | spell1 | 喷火器朝前喷出一大股锥形火焰（这一下他站着喷） |
| **破碎护盾**（W，并进被动） | spell2 | 一圈废铁护盾套在机甲外面、加速 |
| **电子鱼叉**（E） | spell3 | 机甲射出一支带电的鱼叉，打中后可以马上再射一支 |
| **恒温灼烧**（R） | spell4 | 背后发射一排火箭，沿一条线落下，地上烧成一条火 |
| **热量 / 过热**（被动） | — | 机甲冒黑烟、烧红，普攻带火 |
| 死亡 | death | |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/rumble/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出；`regrid` 的格子要给得比实际略大，否则会拆行），和已合并的约德尔人 / 机械（克烈、布里茨、大发明家、吉格斯、厄加特、库奇）按游戏里的大小并排，给用户定大小、PPU。
- **先核对文字描述**：本提示词里驾驶员和机甲的颜色没有写死（写的时候看不到渲染图），以 `pack_rumble_picture.py` 渲染出的附图为准；渲染出来如果"喷火器 / 钳爪在哪只手""护目镜位置"和文字对不上，先改提示词再交给 Codex。
- 渲染：`pose_ref.py --champ Rumble`（`pack_rumble_picture.py` 从 WAD 的动画列表按名字找 idle / spell1 / spell3 / spell4 的片段，找不到时打印整张清单；`tools/lol/anim_graph.py Rumble` 看 Run 实际播哪个），加 `--fit-all`；B 的布局用 `--head 1.8 --legs 0.8`。加载画面：`assets/characters/rumble/skins/base/rumbleloadscreen.tex`。
