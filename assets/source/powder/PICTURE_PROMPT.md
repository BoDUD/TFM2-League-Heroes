# 爆爆（金铲铲之战 · 双城之战）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 爆爆是《双城之战》里**小时候的金克丝**，一个**小个子女孩**：一头**亮蓝色的短发**，乱蓬蓬的齐肩短发，脑后垂着**两条细细的小辫子**，头顶两侧各别着一个**很大的金色 X 形发夹**（像两根交叉的螺栓）；圆脸，**一双大眼睛（蓝灰色）**，表情有点怯生生又机灵；**青绿色的短袖上衣（下摆像短裙一样盖到大腿）**，袖口露出一截**粉色带条纹的衬衣袖子**，两条小臂缠着**深棕色的护臂（露指）**；腰上一条**棕色皮带**，右边胯上挂着**一个皮袋，里面塞满发蓝光的小炸弹**；**紫色条纹的裤袜**，**棕色系带短靴**。请 Codex 画**两张全身像**（同一个爆爆，长相、颜色、**格子大小**都一样）：
> - **A：金铲铲里的待机**（附图 1、2、8a）。3/4 正面朝右：身体转向右前方，一只手抬到下巴前（像在想主意），另一只手向身体右边伸出去、手掌朝上摊开，两腿稍稍分开站着，脸朝右前方。
> - **B：站直的样子**（附图 8b 只看大小和地面线）。同一个爆爆**站直**，3/4 正面朝右，**两只手臂自然垂在身体两侧**（手离开身体一点，看得见手和护臂），两条腿并拢一点站稳，这一张是后面所有动作的底子。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（3/4 正面、侧面）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本系列借用的同一套画风里的佐伊、波比（两个小个子女孩）和金克丝（长大后的她），**只看风格**。
> - **长相照金铲铲里的模型**（附图 1–4、6、7，附图 5 是官方头像图）。
> - **比例**：Q 版，**头大**（头连头发约占身高的三分之一），身子短、腿细短；不要细长的写实比例。
> - **脸**（附图 3、6 特写）：圆脸，**两只大眼睛一样大、一样高、都看得见**（每只至少 2×3 格，带一个白色高光点），蓝灰色的眼珠，两道细细的深色眉毛，小嘴；脸是浅肉色，两颊一点粉。
> - **头发**：亮蓝色分 3–4 档（暗处偏深蓝），发梢一缕缕翘着；两条小辫子从脑后垂到肩膀下面；金色 X 形发夹分 3 档（亮金、金、暗金），轮廓清楚。
> - **画布用正方形 1536×1536**。**从头顶到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。头发、手全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。蓝头发、金发夹、肉色皮肤、青绿上衣、粉色衬衣袖子、深棕护臂、棕皮带和皮袋、蓝光小炸弹、紫色条纹裤袜、棕靴子要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（爆炸、烟、火花都放到第 3 步单独画）；手里不拿东西（猴子炸弹也放到第 3 步）；皮袋里的小炸弹可以画（她的标志），但不要发光的光晕；不画地面，不画影子。
> - 交付：`outputs/powder-picture/powder-A.png`、`powder-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/powder-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/powder_picture_done.zip`。

## 附图（在压缩包 `powder_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_powder_idle.png` | 金铲铲里爆爆的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_powder_frontal.png` | 同一帧，正面 | 衣服、皮带、皮袋、裤袜、靴子 |
| `refs/3_powder_head.png` | 头部特写（3/4） | 头发、发夹、脸、眼睛 |
| `refs/4_powder_back.png` | 同一帧的背后 | 头发和两条小辫子从背后看 |
| `refs/5_powder_icon.png` | 官方头像图 | 气质、脸、颜色 |
| `refs/6_powder_head_front.png` | 头部特写（正面） | 两只眼睛、两个 X 形发夹 |
| `refs/7_powder_side.png` | 待机，侧面 | 侧面的身形、小辫子 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 大小、地面线（灰）；**姿势按文字：站直、手臂垂下** |
| `style/11_style_zoe.png` | 本系列的佐伊，8 倍放大，一格 = 一个像素 | **只看风格**：小个子女孩的大头、脸、眼睛在格子上怎么画 |
| `style/12_style_poppy.png` | 本系列的波比（8 倍） | **只看风格**：格子密度、描边、金属件在格子上怎么画 |
| `style/13_style_jinx.png` | 本系列的金克丝（8 倍，较粗的旧格子） | **只看风格**：长大后的她，蓝头发和辫子在格子上怎么画 |

## 提示词：`powder-A.png` / `powder-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from a game: a SMALL GIRL with BRIGHT BLUE HAIR in a short messy bob, TWO THIN BRAIDS hanging down behind her, two BIG GOLD X-SHAPED HAIR CLIPS (like two crossed bolts) on top of her head; a round face with BIG BLUE-GREY EYES and thin dark eyebrows, a shy but clever look; a TEAL short-sleeved TUNIC whose hem falls like a short skirt over her thighs, short PINK STRIPED SHIRT SLEEVES showing under it, DARK BROWN fingerless ARM WRAPS on both forearms, a BROWN LEATHER BELT with a LEATHER POUCH on her hip full of small GLOWING BLUE BOMBS, PURPLE STRIPED TIGHTS and BROWN LACED BOOTS (1 her idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the clothes, the belt, the pouch, the tights, the boots; 3 the head close-up in 3/4: the hair, the clips, the face, the eyes; 4 the same from behind: the hair and the two braids; 5 the official portrait: her mood, her face, her colours; 6 the head close-up from the front: both eyes and both X clips; 7 the idle from the side: her body from the side, the braids). Images 8a and 8b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters drawn in the same style, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a small girl's big head, face and eyes on the grid (11), the square density, the outline and metal parts on the grid (12), blue hair and braids on the grid (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (all the hair and both hands whole); the lowest point level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b).
PROPORTIONS: chibi - the head with its hair about ONE THIRD of her height; a short body, short slim legs; NOT realistic slim proportions.
THE FACE: round, light warm skin with a little pink on the cheeks; TWO BIG EYES of the SAME size at the SAME height, both visible (each at least 2x3 squares, blue-grey with one white highlight square), thin dark eyebrows, a small mouth.
THE HAIR: the bright blue in 3-4 shades (the shadows a deeper blue), tufts sticking out at the ends; the two thin braids hanging behind her shoulders; the gold X clips in 3 shades with clear edges.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the blue hair, the gold clips, the skin, the teal tunic, the pink sleeves, the dark brown arm wraps, the brown belt and pouch, the small blue bombs in the pouch, the purple striped tights, the brown boots clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no explosions, no smoke, no sparks, no glow), nothing in her hands (no monkey toy, no bomb in hand), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (powder-A.png): her idle (images 1, 2 and 8a) - 3/4 view facing right (the body turned to the front-right): one hand raised to her chin as if thinking, the other arm held out to her right side with the open palm turned up, the legs a little apart; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker; both soles on the ground line. She is about 660 px (about 60 squares) from the top of her head to her soles.
POSE B (powder-B.png): STANDING STRAIGHT - the SAME girl with the SAME 11-px squares, 3/4 view facing right: standing upright, BOTH ARMS HANGING at her sides a little away from the body (both hands and arm wraps visible), the legs a little apart and planted, the braids hanging behind her; the same height, about 660 px (about 60 squares) from the top of her head to her soles (image 8b shows only her size and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、手完整，不出画。
- Q 版：头连头发约占身高三分之一；**两只大眼睛一样大、一样高**、带白色高光，蓝灰色。
- 亮蓝短发、两条小辫子、两个金色 X 形发夹；青绿上衣、粉色条纹袖子、深棕护臂、棕皮带和装着蓝色小炸弹的皮袋、紫色条纹裤袜、棕靴子。
- A：一只手在下巴前、另一只手向右伸出掌心朝上；B：站直、两只手臂垂在两侧（看得见手和护臂）。
- 两张都是从头顶到脚底约 660 px（约 60 格），脚底在地面线上。
- 没有任何特效，手里不拿东西。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，提示词里本来就没写她的名字，只有外观描述。
- A、B 两张都画完后，最后写 `outputs/powder-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/powder_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/powder/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回，和已合并的小个子女孩（佐伊、波比、吉格斯、璐璐）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画：3/4 正面（待机、选人卡片）和**侧面朝右**（所有动作的底子；脸用 3/4 正面的同一张脸）。动作帧不找 Codex，自己从造型的像素无损摆（`rig_powder.py`：只整格平移、绕半格点的四分之一转、镜像），缺的部件姿势再出部件包（腿要给骨架）。金铲铲的动作（TFTSet13.wad.client 里 TFT13_Blue 的片段，`pose_ref.py --champ TFT13_Blue --wad-file TFTSet13.wad.client`）：待机 Idle，跑 Run，普攻 attack_1 / attack_2，技能 Spell（蹲下点燃、扔出猴子炸弹），死亡 Death。她的猴子炸弹模型是同一个皮肤里的 Monkey 子网格（`--only-joints . --hide-submesh Powder_Mat`），第 3 步特效包用它做参考。
