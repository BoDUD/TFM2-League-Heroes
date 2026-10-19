# 魔法猫咪 悠米：第 0 步，先画像素风原图（给 Codex 的提示词）

> 悠米是一只**小小的魔法猫**，坐在一本**会飞的打开的魔法书**里。猫：**淡紫蓝色的毛**（背和头顶深一点，脸、嘴边、胸口、爪子是**白色**），**一双很大的蓝眼睛**，**粉色的鼻子和耳朵内侧**；胸前一圈**深蓝色的蓬毛**；脖子上一个**金色的项圈**，正中一颗**蓝宝石**；额头上一顶**金色的叶子头饰**，头饰上伸出一根**弯弯的金色触须**，末端挂着一颗**发光的蓝色小球**；一条**长长的尾巴**，套着几圈**金环**，尾巴尖是一簇**金色的毛**。书（门扉之书）：**深红色的皮封面**，包着**金色的边框和书角**，封面正中一个**金色的漩涡纹章**；书页是**米黄色**的。请 Codex 画**三张图**（同一个悠米、同一本书，颜色、**格子大小**都一样）：
> - **A：英雄联盟里的待机**（附图 1、2、8a）。3/4 正面朝右：书打开着竖在她身前和身下，她**坐在书里**，上半身和两只前爪从书页上面探出来（两只前爪搭在书的上沿），脸朝右前方，尾巴从书后面绕出来、在画面左边卷起，尾巴尖的金毛朝上。书离地面有一点点，书底就是画面最低点。
> - **B：附身在队友头上的样子**（附图 6、8b）。同一只猫**趴在摊平的书上**：书完全打开、两边封面平摊、书页朝上（像一块小垫子），她肚子贴着书页**趴着**，两只前爪向前伸出书的前沿，头抬起来朝右前方看（**还是 3/4 的脸，两只眼睛都看得见**），尾巴从书的后沿垂下去，尾巴尖的金毛在下面。侧面朝右。游戏里这张会画在队友的头顶上。
> - **C：合上的书**（附图 9）。只有书，**合上了**，平放在地上，3/4 朝右，看得见封面的金框、漩涡纹章和一侧的书页边。大小和 A 里的书一样。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的奈德丽（豹子形态）、千珏和佐伊，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7、9）。
> - **比例**：Q 版，**头大**（猫头连耳朵约占猫身高的一半），身子小；书比猫身子宽。
> - **脸**（附图 3 特写）：**两只大蓝眼睛一样大、一样高、都看得见**（每只至少 3×3 格，带一个白色高光点），粉色小鼻子，白色的嘴边。
> - **画布用正方形 1536×1536**。**A 从触须上蓝色小球的顶到书底约 660 px，也就是约 60 格**，书底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。B、C 用同样大小的格子，B、C 的最低点也在这条地面线上。触须、尾巴全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。淡紫蓝的毛、白毛、深蓝蓬毛、粉色、蓝眼睛、金饰、蓝宝石和蓝色小球、深红封面、金边框、米黄书页要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（飞弹、波纹、光圈都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/yuumi-picture/yuumi-A.png`、`yuumi-B.png`、`yuumi-C.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/yuumi-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/yuumi_picture_done.zip`。

## 附图（在压缩包 `yuumi_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_yuumi_idle.png` | 英雄联盟原版悠米的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_yuumi_frontal.png` | 同一帧，正面 | 脸、项圈、蓬毛、前爪、书的正面 |
| `refs/3_yuumi_head.png` | 头部特写 | 耳朵、眼睛、头饰、触须和蓝色小球 |
| `refs/4_yuumi_back.png` | 同一帧的背后 | 背上的毛、尾巴的金环、书的封面 |
| `refs/5_yuumi_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/6_yuumi_attached.png` | 趴在摊平的书上（侧面） | **B 的姿势** |
| `refs/7_yuumi_side.png` | 待机，接近侧面 | 侧面的身形、书的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 大小、地面线（灰）；**姿势按文字** |
| `refs/9_book_closed.png` | 合上的书落在地上 | **C**：封面、金框、纹章 |
| `style/11_style_nidalee_cougar.png` | 本包的奈德丽豹子形态，8 倍放大，一格 = 一个像素 | **只看风格**：猫科动物的毛、耳朵、爪子在格子上怎么画 |
| `style/12_style_kindred.png` | 本包的千珏（8 倍） | **只看风格**：动物的大眼睛和白毛在格子上怎么画 |
| `style/13_style_zoe.png` | 本包的佐伊（8 倍） | **只看风格**：格子密度、描边、Q 版大头、金饰在格子上怎么画 |

## 提示词：`yuumi-A.png` / `yuumi-B.png` / `yuumi-C.png`（同一段提示词，只换最后一句）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-7 and 9 are 3D renders and art of a character from the game: a SMALL MAGICAL CAT sitting in an OPEN FLYING BOOK. The cat: LILAC-BLUE fur (darker on the back and the top of the head), WHITE muzzle, chest and paws, two HUGE BLUE EYES, a PINK nose and pink inner ears, a DEEP-BLUE fur ruff on the chest, a GOLD COLLAR with a BLUE GEM in front, a GOLD LEAF CIRCLET on the forehead from which a curling GOLD ANTENNA rises ending in a GLOWING BLUE ORB, a LONG TAIL with a few GOLD RINGS ending in a GOLD TUFT. The book: DARK-RED LEATHER covers framed with GOLD edges and GOLD CORNERS, a GOLD SPIRAL EMBLEM in the middle of the cover, CREAM pages (1 her idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the face, the collar, the ruff, the front paws, the front of the book; 3 the head close-up: the ears, the eyes, the circlet, the antenna and its orb; 4 the same from behind: the back fur, the tail rings, the book's cover; 5 the official illustration: her mood, her colours, her face; 6 her lying on the open book laid flat, from the side - pose B; 7 the idle nearly from the side: her body and the depth of the book; 9 the closed book lying on the ground - picture C). Images 8a and 8b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a big cat's fur, ears and paws on the grid (11), an animal's big eyes and white fur on the grid (12), the square density, the outline, a chibi big head and gold trim on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the antenna, the orb and the whole tail); the lowest point level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b).
PROPORTIONS: chibi - the cat's head with its ears about HALF of the cat's height, a small body; the book wider than the cat's body.
THE FACE: TWO BIG BLUE EYES of the SAME size at the SAME height, both visible (each at least 3x3 squares, with one white highlight square), a small pink nose, a white muzzle.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the lilac-blue fur, the white fur, the deep-blue ruff, the pink, the blue eyes, the gold trim, the blue gem and orb, the dark-red covers, the gold frame and the cream pages clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no missiles, no waves, no sparkles, no glow), no background, no ground plane, no shadow, no text, no frame, no other characters.
PICTURE A (yuumi-A.png): her idle (images 1, 2 and 8a) - 3/4 view facing right (the face to the front-right): the book open and standing in front of and under her, she SITS INSIDE the book with her upper body and both front paws over its top edge (the paws resting on the edge), the tail coming out behind the book and curling up on the image left with its gold tuft upward; the bottom of the book is her lowest point, on the ground line. She is about 660 px (about 60 squares) from the top of the antenna's orb to the bottom of the book.
PICTURE B (yuumi-B.png): ATTACHED - the SAME cat and book with the SAME 11-px squares, seen from the side facing right (image 6): the book OPENED FULLY and laid FLAT like a small cushion (both covers spread under it, the cream pages on top), she LIES ON THE PAGES on her belly, both front paws stretched forward over the front edge of the book, the head raised looking to the front-right (still a 3/4 face with BOTH eyes visible), the tail hanging down over the back edge of the book with its gold tuft at the bottom; the lowest point (the tail tuft) on the ground line (image 8b shows only the size and the ground line).
PICTURE C (yuumi-C.png): THE CLOSED BOOK - the book ALONE, CLOSED, lying flat on the ground, 3/4 view facing right (image 9): the dark-red cover with its gold frame, gold corners and gold spiral emblem on top, the cream page edges on one side; the same size as the book in picture A, resting on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，触须、小球、尾巴完整，不出画。
- Q 版：猫头连耳朵约占猫身高一半；**两只大蓝眼睛一样大、一样高**、带白色高光；粉鼻子、白嘴边。
- 淡紫蓝的毛、白色的脸和胸、深蓝蓬毛、金项圈和蓝宝石、金叶头饰、金触须和蓝色小球、尾巴的金环和金色尾尖。书：深红封面、金边框和书角、金色漩涡纹章、米黄书页。
- A：坐在打开的书里，前爪搭在书沿，尾巴在画面左边卷起；从触须小球顶到书底约 660 px（约 60 格），书底在地面线上。
- B：书摊平、书页朝上，她趴在书页上，前爪伸出书的前沿，头抬起、3/4 的脸两只眼睛都看得见，尾巴从书后沿垂下。
- C：只有合上的书，平放在地上，和 A 里的书一样大。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- 三张都画完后，最后写 `outputs/yuumi-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/yuumi_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/yuumi/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回，和已合并的辅助、小个子英雄（米利欧、璐璐、佐伊、提莫、千珏）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）。B 在队友头上的大小另外定（比 A 小）。
- 定下后第 1 步按游戏格子重画：3/4 正面（待机、选人卡片）、**侧面朝右**（所有动作的底子；脸用 3/4 正面的同一张脸）、附身趴书（a_*）、合上的书。英雄联盟里她不用四条腿跑：**跑步是坐在书里飞**（Run01），所以动作帧大多是整只猫 + 书整体移动、书的封面开合。英雄联盟的动作：普攻 Yuumi_Attack01 / Crit01（从书里跳起来伸长身子扑一下）；Q Spell1_detached；W Spell2_Attach_in（伸长身子飞过去）、Spell2_Detach_out（跳下来）；E Spell3_detached；R Spell4_in / Spell4_loop01（书竖起来，她扒在书边）；跑 Run01；死亡 Yuumi_Death01（她钻进书里，书合上掉在地上）。
